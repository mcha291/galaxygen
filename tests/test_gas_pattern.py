"""The gas's own arm pattern (S51, D210 Phases 1 and 1b; since S56 a response to any stellar pattern, D215).

The gates are D210's predictions that Phase 1 can be judged on alone: the contrast averages to 1
round every ring, on the grid and per sector; the ratio of means over the source's mask is the
published gas_arm_contrast; the ridge sits on the stellar crest with no offset and is narrower
than the stellar arm; the field is seeded through the pattern's drawn numbers and reads no gas
column. Since Phase 1b (D210 as amended, debt #131) the ratio is the bar stage's derived class
mean with no draw.

**S51's field, one mode** (kept as the regression, ``tests/test_modes.py``; the numbers below are
re-made here from the model's own classes with one four-armed mode at phase 0): pitch 13.54 deg,
bar 0.289 of contrast over a 5.21 kpc half-length; the swing window 1.72-3.44 holds m = 2, so
**C = 2.73**, the grand designs' mean. At R0 = 8.122 kpc the mask is clamped at half the period,
**a = 0.466, crest 3.068, trough 0.534**; at 12 kpc a = 0.387, crest 2.715, trough 0.613. (Phase
1's drawn C was 10.02, a = 0.823, crest 4.64, trough 0.180 at R0: the draw D210's amendment
withdrew.)

**Since S56 the default galaxy carries five modes, and the ridge is S51's by rank** (D215, the
second gate turn; both models; run on 2026-10-04): on each ring the gas takes one arm's ridge
values in the order of the stellar modes' sum, so every ring has S51's histogram and the crest is
the form's - at R0 **a = 0.437, crest 2.93, trough 0.564** (S51: 0.466, 3.07, 0.53; the share is
0.439 there, under its cap, by the ring's power-weighted arm number 3.5); at 12 kpc a = 0.424,
crest 2.88, trough 0.576. The published field runs 0.557-2.940 over the whole grid and no cell lies
above 4. The ratio of means is 2.73 on every ring out to 13.76 kpc and fades with the stellar
arms' amplitude beyond: at the last ring that carries a mode (14.81 kpc; amplitude 0.124 of the
arm amplitude) it is 1.21 and the gas runs 0.917-1.366; the next ring is exactly 1.

(The first reading of "the gas follows any pattern", the exponential of the modes' sum, was built
and retired within S56: crest 11.3 at R0, the field 0.34-15.5, the ratio 2.73 held even on the
last ring. It was never merged to main.)
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import s55_patterns as s55
from galaxy import templates
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import pattern as pt
from galaxy.stages.gas_pattern import (
    GAS_PATTERN,
    GAS_PATTERN_READS,
    PHASE_CELLS,
    GasPattern,
    kappa_for_width,
    mask_means,
    pattern_period,
    ridge_value,
)
from galaxy.stages.pattern import PATTERN

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
R_SUN = 8.122
_RUNS: dict[str, object] = {}


def out(model):
    """The default run, once per model per session (the whole pipeline is a few seconds)."""
    if model.name not in _RUNS:
        _RUNS[model.name] = run(model)
    return _RUNS[model.name]


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def shape_of(model, o) -> GasPattern:
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert gp is not None and not gp.flat
    return gp


def one_mode(model, C: float, bar: float = 0.0, m: int = 4, pitch: float = 13.5, bar_length: float = 5.2097) -> GasPattern:
    """S51's pattern: one arm number at unit amplitude on every ring, phase 0."""
    c = constants(model)
    R = DEFAULT.build().R
    unit = np.zeros((len(pt.ARM_MODES), R.size))
    unit[pt.ARM_MODES.index(m)] = 1.0
    return GasPattern(R, unit, (0.0,) * len(pt.ARM_MODES), C, bar, pitch, bar_length, c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])


def bounds(gp: GasPattern) -> tuple[float, float]:
    """The form's bound outside the bar's reach (D215, gate ruling 10), exactly: [1 − a(½, C)(1 − v_trough),
    1 + a(½, C)(v_crest − 1)] with a at the share's cap and the published ratio - 0.534 and 3.068 at the defaults."""
    crest, trough = gp.extremes()
    v_in, v_out = mask_means(np.array([0.5]), gp.kappa)
    a_half = float((gp.ratio - 1.0) / ((v_in[0] - 1.0) - gp.ratio * (v_out[0] - 1.0)))
    return 1.0 - a_half * (1.0 - trough), 1.0 + a_half * (crest - 1.0)


def row(o, R: float) -> int:
    return int(np.argmin(np.abs(o.grid.R - R)))


# --- (a), (b): a redistribution, not a source ---------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g >= 0.0) and np.all(np.isfinite(g))
    assert np.allclose(g.mean(axis=1), 1.0, atol=1e-12)


