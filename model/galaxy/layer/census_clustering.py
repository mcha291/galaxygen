"""census_clustering: the clustering field of the censuses, the randomness layer's hierarchy below a cell (S61, D220 part II).

The clouds the census draws, and the clusters they hold, are clustered in nearby discs on scales the arms and the
disc's profile do not reach: one power law of the correlation function below about a hundred parsecs, a shallower
one above (``docs/READING_CLUSTERING.md``). The model computes neither the turbulence nor the self-gravity that make
that hierarchy - a level-C simulation would (RESEARCH_AREAS section 1). This stage stands in for it with a
**synthetic field** on ``texture_seed`` (DECISIONS.md D220 part II items 2-3, 8)::

    f(x, y) = exp(sigma g(x, y) - sigma^2 / 2),   g = noise.fractal(seed, (x, y) in kpc, slope, octaves,
                                                                    base_frequency = 1 / scale, lacunarity 2)

a log-normal map of an isotropic octave sum of lattice noise in the plane: its coarsest lattice cell is the
hierarchy's largest scale, 190 pc, and its octaves halve to 95 and 47.5 pc, the finest its resolution. Its
statistic is the hierarchy's own excess over the structure - the ratio of the two branches of Grasha et al.
2017a's correlation function (item 2) - and its spectral slope and width are the two numbers measured to give it
(the constants' about lines say how). With the layer off there is no field: each cloud's azimuth is drawn
uniformly in its sector, as before S61.

**How it places** (item 4, under part I item 4's constraint). A cloud's radius is its ring-stream draw, which the
stages that bin clouds and clusters per ring read, so the field never moves it: it reweights the **azimuth within
the sector at the cloud's own radius**. Along the sector's arc at that radius a lattice of n midpoints (n per ring,
:meth:`ClusteringField.arc_points`) is weighted by the gas pattern's point function, sampled as the census always
sampled it (the 24 steps of ``pattern.azimuths``, linear between), times f there; the cloud's azimuth is the
inverse of those weights' cumulative sum at its ``azimuth`` uniform, uniform within the span of the lattice point
it falls in (:meth:`ClusteringField.azimuths`). The ring's count, the sector allocation and every other draw are
part I's and untouched, so **every cell's expected count and every ring's realised total is what it was**: the
field redistributes inside a sector only (rule 2). The clusters inherit it: one per cloud, at its cloud's place
plus the offset.

**What is published** (rule 5: evaluable at a point; no stored grid is the field). Two synthetic fields, each with
its three declarations: the field's 32-bit seed, the one number beside the model's constants that makes f
evaluable anywhere (``noise.fold_seed``: the fold is the model's, done once); and each level-0 cell's mean of the
map over the cell's quadrature lattice (``noise.cell_quadrature``, R dR dphi), the number a renderer divides f by
to give the cell unit mean, carried by ``/api/clouds``' header for the viewer (rule D5 as amended). With the layer
off both are NaN - an unrealised number is NaN (D164; D215's ruling 5 for a synthetic scalar), and the cell table
keeps its rows, which are the cells and are not drawn.

**One noise** (item 6). This is the coarse end of one lattice noise on one seed path,
``(texture_seed, "census_clustering")``: L2's gas fluctuation is the same function on the same path, its octaves
continuing finer; the three octaves, the scale and the width here are L1's.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import FieldDecl, Kind
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.layer import noise as _noise

# The octaves halve downward (D220 part II item 3: "octaves halving downward"): a definition of the field's form.
LACUNARITY = 2.0
# The seed path of the one lattice noise (D220 part II item 6): L2's gas fluctuation continues on it.
SEED_PATH = "census_clustering"
# The steps the census has always sampled the gas pattern's point function at across a sector (pattern.azimuths):
# the field's lattice reads the pattern between them linearly, as the census's inverse CDF always did.
PATTERN_STEPS = 24
# The constants of the model the field is made of, by role (G1's ruling 2b; galaxy/models/level0.py).
CONSTANTS: Mapping[str, str] = {
    "scale": "CENSUS_CLUSTERING_SCALE",
    "octaves": "CENSUS_CLUSTERING_OCTAVES",
    "slope": "CENSUS_CLUSTERING_SPECTRAL_SLOPE",
    "sigma": "CENSUS_CLUSTERING_WIDTH",
    "points": "CENSUS_CLUSTERING_POINTS",
}


def field_seed(texture_seed: int) -> int:
    """The field's 32-bit seed: the child of ``texture_seed`` on the noise's path, folded once (``noise.fold_seed``)."""
    return _noise.fold_seed(_seeds.child(int(texture_seed), SEED_PATH))


@dataclass(frozen=True)
class ClusteringField:
    """The clustering field: its seed and the model's five numbers. ``map`` evaluates it anywhere (rule 5)."""

    seed: int
    scale: float  # kpc, the coarsest lattice cell
    octaves: int
    slope: float  # the octaves' spectral slope
    sigma: float  # the log-normal width
    points: int  # lattice points per finest lattice cell along each axis

    @classmethod
    def of(cls, seed: Any, constants: Mapping[str, Any]) -> "ClusteringField":
        """The field from its published seed and the model's constants (the four roles of :data:`CONSTANTS`)."""
        seed = float(seed)
        if not (math.isfinite(seed) and seed == int(seed) and 0 <= seed <= _noise.MASK32):
            raise ValueError(f"the clustering field's seed is a 32-bit integer; got {seed!r}")
        octaves, points = float(constants[CONSTANTS["octaves"]]), float(constants[CONSTANTS["points"]])
        if not (octaves >= 1 and octaves == int(octaves) and points >= 1 and points == int(points)):
            raise ValueError(f"the clustering field's octaves and lattice points are whole numbers; got {octaves!r}, {points!r}")
        return cls(int(seed), float(constants[CONSTANTS["scale"]]), int(octaves), float(constants[CONSTANTS["slope"]]),
                   float(constants[CONSTANTS["sigma"]]), int(points))

    @property
    def finest_frequency(self) -> float:
        """Lattice cells per kpc of the finest octave: 2^(octaves-1) / scale (21.05 at the model's numbers)."""
        return LACUNARITY ** (self.octaves - 1) / self.scale

    def weights(self) -> tuple[float, float, float]:
        """``(gain, top, norm)`` of the octave sum (``noise.octave_weights``): what a shader reads, computing no power."""
        return _noise.octave_weights(self.slope, self.octaves, LACUNARITY, 2)

    def map(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """f at face-on positions (kpc): exp(sigma g - sigma^2/2), normaliser 1 - not unit mean in a cell; a cell's
        mean is :meth:`cell_means`'. ``x`` and ``y`` broadcast."""
        x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
        g = _noise.fractal(self.seed, np.stack([x, y], axis=-1), self.slope, self.octaves,
                           base_frequency=1.0 / self.scale, lacunarity=LACUNARITY)
        return _noise.lognormal_map(g, self.sigma)

    def arc_points(self, outer_radius: float, width: float) -> int:
        """The lattice points across a sector of angular ``width`` (rad) in a ring whose outer edge is
        ``outer_radius`` (kpc): ``points`` per finest lattice cell along the sector's outer arc, at least one. The
        same n for every cloud of the ring, so a cell's clouds are drawn alike alone or in any set (D60)."""
        return max(1, math.ceil(self.points * float(outer_radius) * float(width) * self.finest_frequency))

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, n: int, pattern: Any) -> np.ndarray:
        """Azimuths in [lo, hi] for clouds at ``radius`` (kpc) with ``azimuth`` uniforms ``u`` (D220 part II item 4).

        The n midpoints of [lo, hi] at each cloud's radius are weighted by the pattern's point function - read at
        the census's 24 steps across the sector and linearly between them, as ``pattern.azimuths`` reads it, and
        clipped at 0 - times the field there (none: 1, a pattern that places nothing). Each cloud's azimuth is
        the inverse of its row's cumulative weights at its uniform, uniform within the span of the point it falls
        in: counted, never rejected (rule B8). A row whose weights are all zero is drawn uniformly."""
        u = np.asarray(u, dtype=float)
        radius = np.asarray(radius, dtype=float)
        if u.size == 0:
            return np.zeros(0)
        n = int(n)
        step = (float(hi) - float(lo)) / n
        phi = float(lo) + (np.arange(n) + 0.5) * step  # (n,)
        w = self.map(radius[:, None] * np.cos(phi)[None, :], radius[:, None] * np.sin(phi)[None, :])
        if pattern is not None and not pattern.flat:
            grid = np.linspace(float(lo), float(hi), PATTERN_STEPS + 1)
            g = np.maximum(pattern.contrast(radius, grid), 0.0)  # (clouds, 25), the census's own sampling
            t = (phi - float(lo)) / (float(hi) - float(lo)) * PATTERN_STEPS
            k = np.minimum(t.astype(np.int64), PATTERN_STEPS - 1)
            a = t - k
            w = w * (g[:, k] * (1.0 - a) + g[:, k + 1] * a)
        total = w.sum(axis=1)
        w = np.where(total[:, None] > 0.0, w, 1.0)
        cdf = np.cumsum(w, axis=1)
        target = u * cdf[:, -1]
        j = np.minimum((cdf <= target[:, None]).sum(axis=1), n - 1)
        rows = np.arange(u.size)
        below = np.where(j > 0, cdf[rows, np.maximum(j - 1, 0)], 0.0)
        within = np.clip((target - below) / w[rows, j], 0.0, 1.0)
        return float(lo) + (j + within) * step

    def cell_means(self, R: np.ndarray) -> np.ndarray:
        """Each level-0 cell's mean of :meth:`map` over its quadrature lattice, (rings * sectors,) ring-major as the
        cells are numbered: ``noise.cell_quadrature`` in (R, phi) with ``points`` per finest lattice cell along
        each axis - the radial extent of the ring and the sector's outer arc - each point weighted by R (the
        cell's area is R dR dphi). One over it is the cell's ``noise.lognormal_normaliser``."""
        from galaxy.stages.systems import CELL_RINGS, CELL_SECTORS, cell_edges

        rings, sectors = cell_edges(np.asarray(R, dtype=float))
        width = float(sectors[1] - sectors[0])
        out = np.empty(CELL_RINGS * CELL_SECTORS)
        for r in range(CELL_RINGS):
            lo, hi = float(rings[r]), float(rings[r + 1])
            n_r = max(1, math.ceil(self.points * (hi - lo) * self.finest_frequency))
            n_phi = self.arc_points(hi, width)
            for s in range(CELL_SECTORS):
                q = _noise.cell_quadrature(lo, hi, float(sectors[s]), float(sectors[s + 1]), (n_r, n_phi))
                e = self.map(q[:, 0] * np.cos(q[:, 1]), q[:, 0] * np.sin(q[:, 1]))
                out[r * CELL_SECTORS + s] = float(np.sum(q[:, 0] * e) / np.sum(q[:, 0]))
        return out


