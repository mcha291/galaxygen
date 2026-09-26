"""Massive stars: the hydrogen-ionizing photon rate, the wind, and the Wolf-Rayet proxy (BUILD_II Phase 3).

Everything nebular the later phases build reads how many hydrogen-ionizing photons a star
emits, Q(H⁰), and that is a steep function of the top few rungs of the IMF. The catalogue
carries each star's L and T_eff (``photometry.lookup``), so Q is one more column, and the
population integral over the same isochrones is the galaxy-scale field (``light.py``).

**The ruling (S28, made before any number was read, rule D113).** Q comes from a *tabulated
q₀(T_eff) calibration from model atmospheres* for O and early-B stars — the photon flux per
unit surface area — times the star's own surface area, 4πR² = L / σT_eff⁴. The blackbody
integral above the Lyman limit is the **named alternative** (rule B12): kept as a function,
compared against the table by a test, never averaged with it.

**The table** is Sternberg, Hoffmann & Pauldrach 2003, ApJ 599, 1333, Table 1 ("Parameters
for OB stars of luminosity class V"; T_eff, gravities, radii and spectral classes from Vacca
et al. 1996, the ionizing fluxes from their own model atmospheres): 15 rows, O3 to B0.5,
32 060 to 51 230 K `[verified: SHP03 Table 1, fetched from arXiv:astro-ph/0312232 (ar5iv) at
S28 by a read-only agent and entered verbatim]`. It is chosen over Martins, Schaerer &
Hillier 2005, A&A 436, 1049, Table 4 (class V, observational T_eff scale, O3–O9.5, also
entered below `[verified: MSH05 Table 4, arXiv:astro-ph/0503346 (ar5iv), S28]`) because it
alone reaches the early B stars; MSH05 is kept as the second calibration a test compares at
common temperatures. Both tables' rows are checked for transcription by their own arithmetic,
Q = q · 4πR² and L = 4πR²σT⁴ (``tests/test_massive_stars.py``).

**What the table does not cover, recorded rather than hidden.**

- *Gravity.* q₀ is read against T_eff alone, from dwarfs. A giant or supergiant of the same
  T_eff has a lower gravity and, in SHP03's own Table 2, a higher q_H (+0.2 dex at 33 kK).
- *Outside 32 060–51 230 K* the table says nothing. There q₀ is the blackbody's, scaled by the
  table-to-blackbody ratio at the nearer end of the table, so the calibration is continuous
  and the blackbody supplies only the temperature dependence `[inferred]`. **That is most of a
  population's photons**: of a steady solar population's Q, 0.328 comes from stars inside the
  table's range, 0.218 from cooler ones (the many B1-B3 stars) and 0.454 from hotter ones, the
  stripped post-main-sequence stars PARSEC takes to 200 kK, whose atmospheres are nothing like
  a dwarf's (``tests/test_massive_stars.py``, S28). The ruling governs a third of the budget;
  the rest is the extension's, and it is the first thing a sourced hot-star table would replace.
- *Stars heavier than the youngest isochrone reaches* (64 M☉ at 4 Myr) have no L or T_eff and
  so no Q (``photometry.py``). Given the Q of the heaviest star the youngest isochrone holds
  for that isochrone's 3.98 Myr, they would be about half of a steady population's photons
  (0.489 at solar metallicity, ``tests/test_massive_stars.py``): an estimate whose two errors
  have opposite signs, not a bound [inferred].
"""

from __future__ import annotations

import numpy as np

# --- physical constants, cgs ------------------------------------------------------------
# h, k, c and the electronvolt are the SI 2019 defining constants, exact; σ follows from them;
# L☉ is the IAU 2015 nominal solar luminosity (Resolution B3) [recall]. The hydrogen
# ionization energy, 13.598 eV, is the 912 Å Lyman limit [recall].
PLANCK = 6.62607015e-27  # erg s
BOLTZMANN = 1.380649e-16  # erg / K
LIGHT_SPEED = 2.99792458e10  # cm / s
ELECTRON_VOLT = 1.602176634e-12  # erg
STEFAN_BOLTZMANN = 5.670374419e-5  # erg / cm² / s / K⁴
SOLAR_LUMINOSITY = 3.828e33  # erg / s
HYDROGEN_EDGE = 13.598 * ELECTRON_VOLT  # erg

