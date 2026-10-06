"""arm_pieces: the census of arm pieces (checkpoint 3; S60, BUILD_III Phase P5; DECISIONS.md D219).

The physics publishes a law: how much arm power each ring carries (``arm_power_budget``), how many arms the law
counts there (``arm_design_count``), the disc's pitch, an arm's width, and the arm class. It does not say where an
arm lies, where it kinks, where it starts or ends: that is the outcome of how swing-amplified pieces form and link
up, which takes a disc stepped through time. This stage draws it - **the realised table** ``arm_piece``, one row a
piece - and the composing stage (``galaxy/stages/pieces.py``) applies the law to it. It replaces the ``arm_phases``
stage (S56-S59): the five modes' drawn phases, the common winding's segments and the ``arm_segment`` table are
retired with it.

**It runs after the** ``pattern`` **stage**, which draws the pitch on the pattern seed: a piece's pitch is the
disc's pitch times one plus the measured relative spread times a unit normal, so the realised table needs the
pitch, and a layer stage may read a seeded field (its own fields are synthetic whatever it reads: the graph's
rule). The stage that needs the pieces to compose a field is therefore no longer ``pattern``.

**A piece** (D219 item 1) is a row: the chain it belongs to and its place in it; its inner end (a radius and an
azimuth); its pitch; its azimuthal extent Δβ; whether a template pinned it. From its start it runs outward to
R exp(Δβ |tan p|), its azimuth advancing by Δβ in the trailing sense where the pitch is positive and the other
way where it is negative (a reversed piece, as measured arms have; nothing is floored or truncated).

**A chain** (item 2) is pieces joined end to start, laid outward from its start: each piece's Δβ log-normal
(median 60°, log-width 0.35, drawn again outside 20°-180°) and its pitch p(1 + 0.56 z), z a unit normal - S59's
draws, now per arm as the sources measure them - and the chain's total length a normal, 273° ± 143° in a grand
design and 244° ± 131° in a multi-armed disc, drawn again under 90° (the sources' definition of an arm), the last
piece cut to it. A chain that has left the grid is not continued (no ring would cross the rest).

**Which chains** (item 3; the lead's readings (a) and (c)). The class is derived by the ``bar`` stage with no
draw - barred: a grand design; unbarred: multi-armed - or pinned by a template:

- *a grand design in a barred disc*: two chains from the bar's two ends, at the bar's half-length on the bar's
  axis, and then the births below;
- *births, in every class*: the grid's rings are swept inside out, and while the chains crossing a ring are fewer
  than the law's arm number there, a chain starts on that ring - **at the midpoint of the widest azimuthal gap
  between the chains crossing it** (the gate's second follow-up, item 3: "the law's arm number m is m crests
  evenly spaced - that is what an m-fold mode is - and births at uniform azimuths spend the law's m-power at
  m = 1-2 as shot noise"); at a uniform azimuth where no chain crosses the ring - the first chain of an
  unbarred disc. No number enters the rule. (The law's number is not an integer: 4.8 gives five.) A ring with
  no arm power starts none; **and none is born inside a bar's half-length** - the sweep starts at R = a in a
  barred disc (the gate's first follow-up, item 2);
- *no crossing* (the second follow-up, item 2): "a drawn piece that meets another chain ends there, joined,
  without taper; a pinned piece is never cut; a drawn piece meeting a pinned one ends" - and its chain ends with
  it, not continued past the join. Pieces are straight lines in the plane of ln R and azimuth, so the meeting
  point is exact. The column ``arm_piece_join`` says which end of a piece meets another chain; the realised
  number of joins of a galaxy is the number of rows where it is not 0;
- *flocculent*, by a template's pin only: a birth is a single piece, of extent uniform on 37°-105° (the one
  flocculent galaxy's measured five); no chain length is drawn;
- *pinned pieces* (item 8): a template's measured arms, each row of the pin a chain of one or two pieces exactly
  on the fitted locus, placed by the Sun's azimuth; each continued beyond its measured range by drawn pieces,
  flagged unpinned, to the chain's drawn length - the drawn length less the measured range split evenly
  between its two ends, the inward part stopping at the bar's half-length (laid from the measured end inward;
  none where that end is already inside the bar). No chain is tied to the bar in a galaxy with pinned pieces;
  the births fill the rings the measured arms leave short, pinned chains counted as crossing.

**The seed** is ``texture_seed``; **the streams** are named by chain and order: ``("chain", c, "length")``,
``("chain", c, "start")`` for the azimuth of a birth on a ring no chain crosses (drawn only then), ``("chain", c, "out", k)`` for the k-th piece laid outward and
``("chain", c, "in", k)`` for the k-th laid inward - each stream z first, then the extent, as S59's segments drew.
Chains are numbered as they are made: the pinned ones in the pin's order, the two of the bar, then the births in
the sweep's order. The census reads the grid (the rings births are counted on), as the ruling's rule does.

**Every count is fixed in advance** (rule A1): an extent or a length is drawn again at most
:data:`MAX_DRAWS` times, a chain holds at most :data:`MAX_CHAIN_PIECES` pieces, and a ring starts at most the
law's count of chains; exhausted, the stage raises - it never clips a draw.

**The layer off:** nothing is drawn and the table has no row: no arm is placed, and every law is what it was.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import ARM_CLASSES, IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.pattern import PIECE_FIELDS, PIECE_JOINS, bar_terms, rotation_sense

MAX_DRAWS = 16  # how often an extent or a chain's length is drawn again before the stage raises (rule A1)
MAX_CHAIN_PIECES = 64  # the most pieces one laying holds: a length of 1280 degrees at the shortest extent
GRAND_DESIGN, MULTI_ARMED, FLOCCULENT = ARM_CLASSES
JOIN_NONE, JOIN_INNER, JOIN_OUTER = PIECE_JOINS
# A new piece's meeting with another chain is looked for past this share of its way: its own first point - where
# it leaves the piece before it, or is born - is no meeting.
MEETING_FROM = 1e-12

# What the draws read: a piece's extent (S59's four numbers), the spread of its pitch, a chain's length by class,
# and a flocculent piece's range.
PIECE_CONSTANTS: tuple[str, ...] = (
    "ARM_SEGMENT_EXTENT_MEDIAN", "ARM_SEGMENT_EXTENT_LOG_SCATTER", "ARM_SEGMENT_EXTENT_MIN", "ARM_SEGMENT_EXTENT_MAX",
    "ARM_SEGMENT_PITCH_RELATIVE_SCATTER",
    "ARM_CHAIN_LENGTH_GRAND_DESIGN", "ARM_CHAIN_LENGTH_GRAND_DESIGN_SCATTER",
    "ARM_CHAIN_LENGTH_MULTI_ARMED", "ARM_CHAIN_LENGTH_MULTI_ARMED_SCATTER", "ARM_CHAIN_LENGTH_MIN",
    "ARM_PIECE_FLOCCULENT_EXTENT_MIN", "ARM_PIECE_FLOCCULENT_EXTENT_MAX",
)


@dataclass(frozen=True, slots=True)
class Law:
    """What a laying reads: the disc's pitch and the numbers of the draws, angles in degrees as the constants
    hold them."""

    pitch_deg: float
    scatter: float            # the standard deviation of a piece's pitch over the disc's
    extent_median: float
    extent_log_scatter: float
    extent_min: float
    extent_max: float
    length_mean: float        # of a chain's total length, by the class; NaN for a flocculent disc, which draws none
    length_scatter: float
    length_min: float
    flocculent_min: float
    flocculent_max: float
    flocculent: bool
    turn: float               # +1 where a piece of positive pitch gains azimuth outwards: minus the rotation's sense

    @classmethod
    def of(cls, pitch_deg: float, arm_class: str, constants: Mapping[str, Any]) -> "Law":
        c = {k: float(constants[k]) for k in PIECE_CONSTANTS}
        grand = arm_class == GRAND_DESIGN
        flocculent = arm_class == FLOCCULENT
        mean = c["ARM_CHAIN_LENGTH_GRAND_DESIGN"] if grand else c["ARM_CHAIN_LENGTH_MULTI_ARMED"]
        scatter = c["ARM_CHAIN_LENGTH_GRAND_DESIGN_SCATTER"] if grand else c["ARM_CHAIN_LENGTH_MULTI_ARMED_SCATTER"]
        return cls(
            float(pitch_deg), c["ARM_SEGMENT_PITCH_RELATIVE_SCATTER"],
            c["ARM_SEGMENT_EXTENT_MEDIAN"], c["ARM_SEGMENT_EXTENT_LOG_SCATTER"], c["ARM_SEGMENT_EXTENT_MIN"], c["ARM_SEGMENT_EXTENT_MAX"],
            float("nan") if flocculent else mean, float("nan") if flocculent else scatter, c["ARM_CHAIN_LENGTH_MIN"],
            c["ARM_PIECE_FLOCCULENT_EXTENT_MIN"], c["ARM_PIECE_FLOCCULENT_EXTENT_MAX"], flocculent,
            -rotation_sense(pitch_deg),
        )


@dataclass(frozen=True, slots=True)
class Piece:
    """One row of the census: its inner end (ln R and azimuth), its pitch in degrees, its extent in radians, and
    which of its ends meets another chain (0 none, 1 its inner end, 2 its outer end)."""

    chain: int
    x: float          # ln of the start radius, kpc
    azimuth: float    # the start azimuth, rad
    pitch_deg: float
    extent: float
    pinned: bool
    join: float = JOIN_NONE

    def reach(self) -> float:
        """How far the piece runs in ln R: Δβ |tan p|."""
        return self.extent * abs(math.tan(math.radians(self.pitch_deg)))

    def advance(self, turn: float) -> float:
        """How far its azimuth moves from its inner end to its outer: Δβ in the trailing sense for a pitch that is
        positive - or exactly 0, an arc at its radius - and the other way for a negative one."""
        return turn * self.extent * (1.0 if math.tan(math.radians(self.pitch_deg)) >= 0.0 else -1.0)

    def ends(self, turn: float) -> tuple[tuple[float, float], tuple[float, float]]:
        """((ln R, azimuth) of the inner end, of the outer end): the piece is the straight line between them in
        the log-polar plane, its azimuth not wrapped."""
        return (self.x, self.azimuth), (self.x + self.reach(), self.azimuth + self.advance(turn))


def meeting(start: tuple[float, float], end: tuple[float, float], others: Sequence[tuple[tuple[float, float], tuple[float, float]]]) -> float | None:
    """Where the straight line from ``start`` to ``end`` in the log-polar plane (ln R, azimuth) first meets one of
    ``others`` - lines each given by its two ends - as the share of the way from ``start`` to ``end``, in
    (:data:`MEETING_FROM`, 1]; None where it meets none. The azimuth is a circle's: each of the others is tried a
    turn either side of where its start lies nearest ``start`` (a piece runs half a turn at most, so no other
    image can reach). "Pieces are straight in the log-polar plane, so the meeting point is exact" (D219, the
    gate's second follow-up, item 2). Parallel lines do not meet."""
    ax, ay = end[0] - start[0], end[1] - start[1]
    first: float | None = None
    for (bx0, by0), (bx1, by1) in others:
        bx, by = bx1 - bx0, by1 - by0
        det = ax * by - ay * bx
        if det == 0.0:
            continue
        nearest = 2.0 * math.pi * round((start[1] - by0) / (2.0 * math.pi))
        for turns in (-1.0, 0.0, 1.0):
            ox, oy = bx0 - start[0], by0 + nearest + 2.0 * math.pi * turns - start[1]
            s = (ox * by - oy * bx) / det   # along the new line
            t = (ox * ay - oy * ax) / det   # along the other
            if MEETING_FROM < s <= 1.0 and 0.0 <= t <= 1.0 and (first is None or s < first):
                first = s
    return first


class Laying:
    """The pieces laid so far, and the two rules a new one is laid by (D219, the gate's second follow-up, items 2
    and 3): **no crossing** - "a drawn piece that meets another chain ends there, joined, without taper; a pinned
    piece is never cut; a drawn piece meeting a pinned one ends" - and **births in the widest gap** - "a chain is
    born at the midpoint of the widest azimuthal gap between the chains crossing its birth ring"."""

    def __init__(self, turn: float) -> None:
        self.turn = turn
        self.pieces: list[Piece] = []

    def add(self, piece: Piece) -> None:
        self.pieces.append(piece)

    def cut(self, piece: Piece, inward: bool) -> Piece:
        """``piece`` as it is laid: whole, or - where it meets a piece of another chain on its way - ended there
        and flagged joined at that end. A piece laid outward runs from its inner end and is cut at its outer; one
        laid ``inward`` runs from its outer end and is cut at its inner."""
        inner, outer = piece.ends(self.turn)
        others = [p.ends(self.turn) for p in self.pieces if p.chain != piece.chain]
        share = meeting(outer, inner, others) if inward else meeting(inner, outer, others)
        if share is None:
            return piece
        kept = Piece(piece.chain, piece.x, piece.azimuth, piece.pitch_deg, share * piece.extent, piece.pinned, JOIN_INNER if inward else JOIN_OUTER)
        if not inward:
            return kept
        # Laid inward, the piece keeps its outer end: its inner end is the meeting point.
        return Piece(piece.chain, outer[0] - kept.reach(), outer[1] - kept.advance(self.turn), piece.pitch_deg, kept.extent, piece.pinned, JOIN_INNER)

    def span(self, chain: int) -> tuple[float, float] | None:
        """The chain's reach in ln R: what "crosses a ring" is counted on. None for a chain with no piece."""
        own = [p for p in self.pieces if p.chain == chain]
        return (min(p.x for p in own), max(p.x + p.reach() for p in own)) if own else None

    def crossings(self, x: float) -> list[float]:
        """The azimuths, within one turn, at which the chains laid so far cross the ring at ln R = ``x``: where
        each piece whose locus crosses it stands on it."""
        out = []
        for p in self.pieces:
            reach = p.reach()
            if p.x <= x < p.x + reach:
                out.append((p.azimuth + (x - p.x) / reach * p.advance(self.turn)) % (2.0 * math.pi))
        return out

    def widest_gap(self, x: float) -> float | None:
        """The midpoint of the widest azimuthal gap between the chains crossing the ring at ln R = ``x``, within
        one turn; None where none crosses. Of two gaps of one width to the last bit, the one that starts at the
        lesser azimuth - and two gaps that are equal but for rounding are told apart by that rounding (the four
        quarter-turns a barred disc's fourth chain finds, for one).
        One chain crossing leaves one gap, the whole turn: the midpoint is opposite it."""
        at = sorted(self.crossings(x))
        if not at:
            return None
        best, start = -1.0, 0.0
        for k, azimuth in enumerate(at):
            gap = (at[k + 1] - azimuth) if k + 1 < len(at) else (at[0] + 2.0 * math.pi - azimuth)
            if gap > best:
                best, start = gap, azimuth
        return (start + 0.5 * best) % (2.0 * math.pi)


def draw_piece(generator: Any, law: Law) -> tuple[float, float]:
    """(Δβ in radians, the pitch's unit normal deviate) of one drawn piece, on its own stream: the deviate first,
    then the extent - log-normal about the median, drawn again while outside the sample's range, never clipped
    (S59's draw, D218 item 2); a flocculent disc's is uniform on its measured range instead."""
    deviate = float(generator.normal())
    if law.flocculent:
        return math.radians(law.flocculent_min + (law.flocculent_max - law.flocculent_min) * float(generator.random())), deviate
    for _ in range(MAX_DRAWS):
        extent = law.extent_median * math.exp(law.extent_log_scatter * float(generator.normal()))
        if law.extent_min <= extent <= law.extent_max:
            return math.radians(extent), deviate
    raise ArithmeticError(f"a piece's extent fell outside {law.extent_min:g}-{law.extent_max:g} degrees {MAX_DRAWS} times running")


def draw_length(generator: Any, law: Law) -> float:
    """A chain's total azimuthal length in radians: normal about the class's mean, drawn again while under the
    shortest length the sources call an arm."""
    for _ in range(MAX_DRAWS):
        length = float(generator.normal(law.length_mean, law.length_scatter))
        if length >= law.length_min:
            return math.radians(length)
    raise ArithmeticError(f"a chain's length fell under {law.length_min:g} degrees {MAX_DRAWS} times running")


def lay_outward(laying: Laying, chain: int, x: float, azimuth: float, length: float, law: Law, stream: Callable[[int], Any], x_edge: float) -> None:
    """Pieces joined end to start from (``x`` = ln R, ``azimuth``) outward, to a total extent of ``length``
    radians, the last piece cut to it. No piece is started past ``x_edge``, the grid's last ring. **A piece that
    meets another chain ends there, and the chain with it**: it is not continued past the join."""
    left = float(length)
    for k in range(MAX_CHAIN_PIECES + 1):
        if not left > 0.0 or not x <= x_edge:
            return
        if k == MAX_CHAIN_PIECES:
            break
        extent, deviate = draw_piece(stream(k), law)
        piece = laying.cut(Piece(chain, x, azimuth, law.pitch_deg * (1.0 + law.scatter * deviate), min(extent, left), False), inward=False)
        laying.add(piece)
        if piece.join != JOIN_NONE:
            return
        left -= piece.extent
        x, azimuth = x + piece.reach(), azimuth + piece.advance(law.turn)
    raise ArithmeticError(f"chain {chain} holds more than {MAX_CHAIN_PIECES} pieces")


def lay_inward(laying: Laying, chain: int, x: float, azimuth: float, length: float, law: Law, stream: Callable[[int], Any], x_floor: float) -> None:
    """Pieces joined end to start from (``x``, ``azimuth``) inward, to a total extent of ``length`` radians or to
    ``x_floor`` (ln of the bar's half-length), whichever comes first: each piece's outer end is the last one's
    inner end, and the piece that would pass the floor is cut where it reaches it. None where the start is at or
    inside the floor. **A piece that meets another chain on its way in ends there, and the chain with it.**"""
    left = float(length)
    for k in range(MAX_CHAIN_PIECES + 1):
        if not left > 0.0 or not x > x_floor:
            return
        if k == MAX_CHAIN_PIECES:
            break
        extent, deviate = draw_piece(stream(k), law)
        pitch = law.pitch_deg * (1.0 + law.scatter * deviate)
        extent = min(extent, left)
        slope = abs(math.tan(math.radians(pitch)))
        floored = slope > 0.0 and x - extent * slope < x_floor
        if floored:
            extent = (x - x_floor) / slope  # where the piece reaches the bar's half-length
        probe = Piece(chain, x, azimuth, pitch, extent, False)
        piece = laying.cut(Piece(chain, x - probe.reach(), azimuth - probe.advance(law.turn), pitch, extent, False), inward=True)
        laying.add(piece)
        if piece.join != JOIN_NONE or floored:
            return
        left -= extent
        x, azimuth = piece.x, piece.azimuth
    raise ArithmeticError(f"chain {chain} holds more than {MAX_CHAIN_PIECES} pieces")


def pinned_pieces(chain: int, row: Sequence[Any], sun_azimuth: float, sense: float) -> tuple[list[Piece], tuple[float, float], tuple[float, float]]:
    """One row of a template's measured arms (``registry.ARM_PIECE_COLUMNS``) as pinned pieces, with the chain's
    two ends: ``(pieces, low end, high end)``, each end (ln R, azimuth) at the low and the high end of the
    row's range of azimuth β.

    The row's locus is ln(R/R_kink) = −(β − β_kink) tan ψ, ψ one pitch up to the kink and another past it; a
    point at β stands at φ = φ_sun + sense · β, the Sun at β = 0 (D219 item 8). Each stretch of one pitch is one
    piece - one for the whole row where the two pitches are the same - entered by its inner end: the high-β
    end of a trailing stretch (ψ > 0), the low-β end of a leading one."""
    _, lo, hi, kink, radius_kink, below, above = row
    stretches = [(lo, hi, below)] if below == above else [(lo, kink, below), (kink, hi, above)]

    def at(beta: float, pitch: float) -> tuple[float, float]:
        return (math.log(radius_kink) - math.radians(beta - kink) * math.tan(math.radians(pitch)), sun_azimuth + sense * math.radians(beta))

    pieces = []
    for a, b, pitch in stretches:
        if not b > a:
            continue
        x, azimuth = at(b if pitch > 0.0 else a, pitch)
        pieces.append(Piece(chain, x, azimuth, float(pitch), math.radians(b - a), True))
    return pieces, at(lo, below), at(hi, above)


def census(
    R: np.ndarray, design_count: np.ndarray, law: Law, arm_class: str, bar_length: float, bar_angle: float,
    pinned_rows: Sequence[Sequence[Any]], sun_azimuth: float, stream: Callable[..., Any],
) -> list[Piece]:
    """The realised census: every piece of every chain, in the order the chains are made (the module's docstring).

    ``R`` the grid's rings, kpc; ``design_count`` the law's arm number on them (0 where a ring has no arm power);
    ``bar_length`` and ``bar_angle`` the bar's (NaN in an unbarred galaxy); ``pinned_rows`` a template's measured
    arms (none: an empty sequence) and ``sun_azimuth`` where they are measured from; ``stream(*path)`` a generator
    on the texture seed for one named draw."""
    R = np.asarray(R, dtype=float)
    x_ring = np.log(R)
    x_edge = float(x_ring[-1])
    sense = -law.turn
    laying = Laying(law.turn)

    def outward(chain: int, x: float, azimuth: float, length: float) -> None:
        lay_outward(laying, chain, x, azimuth, length, law, lambda k: stream("chain", chain, "out", k), x_edge)

    def length_of(chain: int) -> float:
        return draw_length(stream("chain", chain, "length"), law)

    made = 0
    # The pinned chains (D219 item 8; the lead's reading (c)). Every measured piece is laid first - "a pinned piece
    # is never cut" - and then each arm's drawn continuation, which ends where it meets another chain.
    if len(pinned_rows):
        if not (math.isfinite(sun_azimuth) and math.isfinite(bar_length)):
            raise ValueError(
                "measured arm pieces are placed by the Sun's azimuth, and their inward continuation stops at the "
                "bar's half-length: the galaxy has no bar or no pinned angle of the bar to the Sun-centre line"
            )
        x_bar = math.log(bar_length)
        measured = []
        for row in pinned_rows:
            chain = made
            made += 1
            pieces, low, high = pinned_pieces(chain, row, sun_azimuth, sense)
            for piece in pieces:
                laying.add(piece)
            measured.append((chain, row, low, high))
        for chain, row, low, high in measured:
            if law.flocculent:
                continue
            spare = length_of(chain) - math.radians(float(row[2]) - float(row[1]))
            if spare > 0.0:
                # Past the range's low-β end the arm runs on outward; past its high-β end, inward to the bar.
                outward(chain, low[0], low[1], 0.5 * spare)
                lay_inward(laying, chain, high[0], high[1], 0.5 * spare, law, lambda k, c=chain: stream("chain", c, "in", k), x_bar)
    # The two chains of a bar (item 3): none in a galaxy with pinned pieces, and none in a class without them.
    elif arm_class == GRAND_DESIGN and math.isfinite(bar_length) and math.isfinite(bar_angle):
        for end in (0.0, math.pi):
            chain = made
            made += 1
            outward(chain, math.log(bar_length), bar_angle + end, length_of(chain))
    # The births (item 3; the lead's reading (a)): rings swept inside out.
    design_count = np.asarray(design_count, dtype=float)
    spans = [span for span in (laying.span(chain) for chain in range(made)) if span is not None]
    # The gate's follow-up, item 2: "No chain is born inside a bar's half-length; the birth sweep starts at R = a in
    # a barred disc."
    x_first = math.log(bar_length) if math.isfinite(bar_length) else -math.inf
    for i in range(R.size):
        wanted = float(design_count[i])
        x = float(x_ring[i])
        if not wanted > 0.0 or x < x_first:
            continue
        crossing = sum(1 for lo, hi in spans if lo <= x < hi)
        for _ in range(int(math.ceil(wanted))):  # at most the law's count of births on one ring (rule A1)
            if not crossing < wanted:
                break
            chain = made
            made += 1
            # The second follow-up, item 3: "A chain is born at the midpoint of the widest azimuthal gap between the
            # chains crossing its birth ring; the first chain of an unbarred disc at a uniform azimuth" - and so any
            # chain born on a ring that no chain crosses, where there is no gap to halve (the builder's reading of
            # a case the rule does not name). The uniform draw is made only then.
            start = laying.widest_gap(x)
            if start is None:
                start = 2.0 * math.pi * float(stream("chain", chain, "start").random())
            if law.flocculent:  # a single piece, and no chain length drawn
                extent, deviate = draw_piece(stream("chain", chain, "out", 0), law)
                laying.add(laying.cut(Piece(chain, x, start, law.pitch_deg * (1.0 + law.scatter * deviate), extent, False), inward=False))
            else:
                outward(chain, x, start, length_of(chain))
            span = laying.span(chain)
            if span is not None:
                spans.append(span)
            crossing += 1
    return laying.pieces


def columns(pieces: Sequence[Piece]) -> dict[str, np.ndarray]:
    """The census as the table's columns, the rows by chain and, in a chain, inside out."""
    order: dict[int, list[int]] = {}
    for i, p in enumerate(pieces):
        order.setdefault(p.chain, []).append(i)
    rows: list[tuple[float, ...]] = []
    for chain in sorted(order):
        for place, i in enumerate(sorted(order[chain], key=lambda i: (pieces[i].x, i))):
            p = pieces[i]
            rows.append((float(chain), float(place), math.exp(p.x), p.azimuth % (2.0 * math.pi), p.pitch_deg, p.extent, 1.0 if p.pinned else 0.0, float(p.join)))
    table = np.array(rows, dtype=float).reshape(len(rows), len(PIECE_FIELDS))
    return {name: np.ascontiguousarray(table[:, k]) for k, name in enumerate(PIECE_FIELDS)}


_STANDS_IN_FOR = (
    "Where a galaxy's spiral arms lie, where each starts, kinks and ends, and how they link into arms: the "
    "outcome of how swing-amplified pieces of arm form, shear and join in a self-gravitating disc stepped "
    "through time, which the model does not integrate."
)
_CONSERVES = (
    "Every ring's mean density and every law: a piece adds its ridge to a ring less the ridge's own mean round "
    "that ring, so the composed density contrast averages to 1 on every ring exactly, and no radial field, no "
    "scalar, no budget of arm power and no expected count of any census moves. It does not keep a ring's "
    "realised arm power at the budget: the budget is met on average over these draws, and one galaxy's rings "
    "differ from it - by what the composed stage publishes beside it, ring by ring. It says which part of a "
    "ring holds an arm, and so where the censuses' objects are (their realised totals are another draw until "
    "L1, as for every placement)."
)
_STATISTIC = (
    "A piece's azimuthal extent log-normal, median 60 degrees and log-width 0.35, drawn again outside 20-180 "
    "degrees - the reader's arithmetic on the 38 printed rows of one survey of four galaxies [verified: Honig & "
    "Reid 2015, ApJ 800, 53 = arXiv:1412.1012, Tables 2-5; docs/READING_ARM_SEGMENTS.md A1.1]; its pitch the "
    "disc's times one plus 0.56 times a unit normal, independent from piece to piece and untruncated - the "
    "measured variation of the pitch along an arm, 0.56 +- 0.25 over 155 galaxies [verified: Savchenko, Marchuk, "
    "Mosenkov & Grishunin 2020, MNRAS 493, 390, arXiv:2001.09110; docs/READING_ARM_SEGMENTS.md A1.1]. A chain's "
    "whole length normal, 273 +- 143 degrees in a grand design and 244 +- 131 in a multi-armed disc, drawn again "
    "under 90 [verified: Chugunov, Marchuk & Savchenko 2025, arXiv:2504.11642, Sect. 3; "
    "docs/READING_ARM_PIECES.md Part A 3]. How many chains cross a ring: the arm-number law's own count there, "
    "a chain started wherever fewer cross, at the middle of the widest gap between those that do - a reading of "
    "the law, declared as one (a law of m arms is m crests evenly spaced), and no measured statistic; a drawn "
    "piece ends where it meets another chain, joined to it - crossing arms are described by no source, "
    "branches and joins are observed and their frequency is measured nowhere, so the number of joins is a "
    "prediction with nothing to judge it by; two chains from a bar's ends, where Block et al. 2004 find the arms of barred "
    "galaxies starting within 20 degrees of the bar's axis (a detection window; docs/READING_BAR.md). A "
    "flocculent disc's pieces: single, uniform on 37-105 degrees, the five measured segments of one galaxy "
    "[inferred from: Herrera-Endoqui et al. 2015, A&A 582, A86, Table 3; docs/READING_ARM_PIECES.md Part A 5] - "
    "no source gives the number or the lengths of a flocculent disc's pieces (a debt). Not measured anywhere read, "
    "and so not drawn: where arms branch, what share start at a bar's end, how unequal a galaxy's arms are, any "
    "correlation between neighbouring pieces [docs/READING_ARM_PIECES.md, the lead's summary]. Pinned rows are "
    "not drawn at all: they are the template's measured loci. (DECISIONS.md D219 items 1-3 and 8.)"
)


def _column(name: str, label: str, unit: str, about: str) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.TABLE_COLUMN, of="arm_piece",
        meaningful_zero=True, provenance="synthetic",
        about=about + (
            " One row an arm piece of the realised census, the rows by chain and inside out along each chain. No "
            "row with the randomness layer off: no arm is placed. A column of a small table, not of a catalogue: "
            "the model's own stages read the table whole to lay the stars' arms and the gas's answer to them, and "
            "it is not shown by the viewer, which draws the arms it sets."
        ),
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC,
    )


