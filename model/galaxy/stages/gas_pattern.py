"""The gas's own arm pattern (checkpoint 3; S51, D210; since S57 the gas's steady response to the stellar arms, D216).

The stellar pattern (``pattern``) is a sum of cosine modes whose crests the randomness layer places. The gas
is not that field: it answers the modes' potential. From S51 to S56 the answer was stated as a shape - a von
Mises ridge of a measured width, its amplitude set from a measured ratio of means, since S56 laid round each
ring in the order of the stellar modes' sum. Gate G2 of S57 (DECISIONS.md D216) retired the shape for a law:
on every ring the gas takes **the steady response of isothermal gas that turns with the arms**, solved by
``gas_response`` (the instrument, certified in ``tests/test_gas_response.py``), and nothing of the ridge is
put in.

- **The frame** (D216 items 1-2). Every arm mode turns with the gas, Ω_p(R) = Ω(R): the swing-amplified arms
  of the reading (``docs/READING_GAS_SHOCK.md`` Part B) and the only frame in which a ring's several modes are
  steady together. So nothing flows through an arm and nothing shocks in it: there is no sonic point and no
  jump. The derived ``bar`` stage publishes that frame as ``arm_pattern_speed``; nothing here reads it, and
  the flow handed to the solver is 0 by construction.
- **The law** (item 5), on each grid ring, with χ = φ − Φ(R) the pattern coordinate (Φ = ln R · cot p until S59; since
  then the winding in seeded segments, ``pattern.Winding`` - geometry only: ε and f below keep the disc's own
  pitch p, a declared approximation, D218 item 4: "the gas answers each ring at the disc's mean pitch; on a
  segment its normal wavenumber is off by sin p/sin p_seg") and s(χ) the gas's
  surface density over its ring mean:

      ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(m χ − θ_m)

  ε = a/(κ R sin p), a the cold gas's velocity dispersion taken as its isothermal sound speed (the one the
  star-formation threshold reads: there is no second); f_m = m A_m/(X sin p), X = κ²R/(2πGΣ) the arm-number
  law's own variable with checkpoint 1's total disc Σ (``pattern.local_swing_x``); A_m the mode's cosine
  amplitude **before the bar's taper** - the published amplitude over (1 − taper), which is the arm amplitude
  times :meth:`GasPattern.unit_amplitudes`; θ_m the layer's phases. **The forcing's amplitude carries the
  saturation** (gate G3 item 3): A_m is the stellar field's actual cosine amplitude on the ring with the
  taper taken back out - the arm amplitude times the root of the mode's gain times the pattern stage's
  saturation factor, which is under 1 where the modes' linear sum would reach the mean - "because the gas
  answers the stars that exist". Uniform potential vorticity closes the equation (item 3). It is the
  Euler-Lagrange equation of a strictly convex functional, so on every ring the solution exists, is unique,
  is positive and has mean 1. A ring that carries no mode has s = 1.
- **Nothing is put in and nothing is mended.** No amplitude, width, mask or contrast enters; no thickness
  factor, no constant added, no f scaled; nothing clipped, floored, capped or divided by a sampled mean. A
  ring the solver cannot converge raises (``gas_response.ConvergenceError``) and is not caught: there is no
  fallback and no linear substitute (item 7). The solver holds a cell's residual under 1e-10 or under the
  cell's rounding floor where that is larger (gate G3 item 2), so a tightly wound galaxy's rings - a drawn
  pitch under about 2.7 degrees, ε of order 1, a total forcing of 60-80 - converge as every other ring does.
  That regime is published as the law gives it, nothing clipped: s from 1e-44 to 14, the arm-to-arm spacing
  then comparable to the disc's thickness and the razor-thin forcing overstated by about that factor (a
  finding under the razor-thin debt, below).
- **The bar** (item 8; since S58 its gas lanes, DECISIONS.md D217 items 6-8). g = w_arm s + w_bar L(R, φ),
  w_bar the bar's taper, w_arm = 1 − w_bar (their sum is checked); the taper, the winding phase and the bar's
  angle are the stellar pattern's own (``pattern.bar_terms``). The taper acts once, here, on the response to
  the untapered forcing. **L is the lane field** (:func:`lane_profiles`), of ring mean 1 and positive: on each
  ring inside the bar's half-length a uniform base and two lanes - point-symmetric arcs of constant curvature
  on the bar's *leading* side (:func:`rotation_sense`: the arms trail, so the disc turns towards decreasing
  φ), each from the bar's end on its major axis to its minor axis at the nuclear ring, concave towards the
  major axis; the mean inside the stellar body's footprint is a measured ratio times the mean outside it, and
  the excess lies on the lanes with a Gaussian profile across the arc. So g ≥ w_bar min L > 0 in the law and
  the ring's mean is 1. (As published: g ≥ 0, equal to 0 only where s underflows the doubles' subnormals on
  a ring that has no bar's term - every such cell counted and recorded in tests/test_bar.py; nothing is
  clipped.) Nothing is drawn: the lanes are deterministic given the bar's length, shape and angle. They are
  a **synthetic template** standing in for the two-dimensional gas flow in the bar's potential; the lane's
  width is a declared placeholder with no source. The one-dimensional steady shocked branch is not the bar's
  instrument - a bar is not a tightly wound forcing - and is not built (D217). Until S58 the bar's term was
  the stellar bar's own cosine, 1 + B cos 2(φ − φ_bar). **An unbarred galaxy has no lanes and no taper**:
  g = s on every ring.
- **What the star formation law reads** (D217's follow-up at the gate). The lanes' width is a placeholder no
  source gave, and a census must not be driven by it. So the stage publishes a second composed field,
  ``star_formation_gas_contrast``: g_sf = w_arm s + w_bar L_fp, the same blend with **the footprint-uniform
  field** L_fp in the lanes' place (:func:`footprint_profiles`) - the same base outside the footprint and the
  same excess, spread evenly over the footprint instead of on the arcs, so the measured ratio of the gas
  inside the footprint to the gas outside it is kept and there is no ridge. ``sfr_modulation`` reads that
  field, and through it the star sample's and the bright catalogue's young stars: star formation follows the
  bar's footprint and not the placeholder's ridge. ``gas_density_contrast``, the dust's placement and the
  cloud census (and so the clusters, born in the clouds) keep L. On every grid ring at or past the
  half-length, and on every ring of an unbarred galaxy, the two published fields are the same bits: the two
  templates are the same array of ones there (or there is no bar's term at all) and the arithmetic is the
  same.
- **At a point** (item 9). The equation is solved once per grid ring on ``gas_response.CELLS`` cells. A point
  at (R, φ) reads the two neighbouring grid rings' profiles **at its own χ** (the winding at the point's own
  radius), linear in χ between the cells' centres and linear in R between the two rings, held at the end
  rings beyond the grid; the taper is taken at the point's own radius, and the lanes are read the same way
  as the response, in the bar's frame (the two rings' lane profiles at the point's own φ − φ_bar). All the
  blends are convex blends of positive profiles of mean 1, so the gas is positive and its mean round the ring
  is 1 at every radius. :meth:`GasPattern.sector_means` is the exact mean of that same interpolant, so
  sectors that tile a ring average to 1 to rounding.
- **The published field is the law's exact mean over each grid cell's extent in azimuth, at the ring's own
  radius** (gate G3 item 4, which rewords items 9 and 11 i): on each grid ring, the interpolant integrated
  exactly over each of the grid's φ cells (:meth:`GasPattern.cell_means`, the arithmetic of the sector means;
  the lanes' interpolant the same way). It is not a mean over the cell's extent in R: a point between two
  rings is blended in R, as above. So a ring's cells average to 1 to rounding on every φ grid, with no
  division - a field of centre samples did only on grids whose cell count divides the solver's (7e-14 off at
  360 cells, 2e-3 at 36) - and each cell holds the gas the law puts on its ring there. ``contrast_at``,
  ``response_at``, ``azimuths`` and the censuses keep the point function: a cell's expected count is its area
  times its mean, a placed object reads the law at its own point, and the two are the same measure.
- **The offset** (D210 ruling 3, now derived; gate G3 item 7 and its follow-up): zero for a lone mode,
  exactly, by the equation's symmetry about the mode's crest; with several modes, within half a degree over
  the mid disc on the Milky Way template and up to about a degree on ``ngc_4414`` - the mode-by-mode
  weighting (each mode is answered with its own weight, m/(1 + m²ε²) in the linear limit, against the stars'
  1), measured, not ruled; no offset is put in and none is published. As read on the solver's cells (a
  quarter of a degree each), the tallest crest of s against the tallest crest of the stellar modes' sum,
  **since S58, with the two-armed mode's phase the bar's**: the Milky Way template within one cell on 50 of
  53 rings over 6-10 kpc (three read two) and on 103 of the 165 rings that carry a mode, 53 reading two cells
  and two three (on two more, where six nearly equal crests stand, the tallest is another arm's);
  ``ngc_4414`` up to 5 cells (1.25 degrees) over 6-10 kpc and 7 at most over the disc. (As S57 read the
  Milky Way template, its two-armed phase a draw: within one cell on 53 of 53 and on 161 of 165.) **It has
  no one sign**: on the Milky Way template the gas's crest sits to the larger χ on 52 of the 53 mid-disc
  rings and to the smaller χ on the 12 rings inside 0.9 kpc; on ``ngc_4414`` to the smaller χ on 27 of the
  53, the larger on 6, and over its disc 95 rings to the smaller and 16 to the larger; over the suite's 240
  seeded galaxies both sides are met (12 008 rings to the smaller χ, 13 738 to the larger, 9 280 on the same
  cell, of the rings whose two tallest crests are the same arm's). It is the modes' weighting, not a
  displacement downstream or upstream of the arm.
- **Declared approximations, each a debt** (items 4-5): steadiness (the response relaxes on the ridge's
  sound crossing, about as long as an arm lives); the razor-thin WKB potential, which overstates the high
  arm numbers; the stellar mode's fractional amplitude applied to the total disc.

**Since S60 the gas answers a census of arm pieces (BUILD_III Phase P5; DECISIONS.md D219 items 5-6), and
where the text above speaks of modes, phases, a pattern coordinate χ and a common winding it is history.** The
equation, the frame, the solver, the bar's lanes and the composition with them are unchanged. What changed:

- *The forcing* is composed piece by piece. On a ring every stellar arm piece within reach of it is a ridge on
  the solver's cells - a Gaussian in the perpendicular distance to its locus times its window along it
  (``pieces.py``; the gate's second follow-up, item 1: "a ring's profile of a piece is the Gaussian in d times the
  window in s on the solver's cells ... the forcing term by term as now"; from the first build to the second a
  piece on a ring was a wrapped Gaussian in azimuth, which smeared a nearly circular piece round its whole
  ring). The ridge is transformed on those cells, and its m-th term - its amplitude the stars' own on the
  ring, the cut in it, the bar's taper taken back out - is multiplied by m / (X (|sin p_j| + m h_z/R)): **the
  piece's own pitch p_j**, and the thickness of the stellar layer, whose force on the gas at the midplane is
  the razor-thin one times 1/(1 + k h_z) for stars in an exponential layer (the exact form; the sech² layer's
  is the named alternative). h_z is the checkpoint-1 scale length over a measured flattening, so nothing of a
  later checkpoint enters. The factor is bounded by R/(X h_z) for every m and pitch and regular at sin p = 0:
  the blow-up of a tightly wound disc's razor-thin forcing cannot occur. ε keeps the disc's own pitch (one
  pressure scale per ring: declared, a debt). Every term the cells hold is kept, 1 to half their number: a
  window that ends square at a join is no smooth function, and its high terms are bounded by the same factor.
  The sum of the pieces' terms, taken back to the cells, is the forcing, in the galaxy's own azimuth: a
  profile is held at φ, and there is no χ.
- *Between two rings* a ring's solved profile is **carried along the pieces' loci** (:meth:`GasPattern.carried`):
  a periodic piecewise-linear map of azimuth, anchored where each piece that crosses the ring stands on the
  ring and at the point's radius - in place of the common winding's one shift. The carried profile is taken
  over its own mean round the ring at the point's radius (exact, and 1 at the ring's own radius), so each
  ring's term is a redistribution at every radius: the builder's choice where the ruling is silent. A point
  blends its two rings' carried profiles linearly in R, as before. **Dividing the carried profile by its own
  exact mean at the point's radius is part of the map's definition** (the gate's first follow-up, item 6: "a
  non-rigid map keeps no mean; I2 needs it ... it is not the forbidden division of a published field"): the mean
  is the exact integral of the carried interpolant - on each stretch between two anchors the map is linear -
  and sectors that tile a ring average to 1 to 5e-14 at any radius (pinned in ``tests/test_pieces.py``).
- *The rings solved between the grid's* (the same item, built at the second follow-up's order): "where the
  mid-gap misplaced weight passes 1 %, solve a ring at the mid-gap and carry from it, recursing at most twice
  (quartering), then record what remains; the check is that solve". The pattern's store of solved rings holds
  the grid's and, in the gaps that need them, one at the middle and ones at the quarters; a point reads the two
  solved rings it lies between. They are looked for the first time a radius off the grid's own rings is read.
  What remains over 1 % is recorded in the tests: the gaps that hold a radius at which the stellar field itself
  steps or turns over within the gap - a join, a lone chain's free end, a nearly circular piece.
- *The disclosed check's measurements* read the same solved rings: the mask is laid where the stellar pieces'
  sum is highest, for the law's own arm number on the ring; the "mode the gas answers most strongly" is the
  harmonic of largest forcing.

**What became of the ridge's numbers** (item 11 iv; gate G3 items 6-7). The measured ratio of means, the mask
it is measured in and the measured width build nothing. They survive as the target and the definition of a
*disclosed check*, made by the measurement functions at the foot of this module and pinned in the tests,
layer on: the ratio of the means of s inside the source's arm mask against outside it (:func:`mask_share`,
:func:`ratio_of_means`), and the full width at half maximum of a ring's tallest crest (:func:`crest_width`)
over the period of the mode the gas answers most strongly, the one of largest forcing m·A_m. As read over
6-10 kpc: the ratio a hit on the Milky Way template (median 2.571, 53 of 53 rings inside the source's band) and
on ``ngc_4414`` but for its seven outer rings (median 1.881); the width a miss on every ring, 2.52-2.83 times
the measured 0.17 on the Milky Way template (2.49-2.83 until S58 tied the two-armed mode's phase to the bar) and
2.82-3.09 times on ``ngc_4414``. No stage
computes with them, and the mask's width and the measured width are no constants of the model: they left its
registry at gate G3 ("a stage may not declare reads it does not make") and live in ``tests/`` with their
sources; the measuring functions take the mask's width as an argument. The measured ratio's class means stay
constants: the ``bar`` stage derives the check's target from them.

**One solve per pattern.** A pattern object solves its rings the first time a profile is asked for and keeps
them. Several stages of one run build the same pattern (the stage here, the cloud census, its texture, the
cluster census), so the last few solutions are also kept by content - a digest of the forcing amplitudes,
the phases and ε - and handed back as they were made (:func:`respond`). The solver gives a ring the same bits
alone as in any batch, so a pattern's profiles are the same bits with the cache or without it (tested).

**Why its own stage, and why seeded.** It reads no seed of its own and draws nothing; it reads the
pattern's amplitudes, pitch and bar, which carry seeded draws, and the layer's phases, so ``graph`` labels
its two fields seeded through those requirements (D55: a stage that reads a seeded or a synthetic field
publishes seeded fields).
"""

