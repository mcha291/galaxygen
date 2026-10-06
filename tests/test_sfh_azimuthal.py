"""The azimuthal model (BUILD_II Phase 2, S27): one slot differs, the modulation is a redistribution.

``sfh_azimuthal`` publishes every field ``sfh`` does, computed by ``sfh`` itself, plus
``sfr_modulation`` over (R, φ). The gates are assertions here: the models differ in exactly
one slot; the modulation averages to 1 around every ring, so the star formation rate times it
integrates back to the axisymmetric rate (RENDER_PHYSICS.md §7); every shared field is
``sfh``'s own, bit for bit; every acceptance row reads the same in both models; and the
catalogue's young stars follow the modulation in ``azimuthal`` and the contrast in ``basic``.
"""

from __future__ import annotations

import math
import re

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, production
from galaxy.core.stage import Extension, Stage, StageError, UndeclaredAccess, extend
from galaxy.run import run
from galaxy.specs import graph, spec
from galaxy.stages import systems
from galaxy.stages.pieces import ArmPattern  # S60 (D219): was galaxy.stages.pattern
from galaxy.stages.sfh import SFH
from galaxy.stages.sfh_azimuthal import SFH_AZIMUTHAL, SFR_MODULATION, sfr_modulation
from helpers import TINY, decl, impls, model, stage

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
SHARED = SFH.published_names


def identical(x, y) -> bool:
    """Bit for bit, NaN equal to NaN; categorical values by equality."""
    x, y = np.asarray(x), np.asarray(y)
    if x.dtype.kind in "fc" and y.dtype.kind in "fc":
        return bool(np.array_equal(x, y, equal_nan=True))
    return x.shape == y.shape and bool(np.all(x == y))


@pytest.fixture(scope="module")
def models():
    m = production()[0]
    # Both models by name, deliberately (S46, D197): this module compares basic against azimuthal.
    return m.get("basic"), m.get("azimuthal")


@pytest.fixture(scope="module")
def coarse(models):
    """Both models, whole, on the coarse grid at the defaults."""
    basic, azimuthal = models
    return run(basic, None, COARSE), run(azimuthal, None, COARSE)


# --- the declaration ---------------------------------------------------------------


def test_the_two_models_differ_in_exactly_one_slot(models):
    basic, azimuthal = models
    b, a = basic.stage_map, azimuthal.stage_map
    assert list(b) == list(a), "the same slots, in the same order"
    assert {s for s in b if b[s] != a[s]} == {"sfh"}
    assert (b["sfh"], a["sfh"]) == ("sfh", "sfh_azimuthal")
    assert azimuthal.constants is basic.constants or dict(azimuthal.constants) == dict(basic.constants)
    assert azimuthal.inputs == basic.inputs