def test_every_ring_keeps_its_gas_on_the_grid_s_own_cells(model):
    """The ridge's mean is 1 over the ring. Sampled at a grid's cell centres it is 1 to rounding only where the
    ridge is analytic and resolved: one mode on the default 360 cells (S51: nothing aliases there), not on 36 (a
    four-armed ridge's ninth harmonic: 6e-4, found by Phase 2's builder at S51). **A ring of several modes is
    ranked, its ridge has corners where the superlevel set gains or loses a piece, and its sampled mean leaves 1 by
    up to 8.6e-4 on the default grid** (S56, D215). The stage divides a ring by its sampled mean wherever that has
    left 1 by more than 1e-12, as it has since S51 for a coarse grid, and leaves the others the law's own bits."""
    coarse = run(model, grid=GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36), only=("gas_density_contrast",))
    g = np.asarray(coarse.fields["gas_density_contrast"])
    assert np.all(g >= 0.0) and float(np.abs(g.mean(axis=1) - 1.0).max()) < 1e-12
    o = out(model)
    law = shape_of(model, o).contrast(o.grid.R, o.grid.phi)
    mean = law.mean(axis=1, keepdims=True)
    left = np.abs(mean - 1.0) > gm.RING_MEAN_TOLERANCE
    # S56 (D215): was `assert_array_equal(field, closed)` - one mode's ridge, whose sampled mean is 1 to rounding.
    np.testing.assert_array_equal(np.asarray(o.fields["gas_density_contrast"]), np.where(left, law / np.where(left, mean, 1.0), law))
    assert 150 < int(left.sum()) < 198 and float(np.abs(mean - 1.0).max()) == pytest.approx(8.64e-4, abs=2e-5)
    # One mode, the default grid: analytic, and untouched by the stage's division.
    single = one_mode(model, 2.73, bar=0.289, pitch=13.5378)
    assert float(np.abs(single.contrast(o.grid.R, o.grid.phi).mean(axis=1) - 1.0).max()) < 1e-12


def test_the_sector_means_average_to_one_and_are_the_series_s(model):
    """Twelve sectors at four radii: their mean is the ring's, 1, exactly; and each sector's mean is the dense
    numerical average of contrast_at over it **to the series' accuracy, which is no longer its dropped tail**:
    one mode's ridge is analytic (1e-6 here, the dense average's own error), but a ranked ridge of several modes
    has corners, and 1024 samples of it give the sector means to about 1e-3 of the ring's mean (S56, D215: was
    atol 1e-6). Pinned as measured; the number of samples is not changed to hide it."""
    gp = shape_of(model, out(model))
    edges = np.linspace(0.0, 2.0 * np.pi, 13)
    worst = 0.0
    for R in (1.0, 3.0, 6.0, 12.0):
        means = gp.sector_means(R, edges)
        assert float(means.mean()) == pytest.approx(1.0, abs=1e-12)
        dense = []
        for a, b in zip(edges[:-1], edges[1:]):
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000
            dense.append(float(gp.contrast_at(np.full_like(phi, R), phi).mean()))
        worst = max(worst, float(np.abs(means - np.array(dense)).max()))
        assert np.allclose(means, dense, atol=2e-3), (R, float(np.abs(means - np.array(dense)).max()))
        assert means.max() > 1.0 > means.min()  # the ridge is resolved: not a flat ring
    assert 1e-5 < worst < 1e-3
    single = one_mode(model, 2.73)
    for R in (3.0, 12.0):
        means = single.sector_means(R, edges)
        dense = []
        for a, b in zip(edges[:-1], edges[1:]):
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000
            dense.append(float(single.contrast_at(np.full_like(phi, R), phi).mean()))
        assert np.allclose(means, dense, atol=1e-6), R


# --- (c): the ratio of means is the ring's own -----------------------------------


def test_the_ratio_of_means_over_the_mask_is_the_ring_s_ratio(model):
    """The gate (D215, second turn): "the ratio of means inside the ring's mask equals C(R) to 1e-9 on every ring
    that carries a mode", C(R) = 1 + (C − 1) ρ(R) - the published 2.73 where the stellar arms have their full
    amplitude, less where they do not. On the quadrature's own cells it is the algebra (1e-15); recomputed from the
    law on a dense ring, independently - the mask the share of the ring where the rank is lowest - it is the
    quadrature's accuracy, 3.4e-5 at worst (S51's midpoint sums of the ridge, off the integral by up to 7e-5)."""
    o = out(model)
    F, R = o.fields, o.grid.R
    C = float(F["gas_arm_contrast"])
    gp = shape_of(model, o)
    share, a, ratio = gp.mask_share(R), gp.amplitude(R), gp.ratio_at(R)
    carries = np.isfinite(share)
    amplitudes = np.stack([np.asarray(F[n]) for n in pt.AMPLITUDE_FIELDS])
    assert np.array_equal(carries, amplitudes.sum(axis=0) > 0.0) and int(carries.sum()) == 198
    v_in, v_out = mask_means(share[carries], gp.kappa)
    got = (1.0 + a[carries] * (v_in - 1.0)) / (1.0 + a[carries] * (v_out - 1.0))
    assert float(np.abs(got - ratio[carries]).max()) < 1e-9
    # The quadrature cells hold the ring's mean: the mask's share at its mean and the rest at theirs is 1.
    assert float(np.abs(share[carries] * v_in + (1.0 - share[carries]) * v_out - 1.0).max()) < 1e-12
    # The ratio is the published one on every ring out to 13.76 kpc, where the disc's gain is whole.
    full = carries & (R < 13.8)
    assert R[full].max() == pytest.approx(13.76, abs=0.005) and np.allclose(ratio[full], C, rtol=0.0, atol=1e-12)
    assert np.all(ratio[carries & ~full] < C) and np.all(ratio[~carries] == 1.0) and np.all(a[~carries] == 0.0)

    dense = np.linspace(0.0, 2.0 * np.pi, 72000, endpoint=False)
    for i in np.nonzero(carries)[0][::16]:
        Ri = float(R[i])
        taper, phase, bar_angle = pt.bar_terms(np.array([Ri]), gp.pitch_deg, gp.bar_length)
        values = gp.contrast_at(np.full_like(dense, Ri), dense)
        ridge = 1.0 + (values - 1.0 - gp.bar * taper[0] * np.cos(2.0 * (dense - bar_angle))) / (1.0 - taper[0])
        inside = gp.rank(np.array([Ri]), (dense - phase[0])[None, :])[0] < share[i]
        assert float(ridge[inside].mean() / ridge[~inside].mean()) == pytest.approx(float(ratio[i]), rel=1e-4), Ri
        assert float(inside.mean()) == pytest.approx(float(share[i]), abs=1e-4)  # the rank is uniform on the ring
    # The share of the ring the mask covers, and the arm number it is computed with (the lead's reading, D215).
    for radius, m_eff, s in ((6.0, 2.972, 0.5), (R_SUN, 3.505, 0.4393), (12.0, 4.881, 0.4135)):
        Ri = np.array([float(R[row(o, radius)])])
        assert float(gp.effective_arm_number(Ri)[0]) == pytest.approx(m_eff, abs=2e-3), radius
        assert float(gp.mask_share(Ri)[0]) == pytest.approx(s, abs=2e-4), radius


