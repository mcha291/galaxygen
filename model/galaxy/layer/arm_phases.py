"""arm_phases: where each arm mode's crests lie (checkpoint 3, S56, BUILD_III Phase P1; DECISIONS.md D215).

The ``pattern`` stage publishes a law: at every radius, how much of the arms' power each arm number m = 2 … 6
carries (the swing amplifier's weight at the local X and shear). It does not say where the crests of each mode
are - that is the phase a swing-amplified mode happens to have, the outcome of self-gravitating dynamics the model
does not integrate. This stage draws it: **five synthetic scalars** ``arm_mode_phase_2 … _6``, each uniform on
[0, 2π), entering the composed field as cos(m(φ − ln R · cot i) − θ_m). θ = 0 for every mode is the fixed
convention the model had until S56 (one cosine, its crest on the winding's own phase), which is retired: this is a
new draw, not a moved one (gate G1, D214).

- **The seed** is ``texture_seed``, and this is its first reader (D214 section 3): rerolling it moves the arms and
  everything placed by them, and no law - no radial field, no scalar of the pattern, no expected count.
- **The stream** names the mode, ``("phase", m)``, so adding a mode later moves no other mode's phase.
- **The layer off.** The phases are not realised and are NaN (D164: an unrealised quantity is NaN; 0 would claim
  a draw that was not made), and the stream is never drawn: ``compose`` does not call the draw.
- **One pitch for all modes** until P4: the modes are parallel logarithmic spirals that beat in azimuth.
- **The two-armed mode in a barred galaxy is tied to the bar** (S58, BUILD_III Phase P3; D217 item 9): θ₂ = 0,
  the m = 2 crest on the bar's axis at the bar's end - the convention the model had before S56, restored for
  this one mode where there is a bar. It is not drawn there (Block et al. 2004's ±20° between the arms' start
  and the bar's axis is a detection window, not a scatter: no draw). The three-armed mode and above, and the
  two-armed mode of an unbarred galaxy, stay uniform draws on the streams and at the values they had; no
  bar-driven arm amplitude is built. The stage reads the derived ``bar_present`` for this and nothing else.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.pattern import ARM_MODES, BAR_PRESENT, PHASE_FIELDS, SEGMENTS_INWARD, SEGMENTS_OUTWARD, phase_field

BAR_TIED_MODE = 2  # the arm number whose phase a bar fixes (D217 item 9: "#139 re-ruled for m = 2 only")
BAR_TIED_PHASE = 0.0  # θ₂ in a barred galaxy: the two-armed crest on the bar's axis at the bar's end

_STANDS_IN_FOR = (
    "Where the crests of this swing-amplified mode lie around the disc: the phase the mode has when it is seen, "
    "which is the outcome of the self-gravitating stellar dynamics that amplify it - a disc stepped through "
    "time - and the model does not integrate that."
)
_CONSERVES = (
    "Every ring's mean and every amplitude: the phase moves a cosine round its ring, whose mean over the ring is "
    "0 for any phase, so the composed density contrast averages to 1 on every ring exactly as it does at phase 0, "
    "and the mode's amplitude - the law's - is untouched. It changes no radial field, no scalar and no expected "
    "count of any census; it changes which sector of a ring holds the crest, and so where the censuses' objects "
    "are (their realised totals are another draw until L1, as for every placement)."
)
_STATISTIC = (
    "Uniform on the circle, each mode's phase drawn independently of the others'. Not a measured distribution: "
    "the absence of a measured preference, stated as such. The disc the modes grow in is axisymmetric, so the "
    "law has no preferred azimuth and a mode in a differentially rotating disc has no preferred phase; nothing "
    "read gives the modes' phases a correlation with one another, and none is put in [inferred]."
)


_TIED = (
    " **In a barred galaxy this mode is not drawn**: its phase is 0, the two-armed crest on the bar's axis at the "
    "bar's end, so the two-armed arms start from the bar's ends and rerolling the texture seed does not turn "
    "them; in an unbarred galaxy it is the uniform draw the other modes are."
)
_TIED_STATISTIC = (
    " The two-armed mode of a barred galaxy is the exception, and is not drawn: 'for all but two of the "
    "galaxies, the spirals appear to begin within 20° of the bar axis' (twelve barred galaxies, by eye, "
    "unsigned) - a detection window, not a measured scatter, so the phase is set on the axis and no residual is "
    "drawn about it [verified: Block et al. 2004, AJ 128, 183, arXiv:astro-ph/0405227, Table 3, "
    "https://ar5iv.labs.arxiv.org/html/astro-ph/0405227] (docs/READING_BAR.md B1.3 and B2, B04; DECISIONS.md "
    "D217 item 9)."
)


def _phase(m: int) -> FieldDecl:
    tied = m == BAR_TIED_MODE
    return FieldDecl(
        name=phase_field(m), label=f"Phase of the {m}-armed mode", unit="rad", kind=Kind.SCALAR,
        meaningful_zero=True, provenance="synthetic",
        about=(
            f"θ in cos({m}(φ − ln R / tan p) − θ): where round the disc the {m}-armed mode's crests lie. Drawn "
            "uniformly on the circle on the texture seed, one stream per mode, so rerolling that seed turns each "
            "mode by its own angle and the arms meet, part and branch somewhere else - and no amplitude, no "
            "profile and no count changes. At 0 for every mode the crests sit on the winding's own phase, the "
            "convention the model had until S56. Not a number with the randomness layer off: nothing is realised "
            "then, and the density contrast is 1 everywhere." + (_TIED if tied else "")
        ),
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC + (_TIED_STATISTIC if tied else ""),
    )


ARM_MODE_PHASES: tuple[FieldDecl, ...] = tuple(_phase(m) for m in ARM_MODES)


# --- the winding's segments (S59, BUILD_III Phase P4; DECISIONS.md D218 items 1-2) -------------------------------
#
# The arms' common winding is cut into radial segments, each with its own pitch. What is drawn here is the
# realisation and nothing of the law: for each segment an azimuthal extent Δβ and a pitch residual δ. The law -
# the disc's pitch p, which the ``pattern`` stage draws after this stage runs, and the anchor - is applied to
# these rows by ``pattern.Winding``, which every reader builds from the published numbers: p_seg = p + δ, the
# segment spans d ln R = Δβ |tan p_seg| and the phase advances Δβ sign(p_seg) across it. So rerolling the
# texture seed re-lays the segments and moves no pitch, and pinning a pitch re-lays nothing.
#
# - **The rows.** :data:`~galaxy.stages.pattern.SEGMENTS_OUTWARD` rows outward from the anchor, in order, then
#   :data:`~galaxy.stages.pattern.SEGMENTS_INWARD` inward, in order. Fixed counts (rule A1): about six outward
#   and thirty inward are ever reached (a segment spans about a quarter of an e-fold in radius), and a winding
#   asked past the last row raises.
# - **The streams.** ``("segment", "out", j)`` and ``("segment", "in", j)``, j = 0 at the anchor: a segment's
#   draw is its own stream's and no other's, so it does not depend on how many are laid, on the grid, or on
#   the region asked for.
# - **The draw, on one stream, in this order:** δ first - one normal - then the extent, log-normal about the
#   median, **drawn again while outside the sample's range** (about one draw in six hundred), at most
#   :data:`MAX_EXTENT_DRAWS` times; exhausted, the stage raises - it does not clip the last draw (the chance is
#   1e-45 a segment). The residual is not truncated: reversed and nearly flat segments are measured.
# - **The layer off:** no segment is drawn and the columns are empty; the winding is ln R · cot p.

MAX_EXTENT_DRAWS = 16  # the redraw's fixed count (rule A1); exhausted, the stage raises


def draw_segment(generator: Any, median_deg: float, log_scatter: float, lo_deg: float, hi_deg: float, scatter_deg: float) -> tuple[float, float, int]:
    """(Δβ in radians, δ in degrees, how many extents were drawn) for one segment, on its own stream."""
    residual = float(generator.normal(0.0, scatter_deg))
    for attempt in range(1, MAX_EXTENT_DRAWS + 1):
        extent = median_deg * math.exp(log_scatter * float(generator.normal()))
        if lo_deg <= extent <= hi_deg:
            return math.radians(extent), residual, attempt
    raise ArithmeticError(f"a segment's extent fell outside {lo_deg:g}-{hi_deg:g} degrees {MAX_EXTENT_DRAWS} times running")


_SEGMENT_STANDS_IN_FOR = (
    "The kinks of real spiral arms: an arm is a chain of stretches a few kiloparsecs long, each close to a "
    "logarithmic spiral of its own pitch, joined where the pitch changes - the outcome of how swing-amplified "
    "pieces form and link up, which the model does not integrate. Each arm kinks at its own places; here the "
    "kinks fall on common rings for every arm and every mode, which no source describes: declared, and a debt."
)
_SEGMENT_CONSERVES = (
    "Every ring's mean and every mode's amplitude: the winding is one phase per ring, shared by all the modes, "
    "and shifting a ring's cosines round the ring changes neither their mean, which is 0, nor their amplitudes, "
    "which are the law's. It changes no radial field, no scalar and no expected count; the gas's answer on a "
    "ring is the same curve, turned. It does not enter the gas law's strength, the bar's angle or the side the "
    "bar's lanes lie on."
)
_SEGMENT_STATISTIC = (
    "Azimuthal extent log-normal, median 60 degrees and log-width 0.35, drawn again outside 20-180 degrees; "
    "pitch residual normal, 10 degrees, independent from segment to segment and untruncated. The extent's "
    "numbers are the reader's arithmetic on the 38 printed rows of one survey of four galaxies (median 60, "
    "quartiles 50-80, range 20-180), not statistics the paper prints; the residual's width sits between that "
    "sample's pooled 9.9 degrees and a 391-galaxy survey's 9.5 +/- 0.3 within a galaxy [verified: Honig & Reid "
    "2015, ApJ 800, 53 = arXiv:1412.1012, Tables 2-5; Diaz-Garcia et al. 2019, A&A 631, A94 = arXiv:1908.04246; "
    "docs/READING_ARM_SEGMENTS.md A1.1; DECISIONS.md D218 item 2]. No correlation between neighbours and no "
    "arm-to-arm term: none is measured for a common winding [inferred]."
)


# D191's ruling for the two columns, which the viewer does not read (tests/test_v4.py holds the inventory and
# asserts the sentence): a segment is drawn through the winding it sets.
NOT_DRAWN_WHY: dict[str, str] = {
    "arm_segment_extent": "it reaches the picture as the winding it sets - with the segment's pitch, where round "
                          "each ring the arms' crests lie - and the viewer draws the arms, the gas and everything "
                          "placed by them; a row of the table is not a look.",
    "arm_segment_pitch_residual": "it reaches the picture as the winding it sets, as the extent does: across the "
                                  "segment the arms turn at its own pitch.",
}


def _segment(name: str, label: str, unit: str, about: str) -> FieldDecl:
    why = NOT_DRAWN_WHY.get(name)
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.COLUMN, of="arm_segment", ramp=Ramp("viridis"),
        meaningful_zero=True, provenance="synthetic",
        about=about + (
            " One row a segment of the arms' common winding: the first rows run outward from the radius the "
            "winding is anchored at, in order, and the rest inward, in order - far more rows than a disc "
            "reaches, each on its own stream of the texture seed, so a row is the same whatever the grid and "
            "however many are used. Empty with the randomness layer off: no segment is laid, and the arms wind "
            "at the disc's one pitch."
        ) + (f" **Not drawn by the viewer** (D191): {why}" if why else ""),
        stands_in_for=_SEGMENT_STANDS_IN_FOR, conserves=_SEGMENT_CONSERVES, statistic=_SEGMENT_STATISTIC,
    )


ARM_SEGMENT_EXTENT = _segment(
    "arm_segment_extent", "Azimuthal extent of a winding segment", "rad",
    "How far round the disc one segment of the winding runs before the pitch changes. With the segment's "
    "pitch it gives the segment's radial span - the extent times the tangent of the pitch, in the logarithm "
    "of the radius - so a segment of nearly no pitch is a short radial step that still carries the arms "
    "round by its whole extent.",
)
ARM_SEGMENT_RESIDUAL = _segment(
    "arm_segment_pitch_residual", "Pitch residual of a winding segment", "deg",
    "What is added to the disc's pitch to give this segment's own. About a tenth of segments come out "
    "reversed - leading, the arms turning back - and about as many nearly circular, as measured arms do; "
    "nothing is floored.",
)
ARM_SEGMENTS: tuple[FieldDecl, ...] = (ARM_SEGMENT_EXTENT, ARM_SEGMENT_RESIDUAL)
SEGMENT_CONSTANTS: tuple[str, ...] = (
    "ARM_SEGMENT_EXTENT_MEDIAN", "ARM_SEGMENT_EXTENT_LOG_SCATTER", "ARM_SEGMENT_EXTENT_MIN", "ARM_SEGMENT_EXTENT_MAX",
    "ARM_SEGMENT_PITCH_SCATTER",
)


def segment_streams() -> tuple[tuple[str, int], ...]:
    """The rows' streams, in the rows' order: outward from the anchor, then inward."""
    return tuple(("out", j) for j in range(SEGMENTS_OUTWARD)) + tuple(("in", j) for j in range(SEGMENTS_INWARD))


def compute_arm_phases(ctx: Context) -> Mapping[str, Any]:
    return {**_phases(ctx), **_segments(ctx)}


def _segments(ctx: Context) -> Mapping[str, Any]:
    numbers = tuple(float(ctx.constants[k]) for k in SEGMENT_CONSTANTS)

    def draw() -> dict[str, np.ndarray]:
        rows = [draw_segment(ctx.rng("texture_seed", "segment", way, j), *numbers) for way, j in segment_streams()]
        return {"arm_segment_extent": np.array([r[0] for r in rows]), "arm_segment_pitch_residual": np.array([r[1] for r in rows])}

    # compose decides: the draw, or - with the layer off - no rows at all, the streams untouched.
    return _compose.realise(ctx.fields, draw, lambda: {d.name: np.zeros(0) for d in ARM_SEGMENTS})


def _phases(ctx: Context) -> Mapping[str, Any]:
    barred = ctx.fields["bar_present"] == BAR_PRESENT[1]

    def draw() -> dict[str, float]:
        # One stream per mode, named by the mode: uniform on [0, 2 pi). In a barred galaxy the two-armed mode's
        # stream is not drawn and its phase is the bar's (S58, D217 item 9); every other stream is the one it was.
        return {
            phase_field(m): BAR_TIED_PHASE if barred and m == BAR_TIED_MODE
            else 2.0 * math.pi * float(ctx.rng("texture_seed", "phase", int(m)).random())
            for m in ARM_MODES
        }

    # compose decides: the draw, or - with the layer off - NaN for each, the stream untouched.
    return _compose.realise_scalars(ctx.fields, PHASE_FIELDS, draw)


ARM_PHASES = IMPLEMENTATIONS.register(
    Stage(
        id="arm_phases", slot="arm_phases", checkpoint=3,
        about=(
            "The randomness layer's realisation of the arms: the phase of each of the five arm modes, drawn on "
            "the texture seed. Synthetic: it stands in for the stellar dynamics that set where a swing-amplified "
            "mode's crests lie, moves no amplitude and no ring's mean, and is not a number with the layer off. In "
            "a barred galaxy the two-armed mode is not drawn: its crest is put on the bar's axis at the bar's end. "
            "Since S59 it also lays the segments of the arms' common winding - for each a run round the disc and "
            "a residual about the disc's pitch - standing in for the kinks of real arms; they change where the "
            "arms bend and no amplitude, no ring's mean and nothing the gas law or the bar reads."
        ),
        compute=compute_arm_phases,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_constants=SEGMENT_CONSTANTS,
        requires=("bar_present",),  # S58 (D217 item 9): whether there is a bar for the two-armed mode to be tied to
        publishes=(*ARM_MODE_PHASES, *ARM_SEGMENTS),
    )
)
