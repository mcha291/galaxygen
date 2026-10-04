"""The gas's own arm pattern: since S57 the gas's steady response to the stellar arms (BUILD_III Phase P2; D216).

From S51 to S56 this file held a ridge to its form: a von Mises of a measured width, its amplitude solved from a
measured ratio of means, since S56 laid round each ring by rank. Gate G2 of S57 retired the ridge for a law -
``ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m)`` on every ring, solved by ``gas_response`` (the instrument;
``tests/test_gas_response.py`` certifies it) - and this file holds the model to that law and to nothing of the
ridge. What is tested, in the gate's order:

- **the gate**, on every ring of both templates and of the 240 seeded galaxies the suite draws: the discrete
  residual, the ring's mean on the solver's cells with no division, positivity and the bound w_bar (1 − B), the
  grid field's sampled mean, Newton's counts, finiteness, the sector means;
- **the law re-derived by hand** on three rings from the published fields, with a dense Newton and a spectral
  derivative written here, and the bar's composition on a ring inside its reach;
- **the two interpolation errors**, in χ and in R, pinned as measured;
- **the predictions** of D216, read before they are judged (B4), with the as-built numbers;
- **the disclosed check** (not an acceptance row; invariant I3 stands): the ratio of means in the source's mask
  against PHANGS's 2.73 within 1.37-5.79, and the crest's width against 0.17 - layer on, both templates.

**Read on 2026-10-04, the Milky Way template at its default seeds** (165 rings carry a mode; `ngc_4414`: 133):
Newton 8 steps at most and one halving (9 and none); the residual 5.3e-12 (9.0e-12); the ring mean on the
solver's cells off 1 by 8.8e-14 (9.6e-14); the grid field's sampled ring mean off 1 by 7.1e-14 (9.5e-14) on the
default grid with nothing divided; s between 4.5e-11 and 5.70 (1.8e-17 and 4.73), both extremes deep inside the
bar where the arm's weight is under 1 %; the published field between 0.0199 and 3.093 (0.0142 and 2.689), its
margin over w_bar (1 − B) 9.2e-6 (1.3e-6). At R₀ the crest is 2.74 and the trough 0.025 (S56's ridge: 3.06 and
0.534): the gas between the arms is nearly emptied where the modes' forcing sums past 1, as the gate predicted.

**Not as the gate expected, recorded and not mended** (B5): (i) two of the 240 seeded galaxies - `ngc_4414` at
pattern seed 33, either texture seed - draw a pitch of 1.78 degrees, and the solver cannot converge five of their
inner rings (residual stalled at 1.0-1.3e-10 against the 1e-10 tolerance: its rounding floor at ε ≈ 1), so the
model raises for them, as ruled, and the test pins that it does; (ii) the interpolation in χ is off by up to
3.5e-4 at the cells' midpoints outside the bar's reach and 1.2e-3 inside it (3.0e-4 of the published field), not
the 2.0e-4 the two hard rings of the instrument's tests read; (iii) with several modes the gas's crest is within
a degree of the stellar crest, not on it to the cell.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy import templates
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt
from galaxy.stages.gas_pattern import GAS_CHECK_CONSTANTS, GAS_PATTERN, GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS, GasPattern
from galaxy.stages.pattern import BAR, PATTERN

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
TEMPLATES = ("milky_way", "ngc_4414")
R_SUN = 8.122
G_HAND = 4.30091727e-6  # kpc (km/s)^2 / Msun, written here; the model's constant is held to it
SOUND_SPEED_HAND = 6.0  # km/s, written here; the model's GAS_DISPERSION is held to it
MASK_WIDTH_HAND = 1.5   # kpc: PHANGS's median mask width (the check's definition)
WIDTH_TARGET = 0.17     # the measured gas arm's full width at half maximum over its period (the width's target)
RATIO_TARGET, RATIO_LOW, RATIO_HIGH = 2.73, 1.37, 5.79  # PHANGS's grand designs: the mean and its 16th-84th percentiles
PATTERN_FIELDS = ("gas_density_contrast", "pattern_density_contrast", "gas_arm_contrast", "arm_pattern_speed",
                  "circular_velocity", *GAS_PATTERN_READS)
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


# --- a redistribution, not a source ----------------------------------------------------------------------------


def test_the_gas_contrast_averages_to_one_around_every_ring(model):
    """Positive, finite, and mean 1 round every ring of the published field - with nothing divided: the sampled
    mean of the grid's 360 cells is the law's own, 1 to 1e-13."""
    o = out(model)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert g.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(g > 0.0) and np.all(np.isfinite(g))
    assert float(np.abs(g.mean(axis=1) - 1.0).max()) < 1e-12
    assert not np.all(g == 1.0)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_grid_field_is_the_law_at_the_cells_centres_and_is_never_divided(prod, template):
    """D216 item 11 (i): "the new field is never divided by a sampled mean; the model grid's sampled mean is
    asserted against a pinned tolerance (measure it, expected far under 1e-6)".

    The published field is the pattern's point function at the grid's cell centres, bit for bit - so no step
    stands between the law and the field, a division least of all. **Measured on the default grid: the sampled
    ring mean is off 1 by 7.1e-14 at worst for the Milky Way template and 9.5e-14 for ``ngc_4414``** - rounding:
    the solver's 1440 cells are four to each of the grid's 360, so a ring's cells sample the linear interpolant
    at one place between two solver cells and what is left is the response's harmonics from the 360th up. Pinned
    under 5e-13. **On a coarse φ grid it is not rounding**: 36 cells alias the response's 36th harmonic (the
    sixth of a six-armed mode) and the sampled mean leaves 1 by 1.3e-3 (1.1e-3) - from S51 to S56 the stage
    divided that out; it no longer does, and the number is pinned as it is."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    R, phi = o.grid.R, o.grid.phi
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    assert g.tobytes() == gp.contrast(R, phi).tobytes()
    assert g.tobytes() == gp.contrast_at(R[:, None], phi[None, :]).tobytes()
    assert float(np.abs(g.mean(axis=1) - 1.0).max()) < 5e-13
    # The module holds no tolerance to renormalise by, and its source does not divide a field by a mean.
    assert not hasattr(gm, "RING_MEAN_TOLERANCE")
    source = (Path(gm.__file__)).read_text(encoding="utf-8")
    assert ".mean(" not in source
    coarse = run(model, templates.overrides(templates.TEMPLATES[template]), SMALL, only=("gas_density_contrast",))
    small = np.asarray(coarse.fields["gas_density_contrast"])
    assert np.all(small > 0.0)
    assert float(np.abs(small.mean(axis=1) - 1.0).max()) == pytest.approx({"milky_way": 1.257e-3, "ngc_4414": 1.056e-3}[template], rel=0.02)


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
    assert worst < 2e-7  # measured 4e-8: the midpoint rule's, not the means'
    # Thirty-two sectors, unequal ones, and a ring past the last mode and the bar: every sector exactly 1.
    uneven = np.concatenate([[0.0], np.sort(np.random.default_rng(5).uniform(0.0, 2.0 * np.pi, 31)), [2.0 * np.pi]])
    means = gp.sector_means(8.0, uneven)
    assert float((means * np.diff(uneven)).sum() / (2.0 * np.pi)) == pytest.approx(1.0, abs=1e-12)
    assert np.all(gp.sector_means(20.0, edges) == 1.0)


