"""The separation (S55, BUILD_III Phase R; DECISIONS.md D214): the physics model beside the randomness layer.

Phase R is a behaviour-preserving restructure. What this file holds, in the order BUILD_III section 1d states it:

- **The reference.** With the layer off, every field of both models at both templates' inputs on the production
  grid, and every array of every input route's body, is bit-identical to S55's layer-off run, captured before any of
  Phase P1's model code moved (``tests/layer_reference.py``, ``tests/layer_reference_s55.json``) - but for a closed,
  named list (``LAYER_OFF_EXCEPTIONS``). Until S56 the reference was S54's with the layer **on** (Phase R was
  behaviour-preserving); it is retired, because from P1 the layer-on galaxy changes by design (D215).
- **I1.** With the layer off the model runs, and every field not declared composed - every scalar, every history,
  every radial field, a phi-axis field too - is bit-identical to the layer-on run, except the census statistics, a
  closed list here, each entry naming the census it is computed from. Every composed field is its declared neutral.
- **I1, object by object (S70, D234; Audit V F-3-1, #194).** Every placed census's objects, matched on and off by
  their draw (the drawn ring and the place in the ring's draw), keep every column outside the census's declared
  placement set (``FieldDecl.placement``) bit for bit - at both templates, at default and other seeds, and under a
  ``texture_seed`` reroll.
- **I2.** A census's expected count per ring is the same with the layer on or off, to 1e-12; since L1 (S61, D220)
  the realised ring totals are the same too. *(S70, D234, F-3-10: until S70 this line said "Until L1 the realised
  counts ... differ by re-draw noise" as though it were current.)*
- **I3.** The acceptance table and the templates' checks are judged on the layer-off run, and no row names a
  synthetic or a composed field.
- **I4.** No physics stage requires a composed or a synthetic field: the graph refuses one that is not a declared
  placement reader, a composing stage or a layer stage, and ``compose`` refuses it again at run time. Placement
  also reaches physics through the realised catalogues: the stages that bin realised objects are a closed list.
- **I5 (the API's half).** Every route that takes inputs takes ``layer=off``; on and off never share a cache entry;
  any other value is a 400; the header echoes the setting.
- **The oracle.** Layer-off ``azimuthal`` equals layer-off ``basic`` on every field they share.
- **Appendix B applied.** The four cloud columns are the layer's, synthetic, drawn on the streams they always were
  with the layer on and zero with it off; ``texture_seed`` is the fifth seed, and since S56 the arm modes' phases
  read it: rerolling it moves the arms and what is placed by them, and no law (BUILD_III section 1c rule 1).
- **One reader of the switch.** No module of the model but ``galaxy/layer/compose.py`` branches on the setting, none
  calls ``.from_fields(``, and none constructs a pattern object by its class.

**As amended at gate G1 (D214, ruling by Fable).** A *composed* field is one that declares itself so, with its
neutral value (``FieldDecl(composed=True, neutral=...)``): nothing here, and nothing in the model, reads the axes.
The invariants are stated on *expected* totals: a census draws each cell's count at an expectation that carries the
placement weight, so with the layer off its realised objects are another draw. *(Struck at S70, D234, Audit V
F-3-10: "No per-object on/off assertion is made, and none should be added (gate G1, Q6): with different realised
counts the objects of the two runs do not correspond." G1's reason held until L1; drawn ring-first since S61 the
objects do correspond, and the per-object test is the audit's chief finding, F-3-1.)*

**S59 (BUILD_III Phase P4; D218), re-read.** The layer lays the segments of the arms' common winding - two synthetic
columns of a small table (``arm_segment``: 1024 rows with the layer on, none with it off; a table column, domain
``table``, not an object class's - no catalogue, no census, and the stage that lays them is no catalogue stage) - and
two templates hold a measured pin. With the layer off nothing S55 published moved but ``ngc_4414``'s
``pitch_angle``, which is its pin (the draw is published beside it, S55's bits); five fields were added. I1 holds
as now worded: the two expected totals are 1 and 0 units in the last place apart, under its four, and every
``arm_mode_amplitude_m`` is the same bits on and off. The layer-on census is another draw, and its numbers here
were re-read, each marked.

**S59 (D218 follow-up), re-read on the final model.** A segment's pitch is relative to the disc's: the table's
second column is a unit normal row (``arm_segment_pitch_deviate``), the spread it is scaled by is a sixth added
field, the ``bar`` stage's ``arm_segment_pitch_scatter``, and the table holds 1024 rows. With the layer off every
field the first build published is the bits it was. With it on every ring is turned by another phase, so the
census is another draw again, and the two expected totals are 2 and 0 units in the last place apart, under I1's
four. Each number re-read is marked ``S59 (D218 follow-up)``.

**S60 (BUILD_III Phase P5; D219), the interface.** The modes' drawn phases and the common winding are retired: the
layer lays a census of arm pieces - eight synthetic columns of the table ``arm_piece``, as many rows as it lays
and none with the layer off - and the composing stage ``stellar_pattern`` publishes the density contrast and nine
radial fields beside it (the pieces' amplitude and its cut, the chains crossing, the realised ring power and its
split by arm number), each its declared neutral with the layer off; the ``bar`` stage publishes the arm class and
the width of a piece, the ``pattern`` stage the law's arm number and the ring's budget of arm power - laws, the
same on and off. Two pins of new shapes: a named class (``ngc_4414``) and a table of measured arms (``milky_way``).
The layer-on numbers here await the re-pin after the fourth model pass; where one is pinned the test says so.
"""

from __future__ import annotations

import ast
import json
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import layer_reference
from galaxy.api import v6_clouds as v6c
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import RESERVED, ROUTES, Service
from galaxy.core.fielddoc import PROVENANCE, SYNTHETIC_DECLARATIONS, DeclarationError, FieldDecl, Kind, Ramp
from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, production, seeds
from galaxy.core.stage import Fields, LayerError, UndeclaredAccess
from galaxy.core import seeds as _seeds
from galaxy.layer import cloud_texture, compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.specs import graph, spec
from galaxy.specs import templates as checks
from galaxy.stages import bright as br
from galaxy.stages import bubbles as bb
from galaxy.stages import clouds as cl
from galaxy.stages import pattern as pt
from galaxy.stages import planets as pl
from galaxy.stages import systems as sy
from helpers import decl, impls, model, stage

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "model" / "galaxy"
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
MODELS = ("azimuthal", "basic")

