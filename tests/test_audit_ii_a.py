"""Audit II, aim (a) — every prediction the register and spec._MISSES made since S13, run (S21, branch
session-21-a, Fable 5.1, D130). AUDIT_II_A.md is the list; this file is its measurements, pinned loosely
as numbers to spot a regression by and never as targets. Every probe substitutes one function with
the repo unchanged (D114); nothing here fixes anything.

Stated precision (S19's lesson): a pointwise row is pinned to about a tenth of its window, a
verdict to the window itself, a residual to 0.01 sigma.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.registry import INPUTS, MergerEvent
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import halo, sfh
from galaxy.stages.chemistry import age_bin_edges, migration_width, transport
from galaxy.stages.disc import PC_PER_KPC
from test_audit import Q, R_SUN, inside, with_constant

KICK = sfh.radial_transport
CORE = halo.angular_momentum_core
FIRST = sfh.first_infall
SFR = sfh.star_formation_rate
TOOMRE = sfh.toomre_threshold
SEEDS = [name for name, inp in INPUTS.items() if inp.kind == "seed"]
THICK = ("thick_disc_scale_length", "thick_disc_stellar_mass", "thick_thin_surface_density_ratio",
         "thick_thin_local_density_ratio", "thick_disc_scale_height", "thin_disc_stellar_mass", "sfr",
         "v_tangential_sun", "thin_disc_scale_length")
VALLEY = ("alpha_sequence", "alpha_dip_depth", "alpha_split", "alpha_fe_history", "sfr_surface_density_history")


@pytest.fixture(scope="module")
def simple(prod):
    return prod[0].get("simple")


@pytest.fixture(scope="module")
def advanced(prod):
    return prod[0].get("advanced")


def fast_law(tau_first):
    def law(t, tau, span):
        return FIRST(t, np.full_like(tau, tau_first), span)
    return law


class Window:
    """Kennicutt's rate times ``boost`` inside [t0, t1), zero inside [c0, c1); one instance per run."""

    def __init__(self, boost, t0, t1, c0, c1, n_t=2000, t_max=13.8):
        self.boost, self.t0, self.t1, self.c0, self.c1, self.dt, self.calls = boost, t0, t1, c0, c1, t_max / n_t, 0

    def __call__(self, gas, norm, index, threshold):
        t = (self.calls + 0.5) * self.dt
        self.calls += 1
        if self.c0 <= t < self.c1:
            return np.zeros_like(np.asarray(gas, dtype=float))
        if self.t0 <= t < self.t1:
            return SFR(gas, norm * self.boost, index, threshold)
        return SFR(gas, norm, index, threshold)


def r0_histogram(o):
    """The [alpha/Fe] mass distribution at R0 as chemistry_dtd builds it (D126), 0.02 dex bins from -0.3."""
    f, R, t = o.fields, o.grid.R, o.grid.t
    dt = o.grid.spec.t_max / o.grid.spec.n_t
    formed = PC_PER_KPC * f["sfr_surface_density_history"] * dt * (2.0 * math.pi * R * o.grid["R"].width * PC_PER_KPC**2)[:, None]
    afe = np.nan_to_num(f["alpha_fe_history"], nan=0.0)
    edges, age = age_bin_edges(o.grid.spec.t_max), o.grid.spec.t_max - t
    at_sun = int(np.argmin(np.abs(R - R_SUN)))
    w = np.zeros_like(formed)
    for b in range(edges.size - 1):
        in_bin = (age >= edges[b]) & (age < edges[b + 1])
        if in_bin.any():
            K = transport(R, float(migration_width(0.5 * (edges[b] + edges[b + 1]), o.inputs["migration_efficiency"])))
            w[:, in_bin] = formed[:, in_bin] * K[:, at_sun][:, None]
    hist, _ = np.histogram(afe, bins=np.arange(-0.3, 0.71, 0.02), weights=w)
    return hist / hist.sum()


# --- debt #50: the stars moved through both kernels -----------------------------------------------------

