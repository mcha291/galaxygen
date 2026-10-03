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
  one cosine harmonic whose half-maximum is half the arm-to-arm period; the gas's own is a
  narrow ridge on the stellar arm's crest, half the stellar arm's width, with an
  arm-to-interarm ratio of means of two to three, so today's star formation crowds a
  narrower stripe of each arm. So ``sfr_surface_density`` times the modulation integrates over φ back to
  ``sfr_surface_density`` at every radius: a redistribution, not a new source
  (RENDER_PHYSICS.md §7). Where a ring forms nothing at all the modulation is 1.

**Why the normalisation is the plain ring mean.** BUILD_II Phase 2 words it as "its
gas-weighted mean around the ring is 1", and the gate beside it as "integrates to the
axisymmetric SFR over φ at every radius". For a field that multiplies the *rate* those two
cannot both hold — Σ_φ c M = Σ_φ M only if the modulation is uncorrelated with the gas,
and an arm is exactly where both are high — and the gate is the physics: the total star
formation is the axisymmetric model's, only its place moves. The mean is taken over the
grid's φ cells, which are uniform, so it is the φ-integral over 2π exactly.

**Provenance.** ``gas_density_contrast`` is seeded (through the pattern's drawn pitch, arm
number and bar), so the modulation is seeded. The
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
from galaxy.stages.sfh import SFH, star_formation_rate


def sfr_modulation(gas: np.ndarray, threshold: np.ndarray, contrast: np.ndarray, index: float) -> np.ndarray:
    """Ψ(R, φ)/Ψ(R): the local law on Σ_gas(R) c(R, φ), switch per cell, divided by its ring mean.

    ``gas`` and ``threshold`` are (R,), ``contrast`` (R, φ). The normalisation of the law
    divides out, so only its exponent and its threshold matter. A ring whose every cell forms
    nothing reads 1: there is nothing there to redistribute.
    """
    local_gas = np.asarray(gas, dtype=float)[:, None] * np.maximum(np.asarray(contrast, dtype=float), 0.0)
    local = star_formation_rate(local_gas, 1.0, index, np.asarray(threshold, dtype=float)[:, None])
    mean = local.mean(axis=1, keepdims=True)
    return np.where(mean > 0.0, local / np.where(mean > 0.0, mean, 1.0), 1.0)


SFR_MODULATION = FieldDecl(
    name="sfr_modulation", label="Star formation modulation Ψ(R, φ)/Ψ(R)", unit="dimensionless",
    kind=Kind.FIELD, axes=("R", "phi"), ramp=Ramp("magma", scale="log"), meaningful_zero=True,
    optional=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the star formation law read through the gas's composed contrast -
    # and 1 everywhere with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Where around each ring today's stars form, relative to the ring's mean: the gas follows "
        "its own contrast, a narrow ridge on the stellar arm's crest (the stellar bar's term inside "
        "the bar), not the stars' broader arm; the star formation law's own exponent and its "
        "threshold switch are applied cell by cell, and the result is divided by its mean around "
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
    return {
        "sfr_modulation": _compose.field(
            ctx.fields, SFR_MODULATION, (ctx.grid.R.size, ctx.grid.phi.size),
            lambda: sfr_modulation(
                shared["gas_surface_density"], shared["sf_threshold_surface_density"],
                ctx.fields["gas_density_contrast"], float(ctx.constants["KS_INDEX"]),
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
            "the gas's own arm contrast read through the star formation law's own non-linearity and "
            "renormalised around every ring, so the total is unchanged and only its place moves."
        ),
        own=compute_modulation,
        requires=("gas_density_contrast",),
        publishes=(SFR_MODULATION,),
    )
)