def test_the_ridge_fades_with_the_forcing_amplitude(model):
    """Gate ruling 8: C(R) = 1 + (C − 1) ρ(R), ρ = min(1, (Σ u_m²)^½) - "nothing shocks on nothing". The first
    turn's rule set the published ratio on every ring that carried any mode, so on the last one (stellar amplitude
    0.05) the gas still ran 0.34-1.90; it now runs 0.92-1.37 there, and the ridge's amplitude falls to nothing with
    the stellar arms'. No step: a(R) is continuous in ρ, and the ring after the last mode is exactly 1."""
    o = out(model)
    F, R = o.fields, o.grid.R
    gp = shape_of(model, o)
    g = np.asarray(F["gas_density_contrast"])
    amplitudes = np.stack([np.asarray(F[n]) for n in pt.AMPLITUDE_FIELDS])
    last = int(np.nonzero(amplitudes.sum(axis=0) > 0.0)[0].max())
    assert R[last] == pytest.approx(14.81, abs=0.005)
    rho = gp.forcing(R)
    # ρ is the ring's stellar arm amplitude in units of A, before the taper: recomputed from the published fields.
    taper = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0]
    want = np.sqrt((amplitudes**2).sum(axis=0)) / (float(F["arm_contrast"]) * (1.0 - taper))
    assert np.allclose(rho, np.minimum(1.0, want), rtol=1e-12, atol=0.0)
    assert np.all(rho[R < 13.8] == pytest.approx(1.0, abs=1e-15)) and np.all(rho[last + 1:] == 0.0)
    assert np.allclose(gp.ratio_at(R), 1.0 + (gp.ratio - 1.0) * rho, rtol=0.0, atol=1e-15)
    # The gate's prediction for the last ring, as measured: ρ 0.124, C(R) 1.21, the gas within 0.90-1.45.
    assert (float(rho[last]), float(gp.ratio_at(R)[last])) == pytest.approx((0.1239, 1.2143), abs=2e-4)
    assert float(gp.amplitude(R)[last]) == pytest.approx(0.0827, abs=2e-4)
    assert (float(g[last].min()), float(g[last].max())) == pytest.approx((0.9174, 1.3658), abs=2e-3)
    assert 0.90 < g[last].min() and g[last].max() < 1.45
    assert np.all(g[last + 1:] == 1.0)  # past it there is no mode, no mask and no ridge
    # The fade is monotone and without a step: from the last full ring outward ρ, the ratio and the amplitude fall
    # together, ring by ring.
    fading = np.arange(int(np.nonzero(rho > 1.0 - 1e-12)[0].max()), last + 1)
    assert fading.size == 15 and np.all(np.diff(rho[fading]) < 0.0) and np.all(np.diff(gp.amplitude(R)[fading]) < 0.0)
    a = gp.amplitude(R)
    assert np.all(a[fading] <= a[fading[0]]) and a[last] < 0.2 * a[fading[0]]
    # One fully amplified mode has ρ = 1 and the published ratio; a half-amplified one fades half-way.
    single = one_mode(model, 2.73)
    assert np.all(single.forcing(R) == 1.0) and np.all(single.ratio_at(R) == 2.73)
    half = GasPattern(R, 0.5 * single.unit, single.phases, 2.73, 0.0, 13.5, 5.2097, single.width, single.mask_width)
    assert np.all(half.forcing(R) == 0.5) and np.allclose(half.ratio_at(R), 1.865)
    assert np.all(half.amplitude(R) < single.amplitude(R)) and np.all(half.amplitude(R) > 0.0)


# --- the gate: the crest is the form's -----------------------------------------


