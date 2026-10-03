"""Pattern: the bar and the spiral arms (checkpoint 3, ahead of star formation since S25).

Both stages read the checkpoint-1 curve (``circular_velocity``, the halo plus one
exponential) and the λ_d scale length, so the pattern is a consequence of the halo and
disc alone and the star-formation stages can read it (BUILD_II Phase 1, D174). Until
S25 they read ``sfh``'s resolved curve and fitted thin-disc scale length, which put
the pattern behind star formation and made azimuthal star formation impossible.

Two stages, not one, and the reason is a limitation worth naming.
``graph.py`` derives provenance **per stage**: a stage that reads a seed
publishes seeded fields, all of them. But the bar's *length* has no draw in it
while its *pattern speed* does, and acceptance row 15 is pointwise where rows 16
and 17 are statistical — so declaring the length seeded would be a false label on
a reproducible number (rule A10 forbids exactly that vagueness). Splitting the
derived half from the seeded half gets both labels right with the machinery that
exists; making provenance per-field is the alternative, and it is a contract
change that belongs to the audit (DECISIONS.md D55).

**Where the draws come from.** GALAXY_INPUTS.md §4b assigns bar pattern speed and
arm multiplicity to seeded draws rather than to inputs: the residual is real and
nobody would ever choose it. The consequence, stated there and honoured here, is
that the affected acceptance rows become *statistical* — the model must reproduce
the Milky Way within an ensemble, not exactly.

**Which seed.** ``pattern_seed``. GALAXY_INPUTS.md §5 says the pitch dispersion
comes from ``world_seed``, and it cannot: rerolling the arms would then invalidate
every checkpoint from 1 onwards, when the whole point of per-stage seeds is that
rerolling the pattern's stage invalidates what follows it and nothing earlier
(GALAXY_PLAN.md §3; since S25 that is checkpoints 4–6, D174).
The registry and the plan agree on ``pattern_seed``; §5 is the outlier
(DECISIONS.md D56).

**Several arm modes at once (S56, BUILD_III Phase P1; DECISIONS.md D215).** Until S56 the arm
number was one seeded draw, weighted by the swing window at one radius, and the arms one cosine
of that number from the centre to the grid's edge. Since S56 the arm number is not drawn: the
window is evaluated **at every radius** (:func:`local_swing_weights`) and its weights split the
arms' power among m = 2 … 6 there (:func:`mode_law`):

- *The window.* X₂(R) = κ²R / (2πGΣ · 2) with the checkpoint-1 disc's epicyclic frequency and its
  total surface density (stars and gas together: swing amplification is of the whole
  self-gravitating disc), the local shear Γ(R) = 1 − d ln v / d ln R, m_lo = X₂/(Γ x_high),
  m_hi = X₂/(Γ x_low), and w_m(R) the existing :func:`swing_weight`, unchanged.
- *The gain, capped at one.* A_m(R)² = A² · w_m(R) / max(1, Σ_k w_k(R)), A the published
  ``arm_contrast``. Where Σw ≥ 1 the ring carries A² whole, split by the weights; below 1 it
  carries Σw · A², falling continuously to zero where the amplifier is dead. No ring is
  normalised up, there is no fallback where no mode survives, and one fully amplified mode
  carries A² alone and is the single cosine S55 published.
- *The saturation.* The bar's taper multiplies each mode as it multiplied the one arm, and where
  the modes' peak would reach the mean they are scaled down together:
  s(R) = min(1, (1 − b(R)) / Σ_m Ã_m(R)), Ã the tapered amplitudes and b the bar's tapered
  amplitude. s depends on the radius only, so the field is non-negative for every realisation of
  the phases; nothing is floored and nothing is renormalised after composition.
- *The realisation* is not here: where each mode's crests lie is five phases the randomness
  layer draws on ``texture_seed`` (``galaxy/layer/arm_phases.py``). The composed field is
  1 + Σ_m A_m(R) cos(m χ − θ_m) + bar, χ = φ − ln R · cot(pitch): one rigid winding whose
  azimuthal profile changes with radius. θ = 0 for every mode is the convention S55 had.

``arm_multiplicity`` keeps its name as a label - the m carrying the most mass-weighted power -
and **nothing composes a field or places an object from it** (D215, gate ruling 4): every reader
of the pattern reads the modes' amplitudes and phases (:data:`PATTERN_READS`).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose

SHEAR_RADIUS_IN_SCALE_LENGTHS = 2.2  # ruling 3: take the scaled form
# The closed set of arm numbers since S26 (D175): two to ARM_MULTIPLICITY_MAX. From S26 to S55 one of them
# was drawn; since S56 (D215) each is a mode with its own amplitude at every radius. m = 1 is excluded
# (level0, ARM_MULTIPLICITY_MAX's about line).
ARM_MULTIPLICITIES: tuple[float, ...] = (2.0, 3.0, 4.0, 5.0, 6.0)
ARM_MODES: tuple[int, ...] = tuple(int(m) for m in ARM_MULTIPLICITIES)
BAR_CONTRAST_CAP = 0.9  # a cosine bar above this empties its inter-bar sector (BAR_CONTRAST_LOG_SCATTER)
PC_PER_KPC = 1000.0  # a definition: the disc's surface density is published per square parsec


def amplitude_field(m: int) -> str:
    """The radial field holding mode ``m``'s amplitude: what multiplies its cosine in the composed field."""
    return f"arm_mode_amplitude_{int(m)}"


def phase_field(m: int) -> str:
    """The synthetic scalar holding mode ``m``'s phase (the layer's, ``galaxy/layer/arm_phases.py``)."""
    return f"arm_mode_phase_{int(m)}"


