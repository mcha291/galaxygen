"""Light: the disc's unresolved surface brightness and its colour (RENDER_PLAN R3).

A photograph of a galaxy is mostly light no star in it can be picked out of, and
the materialised catalogue is a sample of 2 × 10⁴ stars from 10¹¹. So the smooth
component is published as a field, from the same isochrones the catalogue's
photometry reads (``galaxy/stages/photometry.py``), and the viewer draws the
sample over it.

**The integral.** ``stars_formed_history`` is the mass locked into stars at each
step, *at the radii those stars occupy today* — which is exactly the reading a
present-day image needs, and the reason the formation-history scrubber could not
use it. Locked mass is (1 − R) of the mass formed, so dividing by that gives the
mass formed, and each step's contribution is that times the light per unit mass
formed of a Kroupa population of its age and metallicity, integrated along the
isochrone once and tabulated. The colour is the same sum carried in linear sRGB and
reduced to a correlated colour temperature.

**What it does not include, recorded rather than hidden.**

- *Metallicity at present radius.* Each step is read at ``feh_history`` where its
  stars are now, not where they were born; migration mixes that by up to a few
  kiloparsecs and a quarter-dex of [Fe/H] moves the light by a few per cent.
- *The classical bulge's population.* It is a scalar mass with no history, so its
  light is an old population at the inner disc's abundance: a stated proxy.
- *Dust.* The light is emitted, not observed. ``dust_extinction_v`` is published by
  the ISM stage and is the viewer's to subtract (RENDER_PLAN R4).
- *Ages past 12.6 Gyr read at 12.6 Gyr*, and [Fe/H] for [M/H], as for the catalogue.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.cmaps import BLACKBODY_KELVIN
from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.photometry import correlated_temperature, population_at

SURFACE_BRIGHTNESS = FieldDecl(
    name="disc_surface_brightness", label="Disc surface brightness Σ_L(R)", unit="Lsun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "Bolometric light per square parsec from every star the disc has formed and still has "
        "alive: each step of stars_formed_history, over (1 − R), times a Kroupa population's light "
        "per unit mass formed at that age and the [Fe/H] where those stars are now, from the PARSEC "
        "isochrones. Emitted, not observed: no dust."
    ),
)

LIGHT_TEMPERATURE = FieldDecl(
    name="disc_light_temperature", label="Colour temperature of the disc light", unit="K",
    kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("blackbody", scale="log", lo=BLACKBODY_KELVIN[0], hi=BLACKBODY_KELVIN[1]), meaningful_zero=False,
    about=(
        "The correlated colour temperature of the same sum: every population's light carried in "
        "linear sRGB, weighted by luminosity, and read as the nearest blackbody. A population is not "
        "a blackbody, so this is a colour and not a temperature of anything; it is drawn with the "
        "blackbody cmap because that is what a colour temperature means. An old disc reads cooler "
        "than the Sun because its light is the giants'."
    ),
)

HALPHA_SURFACE_BRIGHTNESS = FieldDecl(
    name="halpha_surface_brightness", label="Hα surface brightness Σ_Hα(R)", unit="Lsun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about=(
        "Line emission from the ionised gas around young massive stars (RENDER_PLAN M4): today's "
        "sfr_surface_density times a Level 0 constant, 4.86 × 10⁷ L☉ per M☉/yr of star formation "
        "(Kennicutt & Evans 2012 for a Kroupa IMF, D166). Intrinsic, before dust. Bolometrically a "
        "thousandth of the starlight, but all of it in one red line, which is why star-forming "
        "arms look pink in a colour image."
    ),
)

BULGE_LUMINOSITY = FieldDecl(
    name="bulge_luminosity", label="Bulge luminosity", unit="Lsun", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The classical bulge's light: its stellar mass over (1 − R), times a Kroupa population's light "
        "per unit mass formed. The bulge is a mass with no history, so its population is taken as old "
        "as the grid's first step and at the mass-weighted [Fe/H] of the stars formed at its scale "
        "radius — the nearest thing the model publishes to its stars, and a stated proxy, not a result."
    ),
)

BULGE_LIGHT_TEMPERATURE = FieldDecl(
    name="bulge_light_temperature", label="Colour temperature of the bulge light", unit="K",
    kind=Kind.SCALAR, meaningful_zero=False,
    about="The correlated colour temperature of the same old population, as for the disc.",
)

DISC_LUMINOSITY = FieldDecl(
    name="disc_luminosity", label="Disc luminosity", unit="Lsun", kind=Kind.SCALAR, meaningful_zero=True,
    about="Σ_L integrated over the disc, 2πR dR. Bolometric and dust-free, so not yet comparable to an observed magnitude.",
)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    locked = np.asarray(ctx.fields["stars_formed_history"], dtype=float)  # M☉/pc², (R, t)
    formed = locked / (1.0 - float(ctx.constants["RETURN_FRACTION"]))
    age = t[-1] - t  # Gyr, per step
    light_per_mass, colour = population_at(np.broadcast_to(age, formed.shape), ctx.fields["feh_history"])

    emitted = formed * light_per_mass  # L☉/pc² per step
    brightness = emitted.sum(axis=1)
    rgb = (emitted[..., None] * colour).sum(axis=1)
    temperature = correlated_temperature(rgb)

    area = 2.0 * np.pi * R * (PC_PER_KPC**2)  # pc² per kpc of radius

    # M4: the line. Σ_SFR is per kpc², the constant per M☉/yr.
    halpha = np.asarray(ctx.fields["sfr_surface_density"], dtype=float) * float(ctx.constants["HALPHA_PER_SFR"]) / PC_PER_KPC**2

    # The bulge: old, at the abundance of the stars formed where it sits (a stated proxy).
    at = int(np.argmin(np.abs(R - float(ctx.fields["bulge_scale_radius"]))))
    weights = formed[at]
    feh_row = np.nan_to_num(np.asarray(ctx.fields["feh_history"], dtype=float)[at], nan=0.0, neginf=-3.0, posinf=1.0)
    feh_bulge = float(np.average(feh_row, weights=weights)) if weights.sum() > 0 else 0.0
    bulge_light, bulge_colour = population_at(np.array([age[0]]), np.array([feh_bulge]))
    bulge_formed = float(ctx.fields["bulge_stellar_mass"]) / (1.0 - float(ctx.constants["RETURN_FRACTION"]))

    return {
        "disc_surface_brightness": brightness,
        "disc_light_temperature": temperature,
        "disc_luminosity": float(np.trapezoid(brightness * area, R)),
        "halpha_surface_brightness": halpha,
        "bulge_luminosity": bulge_formed * float(bulge_light[0]),
        "bulge_light_temperature": float(correlated_temperature(bulge_colour)[0]),
    }


LIGHT = IMPLEMENTATIONS.register(
    Stage(
        id="light",
        slot="light",
        checkpoint=3,
        about=(
            "The disc's unresolved light: surface brightness and colour temperature from the formation "
            "history and the PARSEC isochrones. What the photometric view draws under the star sample."
        ),
        compute=compute,
        reads_constants=("RETURN_FRACTION", "HALPHA_PER_SFR"),
        requires=("stars_formed_history", "feh_history", "sfr_surface_density", "bulge_stellar_mass", "bulge_scale_radius"),
        publishes=(
            SURFACE_BRIGHTNESS, LIGHT_TEMPERATURE, DISC_LUMINOSITY,
            HALPHA_SURFACE_BRIGHTNESS, BULGE_LUMINOSITY, BULGE_LIGHT_TEMPERATURE,
        ),
    )
)
