"""``python -m galaxy.specs``: every executable spec against the production registries.

Exit status is non-zero if any spec reports a problem or any acceptance
quantity fails. Not-yet-computable quantities do not fail the run.
"""

from __future__ import annotations

import sys

from galaxy.core.registry import production
from galaxy.specs import determinism, graph, preflight, spec, utf8_stdout


def main() -> int:
    utf8_stdout()
    models, impls, table = production()
    models = list(models)
    bad = False

    print(graph.report(models, impls, table))
    bad |= bool(graph.check(models, impls, table))

    print(preflight.report(models, impls, table))
    bad |= not preflight.check(models, impls, table).ok

    print(determinism.report(models, impls, table))
    bad |= bool(determinism.check(models, impls, table))

    print(spec.report(models))
    bad |= any(r.status == "fail" for m in models for r in spec.run(m))

    print("specs:", "FAIL" if bad else "OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
