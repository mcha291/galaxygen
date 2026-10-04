"""Several arm modes at once, and a gas ridge that follows any pattern (S56, BUILD_III Phase P1; DECISIONS.md D215).

The gate's tests, in the gate's words (Fable's, D215): ring means 1 to 1e-12 on every ring; the m = 2-6 cosine
amplitudes recovered from the composed field equal the published ones (the bar's m = 2 term added at its taper) to
1e-9 on every ring, no exclusions; the minimum over cells >= 0 on every seed the suite draws. And the plan's: with
one mode the stellar field is S55's exactly and the gas field is S51's to 1e-9.

Then what the law is, read back from the model: the gain capped at one, the saturation, the dominant arm number as a
label nothing composes from, the phases a draw on ``texture_seed`` that is not made with the layer off - and the
gate's predictions, **pinned as measured** (one of them failed, and is pinned as it failed: B5).

The numbers, on the production grid (both templates at their own seeds; 2026-10-04):

    milky_way   A 0.4013, bar 0.2893; the last ring with any pattern 14.81 kpc at 0.0153 A^2; the whole A^2 out to
                13.76 kpc; half of it to 14.14 kpc; saturation 1 on every ring (worst sum of amplitudes 0.893);
                the largest ring-to-ring jump of A_tot/A 0.143; the label 3 (it was the drawn 4)
    ngc_4414    A 0.3552, bar 0.3210; 11.51 kpc at 0.0508 A^2; 10.84; 11.06; saturation 1 (0.790); jump 0.225;
                the label 2 (it was the drawn 4)
"""

from __future__ import annotations

import ast
import math
from pathlib import Path

import numpy as np
import pytest

import layer_reference
import s55_patterns as s55
from galaxy import templates
from galaxy.core import seeds as _seeds
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.core.stage import Context
from galaxy.layer import arm_phases, compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gp
from galaxy.stages import pattern as pt

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "model" / "galaxy"
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
TEMPLATES = ("milky_way", "ngc_4414")
TEXTURE_SEEDS = (None, 1, 2, 77, 987654321)  # None: the template's own
LAW_FIELDS = (*pt.AMPLITUDE_FIELDS, "arm_saturation", "arm_multiplicity", "arm_contrast", "bar_contrast", "pitch_angle",
              "bar_half_length", "gas_arm_contrast")
PATTERN_FIELDS = ("pattern_density_contrast", "gas_density_contrast", *LAW_FIELDS, *pt.PHASE_FIELDS,
                  "circular_velocity", "epicyclic_frequency", "disc_surface_density")
_RUNS: dict[tuple, object] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(m) -> dict[str, float]:
    return {k: c.value for k, c in m.constants.items()}


def inputs_of(template: str, **more) -> dict:
    return {**templates.overrides(templates.TEMPLATES[template]), **{k: v for k, v in more.items() if v is not None}}


STELLAR_FIELDS = tuple(n for n in PATTERN_FIELDS if n != "gas_density_contrast")


def pattern_run(prod, template: str = "milky_way", grid: GridSpec = DEFAULT, layer: bool = True, gas: bool = True, **more):
    """The pattern stages' fields alone (rule D4: four cheap stages), once per request. ``gas=False`` leaves the
    gas's ridge out, where a test draws hundreds of galaxies for the stellar field alone."""
    key = (template, grid, layer, gas, tuple(sorted(more.items())))
    if key not in _RUNS:
        only = PATTERN_FIELDS if gas else STELLAR_FIELDS
        _RUNS[key] = run(the_model(prod), inputs_of(template, **more), grid, only=only, layer=layer)
    return _RUNS[key]


def law_of(out, c) -> pt.ModeLaw:
    """The law recomputed from a run's published fields: the weights, the gain, the taper, the saturation."""
    F, R = out.fields, out.grid.R
    weights = pt.local_swing_weights(
        R, F["circular_velocity"], F["epicyclic_frequency"], F["disc_surface_density"], c["G"],
        c["SWING_X_LOW"], c["SWING_X_HIGH"], c["SWING_X_DEAD"], c["SWING_X_FLOOR"], c["ARM_MULTIPLICITY_MAX"],
    )
    return pt.mode_law(R, weights, float(F["arm_contrast"]), float(F["bar_contrast"]), float(F["pitch_angle"]),
                       float(F["bar_half_length"]))


def published_amplitudes(out) -> np.ndarray:
    return np.stack([np.asarray(out.fields[n]) for n in pt.AMPLITUDE_FIELDS])


def single_mode(R, m: int, f: dict[str, float], c) -> tuple[pt.ArmPattern, gp.GasPattern]:
    """One arm number, phase 0, the amplifier's weight 1 on every ring - a composition, built directly: it does not
    pass through the switch or the draw."""
    weights = np.zeros((len(pt.ARM_MODES), R.size))
    weights[pt.ARM_MODES.index(m)] = 1.0
    law = pt.mode_law(R, weights, f["arm_contrast"], f["bar_contrast"], f["pitch_angle"], f["bar_half_length"])
    assert np.all(law.saturation == 1.0)  # one mode cannot reach the mean: A < 1 and the bar's cap under its taper
    zero = (0.0,) * len(pt.ARM_MODES)
    stars = pt.ArmPattern(R, law.amplitudes, zero, f["bar_contrast"], f["pitch_angle"], f["bar_half_length"])
    unit = gp.GasPattern.unit_amplitudes(R, law.amplitudes, f["arm_contrast"], f["pitch_angle"], f["bar_half_length"])
    gas = gp.GasPattern(R, unit, zero, f["gas_arm_contrast"], f["bar_contrast"], f["pitch_angle"], f["bar_half_length"],
                        c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])
    return stars, gas


