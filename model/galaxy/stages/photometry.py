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
import math
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
class Passband:
    """One band's reference (pivot) wavelength, FWHM and Vega zero point, as the SVO Filter Profile
    Service lists them: what turns the table's Vega magnitudes into a spectrum (S38, BUILD_II V1)."""

    reference: float  # Å: λ_ref, the pivot wavelength, at which the zero point's f_λ is quoted
    fwhm: float  # Å
    zero_point: float  # erg/cm²/s/Å: Vega's mean f_λ through the band


# The eight bands' passbands (S38). CMD's photometric-system page names the table's system "UBVRIJHK
# (cf. Maiz-Apellaniz 2006 + Bessell 1990)" (quoted in fetch_parsec.py's form and this module's
# docstring); CMD's own pages could not be read at S38 (their TLS certificate fails verification), so
# which curve CMD uses per band is [inferred]: U B V R I as SVO's Generic/Bessell (Bessell 1990),
# J H K as its Generic/Bessell_JHKLM ("Bessell & Brett 1988 J/H/K filter"). The numbers are the SVO
# pages' own, λ_ref / FWHM / ZP (erg/cm²/s/Å), each cross-checked there as ZP(Jy) · c / λ_ref²
# [verified: http://svo2.cab.inta-csic.es/theory/fps/index.php?id=Generic/Bessell.U (and .B .V .R .I)
# and ?id=Generic/Bessell_JHKLM.J (and .H .K), read at S38]. The Vega spectrum SVO integrates is not
# necessarily the one YBC's Vega magnitudes are on; the difference is a zero-point term per band [inferred].
PASSBANDS: dict[str, Passband] = {
    "U": Passband(3584.78, 652.84, 3.96526e-9),
    "B": Passband(4371.07, 947.62, 6.13268e-9),
    "V": Passband(5477.70, 852.44, 3.62708e-9),
    "R": Passband(6498.09, 1567.06, 2.17037e-9),
    "I": Passband(8020.14, 1543.11, 1.12588e-9),
    "J": Passband(12303.17, 2065.62, 3.12398e-10),
    "H": Passband(16396.38, 2983.81, 1.13166e-10),
    "K": Passband(22027.46, 3959.11, 3.93276e-11),
}


def band_nu_l_nu(flux: np.ndarray, band: str) -> np.ndarray:
    """λL_λ at the band's reference wavelength, L☉, of a population whose Σ 10^(−0.4 M_band) is
    ``flux`` (absolute magnitudes: 10 pc): 4π (10 pc)² · f_λ,Vega · λ_ref · 10^(−0.4 M)."""
    from galaxy.stages.dust import CM_PER_PC
    from galaxy.stages.massive_stars import SOLAR_LUMINOSITY

    p = PASSBANDS[band]
    return np.asarray(flux, dtype=float) * (4.0 * np.pi * (10.0 * CM_PER_PC) ** 2 * p.zero_point * p.reference / SOLAR_LUMINOSITY)


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


def imf_weights(m: np.ndarray) -> np.ndarray:
    """The Kroupa dN/dm, unnormalised, at masses ``m`` — the catalogue's IMF (``systems.py``)."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE

    return np.where(m < IMF_BREAK, m**IMF_LOW_SLOPE, IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE) * m**IMF_HIGH_SLOPE)


# --- the quadrature: an isochrone as segments between its own points (S48 D202, S49 D204) ---------------
#
# One integral over a population for everything this module and the bright catalogue (``bright.py``) hold. Until
# S49 the field's tables were a trapezoid on 1 500 log-spaced masses, which puts one or two points on a red-giant
# branch a hundredth of a solar mass wide and on an AGB a thousandth wide, so its light per mass was off by up to a
# factor of seven either way, isochrone by isochrone (debt #126, D202). The isochrone's own points are dense where
# the evolved phases are, and they are what is integrated along now.


def imf_cumulative(m: np.ndarray) -> np.ndarray:
    """∫ φ dm from the IMF's lower end to ``m``, with φ :func:`imf_weights`' unnormalised Kroupa form, analytic."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE, IMF_MIN

    m = np.clip(np.asarray(m, dtype=float), IMF_MIN, None)
    p_lo, p_hi = IMF_LOW_SLOPE + 1.0, IMF_HIGH_SLOPE + 1.0
    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    below = (np.minimum(m, IMF_BREAK) ** p_lo - IMF_MIN**p_lo) / p_lo
    above = k_high * (np.maximum(m, IMF_BREAK) ** p_hi - IMF_BREAK**p_hi) / p_hi
    return below + above


