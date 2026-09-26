"""Mechanical feedback in closed form: the wind-blown bubble and the supernova remnant (S36, BUILD_II Phase 10).

No stage lives here: these are the solutions the ``bubbles`` stage evaluates per cluster and per remnant, and
the catalogue evaluates per star (``systems.materialise`` reads :func:`weaver_radius`, which is why the module
imports nothing that imports the catalogue). Every coefficient below was read at S36 before it was written,
and each carries the sentence and its place (rules B9, B14, D175); the level-0 constants the stage reads are
in ``models/level0.py`` with theirs.

**The wind bubble** — Weaver, McCray, Castor, Shapiro & Moore 1977, ApJ 218, 377, read from the ADS scan's
page images at S36. Its assumptions, in its own words: "an early-type star begins to blow a steady,
spherically symmetric stellar wind with constant terminal velocity V_w and mass-loss rate" (§II, p. 377),
"an ambient interstellar gas of uniform atomic density n_0" (p. 377), γ = 5/3 (eq. 4), and in the
intermediate stage the swept-up gas "has collapsed into a thin, almost isobaric shell" (p. 380) while the hot
interior conserves its energy, "E = (5/11) L_w t" (eq. 20). The solution:

- "R_2 = (250/(308π))^{1/5} L_w^{1/5} ρ_0^{−1/5} t^{3/5}" (eq. 21, p. 380), 0.76287 to five figures; the
  paper's numeric form "R_2(t) = 27 n_0^{−1/5} L_36^{1/5} t_6^{3/5} pc" (eq. 51, p. 387) matches it for a mean
  mass per hydrogen atom of about 1.2, and the model's 1.4 gives 26.2 pc (the paper states no μ).
- "V_2(t) = 16 n_0^{−1/5} L_36^{1/5} t_6^{−2/5} km s^−1" (eq. 52, p. 387): dR/dt of eq. 21, (3/5) R/t.
- "p = 7/(3850π)^{2/5} L_w^{2/5} ρ_0^{3/5} t^{−4/5}" (eq. 22, p. 380), the interior's uniform pressure.
- "T = 2.07 × 10^6 L_36^{8/35} n_0^{2/35} t_6^{−6/35} (1 − ξ)^{2/5} K" (eq. 37, p. 382), the conduction-set
  interior temperature, ξ = r/R_2; the model publishes its value at the centre, ξ = 0.
- The stall: "The velocity V_2(t) is slightly less than the approximate result from equation (52), until V_2(t)
  ≤ 10 km s^−1. At this time the exterior pressure becomes important and causes the outer shell to stall at 5 ×
  10^6 yr" (p. 389, their model at L_w = 1.27 × 10^36, n_0 = 1, in an H II region at 8000 K); the paper gives
  no formula for where. Eliminating t between eqs. 21 and 52 at V_2 = C_II gives it for a constant L_w.
- The shell: "n_s = n_0 (V_2² + C_0²)/C_s²" (eq. 67, p. 392), "valid only if C_0² + V_2² ≫ V_2 C_s", the
  isothermal shock's jump, the shell's sound speed "C_II ≈ 10 km s^−1 if the gas is H II" (p. 392); its
  column "N_s = n_0 R_2/3" (eq. 66, p. 391), so its thickness is N_s / n_s.

**The remnant** — the Sedov–Taylor blast wave, "ξ0 = 1.15167 at the shock radius, when the specific heat ratio
is γ = 5/3", R = ξ0 (E t²/ρ0)^{1/5} `[verified: Kim & Ostriker 2015, arXiv:1410.1537, §2]`, and its end in the
pressure-driven snowplow of Cioffi, McKee & Bertschinger 1988, as quoted with attribution by Chen & Slane 2001:
"r_PDS = 14.0 E51^{2/7} n0^{−3/7} ζm^{−1/7} pc", "rs = r_PDS (4t/(3t_PDS) − 1/3)^{3/10}", "vs = v_PDS
(4t/(3t_PDS) − 1/3)^{−7/10}, where v_PDS = 413 n0^{1/7} ζm^{3/14} E51^{1/14} km s^−1 and t_PDS = 1.33 × 10^4
E51^{3/14} n0^{−4/7} ζm^{−5/14} yr" `[verified: arXiv:astro-ph/0108502, §3.4.2, eqs. 3–5]`. The two join: at
n0 = 1 the Sedov radius at t_PDS is 14.04 pc against r_PDS = 14.0. The coefficients are level-0 constants; the
exponents are the solutions' and live here.
"""

