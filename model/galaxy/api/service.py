"""The routes, as pure functions of ``(path, query)``.

No HTTP here: a route takes a parsed query and returns a :class:`Response` with
a status, a media type, bytes, and **the stages it ran**. That last field is the
instrument rule D4 is checked with. A timing cannot check D4 — a metadata
endpoint that quietly runs the pipeline is fast on the second call and fast on
every call a test makes against a warm process (rule B2). What the stages ran
cannot be hidden by a cache: an endpoint that touched a stage says so.

**Where the answers come from.**

- Metadata (``version``, ``stages``, ``fields``, ``inputs``) is answered from
  declarations — ``Stage``, ``FieldDecl``, ``Input`` — which exist without
  anything being computed. These routes run no stage, ever, and it is not a
  matter of care: there is no runner in their path to call.
- ``arrays`` runs the dependency closure above the fields asked for, and nothing
  else (``run(..., only=…)``).
- ``region`` runs what the catalogue stage *reads* and not the catalogue stage
  itself, then materialises the requested cells directly. A region query
  therefore never builds the galaxy-wide sample, which is the exact defect D4
  names.

**What is not published** (rule D5): constants, stage source, model internals of
any kind. The viewer gets declarations, numbers and ramps; it cannot reconstruct
the model from them, and replacing it means reimplementing against these
endpoints rather than against the physics.

**Controls are validated against the registry's own ranges**, so a viewer cannot
ask for a galaxy the input table says is out of bounds, and the range the API
enforces is the range it publishes.
"""

from __future__ import annotations

import json
import math
import threading
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import parse_qsl

import numpy as np

from galaxy.api import wire
from galaxy.api.version import CLIENT, SERVER, content_hash
from galaxy.core.cmaps import COLORMAPS
from galaxy.core.fielddoc import SCALES, FieldDecl, Palette, Ramp
from galaxy.core.grids import DEFAULT, Grid, GridSpec
from galaxy.core.registry import (
    INPUT_CEILING,
    Input,
    MergerEvent,
    Model,
    Registry,
    production,
)
from galaxy.core.stage import CHECKPOINTS, Stage
from galaxy.core.units import unit as _unit
from galaxy.run import Outputs, RunError
from galaxy.run import run as _run
from galaxy.specs import graph as _graph
from galaxy.stages import bright as _bright
from galaxy.stages import bubbles as _bubbles
from galaxy.stages import planets as _planets
from galaxy.stages import clouds as _clouds  # also the HII layer's height (S39)
from galaxy.stages import clusters as _clusters
from galaxy.stages import nebular as _nebular
from galaxy.stages import spectra as _spectra
from galaxy.stages import systems as _catalogue
from galaxy.stages.disc import PC_PER_KPC

JSON = "application/json"
CATALOGUE_SLOT = "systems"  # the slot a region query materialises from
PLANETS_SLOT = "planets"  # and the slot a system query materialises with
CLOUDS_SLOT = "clouds"  # the slot a clouds query materialises from (S32)
CLUSTERS_SLOT = "clusters"  # and the slot a clusters query answers for (S33)
NEBULAR_SLOT = "nebular"  # whose HII-region columns ride on the clusters response (S35)
BUBBLES_SLOT = "bubbles"  # whose bubble columns ride on it too, and whose remnant census /api/remnants serves (S36)
BRIGHT_SLOT = "bright_stars"  # the slot /api/bright answers for (S48, D200)
# The most child cells one level>0 region query may name (S32): 4096 is 64 level-0 cells at level 3,
# about a quarter of a ring's sectors two kiloparsecs deep; a wider window at that depth is refused.
MAX_CHILD_CELLS = 4096
# What /api/render reads (S38): the stellar component's two fields are required, the rest are
# read where the model publishes them and named as absent where it does not (rule B9).
RENDER_STARS = (*(f"disc_sed_{b.lower()}" for b in _spectra.SED_BANDS), "disc_light_temperature")
RENDER_BULGE = (*(f"bulge_sed_{b.lower()}" for b in _spectra.SED_BANDS), "bulge_light_temperature")
# Every line but Halpha the render route draws (S42), by the model's line name: its HII-region field.
RENDER_LINES_HII = tuple(f"{n}_surface_brightness_hii" for n in ("hbeta", "oiii_5007", "nii_6583", "sii_6716", "sii_6731"))
RENDER_OPTIONAL = (
    "pattern_density_contrast", *RENDER_BULGE, "thin_disc_scale_height",
    # The line's two layers (S39, V2): the HII regions' share and the diffuse gas's, with its height.
    "halpha_surface_brightness_hii", "halpha_surface_brightness_dig", "dig_scale_height",
    # The other lines (S42): Hbeta in both layers, the forbidden lines the grid gives the HII regions.
    *RENDER_LINES_HII, "hbeta_surface_brightness_dig",
    # The dust's three components (S39, V2): extinction, scattering, thermal emission.
    "dust_extinction_v", "dust_scattering_optical_depth", "dust_scattering_asymmetry",
    "dust_temperature", "dust_infrared_surface_brightness",
)
# The dust stage's modified blackbody (S39): its shape is read with the stage's own constants, server-side.
RENDER_DUST_CONSTANTS = ("DUST_OPACITY_REFERENCE", "DUST_OPACITY_WAVELENGTH", "DUST_EMISSIVITY_INDEX")
# Sub-samples per side a region cell's mean is taken over (level=k): the grid's values bilinearly
# interpolated at 8 x 8 midpoints, area-weighted.
RENDER_CELL_SAMPLES = 8
# The temperatures /api/blackbody tabulates (S42): 193 log-spaced from 1000 K to 100 000 K, 1/96 dex apart - the
# render's own white-point range. Read linearly in log share against log T (the Wien side is an exponential in 1/T,
# which a line in the share itself misses by 16% at 1000 K), every set's table is within the bound
# tests/test_render.py measures of the integral at any temperature between its rows. The model's one copy, the grid
# the per-object response tabulates its tails on (S48's wiring: until then this module held a mirror of it).
BLACKBODY_GRID = _spectra.RESPONSE_TEMPERATURES
# A guard, not a physical limit: this is a headless service and the LOD ladder
# that decides what a viewer should ask for arrives at S7 (GALAXY_PLAN.md §4).
MAX_STARS = 5_000_000
# The most stars a brightest=N query returns: a magnitude-limited view is a few thousand points,
# and a viewer that wants more than this wants the window itself.
MAX_BRIGHTEST = 200_000
# The most stars one /api/bright request materialises while lowering its threshold to find n inside a view
# (S48): a view that sees a sliver of a wide window stops here, says so, and returns what it found.
MAX_BRIGHT_POOL = 500_000


class ApiError(Exception):
    """A request that cannot be answered. ``status`` is what the caller is told."""

    status = 400


class BadRequest(ApiError):
    status = 400


class NotFound(ApiError):
    status = 404


@dataclass(frozen=True, slots=True)
class Route:
    path: str
    about: str
    params: tuple[str, ...] = ()  # reserved query parameters; everything else is an input
    handler: str = "index"  # the method that answers it, named rather than derived


ROUTES: tuple[Route, ...] = (
    Route("/", "The viewer: / is index.html, /<name> a file beside it.", (), "viewer"),
    Route("/api", "This route table.", (), "index"),
    Route("/api/version", "Content hash of the viewer's bytes and of the API's own (rule D3).", (), "version"),
    Route("/api/stages", "Stage declarations, their checkpoints and the execution order.", ("model",), "stages"),
    Route("/api/fields", "Field declarations and the cmap stops behind them (rule A9).", ("model",), "fields"),
    Route("/api/inputs", "The input registry: defaults, ranges, seeds, event list.", ("model",), "inputs"),
    Route(
        "/api/arrays",
        "Named fields as binary arrays, plus the galaxy-level scalars. t_samples=N keeps N evenly spaced "
        "time steps of fields over t; precision=f4 sends float fields as float32.",
        ("model", "fields", "t_samples", "precision"),
        "arrays",
    ),
    Route(
        "/api/region",
        "A materialised star catalogue for one (R, phi) window. brightest=N keeps the N most luminous "
        "stars of it, each row named by its own cell and index columns; view=<16 numbers> (a column-major "
        "view-projection matrix over x = R cos phi, y = height, z = -R sin phi) first keeps only the stars "
        "inside that frustum. level=k (0..3, S32) names the cell hierarchy's depth: each level-k cell "
        "holds its parent's stars that fall inside it plus its own, 4^k times the sample density, every "
        "row named by level, cell and index columns.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "stars", "brightest", "view", "level"),
        "region",
    ),
    Route(
        "/api/system",
        "One star's planets and belts, by the (level, cell, index) that names it (level 0 by default).",
        ("model", "cell", "index", "stars", "level"),
        "system",
    ),
    Route(
        "/api/clouds",
        "The molecular-cloud census for one (R, phi) window (S32): every cloud of the cells the window "
        "meets, each row named by cell and index; level=k keeps the clouds inside the level-k children "
        "the window meets.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "level"),
        "clouds",
    ),
    Route(
        "/api/clusters",
        "The young star-cluster census for one (R, phi) window (S33): one cluster in every cloud past its "
        "embedded phase, of the cells the window meets, each row named by cell and index as the cloud "
        "that holds it names it, with its HII region's columns (S35) and its bubble's (S36); level=k keeps the "
        "clusters inside the level-k children the window meets. filters= (as /api/render takes it, S48) adds response, "
        "each cluster's own band light through each curve in Lsun; white=<K> the white point, as /api/render's header.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "level", "filters", "white"),
        "clusters",
    ),
    Route(
        "/api/remnants",
        "The supernova-remnant census for one (R, phi) window (S36): every visible remnant of the cells the "
        "window meets, each row named by cell and index, with its blast wave's size, shell and phase; level=k "
        "keeps the remnants inside the level-k children the window meets.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "level"),
        "remnants",
    ),
    Route(
        "/api/bright",
        "Every disc star above a luminosity, complete (S48, D200): the bright catalogue's stars in the finest cells "
        "(level 3) the (R, phi) window meets, drawn from the luminosity function by an ordered Poisson process per "
        "cell, so a higher threshold keeps a prefix and a window's stars are a sweep's. n=N (1..200000) returns the N "
        "brightest, inside view=<16 numbers>'s frustum when one is given (as /api/region takes it); l_min=<Lsun> "
        "every star above it (refused past 200000 expected). Rows brightest first, each named by cell and rank; the "
        "header's threshold says what the body is complete above. Stars younger than the cluster census's window "
        "are the clusters'; the bulge is the field's. precision=f4 sends float32. filters= (as /api/render takes it) "
        "adds response, each star's band light through each curve in Lsun; white=<K> the white point, as /api/render's "
        "header.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "view", "n", "l_min", "precision", "filters", "white"),
        "bright",
    ),
    Route(
        "/api/blackbody",
        "Each of the viewer's filters' share of a blackbody's light (S42), on 193 temperatures, with the white "
        "point's: what a star or a cluster of a colour temperature puts through each filter per unit of its light, "
        "so the points are drawn through the same curves as the field. filters= as for /api/render; white=<K> "
        "optional. Runs no stage.",
        ("filters", "white"),
        "blackbody",
    ),
    Route(
        "/api/render",
        "The filter integral, run here (RENDER_PHYSICS section 0's ruling (a), S38): filters=<JSON list of the "
        "viewer's curves, each {name, shape: gaussian (centre, fwhm) | box (centre, width) | sampled (wavelength, "
        "transmission), optionally wavelengths: air | vacuum (air unless it says so; the lines are converted to "
        "vacuum before a vacuum curve is read, S44)}, angstroms> returns, per cell of the (R, phi) grid inside the "
        "window - or per level-k region cell with level=k - each emitting component's response in each filter, never composited: stars (the "
        "population's eight-band spectrum joined into a continuum, times the pattern's contrast), the Halpha line as "
        "two volumetric layers (halpha_hii placed by the contrast, halpha_dig per ring; S39), and the dust as "
        "dust_extinction (face-on transmission per filter from the grain model's curve), dust_scattered and "
        "dust_thermal (a modified blackbody through each curve). The header names each component's fields and "
        "vertical layer; the bulge's response rides in it; white=<K> adds a blackbody's response per unit light for "
        "the viewer's white balance; set=<name> is echoed; precision=f4 sends float32. l_min=<Lsun> (S48) adds "
        "stars_unresolved, the stars' light that no point carries - less the young stars the cluster census holds and "
        "the disc stars above l_min /api/bright holds - each age part placed as the bright catalogue places it, with "
        "the header's resolved stating the light split and the closure.",
        ("model", "filters", "set", "white", "r_min", "r_max", "phi_min", "phi_max", "level", "precision", "l_min"),
        "render",
    ),
)

