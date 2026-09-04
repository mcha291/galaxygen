"""Chemistry, advanced: two elements, a delay-time distribution, outflows, conservative migration (checkpoint 3).

The simple model's chemistry (``chemistry.py``) has one abundance and returns it
in the timestep that made it. This implementation of the same slot differs on
exactly the three axes GALAXY_INPUTS.md §8 gives the advanced model, and shares
everything else — the gas, star formation and infall histories the sfh stage
published are read unchanged.

**Two elements and a delay.** Iron and oxygen are tracked separately, and
iron has two sources with different clocks: core-collapse supernovae return it
promptly with the oxygen, type Ia supernovae return it after a delay drawn from
a delay-time distribution ``DTD(τ) ∝ τ^-DTD_INDEX`` from ``DTD_MIN_DELAY`` on.
The ratio [α/Fe] therefore starts on a plateau set by the core-collapse yields
alone and falls as the Ia iron arrives — and a population that formed its stars
before the fall is α-enhanced. That is the whole of acceptance row 24, and it is
why the simple model cannot answer it (rule B3, debt #9).

**The DTD is binned at a fixed resolution, not the grid's.** A convolution over
every earlier timestep is quadratic in N_t, and GALAXY_INPUTS.md §10 measured
the naive form at exponent 2.07 and the deposit-forward "fix" at 1.82. The
scheme here bins the DTD into ``DTD_BINS`` delays whatever N_t is, so the Ia
rate at a timestep is a sum over ``DTD_BINS`` shifted copies of the star
formation history: linear in N_t, and the bin count is a numerical resolution
choice rather than a physics constant. ``tools/scaling.py`` measures the exponent
rather than asserting it (rule B7).

**Outflows are metal-loaded and set by the escape velocity.** The fresh metals a
generation makes are hot supernova ejecta, and a fraction of them leave the
disc before they mix. That fraction is a function of how deep the local well is,

    f_esc(R) = 1 / (1 + (v_esc(R) / WIND_SPEED)^WIND_INDEX),

with ``v_esc`` computed from the model's own potential — the halo's, plus the
midplane potential of the resolved baryons — rather than assumed. The inner disc
keeps more of what it makes than the outer disc, which is the differential
metal loss debt #15 predicted would tilt the gradient. What this does *not* do
is remove gas: the wind's mass is the ejecta's, small against the accretion,
and the gas budget stays the sfh stage's (debt #26). The simple model's
``NET_YIELD`` is this mechanism with ``f_esc`` folded in at one radius: the
nucleosynthetic yields here are three times it, and the effective yield at R₀
is a *result* of this stage rather than its input (debt #16, rule B10).

**Migration conserves what it moves.** The same Gaussian in birth radius as the
simple model, with the same input width, but applied to stellar *mass* and the
iron and oxygen that mass carries, per age bin, rather than to a mean. So the
outer disc's old stars are migrants with inner-disc abundances, and the solar
neighbourhood holds a *distribution* of [Fe/H] and [α/Fe] rather than one value
each. Row 24 is judged on that distribution: two modes with a valley between
them, and the α-rich mode spanning a wide range of [Fe/H]. The valley is also
where the advanced model's thin/thick split lives (``vertical_alpha``), so the
thick disc no longer names the merger (debt #20).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages import chemistry as simple
from galaxy.stages.chemistry import MIGRATION_REFERENCE_AGE, OLD_MIN_AGE, YOUNG_MAX_AGE, gradient
from galaxy.stages.disc import PC_PER_KPC

# Numerical resolution choices, not physics: the delay kernel's bin count (fixed
# whatever N_t, which is the whole point), the age bins migration is applied in,
# and the [α/Fe] histogram the bimodality is read off.
DTD_BINS = 32
AGE_BIN = 0.5  # Gyr; 1.0 and 10.0 are bin edges, so the young/old selections are exact
ALPHA_HIST = (-0.3, 0.7, 0.02)  # lo, hi, bin width in dex
PEAK_SEPARATION = 0.1  # dex; two maxima closer than this are one mode
DIP_DEPTH = 0.5  # the valley must fall to at most this fraction of the lower peak
MODE_MIN_SHARE = 0.1  # a mode holds at least this share of the mass within ±PEAK_SEPARATION/2 of its peak
WIDE_SPAN = 0.5  # dex; the α-rich mode must span at least this much [Fe/H] (5th–95th)


# --- the delay-time distribution --------------------------------------------


def dtd_bins(t_min: float, t_max: float, index: float, n_bins: int = DTD_BINS) -> tuple[np.ndarray, np.ndarray]:
    """Delays and weights: ``n_bins`` log-spaced bins of ``τ^-index`` on ``[t_min, t_max]``.

    Weights integrate the power law over each bin and sum to one, so the whole
    Ia iron budget per unit mass formed is ``Y_FE_IA`` however the bins fall.
    """
    edges = np.geomspace(t_min, t_max, n_bins + 1)
    if index == 1.0:
        mass = np.log(edges[1:] / edges[:-1])
    else:
        p = 1.0 - index
        mass = (edges[1:] ** p - edges[:-1] ** p) / p
    weights = mass / mass.sum()
    delays = np.sqrt(edges[1:] * edges[:-1])
    return delays, weights


def snia_rate(psi: np.ndarray, dt: float, delays: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Mass formed per unit time whose type Ia supernovae are exploding at each timestep.

    ``psi`` is ``(R, t)``; the result has the same shape and units, and multiplied
    by ``Y_FE_IA`` is the Ia iron production rate. Each delay bin shifts the star
    formation history by a whole number of timesteps (at least one), so this is
    ``len(delays)`` vector operations rather than a convolution over the past.
    """
    out = np.zeros_like(psi)
    n_t = psi.shape[1]
    for tau, w in zip(delays, weights):
        s = max(1, int(round(tau / dt)))
        if s < n_t:
            out[:, s:] += w * psi[:, : n_t - s]
    return out


