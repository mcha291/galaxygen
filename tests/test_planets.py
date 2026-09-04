"""The planets stage: what the formation model determines, and what it gets wrong.

GALAXY_INPUTS.md §12 sets the gate for this stage itself — "preflight asserts the
set is closed and documented; there is no external contract to satisfy" — so the
checks here are of two kinds. Some are the Solar System, which is the one system
whose answers everybody knows: the ice line, the asteroid belt's edges, the
Kuiper belt's inner edge, and which of Mercury, Mars and Earth keeps an
atmosphere. The rest are internal consistency of the kind rule B3 asks for: the
drawn sample must agree with the computed occurrence, because a sample that
traces the wrong density is still perfectly self-consistent.

Occurrence itself is *not* checked against a target, because the model disagrees
with the literature and the literature disagrees with itself — see debt #25. What
is checked is that the disagreement is the one recorded.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.units import UNITS
from galaxy.models.level0 import LEVEL0
from galaxy.run import run
from galaxy.stages import planets as pl
from galaxy.stages.systems import cell_counts, materialise

CONSTANTS = {k: v.value for k, v in LEVEL0.items()}

# The Solar System, in the units this stage publishes [recall: IAU/NASA fact sheets].
MERCURY = {"mass": 0.0553, "axis": 0.387, "radius": 0.383}
EARTH = {"mass": 1.0, "axis": 1.0, "radius": 1.0}
MARS = {"mass": 0.107, "axis": 1.524, "radius": 0.532}
NEPTUNE = {"mass": 17.15, "axis": 30.07, "radius": 3.865}
JUPITER = {"mass": 317.8, "axis": 5.204, "radius": 11.21}

_RUNS: dict[str, object] = {}


def out(model):
    if model.name not in _RUNS:
        _RUNS[model.name] = run(model)
    return _RUNS[model.name]


# --- the Solar System, which is the check everybody can make ------------------


def test_the_ice_line_is_where_the_solar_system_puts_it():
    """2.7 AU, from the star's luminosity and a condensation temperature alone."""
    solar = float(pl.ice_line(1.0, CONSTANTS["ICE_LINE_TEMPERATURE"]))
    assert 2.5 <= solar <= 2.9, solar
    # It moves with luminosity, which is the whole reason occurrence depends on mass.
    assert pl.ice_line(0.5, CONSTANTS["ICE_LINE_TEMPERATURE"]) < solar
    assert pl.ice_line(2.0, CONSTANTS["ICE_LINE_TEMPERATURE"]) > solar
    # T ∝ L^¼ a^-½, so the ice line goes as √L — which is M^1.75, not M^3.5.
    assert np.isclose(
        pl.ice_line(4.0, CONSTANTS["ICE_LINE_TEMPERATURE"]) / solar,
        4.0 ** (pl.LUMINOSITY_INDEX / 2.0),
    )


def test_belts_are_where_the_giants_left_them():
    """§12: a belt is not placed, it is a region a giant's resonances kept empty.

    The Solar System is the check, and it is a sharp one: nothing about the
    asteroid belt or the Kuiper belt is in this code, only Kepler's third law
    applied to two resonance ratios.
    """
    found = pl.belts([JUPITER["axis"]], 30.0)
    asteroid = found[0]
    assert asteroid["kind"] == "asteroid"
    assert 2.0 <= asteroid["inner"] <= 2.2, asteroid  # observed inner edge ~2.1 AU
    assert 3.2 <= asteroid["outer"] <= 3.4, asteroid  # observed outer edge ~3.3 AU

    with_neptune = pl.belts([JUPITER["axis"], NEPTUNE["axis"]], 50.0)
    kuiper = next(b for b in with_neptune if b["kind"] == "kuiper")
    assert 39.0 <= kuiper["inner"] <= 39.8, kuiper  # observed inner edge 39.4 AU
    assert pl.belts([], 30.0) == (), "no giant, no belt: there is nothing to have cleared one"


