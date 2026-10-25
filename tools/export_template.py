"""Export a template's bundle: every answer the viewer asks of a template, computed once (S72, BUILD_IV Phase W2).

    uv run python tools/export_template.py --out bundles                      # both templates, both layers, levels 0-1
    uv run python tools/export_template.py --out bundles --template milky_way --layer on --only metadata,render
    uv run python tools/export_template.py --check bundles                    # every entry re-computed, byte for byte

A bundle is the model's own answers, stored as the bytes it sent, under the content hash of the model package that
computed them (galaxy.api.bundle has the format and the reader; ``python -m galaxy.api --bundles <dir>`` serves from
it). This tool builds a ``Service()`` with no bundles, asks it every request of the plan through ``service.handle``,
refuses the export if any answer is not a 200, and writes each body and the manifest. ``--check`` is the gate's
instrument: a fresh service recomputes every entry of an existing bundle from its canonical query string - another
path than the export's own mapping (rule B3) - and the table says how many are byte-identical; any difference, or a
bundle from another model hash, exits 1.

**What is bundled is :func:`plan` alone** (the owner's ruling 6 sets the scope after the probe's table): each entry is
a request in the viewer's own spelling - the whole input vector as ``flow.query`` lays it out, ``model=`` and
``template=`` beside it, ``layer=off`` only under "physics only", numbers as a browser writes them, the filter sets as
``JSON.stringify`` writes them (``bundle.js_number``, ``bundle.js_json``) - because a bundle answers a request only
when its canonical form is an entry's, and the viewer asks in that spelling (frontend/src/api.ts, interface/flow.js,
workflow/templates.ts). Changing the scope is changing this function; the mechanism does not move.
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
GROUPS = ("metadata", "arrays", "render", "census", "bright", "region")
# What the viewer asks the history views with (api.ts HISTORY_SAMPLING): a field over t, 200 steps at 32 bits.
HISTORY = {"t_samples": 200, "precision": "f4"}
# The whole-galaxy star sample (api.ts STAR_SAMPLE, D61): /api/region over every cell, as App.tsx loadSample asks.
STAR_SAMPLE = 20_000
# The star-first view's point budget at its slider's default (GalaxyTab.tsx: 10^(2 + 3 x 500/1000), rounded).
POINT_BUDGET = round(10 ** 3.5)
# The tile threshold a zoomed view asks at, per level, Lsun before the grid snaps it: S65's measured picks of the
# viewer's rule at a 1 kpc view (level 1: 2239, 10^3.35) and a 0.25 kpc view (level 2: 224, 10^2.35)
# [verified: tools/timings.py, the "bright: one tile" rows' comments]; level 3 has no measured pick and takes level 2's.
# Level 0 is the galaxy-scale pick, computed from the table by the viewer's rule (galaxy_threshold).
ZOOMED_L_MIN = {1: 2239.0, 2: 224.0, 3: 224.0}


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
    """What every loader spreads (useWorkflow.queryOf, App.tsx galaxyQuery): every input of the model - its default
    under the template's value (templates.ts applyTemplate), the event list as JSON - then model, template, and
    ``layer=off`` under "physics only" (galaxy/layer.ts layerQuery: absent when on)."""
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


def galaxy_threshold(table: Any, budget: int = POINT_BUDGET, cells: Sequence[int] | None = None) -> float:
    """The viewer's pick (brightTiles.ts pickThreshold): the smallest grid threshold at which the tiles in view hold
    at most the point budget, every level-0 cell in view at galaxy scale; the last if none does. The sum is the
    viewer's - the f4 table's counts as doubles, summed cell by cell in order."""
    header, arrays = table
    thresholds = arrays["threshold"].astype(float)
    n = len(thresholds)
    expected = arrays["expected"].astype(float).reshape(-1, n)
    rows = range(expected.shape[0]) if cells is None else cells
    for k in range(n):
        total = 0.0
        for c in rows:
            total += float(expected[c, k])
        if total <= budget:
            return float(thresholds[k])
    return float(thresholds[-1])


def snapped(table: Any, l_min: float) -> float:
    """The grid threshold the route answers a tile at (snapped up to the 0.05 dex grid, v6_tiles): the viewer sends
    the table's own value, so the plan does."""
    _, arrays = table
    grid = arrays["threshold"].astype(float)
    above = [g for g in grid if g >= l_min * (1 - 1e-12)]
    return float(above[0]) if above else float(grid[-1])


