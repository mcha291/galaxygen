"""Scaling exponents in N_t for the two chemistries, and the advanced model's multiplier (rule B7).

    uv run python tools/scaling.py            # the table, to paste into DECISIONS.md
    uv run python tools/scaling.py --json

**Why an exponent and not a stopwatch.** GALAXY_INPUTS.md §10 measured the
naive delay-time distribution — a convolution over every earlier timestep — at
exponent 2.07 in N_t, and a "fix" that truncated the kernel at a fixed physical
window at 1.82: still quadratic, because the number of kernel samples grew with
N_t. Both were fast enough at low resolution; only the exponent told them apart
(rule B7). The advanced chemistry bins the DTD at ``DTD_BINS`` delays whatever
N_t is, and this tool measures whether that bought linearity rather than
asserting it.

**What is timed.** For each N_t the closure below the chemistry slot is run once
and kept; the chemistry stage alone is then timed by resuming from it, so the
number is the stage's and not the star formation history's. Three or more N_t,
a least-squares slope in log–log, published as the exponent. Alongside it, the
naive convolution is timed on the same star formation histories, in this file
rather than in any stage, so the instrument demonstrates it can see the defect
it exists to find (rule B3). ``--quick`` uses fewer grids for a CI-sized check.

**Publish the number, not the verdict** (rule B6). The multiplier column is the
advanced chemistry over the simple one at the default grid, and the whole-model
row is both models end to end, cold in one process each.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from collections.abc import Sequence

import numpy as np

GRIDS: tuple[int, ...] = (500, 1000, 2000, 4000, 8000)
NAIVE_GRIDS: tuple[int, ...] = (250, 500, 1000, 2000)
CHEM = ("metallicity_gradient",)


def exponent(n: Sequence[int], seconds: Sequence[float]) -> float:
    """Least-squares slope of log(seconds) against log(n)."""
    x, y = np.log(np.asarray(n, dtype=float)), np.log(np.asarray(seconds, dtype=float))
    return float(np.polyfit(x, y, 1)[0])


def naive_snia_rate(psi: np.ndarray, dt: float, t_min: float, index: float) -> np.ndarray:
    """The convolution §10 measured at exponent 2.07: every timestep sums over every earlier one."""
    n_t = psi.shape[1]
    tau = np.arange(1, n_t) * dt
    kernel = np.where(tau >= t_min, tau ** -index, 0.0)
    kernel /= kernel.sum() if kernel.sum() > 0 else 1.0
    out = np.zeros_like(psi)
    for j in range(1, n_t):
        out[:, j] = psi[:, :j] @ kernel[j - 1 :: -1][:j]
    return out


def time_stage(model_name: str, n_t: int, repeats: int = 3) -> float:
    """Seconds for the chemistry stage alone at ``n_t``, best of ``repeats``."""
    from galaxy.core.grids import GridSpec
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    model = models.get(model_name)
    grid = GridSpec(n_t=n_t)
    base = run(model, grid=grid, only=("stellar_surface_density", "halo_potential", "circular_velocity_resolved"))
    best = math.inf
    for _ in range(repeats):
        start = time.perf_counter()
        run(model, grid=grid, only=CHEM, resume=base)
        best = min(best, time.perf_counter() - start)
    return best


def time_naive(n_t: int, repeats: int = 2) -> float:
    from galaxy.core.grids import GridSpec
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    model = models.get("advanced")
    base = run(model, grid=GridSpec(n_t=n_t), only=("sfr_surface_density_history",))
    psi = base.fields["sfr_surface_density_history"]
    dt = 13.8 / n_t
    best = math.inf
    for _ in range(repeats):
        start = time.perf_counter()
        naive_snia_rate(psi, dt, 0.15, 1.1)
        best = min(best, time.perf_counter() - start)
    return best


def time_model(model_name: str) -> float:
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    start = time.perf_counter()
    run(models.get(model_name))
    return time.perf_counter() - start


def measure(grids: Sequence[int] = GRIDS, naive_grids: Sequence[int] = NAIVE_GRIDS) -> dict:
    rows = {name: [time_stage(name, n) for n in grids] for name in ("simple", "advanced")}
    naive = [time_naive(n) for n in naive_grids]
    at_default = {name: time_stage(name, 2000) for name in rows}
    return {
        "grids": list(grids),
        "seconds": rows,
        "exponent": {name: exponent(grids, s) for name, s in rows.items()},
        "naive_grids": list(naive_grids),
        "naive_seconds": naive,
        "naive_exponent": exponent(naive_grids, naive),
        "chemistry_multiplier": at_default["advanced"] / at_default["simple"],
        "model_seconds": {name: time_model(name) for name in rows},
    }


def table(m: dict) -> str:
    lines = [f"{'chemistry stage':<18}" + "".join(f"{f'N_t={n}':>12}" for n in m["grids"]) + f"{'exponent':>10}"]
    lines.append("-" * len(lines[0]))
    for name, s in m["seconds"].items():
        lines.append(f"{name:<18}" + "".join(f"{v:>12.4f}" for v in s) + f"{m['exponent'][name]:>10.2f}")
    lines.append("")
    lines.append(f"{'naive DTD (tool)':<18}" + "".join(f"{f'N_t={n}':>12}" for n in m["naive_grids"]) + f"{'exponent':>10}")
    lines.append(f"{'':<18}" + "".join(f"{v:>12.4f}" for v in m["naive_seconds"]) + f"{m['naive_exponent']:>10.2f}")
    lines.append("")
    lines.append(f"advanced chemistry / simple chemistry at N_t = 2000: {m['chemistry_multiplier']:.2f}x")
    ms = m["model_seconds"]
    lines.append(f"whole model, cold: simple {ms['simple']:.3f} s, advanced {ms['advanced']:.3f} s ({ms['advanced'] / ms['simple']:.2f}x)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaling exponents in N_t for the chemistries (rule B7).")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quick", action="store_true", help="three grids, for a check rather than the record")
    args = parser.parse_args()
    m = measure((500, 1000, 2000), (250, 500, 1000)) if args.quick else measure()
    print(json.dumps(m, indent=2) if args.json else table(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
