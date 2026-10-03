"""Field declarations (rule A8).

A field is described where it is computed: the stage that publishes it carries a
:class:`FieldDecl` with a label, a unit from the closed vocabulary, a kind, its
ramp, whether zero is meaningful, and an ``about`` line recording its surprise.
``preflight`` asserts nothing is published undeclared and no declaration is
orphaned; across models it asserts that the same field name carries the same
contract (:meth:`FieldDecl.contract`).

The ``kind`` vocabulary is closed and two-dimensional: a *domain* (grid,
galaxy, object) crossed with a *value class* (continuous, categorical). The
domain decides storage and shape; the value class decides rendering (ramp vs
palette) and comparison. Six kinds result; nothing else is a kind.

Axes are named from a closed set and declared in canonical order ``(R, t, z,
phi)`` so that ``(t, R)`` can never be confused with ``(R, t)``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .cmaps import CMAPS  # the closed cmap vocabulary, with the stops behind it
from .units import UnknownUnit
from .units import unit as _unit

IDENT = re.compile(r"^[a-z][a-z0-9_]*$")  # fields, inputs, seeds, stages, models
CONST_IDENT = re.compile(r"^[A-Z][A-Z0-9_]*$")  # constants: UPPER_SNAKE, never confusable with a field
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

# Closed vocabularies. Extend by editing here, with a DECISIONS.md entry.
AXES: tuple[str, ...] = ("R", "t", "z", "phi")
OBJECTS: tuple[str, ...] = ("system", "star", "planet", "belt", "moon", "cloud", "cluster", "remnant", "bright_star")  # cloud: S32 (D181); cluster: S33, BUILD_II Phase 11; remnant: S36, BUILD_II Phase 10 (the supernova-remnant census); bright_star: S48 (D200, the bright-end-complete catalogue)
SCALES: tuple[str, ...] = ("linear", "log", "symlog")
PROVENANCE: tuple[str, ...] = ("derived", "seeded", "synthetic")  # rule A10 (four kinds since D212); inputs are the other
# What only a synthetic field declares, and must (BUILD_III section 1c, rules 2-4; DECISIONS.md D214 section 2).
SYNTHETIC_DECLARATIONS: tuple[str, ...] = ("stands_in_for", "conserves", "statistic")
# A statistic that was not read says so, and may only beside the debt that owes it (BUILD_III section 9: an
# unsourced draw is not excused by the label).
_NONE_READ = re.compile(r"none read", re.IGNORECASE)
_DEBT = re.compile(r"#\d+")


class DeclarationError(ValueError):
    """A field, ramp or palette declaration violates the contract."""


class Kind(str, Enum):
    FIELD = "field"  # continuous scalar sampled on grid axes
    CATEGORY_FIELD = "category_field"  # categorical label on grid axes
    SCALAR = "scalar"  # one continuous number for the whole galaxy
    CATEGORY_SCALAR = "category_scalar"  # one categorical label for the whole galaxy
    COLUMN = "column"  # continuous per-object value (catalogue column)
    CATEGORY_COLUMN = "category_column"  # categorical per-object value

    @property
    def domain(self) -> str:
        return {
            Kind.FIELD: "grid",
            Kind.CATEGORY_FIELD: "grid",
            Kind.SCALAR: "galaxy",
            Kind.CATEGORY_SCALAR: "galaxy",
            Kind.COLUMN: "object",
            Kind.CATEGORY_COLUMN: "object",
        }[self]

    @property
    def categorical(self) -> bool:
        return self in (Kind.CATEGORY_FIELD, Kind.CATEGORY_SCALAR, Kind.CATEGORY_COLUMN)


@dataclass(frozen=True, slots=True)
class Ramp:
    """The single rendering opinion for a continuous field (rule A9).

    ``lo``/``hi`` of ``None`` mean "from the data" (the viewer picks
    percentiles); a fixed bound pins the ramp.
    """

    cmap: str
    scale: str = "linear"
    lo: float | None = None
    hi: float | None = None

    def __post_init__(self) -> None:
        if self.cmap not in CMAPS:
            raise DeclarationError(f"ramp cmap {self.cmap!r} not in closed set {CMAPS}")
        if self.scale not in SCALES:
            raise DeclarationError(f"ramp scale {self.scale!r} not in {SCALES}")
        if self.lo is not None and self.hi is not None and not self.lo < self.hi:
            raise DeclarationError(f"ramp needs lo < hi, got {self.lo} >= {self.hi}")


@dataclass(frozen=True, slots=True)
class Palette:
    """The single rendering opinion for a categorical field: one colour per category."""

    colors: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.colors:
            raise DeclarationError("palette needs at least one colour")
        bad = [c for c in self.colors if not isinstance(c, str) or not _HEX.match(c)]
        if bad:
            raise DeclarationError(f"palette colours must be #rrggbb, got {bad}")


@dataclass(frozen=True, slots=True)
class FieldDecl:
    name: str
    label: str
    unit: str
    kind: Kind
    about: str
    axes: tuple[str, ...] = ()
    of: str | None = None  # object class for object-domain kinds
    categories: tuple[str, ...] = ()
    ramp: Ramp | Palette | None = None
    meaningful_zero: bool = False
    optional: bool = False  # present in some models only; readers must handle absence
    provenance: str = "derived"  # rule A10: derived (inputs only), seeded (inputs + seed) or synthetic (the layer's)
    # A synthetic field's three declarations (S55, D214): required and non-empty there, refused anywhere else.
    stands_in_for: str = ""  # the physics the model does not compute, which this realisation stands in for
    conserves: str = ""  # the total it redistributes and never changes
    statistic: str = ""  # the measured statistic it is drawn to, cited; "none read" only with the debt's number

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not IDENT.match(self.name):
            raise DeclarationError(f"field name {self.name!r} must match {IDENT.pattern}")
        if not isinstance(self.label, str) or not self.label.strip():
            raise DeclarationError(f"field {self.name}: label is required")
        try:
            _unit(self.unit)
        except UnknownUnit as e:
            raise DeclarationError(f"field {self.name}: {e}") from None
        try:
            kind = Kind(self.kind)
        except ValueError:
            raise DeclarationError(
                f"field {self.name}: kind {self.kind!r} not one of {[k.value for k in Kind]}"
            ) from None
        object.__setattr__(self, "kind", kind)
        if not isinstance(self.about, str) or not self.about.strip():
            raise DeclarationError(f"field {self.name}: an about line is required (rule A8)")
        if self.provenance not in PROVENANCE:
            raise DeclarationError(
                f"field {self.name}: provenance {self.provenance!r} not in {PROVENANCE}"
            )
        object.__setattr__(self, "axes", tuple(self.axes))
        object.__setattr__(self, "categories", tuple(self.categories))
        self._check_synthetic()
        self._check_domain(kind)
        self._check_values(kind)

    @property
    def composed(self) -> bool:
        """A law applied to a realisation (BUILD_III section 1a): a field with a phi axis. Nothing the model
        computes says where round a ring a structure lies, so whatever varies round one was placed by the
        randomness layer - identified by the axes, not by a flag someone could forget to set (D214 section 1)."""
        return "phi" in self.axes

    def _check_synthetic(self) -> None:
        given = {n: getattr(self, n) for n in SYNTHETIC_DECLARATIONS}
        if self.provenance != "synthetic":
            stated = [n for n, v in given.items() if v]
            if stated:
                raise DeclarationError(
                    f"field {self.name}: {stated} are a synthetic field's declarations; this one is {self.provenance}"
                )
            return
        missing = [n for n, v in given.items() if not isinstance(v, str) or not v.strip()]
        if missing:
            raise DeclarationError(
                f"field {self.name}: a synthetic field declares {missing} - what it stands in for, what it "
                "conserves and the statistic it is drawn to (rule A10)"
            )
        if _NONE_READ.search(self.statistic) and not _DEBT.search(self.statistic):
            raise DeclarationError(
                f"field {self.name}: a statistic that was not read is a debt, and names it: 'none read (#<debt>)'"
            )

    def _check_domain(self, kind: Kind) -> None:
        if kind.domain == "grid":
            if not self.axes:
                raise DeclarationError(f"field {self.name}: grid kinds need at least one axis")
            unknown = [a for a in self.axes if a not in AXES]
            if unknown:
                raise DeclarationError(f"field {self.name}: axes {unknown} not in {AXES}")
            order = [AXES.index(a) for a in self.axes]
            if order != sorted(set(order)):
                raise DeclarationError(
                    f"field {self.name}: axes {self.axes} must be unique and in canonical order {AXES}"
                )
            if self.of is not None:
                raise DeclarationError(f"field {self.name}: grid kinds take no object class")
        else:
            if self.axes:
                raise DeclarationError(f"field {self.name}: {kind.value} takes no axes")
            if kind.domain == "object":
                if self.of not in OBJECTS:
                    raise DeclarationError(
                        f"field {self.name}: object kinds need of= one of {OBJECTS}, got {self.of!r}"
                    )
            elif self.of is not None:
                raise DeclarationError(f"field {self.name}: {kind.value} takes no object class")

    def _check_values(self, kind: Kind) -> None:
        if kind.categorical:
            if not self.categories:
                raise DeclarationError(f"field {self.name}: categorical kinds need categories")
            if len(set(self.categories)) != len(self.categories) or not all(
                isinstance(c, str) and c for c in self.categories
            ):
                raise DeclarationError(f"field {self.name}: categories must be unique non-empty strings")
            if self.unit != "dimensionless":
                raise DeclarationError(f"field {self.name}: a category has no unit; use dimensionless")
            if self.ramp is not None:
                if not isinstance(self.ramp, Palette):
                    raise DeclarationError(f"field {self.name}: categorical kinds take a Palette")
                if len(self.ramp.colors) != len(self.categories):
                    raise DeclarationError(
                        f"field {self.name}: palette has {len(self.ramp.colors)} colours "
                        f"for {len(self.categories)} categories"
                    )
        else:
            if self.categories:
                raise DeclarationError(f"field {self.name}: only categorical kinds take categories")
            if self.ramp is not None and not isinstance(self.ramp, Ramp):
                raise DeclarationError(f"field {self.name}: continuous kinds take a Ramp")
        # A ramp is the one rendering opinion (A9). Grid and object fields are
        # drawn, so they must carry one. A galaxy-level scalar is a number, not
        # a picture; its ramp is optional.
        if kind.domain in ("grid", "object") and self.ramp is None:
            raise DeclarationError(f"field {self.name}: {kind.value} fields must declare a ramp")

    def contract(self) -> tuple:
        """Everything but ``about``. Two models publishing the same name must agree on this."""
        return (
            self.name,
            self.label,
            self.unit,
            self.kind.value,
            self.axes,
            self.of,
            self.categories,
            self.ramp,
            self.meaningful_zero,
            self.optional,
            self.provenance,
            self.stands_in_for,
            self.conserves,
            self.statistic,
        )
