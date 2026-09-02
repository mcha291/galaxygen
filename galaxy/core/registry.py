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

INPUT_KINDS: tuple[str, ...] = ("control", "seed", "events")

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
    kind: str  # control | seed | events
    about: str
    unit: str | None = None  # required for controls; None for seeds and event lists
    default: object = UNSET
    lo: float | None = None  # control range for the viewer; None = not yet set
    hi: float | None = None
    checkpoint_hypothesis: int | None = None  # GALAXY_PLAN.md §3 grouping; graph.py checks it
    default_owner: str | None = None  # session that owes the default, when UNSET

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
        else:
            if self.unit is not None:
                raise RegistryError(f"input {self.name}: {self.kind} inputs carry no unit")
        if self.kind == "seed" and (
            self.default is UNSET or isinstance(self.default, bool) or not isinstance(self.default, int)
        ):
            raise RegistryError(f"input {self.name}: seeds need an int default")
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

    def __iter__(self) -> Iterator[T]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items


# --- the closed input vector -------------------------------------------------
# 7 controls, 4 seeds, 1 event list [verified: GALAXY_PLAN.md §8; GALAXY_INPUTS.md §3, §11].

_INPUTS: tuple[Input, ...] = (
    Input(
        "halo_mass",
        "Halo mass M₂₀₀",
        "control",
        "Literature spans 0.89–1.3 × 10¹² M☉ (Karukes+19; McMillan), per GALAXY_INPUTS.md §3. "
        "That span is the uncertainty on the Milky Way, not the control range a generator "
        "should offer; S1 sets lo/hi.",
        unit="Msun",
        default=1.1e12,
        checkpoint_hypothesis=1,
    ),
    Input(
        "disc_spin",
        "Disc spin parameter λ_d",
        "control",
        "The spin parameter of the disc, not of the halo (ruling 8). The S1 gate reproduces it "
        "from a joint fit to stellar mass and scale length. Seeding rolls from a halo-λ "
        "log-normal would make every galaxy three times too extended (GALAXY_PLAN.md §7 risk 1).",
        unit="dimensionless",
        default=0.0144,
        checkpoint_hypothesis=1,
    ),
    Input(
        "halo_assembly_z",
        "Halo assembly redshift",
        "control",
        "z ≈ 2–3 in GALAXY_INPUTS.md §3; no single value is given, so the default is owed by S1. "
        "Does two jobs: sets the assembly epoch and derives c₂₀₀ (ruling 5). Renamed from "
        "galaxy_age by ruling 7.",
        unit="dimensionless",
        default_owner="S1",
        checkpoint_hypothesis=1,
    ),
    Input(
        "baryon_retention",
        "Baryon retention fraction",
        "control",
        "Fraction of the cosmic baryon budget the galaxy keeps: f_b × this = m_d ≈ 0.055 "
        "(ruling 9). The ~0.35 in §3 is approximate; S1 confirms or tightens it.",
        unit="dimensionless",
        default=0.35,
        checkpoint_hypothesis=1,
    ),
    Input(
        "infall_timescale",
        "Infall timescale τ₀ at R₀",
        "control",
        "Two-infall framework (Chiappini+97 via Molero+23), per GALAXY_INPUTS.md §3. "
        "The ~7 Gyr is approximate; S2 confirms.",
        unit="Gyr",
        default=7.0,
        checkpoint_hypothesis=3,
    ),
    Input(
        "inside_out_index",
        "Inside-out index n",
        "control",
        "τ(R) = τ₀ (R/R_d)ⁿ; sets the metallicity gradient. No default is given anywhere; "
        "owed by S2.",
        unit="dimensionless",
        default_owner="S2",
        checkpoint_hypothesis=3,
    ),
    Input(
        "migration_efficiency",
        "Radial migration efficiency",
        "control",
        "Dispersion-kernel strength, ruled in by ruling 4. No default and no unit are given; "
        "dimensionless is provisional and S2 confirms both.",
        unit="dimensionless",
        default_owner="S2",
        checkpoint_hypothesis=3,
    ),
    Input(
        "mergers",
        "Merger events",
        "events",
        "Event list, exempt from the ceiling (GALAXY_INPUTS.md §3). Each event carries a "
        "gas_fraction (ruling 11), which dissolved the second_infall_onset input. The event "
        "schema and the Milky Way default history belong to S3; an empty list is not the "
        "Milky Way, so the default stays UNSET until then.",
        default_owner="S3",
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
        "invalidate checkpoints 5 and 6 only.",
        default=0,
        checkpoint_hypothesis=4,
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
)

INPUTS: Mapping[str, Input] = MappingProxyType({i.name: i for i in _INPUTS})
if len(INPUTS) != len(_INPUTS):
    raise RegistryError("duplicate input names in the input table")


def controls(table: Mapping[str, Input] = INPUTS) -> tuple[Input, ...]:
    return tuple(i for i in table.values() if i.kind == "control")


def seeds(table: Mapping[str, Input] = INPUTS) -> tuple[Input, ...]:
    return tuple(i for i in table.values() if i.kind == "seed")


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
