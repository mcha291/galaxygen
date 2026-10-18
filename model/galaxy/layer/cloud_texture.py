"""cloud_texture: the randomness layer's first realisation stage (checkpoint 5, S55, DECISIONS.md D214 section 5).

BUILD_III Appendix B classifies every draw in the model. Two sites are *synthetic* - a placement with no physics
behind it - and both are a molecular cloud's interior:

- **the four cloud columns** - how far and in which direction a cloud's embedded source sits from its centre, and
  how steeply and in which direction its density leans. Until S55 the ``clouds`` stage drew and published them as
  seeded. No source gives their distributions (debt #95) and the model computes nothing that would: they stand in
  for the turbulent fragmentation of a cloud. They are published here, synthetic, each with its three declarations.
  From S55 to S60 the draws were the census's own, on ``systems_seed`` and each cell's streams; **since S61 they are
  drawn on the layer's own seed** (D220 item 5): each ring's arrays on ``(texture_seed, "cloud", ring, name)``, read
  at each cloud's identity in the ring-first draw, ``(ring, i)``. With the layer off they are their neutral values -
  no offset, no gradient, angles 0 - and a cluster stands at its cloud's centre.
- **the viewer's cloud-interior noise** - the log-normal interior a renderer synthesises from a cloud's vector
  (``frontend/src/galaxy/region.ts``). Rule D5 as amended (D212) lets the viewer evaluate a function the model
  publishes and forbids it a parameter of its own, so the function's three parameters are the model's.
  **They are constants, not fields** (gate G1, change 4): a 4, a 2 and a 0.5 that are the same with the layer on
  or off are not "a realisation from the layer's seed". They are three level-0 constants this stage declares
  (D214 section 2 as amended: "a layer stage's *fields* are synthetic; a constant it declares is a constant"),
  read and checked here (:func:`interior`) and carried by ``/api/clouds``' header as ``cloud_interior``. With the
  layer off the viewer draws the interior smooth.

**The seed** (gate G1, change 2c). From S55 to S60 the four columns were drawn on ``systems_seed``, which was what
Phase R's "existing draw streams keep their seeds and their values" required and what rule A10's "drawn ... on the
randomness layer's own seed" forbade. **Resolved at S61 (D220 item 5)**: they are drawn on ``texture_seed``, so
rerolling it changes the clouds' interiors and nothing else (BUILD_III section 1c, rule 1). ``systems_seed`` is
still read, for the census's layout alone - which ring and which place in it each published cloud is - and no
value here is drawn on it.

**What the offset does not keep** (gate G1, change 5). The source's offset and direction place the cluster; the
offset moves a cluster by a few hundred parsecs at most in radius against a 75 pc radial step, so it can stand in
another ring than its cloud. Since S61 (D220 item 6) the stages that bin clusters by radius bin by the cloud's
radius, carried on the cluster as ``cluster_birth_radius``, so what they publish no longer moves with it. No clamp:
the offset keeps its measured range. The two declarations say so with the numbers.

**The layout.** A cloud is named ``(cell, index)``, and its texture is read at its ring identity ``(ring, i)``, so
the stage needs the census's ring layout (``clouds.cloud_layout``). The published cloud columns do not carry it; it
is the census's own ring counts and sector allocation, redrawn here exactly as the cluster census redraws them
(``clusters.census_of_clouds``). That reads the gas's pattern through ``compose``, as the ``clouds`` stage does: a
layer stage may.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages.clouds import TEXTURE_COLUMNS, RingLayout, cloud_layout, ring_draws
from galaxy.stages.gas_pattern import GAS_PATTERN_CONSTANTS, GAS_PATTERN_READS
from galaxy.stages.spurs import SPUR_READS

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


def draw(seed: int, layout: RingLayout, size: np.ndarray) -> dict[str, np.ndarray]:
    """The four columns for the clouds of ``layout`` (a ``clouds.RingLayout``), in the census's order: each ring's
    arrays on the layer's seed, ``(texture_seed, "cloud", ring, name)``, drawn whole and read at each cloud's
    ``(ring, i)`` (D220 items 1 and 5) - the offset uniform over the cloud's volume (its size times the cube root
    of a uniform), the two angles uniform over the circle, the gradient uniform on [0, 1]."""
    size = np.asarray(size, dtype=float)
    u = ring_draws(seed, "cloud", layout, ("source_offset", "source_angle", "gradient", "gradient_angle"))
    return {
        "cloud_source_offset": size * np.cbrt(u["source_offset"]),
        "cloud_source_angle": 2.0 * math.pi * u["source_angle"],
        "cloud_density_gradient": u["gradient"],
        "cloud_gradient_angle": 2.0 * math.pi * u["gradient_angle"],
    }


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
# and 43.7 % of the mass, 157 in another cell ring), again at S56 when the census became another draw (D215: the
# clouds follow five arm modes' ridge, not one's: 1 598 of 12 814, 12.5 % and 43.8 %, 137), again at S57 when
# the clouds came to follow the gas's steady response to those modes (D216: 1 598 of 12 829, 12.5 % and 43.7 %,
# 139), again at S58 when the bar's reach came to hold its lanes and the two-armed mode the bar's phase (D217:
# 1 600 of 12 826, 12.5 % and 43.6 %, 137), again at S59 when the winding came in seeded segments (D218: up to 223
# pc, 255 pc, 1 576 of 12 840, 12.3 % and 42.9 %, 142), again at S60 when the arms became a census of pieces
# (D219: up to 249 pc, 265 pc, 1 605 of 12 916, 12.4 % and 42.9 %, 140), and again at S61 when the census was drawn
# ring-first and the binners came to read the cloud's radius (D220 items 1 and 6).
# S67 (D231): re-read again when the clouds' size law (82 / 35 Msun/pc2, the 150 pc cap) shrank the inner clouds the
# offset is drawn inside (was 230 pc, 248 pc, 1 581 of 12 710, 12.4 % and 36.1 %, 133).
_CONSERVES_PLACEMENT = (
    "The cloud's mass and the cluster's mass: the column places, it does not weigh. It does not keep the cluster in "
    "its cloud's ring: at S67 the offset moves a cluster by up to 140 pc in radius (its own length reaches 146 pc) "
    "against a 75 pc radial step and puts 1 376 of 12 710 "
    "clusters (10.8 %, 31.8 % of the cluster mass) in another radial ring and 119 in another cell ring than their "
    "cloud. What the stages that bin clusters by radius publish does not move with it: since S61 `nebular` and "
    "`bubbles` bin a cluster by the radius its cloud's ring drew, `cluster_birth_radius`, a draw on the ring's "
    "stream (D220 item 6 and part II; #95). No clamp: the offset keeps its measured range, and the cluster stands where the offset puts it."
)
_STATISTIC = (
    "none read (#95): no source gives the distribution, so the draw's own - {law} - is a stated guess and the "
    "debt stays open."
)
_PER_CLOUD = " Zero for every cloud with the randomness layer off."
# Which seed, said in each declaration (gate G1, change 6): the layer's own seed is texture_seed (rule A10), and
# these four are not on it yet.
_SEED = (" Drawn on `texture_seed`, the layer's own seed, at the cloud's place in its ring's draw: the contradiction "
         "with rule A10 that stood from S55 is resolved at S61 (D220 item 5).")


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
    # The interior's three constants are this stage's to declare: read here, so a parameter set that is not a
    # noise stops the run rather than reaching a renderer (the API serves the same function's answer).
    interior(c)
    # The census's own ring layout, redrawn on its seed (cheap: each ring's count and sector uniforms); the four
    # columns are drawn on the layer's (D220 item 5).
    layout = cloud_layout(ctx.fields, R, int(ctx.seeds["systems_seed"]), c)
    return _compose.cloud_texture(ctx.fields, int(ctx.seeds["texture_seed"]), layout, ctx.fields["cloud_size"])


CLOUD_TEXTURE = IMPLEMENTATIONS.register(
    Stage(
        id="cloud_texture", slot="cloud_texture", checkpoint=5,
        about=(
            "The randomness layer's realisation of a molecular cloud's interior: where each cloud's embedded "
            "source sits and how its density leans, drawn per cloud on the layer's own seed. Synthetic: it "
            "stands in for turbulent fragmentation the model does not compute, weighs nothing, and is zero with "
            "the layer off. It also holds the shape of the noise a renderer synthesises the interior from - an "
            "octave count, a lacunarity and a gain, constants and not fields."
        ),
        compute=compute_cloud_texture,
        layer_stage=True,
        # S61 (D220 item 5): the four columns are drawn on texture_seed; systems_seed gives the census's layout only.
        reads_seeds=("systems_seed", "texture_seed"),
        reads_constants=(
            # The census's layout: the mass function's mean and the gas pattern's two constants, as the census reads them.
            "R_SUN", "GMC_MASS_SLOPE_INNER", "GMC_MASS_TRUNCATION_INNER", "GMC_MASS_SLOPE_OUTER",
            "GMC_MASS_TRUNCATION_OUTER", "GMC_MASS_MIN", *GAS_PATTERN_CONSTANTS,
            # The cloud-interior noise's parameters: constants this stage declares (gate G1, change 4).
            "CLOUD_INTERIOR_OCTAVES", "CLOUD_INTERIOR_LACUNARITY", "CLOUD_INTERIOR_GAIN",
        ),
        requires=(
            "cloud_size", "gas_molecular_surface_density",
            *GAS_PATTERN_READS,  # S57 (D216): the layout's gas response reads the stellar modes, their phases and the disc
            *SPUR_READS,  # S62 (D221 item 7 as amended): the census's layout is the spurred gas pattern's
        ),
        publishes=(CLOUD_SOURCE_OFFSET, CLOUD_SOURCE_ANGLE, CLOUD_GRADIENT, CLOUD_GRADIENT_ANGLE),
    )
)
