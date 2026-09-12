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


# Row 2's miss (debt #47, S16) was removed at S17 when the spheroid took 13% of the budget out of
# what the disc accretes (D121); it reads 1.755 since S18 built the derived threshold, still inside.
# Row 7's miss (debt #42, since S16) was removed at S20: it reads 962 pc, inside 720-1080, because
# MERGER_HEATING was re-derived (120 -> 88.8, D128). The constant had been 'scaled so the merger
# leaves the pre-existing disc at about 30 km/s' as if the kick were the thick disc's whole
# dispersion, while the assembly stage composes it in quadrature with 27 km/s of secular heating
# those stars already carry; net of that, the observed 35 km/s [recall: Bensby+03] needs a kick of
# 22 km/s. The row is green on the constant's re-derivation and not on the thick disc's shape -
# Sigma(R0) is unmoved at 47.3 and rows 5, 9 and 11 still miss - so if the thick disc is ever born
# extended (debt #49) Sigma(R0) moves and this row with it. A miss that passes is an error to leave
# (debt #29); the reason is here.
# S21 (a) read the citation (AUDIT_II_A.md A-14): the 35 is Bensby et al. 2003's Table 1 adopted value for a
# selection function, with no uncertainty; the measurement it stands in for is Soubiran et al. 2003's 39 +/- 4,
# at which the constant is 112.3 and this row reads 1193 (out) with row 3 at 250.97 (in). The row is green on
# the round number at the -1 sigma edge of the measurement; S22 rules whether the constant is re-set.
_MISSES: tuple[Miss, ...] = (
    Miss(
        row=3,
        debt=11,
        since="S20",
        reason=(
            "251.03 km/s against 248 +/- 3, out by 0.03 (250.96 and inside by 0.04 at S18; 251.3 at "
            "S17; 252.9 at S16; 260.1 at S15). S18 landed it on the merger's radial kick, worth -0.2, "
            "and S20 re-derived the kick's constant: MERGER_HEATING was scaled so the merger alone "
            "leaves the pre-existing disc at 30 km/s, but the model composes the kick in quadrature "
            "with 27 km/s of secular heating those stars already carry, so the thick disc read 40.4 "
            "against Bensby et al. 2003's 35. Net of the secular heating the kick is 22 km/s (88.8, "
            "debt #42, D128), the radial spread at R0 falls 1.47 -> 1.09 kpc, fewer of the disc's "
            "stars are carried across R0, and the row rises by 0.07 - back outside by less than the "
            "solver's own correction (D124). Rows 3 and 12 still have one cause: the bar the model has "
            "no dynamics for (D121)."
        ),
        prediction=(
            "The bar's: 7e9 of disc buckled into the spheroid reads this row at 249.4 (D121) and row "
            "12 inside with it; if the buckling is built at a scale radius that keeps row 14 inside "
            "and this row does not fall to ~249, D121's arithmetic is wrong. Not a lever: the kick, "
            "now set by a cited dispersion; nor z_f, derived at S15 (D117); nor the first infall's "
            "law, which S20 probed five ways and which moves this row by under 0.1 (D128). **S21 (a) ran "
            "the bar's**: 7e9 at the derived scale radius reads 249.64, inside - held to 0.2 km/s - and "
            "row 14 at 144, not 123 (AUDIT_II_A.md A-3, tests/test_audit_ii_a.py). The row still closes "
            "with the bar; what the bar costs is row 14's."
        ),
    ),
    Miss(
        row=5,
        model="simple",
        debt=19,
        since="S3",
        reason=(
            "1.09 kpc against 2.0 +/- 0.2 (1.17 at S18 on the 120 km/s kick, D128; 1.18 until S18; "
            "1.32 until S17; 1.17 until S13). The "
            "thick disc is every star born before the last major merger, and by then the disc is "
            "small: the early episode accretes on the thin disc's inside-out law, tau(R) = 7 Gyr x "
            "R/R0, so by 3.8 Gyr only 42% of the early gas at R0 has arrived and 31% at 12 kpc, and "
            "the star formation threshold holds what has arrived outside ~4 kpc as gas. **S18 tested "
            "the prediction this row carried since S3 - that the merger's radial heating spreads the "
            "thick disc - and killed it by the number**: the kick is derived (the vertical impulse read "
            "isotropically, turned into a displacement through kappa and the guiding-centre shift) and "
            "is 1.5 kpc at R0 but 0.3 at 2 kpc, because the inner disc is stiff, so it moves this row "
            "1.18 -> 1.51 on the constant threshold and 0.93 -> 1.17 on the derived one (D124). The "
            "derived threshold lowers it because Kennicutt's Sigma_crit is 26 Msun/pc2 at 4 kpc and "
            "11 at R0, so the early gas forms stars closer in still."
        ),
        prediction=(
            "The thick disc has to be born extended, and S18's probe found where that is decided: the "
            "early episode's arrival law. The two-infall framework the inside-out index cites gives "
            "the *first* infall a short, radius-independent timescale (~1 Gyr) and reserves "
            "tau_D(R) for the second; this model applies tau(R) to both. With the early episode at "
            "1 Gyr everywhere the pre-merger disc reads 2.11 kpc here - inside - but the whole early "
            "share turns into thick disc (row 11 1.7e10, row 9 0.62, row 2 1.30), and shrinking the "
            "share re-truncates it through the threshold (at a merger share of 0.8: rows 9 and 11 "
            "inside, this row 1.35). **S20 ran the prediction and it failed** (D128): with the first "
            "infall on the halo's own dynamical time at z_f (0.55 Gyr; 1 Gyr reads the same) this row "
            "reads 1.95 at the default share, 2.15 at 0.3, 1.70 at 0.65 and 1.26 at 0.8 - it lands "
            "only where row 11 reads 1.7e10 and row 9 0.56, and at 0.8, where row 11 is inside, rows 5 "
            "and 9 read 1.26 and 0.04. Rows 5 and 11 still trade through the share, so the "
            "pre-committed reading applies: the star formation law at high redshift is what is "
            "wrong, not the split and not the arrival law (debt #49). Also dead: the halo's own "
            "mass-accretion history as the first infall (0.98 here, row 11 1.5e9: it delivers too "
            "little before the merger) and a compact early disc at R_d(z_f) (0.62-0.82). Stated so it "
            "can fail: this row lands with rows 9 and 11 only when most of the early gas is still gas "
            "at the merger, which needs the early disc to consume gas slower than it accretes it and "
            "then to stop - a star formation law with a burst and a cut, not a Kennicutt law with a "
            "threshold. **S21 (a) ran that** (AUDIT_II_A.md A-5): star formation off from 1.0 to 3.8 Gyr "
            "on the fast first infall leaves the early gas as gas at the merger, rows 8, 9, 10 and 11 land "
            "together for the first time, and this row reads 1.61 - 0.2 short. By debt #19's own reading "
            "the split criterion is what is wrong; S22 rules."
        ),
    ),
    Miss(
        row=8,
        model="simple",
        debt=19,
        since="S18",
        reason=(
            "0.016 against 4% +/- 2% (0.013 at S18): row 9's surface-density ratio divided by the "
            "scale-height ratio (0.0455 x 328/962), so it carries no information row 9 does not and "
            "fails with it (it read 0.033 while row 9 read 0.135). Registered separately only because "
            "the table judges it separately; rows 8 and 9 are not independent and are never tuned apart."
        ),
        prediction=(
            "It follows row 9 exactly, scaled by row 6 over row 7: whatever lands row 9 at the "
            "observed scale heights lands this one at 0.04. If row 9 is landed and this row is not, "
            "row 7 is what is wrong (debt #42's dispersion), not the thick disc's mass."
        ),
    ),
    Miss(
        row=9,
        model="simple",
        debt=19,
        since="S18",
        reason=(
            "0.0455 against 12% +/- 4% (0.051 at S18 on the 120 km/s kick, which returned 0.015 of it; "
            "the derived kick returns 0.010, D128): S3's gate, green since S3 on the cancellation debt #19 records "
            "(0.103, 0.152, 0.147, 0.135 across S3-S17: a thick disc too massive and too compact, "
            "whose errors compensated at R0), and red at S18 because the derived star formation "
            "threshold holds the reservoir the pre-merger disc formed its outer stars from: 11 "
            "Msun/pc2 at R0 against the constant 5, so the early gas at R0 never reaches it before "
            "the merger and the thick disc's surface density there falls by two thirds. Debt #47 "
            "said so in advance and pre-committed the reading: if this row cannot be restored with "
            "the threshold derived, the thick disc is what is wrong, not the threshold (D119). The "
            "radial kick returns 0.010 of it (0.036 -> 0.0455). The sweep the gate asks for, on the "
            "built model: merger share 0.3 -> 0.8 reads this row 0.131, 0.083, 0.0455, 0.019, 0.005, "
            "0.001 while row 11 reads 1.45e10, 1.21e10, 9.6e9, 7.2e9, 4.9e9, 2.8e9 - never inside "
            "together, so the cancellation is still there and the gate is not met (D124, D128)."
        ),
        prediction=(
            "Rows 5, 9 and 11 are one row: at the observed scale lengths (2.0 thick, 2.6 thin) and "
            "masses (6e9, 3.5e10) this ratio is 0.11 by arithmetic, so whatever lands row 5 at the "
            "observed mass lands this one. The candidate is the early episode's arrival law (debt "
            "#49, row 5's entry): a fast first infall reads 0.62 at the default merger share and "
            "0.13 at 0.8 on the constant threshold, 0.03 on the derived one. If that is built and "
            "this row lands with rows 5 and 11 inside together across a sweep of the merger share, "
            "the gate is met for the first time; if it lands with row 5 out, it is the same "
            "cancellation in new clothes. **S21 (a)**: it lands with row 5 out, twice - at 0.115 with row "
            "11 inside and row 5 at 1.61 on a cut-only law (A-5), and at 0.113 with row 11 inside and row 5 "
            "at 2.56 when the stars are moved through the chemistry's kernel as well as the kick at a "
            "merger share of 0.7 (A-2). Debt #50's bracket for this row was a fraction read as a ratio: "
            "both kernels read 0.266 at the default share."
        ),
    ),
    Miss(
        row=11,
        model="simple",
        debt=19,
        since="S3",
        reason=(
            "9.6e9 Msun against 6 +/- 3e9 (1.09e10 until S18; 1.30e10 at S16; 1.42e10 at S13): the "
            "pre-merger episode carries half the baryon budget, and with the derived threshold a "
            "little less of it forms stars before 3.8 Gyr, so the row is 7% over its ceiling. The "
            "radial kick conserves mass and moves it not at all. Shrinking the pre-merger episode "
            "through the merger's share lands this row at 0.6 (7.2e9) and 0.7 (4.9e9) - and reads "
            "row 9 at 0.024 and 0.007 there, which is the cancellation debt #19 has recorded since "
            "D51: a thick disc this centrally concentrated loses surface density at R0 far faster "
            "than it loses mass. Also on the record: instantaneous recycling returns 30% of every "
            "generation at birth, where an 11 Gyr population has returned nearer 45% [recall: "
            "Kroupa/Chabrier], so the present mass of the oldest stars is overstated by ~25% in "
            "both models - 9.6e9 formed is ~7.6e9 today - which is the simple model's defining "
            "approximation (debt #15's scope) and not a lever."
        ),
        prediction=(
            "Row 5 is the prerequisite, as it has been since S3, and S18 located what row 5 needs "
            "(debt #49): a first infall fast enough that the pre-merger disc is extended, with "
            "most of its gas still gas at the merger, so that the thick disc is light *and* wide "
            "and this row and row 9 move together under the merger share instead of against each "
            "other. If they still cannot be satisfied together at the right scale length once the "
            "early infall is fast, the split criterion - born before the last major merger - is "
            "what is wrong. **S21 (a)**: with the early infall fast and the early gas kept as gas to the "
            "merger this row and rows 8, 9, 10 are inside together and row 5 is 1.61 (A-5), so that "
            "sentence is now the reading."
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
            "verified, and which moves rows 20 and 2 with this one. **S21 (a) ran both** (A-3): 7e9 at the "
            "derived radius reads row 3 at 249.6 and row 14 at 144, and at 1.5, 2, 3 and 4 times the "
            "half-mass radius row 14 reads 129, 124, 121, 121.5 - never inside - so no concentration "
            "lands this row and row 14 together and the conditional cannot be reached from either side; "
            "the isotropic dispersion is the suspect (debt #52). mu = 1.06 reads this row at 1.46e10 and "
            "row 2 at 1.14 (A-9)."
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
            "cannot both be right, so the first session to build the buckling reads which. **S21 (a) read "
            "both** (A-3, A-12): the buckled 7e9 takes the row to 144 (not 123) and no concentration "
            "brings it under 121; the rotation the model computes is 160 km/s at the half-mass radius and "
            "subtracting it leaves 70. Two large errors of opposite sign, so 116 is not evidence; the "
            "prediction is now debt #52's - a V/sigma-aware dispersion with the buckled mass reads near 113."
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
        debt=17,
        since="S16",
        reason=(
            "8.09e9 Msun of hydrogen against 8.0e9, quoted with no uncertainty at all - a zero-width "
            "target that no float meets (debt #17, D100), and the number is at it: 1% over. It read "
            "4.17e9 until S16 built the high-j tail (debt #18), 6.03e9 until S18 derived the star "
            "formation threshold from the rotation curve's epicyclic frequency (debt #47, D124): "
            "Kennicutt's Sigma_crit is 11 Msun/pc2 at R0 where the constant was 5, and the gas at R0 "
            "reads 10.8 against the observed 10-13. **But the number is at the target for two "
            "reasons, and one of them is wrong**: the same threshold rises with kappa inside (44 "
            "Msun/pc2 of gas at 1 kpc, 276 at the first cell, where the Milky Way's inner disc is "
            "nearly empty), so 1.1e9 of hydrogen sits inside 4 kpc where S17 held 0.3e9 and the "
            "Galaxy holds a few 1e8. Outside 4 kpc the model reads 7.0e9 against the target's "
            "~7.7e9 - still short, by less than half of S17's shortfall."
        ),
        prediction=(
            "The row cannot pass as written; it can only be judged once Nakanishi & Sofue's own "
            "uncertainty is entered, as row 14's was at S17 (D122). What would move the number: the "
            "bar the model lacks, which clears the inner disc and would take ~0.8e9 out (debt #21) - "
            "after which the row reads ~7.3e9 and is short again - and the tail's mu across its "
            "1.06-1.4 (D119: +/-1e9). Stated so it can fail: a model with the inner reservoir "
            "drained lands this row only if the tail is larger than the median mu gives, and if it "
            "lands at the median with the reservoir still there, the reservoir is being counted as "
            "the outer HI. **S21 (a)**: it does, at every mu - the hydrogen outside 4 kpc reads 6.4 / 7.7 / "
            "7.0 / 5.9e9 across mu = 1.06 / 1.15 / 1.25 / 1.4 and never the target's ~7.7e9 (A-13)."
        ),
    ),
    Miss(
        row=6,
        model="advanced",
        debt=42,
        since="S13",
        reason=(
            "356 pc against 250-350 (373 at S18 on the 120 km/s kick; 439 until S18 derived the "
            "threshold, which holds 10.8 Msun/pc2 of gas at R0 where the constant held 6.3, so Sigma "
            "rose and h_z fell; 384 at S16, 358 at S13). The advanced thin disc is every star - the "
            "chemical split finds no thick disc (debt #27) - so it keeps the merger-heated old "
            "population, and once Sagittarius stopped delivering a tenth of the budget as young gas "
            "(debt #29, S13) the mass-weighted dispersion at R0 rose from 326 pc to 358. S20 judged "
            "rows 6 and 7 together and re-examined both heating constants (D128): MERGER_HEATING is "
            "re-derived from the thick disc's observed dispersion net of the model's own secular "
            "heating (120 -> 88.8), which lands the simple row 7 at 962 and moves this row 373 -> 356; "
            "SECULAR_HEATING stays at 25, because 20 reads the simple row 6 at 228 and 30 at 451, both "
            "out, and this row at 252 and 483. What is left, 6 pc over, is the heated old population "
            "counted as thin (debt #27): 60 km/s reads it inside at 346 and the simple row 7 at 751."
        ),
        prediction=(
            "When the valley opens (debt #27) the heated stars leave the thin disc and this row falls "
            "toward the simple model's 328. If a valley ever opens and it stays above 350 with a thick "
            "disc present, SECULAR_HEATING is wrong for both models and the age-velocity relation it "
            "was read from is the place to look. Not a lever now: MERGER_HEATING, which is set by a "
            "cited dispersion since S20 and would have to fall below 78 to land this row alone (S21 (a): "
            "below 74 - 351.4 at 78, 350.3 at 75, 348.7 at 70; A-11). The one probe that opens a real "
            "alpha-rich mode - a burst inside the alpha-fall, A-4 - reads this row at 353, inside."
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
    "S9's prediction - the inner disc fast - ran at S10, S13, S18 and S20, and every valley it "
    "opens is not the one this row asks for: each 'bimodal_wide' the detector has reported at "
    "N_t >= 1000 (tau_0 = 1 at n = 2-3; Gaia-Enceladus alone at n = 3) is a spike of the stars "
    "formed before any type Ia iron arrived, at the +0.45 plateau exactly, holding 5% of the mass, "
    "with the split at 0.39 - above the alpha-rich sequence itself - and the rest of the early "
    "population spread evenly from +0.2 to +0.45 (D128). S20 probed the mechanisms the plan and "
    "the register named, the repo unchanged, all at the default grid and the dip checked across "
    "N_t = 1000-4000: the first infall on the halo's dynamical time at z_f (dip 0.15); a compact "
    "early disc at R_d(z_f) (0.00, and row 22 -0.147); the halo's own mass-accretion history (no "
    "thick disc at all); the threshold switch's width (0.15 -> 0.19); a bar-driven drain of the "
    "inner disc (a spike valley, row 10 halved); a mass-loaded wind at the metal escape fraction's "
    "own odds (a spike valley at dip 0.6-0.7 with the budget gutted: row 2 0.4-0.7, row 3 214-224). "
    "The cause is the shape of the chemistry's own histogram: dN/d[alpha/Fe] = Psi / |d[alpha/Fe]/dt|, "
    "and in a threshold-regulated Kennicutt disc fed from t = 0 the star formation rate is already "
    "falling while the alpha-fall runs, so the early population never piles up anywhere short of "
    "the plateau. Prediction, stated so it can fail: a thick mode near +0.3 needs the first phase's "
    "star formation to *rise* while its gas is rich and then be cut within ~1 Gyr - a burst - and "
    "no accretion law under a constant-efficiency Kennicutt law does that (the reading debts #47 "
    "and #49 reached for rows 5, 9 and 11 from the other side); if a mechanism ends the first "
    "phase sharply and the histogram still shows no mode short of the plateau, the DTD's minimum "
    "delay (0.15 Gyr, a spike by construction) is what the detector is reading, not a thick disc. "
    "**S21 (a) attacked this and it held with its clock corrected** (AUDIT_II_A.md A-4): the strongest "
    "accretion law (the early gas in 0.1 Gyr) reads the spike valley (dip 0.78, split 0.21); a x5 burst of "
    "star formation in the first 0.8 Gyr forms its stars at the plateau and makes nothing; the same burst "
    "placed inside the alpha-fall, 1-2 Gyr on the fast first infall and cut 2-3 Gyr, makes an alpha-rich "
    "mode at +0.35 holding a tenth of the mass in one 0.02 dex bin, twice the spike, with the advanced row "
    "6 at 353. The burst has to run after the first Ia iron and while the gas is rich - not within a "
    "gigayear of t = 0 - and nothing in the repo makes one; in the simple model it is #49's trade unchanged."
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
        row=22,
        model="advanced",
        debt=47,
        since="S18",
        reason=(
            "-0.0698 dex/kpc against -0.069 to -0.049, out by 0.0008: the row passed at -0.064 until "
            "S18 derived the star formation threshold. Kennicutt's Sigma_crit falls outward with "
            "kappa (47 Msun/pc2 at 2 kpc, 26 at 4, 11 at R0, 4 at 20), so the inner disc holds two to "
            "three times the gas it did and the wind, refitted to keep R0 solar (982 -> 860 km/s, "
            "debt #43), keeps more metals everywhere; the gradient steepened by 0.006 and crossed the "
            "edge. The refit is not what did it: +/-10% on WIND_SPEED moves the row by 0.0008 (D124)."
        ),
        prediction=(
            "The inner gas is the prediction: the model holds 33 Msun/pc2 at 2 kpc, 44 at 1 and 276 at "
            "the first cell - 1.5e9 of gas inside 4 kpc where S17 held 0.4e9 - where "
            "the Milky Way has ~5-20, because the threshold is evaluated at a 6 km/s dispersion the "
            "inner gas does not have and because the bar that clears the inner disc is not modelled "
            "(debt #21). A gas dispersion that rises inward makes it worse (8 km/s everywhere reads "
            "-0.089), so the bar is the candidate; if the inner gas is cleared and the row still "
            "reads below -0.069, the wind's tilt (debt #26) is what is wrong. Not the lever: "
            "GAS_DISC_SCALE_RATIO 1.25 reads -0.047 and is the wrong answer that passes (debt #45). "
            "**S21 (a) ran it and the mechanism is dead** (A-7): the row is fitted over 4-12 kpc and the "
            "reservoir is inside 4 - emptied to 4e8 (the threshold capped at 5 Msun/pc2 there) the row reads "
            "-0.0699, unmoved; capped at the R0 value everywhere inside R0 it reads -0.0794, further out; "
            "the constant 5 everywhere reads -0.0633. What steepened it is the gas the threshold holds "
            "inside the fit window (22.8 Msun/pc2 at 4 kpc, 6.1 at 12, against 10.2 and 4.7) with the wind "
            "refitted to keep R0 solar. By this entry's own reading the wind's tilt (debt #26) is what is "
            "wrong, and the bar is not this row's lever."
        ),
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
            "steep to begin with. A measurement of the gradient at 10 Gyr decides between them. **S21 "
            "(a)**: 2.5 kpc reads -0.048, inside, with the young/old ratio at 1.22 - under 1.75 now - and "
            "2.0 kpc inverts it (0.81); the ratio convicts the old stars' starting point (A-10). **S22 "
            "corrected that**: both points are below where the ratio crosses 1.75, and the crossing is "
            "inside this row's window - at 3.0 kpc the old gradient reads -0.033 and the ratio 1.76, so "
            "one width lands the row and the ratio together and it is the citation's that does not. "
            "**This is the one recorded miss whose cause is a constant the model could tune**, and it is "
            "not tuned because 3.6 kpc is cited (Frankel et al. 2018) and moving it with both readings "
            "known is what rule B5 forbids. The disc's structure wants a third width, under 1.8 (#50)."
        ),
    ),
    Miss(
        row=24,
        model="advanced",
        debt=27,
        since="S9",
        reason=(
            "'single' against 'bimodal_wide' at the default grid (N_t = 2000; 1000 and 4000 read the "
            "same, and N_t = 8 manufactures a valley). The [α/Fe] plane exists — the plateau is at "
            "+0.45 and the present-day gas at R₀ is at +0.05 — but the stars at R₀ form one mode "
            "at +0.17 (+0.21 until S18's threshold), where the local track lingers while the delayed "
            "iron catches up with a star formation history that never pauses; the 21% born before "
            "the merger are spread evenly from +0.14 to +0.42 and make no second mode (D128)."
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
