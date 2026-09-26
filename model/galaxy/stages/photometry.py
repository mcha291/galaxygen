"""Per-star luminosity and effective temperature from PARSEC isochrones (RENDER_PLAN M2).

A photometric render is radiance, not a field painted with a ramp, so what a star
emits is published by the model and the viewer only composites it (rules A9, D5).
The catalogue already carries each star's initial mass, age and [Fe/H]; this
module maps them onto the isochrone table committed at
``galaxy/data/parsec_isochrones.npz`` (``tools/fetch_parsec.py``; attribution in the
README): 396 isochrones, 36 ages at log age 6.6–10.1 in steps of 0.1 and 11
metallicities at [M/H] −2.19 to +0.30 in steps of 0.25, each carrying initial
mass, log L and log T_eff — and since S28 (BUILD_II Phase 3) the present mass, the
phase label, the bolometric magnitude and the absolute magnitudes in U B V R I J H K
(Vega; CMD's UBVRIJHK system, "Maiz-Apellaniz 2006 + Bessell 1990", with the YBC
bolometric corrections), all of which CMD returned from the start and the
conversion dropped until then. Regenerated at S28 by the same request: mass, log L
and log T_eff came back bit for bit what they were.

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


BANDS: tuple[str, ...] = ("U", "B", "V", "R", "I", "J", "H", "K")  # the table's absolute magnitudes, Vega
# The columns each isochrone carries beside (mass, log L, log T_eff), in this order: the eight
# band magnitudes, the bolometric magnitude CMD computes from log L, the present mass (after the
# tracks' own mass loss) and PARSEC's evolutionary-phase label.
EXTRA: tuple[str, ...] = (*BANDS, "mbol", "mass_now", "label")


@dataclass(frozen=True)
class Isochrones:
    log_ages: np.ndarray  # (n_age,), increasing, evenly spaced
    mhs: np.ndarray  # (n_mh,), increasing
    # Per (age, metallicity): initial mass (made non-decreasing), log L, log T_eff.
    tracks: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray]]
    # Per (age, metallicity): the EXTRA columns at the same points, (n_points, len(EXTRA)).
    extra: dict[tuple[int, int], np.ndarray]

    def track(self, age: int, mh: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.tracks[(age, mh)]


@functools.cache
def isochrones() -> Isochrones:
    # Read each array out once: indexing the archive decompresses on every access, and in the
    # loop below that cost 4 s where one read costs a twentieth of it.
    with np.load(TABLE) as archive:
        raw = {
            k: archive[k]
            for k in ("mh", "log_age", "offset", "length", "mass", "log_l", "log_teff", "mass_now", "label",
                      "mag_mmag_delta", "mbol_mmag_delta")
        }
        if tuple(str(b) for b in archive["bands"]) != BANDS:
            raise ValueError(f"{TABLE.name}: bands {archive['bands']} are not {BANDS}")
    # The magnitudes are stored as differenced thousandths (tools/fetch_parsec.py): undo it.
    mags = np.cumsum(raw["mag_mmag_delta"].astype(np.int64), axis=0) / 1000.0
    mbol = np.cumsum(raw["mbol_mmag_delta"].astype(np.int64)) / 1000.0
    columns = np.column_stack([mags, mbol, raw["mass_now"].astype(float), raw["label"].astype(float)])
    log_ages = np.unique(np.round(raw["log_age"].astype(float), 2))
    mhs = np.unique(np.round(raw["mh"].astype(float), 2))
    tracks = {}
    extra = {}
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
        extra[(age, mh)] = columns[o : o + n][real]
    return Isochrones(log_ages, mhs, tracks, extra)


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


def _nearest(grid: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Index of the point of a non-decreasing ``grid`` nearest each ``x``."""
    right = np.clip(np.searchsorted(grid, x), 1, grid.size - 1) if grid.size > 1 else np.zeros(x.shape, dtype=int)
    if grid.size == 1:
        return right
    left = right - 1
    return np.where(np.abs(x - grid[left]) <= np.abs(grid[right] - x), left, right)


