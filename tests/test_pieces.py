"""The arms as a census of pieces (S60, BUILD_III Phase P5; DECISIONS.md D219).

Until S60 the stellar arms were five cosine modes with drawn phases on one winding (cut into seeded segments at
S59). The owner ruled them a census of arm pieces, and a conditional gate ruled the rest (D219, nine items, its
predictions, its gate, what is forbidden; the lead's readings (a)-(d) where the ruling leaves a choice). This
file holds the build to it:

- **a piece on a ring, by hand** - one Gaussian ridge: its mean, its ring variance, its Fourier terms and its
  forcing, derived here and held against the modules;
- **the thickness factor** - ½ at k h = 1, and the forcing bounded by ĉ_m R/(X h) on every ring of the gate's
  galaxies;
- **the census** - a chain laid by this file's own loop from the texture seed's streams, the births' count, a
  flocculent disc's single pieces, the Milky Way's pinned loci and their continuation;
- **the gate** on the 360 galaxies of S59's three legs: ring means, the budget in expectation and the realised
  power's scatter, positivity by the saturation alone, no bit of a law moving with the layer, the gas converging;
- **the layer off** - no row, every composed field its neutral value (the comparison of every field with ``main``,
  bit for bit, is the builder's and is recorded in D219);
- **the gas between rings** - the carried profile against a direct solve at mid-gap radii, both templates;
- **the gate's predictions, as measured**, each recorded held or not held; nothing was changed to make one hold;
- **the m-split** - the composed field's Fourier power by arm number beside the law's, a disclosed check;
- **the pinned loci** on the stellar pieces by construction, and **the masers' loci against the gas's and the young
  stars' crests**, a disclosed check read against its null (``tests/reid2019.py``);
- **the pins** - a class of three and a table, by D217's mechanism - and what S59's file held that still applies:
  the numeric pins, the table kind, the young stars' reader.

**What of ``tests/test_segments.py`` came here and what went** is at the foot of this docstring's list in D219's
record; in short: the pins' tests, the table kind's and the reader's are ported onto the new pattern; the winding's
own tests (its rows, its knots, its continuity, its segment statistics, its door) are deleted with the winding.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import gas_check
import reid2019
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import TABLES, FieldDecl, Kind
from galaxy.core.grids import GridSpec
from galaxy.core.registry import ARM_CLASSES, INPUTS, Input, RegistryError
from galaxy.layer import arm_pieces as ap
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.specs import graph
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt
from galaxy.stages import pieces as pc
from galaxy.stages import systems

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
COMPOSED = tuple(d.name for d in pc.COMPOSED)
PATTERN = (*COMPOSED, "gas_density_contrast", "star_formation_gas_contrast", *gm.GAS_PATTERN_READS, *pt.AMPLITUDE_FIELDS,
           "arm_class", "bar_present", "pitch_angle_drawn", "sun_azimuth", "arm_saturation", "arm_contrast")
READER = ("sfr_modulation", "gas_surface_density", "sf_threshold_surface_density", "sfr_surface_density", *PATTERN)
LAWS = (*pt.AMPLITUDE_FIELDS, "arm_power_budget", "arm_design_count", "arm_piece_width", "arm_saturation", "pitch_angle", "arm_class")
LEGS = ("milky_way", "ngc_4414", "ngc_4414 drawn")
# The scalars that are not numbers, as ruled: an unbarred galaxy's bar (D217 item 3, D164) and the Sun's azimuth
# without a bar or without the pin (D218 item 5). A barred, pinned galaxy has none.
UNBARRED_NAN = {"bar_half_length", "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_contrast", "bar_mass_share",
                "bar_corotation_radius", "bar_pattern_speed", "sun_azimuth"}
FWHM = 2.0 * math.sqrt(2.0 * math.log(2.0))
_RUNS: dict[object, object] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def inputs_of(template: str, **more) -> dict:
    return {**templates.overrides(templates.TEMPLATES[template]), **more}


def leg_inputs(leg: str, **more) -> dict:
    """S59's three legs: the two templates, and ``ngc_4414`` with its pitch pin taken off (its other pins kept)."""
    if leg == "ngc_4414 drawn":
        return {k: v for k, v in inputs_of("ngc_4414", **more).items() if k != "pitch_angle"}
    return inputs_of(leg, **more)


def template_run(prod, template: str, fields=READER, **more):
    key = (template, fields, tuple(sorted(more.items())))
    if key not in _RUNS:
        _RUNS[key] = run(the_model(prod), inputs_of(template, **more), only=fields)
    return _RUNS[key]


def patterns(prod, o):
    c = constants(the_model(prod))
    return compose.stellar_pattern(o.fields, o.grid.R), compose.gas_pattern(o.fields, o.grid.R, c), c


def misplaced(reader: np.ndarray, law: np.ndarray) -> np.ndarray:
    """The reviewer's statistic of S59, per radius: half the mean absolute difference of two azimuthal profiles,
    each over its own mean - the share of the ring's weight the one puts where the other does not."""
    a, b = reader / reader.mean(axis=1, keepdims=True), law / law.mean(axis=1, keepdims=True)
    return 0.5 * np.abs(a - b).mean(axis=1)


# --- the declarations ----------------------------------------------------------------------------------------------


def test_the_constants_are_the_ruling_s_and_the_stages_are_declared_as_ruled(prod):
    """D219 items 1-3, 5 and 7. The numbers are the ruling's; the census is the layer's, a table, synthetic, laid
    after the pattern stage; the composed fields are a composing stage's; the phases, the winding and
    ``arm_segment`` are gone, with the ``arm_phases`` stage."""
    model = the_model(prod)
    c = constants(model)
    assert (c["ARM_PIECE_WIDTH"], c["ARM_PIECE_WIDTH_ZERO_POINT"], c["ARM_PIECE_WIDTH_RADIUS"]) == (0.53, 0.27, 2.0)
    assert (c["ARM_CHAIN_LENGTH_GRAND_DESIGN"], c["ARM_CHAIN_LENGTH_GRAND_DESIGN_SCATTER"]) == (273.0, 143.0)
    assert (c["ARM_CHAIN_LENGTH_MULTI_ARMED"], c["ARM_CHAIN_LENGTH_MULTI_ARMED_SCATTER"], c["ARM_CHAIN_LENGTH_MIN"]) == (244.0, 131.0, 90.0)
    assert (c["ARM_PIECE_FLOCCULENT_EXTENT_MIN"], c["ARM_PIECE_FLOCCULENT_EXTENT_MAX"], c["ARM_LAYER_FLATTENING"]) == (37.0, 105.0, 7.3)
    assert (c["ARM_SEGMENT_EXTENT_MEDIAN"], c["ARM_SEGMENT_EXTENT_LOG_SCATTER"], c["ARM_SEGMENT_EXTENT_MIN"], c["ARM_SEGMENT_EXTENT_MAX"],
            c["ARM_SEGMENT_PITCH_RELATIVE_SCATTER"]) == (60.0, 0.35, 20.0, 180.0, 0.56)
    g = graph.analyse(model, prod[1], prod[2])
    assert g.ok, g.problems
    order = [s.id for s in g.order]
    assert "arm_phases" not in order and order.index("pattern") < order.index("arm_pieces") < min(order.index("stellar_pattern"), order.index("gas_pattern"))
    assert g.layer_stages == ("arm_pieces", "cloud_texture") and {"stellar_pattern", "gas_pattern"} <= set(g.composing_stages)
    assert "pattern" not in g.composing_stages  # the law's stage composes nothing since S60
    assert TABLES == ("arm_piece",)
    decls = {d.name: d for s in g.order for d in s.publishes}
    for name in pt.PIECE_FIELDS:
        d = decls[name]
        assert d.kind is Kind.TABLE_COLUMN and d.of == "arm_piece" and d.provenance == "synthetic" and d.stands_in_for and d.conserves and d.statistic
    for name in COMPOSED:
        assert decls[name].composed and decls[name].provenance == "seeded", name
    for name in LAWS:
        assert not decls[name].composed and decls[name].provenance != "synthetic", name
    gone = [n for n in decls if n.startswith(("arm_mode_phase", "arm_segment", "arm_winding"))]
    assert not gone and not hasattr(pt, "Winding") and decls["pattern_density_contrast"] is pc.DENSITY_CONTRAST
    assert decls["arm_class"].categories == ARM_CLASSES == ("grand_design", "multi_armed", "flocculent")
    # The width law: FWHM(R) = 0.53 h (0.27 + 0.73 R/(2h)), by hand on the default disc.
    o = run(model, None, only=("arm_piece_width", "disc_scale_length_spin"))
    h, R = float(o.fields["disc_scale_length_spin"]), o.grid.R
    assert np.allclose(o.fields["arm_piece_width"], 0.53 * h * (0.27 + 0.73 * R / (2.0 * h)), rtol=1e-14, atol=0.0)
    assert float(np.interp(8.15, R, o.fields["arm_piece_width"])) == pytest.approx(1.9494, abs=1e-4)


# --- a piece on a ring, by hand ------------------------------------------------------------------------------------