def test_the_crest_and_the_trough_are_the_form_s_on_every_seed(prod):
    """Gate ruling 10, on the suite's seeds - sixty pattern seeds by two texture seeds for each template's inputs,
    the galaxies the stellar positivity test draws: outside the bar's reach the gas lies in [1 − a(½, C)(1 − v_trough),
    1 + a(½, C)(v_crest − 1)] = [0.534, 3.068] (the exact bounds, not the rounded ones), and inside it within the
    bar's own term B·taper of them; finite everywhere.

    **The law meets it on every ring and every seed, to rounding. The published field does not, by up to 2.6e-3**
    (0.08 % of the crest), and that is recorded here, not mended (B5): the published field is the law at the grid's
    cell centres divided by the ring's sampled mean wherever that has left 1 (the stage's division, there since
    S51 so that every ring keeps its gas on any grid), and a ranked ridge's sampled mean is off 1 by up to 9.5e-4.
    Ruling 10 forbids a clip, cap or floor after composition to obtain the bound; none was added, and the one
    after-composition step that exists is the one that passes it. For the gate to rule."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    law_over, law_under, over, under, mean_off, drawn = -1.0, -1.0, -1.0, -1.0, 0.0, 0
    for template in ("milky_way", "ngc_4414"):
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = {**templates.overrides(templates.TEMPLATES[template]), "pattern_seed": pattern_seed, "texture_seed": texture_seed}
                # The pattern's own fields alone; the published gas field is made from the law below exactly as
                # the stage makes it (the test above holds the stage to that on the default galaxy).
                o = run(model, given, only=GAS_PATTERN_READS)
                R, phi = o.grid.R, o.grid.phi
                gp = compose.gas_pattern(o.fields, R, c)
                assert gp is not None and not gp.flat
                lo, hi = bounds(gp)
                bar = gp.bar * pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0]
                law = gp.contrast(R, phi)
                assert np.all(np.isfinite(law)), (template, pattern_seed, texture_seed)
                sampled = law.mean(axis=1, keepdims=True)
                left = np.abs(sampled - 1.0) > gm.RING_MEAN_TOLERANCE
                g = np.where(left, law / np.where(left, sampled, 1.0), law)
                drawn += 1
                law_over = max(law_over, float((law - (hi + bar)[:, None]).max()))
                law_under = max(law_under, float(((lo - bar)[:, None] - law).max()))
                over = max(over, float((g - (hi + bar)[:, None]).max()))
                under = max(under, float(((lo - bar)[:, None] - g).max()))
                mean_off = max(mean_off, float(np.abs(sampled - 1.0).max()))
                assert float(np.abs(g.mean(axis=1) - 1.0).max()) < 1e-12 and g.min() >= 0.0
    assert drawn == 240
    assert (lo, hi) == pytest.approx((0.533963, 3.067524), abs=2e-6)
    # The law: inside the exact bound on all 240 (the margins are rounding's).
    assert law_over <= 1e-10 and law_under <= 1e-10
    # The published field: the gate as worded fails by this much, measured.
    assert over == pytest.approx(2.56e-3, abs=1e-4) and under == pytest.approx(5.1e-4, abs=1e-4)
    assert mean_off == pytest.approx(9.5e-4, abs=5e-5)


def test_the_default_field_s_range_and_what_the_spike_was(model):
    """The predictions for the default galaxy, as measured: no cell above 4 (the exponential's field had 1.0 % of
    its cells there, holding 8.8 % of the gas); the field's range; ⟨g²⟩; and at R0 the crest and the trough."""
    o = out(model)
    F, R = o.fields, o.grid.R
    g = np.asarray(F["gas_density_contrast"])
    gp = shape_of(model, o)
    lo, hi = bounds(gp)
    assert not np.any(g > 4.0)
    far = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0] < 1e-6
    # Outside the bar's reach: inside the form's bound (the sampled mean's factor is under the margin here).
    assert lo < g[far].min() and g[far].max() < hi
    assert (float(g[far].min()), float(g[far].max())) == pytest.approx((0.5689, 2.9114), abs=2e-3)
    # Each ring's mean square is 1 + a²·Var(V): 1.53 at R0, under S51's 1.606 at the cap; 1.23 by gas mass over
    # the whole disc (the exponential's ring at 12 kpc read 5.10).
    i = row(o, R_SUN)
    assert float((g[i] ** 2).mean()) == pytest.approx(1.529, abs=3e-3)
    weight = np.asarray(F["gas_surface_density"]) * R
    assert float(((g**2).mean(axis=1) * weight).sum() / weight.sum()) == pytest.approx(1.226, abs=3e-3)


# --- (d): the ratio derived, the field seeded through the pattern ----------------


def test_the_field_moves_with_the_pattern_seed_and_not_the_world_seed(model):
    """The field is seeded through the pattern's drawn pitch, amplitudes and bar and the layer's phases (graph
    labels it so, D55); the stage itself reads no seed and draws nothing (D210 as amended)."""
    a = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    b = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    c = run(model, {"pattern_seed": 8}, grid=COARSE).fields
    w = run(model, {"pattern_seed": 7, "world_seed": 12345}, grid=COARSE).fields
    t = run(model, {"pattern_seed": 7, "texture_seed": 9}, grid=COARSE, only=("gas_density_contrast",)).fields
    assert np.array_equal(a["gas_density_contrast"], b["gas_density_contrast"])
    assert not np.array_equal(a["gas_density_contrast"], c["gas_density_contrast"])
    assert np.array_equal(a["gas_density_contrast"], w["gas_density_contrast"])
    assert not np.array_equal(a["gas_density_contrast"], t["gas_density_contrast"])  # S56: the phases are the layer's
    assert GAS_PATTERN.reads_seeds == ()
    assert [d.provenance for d in GAS_PATTERN.publishes] == ["seeded"]


