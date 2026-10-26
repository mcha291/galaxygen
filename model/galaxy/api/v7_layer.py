"""The randomness layer's galaxy-wide tables (S66, BUILD_III Phase V7; RULING_S66 R4-R6), published by ``/api/layer``
once per galaxy since S73 (#199; on ``/api/render``'s header from S66 to S72, where every windowed render repeated
them): what the viewer needs to evaluate the gas fluctuation field, the clustering field and the gas spurs in its
march - each map read once per ray as a thin screen at the ray's crossing of the midplane (D226 R3/R5 as amended) -
every number the model's, read off the run's published fields and the model's constants (rule D5 as amended, D220's
precedent: a function the model publishes, evaluated with every parameter the model's). No stage and no constant here.
The render keeps the arrays (the placement without the spurs, the middle part's kept windows) and names the route in
its header's ``layer_tables`` (:data:`LAYER_TABLES`).

- **gas_fluctuation** (:func:`gas_fluctuation_entry`): the seed, the field's form, the ring table (break index, sigma,
  strain, twist, normaliser), the ladder's weights for every break index (``GasFluctuationField.amplitudes``) and the
  level-0 cells' normalisers: the map ``normaliser_cell exp(sigma_r g - sigma_r^2 / 2)`` the viewer multiplies the
  dust's placement by, read once per ray at the midplane, the value multiplying each sub-step's placement (R3).
- **census_clustering** (:func:`clustering_entry`): the field's form and seed, the octaves' survival ages, and the
  k-octave maps' means per level-0 cell for k = 1, 2, 3 on the field's table lattice (R5c), so that the field mode's
  young and middle starlight are modulated by a map over its own cell mean whatever the clouds toggle.
- **spurs** (:func:`spurs_entry`): the gas spurs' table and their ring mean per grid ring; the render sends beside the
  placed gas the placement without them (:func:`unspurred_placement`, ``dust_placement_unspurred``):
  g' = (1 - <S>(R)) g + S, S read once per ray at the midplane (R4).

With the layer off every value is None, the keys kept (I5): the viewer's maps are then exactly 1.

**The stages** (review M1; S73): ``/api/layer`` asks for the gas fluctuation stage's fields on every request, layer
off included (:func:`reads`): with the layer on the entry carries its cell normalisers; with it off the stage returns
its neutral and the route does not branch on the layer (I5). From S66 to S72 the render asked for them so that its
header could carry the entries; since S73 it does not, and runs S65's stages again. The middle part's four windows -
their anchors and their responses through the request's curves - are the render's, cached with the run
(:func:`window_anchors`, :func:`window_responses`).
"""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.layer import census_clustering as _l1
from galaxy.layer import compose as _compose
from galaxy.layer import gas_fluctuation as _gas
from galaxy.stages import bright as _bright
from galaxy.stages import pieces as _pieces
from galaxy.stages.gas_pattern import GAS_PATTERN_READS
from galaxy.stages.spurs import SPUR_FIELDS

GAS_READS = tuple(d.name for d in _gas.PUBLISHES)
CLUSTERING_READS = (_l1.CENSUS_CLUSTERING_SEED.name, _l1.CENSUS_CLUSTERING_CELL_MEAN.name)
# S73 (#199): where the three tables live - /api/layer, once per galaxy - in the order its answer carries them.
LAYER_ROUTE = "/api/layer"
ENTRIES = ("gas_fluctuation", "census_clustering", "spurs")
LAYER_TABLES_ABOUT = (
    "the randomness layer's galaxy-wide tables the march reads - the gas fluctuation field, the clustering field's "
    "k-octave cell means and the gas spurs (S66, V7, D226) - are /api/layer's answer to the same inputs, template and "
    "layer setting as this render: fetched once per galaxy, never carried by a render (S73, #199)"
)
# What places the dust round a ring where the render places it by a pattern (the gas's own contrast, or the stars'
# where a model publishes no gas pattern): the spurs' entry is that placement's, so it exists only where the dust is.
DUST_PLACED_BY = ("gas_density_contrast", "pattern_density_contrast")