from __future__ import annotations

import hashlib
import math
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages import gas_response as _response
from galaxy.stages.pattern import (
    PATTERN_READS,
    bar_radius,
    bar_terms,
    invert_azimuths,
    local_swing_x,
    ring_bracket,
    rotation_sense,
)
from galaxy.stages.pieces import forcing_factor

CELLS = _response.CELLS  # the solver's fixed cells round a ring; a profile is held on their centres

# What the gas's pattern is built from, and so what every stage that places by it requires. Since S60 (D219) the
# gas answers the stellar pattern's arm pieces, so it reads everything the stellar pattern reads - the census of
# pieces, their width, the ring's budget and the law's arm number, the pitch, the bar's body (whose depth cuts
# the pieces' amplitude: "the gas answers the stars that exist") and checkpoint 1's disc - and beside it the
# disc's epicyclic frequency and the scale length the stellar layer's height is a measured fraction of. Never
# ``arm_multiplicity``, and no longer a mode's amplitude or a phase.
GAS_PATTERN_READS: tuple[str, ...] = (*PATTERN_READS, "epicyclic_frequency", "disc_scale_length_spin")
# The lanes' four numbers (S58): the arcs' curvature, where they end, the gas inside the footprint over the gas
# outside it, and the lane's width - the last a declared placeholder (D217 item 8).
LANE_CONSTANTS: tuple[str, ...] = ("BAR_LANE_CURVATURE", "NUCLEAR_RING_RATIO", "BAR_GAS_RATIO", "BAR_LANE_WIDTH")
# ... the gas's sound speed and G, and since S60 the stellar layer's flattening (D219 item 5).
GAS_PATTERN_CONSTANTS: tuple[str, ...] = ("G", "GAS_DISPERSION", "ARM_LAYER_FLATTENING", *LANE_CONSTANTS)

SOLUTIONS_KEPT = 4  # how many patterns' solved rings the content-keyed cache holds (about 4.6 MB each)
TWO_PI = 2.0 * math.pi
# An image interval narrower than this (rad) is read at its middle: the mean of a profile over it is that value
# to the square of the width, and the difference of two integrals would be rounding.
NARROW_IMAGE = 1e-9
MANY_AZIMUTHS = 256  # past this many azimuths a row, the stretch each lies in is found by bisection (``_stretch``)

# The harmonics of a ring's profile on the solver's cells: every one the cells hold, 1 … CELLS/2 (the second
# follow-up to D219's gate, item 1: "a ring's profile of a piece is the Gaussian in d times the window in s on the
# solver's cells ... the forcing term by term as now").
HARMONICS = CELLS // 2
_HARMONIC = np.arange(HARMONICS + 1, dtype=float)  # 0 … CELLS/2: the arm numbers of a real transform's terms
# The carried map's check (D219 item 6, as the gate's first follow-up words it: "where the mid-gap misplaced weight
# passes 1 %, solve a ring at the mid-gap and carry from it, recursing at most twice (quartering)").
MISPLACED_LIMIT = 0.01
MID_GAP_DEPTH = 2
STORE_KEYS = ("radii", "profiles", "carries", "level", "running", "turn", "grid", "grid_profiles", "grid_carries", "diagnostics", "checked", "complete")
_SOLUTIONS: dict[bytes, tuple[np.ndarray, _response.Diagnostics]] = {}
_STORES: dict[bytes, dict] = {}  # the last few patterns' solved rings - the grid's and the mid-gap ones - by content
_FORCINGS: dict[bytes, np.ndarray] = {}  # the last few patterns' forcings on their rings, by what the pattern is made of
_SOLUTIONS_LOCK = threading.Lock()


def respond(forcing: np.ndarray, eps: np.ndarray, *, cache: bool = True) -> tuple[np.ndarray, _response.Diagnostics]:
    """The steady response of each ring given: ``(s, diagnostics)``, s shaped (rings, CELLS) on the cells' centres.

    ``forcing`` g on the cells' centres, shaped (rings, CELLS), dimensionless, of zero mean round each ring;
    ``eps`` ε, shaped (rings,), dimensionless. The flow through the pattern is 0 (D216 item 1). Raises what the
    solver raises - ``gas_response.ConvergenceError`` for a ring it could not converge - and catches nothing.
    (Until S60 the forcing was handed over as five modes' amplitudes and phases.)

    ``cache``: the last ``SOLUTIONS_KEPT`` solutions are kept under a digest of the two arguments' bytes and
    returned as they were made (read-only arrays); ``cache=False`` solves afresh and keeps nothing. The bits
    are the same either way.
    """
    f = np.ascontiguousarray(forcing, dtype=float)
    e = np.ascontiguousarray(eps, dtype=float)
    key = b""
    if cache:
        digest = hashlib.sha256()
        for part in (np.asarray(f.shape, dtype=np.int64), f, e):
            digest.update(part.tobytes())
        key = digest.digest()
        with _SOLUTIONS_LOCK:
            held = _SOLUTIONS.get(key)
        if held is not None:
            return held
    s, diagnostics = _response.solve(f, e, 0.0)
    s.setflags(write=False)
    for name in ("steps", "halvings", "deepest", "residual", "residual_sum", "floor"):
        getattr(diagnostics, name).setflags(write=False)
    if cache:
        with _SOLUTIONS_LOCK:
            _SOLUTIONS[key] = (s, diagnostics)
            while len(_SOLUTIONS) > SOLUTIONS_KEPT:  # the oldest out: a dict keeps the order things went in
                del _SOLUTIONS[next(iter(_SOLUTIONS))]
    return s, diagnostics


def forget_solutions() -> None:
    """Empty the content-keyed caches (the tests compare a pattern's bits with them and without)."""
    with _SOLUTIONS_LOCK:
        _SOLUTIONS.clear()
        _FORCINGS.clear()
        _STORES.clear()


def misplaced_weight(one: np.ndarray, other: np.ndarray) -> np.ndarray:
    """Half the mean absolute difference of two azimuthal profiles on one set of cells, each over its own mean, per
    ring: the share of the ring's weight the one puts where the other does not (S59's statistic; D219 item 6)."""
    a, b = one / one.mean(axis=1, keepdims=True), other / other.mean(axis=1, keepdims=True)
    return 0.5 * np.abs(a - b).mean(axis=1)


