"""The gas's own arm pattern: since S57 the gas's steady response to the stellar arms (BUILD_III Phase P2; D216).

From S51 to S56 this file held a ridge to its form: a von Mises of a measured width, its amplitude solved from a
measured ratio of means, since S56 laid round each ring by rank. Gate G2 of S57 retired the ridge for a law -
``ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m)`` on every ring, solved by ``gas_response`` (the instrument;
``tests/test_gas_response.py`` certifies it) - and this file holds the model to that law and to nothing of the
ridge. What is tested, in the gate's order:

- **the gate**, on every ring of both templates and of the 240 seeded galaxies the suite draws: the discrete
  residual as gate G3 words it (under 1e-10 or under the cell's rounding floor, the returned profile re-logged
  too), the ring's mean on the solver's cells with no division, positivity and the bound w_bar (1 − B), the
  published field's ring mean, Newton's counts, finiteness, the sector means, the saturation's bound;
- **the law re-derived by hand** on three rings from the published fields, with a dense Newton and a spectral
  derivative written here, and the published cell means with the bar's composition; and again on the suite's most
  saturated seed (gate G3 item 3: the forcing's amplitude carries the saturation);
- **the published field is the law's mean over each grid cell** (G3 item 4): ring means 1 to 1e-13 on any φ grid
  with nothing divided, and its error against the exact solution's cell means with the h² law;
- **the two interpolation errors** of the point function, in χ and in R, pinned as measured (G3 item 5);
- **the predictions** of D216, read before they are judged (B4), with the as-built numbers;
- **the disclosed check** (not an acceptance row; invariant I3 stands): the ratio of means in the source's mask
  against PHANGS's 2.73 within 1.37-5.79, and the crest's width against 0.17 - layer on, both templates.

**Read on 2026-10-04, the Milky Way template at its default seeds** (165 rings carry a mode; `ngc_4414`: 133):
Newton 8 steps at most and one halving (9 and none); the residual 5.3e-12 (9.0e-12), the rounding floor 1.3e-11
(1.9e-11) - the absolute tolerance governs; the ring mean on the solver's cells off 1 by 8.8e-14 (9.6e-14); the
published field's ring mean off 1 by 7.1e-14 (9.7e-14) on the default grid and 1e-14 on a 36-, 108- or 500-cell
one, with nothing divided; s between 4.5e-11 and 5.70 (1.8e-17 and 4.73), both extremes deep inside the bar where
the arm's weight is under 1 %; the published field between 0.0199 and 3.092 (0.0143 and 2.688), its margin over
w_bar (1 − B) 2.0e-5 (7.7e-6). At R₀ the crest is 2.74 and the trough 0.025 (S56's ridge: 3.06 and 0.534): the
gas between the arms is nearly emptied where the modes' forcing sums past 1, as the gate predicted.

**What the first build found, and what gate G3 ruled** (D216). (i) Tightly wound galaxies raised: at a drawn
pitch under about 2.7 degrees ε is of order 1 and the forcing's sum 60-80, the residual's rounding floor passes
the absolute 1e-10, and two of the 240 seeded galaxies (``ngc_4414`` at pattern seed 33) - 20 of 600 over a sweep
of 300 pattern seeds a template - were solved and still raised. Since G3 a cell is converged under 1e-10 **or
under its rounding floor**; all 240 and all 600 converge, and the regime is published as the law gives it.
**One of the 238 that converged before moved its bits** (``ngc_4414`` at pattern seed 1, texture seed 1: one ring
at 0.49 kpc stops at 8 Newton steps where the absolute tolerance took 10; the profile moves by 1.8e-15 of itself
and the published field not at all) and three of the sweep's 580: reported to the gate, which asked for none.
(ii) The interpolation in χ reads 3.5e-4 outside the bar's reach and 1.2e-3 inside it (3.0e-4 of the point
field), not the 2.0e-4 of the instrument's two hard rings: 1440 cells stand, pinned per quantity. (iii) The
offset is zero for a lone mode; with several modes the two crests are within one solver cell on the default
galaxy's mid disc and up to five cells on ``ngc_4414``'s. (iv) The published field is cell means, not centre
samples: ring totals hold on every grid.
"""

from __future__ import annotations

import ast
import functools
import math
from pathlib import Path

import numpy as np
import pytest

import gas_check
from galaxy import templates
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt
from galaxy.stages.gas_pattern import GAS_PATTERN, GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS, GasPattern
from galaxy.stages.pattern import BAR, PATTERN

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
TEMPLATES = ("milky_way", "ngc_4414")
R_SUN = 8.122
G_HAND = 4.30091727e-6  # kpc (km/s)^2 / Msun, written here; the model's constant is held to it
SOUND_SPEED_HAND = 6.0  # km/s, written here; the model's GAS_DISPERSION is held to it
# The disclosed check's two numbers are no constants of the model since gate G3 (item 7): they live in
# tests/gas_check.py with their sources. PHANGS's median mask width, and the measured gas arm's width over its period.
MASK_WIDTH = gas_check.GAS_ARM_MASK_WIDTH
WIDTH_TARGET = gas_check.GAS_ARM_WIDTH
RATIO_TARGET, RATIO_LOW, RATIO_HIGH = 2.73, 1.37, 5.79  # PHANGS's grand designs: the mean and its 16th-84th percentiles
PATTERN_FIELDS = ("gas_density_contrast", "pattern_density_contrast", "gas_arm_contrast", "arm_pattern_speed",
                  "circular_velocity", "arm_saturation", *GAS_PATTERN_READS)
ROUNDING = 2.0**-53  # u: half a unit in the last place of 1
_RUNS: dict[object, object] = {}


def out(model):
    """The default run, once per model per session (the whole pipeline is a few seconds)."""
    if model.name not in _RUNS:
        _RUNS[model.name] = run(model)
    return _RUNS[model.name]


def template_run(prod, template: str):
    """A template's pattern fields alone on the production grid (rule D4), once per session."""
    key = ("template", template)
    if key not in _RUNS:
        _RUNS[key] = run(prod[0].get(DEFAULT_MODEL), templates.overrides(templates.TEMPLATES[template]), only=PATTERN_FIELDS)
    return _RUNS[key]


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def shape_of(model, o) -> GasPattern:
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert gp is not None and not gp.flat
    return gp


def row(o, R: float) -> int:
    return int(np.argmin(np.abs(o.grid.R - R)))


def synthetic(unit: np.ndarray, phases=(0.0,) * 5, arm: float = 0.4, bar: float = 0.0, pitch: float = 13.5,
              bar_length: float = 5.2097, R: np.ndarray | None = None) -> GasPattern:
    """A pattern on a made-up disc: a flat curve of 220 km/s (κ = √2 v/R) and an exponential disc of 50 M☉/pc² at
    8 kpc with a 2.6 kpc scale length. Built directly: it does not pass through the switch."""
    R = DEFAULT.build().R if R is None else R
    kappa = math.sqrt(2.0) * 220.0 / R
    sigma = 50.0 * np.exp(-(R - 8.0) / 2.6)
    return GasPattern(R, unit, phases, arm, bar, pitch, bar_length, kappa, sigma, G_HAND, SOUND_SPEED_HAND)


def one_mode(m: int = 4, strength: float = 1.0, **more) -> GasPattern:
    R = DEFAULT.build().R
    unit = np.zeros((len(pt.ARM_MODES), R.size))
    unit[pt.ARM_MODES.index(m)] = strength
    return synthetic(unit, **more)


def hand_newton(forcing: np.ndarray, eps: float) -> tuple[np.ndarray, int]:
    """The discrete equation ε² (φ_{k+1} − 2φ_k + φ_{k−1})/h² = e^{φ_k} − 1 − g_k on the ring's cells, solved here by
    a dense Newton in φ = ln s from s = 1 - a full matrix and numpy's general solver, the step halved while the
    convex functional J does not fall. Nothing of ``gas_response`` or ``gas_pattern``."""
    n = forcing.size
    h = 2.0 * math.pi / n
    stiffness = (eps / h) ** 2
    laplacian = 2.0 * np.eye(n) - np.roll(np.eye(n), 1, axis=0) - np.roll(np.eye(n), -1, axis=0)

    def functional(phi: np.ndarray) -> float:
        d = np.roll(phi, -1) - phi
        return float((0.5 * stiffness * d * d + np.exp(phi) - (1.0 + forcing) * phi).sum())

    phi = np.zeros(n)
    for step in range(60):
        s = np.exp(phi)
        residual = s - 1.0 - forcing + stiffness * (laplacian @ phi)
        if float(np.abs(residual).max()) < 1e-11:
            return s, step
        delta = np.linalg.solve(np.diag(s) + stiffness * laplacian, -residual)
        t, before = 1.0, functional(phi)
        while functional(phi + t * delta) > before and t > 1e-6:
            t *= 0.5
        phi = phi + t * delta
    raise AssertionError("the hand Newton did not converge in 60 steps")