def kick_then_churn(scale: float, eff: float):
    def moved(formed, spread, R, dR):
        out = KICK(formed, spread, R, dR)
        n_t, t_max = formed.shape[1], 13.8
        age = t_max - (np.arange(n_t) + 0.5) * t_max / n_t
        area, edges, res = 2.0 * math.pi * R * dR, age_bin_edges(t_max), np.array(out, copy=True)
        for b in range(edges.size - 1):
            in_bin = (age >= edges[b]) & (age < edges[b + 1])
            sigma = scale * float(migration_width(0.5 * (edges[b] + edges[b + 1]), eff))
            if in_bin.any() and sigma > 0.0:
                res[:, in_bin] = (transport(R, sigma).T @ (out[:, in_bin] * area[:, None])) / area[:, None]
        return res
    return moved


def test_debt_50s_prediction_ran_the_stars_moved_through_both_kernels_and_failed(simple, monkeypatch):
    """#50: row 9 would land between 0.0455 and 0.221. It reads 0.266 — above the bracket, because the bracket
    compared a fraction with a ratio (0.221 of the catalogue is 0.284 as thick/thin) — and the churn applied to
    the mass takes row 4 to 3.5 kpc and row 3 to 244.9: the chemistry's kernel is ruled out by the disc's
    structure the moment the mass follows it (A-1, A-2)."""
    eff = float(INPUTS.get("migration_efficiency").default)
    monkeypatch.setattr(sfh, "radial_transport", kick_then_churn(1.0, eff))
    f = run(simple, only=THICK).fields
    assert f["thick_thin_surface_density_ratio"] == pytest.approx(0.2655, abs=0.01) and f["thick_thin_surface_density_ratio"] > 0.221
    assert f["thin_disc_scale_length"] == pytest.approx(3.49, abs=0.1) and not inside(4, f["thin_disc_scale_length"])
    assert f["v_tangential_sun"] == pytest.approx(244.9, abs=0.5) and not inside(3, f["v_tangential_sun"])
    assert f["thick_disc_scale_length"] == pytest.approx(2.73, abs=0.1) and f["thick_disc_stellar_mass"] == pytest.approx(9.59e9, rel=0.02)
    # the kick is nothing beside the churn: the churn alone reads the same to three figures
    monkeypatch.setattr(sfh, "radial_transport", lambda formed, spread, R, dR: kick_then_churn(1.0, eff)(formed, np.zeros_like(spread), R, dR))
    g = run(simple, only=THICK).fields
    assert g["thick_thin_surface_density_ratio"] == pytest.approx(f["thick_thin_surface_density_ratio"], abs=0.002)
    # rows 9 and 11 inside together for the first time, at share 0.7 - with row 5 out the other way (2.56)
    monkeypatch.setattr(sfh, "radial_transport", kick_then_churn(1.0, eff))
    h = run(simple, {"mergers": (MergerEvent(3.8, 0.25, 0.7, "probe"), MergerEvent(8.8, 0.02, 0.01, "probe"))}, only=THICK).fields
    assert inside(9, h["thick_thin_surface_density_ratio"]) and inside(11, h["thick_disc_stellar_mass"])
    assert h["thick_disc_scale_length"] == pytest.approx(2.56, abs=0.1) and not inside(5, h["thick_disc_scale_length"])


# --- D121: the bar's prediction, run for the first time -------------------------------------------------

def buckled(extra: float, r_half_scale: float = 1.0):
    def core(R, j, M_d, R_d, mu):
        mass, r_half, R_c, j_mean = CORE(R, j, M_d, R_d, mu)
        return mass + extra, r_half * r_half_scale, R_c, j_mean
    return core


