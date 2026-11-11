"""The request walk (S95, Audit VI F-4-1): what a real viewer asks, logged, reduced and held to the fixture and the plan.

``tests/fixtures/s72_viewer_requests.json`` is a recording of every galaxy-scale request a real viewer made (one
entry per ``galaxy.api.bundle.key`` meaning), and ``tests/test_bundle.py`` holds ``tools/export_template.py``'s bundle
plan to it string for string - the bundle is keyed on the raw query, so only the viewer's own spelling is sure to hit.
S73 (#200, D236) recorded it with a walker that was never committed; this is that walker, repeatable:

``serve``
    The built viewer (``frontend/dist``) and the API on 127.0.0.1:8041 through the API's own handler, the template
    bundles mounted (a galaxy-scale request is a bundle hit or a visible miss), every answer logged as one JSON line:
    the path, the full raw query as ``Service.handle`` and ``bundle.key`` see it (a GET's query, or a POST's
    form-encoded body appended to it, as ``galaxy.api.http`` hands it on), status, ``X-Galaxy-Source``, bytes, sha256.
    ``/api/version?walk=<step>`` is the walk's mark: the answers after it are that step's.
``walk``
    ``serve`` in a child process, then the Playwright walk (``frontend/e2e/walk/walk.probe.ts``,
    ``npm --prefix frontend run walk``) against it, then the server stopped and ``reduce`` run on the log. An existing
    file at ``--log`` is replaced (deleted before the server starts), and the server's and Playwright's output are
    written beside it, at the log's path with ``.server.txt`` and ``.probe.txt`` in place of its suffix.
``reduce``
    The log turned into the fixture's own format and a three-way diff: the walk's meanings against the committed
    fixture's and the mounted bundles' plan (their manifests' queries) - meanings only in the walk, only in the fixture,
    only in the plan; for every meaning both hold, whether the walk's string is the fixture's; the hits and misses.
    ``--write-fixture`` re-records the fixture conservatively (see :func:`rerecord`); it is refused without
    ``--bundles`` (the plan would be empty, every new meaning ``unplanned`` and the jwst_nircam guard vacuous).

    npm --prefix frontend run build
    uv run python tools/walk_requests.py walk --bundles <dir> --log <file.jsonl> --report <file.json>
    uv run python tools/walk_requests.py reduce --bundles <dir> --log <file.jsonl> --report <file.json> [--write-fixture]

Nothing here changes what the viewer sends or what the model answers: the server is ``galaxy.api``'s handler with a
log round it, and the walk presses the viewer's own controls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
FIXTURE = ROOT / "tests" / "fixtures" / "s72_viewer_requests.json"
PORT = 8041  # S73's walker's; never the owner's 5173 / 8017, the picture test's 8019 or the smoothness tool's 8050 / 8060
MARK = "walk"

sys.path.insert(0, str(ROOT / "model"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


def log(msg: str) -> None:
    print(msg, flush=True)


def listening(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


# --- serve ------------------------------------------------------------------------------------------------------------

def _logging(handle, path: Path):
    """``handle`` with every answer appended to ``path`` as a JSON line (written after the answer: never costs it)."""
    lock = threading.Lock()
    seq = [0]

    def logged(route, query=None):
        arrived = time.time()  # the request's arrival: a step is cut by it (a computed answer is written late)
        response = handle(route, query)
        raw = query if isinstance(query, str) else ("" if query is None else repr(query))
        with lock:
            seq[0] += 1
            entry = {"n": seq[0], "t_in": round(arrived, 4), "t": round(time.time(), 4), "path": route, "query": raw,
                     "status": response.status,
                     "source": response.source, "bytes": len(response.body),
                     "sha256": hashlib.sha256(response.body).hexdigest()}
            with path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(entry) + "\n")
        return response

    return logged


def serve(args: argparse.Namespace) -> int:
    from galaxy.api.http import serve as http_serve
    from galaxy.api.service import Service

    if listening(args.port):
        log(f"port {args.port} answers already (not ours): refusing to stand a second server")
        return 2
    if not (args.client / "index.html").is_file():
        log(f"{args.client} has no index.html: npm --prefix frontend run build")
        return 2
    service = Service(client=args.client, bundles=args.bundles)  # a bundle of another model is refused here (D3)
    service.handle = _logging(service.handle, args.log)
    held = "no bundles" if service.bundles is None else ", ".join(
        f"{b['template']}/{b['layer']} {b['entries']}" for b in service.bundles.bundles)
    log(f"model {service.model_hash}; {held}; logging to {args.log}")
    http_serve("127.0.0.1", args.port, service, quiet=True)
    return 0


# --- walk -------------------------------------------------------------------------------------------------------------

def walk(args: argparse.Namespace) -> int:
    if listening(args.port):
        log(f"port {args.port} answers already (not ours): refusing")
        return 2
    args.log.parent.mkdir(parents=True, exist_ok=True)
    if args.log.exists():
        args.log.unlink()
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    argv = [sys.executable, str(Path(__file__).resolve()), "serve", "--port", str(args.port), "--log", str(args.log),
            "--client", str(args.client)] + (["--bundles", str(args.bundles)] if args.bundles else [])
    server_log = args.log.with_suffix(".server.txt")
    started = time.perf_counter()
    with server_log.open("w", encoding="utf-8", newline="\n") as out:
        server = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    try:
        deadline = time.perf_counter() + 300
        while True:
            if server.poll() is not None:
                log(f"the server exited with {server.returncode}: see {server_log}")
                return 2
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{args.port}/api", timeout=2) as r:
                    if r.status == 200:
                        break
            except (OSError, urllib.error.URLError):
                pass
            if time.perf_counter() > deadline:
                log("the server did not answer in 300 s")
                return 2
            time.sleep(0.2)
        log(f"server up on :{args.port} in {time.perf_counter() - started:.1f} s")
        npx = shutil.which("npx") or "npx"
        penv = {**os.environ, "GALAXYGEN_URL": f"http://127.0.0.1:{args.port}"}
        if args.only:
            penv["GALAXYGEN_WALK_ONLY"] = args.only
        probe_log = args.log.with_suffix(".probe.txt")
        t = time.perf_counter()
        with probe_log.open("w", encoding="utf-8", newline="\n") as out:
            r = subprocess.run([npx, "playwright", "test", "-c", "playwright.walk.config.ts"], cwd=FRONTEND, env=penv,
                               stdout=out, stderr=subprocess.STDOUT)
        log(f"walk exit {r.returncode} in {time.perf_counter() - t:.1f} s (Playwright's output: {probe_log})")
    finally:
        if server.poll() is None:
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"], capture_output=True) if os.name == "nt" \
                else server.terminate()
            try:
                server.wait(timeout=20)
            except subprocess.TimeoutExpired:
                server.kill()
    log(f"wall time {time.perf_counter() - started:.1f} s, server stopped")
    code = reduce(args)
    return r.returncode or code


# --- reduce -----------------------------------------------------------------------------------------------------------

def set_strings() -> "OrderedDict[str, str]":
    """Each shipped set's curves as the viewer form-encodes them: ``filters=<curves>`` (export_template.filter_sets)."""
    from export_template import filter_sets
    from galaxy.api import bundle

    return OrderedDict((name, "filters=" + bundle.js_query({"": bundle.js_json(c)})[1:]) for name, c in filter_sets().items())


