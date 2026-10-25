"""Template bundles (S72, BUILD_IV Phase W2): answers computed once, served from files, under the model's hash.

A bundle is a directory of answers the model gave, each stored as the bytes it sent, beside a manifest that names
the request each answers and the content hash of the model that computed them::

    <bundles>/<template>/<layer>/manifest.json
    <bundles>/<template>/<layer>/entries/<key>        the body, no extension

**The key is the request, canonically** (:func:`canonical`): the route, then the query's (name, value) pairs sorted by
name and value and url-encoded, after two normalisations and no others - ``layer`` absent is written ``layer=on`` on a
route that takes the switch (the service treats the two alike), and ``filters``, which is JSON, is re-serialised with
sorted keys and no spaces (a browser's ``JSON.stringify`` and Python's ``json.dumps`` space it differently). Nothing is
defaulted: ``model=``, ``template=`` and ``precision=`` are as the request gives them, so a request that would be
answered alike by the model but is spelled otherwise is a miss, and a miss is computed - never a wrong answer.

**The hash is the guard** (rule D3, restated at the boundary: *every cache between the model and the viewer is keyed
on that hash*). A manifest names the hash of ``model/galaxy`` it was built from (``version.MODEL``); the service
refuses, at construction, a bundle whose hash is not its own - :class:`BundleMismatch`, naming both. "A mismatch is
an error, not a fallback" (BUILD_IV section 2b): a stale bundle served beside new code is the defect rule D3 exists to
make visible, and falling through to the model would hide that the deployment is wrong.

A hit runs nothing (rule D4): the service answers it before any handler, so no stage runs, no galaxy is cached and
the response's ``stages`` is empty; its ``source`` says ``bundle``. This module holds the format's one definition:
the writer (``tools/export_template.py``) and the reader (``Service(bundles=...)``) both go through it (rule B13).
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode

FORMAT = "galaxy-bundle/1"
MANIFEST = "manifest.json"
ENTRIES = "entries"
LAYERS = ("on", "off")
# Routes a bundle never answers: /api/version is the check itself (it must say what is on disk now, B2), and the
# index is the route table (BUILD_IV W2 as the lead fixed it at S72).
NEVER = frozenset({"/api/version", "/api"})


class BundleError(Exception):
    """A bundle directory that cannot be read as one: a missing file, a size that is not the manifest's, a format."""


class BundleMismatch(BundleError):
    """A bundle built from another model than the one serving it (D3): never read, never a fallback."""


def _route(path: str) -> str:
    return path.rstrip("/") or "/"


def pairs(query: str | Mapping[str, Any] | Sequence[tuple[str, Any]] | None) -> list[tuple[str, str]]:
    """The (name, value) pairs of a query in every form ``Service.handle`` takes, decoded as ``Query`` decodes them."""
    if query is None:
        return []
    if isinstance(query, str):
        return list(parse_qsl(query.lstrip("?"), keep_blank_values=True))
    if isinstance(query, Mapping):
        return [(k, str(v)) for k, vs in query.items() for v in (vs if not isinstance(vs, str) else [vs])]
    return [(str(k), str(v)) for k, v in query]


def _layered(route: str) -> bool:
    from galaxy.api.service import ROUTES  # the route table; imported here, the service importing this module

    return any(r.path == route and "layer" in r.params for r in ROUTES)