def test_the_wrapped_normal_its_mean_its_variance_and_its_depth():
    """A piece's profile round its ring: W(δ; σ) = Σ_k exp(−(δ + 2πk)²/2σ²), less its mean σ/√(2π). Held to this
    file's own sums: its three evaluations (two images, five images, six Fourier terms) are one function across
    the changes; its mean round the ring is 0; its variance is Σ c_m²/2 by both closed forms, and the ruling's
    σ/(2√π) − σ²/(2π) while the piece is narrower than its ring; its trough is at the antipode."""
    delta = np.linspace(-math.pi, math.pi, 2001)
    for sigma in (0.0822, 0.3, pc.NARROW, pc.NARROW + 1e-9, 1.0, pc.WIDE, pc.WIDE + 1e-9, 1.7724, 3.0, 6.0):
        by_images = sum(np.exp(-0.5 * ((delta + 2.0 * math.pi * k) / sigma) ** 2) for k in range(-40, 41)) - sigma / math.sqrt(2.0 * math.pi)
        got = pc.deviation(delta, np.full(delta.shape, sigma))
        assert np.abs(got - by_images).max() < 4e-15, sigma
        fine = pc.deviation((np.arange(20000) + 0.5) * (2.0 * math.pi / 20000), np.full(20000, sigma))
        assert abs(fine.mean()) < 1e-15 and float(pc.depth(np.array(sigma))) == pytest.approx(-fine.min(), abs=1e-7)
        c = (2.0 * sigma / math.sqrt(2.0 * math.pi)) * np.exp(-0.5 * (np.arange(1, 400) * sigma) ** 2)
        assert np.allclose(pc.harmonic_amplitudes(np.array(sigma)), c[: pc.HARMONICS], rtol=1e-13, atol=1e-300)
        assert float(pc.ring_variance(np.array(sigma))) == pytest.approx(0.5 * float((c**2).sum()), rel=2e-13)
        assert float((fine**2).mean()) == pytest.approx(0.5 * float((c**2).sum()), rel=1e-9)
    for sigma in (0.1, 0.3, 0.6):  # the ruling's expression, where the piece is narrow (the images' terms e^-27 and less)
        assert float(pc.ring_variance(np.array(sigma))) == pytest.approx(sigma / (2.0 * math.sqrt(math.pi)) - sigma**2 / (2.0 * math.pi), rel=1e-11)
    # ... which is no longer positive at sqrt(pi): the dispersion past which a ring carries no arm.
    assert pc.WIDEST == math.sqrt(math.pi) and pc.WIDEST / (2.0 * math.sqrt(math.pi)) - pc.WIDEST**2 / (2.0 * math.pi) == pytest.approx(0.0, abs=1e-16)
    assert np.array_equal(pc.budget_amplitude(np.full(3, 0.1), np.full(3, 4.0), np.array([1.0, pc.WIDEST, 5.0])) > 0.0, [True, False, False])
    # The narrowest piece the width law allows keeps harmonic 128 far under the first.
    assert float(pc.harmonic_amplitudes(np.array(0.0822))[-1] / pc.harmonic_amplitudes(np.array(0.0822))[0]) < 1e-23


def hand_pattern(sigma: float = 0.3, budget: float = 0.02, count: float = 1.0):
    """One arm piece on a disc of this file's making: pitch 20 degrees, from 2 kpc round 4 radians, its width
    such that it lies with dispersion ``sigma`` on the ring at 5 kpc. No bar. Returns the patterns and the ring."""
    R = np.linspace(1.0, 20.0, 77)
    i = 16
    assert R[i] == 5.0
    pitch = 20.0
    width = np.full(R.size, sigma * FWHM * 5.0 * math.sin(math.radians(pitch)))
    pieces = pc.Pieces(np.array([0.0]), np.array([0.0]), np.array([2.0]), np.array([0.3]), np.array([pitch]), np.array([4.0]), np.array([0.0]), turn=1.0)
    stars = pc.ArmPattern(R, np.full(R.size, budget), np.full(R.size, count), width, pieces, float("nan"), pitch, float("nan"))
    kappa, density = 60.0 / np.sqrt(R), 80.0 * np.exp(-R / 3.0)
    gas = gm.GasPattern(R, stars, pitch, float("nan"), kappa, density, 4.3e-6, 8.0, 0.4)
    return R, i, stars, gas, kappa, density


def test_one_ridge_on_one_ring_by_hand():
    """**Derived here, independently of the modules.** One Gaussian ridge of height B and azimuthal dispersion σ
    on a ring, narrow against the ring: its mean round the ring is Bσ/√(2π), so the field is
    1 + B(e^{−δ²/2σ²} − σ/√(2π)); its ring variance is B²σ/(2√π) − (Bσ)²/(2π) (the ruling's own arithmetic);
    its m-th Fourier amplitude is (2Bσ/√(2π)) e^{−m²σ²/2}; the budget's amplitude for one piece is
    B = √(budget/(σ/(2√π) − σ²/(2π))); and the gas's forcing has the m-th amplitude
    c_m · m/(X (sin p + m h/R)), X = κ²R/(2πGΣ), all crests on the ridge. σ = 0.3 on the ring at 5 kpc."""
    sigma, budget = 0.3, 0.02
    R, i, stars, gas, kappa, density = hand_pattern(sigma, budget)
    r = 5.0
    v = sigma / (2.0 * math.sqrt(math.pi)) - sigma**2 / (2.0 * math.pi)
    B = math.sqrt(budget / v)
    crest = 0.3 + math.log(r / 2.0) / math.tan(math.radians(20.0))  # where the locus crosses the ring
    assert float(stars.amplitude_at(np.array([r]))[0]) == pytest.approx(B, rel=1e-12)
    assert float(stars.saturation(np.array([r]))[0]) == 1.0  # B sigma / sqrt(2 pi) = 0.059: far from the mean
    mean = B * sigma / math.sqrt(2.0 * math.pi)
    for delta in (0.0, 0.2, -0.5, 1.3, math.pi):
        want = 1.0 + B * math.exp(-0.5 * (delta / sigma) ** 2) - mean
        assert float(stars.contrast_at(np.array([r]), np.array([crest + delta]))[0]) == pytest.approx(want, abs=1e-14)
    power, by_mode = stars.ring_power(np.array([r]))
    assert float(power[0]) == pytest.approx(B * B * v, rel=1e-12) and float(power[0]) == pytest.approx(budget, rel=1e-12)
    c = [(2.0 * B * sigma / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * (m * sigma) ** 2) for m in range(1, 129)]
    assert by_mode[:, 0] == pytest.approx([c[m - 1] ** 2 for m in pt.ARM_MODES], rel=1e-12)
    edges = np.linspace(0.0, 2.0 * math.pi, 361)
    cells = stars.sector_means(r, edges)
    assert abs(cells.mean() - 1.0) < 1e-15 and np.array_equal(cells, stars.published(np.array([r]), None, edges)[0])
    samples = (edges[:-1, None] + (edges[1] - edges[0]) * ((np.arange(200) + 0.5) / 200.0)[None, :])
    assert np.abs(cells - stars.contrast_at(np.array([[r]]), samples).mean(axis=1)).max() < 2e-7  # the midpoint rule's own error
    # The forcing: X by hand, the piece's own pitch, the layer's thickness.
    x = float(kappa[i]) ** 2 * r / (2.0 * math.pi * 4.3e-6 * float(density[i]) * 1.0e6)
    sin_p, h = math.sin(math.radians(20.0)), 0.4
    f = [c[m - 1] * m / (x * (sin_p + m * h / r)) for m in range(1, 129)]
    assert np.allclose(gas.forcing_amplitudes()[i], f, rtol=1e-11, atol=1e-300)
    on_cells = gas.forcing()[i]
    chi = gr.cell_centres(gr.CELLS)
    by_hand = sum(f[m - 1] * np.cos(m * (chi - crest)) for m in range(1, 129))
    assert np.abs(on_cells - by_hand).max() < 1e-13 and abs(on_cells.mean()) < 1e-15
    # ... each term the razor-thin m c_m/(X sin p) times 1/(1 + k h), k = m/(R sin p).
    for m in (1, 2, 6, 40):
        assert f[m - 1] == pytest.approx(c[m - 1] * m / (x * sin_p) / (1.0 + m * h / (r * sin_p)), rel=1e-13)
    # The gas answers it: mean 1, a crest on the ridge, by the solver.
    s = gas.profiles[i]
    assert abs(s.mean() - 1.0) < 1e-12 and abs(float(chi[int(np.argmax(s))]) - (crest - 2.0 * math.pi * round(crest / (2.0 * math.pi)))) < 2.0 * math.pi / gr.CELLS


def test_the_thickness_factor_by_hand():
    """D219 item 5: "the thickness factor per harmonic turns f_m into |m| ĉ_m/(X(|sin p| + |m| h/R)), bounded by
    ĉ_m R/(X h) for every m and pitch, regular at sin p = 0"; the gate: "T = ½ at kh = 1"."""
    for m, sin_p in ((2.0, 0.2), (5.0, 0.05), (1.0, 1.0)):
        h_over_r = sin_p / m  # k h = m h / (R sin p) = 1
        assert float(pc.thickness_factor(m, sin_p, h_over_r)) == pytest.approx(0.5, rel=1e-15)
        assert float(pc.forcing_factor(m, 3.0, sin_p, h_over_r)) == pytest.approx(0.5 * m / (3.0 * sin_p), rel=1e-15)
    m = np.arange(1.0, 129.0)
    for sin_p in (0.0, 1e-12, 0.0175, 0.24, -0.5, 1.0):
        f = pc.forcing_factor(m, 2.5, sin_p, 0.04)
        assert np.all(np.isfinite(f)) and np.all(f <= 1.0 / (2.5 * 0.04) * (1.0 + 1e-15))
    assert float(pc.forcing_factor(4.0, 2.5, 0.0, 0.04)) == pytest.approx(1.0 / (2.5 * 0.04), rel=1e-15)  # the bound, met at sin p = 0
    assert float(pc.thickness_factor(3.0, 0.3, 0.0)) == 1.0  # a razor-thin layer: D216's forcing


# --- the census ----------------------------------------------------------------------------------------------------


def hand_chain(seed: int, chain: int, x: float, azimuth: float, pitch: float, mean: float, sd: float, x_edge: float):
    """A chain laid by this file's own loop from the texture seed's streams: (start radius, start azimuth, pitch,
    extent) per piece, and the drawn length in radians."""
    def stream(*path):
        return _seeds.rng(seed, "arm_pieces", "chain", chain, *path)

    g = stream("length")
    length = float(g.normal(mean, sd))
    while length < 90.0:
        length = float(g.normal(mean, sd))
    left, rows, k = math.radians(length), [], 0
    while left > 0.0 and x <= x_edge:
        g = stream("out", k)
        z = float(g.normal())
        extent = 60.0 * math.exp(0.35 * float(g.normal()))
        while not 20.0 <= extent <= 180.0:
            extent = 60.0 * math.exp(0.35 * float(g.normal()))
        extent = min(math.radians(extent), left)
        p = pitch * (1.0 + 0.56 * z)
        rows.append((math.exp(x), azimuth % (2.0 * math.pi), p, extent))
        t = math.tan(math.radians(p))
        x, azimuth, left, k = x + extent * abs(t), azimuth + extent * (1.0 if t > 0.0 else -1.0), left - extent, k + 1
    return rows, math.radians(length)


