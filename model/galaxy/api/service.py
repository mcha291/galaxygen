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
from galaxy.stages import planets as _planets
from galaxy.stages import clouds as _clouds
from galaxy.stages import systems as _catalogue

JSON = "application/json"
CATALOGUE_SLOT = "systems"  # the slot a region query materialises from
PLANETS_SLOT = "planets"  # and the slot a system query materialises with
CLOUDS_SLOT = "clouds"  # the slot a clouds query materialises from (S32)
# The most child cells one level>0 region query may name (S32): 4096 is 64 level-0 cells at level 3,
# about a quarter of a ring's sectors two kiloparsecs deep; a wider window at that depth is refused.
MAX_CHILD_CELLS = 4096
# A guard, not a physical limit: this is a headless service and the LOD ladder
# that decides what a viewer should ask for arrives at S7 (GALAXY_PLAN.md §4).
MAX_STARS = 5_000_000
# The most stars a brightest=N query returns: a magnitude-limited view is a few thousand points,
# and a viewer that wants more than this wants the window itself.
MAX_BRIGHTEST = 200_000


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


def _json(payload: Mapping[str, Any], status: int = 200, stages: tuple[str, ...] = ()) -> Response:
    return Response(status, JSON, json.dumps(payload, allow_nan=False).encode("utf-8"), stages)


class CellCache:
    """Materialised cells, kept between requests.

    The catalogue draws every cell from its own seed, so a cell drawn alone is the cell drawn
    in any set and a window's catalogue is its cells' rows in cell order (D60). Materialising
    costs about 0.4 ms of Python per cell before a star is made, 832 cells to a galaxy, so a
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
        kept = None
        if level:
            children = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max, level=level)
            wanted = set(children)
            keep = np.zeros(census.size, dtype=bool)
            offset = 0
            for cell, count in census.counts:
                r = np.asarray(census["cloud_radius"])[offset:offset + count]
                phi = np.asarray(census["cloud_azimuth"])[offset:offset + count]
                for qq in range(_catalogue.children_per_cell(level)):
                    cid = _catalogue.child_id(cell, level, qq)
                    if cid in wanted:
                        keep[offset:offset + count] |= _catalogue._within(r, phi, {}, R, cell, level, qq)
                offset += count
            kept = int(keep.sum())
            census = _catalogue.Catalogue.of({n: np.asarray(v)[keep] for n, v in census.items()}, census.counts)
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
            },
            "columns": columns,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, census[c]) for c in columns]), ran)

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
        r = np.asarray(catalogue["star_radius"], dtype=float)
        phi = np.asarray(catalogue["star_azimuth"], dtype=float)
        # The viewer's frame (frontend/src/galaxy/positions.ts): y up, phi from +x towards -z.
        p = np.stack([r * np.cos(phi), np.asarray(catalogue["star_height"], dtype=float), -r * np.sin(phi), np.ones_like(r)])
        clip = view @ p
        w = clip[3]
        inside = (w > 0) & (np.abs(clip[0]) <= w) & (np.abs(clip[1]) <= w) & (np.abs(clip[2]) <= w)
        keep = keep[inside]
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