# --- the gate: ring means ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("grid", [DEFAULT, SMALL], ids=["production grid", "small grid"])
def test_gate_every_ring_of_the_composed_fields_has_mean_one(prod, template, grid):
    """Ring means 1 to 1e-12 on every ring, both templates, several texture seeds: a phase moves a cosine round its
    ring and no mode has a mean. The gas's ridge has mean 1 over the ring and is finite everywhere; on the grid's
    cells the stage holds its sampled mean (a ranked ridge's is not 1 to rounding: tests/test_gas_pattern.py)."""
    for seed in TEXTURE_SEEDS:
        o = pattern_run(prod, template, grid, texture_seed=seed)
        stars, gas = np.asarray(o.fields["pattern_density_contrast"]), np.asarray(o.fields["gas_density_contrast"])
        assert stars.shape == gas.shape == (o.grid.R.size, o.grid.phi.size)
        assert float(np.abs(stars.mean(axis=1) - 1.0).max()) < 1e-12, (template, seed)
        assert np.all(np.isfinite(gas)) and float(np.abs(gas.mean(axis=1) - 1.0).max()) < 1e-12, (template, seed)
        assert not np.all(stars == 1.0) and not np.all(gas == 1.0)


# --- the gate: the Fourier amplitudes ------------------------------------------------------------------------------


def fourier(field: np.ndarray, phi: np.ndarray, m: int) -> np.ndarray:
    """The complex coefficient of cos/sin m phi round each ring, on the model's own phi cells: for a field
    1 + sum A cos(m phi - alpha) it is A e^{-i alpha}, exactly for m below half the cell count."""
    return 2.0 * (field * np.exp(-1j * m * phi)[None, :]).mean(axis=1)


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("grid", [DEFAULT, SMALL], ids=["production grid", "small grid"])
def test_gate_the_amplitudes_recovered_from_the_field_are_the_published_ones(prod, template, grid):
    """"The m = 2-6 cosine amplitudes recovered from the composed field equal the published ones (the bar's m = 2
    term added at its taper) to 1e-9 on every ring, no exclusions." Phase-aware: the complex coefficient is recovered,
    the bar's own subtracted from the two-fold one, and what is left is the published amplitude at the published
    phase - modulus and argument both. Every ring, every mode, several texture seeds."""
    worst = 0.0
    for seed in TEXTURE_SEEDS:
        o = pattern_run(prod, template, grid, texture_seed=seed)
        F, R, phi = o.fields, o.grid.R, o.grid.phi
        field = np.asarray(F["pattern_density_contrast"])
        taper, phase, bar_angle = pt.bar_terms(R, float(F["pitch_angle"]), float(F["bar_half_length"]))
        bar = float(F["bar_contrast"]) * taper * np.exp(-2j * bar_angle)
        for m in pt.ARM_MODES:
            published = np.asarray(F[pt.amplitude_field(m)])
            theta = float(F[pt.phase_field(m)])
            got = fourier(field, phi, m) - (bar if m == 2 else 0.0)
            want = published * np.exp(-1j * (m * phase + theta))
            worst = max(worst, float(np.abs(np.abs(got) - published).max()), float(np.abs(got - want).max()))
            assert np.all(np.abs(np.abs(got) - published) < 1e-9), (template, seed, m)
            assert np.all(np.abs(got - want) < 1e-9), (template, seed, m)
        # And nothing else is in the field: no m = 1, no m = 7 or 8.
        for m in (1, 7, 8):
            assert float(np.abs(fourier(field, phi, m)).max()) < 1e-9, (template, seed, m)
    assert worst < 1e-13  # measured 4.3e-15 at worst over both grids, templates and seeds: 1e-9 is met at rounding


# --- the gate: nothing below zero ----------------------------------------------------------------------------------


def test_gate_no_cell_is_below_zero_on_any_seed(prod):
    """"The minimum over cells >= 0 on every seed the suite draws": sixty pattern seeds by two texture seeds for each
    template's inputs, on the production grid (the pattern stages alone are a few hundredths of a second), and the
    templates' own. Zero is the bound, not a tolerance: the saturation is a law of the radius, so the bound holds for
    every realisation of the phases. Before the saturation was ruled, 21 of 120 such galaxies had a negative cell."""
    c = constants(the_model(prod))
    lowest, saturated, drawn = math.inf, dict.fromkeys(TEMPLATES, 0), 0
    for template in TEMPLATES:
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                # The stellar field alone: the gas's ridge on the same 240 galaxies is held to its own bound in
                # tests/test_gas_pattern.py (the crest and the trough are the form's).
                o = pattern_run(prod, template, gas=False, pattern_seed=pattern_seed, texture_seed=texture_seed)
                field = np.asarray(o.fields["pattern_density_contrast"])
                lowest = min(lowest, float(field.min()))
                assert field.min() >= 0.0, (template, pattern_seed, texture_seed, float(field.min()))
                drawn += 1
            law = law_of(pattern_run(prod, template, gas=False, pattern_seed=pattern_seed, texture_seed=0), c)
            s = np.asarray(pattern_run(prod, template, gas=False, pattern_seed=pattern_seed, texture_seed=0).fields["arm_saturation"])
            assert np.array_equal(s, law.saturation) and np.all((s > 0.0) & (s <= 1.0))
            # What the saturation guarantees: the modes' amplitudes and the bar's add up to at most 1 on every ring.
            assert float((law.amplitudes.sum(axis=0) + law.bar).max()) <= 1.0 + 4e-16
            saturated[template] += int((s < 1.0).any())
    assert drawn == 240
    # Measured: the lowest cell over the 240 galaxies, and how many of each template's 60 pattern seeds saturate
    # some ring (the probe read 67 of 120 at the Milky Way's inputs: more than half, as here).
    assert lowest == pytest.approx(0.00259, abs=1e-5)
    assert saturated == {"milky_way": 35, "ngc_4414": 35}
    for template in TEMPLATES:
        assert np.asarray(pattern_run(prod, template).fields["pattern_density_contrast"]).min() > 0.3


