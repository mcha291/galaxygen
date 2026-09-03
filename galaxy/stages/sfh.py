"""Star formation history: the baryon budget resolved into gas and stars (checkpoint 3).

S1 put every retained baryon into one exponential and said so (debt #11). This
stage accretes them over time and lets a star formation law decide what is still
gas at t = now, which is the mechanism debt #11 predicted would close the
acceptance row 3 miss.

The model, per annulus, with instantaneous recycling:

    dSigma_gas/dt  = f(R, t) - (1 - RETURN_FRACTION) * Psi(R, t)
    dSigma_star/dt =           (1 - RETURN_FRACTION) * Psi(R, t)

- **Infall** ``f(R, t) = A(R) exp(-t/tau(R))`` with ``tau(R) = tau_0 (R/R_0)^n``
  — inside-out growth, the outer disc still accreting today. GALAXY_INPUTS.md §3
  states tau_0 as "~7 Gyr **at R_0**" in one row and the law as
  ``tau_0 (R/R_d)^n`` in the next; those cannot both hold, and R_0 is the one
  that matches the source's own numbers (DECISIONS.md D43).
- **Star formation** is Kennicutt-Schmidt, switched off below a threshold:
  ``Psi = KS_NORM * Sigma_gas^KS_INDEX * s(Sigma_gas)``. The threshold is what
  leaves an extended gas disc outside a truncated stellar one. The switch ``s``
  is a ``tanh`` of width a quarter of the threshold, **not** a step, and that is
  a numerical requirement rather than a flourish: a step makes the star
  formation rate a grid-alignment artefact. Self-regulation holds a wide annulus
  of gas *at* the threshold, so with a step the integrated SFR depends on which
  side of it each cell lands on, and it wanders between 1.47 and 1.79 with no
  trend as N_R and N_t change. With the switch it converges to 0.1%
  ``[verified: tests/test_sfh.py::test_the_star_formation_rate_converges]``.
- **The accreting gas is more extended than the stars it makes**, by
  ``GAS_DISC_SCALE_RATIO``. Without that the model has no outer HI at all.

**Why the rotation curve is recomputed here.** Acceptance row 3 reads a velocity
at R_0, and until this stage the model does not know how the baryons are
distributed — checkpoint 1 has one exponential holding gas and stars together.
So the checkpoint-1 curve stays as stage one's preview and the *acceptance*
scalars are published here, off the two-component mass distribution.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC, disc_circular_velocity


# Width of the threshold switch, as a fraction of the threshold itself. A
# threshold in nature is not a step, and a step here is numerically fatal (see
# the module docstring), so the width belongs to the threshold rather than
# being a constant of its own.
THRESHOLD_WIDTH = 0.25


def star_formation_rate(gas: np.ndarray, norm: float, index: float, threshold: float) -> np.ndarray:
    """Kennicutt-Schmidt with a smooth low-density cutoff, in M☉/yr/kpc²."""
    switch = 0.5 * (1.0 + np.tanh((gas - threshold) / (THRESHOLD_WIDTH * threshold)))
    return norm * np.maximum(gas, 0.0) ** index * switch


def surface_to_mass(sigma: np.ndarray, R: np.ndarray) -> float:
    """Integrate a surface density in M☉/pc² over the grid to a mass in M☉."""
    return float(np.trapezoid(sigma * PC_PER_KPC**2 * 2.0 * math.pi * R, R))


def fit_scale_length(sigma: np.ndarray, R: np.ndarray, lo: float, hi: float) -> float:
    """Least-squares exponential scale length of ``sigma`` over ``lo < R < hi``."""
    w = (R > lo) & (R < hi) & (sigma > 0.0)
    if w.sum() < 3:
        return float("nan")
    slope = np.polyfit(R[w], np.log(sigma[w]), 1)[0]
    return float(-1.0 / slope)


GAS_SURFACE_DENSITY = FieldDecl(
    name="gas_surface_density", label="Gas surface density", unit="Msun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("cividis", scale="log"), meaningful_zero=True,
    about=(
        "What the star formation law has not consumed. Far shallower than the stars: inside the "
        "threshold radius the gas is held near the threshold because anything above it is turned "
        "into stars within a depletion time, and outside it nothing is consumed at all."
    ),
)

STELLAR_SURFACE_DENSITY = FieldDecl(
    name="stellar_surface_density", label="Stellar surface density", unit="Msun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "Built up by the star formation law rather than assumed. Its exponential scale length is "
        "therefore a *result* — and it does not agree with the one lambda_d predicts (debt #13)."
    ),
)

SFR_SURFACE_DENSITY = FieldDecl(
    name="sfr_surface_density", label="SFR surface density", unit="Msun/yr/kpc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about="Present-day Kennicutt-Schmidt rate. Zero outside the threshold radius, sharply so.",
)

GAS_HISTORY = FieldDecl(
    name="gas_surface_density_history", label="Gas surface density history", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("cividis", scale="log"), meaningful_zero=True,
    about="Sigma_gas(R, t) over cosmic time, t = 0 at the Big Bang. Chemistry integrates against it.",
)

SFR_HISTORY = FieldDecl(
    name="sfr_surface_density_history", label="SFR surface density history", unit="Msun/yr/kpc2",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about=(
        "Psi(R, t). The inside-out signature is here rather than in any single snapshot: the inner "
        "disc peaks early and fades, the outer disc is still rising."
    ),
)

INFALL_HISTORY = FieldDecl(
    name="infall_rate_history", label="Infall rate history", unit="Msun/pc2", kind=Kind.FIELD,
    axes=("R", "t"), ramp=Ramp("viridis", scale="log"), meaningful_zero=True,
    about=(
        "f(R, t), per Gyr. Unit is a surface density because the closed vocabulary has no "
        "surface-density-per-time symbol yet; the per-Gyr is in the name and in this line, which "
        "is a wart the session that needs the unit should fix."
    ),
)

SFR = FieldDecl(
    name="sfr", label="Star formation rate", unit="Msun/yr", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Acceptance row 2. A genuine prediction: the Kennicutt-Schmidt normalisation is measured "
        "and deliberately not fitted, so this number is what the accretion history and the "
        "threshold happen to leave forming stars today."
    ),
)

GAS_MASS_30KPC = FieldDecl(
    name="gas_mass_30kpc", label="Gas mass inside 30 kpc", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 20, whose target is quoted with no uncertainty at all. The grid reaches "
        "exactly 30 kpc, which is why R_max was set there (D6)."
    ),
)

STELLAR_MASS_TOTAL = FieldDecl(
    name="stellar_mass_total", label="Total stellar mass", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 1, and now actually stellar: S1 published the whole baryon budget under "
        "this name because it had no gas phase (debt #11). The difference is the gas mass, and "
        "it is no longer assumed — the star formation law decides it."
    ),
)

STELLAR_SCALE_LENGTH = FieldDecl(
    name="thin_disc_scale_length", label="Thin disc scale length R_d", unit="kpc", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 4, fitted to the stellar surface density the model actually built, over "
        "1 kpc to 3 R_d. This is the model's prediction of the observable; the lambda_d route "
        "publishes its own under disc_scale_length_spin, and the two disagree by a third "
        "(debt #13). Reading the fitted one here is the honest choice — row 4 measures starlight, "
        "not angular momentum."
    ),
)

CIRCULAR_VELOCITY_RESOLVED = FieldDecl(
    name="circular_velocity_resolved", label="Circular velocity (stars + gas + halo)", unit="km/s",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis", scale="linear", lo=0.0, hi=300.0),
    meaningful_zero=True,
    about=(
        "Supersedes the checkpoint-1 circular_velocity, which had every baryon in one exponential. "
        "The stars and the gas are fitted separately and each given Freeman's razor-thin form; the "
        "checkpoint-1 field stays because stage one's preview is a rotation curve and stage one "
        "does not know the split."
    ),
)

V_CIRCULAR_SUN = FieldDecl(
    name="v_circular_sun", label="Circular velocity at R₀", unit="km/s", kind=Kind.SCALAR,
    meaningful_zero=True,
    about="v_c(R₀) off the resolved mass distribution. Commonly quoted as 238 ± 15 km/s.",
)

V_TANGENTIAL_SUN = FieldDecl(
    name="v_tangential_sun", label="Solar tangential velocity", unit="km/s", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 3, moved here from checkpoint 1 because a velocity at R₀ cannot be right "
        "until the mass inside R₀ is right. Debt #11 predicted this would fall by about 10 km/s "
        "once the gas left the stellar profile; what it actually did is recorded in DECISIONS."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    dt = ctx.grid.spec.t_max / ctx.grid.spec.n_t
    ret = float(ctx.constants["RETURN_FRACTION"])
    ks_n, ks_k = float(ctx.constants["KS_NORM"]), float(ctx.constants["KS_INDEX"])
    crit = float(ctx.constants["SF_THRESHOLD"])
    G = float(ctx.constants["G"])
    R_sun = float(ctx.constants["R_SUN"])

    R_d = float(ctx.fields["disc_scale_length_spin"])
    baryons = float(ctx.fields["baryon_mass_total"])

    # Total gas to be accreted at each radius: exponential, more extended than the stars.
    R_inf = float(ctx.constants["GAS_DISC_SCALE_RATIO"]) * R_d
    shape = np.exp(-R / R_inf)
    sigma_total = shape * baryons / surface_to_mass(shape, R)

    # Inside-out infall timescale, anchored at R_0 (see the module docstring).
    tau = float(ctx.inputs["infall_timescale"]) * (R / R_sun) ** float(ctx.inputs["inside_out_index"])
    amplitude = sigma_total / (tau * (1.0 - np.exp(-ctx.grid.spec.t_max / tau)))

    gas = np.zeros_like(R)
    stars = np.zeros_like(R)
    gas_hist = np.empty((R.size, t.size))
    sfr_hist = np.empty((R.size, t.size))
    infall_hist = np.empty((R.size, t.size))
    for j, tj in enumerate(t):
        infall = amplitude * np.exp(-tj / tau)
        psi = star_formation_rate(gas, ks_n, ks_k, crit)
        locked = (1.0 - ret) * PC_PER_KPC * psi  # M☉/yr/kpc² -> M☉/pc²/Gyr
        gas = np.maximum(gas + (infall - locked) * dt, 0.0)
        stars = stars + locked * dt
        gas_hist[:, j] = gas
        sfr_hist[:, j] = psi
        infall_hist[:, j] = infall
    psi_now = star_formation_rate(gas, ks_n, ks_k, crit)

    R_star = fit_scale_length(stars, R, 1.0, 3.0 * R_d)
    R_gas = fit_scale_length(gas, R, 1.0, ctx.grid.spec.R_max)
    m_star, m_gas = surface_to_mass(stars, R), surface_to_mass(gas, R)

    # Neither profile is an exponential, so each goes through the general
    # razor-thin solver rather than through a fitted single exponential.
    v_star, res_star = disc_circular_velocity(stars, R, G)
    v_gas, res_gas = disc_circular_velocity(gas, R, G)
    v_star_sun, _ = disc_circular_velocity(stars, R, G, at=R_sun)
    v_gas_sun, _ = disc_circular_velocity(gas, R, G, at=R_sun)
    v_baryons = np.hypot(v_star, v_gas)
    v_sun = math.hypot(
        float(ctx.fields["halo_circular_velocity_sun"]), math.hypot(v_star_sun, v_gas_sun)
    )

    return {
        "gas_surface_density": gas,
        "stellar_surface_density": stars,
        "sfr_surface_density": psi_now,
        "gas_surface_density_history": gas_hist,
        "sfr_surface_density_history": sfr_hist,
        "infall_rate_history": infall_hist,
        "sfr": float(np.trapezoid(psi_now * 2.0 * math.pi * R, R)),
        "gas_mass_30kpc": m_gas,
        "stellar_mass_total": m_star,
        "thin_disc_scale_length": R_star,
        "circular_velocity_resolved": np.hypot(ctx.fields["halo_circular_velocity"], v_baryons),
        "v_circular_sun": v_sun,
        "v_tangential_sun": v_sun + float(ctx.constants["V_SUN_PECULIAR"]),
    }


SFH = IMPLEMENTATIONS.register(
    Stage(
        id="sfh",
        slot="sfh",
        checkpoint=3,
        about=(
            "Inside-out infall, Kennicutt-Schmidt star formation above a threshold, instantaneous "
            "recycling. Splits the baryon budget into gas and stars and republishes the "
            "acceptance-row kinematics off the result. Shared by both models until S9."
        ),
        compute=compute,
        reads_inputs=("infall_timescale", "inside_out_index"),
        reads_constants=(
            "RETURN_FRACTION", "KS_NORM", "KS_INDEX", "SF_THRESHOLD",
            "GAS_DISC_SCALE_RATIO", "G", "R_SUN", "V_SUN_PECULIAR",
        ),
        requires=("disc_scale_length_spin", "baryon_mass_total", "halo_circular_velocity", "halo_circular_velocity_sun"),
        publishes=(
            GAS_SURFACE_DENSITY, STELLAR_SURFACE_DENSITY, SFR_SURFACE_DENSITY,
            GAS_HISTORY, SFR_HISTORY, INFALL_HISTORY,
            SFR, GAS_MASS_30KPC, STELLAR_MASS_TOTAL, STELLAR_SCALE_LENGTH,
            CIRCULAR_VELOCITY_RESOLVED, V_CIRCULAR_SUN, V_TANGENTIAL_SUN,
        ),
    )
)
