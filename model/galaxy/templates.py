"""The templates: named galaxies as data (BUILD_III section 2, Phase T; rule A5 as amended).

A template is a name, a label, an about, the model, its inputs — overrides of the registry's
defaults, its merger list, its seeds — a camera, a filter set, an instrument, its pins, and for a
fitted template the targets, the residuals and the checks ``[verified: DECISIONS.md D213, ruling 1]``.
Nothing here computes: the inputs are resolved against the registry by :func:`resolve`, the fit is
``tools/fit_template.py``'s, the checks are judged by ``galaxy/specs/templates.py``.

**Two are registered.** ``milky_way`` is the default and overrides no control, no seed and no event
list, so it cannot drift from the registry's defaults (the gate: a run of it is bit-identical to a
run with no inputs given). ``ngc_4414`` sets the four controls its fit's targets measure and leaves
the other three to the registry; its merger list is empty and every seed is 4414.

**Pins** (S58, DECISIONS.md D217 item 2). A pin is a measured fact about the galaxy's structure that
replaces what the model would derive or draw: a :class:`Pin` names one of the registry's pin inputs,
states its value and carries its source. It is "a measured fact entering as template structure, not a
fit". Since S60 (D219 items 3 and 8) there are five, and each template holds three: ``arm_class``, the observed
arm class, one of three names - ``ngc_4414`` pins flocculent, which the model derives of no disc - and
``arm_pieces``, a table: the measured arms of the one galaxy with an observer inside it, each row a kinked
logarithmic spiral over a range of azimuth from the Sun, which ``milky_way`` gives (Reid et al. 2019's four
major arms and the Local arm) and which places pinned arm pieces with the randomness layer on and nothing with
it off. The three of S58-S59 (D218 items 5-6): ``bar_present``, the observed
class, True or False - ``milky_way`` pins barred and ``ngc_4414`` unbarred; ``sun_bar_angle``, the
angle of the bar to the Sun-centre line in degrees, which ``milky_way`` gives (30) and which places
the published Sun's azimuth and moves no other field; and ``pitch_angle``, the measured mean pitch of
the arms in degrees, which ``ngc_4414`` gives (28.9) in place of the pitch the model draws - the draw
is still published beside it. **A pin that is a measured number is held to the range of what it
replaces** (the gate's follow-up, item 7: the pitch 1-60 degrees, the Sun's angle 0 up to 360) and
refused outside it, here (:meth:`Template.validate`) and at ``run()``. A pin travels with the
template's inputs (:func:`overrides`, :func:`resolve`), so every run of a template is the pinned
galaxy; no request gives one directly. **The default template's pins move no field the bare default
run publishes as a number**: ``bar_present`` restates what the model derives at the registry's
defaults (the criterion says barred there), and ``sun_bar_angle`` is read by ``sun_azimuth`` alone -
a number in the template's run and not a number without the pin. Every other field is bit for bit the
bare run's - that is the gate above, still - but a run of the template and a run with no inputs are
two points in input space: their ``inputs`` differ by the pins, and by nothing else.

**A fit's free set is a rule, in data** ``[verified: DECISIONS.md D213, as amended at the gate, ruling 1]``:
a control is free only if a fit target measures what it controls, and ``Fit.free`` names that target
beside each free control. Every other control is not stated by the template at all, so it is the
registry's default by construction and cannot move by any amount. A free control that ends on a bound
of its range is a finding, labelled in ``Fit.bounds`` with the finding written out (ruling 3).

**Every number carries its tag** (rule B14). A target and a check carry their own ``source``; every
other number of a template is tagged in ``sources`` under its dotted path (``camera.fov_deg``,
``inputs.controls.disc_spin``). A number read on a page is ``[verified: READING_NGC_4414.md, <key>]``
with the reading's source key; a display choice of the lead's is ``[inferred]``; a fitted number
says so, with the tool, the date and the test that reproduces it.

**What a template does not hold.** No model output of the galaxy as it stands but the fit's own three
numbers: a check holds its window and never the model's number, which only ``python -m galaxy.specs``
prints. A check does hold its **first reading** where it has one - the value read once, blind, on a
fit since withdrawn - and its **standing**: ``disclosed`` where the fit it is judged on was decided
after that reading (ruling 2), so no verdict on it is ever called blind.
"""

from __future__ import annotations

