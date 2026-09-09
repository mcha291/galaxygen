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
    """Ruling 5: c_vir = K(1 + z_f), converted to c₂₀₀ since S13 (debt #12). Since S15 the default
    epoch is the ΛCDM median for the default mass (c₂₀₀ = 8.24 before the halo responds to the
    disc, 10.91 until S15), and the measured span c ≈ 10–18 (GALAXY_INPUTS.md §4b) is read
    against the *contracted* halo's effective concentration, which is what a fit to the Milky
    Way measures: 15.4 at the default, inside; 18.5 at the old 2.5, over (D117)."""
    o = out(model)
    assert o.fields["halo_concentration_virial"] == pytest.approx(10.91, abs=0.01)  # 14.35 until S15
    assert o.fields["halo_concentration"] == pytest.approx(8.24, abs=0.01)  # 10.91 until S15
    assert o.fields["halo_concentration"] < o.fields["halo_concentration_virial"]
    assert 10.0 <= o.fields["halo_concentration_contracted"] <= 18.0
    assert o.fields["halo_concentration_contracted"] == pytest.approx(14.97, abs=0.02)  # 15.43 until S16's tail (a less compact total)
    assert out(model, halo_assembly_z=2.5).fields["halo_concentration_contracted"] == pytest.approx(18.0, abs=0.05)  # 18.5 until S16; at the edge
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
    assert naive - o.fields["halo_circular_velocity_sun_initial"] == pytest.approx(3.3, abs=0.5)  # 4.3 until S15 (c₂₀₀ 10.9 → 8.2)
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
    assert c_vir == pytest.approx(10.91, abs=0.01) and c200 == pytest.approx(8.24, abs=0.01)  # 14.35 and 10.91 until S15
    assert c200 == pytest.approx(concentration_at(200.0, c_vir, dvir), rel=1e-9)
    assert concentration_at(dvir, c200, 200.0) == pytest.approx(c_vir, abs=1e-6)  # the root round-trips
    assert dvir * c_vir**3 / mu(c_vir) == pytest.approx(200.0 * c200**3 / mu(c200), rel=1e-9)
    assert o.fields["halo_scale_radius"] == pytest.approx(o.fields["halo_virial_radius"] / c200, rel=1e-12)


def test_the_conversion_moved_row_3_and_nothing_else(model):
    """What the conversion is worth: 10.7 km/s on row 3 at the S15 default (12.4 at z_f = 2.5; 13.5 before the halo contracted), and < 1e-9 on every other row.

    Until S14 it took the row from 5 high to 2 low (256.2 → 242.7); on the contracted
    halo at z_f = 2.5 it read 283.2 → 270.8; at the ΛCDM-median epoch 270.8 → 260.1 —
    both high, the conversion still worth three half-widths.
    """
    from galaxy.core.registry import INPUTS
    from galaxy.stages.halo import concentration_at, virial_overdensity

    dvir = virial_overdensity(float(model.constants["OMEGA_M"].value))
    z = INPUTS["halo_assembly_z"].default
    c_unconverted = 4.1 * (1.0 + z)  # what K(1 + z_f) was used as until S13
    k_unconverted = concentration_at(dvir, c_unconverted, 200.0) / (1.0 + z)  # the K whose c_vir converts to it
    before, after = run(_with_norm(model, k_unconverted)), run(model)
    assert float(before.fields["halo_concentration"]) == pytest.approx(c_unconverted, abs=0.01)
    assert float(before.fields["v_tangential_sun"]) == pytest.approx(262.4, abs=0.5)  # 263.9 until S17; 270.8 until S16; 283.2 until S15
    assert float(after.fields["v_tangential_sun"]) == pytest.approx(251.3, abs=0.5)  # 252.9 until S17; 260.1 until S16; 270.8 until S15
    # The conversion is worth 11.1 km/s now, one half-width less than at S16: it moves the
    # spheroid too (the low-j excess is read off the same curve), and the spheroid pushes back.
    assert 250.0 < float(after.fields["v_tangential_sun"]) < float(before.fields["v_tangential_sun"])
    # Until S16 every other row moved by < 1e-9. The high-j tail is mapped onto the plane on the
    # rotation curve (j = R v_c), so the halo's parameters now reach the infall through it: the
    # conversion moves row 2 by 0.4% and the gas mass by 2.3% - the tail's edge moves with the curve (D119). Row 19 is exact.
    assert float(after.fields["halo_virial_mass"]) == float(before.fields["halo_virial_mass"])
    for name in ("sfr", "gas_mass_30kpc", "stellar_mass_total", "thin_disc_scale_length"):
        assert float(after.fields[name]) == pytest.approx(float(before.fields[name]), rel=3e-2), name