# What the viewer may be served. A suffix that is not here is not a file this
# service hands out, whatever is sitting in the directory: an allowlist cannot
# be widened by accident, and a denylist can.
MEDIA_TYPES: Mapping[str, str] = MappingProxyType({
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",  # the frontend build self-hosts its fonts
    ".woff": "font/woff",
})

RESERVED: frozenset[str] = frozenset(p for r in ROUTES for p in r.params)


def routes() -> tuple[Route, ...]:
    """The route table. Published at ``/api`` and read by ``tools/timings.py``."""
    return ROUTES


@dataclass(frozen=True, slots=True)
class Response:
    status: int
    media: str
    body: bytes
    stages: tuple[str, ...] = ()  # what this request executed: rule D4's instrument

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def frame(self) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
        return wire.decode(self.body)


def _parse_filters(q: Query) -> list[Any]:
    """filters=: the viewer's curves, parsed by the model's spectrum module, or a 400 saying why not."""
    raw = q.one("filters")
    if raw is None:
        raise BadRequest(
            "filters= is the viewer's filter set as a JSON list of curves; the model holds no filter set "
            "(RENDER_PHYSICS section 2a)"
        )
    try:
        return _spectra.parse_curves(json.loads(raw))
    except json.JSONDecodeError as e:
        raise BadRequest(f"filters= must be a JSON list of curves: {e}") from None
    except _spectra.CurveError as e:
        raise BadRequest(f"filters=: {e}") from None


def _white_point(q: Query, curves: Sequence[Any]) -> dict[str, Any] | None:
    """white=<K>: a blackbody's response per unit light through the curves, the viewer's white balance (S38), as the
    header of every route that takes filters= carries it; None without it, a 400 outside the blackbody grid."""
    if q.one("white") is None:
        return None
    white_k = q.number("white", 0.0)
    if not BLACKBODY_GRID[0] <= white_k <= BLACKBODY_GRID[-1]:
        raise BadRequest(f"white={white_k!r} is outside {BLACKBODY_GRID[0]:g}..{BLACKBODY_GRID[-1]:g} K")
    return {"kelvin": white_k, "response": [_number(v) for v in _spectra.blackbody_response(curves, np.array([white_k]))[0]]}


def _object_filters(q: Query) -> tuple[list[Any] | None, dict[str, Any] | None]:
    """filters= and white= on an object route (S48): optional there, parsed and refused as /api/render does; white=
    alone is refused, a white point being a response through curves."""
    if q.one("filters") is None:
        if q.one("white") is not None:
            raise BadRequest("white= is a blackbody's response through the curves of filters=; give them with it")
        return None, None
    curves = _parse_filters(q)
    return curves, _white_point(q, curves)


# What an object route's ``response`` array is, in its header (S48, D200 (5), D201).
OBJECT_RESPONSE_ABOUT = (
    "each object's light through each curve, Lsun: its light in the table's eight bands U..K (a star's own magnitudes; "
    "a cluster's, its burst's at its age and [Fe/H] times its mass) as lambda L_lambda anchors, joined as the field's "
    "stars are - power laws between the anchors, made band-consistent, a blackbody at "
    "its temperature beyond U and K - and integrated through the curve (spectra.object_response: the field's own "
    "machinery on one-dimensional tables; an anchor below 1e-12 of the object's brightest is floored there). NaN where "
    "an object has light and no temperature (B9). Drawn as a point of this light in each filter, the object and the "
    "field are the same physics"
)


def _object_response_header(curves: Sequence[Any], white: dict[str, Any] | None, temperature: str) -> dict[str, Any]:
    """What an object route's header gains with filters= (S48): the curves echoed, the white point as /api/render
    carries it, and what the body's ``response`` array is."""
    return {
        "filters": [c.json() for c in curves],
        "white": white,
        "response": {"unit": "Lsun", "axes": ["row", "filter"], "temperature": temperature, "about": OBJECT_RESPONSE_ABOUT},
    }


def _json(payload: Mapping[str, Any], status: int = 200, stages: tuple[str, ...] = ()) -> Response:
    return Response(status, JSON, json.dumps(payload, allow_nan=False).encode("utf-8"), stages)


class CellCache:
    """Materialised cells, kept between requests.

    The catalogue draws every cell from its own seed, so a cell drawn alone is the cell drawn
    in any set and a window's catalogue is its cells' rows in cell order (D60). Materialising
    costs about 0.4 ms of Python per cell before a star is made, 1024 cells to a galaxy, so a
    view that asked for the same window twice — every zoom step of the brightest mode, which
    re-selects inside the same pool — waited half a second for rows the server had just made.
    Bounded by rows, least recently used out first. A key names the galaxy the rows belong to
    (model, grid, resolved inputs, sample size, seed); the caller makes it.
    """

    def __init__(self, max_rows: int = 1_500_000) -> None:
        self.max_rows = max_rows
        self._cells: OrderedDict[tuple[str, int], tuple[dict[str, np.ndarray], int]] = OrderedDict()
        self._rows = 0
        self._lock = threading.Lock()

    def catalogue(self, key: str, cells: Sequence[int], make: Any) -> Any:
        """The catalogue of ``cells`` under ``key``, materialising the ones not held via ``make(cells)``."""
        cells = [int(c) for c in cells]
        if not cells:
            return make([])  # the typed empty catalogue, as the stage makes it
        with self._lock:
            held = {c: self._cells.get((key, c)) for c in cells}
        missing = [c for c, h in held.items() if h is None]
        if missing:
            made = make(missing)
            runs = dict(made.counts)
            offset = 0
            fresh: dict[int, tuple[dict[str, np.ndarray], int]] = {}
            for cell in missing:
                # cell_counts lists cells in the order asked, so the runs follow `missing`.
                count = runs.get(cell, 0)
                fresh[cell] = ({name: np.asarray(col)[offset:offset + count] for name, col in made.items()}, count)
                offset += count
            with self._lock:
                for cell, entry in fresh.items():
                    old = self._cells.pop((key, cell), None)
                    if old is not None:
                        self._rows -= old[1]
                    self._cells[(key, cell)] = entry
                    self._rows += entry[1]
                while self._rows > self.max_rows and self._cells:
                    _, (_, dropped) = self._cells.popitem(last=False)
                    self._rows -= dropped
            held.update(fresh)
        with self._lock:
            # Touch the hits, so what a view keeps asking for stays.
            for cell in cells:
                entry = self._cells.pop((key, cell), None)
                if entry is not None:
                    self._cells[(key, cell)] = entry
        entries = [held[c] for c in cells]
        counts = [(c, n) for c, (_, n) in zip(cells, entries) if n]
        names = list(entries[0][0]) if entries else []
        columns = {name: np.concatenate([e[0][name] for e in entries]) for name in names}
        return _catalogue.Catalogue.of(columns, counts)


class BrightCache:
    """The bright catalogue's finest cells, kept between requests (S48).

    A cell's stars above a threshold are a prefix of its stars above any lower one (``bright.py``'s ordered
    process), so a cell is held with the lowest threshold it was drawn to and serves any higher one by
    cutting the prefix whose Γ lies under the higher threshold's expected count; a lower one draws the cell
    again, longer, from the same streams. Bounded by rows (an empty cell counts as one), least recently used
    out first. A key names the galaxy (model, grid, resolved inputs, seed); the caller makes it.
    """

    def __init__(self, max_rows: int = 2_000_000) -> None:
        self.max_rows = max_rows
        self._cells: OrderedDict[tuple[str, int], tuple[float, dict[str, np.ndarray], int]] = OrderedDict()
        self._rows = 0
        self._lock = threading.Lock()

    def fetch(self, key: str, galaxy: Any, seed: int, cells: Sequence[int], l_min: float) -> Any:
        """Every star above ``l_min`` in ``cells``, grouped by cell in the order asked, as ``materialise_bright``."""
        cells = [int(c) for c in cells]
        log_l = math.log10(max(float(l_min), 10.0 ** float(_bright.LOG_L_GRID[0])))
        with self._lock:
            held = {c: self._cells.get((key, c)) for c in cells}
        missing = [c for c, h in held.items() if h is None or h[0] > log_l]
        if missing:
            made = _bright.materialise_bright(galaxy, seed, missing, l_min)
            runs = dict(made.counts)
            starts = np.concatenate([[0], np.cumsum([runs.get(c, 0) for c in missing])])
            fresh = {
                c: (log_l, {name: np.asarray(col)[starts[i]:starts[i + 1]] for name, col in made.items()}, runs.get(c, 0))
                for i, c in enumerate(missing)
            }
            with self._lock:
                for c, entry in fresh.items():
                    old = self._cells.pop((key, c), None)
                    if old is not None:
                        self._rows -= max(old[2], 1)
                    self._cells[(key, c)] = entry
                    self._rows += max(entry[2], 1)
                while self._rows > self.max_rows and self._cells:
                    _, (_, _, dropped) = self._cells.popitem(last=False)
                    self._rows -= max(dropped, 1)
            held.update(fresh)
        with self._lock:
            for c in cells:
                entry = self._cells.pop((key, c), None)
                if entry is not None:
                    self._cells[(key, c)] = entry
        ceilings = galaxy.expected(cells, log_l) if cells else np.zeros(0)
        parts: list[dict[str, np.ndarray]] = []
        counts: list[tuple[int, int]] = []
        for c, ceiling in zip(cells, ceilings):
            _, columns, n = held[c]
            keep = int(np.searchsorted(columns["gamma"], ceiling, side="left")) if n else 0
            if keep:
                parts.append({name: col[:keep] for name, col in columns.items()})
                counts.append((c, keep))
        if not parts:
            return _bright.materialise_bright(galaxy, seed, [], l_min)
        return _catalogue.Catalogue.of({name: np.concatenate([p[name] for p in parts]) for name in parts[0]}, counts)