import math
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
class Pin:
    """One measured fact of the galaxy's structure, stated in place of what the model derives (D217 item 2).

    ``name`` is a pin input of the registry (kind ``pin``); ``value`` is the observed class, True or False,
    or - since S59 (D218 items 5-6), for a pin the registry gives a unit - a measured number in that unit;
    or - since S60 (D219 items 3 and 8) - the name of a class of more than two, or the rows of a measured table
    (a tuple of tuples: the source's own columns, as the registry's pin declares them).
    ``source`` carries its tag (rule B14). Nothing is fitted: the model's derivation or draw is replaced, and
    what it would have said is still published beside the pinned value. Which of the four a pin is, is the
    registry's (``Input.shape``), and a template is held to it when it is built.
    """

    name: str
    value: bool | float | str | tuple
    source: str

    def __post_init__(self) -> None:
        if not IDENT.match(self.name):
            raise TemplateError(f"pin name {self.name!r} must match {IDENT.pattern}")
        if isinstance(self.value, list):
            object.__setattr__(self, "value", tuple(tuple(row) if isinstance(row, list) else row for row in self.value))
        number = isinstance(self.value, (int, float)) and not isinstance(self.value, bool) and math.isfinite(self.value)
        named = isinstance(self.value, str) and bool(self.value.strip())
        table = isinstance(self.value, tuple) and bool(self.value) and all(isinstance(row, tuple) for row in self.value)
        if not (isinstance(self.value, bool) or number or named or table):
            raise TemplateError(
                f"pin {self.name}: the observed class is True or False or a class's name, or a measured finite number, "
                f"or the rows of a measured table; got {self.value!r}"
            )
        if not any(tag in self.source for tag in TAGS):
            raise TemplateError(f"pin {self.name}: the source carries no tag (rule B14)")


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


STANDINGS: tuple[str, ...] = ("blind", "disclosed")
VERDICTS: tuple[str, ...] = ("pass", "fail")


@dataclass(frozen=True, slots=True)
class FirstReading:
    """A check's value as it was read once on an earlier fit of the template, since withdrawn: a record, kept
    beside the check so the specs' report prints it next to the verdict on the fit that stands."""

    fit: str  # the fit it was read on, as the decision record names it
    value: float  # as the specs' report printed it
    verdict: str  # pass | fail, against the same window
    standing: str  # blind: read before any model output for the template existed
    source: str

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS or self.standing not in STANDINGS:
            raise TemplateError(f"a first reading's verdict is one of {VERDICTS} and its standing one of {STANDINGS}")
        if not any(tag in self.source for tag in TAGS):
            raise TemplateError("a first reading's source carries no tag (rule B14)")