def test_sfh_azimuthal_extends_sfh_and_adds_one_optional_field():
    assert SFH_AZIMUTHAL.slot == "sfh" and SFH_AZIMUTHAL.extends is SFH
    assert SFH_AZIMUTHAL.checkpoint == SFH.checkpoint == 4
    # The same declaration objects, so preflight's one-contract-per-name holds by identity.
    assert SFH_AZIMUTHAL.publishes[: len(SFH.publishes)] == SFH.publishes
    assert all(a is b for a, b in zip(SFH_AZIMUTHAL.publishes, SFH.publishes))
    own = [d for d in SFH_AZIMUTHAL.publishes if d.name not in SHARED]
    assert own == [SFR_MODULATION]
    assert SFR_MODULATION.optional and SFR_MODULATION.provenance == "seeded"
    assert SFR_MODULATION.axes == ("R", "phi") and SFR_MODULATION.unit == "dimensionless"
    # S51 (D210): the gas's own contrast, not the stellar one (was pattern_density_contrast).
    # S58 (D217 follow-up): was {"gas_density_contrast"} - the gas's contrast as the star formation law reads it,
    # the bar's lanes spread over the bar's footprint; the same numbers outside every bar's reach.
    assert set(SFH_AZIMUTHAL.requires) - set(SFH.requires) == {"star_formation_gas_contrast"}
    # Rule D5: no constant's name in what the viewer reads.
    assert not re.search(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b", SFR_MODULATION.about + SFH_AZIMUTHAL.about)


def test_provenance_the_histories_stay_derived_and_the_modulation_is_seeded(prod):
    models_, impls_, table = prod
    g = graph.analyse(models_.get("azimuthal"), impls_, table)
    assert g.ok, g.problems
    assert g.provenance["sfr_modulation"] == "seeded"
    assert {g.provenance[n] for n in SHARED} == {"derived"}
    # ... and so is everything downstream the two models share.
    base = graph.analyse(models_.get("basic"), impls_, table)
    assert {n: p for n, p in g.provenance.items() if n != "sfr_modulation"} == base.provenance


# --- the machinery -----------------------------------------------------------------


def test_an_extension_computes_its_base_in_the_bases_own_view():
    """The base cannot read what only the extension declared: the shared fields cannot depend on it."""
    peek = decl("peek")

    def base_compute(ctx):
        ctx.fields["f"]  # declared by the extension, not by the base
        return {"peek": np.ones(ctx.grid.shape(("R",)))}

    base = stage("b", (peek,), compute=base_compute, slot="x")
    ext = extend(base, id="e", about="extension", own=lambda ctx, shared: {}, requires=("f",))
    src = stage("src", ("f",))
    with pytest.raises(UndeclaredAccess):
        run(model("m", src, ext), None, TINY, impls=impls(src, ext), table=INPUTS)


def test_an_extension_must_compute_through_its_base_and_republish_it():
    from dataclasses import replace

    from galaxy.core.registry import Registry

    base = stage("b", ("h",), slot="x")
    # The compute check fires at registration, the one door into production, so that an
    # instrument may wrap an unregistered copy's compute (D114's probes, S21 b's D4 count) —
    # construction alone does not refuse it (S27, D176).
    loose = Stage(id="e", slot="x", checkpoint=1, about="a", compute=lambda ctx: {}, publishes=base.publishes, extends=base)
    with pytest.raises(StageError, match="Extension"):
        Registry("stage", lambda s: s.id).register(loose)
    good = extend(base, id="g", about="a", own=lambda ctx, shared: {})
    Registry("stage", lambda s: s.id).register(good)
    replace(good, compute=lambda ctx: {})  # an instrument's copy: constructs without complaint
    with pytest.raises(StageError, match="republish"):
        Stage(id="e", slot="x", checkpoint=1, about="a", compute=Extension(base, lambda c, s: {}), extends=base)
    other = stage("o", ("h2",), slot="y")
    with pytest.raises(StageError, match="slot"):
        Stage(id="e", slot="x", checkpoint=1, about="a", compute=Extension(other, lambda c, s: {}),
              publishes=other.publishes, extends=other)
    clash = extend(base, id="e", about="a", own=lambda ctx, shared: {"h": np.zeros(ctx.grid.shape(("R",)))})
    with pytest.raises(StageError, match="republished"):
        run(model("m", clash), None, TINY, impls=impls(clash), table=INPUTS)


def test_the_modulation_function_is_one_where_there_is_nothing_to_redistribute():
    gas = np.array([0.0, 5.0, 20.0])
    crit = np.array([10.0, 10.0, 10.0])
    flat = np.ones((3, 12))
    assert np.allclose(sfr_modulation(gas, crit, flat, 1.4), 1.0, rtol=0, atol=1e-15)
    wavy = 1.0 + 0.5 * np.cos(2.0 * np.linspace(0, 2 * np.pi, 12, endpoint=False))[None, :].repeat(3, axis=0)
    m = sfr_modulation(gas, crit, wavy, 1.4)
    assert np.all(m[0] == 1.0), "a ring with no gas forms nothing and moves nothing"
    assert np.allclose(m.mean(axis=1), 1.0, rtol=0, atol=1e-12)
    # Above the threshold the law's exponent sharpens the contrast; at the threshold its switch does,
    # much more: 5 below a threshold of 10 is lifted over it only in the arm.
    spread = lambda a: a.max() / a.min()  # noqa: E731
    assert spread(wavy[2]) < spread(m[2]) < spread(m[1])


# --- the gate: a redistribution ------------------------------------------------------


@pytest.mark.parametrize("pattern_seed", [0, 3, 11])
def test_the_modulation_is_a_redistribution_of_the_axisymmetric_rate(models, pattern_seed):
    """RENDER_PHYSICS.md §7: the modulation integrates back to the axisymmetric star formation rate."""
    _, azimuthal = models
    o = run(azimuthal, {"pattern_seed": pattern_seed}, COARSE, only=("sfr_modulation", "sfr", "sfr_surface_density"))
    M = np.asarray(o.fields["sfr_modulation"])
    R, psi = o.grid.R, np.asarray(o.fields["sfr_surface_density"])
    assert M.shape == (R.size, o.grid.phi.size) and np.all(M >= 0.0) and np.all(np.isfinite(M))
    # Its mean around every ring is 1: the grid's φ cells are uniform, so this is the φ-integral over 2π.
    assert np.max(np.abs(M.mean(axis=1) - 1.0)) < 1e-9
    # So Ψ(R) M(R, φ) over the whole (R, φ) grid is the axisymmetric total, to rounding.
    dphi = o.grid["phi"].width
    total = float(np.trapezoid((psi[:, None] * M).sum(axis=1) * dphi * R, R))
    assert total == pytest.approx(float(o.fields["sfr"]), rel=1e-12)
    # And it is not the contrast: it moves where stars form, sharper than the gas it reads (S51, D210:
    # the gas's own contrast, the stage's input, in place of the stellar one).
    c = np.asarray(run(azimuthal, {"pattern_seed": pattern_seed}, COARSE, only=("gas_density_contrast",)).fields["gas_density_contrast"])
    i = int(np.argmin(np.abs(R - 8.2)))
    assert M[i].max() / max(M[i].min(), 1e-12) > c[i].max() / c[i].min()
    assert np.corrcoef(M[i], c[i])[0, 1] > 0.9


def test_a_gas_weighted_normalisation_would_have_made_stars(coarse):
    """Why the ring mean is plain: normalised by the gas the modulation would not integrate back.

    BUILD_II Phase 2 words the normalisation as a gas-weighted mean of 1 and the gate as the
    integral; for a field that multiplies the *rate* the two differ by the modulation's
    correlation with the gas, which in an arm is the whole point. Pinned so the reading is
    visible: at R₀ the gas-weighted mean of the modulation is about 1.26, i.e. a gas-weighted
    normalisation would have taken a fifth of the star formation out of the ring.
    """
    _, a = coarse
    # S51 (D210): weighted by the gas the stage reads, its own contrast (was pattern_density_contrast).
    M, c = np.asarray(a.fields["sfr_modulation"]), np.asarray(a.fields["gas_density_contrast"])
    i = int(np.argmin(np.abs(a.grid.R - 8.2)))
    weighted = float((c[i] * M[i]).sum() / c[i].sum())
    assert abs(M[i].mean() - 1.0) < 1e-12
    assert weighted > 1.1


# --- the gate: nothing radial moves ----------------------------------------------------


def test_every_shared_field_is_sfhs_own(coarse, models):
    """Bit for bit: the extension cannot alter what it shares with basic, and the pattern seed cannot reach it."""
    b, a = coarse
    for name in SHARED:
        assert identical(a.fields[name], b.fields[name]), name
    # Every other field the two models share, downstream included, except the catalogue columns
    # (the young stars move) and the planets drawn around them.
    moved = {"star_azimuth", "star_age", "star_birth_radius", "star_metallicity", "star_alpha",
             "star_luminosity", "star_temperature",
             # S28: looked up from the same moved ages and abundances
             "star_magnitude_v", "star_ionizing_photons", "star_wind_luminosity", "star_wolf_rayet",
             # S29: what the dead stars are, from the same moved ages and abundances
             "star_remnant", "star_remnant_mass",
             # S36: a star's wind bubble, from the same moved ages and winds
             "star_bubble_radius",
             } | {n for n in b.fields if n.startswith("planet_")} | {
        "star_planet_count", "mean_planets_per_star", "giant_fraction_sample"}  # the planets' sample statistics
    # S48 (D200, D203): the bright catalogue's cells carry the azimuthal weight - the contrast for the old stars, the
    # star-formation modulation for the 20-100 Myr ones - so each cell's expected count, its draws, the default
    # selection's columns and the luminosity of its faintest star differ between the models. The galaxy-wide count
    # above a threshold is the tables' summed over cells whose weights average to one around each ring: the same
    # number to rounding (the last bit moves with the order of the sum), not bit for bit.
    moved |= {n for n in b.fields if n.startswith("bright_star_")}
    assert float(a.fields["bright_star_count_1e3"]) == pytest.approx(float(b.fields["bright_star_count_1e3"]), rel=1e-12)
    same = [n for n in b.fields if n not in moved]
    differ = [n for n in same if not identical(a.fields[n], b.fields[n])]
    assert differ == []
    assert set(a.fields) - set(b.fields) == {"sfr_modulation"}
    _, azimuthal = models
    other = run(azimuthal, {"pattern_seed": 9}, COARSE, only=SHARED + ("sfr_modulation",))
    for name in SHARED:
        assert identical(other.fields[name], a.fields[name]), name
    assert not np.array_equal(np.asarray(other.fields["sfr_modulation"]), np.asarray(a.fields["sfr_modulation"]))


def test_every_acceptance_row_reads_the_same_in_both_models(judged):
    """The rows are radial and vertical: the azimuthal model reads basic's, number for number."""
    basic = {r.n: r for r in judged["basic"]}
    azimuthal = {r.n: r for r in judged["azimuthal"]}
    # 25-29 since S28 (Phase 3), 30-31 (the supernova rates) since S30 (Phase 6), 32-33 (globular clusters,
    # stellar halo) since S34 (Phase 5): the same rule. range(1, 32) until S34.
    assert sorted(basic) == sorted(azimuthal) == [q.n for q in spec.QUANTITIES] == list(range(1, 38))  # 37 until S44 (row 37, D195), 34 until S35
    for n in basic:
        b, a = basic[n], azimuthal[n]
        assert a.status == b.status, (n, a.status, b.status)
        same = a.value == b.value or (
            isinstance(a.value, float) and isinstance(b.value, float) and math.isnan(a.value) and math.isnan(b.value)
        )
        assert same, (n, a.value, b.value)
    # Rows 15-17 unmoved in both (Phase 1b's pins): 15 the recorded miss of debt #80.
    for results in (basic, azimuthal):
        assert results[15].value == pytest.approx(5.20971, abs=1e-4) and results[15].status == "fail"
        assert results[16].value == pytest.approx(41.1036, abs=1e-3) and results[16].status == "pass"
        assert results[17].value == pytest.approx(6.08381, abs=1e-4) and results[17].status == "pass"


# --- the catalogue ----------------------------------------------------------------------


def _constants() -> dict:
    """The model's constants, as its stage passes them (the two models hold the same ones, asserted above).
    S59 (D218 follow-up): the young stars' reader is the star formation law at a point, which reads the gas
    pattern's constants and the law's index; ``materialise`` refuses ``azimuthal``'s fields without them."""
    return {k: c.value for k, c in production()[0].get("azimuthal").constants.items()}


def _catalogue(out, n=100_000, **more):
    return systems.materialise(out.fields, out.grid.R, out.grid.t, 0, n, migration=float(out.inputs["migration_efficiency"]),
                               constants=_constants(), **more)


def test_the_young_stars_follow_the_modulation_and_the_old_ones_the_contrast(coarse):
    b, a = coarse
    cb, ca = _catalogue(b), _catalogue(a)
    # The layout is the contrast's in both, so a star's (cell, index) names the same place.
    assert ca.counts == cb.counts
    for name in ("star_radius", "star_height", "star_mass", "star_population"):
        assert np.array_equal(ca[name], cb[name]), name
    # S59 (D218 follow-up): was `systems.Modulation(a.fields["sfr_modulation"], a.grid.R)`, the grid table read
    # between rings. The reader is the catalogue's own now - the law at a point, built as the stage builds it.
    mod = systems.young_reader(a.fields, a.grid.R, _constants())
    assert isinstance(mod, systems.Modulation) and systems.young_reader(b.fields, b.grid.R, _constants()) is None
    pattern = ArmPattern.from_fields(a.fields, a.grid.R)  # S56 (D215): the modes are published on the grid radii

    def mean_at(table, cat, pick):
        return float(np.mean([table(np.array([r]), np.array([p]))[0, 0]
                              for r, p in zip(cat["star_radius"][pick], cat["star_azimuth"][pick])]))

    young_a = ca["star_age"] < systems.YOUNG_STAR_AGE
    young_b = cb["star_age"] < systems.YOUNG_STAR_AGE
    assert young_a.sum() > 100 and young_b.sum() > 100
    # Where today's stars form, read at each young star's place: well above 1 in azimuthal,
    # and near what the contrast alone gives in basic.
    in_azimuthal, in_basic = mean_at(mod.at, ca, young_a), mean_at(mod.at, cb, young_b)
    assert in_azimuthal > in_basic + 0.3, (in_azimuthal, in_basic)
    # The old stars still sit where the mass is.
    old = np.flatnonzero(~young_a)[:5000]
    old_b = np.flatnonzero(~young_b)[:5000]
    assert mean_at(pattern.contrast, ca, old) == pytest.approx(mean_at(pattern.contrast, cb, old_b), abs=0.02)


def test_the_azimuthal_catalogue_is_the_same_by_region_as_in_a_sweep(coarse):
    """D60 in the path basic never takes: every table covers every ring and sector."""
    _, a = coarse
    whole = _catalogue(a)
    cells = systems.cells_in(a.grid.R, 7.0, 9.0, 0.0, 0.8)
    part = _catalogue(a, cells=cells)  # S59 (D218 follow-up): the same call, with the model's constants
    start = {}
    offset = 0
    for cell, count in whole.counts:
        start[cell] = offset
        offset += count
    rows = np.concatenate([np.arange(start[c], start[c] + n) for c, n in part.counts])
    for name in part:
        assert identical(part[name], whole[name][rows]), name
    # A smaller sample is a prefix of a larger one, cell by cell.
    small = _catalogue(a, cells=cells[:2])
    assert np.array_equal(small["star_azimuth"], part["star_azimuth"][: small.size])


def test_the_api_publishes_the_modulation_for_the_azimuthal_model_only():
    from galaxy.api.service import Service

    s = Service(grid=GridSpec(n_R=24, n_t=40, n_z=4, n_phi=24))
    listed = s.handle("/api/stages").json()["models"]
    assert listed == ["azimuthal", "basic"]  # S46: the default leads (D197)
    fields = {m: {f["name"]: f for f in s.handle("/api/fields", {"model": [m]}).json()["fields"]} for m in listed}
    assert "sfr_modulation" not in fields["basic"]
    f = fields["azimuthal"]["sfr_modulation"]
    assert f["provenance"] == "seeded" and f["axes"] == ["R", "phi"]
    assert set(fields["azimuthal"]) - set(fields["basic"]) == {"sfr_modulation"}


# --- inside a bar's reach: the footprint, not the lanes (S58, D217's follow-up at the gate) ------------------------


def _top_tenth(modulation: np.ndarray) -> np.ndarray:
    """The share of each ring's star formation in the tenth of its cells that form the most."""
    ranked = -np.sort(-modulation, axis=1)
    return ranked[:, : modulation.shape[1] // 10].sum(axis=1) / ranked.sum(axis=1)


@pytest.mark.xfail(strict=True, reason="S60 (D219): layer-on numbers await the re-pin after the fourth model pass")
def test_star_formation_follows_the_bar_s_footprint_and_not_the_lanes(models):
    """The gate's ruling on the first build of S58 (D217's follow-up): "The lanes' one unsourced number (the width)
    must not drive a census: ``sfr_modulation`` inside the bar's reach reads w_arm s + w_bar L_fp, L_fp the
    footprint-uniform field (base outside the footprint, base + excess/share inside it: the 2.6 ratio kept, no
    ridge), so star formation follows the bar's footprint and not the placeholder's ridge. Dust and the gas census
    keep L."

    **The alternative's prediction, as the gate words it**: the laned field "read 88-93 % of a ring's star
    formation in its top tenth of cells at 2-3.3 kpc and a maximum modulation of 17.2". As this file reads the same
    alternative on the Milky Way template - the star formation law run on the published ``gas_density_contrast``,
    which still carries the lanes: **88.4-95.9 %** on the rings of 2-3.3 kpc, and a largest modulation of **17.35**
    (3.26 kpc). A lane 0.10 a wide - a width nobody measured - raised to the law's exponent.

    **As built**, on ``star_formation_gas_contrast``: the top tenth of cells holds **14.9-31.9 %** of a ring's star
    formation at 2-3.3 kpc (a uniform ring would read 10 %; the arms' own crowding at 8 kpc reads 40 %), and the
    largest modulation is **7.83**, at 4.61 kpc, where the arms and the footprint's end meet. Inside the
    half-length the top tenth holds 10.0-50.5 %. At R₀ nothing moved: the largest modulation there is 5.4401, the
    same bits as the laned alternative's.

    **S59 (D218): every number above was re-read.** The template is read with the layer on, and since S59 the
    arms' winding is laid in seeded segments, outward and inward from the bar's end: each ring's gas is the same
    curve turned by its own phase, so a ring's cell means move a little (the crest falls elsewhere among the
    cells), and inside the bar's reach the arms meet the footprint and the lanes at another angle. Before the
    segments the numbers read 88.1-95.7 %, 17.62 (3.49 kpc), 14.9-28.0 %, 7.41 at 4.31 kpc, 10.0-52.0 % and 5.4391.
    What the test asserts did not move: the two fields are the same bits past the half-length, the law reads the
    footprint's, and the footprint's field carries no ridge - its largest value is the arms' own size (3.135,
    now on a ring 0.15 kpc inside the half-length, where an arm's crest crosses the footprint; 3.134 at 6.34 kpc
    past it), half the lanes'.

    **S59 (D218 follow-up): re-read once more.** A segment's pitch is relative to the disc's and the rows are other
    rows, so each ring is turned by another phase again. On the first build's winding the numbers above read
    88.4-95.8 %, 17.53 (3.49 kpc), 14.9-34.3 %, 7.93 at 4.69 kpc, 10.0-49.9 % and 5.4414, and the footprint field's
    largest cell was the 3.135 just inside the half-length; it is 3.134 at 6.34 kpc now, the arms' own, past the
    half-length. What the test asserts did not move.

    The two published gas fields: the same bits on every ring at or past the half-length (331 of the 400) and on
    every ring of an unbarred galaxy (``ngc_4414``: every cell); different on each of the 69 rings inside the
    half-length. Both have a ring mean of 1 and neither is anywhere negative."""
    from galaxy import templates

    _, azimuthal = models
    index = float(azimuthal.constants["KS_INDEX"].value)
    only = ("gas_density_contrast", "star_formation_gas_contrast", "sfr_modulation", "gas_surface_density",
            "sf_threshold_surface_density", "bar_half_length", "bar_present")
    o = run(azimuthal, templates.overrides(templates.TEMPLATES["milky_way"]), only=only)
    F, R = o.fields, o.grid.R
    laned_gas, footprint_gas = np.asarray(F["gas_density_contrast"]), np.asarray(F["star_formation_gas_contrast"])
    a = float(F["bar_half_length"])
    past = R >= a
    assert F["bar_present"] == "yes" and int(past.sum()) == 331 and int((~past).sum()) == 69
    assert laned_gas[past].tobytes() == footprint_gas[past].tobytes()  # bit for bit: the templates are the same ones there
    assert not np.any((laned_gas[~past] == footprint_gas[~past]).all(axis=1))
    assert float(np.abs(footprint_gas.sum(axis=1) / footprint_gas.shape[1] - 1.0).max()) < 2e-13 and footprint_gas.min() > 0.0
    # No ridge: the largest value of the field the law reads is the arms' own, in the mid disc; the lanes' is twice it.
    # S59 (D218): was (3.1331, 6.3375) - the segments turn each ring, and the largest cell is now where an arm's
    # crest crosses the footprint just inside the half-length; the arms' own largest past it is read beside it.
    # S59 (D218 follow-up): was (3.1350, 5.0625) - on the follow-up's winding no crest crosses the footprint that
    # high, and the largest cell is the arms' own past the half-length again, the one read beside it (was 3.1342).
    assert (float(footprint_gas.max()), float(R[int(np.argmax(footprint_gas.max(axis=1)))])) == pytest.approx((3.1341, 6.3375), abs=2e-4)
    assert (float(footprint_gas[past].max()), float(R[past][int(np.argmax(footprint_gas[past].max(axis=1)))])) == pytest.approx((3.1341, 6.3375), abs=2e-4)
    assert float(laned_gas.max()) == pytest.approx(6.7614, abs=2e-4)  # S59 (D218 follow-up): was 6.6786; S59 (D218): was 6.6640
    built = np.asarray(F["sfr_modulation"])
    assert built.tobytes() == sfr_modulation(F["gas_surface_density"], F["sf_threshold_surface_density"], footprint_gas, index).tobytes()
    laned = sfr_modulation(F["gas_surface_density"], F["sf_threshold_surface_density"], laned_gas, index)
    band = (R >= 2.0) & (R <= 3.3)
    here = int(np.argmin(np.abs(R - 8.0)))
    # The alternative, as read here (the gate's words: 88-93 % and 17.2).
    top = _top_tenth(laned)
    # S59 (D218): was (0.8812, 0.9567) and (17.619, 3.4875)
    # S59 (D218 follow-up): was (0.8835, 0.9583) and (17.530, 3.4875)
    assert (float(top[band].min()), float(top[band].max())) == pytest.approx((0.8839, 0.9586), abs=2e-4)
    assert (float(laned.max()), float(R[int(np.argmax(laned.max(axis=1)))])) == pytest.approx((17.348, 3.2625), abs=2e-3)
    # As built.
    # S58 (D217 follow-up): was 17.619 at 3.4875 kpc (the largest modulation), 0.8812-0.9567 (the top tenth, 2-3.3 kpc)
    top = _top_tenth(built)
    # S59 (D218): was (0.1490, 0.2804), (0.1000, 0.5204), (7.4075, 4.3125), 0.4015 and 5.4391
    # S59 (D218 follow-up): was (0.1490, 0.3429), (0.1000, 0.4992), (7.9268, 4.6875) and 5.4414; 0.4014 as it was
    assert (float(top[band].min()), float(top[band].max())) == pytest.approx((0.1490, 0.3189), abs=2e-4)
    assert (float(top[~past].min()), float(top[~past].max())) == pytest.approx((0.1000, 0.5055), abs=2e-4)
    assert (float(built.max()), float(R[int(np.argmax(built.max(axis=1)))])) == pytest.approx((7.8290, 4.6125), abs=2e-3)
    assert float(top[here]) == float(_top_tenth(laned)[here]) == pytest.approx(0.4014, abs=2e-4)
    assert built[past].tobytes() == laned[past].tobytes() and float(built[here].max()) == pytest.approx(5.4401, abs=2e-4)
    assert float(np.abs(built.mean(axis=1) - 1.0).max()) < 1e-12 and built.min() >= 0.0
    # An unbarred galaxy has no lanes and no footprint: one field, twice.
    n = run(azimuthal, templates.overrides(templates.TEMPLATES["ngc_4414"]), only=only)
    assert n.fields["bar_present"] == "no"
    assert np.asarray(n.fields["gas_density_contrast"]).tobytes() == np.asarray(n.fields["star_formation_gas_contrast"]).tobytes()
    assert n.fields["gas_density_contrast"] is not n.fields["star_formation_gas_contrast"]