# --- the calibrations ---------------------------------------------------------------------
# Sternberg, Hoffmann & Pauldrach 2003, Table 1, luminosity class V. Columns as printed:
# spectral type, T_eff (K), log g (cm s⁻²), R (R☉), log L (L☉), M (M☉), log Q_H (s⁻¹),
# log q_H (cm⁻² s⁻¹). The v_∞, Ṁ and helium columns are not entered: nothing reads them.
SHP03_CLASS_V: tuple[tuple[str, float, float, float, float, float, float, float], ...] = (
    ("O3", 51230.0, 4.149, 13.2, 6.04, 87.6, 49.87, 24.84),
    ("O4", 48670.0, 4.106, 12.3, 5.88, 68.9, 49.68, 24.72),
    ("O4.5", 47400.0, 4.093, 11.8, 5.81, 62.3, 49.59, 24.66),
    ("O5", 46120.0, 4.081, 11.4, 5.73, 56.6, 49.49, 24.59),
    ("O5.5", 44840.0, 4.060, 11.0, 5.65, 50.4, 49.39, 24.52),
    ("O6", 43560.0, 4.042, 10.7, 5.57, 45.2, 49.29, 24.45),
    ("O6.5", 42280.0, 4.030, 10.3, 5.49, 41.0, 49.18, 24.37),
    ("O7", 41010.0, 4.021, 10.0, 5.40, 37.7, 49.06, 24.28),
    ("O7.5", 39730.0, 4.006, 9.6, 5.32, 34.1, 48.92, 24.17),
    ("O8", 38450.0, 3.989, 9.3, 5.24, 30.8, 48.75, 24.03),
    ("O8.5", 37170.0, 3.974, 9.0, 5.15, 28.0, 48.61, 23.92),
    ("O9", 35900.0, 3.959, 8.8, 5.06, 25.4, 48.47, 23.80),
    ("O9.5", 34620.0, 3.947, 8.5, 4.97, 23.3, 48.26, 23.62),
    ("B0", 33340.0, 3.932, 8.3, 4.88, 21.2, 48.02, 23.40),
    ("B0.5", 32060.0, 3.914, 8.0, 4.79, 19.3, 47.71, 23.12),
)

# Martins, Schaerer & Hillier 2005, Table 4, luminosity class V, observational T_eff scale.
# Columns as printed: spectral type, T_eff (K), log g, log L (L☉), R (R☉), M_spec (M☉),
# log q₀ (cm⁻² s⁻¹), log Q₀ (s⁻¹). M_V, BC and the helium columns are not entered.
MSH05_CLASS_V: tuple[tuple[str, float, float, float, float, float, float, float], ...] = (
    ("O3", 44852.0, 3.92, 5.84, 13.80, 57.95, 24.57, 49.64),
    ("O4", 42857.0, 3.92, 5.67, 12.42, 46.94, 24.47, 49.44),
    ("O5", 40862.0, 3.92, 5.49, 11.20, 38.08, 24.34, 49.22),
    ("O5.5", 39865.0, 3.92, 5.41, 10.64, 34.39, 24.27, 49.10),
    ("O6", 38867.0, 3.92, 5.32, 10.11, 30.98, 24.20, 48.99),
    ("O6.5", 37870.0, 3.92, 5.23, 9.61, 28.00, 24.13, 48.88),
    ("O7", 36872.0, 3.92, 5.14, 9.15, 25.29, 24.04, 48.75),
    ("O7.5", 35874.0, 3.92, 5.05, 8.70, 22.90, 23.94, 48.61),
    ("O8", 34877.0, 3.92, 4.96, 8.29, 20.76, 23.82, 48.44),
    ("O8.5", 33879.0, 3.92, 4.86, 7.90, 18.80, 23.69, 48.27),
    ("O9", 32882.0, 3.92, 4.77, 7.53, 17.08, 23.52, 48.06),
    ("O9.5", 31884.0, 3.92, 4.68, 7.18, 15.55, 23.39, 47.88),
)


def _calibration(rows: tuple[tuple, ...], teff_col: int, logq_col: int) -> tuple[np.ndarray, np.ndarray]:
    table = sorted((float(r[teff_col]), float(r[logq_col])) for r in rows)
    return np.array([t for t, _ in table]), np.array([q for _, q in table])


