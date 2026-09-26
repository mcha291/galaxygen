"""Stellar remnants and planetary nebulae (BUILD_II Phase 4, S29).

The catalogue has published living stars only: a star past the heaviest mass its isochrone
still holds is NaN in L and T_eff (``photometry.lookup``, D164). This module says what such a
star *is* — a white dwarf, a neutron star or a black hole, and for a short while after an
intermediate-mass star leaves the AGB, a planetary nebula — and what the mass the model counts
as locked in stars is made of: living stars at their present mass, and remnants.

**The rulings (S29, made before any number was read, rule D113), and what the sources said.**
Every number below was read from the source's own text by a read-only agent at S29, through
the arXiv / ar5iv HTML, and entered as printed; none is recalled (rule B9).

(a) *The initial–final mass relation is sourced*: Cummings, Kalirai, Tremblay, Ramirez-Ruiz &
Choi 2018, ApJ 866, 21 (arXiv:1809.01673), §VI.2 "Intermediate and High-Mass IFMR", the
**PARSEC-based** piecewise-linear fit, eqs. 1–3, chosen because the catalogue's isochrones are
PARSEC v1.2S, which is what that fit's progenitor ages were computed with ("non-rotating PARSEC
isochrones ... version 1.2S") `[verified: arXiv:1809.01673, read twice at S29, consistent]`:

    M_f = (0.0873 ± 0.0190) M_i + (0.476 ± 0.033)    0.87 < M_i < 2.80 M☉    (eq. 1)
    M_f = (0.181  ± 0.041 ) M_i + (0.210 ± 0.131)    2.80 < M_i < 3.65 M☉    (eq. 2)
    M_f = (0.0835 ± 0.0144) M_i + (0.565 ± 0.073)    3.65 < M_i < 8.20 M☉    (eq. 3)

The **MIST-based** fit of the same paper is the named alternative (rule B12), kept as a
function and compared by a test, never averaged: 0.080 M_i + 0.489 (0.83–2.85), 0.187 M_i +
0.184 (2.85–3.60), 0.107 M_i + 0.471 (3.60–7.20) `[verified: arXiv:1809.01673, read once at S29]`.
Whether the paper prefers one of the two, the two reads disagreed; the ruling does not depend
on it.

*The classes' initial-mass boundaries are sourced too.* A dead star below **8.5 M☉** leaves a
white dwarf: Smartt 2009, ARA&A 47, 63, §4.4, the minimum initial mass for core collapse from
observed progenitors, m_min = 8.5 (+1, −1.5) M☉ `[verified: arXiv:0908.0700, read at S29]`;
Heger et al. 2003's "stars below ∼9 M⊙ ... end their lives as white dwarfs" is the named
alternative. From 8.5 to **25 M☉** it leaves a neutron star, and above 25 a black hole: Heger,
Fryer, Woosley, Langer & Hartmann 2003, ApJ 591, 288, §II.1, "black hole formation by fall back
ensues ... (a ≲25 M⊙ main sequence star)" `[verified: astro-ph/0212469, read at S29]`.

(b) *The black hole's mass is a measured constant, not a function of metallicity*, because no
metallicity-dependent fit was read: Spera, Mapelli & Bressan 2015's solar-metallicity fitting
formula (their Appendix C) could not be extracted from the paper's HTML, and Fryer et al.
2012's prescriptions need a CO-core mass this model does not carry. So a black hole weighs
**7.8 M☉**, the Galactic black-hole mass distribution of Özel, Psaltis, Narayan & McClintock
2010, ApJ 725, 1918 ("a narrow mass distribution at 7.8±1.2 M⊙", arXiv:1006.2834), and a
neutron star **1.33 M☉**, the double-neutron-star distribution of Özel & Freire 2016, ARA&A 54,
401, §2.5 ("M0=1.33 M⊙ and σ=0.09 M⊙", arXiv:1603.02698; its slow pulsars' 1.49 is the named
alternative) `[verified: read at S29]`. The metallicity dependence is a debt, not an invention.

(c) *The planetary-nebula phase lasts 27 000 years*: Badenes, Maoz & Ciardullo 2015, ApJL 804,
L25, §III, "lifetimes of 27±6 kyr for the PNe produced by the older progenitors" — the 1.0–1.2
M☉ stars that make most of the LMC's PNe `[verified: arXiv:1502.01015, read at S29]`. Their
tentative 11 (+6, −8) kyr for progenitors of 2.1–8.2 M☉ and Buzzoni, Arnaboldi & Corradi 2006's
τ ≈ 30 000 yr (MNRAS 368, 877, §2.2, astro-ph/0602458) are named alternatives; one duration is
applied to every white-dwarf progenitor.

**Which star is which, per star.** A star is dead exactly where the table says so — NaN
luminosity — and nothing here re-derives that. A dead star's class is its initial mass against
the two boundaries; its remnant mass is the IFMR's for a white dwarf, the constants otherwise.
A dead white-dwarf progenitor whose death was less than the phase duration ago is a planetary
nebula instead, its remnant mass the white dwarf it is becoming. Its death age is read from the
same table the luminosity is: the heaviest living mass of each isochrone, linear in log age
between them (``photometry.lookup``'s own reading), inverted.

**What does not hold, recorded rather than hidden.**

- *The IFMR is extrapolated* below 0.87 M☉ (the oldest metal-poor stars die at 0.79) and from
  8.20 to 8.5 M☉, each by its end segment.
- *The boundaries are solar-metallicity ones at every metallicity.* Heger et al. say that at high
  metallicity mass loss makes smaller black holes by fallback "until, ultimately, only neutron
  stars are made"; the table cannot see a stripped core and nothing here moves the boundaries.
- *Ages past 12.6 Gyr are read at 12.6 Gyr*, as for the light: no star dies after the table ends,
  so the oldest stars form no planetary nebulae and their remnant mass stops growing there.
- *A star heavier than the youngest isochrone reaches* (64 M☉ at 4 Myr) is NaN at every age and
  so is counted with the dead, as the table counts it, even when younger than 4 Myr.
- *The end of the table's track stands for the end of the AGB.* PARSEC's isochrones stop on the
  TP-AGB or, at 12.6 Gyr, on the early AGB; the time from there to the nebula is not modelled.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

import numpy as np

from galaxy.stages.photometry import EXTRA, cumulative_over_age, imf_weights, isochrones, on_fine_ages, steps_over

# --- the sourced constants (module-level: materialise has no ctx.constants, as in massive_stars) ---

# Cummings et al. 2018 (see the docstring): (M_i low, M_i high, slope, intercept), M☉.
IFMR_PARSEC: tuple[tuple[float, float, float, float], ...] = (
    (0.87, 2.80, 0.0873, 0.476),
    (2.80, 3.65, 0.181, 0.210),
    (3.65, 8.20, 0.0835, 0.565),
)
IFMR_MIST: tuple[tuple[float, float, float, float], ...] = (  # the named alternative
    (0.83, 2.85, 0.080, 0.489),
    (2.85, 3.60, 0.187, 0.184),
    (3.60, 7.20, 0.107, 0.471),
)
WHITE_DWARF_MAX_INITIAL_MASS = 8.5  # M☉, Smartt 2009 m_min
BLACK_HOLE_MIN_INITIAL_MASS = 25.0  # M☉, Heger et al. 2003
NEUTRON_STAR_MASS = 1.33  # M☉, Özel & Freire 2016, double neutron stars
BLACK_HOLE_MASS = 7.8  # M☉, Özel et al. 2010
PLANETARY_NEBULA_DURATION = 27.0e3  # yr, Badenes, Maoz & Ciardullo 2015

REMNANT_CATEGORIES: tuple[str, ...] = ("none", "white_dwarf", "neutron_star", "black_hole", "planetary_nebula")
NONE, WHITE_DWARF, NEUTRON_STAR, BLACK_HOLE, PLANETARY_NEBULA = range(len(REMNANT_CATEGORIES))


def white_dwarf_mass(initial_mass: np.ndarray, relation: str = "parsec") -> np.ndarray:
    """The IFMR's final mass (M☉): each segment on its own range, the end segments extended."""
    segments = IFMR_PARSEC if relation == "parsec" else IFMR_MIST
    m = np.asarray(initial_mass, dtype=float)
    out = segments[0][2] * m + segments[0][3]
    for lo, _, slope, intercept in segments[1:]:
        out = np.where(m >= lo, slope * m + intercept, out)
    return out


