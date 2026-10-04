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

- *The window.* X(R) = κ²R / (2πGΣ) - Toomre's X at m = 1, equal to m·X_m - with the
  checkpoint-1 disc's epicyclic frequency and its total surface density (stars and gas together:
  swing amplification is of the whole self-gravitating disc), the local shear
  Γ(R) = 1 − d ln v / d ln R, m_lo = X/(Γ x_high), m_hi = X/(Γ x_low), and w_m(R) the existing
  :func:`swing_weight`, unchanged: mode m is amplified whole where x_low ≤ X/(mΓ) ≤ x_high.
  (The first two passes of S56 built this window on X/2, the lead's error; D215 ruling 11.)
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

**The bar: a presence, a body (S58, BUILD_III Phase P3; DECISIONS.md D217).** Until S58 every galaxy
had a bar, and the bar was one cosine, B e^{−(R/a)⁴} cos 2(φ − φ_bar). Since S58:

- *Presence* (D217 items 1-3) is derived in the ``bar`` stage, with no draw: the disc is barred where
  the time it takes to form a bar, t_b = T0 exp(S / f_d) with f_d the published ``disc_dominance``
  (:func:`bar_formation_time`), is shorter than the disc's age since the halo's assembly redshift
  (:func:`lookback_time`). ``bar_formation_time`` is published on every galaxy and ``bar_present`` is
  the verdict. A template's pin - the input ``bar_present``, True or False, the observed class -
  replaces the derived verdict when given, and the derived time stays published beside it. **An
  unbarred galaxy publishes NaN for the bar's numbers** (D164): the half-length, the shape, the
  amplitude, the mass share, the corotation radius and the pattern speed; the bar's angle, a closed
  form of the half-length and the pitch, is then NaN too (:func:`bar_terms`). A NaN bar is "no bar,
  taper 0": the body is absent, the arm modes run to the centre, and the saturation is
  min(1, 1/Σ Ã). Every draw keeps its stream and its value whether the galaxy is barred or not.
- *The body* (items 4-5) replaces the cosine: a two-dimensional component of surface density
  Σ_bar ∝ (1 − m²)ⁿ inside m = 1 and nothing outside, m = ((|x|/a)^c + (|y|/(q a))^c)^{1/c} with x
  along the bar's axis, a the half-length, q the axis ratio and c the boxiness (:class:`BarBody`).
  Its mass is taken ring by ring from the ring's own stars: the contrast is
  1 − β(R) + Σ_bar(R, φ)/Σ(R), β the body's share of the ring and Σ **checkpoint 1's total disc**
  (a declared approximation: there is no split into stars and gas and no bulge at this checkpoint).
  The law is laid on the fixed fine cells round each grid ring that the gas's response uses
  (``gas_response.CELLS``): β is the mean of the same samples the ring's profile is made of, so the
  ring's mean is 1 with nothing divided and nothing clipped; a point reads the linear interpolant
  between the cells' centres, in the bar's frame, and blends its two neighbouring rings linearly in
  R; the published field holds the body's exact mean over each grid cell's extent in azimuth
  (``gas_response.sector_mean``), so a ring keeps its stars on any grid. The arm modes are published
  at the cells' centres, as they always were (a cosine's samples have no mean).
- *The input is the drawn* ``bar_contrast`` B: the body's normalisation is the one at which the
  m = 2 Fourier amplitude of the published field's bar part, at its largest over the grid's rings
  inside a, equals B (:func:`body_share`; the amplitude is linear in the normalisation, so it is one
  division). The body's share of the disc's mass on the grid is published as ``bar_mass_share``, and
  every reader builds the body from that number (:meth:`BarBody.normalisation`), the stage included.
- *The saturation* reads the body's depth: b(R) = 1 − min_φ(body contrast) = β − min_φ Σ_bar/Σ, and
  s(R) = min(1, (1 − b)/Σ_m Ã_m) as before, so the composed field is non-negative by the same bound.
  The arms' taper e^{−(R/a)⁴} is unchanged.
- *The two-armed mode's phase* is tied to the bar in a barred galaxy (item 9; the layer's
  ``arm_phases``): θ₂ = 0, the m = 2 crest on the bar's axis at R = a.
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
from galaxy.stages import gas_response as _cells  # the fixed fine cells round a ring, their interpolant, its exact means

SHEAR_RADIUS_IN_SCALE_LENGTHS = 2.2  # ruling 3: take the scaled form
CELLS = _cells.CELLS  # the fixed cells round a ring the bar's body is laid on: the gas response's own (S58, D217)
# One kpc/(km/s) in Gyr: the IAU kiloparsec (3.0856775814913673e16 km) over a Julian gigayear (3.15576e16 s). A
# definition, which turns the Hubble constant's km/s/kpc into a time.
GYR_PER_KPC_PER_KMS = 3.0856775814913673e16 / 3.15576e16
BAR_PRESENT: tuple[str, str] = ("no", "yes")  # the verdict's two labels, in this order (S58, D217)
# The closed set of arm numbers since S26 (D175): two to ARM_MULTIPLICITY_MAX. From S26 to S55 one of them
# was drawn; since S56 (D215) each is a mode with its own amplitude at every radius. m = 1 is excluded
# (level0, ARM_MULTIPLICITY_MAX's about line).
ARM_MULTIPLICITIES: tuple[float, ...] = (2.0, 3.0, 4.0, 5.0, 6.0)
ARM_MODES: tuple[int, ...] = tuple(int(m) for m in ARM_MULTIPLICITIES)
# The draw's cap. Set for the cosine bar S26-S57 held (near 1 a cosine empties its inter-bar sector); the body
# S58 put in its place is nowhere under 0.266 at 0.9, so the cap is kept for the draws' sake, not the field's
# (BAR_CONTRAST_LOG_SCATTER).
BAR_CONTRAST_CAP = 0.9
PC_PER_KPC = 1000.0  # a definition: the disc's surface density is published per square parsec


def amplitude_field(m: int) -> str:
    """The radial field holding mode ``m``'s amplitude: what multiplies its cosine in the composed field."""
    return f"arm_mode_amplitude_{int(m)}"


def phase_field(m: int) -> str:
    """The synthetic scalar holding mode ``m``'s phase (the layer's, ``galaxy/layer/arm_phases.py``)."""
    return f"arm_mode_phase_{int(m)}"


AMPLITUDE_FIELDS: tuple[str, ...] = tuple(amplitude_field(m) for m in ARM_MODES)
PHASE_FIELDS: tuple[str, ...] = tuple(phase_field(m) for m in ARM_MODES)
# What the bar's body is built from (S58, D217 items 4-5): its shape, its share of the disc's mass, and
# checkpoint 1's total disc, which the share is of.
BODY_FIELDS: tuple[str, ...] = ("bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_mass_share", "disc_surface_density")
# What the stellar pattern is built from, and so what every stage that places by it requires (S56, D215:
# the modes, never ``arm_multiplicity``; S58, D217: the body, and the disc's surface density with it).
PATTERN_READS: tuple[str, ...] = ("bar_contrast", "pitch_angle", "bar_half_length", *BODY_FIELDS, *AMPLITUDE_FIELDS, *PHASE_FIELDS)


