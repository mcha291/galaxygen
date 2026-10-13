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
statistic is the hierarchy's own excess over the structure - the slope of the ratio of the two branches of Grasha
et al. 2017a's correlation function (-0.64) at Menon et al. 2021's median largest hierarchical scale (190 pc), two
sources and not Grasha's ratio alone, which meets 1 at its own 112 pc break (item 2; ``_STATISTIC`` says what that
changes: 2.43 at 47.5 pc, not 1.73) - and its spectral slope and width are the two numbers measured to give it
(the constants' about lines say how). With the layer off there is no field: each cloud's azimuth is drawn
uniformly in its sector, as before S61.

**How it places** (item 4, as the lead amended it at S61 on the measurement). A cloud is placed **jointly in
radius and azimuth on its level-0 cell's lattice** (:meth:`ClusteringField.place`): each lattice point weighs the
census's radial law Sigma_H2(R) R times the gas pattern's point function (read on a 16 x 24 mesh across the cell,
bilinear between) times f; the cloud's point is the inverse of the cell's cumulative weights at its ``azimuth``
uniform, and it lies uniformly within the point - in radius at a ``position`` uniform, the ring stream's own array.
Placing the azimuth alone at the radius the ring drew was built first and measured: against the field-off control
the census read a slope of -0.18 (clouds, default galaxy) against the field's own -0.65, because each arc is
normalised alone and a radius through a clump gains no clouds; joint placement in a window of 190 pc about that
radius read -0.41, in the whole cell -0.63. **The radius the ring drew is kept** (``cloud_birth_radius``): every
per-cloud law reads it (the abundances, the clusters' efficiency) and every stage that bins clouds or clusters by
radius bins by it, so no per-ring or per-radius total moves with the placement. The ring's count, the sector
allocation and every other draw are part I's and untouched: **every cell's expected count and every ring's
realised total is what it was** - the field redistributes inside a cell only (rule 2). The clusters inherit it: one
per cloud, at its cloud's place plus the offset. With the layer off a cloud stands at the radius its ring drew,
uniform in its sector: the arithmetic before S61, bit for bit.

**What is published** (rule 5: evaluable at a point; no stored grid is the field). Two synthetic fields, each with
its three declarations: the field's 32-bit seed, the one number beside the model's constants that makes f
evaluable anywhere (``noise.fold_seed``: the fold is the model's, done once); and each level-0 cell's mean of the
map over the cell's quadrature lattice (``noise.cell_quadrature``, R dR dphi), the number a renderer divides f by
to give the cell unit mean, carried by ``/api/clouds``' header for the viewer (rule D5 as amended). With the layer
off both are NaN - an unrealised number is NaN (D164; D215's ruling 5 for a synthetic scalar), and the cell table
keeps its rows, which are the cells and are not drawn.

**Cost** (measured cold at S61, accepted for the session by the lead; debt #159). The placement evaluates the field on
every cell's lattice and the pattern on a 16 x 24 mesh per cell: materialising every cloud costs 3.8-4.5 s (the field
2.0 s, the pattern's meshes 1.1 s) against 1.0-1.1 s before; the whole-disc routes ``clouds`` 4.0 -> 9.6-10.3 s and
``clusters`` 5.3 -> 11.9 s cold, ``run()`` layer on 18.2-19.7 -> 23.1-23.6 s; one cell 0.05-0.07 s, unchanged. A
cached per-cell lattice or a coarser one is V7's. The cell-mean table: 1.2 s at two points per finest cell. The
``clouds`` stage alone, cold (the first time it runs in a fresh process, its upstream run first) - S61 (D220; the
review's finding 8): measured under the suite's load, least of five, 6.82 s layer on and 0.12 s off, against
``main`` at S60 under the same conditions 2.44 s and 0.17 s (2.8x layer on; the reviewer's loaded specs table read
1.93 -> 9.07 s). **The
mesh's error** beside its cost (S61, the review's finding 3; :data:`PATTERN_RADIAL_STEPS`' about has the whole
measurement): the pattern factor up to 32 % off at a lattice point (the bar's end, ring 5), but at most 3.4e-3 of a
cell's probability misplaced (the total-variation distance of its normalised weights; median 0), and none from
13.1 kpc outward.

**The young bright stars** (item 5). The bright catalogue places its stars of 20 to 40.71 Myr by the same field with
its octaves finer than a star's age allows dropped (:meth:`ClusteringField.maps`, ``noise.fractal_coarsest``: the
coarser octaves at the whole field's amplitudes), jointly in the star's level-0 cell on the same lattice: the lattice
is built once per cell and octave count (:meth:`ClusteringField.cell_lattices`, :class:`CellLattice`) and each star's
radial law multiplies its rows at the star's own draw. The clouds' placement is the same arithmetic it was
(:func:`mesh_factor` is its pattern reading, factored out unchanged).

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
# And the radial steps the cell's mesh of the pattern has (S61, D220 part II as amended): the pattern is read on a
# mesh of 16 x 24 steps per cell - 16 radial by 24 azimuthal intervals, so 17 x 25 nodes edge to edge, where the
# point function is evaluated (:func:`mesh_points`); every "16 x 24" in this package counts the steps - the nodes
# 59 pc apart in radius on the production grid, and bilinearly between them; the point function at every lattice
# point would cost about 15 s a run (6.6 s per million points, measured at S61). What it does not
# keep (measured at S61 on the default galaxy, layer on, against the point function at every placement lattice point
# of all 1 024 cells; the review's finding 3): the pattern factor is up to 32 % off at a point (ring 5, sector 18,
# 4.71-5.65 kpc, where the bar's end at 5.21 kpc kinks the blend), the worst cell's rms 3.2e-2 and the cells' mean
# rms 5.5e-4; what a draw sees, the total-variation distance of a cell's normalised weights, is at most 3.4e-3
# (ring 5, sector 2, the bar's other end; median 0) - the highest-contrast ridge cell (ring 2, sector 0, contrast
# 6.7) 1.2 % at most, TV 8e-4; the bar's reach (rings 0-4) 1.3-2.0 %, TV at most 1.2e-3; exact (0) in every cell
# from ring 14 (13.1 kpc) outward. ``tests/test_clouds.py`` holds the distance below 5e-3 on four of those cells.
PATTERN_RADIAL_STEPS = 16
# The constants of the model the field is made of, by role (G1's ruling 2b; galaxy/models/level0.py).
CONSTANTS: Mapping[str, str] = {
    "scale": "CENSUS_CLUSTERING_SCALE",
    "octaves": "CENSUS_CLUSTERING_OCTAVES",
    "slope": "CENSUS_CLUSTERING_SPECTRAL_SLOPE",
    "sigma": "CENSUS_CLUSTERING_WIDTH",
    "points": "CENSUS_CLUSTERING_POINTS",
}
# The lattice density of the published cell means (S61, the lead's ruling 5 on cost): read by this stage alone.
TABLE_POINTS = "CENSUS_CLUSTERING_TABLE_POINTS"


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

    def lattice(self, lo: float, hi: float, phi_lo: float, phi_hi: float, points: int | None = None) -> tuple[np.ndarray, np.ndarray]:
        """A level-0 cell's lattice, ``(R midpoints, phi midpoints)``: ``points`` (default the field's own) per finest
        lattice cell along the ring's radial extent and along the sector's outer arc, at least one each - the
        midpoint rule of ``noise.cell_quadrature``. The same lattice for a cell alone or in any set (D60)."""
        q = self.points if points is None else int(points)
        n_r = max(1, math.ceil(q * (float(hi) - float(lo)) * self.finest_frequency))
        n_phi = max(1, math.ceil(q * float(hi) * (float(phi_hi) - float(phi_lo)) * self.finest_frequency))
        r_mid = float(lo) + (np.arange(n_r) + 0.5) * (float(hi) - float(lo)) / n_r
        phi_mid = float(phi_lo) + (np.arange(n_phi) + 0.5) * (float(phi_hi) - float(phi_lo)) / n_phi
        return r_mid, phi_mid

    def place(
        self, u: np.ndarray, v: np.ndarray, cell: tuple[float, float, float, float], R: np.ndarray,
        sigma_h2: np.ndarray, pattern: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """``(radius, azimuth)`` of a cell's objects, drawn jointly on the cell's lattice (D220 part II item 4, as
        the lead amended it: the whole cell, measured at S61 against a window of one hierarchical scale about the
        ring's radius - -0.63 against -0.41).

        ``cell`` is ``(R_lo, R_hi, phi_lo, phi_hi)``. Each lattice point weighs Sigma_H2(R) R - the census's radial
        law, ``sigma_h2`` on the run's grid ``R``, linear between - times the pattern's point function, read on a
        mesh of 16 radial by 24 azimuthal steps across the cell and bilinear between (the census's own 24 steps
        across a sector, as ``pattern.azimuths`` reads it; a flat or absent pattern is 1), clipped at 0, times the
        field. The object's point is the inverse of the cell's cumulative weights, row by row, at its ``u``; it
        lies uniformly within the point's span - in azimuth by what of ``u`` is left inside the point, in radius
        at ``v``. Counted, never rejected (rule B8); a cell whose weights are all zero is drawn uniformly."""
        u, v = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
        if u.size == 0:
            return np.zeros(0), np.zeros(0)
        lo, hi, p_lo, p_hi = (float(x) for x in cell)
        r_mid, phi_mid = self.lattice(lo, hi, p_lo, p_hi)
        rr, pp = np.meshgrid(r_mid, phi_mid, indexing="ij")
        w = self.map(rr * np.cos(pp), rr * np.sin(pp)) * (np.interp(r_mid, R, sigma_h2) * r_mid)[:, None]
        law = mesh_factor(pattern, (lo, hi, p_lo, p_hi), r_mid, phi_mid)
        if law is not None:
            w = w * law
        flat = np.maximum(w, 0.0).ravel()
        if not float(flat.sum()) > 0.0:
            flat = np.ones_like(flat)
        cdf = np.cumsum(flat)
        target = u * cdf[-1]
        k = np.minimum(np.searchsorted(cdf, target, side="right"), flat.size - 1)
        below = np.where(k > 0, cdf[np.maximum(k - 1, 0)], 0.0)
        within = np.clip((target - below) / np.where(flat[k] > 0.0, flat[k], 1.0), 0.0, 1.0)
        row, col = np.divmod(k, phi_mid.size)
        d_r, d_phi = (hi - lo) / r_mid.size, (p_hi - p_lo) / phi_mid.size
        return lo + (row + v) * d_r, p_lo + (col + within) * d_phi

    def maps(self, x: np.ndarray, y: np.ndarray, kept: tuple[int, ...]) -> tuple[np.ndarray, ...]:
        """The field with only its ``n`` coarsest octaves, for each ``n`` of ``kept``, at face-on positions (kpc): the
        log-normal map of ``noise.fractal_coarsest``'s truncated sum - the finer octaves dropped, the kept ones at
        the whole field's amplitudes and the same sigma (S61, D220 part II item 5: a young star's finest structure has
        dispersed; the structure it was born in at the coarser scales stands as it was). ``n = octaves`` is
        :meth:`map`, bit for bit. A truncated map does not have the whole map's mean (its exponent's variance is the
        kept octaves' share): **a placement renormalises it on the lattice it draws on** - the inversion scales each
        object's uniform by the object's own total of the lattice's weights (:meth:`CellLattice.place`) - so no mean
        is ever read from it."""
        x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
        sums = _noise.fractal_coarsest(self.seed, np.stack([x, y], axis=-1), self.slope, self.octaves, kept,
                                       base_frequency=1.0 / self.scale, lacunarity=LACUNARITY)
        return tuple(_noise.lognormal_map(g, self.sigma) for g in sums)

    def octave_scales_pc(self) -> np.ndarray:
        """Each octave's lattice scale in pc, coarsest first: 190, 95 and 47.5 at the model's numbers."""
        return self.scale * 1000.0 / LACUNARITY ** np.arange(self.octaves)

    def cell_lattices(self, cell: tuple[float, float, float, float], law: Any, kept: tuple[int, ...],
                      mesh: np.ndarray | None = None) -> dict[int, "CellLattice"]:
        """One level-0 cell's lattice weights for each octave count of ``kept``, **without a radial law** (S61, D220
        part II item 5): each point weighs the field's ``n`` coarsest octaves (:meth:`maps`) times ``law`` - an
        azimuthal law read on the cell's 16 x 24 mesh and bilinear between, as :meth:`place` reads the gas pattern
        (:func:`mesh_factor`; None or flat is 1; or the law's ``mesh`` values given, :func:`bilinear`) - clipped at 0.
        The field is evaluated once for every ``n``. An
        object's radial law multiplies each lattice row's weight at the object's own draw
        (:meth:`CellLattice.place`): it is constant along a row, so the lattice is shared by every object of the
        cell and octave count whatever its radial law."""
        lo, hi, p_lo, p_hi = (float(x) for x in cell)
        r_mid, phi_mid = self.lattice(lo, hi, p_lo, p_hi)
        rr, pp = np.meshgrid(r_mid, phi_mid, indexing="ij")
        bounds = (lo, hi, p_lo, p_hi)
        factor = mesh_factor(law, bounds, r_mid, phi_mid) if mesh is None else bilinear(mesh, bounds, r_mid, phi_mid)
        out = {}
        for n, f in zip(kept, self.maps(rr * np.cos(pp), rr * np.sin(pp), kept)):
            w = f if factor is None else f * factor
            out[int(n)] = CellLattice.of((lo, hi, p_lo, p_hi), r_mid, phi_mid, np.maximum(w, 0.0))
        return out

    def cell_means(self, R: np.ndarray, points: int | None = None) -> np.ndarray:
        """Each level-0 cell's mean of :meth:`map` over its quadrature lattice, (rings * sectors,) ring-major as the
        cells are numbered: ``noise.cell_quadrature`` in (R, phi) with ``points`` per finest lattice cell along
        each axis (:meth:`lattice`; the table's own density, see the stage), each point weighted by R (the cell's
        area is R dR dphi). One over it is the cell's ``noise.lognormal_normaliser``."""
        from galaxy.stages.systems import CELL_RINGS, CELL_SECTORS, cell_edges

        rings, sectors = cell_edges(np.asarray(R, dtype=float))
        out = np.empty(CELL_RINGS * CELL_SECTORS)
        for r in range(CELL_RINGS):
            lo, hi = float(rings[r]), float(rings[r + 1])
            for s in range(CELL_SECTORS):
                r_mid, phi_mid = self.lattice(lo, hi, float(sectors[s]), float(sectors[s + 1]), points)
                q = _noise.cell_quadrature(lo, hi, float(sectors[s]), float(sectors[s + 1]), (r_mid.size, phi_mid.size))
                e = self.map(q[:, 0] * np.cos(q[:, 1]), q[:, 0] * np.sin(q[:, 1]))
                out[r * CELL_SECTORS + s] = float(np.sum(q[:, 0] * e) / np.sum(q[:, 0]))
        return out


def mesh_factor(law: Any, cell: tuple[float, float, float, float], r_mid: np.ndarray, phi_mid: np.ndarray) -> np.ndarray | None:
    """An azimuthal law at a cell's lattice points, ``(r_mid.size, phi_mid.size)``, or None where there is none (None,
    or a flat pattern): ``law.contrast(radii, azimuths)`` read on a mesh of ``PATTERN_RADIAL_STEPS`` by
    ``PATTERN_STEPS`` steps across the cell, clipped at 0, and bilinear between - the clouds' reading of the gas
    pattern (:meth:`ClusteringField.place`), shared with the bright catalogue's young stars (S61, D220 part II
    item 5)."""
    if law is None or law.flat:
        return None
    return bilinear(law.contrast(*mesh_points(cell)), cell, r_mid, phi_mid)


def mesh_points(cell: tuple[float, float, float, float]) -> tuple[np.ndarray, np.ndarray]:
    """The radii and azimuths of a cell's mesh, ``PATTERN_RADIAL_STEPS + 1`` by ``PATTERN_STEPS + 1``, edge to edge:
    where :func:`mesh_factor` reads a law."""
    lo, hi, p_lo, p_hi = (float(x) for x in cell)
    return np.linspace(lo, hi, PATTERN_RADIAL_STEPS + 1), np.linspace(p_lo, p_hi, PATTERN_STEPS + 1)


def bilinear(values: np.ndarray, cell: tuple[float, float, float, float], r_mid: np.ndarray, phi_mid: np.ndarray) -> np.ndarray:
    """A law's ``values`` on a cell's mesh (:func:`mesh_points`), clipped at 0 and read bilinearly at the cell's
    lattice points: :func:`mesh_factor`'s reading, for a caller that has the mesh's values already (the bright
    catalogue reads a level-0 ring's meshes in one call: S61, D220 part II item 5)."""
    lo, hi, p_lo, p_hi = (float(x) for x in cell)
    mesh = np.maximum(values, 0.0)
    ti = (r_mid - lo) / (hi - lo) * PATTERN_RADIAL_STEPS
    i = np.minimum(ti.astype(np.int64), PATTERN_RADIAL_STEPS - 1)
    a = ti - i
    tj = (phi_mid - p_lo) / (p_hi - p_lo) * PATTERN_STEPS
    j = np.minimum(tj.astype(np.int64), PATTERN_STEPS - 1)
    b = tj - j
    along_r = mesh[i] * (1.0 - a)[:, None] + mesh[i + 1] * a[:, None]
    return along_r[:, j] * (1.0 - b)[None, :] + along_r[:, j + 1] * b[None, :]


@dataclass(frozen=True)
class CellLattice:
    """One cell's lattice weights, shared by every object placed on it (S61, D220 part II item 5): the points'
    weights row-major, their running total, and each row's sum. Built once per (cell, octave count) and read by
    each object with its own radial law (:meth:`place`)."""

    cell: tuple[float, float, float, float]
    r_mid: np.ndarray
    phi_mid: np.ndarray
    weights: np.ndarray  # (n_r * n_phi,) row-major, >= 0
    cdf: np.ndarray  # their running total
    rows: np.ndarray  # (n_r,) each row's sum

    @classmethod
    def of(cls, cell: tuple[float, float, float, float], r_mid: np.ndarray, phi_mid: np.ndarray, w: np.ndarray) -> "CellLattice":
        flat = np.ascontiguousarray(w, dtype=float).ravel()
        return cls(cell, r_mid, phi_mid, flat, np.cumsum(flat), flat.reshape(r_mid.size, phi_mid.size).sum(axis=1))

    def place(self, radial: np.ndarray, u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """``(radius, azimuth)`` of objects whose weight at a lattice point is ``radial[object, row]`` times the
        lattice's weight there: the joint inverse CDF of :meth:`ClusteringField.place`, taken in two steps - the
        row by the rows' cumulative weights (``radial`` times each row's sum) at ``u``, then the point within the
        row by the row's own cumulative weights at what of ``u`` is left - which is the row-major inverse of the
        product exactly, the radial factor being constant along a row. **The renormalisation is the inversion's**:
        ``u`` is scaled by each object's own total, so the weights' mean - the field's, the law's - never enters.
        The object lies uniformly within its point: in azimuth by what of ``u`` is left inside the point, in radius
        at ``v``. Counted, never rejected (rule B8); an object whose weights are all zero is drawn uniformly in
        the cell."""
        u, v = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
        lo, hi, p_lo, p_hi = self.cell
        n_r, n_phi = self.r_mid.size, self.phi_mid.size
        if u.size == 0:
            return np.zeros(0), np.zeros(0)
        per_row = np.maximum(np.broadcast_to(np.asarray(radial, dtype=float), (u.size, n_r)), 0.0) * self.rows[None, :]
        running = np.cumsum(per_row, axis=1)
        total = running[:, -1]
        target = u * total
        row = np.minimum((running <= target[:, None]).sum(axis=1), n_r - 1)
        idx = np.arange(u.size)
        below = np.where(row > 0, running[idx, np.maximum(row - 1, 0)], 0.0)
        width = per_row[idx, row]
        left = np.clip((target - below) / np.where(width > 0.0, width, 1.0), 0.0, 1.0)
        start = row * n_phi
        base = np.where(start > 0, self.cdf[np.maximum(start - 1, 0)], 0.0)
        aim = base + left * self.rows[row]
        k = np.clip(np.searchsorted(self.cdf, aim, side="right"), start, start + n_phi - 1)
        under = np.where(k > start, self.cdf[np.maximum(k - 1, 0)], base)
        within = np.clip((aim - under) / np.where(self.weights[k] > 0.0, self.weights[k], 1.0), 0.0, 1.0)
        col = k - start
        d_r, d_phi = (hi - lo) / n_r, (p_hi - p_lo) / n_phi
        radius, azimuth = lo + (row + v) * d_r, p_lo + (col + within) * d_phi
        empty = ~(total > 0.0)
        if empty.any():
            radius[empty], azimuth[empty] = lo + v[empty] * (hi - lo), p_lo + u[empty] * (p_hi - p_lo)
        return radius, azimuth


# --- declarations ----------------------------------------------------------------------------------

_STANDS_IN_FOR = (
    "The hierarchical fragmentation of the gas below a cell's scale - where inside a ring's sector the turbulent, "
    "self-gravitating gas gathers into complexes, clouds and their clusters - which the model does not compute "
    "(a level-C simulation would: RESEARCH_AREAS section 1). Nothing the arms, the bar or the disc's profile "
    "already give: the field's own correlation is the hierarchy's excess over that structure."
)
# The spill's cost to the abundances, as measured at S61 on the default galaxy, layer on (the review's finding 1;
# ``tests/test_clustering_gate.py`` holds the measurement to these numbers): |[Fe/H]_gas at the placed radius minus
# at the radius the ring drew|, dex, over the 16 577 clouds - its median, 90th and 99th percentiles and maximum; the
# ring's radius of the maximum (kpc); the clouds beyond 0.06 dex; and the [alpha/Fe] maximum, likewise.
SPILL_FEH_DEX = {"median": 0.022, "p90": 0.063, "p99": 0.123, "max": 1.258}
SPILL_FEH_MAX_AT_KPC = 23.6
SPILL_FEH_BEYOND = (0.06, 1862, 16577)
SPILL_ALPHA_MAX_DEX = 0.232

_CONSERVES = (
    "Every cell's expected count of every census it places and every ring's realised total: it places a cloud "
    "inside the cloud's own cell after the ring's count, the sector allocation and every other draw are made, so "
    "no count, mass or light moves between cells or rings; every per-cloud law and every binner reads the radius "
    "the ring drew (`cloud_birth_radius`, `cluster_birth_radius`), so nothing published per ring or per radius "
    "moves either. It does not keep where a cloud sits in its cell: a cloud's placed radius lies anywhere in its "
    "level-0 ring (0.94 kpc wide on the production grid) and up to that from the radius its ring drew - measured "
    "at S61 on the default galaxy, a median 275 pc and at most 976 pc - while the cloud's abundances and its "
    "cluster's efficiency are read at the radius the ring drew. Measured at S61 (the default galaxy, layer on): "
    f"the gas's [Fe/H] at the placed radius differs from that at the ring's by a median {SPILL_FEH_DEX['median']} "
    f"dex, {SPILL_FEH_DEX['p90']} at the 90th percentile and {SPILL_FEH_DEX['p99']} at the 99th, at most "
    f"{SPILL_FEH_DEX['max']} dex - a cloud the ring drew at {SPILL_FEH_MAX_AT_KPC} kpc, where the gas's [Fe/H] falls "
    "from -1.23 to -2.92 dex between 23 and 24 kpc (6.4 dex/kpc, against a ring 0.94 kpc wide); at most 0.335 dex "
    f"inside 5 kpc and 0.149 in 10-15 kpc; {SPILL_FEH_BEYOND[1]} of {SPILL_FEH_BEYOND[2]} clouds (11 %) more than "
    f"{SPILL_FEH_BEYOND[0]} dex apart; [alpha/Fe] at most {SPILL_ALPHA_MAX_DEX} apart. And its "
    "placed azimuth lies anywhere in its sector. Nor does it keep the field's own mean in a cell at 1: a cell's mean "
    "of the map runs from 0.264 to 2.402 over all 1 024 cells (measured at S61 on the default galaxy; the review's "
    "finding 6 - 0.44-1.93 was a 40-cell sample) - the published cell mean is what divides it out, taken on the "
    "table's 2-point lattice: on the 4-point placement lattice the map divided by it has a mean off from 1 by 5.70e-3 rms "
    "and 3.43e-2 at worst."
)
_STATISTIC = (
    "1 + omega_f(r) = (r / 190 pc)^-0.64 for r < 190 pc and 1 beyond: the inner branch -0.85 +- 0.03 over the "
    "outer -0.21 +- 0.02 of the correlation function of clusters up to 40 Myr, classes 1-3, the pair-weighted "
    "average of six galaxies, meeting at 112 pc [verified: Grasha et al. 2017a, ApJ 840, 113, Table 4; "
    "docs/READING_CLUSTERING.md 1.2] - the six galaxies' inner slopes run -0.4 to -1.7 one by one; the scale "
    "190 pc is the median of the five largest hierarchical scales measured in Menon et al. 2021 Table 3 "
    "(101-845 pc; READING_CLUSTERING.md 1.3), bracketed by that 112 pc break and NGC 628's 210-300 pc (Lapeer "
    "et al. 2026; 1.5). **Two sources, not one ratio**: the slope -0.64 is Grasha et al. 2017a's two branches' "
    "ratio, the scale 190 pc Menon et al. 2021's median largest hierarchical scale - so the excess at 47.5 pc is "
    "(47.5/190)^-0.64 = 2.43, where Grasha's ratio alone, meeting at its own 112 pc break, would give "
    "(47.5/112)^-0.64 = 1.73 (29 % lower; 2.43 is 40 % above it); the lead's choice (D220 part II item 2). "
    "As realised by the field alone in a flat footprint (S61): slope -0.646 +- 0.010 over 47.5-190 pc, 2.45 at 47.5 pc, 0.99-1.00 beyond 380 pc (48 noise seeds). (DECISIONS.md D220 part II item 2.)"
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
    "cloud jointly in radius and azimuth on its level-0 cell's lattice by the field (D220 part II item 4 as "
    "amended; the radius the ring drew is kept as `cloud_birth_radius`), and the bright catalogue its stars of 20 to 40.7 Myr, with the octaves "
    "finer than a star's age allows dropped (D220 part II item 5). **Not shown by the viewer** (rule D4): a galaxy scalar of "
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
        "sigma": shape.sigma, "gain": gain, "top": top, "norm": norm, "table_points": int(constants[TABLE_POINTS]),
        "cells": [int(c) for c in cells],
        "cell_mean": None if field is None else [float(means[int(c)]) for c in cells],
    }


def compute_census_clustering(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants

    def draw() -> dict[str, Any]:
        field = ClusteringField.of(field_seed(int(ctx.seeds["texture_seed"])), c)
        return {"census_clustering_seed": float(field.seed), "census_clustering_cell_mean": field.cell_means(ctx.grid.R, int(c[TABLE_POINTS]))}

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
            "which each cloud is placed jointly in radius and azimuth on its level-0 cell's lattice (with the "
            "molecular law and the gas pattern), its ring's radius kept for every law that reads one - so the "
            "clouds, and the clusters in them, gather into complexes below a cell's scale as the sources measure; and by which the bright "
            "catalogue's young stars stand near where they formed, losing its finer octaves as they age. "
            "Synthetic: it stands in "
            "for the gas's fragmentation, moves no cloud between sectors or rings and no total, and with the "
            "layer off realises nothing."
        ),
        compute=compute_census_clustering,
        layer_stage=True,
        reads_seeds=("texture_seed",),
        reads_constants=(*CONSTANTS.values(), TABLE_POINTS),
        publishes=PUBLISHES,
    )
)