AMPLITUDE_FIELDS: tuple[str, ...] = tuple(amplitude_field(m) for m in ARM_MODES)
PHASE_FIELDS: tuple[str, ...] = tuple(phase_field(m) for m in ARM_MODES)
# What the stellar pattern is built from, and so what every stage that places by it requires (S56, D215:
# the modes, never ``arm_multiplicity``).
PATTERN_READS: tuple[str, ...] = ("bar_contrast", "pitch_angle", "bar_half_length", *AMPLITUDE_FIELDS, *PHASE_FIELDS)


def swing_window(disc_dominance: float, shear: float, x_low: float, x_high: float) -> tuple[float, float, float]:
    """(X₂, m_lo, m_hi): Toomre's X for m = 2 in the Mestel form, and the arm numbers the disc amplifies.

    For a flat curve κ² = 2v²/R² and a disc whose own rotation is v_d² = 2πGΣR (Mestel), so
    X_m = κ²R/(2πGΣm) = 2/(m f_d) with f_d = v_d²/v² the disc's share of the rotation — the
    published ``disc_dominance``. Vigorous amplification for x_low < X/Γ < x_high therefore means
    X₂/(Γ x_high) ≤ m ≤ X₂/(Γ x_low), the review's 1/f_d ≲ m ≲ 2/f_d at Γ = 1 [verified:
    Sellwood & Masters 2022 §4.2.3.2]. The alternative is the local form with the exponential
    disc's own Σ(2.2 R_d), which reads X₂ = 2.7 at the defaults and prefers m = 3–4 there; it
    increases outward (D'Onghia 2015: two arms at 4.5 kpc, five or six at R₀), so it needs a
    radius chosen by hand, and the global form was chosen before either number was read (D175).
    **Since S56 (D215) the local form is the law for the arm number** - evaluated at every radius,
    so no radius is chosen (:func:`local_swing_weights`) - and this global form stays as the
    amplitude's coherence input only: D175's choice is superseded for the arm number.
    """
    f_d = min(max(float(disc_dominance), 1e-6), 1.0)
    gamma = float(shear) if math.isfinite(shear) and shear > 0.0 else 1.0
    x2 = 2.0 / f_d
    return x2, x2 / (gamma * x_high), x2 / (gamma * x_low)


def swing_weight(m: float, m_lo: float, m_hi: float, x_high: float, x_dead: float, x_low: float, x_floor: float) -> float:
    """How strongly a disc amplifies an m-fold pattern, 0–1: 1 inside [m_lo, m_hi], falling
    log-linearly to 0 where X reaches x_dead (fewer arms than m_lo) or x_floor (more than m_hi)."""
    if m_lo <= m <= m_hi:
        return 1.0
    if m < m_lo:  # X above the vigorous range: dead at X = x_dead, i.e. at m_lo × x_high / x_dead
        m_dead = m_lo * x_high / x_dead
        return float(min(max(math.log(m / m_dead) / math.log(m_lo / m_dead), 0.0), 1.0)) if m > m_dead else 0.0
    m_dead = m_hi * x_low / x_floor  # X below the range: dead at X = x_floor
    return float(min(max(math.log(m_dead / m) / math.log(m_dead / m_hi), 0.0), 1.0)) if m < m_dead else 0.0


def contrast_amplitude(mag: float) -> float:
    """The cosine amplitude whose peak-to-trough ratio is an arm–interarm contrast of ``mag`` magnitudes."""
    c = 10.0 ** (0.4 * max(float(mag), 0.0))
    return (c - 1.0) / (c + 1.0)


def shear_rate(R: np.ndarray, v: np.ndarray, at: float) -> float:
    """Γ = 1 − (R/v)(dv/dR): 0 for solid body, 1 for a flat curve, 1.5 for Keplerian."""
    dv = float(np.gradient(v, R)[int(np.argmin(np.abs(R - at)))])
    v_at = float(np.interp(at, R, v))
    return 1.0 - (at / v_at) * dv if v_at > 0.0 else float("nan")


# --- the law of several modes (S56, D215) -------------------------------------


