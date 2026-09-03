"""Chemistry: single-element metallicity, the gradient, and radial migration (checkpoint 3).

One element — total metallicity Z, reported as [Fe/H] = log10(Z/Z☉). The simple
model's defining approximation is instantaneous recycling, so a stellar
generation returns its metals in the same timestep it forms them. S9's delay-time
distribution is what replaces that, and it is why [α/Fe] (acceptance row 24)
cannot be answered here: with no delay there is no α–Fe separation to find.

Per annulus, against the gas and star formation histories the sfh stage
published, and with the infalling gas taken as primordial:

    d(Sigma_gas Z)/dt = NET_YIELD (1 - R) Psi - Z (1 - R) Psi + 0 * f
    =>          dZ/dt = [NET_YIELD (1 - R) Psi - Z f] / Sigma_gas

The two terms are the whole story of a gradient. Enrichment goes as the star
formation rate; dilution goes as the *infall* rate. The inner disc finished
accreting long ago and has been enriching undiluted ever since; the outer disc
is still being rained on by primordial gas. That is where a negative gradient
comes from, and it is why the gradient is set by the inside-out index rather
than by the yield — the yield moves the whole curve up and down.

**Radial migration** applies to stars and not to gas. A star's birth radius is
where its metallicity was set; churning then moves it. Modelled as a Gaussian
in radius whose width grows with age, ``sigma(age) = migration_efficiency *
sqrt(age / 8 Gyr)``, convolved over the birth-radius distribution of each age
bin. So acceptance row 22 — the *present-day* gradient, measured from young
tracers — is untouched by migration, while row 23's old populations are flattened
by it. That contrast is the observable migration is there to reproduce.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC

GRADIENT_FIT_RANGE = (4.0, 12.0)  # kpc; where gradients are actually measured
MIGRATION_REFERENCE_AGE = 8.0  # Gyr, the age the migration width is quoted at
YOUNG_MAX_AGE = 1.0  # Gyr
OLD_MIN_AGE = 10.0  # Gyr


def gradient(feh: np.ndarray, R: np.ndarray, weights: np.ndarray | None = None) -> float:
    """Weighted least-squares slope of [Fe/H] against R over the measured range."""
    lo, hi = GRADIENT_FIT_RANGE
    w = (R > lo) & (R < hi) & np.isfinite(feh)
    if weights is not None:
        w &= weights > 0.0
    if w.sum() < 3:
        return float("nan")
    ww = None if weights is None else weights[w]
    return float(np.polyfit(R[w], feh[w], 1, w=ww)[0])


def migrate(profile: np.ndarray, weight: np.ndarray, R: np.ndarray, sigma: float) -> np.ndarray:
    """Mass-weighted Gaussian smoothing of a per-radius quantity (churning)."""
    if sigma <= 0.0:
        return profile
    kernel = np.exp(-0.5 * ((R[:, None] - R[None, :]) / sigma) ** 2)
    num = kernel @ (weight * profile)
    den = kernel @ weight
    return np.where(den > 0.0, num / np.where(den > 0.0, den, 1.0), np.nan)


METALLICITY_HISTORY = FieldDecl(
    name="metallicity_history", label="Gas metallicity Z(R, t)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("plasma", scale="log"), meaningful_zero=True,
    about=(
        "Mass fraction of metals in the gas. Starts at zero everywhere — the infall is primordial "
        "— and the whole enrichment history is the model's, not an initial condition."
    ),
)

FEH_HISTORY = FieldDecl(
    name="feh_history", label="[Fe/H](R, t)", unit="dex", kind=Kind.FIELD, axes=("R", "t"),
    ramp=Ramp("RdBu", scale="linear", lo=-2.0, hi=0.5), meaningful_zero=True,
    about=(
        "log10(Z/Z☉). Zero is meaningful and is solar, not absent metals; a gas cell with no "
        "metals is −inf and is left as such rather than clipped to a number that would read as a "
        "measurement (rule B9)."
    ),
)

FEH_GAS = FieldDecl(
    name="feh_gas", label="Present-day gas [Fe/H](R)", unit="dex", kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("RdBu", scale="linear", lo=-1.5, hi=0.5), meaningful_zero=True,
    about="The profile acceptance row 22 is fitted to; young tracers such as Cepheids measure this.",
)

FEH_STARS_YOUNG = FieldDecl(
    name="feh_stars_young", label="[Fe/H] of stars younger than 1 Gyr", unit="dex", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("RdBu", scale="linear", lo=-1.5, hi=0.5), meaningful_zero=True,
    about="Barely migrated, so it tracks the gas — which is the check that migration is not misapplied.",
)

FEH_STARS_OLD = FieldDecl(
    name="feh_stars_old", label="[Fe/H] of stars older than 10 Gyr", unit="dex", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("RdBu", scale="linear", lo=-1.5, hi=0.5), meaningful_zero=True,
    about="Migrated the longest, so the flattest. The contrast with the young profile is row 23.",
)

METALLICITY_GRADIENT = FieldDecl(
    name="metallicity_gradient", label="Present-day metallicity gradient", unit="dex/kpc",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Acceptance row 22, fitted to the gas profile over 4–12 kpc — the range the cited "
        "measurements cover. Set by the inside-out index, not by the yield: the yield moves the "
        "whole curve, the differential infall tilts it."
    ),
)

GRADIENT_YOUNG = FieldDecl(
    name="metallicity_gradient_young", label="Gradient, stars younger than 1 Gyr", unit="dex/kpc",
    kind=Kind.SCALAR, meaningful_zero=True,
    about="Acceptance row 23's young end, against a target of about −0.07 dex/kpc.",
)

GRADIENT_OLD = FieldDecl(
    name="metallicity_gradient_old", label="Gradient, stars older than 10 Gyr", unit="dex/kpc",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Acceptance row 23's old end, against about −0.04 dex/kpc. Flatter than the young end only "
        "because of migration, so this row is the one place migration_efficiency is falsifiable."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    dt = ctx.grid.spec.t_max / ctx.grid.spec.n_t
    yield_ = float(ctx.constants["NET_YIELD"])
    ret = float(ctx.constants["RETURN_FRACTION"])
    z_sun = float(ctx.constants["SOLAR_METALLICITY"])

    gas = ctx.fields["gas_surface_density_history"]
    psi = ctx.fields["sfr_surface_density_history"]
    infall = ctx.fields["infall_rate_history"]

    Z = np.zeros_like(R)
    z_hist = np.empty_like(gas)
    for j in range(t.size):
        g = gas[:, j]
        produced = yield_ * (1.0 - ret) * PC_PER_KPC * psi[:, j]  # M☉/pc²/Gyr of new metals
        dZ = np.where(g > 0.0, (produced - Z * infall[:, j]) / np.where(g > 0.0, g, 1.0), 0.0)
        Z = np.clip(Z + dZ * dt, 0.0, 1.0)
        z_hist[:, j] = Z

    with np.errstate(divide="ignore"):
        feh_hist = np.log10(np.where(z_hist > 0.0, z_hist, np.nan) / z_sun)
    feh_gas = feh_hist[:, -1]

    # Age-binned stellar populations, each smoothed by its own migration width.
    age = ctx.grid.spec.t_max - t
    width = float(ctx.inputs["migration_efficiency"])

    def population(mask: np.ndarray) -> np.ndarray:
        if not mask.any():
            return np.full_like(R, np.nan)
        formed = psi[:, mask] * dt  # birth-radius weights, up to a constant
        born = np.nansum(formed, axis=1)
        mean_feh = np.where(born > 0.0, np.nansum(np.nan_to_num(feh_hist[:, mask]) * formed, axis=1) / np.where(born > 0.0, born, 1.0), np.nan)
        mean_age = float(np.average(age[mask], weights=np.maximum(formed.sum(axis=0), 1e-300)))
        sigma = width * math.sqrt(max(mean_age, 0.0) / MIGRATION_REFERENCE_AGE)
        return migrate(np.nan_to_num(mean_feh), born, R, sigma)

    young = population(age <= YOUNG_MAX_AGE)
    old = population(age >= OLD_MIN_AGE)
    stars_now = ctx.fields["stellar_surface_density"]

    return {
        "metallicity_history": z_hist,
        "feh_history": feh_hist,
        "feh_gas": feh_gas,
        "feh_stars_young": young,
        "feh_stars_old": old,
        "metallicity_gradient": gradient(feh_gas, R),
        "metallicity_gradient_young": gradient(young, R, stars_now),
        "metallicity_gradient_old": gradient(old, R, stars_now),
    }


CHEMISTRY = IMPLEMENTATIONS.register(
    Stage(
        id="chemistry",
        slot="chemistry",
        checkpoint=3,
        about=(
            "Single-element chemical evolution with instantaneous recycling and primordial infall, "
            "plus a radial-migration kernel acting on stars only. Shared until S9 replaces it with "
            "multi-element yields and a delay-time distribution."
        ),
        compute=compute,
        reads_inputs=("migration_efficiency",),
        reads_constants=("NET_YIELD", "RETURN_FRACTION", "SOLAR_METALLICITY"),
        requires=(
            "gas_surface_density_history",
            "sfr_surface_density_history",
            "infall_rate_history",
            "stellar_surface_density",
        ),
        publishes=(
            METALLICITY_HISTORY, FEH_HISTORY, FEH_GAS, FEH_STARS_YOUNG, FEH_STARS_OLD,
            METALLICITY_GRADIENT, GRADIENT_YOUNG, GRADIENT_OLD,
        ),
    )
)
