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
from galaxy.stages import systems as _catalogue

JSON = "application/json"
CATALOGUE_SLOT = "systems"  # the slot a region query materialises from
# A guard, not a physical limit: this is a headless service and the LOD ladder
# that decides what a viewer should ask for arrives at S7 (GALAXY_PLAN.md §4).
MAX_STARS = 5_000_000


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
    Route("/api/arrays", "Named fields as binary arrays, plus the galaxy-level scalars.", ("model", "fields"), "arrays"),
    Route(
        "/api/region",
        "A materialised star catalogue for one (R, phi) window.",
        ("model", "r_min", "r_max", "phi_min", "phi_max", "stars"),
        "region",
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

        inputs = self._overrides(model, q)
        out, ran = self.compute(model, inputs, wanted)

        arrays: list[tuple[str, np.ndarray]] = []
        scalars: dict[str, Any] = {}
        for name in wanted:
            decl = declared[name][0]
            value = out.fields[name]
            if decl.kind.domain == "galaxy":
                scalars[name] = _number(value) if not decl.kind.categorical else value
            else:
                arrays.append((name, np.asarray(value)))
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "grid": grid_json(out.grid),
            "fields": list(wanted),
            "scalars": scalars,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, arrays), ran)

    def _region(self, q: Query) -> Response:
        model = self._model(q)
        stage_id = model.stage_map.get(CATALOGUE_SLOT)
        if stage_id is None or stage_id not in self.impls:
            raise NotFound(f"model {model.name!r} has no {CATALOGUE_SLOT} stage to materialise")
        stage = self.impls.get(stage_id) if isinstance(self.impls, Registry) else self.impls[stage_id]

        R, t = self.grid.R, self.grid.t
        r_min = q.number("r_min", float(R[0]))
        r_max = q.number("r_max", float(R[-1]))
        phi_min = q.number("phi_min", 0.0)
        phi_max = q.number("phi_max", 2.0 * math.pi)
        stars = q.integer("stars", _catalogue.CATALOGUE_SAMPLE)
        if not 1 <= stars <= MAX_STARS:
            raise BadRequest(f"stars={stars} is outside 1..{MAX_STARS}")

        inputs = self._overrides(model, q)
        # What the catalogue *reads*, which is not the catalogue: the closure
        # above these fields stops one stage short of materialising anything.
        out, ran = self.compute(model, inputs, stage.requires)
        seed_name = stage.reads_seeds[0] if stage.reads_seeds else None
        seed = int(out.inputs[seed_name]) if seed_name else 0

        cells = _catalogue.cells_in(R, r_min, r_max, phi_min, phi_max)
        catalogue = _catalogue.materialise(out.fields, R, t, seed, stars, cells)
        columns = [d.name for d in stage.publishes if d.kind.domain == "object" and d.name in catalogue]
        header = {
            "model": model.name,
            "inputs": _inputs_json(out.inputs),
            "region": {"r_min": r_min, "r_max": r_max, "phi_min": phi_min, "phi_max": phi_max},
            # The cells that actually realised a star, with how many each has: that
            # is what names a row. Star r of this response is index (r - offset) of
            # the cell whose run covers it, and a system is opened by that name
            # (D60, §12) rather than by a position, which can drift a ring (D69).
            "cells": {
                "ids": [c for c, _ in catalogue.counts],
                "counts": [n for _, n in catalogue.counts],
                "count": len(catalogue.counts),
                "requested": len(cells),
                "of": _catalogue.CELL_COUNT,
                "bounds": [_catalogue.cell_bounds(R, c) for c, _ in catalogue.counts]
                if len(catalogue.counts) <= 64
                else [],
            },
            "stars": {"requested": stars, "materialised": int(catalogue.size), "seed": seed},
            "columns": columns,
            "stages": list(ran),
        }
        return Response(200, wire.MEDIA, wire.encode(header, [(c, catalogue[c]) for c in columns]), ran)


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
