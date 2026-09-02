"""determinism: reproducible given all arguments (rule A10), per model and per region.

Two properties, both checked empirically rather than assumed:

- **Per model.** Running a model twice with the same inputs, seeds and grid gives
  bit-identical fields. A stage that reaches for an unseeded global RNG, wall
  clock or dictionary-order accident fails here.
- **Per region.** ``child(seed, object_id)`` and ``rng(seed, object_id)`` are
  pure functions of their arguments, so the result for one object cannot depend
  on which objects were generated before it, or whether any others were
  generated at all. The check generates a population in two orders and compares.

Three golden values pin the derivation. If numpy changes its Generator streams,
``GOLDEN_DRAW`` fails; that is the instrument working, not a nuisance. Update it
deliberately, with a DECISIONS.md entry, and re-examine anything calibrated
under the old stream (rule B10).
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

from galaxy.core import seeds
from galaxy.core.grids import GridSpec
from galaxy.core.registry import Input, Model, Registry, production
from galaxy.core.stage import Stage
from galaxy.specs import Problem, utf8_stdout

# Computed at S0 under numpy 2.5.2, Python 3.14.4 [verified: recorded when written].
GOLDEN_STABLE_INT = 14449045403633997470  # seeds.stable_int("galaxy")
GOLDEN_CHILD = 8756915065166511446  # seeds.child(0, "stub", 7)
GOLDEN_DRAW = 0.45544494417321946  # seeds.rng(12345, "golden").random()

SMALL = GridSpec(n_R=16, n_t=8, n_z=4, n_phi=6)


def _equal(a: Any, b: Any) -> bool:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        a = np.asarray(a)
        b = np.asarray(b)
        if a.shape != b.shape or a.dtype != b.dtype:
            return False
        return bool(np.array_equal(a, b, equal_nan=bool(np.issubdtype(a.dtype, np.floating))))
    return type(a) is type(b) and bool(a == b)


def check_reproducible(
    model: Model,
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
    grid: GridSpec = SMALL,
    inputs: Mapping[str, Any] | None = None,
) -> list[Problem]:
    from galaxy.run import run

    a = run(model, inputs, grid, impls=impls, table=table)
    b = run(model, inputs, grid, impls=impls, table=table)
    problems: list[Problem] = []
    if a.order != b.order:
        problems.append(Problem(model.name, "irreproducible", f"stage order differs: {a.order} vs {b.order}"))
    for name, value in a.fields.items():
        if name not in b.fields or not _equal(value, b.fields[name]):
            problems.append(Problem(model.name, "irreproducible", f"field {name!r} differs between two identical runs"))
    return problems


def check_region(seed: int = 0, n: int = 512) -> list[Problem]:
    """Per-region determinism: derivation is order-independent and collision-free on a sample."""
    ids = [int(i) for i in range(n)]
    perm = [int(i) for i in np.random.default_rng(1).permutation(n)]  # the shuffle is this check's, not the model's
    problems: list[Problem] = []

    forward = {i: seeds.child(seed, i) for i in ids}
    shuffled = {i: seeds.child(seed, i) for i in perm}
    if forward != shuffled:
        problems.append(Problem("*", "order-dependent", "child seeds differ when objects are generated in a different order"))
    if len(set(forward.values())) != n:
        problems.append(Problem("*", "collision", f"{n - len(set(forward.values()))} child-seed collision(s) among {n} ids"))
    if seeds.child(seed, 5) != forward[5]:
        problems.append(Problem("*", "order-dependent", "a child seed generated alone differs from the same id in a batch"))
    if seeds.child(seed + 1, 0) == seeds.child(seed, 0):
        problems.append(Problem("*", "seed-insensitive", "changing the seed did not change the child"))

    draws = {i: seeds.rng(seed, i).random() for i in ids}
    draws_shuffled = {i: seeds.rng(seed, i).random() for i in perm}
    if draws != draws_shuffled:
        problems.append(Problem("*", "order-dependent", "first draws differ when objects are generated in a different order"))
    return problems


def check_golden() -> list[Problem]:
    problems: list[Problem] = []
    if seeds.stable_int("galaxy") != GOLDEN_STABLE_INT:
        problems.append(Problem("*", "golden", f"stable_int drifted: {seeds.stable_int('galaxy')} != {GOLDEN_STABLE_INT}"))
    if seeds.child(0, "stub", 7) != GOLDEN_CHILD:
        problems.append(Problem("*", "golden", f"child drifted: {seeds.child(0, 'stub', 7)} != {GOLDEN_CHILD}"))
    draw = seeds.rng(12345, "golden").random()
    if draw != GOLDEN_DRAW:
        problems.append(Problem("*", "golden", f"Generator stream drifted: {draw!r} != {GOLDEN_DRAW!r} (numpy {np.__version__}); see module docstring"))
    return problems


def check(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
    grid: GridSpec = SMALL,
) -> list[Problem]:
    out = check_golden() + check_region()
    for m in models:
        out.extend(check_reproducible(m, impls, table, grid))
    return out


def report(
    models: Iterable[Model],
    impls: Registry[Stage] | Mapping[str, Stage],
    table: Mapping[str, Input],
    grid: GridSpec = SMALL,
) -> str:
    models = list(models)
    lines = ["determinism"]
    g = check_golden()
    lines.append("  golden values: " + ("OK" if not g else "FAIL"))
    r = check_region()
    lines.append("  per-region (order-independent child seeds): " + ("OK" if not r else "FAIL"))
    for m in models:
        p = check_reproducible(m, impls, table, grid)
        lines.append(f"  model {m.name}: reproducible " + ("OK" if not p else "FAIL"))
    for p in g + r + [q for m in models for q in check_reproducible(m, impls, table, grid)]:
        lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, impls, table = production()
    print(report(models, impls, table))
    return 1 if check(models, impls, table) else 0


if __name__ == "__main__":
    sys.exit(main())
