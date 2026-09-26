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
from galaxy.stages.pattern import ArmPattern
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
    assert set(SFH_AZIMUTHAL.requires) - set(SFH.requires) == {"pattern_density_contrast"}
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
    # And it is not the contrast: it moves where stars form, sharper than the mass.
    c = np.asarray(run(azimuthal, {"pattern_seed": pattern_seed}, COARSE, only=("pattern_density_contrast",)).fields["pattern_density_contrast"])
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
    M, c = np.asarray(a.fields["sfr_modulation"]), np.asarray(a.fields["pattern_density_contrast"])
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
             } | {n for n in b.fields if n.startswith("planet_")} | {
        "star_planet_count", "mean_planets_per_star", "giant_fraction_sample"}  # the planets' sample statistics
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
    # 25-29 since S28 (Phase 3), 30-31 (the supernova rates) since S30 (Phase 6): the same rule
    assert sorted(basic) == sorted(azimuthal) == [q.n for q in spec.QUANTITIES] == list(range(1, 32))
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


def _catalogue(out, n=100_000):
    return systems.materialise(out.fields, out.grid.R, out.grid.t, 0, n, migration=float(out.inputs["migration_efficiency"]))


def test_the_young_stars_follow_the_modulation_and_the_old_ones_the_contrast(coarse):
    b, a = coarse
    cb, ca = _catalogue(b), _catalogue(a)
    # The layout is the contrast's in both, so a star's (cell, index) names the same place.
    assert ca.counts == cb.counts
    for name in ("star_radius", "star_height", "star_mass", "star_population"):
        assert np.array_equal(ca[name], cb[name]), name
    mod = systems.Modulation(a.fields["sfr_modulation"], a.grid.R)
    pattern = ArmPattern.from_fields(a.fields)

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
    part = systems.materialise(a.fields, a.grid.R, a.grid.t, 0, 100_000, cells=cells,
                               migration=float(a.inputs["migration_efficiency"]))
    start = {}
    offset = 0
    for cell, count in whole.counts:
        start[cell] = offset
        offset += count
    rows = np.concatenate([np.arange(start[c], start[c] + n) for c, n in part.counts])
    for name in part:
        assert identical(part[name], whole[name][rows]), name
    # A smaller sample is a prefix of a larger one, cell by cell.
    small = systems.materialise(a.fields, a.grid.R, a.grid.t, 0, 100_000, cells=cells[:2],
                                migration=float(a.inputs["migration_efficiency"]))
    assert np.array_equal(small["star_azimuth"], part["star_azimuth"][: small.size])


def test_the_api_publishes_the_modulation_for_the_azimuthal_model_only():
    from galaxy.api.service import Service

    s = Service(grid=GridSpec(n_R=24, n_t=40, n_z=4, n_phi=24))
    listed = s.handle("/api/stages").json()["models"]
    assert listed == ["basic", "azimuthal"]
    fields = {m: {f["name"]: f for f in s.handle("/api/fields", {"model": [m]}).json()["fields"]} for m in listed}
    assert "sfr_modulation" not in fields["basic"]
    f = fields["azimuthal"]["sfr_modulation"]
    assert f["provenance"] == "seeded" and f["axes"] == ["R", "phi"]
    assert set(fields["azimuthal"]) - set(fields["basic"]) == {"sfr_modulation"}