def test_k_and_the_assembly_epoch_enter_only_as_their_product(model):
    """So no measurement of z_f alone can validate the relation debt #12 names."""
    from galaxy.core.registry import INPUTS

    z = INPUTS["halo_assembly_z"].default
    a = run(_with_norm(model, 3.5))  # K lowered, z_f at its default
    b = run(model, {"halo_assembly_z": 3.5 * (1.0 + z) / 4.1 - 1.0})  # K left alone, z_f moved to the same product
    assert float(a.fields["halo_concentration"]) == pytest.approx(float(b.fields["halo_concentration"]))
    assert float(a.fields["v_tangential_sun"]) == pytest.approx(float(b.fields["v_tangential_sun"]))


def test_the_epoch_row_3_wants_is_below_the_cited_range(model):
    """Row 3 is met at z_f ≈ 0.7–1.0 on the contracted halo; §3 cites z ≈ 2–3 and the default is neither (S14, S15).

    Until S14 the row wanted 2.7–3.1, the top of the range; the contraction turned it round.
    Choosing z_f against a row whose answer is known is the move rule B5 exists to prevent;
    S15 derived the default from the ΛCDM median instead, 1.66, and the row still misses
    (260.1); S16's tail moved what the row wants to 1.1–1.2 (252.9 at the default) and S17's
    spheroid to 1.3–1.4 (251.3), a quarter of a km/s outside. This test is what notices if the
    range the row wants moves, and it has now moved towards the default three sessions running
    without reaching it.
    """
    inside = [z for z in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 2.0, 2.5, 3.0)
              if 245.0 <= float(run(model, {"halo_assembly_z": z}).fields["v_tangential_sun"]) <= 251.0]
    assert inside == [1.3, 1.4]  # [1.1, 1.2] until S17; [0.7, 0.8, 0.9, 1.0] until S16
    lo = float(run(model, {"halo_assembly_z": 2.0}).fields["v_tangential_sun"])
    hi = float(run(model, {"halo_assembly_z": 3.0}).fields["v_tangential_sun"])
    assert lo == pytest.approx(256.0, abs=0.3)  # 257.6 until S17; 264.5 until S16; 236.4 until S14
    assert hi - lo == pytest.approx(12.4, abs=0.3)  # the cited range spans four half-widths of the target, all of it high (12.8 until S14)


# --- S14, the halo's response to the disc (debt #6) -----------------------------


def _with_contraction(base, A: float, w: float):
    """``base`` with another (A, w) for the contraction invariant and nothing else changed."""
    from galaxy.core.registry import Constant, Model

    constants = dict(base.constants)
    constants["CONTRACTION_A"] = Constant(A, "dimensionless", "probe")
    constants["CONTRACTION_W"] = Constant(w, "dimensionless", "probe")
    return Model(name=base.name, about=base.about, stages=base.stages,
                 constants=constants, inputs=base.inputs)


