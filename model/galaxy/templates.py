"""The templates: named galaxies as data (BUILD_III section 2, Phase T; rule A5 as amended).

A template is a name, a label, an about, the model, its inputs — overrides of the registry's
defaults, its merger list, its seeds — a camera, a filter set, an instrument, its pins, and for a
fitted template the targets, the residuals and the checks ``[verified: DECISIONS.md D213, ruling 1]``.
Nothing here computes: the inputs are resolved against the registry by :func:`resolve`, the fit is
``tools/fit_template.py``'s, the checks are judged by ``galaxy/specs/templates.py``.

**Two are registered.** ``milky_way`` is the default and overrides nothing, so it cannot drift from
the registry's defaults (the gate: a run of it is bit-identical to a run with no inputs given).
``ngc_4414``'s seven controls are the fit's, its merger list is empty and every seed is 4414.

**Every number carries its tag** (rule B14). A target and a check carry their own ``source``; every
other number of a template is tagged in ``sources`` under its dotted path (``camera.fov_deg``,
``inputs.controls.disc_spin``). A number read on a page is ``[verified: READING_NGC_4414.md, <key>]``
with the reading's source key; a display choice of the lead's is ``[inferred]``; a fitted number
says so, with the tool, the date and the test that reproduces it.

**What a template does not hold.** No model output but the fit's own three numbers: a check holds
its window and never the model's number, which only ``python -m galaxy.specs`` prints.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from galaxy.core.fielddoc import IDENT
from galaxy.core.registry import INPUTS, Input, MergerEvent, RegistryError

DEFAULT = "milky_way"

# The tags a number's source string may carry (rule B14's closed set; a fitted number is verified by
# the test that reproduces it).
TAGS: tuple[str, ...] = ("[verified:", "[inferred]", "[recall")


class TemplateError(RegistryError):
    """A template's declaration violates the contract."""


# --- the statistics a target or a check reads off a published field ------------------------


def curve_peak(speed: Any, radius: Any, inside: float) -> float:
    """The largest circular speed at the grid's radii inside ``inside`` kpc."""
    speed, radius = np.asarray(speed, dtype=float), np.asarray(radius, dtype=float)
    return float(speed[radius < inside].max())


def curve_shape(speed: Any, radius: Any, inside: float) -> float:
    """S: the mean circular speed over ``inside`` kpc to the grid's edge, over its maximum inside ``inside``."""
    speed, radius = np.asarray(speed, dtype=float), np.asarray(radius, dtype=float)
    return float(speed[radius >= inside].mean()) / curve_peak(speed, radius, inside)


# ``scalar`` reads a galaxy-level number as published; ``face_on_colour`` is not a field's statistic at
# all but the render's frame through the dust, which galaxy/specs/templates.py computes.
STATISTICS: Mapping[str, Callable[..., float] | None] = MappingProxyType({
    "scalar": None,
    "curve_peak": curve_peak,
    "curve_shape": curve_shape,
    "face_on_colour": None,
})


def measure(statistic: str, value: Any, radius: Any = None, inside: float | None = None) -> float:
    """``statistic`` of a published field: the number a target or a check compares with its window."""
    if statistic == "scalar":
        return float(value)
    fn = STATISTICS.get(statistic)
    if fn is None:
        raise TemplateError(f"statistic {statistic!r} is not read off one field")
    if inside is None:
        raise TemplateError(f"statistic {statistic!r} needs the radius it is taken inside")
    return fn(value, radius, inside)


# --- the declarations --------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Camera:
    """Where the viewer first stands (frontend/e2e/captures.json's convention): inclination from
    face-on, the galactocentric azimuth the camera stands over, half the picture's height at the
    centre's distance, and the lens's field of view."""

    inclination_deg: float
    azimuth_deg: float
    radius_kpc: float
    fov_deg: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.inclination_deg <= 90.0:
            raise TemplateError(f"camera inclination {self.inclination_deg} is outside 0..90 degrees")
        if not self.radius_kpc > 0.0 or not 0.0 < self.fov_deg < 180.0:
            raise TemplateError("camera needs a positive radius and a field of view inside (0, 180) degrees")


@dataclass(frozen=True, slots=True)
class Instrument:
    """What an observer's picture of this galaxy would be taken at. ``None`` is "not read" (rule B9)."""

    distance_mpc: float | None
    pixel_scale_arcsec: float | None