def prefixes(service: Any) -> "OrderedDict[str, str]":
    """Every loader's spread query per galaxy (template/layer), as the export writes it (export_template.viewer_query)."""
    from export_template import viewer_query
    from galaxy.api import bundle

    out: OrderedDict[str, str] = OrderedDict()
    templates = {t["name"]: t for t in service.handle("/api/templates").json()["templates"]}
    for name in ("milky_way", "ngc_4414"):
        t = templates[name]
        inputs = service.handle("/api/inputs", {"model": t["model"]}).json()
        for layer in ("on", "off"):
            out[f"{name}/{layer}"] = bundle.js_query(viewer_query(t, inputs, layer))
    return out


def split(query: str, pre: "OrderedDict[str, str]", sets: "OrderedDict[str, str]") -> tuple[str | None, str]:
    """A raw query as the fixture writes it: its galaxy (the prefix it starts with, longest first) and the rest, a
    set's curves written ``filters=<set:NAME>``."""
    galaxy, rest = None, query
    for name, p in sorted(pre.items(), key=lambda kv: -len(kv[1])):
        if query == p or query.startswith(p + "&"):
            galaxy, rest = name, query[len(p) + 1:]
            break
    for name, s in sets.items():
        rest = rest.replace(s, f"filters=<set:{name}>")
    return galaxy, rest