def test_the_saturation_is_one_on_every_ring_at_both_templates_own_seeds(prod):
    c = constants(the_model(prod))
    for template, worst in (("milky_way", 0.893), ("ngc_4414", 0.790)):
        o = pattern_run(prod, template)
        assert np.all(np.asarray(o.fields["arm_saturation"]) == 1.0), template
        law = law_of(o, c)
        # The gate's prediction, held: "worst sum of the tapered amplitudes and the bar 0.893" at the default seed.
        assert float((law.tapered.sum(axis=0) + law.bar).max()) == pytest.approx(worst, abs=1e-3), template


def test_the_saturation_scales_the_modes_together_where_their_peak_would_reach_the_mean():
    """s(R) = min(1, (1 - b)/sum of the tapered amplitudes), and the amplitudes are the tapered ones times it: five
    modes of equal power peak at root five times one, so a strong arm amplitude saturates."""
    R = DEFAULT.build().R
    weights = np.ones((5, R.size))
    law = pt.mode_law(R, weights, 0.7, 0.5, 14.0, 5.0)
    assert np.allclose(law.gain, 0.2) and np.allclose(law.tapered.sum(axis=0), 0.7 * math.sqrt(5.0) * (1.0 - pt.bar_terms(R, 14.0, 5.0)[0]))
    over = law.tapered.sum(axis=0) > 1.0 - law.bar
    assert over.any() and (~over).any()
    assert np.all(law.saturation[~over] == 1.0) and np.all(law.saturation[over] < 1.0)
    assert np.allclose((law.amplitudes.sum(axis=0) + law.bar)[over], 1.0, rtol=0.0, atol=1e-15)
    assert np.array_equal(law.amplitudes, law.tapered * law.saturation)
    # The ratio between the modes is untouched: they saturate together.
    assert np.allclose(law.amplitudes[0], law.amplitudes[4])
    # No pattern at all: nothing to saturate, and the saturation is 1, not a division by zero.
    none = pt.mode_law(R, np.zeros((5, R.size)), 0.7, 0.5, 14.0, 5.0)
    assert np.all(none.saturation == 1.0) and not none.amplitudes.any()


# --- the law -------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_power_is_the_sourced_power_times_the_gain_capped_at_one(prod, template):
    """A_tot(R)^2 = A^2 min(1, sum of the weights) before the taper and the saturation, split among the modes by the
    weights; the published fields are the law's own arithmetic, bit for bit."""
    c = constants(the_model(prod))
    o = pattern_run(prod, template)
    F, R = o.fields, o.grid.R
    law = law_of(o, c)
    A = float(F["arm_contrast"])
    total = law.weights.sum(axis=0)
    assert np.all((law.weights >= 0.0) & (law.weights <= 1.0)) and total.max() > 4.0
    assert np.allclose(law.gain.sum(axis=0), np.minimum(1.0, total), rtol=1e-12, atol=0.0)
    taper = pt.bar_terms(R, float(F["pitch_angle"]), float(F["bar_half_length"]))[0]
    assert np.allclose((law.tapered**2).sum(axis=0), A * A * np.minimum(1.0, total) * (1.0 - taper) ** 2, rtol=1e-12, atol=1e-300)
    # No ring is normalised up: a ring's power never exceeds the sourced one, and where the amplifier is dead it is 0.
    assert np.all((law.tapered**2).sum(axis=0) <= A * A * (1.0 + 1e-12))
    dead = total == 0.0
    assert dead.any() and not law.amplitudes[:, dead].any()
    # Where the weights sum past one the split is by the weights; under one each mode carries A^2 w_m.
    full = total >= 1.0
    assert np.allclose(law.gain[:, full], law.weights[:, full] / total[full]) and np.array_equal(law.gain[:, ~full], law.weights[:, ~full])
    assert np.array_equal(published_amplitudes(o), law.amplitudes)
    assert np.array_equal(np.asarray(F["arm_saturation"]), law.saturation)