# --- the closed list (BUILD_III section 1d, I1 as amended at gate G1; D214 change 12) ------------------------------
# A census statistic is a scalar or a radial field computed from realised objects. These fourteen - the measured
# fourteen, nine scalars and five radial fields - and no other field outside the catalogues' own columns and the
# declared composed fields, differ between the layer-on and the layer-off run; a field outside this list that moves
# fails test_i1. Each entry names (the stage that publishes it, the census whose realised objects it is computed
# from, and where: the function that computes it). After L1's ring-first draw the list is empty.
# S61 (D220 item 4): "After L1 the list is empty." It held fourteen at S55 (nine scalars and five radial fields:
# the star sample's catalogue_size; its planets' planet_count_sample, mean_planets_per_star, giant_fraction_sample;
# cloud_mass_total; dig_halpha_fraction, hii_luminosity_function_slope, nii_halpha_gradient_hii and the four
# *_surface_brightness_hii; hot_phase_porosity; bright_star_limit) - each a statistic of a census whose realised
# objects differed with the layer on and off, because each cell drew its own count at its own placed expectation.
# Drawn ring-first, every census draws the same objects on and off and the layer only places them: the fourteen are
# RING_FIRST_STATISTICS (below), held on and off to 1e-12. The mechanism stays - an entry here is a statistic I1 lets
# move - and the list holds nothing.
CENSUS_STATISTICS: dict[str, tuple[str, str, str]] = {}
# S61 (D220 item 4): was 4 - the star sample's four, until its own build (14 at S55; the clouds' nine and the bright
# limit left first).
assert CENSUS_STATISTICS == {}
# S61 (D220 item 4): the statistics of the censuses drawn ring-first - a ring's count and every per-object draw on the
# ring's stream before the layer places them, so the same objects on and off and only their sector and azimuth differ.
# Each is identical on and off to 1e-12 relative (bit for bit where nothing is summed in another order: the objects
# are concatenated cell by cell, so a sum over them may differ in its last bits). Each entry: (its stage, the census,
# where it is computed).
RING_FIRST_STATISTICS = {
    # S61 (D220 items 1-4): the star sample drawn ring-first - each ring's count one seeded rounding of its expectation,
    # every star's draws arrays on the ring's streams, only its sector and azimuth placed; its planets keyed on the
    # star's place in its ring's draw. So the sample's size and its planets' numbers are the same on and off.
    "catalogue_size": ("systems", "the star sample",
                       "systems.compute_systems: the rows the rings' seeded rounding realised (systems.ring_star_count)"),
    "planet_count_sample": ("planets", "the star sample's planets",
                            "planets.compute_planets: the planets drawn for the sample's stars, counted"),
    "mean_planets_per_star": ("planets", "the star sample's planets",
                              "planets.compute_planets: the planets per star, averaged over the sample's stars"),
    "giant_fraction_sample": ("planets", "the star sample's planets",
                              "planets.compute_planets: the share of the sample's stars with a giant"),
    # S61 (D220 item 4): the bright catalogue drawn ring-first - each ring's stars the same draws on and off, only their
    # cell and azimuth placed - so the default selection's limit is the same number (bit for bit, measured).
    "bright_star_limit": ("bright_stars", "the bright catalogue",
                          "bright.select_brightest, through bright.scalars: the luminosity the default selection's "
                          "brightest few thousand realised stars are complete above"),
    "cloud_mass_total": ("clouds", "the cloud census",
                         "clouds.compute_clouds: the realised clouds' cloud_mass, summed"),
    "dig_halpha_fraction": ("nebular", "the HII-region census",
                            "nebular.leaked_fraction: the regions' leaked share, a sum over the realised clusters"),
    "hii_luminosity_function_slope": ("nebular", "the HII-region census",
                                      "nebular.luminosity_function_slope: a fit to the realised regions' "
                                      "hii_halpha_luminosity (acceptance row 35)"),
    "nii_halpha_gradient_hii": ("nebular", "the HII-region census",
                                "nebular.nii_halpha_gradient, over the [N II] ring light below (acceptance row 37)"),
    **{f"{line}_surface_brightness_hii": ("nebular", "the HII-region census",
                                          "nebular.compute_nebular: the ring's Halpha times nebular.ring_ratios - the "
                                          "regions' line ratio weighted by their Halpha, binned by cluster_birth_radius")
       for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")},
    "hot_phase_porosity": ("bubbles", "the clusters' bubbles (with the remnants, which no placement moves)",
                           "bubbles.hot_phase_porosity: the realised bubbles' volumes, binned by cluster_birth_radius"),
}
assert len(RING_FIRST_STATISTICS) == 14 and not set(RING_FIRST_STATISTICS) & set(CENSUS_STATISTICS)  # S61 (D220 item 4): was 9 - with bright_star_limit; 10 - with the star sample's four
RING_FIRST_RTOL = 1e-12  # D220 item 4: "to 1e-12 relative for sums"
# The object classes a placement moves: every column of these is a catalogue's, not a statistic.
PLACED_OBJECTS = {"star", "planet", "bright_star", "cloud", "cluster"}
# And the one census no pattern places (bubbles.remnant_expected shares a ring evenly among its sectors).
UNPLACED_OBJECTS = {"remnant"}
# S59 (D218 items 1-2): and one table that is no census and no object class at all - the rows of the arms' winding,
# a segment each: the layer's own realisation (the `arm_phases` stage's two synthetic table columns), 1024 rows with
# the layer on and none with it off ("layer off ... no segments are drawn"). Nothing is counted, expected or placed
# of them. The table's inventory (was LAYER_OBJECTS while the two were declared an object class's columns).
# S60 (D219 item 7): was {"arm_segment"} with 1024 rows, fixed - the table is the census of arm pieces, `arm_piece`,
# the `arm_pieces` stage's eight synthetic columns, one row a piece: as many rows as the census lays (the arm-number
# law and the draws decide it), none with the layer off ("no arm placed").
LAYER_TABLES = {"arm_piece", "gas_spur"}  # S62 (D221 item 7 as amended): was {"arm_piece"} - and the gas spurs' census
# S61 (D220 part II): the clustering field of the censuses - the layer stage `census_clustering`'s two synthetic
# fields, its 32-bit seed (a scalar) and its mean in each level-0 cell (the table `cell`, one row a cell, the rows
# not drawn). A realisation with the layer on; NaN with it off (D164; D215's ruling 5), the cell rows kept.
CLUSTERING_FIELDS = {"census_clustering_seed", "census_clustering_cell_mean"}
# S62 (D221): the gas fluctuation field - the layer stage `gas_fluctuation`'s eight synthetic fields: its seed (a
# scalar), six columns of the table `ring` (one row a level-0 ring: the break index, the Mach number, the width, the
# strain, the twist, the octave sum's normaliser) and its normaliser in each level-0 cell (the table `cell`). Numbers
# with the layer on, NaN with it off, the rows kept. Under another texture seed the seed and the cell normalisers
# move; the ring table is the model's physics read per ring and does not (GAS_RING_FIELDS).
GAS_RING_FIELDS = {"gas_fluctuation_break_octave", "gas_fluctuation_mach", "gas_fluctuation_sigma",
                   "gas_fluctuation_strain", "gas_fluctuation_twist", "gas_fluctuation_norm"}
GAS_FIELDS = {"gas_fluctuation_seed", "gas_fluctuation_cell_normaliser", *GAS_RING_FIELDS}
# The layer's fields that are numbers with the layer on and NaN with it off, the rows kept (S61, S62).
NAN_OFF_FIELDS = CLUSTERING_FIELDS | GAS_FIELDS
# Two scalars are a census's *expected* total: the expected counts summed over every cell, each cell carrying its
# sector's placement weight. The weights average to 1 round a ring to rounding and not to the bit, so the total is
# the same number with the layer on or off, and between two realisations, **to its last bit or the one beside it**:
# found at S56 between two texture seeds (first pass), and between the layer on and off when the window was
# corrected (third pass, D215 ruling 11: at the default seeds `cloud_count_total` is 16693.43298750999 on and
# 16693.432987509994 off - until then the two happened to be the same bits, and I1's test held them to that).
# The layer-off value is S55's own bits (the reference). Held to one unit in the last place here; reported to the
# gate, since I1 says "bit for bit" and an expected total is no census statistic.
# **S58 (D217): two units in the last place, and reported to the lead - I1's wording as amended at gate G2 is "equal
# within one unit in the last place".** Inside a bar's reach a cloud cell's placement weight is now the sum of two
# exact sector means - the response's and the lane field's, each 1 round the ring to its own rounding - where it
# was one and a cosine's closed integral; at the default seeds `cloud_count_total` reads 16693.43298751 with the
# layer on, two units above the layer-off 16693.432987509994 (one unit at S57). The rounding of a mean that is 1
# identically in the law, still; the layer-off value is S55's bits, unmoved. Not widened in silence: the unit count
# is pinned below, and the invariant's text is the gate's to amend or the lanes' means the lead's to have summed
# otherwise.
# **As the gate answered (D217's follow-up): the expected totals are "equal within four units in the last place"**
# (BUILD_III's wording is the lead's to amend). The bound the invariant states is four; what this test pins is the
# measured two, so a third unit is seen here before it reaches the invariant's four.
# **S59 (D218): one unit again, as measured.** The winding's segments turn each ring's response among the cloud
# cells, so the cells' exact means sum to another rounding: `cloud_count_total` reads 16693.432987509997 with the
# layer on, one unit above the layer-off 16693.432987509994 (S55's bits, unmoved); `bright_star_count_1e3` is the
# same bits on and off (0 units). I1 as now worded - "equal within four units in the last place" - holds with three
# to spare; the pin below is the measured one, so a second unit is seen here before it reaches the invariant's four.
# **S59 (D218 follow-up): two units again, as measured.** A segment's pitch is relative to the disc's and the rows
# are other rows, so each ring's response is turned by another phase and the cloud cells' exact means sum to another
# rounding: `cloud_count_total` reads 16693.43298751 with the layer on, two units above the layer-off
# 16693.432987509994 (S55's bits, unmoved) - S58's reading, by another road; `bright_star_count_1e3` is the same
# bits on and off (0 units). I1's "equal within four units in the last place" holds with two to spare.
# **S70 (D234, Audit V F-3-11): the paragraphs above are history.** They cite G2's "one unit" as the wording held and
# label the pin "the measured count", where the invariant's text says four and the count measured on the final model
# is one (test_the_clouds_expected_total_s_layer_on_bits_as_measured pins it at the production run). What an expected
# total is held to here is named for what it is: a margin, and the margin is the invariant's own four units. Measured
# at S70 at the runs the walk now reads (F-3-2): `cloud_count_total` 1 unit apart at the production pair, 3 at the
# Milky Way's seeds (3, 777) on SMALL, and **4 - the bound itself - between texture seeds 0 and 987654321 on SMALL**
# (16076.452597444224 against 16076.452597444217; reported to the lead at S70: the margin has no unit to spare there).
EXPECTED_TOTALS = {"cloud_count_total", "bright_star_count_1e3"}
# S70 (D234, F-3-11): was `EXPECTED_TOTAL_UNITS = 2`, labelled "the measured count" (S59's follow-up; measured 1 since
# S60) - renamed the margin it is, and set to the invariant's four because the second seed pair and the reroll
# measure 3 and 4 (above); the production pair's measured unit is pinned in the test that measures it.
EXPECTED_TOTAL_MARGIN = 4  # units in the last place: I1's bound, as the gate words it at S58 (D217)
EXPECTED_TOTAL_BOUND = 4  # the invariant's own
assert EXPECTED_TOTAL_MARGIN <= EXPECTED_TOTAL_BOUND


def same_expected_total(a, b) -> bool:
    """Equal, or apart by at most ``EXPECTED_TOTAL_MARGIN`` units in the last place: what an expected total is held
    to (I1; above)."""
    a, b = float(a), float(b)
    return abs(a - b) <= EXPECTED_TOTAL_MARGIN * float(np.spacing(max(abs(a), abs(b))))


def same_ring_first(a, b) -> bool:
    """Equal to ``RING_FIRST_RTOL`` relative, element by element (NaN equal to NaN, zero to zero): a statistic of a
    census drawn ring-first, the same objects summed in another order (D220 item 4)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.allclose(a, b, rtol=RING_FIRST_RTOL, atol=0.0, equal_nan=True))


def same(a, b) -> bool:
    """Bit for bit: arrays by dtype, shape and bytes (NaN equal to NaN), scalars and labels by value."""
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    a, b = np.asarray(a), np.asarray(b)
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


def constants(m) -> dict[str, float]:
    return {k: c.value for k, c in m.constants.items()}


def answer(response) -> tuple[dict, list[tuple[str, str, tuple, bytes]]]:
    """A response as what it says: its header less ``stages`` (what a request ran depends on what the service
    already held, not on what was asked) and every array's name, dtype, shape and bytes, in the body's order."""
    assert response.ok, response.status
    header, arrays = wire.decode(response.body)
    return ({k: v for k, v in header.items() if k != "stages"},
            [(n, a.dtype.str, a.shape, a.tobytes()) for n, a in arrays.items()])


@pytest.fixture(scope="module")
def reference():
    return layer_reference.load()


@pytest.fixture(scope="module")
def runs(prod):
    """Both models, the layer on and off, every stage, on the production grid: {(model, layer): Outputs}."""
    models = prod[0]
    return {(name, layer): run(models.get(name), layer=layer) for name in MODELS for layer in (True, False)}


@pytest.fixture(scope="module")
def small(prod):
    models = prod[0]
    return {(name, layer): run(models.get(name), grid=SMALL, layer=layer) for name in MODELS for layer in (True, False)}


# --- the reference: the layer off is S55's layer off --------------------------------------------------------------

# The fields of a layer-off run that are not S55's bits, by name: **a closed list** (D215, the lead's reading 3).
# `arm_multiplicity` was the drawn arm number (4 for both templates) and is the derived dominant one - the mode
# carrying the most mass-weighted power: 6 for the Milky Way, and 4 for ngc_4414 - the number S55 drew, by another
# road, so that template's field is S55's bits and only the Milky Way's differs. Nothing else of S55 moved.
# (On the X / 2 window of S56's first two passes the labels were 3 and 2: D215 ruling 11.)
# S58 (D217 items 2-3): `ngc_4414` is pinned unbarred, as observed, and "an unbarred galaxy publishes NaN for the
# bar's fields" (D164) - so the four bar scalars S55 published for it are NaN by ruling. Each is S55's bits on the
# Milky Way template, and on `ngc_4414` itself with the pin taken off (the test below shows both, and that nothing
# else under any digest moved).
_NAN = float("nan")
LAYER_OFF_EXCEPTIONS = {
    "arm_multiplicity": {"milky_way": (4.0, 6.0), "ngc_4414": (4.0, 4.0)},
    "bar_half_length": {"milky_way": (5.2097114005817895, 5.2097114005817895), "ngc_4414": (3.51010852350661, _NAN)},
    "bar_contrast": {"milky_way": (0.28926359920045497, 0.28926359920045497), "ngc_4414": (0.32104666953110067, _NAN)},
    "bar_corotation_radius": {"milky_way": (5.483712200859753, 5.483712200859753), "ngc_4414": (3.792933285043702, _NAN)},
    "bar_pattern_speed": {"milky_way": (45.46362850463187, 45.46362850463187), "ngc_4414": (63.051302305629854, _NAN)},
    # S59 (D218 item 6): "`pitch_angle` = 28.9° replaces the draw (a measured mean, as `bar_present` is); the law's
    # own value 14.3° is published beside it" - `ngc_4414`'s pitch is the template's pin, layer on and off alike, and
    # the number S55 drew is `pitch_angle_drawn`, to the bit (the test below). The Milky Way's is S55's draw.
    "pitch_angle": {"milky_way": (13.53784060954308, 13.53784060954308), "ngc_4414": (14.330046483982906, 28.9)},
    # S67 (D231): the clouds stage's one central A_V, a law of the constants: one surface density (Heyer et al. 2009's
    # 42) until the size law took Lada & Dame 2020's two regimes; now the inner regime's 82, 82/42 of S55's on both.
    "cloud_extinction_v": {"milky_way": (2.9695761563889844, 5.7977439243784925),
                           "ngc_4414": (2.9695761563889844, 5.7977439243784925)},
}
CLOUD_SIZE_LAW_BY_RULING = {"cloud_extinction_v"}  # S67 (D231): both templates
UNBARRED_BY_RULING = {"bar_half_length", "bar_contrast", "bar_corotation_radius", "bar_pattern_speed"}
PITCH_PINNED_BY_RULING = {"pitch_angle"}  # S59 (D218 item 6): `ngc_4414` alone


def same_number(a: float, b: float) -> bool:
    return a == b or (a != a and b != b)  # NaN is the value an unbarred galaxy's bar number has
# And the fields P1 adds, which S55 did not publish: the law's five amplitudes and its saturation, radial and the
# same on and off; the layer's five phases, not numbers with the layer off.
# S60 (D219): the five phases are retired with the modes' drawn phases - the arms are a census of pieces (below).
ADDED_AT_S56 = {*pt.AMPLITUDE_FIELDS, "arm_saturation"}
# And the one field P2 adds (S57, D216): the frame every arm mode is steady in, a derived radial field of the `bar`
# stage - a statement, the same on and off, read by no stage. Nothing S55 published moved with it.
ADDED_AT_S57 = {"arm_pattern_speed"}
# And the six P3 adds (S58, D217): the bar's formation time and the verdict, the body's shape - derived, the `bar`
# stage's - and the body's share of the disc's mass, the `pattern` stage's. Laws, the same on and off.
ADDED_AT_S58 = {"bar_formation_time", "bar_present", "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_mass_share"}
# And one more at the gate's follow-up (S58, D217): the gas's contrast as the star formation law reads it - the
# `gas_pattern` stage's second composed field, the lanes' excess spread over the bar's footprint. 1 everywhere with
# the layer off, as the gas's own contrast is: its declared neutral.
ADDED_AT_S58 |= {"star_formation_gas_contrast"}
# And the five P4 adds (S59, D218): the radius the winding is anchored at (the `bar` stage's, derived: a number whether
# there is a bar or not); the pitch as the law draws it and the Sun's azimuth (the `pattern` stage's: the first is
# `pitch_angle` wherever no template pins one, the second NaN unless a template gives the bar's angle to the Sun);
# and the layer's two segment columns (the `arm_phases` stage's, synthetic: no row with the layer off).
# S59 (D218 follow-up): six - `arm_segment_pitch_residual` (degrees) is `arm_segment_pitch_deviate`, a unit normal
# row, and the spread it is scaled by is published by the `bar` stage as `arm_segment_pitch_scatter`: a law's
# number, 0.56 of the disc's pitch, the same on and off.
# S60 (D219): the anchor, the two segment columns and the pitch's spread are retired with the common winding; two of
# the six remain.
ADDED_AT_S59 = {"pitch_angle_drawn", "sun_azimuth"}
# And the P5 adds (S60, D219): the arm class and the width of a piece across itself (the `bar` stage's, derived); the
# law's arm number and the ring's budget of arm power (the `pattern` stage's, seeded, the same on and off); the
# layer's table of arm pieces (eight synthetic columns, no row with the layer off); and the composing stage's nine
# radial fields beside the density contrast - the pieces' amplitude and its cut, the chains crossing, the realised
# ring power and its split by arm number - each its declared neutral with the layer off.
ADDED_AT_S60 = {"arm_class", "arm_piece_width", "arm_design_count", "arm_power_budget", *pt.PIECE_FIELDS,
                "arm_piece_amplitude", "arm_piece_saturation", "arm_chain_count", "arm_ring_power",
                *(f"arm_mode_power_{m}" for m in range(2, 7))}
assert len(ADDED_AT_S60) == 21 and len(pt.PIECE_FIELDS) == 8
# And L1's (S61, D220 item 6): the radius the binning stages read, the cluster's cloud's.
# S61 (D220 part II, as the lead amended item 4): the radius the cloud's ring drew, which the cloud now carries beside
# its placed radius, and the layer's clustering field - its seed and its mean in each level-0 cell (NaN with the
# layer off).
ADDED_AT_S61 = {"cluster_birth_radius", "cloud_birth_radius", "census_clustering_seed", "census_clustering_cell_mean"}
# S62 (D221 item 7 as amended): the layer's census of gas spurs, the table `gas_spur` - no row with the layer off.
from galaxy.stages.spurs import SPUR_FIELDS as _SPUR_FIELDS  # noqa: E402

ADDED_AT_S62_SPURS = set(_SPUR_FIELDS)
assert len(ADDED_AT_S62_SPURS) == 12
# S62 (D221): the gas fluctuation field's eight fields (GAS_FIELDS), NaN with the layer off.
ADDED_AT_S62 = GAS_FIELDS
# S61 (D220 items 1 and 10): "everything that moves, moves once". With the layer off the cloud census is a new draw -
# each ring's count and arrays on the ring's stream - and with it every column of the clouds and of the clusters (with
# their HII regions and bubbles, which are columns of the cluster class) and the nine statistics computed from them.
# Nothing else of S55's layer-off run moves: no law, no radial field that is not those statistics, no remnant.
# S61 (D220 items 1-4 and 10): and the bright catalogue, drawn ring-first in its own build - its 17 columns and its
# limit (RING_FIRST_STATISTICS).
# S61 (D220 items 1-4 and 10): and the star sample and its planets, drawn ring-first in their own build - every column
# of both and the four statistics (RING_FIRST_STATISTICS).
REDRAWN_OBJECTS_AT_S61 = {"cloud", "cluster", "bright_star", "star", "planet"}


def redrawn_at_s61(out, held) -> set[str]:
    """The fields of S55's reference the ring-first redraw moves (D220 item 10), read from the declarations."""
    return {n for n in held if out.decls[n].kind.domain == "object" and out.decls[n].of in REDRAWN_OBJECTS_AT_S61} | (
        set(RING_FIRST_STATISTICS) & set(held))
# The composed fields of both models (sfr_modulation is the azimuthal model's own) and the neutral each declares:
# a contrast and the cut are 1 with the layer off, a power, a count and an amplitude 0.
COMPOSED_FIELDS = {"pattern_density_contrast", "gas_density_contrast", "star_formation_gas_contrast",
                   "arm_piece_amplitude", "arm_piece_saturation", "arm_chain_count", "arm_ring_power",
                   *(f"arm_mode_power_{m}" for m in range(2, 7))}
COMPOSED_NEUTRALS = {"arm_piece_amplitude": 0.0, "arm_chain_count": 0.0, "arm_ring_power": 0.0, **{f"arm_mode_power_{m}": 0.0 for m in range(2, 7)}}


@pytest.mark.parametrize("template", layer_reference.TEMPLATES)
@pytest.mark.parametrize("name", MODELS)
def test_layer_off_every_field_is_the_s55_reference_bit_for_bit_but_the_named_list(runs, reference, prod, name, template):
    """D215: "every field that exists in both is bit-identical layer-off, except a closed, named list". The reference
    is sha256 of every field's bytes of S55's layer-off run, captured before P1's model code moved; nothing is
    re-pinned here - a field that moves joins the named list by a decision, or the phase stops (BUILD_III 3d)."""
    out = runs[name, False] if template == "milky_way" else run(prod[0].get(name), layer_reference.template_inputs(template), layer=False)
    held = reference["fields"][layer_reference.label(name, template)]
    now = {n: layer_reference.value_digest(v) for n, v in out.fields.items()}
    assert not set(held) - set(now), sorted(set(held) - set(now))  # no field was lost
    moved = {n for n in held if now[n] != held[n]}
    # The fields of the named list whose value on this template is not S55's (the label can land on S55's number).
    named = {n for n, by_template in LAYER_OFF_EXCEPTIONS.items() if not same_number(*by_template[template])}
    # S61 (D220 item 10): was `moved == named` - the ring-first redraw moves the cloud and cluster censuses and their
    # nine statistics, every one of them (measured: 17 cloud columns, 38 cluster columns, 9 statistics), and nothing else.
    redrawn = redrawn_at_s61(out, held)
    # S61 (D220): 17 + 38 + 9 at the clouds' build; the bright catalogue's 17 columns and its limit join; and the star
    # sample's build: the star's 19 columns (the catalogue's 18 and the planets stage's star_planet_count), the
    # planet's 9 and the four statistics.
    assert len(redrawn) == 17 + 38 + 17 + 19 + 9 + 14 and not redrawn & named
    assert moved == named | redrawn, sorted(moved ^ (named | redrawn))
    moved -= redrawn
    # S58 (D217): was `else set()` - `ngc_4414`'s four bar scalars are NaN by ruling (unbarred, as observed).
    # S59 (D218 item 6): was `else UNBARRED_BY_RULING` - and its pitch is the measured one by ruling. Nothing else of
    # either template's layer-off run moved at S59: "a galaxy without pins: layer off bit for bit" (item 7), and the
    # Milky Way's pin places the Sun and "moves nothing else".
    # S67 (D231): and the clouds' one central A_V on both, the size law's inner surface density.
    assert moved == ({"arm_multiplicity"} if template == "milky_way" else UNBARRED_BY_RULING | PITCH_PINNED_BY_RULING) | CLOUD_SIZE_LAW_BY_RULING
    for n, by_template in LAYER_OFF_EXCEPTIONS.items():
        was, is_now = by_template[template]
        assert held[n] == layer_reference.value_digest(was) and same_number(float(out.fields[n]), is_now), (n, template)
    # S57 (D216): was `== ADDED_AT_S56` - the layer-off run gained one field, `arm_pattern_speed`, and lost or moved none.
    # S58 (D217): was `== ADDED_AT_S56 | ADDED_AT_S57` - six more, and none lost; a seventh at the gate's follow-up.
    # S59 (D218): was `== ADDED_AT_S56 | ADDED_AT_S57 | ADDED_AT_S58` - five more, and none lost (six since the
    # gate's follow-up: ADDED_AT_S59, above).
    # S60 (D219): was `... | ADDED_AT_S59` with the phases, the anchor, the segment columns and the spread among the
    # earlier sets - 21 more and seven retired; the reference's count is S55's and does not move.
    # S61 (D220 item 6): was `... | ADDED_AT_S60` - and the binners' radius, `cluster_birth_radius`.
    # S62 (D221 item 7 as amended): was `... | ADDED_AT_S61` - and the gas spurs' twelve columns, empty with the layer off.
    # S62 (D221): and the gas fluctuation field's eight.
    assert set(now) - set(held) == ADDED_AT_S56 | ADDED_AT_S57 | ADDED_AT_S58 | ADDED_AT_S59 | ADDED_AT_S60 | ADDED_AT_S61 | ADDED_AT_S62_SPURS | ADDED_AT_S62 and len(held) == (332 if name == "azimuthal" else 331)
    assert out.fields["bar_present"] == ("yes" if template == "milky_way" else "no")
    # S59 (D218): what the five are with the layer off. The anchor is the bar's half-length, or where the bar would
    # be; the drawn pitch is S55's `pitch_angle`, to the bit, on both templates; no segment is laid; and the Sun's
    # azimuth is not a number - the default galaxy has no pin (the Milky Way *template*'s is read in
    # tests/test_segments.py), and `ngc_4414` has neither the pin nor a bar.
    # S60 (D219 item 7): the anchor and the spread are gone with the winding; no piece is laid with the layer off
    # (every column of the table has no row); the Milky Way template's pinned arms are read in tests/test_pieces.py.
    assert layer_reference.value_digest(out.fields["pitch_angle_drawn"]) == held["pitch_angle"]
    assert all(np.asarray(out.fields[n]).shape == (0,) for n in pt.PIECE_FIELDS) and np.isnan(out.fields["sun_azimuth"])
    # S60 (D219 items 1 and 3): the P5 laws with the layer off - the class the bar decides (a barred disc a grand
    # design, an unbarred one multi-armed, flocculent by pin alone), the width of a piece a law of the scale length.
    assert out.fields["arm_class"] == ("grand_design" if template == "milky_way" else "flocculent")
    assert np.all(np.asarray(out.fields["arm_piece_width"]) > 0.0) and np.all(np.isfinite(out.fields["arm_power_budget"]))
    if template == "ngc_4414":
        # "Show nothing else under each digest changed": the same inputs with the pins taken off - the criterion bars
        # this disc, the pitch is the draw - are S55's layer-off run on every field S55 published, the four bar
        # scalars and the pitch with them; and the pinned run differs from that one in the verdict, the bar's eight
        # numbers, the five arm amplitudes (no taper: the modes run to the centre) and the pitch - nothing else, on
        # any of the model's fields.
        # S59 (D218 item 6): was `if k != "bar_present"`, one pin; the template holds two, and each is shown alone.
        # S60 (D219 item 3): three - the arm class is pinned flocculent, and with it move the class alone, and with
        # the amplitudes the two radial laws made from them (the budget and the arm number the law counts).
        given = layer_reference.template_inputs(template)
        pins = {"bar_present", "pitch_angle", "arm_class"}
        assert set(templates.pinned(templates.TEMPLATES[template])) == pins
        unpinned = run(prod[0].get(name), {k: v for k, v in given.items() if k not in pins}, layer=False)
        assert unpinned.fields["bar_present"] == "yes" and "bar_present" not in unpinned.inputs and out.inputs["bar_present"] is False
        assert "pitch_angle" not in unpinned.inputs and out.inputs["pitch_angle"] == 28.9
        assert "arm_class" not in unpinned.inputs and out.inputs["arm_class"] == "flocculent" and unpinned.fields["arm_class"] == "grand_design"
        # S61 (D220 item 10): was `== set()` - the unpinned run's census is the ring-first redraw too.
        # S67 (D231): and the clouds' one central A_V, the size law's inner surface density (pinned or not).
        assert {n for n in held if layer_reference.value_digest(unpinned.fields[n]) != held[n]} == redrawn_at_s61(unpinned, held) | CLOUD_SIZE_LAW_BY_RULING
        differ = {n for n in out.fields if not same(out.fields[n], unpinned.fields[n])}
        assert differ == {"bar_present", *UNBARRED_BY_RULING, "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_mass_share", *pt.AMPLITUDE_FIELDS,
                          *PITCH_PINNED_BY_RULING, "arm_class", "arm_design_count", "arm_power_budget"}
        assert np.all(np.asarray(out.fields["arm_saturation"]) == 1.0) and out.fields["bar_formation_time"] == unpinned.fields["bar_formation_time"]
        # The pitch's pin alone, layer off: it moves `pitch_angle` and no other field of the model - the gas law's ε
        # and f read it, and with the layer off no response is solved.
        drawn_pitch = run(prod[0].get(name), {k: v for k, v in given.items() if k != "pitch_angle"}, layer=False)
        assert {n for n in out.fields if not same(out.fields[n], drawn_pitch.fields[n])} == PITCH_PINNED_BY_RULING
        assert float(drawn_pitch.fields["pitch_angle"]) == float(out.fields["pitch_angle_drawn"]) == LAYER_OFF_EXCEPTIONS["pitch_angle"][template][0]
        # S60 (D219 item 3): the class's pin alone, layer off: it moves `arm_class` and nothing else - the class is
        # read by the layer's census alone, and with the layer off no piece is laid. Unpinned, the model's rule
        # makes this unbarred disc multi-armed.
        derived_class = run(prod[0].get(name), {k: v for k, v in given.items() if k != "arm_class"}, layer=False)
        assert {n for n in out.fields if not same(out.fields[n], derived_class.fields[n])} == {"arm_class"}
        assert derived_class.fields["arm_class"] == "multi_armed"
    assert now["arm_pattern_speed"] == layer_reference.value_digest(np.asarray(out.fields["circular_velocity"]) / out.grid.R)
    if template == "ngc_4414":
        assert out.inputs["texture_seed"] == 4414


def test_layer_off_every_route_s_arrays_and_header_are_the_s55_reference(reference):
    """Every input route asked with ``layer=off``, a window and the whole disc, both models and a template: each
    array of the body is the reference's bytes in the reference's order, and the header is the reference's less
    ``stages`` (what a request ran depends on what the service already held). A census placed by no pattern is the
    census S55 placed by no pattern, object for object."""
    made = layer_reference.routes_digest()
    assert set(made) == set(reference["routes"]) and len(made) == 42
    # S61 (D220 item 10): and the bright catalogue's two routes per model, its ring-first redraw (was 14).
    redrawn_routes = {label for label in made if "/clouds/" in label or "/clusters/" in label or "/bright/" in label}
    assert len(redrawn_routes) == 18
    # S61 (D220 items 1-4 and 10): and the star sample's routes - each model's region window, whole disc, level-2
    # window and brightest selection, its system, and the template's window: the ring-first sample, a new draw.
    sample_routes = {label for label in made if "/region/" in label or label.endswith("/system")}
    assert len(sample_routes) == 11
    redrawn_routes |= sample_routes
    for label, got in made.items():
        held = reference["routes"][label]
        assert got["status"] == held["status"] == 200, label
        if label in redrawn_routes:
            # S61 (D220 item 10): the cloud and cluster routes serve the ring-first census, a new draw - every array and
            # the header's cells - in the columns they always sent, the clusters' with the binners' radius after their
            # light temperature (ADDED_AT_S61). The star sample's routes likewise (its star, its planets, its cells).
            names, was = [a[0] for a in got["arrays"]], [a[0] for a in held["arrays"]]
            assert [n for n in names if n not in ADDED_AT_S61] == was, label
            # S64 (V6): the clouds' own dust column is digested apart and reported added (layer_reference.ADDED_AT_S64).
            # S64 (V6, R5): and the clusters' knots entry, with their line_response where filters= is asked
            # (layer_reference.ADDED_KNOTS).
            knots = (["line_response"] if label.endswith("/clusters/filters") else []) + ["knots"]
            # S70 (D234): was ["cloud_dust_extinction_v"] - and the clouds' shape (Audit V F-4-3, ADDED_AT_S70).
            assert got.get("added", []) == (list(v6c.DERIVED_COLUMNS) if "/clouds/" in label else knots if "/clusters/" in label else []), label
            assert ("cluster_birth_radius" in names) == ("/clusters/" in label), label
            assert got["header"] != held["header"], label
            continue
        # S63 (D223): the render adds the stars split by age and the weights that place them (the old part's, and the
        # middle's where the model publishes sfr_modulation; the young's is the dust's placement), digested apart.
        # S64 (V6): and the share of each ring's dust that is diffuse once its realised clouds hold theirs, with its
        # header entry `clouds`, digested apart likewise (layer_reference.ADDED_AT_S64).
        # S66 (V7, D226 R4-R6): and the render's four new arrays (the placement without the spurs - with the layer off
        # the neutral placement itself - and the middle part's kept-octave windows, the same bits on and off) and its
        # header's gas_fluctuation, census_clustering and spurs entries, their values null with the layer off -
        # digested apart likewise (layer_reference.ADDED_ARRAYS_AT_S66, ADDED_AT_S66).
        s66 = [*layer_reference.ADDED_ARRAYS_AT_S66, *layer_reference.ADDED_AT_S66]
        assert got.get("added", []) == ((["stars_young", "stars_middle", "stars_old", "stars_placement"]
                                         + (["stars_middle_placement"] if not label.startswith("basic/") else [])
                                         + ["dust_diffuse_share"] + s66)
                                        if "/render/" in label else []), label
        if "/render/" in label:
            # S61 (D220 items 6 and 10): the render's HII line light is the regions' ring ratios - the ring-first
            # census's, binned by the clouds' radii - and is a new draw; every other array and the header are S55's.
            assert [a[0] for a, b in zip(got["arrays"], held["arrays"]) if a != b] == ["lines_hii"], label
            assert [a[0] for a in got["arrays"]] == [b[0] for b in held["arrays"]], label
            assert got["header"] == held["header"], label
            continue
        assert got["arrays"] == held["arrays"], (label, [a[0] for a, b in zip(got["arrays"], held["arrays"]) if a != b])
        # S58 (D217 item 2): a request for a template carries the template's pin among its inputs, which S55's
        # header did not hold. The header is digested with the pin taken out of its inputs and the pin read beside
        # it (``layer_reference.route_digest``): every other word of the four `ngc_4414` headers is S55's, and the
        # requests that name no template are pinned nothing.
        assert got["header"] == held["header"], label
        # S59 (D218 item 6): was `{"bar_present": False}` - the template holds a second pin, its measured pitch. With
        # the layer off no array of any route reads it: every array above is still S55's, object for object.
        # S60 (D219 item 3): and a third, its observed arm class - read by the layer's census alone.
        assert got.get("pinned", {}) == ({"bar_present": False, "pitch_angle": 28.9, "arm_class": "flocculent"} if label.startswith("ngc_4414/") else {}), label


def test_the_cloud_route_sends_its_columns_in_the_order_it_always_did(prod):
    """The four texture columns changed publisher, not place: /api/clouds' columns are ``clouds.WIRE_COLUMNS``, which
    is the clouds stage's object columns with the layer's four where they stood, and nothing else."""
    _, impls_, _ = prod
    own = [d.name for d in impls_.get("clouds").publishes if d.kind.domain == "object"]
    layers = [d.name for d in impls_.get("cloud_texture").publishes if d.kind.domain == "object"]
    assert tuple(layers) == cl.TEXTURE_COLUMNS
    assert set(cl.WIRE_COLUMNS) == set(own) | set(layers) and len(cl.WIRE_COLUMNS) == len(own) + len(layers)
    assert [n for n in cl.WIRE_COLUMNS if n in own] == own  # the stage's own, in its own order
    header, arrays = Service(grid=SMALL).handle("/api/clouds", "r_min=7&r_max=9&phi_min=0&phi_max=0.6").frame()
    # S64 (D224, R1): the route appends ONE column of its own after the stage's and the layer's - the cloud's dust
    # column, derived in the API from published fields (api/v6_clouds.COLUMN); it is not a stage's column.
    # S70 (D234): was v6c.COLUMN alone - and the clouds' shape after it (Audit V F-4-3), the API's too.
    assert header["columns"] == [*cl.WIRE_COLUMNS, *v6c.DERIVED_COLUMNS] and list(arrays) == [*cl.WIRE_COLUMNS, *v6c.DERIVED_COLUMNS, "cell", "index"]


# --- I1: the layer off moves no law, no radial field and no total -------------------------------------------------


def walk_i1(on, off, name: str, neutral_on: frozenset[str] = frozenset(),
            empty_tables: frozenset[str] = frozenset()) -> tuple[set[str], set[str]]:
    """I1's walk over every declared field of one layer-on and one layer-off run (S70, D234, Audit V F-3-2: set apart
    from the production test so that a second template and a second seed pair walk it too). Returns the fields that
    moved outside every exemption and the ring-first statistics that moved in their last bits; asserts the rest.
    ``neutral_on`` names the composed fields this run may leave at their neutral with the layer on (a cut that does
    not fire, a bar's lanes in a galaxy with no bar)."""
    assert set(on.fields) == set(off.fields) and on.order == off.order  # the same model ran, every stage of it
    composed = {n: d for n, d in on.decls.items() if d.composed}
    # S58 (D217 follow-up): was two (three for azimuthal) - the gas's contrast as the star formation law reads it.
    # S60 (D219): was three (four) - the composing stage `stellar_pattern` publishes nine radial fields beside the
    # density contrast, the law applied to the census: the pieces' amplitude and its cut, the chains crossing a
    # ring, the realised ring power and its split by arm number. A contrast's neutral is 1; a power's, a count's
    # and an amplitude's is 0, the cut's 1.
    assert set(composed) == COMPOSED_FIELDS | ({"sfr_modulation"} if name == "azimuthal" else set())
    for n, d in composed.items():
        # Exactly its declared neutral everywhere with the layer off - the number, not that number to rounding -
        # and not everywhere its neutral with the layer on: the layer does place.
        assert isinstance(d.neutral, float) and d.neutral == COMPOSED_NEUTRALS.get(n, 1.0), n
        assert np.all(np.asarray(off.fields[n]) == d.neutral), n
        if n in neutral_on:
            # S60 (D219), the one exception at the production run, stated: the cut of the pieces' amplitude is
            # composed and is its neutral, 1, wherever the cut does not fire - and on the default seeds it fires on
            # no ring (nor on either template's, layer on). It fires on some seeds of the suite's legs (test_pieces'
            # gate test), so the field is placed by the layer and stays listed; it is not read here as moving.
            # S60 fourth pass: was asserted not everywhere its neutral with the layer on, as every composed field.
            # S70 (D234): was `n == "arm_piece_saturation"` with the neutral asserted - the caller names the fields
            # its run leaves neutral, and the production test asserts the cut's neutral itself.
            continue
        assert not np.all(np.asarray(on.fields[n]) == d.neutral), n

    moved_statistics, rounded = set(), set()
    for n, d in on.decls.items():
        if d.composed:
            continue
        # Every field that does not declare itself composed is held to bit-identity, whatever its axes: a field
        # over phi tabulated in a pattern's own frame (P2, P3) will be physics, and is not exempt.
        if d.kind.domain == "object":
            # A catalogue's own columns. A census that no pattern places is the same census, bit for bit. One that
            # a pattern places is the same objects in other rows (drawn ring-first since S61, L1): its columns are
            # compared object by object, matched by their draw, in test_i1_every_placed_object_keeps_every_column_
            # outside_its_placement_set (S70, D234, Audit V F-3-1, #194).
            # S70 (D234): was "**no per-object on/off assertion is made, here or anywhere** (gate G1, Q6: 'with
            # different realised counts the objects do not correspond')" - G1's reason ended at L1.
            if d.of in UNPLACED_OBJECTS:
                assert same(on.fields[n], off.fields[n]), n
            else:
                assert d.of in PLACED_OBJECTS, (n, d.of)
            continue
        if n in NAN_OFF_FIELDS:
            # S61 (D220 part II): the clustering field's seed and cell means - numbers with the layer on, NaN off.
            # S62 (D221): was CLUSTERING_FIELDS - and the gas fluctuation field's seed, ring table and cell normalisers.
            assert d.provenance == "synthetic", n
            assert np.all(np.isfinite(np.asarray(on.fields[n]))) and np.all(np.isnan(np.asarray(off.fields[n]))), n
            assert np.asarray(on.fields[n]).shape == np.asarray(off.fields[n]).shape, n
            continue
        if d.kind.domain == "table":
            # S59 (D218 items 1-2, 7): the layer's table - the layer's own realisation, a table and not a census.
            # Rows with the layer on, none with it off; synthetic, the layer stage's.
            # S60 (D219 item 7): the census of arm pieces (was the winding's 1024 segment rows): as many rows as it
            # lays, every column the same count, none with the layer off ("no arm placed").
            # S62 (D221 item 7 as amended): and the census of gas spurs, its own table and its own row count.
            assert d.of in LAYER_TABLES and d.provenance == "synthetic" and n in pt.PIECE_FIELDS + _SPUR_FIELDS, n
            first = pt.PIECE_FIELDS[0] if d.of == "arm_piece" else _SPUR_FIELDS[0]
            rows = np.asarray(on.fields[first]).size
            # S70 (D234): `empty_tables` - a table a run lays no row of with the layer on (the flocculent `ngc_4414`
            # lays no gas spur at SMALL); every other run's table has rows, as the production run's do.
            assert np.asarray(on.fields[n]).shape == (rows,) and (rows > 0 or d.of in empty_tables), n
            assert np.asarray(off.fields[n]).shape == (0,), n
            continue
        # S56 (D215, gate ruling 5): a synthetic scalar was a realisation - a number with the layer on, and not one
        # with it off. S60 (D219): the five arm modes' phases, the only ones, are retired; every synthetic field is
        # the layer's table's or a cloud census's column, both above.
        assert d.provenance != "synthetic", n
        if n in EXPECTED_TOTALS:
            # S56 (D215 ruling 11): was held to the bit, as every field below is - and it was the same bits until the
            # window was corrected. An expected total is the same to its last place (EXPECTED_TOTALS, above).
            assert same_expected_total(on.fields[n], off.fields[n]), (n, float(on.fields[n]), float(off.fields[n]))
            continue
        if n in RING_FIRST_STATISTICS:
            # S61 (D220 item 4): a statistic of a census drawn ring-first - the same objects on and off, summed in
            # another order - is held to 1e-12, and the ones whose bits differ are named below as measured.
            assert same_ring_first(on.fields[n], off.fields[n]), n
            if not same(on.fields[n], off.fields[n]):
                rounded.add(n)
            continue
        if not same(on.fields[n], off.fields[n]):
            moved_statistics.add(n)
    # Every other field - every radial field, every history, every scalar - is the bit it was, but for the list.
    assert moved_statistics <= set(CENSUS_STATISTICS), sorted(moved_statistics - set(CENSUS_STATISTICS))
    return moved_statistics, rounded


@pytest.mark.parametrize("name", MODELS)
def test_i1_layer_off_moves_only_placements_and_the_listed_census_statistics(runs, name):
    """I1 as amended at gate G1, walked from the declarations: a field is composed because it says so, and what it
    says is the value it must be with the layer off. Nothing here reads an axis."""
    on, off = runs[name, True], runs[name, False]
    moved_statistics, rounded = walk_i1(on, off, name, neutral_on=frozenset({"arm_piece_saturation"}))
    assert np.all(np.asarray(on.fields["arm_piece_saturation"]) == 1.0)  # the cut fires on no ring here (above)
    # And the list is not padded: each entry does move on the production grid at the default seeds.
    # S58 (D217): was `moved_statistics == set(CENSUS_STATISTICS)`. One entry lands on the same bits by rounding at
    # S58's census: `dig_halpha_fraction` is a ratio of two sums over the realised regions that is three tenths in
    # any census, to rounding; the layer-on and the layer-off sums both round to 0.29999999999999993 now, where
    # S57's differed in the last place. It is still a census statistic - a sum over realised objects - and stays listed.
    # S59 (D218): was `== {"dig_halpha_fraction"}`, both sums 0.29999999999999993. The layer-on census is another
    # draw (the clouds follow a response the winding's segments have turned), its sum rounds to 0.30000000000000004,
    # and the entry moves again as it did until S58: all fourteen do.
    # S60 (D219), as at S58 (D217): the pieces' layer-on census rounds its sum to 0.29999999999999993, the layer-off
    # bits, so the entry lands on the same bits again - still a census statistic, still listed, and named here.
    # S60 fourth pass: was `== set()`, all fourteen moving.
    # S61 (D220 item 4): was `== {"dig_halpha_fraction"}` - the cloud census's nine statistics left the list (they are
    # RING_FIRST_STATISTICS); the four left, the star sample's, all move (the bright limit left too, its own build).
    assert set(CENSUS_STATISTICS) - moved_statistics == set(), sorted(set(CENSUS_STATISTICS) - moved_statistics)
    # S61 (D220 item 4): of the nine, these differ in their last bits (sums over the same objects in another order),
    # as measured; the cloud mass, the luminosity function's slope and the [N II] gradient are the same bits.
    assert rounded == {"dig_halpha_fraction", "hot_phase_porosity",
                       *(f"{line}_surface_brightness_hii" for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731"))}, sorted(rounded)
    # S59 (D218 follow-up): the layer-on sum was 0.30000000000000004 - another draw of the census (a segment's pitch
    # relative to the disc's: other rows, other turns), another rounding of three tenths. Layer off: unmoved.
    # S60 fourth pass: was (0.30000000000000016, 0.29999999999999993) - the layer-on value now the layer-off bits.
    # S61 (D220): was (0.29999999999999993, 0.29999999999999993) - the ring-first census, the same regions on and off
    # summed in another order: one rounding of three tenths each.
    assert (float(on.fields["dig_halpha_fraction"]), float(off.fields["dig_halpha_fraction"])) == (0.29999999999999993, 0.30000000000000016)
    # Each entry says which stage publishes it, and that stage is where the model publishes it.
    producer = {d.name: sid for sid in on.order for d in production()[1].get(sid).publishes}
    for n, (stage_id, census, where) in CENSUS_STATISTICS.items():
        assert producer[n] == stage_id and census and where.startswith(("systems.", "planets.", "bright.", "clouds.", "nebular.", "bubbles.")), n
        assert on.decls[n].kind.domain in ("galaxy", "grid") and on.decls[n].axes in ((), ("R",)), n
    # S61 (D220 item 4): was 9 - the four left are scalars; the ten that left were five scalars (the bright limit with
    # the clouds' four) and five radial fields.
    # S61 (D220 item 4): was 4 (the star sample's) - the list is empty; the ring-first list holds nine scalars (was 5).
    assert sum(1 for n in CENSUS_STATISTICS if on.decls[n].kind.domain == "galaxy") == 0
    assert sum(1 for n in RING_FIRST_STATISTICS if on.decls[n].kind.domain == "galaxy") == 9
    for n, (stage_id, census, where) in RING_FIRST_STATISTICS.items():
        assert producer[n] == stage_id and where.startswith(("systems.", "planets.", "bright.", "clouds.", "nebular.", "bubbles.")), n
    # The expected totals, as measured at the default seeds: the clouds' is one unit in the last place higher with
    # the layer on, the bright stars' the same bits. Neither is a census statistic, and the list is not widened.
    # I1 reads "equal within four units in the last place" (S58, D217's follow-up at the gate); this test holds them
    # to that margin (EXPECTED_TOTAL_MARGIN) and pins the measured one in the test after this.
    # S70 (D234, Audit V F-3-11): struck - "I1 as amended at gate G2 (S57, D216 item 11 ii): 'equal within one unit
    # in the last place ...' - the rule's own wording now, and held" and "the test pins the measured two
    # (EXPECTED_TOTAL_UNITS)": G2's one unit was re-worded at S58, and the measured count is one.
    assert not EXPECTED_TOTALS & set(CENSUS_STATISTICS)
    # S57 (D216): was 16693.43298750999 with the layer on (one unit lower than off, on S56's ranked ridge); the
    # layer-off value is S55's own bits, unmoved.
    # S58 (D217): was 16693.432987509997 with the layer on, one unit above the layer-off value; two units now
    # (EXPECTED_TOTALS, above: reported). The layer-off value is S55's own bits, unmoved.
    # S59 (D218): was 16693.43298751 with the layer on, two units above the layer-off value; one unit now
    # (EXPECTED_TOTALS, above), on rings the winding's segments have turned. The layer-off value is S55's own bits,
    # unmoved; the bright stars' expected total is the same bits on and off (0 units), as before. I1 as now worded,
    # "equal within four units in the last place", holds for both: measured 1 and 0.
    # S59 (D218 follow-up): was 16693.432987509997 with the layer on, one unit above the layer-off value; two units
    # now, 16693.43298751 - the reading S58 had - on rings turned by segments whose pitch is relative to the disc's.
    # The layer-off value is S55's own bits, unmoved; the bright stars' total is the same bits on and off (0 units).
    # I1's "within four units" holds for both: measured 2 and 0.
    # S60 (D219): the layer-on bits are the pieces' rounding now (measured one unit above the layer-off value on
    # the third pass) and are pinned apart, in the test after this one, awaiting the re-pin; the layer-off value
    # is S55's own bits, unmoved, and the bound is held here.
    assert float(off.fields["cloud_count_total"]) == 16693.432987509994
    assert same_expected_total(on.fields["cloud_count_total"], off.fields["cloud_count_total"])
    assert same(on.fields["bright_star_count_1e3"], off.fields["bright_star_count_1e3"])


@pytest.mark.parametrize("case", ["production", "ngc_4414 SMALL"])
def test_i1_the_placement_weights_average_to_1_on_every_ring_to_1e_13(runs, variants, prod, case):
    """S70 (D234, Audit V F-3-11): I1's clause "the rounding of sums over the cells of weights that average to 1 to
    1e-13", asserted ring by ring (until S70 it was asserted nowhere; the nearest was the composed fields' ring means
    at 1e-12 on SMALL). The weights the two expected totals sum: the clouds' sector weights
    (clouds.sector_placement), which ``cloud_count_total`` sums, and the bright catalogue's two parts'
    (``BrightGalaxy.weights``: the middle part's - the young stars' share placed by ``sfr_modulation`` through
    ``young_reader`` - and the old part's, the stellar pattern's contrast), which ``bright_star_count_1e3`` sums
    (``BrightGalaxy.expected``, bright.py). S70 fix pass (the independent reviewer): was the star sample's
    stellar-pattern weights (``systems._sector_weights``) in the bright total's place - weights that total does not
    sum, without the young stars' part. Measured at S70: the clouds' at most 6.0e-15 off 1 on the production run;
    the bright parts' at most 2.2e-16 on SMALL at both templates (the reviewer's reading) - it holds, held here."""
    out = runs[DEFAULT_MODEL, True] if case == "production" else variants[case][0]
    F, R = out.fields, out.grid.R
    c = constants(prod[0].get(DEFAULT_MODEL))
    _, clouds = cl.sector_placement(F, R, c)
    g = br.BrightGalaxy(F, R, out.grid.t, float(out.grid.spec.t_max), int(out.grid.spec.n_t), c)
    assert clouds.shape == (cl.CELL_RINGS, cl.CELL_SECTORS) and g.modulation is not None
    assert np.asarray(g.weights).shape == (2, g.area.size, g.sector_lo.size)
    for weights in (clouds, *np.asarray(g.weights)):
        assert float(np.abs(weights.mean(axis=1) - 1.0).max()) < 1e-13


@pytest.mark.parametrize("name", MODELS)
def test_the_clouds_expected_total_s_layer_on_bits_as_measured(runs, name):
    """The layer-on bits of ``cloud_count_total`` as measured on the final model (S60, D219: one unit in the last
    place above the layer-off value, S55's bits; S59's follow-up read two). The bound is test_i1's; the bits are the
    layer's rounding of the cells' exact means, and move with the pattern they are the means of."""
    on, off = runs[name, True], runs[name, False]
    # S60 fourth pass: was 16693.43298751 (two units above the layer-off value).
    assert float(on.fields["cloud_count_total"]) == 16693.432987509997
    # S59 (D218 follow-up): was `== np.nextafter(off, inf)`, one step; two steps then.
    # S60 fourth pass: was two steps; one step now, as before S59's follow-up.
    assert float(on.fields["cloud_count_total"]) == np.nextafter(float(off.fields["cloud_count_total"]), np.inf)
    for n in EXPECTED_TOTALS:
        apart = abs(float(on.fields[n]) - float(off.fields[n])) / float(np.spacing(max(abs(float(on.fields[n])), abs(float(off.fields[n])))))
        # S59 (D218 follow-up): the clouds' was 1.0. S60 fourth pass: was 2.0.
        assert apart == {"cloud_count_total": 1.0, "bright_star_count_1e3": 0.0}[n] and apart <= EXPECTED_TOTAL_BOUND, (n, apart)
    # S59 (D218, the gate): "every `arm_mode_amplitude_m` bit-identical layer on and off" - radial fields of the
    # pattern stage, held by the walk above with every other field; named here because the gate names them.
    # S60 fourth pass: was `n not in moved_statistics and ...` - a name of test_i1's walk, left behind when these
    # lines were set apart under the xfail (a NameError, hidden by it); the walk's own statement is test_i1's.
    for n in pt.AMPLITUDE_FIELDS:
        assert n not in CENSUS_STATISTICS and same(on.fields[n], off.fields[n]) and np.asarray(on.fields[n]).any(), n


def test_i1_holds_an_undeclared_phi_field_to_bit_identity_and_a_declared_one_to_its_neutral(prod):
    """The case the axes rule got wrong (gate G1, F12): a phi-axis field that is physics - tabulated in a pattern's
    own frame, P2's and P3's - is not composed, and is the same bits with the layer on or off; and a composed field
    need not be 1 when the layer is off: it is whatever its declaration says."""
    def physics(ctx):
        return {"frame_field": np.cos(ctx.grid.phi)[None, :] * (1.0 + ctx.grid.R)[:, None]}

    def composing(ctx):
        cells = (ctx.grid.R.size, ctx.grid.phi.size)
        return {"placed_field": compose.field(ctx.fields, PLACED, cells, lambda: 2.0 + np.sin(ctx.grid.phi)[None, :] * np.ones(cells))}

    PLACED = decl("placed_field", axes=("R", "phi"), composed=True, neutral=2.0)
    frame = decl("frame_field", axes=("R", "phi"))
    assert not frame.composed and frame.neutral is None and PLACED.composed and PLACED.neutral == 2.0
    a, b = stage("frame", (frame,), compute=physics), stage("placing", (PLACED,), compute=composing)
    assert not a.composes and not a.may_place and b.composes
    m, table = model("m", a, b), production()[2]
    on = run(m, grid=SMALL, impls=impls(a, b), table=table, layer=True)
    off = run(m, grid=SMALL, impls=impls(a, b), table=table, layer=False)
    assert same(on.fields["frame_field"], off.fields["frame_field"]) and np.ptp(on.fields["frame_field"]) > 0
    assert np.all(off.fields["placed_field"] == 2.0) and not np.all(on.fields["placed_field"] == 2.0)
    # A stage cannot compose a field that does not declare it: compose refuses, layer on or off (the stage is given
    # a census's standing here so that it is the declaration compose refuses, not the stage).
    undeclared = stage("frame", (frame,), placement_reader=True,
                       compute=lambda ctx: {"frame_field": compose.field(ctx.fields, frame, (1,), lambda: np.ones(1))})
    for layer in (True, False):
        with pytest.raises(LayerError, match="not declared composed"):
            run(model("m", undeclared), grid=SMALL, impls=impls(undeclared), table=table, layer=layer)


@pytest.mark.parametrize("name", MODELS)
def test_i1_every_scalar_of_the_pattern_stages_is_unchanged(runs, prod, name):
    """D214 section 1: "every scalar the bar, pattern and gas_pattern stages publish ... is unchanged: those are
    laws and measured scatters, and they are still drawn. What is switched off is where the arms are\""""
    on, off = runs[name, True], runs[name, False]
    _, impls_, _ = prod
    scalars = [d.name for sid in ("bar", "pattern", "gas_pattern") for d in impls_.get(sid).publishes if d.kind.domain == "galaxy"]
    # S58 (D217): was 14 - the bar's formation time, the verdict, the body's three shape numbers and its mass share.
    # S59 (D218): was 20 - the radius the winding is anchored at, the pitch as the law draws it, the Sun's azimuth.
    # S59 (D218 follow-up): was 23 - the spread of a segment's pitch over the disc's, the `bar` stage's: a law's number.
    # S60 (D219 items 1 and 3): was 24 - the anchor and the spread are retired with the common winding, and the
    # `bar` stage publishes the arm class, a law of the bar (or a template's pin).
    assert len(scalars) == 23 and {"arm_multiplicity", "pitch_angle", "arm_contrast", "bar_contrast", "gas_arm_contrast",
                                   "bar_pattern_speed", "bar_formation_time", "bar_present", "bar_mass_share",
                                   "pitch_angle_drawn", "sun_azimuth", "arm_class"} <= set(scalars)
    for n in scalars:
        # S59 (D218 item 5): was `on.fields[n] == off.fields[n]` for all - the Sun's azimuth is not a number in a
        # galaxy no template places an observer in (the default), and NaN is not equal to itself: the same on and
        # off all the same, bit for bit. Every other scalar is a number, or a label, and equal as it was.
        if n == "sun_azimuth":
            assert np.isnan(on.fields[n]) and np.isnan(off.fields[n]) and same(on.fields[n], off.fields[n]), n
            continue
        assert on.fields[n] == off.fields[n], n
    assert on.fields["pitch_angle_drawn"] == on.fields["pitch_angle"]
    # S56 (D215, gate ruling 5): and the law of several modes - the five amplitudes and the saturation, radial
    # fields of the pattern stage - is the same bits: "with the layer off the texture_seed stream is never drawn,
    # and the five amplitudes, arm_multiplicity and arm_saturation are bit-identical".
    # S60 (D219 items 1 and 4): and the two radial laws made from the amplitudes - the ring's budget of arm power
    # and the arm number the law counts - and the `bar` stage's two, the pattern speed and the width of a piece.
    radial = [d.name for d in impls_.get("pattern").publishes if d.axes == ("R",)]
    assert radial == [*pt.AMPLITUDE_FIELDS, "arm_saturation", "arm_design_count", "arm_power_budget"]
    assert [d.name for d in impls_.get("bar").publishes if d.axes == ("R",)] == ["arm_pattern_speed", "arm_piece_width"]
    for n in (*radial, "arm_pattern_speed", "arm_piece_width"):
        assert same(on.fields[n], off.fields[n]) and np.all(np.isfinite(on.fields[n])), n


def test_i1_the_layer_off_run_is_reproducible_and_its_determinism_is_a_spec(prod):
    from galaxy.specs import determinism

    models, impls_, table = prod
    assert set(determinism.LAYERS) == {True, False}
    for m in models:
        assert determinism.check_reproducible(m, impls_, table, layer=False) == []
    text = determinism.report([models.get(DEFAULT_MODEL)], impls_, table)
    assert f"model {DEFAULT_MODEL}, layer on: reproducible OK" in text
    assert f"model {DEFAULT_MODEL}, layer off: reproducible OK" in text
    assert f"model {DEFAULT_MODEL}, layer off: reproducible across processes" in text and "FAIL" not in text


# --- I1, object by object: a placed census keeps every column outside its placement set (S70, D234; #194) ----------

# S70 (D234, Audit V F-3-1, the audit's chief finding; F-3-2): the runs the per-object test, the walk and the realised
# totals are read at besides the production pair - the second template (`ngc_4414`: unbarred, flocculent, its own
# texture seed) and a non-default seed pair on the Milky Way, each layer on and off on the SMALL grid, and a
# `texture_seed` reroll of the production run (two realisations, both layer on: BUILD_III 1c rule 1).
OTHER_SEEDS = {"systems_seed": 3, "texture_seed": 777}
REROLLED_TEXTURE = 987654321
# The columns of a placed catalogue that name another row, not a property of the object: compared by what they name.
# `cloud_cluster_index` is its cluster's index among its *cell's* clusters (clouds.cluster_indices), -1 for none - a
# row reference into a cell the layer chooses, so its number differs on and off for about half the hosting clouds
# while the cloud holds the same cluster. Held here: whether the cloud holds one, bit for bit, on and off; and, in
# each run, that the index names the cluster drawn for that cloud - it is resolved against the cell's drawn order
# (object_names; S70 fix pass, the independent reviewer: until then "names the one drawn for it" was claimed here
# and only `>= 0` compared). **Reported at S70 (D234)**: not a placement column and not declared one.
ROW_REFERENCES = {"cloud_cluster_index": "cluster"}


@pytest.fixture(scope="module")
def variants(prod, runs):
    """{case: (run a, run b)}: a against b is the layer on against off, or two texture seeds with the layer on."""
    m = prod[0].get(DEFAULT_MODEL)
    ngc = templates.overrides(templates.TEMPLATES["ngc_4414"])
    return {
        "ngc_4414 SMALL": (run(m, ngc, SMALL, layer=True), run(m, ngc, SMALL, layer=False)),
        "milky_way SMALL seeds 3/777": (run(m, OTHER_SEEDS, SMALL, layer=True), run(m, OTHER_SEEDS, SMALL, layer=False)),
        "milky_way texture reroll": (runs[DEFAULT_MODEL, True], run(m, {"texture_seed": REROLLED_TEXTURE}, layer=True)),
    }


def placement_sets(out) -> dict[str, set[str]]:
    """Each object class's placement set, read from the declarations (``FieldDecl.placement``) and nowhere else."""
    classes = {d.of for d in out.decls.values() if d.kind.domain == "object"}
    return {c: {n for n, d in out.decls.items() if d.kind.domain == "object" and d.of == c and d.placement} for c in classes}


def object_names(out, m) -> dict[str, np.ndarray]:
    """Each placed census's rows named by their draw: one int64 per row, the same object's on and off and under any
    texture seed. A cloud is (its drawn level-0 ring, its place in the ring's draw), read from the census's own layout
    (``clouds.cloud_layout``, which the stage materialises by); a cluster its cloud's; a star (ring, place) from
    ``systems.star_layout``; a planet its star's and its place among the star's planets. The bright catalogue is
    named apart (:func:`bright_names`)."""
    F, c = out.fields, constants(m)
    seed = int(out.inputs["systems_seed"])
    clouds = cl.cloud_layout(F, out.grid.R, seed, c)
    assert clouds.index.size == len(F["cloud_mass"]) and int(clouds.index.max()) < 10**7
    cloud = clouds.ring * 10**7 + clouds.index
    hosts = np.asarray(F["cloud_cluster_index"]) >= 0
    # S70 fix pass (the independent reviewer; ROW_REFERENCES): the reference resolved, run by run - each cloud's
    # `cloud_cluster_index` is its cluster's place among the hosting clouds of its own cell, in the cell's drawn
    # order (clouds.cluster_indices on the cell's `cloud_state` rows, the cells as this run's layout counts them),
    # so the index names the cluster drawn for that cloud and no other in the cell. Until this pass only `>= 0` was
    # compared, and an index the layer pointed at another cluster of the cell passed.
    offsets = np.cumsum([0, *(n for _, n in clouds.counts)])
    state = np.asarray(F["cloud_state"])
    resolved = [cl.cluster_indices(state[o:o + n]) for o, (_, n) in zip(offsets, clouds.counts)]
    assert offsets[-1] == state.size and same(np.concatenate(resolved), np.asarray(F["cloud_cluster_index"]))
    stars = sy.star_layout(F, out.grid.R, out.grid.t, seed, sy.CATALOGUE_SAMPLE,
                           migration=float(out.inputs["migration_efficiency"]), constants=c)
    assert stars.index.size == len(F["star_mass"]) and np.all(stars.level == 0)
    star = stars.ring * 10**7 + stars.index
    per = np.asarray(F["star_planet_count"]).astype(np.int64)
    assert per.sum() == len(F["planet_mass"]) and int(per.max(initial=0)) < 100
    place = np.arange(per.sum()) - np.repeat(np.cumsum(per) - per, per)
    return {"cloud": cloud, "cluster": cloud[hosts], "star": star, "planet": np.repeat(star, per) * 100 + place}


def bright_names(out, m) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """The bright catalogue's columns and its rows' names. The stage publishes its default selection's columns and
    not the rows' identity, so the selection is made again here from the run's fields (the stage's own call) and held
    to be the published columns bit for bit; a star is then named by its level-0 ring and its place in the ring's
    ordered process - its Gamma, which is strictly increasing round the ring, so it names the place ``i`` exactly."""
    galaxy = br.BrightGalaxy(out.fields, out.grid.R, out.grid.t, float(out.grid.spec.t_max), int(out.grid.spec.n_t), constants(m))
    chosen, _ = br.select_brightest(galaxy, int(out.inputs["systems_seed"]), br.all_cells(), br.DEFAULT_SELECTION)
    columns = {d.name: np.asarray(chosen[d.name]) for d in br.COLUMNS}
    for n, v in columns.items():
        assert same(v, out.fields[n]), n
    ring = galaxy.ring_of(np.asarray(chosen["cell"], dtype=np.int64)).astype(np.int64)
    gamma = np.asarray(chosen["gamma"], dtype=float)
    # (ring, Gamma) as one sortable int64: the ring, then Gamma's rank among all the catalogue's Gammas (the same
    # stars on and off hold the same Gammas, so the same ranks).
    key = ring * 10**7 + np.searchsorted(np.unique(gamma), gamma).astype(np.int64)
    assert np.unique(key).size == key.size
    return columns, key


def matched(key_a: np.ndarray, key_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The row orders that put the same objects side by side; the two runs must hold the same objects."""
    ia, ib = np.argsort(key_a, kind="stable"), np.argsort(key_b, kind="stable")
    assert np.unique(key_a).size == key_a.size and np.array_equal(key_a[ia], key_b[ib]), "the runs' objects differ"
    return ia, ib


def moved_columns(a, b, m) -> dict[str, set[str]]:
    """Every placed census's columns that are not the same bits object by object between runs ``a`` and ``b``, by
    class; the row references compared by what they name (ROW_REFERENCES). Asserts the objects are the same."""
    names = {True: object_names(a, m), False: object_names(b, m)}
    moved: dict[str, set[str]] = {}
    for census in PLACED_OBJECTS - {"bright_star"}:
        ia, ib = matched(names[True][census], names[False][census])
        assert ia.size > 0, census
        moved[census] = set()
        for n, d in a.decls.items():
            if d.kind.domain != "object" or d.of != census:
                continue
            x, y = np.asarray(a.fields[n])[ia], np.asarray(b.fields[n])[ib]
            if n in ROW_REFERENCES:
                # What the reference names: whether the cloud holds a cluster; that the index names the cluster drawn
                # for that cloud is asserted in each run by object_names, against the run's own layout.
                x, y = x >= 0, y >= 0
            if not same(x, y):
                moved[census].add(n)
    (ca, ka), (cb, kb) = bright_names(a, m), bright_names(b, m)
    ia, ib = matched(ka, kb)
    moved["bright_star"] = {n for n in ca if not same(ca[n][ia], cb[n][ib])}
    return moved


def hold_objects(a, b, m) -> None:
    """The per-object statement of I1 (and of rule 1 for two texture seeds): the same objects, and every column outside
    the declared placement set the same bits; the set is not padded - each column in it does move."""
    declared = placement_sets(a)
    assert declared == placement_sets(b)
    moved = moved_columns(a, b, m)
    assert set(moved) == PLACED_OBJECTS
    for census, columns in moved.items():
        assert columns <= declared[census], (census, sorted(columns - declared[census]))
        assert columns == declared[census], (census, "declared but not moved", sorted(declared[census] - columns))


def test_the_placement_sets_are_declared_on_the_census_columns(runs):
    """S70 (D234, Audit V F-3-1 as ruled at gate G4: "the declared placement set is written into each census's
    FieldDecl ... so the test reads it, not a list in the test"). Read from the declarations: the columns the layer
    may move - where an object stands and the layer's own texture of a cloud - and no other. A synthetic column of a
    placed census is in its set (the layer draws it); an unplaced census, a field, a scalar or a table takes none."""
    out = runs[DEFAULT_MODEL, True]
    declared = placement_sets(out)
    assert declared == {
        "cloud": {"cloud_radius", "cloud_azimuth", *cl.TEXTURE_COLUMNS},
        "cluster": {"cluster_radius", "cluster_azimuth"},
        "star": {"star_azimuth"},
        "planet": set(),
        "bright_star": {"bright_star_radius", "bright_star_azimuth"},
        "remnant": set(),
    }, declared
    for n, d in out.decls.items():
        assert not d.placement or (d.kind.domain == "object" and d.of in PLACED_OBJECTS), n
        if d.kind.domain == "object" and d.provenance == "synthetic":
            assert d.placement, n
    assert not set(ROW_REFERENCES) & {n for s in declared.values() for n in s}
    base = dict(name="f", label="f", unit="dimensionless", about="a test field")
    with pytest.raises(DeclarationError, match="placement column is a placed catalogue's column"):
        FieldDecl(**base, kind=Kind.SCALAR, placement=True)
    with pytest.raises(DeclarationError, match="placement is True or False"):
        FieldDecl(**base, kind=Kind.COLUMN, of="cloud", ramp=Ramp("greys"), placement=1)
    assert FieldDecl(**base, kind=Kind.COLUMN, of="cloud", ramp=Ramp("greys"), placement=True).contract() != \
        FieldDecl(**base, kind=Kind.COLUMN, of="cloud", ramp=Ramp("greys")).contract()


@pytest.mark.parametrize("name", MODELS)
def test_i1_every_placed_object_keeps_every_column_outside_its_placement_set(runs, prod, name):
    """S70 (D234, Audit V F-3-1, #194): the production pair at the default seeds, both models. Every placed census's
    objects - clouds, clusters (with their HII regions and bubbles, columns of the cluster class), the star sample,
    its planets and the bright catalogue - matched on and off by their draw, and every column outside the census's
    declared placement set the same bits: a layer-on change to a cloud's velocity dispersion, its alpha or a star's
    metallicity fails here (it passed I1's walk, I2's sums and rule 1 until S70). The API's derived per-cloud
    columns (``cloud_dust_extinction_v``, ``cloud_axis_ratio``, ``cloud_angle``; model/galaxy/api/v6_clouds.py) are
    functions of the placement columns and the header's rule, declared nowhere as fields, and are held by
    tests/test_v6_clouds.py's closure tests, not here."""
    hold_objects(runs[name, True], runs[name, False], prod[0].get(name))


@pytest.mark.parametrize("case", ["ngc_4414 SMALL", "milky_way SMALL seeds 3/777", "milky_way texture reroll"])
def test_i1_every_placed_object_keeps_its_columns_at_another_template_seed_and_texture(variants, prod, case):
    """The same at the second template, at a non-default (systems_seed, texture_seed) pair, and between two texture
    seeds with the layer on - rule 1, "rerolling it changes placements and texture and nothing else", object by
    object."""
    hold_objects(*variants[case], prod[0].get(DEFAULT_MODEL))


@pytest.mark.parametrize("case", ["ngc_4414 SMALL", "milky_way SMALL seeds 3/777"])
def test_i1_the_walk_holds_at_another_template_and_seed(variants, case):
    """S70 (D234, Audit V F-3-2): I1's walk over every declared field at the second template and a second seed pair
    (it ran at the Milky Way's default seeds alone until S70). The bar's lanes are neutral in a galaxy with no bar,
    and the pieces' cut may or may not fire. The saturation cut (``arm_saturation``) fires on 0 of 48 rings at both
    SMALL runs and nowhere at production, so the walk does not exercise it (measured by the independent reviewer at
    S70; the lead records it as a debt)."""
    on, off = variants[case]
    unbarred = not np.isfinite(float(on.fields["bar_half_length"]))
    neutral = {"arm_piece_saturation"} | ({"star_formation_gas_contrast"} if unbarred else set())
    # The flocculent galaxy lays no gas spur at SMALL (its chains are short: measured 0 rows, layer on).
    empty = {"gas_spur"} if case.startswith("ngc_4414") else set()
    moved, rounded = walk_i1(on, off, DEFAULT_MODEL, neutral_on=frozenset(neutral), empty_tables=frozenset(empty))
    assert moved == set() and rounded <= set(RING_FIRST_STATISTICS)


@pytest.mark.parametrize("case", ["ngc_4414 SMALL", "milky_way SMALL seeds 3/777"])
def test_i4_a_composing_stage_s_other_outputs_are_the_same_on_and_off(variants, prod, case):
    """S70 (D234, Audit V F-3-6): publishing one composed field lends a stage the right to read the layer for all it
    requires, so its non-composed outputs - `gas_pattern`'s scalars and radial fields, the composing stages' laws - could
    carry the layer to any physics stage the graph does not trace. Held here, at the second template and seed: every
    field a composing stage publishes and does not declare composed is the same bits on and off. (The graph route -
    propagating "layer-dependent" through the composing stages - is not taken: this test is the cheaper close, G4.)"""
    on, off = variants[case]
    models, impls_, table = prod
    g = graph.analyse(models.get(DEFAULT_MODEL), impls_, table)
    outputs = [d for st in g.order if st.id in g.composing_stages for d in st.publishes if not d.composed]
    assert {st for st in g.composing_stages} >= {"stellar_pattern", "gas_pattern"} and len(outputs) > 5
    for d in outputs:
        assert same(on.fields[d.name], off.fields[d.name]), (case, d.name)


def test_the_per_object_test_sees_a_moved_column(runs, prod):
    """The instrument: a column outside every placement set, perturbed by one unit in its last place on one cloud of
    the layer-on run, is caught - so a green per-object test is a measurement, not a walk that compares nothing."""
    on, off = runs[DEFAULT_MODEL, True], runs[DEFAULT_MODEL, False]
    m = prod[0].get(DEFAULT_MODEL)
    sigma = np.asarray(on.fields["cloud_velocity_dispersion"]).copy()
    sigma[len(sigma) // 2] = np.nextafter(sigma[len(sigma) // 2], np.inf)
    nudged = replace(on, fields=Fields({**on.fields, "cloud_velocity_dispersion": sigma}, layer=True))
    moved = moved_columns(nudged, off, m)
    assert moved["cloud"] == placement_sets(on)["cloud"] | {"cloud_velocity_dispersion"}
    with pytest.raises(AssertionError, match="cloud_velocity_dispersion"):
        hold_objects(nudged, off, m)


# --- I2: a census's expected count per ring does not know the layer ------------------------------------------------


def ring_expectations(out, m) -> dict[str, np.ndarray]:
    """What each census's draw is given, summed round each ring: the number of objects a ring expects."""
    F, R, c = out.fields, out.grid.R, constants(m)
    spec_ = out.grid.spec
    # S70 (D234, Audit V F-3-4): was the test's own arithmetic - the sample times each cell's share times the stellar
    # pattern's sector weights, summed round the ring - which never saw the young stars' placement by
    # `sfr_modulation`. The stars' expectation is now the number the stage hands `ring_star_count` (systems._layout):
    # `ring_star_expected` of the stellar surface density, the same function the stage calls.
    stars = sy.ring_star_expected(F["stellar_surface_density"], R, sy.CATALOGUE_SAMPLE)
    galaxy = br.BrightGalaxy(F, R, out.grid.t, float(spec_.t_max), int(spec_.n_t), c)
    ring, _ = galaxy.locate(br.all_cells())
    rings = int(ring.max()) + 1
    return {
        "stars": np.asarray(stars, dtype=float),
        "clouds": cl.expected_counts(F, R, c).sum(axis=1),
        "remnants": bb.remnant_expected(F, R, c).sum(axis=1),
        **{f"bright stars above 10^{x:g} Lsun": np.bincount(ring, weights=galaxy.expected(br.all_cells(), x), minlength=rings)
           for x in (3.0, 4.5)},
    }


@pytest.mark.parametrize("name", MODELS)
def test_i2_each_census_expects_the_same_count_in_every_ring(runs, prod, name):
    """"A census's expected counts per ring are identical with the layer on or off; only placements differ": the
    number handed to the draw, summed round the ring, to 1e-12 of itself - the placement weights average to 1."""
    m = prod[0].get(name)
    on, off = ring_expectations(runs[name, True], m), ring_expectations(runs[name, False], m)
    assert set(on) == set(off)
    for census in on:
        a, b = on[census], off[census]
        assert a.shape == b.shape and np.all(np.isfinite(a)) and a.sum() > 0, census
        assert np.allclose(a, b, rtol=1e-12, atol=0.0), (census, float(np.max(np.abs(a - b) / np.where(b > 0, b, 1.0))))
    # The clusters are their clouds' (one per cloud past its embedded phase): no count of their own to expect.
    # And the realised counts differ by the draw alone: prediction (d), the cloud count within 3% of 16 822.
    n_on, n_off = len(runs[name, True].fields["cloud_radius"]), len(runs[name, False].fields["cloud_radius"])
    # S56 (D215): was n_on == 16822 - S51's census, placed by one four-armed ridge; placed by five modes' ridge it
    # is another draw. The layer-off census is S55's own (16 754), and the two still differ by the draw alone.
    # S57 (D216): was n_on == 16660 - placed by the gas's steady response to the modes it is another draw again.
    # S58 (D217): was n_on == 16667 - placed by the response and the bar's lanes, the two-armed mode on the bar's
    # axis, it is another draw again. The layer-off census is S55's own still.
    # S59 (D218): was n_on == 16668 - placed by a response the winding's segments have turned ring by ring, it is
    # another draw again (each cell another expectation, each ring the same one: the loop above). Layer off: S55's.
    # S59 (D218 follow-up): was n_on == 16708 - a segment's pitch is relative to the disc's and the rows are other
    # rows, so the rings are turned by other phases: another draw again. Layer off: S55's, unmoved.
    # S60 (D219): the layer-on count is the pieces' census's and is pinned apart (the test after this one, awaiting
    # the re-pin); the layer-off census is S55's own, unmoved, and the two differ by the draw alone.
    # S61 (D220 items 1 and 10): was n_off == 16754 and the two differing by the draw alone. Drawn ring-first, each
    # ring's count is one draw at the ring's expected total, which no placement enters: the same count on and off.
    assert n_off == 16577 and abs(n_off / 16822 - 1.0) < 0.03 and n_on == n_off, (n_on, n_off)


@pytest.mark.parametrize("name", MODELS)
def test_the_layer_on_cloud_count_as_measured(runs, name):
    """The realised layer-on cloud count as measured on the final model (S60, D219): placed by the arms' census it
    is another draw each time the pattern moves; the invariant is test_i2's."""
    # S61 (D220): was 16753 (S60 fourth pass: was 16713) - drawn ring-first, the layer-off count.
    assert len(runs[name, True].fields["cloud_radius"]) == 16577 == len(runs[name, False].fields["cloud_radius"])


@pytest.mark.parametrize("name", MODELS)
def test_i2_the_realised_ring_totals_are_the_same_on_and_off(runs, prod, name):
    """S61 (D220 item 4; I2's second half, BUILD_III section 1d): drawn ring-first, a ring's clouds are the same
    clouds with the layer on or off, and only their sector and azimuth differ. So every realised ring total is the
    same: the clouds' count and mass, the clusters' count and mass, the HII regions' Halpha and the bubbles' volumes -
    bit for bit for the counts, to 1e-12 relative for the sums (the objects are concatenated cell by cell, so a sum's
    order differs). A cluster's ring is its cloud's, the ring of its draw."""
    hold_cloud_ring_totals(runs[name, True], runs[name, False], prod[0].get(name))


@pytest.mark.parametrize("case", ["ngc_4414 SMALL", "milky_way SMALL seeds 3/777", "milky_way texture reroll"])
def test_i2_the_realised_ring_totals_hold_at_another_template_seed_and_texture(variants, prod, case):
    """S70 (D234, Audit V F-3-2): the clouds', clusters', regions' and bubbles' ring totals and the star sample's and
    its planets' at the second template, a second seed pair and a texture reroll (the production pair's tests above
    ran alone until S70; `ngc_4414` was read on expectations only)."""
    a, b = variants[case]
    m = prod[0].get(DEFAULT_MODEL)
    # The smaller disc holds clouds in 20 of the 32 cell rings (measured at S70 on SMALL), the Milky Way in more than 20.
    rings = 20 if case.startswith("ngc_4414") else 21
    hold_cloud_ring_totals(a, b, m, min_rings=rings)
    hold_star_ring_totals(a, b, m, min_rings=rings)


def hold_cloud_ring_totals(on, off, m, min_rings: int = 21) -> None:
    """The realised ring totals of the cloud census and what is made of it, the same in two runs (test_i2 above)."""
    c = constants(m)
    totals = {}
    for layer, out in ((True, on), (False, off)):
        F = out.fields
        layout = cl.cloud_layout(F, out.grid.R, int(out.inputs["systems_seed"]), c)
        ring = layout.ring
        hosts = ring[np.asarray(F["cloud_cluster_index"]) >= 0]
        assert ring.size == len(F["cloud_mass"]) and hosts.size == len(F["cluster_mass"])

        def per(where, weight=None):
            return np.bincount(where, weights=None if weight is None else np.asarray(weight, dtype=float), minlength=cl.CELL_RINGS)

        totals[layer] = {
            "cloud count": per(ring), "cloud mass": per(ring, F["cloud_mass"]),
            "cluster count": per(hosts), "cluster mass": per(hosts, F["cluster_mass"]),
            "HII Halpha": per(hosts, F["hii_halpha_luminosity"]),
            "bubble volume": per(hosts, 4.0 / 3.0 * np.pi * np.nan_to_num(np.asarray(F["bubble_radius"], dtype=float)) ** 3),
        }
    for k, a in totals[True].items():
        b = totals[False][k]
        assert a.sum() > 0 and np.count_nonzero(a) >= min_rings, k
        if k.endswith("count"):
            assert np.array_equal(a, b), k
        else:
            assert np.allclose(a, b, rtol=1e-12, atol=0.0), (k, float(np.max(np.abs(a - b) / np.where(b > 0, b, 1.0))))
    # And the placement does differ: the clouds stand in other cells.
    assert not same(on.fields["cloud_azimuth"], off.fields["cloud_azimuth"])


@pytest.mark.parametrize("name", MODELS)
def test_i2_the_star_sample_s_ring_totals_and_its_planets_are_the_same_on_and_off(runs, prod, name):
    """S61 (D220 items 1-4, the star sample's build): drawn ring-first, a ring's stars are the same stars with the
    layer on or off - its count one seeded rounding of the ring's expectation, every per-star draw an array on the
    ring's stream - and only their sector and azimuth differ; a star's planets are keyed on its place in its ring's
    draw. So the realised per-ring totals are the same: the stars' count and mass, the planets' count and mass, the
    stars with a giant - bit for bit for the counts, to 1e-12 for the sums (the rows are concatenated cell by cell).
    And the stage's four statistics are the same bits."""
    m = prod[0].get(name)
    hold_star_ring_totals(runs[name, True], runs[name, False], m)
    # S61 (D220 item 8, the lead's ruling (a)): below level 0 the unit is the whole sub-ring (below).
    hold_sub_rings(runs, name, m)


def hold_star_ring_totals(on, off, m, min_rings: int = 21) -> None:
    """The star sample's and its planets' realised ring totals and the stage's four statistics, the same in two runs."""
    totals = {}
    for layer, out in ((True, on), (False, off)):
        F = out.fields
        layout = sy.star_layout(F, out.grid.R, out.grid.t, int(out.inputs["systems_seed"]), sy.CATALOGUE_SAMPLE,
                                migration=float(out.inputs["migration_efficiency"]), constants=constants(m))
        ring = layout.ring
        per_star = np.asarray(F["star_planet_count"]).astype(np.int64)
        assert ring.size == len(F["star_mass"]) == per_star.size and np.all(layout.level == 0)
        host = np.repeat(ring, per_star)
        giant = np.zeros(per_star.size, dtype=bool)
        hydrogen = np.flatnonzero(np.asarray(F["planet_atmosphere"]) == pl.ATMOSPHERES.index("hydrogen"))
        giant[np.unique(np.repeat(np.arange(per_star.size), per_star)[hydrogen])] = True

        def per(where, weight=None):
            return np.bincount(where, weights=None if weight is None else np.asarray(weight, dtype=float), minlength=sy.CELL_RINGS)

        totals[layer] = {
            "star count": per(ring), "star mass": per(ring, F["star_mass"]), "star age": per(ring, F["star_age"]),
            "planet count": per(host), "planet mass": per(host, F["planet_mass"]), "stars with a giant": per(ring[giant]),
        }
    for k, a in totals[True].items():
        b = totals[False][k]
        # (the giants stand in the inner rings, where the metals are: 15 rings hold one)
        assert a.sum() > 0 and np.count_nonzero(a) > (10 if k.endswith("giant") else min_rings - 1), k
        if k.endswith(("count", "giant")):
            assert np.array_equal(a, b), k
        else:
            assert np.allclose(a, b, rtol=1e-12, atol=0.0), (k, float(np.max(np.abs(a - b) / np.where(b > 0, b, 1.0))))
    for n in ("catalogue_size", "planet_count_sample", "mean_planets_per_star", "giant_fraction_sample"):
        assert same(on.fields[n], off.fields[n]), n
    # And the placement does differ: the stars stand in other cells.
    assert not same(on.fields["star_azimuth"], off.fields["star_azimuth"])


def hold_sub_rings(runs, name, m) -> None:
    # S61 (D220 item 8, the lead's ruling (a)): below level 0 the unit is the whole sub-ring, so a sub-ring's own stars
    # and their planets are the same on and off too - one level-1 and one level-3 sub-ring of ring 8 (R_SUN), every
    # child of each asked: the count bit for bit, the sums to 1e-12.
    for level, a in ((1, 1), (3, 5)):
        side = 1 << level
        kids = [sy.child_id(8 * sy.CELL_SECTORS + s_, level, a * side + b_) for s_ in range(sy.CELL_SECTORS) for b_ in range(side)]
        got = {}
        for layer in (True, False):
            out = runs[name, layer]
            cat = sy.materialise(out.fields, out.grid.R, out.grid.t, int(out.inputs["systems_seed"]), sy.CATALOGUE_SAMPLE,
                                 kids, migration=float(out.inputs["migration_efficiency"]), level=level, constants=constants(m))
            lay = sy.star_layout_of(cat)
            own = lay.level == level
            assert np.all(lay.ring[own] == 8 * side + a)
            mine = sy.select(cat, own, ((0, int(own.sum())),))
            cols, per = pl.materialise(mine, sy.star_layout_of(mine), int(out.inputs["planets_seed"]),
                                       {k: constants(m)[k] for k in pl.PLANETS_CONSTANTS})
            got[layer] = {"stars": int(own.sum()), "planets": int(per.sum()), "star mass": float(np.sum(mine["star_mass"])),
                          "star age": float(np.sum(mine["star_age"])), "planet mass": float(np.sum(cols["planet_mass"])),
                          "names": sorted(lay.index[own].tolist())}
        on, off = got[True], got[False]
        assert on["stars"] > 100 and on["stars"] == off["stars"] and on["planets"] == off["planets"] and on["names"] == off["names"], level
        for k in ("star mass", "star age", "planet mass"):
            assert on[k] == pytest.approx(off[k], rel=1e-12, abs=0.0), (level, k)


def test_i2_holds_on_another_galaxy(prod):
    m = prod[0].get(DEFAULT_MODEL)
    given = {**templates.overrides(templates.TEMPLATES["ngc_4414"]), "systems_seed": 3}
    on = ring_expectations(run(m, given, SMALL, layer=True), m)
    off = ring_expectations(run(m, given, SMALL, layer=False), m)
    for census in on:
        assert np.allclose(on[census], off[census], rtol=1e-12, atol=0.0), census


# --- I3: the table is judged with the layer off --------------------------------------------------------------------


def test_i3_every_judging_run_is_layer_off(prod, monkeypatch):
    """``spec.run``, the ensemble, the sweeps and the convergence sweep all pass ``layer=False`` to the runner, and
    none takes a ``layer=`` of its own."""
    import galaxy.run as runner
    from galaxy.specs import convergence

    seen: list[bool] = []
    real = runner.run

    def recording(*args, **kwargs):
        seen.append(kwargs.get("layer", True))
        return real(*args, **kwargs)

    monkeypatch.setattr(runner, "run", recording)
    m = prod[0].get(DEFAULT_MODEL)
    spec.run(m, grid=SMALL)
    spec.ensemble(m, n=2, grid=SMALL)
    spec.sweeps(m, grid=SMALL)
    convergence.sweep(m, {"n_R": (24, 48)}, SMALL)
    assert len(seen) > 12 and not any(seen)
    assert spec.judged({}) == {"layer": False}
    for call in (lambda: spec.run(m, layer=True), lambda: spec.ensemble(m, n=1, layer=True),
                 lambda: spec.judged({"layer": False})):
        with pytest.raises(spec.SpecError, match="layer-off"):
            call()
    assert "judged on the layer-off run" in spec.report([m], {m.name: spec.run(m, grid=SMALL)})


def test_i3_no_row_and_no_check_names_a_synthetic_or_a_composed_field(prod):
    models, impls_, _ = prod
    for m in models:
        declared = {d.name: d for _, sid in m.stages for d in impls_.get(sid).publishes}
        # S70 (D234, Audit V F-3-5): and the field that decides whether a row is judged at all (`only_if`, spec.py) -
        # a row judged only where a synthetic label said so would read the layer through the back door.
        named = [(q.n, f) for q in spec.QUANTITIES
                 for f in (q.field, q.sweep.abscissa if q.sweep else None, q.only_if[0] if q.only_if else None) if f]
        assert len(named) > 30 and any(q.only_if for q in spec.QUANTITIES)
        assert {f for q in spec.QUANTITIES if q.only_if for f in (q.only_if[0],)} <= set(declared)
        for n, f in named:
            if f in declared:
                assert not declared[f].composed and declared[f].provenance != "synthetic", (n, f)
        for template in templates.TEMPLATES.values():
            for check in template.checks:
                if check.field in declared:
                    assert not declared[check.field].composed and declared[check.field].provenance != "synthetic", check.name
    assert checks.JUDGED_LAYER is False and compose.SETTINGS[checks.JUDGED_SETTING] is False


def test_i3_rows_35_and_37_read_the_layer_off_census(runs):
    """The two rows that read a census (BUILD_III section 1d: they "moved with S51's redraw; under I3 they stop
    moving with placement"). Read once layer-off and pinned here; every other row's field is the same number on and
    off (it is no census statistic: test_i1). Row 35 stays inside KEH89's [-2.5, -1.5]; row 37 stays a miss (#117)."""
    for name in MODELS:
        on, off = runs[name, True].fields, runs[name, False].fields
        # S55 (D214): was -1.98926 (the layer-on census), read layer-off
        # S61 (D220 item 10): was -2.08124 - the layer-off census redrawn ring-first, the one move D220 allows the row
        assert float(off["hii_luminosity_function_slope"]) == pytest.approx(-2.05555, abs=1e-5)
        # S55 (D214): was -0.105511 (the layer-on census), read layer-off
        # S61 (D220 item 10): was -0.102973 - the layer-off census redrawn ring-first
        # S67 (D231): was -0.097717 - the clouds' size law moves the regions' densities; still a miss (#117).
        assert float(off["nii_halpha_gradient_hii"]) == pytest.approx(-0.097902, abs=1e-6)
        # The layer-on census's readings, for the record and not judged (I3). S56 (D215): were -1.98926 and
        # -0.105511 on S51's census; the census placed by five modes is another draw.
        # S57 (D216): were -2.06083 and -0.102613 on S56's census; placed by the gas's steady response it is another
        # draw (D216 predicted "rows 35 and 37 may move with placement, layer on"). Not judged: the rows above are.
        # S58 (D217): the first was -2.06976 on S57's census; with the lanes and the bar-tied phase it is another draw.
        # S59 (D218): were -2.06378 and -0.103890 on S58's census; placed by a response the winding's segments have
        # turned it is another draw. Not judged, as before: the two rows above read the layer-off census and are the
        # numbers they were, to every figure pinned.
        # S59 (D218 follow-up): were -1.97863 and -0.102083 on the first build's census; with a segment's pitch
        # relative to the disc's the rings are turned by other phases and the census is another draw (two of the
        # three brightest regions of that census are gone, and the slope is steeper again). Not judged; the two
        # layer-off rows above did not move.
        # S60 (D219): the layer-on readings are the pieces' census's and are pinned apart (the test after this one,
        # awaiting the re-pin); the two layer-off rows above are the numbers they were, to every figure pinned.
        # D214's prediction (b): row 37 within 0.005 dex/kpc of -0.1055, and still outside [-0.045, -0.005]. Held at
        # S55 (-0.102973, 0.0025 from it). S61 (D220 item 10): was asserted of each run - the ring-first redraw reads
        # -0.097717, 0.0078 from -0.1055: the prediction was of S55's census, which no longer exists, and is not
        # re-judged here (reported to the lead); "still outside the window" is asserted below.
        assert not -0.045 <= float(off["nii_halpha_gradient_hii"]) <= -0.005
        for q in spec.QUANTITIES:
            if q.field in on and q.n not in (spec.ROW_HII_LF_SLOPE, spec.ROW_NII_HALPHA_GRADIENT):
                assert same(on[q.field], off[q.field]), (q.n, q.field)
    q35 = next(q for q in spec.QUANTITIES if q.n == spec.ROW_HII_LF_SLOPE)
    q37 = next(q for q in spec.QUANTITIES if q.n == spec.ROW_NII_HALPHA_GRADIENT)
    assert q35.lo <= -2.05555 <= q35.hi and not q37.lo <= -0.097902 <= q37.hi  # S67 (D231): was -0.097717. S61 (D220): were -2.08124 and -0.102973
    assert spec.ROW_NII_HALPHA_GRADIENT in spec.MISSES and spec.ROW_HII_LF_SLOPE not in spec.MISSES


def test_rows_35_and_37_on_the_layer_on_census_as_measured(runs):
    """The layer-on census's readings of rows 35 and 37 as measured on the final model (S60, D219), for the record
    and not judged (I3: the rows are judged layer-off, in test_i3). Placed by the arms' census they are another
    draw each time the pattern moves."""
    for name in MODELS:
        on = runs[name, True].fields
        # S60 fourth pass: were -2.03559 and -0.102201.
        # S61 (D220 item 4): were -2.03381 and -0.101488 - drawn ring-first, the layer-on census is the layer-off
        # census's regions, placed: the two rows read the layer-off numbers (here the same bits).
        assert float(on["hii_luminosity_function_slope"]) == pytest.approx(-2.05555, abs=1e-5)
        assert float(on["nii_halpha_gradient_hii"]) == pytest.approx(-0.097902, abs=1e-6)  # S67 (D231): was -0.097717
        off = runs[name, False].fields
        for n in ("hii_luminosity_function_slope", "nii_halpha_gradient_hii"):
            assert same(on[n], off[n]), n


# --- I4: no physics stage reads the layer --------------------------------------------------------------------------

SYNTHETIC = dict(provenance="synthetic", stands_in_for="a physics", conserves="a total", statistic="none read (#95)")


def test_i4_the_production_graphs_declare_their_readers(prod):
    """The closed set, read from the stages' own declarations. ``nebular`` and ``bubbles`` inherit the clusters'
    objects and require neither a composed nor a synthetic field, so they are not readers; ``planets`` rebuilds
    the star catalogue's layout from the stellar pattern, so it is."""
    models, impls_, table = prod
    assert graph.check(models, impls_, table) == []
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert set(g.placement_readers) == {"systems", "bright_stars", "clouds", "clusters", "planets"}
        # S56 (D215): was the cloud texture alone. S60 (D219): was ("arm_phases", "cloud_texture").
        # S61 (D220 part II): was ("arm_pieces", "cloud_texture") - the clustering field runs in the first wave.
        # S62 (D221 item 7 as amended): was ("census_clustering", "arm_pieces", "cloud_texture") - the gas spurs' census;
        # S62 (D221): and the gas fluctuation field, as the graph orders them.
        assert g.layer_stages == ("census_clustering", "arm_pieces", "gas_spurs", "gas_fluctuation", "cloud_texture")
        # S60 (D219): was {"pattern", "gas_pattern"} - the law's stage composes nothing; the composing stage is
        # `stellar_pattern`, beside the gas's.
        # S60 (D219, the gate's fourth follow-up, C): the disclosed check `arm_ring_power` publishes the realised ring
        # power and its split, composed fields, from a stage of its own - a composing stage beside the two.
        # S60 fourth pass: was {"stellar_pattern", "gas_pattern"} (+ sfh_azimuthal).
        # S62 (D221 item 7 as amended): and `spurs`, which composes the gas spurs into the gas's contrast.
        expected = {"stellar_pattern", "arm_ring_power", "gas_pattern", "spurs"} | ({"sfh_azimuthal"} if m.name == "azimuthal" else set())
        assert set(g.composing_stages) == expected
        # What the declarations are for: every stage that requires a composed or a synthetic field is one of them.
        decl_of = {d.name: d for st in g.order for d in st.publishes}
        for st in g.order:
            reads = [n for n in st.requires + st.requires_optional if n in decl_of]
            if any(decl_of[n].composed or decl_of[n].provenance == "synthetic" for n in reads):
                assert st.may_place, st.id
        assert not impls_.get("sfh").may_place  # the base of the composing extension has no such right
        report = graph.report([m], impls_, table)
        assert "placement readers: bright_stars, clouds, systems, planets, clusters" in report
        # S56 (D215): was "layer stages: cloud_texture" and a line "input unread by ruling: texture_seed".
        # S61 (D220 part II): was "layer stages: arm_pieces, cloud_texture" - the clustering field's stage leads.
        # S62 (D221 item 7 as amended): was "layer stages: census_clustering, arm_pieces, cloud_texture" - the gas spurs' census;
        # S62 (D221): and the gas fluctuation field.
        assert "layer stages: census_clustering, arm_pieces, gas_spurs, gas_fluctuation, cloud_texture" in report and "unread by ruling" not in report  # S60 (D219): was arm_phases
        assert "texture_seed@3" in report and "inputs unbound: 0" in report


def binning_stages(g) -> set[str]:
    """The physics stages a placement reaches through the realised catalogues, read from the graph: a stage that is
    neither a placement reader, a composing stage nor a layer stage, and requires a catalogue column a placement
    reader or a layer stage publishes - or a field of a stage that does."""
    carried = {d.name for st in g.order if st.placement_reader or st.layer_stage for d in st.publishes
               if d.kind.domain == "object" or d.provenance == "synthetic"}
    found: set[str] = set()
    for st in g.order:
        if not st.may_place and any(n in carried for n in st.requires + st.requires_optional):
            found.add(st.id)
            carried |= set(st.published_names)
    return found


# The physics stages that bin realised objects (I4 as amended at gate G1, change 7): **a closed list**. Until S61 each
# read `cluster_radius`, which carries the layer's synthetic source offset, and binned by it - `nebular` the regions'
# line ratios per ring (nebular.ring_ratios), `bubbles` the bubbles' volumes per ring (bubbles.hot_phase_porosity).
# S61 (D220 item 6): they bin by `cluster_birth_radius`, the cloud's radius - a draw on the ring's stream that no
# placement moves - so what they bin per ring does not depend on placement (I4's second half), and what they publish
# from it is in RING_FIRST_STATISTICS, the same on and off. A third stage appearing here fails the test below.
BINNING_STAGES = {"nebular", "bubbles"}


def test_i4_the_stages_that_bin_realised_objects_are_a_closed_list(prod):
    """Placement reaches physics through the realised catalogues, and the graph's field check cannot see it: a
    cluster's radius is a seeded column of a placement reader. So the transitive case is held by name, derived from
    the code: who requires a placed catalogue's column without being a reader."""
    models, impls_, table = prod
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert binning_stages(g) == BINNING_STAGES, sorted(binning_stages(g) ^ BINNING_STAGES)
        stages = {st.id: st for st in g.order}
        clusters = stages["clusters"]
        # The column that carries the offset: a placement reader's, drawn from the layer's synthetic columns.
        assert clusters.placement_reader and "cluster_radius" in clusters.published_names
        assert {"cloud_source_offset", "cloud_source_angle"} <= set(clusters.requires)
        assert g.provenance["cloud_source_offset"] == "synthetic" and g.provenance["cluster_radius"] == "seeded"
        # S61 (D220 item 6): was `readers of cluster_radius == BINNING_STAGES` - they read the cloud's radius now,
        # and no stage reads the placement.
        readers = {st.id for st in g.order if "cluster_birth_radius" in st.requires + st.requires_optional}
        assert readers == BINNING_STAGES and "cluster_birth_radius" in clusters.published_names
        assert not {st.id for st in g.order if "cluster_radius" in st.requires + st.requires_optional}
        # S70 (D234, Audit V F-3-8): and every placement column, read from the declarations - no stage that is not
        # itself a placement reader or a layer stage requires a column the layer may move.
        placed = {d.name for st in g.order for d in st.publishes if d.placement}
        assert {"cluster_radius", "cloud_radius", "star_azimuth", "bright_star_azimuth", *cl.TEXTURE_COLUMNS} <= placed
        readers_of_placed = {st.id for st in g.order if placed & set(st.requires + st.requires_optional)}
        assert readers_of_placed and all(stages[sid].placement_reader or stages[sid].layer_stage for sid in readers_of_placed), readers_of_placed
        assert not readers_of_placed & BINNING_STAGES
        assert g.provenance["cluster_birth_radius"] == "seeded"
        for sid in BINNING_STAGES:
            st = stages[sid]
            assert not st.placement_reader and not st.composes and not st.layer_stage and not st.may_place, sid
            # No composed and no synthetic field among what it requires: the graph's own check passes it.
            for n in st.requires + st.requires_optional:
                d = next(d for s in g.order for d in s.publishes if d.name == n)
                assert not d.composed and d.provenance != "synthetic", (sid, n)
        # And what they publish from the binned objects is what the closed list of census statistics names.
        # S61 (D220 item 4): was CENSUS_STATISTICS - the eight are the same on and off since the ring-first draw.
        binned = {n for n, (sid, _, _) in RING_FIRST_STATISTICS.items() if sid in BINNING_STAGES}
        assert len(binned) == 8 and all(g.producer[n] in BINNING_STAGES for n in binned)
    # The derivation sees a third one: a physics stage that reads a cluster column is found.
    m = models.get(DEFAULT_MODEL)
    third = stage("ring_sums", (decl("cluster_ring_mass", provenance="seeded"),), requires=("cluster_radius", "cluster_mass"),
                  checkpoint=5)
    widened = {**{st.id: st for st in impls_}, "ring_sums": third}
    wider = replace(m, stages=(*m.stages, ("ring_sums", "ring_sums")))
    g = graph.analyse(wider, widened, table)
    assert g.ok and binning_stages(g) == BINNING_STAGES | {"ring_sums"}


def test_i4_the_graph_refuses_a_physics_stage_that_requires_a_composed_field():
    contrast = decl("contrast", axes=("R", "phi"), composed=True, neutral=1.0)
    assert contrast.composed and not decl("profile").composed
    # Declared, not read off the axes (gate G1, change 3): a phi-axis field that does not declare itself composed
    # is physics, and a physics stage may require it.
    in_frame = decl("in_frame", axes=("R", "phi"))
    tabulated, reads_it = stage("tabulated", (in_frame,)), stage("physics", ("g",), requires=("in_frame",))
    assert not in_frame.composed and not tabulated.composes
    assert graph.check([model("m", tabulated, reads_it)], impls(tabulated, reads_it), INPUTS) == []
    composer = stage("composer", (contrast,))
    physics = stage("physics", ("g",), requires=("contrast",))
    m = model("m", composer, physics)
    problems = graph.check([m], impls(composer, physics), INPUTS)
    assert [p.code for p in problems] == ["layer-reader"]
    assert "'physics'" in problems[0].detail and "'contrast'" in problems[0].detail and "invariant I4" in problems[0].detail
    # An optional requirement is a requirement.
    optional = decl("contrast", axes=("R", "phi"), optional=True, composed=True, neutral=1.0)
    po, optional_reader = stage("composer", (optional,)), stage("physics", ("g",), requires_optional=("contrast",))
    assert [p.code for p in graph.check([model("m", po, optional_reader)], impls(po, optional_reader), INPUTS)] == ["layer-reader"]
    # A declared placement reader may, and so may a stage that composes a field of its own from it.
    reader = stage("physics", ("g",), requires=("contrast",), placement_reader=True)
    assert graph.check([model("m", composer, reader)], impls(composer, reader), INPUTS) == []
    second = stage("physics", (decl("g", axes=("R", "phi"), composed=True, neutral=1.0),), requires=("contrast",))
    assert second.composes and graph.check([model("m", composer, second)], impls(composer, second), INPUTS) == []
    # Publishing a field over phi without declaring it composed lends no such right.
    undeclared = stage("physics", (decl("g", axes=("R", "phi")),), requires=("contrast",))
    assert not undeclared.composes
    assert [p.code for p in graph.check([model("m", composer, undeclared)], impls(composer, undeclared), INPUTS)] == ["layer-reader"]


def test_i4_the_graph_refuses_a_physics_stage_that_requires_a_synthetic_field():
    texture = decl("texture", **SYNTHETIC)
    realiser = stage("realiser", (texture,), compute=cloud_texture.compute_cloud_texture, layer_stage=True)
    physics = stage("physics", (decl("g", provenance="seeded"),), requires=("texture",))
    problems = graph.check([model("m", realiser, physics)], impls(realiser, physics), INPUTS)
    assert [p.code for p in problems] == ["layer-reader"] and "synthetic" in problems[0].detail
    reader = stage("physics", (decl("g", provenance="seeded"),), requires=("texture",), placement_reader=True)
    assert graph.check([model("m", realiser, reader)], impls(realiser, reader), INPUTS) == []
    # A reader of a synthetic field is seeded, not synthetic and not derived (D55, one provenance per stage).
    derived = stage("physics", ("g",), requires=("texture",), placement_reader=True)
    assert [p.code for p in graph.check([model("m", realiser, derived)], impls(realiser, derived), INPUTS)] == ["provenance"]


def test_i4_only_a_layer_stage_publishes_synthetic_and_it_lives_under_the_layer():
    texture = decl("texture", **SYNTHETIC)
    # A stage outside galaxy/layer/ that publishes a synthetic field: its provenance does not compute.
    outside = stage("outside", (texture,))
    assert [p.code for p in graph.check([model("m", outside)], impls(outside), INPUTS)] == ["provenance"]
    # One that declares itself a layer stage without living there.
    claims = stage("claims", (texture,), layer_stage=True)
    assert claims.home == "helpers"
    assert [p.code for p in graph.check([model("m", claims)], impls(claims), INPUTS)] == ["layer-stage"]
    # One that lives there and does not say so.
    silent = stage("silent", ("f",), compute=cloud_texture.compute_cloud_texture)
    assert silent.home == "galaxy.layer.cloud_texture"
    assert [p.code for p in graph.check([model("m", silent)], impls(silent), INPUTS)] == ["layer-stage"]
    # A layer stage publishes synthetic fields, all of them, whatever it reads.
    mixed = stage("mixed", (texture, decl("plain")), compute=cloud_texture.compute_cloud_texture, layer_stage=True)
    assert [p.code for p in graph.check([model("m", mixed)], impls(mixed), INPUTS)] == ["provenance"]
    whole = stage("whole", (texture,), compute=cloud_texture.compute_cloud_texture, layer_stage=True,
                  reads_seeds=("systems_seed",), checkpoint=5)
    g = graph.analyse(model("m", whole), impls(whole), INPUTS)
    assert g.ok and g.provenance == {"texture": "synthetic"} and g.layer_stages == ("whole",)


@pytest.mark.parametrize("stage_id, field", [("clusters", "cloud_source_offset"), ("systems", "sfr_modulation"),
                                             ("bright_stars", "sfr_modulation")])
def test_i4_a_production_census_without_its_declaration_fails_the_graph(prod, stage_id, field):
    models, impls_, table = prod
    m = models.get("azimuthal")
    undeclared = {st.id: st for st in impls_}
    undeclared[stage_id] = replace(impls_.get(stage_id), placement_reader=False)
    problems = graph.check([m], undeclared, table)
    assert problems and {p.code for p in problems} == {"layer-reader"}
    assert any(f"'{stage_id}'" in p.detail and f"'{field}'" in p.detail for p in problems)


def test_i4_compose_refuses_a_stage_that_is_not_a_reader_at_run_time(prod):
    """A pattern object is rebuilt from published fields, not read as a composed field. So the stage's own view of
    the fields says whether it may ask, and ``compose`` refuses one that may not.

    S56 (D215): until S56 the graph could not see these two - a pattern was rebuilt from seeded scalars (the drawn
    arm number among them), so ``graph.check`` was empty and only ``compose`` caught them. A pattern is built from
    the layer's phases now, synthetic fields, so the graph refuses them too; the run-time refusal is unchanged and
    is still the one that stops the run (a layer-reader problem is reported, not fatal to building the graph)."""
    models, impls_, table = prod
    m = models.get(DEFAULT_MODEL)
    for stage_id in ("clouds", "planets"):
        undeclared = {st.id: st for st in impls_}
        undeclared[stage_id] = replace(impls_.get(stage_id), placement_reader=False)
        problems = graph.check([m], undeclared, table)
        # S59 (D218): was `len(problems) == len(pt.PHASE_FIELDS)` - a pattern is built from the layer's two segment
        # columns too, synthetic like the phases, and the graph refuses each of the seven by name.
        # S60 (D219 item 7): was the five phases and the two segment columns - a pattern is built from the eight
        # columns of the census of arm pieces, and the graph refuses each of the eight by name.
        # S61 (D220 part II): and the clouds read the clustering field's seed, a ninth synthetic field.
        # S62 (D221 item 7 as amended): and the clouds read the gas spurs' twelve columns, composed into their gas pattern.
        synthetic_reads = pt.PIECE_FIELDS + (("census_clustering_seed", *_SPUR_FIELDS) if stage_id == "clouds" else ())
        # S61 (D220): the planets lay out their stars by the catalogue's own allocation (systems.star_layout), so they
        # read what it reads - the composed `sfr_modulation` too, which the graph refuses by name beside the eight.
        composed_reads = ("sfr_modulation",) if stage_id == "planets" else ()
        assert {p.code for p in problems} == {"layer-reader"} and len(problems) == len(synthetic_reads) + len(composed_reads)
        assert len(synthetic_reads) == (21 if stage_id == "clouds" else 8)  # S62: was 9 for the clouds
        assert all(f"'{stage_id}'" in p.detail and ("synthetic" in p.detail or "composed" in p.detail) for p in problems)
        assert {n for n in composed_reads if any(f"'{n}'" in p.detail for p in problems)} == set(composed_reads)
        assert {n for n in synthetic_reads if any(f"'{n}'" in p.detail for p in problems)} == set(synthetic_reads)
        with pytest.raises(UndeclaredAccess, match="placement reader"):
            run(m, grid=SMALL, impls=undeclared, only=[d.name for d in impls_.get(stage_id).publishes][:1])


# --- I5: the API's half of the switch ------------------------------------------------------------------------------

INPUT_ROUTES = ("/api/arrays", "/api/region", "/api/system", "/api/clouds", "/api/clusters", "/api/remnants",
                "/api/bright", "/api/render")
SECTOR = "r_min=7&r_max=9&phi_min=0&phi_max=0.6"
B_V = json.dumps([{"name": b, "shape": "gaussian", "centre": c, "fwhm": 900.0} for b, c in (("B", 4400.0), ("V", 5500.0))])
QUERIES = {
    "/api/arrays": {"fields": ["pattern_density_contrast,stellar_mass_total"]},
    "/api/region": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/system": {"cell": ["300"], "index": ["0"]},
    "/api/clouds": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/clusters": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/remnants": {"r_min": ["7"], "r_max": ["9"], "phi_min": ["0"], "phi_max": ["0.6"]},
    "/api/bright": {"n": ["400"]},
    "/api/render": {"filters": [B_V]},
}


def test_i5_every_route_that_takes_inputs_takes_the_switch():
    """The routes with ``layer`` among their parameters are exactly those that take inputs (they take ``template``),
    and ``layer`` is reserved, so it is never read as an input."""
    takes = {r.path for r in ROUTES if "layer" in r.params}
    assert takes == {r.path for r in ROUTES if "template" in r.params} == set(INPUT_ROUTES) == set(QUERIES)
    assert "layer" in RESERVED and "layer" not in INPUTS
    index = Service(grid=SMALL).handle("/api").json()
    assert "layer=off" in index["layer"] and "400" in index["layer"]


@pytest.mark.parametrize("path", INPUT_ROUTES)
def test_i5_the_header_echoes_the_setting_and_a_bad_value_is_a_400(path):
    svc = Service(grid=SMALL)
    q = QUERIES[path]
    plain = svc.handle(path, q)
    on = svc.handle(path, {**q, "layer": ["on"]})
    off = svc.handle(path, {**q, "layer": ["off"]})
    assert plain.ok and on.ok and off.ok, (plain.status, on.status, off.status)
    # Absent and on are one request: the same header and the same arrays, byte for byte.
    assert answer(plain) == answer(on) and svc.handle(path, q).body == on.body
    assert answer(on)[0]["layer"] == "on" and answer(off)[0]["layer"] == "off"
    for bad in ("0", "false", "OFF", ""):
        refused = svc.handle(path, {**q, "layer": [bad]})
        assert refused.status == 400 and "layer=" in refused.json()["error"], bad
    assert svc.handle(path, {**q, "layer": ["on", "off"]}).status == 400  # given twice


def test_i5_on_and_off_never_share_a_cache_entry():
    svc = Service(grid=SMALL, cache=4)
    fields = {"fields": ["pattern_density_contrast,gas_density_contrast,sfr_modulation"]}
    on = svc.handle("/api/arrays", fields).frame()[1]
    off = svc.handle("/api/arrays", {**fields, "layer": ["off"]}).frame()[1]
    again = svc.handle("/api/arrays", fields).frame()[1]
    assert len(svc._cache) == 2  # one galaxy, two settings: two entries
    for name in on:
        assert np.all(off[name] == 1.0) and not np.all(on[name] == 1.0) and same(on[name], again[name]), name
    # The census caches too: a window's clouds asked for on, off, on again.
    first = svc.handle("/api/clouds", SECTOR)
    without = svc.handle("/api/clouds", SECTOR + "&layer=off")
    assert answer(svc.handle("/api/clouds", SECTOR)) == answer(first)
    assert answer(svc.handle("/api/clouds", SECTOR + "&layer=off")) == answer(without)
    a, b = first.frame()[1], without.frame()[1]
    assert not same(a["cloud_azimuth"], b["cloud_azimuth"])
    for route, column in (("/api/region", "star_azimuth"), ("/api/clusters", "cluster_azimuth")):
        got_on, got_off = svc.handle(route, SECTOR), svc.handle(route, SECTOR + "&layer=off")
        assert not same(got_on.frame()[1][column], got_off.frame()[1][column]), route
        assert answer(svc.handle(route, SECTOR)) == answer(got_on), route
    bright_on, bright_off = svc.handle("/api/bright", "n=300"), svc.handle("/api/bright", "n=300&layer=off")
    assert not same(bright_on.frame()[1]["bright_star_azimuth"], bright_off.frame()[1]["bright_star_azimuth"])
    assert answer(svc.handle("/api/bright", "n=300")) == answer(bright_on)


def test_i5_what_layer_off_serves():
    """The contract the viewer builds against: the composed fields at their neutral, the cloud texture columns 0, the
    cloud interior's three parameters in the header either way, the render's frame even round each ring."""
    svc = Service(grid=SMALL)
    on_h, on = svc.handle("/api/clouds", SECTOR).frame()
    off_h, off = svc.handle("/api/clouds", SECTOR + "&layer=off").frame()
    for header in (on_h, off_h):
        assert header["cloud_interior"] == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert not [k for k in header["scalars"] if "interior" in k]
        # S64 (D224, R1): the API's derived dust column after the census's; S70 (D234, F-4-3): was last, the shape follows
        assert header["columns"] == [*cl.WIRE_COLUMNS, *v6c.DERIVED_COLUMNS]
    assert len(off["cloud_radius"]) > 20
    for name in cl.TEXTURE_COLUMNS:
        assert np.all(off[name] == 0.0) and np.any(on[name] != 0.0), name


# The render's components, by what each keeps ring by ring between the layer on and off (gate G1, change 10: "each
# ring keeps its light" is every component's claim, not the stars' alone). Measured at S55 on the small and the
# production grid through two filter sets: every component but one is the same ring total to 1.1e-14, the per-ring
# ones to the bit. The one is `lines_hii`, summed from the HII regions' four forbidden lines' ring light - the four
# radial fields CENSUS_STATISTICS names, a sum over realised regions - and it is a census statistic in the render
# too: up to a factor of six in a thinly populated ring on the production grid.
# S63 (D223): the two placing weights the starlight by age ships beside dust_placement - sfr_modulation over its ring
# mean and the stellar contrast floored at 0 - are (R, phi) arrays, exactly 1 with the layer off.
RENDER_PLACED = ("stars", "stars_unresolved", "halpha_hii", "dust_scattered", "dust_placement", "stars_middle_placement", "stars_placement",
                 "dust_placement_unspurred")  # (R, phi, ...) - S66 (D226 R4): and the gas's placement without its spurs
# S63 (D223): and the three age parts of the starlight, per ring and filter, the same numbers on and off.
# S64 (D224, R2): and the share of each ring's dust that is diffuse once its realised clouds hold theirs - (R,), read off
# the ring-first draw's streams, so the same bits on and off (the same clouds either way).
# S66 (D226 R5b): and the middle part's three kept-octave windows - the history's and the constants', the same bits.
RENDER_PER_RING = ("halpha_dig", "lines_dig", "dust_extinction", "dust_thermal", "dust_height", "stars_young", "stars_middle", "stars_old", "dust_diffuse_share",
                   "stars_middle_kept3", "stars_middle_kept2", "stars_middle_kept1")  # (R, ...)
# S61 (D220 items 4 and 6): was ("lines_hii",) - the regions' ring ratios are the ring-first census's, binned by the
# clouds' radii, so the HII line light keeps its ring on and off to 1e-12 (RENDER_RING_FIRST). None is left here.
RENDER_CENSUS_STATISTICS: tuple[str, ...] = ()
RENDER_RING_FIRST = ("lines_hii",)
WIDE = json.dumps([{"name": "optical", "shape": "box", "centre": 5500.0, "width": 4000.0},
                   {"name": "far_infrared", "shape": "box", "centre": 1.0e6, "width": 1.0e6}])


@pytest.mark.parametrize("curves", [B_V, WIDE], ids=["B and V", "optical and far infrared"])
def test_i5_every_component_of_the_render_keeps_its_ring_or_is_a_named_census_statistic(curves):
    svc = Service(grid=SMALL)
    q = {"filters": [curves], "l_min": ["1000"]}  # l_min: the unresolved remainder is a component too
    on_h, on = svc.handle("/api/render", q).frame()
    off_h, off = svc.handle("/api/render", {**q, "layer": ["off"]}).frame()
    assert (on_h["layer"], off_h["layer"]) == ("on", "off") and list(on) == list(off)
    # Every array of the response is in exactly one of the three groups: a new component must be placed in one.
    assert set(on) == {*RENDER_PLACED, *RENDER_PER_RING, *RENDER_CENSUS_STATISTICS, *RENDER_RING_FIRST}

    def rings(arrays, name):
        return np.asarray(arrays[name], dtype=float).sum(axis=1)

    # S57 (D216 G3 item 4): every placed component keeps its ring to rounding on this small grid again. S57's first
    # build published the gas's response at the cells' centres, whose sampled mean on 36 cells left 1 by 1.257e-3,
    # and the two components the gas places (halpha_hii, dust_placement) had been re-pinned to that here, with the
    # 1e-12 moved to the production grid. The published field is now the law's exact mean over each grid cell's
    # extent in azimuth, at the ring's own radius: a ring's cells average to 1 to rounding on any grid, with nothing divided, and the rule below is the one it was.
    for name in RENDER_PLACED:
        assert on_h["axes"][name][:2] == ["R", "phi"], name
        # Layer off: even round the ring - every cell holds its ring's own value. Layer on: it is placed.
        cell = off[name][:, :1]
        assert np.all(off[name] == cell) and not np.all(on[name] == on[name][:, :1]), name
        # And each ring keeps its total, to rounding: the placement averages to 1 round every ring.
        assert np.allclose(rings(on, name), rings(off, name), rtol=1e-12, atol=0.0), name
    assert np.all(off["dust_placement"] == 1.0)
    for name in RENDER_PER_RING:
        assert on_h["axes"][name][0] == "R" and "phi" not in on_h["axes"][name], name
        assert same(on[name], off[name]), name  # a ring's own value, the same bits either way
    for name in RENDER_RING_FIRST:
        # S61 (D220 items 4 and 6): even round the ring with the layer off; with it on placed by the gas's contrast,
        # and each ring's line light the same to 1e-12 - the same regions, binned by their clouds' radii.
        assert np.all(off[name] == off[name][:, :1]) and not np.all(on[name] == on[name][:, :1]), name
        assert np.allclose(rings(on, name), rings(off, name), rtol=1e-12, atol=0.0), name
        assert {f for f in on_h["components"][name]["fields"] if f in RING_FIRST_STATISTICS} == {
            f"{line}_surface_brightness_hii" for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")}
    for name in RENDER_CENSUS_STATISTICS:
        # Not conserved ring by ring, and said so: the regions the ring's line light is summed over are another
        # draw. Even round the ring all the same, and the Halpha it is built on (halpha_hii, above) is conserved.
        assert np.all(off[name] == off[name][:, :1]), name
        a, b = rings(on, name), rings(off, name)
        assert not np.allclose(a, b, rtol=1e-3, atol=0.0), name
        assert on_h["components"][name]["fields"][:4] == [f"{line}_surface_brightness_hii" for line in ("hbeta", "oiii_5007", "nii_6583", "sii_6716")]
        assert {f for f in on_h["components"][name]["fields"] if f in CENSUS_STATISTICS} == {
            f"{line}_surface_brightness_hii" for line in ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")}
    # The frame: every conserving component's light, summed over the disc with the bulge, is the same to rounding.
    # (S57 (D216 G3): the first build's `1e-5` for the HII line on this grid is back at 1e-12.)
    for name in ("stars", "stars_unresolved", "halpha_hii", "dust_scattered"):
        total_on = checks.frame_total(on_h, {**on, "stars": on[name]})
        total_off = checks.frame_total(off_h, {**off, "stars": off[name]})
        assert np.allclose(total_on, total_off, rtol=1e-12, atol=0.0), name
    # What the header says of a placement is true of this response (gate G1, change 11).
    for name in ("stars", "stars_unresolved", "halpha_hii", "lines_hii"):
        assert "layer is off" in off_h["components"][name]["about"] and "neutral value, 1" in off_h["components"][name]["about"], name
        assert "layer is off" not in on_h["components"][name]["about"], name
    placed = off_h["placement"]["arrays"]["dust_placement"]["about"]
    assert "layer is off" in placed and "layer is off" not in on_h["placement"]["arrays"]["dust_placement"]["about"]


def test_i5_the_metadata_names_the_fourth_kind_and_the_fifth_seed(model):
    svc = Service(grid=SMALL)
    fields = svc.handle("/api/fields", f"model={model.name}").json()["fields"]
    assert {f["provenance"] for f in fields} == set(PROVENANCE) == {"derived", "seeded", "synthetic"}
    synthetic = [f for f in fields if f["provenance"] == "synthetic"]
    # The four cloud columns and, since S56 (D215), the five arm modes' phases, and nothing else: the interior's three
    # numbers are constants, not fields (G1, change 4).
    # S59 (D218 items 1-2): and the two columns of the winding's segments - the same stage's, on the same seed.
    # S60 (D219 item 7): was the phases and the segments - the census of arm pieces, eight columns of one table.
    # S61 (D220 part II): and the clustering field's seed and cell means.
    # S62 (D221 item 7 as amended): and the gas spurs' census. S62 (D221): and the gas fluctuation field's eight.
    assert {f["name"] for f in synthetic} == set(cl.TEXTURE_COLUMNS) | set(pt.PIECE_FIELDS) | CLUSTERING_FIELDS | ADDED_AT_S62_SPURS | GAS_FIELDS
    assert not [f["name"] for f in fields if "cloud_interior" in f["name"]]
    for f in fields:
        if f["provenance"] == "synthetic":
            assert all(isinstance(f[k], str) and f[k].strip() for k in SYNTHETIC_DECLARATIONS), f["name"]
            if f["name"] in pt.PIECE_FIELDS:
                # S60 (D219): the pieces' draws. Its statistic names what each number was read from and what is
                # measured nowhere (and so not drawn); what it stands in for is the disc's own history of swing
                # amplification, which the model does not integrate; what it conserves is every ring's mean and
                # every law. A table's column, not a catalogue's: domain "table", no ramp, and it says in plain
                # words that the viewer does not show it, and that there is no row with the layer off.
                assert f["stage"] == "arm_pieces" and f["kind"] == "table_column" and f["of"] == "arm_piece", f["name"]
                assert f["domain"] == "table" and f["ramp"] is None and "not shown by the viewer" in f["about"], f["name"]
                assert "No row with the randomness layer off" in f["about"], f["name"]
                assert "38 printed rows" in f["statistic"] and "while the pitch it makes is not positive" in f["statistic"] and "[verified:" in f["statistic"], f["name"]
                assert "measured nowhere" in f["statistic"] and "not drawn" in f["statistic"], f["name"]
                assert "self-gravitating disc" in f["stands_in_for"] and "Every ring's mean density and every law" in f["conserves"], f["name"]
                assert not re.search(r"none read", f["statistic"], re.IGNORECASE), f["name"]
                continue
            if f["name"] in ADDED_AT_S62_SPURS:
                # S62 (D221 item 7 as amended): the gas spurs' census - a table the viewer does not show, its draw the
                # first foot's place on each chain and every other number a sourced law.
                assert f["stage"] == "gas_spurs" and f["kind"] == "table_column" and f["of"] == "gas_spur", f["name"]
                assert f["domain"] == "table" and f["ramp"] is None and "not shown by the viewer" in f["about"], f["name"]
                assert "No row with the randomness layer off" in f["about"] and "[verified:" in f["statistic"], f["name"]
                assert "magneto-Jeans instability" in f["stands_in_for"] and "Every ring's gas and every law" in f["conserves"], f["name"]
                continue
            if f["name"] in CLUSTERING_FIELDS:
                # S61 (D220 part II): the hierarchy's statistic, read (Grasha et al. 2017a Table 4), and NaN layer off.
                assert f["stage"] == "census_clustering" and "Grasha et al. 2017a" in f["statistic"] and "[verified:" in f["statistic"], f["name"]
                assert "hierarchical fragmentation" in f["stands_in_for"] and "It does not keep" in f["conserves"], f["name"]
                assert "NaN with the randomness layer off" in f["about"], f["name"]
                continue
            if f["name"] in GAS_FIELDS:
                # S62 (D221): the spectrum's slopes, the width relation and the shear time, read; NaN layer off.
                assert f["stage"] == "gas_fluctuation" and "Burkhart" in f["statistic"] and "Heiles & Troland 2003" in f["statistic"], f["name"]
                assert "[verified:" in f["statistic"] and "diffuse ISM between the clouds" in f["stands_in_for"], f["name"]
                assert "It does not keep where within a cell" in f["conserves"] and "noise.shear in each point's own frame" in f["conserves"], f["name"]
                assert "NaN with the randomness layer off" in f["about"], f["name"]
                continue
            assert f["stage"] == "cloud_texture" and re.search(r"none read \(#95\)", f["statistic"]), f["name"]
            # Which seed, in each of the four (G1, change 6).
            # S61 (D220 item 5): was "Drawn on `systems_seed`, the stream Phase R keeps; on `texture_seed` from L1."
            assert "Drawn on `texture_seed`, the layer's own seed" in f["about"] and "resolved at S61 (D220 item 5)" in f["about"], f["name"]
        else:
            assert not set(SYNTHETIC_DECLARATIONS) & set(f), f["name"]
    # A composed field says so, with its neutral value; no other entry carries either key (G1, change 3).
    # S60 (D219): the composing stage's nine radial fields beside the contrast, each with its own neutral.
    composed = {f["name"]: f for f in fields if "composed" in f or "neutral" in f}
    assert set(composed) == COMPOSED_FIELDS | ({"sfr_modulation"} if model.name == "azimuthal" else set())
    for name, f in composed.items():
        assert f["composed"] is True and f["neutral"] == COMPOSED_NEUTRALS.get(name, 1.0) and f["provenance"] == "seeded", name
        if f["neutral"] == 1.0 and name != "arm_piece_saturation":
            assert "A composed field: with the randomness layer off it is 1 everywhere" in f["about"], name
        else:
            assert "with the randomness layer off" in f["about"], name  # "0 with the randomness layer off", "1 with ..."
        # S60 (D219, the fourth follow-up's C): the ring power and its split are published by `arm_ring_power`.
        # S60 fourth pass: was ("stellar_pattern", "gas_pattern", "sfh_azimuthal").
        # S62 (D221 item 7 as amended): and `spurs`, which publishes the gas's contrast with the gas spurs composed on it.
        assert f["stage"] in ("stellar_pattern", "arm_ring_power", "gas_pattern", "sfh_azimuthal", "spurs")  # a composing stage lives in stages/, not layer/
    seeds_ = svc.handle("/api/inputs", f"model={model.name}").json()["seeds"]
    assert [s["name"] for s in seeds_] == [s.name for s in seeds()] and len(seeds_) == 5
    texture = next(s for s in seeds_ if s["name"] == "texture_seed")
    assert texture["default"] == 0 and texture["checkpoint"] == 3 and "P1" in texture["about"]
    published = {t["name"]: t["inputs"]["seeds"]["texture_seed"] for t in svc.handle("/api/templates").json()["templates"]}
    assert published == {"milky_way": 0, "ngc_4414": 4414}
    stages = svc.handle("/api/stages", f"model={model.name}").json()
    assert "cloud_texture" in stages["order"] and stages["order"].index("clouds") < stages["order"].index("cloud_texture") < stages["order"].index("clusters")
    # S56: the phases, then the field. S60 (D219): the law, then the census, then the field composed from both.
    assert stages["order"].index("pattern") < stages["order"].index("arm_pieces") < stages["order"].index("stellar_pattern")


# --- the oracle (BUILD_III Phase R, item 5) ------------------------------------------------------------------------


def test_the_oracle_layer_off_azimuthal_is_layer_off_basic(runs):
    """``basic`` is the model without star formation that follows the arms. With the layer off the arms are nowhere,
    so the two are one galaxy: every field they share is bit-identical - every radial field, every history, every
    scalar and every column of every catalogue - and the one field only ``azimuthal`` has is 1 everywhere."""
    a, b = runs["azimuthal", False], runs["basic", False]
    assert set(a.fields) - set(b.fields) == {"sfr_modulation"} and not set(b.fields) - set(a.fields)
    assert np.all(np.asarray(a.fields["sfr_modulation"]) == 1.0)
    differ = [n for n in b.fields if not same(a.fields[n], b.fields[n])]
    assert differ == [], differ
    columns = [n for n, d in b.decls.items() if d.kind.domain == "object"]
    # 343: S54's 331 fields, name for name (334 while the interior's three numbers were scalars, before gate G1),
    # S56's eleven (D215): five amplitudes, the saturation, five phases; and S57's one (D216): the arms' frame.
    # S57 (D216): was 342. S58 (D217): was 343 - the bar's formation time, its presence, the body's three shape
    # numbers and its share of the disc's mass.
    # S58 (D217 follow-up): was 349 - the gas's contrast as the star formation law reads it, a third composed field
    # of `basic` (so what the oracle below holds, the fields not composed, is still 229).
    # S59 (D218): was 350 - the winding's anchor, the pitch as drawn, the Sun's azimuth, and the layer's two segment
    # columns (empty with the layer off, in both models alike).
    # S59 (D218 follow-up): was 355 - the spread of a segment's pitch over the disc's, the `bar` stage's scalar.
    # S60 (D219): was 356 - twenty-one added (ADDED_AT_S60) and nine retired: the five phases, the anchor, the two
    # segment columns and the spread.
    # S61 (D220 item 6): was 368 - the binners' radius, `cluster_birth_radius`.
    # S61 (D220 part II): was 369 - the cloud's ring-drawn radius and the clustering field's seed and cell means.
    # S62 (D221 item 7 as amended): was 372 - the gas spurs' twelve columns. S62 (D221): was 384 - the gas fluctuation
    # field's eight.
    assert len(columns) > 100 and len(b.fields) == 392


def test_the_oracle_against_layer_on_basic_holds_outside_the_censuses(runs):
    """The second comparison D214 names: layer-off ``azimuthal`` against layer-on ``basic``, the fields not declared
    composed. It holds on every radial field, history and scalar that is not a census statistic - 215 fields, bit
    for bit. It does not hold on the catalogues' columns or the census statistics, and cannot: layer-on ``basic``
    places its censuses by the pattern. Those are exactly the fields I1 lets move, in ``basic`` itself (test_i1) -
    I1's list again, and not an independent check (D214, the predictions as read)."""
    a, b = runs["azimuthal", False], runs["basic", True]
    # S56 (D215 ruling 11): an expected total is held to its last place, not its last bit (EXPECTED_TOTALS, above).
    # S61 (D220 item 4): and a statistic of a census drawn ring-first to 1e-12 (RING_FIRST_STATISTICS).
    differ = {n for n, d in b.decls.items() if not d.composed and not same(a.fields[n], b.fields[n])
              and not (n in EXPECTED_TOTALS and same_expected_total(a.fields[n], b.fields[n]))
              and not (n in RING_FIRST_STATISTICS and same_ring_first(a.fields[n], b.fields[n]))}
    # S56 (D215): the layer's five phases were numbers in the layer-on run and not in the layer-off one. S60 (D219):
    # retired - no synthetic scalar remains.
    # S61 (D220 part II): the clustering field's seed and cell means are numbers in the layer-on run and NaN in the
    # layer-off one - set apart by name.
    # S62 (D221): was CLUSTERING_FIELDS - and the gas fluctuation field's eight (its ring table and cell column too).
    clustering = differ & NAN_OFF_FIELDS
    assert clustering == NAN_OFF_FIELDS
    differ -= clustering
    phases = {n for n in differ if b.decls[n].provenance == "synthetic" and b.decls[n].kind.domain == "galaxy"}
    assert phases == set()
    # S59 (D218): the layer's table's columns are rows in the layer-on run and none in the layer-off one: a table's
    # columns, set apart as the phases were. S60 (D219 item 7): the census of arm pieces, eight columns.
    segments = {n for n in differ if b.decls[n].kind.domain == "table"}
    # S62 (D221 item 7 as amended): and the gas spurs' census, a second table.
    assert segments == set(pt.PIECE_FIELDS) | ADDED_AT_S62_SPURS and {b.decls[n].of for n in segments} == LAYER_TABLES
    statistics = {n for n in differ - phases - segments if b.decls[n].kind.domain != "object"}
    # S58 (D217): was `== set(CENSUS_STATISTICS)`; `dig_halpha_fraction` lands on the same bits at S58's census (test_i1).
    # S59 (D218): was `== set(CENSUS_STATISTICS) - {"dig_halpha_fraction"}`; on S59's layer-on census the two sums
    # round apart again (test_i1), and the list is whole.
    # S60 (D219), as at S58 (D217): `dig_halpha_fraction` lands on the same bits in layer-off `azimuthal` and
    # layer-on `basic` - a ratio of two sums over the realised regions that is three tenths in any census, to
    # rounding, and these two censuses round alike. It is still a census statistic and stays listed; the one
    # entry that does not move here is named. S60 fourth pass: was `== set(CENSUS_STATISTICS)`.
    # S61 (D220 item 4): was `== set(CENSUS_STATISTICS) - {"dig_halpha_fraction"}` - the nine that left the list are
    # held to 1e-12 above; the five left all differ.
    assert statistics == set(CENSUS_STATISTICS)
    assert {b.decls[n].of for n in differ - statistics - phases - segments} == PLACED_OBJECTS
    held = [n for n, d in b.decls.items() if not d.composed and n not in differ and n not in clustering]
    # 222 = basic's 343 fields less its 2 composed ones, the 100 placed columns, the 14 census statistics and the
    # 5 phases (215 until S56, which added the law's five amplitudes and its saturation to what is held).
    # S57 (D216): was 221 - `arm_pattern_speed` joins what is held, the same bits on and off.
    # S58 (D217): was 222 - the six bar fields P3 adds, laws all, and the one census statistic that rounds alike.
    # S59 (D218): was 229 - the three scalars P4 adds (the anchor, the drawn pitch, the Sun's azimuth: NaN in both
    # runs, the same bits), less the census statistic that no longer rounds alike. 231 = basic's 355 fields less
    # its 3 composed ones, the 100 placed columns, the 2 segment columns, the 14 census statistics and the 5 phases.
    # S59 (D218 follow-up): was 231 - the spread of a segment's pitch over the disc's, the `bar` stage's scalar, is
    # held with the laws: the same bits on and off. 232 of basic's 356 fields.
    # S60 (D219): was 232 - the four P5 laws join what is held (the class, the width, the arm number, the budget)
    # and the anchor and the spread leave it. 234 = basic's 368 fields less its 12 composed ones, the 100 placed
    # columns, the 8 columns of the pieces' table and the 14 census statistics.
    # S60 (D219), as at S58 (D217): 235 - the census statistic that rounds alike (above) is held with them.
    # S60 fourth pass: was 234.
    # S61 (D220 item 4): was 235 - the eight ring-first statistics that differed join what is held, to 1e-12 (the
    # ninth, dig_halpha_fraction, was held already), and one cluster column: `hii_density_bounded` is 0 for every
    # region on and off, and since the ring-first draw the two censuses have the same count, so the column is the same
    # bytes - a placed census's column that does not depend on where its objects stand.
    # S61 (D220 items 1-4, the bright catalogue's build): was 244 - its stars are drawn ring-first too, the same draws
    # in both runs with only their cells and azimuths placed, so the stage's default selection (the 3162 brightest, in
    # luminosity order) is the same stars on and off but for the azimuth: sixteen of its seventeen columns are the
    # same bits, and `bright_star_limit` with them (a ring-first statistic now, held above).
    # S61 (D220 II.5): was every column but the azimuth (sixteen) - the young stars the clustering field places (20 to
    # 40.71 Myr: 2707 of the selection's 3162, measured) stand anywhere in their level-0 cell, so their radius moves
    # with the layer too; their height does not (its thin/thick criterion reads the same at the placed radius, measured:
    # the column is the same bits). Fifteen of the seventeen.
    same_stars = [d.name for d in br.COLUMNS if d.name not in ("bright_star_azimuth", "bright_star_radius")]
    # S61 (D220 items 1-4, the star sample's build): was 261 - the sample is drawn ring-first too, so its four statistics
    # are the same bits in both runs (RING_FIRST_STATISTICS, held above), and four of its columns are the same bytes
    # though the rows are in other cells: star_population and star_wolf_rayet are 0 for every star of this sample,
    # and star_wind_luminosity and star_bubble_radius are NaN but for one star, which stands at the same row in both
    # (measured).
    same_sample = ["star_bubble_radius", "star_population", "star_wind_luminosity", "star_wolf_rayet"]
    # S61 (D220 II.5): was 269 - bright_star_radius leaves what is held (above).
    assert len(held) == 268 and "bright_star_limit" in held and {"catalogue_size", "planet_count_sample", "mean_planets_per_star", "giant_fraction_sample"} <= set(held)
    assert sorted(n for n in held if b.decls[n].of not in (None, *UNPLACED_OBJECTS)) == sorted(["hii_density_bounded", *same_stars, *same_sample])
    assert not np.asarray(b.fields["hii_density_bounded"]).any()
    assert {"pitch_angle_drawn", "sun_azimuth", "arm_class", "arm_piece_width", "arm_design_count", "arm_power_budget", *pt.AMPLITUDE_FIELDS} <= set(held)


def test_the_oracle_holds_layer_off_on_a_small_grid_and_another_seed(prod):
    models = prod[0]
    given = {"systems_seed": 5, "pattern_seed": 2, "halo_mass": 8e11}
    a = run(models.get("azimuthal"), given, SMALL, layer=False)
    b = run(models.get("basic"), given, SMALL, layer=False)
    assert [n for n in b.fields if not same(a.fields[n], b.fields[n])] == []


# --- Appendix B applied: the four cloud columns, the cloud interior's noise ----------------------------------------


@pytest.mark.parametrize("name", MODELS)
def test_the_cloud_texture_columns_are_drawn_on_the_layer_s_seed_at_each_cloud_s_ring_identity(runs, prod, name):
    """Layer on: the stage's four columns are what a census materialised whole carries. S61 (D220 item 5): was "drawn
    on the streams they always were" - each cell's own stream ``(systems_seed, "cloud", cell, name)``. Since the
    ring-first draw they are the layer's own: each ring's arrays on ``(texture_seed, "cloud", ring, name)``, drawn
    whole and read at each cloud's place ``i`` in its ring's draw - so they do not depend on where the layer put the
    cloud, and rerolling ``texture_seed`` rerolls them (rule A10, BUILD_III section 1c rule 1)."""
    on = runs[name, True]
    for column in cl.TEXTURE_COLUMNS:
        assert on.decls[column].provenance == "synthetic" and on.decls[column].of == "cloud"
    m = prod[0].get(name)
    seed, texture = int(on.inputs["systems_seed"]), int(on.inputs["texture_seed"])
    layout = cl.cloud_layout(on.fields, on.grid.R, seed, constants(m))
    assert sum(k for _, k in layout.counts) == len(on.fields["cloud_size"]) == layout.ring.size
    size = np.asarray(on.fields["cloud_size"])
    for r in sorted(layout.sizes)[:12]:
        here = layout.ring == r
        n, i = layout.sizes[r], layout.index[here]

        def u(column: str) -> np.ndarray:
            return _seeds.rng(texture, "cloud", r, column).random(n)[i]

        want = {
            "cloud_source_offset": size[here] * np.cbrt(u("source_offset")),
            "cloud_source_angle": 2.0 * np.pi * u("source_angle"),
            "cloud_density_gradient": u("gradient"),
            "cloud_gradient_angle": 2.0 * np.pi * u("gradient_angle"),
        }
        for column, values in want.items():
            assert same(np.asarray(on.fields[column])[here], values), (r, column)
    # On the layer's seed, not the census's: at the default inputs the two seeds are the same number, so the streams
    # agree here; rerolling texture_seed alone rerolls the four (test_rerolling_texture_seed_moves_the_placements...).
    # S61 (D220 item 5): a layer-on census with its texture is given the run's texture_seed.
    census = cl.materialise_clouds(on.fields, on.grid.R, seed, constants(m), texture_seed=texture)
    for column in cl.WIRE_COLUMNS:
        assert same(census[column], on.fields[column]), column
    own = cl.materialise_clouds(on.fields, on.grid.R, seed, constants(m), texture=False)
    assert not set(cl.TEXTURE_COLUMNS) & set(own) and census.counts == own.counts
    # The offset lies inside its cloud, the gradient in [0, 1], the angles on the circle: the draws' own laws.
    offset, size = np.asarray(on.fields["cloud_source_offset"]), np.asarray(on.fields["cloud_size"])
    assert np.all((offset >= 0) & (offset <= size)) and np.all(np.asarray(on.fields["cloud_density_gradient"]) < 1.0)


@pytest.mark.parametrize("name", MODELS)
def test_the_cloud_texture_is_neutral_with_the_layer_off(runs, name):
    """No offset, no gradient, angles 0 - and a cluster then stands at its cloud's centre, exactly."""
    off = runs[name, False]
    n = len(off.fields["cloud_radius"])
    assert n > 16000
    for column in cl.TEXTURE_COLUMNS:
        value = np.asarray(off.fields[column])
        assert value.shape == (n,) and value.dtype == np.float64 and np.all(value == 0.0), column
    hosts = np.asarray(off.fields["cloud_cluster_index"]) >= 0
    assert hosts.sum() == len(off.fields["cluster_radius"]) > 12000
    assert same(off.fields["cluster_radius"], np.asarray(off.fields["cloud_radius"])[hosts])
    assert same(off.fields["cluster_azimuth"], np.asarray(off.fields["cloud_azimuth"])[hosts])
    assert same(off.fields["cluster_height"], np.asarray(off.fields["cloud_height"])[hosts])
    on = runs[name, True]
    hosts_on = np.asarray(on.fields["cloud_cluster_index"]) >= 0
    assert not same(on.fields["cluster_radius"], np.asarray(on.fields["cloud_radius"])[hosts_on])


def test_the_offset_s_declaration_states_what_it_does_not_keep_and_the_numbers_are_the_model_s(runs):
    """Gate G1, change 5 (BUILD_III section 1c rule 2 as amended: "a declaration states what it does not keep, with
    the measured number"). The source's offset and direction place the cluster, and a cluster can leave its cloud's
    ring. The declaration's numbers are measured here on the production grid at the default inputs, the layer on -
    so the text cannot drift from the model. No clamp: nothing here changes a value."""
    on = runs[DEFAULT_MODEL, True]
    F, R = on.fields, on.grid.R
    offset_decl, angle_decl = on.decls["cloud_source_offset"], on.decls["cloud_source_angle"]
    text = offset_decl.conserves
    assert text == angle_decl.conserves and text.startswith("The cloud's mass and the cluster's mass: the column places, it does not weigh.")
    # S56 (D215): were "1 610 of 12 930 clusters (12.5 %, 43.7 % of the cluster mass)" and "157 in another cell ring",
    # measured on S51's census at S55; the layer-on census is another draw since P1 and the declaration was re-read.
    # S57 (D216): were "at S56", "1 598 of 12 814 clusters (12.5 %, 43.8 % of the cluster mass)" and "137 in another
    # cell ring"; the census placed by the gas's steady response is another draw and the declaration was re-read.
    # S58 (D217): were "at S57", "1 598 of 12 829 clusters (12.5 %, 43.7 % of the cluster mass)" and "139 in another
    # cell ring"; the census placed by the response and the bar's lanes is another draw and the declaration was re-read.
    # S59 (D218): were "at S58", "1 600 of 12 826 clusters (12.5 %, 43.6 % of the cluster mass)" and "137 in another
    # cell ring"; the census placed by a response the winding's segments have turned is another draw. **The numbers
    # below are the model's as measured at S59; the declaration's text in `galaxy/layer/cloud_texture.py` is to be
    # re-read to them** - the test builder may not edit the model, and this test stands failing on these phrases
    # until the three strings there say what the model does (reported to the lead, with the strings).
    # S59 (D218 follow-up): were "by up to 249 pc in radius (its own length reaches 265 pc)", "1 581 of 12 839
    # clusters (12.3 %, 44.3 % of the cluster mass)" and "140 in another cell ring", the first build's census, which
    # the declaration was re-read to. With a segment's pitch relative to the disc's the census is another draw
    # again; the declaration's text in `galaxy/layer/cloud_texture.py` was re-read by the lead to the final model
    # (two readings of the model, the lead's builder's and this test's, the same numbers), and the phrases below
    # and the measurements under them are pinned together.
    # S60 (D219): were "at S59", "by up to 223 pc in radius (its own length reaches 255 pc)", "1 576 of 12 840
    # clusters (12.3 %, 42.9 % of the cluster mass)" and "142 in another cell ring". The pieces' census is another
    # draw; the numbers below are the final model's as measured, and - as at S59 - **the declaration's text in
    # `galaxy/layer/cloud_texture.py` is to be re-read to them** (the re-pin may not edit the model): this test stands
    # failing on these phrases until the strings there say what the model does (reported to the lead).
    # S61 (D220 items 1 and 6): were "at S60", "by up to 249 pc in radius (its own length reaches 265 pc)", "1 605 of
    # 12 916 clusters (12.4 %, 42.9 % of the cluster mass)", "140 in another cell ring", "`nebular` and `bubbles` bin
    # from it" and "#95; L1 decides". The census drawn ring-first is a new draw, re-read; and the binners read the
    # cloud's radius since, which the declaration now says.
    # S61 (D220 part II as amended): were "by up to 229 pc", "1 629 of 12 710 clusters (12.8 %, 37.4 % ...)", "161 in
    # another cell ring" and "bin a cluster by its cloud's radius" - the clouds are placed within their cells by the
    # clustering field, so the offsets start from other centres; the binners read the radius the cloud's ring drew.
    # S67 (D231): were "at S61", "by up to 230 pc in radius (its own length reaches 248 pc)", "1 581 of 12 710 clusters
    # (12.4 %, 36.1 % of the cluster mass)" and "133 in another cell ring" - the clouds' size law shrinks the inner
    # clouds the offset is drawn inside (the giants held at 150 pc), so the declaration was re-read to the model.
    for phrase in ("at S67 the offset moves a cluster",
                   "by up to 140 pc in radius (its own length reaches 146 pc) against a 75 pc radial step",
                   "1 376 of 12 710 clusters (10.8 %, 31.8 % of the cluster mass)",  # S62 (D221 item 7 as amended): was 1 582 - the spurs move the clouds' sector shares
                   "119 in another cell ring", "`nebular` and `bubbles` bin a cluster by the radius its cloud's ring drew",
                   "`cluster_birth_radius`", "No clamp"):
        assert phrase in text, phrase
    # The two gradient columns lean a cloud's density and place nothing outside it: they keep their declaration.
    for name in ("cloud_density_gradient", "cloud_gradient_angle"):
        assert on.decls[name].conserves.startswith("The cloud's mass and the census's count") and "249 pc" not in on.decls[name].conserves
    hosts = np.asarray(F["cloud_cluster_index"]) >= 0
    cloud_r, cluster_r = np.asarray(F["cloud_radius"])[hosts], np.asarray(F["cluster_radius"])
    mass = np.asarray(F["cluster_mass"])
    step = float(R[1] - R[0])
    # S61 (D220): the ring-first census, a new draw (the count on the assertion below). And the binners' radius is the cloud's.
    # S61 (D220 part II as amended): was `cloud_r`, the cloud's radius - since the clouds are placed within their cells,
    # the binners' radius is the one the cloud's ring drew.
    assert np.array_equal(np.asarray(F["cluster_birth_radius"]), np.asarray(F["cloud_birth_radius"])[hosts])
    assert step * 1000.0 == pytest.approx(75.0) and cluster_r.size == 12710  # S61 (D220): was 12916; S60 fourth pass: was 12840; S59 (D218 follow-up): was 12839; S59 (D218): was 12826 (S58: 12829; S57: 12814; S56: 12930)
    # "another radial ring": the grid ring whose centre is nearest, the cluster's against its cloud's.
    ring = lambda r: np.floor((r - R[0]) / step + 0.5).astype(int)  # noqa: E731
    moved = ring(cloud_r) != ring(cluster_r)
    # S57 (D216): was 1598 and 0.1247 of 12 814 (S56: 1610, 0.125) - the same count of another census, by chance.
    # S58 (D217): was 1598 and 0.1246 of 12 829.
    # S59 (D218): was 1600 and 0.1247 of 12 826.
    # S59 (D218 follow-up): was 1581 and 0.1231 of 12 839.
    # S60 fourth pass: was 1576 and 0.1227 of 12 840.
    # S61 (D220): was 1605 and 0.1243 of 12 916 (the ring-first census, a new draw).
    # S61 (D220 part II as amended): was 1629 and 0.1282 - the clouds placed within their cells.
    # S62 (D221 item 7 as amended): was 1582 - the gas spurs move the clouds' sector shares, and one cluster's cloud with them.
    # S67 (D231): was 1581 and 0.1244 - the clouds' size law: the inner clouds smaller, the offsets inside them shorter.
    assert int(moved.sum()) == 1376 and moved.mean() == pytest.approx(0.1083, abs=5e-4)
    # The share of the cluster mass that crosses: 0.42939, printed as 42.9 %. S57 (D216): was 0.43796 (43.8 %).
    # S58 (D217): was 0.4373 (43.7 %). S59 (D218): was 0.43648 (43.6 %). S59 (D218 follow-up): was 0.44329 (44.3 %).
    # S60 fourth pass: was 0.42939 (42.9 %); 0.42923 now, printed as 42.9 % still.
    # S61 (D220): was 0.4292 (42.9 %); 0.37412 now, printed as 37.4 % (the ring-first census, a new draw).
    assert mass[moved].sum() / mass.sum() == pytest.approx(0.3182, abs=5e-4)  # S67 (D231): was 0.3614. S61 (D220 part II as amended): was 0.3741
    edges, _ = sy.cell_edges(R)
    # S57 (D216): was 137 (S56: 157). S58 (D217): was 139. S59 (D218): was 137. S59 (D218 follow-up): was 140.
    assert int((np.searchsorted(edges, cloud_r, side="right") != np.searchsorted(edges, cluster_r, side="right")).sum()) == 119  # S67 (D231): was 133. S61 (D220 part II as amended): was 161. S61 (D220): was 140. S60 fourth pass: was 142
    # 223 pc is the largest radial displacement of a cluster from its cloud; the offset's own length reaches 255 pc
    # (it is not all radial), and it is the radial part that crosses rings. The gate's text said "the offset reaches
    # 249 pc"; the declaration says which of the two each number is (D214, the close).
    # S59 (D218 follow-up): were 248.5 and 265.2 pc - both one cloud's, the census's most massive (9.98e6 Msun, at
    # 3.0 kpc), which the first build's census held and this draw does not; the two largest now are clouds both
    # censuses hold (at 2.5 and 3.5 kpc).
    # S60 fourth pass: were 223.3 and 255.5 pc; on the pieces' census they read 248.5 and 265.2 pc, the numbers of
    # S59's first build again.
    # S61 (D220): were 248.5 and 265.2 pc - the ring-first census is a new draw and its texture is drawn on
    # texture_seed (D220 item 5), so the offsets are other numbers: 229.5 and 248.4 pc.
    # S67 (D231): were 229.9 and 248.4 pc - the largest clouds held at 150 pc by the size law, so no offset can pass it.
    assert np.abs(cluster_r - cloud_r).max() * 1000.0 == pytest.approx(140.4, abs=0.1)  # S61 (D220 part II as amended): was 229.5
    assert np.asarray(F["cloud_source_offset"]).max() == pytest.approx(146.4, abs=0.1)


def test_the_cloud_interior_s_noise_is_three_constants_of_the_model(runs, prod):
    """D214 section 5 as ruled at gate G1 (change 4): "the three interior scalars are not synthetic. A constant 4, 2,
    0.5, the same on and off, is not 'a realisation from the layer's seed'. They are parameters of a synthetic
    function and are published as constants of the model ... not as fields of any stage". Three level-0 constants,
    declared by the layer's stage, carried by /api/clouds' header as ``cloud_interior`` - the one constant this API
    serves, by the gate's explicit exception (rule D5 as amended: a parameter of a function the viewer evaluates)."""
    models, impls_, _ = prod
    names = dict(cloud_texture.INTERIOR_CONSTANTS)
    assert names == {"octaves": "CLOUD_INTERIOR_OCTAVES", "lacunarity": "CLOUD_INTERIOR_LACUNARITY", "gain": "CLOUD_INTERIOR_GAIN"}
    for m in models:
        c = constants(m)
        assert cloud_texture.interior(c) == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert isinstance(cloud_texture.interior(c)["octaves"], int)
        for constant in names.values():
            about = m.constants[constant].about
            assert "The viewer's own choice, none read, #110" in about and "[verified: frontend/src/galaxy/region.ts at tag s54" in about
        # Declared by the layer's stage and by no other; not a field of any stage, in either run.
        readers = sorted(sid for _, sid in m.stages if set(names.values()) & set(impls_.get(sid).reads_constants))
        assert readers == ["cloud_texture"] and set(names.values()) <= set(impls_.get("cloud_texture").reads_constants)
    for out in runs.values():
        assert not [n for n in out.fields if "cloud_interior" in n]
    assert [d.name for d in impls_.get("cloud_texture").publishes] == list(cl.TEXTURE_COLUMNS)
    # A parameter set that is not a noise is refused where it is read.
    good = constants(models.get(DEFAULT_MODEL))
    for constant, bad in (("CLOUD_INTERIOR_OCTAVES", 0), ("CLOUD_INTERIOR_OCTAVES", 2.5), ("CLOUD_INTERIOR_LACUNARITY", 0.0),
                          ("CLOUD_INTERIOR_GAIN", float("nan"))):
        with pytest.raises(ValueError, match="cloud-interior noise"):
            cloud_texture.interior({**good, constant: bad})
    # The API: the exception is this one key of this one route, by the wire's names; no constant's name is served,
    # and no other response carries the key.
    svc = Service(grid=SMALL)
    for query in (SECTOR, SECTOR + "&layer=off", "model=basic&" + SECTOR):
        header = svc.handle("/api/clouds", query).frame()[0]
        assert header["cloud_interior"] == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
        assert set(header["scalars"]) == {"cloud_count_total", "cloud_forcing_parameter", "cloud_lifetime", "cloud_extinction_v"}
        assert not re.search(r"CLOUD_INTERIOR", json.dumps(header))
    for path in INPUT_ROUTES:
        if path != "/api/clouds":
            assert "cloud_interior" not in svc.handle(path, QUERIES[path]).frame()[0], path
    for path in ("/api", "/api/fields", "/api/stages", "/api/inputs", "/api/templates"):
        text = svc.handle(path).body.decode("utf-8")
        assert "CLOUD_INTERIOR" not in text and '"constants"' not in text, path
    source = (ROOT / "frontend" / "src" / "galaxy" / "region.ts").read_text(encoding="utf-8")
    # Since builder D (S55) the viewer holds none of the three: it evaluates the interior with what the clouds'
    # header publishes, and keeps one measured normaliser with the parameter set it was measured for. The guard
    # therefore runs the other way round: the viewer names no octave count of its own, and the set its measured
    # constant belongs to is the layer's.
    assert "export const OCTAVES" not in source
    m = re.search(r"measuredFor: \{ octaves: (\d+), lacunarity: ([\d.]+), gain: ([\d.]+) \}", source)
    assert m, "region.ts no longer records which parameters its measured normaliser belongs to"
    interior = cloud_texture.interior(good)  # the model's constants: what the measured normaliser must belong to
    assert (float(m[1]), float(m[2]), float(m[3])) == (interior["octaves"], interior["lacunarity"], interior["gain"])


def test_a_synthetic_field_declares_what_it_stands_in_for_what_it_conserves_and_its_statistic():
    base = dict(name="f", label="f", unit="dimensionless", kind=Kind.FIELD, axes=("R",), ramp=Ramp("greys"), about="a test field")
    ok = FieldDecl(**base, **SYNTHETIC)
    assert ok.provenance == "synthetic" and ok.contract()[-5:-2] == ("a physics", "a total", "none read (#95)")
    for missing in SYNTHETIC_DECLARATIONS:
        with pytest.raises(DeclarationError, match="a synthetic field declares"):
            FieldDecl(**base, **{**SYNTHETIC, missing: "  "})
    for kind in ("derived", "seeded"):
        FieldDecl(**base, provenance=kind)
        for given in SYNTHETIC_DECLARATIONS:
            with pytest.raises(DeclarationError, match="synthetic field's declarations"):
                FieldDecl(**base, provenance=kind, **{given: "said anyway"})
    # "none read" is a debt and names it; a cited statistic needs no debt.
    for unsourced in ("none read", "None read: no source", "none read (debt ninety-five)"):
        with pytest.raises(DeclarationError, match="names it"):
            FieldDecl(**base, **{**SYNTHETIC, "statistic": unsourced})
    FieldDecl(**base, **{**SYNTHETIC, "statistic": "a power spectrum of slope -2.7 [verified: a source]"})
    assert FieldDecl(**base, **{**SYNTHETIC, "statistic": "none read (#110)"}).statistic.endswith("(#110)")
    with pytest.raises(DeclarationError, match="provenance"):
        FieldDecl(**base, provenance="composed")


DOES_NOT_KEEP = re.compile(r"(?:[Ii]t does not keep|Nor does it keep)\b(.*)", re.DOTALL)


def test_every_synthetic_declaration_says_what_it_does_not_keep_with_the_number(prod):
    """S70 (D234, Audit V F-3-13): BUILD_III section 1c rule 2 - "a declaration states what it does not keep, with the
    measured number" - asserted of every synthetic field the production stages publish (until S70 of two; the
    arm pieces' and the gas spurs' columns and the two gradient columns went unasserted, and the pieces' and the
    gradients' declarations carried no number). The clause and a figure after it; the number's sense is the
    declaration's, read by the tests of each field."""
    _, impls_, _ = prod
    synthetic = {d.name: d for st in impls_ for d in st.publishes if d.provenance == "synthetic"}
    assert len(synthetic) == len(cl.TEXTURE_COLUMNS) + len(pt.PIECE_FIELDS) + len(CLUSTERING_FIELDS) + len(ADDED_AT_S62_SPURS) + len(GAS_FIELDS)
    for n, d in synthetic.items():
        clause = DOES_NOT_KEEP.search(d.conserves)
        assert clause and re.search(r"\d", clause.group(1)), (n, d.conserves)
    # The four the audit named, by what their number says.
    assert "0.47 of the budget" in synthetic["arm_piece_chain"].conserves and "#195" in synthetic["arm_piece_chain"].conserves
    assert "at most 0.0092 of a ring" in synthetic["gas_spur_chain"].conserves
    for n in ("cloud_density_gradient", "cloud_gradient_angle"):
        assert "16 577 clouds" in synthetic[n].conserves and "at most 0.99998" in synthetic[n].conserves, n


def test_rule_5_a_stored_cell_number_is_recomputed_at_a_point_from_the_seed_and_the_cell(small, prod):
    """S70 (D234, Audit V F-3-15; BUILD_III section 1c rule 5 as amended: "no stored grid a point cannot recompute").
    The clustering field's mean in a level-0 cell and the gas field's normaliser there are stored per cell; each is
    recomputed here for one cell alone - from the published seed, the model's constants, the ring's published
    parameters and the cell's edges, nothing of any other cell - and is the published number to the bit."""
    from galaxy.layer import census_clustering as l1
    from galaxy.layer import gas_fluctuation as gas
    from galaxy.layer import noise

    out = small[DEFAULT_MODEL, True]
    F, R, c = out.fields, out.grid.R, constants(prod[0].get(DEFAULT_MODEL))
    rings, sectors = sy.cell_edges(R)
    points = int(c[l1.TABLE_POINTS])
    clustering = l1.ClusteringField.of(F["census_clustering_seed"], c)
    params = {key: np.asarray(F[name], dtype=float) for name, key in gas.RING_KEYS.items()}
    params |= {"edges": rings, "sense": gas.disc_sense(F["pitch_angle"])}
    fluctuation = gas.field_of(int(F["gas_fluctuation_seed"]), params, c)  # no stored normaliser handed in
    finest = gas.l1_finest_frequency(c)
    for cell in (0, 8 * sy.CELL_SECTORS + 5, 517, sy.CELL_COUNT - 1):
        r, s = divmod(cell, sy.CELL_SECTORS)
        lo, hi, a, b = float(rings[r]), float(rings[r + 1]), float(sectors[s]), float(sectors[s + 1])
        r_mid, phi_mid = clustering.lattice(lo, hi, a, b, points)
        q = noise.cell_quadrature(lo, hi, a, b, (r_mid.size, phi_mid.size))
        e = clustering.map(q[:, 0] * np.cos(q[:, 1]), q[:, 0] * np.sin(q[:, 1]))
        assert float(np.sum(q[:, 0] * e) / np.sum(q[:, 0])) == float(np.asarray(F["census_clustering_cell_mean"])[cell]), cell
        lattice = fluctuation.cell_lattice(r, s, points, finest)[None]
        g = fluctuation.gaussian_polar(lattice[..., 0], lattice[..., 1], r)
        alone = float(noise.lognormal_normaliser(g, float(fluctuation.sigma[r]), lattice[..., 0])[0])
        assert alone == float(np.asarray(F["gas_fluctuation_cell_normaliser"])[cell]), cell


def test_a_composed_field_declares_itself_and_its_neutral_value():
    """Gate G1, change 3: composed is a declaration with its neutral value, the two refused apart, and nothing is
    read off the axes - a field over phi is not composed unless it says so, and a composed one need not be over phi."""
    over_phi = dict(name="f", label="f", unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"), ramp=Ramp("greys"), about="a test field")
    plain = FieldDecl(**over_phi)
    assert plain.composed is False and plain.neutral is None and plain.contract()[-2:] == (False, None)
    declared = FieldDecl(**over_phi, composed=True, neutral=1)
    assert declared.composed is True and declared.neutral == 1.0 and isinstance(declared.neutral, float)
    assert declared.contract()[-2:] == (True, 1.0) and declared.contract() != plain.contract()
    radial = FieldDecl(**{**over_phi, "axes": ("R",)}, composed=True, neutral=0.0)  # the axes say nothing either way
    assert radial.composed and radial.neutral == 0.0
    with pytest.raises(DeclarationError, match="a neutral value is a composed field's declaration"):
        FieldDecl(**over_phi, neutral=1.0)
    for missing in (None, float("nan"), float("inf"), True, "1"):
        with pytest.raises(DeclarationError, match="declares its neutral value"):
            FieldDecl(**over_phi, composed=True, neutral=missing)
    with pytest.raises(DeclarationError, match="composed is True or False"):
        FieldDecl(**over_phi, composed=1, neutral=1.0)
    # A composed field is a continuous grid field: a scalar or a column is not composed.
    with pytest.raises(DeclarationError, match="continuous grid field"):
        FieldDecl(name="s", label="s", unit="dimensionless", kind=Kind.SCALAR, about="a scalar", composed=True, neutral=1.0)
    # compose gives the declared neutral, and refuses a field that does not declare one.
    assert np.all(compose.neutral(declared, (2, 3)) == 1.0) and compose.neutral(radial, (4,)).tolist() == [0.0] * 4
    with pytest.raises(LayerError, match="not declared composed"):
        compose.neutral(plain, (2, 3))
    # No source in the model reads the axes to decide it: FieldDecl holds a field named composed, not a property.
    source = (PACKAGE / "core" / "fielddoc.py").read_text(encoding="utf-8")
    assert "composed: bool = False" in source and '"phi" in self.axes' not in source
    for path in model_sources():
        assert not re.search(r'["\']phi["\'] in \w+(\.\w+)*\.axes', path.read_text(encoding="utf-8")), path.name


def test_texture_seed_is_the_fifth_seed_and_the_arm_pieces_read_it(prod):
    """D214 section 3 said: "this test fails the day a stage reads ``texture_seed`` (BUILD_III phase P1's mode
    phases): remove ``graph.UNREAD_BY_RULING["texture_seed"]`` then, and this test's first half with it". That day
    was S56 (D215): the layer's ``arm_phases`` stage reads it at the pattern's checkpoint, the seed binds there like
    every other, and the graph's one named exception is spent - the mapping is empty. S60 (D219): the layer's stage
    is ``arm_pieces``, the census of arm pieces, at the same checkpoint."""
    models, impls_, table = prod
    assert [s.name for s in seeds()] == ["world_seed", "pattern_seed", "systems_seed", "planets_seed", "texture_seed"]
    assert dict(graph.UNREAD_BY_RULING) == {}
    readers = sorted(st.id for st in impls_ if "texture_seed" in st.reads_seeds)
    # S60 (D219): was ["arm_phases"] - the layer's stage is the census of arm pieces, at the same checkpoint.
    # S61 (D220 item 5): was ["arm_pieces"] - the cloud texture is drawn on the layer's seed; its stage reads the
    # systems seed beside it for the census's layout alone (which ring and place each published cloud is).
    # S61 (D220 part II): was ["arm_pieces", "cloud_texture"] - the censuses' clustering field is on the layer's seed.
    # S62 (D221 item 7 as amended): was ["arm_pieces", "census_clustering", "cloud_texture"] - the gas spurs' first feet;
    # S62 (D221): and the gas fluctuation field, on the clustering field's path.
    assert readers == ["arm_pieces", "census_clustering", "cloud_texture", "gas_fluctuation", "gas_spurs"] and impls_.get("arm_pieces").layer_stage and impls_.get("arm_pieces").checkpoint == 3
    assert impls_.get("census_clustering").layer_stage and impls_.get("census_clustering").reads_seeds == ("texture_seed",)
    assert impls_.get("gas_fluctuation").layer_stage and impls_.get("gas_fluctuation").reads_seeds == ("texture_seed",)
    assert impls_.get("cloud_texture").layer_stage and impls_.get("cloud_texture").reads_seeds == ("systems_seed", "texture_seed")
    # S58 (D217 item 9): was `requires == ()` - the stage asks whether there is a bar, whose two-armed mode it ties.
    # S59 (D218 item 2): was `reads_constants == ()` - the stage lays the winding's segments too, and reads the five
    # numbers of their draw: the extent's median, log-width and two bounds, and the pitch residual's width.
    # S59 (D218 follow-up): was five, `ARM_SEGMENT_PITCH_SCATTER` the fifth - the stage draws a unit normal row and
    # no width; the spread is the law's (`ARM_SEGMENT_PITCH_RELATIVE_SCATTER`, read and published by the `bar` stage).
    # S60 (D219 items 2-3 and 8): was `requires == ("bar_present",)` - the census is laid by the disc's pitch, its
    # class, the bar's half-length (no chain born inside it), the law's arm number (how many chains cross a ring)
    # and the Sun's azimuth (where a template's measured arms are placed); it reads the measured arms as its one
    # input, and the twelve numbers of its draws - S59's four of a piece's extent and the pitch's spread, now drawn
    # per piece, a chain's length by class, and a flocculent piece's range.
    assert impls_.get("arm_pieces").requires == ("pitch_angle", "arm_class", "bar_half_length", "arm_design_count", "sun_azimuth")
    assert impls_.get("arm_pieces").reads_inputs == ("arm_pieces",)
    assert impls_.get("arm_pieces").reads_constants == (
        "ARM_SEGMENT_EXTENT_MEDIAN", "ARM_SEGMENT_EXTENT_LOG_SCATTER", "ARM_SEGMENT_EXTENT_MIN", "ARM_SEGMENT_EXTENT_MAX",
        "ARM_SEGMENT_PITCH_RELATIVE_SCATTER",
        "ARM_CHAIN_LENGTH_GRAND_DESIGN", "ARM_CHAIN_LENGTH_GRAND_DESIGN_SCATTER",
        "ARM_CHAIN_LENGTH_MULTI_ARMED", "ARM_CHAIN_LENGTH_MULTI_ARMED_SCATTER", "ARM_CHAIN_LENGTH_MIN",
        "ARM_PIECE_FLOCCULENT_EXTENT_MIN", "ARM_PIECE_FLOCCULENT_EXTENT_MAX",
    )
    assert "ARM_SEGMENT_PITCH_RELATIVE_SCATTER" not in impls_.get("bar").reads_constants  # S60: the spread is the pieces' draw's
    assert "ARM_SEGMENT_PITCH_SCATTER" not in models.get(DEFAULT_MODEL).constants
    assert [d.name for d in impls_.get("arm_pieces").publishes] == list(pt.PIECE_FIELDS)
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert g.input_checkpoint["texture_seed"] == 3 == INPUTS["texture_seed"].checkpoint_hypothesis
        assert g.unread_by_ruling == () and g.unbound_inputs == ()  # every input is read
    header = Service(grid=SMALL).handle("/api/clouds", SECTOR + "&texture_seed=12").frame()[0]
    assert header["inputs"]["texture_seed"] == 12
    # A seed nobody may leave unread without a ruling: an unread one is reported, texture_seed among them now.
    unread = stage("s", ("f",))
    g = graph.analyse(model("m", unread), impls(unread), INPUTS)
    assert "world_seed" in g.unbound_inputs and "texture_seed" in g.unbound_inputs


def test_rerolling_texture_seed_moves_the_placements_and_no_law(prod):
    """BUILD_III section 1c rule 1: "rerolling it changes placements and texture and nothing else" - true of
    something for the first time at S56 (gate G1 noted that until P1 no field was on the layer's seed). Two runs of
    the whole model that differ in ``texture_seed`` alone:

    - the five phases differ, and with them the four composed fields and where every placed census's objects are;
    - **no law moves**: every radial field, every history and every scalar that is not a census statistic is the
      same bits - the amplitudes, the saturation, the pitch, the gas's ratio, every profile;
    - every census expects the same count in every ring, to 1e-12 (I2, between two realisations);
    - what does move outside the placements is the closed list of census statistics, and nothing else: the realised
      objects are another draw until L1, exactly as between the layer on and off."""
    m = prod[0].get(DEFAULT_MODEL)
    a, b = run(m, {"texture_seed": 0}, SMALL), run(m, {"texture_seed": 987654321}, SMALL)
    assert b.inputs["texture_seed"] == 987654321 and a.order == b.order and set(a.fields) == set(b.fields)
    # Two scalars are a census's *expected* total - the expected counts summed over every cell, each carrying its
    # sector's placement weight. The weights average to 1 round a ring to rounding, not to the bit, so the sum is
    # the same to 1e-12 (rule 2: "no expected count or expected total") and can differ in its last bit between
    # two realisations: measured 1 ulp here. (Between the layer on and off at the default seeds they were the same
    # bits until the window was corrected, and are a unit or two in the last place apart since: EXPECTED_TOTALS.)
    expected_totals = EXPECTED_TOTALS
    moved_statistics, placed = set(), set()
    for n, d in a.decls.items():
        equal = same(a.fields[n], b.fields[n])
        if n in expected_totals:
            # S70 (D234, Audit V F-3-12): was `pytest.approx(rel=1e-12)` - about 4 600 units in the last place at
            # 16 693, where I1 holds an expected total to its units; held to the same margin as on and off.
            assert same_expected_total(a.fields[n], b.fields[n]), (n, float(a.fields[n]), float(b.fields[n]))
        elif d.composed:
            # S60 (D219): the five phases are retired; every composed field - the contrast, the pieces' amplitude,
            # the chains crossing, the realised power and its split - is another realisation. The cut of the
            # amplitude is 1 on every ring where nothing is cut, and may be 1 under both seeds (it is on this grid).
            assert not equal or n == "arm_piece_saturation", n
            if n == "arm_piece_saturation":
                assert np.all((np.asarray(a.fields[n]) > 0.0) & (np.asarray(a.fields[n]) <= 1.0)), n
        elif n in CLUSTERING_FIELDS:
            # S61 (D220 part II): another seed, another field - and so other means in the cells.
            assert d.provenance == "synthetic" and not equal, n
        elif n in GAS_FIELDS:
            # S62 (D221): another seed, another gas field and other cell normalisers; the ring table is the physics
            # read per ring (the break, the Mach number, the width, the strain, the twist, the sum's normaliser).
            assert d.provenance == "synthetic" and (equal if n in GAS_RING_FIELDS else not equal), n
        elif d.kind.domain == "table":
            # S59 (D218 items 1-2): the layer's table is on the layer's seed - re-laid, row for row.
            # S60 (D219 item 7): the census of arm pieces - other pieces, and as many rows as the laying makes (the
            # count is the draws' own, not fixed); the pinned rows are the template's, and the default has none.
            # S62 (D221 item 7 as amended): and the gas spurs' census, laid on the re-laid chains with other first feet.
            assert d.of in LAYER_TABLES and n in pt.PIECE_FIELDS + _SPUR_FIELDS, n
            assert d.provenance == "synthetic" and np.asarray(a.fields[n]).size > 0 and np.asarray(b.fields[n]).size > 0, n
            if n in ("gas_spur_arc", "gas_spur_radius", "gas_spur_azimuth"):
                assert not equal, n
            if n in ("arm_piece_start_radius", "arm_piece_start_azimuth", "arm_piece_pitch", "arm_piece_extent"):
                assert not equal, n  # the drawn numbers of the pieces; the integer columns may land alike
        elif d.kind.domain == "object":
            if d.of in UNPLACED_OBJECTS:
                assert equal, n
            elif not equal:
                placed.add(d.of)
        elif n in RING_FIRST_STATISTICS:
            # S61 (D220 item 4): the same objects under either realisation, summed in another order.
            assert same_ring_first(a.fields[n], b.fields[n]), n
        elif not equal:
            moved_statistics.add(n)
    assert moved_statistics <= set(CENSUS_STATISTICS), sorted(moved_statistics - set(CENSUS_STATISTICS))
    assert placed == PLACED_OBJECTS
    # S61 (D220 item 5): rerolling texture_seed rerolls the clouds' interiors - all four texture columns.
    assert all(not same(a.fields[n], b.fields[n]) for n in cl.TEXTURE_COLUMNS)
    # S61 (D220 part II item 4): and the clouds' azimuths within their sectors, by the clustering field (and the
    # clusters' with them); the clouds' radii are the ring stream's and do not move.
    assert not same(a.fields["cloud_azimuth"], b.fields["cloud_azimuth"]) and not same(a.fields["cluster_azimuth"], b.fields["cluster_azimuth"])
    # S59 (D218): the winding's anchor and the pitch as the law draws it join the laws named here.
    # S60 (D219): the anchor is retired; the class, the width of a piece, the law's arm number and the budget join.
    for n in (*pt.AMPLITUDE_FIELDS, "arm_saturation", "arm_multiplicity", "arm_contrast", "bar_contrast", "pitch_angle",
              "gas_arm_contrast", "bar_pattern_speed", "sfr_surface_density", "stellar_surface_density", "disc_luminosity",
              "pitch_angle_drawn", "arm_class", "arm_piece_width", "arm_design_count", "arm_power_budget"):
        assert same(a.fields[n], b.fields[n]), n
    expect_a, expect_b = ring_expectations(a, m), ring_expectations(b, m)
    for census in expect_a:
        assert np.allclose(expect_a[census], expect_b[census], rtol=1e-12, atol=0.0), census
    # Each composed field keeps every ring's mean under either realisation. S57 (D216 G3 item 4): the first build
    # had pinned the gas's at 1.257e-3 and 1.54e-4 on these 36 cells (its centre samples, no longer divided by
    # their mean); the published field is the law's exact mean over each cell's azimuth on its ring, and the three are at
    # 1e-12 again.
    for out in (a, b):
        for n in ("pattern_density_contrast", "gas_density_contrast", "star_formation_gas_contrast", "sfr_modulation"):
            assert float(np.abs(np.asarray(out.fields[n]).mean(axis=1) - 1.0).max()) < 1e-12, n


# --- one reader of the switch (rule B13) ---------------------------------------------------------------------------


def model_sources() -> list[Path]:
    files = sorted(PACKAGE.rglob("*.py"))
    assert len(files) > 50
    return files


def test_compose_is_the_only_caller_of_from_fields():
    """A pattern object is obtained from ``compose`` or not at all: ``.from_fields(`` appears in the model only where
    it is defined (the two pattern classes) and where compose calls it.

    **S59 (D218) - amended by the test builder, and the lead's to rule** (not a re-pin the ruling explains: reported).
    The S59 build gave the winding a door of the same name: ``Winding.from_fields(fields)``, called once in each
    pattern class's own ``from_fields`` - inside the door compose opens - so this test's text search found the name
    in the two stage modules and failed. What the test is for still holds, and is held more closely than by a
    search of the text: by the syntax tree, the only calls of a ``from_fields`` outside ``compose`` are those two,
    each ``Winding.from_fields`` and each inside ``ArmPattern.from_fields`` or ``GasPattern.from_fields``; no module
    but ``compose`` calls a pattern class's. (``Winding.from_fields`` gives None where the layer laid no row - it
    reads the rows, not the setting; ``compose`` has already returned None with the layer off before it is
    reached.) If the invariant is to be kept to its letter - "none calls ``.from_fields(``" - the model must hand
    the winding in through ``compose``, and this amendment is to be reverted with that change."""
    calls: dict[str, int] = {}
    for path in model_sources():
        text = path.read_text(encoding="utf-8")
        found = len(re.findall(r"\.from_fields\(", text))
        if found:
            calls[path.relative_to(PACKAGE).as_posix()] = found
    # S59 (D218): was `set(calls) == {"layer/compose.py"}` - the two pattern modules each name the winding's door once.
    # S60 (D219): was {"layer/compose.py": 3, "stages/gas_pattern.py": 1, "stages/pattern.py": 1} - the winding is
    # retired; the stellar pattern lives in `stages/pieces.py` and names the census's door (``Pieces.from_fields``)
    # once, inside its own ``from_fields``, as it named the winding's; the gas pattern no longer opens a door of its
    # own (it is handed the stellar pattern by compose).
    assert calls == {"layer/compose.py": 3, "stages/pieces.py": 1}, calls
    # compose's three: the stellar pattern, the gas pattern, and the docstring that says so. The other one, by the tree:
    outside: list[tuple[str, str, str, str]] = []  # (module, the class called on, the class it is called in, the function)
    for path in model_sources():
        name = path.relative_to(PACKAGE).as_posix()
        if name == "layer/compose.py":
            continue
        for cls in (n for n in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(n, ast.ClassDef)):
            for fn in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "from_fields":
                        outside.append((name, ast.unparse(node.func.value), cls.name, fn.name))
    assert outside == [("stages/pieces.py", "Pieces", "ArmPattern", "from_fields")]
    # ... and there is no call of one anywhere else in those modules (at module level, or in a plain function).
    for name, count in (("stages/gas_pattern.py", 0), ("stages/pieces.py", 1), ("stages/pattern.py", 0)):
        tree = ast.parse((PACKAGE / name).read_text(encoding="utf-8"))
        assert sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "from_fields") == count, name
    defined = [p.relative_to(PACKAGE).as_posix() for p in model_sources() if "def from_fields(" in p.read_text(encoding="utf-8")]
    assert defined == ["stages/gas_pattern.py", "stages/pieces.py"]
    # Three doors by that name: the two pattern classes', which compose alone opens, and the census's, which the
    # stellar pattern opens.
    source = (PACKAGE / "stages" / "pieces.py").read_text(encoding="utf-8")
    assert source.count("def from_fields(") == 2 and (PACKAGE / "stages" / "gas_pattern.py").read_text(encoding="utf-8").count("def from_fields(") == 1


def test_no_module_of_the_model_constructs_a_pattern_object_by_its_class():
    """Gate G1, change 8: ``.from_fields(`` is one door to a pattern object and the constructor is the other. Nothing
    in the model calls ``ArmPattern(`` or ``GasPattern(`` - read from the syntax tree, so a type annotation or a
    docstring is not a call.

    S56 (D215): until S56 the two pattern modules each called ``ArmPattern(`` once - the ``pattern`` stage built the
    stellar law from the numbers it had just drawn, and the gas law built a stellar law of unit amplitude to take
    its weights and phase from. Both are gone: the ``pattern`` stage hands its law to ``compose.stellar_pattern``,
    which reads the layer's phases and builds the object through ``from_fields``, and the gas law takes the taper
    and the phase from ``pattern.bar_terms``. So the second door is shut for the whole model: every pattern object
    comes through ``compose``."""
    calls: dict[str, dict[str, int]] = {}
    for path in model_sources():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            called = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            if called in ("ArmPattern", "GasPattern"):
                where = calls.setdefault(path.relative_to(PACKAGE).as_posix(), {})
                where[called] = where.get(called, 0) + 1
    # S56 (D215): was {"stages/pattern.py": {"ArmPattern": 1}, "stages/gas_pattern.py": {"ArmPattern": 1}}.
    assert calls == {}, calls
    # The text agrees with the tree: the token appears in no module's code or comments either.
    for path in model_sources():
        name = path.relative_to(PACKAGE).as_posix()
        assert not re.search(r"\b(ArmPattern|GasPattern)\(", path.read_text(encoding="utf-8")), name
    # And the one door is compose's: the composing stage asks it for its own composed fields' pattern.
    # S60 (D219): was `stages/pattern.py` and `law=` in it - the composing stage is `stellar_pattern` in
    # `stages/pieces.py`, and it reads the law published before it, so it hands compose no law of its own.
    source = (PACKAGE / "stages" / "pieces.py").read_text(encoding="utf-8")
    assert "_compose.stellar_pattern(" in source and "_compose.stellar_pattern(" not in (PACKAGE / "stages" / "pattern.py").read_text(encoding="utf-8")


SWITCH_WORDS = ("setting", "words")  # compose's two answers in words: "on" / "off", and a sentence that says it


def says_the_word(node: ast.AST) -> bool:
    """A call of compose's ``setting`` / ``words``: ``_compose.setting(f)``, or ``setting(f)`` after a bare-name import
    (``from galaxy.layer.compose import setting``)."""
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Attribute) and node.func.attr in SWITCH_WORDS)
        or (isinstance(node.func, ast.Name) and node.func.id in SWITCH_WORDS))


def reads_by_name(node: ast.AST) -> bool:
    """``getattr(x, "layer")`` (with or without a default): the setting read by its name, which no attribute shows."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr"
            and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and node.args[1].value == "layer")


def names_the_switch(node: ast.AST) -> bool:
    # S70 (D234, Audit V F-3-9): and a call of compose's `setting(...)` or `words(...)` - `compose.setting(f) == "on"`
    # is a branch on the layer by another road, which the identifier alone did not see.
    # S70 fix pass (the independent reviewer): was the attribute callee alone (`_compose.setting(f)`); a bare-name
    # callee after `from galaxy.layer.compose import setting` and `getattr(ctx, "layer")` passed unseen.
    return any((isinstance(n, ast.Name) and n.id == "layer") or (isinstance(n, ast.Attribute) and n.attr == "layer")
               or says_the_word(n) or reads_by_name(n)
               for n in ast.walk(node))


# S70 (D234, Audit V F-3-9): the places outside compose that touch the setting at all - **a closed list**, read from
# the syntax tree. Every read of an attribute `.layer` is the setting handed on (a `layer=` keyword or a call's
# argument: the runner to the stages' context, the context to its view of the fields, the service to the runner);
# every call of compose's `setting` / `words` is the API's echo (a header's value, a cache key's element, an about
# line's words). An alias (`on = ctx.layer`), a read anywhere else or a call in another module fails here.
# S70 fix pass (the independent reviewer): was a set of (file, parent's node type) - any call in core/stage.py could
# take `.layer` as an argument. Now each hand-on is named and counted: the keyword's name, or the callee a call
# hands it to. The one call is core/stage.py's `FieldView(fields, stage, self.layer)` in `Context.__init__` (line
# 181 at S70), the context giving its fields view the run's setting; any other callee there (a `float(ctx.layer)`,
# a second FieldView) fails. A `getattr(..., "layer")` outside compose fails wherever it stands.
PASSED_ON = {("api/service.py", "layer="): 1, ("core/stage.py", "FieldView()"): 1, ("core/stage.py", "layer="): 1,
             ("run.py", "layer="): 1}
ECHOED = {"api/service.py": {"Dict": 8, "Tuple": 5, "Assign": 1}, "api/v6_tiles.py": {"Dict": 2, "Tuple": 1, "BinOp": 1}}


def touches(tree: ast.AST, name: str) -> tuple[dict[tuple[str, str], int], dict[str, int], list[str]]:
    """One module's touches of the setting: its hand-ons ``{(module, "kw=" or "callee()"): count}``, its echoes
    ``{parent's node type: count}``, and the reads that are neither (an alias, a test, a ``getattr`` by name)."""
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    passed: dict[tuple[str, str], int] = {}
    echoed: dict[str, int] = {}
    refused: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "layer" and isinstance(node.ctx, ast.Load):
            up = parent[node]
            if isinstance(up, ast.keyword) and up.arg is not None:
                form = f"{up.arg}="
            elif isinstance(up, ast.Call) and node in up.args:
                form = f"{ast.unparse(up.func)}()"
            else:
                refused.append(f"{name}:{node.lineno}: `{ast.unparse(up)}` reads the setting outside compose")
                continue
            passed[name, form] = passed.get((name, form), 0) + 1
        if reads_by_name(node):
            refused.append(f"{name}:{node.lineno}: `{ast.unparse(node)}` reads the setting by name outside compose")
        if says_the_word(node):
            kind = type(parent[node]).__name__
            echoed[kind] = echoed.get(kind, 0) + 1
    return passed, echoed, refused


def test_nothing_but_compose_branches_on_the_layer():
    """The runner, the stages' context, the service and the specs carry the setting - they pass it, store it and
    echo it. None of them decides anything by it: no ``if``, conditional expression, ``while``, ``assert``,
    comparison, boolean operation, ``not`` or comprehension filter outside ``galaxy/layer/compose.py`` reads a name
    or an attribute called ``layer``."""
    offenders: list[str] = []
    for path in model_sources():
        if path == PACKAGE / "layer" / "compose.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            tests: list[ast.AST] = []
            if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.Assert)):
                tests.append(node.test)
            elif isinstance(node, (ast.Compare, ast.BoolOp)):
                tests.append(node)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                tests.append(node)
            elif isinstance(node, ast.comprehension):
                tests.extend(node.ifs)
            elif isinstance(node, ast.Match):
                tests.append(node.subject)
            if any(names_the_switch(t) for t in tests):
                offenders.append(f"{path.relative_to(PACKAGE).as_posix()}:{node.lineno if hasattr(node, 'lineno') else '?'}")
    assert offenders == [], offenders
    # compose itself does: the instrument sees a branch where there is one.
    tree = ast.parse((PACKAGE / "layer" / "compose.py").read_text(encoding="utf-8"))
    assert any(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(tree))


def test_outside_compose_the_setting_is_only_passed_on_and_echoed():
    """S70 (D234, Audit V F-3-9): the branch guard above sees a test that names the switch; this one sees every other
    touch. A read of ``.layer`` outside compose is the setting handed on and nothing else (its parent is a keyword or
    a call), and compose's ``setting`` / ``words`` are called by the API alone, as an echo. Both closed lists."""
    passed: dict[tuple[str, str], int] = {}
    echoed: dict[str, dict[str, int]] = {}
    refused: list[str] = []
    for path in model_sources():
        name = path.relative_to(PACKAGE).as_posix()
        if name == "layer/compose.py":
            continue
        handed, echoes, wrong = touches(ast.parse(path.read_text(encoding="utf-8")), name)
        passed.update(handed)
        refused += wrong
        if echoes:
            echoed[name] = echoes
    assert refused == [], refused
    assert passed == PASSED_ON, sorted(set(passed.items()) ^ set(PASSED_ON.items()))
    assert echoed == ECHOED, echoed
    # The instrument sees an alias, a read by name, a bare-name echo, another callee and a branch on the words
    # (synthetic sources, parsed the same way).
    assert touches(ast.parse("def f(ctx):\n    on = ctx.layer\n    return on\n"), "x.py")[2] == ["x.py:2: `on = ctx.layer` reads the setting outside compose"]
    assert len(touches(ast.parse("g(layer=getattr(ctx, 'layer', True))\n"), "x.py")[2]) == 1
    assert touches(ast.parse("from galaxy.layer.compose import setting\nkey = (setting(f), 1)\n"), "x.py")[1] == {"Tuple": 1}
    assert touches(ast.parse("x = FieldView(f, s, self.layer)\ny = float(ctx.layer)\n"), "core/stage.py")[0] == \
        {("core/stage.py", "FieldView()"): 1, ("core/stage.py", "float()"): 1}
    branch = ast.parse("if _compose.setting(fields) == 'on':\n    pass\n").body[0]
    assert names_the_switch(branch.test) and not names_the_switch(ast.parse("x == 'on'").body[0].value)
    for test in ("setting(fields) == 'on'", "not words(fields)", "getattr(ctx, 'layer')"):
        assert names_the_switch(ast.parse(test).body[0].value), test
    assert not names_the_switch(ast.parse("getattr(ctx, 'grid') is None").body[0].value)


def test_fields_carry_the_setting_and_compose_refuses_a_mapping_that_does_not(small, prod):
    """How the switch travels: run -> each stage's Context -> the run's fields -> whatever materialises from them.
    A catalogue cannot be materialised with the layer's placements from a run without them, or the reverse, because
    there is no argument to pass: the fields say which run they are."""
    on, off = small[DEFAULT_MODEL, True], small[DEFAULT_MODEL, False]
    assert isinstance(on.fields, Fields) and (on.layer, on.fields.layer, off.layer, off.fields.layer) == (True, True, False, False)
    assert compose.setting(on.fields) == "on" and compose.setting(off.fields) == "off"
    m = prod[0].get(DEFAULT_MODEL)
    c = constants(m)
    R = on.grid.R
    assert compose.stellar_pattern(on.fields, R) is not None and compose.stellar_pattern(off.fields, R) is None
    assert compose.gas_pattern(on.fields, R, c) is not None and compose.gas_pattern(off.fields, R, c) is None
    assert compose.placement_weight(on.fields, "sfr_modulation") is not None
    assert compose.placement_weight(off.fields, "sfr_modulation") is None
    assert np.all(compose.published(off.fields, "sfr_modulation") == 1.0)
    assert compose.published(off.fields, "no_such_field") is None
    # A census drawn from each run's fields is that run's census, with no word from the caller.
    seed = int(on.inputs["systems_seed"])
    for out in (on, off):
        # S61 (D220 item 5): the texture on the run's texture_seed (unread with the layer off).
        census = cl.materialise_clouds(out.fields, out.grid.R, seed, c, texture_seed=int(out.inputs["texture_seed"]))
        for column in cl.WIRE_COLUMNS:
            assert same(census[column], out.fields[column]), (out.layer, column)
    # A plain dict of the same fields says nothing, and is refused rather than assumed.
    bare = dict(off.fields)
    for call in (lambda: compose.stellar_pattern(bare, R), lambda: compose.gas_pattern(bare, R, c),
                 lambda: compose.placement_weight(bare, "sfr_modulation"), lambda: compose.published(bare, "sfr_modulation"),
                 lambda: cl.materialise_clouds(bare, off.grid.R, seed, c),
                 lambda: sy.materialise(bare, off.grid.R, off.grid.t, seed, 2000, migration=3.6)):
        with pytest.raises(LayerError, match="does not say whether the randomness layer is on"):
            call()
    assert same(cl.materialise_clouds(Fields(bare, layer=False), off.grid.R, seed, c)["cloud_azimuth"], off.fields["cloud_azimuth"])


def test_a_run_is_not_resumed_under_the_other_setting(small, prod):
    m = prod[0].get(DEFAULT_MODEL)
    part = run(m, grid=SMALL, only=("pattern_density_contrast",), layer=False)
    with pytest.raises(RunError, match="layer off"):
        run(m, grid=SMALL, resume=part, layer=True)
    whole = run(m, grid=SMALL, resume=part, layer=False)
    assert whole.layer is False and whole.ran and "pattern" not in whole.ran
    assert [n for n in whole.fields if not same(whole.fields[n], small[DEFAULT_MODEL, False].fields[n])] == []


# --- the templates' checks, read layer-off -------------------------------------------------------------------------


def test_the_template_checks_layer_off_are_the_numbers_d213_recorded():
    """The five checks of ``ngc_4414`` on the production grid, read layer-off as the rows are (I3). The four field
    checks are radial and are the bits they were; the colour reads the face-on render, whose frame sums each ring
    round the ring, and moved in its thirteenth decimal (0.6355279197563419 layer-on). No verdict changed."""
    results = {r.name: r for r in checks.evaluate(["ngc_4414"])["ngc_4414"]}
    assert {n: r.status for n, r in results.items()} == dict.fromkeys(results, "fail") and len(results) == 5
    assert results["curve_shape"].value == 0.6532426864889841
    assert results["star_formation_rate"].value == 0.6528663372411139
    assert results["hydrogen_mass"].value == 4803633219.748805
    assert results["absolute_magnitude_k"].value == -23.270507283088264
    assert results["colour_b_v_face_on"].value == pytest.approx(0.6355279197563419, abs=1e-11)
