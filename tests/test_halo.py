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
    """The NFW profile carries (1 − m_d)M₂₀₀. Carrying all of M₂₀₀ would inflate v_c(R₀).

    Read against the halo *before* it contracted (S14): the contraction adds the disc's
    pull on the dark matter, which is a different thing from counting the disc twice.
    """
    o = out(model)
    naive = math.sqrt(
        G * o.fields["halo_virial_mass"] * mu(8.2 / o.fields["halo_scale_radius"]) / mu(o.fields["halo_concentration"]) / 8.2
    )
    assert naive > o.fields["halo_circular_velocity_sun_initial"]
    assert naive - o.fields["halo_circular_velocity_sun_initial"] == pytest.approx(4.3, abs=0.5)
    assert o.fields["halo_circular_velocity_sun"] > naive  # the response is ten times the double count


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


def test_potential_is_negative_falls_off_deeper_than_nfw_and_spherical(model):
    o = out(model)
    phi = o.fields["halo_potential"]
    assert phi.shape == (o.grid.spec.n_R, o.grid.spec.n_z)
    assert np.all(phi < 0.0)
    assert np.all(np.diff(phi[:, 0]) > 0)  # rises towards zero with radius
    r_s, dark, c = o.fields["halo_scale_radius"], o.fields["halo_dark_mass"], o.fields["halo_concentration"]
    R = o.grid.R
    r = np.hypot(R[:, None], o.grid.z[None, :])
    # Deeper than the halo before it responded to the disc, everywhere the grid reaches (S14, debt #6):
    # about 12% at R₀. Until S14 the field *was* the analytic NFW potential.
    assert np.all(phi < -G * dark * np.log1p(r / r_s) / (mu(c) * r))
    nfw0 = -G * dark * np.log1p(R / r_s) / (mu(c) * R)
    deeper_by = float(np.interp(8.2, R, o.fields["halo_potential_midplane"])) / float(np.interp(8.2, R, nfw0))
    assert 1.05 < deeper_by < 1.20
    # Spherical: Φ depends on (R, z) only through r, so the (R, z) field is the midplane's curve read at r.
    inside = (r <= R[-1]) & (r > 1.0)
    on_curve = np.interp(np.log(r[inside]), np.log(R), o.fields["halo_potential_midplane"])
    assert np.allclose(phi[inside], on_curve, rtol=1e-3)


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
    """What the conversion is worth: 12.4 km/s on row 3 (13.5 before the halo contracted, S14), and < 1e-9 on every other row.

    Until S14 it took the row from 5 high to 2 low (256.2 → 242.7); on the contracted
    halo it reads 283.2 → 270.8, both high, the conversion still worth four half-widths.
    """
    from galaxy.stages.halo import concentration_at, virial_overdensity

    dvir = virial_overdensity(float(model.constants["OMEGA_M"].value))
    k_unconverted = concentration_at(dvir, 14.35, 200.0) / 3.5  # the K whose c_vir converts to the old c₂₀₀ = 14.35
    before, after = run(_with_norm(model, k_unconverted)), run(model)
    assert float(before.fields["halo_concentration"]) == pytest.approx(14.35, abs=0.01)
    assert float(before.fields["v_tangential_sun"]) == pytest.approx(283.2, abs=0.5)  # 256.2 until S14
    assert float(after.fields["v_tangential_sun"]) == pytest.approx(270.8, abs=0.5)  # 242.7 until S14
    assert 251.0 < float(after.fields["v_tangential_sun"]) < float(before.fields["v_tangential_sun"])
    for name in ("sfr", "gas_mass_30kpc", "stellar_mass_total", "thin_disc_scale_length"):
        assert float(after.fields[name]) == pytest.approx(float(before.fields[name]), rel=1e-9), name


