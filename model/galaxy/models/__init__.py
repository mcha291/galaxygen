"""Model declarations. Importing this package registers every model.

A model is a declaration, not a pipeline: a name, the inputs it accepts, its
constants, and a map from stage slot to implementation (GALAXY_PLAN.md §2).
A third model slots in by adding a module here, not by forking anything: every
module in this package is a declaration and is imported, except the shared
constants in ``SHARED`` and private modules (``_name``). Each declaration must
register exactly one model.

``DEFAULT`` registers first, because the first registered model is the one a
request without ``model=`` gets (galaxy/api/service.py); the rest follow in
name order. ``python -m galaxy.models`` prints the breakdown.
"""

from __future__ import annotations

import importlib
import pkgutil

from galaxy.core.registry import MODELS, RegistryError

DEFAULT = "simple"
SHARED = frozenset({"level0"})  # modules here that hold shared constants, not a model


def declarations() -> tuple[str, ...]:
    """The declaration modules in this package, the default first."""
    found = sorted(
        m.name for m in pkgutil.iter_modules(__path__) if not m.name.startswith("_") and m.name not in SHARED
    )
    if DEFAULT not in found:
        raise RegistryError(f"the default model's declaration galaxy/models/{DEFAULT}.py is missing")
    return (DEFAULT, *(n for n in found if n != DEFAULT))


for _name in declarations():
    _before = len(MODELS)
    importlib.import_module(f"{__name__}.{_name}")
    if len(MODELS) != _before + 1:
        raise RegistryError(
            f"galaxy/models/{_name}.py registered {len(MODELS) - _before} models; a declaration registers exactly one"
        )
