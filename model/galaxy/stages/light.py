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
- *The classical bulge.* It is a scalar mass with no history, so it has no age and
  no light here; the catalogue does not draw it either.
- *Dust.* The light is emitted, not observed. ``dust_extinction_v`` is published by
  the ISM stage and is the viewer's to subtract (RENDER_PLAN R4).
- *Ages past 10 Gyr read at 10 Gyr*, and [Fe/H] for [M/H], as for the catalogue.
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
    return {
        "disc_surface_brightness": brightness,
        "disc_light_temperature": temperature,
        "disc_luminosity": float(np.trapezoid(brightness * area, R)),
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
        reads_constants=("RETURN_FRACTION",),
        requires=("stars_formed_history", "feh_history"),
        publishes=(SURFACE_BRIGHTNESS, LIGHT_TEMPERATURE, DISC_LUMINOSITY),
    )
)