# --- the potential the wind has to climb out of ------------------------------


def escape_velocity(
    phi_halo: np.ndarray, v_total: np.ndarray, v_halo: np.ndarray, R: np.ndarray, baryons: float, G: float
) -> np.ndarray:
    """Midplane escape speed from the halo potential plus the resolved baryons' own.

    In the plane ``dΦ/dR = v_c²/R`` by definition, so the baryonic potential
    relative to the grid edge is the integral of ``v_b²/R`` outward, and beyond
    the edge the disc is a point mass. ``v_b² = v_total² − v_halo²`` because the
    sfh stage adds the two in quadrature.
    """
    v_b2 = np.maximum(v_total**2 - v_halo**2, 0.0)
    f = v_b2 / np.maximum(R, 1e-9)
    seg = 0.5 * (f[1:] + f[:-1]) * np.diff(R)
    outward = np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])
    phi_b = -outward - G * baryons / R[-1]
    return np.sqrt(np.maximum(-2.0 * (phi_halo + phi_b), 0.0))


# --- the abundance distribution at one radius --------------------------------


def transport(R: np.ndarray, sigma: float) -> np.ndarray:
    """Row-normalised Gaussian kernel: fraction of ring i's stars now found in ring j."""
    if sigma <= 0.0:
        return np.eye(R.size)
    k = np.exp(-0.5 * ((R[None, :] - R[:, None]) / sigma) ** 2)
    return k / k.sum(axis=1, keepdims=True)


def weighted_percentile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    v, w = values[order], weights[order]
    c = np.cumsum(w)
    if c[-1] <= 0.0:
        return float("nan")
    return float(np.interp(q * c[-1], c, v))


