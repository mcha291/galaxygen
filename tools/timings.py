"""Cold timings for every API route, measured from a fresh process (rule B2).

    uv run python tools/timings.py            # the table, to paste into DECISIONS.md
    uv run python tools/timings.py --json     # the same numbers as JSON

**Why a subprocess per measurement.** A cache turns a measurement into a reading
of the cache, and the caches that matter here are not only the service's own: an
imported module, a numpy array still in the allocator, a galaxy already resolved.
The only way to measure the first request is to make it the first request, so
each endpoint is measured in its own interpreter, which then makes the same
request a second time to report what a warm one costs.

**Publish the number, not the verdict** (rule B6). The table carries the cold
seconds, the warm seconds, their ratio and the bytes returned; whether that is
fast enough is a judgement someone can disagree with from the same numbers. A
ratio near 1 says there was no cache to read, which is the honest way to say a
cold measurement was not a warm one in disguise.

Every route in ``galaxy.api.service.routes()`` must appear here, and
``tests/test_api.py`` fails if one does not: a new endpoint that nobody measured
is exactly the omission rule B2 exists to prevent (rule B13).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Endpoint:
    name: str
    route: str
    query: str = ""
    about: str = ""


ENDPOINTS: tuple[Endpoint, ...] = (
    Endpoint("viewer: index.html", "/", "", "the page itself, off disk"),
    Endpoint("viewer: a module", "/app.js", "", "one file beside it"),
    Endpoint("index", "/api", "", "the route table"),
    Endpoint("version", "/api/version", "", "hashes the client bytes on every request (D3)"),
    Endpoint("stages", "/api/stages", "", "12 stage declarations"),
    Endpoint("fields", "/api/fields", "", "every field declaration, with its ramp"),
    Endpoint("inputs", "/api/inputs", "", "7 controls, 4 seeds, 1 event list"),
    Endpoint("arrays: one profile", "/api/arrays", "fields=stellar_surface_density", "400 floats, checkpoint 1"),
    Endpoint("arrays: history", "/api/arrays", "fields=feh_history", "400 x 2000, checkpoint 3"),
    Endpoint("arrays: scalar", "/api/arrays", "fields=stellar_mass_total", "one number"),
    Endpoint("region: one sector", "/api/region", "r_min=7&r_max=9&phi_min=0&phi_max=0.4", "9 of 1024 cells"),
    Endpoint("region: whole disc", "/api/region", "stars=20000", "every cell, the published sample"),
    Endpoint("system: one star", "/api/system", "cell=300&index=0", "one cell, one star's planets"),
    # The advanced model, on the routes where its own stages run (S9). Everything
    # upstream of chemistry is shared code, so a profile costs the same in both.
    Endpoint("adv: history", "/api/arrays", "model=advanced&fields=feh_history", "the DTD chemistry"),
    Endpoint("adv: alpha plane", "/api/arrays", "model=advanced&fields=alpha_fe_history,alpha_sequence", "and its verdict"),
    Endpoint("adv: one sector", "/api/region", "model=advanced&r_min=7&r_max=9&phi_min=0&phi_max=0.4", "the chemical split"),
    Endpoint("adv: one star", "/api/system", "model=advanced&cell=300&index=0", "one system, advanced"),
)


def measure(endpoint: Endpoint) -> dict:
    """Time ``endpoint`` in this process, first call and second. Run under a fresh one."""
    start = time.perf_counter()
    from galaxy.api.service import Service

    imported = time.perf_counter() - start

    start = time.perf_counter()
    service = Service()
    built = time.perf_counter() - start

    start = time.perf_counter()
    cold = service.handle(endpoint.route, endpoint.query)
    cold_s = time.perf_counter() - start

    start = time.perf_counter()
    warm = service.handle(endpoint.route, endpoint.query)
    warm_s = time.perf_counter() - start

    if not cold.ok or not warm.ok:
        raise SystemExit(f"{endpoint.route}?{endpoint.query} returned {cold.status}: {cold.body[:200]!r}")
    return {
        "name": endpoint.name,
        "route": endpoint.route,
        "query": endpoint.query,
        "about": endpoint.about,
        "import_s": imported,
        "build_s": built,
        "cold_s": cold_s,
        "warm_s": warm_s,
        "ratio": cold_s / warm_s if warm_s > 0 else float("inf"),
        "bytes": len(cold.body),
        "stages": list(cold.stages),
    }


def run_all() -> list[dict]:
    """One fresh interpreter per endpoint. Nothing is measured twice in one process."""
    out: list[dict] = []
    for i, endpoint in enumerate(ENDPOINTS):
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--one", str(i)],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        if proc.returncode != 0:
            raise SystemExit(f"measuring {endpoint.name} failed:\n{proc.stderr}")
        out.append(json.loads(proc.stdout.splitlines()[-1]))
    return out


def table(rows: list[dict]) -> str:
    head = f"{'endpoint':<22} {'cold s':>8} {'warm s':>8} {'c/w':>6} {'bytes':>10}  stages"
    lines = [head, "-" * len(head)]
    for r in rows:
        stages = ",".join(r["stages"]) or "-"
        lines.append(
            f"{r['name']:<22} {r['cold_s']:>8.4f} {r['warm_s']:>8.4f} {r['ratio']:>6.2f} {r['bytes']:>10,}  {stages}"
        )
    imports = [r["import_s"] for r in rows]
    lines.append("")
    lines.append(
        f"import + registry: {min(imports):.3f}-{max(imports):.3f} s, paid once per process and "
        f"excluded from the cold column"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Cold timings for every API route (rule B2).")
    parser.add_argument("--json", action="store_true", help="print the measurements as JSON")
    parser.add_argument("--one", type=int, help=argparse.SUPPRESS)  # the subprocess entry point
    args = parser.parse_args()

    if args.one is not None:
        print(json.dumps(measure(ENDPOINTS[args.one])))
        return 0

    rows = run_all()
    print(json.dumps(rows, indent=2) if args.json else table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