def test_k_and_the_assembly_epoch_enter_only_as_their_product(model):
    """So no measurement of z_f alone can validate the relation debt #12 names."""
    a = run(_with_norm(model, 3.5))  # K lowered, z_f at its default 2.5
    b = run(model, {"halo_assembly_z": 3.5 * 3.5 / 4.1 - 1.0})  # K left alone, z_f moved to the same product
    assert float(a.fields["halo_concentration"]) == pytest.approx(float(b.fields["halo_concentration"]))
    assert float(a.fields["v_tangential_sun"]) == pytest.approx(float(b.fields["v_tangential_sun"]))


def test_the_epoch_row_3_wants_is_below_the_cited_range(model):
    """Row 3 is met at z_f ≈ 0.7–1.0 on the contracted halo; §3 cites z ≈ 2–3 and the default stays at its midpoint (S14).

    Until S14 the row wanted 2.7–3.1, the top of the range; the contraction turned it round.
    Choosing z_f against a row whose answer is known is the move rule B5 exists to prevent;
    the row is a recorded miss instead, and this test is what notices if the range moves.
    """
    inside = [z for z in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 2.0, 2.5, 3.0)
              if 245.0 <= float(run(model, {"halo_assembly_z": z}).fields["v_tangential_sun"]) <= 251.0]
    assert inside == [0.7, 0.8, 0.9, 1.0]
    lo = float(run(model, {"halo_assembly_z": 2.0}).fields["v_tangential_sun"])
    hi = float(run(model, {"halo_assembly_z": 3.0}).fields["v_tangential_sun"])
    assert lo == pytest.approx(264.5, abs=0.3)  # 236.4 until S14
    assert hi - lo == pytest.approx(12.2, abs=0.3)  # the cited range spans four half-widths of the target, all of it high (12.8 until S14)


# --- S14, the halo's response to the disc (debt #6) -----------------------------


def _with_contraction(base, A: float, w: float):
    """``base`` with another (A, w) for the contraction invariant and nothing else changed."""
    from galaxy.core.registry import Constant, Model

    constants = dict(base.constants)
    constants["CONTRACTION_A"] = Constant(A, "dimensionless", "probe")
    constants["CONTRACTION_W"] = Constant(w, "dimensionless", "probe")
    return Model(name=base.name, about=base.about, stages=base.stages,
                 constants=constants, inputs=base.inputs)


# The default halo, as the stage builds it: M₂₀₀, R₂₀₀, c₂₀₀ and the disc it contracts around.
HALO = dict(M200=1.1e12, R200=212.94, c=10.911, R_d=2.605)
HALO["r_s"] = HALO["R200"] / HALO["c"]
M_D = 0.0533  # F_BARYON × baryon_retention


def _contracted(mesh, m_d, A, w):
    from galaxy.stages.halo import contracted_halo

    return contracted_halo(mesh, HALO["M200"], HALO["r_s"], HALO["c"], m_d, HALO["R_d"], HALO["R200"], A, w)


def _v_at_sun(mesh, M):
    return math.sqrt(G * float(np.exp(np.interp(math.log(8.2), np.log(mesh), np.log(M)))) / 8.2)


def test_with_no_disc_the_halo_comes_back_unchanged():
    """The instrument before the physics (rule B1): with nothing to respond to, every invariant returns r_i = r_f."""
    from galaxy.stages.halo import MESH_INNER, MESH_OUTER, MESH_POINTS, potential_of

    mesh = np.geomspace(MESH_INNER, MESH_OUTER * HALO["R200"], MESH_POINTS)
    nfw = HALO["M200"] * mu(mesh / HALO["r_s"]) / mu(HALO["c"])
    phi_nfw = -G * HALO["M200"] * np.log1p(mesh / HALO["r_s"]) / (mu(HALO["c"]) * mesh)
    for A, w in ((1.0, 1.0), (0.85, 0.8), (1.6, 0.8)):
        M, ratio = _contracted(mesh, 0.0, A, w)
        assert np.max(np.abs(ratio - 1.0)) < 1e-12 and np.max(np.abs(M / nfw - 1.0)) < 1e-10
        phi = potential_of(mesh, M, HALO["M200"], HALO["r_s"], HALO["c"], G)
        assert np.max(np.abs(phi / phi_nfw - 1.0)) < 1e-5  # the trapezoid in ln r: 600 points over twelve e-folds