def plan(template: str, layer: str, levels: Sequence[int], service: Any,
         only: Iterable[str] | None = None) -> list[tuple[str, dict[str, str]]]:
    """The bundle's entries for one template and layer setting: ``(route, query)`` in the viewer's spelling.

    (i) metadata: /api, /api/templates, and /api/stages, /api/fields, /api/inputs with and without the template's
    model= (transport.js sends model= only once it is known); /api/blackbody per shipped set (no template: it runs no
    stage and is the same for every template). (ii) /api/arrays, one entry per published field, and for a field over
    t also the history form (t_samples=200, precision=f4). (iii) /api/render per shipped set, whole, white and f4 as
    api.ts wholeRender asks; and only=remainder at each tile threshold the plan uses (loadRemainder). (iv) the
    censuses over GalaxyTab.tsx's wholeDisc window (r_min, r_max from the grid, phi 0..2 pi, level 0): clouds at f4,
    clusters per set with white, remnants; and /api/region's whole-galaxy sample (stars=20000, App.tsx loadSample).
    (v) /api/bright: the table (table=1, f4), and the tiles one cell per request - level 0 at the galaxy-scale pick,
    level k > 0 at ZOOMED_L_MIN[k] snapped - per set, f4. (vi) /api/region by cell: none - the viewer's region
    requests are windows (regimes.ts regionAround), not cells.
    """
    from galaxy.api.bundle import js_json

    groups = set(GROUPS if only is None else only)
    unknown = groups - set(GROUPS)
    if unknown:
        raise SystemExit(f"--only {sorted(unknown)}: the groups are {list(GROUPS)}")
    listed = service.handle("/api/templates").json()
    named = {t["name"]: t for t in listed["templates"]}
    if template not in named:
        raise SystemExit(f"no template {template!r}; /api/templates lists {list(named)}")
    t = named[template]
    model = t["model"]
    inputs = service.handle("/api/inputs", {"model": model}).json()
    fields = service.handle("/api/fields", {"model": model}).json()
    base = viewer_query(t, inputs, layer)
    sets = filter_sets()
    curves = {name: js_json(c) for name, c in sets.items()}
    white = white_kelvin()
    R = fields["grid"]["axes"]["R"]
    whole_disc = _js({"r_min": R.get("lo", 0), "r_max": R["hi"], "phi_min": 0, "phi_max": 2 * math.pi, "level": 0})
    out: list[tuple[str, dict[str, str]]] = []

    if "metadata" in groups:
        out += [("/api", {}), ("/api/templates", {})]
        for route in ("/api/stages", "/api/fields", "/api/inputs"):
            out += [(route, {"model": model}), (route, {})]
        out += [("/api/blackbody", _js({"white": white}) | {"filters": curves[s]}) for s in sets]

    if "arrays" in groups:
        for f in fields["fields"]:
            out.append(("/api/arrays", base | {"fields": f["name"]}))
            if "t" in (f.get("axes") or []):
                out.append(("/api/arrays", base | _js(HISTORY) | {"fields": f["name"]}))

    # The tile thresholds, by level: the viewer's picks off the table (the table is computed for them).
    thresholds: dict[int, float] = {}
    if groups & {"render", "bright"}:
        table = service.handle("/api/bright", base | {"table": "1", "precision": "f4"})
        if table.status != 200:
            raise SystemExit(f"/api/bright table=1 answered {table.status}: {table.body[:300]!r}")
        frame = table.frame()
        for level in sorted(set(levels)):
            thresholds[level] = galaxy_threshold(frame) if level == 0 else snapped(frame, ZOOMED_L_MIN[level])

    if "render" in groups:
        for s in sets:
            out.append(("/api/render", base | _js({"white": white, "precision": "f4"}) | {"filters": curves[s]}))
        for s in sets:
            for l_min in sorted(set(thresholds.values()), reverse=True):
                out.append(("/api/render", base | _js({"white": white, "precision": "f4", "l_min": l_min, "only": "remainder"})
                            | {"filters": curves[s]}))

    if "census" in groups:
        out.append(("/api/clouds", base | {"precision": "f4"} | whole_disc))
        for s in sets:
            out.append(("/api/clusters", base | {"filters": curves[s]} | _js({"white": white}) | whole_disc))
        out.append(("/api/remnants", base | whole_disc))
        out.append(("/api/region", base | _js({"stars": STAR_SAMPLE})))

    if "bright" in groups:
        from galaxy.stages import systems

        out.append(("/api/bright", base | {"table": "1", "precision": "f4"}))
        for level in sorted(set(levels)):
            count = systems.CELL_COUNT * systems.children_per_cell(level)
            for cell in range(count):  # ring-major: a ring's draw serves its cells while the bright cache holds it
                for s in sets:
                    tile = {"cells": cell, **({"level": level} if level else {}), "l_min": thresholds[level]}
                    out.append(("/api/bright", base | _js(tile) | {"filters": curves[s]} | _js({"white": white, "precision": "f4"})))

    # (vi) "region": nothing - the viewer asks /api/region by window, never by cell (see the docstring).
    return out


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