def test_the_ratio_is_the_derived_class_mean_and_no_draw(model):
    """C is the bar stage's: 2.73 at the defaults (m = 2 inside the swing window, coherence 1), and
    the same under every pattern seed — no residual, since the source's spread is over segments
    and bins, not galaxies (#131)."""
    assert float(out(model).fields["gas_arm_contrast"]) == pytest.approx(2.73, abs=1e-12)
    values = {run(model, {"pattern_seed": s}, grid=COARSE).fields["gas_arm_contrast"] for s in range(6)}
    assert len(values) == 1


# --- (e), (f): on the crest, and narrower ---------------------------------------


def test_the_ridge_sits_on_the_stellar_crest(model):
    """No offset (D210 ruling 3): outside the bar the two fields peak in the same φ cell - the ridge's value falls
    with the rank, so its highest value sits where the stellar modes' sum is highest on the ring."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    s = np.asarray(o.fields["pattern_density_contrast"])
    n = o.grid.phi.size
    for R in (8.0, 12.0, 14.0):
        i = row(o, R)
        d = abs(int(g[i].argmax()) - int(s[i].argmax()))
        assert min(d, n - d) <= 1, R
    # And the whole order is the stellar one: at a ring outside the bar the gas ranks its cells as the stars do.
    i = row(o, 12.0)
    assert np.array_equal(np.argsort(-g[i], kind="stable"), np.argsort(-s[i], kind="stable"))


def full_width_cells(values: np.ndarray) -> float:
    """Cells above the half level between the row's crest and trough."""
    half = 0.5 * (values.max() + values.min())
    return float((values > half).sum())


def test_the_ridge_is_narrower_than_the_stellar_arm(model):
    """One mode, at 12 kpc (bar weight e^-28): the gas's FWHM is 0.17 of the arm period to a cell, the
    stellar cosine's 0.5 — both in φ cells per arm. And on the default galaxy's five modes the same share of the
    ring stands above the ridge's half level, 0.17, wherever the crests are: every ring has one arm's histogram."""
    grid = DEFAULT.build()
    m = 4
    gas = one_mode(model, 2.73)
    stars = pt.ArmPattern(grid.R, np.where(gas.unit > 0.0, 0.4, 0.0), (0.0,) * 5, 0.0, 13.5, 5.2097)
    i = int(np.argmin(np.abs(grid.R - 12.0)))
    cells_per_period = grid.phi.size / m
    width_gas = full_width_cells(gas.contrast(grid.R, grid.phi)[i]) / m
    width_stars = full_width_cells(stars.contrast(grid.R, grid.phi)[i]) / m
    assert width_gas == pytest.approx(0.17 * cells_per_period, abs=1.0)
    assert width_stars == pytest.approx(0.5 * cells_per_period, abs=1.0)
    assert width_gas < 0.5 * width_stars
    # S56 (D215): the default galaxy was that one mode (m = 4); it is five modes now, ranked.
    o = out(model)
    i = row(o, 12.0)
    n = o.grid.phi.size
    assert full_width_cells(np.asarray(o.fields["gas_density_contrast"])[i]) / n == pytest.approx(0.17, abs=0.006)
    assert full_width_cells(np.asarray(o.fields["pattern_density_contrast"])[i]) / n == pytest.approx(0.436, abs=0.01)


# --- (g): the worked numbers ------------------------------------------------------


