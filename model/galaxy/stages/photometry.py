"""Per-star luminosity and effective temperature from PARSEC isochrones (RENDER_PLAN M2).

A photometric render is radiance, not a field painted with a ramp, so what a star
emits is published by the model and the viewer only composites it (rules A9, D5).
The catalogue already carries each star's initial mass, age and [Fe/H]; this
module maps them onto the isochrone table committed at
``galaxy/data/parsec_isochrones.npz`` (``tools/fetch_parsec.py``; attribution in the
README): 396 isochrones, 36 ages at log age 6.6–10.1 in steps of 0.1 and 11
metallicities at [M/H] −2.19 to +0.30 in steps of 0.25, each carrying initial
mass, log L and log T_eff.

**The lookup.** Nearest metallicity; linear in log age between the two isochrones
that bracket the star; linear in initial mass along each. A star heavier than the
most massive one still alive at its age — the heaviest mass the two isochrones
reach, interpolated the same way — has died, and has neither a luminosity nor a
temperature: NaN rather than a remnant's value the table does not carry (rule B9).
Where it is alive at the younger isochrone and past the end of the older one, it
is in a phase the older one no longer has, and the younger one's values stand.

**What does not hold, recorded rather than hidden.**

- *Ages past 12.6 Gyr are read at 12.6 Gyr* (log age 10.1), where the table stops;
  CMD's own grid ends at 10.13. Until log age 10.1 was appended the table stopped at
  10 Gyr, past which a quarter of the default catalogue lies.
- *[Fe/H] stands in for [M/H]*, so α-enhanced stars are read slightly too metal-poor.
- *Metallicity is the nearest of eleven*, a quarter-dex grid; the 0.2% of stars below
  −2.19 are read at −2.19.
- *Masses below an isochrone's lightest (0.09–0.10 M☉) are read at its lightest*: the
  Kroupa sample starts at 0.08 M☉.
- *Stars heavier than the youngest isochrone reaches* (64 M☉ at 4 Myr) are NaN.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path

import numpy as np

TABLE = Path(__file__).resolve().parents[1] / "data" / "parsec_isochrones.npz"


@dataclass(frozen=True)
class Isochrones:
    log_ages: np.ndarray  # (n_age,), increasing, evenly spaced
    mhs: np.ndarray  # (n_mh,), increasing
    # Per (age, metallicity): initial mass (made non-decreasing), log L, log T_eff.
    tracks: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]

    def track(self, age: int, mh: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.tracks[(age, mh)]


@functools.cache
def isochrones() -> Isochrones:
    # Read each array out once: indexing the archive decompresses on every access, and in the
    # loop below that cost 4 s where one read costs a twentieth of it.
    with np.load(TABLE) as archive:
        raw = {k: archive[k] for k in ("mh", "log_age", "offset", "length", "mass", "log_l", "log_teff")}
    log_ages = np.unique(np.round(raw["log_age"].astype(float), 2))
    mhs = np.unique(np.round(raw["mh"].astype(float), 2))
    tracks = {}
    for k in range(raw["offset"].size):
        o, n = int(raw["offset"][k]), int(raw["length"][k])
        age = int(np.searchsorted(log_ages, round(float(raw["log_age"][k]), 2)))
        mh = int(np.searchsorted(mhs, round(float(raw["mh"][k]), 2)))
        # CMD ends an isochrone on a row at log L = -9.999 with a heavier mass: the
        # boundary of what the tracks follow, not a star. Kept, it would stretch every
        # isochrone's heaviest living mass and interpolate a dying giant toward a dwarf.
        real = raw["log_l"][o : o + n] > -9.0
        # Late phases repeat an initial mass to float32 precision, and a few step back by
        # one ulp; interpolation needs it non-decreasing, and the running maximum is the
        # smallest change that gives it.
        mass = np.maximum.accumulate(raw["mass"][o : o + n][real].astype(float))
        tracks[(age, mh)] = (
            mass, raw["log_l"][o : o + n][real].astype(float), raw["log_teff"][o : o + n][real].astype(float),
        )
    return Isochrones(log_ages, mhs, tracks)


def _along(track: tuple[np.ndarray, np.ndarray, np.ndarray], mass: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    m, log_l, log_teff = track
    at = np.clip(mass, m[0], m[-1])
    return np.interp(at, m, log_l), np.interp(at, m, log_teff)


def lookup(mass: np.ndarray, age_gyr: np.ndarray, feh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Luminosity (L☉) and effective temperature (K) per star; NaN for a star no longer alive."""
    tab = isochrones()
    mass = np.asarray(mass, dtype=float)
    luminosity = np.full(mass.shape, np.nan)
    temperature = np.full(mass.shape, np.nan)
    if mass.size == 0:
        return luminosity, temperature

    step = tab.log_ages[1] - tab.log_ages[0]
    log_age = np.log10(np.maximum(np.asarray(age_gyr, dtype=float), 1e-9) * 1e9)
    position = (np.clip(log_age, tab.log_ages[0], tab.log_ages[-1]) - tab.log_ages[0]) / step
    younger = np.clip(np.floor(position).astype(int), 0, tab.log_ages.size - 2)
    frac = np.clip(position - younger, 0.0, 1.0)
    mh = np.abs(np.asarray(feh, dtype=float)[:, None] - tab.mhs[None, :]).argmin(axis=1)

    group = younger * tab.mhs.size + mh
    for g in np.unique(group):
        sel = np.flatnonzero(group == g)
        a, z = divmod(int(g), tab.mhs.size)
        near, far = tab.track(a, z), tab.track(a + 1, z)
        m, f = mass[sel], frac[sel]
        l0, t0 = _along(near, m)
        l1, t1 = _along(far, m)
        # The heaviest star alive at the star's own age, between the two isochrones' ends.
        alive = m <= (1.0 - f) * near[0][-1] + f * far[0][-1]
        blend = np.where(m <= far[0][-1], f, 0.0)
        luminosity[sel] = np.where(alive, 10.0 ** ((1.0 - blend) * l0 + blend * l1), np.nan)
        temperature[sel] = np.where(alive, 10.0 ** ((1.0 - blend) * t0 + blend * t1), np.nan)
    return luminosity, temperature


