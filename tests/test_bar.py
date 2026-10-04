"""The bar: a presence, a body, its lanes, and the two-armed mode's phase (S58, BUILD_III Phase P3; DECISIONS.md D217).

Until S58 every galaxy had a bar and the bar was one cosine. A conditional gate ruled the rest (D217, items 1-10),
and this file holds the build to it, in the gate's order:

- **the predictions** (B4), read before they were judged and recorded here with the as-built numbers - one of them
  failed (the body's share of the disc: 0.1015 against 0.110) and is pinned as it fails, nothing changed to make it
  hold (B5); the A₂ maximum's place misses the stacks' 0.76-0.94 a, as predicted;
- **the gate**: the stellar ring means, nothing clipped; the stellar contrast positive on every suite seed; the m = 2
  amplitude of the published field's bar part equal to the drawn amplitude; the gas with its lanes; an unbarred
  galaxy that leaks no NaN;
- **the body and the presence re-derived by hand** from the published fields, with this file's arithmetic and no
  function of the model's modules: the body's profile, the ring's share, the published field's cells, the A₂
  profile, the mass share; Fujii's time for both templates and the disc's age by quadrature;
- **the lanes**: the geometry by hand, the leading side from the trailing winding, the ratio of means on every ring,
  conservation, and the lane's peak (a check against one simulation's factor of ten);
- **the gate's follow-up on the build** (the same decision): the gas the star formation law reads - the lanes'
  excess spread over the bar's footprint, by hand; the two reworded checks (the bar part's A₂ maximum, with the
  whole field's recorded beside it; g ≥ 0 and 0 only where the response underflows, at the corner where it does);
  and three consequences recorded as read - the saturation ends with the body, the lanes end in a cliff, no
  nuclear ring is built.

**Read on 2026-10-04** (the production grid). The Milky Way template: B = 0.28926, the body's share of the
checkpoint-1 disc 0.10146, β at most 0.3903 (0.71 kpc), the A₂ maximum B at 2.1375 kpc = 0.4103 a, A₂(0.85 a)
0.0444 (0.1536 B), the body's contrast at least 0.7641 (1.91 kpc), the depth 0.8158 B; the lanes from (5.2097 kpc,
on the bar's axis) to 0.5210 kpc on its minor axis, radius of curvature 4.5302 kpc, the base 0.38462 where the
footprint fills the ring (R < 2.084 kpc), L up to 7.06 times the ring's mean (3.34 kpc) and the published gas up
to 6.66 (2.06 kpc). The shape is scale-free - the bar is two scale lengths of an exponential disc - so every barred
suite seed reads the same peak radius, 0.4103 a, and the same share per unit amplitude, 0.3508.
``ngc_4414``: pinned unbarred; its bar numbers NaN; ``bar_formation_time`` 0.9055 Gyr against a disc 5.04 Gyr old
(the Milky Way's 1.4565 against 9.62), so the criterion bars it and the pin overrules the criterion.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core.grids import DEFAULT, GridSpec
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt

ROOT = Path(__file__).resolve().parents[1]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
TEMPLATES = ("milky_way", "ngc_4414")
# What an unbarred galaxy publishes as NaN (D217 item 3; D164), and nothing else of it is.
BAR_NUMBERS = ("bar_half_length", "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_contrast",
               "bar_mass_share", "bar_corotation_radius", "bar_pattern_speed")
STELLAR = ("pattern_density_contrast", *pt.PATTERN_READS, "arm_saturation", "arm_contrast", "bar_present",
           "bar_formation_time", "disc_dominance", "bar_corotation_radius", "bar_pattern_speed")
PATTERN = (*STELLAR, "gas_density_contrast", "star_formation_gas_contrast", *gm.GAS_PATTERN_READS)
# The constants as the ruling states them, written here; the model's are held to them (the tags are level0's).
T0_HAND, S_HAND = 0.146, 1.38          # Fujii et al. 2018, eq. 11: t_b = T0 exp(S / f_d), Gyr
Q_HAND, C_HAND, N_HAND = 0.4, 3.0, 2.0  # the body: axis ratio, boxiness, the Ferrers exponent
KAPPA_A_HAND, RING_HAND, RATIO_HAND, WIDTH_HAND = 1.15, 0.10, 2.6, 0.10  # the lanes; the last an unsourced placeholder
H0_HAND, OMEGA_M_HAND = 0.07, 0.3      # km/s/kpc; flat
GYR_PER_KPC_PER_KMS = 3.0856775814913673e16 / 3.15576e16
_RUNS: dict[object, object] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def inputs_of(template: str, pinned: bool = True, **more) -> dict:
    given = templates.overrides(templates.TEMPLATES[template])
    if not pinned:
        given = {k: v for k, v in given.items() if k not in templates.pinned(templates.TEMPLATES[template])}
    return {**given, **more}


def template_run(prod, template: str, pinned: bool = True):
    """A template's pattern fields alone on the production grid (rule D4), once per session."""
    key = (template, pinned)
    if key not in _RUNS:
        _RUNS[key] = run(the_model(prod), inputs_of(template, pinned), only=PATTERN)
    return _RUNS[key]


