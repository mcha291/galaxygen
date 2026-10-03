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
  publishes and forbids it a parameter of its own, so the function's parameters are published here: three
  synthetic scalars, the values the viewer holds today. They are parameters, not a realisation, and do not change
  with the layer's switch; with the layer off the viewer draws the interior smooth.

``texture_seed`` is not read: it feeds only fields the third build adds (D214 section 3), and these draws existed
before it.

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

# The viewer's cloud-interior noise, as frontend/src/galaxy/region.ts holds it at S55: OCTAVES = 4 octaves of value
# noise at frequencies 1, 2, 4, 8 per unit with weights 1, 1/2, 1/4, 1/8 - a lacunarity of 2 and a gain of 1/2
# [verified: frontend/src/galaxy/region.ts, "Octaves of the value noise, frequencies 1, 2, 4, 8 per unit, weights
# 1, 1/2, 1/4, 1/8" and OCTAVES = 4]. The viewer's own choices, no source read for any of them (debt #110).
INTERIOR_OCTAVES = 4
INTERIOR_LACUNARITY = 2.0
INTERIOR_GAIN = 0.5


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
_CONSERVES = (
    "The cloud's mass and the census's count: the column places a source and a lean inside a cloud and weighs "
    "nothing. No ring's molecular mass, cloud count or cluster mass changes with it."
)
_STATISTIC = (
    "none read (#95): no source gives the distribution, so the draw's own - {law} - is a stated guess and the "
    "debt stays open."
)
_PER_CLOUD = " Zero for every cloud with the randomness layer off."


def _column(name: str, label: str, unit: str, about: str, law: str) -> FieldDecl:
    why = NOT_DRAWN_WHY.get(name)
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cloud", ramp=Ramp("viridis"), meaningful_zero=True,
        provenance="synthetic", about=about + _PER_CLOUD + (f" **Not drawn by the viewer** (D191): {why}" if why else ""),
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC.format(law=law),
    )


CLOUD_SOURCE_OFFSET = _column(
    "cloud_source_offset", "Embedded source offset", "pc",
    "How far from the cloud's centre its embedded cluster sits, drawn uniformly over the cloud's volume: pillars "
    "are the shadows of clumps that survived the ionization front eating the cloud from one side, so this is what "
    "makes them point one way. No source gives the distribution (debt #95).",
    "uniform over the cloud's volume",
)
CLOUD_SOURCE_ANGLE = _column(
    "cloud_source_angle", "Embedded source direction", "rad",
    "The direction from the cloud's centre to its embedded source, in the plane, uniform.",
    "uniform over the circle, in the plane",
)
CLOUD_GRADIENT = _column(
    "cloud_density_gradient", "Density gradient", "dimensionless",
    "How steeply the cloud's density runs across it, 0 flat to 1 the whole contrast over one radius, drawn "
    "uniform: bubbles sit off-centre because they expand into a gradient. No source gives the distribution "
    "(debt #95).",
    "uniform between flat and the whole contrast over one radius",
)
CLOUD_GRADIENT_ANGLE = _column(
    "cloud_gradient_angle", "Density gradient direction", "rad",
    "The direction the density increases in, in the plane, uniform.",
    "uniform over the circle, in the plane",
)

_INTERIOR_STANDS_IN_FOR = (
    "The density structure inside a molecular cloud - the clumps and filaments supersonic turbulence makes - "
    "which the model does not compute: it publishes each cloud's mean density and the width of its log-normal "
    "density distribution, and a renderer synthesises an interior with that width from a noise of this shape."
)
_INTERIOR_CONSERVES = (
    "The cloud's mass and mean column: the synthesised interior is a log-normal about the cloud's own mean "
    "density at the published width, so the noise redistributes the cloud's gas inside it and adds none."
)
_INTERIOR_STATISTIC = (
    "none read (#110): the noise's octave count, lacunarity and gain - and so its spectral index - are the "
    "viewer's own unsourced choices, published as they stand; the debt stays open."
)
_NOT_SHOWN = (
    " **Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of a stage that "
    "publishes cloud columns, which `scalarsAt` excludes; `/api/arrays` serves it, and the `/api/clouds` header "
    "carries it under `scalars`, where a renderer that synthesises a cloud's interior reads it."
)
_UNSWITCHED = " A parameter of the function, not a realisation: the same with the randomness layer on or off."


