"""Template bundles (S72, BUILD_IV Phase W2): answers computed once, served from files, under the model's hash.

A bundle is a directory of answers the model gave, each stored as the bytes it sent, beside a manifest that names
the request each answers and the content hash of the model that computed them::

    <bundles>/<template>/<layer>/manifest.json
    <bundles>/<template>/<layer>/entries/<key>        the body, no extension

**The key is the request's meaning** (:func:`request`, the lead's ruling R2 at S72), read with the service's own
parsers so that spelling and order never matter: the route; the model and the template it resolves to; the layer's
setting; the input overrides the service would compute with (``Service._overrides``: the template's, then the
query's, controls as floats, seeds as ints, events parsed); and every other parameter as its raw string - ``filters``
re-serialised canonically (sorted keys, no spaces), since it is parsed as JSON - because the body echoes those as given
(a window's r_min, a remainder's l_min). A request the service would refuse has no key and is computed, which answers
it with the service's own error. Nothing is defaulted: a window spelled otherwise, or absent, is another request.

**The hash is the guard** (rule D3, restated at the boundary: *every cache between the model and the viewer is keyed
on that hash*). A manifest names the hash of ``model/galaxy`` it was built from (``version.MODEL``); the service
refuses, at construction, a bundle whose hash is not its own - :class:`BundleMismatch`, naming both. "A mismatch is
an error, not a fallback" (BUILD_IV section 2b): a stale bundle served beside new code is the defect rule D3 exists to
make visible, and falling through to the model would hide that the deployment is wrong.

A hit runs nothing (rule D4): the service answers it before any handler, so no stage runs, no galaxy is cached and
the response's ``stages`` is empty; its ``source`` says ``bundle``. The body is the computation's byte for byte only
because a body is a function of the request alone: its header's ``stages`` is the closure the answer needs, not what
this server happened to run (S72, R3). This module holds the format's one definition: the writer
(``tools/export_template.py``) and the reader (``Service(bundles=...)``) both go through it (rule B13).
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

FORMAT = "galaxy-bundle/1"
MANIFEST = "manifest.json"
ENTRIES = "entries"
LAYERS = ("on", "off")
# Routes a bundle never answers: /api/version is the check itself (it must say what is on disk now, B2), and the
# index is the route table (BUILD_IV W2 as the lead fixed it at S72).
NEVER = frozenset({"/api/version", "/api"})
# The names the key resolves rather than reads raw, on a route that takes inputs.
RESOLVED = ("model", "template", "layer")

Query = str | Mapping[str, Any] | Sequence[tuple[str, Any]] | None


class BundleError(Exception):
    """A bundle directory that cannot be read as one: a missing file, a size that is not the manifest's, a format."""


class BundleMismatch(BundleError):
    """A bundle built from another model than the one serving it (D3): never read, never a fallback."""


def _route(path: str) -> str:
    return path.rstrip("/") or "/"


def pairs(query: Query) -> list[tuple[str, str]]:
    """The (name, value) pairs of a query in every form ``Service.handle`` takes, decoded as ``Query`` decodes them
    (``Query`` calls this: one decoding for the routes and for the keys)."""
    if query is None:
        return []
    if isinstance(query, str):
        return list(parse_qsl(query.lstrip("?"), keep_blank_values=True))
    if isinstance(query, Mapping):
        return [(k, str(v)) for k, vs in query.items() for v in (vs if not isinstance(vs, str) else [vs])]
    return [(str(k), str(v)) for k, v in query]