class Query:
    """Parsed query parameters, with the coercions the routes need and no others."""

    __slots__ = ("_pairs",)

    def __init__(self, raw: str | Mapping[str, Sequence[str]] | None = None) -> None:
        pairs: list[tuple[str, str]] = []
        if isinstance(raw, str):
            pairs = list(parse_qsl(raw.lstrip("?"), keep_blank_values=True))
        elif raw is not None:
            pairs = [(k, str(v)) for k, vs in raw.items() for v in (vs if not isinstance(vs, str) else [vs])]
        self._pairs = pairs

    def one(self, name: str, default: str | None = None) -> str | None:
        found = [v for k, v in self._pairs if k == name]
        if len(found) > 1:
            raise BadRequest(f"{name} was given {len(found)} times")
        return found[0] if found else default

    def number(self, name: str, default: float) -> float:
        raw = self.one(name)
        if raw is None:
            return default
        try:
            value = float(raw)
        except ValueError:
            raise BadRequest(f"{name}={raw!r} is not a number") from None
        if not math.isfinite(value):
            raise BadRequest(f"{name}={raw!r} is not finite")
        return value

    def integer(self, name: str, default: int) -> int:
        raw = self.one(name)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            raise BadRequest(f"{name}={raw!r} is not an integer") from None

    def names(self, name: str) -> tuple[str, ...]:
        """A repeated or comma-separated list, order preserved, duplicates dropped."""
        out: list[str] = []
        for key, value in self._pairs:
            if key != name:
                continue
            out.extend(part for part in value.split(",") if part)
        return tuple(dict.fromkeys(out))

    def rest(self) -> dict[str, str]:
        """Everything that is not a reserved parameter: the input overrides."""
        out: dict[str, str] = {}
        for key, value in self._pairs:
            if key in RESERVED:
                continue
            if key in out:
                raise BadRequest(f"{key} was given twice")
            out[key] = value
        return out


def _number(value: Any) -> Any:
    """JSON has no NaN. A missing number is published as ``null``, never as a value (rule B9)."""
    if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        f = float(value)
        return f if math.isfinite(f) else None
    return value


def _ramp(ramp: Ramp | Palette | None) -> dict[str, Any] | None:
    if isinstance(ramp, Ramp):
        return {"kind": "ramp", "cmap": ramp.cmap, "scale": ramp.scale, "lo": ramp.lo, "hi": ramp.hi}
    if isinstance(ramp, Palette):
        return {"kind": "palette", "colors": list(ramp.colors)}
    return None


def field_json(decl: FieldDecl, stage: Stage) -> dict[str, Any]:
    """A field declaration on the wire. The ramp travels with it and nowhere else (rule A9)."""
    u = _unit(decl.unit)
    return {
        "name": decl.name,
        "label": decl.label,
        "unit": decl.unit,
        "unit_display": u.display,
        "dimension": u.dimension,
        "kind": decl.kind.value,
        "domain": decl.kind.domain,
        "categorical": decl.kind.categorical,
        "axes": list(decl.axes),
        "of": decl.of,
        "categories": list(decl.categories),
        "ramp": _ramp(decl.ramp),
        "meaningful_zero": decl.meaningful_zero,
        "optional": decl.optional,
        "provenance": decl.provenance,
        "about": decl.about,
        "stage": stage.id,
        "checkpoint": stage.checkpoint,
    }


def input_json(inp: Input) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": inp.name,
        "label": inp.label,
        "kind": inp.kind,
        "about": inp.about,
        "checkpoint": inp.checkpoint_hypothesis,
        "unset": inp.unset,
    }
    if inp.kind == "control":
        u = _unit(inp.unit or "dimensionless")
        payload |= {
            "unit": inp.unit,
            "unit_display": u.display,
            "dimension": u.dimension,
            "default": None if inp.unset else _number(inp.default),
            "lo": inp.lo,
            "hi": inp.hi,
        }
    elif inp.kind == "seed":
        payload |= {"default": int(inp.default)}  # type: ignore[arg-type]
    else:
        payload |= {"default": [_event_json(e) for e in inp.default]}  # type: ignore[union-attr]
    return payload


def _event_json(event: MergerEvent) -> dict[str, Any]:
    return {
        "time": event.time,
        "mass_ratio": event.mass_ratio,
        "gas_fraction": event.gas_fraction,
        "about": event.about,
    }


def grid_json(grid: Grid) -> dict[str, Any]:
    """The axes a field is sampled on: the viewer cannot place an image without them."""
    return {
        "axes": {
            name: {
                "unit": axis.unit,
                "unit_display": _unit(axis.unit).display,
                "n": axis.n,
                "lo": axis.lo,
                "hi": axis.hi,
                "width": axis.width,
            }
            for name, axis in grid.axes.items()
        }
    }


class Galaxy:
    """One point in input space, computed no further than it has been asked to be.

    The stages already run are kept, so a second question that needs more of the
    pipeline runs only the difference (``run(..., resume=…)``). This is a cache of
    *work*, not of answers: nothing here can make an endpoint appear to run fewer
    stages than it needs, because a stage that has not run is not in it.
    """

    __slots__ = ("model", "inputs", "grid", "_impls", "_table", "_out")

    def __init__(self, model: Model, inputs: Mapping[str, Any], grid: Grid, impls: Any, table: Any) -> None:
        self.model = model
        self.inputs = dict(inputs)
        self.grid = grid
        self._impls = impls
        self._table = table
        self._out: Outputs | None = None

    def need(self, fields: Sequence[str]) -> tuple[Outputs, tuple[str, ...]]:
        out = _run(
            self.model, self.inputs, self.grid,
            impls=self._impls, table=self._table, only=tuple(fields), resume=self._out,
        )
        self._out = out
        return out, out.ran