# --- the gate ----------------------------------------------------------------------------------------------------


def gate(gp: GasPattern, phi: np.ndarray) -> dict[str, float]:
    """The gate's numbers for one pattern (D216, "the gate (every ring, every seed, both templates)"), each
    recomputed here from the profiles and not read off the solver's own report - but for Newton's counts and the
    residual, which is given both ways: ``residual`` is the solver's own, of ln s as it iterated it, and
    ``recomputed`` is the residual of the profile it returned, s, whose logarithm is taken again here. The two
    differ by the rounding of exp and log, which the equation multiplies by 2 ε²/h² (the solver's rounding floor)."""
    R = gp.R
    s, carries, d = gp.profiles, gp.carries, gp.diagnostics
    f, eps = gp.forcing_amplitudes(), gp.epsilon()
    forcing = gr.forcing(pt.ARM_MODES, f[carries], np.asarray(gp.phases))
    recomputed = float(np.abs(gr.residual(s[carries], forcing, eps[carries])).max())
    assert np.all(s[~carries] == 1.0)  # a ring with no mode has s = 1
    taper, _, _ = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    law = gp.contrast(R, phi)
    assert np.all(np.isfinite(s)) and np.all(np.isfinite(law))
    return {
        "residual": float(d.worst_residual), "recomputed": recomputed,
        "mean": float(np.abs(s.sum(axis=1) / s.shape[1] - 1.0).max()),
        "min_s": float(s.min()), "max_s": float(s.max()),
        "margin": float((law - (taper * (1.0 - gp.bar))[:, None]).min()),  # min g − w_bar (1 − B), ring by ring
        "sampled": float(np.abs(law.sum(axis=1) / law.shape[1] - 1.0).max()),
        "steps": float(d.worst_steps), "halvings": float(d.worst_halvings),
        "max_g": float(law.max()), "min_g": float(law.min()),
    }