def test_d121s_bar_prediction_ran_row_3_held_and_row_14_did_not(simple, monkeypatch):
    """7e9 buckled into the spheroid at the derived scale radius: row 3 249.6 (D121 said 249.4 - held), rows 12
    and 13 inside, row 14 144 (D121 said 123 - dead by 21 km/s). And no concentration lands rows 12 and 14
    together: at four times the half-mass radius row 14 still reads 121, its floor set by the enclosed mass."""
    monkeypatch.setattr(halo, "angular_momentum_core", buckled(7.0e9))
    f = run(simple, only=("v_tangential_sun", "bulge_stellar_mass", "bulge_stellar_fraction", "bulge_velocity_dispersion")).fields
    assert f["v_tangential_sun"] == pytest.approx(249.6, abs=0.3) and inside(3, f["v_tangential_sun"])
    assert inside(12, f["bulge_stellar_mass"]) and inside(13, f["bulge_stellar_fraction"])
    assert f["bulge_velocity_dispersion"] == pytest.approx(144.4, abs=1.5)
    for scale, row3, row14 in ((2.0, 248.4, 123.8), (4.0, 245.9, 121.5)):
        monkeypatch.setattr(halo, "angular_momentum_core", buckled(6.3e9, scale))
        g = run(simple, only=("v_tangential_sun", "bulge_stellar_mass", "bulge_velocity_dispersion")).fields
        assert inside(12, g["bulge_stellar_mass"]) and g["v_tangential_sun"] == pytest.approx(row3, abs=0.3)
        assert g["bulge_velocity_dispersion"] == pytest.approx(row14, abs=1.5) and not inside(14, g["bulge_velocity_dispersion"])


# --- D128: the valley's replacement prediction, attacked -----------------------------------------------

def test_debt_27_a_burst_inside_the_alpha_fall_opens_a_mode_short_of_the_plateau(advanced, monkeypatch):
    """D128 said a thick mode needs a rising first phase cut within ~1 Gyr. Built as a x5 burst at 1-2 Gyr on the
    fast first infall with the star formation cut 2-3 Gyr, the R0 histogram grows a mode at +0.35 holding a tenth
    of the mass in one 0.02 dex bin, twice the plateau spike - the first alpha-rich mode the model has ever made
    that is not the spike (A-4). The same burst placed at t < 0.8 Gyr, before the first Ia iron, forms its stars
    at the plateau and makes none: the timing is the refinement."""
    monkeypatch.setattr(sfh, "first_infall", fast_law(0.55))
    monkeypatch.setattr(sfh, "star_formation_rate", Window(5.0, 1.0, 2.0, 2.0, 3.0))
    o = run(advanced, only=VALLEY)
    s = r0_histogram(o)
    assert o.fields["alpha_sequence"] == "bimodal_wide" and o.fields["alpha_split"] == pytest.approx(0.21, abs=0.03)
    plain, plateau = s[27:35], s[36:38].sum()
    assert plain.max() == pytest.approx(0.103, abs=0.02) and -0.3 + 0.02 * (27 + int(np.argmax(plain)) + 0.5) == pytest.approx(0.35, abs=0.03)
    assert plain.max() > 1.5 * plateau and plateau == pytest.approx(0.051, abs=0.015)
    monkeypatch.setattr(sfh, "star_formation_rate", Window(5.0, 0.0, 0.8, 0.8, 1.5))
    o2 = run(advanced, only=VALLEY)
    s2 = r0_histogram(o2)
    assert o2.fields["alpha_sequence"] == "bimodal_wide" and s2[27:35].max() < 0.03 and s2[36:38].sum() == pytest.approx(0.123, abs=0.02)


# --- debt #19 / #49: the cut-only law ----------------------------------------------------------------------

