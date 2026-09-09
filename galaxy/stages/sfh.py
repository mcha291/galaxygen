"""Star formation history: the baryon budget resolved into gas and stars (checkpoint 3).

S1 put every retained baryon into one exponential and said so (debt #11). This
stage accretes them over time and lets a star formation law decide what is still
gas at t = now, which is the mechanism debt #11 predicted would close the
acceptance row 3 miss.

The model, per annulus, with instantaneous recycling:

    dSigma_gas/dt  = f(R, t) - (1 - RETURN_FRACTION) * Psi(R, t)
    dSigma_star/dt =           (1 - RETURN_FRACTION) * Psi(R, t)

- **Infall** ``f(R, t) = A(R) exp(-t/tau(R))`` with ``tau(R) = tau_0 (R/R_0)^n``
  — inside-out growth, the outer disc still accreting today. The merger-delivered
  share arrives as the assembly stage's delivery windows and accretes on the same
  timescale from each event's own epoch (S13, debt #30). GALAXY_INPUTS.md §3
  states tau_0 as "~7 Gyr **at R_0**" in one row and the law as
  ``tau_0 (R/R_d)^n`` in the next; those cannot both hold, and R_0 is the one
  that matches the source's own numbers (DECISIONS.md D43).
- **Star formation** is Kennicutt-Schmidt, switched off below a threshold:
  ``Psi = KS_NORM * Sigma_gas^KS_INDEX * s(Sigma_gas)``. The threshold is what
  leaves an extended gas disc outside a truncated stellar one. Since S18 it is
  Kennicutt's own, ``Sigma_crit(R) = alpha kappa(R) sigma_g / 3.36 G``, off the
  checkpoint-1 curve's epicyclic frequency (debt #47): 11 M☉/pc² at R₀ falling to
  4 at 20 kpc, where the constant 5 that stood until then was the bottom of its
  cited range and held the gas at R₀ at 6.3 against the observed 10–13. The switch ``s``
  is a ``tanh`` of width a quarter of the threshold, **not** a step, and that is
  a numerical requirement rather than a flourish: a step makes the star
  formation rate a grid-alignment artefact. Self-regulation holds a wide annulus
  of gas *at* the threshold, so with a step the integrated SFR depends on which
  side of it each cell lands on, and it wanders between 1.47 and 1.79 with no
  trend as N_R and N_t change. With the switch it converges to 0.1%
  ``[verified: tests/test_sfh.py::test_the_star_formation_rate_converges]``.
- **The accreting gas is more extended than the stars it makes**, by
  ``GAS_DISC_SCALE_RATIO`` — and, since S16, by the high-j tail the halo stage
  derives from its angular-momentum distribution (debt #18): the part of the
  budget the exponential never held, beyond about 12 kpc, on the same
  inside-out law, which at those radii is already 10–20 Gyr. That is the outer
  HI disc; the ratio still multiplies nothing at 1.0 (debt #45).
- **The spheroid never accretes** (S17, debt #11). The low-j end of the same
  distribution is mass no exponential disc of this scale length can hold, and
  the halo stage derives it as the central spheroid; it is already stars, so it
  leaves the budget this stage accretes and rejoins ``stellar_mass_total`` at
  the end. Removing it is not a bookkeeping detail: it takes 13% of the budget
  out of the disc, which is why acceptance row 2 moved with it.

**Why the rotation curve is recomputed here.** Acceptance row 3 reads a velocity
at R_0, and until this stage the model does not know how the baryons are
distributed — checkpoint 1 has one exponential holding gas and stars together.
So the checkpoint-1 curve stays as stage one's preview and the *acceptance*
scalars are published here, off the three-component mass distribution: two
razor-thin discs and, since S17, the spheroid, whose own circular velocity is
Newton's and enters the same quadrature.
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
from galaxy.stages.halo import hernquist_enclosed


# Width of the threshold switch, as a fraction of the threshold itself. A
# threshold in nature is not a step, and a step here is numerically fatal (see
# the module docstring), so the width belongs to the threshold rather than
# being a constant of its own.
THRESHOLD_WIDTH = 0.25


def star_formation_rate(gas: np.ndarray, norm: float, index: float, threshold: float | np.ndarray) -> np.ndarray:
    """Kennicutt-Schmidt with a smooth low-density cutoff, in M☉/yr/kpc²; ``threshold`` may vary with radius."""
    switch = 0.5 * (1.0 + np.tanh((gas - threshold) / (THRESHOLD_WIDTH * threshold)))
    return norm * np.maximum(gas, 0.0) ** index * switch


def toomre_threshold(kappa: np.ndarray, alpha: float, sigma_g: float, G: float) -> np.ndarray:
    """Kennicutt's Σ_crit = α κ σ_g / 3.36 G in M☉/pc², with κ in km/s/kpc and G in the model's units."""
    return alpha * np.asarray(kappa, dtype=float) * sigma_g / (3.36 * G) / PC_PER_KPC**2


SF_THRESHOLD_SURFACE_DENSITY = FieldDecl(
    name="sf_threshold_surface_density", label="Star formation threshold Σ_crit(R)", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("cividis", scale="log"), meaningful_zero=True,
    about=(
        "Kennicutt's threshold from the rotation curve's epicyclic frequency: the gas surface "
        "density below which the disc is Toomre-stable and forms no stars. Falls outward with κ, "
        "so the inner disc holds more gas below it than a constant would and the outer disc less; "
        "the gas at R₀ sits just under it, which is why the model's gas there reads what is "
        "observed since S18 (debt #47)."
    ),
)


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
        "Every retained baryon the star formation law has not consumed, helium included. The grid "
        "reaches exactly 30 kpc, which is why R_max was set there (D6). Acceptance row 20 counts "
        "hydrogen and reads hydrogen_mass_30kpc since S13 (debt #41)."
    ),
)

HYDROGEN_MASS_30KPC = FieldDecl(
    name="hydrogen_mass_30kpc", label="Hydrogen mass inside 30 kpc", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 20: the gas mass times (1 − Y), because the target — HI plus H₂ from 21 cm "
        "and CO — is hydrogen and the model's gas is not (debt #41, S13). The metals' one to two "
        "percent stays in, this stage being upstream of the chemistry. The target is quoted with no "
        "uncertainty at all (debt #17)."
    ),
)

STELLAR_MASS_TOTAL = FieldDecl(
    name="stellar_mass_total", label="Total stellar mass", unit="Msun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Acceptance row 1, and now actually stellar: S1 published the whole baryon budget under "
        "this name because it had no gas phase (debt #11). The difference is the gas mass, and "
        "it is no longer assumed — the star formation law decides it. Since S17 it is the disc's "
        "stars *plus the spheroid*, because the row's own target is rows 10 + 11 + 12 and so "
        "includes the bulge (AUDIT_RUN2.md §5, D-5); until then the row passed while counting "
        "only the disc, and the disc carried the bulge's mass."
    ),
)

BULGE_STELLAR_FRACTION = FieldDecl(
    name="bulge_stellar_fraction", label="Bulge/total stellar fraction", unit="dimensionless",
    kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Acceptance row 13: the spheroid's share of the stars. Published here rather than beside "
        "the other bulge scalars because this is the stage that knows how many stars the disc "
        "made — the halo derives the spheroid's mass, this stage derives everything it is a "
        "fraction of. Statistical in the table (debt #8) against a residual the model does not "
        "draw: the mass is derived, so every seed reads the same number."
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
        "The stars and the gas are solved separately as razor-thin discs of arbitrary profile; the "
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


STARS_FORMED_HISTORY = FieldDecl(
    name="stars_formed_history", label="Stars formed per step, where they are now", unit="Msun/pc2",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "Surface density locked into stars at each step, at the radii those stars occupy today: "
        "(1 − R) Ψ dt moved through the radial spread of every major merger since (S18, debt #19). "
        "The vertical stage sorts this rather than the birth history, so a population's shape "
        "carries the merger's radial heating as well as its vertical one. Equal to (1 − R) Ψ dt "
        "when there is no major merger; the chemistry still reads the birth history, because an "
        "abundance is set where a star was born."
    ),
)


def radial_transport(formed: np.ndarray, spread: np.ndarray, R: np.ndarray, dR: float) -> np.ndarray:
    """Move each step's stars through a Gaussian in radius of rms ``spread[:, j]``, conserving mass.

    The spread is piecewise constant in time — it changes only where a major merger
    lands — so one kernel serves every step between events. The kernel is built on
    ring masses and row-normalised, so what leaves a ring arrives somewhere on the
    grid and the total is exact to rounding; the surface density is that mass over
    the ring's area again.
    """
    out = np.array(formed, dtype=float, copy=True)
    area = 2.0 * math.pi * R * dR
    start = 0
    for stop in range(1, spread.shape[1] + 1):
        if stop < spread.shape[1] and np.array_equal(spread[:, stop], spread[:, start]):
            continue
        width = spread[:, start]
        if np.any(width > 0.0):
            k = np.exp(-0.5 * ((R[None, :] - R[:, None]) / np.maximum(width, 1e-9)[:, None]) ** 2)
            k /= k.sum(axis=1, keepdims=True)
            out[:, start:stop] = (k.T @ (formed[:, start:stop] * area[:, None])) / area[:, None]
        start = stop
    return out


def infall_profile(R: np.ndarray, R_inf: float, baryons: float) -> np.ndarray:
    """Surface density of everything that will ever accrete: one exponential of scale ``R_inf``, normalised to the budget.

    Factored out at S14 so that debt #18's second, high-angular-momentum component
    could be probed by substituting this one function (D114) before anyone builds it.
    """
    shape = np.exp(-R / R_inf)
    return shape * baryons / surface_to_mass(shape, R)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    dt = ctx.grid.spec.t_max / ctx.grid.spec.n_t
    ret = float(ctx.constants["RETURN_FRACTION"])
    ks_n, ks_k = float(ctx.constants["KS_NORM"]), float(ctx.constants["KS_INDEX"])
    G = float(ctx.constants["G"])
    R_sun = float(ctx.constants["R_SUN"])
    # The threshold is Kennicutt's, off the checkpoint-1 curve (S18, debt #47). That curve has
    # every baryon in one exponential and no gas, so κ inside a few kpc is the preview's; the
    # resolved curve is this stage's own output and cannot set its own threshold (rule A1).
    crit = toomre_threshold(
        ctx.fields["epicyclic_frequency"], float(ctx.constants["TOOMRE_ALPHA"]),
        float(ctx.constants["GAS_DISPERSION"]), G,
    )

    R_d = float(ctx.fields["disc_scale_length_spin"])
    baryons = float(ctx.fields["baryon_mass_total"])

    # Total gas to be accreted at each radius: the exponential, plus the high-j tail the halo
    # stage derived from its angular-momentum distribution (S16, debt #18) — the tail's share
    # comes out of the exponential's budget, so the total is still every retained baryon. The
    # low-j end of the same distribution is the spheroid (S17, debt #11) and it never accretes
    # onto the disc at all: it is already stars, so its share leaves the budget here and
    # rejoins the total stellar mass below.
    R_inf = float(ctx.constants["GAS_DISC_SCALE_RATIO"]) * R_d
    share = float(ctx.fields["infall_tail_share"])
    M_bulge = float(ctx.fields["bulge_stellar_mass"])
    a_bulge = float(ctx.fields["bulge_scale_radius"])
    share_bulge = M_bulge / baryons
    sigma_total = (
        infall_profile(R, R_inf, (1.0 - share - share_bulge) * baryons)
        + np.asarray(ctx.fields["infall_tail_surface_density"], dtype=float)
    )

    # Inside-out infall timescale, anchored at R_0 (see the module docstring).
    tau = float(ctx.inputs["infall_timescale"]) * (R / R_sun) ** float(ctx.inputs["inside_out_index"])
    amplitude = sigma_total

    # Two infalls, and the second one is the merger (ruling 11). Both accrete on the
    # same inside-out timescale. The smooth episode carries whatever the mergers do
    # not, so the budget still adds to one; the merger-delivered gas arrives as the
    # assembly stage's ``merger_delivery`` — each event's share spread over its own
    # crossing time at its own epoch — and accretes from there (S13, debt #30). Until
    # S13 it was a step at the last major merger, which put a minor event's gas five
    # Gyr early and made rows 1 and 10 move non-monotonically with N_t.
    merger_share = float(ctx.fields["second_infall_share"])
    delivery = np.asarray(ctx.fields["merger_delivery"], dtype=float)  # budget fraction per Gyr

    def episode(start: float) -> np.ndarray:
        """Normalised exp(-(t - start)/tau) per radius, zero before ``start``."""
        span = ctx.grid.spec.t_max - start
        norm = tau * (1.0 - np.exp(-span / tau))
        elapsed = t[None, :] - start
        return np.where(elapsed >= 0.0, np.exp(-np.maximum(elapsed, 0.0) / tau[:, None]), 0.0) / norm[:, None]

    early = episode(0.0)
    # A unit of gas delivered in step j accretes as decay^(k - j) over the steps k >= j,
    # normalised so that the whole of it has arrived by the last step — the discrete
    # form of the ``episode`` kernel, exact on the grid so the budget closes to
    # rounding. Convolving the delivery with it is the exponential's own recursion,
    # one multiply per step.
    decay = np.exp(-dt / tau)
    late = np.zeros_like(R)
    n_t_steps = t.size

    gas = np.zeros_like(R)
    gas_hist = np.empty((R.size, t.size))
    sfr_hist = np.empty((R.size, t.size))
    infall_hist = np.empty((R.size, t.size))
    formed_hist = np.empty((R.size, t.size))
    for j, tj in enumerate(t):
        remaining = dt * (1.0 - decay ** (n_t_steps - j)) / (1.0 - decay)  # >= dt: the steps left, weighted
        late = late * decay + delivery[j] * dt / remaining
        infall = sigma_total * ((1.0 - merger_share) * early[:, j] + late)
        psi = star_formation_rate(gas, ks_n, ks_k, crit)
        locked = (1.0 - ret) * PC_PER_KPC * psi  # M☉/yr/kpc² -> M☉/pc²/Gyr
        gas = np.maximum(gas + (infall - locked) * dt, 0.0)
        gas_hist[:, j] = gas
        sfr_hist[:, j] = psi
        infall_hist[:, j] = infall
        formed_hist[:, j] = locked * dt
    psi_now = star_formation_rate(gas, ks_n, ks_k, crit)
    # The stars never feed back on the gas, so where a merger moved them can be settled once
    # the history is complete: every step's stars go through the radial spread of the major
    # mergers after it (S18, debt #19), and the present-day stellar disc is the sum.
    formed_now = radial_transport(
        formed_hist, np.asarray(ctx.fields["disc_radial_spread"], dtype=float), R, ctx.grid["R"].width,
    )
    stars = formed_now.sum(axis=1)

    R_star = fit_scale_length(stars, R, 1.0, 3.0 * R_d)
    R_gas = fit_scale_length(gas, R, 1.0, ctx.grid.spec.R_max)
    m_star, m_gas = surface_to_mass(stars, R), surface_to_mass(gas, R)

    # Neither profile is an exponential, so each goes through the general razor-thin
    # solver rather than through a fitted single exponential — once per profile, the
    # grid and R_0 together, because the solver's cost is in the profile, not the points.
    at = np.append(R, R_sun)
    v_star_all = disc_circular_velocity(stars, R, G, at=at)
    v_gas_all = disc_circular_velocity(gas, R, G, at=at)
    v_star, v_star_sun = v_star_all[:-1], float(v_star_all[-1])
    v_gas, v_gas_sun = v_gas_all[:-1], float(v_gas_all[-1])
    # The spheroid is the third baryonic component and rotation at R_0 must see it: it is a
    # sphere, so its own circular velocity is Newton's, and it enters the quadrature beside the
    # two razor-thin discs. This is the whole of debt #11's remaining prediction for row 3.
    v_bulge = np.sqrt(G * hernquist_enclosed(R, M_bulge, a_bulge) / R)
    v_bulge_sun = math.sqrt(G * float(hernquist_enclosed(R_sun, M_bulge, a_bulge)) / R_sun)
    v_baryons = np.sqrt(v_star**2 + v_gas**2 + v_bulge**2)
    v_sun = math.hypot(
        float(ctx.fields["halo_circular_velocity_sun"]),
        math.sqrt(v_star_sun**2 + v_gas_sun**2 + v_bulge_sun**2),
    )
    stars_total = m_star + M_bulge

    return {
        "gas_surface_density": gas,
        "stellar_surface_density": stars,
        "sfr_surface_density": psi_now,
        "gas_surface_density_history": gas_hist,
        "sfr_surface_density_history": sfr_hist,
        "infall_rate_history": infall_hist,
        "stars_formed_history": formed_now,
        "sf_threshold_surface_density": crit,
        "sfr": float(np.trapezoid(psi_now * 2.0 * math.pi * R, R)),
        "gas_mass_30kpc": m_gas,
        "hydrogen_mass_30kpc": m_gas * (1.0 - float(ctx.constants["HELIUM_MASS_FRACTION"])),
        "stellar_mass_total": stars_total,
        "bulge_stellar_fraction": M_bulge / stars_total if stars_total > 0.0 else 0.0,
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
            "RETURN_FRACTION", "KS_NORM", "KS_INDEX", "TOOMRE_ALPHA", "GAS_DISPERSION",
            "GAS_DISC_SCALE_RATIO", "G", "R_SUN", "V_SUN_PECULIAR", "HELIUM_MASS_FRACTION",
        ),
        requires=(
            "disc_scale_length_spin", "baryon_mass_total", "epicyclic_frequency",
            "infall_tail_surface_density", "infall_tail_share",
            "bulge_stellar_mass", "bulge_scale_radius",
            "halo_circular_velocity", "halo_circular_velocity_sun",
            "second_infall_share", "merger_delivery", "disc_radial_spread",
        ),
        publishes=(
            GAS_SURFACE_DENSITY, STELLAR_SURFACE_DENSITY, SFR_SURFACE_DENSITY,
            GAS_HISTORY, SFR_HISTORY, INFALL_HISTORY, STARS_FORMED_HISTORY, SF_THRESHOLD_SURFACE_DENSITY,
            SFR, GAS_MASS_30KPC, HYDROGEN_MASS_30KPC, STELLAR_MASS_TOTAL, BULGE_STELLAR_FRACTION,
            STELLAR_SCALE_LENGTH,
            CIRCULAR_VELOCITY_RESOLVED, V_CIRCULAR_SUN, V_TANGENTIAL_SUN,
        ),
    )
)