@pytest.mark.parametrize("template", TEMPLATES)
def test_gate_every_ring_of_both_templates(prod, template):
    """The gate at each template's own seeds, on every ring, with the numbers as read (the module docstring)."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, template)
    gp = shape_of(model, o)
    got = gate(gp, o.grid.phi)
    want = {
        "milky_way": dict(rings=165, steps=8, halvings=1, min_s=4.50e-11, max_s=5.6975, min_g=0.019924, max_g=3.09294),
        "ngc_4414": dict(rings=133, steps=9, halvings=0, min_s=1.81e-17, max_s=4.7322, min_g=0.014249, max_g=2.68897),
    }[template]
    assert int(gp.carries.sum()) == want["rings"]
    assert got["residual"] < gr.RESIDUAL_TOLERANCE == 1e-10          # measured 5.3e-12 and 9.0e-12
    assert got["recomputed"] < 1e-10                                 # and of the returned profile, recomputed here
    assert got["mean"] < 1e-12                                       # measured 8.8e-14 and 9.6e-14, nothing divided
    assert got["min_s"] > 0.0 and got["margin"] >= 0.0               # nothing clipped: the law's own positivity
    assert got["sampled"] < 5e-13                                    # measured 7.1e-14 and 9.5e-14
    assert (got["steps"], got["halvings"]) == (want["steps"], want["halvings"])
    assert got["steps"] <= gr.MAX_NEWTON_STEPS == 120 and got["halvings"] <= gr.MAX_HALVINGS == 30
    assert got["min_s"] == pytest.approx(want["min_s"], rel=0.02) and got["max_s"] == pytest.approx(want["max_s"], abs=2e-4)
    assert (got["min_g"], got["max_g"]) == pytest.approx((want["min_g"], want["max_g"]), abs=2e-5)
    # The bound of D216 item 12, [w_bar (1 − B), max s]: the margin under it is small where the arm's weight is.
    assert 0.0 < got["margin"] < 2e-5 and got["max_g"] <= got["max_s"]
    assert not np.any(np.asarray(o.fields["gas_density_contrast"]) > 4.0)  # the declared ramp holds the field


def test_gate_every_ring_on_every_seed_the_suite_draws(prod):
    """The gate on the suite's seeds - sixty pattern seeds by two texture seeds for each template's inputs, the 240
    galaxies the stellar positivity test draws (``tests/test_modes.py``): on every ring the discrete residual under
    1e-10 on every cell; the ring's mean 1 to 1e-12 on the solver's cells with no division; min s > 0 and
    min g ≥ w_bar (1 − B) with nothing clipped; the grid field's sampled mean within its pinned tolerance; Newton's
    counts under the solver's maxima; finite everywhere; the sector means averaging to 1.

    **238 of the 240 meet it. Two do not, and are pinned as they fail (B5), for gate G3 to rule:** ``ngc_4414`` at
    pattern seed 33 (either texture seed) draws a pitch of 1.78 degrees, so ε = a/(κR sin p) is about 1 on its inner
    rings and the forcing's sum 60-80; the solver stalls there at a residual of 1.0-1.3e-10 - its rounding floor,
    2ε² ulp(ln s)/h², which the instrument's own docstring says "cannot converge in doubles and raises" - and
    raises ``ConvergenceError`` after its 120 steps. The model raises with it: there is no fallback (item 7) and
    none was added. (A sweep of 300 pattern seeds a template, outside this test: 5 and 13 galaxies raise, every one
    at a drawn pitch under 2.7 degrees.)"""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    edges = np.linspace(0.0, 2.0 * np.pi, 33)
    worst: dict[str, float] = {}
    raised: dict[tuple[str, int, int], tuple[float, int, float]] = {}
    relogged: dict[tuple[str, int, int], float] = {}
    met = 0
    for template in TEMPLATES:
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = {**templates.overrides(templates.TEMPLATES[template]), "pattern_seed": pattern_seed, "texture_seed": texture_seed}
                o = run(model, given, only=GAS_PATTERN_READS)
                gp = compose.gas_pattern(o.fields, o.grid.R, c)
                assert gp is not None and not gp.flat
                try:
                    got = gate(gp, o.grid.phi)
                except gr.ConvergenceError as error:
                    raised[(template, pattern_seed, texture_seed)] = (float(error.residual), int(error.steps), float(o.fields["pitch_angle"]))
                    continue
                label = (template, pattern_seed, texture_seed)
                assert got["residual"] < 1e-10, label
                if got["recomputed"] >= 1e-10:
                    relogged[label] = float(o.fields["pitch_angle"])
                assert got["mean"] < 1e-12, label
                assert got["min_s"] > 0.0 and got["margin"] >= 0.0, label
                assert got["sampled"] < 1e-12, label
                assert got["steps"] <= gr.MAX_NEWTON_STEPS and got["halvings"] <= gr.MAX_HALVINGS, label
                for radius in (3.0, 8.0):
                    assert float(gp.sector_means(radius, edges).mean()) == pytest.approx(1.0, abs=1e-12), label
                for key, value in got.items():
                    worst[key] = min(worst.get(key, value), value) if key in ("min_s", "margin", "min_g") else max(worst.get(key, value), value)
                met += 1
    assert met == 238 and set(raised) == {("ngc_4414", 33, 0), ("ngc_4414", 33, 1)}
    for residual, steps, pitch in raised.values():
        assert steps == gr.MAX_NEWTON_STEPS and 1.0e-10 <= residual < 1.5e-10 and pitch == pytest.approx(1.780, abs=2e-3)
    # The worst seen over the 238, recorded: Newton's counts (the maxima are 120 and 30); the residual, 9.7e-11
    # (``ngc_4414`` at pattern seed 1, pitch 2.06 degrees: just under the tolerance, on the same rounding floor
    # the two failures sit just over); the ring mean 1.0e-13; the sampled grid mean 2.5e-13; s from 2.4e-44 to
    # 14.39; the published field from 0.0017 to 6.78 (above the declared ramp's 4 on seeds that draw a strong arm
    # or a low pitch; under it at both templates' own seeds); its margin over w_bar (1 − B) 3.0e-9 at the least.
    assert (worst["steps"], worst["halvings"]) == (11, 2)
    assert 5e-11 < worst["residual"] < 1e-10 and worst["mean"] < 2e-13 and worst["sampled"] < 5e-13
    assert 0.0 < worst["min_s"] < 1e-40 and worst["max_s"] == pytest.approx(14.39, abs=0.02)
    assert worst["margin"] >= 0.0 and worst["min_g"] == pytest.approx(1.68e-3, rel=0.02) and worst["max_g"] == pytest.approx(6.78, abs=0.01)
    # **The same floor, seen in the profiles that did converge**: the solver holds its residual under 1e-10 in
    # ln s as it iterated it; the residual of the profile it returns, s, with the logarithm taken again, passes
    # 1e-10 on a few galaxies - seven as read, 4.4e-10 at worst, every one at a drawn pitch of 2.1 degrees or less
    # (ε of order 1, where exp and log's rounding times 2 ε²/h² is that large). Recorded for G3 with the failures.
    assert 1e-10 < worst["recomputed"] < 1e-9
    assert 1 <= len(relogged) <= 12 and max(relogged.values()) < 2.1 and {k[:2] for k in relogged} <= {
        ("milky_way", 22), ("milky_way", 33), ("ngc_4414", 1), ("ngc_4414", 22)}


# --- the law, re-derived by hand ---------------------------------------------------------------------------------


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
    published field is held to the composition g = w_arm s + w_bar (1 + B cos 2(φ − φ_bar)) written out here; at
    4 kpc, inside the bar's reach, the bar's term carries 0.70 of the weight. The spectral residual of the
    differential equation reads 4.8e-4, 9.1e-5 and 3.8e-5 on the three rings: the cells' second-order error."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert c["G"] == pytest.approx(G_HAND, rel=1e-9) and c["GAS_DISPERSION"] == SOUND_SPEED_HAND
    o = template_run(prod, "milky_way")
    F, R, phi = o.fields, o.grid.R, o.grid.phi
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
        # Road one: the dense Newton on the same cells.
        by_hand, steps = hand_newton(forcing, eps)
        model_ring = gp.profiles[i]
        assert steps <= 12 and float(np.abs(model_ring - by_hand).max()) < 1e-9, (radius, steps, float(np.abs(model_ring - by_hand).max()))
        assert float(np.abs(model_ring / by_hand - 1.0).max()) < 1e-8, radius  # in the trough too, where s is 1e-6
        assert abs(float(model_ring.sum()) / n - 1.0) < 1e-12 and model_ring.min() > 0.0
        # Road two: the differential equation, ε² (ln s)″ = s − 1 − g, the second derivative taken spectrally. What
        # is left is the cells' second-order error, ε² h²/12 max|(ln s)⁗|, against terms of order 1: pinned as read.
        log_s = np.log(model_ring)
        k = np.fft.rfftfreq(n, d=1.0 / n)
        second = np.fft.irfft(-(k**2) * np.fft.rfft(log_s), n=n)
        ode = eps**2 * second - (model_ring - 1.0 - forcing)
        assert float(np.abs(ode).max()) == pytest.approx(ode_want, rel=0.03), (radius, float(np.abs(ode).max()))
        # The composition, at the grid's own cells: the hand's ring read at each cell's χ, linear between two cell
        # centres, weighed by 1 − taper, and the bar's own term by the taper.
        winding, bar_angle = math.log(Ri) / math.tan(pitch), math.log(a_bar) / math.tan(pitch)
        place = (phi - winding + math.pi) / h - 0.5
        lower = np.floor(place).astype(int)
        share = place - lower
        ring = (1.0 - share) * by_hand[lower % n] + share * by_hand[(lower + 1) % n]
        composed = (1.0 - taper) * ring + taper * (1.0 + B * np.cos(2.0 * (phi - bar_angle)))
        assert float(np.abs(published[i] - composed).max()) < 1e-9, radius
        assert published[i].min() >= taper * (1.0 - B)
    # Inside the bar's reach the two terms are both there: at 4 kpc the bar carries 0.70 of the weight.
    i = row(o, 4.0125)
    assert float(published[i].max()) == pytest.approx(2.0112, abs=2e-3) and float(published[i].min()) == pytest.approx(0.5010, abs=2e-3)


def test_one_weak_mode_is_the_linear_response_and_sits_on_the_stellar_crest():
    """Two anchors on a made-up disc, with the arithmetic written here. A weak mode's response is the linear one,
    s − 1 = f/(1 + m² ε²) cos(mχ − θ) - so f and ε reach the solver as the law writes them, sign and phase
    included. And **no offset** (D210 ruling 3, D216 item 12: "offset zero by symmetry"): one mode's response is
    even about the mode's crest, so the gas's crest is the stellar crest, at any amplitude."""
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


def test_the_gas_s_crest_is_within_a_degree_of_the_stellar_crest(prod):
    """D216's prediction "offset 0 on every ring", read on the default galaxy's several modes: **held to a degree,
    not to the cell**. One mode's response is even about its crest (the test above). A ring of several modes is
    not one mode: the gas answers each mode with its own weight, m/(1 + m² ε²) against the stars' 1, so the two
    sums need not peak in the same cell - at 7 and 8 kpc they peak one cell (a degree) apart; at 6, 9, 10, 11 and
    12 kpc in the same cell. No offset is put in and none is published."""
    o = template_run(prod, "milky_way")
    g, s = np.asarray(o.fields["gas_density_contrast"]), np.asarray(o.fields["pattern_density_contrast"])
    n = o.grid.phi.size
    apart = []
    for radius in (6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0):
        i = row(o, radius)
        d = abs(int(g[i].argmax()) - int(s[i].argmax()))
        apart.append(min(d, n - d))
    assert apart == [0, 1, 1, 0, 0, 0, 0]


# --- the interpolation, in χ and in R (D216 item 9: "measured and pinned") ---------------------------------------


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
    """**In χ, at the cells' midpoints** (the worst place: h²/8 · max|s″|). The instrument's two hard rings read
    1.96e-4 and 1.54e-4, and the gate ruled 1440 cells on that ("the expected order"). **The model's rings read
    more, and are pinned as they are (B5): 3.5e-4 at worst outside the bar's reach for the Milky Way template
    (9.2e-5 for ``ngc_4414`` beyond 6 kpc), and 1.2e-3 on s deep inside the bar** - where the untapered forcing
    sums to 4-6 and the crest stands at 4-5.7 - **which is 3.0e-4 (2.9e-4) of the published field**, the arm's
    weight there being under 1 %. The cell count is the ruling's and is not touched.

    **In R, midway between two grid rings**, against a ring solved there with the law's inputs linear in R
    between the two rings (the amplitudes as ``ArmPattern`` reads them, κ and Σ alike): the blend of the two
    neighbours at the same χ is off by 5.7e-4 (7.9e-4) of the published field at worst, its median 8e-5 (1.7e-4);
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
    want = {"milky_way": (1.240e-3, 2.963e-4, 3.486e-4), "ngc_4414": (1.210e-3, 2.886e-4, 9.232e-5)}[template]
    got = (float(error.max()), float((error * (1.0 - taper)).max()), float(error[R > 6.0].max()))
    assert got == pytest.approx(want, rel=0.01), got
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

        R kpc     predicted: crest / trough / ratio     as built, s: crest / trough / ratio     as built, g: crest / trough
        4.0125    1.91 / 0.37  / 1.57                   4.170 / 4.5e-7 / 3.811                  2.011 / 0.501
        5.9625    3.02 / 0.007 / 2.69                   3.480 / 2.5e-4 / 3.208                  3.010 / 0.128
        7.9875    2.79 / 0.018 / 2.56                   2.797 / 0.0171 / 2.571                  2.787 / 0.0220
        10.0125   2.09 / 0.18  / 2.04                   2.090 / 0.1819 / 2.037                  2.089 / 0.1822
        10.9875   1.77 / 0.38  / 1.89                   1.765 / 0.3845 / 1.886                  1.765 / 0.3845
        12.0375   1.20 / 0.81  / 1.28                   1.198 / 0.8114 / 1.281                  1.198 / 0.8116

    **Held** at 10, 11 and 12 kpc, to the figures given. **Held at R₀ to the taper's share**: the taper is 0.0040
    at 7.99 kpc, the untapered forcing 0.4 % stronger, and the crest and the ratio stand 0.3-0.4 % above the
    probe's (the trough 5 % under: 0.0171 against 0.018). **Not held inside the bar's reach, as foreseen**: at 4
    and 6 kpc s answers the untapered forcing (its sum 3.7 and 2.8, against the probe's 1.1 and 2.3) and is far
    stronger than the probe's; the published field there is s at 0.30 and 0.82 of the weight with the bar's own
    term. Nothing was changed to make a number hold.

    Also read: "interarm nearly empty where the forcing's sum exceeds 1 (6-8 kpc)" - held, the trough of s
    2.9e-4 to 0.017 there; "Newton at most 8 steps here" - held, 8; "34 on ``ngc_4414``" - the probe's own Newton;
    the instrument takes 9."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert c["GAS_ARM_MASK_WIDTH"] == MASK_WIDTH_HAND
    o = template_run(prod, "milky_way")
    R = o.grid.R
    g = np.asarray(o.fields["gas_density_contrast"])
    gp = shape_of(model, o)
    s, ratio = gp.profiles, gp.arm_ratio(MASK_WIDTH_HAND)
    f_sum = gp.forcing_amplitudes().sum(axis=1)
    table = (
        # R, predicted (crest, trough, ratio), as built s (crest, trough, ratio), as built g (crest, trough), held
        (4.0125, (1.91, 0.37, 1.57), (4.1701, 4.48e-7, 3.8106), (2.0112, 0.5010), False),
        (5.9625, (3.02, 0.007, 2.69), (3.4796, 2.54e-4, 3.2080), (3.0096, 0.1282), False),
        (7.9875, (2.79, 0.018, 2.56), (2.7967, 0.0171, 2.5705), (2.7874, 0.0220), True),
        (10.0125, (2.09, 0.18, 2.04), (2.0896, 0.1819, 2.0375), (2.0892, 0.1822), True),
        (10.9875, (1.77, 0.38, 1.89), (1.7648, 0.3845, 1.8857), (1.7646, 0.3845), True),
        (12.0375, (1.20, 0.81, 1.28), (1.1984, 0.8114, 1.2812), (1.1982, 0.8116), True),
    )
    for radius, predicted, built, composed, held in table:
        i = row(o, radius)
        assert float(R[i]) == pytest.approx(radius, abs=1e-9)
        got = (float(s[i].max()), float(s[i].min()), float(ratio[i]))
        assert got[0] == pytest.approx(built[0], abs=2e-3) and got[2] == pytest.approx(built[2], abs=2e-3), radius
        assert got[1] == pytest.approx(built[1], rel=0.03), radius
        assert (float(g[i].max()), float(g[i].min())) == pytest.approx(composed, abs=2e-3), radius
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
    defined, so it cannot be a blind test. The definitions are the ruling's, fixed before the build's numbers.

    *The ratio of means*: the mean of s inside the source's arm mask - the share m_eff W/(2π R sin p) of the ring,
    at most a half, where the stellar modes' sum is highest (S56's mask) - over its mean outside, against PHANGS's
    2.73 within its 16th-84th percentiles 1.37-5.79. **As read: the Milky Way template's median over 6-10 kpc is
    2.571, inside - a hit, disclosed - and every one of its 53 rings is inside (2.052 to 3.192). ``ngc_4414``'s
    median is 1.881, inside; 46 of its 53 rings are inside and the 7 outermost, where its arms fade (9.49 to
    9.94 kpc), fall under 1.37, down to 1.076.** Nothing was tuned to land it.

    *The width*: the full width at half maximum of the ring's tallest crest, the half level midway between the
    ring's trough and crest, over the period 2π/m of the ring's strongest mode, against the measured 0.17.
    **As read: a miss on every ring of both templates, as predicted (0.23-0.48): 0.211 to 0.481, median 0.311,
    for the Milky Way template - 1.24 to 2.83 times the measured width (the prediction's low end was 0.23: the
    narrowest ring, at 6.04 kpc, answers the untapered forcing) - and 0.262 to 0.508, median 0.422, for
    ``ngc_4414``, 1.54 to 2.99 times.** Its two named suspects (D216, "Honesty"): the steady pressure-balanced response in place of the
    simulations' converging infall, and the razor-thin forcing of the five- and six-armed modes."""
    model = prod[0].get(DEFAULT_MODEL)
    c = constants(model)
    assert (c["GAS_ARM_MASK_WIDTH"], c["GAS_ARM_WIDTH"]) == (MASK_WIDTH_HAND, WIDTH_TARGET)
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    assert float(F["gas_arm_contrast"]) == pytest.approx(RATIO_TARGET, abs=1e-12)  # the target, and no stage's input
    gp = shape_of(model, o)
    band = (R >= 6.0) & (R <= 10.0) & gp.carries
    ratio, width = gp.arm_ratio(MASK_WIDTH_HAND)[band], gp.arm_width()[band]
    want = {
        "milky_way": dict(rings=53, ratio=(2.5705, 2.0523, 3.1921), inside=53, width=(0.3107, 0.2114, 0.4807)),
        "ngc_4414": dict(rings=53, ratio=(1.8814, 1.0762, 2.8299), inside=46, width=(0.4218, 0.2620, 0.5083)),
    }[template]
    assert int(band.sum()) == want["rings"]
    assert (float(np.median(ratio)), float(ratio.min()), float(ratio.max())) == pytest.approx(want["ratio"], abs=2e-3)
    assert (float(np.median(width)), float(width.min()), float(width.max())) == pytest.approx(want["width"], abs=2e-3)
    # The verdicts, as read: the median ratio inside PHANGS's percentiles (a hit, disclosed) ...
    assert RATIO_LOW <= float(np.median(ratio)) <= RATIO_HIGH
    assert int(((ratio >= RATIO_LOW) & (ratio <= RATIO_HIGH)).sum()) == want["inside"] and np.all(ratio <= RATIO_HIGH)
    # ... and the width a miss on every ring: wider than the measured arm, by 1.2 to 3.0 times.
    assert np.all(width > WIDTH_TARGET) and 1.2 < float(width.min()) / WIDTH_TARGET and float(width.max()) / WIDTH_TARGET < 3.0

    # The two measurements, re-made here on one ring by this file's arithmetic (a sort and a walk), from the
    # published amplitudes and phases: the module's helpers are these.
    i = row(o, 8.0)
    amplitudes = np.array([float(np.asarray(F[n])[i]) for n in pt.AMPLITUDE_FIELDS])
    phases = np.array([float(F[n]) for n in pt.PHASE_FIELDS])
    modes = np.arange(2.0, 7.0)
    chi = -math.pi + (np.arange(1440) + 0.5) * (2.0 * math.pi / 1440)
    psi = (amplitudes[:, None] * np.cos(modes[:, None] * chi[None, :] - phases[:, None])).sum(axis=0)
    m_eff = float((modes * amplitudes**2).sum() / (amplitudes**2).sum())
    share = min(0.5, m_eff * MASK_WIDTH_HAND / (2.0 * math.pi * float(R[i]) * math.sin(math.radians(float(F["pitch_angle"])))))
    s = gp.profiles[i]
    order = np.argsort(-psi, kind="stable")
    inside = int(round(share * s.size))
    by_hand = float(s[order[:inside]].mean() / s[order[inside:]].mean())
    assert float(gp.arm_ratio(MASK_WIDTH_HAND)[i]) == pytest.approx(by_hand, rel=2e-3)  # a whole cell at the cut, against a share of it
    half = 0.5 * (float(s.max()) + float(s.min()))
    crest = int(np.argmax(s))
    ahead = next(k for k in range(1, s.size) if s[(crest + k) % s.size] <= half)
    behind = next(k for k in range(1, s.size) if s[(crest - k) % s.size] <= half)
    strongest = float(modes[int(np.argmax(amplitudes))])  # the largest amplitude; the lower arm number on a tie
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