def swing_window(disc_dominance: float, shear: float, x_low: float, x_high: float) -> tuple[float, float, float]:
    """(X, m_lo, m_hi): Toomre's X at m = 1 in the Mestel form, and the arm numbers the disc amplifies.

    For a flat curve κ² = 2v²/R² and a disc whose own rotation is v_d² = 2πGΣR (Mestel), so
    X_m = κ²R/(2πGΣm) = 2/(m f_d) with f_d = v_d²/v² the disc's share of the rotation — the
    published ``disc_dominance``. The first value returned is 2/f_d = m·X_m: **X at m = 1**, the
    Mestel identity, and not X for two arms (which is 1/f_d; S26 to S56's second pass labelled it
    X₂, a mislabel the value never shared: D215 ruling 11). Vigorous amplification for
    x_low < X_m/Γ < x_high therefore means X/(Γ x_high) ≤ m ≤ X/(Γ x_low), the review's
    1/f_d ≲ m ≲ 2/f_d at Γ = 1 [verified: Sellwood & Masters 2022 §4.2.3.2]. The alternative is
    the local form with the exponential disc's own Σ; it increases outward (D'Onghia 2015: two
    arms at 4.5 kpc, five or six at R₀), so it needs a radius chosen by hand, and the global form
    was chosen before either number was read (D175).
    **Since S56 (D215) the local form is the law for the arm number** - evaluated at every radius,
    so no radius is chosen (:func:`local_swing_weights`) - and this global form stays as the
    amplitude's coherence input only: D175's choice is superseded for the arm number.
    """
    f_d = min(max(float(disc_dominance), 1e-6), 1.0)
    gamma = float(shear) if math.isfinite(shear) and shear > 0.0 else 1.0
    x_one = 2.0 / f_d
    return x_one, x_one / (gamma * x_high), x_one / (gamma * x_low)


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
    """Toomre's X at every radius, X(R) = κ²R / (2πGΣ): X at m = 1, equal to m·X_m for every m.

    ``kappa`` in km/s/kpc, ``sigma`` in M☉/pc² (as the disc publishes it) and ``G`` in
    kpc (km/s)²/M☉, so X is a pure number. S56's first two passes divided by a further 2 (X for
    two arms, i.e. X/2, handed to a window that takes X): the lead's error, corrected by D215
    ruling 11. Σ is the checkpoint-1 disc's **total** surface density,
    stars and gas together, as the spin's exponential publishes it: swing amplification is of the
    whole self-gravitating disc, so that is the definition and not an approximation; the
    checkpoint-4 split into stars and gas does not feed back (one way, no iteration: D174, D215
    gate ruling 3). X grows without bound as Σ falls.
    """
    R = np.asarray(R, dtype=float)
    sigma_kpc2 = np.maximum(np.asarray(sigma, dtype=float) * PC_PER_KPC**2, 1e-30)
    return np.asarray(kappa, dtype=float) ** 2 * R / (2.0 * math.pi * G * sigma_kpc2)


def local_swing_weights(
    R: np.ndarray, v: np.ndarray, kappa: np.ndarray, sigma: np.ndarray, G: float,
    x_low: float, x_high: float, x_dead: float, x_floor: float, m_max: float,
) -> np.ndarray:
    """w_m(R), shape (modes, R): how strongly the disc amplifies each arm number at each radius.

    The local window - m_lo = X(R)/(Γ(R) x_high), m_hi = X(R)/(Γ(R) x_low), X the local X at
    m = 1 (:func:`local_swing_x`) - handed to :func:`swing_weight`, the same function the global
    window uses, for every m of :data:`ARM_MODES`; an arm number above ``m_max`` has no weight. A
    shear that is not finite or not positive is read as 1, as :func:`swing_window` reads it; a
    ring whose X is not finite amplifies nothing. One call of the weight per mode per ring: the
    count is the grid's (A1).
    """
    R = np.asarray(R, dtype=float)
    x_one = local_swing_x(R, kappa, sigma, G)
    gamma = local_shear(R, v)
    w = np.zeros((len(ARM_MODES), R.size))
    for i in range(R.size):
        g = float(gamma[i]) if math.isfinite(gamma[i]) and gamma[i] > 0.0 else 1.0
        m_lo, m_hi = float(x_one[i]) / (g * x_high), float(x_one[i]) / (g * x_low)
        for k, m in enumerate(ARM_MODES):
            if m <= m_max:
                w[k, i] = swing_weight(float(m), m_lo, m_hi, x_high, x_dead, x_low, x_floor)
    return w