class Service:
    """The routes over one registry, one grid and a small cache of galaxies."""

    def __init__(
        self,
        *,
        models: Registry[Model] | None = None,
        impls: Registry[Stage] | Mapping[str, Stage] | None = None,
        table: Mapping[str, Input] | None = None,
        grid: GridSpec | Grid = DEFAULT,
        cache: int = 2,
        client=CLIENT,
        server=SERVER,
    ) -> None:
        if models is None or impls is None or table is None:
            p_models, p_impls, p_table = production()
            models = p_models if models is None else models
            impls = p_impls if impls is None else impls
            table = p_table if table is None else table
        self.models = models
        self.impls = impls
        self.table = table
        self.grid = grid.build() if isinstance(grid, GridSpec) else grid
        self.client = client
        self.server = server
        self.cache_size = max(0, int(cache))
        self._cache: dict[str, Galaxy] = {}
        self.cells = CellCache()
        self.bright = BrightCache()  # S48: the bright catalogue's finest cells
        self._bright_galaxies: OrderedDict[str, Any] = OrderedDict()  # its per-galaxy tables, and the default limit
        # The server is threaded, and two requests for one galaxy would otherwise
        # resume the same partial run from two threads. Computation is serialised;
        # metadata, which touches nothing, is not.
        self._lock = threading.RLock()
        # One handler per declared route: a route in the table with no handler is
        # a startup failure, not a 404 discovered by whoever calls it.
        self._handlers = {r.path: getattr(self, "_" + r.handler) for r in ROUTES}

    # --- plumbing ------------------------------------------------------------

    def handle(self, path: str, query: str | Mapping[str, Sequence[str]] | None = None) -> Response:
        """Answer one request. Never raises for a bad request; returns its status."""
        route = path.rstrip("/") or "/"
        handler = self._handlers.get(route)
        try:
            if handler is not None:
                return handler(Query(query))
            if route.startswith("/api"):
                raise NotFound(f"no such route; this service answers {[r.path for r in ROUTES]}")
            # Anything else is asked of the viewer's directory, and answered from
            # it or not at all — the API serves declarations and files, never a
            # path the caller composed (rule D5).
            return self._file(route)
        except ApiError as e:
            return _json({"error": str(e), "route": route}, e.status)
        except RunError as e:
            # A rejected input vector is the caller's mistake, not the server's.
            return _json({"error": str(e), "route": route}, 400)

    def _model(self, q: Query) -> Model:
        name = q.one("model") or self.models.names()[0]
        if name not in self.models:
            raise NotFound(f"no model {name!r}; registered: {list(self.models.names())}")
        return self.models.get(name)

    def _graph(self, model: Model) -> _graph.Graph:
        """Declarations only: ``analyse`` reads the stage table and computes nothing."""
        return _graph.analyse(model, self.impls, self.table)

    def _overrides(self, model: Model, q: Query) -> dict[str, Any]:
        accepted = set(model.input_names(self.table))
        out: dict[str, Any] = {}
        for name, raw in q.rest().items():
            if name not in accepted:
                raise NotFound(f"model {model.name!r} has no input {name!r}")
            inp = self.table[name]
            if inp.kind == "control":
                try:
                    value = float(raw)
                except ValueError:
                    raise BadRequest(f"{name}={raw!r} is not a number") from None
                if not math.isfinite(value):
                    raise BadRequest(f"{name}={raw!r} is not finite")
                if inp.lo is not None and inp.hi is not None and not inp.lo <= value <= inp.hi:
                    raise BadRequest(f"{name}={value!r} is outside the published range [{inp.lo}, {inp.hi}]")
                out[name] = value
            elif inp.kind == "seed":
                try:
                    out[name] = int(raw)
                except ValueError:
                    raise BadRequest(f"{name}={raw!r} is not an integer seed") from None
            else:
                out[name] = _events(name, raw)
        return out

    def compute(self, model: Model, inputs: Mapping[str, Any], fields: Sequence[str]) -> tuple[Outputs, tuple[str, ...]]:
        """Advance the galaxy at this point in input space far enough to answer, no further."""
        key = repr((model.name, self.grid.spec, sorted(inputs.items(), key=lambda kv: kv[0])))
        with self._lock:
            found = self._cache.pop(key, None)
            if found is None:
                found = Galaxy(model, inputs, self.grid, self.impls, self.table)
            if self.cache_size:
                self._cache[key] = found
                while len(self._cache) > self.cache_size:
                    del self._cache[next(iter(self._cache))]
            return found.need(fields)

    def _reads(self, model: Model, stage: Stage) -> tuple[str, ...]:
        """What a stage reads in this model: its requirements, and the optional fields the model has."""
        declared = self._declared(model)
        return stage.requires + tuple(n for n in stage.requires_optional if n in declared)

    def _declared(self, model: Model) -> dict[str, tuple[FieldDecl, Stage]]:
        """Every field this model publishes, from declarations. No stage runs."""
        stages, _ = _graph.resolve_stages(model, self.impls)
        return {d.name: (d, st) for st in stages.values() for d in st.publishes}

    # --- routes --------------------------------------------------------------

    def _viewer(self, q: Query) -> Response:
        return self._file("/")

    def _file(self, route: str) -> Response:
        """Serve one file from the client directory. Nothing outside it is reachable."""
        root = Path(self.client).resolve()
        target = (root / (route.strip("/") or "index.html")).resolve()
        if not target.is_relative_to(root):
            raise NotFound(f"{route} is not in the viewer's directory")
        media = MEDIA_TYPES.get(target.suffix)
        if media is None:
            raise NotFound(f"{target.suffix or route} is not a type this service serves")
        if not target.is_file():
            raise NotFound(f"{route} is not there; /api/version lists what is")
        return Response(200, media, target.read_bytes())

    def _index(self, q: Query) -> Response:
        return _json({
            "api": "galaxygen",
            "wire": wire.FORMAT,
            "models": list(self.models.names()),
            "routes": [{"path": r.path, "about": r.about, "params": list(r.params)} for r in ROUTES],
            "inputs_are": "any query parameter that is not one of a route's params",
        })

    def _blackbody(self, q: Query) -> Response:
        """The blackbody response per filter on BLACKBODY_GRID: the table a point of a colour temperature is drawn
        from, as the render's white point is. A function of the curves alone; no model, no stage (rule D4)."""
        curves = _parse_filters(q)
        white = _white_point(q, curves)
        share = _spectra.blackbody_response(curves, BLACKBODY_GRID)
        return _json({
            "filters": [c.json() for c in curves],
            "kelvin": BLACKBODY_GRID.tolist(),
            "share": share.tolist(),
            "interpolate": "log10(share) linear in log10(kelvin); a temperature off the grid takes its end's row",
            "white": white,
        })

    def _version(self, q: Query) -> Response:
        viewer = content_hash(self.client)
        server = content_hash(self.server, suffixes=(".py",))
        return _json({
            "viewer": viewer,
            "api": {k: v for k, v in server.items() if k != "files"},
            "wire": wire.FORMAT,
            "models": list(self.models.names()),
        })

    def _stages(self, q: Query) -> Response:
        model = self._model(q)
        g = self._graph(model)
        order = [st.id for st in g.order]
        return _json({
            "model": model.name,
            "about": model.about,
            "models": list(self.models.names()),
            "order": order,
            "checkpoints": [
                {
                    "n": n,
                    "name": name,
                    "stages": [st.id for st in g.order if st.checkpoint == n],
                }
                for n, name in enumerate(CHECKPOINTS, start=1)
            ],
            "stages": [
                {
                    "id": st.id,
                    "slot": st.slot,
                    "checkpoint": st.checkpoint,
                    "checkpoint_name": st.checkpoint_name,
                    "about": st.about,
                    "publishes": list(st.published_names),
                    "requires": list(st.requires),
                    "requires_optional": list(st.requires_optional),
                    "reads_inputs": list(st.reads_inputs),
                    "reads_seeds": list(st.reads_seeds),
                }
                for st in g.order
            ],
        })

    def _fields(self, q: Query) -> Response:
        model = self._model(q)
        declared = self._declared(model)
        g = self._graph(model)
        order = {st.id: i for i, st in enumerate(g.order)}
        fields = sorted(declared.values(), key=lambda ds: (order.get(ds[1].id, 0), ds[0].name))
        return _json({
            "model": model.name,
            "grid": grid_json(self.grid),
            # The stops behind every cmap a declaration may name. A9 puts the
            # choice of ramp in the declaration; this puts the colours behind the
            # name here too, so a viewer holds no colour of its own.
            "cmaps": {
                name: {"stops": list(c.stops), "diverging": c.diverging, "midpoint": c.midpoint}
                for name, c in COLORMAPS.items()
            },
            "scales": list(SCALES),
            "fields": [field_json(decl, stage) for decl, stage in fields],
        })

    def _inputs(self, q: Query) -> Response:
        model = self._model(q)
        accepted = [self.table[n] for n in model.input_names(self.table)]
        return _json({
            "model": model.name,
            "ceiling": INPUT_CEILING,
            "controls": [input_json(i) for i in accepted if i.kind == "control"],
            "seeds": [input_json(i) for i in accepted if i.kind == "seed"],
            "events": [input_json(i) for i in accepted if i.kind == "events"],
        })

    def _arrays(self, q: Query) -> Response:
        model = self._model(q)
        wanted = q.names("fields")
        if not wanted:
            raise BadRequest("fields= names at least one field; /api/fields lists them")
        declared = self._declared(model)
        missing = [n for n in wanted if n not in declared]
        if missing:
            raise NotFound(f"model {model.name!r} does not publish {missing}")

        precision = q.one("precision", "f8")
        if precision not in ("f8", "f4"):
            raise BadRequest(f"precision={precision!r} is not f8 or f4")
        t_samples = q.integer("t_samples", 0)
        if t_samples < 0:
            raise BadRequest(f"t_samples={t_samples} is negative")

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, wanted)

        # Fewer time steps are a download choice, not a coarser model: the galaxy is computed
        # on its own grid and every stride-th step is sent, sampled, never averaged (rule B9).
        grid = grid_json(out.grid)
        t_axis = out.grid.axes["t"]
        stride = max(1, t_axis.n // t_samples) if 0 < t_samples < t_axis.n else 1
        steps = np.arange(stride // 2, t_axis.n, stride) if stride > 1 else None
        if steps is not None:
            grid["axes"]["t"] = {**grid["axes"]["t"], "n": int(steps.size), "width": t_axis.width * stride}

        arrays: list[tuple[str, np.ndarray]] = []
        scalars: dict[str, Any] = {}
        for name in wanted:
            decl = declared[name][0]
            value = out.fields[name]
            if decl.kind.domain == "galaxy":
                scalars[name] = _number(value) if not decl.kind.categorical else value
                continue
            arr = np.asarray(value)
            if steps is not None and "t" in decl.axes:
                arr = np.take(arr, steps, axis=decl.axes.index("t"))
            if precision == "f4" and arr.dtype == np.float64:
                arr = arr.astype(np.float32)
            arrays.append((name, arr))
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "grid": grid,
            "fields": list(wanted),
            "scalars": scalars,
            "stages": list(ran),
            "sampling": {"t_stride": stride, "t_first": int(steps[0]) if steps is not None else 0, "precision": precision},
        }
        return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)

    def _region(self, q: Query) -> Response:
        model = self._model(q)
        stage = _stage_for(model, CATALOGUE_SLOT, self.impls)

        R, t = self.grid.R, self.grid.t
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        stars = q.integer("stars", _catalogue.CATALOGUE_SAMPLE)
        if not 1 <= stars <= MAX_STARS:
            raise BadRequest(f"stars={stars} is outside 1..{MAX_STARS}")
        brightest = q.integer("brightest", 0)
        if not 0 <= brightest <= MAX_BRIGHTEST:
            raise BadRequest(f"brightest={brightest} is outside 0..{MAX_BRIGHTEST}")
        view = _view_matrix(q.one("view"))
        if view is not None and not brightest:
            raise BadRequest("view= only means something with brightest=N")
        level = _level(q)
        if level and brightest:
            raise BadRequest("brightest= is a level-0 selection; below level 0 every row already carries its name")

        inputs = self._overrides(model, q)
        # What the catalogue *reads*, which is not the catalogue: the closure
        # above these fields stops one stage short of materialising anything.
        out, ran = self.compute(model, inputs, self._reads(model, stage))
        seed_name = stage.reads_seeds[0] if stage.reads_seeds else None
        seed = int(out.inputs[seed_name]) if seed_name else 0

        cells = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level)
        if level and len(cells) > MAX_CHILD_CELLS:
            raise BadRequest(f"level={level} over this window names {len(cells)} cells, more than {MAX_CHILD_CELLS}: narrow the window")
        migration = float(out.inputs["migration_efficiency"])
        key = repr((model.name, self.grid.spec, sorted(_inputs_json(out.inputs).items()), stars, seed, level))
        catalogue = self.cells.catalogue(
            key, cells,
            # level= only below level 0, so the level-0 call keeps its signature for the instruments
            # that wrap materialise (test_api's cache count).
            lambda wanted: _catalogue.materialise(out.fields, R, t, seed, stars, wanted, migration=migration, **({"level": level} if level else {})),
        )
        columns = [d.name for d in stage.publishes if d.kind.domain == "object" and d.name in catalogue]
        selection = None
        if brightest:
            catalogue, selection = _brightest(catalogue, brightest, view)
            columns += ["cell", "index"]
        if level:
            # Below level 0 the rows carry their canonical names: an inherited star its parent's
            # (level 0, cell, index), an extra star its child's (level, child, index) - S32.
            columns += ["level", "cell", "index"]
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "level": level,
            # With brightest=N the rows are a selection, named by their own cell and index columns
            # rather than by the runs below, which describe the pool they were chosen from.
            "brightest": selection,
            # The cells that actually realised a star, with how many each has: that
            # is what names a row. Star r of this response is index (r - offset) of
            # the cell whose run covers it, and a system is opened by that name
            # (D60, §12) rather than by a position, which can drift a ring (D69).
            "cells": {
                "ids": [c for c, _ in catalogue.counts],
                "counts": [n for _, n in catalogue.counts],
                "count": len(catalogue.counts),
                "requested": len(cells),
                "of": _catalogue.CELL_COUNT * _catalogue.children_per_cell(level),
                "bounds": [_catalogue.cell_bounds(R, c, level) for c, _ in catalogue.counts]
                if len(catalogue.counts) <= 64
                else [],
            },
            "stars": {"requested": stars, "materialised": int(catalogue.size), "seed": seed},
            "columns": columns,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, catalogue[c]) for c in columns]), ran)

    def _clouds(self, q: Query) -> Response:
        """The molecular-cloud census of one window (S32): the clouds of every level-0 cell the window
        meets, whole cells as the star route gives; at level k, the clouds inside the children it meets.
        A census, so no sample size: the same clouds whatever the window (D60)."""
        model = self._model(q)
        stage = _stage_for(model, CLOUDS_SLOT, self.impls)
        R = self.grid.R
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        level = _level(q)

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, self._reads(model, stage))
        seed = int(out.inputs[stage.reads_seeds[0]])
        constants = {k: c.value for k, c in model.constants.items()}
        parents = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max)
        key = repr(("clouds", model.name, self.grid.spec, sorted(_inputs_json(out.inputs).items()), seed))
        census = self.cells.catalogue(
            key, parents, lambda wanted: _clouds.materialise_clouds(out.fields, R, seed, constants, wanted),
        )
        columns = [d.name for d in stage.publishes if d.kind.domain == "object" and d.name in census]
        census = _named(census)  # S40: every row named by (cell, index)
        kept = None
        if level:
            census, kept = _in_children(census, "cloud", R, _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level), level)
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "level": level,
            "cells": {
                "ids": [c for c, _ in census.counts],
                "counts": [n for _, n in census.counts],
                "count": len(census.counts),
                "requested": len(parents),
                "of": _catalogue.CELL_COUNT,
            },
            "clouds": {"materialised": int(census.size) if kept is None else kept, "seed": seed},
            # Three of the stage's galaxy scalars, which rule D4 keeps off the viewer's scalars surface
            # (D148): a renderer that synthesises a cloud's interior reads b and the lifetime here. The
            # stage itself does not run for a window, so the realised mass total is /api/arrays' alone.
            "scalars": {
                "cloud_count_total": float(_clouds.expected_counts(out.fields, R, constants).sum()),
                "cloud_forcing_parameter": float(constants["TURBULENCE_FORCING_B"]),
                "cloud_lifetime": float(constants["GMC_PHASE_EMBEDDED"] + constants["GMC_PHASE_BLOWN_OPEN"]
                                        + constants["GMC_PHASE_DISPERSING"]),
                # S40 (V3): the census's one central A_V, for the region regime's cloud interiors.
                "cloud_extinction_v": float(_clouds.central_extinction_v(
                    np.array([1.0e5]), np.array([_clouds.cloud_radius_pc(np.array([1.0e5]), float(constants["GMC_SURFACE_DENSITY"]))[0]]),
                    float(constants["HII_MASS_PER_HYDROGEN"]), _clouds._grain_v_extinction(),
                )[0]),
            },
            "columns": columns,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, census[c]) for c in columns] + [("cell", census["cell"]), ("index", census["index"])]), ran)

    def _clusters(self, q: Query) -> Response:
        """The star-cluster census of one window (S33): the clusters of every level-0 cell the window meets,
        drawn from those cells' clouds exactly as the stage draws them; at level k, the clusters inside the
        children it meets. The clusters stage does not run, nor the clouds stage: the cells' clouds are
        materialised here from what the clouds read, as ``/api/clouds`` does (D4)."""
        model = self._model(q)
        stage = _stage_for(model, CLUSTERS_SLOT, self.impls)
        nebular = _stage_for(model, NEBULAR_SLOT, self.impls)
        bubbles = _stage_for(model, BUBBLES_SLOT, self.impls)
        R = self.grid.R
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        level = _level(q)
        curves, white = _object_filters(q)

        inputs = self._overrides(model, q)
        # What the stage reads other than the cloud columns, which the census here draws for itself.
        reads = tuple(n for n in self._reads(model, stage) if n not in _clusters.CLOUD_READS)
        out, ran = self.compute(model, inputs, reads)
        seed = int(out.inputs[stage.reads_seeds[0]])
        constants = {k: c.value for k, c in model.constants.items()}
        parents = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max)
        key = repr(("clusters", model.name, self.grid.spec, sorted(_inputs_json(out.inputs).items()), seed))

        def draw(wanted: Sequence[int]) -> Any:
            clouds = _clouds.materialise_clouds(out.fields, R, seed, constants, wanted)
            clusters = _clusters.materialise_clusters(clouds, out.fields, R, seed, constants)
            regions = _nebular.materialise_nebular(clusters, clouds, constants)  # S35: the region is the cluster's
            blown = _bubbles.materialise_bubbles(clusters, regions, constants)  # S36: and so is the bubble
            return _catalogue.Catalogue.of({**clusters, **regions, **blown}, clusters.counts)

        census = self.cells.catalogue(key, parents, draw)
        columns = [
            d.name for st in (stage, nebular, bubbles) for d in st.publishes
            if d.kind.domain == "object" and d.of == "cluster" and d.name in census
        ]
        census = _named(census)  # S40: every row named by (cell, index)
        kept = None
        if level:
            census, kept = _in_children(census, "cluster", R, _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level), level)
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "level": level,
            "cells": {
                "ids": [c for c, _ in census.counts],
                "counts": [n for _, n in census.counts],
                "count": len(census.counts),
                "requested": len(parents),
                "of": _catalogue.CELL_COUNT,
            },
            "clusters": {"materialised": int(census.size) if kept is None else kept, "seed": seed},
            # The stage's galaxy scalars, which rule D4 keeps off the viewer's scalars surface (D148):
            # population integrals, the same numbers /api/arrays serves when the stage runs.
            "scalars": {
                "cluster_formation_efficiency": _clusters.mean_efficiency(
                    out.fields["sfr_surface_density"], out.fields["gas_molecular_surface_density"], R,
                    _clusters.cloud_lifetime(constants),
                ),
                "bound_cluster_mass_total": _clusters.bound_mass(
                    out.fields["stars_formed_history"], R, float(constants["CLUSTER_BOUND_FRACTION"])
                ),
            },
            "columns": columns,
            "stages": list(ran),
        }
        arrays = [(c, census[c]) for c in columns] + [("cell", census["cell"]), ("index", census["index"])]
        if curves is not None:
            # S48's wiring (D200 (5)): the cluster's own band light - the burst's tables at its age and [Fe/H] times its
            # mass, cluster_luminosity's convention - through the viewer's curves at its colour temperature.
            anchors = _clusters.band_anchors(census["cluster_mass"], census["cluster_age"], census["cluster_metallicity"])
            arrays.append(("response", _spectra.object_response(anchors, np.asarray(census["cluster_light_temperature"], dtype=float), curves)))
            header.update(_object_response_header(curves, white, "cluster_light_temperature"))
        return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)

    def _remnants(self, q: Query) -> Response:
        """The supernova-remnant census of one window (S36): the remnants of every level-0 cell the window meets,
        drawn exactly as the stage draws them from the rates it reads; at level k, those inside the children it
        meets. The stage does not run, and neither does anything that makes clusters: the census reads the rates
        and the gas, nothing else (D4)."""
        model = self._model(q)
        stage = _stage_for(model, BUBBLES_SLOT, self.impls)
        R = self.grid.R
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        level = _level(q)

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, tuple(n for n in self._reads(model, stage) if n in _bubbles.REMNANT_READS))
        seed = int(out.inputs[stage.reads_seeds[0]])
        constants = {k: c.value for k, c in model.constants.items()}
        parents = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max)
        key = repr(("remnants", model.name, self.grid.spec, sorted(_inputs_json(out.inputs).items()), seed))
        census = self.cells.catalogue(
            key, parents, lambda wanted: _bubbles.materialise_remnants(out.fields, R, seed, constants, wanted),
        )
        columns = [d.name for d in stage.publishes if d.kind.domain == "object" and d.of == "remnant" and d.name in census]
        census = _named(census)  # S40: every row named by (cell, index)
        kept = None
        if level:
            census, kept = _in_children(census, "remnant", R, _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level), level)
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "level": level,
            "cells": {
                "ids": [c for c, _ in census.counts],
                "counts": [n for _, n in census.counts],
                "count": len(census.counts),
                "requested": len(parents),
                "of": _catalogue.CELL_COUNT,
            },
            "remnants": {"materialised": int(census.size) if kept is None else kept, "seed": seed},
            # The stage's galaxy scalar, which rule D4 keeps off the viewer's scalars surface (D148): the
            # population integral /api/arrays serves when the stage runs.
            "scalars": {"remnant_count_total": float(_bubbles.remnant_expected(out.fields, R, constants).sum())},
            "columns": columns,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, census[c]) for c in columns] + [("cell", census["cell"]), ("index", census["index"])]), ran)

    def _bright_galaxy(self, key: str, out: Outputs, model: Model) -> tuple[Any, dict[str, float]]:
        """The bright catalogue's tables for one galaxy, and its stage's two scalars - the default selection's
        limit is the whole disc's brightest few thousand, materialised once through the cell cache - kept for
        the last two galaxies asked about."""
        with self._lock:
            found = self._bright_galaxies.pop(key, None)
            if found is None:
                constants = {k: c.value for k, c in model.constants.items()}
                spec = self.grid.spec
                galaxy = _bright.BrightGalaxy(out.fields, self.grid.R, self.grid.t, float(spec.t_max), int(spec.n_t), constants)
                seed = int(out.inputs["systems_seed"])
                cells = _bright.all_cells()
                _, info = _bright.select_brightest(
                    galaxy, seed, cells, _bright.DEFAULT_SELECTION,
                    fetch=lambda wanted, l: self.bright.fetch(key, galaxy, seed, wanted, l),
                )
                found = (galaxy, _bright.scalars(galaxy, info["l_min"]))
            self._bright_galaxies[key] = found
            while len(self._bright_galaxies) > 2:
                del self._bright_galaxies[next(iter(self._bright_galaxies))]
            return found

    def _bright(self, q: Query) -> Response:
        """Every disc star above a luminosity in one window (S48, D200): the finest cells the window meets, their
        ordered Poisson processes cut at a threshold - found by bisection on the expected count for ``n``, given for
        ``l_min``. Runs what the stage reads and not the stage (rule D4); the cells are cached between requests."""
        model = self._model(q)
        stage = _stage_for(model, BRIGHT_SLOT, self.impls)
        R = self.grid.R
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        view = _view_matrix(q.one("view"))
        precision = q.one("precision", "f8")
        if precision not in ("f8", "f4"):
            raise BadRequest(f"precision={precision!r} is not f8 or f4")
        has_n, has_l = q.one("n") is not None, q.one("l_min") is not None
        if has_n == has_l:
            raise BadRequest(f"give exactly one of n= (1..{MAX_BRIGHTEST}) or l_min= (Lsun)")
        n = q.integer("n", 0) if has_n else None
        if n is not None and not 1 <= n <= MAX_BRIGHTEST:
            raise BadRequest(f"n={n} is outside 1..{MAX_BRIGHTEST}")
        l_min = q.number("l_min", 0.0) if has_l else None
        if l_min is not None and not l_min > 0.0:
            raise BadRequest(f"l_min={l_min!r} is not a positive luminosity")
        curves, white = _object_filters(q)

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, self._reads(model, stage))
        seed = int(out.inputs[stage.reads_seeds[0]])
        key = repr(("bright", model.name, self.grid.spec, sorted(_inputs_json(out.inputs).items()), seed))
        galaxy, scalars = self._bright_galaxy(key, out, model)
        cells = np.asarray(_catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=_catalogue.MAX_LEVEL), dtype=np.int64)

        def fetch(wanted: Sequence[int], threshold: float) -> Any:
            return self.bright.fetch(key, galaxy, seed, wanted, threshold)

        faint = 10.0 ** float(_bright.LOG_L_GRID[0])
        if n is not None:
            rows, info = _bright.select_brightest(galaxy, seed, cells, n, view=view, fetch=fetch, pool_max=MAX_BRIGHT_POOL)
            threshold = {"l_min": info["l_min"], "complete": info["complete"], "why": info["why"]}
            used = info["l_min"]
        else:
            used = max(float(l_min), faint)
            expected = float(galaxy.expected(cells, math.log10(used)).sum())
            if expected > MAX_BRIGHTEST:
                raise BadRequest(
                    f"l_min={l_min:g} holds {expected:.0f} expected stars in this window, more than {MAX_BRIGHTEST}: "
                    "raise it or narrow the window"
                )
            pool = fetch(cells, used)
            lum = np.asarray(pool["bright_star_luminosity"], dtype=float)
            keep = np.arange(lum.size)
            if view is not None and keep.size:
                keep = keep[_bright.in_frustum(view, pool["bright_star_radius"], pool["bright_star_azimuth"], pool["bright_star_height"])]
            rows = _catalogue.Catalogue.of({name: np.asarray(col)[keep[np.argsort(-lum[keep], kind="stable")]] for name, col in pool.items()})
            why = "every star above l_min is in the body"
            if l_min < faint:
                why += f"; the luminosity function starts at {faint:g} Lsun, so none fainter exists here"
            threshold = {"l_min": used, "complete": True, "why": why}
        log_used = math.log10(max(used, faint))
        columns = [d.name for d in stage.publishes if d.kind.domain == "object"] + ["cell", "rank"]
        lum = np.asarray(rows["bright_star_luminosity"], dtype=float)
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "view": view is not None,
            "cells": {"count": int(cells.size), "level": _catalogue.MAX_LEVEL,
                      "of": _catalogue.CELL_COUNT * _catalogue.children_per_cell(_catalogue.MAX_LEVEL)},
            "threshold": threshold,
            # Expected over the window's cells (not the frustum): the luminosity function's count and light above l_min.
            "count": {"returned": int(lum.size), "expected": float(galaxy.expected(cells, log_used).sum())},
            "light": {
                "returned": float(lum.sum()),
                # The field's budget above l_min (the luminosity function renormalised to the field's tables) and
                # the stars' own; they differ by how well the field's mass grid resolves the giant branch (D200).
                "expected": float(galaxy.expected(cells, log_used, "light").sum()),
                "expected_own": float(galaxy.expected(cells, log_used, "light_own").sum()),
            },
            "columns": columns,
            "scalars": scalars,
            "seed": seed,
            "stages": list(ran),
        }
        arrays = [(c, np.asarray(rows[c])) for c in columns]
        if curves is not None:
            # S48's wiring (D200 (5), D201): each star's band light through the viewer's curves, at its own temperature.
            anchors = _spectra.object_nu_l_nu(_bright.magnitudes(rows))
            arrays.append(("response", _spectra.object_response(anchors, np.asarray(rows["bright_star_temperature"], dtype=float), curves)))
            header.update(_object_response_header(curves, white, "bright_star_temperature"))
        if precision == "f4":
            arrays = [(c, a.astype(np.float32) if a.dtype == np.float64 else a) for c, a in arrays]
        return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)

    def _render(self, q: Query) -> Response:
        """The components through the viewer's filters (RENDER_PHYSICS §§2, 3a; S38, V1).

        The viewer holds its filters as data and sends their curves; this evaluates each published
        emitting component through each curve (``stages/spectra.py``) and returns the responses per
        cell, one array per component, never summed into a colour (§2). The viewer multiplies them by
        its tone map and does nothing else (rule D5). The stages run are the closure of the fields
        read, as for ``/api/arrays`` (rule D4): the nebular line is a checkpoint-5 field, so a render
        runs the census stages its Hα is redistributed from.

        **Since S39 (V2)** the line is two volumetric layers and the dust three components (extinction,
        scattered, thermal), each named in the header's ``components`` with the fields it reads, and
        every component's vertical layer in ``layers``: the arrays are face-on columns the viewer spreads
        through their layers and integrates along each ray. What the frame's dust removes and what it
        emits balance (``tests/test_render.py``).
        """
        model = self._model(q)
        curves = _parse_filters(q)
        precision = q.one("precision", "f8")
        if precision not in ("f8", "f4"):
            raise BadRequest(f"precision={precision!r} is not f8 or f4")
        white = _white_point(q, curves)
        level = None if q.one("level") is None else _level(q)
        l_min = None if q.one("l_min") is None else q.number("l_min", 0.0)
        if l_min is not None and not l_min > 0.0:
            raise BadRequest(f"l_min={l_min!r} is not a positive luminosity")

        declared = self._declared(model)
        missing = [n for n in RENDER_STARS if n not in declared]
        if missing:
            raise NotFound(f"model {model.name!r} does not publish {missing}, which the stellar component is")
        wanted = [*RENDER_STARS, *(n for n in RENDER_OPTIONAL if n in declared)]
        if l_min is not None:
            # S48's wiring (D200 (4)): what the field's remainder decomposes - the bright stage's reads, only those (D4).
            bright = _stage_for(model, BRIGHT_SLOT, self.impls)
            wanted += [n for n in self._reads(model, bright) if n in _bright.RESOLVE_READS and n not in wanted]
        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, wanted)
        f = out.fields
        R_axis, phi_axis = out.grid.axes["R"], out.grid.axes["phi"]
        R = out.grid.R

        # The components on the whole grid: the stars per (R, phi), the line and the dust per R.
        sed = np.stack([np.asarray(f[f"disc_sed_{b.lower()}"], dtype=float) for b in _spectra.SED_BANDS], axis=-1)
        per_ring = _spectra.stellar_response(sed, f["disc_light_temperature"], curves)
        contrast = f["pattern_density_contrast"] if "pattern_density_contrast" in f else None
        # The stellar light follows the pattern's density contrast around each ring (a constant mass-to-light
        # ratio in azimuth), which averages to 1 around every ring, so each ring keeps its published light.
        placed = np.ones((R.size, phi_axis.n)) if contrast is None else np.maximum(np.asarray(contrast, dtype=float), 0.0)
        stars = per_ring[:, None, :] * placed[..., None]
        halpha_share = _spectra.line_response(curves, _spectra.LINE_WAVELENGTHS["halpha"])
        contrast_fields = ["pattern_density_contrast"] if contrast is not None else []
        # Every component's vertical layer (S39): a sech²(z / 2h) / 4h profile, integrating to one over height,
        # at the scale height named here, kpc. The arrays are face-on columns; the viewer spreads each through
        # its layer and integrates along the ray (RENDER_PHYSICS §4), so a thick layer brightens at the limb.
        h_thin = float(f["thin_disc_scale_height"]) / 1000.0 if "thin_disc_scale_height" in f else None
        layers: dict[str, Any] = {
            "form": "sech2(z / 2h) / 4h, per kpc of height, integrating to 1",
            "stars": h_thin,
            # The dust is mixed with the starlight it absorbs: the dust stage's heating is a uniformly mixed slab.
            "dust": h_thin,
        }
        components: list[tuple[str, np.ndarray]] = [("stars", stars)]
        about: dict[str, Any] = {
            "stars": {
                "unit": "Lsun/pc2", "fields": [*RENDER_STARS, *contrast_fields], "layer": "stars",
                "about": "the population's own spectrum - the eight bands' lambda L_lambda at their reference "
                         "wavelengths, power laws between them, a blackbody at the colour temperature beyond U and K - "
                         "through each curve, placed around each ring by the pattern's density contrast",
                "bands": list(_spectra.SED_BANDS),
                "wavelength": _spectra.SED_WAVELENGTHS.tolist(),
            },
        }
        resolved = None
        if l_min is not None:
            unresolved, about["stars_unresolved"], resolved = self._unresolved(model, f, R, curves, per_ring, contrast, l_min)
            components.append(("stars_unresolved", unresolved))
        line_about ={"unit": "Lsun/pc2", "wavelength": _spectra.LINE_WAVELENGTHS["halpha"], "transmission": halpha_share.tolist()}
        if "halpha_surface_brightness_hii" in f and h_thin is not None:
            hii = np.asarray(f["halpha_surface_brightness_hii"], dtype=float)
            components.append(("halpha_hii", hii[:, None, None] * placed[..., None] * halpha_share))
            layers["halpha_hii"] = _clouds.cloud_layer_height(float(f["thin_disc_scale_height"]))
            about["halpha_hii"] = {
                **line_about, "fields": ["halpha_surface_brightness_hii", *contrast_fields, "thin_disc_scale_height"],
                "layer": "halpha_hii",
                "about": "the HII regions' Halpha through each curve at its wavelength, placed around each ring by the "
                         "pattern's density contrast (the same contrast the stars follow; it averages to 1, so each "
                         "ring keeps its published line) in the clouds' layer, where the regions' clusters are",
            }
        # The other lines (S42): each HII-region line through each curve at its own wavelength, placed and layered
        # as the regions' Halpha is; the diffuse gas's Hbeta beside its Halpha. One component per layer, summed
        # over lines, with each line's transmission in the header.
        hii_lines = [n.removesuffix("_surface_brightness_hii") for n in RENDER_LINES_HII if n in f]
        if hii_lines and "halpha_hii" in about:
            shares = {n: _spectra.line_response(curves, _spectra.LINE_WAVELENGTHS[n]) for n in hii_lines}
            summed = sum(np.asarray(f[f"{n}_surface_brightness_hii"], dtype=float)[:, None] * shares[n] for n in hii_lines)
            components.append(("lines_hii", summed[:, None, :] * placed[..., None]))
            layers["lines_hii"] = layers["halpha_hii"]
            about["lines_hii"] = {
                "unit": "Lsun/pc2", "fields": [f"{n}_surface_brightness_hii" for n in hii_lines] + about["halpha_hii"]["fields"][1:],
                "layer": "lines_hii",
                "lines": {n: {"wavelength": _spectra.LINE_WAVELENGTHS[n], "transmission": shares[n].tolist()} for n in hii_lines},
                "about": "the HII regions' other lines - Hbeta by Case B, the forbidden lines off Byler et al. 2017's grid "
                         "at the regions' own metallicity, age and log U - each through each curve at its wavelength, "
                         "summed, placed and layered as the regions' Halpha is",
            }
        if "halpha_surface_brightness_dig" in f and "dig_scale_height" in f:
            dig = np.asarray(f["halpha_surface_brightness_dig"], dtype=float)
            components.append(("halpha_dig", dig[:, None] * halpha_share))
            layers["halpha_dig"] = float(f["dig_scale_height"])
            about["halpha_dig"] = {
                **line_about, "fields": ["halpha_surface_brightness_dig", "dig_scale_height"], "layer": "halpha_dig",
                "about": "the diffuse ionized gas's Halpha through each curve, axisymmetric as published, in its own "
                         "published layer: seen edge-on it is a thick glow that brightens toward the limb",
            }
            if "hbeta_surface_brightness_dig" in f:
                hbeta_share = _spectra.line_response(curves, _spectra.LINE_WAVELENGTHS["hbeta"])
                components.append(("lines_dig", np.asarray(f["hbeta_surface_brightness_dig"], dtype=float)[:, None] * hbeta_share))
                layers["lines_dig"] = layers["halpha_dig"]
                about["lines_dig"] = {
                    "unit": "Lsun/pc2", "fields": ["hbeta_surface_brightness_dig", "dig_scale_height"], "layer": "lines_dig",
                    "lines": {"hbeta": {"wavelength": _spectra.LINE_WAVELENGTHS["hbeta"], "transmission": hbeta_share.tolist()}},
                    "about": "the diffuse gas's Hbeta through each curve, in the Halpha's layer; the diffuse gas carries no "
                             "forbidden line (the grid does not model its field)",
                }
        if "dust_extinction_v" in f:
            a_v = np.asarray(f["dust_extinction_v"], dtype=float)
            refs = _spectra.filter_references(curves)
            components.append(("dust_extinction", _spectra.extinction_transmission(a_v, curves)))
            about["dust_extinction"] = {
                "unit": "dimensionless", "fields": ["dust_extinction_v"], "layer": "dust",
                "reference_wavelength": refs.tolist(),
                "extinction_ratio": _spectra.extinction_ratio(refs).tolist(),
                "albedo": _spectra.albedo(refs).tolist(),
                "about": "the share of each filter's light a face-on column of the dust lets through, 10^(-0.4 A_V r), "
                         "r = A_lambda/A_V the grain model's extinction cross-section at the filter's reference "
                         "wavelength over its V row's (Draine's R_V = 3.1 table, the dust stage's). Occlusion, never a "
                         "colour: the viewer takes its optical depth, -ln of this, through the dust's layer",
            }
        if all(n in f for n in ("dust_extinction_v", "dust_scattering_optical_depth", "dust_scattering_asymmetry")):
            tau_sca = _spectra.scattering_depth(f["dust_scattering_optical_depth"], curves)  # (R, filter)
            tau_ext = _spectra.extinction_depth(f["dust_extinction_v"], curves)
            g = float(f["dust_scattering_asymmetry"])
            components.append(("dust_scattered", _spectra.scattered_share(tau_ext, tau_sca)[:, None, :] * stars))
            about["dust_scattered"] = {
                "unit": "Lsun/pc2", "fields": ["dust_scattering_optical_depth", "dust_extinction_v", "dust_scattering_asymmetry",
                                               *RENDER_STARS, *contrast_fields],
                "layer": "dust", "phase": _spectra.phase_table(g),
                "about": "starlight the dust scatters, all directions together: the published V-band scattering depth, "
                         "moved to each filter by the grain model's scattering cross-section, and the share of the "
                         "stellar component a mixed slab of that depth scatters as the dust stage counts it (what the "
                         "extinction removes less what the absorption keeps). The phase table's factor, a "
                         "Henyey-Greenstein phase function at the published g averaged over light arriving in the "
                         "disc's plane, turns it into what a view at |cos i| receives; it averages to 1 over every view",
            }
        if "dust_infrared_surface_brightness" in f and "dust_temperature" in f:
            dc = {k: float(model.constants[k].value) for k in RENDER_DUST_CONSTANTS}
            thermal = _spectra.thermal_response(
                f["dust_infrared_surface_brightness"], f["dust_temperature"], curves,
                dc["DUST_OPACITY_REFERENCE"], dc["DUST_OPACITY_WAVELENGTH"], dc["DUST_EMISSIVITY_INDEX"],
            )
            components.append(("dust_thermal", thermal))
            about["dust_thermal"] = {
                "unit": "Lsun/pc2", "fields": ["dust_infrared_surface_brightness", "dust_temperature"], "layer": "dust",
                "about": "the dust's own emission through each curve: the published infrared surface brightness as the "
                         "dust stage's modified blackbody at the published temperature and its emissivity index, "
                         "optically thin. Zero through an optical filter; a curve holding the far infrared gets it all",
            }
        drawn = {"halpha"} if ("halpha_hii" in about or "halpha_dig" in about) else set()
        for name in ("lines_hii", "lines_dig"):
            drawn |= set(about.get(name, {}).get("lines", {}))
        absent = [n for n in _spectra.LINE_WAVELENGTHS if n not in drawn]

        # Per ring (R, filter) or placed around it (R, phi, filter).
        per_ring_names = {"halpha_dig", "lines_dig", "dust_extinction", "dust_thermal"}
        arrays: list[tuple[str, np.ndarray]] = []
        if level is None:
            r_min = q.number("r_min", R_axis.lo)
            r_max = q.number("r_max", R_axis.hi)
            phi_min = q.number("phi_min", 0.0)
            phi_max = q.number("phi_max", 2.0 * math.pi)
            i0, n_r = _span(R_axis.lo, R_axis.width, R_axis.n, r_min, r_max, wrap=False)
            j0, n_phi = _span(phi_axis.lo, phi_axis.width, phi_axis.n, phi_min, phi_max, wrap=True)
            rows = np.arange(i0, i0 + n_r)
            cols = (j0 + np.arange(n_phi)) % phi_axis.n
            for name, value in components:
                arrays.append((name, value[rows] if name in per_ring_names else value[rows][:, cols]))
            window: dict[str, Any] = {
                "R": {"first": i0, "n": n_r, "lo": R_axis.lo + i0 * R_axis.width, "width": R_axis.width},
                "phi": {"first": j0, "n": n_phi, "lo": phi_axis.lo + j0 * phi_axis.width, "width": phi_axis.width,
                        "wraps": bool(j0 + n_phi > phi_axis.n)},
            }
            axes = {name: ["R", "filter"] if name in per_ring_names else ["R", "phi", "filter"] for name, _ in components}
        else:
            r_min = q.number("r_min", float(R[0]))
            r_max = q.number("r_max", float(R[-1]))
            phi_min = q.number("phi_min", 0.0)
            phi_max = q.number("phi_max", 2.0 * math.pi)
            cells = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level)
            if level and len(cells) > MAX_CHILD_CELLS:
                raise BadRequest(f"level={level} over this window names {len(cells)} cells, more than {MAX_CHILD_CELLS}: narrow the window")
            bounds = [_catalogue.cell_bounds(R, c, level) for c in cells]
            arrays.append(("cell", np.asarray(cells, dtype=np.int64)))
            for name, value in components:
                arrays.append((name, _cell_means(value, bounds, R_axis, phi_axis, per_ring=name in per_ring_names)))
            window = {"cells": {"count": len(cells), "of": _catalogue.CELL_COUNT * _catalogue.children_per_cell(level),
                                "bounds": bounds if len(cells) <= 64 else []}}
            axes = {"cell": ["cell"], **{name: ["cell", "filter"] for name, _ in components}}
        if precision == "f4":
            arrays = [(n, a.astype(np.float32) if a.dtype == np.float64 else a) for n, a in arrays]

        bulge = None
        if all(n in f for n in RENDER_BULGE):
            points = np.array([float(f[f"bulge_sed_{b.lower()}"]) for b in _spectra.SED_BANDS])
            bulge = [_number(v) for v in _spectra.stellar_response(points, np.array(float(f["bulge_light_temperature"])), curves)]
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "set": q.one("set"),
            "filters": [c.json() for c in curves],
            "level": level,
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            "window": window,
            "axes": axes,
            "components": about,
            "layers": layers,
            # The unresolved bulge is a scalar luminosity at a scalar colour temperature: its response per filter, Lsun.
            "bulge": bulge,
            "white": white,
            "absent": {"lines": absent, "why": "not published by this model; and the diffuse ionized gas carries only its "
                                                "recombination lines (S42: the grid gives the HII regions' forbidden lines)"},
            "stages": list(ran),
        }
        if resolved is not None:
            header["resolved"] = resolved
        return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)

    def _unresolved(
        self, model: Model, f: Mapping[str, Any], R: np.ndarray, curves: Sequence[Any], per_ring: np.ndarray,
        contrast: Any, l_min: float,
    ) -> tuple[np.ndarray, dict[str, Any], dict[str, Any]]:
        """The field's remainder under ``l_min`` (S48's wiring, D200 (4)): (the component on the (R, phi) grid, its
        entry in ``components``, the header's ``resolved``).

        The disc's light less the young population (ages under the cluster census's window, which the cluster
        points carry) and less the disc stars above ``l_min`` older than it (which ``/api/bright`` carries), all
        three from ``bright.resolve``: one decomposition of the history onto the isochrones, the luminosity
        function renormalised to the field's tables, so unresolved + young + bright is the field's total per ring
        and band exactly. Each of the remainder's two age parts goes through the curves on its own and is placed
        around the ring by the weight the bright catalogue gives the same part (``bright.part_weights``: the
        contrast for the old part, the normalised sfr_modulation for the 20-100 Myr part where the model publishes
        it), so the points and the field agree around the arms. The SED join is not linear, so the parts' responses
        do not sum to the total's exactly: the departure through this request's curves is measured here, per ring,
        and stated in the header."""
        spec = self.grid.spec
        constants = {k: c.value for k, c in model.constants.items()}
        res = _bright.resolve(f, float(spec.t_max), int(spec.n_t), constants, l_min)
        T = f["disc_light_temperature"]
        a = res.anchors
        middle = _spectra.stellar_response(a["unresolved_middle"], T, curves)
        old = _spectra.stellar_response(a["unresolved_old"], T, curves)
        modulation = f["sfr_modulation"] if "sfr_modulation" in f else None
        grid_contrast = np.ones((R.size, self.grid.axes["phi"].n)) if contrast is None else contrast
        weights = _bright.part_weights(grid_contrast, modulation)  # (2, R, phi): middle, old
        component = middle[:, None, :] * weights[0][..., None] + old[:, None, :] * weights[1][..., None]
        # The closure through these curves: every part through the field's machinery at the ring's temperature.
        parts = middle + old + _spectra.stellar_response(a["young"], T, curves) + _spectra.stellar_response(
            a["bright_middle"] + a["bright_old"], T, curves)
        lit = per_ring > 0.0
        departure = float(np.max(np.abs(parts[lit] / per_ring[lit] - 1.0))) if lit.any() else 0.0
        area = 2.0 * math.pi * R * PC_PER_KPC**2  # pc² per kpc of radius, as disc_luminosity integrates
        light = {k: float(np.trapezoid(v * area, R)) for k, v in res.light.items()}
        fields = [*RENDER_STARS, *(["pattern_density_contrast"] if contrast is not None else []),
                  *(n for n in _bright.RESOLVE_READS if n in f)]
        entry = {
            "unit": "Lsun/pc2", "fields": fields, "layer": "stars",
            "about": "the disc's starlight no point carries: the stars component's light less the stars younger than "
                     "the cluster census's window (the cluster points carry them) and less the disc stars above l_min "
                     "older than it (the bright catalogue's, /api/bright with the same l_min), from one decomposition "
                     "of the history onto the isochrones and the luminosity function renormalised to the field's "
                     "tables; its 20-100 Myr part placed around each ring by where stars form today (sfr_modulation, "
                     "where the model publishes it) and the older part by the pattern's contrast, as the bright "
                     "catalogue places its stars; through each curve as the stars component is, at the ring's colour "
                     "temperature",
        }
        resolved = {
            "l_min": 10.0**res.log_l,
            "requested": l_min,
            "cluster_window_gyr": _bright.cluster_window(constants),
            # Bolometric, whole disc, Lsun: the trapezoid in R disc_luminosity is. bright is the field's budget above
            # l_min (what the remainder is cut by); bright_own what the catalogue's stars carry themselves - they differ
            # by how well the field's mass grid resolves the giant branch (D202, debt #126).
            "light": light,
            "closure": {
                "anchors": "exact",
                "response": departure,
                "about": "anchors: unresolved + young + bright is the stars' eight band sums per ring and band, one "
                         "decomposition (tests/test_render.py: 1e-13). response: the largest relative departure, over "
                         "rings and these curves, of the four parts' responses summed (each through the field's "
                         "machinery at the ring's temperature) from the stars component's - the join is not linear",
            },
            "temperature": "the remainder is put through the curves at the ring's colour temperature "
                           "(disc_light_temperature), not its own [inferred]: the luminosity function carries no colour, "
                           "so the remainder's own correlated temperature is not computed here. Measured at S48 against "
                           "the remainder's own (its stars' colour integrated along the isochrones): within 7.5e-5 of the "
                           "response through rgb at every ring, within 1.5% through the narrowband and WFC3 sets (the "
                           "20-100 Myr part, which is hotter; the older part within 0.5%); the temperature shapes only "
                           "the blackbody tails beyond U and K and, through them, the band-consistent anchors",
        }
        return component, entry, resolved

    def _system(self, q: Query) -> Response:
        """One star's planets. It materialises one cell and takes one star out of it.

        The whole point of naming a star ``(cell, index)`` is that this costs a
        cell rather than a galaxy: the catalogue stage is not run, the planets
        stage is not run, and what does run is the closure of what the catalogue
        *reads* — the same six stages a region query needs (rule D4).
        """
        model = self._model(q)
        catalogue = _stage_for(model, CATALOGUE_SLOT, self.impls)
        planets = _stage_for(model, PLANETS_SLOT, self.impls)
        level = _level(q)
        cell = q.integer("cell", -1)
        index = q.integer("index", -1)
        n_cells = _catalogue.CELL_COUNT * _catalogue.children_per_cell(level)
        if not 0 <= cell < n_cells:
            raise BadRequest(f"cell={cell} is outside 0..{n_cells - 1} at level {level}")
        if index < 0:
            raise BadRequest(f"index={index} is not a star of that cell")
        stars = q.integer("stars", _catalogue.CATALOGUE_SAMPLE)
        if not 1 <= stars <= MAX_STARS:
            raise BadRequest(f"stars={stars} is outside 1..{MAX_STARS}")

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, self._reads(model, catalogue))
        seeds = {name: int(out.inputs[name]) for name in catalogue.reads_seeds + planets.reads_seeds}
        here = _catalogue.materialise(
            out.fields, self.grid.R, self.grid.t, seeds["systems_seed"], stars, cells=[cell],
            migration=float(out.inputs["migration_efficiency"]), level=level,
        )
        if level:
            # A level-k name addresses the child's own stars: its inherited rows are opened by their
            # parent's level-0 name, so the same star has the same planets by either route (S32).
            own = np.asarray(here["level"]) == level
            here = _catalogue.Catalogue.of({n: np.asarray(v)[own] for n, v in here.items() if n not in ("level", "cell", "index")}, ((cell, int(own.sum())),))
        if index >= here.size:
            raise NotFound(f"cell {cell} has {here.size} stars of its own at this sample size and level, so no index {index}")

        constants = {k: c.value for k, c in model.constants.items()}
        system, found = _planets.one_system(here, index, _catalogue.canonical_cell(level, cell), seeds["planets_seed"], constants)
        columns = [d.name for d in planets.publishes if d.of == "planet" and d.name in system]
        star = {d.name: _number(here[d.name][index]) for d in catalogue.publishes if d.of == "star" and d.name in here}
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "star": star,
            "level": level,
            "cell": cell,
            "index": index,
            "of": here.size,
            "bounds": _catalogue.cell_bounds(self.grid.R, cell, level),
            "planets": len(system[columns[0]]) if columns else 0,
            "belts": [dict(b) for b in found],
            "columns": columns,
            "stars": {"requested": stars, "seed": seeds["systems_seed"], "planets_seed": seeds["planets_seed"]},
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, system[c]) for c in columns]), ran)