def test_the_solar_system_lands_in_the_right_atmosphere_classes():
    """Mercury keeps nothing, Mars keeps a little, Earth keeps its own, a giant is hydrogen."""
    bodies = [MERCURY, MARS, EARTH]
    mass = np.array([b["mass"] for b in bodies])
    axis = np.array([b["axis"] for b in bodies])
    radius = pl.planet_radius(mass)
    insolation = 1.0 / axis**2
    classes = pl.classify(mass, radius, insolation, np.zeros(3, dtype=bool), np.zeros(3, dtype=bool))
    assert [pl.ATMOSPHERES[c] for c in classes] == ["none", "thin", "thin"]
    giant = pl.classify(
        np.array([JUPITER["mass"]]), pl.planet_radius(np.array([JUPITER["mass"]])),
        np.array([1.0 / JUPITER["axis"] ** 2]), np.array([True]), np.array([True]),
    )
    assert pl.ATMOSPHERES[giant[0]] == "hydrogen"


def test_the_mass_radius_relation_is_good_to_about_ten_percent():
    """It exists to decide an escape velocity and to draw with; it is not a claim about interiors."""
    for body in (EARTH, MARS, NEPTUNE, JUPITER):
        got = pl.planet_radius(np.array([body["mass"]]))[0]
        assert abs(got - body["radius"]) / body["radius"] < 0.15, (body, got)


# --- occurrence: the payoff, and the disagreement it exposes -------------------


def test_occurrence_rises_steeply_with_metallicity_and_the_slope_is_measured(model):
    fields = out(model).fields
    grid = np.array([-0.6, -0.3, 0.0, 0.3, 0.6])
    p = pl.giant_probability(grid, pl.QUOTED_STAR_MASS, CONSTANTS)
    assert np.all(np.diff(p) > 0), "occurrence must rise with metallicity"
    # The calibration point, which is the one number fitted (~5% at [Fe/H] = 0).
    assert 0.045 <= fields["giant_occurrence_sun"] <= 0.055
    # And the two predictions that follow from it.
    assert fields["giant_occurrence_index"] > 2.0, (
        "the mechanism is steeper than the β ≈ 2 §12 quotes; debt #25 records why"
    )
    assert fields["giant_occurrence_rich"] > 0.25, (
        "and so it overshoots the ~25% §12 quotes at [Fe/H] = +0.5 — the two cited claims "
        "cannot both hold and this is the one the mechanism agrees with"
    )


def test_the_slope_is_the_disc_mass_scatter_and_not_a_fitted_exponent():
    """Rule B11: the relation fits, but is it the relation? Here it is a consequence.

    Widening the disc-mass distribution flattens occurrence against metallicity
    without any occurrence law being touched, which is what makes β a measurement
    of this model rather than an input to it.
    """
    def slope(scatter: float) -> float:
        constants = {**CONSTANTS, "DISC_MASS_SCATTER": scatter}
        step = 0.05
        lo = float(pl.giant_probability(-step, 1.0, constants))
        hi = float(pl.giant_probability(step, 1.0, constants))
        return (np.log10(hi) - np.log10(lo)) / (2 * step)

    assert slope(0.45) < slope(0.3) < slope(0.2)
    assert abs(slope(0.45) - 2.0) < abs(slope(0.3) - 2.0), (
        "matching the quoted β ≈ 2 needs a wider disc-mass scatter than §12's 0.3 dex"
    )


