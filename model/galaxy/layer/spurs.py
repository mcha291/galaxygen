"""gas_spurs: the census of gas spurs (feathers) off the arm chains' gas ridges (checkpoint 4; S62, BUILD_III Phase L2;
DECISIONS.md D221 item 7, as the lead amended it at S62).

The physics publishes the arms' census (the layer's ``arm_piece`` table, composed by ``pieces.py``), the gas's answer
to it (``gas_pattern``) and the ring's gas column (``gas_surface_density``). Where along an arm a spur leaves the
ridge is the outcome of a magneto-Jeans instability in the arm's gas, which the model does not integrate: this stage
lays it - **the realised table** ``gas_spur``, one row a spur - and the ``spurs`` stage composes the spurs into the
gas's contrast (``galaxy/stages/spurs.py``, which also holds a spur's shape).

**Where spurs are** (item 7): only off chains - a grand design's or a multi-armed disc's arms - and none off a
flocculent disc's single pieces. Feathers are seen in 45 of 223 spirals, in 83 % of those whose primary dust lane is
well defined and in none of 52 Scd-Sd galaxies [verified: La Vigne, Vogel & Ostriker 2006, ApJ 650, 818 =
arXiv:astro-ph/0606761, abstract, Table 1 and section 4.3; docs/READING_SPURS.md row 3]: every chain of a
non-flocculent disc carries them here, which is the 83 %'s side of the sample, declared.

**The spacing along a chain** (item 7; the lead's ruling 1): 10 λ_J,sp, λ_J,sp = c_s² / (G Σ_peak), Σ_peak = the
ring's gas column times the gas ridge's contrast at the foot (``SPUR_SPACING_JEANS``; Kim & Ostriker 2006), c_s the
model's one sound speed of the cold gas, ``GAS_DISPERSION`` (6 km/s; La Vigne et al. assumed 7). The spacing is
taken along the chain's polyline in kiloparsecs at each spur's foot: the first foot uniform within one spacing of the
chain's start - the one draw, on ``texture_seed``, stream ``("spur", chain)`` - each next one the local spacing on
from the last. As measured on the Milky Way template (``tests/test_spurs.py``) the law gives 4.9-6.8 kpc at the
Sun's radius: the model's gas crest there is 1.1-1.55 times the ring's mean (#155's shortfall) and the Galaxy's arm
column about 12-17 M☉/pc², not M51's dust lanes' 100-300 - the law's honest answer, a disclosed check, not tuned
(the lead's ruling 1; the choice between Kim & Ostriker's 10 and 2.5 is the owner's).

**What the walk reads at a foot** (the lead's ruling 3, a declared approximation): the gas contrast g on the two grid
rings that bracket the foot's radius, each at the azimuth where the foot's chain crosses that ring (its polyline
followed, ``Pieces.along``), linear in R between them - so the walk solves no ring between the grid's (a point read
off the grid's rings would solve the mid-gap rings, about two seconds on the Milky Way template). Against the gas
pattern's point function at the foot itself it differs by at most :data:`WALK_READ_DIFFERENCE` of the point
function's value over the feet ``tests/test_spurs.py`` samples. The foot's contrast is the spur's height there:
"the foot's peak equal to the ridge's crest contrast there".

**Every count is fixed in advance** (rule A1): a chain holds at most :data:`MAX_SPURS` spurs; past it the stage raises.

**The layer off:** nothing is drawn and the table has no row: the gas carries no spur.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import ARM_CLASSES, IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.gas_pattern import GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS
from galaxy.stages.pattern import ring_bracket
from galaxy.stages.spurs import SPUR_FIELDS

FLOCCULENT = ARM_CLASSES[2]
MAX_SPURS = 4096  # the most spurs one chain holds (rule A1): a 40 kpc chain at 10 pc spacing
# The walk's read of g at a foot against the point function's, relative, the most over the sampled feet
# (``tests/test_spurs.py``, the ten feet across the Milky Way template's disc, as measured at S62).
WALK_READ_DIFFERENCE = 0.052
SPUR_CONSTANTS: tuple[str, ...] = ("SPUR_SPACING_JEANS", "SPUR_PITCH", "SPUR_LENGTH", "SPUR_WIDTH", "SPUR_FALL")
PER_PC2_IN_KPC2 = 1.0e6  # M☉/pc² to M☉/kpc²


def chain_geometry(pieces: Any, chain: float) -> tuple[np.ndarray, np.ndarray]:
    """(the chain's pieces, inside out; each piece's arc length in kpc): a piece of pitch p from R_s through an
    extent Δβ is a logarithmic spiral, ds = dR/|sin p|, so its length is R_s (e^{Δβ |tan p|} − 1)/|sin p| -
    R_s Δβ/|cos p| in the limit of no radial reach, R_s Δβ for an arc of no pitch."""
    members = np.flatnonzero(pieces.chain == chain)
    members = members[np.argsort(pieces.order[members], kind="stable")]
    reach = pieces.x_end[members] - pieces.x_start[members]
    start = pieces.start_radius[members]
    with np.errstate(divide="ignore", invalid="ignore"):
        arc = np.where(reach > 0.0, start * np.expm1(reach) / np.where(reach > 0.0, pieces.sin_abs[members], 1.0), start * pieces.extent[members])
    return members, arc


def point_on(pieces: Any, piece: int, fraction: float) -> tuple[float, float]:
    """(R, φ) at ``fraction`` of piece ``piece``'s arc length from its start: R = R_s (1 + f (e^u − 1)), u the piece's
    reach in ln R, the azimuth linear in ln R along the piece (an arc of no pitch: linear in f)."""
    u = float(pieces.x_end[piece] - pieces.x_start[piece])
    share = math.log1p(fraction * math.expm1(u)) / u if u > 0.0 else fraction
    radius = float(pieces.start_radius[piece]) * math.exp(share * u)
    azimuth = float(pieces.phi_start[piece] + share * (pieces.phi_end[piece] - pieces.phi_start[piece]))
    return radius, azimuth


def lay(
    gas: Any, sigma_gas: np.ndarray, arm_class: str, constants: Mapping[str, Any], stream: Callable[..., np.random.Generator],
) -> list[tuple[float, ...]]:
    """The spurs' rows: (chain, arc, R, φ, spacing, λ_J, Σ_peak, g, pitch, length, width, fall), the rows by chain and
    along it. ``gas`` the run's gas pattern (``compose.gas_pattern``, without spurs), ``sigma_gas`` the ring's gas
    column on its grid (M☉/pc²), ``stream(*path)`` the layer's streams on ``texture_seed``."""
    if gas is None or gas.flat or gas.stars is None or arm_class == FLOCCULENT:
        return []
    pieces = gas.stars.pieces
    if not pieces.count:
        return []
    c = {k: float(constants[k]) for k in (*SPUR_CONSTANTS, "G", "GAS_DISPERSION")}
    jeans_scale = c["GAS_DISPERSION"] ** 2 / (c["G"] * PER_PC2_IN_KPC2)  # kpc · M☉/pc²: λ_J = this / Σ_peak
    R = gas.R
    sigma_gas = np.asarray(sigma_gas, dtype=float)
    shape = (c["SPUR_PITCH"], c["SPUR_LENGTH"], c["SPUR_WIDTH"], c["SPUR_FALL"])

    # The ridge's contrast where each piece's chain crosses each grid ring the piece spans (and the two beyond its
    # ends): one read of the gas pattern on the grid's own rings, no ring between them solved.
    table: dict[int, dict[int, float]] = {}
    pieces_rings: list[tuple[int, np.ndarray]] = []
    for k in range(pieces.count):
        lo = int(ring_bracket(R, np.array([pieces.start_radius[k]]))[0][0])
        hi = int(ring_bracket(R, np.array([math.exp(min(pieces.x_end[k], 700.0))]))[1][0])
        pieces_rings.append((k, np.arange(lo, hi + 1)))
    slots = np.concatenate([np.full(r.size, k, dtype=np.int64) for k, r in pieces_rings])
    rings = np.concatenate([r for _, r in pieces_rings])
    g = gas.unspurred_contrast_at(R[rings], pieces.along(slots, np.log(R[rings])))
    start = 0
    for k, r in pieces_rings:
        table[k] = {int(i): float(v) for i, v in zip(r, g[start:start + r.size])}
        start += r.size

    def ridge(piece: int, radius: float) -> float:
        """g at ``radius`` on piece ``piece``'s chain: the two bracketing grid rings' reads, linear in R."""
        lower, upper, share = ring_bracket(R, np.array([radius]))
        at = table[piece]
        return (1.0 - float(share[0])) * at[int(lower[0])] + float(share[0]) * at[int(upper[0])]

    rows: list[tuple[float, ...]] = []
    for chain in np.unique(pieces.chain):
        members, arc = chain_geometry(pieces, float(chain))
        ends = np.concatenate([[0.0], np.cumsum(arc)])
        total = float(ends[-1])
        if not total > 0.0:
            continue

        def foot(position: float) -> tuple[float, float, float, float, float]:
            """(R, φ, g, Σ_peak, the spacing) at ``position`` kpc along the chain."""
            i = int(min(max(np.searchsorted(ends, position, side="right") - 1, 0), members.size - 1))
            while arc[i] <= 0.0 and i + 1 < members.size:
                i += 1
            fraction = min(max((position - ends[i]) / arc[i], 0.0), 1.0) if arc[i] > 0.0 else 0.0
            radius, phi = point_on(pieces, int(members[i]), fraction)
            contrast = ridge(int(members[i]), radius)
            peak = float(np.interp(radius, R, sigma_gas)) * contrast
            spacing = c["SPUR_SPACING_JEANS"] * jeans_scale / peak if peak > 0.0 else math.inf
            return radius, phi, contrast, peak, spacing

        first = foot(0.0)[4]
        if not math.isfinite(first):
            continue
        position = float(stream("spur", int(chain)).random()) * first
        made = 0
        while position < total:
            radius, phi, contrast, peak, spacing = foot(position)
            if not math.isfinite(spacing):
                break
            made += 1
            if made > MAX_SPURS:
                raise ArithmeticError(f"chain {chain:g} holds more than {MAX_SPURS} spurs (rule A1): its spacing has fallen under {total / MAX_SPURS:g} kpc")
            rows.append((float(chain), position, radius, phi % (2.0 * math.pi), spacing, spacing / c["SPUR_SPACING_JEANS"], peak, contrast, *shape))
            position += spacing
    return rows


