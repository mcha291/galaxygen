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
formed of a Kroupa population at its metallicity, integrated along the isochrone
once and tabulated — averaged since S28 over the ages the step's stars span (the
present being the end of the last step), where until then it was read at the step's
centre and the youngest step's whole mass shone as a 4 Myr population: the disc's
light moved by 5.5% between N_t = 2000 and 8000 and now by 0.05% (``photometry.population_over``). The
colour is the same sum carried in linear sRGB and reduced to a correlated colour
temperature.

**What it does not include, recorded rather than hidden.**

- *Metallicity at present radius.* Each step is read at ``feh_history`` where its
  stars are now, not where they were born; migration mixes that by up to a few
  kiloparsecs and a quarter-dex of [Fe/H] moves the light by a few per cent.
- *The classical bulge's population.* It is a scalar mass with no history, so its
  light is an old population at the inner disc's abundance: a stated proxy.
- *Dust.* The light is emitted, not observed. ``dust_extinction_v`` is published by
  the ISM stage and is the viewer's to subtract (RENDER_PLAN R4).
- *Ages past 12.6 Gyr read at 12.6 Gyr*, and [Fe/H] for [M/H], as for the catalogue.

**The bands (S28, BUILD_II Phase 3).** The same sum carried in each of the table's eight
bands, U B V R I J H K: every step's mass formed times a Kroupa population's
Σ 10^(−0.4 M_band) per unit mass formed, integrated along the isochrone once
(``photometry.population_light``). The galaxy's magnitudes are therefore the whole
history's, disc and bulge, and not the 2 × 10⁴-star sample's. Intrinsic, like the
bolometric light: what the observed Milky Way's magnitudes include is the acceptance
rows' question (spec rows 25–28), and the answer is in their notes.

**The ionizing budget.** Today's star formation rate at each radius times the
hydrogen-ionizing photons a steady population emits per unit rate
(``photometry.ionizing_yield``: Q per unit mass formed, integrated over the isochrone
ages, the first 4 Myr read at the youngest). Q is the tabulated calibration's
(``massive_stars``), ruling (a) of S28.
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
from galaxy.stages.photometry import (
    BANDS,
    band_flux_at,
    correlated_temperature,
    ionizing_yield,
    population_at,
    population_over,
)
from galaxy.stages.sfh import fit_scale_length

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


def _magnitude_decl(band: str) -> FieldDecl:
    return FieldDecl(
        name=f"absolute_magnitude_{band.lower()}", label=f"Absolute magnitude M_{band}", unit="mag",
        kind=Kind.SCALAR, meaningful_zero=False,
        about=(
            f"The whole galaxy's {band}-band absolute magnitude, Vega system: disc and bulge, every "
            "population the disc has formed and still has alive, each step's mass formed times a Kroupa "
            f"population's {band}-band light per unit mass formed along the PARSEC isochrone. Intrinsic: "
            "no dust, seen from nowhere in particular."
        ),
    )


BAND_MAGNITUDES = tuple(_magnitude_decl(b) for b in BANDS)

COLOUR_B_V = FieldDecl(
    name="colour_b_v", label="B − V colour", unit="mag", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "M_B − M_V of the whole galaxy, intrinsic. A colour of the summed light, not of any star in it, "
        "so it is the young populations' blue against the giants' red, weighted by how much of each the "
        "history made."
    ),
)

MASS_TO_LIGHT_V = FieldDecl(
    name="mass_to_light_v", label="V-band mass-to-light ratio Υ_V", unit="Msun/Lsun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "The galaxy's stellar mass — the mass locked in stars, living and dead — over its V-band "
        "luminosity in solar V units (the Sun's V magnitude from Willmer 2018). Intrinsic light, so "
        "it is the ratio a dust-free galaxy would show."
    ),
)

BOLOMETRIC_CORRECTION_V = FieldDecl(
    name="bolometric_correction_v", label="Bolometric correction BC_V", unit="mag", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "M_bol − M_V of the whole galaxy, M_bol integrated from the table's bolometric magnitudes the "
        "way each band is. It is the number that turns the band sums back into the bolometric light "
        "disc_luminosity and bulge_luminosity carry, and a test asserts that it does."
    ),
)

SURFACE_BRIGHTNESS_V = FieldDecl(
    name="disc_surface_brightness_v", label="Disc V-band surface brightness Σ_V(R)", unit="Lsun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "V-band light per square parsec, in solar V luminosities (the Sun's own V-band light, not its "
        "bolometric), from the same sum as disc_surface_brightness. Intrinsic."
    ),
)

PHOTOMETRIC_SCALE_LENGTH = FieldDecl(
    name="photometric_scale_length", label="V-band scale length", unit="kpc", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "Exponential scale length fitted to Σ_V(R) over the same window as the stellar one (1 kpc to "
        "three λ_d scale lengths), so the two differ only by how the light per unit mass changes "
        "with radius."
    ),
)