def test_the_worked_numbers_at_the_defaults(model):
    """κ, v(0) and v(π) for W = 0.17, and D210's worked table (four arms, pitch 13.5 deg, the clamp).

    κ = 4.9774. **v(0) = 5.435, not D210's 4.93**: D210's own crests need v(0) ≈ 5.4 (1 + 0.462
    × 4.435 = 3.05), so 4.93 is a slip in the entry. Recomputed here with the stage's quadrature on one
    four-armed mode, against D210's: C = 2.73 → a 0.466 (0.462), crest 3.068 (3.04), trough 0.534 (0.54);
    C = 1.90 → 0.312 (0.308), 2.383 (2.36), 0.688 (0.69); C = 5.79 → 0.709 (0.706), 4.144 (4.12), 0.291
    (0.29); C = 2.73 at 12 kpc → crest 2.716 (2.69), trough 0.613 (0.62). All within 1.3 %.
    """
    c = constants(model)
    kappa = kappa_for_width(c["GAS_ARM_WIDTH"])
    assert kappa == pytest.approx(4.977, abs=1e-3)
    # The ridge's values are the von Mises's (S51's closed form, the frozen copy's): its crest, trough and half width.
    v0, vpi = float(ridge_value(0.0, kappa)), float(ridge_value(1.0, kappa))
    assert v0 == float(s55.von_mises(np.array(0.0), kappa)) and vpi == pytest.approx(float(s55.von_mises(np.array(math.pi), kappa)), rel=1e-14)
    assert v0 == pytest.approx(5.435, abs=1e-3)
    assert vpi == pytest.approx(2.58e-4, rel=1e-2)
    # The FWHM relation is exact: V at rank W is half the crest's.
    assert float(ridge_value(c["GAS_ARM_WIDTH"], kappa)) == pytest.approx(0.5 * v0, rel=1e-12)
    assert one_mode(model, 2.73).extremes() == pytest.approx((v0, vpi), rel=1e-14)

    def worked(C: float, R: float, pitch: float = 13.5) -> tuple[float, float, float]:
        a = float(one_mode(model, C, pitch=pitch).amplitude(np.array([R]))[0])
        return a, 1.0 + a * (v0 - 1.0), 1.0 + a * (vpi - 1.0)

    for C, R, want in ((2.73, R_SUN, (0.462, 3.04, 0.54)), (1.90, R_SUN, (0.308, 2.36, 0.69)),
                       (5.79, R_SUN, (0.706, 4.12, 0.29))):
        assert worked(C, R) == pytest.approx(want, rel=0.015), C
    a12, crest12, trough12 = worked(2.73, 12.0)
    assert (crest12, trough12) == pytest.approx((2.69, 0.62), rel=0.015)
    # S51's own numbers at the default galaxy's drawn pitch, one four-armed mode: the model's until S56.
    pitch = float(out(model).fields["pitch_angle"])
    for R, want in ((R_SUN, (0.466, 3.068, 0.534)), (12.0, (0.387, 2.715, 0.613))):
        assert worked(2.73, R, pitch) == pytest.approx(want, abs=1e-3), R

    # The defaults' own ridge, at R0 and 12 kpc (the module docstring's numbers).
    o = out(model)
    gp = shape_of(model, o)
    assert float(o.fields["gas_arm_contrast"]) == pytest.approx(2.73, abs=1e-12)
    g = np.asarray(o.fields["gas_density_contrast"])
    # S56 (D215): was a 0.466, crest 3.068, trough 0.534 at R0 and 0.387, 2.715, 0.613 at 12 kpc - one four-armed
    # mode, whose mask is at its cap at R0. Five modes ranked: the mask's share follows the ring's power-weighted
    # arm number (3.5 at R0, 4.9 at 12 kpc), under the cap at both, and the crest is the form's at that share.
    # (The gate predicted "crest in [2.9, 3.07], trough in [0.53, 0.58]" off the cap: held at R0, and 2.88 at 12 kpc.)
    for R, (a_want, crest_want, trough_want) in ((R_SUN, (0.4367, 2.9317, 0.5637)), (12.0, (0.4238, 2.8795, 0.5763))):
        i = row(o, R)
        a = float(gp.amplitude(np.array([float(o.grid.R[i])]))[0])
        assert (a, float(g[i].max()), float(g[i].min())) == pytest.approx((a_want, crest_want, trough_want), abs=2e-3), R
        # The crest and the trough the form allows on this ring; the grid's cells sample just inside them.
        assert g[i].max() <= (1.0 + a * (v0 - 1.0)) * (1.0 + 1e-3) and g[i].min() >= (1.0 + a * (vpi - 1.0)) * (1.0 - 1e-3)
    # S56 (D215): was (0.535, 3.061)
    assert (float(g.min()), float(g.max())) == pytest.approx((0.5572, 2.9403), abs=2e-3)