def test_nothing_of_the_ridge_builds_the_field(prod):
    """D216 item 11 (iv): "nothing replaces the amplitude: s is the field; ``gas_arm_contrast`` and S56's mask
    survive only as [the check's] target and definition; ``GAS_ARM_WIDTH`` only as the width miss's target". The
    pattern is built from fields and constants that hold none of the three; no stage requires the ratio; the
    stage declares the check's two constants (a constant must have a stage: preflight) and its module's code
    names them once, in that declaration; and the retired machinery is gone from the module."""
    models, impls_, _ = prod
    model = models.get(DEFAULT_MODEL)
    assert GAS_PATTERN_CONSTANTS == ("G", "GAS_DISPERSION") and GAS_CHECK_CONSTANTS == ("GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH")
    assert GAS_PATTERN.reads_constants == (*GAS_PATTERN_CONSTANTS, *GAS_CHECK_CONSTANTS)
    assert "gas_arm_contrast" not in GAS_PATTERN_READS and not set(GAS_CHECK_CONSTANTS) & set(GAS_PATTERN_CONSTANTS)
    for m in models:
        readers = [sid for _, sid in m.stages if "gas_arm_contrast" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [], readers
        declaring = sorted(sid for _, sid in m.stages if set(GAS_CHECK_CONSTANTS) & set(impls_.get(sid).reads_constants))
        assert declaring == ["gas_pattern"], declaring
    # The pattern from fields and the law's two constants alone is the pattern from all of them: the same bits.
    o = template_run(prod, "milky_way")
    R, phi = o.grid.R, o.grid.phi
    c = constants(model)
    lean = compose.gas_pattern(o.fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS})
    assert lean.contrast(R, phi).tobytes() == np.asarray(o.fields["gas_density_contrast"]).tobytes()
    fields = {n: o.fields[n] for n in GAS_PATTERN_READS}
    assert GasPattern.from_fields(fields, R, {k: c[k] for k in GAS_PATTERN_CONSTANTS}).contrast(R, phi).tobytes() == lean.contrast(R, phi).tobytes()
    assert GasPattern.from_fields(fields, R, {"G": c["G"]}) is None  # a constant the law reads is missing: no pattern
    # The module's code (docstrings apart) names each of the check's constants once: in the declaration.
    tree = ast.parse(Path(gm.__file__).read_text(encoding="utf-8"))
    docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body
                  and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings]
    for name in (*GAS_CHECK_CONSTANTS, "gas_arm_contrast"):
        assert sum(1 for text in strings if name in text) == (1 if name in GAS_CHECK_CONSTANTS else 0), name
    for retired in ("_Rings", "ridge_value", "kappa_for_width", "mask_means", "pattern_period", "PHASE_CELLS",
                    "HARMONIC_SAMPLES", "RING_MEAN_TOLERANCE", "NEWTON_STEPS", "BISECTION_STEPS"):
        assert not hasattr(gm, retired), retired
    for retired in ("rank", "ridge", "amplitude", "ratio_at", "forcing", "extremes", "ratio", "width", "mask_width"):
        assert not hasattr(GasPattern, retired), retired
    # Forbidden forms (D216), held by what the code does, read from the syntax tree: nothing is clipped, no error is
    # caught (so no fallback on a ring that did not converge), and no string names an arm number.
    assert [n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "clip"] == []
    assert not any(isinstance(n, (ast.Try, ast.ExceptHandler)) for n in ast.walk(tree))
    assert not any("arm_multiplicity" in text for text in strings)
    # And nothing reads the frame's field: the flow is 0 by construction, not a difference of two speeds. The one
    # call of the solver hands it the constant 0 as the flow.
    for m in models:
        readers = [sid for _, sid in m.stages if "arm_pattern_speed" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [] and "arm_pattern_speed" in impls_.get("bar").published_names
    assert not any("arm_pattern_speed" in text for text in strings)
    solves = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "solve"]
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


