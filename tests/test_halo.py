"""The halo stage: R₂₀₀ arithmetic, the NFW profile, the mass budget.

R₂₀₀ is a definition, not a fit (GALAXY_INPUTS.md §4b verdict A), so it is
checked by inverting the definition rather than against a remembered number: a
sphere of radius R₂₀₀ must enclose exactly 200 ρ_crit on average. A check that
re-ran the stage's own formula would be a check on nothing (rule B3).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.stages.halo import mu, rho_crit, virial_radius

H0 = 0.07
G = 4.300917270e-6


def out(model, **inputs):
    return run(model, inputs or None)


def test_rho_crit_matches_the_textbook_value():
    """ρ_crit = 2.775 × 10¹¹ h² M☉/Mpc³ is the form usually quoted; ours is per kpc³."""
    per_mpc3 = rho_crit(H0, G) * 1e9
    assert per_mpc3 == pytest.approx(2.775e11 * 0.7**2, rel=2e-3)


def test_R200_encloses_200_rho_crit_by_construction():
    """Invert the definition instead of repeating the formula (rule B3)."""
    for M200 in (1e11, 1.1e12, 1e13):
        R = virial_radius(M200, H0, G)
        mean_density = M200 / (4.0 / 3.0 * math.pi * R**3)
        assert mean_density == pytest.approx(200.0 * rho_crit(H0, G), rel=1e-12)


def test_R200_scales_as_the_cube_root_of_mass():
    a, b = virial_radius(1.1e12, H0, G), virial_radius(8.8e12, H0, G)
    assert b / a == pytest.approx(2.0, rel=1e-12)  # 8x the mass, 2x the radius


def test_R200_at_the_default_mass(model):
    """213 kpc, not the 255 kpc GALAXY_INPUTS.md §6 quotes: different overdensity, different
    mass (DECISIONS.md D30). This is the number the disc's scale length hangs off."""
    o = out(model)
    assert o.fields["halo_virial_radius"] == pytest.approx(212.9, abs=0.5)
    assert o.fields["halo_virial_mass"] == 1.1e12


def test_concentration_from_the_assembly_redshift(model):
    """Ruling 5: c_vir = K(1 + z_f), converted to c₂₀₀ since S13 (debt #12). The default's
    consequence must land inside the measured span c ≈ 10–18 (GALAXY_INPUTS.md §4b) — that
    is what makes z_f = 2.5 more than a guess, and both numbers do."""
    o = out(model)
    assert o.fields["halo_concentration_virial"] == pytest.approx(14.35, abs=0.01)
    assert o.fields["halo_concentration"] == pytest.approx(10.91, abs=0.01)
    assert 10.0 <= o.fields["halo_concentration"] <= o.fields["halo_concentration_virial"] <= 18.0
    early, late = out(model, halo_assembly_z=4.0), out(model, halo_assembly_z=1.0)
    assert early.fields["halo_concentration"] > late.fields["halo_concentration"]
    assert early.fields["halo_scale_radius"] < late.fields["halo_scale_radius"]


def test_the_mass_budget_adds_up(model):
    o = out(model)
    f = o.fields
    assert f["halo_dark_mass"] + f["baryon_mass_total"] == pytest.approx(f["halo_virial_mass"])
    assert f["disc_mass_fraction"] == pytest.approx(0.152177 * 0.35, rel=1e-9)
    # Ruling 9 puts the Milky Way's m_d near 0.055; stars (5e10) plus gas (8e9) over M₂₀₀.
    assert 0.045 <= f["disc_mass_fraction"] <= 0.060


def test_the_disc_is_not_counted_twice(model):
    """The NFW profile carries (1 − m_d)M₂₀₀. Carrying all of M₂₀₀ would inflate v_c(R₀)."""
    o = out(model)
    naive = math.sqrt(
        G * o.fields["halo_virial_mass"] * mu(8.2 / o.fields["halo_scale_radius"]) / mu(o.fields["halo_concentration"]) / 8.2
    )
    assert naive > o.fields["halo_circular_velocity_sun"]
    assert naive - o.fields["halo_circular_velocity_sun"] == pytest.approx(4.3, abs=0.5)


def test_nfw_enclosed_mass_and_velocity_are_consistent(model):
    o = out(model)
    R = o.grid.R
    v = np.sqrt(G * o.fields["halo_enclosed_mass"] / R)
    assert np.allclose(v, o.fields["halo_circular_velocity"])
    assert np.all(np.diff(o.fields["halo_enclosed_mass"]) > 0)  # monotonic
    # The whole dark mass sits inside R₂₀₀, and the grid only reaches 30 kpc of it.
    assert o.fields["halo_enclosed_mass"][-1] < 0.3 * o.fields["halo_dark_mass"]


def test_the_scalar_at_R0_matches_the_curve(model):
    """The analytic scalar and the gridded field must agree, or one of them is wrong."""
    o = out(model)
    on_grid = float(np.interp(8.2, o.grid.R, o.fields["halo_circular_velocity"]))
    assert on_grid == pytest.approx(o.fields["halo_circular_velocity_sun"], rel=2e-3)


def test_potential_is_negative_falls_off_and_is_spherical(model):
    o = out(model)
    phi = o.fields["halo_potential"]
    assert phi.shape == (o.grid.spec.n_R, o.grid.spec.n_z)
    assert np.all(phi < 0.0)
    assert np.all(np.diff(phi[:, 0]) > 0)  # rises towards zero with radius
    # Spherical: Φ depends on (R, z) only through r, so equal r gives equal Φ.
    r_s = o.fields["halo_scale_radius"]
    dark = o.fields["halo_dark_mass"]
    r = np.hypot(o.grid.R[:, None], o.grid.z[None, :])
    assert np.allclose(phi, -G * dark * np.log1p(r / r_s) / (mu(o.fields["halo_concentration"]) * r))