def _named(census: Any) -> Any:
    """The census with each row's name as two int64 columns, ``cell`` and ``index``: the level-0 cell it was
    drawn in and its place among that cell's rows - the path it was drawn on (D60), which a renderer seeds a
    cloud's interior by (RENDER_PHYSICS 5a). Taken before any level filter, so a kept row keeps its name (S40)."""
    cells = np.repeat(np.asarray([c for c, _ in census.counts], dtype=np.int64), [n for _, n in census.counts])
    index = np.concatenate([np.arange(n, dtype=np.int64) for _, n in census.counts]) if census.counts else np.zeros(0, dtype=np.int64)
    return _catalogue.Catalogue.of({**census, "cell": cells, "index": index}, census.counts)


def _in_children(census: Any, prefix: str, R: np.ndarray, children: Sequence[int], level: int) -> tuple[Any, int]:
    """A census's rows inside the level-``level`` ``children`` asked for, by each row's own position
    (``<prefix>_radius``, ``<prefix>_azimuth``) within its level-0 cell. The counts are recomputed from the rows
    kept, so the header's cells describe the body (until S40 they stayed the unfiltered cells')."""
    wanted = set(children)
    keep = np.zeros(census.size, dtype=bool)
    offset = 0
    counts: list[tuple[int, int]] = []
    for cell, count in census.counts:
        r = np.asarray(census[f"{prefix}_radius"])[offset:offset + count]
        phi = np.asarray(census[f"{prefix}_azimuth"])[offset:offset + count]
        for qq in range(_catalogue.children_per_cell(level)):
            cid = _catalogue.child_id(cell, level, qq)
            if cid in wanted:
                keep[offset:offset + count] |= _catalogue._within(r, phi, {}, R, cell, level, qq)
        kept_here = int(keep[offset:offset + count].sum())
        if kept_here:
            counts.append((int(cell), kept_here))
        offset += count
    return _catalogue.Catalogue.of({n: np.asarray(v)[keep] for n, v in census.items()}, counts), int(keep.sum())


