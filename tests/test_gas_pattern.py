"""The gas's own arm pattern (S51, D210 Phases 1 and 1b): a von Mises ridge on the stellar arm's crest.

The gates are D210's predictions that Phase 1 can be judged on alone: the contrast averages to 1
round every ring, on the grid and per sector; the ratio of means over the source's mask is the
published gas_arm_contrast; the ridge sits on the stellar crest with no offset and is narrower
than the stellar arm; the field is seeded through the pattern's drawn numbers and reads no gas
column. Since Phase 1b (D210 as amended, debt #131) the ratio is the bar stage's derived class
mean with no draw.

At the defaults (both models; run on 2026-10-03): four arms, pitch 13.54 deg, bar 0.289 of
contrast over a 5.21 kpc half-length; the swing window 1.72-3.44 holds m = 2, so **C = 2.73**, the
grand designs' mean. At R0 = 8.122 kpc the mask is clamped at half the period, **a = 0.466, crest
3.068, trough 0.534**; at 12 kpc a = 0.387, crest 2.715, trough 0.613. The field runs 0.535-3.061
over the whole grid; the stellar contrast at 8 kpc runs 0.600-1.401. (Phase 1's drawn C was 10.02,
a = 0.823, crest 4.64, trough 0.180 at R0: the draw D210's amendment withdrew.)
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.stages.gas_pattern import (
    GAS_PATTERN,
    GasPattern,
    kappa_for_width,
    mask_means,
    von_mises,
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
    gp = GasPattern.from_fields(o.fields, constants(model))
    assert gp is not None and not gp.flat
    return gp


def row(o, R: float) -> int:
    return int(np.argmin(np.abs(o.grid.R - R)))


def wrap(x: np.ndarray) -> np.ndarray:
    return (np.asarray(x) + np.pi) % (2.0 * np.pi) - np.pi


# --- (a), (b): a redistribution, not a source ---------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g >= 0.0)
    assert np.allclose(g.mean(axis=1), 1.0, atol=1e-9)


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
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000  # midpoint, error ~1e-7 at this ridge
            dense.append(float(gp.contrast_at(np.full_like(phi, R), phi).mean()))
        assert np.allclose(means, dense, atol=1e-6), R
        assert means.max() > 1.0 > means.min()  # the ridge is resolved: not a flat ring


# --- (c): the ratio of means is the published one -----------------------------


def test_the_ratio_of_means_over_the_mask_is_the_published_contrast(model):
    """Recomputed from the field on the grid's own φ cells: the bar term and the arm weight taken
    back off with the stellar pattern's published numbers, the mask |θ| < θ_m with
    θ_m = min(m (W/2)/(R sin p), π/2). The grid's cells are m degrees wide in θ and its mask edge
    cuts them where it falls, so the check is to 2e-3 of C; on a dense φ grid it is 2e-5."""
    o = out(model)
    F = o.fields
    c = constants(model)
    C = float(F["gas_arm_contrast"])
    m, p, B, a_bar = (float(F[k]) for k in ("arm_multiplicity", "pitch_angle", "bar_contrast", "bar_half_length"))
    cot = 1.0 / math.tan(math.radians(p))
    g = np.asarray(F["gas_density_contrast"])
    gp = shape_of(model, o)

    def ratio(R: float, phi: np.ndarray, values: np.ndarray) -> float:
        w_bar = math.exp(-((R / a_bar) ** 4))
        ridge = 1.0 + (values - 1.0 - B * w_bar * np.cos(2.0 * (phi - math.log(a_bar) * cot))) / (1.0 - w_bar)
        theta = wrap(m * (phi - math.log(R) * cot))
        theta_m = min(m * 0.5 * c["GAS_ARM_MASK_WIDTH"] / (R * math.sin(math.radians(p))), 0.5 * math.pi)
        inside = np.abs(theta) < theta_m
        return float(ridge[inside].mean() / ridge[~inside].mean())

    for R in (6.0, R_SUN):
        i = row(o, R)
        Ri = float(o.grid.R[i])
        assert ratio(Ri, o.grid.phi, g[i]) == pytest.approx(C, rel=2e-3), R
        dense = np.linspace(0.0, 2.0 * np.pi, 72000, endpoint=False)
        assert ratio(Ri, dense, gp.contrast_at(np.full_like(dense, Ri), dense)) == pytest.approx(C, rel=2e-5), R


# --- (d): the ratio derived, the field seeded through the pattern ----------------


def test_the_field_moves_with_the_pattern_seed_and_not_the_world_seed(model):
    """The field is seeded through the pattern's drawn pitch, arm number and bar (graph labels it so,
    D55); the stage itself reads no seed and draws nothing (D210 as amended)."""
    a = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    b = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    c = run(model, {"pattern_seed": 8}, grid=COARSE).fields
    w = run(model, {"pattern_seed": 7, "world_seed": 12345}, grid=COARSE).fields
    assert np.array_equal(a["gas_density_contrast"], b["gas_density_contrast"])
    assert not np.array_equal(a["gas_density_contrast"], c["gas_density_contrast"])
    assert np.array_equal(a["gas_density_contrast"], w["gas_density_contrast"])
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
    """No offset (D210 ruling 3): outside the bar the two fields peak in the same φ cell."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    s = np.asarray(o.fields["pattern_density_contrast"])
    n = o.grid.phi.size
    for R in (8.0, 12.0):
        i = row(o, R)
        d = abs(int(g[i].argmax()) - int(s[i].argmax()))
        assert min(d, n - d) <= 1, R