def blend_weights(taper: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(w_arm, w_bar) = (1 − taper, taper): the two weights of the composition (D216 item 8), their sum checked.

    The sum is 1 in the law; in doubles (1 − t) + t is 1 or one unit in the last place under it, and anything
    else - a taper that is not a number, or outside [0, 1] - is refused here and not composed.
    """
    w_bar = np.asarray(taper, dtype=float)
    w_arm = 1.0 - w_bar
    if not np.all((w_bar >= 0.0) & (w_bar <= 1.0) & (np.abs((w_arm + w_bar) - 1.0) <= np.finfo(float).eps)):
        raise ArithmeticError("the arm's and the bar's weights do not sum to 1: the bar's taper is not in [0, 1]")
    return w_arm, w_bar


# --------------------------------------------------------------------------------------------------------------
# The gas inside the bar's reach: the lanes (S58, BUILD_III Phase P3; DECISIONS.md D217 items 6-8)
# --------------------------------------------------------------------------------------------------------------


def ring_quadrature(values: np.ndarray) -> np.ndarray:
    """The mean of a law's samples on a ring's fixed cells, per ring: the exact mean of its interpolant. The
    lanes' template is normalised by it (:func:`lane_profiles`); no field is ever divided by one."""
    return values.sum(axis=-1) / values.shape[-1]


def lane_distance(x: np.ndarray, y: np.ndarray, half_length: float, curvature: float, ring: float, side: float) -> np.ndarray:
    """The distance, kpc, from points (x along the bar's axis, y across it) to one gas lane: the arc of a circle
    of radius a/(κa) from the bar's end on its major axis, (a, 0), to its minor axis at the nuclear ring,
    (0, side · r_ring), concave towards the major axis - the circle's centre lies on the major axis' side of
    the chord, so the arc bows out to the side ``side`` (±1) of the axis. Inside the arc's own angular span the
    distance is across the arc; beyond its ends it is to the nearer end. The other lane is this one's point
    reflection: its distance is this function at (−x, −y)."""
    a = float(half_length)
    radius = a / float(curvature)
    end, foot = (a, 0.0), (0.0, side * float(ring) * a)
    chord = math.hypot(foot[0] - end[0], foot[1] - end[1])
    if not radius >= 0.5 * chord:
        raise ValueError(f"a circle of radius {radius:g} kpc does not span the lane's ends, {chord:g} kpc apart")
    height = math.sqrt(radius * radius - 0.25 * chord * chord)
    # The chord's unit normal towards the major axis: the centre is the chord's midpoint moved along it.
    normal = (-float(ring) * a / chord, -side * a / chord)
    centre = (0.5 * (end[0] + foot[0]) + height * normal[0], 0.5 * (end[1] + foot[1]) + height * normal[1])
    half_span = math.asin(min(1.0, 0.5 * chord / radius))
    vx, vy = x - centre[0], y - centre[1]
    # The angle of each point, seen from the centre, off the arc's middle (the direction opposite the normal).
    off_middle = np.arctan2(-normal[0] * vy + normal[1] * vx, -normal[0] * vx - normal[1] * vy)
    across = np.abs(np.hypot(vx, vy) - radius)
    to_ends = np.minimum(np.hypot(x - end[0], y - end[1]), np.hypot(x - foot[0], y - foot[1]))
    return np.where(np.abs(off_middle) <= half_span, across, to_ends)


def lane_profiles(
    R: np.ndarray, half_length: float, axis_ratio: float, boxiness: float,
    curvature: float, ring: float, ratio: float, width: float, sense: float,
) -> np.ndarray:
    """L(R, ψ) on the fixed cells' centres of every grid ring, in the bar's frame ψ = φ − φ_bar; shaped (R, CELLS).

    The gas inside the bar's reach as D217 items 7-8 rule it, a synthetic template standing in for the
    two-dimensional flow in the bar's potential: on each ring inside the half-length a uniform base plus two
    lanes. **The base**: the mean inside the body's footprint (m ≤ 1, ``pattern.bar_radius``) is ``ratio``
    times the mean outside it on every ring, so with f the footprint's share of the ring the base is
    1/(1 + (ratio − 1) f) - 1/ratio where the footprint fills the ring. **The lanes** hold the excess over the
    base, inside the footprint: two point-symmetric arcs (:func:`lane_distance`) on the bar's leading side
    (``sense``: :func:`rotation_sense`), each with a Gaussian profile across the arc of full width at half
    maximum ``width`` · a. **Conserving by construction**: the Gaussian is weighed so that the ring's mean is
    1 - its amplitude on a ring is the ring's excess over ⟨w⟩, the quadrature of its own weight w on the
    ring's cells (:func:`ring_quadrature`), the one division here. ⟨w⟩ on the ring's cells is part of the
    template's definition (a shape defined to have mean 1 on the cells it is defined on), not a published
    field divided by its sampled mean after composition. The footprint's share of a ring is sampled on the
    same cells: 0.2083 at 0.9 a against 0.2090 on a thousand times as many (the Milky Way template's bar, as
    measured at S58; the gate's reviewer read 0.2092), the template's own resolution and no error of a
    published mean. L is positive (never under the base) and nothing is drawn, clipped or floored. 1 on a
    ring at or past the half-length, and on a ring whose footprint is narrower than a cell.
    """
    R = np.asarray(R, dtype=float)
    a = float(half_length)
    lanes = np.ones((R.size, CELLS))
    inside, x, y, footprint, share, base = _footprint(R, a, axis_ratio, boxiness, ratio)
    if not inside.any():
        return lanes
    sigma = float(width) * a / (2.0 * math.sqrt(2.0 * math.log(2.0)))  # the Gaussian's dispersion from its FWHM
    near = lane_distance(x, y, a, curvature, ring, sense)
    far = lane_distance(-x, -y, a, curvature, ring, sense)
    weight = np.where(footprint, np.exp(-0.5 * (near / sigma) ** 2) + np.exp(-0.5 * (far / sigma) ** 2), 0.0)
    total = ring_quadrature(weight)
    holds = share > 0.0
    if np.any(holds & ~(total > 0.0)):
        raise ArithmeticError("a ring inside the bar's footprint carries no lane weight: the lane's width has underflowed")
    amplitude = np.where(holds, (1.0 - base) / np.where(holds, total, 1.0), 0.0)
    lanes[inside] = base[:, None] + amplitude[:, None] * weight
    return lanes


def _footprint(R: np.ndarray, a: float, axis_ratio: float, boxiness: float, ratio: float):
    """What the lane field and the footprint-uniform field share, on the rings inside the half-length:
    ``(inside, x, y, footprint, share, base)`` - the rings R < a; their cells' centres in the bar's frame, kpc;
    the cells inside the body's footprint (m ≤ 1); the footprint's share of each ring, on the ring's own
    cells; and the base 1/(1 + (ratio − 1) share)."""
    inside = R < a
    psi = _response.cell_centres(CELLS)
    radius = R[inside, None]
    x, y = radius * np.cos(psi)[None, :], radius * np.sin(psi)[None, :]
    footprint = bar_radius(x, y, a, axis_ratio, boxiness) <= 1.0
    share = ring_quadrature(footprint.astype(float))
    base = 1.0 / (1.0 + (float(ratio) - 1.0) * share)
    return inside, x, y, footprint, share, base


def footprint_profiles(R: np.ndarray, half_length: float, axis_ratio: float, boxiness: float, ratio: float) -> np.ndarray:
    """L_fp(R, ψ) on the fixed cells' centres of every grid ring, in the bar's frame; shaped (R, CELLS): the
    lane field (:func:`lane_profiles`) with its excess spread evenly over the footprint instead of laid on the
    arcs. What the star formation law reads inside a bar's reach (D217's follow-up at the gate: "the lanes' one
    unsourced number (the width) must not drive a census").

    On each ring inside the half-length: the lanes' own base outside the body's footprint, and inside it the
    base plus the ring's excess over the footprint's share of the ring - base + (1 − base)/share. So the mean
    inside the footprint is ``ratio`` times the mean outside it, exactly as the lanes hold it, and the ring's
    mean is base + (1 − base) = 1; the share is the footprint's on the ring's own cells, part of the template's
    definition as the lanes' weight is. Positive; no ridge, no width, no curvature: of the lanes' four numbers
    it reads the ratio alone. Where the footprint fills the ring, and on a ring at or past the half-length or
    one whose footprint is narrower than a cell, it is 1.
    """
    R = np.asarray(R, dtype=float)
    a = float(half_length)
    uniform = np.ones((R.size, CELLS))
    inside, _, _, footprint, share, base = _footprint(R, a, axis_ratio, boxiness, ratio)
    if not inside.any():
        return uniform
    holds = share > 0.0
    level = np.where(holds, (1.0 - base) / np.where(holds, share, 1.0), 0.0)
    uniform[inside] = base[:, None] + np.where(footprint, level[:, None], 0.0)
    return uniform


GAS_DENSITY_CONTRAST = FieldDecl(
    name="gas_density_contrast", label="Gas density contrast Σ_gas(R, φ)/Σ_gas(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the gas's response to where the arms are - and 1 everywhere
    # with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Σ_gas(R, φ)/Σ_gas(R): mean 1 round every ring, so every radial gas profile is unchanged. Each "
        "value is the mean over its azimuthal cell on its ring - exact over the cell's extent in azimuth, at "
        "the ring's own radius: the gas the cell holds on its ring, not a sample at its "
        "centre - so a ring's cells average to 1 to rounding on any grid, with nothing divided; a census "
        "placing an object reads the same law at the object's own point. "
        "The steady response of isothermal gas to the stellar arm modes' potential, in the frame that turns "
        "with the gas - the frame the arms themselves turn in, so no gas flows through an arm and nothing "
        "shocks there. On each ring the logarithm of the gas's surface density is bent by the pressure of "
        "its own velocity dispersion against the pull of the arm modes, each mode pulling in proportion to "
        "its amplitude as the stars carry it - the saturation in it - and its arm number, and in inverse "
        "proportion to the disc's stability parameter and "
        "the sine of the pitch; the equation is solved on a fixed set of cells round the ring, and a point "
        "between two rings reads both at its own winding phase. Nothing sets the contrast or the width: they "
        "come out of the equation. The gas piles on the stellar crests: the offset is zero for a lone mode, "
        "exactly, by the equation's symmetry; with several modes the gas's crest and the crest of the stellar "
        "modes' sum are within about a degree of each other over the mid disc, to either side, because each "
        "mode is answered with its own weight - measured, not ruled; no offset is put in and none is "
        "published. "
        "Where the modes' pull together exceeds the pressure's reach the gas between the arms is nearly "
        "emptied, the crest standing two to three times the ring's mean in the mid disc and fading to "
        "nothing where the disc amplifies no arm. The crest is two and a half to three times as broad as "
        "the one measured gas arm, about half the period of the mode the gas answers most strongly: the "
        "steady, razor-thin response is an approximation and that is its recorded miss. A tightly wound "
        "galaxy - a drawn pitch of a few degrees - is forced far harder, and its inner rings swing from "
        "nearly empty to many times the mean: the law as it stands, nothing clipped, and a finding against "
        "the razor-thin forcing. Inside a bar's reach the response gives way, by the bar's taper, to the bar's "
        "gas lanes: on each ring inside the bar's half-length a uniform base and two narrow lanes on the "
        "bar's leading side - the side the bar turns into, which the trailing arms give - each an arc of "
        "constant curvature from the bar's end on its long axis to its short axis at the nuclear ring, bowed "
        "away from the long axis. The gas inside the stellar bar's footprint averages a measured multiple of "
        "the gas outside it on the same ring, and all of that excess lies on the lanes, so the lanes stand "
        "several times the ring's mean and the bar off its lanes is thinned to about four tenths of it; the "
        "ring's total is unchanged by construction. A template standing in for the gas flow in the bar's "
        "potential, which the model does not compute: its curvature, its inner end and its excess are "
        "measured typical values, the same for every bar, and its width is a declared placeholder that no "
        "source gave. Nothing of it is drawn. So the field is nowhere below the taper times the lanes' base "
        "and nowhere negative; nothing is clipped. An unbarred galaxy has no lanes and its gas answers the "
        "arms to the centre. It reads no gas column. A composed field: with the randomness layer "
        "off it is 1 everywhere - the equation and its inputs are unchanged, and nothing says where the "
        "arms are."
    ),
)


