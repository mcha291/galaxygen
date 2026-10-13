"""clustering: the two-point correlation function of a census, measured as the sources measure it (S61, D220).

An instrument (rule B1: built and tested before the thing it certifies). It reads a catalogue as published - each
object's face-on position, ``x = R cos phi``, ``y = R sin phi`` with R in pc - and nothing of how the census was
drawn, so it measures any census in any state of the model.

**The estimator** is Landy & Szalay 1993's::

    1 + omega(r) = 1 + (DD - 2 DR + RR) / RR

where DD, DR and RR are the pair counts in a separation bin among the data, between the data and a comparison
catalogue, and among the comparison catalogue, **each normalised by its number of pairs**: ``n_d (n_d - 1) / 2``,
``n_d n_r`` and ``n_r (n_r - 1) / 2``. A pair is counted once (i < j for the auto counts).

**The footprint and the randoms** (the sources' convention as read in ``READING_CLUSTERING.md``: Grasha et al. 2015
and 2017a, Menon et al. 2021, Turner et al. 2022 - Landy-Szalay against a random catalogue uniform in the
instrument's footprint). Two footprints: :class:`Annulus` (``R_in <= R <= R_out``; for a census the radial range of
its cells with a positive expectation) and :class:`Square` (a pointing, as a LEGUS or PHANGS field is; the probe
uses a 6 kpc side centred on the x axis at the solar radius). The randoms are uniform **in area** inside the
footprint - in the annulus ``R = sqrt(U (R_out^2 - R_in^2) + R_in^2)`` and ``phi`` uniform - drawn from a fixed
seed, a multiple of the data count. Data outside the footprint are dropped before counting.

**What each comparison measures.** Against uniform randoms the correlation contains everything that makes the
census non-uniform in its footprint: the disc's radial profile, the arms, the bar, and whatever small-scale
clustering the census has - the quantity every source read prints, none with a smooth disc divided out.
:func:`against_control` replaces the randoms by a **control catalogue** the caller passes (He et al. 2026's
"control following the kpc-scale structure", as read in ``READING_CLUSTERING.md``, item 7 [FQ]); when the control
is the census's own law realised again independently (the same census under other values of the seed that draws
it), the ratio measures only what the census has **beyond** its own expected placement: 1 at every scale for a
census whose objects are drawn independently from that law.

**The bins**: 20 logarithmic bins from 30 pc to 5 kpc (:data:`EDGES_PC`); a bin's centre is the geometric mean of its
edges. **The fit** (:func:`fit_power_law`): ``1 + omega = A (r / 300 pc)^alpha`` by unweighted least squares on
``log10(1 + omega)`` against ``log10(r / 300 pc)`` over the bins whose centres lie in a range, using only bins with
``DD > 0`` and ``1 + omega > 0``; ``A`` is the law's ``1 + omega`` at 300 pc (Turner et al. 2022's amplitude, as
read). The ranges the reading names: [100 pc, 2 kpc] (the default here), [40 pc, 800 pc] (Grasha et al. 2018's for
NGC 7793) and [100 pc, 3 kpc] (Grasha et al. 2019's for M 51). :func:`fit_broken` fits two such laws either side
of a break chosen by the least total squared error (Grasha 2015/2017a's "PW" form, as read), the break a bin edge.

**Cost.** Pairs are counted on a grid hash with cells half the largest edge wide: each occupied cell against the
5 x 5 around it, in blocks of at most ``BLOCK`` float32 distances binned by ``numpy.histogram`` on the squared edges.
The cost grows as the number of pairs closer than about 1.8 times the largest edge, so the randoms' auto count RR
is the expensive one: :meth:`Comparison.auto` sums it over disjoint slices of the randoms of at most ``RR_SPLIT``
points, normalised by the pairs it was counted over (each slice is a draw from the same uniform law, so the
normalised RR has the full catalogue's expectation, with less precision than all pairs would give but more than
DD's while a slice is larger than the data); a :class:`Comparison` holds RR once for every census measured in the
same footprint. DR uses every random.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

EDGES_PC = np.geomspace(30.0, 5000.0, 21)  # 20 logarithmic bins from 30 pc to 5 kpc
PIVOT_PC = 300.0  # the fit's amplitude is 1 + omega here
FIT_RANGES_PC: dict[str, tuple[float, float]] = {
    "default": (100.0, 2000.0),
    "grasha2018": (40.0, 800.0),
    "grasha2019": (100.0, 3000.0),
}
BLOCK = 4_000_000  # distances computed in one numpy block
RR_SPLIT = 50_000  # the randoms' auto count is summed over disjoint slices of at most this many (Comparison.auto)


def centres(edges: np.ndarray = EDGES_PC) -> np.ndarray:
    """The geometric centre of each bin."""
    return np.sqrt(edges[:-1] * edges[1:])


def positions_pc(radius_kpc: np.ndarray, azimuth_rad: np.ndarray) -> np.ndarray:
    """(n, 2) face-on positions in pc from a catalogue's galactocentric radius (kpc) and azimuth (rad)."""
    r = np.asarray(radius_kpc, dtype=float) * 1000.0
    p = np.asarray(azimuth_rad, dtype=float)
    return np.column_stack([r * np.cos(p), r * np.sin(p)])