def test_a_third_ruleset_reads_a_third_number():
    """The defect S14 found by probing (rule B4, the cheap way round).

    With the final dark mass attached to the orbit-averaged radius r̄_f, A cancelled out of the
    whole calculation and Gnedin's A = 0.85 and a probed A = 1.6 read the default's number
    back to the digit. A shell keeps its mass at its own radius; the three (A, w) read three.
    """
    mesh = np.geomspace(1e-3, 1.5 * HALO["R200"], 600)
    at_sun = {}
    for A, w in ((1.0, 1.0), (0.85, 0.8), (1.6, 0.8)):
        M, ratio = _contracted(mesh, M_D, A, w)
        at_sun[(A, w)] = _v_at_sun(mesh, M)
        assert np.all(ratio[mesh < 100.0] > 1.0)  # inward everywhere the disc is
    assert at_sun[(1.0, 1.0)] > at_sun[(0.85, 0.8)] > at_sun[(1.6, 0.8)]
    assert at_sun[(1.0, 1.0)] - at_sun[(0.85, 0.8)] > 10.0
    assert at_sun[(0.85, 0.8)] - at_sun[(1.6, 0.8)] > 10.0


def test_the_mesh_does_not_move_the_scalars():
    """A hidden quadrature would show here: quadrupling the mesh moves v_halo(R₀) and Φ(R₀) by parts in 10⁶."""
    from galaxy.stages.halo import potential_of

    v, phi = {}, {}
    for n in (600, 2400):
        mesh = np.geomspace(1e-3, 1.5 * HALO["R200"], n)
        M, _ = _contracted(mesh, M_D, 0.85, 0.8)
        v[n] = _v_at_sun(mesh, M)
        table = potential_of(mesh, M, HALO["M200"] * (1.0 - M_D), HALO["r_s"], HALO["c"], G)
        phi[n] = float(np.interp(math.log(8.2), np.log(mesh), table))
    assert v[600] == pytest.approx(v[2400], rel=1e-5) and phi[600] == pytest.approx(phi[2400], rel=1e-5)


def test_the_named_rulesets_and_what_each_is_worth_at_R0(model):
    """Debt #46: Gnedin et al. 2004 (the default) and Blumenthal et al. 1986, kept as named rulesets (rule B12).

    The register had the contraction at "several km/s" [recall]; measured, the halo's share at
    R₀ rises 138.6 → 181.4 (Gnedin) or 195.6 (Blumenthal), and row 3 reads 270.8 or 280.9
    against 245–251. The ruleset was chosen before the row was read; the row did not choose it.
    """
    gnedin, blumenthal = out(model), run(_with_contraction(model, 1.0, 1.0))
    for o in (gnedin, blumenthal):
        assert o.fields["halo_circular_velocity_sun_initial"] == pytest.approx(138.6, abs=0.1)
    assert gnedin.fields["halo_circular_velocity_sun"] == pytest.approx(181.4, abs=0.2)
    assert blumenthal.fields["halo_circular_velocity_sun"] == pytest.approx(195.6, abs=0.2)
    assert gnedin.fields["v_tangential_sun"] == pytest.approx(270.8, abs=0.5)
    assert blumenthal.fields["v_tangential_sun"] == pytest.approx(280.9, abs=0.5)
    assert float(np.interp(8.2, gnedin.grid.R, gnedin.fields["halo_contraction"])) == pytest.approx(1.42, abs=0.01)
    assert float(np.interp(8.2, blumenthal.grid.R, blumenthal.fields["halo_contraction"])) == pytest.approx(1.57, abs=0.01)
    # The response tends to a constant at the centre, where disc and halo both enclose mass as R², and falls outward.
    ratio = gnedin.fields["halo_contraction"]
    assert ratio[0] == pytest.approx(2.22, abs=0.02) and np.all(np.diff(ratio) < 0.0)
    # It moves nothing upstream of the kinematics.
    for name in ("sfr", "hydrogen_mass_30kpc", "stellar_mass_total", "thin_disc_scale_length", "halo_virial_mass"):
        assert float(gnedin.fields[name]) == pytest.approx(float(blumenthal.fields[name]), rel=1e-9), name