def table_of(F) -> np.ndarray:
    return np.stack([np.asarray(F[n], dtype=float) for n in pt.PIECE_FIELDS], axis=1)


def test_the_census_by_hand_a_barred_disc_s_chains(prod):
    """D219 items 2-3 on the bare default galaxy (barred, no pin: a grand design). Chains 0 and 1 start at the
    bar's two ends - R = a, φ_bar and φ_bar + π - and are this file's own laying of the streams' draws, to the
    bit of every row: a piece's deviate first, then its extent (drawn again outside 20°-180°), its pitch
    p(1 + 0.56 z), the chain's length a normal of 273° ± 143° drawn again under 90°, the last piece cut to it.
    Then the births: every ring with a budget is crossed by at least the law's arm number of chains, and no
    chain was started where enough already crossed."""
    model = the_model(prod)
    o = run(model, {"texture_seed": 7}, only=PATTERN)
    F, R = o.fields, o.grid.R
    assert F["arm_class"] == "grand_design" and F["bar_present"] == "yes"
    a, pitch = float(F["bar_half_length"]), float(F["pitch_angle"])
    bar_angle = math.log(a) / math.tan(math.radians(pitch))
    rows = table_of(F)
    assert rows.shape[1] == 7 and np.all(rows[:, 6] == 0.0)
    for chain, end in ((0, 0.0), (1, math.pi)):
        mine, length = hand_chain(7, chain, math.log(a), bar_angle + end, pitch, 273.0, 143.0, math.log(R[-1]))
        theirs = rows[rows[:, 0] == chain]
        assert np.array_equal(theirs[:, 1], np.arange(len(mine)))
        assert np.allclose(theirs[:, 2:6], np.array(mine), rtol=1e-13, atol=1e-13), chain
        assert float(theirs[0, 2]) == pytest.approx(a, rel=1e-15)
        # The last piece is cut to the chain's drawn length - unless the chain left the grid first.
        left_the_grid = mine[-1][0] * math.exp(mine[-1][3] * abs(math.tan(math.radians(mine[-1][2])))) > R[-1]
        assert left_the_grid or float(theirs[:, 5].sum()) == pytest.approx(length, rel=1e-13)
    sp = compose.stellar_pattern(F, R)
    count, design, budget = np.asarray(F["arm_chain_count"]), np.asarray(F["arm_design_count"]), np.asarray(F["arm_power_budget"])
    has = budget > 0.0
    assert np.all(count[has] >= design[has]) and np.all(design[has] >= 2.0) and np.all(design[~has] == 0.0)
    assert np.array_equal(count, sp.pieces.chains_crossing(R))
    # A birth happens only where fewer chains cross than the law counts: each born chain's first ring held, without
    # it and the later-born, fewer than the law's number.
    starts = {int(ch): float(r) for ch, order, r in zip(rows[:, 0], rows[:, 1], rows[:, 2]) if order == 0.0}
    spans = {int(ch): (float(rows[rows[:, 0] == ch][:, 2].min()),
                       float((rows[rows[:, 0] == ch][:, 2] * np.exp(rows[rows[:, 0] == ch][:, 5] * np.abs(np.tan(np.radians(rows[rows[:, 0] == ch][:, 4]))))).max()))
             for ch in np.unique(rows[:, 0])}
    for chain, r in starts.items():
        if chain < 2:
            continue
        i = int(np.argmin(np.abs(R - r)))
        assert R[i] == pytest.approx(r, rel=1e-14)
        earlier = sum(1 for ch, (lo, hi) in spans.items() if ch < chain and lo <= R[i] < hi)
        assert earlier < design[i], (chain, r)
    # The table is what the stage says it is: by chain, inside out along each.
    assert np.all(np.diff(rows[:, 0]) >= 0.0)
    for chain in np.unique(rows[:, 0]):
        part = rows[rows[:, 0] == chain]
        assert np.array_equal(part[:, 1], np.arange(part.shape[0])) and np.all(np.diff(part[:, 2]) >= 0.0)
    # Pieces of a drawn chain are joined end to start.
    for chain in (0, 1, 5):
        part = rows[rows[:, 0] == chain]
        t = np.tan(np.radians(part[:, 4]))
        end_r, end_phi = part[:, 2] * np.exp(part[:, 5] * np.abs(t)), part[:, 3] + part[:, 5] * np.sign(t)
        assert np.allclose(end_r[:-1], part[1:, 2], rtol=1e-12) and np.allclose(np.mod(end_phi[:-1] - part[1:, 3] + math.pi, 2.0 * math.pi), math.pi, atol=1e-12)


def test_a_flocculent_disc_is_single_pieces_and_an_unbarred_one_has_no_chain_from_a_bar(prod):
    """D219 item 3. ``ngc_4414`` is pinned flocculent: every chain is one piece, its extent inside 37°-105°, and
    at least the law's number cross every ring with a budget. With the class pin taken off the same unbarred
    galaxy is multi-armed: chains of several pieces, their length drawn about 244°, and no chain starts at a
    bar's end (there is none). The pin moves no law."""
    model = the_model(prod)
    floc = run(model, inputs_of("ngc_4414"), only=PATTERN)
    multi = run(model, {k: v for k, v in inputs_of("ngc_4414").items() if k != "arm_class"}, only=PATTERN)
    assert floc.fields["arm_class"] == "flocculent" and multi.fields["arm_class"] == "multi_armed" and floc.fields["bar_present"] == "no"
    rows = table_of(floc.fields)
    assert np.all(rows[:, 1] == 0.0) and len(np.unique(rows[:, 0])) == rows.shape[0] == 36
    extent = np.degrees(rows[:, 5])
    assert 37.0 <= extent.min() and extent.max() <= 105.0 and (round(float(extent.min()), 1), round(float(extent.max()), 1)) == (37.7, 103.6)
    has = np.asarray(floc.fields["arm_power_budget"]) > 0.0
    assert np.all(np.asarray(floc.fields["arm_chain_count"])[has] >= np.asarray(floc.fields["arm_design_count"])[has])
    other = table_of(multi.fields)
    pieces_per_chain = np.bincount(other[:, 0].astype(int))
    assert pieces_per_chain.max() > 3 and other.shape[0] > rows.shape[0]
    for name in LAWS:
        if name != "arm_class":
            assert np.asarray(floc.fields[name]).tobytes() == np.asarray(multi.fields[name]).tobytes(), name