def test_the_local_window_is_the_existing_weight_at_the_local_x(prod):
    """X_2(R) = kappa^2 R / (2 pi G Sigma 2) with the disc's surface density per square parsec turned into per square
    kiloparsec; the shear in shear_rate's own convention; and swing_weight itself, unchanged, at that window."""
    m = the_model(prod)
    c = constants(m)
    o = pattern_run(prod)
    F, R = o.fields, o.grid.R
    kappa, sigma, v = (np.asarray(F[k]) for k in ("epicyclic_frequency", "disc_surface_density", "circular_velocity"))
    assert o.decls["disc_surface_density"].unit == "Msun/pc2" and o.decls["epicyclic_frequency"].unit == "km/s/kpc"
    x2 = pt.local_swing_x(R, kappa, sigma, c["G"])
    i = int(np.argmin(np.abs(R - 8.0)))
    assert x2[i] == pytest.approx(kappa[i] ** 2 * R[i] / (2.0 * math.pi * c["G"] * sigma[i] * 1.0e6 * 2.0), rel=1e-12)
    gamma = pt.local_shear(R, v)
    assert gamma[i] == pytest.approx(pt.shear_rate(R, v, float(R[i])), rel=1e-12)
    # The probe's table (D215's handoff): X_2 1.54 / 3.96 / 9.82 and the shear 0.63 / 1.10 / 1.19 at 2, 8 and 12 kpc.
    for r, x_want, g_want in ((2.0, 1.54, 0.63), (8.0, 3.96, 1.10), (12.0, 9.82, 1.19)):
        k = int(np.argmin(np.abs(R - r)))
        assert (x2[k], gamma[k]) == pytest.approx((x_want, g_want), abs=0.01), r
    w = pt.local_swing_weights(R, v, kappa, sigma, c["G"], c["SWING_X_LOW"], c["SWING_X_HIGH"], c["SWING_X_DEAD"],
                               c["SWING_X_FLOOR"], c["ARM_MULTIPLICITY_MAX"])
    for k in (5, i, 150):
        lo, hi = x2[k] / (gamma[k] * c["SWING_X_HIGH"]), x2[k] / (gamma[k] * c["SWING_X_LOW"])
        want = [pt.swing_weight(float(mode), lo, hi, c["SWING_X_HIGH"], c["SWING_X_DEAD"], c["SWING_X_LOW"], c["SWING_X_FLOOR"])
                for mode in pt.ARM_MODES]
        assert w[:, k].tolist() == want
    # The window's constants are the ones S26 read: the law moved no constant to move the fade.
    assert (c["SWING_X_LOW"], c["SWING_X_HIGH"], c["SWING_X_DEAD"], c["SWING_X_FLOOR"], c["ARM_MULTIPLICITY_MAX"]) == (1.0, 2.0, 3.0, 0.5, 6.0)
    # The closed set is bounded as it was: an arm number above the cap has no weight.
    capped = pt.local_swing_weights(R, v, kappa, sigma, c["G"], 1.0, 2.0, 3.0, 0.5, 4.0)
    assert not capped[3:].any() and np.array_equal(capped[:3], w[:3])
    # A shear that is not a number is read as 1, as the global window reads it; an X that is not amplifies nothing.
    flat = pt.local_swing_weights(R, np.full_like(R, 220.0), kappa, sigma, c["G"], 1.0, 2.0, 3.0, 0.5, 6.0)
    odd = pt.local_swing_weights(R, np.full_like(R, np.nan), kappa, sigma, c["G"], 1.0, 2.0, 3.0, 0.5, 6.0)
    assert np.allclose(flat, odd, rtol=0.0, atol=1e-12)  # a flat curve's shear is 1 to the gradient's rounding
    assert not pt.local_swing_weights(R, v, np.full_like(R, np.nan), sigma, c["G"], 1.0, 2.0, 3.0, 0.5, 6.0).any()


def test_the_gates_predictions_as_measured(prod):
    """D215's predictions, read on the built model (B4). Held: where the pattern ends, where the whole power ends,
    where half of it ends. **Failed, and pinned as it failed** (B5): "no ring-to-ring jump of A_tot larger than the
    largest in today's bar taper" - the fade from the whole power to none takes fourteen rings and its last steps
    are the square root's; it is built as ruled and not smoothed."""
    c = constants(the_model(prod))
    for template, last, power, full_to, half_to, jump, rings_dead in (
        ("milky_way", 14.81, 0.0153, 13.76, 14.14, 0.1426, 202), ("ngc_4414", 11.51, 0.0508, 10.84, 11.06, 0.2253, 246),
    ):
        o = pattern_run(prod, template)
        R = o.grid.R
        law = law_of(o, c)
        total = law.weights.sum(axis=0)
        share = law.gain.sum(axis=0)  # A_tot^2 / A^2
        alive = np.nonzero(total > 0.0)[0]
        assert R[alive.max()] == pytest.approx(last, abs=0.005) and share[alive.max()] == pytest.approx(power, abs=5e-5), template
        assert int((total <= 0.0).sum()) == rings_dead and np.all(total[alive.max() + 1:] == 0.0), template
        assert R[np.nonzero(total >= 1.0)[0].max()] == pytest.approx(full_to, abs=0.005), template
        assert R[np.nonzero(share >= 0.5)[0].max()] == pytest.approx(half_to, abs=0.005), template
        assert float(np.abs(np.diff(np.sqrt(share))).max()) == pytest.approx(jump, abs=5e-4), template
        # The bar's taper, for the comparison the prediction made: its largest ring-to-ring step is far smaller.
        taper = pt.bar_terms(R, float(o.fields["pitch_angle"]), float(o.fields["bar_half_length"]))[0]
        assert float(np.abs(np.diff(taper)).max()) < 0.04 < jump  # 0.022 and 0.033: the bar's taper per ring
    # Every Milky Way ring inside 12 kpc carries the whole A^2.
    mw = law_of(pattern_run(prod, "milky_way"), c)
    assert np.all(mw.weights.sum(axis=0)[pattern_run(prod).grid.R < 12.0] >= 1.0)


