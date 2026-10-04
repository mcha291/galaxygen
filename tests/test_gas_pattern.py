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

**Since S56 the default galaxy carries five modes** (both models; run on 2026-10-04) and the ridge
is the exponential of their sum at unit amplitude: where their crests meet the sum reaches 2.19 at
R0 against 1 for one mode, so the ridge is far sharper - **a = 0.433, crest 11.27, trough 0.568 at
R0** (S51: 0.466, 3.07, 0.53); at 12 kpc a = 0.418, crest 15.48, trough 0.582. The field runs
0.336-15.53 over the whole grid; 1.0 % of its cells lie above 4 and hold 8.8 % of the gas. The
ratio of means over the mask is still 2.73 on every ring that carries a mode - including the last
(14.81 kpc), where the stellar modes' amplitude is 0.05 and the gas ridge still runs 0.34-1.90.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import s55_patterns as s55
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.run import run
from galaxy.stages import pattern as pt
from galaxy.stages.gas_pattern import (
    GAS_PATTERN,
    GAS_PATTERN_READS,
    PHASE_CELLS,
    GasPattern,
    kappa_for_width,
    pattern_period,
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


def row(o, R: float) -> int:
    return int(np.argmin(np.abs(o.grid.R - R)))


# --- (a), (b): a redistribution, not a source ---------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g >= 0.0) and np.all(np.isfinite(g))
    assert np.allclose(g.mean(axis=1), 1.0, atol=1e-9)


def test_every_ring_keeps_its_gas_on_a_coarse_phi_grid(model):
    """Sampled at cell centres on 36 cells, a ridge's harmonics alias onto the grid (one four-armed mode's ninth:
    6e-4 of the ring's mean, found by Phase 2's builder at S51; with six-armed modes the sixth). The stage divides
    such a ring by its sampled mean, and leaves the default grid's field the law's own, bit for bit (nothing there
    aliases)."""
    coarse = run(model, grid=GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36), only=("gas_density_contrast",))
    g = np.asarray(coarse.fields["gas_density_contrast"])
    assert np.all(g >= 0.0) and float(np.abs(g.mean(axis=1) - 1.0).max()) < 1e-12
    o = out(model)
    closed = shape_of(model, o).contrast(o.grid.R, o.grid.phi)
    np.testing.assert_array_equal(np.asarray(o.fields["gas_density_contrast"]), closed)


def test_the_sector_means_average_to_one_and_are_exact(model):
    """Twelve sectors at four radii: their mean is the ring's, 1; and each sector's mean is the
    dense numerical average of contrast_at over it (the series is exact to its dropped tail)."""
    gp = shape_of(model, out(model))
    edges = np.linspace(0.0, 2.0 * np.pi, 13)
    for R in (1.0, 3.0, 6.0, 12.0):
        means = gp.sector_means(R, edges)
        assert float(means.mean()) == pytest.approx(1.0, abs=1e-9)
        dense = []
        for a, b in zip(edges[:-1], edges[1:]):
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000  # midpoint, error ~1e-6 at this ridge
            dense.append(float(gp.contrast_at(np.full_like(phi, R), phi).mean()))
        # S56 (D215): was atol 1e-6, on one mode's ridge; several modes' crests are sharper for the midpoint rule.
        assert np.allclose(means, dense, atol=5e-6), (R, float(np.abs(means - np.array(dense)).max()))
        assert means.max() > 1.0 > means.min()  # the ridge is resolved: not a flat ring


# --- (c): the ratio of means is the published one -----------------------------


