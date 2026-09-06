"""``python -m galaxy.specs``: every executable spec against the production registries.

Exit status is non-zero if any spec reports a problem, if an acceptance
quantity fails without being a recorded miss, or if a recorded miss has started
passing. Not-yet-computable quantities do not fail the run, and neither does a
miss that is registered for that model (``spec.misses``) with its debt and its reason — it
still prints as ``fail`` (rule B5 relaxes nothing), it just does not pretend to
be news. ``convergence`` judges the same table against the grid under the same
register discipline; ``performance`` publishes numbers and fails only on a
stage that went unprofiled (S10).
"""

from __future__ import annotations

import sys

from galaxy.core.registry import production
from galaxy.specs import convergence, determinism, graph, performance, preflight, spec, utf8_stdout


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

    drift_results = convergence.evaluate_models(models)
    print(convergence.report(models, drift_results))
    bad |= any(convergence.problems(r, name) for name, r in drift_results.items())

    profiles = performance.run_all(m.name for m in models)
    print(performance.report(profiles))
    unprofiled = performance.check(models, impls, table, profiles)
    for p in unprofiled:
        print(f"    FAIL {p}")
    bad |= bool(unprofiled)

    print("specs:", "FAIL" if bad else "OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