def fate(initial_mass: np.ndarray) -> np.ndarray:
    """The class a star of this initial mass leaves when it dies (a category index)."""
    m = np.asarray(initial_mass, dtype=float)
    return np.where(
        m < WHITE_DWARF_MAX_INITIAL_MASS, WHITE_DWARF, np.where(m < BLACK_HOLE_MIN_INITIAL_MASS, NEUTRON_STAR, BLACK_HOLE)
    ).astype(np.int64)


def remnant_mass(initial_mass: np.ndarray) -> np.ndarray:
    """The mass (M☉) of the remnant a star of this initial mass leaves."""
    m = np.asarray(initial_mass, dtype=float)
    kind = fate(m)
    return np.where(kind == WHITE_DWARF, white_dwarf_mass(m), np.where(kind == NEUTRON_STAR, NEUTRON_STAR_MASS, BLACK_HOLE_MASS))


@functools.cache
def _heaviest_alive() -> np.ndarray:
    """(n_mh, n_age): the heaviest mass each isochrone still holds, decreasing with age."""
    tab = isochrones()
    return np.array([[tab.track(a, z)[0][-1] for a in range(tab.log_ages.size)] for z in range(tab.mhs.size)])


def death_age(initial_mass: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """The age (Gyr) at which the table's star of this mass and [Fe/H] dies.

    The inverse of the heaviest living mass, linear in log age between isochrones — the reading
    ``photometry.lookup`` decides "dead" by, so a star is NaN in L exactly when its age (clamped
    to the table) is past this. +inf for a star lighter than the oldest isochrone's heaviest (it
    never dies in the table); NaN for one heavier than the youngest's (it dies before the table
    begins, and when is not known).
    """
    tab = isochrones()
    m = np.asarray(initial_mass, dtype=float)
    mh = np.abs(np.asarray(feh, dtype=float)[:, None] - tab.mhs[None, :]).argmin(axis=1)
    top = _heaviest_alive()
    out = np.empty(m.shape)
    for z in np.unique(mh):
        sel = mh == z
        heaviest = top[z]
        log_age = np.interp(m[sel], heaviest[::-1], tab.log_ages[::-1])
        out[sel] = np.where(m[sel] > heaviest[0], np.nan, np.where(m[sel] < heaviest[-1], np.inf, 10.0**log_age / 1e9))
    return out


def classify(
    initial_mass: np.ndarray, age_gyr: np.ndarray, feh: np.ndarray, luminosity: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """(``star_remnant`` category index, ``star_remnant_mass`` in M☉) per star.

    Dead is NaN luminosity, the table's own mark. A living star is ``none`` with a NaN remnant
    mass: it has no remnant, and zero would read as a measured massless one (rule B9).
    """
    m = np.asarray(initial_mass, dtype=float)
    dead = np.isnan(np.asarray(luminosity, dtype=float))
    kind = np.where(dead, fate(m), NONE).astype(np.int64)
    mass = np.where(dead, remnant_mass(m), np.nan)
    candidates = np.flatnonzero(kind == WHITE_DWARF)
    if candidates.size:
        since = np.asarray(age_gyr, dtype=float)[candidates] - death_age(m[candidates], np.asarray(feh, dtype=float)[candidates])
        young = since * 1e9 < PLANETARY_NEBULA_DURATION  # NaN or inf compare False
        kind[candidates[young]] = PLANETARY_NEBULA
    return kind, mass


# --- the population integral: what locked mass is made of ----------------------------------

# Per unit mass formed, per isochrone: the living stars at their present mass (after the tracks'
# own mass loss), the same at their initial mass, the mass in each remnant class, and the number
# of dead white-dwarf progenitors (the planetary nebulae are that number's rate of change).
MASS_QUANTITIES: tuple[str, ...] = ("living", "living_initial", "white_dwarf", "neutron_star", "black_hole")
QUANTITIES: tuple[str, ...] = (*MASS_QUANTITIES, "white_dwarf_progenitors")
# The mass grid the IMF is integrated on: log-spaced, with a node at every kink of the IMF and the
# IFMR and at both class boundaries, so no trapezoid straddles one. At this density the trapezoid's
# error is ~1e-7 of each integral [inferred: (Δ ln m)² / 12 with Δ ln m = 1.3e-3].
_GRID_POINTS = 6000


def _cumulative(f: np.ndarray, m: np.ndarray) -> np.ndarray:
    """∫ f dm from the grid's first point to each point, by the trapezoid."""
    return np.concatenate([[0.0], np.cumsum(np.diff(m) * 0.5 * (f[1:] + f[:-1]))])


@functools.cache
def population_mass() -> np.ndarray:
    """(n_age, n_mh, len(QUANTITIES)): each quantity per unit mass formed of a Kroupa population.

    Per isochrone, the IMF is split at the heaviest mass it still holds — a node of the grid, so
    the living and the dead meet exactly there: the living below it at their present mass (the
    table's own, after the tracks' mass loss), the dead above it as the remnants they leave.
    """
    from galaxy.stages.systems import IMF_BREAK, IMF_MAX, IMF_MIN

    tab = isochrones()
    now = EXTRA.index("mass_now")
    kinks = [IMF_BREAK, *(s[0] for s in IFMR_PARSEC[1:]), WHITE_DWARF_MAX_INITIAL_MASS, BLACK_HOLE_MIN_INITIAL_MASS]
    base = np.unique(np.concatenate([np.geomspace(IMF_MIN, IMF_MAX, _GRID_POINTS), kinks]))
    formed = _cumulative(imf_weights(base) * base, base)[-1]
    out = np.zeros((tab.log_ages.size, tab.mhs.size, len(QUANTITIES)))
    for (a, z), (mass, _, _) in tab.tracks.items():
        top = min(float(mass[-1]), IMF_MAX)
        at = int(np.searchsorted(base, top))
        m = base if at < base.size and base[at] == top else np.insert(base, at, top)
        phi = imf_weights(m)
        ratio = np.interp(np.clip(m, mass[0], mass[-1]), mass, tab.extra[(a, z)][:, now] / mass)
        number, initial = _cumulative(phi, m), _cumulative(phi * m, m)
        present, white = _cumulative(phi * m * ratio, m), _cumulative(phi * white_dwarf_mass(m), m)
        k, wd, bh = (int(np.searchsorted(m, x)) for x in (top, max(top, WHITE_DWARF_MAX_INITIAL_MASS), max(top, BLACK_HOLE_MIN_INITIAL_MASS)))
        out[a, z] = (
            present[k],
            initial[k],
            white[wd] - white[k],
            NEUTRON_STAR_MASS * (number[bh] - number[wd]),
            BLACK_HOLE_MASS * (number[-1] - number[bh]),
            number[wd] - number[k],
        )
    return out / formed


@functools.cache
def _step_table() -> np.ndarray:
    """(n_mh, n_fine, len(QUANTITIES)) for ``photometry.steps_over``: the masses' cumulative
    integrals over age, and the progenitor count itself, whose step difference over the step's
    width is the rate at which white-dwarf progenitors die."""
    fine = on_fine_ages(population_mass())  # (n_fine, n_mh, k)
    masses = cumulative_over_age(fine[..., : len(MASS_QUANTITIES)])
    count = np.ascontiguousarray(np.moveaxis(fine[..., len(MASS_QUANTITIES):], 0, 1))
    return np.concatenate([masses, count], axis=-1)


@dataclass(frozen=True)
class MassBudget:
    """What the locked mass is, in M☉, and the planetary nebulae alive today."""

    living: float  # at present mass
    living_initial: float  # the same stars at their initial mass
    white_dwarf: float
    neutron_star: float
    black_hole: float
    formed: float  # the mass formed that these are the remains of
    locked: float  # what the model counts: formed less the instantaneous return
    planetary_nebulae: float  # a count

    @property
    def remnant(self) -> float:
        return self.white_dwarf + self.neutron_star + self.black_hole

    @property
    def remnant_fraction(self) -> float:
        """Of the mass in stars and remnants, the share in remnants."""
        return self.remnant / (self.living + self.remnant)


def _per_formed(age_lo: np.ndarray, age_hi: np.ndarray, feh: np.ndarray) -> np.ndarray:
    """``(..., n_t, len(QUANTITIES))`` per unit mass formed, each step averaged over its ages;
    the last quantity the progenitors' death rate per year."""
    return steps_over(_step_table(), age_lo, age_hi, feh)


def budget(
    locked_history: np.ndarray,
    feh_history: np.ndarray,
    R: np.ndarray,
    t: np.ndarray,
    t_max: float,
    return_fraction: float,
    bulge_mass: float,
    bulge_age: float,
    bulge_feh: float,
) -> MassBudget:
    """The disc's history (``stars_formed_history``, locked M☉/pc² per step at today's radii, on
    step centres ``t``) and the bulge (locked M☉, one old population), each over (1 − R) for the
    mass formed, times the population integral per unit mass formed — as ``light`` integrates
    the light, each step averaged over the ages its stars span."""
    pc2_per_kpc = 1.0e6
    dt = t_max / t.size
    youngest = t_max - (t + 0.5 * dt)
    formed = np.asarray(locked_history, dtype=float) / (1.0 - return_fraction)
    per = _per_formed(youngest, youngest + dt, feh_history)  # (n_R, n_t, k)
    per_area = np.einsum("rt,rtk->rk", formed, per)  # per pc²
    disc = np.trapezoid(per_area * (2.0 * np.pi * R * pc2_per_kpc)[:, None], R, axis=0)
    disc_formed = float(np.trapezoid(formed.sum(axis=1) * 2.0 * np.pi * R * pc2_per_kpc, R))
    bulge_formed = bulge_mass / (1.0 - return_fraction)
    # The bulge is one population at one age: read over one step's width about it.
    bulge = bulge_formed * _per_formed(np.array([bulge_age - 0.5 * dt]), np.array([bulge_age + 0.5 * dt]), np.array([bulge_feh]))[0]
    total = disc + bulge
    values = dict(zip(QUANTITIES, (float(v) for v in total)))
    return MassBudget(
        living=values["living"], living_initial=values["living_initial"], white_dwarf=values["white_dwarf"],
        neutron_star=values["neutron_star"], black_hole=values["black_hole"],
        formed=disc_formed + bulge_formed, locked=(disc_formed + bulge_formed) * (1.0 - return_fraction),
        planetary_nebulae=values["white_dwarf_progenitors"] * PLANETARY_NEBULA_DURATION,
    )