def local_shear(R: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Γ(R) = 1 − (R/v)(dv/dR) at every radius: :func:`shear_rate`'s convention, on the whole grid."""
    R = np.asarray(R, dtype=float)
    v = np.asarray(v, dtype=float)
    return 1.0 - (R / np.maximum(v, 1e-9)) * np.gradient(v, R)


def local_swing_x(R: np.ndarray, kappa: np.ndarray, sigma: np.ndarray, G: float) -> np.ndarray:
    """Toomre's X for two arms at every radius, X₂(R) = κ²R / (2πGΣ · 2).

    ``kappa`` in km/s/kpc, ``sigma`` in M☉/pc² (as the disc publishes it) and ``G`` in
    kpc (km/s)²/M☉, so X is a pure number. Σ is the checkpoint-1 disc's **total** surface density,
    stars and gas together, as the spin's exponential publishes it: swing amplification is of the
    whole self-gravitating disc, so that is the definition and not an approximation; the
    checkpoint-4 split into stars and gas does not feed back (one way, no iteration: D174, D215
    gate ruling 3). X grows without bound as Σ falls.
    """
    R = np.asarray(R, dtype=float)
    sigma_kpc2 = np.maximum(np.asarray(sigma, dtype=float) * PC_PER_KPC**2, 1e-30)
    return np.asarray(kappa, dtype=float) ** 2 * R / (2.0 * math.pi * G * sigma_kpc2 * 2.0)


def local_swing_weights(
    R: np.ndarray, v: np.ndarray, kappa: np.ndarray, sigma: np.ndarray, G: float,
    x_low: float, x_high: float, x_dead: float, x_floor: float, m_max: float,
) -> np.ndarray:
    """w_m(R), shape (modes, R): how strongly the disc amplifies each arm number at each radius.

    The local window - m_lo = X₂(R)/(Γ(R) x_high), m_hi = X₂(R)/(Γ(R) x_low) - handed to
    :func:`swing_weight`, the same function the global window uses, for every m of
    :data:`ARM_MODES`; an arm number above ``m_max`` has no weight. A shear that is not finite or
    not positive is read as 1, as :func:`swing_window` reads it; a ring whose X is not finite
    amplifies nothing. One call of the weight per mode per ring: the count is the grid's (A1).
    """
    R = np.asarray(R, dtype=float)
    x2 = local_swing_x(R, kappa, sigma, G)
    gamma = local_shear(R, v)
    w = np.zeros((len(ARM_MODES), R.size))
    for i in range(R.size):
        g = float(gamma[i]) if math.isfinite(gamma[i]) and gamma[i] > 0.0 else 1.0
        m_lo, m_hi = float(x2[i]) / (g * x_high), float(x2[i]) / (g * x_low)
        for k, m in enumerate(ARM_MODES):
            if m <= m_max:
                w[k, i] = swing_weight(float(m), m_lo, m_hi, x_high, x_dead, x_low, x_floor)
    return w


def bar_terms(R: np.ndarray, pitch_deg: float, bar_length: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Per radius the bar's taper and the winding phase ln R · cot(pitch); and the bar's position angle.

    The bar gives way to the arms over its own half-length: a smooth taper e^{−(R/a)⁴}, so the
    density has no seam at the bar's end. The bar lies along the winding's phase at its end,
    ln(a) · cot(pitch) - a fixed convention, not a draw (D214, gate G1).
    """
    R = np.maximum(np.asarray(R, dtype=float), 1e-3)
    taper = np.exp(-((R / max(bar_length, 1e-3)) ** 4))
    cot = 1.0 / math.tan(math.radians(min(max(pitch_deg, 1.0), 89.0)))
    return taper, np.log(R) * cot, float(math.log(max(bar_length, 1e-3)) * cot)


@dataclass(frozen=True, slots=True, eq=False)
class ModeLaw:
    """The law's parts at every radius, kept apart so each can be read (rows are :data:`ARM_MODES`)."""

    weights: np.ndarray     # w_m(R): the amplifier's weight
    gain: np.ndarray        # w_m / max(1, Σ_k w_k): each mode's share of the sourced power A²
    tapered: np.ndarray     # Ã_m(R) = A √gain (1 − bar taper): before saturation
    bar: np.ndarray         # b(R) = B × the bar's taper
    saturation: np.ndarray  # s(R) = min(1, (1 − b) / Σ_m Ã_m)
    amplitudes: np.ndarray  # A_m(R) = s Ã_m: what multiplies each mode's cosine in the composed field


def mode_law(R: np.ndarray, weights: np.ndarray, arm: float, bar: float, pitch_deg: float, bar_length: float) -> ModeLaw:
    """The amplitudes of the arm modes at every radius from the amplifier's weights (D215, gate rulings 1-2).

    A_m(R)² = A² w_m(R) / max(1, Σ_k w_k(R)) - the sourced power times the disc's gain, the gain capped
    at one, never normalised up - then the bar's taper, then the saturation s(R) on the arm modes
    together. One fully amplified mode (w = 1, the rest 0) on an unsaturated ring is A (1 − taper):
    S55's arm weight, to the bit.
    """
    weights = np.asarray(weights, dtype=float)
    gain = weights / np.maximum(1.0, weights.sum(axis=0))
    taper, _, _ = bar_terms(R, pitch_deg, bar_length)
    tapered = arm * np.sqrt(gain) * (1.0 - taper)
    b = bar * taper
    peak = tapered.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        saturation = np.where(peak > 0.0, np.minimum(1.0, (1.0 - b) / np.where(peak > 0.0, peak, 1.0)), 1.0)
    return ModeLaw(weights, gain, tapered, b, saturation, tapered * saturation)


def dominant_mode(R: np.ndarray, sigma: np.ndarray, amplitudes: np.ndarray) -> float:
    """The arm number carrying the most mass-weighted power, Σ_R Σ(R) R ΔR A_m(R)²; a tie goes to the
    lower m. NaN where no mode carries any (D164): a disc with no arms has no arm number."""
    R = np.asarray(R, dtype=float)
    weight = np.asarray(sigma, dtype=float) * R * np.gradient(R)
    power = (weight[None, :] * np.asarray(amplitudes, dtype=float) ** 2).sum(axis=1)
    if not np.all(np.isfinite(power)) or not power.max() > 0.0:
        return float("nan")
    return float(ARM_MODES[int(np.argmax(power))])


def effective_arm_number(amplitudes: np.ndarray) -> np.ndarray:
    """m_eff(R) = Σ_m m A_m² / Σ_m A_m²: the ring's power-weighted arm number (it is m for one mode, and
    does not know the phases). NaN on a ring with no mode. Rows are :data:`ARM_MODES`."""
    power = np.asarray(amplitudes, dtype=float) ** 2
    total = power.sum(axis=0)
    m = np.asarray(ARM_MODES, dtype=float).reshape((-1,) + (1,) * (power.ndim - 1))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(total > 0.0, (m * power).sum(axis=0) / np.where(total > 0.0, total, 1.0), np.nan)


def _scalar(name, label, unit, about, provenance="derived"):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.SCALAR,
                     meaningful_zero=True, about=about, provenance=provenance)


# --- derived half -------------------------------------------------------------

BAR_HALF_LENGTH = _scalar(
    "bar_half_length", "Bar half-length", "kpc",
    "Acceptance row 15, and pointwise rather than statistical — which is why it lives in the "
    "derived stage. Scaled from the disc's λ_d scale length (checkpoint 1) since S25, so that the "
    "pattern can precede star formation; until then from the thin disc's fitted stellar scale "
    "length, a star-formation result 6% shorter (D174, debt #80). The disc-dominance link "
    "GALAXY_INPUTS.md §4b describes is published beside it but not modelled (debt #21).",
)

DISC_DOMINANCE = _scalar(
    "disc_dominance", "Disc share of v_c² at 2.2 R_d", "dimensionless",
    "How much of the rotation the baryons provide where the disc's own curve peaks. §4b makes "
    "this the first link in the chain to the pattern speed; it is measured here and unused, so "
    "that the missing link is visible rather than silently absent. Read off the checkpoint-1 "
    "curve since S25, which holds every baryon in one exponential (D174).",
)

SHEAR = _scalar(
    "shear_rate", "Shear rate Γ", "dimensionless",
    "1 − dln v/dln R at 2.2 R_d. Zero is solid-body rotation and 1 is a flat curve, so a value "
    "near 1 means the disc is shearing as a flat-curve galaxy does. Off the checkpoint-1 curve "
    "since S25 (D174).",
)


SWING_X = _scalar(
    "swing_x", "Swing-amplification X for two arms", "dimensionless",
    "Toomre's X = κ²R/(2πGΣm) at m = 2 in the Mestel form, 2/disc_dominance (S26, D175): the "
    "first link of §4b's chain, disc dominance → the arms the disc can amplify. 3.3 at the "
    "defaults, against the vigorous range of 1–2 the level-0 window holds: a two-armed pattern "
    "is at the edge of what this disc amplifies, three arms are inside it.",
)

SWING_ARM_MIN = _scalar(
    "swing_arm_min", "Fewest arms the disc amplifies", "count",
    "swing_x over the shear rate times the window's upper edge: the m at which X/Γ leaves the vigorous range on the "
    "high side. Not an integer. 1.7 at the defaults; "
    "3.9 for a disc that holds 30% of its rotation at a shear of 0.87 (the flocculent regime). The global "
    "window, at one radius: since S56 it sets only how coherent the arms are (the amplitude's mean); which "
    "arm numbers the disc carries is the same window evaluated at every radius, in the pattern stage (D215).",
)

SWING_ARM_MAX = _scalar(
    "swing_arm_max", "Most arms the disc amplifies", "count",
    "swing_x over the shear rate times the window's lower edge: the m at which X/Γ leaves the range on the low side. 3.4 "
    "at the defaults, the review's 2/f_d [verified: Sellwood & Masters 2022 §4.2.3.2].",
)

ARM_CONTRAST_MEAN = _scalar(
    "arm_contrast_mean", "Mean arm amplitude the disc supports", "dimensionless",
    "The cosine amplitude of the arm–interarm contrast the disc's own dynamics predict before the "
    "residual is drawn: the flocculent class's arm–interarm contrast plus the two-fold pattern's "
    "amplification weight times the way to the grand-design class's, then 10^(0.4 mag) turned into (C−1)/(C+1). 0.48 "
    "at the defaults (the grand-design value, since m = 2 sits inside the vigorous range), falling "
    "to 0.33 for a halo-dominated disc. Derived, so it lives in the derived half (D55).",
)

GAS_ARM_CONTRAST = _scalar(
    "gas_arm_contrast", "Gas arm–interarm contrast (ratio of means)", "dimensionless",
    "The ratio the gas's arm pattern is set to: mean gas surface density inside an arm mask of the "
    "source's width over the mean outside it, on each ring — a ratio of means, not a peak-to-trough. "
    "Its mean is derived as the stellar amplitude's is: the non-grand-design spirals' molecular ratio "
    "plus the two-fold pattern's amplification weight times the way to the grand designs'. No "
    "residual is drawn: the source's spread is over arm segments and radial bins, not galaxies, so it "
    "is not a galaxy-to-galaxy scatter and the galaxy carries the class mean (D210 as amended, debt "
    "#131) [verified: Querejeta et al. 2024, A&A 687, A293, Table 1; docs/READING_GAS_PATTERN.md]. "
    "2.73 at the defaults, where m = 2 sits inside the vigorous range. Where the ridge's amplitude is "
    "clipped to keep its trough or crest above zero, the ring's ratio falls short of this number.",
)


def compute_bar(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    c = ctx.constants
    R_d = float(ctx.fields["disc_scale_length_spin"])
    at = SHEAR_RADIUS_IN_SCALE_LENGTHS * R_d
    total = np.asarray(ctx.fields["circular_velocity"])
    halo = np.asarray(ctx.fields["halo_circular_velocity"])
    v_total = float(np.interp(at, R, total))
    v_halo = float(np.interp(at, R, halo))
    dominance = 1.0 - (v_halo / v_total) ** 2 if v_total > 0.0 else 0.0
    shear = shear_rate(R, total, at)
    x2, m_lo, m_hi = swing_window(dominance, shear, float(c["SWING_X_LOW"]), float(c["SWING_X_HIGH"]))
    coherence = swing_weight(2.0, m_lo, m_hi, float(c["SWING_X_HIGH"]), float(c["SWING_X_DEAD"]), float(c["SWING_X_LOW"]), float(c["SWING_X_FLOOR"]))
    floc, grand = float(c["ARM_INTERARM_FLOCCULENT"]), float(c["ARM_INTERARM_GRAND_DESIGN"])
    # The gas's ratio of means, joined between its two classes by the same weight (D210 as amended):
    # a derived mean with no residual, since the source's spread is not galaxy-to-galaxy (#131).
    gas_other, gas_grand = float(c["GAS_ARM_CONTRAST_OTHER"]), float(c["GAS_ARM_CONTRAST_GRAND_DESIGN"])
    return {
        "bar_half_length": float(c["BAR_LENGTH_RATIO"]) * R_d,
        "disc_dominance": dominance,
        "shear_rate": shear,
        "swing_x": x2,
        "swing_arm_min": m_lo,
        "swing_arm_max": m_hi,
        "arm_contrast_mean": contrast_amplitude(floc + (grand - floc) * coherence),
        "gas_arm_contrast": gas_other + (gas_grand - gas_other) * coherence,
    }


BAR = IMPLEMENTATIONS.register(
    Stage(
        id="bar", slot="bar", checkpoint=3,
        about=(
            "The bar's size, the disc's shear, and what the disc can amplify — everything about the "
            "pattern that has no draw in it. Split from the seeded half so that row 15 stays "
            "reproducible (D55). Since S26 it publishes the swing-amplification window and the mean "
            "arm amplitude, derived from disc_dominance and shear_rate (D175); since S51 the gas's "
            "arm–interarm ratio of means, derived the same way with no draw (D210 as amended)."
        ),
        compute=compute_bar,
        reads_constants=(
            "BAR_LENGTH_RATIO", "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR",
            "ARM_INTERARM_GRAND_DESIGN", "ARM_INTERARM_FLOCCULENT",
            "GAS_ARM_CONTRAST_GRAND_DESIGN", "GAS_ARM_CONTRAST_OTHER",
        ),
        requires=("disc_scale_length_spin", "circular_velocity", "halo_circular_velocity"),
        publishes=(BAR_HALF_LENGTH, DISC_DOMINANCE, SHEAR, SWING_X, SWING_ARM_MIN, SWING_ARM_MAX, ARM_CONTRAST_MEAN,
                   GAS_ARM_CONTRAST),
    )
)


# --- seeded half --------------------------------------------------------------

COROTATION = _scalar(
    "bar_corotation_radius", "Bar corotation radius", "kpc",
    "Acceptance row 17, statistical. The fast-bar ratio R_CR/a_bar is 1.2 ± 0.2, and that ± is "
    "observed scatter between galaxies rather than measurement error — so it is drawn, and the "
    "row is judged against an ensemble (debt #8).",
    provenance="seeded",
)

PATTERN_SPEED = _scalar(
    "bar_pattern_speed", "Bar pattern speed Ω_b", "km/s/kpc",
    "Acceptance row 16, statistical. Not drawn directly: it is v_c at the corotation radius "
    "divided by that radius, which is a definition, so all of its scatter is inherited from the "
    "fast-bar draw. Two galaxies with identical inputs differ here, and that is the point.",
    provenance="seeded",
)

PITCH_ANGLE = _scalar(
    "pitch_angle", "Spiral arm pitch angle", "deg",
    "Mean from the shear trend, dispersion drawn (ruling 3, PITCH_YU). **Because the trend is "
    "weak the draw dominates**, so arm winding is not a consequence of the mass distribution and "
    "anything reading this inherits a random component — the flag ruling 3 asks for. It is also a "
    "live instance of rule B11: a relation that fits the validation table can still be the wrong "
    "relation.",
    provenance="seeded",
)

ARM_MULTIPLICITY = _scalar(
    "arm_multiplicity", "Arm number carrying the most power", "count",
    "A label, not a law: the arm number whose mode carries the most power over the whole disc, "
    "each ring weighted by its mass (the disc's surface density times its area), a tie going to the "
    "lower number. **Nothing composes a field or places an object from it** - the arms are the "
    "five modes' amplitudes at every radius (arm_mode_amplitude_2 … 6) and their phases - so a "
    "galaxy whose label reads 3 carries two arms inside, three or four at mid-disc and five or six "
    "beyond. Not a number at all for a disc that amplifies nothing. From S26 to S55 this was a "
    "seeded draw weighted by the swing window at one radius, and the whole pattern was one cosine "
    "of the drawn number; the draw retired at S56, when the window became the split of power among "
    "the modes at every radius (D215). Labelled seeded because its stage reads the pattern seed "
    "(D55): the weighting takes the saturated amplitudes, which carry the drawn arm and bar "
    "amplitudes, and the bar's length.",
    provenance="seeded",
)


ARM_CONTRAST = _scalar(
    "arm_contrast", "Spiral arm amplitude A", "dimensionless",
    "The amplitude a single fully amplified arm mode has: Σ(R, φ) = Σ(R)[1 + A cos m(φ − ln R / tan p)] "
    "for one mode; with several, A² is the power the modes share at each radius, less where the disc's "
    "amplification falls short (the mode amplitudes carry the split). "
    "Since S26 the mean is derived (arm_contrast_mean, from the disc's own amplification) and the "
    "residual drawn on pattern_seed as the grand-design class's scatter in arm–interarm contrast "
    "(§4b verdict C, D175); until then an experimental input (D171, debt #23).",
    provenance="seeded",
)


def _mode_amplitude(m: int) -> FieldDecl:
    return FieldDecl(
        name=amplitude_field(m), label=f"Amplitude of the {m}-armed mode", unit="dimensionless",
        kind=Kind.FIELD, axes=("R",), ramp=Ramp("magma", lo=0.0, hi=1.0), meaningful_zero=True, provenance="seeded",
        about=(
            f"What multiplies cos({m}(φ − ln R / tan p) − θ) in the stellar density contrast at each radius: "
            f"the {m}-armed mode's amplitude with the bar's taper and the saturation already in it, so a "
            "Fourier transform of the composed field round a ring returns this number. Its square is the arm "
            "amplitude's square times the disc's gain for this arm number at this radius - the swing "
            "amplifier's weight at the local X and shear, over the sum of the five modes' weights where that "
            "sum exceeds one - so where the disc amplifies several arm numbers they share the sourced power, "
            "and where it amplifies none there is no arm: the power falls continuously to zero outward and is "
            "never normalised up. Two and three arms carry the inner disc, five and six the outer; past about "
            "15 kpc at the defaults no mode with six arms or fewer survives. The same with the randomness "
            "layer on or off: the layer only says where the crests are. Labelled seeded because it carries "
            "the drawn arm and bar amplitudes and its stage reads the pattern seed (D55); the split among the "
            "modes has no draw in it."
        ),
    )


ARM_MODE_AMPLITUDES: tuple[FieldDecl, ...] = tuple(_mode_amplitude(m) for m in ARM_MODES)

ARM_SATURATION = FieldDecl(
    name="arm_saturation", label="Arm saturation s(R)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis", lo=0.0, hi=1.0), meaningful_zero=True, provenance="seeded",
    about=(
        "The factor the arm modes are scaled by together where their linear sum would reach the mean density: "
        "1 where the modes' amplitudes and the bar's add up to less than 1, and below 1 where they would not - "
        "one minus the bar's amplitude there, over the sum of the modes' tapered amplitudes. It depends on the "
        "radius only, never on the phases, so the density contrast is non-negative for every realisation and "
        "nothing is floored. Five modes of equal power peak at √5 times the amplitude of one, so a strong draw "
        "of the arm amplitude saturates the rings that carry the most modes and loses power there; 1 on every "
        "ring at the default seeds. Labelled seeded as the amplitudes it is made from are (D55)."
    ),
)

BAR_CONTRAST = _scalar(
    "bar_contrast", "Bar amplitude", "dimensionless",
    "Fractional density contrast of the bar, an m = 2 term tapered off beyond the bar's "
    "half-length. Since S26 drawn log-normally on pattern_seed about the S4G barred sample's median "
    "with its 16th–84th-percentile width, capped at 0.9 (D175); until then an experimental input (D171).",
    provenance="seeded",
)

DENSITY_CONTRAST = FieldDecl(
    name="pattern_density_contrast", label="Bar and arm density contrast Σ(R, φ)/Σ(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=2.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the law (the modes' amplitudes, the pitch, the bar) applied to
    # where the arms are (the modes' phases, the layer's) - and 1 everywhere with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "The non-axisymmetric factor the star catalogue samples azimuth from: 1 on average around "
        "every ring, so the radial profile and every radial row are unchanged. Outside the bar, five "
        "logarithmic spirals of one drawn pitch angle laid over each other - two- to six-armed, each "
        "with its own amplitude at each radius and its own phase - so the arms are unequal, they "
        "branch, and their number changes outward; a straight m = 2 bar inside. Nowhere negative: "
        "where the modes would add up to more than the mean they are scaled down together. "
        "A composed field: with the randomness layer off it is 1 everywhere - the amplitudes and the "
        "pitch are still published, and nothing says where the arms are."
    ),
)