def _span(lo: float, width: float, n: int, a: float, b: float, *, wrap: bool) -> tuple[int, int]:
    """The run of grid cells ``(first, count)`` whose extent meets ``[a, b]`` on an axis of ``n`` cells of
    ``width`` from ``lo``. A window narrower than a cell still selects the cell containing it; a wrapping axis
    (phi) takes the run from the cell holding ``a`` round past its end, at most once round."""
    if b < a and not wrap:
        a, b = b, a
    if wrap:
        span = min(max(b - a, 0.0), n * width)
        start = (a - lo) % (n * width)
        first = min(int(math.floor(start / width)), n - 1)
        last = int(math.ceil((start + span) / width - 1e-9))
        return first, int(min(max(last - first, 1), n))
    first = int(min(max(math.floor((a - lo) / width), 0), n - 1))
    last = int(min(max(math.ceil((b - lo) / width - 1e-9), first + 1), n))
    return first, last - first


def _cell_means(value: np.ndarray, bounds: Sequence[Mapping[str, float]], R_axis: Any, phi_axis: Any, *, per_ring: bool) -> np.ndarray:
    """Each region cell's area-weighted mean of a grid quantity: the grid's values, bilinear in (R, phi) and
    periodic in phi (linear in R for a per-ring one), at RENDER_CELL_SAMPLES² midpoints of the cell."""
    k = RENDER_CELL_SAMPLES
    edges = np.array([[b["r_lo"], b["r_hi"], b["phi_lo"], b["phi_hi"]] for b in bounds], dtype=float).reshape(-1, 4)
    u = (np.arange(k) + 0.5) / k
    r = edges[:, 0, None, None] + (edges[:, 1] - edges[:, 0])[:, None, None] * u[:, None]  # (n, k, 1)
    p = edges[:, 2, None, None] + (edges[:, 3] - edges[:, 2])[:, None, None] * u[None, :]  # (n, 1, k)
    r, p = np.broadcast_arrays(r, p)
    x = np.clip((r - R_axis.lo) / R_axis.width - 0.5, 0.0, R_axis.n - 1.0)
    i0 = np.minimum(np.floor(x).astype(int), R_axis.n - 2)
    fx = x - i0
    weight = r / r.sum(axis=(1, 2), keepdims=True)
    if per_ring:
        at = value[i0] * (1.0 - fx if value.ndim == 1 else (1.0 - fx)[..., None]) + value[i0 + 1] * (fx if value.ndim == 1 else fx[..., None])
    else:
        y = (p - phi_axis.lo) / phi_axis.width - 0.5
        j0 = np.floor(y).astype(int)
        fy = (y - j0)[..., None]
        j0 %= phi_axis.n
        j1 = (j0 + 1) % phi_axis.n
        fxe = fx[..., None]
        at = ((1.0 - fxe) * ((1.0 - fy) * value[i0, j0] + fy * value[i0, j1])
              + fxe * ((1.0 - fy) * value[i0 + 1, j0] + fy * value[i0 + 1, j1]))
    w = weight if at.ndim == 3 else weight[..., None]
    return (at * w).sum(axis=(1, 2))