def imf_number(lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """∫ φ dm over [lo, hi]: the IMF's number in each mass interval, unnormalised."""
    return imf_cumulative(hi) - imf_cumulative(lo)


@functools.cache
def imf_mass_formed() -> float:
    """∫ φ m dm over the whole IMF, analytic: what turns the unnormalised number into stars per M☉ formed."""
    from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE, IMF_MAX, IMF_MIN

    k_high = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)
    p_lo, p_hi = IMF_LOW_SLOPE + 2.0, IMF_HIGH_SLOPE + 2.0
    return float((IMF_BREAK**p_lo - IMF_MIN**p_lo) / p_lo + k_high * (IMF_MAX**p_hi - IMF_BREAK**p_hi) / p_hi)


@dataclass(frozen=True)
class Segments:
    """One isochrone as straight pieces between its consecutive living points.

    Each segment holds ``number`` stars per M☉ formed (the IMF's exact number in its mass interval), spread
    uniformly in its parameter s ∈ [0, 1] (and so in log L, which is linear in s); every other column is linear
    in s between its ends. The first segment runs from the IMF's lower end to the isochrone's first point at that
    point's values: the stars the table does not reach, read at its lightest. The stars heavier than the last
    point are dead: they count toward the mass formed (``imf_mass_formed``) and hold no segment.
    """

    number: np.ndarray  # (n,) stars per M☉ formed
    log_l: np.ndarray  # (n, 2) log10 L/L☉ at the two ends
    mass: np.ndarray  # (n, 2) initial mass, M☉
    log_teff: np.ndarray  # (n, 2)
    neg_mag: np.ndarray  # (n, 2, 8): −0.4 M_band at the ends, so 10^this is the band flux
    neg_mbol: np.ndarray  # (n, 2): −0.4 M_bol, CMD's own bolometric magnitude
    mass_now: np.ndarray  # (n, 2) present mass, after the tracks' mass loss
    label: np.ndarray  # (n, 2) PARSEC's phase label at the ends


@functools.cache
def segments(age: int, mh: int) -> Segments:
    """The segments of isochrone ``(age, mh)``: see :class:`Segments`."""
    from galaxy.stages.systems import IMF_MIN

    tab = isochrones()
    m, log_l, log_teff = tab.track(age, mh)
    cols = tab.extra[(age, mh)]
    mags = cols[:, [EXTRA.index(b) for b in BANDS]]
    mbol, now, label = (cols[:, EXTRA.index(c)] for c in ("mbol", "mass_now", "label"))
    # Prepend the IMF's lower end at the first point's values (a degenerate segment in L).
    m0 = np.concatenate([[min(IMF_MIN, m[0])], m])
    idx = np.concatenate([[0], np.arange(m.size)])
    lo, hi = idx[:-1], idx[1:]
    number = imf_number(m0[:-1], m0[1:]) / imf_mass_formed()

    def ends(v: np.ndarray) -> np.ndarray:
        return np.stack([v[lo], v[hi]], axis=1)

    return Segments(
        number=number,
        log_l=ends(log_l),
        mass=np.stack([m0[:-1], m0[1:]], axis=1),
        log_teff=ends(log_teff),
        neg_mag=ends(-0.4 * mags),
        neg_mbol=ends(-0.4 * mbol),
        mass_now=ends(now),
        label=ends(label),
    )