def layer_tables() -> dict[str, Any]:
    """The render header's ``layer_tables`` (S73, #199): the route that carries the three tables and their names."""
    return {"route": LAYER_ROUTE, "entries": list(ENTRIES), "about": LAYER_TABLES_ABOUT}


def published_entries(declared: Mapping[str, Any]) -> dict[str, bool]:
    """Which of the three entries the model publishes, from its declarations alone (no stage runs): the two fields
    where it publishes their stages' fields, the spurs where it publishes their table and places the dust by a
    pattern - the render's own conditions from S66 to S72 (its placement and :func:`spurs_entry`'s)."""
    return {
        "gas_fluctuation": all(n in declared for n in GAS_READS),
        "census_clustering": all(n in declared for n in CLUSTERING_READS),
        "spurs": "dust_extinction_v" in declared and any(n in declared for n in DUST_PLACED_BY)
                 and all(n in declared for n in SPUR_FIELDS),
    }


def reads(declared: Mapping[str, Any]) -> tuple[str, ...]:
    """What ``/api/layer`` asks the run for (rule D4): each published entry's fields - the gas fluctuation stage's, the
    clustering field's seed and cell means, the spurs' table and what the gas pattern is built from - and nothing
    else, layer off included (the route does not branch on the layer, I5)."""
    which = published_entries(declared)
    names = [*(GAS_READS if which["gas_fluctuation"] else ()), *(CLUSTERING_READS if which["census_clustering"] else ())]
    if which["spurs"]:
        names += [*SPUR_FIELDS, *(n for n in GAS_PATTERN_READS if n in declared)]
    return tuple(dict.fromkeys(names))
KEPT = (1, 2, 3)  # the octave counts the young starlight keeps (bright.octaves_kept): each a cell-mean table
UNSPURRED = "dust_placement_unspurred"
MIDDLE_KEPT = {3: "stars_middle_kept3", 2: "stars_middle_kept2", 1: "stars_middle_kept1"}
# How the march reads every map of the layer (D226 R3/R5 as amended): the rules below and the render about say it.
THIN_SCREEN = (
    "read once per ray as a thin screen at the ray's crossing of the midplane, the value multiplying each "
    "sub-step's placement; a column map says nothing of height, and drawn through the layer it would smear each "
    "feature by h tan i along the view"
)

