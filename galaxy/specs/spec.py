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
  the **median** of at least ``ENSEMBLE_MIN`` values lies in ``[lo, hi]``; the
  central 95 % interval is published beside it. S13 revised the S0 criterion
  (the interval *intersects* the target), which rewarded a noisier model (debt
  #38); no target was relaxed (rule B5).
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
ENSEMBLE_MIN = 41  # S13 (debt #38): the smallest n at which a central 95% interval excludes one draw at each end
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
        if not self.testable and not self.note.strip():
            raise SpecError(
                f"row {self.n}: a pointwise row whose target has zero width cannot be met by any "
                f"float that is not bit-exact, and must say so in its note (debt #17)"
            )

    @property
    def testable(self) -> bool:
        """Whether any value could pass this row (debt #17).

        A pointwise check against a target quoted without an uncertainty fails
        for every float that is not exactly equal, so the row reports the table's
        defect and not the model's. Said here rather than left in prose: the
        table needed a way to say "no testable target", the alternative being to
        invent an interval, and inventing one *now* — with the model's answer
        already known — is the thing rule B5 exists to prevent. A statistical row
        passes on its ensemble's median (S13, debt #38), which no float meets at
        zero width either, so row 14 is untestable until its source's uncertainty is
        entered; only a qualitative row has no interval to be zero.
        """
        return self.mode == "qualitative" or self.lo is None or self.lo != self.hi

    @property
    def width(self) -> float | None:
        """``hi − lo``: how far a value can move before the verdict can change; None without an interval.

        It is what the convergence sweep judges a grid drift against (``specs/convergence.py``).
        """
        return None if self.lo is None or self.hi is None else self.hi - self.lo


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
    Quantity(14, "Bulge velocity dispersion (rms)", "km/s", "bulge_velocity_dispersion", 110.0, 116.0, "statistical", "113 ± 3 km/s", _BHG16, note="The source's own uncertainty, entered at S17 and not chosen here: BHG16 §4.3 gives the bulge's mass-weighted dispersion within its half-mass radius as \"the rms is σ_rms,b ≈ 113 km/s, to ≈3 km/s\", so the row has a testable target and leaves debt #17's list (rows 20 and 21 stay on it). The model's number was already known when the uncertainty was looked up, which is recorded in D122 so that a reader can judge; the width is the source's verbatim. Statistical per debt #8, against a field the model derives, so every seed reads the same number."),
    Quantity(15, "Bar half-length", "kpc", "bar_half_length", 4.8, 5.2, "pointwise", "5.0 ± 0.2 kpc", _BHG16),
    Quantity(16, "Bar pattern speed", "km/s/kpc", "bar_pattern_speed", 34.0, 52.0, "statistical", "43 ± 9 km/s/kpc", _BHG16, note="Statistical per debt #8."),
    Quantity(17, "Bar corotation radius", "kpc", "bar_corotation_radius", 4.5, 7.0, "statistical", "4.5–7.0 kpc", _BHG16, note="Statistical per debt #8."),
    Quantity(18, "Black hole mass", "Msun", "black_hole_mass", 4.0e6, 4.4e6, "statistical", "4.2 ± 0.2 × 10⁶ M☉", _BHG16, note="Debt #2: derived from M–σ plus a seeded residual (ruling 10); the Milky Way sits 5–6× below the relation, so this is expected to miss by ~0.75 dex and must not be re-scoped to include the miss (GALAXY_INPUTS.md §3, rule B5). Statistical per debt #8."),
    Quantity(19, "Halo virial mass", "Msun", "halo_virial_mass", 1.0e12, 1.3e12, "pointwise", "1.0–1.3 × 10¹² M☉", "McMillan"),
    Quantity(20, "Total gas mass (<30 kpc)", "Msun", "hydrogen_mass_30kpc", 8.0e9, 8.0e9, "pointwise", "8.0 × 10⁹ M☉", "Nakanishi & Sofue 15", note="HI + H₂ from 21 cm and CO: hydrogen, so the row reads the gas's hydrogen mass, (1 − Y) of gas_mass_30kpc (debt #41, S13). No uncertainty quoted: zero-width target (debt #17)."),
    Quantity(21, "Gas HI:H₂ split", "dimensionless", "gas_h2_fraction", 0.11, 0.11, "pointwise", "89% : 11%", "Nakanishi & Sofue 15", note="Read as the H₂ mass fraction f_H₂ = 0.11 (HI = 1 − f_H₂). No uncertainty quoted: zero-width target; see row 20."),
    Quantity(22, "Present-day metallicity gradient", "dex/kpc", "metallicity_gradient", -0.069, -0.049, "pointwise", "−0.06 dex/kpc", "Trentin+24 −0.064 ± 0.003; Feuillet+19 −0.059 ± 0.010", note="Interval is the union of the two cited measurements [inferred]; the table itself quotes −0.06 with no error."),
    Quantity(23, "Gradient evolution with age", "dex/kpc", "metallicity_gradient_old", -0.05, -0.03, "pointwise", "−0.07 (young) → −0.04 (>10 Gyr)", "Willett+23", note="Two values at two ages; one row can name one field, so S2 operationalises it as the *old* end (>10 Gyr, target −0.04) and leaves the young end to row 22's companion field metallicity_gradient_young, which the same stage publishes. Interval is ±0.01 around −0.04 [inferred]: the source quotes no uncertainty and a zero-width target would make the row untestable rather than strict."),
    Quantity(24, "[α/Fe] bimodality", "dimensionless", "alpha_sequence", None, None, "qualitative", "Thick disc α-enhanced across a wide [Fe/H] range", "BHG16 §5.2.2", expect="bimodal_wide", note="Judged on the [α/Fe] mass distribution of the stars now at R₀, migrants included: two modes with a valley between them, and the α-rich mode spanning at least 0.5 dex of [Fe/H] (S9). Only the advanced model publishes the field; the simple model has one abundance and stays not-yet-computable (rule B3). Debt #9 asks whether it appears without a merger."),
)

