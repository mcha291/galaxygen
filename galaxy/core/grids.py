"""Grids: the axes fields are sampled on.

Defaults follow GALAXY_PLAN.md §5a: ``N_R = 400`` radial annuli, ``N_t = 2000``
timesteps, ``N_z = 60`` for the ``(R, z)`` potential grid. N_R and N_t are
separate quality knobs, never one: the measured cost exponent is 0.13 in N_R
against 1.0+ in N_t ``[verified: GALAXY_PLAN.md §5a, citing bench2.py §3]``.
``convergence.py`` (S10) sweeps them independently, which is why the runner
takes a :class:`GridSpec` rather than reading module constants.

Extents are provisional and flagged for the stage that first needs them:

- ``R_max = 30`` kpc: the acceptance table quotes the gas mass inside 30 kpc
  ``[verified: GALAXY_INPUTS.md §7 row 20]``, so the grid must reach it.
- ``t_max = 13.8`` Gyr: cosmic time from t = 0 ``[recall: age of the universe]``.
  S2 confirms the time convention.
- ``z_max = 5`` kpc, z ≥ 0 by plane symmetry: about 5.5 thick-disc scale
  heights ``[verified: GALAXY_INPUTS.md §7 row 7]``. S1 confirms.
- ``n_phi = 360`` (1°): not in the plan; S4 (pattern) decides.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from .fielddoc import AXES


class GridError(ValueError):
    """A grid specification that cannot be built."""


@dataclass(frozen=True, slots=True)
class Axis:
    name: str
    unit: str
    n: int
    lo: float
    hi: float

    def __post_init__(self) -> None:
        if self.name not in AXES:
            raise GridError(f"axis {self.name!r} not in {AXES}")
        if not isinstance(self.n, int) or isinstance(self.n, bool) or self.n < 1:
            raise GridError(f"axis {self.name}: n must be a positive int, got {self.n!r}")
        if not self.hi > self.lo:
            raise GridError(f"axis {self.name}: need lo < hi, got {self.lo} >= {self.hi}")

    @property
    def edges(self) -> np.ndarray:
        return np.linspace(self.lo, self.hi, self.n + 1)

    @property
    def centres(self) -> np.ndarray:
        e = self.edges
        return 0.5 * (e[1:] + e[:-1])

    @property
    def width(self) -> float:
        return (self.hi - self.lo) / self.n


@dataclass(frozen=True, slots=True)
class GridSpec:
    n_R: int = 400
    n_t: int = 2000
    n_z: int = 60
    n_phi: int = 360
    R_max: float = 30.0
    t_max: float = 13.8
    z_max: float = 5.0

    def build(self) -> Grid:
        return Grid(self)

    def replace(self, **changes: object) -> GridSpec:
        return replace(self, **changes)


class Grid:
    """Built axes. Fields of kind ``field`` have shape ``grid.shape(decl.axes)``."""

    def __init__(self, spec: GridSpec) -> None:
        self.spec = spec
        self.axes: dict[str, Axis] = {
            "R": Axis("R", "kpc", spec.n_R, 0.0, float(spec.R_max)),
            "t": Axis("t", "Gyr", spec.n_t, 0.0, float(spec.t_max)),
            "z": Axis("z", "kpc", spec.n_z, 0.0, float(spec.z_max)),
            "phi": Axis("phi", "rad", spec.n_phi, 0.0, 2.0 * math.pi),
        }

    def __getitem__(self, name: str) -> Axis:
        return self.axes[name]

    def shape(self, axes: tuple[str, ...]) -> tuple[int, ...]:
        return tuple(self.axes[a].n for a in axes)

    @property
    def R(self) -> np.ndarray:
        return self.axes["R"].centres

    @property
    def t(self) -> np.ndarray:
        return self.axes["t"].centres

    @property
    def z(self) -> np.ndarray:
        return self.axes["z"].centres

    @property
    def phi(self) -> np.ndarray:
        return self.axes["phi"].centres

    def __repr__(self) -> str:
        return f"Grid({self.spec})"


DEFAULT = GridSpec()
