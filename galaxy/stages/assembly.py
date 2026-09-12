"""Assembly: the merger history, the gas it delivers, and the disc it heats (checkpoint 2).

Ruling 11 dissolved the `second_infall_onset` input by putting a `gas_fraction`
on each merger event: a gas-rich major merger *is* the second infall rather than
something that happens alongside one. So this stage does two things, and the
second is what the thick disc is made of.

**Gas delivery.** Each event delivers `gas_fraction` of the baryon budget still
outstanding when it arrives. The Milky Way's one major merger therefore splits
the accretion into an early episode that builds a small, old, hot disc and a
later one that builds the thin disc — the two-infall structure, arrived at from
the merger list rather than from an input that names it.

**Heating.** A star's vertical velocity dispersion today is what decides whether
it is thin-disc or thick-disc. Two contributions, added in quadrature:

- **Secular**, from giant molecular clouds and spiral arms, growing as a power of
  age. Every star has it and it alone produces no thick disc — it is a gradient
  in sigma_z, not a second population.
- **Merger**, a discrete jump applied to every star already born when the event
  arrives, scaled by the mass ratio. This is the mechanism that makes the thick
  disc a *population* rather than a tail.

- **Radial**, since S18 (debt #19): the same kick, read as an isotropic velocity
  impulse, moves a star in radius as well as in height. A radial impulse δv_R
  becomes an epicycle of amplitude δv_R/κ; an azimuthal one δv_φ shifts the
  guiding centre by 2Ω δv_φ/κ² and leaves an epicycle of that amplitude around
  it. Averaged over the epicycle, the mean-square displacement from the birth
  radius is σ_k² (1/2κ² + 6Ω²/κ⁴) — 1.5 kpc at R₀ for the default merger and a
  fifth of that at 2 kpc, because κ is what it is inside. Published as an rms
  by birth time and radius; the sfh stage moves the stars it formed through it.

**Why the thick disc cannot be drawn at this checkpoint.** GALAXY_PLAN.md §3
gives stage 2 the preview "edge-on view showing the thick disc appear", but
checkpoint 2 runs before star formation and there are no stars here to heat.
This stage publishes the heating a star born at time t would carry; the
population that heating sorts into thin and thick belongs to checkpoint 3
(DECISIONS.md D50).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import MAJOR_MERGER_RATIO, IMPLEMENTATIONS, MergerEvent
from galaxy.core.stage import Context, Stage


def delivered_shares(events: Sequence[MergerEvent], total: float = 1.0) -> list[float]:
    """Share of the whole baryon budget each event delivers, in time order.

    Each event takes ``gas_fraction`` of what is still outstanding, so the shares
    compose without any of them being able to exceed the budget.
    """
    outstanding = total
    shares = []
    for event in sorted(events, key=lambda e: e.time):
        share = outstanding * event.gas_fraction
        shares.append(share)
        outstanding -= share
    return shares


MERGER_COUNT = FieldDecl(
    name="merger_count", label="Merger events", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True,
    about="How many events the history carries. Zero is a legitimate galaxy and is debt #9's control.",
)

MAJOR_MERGER_COUNT = FieldDecl(
    name="major_merger_count", label="Major mergers", unit="count", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=f"Events above a mass ratio of {MAJOR_MERGER_RATIO}. The Milky Way has one.",
)

LAST_MAJOR_MERGER_TIME = FieldDecl(
    name="last_major_merger_time", label="Last major merger", unit="Gyr", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Cosmic time of the most recent major merger, or 0 if there is none — which is a real "
        "answer and not a missing one, because a galaxy can have had no major merger. Every star "
        "born before it is thick-disc in this model."
    ),
)

SECOND_INFALL_SHARE = FieldDecl(
    name="second_infall_share", label="Share of baryons delivered after the last major merger",
    unit="dimensionless", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "Share of the baryon budget delivered by mergers rather than by smooth accretion — what "
        "ruling 11 replaced the second_infall_onset input with. The rest accretes smoothly from "
        "the start and makes the old, hot disc. Zero for a galaxy with no mergers, which is then "
        "a pure single-infall model and is debt #9's control."
    ),
)

MERGER_DELIVERY = FieldDecl(
    name="merger_delivery", label="Baryon share delivered per Gyr", unit="dimensionless",
    kind=Kind.FIELD, axes=("t",), ramp=Ramp("viridis", scale="linear"), meaningful_zero=True,
    about=(
        "Fraction of the whole baryon budget arriving per Gyr, summed over events. Spread over a "
        "merger's own duration rather than delivered instantaneously, because an instantaneous "
        "delivery makes the star formation rate a function of the timestep."
    ),
)

DISC_HEATING = FieldDecl(
    name="disc_heating", label="σ_z today for a star born at t", unit="km/s", kind=Kind.FIELD,
    axes=("t",), ramp=Ramp("magma", scale="linear", lo=0.0, hi=60.0), meaningful_zero=True,
    about=(
        "Vertical velocity dispersion a star born at cosmic time t carries at the present day: "
        "secular heating over its whole life, plus a jump for every major merger it lived through. "
        "The jump is what separates a thick disc from a warm tail."
    ),
)


DISC_RADIAL_SPREAD = FieldDecl(
    name="disc_radial_spread", label="Radial spread today for a star born at (R, t)", unit="kpc",
    kind=Kind.FIELD, axes=("R", "t"), ramp=Ramp("viridis", scale="linear", lo=0.0, hi=3.0),
    meaningful_zero=True,
    about=(
        "Root-mean-square radial displacement a star born at radius R and cosmic time t carries "
        "today from the major mergers it lived through: the vertical kick read as an isotropic "
        "impulse, turned into a displacement by the epicyclic frequency (the radial part) and the "
        "guiding-centre shift (the azimuthal part), summed in quadrature over events. Zero for "
        "every star born after the last major merger. Grows with radius because κ falls: the "
        "inner disc is stiff and barely moves, which is why the merger cannot make a compact "
        "thick disc extended on its own (S18, debt #19). **The number the records quote for this "
        "field is its maximum over t at a radius** — 1.09 kpc at R₀ and 0.22 at 2 kpc since S20 — "
        "and the viewer draws the field as an image, so the reduction is stated here rather than "
        "left for a reader to guess (debt #73, ruled at S22: a reduction over an axis is a "
        "rendering opinion and rule A9 puts those in the declaration)."
    ),
)


def radial_spread(kick: float, omega: np.ndarray, kappa: np.ndarray) -> np.ndarray:
    """rms radial displacement, in kpc, from an isotropic velocity impulse ``kick`` (km/s).

    ⟨ΔR²⟩ = kick² (1/2κ² + 6Ω²/κ⁴): the first term is the epicycle a radial impulse
    starts, the second the guiding-centre shift an azimuthal impulse makes (2Ω δv/κ²)
    plus the epicycle of that amplitude it leaves the star on.
    """
    return kick * np.sqrt(0.5 / kappa**2 + 6.0 * omega**2 / kappa**4)


def compute(ctx: Context) -> Mapping[str, Any]:
    t = ctx.grid.t
    R = ctx.grid.R
    events = list(ctx.inputs["mergers"])
    now = ctx.grid.spec.t_max

    major = [e for e in events if e.mass_ratio >= MAJOR_MERGER_RATIO]
    last_major = max((e.time for e in major), default=0.0)

    # Gas delivery, spread over each event's own crossing time rather than a spike.
    duration = float(ctx.constants["MERGER_DURATION"])
    delivery = np.zeros_like(t)
    for event, share in zip(sorted(events, key=lambda e: e.time), delivered_shares(events)):
        window = np.exp(-0.5 * ((t - event.time) / duration) ** 2)
        area = np.trapezoid(window, t)
        if area > 0.0:
            delivery += share * window / area

    # Heating: secular for everyone, plus a jump per major merger already survived.
    age = np.maximum(now - t, 0.0)
    sigma0 = float(ctx.constants["BIRTH_DISPERSION"])
    secular = float(ctx.constants["SECULAR_HEATING"]) * (age / 10.0) ** float(ctx.constants["SECULAR_HEATING_INDEX"])
    sigma2 = sigma0**2 + secular**2
    kick = float(ctx.constants["MERGER_HEATING"])
    # The same impulse radially (S18): each event's rms displacement, by radius, applied to
    # the stars already born, in quadrature across events.
    v = np.asarray(ctx.fields["circular_velocity"], dtype=float)
    kappa = np.asarray(ctx.fields["epicyclic_frequency"], dtype=float)
    spread2 = np.zeros((R.size, t.size))
    for event in events:
        if event.mass_ratio >= MAJOR_MERGER_RATIO:
            sigma2 = sigma2 + np.where(t <= event.time, (kick * event.mass_ratio) ** 2, 0.0)
            spread2 += np.where((t <= event.time)[None, :], radial_spread(kick * event.mass_ratio, v / R, kappa)[:, None] ** 2, 0.0)

    merger_share = float(np.trapezoid(delivery, t))

    return {
        "merger_count": float(len(events)),
        "major_merger_count": float(len(major)),
        "last_major_merger_time": last_major,
        "second_infall_share": merger_share,
        "merger_delivery": delivery,
        "disc_heating": np.sqrt(sigma2),
        "disc_radial_spread": np.sqrt(spread2),
    }


ASSEMBLY = IMPLEMENTATIONS.register(
    Stage(
        id="assembly",
        slot="assembly",
        checkpoint=2,
        about=(
            "The merger history: the share of the baryon budget each event delivers and the "
            "vertical heating it leaves in the stars already present. Shared by both models."
        ),
        compute=compute,
        reads_inputs=("mergers",),
        reads_constants=(
            "MERGER_DURATION", "BIRTH_DISPERSION", "SECULAR_HEATING",
            "SECULAR_HEATING_INDEX", "MERGER_HEATING",
        ),
        requires=("circular_velocity", "epicyclic_frequency"),
        publishes=(
            MERGER_COUNT, MAJOR_MERGER_COUNT, LAST_MAJOR_MERGER_TIME,
            SECOND_INFALL_SHARE, MERGER_DELIVERY, DISC_HEATING, DISC_RADIAL_SPREAD,
        ),
    )
)