def bimodality(afe: np.ndarray, feh: np.ndarray, weight: np.ndarray) -> tuple[str, float, float, float]:
    """(category, valley [α/Fe], dip depth, [Fe/H] span of the α-rich mode).

    Two modes means two local maxima of the mass histogram at least
    ``PEAK_SEPARATION`` apart, each holding ``MODE_MIN_SHARE`` of the mass around
    it (a bump on a tail is not a mode), whose valley falls to ``DIP_DEPTH`` of
    the lower peak or less. The valley is where the thin/thick split goes; NaN if
    there is none, because a missing valley is not a valley at zero (rule B9).
    """
    ok = np.isfinite(afe) & np.isfinite(feh) & (weight > 0.0)
    afe, feh, weight = afe[ok], feh[ok], weight[ok]
    lo, hi, width = ALPHA_HIST
    edges = np.arange(lo, hi + width / 2, width)
    hist, _ = np.histogram(afe, bins=edges, weights=weight)
    centres = 0.5 * (edges[1:] + edges[:-1])
    if hist.sum() <= 0.0:
        return "single", float("nan"), 0.0, 0.0
    # Local maxima that hold a real share of the mass, tallest first, kept only if
    # clear of every taller one.
    half = max(1, int(round(0.5 * PEAK_SEPARATION / width)))
    total = hist.sum()
    idx = [i for i in range(hist.size) if hist[i] > 0.0
           and (i == 0 or hist[i] >= hist[i - 1]) and (i == hist.size - 1 or hist[i] > hist[i + 1])
           and hist[max(0, i - half) : i + half + 1].sum() >= MODE_MIN_SHARE * total]
    idx.sort(key=lambda i: -hist[i])
    peaks: list[int] = []
    for i in idx:
        if all(abs(centres[i] - centres[j]) >= PEAK_SEPARATION for j in peaks):
            peaks.append(i)
        if len(peaks) == 2:
            break
    if len(peaks) < 2:
        return "single", float("nan"), 0.0, 0.0
    a, b = sorted(peaks)
    valley = a + int(np.argmin(hist[a : b + 1]))
    depth = 1.0 - float(hist[valley] / min(hist[a], hist[b]))
    if depth < DIP_DEPTH:
        return "single", float("nan"), depth, 0.0
    split = float(centres[valley])
    rich = afe >= split
    span = weighted_percentile(feh[rich], weight[rich], 0.95) - weighted_percentile(feh[rich], weight[rich], 0.05)
    return ("bimodal_wide" if span >= WIDE_SPAN else "bimodal_narrow"), split, depth, float(span)


# --- declarations -------------------------------------------------------------

# Same contract as the simple model's, so preflight reconciles them; the about
# line is this stage's own, because what is behind the name has changed.
METALLICITY_HISTORY = replace(simple.METALLICITY_HISTORY, about=(
    "Total metal mass fraction in the gas: core-collapse metals in solar proportions to the "
    "oxygen, plus the iron-peak ejecta of type Ia supernovae, less what the wind removed."
))
FEH_HISTORY = replace(simple.FEH_HISTORY, about=(
    "log10(Z_Fe/Z_Fe☉), iron proper rather than total metallicity as a proxy for it. Two "
    "sources with two clocks: prompt core-collapse iron and delayed Ia iron. −inf where no "
    "metals exist, never a floor (rule B9)."
))
FEH_GAS = replace(simple.FEH_GAS, about=(
    "Present-day gas iron. The level at R₀ is a result of the wind's escape fraction there, "
    "not of a calibrated yield; row 22 is fitted to this over 4–12 kpc."
))
FEH_STARS_YOUNG = replace(simple.FEH_STARS_YOUNG, about=(
    "Mass-weighted mean [Fe/H] of the stars now at R that are younger than 1 Gyr, after "
    "migration has moved them — which at this age is hardly at all."
))
FEH_STARS_OLD = replace(simple.FEH_STARS_OLD, about=(
    "Mass-weighted mean [Fe/H] of the stars now at R older than 10 Gyr. Beyond the disc they "
    "formed in these are migrants, carrying inner-disc abundances outward."
))
METALLICITY_GRADIENT = replace(simple.METALLICITY_GRADIENT, about=(
    "Acceptance row 22. Two tilts add here: the differential infall the simple model has, and "
    "the differential metal loss of a wind that escapes the outer disc more easily (debt #15)."
))
GRADIENT_YOUNG = replace(simple.GRADIENT_YOUNG, about="Acceptance row 23's young end, on the migrated young population.")
GRADIENT_OLD = replace(simple.GRADIENT_OLD, about=(
    "Acceptance row 23's old end, on the migrated old population; flatter than the young end "
    "because the old stars have moved furthest and the outer disc's old stars came from inside."
))