def test_grid_resolution_does_not_move_the_scalars(model):
    """The scalars are analytic. A grid-dependent scalar would mean a hidden quadrature."""
    coarse = run(model, grid=GridSpec(n_R=40, n_t=5, n_z=6))
    fine = run(model, grid=GridSpec(n_R=800, n_t=5, n_z=120))
    for name in ("halo_virial_radius", "halo_concentration", "halo_circular_velocity_sun"):
        assert coarse.fields[name] == pytest.approx(fine.fields[name], rel=1e-12), name


# --- S10, the calibration audit (rule B10) ------------------------------------


def _with_norm(base, k: float):
    """``base`` with a different CONCENTRATION_NORM and nothing else changed."""
    from galaxy.core.registry import Constant, Model

    constants = dict(base.constants)
    constants["CONCENTRATION_NORM"] = Constant(k, "dimensionless", "the c_vir-to-c200 conversion, done")
    return Model(name=base.name, about=base.about, stages=base.stages,
                 constants=constants, inputs=base.inputs)


def test_the_concentration_is_converted_from_the_virial_overdensity(model):
    """Debt #12, half discharged at S13: K(1 + z_f) is a c_vir, and the halo converts it to c₂₀₀.

    Δ_vir(Ω_M = 0.3) ≈ 101 ρ_crit [recall: Bryan & Norman 1998]; Δ c³/μ(c) is the halo's own
    invariant, so the conversion is a root of the NFW profile and not a factor recalled or
    taken from a cited radius — the two other readings the S10 audits gave it (D102).
    """
    from galaxy.stages.halo import concentration_at, virial_overdensity

    o = out(model)
    dvir = virial_overdensity(float(model.constants["OMEGA_M"].value))
    assert dvir == pytest.approx(101.1, abs=0.2)
    c_vir, c200 = float(o.fields["halo_concentration_virial"]), float(o.fields["halo_concentration"])
    assert c_vir == pytest.approx(14.35, abs=0.01) and c200 == pytest.approx(10.91, abs=0.01)
    assert c200 == pytest.approx(concentration_at(200.0, c_vir, dvir), rel=1e-9)
    assert concentration_at(dvir, c200, 200.0) == pytest.approx(c_vir, abs=1e-6)  # the root round-trips
    assert dvir * c_vir**3 / mu(c_vir) == pytest.approx(200.0 * c200**3 / mu(c200), rel=1e-9)
    assert o.fields["halo_scale_radius"] == pytest.approx(o.fields["halo_virial_radius"] / c200, rel=1e-12)


def test_the_conversion_moved_row_3_and_nothing_else(model):
    """What the conversion is worth: 13.5 km/s on row 3, from 5 high to 2 low, and < 1e-9 on every other row."""
    from galaxy.stages.halo import concentration_at, virial_overdensity

    dvir = virial_overdensity(float(model.constants["OMEGA_M"].value))
    k_unconverted = concentration_at(dvir, 14.35, 200.0) / 3.5  # the K whose c_vir converts to the old c₂₀₀ = 14.35
    before, after = run(_with_norm(model, k_unconverted)), run(model)
    assert float(before.fields["halo_concentration"]) == pytest.approx(14.35, abs=0.01)
    assert float(before.fields["v_tangential_sun"]) == pytest.approx(256.2, abs=0.5)
    assert float(after.fields["v_tangential_sun"]) == pytest.approx(242.7, abs=0.5)
    assert float(after.fields["v_tangential_sun"]) < 245.0 < 251.0 < float(before.fields["v_tangential_sun"])
    for name in ("sfr", "gas_mass_30kpc", "stellar_mass_total", "thin_disc_scale_length"):
        assert float(after.fields[name]) == pytest.approx(float(before.fields[name]), rel=1e-9), name


def test_k_and_the_assembly_epoch_enter_only_as_their_product(model):
    """So no measurement of z_f alone can validate the relation debt #12 names."""
    a = run(_with_norm(model, 3.5))  # K lowered, z_f at its default 2.5
    b = run(model, {"halo_assembly_z": 3.5 * 3.5 / 4.1 - 1.0})  # K left alone, z_f moved to the same product
    assert float(a.fields["halo_concentration"]) == pytest.approx(float(b.fields["halo_concentration"]))
    assert float(a.fields["v_tangential_sun"]) == pytest.approx(float(b.fields["v_tangential_sun"]))


def test_the_epoch_row_3_wants_is_the_top_of_the_cited_range(model):
    """Row 3 is met at z_f ≈ 2.7–3.1; §3 cites z ≈ 2–3 and the default stays at its midpoint (S13).

    Choosing z_f against a row whose answer is known is the move rule B5 exists to prevent;
    the row is a recorded miss instead, and this test is what notices if the range moves.
    """
    inside = [z for z in (2.5, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2)
              if 245.0 <= float(run(model, {"halo_assembly_z": z}).fields["v_tangential_sun"]) <= 251.0]
    assert inside == [2.7, 2.8, 2.9, 3.0, 3.1]
    lo = float(run(model, {"halo_assembly_z": 2.0}).fields["v_tangential_sun"])
    hi = float(run(model, {"halo_assembly_z": 3.0}).fields["v_tangential_sun"])
    assert hi - lo == pytest.approx(12.8, abs=0.3)  # the cited range spans four half-widths of the target
