"""Halo: the NFW dark halo and the mass budget of the galaxy (checkpoint 1).

One implementation, shared by both models (GALAXY_PLAN.md §2): nothing here
differs between the simple and the advanced pass, so the model chooses the same
code and the field set is identical.

What it computes, and how much freedom each step has (GALAXY_INPUTS.md §4b):

- **R₂₀₀ is arithmetic (verdict A).** ``R₂₀₀ = (3 M₂₀₀ / 800 π ρ_crit)^(1/3)`` is
  the *definition* of the radius enclosing 200 ρ_crit, not a fitted relation, so
  it has no freedom at all once M₂₀₀ and the cosmology are fixed.
- **c₂₀₀ is correlated with scatter (verdict C)**, absorbed into the assembly
  redshift by ruling 5: ``c₂₀₀ = CONCENTRATION_NORM (1 + z_f)``. The scatter it
  does not absorb is a calibration debt, not a variable.
- **The baryon budget** splits M₂₀₀ into what became the disc and what stayed
  dark. ``m_d = f_b × baryon_retention`` (ruling 9). The dark halo carries
  ``(1 − m_d) M₂₀₀``, so the disc's mass is not counted twice in the rotation
  curve — at m_d ≈ 0.05 double counting would be worth about 6 km/s at R₀,
  which is twice acceptance row 3's error bar ``[inferred]``.

The halo owns the budget rather than the disc because M₂₀₀ and its split are
properties of the halo; the disc stage turns the baryon half into a disc.

"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage


def mu(x: np.ndarray | float) -> np.ndarray | float:
    """The NFW mass factor ``ln(1+x) − x/(1+x)``; ``M(<r) = M_tot μ(r/r_s)/μ(c)``."""
    return np.log1p(x) - x / (1.0 + x)


def rho_crit(H0: float, G: float) -> float:
    """Critical density ``3H₀²/8πG`` in M☉/kpc³, with H₀ in km/s/kpc and G in kpc (km/s)²/M☉."""
    return 3.0 * H0 * H0 / (8.0 * math.pi * G)


def virial_radius(M200: float, H0: float, G: float) -> float:
    """R₂₀₀ from its definition: the radius enclosing a mean density of 200 ρ_crit."""
    return (3.0 * M200 / (800.0 * math.pi * rho_crit(H0, G))) ** (1.0 / 3.0)


def nfw_circular_velocity(R: np.ndarray | float, M: float, r_s: float, c: float, G: float) -> np.ndarray | float:
    """Circular velocity of an NFW halo of total mass ``M`` inside R₂₀₀ = c·r_s."""
    return np.sqrt(G * M * mu(np.asarray(R, dtype=float) / r_s) / mu(c) / np.asarray(R, dtype=float))


HALO_VIRIAL_MASS = FieldDecl(
    name="halo_virial_mass",
    label="Halo mass M₂₀₀",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Total mass inside R₂₀₀, dark and baryonic. Equal to the halo_mass input: the model does "
        "not derive it, and acceptance row 19 is therefore a check that the default lies inside the "
        "literature span 1.0–1.3 × 10¹² M☉, not a check on any physics."
    ),
)

HALO_VIRIAL_RADIUS = FieldDecl(
    name="halo_virial_radius",
    label="Virial radius R₂₀₀",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Radius enclosing a mean density of 200 ρ_crit. A definition, not a relation (verdict A), "
        "so the only freedom is the cosmology. The surprise is how large it is: 213 kpc at the "
        "default mass, an order of magnitude beyond every stellar structure the model publishes. "
        "It is not the R_vir ≈ 255 kpc quoted in GALAXY_INPUTS.md §6, which is a different "
        "overdensity at a different mass — see DECISIONS.md D30."
    ),
)

HALO_CONCENTRATION = FieldDecl(
    name="halo_concentration",
    label="Concentration c₂₀₀",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "R₂₀₀/r_s, derived from the assembly redshift by ruling 5: haloes that assembled early are "
        "concentrated because they froze in the mean density of an earlier, denser universe. "
        "Verdict C: the epoch absorbs most of the galaxy-to-galaxy scatter and not all of it."
    ),
)

HALO_SCALE_RADIUS = FieldDecl(
    name="halo_scale_radius",
    label="NFW scale radius r_s",
    unit="kpc",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about="R₂₀₀/c₂₀₀. The radius where the NFW logarithmic slope passes through −2.",
)

HALO_DARK_MASS = FieldDecl(
    name="halo_dark_mass",
    label="Dark halo mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "(1 − m_d) M₂₀₀: what the NFW profile carries once the disc's baryons are taken out, so "
        "that the rotation curve does not count them twice."
    ),
)

BARYON_MASS_TOTAL = FieldDecl(
    name="baryon_mass_total",
    label="Retained baryon mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "f_b × baryon_retention × M₂₀₀: every baryon the galaxy kept, stars and gas together. "
        "Until S2 splits off a gas phase the disc stage treats all of it as stars, so "
        "stellar_mass_total is high by the gas mass — about 8 × 10⁹ M☉, or 14% (debt #11)."
    ),
)

DISC_MASS_FRACTION = FieldDecl(
    name="disc_mass_fraction",
    label="Disc mass fraction m_d",
    unit="dimensionless",
    kind=Kind.SCALAR,
    about=(
        "Retained baryons as a fraction of M₂₀₀. Ruling 9 puts the Milky Way near 0.055; the "
        "default inputs give 0.053. Only about a third of the cosmic share survives feedback."
    ),
)

HALO_CIRCULAR_VELOCITY_SUN = FieldDecl(
    name="halo_circular_velocity_sun",
    label="Halo circular velocity at R₀",
    unit="km/s",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The dark halo's contribution to v_c at the solar radius, evaluated analytically rather "
        "than read off the grid so that it does not inherit the radial resolution. Published as a "
        "scalar so the disc stage can add its own contribution without a second copy of the NFW "
        "formula (rule A9)."
    ),
)

HALO_ENCLOSED_MASS = FieldDecl(
    name="halo_enclosed_mass",
    label="Dark mass inside R",
    unit="Msun",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="log"),
    meaningful_zero=True,
    about="NFW cumulative mass. Rises logarithmically: half the halo's mass lies outside 60 kpc.",
)

HALO_CIRCULAR_VELOCITY = FieldDecl(
    name="halo_circular_velocity",
    label="Halo circular velocity",
    unit="km/s",
    kind=Kind.FIELD,
    axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=0.0, hi=300.0),
    meaningful_zero=True,
    about=(
        "√(GM(<R)/R) for the dark halo alone. Nearly flat across the disc, which is the whole "
        "reason a halo is needed: the baryons alone fall off Keplerian beyond a few scale lengths."
    ),
)

HALO_POTENTIAL = FieldDecl(
    name="halo_potential",
    label="Halo potential Φ(R, z)",
    unit="km2/s2",
    kind=Kind.FIELD,
    axes=("R", "z"),
    ramp=Ramp("magma", scale="linear"),
    meaningful_zero=False,
    about=(
        "NFW potential −G M_dark ln(1 + r/r_s) / (μ(c) r) at r = √(R² + z²), on the half-space "
        "z ≥ 0 by plane symmetry. Spherical, so it varies with z only through r; the disc's own "
        "flattened potential arrives with the vertical structure at S2. Zero is not meaningful: "
        "the zero point is at infinity."
    ),
)



def compute(ctx: Context) -> Mapping[str, Any]:
    G = float(ctx.constants["G"])
    H0 = float(ctx.constants["H0"])
    M200 = float(ctx.inputs["halo_mass"])
    z_f = float(ctx.inputs["halo_assembly_z"])

    R200 = virial_radius(M200, H0, G)
    c = float(ctx.constants["CONCENTRATION_NORM"]) * (1.0 + z_f)
    r_s = R200 / c

    m_d = float(ctx.constants["F_BARYON"]) * float(ctx.inputs["baryon_retention"])
    baryons = m_d * M200
    dark = M200 - baryons

    R = ctx.grid.R
    enclosed = dark * mu(R / r_s) / mu(c)
    v_c = np.sqrt(G * enclosed / R)

    r = np.hypot(R[:, None], ctx.grid.z[None, :])
    potential = -G * dark * np.log1p(r / r_s) / (mu(c) * r)

    return {
        "halo_virial_mass": M200,
        "halo_virial_radius": R200,
        "halo_concentration": c,
        "halo_scale_radius": r_s,
        "halo_dark_mass": dark,
        "baryon_mass_total": baryons,
        "disc_mass_fraction": m_d,
        "halo_circular_velocity_sun": float(
            nfw_circular_velocity(float(ctx.constants["R_SUN"]), dark, r_s, c, G)
        ),
        "halo_enclosed_mass": enclosed,
        "halo_circular_velocity": v_c,
        "halo_potential": potential,
    }


HALO = IMPLEMENTATIONS.register(
    Stage(
        id="halo",
        slot="halo",
        checkpoint=1,
        about=(
            "NFW dark halo from M₂₀₀ and the assembly redshift, plus the split of M₂₀₀ into "
            "retained baryons and dark matter. Shared by both models."
        ),
        compute=compute,
        reads_inputs=("halo_mass", "halo_assembly_z", "baryon_retention"),
        reads_constants=("G", "H0", "F_BARYON", "CONCENTRATION_NORM", "R_SUN"),
        publishes=(
            HALO_VIRIAL_MASS,
            HALO_VIRIAL_RADIUS,
            HALO_CONCENTRATION,
            HALO_SCALE_RADIUS,
            HALO_DARK_MASS,
            BARYON_MASS_TOTAL,
            DISC_MASS_FRACTION,
            HALO_CIRCULAR_VELOCITY_SUN,
            HALO_ENCLOSED_MASS,
            HALO_CIRCULAR_VELOCITY,
            HALO_POTENTIAL,
        ),
    )
)
