"""S22 scratch: the measurements the rulings need. Deleted before the close (C2)."""
from __future__ import annotations

import json
import sys

import numpy as np

from galaxy.core.registry import INPUTS, production
from galaxy.run import run
from galaxy.specs import spec

_MODELS, _, _ = production()
MODELS = [_MODELS.get(n) for n in ('simple', 'advanced')]
SEEDS = tuple(n for n, i in INPUTS.items() if i.kind == "seed")
STAT = [q for q in spec.QUANTITIES if q.mode == "statistical"]
out: dict = {}

# --- debt #51: the pre-committed test. Three disjoint diagonals, every statistical row.
print("statistical rows:", [(q.n, q.field) for q in STAT], flush=True)
diag: dict = {}
for model in MODELS:
    fields = tuple(q.field for q in STAT if q.field)
    for start in (0, 41, 82):
        vals: dict[str, list[float]] = {}
        for d in range(start, start + 41):
            f = run(model, {s: d for s in SEEDS}, only=fields).fields
            for k in fields:
                if k in f:
                    vals.setdefault(k, []).append(float(f[k]))
        for q in STAT:
            if q.field in vals:
                med = float(np.median(vals[q.field]))
                lo, hi = np.percentile(vals[q.field], [2.5, 97.5])
                diag.setdefault(f"{model.name}:{q.n}", []).append(
                    {"seeds": f"{start}-{start + 40}", "median": med,
                     "inside": bool(q.lo <= med <= q.hi), "lo95": float(lo), "hi95": float(hi),
                     "target": [q.lo, q.hi]}
                )
        print(model.name, start, "done", flush=True)
out["diagonals"] = diag
print(json.dumps(diag, indent=1), flush=True)
json.dump(out, open("s22_rulings.json", "w"), indent=1)
