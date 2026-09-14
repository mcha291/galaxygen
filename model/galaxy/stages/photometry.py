"""Per-star luminosity and effective temperature from PARSEC isochrones (RENDER_PLAN M2).

A photometric render is radiance, not a field painted with a ramp, so what a star
emits is published by the model and the viewer only composites it (rules A9, D5).
The catalogue already carries each star's initial mass, age and [Fe/H]; this
module maps them onto the isochrone table committed at
``galaxy/data/parsec_isochrones.npz`` (``tools/fetch_parsec.py``; attribution in the
README): 385 isochrones, 35 ages at log age 6.6–10.0 in steps of 0.1 and 11
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

- *Ages past 10 Gyr are read at 10 Gyr.* The table stops there and a quarter of the
  default catalogue is older [verified at S23 against the simple model's catalogue:
  25.3%]. Their turnoff is placed at ~1.05 M☉ rather than ~0.9 M☉.
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
    raw = np.load(TABLE)
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