GAS_RULE = (
    "the map m(x, y) = cell_normaliser[c] exp(sigma_r g - sigma_r^2 / 2), c the point's level-0 cell (ring r by the "
    "edges, sector by floor(atan2(y, x) mod 2 pi / (2 pi / 32))), g = sum_j weights[break_octave_r][j] noise2(seed, "
    "X 2^j / scale, Y 2^j / scale, octave j), (X, Y) = R (cos, sin)(atan2(y, x) - sense (twist_r + strain_r "
    "log(max(R, edges[0]) / edges[r]))), R = hypot(x, y) (gas_fluctuation.GasFluctuationField.evaluate; the twin's "
    "vectors in layer/vectors.json); its mean is 1 over every level-0 cell's quadrature lattice. In the march it is "
    + THIN_SCREEN + "; it multiplies the dust's placement (its column: the depth, the thermal light, the diagnostic - "
    "not the scattered light) (V7, D226 R3 as amended)"
)
CLUSTERING_RULE = (
    "the k-octave map m_k(x, y) = exp(sigma g_k - sigma^2 / 2), g_k = norm sum_(j < k) a_j noise2(seed, x 2^j / scale, "
    "y 2^j / scale, octave j), a_j = gain^j, times top on the field's last octave (census_clustering.ClusteringField."
    "maps; noise.fractal_coarsest); cell_mean[k][c] its mean over level-0 cell c's table lattice (table_points per "
    "finest lattice cell, R-weighted), cell_mean['3'] the published census_clustering_cell_mean. A star of age t keeps "
    "the octaves whose survival age (octave_ages_myr, coarsest first) it has not passed (bright.octaves_kept). In the "
    "field mode the young starlight (stars_young) is multiplied by m_3 / cell_mean['3'] and each of the middle "
    "part's kept arrays (ages.middle_kept) by m_k / cell_mean[k], each map " + THIN_SCREEN + " (V7, D226 R5 as amended)"
)
SPUR_RULE = (
    "g' = (1 - share(R)) g_unspurred + S (D221 item 7; V7, D226 R4 as amended): share and g_unspurred read at each "
    "sub-step's radius, the spurs' sum S read once per ray as a thin screen at the ray's crossing of the midplane and "
    "added to each sub-step's placement (a column map says nothing of height, and drawn through the layer it would "
    "smear each feature by h tan i along the view). g_unspurred the array placement."
    "dust_unspurred names, share the spurs' exact mean round the render ring, S = sum over the rows a radius reads of "
    "each spur's excess (stages/spurs.Spurs.excess: in the log-polar plane from the foot, across d = dx cos p - psi "
    "sin p, along t = dx sin p + psi cos p, dx = ln(R / R_f), psi = turn (phi - phi_f) within half a turn of the "
    "spur's middle; E = A exp(-lambda t) exp(-d^2 / 2 s^2) on 0 <= t <= T, round caps beyond, T = length / R_f, "
    "lambda = ln(fall) / T, s = (width / fwhm_per_sigma) / R); a spur is read at a radius whose gap in ln R past its "
    "foot or tip, times R, is within reach dispersions. With no rows, g_unspurred is dust_placement to the bit"
)


def _floats(values: Any) -> list[float]:
    return [float(v) for v in np.asarray(values, dtype=float).reshape(-1)]


def gas_fluctuation_entry(declared: bool, fields: Any, constants: Mapping[str, Any], R: np.ndarray) -> dict[str, Any] | None:
    """The header's ``gas_fluctuation``: None where the model does not publish the field (``declared``); with the
    layer off its seed and tables None, the keys kept, and nothing of the field read."""
    if not declared:
        return None
    field = _compose.gas_fluctuation(fields, constants, R)
    c = _gas.CONSTANTS
    entry: dict[str, Any] = {
        "seed": None, "scale": float(constants[c["scale"]]), "slope": float(constants[c["slope"]]),
        "change": float(constants[c["change"]]), "octaves": int(constants[c["octaves"]]), "lacunarity": _gas.LACUNARITY,
        "sense": None, "edges": None, "ring": None, "weights": None, "cell_normaliser": None, "rule": GAS_RULE,
    }
    if field is None:
        return entry
    entry.update(
        seed=int(field.seed), sense=float(field.sense), edges=_floats(field.edges),
        ring={"break_octave": [int(b) for b in field.break_octave], "sigma": _floats(field.sigma),
              "strain": _floats(field.strain), "twist": _floats(field.twist),
              "norm": _floats(fields["gas_fluctuation_norm"])},
        weights=[_floats(row) for row in field.amplitudes()], cell_normaliser=_floats(field.cell_normaliser),
    )
    return entry


def octave_ages_myr(constants: Mapping[str, Any]) -> list[float]:
    """Myr, coarsest octave first: the ages past which a star drops each of the clustering field's octaves - the
    bright catalogue's own (``bright.octave_survival`` of the field's scales), from the constants alone."""
    c = _l1.CONSTANTS
    scales = float(constants[c["scale"]]) * 1000.0 / _l1.LACUNARITY ** np.arange(int(constants[c["octaves"]]))
    return _floats(_bright.octave_survival(scales, float(constants[_bright.AGE_AMPLITUDE]), float(constants[_bright.AGE_INDEX])))