@dataclass(frozen=True, slots=True, eq=False)
class ArmPattern:
    """The stellar pattern of several modes: everything the density contrast needs, read from published
    fields in one place (rule A9).

    c(R, φ) = 1 + Σ_m A_m(R) cos(m χ − θ_m) + B w_bar(R) cos 2(φ − φ_bar), χ = φ − ln R · cot(pitch).

    **Evaluable at a point** (BUILD_III section 1c rule 5, D60): the amplitudes at an arbitrary radius are
    the published radial fields ``arm_mode_amplitude_m`` interpolated linearly in R between the grid radii
    they are published at (held at the end values beyond them); at a grid radius that is the field
    exactly. The bar's taper, the winding phase and the bar's angle are closed forms of R. The phases are
    the layer's five scalars; all zero is the convention S55 had.

    Built through ``galaxy.layer.compose`` (the one reader of the layer's switch) and by tests.
    """

    R: np.ndarray            # the grid radii the amplitudes are published at
    amplitudes: np.ndarray   # (modes, R): arm_mode_amplitude_m, with the taper and the saturation in them
    phases: tuple[float, ...]  # θ_m, one per mode of ARM_MODES
    bar: float
    pitch_deg: float
    bar_length: float
    flat: bool = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "R", np.asarray(self.R, dtype=float))
        object.__setattr__(self, "amplitudes", np.asarray(self.amplitudes, dtype=float))
        object.__setattr__(self, "phases", tuple(float(p) for p in self.phases))
        if self.amplitudes.shape != (len(ARM_MODES), self.R.size) or len(self.phases) != len(ARM_MODES):
            raise ValueError(
                f"a pattern holds {len(ARM_MODES)} modes on its {self.R.size} radii; got amplitudes "
                f"{self.amplitudes.shape} and {len(self.phases)} phases"
            )
        # No perturbation to apply: no arm amplitude and no bar, or a pattern the grid could not resolve (a
        # mesh too coarse for the shear gives a NaN pitch and bar) or the layer did not realise (NaN phases),
        # which stays axisymmetric. Decided once: the censuses ask per cell.
        scalars = (self.bar, self.pitch_deg, self.bar_length, *self.phases)
        finite = all(math.isfinite(v) for v in scalars) and bool(np.all(np.isfinite(self.amplitudes)))
        object.__setattr__(self, "flat", not finite or (not self.amplitudes.any() and self.bar == 0.0))

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], R: np.ndarray) -> "ArmPattern | None":
        """The pattern of a run's published fields on the run's grid radii ``R``, or None where the fields
        hold no pattern. It reads the modes; ``arm_multiplicity`` is not among what it reads (D215)."""
        if any(n not in fields for n in PATTERN_READS):
            return None
        return cls(
            R, np.stack([np.asarray(fields[n], dtype=float) for n in AMPLITUDE_FIELDS]),
            tuple(float(fields[n]) for n in PHASE_FIELDS),
            float(fields["bar_contrast"]), float(fields["pitch_angle"]), float(fields["bar_half_length"]),
        )

    def amplitudes_at(self, R: np.ndarray) -> np.ndarray:
        """(modes, …R's shape): each mode's amplitude at ``R``, linear in R between the grid radii."""
        R = np.asarray(R, dtype=float)
        return np.stack([np.interp(R, self.R, row) for row in self.amplitudes])

    def _terms(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """Per radius: the modes' amplitudes, the bar's weight, the winding phase; and the bar's angle."""
        taper, phase, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        return self.amplitudes_at(R), self.bar * taper, phase, bar_angle

    def _arms(self, weights: list[np.ndarray], chi: np.ndarray) -> np.ndarray | float:
        """Σ_m A_m cos(m χ − θ_m), the modes with no amplitude anywhere among ``weights`` left out (so one
        mode alone is S55's one product, to the bit)."""
        total: np.ndarray | None = None
        for m, theta, a in zip(ARM_MODES, self.phases, weights):
            if not np.any(a):
                continue
            term = a * np.cos(float(m) * chi - theta)
            total = term if total is None else total + term
        return 0.0 if total is None else total

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ(R, φ)/Σ(R) on the (R, φ) grid. Mean 1 around every ring: every m is an integer."""
        amp, bar_w, phase, bar_angle = self._terms(R)
        phi = np.asarray(phi, dtype=float)[None, :]
        arms = self._arms([a[:, None] for a in amp], phi - phase[:, None])
        bar = bar_w[:, None] * np.cos(2.0 * (phi - bar_angle))
        return 1.0 + arms + bar

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise (S48: each
        bright star inverts its own row of azimuths inside its own cell)."""
        amp, bar_w, phase, bar_angle = self._terms(np.asarray(R, dtype=float))
        phi = np.asarray(phi, dtype=float)
        return 1.0 + self._arms(list(amp), phi - phase) + bar_w * np.cos(2.0 * (phi - bar_angle))

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius, analytically: a sum of
        the modes' own integrals, each a sine difference - no quadrature."""
        amp, bar_w, phase, bar_angle = self._terms(np.array([R]))
        a, b = edges[:-1], edges[1:]

        def mean_cos(m: float, shift: float, theta: float = 0.0) -> np.ndarray:
            return (np.sin(m * (b - shift) - theta) - np.sin(m * (a - shift) - theta)) / (m * (b - a))

        arms: np.ndarray | float | None = None
        for m, theta, row in zip(ARM_MODES, self.phases, amp):
            if row[0] == 0.0:
                continue
            term = row[0] * mean_cos(float(m), float(phase[0]), theta)
            arms = term if arms is None else arms + term
        return 1.0 + (0.0 if arms is None else arms) + bar_w[0] * mean_cos(2.0, bar_angle)

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))