def unsplit(r: dict[str, Any], pre: dict[str, str], sets: "OrderedDict[str, str]") -> str:
    rest = r["rest"]
    for name, s in sets.items():
        rest = rest.replace(f"filters=<set:{name}>", s)
    return rest if r["galaxy"] is None else pre[r["galaxy"]] + ("&" + rest if rest else "")


def windowed(path: str, query: str) -> bool:
    """A request for less than the whole disc (a zoom stand's window, a tile set short of every level-0 cell): not
    galaxy-scale, so not the fixture's (S73: "nothing windowed")."""
    q = dict(parse_qsl(query, keep_blank_values=True))
    if "r_min" in q and (q.get("r_min"), q.get("r_max"), q.get("level", "0")) != ("0", "30", "0"):
        return True
    if path.rstrip("/") == "/api/bright" and "cells" in q and len(q["cells"].split(",")) != 1024:
        return True
    return path.rstrip("/") == "/api/system"  # one star system round the view's target


def read_log(path: Path) -> list[dict[str, Any]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a line cut short when the server was stopped
    # In the order the requests arrived (a line is written when its answer is sent; a computed one comes late).
    return sorted(out, key=lambda e: (e.get("t_in", e.get("t", 0)), e["n"]))


def plan_of(bundles: Path | None) -> dict[str, dict[str, Any]]:
    """The mounted bundles' entries by key: the plan as exported (tools/export_template.py wrote each manifest)."""
    from galaxy.api import bundle

    planned: dict[str, dict[str, Any]] = {}
    if bundles is None:
        return planned
    for path in bundle.manifests(bundles):
        m = bundle.read_manifest(path)
        for e in m["entries"]:
            planned[e["key"]] = {"route": e["route"], "query": e["query"], "galaxy": f"{m['template']}/{m['layer']}"}
    return planned


def reduce(args: argparse.Namespace) -> int:
    from galaxy.api import bundle
    from galaxy.api.service import Service

    service = Service()
    sets = set_strings()
    pre = prefixes(service)
    entries = read_log(args.log)
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_pre = doc["prefixes"]
    planned = plan_of(args.bundles)

    # The walk: marks, answers, meanings.
    step = "(before any mark)"
    steps: list[str] = []
    walked: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    counts = {"answers": 0, "api": 0, "marks": 0, "bundle": 0, "model": 0, "non_200": 0, "windowed": 0, "unkeyed": 0}
    windowed_misses: list[dict[str, Any]] = []
    for e in entries:
        counts["answers"] += 1
        path, query = e["path"], e["query"]
        if path.rstrip("/") == "/api/version":
            q = dict(parse_qsl(query, keep_blank_values=True))
            if MARK in q:
                step = q[MARK]
                steps.append(step)
                counts["marks"] += 1
                continue
        if not path.startswith("/api"):
            continue
        counts["api"] += 1
        if e["status"] != 200:
            counts["non_200"] += 1
        k = bundle.key(service, path, query)
        if k is None:
            counts["unkeyed"] += 1
            continue
        counts[e["source"]] = counts.get(e["source"], 0) + 1
        if windowed(path, query):
            counts["windowed"] += 1
            if e["source"] != "bundle":
                windowed_misses.append({"path": path, "step": step})
            continue
        w = walked.setdefault(k, {"path": bundle._route(path), "spellings": OrderedDict(), "sources": set(), "steps": [],
                                  "bytes": set(), "sha256": set()})
        w["spellings"].setdefault(query, 0)
        w["spellings"][query] += 1
        w["sources"].add(e["source"])
        if step not in w["steps"]:
            w["steps"].append(step)
        w["bytes"].add(e["bytes"])
        w["sha256"].add(e["sha256"])

    # The fixture's meanings.
    fixture: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    for i, r in enumerate(doc["requests"]):
        sent = unsplit(r, fixture_pre, sets)
        k = bundle.key(service, r["path"], sent)
        fixture[k] = {"index": i, "record": r, "sent": sent}

    hand = {i for i, r in enumerate(doc["requests"]) if "kept=1" in r["rest"] or "sii_6716_surface_brightness_dig" in r["rest"]}
    report: dict[str, Any] = {
        "log": str(args.log), "counts": counts, "steps": len(steps), "meanings": len(walked),
        "prefixes_match_fixture": {g: fixture_pre.get(g) == p for g, p in pre.items()},
        "multi_spelled": [], "only_in_walk": [], "only_in_fixture": [], "string_differs": [], "hand_written": [],
        "jwst_nircam": [], "walk_not_planned": [], "planned_not_walked": [], "misses": [], "windowed_misses": windowed_misses,
    }
    for k, w in walked.items():
        spelled = list(w["spellings"])
        if len(spelled) > 1:
            report["multi_spelled"].append({"path": w["path"], "spellings": [split(s, pre, sets) for s in spelled]})
        galaxy, rest = split(spelled[0], pre, sets)
        w["record"] = {"path": w["path"], "galaxy": galaxy, "rest": rest, "bytes": max(w["bytes"])}
        if "model" in w["sources"]:
            report["misses"].append({"path": w["path"], "galaxy": galaxy, "rest": rest, "steps": w["steps"],
                                     "planned": k in planned, "in_fixture": k in fixture})
        if planned and k not in planned:
            report["walk_not_planned"].append({"path": w["path"], "galaxy": galaxy, "rest": rest[:300], "steps": w["steps"][:3]})
        if k not in fixture:
            report["only_in_walk"].append({"path": w["path"], "galaxy": galaxy, "rest": rest[:300], "steps": w["steps"][:3]})
            continue
        f = fixture[k]
        same = f["sent"] in w["spellings"]
        if not same:
            report["string_differs"].append({"path": w["path"], "fixture": f["sent"][-400:], "walk": spelled[0][-400:]})
        if f["index"] in hand:
            report["hand_written"].append({"index": f["index"], "path": w["path"], "galaxy": f["record"]["galaxy"],
                                           "equal": same, "bytes_fixture": f["record"]["bytes"], "bytes_walk": sorted(w["bytes"])})
    for k, f in fixture.items():
        if k not in walked:
            report["only_in_fixture"].append({"index": f["index"], "path": f["record"]["path"], "galaxy": f["record"]["galaxy"],
                                              "rest": f["record"]["rest"][:300], "hand_written": f["index"] in hand})
    for k, p in planned.items():
        if k not in walked:
            report["planned_not_walked"].append({"route": p["route"], "galaxy": p["galaxy"],
                                                 "query": split(p["query"], pre, sets)[1][:200]})
        if sets["jwst_nircam"] in p["query"]:
            seen = walked.get(k)
            report["jwst_nircam"].append({"route": p["route"], "galaxy": p["galaxy"], "walked": seen is not None,
                                          "equal": seen is not None and p["query"] in seen["spellings"]})
    for i in hand:
        if not any(h["index"] == i for h in report["hand_written"]):
            r = doc["requests"][i]
            report["hand_written"].append({"index": i, "path": r["path"], "galaxy": r["galaxy"], "equal": None,
                                           "bytes_fixture": r["bytes"], "bytes_walk": None})
    report["hand_written"].sort(key=lambda h: h["index"])
    report["summary"] = {
        "answers": counts["answers"], "api_answers": counts["api"], "marks": counts["marks"], "steps": len(set(steps)),
        "meanings": len(walked), "bundle_hits": counts["bundle"], "model_answers": counts["model"],
        "windowed": counts["windowed"], "windowed_misses": len(windowed_misses), "non_200": counts["non_200"],
        "galaxy_scale_misses": len(report["misses"]),
        "fixture_meanings": len(fixture), "planned": len(planned),
        "only_in_walk": len(report["only_in_walk"]), "only_in_fixture": len(report["only_in_fixture"]),
        "walk_not_planned": len(report["walk_not_planned"]), "planned_not_walked": len(report["planned_not_walked"]),
        "string_differs": len(report["string_differs"]), "multi_spelled": len(report["multi_spelled"]),
        "meanings_answered_with_two_bodies": sum(1 for w in walked.values() if len(w["sha256"]) > 1),
        "hand_written": f"{sum(1 for h in report['hand_written'] if h['equal'])} of {len(report['hand_written'])} equal",
        "jwst_nircam": f"{sum(1 for j in report['jwst_nircam'] if j['equal'])} of {len(report['jwst_nircam'])} walked and equal",
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=1, default=sorted) + "\n", encoding="utf-8", newline="\n")
    for k2, v in report["summary"].items():
        log(f"{k2}: {v}")
    if args.write_fixture:
        rerecord(doc, walked, fixture, report, args)
    return 0


