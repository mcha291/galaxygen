"""The disc stage, and S1's gate: the joint fit, stated as a prediction that can fail.

GALAXY_PLAN.md §5b sets S1's gate as "λ_d = 0.0144 from a joint fit to stellar
mass and scale length". That is a prediction (rule B4), and it is tested here as
one rather than assumed. It fails: run inside this model's own definitions the
fit returns 0.0173, because ruling 8 inferred 0.0144 against R_vir = 255 kpc —
a different overdensity at a different mass — while MMW98's relation takes r₂₀₀,
which is 212.9 kpc here. The argument of ruling 8 survives untouched; its
arithmetic does not (DECISIONS.md D30, debt #10).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS
from galaxy.run import run
from galaxy.stages.disc import disc_circular_velocity, freeman_circular_velocity, scale_length

G = 4.300917270e-6
R_SUN = 8.2

# The two observables the fit is against, from acceptance rows 1 and 4.
STELLAR_MASS = 5.0e10
SCALE_LENGTH = 2.6


def out(model, **inputs):
    return run(model, inputs or None)


# --- the gate ----------------------------------------------------------------


def test_joint_fit_reproduces_the_defaults(model):
    """Invert both observables and check they return the registry's defaults.

    Two parameters, two observables, as GALAXY_INPUTS.md §6 describes: m_d is
    pinned by the stellar mass and λ_d by the scale length given R₂₀₀.
    """
    o = out(model)
    R200 = o.fields["halo_virial_radius"]
    f_b = 0.152177

    fitted_spin = math.sqrt(2.0) * SCALE_LENGTH / R200
    fitted_retention = STELLAR_MASS / (f_b * o.fields["halo_virial_mass"])

    assert fitted_spin == pytest.approx(INPUTS["disc_spin"].default, abs=5e-5)
    # Retention is *not* fitted to the stellar mass alone: the budget it names is
    # stars plus gas, and the gas is 8e9 of it (row 20). Fitting it here would tune
    # a defined parameter to cover for the missing gas phase (rule B10).
    with_gas = (STELLAR_MASS + 8.0e9) / (f_b * o.fields["halo_virial_mass"])
    assert with_gas == pytest.approx(INPUTS["baryon_retention"].default, abs=0.02)
    assert fitted_retention < INPUTS["baryon_retention"].default


def test_the_gate_prediction_of_0_0144_is_dead(model):
    """Ruling 8's number, used with this model's R₂₀₀, misses the measured scale length."""
    o = out(model)
    with_ruling_8 = scale_length(0.0144, o.fields["halo_virial_radius"])
    assert with_ruling_8 == pytest.approx(2.17, abs=0.02)
    assert abs(with_ruling_8 - SCALE_LENGTH) > 0.4
    # And the value it *was* inferred against reproduces 2.6 kpc, which is the diagnosis.
    assert scale_length(0.0144, 255.0) == pytest.approx(SCALE_LENGTH, abs=0.02)
    # Both values sit inside Burkert+10's λ_d = 0.01-0.03 for m_d ≈ 0.05, so ruling 8's
    # argument — that the Milky Way is typical, not a 1.9σ outlier — is untouched.
    assert 0.01 <= 0.0144 <= 0.03 and 0.01 <= INPUTS["disc_spin"].default <= 0.03


def test_the_255_kpc_is_a_top_hat_radius_not_R200():
    """The diagnosis behind D30, as arithmetic rather than assertion.

    GALAXY_INPUTS.md §6 pairs R_vir = 255 kpc with M_vir ≈ 0.9 × 10¹² M☉ [Huang+16].
    Ask what overdensity that pair implies: it is ~95 ρ_crit, not 200. That is the
    Bryan & Norman top-hat value Δ_vir ≈ 101 for Ω_m = 0.3 at z = 0 [recall: Bryan &
    Norman 1998], so the two radii are two different definitions and MMW98's r₂₀₀ is
    the one this model computes. Nothing about the Milky Way is in question here.
    """
    from galaxy.stages.halo import rho_crit

    implied = 0.9e12 / (4.0 / 3.0 * math.pi * 255.0**3 * rho_crit(0.07, G))
    assert 80.0 < implied < 120.0  # top-hat, not 200
    assert abs(implied - 200.0) > 80.0
    # The same mass at 200 ρ_crit is a fifth smaller, which is the whole factor in λ_d.
    from galaxy.stages.halo import virial_radius

    assert virial_radius(0.9e12, 0.07, G) == pytest.approx(199.2, abs=1.0)
    assert 255.0 / virial_radius(0.9e12, 0.07, G) == pytest.approx(1.28, abs=0.03)


def test_the_defaults_hit_rows_1_and_4(model):
    o = out(model)
    assert o.fields["disc_scale_length_spin"] == pytest.approx(SCALE_LENGTH, abs=0.02)
    assert 4.0e10 <= o.fields["baryon_mass_total"] <= 6.0e10


# --- the disc itself ---------------------------------------------------------


def test_scale_length_is_a_fixed_fraction_of_the_halo(model):
    o = out(model)
    ratio = o.fields["disc_scale_length_spin"] / o.fields["halo_virial_radius"]
    assert ratio == pytest.approx(INPUTS["disc_spin"].default / math.sqrt(2.0), rel=1e-12)
    assert ratio < 0.02  # the visible galaxy is a speck inside its halo


def test_surface_density_integrates_to_the_disc_mass(model):
    """∫Σ 2πR dR over an infinite disc is M_d; the grid stops at 30 kpc, so check the tail."""
    o = out(model)
    R, R_d = o.grid.R, o.fields["disc_scale_length_spin"]
    sigma = o.fields["disc_surface_density"] * 1e6  # M☉/pc² -> M☉/kpc²
    enclosed = np.trapezoid(sigma * 2.0 * math.pi * R, R)
    x = o.grid.spec.R_max / R_d
    analytic = o.fields["baryon_mass_total"] * (1.0 - (1.0 + x) * math.exp(-x))
    assert enclosed == pytest.approx(analytic, rel=1e-3)
    assert analytic / o.fields["baryon_mass_total"] > 0.999  # 30 kpc is 11.5 scale lengths


def test_freeman_beats_the_spherical_approximation(model):
    """Justifies the Bessel form over M(<R): the difference is far bigger than row 3's bar."""
    o = out(model)
    M_d, R_d = o.fields["baryon_mass_total"], o.fields["disc_scale_length_spin"]
    freeman = float(freeman_circular_velocity(R_SUN, M_d / (2 * math.pi * R_d**2), R_d, G))
    x = R_SUN / R_d
    spherical = math.sqrt(G * M_d * (1.0 - (1.0 + x) * math.exp(-x)) / R_SUN)
    assert abs(freeman - spherical) / freeman > 0.10
    assert freeman > spherical  # a flattened mass distribution pulls harder in its own plane