def _filters(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except ValueError:
        return raw
    return json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def request(service: Any, route: str, query: Query) -> dict[str, Any] | None:
    """What a request asks, as the service reads it; None for a request the service would refuse (or no route)."""
    from galaxy.api import service as _service  # the service imports this module; the reverse waits until called
    from galaxy.run import RunError

    path = _route(route)
    declared = next((r for r in _service.ROUTES if r.path == path), None)
    if declared is None or path in NEVER or not path.startswith("/api"):
        return None
    q = _service.Query(query)
    takes_inputs = "layer" in declared.params  # every route that takes inputs takes the layer's switch
    out: dict[str, Any] = {"route": path, "model": None, "template": None, "layer": None, "inputs": None}
    try:
        if "model" in declared.params:
            model = service._model(q)
            out["model"] = model.name
        if takes_inputs:
            template = service._template(q)
            out["template"] = None if template is None else template.name
            out["layer"] = service._layer(q)
            out["inputs"] = _service._inputs_json(service._overrides(model, q))
    except (_service.ApiError, RunError, ValueError, TypeError):
        return None
    params: dict[str, list[str]] = {}
    for name, value in q.pairs():
        if name == "model" and "model" in declared.params:
            continue
        if takes_inputs and (name in RESOLVED or name not in _service.RESERVED):
            continue  # resolved above, or an input (validated by _overrides and held in "inputs")
        params.setdefault(name, []).append(_filters(value) if name == "filters" else value)
    out["params"] = params
    return out


def key(service: Any, route: str, query: Query) -> str | None:
    """The entry's file name: sha256 of :func:`request` as sorted JSON, hex; None where the request has no key."""
    asked = request(service, route, query)
    if asked is None:
        return None
    text = json.dumps(asked, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


# --- the viewer's spelling (what the browser sends; the export plans entries in it) --------------------------------

def js_number(x: float | int) -> str:
    """ECMAScript Number::toString: the shortest digits that round-trip (as Python's repr), laid out as a browser
    lays them out - 7 not 7.0, 1100000000000 not 1100000000000.0, 1e-7 not 1e-07, exponents from 1e21 and below 1e-6."""
    if isinstance(x, bool):
        return "true" if x else "false"
    v = float(x)
    if not math.isfinite(v):
        return "NaN" if math.isnan(v) else ("Infinity" if v > 0 else "-Infinity")
    if v == 0:
        return "0"
    if v < 0:
        return "-" + js_number(-v)
    mantissa, _, exp = repr(v).partition("e")
    whole, _, frac = mantissa.partition(".")
    written = whole + frac
    lead = len(written) - len(written.lstrip("0"))
    n = len(whole) + (int(exp) if exp else 0) - lead  # the decimal point's place after the first significant digit
    digits = written.lstrip("0").rstrip("0")
    k = len(digits)
    if k <= n <= 21:
        return digits + "0" * (n - k)
    if 0 < n <= 21:
        return digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return "0." + "0" * (-n) + digits
    e = n - 1
    return digits[0] + ("." + digits[1:] if k > 1 else "") + "e" + ("+" if e >= 0 else "-") + str(abs(e))


def js_json(value: Any) -> str:
    """JSON.stringify(value) for JSON-shaped data: keys in their order, no spaces, numbers by :func:`js_number`."""
    if value is None:
        return "null"
    if isinstance(value, (bool, int, float)):
        return js_number(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, Mapping):
        return "{" + ",".join(json.dumps(str(k), ensure_ascii=False) + ":" + js_json(v) for k, v in value.items()) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(js_json(v) for v in value) + "]"
    raise TypeError(f"{type(value).__name__} is not JSON-shaped")


def js_value(value: Any) -> str:
    """What URLSearchParams.set(key, String(value)) sends for one value (arrays joined by commas, as transport.js)."""
    if isinstance(value, (list, tuple)):
        return ",".join(js_value(v) for v in value)
    if isinstance(value, (bool, int, float)):
        return js_number(value)
    return str(value)


_FORM_SAFE = frozenset(b"*-._0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def _form(text: str) -> str:
    return "".join(chr(b) if b in _FORM_SAFE else "+" if b == 0x20 else f"%{b:02X}" for b in text.encode("utf-8"))


def js_query(params: Mapping[str, Any] | Sequence[tuple[str, Any]]) -> str:
    """URLSearchParams.toString(): the application/x-www-form-urlencoded serialisation a browser sends - '*-._' and
    alphanumerics as they are, a space as '+', every other byte of the UTF-8 as %XX (so '~' is %7E, as no Python
    quoting writes it)."""
    items = params.items() if isinstance(params, Mapping) else params
    return "&".join(_form(str(k)) + "=" + _form(js_value(v)) for k, v in items)


# --- the format: the writer and the reader ------------------------------------------------------------------------

def served(service: Any) -> dict[str, Any]:
    """What else a bundle's answers depend on besides the model's bytes (the lead's Q3 at S72): the grid the service
    computes on, as ``Service.compute`` keys a galaxy on it, and the models it registers."""
    return {"grid": repr(service.grid.spec), "models": list(service.models.names())}


def directory(root: Path, template: str, layer: str) -> Path:
    if layer not in LAYERS:
        raise ValueError(f"layer {layer!r} is not one of {LAYERS}")
    return Path(root) / template / layer


def write(root: Path, template: str, layer: str, service: Any,
          answers: Iterable[tuple[str, Any, Any]]) -> dict[str, Any]:
    """Write one bundle: each ``(route, query, response)`` - a 200 :class:`~galaxy.api.service.Response` - as its body
    under its key, then the manifest (sorted keys, indent 1, LF). The manifest's ``query`` is the request as sent: a
    string as given, a mapping as a browser serialises it (:func:`js_query`). Refuses a response that is not a 200,
    a request with no key, and two answers to one key with different bytes. Returns the manifest."""
    out = directory(root, template, layer)
    (out / ENTRIES).mkdir(parents=True, exist_ok=True)
    entries: dict[str, dict[str, Any]] = {}
    for route, query, response in answers:
        sent = query if isinstance(query, str) else js_query(query if query is not None else {})
        if response.status != 200:
            raise BundleError(f"{route}?{sent[:200]} answered {response.status}: a bundle holds only answers")
        k = key(service, route, query)
        if k is None:
            raise BundleError(f"{route}?{sent[:200]} has no key: the service would refuse it, or never bundles the route")
        if k in entries:
            if entries[k]["bytes"] != len(response.body):
                raise BundleError(f"{route}?{sent[:200]} was planned twice and answered differently")
            continue
        (out / ENTRIES / k).write_bytes(response.body)
        entries[k] = {
            "route": _route(route), "query": sent, "key": k, "bytes": len(response.body),
            "media": response.media, "stages": list(response.stages),
        }
    manifest = {
        "format": FORMAT, "model_hash": service.model_hash, **served(service), "template": template, "layer": layer,
        "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "entries": list(entries.values()),
    }
    (out / MANIFEST).write_bytes((json.dumps(manifest, sort_keys=True, indent=1) + "\n").encode("utf-8"))
    return manifest


def manifests(root: Path) -> list[Path]:
    """Every manifest under ``root``: ``<template>/<layer>/manifest.json``, or ``root``'s own for one bundle."""
    root = Path(root)
    if (root / MANIFEST).is_file():
        return [root / MANIFEST]
    return sorted(root.glob(f"*/*/{MANIFEST}"))


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BundleError(f"{path}: not a readable manifest ({e})") from None
    if manifest.get("format") != FORMAT:
        raise BundleError(f"{path}: format {manifest.get('format')!r}, this reader reads {FORMAT!r}")
    return manifest


class Index:
    """Every entry of every bundle under a root, by key, checked against the serving model's hash at construction.

    Bodies stay on disk and are read on each hit (tools/timings.py's "bundle: render hit" row measures the read of a
    9.4 MB render); the page cache holds what is read often, and a second copy in this process would be a cache of
    a cache."""

    __slots__ = ("root", "service", "bundles", "_entries")

    def __init__(self, root: Path, service: Any) -> None:
        self.root = Path(root)
        self.service = service
        self.bundles: list[dict[str, Any]] = []
        self._entries: dict[str, tuple[str, Path, int]] = {}
        if not self.root.is_dir():
            raise BundleError(f"bundles {self.root} is not a directory")
        live = service.model_hash
        for path in manifests(self.root):
            manifest = read_manifest(path)
            if manifest.get("model_hash") != live:
                raise BundleMismatch(
                    f"bundle {path.parent} was built from model {manifest.get('model_hash')} and this server's model "
                    f"is {live}: rebuild it with tools/export_template.py (a mismatch is an error, not a fallback)"
                )
            for name, value in served(service).items():  # the hash first, then what the same bytes may be run on
                if manifest.get(name) != value:
                    raise BundleMismatch(
                        f"bundle {path.parent} was built on {name} {manifest.get(name)!r} and this server's {name} is "
                        f"{value!r}: its answers are another service's (a mismatch is an error, not a fallback)"
                    )
            for e in manifest["entries"]:
                body = path.parent / ENTRIES / e["key"]
                try:
                    size = body.stat().st_size
                except OSError:
                    raise BundleError(f"bundle {path.parent}: entry {e['key']} ({e['route']}) is missing") from None
                if size != e["bytes"]:
                    raise BundleError(f"bundle {path.parent}: entry {e['key']} holds {size} B, the manifest says {e['bytes']}")
                held = self._entries.get(e["key"])
                if held is not None and held[2] != size:
                    raise BundleError(f"{e['route']} entry {e['key']} is in two bundles with different bytes")
                if held is None and _route(e["route"]) not in NEVER:
                    self._entries[e["key"]] = (e["media"], body, size)
            self.bundles.append({k: manifest[k] for k in ("template", "layer", "model_hash", "built_at")}
                                | {"entries": len(manifest["entries"]), "path": str(path.parent)})

    def __len__(self) -> int:
        return len(self._entries)

    def find(self, route: str, query: Query) -> tuple[str, bytes] | None:
        """``(media, body)`` for a request a bundle holds, else None. /api/version and the index are never held."""
        if not self._entries:
            return None
        k = key(self.service, route, query)
        held = None if k is None else self._entries.get(k)
        if held is None:
            return None
        media, body, _ = held
        return media, body.read_bytes()
