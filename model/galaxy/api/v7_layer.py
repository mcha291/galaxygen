"""The randomness layer's fields on /api/render's header (S66, BUILD_III Phase V7; RULING_S66 R4-R6): what the viewer
needs to evaluate the gas fluctuation field, the clustering field and the gas spurs per sub-step in its march - every
number the model's, read off the run's published fields and the model's constants (rule D5 as amended, D220's
precedent: a function the model publishes, evaluated with every parameter the model's). No stage and no constant here.

- **gas_fluctuation** (:func:`gas_fluctuation_entry`): the seed, the field's form, the ring table (break index, sigma,
  strain, twist, normaliser), the ladder's weights for every break index (``GasFluctuationField.amplitudes``) and the
  level-0 cells' normalisers: the map ``normaliser_cell exp(sigma_r g - sigma_r^2 / 2)`` the viewer multiplies the
  dust's placement by per sub-step (R3).
- **census_clustering** (:func:`clustering_entry`): the field's form and seed, the octaves' survival ages, and the
  k-octave maps' means per level-0 cell for k = 1, 2, 3 on the field's table lattice (R5c), so that the field mode's
  young and middle starlight are modulated by a map over its own cell mean whatever the clouds toggle.
- **spurs** (:func:`spurs_entry`): the gas spurs' table and their ring mean per render ring, and beside the placed gas
  the placement without them (``dust_placement_unspurred``): g' = (1 - <S>(R)) g + S per sub-step (R4).

With the layer off every value is None, the keys kept (I5): the viewer's maps are then exactly 1.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.layer import census_clustering as _l1
from galaxy.layer import compose as _compose
from galaxy.layer import gas_fluctuation as _gas
from galaxy.stages import bright as _bright
from galaxy.stages import pieces as _pieces
from galaxy.stages.spurs import SPUR_FIELDS

GAS_READS = tuple(d.name for d in _gas.PUBLISHES)
CLUSTERING_READS = (_l1.CENSUS_CLUSTERING_SEED.name, _l1.CENSUS_CLUSTERING_CELL_MEAN.name)
KEPT = (1, 2, 3)  # the octave counts the young starlight keeps (bright.octaves_kept): each a cell-mean table
UNSPURRED = "dust_placement_unspurred"
MIDDLE_KEPT = {3: "stars_middle_kept3", 2: "stars_middle_kept2", 1: "stars_middle_kept1"}

GAS_RULE = (
    "the map m(x, y) = cell_normaliser[c] exp(sigma_r g - sigma_r^2 / 2), c the point's level-0 cell (ring r by the "
    "edges, sector by floor(atan2(y, x) mod 2 pi / (2 pi / 32))), g = sum_j weights[break_octave_r][j] noise2(seed, "
    "X 2^j / scale, Y 2^j / scale, octave j), (X, Y) = R (cos, sin)(atan2(y, x) - sense (twist_r + strain_r "
    "log(max(R, edges[0]) / edges[r]))), R = hypot(x, y) (gas_fluctuation.GasFluctuationField.evaluate; the twin's "
    "vectors in layer/vectors.json); its mean is 1 over every level-0 cell's quadrature lattice. Evaluated per "
    "sub-step in the march at the sub-step's face-on read point, multiplying the dust's placement (its column: the "
    "depth, the thermal light, the diagnostic - not the scattered light) (V7, D226)"
)
CLUSTERING_RULE = (
    "the k-octave map m_k(x, y) = exp(sigma g_k - sigma^2 / 2), g_k = norm sum_(j < k) a_j noise2(seed, x 2^j / scale, "
    "y 2^j / scale, octave j), a_j = gain^j, times top on the field's last octave (census_clustering.ClusteringField."
    "maps; noise.fractal_coarsest); cell_mean[k][c] its mean over level-0 cell c's table lattice (table_points per "
    "finest lattice cell, R-weighted), cell_mean['3'] the published census_clustering_cell_mean. A star of age t keeps "
    "the octaves whose survival age (octave_ages_myr, coarsest first) it has not passed (bright.octaves_kept). In the "
    "field mode the young starlight (stars_young) is multiplied per sub-step by m_3 / cell_mean['3'] and each of the "
    "middle part's kept arrays (ages.middle_kept) by m_k / cell_mean[k] at the sub-step's read point (V7, D226)"
)
SPUR_RULE = (
    "g' = (1 - share(R)) g_unspurred + S per sub-step (D221 item 7; V7, D226): g_unspurred the array placement."
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


def spurs_entry(fields: Any, constants: Mapping[str, Any], R: np.ndarray,
                phi_edges: np.ndarray) -> tuple[dict[str, Any] | None, np.ndarray | None]:
    """(the header's ``spurs``, the placement without the spurs on the grid) - or (None, None) where the model
    publishes no spurs' table or the render places no dust by the gas. With the layer off the entry's values are None
    and no array is made (the route ships the neutral placement itself). The unspurred placement is the gas pattern's exact cell means without the spurs, floored
    at zero as ``dust_placement`` is; on a pattern without spurs it is ``placed_gas`` to the bit (tested)."""
    if any(n not in fields for n in SPUR_FIELDS):
        return None, None
    entry: dict[str, Any] = {
        "rows": None, "turn": None, "share": None, "reach": _pieces.REACH, "fwhm_per_sigma": _pieces.FWHM_PER_SIGMA,
        "constants": {k: float(constants[k]) for k in ("SPUR_PITCH", "SPUR_LENGTH", "SPUR_WIDTH", "SPUR_FALL")},
        "rule": SPUR_RULE,
    }
    from galaxy.stages.pattern import rotation_sense

    shape = _compose.gas_pattern(fields, R, constants)  # None with the layer off: no spur is composed then
    if shape is None:
        return entry, None
    columns = {"chain": "gas_spur_chain", "radius": "gas_spur_radius", "azimuth": "gas_spur_azimuth",
               "contrast": "gas_spur_contrast", "pitch": "gas_spur_pitch", "length": "gas_spur_length",
               "width": "gas_spur_width", "fall": "gas_spur_fall"}
    entry["rows"] = {k: _floats(fields[n]) for k, n in columns.items()}
    entry["units"] = {"radius": "kpc", "azimuth": "rad", "pitch": "deg", "length": "kpc", "width": "kpc (FWHM)",
                      "contrast": "dimensionless (A: the ridge's crest contrast at the foot)", "fall": "dimensionless"}
    entry["turn"] = -float(rotation_sense(float(fields["pitch_angle"])))  # GasPattern.from_fields' sense for psi
    spurs = shape.spurs
    entry["share"] = _floats(np.zeros(np.size(R)) if spurs is None else spurs.ring_mean(np.asarray(R, dtype=float)))
    if shape.flat:
        return entry, None
    return entry, np.maximum(shape.unspurred_cell_means(R, phi_edges), 0.0)


def middle_kept(declared: bool, fields: Any, constants: Mapping[str, Any], t_max: float, n_t: int, curves: Any,
                middle: np.ndarray, cut: float, young_age: float,
                weight: str) -> tuple[dict[str, Any] | None, list[tuple[str, np.ndarray]]]:
    """The ages' ``middle_kept`` entry and its three per-ring arrays (S66, D226 R5b): the middle part's light split by
    the clustering field's octaves its stars keep - ages [cut, t_3), [t_3, t_2), [t_2, t_1) keep 3, 2, 1 octaves
    (t_k the octave survival ages, :func:`octave_ages_myr`), the rest [t_1, young_age) none. Each window's anchors are
    ``bright.window_anchors`` (``part_anchors``' arithmetic), put through the curves at the ring's colour temperature,
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
    from galaxy.stages import spectra as _spectra

    anchors = _bright.window_anchors(fields, t_max, n_t, constants, windows)
    T = fields["disc_light_temperature"]
    raw = np.stack([_spectra.stellar_response(a, T, curves) for a in anchors])  # (4, R, filter)
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
        "rule": "each kept part k is placed as stars_middle is (its weight) and multiplied per sub-step by the "
                "clustering field's k-octave map over its level-0 cell's k-octave mean (census_clustering.cell_mean[k], "
                "census_clustering.rule) (V7, D226)",
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