def full_width_cells(values: np.ndarray) -> float:
    """Cells above the half level between the row's crest and trough."""
    half = 0.5 * (values.max() + values.min())
    return float((values > half).sum())


def test_the_ridge_is_narrower_than_the_stellar_arm(model):
    """At 12 kpc (bar weight e^-28): the gas's FWHM is 0.17 of the arm period to a cell, the
    stellar cosine's 0.5 — both in φ cells per arm."""
    o = out(model)
    m = float(o.fields["arm_multiplicity"])
    i = row(o, 12.0)
    cells_per_period = o.grid.phi.size / m
    gas = full_width_cells(np.asarray(o.fields["gas_density_contrast"])[i]) / m
    star = full_width_cells(np.asarray(o.fields["pattern_density_contrast"])[i]) / m
    assert gas == pytest.approx(0.17 * cells_per_period, abs=1.0)
    assert star == pytest.approx(0.5 * cells_per_period, abs=1.0)
    assert gas < 0.5 * star


# --- (g): the worked numbers ------------------------------------------------------


def test_the_worked_numbers_at_the_defaults(model):
    """κ, v(0) and v(π) for W = 0.17, and D210's worked table (four arms, pitch 13.5 deg, the clamp).

    κ = 4.9774. **v(0) = 5.435, not D210's 4.93**: D210's own crests need v(0) ≈ 5.4 (1 + 0.462
    × 4.435 = 3.05), so 4.93 is a slip in the entry. Recomputed here with the stage's quadrature,
    against D210's: C = 2.73 → a 0.466 (0.462), crest 3.068 (3.04), trough 0.534 (0.54); C = 1.90
    → 0.312 (0.308), 2.383 (2.36), 0.688 (0.69); C = 5.79 → 0.709 (0.706), 4.144 (4.12), 0.291
    (0.29); C = 2.73 at 12 kpc → crest 2.716 (2.69), trough 0.613 (0.62). All within 1.3 %.
    """
    c = constants(model)
    kappa = kappa_for_width(c["GAS_ARM_WIDTH"])
    assert kappa == pytest.approx(4.977, abs=1e-3)
    v0 = float(von_mises(np.array(0.0), kappa))
    vpi = float(von_mises(np.array(math.pi), kappa))
    assert v0 == pytest.approx(5.435, abs=1e-3)
    assert vpi == pytest.approx(2.58e-4, rel=1e-2)
    # The FWHM relation is exact: v(±πW) = v(0)/2.
    assert float(von_mises(np.array(math.pi * c["GAS_ARM_WIDTH"]), kappa)) == pytest.approx(0.5 * v0, rel=1e-12)

    def worked(C: float, R: float) -> tuple[float, float, float]:
        gp = GasPattern(C, 0.0, 4.0, 13.5, 5.2097, c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])
        a = float(gp.amplitude(np.array([R]))[0])
        return a, 1.0 + a * (v0 - 1.0), 1.0 + a * (vpi - 1.0)

    for C, R, want in ((2.73, R_SUN, (0.462, 3.04, 0.54)), (1.90, R_SUN, (0.308, 2.36, 0.69)),
                       (5.79, R_SUN, (0.706, 4.12, 0.29))):
        assert worked(C, R) == pytest.approx(want, rel=0.015), C
    a12, crest12, trough12 = worked(2.73, 12.0)
    assert (crest12, trough12) == pytest.approx((2.69, 0.62), rel=0.015)

    # The defaults' own ratio, at R0 and 12 kpc (the module docstring's numbers; D210's corrected table).
    o = out(model)
    gp = shape_of(model, o)
    assert float(o.fields["gas_arm_contrast"]) == pytest.approx(2.73, abs=1e-12)
    for R, (a_want, crest_want, trough_want) in ((R_SUN, (0.466, 3.068, 0.534)), (12.0, (0.387, 2.715, 0.613))):
        a = float(gp.amplitude(np.array([R]))[0])
        assert (a, 1.0 + a * (v0 - 1.0), 1.0 + a * (vpi - 1.0)) == pytest.approx(
            (a_want, crest_want, trough_want), abs=1e-3), R
    g = np.asarray(o.fields["gas_density_contrast"])
    assert (float(g.min()), float(g.max())) == pytest.approx((0.535, 3.061), abs=1e-3)


