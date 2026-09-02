"""Disc: the exponential stellar disc and the total rotation curve (checkpoint 1).

One implementation, shared by both models. The disc turns the halo's retained
baryon budget into a razor-thin exponential disc and adds its contribution to
the rotation curve.

Two relations, and neither is free:

- **Scale length.** ``R_d = (1/√2) λ_d R₂₀₀`` — MMW98's relation with the
  angular-momentum retention fraction j_d/m_d folded into λ_d, which is what
  makes λ_d the *disc* spin rather than the halo's (ruling 8, GALAXY_INPUTS.md
  §6). MMW98 define their virial radius as r₂₀₀, the radius enclosing 200 ρ_crit
  ``[recall: Mo, Mao & White 1998 §2]``, which is the R₂₀₀ the halo stage
  publishes. MMW98's structure factors f_c^(−1/2) f_R — the NFW binding-energy
  correction and the disc's self-gravity plus adiabatic contraction — are *not*
  modelled; they are O(1) and are absorbed into λ_d, which is why λ_d is an
  inferred effective parameter rather than a measured one (debts #6, #10).
- **Circular velocity.** Freeman's exact result for a razor-thin exponential
  disc, ``v² = 4πGΣ₀R_d y²[I₀(y)K₀(y) − I₁(y)K₁(y)]`` at ``y = R/2R_d``
  ``[recall: Freeman 1970; Binney & Tremaine §2.6.1]``. A spherical
  approximation would be wrong by about 15% in v at R₀ — six times acceptance
  row 3's error bar — so the Bessel form is not a refinement here
  ``[verified: tests/test_disc.py::test_freeman_beats_the_spherical_approximation]``.

**What this stage does not have yet, and what that costs.** There is no gas
phase (S2) and no bulge (S3–S4), so the whole retained baryon budget sits in one
exponential of scale length 2.6 kpc. That over-concentrates mass inside R₀ and
pushes v_c up: acceptance row 3 misses high, by construction rather than by
accident (debt #11). The prediction, which S2 can kill: moving the ~8 × 10⁹ M☉
of gas onto its own, much shallower profile lowers v_c(R₀) into the window.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.special import i0, i1, k0, k1
from galaxy.core.stage import Context, Stage

PC_PER_KPC = 1000.0  # a definition, not a measurement


def scale_length(spin: float, R200: float) -> float:
    """MMW98: ``R_d = λ_d R₂₀₀ / √2``, with j_d/m_d folded into λ_d (ruling 8)."""
    return spin * R200 / math.sqrt(2.0)


def freeman_circular_velocity(R: np.ndarray | float, sigma0: float, R_d: float, G: float) -> np.ndarray:
    """Freeman's razor-thin exponential disc, with ``sigma0`` in M☉/kpc² and ``R_d`` in kpc."""
    y = np.asarray(R, dtype=float) / (2.0 * R_d)
    bracket = i0(y) * k0(y) - i1(y) * k1(y)
    # The bracket is positive for every y > 0; it is a difference of nearly equal
    # products at large y, so floating point can carry it a few ulp below zero.
    v2 = 4.0 * math.pi * G * sigma0 * R_d * y * y * np.maximum(bracket, 0.0)
    return np.sqrt(v2)


THIN_DISC_SCALE_LENGTH = FieldDecl(
    name="thin_disc_scale_length",
    label="Thin disc scale length R_d",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Exponential scale length from MMW98 given λ_d and R₂₀₀. The surprise is how little of "
        "the halo it is: R_d/R₂₀₀ ≈ 1.2%, so the visible galaxy is a speck at the centre of the "
        "thing that holds it. At S1 there is one disc, so this is the whole stellar distribution "
        "and 'thin' names acceptance row 4 rather than a thin/thick split (S2)."
    ),
)

STELLAR_MASS_TOTAL = FieldDecl(
    name="stellar_mass_total",
    label="Total stellar mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Every retained baryon, treated as a star. Until S2 gives the model a gas phase this is "
        "the baryon budget rather than the stellar mass, so it is high by the gas — about 8 × 10⁹ "
        "M☉ against a target of 5 ± 1 × 10¹⁰ (debt #11). It still lands inside acceptance row 1, "
        "at the top of the window, and rule B10 says baryon_retention must be re-examined the "
        "moment the gas is split off."
    ),
)

DISC_CENTRAL_SURFACE_DENSITY = FieldDecl(
    name="disc_central_surface_density",
    label="Central surface density Σ₀",
    unit="Msun/pc2",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "M_d/2πR_d². Carrying the bulge's and the gas's mass in a disc profile puts this some 70% "
        "above the ~800 M☉/pc² usually quoted for the Milky Way's stellar disc — the same "
        "over-concentration that shows up in v_c(R₀) (debt #11)."
    ),
)