def clustering_entry(declared: bool, fields: Any, constants: Mapping[str, Any], R: np.ndarray) -> dict[str, Any] | None:
    """The header's ``census_clustering``: None where the model does not publish the field (``declared``); with the
    layer off its seed and cell means None and nothing of the field read. The form's numbers are ``/api/clouds``'
    (``census_clustering.header``'s); the k-octave means are computed here (cached by the field and the grid)."""
    if not declared:
        return None
    field = _compose.census_clustering(fields, constants)
    c = _l1.CONSTANTS
    shape = _l1.ClusteringField(0, float(constants[c["scale"]]), int(constants[c["octaves"]]), float(constants[c["slope"]]),
                                float(constants[c["sigma"]]), int(constants[c["points"]]))
    gain, top, norm = shape.weights()
    entry: dict[str, Any] = {
        "seed": None if field is None else int(field.seed), "scale": shape.scale, "octaves": shape.octaves,
        "lacunarity": _l1.LACUNARITY, "slope": shape.slope, "sigma": shape.sigma, "gain": gain, "top": top, "norm": norm,
        "table_points": int(constants[_l1.TABLE_POINTS]),
    }
    entry["octave_ages_myr"] = octave_ages_myr(constants)
    entry["cell_mean"] = None
    if field is not None:
        means = field.kept_cell_means(R, KEPT, int(constants[_l1.TABLE_POINTS]))
        entry["cell_mean"] = {str(k): _floats(means[k]) for k in sorted(KEPT, reverse=True)}
    entry["rule"] = CLUSTERING_RULE
    return entry


def spurs_entry(fields: Any, constants: Mapping[str, Any], R: np.ndarray) -> dict[str, Any] | None:
    """``/api/layer``'s ``spurs`` (the render header's from S66 to S72): the gas spurs' table, their ring mean on the
    grid's rings ``R``, the constants and the rule - or None where the model publishes no spurs' table (the caller
    asks only where the dust is placed by a pattern, :func:`published_entries`). With the layer off the entry's values
    are None, the keys kept."""
    if any(n not in fields for n in SPUR_FIELDS):
        return None
    entry: dict[str, Any] = {
        "rows": None, "turn": None, "share": None, "reach": _pieces.REACH, "fwhm_per_sigma": _pieces.FWHM_PER_SIGMA,
        "constants": {k: float(constants[k]) for k in ("SPUR_PITCH", "SPUR_LENGTH", "SPUR_WIDTH", "SPUR_FALL")},
        "rule": SPUR_RULE,
    }
    from galaxy.stages.pattern import rotation_sense

    shape = _compose.gas_pattern(fields, R, constants)  # None with the layer off: no spur is composed then
    if shape is None:
        return entry
    columns = {"chain": "gas_spur_chain", "radius": "gas_spur_radius", "azimuth": "gas_spur_azimuth",
               "contrast": "gas_spur_contrast", "pitch": "gas_spur_pitch", "length": "gas_spur_length",
               "width": "gas_spur_width", "fall": "gas_spur_fall"}
    entry["rows"] = {k: _floats(fields[n]) for k, n in columns.items()}
    entry["units"] = {"radius": "kpc", "azimuth": "rad", "pitch": "deg", "length": "kpc", "width": "kpc (FWHM)",
                      "contrast": "dimensionless (A: the ridge's crest contrast at the foot)", "fall": "dimensionless"}
    entry["turn"] = -float(rotation_sense(float(fields["pitch_angle"])))  # GasPattern.from_fields' sense for psi
    spurs = shape.spurs
    entry["share"] = _floats(np.zeros(np.size(R)) if spurs is None else spurs.ring_mean(np.asarray(R, dtype=float)))
    return entry


def unspurred_placement(fields: Any, constants: Mapping[str, Any], R: np.ndarray, phi_edges: np.ndarray) -> np.ndarray | None:
    """The render's ``dust_placement_unspurred`` on the grid: the gas pattern's exact cell means without the spurs,
    floored at zero as ``dust_placement`` is - or None where no spur is composed (no spurs' table, the layer off, a flat
    pattern), where the route sends the placement itself. On a pattern without spurs it is ``placed_gas`` to the bit
    (tested). The same gas pattern :func:`spurs_entry` reads its table's share off (``compose.gas_pattern``)."""
    if any(n not in fields for n in SPUR_FIELDS):
        return None
    shape = _compose.gas_pattern(fields, R, constants)
    if shape is None or shape.flat:
        return None
    return np.maximum(shape.unspurred_cell_means(R, phi_edges), 0.0)