def _level(q: Query) -> int:
    level = q.integer("level", 0)
    if not 0 <= level <= _catalogue.MAX_LEVEL:
        raise BadRequest(f"level={level} is outside 0..{_catalogue.MAX_LEVEL}")
    return level


def _view_matrix(raw: str | None) -> np.ndarray | None:
    """``view=`` as a 4×4 view-projection matrix, given column-major as three.js writes one."""
    if raw is None:
        return None
    try:
        values = [float(v) for v in raw.split(",")]
    except ValueError:
        raise BadRequest("view= must be 16 comma-separated numbers") from None
    if len(values) != 16 or not all(math.isfinite(v) for v in values):
        raise BadRequest("view= must be 16 finite numbers")
    return np.asarray(values, dtype=float).reshape(4, 4).T


def _brightest(catalogue: Any, n: int, view: np.ndarray | None) -> tuple[Any, dict[str, int]]:
    """The ``n`` most luminous stars of a catalogue, inside ``view``'s frustum when one is given.

    A magnitude-limited catalogue of what the camera sees, in the sense a survey means it: the
    brightest of the *sample*, not of the galaxy, so what ``n`` reaches into the luminosity function
    is ``n`` over the pool, which the header states. Rows come back brightest first, each named by
    its own ``cell`` and ``index`` (the runs no longer name a selection), and stars with no light
    (M2's dead ones, NaN) rank last and never make the cut.
    """
    keep = np.arange(catalogue.size)
    if view is not None and keep.size:
        # The viewer's frame (frontend/src/galaxy/positions.ts): y up, phi from +x towards -z; one test,
        # shared with /api/bright (S48).
        keep = keep[_bright.in_frustum(view, catalogue["star_radius"], catalogue["star_azimuth"], catalogue["star_height"])]
    in_view = int(keep.size)
    lum = np.nan_to_num(np.asarray(catalogue["star_luminosity"], dtype=float)[keep], nan=-np.inf)
    lit = keep[lum > -np.inf]
    lum = lum[lum > -np.inf]
    if lit.size > n:
        top = np.argpartition(-lum, n - 1)[:n]
        lit, lum = lit[top], lum[top]
    order = np.argsort(-lum, kind="stable")
    keep = lit[order]

    cells = np.concatenate([np.full(count, cell, dtype=np.int64) for cell, count in catalogue.counts] or [np.zeros(0, np.int64)])
    indices = np.concatenate([np.arange(count, dtype=np.int64) for _, count in catalogue.counts] or [np.zeros(0, np.int64)])
    chosen = _catalogue.Catalogue.of({name: np.asarray(column)[keep] for name, column in catalogue.items()})
    chosen["cell"] = cells[keep]
    chosen["index"] = indices[keep]
    return chosen, {"requested": n, "pool": int(catalogue.size), "in_view": in_view, "returned": int(keep.size)}


