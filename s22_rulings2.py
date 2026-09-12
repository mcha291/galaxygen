"""S22 scratch, part 2: row 3's grid drift, the wind pin here, the detector's margins."""
from __future__ import annotations

import json
import math

import numpy as np

from galaxy.core.registry import production
from galaxy.specs import convergence, spec

_M, _, _ = production()
simple, advanced = _M.get("simple"), _M.get("advanced")
out: dict = {}

# --- debt #11 / row 3: the 0.03 km/s miss against the grid's own effect on the row.
rep = convergence.sweep(simple)
Q = {q.n: q for q in spec.QUANTITIES}
for n in (3, 5, 9, 11):
    q = Q[n]
    ds = [d for d in rep.drifts if d.row == n]
    if not ds:
        continue
    default = ds[0].default
    edge = min(abs(default - q.lo), abs(default - q.hi)) if q.lo is not None else float("nan")
    out.setdefault("grid", {})[n] = {
        "default": default, "target": [q.lo, q.hi], "width": q.hi - q.lo,
        "distance to nearest edge": edge,
        "drift": {d.axis: {"drift": d.drift, "values": {str(k): v for k, v in d.values.items()}} for d in ds},
        "largest drift": max(d.drift for d in ds),
    }
    print(n, json.dumps(out["grid"][n], indent=1), flush=True)

# --- debt #70 x A-4: the detector's margin, on the only mode this project has opened.
from galaxy.stages.chemistry_dtd import ALPHA_HIST, MODE_MIN_SHARE, PEAK_SEPARATION

lo, hi, width = ALPHA_HIST
out["detector"] = {"ALPHA_HIST": [lo, hi, width], "MODE_MIN_SHARE": MODE_MIN_SHARE,
                   "PEAK_SEPARATION": PEAK_SEPARATION}
# reach: the widest sigma a Gaussian mode of share s can have and still be kept
def reach(s: float) -> float | None:
    target = MODE_MIN_SHARE / s
    if target >= 1.0:
        return None
    # s * erf(0.05/(sigma sqrt2)) = 0.1  ->  sigma = 0.05 / (sqrt2 * erfinv(target))
    from scipy.special import erfinv  # noqa
    return 0.5 * PEAK_SEPARATION / (math.sqrt(2.0) * float(erfinv(target)))
try:
    out["detector"]["reach"] = {f"{s:.2f}": reach(s) for s in (0.05, 0.10, 0.103, 0.12, 0.15, 0.20, 0.30)}
except Exception as e:  # no scipy in this project
    # bisect instead
    def reach2(s: float) -> float | None:
        f = lambda sig: s * math.erf(0.5 * PEAK_SEPARATION / (sig * math.sqrt(2.0))) - MODE_MIN_SHARE
        if f(1e-6) < 0:
            return None
        a, b = 1e-6, 5.0
        for _ in range(200):
            m = 0.5 * (a + b)
            if f(m) > 0:
                a = m
            else:
                b = m
        return 0.5 * (a + b)
    out["detector"]["reach"] = {f"{s:.3f}": reach2(s) for s in (0.05, 0.10, 0.103, 0.12, 0.15, 0.20, 0.30)}
print("detector reach:", json.dumps(out["detector"]["reach"], indent=1), flush=True)
json.dump(out, open("s22_rulings2.json", "w"), indent=1)