def test_the_milky_way_s_pinned_pieces_lie_on_the_measured_loci_and_are_continued_by_drawn_ones(prod):
    """D219 item 8 and the lead's reading (c). Each pinned row of Reid et al. 2019's Table 2 is a chain of its
    fitted pieces - two where its two pitches differ, one for the Local arm - **exactly on the fitted locus**
    over its β range (asserted to 1e-12: by construction, not a test of the model), the Sun at β = 0 by the
    pinned bar angle. Each is continued by drawn pieces flagged unpinned: outward past its low-β end, and inward
    past its high-β end as far as the bar's half-length (none where that end is already inside the bar). The
    3 kpc arm is not entered, and no chain starts at the bar's ends."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp, _, _ = patterns(prod, o)
    rows = table_of(F)
    sun, a = float(F["sun_azimuth"]), float(F["bar_half_length"])
    sense = pt.rotation_sense(float(F["pitch_angle"]))
    assert sense == -1.0 and F["arm_class"] == "grand_design"
    table = {row[0]: row for row in reid2019.TABLE2}
    assert reid2019.PINNED == ("Norma", "Sct-Cen", "Sgr-Car", "Local", "Perseus", "Outer") and "3-kpc(N)" not in reid2019.PINNED
    p = sp.pieces
    worst = 0.0
    for chain, name in enumerate(reid2019.PINNED):
        part = rows[rows[:, 0] == chain]
        pinned = part[part[:, 6] == 1.0]
        _, lo, hi, kink, r_kink, below, above = table[name]
        assert pinned.shape[0] == (1 if below == above else 2), name
        assert sorted(pinned[:, 4].tolist()) == sorted({below, above}) and float(pinned[:, 5].sum()) == pytest.approx(math.radians(hi - lo), rel=1e-14)
        # The locus by the source's formula against the model's own piece, at every degree of the range.
        beta, radius = reid2019.locus(table[name])
        phi = sun + sense * np.radians(beta)
        for b, r, f in zip(beta, radius, phi):
            pitch = below if b <= kink else above
            k = int(np.flatnonzero((p.chain == chain) & (p.pinned == 1.0) & (p.pitch_deg == pitch))[0])
            share = (math.log(r) - p.x_start[k]) / (p.x_end[k] - p.x_start[k])
            on_piece = p.phi_start[k] + share * (p.phi_end[k] - p.phi_start[k])
            assert -1e-9 <= share <= 1.0 + 1e-9
            worst = max(worst, abs(math.remainder(on_piece - f, 2.0 * math.pi)) * r)
        drawn = part[part[:, 6] == 0.0]
        inner_end = r_kink * math.exp(-math.radians(hi - kink) * math.tan(math.radians(above)))
        inward = drawn[drawn[:, 2] < min(pinned[:, 2].min(), inner_end) - 1e-9]
        if inner_end <= a:
            assert inward.shape[0] == 0, name  # the measured end is inside the bar: nothing is laid inward
        else:
            assert inward.shape[0] == 0 or float(inward[:, 2].min()) >= a * (1.0 - 1e-12), name
    assert worst < 1e-12  # kpc: the pinned pieces are the fitted loci
    # No chain is tied to the bar: none starts at (a, the bar's angle) or its opposite.
    bar_angle = sp.bar_angle
    at_bar = [r for r in rows if abs(r[2] - a) < 1e-9 and min(abs(math.remainder(r[3] - bar_angle, math.pi)), 1.0) < 1e-9 and r[1] == 0.0]
    assert not at_bar
    record = (rows.shape[0], len(np.unique(rows[:, 0])), int(rows[:, 6].sum()),
              [int((rows[(rows[:, 0] == c)][:, 6] == 0.0).sum()) for c in range(6)])
    # (pieces, chains, pinned pieces, the drawn pieces that continue each of the six pinned chains)
    assert record == (137, 26, 11, [2, 1, 3, 2, 4, 4]), record
    # A galaxy whose arms are pinned needs the Sun: without the bar's angle to it, or without a bar, it is refused.
    pins = templates.pinned(templates.TEMPLATES["milky_way"])
    for missing in ("sun_bar_angle", "bar_present"):
        given = {k: v for k, v in pins.items() if k != missing} | ({"bar_present": False} if missing == "bar_present" else {})
        with pytest.raises(ValueError, match="placed by the Sun's azimuth"):
            run(the_model(prod), given, SMALL, only=("arm_piece_chain",))


# --- the gate ------------------------------------------------------------------------------------------------------


def test_gate_on_the_three_legs_of_the_suite_s_galaxies(prod):
    """D219's gate: "Ring means 1 to 1e-12 on cells; expected ring power = budget to 1e-10 by the analytic
    expectation, the realised power per ring published and its scatter pinned; min ≥ 0 on every suite seed by the
    saturation only, the cut counted; ... the gas converges under D216's criterion or raises; ... f_m ≤ ĉ_m R/(X h)
    on every ring and seed".

    **S59's three legs, 60 pattern seeds × 2 texture seeds each** - the Milky Way template (barred, its arms
    pinned), ``ngc_4414`` (unbarred, flocculent, its pitch pinned) and ``ngc_4414`` with its pitch pin off. On
    every one of the 360: nothing raises (so every ring converged); the stellar and the gas ring means are 1;
    the stellar field is nowhere negative **with nothing but the cut** and the gas positive; no bit of a law
    moves with the layer; no field holds a NaN but the ruled ones; N v(σ_d) B² is the budget wherever a ring
    has an amplitude; and every harmonic of the forcing is under the bound.

    **As read** (the record below). Ring means: stars 1.6e-15, gas 1.0e-13 at worst; N v B² against the budget
    1.6e-15. **The realised power is about half the budget in the median ring**: over the rings that have an
    amplitude its 16th / 50th / 84th percentiles are 0.20 / 0.44 / 0.87 of the budget on the Milky Way's leg,
    0.40 / 0.55 / 1.08 on ``ngc_4414``'s and 0.27 / 0.52 / 0.98 on the drawn-pitch leg - the scatter the gate asks
    to be pinned, and a shortfall the expectation does not have: the expectation is of the law's count of pieces
    at the disc's pitch and at full height, and a realised piece is faded over one width at each of its ends
    (each piece's own taper, as ruled: a chain's pieces are both at zero where they join), lies wider or
    narrower on its ring by its own pitch, and overlaps its neighbours. Read, not mended: nothing is divided by a
    realised power. **Rings cut**: 6, 0 and 11 of 19 800, 15 960 and 15 960 with a budget. **Rings with a budget
    and no amplitude** - the designed piece wider than its ring, no arm, counted: 2 080, 240 and 1 584; **six
    galaxies of each drawn-pitch leg hold no arm at all** (a pitch under about 3 degrees: an arm as wide as the
    width law makes it is then wider than every ring that has a budget). **None with a budget and no chain** (the lead's reading
    (d): counted, 0). The stellar field is nowhere under 0.11 and has no exact zero; the gas runs from 0.022 to
    6.68; no ring took more than 7 Newton steps."""
    model = the_model(prod)
    c = constants(model)
    worst = {"stars": 0.0, "gas": 0.0, "expected": 0.0, "bound": 0.0}
    read = {leg: {"ratio": [], "cut": 0, "no_arm": 0, "no_chain": 0, "least": math.inf, "least_gas": math.inf, "most_gas": 0.0, "zeros": 0,
                  "budget": 0, "pitch": [], "steps": 0, "armless": 0} for leg in LEGS}
    for leg in LEGS:
        got = read[leg]
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = leg_inputs(leg, pattern_seed=pattern_seed, texture_seed=texture_seed)
                o = run(model, given, only=PATTERN)
                F, R = o.fields, o.grid.R
                label = (leg, pattern_seed, texture_seed)
                stars, gas = np.asarray(F["pattern_density_contrast"]), np.asarray(F["gas_density_contrast"])
                worst["stars"] = max(worst["stars"], float(np.abs(stars.mean(axis=1) - 1.0).max()))
                worst["gas"] = max(worst["gas"], float(np.abs(gas.sum(axis=1) / gas.shape[1] - 1.0).max()))
                assert stars.min() >= 0.0 and gas.min() > 0.0, label
                got["least"], got["least_gas"], got["most_gas"] = min(got["least"], float(stars.min())), min(got["least_gas"], float(gas.min())), max(got["most_gas"], float(gas.max()))
                got["zeros"] += int((stars == 0.0).sum())
                nan = {n for n, v in F.items() if not isinstance(v, (str, tuple)) and np.isnan(np.asarray(v, dtype=float)).any()}
                assert nan == (set() if leg == "milky_way" else UNBARRED_NAN), (label, sorted(nan))
                off = run(model, given, only=LAWS, layer=False).fields
                assert all(np.asarray(off[k]).tobytes() == np.asarray(F[k]).tobytes() for k in LAWS), label
                budget, amplitude = np.asarray(F["arm_power_budget"]), np.asarray(F["arm_piece_amplitude"])
                cut, chains = np.asarray(F["arm_piece_saturation"]), np.asarray(F["arm_chain_count"])
                assert np.array_equal(budget, 0.5 * sum(np.asarray(F[k]) ** 2 for k in pt.AMPLITUDE_FIELDS)), label
                has, live = budget > 0.0, amplitude > 0.0
                # The budget in expectation, analytically: N v(sigma_d) B^2 - the count the law's, or a pinned
                # galaxy's chains - with v by this file's own sum of the piece's harmonics.
                pitch = float(F["pitch_angle"])
                sigma_d = (np.asarray(F["arm_piece_width"]) / FWHM) / (R * math.sin(math.radians(pitch)))
                m = np.arange(1, 400)[None, :]
                v = (sigma_d[:, None] ** 2 / math.pi * np.exp(-((m * sigma_d[:, None]) ** 2))).sum(axis=1)
                count = chains if leg == "milky_way" else np.asarray(F["arm_design_count"])
                worst["expected"] = max(worst["expected"], float(np.abs(count[live] * v[live] * amplitude[live] ** 2 / budget[live] - 1.0).max(initial=0.0)))
                assert np.array_equal(live, has & (sigma_d < math.sqrt(math.pi))) and np.all((cut > 0.0) & (cut <= 1.0)), label
                got["ratio"].extend((np.asarray(F["arm_ring_power"])[live] / budget[live]).tolist())
                got["cut"] += int((cut < 1.0).sum())
                got["no_arm"] += int((has & ~live).sum())
                got["no_chain"] += int((has & (chains == 0.0)).sum())
                got["budget"] += int(has.sum())
                got["pitch"].append(pitch)
                # The forcing's bound: each piece's m-th harmonic is under its stellar amplitude times R/(X h) whatever
                # its pitch, so a ring's m-th forcing amplitude is under the pieces' summed amplitudes times that.
                sp, gp = compose.stellar_pattern(F, R), compose.gas_pattern(F, R, c)
                _, tau, _, sigma, _ = sp.ring_pieces(R)
                stellar = ((sp.effective_amplitude(R, tau, sigma)[:, None] * tau)[:, :, None] * pc.harmonic_amplitudes(sigma)).sum(axis=1)
                taper = pt.bar_terms(R, pitch, float(F["bar_half_length"]))[0]
                bound = stellar / (1.0 - taper)[:, None] * (R / (gp.swing_x() * gp.layer_height))[:, None]
                f = gp.forcing_amplitudes()
                on = stellar > 1e-12 * stellar.max()
                worst["bound"] = max(worst["bound"], float((f[on] / bound[on]).max(initial=0.0)))
                got["armless"] += int(not live.any())  # a disc wound so tightly that no ring holds a ridge
                d = gp.diagnostics
                got["steps"] = max(got["steps"], d.worst_steps if d is not None else 0)
    assert worst["stars"] < 1e-12 and worst["gas"] < 2e-13 and worst["expected"] < 1e-10 and worst["bound"] <= 1.0, worst
    record = {}
    for leg in LEGS:
        got = read[leg]
        ratio = np.array(got["ratio"])
        low, mid, high = (round(float(q), 3) for q in np.percentile(ratio, (16.0, 50.0, 84.0)))
        record[leg] = (got["budget"], ratio.size, (low, mid, high), got["cut"], got["no_arm"], got["no_chain"], got["zeros"],
                       round(min(got["pitch"]), 3), round(max(got["pitch"]), 3), got["steps"], got["armless"])
    # (rings with a budget, rings with an amplitude, the realised power over the budget: 16th / 50th / 84th
    #  percentile, rings cut, rings with a budget and no amplitude, rings with a budget and no chain, exact zeros
    #  of the stellar field, the lowest and highest pitch, the most Newton steps a ring took, the galaxies in which
    #  no ring holds an amplitude at all - a disc wound so tightly that a piece is wider than every ring)
    assert record == EXPECTED_GATE, repr(record)
    least = {leg: (round(read[leg]["least"], 4), round(read[leg]["least_gas"], 4), round(read[leg]["most_gas"], 3)) for leg in LEGS}
    assert least == EXPECTED_LEAST, repr(least)


EXPECTED_GATE: dict = {
    "milky_way": (19800, 17720, (0.196, 0.442, 0.87), 6, 2080, 0, 0, 1.0, 24.333, 6, 6),
    "ngc_4414": (15960, 15720, (0.396, 0.549, 1.08), 0, 240, 0, 0, 28.9, 28.9, 6, 0),
    "ngc_4414 drawn": (15960, 14376, (0.265, 0.52, 0.984), 11, 1584, 0, 0, 1.0, 24.096, 7, 6),
}
# (the least value of the stellar field, the least and the largest of the gas's, over each leg's 120 galaxies)
EXPECTED_LEAST: dict = {
    "milky_way": (0.2244, 0.3253, 6.68), "ngc_4414": (0.5029, 0.2848, 2.669), "ngc_4414 drawn": (0.1093, 0.0218, 2.681),
}


def test_the_layer_off_lays_no_piece_and_every_composed_field_is_its_neutral(prod):
    """D219 item 7: "Layer off: no arm placed, every field bit-identical to main." Here: no row in the table, every
    composed field its declared neutral, every law the layer-on run's to the bit, and the census's streams not
    drawn (the run is the same whatever the texture seed). The comparison of every field of both templates and
    the default run with ``main`` is the builder's, made from a second checkout, and is recorded in D219."""
    model = the_model(prod)
    decls = {d.name: d for d in (*pc.COMPOSED, gm.GAS_DENSITY_CONTRAST, gm.STAR_FORMATION_GAS_CONTRAST)}
    for template in ("milky_way", "ngc_4414"):
        on = template_run(prod, template)
        off = run(model, inputs_of(template), only=PATTERN, layer=False)
        other = run(model, inputs_of(template, texture_seed=99), only=PATTERN, layer=False)
        for name in pt.PIECE_FIELDS:
            assert np.asarray(off.fields[name]).shape == (0,) and np.asarray(on.fields[name]).size > 0
        for name, d in decls.items():
            assert np.all(np.asarray(off.fields[name]) == d.neutral), name
        for name in LAWS:
            assert np.asarray(off.fields[name]).tobytes() == np.asarray(on.fields[name]).tobytes(), name
        for name in PATTERN:
            a, b = off.fields[name], other.fields[name]
            assert a == b if isinstance(a, str) else np.asarray(a).tobytes() == np.asarray(b).tobytes(), name
        assert compose.stellar_pattern(off.fields, off.grid.R) is None and compose.gas_pattern(off.fields, off.grid.R, constants(model)) is None


