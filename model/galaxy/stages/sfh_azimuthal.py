"""Azimuthal star formation: the ``sfh`` slot's second implementation (checkpoint 4, BUILD_II Phase 2).

Everything ``sfh`` publishes, computed by ``sfh`` itself, plus one (R, φ) field: where
around each ring today's stars form. The design is BUILD_II.md Phase 2's and was made
there, not here:

- **No history gains a φ axis.** ``sfr_surface_density_history`` is (R, t) at 400 × 2000;
  φ at 360 would make it 288 million cells. And it would be physically wrong: gas orbits
  and mixes azimuthally on ~100 Myr, far faster than enrichment, so the chemistry *should*
  be the azimuthal average. The arms do not change what the gas becomes; they change where
  stars are when they form.
- **The modulation is the star formation law's own non-linearity** read through the
  gas's own density contrast g(R, φ) (``gas_pattern``, S51, D210): Σ_gas(R, φ) = Σ_gas(R) g,
  then Ψ ∝ Σ_gas^n s(Σ_gas) with the threshold's switch ``s`` applied *per cell* — an arm
  can carry gas over the threshold the ring mean sits under — and the result is divided by
  its own mean around the ring. Until S51 the gas was taken to follow the stellar contrast,
  one cosine harmonic whose half-maximum is half the arm-to-arm period; from S51 to S56 it
  was a narrow ridge of a measured width and contrast on the stellar crest; since S57 (D216)
  it is the gas's steady response to the stellar arm modes, solved ring by ring - as broad
  as the stellar arm, far deeper between the arms, with a ratio of means of two to three in
  the mid disc that nothing put in - so today's star formation crowds the crests and all but
  leaves the gaps. So ``sfr_surface_density`` times the modulation integrates over φ back to
  ``sfr_surface_density`` at every radius: a redistribution, not a new source
  (RENDER_PHYSICS.md §7). Where a ring forms nothing at all the modulation is 1.
- **Each cell holds the law's mean over the cell, not the law at the cell's mean gas** (S86, BUILD_V M1, debt
  #154): since S59 the young stars are placed by the law at a point (``systems.Modulation``), and the table
  became a second reading of it - the law at each cell's mean contrast, which differs from the point law's cell
  mean wherever a cell's contrast is not one number (the bar footprint's edge: 1.07 in a cell, 0.59 % of the
  worst ring's young weight on the Milky Way template). Since S86 the table is the reader's own cell means,
  renormalised round the ring (:func:`modulation_cells`), so the viewer's young light and the census's young stars
  read one law.
- **Inside a bar's reach it reads the bar's footprint, not the lanes** (S58, D217's follow-up at
  the gate). The gas's own contrast there carries the bar's two gas lanes, whose width is a
  declared placeholder no source gave; "the lanes' one unsourced number (the width) must not
  drive a census". So g here is ``star_formation_gas_contrast``, which ``gas_pattern``
  publishes beside its own contrast: the same blend with the lanes' excess spread evenly over
  the stellar bar's footprint - the measured ratio of the gas inside the footprint to the gas
  outside it kept, no ridge. Outside every bar's reach and in an unbarred galaxy the two
  fields are the same numbers, so nothing moves there. The dust and the cloud census keep the
  lanes. (The laned alternative, as the gate read it before ruling: 88-93 % of a ring's star
  formation in its top tenth of cells at 2-3.3 kpc, and a largest modulation of 17.2 - the
  placeholder's ridge raised to the law's exponent.)

**Why the normalisation is the plain ring mean.** BUILD_II Phase 2 words it as "its
gas-weighted mean around the ring is 1", and the gate beside it as "integrates to the
axisymmetric SFR over φ at every radius". For a field that multiplies the *rate* those two
cannot both hold — Σ_φ c M = Σ_φ M only if the modulation is uncorrelated with the gas,
and an arm is exactly where both are high — and the gate is the physics: the total star
formation is the axisymmetric model's, only its place moves. The mean is taken over the
grid's φ cells, which are uniform, so it is the φ-integral over 2π exactly.

**Provenance.** ``star_formation_gas_contrast`` is seeded (through the pattern's drawn pitch, amplitudes
and bar, and since S56 the layer's phases of the arm modes), so the modulation is seeded. The
histories are not: ``sfh_azimuthal`` *extends* ``sfh`` (``Stage.extends``), so every field
the two share is computed by ``sfh``'s own compute in ``sfh``'s own restricted view, which
cannot reach the contrast, and ``graph`` labels them from ``sfh``'s reads. Declaring them
seeded would have been a false label on reproducible numbers — and it would have
propagated to every downstream stage the two models share (rule A10, D55).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, extend
from galaxy.layer import compose as _compose
from galaxy.stages import systems as _systems  # the young stars' point reader, whose cell means the table is (S86, #154)
from galaxy.stages.gas_pattern import GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS
from galaxy.stages.sfh import SFH, star_formation_rate


def sfr_modulation(gas: np.ndarray, threshold: np.ndarray, contrast: np.ndarray, index: float) -> np.ndarray:
    """Ψ(R, φ)/Ψ(R): the local law on Σ_gas(R) c(R, φ), switch per cell, divided by its ring mean.

    ``gas`` and ``threshold`` are (R,), ``contrast`` (R, φ). The normalisation of the law
    divides out, so only its exponent and its threshold matter. A ring whose every cell forms
    nothing reads 1: there is nothing there to redistribute.

    **Since S86 (BUILD_V M1, debt #154) not the published table**: this is the law at each cell's *mean* contrast,
    which the table was from S27 to S85; the law is not linear, so where a cell's contrast is not one number - the
    bar footprint's edge crossing it - this differs from the law's mean over the cell (1.07 in a cell, 0.59 % of
    the worst ring's young weight on the Milky Way template at S70). Kept as that form, which the tests read beside
    the table. The table is :func:`modulation_cells`.
    """
    local_gas = np.asarray(gas, dtype=float)[:, None] * np.maximum(np.asarray(contrast, dtype=float), 0.0)
    local = star_formation_rate(local_gas, 1.0, index, np.asarray(threshold, dtype=float)[:, None])
    mean = local.mean(axis=1, keepdims=True)
    return np.where(mean > 0.0, local / np.where(mean > 0.0, mean, 1.0), 1.0)


def modulation_cells(fields: Mapping[str, Any], R: np.ndarray, edges: np.ndarray, constants: Mapping[str, Any],
                     gas: np.ndarray, threshold: np.ndarray, index: float) -> np.ndarray:
    """The published table (S86, debt #154, the remedy Fable named at S59: "the table's correct form is the cell
    mean of the law of the point function"): on every grid ring and φ cell, the mean over the cell of the young
    stars' own reader - ``systems.Modulation``, the star formation law applied to the gas pattern's point function
    and normalised round the ring by its quadrature - its integral over each sector taken piecewise between the
    contrast's breaks by a Gauss rule (``Modulation.sector_means_at``), then divided by its own mean round the ring.

    The division is the plain ring mean this field has always been divided by (the module's note); here it takes
    out the reader's normaliser's quadrature error - the cells' ring mean is 1 to 1.5e-4 on the Milky Way template
    without it - so the rate times this integrates back to the axisymmetric rate exactly, and the table is the
    census's reader's cell means to that accuracy. No gas pattern (none built, or flat) is the law of a uniform
    ring: 1 everywhere, as the reader is."""
    reader = _systems.Modulation(_compose.gas_pattern(fields, R, constants), R, gas, threshold, index)
    cells = reader.sector_means_at(R, edges)
    mean = cells.mean(axis=1, keepdims=True)
    return np.where(mean > 0.0, cells / np.where(mean > 0.0, mean, 1.0), 1.0)


SFR_MODULATION = FieldDecl(
    name="sfr_modulation", label="Star formation modulation Ψ(R, φ)/Ψ(R)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R", "phi"), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    optional=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the star formation law read through the gas's composed contrast -
    # and 1 everywhere with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Where around each ring today's stars form, relative to the ring's mean: the gas follows "
        "its own contrast, its steady response to the stellar arms, not the stars' own contrast - "
        "and inside a bar's reach the gas raised evenly over the stellar bar's footprint, not the "
        "bar's two gas lanes, whose width no source gave: star formation follows the bar's "
        "footprint; the star formation law's own exponent and its "
        "threshold switch are applied point by point - each cell holds the law's mean over the cell, the "
        "young stars' own reader averaged over it, not the law at the cell's mean gas - and the result is "
        "divided by its mean around "
        "the ring. So it averages to exactly 1 on every ring and the star formation rate times it "
        "integrates back to the axisymmetric rate: the arms move where stars form, not how many. "
        "Sharper than the gas's contrast, because the law is steeper than linear, and sharpest "
        "where an arm lifts gas over a threshold the ring mean sits under. Only the azimuthal "
        "model publishes it; its catalogue places the young stars by it. A composed field: with the "
        "randomness layer off it is 1 everywhere, and the young stars are placed as the old ones are, "
        "evenly round each ring."
    ),
)


def compute_modulation(ctx: Context, shared: Mapping[str, Any]) -> Mapping[str, Any]:
    # A composed field made from a composed field (S55, D214): this stage composes, it is not a physics stage,
    # and every history above it is still sfh's own. With the layer off compose gives the declared neutral
    # everywhere, exactly - the law run on a contrast of ones would give 1 only to rounding, a ring's mean of
    # equal numbers.
    # S86 (#154): the cell means of the young stars' point reader; until S86 the law at each cell's mean contrast
    # (`sfr_modulation` above, on `star_formation_gas_contrast`).
    return {
        "sfr_modulation": _compose.field(
            ctx.fields, SFR_MODULATION, (ctx.grid.R.size, ctx.grid.phi.size),
            lambda: modulation_cells(
                ctx.fields, ctx.grid.R, ctx.grid["phi"].edges, ctx.constants,
                shared["gas_surface_density"], shared["sf_threshold_surface_density"], float(ctx.constants["KS_INDEX"]),
            ),
        ),
    }


SFH_AZIMUTHAL = IMPLEMENTATIONS.register(
    extend(
        SFH,
        id="sfh_azimuthal",
        about=(
            "The inside-out star formation history exactly as the axisymmetric stage computes it — "
            "every history on (R, t), no azimuth — plus where around each ring today's stars form: "
            "the gas's own arm contrast - inside a bar's reach, the gas raised evenly over the bar's "
            "footprint - read through the star formation law's own non-linearity and "
            "renormalised around every ring, so the total is unchanged and only its place moves."
        ),
        own=compute_modulation,
        # S86 (#154): the gas pattern's own reads and constants, from which the point reader is built as the young
        # stars' is (`systems.young_reader`); was `("star_formation_gas_contrast",)`, the cells' mean contrast.
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=GAS_PATTERN_READS,
        publishes=(SFR_MODULATION,),
    )
)
