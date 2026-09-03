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

**Recorded misses** (:data:`MISSES`). Rule B5 says to record a failed acceptance
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
is lying (rule B10).
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
    Quantity(24, "[α/Fe] bimodality", "dimensionless", None, None, None, "qualitative", "Thick disc α-enhanced across a wide [Fe/H] range", "BHG16 §5.2.2", note="S2 (simple) and S9 (advanced) operationalise this as a category_scalar and set field/expect. Debt #9 asks whether it appears without a merger."),
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

    def __post_init__(self) -> None:
        if self.row not in {q.n for q in QUANTITIES}:
            raise SpecError(f"recorded miss names row {self.row}, which is not in the table")
        if self.debt < 1 or not self.since.startswith("S"):
            raise SpecError(f"row {self.row}: a recorded miss needs a debt number and a session")
        if not self.reason.strip() or not self.prediction.strip():
            raise SpecError(f"row {self.row}: a recorded miss needs a reason and a prediction")


_MISSES: tuple[Miss, ...] = (
    Miss(
        row=20,
        debt=17,
        since="S2",
        reason=(
            "The target has no width. Nakanishi & Sofue's 8.0 x 10^9 Msun is quoted with no "
            "uncertainty, so a pointwise check fails for any float that is not bit-exact, and the "
            "model's 8.49 x 10^9 agrees to 6% - as close as a galaxy's total gas mass is ever "
            "known. This is a defect in the acceptance table, not in the model, and it is recorded "
            "rather than fixed by widening the interval to whatever the model happens to produce "
            "(rule B5)."
        ),
        prediction=(
            "Someone has to read the source and record its actual uncertainty; anything above 6% "
            "makes this row pass on the value it already has. If the source really quotes none, "
            "the row should be marked as having no testable target rather than a zero-width one, "
            "which is a change to the table's schema and belongs to the S10 audit."
        ),
    ),
    Miss(
        row=4,
        debt=13,
        since="S2",
        reason=(
            "The model has two independent routes to the disc scale length and they disagree. "
            "lambda_d and MMW98 predict 2.60 kpc (disc_scale_length_spin); the star formation "
            "history builds a stellar profile with a fitted scale length of 3.74 kpc, 44% larger, "
            "because the accreting gas must be more extended than the stars for the model to "
            "retain the observed gas mass at all. Row 4 reads the fitted one, because row 4 "
            "measures starlight and not angular momentum."
        ),
        prediction=(
            "One of the two is wrong and the disagreement is not a tolerance to be split. Either "
            "GAS_DISC_SCALE_RATIO is too large - in which case the gas mass and SFR fall out of "
            "their windows together - or MMW98's structure factors, which S1 folded into lambda_d "
            "unmodelled (debt #6), account for the difference. S3 can decide it by modelling f_c "
            "and f_R explicitly; if neither moves it, the infall profile is the wrong shape."
        ),
    ),
    Miss(
        row=22,
        debt=15,
        since="S2",
        reason=(
            "Inside-out growth alone produces a third of the observed gradient: -0.019 dex/kpc "
            "against -0.06. The gradient was measured to be exactly insensitive to the yield, so "
            "the level and the tilt are set separately and this is a statement about the tilt. "
            "Reproducing -0.06 needs an inside-out index near 3, and the source that gives "
            "tau_0 = 7 Gyr at R_0 gives a linear tau(R), i.e. n = 1; the model cannot have both."
        ),
        prediction=(
            "Outflows are the missing tilt. Metal loss scaling with escape velocity removes more "
            "from the outer disc than the inner one, steepening the gradient without touching the "
            "inside-out index. S9 adds them (GALAXY_INPUTS.md 8); if the gradient does not steepen "
            "towards -0.06 when it does, this explanation is wrong and the infall law is."
        ),
    ),
    Miss(
        row=23,
        debt=15,
        since="S2",
        reason=(
            "The old-population gradient is -0.009 dex/kpc against -0.04, too flat for the same "
            "reason row 22 is: every gradient this model produces is about a third of the observed "
            "one. Migration itself is close to right - the young/old ratio comes out 2.3 against "
            "an observed 1.75 - so the error is in the gradient it is flattening, not in the "
            "flattening."
        ),
        prediction=(
            "Whatever steepens row 22 steepens this row by the same factor and the young/old ratio "
            "does not move, because migration and enrichment are separate mechanisms here. If "
            "row 22 steepens and this one does not, migration_efficiency is wrong too."
        ),
    ),
    Miss(
        row=3,
        debt=11,
        since="S1",
        reason=(
            "S1 has one baryonic component. The whole retained budget sits in an exponential of "
            "scale length 2.6 kpc, so the ~8 x 10^9 Msun of gas that really extends to 30 kpc and "
            "the ~1.5 x 10^10 Msun bulge that really sits inside 1 kpc are both in the disc, "
            "over-concentrating mass inside R0 and pushing v_c up."
        ),
        prediction=(
            "S1 predicted that giving the gas its own shallower profile would lower v_tan by about "
            "the 5 km/s of the miss, to 246.4. S2 did it and got 237.2: the direction was right "
            "and the magnitude was not, because the same change that moved the gas out also "
            "broadened the stellar disc from 2.60 to 3.74 kpc (debt #13). Row 3 now misses low "
            "rather than high, and closing debt #13 is what should close it. If row 3 does not "
            "land in [245, 251] once the two scale lengths agree, the missing mass at R_0 is the "
            "bulge, which arrives at S3-S4."
        ),
    ),
)

