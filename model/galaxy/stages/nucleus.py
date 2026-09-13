"""Nucleus: the central black hole (checkpoint 1). The first seeded stage in the run.

**Why the hole is a draw and not a prediction** (ruling 10, GALAXY_INPUTS.md §13).
The M–σ relation is tight — 0.28 dex — for classical bulges and ellipticals, and
those are the objects that form in gas-rich mergers and coevolve with the hole.
Pseudobulges, grown out of the disc by a bar, show no significant correlation at
all ``[verified: GALAXY_INPUTS.md §13, citing Kormendy & Ho via Ho 2014]``. The
Milky Way's bulge is a pseudobulge ``[verified: BHG16 §4.2.1, §4.2.3, via
GALAXY_INPUTS.md §13]``, so deriving its hole from M–σ and calling the answer a
prediction would be applying a relation that demonstrably does not hold for the
class of object. §4b's standard remedy for exactly this — a relation with real
scatter — is to **derive the mean and seed the residual**, and M_• is its sixth
instance rather than a special case.

So this stage publishes one number, drawn: the M–σ mean of the spheroid's own
dispersion, times a lognormal residual of width ``BLACK_HOLE_SCATTER``. Acceptance
row 18 is judged statistically, against the ensemble's median (debt #8, D109), and
the median is the mean relation — which for this galaxy is about six times the
observed 4.2 × 10⁶ M☉, the miss GALAXY_INPUTS.md §3 says is expected and must not
be re-scoped (rule B5).

**Why it is its own stage.** Two reasons, both contract. ``graph.py`` derives
provenance per *stage*, so a stage that reads a seed publishes seeded fields, all
of them (D55): folding this into the halo would relabel the spheroid's mass, its
scale and its dispersion as seeded, and rule A10 forbids exactly that vagueness —
they are determined and this is not. And ``world_seed`` sits at checkpoint 1 in
GALAXY_PLAN.md §3, which is where the spheroid it needs is computed, so the stage
belongs there; until S17 nothing read that seed at all (debt #39).

**Why it is a leaf.** Nothing reads M_•. The nuclear region it governs is far
below the model's radial resolution and no later stage consults it, which is why
ruling 10 could settle for a draw rather than a branch on bulge type. Revisit if
AGN feedback ever enters the advanced model.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage

SIGMA_REFERENCE = 200.0  # km/s: the dispersion the M–σ normalisation is quoted at (Ho 2014 eq. 2)


def m_sigma(sigma: float, norm: float, index: float) -> float:
    """The M–σ mean: ``norm (σ/200 km/s)^index`` in M☉ ``[verified: GALAXY_INPUTS.md §13]``."""
    return norm * (max(sigma, 0.0) / SIGMA_REFERENCE) ** index


BLACK_HOLE_MASS = FieldDecl(
    name="black_hole_mass",
    label="Central black hole mass",
    unit="Msun",
    kind=Kind.SCALAR,
    meaningful_zero=True,
    provenance="seeded",
    about=(
        "Acceptance row 18, statistical. The M–σ mean of the spheroid's dispersion times a "
        "lognormal residual — derived mean, seeded residual, the remedy §4b already applies to "
        "five other quantities (ruling 10). It is expected to miss: the relation is calibrated on "
        "classical bulges and ellipticals, the Milky Way's spheroid is 83% pseudo by the model's "
        "own measure, and pseudobulges do not correlate with the hole at all — so the mean lands "
        "near 2.4 × 10⁷ M☉ against the observed 4.2 × 10⁶, a factor of six, which is the 5–6× "
        "BHG16 records and the ~0.75 dex GALAXY_INPUTS.md §3 says must not be re-scoped away. "
        "The residual's width is the *classical* 0.28 dex because the pseudobulge end has no "
        "published number (debt #48), so the spread shown here is narrower than the truth."
    ),
)


def compute(ctx: Context) -> Mapping[str, Any]:
    sigma = float(ctx.fields["bulge_velocity_dispersion"])
    mean = m_sigma(
        sigma, float(ctx.constants["BLACK_HOLE_NORM"]), float(ctx.constants["BLACK_HOLE_INDEX"])
    )
    # The residual is lognormal in M_•, so its width is in dex and its median is the mean
    # relation: at any width the statistical row is judged on the same number (D109).
    dex = ctx.rng("world_seed", "black_hole").normal(0.0, float(ctx.constants["BLACK_HOLE_SCATTER"]))
    return {"black_hole_mass": mean * math.pow(10.0, float(dex))}


NUCLEUS = IMPLEMENTATIONS.register(
    Stage(
        id="nucleus",
        slot="nucleus",
        checkpoint=1,
        about=(
            "The central black hole: the M–σ mean of the spheroid's dispersion with a seeded "
            "residual (ruling 10). Split from the halo so that the spheroid's own scalars keep "
            "their derived label (D55, rule A10); reads world_seed, which nothing read until S17."
        ),
        compute=compute,
        reads_seeds=("world_seed",),
        reads_constants=("BLACK_HOLE_NORM", "BLACK_HOLE_INDEX", "BLACK_HOLE_SCATTER"),
        requires=("bulge_velocity_dispersion",),
        publishes=(BLACK_HOLE_MASS,),
    )
)
