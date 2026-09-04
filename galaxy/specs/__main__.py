"""``python -m galaxy.specs``: every executable spec against the production registries.

Exit status is non-zero if any spec reports a problem, if an acceptance
quantity fails without being a recorded miss, or if a recorded miss has started
passing. Not-yet-computable quantities do not fail the run, and neither does a
miss that is registered for that model (``spec.misses``) with its debt and its reason — it
still prints as ``fail`` (rule B5 relaxes nothing), it just does not pretend to
be news.
"""

from __future__ import annotations

import sys

from galaxy.core.registry import production
from galaxy.specs import convergence, determinism, graph, preflight, spec, utf8_stdout


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

    spec_results = spec.evaluate_models(models)
    print(spec.report(models, spec_results))
    bad |= any(spec.problems(r, name) for name, r in spec_results.items())

    audits = convergence.sweep_models(models)
    print(convergence.report(models, audits))
    bad |= bool(convergence.check(models, audits))

    print("specs:", "FAIL" if bad else "OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