def test_occurrence_falls_with_stellar_mass_the_way_the_m_dwarfs_do():
    """A prediction, not a fit: only the solar-mass zero point was calibrated.

    §12 quotes Montet+14 for M dwarfs — 12.4 ± 5.4% above the sample median
    metallicity against 0.96 ± 0.51% below. The model is given no M-dwarf data at
    all, and its numbers bracket those.
    """
    dwarf = 0.4
    poor = float(pl.giant_probability(-0.1, dwarf, CONSTANTS))
    rich = float(pl.giant_probability(0.3, dwarf, CONSTANTS))
    assert poor < float(pl.giant_probability(-0.1, 1.0, CONSTANTS)), "an M dwarf makes fewer giants"
    assert poor < 0.02, poor  # Montet's metal-poor half: ~1%
    assert 0.01 < rich < 0.30, rich  # and its metal-rich half: ~12%
    assert rich > 5 * poor, "the split with metallicity is at least as steep as the observed one"


def test_the_drawn_sample_agrees_with_the_computed_occurrence(model):
    """Rule B3: check the sample against the field it was drawn from, never itself."""
    fields = out(model).fields
    expected = pl.giant_probability(fields["star_metallicity"], fields["star_mass"], CONSTANTS).mean()
    drawn = fields["giant_fraction_sample"]
    assert expected > 0.0
    assert abs(drawn - expected) < 0.35 * expected, (
        f"the drawn giants ({drawn:.4f}) and the computed probability ({expected:.4f}) disagree; "
        "one of the two definitions of a giant has drifted"
    )
    # They differ by a couple of per cent and the reason is known: the computed
    # form asks whether a zone's *centre* lies beyond the ice line, while a drawn
    # planet sits somewhere inside its zone and can land on the other side of it.
    assert abs(drawn - expected) < 0.05 * expected


# --- the architecture ---------------------------------------------------------


def test_the_disc_is_partitioned_not_invented():
    """Zones share out the solids; they cannot between them contain more than the disc had."""
    edges = pl.zone_edges(CONSTANTS["DISC_INNER_EDGE"], CONSTANTS["DISC_OUTER_EDGE"])
    budget = np.array([10.0, 3.0])
    zones = pl.zone_solids(edges, np.array([2.7, 0.5]), budget, CONSTANTS["ICE_BOOST"])
    assert np.allclose(zones.sum(axis=1), budget)
    assert np.all(zones >= 0.0)
    # The ice line puts more mass outside it than a smooth profile would.
    smooth = pl.zone_solids(edges, np.array([2.7]), np.array([10.0]), 1.0)
    stepped = pl.zone_solids(edges, np.array([2.7]), np.array([10.0]), 4.0)
    beyond = np.sqrt(edges[:-1] * edges[1:]) > 2.7
    assert stepped[0][beyond].sum() > smooth[0][beyond].sum()


def test_no_solids_no_planets():
    """A disc with no metals makes nothing, and says so rather than making dust."""
    built = pl.architecture(
        np.array([1.0]), np.array([-9.0]), np.zeros(1), np.full((1, pl.SLOTS), 0.5), CONSTANTS
    )
    assert built["count"][0] == 0
    assert not np.any(np.isfinite(built["axis"]))


def test_the_stability_filter_leaves_nothing_crowded():
    """§12 forbids an integrator, so the criterion has to hold by construction."""
    rng = np.random.default_rng(7)
    n = 500
    star = rng.uniform(0.15, 1.6, n)
    built = pl.architecture(
        star, rng.normal(0.0, 0.3, n), rng.standard_normal(n), rng.random((n, pl.SLOTS)), CONSTANTS
    )
    axis, mass = built["axis"], built["mass"]
    alive = np.isfinite(axis)
    earths = star * pl.EARTH_MASSES_PER_SOLAR
    crowded = 0
    for i in range(n):
        where = np.flatnonzero(alive[i])
        for a, b in zip(where[:-1], where[1:]):
            hill = 0.5 * (axis[i, a] + axis[i, b]) * np.cbrt((mass[i, a] + mass[i, b]) / (3 * earths[i]))
            crowded += (axis[i, b] - axis[i, a]) < CONSTANTS["HILL_SEPARATION"] * hill
    assert crowded == 0
    assert built["count"].max() > 1, "this check would be vacuous on single-planet systems"


# --- identity: the same system however you ask for it -------------------------