ARM_PIECE_CHAIN = _column(
    "arm_piece_chain", "Chain an arm piece belongs to", "count",
    "The number of the chain - the arm - this piece is part of, counted from 0 in the order the chains are "
    "made: a template's measured arms first, then the two chains from a bar's ends, then the chains started "
    "ring by ring from the centre outward wherever fewer cross a ring than the law counts. A flocculent "
    "disc's chains are one piece each.",
)
ARM_PIECE_ORDER = _column(
    "arm_piece_order", "Place of an arm piece in its chain", "count",
    "Where along its chain the piece stands, counted from 0 at the chain's innermost piece outward. Pieces of "
    "one chain are joined end to start; where they join the pitch changes, which is an arm's kink.",
)
ARM_PIECE_START_RADIUS = _column(
    "arm_piece_start_radius", "Radius of an arm piece's inner end", "kpc",
    "The radius at which the piece starts. From there it runs outward to this radius times the exponential of "
    "its extent times the tangent of its pitch, taken without its sign - so a piece of nearly no pitch is a "
    "short step in radius that still carries its whole extent round the disc.",
)
ARM_PIECE_START_AZIMUTH = _column(
    "arm_piece_start_azimuth", "Azimuth of an arm piece's inner end", "rad",
    "Where round the disc the piece starts, within one turn. From there its azimuth changes by its extent on "
    "the way to its outer end, in proportion to the logarithm of the radius: growing outward for a piece of "
    "positive pitch - a trailing arm, the disc turning the other way - and falling for one of negative pitch.",
)
ARM_PIECE_PITCH = _column(
    "arm_piece_pitch", "Pitch of an arm piece", "deg",
    "The piece's own pitch angle: the disc's pitch times one plus the measured relative spread times a unit "
    "normal draw, so a piece in twenty-seven comes out reversed - leading - and a few nearly circular, as "
    "measured arms' stretches do; nothing is floored and nothing truncated. A template's measured piece holds "
    "its fitted pitch. The pitch sets how wide the piece lies on a ring and how hard it pulls the gas.",
)
ARM_PIECE_EXTENT = _column(
    "arm_piece_extent", "Azimuthal extent of an arm piece", "rad",
    "How far round the disc the piece runs from its inner end to its outer. The last piece of a chain is cut "
    "so that the chain's pieces add up to the chain's drawn length; a piece laid inward from a measured arm "
    "is cut where it reaches the bar's half-length.",
)
ARM_PIECE_PINNED = _column(
    "arm_piece_pinned", "Whether a template pinned the arm piece", "dimensionless",
    "1 for a piece a template states from a measurement - it lies exactly on the fitted locus - and 0 for one "
    "the layer drew, the drawn pieces that continue a measured arm beyond its measured range among them.",
)
ARM_PIECE_JOIN = _column(
    "arm_piece_join", "Which end of an arm piece meets another chain", "dimensionless",
    "0 for a piece neither of whose ends meets another chain, 1 for one whose inner end does and 2 for one whose "
    "outer end does. A drawn piece that would cross another chain ends where it meets it, and its chain ends "
    "there too: the two arms join, as arms are seen to branch and join, and no two chains cross. A joined end "
    "is not faded - the piece runs at full height into the arm it meets. A measured piece is never cut, so it "
    "is always 0 for one; a drawn piece that meets a measured one ends. The number of rows where this is not "
    "0 is the galaxy's number of joins - a prediction with nothing to judge it by, since how often arms join "
    "is measured nowhere.",
)
ARM_PIECES: tuple[FieldDecl, ...] = (
    ARM_PIECE_CHAIN, ARM_PIECE_ORDER, ARM_PIECE_START_RADIUS, ARM_PIECE_START_AZIMUTH, ARM_PIECE_PITCH, ARM_PIECE_EXTENT, ARM_PIECE_PINNED,
    ARM_PIECE_JOIN,
)
assert tuple(d.name for d in ARM_PIECES) == PIECE_FIELDS