def test_debt_19_a_cut_only_law_lands_rows_9_and_11_together_and_row_5_short(simple, monkeypatch):
    """Rows 9 and 11's pre-committed reading run: with the early gas left as gas at the merger (star formation
    off from 1 to 3.8 Gyr on the fast first infall) rows 8, 9, 10 and 11 are inside together for the first time
    and row 5 reads 1.61, 0.2 short - so by #19's own sentence the split criterion is what is wrong (A-5)."""
    monkeypatch.setattr(sfh, "first_infall", fast_law(0.55))
    monkeypatch.setattr(sfh, "star_formation_rate", Window(1.0, 0.0, 0.0, 1.0, 3.8))
    f = run(simple, only=THICK).fields
    assert all(inside(n, f[k]) for n, k in ((8, "thick_thin_local_density_ratio"), (9, "thick_thin_surface_density_ratio"), (10, "thin_disc_stellar_mass"), (11, "thick_disc_stellar_mass")))
    assert f["thick_disc_scale_length"] == pytest.approx(1.61, abs=0.05) and not inside(5, f["thick_disc_scale_length"])
    assert f["thick_disc_scale_height"] == pytest.approx(1095.0, abs=20.0) and f["sfr"] == pytest.approx(1.27, abs=0.05)


# --- debt #48: the ensemble's median -------------------------------------------------------------------------

def masses(model, draws):
    return np.array([float(run(model, {s: d for s in SEEDS}, only=("black_hole_mass",)).fields["black_hole_mass"]) for d in draws])


def test_debt_48_the_ensembles_median_residual_sits_half_a_sigma_low(simple):
    """#48 said row 18's median is the mean relation at any width. The 41-draw diagonal the spec judges every
    statistical row on has a median residual of -0.58 sigma, 2.9 standard errors of a 41-sample median from
    zero, so the row's median moves with the width (1.97e7 at 0.28 dex, 9.9e6 at 0.8) while the verdict does
    not; the next diagonal reads -0.10 (A-6, debt #51)."""
    m28, m50 = masses(simple, range(41)), masses(with_constant(simple, "BLACK_HOLE_SCATTER", 0.5), range(41))
    z = np.log10(m50 / m28) / 0.22
    assert np.median(z) == pytest.approx(-0.577, abs=0.01) and 1.2533 / math.sqrt(41) < 0.2
    assert np.median(m28) == pytest.approx(1.97e7, rel=0.02) and np.allclose(m28 / 10 ** (0.28 * z), 2.86e7, rtol=0.01)
    assert np.median(masses(with_constant(simple, "BLACK_HOLE_SCATTER", 0.8), range(41))) == pytest.approx(9.9e6, rel=0.03)
    z2 = np.log10(masses(with_constant(simple, "BLACK_HOLE_SCATTER", 0.5), range(41, 82)) / masses(simple, range(41, 82))) / 0.22
    assert np.median(z2) == pytest.approx(-0.10, abs=0.03)


# --- the advanced row 22 miss: the inner gas ------------------------------------------------------------------

def test_the_advanced_row_22_does_not_see_the_inner_reservoir(advanced, monkeypatch):
    """The miss's prediction named the gas inside 4 kpc. Emptied to the Galaxy's few 1e8 (the threshold capped at
    5 Msun/pc2 there) the row reads -0.0699, unmoved; capped at the R0 value everywhere inside R0 it reads -0.0794,
    further out. The row is the gas held in its own 4-12 kpc window, and its pre-committed reading - the wind's
    tilt - applies (A-7)."""
    R = run(advanced, only=("sf_threshold_surface_density",)).grid.R

    def capped(rule):
        def f(kappa, alpha, sigma_g, G):
            return rule(TOOMRE(kappa, alpha, sigma_g, G))
        return f

    monkeypatch.setattr(sfh, "toomre_threshold", capped(lambda c: np.where(R < 4.0, np.minimum(c, 5.0), c)))
    o = run(advanced, only=("metallicity_gradient", "gas_surface_density"))
    gas = np.asarray(o.fields["gas_surface_density"], dtype=float)
    assert np.trapezoid(np.where(R < 4.0, gas, 0.0) * 2.0 * math.pi * R, R) * 1.0e6 < 5.0e8
    assert o.fields["metallicity_gradient"] == pytest.approx(-0.0699, abs=0.0005)
    crit_sun = float(np.interp(R_SUN, R, TOOMRE(run(advanced, only=("epicyclic_frequency",)).fields["epicyclic_frequency"], 0.69, 6.0, advanced.constants["G"].value)))
    monkeypatch.setattr(sfh, "toomre_threshold", capped(lambda c: np.minimum(c, crit_sun)))
    assert run(advanced, only=("metallicity_gradient",)).fields["metallicity_gradient"] == pytest.approx(-0.0794, abs=0.001)
    monkeypatch.setattr(sfh, "toomre_threshold", capped(lambda c: np.full_like(c, 5.0)))
    assert run(advanced, only=("metallicity_gradient",)).fields["metallicity_gradient"] == pytest.approx(-0.0633, abs=0.001)


