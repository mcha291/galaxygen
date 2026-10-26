"""Export a template's bundle: every answer the viewer asks of a template at galaxy scale, computed once (S72, W2).

    uv run python tools/export_template.py --out bundles                       # both templates, both layers
    uv run python tools/export_template.py --out bundles --template milky_way --layer on --only metadata,render
    uv run python tools/export_template.py --check bundles                     # every entry re-computed, byte for byte
    uv run python tools/export_template.py --dry-run                           # the plan's entries per route

A bundle is the model's own answers, stored as the bytes it sent, under the content hash of the model package that
computed them (galaxy.api.bundle holds the format, the key and the reader; ``python -m galaxy.api --bundles <dir>``
serves from it). This tool builds a ``Service()`` with no bundles, asks it every request of the plan through
``service.handle``, refuses the export if any answer is not a 200, and writes each body and the manifest.
``--check`` is the gate's instrument: a fresh service recomputes every entry of an existing bundle from the query
string the manifest records - the viewer's own spelling, parsed as a GET's - and the table says how many are
byte-identical; any difference, or a bundle from another model hash, exits 1. **It replays in another order than the
export's**, so identity cannot rest on the export's warm cache: the export runs template by template, layer on before
off, each bundle's entries in plan order; the check runs the bundles in path order (each template's layer off before
on) and each bundle's entries last-planned first (a tile or a remainder on a cold galaxy before its render). It prints
the order it ran.

**What is bundled is :func:`plan` alone** (the lead's ruling R1 at S72; the owner rules the size bound with the
probe's table): what the viewer asks at galaxy scale, each request in the viewer's own spelling - the whole input
vector as ``flow.query`` lays it out, then ``model=`` and ``template=``, ``layer=off`` only under "physics only", then
the route's parameters in the order its loader spreads them (frontend/src/api.ts, interface/transport.js), numbers as
a browser writes them and the filter sets as ``JSON.stringify`` writes them (``bundle.js_number``, ``bundle.js_json``).
The key is the request's meaning, but its route parameters are raw strings (the key does not know which a route
parses as numbers; a raw key can only cost a miss, never a wrong answer), so the plan spells them as the viewer does
for its requests to hit, and tests/test_bundle.py checks the plan against the requests a real viewer made
(tests/fixtures/s72_viewer_requests.json). Per-cell bright tiles (``--levels``) are
opt-in and are not what the viewer sends (it asks the cells in view in one request): nothing below 4 kpc is bundled.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import OrderedDict
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILTERS = ROOT / "frontend" / "src" / "galaxy" / "filters.json"
INSTRUMENTS = ROOT / "frontend" / "src" / "galaxy" / "instruments.json"
TEMPLATES = ("milky_way", "ngc_4414")
GROUPS = ("metadata", "arrays", "render", "census", "bright")
# What the viewer asks the history views with (api.ts HISTORY_SAMPLING): a field over t, 200 steps at 32 bits.
HISTORY = {"t_samples": 200, "precision": "f4"}
# The whole-galaxy star sample (api.ts STAR_SAMPLE, D61): /api/region over every cell, as App.tsx loadSample asks.
STAR_SAMPLE = 20_000
# The star-first view's point budget at its slider's default (GalaxyTab.tsx brightestOf(500): 10^(2 + 3 x 0.5), rounded).
POINT_BUDGET = round(10 ** 3.5)
# The Galaxy view's own arrays request (FieldVolume.tsx SCALARS = interface/ages.js FIELD_SCALARS).
FIELD_SCALARS = ("bulge_scale_radius",)
# The Science tab's scenes (preview/CheckpointScene.tsx): the disc each checkpoint draws, the rotation curve's inset,
# checkpoint 2's playback, and the histories checkpoint 4 scrubs (all but the one that is not an epoch).
DISC_AT = {1: "disc_surface_density", 3: "disc_surface_density", 4: "stellar_surface_density"}
INSET_AT = {1: ("circular_velocity", "halo_circular_velocity", "disc_circular_velocity")}
PLAYBACK_FIELDS = ("disc_surface_density", "disc_radial_spread", "merger_delivery", "disc_heating", "halo_potential",
                   "halo_potential_midplane")
NOT_AN_EPOCH = ("stars_formed_history",)
# Opt-in per-cell tiles (--levels): the threshold a zoomed view asks at, Lsun; the table's grid value nearest it is
# sent. S72's probe read MW 10^3.10 and NGC 10^3.25 at level 2 from a real zoom; S65's 1 kpc reading was 10^3.35.
ZOOMED_L_MIN = {1: 2239.0, 2: 1259.0, 3: 1259.0}


def filter_sets() -> "OrderedDict[str, list[dict[str, Any]]]":
    """Every shipped set by name, as filters.ts FILTER_SETS joins them ({...filters.sets, ...instruments.sets})."""
    out: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for path in (FILTERS, INSTRUMENTS):
        for name, s in json.loads(path.read_text(encoding="utf-8"))["sets"].items():
            out[name] = s["curves"]
    return out


def white_kelvin() -> float:
    """The viewer's white point (filters.json white.kelvin): every render, cluster and tile request carries it."""
    return json.loads(FILTERS.read_text(encoding="utf-8"))["white"]["kelvin"]