def bar_terms(R: np.ndarray, pitch_deg: float, bar_length: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Per radius the bar's taper and the winding phase ln R · cot(pitch); and the bar's position angle.

    The bar gives way to the arms over its own half-length: a smooth taper e^{−(R/a)⁴}, so the
    density has no seam at the bar's end. The bar lies along the winding's phase at its end,
    ln(a) · cot(pitch) - a fixed convention, not a draw (D214, gate G1).

    **A half-length that is not a number is no bar** (S58, D217 item 3; D164): the taper is 0 on
    every ring - the arms' weight 1 everywhere, the arm modes to the centre - and there is no
    angle (NaN). It is not an unresolved pattern: the winding phase is still the pitch's.
    """
    R = np.maximum(np.asarray(R, dtype=float), 1e-3)
    cot = 1.0 / math.tan(math.radians(min(max(pitch_deg, 1.0), 89.0)))
    if math.isnan(bar_length):
        return np.zeros(R.shape), np.log(R) * cot, float("nan")
    taper = np.exp(-((R / max(bar_length, 1e-3)) ** 4))
    return taper, np.log(R) * cot, float(math.log(max(bar_length, 1e-3)) * cot)


# --- the bar's presence (S58, D217 items 1-3) ---------------------------------


def cosmic_time(redshift: float, hubble: float, omega_m: float) -> float:
    """The age of the universe at ``redshift``, in Gyr, for flat matter and a cosmological constant:
    t(z) = (2 / (3 H₀ √Ω_Λ)) asinh(√(Ω_Λ/Ω_M) (1 + z)^{−3/2}), Ω_Λ = 1 − Ω_M - the closed form of the
    Friedmann equation with no radiation and no curvature [inferred: the textbook integral; held against
    its own quadrature in tests/test_bar.py]. ``hubble`` in km/s/kpc, as the model holds H₀.

    Flat because the model's one other use of Ω_M, the virial overdensity the halo's concentration is
    quoted at, is the flat-universe form (``halo.virial_overdensity``): one cosmology, not two.
    """
    omega_l = 1.0 - omega_m
    scale = 2.0 / (3.0 * hubble * math.sqrt(omega_l)) * GYR_PER_KPC_PER_KMS
    return scale * math.asinh(math.sqrt(omega_l / omega_m) * (1.0 + redshift) ** -1.5)


def lookback_time(redshift: float, hubble: float, omega_m: float) -> float:
    """How long ago ``redshift`` was, in Gyr: t(0) − t(z) of :func:`cosmic_time`. The disc's age since the
    halo's assembly redshift is this (D217 item 1: "the disc's age since ``halo_assembly_z``"); the model
    held no function from that redshift to a time until S58 - the halo reads it for its concentration only.

    **Two clocks, a declared debt.** By this cosmology the universe is 13.467 Gyr old (H₀ = 70 km/s/Mpc,
    Ω_M = 0.3, flat); the grid's time axis runs to ``t_max`` = 13.8 Gyr, "cosmic time from t = 0"
    (``core/grids.py``). The model so holds two ages of the universe, 2.5 % apart, and the bar's presence is
    judged on this one. What the choice moves: at the default assembly redshift (1.66, a lookback of
    9.625 Gyr) a disc is barred above f_d = 0.3295; with the same lookback stretched to the grid's clock
    (× 13.8/13.467: 9.863 Gyr) the threshold would be 0.3276. Neither clock is reconciled with the other
    here.
    """
    return cosmic_time(0.0, hubble, omega_m) - cosmic_time(redshift, hubble, omega_m)


def bar_formation_time(disc_dominance: float, scale: float, exponent: float) -> float:
    """t_b = T0 exp(S / f_d), in Gyr: how long a disc holding the share f_d of the squared circular speed at
    2.2 scale lengths takes to form a bar (Fujii et al. 2018's fit; the constants carry the tag and the
    fit's errors). Infinite for a disc that holds none of it: it never forms one."""
    f_d = float(disc_dominance)
    if not f_d > 0.0 or exponent / f_d > 700.0:
        return math.inf
    return scale * math.exp(exponent / f_d)


# --- the bar's body (S58, D217 items 4-5) -------------------------------------


def bar_radius(x: np.ndarray, y: np.ndarray, half_length: float, axis_ratio: float, boxiness: float) -> np.ndarray:
    """m = ((|x|/a)^c + (|y|/(q a))^c)^{1/c}: the generalised radius of the bar's body, 1 on its edge.
    ``x`` along the bar's axis and ``y`` across it, kpc; a the half-length, q the axis ratio, c the boxiness."""
    along = (np.abs(x) / half_length) ** boxiness
    across = (np.abs(y) / (axis_ratio * half_length)) ** boxiness
    return (along + across) ** (1.0 / boxiness)


def ring_bracket(grid: np.ndarray, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(lower ring, upper ring, share of the upper) for each radius: linear in R between two grid rings, the
    end ring alone beyond the grid. At a grid radius the share is 0 or 1 and the ring is its own. The gas
    pattern's own bracket (D216 item 9), which the bar's body reads its rings by too."""
    if grid.size < 2:
        zero = np.zeros(np.shape(R), dtype=np.int64)
        return zero, zero, np.zeros(np.shape(R))
    lower = np.minimum(np.maximum(np.searchsorted(grid, R, side="right") - 1, 0), grid.size - 2)
    share = (R - grid[lower]) / (grid[lower + 1] - grid[lower])
    return lower, lower + 1, np.minimum(np.maximum(share, 0.0), 1.0)


def fourier_amplitude(values: np.ndarray, edges: np.ndarray, m: int = 2) -> np.ndarray:
    """The m-fold Fourier amplitude round each ring of a field held as cell values, shaped (rings, cells) on
    the cells between ``edges``: |2 Σ_j w_j v_j e^{−i m φ_j}|, φ_j the cells' centres and w_j their shares of
    the ring. For 1 + A cos(m(φ − φ₀)) sampled at the centres it is A."""
    lo, hi = np.asarray(edges[:-1], dtype=float), np.asarray(edges[1:], dtype=float)
    weight = (hi - lo) / float(edges[-1] - edges[0])
    return 2.0 * np.abs((np.asarray(values, dtype=float) * (weight * np.exp(-1j * m * 0.5 * (lo + hi)))[None, :]).sum(axis=1))


@dataclass(frozen=True, slots=True, eq=False)
class BarBody:
    """The bar's body as a two-dimensional component, at unit normalisation, on the fixed cells of every grid
    ring (D217 item 4).

    ``unit`` is (1 − m²)ⁿ inside m = 1 and 0 outside, on the cells' centres ψ_k (``gas_response.cell_centres``)
    **in the bar's frame**, ψ = φ − φ_bar, shaped (R, CELLS). The edge m = 1 is the law's, not the circle R = a:
    a boxy body (c > 2) stands a little proud of that circle beside its own axis - to 1.0007 a at this shape,
    (1 + q⁶)^{1/6} for c = 3 - so the first ring past the half-length can hold a sliver of it (1e-7 of the
    central density on the production grid), and holds it. With a normalisation N in M☉/pc² the body's
    surface density is N · unit, the ring's share β = N ⟨unit⟩/Σ, the contrast's departure from 1 is
    N (unit − ⟨unit⟩)/Σ - of mean 0 round the ring by construction, ⟨·⟩ being the mean of the same samples -
    and its depth b = N (⟨unit⟩ − min unit)/Σ.
    Σ is checkpoint 1's total disc on the grid radii. Nothing here knows the bar's angle but the cell
    means, which are taken over a grid's own φ cells.
    """

    R: np.ndarray                # the grid radii, kpc
    surface_density: np.ndarray  # (R,): checkpoint 1's total disc Σ, M☉/pc²
    half_length: float           # a, kpc
    axis_ratio: float            # q
    boxiness: float              # c
    index: float                 # n, the profile's exponent
    unit: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("R", "surface_density"):
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        if self.surface_density.shape != self.R.shape:
            raise ValueError(f"a bar's body holds the disc's surface density on its {self.R.size} radii; got {self.surface_density.shape}")
        unit = np.zeros((self.R.size, CELLS))
        # The rings the body can reach: inside the corner of its bounding box, a (1 + q²)^½ - a bound, not the
        # law's edge, which m < 1 decides cell by cell below.
        inside = self.R < self.half_length * math.sqrt(1.0 + self.axis_ratio**2)
        if inside.any():
            psi = _cells.cell_centres(CELLS)
            radius = self.R[inside, None]
            m = bar_radius(radius * np.cos(psi)[None, :], radius * np.sin(psi)[None, :], self.half_length, self.axis_ratio, self.boxiness)
            unit[inside] = np.where(m < 1.0, (1.0 - np.minimum(m, 1.0) ** 2) ** self.index, 0.0)
        unit.setflags(write=False)
        object.__setattr__(self, "unit", unit)

    @property
    def holds(self) -> np.ndarray:
        """(R,) bool: the grid rings that hold some of the body - a cell of theirs lies inside m = 1."""
        return self.unit.any(axis=1)

    @property
    def inside(self) -> np.ndarray:
        """(R,) bool: the grid rings inside the bar's half-length, R < a: the rings the drawn amplitude is the
        largest two-fold amplitude over (D217 item 4: "the published field's A₂ maximum inside a")."""
        return self.R < self.half_length

    @property
    def ring_mean(self) -> np.ndarray:
        """⟨unit⟩ on each ring: the mean of the ring's own samples, which is its interpolant's exact mean."""
        return self.unit.sum(axis=1) / CELLS

    def ring_areas(self) -> np.ndarray:
        """Each ring's area over 2π, R ΔR, kpc²: the weights the arm number's label uses (:func:`dominant_mode`)."""
        return self.R * (np.gradient(self.R) if self.R.size > 1 else np.ones_like(self.R))

    def _per_density(self, normalisation: float) -> np.ndarray:
        """N/Σ on the rings that hold the body, 0 elsewhere (where the disc's density is not asked)."""
        holds = self.holds
        return np.where(holds, normalisation / np.where(holds, self.surface_density, 1.0), 0.0)

    def mass_share(self, normalisation: float) -> float:
        """The body's mass over the disc's, both on the grid's rings: Σ_i β_i Σ_i R_i ΔR_i / Σ_i Σ_i R_i ΔR_i."""
        areas = self.ring_areas()
        return float(normalisation * (self.ring_mean * areas).sum() / (self.surface_density * areas).sum())

    def normalisation(self, share: float) -> float:
        """N in M☉/pc² for a body holding ``share`` of the disc's mass on the grid: :meth:`mass_share` inverted.
        Every reader of the published share builds its body through this, the stage that publishes it too."""
        areas = self.ring_areas()
        body = float((self.ring_mean * areas).sum())
        return float(share) * float((self.surface_density * areas).sum()) / body if body > 0.0 else 0.0

    def ring_share(self, normalisation: float) -> np.ndarray:
        """β(R): the body's share of each ring's stars, N ⟨unit⟩/Σ."""
        return self._per_density(normalisation) * self.ring_mean

    def depth(self, normalisation: float) -> np.ndarray:
        """b(R) = 1 − min_φ(body contrast) = N (⟨unit⟩ − min unit)/Σ: what the saturation reads (item 5)."""
        return self._per_density(normalisation) * (self.ring_mean - self.unit.min(axis=1))

    def deviation(self, normalisation: float) -> np.ndarray:
        """The body's contrast less 1 on the cells' centres, shaped (R, CELLS): N (unit − ⟨unit⟩)/Σ. Its mean
        round a ring is 0 to rounding - the share is the mean of the same samples - and nothing is divided by
        a mean or clipped to make it so."""
        return self._per_density(normalisation)[:, None] * (self.unit - self.ring_mean[:, None])

    def cell_means(self, edges: np.ndarray, angle: float) -> np.ndarray:
        """``unit``'s exact mean over each φ cell between ``edges`` on every grid ring, for a bar along
        ``angle`` (rad): the interpolant integrated piece by piece (``gas_response.sector_mean``), shaped (R, cells)."""
        edges = np.asarray(edges, dtype=float)
        lo = np.broadcast_to(edges[None, :-1] - angle, (self.R.size, edges.size - 1))
        hi = np.broadcast_to(edges[None, 1:] - angle, (self.R.size, edges.size - 1))
        return _cells.sector_mean(self.unit, lo, hi)

    def amplitude(self, edges: np.ndarray, angle: float) -> np.ndarray:
        """The m = 2 Fourier amplitude, on each ring, of the body's part of the published field per unit
        normalisation: of the cell means of unit/Σ over the grid's φ cells. 0 on a ring that holds no body."""
        return self._per_density(1.0) * fourier_amplitude(self.cell_means(edges, angle), edges)


def body_share(body: BarBody, bar_contrast: float, edges: np.ndarray, angle: float) -> float:
    """The body's share of the disc's mass at which the m = 2 amplitude of the published field's bar part,
    at its largest over the grid's rings inside the half-length, is ``bar_contrast`` (D217 item 4: "the drawn
    ``bar_contrast`` B sets the normalisation so that the published field's A₂ maximum inside a equals B").
    The amplitude is linear in the normalisation, so this is one division; 0 where the grid holds no ring
    inside the bar."""
    inside = body.inside
    if not inside.any():
        return 0.0
    peak = float(body.amplitude(edges, angle)[inside].max())
    return body.mass_share(bar_contrast / peak) if peak > 0.0 else 0.0


@dataclass(frozen=True, slots=True, eq=False)
class ModeLaw:
    """The law's parts at every radius, kept apart so each can be read (rows are :data:`ARM_MODES`)."""

    weights: np.ndarray     # w_m(R): the amplifier's weight
    gain: np.ndarray        # w_m / max(1, Σ_k w_k): each mode's share of the sourced power A²
    tapered: np.ndarray     # Ã_m(R) = A √gain (1 − bar taper): before saturation
    bar: np.ndarray         # b(R) = 1 − min_φ(the bar's body's contrast): the body's depth (S58; B × taper until then)
    saturation: np.ndarray  # s(R) = min(1, (1 − b) / Σ_m Ã_m)
    amplitudes: np.ndarray  # A_m(R) = s Ã_m: what multiplies each mode's cosine in the composed field


def mode_law(R: np.ndarray, weights: np.ndarray, arm: float, depth: np.ndarray | float, pitch_deg: float, bar_length: float) -> ModeLaw:
    """The amplitudes of the arm modes at every radius from the amplifier's weights (D215, gate rulings 1-2).

    A_m(R)² = A² w_m(R) / max(1, Σ_k w_k(R)) - the sourced power times the disc's gain, the gain capped
    at one, never normalised up - then the bar's taper, then the saturation s(R) on the arm modes
    together. One fully amplified mode (w = 1, the rest 0) on an unsaturated ring is A (1 − taper):
    S55's arm weight, to the bit.

    ``depth`` is b(R), the bar's body's depth under the ring's mean (:meth:`BarBody.depth`; S58, D217 item 5:
    until then b was the cosine bar's amplitude times its taper) - an array on ``R``, or one number for every
    ring; 0 for an unbarred galaxy, whose ``bar_length`` is NaN and whose taper is 0 on every ring.
    """
    weights = np.asarray(weights, dtype=float)
    gain = weights / np.maximum(1.0, weights.sum(axis=0))
    taper, _, _ = bar_terms(R, pitch_deg, bar_length)
    tapered = arm * np.sqrt(gain) * (1.0 - taper)
    b = np.array(np.broadcast_to(np.asarray(depth, dtype=float), taper.shape))
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
    "GALAXY_INPUTS.md §4b describes is published beside it but not modelled (debt #21). "
    "Not a number for a galaxy with no bar: an unbarred disc has no bar length, and the bar's shape, "
    "amplitude, corotation radius and pattern speed are not numbers either.",
)

BAR_FORMATION_TIME = _scalar(
    "bar_formation_time", "Bar formation time", "Gyr",
    "How long a disc this dominant takes to form a bar: a fitted time scale times the exponential of a fitted "
    "number over the disc's share of the rotation at 2.2 scale lengths - the more of the rotation the disc "
    "provides, the sooner it bars. Published for every galaxy, barred or not. The galaxy is barred where this "
    "time is shorter than the disc's age since its halo assembled; a template may state the observed class "
    "instead, and this number is then still published beside the stated verdict, so a disagreement between "
    "the criterion and the galaxy is visible. 1.5 Gyr at the defaults. The fit is over N-body discs of one "
    "stability parameter; at one disc share its models span a factor of thirty in this time with that "
    "parameter, which is not modelled, and the fit's own errors are about a half of the scale and an eighth "
    "of the number in the exponent. It bars almost every disc the inputs can make, whatever the mass - "
    "measured bar fractions are a half to seven tenths - and no residual is drawn: no source read gives a "
    "scatter between galaxies about a threshold. Infinite for a disc that provides none of its rotation.",
)

BAR_PRESENT_DECL = FieldDecl(
    name="bar_present", label="Barred", unit="dimensionless", kind=Kind.CATEGORY_SCALAR, categories=BAR_PRESENT,
    about=(
        "Whether the galaxy has a bar. Derived, with no draw: yes where the bar's formation time is shorter than "
        "the disc's age since the halo's assembly redshift - the lookback time to that redshift in a flat "
        "universe of the model's own Hubble constant and matter density. A template that states the observed "
        "class replaces this verdict with it; nothing else of the galaxy is touched. Where it reads no, the bar's "
        "length, shape, amplitude, mass share, corotation radius and pattern speed are not numbers, the bar's "
        "body and its gas lanes are absent, the arm modes run to the centre and the three acceptance rows that "
        "measure a bar do not apply."
    ),
)

BAR_AXIS_RATIO = _scalar(
    "bar_axis_ratio", "Bar axis ratio b/a", "dimensionless",
    "The width of the bar's body over its length, in the disc's plane: the body's edge is a boxy generalised "
    "ellipse of this axis ratio. A measured typical value, the same for every bar: no scatter of it was "
    "readable, so none is drawn. Not a number for an unbarred galaxy.",
)

BAR_BOXINESS = _scalar(
    "bar_boxiness", "Bar boxiness", "dimensionless",
    "The exponent of the generalised ellipse that is the bar's body's edge: 2 would be an ellipse, and above "
    "2 the body is boxy, as fitted bars are. Not a number for an unbarred galaxy.",
)

BAR_PROFILE_INDEX = _scalar(
    "bar_profile_index", "Bar profile exponent", "dimensionless",
    "The exponent of the body's surface density along its generalised radius: one minus that radius squared, "
    "raised to this power, and nothing beyond the body's edge at the bar's half-length - the form the bar "
    "decompositions fit, so the body has no free scale of its own. Not a number for an unbarred galaxy.",
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
    "swing_x", "Swing-amplification X at m = 1 (m·X_m)", "dimensionless",
    "Toomre's X_m = κ²R/(2πGΣm) times m, in the Mestel form: 2/disc_dominance, X at m = 1 (S26, "
    "D175) - not X for two arms, which is half of it; until S56 this field was labelled as the "
    "two-armed X, a mislabel of the words and not of the number (D215 ruling 11). The first link of "
    "§4b's chain, disc dominance → the arms the disc can amplify: an m-armed pattern is amplified "
    "vigorously where this number over m and over the shear lies in the level-0 window's range of "
    "1–2. 3.3 at the defaults, so two and three arms are inside the range and four is past its "
    "edge. Kept as the amplitude's coherence input only: since S56 the arm numbers the disc "
    "carries come from the local X at every radius, in the pattern stage.",
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
    "The measured ratio the gas's arms are checked against, and no longer what they are set to: mean "
    "gas surface density inside an arm mask of the source's width over the mean outside it — a ratio "
    "of means, not a peak-to-trough. From S51 to S56 the gas pattern's amplitude was solved from this "
    "number; since S57 the gas pattern is the gas's own steady response to the stellar arms, which "
    "reads no contrast, and this number is the target of a disclosed check held in the tests: the "
    "same ratio measured on the model's response, ring by ring, with the layer on (D216). No stage "
    "reads it. "
    "Its mean is derived as the stellar amplitude's is: the non-grand-design spirals' molecular ratio "
    "plus the two-fold pattern's amplification weight times the way to the grand designs'. No "
    "residual is drawn: the source's spread is over arm segments and radial bins, not galaxies, so it "
    "is not a galaxy-to-galaxy scatter and the galaxy carries the class mean (D210 as amended, debt "
    "#131) [verified: Querejeta et al. 2024, A&A 687, A293, Table 1; docs/READING_GAS_PATTERN.md]. "
    "2.73 at the defaults, where m = 2 sits inside the vigorous range.",
)

ARM_PATTERN_SPEED = FieldDecl(
    name="arm_pattern_speed", label="Arm pattern speed Ω_p(R)", unit="km/s/kpc",
    kind=Kind.FIELD, axes=("R",), ramp=Ramp("viridis", scale="log"), meaningful_zero=True,
    about=(
        "A statement of the frame, not a measurement: the angular speed at which every arm mode is taken "
        "to turn at each radius, which is the disc's own - the circular velocity over the radius. The arms "
        "are material, swing-amplified patterns that turn with the gas at every radius, so there is no "
        "one corotation radius, no gas flows through an arm, and each ring's several modes are steady "
        "together in the one frame that turns with that ring (D216). It is the frame the gas's arm "
        "pattern is solved in. Nothing computes anything from this field: the flow through the arms is "
        "zero by construction, not by a subtraction of two speeds. The bar's pattern speed is another "
        "quantity, a single number drawn through the fast-bar ratio."
    ),
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
    x_one, m_lo, m_hi = swing_window(dominance, shear, float(c["SWING_X_LOW"]), float(c["SWING_X_HIGH"]))
    coherence = swing_weight(2.0, m_lo, m_hi, float(c["SWING_X_HIGH"]), float(c["SWING_X_DEAD"]), float(c["SWING_X_LOW"]), float(c["SWING_X_FLOOR"]))
    floc, grand = float(c["ARM_INTERARM_FLOCCULENT"]), float(c["ARM_INTERARM_GRAND_DESIGN"])
    # The gas's ratio of means, joined between its two classes by the same weight (D210 as amended):
    # a derived mean with no residual, since the source's spread is not galaxy-to-galaxy (#131).
    gas_other, gas_grand = float(c["GAS_ARM_CONTRAST_OTHER"]), float(c["GAS_ARM_CONTRAST_GRAND_DESIGN"])
    # The presence (S58, D217 items 1-3): derived, no draw - the bar's formation time against the disc's age
    # since the halo's assembly redshift; a template's pin, where one is given, replaces the verdict and nothing
    # else (the time is published either way). An unbarred galaxy's bar numbers are NaN (D164).
    formation = bar_formation_time(dominance, float(c["BAR_FORMATION_TIME_SCALE"]), float(c["BAR_FORMATION_EXPONENT"]))
    age = lookback_time(float(ctx.inputs["halo_assembly_z"]), float(c["H0"]), float(c["OMEGA_M"]))
    pin = ctx.inputs.get("bar_present")
    present = formation < age if pin is None else bool(pin)
    nan = float("nan")
    return {
        "bar_formation_time": formation,
        "bar_present": BAR_PRESENT[int(present)],
        "bar_half_length": float(c["BAR_LENGTH_RATIO"]) * R_d if present else nan,
        "bar_axis_ratio": float(c["BAR_AXIS_RATIO"]) if present else nan,
        "bar_boxiness": float(c["BAR_BOXINESS"]) if present else nan,
        "bar_profile_index": float(c["BAR_PROFILE_INDEX"]) if present else nan,
        "disc_dominance": dominance,
        "shear_rate": shear,
        "swing_x": x_one,  # 2/f_d = m·X_m: X at m = 1, not X for two arms (D215 ruling 11)
        "swing_arm_min": m_lo,
        "swing_arm_max": m_hi,
        "arm_contrast_mean": contrast_amplitude(floc + (grand - floc) * coherence),
        "gas_arm_contrast": gas_other + (gas_grand - gas_other) * coherence,
        # S57 (D216): the frame every arm mode is steady in, Ω_p(R) = Ω(R) = v_c/R. A statement, published so
        # that the frame is on the record; no stage reads it and the flow through the arms is 0 by construction.
        "arm_pattern_speed": total / R,
    }


BAR = IMPLEMENTATIONS.register(
    Stage(
        id="bar", slot="bar", checkpoint=3,
        about=(
            "The bar's size, the disc's shear, and what the disc can amplify — everything about the "
            "pattern that has no draw in it. Split from the seeded half so that row 15 stays "
            "reproducible (D55). Since S26 it publishes the swing-amplification window and the mean "
            "arm amplitude, derived from disc_dominance and shear_rate (D175); since S51 the gas's "
            "arm–interarm ratio of means, derived the same way with no draw (D210 as amended) - since S57 "
            "the target of a disclosed check and no stage's input; and since S57 the frame the arm modes "
            "are steady in, the disc's own angular speed at each radius (D216). Since S58 it says whether "
            "the galaxy has a bar at all - the time the disc takes to form one against the disc's age since "
            "the halo assembled, with no draw, or the observed class where a template states it - and the "
            "shape of the bar's body; an unbarred galaxy's bar numbers are not numbers (D217)."
        ),
        compute=compute_bar,
        # S58 (D217 items 1-2): the assembly redshift, for the disc's age, and the pin - an input that is not a
        # control and not a seed, given by a template or not at all (read with .get: absent, the stage derives).
        reads_inputs=("halo_assembly_z", "bar_present"),
        reads_constants=(
            "BAR_LENGTH_RATIO", "SWING_X_LOW", "SWING_X_HIGH", "SWING_X_DEAD", "SWING_X_FLOOR",
            "ARM_INTERARM_GRAND_DESIGN", "ARM_INTERARM_FLOCCULENT",
            "GAS_ARM_CONTRAST_GRAND_DESIGN", "GAS_ARM_CONTRAST_OTHER",
            "BAR_FORMATION_TIME_SCALE", "BAR_FORMATION_EXPONENT", "H0", "OMEGA_M",
            "BAR_AXIS_RATIO", "BAR_BOXINESS", "BAR_PROFILE_INDEX",
        ),
        requires=("disc_scale_length_spin", "circular_velocity", "halo_circular_velocity"),
        publishes=(BAR_HALF_LENGTH, DISC_DOMINANCE, SHEAR, SWING_X, SWING_ARM_MIN, SWING_ARM_MAX, ARM_CONTRAST_MEAN,
                   GAS_ARM_CONTRAST, ARM_PATTERN_SPEED,
                   BAR_FORMATION_TIME, BAR_PRESENT_DECL, BAR_AXIS_RATIO, BAR_BOXINESS, BAR_PROFILE_INDEX),
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
    "galaxy whose label reads 6 carries three to six arms at once inside, four to six at the solar "
    "radius and six alone on its last rings; the label weighs the amplitudes as published, the bar's "
    "taper in them, so it leans to the arm numbers of the outer disc. Not a number at all where no mode carries any power - a disc that amplifies nothing, or "
    "a draw of no arm amplitude: a galaxy with no arms has no arm number. From S26 to S55 this was a "
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
            "never normalised up. At the defaults three to six arms share the inner disc, four to six the solar "
            "radius and six alone the last rings; past about 12 kpc no mode with six arms or fewer survives. "
            "The same with the randomness "
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
        "1 where the modes' amplitudes and the depth of the bar's body under the ring's mean add up to less than "
        "1, and below 1 where they would not - "
        "one minus that depth, over the sum of the modes' tapered amplitudes. It depends on the "
        "radius only, never on the phases, so the density contrast is non-negative for every realisation and "
        "nothing is floored. Five modes of equal power peak at √5 times the amplitude of one, so a strong draw "
        "of the arm amplitude saturates the rings that carry the most modes and loses power there; 1 on every "
        "ring at the default seeds. Labelled seeded as the amplitudes it is made from are (D55)."
    ),
)

BAR_CONTRAST = _scalar(
    "bar_contrast", "Bar amplitude (largest m = 2 amplitude)", "dimensionless",
    "The largest two-fold Fourier amplitude of the bar's body round a ring, over the rings inside the bar's "
    "half-length: the number the bar surveys measure, and what the body's mass is set from - the body is "
    "normalised so that its part of the stellar density contrast has exactly this amplitude at its strongest "
    "ring. Since S26 drawn log-normally on pattern_seed about the S4G barred sample's median "
    "with its 16th–84th-percentile width, capped at 0.9 (D175); until then an experimental input (D171); until "
    "S58 the amplitude of a single cosine tapered off beyond the bar's half-length. Drawn on the same stream "
    "whether the galaxy is barred or not, and not a number for an unbarred galaxy.",
    provenance="seeded",
)

BAR_MASS_SHARE = _scalar(
    "bar_mass_share", "Bar body's share of the disc's mass", "dimensionless",
    "The mass of the bar's body over the mass of the disc, both summed over the grid's rings - the disc "
    "being the checkpoint-1 total disc, stars and gas together and no bulge, because the pattern precedes "
    "star formation: a declared approximation. It follows from the drawn bar amplitude: the body's "
    "normalisation is the one that gives its strongest ring that two-fold amplitude, and this is the mass that "
    "normalisation holds. Every reader of the pattern builds the body from this number, so all of them build "
    "the same one. The body takes its mass ring by ring from the ring's own stars, so no ring's total changes; "
    "on a ring the body's share runs to about four tenths at the defaults. About 0.10 at the defaults, beside "
    "a measured tenth of a galaxy's whole light - a comparison that waits for the stellar disc and the bulge. "
    "0 on a grid with no ring inside the bar, and not a number for an unbarred galaxy. Labelled seeded: it "
    "carries the drawn bar amplitude and the drawn pitch (D55).",
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
        "branch, and their number changes outward. Inside the bar's half-length, the bar's body: a boxy, "
        "elongated component along the bar's axis whose surface density falls smoothly to nothing at its "
        "edge, its mass taken ring by ring from the ring's own stars - each ring loses the body's share "
        "everywhere and holds the body where the body is - against the checkpoint-1 total disc (no split "
        "into stars and gas and no bulge there: a declared approximation). The body's value in a cell is its "
        "mean over the cell's extent in azimuth, on the ring; the arm modes are read at the cell's centre. "
        "In a barred galaxy the two-armed mode's crest lies on the bar's axis at the bar's end; an unbarred "
        "galaxy has no body and its arms run to the centre. Nowhere negative: "
        "where the modes would add up to more than the body leaves of the mean they are scaled down together. "
        "A composed field: with the randomness layer off it is 1 everywhere - the amplitudes, the pitch and "
        "the body's mass are still published, and nothing says where the arms are."
    ),
)


@dataclass(frozen=True, slots=True, eq=False)
class ArmPattern:
    """The stellar pattern of several modes and the bar's body: everything the density contrast needs, read
    from published fields in one place (rule A9).

    c(R, φ) = 1 − β(R) + Σ_bar(R, φ)/Σ(R) + Σ_m A_m(R) cos(m χ − θ_m), χ = φ − ln R · cot(pitch).

    **Evaluable at a point** (BUILD_III section 1c rule 5, D60): the amplitudes at an arbitrary radius are
    the published radial fields ``arm_mode_amplitude_m`` interpolated linearly in R between the grid radii
    they are published at (held at the end values beyond them); at a grid radius that is the field
    exactly. The winding phase and the bar's angle are closed forms of R. The phases are the layer's five
    scalars; all zero is the convention S55 had.

    **The bar's body** (S58, D217 items 4-5) is :class:`BarBody` at the normalisation the published
    ``bar_mass_share`` states, laid on the fixed cells of each grid ring in the bar's frame. A point reads
    its two neighbouring grid rings' profiles at its own φ − φ_bar - linear between the cells' centres -
    and blends them linearly in R (the gas pattern's way, D216 item 9); a ring past the body's edge holds
    none of it. :meth:`sector_means` and :meth:`published` take the body's exact mean over a sector
    (``gas_response.sector_mean``), so sectors that tile a ring average to 1 to rounding on any grid, with
    nothing divided. Until S58 the bar was one cosine, B e^{−(R/a)⁴} cos 2(φ − φ_bar).

    **No bar** (D217 item 3): a bar amplitude and a half-length that are both NaN are an unbarred galaxy -
    no body, no taper, the modes as published - and not an unresolved pattern.

    Built through ``galaxy.layer.compose`` (the one reader of the layer's switch) and by tests.
    """

    R: np.ndarray            # the grid radii the amplitudes are published at
    amplitudes: np.ndarray   # (modes, R): arm_mode_amplitude_m, with the taper and the saturation in them
    phases: tuple[float, ...]  # θ_m, one per mode of ARM_MODES
    bar: float               # B, the published bar_contrast: NaN for an unbarred galaxy
    pitch_deg: float
    bar_length: float        # a, kpc: NaN for an unbarred galaxy
    axis_ratio: float = float("nan")    # q, the body's
    boxiness: float = float("nan")      # c
    index: float = float("nan")         # n, the profile's exponent
    share: float = float("nan")         # the published bar_mass_share: the body's normalisation, as a mass share
    surface_density: np.ndarray | None = None  # (R,): checkpoint 1's total disc Σ, M☉/pc², which the share is of
    flat: bool = field(init=False)
    barred: bool = field(init=False)
    body: BarBody | None = field(init=False, repr=False)
    normalisation: float = field(init=False)  # N, M☉/pc²: the body's surface density is N · body.unit
    _deviation: np.ndarray | None = field(init=False, repr=False)  # (R, CELLS): the body's contrast less 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "R", np.asarray(self.R, dtype=float))
        object.__setattr__(self, "amplitudes", np.asarray(self.amplitudes, dtype=float))
        object.__setattr__(self, "phases", tuple(float(p) for p in self.phases))
        if self.amplitudes.shape != (len(ARM_MODES), self.R.size) or len(self.phases) != len(ARM_MODES):
            raise ValueError(
                f"a pattern holds {len(ARM_MODES)} modes on its {self.R.size} radii; got amplitudes "
                f"{self.amplitudes.shape} and {len(self.phases)} phases"
            )
        # The bar. Both of its numbers NaN: an unbarred galaxy (D217 item 3), which is a pattern like any other.
        # Both finite: a bar, whose body needs its shape, its share and the disc it is a share of. Anything else
        # - one of the two missing, a body that cannot be built - is a pattern the grid could not resolve.
        unbarred = math.isnan(self.bar) and math.isnan(self.bar_length)
        barred = math.isfinite(self.bar) and math.isfinite(self.bar_length)
        body: BarBody | None = None
        normalisation, deviation = 0.0, None
        resolved = unbarred
        if barred:
            shape = (self.axis_ratio, self.boxiness, self.index, self.share)
            if all(math.isfinite(v) for v in shape) and self.surface_density is not None and self.share >= 0.0:
                body = BarBody(self.R, self.surface_density, self.bar_length, self.axis_ratio, self.boxiness, self.index)
                normalisation = body.normalisation(self.share)
                resolved = True
                if normalisation > 0.0:
                    deviation = body.deviation(normalisation)
                    deviation.setflags(write=False)
        object.__setattr__(self, "barred", barred and resolved)
        object.__setattr__(self, "body", body)
        object.__setattr__(self, "normalisation", normalisation)
        object.__setattr__(self, "_deviation", deviation)
        # No perturbation to apply: no arm amplitude and no body, or a pattern the grid could not resolve (a
        # mesh too coarse for the shear gives a NaN pitch) or the layer did not realise (NaN phases), which
        # stays axisymmetric. Decided once: the censuses ask per cell.
        scalars = (self.pitch_deg, *self.phases)
        finite = resolved and all(math.isfinite(v) for v in scalars) and bool(np.all(np.isfinite(self.amplitudes)))
        if finite and deviation is not None and not math.isfinite(bar_terms(self.R, self.pitch_deg, self.bar_length)[2]):
            finite = False  # a body with no angle to lie along
        object.__setattr__(self, "flat", not finite or (not self.amplitudes.any() and deviation is None))

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
            float(fields["bar_axis_ratio"]), float(fields["bar_boxiness"]), float(fields["bar_profile_index"]),
            float(fields["bar_mass_share"]), np.asarray(fields["disc_surface_density"], dtype=float),
        )

    # --- the bar's body ---------------------------------------------------------------------------------

    @property
    def bar_angle(self) -> float:
        """The bar's position angle, rad: the winding's phase at the bar's end. NaN for an unbarred galaxy."""
        return bar_terms(self.R, self.pitch_deg, self.bar_length)[2]

    @property
    def ring_share(self) -> np.ndarray:
        """β on the grid rings: the body's share of each ring's stars; 0 where there is no body."""
        return np.zeros(self.R.size) if self.body is None else self.body.ring_share(self.normalisation)

    @property
    def depth(self) -> np.ndarray:
        """b on the grid rings: 1 − min_φ of the body's contrast, what the saturation reads; 0 with no body."""
        return np.zeros(self.R.size) if self.body is None else self.body.depth(self.normalisation)

    def body_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray | float:
        """The body's contrast less 1 at points, ``R`` and ``phi`` broadcast against each other: each point
        reads its two neighbouring grid rings at its own φ − φ_bar - ``gas_response.interpolate``'s arithmetic
        on the two cells it lies between - and blends them linearly in R. 0.0 where there is no body."""
        deviation = self._deviation
        if deviation is None:
            return 0.0
        R, psi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(phi, dtype=float) - self.bar_angle)
        lower, upper, share = ring_bracket(self.R, R)
        below, above, weight, _ = _cells.bracket(psi, CELLS)

        def read(ring: np.ndarray) -> np.ndarray:
            first, second = deviation[ring, below], deviation[ring, above]
            rising = second >= first
            return np.where(rising, first, second) + np.where(rising, weight, 1.0 - weight) * np.abs(second - first)

        return (1.0 - share) * read(lower) + share * read(upper)

    def body_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray | float:
        """The body's contrast less 1 averaged over each azimuthal cell between ``edges`` at each radius of
        ``R``, shaped (R, cells): the exact mean of :meth:`body_at` over the cell - the two neighbouring
        rings' interpolants integrated piece by piece and blended as a point blends them. 0.0 with no body."""
        deviation = self._deviation
        if deviation is None:
            return 0.0
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        angle = self.bar_angle
        lo = np.broadcast_to(edges[None, :-1] - angle, (R.size, edges.size - 1))
        hi = np.broadcast_to(edges[None, 1:] - angle, (R.size, edges.size - 1))
        lower, upper, share = ring_bracket(self.R, R)
        return ((1.0 - share)[:, None] * _cells.sector_mean(deviation[lower], lo, hi)
                + share[:, None] * _cells.sector_mean(deviation[upper], lo, hi))

    # --- the arm modes ----------------------------------------------------------------------------------

    def amplitudes_at(self, R: np.ndarray) -> np.ndarray:
        """(modes, …R's shape): each mode's amplitude at ``R``, linear in R between the grid radii."""
        R = np.asarray(R, dtype=float)
        return np.stack([np.interp(R, self.R, row) for row in self.amplitudes])

    def _terms(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Per radius: the modes' amplitudes and the winding phase."""
        _, phase, _ = bar_terms(R, self.pitch_deg, self.bar_length)
        return self.amplitudes_at(R), phase

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

    def arms(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray | float:
        """Σ_m A_m(R) cos(m χ − θ_m) on the (R, φ) mesh: the arm modes alone, with no body and no 1."""
        amp, phase = self._terms(R)
        return self._arms([a[:, None] for a in amp], np.asarray(phi, dtype=float)[None, :] - phase[:, None])

    # --- the contrast -----------------------------------------------------------------------------------

    @staticmethod
    def _whole(value: np.ndarray | float, shape: tuple[int, ...]) -> np.ndarray:
        """``value`` on ``shape``: where the points asked for carry no mode and no body (an unbarred galaxy
        past its last arm) the contrast is the one number 1, and it is returned on every point."""
        return np.full(shape, value) if np.ndim(value) == 0 else value

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ(R, φ)/Σ(R) at the points of an (R, φ) mesh: the point function at each (R_i, φ_j), what a census
        inverts for an azimuth. Its mean round a ring is 1 over the ring itself: every m is an integer, and
        the body's share is the mean of its own profile."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        return self._whole(1.0 + self.arms(R, phi) + self.body_at(R[:, None], phi[None, :]), (R.size, phi.size))

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise (S48: each
        bright star inverts its own row of azimuths inside its own cell)."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        amp, phase = self._terms(R)
        return self._whole(1.0 + self._arms(list(amp), phi - phase) + self.body_at(R, phi), np.broadcast_shapes(R.shape, phi.shape))

    def published(self, R: np.ndarray, phi: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """What the stage publishes on the grid: at each radius of ``R``, the arm modes at the cells' centres
        ``phi`` - as they have been published since S56, a cosine's samples having no mean - and the body's
        exact mean over each cell between ``edges``. A ring's cells average to 1 to rounding on any grid, with
        nothing divided; the m = 2 Fourier amplitude of its body part, at its largest ring, is the published
        bar amplitude."""
        R = np.asarray(R, dtype=float)
        return self._whole(1.0 + self.arms(R, phi) + self.body_cell_means(R, edges), (R.size, np.size(phi)))

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` at one radius, exactly: the modes' own
        integrals, each a sine difference, and the body's interpolant integrated piece by piece - no
        quadrature. Sectors that tile the ring average to 1 to rounding."""
        radius = np.array([float(R)])
        amp, phase = self._terms(radius)
        edges = np.asarray(edges, dtype=float)
        a, b = edges[:-1], edges[1:]

        def mean_cos(m: float, shift: float, theta: float = 0.0) -> np.ndarray:
            return (np.sin(m * (b - shift) - theta) - np.sin(m * (a - shift) - theta)) / (m * (b - a))

        arms: np.ndarray | float | None = None
        for m, theta, row in zip(ARM_MODES, self.phases, amp):
            if row[0] == 0.0:
                continue
            term = row[0] * mean_cos(float(m), float(phase[0]), theta)
            arms = term if arms is None else arms + term
        body = self.body_cell_means(radius, edges)
        means = 1.0 + (0.0 if arms is None else arms) + (body if isinstance(body, float) else body[0])
        # A radius with no mode and no body (an unbarred galaxy past its last arm) is 1 in every sector.
        return np.full(a.shape, means) if np.ndim(means) == 0 else means

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
    # S58 (D217 item 3): a half-length that is not a number is an unbarred galaxy. Every draw below is made on
    # its own stream whether the galaxy is barred or not - a barred galaxy's numbers do not move because
    # unbarred galaxies exist - and an unbarred galaxy's bar numbers are published as NaN (D164).
    a_bar = float(ctx.fields["bar_half_length"])
    barred = math.isfinite(a_bar)
    nan = float("nan")
    total = np.asarray(ctx.fields["circular_velocity"])

    ratio = ctx.rng("pattern_seed", "fast_bar").normal(
        float(ctx.constants["FAST_BAR_RATIO"]), float(ctx.constants["FAST_BAR_SCATTER"])
    )
    corotation = max(float(ratio), 0.1) * a_bar if barred else nan
    v_cr = float(np.interp(corotation, R, total)) if barred else nan

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
    # The bar's body (S58, D217 items 4-5): the drawn amplitude sets its normalisation - the one at which the
    # m = 2 amplitude of the published field's bar part, at its largest ring inside the half-length, is the
    # drawn B - and that normalisation is published as the body's share of the disc's mass. A law: it reads the
    # grid's own φ cells, the disc and the bar's angle (the drawn pitch's), and no realisation of the layer, so
    # it is the same with the layer on or off. The depth the saturation reads is then taken from the published
    # share, as every reader of the pattern will take it.
    phi_edges = ctx.grid["phi"].edges
    share, depth = nan, np.zeros(R.size)
    if barred:
        angle = bar_terms(R, pitch_angle, a_bar)[2]
        body = BarBody(R, sigma, a_bar, float(ctx.fields["bar_axis_ratio"]), float(ctx.fields["bar_boxiness"]),
                       float(ctx.fields["bar_profile_index"]))
        if math.isfinite(angle):  # a pitch the mesh could not resolve leaves the bar no angle: no body, no share
            share = body_share(body, bar_contrast, phi_edges, angle)
            depth = body.depth(body.normalisation(share))
    else:
        bar_contrast = nan
    law = mode_law(R, weights, arm_contrast, depth, pitch_angle, a_bar)
    amplitudes = {name: law.amplitudes[k] for k, name in enumerate(AMPLITUDE_FIELDS)}
    cells = (R.size, ctx.grid.phi.size)

    def composed() -> np.ndarray:
        # The law applied to the realisation: the pattern object is compose's, built from what this stage has
        # just made and the layer's phases. A pattern with nothing to place is the neutral. The arm modes at
        # the cells' centres, the body as its exact mean over each cell (S58).
        shape = _compose.stellar_pattern(
            ctx.fields, R,
            law={**amplitudes, "bar_contrast": bar_contrast, "pitch_angle": pitch_angle, "bar_mass_share": share},
        )
        if shape is None or shape.flat:
            return _compose.neutral(DENSITY_CONTRAST, cells)
        return shape.published(R, ctx.grid.phi, phi_edges)

    return {
        "bar_corotation_radius": corotation,
        "bar_pattern_speed": (v_cr / corotation if corotation > 0.0 else 0.0) if barred else nan,
        "pitch_angle": pitch_angle,
        "arm_multiplicity": dominant_mode(R, sigma, law.amplitudes),
        "arm_contrast": arm_contrast,
        "bar_contrast": bar_contrast,
        "bar_mass_share": share,
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
            "lie is the randomness layer's, on its own seed. Since S58 the bar is a body and not a cosine: "
            "a boxy two-dimensional component whose mass is set from the drawn bar amplitude and taken ring "
            "by ring from the checkpoint-1 disc, published as a share of that disc; an unbarred galaxy has "
            "none, and its bar numbers are not numbers (D217)."
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
            # S58 (D217 item 4): the body's shape, the derived stage's. The surface density the body is a share
            # of is the one above: checkpoint 1's total disc - no stellar/gas split and no bulge here.
            "bar_axis_ratio", "bar_boxiness", "bar_profile_index",
        ),
        publishes=(COROTATION, PATTERN_SPEED, PITCH_ANGLE, ARM_MULTIPLICITY, ARM_CONTRAST, BAR_CONTRAST, BAR_MASS_SHARE,
                   *ARM_MODE_AMPLITUDES, ARM_SATURATION, DENSITY_CONTRAST),
    )
)