def rerecord(doc: dict[str, Any], walked: dict[str, Any], fixture: dict[str, Any], report: dict[str, Any],
             args: argparse.Namespace) -> None:
    """The fixture re-recorded conservatively from the walk, only where the walk confirms every hand-written string:
    every existing entry keeps its place and its string; an entry the walk reproduced takes the walk's bytes; an
    entry the walk did not visit stays as it was, marked ``walked: S73``; a galaxy-scale meaning new to the file and
    in the plan is appended; one the plan does not hold is not a request the bundles answer - it goes to ``unplanned``
    with the step it was asked at, for the test to state (S95, F-W-1); the two "by hand, no walk run" walks entries
    give way to this walk's."""
    if report["string_differs"] or any(h["equal"] is not True for h in report["hand_written"]) \
            or any(not j["equal"] for j in report["jwst_nircam"]):
        log("NOT re-recorded: a hand-written or jwst_nircam string is not the walk's (see the report)")
        return
    requests = []
    for k, f in fixture.items():
        r = dict(f["record"])
        if k in walked:
            r["bytes"] = walked[k]["record"]["bytes"]
            r.pop("walked", None)
        else:
            r["walked"] = "S73"
        requests.append(r)
    planned = plan_of(args.bundles)
    added = [w["record"] for k, w in walked.items() if k not in fixture and k in planned]
    unplanned = [w["record"] | {"steps": w["steps"]} for k, w in walked.items() if k not in fixture and k not in planned]
    requests.extend(added)
    walks = [w for w in doc["walks"] if "no walk run" not in w["by"]]
    walks.append({
        "session": "S95", "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "by": "tools/walk_requests.py (S95, Audit VI F-4-1; frontend/e2e/walk/walk.probe.ts)",
        "covered": args.covered or "",
    })
    out = OrderedDict(doc)
    if args.about:
        out["about"] = args.about
    out["walks"] = walks
    out["requests"] = requests
    out["unplanned"] = unplanned
    FIXTURE.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    log(f"fixture re-recorded: {len(requests)} entries ({len(added)} new, {len(unplanned)} unplanned, "
        f"{sum(1 for r in requests if r.get('walked') == 'S73')} not re-walked, kept as S73's)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("serve", "walk", "reduce"):
        p = sub.add_parser(name)
        p.add_argument("--log", type=Path, required=True, help="the JSON-lines log of every answer")
        p.add_argument("--bundles", type=Path, default=Path(os.environ["GALAXY_BUNDLES"]) if os.environ.get("GALAXY_BUNDLES") else None)
        if name in ("serve", "walk"):
            p.add_argument("--port", type=int, default=PORT)
            p.add_argument("--client", type=Path, default=FRONTEND / "dist")
        if name in ("walk", "reduce"):
            p.add_argument("--report", type=Path, default=None, help="the three-way diff as JSON")
            p.add_argument("--write-fixture", action="store_true", help="re-record the fixture (only if every string matches)")
            p.add_argument("--covered", default="", help="the walks entry's text when re-recording")
            p.add_argument("--about", default="", help="the fixture's about text when re-recording (default: kept)")
        if name == "walk":
            p.add_argument("--only", default="", help="GALAXYGEN_WALK_ONLY: a comma list of the walk's parts to run")
    args = parser.parse_args(argv)
    if getattr(args, "write_fixture", False) and args.bundles is None:
        # S95 (review N-8): without the bundles the plan is empty - every new meaning would go to ``unplanned`` and
        # the jwst_nircam guard in rerecord would hold vacuously - so the fixture is never re-recorded without them.
        parser.error("--write-fixture needs --bundles (or GALAXY_BUNDLES): the plan is empty without them")
    return {"serve": serve, "walk": walk, "reduce": reduce}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