# --- declarations ----------------------------------------------------------------------------------

_STANDS_IN_FOR = (
    "The hierarchical fragmentation of the gas below a cell's scale - where inside a ring's sector the turbulent, "
    "self-gravitating gas gathers into complexes, clouds and their clusters - which the model does not compute "
    "(a level-C simulation would: RESEARCH_AREAS section 1). Nothing the arms, the bar or the disc's profile "
    "already give: the field's own correlation is the hierarchy's excess over that structure."
)
_CONSERVES = (
    "Every cell's expected count of every census it places and every ring's realised total: it reweights a "
    "cloud's azimuth inside the cloud's own sector at the cloud's own radius, after the ring's count, the "
    "sector allocation and every other draw are made, so no count, mass or light moves between sectors or "
    "rings, and a cluster binned by its cloud's radius is binned where it was. It does not keep where a cloud "
    "sits within its sector: with the layer on a cloud's azimuth is the pattern's and the field's draw together, "
    "and with it off uniform in the sector. Nor does it keep the field's own mean in a cell at 1: a cell's mean "
    "of the map ran from 0.44 to 1.93 over 40 cells measured at S61 - the published cell mean is what divides it out."
)
_STATISTIC = (
    "1 + omega_f(r) = (r / 190 pc)^-0.64 for r < 190 pc and 1 beyond: the inner branch -0.85 +- 0.03 over the "
    "outer -0.21 +- 0.02 of the correlation function of clusters up to 40 Myr, classes 1-3, the pair-weighted "
    "average of six galaxies, meeting at 112 pc [verified: Grasha et al. 2017a, ApJ 840, 113, Table 4; "
    "docs/READING_CLUSTERING.md 1.2] - the six galaxies' inner slopes run -0.4 to -1.7 one by one; the scale "
    "190 pc is the median of the five largest hierarchical scales measured in Menon et al. 2021 Table 3 "
    "(101-845 pc; READING_CLUSTERING.md 1.3), bracketed by that 112 pc break and NGC 628's 210-300 pc (Lapeer "
    "et al. 2026; 1.5). As realised by the field alone in a flat footprint (S61): slope -0.646 +- 0.010 over "
    "47.5-190 pc, 2.45 at 47.5 pc, 0.99-1.00 beyond 380 pc (48 noise seeds). (DECISIONS.md D220 part II item 2.)"
)


