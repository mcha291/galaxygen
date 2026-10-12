"""The input table, constants, model declarations and the registries.

Inputs are global scalars only (rule A2). Every quantity is exactly one of
input, derived or seeded (rule A10); this module holds the inputs, the field
declarations hold derived and seeded. Defaults are real measured values so that
launching with nothing touched generates the Milky Way (rule A5). Where no
document gives a value, the default is :data:`UNSET` with an owning session,
and the runner refuses to substitute a number (rule B9).

Source: GALAXY_INPUTS.md §3 as amended by the rulings in §11 and the closed
input vector in GALAXY_PLAN.md §8 ``[verified: those sections]``. The plan's
§5a points at §11 for the input table; the table is §3.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Generic, TypeVar

from .fielddoc import CONST_IDENT, IDENT
from .stage import CHECKPOINTS, Stage
from .units import UnknownUnit
from .units import unit as _unit


class _Unset:
    __slots__ = ()

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET = _Unset()

# A *pin* (S58, D217 item 2) is the fourth kind: a measured fact about one galaxy's structure that a template
# states in place of what the model would derive. It is not a control - no request offers it and it does not
# count against the ceiling - and it has no default: where none is given the model derives. A pin that is a class
# (True or False) has no range. A pin that is a measured number is **held to the range of what it replaces**
# (S59, D218, the gate's follow-up, item 7): it declares lo and hi, and a value outside them is refused where a
# template is validated and where a run resolves its inputs - not a viewer's range, which a pin has none of.
# Since S60 (D219) a class may have more than two values - the pin then names its closed list (``classes``) and is
# one of them, a text - and a pin may be a **table**: rows of a measured structure in the source's own columns
# (``columns``: each a name and a unit, or a name alone for a column of names). Four shapes, told apart by the
# declaration (``Input.shape``): True or False; one of ``classes``; a number in ``unit``; rows of ``columns``.
INPUT_KINDS: tuple[str, ...] = ("control", "seed", "events", "pin")

# Ruling 6: ceiling 12 [verified: GALAXY_INPUTS.md §11]. Counts controls only;
# seeds and event lists are exempt [verified: GALAXY_INPUTS.md §3 table foot].
INPUT_CEILING = 12


class RegistryError(ValueError):
    """An input, constant or model declaration violates the contract."""


class DuplicateRegistration(RegistryError):
    """Two items registered under one name."""


@dataclass(frozen=True, slots=True)
class Input:
    name: str
    label: str
    kind: str  # control | seed | events | pin
    about: str
    unit: str | None = None  # required for controls; None for seeds, event lists and a pin that is a class (True or False); a pin that is a measured number carries its unit (S59, D218)
    default: object = UNSET  # a pin's is None: no pin is given, and the model derives
    lo: float | None = None  # control range for the viewer; None = not yet set. A numeric pin's: the range it is held to
    hi: float | None = None
    checkpoint_hypothesis: int | None = None  # GALAXY_PLAN.md §3 grouping; graph.py checks it
    default_owner: str | None = None  # session that owes the default, when UNSET
    hi_open: bool = False  # a numeric pin whose range does not include hi itself (an angle of one turn: 0 <= x < 360)
    # S60 (D219): a pin that is a named class - its closed list of values - and a pin that is a table - its columns,
    # each (name, unit) with the unit None for a column of names - with what its rows must satisfy beyond their
    # types (``defect`` returns the rows' first defect in words, or None).
    classes: tuple[str, ...] = ()
    columns: tuple[tuple[str, str | None], ...] = ()
    defect: Callable[[tuple], str | None] | None = None

    def __post_init__(self) -> None:
        if not IDENT.match(self.name):
            raise RegistryError(f"input name {self.name!r} must match {IDENT.pattern}")
        if self.kind not in INPUT_KINDS:
            raise RegistryError(f"input {self.name}: kind {self.kind!r} not in {INPUT_KINDS}")
        if not self.label.strip() or not self.about.strip():
            raise RegistryError(f"input {self.name}: label and about are required")
        if self.kind == "control":
            if self.unit is None:
                raise RegistryError(f"input {self.name}: controls need a unit")
            try:
                _unit(self.unit)
            except UnknownUnit as e:
                raise RegistryError(f"input {self.name}: {e}") from None
            if self.default is not UNSET and (
                isinstance(self.default, bool) or not isinstance(self.default, (int, float))
            ):
                raise RegistryError(f"input {self.name}: control default must be a number or UNSET")
        elif self.kind == "pin":
            # S59 (D218 items 5-6): a pin is a class (no unit: True or False) or a measured number (its unit).
            if self.unit is not None:
                try:
                    _unit(self.unit)
                except UnknownUnit as e:
                    raise RegistryError(f"input {self.name}: {e}") from None
        else:
            if self.unit is not None:
                raise RegistryError(f"input {self.name}: {self.kind} inputs carry no unit")
        if self.kind == "seed" and (
            self.default is UNSET or isinstance(self.default, bool) or not isinstance(self.default, int)
        ):
            raise RegistryError(f"input {self.name}: seeds need an int default")
        if self.kind == "pin" and (self.default is not None or (self.unit is None and (self.lo is not None or self.hi is not None))):
            raise RegistryError(
                f"input {self.name}: a pin has no default and no range - where a template gives none the model "
                "derives (default=None); only a pin that is a measured number, with its unit, is held to a range"
            )
        if self.kind == "pin" and self.unit is not None and (self.lo is None or self.hi is None):
            # S59 (D218, the gate's follow-up, item 7): "a numeric pin is held to the range of the draw it replaces".
            raise RegistryError(
                f"input {self.name}: a pin that is a measured number is held to the range of what it replaces - "
                "lo and hi are required"
            )
        if self.hi_open and not (self.kind == "pin" and self.unit is not None):
            raise RegistryError(f"input {self.name}: only a numeric pin's range may leave its upper end out")
        object.__setattr__(self, "classes", tuple(self.classes))
        object.__setattr__(self, "columns", tuple((str(n), u) for n, u in self.columns))
        if (self.classes or self.columns or self.defect is not None) and self.kind != "pin":
            raise RegistryError(f"input {self.name}: only a pin names classes or columns")
        if self.classes and (
            self.unit is not None or self.columns or len(set(self.classes)) != len(self.classes)
            or len(self.classes) < 2 or not all(isinstance(c, str) and IDENT.match(c) for c in self.classes)
        ):
            raise RegistryError(f"input {self.name}: a named class pin has two or more distinct class names and no unit")
        if self.columns:
            if self.unit is not None or len({n for n, _ in self.columns}) != len(self.columns):
                raise RegistryError(f"input {self.name}: a table pin has distinctly named columns and no unit of its own")
            for column, unit in self.columns:
                if not IDENT.match(column):
                    raise RegistryError(f"input {self.name}: column name {column!r} must match {IDENT.pattern}")
                if unit is not None:
                    try:
                        _unit(unit)
                    except UnknownUnit as e:
                        raise RegistryError(f"input {self.name}: column {column}: {e}") from None
        if self.defect is not None and not self.columns:
            raise RegistryError(f"input {self.name}: only a table pin states what its rows must satisfy")
        if (self.default is UNSET) != (self.default_owner is not None):
            raise RegistryError(
                f"input {self.name}: default_owner is required exactly when the default is UNSET"
            )
        if self.lo is not None and self.hi is not None and not self.lo < self.hi:
            raise RegistryError(f"input {self.name}: need lo < hi")
        if self.checkpoint_hypothesis is not None and not (
            1 <= self.checkpoint_hypothesis <= len(CHECKPOINTS)
        ):
            raise RegistryError(f"input {self.name}: checkpoint_hypothesis out of range")

    @property
    def unset(self) -> bool:
        return self.default is UNSET

    @property
    def has_range(self) -> bool:
        return self.lo is not None and self.hi is not None

    @property
    def range_text(self) -> str:
        """The range in words, for a refusal: "1 to 60", or "0 up to, not including, 360"."""
        return f"{self.lo:g} up to, not including, {self.hi:g}" if self.hi_open else f"{self.lo:g} to {self.hi:g}"

    @property
    def shape(self) -> str:
        """What a pin's value is (S60, D219): ``class`` (True or False), ``named`` (one of ``classes``), ``number``
        (in ``unit``) or ``table`` (rows of ``columns``). Not asked of an input that is no pin."""
        if self.kind != "pin":
            raise RegistryError(f"input {self.name} is no pin")
        return "table" if self.columns else "named" if self.classes else "class" if self.unit is None else "number"

    def pinned(self, value: object) -> object:
        """A pin's value as a run holds it, or a ``RegistryError`` saying what the pin is: True or False; one of
        the named classes; a finite number inside the range of what it replaces; or the rows of a table - a tuple
        of tuples, each cell a name where its column has no unit and a finite number where it has one, the rows
        satisfying what the declaration asks of them (``defect``)."""
        shape = self.shape
        if shape == "class":
            if not isinstance(value, bool):
                raise RegistryError(f"pin {self.name!r} is True or False (or not given), got {value!r}")
            return value
        if shape == "named":
            if not isinstance(value, str) or value not in self.classes:
                raise RegistryError(f"pin {self.name!r} is one of {list(self.classes)} (or not given), got {value!r}")
            return value
        if shape == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise RegistryError(f"pin {self.name!r} is a finite number in {self.unit} (or not given), got {value!r}")
            if not self.admits(float(value)):
                raise RegistryError(
                    f"pin {self.name!r} is held to the range of what it replaces, {self.range_text} {self.unit}; got {value!r}"
                )
            return float(value)
        names = [n for n, _ in self.columns]
        if not isinstance(value, (tuple, list)) or not value:
            raise RegistryError(f"pin {self.name!r} is a table, one or more rows of {names} (or not given), got {value!r}")
        rows = []
        for row in value:
            if not isinstance(row, (tuple, list)) or len(row) != len(self.columns):
                raise RegistryError(f"pin {self.name!r}: a row holds {names}, got {row!r}")
            cells: list[object] = []
            for cell, (column, unit) in zip(row, self.columns):
                if unit is None:
                    if not isinstance(cell, str) or not cell.strip():
                        raise RegistryError(f"pin {self.name!r}: column {column} is a name, got {cell!r}")
                    cells.append(cell)
                else:
                    if isinstance(cell, bool) or not isinstance(cell, (int, float)) or not math.isfinite(cell):
                        raise RegistryError(f"pin {self.name!r}: column {column} is a finite number in {unit}, got {cell!r}")
                    cells.append(float(cell))
            rows.append(tuple(cells))
        table = tuple(rows)
        fault = None if self.defect is None else self.defect(table)
        if fault:
            raise RegistryError(f"pin {self.name!r}: {fault}")
        return table

    def admits(self, value: float) -> bool:
        """Whether ``value`` lies in the declared range (both ends included, but ``hi`` where ``hi_open``).
        True where no range is declared."""
        if not self.has_range:
            return True
        return bool(self.lo <= value < self.hi) if self.hi_open else bool(self.lo <= value <= self.hi)  # type: ignore[operator]


@dataclass(frozen=True, slots=True)
class MergerEvent:
    """One entry in the ``mergers`` event list (ruling 11).

    ``gas_fraction`` is what dissolved the ``second_infall_onset`` input: it is the
    share of the galaxy's remaining baryon budget this event delivers, not the
    satellite's own internal gas fraction. A gas-rich major merger is therefore
    *the* second infall rather than something that happens alongside one.
    """

    time: float  # Gyr of cosmic time, t = 0 at the Big Bang
    mass_ratio: float  # satellite : host, so 0.25 is a 1:4 merger
    gas_fraction: float  # share of the remaining baryon budget this event delivers
    about: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.time:
            raise RegistryError(f"merger at t={self.time}: time is cosmic time and cannot be negative")
        if not 0.0 < self.mass_ratio <= 1.0:
            raise RegistryError(f"merger at t={self.time}: mass_ratio must be in (0, 1]")
        if not 0.0 <= self.gas_fraction <= 1.0:
            raise RegistryError(f"merger at t={self.time}: gas_fraction must be in [0, 1]")


# A merger is "major" above this ratio; below it the satellite is absorbed without
# restructuring the disc [recall: the usual 1:10 convention].
MAJOR_MERGER_RATIO = 0.1


@dataclass(frozen=True, slots=True)
class Constant:
    value: float
    unit: str
    about: str

    def __post_init__(self) -> None:
        try:
            _unit(self.unit)
        except UnknownUnit as e:
            raise RegistryError(str(e)) from None
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise RegistryError(f"constant value must be a number, got {self.value!r}")
        if not self.about.strip():
            raise RegistryError("constant needs an about line")


@dataclass(frozen=True, slots=True)
class Model:
    """A model is a declaration, not a pipeline (GALAXY_PLAN.md §2)."""

    name: str
    about: str
    stages: tuple[tuple[str, str], ...]  # (slot, implementation id)
    constants: Mapping[str, Constant]
    inputs: tuple[str, ...] | None = None  # None = every registered input

    def __post_init__(self) -> None:
        if not IDENT.match(self.name):
            raise RegistryError(f"model name {self.name!r} must match {IDENT.pattern}")
        if not self.about.strip():
            raise RegistryError(f"model {self.name}: an about line is required")
        stages = tuple((str(s), str(i)) for s, i in self.stages)
        slots = [s for s, _ in stages]
        if len(set(slots)) != len(slots):
            raise RegistryError(f"model {self.name}: a slot appears twice: {slots}")
        object.__setattr__(self, "stages", stages)
        consts = dict(self.constants)
        for k, v in consts.items():
            if not isinstance(k, str) or not CONST_IDENT.match(k):
                raise RegistryError(f"model {self.name}: constant name {k!r} must match {CONST_IDENT.pattern}")
            if not isinstance(v, Constant):
                raise RegistryError(f"model {self.name}: constant {k} must be a Constant, got {v!r}")
        object.__setattr__(self, "constants", MappingProxyType(consts))
        if self.inputs is not None:
            object.__setattr__(self, "inputs", tuple(self.inputs))

    @property
    def stage_map(self) -> dict[str, str]:
        return dict(self.stages)

    def input_names(self, table: Mapping[str, Input]) -> tuple[str, ...]:
        return tuple(table) if self.inputs is None else self.inputs


T = TypeVar("T")


class Registry(Generic[T]):
    """Name-keyed registry that refuses duplicates."""

    def __init__(self, what: str, key: Callable[[T], str]) -> None:
        self._what = what
        self._key = key
        self._items: dict[str, T] = {}

    def register(self, item: T) -> T:
        name = self._key(item)
        if name in self._items:
            raise DuplicateRegistration(f"{self._what} {name!r} is already registered")
        # What must hold for an item production runs, and need not for an instrument's copy of
        # it (Stage.validate_registration, S27): checked here, at the one door into production.
        validate = getattr(item, "validate_registration", None)
        if callable(validate):
            validate()
        self._items[name] = item
        return item

    def get(self, name: str) -> T:
        try:
            return self._items[name]
        except KeyError:
            raise KeyError(
                f"no {self._what} named {name!r}; registered: {sorted(self._items)}"
            ) from None

    def names(self) -> tuple[str, ...]:
        return tuple(self._items)

    def put_first(self, name: str) -> None:
        """Move ``name`` to the front of the order (the default model leads: galaxy/models/__init__.py, D197)."""
        item = self.get(name)
        self._items = {name: item, **{k: v for k, v in self._items.items() if k != name}}

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items


# --- the two pins of the arms' pieces (S60, D219 items 3 and 8) ---------------

# The arm classes, in the order the published ``arm_class`` holds them: the two the model derives - a barred disc
# is a grand design, an unbarred one multi-armed - and the one a template alone can state.
ARM_CLASSES: tuple[str, ...] = ("grand_design", "multi_armed", "flocculent")
# A measured arm as its source fits it: a logarithmic spiral with one kink over a range of azimuth β from the
# centre, β = 0 towards the Sun and increasing with the disc's rotation: ln(R / radius_kink) =
# −(β − beta_kink) tan ψ, ψ = pitch_below for β ≤ beta_kink and pitch_above past it.
ARM_PIECE_COLUMNS: tuple[tuple[str, str | None], ...] = (
    ("arm", None), ("beta_from", "deg"), ("beta_to", "deg"), ("beta_kink", "deg"), ("radius_kink", "kpc"),
    ("pitch_below", "deg"), ("pitch_above", "deg"),
)


def arm_rows_defect(rows: tuple) -> str | None:
    """The first defect of a table of measured arms (``ARM_PIECE_COLUMNS``), in words, or None: every arm named
    once; a range of azimuth that runs forward, within a turn of the Sun either way, its kink inside it; a
    positive kink radius; two pitches that are not zero and under 90 degrees either way."""
    names = [row[0] for row in rows]
    if len(set(names)) != len(names):
        return f"an arm is named twice among {names}"
    for arm, lo, hi, kink, radius, below, above in rows:
        if not (-360.0 <= lo < hi <= 360.0):
            return f"{arm}: the azimuths run from beta_from to a larger beta_to, within a turn of the Sun; got {lo!r} to {hi!r}"
        if not lo <= kink <= hi:
            return f"{arm}: the kink lies inside the range of azimuth; got {kink!r} outside {lo!r} to {hi!r}"
        if not radius > 0.0:
            return f"{arm}: the kink's radius is positive; got {radius!r}"
        for pitch in (below, above):
            if not 0.0 < abs(pitch) < 90.0:
                return f"{arm}: a pitch is not zero and under 90 degrees either way; got {pitch!r}"
    return None


# --- the closed input vector -------------------------------------------------
# 7 controls, 4 seeds, 1 event list [verified: GALAXY_PLAN.md §8; GALAXY_INPUTS.md §3, §11]; a fifth seed,
# texture_seed, since S55 [verified: DECISIONS.md D214 section 3; BUILD_III.md section 1c].

_INPUTS: tuple[Input, ...] = (
    Input(
        "halo_mass",
        "Halo mass M₂₀₀",
        "control",
        "Literature spans 0.89–1.3 × 10¹² M☉ (Karukes+19; McMillan), per GALAXY_INPUTS.md §3. "
        "That span is the uncertainty on the Milky Way, not the control range: the range is set "
        "to the disc-galaxy regime this model is built for, 10¹¹–10¹³ M☉, which runs from a large "
        "dwarf to a group-scale halo. Below 10¹¹ the assumption that the baryons make a rotating "
        "disc stops holding, and above 10¹³ the galaxy is not a disc galaxy [inferred]. Sets "
        "everything: R₂₀₀ by definition, and the baryon budget through m_d.",
        unit="Msun",
        default=1.1e12,
        lo=1e11,
        hi=1e13,
        checkpoint_hypothesis=1,
    ),
    Input(
        "disc_spin",
        "Disc spin parameter λ_d",
        "control",
        "The spin parameter of the disc, not of the halo (ruling 8): the halo spin λ times the "
        "angular-momentum retention fraction j_d/m_d, plus whatever MMW98's unmodelled structure "
        "factors would have contributed. Seeding rolls from a halo-λ log-normal would make every "
        "galaxy three times too extended (GALAXY_PLAN.md §7 risk 1), so the prior must be the "
        "λ_d distribution. Default re-derived at S1: ruling 8's 0.0144 was inferred against "
        "R_vir = 255 kpc, a different overdensity at a different mass, while this model's own "
        "R₂₀₀ is 212.9 kpc; λ_d = √2 R_d/R₂₀₀ = 0.0173 reproduces the measured 2.6 kpc "
        "[verified: DECISIONS.md D30, tests/test_disc.py::test_joint_fit_reproduces_the_defaults]. "
        "Ruling 8's argument is untouched, only its arithmetic; both values sit inside the "
        "λ_d = 0.01–0.03 that Burkert+10 need for m_d ≈ 0.05. **Re-ruled at S22, which discharges "
        "debt #10:** the default is the value MMW98's relation gives at the model's own R₂₀₀ and "
        "not at a radius quoted for another overdensity, because a relation and the radius it is "
        "written in are one thing — 0.0144 was ruling 8's arithmetic read against Huang+16's "
        "255 kpc top-hat radius (≈95 ρ_crit at a different mass) and 0.0173 is the same relation "
        "read against this model's 212.9 kpc. The rule this leaves is general: a length taken from "
        "a source enters at the source's own definition or not at all.",
        unit="dimensionless",
        default=0.0173,
        lo=0.005,
        hi=0.05,
        checkpoint_hypothesis=1,
    ),
    Input(
        "halo_assembly_z",
        "Halo assembly redshift",
        "control",
        "Does two jobs: sets the assembly epoch and derives c_vir = K(1 + z_f), converted to c₂₀₀ "
        "(ruling 5, debt #12). Renamed from galaxy_age by ruling 7. GALAXY_INPUTS.md §3 gives "
        "z ≈ 2–3, and until S15 the default was that range's midpoint, 2.5, justified by its "
        "c₂₀₀ = 14.4 landing inside the 10–18 the Milky Way's concentration measurements span. But "
        "K is calibrated on dark-matter-only simulations [verified: Wechsler et al. 2002, c_vir = "
        "c₁/a_c], so the concentration it gives is the halo's *before* it contracted around the disc "
        "(S14), while a measurement of the Milky Way fits an NFW to the halo *after*: at 2.5 that "
        "fit, halo_concentration_contracted, reads 18.5 — over. Since S15 the default is derived: "
        "the epoch at which the ΛCDM median halo of the default mass assembled, z_f = c_vir/K − 1 "
        "with c₂₀₀ = 10^(0.905 − 0.101 log₁₀(M₂₀₀ h/10¹² M☉)) = 8.25 [verified: Dutton & Macciò "
        "2014, the z = 0 relation, Planck; h = 0.7 here] converted to c_vir = 10.92 at Δ_vir — "
        "1.66, its 0.11 dex scatter spanning 1.08–2.41 [verified: tests/test_registry.py::"
        "test_the_epochs_default_is_the_lcdm_median]. The Milky Way's own pre-contraction "
        "concentration, 9.4 (+1.9/−2.6) from a contracted fit to Gaia DR2 [recall: Cautun et al. "
        "2020], is z_f = 2.0 (+0.6/−0.9) and brackets it. The range 0.5–5 covers late assembly to "
        "the earliest epoch the relation is quoted for [inferred]. Row 3 still misses high at this "
        "default, 260 against 245–251, and spans 252–270 across the scatter: its prediction names "
        "the bulge and the extended component (spec._MISSES row 3), not this input.",
        unit="dimensionless",
        default=1.66,
        lo=0.5,
        hi=5.0,
        checkpoint_hypothesis=1,
    ),
    Input(
        "baryon_retention",
        "Baryon retention fraction",
        "control",
        "Fraction of the cosmic baryon budget the galaxy keeps: f_b × this = m_d ≈ 0.055 "
        "(ruling 9). S1 confirms the ~0.35 of §3 and does not tighten it: 0.35 gives m_d = 0.053, "
        "and 0.053 × M₂₀₀ = 5.9 × 10¹⁰ M☉ reconciles acceptance row 1's 5 ± 1 × 10¹⁰ of stars "
        "with row 20's 8 × 10⁹ of gas, which is what a baryon budget should do. Fitting it "
        "instead to the stellar mass alone would tune a well-defined parameter to cover for the "
        "missing gas phase — the constant would then have no claim on its value (rule B10). "
        "Range from the observed disc fractions f_disk ≈ 0.01–0.07 against cosmic f_b "
        "[verified: GALAXY_INPUTS.md §4b, citing Burkert+10], i.e. retention 0.07–0.46, widened "
        "to 0.05–0.50.",
        unit="dimensionless",
        default=0.35,
        lo=0.05,
        hi=0.5,
        checkpoint_hypothesis=1,
    ),
    Input(
        "infall_timescale",
        "Infall timescale τ₀ at R₀",
        "control",
        "e-folding time of the gas accretion at the solar radius; τ(R) = τ₀ (R/R₀)ⁿ. "
        "Two-infall framework (Chiappini+97 via Molero+23), per GALAXY_INPUTS.md §3. S2 confirms "
        "the ~7 Gyr: the same source's τ_D(R) = 1.033 R − 1.267 Gyr gives 7.2 Gyr at R₀ [recall: "
        "Chiappini+01], so τ₀ and the inside-out index are two readings of one relation. Range "
        "1–14 Gyr: below 1 the disc is built before it can be observed forming, above a Hubble "
        "time nothing has arrived yet [inferred]. Only one infall episode is modelled — the "
        "second is merger-delivered by ruling 11 and belongs to S3 (debt #14).",
        unit="Gyr",
        default=7.0,
        lo=1.0,
        hi=14.0,
        checkpoint_hypothesis=4,
    ),
    Input(
        "inside_out_index",
        "Inside-out index n",
        "control",
        "Inside-out growth: the outer disc accretes over a longer timescale, τ(R) = τ₀ (R/R₀)ⁿ. "
        "GALAXY_INPUTS.md §3 gives no default, but its own source does: the two-infall framework "
        "it cites uses τ_D(R) = 1.033 R/kpc − 1.267 Gyr [recall: Chiappini+01, the Chiappini+97 "
        "line §3 names], which is linear in R and gives 7.2 Gyr at R₀ = 8.2 kpc — the same ~7 Gyr "
        "§3 quotes for τ₀. So n = 1 and τ₀ = 7 Gyr are one statement, not two, and the default "
        "follows from the citation already in the document rather than from a fit. Range 0–3: "
        "n = 0 is no inside-out growth at all, and beyond 3 the outer disc has not begun forming "
        "[inferred]. Note §3 writes the law with R_d where its own numbers require R₀ (D43).",
        unit="dimensionless",
        default=1.0,
        lo=0.0,
        hi=3.0,
        checkpoint_hypothesis=4,
    ),
    Input(
        "migration_efficiency",
        "Radial migration efficiency",
        "control",
        "Churning strength: the r.m.s. distance a star's guiding centre wanders from its birth "
        "radius, quoted at an age of 8 Gyr and growing as sqrt(age). Ruled in by ruling 4. S2 "
        "confirms the unit is **kpc**, not the provisional dimensionless — a dispersion in radius "
        "has a length, and leaving it dimensionless would have let a kernel width be compared "
        "against a metallicity. Default 3.6 kpc [recall: Frankel et al. measure churning of this "
        "order for the solar neighbourhood over 8 Gyr]. Range 0–8 kpc: zero is no migration, and "
        "beyond about 8 the disc is radially mixed and no gradient survives [inferred]. Acts on "
        "stars only, never gas, so acceptance row 22 does not see it and row 23 does.",
        unit="kpc",
        default=3.6,
        lo=0.0,
        hi=8.0,
        checkpoint_hypothesis=4,
    ),
    # The arm and bar amplitudes were two experimental inputs from RENDER_PLAN M1 (5f79cfc, D171) until
    # S26 derived their means and seeded their residuals on pattern_seed (BUILD_II Phase 1b, D175).
    Input(
        "mergers",
        "Merger events",
        "events",
        "Event list, exempt from the ceiling (GALAXY_INPUTS.md §3). Each event is a "
        "MergerEvent(time, mass_ratio, gas_fraction); the gas_fraction is what dissolved the "
        "second_infall_onset input (ruling 11), being the share of the remaining baryon budget "
        "the event delivers. The Milky Way default is the one major merger its stellar halo "
        "records — Gaia-Enceladus/Sausage, at a lookback of about 10 Gyr and a mass ratio near "
        "1:4 [recall: Helmi+18; Belokurov+18] — plus Sagittarius, which is minor and ongoing "
        "[recall: Ibata+94]. An empty list is a legitimate galaxy and is what debt #9's "
        "merger-free control run passes.",
        default=(
            MergerEvent(
                3.8, 0.25, 0.5,
                "Gaia-Enceladus/Sausage: the last major merger, ~10 Gyr ago, and the event the "
                "two-infall framework needs. Mass ratio ~1:4 from the stellar halo it left.",
            ),
            MergerEvent(
                8.8, 0.02, 0.01,
                "Sagittarius dwarf: minor and still in progress, ~5 Gyr since first pericentre. "
                "Below the major threshold, so it delivers gas without restructuring the disc. Its "
                "progenitor was 10⁸–10⁹ M☉ in all [recall], so the gas it can bring is a few 10⁸ M☉: "
                "0.01 of the budget outstanding after Gaia-Enceladus, about 3 × 10⁸ M☉. The 0.2 that "
                "stood until S13 delivered 5.9 × 10⁹, more than the whole progenitor (debt #29).",
            ),
        ),
        checkpoint_hypothesis=2,
    ),
    Input(
        "world_seed",
        "World seed",
        "seed",
        "Seeds the residual draws of stages 1–3 (e.g. the M_• residual of ruling 10). "
        "Any fixed integer is a valid default; a seed has no Milky Way value.",
        default=0,
        checkpoint_hypothesis=1,
    ),
    Input(
        "pattern_seed",
        "Pattern seed",
        "seed",
        "Seeds the bar and arms, including the PITCH_YU draw (ruling 3). Rerolling it must "
        "invalidate checkpoints 4, 5 and 6 only: since S25 the pattern is checkpoint 3 and star "
        "formation follows it, because the arms shape where stars form and not the reverse (D174).",
        default=0,
        checkpoint_hypothesis=3,
    ),
    Input(
        "systems_seed",
        "Systems seed",
        "seed",
        "Seeds the star catalogue; hash(systems_seed, star_id) makes the sample stable.",
        default=0,
        checkpoint_hypothesis=5,
    ),
    Input(
        "planets_seed",
        "Planets seed",
        "seed",
        "Seeds the planets of a system at the moment it is opened, from "
        "hash(planets_seed, star_id).",
        default=0,
        checkpoint_hypothesis=6,
    ),
    Input(
        "texture_seed",
        "Texture seed",
        "seed",
        "Seeds the randomness layer: the realisations that stand in for physics the model does not compute - "
        "where an arm's phase, a cloud complex or a filament lies. It feeds only the synthetic fields BUILD_III "
        "adds, so rerolling it changes placements and texture and nothing else: no ring total of a field, no "
        "expected ring total of a census, no radial field but the census statistics (what is summed over a "
        "census's realised objects, which a placement re-draws until phase L1), no acceptance row. Its first "
        "reader, since phase P1 (S56, D215), is the arm modes' phases, at the pattern's checkpoint: rerolling it "
        "turns each of the five arm modes by its own angle, so the arms and everything placed by them move, and "
        "no amplitude does; from S55 until that stage existed the seed was accepted and moved nothing (D214). "
        "With the layer off it is not drawn. The draws that existed before "
        "the layer keep the seeds they had: the four cloud texture columns are drawn on the systems seed until L1.",
        default=0,
        checkpoint_hypothesis=3,
    ),
    Input(
        "bar_present",
        "Bar present (a template's pin)",
        "pin",
        "A pin, not a control (S58, D217 item 2): the observed class of one named galaxy - barred or unbarred, "
        "with its source - stated by a template in place of the presence the model derives. True or False "
        "replaces the derived verdict in the published bar_present; given by no template, the model derives it "
        "(the bar's formation time against the disc's age) and nothing is pinned. A measured fact entering as "
        "template structure, not a fit: no parameter is set to a number, and the derived formation time is "
        "still published beside it, so a disagreement between the criterion and the galaxy is visible. No "
        "request offers it: the API takes it from template=<name> alone, it has no range and no default, and "
        "it does not count against the ceiling. An input that is not given is not among a run's inputs.",
        default=None,
        checkpoint_hypothesis=3,
    ),
    Input(
        "pitch_angle",
        "Arm pitch angle (a template's pin)",
        "pin",
        "A pin, not a control (S59, D218 item 6): the measured mean pitch of one named galaxy's arm segments, "
        "with its source, stated by a template in place of the pitch the model draws about its shear law. A "
        "number in degrees: it replaces the drawn value in the published pitch_angle - the winding, the bar's "
        "angle and the gas's response all read it - and the law's own draw is still made on its stream and "
        "published beside it as pitch_angle_drawn, so a disagreement between the law and the galaxy is visible. "
        "A measured mean entering as template structure, as the bar's presence does: nothing is fitted. Given "
        "by no template, nothing is pinned. It is held to the range of the draw it replaces, 1 to 60 degrees - "
        "the range the drawn pitch is kept inside - and refused outside it, by a template and by a run, so the "
        "pitch law's own bounds and the winding read one pitch. No request offers it: the API takes it from "
        "template=<name> alone, it has no default, and it does not count against the ceiling.",
        unit="deg",
        default=None,
        lo=1.0,
        hi=60.0,
        checkpoint_hypothesis=3,
    ),
    Input(
        "sun_bar_angle",
        "Angle of the bar to the Sun-centre line (a template's pin)",
        "pin",
        "A pin, not a control (S59, D218 item 5): for the one galaxy that has an observer inside it, the angle "
        "between the bar's long axis and the line from the Sun to the centre, in degrees, with the bar's near "
        "end ahead of that line in the direction the disc turns. It places the Sun: the published sun_azimuth "
        "is the bar's angle taken back by this much against the rotation. It moves nothing else - no field of "
        "the galaxy reads where the Sun is - and where no template gives it, or the galaxy has no bar, the "
        "Sun's azimuth is not a number. An angle of one turn: 0 up to, not including, 360 degrees, and refused "
        "outside that, by a template and by a run. No request offers it: the API takes it from template=<name> "
        "alone, it has no default, and it does not count against the ceiling.",
        unit="deg",
        default=None,
        lo=0.0,
        hi=360.0,
        hi_open=True,
        checkpoint_hypothesis=3,
    ),
    Input(
        "arm_class",
        "Arm class (a template's pin)",
        "pin",
        "A pin, not a control (S60, D219 item 3): the observed arm class of one named galaxy, with its source, "
        "stated by a template in place of the class the model derives from the bar - a barred disc is a grand "
        "design, an unbarred one multi-armed, with no draw. One of three names. The class decides how the "
        "randomness layer lays the arms' pieces: long chains of pieces in a grand design (and two of them from "
        "the bar's ends) or a multi-armed disc, and single short pieces in a flocculent one. **A flocculent disc "
        "comes from this pin alone**: the model derives none, though half of observed spirals are - a recorded "
        "miss; a draw of the class from the measured frequencies is not made. The pinned class replaces the "
        "derived one in the published arm_class and touches nothing else of the galaxy: no amplitude, no pitch, "
        "no budget of arm power. No request offers it: the API takes it from template=<name> alone, it has no "
        "default, and it does not count against the ceiling.",
        default=None,
        classes=ARM_CLASSES,
        checkpoint_hypothesis=3,
    ),
    Input(
        "arm_pieces",
        "Measured arm pieces (a template's pin)",
        "pin",
        "A pin, not a control (S60, D219 item 8): the mapped arms of one named galaxy that has an observer inside "
        "it, as a table in the source's own form - one row an arm, a logarithmic spiral with one kink, fitted "
        "over a range of azimuth from the galaxy's centre measured from the Sun in the direction the disc "
        "turns: the radius falls with that azimuth as the exponential of minus the azimuth from the kink times "
        "the tangent of the pitch, the pitch one value up to the kink and another past it. Each row becomes a "
        "chain of one or two pinned arm pieces exactly on that locus - two where the two pitches differ - in "
        "place of chains the randomness layer would draw there; beyond its measured range a pinned chain is "
        "continued by drawn pieces to a drawn length, and where no measured arm crosses a ring the layer's own "
        "chains fill it. The rows are placed by the Sun's azimuth, so the pin needs the pinned angle of the bar "
        "to the Sun-centre line and a bar, and is refused without them. Only where the arms are is pinned: their "
        "widths are the model's width law and their amplitude the budget's, every pinned arm alike. A row's "
        "azimuths lie within a turn of the Sun, its kink inside its range, its kink radius is positive and its "
        "pitches are not zero and under 90 degrees either way; a row that is not so is refused, by a template "
        "and by a run. No request offers it: the API takes it from template=<name> alone, it has no default, and "
        "it does not count against the ceiling.",
        default=None,
        columns=ARM_PIECE_COLUMNS,
        defect=arm_rows_defect,
        checkpoint_hypothesis=3,
    ),
)

INPUTS: Mapping[str, Input] = MappingProxyType({i.name: i for i in _INPUTS})
if len(INPUTS) != len(_INPUTS):
    raise RegistryError("duplicate input names in the input table")


def controls(table: Mapping[str, Input] = INPUTS) -> tuple[Input, ...]:
    return tuple(i for i in table.values() if i.kind == "control")


def seeds(table: Mapping[str, Input] = INPUTS) -> tuple[Input, ...]:
    return tuple(i for i in table.values() if i.kind == "seed")


def pins(table: Mapping[str, Input] = INPUTS) -> tuple[Input, ...]:
    """The pins (S58, D217): what a template may state of a galaxy's measured structure. No request offers one."""
    return tuple(i for i in table.values() if i.kind == "pin")


# --- registries ---------------------------------------------------------------

IMPLEMENTATIONS: Registry[Stage] = Registry("stage implementation", lambda s: s.id)
MODELS: Registry[Model] = Registry("model", lambda m: m.name)


def production() -> tuple[Registry[Model], Registry[Stage], Mapping[str, Input]]:
    """The registries with every production stage and model loaded.

    Importing ``galaxy.stages`` and ``galaxy.models`` registers their contents;
    going through this function is how callers avoid forgetting to.
    """
    import galaxy.models  # noqa: F401  (registers models)
    import galaxy.stages  # noqa: F401  (registers implementations)

    return MODELS, IMPLEMENTATIONS, INPUTS