def invert_azimuths(u: np.ndarray, grid: np.ndarray, density: np.ndarray) -> np.ndarray:
    """Azimuths on ``grid`` (one sector, evenly spaced) by inverting each star's own row of ``density``.

    ``density`` is (stars, len(grid)): the contrast, or since S27 the star-formation modulation,
    evaluated at each star's radius. Trapezoids between the grid points, linear inside one —
    an inverse CDF, never a rejection (rule B8).
    """
    steps = grid.size - 1
    f = np.maximum(density, 0.0)  # (stars, steps + 1)
    stars = f.shape[0]
    seg = 0.5 * (f[:, 1:] + f[:, :-1])
    cdf = np.concatenate([np.zeros((stars, 1)), np.cumsum(seg, axis=1)], axis=1)
    total = np.where(cdf[:, -1] > 0.0, cdf[:, -1], 1.0)
    target = np.asarray(u, dtype=float) * total
    k = np.clip((cdf < target[:, None]).sum(axis=1) - 1, 0, steps - 1)
    rows = np.arange(stars)
    c0, c1 = cdf[rows, k], cdf[rows, k + 1]
    frac = np.where(c1 > c0, (target - c0) / np.where(c1 > c0, c1 - c0, 1.0), 0.0)
    return grid[k] + np.clip(frac, 0.0, 1.0) * (grid[1] - grid[0])