@dataclass(frozen=True, slots=True)
class Target:
    """One measured property the fit sees: the reader's value and window, and what the fit left."""

    name: str
    label: str
    field: str  # the published field the model's number is read off
    statistic: str  # how: STATISTICS
    unit: str
    value: float  # the measured value, as read
    window: tuple[float, float]  # the reader's window, fixed before any model output existed (D113)
    source: str
    model: float  # the model's number at the fitted controls, committed with the fit
    residual: float  # (model - value) / half_window
    inside_kpc: float | None = None  # the radius a curve statistic is taken inside

    def __post_init__(self) -> None:
        _check_window(self.name, self.window, self.source, self.statistic)
        if not self.window[0] <= self.value <= self.window[1]:
            raise TemplateError(f"target {self.name}: the measured value lies outside its own window")

    @property
    def half_window(self) -> float:
        """Half the window's width: the unit the fit's residuals are counted in."""
        return 0.5 * (self.window[1] - self.window[0])

    def residual_of(self, model: float) -> float:
        return (model - self.value) / self.half_window

    def holds(self, model: float) -> bool:
        return self.window[0] <= model <= self.window[1]


@dataclass(frozen=True, slots=True)
class Check:
    """One measured property the fit never sees: its window, the model's quantity, what still differs.

    It holds no model number: the result is the specs' report, never the template's data.
    """

    name: str
    label: str
    unit: str
    window: tuple[float, float]
    quantity: str  # the model's quantity, in words
    mismatch: str  # what still differs between the measurement and the model's quantity
    source: str
    statistic: str
    field: str | None = None  # the published field read; None where the quantity is the render's frame
    inside_kpc: float | None = None

    def __post_init__(self) -> None:
        _check_window(self.name, self.window, self.source, self.statistic)
        if not self.quantity.strip() or not self.mismatch.strip():
            raise TemplateError(f"check {self.name}: the quantity and what still differs are both stated")
        if (self.field is None) != (self.statistic == "face_on_colour"):
            raise TemplateError(f"check {self.name}: a field is named exactly when the statistic reads one")

    def holds(self, model: float) -> bool:
        return self.window[0] <= model <= self.window[1]


def _check_window(name: str, window: tuple[float, float], source: str, statistic: str) -> None:
    if not IDENT.match(name):
        raise TemplateError(f"{name!r} must match {IDENT.pattern}")
    if len(window) != 2 or not window[0] < window[1]:
        raise TemplateError(f"{name}: a window is (lo, hi) with lo < hi, got {window!r}")
    if not any(tag in source for tag in TAGS):
        raise TemplateError(f"{name}: the source carries no tag (rule B14)")
    if statistic not in STATISTICS:
        raise TemplateError(f"{name}: statistic {statistic!r} is not one of {sorted(STATISTICS)}")


@dataclass(frozen=True, slots=True)
class Fit:
    """What the offline search was given and what it left (D213, ruling 3)."""

    targets: tuple[Target, ...]
    tiebreak: float  # the weight of the departures from the defaults in the objective
    objective: str  # the objective in words, with its value at the fitted point
    objective_value: float
    tool: str
    method: str
    date: str
    evaluations: int