def columns(rows: list[tuple[float, ...]]) -> dict[str, np.ndarray]:
    table = np.array(rows, dtype=float).reshape(len(rows), len(SPUR_FIELDS))
    return {name: np.ascontiguousarray(table[:, k]) for k, name in enumerate(SPUR_FIELDS)}


_STANDS_IN_FOR = (
    "Where along a spiral arm the gas breaks into feathers: the outcome of a magneto-Jeans instability of the gas "
    "compressed in the arm, growing over one or two orbits, which the model does not integrate."
)
_CONSERVES = (
    "Every ring's gas and every law: the spurs' excess is taken from the whole ring in proportion to its gas, so "
    "the composed gas contrast averages to 1 on every ring exactly, and no radial field, no scalar and no expected "
    "count of any census moves - the clouds' and the clusters' sector shares on a ring do. It does not keep the "
    "interarm gas's share of a ring, which falls by the spurs' mean there."
)
_STATISTIC = (
    "One uniform draw per chain, where the first spur stands within one spacing of the chain's start - no source "
    "gives the phase, and none contradicts a random one (docs/READING_SPURS.md, Recommendation 1). Everything "
    "else is a law: the spacing 10 local Jeans lengths of the ridge's peak [verified: Kim & Ostriker 2006, "
    "arXiv:astro-ph/0603751, abstract and section 6; La Vigne, Vogel & Ostriker 2006, arXiv:astro-ph/0606761, "
    "section 4.7: 10.4 in M51]; the pitch 63 degrees from the circle [verified: Elmegreen 1980, ApJ 242, 528, Table "
    "1]; the length 240 pc and the width 60 pc [verified: Schinnerer et al. 2017, arXiv:1701.02184, section 3.1.1]; "
    "the fall of 7 [verified: La Vigne et al. 2006, section 4.6: a factor 5-10]; spurs off chains only, none off a "
    "flocculent disc [verified: La Vigne et al. 2006, section 4.3: 0 of 52 Scd-Sd]. (DECISIONS.md D221 item 7.)"
)