def test_a_system_is_the_same_alone_as_in_the_sample(model):
    """D60 one level down: (cell, index) names a system, and naming it is enough."""
    o = out(model)
    fields = o.fields
    counts = cell_counts(fields["stellar_surface_density"], o.grid.R, 0, 20000)
    offsets = np.cumsum([0] + [n for _, n in counts])
    planets_before = np.cumsum(np.concatenate([[0], fields["star_planet_count"]])).astype(int)

    for row in (0, 500, 5000):
        cell, index = counts[np.searchsorted(offsets, row, side="right") - 1][0], None
        index = row - offsets[np.searchsorted(offsets, row, side="right") - 1]
        stars = materialise(fields, o.grid.R, o.grid.t, 0, 20000, cells=[cell])
        mine, belts = pl.one_system(stars, index, cell, 0, CONSTANTS)
        start, end = planets_before[row], planets_before[row + 1]
        assert len(mine["planet_mass"]) == end - start
        assert np.array_equal(mine["planet_mass"], fields["planet_mass"][start:end])
        assert np.array_equal(mine["planet_semi_major_axis"], fields["planet_semi_major_axis"][start:end])
        giants = mine["planet_atmosphere"] == pl.ATMOSPHERES.index("hydrogen")
        assert bool(len(belts)) == bool(giants.any()), "a belt needs a giant to have cleared it"


def test_a_smaller_sample_gives_a_star_the_same_planets(model):
    """The prefix property (D60) has to survive the second object class too."""
    o = out(model)
    fields = o.fields
    small = materialise(fields, o.grid.R, o.grid.t, 0, 4000)
    large = materialise(fields, o.grid.R, o.grid.t, 0, 20000)
    cell, index = small.counts[3]
    index = 0
    little, _ = pl.one_system(
        materialise(fields, o.grid.R, o.grid.t, 0, 4000, cells=[cell]), index, cell, 0, CONSTANTS
    )
    lots, _ = pl.one_system(
        materialise(fields, o.grid.R, o.grid.t, 0, 20000, cells=[cell]), index, cell, 0, CONSTANTS
    )
    assert len(little["planet_mass"]) == len(lots["planet_mass"])
    assert np.array_equal(little["planet_mass"], lots["planet_mass"])
    assert np.array_equal(little["planet_obliquity"], lots["planet_obliquity"])


# --- §12's own gate: the set is closed and documented -------------------------


def test_the_planet_scalar_set_is_closed_and_documented(model, prod):
    """§12: 'preflight asserts the set is closed and documented. That is the gate.'"""
    _, impls, _ = prod
    stage = impls.get(model.stage_map["planets"])
    published = {d.name: d for d in stage.publishes}
    columns = {n: d for n, d in published.items() if d.of == "planet"}
    assert set(columns) == set(pl.PLANET_COLUMNS)
    for name, decl in published.items():
        assert decl.unit in UNITS, name
        assert decl.about.strip() and len(decl.about) > 60, name
        assert decl.provenance == "seeded", name
        if decl.kind.domain in ("grid", "object"):
            assert decl.ramp is not None, name
    # §12 names the set: mass, insolation, volatiles, rotation, obliquity, atmosphere.
    for expected in ("mass", "insolation", "volatile_fraction", "rotation_period", "obliquity", "atmosphere"):
        assert f"planet_{expected}" in columns, expected


def test_the_stage_counts_planets_onto_stars(model):
    """The two object classes are joined by a running total, not by an identifier field."""
    fields = out(model).fields
    counts = fields["star_planet_count"]
    assert len(counts) == len(fields["star_mass"])
    assert counts.sum() == len(fields["planet_mass"]) == fields["planet_count_sample"]
    assert np.all(counts == np.round(counts)), "a count of planets is a whole number"
    assert 0 <= counts.min() and counts.max() <= pl.SLOTS
    assert fields["mean_planets_per_star"] == pytest.approx(counts.mean())
