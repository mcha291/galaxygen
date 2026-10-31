"""Stand the site locally and run the smoothness probe in three states (S76, BUILD_IV Phase W5; D240 R1-R3).

    uv run python tools/smoothness.py --bundles <dir>                  # the local stand, three states, five runs each
    uv run python tools/smoothness.py --bundles <dir> --no-build       # the viewer already built (frontend/dist)
    uv run python tools/smoothness.py --url https://<site>             # the deployed site: the warm state only

The probe is ``frontend/e2e/smooth/smooth.probe.ts`` (``npm --prefix frontend run smooth``); this script stands what
it measures and restarts it between runs. Locally (R3, S74's stand): the viewer built by ``vite build``; the model
``python -m galaxy.api --port 8050 --client frontend/dist --bundles <dir> --verbose --source-log <out>/model-source.log``
run with this interpreter (the venv's python, as the image runs it, not through ``uv run``); the gateway published
once (``dotnet publish -c Release``) and run as ``dotnet Galaxygen.Gateway.dll`` on :8060, pinned to the live
``model.hash``, ``Frontend:Path`` the built viewer, ``ASPNETCORE_ENVIRONMENT=Production``. If 8050 or 8060 answers,
the pair 8051/8061 is used and the script says so; a port held by another process is never touched.

The states, in this order (R2), every run on a fresh browser context:
  1. model-cold   - before EACH run the model and the gateway are stopped and started again: the model's process
                    start, its bundle index (every body's sha256 checked) and its first answers; the gateway's cache
                    empty. The model's cold start alone (process start to the first /api answer) is timed each time.
  2. gateway-cold - before EACH run the gateway alone is restarted (its output cache empty, #205's case) against the
                    model the previous state left warm.
  3. warm         - nothing restarted: the gateway's cache as the last gateway-cold run filled it, five runs in one
                    browser session (each a fresh context).
The model's source log is cut per step by markers the probe asks of the model directly (``/api/version?capture=``),
so each step's model answers are counted by route and source (``bundle`` or ``model``). Everything is written under
``--out`` (default: ``<bundles>/../smooth``): each run's JSON, the merged ``smooth-<state>.json``, ``summary.json``,
``table.md``, and the processes' logs. Every process started here is stopped at the end, on failure and on Ctrl-C.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
GATEWAY = ROOT / "gateway" / "Galaxygen.Gateway"
STATES = ("model-cold", "gateway-cold", "warm")
STEPS = ("first_paint", "switch_to_ngc_4414", "switch_back", "mode_stars", "zoom")
# Ruling 10's bound, seconds per step: warm, cold.
BOUND = {"warm": 1.0, "cold": 5.0}


def log(msg: str) -> None:
    print(msg, flush=True)


def get(url: str, timeout: float = 5.0) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def listening(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


class Proc:
    """A process started here, its output timestamped into a log; stopped with its whole tree, and only it."""

    def __init__(self, name: str, argv: list[str], logfile: Path, cwd: Path, env: dict[str, str] | None = None):
        self.name = name
        self.lines: list[tuple[float, str]] = []
        self.started = time.perf_counter()
        self.log = logfile.open("a", encoding="utf-8", newline="\n")
        self.log.write(f"=== {time.strftime('%H:%M:%S')} start {' '.join(argv)}\n")
        self.p = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
        RUNNING.append(self)
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self) -> None:
        assert self.p.stdout is not None
        for line in self.p.stdout:
            t = time.perf_counter() - self.started
            self.lines.append((t, line.rstrip()))
            self.log.write(f"{t:9.3f} {line}")
            self.log.flush()

    def first(self, text: str) -> float | None:
        return next((t for t, line in list(self.lines) if text in line), None)

    def stop(self) -> None:
        if self.p.poll() is None:
            subprocess.run(["taskkill", "/PID", str(self.p.pid), "/T", "/F"], capture_output=True)
            try:
                self.p.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.p.kill()
        self.reader.join(timeout=5)
        self.log.write(f"=== {time.strftime('%H:%M:%S')} stopped, exit {self.p.returncode}\n")
        self.log.close()
        if self in RUNNING:
            RUNNING.remove(self)


RUNNING: list[Proc] = []


def stop_all() -> None:
    for p in list(RUNNING):
        p.stop()


def wait_for(check, what: str, timeout: float, proc: Proc | None = None, every: float = 0.05) -> float:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        if proc is not None and proc.p.poll() is not None:
            raise RuntimeError(f"{what}: the process exited with {proc.p.returncode}")
        try:
            if check():
                return time.perf_counter() - start
        except (OSError, urllib.error.URLError, ValueError):
            pass
        time.sleep(every)
    raise RuntimeError(f"{what}: not within {timeout} s")


class Stand:
    def __init__(self, args, out: Path):
        self.args = args
        self.out = out
        self.model: Proc | None = None
        self.gateway: Proc | None = None
        self.hash = ""
        self.cold_starts: list[dict[str, Any]] = []
        self.gateway_starts: list[float] = []
        self.mport, self.gport = 8050, 8060
        if listening(8050) or listening(8060):
            self.mport, self.gport = 8051, 8061
            log("8050 or 8060 answers (not ours): using 8051/8061")
            if listening(8051) or listening(8061):
                raise SystemExit("8051 or 8061 answers too: refusing to stand anything")
        self.model_url = f"http://127.0.0.1:{self.mport}"
        self.site = f"http://127.0.0.1:{self.gport}"
        self.source_log = out / "model-source.log"
        self.published = out / "gateway-publish"

    def publish_gateway(self) -> None:
        dotnet = shutil.which("dotnet") or "dotnet"
        t = time.perf_counter()
        r = subprocess.run([dotnet, "publish", str(GATEWAY), "-c", "Release", "-o", str(self.published), "--nologo"],
                           capture_output=True, text=True)
        (self.out / "gateway-publish.log").write_text(r.stdout + r.stderr, encoding="utf-8", newline="\n")
        if r.returncode != 0:
            raise SystemExit(f"dotnet publish failed ({r.returncode}): see {self.out / 'gateway-publish.log'}")
        log(f"gateway published in {time.perf_counter() - t:.1f} s to {self.published}")

    def start_model(self) -> dict[str, Any]:
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        argv = [sys.executable, "-m", "galaxy.api", "--port", str(self.mport), "--client", str(FRONTEND / "dist"),
                "--bundles", str(self.args.bundles), "--verbose", "--source-log", str(self.source_log)]
        self.model = Proc("model", argv, self.out / "model.log", ROOT, env)
        wait_for(lambda: get(f"{self.model_url}/api", 1.0)[0] == 200, "the model's /api", 180, self.model)
        # G4: the process's start to its first /api answer, from the Popen (Proc.started), as the row labels it.
        first = time.perf_counter() - self.model.started
        cold = {"first_api_s": round(first, 3), "bundles_line_s": self.model.first("; bundles "),
                "listening_line_s": self.model.first("galaxy.api on http")}
        status, body = get(f"{self.model_url}/api/version")
        self.hash = json.loads(body)["model"]["hash"]
        self.cold_starts.append(cold)
        log(f"model up on :{self.mport} in {first:.2f} s (bundle index read at {cold['bundles_line_s']} s), hash {self.hash}")
        return cold

    def start_gateway(self) -> float:
        dotnet = shutil.which("dotnet") or "dotnet"
        env = {**os.environ, "ASPNETCORE_URLS": self.site, "ASPNETCORE_ENVIRONMENT": "Production",
               "Gateway__Model__BaseUrl": self.model_url, "Gateway__Model__ContentHash": self.hash,
               "Gateway__Frontend__Path": str(FRONTEND / "dist")}
        self.gateway = Proc("gateway", [dotnet, str(self.published / "Galaxygen.Gateway.dll")], self.out / "gateway.log",
                            self.published, env)

        def ready() -> bool:
            status, body = get(f"{self.site}/healthz", 1.0)
            h = json.loads(body)
            return status == 200 and h.get("pinned") is True and h.get("frontend") is True

        wait_for(ready, "the gateway's /healthz", 60, self.gateway)
        # G4: the process's start to /healthz 200 (pinned, the frontend found), from the Popen.
        took = time.perf_counter() - self.gateway.started
        self.gateway_starts.append(round(took, 3))
        log(f"gateway up on :{self.gport} in {took:.2f} s, pinned {self.hash}")
        return took

    def stop_gateway(self) -> None:
        if self.gateway:
            self.gateway.stop()
            self.gateway = None

    def stop_model(self) -> None:
        if self.model:
            self.model.stop()
            self.model = None


def probe(out: Path, site: str, state: str, runs: int, base: int, model_url: str = "") -> dict[str, Any]:
    """One invocation of the probe; its JSON and its exit code."""
    raw = out / "raw" / f"{state}-{base}.json"
    npx = shutil.which("npx") or "npx"
    env = {**os.environ, "GALAXYGEN_URL": site, "GALAXYGEN_RUNS": str(runs), "GALAXYGEN_RUN_BASE": str(base),
           "GALAXYGEN_STATE": state, "GALAXYGEN_OUT": str(raw), "GALAXYGEN_MODEL_URL": model_url}
    with (out / "probe.log").open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"=== {time.strftime('%H:%M:%S')} {state} runs {base}..{base + runs - 1}\n")
        f.flush()
        r = subprocess.run([npx, "playwright", "test", "-c", "playwright.smooth.config.ts"], cwd=FRONTEND, env=env,
                           stdout=f, stderr=subprocess.STDOUT)
        f.write(f"=== exit {r.returncode}\n")
    got = json.loads(raw.read_text(encoding="utf-8")) if raw.is_file() else {"runs": []}
    got["exit"] = r.returncode
    log(f"{state} runs {base}..{base + runs - 1}: probe exit {r.returncode}, {len(got['runs'])} run(s) recorded")
    return got


def model_lines(source_log: Path) -> dict[str, dict[str, Any]]:
    """Each probe step's model answers, cut from the source log by the probe's begin and end markers."""
    if not source_log.is_file():
        return {}
    steps: dict[str, dict[str, Any]] = {}
    open_label = None
    for line in source_log.read_text(encoding="utf-8").splitlines():
        e = json.loads(line)
        q = e.get("query", "")
        if q.startswith("capture=smooth-"):
            label = q[len("capture="):]
            if label.endswith("-begin"):
                open_label = label[: -len("-begin")]
                steps[open_label] = {"lines": 0, "by_source": {}, "by_route": {}, "bytes": 0}
            elif label.endswith("-end"):
                open_label = None
            continue
        if open_label is None:
            continue
        s = steps[open_label]
        s["lines"] += 1
        s["bytes"] += e.get("bytes", 0)
        s["by_source"][e.get("source")] = s["by_source"].get(e.get("source"), 0) + 1
        key = f"{e.get('path')} {e.get('source')}"
        s["by_route"][key] = s["by_route"].get(key, 0) + 1
    return steps


def med(xs: list[float]) -> float | None:
    return statistics.median(xs) if xs else None


def fmt(ms: float | None) -> str:
    return "-" if ms is None else f"{ms / 1000:.2f}"


def starts_label(state: str, step: str, runs: list[dict[str, Any]]) -> str:
    """The cold rows' first paint with the processes' starts beside it (S76's review, G4): the probe's clock starts at
    the navigation, after the runner has started the processes and seen them answer (the model's /api and /api/version,
    the gateway's /healthz - readiness checks, not the step's), so a new visitor's wait on a cold stand is the first
    paint plus these: the model's process start to its first /api answer, the gateway's start to /healthz 200."""
    if step != "first_paint":
        return ""
    st = [r["starts"] for r in runs if r.get("starts")]
    if not st:
        return ""
    g = med([x["gateway_s"] for x in st])
    if state == "model-cold" and all("model_s" in x for x in st):
        m = med([x["model_s"] for x in st])
        return f" + starts {m + g:.2f} s (model {m:.2f}, gateway {g:.2f}; medians)"
    return f" + starts {g:.2f} s (gateway; median)"


def table(merged: dict[str, dict[str, Any]]) -> str:
    rows = ["| state | step | ready s median, from the bracket's lower end (range) [n ok] | api wait s | long tasks inside the api wait s | client s (lower bound) | after last /api s | long tasks s | /api reqs "
            "| longest /api (route, s, KB, cache/source) | healthz max in_flight/waiting | model lines (by source) "
            "| bound |", "|" + "---|" * 13]
    for state, data in merged.items():
        for step in STEPS:
            got = [s for r in data["runs"] for s in r["steps"] if s["step"] == step]
            if not got:
                continue
            ok = [s for s in got if s["ready_ms"] is not None]
            ready = [s["ready_ms"] for s in ok]
            pick = lambda k: med([s.get(k) for s in ok if s.get(k) is not None])  # noqa: E731
            longest = max((s["longest"] for s in ok if s["longest"]), key=lambda x: x["ms"], default=None)
            lng = "-" if not longest else (f"{longest['route']} {longest['ms'] / 1000:.2f}, "
                                           f"{(longest['bytes'] or 0) / 1024:.0f}, {longest['cache']}/{longest['source']}")
            hz_in = max((s["healthz"]["inFlight"] for s in got), default=0)
            hz_w = max((s["healthz"]["waiting"] for s in got), default=0)
            ml = [s.get("model", {}) for s in got]
            lines = med([m.get("lines", 0) for m in ml])
            src: dict[str, int] = {}
            for m in ml:
                for k, v in m.get("by_source", {}).items():
                    src[k] = src.get(k, 0) + v
            src_s = ", ".join(f"{k} {v}" for k, v in sorted(src.items(), key=lambda kv: str(kv[0])))
            bound = BOUND["warm" if state == "warm" else "cold"] * 1000
            over = sum(1 for x in ready if x > bound)
            rng = f"{min(ready) / 1000:.2f}-{max(ready) / 1000:.2f}" if ready else "-"
            lo = fmt(pick("ready_lo_ms"))
            # G8: a run whose frame sum changed in the second after the confirmation is starred, with how many did.
            moved = sum(1 for s in ok if s.get("after_confirm", {}).get("changed"))
            star = f"* ({moved} moved after)" if moved else ""
            rows.append(f"| {state} | {step}{starts_label(state, step, data['runs'])} | {fmt(med(ready))}{star} from {lo} ({rng}) [{len(ok)}/{len(got)}] | {fmt(pick('api_wait_ms'))} "
                        f"| {fmt(pick('api_long_tasks_ms'))} | {fmt(pick('client_ms'))} | {fmt(pick('after_last_api_ms'))} | {fmt(med([s['long_tasks']['ms'] for s in ok]))} | {med([s['api_requests'] for s in ok])} "
                        f"| {lng} | {hz_in}/{hz_w} | {lines} ({src_s}) | {over}/{len(ready)} over {bound / 1000:.0f} s |")
    return "\n".join(rows) + "\n\n" + probe_cost(merged)


def probe_cost(merged: dict[str, dict[str, Any]]) -> str:
    """The probe's own cost (S76's review, G1): ms a call in the page, median over every probe of every step, and the
    duty cycle it is of the probe's interval - the share of the page's main thread the instrument takes."""
    costs = [c for d in merged.values() for r in d["runs"] for s in r["steps"] for c in s["probes"].get("costs", [])]
    trips = [s["probes"].get("round_trip_ms_median") for d in merged.values() for r in d["runs"] for s in r["steps"]]
    trips = [t for t in trips if t is not None]
    intervals = [s["probes"].get("interval_ms_median") for d in merged.values() for r in d["runs"] for s in r["steps"]]
    every = med([i for i in intervals if i is not None]) or 250.0
    if not costs:
        return "the probe's cost: no probe recorded"
    c = med(costs)
    cs = sorted(costs)
    return (f"the probe: every {every:.0f} ms (median interval); its own cost {c:.0f} ms a call in the page (median of "
            f"{len(costs)}, 90th percentile {cs[int(0.9 * (len(cs) - 1))]:.0f}, at most {cs[-1]:.0f}), round trip "
            f"{med(trips):.0f} ms: a duty cycle of {100 * c / every:.0f} % of the page's main thread. The ready column is the "
            f"bracket's upper end (the first probe of the final still run), its lower end beside it (the last probe that differed); "
            f"* marks a step whose frame sum changed in the second probed after settle's criteria held. The api wait is the "
            f"union of the time any /api request was in flight, not the critical path: the long tasks inside it were client "
            f"work too, so the client column (ready less the api wait) is a lower bound on the client's share.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bundles", type=Path, help="the template bundles (exported here if missing or empty)")
    parser.add_argument("--url", help="a deployed site: the warm state only, nothing stood or restarted")
    parser.add_argument("--out", type=Path, help="where results and logs go (default <bundles>/../smooth)")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--states", default=",".join(STATES), help="comma-separated, in the order run")
    parser.add_argument("--no-build", action="store_true", help="use frontend/dist as it is")
    args = parser.parse_args(argv)
    if not args.url and not args.bundles:
        parser.error("--bundles is needed for the local stand (or --url for a deployed site)")
    out = args.out or (args.bundles.resolve().parent / "smooth" if args.bundles else Path(tempfile.gettempdir()) / "galaxygen-smooth")
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw").mkdir(exist_ok=True)
    states = [s for s in args.states.split(",") if s]
    merged: dict[str, dict[str, Any]] = {}
    summary: dict[str, Any] = {"out": str(out), "runs": args.runs, "states": states}

    if args.url:
        site = args.url.rstrip("/")
        status, body = get(f"{site}/healthz")
        log(f"healthz {status}: {body[:600].decode('utf-8', 'replace')}")
        merged["warm"] = probe(out, site, "warm", args.runs, 1)
        summary["site"] = site
    else:
        if not args.bundles.is_dir() or not any(args.bundles.iterdir()):
            log(f"exporting the bundles to {args.bundles} (both templates, both layer settings)")
            subprocess.run([sys.executable, str(ROOT / "tools" / "export_template.py"), "--out", str(args.bundles)],
                           cwd=ROOT, check=True)
        if not args.no_build:
            npm = shutil.which("npm") or "npm"
            t = time.perf_counter()
            subprocess.run([npm, "--prefix", str(FRONTEND), "run", "build"], cwd=ROOT, check=True,
                           stdout=subprocess.DEVNULL)
            log(f"viewer built in {time.perf_counter() - t:.1f} s")
        if (out / "model-source.log").exists():
            (out / "model-source.log").unlink()
        stand = Stand(args, out)
        summary["site"] = stand.site
        try:
            stand.publish_gateway()
            stand.start_model()
            stand.start_gateway()
            status, body = get(f"{stand.site}/healthz")
            log(f"healthz {status}: {body.decode('utf-8', 'replace')}")
            summary["healthz_once"] = json.loads(body)
            for state in states:
                runs: list[dict[str, Any]] = []
                exits: list[int] = []
                if state == "warm":
                    got = probe(out, stand.site, state, args.runs, 1, stand.model_url)
                    runs += got["runs"]
                    exits.append(got["exit"])
                else:
                    for i in range(1, args.runs + 1):
                        stand.stop_gateway()
                        starts: dict[str, float] = {}
                        if state == "model-cold":
                            stand.stop_model()
                            starts["model_s"] = stand.start_model()["first_api_s"]
                        starts["gateway_s"] = round(stand.start_gateway(), 3)
                        got = probe(out, stand.site, state, 1, i, stand.model_url)
                        for r in got["runs"]:
                            r["starts"] = starts  # G4: the processes' starts before this run, the runner's own readiness checks
                        runs += got["runs"]
                        exits.append(got["exit"])
                merged[state] = {"runs": runs, "exits": exits}
            summary["model_cold_starts"] = stand.cold_starts
            summary["gateway_starts_s"] = stand.gateway_starts
            summary["hash"] = stand.hash
        finally:
            stop_all()
        lines = model_lines(stand.source_log)
        for state, data in merged.items():
            for r in data["runs"]:
                for s in r["steps"]:
                    s["model"] = lines.get(f"smooth-{state}-{r['run']}-{s['step']}", {})

    for state, data in merged.items():
        (out / f"smooth-{state}.json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8", newline="\n")
    md = table(merged)
    (out / "table.md").write_text(md + "\n", encoding="utf-8", newline="\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    log("\n" + md)
    if summary.get("model_cold_starts"):
        log("\nthe model's cold start alone (s): " + json.dumps(summary["model_cold_starts"]))
        log("the gateway's start (s): " + json.dumps(summary["gateway_starts_s"]))
    log(f"\nwritten under {out}")
    return 0 if all(e == 0 for d in merged.values() for e in d.get("exits", [d.get("exit", 0)])) else 1


if __name__ == "__main__":
    raise SystemExit(main())
