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


# Scale lengths of the exponential basis used to represent an arbitrary disc.
# Log-spaced from well inside the stellar disc to the edge of the grid.
BASIS_SCALE_LENGTHS: tuple[float, ...] = (0.5, 0.9, 1.6, 2.8, 5.0, 9.0, 16.0, 28.0)


def _freeman_v2(R: np.ndarray, sigma0: float, R_d: float, G: float) -> np.ndarray:
    y = np.asarray(R, dtype=float) / (2.0 * R_d)
    return 4.0 * math.pi * G * sigma0 * R_d * y * y * (i0(y) * k0(y) - i1(y) * k1(y))


def disc_circular_velocity(sigma: np.ndarray, R: np.ndarray, G: float, at: np.ndarray | float | None = None):
    """Circular velocity of an arbitrary razor-thin axisymmetric disc ``sigma(R)``.

    Freeman's formula is exact only for an exponential, and a gas disc is not one
    — star formation holds its inner part near the threshold and leaves the outer
    part untouched, so fitting a single exponential to it and calling that the
    mass distribution would be wrong where it matters most.

    Poisson's equation is *linear* in the surface density, so the honest fix is
    cheap: least-squares the profile onto a fixed basis of exponentials, then add
    the exact Freeman solution for each. Coefficients may come out negative, which
    is fine — the sum represents the profile, and each term contributes its own
    (signed) v² to a superposition, not a mass in its own right. The residual of
    the fit is returned so a caller can assert the representation is good rather
    than assume it.

    ``sigma`` is in M☉/pc² and ``R`` in kpc; returns ``(v_c, relative residual)``.
    """
    sigma = np.asarray(sigma, dtype=float)
    R = np.asarray(R, dtype=float)
    basis = np.exp(-R[:, None] / np.asarray(BASIS_SCALE_LENGTHS)[None, :])
    coeffs, *_ = np.linalg.lstsq(basis, sigma, rcond=None)
    scale = float(np.max(np.abs(sigma)))
    residual = float(np.max(np.abs(basis @ coeffs - sigma)) / scale) if scale > 0.0 else 0.0
    where = R if at is None else np.asarray(at, dtype=float)
    v2 = np.zeros_like(np.atleast_1d(where), dtype=float)
    for c, L in zip(coeffs, BASIS_SCALE_LENGTHS):
        v2 = v2 + _freeman_v2(where, float(c) * PC_PER_KPC**2, float(L), G)
    v = np.sqrt(np.maximum(v2, 0.0))
    return (v if at is None else float(v[0]) if np.ndim(at) == 0 else v), residual


DISC_SCALE_LENGTH_SPIN = FieldDecl(
    name="disc_scale_length_spin",
    label="Disc scale length from λ_d",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Exponential scale length from MMW98 given λ_d and R₂₀₀. The surprise is how little of "
        "the halo it is: R_d/R₂₀₀ ≈ 1.2%, so the visible galaxy is a speck at the centre of the "
        "thing that holds it. This is MMW98's *prediction* of the scale length from angular "
        "momentum. Acceptance row 4 is read from thin_disc_scale_length, which S2 fits to the "
        "stellar profile the star formation history actually builds — the two disagree by a "
        "third, and that disagreement is debt #13 rather than something to average away."
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




def compute(ctx: Context) -> Mapping[str, Any]:
    G = float(ctx.constants["G"])
    R200 = float(ctx.fields["halo_virial_radius"])
    M_d = float(ctx.fields["baryon_mass_total"])

    R_d = scale_length(float(ctx.inputs["disc_spin"]), R200)
    sigma0 = M_d / (2.0 * math.pi * R_d * R_d)  # M☉/kpc²

    R = ctx.grid.R
    v_disc = freeman_circular_velocity(R, sigma0, R_d, G)
    v_halo = ctx.fields["halo_circular_velocity"]

    return {
        "disc_scale_length_spin": R_d,
        "disc_central_surface_density": sigma0 / PC_PER_KPC**2,
        "disc_surface_density": sigma0 / PC_PER_KPC**2 * np.exp(-R / R_d),
        "disc_circular_velocity": v_disc,
        "circular_velocity": np.hypot(v_halo, v_disc),
    }


DISC = IMPLEMENTATIONS.register(
    Stage(
        id="disc",
        slot="disc",
        checkpoint=1,
        about=(
            "Exponential baryon disc from λ_d and the halo's baryon budget, and the "
            "checkpoint-1 rotation curve. Shared by both models. The split into stars and gas, "
            "and the acceptance-row kinematics that depend on it, belong to the sfh stage."
        ),
        compute=compute,
        reads_inputs=("disc_spin",),
        reads_constants=("G",),
        requires=(
            "halo_virial_radius",
            "baryon_mass_total",
            "halo_circular_velocity",
        ),
        publishes=(
            DISC_SCALE_LENGTH_SPIN,
            DISC_CENTRAL_SURFACE_DENSITY,
            DISC_SURFACE_DENSITY,
            DISC_CIRCULAR_VELOCITY,
            CIRCULAR_VELOCITY,
        ),
    )
)
