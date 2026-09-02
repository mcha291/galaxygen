"""Executable specs. A session runs ``python -m galaxy.specs`` and reads pass/fail.

- ``graph``: acyclic per model; checkpoint order; input→checkpoint hypotheses; provenance
- ``preflight``: declarations reconcile within and across models; optional absence handled
- ``determinism``: reproducible per model; per-region seed derivation is order-independent
- ``spec``: the 24 acceptance quantities, each pass / fail / not-yet-computable

``convergence`` and ``performance`` arrive at S10, when there is something to measure.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


def utf8_stdout() -> None:
    """Reports carry non-ASCII (M☉, subscripts). A cp1252 console must not crash the instrument."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="backslashreplace")


@dataclass(frozen=True, slots=True)
class Problem:
    """One failed check. ``scope`` is a model name or ``*`` for cross-model."""

    scope: str
    code: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.scope}] {self.code}: {self.detail}"