def lookup_columns(mass: np.ndarray, age_gyr: np.ndarray, feh: np.ndarray, names: tuple[str, ...]) -> dict[str, np.ndarray]:
    """The table's other columns per star (``EXTRA``: band magnitudes, M_bol, present mass, phase).

    The same reading as :func:`lookup` — nearest metallicity, linear in log age between the
    bracketing isochrones, linear in initial mass along each, the older one dropped where the
    star has outlived it — so a star's V magnitude and its luminosity belong to one point of
    the table. The phase label is a category and is not interpolated: it is the label of the
    nearest tabulated point on whichever isochrone the star's age is nearer. NaN, and phase
    −1, for a star no longer alive (rule B9).
    """
    tab = isochrones()
    index = [EXTRA.index(n) for n in names]
    mass = np.asarray(mass, dtype=float)
    out = {n: np.full(mass.shape, np.nan) for n in names}
    if mass.size == 0:
        return out

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
        near, far = tab.track(a, z)[0], tab.track(a + 1, z)[0]
        cols_near, cols_far = tab.extra[(a, z)], tab.extra[(a + 1, z)]
        m, f = mass[sel], frac[sel]
        alive = m <= (1.0 - f) * near[-1] + f * far[-1]
        blend = np.where(m <= far[-1], f, 0.0)
        at_near, at_far = np.clip(m, near[0], near[-1]), np.clip(m, far[0], far[-1])
        for name, c in zip(names, index):
            if name == "label":
                use_far = blend >= 0.5
                value = np.where(use_far, cols_far[_nearest(far, at_far), c], cols_near[_nearest(near, at_near), c])
                out[name][sel] = np.where(alive, value, -1.0)
            else:
                v0 = np.interp(at_near, near, cols_near[:, c])
                v1 = np.interp(at_far, far, cols_far[:, c])
                out[name][sel] = np.where(alive, (1.0 - blend) * v0 + blend * v1, np.nan)
    return out


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
    """Per isochrone: light today per solar mass *formed*, and that light's linear colour.

    Since S28 also the same integral in every band of the table, the bolometric magnitude's
    (the check that the bands and log L belong to the same stars), and the hydrogen-ionizing
    photon rate (``massive_stars.ionizing_photons`` at each point's L and T_eff).
    """

    light_per_mass: np.ndarray  # (n_age, n_mh), L☉ per M☉ of initial mass
    colour: np.ndarray  # (n_age, n_mh, 3), luminosity-weighted linear chromaticity
    band_flux: np.ndarray  # (n_age, n_mh, len(BANDS)), Σ 10^(−0.4 M_band) per M☉ formed
    bolometric_flux: np.ndarray  # (n_age, n_mh), Σ 10^(−0.4 M_bol) per M☉ formed, from CMD's M_bol column
    ionizing_per_mass: np.ndarray  # (n_age, n_mh), photons/s per M☉ formed