ALPHA_FE_HISTORY = FieldDecl(
    name="alpha_fe_history", label="[α/Fe](R, t)", unit="dex", kind=Kind.FIELD, axes=("R", "t"),
    ramp=Ramp("viridis", scale="linear", lo=-0.1, hi=0.5), meaningful_zero=True, optional=True,
    about=(
        "[O/H] − [Fe/H] of the gas. Starts on the core-collapse plateau and falls as the delayed "
        "Ia iron arrives; where star formation was fast the fall is late and the stars formed "
        "before it are α-enhanced. Advanced model only: the simple model has one abundance."
    ),
)
ALPHA_FE_GAS = FieldDecl(
    name="alpha_fe_gas", label="Present-day gas [α/Fe](R)", unit="dex", kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=-0.1, hi=0.5), meaningful_zero=True, optional=True,
    about="Near solar across the star-forming disc: the Ia iron has had time to arrive everywhere.",
)
ALPHA_FE_STARS = FieldDecl(
    name="alpha_fe_stars", label="Mean stellar [α/Fe](R)", unit="dex", kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=-0.1, hi=0.5), meaningful_zero=True, optional=True,
    about="Mass-weighted over every star now at R, migrants included. Rises inward, where the old stars are.",
)
ESCAPE_VELOCITY = FieldDecl(
    name="escape_velocity", label="Midplane escape velocity", unit="km/s", kind=Kind.FIELD, axes=("R",),
    ramp=Ramp("viridis", scale="linear", lo=300.0, hi=800.0), meaningful_zero=True, optional=True,
    about=(
        "From the halo potential plus the resolved baryons' midplane potential. The local value "
        "is what the wind loading is judged against; the Sun's is commonly put at 530–580 km/s."
    ),
)
METAL_ESCAPE_FRACTION = FieldDecl(
    name="metal_escape_fraction", label="Fraction of fresh metals lost to the wind", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", scale="linear", lo=0.0, hi=1.0), meaningful_zero=True,
    optional=True,
    about=(
        "1/(1 + (v_esc/WIND_SPEED)^WIND_INDEX): the share of a generation's supernova metals that "
        "leaves before mixing. About two thirds at R₀ — which is the factor the simple model's "
        "effective yield was hiding (debt #16) — and more outside."
    ),
)
FEH_SPREAD_SUN = FieldDecl(
    name="feh_spread_sun", label="[Fe/H] dispersion of stars at R₀", unit="dex", kind=Kind.SCALAR,
    meaningful_zero=True, optional=True,
    about=(
        "Mass-weighted standard deviation of [Fe/H] across every star now at the solar radius. "
        "Without migration this is the width of the local age–metallicity relation alone and "
        "comes out far too narrow (GALAXY_INPUTS.md §8); the observed local value is about 0.2 dex."
    ),
)
ALPHA_SPLIT = FieldDecl(
    name="alpha_split", label="[α/Fe] valley between the two sequences at R₀", unit="dex", kind=Kind.SCALAR,
    meaningful_zero=True, optional=True,
    about=(
        "The minimum of the [α/Fe] mass histogram between its two modes. NaN when there is one "
        "mode, which is a real answer (rule B9). This is the advanced model's thin/thick split: "
        "a star born above it is thick-disc, whatever the merger list says (debt #20)."
    ),
)
ALPHA_DIP_DEPTH = FieldDecl(
    name="alpha_dip_depth", label="Depth of the [α/Fe] valley", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, optional=True,
    about="1 − valley/lower peak. Zero for one mode; bimodal needs at least 0.5. Published so the verdict can be read.",
)
HIGH_ALPHA_FEH_SPAN = FieldDecl(
    name="high_alpha_feh_span", label="[Fe/H] span of the α-rich sequence at R₀", unit="dex", kind=Kind.SCALAR,
    meaningful_zero=True, optional=True,
    about=(
        "5th to 95th mass percentile of [Fe/H] among stars above the valley. Row 24 asks for the "
        "thick disc to be α-enhanced *across a wide [Fe/H] range*; wide here is 0.5 dex."
    ),
)
ALPHA_SEQUENCE = FieldDecl(
    name="alpha_sequence", label="[α/Fe] sequences at R₀", unit="dimensionless", kind=Kind.CATEGORY_SCALAR,
    categories=("single", "bimodal_narrow", "bimodal_wide"), meaningful_zero=False, optional=True,
    about=(
        "Acceptance row 24. 'single': one mode. 'bimodal_narrow': two modes but the α-rich one "
        "spans under 0.5 dex of [Fe/H]. 'bimodal_wide': what BHG16 §5.2.2 describes. A merger-free "
        "galaxy's answer is debt #9's experiment, run in tests/test_chemistry_dtd.py."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    R, t = ctx.grid.R, ctx.grid.t
    n_t = t.size
    dt = ctx.grid.spec.t_max / n_t
    c = ctx.constants
    z_sun, fe_sun, o_sun = float(c["SOLAR_METALLICITY"]), float(c["SOLAR_IRON"]), float(c["SOLAR_OXYGEN"])
    y_o, y_fe_cc, y_fe_ia = float(c["Y_O_CC"]), float(c["Y_FE_CC"]), float(c["Y_FE_IA"])
    # Core-collapse metals in solar proportion to their oxygen, so total Z follows
    # from the oxygen yield rather than from a fourth constant; an Ia's ejecta are
    # iron-peak throughout, about twice the iron by mass [recall].
    y_z_cc = y_o * z_sun / o_sun
    y_z_ia = 2.0 * y_fe_ia

    gas = ctx.fields["gas_surface_density_history"]
    psi = ctx.fields["sfr_surface_density_history"]
    infall = ctx.fields["infall_rate_history"]

    delays, weights = dtd_bins(float(c["DTD_MIN_DELAY"]), ctx.grid.spec.t_max, float(c["DTD_INDEX"]))
    ia = snia_rate(psi, dt, delays, weights)

    v_esc = escape_velocity(
        ctx.fields["halo_potential"][:, 0], ctx.fields["circular_velocity_resolved"],
        ctx.fields["halo_circular_velocity"], R, float(ctx.fields["baryon_mass_total"]), float(c["G"]),
    )
    kept = 1.0 - 1.0 / (1.0 + (v_esc / float(c["WIND_SPEED"])) ** float(c["WIND_INDEX"]))

    species = np.zeros((3, R.size))  # Z, Fe, O mass fractions of the gas
    hist = np.empty((3, R.size, n_t))
    for j in range(n_t):
        g = gas[:, j]
        prod = PC_PER_KPC * kept * np.stack((
            y_z_cc * psi[:, j] + y_z_ia * ia[:, j],
            y_fe_cc * psi[:, j] + y_fe_ia * ia[:, j],
            y_o * psi[:, j],
        ))
        safe = np.where(g > 0.0, g, 1.0)
        dZ = np.where(g > 0.0, (prod - species * infall[:, j]) / safe, 0.0)
        species = np.clip(species + dZ * dt, 0.0, 1.0)
        hist[:, :, j] = species

    with np.errstate(divide="ignore", invalid="ignore"):
        feh_hist = np.log10(np.where(hist[1] > 0.0, hist[1], np.nan) / fe_sun)
        oh_hist = np.log10(np.where(hist[2] > 0.0, hist[2], np.nan) / o_sun)
    afe_hist = oh_hist - feh_hist

    # --- stars: formed, then moved, carrying their birth abundances ----------
    age = ctx.grid.spec.t_max - t
    width = float(ctx.inputs["migration_efficiency"])
    formed = PC_PER_KPC * psi * dt * (2.0 * math.pi * R * ctx.grid["R"].width * PC_PER_KPC**2)[:, None]  # M☉ per ring per step
    feh_b, afe_b = np.nan_to_num(feh_hist, nan=-99.0), np.nan_to_num(afe_hist, nan=0.0)
    edges = np.arange(0.0, ctx.grid.spec.t_max + AGE_BIN, AGE_BIN)
    at_sun = int(np.argmin(np.abs(R - float(c["R_SUN"]))))

    mass_now = np.zeros((edges.size - 1, R.size))
    feh_now = np.zeros_like(mass_now)  # mass-weighted sums of [Fe/H] and of its square
    feh2_now = np.zeros_like(mass_now)
    afe_now = np.zeros_like(mass_now)
    sun_w, sun_feh, sun_afe = [], [], []
    for b in range(edges.size - 1):
        in_bin = (age >= edges[b]) & (age < edges[b + 1])
        if not in_bin.any():
            continue
        m = formed[:, in_bin]
        if m.sum() <= 0.0:
            continue
        sigma = width * math.sqrt(0.5 * (edges[b] + edges[b + 1]) / MIGRATION_REFERENCE_AGE)
        K = transport(R, sigma)
        mass_b, feh_bin, afe_bin = m.sum(axis=1), feh_b[:, in_bin], afe_b[:, in_bin]
        mass_now[b] = K.T @ mass_b
        feh_now[b] = K.T @ (m * feh_bin).sum(axis=1)
        feh2_now[b] = K.T @ (m * feh_bin**2).sum(axis=1)
        afe_now[b] = K.T @ (m * afe_bin).sum(axis=1)
        # Every (birth ring, birth step) that reaches R₀, for the distribution there.
        w = m * K[:, at_sun][:, None]
        sun_w.append(w.ravel())
        sun_feh.append(feh_bin.ravel())
        sun_afe.append(afe_bin.ravel())

    def mean_feh(rows: np.ndarray) -> np.ndarray:
        m = mass_now[rows].sum(axis=0)
        return np.where(m > 0.0, feh_now[rows].sum(axis=0) / np.where(m > 0.0, m, 1.0), np.nan)

    centres = 0.5 * (edges[1:] + edges[:-1])
    young = mean_feh(centres <= YOUNG_MAX_AGE)
    old = mean_feh(centres >= OLD_MIN_AGE)
    total = mass_now.sum(axis=0)
    safe_total = np.where(total > 0.0, total, 1.0)
    afe_stars = np.where(total > 0.0, afe_now.sum(axis=0) / safe_total, np.nan)
    stars_now = ctx.fields["stellar_surface_density"]

    w_sun = np.concatenate(sun_w) if sun_w else np.zeros(0)
    feh_sun = np.concatenate(sun_feh) if sun_feh else np.zeros(0)
    afe_sun = np.concatenate(sun_afe) if sun_afe else np.zeros(0)
    real = w_sun > 0.0
    if real.any() and w_sun[real].sum() > 0.0:
        mean = np.average(feh_sun[real], weights=w_sun[real])
        spread = math.sqrt(max(np.average((feh_sun[real] - mean) ** 2, weights=w_sun[real]), 0.0))
    else:
        spread = float("nan")
    category, split, depth, span = bimodality(afe_sun, feh_sun, w_sun)

    return {
        "metallicity_history": hist[0],
        "feh_history": feh_hist,
        "alpha_fe_history": afe_hist,
        "feh_gas": feh_hist[:, -1],
        "alpha_fe_gas": afe_hist[:, -1],
        "feh_stars_young": young,
        "feh_stars_old": old,
        "alpha_fe_stars": afe_stars,
        "escape_velocity": v_esc,
        "metal_escape_fraction": 1.0 - kept,
        "metallicity_gradient": gradient(feh_hist[:, -1], R),
        "metallicity_gradient_young": gradient(young, R, stars_now),
        "metallicity_gradient_old": gradient(old, R, stars_now),
        "feh_spread_sun": spread,
        "alpha_split": split,
        "alpha_dip_depth": depth,
        "high_alpha_feh_span": span,
        "alpha_sequence": category,
    }


CHEMISTRY_DTD = IMPLEMENTATIONS.register(
    Stage(
        id="chemistry_dtd",
        slot="chemistry",
        checkpoint=3,
        about=(
            "Iron and oxygen with a type Ia delay-time distribution, a metal-loaded wind set by "
            "the local escape velocity, and mass-conserving radial migration. The advanced model's "
            "chemistry; publishes the simple model's fields under the same contract plus the "
            "[α/Fe] plane, and acceptance row 24 is judged on it."
        ),
        compute=compute,
        reads_inputs=("migration_efficiency",),
        reads_constants=(
            "SOLAR_METALLICITY", "SOLAR_IRON", "SOLAR_OXYGEN",
            "Y_O_CC", "Y_FE_CC", "Y_FE_IA", "DTD_INDEX", "DTD_MIN_DELAY",
            "WIND_SPEED", "WIND_INDEX", "G", "R_SUN",
        ),
        requires=(
            "gas_surface_density_history", "sfr_surface_density_history", "infall_rate_history",
            "stellar_surface_density", "halo_potential", "circular_velocity_resolved",
            "halo_circular_velocity", "baryon_mass_total",
        ),
        publishes=(
            METALLICITY_HISTORY, FEH_HISTORY, ALPHA_FE_HISTORY, FEH_GAS, ALPHA_FE_GAS,
            FEH_STARS_YOUNG, FEH_STARS_OLD, ALPHA_FE_STARS, ESCAPE_VELOCITY, METAL_ESCAPE_FRACTION,
            METALLICITY_GRADIENT, GRADIENT_YOUNG, GRADIENT_OLD,
            FEH_SPREAD_SUN, ALPHA_SPLIT, ALPHA_DIP_DEPTH, HIGH_ALPHA_FEH_SPAN, ALPHA_SEQUENCE,
        ),
    )
)
