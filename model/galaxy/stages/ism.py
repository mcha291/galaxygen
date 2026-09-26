"""The cold ISM: midplane pressure, the molecular fraction, and dust (checkpoint 4).

Everything here is derived from fields that already exist. No new input, no new
seed, no new stage boundary — the stage reads the gas and stellar surface
densities, the stellar scale height and the gas-phase abundance, and publishes
what light needs from them.

**Why this stage exists at all.** Debt #79 was ruled permanent at S22 on the
grounds that the project held no citation for a molecular-fraction prescription
and that inventing one would be rule A4 read forwards. The ruling was against
*inventing* a prescription, not against *sourcing* one: the pressure-based
partition below is Blitz & Rosolowsky's, measured on fourteen nearby galaxies,
and it enters as a cited Level 0 prescription like any other. **If the S22 ruling
is upheld rather than revisited, this stage should not exist** — that ruling is a
prerequisite, not something this file settles.

**Acceptance row 21 will fail, and that is the correct outcome.** Its target is
0.11 with no quoted uncertainty: a zero-width target, the same defect as row 20
and from the same source (debt #17). No float that is not bit-exact can pass it.
Record the miss under rule B5 and do not move a constant to close it.

**Two conflicts are preserved, not averaged** (rule B12). The pressure normalisation
and index have a second measured pair, and the dust-to-gas law has a second
functional form. Both alternatives are named in the constants that carry them.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.feedback import MSUN_PER_PC3_IN_G_PER_CM3
from galaxy.stages.massive_stars import BOLTZMANN

# Blitz & Rosolowsky's own pressure form (their eq. for P_tot, after Elmegreen 1989):
#   P/k_B = 272 · Σ_gas · Σ_*^0.5 · v_disp · h_*^-0.5   [cm^-3 K]
# with Σ in M☉/pc², h_* in pc, v_disp in km/s. The 272 carries the unit conversion
# and is part of the prescription, not a free constant.
PRESSURE_COEFFICIENT = 272.0

# No SOLAR_OXYGEN here: the dust-to-gas law is published in 12 + log(O/H), but a
# power law in (O/H)/(O/H)☉ is identical to one in 10^[Fe/H] under the assumption
# that oxygen tracks iron, so the absolute abundance scale never enters. It would
# come back the moment the broken power law is adopted, because its transition is
# specified at an absolute 12 + log(O/H) = 7.96 rather than as a ratio.


def midplane_pressure(sigma_gas: np.ndarray, sigma_star: np.ndarray,
                      h_star_pc: float, v_disp: float) -> np.ndarray:
    """Hydrostatic midplane pressure, P/k_B in cm^-3 K.

    Assumes the stellar disc dominates the vertical gravity, which is the
    assumption Blitz & Rosolowsky's fit was made under; it fails in the gas-
    dominated outer disc, where Leroy's variant adds the gas self-gravity term.
    That difference is why the two rulesets below are kept apart rather than
    blended.
    """
    return (PRESSURE_COEFFICIENT * np.asarray(sigma_gas)
            * np.sqrt(np.maximum(np.asarray(sigma_star), 0.0))
            * v_disp / np.sqrt(max(h_star_pc, 1e-6)))


def midplane_density(pressure: np.ndarray, v_disp: float) -> np.ndarray:
    """The gas's midplane mass density in M☉/pc³, ρ0 = P / σ²: the hydrostatic pressure (P/k_B in
    cm⁻³ K) over the square of the same velocity dispersion the pressure was computed with (km/s)."""
    rho = np.maximum(np.asarray(pressure, dtype=float), 0.0) * BOLTZMANN / (v_disp * 1.0e5) ** 2  # g/cm³
    return rho / MSUN_PER_PC3_IN_G_PER_CM3


def molecular_ratio(pressure: np.ndarray, p_norm: float, index: float) -> np.ndarray:
    """R_mol = Σ_H2/Σ_HI = (P/P_0)^α, Blitz & Rosolowsky 2006."""
    return (np.maximum(np.asarray(pressure), 0.0) / p_norm) ** index


def dust_to_gas(feh: np.ndarray, solar_ratio: float, slope: float) -> np.ndarray:
    """Dust-to-gas mass ratio from the gas-phase abundance.

    Single power law in metallicity. The model carries [Fe/H]; the law is
    calibrated on 12 + log(O/H), and the conversion here assumes oxygen tracks
    iron, which is exactly the assumption the advanced model's α-elements exist
    to break. In the chemical model this should read [O/H] directly once that is
    published — recorded on the field's about line rather than silently ignored.
    """
    z_rel = 10.0 ** np.asarray(feh)
    return solar_ratio * z_rel ** slope


MIDPLANE_PRESSURE = FieldDecl(
    name="gas_midplane_pressure", label="Hydrostatic midplane pressure P/k_B", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "In cm^-3 K, though the unit vocabulary has no entry for it — declared dimensionless and "
        "said here rather than inventing a unit (rule A8's vocabulary is closed). Elmegreen's "
        "hydrostatic estimate as Blitz & Rosolowsky wrote it, assuming the stellar disc dominates "
        "the vertical gravity. That assumption fails where the gas dominates, so the outer disc's "
        "pressure is underestimated and with it the molecular fraction."
    ),
)

MIDPLANE_DENSITY = FieldDecl(
    name="gas_midplane_density", label="Gas midplane density ρ₀(R)", unit="Msun/pc3",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis", scale="log"), meaningful_zero=True,
    about=(
        "The midplane pressure over the square of the gas's velocity dispersion: in vertical equilibrium "
        "'the thermal and turbulent terms can be combined as a single midplane kinetic pressure ρ0σ_z²' "
        "(Ostriker & Shetty 2011), so the mass density is the pressure divided by it, at the dispersion the "
        "pressure prescription assumed. The volume-averaged density of the diffuse gas, clouds and "
        "intercloud medium together, not of any one phase: about 0.7 hydrogen atoms per cm³ at the "
        "solar radius, where Leroy et al. 2008 read 'Ph/k_B ≈ 2.3 × 10^4 cm^-3 K, corresponding to a "
        "particle density n ∼ 1 cm^-3'. What a single star's wind bubble and a supernova remnant expand "
        "into (S36)."
    ),
)

H2_FRACTION_PROFILE = FieldDecl(
    name="gas_molecular_fraction_profile", label="Molecular fraction f_H₂(R)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis"), meaningful_zero=True,
    about=(
        "Σ_H₂ / Σ_gas, from the pressure partition. Rises steeply inward because pressure does; "
        "this is what puts molecular clouds in the inner disc and on arm peaks once a "
        "non-axisymmetric density exists (debt #23). Flat here would mean the pressure is wired wrong."
    ),
)

MOLECULAR_SURFACE = FieldDecl(
    name="gas_molecular_surface_density", label="Molecular gas Σ_H₂(R)", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about="The molecular half of the partition. Where clouds would be sampled from, and what a star formation law keyed off H₂ would read.",
)

H2_FRACTION = FieldDecl(
    name="gas_h2_fraction", label="H₂ mass fraction of the gas", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "**Acceptance row 21**, mass-weighted over the disc. Its target is 0.11 with no quoted "
        "uncertainty — a zero-width target, exactly as row 20 and from the same source (debt #17) "
        "— so it cannot pass and the miss is the correct outcome under rule B5. Published by no "
        "stage of either model until now; debt #79's ruling is the prerequisite for this field's "
        "existence, not something it settles."
    ),
)

DUST_TO_GAS = FieldDecl(
    name="dust_to_gas_ratio", label="Dust-to-gas mass ratio", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("cividis", scale="log"), meaningful_zero=True,
    about=(
        "Metallicity is the property that drives it — Rémy-Ruyer found it dominant over four other "
        "galactic parameters, with a Spearman rank of -0.45 against -0.30 for stellar mass and "
        "-0.25 for star formation rate. The observed scatter is 0.37 dex in 0.1 dex metallicity "
        "bins — a factor of 2.3, and **it does not vary with metallicity**, which is what told "
        "Rémy-Ruyer it is intrinsic rather than measurement error. This derivation publishes the "
        "mean only: under §4b that residual is a seeded draw, left for whichever session gives "
        "this stage a seed. Deriving the mean and calling it the answer would claim a precision "
        "the relation does not have, and the relation itself is only good to a factor of 1.6."
    ),
)

DUST_SURFACE = FieldDecl(
    name="dust_surface_density", label="Dust Σ(R)", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys", scale="log"), meaningful_zero=True,
    about="Gas times the dust-to-gas ratio. The quantity extinction is computed from.",
)

DUST_EXTINCTION = FieldDecl(
    name="dust_extinction_v", label="V-band extinction A_V(R), face-on", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), meaningful_zero=True,
    about=(
        "Magnitudes through the whole disc, face-on. **Extinction is occlusion, not a colour**: a "
        "renderer composites this multiplicatively against what lies behind it, and adding brown "
        "light instead is the usual way dust is drawn wrong. Face-on and axisymmetric, so it "
        "cannot yet make a dust *lane* — lanes need the non-axisymmetric density of debt #23."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    sigma_gas = np.asarray(ctx.fields["gas_surface_density"])
    sigma_star = np.asarray(ctx.fields["stellar_surface_density"])
    h_star = float(ctx.fields["thin_disc_scale_height"])          # pc
    feh = np.asarray(ctx.fields["feh_gas"])

    p_norm = 10.0 ** float(ctx.constants["H2_PRESSURE_LOG_NORM"])
    index = float(ctx.constants["H2_PRESSURE_INDEX"])
    v_disp = float(ctx.constants["H2_GAS_DISPERSION"])

    pressure = midplane_pressure(sigma_gas, sigma_star, h_star, v_disp)
    r_mol = molecular_ratio(pressure, p_norm, index)
    f_mol = r_mol / (1.0 + r_mol)
    sigma_h2 = sigma_gas * f_mol

    # Mass-weighted over the disc, by area: the row is the Galaxy's H₂ fraction,
    # not the fraction at any one radius.
    R = ctx.grid.R
    weight = sigma_gas * R
    total = float(np.trapezoid(weight, R))
    h2_fraction = float(np.trapezoid(weight * f_mol, R) / total) if total > 0.0 else 0.0

    dgr = dust_to_gas(feh, float(ctx.constants["DUST_TO_GAS_SOLAR"]),
                      float(ctx.constants["DUST_TO_GAS_SLOPE"]))
    sigma_dust = sigma_gas * dgr
    a_v = sigma_dust * float(ctx.constants["DUST_EXTINCTION_COEFFICIENT"])

    return {
        "gas_midplane_pressure": pressure,
        "gas_midplane_density": midplane_density(pressure, v_disp),
        "gas_molecular_fraction_profile": f_mol,
        "gas_molecular_surface_density": sigma_h2,
        "gas_h2_fraction": h2_fraction,
        "dust_to_gas_ratio": dgr,
        "dust_surface_density": sigma_dust,
        "dust_extinction_v": a_v,
    }


ISM = IMPLEMENTATIONS.register(
    Stage(
        id="ism",
        slot="ism",
        checkpoint=4,
        about=(
            "Partitions the cold gas into atomic and molecular by midplane pressure, and derives "
            "dust from the gas-phase abundance. Adds no input and no seed: every ingredient is "
            "already published. Shared by every model — the partition does not depend on which "
            "chemistry produced the abundance, though the chemical model could pass [O/H] directly "
            "instead of the iron proxy this uses."
        ),
        compute=compute,
        reads_constants=(
            "H2_PRESSURE_LOG_NORM", "H2_PRESSURE_INDEX", "H2_GAS_DISPERSION",
            "DUST_TO_GAS_SOLAR", "DUST_TO_GAS_SLOPE", "DUST_EXTINCTION_COEFFICIENT",
        ),
        requires=(
            "gas_surface_density", "stellar_surface_density",
            "thin_disc_scale_height", "feh_gas",
        ),
        publishes=(
            MIDPLANE_PRESSURE, MIDPLANE_DENSITY, H2_FRACTION_PROFILE, MOLECULAR_SURFACE, H2_FRACTION,
            DUST_TO_GAS, DUST_SURFACE, DUST_EXTINCTION,
        ),
    )
)