# --- debt #46: the pre-committed two-parameter sweep --------------------------------------------------------

def test_debt_46s_pre_committed_sweep_cannot_discriminate(advanced):
    """#46 named rows 3, 19 and v_esc(R0) as the sweep's judges. Row 19 is the input and never moves; v_esc(R0) is
    inside 530-580 at every w; only row 3 is left, and a one-row sweep is a fit (A-8)."""
    for w, row3, v_esc in ((0.6, 230.3, 544.1), (1.0, 249.3, 558.9), (1.3, 267.8, 577.0)):
        m = with_constant(with_constant(advanced, "CONTRACTION_A", 1.6), "CONTRACTION_W", w)
        o = run(m, only=("v_tangential_sun", "escape_velocity", "halo_virial_mass"))
        assert o.fields["v_tangential_sun"] == pytest.approx(row3, abs=0.5) and o.fields["halo_virial_mass"] == 1.1e12
        assert 530.0 < np.interp(R_SUN, o.grid.R, o.fields["escape_velocity"]) < 580.0
        assert np.interp(R_SUN, o.grid.R, o.fields["escape_velocity"]) == pytest.approx(v_esc, abs=1.0)


# --- the spheroid's constant, the kernel's width, the heating constant: the smaller predictions ------------

def test_the_distributions_mu_lands_rows_3_and_12_and_loses_rows_2_and_14(simple):
    """Row 12's entry: across mu = 1.06-1.40 the spheroid runs 1.46e10 down to 5.6e9 - reproduced. At 1.06 rows 3,
    12 and 13 are inside and rows 2 (1.14) and 14 (146) are out: the constant is not a lever (A-9)."""
    lo = run(with_constant(simple, "ANGULAR_MOMENTUM_MU", 1.06), only=("bulge_stellar_mass", "v_tangential_sun", "sfr", "bulge_velocity_dispersion", "hydrogen_mass_30kpc")).fields
    assert lo["bulge_stellar_mass"] == pytest.approx(1.46e10, rel=0.02) and inside(12, lo["bulge_stellar_mass"])
    assert lo["v_tangential_sun"] == pytest.approx(249.4, abs=0.3) and inside(3, lo["v_tangential_sun"])
    assert lo["sfr"] == pytest.approx(1.14, abs=0.03) and lo["bulge_velocity_dispersion"] == pytest.approx(145.6, abs=1.5)
    assert lo["hydrogen_mass_30kpc"] == pytest.approx(7.53e9, rel=0.02)
    hi = run(with_constant(simple, "ANGULAR_MOMENTUM_MU", 1.4), only=("bulge_stellar_mass",)).fields
    assert hi["bulge_stellar_mass"] == pytest.approx(5.6e9, rel=0.03)


