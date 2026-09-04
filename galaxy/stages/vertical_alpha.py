"""Vertical structure, advanced: the thin/thick split is chemical (checkpoint 3).

The simple model's ``vertical`` sorts stars by whether they were born before the
last major merger. That is a definition, not a measurement, and it made the
merger-free control run circular: a galaxy with no major merger had no thick
disc *by construction* (debt #20), so nothing it produced could be evidence
about whether mergers are needed (debt #9).

Here a star is thick-disc if it was born α-enhanced: if the gas it formed from
had [α/Fe] above the valley the advanced chemistry found between the two
sequences at R₀ (``alpha_split``). The criterion names nothing about the event
list. A merger still matters — through the second infall it delivers, which
dilutes the gas and restarts the sequence — but whether the result is a thick
disc is now read off the [α/Fe] plane. With no valley there is no thick disc,
which is a result rather than a rule.

The arithmetic — scale heights, dispersions, masses, the acceptance rows — is
the simple stage's, shared through ``vertical.split``; only the mask differs.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages import vertical


def alpha_mask(afe_history: np.ndarray, split: float) -> np.ndarray:
    """``(R, t)`` mask of star formation that was α-enhanced at birth.

    Gas with no metals yet has no [α/Fe]; the stars it made are the very first
    and count as thick. No valley means no thick disc at all.
    """
    if not math.isfinite(split):
        return np.zeros_like(afe_history, dtype=bool)
    return ~(afe_history < split)


def compute(ctx: Context) -> Mapping[str, Any]:
    return vertical.split(ctx, alpha_mask(ctx.fields["alpha_fe_history"], float(ctx.fields["alpha_split"])))


VERTICAL_ALPHA = IMPLEMENTATIONS.register(
    Stage(
        id="vertical_alpha",
        slot="vertical",
        checkpoint=3,
        about=(
            "Sorts the stellar populations into thin and thick by their birth [α/Fe] against the "
            "valley the advanced chemistry found, and turns their dispersions into scale heights. "
            "The advanced model's vertical stage; the criterion does not name the merger."
        ),
        compute=compute,
        reads_constants=("R_SUN", "RETURN_FRACTION"),
        requires=(
            "sfr_surface_density_history", "gas_surface_density",
            "disc_heating", "alpha_fe_history", "alpha_split",
        ),
        publishes=vertical.VERTICAL.publishes,
    )
)