MISSES: Mapping[int, Miss] = MappingProxyType({m.row: m for m in _MISSES})
if len(MISSES) != len(_MISSES):
    raise SpecError("a row is registered as a miss twice")


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


def summary(results: Iterable[Result]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for r in results:
        counts[r.status] += 1
    return counts


def unexplained(results: Iterable[Result]) -> tuple[Result, ...]:
    """Failing rows with no entry in :data:`MISSES`. These are what should stop a build."""
    return tuple(r for r in results if r.status == "fail" and r.n not in MISSES)


def stale(results: Iterable[Result]) -> tuple[Result, ...]:
    """Registered misses that now pass: the recorded explanation is wrong or spent (rule B10)."""
    return tuple(r for r in results if r.status == "pass" and r.n in MISSES)


def problems(results: Iterable[Result]) -> list[Problem]:
    """Everything a spec run should fail on. A recorded, still-failing miss is not one."""
    results = list(results)
    out = [
        Problem("spec", "acceptance", f"row {r.n} ({r.name}) fails and is not a recorded miss: {r.reason}")
        for r in unexplained(results)
    ]
    out += [
        Problem(
            "spec",
            "stale-miss",
            f"row {r.n} ({r.name}) is registered as a miss since {MISSES[r.n].since} (debt "
            f"#{MISSES[r.n].debt}) but now passes: {r.reason}. Remove the entry or find out why.",
        )
        for r in stale(results)
    ]
    return out


def report(models: Iterable[Model], **run_kwargs: Any) -> str:
    lines = ["spec"]
    for m in models:
        results = run(m, **run_kwargs)
        s = summary(results)
        recorded = sum(1 for r in results if r.status == "fail" and r.n in MISSES)
        head = f"  model {m.name}: {s['pass']} pass, {s['fail']} fail, {s['not-yet-computable']} not-yet-computable of {len(results)}"
        if recorded:
            head += f" ({recorded} of the failures recorded as misses)"
        lines.append(head)
        for r in results:
            tag = ""
            if r.n in MISSES and r.status == "fail":
                tag = f" [recorded miss, debt #{MISSES[r.n].debt}, since {MISSES[r.n].since}]"
            lines.append(f"    {r.n:>2} {r.status:<19} {r.name}: {r.reason}{tag}")
        for p in problems(results):
            lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    models, _, _ = production()
    print(report(models))
    return 1 if any(problems(run(m)) for m in models) else 0


if __name__ == "__main__":
    sys.exit(main())