def compute_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    a_bar = float(ctx.fields["bar_half_length"])
    total = np.asarray(ctx.fields["circular_velocity"])

    ratio = ctx.rng("pattern_seed", "fast_bar").normal(
        float(ctx.constants["FAST_BAR_RATIO"]), float(ctx.constants["FAST_BAR_SCATTER"])
    )
    corotation = max(float(ratio), 0.1) * a_bar
    v_cr = float(np.interp(corotation, R, total))

    gamma = float(ctx.fields["shear_rate"])
    pitch_mean = float(ctx.constants["PITCH_SHEAR_INTERCEPT"]) + float(ctx.constants["PITCH_SHEAR_SLOPE"]) * (gamma - 1.0)
    pitch = ctx.rng("pattern_seed", "pitch").normal(pitch_mean, float(ctx.constants["PITCH_SCATTER"]))

    # The arm number is not drawn (S56, D215): the stream ("pattern_seed", "arms") retired with the draw and
    # the nearest-m fallback with it. Every other stream here keeps its path, so the pitch, the fast-bar ratio
    # and the two amplitudes are the numbers they were.
    c = ctx.constants
    m_lo, m_hi = float(ctx.fields["swing_arm_min"]), float(ctx.fields["swing_arm_max"])
    x_high, x_dead, x_low, x_floor = (float(c[k]) for k in ("SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_LOW", "SWING_X_FLOOR"))
    pitch_angle = float(np.clip(pitch, 1.0, 60.0))
    # The amplitudes: derived means, seeded residuals (§4b verdict C). The arms' residual is drawn
    # in magnitudes of arm–interarm contrast about the derived mean; the bar's log-normally.
    floc, grand = float(c["ARM_INTERARM_FLOCCULENT"]), float(c["ARM_INTERARM_GRAND_DESIGN"])
    coherence = swing_weight(2.0, m_lo, m_hi, x_high, x_dead, x_low, x_floor)
    mag = floc + (grand - floc) * coherence + ctx.rng("pattern_seed", "arm_contrast").normal(0.0, float(c["ARM_INTERARM_SCATTER"]))
    arm_contrast = contrast_amplitude(mag)
    bar_contrast = min(
        math.exp(math.log(float(c["BAR_CONTRAST_MEDIAN"])) + ctx.rng("pattern_seed", "bar_contrast").normal(0.0, float(c["BAR_CONTRAST_LOG_SCATTER"]))),
        BAR_CONTRAST_CAP,
    )
    # The law of several modes (S56, D215): the swing window at every radius splits the sourced power A²
    # among the arm numbers, the gain capped at one; the bar's taper; the saturation. A law: no draw in it,
    # and the same with the randomness layer on or off.
    sigma = np.asarray(ctx.fields["disc_surface_density"], dtype=float)
    weights = local_swing_weights(
        R, total, ctx.fields["epicyclic_frequency"], sigma, float(c["G"]),
        x_low, x_high, x_dead, x_floor, float(c["ARM_MULTIPLICITY_MAX"]),
    )
    law = mode_law(R, weights, arm_contrast, bar_contrast, pitch_angle, a_bar)
    amplitudes = {name: law.amplitudes[k] for k, name in enumerate(AMPLITUDE_FIELDS)}
    cells = (R.size, ctx.grid.phi.size)

    def composed() -> np.ndarray:
        # The law applied to the realisation: the pattern object is compose's, built from what this stage has
        # just made and the layer's phases. A pattern with nothing to place is the neutral.
        shape = _compose.stellar_pattern(
            ctx.fields, R, law={**amplitudes, "bar_contrast": bar_contrast, "pitch_angle": pitch_angle},
        )
        return _compose.neutral(DENSITY_CONTRAST, cells) if shape is None or shape.flat else shape.contrast(R, ctx.grid.phi)

    return {
        "bar_corotation_radius": corotation,
        "bar_pattern_speed": v_cr / corotation if corotation > 0.0 else 0.0,
        "pitch_angle": pitch_angle,
        "arm_multiplicity": dominant_mode(R, sigma, law.amplitudes),
        "arm_contrast": arm_contrast,
        "bar_contrast": bar_contrast,
        **amplitudes,
        "arm_saturation": law.saturation,
        # The one composed field here (S55, D214): the law above applied to where the arms are. With the layer
        # off it is its declared neutral everywhere and every field above is what it was - compose is the one
        # place that asks, and the neutral is the declaration's, not a number written here.
        "pattern_density_contrast": _compose.field(ctx.fields, DENSITY_CONTRAST, cells, composed),
    }


PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="pattern", slot="pattern", checkpoint=3,
        about=(
            "The pattern's kinematics and the arms: everything §4b assigns to a seeded draw - the "
            "pitch, the fast-bar ratio, the arm and bar amplitudes - and, since S56, the law of several "
            "arm modes at once: the swing window at every radius splits the arms' power among two to six "
            "arms, with no draw of an arm number (D215). "
            "Reads pattern_seed, so rerolling it invalidates checkpoints 4, 5 and 6 and nothing "
            "earlier — star formation follows the pattern since S25 (D174). Where each mode's crests "
            "lie is the randomness layer's, on its own seed."
        ),
        compute=compute_pattern,
        reads_seeds=("pattern_seed",),
        reads_constants=(
            "FAST_BAR_RATIO", "FAST_BAR_SCATTER",
            "PITCH_SHEAR_INTERCEPT", "PITCH_SHEAR_SLOPE", "PITCH_SCATTER",
            "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR", "ARM_MULTIPLICITY_MAX",
            "ARM_INTERARM_GRAND_DESIGN", "ARM_INTERARM_FLOCCULENT", "ARM_INTERARM_SCATTER",
            "BAR_CONTRAST_MEDIAN", "BAR_CONTRAST_LOG_SCATTER",
            "G",  # S56 (D215): the local swing parameter, X = kappa^2 R / (2 pi G Sigma m)
        ),
        requires=(
            "bar_half_length", "shear_rate", "circular_velocity", "swing_arm_min", "swing_arm_max",
            # S56 (D215): the local window's disc - the checkpoint-1 curve's kappa and the total surface density -
            # and the layer's phases, which only the composed field reads.
            "epicyclic_frequency", "disc_surface_density", *PHASE_FIELDS,
        ),
        publishes=(COROTATION, PATTERN_SPEED, PITCH_ANGLE, ARM_MULTIPLICITY, ARM_CONTRAST, BAR_CONTRAST,
                   *ARM_MODE_AMPLITUDES, ARM_SATURATION, DENSITY_CONTRAST),
    )
)
