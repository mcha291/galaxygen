"""Shared fixtures.

Any test that takes a ``model`` argument runs once per registered model. From D170
to S27 there was one, ``basic``; since S27 (BUILD_II Phase 2) there are two, ``basic``
and ``azimuthal``, and every such test runs for both. Since S46 (D197) ``azimuthal`` is
the default and leads the registry; a test that means "the default run" reads
``galaxy.models.DEFAULT``, and one that names ``basic`` says why.

A test marked ``machine_pinned`` pins this machine's floating point bit for bit or to an
ulp - a sha256 digest of a run's bytes, an equality to the last place, a record of counts
that rounding decides - by design (B5: a pin is recorded, never widened into a tolerance).
Another machine's libm, SIMD paths and summation order land elsewhere by an ulp, so under
``CI`` (GitHub sets ``CI=true``) the hook below skips them, as test_hook.py skips the hooks
check (D14); here they run (S77, #206).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# tools/ holds scripts, not a package; tests import them by name.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from galaxy.core.registry import production


@pytest.fixture(scope="session")
def prod():
    """(models, impls, table) with every production stage and model registered."""
    return production()


@pytest.fixture(scope="session")
def judged(prod):
    """Every model judged once, ensembles included.

    A statistical acceptance row needs twenty runs of the whole pipeline, and
    several test modules want the verdict. Building it once per session rather
    than once per test is the difference between a suite of seconds and minutes.
    """
    from galaxy.specs import spec

    return spec.evaluate_models(list(prod[0]))


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "model" in metafunc.fixturenames:
        models, _, _ = production()
        models = list(models)
        metafunc.parametrize("model", models, ids=[m.name for m in models])


MACHINE_PINNED = ("machine_pinned: a bit-exact pin of the capturing machine's floating point, by design "
                  "(B5: no tolerance); another machine lands elsewhere by an ulp, so CI skips it (#206)")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not os.environ.get("CI"):
        return
    skip = pytest.mark.skip(reason=MACHINE_PINNED)
    for item in items:
        if item.get_closest_marker("machine_pinned") is not None:
            item.add_marker(skip)