# --- the unresolved population (RENDER_PLAN R3) ----------------------------------

# Temperatures the population colours are tabulated at, log-spaced past both ends of the
# blackbody cmap so a cool M dwarf and a hot O star each land on a real sample.
_CCT_GRID = np.geomspace(1500.0, 60000.0, 384)
_IMF_MASSES = np.geomspace(0.08, 150.0, 1500)


@functools.cache
def _blackbody_table() -> np.ndarray:
    from galaxy.core.cmaps import blackbody_rgb

    return np.array([blackbody_rgb(float(k)) for k in _CCT_GRID])  # (n_T, 3), linear, max channel 1


def blackbody_linear(kelvin: np.ndarray) -> np.ndarray:
    """Linear sRGB chromaticity per temperature, interpolated in log T on a computed table."""
    table = _blackbody_table()
    x = np.log(np.clip(np.asarray(kelvin, dtype=float), _CCT_GRID[0], _CCT_GRID[-1]))
    grid = np.log(_CCT_GRID)
    return np.stack([np.interp(x, grid, table[:, c]) for c in range(3)], axis=-1)


def correlated_temperature(rgb: np.ndarray) -> np.ndarray:
    """The blackbody temperature whose chromaticity is nearest a summed linear colour.

    A population's light is a sum of blackbodies and so lies near the Planckian locus
    rather than on it; this is its correlated colour temperature, the standard reduction
    of a near-Planckian colour to one number, taken here as the nearest tabulated
    blackbody after both are scaled to their brightest channel. NaN where there is no light.
    """
    rgb = np.asarray(rgb, dtype=float)
    top = rgb.max(axis=-1, keepdims=True)
    unit = np.where(top > 0.0, rgb / np.where(top > 0.0, top, 1.0), np.nan)
    table = _blackbody_table()
    distance = ((unit[..., None, :] - table) ** 2).sum(axis=-1)
    return np.where(np.isfinite(unit[..., 0]), _CCT_GRID[np.nanargmin(np.nan_to_num(distance, nan=np.inf), axis=-1)], np.nan)


@dataclass(frozen=True)
class PopulationLight:
    """Per isochrone: light today per solar mass *formed*, and that light's linear colour."""

    light_per_mass: np.ndarray  # (n_age, n_mh), L☉ per M☉ of initial mass
    colour: np.ndarray  # (n_age, n_mh, 3), luminosity-weighted linear chromaticity


@functools.cache
def population_light() -> PopulationLight:
    """Integrate a Kroupa population along every isochrone.

    Light per unit mass formed is ∫ φ(m) L(m) dm over the stars still alive, divided by
    ∫ φ(m) m dm over the whole IMF — the dead count toward the mass formed and add no
    light. The colour is the same integral of L(m) times the blackbody chromaticity of
    T_eff(m). Both are integrated on a fixed log-spaced mass grid, which puts ~150
    samples per decade of mass and resolves the giant branch, where most of an old
    population's light is, to a hundredth of a solar mass near the turnoff.
    """
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE

    tab = isochrones()
    m = _IMF_MASSES
    phi = np.where(m < IMF_BREAK, m**IMF_LOW_SLOPE, IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE) * m**IMF_HIGH_SLOPE)
    mass_formed = np.trapezoid(phi * m, m)
    light = np.zeros((tab.log_ages.size, tab.mhs.size))
    colour = np.zeros((tab.log_ages.size, tab.mhs.size, 3))
    for (a, z), track in tab.tracks.items():
        alive = m <= track[0][-1]
        log_l, log_teff = _along(track, m)
        L = np.where(alive, 10.0**log_l, 0.0)
        light[a, z] = np.trapezoid(phi * L, m) / mass_formed
        weights = phi * L
        colour[a, z] = np.trapezoid(weights[:, None] * blackbody_linear(10.0**log_teff), m, axis=0) / max(
            np.trapezoid(weights, m), 1e-300
        )
    return PopulationLight(light, colour)


def population_at(age_gyr: np.ndarray, feh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Light per mass formed and its linear colour for populations of these ages and [Fe/H].

    The same reading as :func:`lookup`: nearest metallicity, linear in log age, ages
    clamped to the table's span.
    """
    tab = isochrones()
    pop = population_light()
    step = tab.log_ages[1] - tab.log_ages[0]
    log_age = np.log10(np.maximum(np.asarray(age_gyr, dtype=float), 1e-9) * 1e9)
    position = (np.clip(log_age, tab.log_ages[0], tab.log_ages[-1]) - tab.log_ages[0]) / step
    younger = np.clip(np.floor(position).astype(int), 0, tab.log_ages.size - 2)
    frac = np.clip(position - younger, 0.0, 1.0)
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=tab.mhs[0], neginf=tab.mhs[0], posinf=tab.mhs[-1])
    mh = np.abs(feh[..., None] - tab.mhs).argmin(axis=-1)
    light = (1.0 - frac) * pop.light_per_mass[younger, mh] + frac * pop.light_per_mass[younger + 1, mh]
    colour = (1.0 - frac)[..., None] * pop.colour[younger, mh] + frac[..., None] * pop.colour[younger + 1, mh]
    return light, colour