# --- the gas between rings ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", ("milky_way", "ngc_4414"))
def test_the_gas_carried_between_two_rings_against_a_direct_solve(prod, template):
    """D219 item 6: "a ring's solved profile is carried to a point along the pieces' loci ...; its misplaced weight
    against a direct solve at mid-gap radii is measured on both templates and pinned; if it exceeds 1 % on any
    star-forming gap, the ring step is halved there, not the tolerance raised."

    At the middle of every gap between two grid rings: the pattern's response (its two rings' carried profiles,
    blended) against the law solved at that radius (``GasPattern.solve_at``: the same pieces, the disc's κ and Σ
    read linearly between the rings), by S59's statistic. **It exceeds 1 % on star-forming gaps of both
    templates**: 4 gaps of the Milky Way template's 321, all inside the bar's half-length (0.45, 1.575, 1.65 and
    1.8 kpc; 2.20 % at worst; 0.78 % at worst past the bar), and 8 of ``ngc_4414``'s 247 (0.6-0.75, 2.175-2.325 and
    3.075-3.15 kpc; 2.77 % at worst). Each is crossed by a piece of little pitch - its anchor is displaced by the
    cotangent of its pitch across the gap, far more than its neighbours', and drags the profile between them,
    while its own ridge is nearly flat round the ring - but for the one gap in which the arms begin (the designed
    piece narrower than its ring on the outer ring and not on the inner). **The remedy is not taken here**: it
    is the lead's decision (halving the step halves such a piece's displacement and no more). The carried profile's
    mean round the ring is 1 by its own normaliser, exactly, at every such radius."""
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    sp, gp, _ = patterns(prod, o)
    mids = 0.5 * (R[:-1] + R[1:])
    cells = gr.cell_centres(gr.CELLS)
    carried = gp.response_at(mids[:, None], cells[None, :])
    miss = misplaced(carried, gp.solve_at(mids))
    now = np.asarray(F["sfr_surface_density"])  # the present-day star formation rate per ring
    forming = (now[:-1] > 1e-6 * now.max()) & (now[1:] > 1e-6 * now.max())
    over = np.flatnonzero((miss > 0.01) & forming)
    past_bar = mids > (float(F["bar_half_length"]) if template == "milky_way" else 0.0)
    record = (int(forming.sum()), round(100.0 * float(miss[forming].max()), 2), round(float(mids[forming][int(np.argmax(miss[forming]))]), 3),
              [round(float(mids[i]), 3) for i in over], round(100.0 * float(miss[forming & past_bar].max()), 2),
              round(100.0 * float(np.median(miss[forming & (miss > 0.0)])), 3))
    # (star-forming gaps, the worst misplaced weight % and its radius, the gaps over 1 %, the worst past the bar's
    #  half-length, the median over the gaps that carry an arm)
    assert record == EXPECTED_GAPS[template], repr(record)
    # Each gap over 1 % is crossed by a piece of little pitch - under half the disc's - or is the gap in which the
    # designed piece becomes a ridge on its ring and the arms begin (the amplitude 0 on its inner ring).
    p, pitch, amplitude = sp.pieces, float(F["pitch_angle"]), np.asarray(F["arm_piece_amplitude"])
    causes = []
    for i in over:
        crossing = {k for k in p.slots(np.array([R[i], R[i + 1]])).ravel().tolist() if k < p.count}
        low = min(abs(float(p.pitch_deg[k])) for k in crossing) < 0.5 * pitch
        begins = bool(amplitude[i] == 0.0 and amplitude[i + 1] > 0.0)
        assert low or begins, float(mids[i])
        causes.append("begins" if begins else "low pitch")
    assert causes.count("begins") == (1 if template == "milky_way" else 0)
    # The carried profile is a redistribution: sectors that tile the ring average to 1, at any radius.
    edges = np.linspace(0.0, 2.0 * math.pi, 65)
    means = np.array([gp.sector_means(float(r), edges) for r in mids[::9]])
    assert np.abs(means.mean(axis=1) - 1.0).max() < 5e-14 and means.min() > 0.0
    # ... and the sector means are the point function's integrals (a midpoint rule of 400 to a sector).
    r = float(mids[int(np.argmax(miss))])
    samples = (edges[:-1, None] + (edges[1] - edges[0]) * ((np.arange(400) + 0.5) / 400.0)[None, :])
    assert np.abs(gp.sector_means(r, edges) - gp.contrast_at(r, samples).mean(axis=1)).max() < 2e-6
    # At a ring's own radius nothing is carried: the point function is the ring's interpolant, to the bit.
    i = int(np.argmin(np.abs(R - 8.0)))
    phi = np.linspace(-3.0, 9.0, 501)
    assert np.array_equal(gp.response_at(R[i], phi), gr.interpolate(gp.profiles[i], phi))
    assert np.array_equal(gp.carried(np.array([i]), R[i : i + 1], phi[None, :])[0], gr.interpolate(gp.profiles[i], phi))


EXPECTED_GAPS: dict = {
    "milky_way": (321, 2.2, 1.575, [0.45, 1.575, 1.65, 1.8], 0.78, 0.063),
    "ngc_4414": (247, 2.77, 2.25, [0.6, 0.675, 0.75, 2.175, 2.25, 2.325, 3.075, 3.15], 2.77, 0.031),
}


# --- the gate's predictions, read as measured ----------------------------------------------------------------------