def log_linear_integral(g0: np.ndarray, g1: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """∫_a^b 10^(g0 + s (g1 − g0)) ds, exactly, for g linear in s; zero where b <= a."""
    d = (g1 - g0) * math.log(10.0)
    width = np.maximum(b - a, 0.0)
    start = 10.0 ** (g0 + a * (g1 - g0))
    x = d * width
    small = np.abs(x) < 1e-9
    factor = np.where(small, width * (1.0 + 0.5 * x), np.expm1(np.where(small, 0.0, x)) / np.where(small, 1.0, d))
    return start * factor


# Gauss-Legendre nodes per segment for what is not log-linear along it (the colour, the ionizing rate, the wind's
# power). S49 (D204), against 128 nodes over all 396 isochrones: the colour within 3.7e-5 and Q within 3.2e-6 of
# each isochrone's own; the light read on the same nodes is the exact integral to 4e-15. The wind is discontinuous
# along a segment (the recipe's two sides of the bistability jump, its 12.5-50 kK window), so it converges slower:
# against a 2 048-point midpoint rule, within 6.2e-3 per isochrone holding above 1e-3 of the peak, and 7.5e-4
# integrated over age, at [M/H] +0.05 (2e-4 and 1e-6 at -2.2 and -0.95).
SEGMENT_NODES = 16


@dataclass(frozen=True)
class Nodes:
    """Points inside every segment of an isochrone, and the stars per M☉ formed each stands for: the
    Gauss-Legendre rule on s ∈ [0, 1] times each segment's number. Σ ``weight`` · f(point) is ∫ f over the
    living stars, for any f of the columns read at the point."""

    weight: np.ndarray  # (n_seg, k) stars per M☉ formed
    log_l: np.ndarray  # (n_seg, k)
    log_teff: np.ndarray  # (n_seg, k)
    mass_now: np.ndarray  # (n_seg, k)


def nodes(seg: Segments, k: int = SEGMENT_NODES) -> Nodes:
    """The :class:`Nodes` of ``seg``, ``k`` per segment."""
    x, w = np.polynomial.legendre.leggauss(int(k))
    s, w = 0.5 * (x + 1.0), 0.5 * w

    def at(ends: np.ndarray) -> np.ndarray:
        return ends[:, :1] + s[None, :] * (ends[:, 1:] - ends[:, :1])

    return Nodes(seg.number[:, None] * w[None, :], at(seg.log_l), at(seg.log_teff), at(seg.mass_now))


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


@functools.cache
def population_light() -> PopulationLight:
    """Integrate a Kroupa population along every isochrone's own points (S49, D204; debt #126).

    Light per unit mass formed is ∫ φ(m) L(m) dm over the stars still alive, divided by ∫ φ(m) m dm
    over the whole IMF — the dead count toward the mass formed and add no light. The integral is taken
    along the isochrone's :func:`segments`: between consecutive living points the IMF's exact number in
    the mass interval, spread uniformly along the segment, with log L and each magnitude linear along it,
    so the light, each band's Σ 10^(−0.4 M_band) and CMD's bolometric magnitude's are integrated exactly
    (:func:`log_linear_integral`); the stars lighter than the first point are read at it. The points are
    dense where the evolved phases are. Until S49 the integral was a trapezoid on 1 500 log-spaced masses,
    which resolves the main sequence and puts one or two points on a red-giant branch a hundredth of a
    solar mass wide and on an AGB a thousandth wide: S48 measured its light per mass 0.55–7.1 times this
    one bolometric and 0.26–12 in K, isochrone by isochrone, the disc's light 6.7 % high (D202).

    What is not log-linear along a segment — the colour (the luminosity-weighted linear chromaticity of
    the blackbody at T_eff, ∫ L · chromaticity over ∫ L) and the ionizing rate (``massive_stars.
    ionizing_photons`` at L and T_eff) — is integrated on :func:`nodes` (``SEGMENT_NODES`` Gauss-Legendre
    points per segment). This is the same quadrature as the bright catalogue's luminosity function, so the
    two hold one budget (``bright.luminosity_function``'s totals are these to rounding).
    """
    from galaxy.stages.massive_stars import ionizing_photons

    tab = isochrones()
    shape = (tab.log_ages.size, tab.mhs.size)
    light = np.zeros(shape)
    colour = np.zeros((*shape, 3))
    bands = np.zeros((*shape, len(BANDS)))
    bolometric = np.zeros(shape)
    ionizing = np.zeros(shape)
    for (a, z) in tab.tracks:
        seg = segments(a, z)
        g0 = np.concatenate([seg.log_l[:, :1], seg.neg_mag[:, 0, :], seg.neg_mbol[:, :1]], axis=1)
        g1 = np.concatenate([seg.log_l[:, 1:], seg.neg_mag[:, 1, :], seg.neg_mbol[:, 1:]], axis=1)
        total = (seg.number[:, None] * log_linear_integral(g0, g1, 0.0, 1.0)).sum(axis=0)
        light[a, z], bands[a, z], bolometric[a, z] = total[0], total[1:-1], total[-1]
        at = nodes(seg)
        L, T = 10.0 ** at.log_l, 10.0 ** at.log_teff
        weights = at.weight * L
        colour[a, z] = np.einsum("sk,skc->c", weights, blackbody_linear(T)) / max(float(weights.sum()), 1e-300)
        ionizing[a, z] = float((at.weight * np.nan_to_num(ionizing_photons(L, T))).sum())
    return PopulationLight(light, colour, bands, bolometric, ionizing)


@functools.cache
def population_wind() -> np.ndarray:
    """(n_age, n_mh): the wind's mechanical power per unit mass *formed*, L☉ per M☉, along every isochrone.

    The integral :func:`population_light` takes of Q, of ``massive_stars.wind_luminosity`` instead: at each
    of the :func:`nodes` along the isochrone's segments, its L, T_eff and present mass read along the segment
    as the bands are, at Z/Z☉ = 10^[M/H] of the isochrone's own metallicity; zero where the recipe says
    nothing (outside 12.5–50 kK). S33 (BUILD_II Phase 11): a cluster's wind is its mass times this at its
    age, not a sum over a sample. On the segments since S49 (D204), as the light is: one quadrature.
    """
    from galaxy.stages.massive_stars import wind_luminosity

    tab = isochrones()
    out = np.zeros((tab.log_ages.size, tab.mhs.size))
    for (a, z) in tab.tracks:
        at = nodes(segments(a, z))
        power = np.nan_to_num(wind_luminosity(
            10.0 ** at.log_l, 10.0 ** at.log_teff, at.mass_now, np.full(at.log_l.shape, 10.0 ** tab.mhs[z])
        ))
        out[a, z] = float((at.weight * power).sum())
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
    lo =np.clip(np.atleast_1d(np.asarray(age_lo_gyr, dtype=float)) * 1e9, 0.0, _FINE_AGES[-1])
    hi = np.clip(np.atleast_1d(np.asarray(age_hi_gyr, dtype=float)) * 1e9, 0.0, _FINE_AGES[-1])
    width = np.where(hi > lo, hi - lo, 1.0)

    def at(x: np.ndarray) -> np.ndarray:  # (n_mh, n_t, k): the cumulative integral at ages x
        i = np.clip(np.searchsorted(_FINE_AGES, x, side="right") - 1, 0, _FINE_AGES.size - 2)
        w = ((x - _FINE_AGES[i]) / (_FINE_AGES[i + 1] - _FINE_AGES[i]))[None, :, None]
        return table[:, i] * (1.0 - w) + table[:, i + 1] * w

    per_step = (at(hi) - at(lo)) / width[None, :, None]  # (n_mh, n_t, k)
    mh = nearest_metallicity(feh)
    flat = mh * lo.size + np.arange(lo.size)
    return per_step.reshape(-1, per_step.shape[-1])[flat]


def nearest_metallicity(feh: np.ndarray) -> np.ndarray:
    """The isochrone metallicity index :func:`steps_over` reads each [Fe/H] at: the nearest, as argmin
    |feh - mh| picks it (ties to the lower), by a search; NaN at the lowest. Shared with the bright
    catalogue's decomposition (``bright.py``, S48), which must put each step's mass on the same row."""
    tab = isochrones()
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=tab.mhs[0], neginf=tab.mhs[0], posinf=tab.mhs[-1])
    return np.searchsorted(0.5 * (tab.mhs[1:] + tab.mhs[:-1]), feh, side="left")


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