# The halo as S14 built it at z_f = 2.5: M₂₀₀, R₂₀₀, c₂₀₀ and the disc it contracts around. The
# solver tests below keep it (the default's c₂₀₀ is 8.24 since S15); the stage tests read the default.
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

    The register had the contraction at "several km/s" [recall]; measured at z_f = 2.5, the halo's
    share at R₀ rose 138.6 → 181.4 (Gnedin) or 195.6 (Blumenthal), and row 3 read 270.8 or 280.9
    against 245–251. At the S15 default (z_f 1.66, c₂₀₀ 8.24) the less concentrated halo responds
    *more* — 119.3 → 165.8 or 180.6, r_i/r_f 1.50 — and the row read 260.1 or 270.2; with S16's
    tail the total is less compact and the response a little smaller: 163.3 or 178.0, and the row
    252.9 or 263.3; with S17's spheroid the same mass is more compact again and the row reads
    251.3 or 262.2. The ruleset was chosen before the row was read; the row did not choose it.
    A = 1.6 at w = 0.8 read 245.6 at S15, inside, and reads 238.1 now, out the other way — not
    adopted either time: the Auriga-calibrated response [recall: Cautun et al. 2020] agrees with
    Gnedin's at R₀ to 2 km/s, not with 1.6 (D117).
    """
    gnedin, blumenthal = out(model), run(_with_contraction(model, 1.0, 1.0))
    for o in (gnedin, blumenthal):
        assert o.fields["halo_circular_velocity_sun_initial"] == pytest.approx(119.3, abs=0.1)  # 138.6 until S15
    assert gnedin.fields["halo_circular_velocity_sun"] == pytest.approx(163.2, abs=0.2)  # 163.3 until S17; 181.4 until S15
    assert blumenthal.fields["halo_circular_velocity_sun"] == pytest.approx(178.5, abs=0.2)  # 178.0 until S17; 195.6 until S15
    assert gnedin.fields["v_tangential_sun"] == pytest.approx(251.3, abs=0.5)  # 252.9 until S17; 270.8 until S15
    assert blumenthal.fields["v_tangential_sun"] == pytest.approx(262.2, abs=0.5)  # 263.3 until S17; 280.9 until S15
    assert float(np.interp(8.2, gnedin.grid.R, gnedin.fields["halo_contraction"])) == pytest.approx(1.47, abs=0.01)  # 1.50 until S16; 1.42 until S15
    assert float(np.interp(8.2, blumenthal.grid.R, blumenthal.fields["halo_contraction"])) == pytest.approx(1.65, abs=0.01)  # 1.68 until S16; 1.57 until S15
    weak = run(_with_contraction(model, 1.6, 0.8), only=("v_tangential_sun",))
    assert weak.fields["v_tangential_sun"] == pytest.approx(238.1, abs=0.5)  # 239.8 until S17; 245.6 until S16; not adopted
    # The response tends to a constant at the centre where the *disc* and the halo both enclose
    # mass as R², and falls outward. Since S17 the spheroid is there too and it does not: a
    # Hernquist sphere encloses mass as r² only well inside a = 0.36 kpc, and the first grid
    # cell is at 0.04 kpc, so the innermost ratio jumped 2.45 → 4.85 with the spheroid.
    ratio = gnedin.fields["halo_contraction"]
    assert ratio[0] == pytest.approx(4.85, abs=0.02) and np.all(np.diff(ratio) < 0.0)  # 2.45 until S17; 2.22 until S15
    # It moved nothing upstream of the kinematics until S16; the high-j tail is mapped onto the plane on
    # the rotation curve, so the ruleset now reaches the infall through it — row 2 by 0.9%, the masses by less (D119).
    assert float(gnedin.fields["halo_virial_mass"]) == float(blumenthal.fields["halo_virial_mass"])
    for name in ("sfr", "hydrogen_mass_30kpc", "stellar_mass_total", "thin_disc_scale_length"):
        assert float(gnedin.fields[name]) == pytest.approx(float(blumenthal.fields[name]), rel=1e-2), name


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


# --- S16, the high-j tail of the halo's angular-momentum distribution (debt #18) -------


def test_the_high_j_tail_is_derived_and_where_it_lies(model):
    """Bullock et al. 2001's profile, mapped onto the plane on the model's own curve, lies above the
    exponential only outside their outer crossing; that excess is the tail (D119).

    Its share is nearly independent of the profile's shape (0.07-0.08 across mu 1.06-1.4); its
    inner edge is not. Inside the crossing it is zero, so row 4 cannot see it.
    """
    o = out(model)
    f, R = o.fields, o.grid.R
    tail, share, R_c = f["infall_tail_surface_density"], f["infall_tail_share"], f["infall_tail_inner_radius"]
    assert share == pytest.approx(0.0756, abs=0.001) and R_c == pytest.approx(12.3, abs=0.1)
    assert np.all(tail[R < R_c - 0.3] == 0.0) and np.all(tail[(R > 13.0) & (R < 24.0)] > 0.0)  # the edge is one mesh step wide on the grid
    assert float(np.interp(15.0, R, tail)) == pytest.approx(3.7, abs=0.1)
    assert float(np.interp(20.0, R, tail)) == pytest.approx(3.6, abs=0.1)
    assert float(np.interp(26.0, R, tail)) == 0.0  # the distribution's j_max lands near 25 kpc
    # The tail's share comes out of the exponential's budget: the halo contracts around the same total mass.
    from galaxy.stages.disc import PC_PER_KPC

    on_grid = float(np.trapezoid(tail * 2.0 * math.pi * R, R)) * PC_PER_KPC**2
    assert on_grid == pytest.approx(share * f["baryon_mass_total"], rel=0.02)  # what the grid sees of it


def test_the_tail_moves_the_halos_response_and_not_the_scale_length(model):
    """Row 4's check (debt #18): the disc stage's R_d is untouched; the halo responds to a less compact total."""
    from galaxy.core.registry import Constant, Model
    from galaxy.stages.halo import MESH_INNER, MESH_OUTER, MESH_POINTS

    o = out(model)
    assert o.fields["disc_scale_length_spin"] == pytest.approx(2.605, abs=0.005)
    # 165.8 at S15, around the exponential alone (D117); the tail's 7.6% beyond 12 kpc lowers the response at R0.
    assert o.fields["halo_circular_velocity_sun"] == pytest.approx(163.3, abs=0.2)
    mesh = np.geomspace(MESH_INNER, MESH_OUTER * o.fields["halo_virial_radius"], MESH_POINTS)
    r_s, c, m_d = o.fields["halo_scale_radius"], o.fields["halo_concentration"], o.fields["disc_mass_fraction"]
    from galaxy.stages.halo import contracted_halo

    M_alone, _ = contracted_halo(mesh, 1.1e12, r_s, c, m_d, 2.605, o.fields["halo_virial_radius"], 0.85, 0.8)
    assert _v_at_sun(mesh, M_alone) == pytest.approx(165.8, abs=0.2)
    assert _v_at_sun(mesh, M_alone) > o.fields["halo_circular_velocity_sun"]
    # The shape constant moves the edge, not the share (D119, debt #47).
    constants = dict(model.constants)
    constants["ANGULAR_MOMENTUM_MU"] = Constant(1.4, "dimensionless", "probe")
    peaked = run(Model(name=model.name, about=model.about, stages=model.stages, constants=constants, inputs=model.inputs),
                 only=("infall_tail_share", "infall_tail_inner_radius"))
    assert peaked.fields["infall_tail_inner_radius"] == pytest.approx(11.0, abs=0.2)
    assert abs(peaked.fields["infall_tail_share"] - o.fields["infall_tail_share"]) < 0.01


# --- S17, the spheroid: the low-j end of the same distribution (debt #11) --------


def test_the_hernquist_half_mass_radius_is_algebra():
    """a(1 + sqrt 2) is where r^2/(r + a)^2 = 1/2; the scale radius is set by inverting it (D121)."""
    from galaxy.stages.halo import HERNQUIST_HALF_MASS, hernquist_enclosed

    for a in (0.1, 0.365, 2.0):
        assert hernquist_enclosed(a * HERNQUIST_HALF_MASS, 1.0, a) == pytest.approx(0.5, rel=1e-12)
    # And the density is the derivative of the enclosed mass, which is what the Jeans integral needs.
    from galaxy.stages.halo import hernquist_density

    r = np.geomspace(1e-4, 1e3, 20001)
    M = hernquist_enclosed(r, 3.0, 0.4)
    assert np.trapezoid(hernquist_density(r, 3.0, 0.4) * 4.0 * math.pi * r**2, r) == pytest.approx(M[-1], rel=1e-4)


def test_the_two_excesses_are_one_construction_read_twice(model):
    """The distribution lies above the exponential at both ends; the tail is one, the spheroid the other."""
    from galaxy.stages.halo import (
        MESH_INNER,
        MESH_OUTER,
        MESH_POINTS,
        angular_momentum_core,
        angular_momentum_excess,
        angular_momentum_tail,
        contracted_halo,
    )
    from galaxy.stages.disc import freeman_circular_velocity

    o = out(model)
    f = o.fields
    R200, r_s = f["halo_virial_radius"], f["halo_scale_radius"]
    c, m_d, R_d = f["halo_concentration"], f["disc_mass_fraction"], f["disc_scale_length_spin"]
    baryons = f["baryon_mass_total"]
    mesh = np.geomspace(MESH_INNER, MESH_OUTER * R200, MESH_POINTS)
    M_dark, _ = contracted_halo(mesh, 1.1e12, r_s, c, m_d, R_d, R200, 0.85, 0.8)
    v_disc = freeman_circular_velocity(mesh, baryons / (2.0 * math.pi * R_d * R_d), R_d, G)
    j = mesh * np.hypot(np.sqrt(G * M_dark / mesh), v_disc)

    disc, profile = angular_momentum_excess(mesh, j, baryons, R_d, 1.25)
    ring = 2.0 * math.pi * mesh
    # Both are normalised to the same budget, so their difference integrates to zero: what the
    # spheroid and the tail take is exactly what the middle of the exponential gives up.
    # (the exponential's own quadrature on this mesh is 0.007% over the analytic budget, which
    # is the mesh's inner cut at 1e-3 kpc and the trapezoid; the profile is normalised exactly)
    assert np.trapezoid(profile * ring, mesh) == pytest.approx(np.trapezoid(disc * ring, mesh), rel=1e-3)
    assert np.trapezoid((profile - disc) * ring, mesh) == pytest.approx(0.0, abs=1e-3 * baryons)

    _tail, share, R_out = angular_momentum_tail(mesh, j, baryons, R_d, 1.25)
    mass, r_half, R_in, j_mean = angular_momentum_core(mesh, j, baryons, R_d, 1.25)
    assert R_in < R_d < R_out  # the exponential wins in the middle, and only there
    assert mass == pytest.approx(f["bulge_stellar_mass"], rel=1e-9)
    assert r_half / (1.0 + math.sqrt(2.0)) == pytest.approx(f["bulge_scale_radius"], rel=1e-9)
    assert j_mean > 0.0 and share > 0.0


def test_the_spheroid_is_derived_and_does_not_move_with_the_mesh(model):
    """A scalar that moved with the mesh would be a hidden quadrature (rule B2's cousin, S16)."""
    from galaxy.stages.halo import (
        MESH_OUTER,
        angular_momentum_core,
        contracted_halo,
    )
    from galaxy.stages.disc import freeman_circular_velocity

    o = out(model)
    f = o.fields
    assert f["bulge_stellar_mass"] == pytest.approx(7.71e9, rel=0.01)
    assert f["bulge_stellar_mass"] / f["baryon_mass_total"] == pytest.approx(0.132, abs=0.002)
    assert f["bulge_scale_radius"] == pytest.approx(0.365, abs=0.005)
    R200, r_s = f["halo_virial_radius"], f["halo_scale_radius"]
    c, m_d, R_d = f["halo_concentration"], f["disc_mass_fraction"], f["disc_scale_length_spin"]
    baryons = f["baryon_mass_total"]
    for n, inner in ((300, 1e-3), (1200, 1e-3), (600, 1e-4), (2400, 1e-4)):
        mesh = np.geomspace(inner, MESH_OUTER * R200, n)
        M_dark, _ = contracted_halo(mesh, 1.1e12, r_s, c, m_d, R_d, R200, 0.85, 0.8)
        v_disc = freeman_circular_velocity(mesh, baryons / (2.0 * math.pi * R_d * R_d), R_d, G)
        j = mesh * np.hypot(np.sqrt(G * M_dark / mesh), v_disc)
        mass, r_half, _, _ = angular_momentum_core(mesh, j, baryons, R_d, 1.25)
        assert mass == pytest.approx(f["bulge_stellar_mass"], rel=0.02), (n, inner)
        assert r_half == pytest.approx(f["bulge_scale_radius"] * (1.0 + math.sqrt(2.0)), rel=0.05), (n, inner)


def test_the_spheroid_grows_as_the_distribution_gets_flatter(model):
    """mu is the distribution's shape: a flatter one has more low-j material, and the spheroid is it."""
    from galaxy.core.registry import Constant, Model

    masses = []
    for mu_j in (1.06, 1.25, 1.40):
        constants = dict(model.constants)
        constants["ANGULAR_MOMENTUM_MU"] = Constant(mu_j, "dimensionless", "probe")
        probe = Model(name=model.name, about=model.about, stages=model.stages,
                      constants=constants, inputs=model.inputs)
        masses.append(float(run(probe, only=("bulge_stellar_mass",)).fields["bulge_stellar_mass"]))
    assert masses[0] > masses[1] > masses[2]
    # 1.46e10 to 5.6e9 across the range debt #47 holds: the observed 1.4-1.7e10 needs the
    # flattest distribution anyone quotes, and mu = 1.25 is the value S16 verified (D119).
    assert masses[0] == pytest.approx(1.46e10, rel=0.02)
    assert masses[2] == pytest.approx(5.60e9, rel=0.02)


def test_the_dispersion_is_the_total_potentials_and_not_the_spheroids(model):
    """Row 14 is a derivation with one assumption, isotropy; on self-gravity alone it is a third lower."""
    o = out(model)
    f = o.fields
    M_b, a = f["bulge_stellar_mass"], f["bulge_scale_radius"]
    assert f["bulge_velocity_dispersion"] == pytest.approx(116.2, abs=0.3)
    self_gravity = math.sqrt(G * M_b / (18.0 * a))  # virial for an isolated Hernquist sphere
    assert self_gravity == pytest.approx(71.1, abs=0.5)
    assert f["bulge_velocity_dispersion"] > 1.5 * self_gravity
    # And the classical share is a prediction, read against BHG16's 0-25% for the Milky Way.
    assert 0.0 <= f["bulge_classical_fraction"] <= 0.25
    assert f["bulge_classical_fraction"] == pytest.approx(0.171, abs=0.005)