def tenth_over_half(s: np.ndarray) -> float:
    """The mean of the highest tenth of a ring's cells over the mean of its lower half."""
    ranked = np.sort(s)
    return float(ranked[-(ranked.size // 10):].mean() / ranked[: ranked.size // 2].mean())


def measured(prod, template: str) -> dict:
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    sp, gp, _ = patterns(prod, o)
    i0, i8 = int(np.argmin(np.abs(R - 8.15))), int(np.argmin(np.abs(R - 8.0)))
    band = (R >= 6.0) & (R <= 10.0)
    round_ring = np.linspace(0.0, 2.0 * math.pi, 7200, endpoint=False)
    stars = sp.contrast_at(R[i0], round_ring)
    ratio = gp.arm_ratio(gas_check.GAS_ARM_MASK_WIDTH)
    s = gp.profiles
    inner = (R < 3.0) & gp.carries
    p = sp.pieces
    pinned_crossing = len({int(p.chain[k]) for k in range(p.count) if p.pinned[k] and p.x_start[k] <= math.log(R[i0]) < p.x_end[k]})
    return {
        "chains at R0": int(F["arm_chain_count"][i0]), "pinned chains at R0": pinned_crossing, "n at R0": round(float(F["arm_design_count"][i0]), 2),
        "FWHM at R0": round(float(F["arm_piece_width"][i0]), 3), "B at R0": round(float(F["arm_piece_amplitude"][i0]), 3),
        "crest over trough at R0": round(float(stars.max() / stars.min()), 2),
        "sum f at 8": round(float(gp.forcing_amplitudes()[i8].sum()), 3), "gas min at 8": round(float(s[i8].min()), 3),
        "top tenth over lower half at 8": round(tenth_over_half(s[i8]), 2),
        "ratio of means 6-10": round(float(np.nanmedian(ratio[band])), 3), "rings under 1.37": int((ratio[band] < 1.37).sum()),
        "inner gas min": round(float(s[inner].min()), 3), "inner ratio": round(float(np.nanmedian(ratio[inner])), 2),
        "pieces": p.count, "chains": len(np.unique(p.chain)),
    }


def test_the_gate_s_predictions_as_measured(prod):
    """D219, "Its predictions (B4; read before they are judged)", each read on the built model before anything else
    was judged and recorded here held or not held. **Nothing was changed to make one hold.**

    *Milky Way template* (its arms pinned):
    - "five chains cross R₀ (pinned: Reid's four and the Local arm; unpinned: n ≈ 4.8)" - **not held: eight.** Two
      of them are measured stretches (the Local arm and Perseus: no other fitted range reaches R₀), three are
      drawn continuations of measured arms and three are chains born inside, where no measured arm crosses and
      the law counts three to five. n there is 4.72.
    - "FWHM 1.9 kpc there" - **held: 1.947.** "against a spacing of about 2.4 kpc" - not held: eight chains stand
      1.50 kpc apart.
    - "B ≈ 0.45–0.55" - **not held: 0.329**, the budget shared among eight chains (with the law's 4.72: 0.43).
    - "crest over trough 1.6–1.8 (0.5–0.6 mag)" - **not held: 2.26 (0.89 mag)**, over the multi-armed 0.81 ± 0.28
      mag's centre and over the goal's 1.83.
    - "with the thickness factor Σf at 8 kpc ≈ 1.0" - **not held: 0.563** (the forcing's harmonics' summed
      amplitudes; a broad Gaussian piece holds little past m = 5, where the modes held most).
    - "the gas minimum 0.3–0.5" - **not held: 0.788.** "the top tenth over the lower half ≈ 2" - **not held: 1.48.**
    - "the PHANGS ratio of means 1.8–2.2" - **not held: 1.275** over 6-10 kpc, 51 of its 53 rings under the
      source's 16th percentile 1.37: the disclosed check turns to a miss on this template.

    *``ngc_4414``* (flocculent):
    - "many pieces of 37°–105°" - **held: 36 single pieces, 39.7°-104.1°.**
    - "the inner gas restored (minimum 1e-14 → ≈ 0.8, ratio 1.2–1.4 inside 3 kpc)" - **held in kind**: the
      minimum inside 3 kpc is 0.688 and the ratio 1.26.
    - "the check's median falls from 1.406 to ≈ 1.3, under 1.37: a miss" - **held: 1.258**, 50 of 53 rings under.

    "Layer off: nothing moves" - held (the test above, and the builder's comparison with ``main``)."""
    got = {template: measured(prod, template) for template in ("milky_way", "ngc_4414")}
    assert got == EXPECTED_PREDICTIONS, repr(got)
    mw, n4 = got["milky_way"], got["ngc_4414"]
    held = {
        "five chains cross R0": mw["chains at R0"] == 5,
        "FWHM 1.9 kpc": abs(mw["FWHM at R0"] - 1.9) < 0.05,
        "B 0.45-0.55": 0.45 <= mw["B at R0"] <= 0.55,
        "crest over trough 1.6-1.8": 1.6 <= mw["crest over trough at R0"] <= 1.8,
        "sum f about 1.0": abs(mw["sum f at 8"] - 1.0) < 0.15,
        "gas minimum 0.3-0.5": 0.3 <= mw["gas min at 8"] <= 0.5,
        "top tenth over lower half about 2": abs(mw["top tenth over lower half at 8"] - 2.0) < 0.3,
        "ratio of means 1.8-2.2": 1.8 <= mw["ratio of means 6-10"] <= 2.2,
        "ngc_4414 inner ratio 1.2-1.4": 1.2 <= n4["inner ratio"] <= 1.4,
        "ngc_4414 median about 1.3, a miss under 1.37": abs(n4["ratio of means 6-10"] - 1.3) < 0.08 and n4["ratio of means 6-10"] < 1.37,
    }
    assert held == {
        "five chains cross R0": False, "FWHM 1.9 kpc": True, "B 0.45-0.55": False, "crest over trough 1.6-1.8": False,
        "sum f about 1.0": False, "gas minimum 0.3-0.5": False, "top tenth over lower half about 2": False,
        "ratio of means 1.8-2.2": False, "ngc_4414 inner ratio 1.2-1.4": True, "ngc_4414 median about 1.3, a miss under 1.37": True,
    }, held


EXPECTED_PREDICTIONS: dict = {
    "milky_way": {"chains at R0": 8, "pinned chains at R0": 2, "n at R0": 4.72, "FWHM at R0": 1.947, "B at R0": 0.329,
                  "crest over trough at R0": 2.26, "sum f at 8": 0.563, "gas min at 8": 0.788, "top tenth over lower half at 8": 1.48,
                  "ratio of means 6-10": 1.275, "rings under 1.37": 51, "inner gas min": 0.768, "inner ratio": 1.2, "pieces": 137, "chains": 26},
    "ngc_4414": {"chains at R0": 6, "pinned chains at R0": 0, "n at R0": 5.12, "FWHM at R0": 1.825, "B at R0": 0.5,
                 "crest over trough at R0": 2.65, "sum f at 8": 0.71, "gas min at 8": 0.835, "top tenth over lower half at 8": 1.47,
                 "ratio of means 6-10": 1.258, "rings under 1.37": 50, "inner gas min": 0.688, "inner ratio": 1.26, "pieces": 36, "chains": 36},
}


def test_disclosed_check_the_split_of_a_ring_s_power_by_arm_number(prod):
    """D219 item 4: "The split by m survives as a disclosed check: the composed field's realised Fourier power by m
    against the law's A_m², published, read, not tuned." Per template, summed over the rings of 6-10 kpc: the
    square of the composed arm field's m-fold amplitude beside the square of the law's amplitude, m = 2 … 6; and
    the realised ring variance over the budget.

    **As read: the pieces do not split a ring's power as the law does.** A broad ridge puts its power at low arm
    numbers - a piece half a radian wide holds almost nothing past m = 4 - where the law, outside the bar, puts
    it at five and six arms. On the Milky Way template the two-fold power is about 170 times the law's over
    6-10 kpc and the six-fold a sixty-sixth of it; on ``ngc_4414`` 22 times and a sixth. The realised ring
    variance is 0.55 and 0.95 of the budget there. Recorded; nothing is tuned to it. The published fields are the
    pattern's own Fourier coefficients, held here to a transform of the point function."""
    record = {}
    for template in ("milky_way", "ngc_4414"):
        o = template_run(prod, template)
        F, R = o.fields, o.grid.R
        sp, _, _ = patterns(prod, o)
        band = (R >= 6.0) & (R <= 10.0)
        realised = [float(np.asarray(F[f"arm_mode_power_{m}"])[band].sum()) for m in pt.ARM_MODES]
        law = [float((np.asarray(F[pt.amplitude_field(m)])[band] ** 2).sum()) for m in pt.ARM_MODES]
        budget, power = np.asarray(F["arm_power_budget"]), np.asarray(F["arm_ring_power"])
        record[template] = ([round(v, 3) for v in realised], [round(v, 3) for v in law], round(float(power[band].sum() / budget[band].sum()), 3))
        # The published powers are the field's: a transform of the point function on one ring.
        i = int(np.argmin(np.abs(R - 8.0)))
        phi = (np.arange(4096) + 0.5) * (2.0 * math.pi / 4096)
        spectrum = np.fft.rfft(sp.arms_at(R[i], phi)) / 2048.0
        for m in pt.ARM_MODES:
            assert abs(spectrum[m]) ** 2 == pytest.approx(float(F[f"arm_mode_power_{m}"][i]), rel=1e-9)
        assert float(F["arm_ring_power"][i]) == pytest.approx(0.5 * float((np.abs(spectrum[1:]) ** 2).sum()), rel=1e-9)
    assert record == EXPECTED_SPLIT, repr(record)


EXPECTED_SPLIT: dict = {
    # (the realised m-fold power summed over 6-10 kpc, m = 2 ... 6; the law's; the realised ring variance over the budget there)
    "milky_way": ([1.542, 0.484, 0.181, 0.106, 0.037], [0.009, 1.064, 2.126, 2.44, 2.437], 0.553),
    "ngc_4414": ([0.874, 0.983, 0.386, 0.747, 0.432], [0.039, 0.619, 1.165, 1.757, 2.408], 0.945),
}


# --- the pinned loci, and the masers against the gas and the young stars ---------------------------------------------


def test_the_composed_stellar_crest_against_the_pinned_loci(prod):
    """D219 item 8: "the composed stellar crest lies within 0.1 width of each pinned locus over its β range — by
    construction, asserted, not a test of the model". **What holds by construction is asserted in the test of the
    pinned pieces: each pinned piece's own ridge is the fitted locus, to 1e-12 kpc. The sentence as worded does
    not hold, and is measured here**: the crest of the *composed* field - a local maximum along a radius of the
    sum of every piece - stands within a tenth of the arm's width (the model's, 1.9 kpc at R₀) of a locus on
    the share of its points recorded below: 78 % for Scutum-Centaurus, 72 % for the Local arm, 60 % for Perseus,
    55 % and 48 % for Sagittarius-Carina and Norma, 28 % for the Outer arm (the median distance 0.06-0.10 width,
    0.24 for the Outer arm). A stellar arm 1.9 kpc wide beside neighbours 1.5 kpc away has no
    crest of its own: the Local arm lies between Sagittarius-Carina and Perseus and merges with them, and near a
    piece's ends its ridge has faded (each piece's taper, as ruled). Recorded, not mended."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp, _, _ = patterns(prod, o)
    sun, sense = float(F["sun_azimuth"]), pt.rotation_sense(float(F["pitch_angle"]))
    r = np.arange(0.5, 20.0, 0.005)
    record = {}
    for row in reid2019.TABLE2:
        if row[0] not in reid2019.PINNED:
            continue
        beta, radius = reid2019.locus(row)
        v = sp.contrast_at(r[:, None], (sun + sense * np.radians(beta))[None, :])
        peak = (v[1:-1] > v[:-2]) & (v[1:-1] >= v[2:])
        near = np.array([np.abs(r[1:-1][peak[:, j]] - radius[j]).min() if peak[:, j].any() else np.inf for j in range(beta.size)])
        widths = near / np.interp(radius, R, np.asarray(F["arm_piece_width"]))
        record[row[0]] = (round(float(np.median(widths)), 2), round(float((widths <= 0.1).mean()), 2))
    # (the median distance from the locus to the nearest composed crest, in the model's arm widths; the share of the
    #  locus within a tenth of a width)
    assert record == EXPECTED_CREST, repr(record)


EXPECTED_CREST: dict = {
    "Norma": (0.1, 0.48), "Sct-Cen": (0.07, 0.78), "Sgr-Car": (0.1, 0.55), "Local": (0.06, 0.72), "Perseus": (0.08, 0.6), "Outer": (0.24, 0.28),
}


def test_disclosed_check_the_masers_loci_against_the_gas_s_and_the_young_stars_crests(prod):
    """D219 item 8: "the model is tested by the gas and young stars' crest against the maser loci within the masers'
    σ (0.34 kpc at R₀), a disclosed check with its null stated". **A disclosed check, not a spec row** (I3). The
    statistic is ``tests/reid2019.py``'s: for each of the five arms, over its β range, the radial distance from
    the fitted locus to the nearest crest of the field along the point's azimuth, in the masers' own σ(R) =
    336 + 36 (R − 8.15) pc; the median of the five arms' medians. Read on the gas's contrast and on the young
    stars' placement law (the reader's point function), on the Milky Way template at its default seeds - and
    against **the null**: the same field with the Sun placed at each of 360 azimuths.

    **As read** (the record): the gas's crests stand a median of 0.39 maser σ from the loci (Norma-Outer 1.30,
    Scutum-Centaurus 0.55, Sagittarius-Carina 0.05, Perseus 0.38, the Local arm 0.39; all points pooled 0.48) and
    the young stars' 0.45 (0.79, 0.39, 0.05, 0.45, 0.47; pooled 0.39): **inside the masers' σ**. **And the null
    reads the same**: with the Sun at any of 360 azimuths the gas's statistic has a median of 0.50 σ (5-95 %:
    0.37-0.88) and 98 % of the rotations lie within one σ; the young stars' 0.49 (0.36-0.64), every rotation
    within one σ. The as-built values are the 14th and the 36th percentile of their nulls. **So the check passes
    and has little power**: a crest of the gas or of the young stars' law is never far along a radius - several
    broad arms to a ring, and the ripples of their answer - against a σ of 0.34 kpc. It does not tell the pinned
    Milky Way from a rotated one; no verdict beyond the percentile is drawn."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    _, gp, c = patterns(prod, o)
    reader = systems.young_reader(F, R, c)
    sun, sense = float(F["sun_azimuth"]), pt.rotation_sense(float(F["pitch_angle"]))
    fields = {"gas": lambda r, phi: gp.contrast_at(r[:, None], phi[None, :]), "young stars": lambda r, phi: reader.at(r, phi)}
    record = {}
    for name, contrast in fields.items():
        null, per_arm, pooled = reid2019.rotation_null(contrast, sun, sense)
        built = float(null[0])
        record[name] = (round(built, 2), {arm: round(v, 2) for arm, v in per_arm.items()}, round(pooled, 2), round(float(np.median(null)), 2),
                        tuple(round(float(q), 2) for q in np.percentile(null, (5.0, 95.0))), round(100.0 * float((null <= built).mean())),
                        round(100.0 * float((null <= 1.0).mean())))
    # (as built: the median over the five arms in maser sigmas; each arm's; all points pooled; the null's median;
    #  its 5th and 95th percentiles; the percentile of the as-built value in its null; the share of rotations at
    #  or under one sigma)
    assert record == EXPECTED_MASERS, repr(record)


