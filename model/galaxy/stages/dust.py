"""Dust that radiates, not only absorbs: scattering, the heating balance, PAHs (checkpoint 4, S31).

BUILD_II Phase 7. The ``ism`` stage (D163) gives the dust's surface density and the V-band
extinction it causes face-on; the ``light`` stage (D165) gives the starlight it sits in. This
stage adds what the dust does with that light, and adds no input, no seed and no field the
two stages' definitions change: ``dust_extinction_v`` is read, never redefined (D167).

**One grain model** (ruling (a), S31). The extinction law's shape R_V, the V-band albedo and
the scattering asymmetry g are the Milky Way R_V = 3.1 carbonaceous-silicate model of
Weingartner & Draine 2001 as renormalised by Draine 2003, read from Draine's own tabulation;
so are the far-ultraviolet extinction and albedo G₀ needs and the far-infrared opacity the
temperature needs. Any other R_V is the named alternative, never an average (rule B12).

**The heating balance** (ruling (b)). At each radius the disc is a slab in which stars and dust
are uniformly mixed, and the starlight a unit area emits, ``disc_surface_brightness``, is
absorbed with the probability that an isotropically emitted photon does not escape a slab of
total vertical absorption optical depth τ:

    P_esc(τ) = (1/2 − E₃(τ)) / τ,     absorbed = Σ_L (1 − P_esc(τ))

(the angle-averaged escape probability of a uniform emitting and absorbing slab, both faces
counted) ``[inferred: the integral ∫₀¹ μ (1 − e^(−τ/μ)) dμ / τ, derived here]``. τ is the
absorption part of the V-band optical depth, (1 − albedo_V) τ_V, and it is applied to the
whole bolometric light: **the absorption is grey at V**. Young stars' ultraviolet is absorbed
more strongly than that and the old stars' red light less, so the absorbed power is wrong in
both directions by an amount this stage does not know; the report of S31 measures one side of it
and the debt is recorded there. Scattering is taken to remove no energy and to lengthen no path.

The dust then emits that power as a modified blackbody, κ_ν = κ₀ (ν/ν₀)^β, optically thin in
the infrared. Its power per unit dust mass, 4π ∫ κ_ν B_ν(T) dν, is analytic,

    4π κ₀ ν₀^(−β) (2h/c²) (kT/h)^(4+β) Γ(4+β) ζ(4+β),

so the temperature is that equation inverted for the absorbed power per unit dust mass — one
line, no fit and no assumed temperature. The published infrared surface brightness is *not* that
line run backwards: it is the emission spectrum (:func:`emission_per_mass`, the function a renderer
evaluates) integrated over wavelength by quadrature, so the energy balance the suite asserts
compares two computations (rule B3).

**The radiation field G₀** is the far-ultraviolet flux at the midplane over Habing's. The light
stage has no far-ultraviolet band, so the ultraviolet is the star formation rate's, through
Kennicutt & Evans 2012's calibration (the same table the Hα constant is read from), taken flat in
νL_ν across the Habing band 6–13.6 eV ``[inferred]``; the midplane flux of a uniform slab of
absorption depth τ emitting Σ in total is Σ (1 − E₂(τ/2)) / τ ``[inferred: derived as above]``.

**PAHs** (ruling (c)). The metallicity dependence enters because a source for it was read:
Rémy-Ruyer et al. 2015's eq. 5, fitted across 109 galaxies, applied per radius to the gas's
abundance exactly as the ISM stage applies their dust-to-gas law, and held flat above the most
metal-rich galaxy it was fitted to (:func:`pah_mass_fraction`). Draine & Li 2007's constant Milky
Way value is the named alternative.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.special import expn
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.massive_stars import BOLTZMANN, ELECTRON_VOLT, LIGHT_SPEED, PLANCK, SOLAR_LUMINOSITY

# --- conversions, cgs ---------------------------------------------------------------------
# The parsec is 648000/π au with the au the IAU 2012 exact 149 597 870 700 m (IAU 2015 B2); the
# solar mass is the IAU 2015 nominal GM☉ over CODATA's G [recall]. L☉ is massive_stars'.
CM_PER_PC = 3.0856775814913673e18
GRAMS_PER_MSUN = 1.98847e33
MAGNITUDES_PER_OPTICAL_DEPTH = 2.5 * math.log10(math.e)  # A = 1.0857 τ: a definition
MICRON_CM = 1.0e-4
# Lsun/pc² in erg s⁻¹ cm⁻², and a dust mass's power in Lsun/Msun from erg s⁻¹ g⁻¹.
FLUX_PER_LSUN_PC2 = SOLAR_LUMINOSITY / CM_PER_PC**2
LSUN_PER_MSUN_PER_CGS = GRAMS_PER_MSUN / SOLAR_LUMINOSITY
# The Habing band's edges (Habing 1968's 6–13.6 eV): its width in ln ν, for a flat νL_ν.
HABING_BAND_LN_WIDTH = math.log(13.6 / 6.0)

# The wavelengths the emission is integrated over: 1 µm to 1 m, log-spaced. At 2 K the modified
# blackbody peaks near 2 mm, and at 60 K the short end sits 80 e-folds past the Wien cut.
EMISSION_WAVELENGTHS_UM = np.geomspace(1.0, 1.0e6, 6001)


# --- the physics, as functions -------------------------------------------------------------


def optical_depth(extinction_mag: np.ndarray) -> np.ndarray:
    """τ from an extinction in magnitudes: A = 2.5 log₁₀(e) τ."""
    return np.asarray(extinction_mag, dtype=float) / MAGNITUDES_PER_OPTICAL_DEPTH


def slab_absorbed_fraction(tau: np.ndarray) -> np.ndarray:
    """1 − P_esc(τ) of a uniform, isotropically emitting slab of total vertical absorption depth τ.

    P_esc = (1/2 − E₃(τ)) / τ. Below τ = 10⁻³ the difference loses digits, so the series
    (τ/2)(ln(1/τ) + 3/2 − γ) + τ²/6 is used there (the next term is O(τ³ ln τ)).
    """
    tau = np.asarray(tau, dtype=float)
    out = np.zeros_like(tau)
    thin = (tau > 0.0) & (tau < 1e-3)
    thick = tau >= 1e-3
    t = tau[thin]
    out[thin] = 0.5 * t * (np.log(1.0 / t) + 1.5 - 0.5772156649015329) + t * t / 6.0
    t = tau[thick]
    out[thick] = 1.0 - (0.5 - expn(3, t)) / t
    return out


def slab_midplane_flux(emitted: np.ndarray, tau: np.ndarray) -> np.ndarray:
    """4πJ at the midplane of a uniform slab emitting ``emitted`` per unit area in total (both
    faces) with total vertical absorption depth τ: emitted × (1 − E₂(τ/2)) / τ.

    Diverges as ln(1/τ) when τ → 0 — the infinite slab's grazing rays — so it is evaluated only
    where there is dust; zero where there is none.
    """
    emitted = np.asarray(emitted, dtype=float)
    tau = np.asarray(tau, dtype=float)
    out = np.zeros(np.broadcast(emitted, tau).shape)
    ok = tau > 0.0
    t = np.broadcast_to(tau, out.shape)[ok]
    out[ok] = np.broadcast_to(emitted, out.shape)[ok] * (1.0 - expn(2, 0.5 * t)) / t
    return out


def _zeta(s: float) -> float:
    """Riemann ζ(s) for s > 1: forty terms and the Euler–Maclaurin tail to s(s+1)(s+2) — below
    10⁻¹⁴ relative for s ≥ 4 [inferred: the next correction is ~N^(−s−5))."""
    n = 40
    head = sum(k ** (-s) for k in range(1, n))
    tail = n ** (1 - s) / (s - 1) + 0.5 * n ** (-s) + s * n ** (-s - 1) / 12.0 - s * (s + 1) * (s + 2) * n ** (-s - 3) / 720.0
    return head + tail


def emitted_power_coefficient(kappa_ref: float, wavelength_ref_um: float, beta: float) -> float:
    """A in P/M = A T^(4+β), erg s⁻¹ g⁻¹ K^−(4+β): 4π κ₀ ν₀^(−β) (2h/c²)(k/h)^(4+β) Γ(4+β) ζ(4+β)."""
    nu0 = LIGHT_SPEED / (wavelength_ref_um * MICRON_CM)
    p = 4.0 + beta
    return (4.0 * math.pi * kappa_ref * nu0 ** (-beta) * 2.0 * PLANCK / LIGHT_SPEED**2
            * (BOLTZMANN / PLANCK) ** p * math.gamma(p) * _zeta(p))


def dust_temperature(power_per_mass: np.ndarray, kappa_ref: float, wavelength_ref_um: float, beta: float) -> np.ndarray:
    """The temperature at which a unit dust mass emits ``power_per_mass`` (erg s⁻¹ g⁻¹); 0 where it
    absorbs nothing."""
    power = np.asarray(power_per_mass, dtype=float)
    a = emitted_power_coefficient(kappa_ref, wavelength_ref_um, beta)
    return np.where(power > 0.0, (np.maximum(power, 0.0) / a) ** (1.0 / (4.0 + beta)), 0.0)


def emission_per_mass(wavelength_um: np.ndarray, temperature: np.ndarray, kappa_ref: float,
                      wavelength_ref_um: float, beta: float) -> np.ndarray:
    """The dust's emission spectrum: L_ν per unit dust mass, 4π κ_ν B_ν(T), erg s⁻¹ Hz⁻¹ g⁻¹.

    Broadcasts ``temperature[..., None]`` against ``wavelength_um``. The function a renderer
    evaluates for the dust component (RENDER_PHYSICS §3a: Σ_dust, T_dust, β per cell).
    """
    lam = np.asarray(wavelength_um, dtype=float) * MICRON_CM
    nu = LIGHT_SPEED / lam
    T = np.asarray(temperature, dtype=float)[..., None]
    kappa = kappa_ref * (wavelength_ref_um * MICRON_CM / lam) ** beta
    x = np.where(T > 0.0, PLANCK * nu / (BOLTZMANN * np.where(T > 0.0, T, 1.0)), np.inf)
    with np.errstate(over="ignore"):
        planck = np.where(np.isfinite(x) & (x < 700.0), 2.0 * PLANCK * nu**3 / LIGHT_SPEED**2 / np.expm1(np.minimum(x, 700.0)), 0.0)
    return 4.0 * math.pi * kappa * planck


def emitted_per_mass(temperature: np.ndarray, kappa_ref: float, wavelength_ref_um: float, beta: float) -> np.ndarray:
    """∫ :func:`emission_per_mass` dν over ``EMISSION_WAVELENGTHS_UM`` by the trapezoid in ln ν,
    erg s⁻¹ g⁻¹: the spectrum's own power, integrated, not the closed form."""
    lam = EMISSION_WAVELENGTHS_UM
    nu = LIGHT_SPEED / (lam * MICRON_CM)
    per_nu = emission_per_mass(lam, temperature, kappa_ref, wavelength_ref_um, beta)
    # dν = ν d ln ν = −ν d ln λ, and ν runs down the ascending wavelength grid, so the integral over
    # rising ν is the integral over rising ln λ with the sign absorbed.
    return np.trapezoid(per_nu * nu, np.log(lam), axis=-1)