def _column(name: str, label: str, unit: str, about: str) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.TABLE_COLUMN, of="gas_spur",
        meaningful_zero=True, provenance="synthetic",
        about=about + (
            " One row a gas spur of the realised census, the rows by chain and along each chain. No row with the "
            "randomness layer off, or in a flocculent disc. A column of a small table, not of a catalogue: the "
            "model's own stages read the table whole to compose the spurs into the gas's contrast, and it is not "
            "shown by the viewer, which draws the gas it places."
        ),
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC,
    )


GAS_SPUR_COLUMNS: tuple[FieldDecl, ...] = (
    _column("gas_spur_chain", "Chain a gas spur leaves", "count", "The number of the arm chain whose gas ridge the spur leaves, as the arm pieces' table numbers it."),
    _column("gas_spur_arc", "Spur's foot along its chain", "kpc", "How far along its chain's polyline, from the chain's inner end, the spur's foot stands."),
    _column("gas_spur_radius", "Radius of a spur's foot", "kpc", "The radius at which the spur leaves its chain's gas ridge."),
    _column("gas_spur_azimuth", "Azimuth of a spur's foot", "rad", "Where round the disc the spur leaves its chain's gas ridge, within one turn."),
    _column("gas_spur_spacing", "Spacing to the next spur", "kpc", "Ten local Jeans lengths of the ridge's peak at the foot: how far along the chain the next spur stands."),
    _column("gas_spur_jeans_length", "Jeans length at a spur's foot", "kpc", "The square of the cold gas's sound speed over the gravitational constant times the ridge's peak column at the foot."),
    _column("gas_spur_peak_surface_density", "Ridge's peak column at a spur's foot", "Msun/pc2",
            "The ring's gas column times the gas ridge's contrast at the foot, read on the two grid rings either side of it."),
    _column("gas_spur_contrast", "Ridge's contrast at a spur's foot", "dimensionless",
            "The gas contrast of the ridge at the foot, and so the spur's height there: it leaves the ridge as dense as the ridge."),
    _column("gas_spur_pitch", "Pitch of a gas spur", "deg", "The angle the spur makes with the circle at its foot, trailing, on the ridge's outer side."),
    _column("gas_spur_length", "Length of a gas spur", "kpc", "How far the spur runs from the ridge."),
    _column("gas_spur_width", "Width of a gas spur", "kpc", "The spur's full width at half maximum across itself."),
    _column("gas_spur_fall", "Fall of a spur's contrast", "dimensionless", "By what factor the spur's contrast falls from its foot to its tip."),
)
assert tuple(d.name for d in GAS_SPUR_COLUMNS) == SPUR_FIELDS