IONIZING_PHOTON_RATE = FieldDecl(
    name="ionizing_photon_rate", label="Hydrogen-ionizing photon rate Σ_Q(R)", unit="1/s/kpc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about=(
        "Photons above 13.6 eV emitted per second per square kiloparsec by the young stars: today's "
        "sfr_surface_density times what a population formed at a steady rate emits per unit rate — "
        "Q(L, T_eff) from a model-atmosphere calibration (Sternberg, Hoffmann & Pauldrach 2003) summed "
        "over the IMF along every isochrone and over age. The table cannot see stars heavier than its "
        "youngest isochrone reaches (64 M☉ at 4 Myr), and by an estimate they would emit about as "
        "much again, so this is a lower limit by up to a factor of two. Everything nebular reads it."
    ),
)

IONIZING_PHOTON_RATE_TOTAL = FieldDecl(
    name="ionizing_photon_rate_total", label="Ionizing photon rate Q(H⁰)", unit="1/s", kind=Kind.SCALAR,
    meaningful_zero=True,
    about="Σ_Q integrated over the disc, 2πR dR: the galaxy's hydrogen-ionizing photons per second.",
)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    locked = np.asarray(ctx.fields["stars_formed_history"], dtype=float)  # M☉/pc², (R, t)
    formed = locked / (1.0 - float(ctx.constants["RETURN_FRACTION"]))
    age = t[-1] - t  # Gyr, per step: the bulge's clock, read at a step's centre as before S28
    # Each step's stars span the ages of its whole interval, the present being the end of the
    # last one (S28): the population's light averaged over those ages, not read at one of them.
    dt = float(ctx.grid.spec.t_max) / float(ctx.grid.spec.n_t)
    youngest = float(ctx.grid.spec.t_max) - (t + 0.5 * dt)
    feh = ctx.fields["feh_history"]
    step = population_over(np.broadcast_to(youngest, formed.shape), np.broadcast_to(youngest + dt, formed.shape), feh)

    brightness = (formed * step["light"]).sum(axis=1)  # L☉/pc²
    rgb = np.stack([(formed * step[c]).sum(axis=1) for c in ("red", "green", "blue")], axis=-1)
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

    # The bands: the same sum in each, disc then bulge, as a sum of 10^(-0.4 M) and then a magnitude.
    m_sun_v = float(ctx.constants["SOLAR_ABSOLUTE_MAGNITUDE_V"])
    magnitude = {}
    surface_v = np.zeros_like(brightness)
    every = (*BANDS, "mbol")
    bulge_bands = band_flux_at(np.array([age[0]]), np.array([feh_bulge]), every)
    for band in every:
        per_area = (formed * step[band]).sum(axis=1)  # per pc²
        disc_flux = float(np.trapezoid(per_area * area, R))
        bulge_flux = bulge_formed * float(bulge_bands[band][0])
        magnitude[band] = -2.5 * float(np.log10(disc_flux + bulge_flux))
        if band == "V":
            surface_v = per_area * 10.0 ** (0.4 * m_sun_v)  # solar V luminosities per pc²
    luminosity_v = 10.0 ** (-0.4 * (magnitude["V"] - m_sun_v))
    R_d = float(ctx.fields["disc_scale_length_spin"])

    # The ionizing photons: today's rate times what a steady population emits per unit rate,
    # at the [Fe/H] of today's gas.
    feh_now = np.asarray(feh, dtype=float)[:, -1]
    ionizing = np.asarray(ctx.fields["sfr_surface_density"], dtype=float) * ionizing_yield(feh_now)  # s⁻¹ kpc⁻²

    return {
        **{f"absolute_magnitude_{b.lower()}": magnitude[b] for b in BANDS},
        "colour_b_v": magnitude["B"] - magnitude["V"],
        "mass_to_light_v": float(ctx.fields["stellar_mass_total"]) / luminosity_v,
        "bolometric_correction_v": magnitude["mbol"] - magnitude["V"],
        "disc_surface_brightness_v": surface_v,
        "photometric_scale_length": fit_scale_length(surface_v, R, 1.0, 3.0 * R_d),
        "ionizing_photon_rate": ionizing,
        "ionizing_photon_rate_total": float(np.trapezoid(ionizing * 2.0 * np.pi * R, R)),
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
        checkpoint=4,
        about=(
            "The disc's unresolved light: surface brightness and colour temperature from the formation "
            "history and the PARSEC isochrones, the galaxy's magnitudes in eight bands, its colour and "
            "mass-to-light ratio, and the young stars' hydrogen-ionizing photons. What the photometric "
            "view draws under the star sample."
        ),
        compute=compute,
        reads_constants=("RETURN_FRACTION", "HALPHA_PER_SFR", "SOLAR_ABSOLUTE_MAGNITUDE_V"),
        requires=(
            "stars_formed_history", "feh_history", "sfr_surface_density", "bulge_stellar_mass", "bulge_scale_radius",
            "stellar_mass_total", "disc_scale_length_spin",
        ),
        publishes=(
            SURFACE_BRIGHTNESS, LIGHT_TEMPERATURE, DISC_LUMINOSITY,
            HALPHA_SURFACE_BRIGHTNESS, BULGE_LUMINOSITY, BULGE_LIGHT_TEMPERATURE,
            *BAND_MAGNITUDES, COLOUR_B_V, MASS_TO_LIGHT_V, BOLOMETRIC_CORRECTION_V,
            SURFACE_BRIGHTNESS_V, PHOTOMETRIC_SCALE_LENGTH, IONIZING_PHOTON_RATE, IONIZING_PHOTON_RATE_TOTAL,
        ),
    )
)