def test_the_mask_means_are_the_integral(model):
    """The fixed quadrature against a dense integral, at the clamp and below it."""
    kappa = kappa_for_width(constants(model)["GAS_ARM_WIDTH"])
    t = (np.arange(400_000) + 0.5) * (2.0 * np.pi / 400_000) - np.pi
    v = von_mises(t, kappa)
    for theta_m in (0.5 * np.pi, 1.068, 0.5):
        v_in, v_out = mask_means(np.array([theta_m]), kappa)
        inside = np.abs(t) < theta_m
        # Absolute: a reads (v_in - 1) - C (v_out - 1), and v_out is 0.005 at the clamp.
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
    # mean square (1.42 at the defaults), well above 1 — to sampling noise, about 0.5 %.
    ring = np.linspace(0.0, 2.0 * np.pi, 36000, endpoint=False)
    mean_square = float((gp.contrast_at(np.full_like(ring, 12.0), ring) ** 2).mean())
    assert mean_square > 1.2
    assert float(gp.contrast_at(radius, phi).mean()) == pytest.approx(mean_square, rel=0.02)


# --- (i), (j): what the stage reads, where it sits ----------------------------------


def test_the_stage_reads_no_gas_and_sits_at_checkpoint_three():
    assert GAS_PATTERN.checkpoint == 3 == PATTERN.checkpoint
    # No gas column: the one gas name it reads is the bar stage's derived ratio, a scalar.
    assert [n for n in GAS_PATTERN.requires if "gas" in n] == ["gas_arm_contrast"]
    assert "arm_contrast" not in GAS_PATTERN.requires
    assert GAS_PATTERN.reads_seeds == ()
    assert {d.name for d in GAS_PATTERN.publishes} == {"gas_density_contrast"}


def test_both_models_run_the_gas_pattern_after_the_pattern(model):
    slots = [slot for slot, _ in model.stages]
    assert dict(model.stages)["gas_pattern"] == "gas_pattern"
    assert slots.index("gas_pattern") == slots.index("pattern") + 1


def test_a_flat_pattern_publishes_ones():
    gp = GasPattern(2.73, float("nan"), 4.0, float("nan"), 5.2, 0.17, 1.5)
    assert gp.flat
    assert GasPattern(1.0, 0.0, 4.0, 13.5, 5.2, 0.17, 1.5).flat
    assert not GasPattern(2.73, 0.0, 4.0, 13.5, 5.2, 0.17, 1.5).flat