STAR_FORMATION_GAS_CONTRAST = FieldDecl(
    name="star_formation_gas_contrast", label="Gas density contrast the star formation law reads",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    # S58 (D217's follow-up at the gate): composed, as the gas's own contrast is, and 1 everywhere with the
    # randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "The gas's density contrast as the star formation law reads it: mean 1 round every ring, each value "
        "the exact mean over its azimuthal cell on its ring. Outside a bar's reach, and everywhere in an "
        "unbarred galaxy, it is the gas's own contrast - its steady response to the stellar arm modes - "
        "number for number. Inside a bar's reach the gas's own contrast gives way to the bar's two gas lanes, "
        "and the width of those lanes is a declared placeholder that no source gave; a census of stars must "
        "not be driven by a number nobody measured. So here the lanes' excess is spread evenly over the "
        "stellar bar's footprint instead: on each ring inside the bar's half-length the gas outside the "
        "footprint is thinned to the lanes' own base and the gas inside it is raised by one uniform step, so "
        "the gas inside the footprint still averages the same measured multiple of the gas outside it, the "
        "ring's total is unchanged, and there is no ridge. Star formation therefore follows the bar's "
        "footprint, not the lanes: the young stars of a barred galaxy fill the bar where it does not fill "
        "its ring, and where the footprint covers the whole ring this field is the response's blend alone. "
        "The dust and the cloud census keep the lanes. Positive wherever the gas's own contrast is; nothing "
        "is drawn, clipped or divided by a mean taken after the fact. A composed field: with the randomness "
        "layer off it is 1 everywhere."
    ),
)