# The middle part's window anchors per run (S66 fix pass, review M1): bright.window_anchors is 0.2-0.7 s of history on
# the isochrones, and was recomputed on every render request. It reads the run's fields and constants only - the curves
# are applied after - so it is cached as the k-octave means are (census_clustering.kept_cell_means): by what it reads.
_ANCHORS: OrderedDict[tuple, np.ndarray] = OrderedDict()
_ANCHORS_HELD = 8  # runs, as kept_cell_means' lru_cache holds


def _digest(value: Any) -> tuple:
    a = np.ascontiguousarray(np.asarray(value))
    return a.dtype.str, a.shape, hashlib.blake2b(a.tobytes(), digest_size=16).hexdigest()


def window_anchors(fields: Any, t_max: float, n_t: int, constants: Mapping[str, Any],
                   windows: Sequence[tuple[float, float]]) -> np.ndarray:
    """``bright.window_anchors``, cached by everything it reads: the run's formed and metallicity histories (by their
    bytes), the age grid, RETURN_FRACTION and the windows. A copy each call; the arithmetic is the stage's, bit for bit."""
    key = (_digest(fields["stars_formed_history"]), _digest(fields["feh_history"]), float(t_max), int(n_t),
           float(constants["RETURN_FRACTION"]), tuple((float(lo), float(hi)) for lo, hi in windows))
    held = _ANCHORS.get(key)
    if held is None:
        held = np.array(_bright.window_anchors(fields, t_max, n_t, constants, windows))
        held.setflags(write=False)
        _ANCHORS[key] = held
        while len(_ANCHORS) > _ANCHORS_HELD:
            _ANCHORS.popitem(last=False)
    else:
        _ANCHORS.move_to_end(key)
    return held.copy()


_RESPONSES: OrderedDict[tuple, np.ndarray] = OrderedDict()


def window_responses(fields: Any, t_max: float, n_t: int, constants: Mapping[str, Any],
                     windows: Sequence[tuple[float, float]], curves: Sequence[Any]) -> np.ndarray:
    """(len(windows), n_R, n_filters): the window anchors (:func:`window_anchors`) through ``curves`` at the ring's
    colour temperature (``spectra.stellar_response``), cached with the run and the request's filter set (the lead's
    ruling on review M1): keyed as the anchors are, plus disc_light_temperature by its bytes and the parsed curves by a
    digest of their definition (``repr`` of the frozen ``spectra.Curve`` tuple). The three age parts' own responses
    (``Service._ages``) are recomputed every request, as at S63-S65; only these four, S66's addition, are held.
    A copy each call; the arithmetic is the stage's, bit for bit."""
    from galaxy.stages import spectra as _spectra

    T = fields["disc_light_temperature"]
    key = (_digest(fields["stars_formed_history"]), _digest(fields["feh_history"]), _digest(T), float(t_max), int(n_t),
           float(constants["RETURN_FRACTION"]), tuple((float(lo), float(hi)) for lo, hi in windows),
           hashlib.blake2b(repr(tuple(curves)).encode("utf-8"), digest_size=16).hexdigest())
    held = _RESPONSES.get(key)
    if held is None:
        anchors = window_anchors(fields, t_max, n_t, constants, windows)
        held = np.stack([_spectra.stellar_response(a, T, curves) for a in anchors])
        held.setflags(write=False)
        _RESPONSES[key] = held
        while len(_RESPONSES) > _ANCHORS_HELD:
            _RESPONSES.popitem(last=False)
    else:
        _RESPONSES.move_to_end(key)
    return held.copy()