def imf_weights(m: np.ndarray) -> np.ndarray:
    """The Kroupa dN/dm, unnormalised, at masses ``m`` — the catalogue's IMF (``systems.py``)."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE

    return np.where(m < IMF_BREAK, m**IMF_LOW_SLOPE, IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE) * m**IMF_HIGH_SLOPE)


@functools.cache
def population_light() -> PopulationLight:
    """Integrate a Kroupa population along every isochrone.

    Light per unit mass formed is ∫ φ(m) L(m) dm over the stars still alive, divided by
    ∫ φ(m) m dm over the whole IMF — the dead count toward the mass formed and add no
    light. The colour is the same integral of L(m) times the blackbody chromaticity of
    T_eff(m). Both are integrated on a fixed log-spaced mass grid, which puts ~150
    samples per decade of mass and resolves the giant branch, where most of an old
    population's light is, to a hundredth of a solar mass near the turnoff.

    A band's light is the same integral of 10^(−0.4 M_band(m)), each point's absolute
    magnitude read along the isochrone exactly as log L is, so a population's magnitude
    is −2.5 log₁₀ of it times the mass formed; the ionizing rate is the same integral of
    Q(L(m), T_eff(m)).
    """
    from galaxy.stages.massive_stars import ionizing_photons

    tab = isochrones()
    m = _IMF_MASSES
    phi = imf_weights(m)
    mass_formed = np.trapezoid(phi * m, m)
    shape = (tab.log_ages.size, tab.mhs.size)
    light = np.zeros(shape)
    colour = np.zeros((*shape, 3))
    bands = np.zeros((*shape, len(BANDS)))
    bolometric = np.zeros(shape)
    ionizing = np.zeros(shape)
    columns = [EXTRA.index(b) for b in BANDS] + [EXTRA.index("mbol")]
    for (a, z), track in tab.tracks.items():
        alive = m <= track[0][-1]
        log_l, log_teff = _along(track, m)
        L = np.where(alive, 10.0**log_l, 0.0)
        light[a, z] = np.trapezoid(phi * L, m) / mass_formed
        weights = phi * L
        colour[a, z] = np.trapezoid(weights[:, None] * blackbody_linear(10.0**log_teff), m, axis=0) / max(
            np.trapezoid(weights, m), 1e-300
        )
        # np.interp for every column at once: one search along the track, then a weighted gather.
        at = np.clip(m[alive], track[0][0], track[0][-1])
        right = np.clip(np.searchsorted(track[0], at, side="right"), 1, max(track[0].size - 1, 1))
        left = right - 1
        span = track[0][right] - track[0][left]
        w = np.where(span > 0.0, (at - track[0][left]) / np.where(span > 0.0, span, 1.0), 0.0)[:, None]
        cols = tab.extra[(a, z)][:, columns]
        flux = np.zeros((m.size, len(columns)))
        flux[alive] = 10.0 ** (-0.4 * (cols[left] * (1.0 - w) + cols[right] * w))
        integrated = np.trapezoid(phi[:, None] * flux, m, axis=0) / mass_formed
        bands[a, z], bolometric[a, z] = integrated[:-1], integrated[-1]
        Q = np.zeros(m.size)
        Q[alive] = np.nan_to_num(ionizing_photons(L[alive], 10.0 ** log_teff[alive]))
        ionizing[a, z] = np.trapezoid(phi * Q, m) / mass_formed
    return PopulationLight(light, colour, bands, bolometric, ionizing)


@functools.cache
def population_wind() -> np.ndarray:
    """(n_age, n_mh): the wind's mechanical power per unit mass *formed*, L☉ per M☉, along every isochrone.

    The integral :func:`population_light` takes of Q, of ``massive_stars.wind_luminosity`` instead: each
    living point's L, T_eff and present mass read along the track as the bands are, at Z/Z☉ = 10^[M/H]
    of the isochrone's own metallicity; zero where the recipe says nothing (outside 12.5–50 kK). S33
    (BUILD_II Phase 11): a cluster's wind is its mass times this at its age, not a sum over a sample.
    """
    from galaxy.stages.massive_stars import wind_luminosity

    tab = isochrones()
    m = _IMF_MASSES
    phi = imf_weights(m)
    mass_formed = np.trapezoid(phi * m, m)
    out = np.zeros((tab.log_ages.size, tab.mhs.size))
    column = EXTRA.index("mass_now")
    for (a, z), track in tab.tracks.items():
        alive = m <= track[0][-1]
        log_l, log_teff = _along(track, m)
        at = np.clip(m[alive], track[0][0], track[0][-1])
        right = np.clip(np.searchsorted(track[0], at, side="right"), 1, max(track[0].size - 1, 1))
        left = right - 1
        span = track[0][right] - track[0][left]
        w = np.where(span > 0.0, (at - track[0][left]) / np.where(span > 0.0, span, 1.0), 0.0)
        present = tab.extra[(a, z)][:, column]
        mass_now = present[left] * (1.0 - w) + present[right] * w
        power = np.zeros(m.size)
        power[alive] = np.nan_to_num(wind_luminosity(
            10.0 ** log_l[alive], 10.0 ** log_teff[alive], mass_now, np.full(at.size, 10.0 ** tab.mhs[z])
        ))
        out[a, z] = np.trapezoid(phi * power, m) / mass_formed
    return out


def _blend(age_gyr: np.ndarray, feh: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(younger isochrone, fraction toward the older, metallicity index) — :func:`lookup`'s reading."""
    tab = isochrones()
    step = tab.log_ages[1] - tab.log_ages[0]
    log_age = np.log10(np.maximum(np.asarray(age_gyr, dtype=float), 1e-9) * 1e9)
    position = (np.clip(log_age, tab.log_ages[0], tab.log_ages[-1]) - tab.log_ages[0]) / step
    younger = np.clip(np.floor(position).astype(int), 0, tab.log_ages.size - 2)
    frac = np.clip(position - younger, 0.0, 1.0)
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=tab.mhs[0], neginf=tab.mhs[0], posinf=tab.mhs[-1])
    mh = np.abs(feh[..., None] - tab.mhs).argmin(axis=-1)
    return younger, frac, mh