def _decl(name: str, label: str, unit: str, kind: Kind, about: str, **extra: Any) -> FieldDecl:
    return FieldDecl(
        name=name, label=label, unit=unit, kind=kind, meaningful_zero=True, provenance="synthetic",
        about=about + " NaN with the randomness layer off: no field is realised then (D164; D215's ruling 5).",
        stands_in_for=_STANDS_IN_FOR, conserves=_CONSERVES, statistic=_STATISTIC, **extra,
    )


CENSUS_CLUSTERING_SEED = _decl(
    "census_clustering_seed", "Clustering field's seed", "dimensionless", Kind.SCALAR,
    "The 32-bit seed of the clustering field, folded once from the layer's seed on the noise's own path: with "
    "the model's five numbers for the field it makes the field evaluable at any point, by the model or a "
    "shader, as the lattice noise's committed vectors define it. The cloud census reads it to place each "
    "cloud's azimuth within its sector by the field. **Not shown by the viewer** (rule D4): a galaxy scalar of "
    "a layer stage, a key and no quantity; `/api/clouds`' header carries it with the field's numbers.",
)
CENSUS_CLUSTERING_CELL_MEAN = _decl(
    "census_clustering_cell_mean", "Clustering field's mean in a cell", "dimensionless", Kind.TABLE_COLUMN,
    "Each level-0 cell's mean of the clustering field's log-normal map over the cell's quadrature lattice, area "
    "weighted, one row a cell in the cells' order (ring by ring, sector by sector): what a renderer divides "
    "the field by to give the cell unit mean, so that the map it draws redistributes the cell's clouds and "
    "weighs nothing. Not near 1 - a cell spans a few dozen of the field's coarsest lattice cells. `/api/clouds`' "
    "header carries the window's cells' values for the viewer.",
    of="cell",
)
PUBLISHES = (CENSUS_CLUSTERING_SEED, CENSUS_CLUSTERING_CELL_MEAN)