# --- the label -----------------------------------------------------------------------------------------------------


def test_arm_multiplicity_is_the_mode_with_the_most_mass_weighted_power(prod):
    """Kept under its name, as a label: the m whose sum over rings of Sigma R dR A_m^2 is greatest, a tie to the
    lower m; not a number for a disc with no arms. It was the drawn 4 for both templates at S55."""
    for template, label, shares in (("milky_way", 3.0, (0.2500, 0.2718, 0.2146, 0.1526, 0.1110)),
                                    ("ngc_4414", 2.0, (0.4591, 0.3054, 0.1326, 0.0585, 0.0445))):
        o = pattern_run(prod, template)
        F, R = o.fields, o.grid.R
        amplitudes = published_amplitudes(o)
        power = (np.asarray(F["disc_surface_density"]) * R * np.gradient(R))[None, :] * amplitudes**2
        assert F["arm_multiplicity"] == label == float(pt.ARM_MODES[int(np.argmax(power.sum(axis=1)))]), template
        assert (power.sum(axis=1) / power.sum()).tolist() == pytest.approx(shares, abs=5e-4), template
        assert pt.dominant_mode(R, F["disc_surface_density"], amplitudes) == label
    R = DEFAULT.build().R
    sigma = np.exp(-R / 2.6)
    tie = np.zeros((5, R.size))
    tie[1] = tie[3] = 0.2
    assert pt.dominant_mode(R, sigma, tie) == 3.0  # a tie goes to the lower arm number
    assert math.isnan(pt.dominant_mode(R, sigma, np.zeros((5, R.size))))  # no arms, no arm number (D164)
    assert math.isnan(pt.dominant_mode(R, sigma, np.full((5, R.size), np.nan)))
    assert o.decls["arm_multiplicity"].label == "Arm number carrying the most power"


def test_the_effective_arm_number_is_m_for_one_mode_and_does_not_know_the_phases(prod):
    amplitudes = np.zeros((5, 3))
    amplitudes[2] = 0.3
    assert pt.effective_arm_number(amplitudes).tolist() == [4.0, 4.0, 4.0]
    assert np.all(np.isnan(pt.effective_arm_number(np.zeros((5, 3)))))
    # At the defaults: 2.64 at 2 kpc, 3.47 at 8, 4.88 at 12 - and the same under another texture seed.
    for seed in (None, 5):
        o = pattern_run(prod, texture_seed=seed)
        m_eff = pt.effective_arm_number(published_amplitudes(o))
        R = o.grid.R
        got = [float(m_eff[int(np.argmin(np.abs(R - r)))]) for r in (2.0, 8.0, 12.0)]
        assert got == pytest.approx([2.643, 3.466, 4.881], abs=2e-3)
        gas = compose.gas_pattern(o.fields, R, constants(the_model(prod)))
        assert np.allclose(gas.effective_arm_number(R)[np.isfinite(m_eff)], m_eff[np.isfinite(m_eff)], rtol=1e-12)


def model_sources() -> list[Path]:
    return sorted(PACKAGE.rglob("*.py"))


def test_the_fence_nothing_composes_or_places_from_arm_multiplicity(prod):
    """Gate ruling 4: "nothing composes a field from ``arm_multiplicity``; every reader is listed at close and shown
    to read it as a label." Held three ways. No stage of either model requires it. No module of the model but the one
    that publishes it holds its name as a string at all, so nothing looks it up - the pattern objects are built from
    ``PATTERN_READS`` and ``GAS_PATTERN_READS``, which do not hold it. And the viewer's source does not name it: it
    reaches a reader only through the metadata and ``/api/arrays``, as every scalar does, which is a label's reach."""
    models, impls_, _ = prod
    for m in models:
        readers = [sid for _, sid in m.stages if "arm_multiplicity" in impls_.get(sid).requires + impls_.get(sid).requires_optional]
        assert readers == [], readers
        publishers = [sid for _, sid in m.stages if "arm_multiplicity" in impls_.get(sid).published_names]
        assert publishers == ["pattern"]
    assert "arm_multiplicity" not in pt.PATTERN_READS and "arm_multiplicity" not in gp.GAS_PATTERN_READS
    named: dict[str, int] = {}
    for path in model_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {id(n.body[0].value) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body
                      and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
        count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                    and "arm_multiplicity" in n.value and id(n) not in docstrings)
        if count:
            named[path.relative_to(PACKAGE).as_posix()] = count
    # The declaration's name and the key the stage publishes it under: two strings, one module.
    assert named == {"stages/pattern.py": 2}, named
    # A pattern object has no arm number to read: its numbers are the modes'.
    assert not {"m", "arm"} & set(pt.ArmPattern.__slots__) and "m" not in gp.GasPattern.__slots__
    viewer = [p for d in ("frontend/src", "interface") for p in (ROOT / d).rglob("*") if p.suffix in (".ts", ".tsx", ".js", ".mjs")]
    assert len(viewer) > 20
    assert [p.name for p in viewer if "arm_multiplicity" in p.read_text(encoding="utf-8")] == []


