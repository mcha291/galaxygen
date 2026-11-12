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
non-flocculent disc long enough for a first foot carries them here, which is the 83 %'s side of the sample, declared
- a chain shorter than its first foot's draw (one uniform within one spacing of its start, 5-7 kpc at the Sun)
carries none: S70 (D234; Audit V F-2-5) was "every chain of a non-flocculent disc carries them", and Audit V's mesh
found a 2.3 kpc chain of the Milky Way template at seed 4242 with none.

**The spacing along a chain** (item 7; the lead's ruling 1): 10 λ_J,sp, λ_J,sp = c_s² / (G Σ_peak), Σ_peak = the
ring's gas column times the gas ridge's contrast at the foot (``SPUR_SPACING_JEANS``; Kim & Ostriker 2006), c_s the
model's one sound speed of the cold gas, ``GAS_DISPERSION`` (6 km/s; La Vigne et al. assumed 7). The spacing is
taken along the chain's polyline in kiloparsecs at each spur's foot: the first foot uniform within one spacing of the
chain's start - the one draw, on ``texture_seed``, stream ``("spur", chain)`` - each next one the local spacing on
from the last. As measured on the Milky Way template (``tests/test_spurs.py``) the law gives 4.9-6.8 kpc at the
Sun's radius: the model's gas crest there is 1.1-1.55 times the ring's mean (#155's shortfall) and the Galaxy's arm
column about 12-17 M☉/pc², not M51's dust lanes' 100-300 - the law's honest answer, a disclosed check, not tuned
(the lead's ruling 1; the choice between Kim & Ostriker's 10 and 2.5 is the owner's).

**What the walk reads at a foot** (S99, #220; the gate's ruling, the closer's second form): the gas pattern's point
function on the foot's own ring - that ring at the foot's radius read whole on the solver's cell centres
(``foot_reads``), the crest and the trough below taken from it. It is therefore the point function's read by
construction, and :data:`WALK_READ_DIFFERENCE` holds with nothing to spare: the walk's crest against the point
function's at every foot reads 0 exactly (the Milky Way template at texture seeds 0 and 4242, 44 and 42 feet, and four
of S95's population pairs that read over the bound before: 0.3667, 0.4863, 0.6656, 0.4002 -> 0). The cost is one ring
solved at each foot's radius, about two seconds a lay on the Milky Way template (S90 measured +1.9-2.2 s; S99 the run
3.5-5.1 -> 5.3-7.7 s). Was, from S62 to S99 (the lead's ruling 3, a declared approximation): g read on the two grid
rings that bracket the foot's radius, each at the azimuth where the foot's chain crosses that ring (its polyline
followed, ``Pieces.along``), linear in R between them, so that the walk solved no ring between the grid's; against the
point function at the foot it differed by up to 0.27 (S70, D234; S88's 0.2506). Until S92 the foot's contrast was the
spur's height there: "the foot's peak equal to the ridge's crest contrast there".

**Since S92 (#164 / #165; the owner's ruling of 2026-11-10, "accept all recommendations" - S90's option 4):** the foot
stays on the chain; the walk reads the gas crest - the largest of g over the ring's profile cells (``ring_profiles``:
the solver's 1440 cell centres) within half the ring's crest width of the foot each side, the width
``gas_pattern.crest_width``'s (the full width at half maximum of the ring's tallest crest, the half level midway
between the ring's trough and that crest), the foot's own read among them - and the ring's trough, that profile's
least value (``crest_width``'s floor). Since S99 both on the foot's own ring (above); S92 to S99 on each of the two
bracketing grid rings, linear in R between them. **The spur's
height is the crest's excess over the trough** (``gas_spur_contrast``), so the composed contrast at a foot is about
2 crest - trough where it was twice the crest (#164: the composed over the unspurred contrast at the feet, median
1.9975 / 1.9974 at texture seeds 0 / 4242 before, 1.5312 / 1.5175 after; over the crest, at most 1.7573 / 1.8251);
**the ridge's peak column is the crest's** (#165: Σ_peak = the ring's column times the crest), so the spacing reads
the ridge, not the stellar chain. From S92 to S99 the walk's crest against the point function's crest within the same
window at the foot's own radius read at most 0.2176 (seed 0, 45 feet) and 0.4582 (seed 4242, 43 feet), over the
bound (#220): between two grid rings the crest the window held could be another ridge's (the worst feet at 4.44-4.45
kpc, inside the pinned bar); read at the foot since S99, 0.

**The walk reads the gas at the stellar chain's polyline, not at the gas crest** (S62's review, finding 4; measured on
the Milky Way template's 48 spurs, unchanged here - the lead opens the debt): the gas ridge stands near the stellar
crest but not on it, so the contrast the table carries is the gas's *at the chain*, which the column says. Of the 28
feet whose contrast is above 1.05, the foot's contrast over the local gas crest (its largest within 0.5 kpc of arc
round the ring) has median 0.987 and minimum 0.323, the crest up to 500 pc from the foot (median 36 pc); 6 feet read
1-1.05, 11 exactly 1.0 (on chains past the arm power, where the gas pattern is flat: Sigma_peak is the ring's own
column) and 3 below 1 - spurs 2, 12 and 44 (chains 1, 3 and 11 at R 4.20, 10.33 and 10.51 kpc) at 0.933, 0.799 and
0.821: feet in a gas trough. (D221's "9 of them on chains past the arm power" counted the 11 and the 3 short.)

**Where a chain's spurs end** (S90, #213; the gate's ruling at S88's close, D256: "a spur does not belong where no
ridge stands"): at the arms' budget's edge, the last grid ring where the pieces carry any amplitude
(``arm_piece_amplitude`` > 0; 12.34 kpc on the Milky Way template). Until S90 the walk ran each chain to its end, and
13 of the Milky Way template's 53 feet stood past the edge (12.43-24.87 kpc) at a contrast of exactly 1: they bent
the gas there (the sector means at 25 kpc 4.4e-3 off 1). The other choice the entry named - a spur's height the
ridge's excess over 1 - was measured beside it and not taken: it meets the sector means too (every foot past the
edge reads 1.0 exactly) but changes the height of all 40 spurs inside the budget, needs a rule for the 6 feet in a
trough (g < 1, a negative height), keeps zero-height rows, and changes D221 item 7's law; ending the walk leaves the
40 rows inside bit for bit (the composed gas moves within a spur's reach of the removed feet).

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
from galaxy.stages.gas_pattern import CELLS, GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS, crest_width
from galaxy.stages.spurs import SPUR_FIELDS

FLOCCULENT = ARM_CLASSES[2]
MAX_SPURS = 4096  # the most spurs one chain holds (rule A1): a 40 kpc chain at 10 pc spacing
# The walk's read of g at a foot against the point function's, relative: the most over EVERY foot (D117: measured
# over N). S70 (D234; Audit V F-2-4): was 0.052, the most over ten sampled feet (``tests/test_spurs.py``, S62) - over
# every foot the production grid reads 0.2698 (the Milky Way template at texture seed 4242, 44 feet, 6 over 0.052;
# 0.0516 over 48 at its own seed 0) and Audit V's coarser mesh (130 rings) 0.4804 (seed 4242, 49 feet; 0.2553 over 40
# at 777). The bound on the model's grid, and the coarser mesh's beside it (tests/test_audit_v.py holds both).
# S88 (D255 ruling 4): re-measured over the same feet on M1's final model - the production grid 0.2506 (seed 4242, 45
# feet, 3 over 0.052; 0.0573 over 53 at seed 0), under 0.27, which stands; Audit V's mesh 0.5700 (seed 4242, 45
# feet, at 5.95 kpc; 0.2596 over 47 at 777), over S70's 0.49. The cause, by M1's model states on the same seeds:
# #148's clock moved the mesh's worst foot 0.4804 -> 0.5680 (the spurs' spacing reads the gas column the clock
# moved, so the feet stand elsewhere), #209's floor to 0.5687, #80's pinned bar to 0.5700; the worst feet stand at
# 5.9-6.1 kpc, just past the bar's end, where the mesh's rings are 0.23 kpc apart. Was 0.49.
# S99 (#220): the walk reads the crest by the point function at the foot (``foot_reads``), so both bounds hold by
# construction (0 at every foot measured); neither is moved (B5).
WALK_READ_DIFFERENCE = 0.27
WALK_READ_DIFFERENCE_COARSE = 0.58
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


def ring_profiles(gas: Any, radii: np.ndarray) -> np.ndarray:
    """g (without spurs) on the solver's cell centres of each ring of ``radii``: shaped (radii, CELLS), the cells'
    centres at the galaxy's azimuth -pi + (k + 1/2) 2 pi / CELLS (the profiles' own, ``GasPattern.profiles``)."""
    centres = -math.pi + (np.arange(CELLS) + 0.5) * (2.0 * math.pi / CELLS)
    radii = np.asarray(radii, dtype=float)
    return gas.unspurred_contrast_at(radii[:, None], centres[None, :])


def foot_reads(gas: Any, radius: float, phi: float) -> tuple[float, float]:
    """(the gas crest, the ring's trough) at a foot (``radius``, ``phi``), by the gas pattern's point function on the
    foot's own ring (S99, #220; was ``ridge_reads``, the two bracketing grid rings' reads linear in R - S92, #164 /
    #165): the ring at ``radius`` read whole on the solver's cell centres (``ring_profiles``); the trough its least
    value (``crest_width``'s floor), the crest the largest of g over its cells whose centres lie within half its crest
    width of ``phi``, and g at the foot itself. A flat ring (no crest: the width NaN) reads the foot's g as its
    crest."""
    centres = -math.pi + (np.arange(CELLS) + 0.5) * (2.0 * math.pi / CELLS)
    profile = ring_profiles(gas, np.array([radius]))[0]
    crest = float(gas.unspurred_contrast_at(np.array([radius]), np.array([phi]))[0])
    width = crest_width(profile)
    if math.isfinite(width):
        near = np.abs(np.mod(centres - phi + math.pi, 2.0 * math.pi) - math.pi) <= 0.5 * width
        if near.any():
            crest = max(crest, float(profile[near].max()))
    return crest, float(profile.min())


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

    # S99 (#220; the gate's ruling, the closer's second form): the ridge is read at each foot by the gas pattern's
    # point function on the foot's own ring (``foot_reads``) - its trough, the floor of ``gas_pattern.crest_width``
    # (the repository's one rule for a ridge), and the gas crest, the largest of g within half that ring's crest width
    # of the foot (the foot's own g among them). Was (S92, #164 / #165): each grid ring the pieces span read whole once
    # and, where the chain crosses it, its window's crest and its trough; at a foot the two bracketing rings' reads
    # linear in R - the crest the window held on a grid ring could be another ridge's, and the linear read between two
    # rings missed the foot's own crest by up to 0.4582 at texture seed 4242 (#220). The cost: one ring solved at each
    # foot's radius (S90 measured +1.9-2.2 s a lay).

    # S90 (#213; the gate's ruling at S88's close, D256: a spur does not belong where no ridge stands): the walk ends
    # at the arms' budget's edge - the last grid ring where the pieces carry any amplitude. Past it the gas ridge is
    # flat (the contrast exactly 1 at every foot S88 found there) and a chain runs on with no amplitude, so a spur
    # there would be composed whole where its cause is absent.
    carried = np.flatnonzero(gas.stars.amplitude_at(R) > 0.0)
    if not carried.size:
        return []
    edge = float(R[carried[-1]])

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
            # S92 (#164): the spur's height is the crest's excess over the ring's trough, so the foot's sum is about
            # 2 crest - trough, not twice the crest; (#165) the ridge's peak column is the crest's. Was: g at the
            # chain, both the height and the peak's contrast. S99 (#220): both read at the foot itself (``foot_reads``);
            # was the two bracketing grid rings' reads, linear in R.
            top, floor = foot_reads(gas, radius, phi % (2.0 * math.pi))
            contrast = max(top - floor, 0.0)
            peak = float(np.interp(radius, R, sigma_gas)) * top
            spacing = c["SPUR_SPACING_JEANS"] * jeans_scale / peak if peak > 0.0 else math.inf
            return radius, phi, contrast, peak, spacing

        first = foot(0.0)[4]
        if not math.isfinite(first):
            continue
        position = float(stream("spur", int(chain)).random()) * first
        made = 0
        while position < total:
            radius, phi, contrast, peak, spacing = foot(position)
            if radius > edge or not math.isfinite(spacing):  # S90 (#213): past the budget's edge the chain carries none
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
    "the composed gas contrast averages to 1 on every ring (to 2e-13: measured at most 9.97e-14 over every ring on "
    "the production grid, both templates at four texture seeds, and 1.006e-13 on Audit V's mesh on NGC 4414, which "
    "carries no spur - the gas pattern's own rounding; S70, D234, was 'to 1e-13', Audit V F-2-3), and no radial "
    "field, no scalar and no "
    "expected count of any census moves - to 4.4e-16 (last-bit differences in 4-13 cells of hot_phase_porosity and "
    "three HII surface brightnesses on milky_way, the moved census summed in another order) - the clouds' and the "
    "clusters' sector shares on a ring do. It does not keep the interarm gas's share of a ring, which falls by the "
    "spurs' mean there: <S> at most 0.0139 of a ring (S92, #164 / #165, the Milky Way template at texture seed 0; was "
    "0.0092). Since S92 the walk reads the gas crest near each foot - the largest contrast within half the ring's crest "
    "width of the foot - and the ring's trough; since S99 on the foot's own ring by the gas pattern's point function, "
    "so the crest is the point function's to the bit (0 at every foot of the Milky Way template at texture seeds 0 and "
    "4242 and of four seed pairs of S95's population that read 0.37-0.67 before). S92 to S99 it read them on the two "
    "grid rings either side, linear in R: 0.2176 over the 45 feet at seed 0 and 0.4582 over the 43 at seed 4242, over "
    "the bound 0.27 (#220). Until S92 it read g at the chain's polyline: "
    "within 0.27 of the point function's value there, relative - measured "
    "at S88 over every foot on the production grid (98 feet of the Milky Way template at texture seeds 0 and 4242: "
    "at most 0.2506, 4 over 0.052, the median 2e-5; S70: 92 feet, at most 0.2698), and within 0.58 on Audit V's "
    "coarser mesh (0.5700 at seed 4242, 0.2596 at 777; S70: 0.4804, under 0.49 - the model's own clock moved the "
    "feet, #148; S70, D234: was 'within 0.052 ... measured on the Milky Way template's feet', ten of them; Audit V "
    "F-2-4)."
)
_STATISTIC = (
    "One uniform draw per chain, where the first spur stands within one spacing of the chain's start - no source "
    "gives the phase, and none contradicts a random one (docs/READING_SPURS.md, Recommendation 1). Everything "
    "else is a law: the spacing 10 local Jeans lengths of the ridge's peak [verified: Kim & Ostriker 2006, "
    "arXiv:astro-ph/0603751, abstract and section 5.1 item 1 (no section 6; corrected at Audit V, S70); La Vigne, "
    "Vogel & Ostriker 2006, arXiv:astro-ph/0606761, "
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
            "The ring's gas column times the gas crest at the foot: the largest gas contrast within half the ring's crest "
            "width of the foot, read on the ring at the foot's own radius."),
    _column("gas_spur_contrast", "Height of a spur at its foot", "dimensionless",
            "The spur's height where it leaves its chain: the gas crest's excess over the ring's trough there (the crest the "
            "largest gas contrast within half the ring's crest width of the foot, the trough the ring's least), read on "
            "the ring at the foot's own radius."),
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
