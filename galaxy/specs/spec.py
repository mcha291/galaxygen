"""spec: the 24 acceptance quantities as data (rule C6), with a runner.

Each :class:`Quantity` names the published scalar field the runner reads, the
target interval, how it is judged, and its source. The table is
GALAXY_INPUTS.md §7 ``[verified: that section]``; the ``stated`` column carries
each value as written there and ``lo``/``hi`` are the arithmetic of ``±``.
"BHG16" is the source that section cites for every row not marked otherwise
``[recall: Bland-Hawthorn & Gerhard 2016, ARA&A]``.

Three statuses, no more: ``pass``, ``fail``, ``not-yet-computable``. A quantity
is not yet computable when no field is named for it, when the model does not
publish that field, or when a statistical row lacks an ensemble. A quantity
never passes by default and a missing number is never shown as a measured one
(rule B9).

Judging modes:

- ``pointwise``: the published scalar lies in ``[lo, hi]``.
- ``statistical`` (debt #8: rows 13, 14, 16, 17, 18): the model publishes a
  seeded quantity, so the check is against an ensemble over seeds. Pass when
  the central 95 % interval of at least ``ENSEMBLE_MIN`` values intersects
  ``[lo, hi]``. This criterion is an S0 decision (DECISIONS.md); S3 or S4 may
  revise it, never relax a target (rule B5).
- ``qualitative`` (row 24): a ``category_scalar`` equal to ``expect``.

Rows 20 and 21 are quoted without an uncertainty and have ``lo == hi``; a
pointwise check against a zero-width target fails for any float that is not
exactly equal. That is recorded here rather than widened: S2 either finds the
uncertainty in the source or records the miss (rule B5).

**Recorded misses** (:func:`misses`). Rule B5 says to record a failed acceptance
check rather than relax it, and GALAXY_INPUTS.md §3 says row 18 is *expected* to
miss by ~0.75 dex and must not be re-scoped. A target the model is known not to
meet therefore has to stay red in this report and still not be indistinguishable
from a regression, or the first honest miss makes every later one invisible. So
a miss is registered here with the debt it belongs to, the session that measured
it, and a prediction that could kill the explanation (rule B4). A registered miss
still evaluates to ``fail`` — nothing is widened, nothing is skipped — but the
process exit status distinguishes *explained* from *unexplained*. Two things are
errors, not misses: a failing row nobody has explained, and a registered miss
that has started passing, because its explanation is then stale and the register
is lying (rule B10). A miss belongs to one model or to all: the advanced model's
findings are its own (rule A7), so a row the simple model misses and the
advanced model meets is stale for one and recorded for the other.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np

from galaxy.core.fielddoc import IDENT, FieldDecl, Kind
from galaxy.core.registry import Model, production
from galaxy.core.units import UnknownUnit
from galaxy.core.units import unit as _unit
from galaxy.specs import Problem, utf8_stdout

MODES: tuple[str, ...] = ("pointwise", "statistical", "qualitative")
STATUSES: tuple[str, ...] = ("pass", "fail", "not-yet-computable")
ENSEMBLE_MIN = 20
CENTRAL = 0.95


class SpecError(ValueError):
    """A quantity row is malformed."""


@dataclass(frozen=True, slots=True)
class Quantity:
    n: int
    name: str
    unit: str
    field: str | None  # the published scalar field the runner reads; None = not defined yet
    lo: float | None
    hi: float | None
    mode: str
    stated: str  # the value as GALAXY_INPUTS.md §7 states it
    source: str
    note: str = ""
    expect: str | None = None  # qualitative rows: the category that passes

    def __post_init__(self) -> None:
        try:
            _unit(self.unit)
        except UnknownUnit as e:
            raise SpecError(f"row {self.n}: {e}") from None
        if self.mode not in MODES:
            raise SpecError(f"row {self.n}: mode {self.mode!r} not in {MODES}")
        if self.field is not None and not IDENT.match(self.field):
            raise SpecError(f"row {self.n}: field {self.field!r} must match {IDENT.pattern}")
        if (self.lo is None) != (self.hi is None):
            raise SpecError(f"row {self.n}: lo and hi must both be set or both be None")
        if self.lo is not None and self.hi is not None and self.lo > self.hi:
            raise SpecError(f"row {self.n}: lo > hi")
        if self.mode != "qualitative" and self.field is not None and self.lo is None:
            raise SpecError(f"row {self.n}: a {self.mode} row with a field needs an interval")
        if self.mode == "qualitative" and self.field is not None and self.expect is None:
            raise SpecError(f"row {self.n}: a qualitative row with a field needs expect=")
        if not self.stated.strip() or not self.source.strip():
            raise SpecError(f"row {self.n}: stated and source are required")


_BHG16 = "BHG16"

QUANTITIES: tuple[Quantity, ...] = (
    Quantity(1, "Total stellar mass", "Msun", "stellar_mass_total", 4.0e10, 6.0e10, "pointwise", "5 ± 1 × 10¹⁰ M☉", _BHG16),
    Quantity(2, "Star formation rate", "Msun/yr", "sfr", 1.46, 1.84, "pointwise", "1.65 ± 0.19 M☉/yr", _BHG16),
    Quantity(3, "Solar tangential velocity", "km/s", "v_tangential_sun", 245.0, 251.0, "pointwise", "248 ± 3 km/s", _BHG16),
    Quantity(4, "Thin disc scale length", "kpc", "thin_disc_scale_length", 2.1, 3.1, "pointwise", "2.6 ± 0.5 kpc", _BHG16),
    Quantity(5, "Thick disc scale length", "kpc", "thick_disc_scale_length", 1.8, 2.2, "pointwise", "2.0 ± 0.2 kpc", _BHG16),
    Quantity(6, "Thin disc scale height", "pc", "thin_disc_scale_height", 250.0, 350.0, "pointwise", "300 ± 50 pc", _BHG16),
    Quantity(7, "Thick disc scale height", "pc", "thick_disc_scale_height", 720.0, 1080.0, "pointwise", "900 ± 180 pc", _BHG16),
    Quantity(8, "Thick/thin local density ratio", "dimensionless", "thick_thin_local_density_ratio", 0.02, 0.06, "pointwise", "4% ± 2%", _BHG16),
    Quantity(9, "Thick/thin surface density ratio", "dimensionless", "thick_thin_surface_density_ratio", 0.08, 0.16, "pointwise", "12% ± 4%", _BHG16),
    Quantity(10, "Thin disc stellar mass", "Msun", "thin_disc_stellar_mass", 2.5e10, 4.5e10, "pointwise", "3.5 ± 1 × 10¹⁰ M☉", _BHG16),
    Quantity(11, "Thick disc stellar mass", "Msun", "thick_disc_stellar_mass", 3.0e9, 9.0e9, "pointwise", "6 ± 3 × 10⁹ M☉", _BHG16),
    Quantity(12, "Bulge stellar mass", "Msun", "bulge_stellar_mass", 1.4e10, 1.7e10, "pointwise", "1.4–1.7 × 10¹⁰ M☉", _BHG16),
    Quantity(13, "Bulge/total stellar fraction", "dimensionless", "bulge_stellar_fraction", 0.24, 0.36, "statistical", "0.30 ± 0.06", _BHG16, note="Statistical per debt #8 (GALAXY_INPUTS.md §4b)."),
    Quantity(14, "Bulge velocity dispersion (rms)", "km/s", "bulge_velocity_dispersion", 113.0, 113.0, "statistical", "113 km/s", _BHG16, note="No uncertainty quoted; statistical per debt #8, so the ensemble spread does the work."),
    Quantity(15, "Bar half-length", "kpc", "bar_half_length", 4.8, 5.2, "pointwise", "5.0 ± 0.2 kpc", _BHG16),
    Quantity(16, "Bar pattern speed", "km/s/kpc", "bar_pattern_speed", 34.0, 52.0, "statistical", "43 ± 9 km/s/kpc", _BHG16, note="Statistical per debt #8."),
    Quantity(17, "Bar corotation radius", "kpc", "bar_corotation_radius", 4.5, 7.0, "statistical", "4.5–7.0 kpc", _BHG16, note="Statistical per debt #8."),
    Quantity(18, "Black hole mass", "Msun", "black_hole_mass", 4.0e6, 4.4e6, "statistical", "4.2 ± 0.2 × 10⁶ M☉", _BHG16, note="Debt #2: derived from M–σ plus a seeded residual (ruling 10); the Milky Way sits 5–6× below the relation, so this is expected to miss by ~0.75 dex and must not be re-scoped to include the miss (GALAXY_INPUTS.md §3, rule B5). Statistical per debt #8."),
    Quantity(19, "Halo virial mass", "Msun", "halo_virial_mass", 1.0e12, 1.3e12, "pointwise", "1.0–1.3 × 10¹² M☉", "McMillan"),
    Quantity(20, "Total gas mass (<30 kpc)", "Msun", "gas_mass_30kpc", 8.0e9, 8.0e9, "pointwise", "8.0 × 10⁹ M☉", "Nakanishi & Sofue 15", note="No uncertainty quoted: zero-width target. S2 finds the uncertainty in the source or records the miss (rule B5)."),
    Quantity(21, "Gas HI:H₂ split", "dimensionless", "gas_h2_fraction", 0.11, 0.11, "pointwise", "89% : 11%", "Nakanishi & Sofue 15", note="Read as the H₂ mass fraction f_H₂ = 0.11 (HI = 1 − f_H₂). No uncertainty quoted: zero-width target; see row 20."),
    Quantity(22, "Present-day metallicity gradient", "dex/kpc", "metallicity_gradient", -0.069, -0.049, "pointwise", "−0.06 dex/kpc", "Trentin+24 −0.064 ± 0.003; Feuillet+19 −0.059 ± 0.010", note="Interval is the union of the two cited measurements [inferred]; the table itself quotes −0.06 with no error."),
    Quantity(23, "Gradient evolution with age", "dex/kpc", "metallicity_gradient_old", -0.05, -0.03, "pointwise", "−0.07 (young) → −0.04 (>10 Gyr)", "Willett+23", note="Two values at two ages; one row can name one field, so S2 operationalises it as the *old* end (>10 Gyr, target −0.04) and leaves the young end to row 22's companion field metallicity_gradient_young, which the same stage publishes. Interval is ±0.01 around −0.04 [inferred]: the source quotes no uncertainty and a zero-width target would make the row untestable rather than strict."),
    Quantity(24, "[α/Fe] bimodality", "dimensionless", "alpha_sequence", None, None, "qualitative", "Thick disc α-enhanced across a wide [Fe/H] range", "BHG16 §5.2.2", expect="bimodal_wide", note="Judged on the [α/Fe] mass distribution of the stars now at R₀, migrants included: two modes with a valley between them, and the α-rich mode spanning at least 0.5 dex of [Fe/H] (S9). Only the advanced model publishes the field; the simple model has one abundance and stays not-yet-computable (rule B3). Debt #9 asks whether it appears without a merger."),
)

if [q.n for q in QUANTITIES] != list(range(1, len(QUANTITIES) + 1)):
    raise SpecError("quantities must be numbered 1..N in order")


@dataclass(frozen=True, slots=True)
class Miss:
    """A target the model is known not to meet, with the reason on the record (rule B5)."""

    row: int
    debt: int  # entry in the calibration debt register, GALAXY_INPUTS.md §11
    since: str  # the session that measured the miss
    reason: str
    prediction: str  # what would change it, stated so that it can fail (rule B4)
    model: str | None = None  # None: every model; else the one model this explanation belongs to (rule A7)

    def __post_init__(self) -> None:
        if self.model is not None and not IDENT.match(self.model):
            raise SpecError(f"row {self.row}: model {self.model!r} must be a model name or None")
        if self.row not in {q.n for q in QUANTITIES}:
            raise SpecError(f"recorded miss names row {self.row}, which is not in the table")
        if self.debt < 1 or not self.since.startswith("S"):
            raise SpecError(f"row {self.row}: a recorded miss needs a debt number and a session")
        if not self.reason.strip() or not self.prediction.strip():
            raise SpecError(f"row {self.row}: a recorded miss needs a reason and a prediction")


_MISSES: tuple[Miss, ...] = (
    Miss(
        row=2,
        debt=18,
        since="S3",
        reason=(
            "1.97 Msun/yr against 1.65, having been 1.14 before the merger-delivered second "
            "infall existed. Moving 60% of the accretion to start at the merger keeps gas "
            "arriving late, which is the right mechanism and overshoots: the second episode "
            "decays on the same 7 Gyr timescale as the first, so too much of it is still "
            "arriving now."
        ),
        prediction=(
            "The second infall should be *slower* than the first, not the same speed - the outer "
            "disc it feeds accretes over longer. A separate timescale for the post-merger episode "
            "brings this down without touching the stellar structure. If it also moves rows 10 and "
            "11, the two episodes are not as separable as this model assumes."
        ),
    ),
    Miss(
        row=5,
        model="simple",
        debt=19,
        since="S3",
        reason=(
            "The thick disc's scale length is 1.17 kpc against 2.0. It forms before the merger, "
            "when the disc is small and inside-out growth has star formation concentrated in the "
            "middle, so it comes out far more centrally concentrated than the observed thick disc."
        ),
        prediction=(
            "The thick disc has to be born extended, not merely early. Either the pre-merger disc "
            "is already larger than this model makes it, or the merger itself spreads the stars it "
            "heats - radial as well as vertical heating, which this model does not do. The second "
            "is testable: a radial kick applied with the vertical one should raise row 5 towards "
            "2.0 and lower row 9 at the same time."
        ),
    ),
    Miss(
        row=11,
        model="simple",
        debt=19,
        since="S3",
        reason=(
            "1.07e10 Msun against 6e9: the pre-merger episode carries 40% of the baryon budget and "
            "should carry nearer 15%. **Row 9, this session's gate, passes at 0.103 only because "
            "this error and the row 5 error compensate.** Raising the merger's gas_fraction to "
            "shrink the thick disc drives row 9 from 0.103 to 0.015, because a thick disc this "
            "centrally concentrated loses surface density at R_0 far faster than it loses mass. "
            "The gate is therefore passing for the wrong reason and is recorded as such."
        ),
        prediction=(
            "Row 5 is the prerequisite. Once the thick disc has the right extent, its mass and its "
            "surface-density ratio can be right together; until then either one can be fixed only "
            "by breaking the other. If they still cannot be satisfied together at the right scale "
            "length, the split criterion - born before the last major merger - is what is wrong."
        ),
    ),
    Miss(
        row=3,
        debt=18,
        since="S1",
        reason=(
            "256.1 km/s against 248 +/- 3: too much mass inside R0. S1 recorded this as the gas "
            "not yet having its own profile and predicted 246.4 once it did. S2 gave it one and "
            "got 237.2 - overshooting - but only because the same constant that moved the gas out "
            "also broadened the stellar disc to 3.74 kpc. S3 corrected that constant, the two disc "
            "scale lengths came into agreement (debt #13 discharged), and the miss returned to "
            "where S1 left it. So the cause is not the gas profile at all: it is that all the "
            "baryons are in the compact disc, with no extended component and no bulge."
        ),
        prediction=(
            "Splitting the baryons into a compact disc plus an extended high-angular-momentum "
            "component moves mass outside R0 and lowers v_c there. The bulge (S3-S4) pushes the "
            "other way, so the two must be added together before this row is judged - which is why "
            "it is not closable until both exist."
        ),
    ),
    Miss(
        row=20,
        debt=18,
        since="S2",
        reason=(
            "5.80e9 Msun against 8.0e9, a 28% shortfall, improved from 4.94e9 by the "
            "merger-delivered second infall. With the infall carrying the disc's own "
            "scale length there is nothing accreting beyond about 10 kpc, so the outer HI disc "
            "that holds most of the Milky Way's gas simply does not exist in this model."
        ),
        prediction=(
            "An extended accretion component sized to the observed HI disc closes this row and "
            "rows 2 and 3 with it. Note the target is also zero-width (debt #17), so even a model "
            "that got the mass right would fail this check until the table records an uncertainty."
        ),
    ),
    Miss(
        row=22,
        model="simple",
        debt=15,
        since="S2",
        reason=(
            "-0.027 dex/kpc against -0.06. The gradient was measured to be exactly insensitive to "
            "the yield, so the level and the tilt are set separately and this is about the tilt. "
            "S3's more compact infall steepened it from -0.020, which confirms the tilt comes from "
            "the differential infall, and it is still less than half of what is observed."
        ),
        prediction=(
            "Outflows are the missing tilt: metal loss scaling with escape velocity strips more "
            "from the outer disc than the inner one, steepening the gradient without touching the "
            "inside-out index. S9 adds them. If the gradient does not steepen towards -0.06 when "
            "it does, the infall law is wrong rather than the outflows missing."
        ),
    ),
    Miss(
        row=23,
        model="simple",
        debt=15,
        since="S2",
        reason=(
            "The old-population gradient is too flat for the same reason row 22 is. Migration "
            "itself is close to right - the young/old ratio is near the observed 1.75 - so the "
            "error is in the gradient being flattened, not in the flattening."
        ),
        prediction=(
            "Whatever steepens row 22 steepens this row by the same factor and leaves the "
            "young/old ratio alone, because migration and enrichment are separate mechanisms here. "
            "If row 22 steepens and this one does not, migration_efficiency is wrong too."
        ),
    ),
)


# The advanced model's own misses (rule A7). Its chemistry finds no valley in the
# [α/Fe] distribution at R₀, so its chemical thin/thick split selects nothing and
# every thick-disc row reads zero — one cause, six rows, plus row 24 itself.
_NO_VALLEY = (
    "The advanced model's thin/thick split is the valley between the two [α/Fe] sequences at "
    "R₀ (D88), and there is none: the stellar mass there piles up at [α/Fe] = +0.21 in one "
    "mode with a high-α tail, so the thick disc is empty and this row reads zero (debt #27)."
)
_NO_VALLEY_PREDICTION = (
    "S9 swept the accretion inputs and re-integrated the infall with a fast first episode, a "
    "slow merger-delivered second one, and a pause between them: the dip reaches 0.38 at "
    "best and never the 0.5 that makes two modes. The accretion history alone will not "
    "produce the valley; what should is the *inner* disc reaching low [α/Fe] early and its "
    "migrants arriving at R₀ as a separate lump — which needs the inner disc's own early "
    "history to be fast, i.e. an infall timescale far shorter than τ₀(R/R₀) gives inside "
    "4 kpc. If a steeper inside-out law inside R₀ does not open a valley either, the DTD's "
    "long tail is what keeps the local track at intermediate [α/Fe] and the miss is there."
)
_MISSES_ADVANCED: tuple[Miss, ...] = tuple(
    Miss(row=row, model="advanced", debt=27, since="S9", reason=_NO_VALLEY, prediction=_NO_VALLEY_PREDICTION)
    for row in (5, 7, 8, 9, 11)
) + (
    Miss(
        row=10,
        model="advanced",
        debt=27,
        since="S9",
        reason=(
            "5.28e10 Msun against 3.5 ± 1e10: with no valley the chemical split puts every star "
            "in the thin disc, so this row carries the whole stellar mass (debt #27)."
        ),
        prediction=_NO_VALLEY_PREDICTION,
    ),
    Miss(
        row=23,
        model="advanced",
        debt=28,
        since="S9",
        reason=(
            "-0.019 dex/kpc against -0.04. Row 22 steepened to -0.057 when the wind arrived, "
            "exactly as debt #15 predicted, and this row did not follow: the young/old ratio is "
            "3.1 against the observed 1.75. The S2 prediction said that if row 22 steepens and "
            "this one does not, migration_efficiency is wrong too, and that is what happened."
        ),
        prediction=(
            "A kernel width of 2.5 kpc at 8 Gyr puts this row at -0.039 with a young/old ratio "
            "of 1.6 [verified: S9's sweep, tests/test_chemistry_dtd.py]; the default is the "
            "cited 3.6 kpc. Either the citation's width is not this kernel's width, or the old "
            "gas gradient the model flattens from (-0.127 at 10 Gyr without migration) is too "
            "steep to begin with. A measurement of the gradient at 10 Gyr decides between them."
        ),
    ),
    Miss(
        row=24,
        model="advanced",
        debt=27,
        since="S9",
        reason=(
            "'single' against 'bimodal_wide'. The [α/Fe] plane exists now — the plateau is at "
            "+0.45 and the present-day gas at R₀ is at +0.05 — but the stars at R₀ form one mode "
            "at +0.21, where the local track lingers while the delayed iron catches up with a "
            "star formation history that never pauses."
        ),
        prediction=_NO_VALLEY_PREDICTION,
    ),
)


def misses(model: str) -> Mapping[int, Miss]:
    """The recorded misses that apply to ``model``: the shared ones and its own (rule A7)."""
    out: dict[int, Miss] = {}
    for m in _MISSES + _MISSES_ADVANCED:
        if m.model is None or m.model == model:
            if m.row in out:
                raise SpecError(f"row {m.row} is registered as a miss twice for model {model!r}")
            out[m.row] = m
    return MappingProxyType(out)


MISSES: Mapping[int, Miss] = misses("simple")
MISSES_ADVANCED: Mapping[int, Miss] = misses("advanced")


@dataclass(frozen=True, slots=True)
class Result:
    n: int
    name: str
    status: str
    reason: str
    value: float | str | None = None


def evaluate(
    q: Quantity,
    fields: Mapping[str, Any],
    decls: Mapping[str, FieldDecl],
    model: str,
    ensemble: Mapping[str, Sequence[float]] | None = None,
) -> Result:
    nyc = "not-yet-computable"
    if q.field is None:
        return Result(q.n, q.name, nyc, "no published scalar is named for this quantity yet" + (f" ({q.note})" if q.note else ""))
    if q.field not in fields:
        return Result(q.n, q.name, nyc, f"field {q.field!r} is not published by model {model!r}")
    decl = decls[q.field]
    if decl.unit != q.unit:
        return Result(q.n, q.name, "fail", f"unit mismatch: field {q.field!r} is {decl.unit}, target is {q.unit}")
    if q.mode == "qualitative":
        if decl.kind is not Kind.CATEGORY_SCALAR:
            return Result(q.n, q.name, "fail", f"qualitative rows read a category_scalar, field is {decl.kind.value}")
        value = fields[q.field]
        ok = value == q.expect
        return Result(q.n, q.name, "pass" if ok else "fail", f"{value!r} {'==' if ok else '!='} {q.expect!r}", value)
    if decl.kind is not Kind.SCALAR:
        return Result(q.n, q.name, "fail", f"field {q.field!r} is a {decl.kind.value}, not a scalar")
    assert q.lo is not None and q.hi is not None
    if q.mode == "pointwise":
        value = float(fields[q.field])
        ok = q.lo <= value <= q.hi
        width = "" if q.lo != q.hi else " (zero-width target; see note)"
        return Result(q.n, q.name, "pass" if ok else "fail", f"{value:.6g} {'in' if ok else 'not in'} [{q.lo:.6g}, {q.hi:.6g}]{width}", value)
    # statistical
    if ensemble is None or q.field not in ensemble:
        return Result(q.n, q.name, nyc, f"statistical: needs an ensemble of >= {ENSEMBLE_MIN} seeded runs (debt #8)")
    values = np.asarray(ensemble[q.field], dtype=float)
    if values.size < ENSEMBLE_MIN:
        return Result(q.n, q.name, nyc, f"statistical: ensemble has {values.size} values, needs >= {ENSEMBLE_MIN}")
    tail = 100.0 * (1.0 - CENTRAL) / 2.0
    p_lo, p_hi = np.percentile(values, [tail, 100.0 - tail])
    ok = p_lo <= q.hi and q.lo <= p_hi
    return Result(
        q.n,
        q.name,
        "pass" if ok else "fail",
        f"central {CENTRAL:.0%} [{p_lo:.6g}, {p_hi:.6g}] {'intersects' if ok else 'misses'} [{q.lo:.6g}, {q.hi:.6g}] (n={values.size})",
        float(np.median(values)),
    )


def evaluate_all(
    fields: Mapping[str, Any],
    decls: Mapping[str, FieldDecl],
    model: str,
    ensemble: Mapping[str, Sequence[float]] | None = None,
) -> list[Result]:
    return [evaluate(q, fields, decls, model, ensemble) for q in QUANTITIES]


def run(model: Model, ensemble: Mapping[str, Sequence[float]] | None = None, **run_kwargs: Any) -> list[Result]:
    """Run ``model`` with default inputs and judge every quantity."""
    from galaxy.run import run as _run

    out = _run(model, **run_kwargs)
    return evaluate_all(out.fields, out.decls, model.name, ensemble)


STATISTICAL_FIELDS: tuple[str, ...] = tuple(
    q.field for q in QUANTITIES if q.mode == "statistical" and q.field is not None
)


def ensemble(
    model: Model,
    fields: Sequence[str] = STATISTICAL_FIELDS,
    n: int = ENSEMBLE_MIN,
    **run_kwargs: Any,
) -> dict[str, list[float]]:
    """Values of ``fields`` across ``n`` galaxies that differ only in their seeds.

    Every seed moves together, so this is an ensemble of galaxies with identical
    physical inputs — which is what a statistical row is judged against. Fields the
    model does not publish are simply absent, and the row stays not-yet-computable.

    **Only the stages those fields need are run** (``only=``, rule D4). Debt #24
    was this function rebuilding a 20 000-star catalogue twenty times to read two
    scalars that depend on checkpoint 4; the closure above the requested fields is
    the whole of the fix, and the values are unchanged because a stage is a pure
    function of its declared reads.
    """
    from galaxy.core.registry import INPUTS
    from galaxy.run import run as _run

    table = run_kwargs.get("table") or INPUTS
    seed_names = [name for name, inp in table.items() if inp.kind == "seed"]
    collected: dict[str, list[float]] = {}
    for draw in range(n):
        out = _run(model, {name: draw for name in seed_names}, only=tuple(fields), **run_kwargs)
        for field in fields:
            if field in out.fields:
                collected.setdefault(field, []).append(float(out.fields[field]))
    return collected


def evaluate_models(models: Iterable[Model], **run_kwargs: Any) -> dict[str, list[Result]]:
    """Judge every model once, building each an ensemble for the statistical rows."""
    return {
        m.name: run(m, ensemble=ensemble(m, **run_kwargs), **run_kwargs) for m in models
    }


def summary(results: Iterable[Result]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for r in results:
        counts[r.status] += 1
    return counts


def unexplained(results: Iterable[Result], model: str = "simple") -> tuple[Result, ...]:
    """Failing rows with no recorded miss for ``model``. These are what should stop a build."""
    known = misses(model)
    return tuple(r for r in results if r.status == "fail" and r.n not in known)


def stale(results: Iterable[Result], model: str = "simple") -> tuple[Result, ...]:
    """Registered misses that now pass: the recorded explanation is wrong or spent (rule B10)."""
    known = misses(model)
    return tuple(r for r in results if r.status == "pass" and r.n in known)


def problems(results: Iterable[Result], model: str = "simple") -> list[Problem]:
    """Everything a spec run should fail on. A recorded, still-failing miss is not one."""
    results = list(results)
    known = misses(model)
    out = [
        Problem("spec", "acceptance", f"row {r.n} ({r.name}) fails and is not a recorded miss for model {model!r}: {r.reason}")
        for r in unexplained(results, model)
    ]
    out += [
        Problem(
            "spec",
            "stale-miss",
            f"row {r.n} ({r.name}) is registered as a miss for model {model!r} since {known[r.n].since} (debt "
            f"#{known[r.n].debt}) but now passes: {r.reason}. Remove the entry or find out why.",
        )
        for r in stale(results, model)
    ]
    return out


def report(
    models: Iterable[Model],
    results: Mapping[str, list[Result]] | None = None,
    **run_kwargs: Any,
) -> str:
    models = list(models)
    if results is None:
        results = evaluate_models(models, **run_kwargs)
    lines = ["spec"]
    for m in models:
        judged = results[m.name]
        s = summary(judged)
        known = misses(m.name)
        recorded = sum(1 for r in judged if r.status == "fail" and r.n in known)
        head = f"  model {m.name}: {s['pass']} pass, {s['fail']} fail, {s['not-yet-computable']} not-yet-computable of {len(judged)}"
        if recorded:
            head += f" ({recorded} of the failures recorded as misses)"
        lines.append(head)
        for r in judged:
            tag = ""
            if r.n in known and r.status == "fail":
                tag = f" [recorded miss, debt #{known[r.n].debt}, since {known[r.n].since}]"
            lines.append(f"    {r.n:>2} {r.status:<19} {r.name}: {r.reason}{tag}")
        for p in problems(judged, m.name):
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, _, _ = production()
    models = list(models)
    results = evaluate_models(models)
    print(report(models, results))
    return 1 if any(problems(r, name) for name, r in results.items()) else 0


if __name__ == "__main__":
    sys.exit(main())