SHP03_TEFF, SHP03_LOG_Q = _calibration(SHP03_CLASS_V, 1, 7)
MSH05_TEFF, MSH05_LOG_Q = _calibration(MSH05_CLASS_V, 1, 6)


def blackbody_q0(teff: np.ndarray) -> np.ndarray:
    """Hydrogen-ionizing photons per cm² per second from a blackbody surface (the named alternative).

    q = π ∫ B_ν / hν dν above the Lyman limit = (2π / c²)(kT / h)³ ∫ x² / (eˣ − 1) dx from
    x₀ = hν₀ / kT, the integral summed as Σₙ e^(−n x₀)(x₀²/n + 2x₀/n² + 2/n³), exact term by
    term, until the next term is under 10⁻¹⁶ of the first at the hottest star asked about; at
    most sixty terms, which leave less than e^(−60 x₀) of it, under 10⁻¹² below 10⁶ K.
    """
    t = np.asarray(teff, dtype=float)
    out = np.zeros(t.shape)
    ok = np.isfinite(t) & (t > 0.0)
    x0 = HYDROGEN_EDGE / (BOLTZMANN * t[ok])
    # Terms until e^(−n x₀) < 10⁻¹⁶ at the hottest star asked about, at most sixty.
    terms = int(min(60, np.ceil(37.0 / max(float(x0.min()), 1e-3)))) if x0.size else 1
    n = np.arange(1, terms + 1, dtype=float)[:, None]
    series = (np.exp(-n * x0) * (x0**2 / n + 2.0 * x0 / n**2 + 2.0 / n**3)).sum(axis=0)
    out[ok] = 2.0 * np.pi / LIGHT_SPEED**2 * (BOLTZMANN * t[ok] / PLANCK) ** 3 * series
    out[~ok] = np.nan
    return out


def tabulated_q0(teff: np.ndarray, calibration: str = "shp03") -> np.ndarray:
    """q₀(T_eff) from the adopted table, log-linear in T_eff between its rows.

    Outside the table the blackbody carries the temperature dependence, scaled to meet the
    table at its nearer end (see the module docstring). ``calibration="msh05"`` reads Martins,
    Schaerer & Hillier's class V table the same way, for the comparison only.
    """
    grid, log_q = (SHP03_TEFF, SHP03_LOG_Q) if calibration == "shp03" else (MSH05_TEFF, MSH05_LOG_Q)
    t = np.asarray(teff, dtype=float)
    log_out = np.interp(t, grid, log_q)
    outside = np.isfinite(t) & ((t < grid[0]) | (t > grid[-1]))
    if outside.any():
        ends = np.log10(blackbody_q0(np.array([grid[0], grid[-1]])))
        shape = np.log10(np.maximum(blackbody_q0(t[outside]), 1e-300))
        offset = np.where(t[outside] < grid[0], log_q[0] - ends[0], log_q[-1] - ends[1])
        log_out[outside] = shape + offset
    return np.where(np.isfinite(t) & (t > 0.0), 10.0**log_out, np.nan)


def ionizing_photons(luminosity: np.ndarray, teff: np.ndarray, calibration: str = "shp03") -> np.ndarray:
    """Q(H⁰), photons per second, for stars of luminosity ``luminosity`` (L☉) and ``teff`` (K).

    Q = q₀(T_eff) · 4πR², with 4πR² = L / σT_eff⁴, so no radius is needed. ``calibration`` is
    ``"shp03"`` (the ruling), ``"msh05"`` (the second table) or ``"blackbody"`` (the named
    alternative). NaN where L or T_eff is: a star that has died emits nothing the table knows.
    """
    L = np.asarray(luminosity, dtype=float)
    t = np.asarray(teff, dtype=float)
    q0 = blackbody_q0(t) if calibration == "blackbody" else tabulated_q0(t, calibration)
    area = L * SOLAR_LUMINOSITY / (STEFAN_BOLTZMANN * np.where(t > 0.0, t, np.nan) ** 4)
    return q0 * area