def test_the_ratio_of_means_over_the_mask_is_the_published_contrast(model):
    """Recomputed from the field, independently of the stage's quadrature: the bar term and the arm weight taken
    back off with the stellar pattern's published numbers, psi rebuilt from the published mode amplitudes and
    phases, and the mask the share of the ring where psi is highest - the share the source's mask covers,
    m_eff W/(2 pi R sin p), at most a half. On the grid's own 360 cells the mask's edge cuts where it falls, so the
    check is to 2e-3 of C; on a dense ring it is 2e-4 (S56, D215: was 2e-5 with one mode's 360 cells per arm period;
    several modes share 360 cells per ring). **Every ring that carries a mode has the ratio, however faint the
    stellar pattern**: the last one too."""
    o = out(model)
    F = o.fields
    c = constants(model)
    C = float(F["gas_arm_contrast"])
    A, p, B, a_bar = (float(F[k]) for k in ("arm_contrast", "pitch_angle", "bar_contrast", "bar_half_length"))
    g = np.asarray(F["gas_density_contrast"])
    gp = shape_of(model, o)
    amplitudes = np.stack([np.asarray(F[n]) for n in pt.AMPLITUDE_FIELDS])
    theta = [float(F[n]) for n in pt.PHASE_FIELDS]

    def ratio(i: int, phi: np.ndarray, values: np.ndarray) -> float:
        R = float(o.grid.R[i])
        taper, phase, bar_angle = pt.bar_terms(np.array([R]), p, a_bar)
        ridge = 1.0 + (values - 1.0 - B * taper[0] * np.cos(2.0 * (phi - bar_angle))) / (1.0 - taper[0])
        unit = amplitudes[:, i] / (A * (1.0 - taper[0]))
        psi = sum(u * np.cos(m * (phi - phase[0]) - t) for u, m, t in zip(unit, pt.ARM_MODES, theta))
        m_eff = float((np.asarray(pt.ARM_MODES) * unit**2).sum() / (unit**2).sum())
        share = min(m_eff * c["GAS_ARM_MASK_WIDTH"] / (2.0 * math.pi * R * math.sin(math.radians(p))), 0.5)
        inside = psi > np.quantile(psi, 1.0 - share)
        return float(ridge[inside].mean() / ridge[~inside].mean())

    last = int(np.nonzero(amplitudes.sum(axis=0) > 0.0)[0].max())
    assert o.grid.R[last] == pytest.approx(14.81, abs=0.005)
    for R in (6.0, R_SUN, 12.0, 14.0, float(o.grid.R[last])):
        i = row(o, R)
        Ri = float(o.grid.R[i])
        assert ratio(i, o.grid.phi, g[i]) == pytest.approx(C, rel=2e-3), R
        dense = np.linspace(0.0, 2.0 * np.pi, 72000, endpoint=False)
        assert ratio(i, dense, gp.contrast_at(np.full_like(dense, Ri), dense)) == pytest.approx(C, rel=2e-4), R
    # The share of the ring the mask covers, and the arm number it is computed with (the lead's reading, D215).
    for R, m_eff, share in ((6.0, 2.972, 0.5), (R_SUN, 3.505, 0.4393), (12.0, 4.881, 0.4135)):
        Ri = np.array([float(o.grid.R[row(o, R)])])
        assert float(gp.effective_arm_number(Ri)[0]) == pytest.approx(m_eff, abs=2e-3), R
        assert float(gp.mask_share(Ri)[0]) == pytest.approx(share, abs=2e-4), R
    # What the rule does where the stellar pattern fades, measured: the last ring's stellar modes have an amplitude
    # of 0.05, and the gas's ridge there still runs from 0.34 to 1.90 - the ratio of means is kept, so a(R) grows as
    # the ridge flattens (1.31 against 0.43 at R0). "The gas fades with the potential that drives it" (D215, gate
    # ruling 6) does not hold of the field as built: recorded, not adjusted (B5).
    assert float(gp.amplitude(np.array([float(o.grid.R[last])]))[0]) == pytest.approx(1.306, abs=2e-3)
    assert (float(g[last].max()), float(g[last].min())) == pytest.approx((1.899, 0.336), abs=2e-3)
    assert np.all(g[last + 1:] == 1.0)  # and past it there is no mode, no mask and no ridge


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
    """No offset (D210 ruling 3): outside the bar the two fields peak in the same φ cell - the ridge is a rising
    function of the stellar modes' sum, so with several modes it peaks where their crests meet."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    s = np.asarray(o.fields["pattern_density_contrast"])
    n = o.grid.phi.size
    for R in (8.0, 12.0, 14.0):
        i = row(o, R)
        d = abs(int(g[i].argmax()) - int(s[i].argmax()))
        assert min(d, n - d) <= 1, R


def full_width_cells(values: np.ndarray) -> float:
    """Cells above the half level between the row's crest and trough."""
    half = 0.5 * (values.max() + values.min())
    return float((values > half).sum())


