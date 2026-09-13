"""``python -m galaxy.models``: every registered model side by side.

One row per stage slot, one column per model; ``*`` marks a slot where the
models do not all map the same implementation. Below it, each model's own
constants: the ones not in LEVEL0, and LEVEL0 values it overrides.
"""

from __future__ import annotations

import sys

from galaxy.core.registry import production
from galaxy.models import DEFAULT
from galaxy.models.level0 import LEVEL0
from galaxy.specs import utf8_stdout


def slot_table(models) -> list[str]:
    slots: list[str] = []
    for m in models:
        slots += [s for s, _ in m.stages if s not in slots]
    header = ["", "slot", *(m.name + (" (default)" if m.name == DEFAULT else "") for m in models)]
    rows = []
    for slot in slots:
        impls = [m.stage_map.get(slot, "-") for m in models]
        rows.append(["*" if len(set(impls)) > 1 else "", slot, *impls])
    widths = [max(len(r[i]) for r in [header, *rows]) for i in range(len(header))]
    line = lambda r: "  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip()  # noqa: E731
    return [line(header), line(["-" * w for w in widths]), *map(line, rows)]


def own_constants(model) -> list[str]:
    out = []
    for name, c in model.constants.items():
        if name not in LEVEL0:
            out.append(f"    {name} = {c.value:g} {c.unit}")
        elif c.value != LEVEL0[name].value:
            out.append(f"    {name} = {c.value:g} {c.unit}  (LEVEL0: {LEVEL0[name].value:g})")
    return out or ["    (none beyond LEVEL0)"]


def main() -> int:
    utf8_stdout()
    models = list(production()[0])
    print("\n".join(slot_table(models)))
    for m in models:
        print(f"\n{m.name}: own constants")
        print("\n".join(own_constants(m)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