@dataclass(frozen=True, slots=True, eq=False)
class GasPattern:
    """Everything the gas contrast needs, read from published fields in one place (rule A9).

    The interface is ``ArmPattern``'s (``flat``, ``contrast``, ``contrast_at``, ``sector_means``,
    ``azimuths``), so a stage that places by the stellar pattern can place by this one instead.

    **Evaluable at a point** (D216 item 9; D219 item 6): the response is solved once on each grid ring, in the
    galaxy's own azimuth; a point reads its two neighbouring rings' profiles, **each carried to the point's
    radius along the arm pieces' loci** (:meth:`carried`), and blends them linearly in R (held at the end rings
    beyond the grid). At a grid radius that is the ring's own profile, exactly. ``contrast``, ``contrast_at``,
    ``response_at`` and ``azimuths`` are that point function; ``sector_means`` and ``cell_means`` are its exact
    means over sectors of a ring, and ``cell_means`` on the grid's own φ cells is the field the stage publishes
    (gate G3 item 4).

    Built through ``galaxy.layer.compose`` (the one reader of the layer's switch) and by tests.
    """

    R: np.ndarray                # the grid radii, kpc: one solved ring each
    stars: Any                   # the stellar pattern (``pieces.ArmPattern``) the gas answers, or None: no pieces
    pitch_deg: float
    bar_length: float            # a, kpc: NaN for an unbarred galaxy (no bar, the taper 0 on every ring)
    epicyclic: np.ndarray        # (R,): κ, km/s/kpc
    surface_density: np.ndarray  # (R,): checkpoint 1's total disc Σ, M☉/pc²
    gravity: float               # G, kpc (km/s)²/M☉
    sound_speed: float           # a, km/s
    layer_height: float          # h_z, kpc: the stellar layer's exponential scale height (D219 item 5)
    # The lanes (S58, D217 items 7-8): the body's footprint and the template's four numbers. Asked of a barred
    # pattern only.
    axis_ratio: float = float("nan")      # q, the footprint's
    boxiness: float = float("nan")        # c
    lane_curvature: float = float("nan")  # κ·a
    ring_ratio: float = float("nan")      # r_ring / a
    gas_ratio: float = float("nan")       # the mean inside the footprint over the mean outside it
    lane_width: float = float("nan")      # the lane's FWHM / a: a declared placeholder
    design_count: np.ndarray | None = None  # (R,): the law's arm number - read by the disclosed check's mask alone
    flat: bool = field(init=False)
    barred: bool = field(init=False)
    _solved: dict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("R", "epicyclic", "surface_density"):
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        n = self.R.size
        if self.epicyclic.shape != (n,) or self.surface_density.shape != (n,):
            raise ValueError(
                f"a gas pattern holds the disc's epicyclic frequency and surface density on its {n} radii; got "
                f"{self.epicyclic.shape} and {self.surface_density.shape}"
            )
        if self.stars is not None and (self.stars.R.shape != (n,) or not np.array_equal(self.stars.R, self.R)):
            raise ValueError("a gas pattern and the stellar pattern it answers hold the same grid radii")
        # No perturbation to apply: a pattern the grid could not resolve (a NaN among its own numbers), or no arm
        # piece anywhere and no bar. (The disc's κ and Σ are not asked here: a ring that carries a piece on a
        # disc that is not a number is the solver's to refuse, loudly.)
        # **A half-length that is NaN is no bar** (S58, D217 item 3) - an unbarred galaxy, the taper 0 on every
        # ring - and not an unresolved pattern; a bar there is needs the lanes' numbers, all of them finite.
        barred = not math.isnan(self.bar_length)
        scalars: tuple[float, ...] = (self.pitch_deg, self.layer_height)
        if barred:
            scalars += (self.bar_length, self.axis_ratio, self.boxiness, self.lane_curvature, self.ring_ratio,
                        self.gas_ratio, self.lane_width)
        stars = self.stars
        finite = all(math.isfinite(v) for v in scalars) and (
            stars is None or bool(np.all(np.isfinite(stars.budget)) and np.all(np.isfinite(stars.width)))
        )
        no_arms = stars is None or not (stars.budget.any() and stars.pieces.most)
        object.__setattr__(self, "barred", barred and finite)
        object.__setattr__(self, "flat", not finite or (no_arms and not barred))
        object.__setattr__(self, "_solved", {})

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, Any], stars: Any = None) -> "GasPattern | None":
        """The gas pattern of a run's published fields on the run's grid radii ``R``, or None where the fields
        hold no pattern. ``stars`` is the stellar pattern of the same fields - ``compose`` builds it and hands it
        over; the gas answers its arm pieces. ``arm_multiplicity`` is not among what it reads (D215)."""
        if any(n not in fields for n in GAS_PATTERN_READS) or any(k not in constants for k in GAS_PATTERN_CONSTANTS):
            return None
        return cls(
            R, stars, float(fields["pitch_angle"]), float(fields["bar_half_length"]),
            fields["epicyclic_frequency"], fields["disc_surface_density"],
            float(constants["G"]), float(constants["GAS_DISPERSION"]),
            float(fields["disc_scale_length_spin"]) / float(constants["ARM_LAYER_FLATTENING"]),
            float(fields["bar_axis_ratio"]), float(fields["bar_boxiness"]),
            *(float(constants[k]) for k in LANE_CONSTANTS),
            np.asarray(fields["arm_design_count"], dtype=float),
        )

    # --- the law's inputs ------------------------------------------------------------------------------

    @property
    def sin_pitch(self) -> float:
        """sin p, of the disc's pitch (held inside 1-89 degrees, as ``pattern.bar_terms`` holds it): what ε reads
        (D219 item 5: "ε keeps the disc's pitch")."""
        return math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))

    def swing_x(self) -> np.ndarray:
        """X(R) = κ²R/(2πGΣ) on the grid rings: the arm-number law's own variable, by its own function."""
        return local_swing_x(self.R, self.epicyclic, self.surface_density, self.gravity)

    def epsilon(self) -> np.ndarray:
        """ε = a/(κ R sin p) on the grid rings, shaped (R,)."""
        return _response.epsilon(self.sound_speed, self.epicyclic, self.R, self.sin_pitch)

    def _disc_at(self, radii: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(κ, Σ) at radii: the grid's own on a grid radius, linear between two (for the instrument's direct
        solve off the grid, :meth:`solve_at`)."""
        return np.interp(radii, self.R, self.epicyclic), np.interp(radii, self.R, self.surface_density)

    def forcing_spectrum(self, radii: np.ndarray | None = None) -> np.ndarray:
        """The forcing's transform on the solver's cells, ring by ring: complex, shaped (rings, CELLS/2 + 1) -
        ``numpy.fft.rfft``'s terms of F on the cells' centres, term 0 (the mean) nothing (D219 item 5; the second
        follow-up's item 1).

        Composed piece by piece: each piece's ridge on the ring's cells - a Gaussian in the perpendicular distance
        to its locus times its window along it, at the stars' own amplitude on the ring, the cut in it and the
        bar's taper taken back out - is transformed, and its m-th term multiplied by m / (X (|sin p_j| + m h_z/R)),
        the piece's own pitch and the stellar layer's thickness (``pieces.forcing_factor``). The pieces' terms are
        added in the table's order. ``radii`` None: the grid rings."""
        on_grid = radii is None
        R = self.R if on_grid else np.asarray(radii, dtype=float)
        out = np.zeros((R.size, HARMONICS + 1), dtype=complex)
        stars = self.stars
        if stars is None or self.flat:
            return out
        kappa, sigma = (self.epicyclic, self.surface_density) if on_grid else self._disc_at(R)
        x = local_swing_x(R, kappa, sigma, self.gravity)
        taper, _, _ = bar_terms(R, self.pitch_deg, self.bar_length)
        with np.errstate(divide="ignore"):
            untapered = np.where(taper < 1.0, 1.0 / np.where(taper < 1.0, 1.0 - taper, 1.0), 0.0)
        for rows, sin_abs, ridges in stars.piece_profiles(R):
            spectrum = np.fft.rfft(ridges, axis=2)
            factor = forcing_factor(_HARMONIC[None, None, :], x[rows, None, None], sin_abs[:, :, None], (self.layer_height / R[rows])[:, None, None])
            total = np.zeros(spectrum.shape[::2], dtype=complex)
            for k in range(spectrum.shape[1]):
                total = total + spectrum[:, k, :] * factor[:, k, :]
            out[rows] = total * untapered[rows, None]
        return out

    def forcing(self, radii: np.ndarray | None = None) -> np.ndarray:
        """F on the solver's cells' centres of each ring, shaped (rings, CELLS): :meth:`forcing_spectrum` taken
        back to the cells. Its mean round a ring is 0."""
        return np.fft.irfft(self.forcing_spectrum(radii), n=CELLS, axis=1)

    def _digest(self) -> bytes:
        """A digest of everything the solved rings are made of - the census, the law's fields, the disc and the
        constants: what the content-keyed caches are held under."""
        stars = self.stars
        digest = hashlib.sha256()
        pieces = stars.pieces
        scalars = np.array([self.pitch_deg, self.bar_length, self.gravity, self.layer_height, self.sound_speed, stars.bar, stars.axis_ratio,
                            stars.boxiness, stars.index, stars.share, pieces.turn], dtype=float)
        for part in (self.R, self.epicyclic, self.surface_density, scalars, stars.budget, stars.design, stars.width,
                     pieces.chain, pieces.order, pieces.start_radius, pieces.start_azimuth, pieces.pitch_deg, pieces.extent,
                     pieces.pinned, pieces.join, np.zeros(0) if stars.surface_density is None else stars.surface_density):
            digest.update(np.asarray(part.shape, dtype=np.int64).tobytes())
            digest.update(np.ascontiguousarray(part, dtype=float).tobytes())
        return digest.digest()

    def _ring_forcing(self) -> np.ndarray:
        """:meth:`forcing` on the grid rings, kept by content: several stages of one run build the same pattern,
        and the last few patterns' forcings are held under a digest of everything the forcing is made of
        (:meth:`_digest`) and handed back as made (read-only). The bits are :meth:`forcing`'s."""
        stars = self.stars
        if stars is None or self.flat:
            return np.zeros((self.R.size, CELLS))
        key = self._digest()
        with _SOLUTIONS_LOCK:
            held = _FORCINGS.get(key)
        if held is None:
            held = self.forcing()
            held.setflags(write=False)
            with _SOLUTIONS_LOCK:
                _FORCINGS[key] = held
                while len(_FORCINGS) > SOLUTIONS_KEPT:
                    del _FORCINGS[next(iter(_FORCINGS))]
        return held

    def forcing_amplitudes(self) -> np.ndarray:
        """The cosine amplitude of each harmonic of the forcing on the grid rings, m = 1 … CELLS/2, shaped
        (R, HARMONICS): the analogue of the modes' f_m. Its sum along a ring is the most the forcing could reach
        were every harmonic's crest at one azimuth."""
        amplitude = 2.0 * np.abs(self.forcing_spectrum()[:, 1:]) / CELLS
        amplitude[:, -1] *= 0.5  # the last harmonic the cells hold is a cosine alone
        return amplitude

    # --- the solved rings ------------------------------------------------------------------------------

    # **The store** (D219 item 6 as the gate's first follow-up words it, built at the second's order). The response is
    # solved on every grid ring; a point between two rings reads the two rings' profiles carried to its radius
    # (below). Where that misplaces more than a hundredth of a ring's gas against the law solved at the gap's
    # middle, the ring solved there is kept and carried from - "where the mid-gap misplaced weight passes 1 %,
    # solve a ring at the mid-gap and carry from it, recursing at most twice (quartering), then record what
    # remains; the check is that solve". So the store holds the grid's rings and, in the gaps that need them, a
    # ring at the middle and rings at the quarters. A mid-gap ring's own inputs - X, ε, the budget, the count,
    # the widths - are read at its radius as the point functions give them (:meth:`solve_at`). A ring index in
    # the carrying methods below is the store's; the grid's own rings are ``store["grid"]``.

    def _rings(self) -> dict:
        """The store of solved rings, made the first time it is asked for: ``radii`` (M,) ascending - the grid's
        and the mid-gap rings'; ``profiles`` (M, CELLS); ``carries`` (M,), the rings a piece forces; ``level`` (M,),
        0 a grid ring, 1 one at a gap's middle, 2 one at a quarter; ``grid`` (R,), where each grid ring stands
        in it; ``diagnostics``, the solver's for the grid rings that carry a forcing (None where none does);
        ``checked``, per level the radii solved for the check and what each misplaced; ``complete``, whether the
        mid-gap rings have been looked for yet. **They are looked for the first time a radius off the grid's
        rings is read** (:meth:`_complete`): what is read on the grid's own rings - the published fields - is the
        same numbers with them or without, and a run that places no object does not pay for them."""
        solved = self._solved
        if "radii" in solved:
            return solved
        stars = self.stars
        key = None if stars is None or self.flat else self._digest()
        if key is not None:
            with _SOLUTIONS_LOCK:
                held = _STORES.get(key)
            if held is not None:
                solved.update(held)
                return solved
        g, eps = self._ring_forcing(), self.epsilon()
        carries = (g != 0.0).any(axis=1)
        profiles = np.ones((self.R.size, CELLS))  # a ring no piece forces: s = 1
        diagnostics = None
        if carries.any():
            s, diagnostics = respond(g[carries], eps[carries])
            profiles[carries] = s
        self._store(self.R, profiles, carries, np.zeros(self.R.size, dtype=np.int64))
        solved.update(diagnostics=diagnostics, checked=(), complete=key is None or self.R.size < 2)
        self._keep(key)
        return solved

    def _keep(self, key: bytes | None) -> None:
        """Hold the store under its digest, the last few patterns' (:data:`SOLUTIONS_KEPT`)."""
        if key is not None:
            with _SOLUTIONS_LOCK:
                _STORES.pop(key, None)
                _STORES[key] = {name: self._solved[name] for name in STORE_KEYS}
                while len(_STORES) > SOLUTIONS_KEPT:
                    del _STORES[next(iter(_STORES))]

    def _complete(self) -> dict:
        """The store with its mid-gap rings: looked for once, level by level (the comment above)."""
        solved = self._rings()
        if solved["complete"] is not False:  # done, or being done by this very call
            return solved
        solved["complete"] = None
        checked: list[tuple[np.ndarray, np.ndarray]] = []
        centres = _response.cell_centres(CELLS)
        lower, upper = self.R[:-1], self.R[1:]
        for depth in range(1, MID_GAP_DEPTH + 1):
            asked = np.sort(0.5 * (lower + upper))
            if not asked.size:
                break
            direct, forced = self._solve(asked)
            carried = self.response_at(asked[:, None], centres[None, :])
            miss = misplaced_weight(carried, direct)
            checked.append((asked, miss))
            keep = miss > MISPLACED_LIMIT
            if not keep.any():
                break
            # The gaps the kept rings open: each kept middle halves its gap, and each half is checked next.
            order = np.argsort(0.5 * (lower + upper), kind="stable")
            low, high, middle = lower[order][keep], upper[order][keep], asked[keep]
            store = self._solved
            radii = np.concatenate([store["radii"], middle])
            rank = np.argsort(radii, kind="stable")
            self._store(radii[rank], np.concatenate([store["profiles"], direct[keep]])[rank],
                        np.concatenate([store["carries"], forced[keep]])[rank],
                        np.concatenate([store["level"], np.full(middle.size, depth, dtype=np.int64)])[rank])
            lower, upper = np.concatenate([low, middle]), np.concatenate([middle, high])
        solved.update(checked=tuple(checked), complete=True)
        self._keep(self._digest())
        return solved

    def _store(self, radii: np.ndarray, profiles: np.ndarray, carries: np.ndarray, level: np.ndarray) -> None:
        """Set the store to these rings (ascending radii), with what a mean over an interval of a ring is read
        from: the integral of each ring's interpolant from its first cell's centre to each centre, in cells, and
        over the whole turn."""
        segments = 0.5 * (profiles + np.roll(profiles, -1, axis=1))
        running = np.cumsum(segments, axis=1) - segments
        turn = running[:, -1] + segments[:, -1]
        grid = np.flatnonzero(level == 0)
        own = profiles[grid]
        for array in (radii, profiles, carries, level, running, turn, grid, own):
            array.setflags(write=False)
        self._solved.update(radii=radii, profiles=profiles, carries=carries, level=level, running=running, turn=turn, grid=grid,
                            grid_profiles=own, grid_carries=carries[grid])

    def _solve(self, radii: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(the response solved directly at ``radii``, shaped (radii, CELLS); which of them a piece forces): the law
        at those radii, with the disc's κ and Σ read linearly between the grid rings and everything of the arms
        the radius' own. Kept by content as the grid's rings are (:func:`respond`)."""
        g = self.forcing(radii)
        kappa, _ = self._disc_at(radii)
        eps = _response.epsilon(self.sound_speed, kappa, radii, self.sin_pitch)
        out = np.ones((radii.size, CELLS))
        on = (g != 0.0).any(axis=1)
        if on.any():
            out[on] = respond(g[on], eps[on])[0]
        return out, on

    @property
    def profiles(self) -> np.ndarray:
        """s on the cells' centres of every grid ring, in the galaxy's azimuth (a cell's centre is φ = −π +
        (k + ½) 2π/CELLS), shaped (R, CELLS); read-only. 1 on a ring no piece forces."""
        return self._rings()["grid_profiles"]

    @property
    def carries(self) -> np.ndarray:
        """(R,) bool: the grid rings a piece forces - the ones the solver solved."""
        return self._rings()["grid_carries"]

    @property
    def diagnostics(self) -> "_response.Diagnostics | None":
        """What Newton did on the grid rings that carry a forcing, in their order (None where no ring does)."""
        return self._rings()["diagnostics"]

    @property
    def mid_gap(self) -> tuple[np.ndarray, np.ndarray]:
        """(the radii of the rings kept between the grid's, their levels - 1 a gap's middle, 2 a quarter)."""
        store = self._complete()
        extra = store["level"] > 0
        return store["radii"][extra], store["level"][extra]

    def solve_at(self, radii: np.ndarray) -> np.ndarray:
        """The response solved directly at ``radii`` (kpc, any), shaped (radii, CELLS): the law at those radii,
        with the disc's κ and Σ read linearly between the grid rings. **The instrument's**: what the carried
        profiles are measured against between two rings (D219 item 6). No reader of the model calls it."""
        return self._solve(np.asarray(radii, dtype=float))[0]

    # --- a ring's profile, carried to another radius (S60, D219 item 6) --------------------------------
    #
    # The arms of S57-S59 shared one winding, so a ring's profile was read at another radius by turning it: one
    # shift. Arm pieces have each their own pitch, so between two rings they move by different angles. The
    # ruling: "a ring's solved profile is carried to a point along the pieces' loci (a periodic piecewise-linear
    # map of azimuth anchored where each crossing piece stands on the ring and at the point's radius)".
    #
    # For grid ring k and a radius r: every piece that crosses the ring stands at φ_j(R_k) on it and - on its own
    # chain's polyline followed from it, the end piece's line continued where the chain ends (``Pieces.along``) -
    # at φ_j(r). Its displacement is d_j = φ_j(R_k) − φ_j(r).
    # The map is M(φ) = φ + D(φ), D periodic and linear between neighbouring anchors φ_j(r) round the circle,
    # D(φ_j(r)) = d_j: each arm is read where it is on the ring, and the gas between two arms in proportion.
    # One crossing piece: a turn by its own d, the old shift. None: nothing to carry (s = 1). At r = R_k: the
    # identity.
    #
    # **The carried profile is s_k(M(φ)) over its own mean round the ring at r.** A map that stretches one
    # stretch between arms and squeezes the next does not keep the profile's mean, and every reader needs each
    # ring's term to be a redistribution at every radius (a census's expected count in a cell ring is the ring's
    # count times a mean of this function: I2). The mean is the exact integral of the carried interpolant - on
    # each stretch between two anchors M is linear, so the integral there is the stretch's width times the
    # interpolant's own mean between the two images - not a sampled one, and at the ring's own radius nothing is
    # divided. The ruling does not say how the mean is kept: this is the builder's choice, declared.

    def _integral(self, ring: np.ndarray, psi: np.ndarray) -> np.ndarray:
        """∫ of ring ``ring``'s interpolant from its first cell's centre to ``psi``, in cells: exact (the
        interpolant is linear between centres). ``ring`` broadcasts against ``psi``."""
        solved = self._rings()
        profiles, running, turn = solved["profiles"], solved["running"], solved["turn"]
        ring, psi = np.broadcast_arrays(np.asarray(ring, dtype=np.int64), np.asarray(psi, dtype=float))
        below, above, weight, wraps = _response.bracket(psi, CELLS)
        first = profiles[ring, below]
        return wraps * turn[ring] + running[ring, below] + weight * (first + 0.5 * weight * (profiles[ring, above] - first))

    def _image_mean(self, ring: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
        """The mean of ring ``ring``'s interpolant between the azimuths ``lo`` and ``hi`` (either order): the
        difference of two integrals over the interval's width, or - for an interval under :data:`NARROW_IMAGE` -
        the interpolant at its middle."""
        width = hi - lo
        wide = np.abs(width) > NARROW_IMAGE
        mean = (self._integral(ring, hi) - self._integral(ring, lo)) / np.where(wide, width * (CELLS / TWO_PI), 1.0)
        return np.where(wide, mean, self._ring_read(self._rings()["profiles"], ring, 0.5 * (lo + hi)))

    def _anchors(self, ring: np.ndarray, r: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """The map of each (grid ring, radius) pair: ``(anchors, shifts, first, sorted, count)``.

        ``sorted`` (n, K): the anchors φ_j(r) of the pieces crossing the ring, in [0, 2π) and ascending, +inf in
        the slots that hold none; ``count`` (n,) how many there are; ``first`` (n,) the first anchor (0 where
        there is none); ``anchors`` and ``shifts`` (n, K + 1): the anchors with the first one a turn on after the
        last (and in every slot past it), and each one's displacement d_j - the knots D is linear between."""
        pieces = self.stars.pieces
        radius = self._rings()["radii"][ring]
        slots = pieces.slots(radius)
        live, on_ring, _ = pieces.geometry(radius, slots)
        at_point = pieces.along(slots, np.log(np.asarray(r, dtype=float))[:, None])  # the chain followed along its polyline (the fourth pass)
        key = np.where(live, np.mod(at_point, TWO_PI), np.inf)
        order = np.argsort(key, axis=1, kind="stable")
        ordered = np.take_along_axis(key, order, axis=1)
        shift = np.take_along_axis(np.where(live, on_ring - at_point, 0.0), order, axis=1)
        count = live.sum(axis=1)
        held = np.isfinite(ordered)
        first = np.where(count > 0, np.where(held[:, 0], ordered[:, 0], 0.0), 0.0)
        first_shift = np.where(count > 0, shift[:, 0], 0.0)
        wrap = first + TWO_PI
        anchors = np.concatenate([np.where(held, ordered, wrap[:, None]), wrap[:, None]], axis=1)
        shifts = np.concatenate([np.where(held, shift, first_shift[:, None]), first_shift[:, None]], axis=1)
        return anchors, shifts, first, ordered, count

    @staticmethod
    def _stretch(q: np.ndarray, ordered: np.ndarray) -> np.ndarray:
        """Which stretch between anchors each azimuth of ``q`` (n, k) lies in: the index of the last anchor at or
        under it in its row of ``ordered`` (n, K), 0 where the row holds none. Counted directly for a few
        azimuths a row, and found by bisection row by row for many: the same indices either way."""
        if q.shape[1] <= MANY_AZIMUTHS:
            return np.maximum((ordered[:, None, :] <= q[:, :, None]).sum(axis=2) - 1, 0)
        at = np.empty(q.shape, dtype=np.int64)
        for i in range(q.shape[0]):
            at[i] = np.searchsorted(ordered[i], q[i], side="right")
        return np.maximum(at - 1, 0)

    @staticmethod
    def _displacement(phi: np.ndarray, anchors: np.ndarray, shifts: np.ndarray, first: np.ndarray, ordered: np.ndarray) -> np.ndarray:
        """D at each azimuth of ``phi`` (n, k): linear between the two anchors the azimuth lies between."""
        q = first[:, None] + np.mod(phi - first[:, None], TWO_PI)
        at = GasPattern._stretch(q, ordered)
        lo, hi = np.take_along_axis(anchors, at, axis=1), np.take_along_axis(anchors, at + 1, axis=1)
        d_lo, d_hi = np.take_along_axis(shifts, at, axis=1), np.take_along_axis(shifts, at + 1, axis=1)
        span = hi - lo
        share = np.where(span > 0.0, (q - lo) / np.where(span > 0.0, span, 1.0), 0.0)
        return d_lo + share * (d_hi - d_lo)

    def _carried_mean(self, ring: np.ndarray, anchors: np.ndarray, shifts: np.ndarray, count: np.ndarray) -> np.ndarray:
        """The mean round the ring of s_k(M(φ)), per (ring, radius) pair: Σ over the stretches between anchors of
        the stretch's width times the interpolant's mean between its two images, over 2π. 1 where nothing moves
        (the ring's own radius, or no anchor): the profile is then not divided at all."""
        width = anchors[:, 1:] - anchors[:, :-1]
        image = anchors + shifts
        total = (width * self._image_mean(ring[:, None], image[:, :-1], image[:, 1:])).sum(axis=1) / TWO_PI
        moved = (count > 0) & (shifts != 0.0).any(axis=1)
        return np.where(moved, total, 1.0)

    def carried(self, ring: np.ndarray, r: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Grid ring ``ring``'s solved profile as a point at radius ``r`` sees it, at that row's azimuths ``phi``:
        s_ring(M(φ)) over its mean round the ring at r (the comment above). ``ring`` and ``r`` are (n,) and
        ``phi`` (n, k); returns (n, k). At ``r`` = the ring's own radius it is the ring's interpolant at φ, to
        the bit; a ring no piece forces is 1."""
        ring = np.asarray(ring, dtype=np.int64)
        r = np.asarray(r, dtype=float)
        phi = np.asarray(phi, dtype=float)
        out = np.ones(np.broadcast_shapes(phi.shape, (ring.size, 1)))
        store = self._rings()
        on = store["carries"][ring]
        if on.any():
            k, radius, angle = ring[on], r[on], np.broadcast_to(phi, out.shape)[on]
            anchors, shifts, first, ordered, count = self._anchors(k, radius)
            image = angle + self._displacement(angle, anchors, shifts, first, ordered)
            out[on] = self._ring_read(store["profiles"], k[:, None], image) / self._carried_mean(k, anchors, shifts, count)[:, None]
        return out

    def carried_cell_means(self, ring: np.ndarray, r: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The mean of :meth:`carried` over each azimuthal cell between ``edges`` (ascending, spanning a turn at
        most), per (ring, radius) pair, shaped (n, cells): exact - between two neighbouring breaks (an edge or
        an anchor) the map is linear, and the integral there is the stretch's width times the interpolant's own
        mean between the two images. At the ring's own radius it is the ring's interpolant integrated over each
        cell (``gas_response.sector_mean``), with nothing divided."""
        ring = np.asarray(ring, dtype=np.int64)
        r = np.asarray(r, dtype=float)
        edges = np.asarray(edges, dtype=float)
        lo, hi = edges[:-1], edges[1:]
        if edges[-1] - edges[0] > TWO_PI * (1.0 + 1e-12):
            raise ValueError("the cells a ring's carried profile is averaged over span a turn at most")
        out = np.ones((ring.size, lo.size))
        store = self._rings()
        on = store["carries"][ring]
        own = on & (r == store["radii"][ring])
        if own.any():
            out[own] = _response.sector_mean(store["profiles"][ring[own]], np.broadcast_to(lo, (int(own.sum()), lo.size)), np.broadcast_to(hi, (int(own.sum()), lo.size)))
        moved = on & ~own
        if moved.any():
            k, radius = ring[moved], r[moved]
            anchors, shifts, first, ordered, count = self._anchors(k, radius)
            n, slots = ordered.shape
            # The breaks: the cells' edges and every anchor inside their span, in order.
            held = np.isfinite(ordered)
            inside = edges[0] + np.mod(np.where(held, ordered, 0.0) - edges[0], TWO_PI)
            inside = np.where(held, np.minimum(inside, edges[-1]), edges[-1])
            breaks = np.concatenate([np.broadcast_to(edges[None, :], (n, edges.size)), inside], axis=1)
            order = np.argsort(breaks, axis=1, kind="stable")  # an edge before an anchor that falls on it
            breaks = np.take_along_axis(breaks, order, axis=1)
            place = np.empty_like(order)
            np.put_along_axis(place, order, np.broadcast_to(np.arange(order.shape[1])[None, :], order.shape), axis=1)
            # The map is read at each end of a stretch from inside the stretch: at its middle, by the stretch's
            # own slope - an anchor is a kink of the map, and its two sides differ.
            middle = 0.5 * (breaks[:, 1:] + breaks[:, :-1])
            half = 0.5 * (breaks[:, 1:] - breaks[:, :-1])
            centre = middle + self._displacement(middle, anchors, shifts, first, ordered)
            q = first[:, None] + np.mod(middle - first[:, None], TWO_PI)
            at = self._stretch(q, ordered)
            a_lo, a_hi = np.take_along_axis(anchors, at, axis=1), np.take_along_axis(anchors, at + 1, axis=1)
            d_lo, d_hi = np.take_along_axis(shifts, at, axis=1), np.take_along_axis(shifts, at + 1, axis=1)
            span = a_hi - a_lo
            slope = 1.0 + np.where(span > 0.0, (d_hi - d_lo) / np.where(span > 0.0, span, 1.0), 0.0)
            pieces = 2.0 * half * self._image_mean(k[:, None], centre - slope * half, centre + slope * half)
            running = np.concatenate([np.zeros((n, 1)), np.cumsum(pieces, axis=1)], axis=1)
            at_edges = place[:, : edges.size]
            integral = np.take_along_axis(running, at_edges[:, 1:], axis=1) - np.take_along_axis(running, at_edges[:, :-1], axis=1)
            out[moved] = integral / (hi - lo)[None, :] / self._carried_mean(k, anchors, shifts, count)[:, None]
        return out

    # --- at a point ------------------------------------------------------------------------------------

    def _between(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(lower ring, upper ring, share of the upper) for each radius, **in the store**: linear in R between the
        two solved rings a radius lies between - the grid's, or a mid-gap one where the gap holds one - the end
        ring alone beyond the grid (item 9). At a solved ring's radius the share is 0 or 1 and the ring is its
        own. A radius that is not one of the grid's own has the mid-gap rings looked for first."""
        R = np.asarray(R, dtype=float)
        store = self._rings()
        if store["complete"] is False and not np.isin(R, self.R).all():
            store = self._complete()
        return ring_bracket(store["radii"], R)

    def _read(self, profiles: np.ndarray, R: np.ndarray, angle: np.ndarray) -> np.ndarray:
        """Profiles held on the cells of every grid ring, read at points: ``R`` in kpc and ``angle`` in radians
        of the profiles' own coordinate, broadcast against each other. Each point reads its two neighbouring
        grid rings at its own angle - ``gas_response.interpolate``'s own arithmetic on the two cells it lies
        between, the ring picked point by point - and blends them linearly in R. The bar's lanes and its
        footprint are read so, in the bar's frame; the response is not (it is carried: :meth:`response_at`)."""
        R, angle = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(angle, dtype=float))
        lower, upper, share = ring_bracket(self.R, R)  # the bar's templates are the grid rings'
        below, above, weight, _ = _response.bracket(angle, CELLS)

        def read(ring: np.ndarray) -> np.ndarray:
            first, second = profiles[ring, below], profiles[ring, above]
            rising = second >= first
            return np.where(rising, first, second) + np.where(rising, weight, 1.0 - weight) * np.abs(second - first)

        return (1.0 - share) * read(lower) + share * read(upper)

    def _rows(self, R: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[int, ...]]:
        """``R`` and ``phi``, broadcast against each other, as rows: (radii (n,), azimuths (n, k), the broadcast
        shape). A column of radii against rows of azimuths keeps one row a radius, so a radius' map is made
        once; anything else is one row a point."""
        R, phi = np.asarray(R, dtype=float), np.asarray(phi, dtype=float)
        shape = np.broadcast_shapes(R.shape, phi.shape)
        rank = len(shape)
        aligned = R.reshape((1,) * (rank - R.ndim) + R.shape)
        if rank >= 1 and aligned.shape[-1] == 1 and shape[-1] > 1:
            radii = np.broadcast_to(aligned, shape[:-1] + (1,)).reshape(-1)
            return radii, np.broadcast_to(phi, shape).reshape(radii.size, shape[-1]), shape
        return np.broadcast_to(R, shape).reshape(-1), np.broadcast_to(phi, shape).reshape(-1, 1), shape

    def response_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """s at points: ``R`` in kpc and ``phi`` in radians broadcast against each other. Each point reads its
        two neighbouring grid rings, each carried to the point's radius along the pieces' loci
        (:meth:`carried`), and blends them linearly in R. (Until S60 the second argument was the pattern
        coordinate χ of a common winding; there is none now, and a profile is held in the galaxy's azimuth.)"""
        radii, azimuths, shape = self._rows(R, phi)
        lower, upper, share = self._between(radii)
        out = np.empty(azimuths.shape)
        whole = share == 0.0
        if whole.any():
            out[whole] = self.carried(lower[whole], radii[whole], azimuths[whole])
        top = share == 1.0
        if top.any():
            out[top] = self.carried(upper[top], radii[top], azimuths[top])
        mixed = ~(whole | top)
        if mixed.any():
            a = share[mixed][:, None]
            out[mixed] = ((1.0 - a) * self.carried(lower[mixed], radii[mixed], azimuths[mixed])
                          + a * self.carried(upper[mixed], radii[mixed], azimuths[mixed]))
        return out.reshape(shape)

    def response_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The mean of :meth:`response_at` over each azimuthal cell between ``edges`` at each radius of ``R``,
        shaped (R, cells): the two neighbouring rings' carried profiles, each integrated exactly
        (:meth:`carried_cell_means`), blended as a point blends them."""
        R = np.asarray(R, dtype=float)
        lower, upper, share = self._between(R)
        out = np.empty((R.size, np.size(edges) - 1))
        whole, top = share == 0.0, share == 1.0
        if whole.any():
            out[whole] = self.carried_cell_means(lower[whole], R[whole], edges)
        if top.any():
            out[top] = self.carried_cell_means(upper[top], R[top], edges)
        mixed = ~(whole | top)
        if mixed.any():
            a = share[mixed][:, None]
            out[mixed] = ((1.0 - a) * self.carried_cell_means(lower[mixed], R[mixed], edges)
                          + a * self.carried_cell_means(upper[mixed], R[mixed], edges))
        return out

    # --- the lanes (S58, D217 items 6-8) ---------------------------------------------------------------

    @property
    def sense(self) -> float:
        """The disc's sense of rotation in φ, from the winding (:func:`rotation_sense`): the lanes' side."""
        return rotation_sense(self.pitch_deg)

    @property
    def lanes(self) -> np.ndarray:
        """L on the cells' centres of every grid ring in the bar's frame ψ = φ − φ_bar, shaped (R, CELLS);
        read-only. Made the first time it is asked for. A barred pattern's only: an unbarred one has none."""
        solved = self._solved
        if "lanes" not in solved:
            if not self.barred:
                raise ValueError("an unbarred pattern has no lanes")
            lanes = lane_profiles(self.R, self.bar_length, self.axis_ratio, self.boxiness, self.lane_curvature,
                                  self.ring_ratio, self.gas_ratio, self.lane_width, self.sense)
            lanes.setflags(write=False)
            solved["lanes"] = lanes
        return solved["lanes"]

    def lanes_at(self, R: np.ndarray, psi: np.ndarray) -> np.ndarray:
        """L at points, ``R`` in kpc and ``psi`` = φ − φ_bar in radians, broadcast against each other: the two
        neighbouring grid rings' lane profiles read at the point's own ψ and blended linearly in R - a convex
        blend of positive profiles of mean 1, so L is positive and its mean round a ring is 1 at every radius."""
        return self._read(self.lanes, R, psi)

    @property
    def footprint(self) -> np.ndarray:
        """L_fp on the cells' centres of every grid ring in the bar's frame, shaped (R, CELLS); read-only: the
        lanes' excess spread evenly over the body's footprint (:func:`footprint_profiles`) - what the star
        formation law reads in the lanes' place. A barred pattern's only."""
        solved = self._solved
        if "footprint" not in solved:
            if not self.barred:
                raise ValueError("an unbarred pattern has no bar's footprint")
            uniform = footprint_profiles(self.R, self.bar_length, self.axis_ratio, self.boxiness, self.gas_ratio)
            uniform.setflags(write=False)
            solved["footprint"] = uniform
        return solved["footprint"]

    def footprint_at(self, R: np.ndarray, psi: np.ndarray) -> np.ndarray:
        """L_fp at points, read as :meth:`lanes_at` reads L: positive, of mean 1 round a ring at every radius."""
        return self._read(self.footprint, R, psi)

    def _contrast_at(self, R: np.ndarray, phi: np.ndarray, bar: "Callable[[], np.ndarray]") -> np.ndarray:
        """w_arm s + w_bar (the bar's profiles) at points; ``bar`` gives the profiles, asked of a barred pattern only."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        taper, _, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        w_arm, w_bar = blend_weights(taper)
        arms = w_arm * self.response_at(R, phi)
        return arms + w_bar * self._read(bar(), R, phi - bar_angle) if self.barred else arms

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise.
        g = w_arm s + w_bar L, the taper at the point's own radius; an unbarred pattern is s (w_arm = 1)."""
        return self._contrast_at(R, phi, lambda: self.lanes)

    def star_formation_contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast the star formation law reads, at points: g_sf = w_arm s + w_bar L_fp - :meth:`contrast_at`
        with the footprint-uniform field in the lanes' place. An unbarred pattern's is :meth:`contrast_at`'s."""
        return self._contrast_at(R, phi, lambda: self.footprint)

    # --- what the young stars' reader asks (S59, D218; S60, the second follow-up to D219's gate, item 3) ---------
    #
    # "The young stars' reader applies each bracketing grid ring's law to the gas pattern's point function at the
    # point ... the point function using the mid-gap rings of item 6; nothing ring-only is interpolated." So the
    # reader asks this pattern for one thing, :meth:`star_formation_contrast_at`, and beside it only where that
    # function's kinks lie (for its quadrature) and where it is one number round the ring (so that a mean is not
    # sampled). The ring-by-ring contrasts S59 and the first two passes of S60 served are gone with their reader.

    def _ring_read(self, profiles: np.ndarray, ring: np.ndarray, angle: np.ndarray) -> np.ndarray:
        """``profiles[ring]`` read at ``angle`` (radians of the profiles' own coordinate), the two broadcast
        against each other: ``gas_response.interpolate``'s own arithmetic on the two cells an angle lies between,
        the ring picked point by point - :meth:`_read`'s read of one ring, with no blend in R."""
        ring, angle = np.broadcast_arrays(np.asarray(ring, dtype=np.int64), np.asarray(angle, dtype=float))
        below, above, weight, _ = _response.bracket(angle, CELLS)
        first, second = profiles[ring, below], profiles[ring, above]
        rising = second >= first
        return np.where(rising, first, second) + np.where(rising, weight, 1.0 - weight) * np.abs(second - first)

    def footprint_uniform_at(self, R: np.ndarray) -> np.ndarray:
        """(radii,) bool: the radii at which the bar's footprint adds one number round the ring to the
        star-formation contrast - no bar, or both grid rings the radius reads hold a footprint row that is one
        number on every cell (every ring at or past the half-length, and those the footprint fills)."""
        R = np.asarray(R, dtype=float)
        if not self.barred:
            return np.ones(R.shape, dtype=bool)
        rows = self.footprint
        even = rows.min(axis=1) == rows.max(axis=1)
        lower, upper, _ = ring_bracket(self.R, R)
        return even[lower] & even[upper]

    def uniform_at(self, R: np.ndarray) -> np.ndarray:
        """(radii,) bool: the radii at which the star-formation contrast is one number round the ring - neither
        solved ring the radius reads is forced by a piece (the response is 1 there), and the footprint is uniform
        (:meth:`footprint_uniform_at`)."""
        R = np.asarray(R, dtype=float)
        lower, upper, _ = self._between(R)
        carries = self._rings()["carries"]
        return ~carries[lower] & ~carries[upper] & self.footprint_uniform_at(R)

    def star_formation_kinks(self, R: np.ndarray, bar: bool) -> np.ndarray:
        """Azimuths a quadrature of a function of a grid ring's star-formation contrast, read by a point at radius
        ``R`` (:meth:`ring_star_formation_contrast_at`), is cut at, one row a radius: the profile's cells'
        centres; the anchors of the two solved rings the radius reads, where the map that carries a ring's profile
        changes slope; and, with ``bar``, the footprint's cells' centres in the bar's frame, φ_bar + ψ_c.

        At a grid radius these are the contrast's kinks exactly, as they were under the common winding. Between
        two rings the carried arm profile's own kinks stand where the map sends the cells' centres - by up to
        the pieces' differing turns from where this method puts them - so a piece between two breaks holds at
        most a kink or two of a profile that bends little there: what that leaves is measured in the tests.
        One turn's worth each, not wrapped into any range. ``bar`` is the caller's to drop where no ring it
        reads holds a footprint that is not uniform; an unbarred pattern has none."""
        R = np.asarray(R, dtype=float)
        centres = _response.cell_centres(CELLS)
        parts = [np.broadcast_to(centres[None, :], (R.size, CELLS))]
        if self.stars is not None and self.stars.pieces.most:
            lower, upper, _ = self._between(R)
            for ring in (lower, upper):
                anchors, _, first, _, _ = self._anchors(ring, R)
                parts.append(np.where(np.isfinite(anchors), anchors, first[:, None])[:, :-1])
        if bar and self.barred:
            bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)[2]
            parts.append(np.broadcast_to(bar_angle + centres[None, :], (R.size, CELLS)))
        return np.concatenate(parts, axis=1)

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ_gas(R, φ)/Σ_gas(R) at the points of an (R, φ) mesh: the point function at each (R_i, φ_j) - what a
        census inverts for an azimuth. Its mean round a ring is 1 over the ring itself; a mesh's samples
        average to 1 only to their sampling, and nothing is divided. (The field the stage publishes is not
        this: it is :meth:`cell_means`.)"""
        return self.contrast_at(np.asarray(R, dtype=float)[:, None], np.asarray(phi, dtype=float)[None, :])

    def cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The contrast's mean over each azimuthal cell between ``edges`` (radians, ascending) at each radius of
        ``R``, shaped (R, cells): what the stage publishes on the grid (gate G3 item 4). The exact mean of the
        point function over the cell - the two neighbouring rings' carried profiles integrated exactly and
        blended as a point blends them, the lanes' interpolants piece by piece in the bar's frame - so cells
        that tile the ring average to 1 to rounding on any grid, and a cell's value is never under
        w_bar min L. At one radius it is :meth:`sector_means`' arithmetic."""
        return self._cell_means(R, edges, (lambda: self.lanes,))[0]

    def star_formation_cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """:meth:`cell_means` of the contrast the star formation law reads (:meth:`star_formation_contrast_at`):
        the footprint-uniform field's interpolant integrated in the lanes' place. An unbarred pattern's, and
        every ring's at or past the half-length, is :meth:`cell_means`' to the bit."""
        return self._cell_means(R, edges, (lambda: self.footprint,))[0]

    def published_cell_means(self, R: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(:meth:`cell_means`, :meth:`star_formation_cell_means`): the stage's two fields, the response's part
        integrated once and shared - each the same bits as its own method gives."""
        laned, uniform = self._cell_means(R, edges, (lambda: self.lanes, lambda: self.footprint))
        return laned, uniform

    def _cell_means(self, R: np.ndarray, edges: np.ndarray, bars: "tuple[Callable[[], np.ndarray], ...]") -> tuple[np.ndarray, ...]:
        """The exact cell means of w_arm s + w_bar (a bar's profiles), one array per entry of ``bars`` (each
        gives its profiles; asked of a barred pattern only). An unbarred pattern's are the response's alone."""
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        lo, hi = edges[:-1], edges[1:]
        taper, _, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        w_arm, w_bar = blend_weights(taper)
        lower, upper, share = ring_bracket(self.R, R)  # the bar's templates are the grid rings'
        arms = w_arm[:, None] * self.response_cell_means(R, edges)
        if not self.barred:
            return tuple(arms if k == 0 else arms.copy() for k in range(len(bars)))  # the same bits, not one array
        low = np.broadcast_to(lo[None, :] - bar_angle, (R.size, lo.size))
        high = np.broadcast_to(hi[None, :] - bar_angle, (R.size, lo.size))

        def blended(profiles: np.ndarray) -> np.ndarray:
            bar = ((1.0 - share)[:, None] * _response.sector_mean(profiles[lower], low, high)
                   + share[:, None] * _response.sector_mean(profiles[upper], low, high))
            return arms + w_bar[:, None] * bar

        return tuple(blended(bar()) for bar in bars)

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` (radians, ascending) at one radius: the exact
        mean of the point function (:meth:`cell_means`' arithmetic at one radius). Sectors that tile the ring
        average to 1 to rounding."""
        return self._cell_means(np.array([float(R)]), edges, (lambda: self.lanes,))[0][0]

    def star_formation_sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """:meth:`sector_means` of the contrast the star formation law reads: the footprint-uniform field in
        the lanes' place. An unbarred pattern's is :meth:`sector_means`'."""
        return self._cell_means(np.array([float(R)]), edges, (lambda: self.footprint,))[0][0]

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))

    # --- the disclosed check's measurements (D216 item 11 iv): they build nothing --------------------

    def stellar_sum(self) -> np.ndarray:
        """The stellar arm pieces' sum on the cells' centres of every grid ring, shaped (R, CELLS): the stars'
        own arm field there (``ArmPattern.ring_profile``), whose highest part of a ring the source's mask is
        laid on. 0 where there are no pieces."""
        if self.stars is None or self.flat:
            return np.zeros((self.R.size, CELLS))
        return self.stars.ring_profile(self.R, CELLS)

    def arm_ratio(self, mask_width: float) -> np.ndarray:
        """The ratio of means on every grid ring, shaped (R,): the mean of s over the source's arm mask - the
        share :func:`mask_share` of the ring, taken where the stellar pieces' sum is highest - over its mean on
        the rest of the ring. ``mask_width`` in kpc, the mask's full width perpendicular to an arm; the arm
        number the share is laid for is the law's own count on the ring. NaN on a ring no piece forces. A
        measurement of the solved rings: nothing is built from it."""
        profiles, carries = self.profiles, self.carries
        count = np.zeros(self.R.size) if self.design_count is None else np.asarray(self.design_count, dtype=float)
        share = mask_share(np.where(count > 0.0, count, np.nan), self.R, self.sin_pitch, mask_width)
        psi = self.stellar_sum()
        out = np.full(self.R.size, np.nan)
        for i in np.flatnonzero(carries & np.isfinite(share)):
            out[i] = ratio_of_means(profiles[i], psi[i], float(share[i]))
        return out

    def strongest_forcing(self) -> np.ndarray:
        """The harmonic of largest forcing amplitude on every grid ring, shaped (R,): the arm number the gas is
        pulled at most strongly (gate G3 item 6, read on the pieces' forcing since S60)."""
        return _HARMONIC[1:][np.argmax(self.forcing_amplitudes(), axis=1)]

    def arm_width(self, arm_number: np.ndarray | None = None) -> np.ndarray:
        """The full width at half maximum of every grid ring's tallest crest of s (:func:`crest_width`) as a
        fraction of the period 2π/m, shaped (R,); NaN on a ring no piece forces. A measurement only.

        m is the harmonic of largest forcing (:meth:`strongest_forcing`): the check's definition, fixed at gate
        G3 (item 6). ``arm_number`` (R,) reads the same widths against another period."""
        profiles, carries = self.profiles, self.carries
        m = self.strongest_forcing() if arm_number is None else np.asarray(arm_number, dtype=float)
        out = np.full(self.R.size, np.nan)
        for i in np.flatnonzero(carries):
            out[i] = crest_width(profiles[i]) / (TWO_PI / m[i])
        return out


# --------------------------------------------------------------------------------------------------------------
# The disclosed check's two measurements (D216 item 11 iv; the gate's follow-up). They read a solved ring and
# build nothing: no stage calls them. Their definitions are fixed by the ruling, before the build's numbers.
# --------------------------------------------------------------------------------------------------------------


def mask_share(arm_number, radius, sin_pitch, mask_width) -> np.ndarray:
    """The share of a ring the source's arm mask covers: m W/(2π R sin p), at most a half (S56's definition,
    D215, unchanged): a mask of full width W perpendicular to an arm, for the ring's power-weighted arm number
    m (``pattern.effective_arm_number``). ``radius`` and ``mask_width`` in kpc. NaN where the arm number is."""
    m = np.asarray(arm_number, dtype=float)
    return np.minimum(m * mask_width / (2.0 * math.pi * np.asarray(radius, dtype=float) * sin_pitch), 0.5)


def ratio_of_means(profile: np.ndarray, order_by: np.ndarray, share: float) -> float:
    """The mean of ``profile`` over the ``share`` of a ring's cells on which ``order_by`` is highest, over its
    mean on the rest. Both arrays are on the ring's equal cells; the cell the share cuts is counted by the
    fraction of it inside, and the order is stable (equal values keep the cells' own order)."""
    profile = np.asarray(profile, dtype=float)
    ranked = profile[np.argsort(-np.asarray(order_by, dtype=float), kind="stable")]
    cells = float(share) * ranked.size
    whole = min(int(math.floor(cells)), ranked.size)
    inside = float(ranked[:whole].sum()) + ((cells - whole) * float(ranked[whole]) if whole < ranked.size else 0.0)
    outside = float(ranked.sum()) - inside
    return (inside / cells) / (outside / (ranked.size - cells))


def crest_width(profile: np.ndarray) -> float:
    """The full width at half maximum of a ring's tallest crest, in radians of the pattern coordinate.

    The half level is midway between the ring's trough and its crest. From the tallest cell the profile is
    followed each way to where it first falls to that level, the crossing placed linearly between the two
    cells it lies between. NaN for a ring with no crest (a flat profile).
    """
    s = np.asarray(profile, dtype=float)
    n = s.size
    half = 0.5 * (float(s.max()) + float(s.min()))
    if not s.max() > half:
        return float("nan")
    ahead = np.roll(s, -int(np.argmax(s)))  # the crest first; then the cells after it, round the ring

    def reach(run: np.ndarray) -> float:
        """Cells from the crest to the first crossing of the half level along ``run`` (run[0] is the crest)."""
        k = int(np.argmax(run <= half))  # the first cell at or under the level: there is one, the trough
        return (k - 1) + (run[k - 1] - half) / (run[k - 1] - run[k])

    behind = np.concatenate([ahead[:1], ahead[:0:-1]])  # the crest, then the cells before it
    return (reach(ahead) + reach(behind)) * (2.0 * math.pi / n)


def compute_gas_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    # Everything is read, nothing drawn: the stellar pattern's arm pieces (the layer's) and checkpoint 1's disc.
    # A composed field (S55, D214): with the layer off compose gives the neutral value the declaration states,
    # everywhere. With it on, the pattern object comes from compose too, and a pattern with nothing to place
    # (unresolved, or no arm mode and no bar) is the neutral.
    cells = (R.size, ctx.grid.phi.size)
    made: dict[str, np.ndarray] = {}

    def response(decl: FieldDecl) -> np.ndarray:
        # Both fields come of one pattern, solved once: the gas's own contrast, with the bar's lanes, and the
        # contrast the star formation law reads, with the lanes' excess spread over the bar's footprint (S58).
        if not made:
            shape = _compose.gas_pattern(ctx.fields, R, ctx.constants)
            if shape is None or shape.flat:
                made.update({d.name: _compose.neutral(d, cells) for d in (GAS_DENSITY_CONTRAST, STAR_FORMATION_GAS_CONTRAST)})
            else:
                # The law's mean over each of the grid's φ cells, on each grid ring (gate G3 item 4): the interpolant
                # integrated exactly, so a ring's cells average to 1 to rounding on any grid and nothing is divided.
                laned, uniform = shape.published_cell_means(R, ctx.grid["phi"].edges)
                made.update({GAS_DENSITY_CONTRAST.name: laned, STAR_FORMATION_GAS_CONTRAST.name: uniform})
        return made[decl.name]

    return {
        decl.name: _compose.field(ctx.fields, decl, cells, lambda decl=decl: response(decl))
        for decl in (GAS_DENSITY_CONTRAST, STAR_FORMATION_GAS_CONTRAST)
    }


GAS_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="gas_pattern", slot="gas_pattern", checkpoint=3,
        about=(
            "The gas's own arm pattern: on every ring the steady response of isothermal gas to the stellar "
            "arms' potential in the frame that turns with the gas - no flow through the arms, no shock - "
            "solved ring by ring under uniform potential vorticity, and blended by the bar's taper with the "
            "bar's gas lanes - a uniform base and two arcs on the bar's leading side holding the excess of gas "
            "inside the bar's footprint, a conserving template with nothing drawn and one declared placeholder, "
            "its width (D216, D217). Since the stellar arms are a census of arm pieces the pull on a ring is "
            "put together piece by piece - each piece pulling by its own pitch, and each of its harmonics "
            "weakened by the thickness of the stellar layer, a measured fraction of the disc's scale length - "
            "and between two rings a ring's answer is carried along the pieces' own loci (D219). Reads the "
            "stellar pattern's pieces, their width and amplitude, and the disc's "
            "epicyclic frequency and surface density, and no gas column. Neither a contrast nor a width is "
            "put in: the measured ones are a disclosed check's target, held in the tests. The field it "
            "publishes is the response's exact mean over each grid cell's extent in azimuth, at the ring's own "
            "radius, so every ring keeps its gas on any grid with nothing divided. Beside it, the same "
            "contrast as the star formation law reads it: inside a bar's reach the lanes' excess spread "
            "evenly over the bar's footprint, because the lanes' width is a placeholder and star formation "
            "must not ride it; elsewhere the same numbers. It draws nothing; "
            "its fields are seeded through the pattern's drawn pitch and amplitudes and the layer's pieces."
        ),
        compute=compute_gas_pattern,
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=GAS_PATTERN_READS,
        publishes=(GAS_DENSITY_CONTRAST, STAR_FORMATION_GAS_CONTRAST),
    )
)
