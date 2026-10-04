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

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.pattern import ARM_MODES, BAR_PRESENT, PHASE_FIELDS, phase_field

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


def compute_arm_phases(ctx: Context) -> Mapping[str, Any]:
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
            "a barred galaxy the two-armed mode is not drawn: its crest is put on the bar's axis at the bar's end."
        ),
        compute=compute_arm_phases,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        requires=("bar_present",),  # S58 (D217 item 9): whether there is a bar for the two-armed mode to be tied to
        publishes=ARM_MODE_PHASES,
    )
)