def _filters(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except ValueError:
        return raw
    return json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical(route: str, query: str | Mapping[str, Any] | Sequence[tuple[str, Any]] | None) -> str:
    """``<route>?<pairs>``: the request a bundle entry is keyed on (see the module's docstring for the two
    normalisations). A query given twice by name keeps both pairs: the service refuses it, so no entry holds it."""
    path = _route(route)
    got = pairs(query)
    if _layered(path) and not any(k == "layer" for k, _ in got):
        got.append(("layer", "on"))
    got = [(k, _filters(v) if k == "filters" else v) for k, v in got]
    return path + "?" + urlencode(sorted(got), quote_via=quote, safe="")


def key(route: str, query: str | Mapping[str, Any] | Sequence[tuple[str, Any]] | None) -> str:
    """The entry's file name: sha256 of :func:`canonical`, hex."""
    return hashlib.sha256(canonical(route, query).encode("ascii")).hexdigest()


def query_of(canonical_request: str) -> str:
    """The query part of a canonical request: what a manifest stores, and a query string the service takes as is."""
    return canonical_request.split("?", 1)[1]


# --- the viewer's spelling (what the browser sends; used to plan entries a viewer will ask for) -------------------

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
    digits = (whole + frac).lstrip("0")
    point = len(whole) + (int(exp) if exp else 0)  # the decimal point's place counted from the first written digit
    lead = len(whole + frac) - len((whole + frac).lstrip("0"))
    n = point - lead
    digits = digits.rstrip("0")
    k = len(digits)
    if k <= n <= 21:
        return digits + "0" * (n - k)
    if 0 < n <= 21:
        return digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return "0." + "0" * (-n) + digits
    e = n - 1
    sign = "+" if e >= 0 else "-"
    return (digits[0] + ("." + digits[1:] if k > 1 else "")) + "e" + sign + str(abs(e))


def js_json(value: Any) -> str:
    """JSON.stringify(value) for JSON-shaped data: keys in their order, no spaces, numbers by :func:`js_number`."""
    if value is None:
        return "null"
    if isinstance(value, bool) or isinstance(value, (int, float)):
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
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return js_number(value)
    return str(value)


# --- the format: the writer and the reader ------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Entry:
    route: str
    query: str  # the canonical query part (route + "?" + query is canonical())
    key: str
    bytes: int
    media: str
    stages: tuple[str, ...]


def directory(root: Path, template: str, layer: str) -> Path:
    if layer not in LAYERS:
        raise ValueError(f"layer {layer!r} is not one of {LAYERS}")
    return Path(root) / template / layer


def write(root: Path, template: str, layer: str, model_hash: str,
          answers: Iterable[tuple[str, Any, Any]]) -> dict[str, Any]:
    """Write one bundle: each ``(route, query, response)`` - a 200 :class:`~galaxy.api.service.Response` - as its body
    under its key, then the manifest (sorted keys, indent 1, LF). Refuses a response that is not a 200, and two
    answers to one key with different bytes. Returns the manifest."""
    out = directory(root, template, layer)
    (out / ENTRIES).mkdir(parents=True, exist_ok=True)
    entries: dict[str, dict[str, Any]] = {}
    for route, query, response in answers:
        if response.status != 200:
            raise BundleError(f"{route}?{query} answered {response.status}: a bundle holds only answers")
        request = canonical(route, query)
        k = hashlib.sha256(request.encode("ascii")).hexdigest()
        if k in entries:
            if entries[k]["bytes"] != len(response.body):
                raise BundleError(f"{request} was planned twice and answered differently")
            continue
        (out / ENTRIES / k).write_bytes(response.body)
        entries[k] = {
            "route": _route(route), "query": query_of(request), "key": k, "bytes": len(response.body),
            "media": response.media, "stages": list(response.stages),
        }
    manifest = {
        "format": FORMAT, "model_hash": model_hash, "template": template, "layer": layer,
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

    Bodies stay on disk and are read on each hit (an 18 MB render reads in milliseconds; a cache of bodies would be a
    second copy of what the page cache already holds)."""

    __slots__ = ("root", "model_hash", "bundles", "_entries")

    def __init__(self, root: Path, model_hash: str) -> None:
        self.root = Path(root)
        self.model_hash = model_hash
        self.bundles: list[dict[str, Any]] = []
        self._entries: dict[str, tuple[str, Path, int]] = {}
        if not self.root.is_dir():
            raise BundleError(f"bundles {self.root} is not a directory")
        for path in manifests(self.root):
            manifest = read_manifest(path)
            if manifest.get("model_hash") != model_hash:
                raise BundleMismatch(
                    f"bundle {path.parent} was built from model {manifest.get('model_hash')} and this server's model "
                    f"is {model_hash}: rebuild it with tools/export_template.py (a mismatch is an error, not a fallback)"
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
                    raise BundleError(f"{e['route']}?{e['query']} is in two bundles with different bytes")
                if held is None and _route(e["route"]) not in NEVER:
                    self._entries[e["key"]] = (e["media"], body, size)
            self.bundles.append({k: manifest[k] for k in ("template", "layer", "model_hash", "built_at")}
                                | {"entries": len(manifest["entries"]), "path": str(path.parent)})

    def __len__(self) -> int:
        return len(self._entries)

    def find(self, route: str, query: Any) -> tuple[str, bytes] | None:
        """``(media, body)`` for a request a bundle holds, else None. /api/version and the index are never held."""
        path = _route(route)
        if path in NEVER or not path.startswith("/api"):
            return None
        held = self._entries.get(key(path, query))
        if held is None:
            return None
        media, body, _ = held
        return media, body.read_bytes()
