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
        "λ_d = 0.01–0.03 that Burkert+10 need for m_d ≈ 0.05. Debt #10 asks for the re-ruling.",
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
        "Does two jobs: sets the assembly epoch and derives c₂₀₀ = 4.1(1 + z_f) (ruling 5). "
        "Renamed from galaxy_age by ruling 7. GALAXY_INPUTS.md §3 gives z ≈ 2–3 and no single "
        "value; the default is the midpoint, 2.5, which is [inferred] and not a measurement. What "
        "makes it more than a guess is its consequence: c₂₀₀ = 14.4, inside the 10–18 the Milky "
        "Way's own concentration measurements span [verified: GALAXY_INPUTS.md §4b]. The range "
        "0.5–5 covers late assembly to the earliest epoch the relation is quoted for [inferred]. "
        "v_c(R₀) moves about 10 km/s across the cited 2–3, which is three times acceptance row "
        "3's error bar, so this default is load-bearing and unvalidated (debt #12).",
        unit="dimensionless",
        default=2.5,
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
        checkpoint_hypothesis=3,
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
        checkpoint_hypothesis=3,
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
        checkpoint_hypothesis=3,
    ),
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
                8.8, 0.02, 0.2,
                "Sagittarius dwarf: minor and still in progress, ~5 Gyr since first pericentre. "
                "Below the major threshold, so it delivers gas without restructuring the disc.",
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