@dataclass(frozen=True, slots=True)
class Template:
    name: str
    label: str
    about: str
    model: str
    camera: Camera
    filters: str  # the viewer's filter set, by name: the model holds no filter set
    instrument: Instrument
    controls: Mapping[str, float] = MappingProxyType({})  # overrides of the registry's defaults
    seeds: Mapping[str, int] = MappingProxyType({})
    mergers: tuple[MergerEvent, ...] | None = None  # None: the registry's list; (): no merger
    pins: tuple[Any, ...] = ()  # measured structure that replaces the layer's draw: none until P3-P4
    fit: Fit | None = None
    checks: tuple[Check, ...] = ()
    sources: Mapping[str, str] = MappingProxyType({})  # dotted path of a number -> its tag

    def __post_init__(self) -> None:
        if not IDENT.match(self.name):
            raise TemplateError(f"template name {self.name!r} must match {IDENT.pattern}")
        if not self.label.strip() or not self.about.strip():
            raise TemplateError(f"template {self.name}: label and about are required")
        object.__setattr__(self, "controls", MappingProxyType({k: float(v) for k, v in self.controls.items()}))
        object.__setattr__(self, "seeds", MappingProxyType({k: int(v) for k, v in self.seeds.items()}))
        object.__setattr__(self, "sources", MappingProxyType(dict(self.sources)))
        if self.mergers is not None:
            object.__setattr__(self, "mergers", tuple(self.mergers))
        names = [c.name for c in self.checks]
        if len(set(names)) != len(names):
            raise TemplateError(f"template {self.name}: a check is named twice")

    def validate(self, table: Mapping[str, Input] = INPUTS) -> None:
        """The inputs against the registry, and every number against its tag. Raises on the first defect."""
        for name, value in self.controls.items():
            inp = table.get(name)
            if inp is None or inp.kind != "control":
                raise TemplateError(f"template {self.name}: {name!r} is not a registered control")
            if inp.has_range and not inp.lo <= value <= inp.hi:  # type: ignore[operator]
                raise TemplateError(f"template {self.name}: {name}={value!r} is outside [{inp.lo}, {inp.hi}]")
        for name in self.seeds:
            inp = table.get(name)
            if inp is None or inp.kind != "seed":
                raise TemplateError(f"template {self.name}: {name!r} is not a registered seed")
        if self.mergers is not None and "mergers" not in table:
            raise TemplateError(f"template {self.name}: the registry has no merger list to override")
        missing = [path for path in numbers(self) if path not in self.sources]
        if missing:
            raise TemplateError(f"template {self.name}: no source for {missing} (rule B14)")
        for path, source in self.sources.items():
            if not any(tag in source for tag in TAGS):
                raise TemplateError(f"template {self.name}: the source of {path} carries no tag (rule B14)")
        if self.fit is not None:
            fitted = {t.field for t in self.fit.targets}
            seen = fitted & {c.field for c in self.checks if c.statistic == "scalar"}
            if seen:
                raise TemplateError(f"template {self.name}: the fit sees {sorted(seen)}, so they are not checks")


def numbers(template: Template) -> tuple[str, ...]:
    """The dotted path of every number a template states outside its targets and checks (which carry
    their own source): the overridden inputs, the camera, what the instrument holds."""
    paths = [f"inputs.controls.{n}" for n in template.controls]
    paths += [f"inputs.seeds.{n}" for n in template.seeds]
    if template.mergers is not None:
        paths.append("inputs.mergers")
    paths += [f"camera.{n}" for n in ("inclination_deg", "azimuth_deg", "radius_kpc", "fov_deg")]
    paths += [f"instrument.{n}" for n in ("distance_mpc", "pixel_scale_arcsec") if getattr(template.instrument, n) is not None]
    return tuple(paths)


def overrides(template: Template) -> dict[str, Any]:
    """Only what the template sets: the base a request's own inputs are laid over. ``milky_way``'s is empty."""
    out: dict[str, Any] = {**template.controls, **template.seeds}
    if template.mergers is not None:
        out["mergers"] = template.mergers
    return out


def resolve(template: Template, table: Mapping[str, Input] = INPUTS, accepted: tuple[str, ...] | None = None) -> dict[str, Any]:
    """The template's full input mapping: its overrides on the registry's defaults, in the registry's order.

    ``accepted`` restricts it to the inputs a model takes (``Model.input_names``). An input with no default
    and no override is left out, as the runner leaves it (rule B9).
    """
    given = overrides(template)
    out: dict[str, Any] = {}
    for name in tuple(table) if accepted is None else accepted:
        if name in given:
            out[name] = given[name]
        elif not table[name].unset:
            out[name] = table[name].default
    return out


# --- the two templates ---------------------------------------------------------------------

_READING = "READING_NGC_4414.md"
# The edge of NGC 4414's inner disc, where its HI curve's gentle decline ends and the warped outer disc
# begins: 240 arcsec at 17.7 Mpc [verified: READING_NGC_4414.md, rows 4-6; dB14 Sect. 3.2 "out to R ~ 240
# arcsec"; 240 x 0.08581 kpc/arcsec = 20.6 kpc].
NGC_4414_INNER_DISC_KPC = 20.6
_FITTED = (
    "fitted 2026-10-04 by tools/fit_template.py ngc_4414 (D213, ruling 3) "
    "[verified: tests/test_templates.py::test_the_committed_fit_is_where_the_search_stops_and_reproduces_its_numbers]"
)
_SEED = (
    "[inferred] a seed has no measured value and none is chosen for the picture: every seed is the "
    "catalogue number, 4414 [verified: DECISIONS.md D213, ruling 4]"
)

