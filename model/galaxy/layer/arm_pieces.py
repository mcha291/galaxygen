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
  than the law's arm number there, a chain starts on that ring at a uniform azimuth. (The law's number is not an
  integer: 4.8 gives five.) A ring with no arm power starts none;
- *flocculent*, by a template's pin only: a birth is a single piece, of extent uniform on 37°-105° (the one
  flocculent galaxy's measured five); no chain length is drawn;
- *pinned pieces* (item 8): a template's measured arms, each row of the pin a chain of one or two pieces exactly
  on the fitted locus, placed by the Sun's azimuth; each continued beyond its measured range by drawn pieces,
  flagged unpinned, to the chain's drawn length - the drawn length less the measured range split evenly
  between its two ends, the inward part stopping at the bar's half-length (laid from the measured end inward;
  none where that end is already inside the bar). No chain is tied to the bar in a galaxy with pinned pieces;
  the births fill the rings the measured arms leave short, pinned chains counted as crossing.

**The seed** is ``texture_seed``; **the streams** are named by chain and order: ``("chain", c, "length")``,
``("chain", c, "start")`` for a birth's azimuth, ``("chain", c, "out", k)`` for the k-th piece laid outward and
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
from galaxy.stages.pattern import PIECE_FIELDS, bar_terms, rotation_sense

MAX_DRAWS = 16  # how often an extent or a chain's length is drawn again before the stage raises (rule A1)
MAX_CHAIN_PIECES = 64  # the most pieces one laying holds: a length of 1280 degrees at the shortest extent
GRAND_DESIGN, MULTI_ARMED, FLOCCULENT = ARM_CLASSES

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
    """One row of the census: its inner end (ln R and azimuth), its pitch in degrees, its extent in radians."""

    chain: int
    x: float          # ln of the start radius, kpc
    azimuth: float    # the start azimuth, rad
    pitch_deg: float
    extent: float
    pinned: bool

    def reach(self) -> float:
        """How far the piece runs in ln R: Δβ |tan p|."""
        return self.extent * abs(math.tan(math.radians(self.pitch_deg)))

    def advance(self, turn: float) -> float:
        """How far its azimuth moves from its inner end to its outer: Δβ in the trailing sense for a positive
        pitch, the other way for a negative one, nothing for a pitch of exactly 0."""
        tangent = math.tan(math.radians(self.pitch_deg))
        return turn * self.extent * (1.0 if tangent > 0.0 else -1.0 if tangent < 0.0 else 0.0)


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


def lay_outward(chain: int, x: float, azimuth: float, length: float, law: Law, stream: Callable[[int], Any], x_edge: float) -> list[Piece]:
    """Pieces joined end to start from (``x`` = ln R, ``azimuth``) outward, to a total extent of ``length``
    radians, the last piece cut to it. No piece is started past ``x_edge``, the grid's last ring."""
    pieces: list[Piece] = []
    left = float(length)
    for k in range(MAX_CHAIN_PIECES + 1):
        if not left > 0.0 or not x <= x_edge:
            return pieces
        if k == MAX_CHAIN_PIECES:
            break
        extent, deviate = draw_piece(stream(k), law)
        piece = Piece(chain, x, azimuth, law.pitch_deg * (1.0 + law.scatter * deviate), min(extent, left), False)
        pieces.append(piece)
        left -= piece.extent
        x, azimuth = x + piece.reach(), azimuth + piece.advance(law.turn)
    raise ArithmeticError(f"chain {chain} holds more than {MAX_CHAIN_PIECES} pieces")