def test_the_scale_length_is_the_halos_now_and_the_disc_reads_it(model):
    """Rule A9: one opinion about R_d, held by the stage that needs it first — the halo contracts around it."""
    from galaxy.core.registry import IMPLEMENTATIONS, INPUTS
    from galaxy.stages.halo import scale_length

    o = run(model, only=("circular_velocity",))
    assert o.order == ("halo", "disc")
    expected = scale_length(INPUTS["disc_spin"].default, o.fields["halo_virial_radius"])
    assert o.fields["disc_scale_length_spin"] == pytest.approx(expected, rel=1e-12)
    assert "disc_scale_length_spin" in {d.name for d in IMPLEMENTATIONS.get("halo").publishes}
    assert "disc_scale_length_spin" in IMPLEMENTATIONS.get("disc").requires
    assert "disc_spin" in IMPLEMENTATIONS.get("halo").reads_inputs and "disc_spin" not in IMPLEMENTATIONS.get("disc").reads_inputs


# --- S15, two more discriminants read off the contracted halo -------------------


def test_with_no_disc_the_density_and_the_effective_concentration_are_the_nfw_ones():
    """The instrument before the physics (rule B1): both new scalars reduce to the analytic halo with nothing to respond to."""
    from galaxy.stages.halo import concentration_enclosing, density_of, nfw_density

    mesh = np.geomspace(1e-3, 1.5 * HALO["R200"], 600)
    M, _ = _contracted(mesh, 0.0, 0.85, 0.8)
    rho = density_of(mesh, M)
    nfw = nfw_density(mesh, HALO["M200"], HALO["r_s"], HALO["c"])
    inside = slice(2, -2)  # the one-sided differences at the mesh's ends are first order
    assert np.max(np.abs(rho[inside] / nfw[inside] - 1.0)) < 1e-4
    at_sun = float(np.exp(np.interp(math.log(8.2), np.log(mesh), np.log(M))))
    # rel 1e-5: at_sun is read between mesh points in log-log, and the root inherits that interpolation.
    assert concentration_enclosing(at_sun, 8.2, HALO["M200"], HALO["R200"]) == pytest.approx(HALO["c"], rel=1e-5)


def test_the_mesh_does_not_move_the_density_or_the_effective_concentration():
    from galaxy.stages.halo import concentration_enclosing, density_of

    rho, c_eff = {}, {}
    for n in (600, 2400):
        mesh = np.geomspace(1e-3, 1.5 * HALO["R200"], n)
        M, _ = _contracted(mesh, M_D, 0.85, 0.8)
        rho[n] = float(np.exp(np.interp(math.log(8.2), np.log(mesh), np.log(density_of(mesh, M)))))
        c_eff[n] = concentration_enclosing(
            float(np.exp(np.interp(math.log(8.2), np.log(mesh), np.log(M)))), 8.2, HALO["M200"] * (1.0 - M_D), HALO["R200"]
        )
    assert rho[600] == pytest.approx(rho[2400], rel=1e-4) and c_eff[600] == pytest.approx(c_eff[2400], rel=1e-5)


def test_the_stage_publishes_both_in_the_units_a_measurement_quotes(model):
    """Msun/pc3 for the density; the effective concentration above the initial one wherever the halo contracted inward."""
    o = out(model)
    rho, c_eff, c = o.fields["halo_density_sun"], o.fields["halo_concentration_contracted"], o.fields["halo_concentration"]
    assert 1e-3 < rho < 1e-1  # a volume density in Msun/pc3, not Msun/kpc3
    assert c_eff > c  # the disc pulled dark matter inward, so an NFW anchored inside reads it more concentrated
    assert o.fields["halo_contraction"][0] > 1.0
