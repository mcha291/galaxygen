"""cloud_texture: the randomness layer's first realisation stage (checkpoint 5, S55, DECISIONS.md D214 section 5).

BUILD_III Appendix B classifies every draw in the model. Two sites are *synthetic* - a placement with no physics
behind it - and both are a molecular cloud's interior:

- **the four cloud columns** - how far and in which direction a cloud's embedded source sits from its centre, and
  how steeply and in which direction its density leans. Until S55 the ``clouds`` stage drew and published them as
  seeded. No source gives their distributions (debt #95) and the model computes nothing that would: they stand in
  for the turbulent fragmentation of a cloud. They are published here, synthetic, each with its three declarations.
  **The draws are unchanged**: the same seed (``systems_seed``), the same stream paths
  (``(seed, "cloud", cell, name)``), the same arithmetic, so every value is the bit it was. With the layer off
  they are their neutral values - no offset, no gradient, angles 0 - and a cluster stands at its cloud's centre.
- **the viewer's cloud-interior noise** - the log-normal interior a renderer synthesises from a cloud's vector
  (``frontend/src/galaxy/region.ts``). Rule D5 as amended (D212) lets the viewer evaluate a function the model
  publishes and forbids it a parameter of its own, so the function's three parameters are the model's.
  **They are constants, not fields** (gate G1, change 4): a 4, a 2 and a 0.5 that are the same with the layer on
  or off are not "a realisation from the layer's seed". They are three level-0 constants this stage declares
  (D214 section 2 as amended: "a layer stage's *fields* are synthetic; a constant it declares is a constant"),
  read and checked here (:func:`interior`) and carried by ``/api/clouds``' header as ``cloud_interior``. With the
  layer off the viewer draws the interior smooth.

**The seed, and what it contradicts** (gate G1, change 2c). The four columns are drawn on ``systems_seed``, which
is what Phase R's "existing draw streams keep their seeds and their values" requires and what rule A10's "drawn ...
on the randomness layer's own seed" forbids. The contradiction stands until L1 moves them to ``texture_seed``; each
of the four declarations says so. ``texture_seed`` is not read here.

**What the offset does not keep** (gate G1, change 5). The source's offset and direction place the cluster; the
offset moves a cluster by up to 249 pc in radius against a 75 pc radial step, so it can stand in another ring than its cloud, and what
the stages that bin clusters by radius publish moves with it. The two declarations say so with the numbers; there
is no clamp in Phase R, because no value moves in Phase R.

**The layout.** A cloud is named ``(cell, index)`` and its streams are its cell's, so the stage needs the census's
``(cell, count)`` layout. The published cloud columns do not carry it; the counts are the census's own Poisson
draws, redrawn here exactly as the cluster census redraws them (``clusters.census_of_clouds``). That reads the
gas's pattern through ``compose``, as the ``clouds`` stage does: a layer stage may.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.clouds import TEXTURE_COLUMNS, cloud_counts, expected_counts
from galaxy.stages.gas_pattern import GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS

# The cloud-interior noise's three parameters, by the name each has on the wire and the level-0 constant that holds
# it (the viewer's own choices until S55, none read, #110: the constants' about lines carry the source).
INTERIOR_CONSTANTS: Mapping[str, str] = {
    "octaves": "CLOUD_INTERIOR_OCTAVES",
    "lacunarity": "CLOUD_INTERIOR_LACUNARITY",
    "gain": "CLOUD_INTERIOR_GAIN",
}


def interior(constants: Mapping[str, Any]) -> dict[str, float | int]:
    """The cloud-interior noise's parameters as ``/api/clouds``' header carries them - ``{"octaves": 4,
    "lacunarity": 2.0, "gain": 0.5}`` at the model's values - read from the model's constants and refused if they
    are not a noise: a whole number of octaves, at least one, and a positive finite lacunarity and gain."""
    octaves, lacunarity, gain = (float(constants[INTERIOR_CONSTANTS[k]]) for k in ("octaves", "lacunarity", "gain"))
    if not (octaves >= 1.0 and octaves == int(octaves)):
        raise ValueError(f"the cloud-interior noise has a whole number of octaves, at least one; got {octaves!r}")
    if not (math.isfinite(lacunarity) and lacunarity > 0.0 and math.isfinite(gain) and gain > 0.0):
        raise ValueError(f"the cloud-interior noise's lacunarity and gain are positive; got {lacunarity!r}, {gain!r}")
    return {"octaves": int(octaves), "lacunarity": lacunarity, "gain": gain}


def draw(seed: int, counts: Sequence[tuple[int, int]], size: np.ndarray) -> dict[str, np.ndarray]:
    """The four columns for the clouds of ``counts``' cells, in the census's order: each cell's own streams, as
    the cloud census drew them until S55 - the offset uniform over the cloud's volume (its size times the cube
    root of a uniform), the two angles uniform over the circle, the gradient uniform on [0, 1]."""
    size = np.asarray(size, dtype=float)
    parts: dict[str, list[np.ndarray]] = {name: [] for name in TEXTURE_COLUMNS}
    offset = 0
    for cell, count in counts:

        def u(name: str, k: int = count, cell: int = cell) -> np.ndarray:
            return _seeds.rng(seed, "cloud", int(cell), name).random(k)

        parts["cloud_source_offset"].append(size[offset:offset + count] * np.cbrt(u("source_offset")))
        parts["cloud_source_angle"].append(2.0 * math.pi * u("source_angle"))
        parts["cloud_density_gradient"].append(u("gradient"))
        parts["cloud_gradient_angle"].append(2.0 * math.pi * u("gradient_angle"))
        offset += count
    return {name: np.concatenate(p) if p else np.zeros(0) for name, p in parts.items()}


def neutral(n: int) -> dict[str, np.ndarray]:
    """The four columns with the layer off: the source at the cloud's centre, no gradient, both angles 0."""
    return {name: np.zeros(int(n)) for name in TEXTURE_COLUMNS}