def header(source: Any, constants: Mapping[str, Any], cells: Any) -> dict[str, Any]:
    """What ``/api/clouds``' header carries of the field for the viewer (rule D5 as amended: a function the viewer
    may evaluate, with every parameter the model's): its seed and form, the octave sum's three weights, and the
    mean of the map in each of ``cells`` (level-0 ids). With the layer off the seed and the means are None."""
    field = _compose.census_clustering(source, constants)
    fields = getattr(source, "fields", source)
    shape = ClusteringField(0, float(constants[CONSTANTS["scale"]]), int(constants[CONSTANTS["octaves"]]),
                            float(constants[CONSTANTS["slope"]]), float(constants[CONSTANTS["sigma"]]),
                            int(constants[CONSTANTS["points"]]))
    gain, top, norm = shape.weights()
    means = np.asarray(fields[CENSUS_CLUSTERING_CELL_MEAN.name], dtype=float)
    return {
        "seed": None if field is None else field.seed,
        "scale": shape.scale, "octaves": shape.octaves, "lacunarity": LACUNARITY, "slope": shape.slope,
        "sigma": shape.sigma, "gain": gain, "top": top, "norm": norm,
        "cells": [int(c) for c in cells],
        "cell_mean": None if field is None else [float(means[int(c)]) for c in cells],
    }


def compute_census_clustering(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants

    def draw() -> dict[str, Any]:
        field = ClusteringField.of(field_seed(int(ctx.seeds["texture_seed"])), c)
        return {"census_clustering_seed": float(field.seed), "census_clustering_cell_mean": field.cell_means(ctx.grid.R)}

    def neutral() -> dict[str, Any]:
        from galaxy.stages.systems import CELL_COUNT

        return {"census_clustering_seed": float("nan"), "census_clustering_cell_mean": np.full(CELL_COUNT, np.nan)}

    return _compose.realise(ctx.fields, draw, neutral)


CENSUS_CLUSTERING = IMPLEMENTATIONS.register(
    Stage(
        id="census_clustering", slot="census_clustering", checkpoint=5,
        about=(
            "The randomness layer's clustering of the censuses: a log-normal field of lattice noise in the plane, "
            "on the layer's own seed, coarsest at the hierarchy's largest measured scale and halving twice, by "
            "which each cloud's azimuth is drawn within its sector at its radius - so the clouds, and the clusters "
            "in them, gather into complexes below a cell's scale as the sources measure. Synthetic: it stands in "
            "for the gas's fragmentation, moves no cloud between sectors or rings and no total, and with the "
            "layer off realises nothing."
        ),
        compute=compute_census_clustering,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_constants=tuple(CONSTANTS.values()),
        publishes=PUBLISHES,
    )
)