def compute_gas_spurs(ctx: Context) -> Mapping[str, Any]:
    def draw() -> dict[str, np.ndarray]:
        gas = _compose.gas_pattern(ctx.fields, ctx.grid.R, ctx.constants)
        rows = lay(gas, ctx.fields["gas_surface_density"], str(ctx.fields["arm_class"]), ctx.constants,
                   lambda *path: ctx.rng("texture_seed", *path))
        return columns(rows)

    # compose decides: the draw, or - with the layer off - no row at all, the stream untouched.
    return _compose.realise(ctx.fields, draw, lambda: columns([]))


GAS_SPURS = IMPLEMENTATIONS.register(
    Stage(
        id="gas_spurs", slot="gas_spurs", checkpoint=4,
        about=(
            "The randomness layer's census of gas spurs: along every arm chain of a disc that is not flocculent, "
            "feathers leave the gas ridge every ten local Jeans lengths of the ridge's peak column, the first at a "
            "drawn place within one spacing of the chain's start. Synthetic: it stands in for the instability "
            "that breaks the arm's gas into feathers, moves no ring's gas and no law, and lays nothing with the "
            "layer off. It runs after the star formation history, whose gas column the spacing reads."
        ),
        compute=compute_gas_spurs,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_constants=(*GAS_PATTERN_CONSTANTS, *SPUR_CONSTANTS),
        requires=(*GAS_PATTERN_READS, "gas_surface_density", "arm_class"),
        publishes=GAS_SPUR_COLUMNS,
    )
)