def compute_arm_pieces(ctx: Context) -> Mapping[str, Any]:
    def draw() -> dict[str, np.ndarray]:
        pitch = float(ctx.fields["pitch_angle"])
        if not math.isfinite(pitch):  # a mesh too coarse for the shear: the pattern is unresolved and nothing is laid
            return columns(())
        R = ctx.grid.R
        arm_class = str(ctx.fields["arm_class"])
        bar_length = float(ctx.fields["bar_half_length"])
        law = Law.of(pitch, arm_class, ctx.constants)
        pinned = ctx.inputs.get("arm_pieces") or ()
        laid = census(
            R, ctx.fields["arm_design_count"], law, arm_class, bar_length, bar_terms(R, pitch, bar_length)[2],
            pinned, float(ctx.fields["sun_azimuth"]), lambda *path: ctx.rng("texture_seed", *path),
        )
        return columns(laid)

    # compose decides: the draw, or - with the layer off - no row at all, the streams untouched.
    return _compose.realise(ctx.fields, draw, lambda: columns(()))


ARM_PIECES_STAGE = IMPLEMENTATIONS.register(
    Stage(
        id="arm_pieces", slot="arm_pieces", checkpoint=3,
        about=(
            "The randomness layer's realisation of the arms: a census of arm pieces, drawn on the texture seed. "
            "Each piece is a stretch of arm on its own logarithmic spiral - a start, a pitch, a run round the "
            "disc; pieces joined end to start make a chain, an arm with kinks. A barred disc gets two chains "
            "from the bar's ends; every disc gets a chain started on each ring that fewer chains cross than the "
            "arm-number law counts there, in the middle of the widest gap between those that do; a drawn piece "
            "that meets another chain ends there, joined to it, so no two chains cross; a disc a template states to be flocculent gets "
            "single short pieces instead of chains; and a template's measured arms are entered where they were "
            "measured and continued by drawn pieces. Synthetic: it stands in for the dynamics that set where "
            "arms form and join, moves no amplitude, no budget and no ring's mean, and lays nothing with the "
            "layer off. It runs after the pattern stage, whose drawn pitch each piece's pitch scatters about."
        ),
        compute=compute_arm_pieces,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_inputs=("arm_pieces",),  # S60 (D219 item 8): a template's measured arms, or not given (read with .get)
        reads_constants=PIECE_CONSTANTS,
        requires=("pitch_angle", "arm_class", "bar_half_length", "arm_design_count", "sun_azimuth"),
        publishes=ARM_PIECES,
    )
)