MILKY_WAY = Template(
    name="milky_way",
    label="Milky Way",
    about=(
        "The default galaxy: the registry's defaults, every one a measured value of the Milky Way or derived "
        "from one (rule A5). The template overrides no input, so it is the defaults by construction; its "
        "merger list is the registry's two events and its seeds the registry's. Seen face-on."
    ),
    model="azimuthal",
    camera=Camera(inclination_deg=0.0, azimuth_deg=270.0, radius_kpc=20.0, fov_deg=45.0),
    filters="rgb",
    instrument=Instrument(distance_mpc=None, pixel_scale_arcsec=None),
    sources={
        "camera.inclination_deg": "[inferred] a display choice: the Milky Way stands face-on [verified: BUILD_III.md section 2]",
        "camera.azimuth_deg": "[inferred] a display choice: the viewer's face-on preset, a turn of the picture "
                              "[verified: frontend/e2e/captures.json, the camera's about]",
        "camera.radius_kpc": "[inferred] a display choice: half the picture's height, the viewer's landing frame "
                             "[verified: frontend/e2e/captures.json, face-on-field]",
        "camera.fov_deg": "[inferred] a display choice: the viewer's own perspective "
                          "[verified: DECISIONS.md D213, ruling 5: milky_way keeps 45 degrees]",
    },
)