def test_debt_28_the_narrower_kernel_lands_row_23_with_the_ratio_on_the_wrong_side(advanced):
    """S9's sweep: 2.5 kpc at 8 Gyr reads row 23 at -0.039 with young/old 1.6. Now: -0.048 (inside) with 1.22,
    under the observed 1.75; at 2.0 kpc the old gradient is steeper than the young (0.81). The ratio, not the
    row, is the discriminant, and it convicts the old stars' starting point (A-10)."""
    for eff, old, ratio in ((2.5, -0.048, 1.22), (2.0, -0.0734, 0.81)):
        f = run(advanced, {"migration_efficiency": eff}, only=("metallicity_gradient_old", "metallicity_gradient_young", "metallicity_gradient")).fields
        assert f["metallicity_gradient_old"] == pytest.approx(old, abs=0.002)
        assert f["metallicity_gradient_young"] / f["metallicity_gradient_old"] == pytest.approx(ratio, abs=0.05)
        assert f["metallicity_gradient"] == pytest.approx(-0.0698, abs=0.0005)  # the present-day gas does not migrate
    assert inside(23, run(advanced, {"migration_efficiency": 2.5}, only=("metallicity_gradient_old",)).fields["metallicity_gradient_old"])


def test_debt_42_the_advanced_row_6_lands_at_74_not_78(advanced):
    """The advanced row 6 miss said MERGER_HEATING would have to fall below 78 to land it alone: 78 reads 351.4 and
    75 reads 350.3, both out; 70 reads 348.7. The number is 74, and the direction held."""
    for k, h in ((78.0, 351.4), (75.0, 350.3), (70.0, 348.7)):
        v = run(with_constant(advanced, "MERGER_HEATING", k), only=("thin_disc_scale_height",)).fields["thin_disc_scale_height"]
        assert v == pytest.approx(h, abs=0.5) and inside(6, v) == (k < 74.0)


def test_the_second_diagonal_moves_rows_16_and_17_and_not_their_verdicts(simple):
    """The statistical rows are judged on seeds 0-40. Seeds 41-81 read row 16 at 41.1 (42.8) and row 17 at 5.94
    (5.70): both verdicts hold, so the fixed sample decides row 18's number (debt #51) and not these."""
    vals = {"bar_pattern_speed": [], "bar_corotation_radius": []}
    for d in range(41, 82):
        f = run(simple, {s: d for s in SEEDS}, only=tuple(vals)).fields
        for k in vals:
            vals[k].append(float(f[k]))
    assert np.median(vals["bar_pattern_speed"]) == pytest.approx(41.1, abs=0.3) and inside(16, np.median(vals["bar_pattern_speed"]))
    assert np.median(vals["bar_corotation_radius"]) == pytest.approx(5.94, abs=0.05) and inside(17, np.median(vals["bar_corotation_radius"]))


# --- row 7: the constant's citation, read (A-14) -----------------------------------------------------------

def test_row_7_is_green_on_an_adopted_round_number_and_out_on_the_measured_one(simple, advanced):
    """MERGER_HEATING = 88.8 is derived from sigma_W = 35 km/s cited to Bensby, Feltzing & Lundstrom 2003. Read at
    S21 (a), that 35 is their Table 1's adopted 'characteristic' value for a selection function, with no
    uncertainty; the measurement the same paper quotes is Soubiran et al. 2003's 39 +/- 4. Net of the model's
    27.06 km/s that is a constant of 112.3, which reads row 7 at 1193 (out) and row 3 at 250.97 (in): the two
    rows trade across the source's own error bar, and row 7's window ends at sigma_W = 37.1 (101.5)."""
    for sigma_w, k, row7, row3 in ((39.0, 112.3, 1193.0, 250.97), (37.1, 101.5, 1080.0, 251.00)):
        assert math.sqrt(sigma_w**2 - 27.06**2) / 0.25 == pytest.approx(k, abs=0.1)
        f = run(with_constant(simple, "MERGER_HEATING", k), only=("thick_disc_scale_height", "v_tangential_sun")).fields
        assert f["thick_disc_scale_height"] == pytest.approx(row7, abs=3.0) and f["v_tangential_sun"] == pytest.approx(row3, abs=0.05)
    assert not inside(7, 1193.0) and inside(3, 250.97)
    assert run(with_constant(advanced, "MERGER_HEATING", 112.3), only=("thin_disc_scale_height",)).fields["thin_disc_scale_height"] == pytest.approx(368.0, abs=1.0)
