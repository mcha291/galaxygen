"""S26's measurements (BUILD_II Phase 1b, D175): the arm and bar amplitudes derived and seeded, the arm number drawn
from what the disc amplifies, and the two experimental inputs gone. **Since S56 (D215) the arm number is not drawn**:
the window that weighted the draw is evaluated at every radius and splits the arms' power among the arm numbers. What
is still true here is kept - the window, its constants, the amplitudes' sources - and the one test that read the
draw's odds states the law's split instead.

Every constant that entered level0 here was read from a source, and where the source is a table the
class means are recomputed from its rows rather than trusted (rule B9; S21 (a)'s A-14). Pinned as
measurements, never as targets.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, production
from galaxy.run import run
from galaxy.stages.pattern import AMPLITUDE_FIELDS, ARM_MULTIPLICITIES, BAR_CONTRAST_CAP, contrast_amplitude, swing_weight, swing_window

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)

# Elmegreen et al. 2011, ApJ 737, 32, Table 2 ("Bar and Arm Measurements"), 3.6 micron: NGC, Arm Class
# (F flocculent, M multiple arm, G grand design), peak m=2 Fourier amplitude (the bar's when barred),
# the arms' m=2 amplitude, the average arm-interarm contrast in magnitudes. Read on 2026-09-26.
ELMEGREEN_2011_TABLE_2 = """
300 M 0.13 0.08 0.6 | 337 F 0.32 0.18 0.9 | 428 F 0.30 0.12 1.0 | 628 M 0.20 0.1 0.9 | 986 G 0.63 0.28 0.9
1097 G 0.46 0.15 1.2 | 1313 F 0.32 0.16 1.3 | 1433 M 0.44 0.19 0.55 | 1512 M 0.33 0.16 0.8 | 1566 G 0.39 0.25 1.1
2500 F 0.13 0.1 0.6 | 2552 F 0.13 0.12 0.9 | 2805 M 0.18 0.07 1.2 | 2841 F 0.16 0.08 0.3 | 2903 M 0.31 0.07 0.7
3049 G 0.32 0.12 0.7 | 3147 M 0.10 0.07 0.4 | 3184 M 0.19 0.1 0.6 | 3198 M 0.29 0.18 0.9 | 3344 M 0.07 0.07 0.9
3351 M 0.27 0.12 0.4 | 3504 G 0.52 0.05 0.4 | 3627 M 0.33 0.18 1.05 | 3906 F 0.26 0.1 1.4 | 3938 M 0.11 0.075 0.7
3953 M 0.24 0.09 0.8 | 4254 M 0.18 0.15 1.2 | 4299 M 0.17 0.16 1.1 | 4314 G 0.47 0.25 2.3 | 4321 G 0.30 0.2 1.2
4450 M 0.19 0.05 0.6 | 4536 G 0.33 0.25 1.3 | 4579 M 0.23 0.065 0.45 | 4689 F 0.07 0.02 0.3 | 4725 M 0.30 0.2 1.2
4736 G 0.28 0.16 0.9 | 5055 F 0.13 0.09 0.35 | 5068 F 0.18 0.15 0.75 | 5147 F 0.08 0.07 0.8 | 5194 G 0.34 0.23 1.5
5248 G 0.42 0.3 1.1 | 5457 M 0.23 0.3 1.2 | 5713 F 0.31 0.12 0.7 | 7479 G 0.46 0.15 1.1 | 7552 G 0.62 0.3 1.1
7793 F 0.16 0.07 0.5
"""


def _rows():
    return [r.split() for r in ELMEGREEN_2011_TABLE_2.replace("\n", "|").split("|") if r.strip()]


@pytest.fixture(scope="module")
def basic():
    models, _, _ = production()
    # "basic" by name, deliberately (S46, D197): S26's rulings read basic's constants, which azimuthal shares.
    return next(m for m in models if m.name == "basic")


def test_the_arm_interarm_constants_are_the_tables_class_means(basic):
    """ARM_INTERARM_GRAND_DESIGN / _FLOCCULENT / _SCATTER reproduce Elmegreen et al. 2011 §4.2 from Table 2.

    The paper's sentence: 'The averages for all Hubble types combined are 1.14±0.44, 0.81±0.28, and
    0.75±0.35 in these three Arm Classes, respectively' (grand design, multiple arm, flocculent).
    """
    rows = _rows()
    assert len(rows) == 46
    by = {cls: np.array([[float(r[2]), float(r[3]), float(r[4])] for r in rows if r[1] == cls]) for cls in "GMF"}
    assert {k: len(v) for k, v in by.items()} == {"G": 13, "M": 20, "F": 13}
    contrast = {k: (v[:, 2].mean(), v[:, 2].std(ddof=1)) for k, v in by.items()}
    assert contrast["G"] == pytest.approx((1.14, 0.44), abs=0.005)
    assert contrast["M"] == pytest.approx((0.81, 0.28), abs=0.005)
    assert contrast["F"] == pytest.approx((0.75, 0.35), abs=0.005)
    c = {k: v.value for k, v in basic.constants.items()}
    assert c["ARM_INTERARM_GRAND_DESIGN"] == pytest.approx(contrast["G"][0], abs=0.005)
    assert c["ARM_INTERARM_FLOCCULENT"] == pytest.approx(contrast["F"][0], abs=0.005)
    assert c["ARM_INTERARM_SCATTER"] == pytest.approx(contrast["G"][1], abs=0.005)
    # The named alternative: the arms' own m = 2 Fourier amplitude, 0.21 +/- 0.08 for the grand designs.
    assert by["G"][:, 1].mean() == pytest.approx(0.207, abs=0.005) and by["G"][:, 0].mean() == pytest.approx(0.426, abs=0.005)


def test_a_contrast_in_magnitudes_becomes_a_cosine_amplitude():
    """(C - 1)/(C + 1) with C = 10^(0.4 mag): the peak-to-trough of one harmonic is the whole contrast."""
    assert contrast_amplitude(0.0) == 0.0
    assert contrast_amplitude(1.14) == pytest.approx(0.482, abs=1e-3)
    assert contrast_amplitude(0.75) == pytest.approx(0.332, abs=1e-3)
    assert contrast_amplitude(-1.0) == 0.0, "a negative draw is no arms, not anti-arms"
    a = contrast_amplitude(0.81)
    assert 2.5 * math.log10((1 + a) / (1 - a)) == pytest.approx(0.81, abs=1e-9)


def test_the_bar_amplitude_constants_are_the_s4g_tables_summary(basic):
    """BAR_CONTRAST_MEDIAN and _LOG_SCATTER: VizieR J/A+A/587/A160 tablea3.dat, column A2, 587 barred
    galaxies, read and reduced on 2026-09-26 — median 0.374, 16th-84th percentiles 0.214-0.609."""
    c = {k: v.value for k, v in basic.constants.items()}
    assert c["BAR_CONTRAST_MEDIAN"] == pytest.approx(0.374, abs=1e-3)
    assert c["BAR_CONTRAST_LOG_SCATTER"] == pytest.approx(math.log(0.609 / 0.214) / 2.0, abs=0.01)
    assert 0.6 <= BAR_CONTRAST_CAP < 1.0


def test_the_swing_window_is_the_reviews_rule_at_the_defaults(basic):
    """m X_m = 2/f_d and 1/f_d <= m <= 2/f_d at Gamma = 1 (Sellwood & Masters 2022 §4.2.3.2), scaled by the shear.

    2/f_d is **X at m = 1** - the Mestel identity X_m = 2/(m f_d), times m - and not X for two arms, which is
    1/f_d. From S26 until S56 this test, the function's variable and the field's about called it "X_2"; the value
    and the window were always those of m X_m, and only the words are corrected (D215 ruling 11)."""
    f = run(basic, only=("swing_x", "swing_arm_min", "swing_arm_max", "disc_dominance", "shear_rate", "arm_contrast_mean")).fields
    x_one, lo, hi = swing_window(f["disc_dominance"], f["shear_rate"], 1.0, 2.0)
    assert (x_one, lo, hi) == (f["swing_x"], f["swing_arm_min"], f["swing_arm_max"])
    assert x_one == pytest.approx(2.0 / f["disc_dominance"]) and hi == pytest.approx(2.0 * lo)
    assert lo * f["shear_rate"] == pytest.approx(1.0 / f["disc_dominance"])
    # Measured at S26: m X_m 3.33 (so X for two arms is 1.67), window 1.72-3.44, so m = 2 and 3 are amplified in
    # full and 4 at 0.78.
    assert x_one == pytest.approx(3.334, abs=0.01) and lo == pytest.approx(1.722, abs=0.01) and hi == pytest.approx(3.444, abs=0.01)
    weights = [swing_weight(m, lo, hi, 2.0, 3.0, 1.0, 0.5) for m in ARM_MULTIPLICITIES]
    assert weights == pytest.approx([1.0, 1.0, 0.784, 0.462, 0.199], abs=0.01)
    assert f["arm_contrast_mean"] == pytest.approx(contrast_amplitude(1.14), abs=1e-3), "m = 2 inside the window: the grand-design mean"


def test_the_window_closes_where_the_sources_say():
    lo, hi = 2.0, 4.0
    args = (lo, hi, 2.0, 3.0, 1.0, 0.5)
    assert swing_weight(2.0, *args) == swing_weight(4.0, *args) == 1.0
    assert swing_weight(lo * 2.0 / 3.0, *args) == 0.0, "X = SWING_X_DEAD: fewer arms than the disc amplifies"
    assert swing_weight(hi * 2.0, *args) == 0.0, "X = SWING_X_FLOOR: more arms than it can carry"
    assert 0.0 < swing_weight(1.6, *args) < 1.0 and 0.0 < swing_weight(6.0, *args) < 1.0
    assert swing_weight(3.0, 4.0, 8.0, *args[2:]) == pytest.approx(math.log(3.0 / (8.0 / 3.0)) / math.log(4.0 / (8.0 / 3.0)))


def _odds(basic, inputs, n=60):
    ms, arms, bars = [], [], []
    for s in range(n):
        f = run(basic, {"pattern_seed": s, **inputs}, grid=COARSE, only=("arm_multiplicity", "arm_contrast", "bar_contrast")).fields
        ms.append(float(f["arm_multiplicity"])); arms.append(float(f["arm_contrast"])); bars.append(float(f["bar_contrast"]))
    return np.array(ms), np.array(arms), np.array(bars)


def _power(model, inputs, grid=COARSE):
    """(R, each mode's share of each ring's arm power, each mode's share of the disc's mass-weighted arm power)."""
    o = run(model, inputs, grid=grid, only=(*AMPLITUDE_FIELDS, "disc_surface_density"))
    R = o.grid.R
    power = np.stack([np.asarray(o.fields[n]) for n in AMPLITUDE_FIELDS]) ** 2
    total = power.sum(axis=0)
    ring = np.where(total > 0.0, power / np.where(total > 0.0, total, 1.0), 0.0)
    weighted = (np.asarray(o.fields["disc_surface_density"]) * R * np.gradient(R))[None, :] * power
    return R, ring, weighted.sum(axis=1) / weighted.sum()


def test_the_arm_number_follows_the_discs_share_of_the_rotation(basic):
    """The lever the pitch-shear relation never had (debt #22): disc dominance moves the arm number.

    **S56 (D215): the draw this test pinned has retired.** From S26 to S55 the arm number was one seeded draw
    weighted by the swing window at 2.2 scale lengths, and this test read its odds: 200 seeds at S26 gave
    {2: 47, 3: 59, 4: 55, 5: 27, 6: 12} at the defaults, {3: 13, 4: 55, 5: 68, 6: 64} for a disc holding 30% of its
    rotation (the flocculent regime, m >= 4) and {2: 81, 3: 81, 4: 35, 5: 3} for one holding 76%. What it claimed
    is still true and is now a statement of the law, with no seed in it: the same window, evaluated at every radius,
    splits the arms' power among the arm numbers - so the claims are about where the power is, not about majorities
    of draws, and every pattern seed gives the same split.

    The split at the defaults on the production grid, **on the window D215's third gate turn ruled** (ruling 11:
    the local X at m = 1; the first two passes of S56 built it on half of that, and read 0.50 / 0.35 / 0.15 / 0 / 0
    at 2 kpc): 0.12 / 0.24 / 0.24 / 0.23 / 0.17 at 2 kpc, 0 / 0.15 / 0.28 / 0.28 / 0.28 at 8 kpc, and the six-armed
    mode alone at 12 kpc - three to six arms share the inner disc, four to six the solar radius, and no ring of the
    default disc is two-armed. That is the law as ruled, and it does not meet what the sources of this file's first
    reading say of real discs (D'Onghia 2015: two arms at 4.5 kpc, five or six at R0): D215 ruling 12 opens that as
    a debt against the blind reading, to be re-read at the close of the bar-driven two-armed pattern's phase, and
    it is not closed with a constant here.
    """
    R, ring, _ = _power(basic, {}, grid=GridSpec())
    for r, want in ((2.0, (0.12, 0.24, 0.24, 0.23, 0.17)), (8.0, (0.0, 0.15, 0.28, 0.28, 0.28)), (12.0, (0.0, 0.0, 0.0, 0.0, 1.0))):
        assert ring[:, int(np.argmin(np.abs(R - r)))].tolist() == pytest.approx(want, abs=0.01), r
    # Over the whole disc, by mass, of the published amplitudes (the coarse grid here): 0.01 / 0.16 / 0.23 / 0.28 /
    # 0.32 at the defaults. The lever still points the way S26 found it - the more of its rotation a disc holds, the
    # fewer its arms - but its levels are the corrected window's: a disc holding 30% of its rotation carries 0.98 of
    # its arm power in five and six arms and none in two or three; one holding 76% carries 0.34 in two and three
    # (the defaults: 0.17), and is not "two- or three-armed" as the draw's odds made it at S26.
    # (On the X / 2 window: 0.250 / 0.272 / 0.215 / 0.153 / 0.111; 0.912 in four to six; 0.777 in two and three.)
    _, _, default = _power(basic, {})
    _, _, halo = _power(basic, {"disc_spin": 0.03, "baryon_retention": 0.15})
    _, _, disc = _power(basic, {"disc_spin": 0.01, "baryon_retention": 0.5})
    assert default.tolist() == pytest.approx([0.014, 0.157, 0.231, 0.281, 0.316], abs=5e-3)
    # S58 (D217 items 1-3): were 0.980 in five and six arms and under 1e-3 in two and three. **This disc is unbarred
    # by the criterion itself** - it holds 0.30 of its rotation, a bar would take 15 Gyr to form and the disc is 9.6
    # Gyr old - so its published amplitudes carry no bar's taper and its inner rings, where the low arm numbers
    # live, are in the sum: 0.819 in five and six arms, 0.017 in two and three (the two-armed mode still none). The
    # split itself, ring by ring, is the one it was; the lever points the same way.
    assert run(basic, {"disc_spin": 0.03, "baryon_retention": 0.15}, grid=COARSE, only=("bar_present",)).fields["bar_present"] == "no"
    assert halo[3:].sum() == pytest.approx(0.819, abs=5e-3), "a halo-dominated disc is multi-armed"
    assert halo[0] == 0.0 and halo[:2].sum() == pytest.approx(0.017, abs=2e-3), "two arms cannot be amplified where the disc holds so little of the rotation, and three barely"
    assert disc.tolist() == pytest.approx([0.130, 0.213, 0.237, 0.225, 0.195], abs=5e-3)
    assert halo[:2].sum() < default[:2].sum() < disc[:2].sum() == pytest.approx(0.343, abs=5e-3), "disc dominance moves the arm number"
    # The label follows: 6 at the defaults on every seed, 6 for the halo-dominated disc (not a number on the two
    # seeds of sixty that draw no arm amplitude at all), 4 for the disc-dominated one - on 58 seeds of sixty, and 5 on
    # two: the label weighs the published amplitudes, the saturation is in them and is the one seeded thing in the
    # weighting (through the drawn amplitudes), and that disc's four- and five-armed shares are 0.24 and 0.23. The
    # split itself has no seed in it (below). (On the X / 2 window: 3, 6 and 2, on every seed.)
    label, _, _ = _odds(basic, {})
    label_halo, arms_halo, _ = _odds(basic, {"disc_spin": 0.03, "baryon_retention": 0.15})
    label_disc, arms_disc, _ = _odds(basic, {"disc_spin": 0.01, "baryon_retention": 0.5})
    assert set(label) == {6.0}
    # S58 (D217 item 5): was 58 fours and 2 fives - the saturation reads the bar's body's depth where it read the
    # cosine bar's amplitude times its taper, and on those two seeds the saturated rings weigh the other way: 4 on
    # every one of the sixty.
    assert sorted(label_disc.tolist()).count(4.0) == 60
    assert set(label_halo[np.isfinite(label_halo)]) == {6.0} and int(np.isnan(label_halo).sum()) == 2
    assert np.all(arms_halo[np.isnan(label_halo)] == 0.0), "no arms, no arm number"
    assert arms_halo.mean() < arms_disc.mean(), "the flocculent regime's arms are weaker (Elmegreen et al. 2011 §4.2)"
    # And the split has no seed in it: another pattern seed, the same shares ring by ring.
    _, again, _ = _power(basic, {"pattern_seed": 11})
    assert np.allclose(again, _power(basic, {})[1], rtol=1e-12, atol=1e-15)


def test_the_amplitudes_are_seeded_about_derived_means(basic):
    ms, arms, bars = _odds(basic, {})
    assert len(set(np.round(arms, 6))) > 50 and len(set(np.round(bars, 6))) > 50, "the residual is drawn"
    assert np.all((0.0 <= arms) & (arms < 1.0)) and np.all((0.0 < bars) & (bars <= BAR_CONTRAST_CAP))
    # The bar's median sits at the S4G median and its scatter at the table's percentiles (log-normal);
    # the arms' mean at the derived grand-design value less what the magnitude scatter clips at zero.
    assert np.median(bars) == pytest.approx(0.374, abs=0.06)
    assert arms.mean() == pytest.approx(0.46, abs=0.06)
    f = run(basic, only=("arm_contrast_mean",)).fields
    assert f["arm_contrast_mean"] == pytest.approx(0.4815, abs=1e-3)


def test_the_experimental_inputs_are_gone_and_seven_controls_remain():
    controls = [i for i in INPUTS.values() if i.kind == "control"]
    assert len(controls) == 7, sorted(i.name for i in controls)
    assert not {"arm_amplitude", "bar_amplitude"} & set(INPUTS)


def test_rows_15_to_17_did_not_move(judged):
    """Phase 1b's gate: the amplitudes do not enter the bar's length, corotation or pattern speed."""
    # basic's verdicts by name, deliberately (S46, D197): the gate was set on basic; the rows are radial.
    results = {r.n: r for r in judged["basic"]}
    assert results[15].value == pytest.approx(5.20971, abs=1e-4) and results[15].status == "fail"  # the recorded miss, #80
    assert results[16].value == pytest.approx(41.1036, abs=1e-3) and results[16].status == "pass"
    assert results[17].value == pytest.approx(6.08381, abs=1e-4) and results[17].status == "pass"