def test_the_mask_s_sums_are_s51_s_and_the_rank_is_the_measure(model):
    """The mask's means are sums of the ridge's values over the fixed cells of the rank, from the crest outward:
    S51's cells and S51's sums, so a(R) is S51's number at the same share - with its quadrature's own error against
    the integral (2e-7 of v_in at the cap, 7e-5 at a half-width of 0.5), which a finer rule would not reproduce.
    And one mode's rank is |θ|/π, through the general method: the crossings refined, not the cells counted."""
    assert PHASE_CELLS == s55.PHASE_CELLS == 360
    assert [pattern_period(1 << k) for k in range(5)] == [2, 3, 4, 5, 6]
    assert pattern_period(0b00101) == 2 and pattern_period(0b10010) == 3 and pattern_period(0b00011) == 1
    assert pattern_period(0b11111) == 1 and pattern_period(0) == 1
    c = constants(model)
    grid = DEFAULT.build()
    R, phi = grid.R, grid.phi
    for m in (2, 4, 6):
        gp = one_mode(model, 2.73, m=m, pitch=13.5378)
        old = s55.gas_amplitude(R, 2.73, float(m), 13.5378, c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])
        assert float(np.abs(gp.amplitude(R) - old).max()) < 1e-13, m
        half_width = np.clip(s55.mask_half_width(R, float(m), 13.5378, c["GAS_ARM_MASK_WIDTH"]), math.pi / 360.0, 0.5 * math.pi)
        assert np.allclose(gp.mask_share(R) * math.pi, half_width, rtol=1e-14)
        v_in, v_out = mask_means(gp.mask_share(R), gp.kappa)
        old_in, old_out = s55.mask_means(half_width, gp.kappa)
        assert float(np.abs(v_in - old_in).max()) < 1e-13 and float(np.abs(v_out - old_out).max()) < 1e-13
        # The rank: q = |θ|/π at every cell of the grid. To 1e-10: a cell that sits within 1e-6 of a crest has its
        # mirror crossing determined only to ψ's rounding over its slope there (measured 2.5e-11 at worst).
        _, phase, _ = pt.bar_terms(R, 13.5378, 5.2097)
        theta = np.mod(m * (phi[None, :] - phase[:, None]) + math.pi, 2.0 * math.pi) - math.pi
        q = gp.rank(R, phi[None, :] - phase[:, None])
        assert float(np.abs(q - np.abs(theta) / math.pi).max()) < 1e-10, m
        # A linearly interpolated rank of the grid's own cells is not it: 1e-3 off here, and 1e-5 in the field.
        ranked = (np.argsort(np.argsort(-np.cos(theta[200]), kind="stable"), kind="stable") + 0.5) / phi.size
        assert float(np.abs(ranked - np.abs(theta[200]) / math.pi).max()) > 1e-4
    # S51's mask means against the integral, for the record of what is being reproduced.
    kappa = kappa_for_width(c["GAS_ARM_WIDTH"])
    t = (np.arange(400_000) + 0.5) * (2.0 * np.pi / 400_000) - np.pi
    v = s55.von_mises(t, kappa)
    for theta_m in (0.5 * np.pi, 1.068, 0.5):
        v_in, v_out = mask_means(np.array([theta_m / math.pi]), kappa)
        inside = np.abs(t) < theta_m
        assert float(v_in[0]) == pytest.approx(float(v[inside].mean()), abs=5e-4), theta_m
        assert float(v_out[0]) == pytest.approx(float(v[~inside].mean()), abs=1e-4), theta_m


def oracle_rank(unit: np.ndarray, theta: np.ndarray, chi: float) -> float:
    """The rank by another road: ψ − ψ(χ) times e^{6iχ} is a polynomial of degree 12 in e^{iχ}; its roots on the
    unit circle are the crossings, all of them, and the superlevel set is read between them."""
    m = np.asarray(pt.ARM_MODES)
    a, b = unit * np.cos(theta), unit * np.sin(theta)
    psi = lambda x: float((a * np.cos(m * x) + b * np.sin(m * x)).sum())  # noqa: E731
    level = psi(chi)
    coefficients = np.zeros(13, dtype=complex)
    for k, mode in enumerate(m):
        coefficients[6 + mode] += (a[k] - 1j * b[k]) / 2.0
        coefficients[6 - mode] += (a[k] + 1j * b[k]) / 2.0
    coefficients[6] -= level
    roots = np.roots(coefficients[::-1])
    angles = np.sort(np.mod(np.angle(roots[np.abs(np.abs(roots) - 1.0) < 1e-6]), 2.0 * math.pi))
    edges = np.concatenate([angles, [angles[0] + 2.0 * math.pi]])
    inside = np.array([psi(x) > level for x in 0.5 * (edges[1:] + edges[:-1])])
    return float(((edges[1:] - edges[:-1]) * inside).sum() / (2.0 * math.pi))


def test_the_rank_is_the_measure_of_the_superlevel_set(model):
    """q against an independent computation on rings of several modes: every crossing of ψ − ψ(point) as a root of
    the degree-12 polynomial in e^{iχ}. Agreement to 1e-11 (measured 4e-13): the crossings are refined, each inside
    its own bracket between two nodes, and none is missed where ψ turns inside a cell."""
    gp = shape_of(model, out(model))
    rng = np.random.default_rng(3)  # the test's own points, not the model's
    worst = 0.0
    for radius in (1.0, 3.3, 6.1, R_SUN, 10.4, 12.2, 13.9, 14.5):
        unit = gp.unit_at(np.array([radius]))[:, 0]
        assert unit.any()
        chi = rng.uniform(-math.pi, math.pi, 40)
        q = gp.rank(np.array([radius]), chi[None, :])[0]
        assert np.all((q >= 0.0) & (q <= 1.0))
        want = np.array([oracle_rank(unit, np.asarray(gp.phases), float(x)) for x in chi])
        worst = max(worst, float(np.abs(q - want).max()))
    assert worst < 1e-11
    # The rank is uniform on the ring - that is what makes every ring's histogram the same: on a dense ring its
    # mean is a half and the share below any level is the level.
    dense = np.linspace(-math.pi, math.pi, 20000, endpoint=False)
    q = gp.rank(np.array([R_SUN]), dense[None, :])[0]
    assert float(q.mean()) == pytest.approx(0.5, abs=1e-4)
    for level in (0.1, 0.17, 0.5, 0.9):
        assert float((q < level).mean()) == pytest.approx(level, abs=2e-4)
    # The steps are counted in advance (A1), and a refined crossing is bounded to the tolerance.
    assert (gm.NEWTON_STEPS, gm.BISECTION_STEPS, gm.CROSSING_TOLERANCE) == (6, 40, 1e-12)
    assert 2.0 * math.pi / PHASE_CELLS / 2.0**gm.BISECTION_STEPS < gm.CROSSING_TOLERANCE


# --- (h): one function at points and on the grid ----------------------------------