def population_at(age_gyr: np.ndarray, feh: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Light per mass formed and its linear colour for populations of these ages and [Fe/H].

    The same reading as :func:`lookup`: nearest metallicity, linear in log age, ages
    clamped to the table's span.
    """
    pop = population_light()
    younger, frac, mh = _blend(age_gyr, feh)
    light = (1.0 - frac) * pop.light_per_mass[younger, mh] + frac * pop.light_per_mass[younger + 1, mh]
    colour = (1.0 - frac)[..., None] * pop.colour[younger, mh] + frac[..., None] * pop.colour[younger + 1, mh]
    return light, colour


def band_flux_at(age_gyr: np.ndarray, feh: np.ndarray, bands: tuple[str, ...]) -> dict[str, np.ndarray]:
    """Σ 10^(−0.4 M_band) per mass formed for populations of these ages and [Fe/H], per band
    (``"mbol"`` for the bolometric magnitude), read as :func:`population_at` reads the light."""
    pop = population_light()
    younger, frac, mh = _blend(age_gyr, feh)
    out = {}
    for band in bands:
        table = pop.bolometric_flux if band == "mbol" else pop.band_flux[..., BANDS.index(band)]
        out[band] = (1.0 - frac) * table[younger, mh] + frac * table[younger + 1, mh]
    return out


def per_mass_at(table: np.ndarray, age_gyr: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """A per-isochrone table ``(n_age, n_mh)`` read at single ages and [Fe/H], as :func:`population_at`
    reads the light: nearest metallicity, linear in log age, the first 4 Myr the youngest isochrone's.
    What one burst of star formation — a cluster — does per unit mass formed (S33)."""
    younger, frac, mh = _blend(age_gyr, feh)
    return (1.0 - frac) * table[younger, mh] + frac * table[younger + 1, mh]


# --- a formation step's stars span its whole interval (S28) --------------------------------------
#
# A step of the history forms its stars across dt, not at one instant, so its light is the
# population's light averaged over the ages its stars span. Reading it at one age instead - what
# ``light.py`` did until S28 - put the last step's whole mass at the youngest isochrone and
# made the disc's light depend on the time step: disc_luminosity read 8.77e10 at N_t = 400,
# 5.31e10 at 2000 and 5.02e10 at 8000, and B - V 0.514, 0.616, 0.626. The average is the
# difference of a cumulative integral over age, tabulated once per metallicity on a fine
# log-spaced age grid read exactly as :func:`population_at` reads the table (linear in log age,
# clamped to its span, so the first 4 Myr are the youngest isochrone's).

_FINE_AGES = np.concatenate([[0.0], np.geomspace(1e5, 2e10, 4000)])  # yr
STEP_QUANTITIES: tuple[str, ...] = ("light", "red", "green", "blue", *BANDS, "mbol", "ionizing")


def on_fine_ages(per_iso: np.ndarray) -> np.ndarray:
    """(n_fine, n_mh, k): a per-isochrone table ``(n_age, n_mh, k)`` read at every fine age, as
    :func:`population_at` reads the light (linear in log age, clamped to the table's span)."""
    younger, frac, _ = _blend(_FINE_AGES / 1e9, np.zeros(_FINE_AGES.shape))
    return (1.0 - frac)[:, None, None] * per_iso[younger] + frac[:, None, None] * per_iso[younger + 1]


def cumulative_over_age(f: np.ndarray) -> np.ndarray:
    """(n_mh, n_fine, k): ∫₀^τ f(τ') dτ', τ in yr, of a quantity already on the fine ages."""
    steps = np.diff(_FINE_AGES)[:, None, None] * 0.5 * (f[1:] + f[:-1])
    cumulative = np.concatenate([np.zeros((1, *f.shape[1:])), np.cumsum(steps, axis=0)])
    return np.ascontiguousarray(np.moveaxis(cumulative, 0, 1))


@functools.cache
def _age_integrals() -> np.ndarray:
    """(n_mh, n_fine, len(STEP_QUANTITIES)): ∫₀^τ f(τ') dτ' per unit mass formed, τ in yr."""
    pop = population_light()
    per_iso = np.concatenate([
        pop.light_per_mass[..., None],
        pop.light_per_mass[..., None] * pop.colour,
        pop.band_flux,
        pop.bolometric_flux[..., None],
        pop.ionizing_per_mass[..., None],
    ], axis=-1)  # (n_age, n_mh, k)
    return cumulative_over_age(on_fine_ages(per_iso))


def population_over(age_lo_gyr: np.ndarray, age_hi_gyr: np.ndarray, feh: np.ndarray) -> dict[str, np.ndarray]:
    """Each of ``STEP_QUANTITIES`` per unit mass formed, averaged over ages [lo, hi] (Gyr).

    ``age_lo_gyr`` and ``age_hi_gyr`` are one pair per step, shape ``(n_t,)``, and ``feh`` is
    ``(..., n_t)``: the averages are taken once per step and metallicity, then read per cell.
    ``light`` in L☉/M☉; ``red``/``green``/``blue`` the light times its linear colour; the bands
    and ``mbol`` as Σ 10^(−0.4 M) per M☉; ``ionizing`` in photons/s per M☉. Nearest metallicity,
    as everywhere in this module.
    """
    per_step = steps_over(_age_integrals(), age_lo_gyr, age_hi_gyr, feh)
    return {name: per_step[..., k] for k, name in enumerate(STEP_QUANTITIES)}


def steps_over(table: np.ndarray, age_lo_gyr: np.ndarray, age_hi_gyr: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """``(..., n_t, k)``: the difference of a cumulative table ``(n_mh, n_fine, k)`` over each
    step's ages [lo, hi] (Gyr) divided by its width in yr, read at each cell's nearest metallicity
    — :func:`population_over`'s reading, for any table built by :func:`cumulative_over_age`."""
    tab = isochrones()
    lo = np.clip(np.atleast_1d(np.asarray(age_lo_gyr, dtype=float)) * 1e9, 0.0, _FINE_AGES[-1])
    hi = np.clip(np.atleast_1d(np.asarray(age_hi_gyr, dtype=float)) * 1e9, 0.0, _FINE_AGES[-1])
    width = np.where(hi > lo, hi - lo, 1.0)

    def at(x: np.ndarray) -> np.ndarray:  # (n_mh, n_t, k): the cumulative integral at ages x
        i = np.clip(np.searchsorted(_FINE_AGES, x, side="right") - 1, 0, _FINE_AGES.size - 2)
        w = ((x - _FINE_AGES[i]) / (_FINE_AGES[i + 1] - _FINE_AGES[i]))[None, :, None]
        return table[:, i] * (1.0 - w) + table[:, i + 1] * w

    per_step = (at(hi) - at(lo)) / width[None, :, None]  # (n_mh, n_t, k)
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=tab.mhs[0], neginf=tab.mhs[0], posinf=tab.mhs[-1])
    # The nearest metallicity, as argmin |feh - mh| picks it (ties to the lower), by a search.
    mh = np.searchsorted(0.5 * (tab.mhs[1:] + tab.mhs[:-1]), feh, side="left")
    flat = mh * lo.size + np.arange(lo.size)
    return per_step.reshape(-1, per_step.shape[-1])[flat]


def ionizing_yield(feh: np.ndarray) -> np.ndarray:
    """Hydrogen-ionizing photons per second, per M☉/yr of steady star formation, at these [Fe/H].

    ∫ Q(τ) dτ over the population's age τ, per unit mass formed, in photons/s · yr / M☉ — the
    same age integral the steps are averaged with, the first 10^6.6 yr read at the youngest
    isochrone (the table starts at 4 Myr). Times a star formation rate held steady over the last
    few tens of Myr, it is the rate of ionizing photons the young stars emit.
    """
    tab = isochrones()
    total = _age_integrals()[:, -1, STEP_QUANTITIES.index("ionizing")]
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=tab.mhs[0], neginf=tab.mhs[0], posinf=tab.mhs[-1])
    return total[np.abs(feh[..., None] - tab.mhs).argmin(axis=-1)]