def lay_inward(chain: int, x: float, azimuth: float, length: float, law: Law, stream: Callable[[int], Any], x_floor: float) -> list[Piece]:
    """Pieces joined end to start from (``x``, ``azimuth``) inward, to a total extent of ``length`` radians or to
    ``x_floor`` (ln of the bar's half-length), whichever comes first: each piece's outer end is the last one's
    inner end, and the piece that would pass the floor is cut where it reaches it. None where the start is at or
    inside the floor."""
    pieces: list[Piece] = []
    left = float(length)
    for k in range(MAX_CHAIN_PIECES + 1):
        if not left > 0.0 or not x > x_floor:
            return pieces
        if k == MAX_CHAIN_PIECES:
            break
        extent, deviate = draw_piece(stream(k), law)
        pitch = law.pitch_deg * (1.0 + law.scatter * deviate)
        extent = min(extent, left)
        slope = abs(math.tan(math.radians(pitch)))
        cut = slope > 0.0 and x - extent * slope < x_floor
        if cut:
            extent = (x - x_floor) / slope  # where the piece reaches the bar's half-length
        probe = Piece(chain, x, azimuth, pitch, extent, False)
        piece = Piece(chain, x - probe.reach(), azimuth - probe.advance(law.turn), pitch, extent, False)
        pieces.append(piece)
        left -= extent
        x, azimuth = piece.x, piece.azimuth
        if cut:
            return pieces
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
    pieces: list[Piece] = []
    spans: list[tuple[float, float]] = []  # each chain's reach in ln R: what "crosses a ring" is counted on

    def close(chain_pieces: list[Piece]) -> None:
        pieces.extend(chain_pieces)
        if chain_pieces:
            spans.append((min(p.x for p in chain_pieces), max(p.x + p.reach() for p in chain_pieces)))

    def outward(chain: int, x: float, azimuth: float, length: float) -> list[Piece]:
        return lay_outward(chain, x, azimuth, length, law, lambda k: stream("chain", chain, "out", k), x_edge)

    def length_of(chain: int) -> float:
        return draw_length(stream("chain", chain, "length"), law)

    made = 0
    # The pinned chains (D219 item 8; the lead's reading (c)).
    if len(pinned_rows):
        if not (math.isfinite(sun_azimuth) and math.isfinite(bar_length)):
            raise ValueError(
                "measured arm pieces are placed by the Sun's azimuth, and their inward continuation stops at the "
                "bar's half-length: the galaxy has no bar or no pinned angle of the bar to the Sun-centre line"
            )
        x_bar = math.log(bar_length)
        for row in pinned_rows:
            chain = made
            made += 1
            measured, low, high = pinned_pieces(chain, row, sun_azimuth, sense)
            grown: list[Piece] = list(measured)
            if not law.flocculent:
                spare = length_of(chain) - math.radians(float(row[2]) - float(row[1]))
                if spare > 0.0:
                    # Past the range's low-β end the arm runs on outward; past its high-β end, inward to the bar.
                    grown += outward(chain, low[0], low[1], 0.5 * spare)
                    grown += lay_inward(chain, high[0], high[1], 0.5 * spare, law, lambda k, c=chain: stream("chain", c, "in", k), x_bar)
            close(grown)
    # The two chains of a bar (item 3): none in a galaxy with pinned pieces, and none in a class without them.
    elif arm_class == GRAND_DESIGN and math.isfinite(bar_length) and math.isfinite(bar_angle):
        for end in (0.0, math.pi):
            chain = made
            made += 1
            close(outward(chain, math.log(bar_length), bar_angle + end, length_of(chain)))
    # The births (item 3; the lead's reading (a)): rings swept inside out.
    design_count = np.asarray(design_count, dtype=float)
    for i in range(R.size):
        wanted = float(design_count[i])
        if not wanted > 0.0:
            continue
        x = float(x_ring[i])
        crossing = sum(1 for lo, hi in spans if lo <= x < hi)
        for _ in range(int(math.ceil(wanted))):  # at most the law's count of births on one ring (rule A1)
            if not crossing < wanted:
                break
            chain = made
            made += 1
            start = 2.0 * math.pi * float(stream("chain", chain, "start").random())
            if law.flocculent:  # a single piece, and no chain length drawn
                extent, deviate = draw_piece(stream("chain", chain, "out", 0), law)
                close([Piece(chain, x, start, law.pitch_deg * (1.0 + law.scatter * deviate), extent, False)])
            else:
                close(outward(chain, x, start, length_of(chain)))
            crossing += 1
    return pieces


def columns(pieces: Sequence[Piece]) -> dict[str, np.ndarray]:
    """The census as the table's columns, the rows by chain and, in a chain, inside out."""
    order: dict[int, list[int]] = {}
    for i, p in enumerate(pieces):
        order.setdefault(p.chain, []).append(i)
    rows: list[tuple[float, ...]] = []
    for chain in sorted(order):
        for place, i in enumerate(sorted(order[chain], key=lambda i: (pieces[i].x, i))):
            p = pieces[i]
            rows.append((float(chain), float(place), math.exp(p.x), p.azimuth % (2.0 * math.pi), p.pitch_deg, p.extent, 1.0 if p.pinned else 0.0))
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
    "a chain started at a uniform azimuth wherever fewer cross - a reading of the law, declared as one, and no "
    "measured statistic; two chains from a bar's ends, where Block et al. 2004 find the arms of barred "
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
            "the model's own stages read the table whole to lay the stars' arms and the gas's answer to them."
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
ARM_PIECES: tuple[FieldDecl, ...] = (
    ARM_PIECE_CHAIN, ARM_PIECE_ORDER, ARM_PIECE_START_RADIUS, ARM_PIECE_START_AZIMUTH, ARM_PIECE_PITCH, ARM_PIECE_EXTENT, ARM_PIECE_PINNED,
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
            "from the bar's ends; every disc gets a chain started at a random azimuth on each ring that fewer "
            "chains cross than the arm-number law counts there; a disc a template states to be flocculent gets "
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