# --- footprints ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Annulus:
    r_in_pc: float
    r_out_pc: float

    def contains(self, xy: np.ndarray) -> np.ndarray:
        r2 = np.einsum("ij,ij->i", xy, xy)
        return (r2 >= self.r_in_pc**2) & (r2 <= self.r_out_pc**2)

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        u, v = rng.random(n), rng.random(n)
        r = np.sqrt(u * (self.r_out_pc**2 - self.r_in_pc**2) + self.r_in_pc**2)
        p = 2.0 * math.pi * v
        return np.column_stack([r * np.cos(p), r * np.sin(p)])

    @property
    def area_pc2(self) -> float:
        return math.pi * (self.r_out_pc**2 - self.r_in_pc**2)

    def describe(self) -> str:
        return f"annulus {self.r_in_pc / 1000:.3f}-{self.r_out_pc / 1000:.3f} kpc"


@dataclass(frozen=True)
class Square:
    x0_pc: float
    y0_pc: float
    side_pc: float

    def contains(self, xy: np.ndarray) -> np.ndarray:
        h = 0.5 * self.side_pc
        return (np.abs(xy[:, 0] - self.x0_pc) <= h) & (np.abs(xy[:, 1] - self.y0_pc) <= h)

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        h = 0.5 * self.side_pc
        return np.column_stack([self.x0_pc + rng.uniform(-h, h, n), self.y0_pc + rng.uniform(-h, h, n)])

    @property
    def area_pc2(self) -> float:
        return self.side_pc**2

    def describe(self) -> str:
        return f"square {self.side_pc / 1000:g} kpc at ({self.x0_pc / 1000:g}, {self.y0_pc / 1000:g}) kpc"


def solar_pointing(r_sun_kpc: float, side_pc: float = 6000.0) -> Square:
    """A LEGUS/PHANGS-like pointing: a square of ``side_pc`` centred on the x axis at the solar radius."""
    return Square(float(r_sun_kpc) * 1000.0, 0.0, float(side_pc))


# --- pair counts --------------------------------------------------------------------------------------------


REACH = 2  # grid cells are the largest edge over REACH wide; a cell meets the (2 REACH + 1)^2 around it


def _cells(xy: np.ndarray, h: float) -> tuple[np.ndarray, dict[tuple[int, int], tuple[int, int]]]:
    """Points sorted by grid cell of side h, as float32 offsets from their common origin: (sorted points,
    {cell: (start, stop)})."""
    ij = np.floor(xy / h).astype(np.int64)
    key = ij[:, 0] * 1_000_003 + ij[:, 1]
    order = np.argsort(key, kind="stable")
    key_s = key[order]
    starts = np.flatnonzero(np.r_[True, key_s[1:] != key_s[:-1]])
    stops = np.r_[starts[1:], key_s.size]
    ij_s = ij[order]
    table = {(int(ij_s[s, 0]), int(ij_s[s, 1])): (int(s), int(e)) for s, e in zip(starts, stops)}
    return xy[order].astype(np.float32), table