from __future__ import annotations

import math

import numpy as np

from galaxy.stages.dust import CM_PER_PC
from galaxy.stages.massive_stars import BOLTZMANN, SECONDS_PER_YEAR, SOLAR_LUMINOSITY, SOLAR_MASS

# Weaver et al. 1977's similarity solution: pure numbers of the solution, not calibrations.
WEAVER_RADIUS = (250.0 / (308.0 * math.pi)) ** 0.2  # eq. 21, 0.76287
WEAVER_PRESSURE = 7.0 / (3850.0 * math.pi) ** 0.4  # eq. 22, 0.16295 = (5/11) / (2π WEAVER_RADIUS³)
WEAVER_TEMPERATURE = 2.07e6  # K, eq. 37 at the centre, for L_36, n_0 (cm⁻³) and t_6
CM_PER_KM = 1.0e5
MSUN_PER_PC3_IN_G_PER_CM3 = SOLAR_MASS / CM_PER_PC**3


def weaver_radius(luminosity_erg: np.ndarray, density_g: np.ndarray, age_s: np.ndarray) -> np.ndarray:
    """R_2 in cm (eq. 21): wind power in erg/s, ambient mass density in g/cm³, age in s. NaN where the power
    is NaN (no wind the recipe covers) or the density is not positive (no medium to sweep)."""
    L = np.asarray(luminosity_erg, dtype=float)
    rho = np.asarray(density_g, dtype=float)
    t = np.asarray(age_s, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = WEAVER_RADIUS * (L / np.where(rho > 0.0, rho, np.nan)) ** 0.2 * np.maximum(t, 0.0) ** 0.6
    return np.where(rho > 0.0, r, np.nan)


def weaver_velocity(radius_cm: np.ndarray, age_s: np.ndarray) -> np.ndarray:
    """V_2 = (3/5) R_2 / t in km/s (eq. 52 is this for eq. 21); NaN at t = 0, where it diverges."""
    t = np.asarray(age_s, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = 0.6 * np.asarray(radius_cm, dtype=float) / np.where(t > 0.0, t, np.nan) / CM_PER_KM
    return v


def weaver_pressure(luminosity_erg: np.ndarray, density_g: np.ndarray, age_s: np.ndarray) -> np.ndarray:
    """The interior's pressure over Boltzmann's constant, K cm⁻³ (eq. 22); NaN at t = 0."""
    L = np.asarray(luminosity_erg, dtype=float)
    rho = np.asarray(density_g, dtype=float)
    t = np.asarray(age_s, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = WEAVER_PRESSURE * L**0.4 * rho**0.6 * np.where(t > 0.0, t, np.nan) ** -0.8
    return p / BOLTZMANN


def weaver_temperature(luminosity_erg: np.ndarray, n0: np.ndarray, age_yr: np.ndarray) -> np.ndarray:
    """The interior's temperature at its centre, K (eq. 37 at ξ = 0); NaN at t = 0."""
    L36 = np.asarray(luminosity_erg, dtype=float) / 1.0e36
    t6 = np.asarray(age_yr, dtype=float) / 1.0e6
    with np.errstate(divide="ignore", invalid="ignore"):
        return WEAVER_TEMPERATURE * L36 ** (8.0 / 35.0) * np.asarray(n0, dtype=float) ** (2.0 / 35.0) * np.where(t6 > 0.0, t6, np.nan) ** (-6.0 / 35.0)


def weaver_stall_radius(luminosity_erg: np.ndarray, density_g: np.ndarray, sound_kms: float) -> np.ndarray:
    """R_2 in cm when its velocity (3/5) R_2/t has fallen to ``sound_kms``: eliminating t between eqs. 21 and
    52, R = a^{5/2} (L/ρ₀)^{1/2} (0.6/C)^{3/2}. Weaver et al. find the shell stalls there: "until V_2(t) ≤ 10
    km s^−1. At this time the exterior pressure becomes important and causes the outer shell to stall" (p. 389),
    and the thin-shell treatment "fails when V_2 approaches C_0" (p. 392)."""
    rho = np.asarray(density_g, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return WEAVER_RADIUS**2.5 * np.sqrt(np.asarray(luminosity_erg, dtype=float) / np.where(rho > 0.0, rho, np.nan)) * (
            0.6 / (sound_kms * CM_PER_KM)
        ) ** 1.5


def isothermal_shell_density(n0: np.ndarray, velocity_kms: np.ndarray, ambient_sound: float, shell_sound: float) -> np.ndarray:
    """n_s = n_0 (V² + C_0²) / C_s² (Weaver et al. 1977 eq. 67): the density behind an isothermal shock."""
    v = np.asarray(velocity_kms, dtype=float)
    return np.asarray(n0, dtype=float) * (v * v + ambient_sound**2) / shell_sound**2


def shell_thickness(radius: np.ndarray, n0: np.ndarray, n_shell: np.ndarray) -> np.ndarray:
    """The swept-up shell's thickness, in ``radius``'s unit: its column n_0 R/3 (eq. 66) over its density."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(radius, dtype=float) * np.asarray(n0, dtype=float) / (3.0 * np.asarray(n_shell, dtype=float))


def shell_volume(radius: np.ndarray, thickness: np.ndarray) -> np.ndarray:
    """The volume between R − Δ and R, in the cube of their unit."""
    r = np.asarray(radius, dtype=float)
    inner = np.maximum(r - np.asarray(thickness, dtype=float), 0.0)
    return 4.0 / 3.0 * math.pi * (r**3 - inner**3)


def sedov_radius(energy_erg: float, density_g: np.ndarray, age_s: np.ndarray, xi: float) -> np.ndarray:
    """R = ξ0 (E t² / ρ0)^{1/5} in cm."""
    rho = np.asarray(density_g, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return xi * (energy_erg * np.asarray(age_s, dtype=float) ** 2 / rho) ** 0.2


def pds_time(e51: float, n0: np.ndarray, zeta: np.ndarray, coefficient: float) -> np.ndarray:
    """t_PDS in yr, Cioffi et al. 1988: coefficient × E51^{3/14} n0^{−4/7} ζm^{−5/14}."""
    return coefficient * e51 ** (3.0 / 14.0) * np.asarray(n0, dtype=float) ** (-4.0 / 7.0) * np.asarray(zeta, dtype=float) ** (-5.0 / 14.0)


def pds_radius(e51: float, n0: np.ndarray, zeta: np.ndarray, coefficient: float) -> np.ndarray:
    """r_PDS in pc: coefficient × E51^{2/7} n0^{−3/7} ζm^{−1/7}."""
    return coefficient * e51 ** (2.0 / 7.0) * np.asarray(n0, dtype=float) ** (-3.0 / 7.0) * np.asarray(zeta, dtype=float) ** (-1.0 / 7.0)


def pds_velocity(e51: float, n0: np.ndarray, zeta: np.ndarray, coefficient: float) -> np.ndarray:
    """v_PDS in km/s: coefficient × n0^{1/7} ζm^{3/14} E51^{1/14}."""
    return coefficient * np.asarray(n0, dtype=float) ** (1.0 / 7.0) * np.asarray(zeta, dtype=float) ** (3.0 / 14.0) * e51 ** (1.0 / 14.0)


def snowplow(age_yr: np.ndarray, t_pds: np.ndarray) -> np.ndarray:
    """(4t / 3t_PDS − 1/3): the snowplow's clock, 1 at t_PDS."""
    return 4.0 * np.asarray(age_yr, dtype=float) / (3.0 * np.asarray(t_pds, dtype=float)) - 1.0 / 3.0


def star_bubble_radius(wind_lsun: np.ndarray, age_gyr: np.ndarray, density_msun_pc3: np.ndarray) -> np.ndarray:
    """One star's bubble in pc: eq. 21 at its own wind power (L☉) held for its whole age (Gyr), in an ambient
    mass density given in M☉/pc³. NaN where the star has no wind the recipe covers."""
    return weaver_radius(
        np.asarray(wind_lsun, dtype=float) * SOLAR_LUMINOSITY,
        np.asarray(density_msun_pc3, dtype=float) * MSUN_PER_PC3_IN_G_PER_CM3,
        np.asarray(age_gyr, dtype=float) * 1.0e9 * SECONDS_PER_YEAR,
    ) / CM_PER_PC