# --- the regression: one mode is S55's field -----------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("m", [4, 2])
def test_regression_one_mode_is_the_field_s55_published(prod, template, m):
    """"With one mode - one m, phase 0, the amplifier's weight 1 on every ring - the stellar field is S55's
    ``pattern_density_contrast`` exactly and the gas field is S51's ``gas_density_contrast`` to 1e-9", on each
    template's own scalars, for the arm number S55 drew (4) and for 2.

    The S55 fields are ``tests/s55_patterns.py``'s, a frozen copy of S55's two classes; the reference holds the
    digests of what S55's own classes made (for m = 4, the published fields), and the copy is them bit for bit."""
    c = constants(the_model(prod))
    grid = DEFAULT.build()
    R, phi = grid.R, grid.phi
    f = layer_reference.single_mode_scalars(template)
    old_stars, old_gas = layer_reference.single_mode_fields(template, float(m))
    held = layer_reference.load()["single_mode"][template][f"m{m}"]
    assert layer_reference.value_digest(old_stars) == held["stars"] and layer_reference.value_digest(old_gas) == held["gas"]

    stars, gas = single_mode(R, m, f, c)
    new_stars, new_gas = stars.contrast(R, phi), gas.contrast(R, phi)
    # The stars: exactly - the same bytes.
    assert new_stars.tobytes() == old_stars.tobytes()
    # The gas: to 1e-9, **through the general method** - the ridge by rank, the rank the measure of psi's superlevel
    # set from the refined crossings (D215, gate ruling 7), with no one-mode case in the code. Measured 1.4e-12 at
    # worst: each crossing is bounded to 1e-12 in chi. (The first turn's exponential of the modes' sum read 3e-15
    # here and spiked on several modes.)
    assert float(np.abs(new_gas - old_gas).max()) < 1e-9
    assert float(np.abs(new_gas - old_gas).max()) < 1e-11
    # The ridge's amplitude is S51's at every radius, and the unit amplitudes are 1: psi is cos m chi.
    a_old = s55.gas_amplitude(R, f["gas_arm_contrast"], float(m), f["pitch_angle"], c["GAS_ARM_WIDTH"], c["GAS_ARM_MASK_WIDTH"])
    assert float(np.abs(gas.amplitude(R) - a_old).max()) < 1e-13
    assert np.all(gas.unit[pt.ARM_MODES.index(m)] == 1.0) and gas.unit.sum() == R.size
    # The same pattern through compose's own door, from a mapping of fields at phase 0.
    fields = {**{n: stars.amplitudes[k] for k, n in enumerate(pt.AMPLITUDE_FIELDS)}, **dict.fromkeys(pt.PHASE_FIELDS, 0.0),
              "bar_contrast": f["bar_contrast"], "pitch_angle": f["pitch_angle"], "bar_half_length": f["bar_half_length"],
              "arm_contrast": f["arm_contrast"], "gas_arm_contrast": f["gas_arm_contrast"]}
    assert pt.ArmPattern.from_fields(fields, R).contrast(R, phi).tobytes() == old_stars.tobytes()
    assert float(np.abs(gp.GasPattern.from_fields(fields, R, c).contrast(R, phi) - old_gas).max()) < 1e-11


def test_regression_the_published_s55_fields_are_the_m_4_oracle(prod):
    """What ties the frozen copy to S55: for the drawn arm number its two fields are the ones S55 published - the
    digests ``tests/layer_reference_s54.json`` held for the layer-on run until S56, carried here."""
    held = layer_reference.load()["single_mode"]
    assert held["milky_way"]["m4"] == {
        "stars": "<f8[400, 360]:7c90330760ec53ab57e1c96203a236b2a79fa54c6994284574a8471cd514a226",
        "gas": "<f8[400, 360]:eb04c184a7de24db197344cdba06807694a32c54b41a05277166008e13b206d1",
    }
    assert held["ngc_4414"]["m4"] == {
        "stars": "<f8[400, 360]:28b5ab04cc358b7b4f3dbc7b1e5f764a6011c6fecd075f612595e01c74ab3e91",
        "gas": "<f8[400, 360]:5f5d8835e4efcbad39faa963a860787e07c1752a17f8901afd64e0ab2edf0466",
    }
    assert set(held) == set(TEMPLATES) and all(set(v) == {"m4", "m2"} for v in held.values())


def test_the_streams_that_stay_are_the_numbers_s55_drew(prod):
    """"The arm number's draw retires ... and no other stream's path changes": the pitch, the fast-bar ratio (through
    the corotation radius and the pattern speed) and the two amplitudes are S55's bits, on the default seed and on
    ``ngc_4414``'s - read against the reference captured before the law moved."""
    held = layer_reference.load()["fields"]
    names = ("pitch_angle", "arm_contrast", "bar_contrast", "bar_corotation_radius", "bar_pattern_speed",
             "bar_half_length", "gas_arm_contrast", "swing_x", "swing_arm_min", "swing_arm_max", "arm_contrast_mean")
    for template in TEMPLATES:
        for layer in (True, False):
            o = run(the_model(prod), inputs_of(template), only=names, layer=layer)
            label = layer_reference.label(DEFAULT_MODEL, template)
            assert [n for n in names if layer_reference.value_digest(o.fields[n]) != held[label][n]] == [], (template, layer)
    # And the retired stream is not read: the stage's source names no "arms" stream.
    source = (PACKAGE / "stages" / "pattern.py").read_text(encoding="utf-8")
    streams = [n.args[1].value for n in ast.walk(ast.parse(source))
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "rng" and len(n.args) > 1]
    assert streams == ["fast_bar", "pitch", "arm_contrast", "bar_contrast"]


# --- the realisation: the phases -----------------------------------------------------------------------------------