def test_disc_curve_peaks_near_2_2_scale_lengths(model):
    """The classic exponential-disc result, and a check the Bessel branch join is not visible."""
    o = out(model)
    R, v = o.grid.R, o.fields["disc_circular_velocity"]
    peak = R[int(np.argmax(v))] / o.fields["disc_scale_length_spin"]
    assert peak == pytest.approx(2.2, abs=0.1)
    assert np.all(np.isfinite(v)) and np.all(v >= 0.0)
    # No step where A&S switches formula at y = 2, i.e. R = 4 R_d. The curve has real
    # curvature at small R, so the join is checked at the join and not by a global bound.
    R_d = o.fields["disc_scale_length_spin"]
    sigma0 = o.fields["baryon_mass_total"] / (2 * math.pi * R_d**2)
    join = 4.0 * R_d
    h = 1e-6
    below = float(freeman_circular_velocity(join - h, sigma0, R_d, G))
    above = float(freeman_circular_velocity(join + h, sigma0, R_d, G))
    # Row 3's error bar is 3 km/s. The step across the join is the A&S truncation error
    # and must be thousands of times smaller than anything the acceptance table can see.
    assert abs(above - below) < 1e-3
    # And the curve either side of the join is monotone falling, with no local kink.
    window = (R > join - 2.0) & (R < join + 2.0)
    assert np.all(np.diff(v[window]) < 0.0)


def test_total_curve_is_the_quadrature_sum_and_halo_dominates_outside(model):
    o = out(model)
    f = o.fields
    assert np.allclose(f["circular_velocity"], np.hypot(f["halo_circular_velocity"], f["disc_circular_velocity"]))
    outer = o.grid.R > 20.0
    assert np.all(f["halo_circular_velocity"][outer] > f["disc_circular_velocity"][outer])


def test_the_checkpoint_one_curve_still_has_every_baryon_in_one_exponential(model):
    """S1's curve is stage one's preview and is deliberately left alone (D42).

    It is not the acceptance number any more — row 3 reads the sfh stage's resolved
    curve — but it must still be the one-component curve it was, or the two stages
    are computing the same thing twice and disagreeing (rule A9).
    """
    o = out(model)
    R_d = o.fields["disc_scale_length_spin"]
    M = o.fields["baryon_mass_total"]
    expected = float(freeman_circular_velocity(R_SUN, M / (2 * math.pi * R_d**2), R_d, G))
    on_curve = float(np.interp(R_SUN, o.grid.R, o.fields["disc_circular_velocity"]))
    assert on_curve == pytest.approx(expected, rel=2e-3)
    assert np.allclose(
        o.fields["circular_velocity"],
        np.hypot(o.fields["halo_circular_velocity"], o.fields["disc_circular_velocity"]),
    )


def test_the_general_solver_reproduces_freeman_on_an_exponential():
    """The solver that replaced the single-exponential fit must not have cost accuracy."""
    R = np.linspace(0.0375, 30.0, 400)
    R_d, M = 2.6, 5.0e10
    sigma0 = M / (2 * math.pi * R_d**2)
    exact = freeman_circular_velocity(R, sigma0, R_d, G)
    got, residual = disc_circular_velocity(sigma0 / 1e6 * np.exp(-R / R_d), R, G)
    assert residual < 1e-3
    at_sun = np.argmin(np.abs(R - R_SUN))
    # Row 3's bar is 3 km/s; the representation must be far inside it where it is read.
    assert abs(got[at_sun] - exact[at_sun]) < 0.1
    inner = R < 25.0
    assert np.max(np.abs(got[inner] - exact[inner]) / np.maximum(exact[inner], 1e-9)) < 0.01


def test_the_two_models_agree_on_every_field_but_the_canary(prod):
    """The stages are shared code; only CANARY may differ until S9 (GALAXY_PLAN.md §7 risk 3)."""
    a, b = run(prod[0].get("simple")), run(prod[0].get("advanced"))
    assert set(a.fields) == set(b.fields)
    differing = [
        k for k in a.fields
        if not np.array_equal(np.asarray(a.fields[k]), np.asarray(b.fields[k]), equal_nan=True)
    ]
    assert differing == ["canary"]