def _block_counts(a: np.ndarray, b: np.ndarray, edges2: np.ndarray) -> np.ndarray:
    """Pairs (one from a, one from b) per bin of squared separation, in blocks of at most BLOCK distances
    (float32 differences: a separation's relative error ~1e-7 at 20 kpc offsets, far inside a bin)."""
    nb = edges2.size - 1
    out = np.zeros(nb, dtype=np.int64)
    if not a.size or not b.size:
        return out
    rows = max(1, BLOCK // max(1, b.shape[0]))
    for s in range(0, a.shape[0], rows):
        aa = a[s:s + rows]
        d2 = (aa[:, 0, None] - b[None, :, 0]) ** 2 + (aa[:, 1, None] - b[None, :, 1]) ** 2
        out += np.histogram(d2.ravel(), bins=edges2)[0]
    return out


def pair_counts(a: np.ndarray, b: np.ndarray | None = None, edges: np.ndarray = EDGES_PC) -> np.ndarray:
    """Raw pair counts per separation bin: among ``a`` (each unordered pair once) when ``b`` is None, else between
    ``a`` and ``b``. A pair at separation s falls in bin k when ``edges[k] <= s < edges[k + 1]`` (the last bin also
    holds s equal to the largest edge: numpy's histogram)."""
    edges = np.asarray(edges, dtype=float)
    edges2 = edges**2
    h = float(edges[-1]) / REACH
    nb = edges.size - 1
    out = np.zeros(nb, dtype=np.int64)
    a = np.asarray(a, dtype=float).reshape(-1, 2)
    around = [(di, dj) for di in range(-REACH, REACH + 1) for dj in range(-REACH, REACH + 1)]
    if b is None:
        pts, table = _cells(a, h)
        forward = [(di, dj) for di, dj in around if di > 0 or (di == 0 and dj > 0)]
        for (i, j), (s, e) in table.items():
            own = pts[s:e]
            # The cell with itself: every ordered pair once, so halved; the diagonal (separation 0) is below the
            # first edge, as is any duplicate position.
            out += _block_counts(own, own, edges2) // 2
            for di, dj in forward:
                other = table.get((i + di, j + dj))
                if other is not None:
                    out += _block_counts(own, pts[other[0]:other[1]], edges2)
        return out
    b = np.asarray(b, dtype=float).reshape(-1, 2)
    pts_b, table_b = _cells(b, h)
    pts_a, table_a = _cells(a, h)
    for (i, j), (s, e) in table_a.items():
        own = pts_a[s:e]
        for di, dj in around:
            other = table_b.get((i + di, j + dj))
            if other is not None:
                out += _block_counts(own, pts_b[other[0]:other[1]], edges2)
    return out


# --- the estimator ------------------------------------------------------------------------------------------


@dataclass
class Comparison:
    """A comparison catalogue in a footprint - uniform randoms, or a control - with its auto counts computed once."""

    points: np.ndarray
    footprint: Annulus | Square
    edges: np.ndarray = field(default_factory=lambda: EDGES_PC.copy())
    split: int | None = RR_SPLIT
    rr: np.ndarray | None = None
    rr_pairs: float = 0.0  # the number of pairs RR was counted over: its normaliser
    seconds_rr: float = 0.0

    @classmethod
    def uniform(cls, footprint: Annulus | Square, n: int, seed: int, edges: np.ndarray = EDGES_PC,
                split: int | None = RR_SPLIT) -> "Comparison":
        return cls(footprint.sample(int(n), np.random.default_rng(int(seed))), footprint, np.asarray(edges, dtype=float),
                   split)

    @classmethod
    def control(cls, points: np.ndarray, footprint: Annulus | Square, edges: np.ndarray = EDGES_PC,
                split: int | None = RR_SPLIT) -> "Comparison":
        pts = np.asarray(points, dtype=float).reshape(-1, 2)
        return cls(pts[footprint.contains(pts)], footprint, np.asarray(edges, dtype=float), split)

    def auto(self) -> np.ndarray:
        """RR: the auto pair counts, summed over disjoint consecutive slices of at most ``split`` points (all of them
        at once when ``split`` is None), with :attr:`rr_pairs` the pairs counted over. Each slice of an iid catalogue
        is itself a draw from the same law, so the normalised count has the full catalogue's expectation; the cost
        falls by the number of slices, and its noise stays below DD's while a slice holds more points than the
        data (the probe reports the slice size beside every number)."""
        if self.rr is None:
            import time

            t0 = time.perf_counter()
            n = self.points.shape[0]
            step = n if not self.split else int(self.split)
            rr = np.zeros(self.edges.size - 1, dtype=np.int64)
            pairs = 0.0
            for s in range(0, n, max(step, 1)):
                part = self.points[s:s + step]
                rr += pair_counts(part, None, self.edges)
                pairs += part.shape[0] * (part.shape[0] - 1) / 2.0
            self.rr, self.rr_pairs = rr, pairs
            self.seconds_rr = time.perf_counter() - t0
        return self.rr


@dataclass
class Correlation:
    """One measurement: the bins, 1 + omega, the raw counts, the sizes and what it cost."""

    edges: np.ndarray
    one_plus_omega: np.ndarray
    dd: np.ndarray
    dr: np.ndarray
    rr: np.ndarray
    n_data: int
    n_random: int
    dropped: int  # data outside the footprint
    footprint: str
    seconds: float
    rr_split: int | None = None  # the slice size RR was summed over (None: all randoms at once)

    @property
    def r(self) -> np.ndarray:
        return centres(self.edges)

    @property
    def poisson_error(self) -> np.ndarray:
        """(1 + omega) / sqrt(DD): the Poisson error of a bin (inf where DD = 0)."""
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(self.dd > 0, np.abs(self.one_plus_omega) / np.sqrt(np.maximum(self.dd, 1)), np.inf)

    def at(self, r_pc: float) -> float:
        """1 + omega in the bin holding ``r_pc``."""
        k = int(np.clip(np.searchsorted(self.edges, r_pc, side="right") - 1, 0, self.edges.size - 2))
        return float(self.one_plus_omega[k])


def landy_szalay(data: np.ndarray, comparison: Comparison) -> Correlation:
    """1 + omega of ``data`` (n, 2 positions in pc) against a :class:`Comparison` in its footprint (Landy & Szalay
    1993), each pair count normalised by its number of pairs."""
    import time

    t0 = time.perf_counter()
    xy = np.asarray(data, dtype=float).reshape(-1, 2)
    inside = comparison.footprint.contains(xy)
    d = xy[inside]
    r = comparison.points
    nd, nr = d.shape[0], r.shape[0]
    rr = comparison.auto()
    dd = pair_counts(d, None, comparison.edges)
    dr = pair_counts(d, r, comparison.edges)
    with np.errstate(divide="ignore", invalid="ignore"):
        ddn = dd / (nd * (nd - 1) / 2.0)
        drn = dr / (nd * float(nr))
        rrn = rr / comparison.rr_pairs
        opo = 1.0 + (ddn - 2.0 * drn + rrn) / rrn
    return Correlation(comparison.edges, opo, dd, dr, rr, nd, nr, int((~inside).sum()), comparison.footprint.describe(),
                       time.perf_counter() - t0, comparison.split if comparison.split and comparison.split < nr else None)


def against_uniform(data: np.ndarray, footprint: Annulus | Square, multiple: float = 10.0, seed: int = 61) -> Correlation:
    """The sources' convention: Landy-Szalay against randoms uniform in the footprint, ``multiple`` times the data
    inside it, from ``seed``."""
    xy = np.asarray(data, dtype=float).reshape(-1, 2)
    n = int(round(multiple * int(footprint.contains(xy).sum())))
    return landy_szalay(xy, Comparison.uniform(footprint, n, seed))


def against_control(data: np.ndarray, control: np.ndarray, footprint: Annulus | Square) -> Correlation:
    """Landy-Szalay with the randoms replaced by a control catalogue (positions in pc), cut to the footprint: what
    the data hold beyond the control's own placement (He et al. 2026's construction, as read)."""
    return landy_szalay(data, Comparison.control(control, footprint))


# --- the fits -----------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PowerLaw:
    alpha: float
    amplitude: float  # 1 + omega of the law at PIVOT_PC
    scatter_dex: float  # rms residual of log10(1 + omega) about the law
    alpha_error: float  # the ordinary least-squares standard error of the slope
    bins: int
    lo_pc: float
    hi_pc: float


def _usable(corr: Correlation, lo: float, hi: float) -> np.ndarray:
    r = corr.r
    return (r >= lo) & (r <= hi) & (corr.dd > 0) & (corr.one_plus_omega > 0) & np.isfinite(corr.one_plus_omega)


def _line(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """(slope, intercept, rms residual, slope standard error) of y on x by ordinary least squares."""
    n = x.size
    xm, ym = x.mean(), y.mean()
    sxx = float(((x - xm) ** 2).sum())
    slope = float(((x - xm) * (y - ym)).sum() / sxx) if sxx > 0 else float("nan")
    icpt = float(ym - slope * xm)
    res = y - (icpt + slope * x)
    rms = float(np.sqrt((res**2).mean()))
    err = float(np.sqrt((res**2).sum() / (n - 2) / sxx)) if n > 2 and sxx > 0 else float("nan")
    return slope, icpt, rms, err


def fit_power_law(corr: Correlation, lo_pc: float = 100.0, hi_pc: float = 2000.0) -> PowerLaw:
    """``1 + omega = A (r / 300 pc)^alpha`` by least squares in log-log over the bins centred in [lo, hi] with
    DD > 0 and 1 + omega > 0. NaNs when fewer than two bins qualify."""
    m = _usable(corr, lo_pc, hi_pc)
    if m.sum() < 2:
        return PowerLaw(float("nan"), float("nan"), float("nan"), float("nan"), int(m.sum()), lo_pc, hi_pc)
    x = np.log10(corr.r[m] / PIVOT_PC)
    y = np.log10(corr.one_plus_omega[m])
    slope, icpt, rms, err = _line(x, y)
    return PowerLaw(slope, 10.0**icpt, rms, err, int(m.sum()), lo_pc, hi_pc)


@dataclass(frozen=True)
class BrokenLaw:
    inner: PowerLaw
    outer: PowerLaw
    break_pc: float
    sse: float


def fit_broken(corr: Correlation, lo_pc: float = 30.0, hi_pc: float = 3000.0, min_bins: int = 3) -> BrokenLaw | None:
    """Two power laws either side of a break at a bin edge, the break chosen by the least total squared error in
    log10(1 + omega); each side at least ``min_bins`` usable bins. None when no break qualifies."""
    m = _usable(corr, lo_pc, hi_pc)
    idx = np.flatnonzero(m)
    best: BrokenLaw | None = None
    for k in range(min_bins, idx.size - min_bins + 1):
        inner_i, outer_i = idx[:k], idx[k:]
        edge = float(corr.edges[outer_i[0]])
        sse = 0.0
        laws = []
        for sel in (inner_i, outer_i):
            x = np.log10(corr.r[sel] / PIVOT_PC)
            y = np.log10(corr.one_plus_omega[sel])
            slope, icpt, rms, err = _line(x, y)
            sse += float(rms**2 * sel.size)
            laws.append(PowerLaw(slope, 10.0**icpt, rms, err, int(sel.size), float(corr.r[sel[0]]), float(corr.r[sel[-1]])))
        if best is None or sse < best.sse:
            best = BrokenLaw(laws[0], laws[1], edge, sse)
    return best
