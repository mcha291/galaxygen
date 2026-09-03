"""Shared fixtures.

Any test that takes a ``model`` argument runs once per registered model. This is
the two-model discipline: nothing is tested against ``simple`` alone.
"""

from __future__ import annotations

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