EXPECTED_MASERS: dict = {
    "gas": (0.39, {"Norma-Outer": 1.3, "Sct-Cen": 0.55, "Sgr-Car": 0.05, "Perseus": 0.38, "Local": 0.39}, 0.48, 0.5, (0.37, 0.88), 14, 98),
    "young stars": (0.45, {"Norma-Outer": 0.79, "Sct-Cen": 0.39, "Sgr-Car": 0.05, "Perseus": 0.45, "Local": 0.47}, 0.39, 0.49, (0.36, 0.64), 36, 100),
}


# --- the young stars' reader on the new pattern (ported from S59's file) ---------------------------------------------


def test_the_young_stars_reader_is_the_law_of_the_gas_s_point_function(prod):
    """S59's ruling on the reader (D218), on the pattern of pieces: the young stars are placed by the star
    formation law applied to the gas pattern's point function, ring by ring, each ring's term a redistribution
    at every radius, nothing that exists only on rings interpolated. What S60 changes is how a ring's profile
    reaches a point at another radius - carried along the pieces' loci, not turned by a common winding - and the
    reader follows by construction (D219 item 7). Held here: at a grid radius the reader is that ring's law of
    the pattern's own contrast, the ratio constant round the ring; between two rings each ring's term averages
    to 1 round the ring (the normaliser's quadrature) and so does the reader; its sector means are the
    function's integrals; and the published table, at every cell, is the same law at the cell's mean contrast."""
    for template in ("milky_way", "ngc_4414"):
        o = template_run(prod, template)
        F, R = o.fields, o.grid.R
        _, gp, c = patterns(prod, o)
        reader = systems.young_reader(F, R, c)
        phi = (np.arange(2880) + 0.5) * (2.0 * math.pi / 2880)
        # At a grid radius: the law of the pattern's own star-formation contrast there, over its mean.
        for radius in (2.0, 5.0, 8.0, 11.0):
            i = int(np.argmin(np.abs(R - radius)))
            contrast = gp.star_formation_contrast_at(R[i], phi)
            law = reader._law(np.array([i]), contrast[None, :])[0]
            got = reader.at(R[i : i + 1], phi)[0]
            if law.mean() > 0.0:
                assert np.abs(got * law.mean() - law).max() < 2e-3 * law.mean() and abs(got.mean() - 1.0) < 5e-4, (template, radius)
        # Between two rings: a redistribution, and positive.
        mids = 0.5 * (R[:-1] + R[1:])[10:160:7]
        between = reader.at(mids, phi)
        assert np.abs(between.mean(axis=1) - 1.0).max() < 2e-3 and between.min() >= 0.0, template
        # Its sector means are its integrals: against 400 midpoints to a sector.
        edges = np.linspace(0.0, 2.0 * math.pi, 65)
        samples = (edges[:-1, None] + (edges[1] - edges[0]) * ((np.arange(400) + 0.5) / 400.0)[None, :]).ravel()
        radii = mids[::5]
        want = reader.at(radii, samples).reshape(radii.size, 64, 400).mean(axis=2)
        assert np.abs(reader.sector_means_at(radii, edges) - want).max() < READER_SECTOR_BOUND[template], template
        # The published table is the law at the cell's mean contrast, over the ring's mean (D218's third follow-up).
        table, cellwise = np.asarray(F["sfr_modulation"]), np.asarray(F["star_formation_gas_contrast"])
        rings = np.arange(5, R.size, 31)
        law = reader._law(rings, cellwise[rings])
        mean = law.mean(axis=1, keepdims=True)
        assert np.array_equal(np.where(mean > 0.0, law / np.where(mean > 0.0, mean, 1.0), 1.0), table[rings]), template


READER_SECTOR_BOUND = {"milky_way": 1e-3, "ngc_4414": 1e-3}


# --- the pins --------------------------------------------------------------------------------------------------------