# --- the wind (Vink, de Koter & Lamers 2001) -------------------------------------------------
#
# The mass-loss recipe for O and B stars, A&A 369, 574, eqs. 24 and 25, the coefficients as
# printed [verified: arXiv:astro-ph/0101509 (ar5iv), read at S28 by a read-only agent]:
#
#   hot side, 27 500 < T_eff <= 50 000 K, v_inf/v_esc = 2.6 (eq. 24)
#     log Mdot = -6.697 + 2.194 log(L/1e5) - 1.313 log(M/30) - 1.226 log[(v_inf/v_esc)/2.0]
#                + 0.933 log(T/40000) - 10.92 [log(T/40000)]^2 + 0.85 log(Z/Z_sun)
#   cool side, 12 500 <= T_eff <= 22 500 K, v_inf/v_esc = 1.3 (eq. 25)
#     log Mdot = -6.688 + 2.210 log(L/1e5) - 1.339 log(M/30) - 1.601 log[(v_inf/v_esc)/2.0]
#                + 1.07 log(T/20000) + 0.85 log(Z/Z_sun)
#
# with Mdot in Msun/yr, L and M in solar units. "In the critical temperature range between
# 22 500 <= Teff <= 27 500 K, either Eq. (24) or Eq. (25) should be used depending on the
# position of the bi-stability jump given by Eq. (15)": T_jump [kK] = 61.2 + 2.59 log<rho>,
# log<rho> = -14.94 + 0.85 log(Z/Z_sun) + 3.2 Gamma_e (eq. 23).
#
# **What is not sourced, and what is done instead.** The escape velocity the ratio multiplies
# is the effective one, with M_eff = M (1 - Gamma_e) [verified: Vink, de Koter & Lamers 2000,
# A&A 362, 295, arXiv:astro-ph/0008183, "the effective mass M_eff = M_* (1 - Gamma_e) was
# used"], Gamma_e = 7.66e-5 sigma_e L/M with sigma_e "taken as determined in Lamers &
# Leitherer 1993", a value S28 could not read. So Gamma_e is not applied: v_esc here is the
# Newtonian sqrt(2GM/R), which overstates v_inf by (1 - Gamma_e)^(-1/2) and the wind's power
# by (1 - Gamma_e)^(-1), and puts the jump by 3.2 x 2.59 Gamma_e kK too cool [inferred]. The
# mass-loss rate itself does not move: the ratio in eqs. 24-25 is the recipe's fixed 2.6 or
# 1.3. Outside 12 500-50 000 K the recipe says nothing, and nor does this: NaN.
VINK_HOT = (-6.697, 2.194, -1.313, -1.226, 0.933, -10.92, 0.85)
VINK_COOL = (-6.688, 2.210, -1.339, -1.601, 1.07, 0.85)
VINK_RATIO_HOT, VINK_RATIO_COOL = 2.6, 1.3
VINK_TEFF_RANGE = (12500.0, 50000.0)  # K: the cool side's floor and the hot side's ceiling
VINK_JUMP = (61.2, 2.59, -14.94, 0.85)  # eq. 15 (kK) and eq. 23 without its Gamma_e term

SOLAR_GM = 1.32712440018e26  # cm³/s², the IAU nominal solar mass parameter (level0's G cites it)
SECONDS_PER_YEAR = 3.15576e7  # the Julian year, a definition
SOLAR_MASS = SOLAR_GM / 6.67430e-8  # g: GM☉ over CODATA 2018's G [recall]; only Mdot's mass flux reads it


def jump_temperature(z_ratio: np.ndarray) -> np.ndarray:
    """The bistability jump's T_eff (K) at metallicity Z/Z☉, eqs. 15 and 23 without Γ_e."""
    a, b, c, d = VINK_JUMP
    return 1000.0 * (a + b * (c + d * np.log10(z_ratio)))