def test_contrast_at_agrees_with_the_grid(model):
    o = out(model)
    gp = shape_of(model, o)
    R, phi = o.grid.R, o.grid.phi
    on_grid = gp.contrast(R, phi)
    assert on_grid.tobytes() == np.asarray(o.fields["gas_density_contrast"]).tobytes()  # S57: the samples themselves
    idx = np.array([5, 77, 190, 399]), np.array([0, 91, 180, 359])
    assert np.array_equal(gp.contrast_at(R[idx[0]], phi[idx[1]]), on_grid[idx])
    # Points that share a radius unevenly: each is the single point's value.
    radii = np.concatenate([np.full(7, R[100]), np.full(3, R[150])])
    azimuths = np.linspace(0.3, 5.9, 10)
    alone = np.array([gp.contrast_at(np.array([r]), np.array([p]))[0] for r, p in zip(radii, azimuths)])
    assert np.array_equal(gp.contrast_at(radii, azimuths), alone)


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
    """The default galaxy's field as read: its range; at R₀ the crest and the trough; and ⟨g²⟩ - the factor a
    process quadratic in the gas gains from the arms - at R₀ and by gas mass over the disc."""
    o = out(model)
    F, R = o.fields, o.grid.R
    g = np.asarray(F["gas_density_contrast"])
    # S57 (D216): was (0.5336, 3.0688), the ranked ridge's form; the response empties the gaps between the arms.
    assert (float(g.min()), float(g.max())) == pytest.approx((0.01992, 3.09294), abs=2e-4)
    i = row(o, R_SUN)
    # S57 (D216): was crest 3.0592, trough 0.5340 at R0.
    assert (float(g[i].max()), float(g[i].min())) == pytest.approx((2.7403, 0.02534), abs=2e-3)
    # S57 (D216): was 1.603 at R0 and 1.194 by gas mass.
    assert float((g[i] ** 2).mean()) == pytest.approx(1.3443, abs=3e-3)
    weight = np.asarray(F["gas_surface_density"]) * R
    assert float(((g**2).mean(axis=1) * weight).sum() / weight.sum()) == pytest.approx(1.1157, abs=3e-3)


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
    R = DEFAULT.build().R
    unit = np.zeros((5, R.size))
    unit[2, R < 10.0] = 1.0
    gp = synthetic(unit, bar=0.3)
    assert np.array_equal(gp.carries, R < 10.0) and np.all(gp.profiles[R >= 10.0] == 1.0)
    assert gp.diagnostics.steps.size == int((R < 10.0).sum())
    phi = DEFAULT.build().phi
    field = gp.contrast(R, phi)
    taper, _, bar_angle = pt.bar_terms(R, gp.pitch_deg, gp.bar_length)
    beyond = R >= 10.0
    assert np.array_equal(field[beyond], (1.0 - taper[beyond, None]) + taper[beyond, None] * (1.0 + 0.3 * np.cos(2.0 * (phi[None, :] - bar_angle))))
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