def test_the_ridge_is_narrower_than_the_stellar_arm(model):
    """One mode, at 12 kpc (bar weight e^-28): the gas's FWHM is 0.17 of the arm period to a cell, the
    stellar cosine's 0.5 — both in φ cells per arm. And on the default galaxy's five modes the ridge is
    narrower still: the cells above its half level are 2.5 % of the ring against the stars' 44 %."""
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
    # S56 (D215): the default galaxy was that one mode (m = 4); it is five modes now.
    o = out(model)
    i = row(o, 12.0)
    n = o.grid.phi.size
    assert full_width_cells(np.asarray(o.fields["gas_density_contrast"])[i]) / n == pytest.approx(0.025, abs=0.005)
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
    # One mode's ridge is the von Mises (S51's closed form, the frozen copy's): its crest, trough and half width.
    v0 = float(s55.von_mises(np.array(0.0), kappa))
    vpi = float(s55.von_mises(np.array(math.pi), kappa))
    assert v0 == pytest.approx(5.435, abs=1e-3)
    assert vpi == pytest.approx(2.58e-4, rel=1e-2)
    # The FWHM relation is exact: v(±πW) = v(0)/2.
    assert float(s55.von_mises(np.array(math.pi * c["GAS_ARM_WIDTH"]), kappa)) == pytest.approx(0.5 * v0, rel=1e-12)

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
    # S56 (D215): was a 0.466, crest 3.068, trough 0.534 at R0 and 0.387, 2.715, 0.613 at 12 kpc - one mode's
    # von Mises; five modes' crests meet, and the exponential of their sum is far sharper.
    for R, (a_want, crest_want, trough_want) in ((R_SUN, (0.433, 11.265, 0.568)), (12.0, (0.418, 15.482, 0.582))):
        i = row(o, R)
        a = float(gp.amplitude(np.array([float(o.grid.R[i])]))[0])
        assert (a, float(g[i].max()), float(g[i].min())) == pytest.approx((a_want, crest_want, trough_want), abs=2e-3), R
    # S56 (D215): was (0.535, 3.061)
    assert (float(g.min()), float(g.max())) == pytest.approx((0.336, 15.528), abs=2e-3)
    # How much of the ring the sharp crests are: 1.0 % of the cells lie above 4, holding 8.8 % of the gas.
    assert float((g > 4.0).mean()) == pytest.approx(0.0102, abs=5e-4)
    assert float((g * (g > 4.0)).mean()) == pytest.approx(0.0880, abs=2e-3)


def test_the_quadrature_is_one_period_of_the_ring_s_pattern_and_s51_s_for_one_mode(model):
    """The ring's mean and the mask's means are midpoint sums over 360 cells across one period of the ring's
    pattern: 2 pi over the greatest common divisor of the arm numbers the ring carries. For one mode that is the
    arm-to-arm period and the cells are S51's, so a(R) is S51's number - with its quadrature's own error against
    the integral (2e-7 of v_in at the clamp, 7e-5 at a half-width of 0.5), which a finer rule would not reproduce."""
    assert PHASE_CELLS == s55.PHASE_CELLS == 360
    assert [pattern_period(1 << k) for k in range(5)] == [2, 3, 4, 5, 6]
    assert pattern_period(0b00101) == 2 and pattern_period(0b10010) == 3 and pattern_period(0b00011) == 1
    assert pattern_period(0b11111) == 1 and pattern_period(0) == 1
    c = constants(model)
    R = DEFAULT.build().R
    for m in (2, 4, 6):
        gp = one_mode(model, 2.73, m=m, pitch=13.5378)
        old = s55.gas_amplitude(R, 2.73, float(m), 13.5378, c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])
        assert float(np.abs(gp.amplitude(R) - old).max()) < 1e-13, m
        assert np.allclose(gp.mask_share(R) * math.pi, np.clip(s55.mask_half_width(R, float(m), 13.5378, c["GAS_ARM_MASK_WIDTH"]),
                                                              math.pi / 360.0, 0.5 * math.pi), rtol=1e-14)
    # S51's mask means against the integral, for the record of what is being reproduced.
    kappa = kappa_for_width(c["GAS_ARM_WIDTH"])
    t = (np.arange(400_000) + 0.5) * (2.0 * np.pi / 400_000) - np.pi
    v = s55.von_mises(t, kappa)
    for theta_m in (0.5 * np.pi, 1.068, 0.5):
        v_in, v_out = s55.mask_means(np.array([theta_m]), kappa)
        inside = np.abs(t) < theta_m
        assert float(v_in[0]) == pytest.approx(float(v[inside].mean()), abs=5e-4), theta_m
        assert float(v_out[0]) == pytest.approx(float(v[~inside].mean()), abs=1e-4), theta_m