def _interior(name: str, label: str, unit: str, about: str) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=Kind.SCALAR, meaningful_zero=True, provenance="synthetic",
        about=about + _UNSWITCHED + _NOT_SHOWN,
        stands_in_for=_INTERIOR_STANDS_IN_FOR, conserves=_INTERIOR_CONSERVES, statistic=_INTERIOR_STATISTIC,
    )


CLOUD_INTERIOR_OCTAVES = _interior(
    "cloud_interior_octaves", "Cloud-interior noise: octaves", "count",
    "How many octaves of value noise a renderer sums to synthesise a cloud's interior: four.",
)
CLOUD_INTERIOR_LACUNARITY = _interior(
    "cloud_interior_lacunarity", "Cloud-interior noise: lacunarity", "dimensionless",
    "The ratio of one octave's spatial frequency to the last one's: two, so the four octaves stand at one, two, "
    "four and eight cycles per unit.",
)
CLOUD_INTERIOR_GAIN = _interior(
    "cloud_interior_gain", "Cloud-interior noise: gain", "dimensionless",
    "The ratio of one octave's amplitude to the last one's: a half, so the four octaves weigh one, a half, a "
    "quarter and an eighth.",
)


def compute_cloud_texture(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    seed = int(ctx.seeds["systems_seed"])
    # The census's own layout, redrawn: the counts are its Poisson draws on the cells' own streams (cheap).
    counts = cloud_counts(expected_counts(ctx.fields, R, c), seed)
    return {
        **_compose.cloud_texture(ctx.fields, seed, counts, ctx.fields["cloud_size"]),
        "cloud_interior_octaves": float(INTERIOR_OCTAVES),
        "cloud_interior_lacunarity": INTERIOR_LACUNARITY,
        "cloud_interior_gain": INTERIOR_GAIN,
    }


def interior_scalars() -> dict[str, float]:
    """The three scalars as ``/api/clouds``' header carries them (rule D4: the stage does not run for a window)."""
    return {
        "cloud_interior_octaves": float(INTERIOR_OCTAVES),
        "cloud_interior_lacunarity": INTERIOR_LACUNARITY,
        "cloud_interior_gain": INTERIOR_GAIN,
    }


CLOUD_TEXTURE = IMPLEMENTATIONS.register(
    Stage(
        id="cloud_texture", slot="cloud_texture", checkpoint=5,
        about=(
            "The randomness layer's realisation of a molecular cloud's interior: where each cloud's embedded "
            "source sits and how its density leans, drawn per cloud on the census's own streams, and the shape "
            "of the noise a renderer synthesises the interior from. Synthetic: it stands in for turbulent "
            "fragmentation the model does not compute, changes no mass and no count, and is zero with the "
            "layer off."
        ),
        compute=compute_cloud_texture,
        layer_stage=True,
        reads_seeds=("systems_seed",),
        reads_constants=(
            # The census's layout: the mass function's mean and the gas pattern's ridge, as the census reads them.
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", "GAS_ARM_WIDTH", "GAS_ARM_MASK_WIDTH",
        ),
        requires=(
            "cloud_size", "gas_molecular_surface_density",
            "gas_arm_contrast", "bar_contrast", "arm_multiplicity", "pitch_angle", "bar_half_length",
        ),
        publishes=(
            CLOUD_SOURCE_OFFSET, CLOUD_SOURCE_ANGLE, CLOUD_GRADIENT, CLOUD_GRADIENT_ANGLE,
            CLOUD_INTERIOR_OCTAVES, CLOUD_INTERIOR_LACUNARITY, CLOUD_INTERIOR_GAIN,
        ),
    )
)