def wind(luminosity: np.ndarray, teff: np.ndarray, mass: np.ndarray, z_ratio: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(Ṁ in M☉/yr, v_∞ in km/s) by Vink, de Koter & Lamers 2001; NaN outside 12.5–50 kK.

    ``mass`` is the star's present mass (the isochrone's, after its own mass loss); ``z_ratio``
    is Z/Z☉, which the catalogue takes as 10^[Fe/H].
    """
    L = np.asarray(luminosity, dtype=float)
    T = np.asarray(teff, dtype=float)
    M = np.asarray(mass, dtype=float)
    z = np.asarray(z_ratio, dtype=float)
    hot = T >= jump_temperature(z)
    ratio = np.where(hot, VINK_RATIO_HOT, VINK_RATIO_COOL)
    lz = np.log10(z)
    h0, h1, h2, h3, h4, h5, h6 = VINK_HOT
    c0, c1, c2, c3, c4, c5 = VINK_COOL
    with np.errstate(invalid="ignore", divide="ignore"):
        x40 = np.log10(T / 40000.0)
        log_hot = (h0 + h1 * np.log10(L / 1e5) + h2 * np.log10(M / 30.0) + h3 * np.log10(VINK_RATIO_HOT / 2.0)
                   + h4 * x40 + h5 * x40**2 + h6 * lz)
        log_cool = (c0 + c1 * np.log10(L / 1e5) + c2 * np.log10(M / 30.0) + c3 * np.log10(VINK_RATIO_COOL / 2.0)
                    + c4 * np.log10(T / 20000.0) + c5 * lz)
        radius = np.sqrt(L * SOLAR_LUMINOSITY / (4.0 * np.pi * STEFAN_BOLTZMANN * T**4))  # cm
        v_esc = np.sqrt(2.0 * SOLAR_GM * M / radius) / 1e5  # km/s, Newtonian (see above)
    inside = (T >= VINK_TEFF_RANGE[0]) & (T <= VINK_TEFF_RANGE[1]) & np.isfinite(L) & np.isfinite(M) & (M > 0.0)
    mdot = np.where(inside, 10.0 ** np.where(hot, log_hot, log_cool), np.nan)
    return mdot, np.where(inside, ratio * v_esc, np.nan)


def wind_luminosity(luminosity: np.ndarray, teff: np.ndarray, mass: np.ndarray, z_ratio: np.ndarray) -> np.ndarray:
    """The wind's mechanical power ½ Ṁ v_∞², in L☉; NaN where the recipe does not apply."""
    mdot, v_inf = wind(luminosity, teff, mass, z_ratio)
    grams_per_second = mdot * SOLAR_MASS / SECONDS_PER_YEAR
    return 0.5 * grams_per_second * (v_inf * 1e5) ** 2 / SOLAR_LUMINOSITY


# --- the Wolf-Rayet proxy ------------------------------------------------------------------
#
# PARSEC's phase label does not name Wolf-Rayet stars, so the flag is a **stated proxy**, not a
# classification: a star past the main sequence (label >= 2; CMD's labels are 0 pre-main
# sequence and 1 main sequence [recall: the CMD output documentation]), born at least as massive
# as the lowest initial mass that becomes a WR star at solar metallicity, hotter than the coolest
# WR stars and at least as luminous as the faintest. The three numbers are Crowther 2007, ARA&A
# 45, 177 [verified: arXiv:astro-ph/0610356 (ar5iv), read at S28]: "At Solar metallicity the
# minimum initial mass for a star to become a WR star is ~25 Msun" (section 1); T* "range from
# 30 kK amongst WN10 subtypes" upward (section 3.2); "For Milky Way WC stars, inferred stellar
# luminosities are ~150,000 Lsun", the lowest the section quotes (section 3.3). What a WR star
# is - a hydrogen-depleted surface under a dense wind - the table cannot see; the minimum mass
# is the solar one at every metallicity, where the source says it rises as Z falls.
WR_MIN_INITIAL_MASS = 25.0  # Msun
WR_MIN_TEFF = 30000.0  # K
WR_MIN_LUMINOSITY = 1.5e5  # Lsun
POST_MAIN_SEQUENCE = 2  # the first PARSEC label past the main sequence
WR_CATEGORIES: tuple[str, ...] = ("no", "wolf_rayet")


def wolf_rayet(initial_mass: np.ndarray, luminosity: np.ndarray, teff: np.ndarray, phase: np.ndarray) -> np.ndarray:
    """1 where a star meets the proxy, 0 elsewhere (a dead star included: it is not a WR star)."""
    with np.errstate(invalid="ignore"):
        flag = (
            (np.asarray(phase) >= POST_MAIN_SEQUENCE)
            & (np.asarray(initial_mass) >= WR_MIN_INITIAL_MASS)
            & (np.asarray(teff) >= WR_MIN_TEFF)
            & (np.asarray(luminosity) >= WR_MIN_LUMINOSITY)
        )
    return flag.astype(np.int64)