# --- declarations ----------------------------------------------------------------------------------

# D191's ruling for the two the viewer does not read, moved here with their declarations (tests/test_v4.py).
NOT_DRAWN_WHY: dict[str, str] = {
    "cloud_source_offset": "it is drawn where the cluster stands: the cluster census places its cluster by this "
                           "offset, and the cavity is carved at the cluster's position.",
    "cloud_source_angle": "it is drawn where the cluster stands, as the offset is.",
}

_STANDS_IN_FOR = (
    "The cloud's internal structure - where inside it its embedded source formed and which way its density "
    "leans - which is the turbulent fragmentation of the cloud, a process the model does not compute."
)
# What the two gradient columns keep: they lean a cloud's density and place nothing outside it.
_CONSERVES_GRADIENT = (
    "The cloud's mass and the census's count: the column places a source and a lean inside a cloud and weighs "
    "nothing. No ring's molecular mass, cloud count or cluster mass changes with it."
)
# What the source's offset and direction keep, and what they do not, with the measured numbers (gate G1, change 5;
# BUILD_III section 1c rule 2 as amended: "a declaration states what it does not keep, with the measured number").
# Measured on the production grid at the default inputs, the layer on: first at S55 (1 610 of 12 930 clusters, 12.5 %
# and 43.7 % of the mass, 157 in another cell ring), and again at S56 when the census became another draw (D215: the
# clouds follow five arm modes' ridge, not one's; read on the window of D215 ruling 11, the third gate turn).
_CONSERVES_PLACEMENT = (
    "The cloud's mass and the cluster's mass: the column places, it does not weigh. It does not keep the cluster in "
    "its cloud's ring: at S56 the offset moves a cluster by up to 249 pc in radius (its own length reaches 265 pc) "
    "against a 75 pc radial step and puts 1 598 of 12 814 "
    "clusters (12.5 %, 43.8 % of the cluster mass) in another radial ring and 137 in another cell ring than their "
    "cloud, so a ring's realised cluster mass, and what `nebular` and `bubbles` bin from it, move with it (#95; L1 "
    "decides whether the offset is bounded to the cell or the cluster binned by its cloud's ring)."
)
_STATISTIC = (
    "none read (#95): no source gives the distribution, so the draw's own - {law} - is a stated guess and the "
    "debt stays open."
)
_PER_CLOUD = " Zero for every cloud with the randomness layer off."
# Which seed, said in each declaration (gate G1, change 6): the layer's own seed is texture_seed (rule A10), and
# these four are not on it yet.
_SEED = " Drawn on `systems_seed`, the stream Phase R keeps; on `texture_seed` from L1."