def _stage_for(model: Model, slot: str, impls: Any) -> Stage:
    stage_id = model.stage_map.get(slot)
    if stage_id is None or stage_id not in impls:
        raise NotFound(f"model {model.name!r} has no {slot} stage")
    return impls.get(stage_id) if isinstance(impls, Registry) else impls[stage_id]


def _inputs_json(inputs: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, value in inputs.items():
        if isinstance(value, tuple) and value and isinstance(value[0], MergerEvent):
            out[name] = [_event_json(e) for e in value]
        elif isinstance(value, tuple):
            out[name] = list(value)
        else:
            out[name] = _number(value)
    return out


def _events(name: str, raw: str) -> tuple[MergerEvent, ...]:
    """An event list arrives as JSON, because it is a list of records, not a scalar."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise BadRequest(f"{name} must be a JSON array of events: {e}") from None
    if not isinstance(parsed, list):
        raise BadRequest(f"{name} must be a JSON array of events, got {type(parsed).__name__}")
    events: list[MergerEvent] = []
    for entry in parsed:
        if not isinstance(entry, Mapping):
            raise BadRequest(f"{name}: each event is an object with time, mass_ratio, gas_fraction")
        unknown = set(entry) - {"time", "mass_ratio", "gas_fraction", "about"}
        if unknown:
            raise BadRequest(f"{name}: unknown event keys {sorted(unknown)}")
        try:
            events.append(
                MergerEvent(
                    float(entry["time"]), float(entry["mass_ratio"]), float(entry["gas_fraction"]),
                    str(entry.get("about", "")),
                )
            )
        except KeyError as e:
            raise BadRequest(f"{name}: an event is missing {e}") from None
        except (TypeError, ValueError) as e:
            raise BadRequest(f"{name}: {e}") from None
    return tuple(events)


# A reserved parameter that is also an input name would make the input
# unreachable, and the collision would be discovered by a control that silently
# stopped working. Refused at import instead (rule B13).
_clash = RESERVED & set(production()[2])
if _clash:  # pragma: no cover - a registry edit is what would trigger this
    raise RuntimeError(f"reserved query parameters collide with input names: {sorted(_clash)}")