def test_a_ring_the_solver_cannot_converge_raises_and_nothing_catches_it(prod):
    """D216 item 7: "a ring that fails to converge within the counts is a build failure (raise) ... there is no
    fallback and no linear substitute". Shown on the galaxy of the suite's seeds that does it (``ngc_4414`` at
    pattern seed 33: a drawn pitch of 1.78 degrees): asking the pattern for a profile, a point or a sector raises
    the solver's own error, and the stage raises it with the run."""
    model = prod[0].get(DEFAULT_MODEL)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "pattern_seed": 33}
    o = run(model, given, only=GAS_PATTERN_READS)
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert not gp.flat and float(o.fields["pitch_angle"]) == pytest.approx(1.780, abs=2e-3)
    with pytest.raises(gr.ConvergenceError, match="Newton did not converge"):
        gp.profiles
    with pytest.raises(gr.ConvergenceError):
        gp.contrast_at(np.array([8.0]), np.array([1.0]))
    with pytest.raises(gr.ConvergenceError):
        gp.sector_means(8.0, np.linspace(0.0, 2.0 * np.pi, 5))
    with pytest.raises(gr.ConvergenceError):
        run(model, given, only=("gas_density_contrast",))
    # Why: ε is of order 1 on the inner rings at that pitch (0.07-0.09 at the template's own 14.3 degrees) and the
    # forcing's sum 60-80, where the solver's rounding floor passes its tolerance.
    eps, f = gp.epsilon(), gp.forcing_amplitudes()
    inner = o.grid.R < 1.0
    assert float(eps[inner].min()) == pytest.approx(0.7035, abs=1e-3) and float(f[inner].sum(axis=1).max()) == pytest.approx(79.06, abs=0.05)
    # With the layer off there is no pattern to solve, and the galaxy runs.
    off = run(model, given, only=("gas_density_contrast",), layer=False)
    assert np.all(np.asarray(off.fields["gas_density_contrast"]) == 1.0)