# --- (h): one function at points and on the grid ----------------------------------


def test_contrast_at_agrees_with_the_grid(model):
    o = out(model)
    gp = shape_of(model, o)
    R, phi = o.grid.R, o.grid.phi
    on_grid = gp.contrast(R, phi)
    assert np.allclose(on_grid, np.asarray(o.fields["gas_density_contrast"]), rtol=0.0, atol=1e-12)
    assert np.allclose(gp.contrast_at(R[:, None], phi[None, :]), on_grid, rtol=0.0, atol=1e-12)
    idx = np.array([5, 77, 200, 399]), np.array([0, 91, 180, 359])
    assert np.allclose(gp.contrast_at(R[idx[0]], phi[idx[1]]), on_grid[idx], rtol=0.0, atol=1e-12)


def test_azimuths_fall_inside_the_sector_and_follow_the_ridge(model):
    gp = shape_of(model, out(model))
    u = np.random.default_rng(0).random(20000)
    radius = np.full(u.size, 12.0)
    phi = gp.azimuths(u, radius, 0.0, 2.0 * np.pi, steps=720)
    assert np.all((phi >= 0.0) & (phi <= 2.0 * np.pi))
    # Drawn by the contrast, the stars sit where it is high: their mean contrast is the ring's
    # mean square, well above 1 — to sampling noise.
    ring = np.linspace(0.0, 2.0 * np.pi, 36000, endpoint=False)
    mean_square = float((gp.contrast_at(np.full_like(ring, 12.0), ring) ** 2).mean())
    # S56 (D215): was 1.42 for one mode's ridge; 5.10 for five modes' (their crests meet).
    assert mean_square == pytest.approx(5.10, abs=0.02)
    # S56 (D215): was rel 0.02; the sharper ridge is sampled on 720 steps here, and its crests carry the square.
    assert float(gp.contrast_at(radius, phi).mean()) == pytest.approx(mean_square, rel=0.05)


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


def test_both_models_run_the_gas_pattern_after_the_pattern(model):
    slots = [slot for slot, _ in model.stages]
    assert dict(model.stages)["gas_pattern"] == "gas_pattern"
    assert slots.index("gas_pattern") == slots.index("pattern") + 1


def test_a_flat_pattern_publishes_ones(model):
    assert one_mode(model, 2.73, bar=float("nan"), pitch=float("nan")).flat
    assert one_mode(model, 1.0).flat
    assert not one_mode(model, 2.73).flat
    # A ring that carries no mode: the ridge is 1 and no mask is formed (D215, gate ruling 6).
    gp = one_mode(model, 2.73)
    R = gp.R
    none = GasPattern(R, np.where(R[None, :] < 10.0, gp.unit, 0.0), gp.phases, 2.73, 0.0, 13.5, 5.2097, gp.width, gp.mask_width)
    field = none.contrast(R, DEFAULT.build().phi)
    assert np.all(field[R >= 10.0] == 1.0) and not np.all(field[R < 10.0] == 1.0)
    assert np.all(none.amplitude(R[R >= 10.0]) == 0.0) and np.all(np.isnan(none.mask_share(R[R >= 10.0])))
