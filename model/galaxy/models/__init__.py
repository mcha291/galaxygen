"""Model declarations. Importing this package registers every model.

A model is a declaration, not a pipeline: a name, the inputs it accepts, its
constants, and a map from stage slot to implementation (GALAXY_PLAN.md §2).
A third model slots in by adding a module here, not by forking anything: every
module in this package is a declaration and is imported, except the shared
constants in ``SHARED`` and private modules (``_name``). Each declaration must
register exactly one model.

``DEFAULT`` leads the registry's order, because the first registered model is the
one a request without ``model=`` gets (galaxy/api/service.py) and the one the specs
report first; the rest follow in name order. The declarations import in name order
with the default last, so a default built from another declaration (``azimuthal``
from ``basic``, S27) finds it registered and each import still registers exactly
one; the default is then moved to the front (S46, D197). ``python -m galaxy.models``
prints the breakdown.
"""

from __future__ import annotations

import importlib
import pkgutil

from galaxy.core.registry import MODELS, RegistryError

# S46: the owner's ruling of 2026-10-01 (D197) - the azimuthal model is basic plus where today's stars form; basic stays registered
DEFAULT = "azimuthal"
SHARED = frozenset({"level0"})  # modules here that hold shared constants, not a model


def declarations() -> tuple[str, ...]:
    """The declaration modules in this package, the default first (the registry's order)."""
    found = sorted(
        m.name for m in pkgutil.iter_modules(__path__) if not m.name.startswith("_") and m.name not in SHARED
    )
    if DEFAULT not in found:
        raise RegistryError(f"the default model's declaration galaxy/models/{DEFAULT}.py is missing")
    return (DEFAULT, *(n for n in found if n != DEFAULT))


# Import order: the others in name order, the default last (it may be built from one of them).
for _name in (*declarations()[1:], DEFAULT):
    _before = len(MODELS)
    importlib.import_module(f"{__name__}.{_name}")
    if len(MODELS) != _before + 1:
        raise RegistryError(
            f"galaxy/models/{_name}.py registered {len(MODELS) - _before} models; a declaration registers exactly one"
        )
MODELS.put_first(DEFAULT)