@dataclass(frozen=True, slots=True)
class Check:
    """One measured property the fit never sees: its window, the model's quantity, what still differs.

    It holds no model number of the template as it stands: that result is the specs' report, never the
    template's data. It holds its standing - ``blind`` if the fit it is judged on was fixed before any of
    the checks was read, ``disclosed`` if not, with the sentence that says why - and the first reading where
    one was spent on a withdrawn fit.
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
    standing: str = "blind"
    standing_about: str = ""  # one sentence: why the verdict on the fit that stands is not blind
    first_reading: FirstReading | None = None

    def __post_init__(self) -> None:
        _check_window(self.name, self.window, self.source, self.statistic)
        if not self.quantity.strip() or not self.mismatch.strip():
            raise TemplateError(f"check {self.name}: the quantity and what still differs are both stated")
        if (self.field is None) != (self.statistic == "face_on_colour"):
            raise TemplateError(f"check {self.name}: a field is named exactly when the statistic reads one")
        if self.standing not in STANDINGS:
            raise TemplateError(f"check {self.name}: standing {self.standing!r} is not one of {STANDINGS}")
        if (self.standing == "disclosed") != bool(self.standing_about.strip()):
            raise TemplateError(f"check {self.name}: a disclosed check says why in one sentence, a blind one says nothing")
        if self.first_reading is not None:
            if self.standing != "disclosed":
                raise TemplateError(f"check {self.name}: a check read once already is disclosed on any later fit")
            if (self.first_reading.verdict == "pass") != self.holds(self.first_reading.value):
                raise TemplateError(f"check {self.name}: the first reading's verdict is not its value against the window")

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
    """What the offline search was given and what it left (D213, ruling 3 as amended at the gate).

    ``free`` is the fit's free set, fixed by a rule and not by a weight: a control is free only if a target
    measures what it controls, and the mapping names that target beside each one. No other control is the
    search's to move. ``bounds`` labels each free control the search left on a bound of its published range,
    with the finding written out: a value on a bound is a finding, not a fit.
    """

    targets: tuple[Target, ...]
    free: Mapping[str, str]  # free control -> the name of the target that measures it
    measures: Mapping[str, str]  # free control -> how that target measures it, in words
    bounds: Mapping[str, str]  # free control left on a bound -> the finding, with its debt
    tiebreak: float  # the weight of the free controls' departures from the defaults in the objective
    objective: str  # the objective in words, with its value at the fitted point
    objective_value: float
    tool: str
    method: str
    date: str
    evaluations: int

    def __post_init__(self) -> None:
        for name in ("free", "measures", "bounds"):
            object.__setattr__(self, name, MappingProxyType(dict(getattr(self, name))))
        targets = {t.name for t in self.targets}
        if not self.free:
            raise TemplateError("a fit names its free controls: none is admitted any other way")
        for control, target in self.free.items():
            if target not in targets:
                raise TemplateError(f"free control {control}: {target!r} is not one of the fit's targets")
        if set(self.measures) != set(self.free) or not all(v.strip() for v in self.measures.values()):
            raise TemplateError("every free control says how its target measures it")
        if not set(self.bounds) <= set(self.free) or not all(v.strip() for v in self.bounds.values()):
            raise TemplateError("only a free control can stand on a bound, and its finding is written out")


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
    # Measured structure that replaces what the model derives or the layer draws. Since P3 (S58, D217): the
    # observed bar class, ``bar_present``.
    pins: tuple[Pin, ...] = ()
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
        object.__setattr__(self, "pins", tuple(self.pins))
        pinned = [p.name for p in self.pins if isinstance(p, Pin)]
        if len(pinned) != len(self.pins) or len(set(pinned)) != len(pinned):
            raise TemplateError(f"template {self.name}: pins are Pin declarations, each input pinned once")
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
        for pin in self.pins:
            inp = table.get(pin.name)
            if inp is None or inp.kind != "pin":
                raise TemplateError(f"template {self.name}: {pin.name!r} is not a registered pin")
            shape = inp.shape
            if shape in ("named", "table"):
                # S60 (D219 items 3 and 8): one of the pin's named classes, or the rows of its table - held to the
                # registry's declaration by the registry's own check, which a run applies too.
                try:
                    inp.pinned(pin.value)
                except RegistryError as e:
                    raise TemplateError(f"template {self.name}: {e}") from None
                continue
            if (shape == "class") != isinstance(pin.value, bool) or isinstance(pin.value, (str, tuple)):
                raise TemplateError(
                    f"template {self.name}: pin {pin.name!r} is "
                    + ("a class, True or False" if inp.unit is None else f"a measured number in {inp.unit}")
                    + f", got {pin.value!r}"
                )
            # S59 (D218, the gate's follow-up, item 7): a measured number is held to the range of what it replaces.
            if inp.unit is not None and not inp.admits(float(pin.value)):
                raise TemplateError(
                    f"template {self.name}: pin {pin.name!r} is held to the range of what it replaces, "
                    f"{inp.range_text} {inp.unit}; got {pin.value!r}"
                )
        # S60 (D219 item 8): measured arms are given in azimuth from the Sun, so a template that pins them pins
        # where the Sun is - the bar's angle to the Sun-centre line - and a bar for that angle to be measured from.
        stated = {p.name: p.value for p in self.pins}
        if "arm_pieces" in stated and not (stated.get("bar_present") is True and "sun_bar_angle" in stated):
            raise TemplateError(
                f"template {self.name}: pinned arm pieces are placed by the Sun's azimuth: the template pins "
                "bar_present True and sun_bar_angle with them"
            )
        missing =[path for path in numbers(self) if path not in self.sources]
        if missing:
            raise TemplateError(f"template {self.name}: no source for {missing} (rule B14)")
        for path, source in self.sources.items():
            if not any(tag in source for tag in TAGS):
                raise TemplateError(f"template {self.name}: the source of {path} carries no tag (rule B14)")
        if self.fit is not None:
            # The free set is the stated set: a control the targets do not measure is not stated, so it is the
            # registry's default and cannot have moved; a free control on a bound is labelled, and only those.
            if set(self.controls) != set(self.fit.free):
                raise TemplateError(
                    f"template {self.name}: the controls it states {sorted(self.controls)} are not the fit's free "
                    f"set {sorted(self.fit.free)}: a control no target measures stays at the registry's default"
                )
            on_bound = {n for n, v in self.controls.items() if v in (table[n].lo, table[n].hi)}
            if on_bound != set(self.fit.bounds):
                raise TemplateError(
                    f"template {self.name}: {sorted(on_bound)} stand on a bound and {sorted(self.fit.bounds)} are "
                    "labelled: a value on a bound is a finding and is written out"
                )
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


def pinned(template: Template) -> dict[str, bool | float]:
    """The template's pins as inputs: {pin input: the observed class, or the measured number} (S58, D217 item
    2; S59, D218 items 5-6)."""
    return {p.name: p.value for p in template.pins}


def overrides(template: Template) -> dict[str, Any]:
    """Only what the template sets: the base a request's own inputs are laid over - its controls, its seeds, its
    merger list, and its pins. ``milky_way``'s holds its two pins and nothing else: no control, no seed and no
    event list, so it is the registry's defaults; its ``bar_present`` restates what the model derives there
    and its ``sun_bar_angle`` places the Sun and moves no other field (S59, D218 item 5)."""
    out: dict[str, Any] = {**template.controls, **template.seeds}
    if template.mergers is not None:
        out["mergers"] = template.mergers
    out.update(pinned(template))
    return out


def resolve(template: Template, table: Mapping[str, Input] = INPUTS, accepted: tuple[str, ...] | None = None) -> dict[str, Any]:
    """The template's full input mapping: its overrides on the registry's defaults, in the registry's order.

    ``accepted`` restricts it to the inputs a model takes (``Model.input_names``). An input with no default
    and no override is left out, as the runner leaves it (rule B9); so is a pin the template does not state
    (S58, D217: a pin has no default - not given, the model derives).
    """
    given = overrides(template)
    out: dict[str, Any] = {}
    for name in tuple(table) if accepted is None else accepted:
        if name in given:
            out[name] = given[name]
        elif not table[name].unset and table[name].kind != "pin":
            out[name] = table[name].default
    return out


# --- the two templates ---------------------------------------------------------------------

_READING = "READING_NGC_4414.md"
# The edge of NGC 4414's inner disc, where its HI curve's gentle decline ends and the warped outer disc
# begins: 240 arcsec at 17.7 Mpc [verified: READING_NGC_4414.md, rows 4-6; dB14 Sect. 3.2 "out to R ~ 240
# arcsec"; 240 x 0.08581 kpc/arcsec = 20.6 kpc].
NGC_4414_INNER_DISC_KPC = 20.6
_FITTED = (
    "fitted 2026-10-04 by tools/fit_template.py ngc_4414, free because a target measures it (D213 as amended at "
    "the gate, ruling 1): a point on a plateau resolved to the model's own steps, not a minimum to the printed "
    "precision "
    "[verified: tests/test_templates.py::test_the_committed_fit_is_where_the_search_stops_and_reproduces_its_numbers]"
)
# Why every verdict on the fit that stands is disclosed and none is blind (D213 as amended, ruling 2).
_DISCLOSED = (
    "The fit this check is judged on was decided after four of the five checks had been read on fit A, and read "
    "is read: its verdict is disclosed, never blind (D213, amended at the gate)."
)
_FIT_A = "[verified: DECISIONS.md D213, 'The first reading: fit A': read once on the production grid, 2026-10-04, blind]"


def _first(value: float, verdict: str) -> FirstReading:
    return FirstReading(fit="fit A", value=value, verdict=verdict, standing="blind", source=_FIT_A)

_SEED = (
    "[inferred] a seed has no measured value and none is chosen for the picture: every seed is the "
    "catalogue number, 4414 [verified: DECISIONS.md D213, ruling 4]"
)

# --- the Milky Way's measured arms (S60, DECISIONS.md D219 item 8) -------------------------------------------------
#
# Reid et al. 2019's maser-fitted spiral arms, Table 2 as printed, the uncertainties left out: each row an arm as
# one logarithmic spiral with a kink, ln(R/R_kink) = −(β − β_kink) tan ψ, ψ = ψ_< for β ≤ β_kink and ψ_> for
# β > β_kink; β the Galactocentric azimuth, 0 towards the Sun and increasing in the direction of Galactic rotation;
# R0 = 8.15 kpc [verified: Reid et al. 2019, ApJ 885, 131 = arXiv:1910.03357, Table 2 and note,
# https://arxiv.org/pdf/1910.03357; all seven rows, two reads of the PDF text agree digit for digit;
# docs/READING_ARM_SEGMENTS.md A1.3]. Columns: (arm, β from, β to, β_kink in degrees, R_kink in kpc, ψ_<, ψ_> in
# degrees) - the registry's ``ARM_PIECE_COLUMNS``. Until S60 the table lived in ``tests/reid2019.py`` as the
# definition of a disclosed check; it is the template's own data since the arms are pinned, and the test module
# reads it from here.
REID_2019_R0 = 8.15  # kpc: the table's own distance of the Sun from the centre
REID_2019_TABLE2: tuple[tuple[str, float, float, float, float, float, float], ...] = (
    ("3-kpc(N)", 15.0, 18.0, 15.0, 3.52, -4.2, -4.2),
    ("Norma", 5.0, 54.0, 18.0, 4.46, -1.0, 19.5),
    ("Sct-Cen", 0.0, 104.0, 23.0, 4.91, 14.1, 12.1),
    ("Sgr-Car", 2.0, 97.0, 24.0, 6.04, 17.1, 1.0),
    ("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4),
    ("Perseus", -23.0, 115.0, 40.0, 8.87, 10.3, 8.7),
    ("Outer", -16.0, 71.0, 18.0, 12.24, 3.0, 9.4),
)
# The rows the template pins: the four major arms - Norma-Outer, Scutum-Centaurus, Sagittarius-Carina, Perseus -
# and the Local arm (D219 item 8). The source reads Norma and the Outer arm as one arm and fits it in two
# stretches with nothing measured between them (Table 2 has no row for the Outer-Scutum-Centaurus arm either):
# **each of the two rows is entered as its own chain**, so the four major arms are five pinned chains and the
# Local arm a sixth. The 3-kpc arm's row is left out ("associated with the Galactic bar and may not be true
# spiral arms").
MILKY_WAY_PINNED_ARMS: tuple[str, ...] = ("Norma", "Sct-Cen", "Sgr-Car", "Local", "Perseus", "Outer")

MILKY_WAY = Template(
    name="milky_way",
    label="Milky Way",
    about=(
        "The default galaxy: the registry's defaults, every one a measured value of the Milky Way or derived "
        "from one (rule A5). The template overrides no control, no seed and no event list, so it is the defaults "
        "by construction; its merger list is the registry's two events and its seeds the registry's. It pins three "
        "measured facts of its structure: the Milky Way is barred, which the model derives too at these inputs, "
        "so that pin changes no number; its bar stands 30 degrees from the line from the Sun to the centre, "
        "the near end ahead of the Sun in the direction the disc turns, which places the Sun's azimuth and moves "
        "nothing else of the galaxy; and its mapped arms - the four major arms and the Local arm, as fitted to "
        "the masers' parallaxes over the third of the disc on the Sun's side - lie where they were measured, "
        "each continued past its measured range by drawn pieces, with the randomness layer's own arm pieces "
        "filling the radii no measured arm crosses. With the layer off no arm is placed and the galaxy is the "
        "bare default one, number for number. Seen face-on."
    ),
    model="azimuthal",
    camera=Camera(inclination_deg=0.0, azimuth_deg=270.0, radius_kpc=20.0, fov_deg=45.0),
    filters="rgb",
    instrument=Instrument(distance_mpc=None, pixel_scale_arcsec=None),
    # S58 (D217 item 2): the observed class, barred. The derivation says the same at the defaults (the bar's
    # formation time 1.5 Gyr against a disc 9.6 Gyr old), so no bit of any field moves with the pin
    # (tests/test_templates.py::test_a_run_of_milky_way_is_bit_identical_to_a_run_with_no_inputs).
    pins=(
        Pin(
            name="bar_present",
            value=True,
            source=(
                "[verified: GALAXY_INPUTS.md §7 rows 15-17, citing Bland-Hawthorn & Gerhard 2016 (BHG16) as the "
                "acceptance rows do: the Milky Way's bar, half-length 5.0 +/- 0.2 kpc, pattern speed 43 +/- 9 km/s/kpc, "
                "corotation 4.5-7.0 kpc; docs/READING_BAR.md A2, We15 and P17, read the same bar] "
                "[verified: DECISIONS.md D217 item 2: milky_way pins barred]"
            ),
        ),
        # S59 (D218 item 5): where the Sun is. The bar's long axis stands 28-33 degrees from the Sun-centre line,
        # its near end at positive Galactic longitude - ahead of that line in the direction of rotation; 30 is
        # the ruling's value inside the measured range. It places the published sun_azimuth and moves no field
        # of the galaxy. Nothing of the arms' loci is pinned: a sum of modes with drawn phases holds no arm.
        Pin(
            name="sun_bar_angle",
            value=30.0,
            source=(
                "[verified: Wegg, Gerhard & Portail 2015, MNRAS 450, 4050 = arXiv:1504.01401, abstract, "
                "https://ar5iv.labs.arxiv.org/html/1504.01401: the long bar's angle to the line of sight "
                "'(28-33) deg'; best-fit 28.4 (one component), 29.1/30.0 (two)] [verified: Bland-Hawthorn & "
                "Gerhard 2016, ARA&A 54, 529 = arXiv:1602.07702, §4.2.1, §4.3: long bar 28-33 deg, the box/peanut "
                "bulge 27 +/- 2 deg] (docs/READING_ARM_SEGMENTS.md A1.3, W15 and BHG16) "
                "[verified: DECISIONS.md D218 item 5: sun_azimuth = phi_bar - 30 deg in the rotation's sense, the "
                "bar's near end at beta > 0]"
            ),
        ),
        # S60 (D219 item 8): where the Milky Way's mapped arms are. Reid et al. 2019's four major arms and the
        # Local arm, each row of the table a chain of its fitted pieces over its measured range of azimuth, placed
        # by the Sun's azimuth. With the randomness layer off nothing is placed and no field moves.
        Pin(
            name="arm_pieces",
            value=tuple(row for row in REID_2019_TABLE2 if row[0] in MILKY_WAY_PINNED_ARMS),
            source=(
                "[verified: Reid et al. 2019, ApJ 885, 131 = arXiv:1910.03357, Table 2 and note, "
                "https://arxiv.org/pdf/1910.03357: the fitted arms' beta ranges, kinks and pitches, R0 = 8.15 kpc; "
                "all seven rows, two reads of the PDF text agree digit for digit] (docs/READING_ARM_SEGMENTS.md "
                "A1.3 and 'Milky Way pins') [verified: DECISIONS.md D219 item 8: the four major arms and the "
                "Local arm as chains of their fitted pieces over their measured beta ranges, the 3 kpc arm out, "
                "no chain tied to the bar, equal weights]. The source's uncertainties are not entered. Disputed, "
                "and recorded here beside the pin: four arms (this source) against two inner arms that "
                "bifurcate at 5.0-6.5 kpc plus outer segments (Xu et al. 2023), Scutum a separate arm (here) "
                "or part of Norma (Xu et al. 2023); the Sagittarius arm's pitch 1.0/17.1 deg about a kink "
                "(here), 6.9 deg (Reid et al. 2014) or 1.3 deg with Carina a separate arm of 21.4 deg (Xu et "
                "al. 2023); Perseus at beta = 40 deg at 8.87 kpc (here) against 9.08-9.29 kpc (the 2026 "
                "re-fit the reading calls Hy26); the Outer arm's pitch 3.0/9.4 deg (here), 13.8 (Reid et al. "
                "2014) or 3.6 (Xu et al. 2023); the Sun's distance 8.15 kpc here against 7.92-8.34 elsewhere "
                "[verified: docs/READING_ARM_SEGMENTS.md A4 items 5-6]. The Norma and Outer rows are one arm "
                "in the source, fitted in two stretches with nothing measured between them: entered as two "
                "chains [inferred]."
            ),
        ),
    ),
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
        "An unbarred flocculent Sc spiral at 17.7 Mpc, seen at 55 degrees. Three measured properties - the rotation "
        "curve's peak, the stellar disc's scale length and the stellar mass - fit the four controls they measure: "
        "the halo's mass, the disc's spin, the halo's assembly redshift and the share of the baryons kept. The other "
        "three controls no target measures, so they stay at the Milky Way's values. What the fit could not remove is "
        "published beside it: all three targets land inside their windows, none on its value, and the assembly "
        "redshift ends on the lower bound of its range - a finding, not a fit. Five more measured properties the "
        "fit never saw are checks, judged by the specs; they were read once on an earlier fit, since withdrawn, so "
        "every verdict on this one is disclosed and none is blind. Nothing measures its mergers or its seeds, so the "
        "merger list is empty and every seed is 4414. It is pinned unbarred, as observed: no source finds a bar in "
        "NGC 4414, while the model's own criterion - the time a disc this dominant takes to form a bar, under a "
        "gigayear, against the disc's age - says it should have one; the disagreement is published, the formation "
        "time beside the pinned verdict. So it has no bar's body and no bar's lanes, and its arms run to the "
        "centre. Its arm class is pinned flocculent, as observed: its arms are single short pieces, not long "
        "chains, where the model's own rule would make an unbarred disc multi-armed. Nothing positional is pinned "
        "of them: no source gives where its pieces lie. The position angle (159 degrees) is not applied: the camera "
        "has no roll."
    ),
    model="azimuthal",
    # The four free controls as the fit leaves them (tools/fit_template.py ngc_4414, 2026-10-04), copied by hand
    # from the tool's output. **They are a point on a plateau, resolved to the model's own steps - about 0.01
    # half-windows in the objective, a few 1e-4 of a range in the controls - and not a minimum to the printed
    # precision** (debt #133: the three target fields are stepped in halo_mass and disc_spin). The sixteen
    # digits stay because a rounded value is another point. infall_timescale, inside_out_index and
    # migration_efficiency are not stated: no target measures them, so they are the registry's defaults and
    # do not move by any amount (D213 as amended at the gate, ruling 1). The first fit, which moved them, is
    # withdrawn and kept in D213 as the first reading.
    controls={
        "halo_mass": 609546153006.4983,
        "disc_spin": 0.014191065730401048,
        "halo_assembly_z": 0.5,  # bound: the lower bound of its range, a finding and not a fit (Fit.bounds, debt #132)
        "baryon_retention": 0.4918931810399049,
    },
    # texture_seed since S55 (D214 section 3): the randomness layer's seed, the catalogue number as the rest are.
    # No stage read it until BUILD_III's phase P1 (S56, D215): the arm modes' phases are drawn on it since, so it
    # says where this template's arms lie with the layer on - and moves no number of the layer-off run, which is
    # what the fit and the five checks are judged on.
    seeds={"world_seed": 4414, "pattern_seed": 4414, "systems_seed": 4414, "planets_seed": 4414, "texture_seed": 4414},
    mergers=(),
    camera=Camera(inclination_deg=55.0, azimuth_deg=0.0, radius_kpc=15.0, fov_deg=5.0),
    filters="wfc3",
    instrument=Instrument(distance_mpc=17.7, pixel_scale_arcsec=None),
    # S58 (D217 item 2): the observed class, unbarred, in place of the derived presence (which says barred: the
    # criterion's recorded miss on this galaxy). Not a fit - no control moves and no number is set - and the five
    # checks are judged on the pinned galaxy. A one-field flip restores the barred picture with nothing else changed.
    pins=(
        Pin(
            name="bar_present",
            value=False,
            source=(
                f"[verified: {_READING}, row 16 and 'Structural mismatches': NGC 4414 has no bar - RC3 SA(rs)c? (the "
                "family SA), S4G fits no bar component, Buta family index 0.00, V02 'no bar', W04 'little evidence "
                "for a bar'] [verified: DECISIONS.md D217 item 2: ngc_4414 pins unbarred]"
            ),
        ),
        # S59 (D218 item 6): the measured mean pitch replaces the draw. The law's own value at this template's
        # seed, 14.33 degrees, is published beside it (pitch_angle_drawn): 2.4 sigma of the 6-degree draw under
        # the measurement - a finding against the pitch law, recorded and not tuned. The five segments' rows
        # overlap in radius (pieces of different arms), so nothing positional is pinned: they are a disclosed
        # check of the drawn segments' spread, in tests/.
        Pin(
            name="pitch_angle",
            value=28.9,
            source=(
                "[verified: Herrera-Endoqui, Diaz-Garcia, Laurikainen & Salo 2015, A&A 582, A86 = arXiv:1509.05328, "
                "Table 3 at VizieR J/A+A/582/A86/table3, the five NGC 4414 rows: pitches -30.5, -34.2, -28.1, "
                "-44.0, -7.6 deg] [verified: Diaz-Garcia, Salo, Knapen & Herrera-Endoqui 2019, A&A 631, A94 = "
                "arXiv:1908.04246, table a1: mean 28.88 deg, error of the mean 5.97 deg (sd 13.35 deg)] "
                "(docs/READING_ARM_SEGMENTS.md A1.4, HE15 and DG19) [verified: DECISIONS.md D218 item 6: "
                "pitch_angle = 28.9 deg replaces the draw]"
            ),
        ),
        # S60 (D219 item 3): the observed arm class, flocculent, in place of the class the model derives from the
        # bar (an unbarred disc: multi-armed). The layer then lays single pieces, not chains. The model makes no
        # flocculent disc without this pin: a recorded miss of the measured half of spirals.
        Pin(
            name="arm_class",
            value="flocculent",
            source=(
                "[verified: docs/READING_ARM_SEGMENTS.md 'NGC 4414' and A4 item 3: arm class F in Buta et al. "
                "2015 and in Herrera-Endoqui et al. 2015's Table 3; M in Diaz-Garcia et al. 2019's table a1, "
                "read twice - the conflict recorded; Thornley 1996: 'the most flocculent of the sample', no "
                "regular two-arm pattern in K'] [verified: DECISIONS.md D219 item 3: flocculent by pin only, "
                "arm_class on ngc_4414]"
            ),
        ),
    ),
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
                model=239.1813996587132,
                residual=0.17451197269705518,
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
                model=1.6760444551064766,
                residual=0.1352222755323829,
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
                model=39047506448.23065,
                residual=-0.449668221349256,
            ),
        ),
        free={
            "halo_mass": "curve_peak",
            "disc_spin": "disc_scale_length",
            "halo_assembly_z": "curve_peak",
            "baryon_retention": "stellar_mass",
        },
        measures={
            "halo_mass": "the peak",
            "disc_spin": "the scale length",
            "halo_assembly_z": "the peak at a given disc, through the concentration",
            "baryon_retention": "the stellar mass at a given halo",
        },
        bounds={
            "halo_assembly_z": (
                "the model cannot lower its inner peak enough for this disc inside the range; the concentration "
                "floor, or the concentration–mass relation, is the debt (debt #132) "
                "[verified: DECISIONS.md D213 as amended at the gate, ruling 3]"
            ),
        },
        tiebreak=1e-3,
        objective=(
            "the sum over the three targets of ((model - value) / half-window)^2, plus 0.001 times the sum over "
            "the four free controls of ((fitted - default) / (hi - lo))^2: the last term breaks ties among the free "
            "controls and does nothing else. Where the search stops it is 0.2511 - 0.2509 from the targets, 0.0002 "
            "from the tie-break - on a plateau resolved to the model's own steps, about 0.01 half-windows in the "
            "objective: not a minimum to the printed precision"
        ),
        objective_value=0.2511141040064585,
        tool="tools/fit_template.py ngc_4414",
        method=(
            "damped Gauss-Newton (Levenberg-Marquardt) with a coordinate search in every step, over the free controls "
            "only - those a target measures, named in the template's data: 24 steps from the registry's defaults, in "
            "the logarithm of each free control whose range starts above zero, the targets differenced in each "
            "coordinate at 0.04, 0.02, 0.01 of its span in turn, 4 damped trial steps solved inside the published "
            "ranges, the lowest of the trial and differencing points taken when it is lower. Where it stops is a "
            "point on a plateau resolved to the model's own steps - about 0.01 half-windows in the objective, a few "
            "1e-4 of a range in the controls - and not a minimum to the printed precision"
        ),
        date="2026-10-04",
        evaluations=289,
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
            standing="disclosed",
            standing_about=_DISCLOSED,
            first_reading=_first(0.64787, "fail"),
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
            standing="disclosed",
            standing_about=_DISCLOSED,
            first_reading=_first(0.125061, "fail"),
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
            standing="disclosed",
            standing_about=_DISCLOSED,
            first_reading=_first(3.72206e9, "fail"),
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
            standing="disclosed",
            standing_about=_DISCLOSED,
            first_reading=_first(-22.9793, "fail"),
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
            standing="disclosed",
            standing_about=_DISCLOSED,
            first_reading=_first(0.818747, "pass"),
        ),
    ),
    sources={
        **{f"inputs.controls.{name}": _FITTED for name in ("halo_mass", "disc_spin", "halo_assembly_z", "baryon_retention")},
        **{f"inputs.seeds.{name}": _SEED for name in ("world_seed", "pattern_seed", "systems_seed", "planets_seed")},
        "inputs.seeds.texture_seed": (
            "[inferred] a seed has no measured value and none is chosen for the picture: the randomness layer's "
            "seed is the catalogue number, 4414, as every seed of this template is "
            "[verified: DECISIONS.md D214, section 3: both templates gain it, 0 and 4414]"
        ),
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
if TEMPLATES[DEFAULT].controls or TEMPLATES[DEFAULT].seeds or TEMPLATES[DEFAULT].mergers is not None:
    raise TemplateError(
        "the default template overrides no control, no seed and no event list: it is the registry's defaults "
        "(D213, ruling 1); what it pins, the model derives there (D217 item 2)"
    )
for _template in TEMPLATES.values():
    _template.validate()


def names() -> tuple[str, ...]:
    return tuple(TEMPLATES)


def get(name: str) -> Template:
    try:
        return TEMPLATES[name]
    except KeyError:
        raise KeyError(f"no template named {name!r}; registered: {list(TEMPLATES)}") from None