def pah_mass_fraction(feh: np.ndarray, sigma_dust: np.ndarray, galactic: float, intercept: float, slope: float,
                      solar_oxygen: float, z_max: float) -> np.ndarray:
    """The PAH share of the dust mass from the gas abundance (ruling (c)): Rémy-Ruyer et al. 2015's
    eq. 5, log f_PAH = intercept + slope × (12 + log(O/H)), f_PAH in units of the Galactic fraction.

    12 + log(O/H) is the Sun's on the relation's scale plus the gas's [Fe/H] (oxygen tracks iron, as
    in the ISM stage), held at the most metal-rich galaxy the relation was fitted to — not
    extrapolated above it. Zero where there is no dust. One function, so the constant alternative
    (Draine & Li 2007's Milky Way value everywhere) is a substitution (D114).
    """
    feh = np.nan_to_num(np.asarray(feh, dtype=float), nan=-10.0, neginf=-10.0, posinf=math.log10(z_max))
    abundance = solar_oxygen + np.minimum(feh, math.log10(z_max))
    q = galactic * 10.0 ** (intercept + slope * abundance)
    return np.where(np.asarray(sigma_dust, dtype=float) > 0.0, q, 0.0)


# --- declarations -------------------------------------------------------------

SCATTERING_DEPTH = FieldDecl(
    name="dust_scattering_optical_depth", label="V-band scattering optical depth τ_sca(R), face-on",
    unit="dimensionless", kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), meaningful_zero=True,
    about=(
        "The part of the face-on V-band optical depth through the whole disc that scatters rather than "
        "absorbs: the grain model's V albedo, 0.677 (Draine's R_V = 3.1 Milky Way dust), times τ_V = "
        "A_V / 1.0857. Two thirds of what dust takes out of a V-band ray it throws somewhere else, mostly "
        "forward, which is what lights a dust lane's rim and puts a blue haze round a disc. The light a "
        "line of sight gains from it is the renderer's integral; this is the per-radius quantity it needs."
    ),
)
COLOUR_EXCESS = FieldDecl(
    name="dust_colour_excess_b_v", label="Colour excess E(B − V)(R), face-on", unit="mag",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), meaningful_zero=True,
    about=(
        "A_V over R_V = 3.1, the grain model's ratio of total to selective extinction: how much redder "
        "than it was the light through the whole disc face-on comes out, in B − V. A_B = A_V + E(B − V), "
        "so this is the extinction law's shape between B and V in one number per radius."
    ),
)
SCATTERING_ASYMMETRY = FieldDecl(
    name="dust_scattering_asymmetry", label="Scattering asymmetry g = ⟨cos θ⟩ (V band)",
    unit="dimensionless", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The mean cosine of the angle V-band light is scattered through, 0.538 for Draine's R_V = 3.1 Milky "
        "Way grain model: strongly forward, so a dust lane's rim is bright when the light behind it comes "
        "towards the viewer and dim otherwise. One number for the whole galaxy, published because the "
        "renderer's phase function needs it and the API publishes no constants."
    ),
)
ABSORBED = FieldDecl(
    name="dust_absorbed_surface_brightness", label="Starlight absorbed by dust Σ_abs(R)", unit="Lsun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "The disc's starlight per square parsec that the dust at that radius absorbs: disc_surface_brightness "
        "times the probability that light emitted isotropically in a uniform mixed slab does not escape it, "
        "(1/2 − E₃(τ))/τ subtracted from one, τ the V-band absorption depth (1 − albedo) τ_V. Grey at V: "
        "the young stars' ultraviolet is absorbed more than that and the old stars' red light less, so this "
        "is not exact in either direction. The bulge's light heats nothing here (it has no radial profile)."
    ),
)
TEMPERATURE = FieldDecl(
    name="dust_temperature", label="Dust temperature T_d(R)", unit="K",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno"), meaningful_zero=False,
    about=(
        "The temperature at which a modified blackbody (β = 1.62, Planck's all-sky value; opacity 16.4 cm²/g "
        "at 156 µm from Draine's grain model) emits exactly what the dust at that radius absorbs per unit "
        "mass — the heating balance solved, not fitted and not assumed. Rises slowly, as the 5.6th root of "
        "the heating: a hundred times the light is only 2.3 times hotter. NaN where the dust absorbs nothing."
    ),
)
INFRARED = FieldDecl(
    name="dust_infrared_surface_brightness", label="Dust infrared emission Σ_IR(R)", unit="Lsun/pc2",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about=(
        "What the dust re-emits per square parsec: dust_surface_density times the modified blackbody's "
        "spectrum at dust_temperature, integrated over 1 µm – 1 m by quadrature — the spectrum a renderer "
        "draws, integrated, rather than the temperature's own equation run backwards, so that the suite's "
        "energy-balance test compares two computations. Optically thin in the infrared. Equal to the "
        "absorbed starlight at every radius to the quadrature's precision; nothing else heats the dust."
    ),
)
ABSORBED_TOTAL = FieldDecl(
    name="dust_absorbed_luminosity", label="Starlight absorbed by dust", unit="Lsun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about="dust_absorbed_surface_brightness integrated over the disc, 2πR dR: one side of the energy balance.",
)
INFRARED_TOTAL = FieldDecl(
    name="dust_infrared_luminosity", label="Dust infrared luminosity L_IR", unit="Lsun", kind=Kind.SCALAR,
    meaningful_zero=True,
    about=(
        "dust_infrared_surface_brightness integrated over the disc, 2πR dR: the other side. The disc's own "
        "starlight is its only heat source, so it is a share of disc_luminosity — and grey absorption at V "
        "makes the share uncertain, since the young stars' ultraviolet is absorbed more."
    ),
)
G0 = FieldDecl(
    name="radiation_field_g0", label="Far-ultraviolet radiation field G0(R), Habing units", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    about=(
        "The 6–13.6 eV flux at the midplane over Habing's 1968 interstellar value, 1.6 × 10⁻³ erg cm⁻² s⁻¹. "
        "The light stage has no far-ultraviolet band, so the ultraviolet is today's star formation times "
        "Kennicutt & Evans 2012's far-ultraviolet calibration, taken flat in νL_ν across the band (an "
        "assumption, not a spectrum), and the flux at the midplane of a uniform slab of that emission and "
        "the grain model's far-ultraviolet absorption. What sets the PAHs' excitation and the "
        "photodissociation regions' chemistry; the local field is quoted near 1.7."
    ),
)
PAH = FieldDecl(
    name="pah_fraction", label="PAH mass fraction q_PAH(R)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis"), meaningful_zero=True,
    about=(
        "The fraction of the dust mass in polycyclic aromatic hydrocarbons, from the gas's abundance by "
        "Rémy-Ruyer et al. 2015's relation across 109 galaxies (log f_PAH rising 1.30 per dex of "
        "12 + log(O/H), 0.35 dex of scatter, in units of the Galactic 4.57%), oxygen taken to track iron. "
        "Held flat above 1.2 times solar, the most metal-rich galaxy the relation was fitted to, so the "
        "inner disc is not extrapolated. At solar abundance it reads 9.06%, twice Draine & Li's 4.58% for "
        "the Milky Way itself (0.30 dex, inside the scatter); the metal-poor outer disc falls to a few "
        "tenths of a per cent, which is what makes a metal-poor galaxy's infrared look different."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    sigma_light = np.asarray(ctx.fields["disc_surface_brightness"], dtype=float)  # Lsun/pc²
    sigma_dust = np.asarray(ctx.fields["dust_surface_density"], dtype=float)  # Msun/pc²
    a_v = np.asarray(ctx.fields["dust_extinction_v"], dtype=float)  # mag, face-on, through the whole disc
    sfr = np.asarray(ctx.fields["sfr_surface_density"], dtype=float)  # Msun/yr/kpc²
    feh = np.asarray(ctx.fields["feh_gas"], dtype=float)

    albedo_v = float(c["DUST_ALBEDO_V"])
    tau_v = optical_depth(a_v)
    kappa0, lam0, beta = float(c["DUST_OPACITY_REFERENCE"]), float(c["DUST_OPACITY_WAVELENGTH"]), float(c["DUST_EMISSIVITY_INDEX"])

    # The heating: the starlight the slab keeps, grey at V's absorption depth.
    absorbed = sigma_light * slab_absorbed_fraction((1.0 - albedo_v) * tau_v)  # Lsun/pc²
    heated = (sigma_dust > 0.0) & (absorbed > 0.0)
    per_mass = np.where(heated, absorbed / np.where(heated, sigma_dust, 1.0), 0.0) / LSUN_PER_MSUN_PER_CGS  # erg/s/g
    temperature = np.where(heated, dust_temperature(per_mass, kappa0, lam0, beta), np.nan)
    emitted = np.zeros_like(absorbed)
    emitted[heated] = sigma_dust[heated] * emitted_per_mass(temperature[heated], kappa0, lam0, beta) * LSUN_PER_MSUN_PER_CGS

    # The far-ultraviolet field at the midplane, in Habing's units.
    fuv = sfr * float(c["FUV_LUMINOSITY_PER_SFR"]) / PC_PER_KPC**2 * HABING_BAND_LN_WIDTH  # Lsun/pc², 6–13.6 eV
    tau_fuv = (1.0 - float(c["DUST_ALBEDO_FUV"])) * float(c["DUST_EXTINCTION_RATIO_FUV"]) * tau_v
    g0 = slab_midplane_flux(fuv, tau_fuv) * FLUX_PER_LSUN_PC2 / float(c["HABING_FLUX"])

    area = 2.0 * math.pi * R * PC_PER_KPC**2  # pc² per kpc of radius
    return {
        "dust_scattering_optical_depth": albedo_v * tau_v,
        "dust_colour_excess_b_v": a_v / float(c["DUST_R_V"]),
        "dust_scattering_asymmetry": float(c["DUST_SCATTERING_G"]),
        "dust_absorbed_surface_brightness": absorbed,
        "dust_temperature": temperature,
        "dust_infrared_surface_brightness": emitted,
        "dust_absorbed_luminosity": float(np.trapezoid(absorbed * area, R)),
        "dust_infrared_luminosity": float(np.trapezoid(emitted * area, R)),
        "radiation_field_g0": g0,
        "pah_fraction": pah_mass_fraction(
            feh, sigma_dust, float(c["PAH_FRACTION_GALACTIC"]), float(c["PAH_METALLICITY_INTERCEPT"]),
            float(c["PAH_METALLICITY_SLOPE"]), float(c["OXYGEN_ABUNDANCE_SOLAR"]), float(c["PAH_METALLICITY_MAX"]),
        ),
    }


DUST = IMPLEMENTATIONS.register(
    Stage(
        id="dust",
        slot="dust",
        checkpoint=4,
        about=(
            "What the dust does with the starlight it sits in: scatters two thirds of what it takes out of a "
            "V-band ray, absorbs the rest and re-emits it in the far infrared at the temperature where the "
            "two balance, and carries PAHs in a far-ultraviolet field set by today's star formation. One "
            "grain model throughout (Draine's Milky Way R_V = 3.1); no input, no seed."
        ),
        compute=compute,
        reads_constants=(
            "DUST_R_V", "DUST_ALBEDO_V", "DUST_SCATTERING_G", "DUST_EXTINCTION_RATIO_FUV", "DUST_ALBEDO_FUV",
            "DUST_OPACITY_REFERENCE", "DUST_OPACITY_WAVELENGTH", "DUST_EMISSIVITY_INDEX",
            "FUV_LUMINOSITY_PER_SFR", "HABING_FLUX", "PAH_FRACTION_GALACTIC", "PAH_METALLICITY_INTERCEPT",
            "PAH_METALLICITY_SLOPE", "OXYGEN_ABUNDANCE_SOLAR", "PAH_METALLICITY_MAX",
        ),
        requires=("disc_surface_brightness", "dust_surface_density", "dust_extinction_v", "sfr_surface_density", "feh_gas"),
        publishes=(
            SCATTERING_DEPTH, COLOUR_EXCESS, SCATTERING_ASYMMETRY, ABSORBED, TEMPERATURE, INFRARED,
            ABSORBED_TOTAL, INFRARED_TOTAL, G0, PAH,
        ),
    )
)