def middle_kept(declared: bool, fields: Any, constants: Mapping[str, Any], t_max: float, n_t: int, curves: Any,
                middle: np.ndarray, cut: float, young_age: float,
                weight: str) -> tuple[dict[str, Any] | None, list[tuple[str, np.ndarray]]]:
    """The ages' ``middle_kept`` entry and its three per-ring arrays (S66, D226 R5b): the middle part's light split by
    the clustering field's octaves its stars keep - ages [cut, t_3), [t_3, t_2), [t_2, t_1) keep 3, 2, 1 octaves
    (t_k the octave survival ages, :func:`octave_ages_myr`), the rest [t_1, young_age) none. Each window's anchors are
    ``bright.window_anchors`` (``part_anchors``' arithmetic), put through the curves at the ring's colour temperature
    (both cached with the run and the curves, :func:`window_responses`),
    and the four are scaled per ring and filter by one closure factor ``middle / their sum``, as the three parts are
    scaled to the stars: so the three arrays and the rest (``middle`` less the three) sum to ``middle`` to rounding.
    The ages are the history's and the constants', not the layer's: the same arrays with the layer off, where the maps
    are 1 (I5). None and no arrays where the model publishes no clustering field (``declared``)."""
    if not declared:
        return None, []
    ages = np.asarray(octave_ages_myr(constants)) / 1000.0  # Gyr, coarsest octave first
    if ages.size != len(KEPT):
        raise ValueError(f"the middle part splits by {len(KEPT)} octaves; the clustering field has {ages.size}")
    edges = np.clip(np.array([cut, ages[2], ages[1], ages[0], young_age]), cut, young_age)
    windows = [(float(edges[i]), float(edges[i + 1])) for i in range(4)]  # keep 3, 2, 1, 0 octaves
    raw = window_responses(fields, t_max, n_t, constants, windows, curves)  # (4, R, filter), cached (review M1)
    total = raw.sum(axis=0)
    lit = (total > 0.0) & (middle > 0.0)
    factor = np.where(lit, middle / np.where(lit, total, 1.0), 1.0)
    parts = raw * factor[None]
    departure = [float(np.max(np.abs(factor[:, k] - 1.0), initial=0.0)) for k in range(factor.shape[1])]
    entry = {
        "arrays": {str(k): MIDDLE_KEPT[k] for k in (3, 2, 1)},
        "ages_gyr": {"3": list(windows[0]), "2": list(windows[1]), "1": list(windows[2]), "rest": list(windows[3])},
        "octave_ages_myr": octave_ages_myr(constants),
        "weight": weight,
        "rest": "stars_middle less the three kept arrays: the middle part's stars older than every octave's survival "
                "age, placed as stars_middle is and modulated by nothing (bright.octaves_kept: 0 octaves)",
        "rule": "each kept part k is placed as stars_middle is (its weight) and multiplied by the clustering field's "
                "k-octave map over its level-0 cell's k-octave mean (" + LAYER_ROUTE + "'s census_clustering.cell_mean[k], "
                "census_clustering.rule), the map " + THIN_SCREEN + " (V7, D226 R5 as amended)",
        "closure": {
            "factor": departure,
            "about": "per filter, the largest |factor - 1| over the rings of the factor the four windows' responses are "
                     "scaled by: stars_middle over their sum, at the ring's colour temperature (the join is not linear, "
                     "as for the three parts). So the kept arrays and the rest sum to stars_middle per ring and filter "
                     "to rounding",
        },
        "about": "the middle part's light split by the age windows of the clustering octaves its stars keep (L1's rule "
                 "for the bright catalogue's young stars, D220 part II item 5): the windows' bounds are the octaves' "
                 "survival ages, derived from the constants as the bright catalogue derives them. The same arrays with "
                 "the layer off, where every map is 1 (census_clustering's seed and cell means null): the parts are "
                 "then stars_middle split and placed as it is",
    }
    return entry, [(MIDDLE_KEPT[k], parts[i]) for i, k in enumerate((3, 2, 1))]