def _js(params: dict[str, Any]) -> dict[str, str]:
    from galaxy.api.bundle import js_value

    return {k: js_value(v) for k, v in params.items() if v is not None}


def viewer_query(template: dict[str, Any], inputs: dict[str, Any], layer: str) -> dict[str, str]:
    """What every loader spreads (useWorkflow.queryOf, App.tsx galaxyQuery): every input of the model in the
    catalogue's order (controls, seeds, events: flow.catalogue), each its default under the template's value
    (templates.ts applyTemplate), the event list as JSON in the served key order (flow.query) - then model, template,
    and ``layer=off`` under "physics only" (galaxy/layer.ts layerQuery: absent when on)."""
    from galaxy.api.bundle import js_json

    resolved = {**template["inputs"]["controls"], **template["inputs"]["seeds"]}
    out: dict[str, Any] = {}
    for kind in ("controls", "seeds", "events"):
        for inp in inputs[kind]:
            name = inp["name"]
            if kind == "events":
                out[name] = js_json(template["inputs"]["mergers"] if name == "mergers" else inp["default"])
            else:
                out[name] = resolved.get(name, inp["default"])
    out["model"] = template["model"]
    out["template"] = template["name"]
    if layer == "off":
        out["layer"] = "off"
    return _js(out)


def pick_threshold(frame: Any, cells: Sequence[int] | None = None, budget: int = POINT_BUDGET) -> float:
    """brightTiles.ts pickThreshold over the tiles in view (every level-0 cell at the landing): the smallest grid
    threshold at which the summed expected count is at most the point budget, the last if none is. The sum is the
    viewer's: the f4 table's counts as doubles, added cell by cell in order. The value is the table's own double."""
    _, arrays = frame
    thresholds = arrays["threshold"]
    n = len(thresholds)
    expected = arrays["expected"].ravel()
    rows = range(len(expected) // n) if cells is None else cells
    for k in range(n):
        total = 0.0
        for c in rows:
            total += float(expected[c * n + k])
        if total <= budget:
            return float(thresholds[k])
    return float(thresholds[n - 1])


def nearest(frame: Any, l_min: float) -> float:
    """The table's grid threshold nearest ``l_min`` in log (the viewer sends a table value, never its own number)."""
    _, arrays = frame
    return float(min(arrays["threshold"], key=lambda g: abs(math.log10(float(g)) - math.log10(l_min))))


def science_arrays(fields: list[dict[str, Any]], checkpoints: Sequence[int]) -> list[tuple[list[str], bool]]:
    """The Science tab's /api/arrays requests, (names, history?) in the order its views build them: per checkpoint
    the plots look (Preview.tsx: wantedAt(panelsAt) plain, then each (R, t) map with HISTORY_SAMPLING), the scene look
    (CheckpointScene.tsx: DiscScene's names, with and without the rotation-curve inset; MergerScene's playback and
    HistoryScene's histories with HISTORY_SAMPLING) and the scene's readout (Published.tsx: the scalars, plain)."""
    declared = {f["name"]: f for f in fields}
    catalogues = {f["stage"] for f in fields if f.get("domain") == "object"}
    out: list[tuple[list[str], bool]] = []
    for n in checkpoints:
        at = [f for f in fields if f.get("checkpoint") == n]
        groups: OrderedDict[str, list[str]] = OrderedDict()
        for f in at:
            if f.get("domain") == "grid" and len(f.get("axes") or []) == 1 and f.get("kind") == "field":
                groups.setdefault(f"{f['axes'][0]}:{f['unit']}", []).append(f["name"])
        scalars = [f["name"] for f in at if f.get("domain") == "galaxy" and f["stage"] not in catalogues]
        maps = [f["name"] for f in at if f.get("domain") == "grid" and list(f.get("axes") or []) == ["R", "t"]]
        wanted = [name for names in groups.values() for name in names] + scalars
        if wanted:
            out.append((wanted, False))
        out += [([m], True) for m in maps]
        if n == 2:
            if all(name in declared for name in PLAYBACK_FIELDS):
                out.append((list(PLAYBACK_FIELDS), True))
        elif n == 4:
            out += [([m], True) for m in maps if m not in NOT_AN_EPOCH]
        elif n in DISC_AT and n < 5:
            base = [DISC_AT[n]] if DISC_AT[n] in declared else []
            base += ["pattern_density_contrast"] if n >= 3 and "pattern_density_contrast" in declared else []
            base += ["circular_velocity"] if n == 1 and "circular_velocity" in declared else []
            names = list(dict.fromkeys(base))
            if names:
                out.append((names, False))
            if n in INSET_AT:
                charts = list(dict.fromkeys(base + [f for f in INSET_AT[n] if f in declared]))
                out.append((charts, False))
        if scalars:
            out.append((scalars, False))
    return out


def plan(template: str, layer: str, service: Any, levels: Sequence[int] = (), only: Iterable[str] | None = None,
         l_min: float | None = None) -> list[tuple[str, dict[str, str]]]:
    """The bundle's entries for one template and layer setting: ``(route, query)``, the query in the viewer's order
    and spelling, no request twice. ``l_min`` is the landing's tile threshold; None picks it from the bright table by
    the viewer's rule (the table is computed for it).

    metadata: /api/templates; /api/stages, /api/fields, /api/inputs with model=; /api/blackbody per shipped set (no
    template: it runs no stage). arrays: the Galaxy view's (fields=bulge_scale_radius) and, with the layer on (the
    Science tab sends no layer switch), the Science tab's sets (:func:`science_arrays`). render: the layer's tables
    (/api/layer, once; S73), per set the whole render (white, f4) and the star-first remainder at the landing
    threshold. census: over GalaxyTab.tsx's wholeDisc
    window (r_min, r_max from the grid, phi 0..2 pi, level 0) - clouds f4, clusters per set with white, remnants - and
    /api/region's whole-galaxy sample (stars=20000). bright: the table (table=1, f4) and the landing's one tile request
    per set, every level-0 cell at the landing threshold; with ``levels``, single-cell tiles at those levels.
    """
    from galaxy.api.bundle import js_json, js_number

    groups = set(GROUPS if only is None else only)
    unknown = groups - set(GROUPS)
    if unknown:
        raise SystemExit(f"--only {sorted(unknown)}: the groups are {list(GROUPS)}")
    named = {t["name"]: t for t in service.handle("/api/templates").json()["templates"]}
    if template not in named:
        raise SystemExit(f"no template {template!r}; /api/templates lists {list(named)}")
    t = named[template]
    model = t["model"]
    meta = {"model": model}
    inputs = service.handle("/api/inputs", meta).json()
    fields = service.handle("/api/fields", meta).json()
    stages = service.handle("/api/stages", meta).json()
    base = viewer_query(t, inputs, layer)
    sets = filter_sets()
    curves = {name: js_json(c) for name, c in sets.items()}
    white = _js({"white": white_kelvin()})
    R = fields["grid"]["axes"]["R"]
    whole_disc = _js({"r_min": R.get("lo", 0), "r_max": R["hi"], "phi_min": 0, "phi_max": 2 * math.pi, "level": 0})
    out: list[tuple[str, dict[str, str]]] = []

    if "metadata" in groups:
        out += [("/api/templates", {}), ("/api/fields", meta), ("/api/stages", meta), ("/api/inputs", meta)]
        out += [("/api/blackbody", white | {"filters": curves[s]}) for s in sets]

    if "arrays" in groups:
        declared = {f["name"] for f in fields["fields"]}
        asks = [([n for n in FIELD_SCALARS if n in declared], False)]
        if layer == "on":
            asks += science_arrays(fields["fields"], [cp["n"] for cp in stages["checkpoints"]])
        for names, history in asks:
            if names:
                out.append(("/api/arrays", base | (_js(HISTORY) if history else {}) | {"fields": ",".join(names)}))

    table = None
    if groups & {"render", "bright"}:
        table_query = base | {"table": "1", "precision": "f4"}
        if l_min is None or levels:
            got = service.handle("/api/bright", table_query)
            if got.status != 200:
                raise SystemExit(f"/api/bright table=1 answered {got.status}: {got.body[:300]!r}")
            table = got.frame()
            l_min = pick_threshold(table) if l_min is None else l_min
    landing = None if l_min is None else js_number(l_min)

    if "render" in groups:
        # S73 (#199): the layer's tables, once per galaxy - the query every loader spreads, nothing else (api.ts loadLayer).
        out.append(("/api/layer", dict(base)))
        for s in sets:
            out.append(("/api/render", base | white | {"precision": "f4", "filters": curves[s]}))
        for s in sets:
            out.append(("/api/render", base | white | {"precision": "f4", "l_min": landing, "only": "remainder", "filters": curves[s]}))

    if "census" in groups:
        out.append(("/api/clouds", base | {"precision": "f4"} | whole_disc))
        for s in sets:
            out.append(("/api/clusters", base | {"filters": curves[s]} | white | whole_disc))
        # The whole-disc remnants: the plan's text names the censuses, but neither S72's walk nor S73's (#200: every set,
        # both modes, both layers, the Science tab, the clouds' switches) logged it - the viewer asks remnants only in
        # RegionVolume, for the stars regime's window round the view's target (GalaxyTab.tsx `area`), never the whole
        # disc. Kept (a bundle may serve another client), the one planned entry no viewer sends.
        out.append(("/api/remnants", base | whole_disc))
        out.append(("/api/region", base | _js({"stars": STAR_SAMPLE})))

    if "bright" in groups:
        from galaxy.stages import systems

        out.append(("/api/bright", base | {"table": "1", "precision": "f4"}))
        every = ",".join(str(c) for c in range(systems.CELL_COUNT))
        for s in sets:
            out.append(("/api/bright", base | {"cells": every, "l_min": landing, "filters": curves[s]} | white | {"precision": "f4"}))
        for level in sorted(set(levels)):
            at = landing if level == 0 else js_number(nearest(table, ZOOMED_L_MIN[level]))
            for cell in range(systems.CELL_COUNT * systems.children_per_cell(level)):  # ring-major: a ring's draw serves its cells
                for s in sets:
                    tile = {"cells": str(cell), **({"level": str(level)} if level else {}), "l_min": at, "filters": curves[s]}
                    out.append(("/api/bright", base | tile | white | {"precision": "f4"}))
    once: dict[tuple[str, tuple[tuple[str, str], ...]], dict[str, str]] = {}
    for route, query in out:  # a request two views build alike (Published's scalars, a history) is planned once
        once.setdefault((route, tuple(query.items())), query)
    return [(route, query) for (route, _), query in once.items()]


# --- the export and the check ----------------------------------------------------------------------------------------

class Tally:
    """Per route: entries, bytes, seconds - the table the tool prints."""

    def __init__(self) -> None:
        self.rows: OrderedDict[str, list[float]] = OrderedDict()

    def add(self, route: str, size: int, seconds: float) -> None:
        row = self.rows.setdefault(route, [0, 0, 0.0])
        row[0] += 1
        row[1] += size
        row[2] += seconds

    def table(self, title: str) -> str:
        head = f"{'route':<16} {'entries':>8} {'bytes':>14} {'seconds':>9}"
        lines = [title, head, "-" * len(head)]
        for route, (n, size, sec) in self.rows.items():
            lines.append(f"{route:<16} {n:>8} {size:>14,} {sec:>9.1f}")
        n, size, sec = (sum(r[i] for r in self.rows.values()) for i in range(3))
        lines.append(f"{'total':<16} {n:>8} {size:>14,} {sec:>9.1f}")
        return "\n".join(lines)


def answers(service: Any, entries: Iterable[tuple[str, dict[str, str]]], tally: Tally) -> Iterator[tuple[str, dict[str, str], Any]]:
    """Each planned request answered by the model, timed; anything but a 200 stops the export (a bundle holds
    answers only, and a plan that asks what the model refuses is a wrong plan)."""
    for route, query in entries:
        start = time.perf_counter()
        response = service.handle(route, query)
        seconds = time.perf_counter() - start
        if response.status != 200:
            shown = {k: (v if len(v) < 80 else v[:77] + "...") for k, v in query.items()}
            raise SystemExit(f"{route} {shown} answered {response.status}: {response.body[:300]!r}")
        tally.add(route, len(response.body), seconds)
        yield route, query, response


def export(service: Any, out: Path, template: str, layer: str, levels: Sequence[int] = (),
           only: Iterable[str] | None = None) -> tuple[dict[str, Any], Tally]:
    from galaxy.api import bundle

    tally = Tally()
    entries = plan(template, layer, service, levels, only)
    manifest = bundle.write(out, template, layer, service, answers(service, entries, tally))
    return manifest, tally


def check(root: Path, service: Any) -> tuple[list[list[Any]], bool]:
    """Recompute every entry of every bundle under ``root`` live and compare bytes, in the replay order the module's
    docstring states (bundles in path order, entries last-planned first). Returns rows of [bundle, route, entries,
    identical, differing] and whether all were identical under this model's hash."""
    from galaxy.api import bundle

    rows: list[list[Any]] = []
    ok = True
    for path in bundle.manifests(root):
        manifest = bundle.read_manifest(path)
        print(f"replaying {manifest['template']}/{manifest['layer']}: {len(manifest['entries'])} entries, last-planned first")
        manifest["entries"] = list(reversed(manifest["entries"]))
        where = f"{manifest['template']}/{manifest['layer']}"
        if manifest["model_hash"] != service.model_hash:
            print(f"{where}: built from model {manifest['model_hash']}, this model is {service.model_hash}")
            ok = False
            continue
        by_route: OrderedDict[str, list[Any]] = OrderedDict()
        for e in manifest["entries"]:
            live = service.handle(e["route"], e["query"])
            held = (path.parent / bundle.ENTRIES / e["key"]).read_bytes()
            same = live.status == 200 and live.body == held and live.media == e["media"] \
                and bundle.key(service, e["route"], e["query"]) == e["key"]
            row = by_route.setdefault(e["route"], [where, e["route"], 0, 0, 0])
            row[2] += 1
            row[3 if same else 4] += 1
            if not same:
                ok = False
                print(f"DIFFERS {where} {e['route']} {e['key'][:12]}: live {live.status} {len(live.body)} B, held {len(held)} B")
        rows += list(by_route.values())
    return rows, ok


def _list(raw: str) -> list[str]:
    return [p for p in raw.split(",") if p]


def main(argv: Sequence[str] | None = None) -> int:
    from galaxy.api.service import Service
    from galaxy.specs import utf8_stdout

    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, help="the bundles directory to write (<out>/<template>/<layer>/)")
    parser.add_argument("--template", default=",".join(TEMPLATES), help="comma-separated template names")
    parser.add_argument("--layer", default="on,off", help="comma-separated: on, off")
    parser.add_argument("--levels", default="", help="comma-separated cell levels to add single-cell bright tiles at (none by default)")
    parser.add_argument("--only", default=",".join(GROUPS), help=f"comma-separated groups of {','.join(GROUPS)}")
    parser.add_argument("--check", nargs="?", const="", default=None, metavar="DIR",
                        help="re-compute every entry of the bundles in DIR (default --out) and compare bytes")
    parser.add_argument("--dry-run", action="store_true", help="print the plan's entries per route")
    args = parser.parse_args(argv)
    levels = [int(x) for x in _list(args.levels)]

    if args.dry_run:
        service = Service()
        for template in _list(args.template):
            for layer in _list(args.layer):
                counts: OrderedDict[str, int] = OrderedDict()
                for route, _ in plan(template, layer, service, levels, _list(args.only)):
                    counts[route] = counts.get(route, 0) + 1
                print(f"{template} / layer {layer}: " + ", ".join(f"{r} {n}" for r, n in counts.items()))
        return 0

    if args.check is not None:
        root = Path(args.check) if args.check else args.out
        if root is None:
            parser.error("--check needs a directory (or --out)")
        start = time.perf_counter()
        rows, ok = check(root, Service())
        head = f"{'bundle':<18} {'route':<16} {'entries':>8} {'identical':>10} {'differing':>10}"
        print(head)
        print("-" * len(head))
        for where, route, n, same, differ in rows:
            print(f"{where:<18} {route:<16} {n:>8} {same:>10} {differ:>10}")
        total = [sum(r[i] for r in rows) for i in (2, 3, 4)]
        print(f"{'total':<35} {total[0]:>8} {total[1]:>10} {total[2]:>10}")
        print(f"checked in {time.perf_counter() - start:.1f} s: {'every entry byte-identical' if ok and rows else 'NOT identical'}")
        return 0 if ok and rows else 1

    if args.out is None:
        parser.error("--out is required to export")
    service = Service()
    print(f"model {service.model_hash}")
    grand = time.perf_counter()
    for template in _list(args.template):
        for layer in _list(args.layer):
            start = time.perf_counter()
            manifest, tally = export(service, args.out, template, layer, levels, _list(args.only))
            print(tally.table(f"\n{template} / layer {layer}: {len(manifest['entries'])} entries, "
                              f"{time.perf_counter() - start:.1f} s"))
            sys.stdout.flush()
    print(f"\nexported in {time.perf_counter() - grand:.1f} s into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