def export(service: Any, out: Path, template: str, layer: str, levels: Sequence[int],
           only: Iterable[str] | None = None) -> tuple[dict[str, Any], Tally]:
    from galaxy.api import bundle

    tally = Tally()
    entries = plan(template, layer, levels, service, only)
    manifest = bundle.write(out, template, layer, service.model_hash, answers(service, entries, tally))
    return manifest, tally


def check(root: Path, service: Any) -> tuple[list[list[Any]], bool]:
    """Recompute every entry of every bundle under ``root`` live and compare bytes. Returns rows of
    [bundle, route, entries, identical, differing] and whether all were identical under this model's hash."""
    from galaxy.api import bundle

    rows: list[list[Any]] = []
    ok = True
    for path in bundle.manifests(root):
        manifest = bundle.read_manifest(path)
        where = f"{manifest['template']}/{manifest['layer']}"
        if manifest["model_hash"] != service.model_hash:
            print(f"{where}: built from model {manifest['model_hash']}, this model is {service.model_hash}")
            ok = False
            continue
        by_route: OrderedDict[str, list[Any]] = OrderedDict()
        for e in manifest["entries"]:
            live = service.handle(e["route"], e["query"])
            held = (path.parent / bundle.ENTRIES / e["key"]).read_bytes()
            same = live.status == 200 and live.body == held and live.media == e["media"]
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
    parser.add_argument("--levels", default="0,1", help="comma-separated cell levels the bright tiles ship at")
    parser.add_argument("--only", default=",".join(GROUPS), help=f"comma-separated groups of {','.join(GROUPS)}")
    parser.add_argument("--check", nargs="?", const="", default=None, metavar="DIR",
                        help="re-compute every entry of the bundles in DIR (default --out) and compare bytes")
    parser.add_argument("--dry-run", action="store_true", help="print the plan's entries per route and compute nothing more")
    args = parser.parse_args(argv)

    if args.dry_run:
        service = Service()
        for template in _list(args.template):
            for layer in _list(args.layer):
                counts: OrderedDict[str, int] = OrderedDict()
                for route, _ in plan(template, layer, [int(x) for x in _list(args.levels)], service, _list(args.only)):
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
    levels = [int(x) for x in _list(args.levels)]
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