def test_one_solve_per_pattern_and_the_cache_changes_no_bit(prod):
    """The pattern solves its rings once, the first time a profile is asked for. Several stages of a run build the
    same pattern, so the last few solutions are kept under a digest of what was solved; a solution from the cache
    is the one a fresh solve makes, bit for bit - with the cache, without it, and ring by ring alone."""
    model = prod[0].get(DEFAULT_MODEL)
    o = template_run(prod, "milky_way")
    c = constants(model)
    R, phi = o.grid.R, o.grid.phi
    gm.forget_solutions()
    first = compose.gas_pattern(o.fields, R, c)
    cold = first.profiles
    assert len(gm._SOLUTIONS) == 1 and first.profiles is cold  # kept on the object: no second solve, no second look-up
    second = compose.gas_pattern(o.fields, R, c)
    assert second.profiles.tobytes() == cold.tobytes() and len(gm._SOLUTIONS) == 1
    assert second.contrast(R, phi).tobytes() == first.contrast(R, phi).tobytes()
    # Without the cache, and one ring at a time: the same bits (the solver gives a ring the same arithmetic alone
    # as in any batch).
    f, eps, carries = first.forcing_amplitudes(), first.epsilon(), first.carries
    fresh, diagnostics = gm.respond(f[carries], first.phases, eps[carries], cache=False)
    assert fresh.tobytes() == cold[carries].tobytes() and len(gm._SOLUTIONS) == 1
    assert np.array_equal(diagnostics.steps, first.diagnostics.steps)
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