def hand_cell_means(profile: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """The mean, over each interval [lo_j, hi_j] of χ, of the periodic piecewise-linear function through ``profile``
    on the ring's cell centres χ_k = −π + (k + ½) 2π/n: the trapezoid rule on the function's own breakpoints, which
    is its exact integral. This file's arithmetic - no function of ``gas_response`` or ``gas_pattern``."""
    n = profile.size
    h = 2.0 * math.pi / n
    centres = -math.pi + (np.arange(-n, 2 * n) + 0.5) * h  # three turns of the ring
    values = np.tile(profile, 3)
    means = []
    for a, b in zip(lo, hi):
        turn = math.floor((a + math.pi) / (2.0 * math.pi))
        a0, b0 = a - 2.0 * math.pi * turn, b - 2.0 * math.pi * turn
        nodes = np.concatenate([[a0], centres[(centres > a0) & (centres < b0)], [b0]])
        height = np.interp(nodes, centres, values)
        means.append(float((0.5 * (height[1:] + height[:-1]) * np.diff(nodes)).sum()) / (b0 - a0))
    return np.array(means)


# --- a redistribution, not a source ----------------------------------------------------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    """Positive, finite, and mean 1 round every ring of the published field - with nothing divided: each value is
    the law's mean over its cell, and a ring's cells tile the ring."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g > 0.0) and np.all(np.isfinite(g))
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 1e-13
    assert not np.all(g == 1.0)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_published_field_is_the_law_s_mean_over_each_cell_and_is_never_divided(prod, template):
    """Gate G3 item 4 (it rewords D216 items 9 and 11 i): "the published (R, φ) field is the law's mean over each
    grid cell - the interpolant integrated exactly - so its ring mean is 1 to rounding on every grid with no
    division (pin 1e-13) ... ``contrast_at``, ``response_at`` and the censuses keep the point function".

    The published field is ``GasPattern.cell_means`` on the grid's own φ edges, bit for bit, and each of its rows
    is ``sector_means`` at that ring's radius, bit for bit: no step stands between the law and the field, a
    division least of all. **Measured: the ring mean is off 1 by 7.1e-14 (the Milky Way template) and 9.7e-14
    (``ngc_4414``) on the default grid - the solver's own ring mean, which it holds to 1e-13 - and by 1e-14 and
    2e-15 on grids of 36, 108, 500 and 720 φ cells.** (The first build published the point function at the cells'
    centres: 7e-14 on 360 cells, which divide the solver's 1440, but 2e-6 on 108 and 1.3e-3 on 36 - the response's
    harmonics aliased - and three small-grid tests had been re-pinned to that. They are back at 1e-12.)
    A cell's mean is not its centre's value: the two differ by up to 1.7e-3 of the ring's mean (on the flank of a
    crest, where the profile curves); and it is never under w_bar (1 − B)."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    assert g.tobytes() == gp.cell_means(R, edges).tobytes()
    for i in (3, 60, 106, 133, 160, 399):
        assert g[i].tobytes() == gp.sector_means(float(R[i]), edges).tobytes(), i
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 1e-13
    taper = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0]
    assert float((g - (taper * (1.0 - gp.bar))[:, None]).min()) >= 0.0 and g.min() > 0.0
    # Against the point function at the cells' centres: another number, by the profile's curvature across a cell.
    point = gp.contrast(R, phi)
    assert float(np.abs(g - point).max()) == pytest.approx({"milky_way": 1.718e-3, "ngc_4414": 1.716e-3}[template], rel=0.02)
    assert float(np.abs(point.sum(axis=1) / point.shape[1] - 1.0).max()) < 5e-13  # 360 divides 1440: rounding here
    # The module holds no tolerance to renormalise by, and its source does not divide a field by a mean.
    assert not hasattr(gm, "RING_MEAN_TOLERANCE")
    assert ".mean(" not in Path(gm.__file__).read_text(encoding="utf-8")
    # Any φ grid: the ring keeps its gas to rounding, and the centre samples do not.
    given = templates.overrides(templates.TEMPLATES[template])
    for n_phi, sampled in ((36, {"milky_way": 1.257e-3, "ngc_4414": 1.056e-3}[template]), (108, None), (500, None)):
        coarse = run(model, given, GridSpec(n_R=48, n_t=64, n_z=8, n_phi=n_phi), only=GAS_PATTERN_READS + ("gas_density_contrast",))
        small = np.asarray(coarse.fields["gas_density_contrast"])
        assert small.shape[1] == n_phi and np.all(small > 0.0)
        assert float(np.abs(small.sum(axis=1) / n_phi - 1.0).max()) < 1e-13, n_phi  # measured 1.2e-14 and 2e-15
        if sampled is not None:  # what the centre samples read on this grid: the first build's field
            centre = compose.gas_pattern(coarse.fields, coarse.grid.R, constants(model)).contrast(coarse.grid.R, coarse.grid.phi)
            assert float(np.abs(centre.sum(axis=1) / n_phi - 1.0).max()) == pytest.approx(sampled, rel=0.02)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_cell_averaged_field_against_the_exact_solution_s_cell_means(prod, template):
    """Gate G3 item 4: "re-measure and pin the averaged field's error against the exact solution's cell means".
    The reference is the same equation solved on finer cells - 2880 and 5760 - and averaged over the same grid
    cells. **The h² law**: the error of a cell mean at n solver cells is c/n² (the solver's second-order error and
    the linear interpolant's, both; a cell's mean feels them averaged over the grid cell, so it is smaller than the
    point function's error at a midpoint), so against the 5760-cell reference the 1440-cell means are off by
    c (1 − 1/16)/1440² and the 2880-cell ones by c (1/4 − 1/16)/1440²: **their ratio is 5, and it reads 5.00**.
    The 1440-cell error against the exact solution is then 16/15 of the first.

    **As measured (the Milky Way template; ``ngc_4414``): of the published field 2.1e-4 (2.1e-4) at worst, at
    5.5 kpc (3.6 kpc); of s itself 9.2e-4 (9.1e-4), deep inside the bar where the arm's weight is under 1 %, and
    2.5e-4 (6.1e-5) beyond 6 kpc.** The cell count is the ruling's (G3 item 5) and is not touched."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R, edges = o.grid.R, o.grid["phi"].edges
    gp = shape_of(model, o)
    carries = gp.carries
    f, eps = gp.forcing_amplitudes()[carries], gp.epsilon()[carries]
    taper, phase, _ = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    lo, hi = edges[None, :-1] - phase[carries, None], edges[None, 1:] - phase[carries, None]
    means = {gr.CELLS: gr.sector_mean(gp.profiles[carries], lo, hi)}
    for cells in (2880, 5760):
        fine, _ = gr.solve(gr.forcing(pt.ARM_MODES, f, np.asarray(gp.phases), cells), eps)
        means[cells] = gr.sector_mean(fine, lo, hi)
    weight = (1.0 - taper[carries])[:, None]
    at_1440, at_2880 = np.abs(means[1440] - means[5760]), np.abs(means[2880] - means[5760])
    got = (float(at_1440.max()), float((at_1440 * weight).max()), float(at_1440[R[carries] > 6.0].max()))
    want = {"milky_way": (9.207e-4, 2.105e-4, 2.458e-4), "ngc_4414": (9.144e-4, 2.101e-4, 6.122e-5)}[template]
    assert got == pytest.approx(want, rel=0.01), got
    assert float(at_1440.max() / at_2880.max()) == pytest.approx(5.0, abs=0.03)
    assert float((at_1440 * weight).max() / (at_2880 * weight).max()) == pytest.approx(5.0, abs=0.03)
    # The published field's own arm part is those 1440-cell means: its error is the weighted one above.
    published = np.asarray(o.fields["gas_density_contrast"])[carries]
    bar = (np.sin(2.0 * (edges[1:] - pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[2])) - np.sin(2.0 * (edges[:-1] - pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[2]))) / (2.0 * np.diff(edges))
    exact = weight * means[5760] + taper[carries, None] * (1.0 + gp.bar * bar[None, :])
    assert float(np.abs(published - exact).max()) == pytest.approx(want[1], rel=0.01)


def test_the_sector_means_are_the_exact_means_of_the_point_function(model):
    """Twelve sectors at five radii: their mean is the ring's, 1, to rounding; and each sector's mean is the
    dense average of ``contrast_at`` over it to the dense average's own error (a midpoint rule on a piecewise
    linear function: 4000 points a sector) - the series of S56 was good to 1e-3 on a ranked ridge; this is the
    interpolant's own integral. Also between two grid rings, where a point blends two profiles."""
    o = out(model)
    gp = shape_of(model, o)
    R = o.grid.R
    edges = np.linspace(0.0, 2.0 * np.pi, 13)
    worst = 0.0
    for radius in (1.0, 3.0, 6.0, 10.0, float(0.3 * R[120] + 0.7 * R[121])):
        means = gp.sector_means(radius, edges)
        assert float(means.mean()) == pytest.approx(1.0, abs=1e-12)
        dense = []
        for a, b in zip(edges[:-1], edges[1:]):
            phi = a + (np.arange(4000) + 0.5) * (b - a) / 4000
            dense.append(float(gp.contrast_at(np.full_like(phi, radius), phi).mean()))
        worst = max(worst, float(np.abs(means - np.array(dense)).max()))
        assert means.max() > 1.0 > means.min()  # the arms are resolved: not a flat ring
        # and the many-radii form the stage publishes with is this one, at any radius
        assert gp.cell_means(np.array([radius]), edges)[0].tobytes() == means.tobytes()
    assert worst < 2e-7  # measured 4e-8: the midpoint rule's, not the means'
    # Thirty-two sectors, unequal ones, and a ring past the last mode and the bar: every sector exactly 1.
    uneven = np.concatenate([[0.0], np.sort(np.random.default_rng(5).uniform(0.0, 2.0 * np.pi, 31)), [2.0 * np.pi]])
    means = gp.sector_means(8.0, uneven)
    assert float((means * np.diff(uneven)).sum() / (2.0 * np.pi)) == pytest.approx(1.0, abs=1e-12)
    assert np.all(gp.sector_means(20.0, edges) == 1.0) and np.all(gp.cell_means(np.array([20.0, 25.0]), edges) == 1.0)


# --- the gate ----------------------------------------------------------------------------------------------------


def gate(gp: GasPattern, edges: np.ndarray) -> dict[str, float]:
    """The gate's numbers for one pattern (D216, "the gate (every ring, every seed, both templates)"), with its
    residual item as gate G3 words it (item 2): "on every cell |r_k| ≤ max(1e-10, F_k), F_k recorded per ring as
    its rounding floor; |Σr_k|/cells < 1e-13; the returned s re-logged satisfies the same with F_k + 4u·ε²/h²".

    The solver's own residual and floor are its report's (per ring: the largest of each; the cell-by-cell rule is
    the solver's convergence itself). The re-logged statement is asserted here on every cell of every ring, from
    the profile the pattern holds, with ``gas_response.residual`` and ``gas_response.rounding_floor``. Everything
    else is recomputed from the profiles."""
    R = gp.R
    s, carries, d = gp.profiles, gp.carries, gp.diagnostics
    f, eps = gp.forcing_amplitudes(), gp.epsilon()
    forcing = gr.forcing(pt.ARM_MODES, f[carries], np.asarray(gp.phases))
    relogged = np.abs(gr.residual(s[carries], forcing, eps[carries]))
    floor = gr.rounding_floor(s[carries], eps[carries])
    inv_h2 = (gr.CELLS / (2.0 * math.pi)) ** 2
    assert np.all(relogged <= np.maximum(1e-10, floor + 4.0 * ROUNDING * (eps[carries] ** 2)[:, None] * inv_h2))
    assert np.all(d.residual <= np.maximum(1e-10, d.floor))
    # The floor of ln s as the solver held it and of the logarithm taken again: the same spacing of doubles, but
    # where a cell's ln s sits on a power of two (a factor 2 there, on that cell).
    assert np.all((floor.max(axis=1) <= 2.0 * d.floor) & (d.floor <= 2.0 * floor.max(axis=1)))
    assert np.all(s[~carries] == 1.0)  # a ring with no mode has s = 1
    taper, _, _ = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    field = gp.cell_means(R, edges)  # what the stage publishes
    assert np.all(np.isfinite(s)) and np.all(np.isfinite(field))
    return {
        "residual": float(d.worst_residual), "relogged": float(relogged.max()), "floor": float(d.floor.max()),
        "over": float((d.residual / np.maximum(1e-10, d.floor)).max()),  # the residual over what it is held under
        "on_floor": float((d.floor > 1e-10).sum()),  # rings whose floor, not the tolerance, is the bound
        "sum": float(np.abs(d.residual_sum).max() / gr.CELLS),
        "mean": float(np.abs(s.sum(axis=1) / s.shape[1] - 1.0).max()),
        "min_s": float(s.min()), "max_s": float(s.max()),
        "margin": float((field - (taper * (1.0 - gp.bar))[:, None]).min()),  # min g − w_bar (1 − B), ring by ring
        "ring_mean": float(np.abs(field.sum(axis=1) / field.shape[1] - 1.0).max()),
        "steps": float(d.worst_steps), "halvings": float(d.worst_halvings),
        "max_g": float(field.max()), "min_g": float(field.min()),
    }


@pytest.mark.parametrize("template", TEMPLATES)
def test_gate_every_ring_of_both_templates(prod, template):
    """The gate at each template's own seeds, on every ring, with the numbers as read (the module docstring)."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    gp = shape_of(model, o)
    got = gate(gp, o.grid["phi"].edges)
    want = {
        "milky_way": dict(rings=165, steps=8, halvings=1, min_s=4.50e-11, max_s=5.6975, min_g=0.019943, max_g=3.092221, floor=1.279e-11),
        "ngc_4414": dict(rings=133, steps=9, halvings=0, min_s=1.81e-17, max_s=4.7322, min_g=0.014257, max_g=2.688408, floor=1.933e-11),
    }[template]
    assert int(gp.carries.sum()) == want["rings"]
    # The residual: at these pitches (13.5 and 14.3 degrees) every ring's floor is far under 1e-10 and the absolute
    # tolerance governs, as it did before G3. Measured 5.3e-12 and 9.0e-12, re-logged the same.
    assert got["floor"] == pytest.approx(want["floor"], rel=0.01) and got["on_floor"] == 0
    assert got["residual"] < gr.RESIDUAL_TOLERANCE == 1e-10 and got["relogged"] < 1e-10
    assert got["sum"] < gr.SUM_TOLERANCE == 1e-13
    assert got["mean"] < 1e-12                                       # measured 8.8e-14 and 9.6e-14, nothing divided
    assert got["min_s"] > 0.0 and got["margin"] >= 0.0               # nothing clipped: the law's own positivity
    assert got["ring_mean"] < 1e-13                                  # measured 7.1e-14 and 9.7e-14: the cell means
    assert (got["steps"], got["halvings"]) == (want["steps"], want["halvings"])
    assert got["steps"] <= gr.MAX_NEWTON_STEPS == 120 and got["halvings"] <= gr.MAX_HALVINGS == 30
    assert got["min_s"] == pytest.approx(want["min_s"], rel=0.02) and got["max_s"] == pytest.approx(want["max_s"], abs=2e-4)
    # S57 (D216 G3): were (0.019924, 3.09294) and (0.014249, 2.68897), the point function at the cells' centres.
    assert (got["min_g"], got["max_g"]) == pytest.approx((want["min_g"], want["max_g"]), abs=2e-5)
    # The bound of D216 item 12, [w_bar (1 − B), max s]: the margin under it is small where the arm's weight is.
    # S57 (D216 G3): was under 2e-5 (9.2e-6 and 1.3e-6 on the centre samples; 2.0e-5 and 7.7e-6 on the cell means).
    assert 0.0 < got["margin"] < 3e-5 and got["max_g"] <= got["max_s"]
    # At the templates' own seeds the field stays under the declared ramp's top. That top is the viewer's display
    # range, not a cap on the field: nothing clips to it, and seeds that draw a strong arm or a low pitch pass it
    # (6.8 at most over the suite's seeds; the test below).
    assert gm.GAS_DENSITY_CONTRAST.ramp.hi == 4.0 and not np.any(np.asarray(o.fields["gas_density_contrast"]) > 4.0)


def test_gate_every_ring_on_every_seed_the_suite_draws(prod):
    """The gate on the suite's seeds - sixty pattern seeds by two texture seeds for each template's inputs, the 240
    galaxies the stellar positivity test draws (``tests/test_modes.py``): on every ring the residual item as gate
    G3 words it (``gate``, above); the ring's mean 1 to 1e-12 on the solver's cells with no division; min s > 0 and
    min g ≥ w_bar (1 − B) with nothing clipped; the published field's ring mean within its pinned 2e-13; Newton's
    counts under the solver's maxima; finite everywhere; the sector means averaging to 1; and the stellar
    amplitudes the forcing is made of inside the saturation's bound, Σ_m A_m ≤ 1 − B·taper, on every ring (G3
    item 3).

    **All 240 meet it.** The first build's two failures - ``ngc_4414`` at pattern seed 33, either texture seed, a
    drawn pitch of 1.78 degrees: ε = a/(κR sin p) about 1 on the inner rings, the forcing's sum 60-80, the
    residual stalled at 1.0-1.3e-10 against an absolute 1e-10 for 120 steps - **now converge in 10 steps at most**:
    their worst ring's rounding floor is 3.38e-10 and its residual 1.31e-10 and 1.24e-10, 0.48 and 0.49 of what
    it is held under; 50 and 48 of their 133 rings have a floor above 1e-10. Seventeen of the 240 galaxies have
    such a ring (249 rings in all), every one at a drawn pitch under 7.7 degrees.

    **One galaxy that converged before G3 is not the bits it was** (the forbidden "any change to a converged
    solution's bits" could not be kept with the criterion as ruled, and is reported): ``ngc_4414`` at pattern seed
    1, texture seed 1 (pitch 2.06 degrees). Its ring at 0.49 kpc (arm weight 3.7e-4) took 10 Newton steps under
    the absolute tolerance - the last two wandering on the rounding floor until one landed at 9.5e-11 - and takes
    8 now, stopping at 1.19e-10 under a floor of 2.5e-10. The two profiles differ by 1.8e-15 of themselves; the
    published field, the point function and the sector means of that galaxy are bit for bit what they were.
    (Outside this test, a sweep of 300 pattern seeds a template at the template's own texture seed: no galaxy
    raises where 5 and 15 did; the worst floor 5.8e-10 and 9.7e-10, the worst residual over its bound 0.49; s from
    3.9e-41 to 14.0 and from 2.7e-79 to 14.8; of the 580 that did not raise before, three more moved, as this one.)"""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    edges = np.linspace(0.0, 2.0 * np.pi, 33)
    worst: dict[str, float] = {}
    held: dict[tuple[str, int, int], dict[str, float]] = {}
    on_floor: dict[tuple[str, int, int], float] = {}
    saturated_most = 0.0
    for template in TEMPLATES:
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = {**templates.overrides(templates.TEMPLATES[template]), "pattern_seed": pattern_seed, "texture_seed": texture_seed}
                o = run(model, given, only=GAS_PATTERN_READS)
                gp = compose.gas_pattern(o.fields, o.grid.R, c)
                assert gp is not None and not gp.flat
                label = (template, pattern_seed, texture_seed)
                got = gate(gp, o.grid["phi"].edges)  # raises nowhere: every ring of every galaxy converges
                held[label] = got
                assert got["over"] <= 1.0 and got["sum"] < 1e-13, label
                assert got["mean"] < 1e-12, label
                assert got["min_s"] > 0.0 and got["margin"] >= 0.0, label
                assert got["ring_mean"] < 2e-13, label
                assert got["steps"] <= gr.MAX_NEWTON_STEPS and got["halvings"] <= gr.MAX_HALVINGS, label
                if got["on_floor"]:
                    on_floor[label] = float(o.fields["pitch_angle"])
                for radius in (3.0, 8.0):
                    assert float(gp.sector_means(radius, edges).mean()) == pytest.approx(1.0, abs=1e-12), label
                # The stellar amplitudes the forcing is made of, as published: inside the saturation's bound.
                taper = pt.bar_terms(o.grid.R, float(o.fields["pitch_angle"]), float(o.fields["bar_half_length"]))[0]
                total = np.sum([np.asarray(o.fields[n], dtype=float) for n in pt.AMPLITUDE_FIELDS], axis=0)
                excess = float((total - (1.0 - float(o.fields["bar_contrast"]) * taper)).max())
                assert excess <= 1e-12, label
                saturated_most = max(saturated_most, excess)
                for key, value in got.items():
                    worst[key] = min(worst.get(key, value), value) if key in ("min_s", "margin", "min_g") else max(worst.get(key, value), value)
    assert len(held) == 240
    # The two that raised at the first build, as they converge now (their floors and residuals, as read).
    for label, residual in ((("ngc_4414", 33, 0), 1.305e-10), (("ngc_4414", 33, 1), 1.238e-10)):
        got = held[label]
        assert got["floor"] == pytest.approx(3.384e-10, rel=0.01) and got["residual"] == pytest.approx(residual, rel=0.01), label
        assert got["steps"] == 10 and got["residual"] > 1e-10 and 0.3 < got["over"] < 0.5, label
        assert on_floor[label] == pytest.approx(1.780, abs=2e-3) and got["on_floor"] in (48, 50), label
    # The one whose bits moved with the criterion (the docstring): 9 steps at most over its rings now, its worst
    # ring's residual 1.19e-10 under a floor of 2.5e-10 (the absolute tolerance had left it at 9.7e-11).
    moved = held[("ngc_4414", 1, 1)]
    assert moved["residual"] == pytest.approx(1.186e-10, rel=0.01) and moved["floor"] == pytest.approx(2.516e-10, rel=0.01) and moved["steps"] == 9
    # The worst seen over the 240, recorded: Newton's counts (the maxima are 120 and 30); the largest floor and the
    # residual nearest its bound - under half of it everywhere, since the bound carries a factor 2 for the
    # residual's own arithmetic; the ring mean 1.0e-13 on the solver's cells; the published ring mean; s from
    # 2.4e-44 to 14.39; the published field from 0.0017 to 6.8; its margin over w_bar (1 − B).
    # S57 (D216 G3): was `5e-11 < worst residual < 1e-10` over the 238 - a pin that sat on the rounding floor it
    # is now judged against. The residual over its bound is the robust reading.
    assert (worst["steps"], worst["halvings"]) == (11, 2)
    assert worst["floor"] == pytest.approx(3.384e-10, rel=0.01) and 0.45 < worst["over"] < 0.5
    assert worst["residual"] == pytest.approx(1.305e-10, rel=0.01) and worst["relogged"] < 5e-10
    assert worst["mean"] < 2e-13 and worst["ring_mean"] < 2e-13 and worst["sum"] < 1e-13
    assert 0.0 < worst["min_s"] < 1e-40 and worst["max_s"] == pytest.approx(14.39, abs=0.02)
    assert worst["margin"] >= 0.0 and worst["min_g"] > 1e-3 and worst["max_g"] == pytest.approx(6.78, abs=0.03)
    # Which galaxies have a ring whose floor is the bound: seventeen, at the lowest drawn pitches.
    assert len(on_floor) == 17 and max(on_floor.values()) < 7.7 and worst["on_floor"] == 50
    assert {k[:2] for k in on_floor} == {("milky_way", 1), ("milky_way", 33), ("milky_way", 40), ("ngc_4414", 1), ("ngc_4414", 18),
                                        ("ngc_4414", 28), ("ngc_4414", 33), ("ngc_4414", 40), ("ngc_4414", 52)}
    # The saturation's bound is met with equality on a saturated ring, to rounding (the excess is rounding's).
    assert -1e-15 < saturated_most <= 1e-12


def test_a_ring_the_solver_cannot_converge_raises_and_nothing_catches_it(prod, monkeypatch):
    """D216 item 7: "a ring that fails to converge within the counts is a build failure (raise) ... there is no
    fallback and no linear substitute". Since gate G3 the galaxies that raised at the first build converge, so the
    failure is forced as the instrument's own test forces it - the solver is given fewer Newton steps than a ring
    needs - and it is shown to come through every door uncaught: the pattern's profiles, a point, a sector, the
    cell means, the stage and the whole run."""
    model = prod[0].get(DEFAULT_MODEL)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "pattern_seed": 33}
    o = run(model, given, only=GAS_PATTERN_READS)
    assert float(o.fields["pitch_angle"]) == pytest.approx(1.780, abs=2e-3)
    # With the steps it needs (10 at most) this galaxy - the pattern seed that raised before G3 - is solved, its
    # worst ring on a rounding floor above the absolute tolerance.
    gm.forget_solutions()
    solved = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert 5 < solved.diagnostics.worst_steps <= 10 and solved.profiles.min() > 0.0 and solved.diagnostics.floor.max() > 1e-10
    full = np.asarray(run(model, given, only=("gas_density_contrast",)).fields["gas_density_contrast"])
    assert np.all(np.isfinite(full)) and full.min() > 0.0
    # Refused its steps, it raises - and nothing between the solver and the caller catches it.
    gm.forget_solutions()  # the cache must not hand back the solution just made
    monkeypatch.setattr(gr, "solve", functools.partial(gr.solve, max_steps=4))
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert not gp.flat
    with pytest.raises(gr.ConvergenceError, match="Newton did not converge") as failure:
        gp.profiles
    assert failure.value.steps == 4 and failure.value.residual > 1e-10
    for call in (lambda: gp.contrast_at(np.array([8.0]), np.array([1.0])),
                 lambda: gp.sector_means(8.0, np.linspace(0.0, 2.0 * np.pi, 5)),
                 lambda: gp.cell_means(o.grid.R, o.grid["phi"].edges),
                 lambda: run(model, given, only=("gas_density_contrast",)),
                 lambda: run(model, only=("gas_density_contrast",))):  # the default galaxy needs 8 steps: it raises too
        with pytest.raises(gr.ConvergenceError):
            call()
    assert len(gm._SOLUTIONS) == 0  # a failure is not kept
    # With the layer off there is no pattern to solve, and the galaxy runs whatever the solver is given.
    off = run(model, given, only=("gas_density_contrast",), layer=False)
    assert np.all(np.asarray(off.fields["gas_density_contrast"]) == 1.0)
    monkeypatch.undo()
    gm.forget_solutions()


# --- the law, re-derived by hand ---------------------------------------------------------------------------------


def test_the_law_rederived_by_hand_on_three_rings(prod):
    """D216's law on three rings of the default galaxy, independent of the modules: f_m and ε are computed here
    from the **published** ``epicyclic_frequency``, ``disc_surface_density``, pitch, amplitudes, phases and the
    bar's taper with this file's arithmetic - no function of ``pattern``, ``gas_pattern`` or ``gas_response`` -
    and the model's ring is held to the equation by two roads the module does not take: a dense Newton on the
    same cells (agreement to rounding), and the differential equation itself through a spectral derivative (to
    the cells' second-order error).

        R kpc     Ω       κ       X         ε         f_2 … f_6 (the untapered forcing)             1 − taper
        4.0125    59.942  91.930  4.26101   0.069486  0.23897 0.59227 0.78969 0.98712 1.04999   0.29664
        7.9875    30.895  41.442  7.92860   0.077433  0       0.25498 0.45908 0.57385 0.68861   0.99602
        10.0125   23.905  30.879  12.00573  0.082903  0       0       0.23099 0.45286 0.56434   1.00000

    X(7.99 kpc) = 7.93 is D215's hand anchor, and Ω and κ there are the probe's 30.9 and 41.4. At every ring the
    **published field** is held to the composition written out here: the mean over each grid cell of
    g = w_arm s + w_bar (1 + B cos 2(φ − φ_bar)) - the hand's ring integrated over the cell by the trapezoid rule
    on its own breakpoints, the bar's cosine by its own integral (gate G3 item 4). At 4 kpc, inside the bar's
    reach, the bar's term carries 0.70 of the weight. The spectral residual of the differential equation reads
    4.8e-4, 9.1e-5 and 3.8e-5 on the three rings: the cells' second-order error."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert c["G"] == pytest.approx(G_HAND, rel=1e-9) and c["GAS_DISPERSION"] == SOUND_SPEED_HAND
    o = template_run(prod, "milky_way")
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    assert edges[0] == 0.0 and edges[-1] == pytest.approx(2.0 * math.pi, rel=1e-15) and edges.size == 361
    kappa, sigma, v = (np.asarray(F[k], dtype=float) for k in ("epicyclic_frequency", "disc_surface_density", "circular_velocity"))
    assert o.decls["disc_surface_density"].unit == "Msun/pc2" and o.decls["epicyclic_frequency"].unit == "km/s/kpc"
    pitch = math.radians(float(F["pitch_angle"]))
    a_bar, B = float(F["bar_half_length"]), float(F["bar_contrast"])
    theta = [float(F[n]) for n in pt.PHASE_FIELDS]
    published = np.asarray(F["gas_density_contrast"])
    gp = shape_of(model, o)
    n = gr.CELLS
    assert n == 1440
    h = 2.0 * math.pi / n
    chi = -math.pi + (np.arange(n) + 0.5) * h
    for radius, omega_want, kappa_want, x_want, eps_want, f_want, weight_want, ode_want in (
        (4.0125, 59.942, 91.930, 4.26101, 0.069486, (0.23897, 0.59227, 0.78969, 0.98712, 1.04999), 0.29664, 4.85e-4),
        (7.9875, 30.895, 41.442, 7.92860, 0.077433, (0.0, 0.25498, 0.45908, 0.57385, 0.68861), 0.99602, 9.1e-5),
        (10.0125, 23.905, 30.879, 12.00573, 0.082903, (0.0, 0.0, 0.23099, 0.45286, 0.56434), 1.00000, 3.8e-5),
    ):
        i = int(np.argmin(np.abs(R - radius)))
        Ri = float(R[i])
        assert Ri == pytest.approx(radius, abs=1e-9)
        # The frame: the arms turn at the disc's own angular speed, published as a statement (and read by nothing).
        assert float(np.asarray(F["arm_pattern_speed"])[i]) == float(v[i]) / Ri == pytest.approx(omega_want, abs=1e-3)
        x = float(kappa[i]) ** 2 * Ri / (2.0 * math.pi * G_HAND * float(sigma[i]) * 1.0e6)  # Σ per pc² → per kpc²
        eps = SOUND_SPEED_HAND / (float(kappa[i]) * Ri * math.sin(pitch))
        taper = math.exp(-((Ri / a_bar) ** 4))
        untapered = [float(np.asarray(F[pt.amplitude_field(m)])[i]) / (1.0 - taper) for m in (2, 3, 4, 5, 6)]
        f = [m * a / (x * math.sin(pitch)) for m, a in zip((2, 3, 4, 5, 6), untapered)]
        assert float(kappa[i]) == pytest.approx(kappa_want, abs=1e-3) and x == pytest.approx(x_want, abs=2e-5), radius
        assert eps == pytest.approx(eps_want, abs=2e-6) and 1.0 - taper == pytest.approx(weight_want, abs=2e-5), radius
        assert f == pytest.approx(f_want, abs=2e-5), radius
        # The module's own f and ε are these (its arithmetic goes through the unit amplitudes: equal to rounding).
        assert gp.forcing_amplitudes()[i].tolist() == pytest.approx(f, rel=1e-12, abs=1e-15)
        assert float(gp.epsilon()[i]) == pytest.approx(eps, rel=1e-13)
        forcing = sum(f_m * np.cos(m * chi - t) for m, f_m, t in zip((2, 3, 4, 5, 6), f, theta))
        # Road one: the dense Newton on the same cells (measured: 1e-13, 1e-14 and 7e-15 apart).
        by_hand, steps = hand_newton(forcing, eps)
        model_ring = gp.profiles[i]
        assert steps <= 12 and float(np.abs(model_ring - by_hand).max()) < 1e-9, (radius, steps, float(np.abs(model_ring - by_hand).max()))
        assert float(np.abs(model_ring / by_hand - 1.0).max()) < 1e-8, radius  # in the trough too, where s is 1e-6
        assert abs(float(model_ring.sum()) / n - 1.0) < 1e-12 and model_ring.min() > 0.0
        # Road two: the differential equation, ε² (ln s)″ = s − 1 − g, the second derivative taken spectrally. What
        # is left is the cells' second-order error, ε² h²/12 max|(ln s)⁗|: pinned as read.
        log_s = np.log(model_ring)
        k = np.fft.rfftfreq(n, d=1.0 / n)
        second = np.fft.irfft(-(k**2) * np.fft.rfft(log_s), n=n)
        ode = eps**2 * second - (model_ring - 1.0 - forcing)
        assert float(np.abs(ode).max()) == pytest.approx(ode_want, rel=0.03), (radius, float(np.abs(ode).max()))
        # The published field, at the grid's own cells: the hand's ring averaged over each cell's χ - the cell's φ
        # edges less the winding at the ring's radius - weighed by 1 − taper, and the bar's own term, averaged over
        # the same cell, by the taper. S57 (D216 G3): was the hand's ring read at each cell's centre.
        winding, bar_angle = math.log(Ri) / math.tan(pitch), math.log(a_bar) / math.tan(pitch)
        lo, hi = edges[:-1], edges[1:]
        ring = hand_cell_means(by_hand, lo - winding, hi - winding)
        bar = (np.sin(2.0 * (hi - bar_angle)) - np.sin(2.0 * (lo - bar_angle))) / (2.0 * (hi - lo))
        composed = (1.0 - taper) * ring + taper * (1.0 + B * bar)
        assert float(np.abs(published[i] - composed).max()) < 1e-11, (radius, float(np.abs(published[i] - composed).max()))
        assert published[i].min() >= taper * (1.0 - B) and abs(float(published[i].sum()) / 360.0 - 1.0) < 1e-13
    # Inside the bar's reach the two terms are both there: at 4 kpc the bar carries 0.70 of the weight.
    # S57 (D216 G3): was (2.0112, 0.5010), the centre samples.
    i = row(o, 4.0125)
    assert float(published[i].max()) == pytest.approx(2.0108, abs=1e-3) and float(published[i].min()) == pytest.approx(0.5010, abs=1e-3)


def test_the_forcing_carries_the_saturation_by_hand_on_the_most_saturated_seed(prod):
    """Gate G3 item 3: "A_m is the stellar field's actual cosine amplitude on the ring (published over (1 − taper)),
    the saturation in it, because the gas answers the stars that exist" - the forcing is the saturated one, as
    built. The hand test it owes, on the suite's most saturated pattern seed and from the published fields alone.

    Over the suite's seeds (sixty pattern seeds, each template's inputs) the smallest saturation is 0.574, on
    ``ngc_4414`` at pattern seed 28 (0.642 on the Milky Way template, the same seed; the arm amplitude draws 0.786
    and the bar's 0.410); 83 of its rings are saturated, from 3.1 to 9.3 kpc. Two of them are read: the most
    saturated ring of all (5.36 kpc, the taper 4e-3) and the most saturated one outside the bar's reach (the taper
    under 1e-6). On each: the published amplitudes sum to 1 − B·taper to rounding - that is what saturated means;
    f_m = m A_m(published)/((1 − taper) X sin p), by this file's arithmetic, is the stage's forcing to 1e-15; and
    this file's dense Newton on that forcing is the stage's profile to 1e-10. The unsaturated amplitude A √gain
    would force 1/0.57 times harder: it is not what the stage uses."""
    model = prod[0].get(DEFAULT_MODEL)
    lowest = min(
        (float(np.min(run(model, {**templates.overrides(templates.TEMPLATES[t]), "pattern_seed": seed, "texture_seed": 0},
                          only=("arm_saturation",)).fields["arm_saturation"])), t, seed)
        for t in TEMPLATES for seed in range(60))
    assert lowest[1:] == ("ngc_4414", 28) and lowest[0] == pytest.approx(0.5744, abs=2e-4)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "pattern_seed": 28, "texture_seed": 0}
    o = run(model, given, only=PATTERN_FIELDS)
    F, R = o.fields, o.grid.R
    gp = shape_of(model, o)
    saturation = np.asarray(F["arm_saturation"], dtype=float)
    kappa, sigma = (np.asarray(F[k], dtype=float) for k in ("epicyclic_frequency", "disc_surface_density"))
    pitch = math.radians(float(F["pitch_angle"]))
    a_bar, B, A = float(F["bar_half_length"]), float(F["bar_contrast"]), float(F["arm_contrast"])
    assert (math.degrees(pitch), A, B) == pytest.approx((7.615, 0.7859, 0.4101), abs=2e-3)
    theta = [float(F[n]) for n in pt.PHASE_FIELDS]
    taper_all = np.exp(-((R / a_bar) ** 4))
    assert int((saturation < 1.0).sum()) == 83 and (R[saturation < 1.0].min(), R[saturation < 1.0].max()) == pytest.approx((3.1125, 9.2625), abs=1e-6)
    most = int(np.argmin(saturation))
    outside = int(np.flatnonzero(taper_all < 1e-6)[np.argmin(saturation[taper_all < 1e-6])])
    n = gr.CELLS
    chi = -math.pi + (np.arange(n) + 0.5) * (2.0 * math.pi / n)
    read = {}
    for i in (most, outside):
        Ri, taper = float(R[i]), float(taper_all[i])
        published = [float(np.asarray(F[pt.amplitude_field(m)])[i]) for m in (2, 3, 4, 5, 6)]
        # Saturated: the modes' amplitudes and the bar's add up to 1 exactly - to rounding.
        assert saturation[i] < 1.0 and sum(published) == pytest.approx(1.0 - B * taper, rel=1e-15, abs=0.0), Ri
        x = float(kappa[i]) ** 2 * Ri / (2.0 * math.pi * G_HAND * float(sigma[i]) * 1.0e6)
        eps = SOUND_SPEED_HAND / (float(kappa[i]) * Ri * math.sin(pitch))
        f = [m * a / ((1.0 - taper) * x * math.sin(pitch)) for m, a in zip((2, 3, 4, 5, 6), published)]
        stage = gp.forcing_amplitudes()[i]
        assert stage.tolist() == pytest.approx(f, rel=1e-15, abs=0.0), (Ri, (stage / np.array(f) - 1.0).tolist())
        assert float(gp.epsilon()[i]) == pytest.approx(eps, rel=1e-15)
        forcing = sum(f_m * np.cos(m * chi - t) for m, f_m, t in zip((2, 3, 4, 5, 6), f, theta))
        by_hand, steps = hand_newton(forcing, eps)
        ring = gp.profiles[i]
        assert float(np.abs(ring - by_hand).max()) < 1e-10 and float(np.abs(ring / by_hand - 1.0).max()) < 1e-8, Ri
        read[i] = (Ri, float(saturation[i]), taper, sum(f), eps, float(ring.max()), float(ring.min()), steps)
        # The unsaturated amplitude, A √gain (the saturation taken back out), is another forcing by 1/saturation.
        carried = np.array(f) > 0.0
        unsaturated = np.array(f)[carried] / float(saturation[i])
        assert carried.sum() >= 3 and float(np.abs(stage[carried] / unsaturated - 1.0).max()) == pytest.approx(1.0 - float(saturation[i]), rel=1e-12)
    # The two rings, as read: R, the saturation, the taper; the forcing's sum, ε, the crest and the trough of s.
    # 5.36 kpc: 0.574, 4.3e-3; Σf 5.44, ε 0.151, s from 4.3e-4 to 4.83. 6.79 kpc: 0.636, 8.5e-7; Σf 4.31, ε 0.169,
    # s from 9.0e-3 to 4.12. (The hand's Newton took 7 steps on each.)
    assert read[most][:3] == pytest.approx((5.3625, 0.5744, 4.308e-3), abs=2e-4)
    assert read[most][3:7] == pytest.approx((5.440, 0.1508, 4.829, 4.26e-4), rel=2e-3)
    assert read[outside][:2] == pytest.approx((6.7875, 0.6364), abs=2e-4) and read[outside][2] == pytest.approx(8.47e-7, rel=0.01)
    assert read[outside][3:7] == pytest.approx((4.311, 0.1693, 4.121, 9.00e-3), rel=2e-3)


def test_one_weak_mode_is_the_linear_response_and_a_lone_mode_has_no_offset():
    """Two anchors on a made-up disc, with the arithmetic written here. A weak mode's response is the linear one,
    s − 1 = f/(1 + m² ε²) cos(mχ − θ) - so f and ε reach the solver as the law writes them, sign and phase
    included. And **the offset is zero for a lone mode, exactly, by the equation's symmetry** (D210 ruling 3, D216
    item 12; gate G3 item 7): one mode's response is even about the mode's crest at any amplitude."""
    R = DEFAULT.build().R
    i = int(np.argmin(np.abs(R - 8.0)))
    m, theta, arm, pitch = 4, 0.7, 0.4, 13.5
    weak = one_mode(m, strength=0.01, phases=(0.0, 0.0, theta, 0.0, 0.0), arm=arm, pitch=pitch)
    kappa, sigma = math.sqrt(2.0) * 220.0 / R[i], 50.0 * math.exp(-(R[i] - 8.0) / 2.6)
    sin_p = math.sin(math.radians(pitch))
    x = kappa**2 * R[i] / (2.0 * math.pi * G_HAND * sigma * 1.0e6)
    f = m * arm * 0.01 / (x * sin_p)
    eps = SOUND_SPEED_HAND / (kappa * R[i] * sin_p)
    assert (float(weak.forcing_amplitudes()[i, 2]), float(weak.epsilon()[i])) == pytest.approx((f, eps), rel=1e-12)
    chi = gr.cell_centres()
    linear = f / (1.0 + m * m * eps * eps) * np.cos(m * chi - theta)
    departure = float(np.abs(weak.profiles[i] - 1.0 - linear).max())
    # f = 0.0077 here; what is left of the linear response is second order in it (measured 2.4e-5: about f²/2).
    assert f == pytest.approx(0.00768, abs=1e-5) and departure < f * f
    # Symmetry about the crest, at full strength: phase 0 puts a crest of the four on the edge between cells 719
    # and 720 (χ = 0), and the response is even about it.
    strong = one_mode(m, strength=1.0, arm=arm, pitch=pitch)
    s = strong.profiles[i]
    assert float(s.max()) > 1.5 and int(np.argmax(s)) in (0, 1439, 359, 360, 719, 720, 1079, 1080)
    assert float(np.abs(s[:720][::-1] - s[720:]).max()) < 1e-10
    assert s[719] == pytest.approx(float(s.max()), rel=1e-12) and s[720] == pytest.approx(float(s.max()), rel=1e-12)
    # And where the crests are: at χ = θ/m (and every quarter turn from it) for a phase θ, to the cell.
    turned = one_mode(m, strength=1.0, phases=(0.0, 0.0, theta, 0.0, 0.0), arm=arm, pitch=pitch).profiles[i]
    away = (float(chi[int(np.argmax(turned))]) - theta / m) % (2.0 * math.pi / m)
    assert min(away, 2.0 * math.pi / m - away) <= 2.0 * math.pi / gr.CELLS


@pytest.mark.parametrize("template", TEMPLATES)
def test_with_several_modes_the_two_crests_are_cells_apart_as_read(prod, template):
    """D216's prediction "offset 0 on every ring", as gate G3 words the record (item 7): "zero for a lone mode,
    exactly, by the equation's symmetry; with several modes the gas crest and the stellar sum's crest are within
    one solver cell (0.25°) on the default galaxy because each mode is answered with its own weight; no offset is
    put in and none is published". Read here on the solver's own cells, the tallest crest of s against the tallest
    crest of the stellar modes' sum, ring by ring.

    **The Milky Way template: within one solver cell on every one of the 53 rings over 6-10 kpc (the same cell on
    5, one apart on 48), and on 161 of the 165 rings that carry a mode; two rings read two cells, and on two (12.1
    and 12.2 kpc, where the six-armed mode is all but alone and six nearly equal crests stand) the gas's tallest
    crest is another arm's. ``ngc_4414`` is not within a cell: over 6-10 kpc the two are the same cell on 20 rings,
    one apart on 12, two on 13, and three to five on 8 (five cells is 1.25 degrees); 7 at most over the disc.**
    G3's wording is the default galaxy's, and holds on it over the band the check reads; the other template's
    reading is recorded beside it."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R = o.grid.R
    gp = shape_of(model, o)
    s, psi = gp.profiles, gp.stellar_sum()

    def apart(i: int) -> int:
        d = abs(int(s[i].argmax()) - int(psi[i].argmax()))
        return min(d, gr.CELLS - d)

    band = [apart(i) for i in np.flatnonzero(gp.carries & (R >= 6.0) & (R <= 10.0))]
    every = [apart(i) for i in np.flatnonzero(gp.carries)]
    same_arm = [d for d in every if d <= 10]
    want = {
        "milky_way": dict(band=[5, 48], most=2, other_arm=2, within_one=161),
        "ngc_4414": dict(band=[20, 12, 13, 2, 4, 2], most=7, other_arm=0, within_one=37),
    }[template]
    assert np.bincount(band).tolist() == want["band"] and len(band) == 53
    assert max(same_arm) == want["most"] and len(every) - len(same_arm) == want["other_arm"]
    assert sum(1 for d in every if d <= 1) == want["within_one"]


# --- the interpolation of the point function, in χ and in R (D216 item 9; gate G3 item 5) -----------------------


def midpoint_error(s: np.ndarray) -> np.ndarray:
    """Per ring, how far the linear interpolant is from the profile midway between two cell centres: the profile
    there by its own trigonometric series (a half-cell shift of its Fourier coefficients - the response is smooth
    and its spectrum has fallen to rounding well under the cells' Nyquist number, which the caller checks)."""
    n = s.shape[1]
    spectrum = np.fft.rfft(s, axis=1)
    k = np.arange(spectrum.shape[1])
    midway = np.fft.irfft(spectrum * np.exp(1j * math.pi * k / n)[None, :], n=n, axis=1)
    return np.abs(0.5 * (s + np.roll(s, -1, axis=1)) - midway).max(axis=1)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_interpolation_errors_are_pinned_as_measured(prod, template):
    """Gate G3 item 5: "1440 cells stand. Pinned as measured: s 3.5e-4 beyond 6 kpc, 1.2e-3 inside the bar's
    reach (≤ 1.2e-5 of the field there), the point field 3.0e-4, the R-interpolation 5.7e-4 / 7.9e-4."

    **In χ, at the cells' midpoints** (the worst place for the point function: h²/8 · max|s″|). The instrument's
    two hard rings read 1.96e-4 and 1.54e-4. The model's rings, per quantity: **s beyond 6 kpc 3.5e-4 at worst for
    the Milky Way template (9.2e-5 for ``ngc_4414``); s inside the bar's reach 1.2e-3 (1.2e-3)** - where the
    untapered forcing sums to 4-6 and the crest stands at 4-5.7 - **which on that ring is 9.4e-6 (1.4e-5) of the
    field, the arm's weight there being under 1.2 %; the point field 3.0e-4 (2.9e-4) at worst over every ring.**
    (The published field is cell means, whose error is smaller: the test of the cell-averaged field, above.)

    **In R, midway between two grid rings**, against a ring solved there with the law's inputs linear in R
    between the two rings (the amplitudes as ``ArmPattern`` reads them, κ and Σ alike): the blend of the two
    neighbours at the same χ is off by 5.7e-4 (7.9e-4) of the point field at worst, its median 8e-5 (1.7e-4);
    on s itself by 0.22 (0.30), on the innermost pair, where ε falls by a third between two rings and the arm's
    weight is 1e-7. The worst pairs are where a mode enters or leaves between two rings."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R = o.grid.R
    gp = shape_of(model, o)
    s, carries = gp.profiles, gp.carries
    taper = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)[0]
    # In χ.
    spectrum = np.abs(np.fft.rfft(s, axis=1)) / s.shape[1]
    assert float(spectrum[:, 480:].max()) < 1e-13  # resolved: nothing left above two thirds of the Nyquist number
    error = midpoint_error(s)
    worst = int(np.argmax(error))
    want = {"milky_way": (1.240e-3, 2.963e-4, 3.486e-4, 9.37e-6), "ngc_4414": (1.210e-3, 2.886e-4, 9.232e-5, 1.45e-5)}[template]
    got = (float(error.max()), float((error * (1.0 - taper)).max()), float(error[R > 6.0].max()), float(error[worst] * (1.0 - taper[worst])))
    assert got == pytest.approx(want, rel=0.01), got
    assert 1.0 - taper[worst] < 0.012 and R[worst] < 2.0  # the worst ring of s: deep inside the bar's reach
    # The interpolant the pattern reads is that linear one: at a midpoint, the mean of the two cells.
    chi = gr.cell_centres() + math.pi / gr.CELLS
    i = int(np.argmax(error * (1.0 - taper)))
    assert np.allclose(gp.response_at(R[i], chi), 0.5 * (s[i] + np.roll(s[i], -1)), rtol=0.0, atol=1e-12)
    # In R.
    pairs = np.flatnonzero(carries[:-1] | carries[1:])
    mid = 0.5 * (R[pairs] + R[pairs + 1])
    unit = np.stack([np.interp(mid, R, u) for u in gp.unit])
    kappa, sigma = np.interp(mid, R, gp.epicyclic), np.interp(mid, R, gp.surface_density)
    f = gr.forcing_amplitudes(pt.ARM_MODES, (gp.arm * unit).T, pt.local_swing_x(mid, kappa, sigma, gp.gravity), gp.sin_pitch)
    solved, _ = gr.solve(gr.forcing(pt.ARM_MODES, f, np.asarray(gp.phases)), gr.epsilon(gp.sound_speed, kappa, mid, gp.sin_pitch))
    weight = 1.0 - pt.bar_terms(mid, gp.pitch_deg, gp.bar_length)[0]
    apart = np.abs(solved - 0.5 * (s[pairs] + s[pairs + 1])).max(axis=1)
    want = {"milky_way": (0.2208, 5.709e-4, 8.45e-5, 6.45), "ngc_4414": (0.2966, 7.933e-4, 1.69e-4, 9.525)}[template]
    got = (float(apart.max()), float((apart * weight).max()), float(np.median(apart * weight)), float(mid[int(np.argmax(apart * weight))]))
    assert got == pytest.approx(want, rel=0.02), got
    # And what a point between two rings reads is that blend, at its own χ: the point function at the mid radius.
    j = int(np.argmax(apart * weight))
    centres = gr.cell_centres()
    assert np.allclose(gp.response_at(mid[j], centres), 0.5 * (s[pairs[j]] + s[pairs[j] + 1]), rtol=0.0, atol=1e-12)


# --- the predictions, read before they are judged (B4) -----------------------------------------------------------


def test_the_gate_s_predictions_as_measured(prod):
    """D216's predictions for the default galaxy, read on the built model before they were judged. The probe that
    made them forced with the *tapered* amplitudes; the ruling forces with the untapered ones and composes with the
    bar afterwards (item 8), so "outside the bar's reach these are the ruling's" (Fable).

        R kpc     predicted: crest / trough / ratio     as built, s: crest / trough / ratio     published g: crest / trough
        4.0125    1.91 / 0.37  / 1.57                   4.170 / 4.5e-7 / 3.811                  2.011 / 0.501
        5.9625    3.02 / 0.007 / 2.69                   3.480 / 2.5e-4 / 3.208                  3.009 / 0.128
        7.9875    2.79 / 0.018 / 2.56                   2.797 / 0.0171 / 2.571                  2.787 / 0.0220
        10.0125   2.09 / 0.18  / 2.04                   2.090 / 0.1819 / 2.037                  2.089 / 0.1823
        10.9875   1.77 / 0.38  / 1.89                   1.765 / 0.3845 / 1.886                  1.764 / 0.3847
        12.0375   1.20 / 0.81  / 1.28                   1.198 / 0.8114 / 1.281                  1.198 / 0.8117

    (The published g is the cells' means since gate G3: its crest reads a few 1e-4 under the point function's and
    its trough as much over.) **Held** at 10, 11 and 12 kpc, to the figures given. **Held at R₀ to the taper's
    share**: the taper is 0.0040 at 7.99 kpc, the untapered forcing 0.4 % stronger, and the crest and the ratio
    stand 0.3-0.4 % above the probe's (the trough 5 % under: 0.0171 against 0.018). **Not held inside the bar's
    reach, as foreseen**: at 4 and 6 kpc s answers the untapered forcing (its sum 3.7 and 2.8, against the probe's
    1.1 and 2.3) and is far stronger than the probe's; the published field there is s at 0.30 and 0.82 of the
    weight with the bar's own term. Nothing was changed to make a number hold.

    Also read: "interarm nearly empty where the forcing's sum exceeds 1 (6-8 kpc)" - held, the trough of s
    2.9e-4 to 0.017 there; "Newton at most 8 steps here" - held, 8; "34 on ``ngc_4414``" - the probe's own Newton;
    the instrument takes 9."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, "milky_way")
    R = o.grid.R
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    s, ratio = gp.profiles, gp.arm_ratio(MASK_WIDTH)
    f_sum = gp.forcing_amplitudes().sum(axis=1)
    table = (
        # R, predicted (crest, trough, ratio), as built s (crest, trough, ratio), published g (crest, trough), held
        # S57 (D216 G3): the published g were (2.0112, 0.5010), (3.0096, 0.1282), (2.7874, 0.0220), (2.0892, 0.1822),
        # (1.7646, 0.3845), (1.1982, 0.8116) - the point function at the cells' centres; they are the cells' means.
        (4.0125, (1.91, 0.37, 1.57), (4.1701, 4.48e-7, 3.8106), (2.0108, 0.5010), False),
        (5.9625, (3.02, 0.007, 2.69), (3.4796, 2.54e-4, 3.2080), (3.0088, 0.1282), False),
        (7.9875, (2.79, 0.018, 2.56), (2.7967, 0.0171, 2.5705), (2.7868, 0.0220), True),
        (10.0125, (2.09, 0.18, 2.04), (2.0896, 0.1819, 2.0375), (2.0888, 0.1823), True),
        (10.9875, (1.77, 0.38, 1.89), (1.7648, 0.3845, 1.8857), (1.7642, 0.3847), True),
        (12.0375, (1.20, 0.81, 1.28), (1.1984, 0.8114, 1.2812), (1.1981, 0.8117), True),
    )
    for radius, predicted, built, composed, held in table:
        i = row(o, radius)
        assert float(R[i]) == pytest.approx(radius, abs=1e-9)
        got = (float(s[i].max()), float(s[i].min()), float(ratio[i]))
        assert got[0] == pytest.approx(built[0], abs=2e-3) and got[2] == pytest.approx(built[2], abs=2e-3), radius
        assert got[1] == pytest.approx(built[1], rel=0.03), radius
        assert (float(g[i].max()), float(g[i].min())) == pytest.approx(composed, abs=2e-4), radius
        # Against the prediction: the crest and the ratio within 0.5 % and the trough within 0.006 where it held.
        near = abs(got[0] / predicted[0] - 1.0) < 5e-3 and abs(got[2] / predicted[2] - 1.0) < 5e-3 and abs(got[1] - predicted[1]) < 6e-3
        assert near == held, (radius, got, predicted)
    # The forcing's sum at the six rings: the untapered one (the probe's tapered sums were 1.08, 2.28, 1.97, 1.25, 0.88, 0.25).
    sums = [float(f_sum[row(o, radius)]) for radius, *_ in table]
    assert sums == pytest.approx([3.659, 2.781, 1.976, 1.249, 0.884, 0.247], abs=3e-3)
    # The gaps between the arms, 6 to 8 kpc: nearly emptied, on every ring.
    band = (R >= 6.0) & (R <= 8.0)
    assert np.all(f_sum[band] > 1.0) and float(s[band].min(axis=1).max()) < 0.02 and float(s[band].min()) == pytest.approx(2.93e-4, rel=0.03)
    assert gp.diagnostics.worst_steps == 8


# --- the disclosed check: NOT an acceptance row (I3 stands) ------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_disclosed_check_the_ratio_of_means_and_the_width(prod, template):
    """**A disclosed check, not an acceptance row** (D216, the gate's follow-up: "row 38 is not an acceptance row;
    the number 38 is not taken; I3 stands as tested"). Layer on, each template at its default seeds, per ring over
    6-10 kpc. **Disclosed** (D113): the probe printed 2.56 at R₀ and 2.0-2.8 over 6-10 kpc before the check was
    defined, so it cannot be a blind test. The definitions are the gates', fixed before the numbers they judge.

    *The ratio of means*: the mean of s inside the source's arm mask - the share m_eff W/(2π R sin p) of the ring,
    at most a half, where the stellar modes' sum is highest (S56's mask) - over its mean outside, against PHANGS's
    2.73 within its 16th-84th percentiles 1.37-5.79. **The verdict, in gate G3's words (item 7): "a hit, disclosed
    (D113): Milky Way median 2.571, 53 of 53 rings inside 1.37-5.79; ``ngc_4414`` median 1.881 inside, seven of
    its 53 rings (the outer ones) below the 16th percentile, recorded".** Those seven are 9.49 to 9.94 kpc, where
    its arms fade, down to 1.076. Nothing was tuned to land it.

    *The width*, as gate G3 fixed its definition (item 6): "the FWHM of the ring's tallest crest of s as a fraction
    of the period 2π/m of the mode of largest forcing m·A_m - the mode the gas answers most strongly - not a
    tie-break on amplitude", the half level midway between the ring's trough and crest, against the measured 0.17.
    **As read: the Milky Way template 0.466 at the median, 0.423 to 0.481; ``ngc_4414`` 0.512, 0.479 to 0.526 - a
    miss on every ring, by 2.5 to 2.8 times and by 2.8 to 3.1 times** (G3 recorded "2.5-3.0× on every ring";
    ``ngc_4414``'s widest ring reads 3.09). Its two named suspects (D216, "Honesty"): the steady pressure-balanced
    response in place of the simulations' converging infall, and the razor-thin forcing of the five- and six-armed
    modes.

    **The other two readings, printed beside it and not the check** (G3: "the build's first reading (0.311) was
    the kindest and is replaced"). The first build read the period of the mode of *largest amplitude*; on 52 of
    the Milky Way's 53 rings (32 of ``ngc_4414``'s) the top amplitude is a tie between arm numbers - the gain is
    whole for each - and it took the lower one, as the probe had: 0.311 at the median, 0.211 to 0.481 (0.422, 0.262
    to 0.508), a miss by 1.2 to 2.8 times. Taking the higher tied arm number: 0.466, 0.352 to 0.481 (0.506, 0.437
    to 0.525). A miss on every ring under every reading."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert "GAS_ARM_MASK_WIDTH" not in c and "GAS_ARM_WIDTH" not in c  # the model reads neither: tests/gas_check.py
    assert (MASK_WIDTH, WIDTH_TARGET) == (1.5, 0.17)
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    assert float(F["gas_arm_contrast"]) == pytest.approx(RATIO_TARGET, abs=1e-12)  # the target, and no stage's input
    gp = shape_of(model, o)
    band = (R >= 6.0) & (R <= 10.0) & gp.carries
    ratio, width = gp.arm_ratio(MASK_WIDTH)[band], gp.arm_width()[band]
    # The arm numbers the three readings take on every ring, from the published amplitudes, by this file's arithmetic.
    modes = np.arange(2.0, 7.0)
    amplitudes = np.stack([np.asarray(F[n], dtype=float) for n in pt.AMPLITUDE_FIELDS])
    by_forcing = modes[np.argmax(modes[:, None] * amplitudes, axis=0)]
    lower_tied = modes[np.argmax(amplitudes, axis=0)]
    higher_tied = modes[len(modes) - 1 - np.argmax(amplitudes[::-1], axis=0)]
    tied = int(((amplitudes == amplitudes.max(axis=0)).sum(axis=0) > 1)[band].sum())
    assert np.array_equal(gp.strongest_forcing()[band], by_forcing[band])
    # One measurement - the crest's width in radians - read against three periods.
    readings = {"largest forcing (the check)": width,
                "largest amplitude, the lower arm number on a tie (the first build's)": gp.arm_width(lower_tied)[band],
                "largest amplitude, the higher arm number on a tie": gp.arm_width(higher_tied)[band]}
    assert np.allclose(readings["largest amplitude, the higher arm number on a tie"] / higher_tied[band], width / by_forcing[band], rtol=1e-12)
    for name, values in readings.items():
        print(f"{template}: width by the {name}: median {np.median(values):.3f}, {values.min():.3f} to {values.max():.3f}, "
              f"{values.min() / WIDTH_TARGET:.2f} to {values.max() / WIDTH_TARGET:.2f} times the measured {WIDTH_TARGET}")
    want = {
        "milky_way": dict(rings=53, ratio=(2.5705, 2.0523, 3.1921), inside=53, tied=52,
                          width=(0.4660, 0.4229, 0.4807), lower=(0.3107, 0.2114, 0.4807), higher=(0.4660, 0.3524, 0.4807)),
        "ngc_4414": dict(rings=53, ratio=(1.8814, 1.0762, 2.8299), inside=46, tied=32,
                         width=(0.5120, 0.4790, 0.5260), lower=(0.4218, 0.2620, 0.5083), higher=(0.5061, 0.4366, 0.5253)),
    }[template]
    assert int(band.sum()) == want["rings"] and tied == want["tied"]
    assert (float(np.median(ratio)), float(ratio.min()), float(ratio.max())) == pytest.approx(want["ratio"], abs=2e-3)
    # S57 (D216 G3 item 6): the check's width was (0.3107, 0.2114, 0.4807) and (0.4218, 0.2620, 0.5083) - the reading
    # by the largest amplitude, the lower arm number on a tie, which is kept below as the record of the first build.
    for values, key in zip(readings.values(), ("width", "lower", "higher")):
        assert (float(np.median(values)), float(values.min()), float(values.max())) == pytest.approx(want[key], abs=2e-3), key
    # The verdicts, as read: the median ratio inside PHANGS's percentiles (a hit, disclosed) ...
    assert RATIO_LOW <= float(np.median(ratio)) <= RATIO_HIGH
    assert int(((ratio >= RATIO_LOW) & (ratio <= RATIO_HIGH)).sum()) == want["inside"] and np.all(ratio <= RATIO_HIGH)
    below = R[band][ratio < RATIO_LOW]
    assert below.size == want["rings"] - want["inside"] and (below.size == 0 or (below.min() == pytest.approx(9.4875, abs=1e-6) and below.max() == pytest.approx(9.9375, abs=1e-6)))
    # ... and the width a miss on every ring, under every reading: wider than the measured arm - by 2.5 to 3.1 times
    # as the check reads it.
    for values in readings.values():
        assert np.all(values > WIDTH_TARGET)
    assert 2.45 < float(width.min()) / WIDTH_TARGET and float(width.max()) / WIDTH_TARGET < 3.1

    # The two measurements, re-made here on one ring by this file's arithmetic (a sort and a walk), from the
    # published amplitudes and phases: the module's helpers are these.
    i = row(o, 8.0)
    amplitudes = amplitudes[:, i]
    phases = np.array([float(F[n]) for n in pt.PHASE_FIELDS])
    chi = -math.pi + (np.arange(1440) + 0.5) * (2.0 * math.pi / 1440)
    psi = (amplitudes[:, None] * np.cos(modes[:, None] * chi[None, :] - phases[:, None])).sum(axis=0)
    m_eff = float((modes * amplitudes**2).sum() / (amplitudes**2).sum())
    share = min(0.5, m_eff * MASK_WIDTH / (2.0 * math.pi * float(R[i]) * math.sin(math.radians(float(F["pitch_angle"])))))
    s = gp.profiles[i]
    order = np.argsort(-psi, kind="stable")
    inside = int(round(share * s.size))
    by_hand = float(s[order[:inside]].mean() / s[order[inside:]].mean())
    assert float(gp.arm_ratio(MASK_WIDTH)[i]) == pytest.approx(by_hand, rel=2e-3)  # a whole cell at the cut, against a share of it
    half = 0.5 * (float(s.max()) + float(s.min()))
    top = int(np.argmax(s))
    ahead = next(k for k in range(1, s.size) if s[(top + k) % s.size] <= half)
    behind = next(k for k in range(1, s.size) if s[(top - k) % s.size] <= half)
    strongest = float(modes[int(np.argmax(modes * amplitudes))])  # the mode of largest forcing m·A_m
    cells = (ahead + behind - 1) * (2.0 * math.pi / s.size) / (2.0 * math.pi / strongest)
    assert float(gp.arm_width()[i]) == pytest.approx(cells, abs=1.5 * strongest / s.size)  # whole cells against the crossing


def test_the_check_s_measurements_on_shapes_whose_answers_are_known():
    """The two measuring functions on profiles written here. A cosine's full width at half maximum is half its
    period; a ring that is 3 on a quarter of its cells and 1/3 elsewhere has a ratio of means of 9 in a mask of a
    quarter laid on its high part, and 1 in a mask laid by an order that knows nothing of it; the mask's share is
    m W/(2π R sin p), at most a half."""
    chi = gr.cell_centres()
    for m in (2, 3, 6):
        assert gm.crest_width(1.0 + 0.3 * np.cos(m * chi)) == pytest.approx(0.5 * 2.0 * math.pi / m, rel=1e-4)
    assert gm.crest_width(np.exp(4.0 * np.cos(2 * chi - 1.0))) == pytest.approx(2.0 * math.acos(1.0 + math.log(0.5 * (1.0 + math.exp(-8.0))) / 4.0) / 2.0, rel=1e-4)
    assert math.isnan(gm.crest_width(np.ones(1440)))
    step = np.where(np.abs(chi) < 0.25 * math.pi, 3.0, 1.0 / 3.0)
    assert gm.ratio_of_means(step, np.cos(chi), 0.25) == pytest.approx(9.0, rel=1e-12)
    assert gm.ratio_of_means(step, np.cos(chi), 0.5) == pytest.approx((0.5 * 3.0 + 0.5 / 3.0) / (1.0 / 3.0), rel=1e-12)
    assert gm.ratio_of_means(step, np.cos(8 * chi), 0.5) == pytest.approx(1.0, abs=1e-12)
    # The cell the share cuts is counted by the fraction of it inside: continuous in the share.
    ramp = np.linspace(2.0, 0.0, 1440)
    a, b = gm.ratio_of_means(ramp, ramp, 0.25), gm.ratio_of_means(ramp, ramp, 0.25 + 1e-7)
    assert a != b and abs(a - b) < 1e-5
    share = gm.mask_share(np.array([4.0, 4.0, np.nan]), np.array([8.0, 2.0, 8.0]), 0.25, 1.5)
    assert share[0] == pytest.approx(4.0 * 1.5 / (2.0 * math.pi * 8.0 * 0.25)) and share[1] == 0.5 and math.isnan(share[2])
    # The width's mode is the one of largest forcing m·A_m: with equal amplitudes that is the highest arm number.
    R = DEFAULT.build().R
    unit = np.zeros((5, R.size))
    unit[1:4] = 1.0 / math.sqrt(3.0)  # three, four and five arms at one amplitude: a tie the amplitude cannot break
    assert np.all(synthetic(unit).strongest_forcing() == 5.0)
    unit[1] = 0.9  # m·A: 3 × 0.9 = 2.7 against 5 × 0.577 = 2.89 - still five; at 0.97, 2.91: three
    assert np.all(synthetic(unit).strongest_forcing() == 5.0)
    unit[1] = 0.97
    assert np.all(synthetic(unit).strongest_forcing() == 3.0)


def test_nothing_of_the_ridge_builds_the_field(prod):
    """D216 item 11 (iv): "nothing replaces the amplitude: s is the field; ``gas_arm_contrast`` and S56's mask
    survive only as [the check's] target and definition; ``GAS_ARM_WIDTH`` only as the width miss's target". And
    gate G3 item 7: "the two retired constants leave the model's registry and live in ``tests/`` with their
    sources: a stage may not declare reads it does not make." The model declares neither constant and no stage
    names one; the pattern is built from the law's two constants; no stage requires the ratio; and the retired
    machinery is gone from the module."""
    models, impls_, _ = prod
    model = models.get(DEFAULT_MODEL)
    assert GAS_PATTERN_CONSTANTS == ("G", "GAS_DISPERSION") and not hasattr(gm, "GAS_CHECK_CONSTANTS")
    assert GAS_PATTERN.reads_constants == GAS_PATTERN_CONSTANTS and "gas_arm_contrast" not in GAS_PATTERN_READS
    retired = ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")
    for m in models:
        assert not set(retired) & set(m.constants), m.name
        assert {"GAS_ARM_CONTRAST_GRAND_DESIGN", "GAS_ARM_CONTRAST_OTHER", "G", "GAS_DISPERSION"} <= set(m.constants)
        readers = [sid for _, sid in m.stages if "gas_arm_contrast" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [], readers
        declaring = sorted(sid for _, sid in m.stages if set(retired) & set(impls_.get(sid).reads_constants))
        assert declaring == [], declaring
        # ... and every stage that places by the gas declares the two the law does read.
        for sid in ("gas_pattern", "clouds", "cloud_texture", "clusters"):
            assert set(GAS_PATTERN_CONSTANTS) <= set(impls_.get(sid).reads_constants), sid
    # They live in tests/, with the values the model held and their sources.
    assert (gas_check.GAS_ARM_WIDTH, gas_check.GAS_ARM_MASK_WIDTH) == (0.17, 1.5)
    assert "[verified: Egusa et al. 2017, MNRAS 465, 460, arXiv:1610.06642" in gas_check.GAS_ARM_WIDTH_SOURCE
    assert "[verified: Querejeta et al. 2021, A&A 656, A133, arXiv:2109.04491" in gas_check.GAS_ARM_MASK_WIDTH_SOURCE
    # The pattern from fields and the law's two constants alone is the pattern the stage published: the same bits.
    o = template_run(prod, "milky_way")
    R, edges = o.grid.R, o.grid["phi"].edges
    c = constants(model)
    lean = compose.gas_pattern(o.fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS})
    assert lean.cell_means(R, edges).tobytes() == np.asarray(o.fields["gas_density_contrast"]).tobytes()
    fields = {n: o.fields[n] for n in GAS_PATTERN_READS}
    assert GasPattern.from_fields(fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS}).cell_means(R, edges).tobytes() == lean.cell_means(R, edges).tobytes()
    assert GasPattern.from_fields(fields, R, {"G": c["G"]}) is None  # a constant the law reads is missing: no pattern
    # No module of the model names either retired constant in its code (docstrings and comments apart).
    package = Path(gm.__file__).resolve().parents[1]
    named = []
    for path in sorted(package.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body
                      and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings]
        named += [(path.name, name) for name in retired for text in strings if name in text]
        if path.name == Path(gm.__file__).name and path.parent.name == "stages":
            own_tree, own_strings = tree, strings
    assert named == [], named  # not as a key, not in a declaration, not in an about line: the registry does not know them
    assert not any("gas_arm_contrast" in text or "arm_multiplicity" in text or "arm_pattern_speed" in text for text in own_strings)
    for name in ("_Rings", "ridge_value", "kappa_for_width", "mask_means", "pattern_period", "PHASE_CELLS",
                 "HARMONIC_SAMPLES", "RING_MEAN_TOLERANCE", "NEWTON_STEPS", "BISECTION_STEPS"):
        assert not hasattr(gm, name), name
    for name in ("rank", "ridge", "amplitude", "ratio_at", "forcing", "extremes", "ratio", "width", "mask_width"):
        assert not hasattr(GasPattern, name), name
    # Forbidden forms (D216), held by what the code does, read from the syntax tree: nothing is clipped and no error
    # is caught (so no fallback on a ring that did not converge).
    assert [n.attr for n in ast.walk(own_tree) if isinstance(n, ast.Attribute) and n.attr == "clip"] == []
    assert not any(isinstance(n, (ast.Try, ast.ExceptHandler)) for n in ast.walk(own_tree))
    # And nothing reads the frame's field: the flow is 0 by construction, not a difference of two speeds. The one
    # call of the solver hands it the constant 0 as the flow.
    for m in models:
        readers = [sid for _, sid in m.stages if "arm_pattern_speed" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [] and "arm_pattern_speed" in impls_.get("bar").published_names
    solves = [n for n in ast.walk(own_tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "solve"]
    assert len(solves) == 1 and isinstance(solves[0].args[2], ast.Constant) and solves[0].args[2].value == 0.0 and not solves[0].keywords


def test_the_frame_is_published_as_a_statement(model):
    """``arm_pattern_speed`` = v_c/R on every ring, a derived radial field of the ``bar`` stage whose about line
    says what it is: a statement of the frame, not a measurement (the gate's two conditions)."""
    o = out(model)
    speed = np.asarray(o.fields["arm_pattern_speed"])
    assert speed.tobytes() == (np.asarray(o.fields["circular_velocity"]) / o.grid.R).tobytes()
    d = o.decls["arm_pattern_speed"]
    assert d.unit == "km/s/kpc" and d.axes == ("R",) and d.provenance == "derived" and not d.composed
    assert "A statement of the frame, not a measurement" in d.about and "Nothing computes anything from this field" in d.about
    assert d.name in {x.name for x in BAR.publishes}
    assert float(speed[row(o, 7.9875)]) == pytest.approx(30.90, abs=0.01)  # the probe's table: Ω(7.99 kpc) = 30.9
    # The same with the layer off: a law's field.
    off = run(model, layer=False, only=("arm_pattern_speed",))
    assert np.asarray(off.fields["arm_pattern_speed"]).tobytes() == speed.tobytes()


# --- seeded through the pattern; the ratio a derived target ---------------------------------------------------


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
    """The check's target is the bar stage's: 2.73 at the defaults (m = 2 inside the swing window, coherence 1),
    and the same under every pattern seed — no residual, since the source's spread is over segments and bins, not
    galaxies (#131)."""
    assert float(out(model).fields["gas_arm_contrast"]) == pytest.approx(2.73, abs=1e-12)
    values = {run(model, {"pattern_seed": s}, grid=COARSE).fields["gas_arm_contrast"] for s in range(6)}
    assert len(values) == 1
    about = out(model).decls["gas_arm_contrast"].about
    assert "the target of a disclosed check" in about and "No stage reads it" in about


# --- one function at points and on the grid ------------------------------------------------------------------


def test_the_point_function_is_one_function_and_the_published_field_is_its_cell_means(model):
    o = out(model)
    gp = shape_of(model, o)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    on_mesh = gp.contrast(R, phi)
    # S57 (D216 G3): was `on_mesh.tobytes() == published` - the first build published these samples. The published
    # field is the cells' means; the point function at a cell's centre is within 1.7e-3 of its cell's mean.
    published = np.asarray(o.fields["gas_density_contrast"])
    assert published.tobytes() == gp.cell_means(R, edges).tobytes() and published.tobytes() != on_mesh.tobytes()
    assert float(np.abs(published - on_mesh).max()) == pytest.approx(1.718e-3, rel=0.02)
    idx = np.array([5, 77, 190, 399]), np.array([0, 91, 180, 359])
    assert np.array_equal(gp.contrast_at(R[idx[0]], phi[idx[1]]), on_mesh[idx])
    assert np.array_equal(gp.contrast_at(R[:, None], phi[None, :]), on_mesh)
    # Points that share a radius unevenly: each is the single point's value.
    radii = np.concatenate([np.full(7, R[100]), np.full(3, R[150])])
    azimuths = np.linspace(0.3, 5.9, 10)
    alone = np.array([gp.contrast_at(np.array([r]), np.array([p]))[0] for r, p in zip(radii, azimuths)])
    assert np.array_equal(gp.contrast_at(radii, azimuths), alone)
    # A cell's mean is the dense average of the point function over the cell (the same measure, G3 item 4).
    i, j = 106, 200
    dense = edges[j] + (np.arange(2000) + 0.5) * (edges[j + 1] - edges[j]) / 2000
    assert float(gp.contrast_at(np.full_like(dense, R[i]), dense).mean()) == pytest.approx(float(published[i, j]), abs=1e-7)


def test_a_point_reads_its_two_rings_at_its_own_winding_phase(model):
    """D216 item 9. At a grid radius a point reads that ring's profile by the instrument's own interpolant, bit
    for bit; between two rings it reads both **at its own χ** - the winding at the point's radius, not at either
    ring's - and blends them linearly in R; beyond the grid it holds the end ring; the taper and the bar's term
    are taken at the point's own radius."""
    o = out(model)
    gp = shape_of(model, o)
    R = o.grid.R
    s = gp.profiles
    chi = np.random.default_rng(11).uniform(-9.0, 9.0, 500)  # the test's own points, any turn of the ring
    for i in (40, 106, 133, 160):
        assert gp.response_at(R[i], chi).tobytes() == gr.interpolate(s[i], chi).tobytes()
    assert not s.flags.writeable
    k, share = 106, 0.3
    radius = float((1.0 - share) * R[k] + share * R[k + 1])
    got = gp.response_at(radius, chi)
    lower, upper = gr.interpolate(s[k], chi), gr.interpolate(s[k + 1], chi)
    assert np.allclose(got, (1.0 - share) * lower + share * upper, rtol=1e-13, atol=0.0)
    assert np.all(got >= np.minimum(lower, upper) * (1.0 - 1e-15)) and np.all(got <= np.maximum(lower, upper) * (1.0 + 1e-15))
    # The whole contrast at that point, written out: its own taper, its own winding phase, its own bar term.
    phi = chi + 3.0
    taper, phase, bar_angle = pt.bar_terms(np.array([radius]), gp.pitch_deg, gp.bar_length)
    by_hand = (1.0 - taper[0]) * gp.response_at(radius, phi - phase[0]) + taper[0] * (1.0 + gp.bar * np.cos(2.0 * (phi - bar_angle)))
    assert np.allclose(gp.contrast_at(np.full_like(phi, radius), phi), by_hand, rtol=1e-13, atol=0.0)
    # Beyond the grid: the end rings, held.
    assert gp.response_at(0.0, chi).tobytes() == gr.interpolate(s[0], chi).tobytes()
    assert gp.response_at(99.0, chi).tobytes() == gr.interpolate(s[-1], chi).tobytes()
    # A point's mean round its ring is 1 at any radius: both blends are convex blends of mean-1 profiles.
    dense = (np.arange(14400) + 0.5) * (2.0 * math.pi / 14400)
    for radius in (2.03, 6.511, 8.3, 11.99):
        ring = gp.contrast_at(np.full_like(dense, radius), dense)
        assert float(ring.mean()) == pytest.approx(1.0, abs=1e-12) and ring.min() > 0.0


def test_azimuths_fall_inside_the_sector_and_follow_the_arms(model):
    gp = shape_of(model, out(model))
    u = np.random.default_rng(0).random(20000)
    radius = np.full(u.size, 8.0)
    phi = gp.azimuths(u, radius, 0.0, 2.0 * np.pi, steps=720)
    assert np.all((phi >= 0.0) & (phi <= 2.0 * np.pi))
    # Drawn by the contrast, the clouds sit where it is high: their mean contrast is the ring's mean square, well
    # above 1 — to sampling noise, about 0.5 %.
    ring = np.linspace(0.0, 2.0 * np.pi, 36000, endpoint=False)
    mean_square = float((gp.contrast_at(np.full_like(ring, 8.0), ring) ** 2).mean())
    # S57 (D216): was 1.253 at 12 kpc, the ranked ridge of the six-armed mode alone at half the arm amplitude. The
    # response there is weak (1.021: the crest 1.20); read at 8 kpc instead, where the arms are whole.
    assert mean_square == pytest.approx(1.358, abs=0.005)
    assert float(gp.contrast_at(radius, phi).mean()) == pytest.approx(mean_square, rel=0.02)


def test_the_default_field_s_range_and_its_mean_square(model):
    """The default galaxy's published field as read: its range; at R₀ the crest and the trough; and ⟨g²⟩ - the
    factor a process quadratic in the gas gains from the arms - at R₀ and by gas mass over the disc."""
    o = out(model)
    F, R = o.fields, o.grid.R
    g = np.asarray(F["gas_density_contrast"])
    # S57 (D216): was (0.5336, 3.0688), the ranked ridge's form; the response empties the gaps between the arms.
    # S57 (D216 G3): was (0.01992, 3.09294), the centre samples; the cells' means read (0.01994, 3.09222).
    assert (float(g.min()), float(g.max())) == pytest.approx((0.019943, 3.092221), abs=2e-5)
    i = row(o, R_SUN)
    # S57 (D216): was crest 3.0592, trough 0.5340 at R0. S57 (D216 G3): was (2.7403, 0.02534) on the centre samples.
    assert (float(g[i].max()), float(g[i].min())) == pytest.approx((2.73964, 0.025373), abs=2e-5)
    # S57 (D216): was 1.603 at R0 and 1.194 by gas mass. S57 (D216 G3): was 1.3443 and 1.1157 on the centre samples.
    assert float((g[i] ** 2).mean()) == pytest.approx(1.34398, abs=2e-5)
    weight = np.asarray(F["gas_surface_density"]) * R
    assert float(((g**2).mean(axis=1) * weight).sum() / weight.sum()) == pytest.approx(1.11562, abs=2e-5)


# --- what the stage reads, where it sits ---------------------------------------------------------------------


def test_the_stage_reads_no_gas_and_sits_at_checkpoint_three():
    assert GAS_PATTERN.checkpoint == 3 == PATTERN.checkpoint
    # No gas column and no gas ratio: nothing it requires is a gas field.
    assert [n for n in GAS_PATTERN.requires if "gas" in n] == []
    # S57 (D216): was ("gas_arm_contrast", "arm_contrast", *PATTERN_READS). The response reads the stellar modes,
    # their phases, the arm amplitude the taper is taken back out with, and checkpoint 1's disc - and no arm number.
    assert GAS_PATTERN.requires == GAS_PATTERN_READS == ("arm_contrast", *pt.PATTERN_READS, "epicyclic_frequency", "disc_surface_density")
    assert "arm_multiplicity" not in GAS_PATTERN.requires
    assert set(pt.AMPLITUDE_FIELDS) | set(pt.PHASE_FIELDS) <= set(GAS_PATTERN.requires)
    assert GAS_PATTERN.reads_seeds == ()
    assert {d.name for d in GAS_PATTERN.publishes} == {"gas_density_contrast"}
    about = GAS_PATTERN.publishes[0].about
    assert "the mean over its azimuthal cell" in about and "the offset is zero for a lone mode" in about


def test_both_models_run_the_gas_pattern_after_the_pattern(model):
    slots = [slot for slot, _ in model.stages]
    assert dict(model.stages)["gas_pattern"] == "gas_pattern"
    assert slots.index("gas_pattern") == slots.index("pattern") + 1


def test_a_flat_pattern_publishes_ones_and_a_ring_with_no_mode_is_one():
    assert one_mode(4, bar=float("nan"), pitch=float("nan")).flat
    assert one_mode(4, phases=(float("nan"),) * 5).flat   # the layer did not realise the phases
    assert one_mode(4, strength=0.0).flat                 # no mode and no bar
    assert one_mode(4, arm=0.0).flat                      # no arm amplitude and no bar
    assert not one_mode(4).flat
    assert not one_mode(4, strength=0.0, bar=0.3).flat    # the bar's term alone
    # A ring that carries no mode: s = 1 exactly, the solver is not asked, and the field there is the bar's own.
    grid = DEFAULT.build()
    R, phi, edges = grid.R, grid.phi, grid["phi"].edges
    unit = np.zeros((5, R.size))
    unit[2, R < 10.0] = 1.0
    gp = synthetic(unit, bar=0.3)
    assert np.array_equal(gp.carries, R < 10.0) and np.all(gp.profiles[R >= 10.0] == 1.0)
    assert gp.diagnostics.steps.size == int((R < 10.0).sum())
    field = gp.contrast(R, phi)
    taper, _, bar_angle = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    beyond = R >= 10.0
    assert np.array_equal(field[beyond], (1.0 - taper[beyond, None]) + taper[beyond, None] * (1.0 + 0.3 * np.cos(2.0 * (phi[None, :] - bar_angle))))
    # ... and its cell means there are the bar's own term averaged over each cell: 1 to 1e-14 at 10 kpc and beyond.
    means = gp.cell_means(R, edges)
    bar = (np.sin(2.0 * (edges[1:] - bar_angle)) - np.sin(2.0 * (edges[:-1] - bar_angle))) / (2.0 * np.diff(edges))
    assert np.array_equal(means[beyond], (1.0 - taper[beyond, None]) + taper[beyond, None] * (1.0 + 0.3 * bar[None, :]))
    assert np.all(np.isnan(gp.arm_ratio(1.5)[beyond])) and np.all(np.isnan(gp.arm_width()[beyond]))
    bar_only = one_mode(4, strength=0.0, bar=0.3)
    assert bar_only.diagnostics is None and np.all(bar_only.profiles == 1.0)
    with pytest.raises(ValueError, match="5 modes"):
        synthetic(unit[:3])
    with pytest.raises(ValueError, match="epicyclic frequency and surface density"):
        GasPattern(R, unit, (0.0,) * 5, 0.4, 0.0, 13.5, 5.2, np.ones(3), np.ones(R.size), G_HAND, SOUND_SPEED_HAND)
    # Fields that hold no pattern give none.
    assert GasPattern.from_fields({"bar_contrast": 0.3}, R, {"G": G_HAND, "GAS_DISPERSION": 6.0}) is None


def test_the_two_weights_sum_to_one_or_the_composition_is_refused():
    """D216 item 8: "w_arm + w_bar = 1 asserted". (1 − t) + t is 1 in doubles to one unit in the last place; a
    taper that is not a number or outside [0, 1] is refused, not composed."""
    taper = np.concatenate([[0.0, 1.0, 0.5, 1e-300, 1.0 - 1e-16], np.random.default_rng(2).random(1000)])
    w_arm, w_bar = gm.blend_weights(taper)
    assert np.array_equal(w_bar, taper) and np.array_equal(w_arm, 1.0 - taper)
    assert float(np.abs(w_arm + w_bar - 1.0).max()) <= np.finfo(float).eps
    for bad in (np.array([0.2, np.nan]), np.array([1.5]), np.array([-0.1])):
        with pytest.raises(ArithmeticError, match="do not sum to 1"):
            gm.blend_weights(bad)


def test_one_solve_per_pattern_and_the_cache_changes_no_bit(prod):
    """The pattern solves its rings once, the first time a profile is asked for. Several stages of a run build the
    same pattern, so the last few solutions are kept under a digest of what was solved; a solution from the cache
    is the one a fresh solve makes, bit for bit - with the cache, without it, and ring by ring alone."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, "milky_way")
    c = constants(model)
    R, phi, edges = o.grid.R, o.grid.phi, o.grid["phi"].edges
    gm.forget_solutions()
    first = compose.gas_pattern(o.fields, R, c)
    cold = first.profiles
    assert len(gm._SOLUTIONS) == 1 and first.profiles is cold  # kept on the object: no second solve, no second look-up
    second = compose.gas_pattern(o.fields, R, c)
    assert second.profiles.tobytes() == cold.tobytes() and len(gm._SOLUTIONS) == 1
    assert second.contrast(R, phi).tobytes() == first.contrast(R, phi).tobytes()
    assert second.cell_means(R, edges).tobytes() == first.cell_means(R, edges).tobytes()
    # Without the cache, and one ring at a time: the same bits (the solver gives a ring the same arithmetic alone
    # as in any batch).
    f, eps, carries = first.forcing_amplitudes(), first.epsilon(), first.carries
    fresh, diagnostics = gm.respond(f[carries], first.phases, eps[carries], cache=False)
    assert fresh.tobytes() == cold[carries].tobytes() and len(gm._SOLUTIONS) == 1
    assert np.array_equal(diagnostics.steps, first.diagnostics.steps) and np.array_equal(diagnostics.floor, first.diagnostics.floor)
    for i in np.flatnonzero(carries)[[0, 37, 90, -1]]:
        alone, _ = gm.respond(f[i:i + 1], first.phases, eps[i:i + 1], cache=False)
        assert alone[0].tobytes() == cold[i].tobytes()
    # The cache is bounded, and another pattern does not get this one's rings.
    for seed in range(1, gm.SOLUTIONS_KEPT + 3):
        other = run(model, {"texture_seed": seed}, only=GAS_PATTERN_READS)
        assert compose.gas_pattern(other.fields, R, c).profiles.tobytes() != cold.tobytes()
    assert len(gm._SOLUTIONS) == gm.SOLUTIONS_KEPT == 4
    again = compose.gas_pattern(o.fields, R, c)
    assert again.profiles.tobytes() == cold.tobytes()
    gm.forget_solutions()
    assert len(gm._SOLUTIONS) == 0