def test_a_pin_is_a_class_a_named_class_a_number_or_a_table(prod):
    """D217's mechanism (a pin reaches a run by its template's name alone), D218's (a pin with a unit is a measured
    number, held to the range of what it replaces), and S60's two shapes (D219 items 3 and 8): **a named class** -
    one of a closed list, a text - and **a table** - rows of the source's own columns. Each is validated where a
    template is built and where a run resolves its inputs, refused as a request's own parameter, and served by
    ``/api/templates`` in the shape ``service.pin_json`` documents."""
    model = the_model(prod)
    assert [INPUTS[n].shape for n in ("bar_present", "arm_class", "pitch_angle", "sun_bar_angle", "arm_pieces")] == ["class", "named", "number", "number", "table"]
    only = ("arm_class", "arm_piece_chain", "pitch_angle", "sun_azimuth")
    # The class of three.
    assert run(model, None, SMALL, only=only).fields["arm_class"] == "grand_design"
    assert run(model, {"bar_present": False}, SMALL, only=only).fields["arm_class"] == "multi_armed"
    for name in ARM_CLASSES:
        assert run(model, {"arm_class": name}, SMALL, only=only).fields["arm_class"] == name
    for bad in (True, 2.0, "grand design", "", ("flocculent",)):
        with pytest.raises(RunError, match="is one of"):
            run(model, {"arm_class": bad}, SMALL, only=only)
    # The table: rows of the declared columns, each held to what the source's form allows.
    good = ("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4)
    pins = {"bar_present": True, "sun_bar_angle": 30.0}
    assert int(run(model, {**pins, "arm_pieces": (good,)}, SMALL, only=only).fields["arm_piece_chain"].size) > 0
    assert INPUTS["arm_pieces"].pinned([list(good)]) == (good,)  # a list of lists is taken as rows
    for bad, why in (
        ((), "a table"), ("Local", "a table"), ((good[:-1],), "a row holds"), (((1.0, *good[1:]),), "is a name"),
        ((("Local", "x", *good[2:]),), "finite number in deg"), (((*good[:4], float("nan"), *good[5:]),), "finite number in kpc"),
        ((good, good), "named twice"), ((("Local", 34.0, -8.0, 9.0, 8.26, 11.4, 11.4),), "run from beta_from"),
        ((("Local", -8.0, 34.0, 40.0, 8.26, 11.4, 11.4),), "kink lies inside"), ((("Local", -8.0, 34.0, 9.0, 0.0, 11.4, 11.4),), "radius is positive"),
        ((("Local", -8.0, 34.0, 9.0, 8.26, 0.0, 11.4),), "not zero and under 90"), ((("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 90.0),), "not zero and under 90"),
        ((("Local", -400.0, 34.0, 9.0, 8.26, 11.4, 11.4),), "within a turn"),
    ):
        with pytest.raises(RunError, match=why):
            run(model, {**pins, "arm_pieces": bad}, SMALL, only=only)
    # A template is held to the same, when it is built; and pinned arms need the Sun.
    mw = templates.TEMPLATES["milky_way"]
    import dataclasses
    with pytest.raises(templates.TemplateError, match="is one of"):
        dataclasses.replace(mw, pins=(*mw.pins, templates.Pin("arm_class", "spiral", "[inferred]"))).validate()
    with pytest.raises(templates.TemplateError, match="named twice"):
        dataclasses.replace(mw, pins=tuple(p if p.name != "arm_pieces" else templates.Pin("arm_pieces", (good, good), "[inferred]") for p in mw.pins)).validate()
    with pytest.raises(templates.TemplateError, match="placed by the Sun's azimuth"):
        dataclasses.replace(mw, pins=tuple(p for p in mw.pins if p.name != "sun_bar_angle")).validate()
    with pytest.raises(templates.TemplateError, match="a class, True or False"):
        dataclasses.replace(mw, pins=(templates.Pin("bar_present", "yes", "[inferred]"),)).validate()
    with pytest.raises(RegistryError, match="only a pin names classes or columns"):
        Input("x", "x", "control", "x", unit="deg", default=1.0, classes=("a", "b"))
    # No request offers a pin, of any shape; /api/inputs lists none.
    api = Service(grid=SMALL)
    for query in ("fields=arm_class&arm_class=flocculent", "fields=arm_class&template=ngc_4414&arm_class=grand_design", "fields=arm_class&arm_pieces=[]"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    listed = api.handle("/api/inputs").json()
    assert not {"arm_class", "arm_pieces"} & {i["name"] for kind in ("controls", "seeds", "events") for i in listed[kind]}
    # The wire: /api/templates serves each pin in its shape.
    served = {t["name"]: {p["name"]: p for p in t["pins"]} for t in api.handle("/api/templates").json()["templates"]}
    assert set(served["milky_way"]) == {"bar_present", "sun_bar_angle", "arm_pieces"} and set(served["ngc_4414"]) == {"bar_present", "pitch_angle", "arm_class"}
    klass = served["ngc_4414"]["arm_class"]
    assert set(klass) == {"name", "label", "unit", "value", "source", "classes"} and klass["value"] == "flocculent" and klass["unit"] is None
    assert klass["classes"] == ["grand_design", "multi_armed", "flocculent"]
    rows = served["milky_way"]["arm_pieces"]
    assert set(rows) == {"name", "label", "unit", "value", "source"} and rows["unit"] is None and set(rows["value"]) == {"columns", "rows"}
    assert rows["value"]["columns"] == [{"name": "arm", "unit": None}, {"name": "beta_from", "unit": "deg"}, {"name": "beta_to", "unit": "deg"},
                                        {"name": "beta_kink", "unit": "deg"}, {"name": "radius_kink", "unit": "kpc"},
                                        {"name": "pitch_below", "unit": "deg"}, {"name": "pitch_above", "unit": "deg"}]
    assert rows["value"]["rows"][0] == ["Norma", 5.0, 54.0, 18.0, 4.46, -1.0, 19.5] and len(rows["value"]["rows"]) == 6
    assert set(served["milky_way"]["bar_present"]) == set(served["milky_way"]["sun_bar_angle"]) == {"name", "label", "unit", "value", "source"}
    assert served["milky_way"]["bar_present"]["value"] is True and served["milky_way"]["sun_bar_angle"]["value"] == 30.0
    # A response's inputs echo the pins the template gave: the table as rows.
    head = api.handle("/api/arrays", "fields=arm_class&template=milky_way").frame()[0]
    assert head["inputs"]["arm_pieces"][3] == ["Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4] and head["inputs"]["sun_bar_angle"] == 30.0
    assert api.handle("/api/arrays", "fields=arm_class&template=ngc_4414").frame()[0]["inputs"]["arm_class"] == "flocculent"


def test_a_measured_number_is_a_pin_and_the_sun_moves_nothing_else(prod):
    """Ported from S59's file (D218 items 5-6 and the follow-up's item 7), unchanged in what it holds: a pin with
    a unit is a finite number held to the range of what it replaces; ``sun_bar_angle`` gives ``sun_azimuth`` and
    moves no other field; ``pitch_angle`` replaces the draw, which is published beside it; a run made with a pin
    is not resumed without it."""
    model = the_model(prod)
    only = ("sun_azimuth", "pitch_angle", "pitch_angle_drawn", "bar_half_length", "pattern_density_contrast", "gas_density_contrast")
    bare = run(model, None, SMALL, only=only)
    sun = run(model, {"sun_bar_angle": 30.0}, SMALL, only=only)
    assert math.isnan(float(bare.fields["sun_azimuth"])) and math.isfinite(float(sun.fields["sun_azimuth"]))
    for name in only[1:]:
        assert np.asarray(bare.fields[name]).tobytes() == np.asarray(sun.fields[name]).tobytes(), name
    assert math.isnan(float(run(model, {"sun_bar_angle": 30.0, "bar_present": False}, SMALL, only=only).fields["sun_azimuth"]))
    other = run(model, {"sun_bar_angle": 28.0}, SMALL, only=only)
    assert float(other.fields["sun_azimuth"]) - float(sun.fields["sun_azimuth"]) == pytest.approx(math.radians(-2.0), abs=1e-12)
    pitched = run(model, {"pitch_angle": 20.0}, SMALL, only=only)
    assert float(pitched.fields["pitch_angle"]) == 20.0 and float(pitched.fields["pitch_angle_drawn"]) == float(bare.fields["pitch_angle"])
    for bad in (True, "30", float("nan"), float("inf")):
        with pytest.raises(RunError, match="finite number in deg"):
            run(model, {"sun_bar_angle": bad}, SMALL, only=only)
    with pytest.raises(RunError, match="True or False"):
        run(model, {"bar_present": 1.0}, SMALL, only=only)
    with pytest.raises(RunError, match="cannot resume: (pin|input) 'pitch_angle'"):
        run(model, {}, SMALL, resume=pitched, only=only)
    for value, ok in ((1.0, True), (60.0, True), (0.999, False), (60.001, False), (-5.0, False)):
        if ok:
            assert float(run(model, {"pitch_angle": value}, SMALL, only=only).fields["pitch_angle"]) == value
        else:
            with pytest.raises(RunError, match="held to the range of what it replaces, 1 to 60 deg"):
                run(model, {"pitch_angle": value}, SMALL, only=only)
    for value, ok in ((0.0, True), (359.9, True), (360.0, False), (-0.1, False)):
        if ok:
            run(model, {"sun_bar_angle": value}, SMALL, only=only)
        else:
            with pytest.raises(RunError, match="0 up to, not including, 360 deg"):
                run(model, {"sun_bar_angle": value}, SMALL, only=only)
    api = Service(grid=SMALL)
    for query in ("fields=sun_azimuth&sun_bar_angle=30", "fields=pitch_angle&pitch_angle=20", "fields=pitch_angle&template=ngc_4414&pitch_angle=20"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    head = api.handle("/api/arrays", "fields=sun_azimuth,pitch_angle,pitch_angle_drawn&template=ngc_4414").frame()[0]
    assert head["inputs"]["pitch_angle"] == 28.9 and head["scalars"]["pitch_angle"] == 28.9 and head["scalars"]["sun_azimuth"] is None


# --- the table kind (ported from S59's file) -------------------------------------------------------------------------


def test_the_pieces_are_a_table_served_whole_and_no_catalogue(prod):
    """S59's plumbing decision (D218), kept for the table that replaced ``arm_segment``: the census's columns are
    a table's - domain ``table``, read whole by the model's own stages, no object class, no census route, no ramp -
    and the API serves them whole with the run's other arrays."""
    assert TABLES == ("arm_piece",) and Kind.TABLE_COLUMN.domain == "table" and not Kind.TABLE_COLUMN.categorical
    for d in ap.ARM_PIECES:
        assert d.kind is Kind.TABLE_COLUMN and d.of == "arm_piece" and d.ramp is None and not d.axes
    base = dict(name="x", label="x", unit="rad", about="x", kind=Kind.TABLE_COLUMN)
    from galaxy.core.fielddoc import DeclarationError, Ramp
    with pytest.raises(DeclarationError, match="one of the tables"):
        FieldDecl(**base, of="arm_segment")
    with pytest.raises(DeclarationError, match="is not drawn and takes no ramp"):
        FieldDecl(**base, of="arm_piece", ramp=Ramp("viridis"))
    api = Service(grid=SMALL)
    ask = "fields=" + ",".join((*pt.PIECE_FIELDS, "arm_class")) + "&template=milky_way"
    got = api.handle("/api/arrays", ask)
    assert got.status == 200
    head, arrays = got.frame()
    o = run(the_model(prod), inputs_of("milky_way"), SMALL, only=pt.PIECE_FIELDS)
    assert set(arrays) == set(pt.PIECE_FIELDS) and "arm_pieces" in head["stages"] and not {"systems", "clouds", "clusters"} & set(head["stages"])
    for name in pt.PIECE_FIELDS:
        assert arrays[name].dtype == np.float64 and arrays[name].ndim == 1 and arrays[name].size > 0
        assert arrays[name].tobytes() == np.asarray(o.fields[name]).tobytes() and o.decls[name].kind is Kind.TABLE_COLUMN, name
    _, narrow = api.handle("/api/arrays", ask + "&precision=f4&t_samples=8").frame()
    assert all(narrow[n].dtype == np.float32 and np.array_equal(narrow[n], arrays[n].astype(np.float32)) for n in pt.PIECE_FIELDS)
    _, off = api.handle("/api/arrays", ask + "&layer=off").frame()
    assert all(off[name].shape == (0,) for name in pt.PIECE_FIELDS)
    window = "r_min=7&r_max=9&phi_min=0&phi_max=0.4"
    for path, query in (("/api/region", window), ("/api/clouds", window), ("/api/clusters", window), ("/api/remnants", window),
                        ("/api/bright", window + "&n=50")):
        r = api.handle(path, query)
        assert r.status == 200, (path, r.body[:200])
        header, rows = wire.decode(r.body)
        assert header["columns"] and not [c for c in (*header["columns"], *rows) if c.startswith("arm_piece")], path
