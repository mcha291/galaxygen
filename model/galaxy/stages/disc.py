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
  correction and the disc's self-gravity in the scale length — are *not*
  modelled; they are O(1) and are absorbed into λ_d, which is why λ_d is an
  inferred effective parameter rather than a measured one (debt #10). The
  halo's adiabatic contraction around the disc *is* modelled since S14, in the
  halo stage, which is why the scale length is computed there and read here
  (debt #6): the halo needs the disc it contracts around before this stage runs.
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
from galaxy.stages.halo import scale_length  # noqa: F401  (computed by the halo since S14; re-exported for its readers)

PC_PER_KPC = 1000.0  # a definition, not a measurement


def freeman_circular_velocity(R: np.ndarray | float, sigma0: float, R_d: float, G: float) -> np.ndarray:
    """Freeman's razor-thin exponential disc, with ``sigma0`` in M☉/kpc² and ``R_d`` in kpc."""
    y = np.asarray(R, dtype=float) / (2.0 * R_d)
    bracket = i0(y) * k0(y) - i1(y) * k1(y)
    # The bracket is positive for every y > 0; it is a difference of nearly equal
    # products at large y, so floating point can carry it a few ulp below zero.
    v2 = 4.0 * math.pi * G * sigma0 * R_d * y * y * np.maximum(bracket, 0.0)
    return np.sqrt(v2)


def disc_circular_velocity(
    sigma: np.ndarray, R: np.ndarray, G: float, at: np.ndarray | float | None = None,
    n_quad: int = 1000,
) -> np.ndarray | float:
    """Circular velocity of an arbitrary razor-thin axisymmetric disc ``sigma(R)``.

    Freeman's formula is exact only for an exponential, and a gas disc is not one
    — star formation holds its inner part near the threshold and leaves the outer
    part untouched. From S2 to S17 the profile was least-squared onto eight
    exponentials and Freeman's solution summed over them; that representation
    read the stars at R₀ to 0.1 km/s while the profiles were smooth, but the S18
    profiles are not — the merger's radial kick steepens the centre and the
    derived threshold shapes the gas like κ(R) — and the basis then missed the
    gas's v_c at R₀ by 2 km/s and the outer curve by 10, with no way to densify
    it (the exponentials are collinear and the fit blows up past twelve terms).

    This is the basis-free form (Binney & Tremaine 2008 §2.6.2, the homoeoid
    decomposition of a thin disc):

        v_c²(R) = −4G ∫₀^R a g′(a) / √(R² − a²) da,   g(a) = ∫₀^∞ Σ(√(a² + u²)) du

    Both integrals are regular after the substitutions above (``u`` takes the
    inner endpoint's inverse square root, ``a = R sin θ`` the outer's), so the
    quadrature is plain trapezoid on ``n_quad`` points and converges to 10⁻⁵ at
    R₀ ``[verified: tests/test_disc.py::test_the_general_solver_reproduces_freeman_on_an_exponential]``.
    The profile is linear between grid points and zero beyond the last one, which
    is what the grid means: nothing is modelled past R_max.

    ``sigma`` is in M☉/pc² and ``R`` in kpc; returns v_c on the grid, or at ``at``.
    """
    sigma = np.asarray(sigma, dtype=float) * PC_PER_KPC**2  # M☉/kpc²
    R = np.asarray(R, dtype=float)
    R_max = float(R[-1])
    a = np.linspace(0.0, R_max, n_quad)
    u = np.linspace(0.0, R_max, n_quad)
    r = np.sqrt(a[:, None] ** 2 + u[None, :] ** 2)
    g = np.trapezoid(np.interp(r, R, sigma, left=float(sigma[0]), right=0.0), u, axis=1)
    dg = np.gradient(g, a)
    where = R if at is None else np.atleast_1d(np.asarray(at, dtype=float))
    theta = np.linspace(0.0, 0.5 * math.pi, max(n_quad // 4, 100))
    aa = where[:, None] * np.sin(theta)[None, :]
    v2 = -4.0 * G * np.trapezoid(aa * np.interp(aa, a, dg), theta, axis=1)
    v = np.sqrt(np.maximum(v2, 0.0))
    return v if at is None else float(v[0]) if np.ndim(at) == 0 else v


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

def epicyclic_frequency(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """κ(R) in km/s/kpc from a rotation curve: κ² = 2 (v/R)² (1 + dln v/dln R).

    Solid-body inside (κ → 2Ω), √2 Ω where the curve is flat. The derivative is
    taken on the grid; a curve that is smooth on the grid's scale gives κ to the
    precision of the interpolation, which is what the convergence sweep checks.
    """
    R = np.asarray(R, dtype=float)
    v = np.maximum(np.asarray(v, dtype=float), 1e-9)
    dlnv = np.gradient(np.log(v), np.log(R))
    return np.sqrt(np.maximum(2.0 * (v / R) ** 2 * (1.0 + dlnv), 0.0))


EPICYCLIC_FREQUENCY = FieldDecl(
    name="epicyclic_frequency",
    label="Epicyclic frequency κ(R)",
    unit="km/s/kpc",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="log"),
    meaningful_zero=True,
    about=(
        "κ² = 2Ω²(1 + dln v/dln R) off the checkpoint-1 curve: 40 km/s/kpc at R₀, ten times that "
        "inside a kiloparsec. Two later stages read it — the merger's radial kick becomes a "
        "displacement through it (S18, debt #19) and the star formation threshold is Kennicutt's "
        "κ σ_g form rather than a constant (S18, debt #47) — so it is computed once, beside the "
        "curve it belongs to (rule A9)."
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
    M_d = float(ctx.fields["baryon_mass_total"])
    R_d = float(ctx.fields["disc_scale_length_spin"])  # the halo's, since S14: the disc it contracted around
    sigma0 = M_d / (2.0 * math.pi * R_d * R_d)  # M☉/kpc²

    R = ctx.grid.R
    v_disc = freeman_circular_velocity(R, sigma0, R_d, G)
    v_halo = ctx.fields["halo_circular_velocity"]
    v_total = np.hypot(v_halo, v_disc)

    return {
        "disc_central_surface_density": sigma0 / PC_PER_KPC**2,
        "disc_surface_density": sigma0 / PC_PER_KPC**2 * np.exp(-R / R_d),
        "disc_circular_velocity": v_disc,
        "circular_velocity": v_total,
        "epicyclic_frequency": epicyclic_frequency(R, v_total),
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
        reads_constants=("G",),
        requires=(
            "disc_scale_length_spin",
            "baryon_mass_total",
            "halo_circular_velocity",
        ),
        publishes=(
            DISC_CENTRAL_SURFACE_DENSITY,
            DISC_SURFACE_DENSITY,
            DISC_CIRCULAR_VELOCITY,
            CIRCULAR_VELOCITY,
            EPICYCLIC_FREQUENCY,
        ),
    )
)