def test_the_phases_are_uniform_draws_on_the_texture_seed_one_stream_per_mode(prod):
    m = the_model(prod)
    seen = []
    for seed in range(200):
        F = run(m, {"texture_seed": seed}, SMALL, only=pt.PHASE_FIELDS).fields
        phases = [float(F[n]) for n in pt.PHASE_FIELDS]
        # The stream is named by the slot, "phase" and the mode: adding a mode later moves no other mode's phase.
        want = [2.0 * math.pi * float(_seeds.rng(seed, "arm_phases", "phase", mode).random()) for mode in pt.ARM_MODES]
        assert phases == want and all(0.0 <= p < 2.0 * math.pi for p in phases), seed
        seen.append(phases)
    seen = np.array(seen)
    # Uniform on the circle: no preferred value (the mean direction of 200 draws is under 3/sqrt(200)), and the
    # modes are drawn apart (their phases are uncorrelated).
    assert np.all(np.abs(np.exp(1j * seen).mean(axis=0)) < 0.2)
    assert np.all(np.abs(np.corrcoef(seen.T) - np.eye(5)) < 0.25)
    assert len({tuple(row) for row in seen}) == 200
    for d in arm_phases.ARM_MODE_PHASES:
        assert d.provenance == "synthetic" and d.unit == "rad" and d.kind.value == "scalar"
        assert "Uniform on the circle" in d.statistic and "[inferred]" in d.statistic and "absence of a measured preference" in d.statistic
        assert "self-gravitating" in d.stands_in_for and "Every ring's mean and every amplitude" in d.conserves
    assert [d.name for d in arm_phases.ARM_MODE_PHASES] == list(pt.PHASE_FIELDS) == [f"arm_mode_phase_{k}" for k in range(2, 7)]


def test_rerolling_the_pattern_seed_leaves_the_phases_and_rerolling_the_texture_seed_leaves_the_law(prod):
    m = the_model(prod)
    base = run(m, {"pattern_seed": 0, "texture_seed": 3}, only=PATTERN_FIELDS).fields
    for seed in range(1, 6):
        other = run(m, {"pattern_seed": seed, "texture_seed": 3}, only=PATTERN_FIELDS).fields
        assert [other[n] for n in pt.PHASE_FIELDS] == [base[n] for n in pt.PHASE_FIELDS]
        assert other["arm_contrast"] != base["arm_contrast"] and other["pitch_angle"] != base["pitch_angle"]
    for seed in (4, 5, 6):
        other = run(m, {"pattern_seed": 0, "texture_seed": seed}, only=PATTERN_FIELDS).fields
        assert all(other[n] != base[n] for n in pt.PHASE_FIELDS)
        for n in LAW_FIELDS:
            assert np.array_equal(np.asarray(other[n]), np.asarray(base[n])), n
        for n in ("pattern_density_contrast", "gas_density_contrast"):
            assert not np.array_equal(other[n], base[n]), n


def test_with_the_layer_off_the_phases_are_not_numbers_and_the_stream_is_never_drawn(prod, monkeypatch):
    """"A synthetic quantity is not realised, and an unrealised quantity is NaN; the field list is the same on and
    off; 0 would claim a draw that was not made" - and the stage does not touch its stream: compose does not call the
    draw. The law's fields are the same bits on and off."""
    m = the_model(prod)
    on, off = pattern_run(prod, layer=True), pattern_run(prod, layer=False)
    assert set(on.fields) == set(off.fields)
    for n in pt.PHASE_FIELDS:
        assert math.isnan(off.fields[n]) and math.isfinite(on.fields[n]), n
    for n in LAW_FIELDS:
        a, b = np.asarray(on.fields[n]), np.asarray(off.fields[n])
        assert a.dtype == b.dtype and a.tobytes() == b.tobytes(), n
    assert np.all(np.asarray(off.fields["pattern_density_contrast"]) == 1.0) and np.all(np.asarray(off.fields["gas_density_contrast"]) == 1.0)
    # No draw: with the layer off the stage's context is never asked for a generator, nor for the seed.
    calls: list[tuple] = []
    real = Context.rng

    def counting(self, seed_name, *path):
        calls.append((self.stage.id, seed_name, *path))
        return real(self, seed_name, *path)

    monkeypatch.setattr(Context, "rng", counting)
    run(m, grid=SMALL, only=pt.PHASE_FIELDS, layer=False)
    assert calls == []
    run(m, grid=SMALL, only=pt.PHASE_FIELDS, layer=True)
    assert calls == [("arm_phases", "texture_seed", "phase", mode) for mode in pt.ARM_MODES]
    calls.clear()
    whole_off = run(m, grid=SMALL, only=PATTERN_FIELDS, layer=False)
    assert not [c for c in calls if c[1] == "texture_seed"] and {c[0] for c in calls} == {"pattern"}
    assert compose.stellar_pattern(whole_off.fields, whole_off.grid.R) is None
    assert compose.realise_scalars(whole_off.fields, ("a", "b"), lambda: 1 / 0) .keys() == {"a", "b"}
    assert compose.realise_scalars(pattern_run(prod, grid=SMALL).fields, ("a",), lambda: {"a": 2.0}) == {"a": 2.0}