if [q.n for q in QUANTITIES] != list(range(1, len(QUANTITIES) + 1)):
    raise SpecError("quantities must be numbered 1..N in order")


def untestable(quantities: Iterable[Quantity] = QUANTITIES) -> tuple[Quantity, ...]:
    """Rows no value can pass, because the source quotes no uncertainty (debt #17).

    A standing defect in the table, not in any model, so it is reported once
    rather than per model and it fails nothing: the rows it names still evaluate
    and still print their number. What it stops is the defect spreading quietly —
    a new row added without an interval now has to say so in its note, and this
    list is pinned by a test.
    """
    return tuple(q for q in quantities if not q.testable)


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


# Row 2's miss (debt #47, S16) was removed at S17: the spheroid took 13% of the budget out of
# what the disc accretes and the rate fell 2.08 -> 1.82, inside 1.65 +/- 0.19 for the first time
# since S2. It is *not* removed because the mechanism debt #47 names was built - the threshold is
# still the constant 5 Msun/pc2 at the bottom of its cited range - so the debt stays open and rows
# 9 and 20 are still judged with it at S18 (D121). What the row would do under the derived
# threshold is no longer measured; S16's probe read 1.95 with the whole budget in the disc.
_MISSES: tuple[Miss, ...] = (
    Miss(
        row=7,
        model="simple",
        debt=19,
        since="S16",
        reason=(
            "1126 pc against 900 +/- 180, over by 46, from 1042 (inside) until S16: the high-j tail "
            "took 7.6% of the budget out of the exponential (D119), the stellar surface density at R0 "
            "fell 51.6 -> 47.6 Msun/pc2, and the thick disc, which is too massive and too compact "
            "(debt #19) and sat at the top of its window on the cancellation debt #19 records, "
            "puffed up with the weaker self-gravity."
        ),
        prediction=(
            "This row is debt #19's with rows 5, 9 and 11: radial heating with the vertical kick "
            "(S18) spreads the thick disc, and a thick disc at its own mass in the observed scale "
            "length has the surface density that holds its height inside 720-1080. If S18 restores "
            "rows 5 and 11 and this row stays over, the vertical stage's heating constants are what "
            "is wrong (debt #42), not the thick disc's shape."
        ),
    ),
    Miss(
        row=5,
        model="simple",
        debt=19,
        since="S3",
        reason=(
            "The thick disc's scale length is 1.32 kpc against 2.0 (1.17 until S13 moved a tenth of "
            "the budget out of the pre-merger episode, debt #29). It forms before the merger, "
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
            "1.42e10 Msun against 6e9 (1.07e10 until S13): the pre-merger episode carries half the "
            "baryon budget now that Sagittarius delivers a physical share (debt #29), and should "
            "carry nearer 15%. **Row 9, S3's gate, passes at 0.152 only because this error and the "
            "row 5 error compensate** (0.103 before S13; the ceiling is 0.16). Raising the merger's "
            "gas_fraction to shrink the thick disc collapses row 9, because a thick disc this "
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
        debt=11,
        since="S15",
        reason=(
            "251.3 km/s against 248 +/- 3: too much mass inside R0, by a quarter of a km/s over the "
            "window, with the halo contracted around the disc (S14), the assembly epoch at its "
            "derived default (S15) and both ends of the angular-momentum distribution built (S16, "
            "S17). **The prediction this miss carried has failed and the number is what killed it**: "
            "the bulge was to be worth 5-8 km/s (D110) and it is worth 1.6. D110's probe drew a "
            "spheroid from the stellar disc in proportion on the *uncontracted* S13 halo; the "
            "spheroid the model derives comes out of the accreting budget instead, and that budget "
            "included the 15% of the exponential that sat outside R0 and pulled the Sun outward - so "
            "moving it inward gives back nearly as much as the disc's flattening loses. Measured at "
            "S17: 1.4e10 in the spheroid is worth 3.7 km/s and 1.7e10 is worth 4.2, so no bulge mass "
            "in the observed range closes 4.9 km/s on its own either. "
            "The row's history: S1 blamed the gas profile (246.4 predicted); S2 gave it one and got "
            "237.2, the stellar disc broadening at the same time; S3 corrected that and the miss "
            "returned to 256, blamed on the compact disc (debt #18); S13 converted c_vir to c200 "
            "(debt #12) and the row read 242.7, low, with the contraction named as 'several km/s' "
            "[recall]; S14 solved the contraction and it was 28 km/s - 270.8, high by 20. S15 found "
            "the epoch's default, 2.5, had been validated against measurements of the contracted "
            "halo (an NFW fitted to it reads c200 = 18.5, over the 10-18 span, not the 14.4 claimed) "
            "and derived it from the LCDM median for the default mass instead: z_f = 1.66, c200 = 8.24 "
            "before the response, 15.4 after. The less concentrated halo responds more (r_i/r_f 1.50) "
            "and its share at R0 is 165.8 km/s; the row reads 260.1. The escape velocity at R0 fell "
            "585 -> 569, inside its observed 530-580; WIND_SPEED was refitted 1028 -> 999 (debt #43). "
            "What is left is the baryons: 5.9e10 Msun in one exponential at 2.6 kpc, with no bulge "
            "and no extended component (debts #11, #18)."
        ),
        prediction=(
            "This row and row 12 now have one cause and it is the bar. The spheroid the model derives "
            "is 7.7e9 against the observed 1.4-1.7e10, and what is missing is the box/peanut a bar "
            "makes of the inner disc, which BHG16 §4.2 says is most of the Milky Way's bulge and which "
            "this model does not have (debt #21: the bar is a scaled length, not a dynamics). "
            "Prediction, stated so it can fail: a spheroid of 1.4e10 - the observed bulge, reached by "
            "adding the missing 7e9 to the same reservoir - reads 249.4 here and lands the row, and "
            "1.7e10 reads 248.7, so **closing row 12 closes row 3 and the interval it lands in is not "
            "wide**. If a session builds the buckling and this row does not fall below 251, the "
            "baryon distribution is not the cause and debt #46's calibration is - A = 1.6 at w = 0.8 "
            "reads 238.1 now, out the other way, and is not adopted, because the Auriga-calibrated "
            "response [recall: Cautun et al. 2020] agrees with Gnedin et al. 2004's at R0 to 2 km/s. "
            "The same change is measured to push row 14 to 123 km/s, outside 110-116, unless the "
            "spheroid's scale radius grows with its mass; that is the tension to watch. Not a lever: "
            "the epoch below 1.3 (the row is met at 1.3-1.4, and the relation's scatter runs to 1.08), "
            "a baryon retention of 0.25 (fails row 1). Discriminants: halo_concentration_contracted "
            "against 10-18 (15.0), halo_density_sun against 0.008-0.013 Msun/pc3 (inside at every "
            "epoch, so it does not discriminate), the escape velocity at R0 against 530-580, and "
            "row 19, which none of these moves."
        ),
    ),
    Miss(
        row=12,
        debt=11,
        since="S17",
        reason=(
            "7.71e9 Msun against 1.4-1.7e10, low by 45%. The spheroid is derived rather than sized: "
            "it is the low-j end of the halo's angular-momentum distribution, the mass no exponential "
            "disc of this scale length can hold, 13.2% of the retained budget inside a crossing at "
            "2.46 kpc with half of it inside 0.88 kpc (D121). That is one formation channel - "
            "material that could never have been a disc - and BHG16 §4.2 says it is the smaller one: "
            "the Milky Way's bulge is mostly the box/peanut inner part of the bar, made of disc stars "
            "the bar rearranged, and this model has no bar dynamics to make it with (debt #21). The "
            "shape constant carries the rest of the spread: across mu = 1.06-1.40, the range Bullock "
            "et al. 2001 quote, the spheroid runs 1.46e10 down to 5.6e9, so the observed mass is "
            "inside the distribution's own scatter and outside what the median value gives (debt #47)."
        ),
        prediction=(
            "Buckling the inner disc is the mechanism, and it is testable in the direction that "
            "matters: it must add mass without adding compactness. Adding 7e9 to the spheroid at the "
            "derived scale radius reads row 3 at 249.4 (inside, closing that row too) and row 14 at "
            "123 km/s (outside 110-116), so a bar-built component has to be *less* concentrated than "
            "the dissipational one - which is what a box/peanut is. If a session builds it at a scale "
            "radius that keeps row 14 inside and row 12 still misses, the low-j excess is not the "
            "bulge's seed and the whole derivation is wrong. Not a lever: mu, which is S16's and "
            "verified, and which moves rows 20 and 2 with this one."
        ),
    ),
    Miss(
        row=13,
        debt=11,
        since="S17",
        reason=(
            "0.153 against 0.30 +/- 0.06. The numerator is row 12 and misses low by 45% for the "
            "reason recorded there; the denominator is row 1, which passes. So this row carries no "
            "information row 12 does not, and it is registered separately only because the table "
            "judges it separately. The ensemble is degenerate - the spheroid's mass is derived, so "
            "all 41 seeds read the same number - which is the honest reading of a row §4b made "
            "statistical against a residual the model turned out not to need (rule A10)."
        ),
        prediction=(
            "It follows row 12 exactly: at the observed 1.4-1.7e10 the fraction is 0.28-0.34, inside. "
            "If row 12 is ever landed and this row is not, the model's total stellar mass is wrong "
            "rather than its bulge."
        ),
    ),
    Miss(
        row=14,
        debt=11,
        since="S17",
        reason=(
            "116.2 km/s against 113 +/- 3, high by 0.16 - a seventh of a km/s outside a window that "
            "S17 entered from the source rather than chose (debt #17 discharged for this row; BHG16 "
            "§4.3 quotes 'the rms is sigma_rms,b = 113 km/s, to = 3 km/s'). The number is the "
            "isotropic spherical Jeans equation in the model's own total potential, mass-weighted "
            "inside the spheroid's half-mass radius to match how the source defines it, and it is a "
            "derivation with no fitted quantity anywhere in it. **The surprise is that it is nearly "
            "right while row 12 is 45% low**: sigma inside the half-mass radius is set by the whole "
            "enclosed mass - dark halo, disc and spheroid - so it is a weak function of the spheroid "
            "alone, and on the spheroid's self-gravity it would read 71. Isotropy is the assumption: "
            "a bulge with 83% of its support in rotation by the model's own measure has that rotation "
            "counted here as dispersion, which raises the number rather than lowering it."
        ),
        prediction=(
            "The two ways out disagree, and that is what makes this testable. If the miss is the "
            "isotropy assumption, subtracting the rotation the model already computes "
            "(bulge_classical_fraction) would take the row below 113 and row 12 would still miss; if "
            "it is the missing bar-built mass, adding 7e9 takes the row to 123 and further out. They "
            "cannot both be right, so the first session to build the buckling reads which."
        ),
    ),
    Miss(
        row=18,
        debt=2,
        since="S17",
        reason=(
            "the ensemble's median is 1.97e7 Msun against 4.2 +/- 0.2e6, high by 0.67 dex; the "
            "M-sigma mean itself, which the median estimates, is 2.86e7, high by 0.83. This is the miss "
            "GALAXY_INPUTS.md §3 says is expected at ~0.75 dex and must not be re-scoped, and it is "
            "not a defect in the model: BHG16 records the Milky Way falling 5-6x below the M-sigma "
            "relation *for elliptical galaxies and classical bulges*, and the model applies exactly "
            "that relation because ruling 10 says to derive the mean and seed the residual. The "
            "Milky Way's spheroid is a pseudobulge and pseudobulges do not correlate with the hole at "
            "all (GALAXY_INPUTS.md §13), so the mean is being asked a question it cannot answer. The "
            "model's own classical share, 0.17, says the same thing in its own terms. The row is "
            "judged on the ensemble's median (D109), which is the mean relation at any residual "
            "width, so the width - the classical 0.28 dex, because the pseudobulge end has no "
            "published number (debt #48) - moves this verdict not at all."
        ),
        prediction=(
            "The miss is the source's, not the model's, and the way to kill that explanation is to "
            "make the relation the model applies match the object it applies it to. Two candidates, "
            "both refused here as inventions: an M_bullet-M_bulge relation applied to the classical "
            "share alone reads 5.2e6 and would land the row, which is precisely why it was not "
            "adopted with the answer already known (rule B5); and a crossover on bulge type needs a "
            "constant ruling 10 declined to add. What would settle it is a published pseudobulge "
            "calibration - a zero point and a width - entered before the row is next judged. Until "
            "then the row stays red at 0.83 dex, and if a future session moves it by touching "
            "BLACK_HOLE_NORM or the dispersion, that is the tuning this entry exists to catch."
        ),
    ),
    Miss(
        row=20,
        debt=47,
        since="S16",
        reason=(
            "6.24e9 Msun of hydrogen against 8.0e9, a 22% shortfall, from 4.17e9 (48%) until S16 "
            "built the extended component (debt #18, D119): the high-j tail of the halo's "
            "angular-momentum distribution, 7.6% of the budget beyond 12 kpc, 3.6-3.7 Msun/pc2 from "
            "15 to 20 kpc, ending where the distribution's j_max lands, near 25 kpc. What is still "
            "missing is not in the tail: the model's gas at R0 is 6.8 Msun/pc2 against the observed "
            "10-13, because the constant threshold of 5 is the bottom of its cited range, and the "
            "tail's shape follows one constant, mu, whose scatter no input absorbs (debt #47). The "
            "target is zero-width (debt #17), so no float meets it."
        ),
        prediction=(
            "The derived Toomre threshold (D119's probe) reads 8.2e9 with the tail as built; that is "
            "the mechanism, judged with rows 2 and 9 at S18. The tail itself is not the lever: across "
            "mu = 1.06-1.4 this row reads 5.0-6.9e9 and row 3 does not move. If the derived threshold "
            "lands this row and row 2 is still out, the two rows are not one story."
        ),
    ),
    Miss(
        row=6,
        model="advanced",
        debt=42,
        since="S13",
        reason=(
            "358 pc against 250-350. The advanced thin disc is every star - the chemical split finds "
            "no thick disc (debt #27) - so it keeps the merger-heated old population, and once "
            "Sagittarius stopped delivering a tenth of the budget as young gas (debt #29, S13) the "
            "mass-weighted dispersion at R0 rose from 326 pc to 358. SECULAR_HEATING and "
            "MERGER_HEATING were fitted at S3 to the simple model's merger split (rule B10)."
        ),
        prediction=(
            "When the valley opens (debt #27) the heated stars leave the thin disc and this row falls "
            "toward the simple model's 255; rows 6 and 7 are then judged together with both heating "
            "constants re-examined. If it stays above 350 with a thick disc present, SECULAR_HEATING "
            "is wrong for both models and the age-velocity relation it was read from is the place "
            "to look."
        ),
    ),
    Miss(
        row=22,
        model="simple",
        debt=15,
        since="S2",
        reason=(
            "-0.024 dex/kpc against -0.06 (-0.027 when recorded at S3). The gradient was measured to be exactly insensitive to "
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
            "The old-population gradient is too flat for two reasons, not one. Row 22's tilt is "
            "a third of the observed (debt #15), and migration over-flattens on top of it: the "
            "young/old ratio is 3.18 against the observed 1.75, and 1.75 is reached near 2.9 kpc "
            "(AUDIT_RUN2.md D-2). S2 wrote 'migration itself is close to right' at a ratio of "
            "2.3; S3's smaller disc took it to 3.2 and S10 (run 2) corrected the record."
        ),
        prediction=(
            "Whatever steepens row 22 steepens this row by the same factor and leaves the "
            "young/old ratio alone, because migration and enrichment are separate mechanisms here. "
            "If row 22 steepens and this one does not, migration_efficiency is wrong too. It "
            "did, in the advanced model (debt #28), and the ratio there is 3.09: the same "
            "over-flattening with the tilt right, so the kernel is wrong independently of the tilt."
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
    # The advanced model's row 10 miss (debt #27, S9) was removed at S17. It read 5.28e10 and
    # then 5.00e10 against 3.5 ± 1e10 because with no valley the chemical split puts every star
    # in the thin disc; the spheroid took 13% of the budget out of the disc and it now reads
    # 4.26e10, inside. Nothing about the valley changed. **The row is green on the same
    # cancellation debt #11 named for the simple model** — thin = every star, and it lands only
    # because the total is smaller — so it is not evidence for the chemical split, and if debt
    # #27's valley ever appears this row will move again by the thick disc's whole mass.
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
        width = "" if q.testable else " (zero-width target, so no testable target — debt #17; see note)"
        return Result(q.n, q.name, "pass" if ok else "fail", f"{value:.6g} {'in' if ok else 'not in'} [{q.lo:.6g}, {q.hi:.6g}]{width}", value)
    # statistical
    if ensemble is None or q.field not in ensemble:
        return Result(q.n, q.name, nyc, f"statistical: needs an ensemble of >= {ENSEMBLE_MIN} seeded runs (debt #8)")
    values = np.asarray(ensemble[q.field], dtype=float)
    if values.size < ENSEMBLE_MIN:
        return Result(q.n, q.name, nyc, f"statistical: ensemble has {values.size} values, needs >= {ENSEMBLE_MIN}")
    # S13 (debt #38): the verdict is the median's, so a noisier model is not an easier one to
    # pass; the central interval is published beside it, at an n where 95% means something.
    tail = 100.0 * (1.0 - CENTRAL) / 2.0
    p_lo, p_hi = np.percentile(values, [tail, 100.0 - tail])
    median = float(np.median(values))
    ok = q.lo <= median <= q.hi
    width = "" if q.testable else " (zero-width target, so no testable target — debt #17; see note)"
    return Result(
        q.n,
        q.name,
        "pass" if ok else "fail",
        f"median {median:.6g} {'in' if ok else 'not in'} [{q.lo:.6g}, {q.hi:.6g}]; central {CENTRAL:.0%} [{p_lo:.6g}, {p_hi:.6g}] (n={values.size}){width}",
        median,
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
    bad = untestable()
    if bad:
        lines.append(
            "  table: rows " + ", ".join(str(q.n) for q in bad) + " have zero-width targets and can "
            "be met by no float that is not bit-exact — a defect in the table, not in a model "
            "(debt #17). They are still evaluated and still print their number."
        )
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