def _column(name: str, label: str, unit: str, about: str, law: str, conserves: str) -> FieldDecl:
    why = NOT_DRAWN_WHY.get(name)
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cloud", ramp=Ramp("viridis"), meaningful_zero=True,
        provenance="synthetic",
        about=about + _SEED + _PER_CLOUD + (f" **Not drawn by the viewer** (D191): {why}" if why else ""),
        stands_in_for=_STANDS_IN_FOR, conserves=conserves, statistic=_STATISTIC.format(law=law),
    )


CLOUD_SOURCE_OFFSET = _column(
    "cloud_source_offset", "Embedded source offset", "pc",
    "How far from the cloud's centre its embedded cluster sits, drawn uniformly over the cloud's volume: pillars "
    "are the shadows of clumps that survived the ionization front eating the cloud from one side, so this is what "
    "makes them point one way. No source gives the distribution (debt #95).",
    "uniform over the cloud's volume", _CONSERVES_PLACEMENT,
)
CLOUD_SOURCE_ANGLE = _column(
    "cloud_source_angle", "Embedded source direction", "rad",
    "The direction from the cloud's centre to its embedded source, in the plane, uniform.",
    "uniform over the circle, in the plane", _CONSERVES_PLACEMENT,
)
CLOUD_GRADIENT = _column(
    "cloud_density_gradient", "Density gradient", "dimensionless",
    "How steeply the cloud's density runs across it, 0 flat to 1 the whole contrast over one radius, drawn "
    "uniform: bubbles sit off-centre because they expand into a gradient. No source gives the distribution "
    "(debt #95).",
    "uniform between flat and the whole contrast over one radius", _CONSERVES_GRADIENT,
)
CLOUD_GRADIENT_ANGLE = _column(
    "cloud_gradient_angle", "Density gradient direction", "rad",
    "The direction the density increases in, in the plane, uniform.",
    "uniform over the circle, in the plane", _CONSERVES_GRADIENT,
)


def compute_cloud_texture(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    seed = int(ctx.seeds["systems_seed"])
    # The interior's three constants are this stage's to declare: read here, so a parameter set that is not a
    # noise stops the run rather than reaching a renderer (the API serves the same function's answer).
    interior(c)
    # The census's own layout, redrawn: the counts are its Poisson draws on the cells' own streams (cheap).
    counts = cloud_counts(expected_counts(ctx.fields, R, c), seed)
    return _compose.cloud_texture(ctx.fields, seed, counts, ctx.fields["cloud_size"])


CLOUD_TEXTURE = IMPLEMENTATIONS.register(
    Stage(
        id="cloud_texture", slot="cloud_texture", checkpoint=5,
        about=(
            "The randomness layer's realisation of a molecular cloud's interior: where each cloud's embedded "
            "source sits and how its density leans, drawn per cloud on the census's own streams. Synthetic: it "
            "stands in for turbulent fragmentation the model does not compute, weighs nothing, and is zero with "
            "the layer off. It also holds the shape of the noise a renderer synthesises the interior from - an "
            "octave count, a lacunarity and a gain, constants and not fields."
        ),
        compute=compute_cloud_texture,
        layer_stage=True,
        reads_seeds=("systems_seed",),
        reads_constants=(
            # The census's layout: the mass function's mean and the gas pattern's ridge, as the census reads them.
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", *GAS_PATTERN_CONSTANTS,
            # The cloud-interior noise's parameters: constants this stage declares (gate G1, change 4).
            "CLOUD_INTERIOR_OCTAVES", "CLOUD_INTERIOR_LACUNARITY", "CLOUD_INTERIOR_GAIN",
        ),
        requires=(
            "cloud_size", "gas_molecular_surface_density",
            *GAS_PATTERN_READS,  # S56 (D215): the layout's ridge follows the stellar modes and their phases
        ),
        publishes=(CLOUD_SOURCE_OFFSET, CLOUD_SOURCE_ANGLE, CLOUD_GRADIENT, CLOUD_GRADIENT_ANGLE),
    )
)