NGC_4414 = Template(
    name="ngc_4414",
    label="NGC 4414",
    about=(
        "An unbarred flocculent Sc spiral at 17.7 Mpc, seen at 55 degrees. Its seven controls are fitted to three "
        "measured properties - the rotation curve's peak, the stellar disc's scale length and the stellar mass - "
        "and what the fit could not remove is published beside them: all three land inside their windows, none on "
        "its value, and three controls end on a bound of their range. Five more measured properties the fit never "
        "saw are checks, judged by the specs. Nothing measures its mergers or its seeds, so the merger list is "
        "empty and every seed is 4414. The model draws it with a bar and with regular arms: no source finds a "
        "bar in NGC 4414 and its arms are flocculent, and a template takes its measured structure as pins only "
        "from build phases P3 and P4 on. The position angle (159 degrees) is not applied: the camera has no roll."
    ),
    model="azimuthal",
    # The seven controls as the fit leaves them (tools/fit_template.py ngc_4414, 2026-10-04), copied by hand
    # from the tool's output at full precision: the search stops on a stepped objective, so a rounded value
    # is another point. Three stand on a bound of their range - the halo assembled as late, the baryons kept
    # as fully and the gas fallen in as fast as the ranges allow - and migration_efficiency is unmoved: the
    # three targets do not see it. That is the fit's finding, published and not tuned away (B5).
    controls={
        "halo_mass": 589186551731.6183,
        "disc_spin": 0.014085408391676634,
        "halo_assembly_z": 0.5,
        "baryon_retention": 0.5,
        "infall_timescale": 1.0,
        "inside_out_index": 0.45000000000000007,
        "migration_efficiency": 3.6,
    },
    seeds={"world_seed": 4414, "pattern_seed": 4414, "systems_seed": 4414, "planets_seed": 4414},
    mergers=(),
    camera=Camera(inclination_deg=55.0, azimuth_deg=0.0, radius_kpc=15.0, fov_deg=5.0),
    filters="wfc3",
    instrument=Instrument(distance_mpc=17.7, pixel_scale_arcsec=None),
    pins=(),
    fit=Fit(
        targets=(
            Target(
                name="curve_peak",
                label="Peak rotation speed",
                field="circular_velocity",
                statistic="curve_peak",
                inside_kpc=NGC_4414_INNER_DISC_KPC,
                unit="km/s",
                value=237.0,
                window=(222.0, 247.0),
                source=(
                    f"[verified: {_READING}, row 4 and window W-A; P16 (Ponomareva, Verheijen & Bosma 2016, "
                    "Table 5): V_max = 237 +/- 10 km/s from HI tilted rings at i = 52; the lower edge is the "
                    "same line-of-sight speed deprojected at 57 degrees]. The model's number is the largest "
                    "circular speed inside 20.6 kpc [verified: DECISIONS.md D213, ruling 3]"
                ),
                model=238.8482146686635,
                residual=0.14785717349308014,
            ),
            Target(
                name="disc_scale_length",
                label="Stellar disc scale length",
                field="thin_disc_scale_length",
                statistic="scalar",
                unit="kpc",
                value=1.649,
                window=(1.5, 1.9),
                source=(
                    f"[verified: {_READING}, row 7 and window W-D; S4G (Salo et al. 2015, pipeline 4, table 7): "
                    "h_r = 19.22 arcsec at 3.6 micron, 1.649 kpc at 17.7 Mpc; Wat19's two inner segments span "
                    "the window with the distance bracket]"
                ),
                model=1.673357386927466,
                residual=0.12178693463733017,
            ),
            Target(
                name="stellar_mass",
                label="Stellar mass",
                field="stellar_mass_total",
                statistic="scalar",
                unit="Msun",
                value=10.0**10.65,
                window=(3.4e10, 5.9e10),
                source=(
                    f"[verified: {_READING}, row 8 and window W-E; z0MGS (Leroy et al. 2019, table 4): "
                    "log M* = 10.65 +/- 0.10 at 17.7 Mpc, WISE 3.4 micron, a Kroupa-type IMF]"
                ),
                model=39731914953.735306,
                residual=-0.39491554090888364,
            ),
        ),
        tiebreak=1e-3,
        objective=(
            "the sum over the three targets of ((model - value) / half-window)^2, plus 0.001 times the sum over "
            "the seven controls of ((fitted - default) / (hi - lo))^2: the tie-break keeps a control nothing "
            "measures at the Milky Way's value and is not a prior with weight. At the fitted point it is 0.1931: "
            "0.1927 from the targets, 0.0004 from the tie-break"
        ),
        objective_value=0.19308404030467408,
        tool="tools/fit_template.py ngc_4414",
        method=(
            "damped Gauss-Newton (Levenberg-Marquardt) with a coordinate search in every step: 24 steps from the "
            "registry's defaults, in the logarithm of each control whose range starts above zero, the targets "
            "differenced in each coordinate at 0.04, 0.02, 0.01 of its span in turn, 4 damped trial steps solved "
            "inside the published ranges, the lowest of the trial and differencing points taken when it is lower"
        ),
        date="2026-10-04",
        evaluations=433,
    ),
    checks=(
        Check(
            name="curve_shape",
            label="The curve's shape, S = outer speed over peak",
            unit="dimensionless",
            window=(0.71, 0.86),
            quantity="mean circular_velocity over 20.6 kpc to the grid's edge (30 kpc), over its maximum inside 20.6 kpc",
            mismatch="The window's outer range is 20.6–41.2 kpc, a warped disc",
            source=(
                f"[verified: {_READING}, row 6 and window W-C; P16 Table 5: V_flat / V_max = 185 / 237 = 0.78, "
                "the outer inclination's systematic on V_flat in quadrature]"
            ),
            statistic="curve_shape",
            field="circular_velocity",
            inside_kpc=NGC_4414_INNER_DISC_KPC,
        ),
        Check(
            name="star_formation_rate",
            label="Star formation rate",
            unit="Msun/yr",
            window=(1.8, 4.7),
            quantity="sfr",
            mismatch="FUV + 22 µm on a Kroupa-type scale",
            source=(
                f"[verified: {_READING}, row 11 and window W-H; z0MGS (Leroy et al. 2019, table 4): "
                "log SFR = 0.46 +/- 0.20, the distance in quadrature]"
            ),
            statistic="scalar",
            field="sfr",
        ),
        Check(
            name="hydrogen_mass",
            label="Gas: atomic and molecular hydrogen",
            unit="Msun",
            window=(7.4e9, 14.7e9),
            quantity="hydrogen_mass_30kpc",
            mismatch="28 % of the HI lies beyond 20.6 kpc; X_CO",
            source=(
                f"[verified: {_READING}, rows 9 and 10 and section 3's total hydrogen: the HI window [3.8, 6.3] and the "
                "H2 window [3.6, 8.4] x 10^9 Msun summed edge to edge; dB14, Pin18, H03 (Helfer et al. 2003, Table 4)]"
            ),
            statistic="scalar",
            field="hydrogen_mass_30kpc",
        ),
        Check(
            name="absolute_magnitude_k",
            label="Absolute K magnitude",
            unit="mag",
            window=(-24.62, -24.12),
            quantity="absolute_magnitude_k",
            mismatch="The window allows 0.15 mag of internal extinction",
            source=(
                f"[verified: {_READING}, row 12 and window W-I; 2MRS (Huchra et al. 2012) K_s = 6.939 and "
                "HyperLeda kt = 6.98 at the three Cepheid distances]"
            ),
            statistic="scalar",
            field="absolute_magnitude_k",
        ),
        Check(
            name="colour_b_v_face_on",
            label="B − V, face-on, attenuated",
            unit="mag",
            window=(0.72, 0.82),
            quantity="the face-on render's frame, B − V through the dust",
            mismatch="RC3's statistical correction to face-on",
            source=(
                f"[verified: {_READING}, row 14 and window W-K; RC3 (B-V)_T0 = 0.77 and HyperLeda bvtc = 0.77, "
                "corrected to face-on and still attenuated, +/- 0.05 from the observed totals' spread]"
            ),
            statistic="face_on_colour",
        ),
    ),
    sources={
        **{f"inputs.controls.{name}": _FITTED for name in (
            "halo_mass", "disc_spin", "halo_assembly_z", "baryon_retention", "infall_timescale",
            "inside_out_index", "migration_efficiency",
        )},
        **{f"inputs.seeds.{name}": _SEED for name in ("world_seed", "pattern_seed", "systems_seed", "planets_seed")},
        "inputs.mergers": (
            "[verified: DECISIONS.md D213, ruling 4: no merger of NGC 4414 was read, and what nothing measures is "
            "not invented - the list is empty and not the Milky Way's two events]"
        ),
        "camera.inclination_deg": (
            f"[verified: {_READING}, row 2; W04 (Wong, Blitz & Bosma 2004, Tables 1 and 3): i = 55 +/- 2 from the CO + HI "
            "kinematic fit, the inner disc the picture shows]; the reading's range is 52-57 degrees and the HI "
            "kinematic 52.3 (dB14) is the named alternative"
        ),
        "camera.azimuth_deg": "[inferred] arbitrary: which side of NGC 4414 is the near one was not read [verified: DECISIONS.md D213, ruling 5]",
        "camera.radius_kpc": (
            "[inferred] a display choice: half the picture's height, set to hold the disc out to its 3.6 micron "
            "isophote of 25.5 AB mag per square arcsec with an eighth to spare - a semi-major axis of 153.5 arcsec, "
            f"13.2 kpc at 17.7 Mpc [verified: {_READING}, S4G (Sheth et al. 2010 catalogue v2)] - which is 9.1 of "
            "the measured scale lengths (1.649 kpc); the goal picture's own framing was not read"
        ),
        "camera.fov_deg": (
            "[inferred] a display choice: a long lens, so the perspective puts no lopsidedness into an inclined "
            "picture - at 5 degrees the near side is magnified by under 4 % [verified: DECISIONS.md D213, ruling 5]"
        ),
        "instrument.distance_mpc": (
            f"[verified: {_READING}, row 1; F01 (Freedman et al. 2001, Table 4): mu_Z = 31.24, D_Z = 17.70 Mpc, "
            "Cepheids, metallicity-corrected; the bracket of the three Cepheid values is 16.6-19.1 Mpc]"
        ),
    },
)

TEMPLATES: Mapping[str, Template] = MappingProxyType({t.name: t for t in (MILKY_WAY, NGC_4414)})
if DEFAULT not in TEMPLATES or next(iter(TEMPLATES)) != DEFAULT:
    raise TemplateError(f"the default template {DEFAULT!r} leads the registry")
if overrides(TEMPLATES[DEFAULT]):
    raise TemplateError("the default template overrides nothing: it is the registry's defaults (D213, ruling 1)")
for _template in TEMPLATES.values():
    _template.validate()


def names() -> tuple[str, ...]:
    return tuple(TEMPLATES)


def get(name: str) -> Template:
    try:
        return TEMPLATES[name]
    except KeyError:
        raise KeyError(f"no template named {name!r}; registered: {list(TEMPLATES)}") from None