def hand_arms(F, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """The arm modes at the cells' centres from the published amplitudes, phases and pitch: this file's arithmetic."""
    cot = 1.0 / math.tan(math.radians(float(F["pitch_angle"])))
    chi = phi[None, :] - (np.log(R) * cot)[:, None]
    out = np.zeros((R.size, phi.size))
    for m in (2, 3, 4, 5, 6):
        out += np.asarray(F[f"arm_mode_amplitude_{m}"])[:, None] * np.cos(m * chi - float(F[f"arm_mode_phase_{m}"]))
    return out


def hand_fourier(values: np.ndarray, phi: np.ndarray, m: int = 2) -> np.ndarray:
    """|2 <v e^{-i m phi}>| round each ring on equal cells: the m-fold amplitude, this file's arithmetic."""
    return 2.0 * np.abs((values * np.exp(-1j * m * phi)[None, :]).mean(axis=1))


def hand_cell_means(profile: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """The mean, over each interval [lo_j, hi_j], of the periodic piecewise-linear function through ``profile`` on a
    ring's cell centres -π + (k + ½) 2π/n: the trapezoid rule on the function's own breakpoints, which is its exact
    integral. This file's arithmetic - no function of ``gas_response``, ``pattern`` or ``gas_pattern``."""
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


def hand_body(R: np.ndarray, a: float) -> tuple[np.ndarray, np.ndarray]:
    """(ψ, p): the body's unit profile (1 − m²)ⁿ inside m = 1 on 1440 cells' centres ψ of every ring, in the bar's
    frame, with the ruling's q, c and n - written here."""
    n = 1440
    psi = -math.pi + (np.arange(n) + 0.5) * (2.0 * math.pi / n)
    x, y = R[:, None] * np.cos(psi)[None, :], R[:, None] * np.sin(psi)[None, :]
    m = ((np.abs(x) / a) ** C_HAND + (np.abs(y) / (Q_HAND * a)) ** C_HAND) ** (1.0 / C_HAND)
    return psi, np.where(m < 1.0, (1.0 - np.minimum(m, 1.0) ** 2) ** N_HAND, 0.0)


def hand_age(z: float) -> float:
    """The lookback time to redshift z in Gyr for flat matter + Λ, by quadrature of dt = dz / ((1 + z) H(z)):
    Simpson's rule on 20 000 intervals in ln(1 + z). Not the model's closed form."""
    u = np.linspace(0.0, math.log(1.0 + z), 20001)
    e = np.sqrt(OMEGA_M_HAND * np.exp(3.0 * u) + (1.0 - OMEGA_M_HAND))
    f = 1.0 / e  # dt = du / H(u), u = ln(1 + z)
    h = u[1] - u[0]
    integral = h / 3.0 * (f[0] + f[-1] + 4.0 * f[1:-1:2].sum() + 2.0 * f[2:-1:2].sum())
    return float(integral) / H0_HAND * GYR_PER_KPC_PER_KMS


# --- the constants are the ruling's ----------------------------------------------------------------------------------


def test_the_constants_are_the_ruling_s_and_carry_their_tags(prod):
    """D217's numbers enter as level-0 constants, each with the reading's tag; the lane's width says what it is."""
    m = the_model(prod)
    c = constants(m)
    held = {"BAR_FORMATION_TIME_SCALE": T0_HAND, "BAR_FORMATION_EXPONENT": S_HAND, "BAR_AXIS_RATIO": Q_HAND,
            "BAR_BOXINESS": C_HAND, "BAR_PROFILE_INDEX": N_HAND, "BAR_LANE_CURVATURE": KAPPA_A_HAND,
            "NUCLEAR_RING_RATIO": RING_HAND, "BAR_GAS_RATIO": RATIO_HAND, "BAR_LANE_WIDTH": WIDTH_HAND,
            "H0": H0_HAND, "OMEGA_M": OMEGA_M_HAND}
    assert {k: c[k] for k in held} == held
    about = {k: m.constants[k].about for k in held}
    assert m.constants["BAR_FORMATION_TIME_SCALE"].unit == "Gyr"
    fujii = "[verified: Fujii et al. 2018, MNRAS 477, 1451, arXiv:1712.00058, eqs 6, 9, 11, §3.3, https://ar5iv.labs.arxiv.org/html/1712.00058]"
    for k in ("BAR_FORMATION_TIME_SCALE", "BAR_FORMATION_EXPONENT"):
        text = " ".join(about[k].split())
        assert fujii in text and "0.146 +/- 0.079" in text and "1.38 +/- 0.17" in text
        assert "Q-dependence is unmodelled" in text and "0.27" in text and "8.8 Gyr" in text
    for k, source in (("BAR_AXIS_RATIO", "Gadotti 2011, MNRAS 415, 3308"), ("BAR_BOXINESS", "Gadotti 2011, MNRAS 415, 3308"),
                      ("BAR_PROFILE_INDEX", "Salo et al. 2015, ApJS 219, 4"), ("BAR_LANE_CURVATURE", "Sánchez-Menguiano et al. 2015, MNRAS 450, 2670"),
                      ("NUCLEAR_RING_RATIO", "Kim, Seo & Kim 2012, ApJ 758, 14"), ("BAR_GAS_RATIO", "Querejeta et al. 2021, A&A 656, A133")):
        assert "[verified: " + source in about[k], k
    assert "Comerón et al. 2010, MNRAS 402, 2462" in about["NUCLEAR_RING_RATIO"]
    assert "11.51" in about["BAR_GAS_RATIO"] and "4.492" in about["BAR_GAS_RATIO"]
    width = about["BAR_LANE_WIDTH"]
    assert "**An unsourced placeholder**" in width and "no source read gives a lane width" in width and "debt" in width
    assert "[verified:" not in width and "[inferred]" in width
    # The reading's own words, where a tag quotes them.
    reading = " ".join((ROOT / "docs" / "READING_BAR.md").read_text(encoding="utf-8").split())
    for quoted in ("Median of the 16 lane values = 1.15 [derived by this reader; not printed]", "Not found in anything read: a lane width",
                   "t_b = (0.146 ± 0.079) exp[(1.38 ± 0.17)/f_d]", "11.51", "4.492", "Fujii et al. 2018, MNRAS 477, 1451, arXiv:1712.00058, eqs 6, 9, 11, §3.3"):
        assert quoted in reading, quoted


# --- the predictions (B4) ----------------------------------------------------------------------------------------


def test_the_gate_s_predictions_as_measured(prod):
    """D217's predictions, read before the build was judged and recorded with the as-built numbers. Nothing was
    changed to make one hold.

    The Milky Way template: "B = 0.289 → the body's share of the cp1 disc 0.110, β_max ≈ 0.39, A₂^max = 0.289 at
    ≈ 0.42 a = 2.2 kpc (today's cosine peaks at 0), A₂(0.85 a) ≈ 0.046, the minimum stellar contrast before the
    arms ≈ 0.77; lanes from (5.21 kpc, φ_bar) to 0.52 kpc with radius of curvature 4.5 kpc; the gas's base inside
    the footprint-filled rings (R < 2.1 kpc) 0.385; rows 15-17 unchanged". ``ngc_4414``: "unbarred, the bar's
    fields NaN, arms to the centre; its two disclosed checks over 6-10 kpc unchanged to three figures (1.881 and
    0.512); t_b 0.91 Gyr published beside the pin. Both A₂ peak radii miss 0.76-0.94 a."

    **As built.** Held: β_max 0.3903; A₂^max = B to rounding at 2.1375 kpc = 0.4103 a; the minimum stellar contrast
    before the arms 0.7641; the lanes' ends and their radius of curvature 4.5302 kpc; the base 0.38462; rows 15-17;
    ``ngc_4414`` unbarred with t_b 0.9055 Gyr (the Milky Way 1.4565). **A₂(0.85 a) reads 0.0444** against "≈ 0.046"
    (3.5 % under; 0.0408 on the grid ring nearest 0.85 a). **Failed: the body's share of the checkpoint-1 disc is
    0.1015, not 0.110** - 8 % under. The prediction scaled the handoff's probe (a share of 0.10 for an A₂ maximum
    of 0.262), and that probe's Σ was not the checkpoint-1 total disc the ruling names; on the ruled Σ a share of
    0.10 gives 0.285. Pinned as it fails; nothing is tuned to it (D217 forbids "tuning the share ... to land a
    check"). **Missed, as predicted: the A₂ peak sits at 0.41 a** (``ngc_4414``'s disc, were it barred: 0.42 a),
    where the S⁴G stacks peak at 0.76-0.94 a; the bulge's dilution of the inner amplitude in the stacks is the
    named suspect. ``ngc_4414``'s two disclosed gas checks are in ``tests/test_gas_pattern.py``."""
    o = template_run(prod, "milky_way")
    F, R, phi = o.fields, o.grid.R, o.grid.phi
    a, B = float(F["bar_half_length"]), float(F["bar_contrast"])
    assert (a, B) == pytest.approx((5.2097, 0.28926), abs=5e-5)
    stars = compose.stellar_pattern(F, R)
    # "the body's share of the cp1 disc 0.110": FAILED - 0.1015.
    assert float(F["bar_mass_share"]) == pytest.approx(0.10146, abs=2e-5)
    assert abs(float(F["bar_mass_share"]) - 0.110) > 0.008
    # "β_max ≈ 0.39": held.
    beta = stars.ring_share
    assert float(beta.max()) == pytest.approx(0.3903, abs=2e-4) and float(R[int(np.argmax(beta))]) == pytest.approx(0.7125, abs=1e-6)
    # "A₂^max = 0.289 at ≈ 0.42 a = 2.2 kpc": held (0.4103 a = 2.1375 kpc, the grid ring).
    part = np.asarray(F["pattern_density_contrast"]) - 1.0 - hand_arms(F, R, phi)
    a2 = hand_fourier(part, phi)
    inside = R < a
    peak = int(np.argmax(np.where(inside, a2, -1.0)))
    assert float(a2[peak]) == pytest.approx(B, abs=1e-12) and (float(R[peak]), float(R[peak]) / a) == pytest.approx((2.1375, 0.4103), abs=1e-4)
    assert not 0.76 <= float(R[peak]) / a <= 0.94  # the recorded miss: the stacks' maximum sits at 0.76-0.94 a
    # "A₂(0.85 a) ≈ 0.046": 0.0444, read at 0.85 a between the two grid rings (0.0408 on the nearer one).
    assert float(np.interp(0.85 * a, R, a2)) == pytest.approx(0.04444, abs=2e-5)
    assert float(a2[int(np.argmin(np.abs(R - 0.85 * a)))]) == pytest.approx(0.04081, abs=2e-5)
    # "the minimum stellar contrast before the arms ≈ 0.77": 0.7641, at 1.91 kpc.
    low = 1.0 - stars.depth
    assert float(low.min()) == pytest.approx(0.7641, abs=1e-4) and float(R[int(np.argmin(low))]) == pytest.approx(1.9125, abs=1e-6)
    # "lanes from (5.21 kpc, φ_bar) to 0.52 kpc with radius of curvature 4.5 kpc"; "the base ... (R < 2.1 kpc) 0.385".
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    assert (a, gas.ring_ratio * a, a / gas.lane_curvature, gas.axis_ratio * a) == pytest.approx((5.2097, 0.52097, 4.5302, 2.0839), abs=5e-5)
    filled = R < gas.axis_ratio * a
    base = 1.0 / RATIO_HAND
    assert int(filled.sum()) == 28 and base == pytest.approx(0.38462, abs=1e-5)
    assert float(gas.lanes[filled].min()) == pytest.approx(base, abs=1e-12)  # the Gaussians' tails reach 0 between the lanes
    # "rows 15-17 unchanged": the half-length is S57's bit for bit (the reference, tests/test_layer.py); the two
    # statistical rows' ensemble medians are the regression numbers RESUMING.md carries, 41.10 and 6.08.
    assert float(F["bar_half_length"]) == pytest.approx(5.20971, abs=5e-6)
    ensemble = spec.ensemble(the_model(prod), ("bar_pattern_speed", "bar_corotation_radius"))
    assert (float(np.median(ensemble["bar_pattern_speed"])), float(np.median(ensemble["bar_corotation_radius"]))) == pytest.approx((41.10, 6.08), abs=0.01)
    # ngc_4414: "unbarred, the bar's fields NaN, arms to the centre; ... t_b 0.91 Gyr published beside the pin".
    n = template_run(prod, "ngc_4414")
    assert n.fields["bar_present"] == "no" and all(math.isnan(float(n.fields[k])) for k in BAR_NUMBERS)
    assert (float(n.fields["bar_formation_time"]), float(F["bar_formation_time"])) == pytest.approx((0.9055, 1.4565), abs=5e-5)
    inner = sum(float(np.asarray(n.fields[k])[0]) for k in pt.AMPLITUDE_FIELDS)
    assert inner > 0.3 and sum(float(np.asarray(F[k])[0]) for k in pt.AMPLITUDE_FIELDS) < 1e-6  # no taper against a whole one
    # "Both A₂ peak radii miss 0.76-0.94 a": the same disc with the pin taken off - the criterion bars it - peaks at 0.42 a.
    u = template_run(prod, "ngc_4414", pinned=False)
    assert u.fields["bar_present"] == "yes" and float(u.fields["bar_mass_share"]) == pytest.approx(0.11256, abs=2e-5)
    ua = float(u.fields["bar_half_length"])
    upart = np.asarray(u.fields["pattern_density_contrast"]) - 1.0 - hand_arms(u.fields, R, phi)
    ua2 = hand_fourier(upart, phi)
    upeak = int(np.argmax(np.where(R < ua, ua2, -1.0)))
    assert float(ua2[upeak]) == pytest.approx(float(u.fields["bar_contrast"]), abs=1e-12) and float(R[upeak]) / ua == pytest.approx(0.4167, abs=1e-4)


# --- the gate -----------------------------------------------------------------------------------------------------


def test_gate_the_stellar_field_on_every_suite_seed(prod):
    """"Stellar ring means 1 to 1e-12 on cells, nothing clipped; min contrast > 0 on every suite seed (a seed that
    fails is reported, B5, not clipped); A₂^max of the published field inside a equals B to 1e-6 on every barred
    seed; the A₂ peak radius and A₂(0.85 a) recorded" - on the 240 galaxies the suite draws (both templates' inputs,
    sixty pattern seeds, two texture seeds), and on ``ngc_4414``'s disc with its pin taken off, sixty more barred
    galaxies of another disc. The bar part is the published field less the arm modes at the published amplitudes
    and phases, by this file's arithmetic; its amplitude is this file's Fourier sum.

    **The check, as the gate reworded it after the build**: "the A₂ maximum inside a of the bar part of the
    published field (the field less the arm modes) equals B to 1e-6". The *whole* field's two-fold amplitude inside
    a is not B: the two-armed mode, tied to the bar's axis (item 9), adds to it or takes from it under the taper.
    A consequence, not a check, recorded as read: the whole field's A₂ maximum inside a less B runs from −0.0059
    (pattern seed 34) to +0.0081 (seed 28) over the Milky Way's 120 suite galaxies - −1.9 % to +2.5 % of B, the
    maximum at 0.396-0.439 a - and from −0.0082 to +0.0101 on ``ngc_4414``'s disc unpinned, where on some seeds
    the largest two-fold amplitude inside a is the arms' own, at the bar's end (0.99 a).

    **As read**: ring means off 1 by 1.6e-15 at worst; the lowest cell 0.0024886 (the Milky Way's inputs, pattern
    seed 28, texture seed 1 - the suite's lowest before S58 too) - **no seed fails**; A₂^max − B under 2e-15 on each
    of the 120 barred suite galaxies and the sixty unpinned ones; the peak at 0.4103 a on every Milky Way seed and
    0.4167 a on ``ngc_4414``'s disc (the grid's ring nearest the continuous maximum: the shape is scale-free);
    A₂(0.85 a) 0.1536 B and 0.1538 B; the share 0.3508 B and 0.3506 B; the body's contrast before the arms at
    least 0.266 (the bar amplitude at its cap, 0.9; 0.2661 on the suite's 240 and 0.2658 on the other disc)."""
    model = the_model(prod)
    worst_mean, worst_error, lowest, lowest_body, where = 0.0, 0.0, math.inf, math.inf, None
    read: dict[str, list[tuple[float, float, float]]] = {}
    whole: dict[str, list[tuple[float, float]]] = {}
    drawn = 0
    cases = [(t, True, s, x) for t in TEMPLATES for s in range(60) for x in (0, 1)] + [("ngc_4414", False, s, 0) for s in range(60)]
    for template, pinned, pattern_seed, texture_seed in cases:
        o = run(model, inputs_of(template, pinned, pattern_seed=pattern_seed, texture_seed=texture_seed), only=STELLAR)
        F, R, phi = o.fields, o.grid.R, o.grid.phi
        field = np.asarray(F["pattern_density_contrast"])
        label = (template, pinned, pattern_seed, texture_seed)
        assert np.all(np.isfinite(field)), label
        worst_mean = max(worst_mean, float(np.abs(field.mean(axis=1) - 1.0).max()))
        if pinned:
            drawn += 1
            if float(field.min()) < lowest:
                lowest, where = float(field.min()), label
        assert field.min() > 0.0, label  # nothing is clipped: a seed that failed here would be reported, not mended
        barred = F["bar_present"] == "yes"
        assert barred == (template == "milky_way" or not pinned), label
        if not barred:
            assert all(math.isnan(float(F[k])) for k in BAR_NUMBERS), label
            continue
        a, B = float(F["bar_half_length"]), float(F["bar_contrast"])
        a2 = hand_fourier(field - 1.0 - hand_arms(F, R, phi), phi)
        inside = R < a
        peak = int(np.argmax(np.where(inside, a2, -1.0)))
        worst_error = max(worst_error, abs(float(a2[peak]) - B))
        assert abs(float(a2[peak]) - B) < 1e-6, label
        assert float(F[pt.phase_field(2)]) == 0.0, label  # item 9: the two-armed crest on the bar's axis
        read.setdefault(template, []).append((float(R[peak]) / a, float(np.interp(0.85 * a, R, a2)) / B, float(F["bar_mass_share"]) / B))
        whole_a2 = hand_fourier(field - 1.0, phi)  # the whole field's: the bar part and the two-armed mode together
        top = int(np.argmax(np.where(inside, whole_a2, -1.0)))
        whole.setdefault(template, []).append((float(whole_a2[top]) - B, float(R[top]) / a))
        stars = compose.stellar_pattern(F, R)
        lowest_body = min(lowest_body, float((1.0 - stars.depth).min()))
        assert 0.0 < B <= pt.BAR_CONTRAST_CAP and 0.0 <= float(F["bar_mass_share"]) < 0.35, label
    assert drawn == 240 and len(read["milky_way"]) == 120 and len(read["ngc_4414"]) == 60
    assert worst_mean < 1e-12 and worst_error < 1e-13
    assert lowest == pytest.approx(0.0024886, abs=1e-7) and where == ("milky_way", True, 28, 1)
    assert lowest_body == pytest.approx(0.2658, abs=2e-4) and lowest_body > 0.0
    for template, want in (("milky_way", (0.4103, 0.1536, 0.3508)), ("ngc_4414", (0.4167, 0.1538, 0.3506))):
        got = np.array(read[template])
        assert got.min(axis=0).tolist() == pytest.approx(want, abs=1e-4) and got.max(axis=0).tolist() == pytest.approx(want, abs=1e-4), template
        assert not np.any((got[:, 0] >= 0.76) & (got[:, 0] <= 0.94))  # the recorded miss, on every barred seed
    # The whole field's A₂ maximum inside a, less B: a consequence of the two-armed mode on the bar's axis, as read.
    for template, (low, high), (near, far) in (("milky_way", (-0.005854, 0.008093), (0.3959, 0.4391)),
                                                ("ngc_4414", (-0.008212, 0.010120), (0.3953, 0.9936))):
        got = np.array(whole[template])
        assert (float(got[:, 0].min()), float(got[:, 0].max())) == pytest.approx((low, high), abs=2e-6), template
        assert (float(got[:, 1].min()), float(got[:, 1].max())) == pytest.approx((near, far), abs=1e-4), template


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("n_phi", [36, 108, 360, 500])
def test_gate_a_ring_keeps_its_stars_and_its_gas_on_any_grid(prod, template, n_phi):
    """Ring means 1 with nothing divided: the body's share is the mean of the same samples its profile is made of,
    and a cell holds the body's - and the lanes' - exact mean over its extent in azimuth, so the cells of a ring
    average to 1 to rounding whatever the φ grid; and the m = 2 amplitude of that grid's own bar part is the drawn
    amplitude (the normalisation is taken on the grid the field is published on)."""
    grid = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=n_phi)
    o = run(the_model(prod), inputs_of(template), grid, only=PATTERN)
    F, R, phi = o.fields, o.grid.R, o.grid.phi
    stars, gas = np.asarray(F["pattern_density_contrast"]), np.asarray(F["gas_density_contrast"])
    assert float(np.abs(stars.sum(axis=1) / n_phi - 1.0).max()) < 1e-12 and stars.min() > 0.0
    assert float(np.abs(gas.sum(axis=1) / n_phi - 1.0).max()) < 1e-13 and gas.min() > 0.0
    if template == "milky_way":
        a, B = float(F["bar_half_length"]), float(F["bar_contrast"])
        a2 = hand_fourier(stars - 1.0 - hand_arms(F, R, phi), phi)
        assert float(a2[R < a].max()) == pytest.approx(B, abs=1e-12)
        # A coarse R grid has no ring at the continuous maximum, so the same amplitude takes another share: the
        # share is the published field's on its own grid (0.1015 on the production grid).
        assert float(F["bar_mass_share"]) == pytest.approx(0.1033, abs=2e-3)
    else:
        assert math.isnan(float(F["bar_mass_share"]))


@pytest.mark.parametrize("template", TEMPLATES)
def test_gate_the_gas_with_its_lanes(prod, template):
    """"Gas ring means 1 to 1e-13 with the lanes, g ≥ w_bar·min L > 0". On every ring of the published field, with
    the lane field read from the pattern; an unbarred galaxy's gas is its response alone, w_bar = 0 on every ring.

    **The second clause, as the gate reworded it after the build**: "g ≥ 0, equal to 0 only where s underflows the
    doubles' subnormals, every such cell counted and recorded". On the two templates no cell is 0; the corner where
    some are is ``test_gate_the_gas_is_zero_only_where_the_response_underflows``."""
    o = template_run(prod, template)
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    g = np.asarray(F["gas_density_contrast"])
    assert g.tobytes() == gas.cell_means(R, edges).tobytes()
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 1e-13 and np.all(np.isfinite(g)) and g.min() > 0.0
    taper = pt.bar_terms(R, gas.pitch_deg, gas.bar_length)[0]
    if template == "ngc_4414":
        assert not gas.barred and not taper.any() and math.isnan(gas.bar_length)
        winding = pt.bar_terms(R, gas.pitch_deg, gas.bar_length)[1]
        on = gas.carries  # the rings that carry a mode: the response's own cell means, to the bit; the rest are 1
        alone = gr.sector_mean(gas.profiles[on], edges[None, :-1] - winding[on, None], edges[None, 1:] - winding[on, None])
        assert g[on].tobytes() == alone.tobytes() and np.all(g[~on] == 1.0)
        return
    L = gas.lanes
    assert L.shape == (R.size, gr.CELLS) and float(np.abs(L.sum(axis=1) / gr.CELLS - 1.0).max()) < 1e-13
    floor = taper * L.min(axis=1)
    assert L.min() == pytest.approx(1.0 / RATIO_HAND, abs=1e-12) and np.all(floor[R < gas.bar_length] > 0.0)
    # g ≥ w_bar min L: to the rounding of a cell's mean (where the lane field sits on its base across a whole cell
    # and the response is 1e-11 of the ring's mean, the mean of the base is the base to 2e-15). Nothing is clipped.
    margin = float((g - floor[:, None]).min())
    assert -1e-14 < margin < 1e-4, margin
    # The lane's peak over the ring's mean: 7.06 on the lane field (3.34 kpc), 6.66 on the published gas (2.06 kpc,
    # the taper and the cell's mean in it). One simulation's Σ_peak ~ 10 x its initial 10 M☉/pc² (Kim, Seo & Kim
    # 2012) is the check: the same order, under it. Nothing is tuned to it - the width is a declared placeholder.
    peak = L.max(axis=1)
    assert (float(peak.max()), float(R[int(np.argmax(peak))])) == pytest.approx((7.058, 3.3375), abs=2e-3)
    inside = R < gas.bar_length
    assert (float(g[inside].max()), float(R[int(np.argmax(g.max(axis=1)))])) == pytest.approx((6.664, 2.0625), abs=2e-3)
    assert 5.0 < float(peak.max()) < 10.0


def test_gate_the_gas_is_zero_only_where_the_response_underflows(prod):
    """"g ≥ 0, equal to 0 only where s underflows the doubles' subnormals, every such cell counted and recorded."

    The corner the gate's reviewer found: a massive, compact, disc-dominated galaxy - ``halo_mass`` 1e13,
    ``disc_spin`` 0.005, ``baryon_retention`` 0.5 - **pinned unbarred** (the criterion bars it: f_d 0.861, t_b
    0.73 Gyr; with its bar the same disc's lowest cell is 4.8e-11, the taper times the lanes' base, and none is
    0). With no bar there is no taper, the arms run to the centre, and between the arms of the inner rings the
    response falls under the smallest double: s is exactly 0.0 on 239 of the solver's cells and subnormal on 343
    more. **As read: 55 cells of the published field are exactly 0.0, on 8 rings, 0.71-1.24 kpc** (2, 6, 9, 9, 9,
    8, 7 and 5 cells, outwards) - cells whose whole extent in azimuth lies where s has underflowed. Nothing is
    negative, nothing is NaN, nothing is clipped or floored; the rings' means are still 1 (9.4e-14); the whole
    pipeline runs, and the only fields that hold a NaN the barred galaxy's do not are the bar's eight numbers. The
    field the star formation law reads is the same bits (no bar, no footprint)."""
    model = the_model(prod)
    corner = {"halo_mass": 1e13, "disc_spin": 0.005, "baryon_retention": 0.5}
    o = run(model, {**corner, "bar_present": False})
    F, R = o.fields, o.grid.R
    g = np.asarray(F["gas_density_contrast"])
    assert F["bar_present"] == "no" and np.all(np.isfinite(g)) and g.min() == 0.0 and not np.any(g < 0.0)
    zero = g == 0.0
    rings = np.flatnonzero(zero.any(axis=1))
    assert int(zero.sum()) == 55 and rings.size == 8
    assert (float(R[rings[0]]), float(R[rings[-1]])) == pytest.approx((0.7125, 1.2375), abs=1e-9) and np.all(np.diff(rings) == 1)
    assert zero[rings].sum(axis=1).tolist() == [2, 6, 9, 9, 9, 8, 7, 5]
    assert float(np.abs(g.sum(axis=1) / g.shape[1] - 1.0).max()) < 2e-13
    # Only where s underflows: every zero cell lies, whole, where the solver's own profile is under the smallest
    # normal double; and the profile is exactly 0 or subnormal on the counted cells.
    gas = compose.gas_pattern(F, R, constants(model))
    s = gas.profiles
    tiny = float(np.finfo(float).tiny)
    assert not gas.barred and float(s.min()) == 0.0 and not np.any(s < 0.0)
    assert (int((s == 0.0).sum()), int(((s > 0.0) & (s < tiny)).sum())) == (239, 343)
    assert set(np.flatnonzero((s < tiny).any(axis=1))) >= set(rings)
    winding = pt.bar_terms(R, gas.pitch_deg, gas.bar_length)[1]
    edges = o.grid["phi"].edges
    for i in rings:
        for j in np.flatnonzero(zero[i]):
            at = np.linspace(edges[j], edges[j + 1], 9) - winding[i]
            assert float(gas.response_at(np.full(9, R[i]), at).max()) < tiny, (i, j)
    assert np.asarray(F["star_formation_gas_contrast"]).tobytes() == g.tobytes()
    # No NaN where the barred galaxy has none, and the whole pipeline ran: the same fields, the modulation finite.
    barred = run(model, corner)
    assert barred.fields["bar_present"] == "yes" and set(barred.fields) == set(F)
    low = np.asarray(barred.fields["gas_density_contrast"])
    assert low.min() > 0.0 and float(low.min()) == pytest.approx(4.768e-11, rel=2e-3)
    assert (float(barred.fields["disc_dominance"]), float(barred.fields["bar_formation_time"])) == pytest.approx((0.8606, 0.7257), abs=2e-4)

    def holds_nan(fields) -> set[str]:
        return {n for n, v in fields.items() if not isinstance(v, str) and np.asarray(v).dtype.kind == "f" and bool(np.isnan(np.asarray(v)).any())}

    assert holds_nan(F) - holds_nan(barred.fields) == set(BAR_NUMBERS)
    assert np.all(np.isfinite(np.asarray(F["sfr_modulation"]))) and np.asarray(F["sfr_modulation"]).min() >= 0.0


# --- by hand -------------------------------------------------------------------------------------------------------


def test_the_presence_rederived_by_hand_for_both_templates(prod):
    """D217 item 1, with this file's arithmetic: t_b = 0.146 exp(1.38 / f_d) Gyr, f_d the published
    ``disc_dominance``; the disc's age the lookback time to ``halo_assembly_z`` - flat matter + Λ at the model's
    H₀ = 70 km/s/Mpc and Ω_M = 0.3, integrated here by Simpson's rule, not by the model's closed form; barred where
    t_b < the age. Both templates' discs are barred by the criterion; ``ngc_4414``'s pin says otherwise, and its
    formation time is published beside the pinned verdict.

        template    f_d      t_b Gyr   z_f    age Gyr   derived   published
        milky_way   0.5999   1.4565    1.66   9.6248    barred    barred (the pin says the same)
        ngc_4414    0.7562   0.9055    0.5    5.0406    barred    unbarred (the pin)

    The universe is 13.467 Gyr old in this cosmology. **The model held no function from the assembly redshift to
    a time before S58** (the halo reads the redshift for its concentration alone); ``pattern.lookback_time`` is
    the closed form of the integral taken here."""
    model = the_model(prod)
    for template, f_want, t_want, z_want, age_want, published in (
        ("milky_way", 0.5999, 1.4565, 1.66, 9.6248, "yes"), ("ngc_4414", 0.7562, 0.9055, 0.5, 5.0406, "no"),
    ):
        o = template_run(prod, template)
        f_d = float(o.fields["disc_dominance"])
        t_b = T0_HAND * math.exp(S_HAND / f_d)
        z = float(o.inputs["halo_assembly_z"])
        age = hand_age(z)
        assert (f_d, t_b, z, age) == pytest.approx((f_want, t_want, z_want, age_want), abs=5e-5), template
        assert float(o.fields["bar_formation_time"]) == pytest.approx(t_b, rel=1e-13), template
        assert pt.lookback_time(z, H0_HAND, OMEGA_M_HAND) == pytest.approx(age, rel=1e-10), template
        assert t_b < age and o.fields["bar_present"] == published, template
        # The verdict the criterion gives this disc, with no pin: barred, both.
        derived = run(model, inputs_of(template, pinned=False), only=("bar_present", "bar_formation_time"))
        assert derived.fields["bar_present"] == "yes" and derived.fields["bar_formation_time"] == o.fields["bar_formation_time"]
    assert hand_age(1e6) == pytest.approx(pt.cosmic_time(0.0, H0_HAND, OMEGA_M_HAND), rel=1e-6) == pytest.approx(13.467, abs=1e-3)
    # **Two clocks, a declared debt** (``pattern.lookback_time``'s docstring): the universe is 13.467 Gyr old by this
    # cosmology and the grid's time axis runs to 13.8 Gyr "from t = 0". What the choice moves: at the default
    # assembly redshift a disc is barred above f_d = 0.3295 on this clock, and above 0.3276 with the same lookback
    # stretched to the grid's.
    assert DEFAULT.t_max == 13.8
    default_age = hand_age(1.66)
    assert S_HAND / math.log(default_age / T0_HAND) == pytest.approx(0.3295, abs=5e-5)
    assert S_HAND / math.log(default_age * 13.8 / 13.467 / T0_HAND) == pytest.approx(0.3276, abs=5e-5)
    assert pt.bar_formation_time(0.0, T0_HAND, S_HAND) == math.inf and pt.bar_formation_time(1e-4, T0_HAND, S_HAND) == math.inf
    # Fujii's time at the reading's anchors (READING_BAR.md A2, the reader's derivation): 7.5 Gyr at f_d = 0.35,
    # 4.6 at 0.4, 2.3 at 0.5, 1.5 at 0.6; and 14.5 Gyr at 0.30, past a Hubble time.
    for f_d, want in ((0.30, 14.5), (0.35, 7.5), (0.4, 4.6), (0.5, 2.3), (0.6, 1.5)):
        assert pt.bar_formation_time(f_d, T0_HAND, S_HAND) == pytest.approx(want, abs=0.06), f_d


def test_where_the_criterion_itself_says_unbarred(prod):
    """The criterion over the controls, one at a time from the defaults (the handoff's probe, re-read on the built
    model): barred everywhere but at ``baryon_retention`` 0.05 (f_d 0.27, t_b 24.9 Gyr) **and at ``disc_spin``
    0.05** (f_d 0.317, t_b 11.4 Gyr against a disc 9.62 Gyr old). The handoff read the second as unbarred "by ELN
    alone" - against a Hubble time it would be barred; against the disc's age since the halo's assembly, which is
    what D217 item 1 rules, it is not. No mass dependence: the halo's mass moves f_d by nothing."""
    from galaxy.core.registry import controls

    model = the_model(prod)
    verdicts = {}
    for control in controls():
        for value in (control.lo, control.hi):
            o = run(model, {control.name: value}, only=("bar_present", "bar_formation_time", "disc_dominance"))
            verdicts[control.name, value] = (o.fields["bar_present"], round(float(o.fields["disc_dominance"]), 3), round(float(o.fields["bar_formation_time"]), 1))
    unbarred = {k: v for k, v in verdicts.items() if v[0] == "no"}
    assert unbarred == {("disc_spin", 0.05): ("no", 0.317, 11.4), ("baryon_retention", 0.05): ("no", 0.268, 24.9)}
    assert verdicts["halo_mass", 1e11][1:] == verdicts["halo_mass", 1e13][1:] == (0.6, 1.5)
    assert run(model, {"disc_spin": 0.045}, only=("bar_present",)).fields["bar_present"] == "yes"  # t_b 8.2 Gyr


def test_the_body_rederived_by_hand_on_the_milky_way_template(prod):
    """D217 items 4-5 from the **published** fields, with this file's arithmetic and no function of ``pattern``,
    ``gas_pattern`` or ``gas_response``: the body's profile on 1440 cells in the bar's frame, the ring's share β,
    the normalisation from the published mass share, the published field's cells (the trapezoid rule on the
    interpolant's own breakpoints), the A₂ profile, and the share back from the drawn amplitude.

        R kpc     Σ M☉/pc²   β        b        1 − b    A₂        A₂ / B
        0.7125    1045.37    0.3903   0.0436   0.9564   0.0422    0.146   (β's maximum)
        2.1375    604.91     0.2200   0.2200   0.7800   0.2893    1.000   (A₂'s maximum)
        4.0125    294.50     0.0511   0.0511   0.9489   0.0945    0.327
        5.0625    196.80     0.0008   0.0008   0.9992   0.0015    0.005

    (Past 2.08 kpc the body does not reach the bar's minor axis, so the ring's trough is empty of it and b = β.)

    β is the mean of the ring's own samples, so each ring's cells average to 1 with nothing divided (measured
    3e-16). The body's contrast is 1 − β + N p/Σ: nowhere under 1 − b, which is positive on every ring. Outside
    the half-length the body is nothing and the field is the arm modes alone."""
    o = template_run(prod, "milky_way")
    F, R, phi, edges = o.fields, o.grid.R, o.grid.phi, o.grid["phi"].edges
    assert (float(F["bar_axis_ratio"]), float(F["bar_boxiness"]), float(F["bar_profile_index"])) == (Q_HAND, C_HAND, N_HAND)
    sigma = np.asarray(F["disc_surface_density"], dtype=float)
    assert o.decls["disc_surface_density"].unit == "Msun/pc2" and o.decls["bar_mass_share"].unit == "dimensionless"
    a, B, share = float(F["bar_half_length"]), float(F["bar_contrast"]), float(F["bar_mass_share"])
    angle = math.log(a) / math.tan(math.radians(float(F["pitch_angle"])))  # the bar lies on the winding's phase at its end
    psi, p = hand_body(R, a)
    P = p.mean(axis=1)
    areas = R * (R[1] - R[0])  # R ΔR on the grid's equal rings
    normalisation = share * float((sigma * areas).sum()) / float((P * areas).sum())  # M☉/pc²
    assert normalisation == pytest.approx(464.8, abs=0.1)
    beta = normalisation * P / sigma
    depth = normalisation * (P - p.min(axis=1)) / sigma
    field = np.asarray(F["pattern_density_contrast"])
    part = field - 1.0 - hand_arms(F, R, phi)
    a2 = hand_fourier(part, phi)
    worst = 0.0
    for radius, sigma_want, beta_want, depth_want, a2_want in (
        (0.7125, 1045.37, 0.3903, 0.0436, 0.0422), (2.1375, 604.91, 0.2200, 0.2200, 0.2893),
        (4.0125, 294.50, 0.0511, 0.0511, 0.0945), (5.0625, 196.80, 0.0008, 0.0008, 0.0015),
    ):
        i = int(np.argmin(np.abs(R - radius)))
        assert float(R[i]) == pytest.approx(radius, abs=1e-9)
        assert float(sigma[i]) == pytest.approx(sigma_want, abs=6e-3), radius
        assert (float(beta[i]), float(depth[i]), float(a2[i])) == pytest.approx((beta_want, depth_want, a2_want), abs=6e-5), radius
        # The ring's contrast on the fixed cells, and its mean over each of the grid's cells, by hand.
        contrast = 1.0 - beta[i] + normalisation * p[i] / sigma[i]
        assert abs(float(contrast.mean()) - 1.0) < 1e-14 and float(contrast.min()) == pytest.approx(1.0 - depth[i], abs=1e-14) and contrast.min() > 0.0
        cells = hand_cell_means(contrast, edges[:-1] - angle, edges[1:] - angle)
        worst = max(worst, float(np.abs(cells - (1.0 + part[i])).max()))
        assert abs(float(cells.mean()) - 1.0) < 1e-13 and abs(float(field[i].mean()) - 1.0) < 1e-13
    assert worst < 1e-12  # the published field's body part is the hand's cell means: measured 4e-15
    # The body's two ends: its share runs to 0.39 of a ring; past its edge there is none of it. **The edge is
    # m = 1, not the circle R = a**: a boxy body stands proud of that circle beside its axis, to
    # a (1 + q⁶)^{1/6} = 1.00068 a for c = 3, and the one grid ring between a and that (5.2125 kpc) holds a sliver
    # of it - 8.5e-8 of the central density at most, 2e-7 of the ring's mean in the published field. The first
    # build cut the body at R < a and dropped the sliver; this test's own arithmetic found it.
    reach = a * (1.0 + Q_HAND**6) ** (1.0 / 6.0)
    assert reach / a == pytest.approx(1.00068, abs=1e-5)
    outside, sliver = R >= reach, (R >= a) & (R < reach)
    assert not p[outside].any() and float(np.abs(part[outside]).max()) < 1e-15
    assert int(sliver.sum()) == 1 and float(R[sliver][0]) == pytest.approx(5.2125, abs=1e-9)
    assert float(p[sliver].max()) == pytest.approx(8.52e-8, rel=0.01) and 1e-8 < float(np.abs(part[sliver]).max()) < 3e-7
    assert np.array_equal(compose.stellar_pattern(F, R).body.holds, p.any(axis=1)) and int(p.any(axis=1).sum()) == 70
    assert (float(beta.max()), float((1.0 - depth).min())) == pytest.approx((0.3903, 0.7641), abs=1e-4)
    # The model's own body is the hand's: β and b on every ring.
    stars = compose.stellar_pattern(F, R)
    assert np.allclose(stars.ring_share, beta, rtol=1e-12, atol=1e-15) and np.allclose(stars.depth, depth, rtol=1e-12, atol=1e-15)
    assert stars.normalisation == pytest.approx(normalisation, rel=1e-13) and stars.bar_angle == pytest.approx(angle, rel=1e-15)
    # The input is the drawn amplitude: the A₂ profile's maximum inside a is B, and it is what fixes the share.
    inside = R < a
    assert float(a2[inside].max()) == pytest.approx(B, abs=1e-12)
    unit = np.array([hand_fourier(hand_cell_means(p[i] / sigma[i], edges[:-1] - angle, edges[1:] - angle)[None, :], phi)[0]
                     for i in np.flatnonzero(inside)])
    by_amplitude = (B / float(unit.max())) * float((P * areas).sum()) / float((sigma * areas).sum())
    assert by_amplitude == pytest.approx(share, rel=1e-12) == pytest.approx(0.10146, abs=2e-5)
    # The amplitude is linear in the normalisation ("so A₂^max fixes the share and the share fixes A₂^max, one number").
    assert np.allclose(a2[inside], normalisation * unit, rtol=0.0, atol=1e-13)
    # The saturation reads this depth: the published amplitudes sum to at most 1 − b on every ring.
    total = np.sum([np.asarray(F[k], dtype=float) for k in pt.AMPLITUDE_FIELDS], axis=0)
    assert float((total + depth).max()) == pytest.approx(0.7937, abs=1e-3) and np.all(np.asarray(F["arm_saturation"]) == 1.0)
    # And the body's mass in closed form: N a² q K_c / 3, K_c = 4 Γ(1 + 1/c)² / Γ(1 + 2/c), against the disc's 2π Σ₀ R_d²
    # - the grid's rings give the same share to 2e-4 of it (the body is resolved; the disc runs to the grid's edge).
    k_c = 4.0 * math.gamma(1.0 + 1.0 / C_HAND) ** 2 / math.gamma(1.0 + 2.0 / C_HAND)
    closed = normalisation * a * a * Q_HAND * k_c / 3.0 / (2.0 * math.pi * float(F["disc_central_surface_density"]) * (a / 2.0) ** 2)
    assert closed == pytest.approx(share, rel=5e-4)


def test_the_saturation_reads_the_body_s_depth_on_a_saturated_barred_galaxy(prod):
    """D217 item 5: "b(R) := 1 − min_φ(body contrast)(R) = β(R) − min_φ Σ_bar/Σ; s(R) = min(1, (1 − b)/ΣÃ_m) as
    today, so the composed field stays positive by the same bound." Read where the bound binds: the Milky Way's
    inputs at pattern seed 28, the most saturated barred galaxy of the suite's sixty (a drawn arm amplitude of
    0.786, a bar amplitude of 0.410, a share of 0.1438; the smallest saturation 0.643, at 7.91 kpc; 84 saturated
    rings, 5.06 to 11.29 kpc). The depth is this file's - the body's profile and the normalisation from the
    published share, by hand. **On every saturated ring the published amplitudes and the depth add up to 1 to
    rounding; on every other ring to less.** Three of the saturated rings hold some of the body (two inside the
    half-length and the sliver's ring): there the modes are scaled to 1 − b and not to 1. And the composed field
    of that galaxy is non-negative on every cell, with nothing floored."""
    model = the_model(prod)
    o = run(model, inputs_of("milky_way", pattern_seed=28, texture_seed=0), only=STELLAR)
    F, R = o.fields, o.grid.R
    a, B, share = float(F["bar_half_length"]), float(F["bar_contrast"]), float(F["bar_mass_share"])
    assert (B, float(F["arm_contrast"]), share) == pytest.approx((0.41008, 0.78587, 0.14384), abs=2e-5)
    sigma = np.asarray(F["disc_surface_density"], dtype=float)
    _, p = hand_body(R, a)
    P = p.mean(axis=1)
    areas = R * (R[1] - R[0])
    normalisation = share * float((sigma * areas).sum()) / float((P * areas).sum())
    depth = normalisation * (P - p.min(axis=1)) / sigma
    saturation = np.asarray(F["arm_saturation"], dtype=float)
    total = np.sum([np.asarray(F[k], dtype=float) for k in pt.AMPLITUDE_FIELDS], axis=0)
    saturated = saturation < 1.0
    assert int(saturated.sum()) == 84 and (float(R[saturated].min()), float(R[saturated].max())) == pytest.approx((5.0625, 11.2875), abs=1e-6)
    assert (float(saturation.min()), float(R[int(np.argmin(saturation))])) == pytest.approx((0.6433, 7.9125), abs=2e-4)
    assert float(np.abs(total[saturated] + depth[saturated] - 1.0).max()) < 1e-15
    assert np.all(total[~saturated] + depth[~saturated] < 1.0) and np.all(saturation[~saturated] == 1.0)
    with_body = saturated & (depth > 0.0)
    assert int(with_body.sum()) == 3 and float(depth[with_body].max()) == pytest.approx(1.070e-3, rel=0.02)
    assert np.all(total[with_body] < 1.0) and np.allclose(total[with_body], 1.0 - depth[with_body], rtol=0.0, atol=1e-15)
    field = np.asarray(F["pattern_density_contrast"])
    assert field.min() >= 0.0 and float(field.min()) == pytest.approx(0.03145, abs=2e-5)


def test_the_saturation_ends_with_the_body_so_a_saturated_galaxy_s_arms_are_stronger_at_the_bar_s_end(prod):
    """A consequence of D217 item 5, recorded (the gate's follow-up; no behaviour is changed here). Until S58 the
    saturation read the cosine bar's depth, b = B e^{−(R/a)⁴}: 0.37 B at the bar's end and still 0.01 B at 1.46 a.
    The body's depth ends where the body does, at a (its sliver's ring apart). So **on a saturated galaxy the arm
    law is not the cosine's**: between the bar's end and where the old taper died, the modes are scaled to 1
    where they were scaled to 1 − B e^{−(R/a)⁴}.

    **No frozen oracle holds the pre-S58 saturated law** - ``tests/s55_patterns.py`` is S55's, one unsaturated mode -
    so the cosine's saturation is rebuilt here from the published fields by this file's arithmetic: the modes'
    sum before saturation is ΣA_m/s, and s_cos = min(1, (1 − B e^{−(R/a)⁴}) / that). The as-built saturation is
    the published one.

    **As read**, the sixty pattern seeds of the default disc: on 26 the law differs from the cosine's somewhere
    (12 to 98 rings each); the default seed is not among them (its arms are unsaturated: no ring moves, as the
    layer-off comparison with ``main`` holds). At worst - pattern seed 34, B = 0.875, an arm amplitude of 0.716 -
    the cosine's saturation on the first ring past the bar's end (5.2125 kpc = 1.0005 a) was **0.687 and is now
    1.000**: "arms at a saturated galaxy's bar end are up to 45 % stronger than under the cosine" (1.455). The
    cosine's bound was the stricter one: the as-built law is never under it."""
    model = the_model(prod)
    read = []
    for seed in range(60):
        o = run(model, inputs_of("milky_way", pattern_seed=seed), only=STELLAR)
        F, R = o.fields, o.grid.R
        a, B = float(F["bar_half_length"]), float(F["bar_contrast"])
        s = np.asarray(F["arm_saturation"], dtype=float)
        before = np.sum([np.asarray(F[k], dtype=float) for k in pt.AMPLITUDE_FIELDS], axis=0) / s
        cosine = np.where(before > 0.0, np.minimum(1.0, (1.0 - B * np.exp(-((R / a) ** 4))) / np.where(before > 0.0, before, 1.0)), 1.0)
        assert np.all(s >= cosine - 1e-12), seed
        differs = np.abs(s - cosine) > 1e-12
        end = int(np.argmax(R >= a))  # the first ring past the bar's end
        read.append((seed, int(differs.sum()), float(cosine[end]), float(s[end]), float((s / cosine).max()), float(R[int(np.argmax(s / cosine))]), B, float(F["arm_contrast"])))
    moved = [row for row in read if row[1] > 0]
    assert [row[0] for row in moved] == [3, 4, 5, 6, 7, 12, 13, 16, 18, 20, 21, 28, 29, 33, 34, 36, 38, 40, 41, 44, 48, 51, 52, 55, 58, 59]
    assert (min(row[1] for row in moved), max(row[1] for row in moved)) == (12, 98) and read[0][1] == 0
    worst = max(read, key=lambda row: row[4])
    assert worst[:2] == (34, 98) and worst[2:] == pytest.approx((0.6872, 1.0, 1.4552, 5.2125, 0.87526, 0.71585), abs=2e-4)


def test_a_point_reads_the_body_between_its_two_rings_in_the_bar_s_frame(prod):
    """Evaluable at a point (D60): the body at (R, φ) is its two neighbouring grid rings' profiles read at φ − φ_bar
    - linear between the cells' centres - and blended linearly in R; at a grid radius it is the ring's own. The
    sector means are that function's exact means: twelve sectors average to 1, and each is the dense average of the
    point function to the dense average's own error."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    stars = compose.stellar_pattern(F, R)
    a, angle = stars.bar_length, stars.bar_angle
    psi, p = hand_body(R, a)
    sigma = np.asarray(F["disc_surface_density"], dtype=float)
    deviation = stars.normalisation * (p - p.mean(axis=1)[:, None]) / sigma[:, None]
    rng = np.random.default_rng(58)
    k = 28  # between 2.1375 and 2.2125 kpc
    radius = float(0.3 * R[k] + 0.7 * R[k + 1])
    phi = rng.uniform(0.0, 2.0 * math.pi, 200)
    centres = np.concatenate([psi - 2.0 * math.pi, psi, psi + 2.0 * math.pi])
    at = ((phi - angle + math.pi) % (2.0 * math.pi)) - math.pi
    want = 0.3 * np.interp(at, centres, np.tile(deviation[k], 3)) + 0.7 * np.interp(at, centres, np.tile(deviation[k + 1], 3))
    assert np.allclose(stars.body_at(np.full_like(phi, radius), phi), want, rtol=0.0, atol=1e-13)
    assert np.allclose(stars.body_at(np.full_like(phi, R[k]), phi), np.interp(at, centres, np.tile(deviation[k], 3)), rtol=0.0, atol=1e-13)
    assert np.all(stars.body_at(np.full_like(phi, 1.2 * a), phi) == 0.0)
    # On the bar's axis the body stands over the ring's mean, across it under: at 2.14 kpc, +0.31 and −0.22.
    on_axis, across = stars.body_at(np.array([R[28]]), np.array([angle])), stars.body_at(np.array([R[28]]), np.array([angle + 0.5 * math.pi]))
    assert (float(on_axis[0]), float(across[0])) == pytest.approx((0.3115, -0.2200), abs=2e-4)
    edges = np.linspace(0.0, 2.0 * math.pi, 13)
    for r in (0.5, 2.0, radius, 4.9, 5.3, 8.0):
        means = stars.sector_means(r, edges)
        assert means.shape == (12,) and float(means.mean()) == pytest.approx(1.0, abs=1e-12), r
        dense = [float(stars.contrast_at(np.full(4000, r), lo + (np.arange(4000) + 0.5) * (hi - lo) / 4000).mean())
                 for lo, hi in zip(edges[:-1], edges[1:])]
        assert float(np.abs(means - np.array(dense)).max()) < 1e-6, r


# --- the lanes -------------------------------------------------------------------------------------------------------


def hand_lane_distance(x: np.ndarray, y: np.ndarray, a: float, side: float) -> np.ndarray:
    """The distance from points to one lane, by brute force: the arc of radius a / 1.15 from (a, 0) to (0, side
    0.10 a), bowed away from the major axis, sampled at 20 001 points - this file's arithmetic. The circle's centre
    is found from the two ends and the radius; of the two circles through them, the one whose centre lies across
    the major axis from the lane's foot."""
    radius = a / KAPPA_A_HAND
    end, foot = np.array([a, 0.0]), np.array([0.0, side * RING_HAND * a])
    mid, chord = 0.5 * (end + foot), foot - end
    d = float(np.hypot(*chord))
    normal = np.array([-chord[1], chord[0]]) / d
    centres = [mid + s * math.sqrt(radius * radius - 0.25 * d * d) * normal for s in (1.0, -1.0)]
    centre = next(c for c in centres if c[1] * side < 0.0)  # on the other side of the major axis from the foot
    t0, t1 = (math.atan2(*(q - centre)[::-1]) for q in (end, foot))
    span = (t1 - t0 + math.pi) % (2.0 * math.pi) - math.pi  # the minor arc
    t = t0 + span * np.linspace(0.0, 1.0, 20001)
    ax, ay = centre[0] + radius * np.cos(t), centre[1] + radius * np.sin(t)
    out = np.empty(np.shape(x))
    for index in np.ndindex(out.shape):
        out[index] = float(np.sqrt((ax - x[index]) ** 2 + (ay - y[index]) ** 2).min())
    return out


def test_the_lanes_geometry_by_hand_and_the_leading_side_from_the_trailing_arms(prod):
    """D217 item 7: "two point-symmetric constant-curvature arcs on the leading side, each from the bar's end on
    the major axis (R = a) to the minor axis at the nuclear ring, concave to the major axis; κ·a = 1.15 ...;
    r_ring = 0.10 a ... Leading side needs the sense of rotation: the arms' trailing sense gives it."

    **The sense.** A crest of the model's arms lies at φ = ln R · cot(pitch) + a constant, so its azimuth grows
    outwards; trailing arms lag the rotation at their outer ends, so the disc turns towards *decreasing* φ:
    ``rotation_sense`` is −1, read off the winding itself. The bar's leading side is then at smaller azimuth: the
    lane from the end at ψ = 0 (ψ = φ − φ_bar) runs through negative ψ to the minor axis at ψ = −90°, and its twin
    from ψ = 180° to +90°.

    **The geometry** on the Milky Way template (a = 5.2097 kpc): ends at (5.2097, 0) and (0, −0.5210) kpc in the
    bar's frame, a circle of radius 4.5302 kpc centred at (2.2370, +3.4184) kpc - across the major axis from the
    lane, so the lane bows away from the axis, to 1.10 kpc off it at mid-length. The module's distance to the lane
    is the hand's brute-force one to 2e-8 kpc; the ridge of L follows the arc."""
    assert gm.rotation_sense(13.5) == gm.rotation_sense(1.0) == gm.rotation_sense(60.0) == -1.0
    _, winding, _ = pt.bar_terms(np.array([2.0, 4.0, 8.0]), 13.5, 5.2)
    assert np.all(np.diff(winding) > 0.0)  # the crests' azimuth grows outwards: trailing means the disc turns to smaller φ
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    a = gas.bar_length
    assert (gas.sense, gas.lane_curvature, gas.ring_ratio, gas.gas_ratio, gas.lane_width) == (-1.0, KAPPA_A_HAND, RING_HAND, RATIO_HAND, WIDTH_HAND)
    assert (gas.axis_ratio, gas.boxiness) == (Q_HAND, C_HAND)
    # The module's distance against the hand's, on a spread of points; and on the arc itself it is 0.
    rng = np.random.default_rng(7)
    x, y = rng.uniform(-1.2 * a, 1.2 * a, 400), rng.uniform(-0.6 * a, 0.6 * a, 400)
    assert float(np.abs(gm.lane_distance(x, y, a, KAPPA_A_HAND, RING_HAND, -1.0) - hand_lane_distance(x, y, a, -1.0)).max()) < 1e-6
    for (px, py) in ((a, 0.0), (0.0, -RING_HAND * a)):
        assert float(gm.lane_distance(np.array([px]), np.array([py]), a, KAPPA_A_HAND, RING_HAND, -1.0)[0]) < 1e-12
    # Concave towards the major axis: the centre lies across the axis, and the lane's mid-point is off the axis on
    # the leading side - 1.10 kpc at x = a/2 - further than its chord (0.26 kpc there).
    chord = math.hypot(a, RING_HAND * a)
    radius = a / KAPPA_A_HAND
    height = math.sqrt(radius**2 - 0.25 * chord**2)
    centre = (0.5 * a - height * RING_HAND * a / chord, -0.5 * RING_HAND * a + height * a / chord)
    assert centre == pytest.approx((2.2370, 3.4184), abs=1e-4) and radius == pytest.approx(4.5302, abs=1e-4)
    middle_y = centre[1] - math.sqrt(radius**2 - (0.5 * a - centre[0]) ** 2)
    assert middle_y == pytest.approx(-1.0968, abs=1e-4) and middle_y < -0.5 * RING_HAND * a
    assert float(gm.lane_distance(np.array([0.5 * a]), np.array([middle_y]), a, KAPPA_A_HAND, RING_HAND, -1.0)[0]) < 1e-12
    # The other lane is this one's point reflection, and the other side's lane its mirror image.
    assert np.allclose(gm.lane_distance(x, y, a, KAPPA_A_HAND, RING_HAND, 1.0), gm.lane_distance(x, -y, a, KAPPA_A_HAND, RING_HAND, -1.0), rtol=0.0, atol=1e-12)
    # A circle that cannot span the two ends is refused, not bent.
    with pytest.raises(ValueError, match="does not span the lane's ends"):
        gm.lane_distance(x, y, a, 2.5, RING_HAND, -1.0)
    # The ridge of the lane field: on each ring the tallest cell sits on the arc (within a cell and the Gaussian's
    # own skew against the footprint's edge), at negative ψ for the end at ψ = 0, and its twin half a turn away.
    L = gas.lanes
    psi = gr.cell_centres()
    for radius_kpc, want_deg in ((1.0125, -53.1), (2.0625, -31.9), (3.0375, -20.6), (4.0125, -11.1), (4.9875, -2.1)):
        i = int(np.argmin(np.abs(R - radius_kpc)))
        half = L[i][(psi > -0.5 * math.pi) & (psi < 0.5 * math.pi)]
        crest = float(psi[(psi > -0.5 * math.pi) & (psi < 0.5 * math.pi)][int(np.argmax(half))])
        assert math.degrees(crest) == pytest.approx(want_deg, abs=0.3), radius_kpc
        on_arc = float(gm.lane_distance(np.array([R[i] * math.cos(crest)]), np.array([R[i] * math.sin(crest)]), a, KAPPA_A_HAND, RING_HAND, -1.0)[0])
        assert on_arc < 0.03 and crest < 0.0, radius_kpc
        assert np.allclose(L[i], np.roll(L[i], gr.CELLS // 2), rtol=0.0, atol=1e-12)  # point-symmetric
    # In the galaxy's frame the lane is at smaller azimuth than the bar's end it starts from: the leading side.
    i = int(np.argmin(np.abs(R - 3.0375)))
    phi = np.linspace(0.0, 2.0 * math.pi, 2880, endpoint=False)
    field = gas.lanes_at(np.full_like(phi, R[i]), phi - pt.bar_terms(R, gas.pitch_deg, a)[2])
    lead = (phi[int(np.argmax(field))] - pt.bar_terms(R, gas.pitch_deg, a)[2] + math.pi) % math.pi - math.pi
    assert -0.5 * math.pi < lead < 0.0 or lead < -0.5 * math.pi + 1e-9


def test_the_lanes_gas_by_hand_on_four_rings(prod):
    """D217 item 8, by this file's arithmetic: on a ring the footprint's share f of the cells (m ≤ 1, the body's
    own generalised ellipse), the base 1/(1 + 1.6 f), and the excess 1 − base laid on the two lanes inside the
    footprint with a Gaussian of FWHM 0.10 a across the arc (the distance by brute force) - weighed by its own
    mean over the ring's cells, so the ring's mean is 1 by construction. **The one division in the gas pattern**:
    the template's Gaussian by its own quadrature - its normalisation, as a Gaussian is divided by its integral -
    not a field divided by its sampled mean (D217 forbids that, and no field is; reported to the gate).

        R kpc     f        base      L min     L max    mean in / mean out
        1.0125    1        0.38462   0.38468   3.162    (the footprint fills the ring; the Gaussians' tails are everywhere)
        3.0375    0.4639   0.57398   0.57398   7.010    2.6
        4.0125    0.3028   0.67365   0.67365   6.867    2.6
        4.9875    0.1583   0.79786   0.79786   5.226    2.6
    """
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    a = float(F["bar_half_length"])
    L = gas.lanes
    n = 1440
    psi = -math.pi + (np.arange(n) + 0.5) * (2.0 * math.pi / n)
    sigma = WIDTH_HAND * a / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    for radius, f_want, base_want, top_want in ((1.0125, 1.0, 0.38462, 3.162), (3.0375, 0.4639, 0.57398, 7.010),
                                               (4.0125, 0.3028, 0.67365, 6.867), (4.9875, 0.1583, 0.79786, 5.226)):
        i = int(np.argmin(np.abs(R - radius)))
        x, y = R[i] * np.cos(psi), R[i] * np.sin(psi)
        inside = ((np.abs(x) / a) ** C_HAND + (np.abs(y) / (Q_HAND * a)) ** C_HAND) ** (1.0 / C_HAND) <= 1.0
        f = float(inside.mean())
        base = 1.0 / (1.0 + (RATIO_HAND - 1.0) * f)
        weight = np.where(inside, np.exp(-0.5 * (hand_lane_distance(x, y, a, -1.0) / sigma) ** 2)
                          + np.exp(-0.5 * (hand_lane_distance(-x, -y, a, -1.0) / sigma) ** 2), 0.0)
        by_hand = base + (1.0 - base) * weight / float(weight.mean())
        assert (f, base, float(by_hand.max())) == pytest.approx((f_want, base_want, top_want), abs=2e-4 * max(1.0, top_want)), radius
        assert float(np.abs(L[i] - by_hand).max()) < 2e-5 * top_want, radius  # the brute-force distance's own error
        assert abs(float(L[i].mean()) - 1.0) < 1e-14 and base <= float(L[i].min()) < base + 1e-4
        if f < 1.0:
            assert float(L[i][inside].mean() / L[i][~inside].mean()) == pytest.approx(RATIO_HAND, rel=1e-12), radius
            assert np.all(L[i][~inside] == L[i][~inside][0])  # outside the footprint the ring is its uniform base
    # Every ring inside the bar: mean 1, never under its base, the ratio of means 2.6 wherever there is an outside;
    # past the bar's end, 1.
    inside_a = R < a
    assert float(np.abs(L.sum(axis=1) / n - 1.0).max()) < 1e-13 and np.all(L[~inside_a] == 1.0)
    x, y = R[:, None] * np.cos(psi)[None, :], R[:, None] * np.sin(psi)[None, :]
    footprint = ((np.abs(x) / a) ** C_HAND + (np.abs(y) / (Q_HAND * a)) ** C_HAND) ** (1.0 / C_HAND) <= 1.0
    share = footprint.mean(axis=1)
    base_all = 1.0 / (1.0 + (RATIO_HAND - 1.0) * share)
    assert np.all(share[inside_a] > 0.0) and np.all(L.min(axis=1)[inside_a] >= base_all[inside_a])  # never under its base
    open_rings = inside_a & (share < 1.0)  # where the ring leaves the footprint the minimum is the base itself
    assert np.array_equal(L.min(axis=1)[open_rings], base_all[open_rings]) and int(open_rings.sum()) == 41
    for i in np.flatnonzero(inside_a & (share > 0.0) & (share < 1.0)):
        assert float(L[i][footprint[i]].mean() / L[i][~footprint[i]].mean()) == pytest.approx(RATIO_HAND, rel=1e-11), float(R[i])
    # Deterministic given the bar: nothing is drawn, and another texture seed gives the same lanes.
    other = run(the_model(prod), inputs_of("milky_way", texture_seed=11), only=PATTERN)
    again = compose.gas_pattern(other.fields, R, constants(the_model(prod)))
    assert again.lanes.tobytes() == L.tobytes() and again.phases != gas.phases
    # The lanes are read by no stage as a draw: the gas pattern's source asks for no generator.
    source = Path(gm.__file__).read_text(encoding="utf-8")
    assert ".rng(" not in source and "reads_seeds" not in source


def test_the_lanes_end_in_a_cliff_and_build_no_nuclear_ring(prod):
    """Two things the template does not do, pinned as read and each a debt (the gate's follow-up; no behaviour is
    changed here).

    **Debt: the lanes end in a cliff at R = a.** The lane field is the template inside the half-length and 1 past
    it, with nothing between: on the last three rings inside a (4.99, 5.06, 5.14 kpc) the lane's peak stands 5.23,
    4.89 and 4.45 times the ring's mean, and on the next ring (5.2125 kpc) the field is 1 everywhere. The
    published gas does not show the whole of it - the taper there is 0.4 and the arms' response carries the rest
    (peaks of 2.87, 2.63, 2.69, then 2.80) - but the lanes' own term stops in one ring.

    **Debt: no nuclear ring is built.** The ruling ends each lane on the minor axis "at the nuclear ring",
    r_ring = 0.10 a = 0.52 kpc, and nothing is put there: every ring's mean is 1, so no ring stands over its
    neighbours, and inside r_ring the excess is laid by the lanes' Gaussian tails alone (the distance to the
    lane's foot). On the seven rings inside r_ring the lane field runs from 0.976-1.024 (0.04 kpc: nearly uniform)
    to 0.405-1.934 (0.49 kpc), where the lanes' highest value is 7.06 (3.34 kpc)."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    a, L, g = gas.bar_length, gas.lanes, np.asarray(F["gas_density_contrast"])
    last = np.flatnonzero(R < a)[-3:]
    after = int(last[-1]) + 1
    assert R[last].tolist() == pytest.approx([4.9875, 5.0625, 5.1375], abs=1e-9) and float(R[after]) == pytest.approx(5.2125, abs=1e-9)
    assert L[last].max(axis=1).tolist() == pytest.approx([5.226, 4.886, 4.448], abs=2e-3)
    assert np.all(L[after:] == 1.0)  # the cliff: nothing of the lanes on the first ring past the half-length
    assert g[last].max(axis=1).tolist() == pytest.approx([2.868, 2.634, 2.694], abs=2e-3) and float(g[after].max()) == pytest.approx(2.796, abs=2e-3)
    assert float(pt.bar_terms(R, gas.pitch_deg, a)[0][after]) == pytest.approx(0.367, abs=2e-3)
    # No nuclear ring: every ring's mean is 1; inside r_ring the field is the base and the two lanes' tails.
    ring = gas.ring_ratio * a
    inner = np.flatnonzero(R < ring)
    assert ring == pytest.approx(0.52097, abs=1e-5) and inner.size == 7
    assert float(np.abs(L.sum(axis=1) / L.shape[1] - 1.0).max()) < 1e-13
    assert (float(L[inner[0]].min()), float(L[inner[0]].max())) == pytest.approx((0.9762, 1.0240), abs=2e-4)
    assert (float(L[inner[-1]].min()), float(L[inner[-1]].max())) == pytest.approx((0.4047, 1.9336), abs=2e-4)
    peaks = L[R < a].max(axis=1)
    assert np.all(np.diff(peaks[: inner.size]) > 0.0)  # the peak rises outwards through r_ring: nothing marks the ring
    assert (float(peaks.max()), float(R[int(np.argmax(peaks))])) == pytest.approx((7.058, 3.3375), abs=2e-3)


def test_the_gas_the_star_formation_law_reads_by_hand(prod):
    """The gate's follow-up on the first build: "the lanes' one unsourced number (the width) must not drive a census:
    ``sfr_modulation`` inside the bar's reach reads w_arm s + w_bar L_fp, L_fp the footprint-uniform field (base
    outside the footprint, base + excess/share inside it: the 2.6 ratio kept, no ridge)". By this file's
    arithmetic, on the lanes' own four rings: the footprint's share f of the ring's cells, the base 1/(1 + 1.6 f),
    and inside the footprint the base plus (1 − base)/f.

        R kpc     f        base      inside    mean in / mean out
        1.0125    1        0.38462   1         (the footprint fills the ring: the field is 1)
        3.0375    0.4639   0.57398   1.49234   2.6
        4.0125    0.3028   0.67365   1.75149   2.6
        4.9875    0.1583   0.79786   2.07447   2.6

    The ring's mean is 1 by construction - base (1 − f) + (base + (1 − base)/f) f - with the share taken on the
    cells the template is defined on, as the lanes' weight is; two values on a ring, no ridge; it reads the ratio
    alone of the lanes' four numbers. The published ``star_formation_gas_contrast`` is the blend's exact cell
    means; a point reads it as it reads the laned field; sectors average to 1. Past the half-length it is 1 and
    the two fields are one."""
    o = template_run(prod, "milky_way")
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    a = float(F["bar_half_length"])
    U = gas.footprint
    n = 1440
    psi = -math.pi + (np.arange(n) + 0.5) * (2.0 * math.pi / n)
    for radius, f_want, base_want, top_want in ((1.0125, 1.0, 0.38462, 1.0), (3.0375, 0.4639, 0.57398, 1.49234),
                                               (4.0125, 0.3028, 0.67365, 1.75149), (4.9875, 0.1583, 0.79786, 2.07447)):
        i = int(np.argmin(np.abs(R - radius)))
        x, y = R[i] * np.cos(psi), R[i] * np.sin(psi)
        inside = ((np.abs(x) / a) ** C_HAND + (np.abs(y) / (Q_HAND * a)) ** C_HAND) ** (1.0 / C_HAND) <= 1.0
        f = float(inside.mean())
        base = 1.0 / (1.0 + (RATIO_HAND - 1.0) * f)
        by_hand = np.where(inside, base + (1.0 - base) / f, base)
        assert (f, base, float(by_hand.max())) == pytest.approx((f_want, base_want, top_want), abs=2e-4), radius
        assert float(np.abs(U[i] - by_hand).max()) < 1e-14 and abs(float(U[i].mean()) - 1.0) < 1e-14, radius
        assert np.unique(U[i]).size == (1 if f == 1.0 else 2)  # two levels and no ridge
        if f < 1.0:
            assert float(U[i][inside].mean() / U[i][~inside].mean()) == pytest.approx(RATIO_HAND, rel=1e-12), radius
            assert float(U[i].min()) == float(gas.lanes[i].min())  # the lanes' own base outside the footprint
    assert U.shape == (R.size, gr.CELLS) and float(np.abs(U.sum(axis=1) / gr.CELLS - 1.0).max()) < 1e-13
    assert np.all(U[R >= a] == 1.0) and np.all(U[R < gas.axis_ratio * a] == 1.0) and U.min() > 0.0
    assert float(U.max()) == pytest.approx(2.2, abs=0.01) and float(U.max()) < RATIO_HAND < float(gas.lanes.max())
    # The published field is the blend's exact cell means, by hand, and the model's own to the bit.
    published = np.asarray(F["star_formation_gas_contrast"])
    assert published.tobytes() == gas.star_formation_cell_means(R, edges).tobytes()
    both = gas.published_cell_means(R, edges)
    assert both[0].tobytes() == np.asarray(F["gas_density_contrast"]).tobytes() and both[1].tobytes() == published.tobytes()
    taper, winding, angle = pt.bar_terms(R, gas.pitch_deg, gas.bar_length)
    for i in (5, 28, 40, 60, 66):  # 0.41, 2.14, 3.04, 4.54 and 4.99 kpc
        cell = ((1.0 - taper[i]) * hand_cell_means(gas.profiles[i], edges[:-1] - winding[i], edges[1:] - winding[i])
                + taper[i] * hand_cell_means(U[i], edges[:-1] - angle, edges[1:] - angle))
        assert float(np.abs(published[i] - cell).max()) < 1e-11, i
    assert float(np.abs(published.sum(axis=1) / published.shape[1] - 1.0).max()) < 2e-13 and published.min() > 0.0
    # At a point, and over sectors: the laned field's own reading with the other template.
    rng = np.random.default_rng(58)
    radius, phi = rng.uniform(0.2, 9.0, 300), rng.uniform(0.0, 2.0 * math.pi, 300)
    t, w, _ = pt.bar_terms(radius, gas.pitch_deg, gas.bar_length)
    want = (1.0 - t) * gas.response_at(radius, phi - w) + t * gas.footprint_at(radius, phi - angle)
    assert np.allclose(gas.star_formation_contrast_at(radius, phi), want, rtol=0.0, atol=1e-13)
    assert np.all(gas.star_formation_contrast_at(radius, phi) >= t * (1.0 / RATIO_HAND))
    sectors = np.linspace(0.0, 2.0 * math.pi, 13)
    for r in (0.5, 2.0, 3.3, 4.9, 5.3, 8.0):
        means = gas.star_formation_sector_means(r, sectors)
        assert means.shape == (12,) and float(means.mean()) == pytest.approx(1.0, abs=1e-12), r
        if r > a:
            assert means.tobytes() == gas.sector_means(r, sectors).tobytes(), r
    past = R >= a
    assert published[past].tobytes() == np.asarray(F["gas_density_contrast"])[past].tobytes() and int(past.sum()) == 331
    # An unbarred pattern has no footprint to ask for; its star-formation readings are its own.
    n4414 = template_run(prod, "ngc_4414")
    bare = compose.gas_pattern(n4414.fields, R, constants(the_model(prod)))
    with pytest.raises(ValueError, match="no bar's footprint"):
        bare.footprint
    assert np.array_equal(bare.star_formation_contrast_at(radius, phi), bare.contrast_at(radius, phi))
    assert bare.star_formation_sector_means(3.0, sectors).tobytes() == bare.sector_means(3.0, sectors).tobytes()
    assert np.asarray(n4414.fields["star_formation_gas_contrast"]).tobytes() == np.asarray(n4414.fields["gas_density_contrast"]).tobytes()


def test_the_gas_at_a_point_inside_the_bar_is_the_blend_of_the_response_and_the_lanes(prod):
    """g = w_arm s + w_bar L at a point (D217 item 6): the taper at the point's own radius, s at the point's winding
    phase and L at its angle from the bar, each read from the two neighbouring rings. The published cell is the
    same blend of the two exact cell means."""
    o = template_run(prod, "milky_way")
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    gas = compose.gas_pattern(F, R, constants(the_model(prod)))
    rng = np.random.default_rng(58)
    radius = rng.uniform(0.2, 9.0, 300)
    phi = rng.uniform(0.0, 2.0 * math.pi, 300)
    taper, phase, angle = pt.bar_terms(radius, gas.pitch_deg, gas.bar_length)
    want = (1.0 - taper) * gas.response_at(radius, phi - phase) + taper * gas.lanes_at(radius, phi - angle)
    assert np.allclose(gas.contrast_at(radius, phi), want, rtol=0.0, atol=1e-13)
    assert np.all(gas.contrast_at(radius, phi) >= taper * (1.0 / RATIO_HAND)) and np.all(gas.lanes_at(radius, phi - angle) > 0.0)
    for i in (5, 28, 40, 60):  # 0.41, 2.14, 3.04 and 4.54 kpc
        t = float(pt.bar_terms(R, gas.pitch_deg, gas.bar_length)[0][i])
        w = float(pt.bar_terms(R, gas.pitch_deg, gas.bar_length)[1][i])
        cell = (1.0 - t) * hand_cell_means(gas.profiles[i], edges[:-1] - w, edges[1:] - w) + t * hand_cell_means(gas.lanes[i], edges[:-1] - angle, edges[1:] - angle)
        assert float(np.abs(np.asarray(F["gas_density_contrast"])[i] - cell).max()) < 1e-11, i


# --- the unbarred galaxy ---------------------------------------------------------------------------------------------


UNBARRED_PATHS = {
    "the pin on a template": lambda: templates.overrides(templates.TEMPLATES["ngc_4414"]),
    "the default disc pinned unbarred": lambda: {"bar_present": False},
    "the derivation itself": lambda: {"baryon_retention": 0.05},
}


@pytest.mark.parametrize("path", sorted(UNBARRED_PATHS))
def test_an_unbarred_galaxy_builds_whole_and_leaks_no_nan(prod, path):
    """D217 item 3 and the gate: an unbarred galaxy "publishes NaN for ``bar_contrast``, ``bar_half_length`` and
    the bar's angle (D164); the body and the lanes are absent; the taper is 0 on every ring ...; the arm modes run
    to the centre" - and **no NaN leaks into any other field**. The whole pipeline, layer on and off, by each of
    the three roads to an unbarred galaxy: a template's pin, a pin on the default disc, and a disc the criterion
    itself leaves unbarred. The fields that hold a NaN are the eight bar numbers and whatever holds one in the
    same galaxy *with* a bar (a census's dead entries are NaN by D164: the same fields, barred or not)."""
    model = the_model(prod)
    given = UNBARRED_PATHS[path]()
    for layer in (True, False):
        o = run(model, given, SMALL, layer=layer)
        assert o.fields["bar_present"] == "no" and math.isfinite(float(o.fields["bar_formation_time"]))
        barred = run(model, {**given, "bar_present": True}, SMALL, layer=layer)
        assert barred.fields["bar_present"] == "yes" and set(barred.fields) == set(o.fields)

        def holds_nan(fields) -> set[str]:
            return {n for n, v in fields.items() if not isinstance(v, str) and np.asarray(v).dtype.kind == "f" and bool(np.isnan(np.asarray(v)).any())}

        assert holds_nan(o.fields) - holds_nan(barred.fields) == set(BAR_NUMBERS), (path, layer)
        assert not any(np.isinf(np.asarray(v)).any() for v in o.fields.values() if not isinstance(v, str) and np.asarray(v).dtype.kind == "f")
        R = o.grid.R
        # The taper is 0 on every ring and there is no angle; the arm modes run to the centre.
        taper, _, angle = pt.bar_terms(R, float(o.fields["pitch_angle"]), float(o.fields["bar_half_length"]))
        assert not taper.any() and math.isnan(angle)
        amplitudes = np.stack([np.asarray(o.fields[k]) for k in pt.AMPLITUDE_FIELDS])
        tapered = np.stack([np.asarray(barred.fields[k]) for k in pt.AMPLITUDE_FIELDS])
        assert np.all(np.isfinite(amplitudes)) and amplitudes[:, 0].sum() > 10.0 * tapered[:, 0].sum()
        s = np.asarray(o.fields["arm_saturation"])
        total = amplitudes.sum(axis=0)
        assert np.all((s > 0.0) & (s <= 1.0)) and float(total.max()) <= 1.0 + 4e-16  # min(1, 1/ΣÃ): b = 0
        stars_field, gas_field = np.asarray(o.fields["pattern_density_contrast"]), np.asarray(o.fields["gas_density_contrast"])
        if not layer:
            assert np.all(stars_field == 1.0) and np.all(gas_field == 1.0)
            assert all(math.isnan(float(o.fields[k])) for k in pt.PHASE_FIELDS)
            continue
        stars, gas = compose.stellar_pattern(o.fields, R), compose.gas_pattern(o.fields, R, constants(model))
        assert not stars.flat and not stars.barred and stars.body is None and not gas.flat and not gas.barred
        assert float(np.abs(stars_field.mean(axis=1) - 1.0).max()) < 1e-12 and stars_field.min() >= 0.0
        assert float(np.abs(gas_field.sum(axis=1) / gas_field.shape[1] - 1.0).max()) < 1e-13 and gas_field.min() > 0.0
        # The two-armed mode of an unbarred galaxy is a draw, on its stream.
        assert float(o.fields[pt.phase_field(2)]) != 0.0 and float(barred.fields[pt.phase_field(2)]) == 0.0
        assert [float(o.fields[k]) for k in pt.PHASE_FIELDS[1:]] == [float(barred.fields[k]) for k in pt.PHASE_FIELDS[1:]]


def test_a_barred_galaxy_s_numbers_do_not_move_because_unbarred_ones_exist(prod):
    """"Every existing draw keeps its stream and value": the pitch and the arm amplitude are the same number in the
    barred and the unbarred galaxy of one seed; the bar's own draws are made on their streams either way and are
    what they were when the bar is there. Over ten pattern seeds."""
    model = the_model(prod)
    names = ("pitch_angle", "arm_contrast", "bar_contrast", "bar_corotation_radius", "bar_pattern_speed", "bar_half_length",
             "shear_rate", "arm_contrast_mean", "gas_arm_contrast", "bar_formation_time", "disc_dominance", "swing_x")
    for seed in range(10):
        derived = run(model, {"pattern_seed": seed}, SMALL, only=names).fields
        pinned = run(model, {"pattern_seed": seed, "bar_present": True}, SMALL, only=names).fields
        without = run(model, {"pattern_seed": seed, "bar_present": False}, SMALL, only=names).fields
        for n in names:
            assert derived[n] == pinned[n], (seed, n)
            if n in BAR_NUMBERS:
                assert math.isnan(without[n]) and math.isfinite(derived[n]), (seed, n)
            else:
                assert without[n] == derived[n], (seed, n)


def test_rows_15_to_17_do_not_apply_to_an_unbarred_galaxy_and_are_unchanged_for_the_default(prod):
    """D217 item 3: "Rows 15-17 are not applicable to it and unchanged for the Milky Way." A row that does not apply
    is the table's third status with its reason - never a pass by default (rule B9), never a failure of a galaxy
    for lacking what it does not have."""
    model = the_model(prod)
    rows = {q.n: q for q in spec.QUANTITIES}
    assert {n for n, q in rows.items() if q.only_if is not None} == {15, 16, 17}
    assert all(rows[n].only_if == ("bar_present", "yes") for n in (15, 16, 17))
    ensemble = {"bar_pattern_speed": [45.0] * 41, "bar_corotation_radius": [5.5] * 41}
    barred = run(model, grid=SMALL, layer=False)
    unbarred = run(model, {"bar_present": False}, SMALL, layer=False)
    for n in (15, 16, 17):
        on = spec.evaluate(rows[n], barred.fields, barred.decls, model.name, ensemble)
        off = spec.evaluate(rows[n], unbarred.fields, unbarred.decls, model.name, ensemble)
        assert on.status in ("pass", "fail") and "not applicable" not in on.reason, n
        assert off.status == "not-yet-computable" and off.reason == "not applicable: bar_present is 'no', and the row is of a galaxy where it is 'yes'", n
        assert off.value is None
    # Every other row reads the same on the two galaxies: the bar reaches no acceptance number with the layer off.
    for q in spec.QUANTITIES:
        if q.n in (15, 16, 17) or q.mode in ("statistical", "sweep"):
            continue
        a, b = (spec.evaluate(q, o.fields, o.decls, model.name) for o in (barred, unbarred))
        assert (a.status, a.value) == (b.status, b.value) or (a.value != a.value and b.value != b.value), q.n
    with pytest.raises(spec.SpecError, match="only_if is"):
        spec.Quantity(99, "x", "kpc", "bar_half_length", 1.0, 2.0, "pointwise", "x", "y", only_if=("bar_present",))  # type: ignore[arg-type]


def test_the_api_serves_an_unbarred_galaxy_with_nulls_for_the_bar_and_no_nan_anywhere(prod):
    """No NaN in "any ... API array or header of an unbarred galaxy": the bar's scalars travel as null (JSON has no
    NaN); every route that takes inputs answers for ``ngc_4414``; and an array holds a NaN only where the same
    route's array holds one for the same disc with its bar."""
    api = Service(grid=SMALL)
    wanted = ",".join((*BAR_NUMBERS, "bar_present", "bar_formation_time", "pattern_density_contrast", "gas_density_contrast", *pt.AMPLITUDE_FIELDS))
    got = api.handle("/api/arrays", f"template=ngc_4414&fields={wanted}")
    assert got.status == 200
    header, arrays = got.frame()
    assert all(header["scalars"][k] is None for k in BAR_NUMBERS) and header["scalars"]["bar_present"] == "no"
    assert header["scalars"]["bar_formation_time"] == pytest.approx(0.9054, abs=2e-3) and header["inputs"]["bar_present"] is False
    assert all(np.all(np.isfinite(a)) for a in arrays.values())
    b_v = json.dumps([{"name": b, "shape": "gaussian", "centre": c, "fwhm": 900.0} for b, c in (("B", 4400.0), ("V", 5500.0))])
    sector = {"r_min": ["1"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["1.5"]}
    for path, query in (("/api/region", sector), ("/api/clouds", sector), ("/api/clusters", sector), ("/api/remnants", sector),
                        ("/api/bright", {**sector, "n": ["500"]}), ("/api/render", {"filters": [b_v]}), ("/api/system", {"cell": ["300"], "index": ["0"]})):
        unbarred = api.handle(path, {**query, "template": ["ngc_4414"]})
        assert unbarred.status == 200, (path, unbarred.body[:300])
        head, body = wire.decode(unbarred.body)
        json.dumps(head, allow_nan=False)  # raises on a NaN or an infinity among the header's numbers
        assert head["inputs"]["bar_present"] is False, path
        spelled = {n: [json.dumps(v) if n == "mergers" else (str(int(v)) if n.endswith("_seed") else repr(v))]
                   for n, v in head["inputs"].items() if n != "bar_present"}
        barred = api.handle(path, {**query, **spelled})  # the same disc with no pin: the criterion bars it
        assert barred.status == 200, (path, barred.body[:300])
        barred_head, barred_body = wire.decode(barred.body)
        assert "bar_present" not in barred_head["inputs"], path

        def nan_arrays(arrays) -> set[str]:
            return {n for n, a in arrays.items() if a.dtype.kind == "f" and bool(np.isnan(a).any())}

        assert nan_arrays(body) <= nan_arrays(barred_body), (path, nan_arrays(body) - nan_arrays(barred_body))