DISC_SURFACE_DENSITY = FieldDecl(
    name="disc_surface_density",
    label="Disc surface density Σ(R)",
    unit="Msun/pc2",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("inferno", scale="log"),
    meaningful_zero=True,
    about=(
        "Σ₀ exp(−R/R_d), axisymmetric and smooth. The target is not: Juríc et al. found "
        "substructure prevalent enough that a smooth exponential cannot be fitted to either disc "
        "without accounting for it (GALAXY_INPUTS.md §7). Structure arrives at S4."
    ),
)

DISC_CIRCULAR_VELOCITY = FieldDecl(
    name="disc_circular_velocity",
    label="Disc circular velocity",
    unit="km/s",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=0.0, hi=300.0),
    meaningful_zero=True,
    about=(
        "Freeman's exact razor-thin exponential disc. Peaks near 2.2 R_d and falls away, which is "
        "why the flat outer curve has to come from the halo."
    ),
)

CIRCULAR_VELOCITY = FieldDecl(
    name="circular_velocity",
    label="Circular velocity v_c(R)",
    unit="km/s",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=0.0, hi=300.0),
    meaningful_zero=True,
    about=(
        "Halo and disc added in quadrature — the rotation curve the model actually predicts. Two "
        "components only: no gas (S2), no bulge (S3–S4), so it is over-concentrated inside a few "
        "kpc (debt #11)."
    ),
)

V_CIRCULAR_SUN = FieldDecl(
    name="v_circular_sun",
    label="Circular velocity at R₀",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "v_c at the solar radius, computed analytically rather than interpolated from the grid. "
        "The commonly quoted value is 238 ± 15 km/s; it is not an acceptance row, because the "
        "table's row 3 is the Sun's tangential velocity, which is this plus the solar motion."
    ),
)

V_TANGENTIAL_SUN = FieldDecl(
    name="v_tangential_sun",
    label="Solar tangential velocity",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "v_c(R₀) plus the Sun's own tangential peculiar motion, which is what acceptance row 3's "
        "248 ± 3 km/s measures — it comes from the proper motion of Sgr A*, so it is the Sun's "
        "velocity in the Galactic rest frame and not the circular speed of the disc there."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    G = float(ctx.constants["G"])
    R200 = float(ctx.fields["halo_virial_radius"])
    M_d = float(ctx.fields["baryon_mass_total"])

    R_d = scale_length(float(ctx.inputs["disc_spin"]), R200)
    sigma0 = M_d / (2.0 * math.pi * R_d * R_d)  # M☉/kpc²

    R = ctx.grid.R
    v_disc = freeman_circular_velocity(R, sigma0, R_d, G)
    v_halo = ctx.fields["halo_circular_velocity"]

    R_sun = float(ctx.constants["R_SUN"])
    v_disc_sun = float(freeman_circular_velocity(R_sun, sigma0, R_d, G))
    v_c_sun = math.hypot(float(ctx.fields["halo_circular_velocity_sun"]), v_disc_sun)

    return {
        "thin_disc_scale_length": R_d,
        "stellar_mass_total": M_d,
        "disc_central_surface_density": sigma0 / PC_PER_KPC**2,
        "disc_surface_density": sigma0 / PC_PER_KPC**2 * np.exp(-R / R_d),
        "disc_circular_velocity": v_disc,
        "circular_velocity": np.hypot(v_halo, v_disc),
        "v_circular_sun": v_c_sun,
        "v_tangential_sun": v_c_sun + float(ctx.constants["V_SUN_PECULIAR"]),
    }


DISC = IMPLEMENTATIONS.register(
    Stage(
        id="disc",
        slot="disc",
        checkpoint=1,
        about=(
            "Exponential stellar disc from λ_d and the halo's baryon budget, and the total "
            "rotation curve. Shared by both models."
        ),
        compute=compute,
        reads_inputs=("disc_spin",),
        reads_constants=("G", "R_SUN", "V_SUN_PECULIAR"),
        requires=(
            "halo_virial_radius",
            "baryon_mass_total",
            "halo_circular_velocity",
            "halo_circular_velocity_sun",
        ),
        publishes=(
            THIN_DISC_SCALE_LENGTH,
            STELLAR_MASS_TOTAL,
            DISC_CENTRAL_SURFACE_DENSITY,
            DISC_SURFACE_DENSITY,
            DISC_CIRCULAR_VELOCITY,
            CIRCULAR_VELOCITY,
            V_CIRCULAR_SUN,
            V_TANGENTIAL_SUN,
        ),
    )
)