# --- evaluable at a point ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_pattern_objects_are_the_published_fields_and_evaluable_at_a_point(prod, template):
    """Rule 1c-5 (D60): the same function at a grid cell, at a point, over a sector. At the grid radii the pattern is
    the published field exactly; between them the amplitudes are linear in R."""
    c = constants(the_model(prod))
    o = pattern_run(prod, template)
    F, R, phi = o.fields, o.grid.R, o.grid.phi
    stars, gas = compose.stellar_pattern(F, R), compose.gas_pattern(F, R, c)
    assert not stars.flat and not gas.flat
    assert stars.contrast(R, phi).tobytes() == np.asarray(F["pattern_density_contrast"]).tobytes()
    # The gas's published field is the law at the cells' centres over each ring's sampled mean, where that has left
    # 1 (a ranked ridge's does, by under 1e-3: tests/test_gas_pattern.py).
    law = gas.contrast(R, phi)
    assert np.allclose(law / law.mean(axis=1, keepdims=True), np.asarray(F["gas_density_contrast"]), rtol=0.0, atol=1e-11)
    assert float(np.abs(law.mean(axis=1) - 1.0).max()) < 1e-3
    for shape in (stars, gas):
        on_grid = shape.contrast(R, phi)
        assert np.allclose(shape.contrast_at(R[:, None], phi[None, :]), on_grid, rtol=0.0, atol=1e-12)
        idx = np.array([5, 77, 150, 190]), np.array([0, 91, 180, 359])
        assert np.allclose(shape.contrast_at(R[idx[0]], phi[idx[1]]), on_grid[idx], rtol=0.0, atol=1e-12)
    # The amplitudes at a radius between two rings: linear in R between the published values.
    k = 100
    mid = 0.25 * R[k] + 0.75 * R[k + 1]
    amplitudes = published_amplitudes(o)
    assert np.allclose(stars.amplitudes_at(np.array([mid]))[:, 0], 0.25 * amplitudes[:, k] + 0.75 * amplitudes[:, k + 1], rtol=1e-12)
    assert np.array_equal(stars.amplitudes_at(R), amplitudes)
    # Sector means: analytic for the stars (the modes' own integrals), by the ridge's series for the gas; they
    # average to 1 round the ring and are the dense average of the point function over each sector - for the stars
    # to the dense average's own error; for the gas to the series' accuracy on a ridge with corners, **pinned as
    # measured: 1.2e-3 of the ring's mean at worst over thirty-two sectors, five radii and both templates** with
    # the 1024 samples the series is taken from (D215: the number of samples is not changed to hide it).
    edges = np.linspace(0.0, 2.0 * np.pi, 33)
    for shape in (stars, gas):  # past the last ring with a mode, and past the bar: every sector alike, exactly
        assert np.all(shape.sector_means(20.0, edges) == 1.0)
    assert gp.HARMONIC_SAMPLES == 1024
    worst = 0.0
    for radius in (1.0, 3.0, 6.0, 9.0, 11.0):
        for shape, tolerance in ((stars, 1e-8), (gas, 2e-3)):
            means = shape.sector_means(radius, edges)
            assert float(means.mean()) == pytest.approx(1.0, abs=1e-12), radius
            dense = []
            for a, b in zip(edges[:-1], edges[1:]):
                x = a + (np.arange(4000) + 0.5) * (b - a) / 4000
                dense.append(float(shape.contrast_at(np.full_like(x, radius), x).mean()))
            error = float(np.abs(means - np.array(dense)).max())
            assert error <= tolerance, (radius, error)
            assert means.max() > 1.0 > means.min()
            worst = max(worst, error) if shape is gas else worst
    assert 3e-4 < worst < 1.5e-3


def test_a_pattern_with_nothing_to_place_is_flat():
    R = DEFAULT.build().R
    zero, none = (0.0,) * 5, np.zeros((5, R.size))
    assert pt.ArmPattern(R, none, zero, 0.0, 13.5, 5.2).flat
    assert not pt.ArmPattern(R, none, zero, 0.3, 13.5, 5.2).flat  # the bar alone is a pattern
    some = none.copy()
    some[2] = 0.3
    assert not pt.ArmPattern(R, some, zero, 0.0, 13.5, 5.2).flat
    # A pattern the grid could not resolve, or the layer did not realise, stays axisymmetric.
    assert pt.ArmPattern(R, some, zero, float("nan"), float("nan"), 5.2).flat
    assert pt.ArmPattern(R, some, (float("nan"),) * 5, 0.3, 13.5, 5.2).flat
    with pytest.raises(ValueError, match="5 modes"):
        pt.ArmPattern(R, some[:3], zero, 0.3, 13.5, 5.2)
    unit = np.where(some > 0, 1.0, 0.0)
    assert gp.GasPattern(R, unit, zero, 2.73, float("nan"), float("nan"), 5.2, 0.17, 1.5).flat
    assert gp.GasPattern(R, unit, zero, 1.0, 0.0, 13.5, 5.2, 0.17, 1.5).flat          # a ratio of 1 and no bar
    assert gp.GasPattern(R, none, zero, 2.73, 0.0, 13.5, 5.2, 0.17, 1.5).flat         # no stellar mode and no bar
    assert not gp.GasPattern(R, unit, zero, 2.73, 0.0, 13.5, 5.2, 0.17, 1.5).flat
    assert not gp.GasPattern(R, none, zero, 2.73, 0.3, 13.5, 5.2, 0.17, 1.5).flat     # the bar's term alone
    # Fields that hold no pattern give none.
    assert pt.ArmPattern.from_fields({"bar_contrast": 0.3}, R) is None
    assert gp.GasPattern.from_fields({"bar_contrast": 0.3}, R, {"GAS_ARM_WIDTH": 0.17, "GAS_ARM_MASK_WIDTH": 1.5}) is None