def test_contrast_at_agrees_with_the_grid(model):
    o = out(model)
    gp = shape_of(model, o)
    R, phi = o.grid.R, o.grid.phi
    on_grid = gp.contrast(R, phi)
    # The published field is the law's samples over their ring mean (S56: was the samples themselves, to 1e-12).
    assert np.allclose(on_grid / on_grid.mean(axis=1, keepdims=True), np.asarray(o.fields["gas_density_contrast"]), rtol=0.0, atol=1e-11)
    assert np.allclose(gp.contrast_at(R[:, None], phi[None, :]), on_grid, rtol=0.0, atol=1e-12)
    idx = np.array([5, 77, 190, 399]), np.array([0, 91, 180, 359])
    assert np.allclose(gp.contrast_at(R[idx[0]], phi[idx[1]]), on_grid[idx], rtol=0.0, atol=1e-12)
    # Points that share a radius unevenly: each is the single point's value.
    radii = np.concatenate([np.full(7, R[100]), np.full(3, R[150])])
    azimuths = np.linspace(0.3, 5.9, 10)
    alone = np.array([gp.contrast_at(np.array([r]), np.array([p]))[0] for r, p in zip(radii, azimuths)])
    assert np.allclose(gp.contrast_at(radii, azimuths), alone, rtol=0.0, atol=1e-12)


def test_azimuths_fall_inside_the_sector_and_follow_the_ridge(model):
    gp = shape_of(model, out(model))
    u = np.random.default_rng(0).random(20000)
    radius = np.full(u.size, 12.0)
    phi = gp.azimuths(u, radius, 0.0, 2.0 * np.pi, steps=720)
    assert np.all((phi >= 0.0) & (phi <= 2.0 * np.pi))
    # Drawn by the contrast, the stars sit where it is high: their mean contrast is the ring's
    # mean square, well above 1 — to sampling noise, about 0.5 %.
    ring = np.linspace(0.0, 2.0 * np.pi, 36000, endpoint=False)
    mean_square = float((gp.contrast_at(np.full_like(ring, 12.0), ring) ** 2).mean())
    # S56 (D215): was 1.42 for one four-armed mode's ridge at 12 kpc (a 0.387); 1.50 by rank (a 0.424).
    assert mean_square == pytest.approx(1.500, abs=0.005)
    assert float(gp.contrast_at(radius, phi).mean()) == pytest.approx(mean_square, rel=0.02)


# --- (i), (j): what the stage reads, where it sits ----------------------------------


def test_the_stage_reads_no_gas_and_sits_at_checkpoint_three():
    assert GAS_PATTERN.checkpoint == 3 == PATTERN.checkpoint
    # No gas column: the one gas name it reads is the bar stage's derived ratio, a scalar.
    assert [n for n in GAS_PATTERN.requires if "gas" in n] == ["gas_arm_contrast"]
    # S56 (D215): until S56 it read "the stellar pattern's numbers, not its amplitude" - a drawn arm number, and
    # `"arm_contrast" not in requires`. The ridge now follows the stellar modes scaled to unit amplitude, so it reads
    # the arm amplitude they are scaled by, the modes and their phases - and no arm number.
    assert GAS_PATTERN.requires == GAS_PATTERN_READS == ("gas_arm_contrast", "arm_contrast", *pt.PATTERN_READS)
    assert "arm_multiplicity" not in GAS_PATTERN.requires
    assert set(pt.AMPLITUDE_FIELDS) | set(pt.PHASE_FIELDS) <= set(GAS_PATTERN.requires)
    assert GAS_PATTERN.reads_seeds == ()
    assert {d.name for d in GAS_PATTERN.publishes} == {"gas_density_contrast"}
    # The retired form is gone from the source: nothing takes the exponential of a sum of modes (D215: forbidden).
    import inspect

    source = inspect.getsource(gm)
    assert "np.exp(kappa * (unit" not in source and "np.exp(self.kappa * psi" not in source


def test_both_models_run_the_gas_pattern_after_the_pattern(model):
    slots = [slot for slot, _ in model.stages]
    assert dict(model.stages)["gas_pattern"] == "gas_pattern"
    assert slots.index("gas_pattern") == slots.index("pattern") + 1


def test_a_flat_pattern_publishes_ones(model):
    assert one_mode(model, 2.73, bar=float("nan"), pitch=float("nan")).flat
    assert one_mode(model, 1.0).flat
    assert not one_mode(model, 2.73).flat
    # A ring that carries no mode: the ridge is 1 and no mask is formed (D215, gate ruling 7).
    gp = one_mode(model, 2.73)
    R = gp.R
    none = GasPattern(R, np.where(R[None, :] < 10.0, gp.unit, 0.0), gp.phases, 2.73, 0.0, 13.5, 5.2097, gp.width, gp.mask_width)
    field = none.contrast(R, DEFAULT.build().phi)
    assert np.all(field[R >= 10.0] == 1.0) and not np.all(field[R < 10.0] == 1.0)
    assert np.all(none.amplitude(R[R >= 10.0]) == 0.0) and np.all(np.isnan(none.mask_share(R[R >= 10.0])))
    assert np.all(np.isnan(none.rank(R[R >= 10.0], np.zeros((int((R >= 10.0).sum()), 3)))))
