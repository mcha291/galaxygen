"""BUILD_III Phase L1's gate on the finished census (S61, DECISIONS.md D220 part II item 7 a-b and e, as the lead
amended item 4): the clouds and the clusters measured by the clustering instrument (``galaxy.specs.clustering``);
and item 7c, the bright catalogue's young stars by age bin (item 5: the field's octaves dropped as a star ages), at
the end of the file.

**What is judged** (item 7 a-b): against a control, the census's correlation over the field's own range - the
fitted slope over [47.5, 190] pc within 0.15 of -0.64, and 1 + omega within 0.05 of 1 in every bin beyond 380 pc.
**The control** is the census's own law realised again: the same census materialised from the run's fields under
four other systems seeds, pooled, with the layer on and **the clustering field's width set to 0** - the radial
law and the gas pattern place the control's clouds, the field does not (the lead's ruling 2 at S61). The literal
"same census, other seeds" control reads 1 at every scale (measured at S61: slope +0.02 for the clouds, +0.04 for
the clusters), because the field is the layer's realisation on ``texture_seed``, not on the systems seed: data and
control would share the same clumps, and the ratio would measure nothing.

**What is disclosed and not judged** (item 7 e, item 1): the 6 kpc square at R_SUN against uniform randoms - the
sources' own convention, whose number is the footprint's structure as much as the census's (D220 part II item 1).
Recorded here as measured, beside the S60 census's numbers before the field (``docs/S61_PROBE.md``) and the
sources' (``READING_CLUSTERING.md``, "What a model could adopt": clusters up to 10 Myr 3.4 at 300 pc, PHANGS
medians; clouds about 2.2).

**The field's own statistic**, cheaply: the default galaxy's field alone in a flat 6.08 kpc square - its exact
two-point expectation by FFT (what the constants were derived from, with 48 seeds), and points drawn by it measured
by the instrument against uniform randoms. One square's slope scatters by 0.068 between seeds, so the square's own
number is pinned as measured and held to the gate's window.

The templates are measured by hand (each about a minute and a half more) and recorded below as measured: against the
same control, slope over [47.5, 190] pc, the default galaxy's clouds -0.636 +- 0.046 and clusters -0.670 +- 0.057;
milky_way's -0.619 +- 0.048 and -0.639 +- 0.059; ngc_4414's -0.524 +- 0.087 and -0.594 +- 0.092 - the clouds of
ngc_4414 nearest the window's edge (-0.49), within it, on a third of the default's clouds (6 530).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.layer.census_clustering import ClusteringField, field_seed
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs import clustering as C
from galaxy.stages import clouds as CL
from galaxy.stages import bright as BR
from galaxy.stages import clusters as CU

TARGET_SLOPE = -0.64  # (r / 190 pc)^-0.64 below 190 pc: Grasha et al. 2017a Table 4's two branches' ratio (D220 II item 2)
SLOPE_WINDOW = 0.15  # D220 part II item 7: within 0.15
FLAT_WITHIN = 0.05  # and 1 + omega within 0.05 of 1 beyond 2 l
FIT_PC = (47.5, 190.0)  # the field's finest scale to its coarsest
BEYOND_PC = 380.0
CONTROL_SEEDS = 4
WIDTH = "CENSUS_CLUSTERING_WIDTH"

# As measured at S61 on the finished census (default galaxy, layer on; slope / law at 47.5 pc / worst bin beyond 380 pc).
MEASURED = {
    "clouds": (-0.636, 1.977, 0.0216),
    "clusters": (-0.670, 2.097, 0.0210),
}
# The templates, measured by hand with this file's construction at S61 (each run about 30 s, its control 10-20 s):
# as measured, not run here. Every one inside the judged window; ngc_4414 holds a third of the clouds, so its
# slopes carry 0.09 of least-squares error. Beside them the disclosed square (slope, A at 300 pc, 1 + omega at 100
# and 300 pc): milky_way clouds -0.187 / 1.25 / 1.83 / 1.16, clusters <= 10 Myr -0.161 / 1.27 / 2.32 / 1.16;
# ngc_4414 clouds -0.182 / 1.23 / 3.04 / 1.09 (173 clouds), clusters <= 10 Myr +0.222 / 0.72 / 2.04 / 0.64 (62).
TEMPLATES_MEASURED = {
    "milky_way": {"clouds": (-0.619, 1.955, 0.0280), "clusters": (-0.639, 2.058, 0.0298)},
    "ngc_4414": {"clouds": (-0.524, 1.789, 0.0276), "clusters": (-0.594, 1.962, 0.0311)},
}
assert all(abs(v[0] - (-0.64)) < 0.15 and v[2] < 0.05 for t in TEMPLATES_MEASURED.values() for v in t.values())
# The disclosed check: the 6 kpc square at R_SUN against uniform randoms - slope over [100, 2000] pc, the law's A at
# 300 pc, and 1 + omega in the bins holding 100 and 300 pc. Before: the S60 census (docs/S61_PROBE.md, default galaxy,
# layer on). After: as measured at S61 with the field. Not judged (D220 part II item 1).
SQUARE_BEFORE = {"clouds": (-0.096, 1.17, 1.18, 1.17), "clusters<=10Myr": (-0.108, 1.18, 1.46, 1.10)}
SQUARE_AFTER = {"clouds": (-0.163, 1.24, 2.01, 1.16), "clusters<=10Myr": (-0.141, 1.30, 1.60, 1.24)}
# The default galaxy's field alone in a flat 6.08 kpc square (exact expectation; points through the instrument).
FIELD_ALONE = {"exact": (-0.613, 2.324), "points": (-0.621,)}  # as measured at S61; the 48-seed mean is -0.646


def _constants(m) -> dict[str, float]:
    return {k: v.value for k, v in m.constants.items()}


@pytest.fixture(scope="module")
def census():
    models, _, _ = production()
    m = models.get(DEFAULT_MODEL)
    c = _constants(m)
    out = run(m)
    F, R = out.fields, out.grid.R
    seed, tex = int(out.inputs["systems_seed"]), int(out.inputs["texture_seed"])
    law = dict(c, **{WIDTH: 0.0})  # the census's own law: the pattern and the radial law, no field
    ctl_clouds, ctl_clusters = [], []
    for s in range(seed + 1, seed + 1 + CONTROL_SEEDS):
        clouds = CL.materialise_clouds(F, R, s, law, texture_seed=tex)
        clusters = CU.materialise_clusters(clouds, F, R, s, law)
        ctl_clouds.append(C.positions_pc(clouds["cloud_radius"], clouds["cloud_azimuth"]))
        ctl_clusters.append(C.positions_pc(clusters["cluster_radius"], clusters["cluster_azimuth"]))
    return {
        "out": out, "c": c,
        "data": {"clouds": C.positions_pc(F["cloud_radius"], F["cloud_azimuth"]),
                 "clusters": C.positions_pc(F["cluster_radius"], F["cluster_azimuth"])},
        "control": {"clouds": np.concatenate(ctl_clouds), "clusters": np.concatenate(ctl_clusters)},
        "annulus": C.Annulus(float(R[0]) * 1000.0, float(R[-1]) * 1000.0),
    }


def _judged(corr: C.Correlation) -> tuple[float, float, float]:
    law = C.fit_power_law(corr, *FIT_PC)
    beyond = C.centres(corr.edges) > BEYOND_PC
    return law.alpha, law.amplitude * (FIT_PC[0] / C.PIVOT_PC) ** law.alpha, float(np.nanmax(np.abs(corr.one_plus_omega[beyond] - 1.0)))


@pytest.mark.parametrize("name", ("clouds", "clusters"))
def test_the_census_against_its_own_law_returns_the_hierarchy_s_slope(census, name):
    corr = C.against_control(census["data"][name], census["control"][name], census["annulus"])
    slope, at_finest, worst = _judged(corr)
    assert abs(slope - TARGET_SLOPE) < SLOPE_WINDOW, slope  # judged (D220 part II item 7 a-b)
    assert worst < FLAT_WITHIN, worst
    assert (slope, at_finest, worst) == pytest.approx(MEASURED[name], abs=1e-3)  # as measured


def test_the_literal_control_shares_the_clumps_and_reads_one(census):
    """Why the control is the law without the field: the same census under other systems seeds, the field kept,
    stands its clouds in the same clumps, and the ratio reads 1 (the module's docstring)."""
    out, c = census["out"], census["c"]
    F, R = out.fields, out.grid.R
    seed, tex = int(out.inputs["systems_seed"]), int(out.inputs["texture_seed"])
    same = [CL.materialise_clouds(F, R, s, c, texture_seed=tex, texture=False) for s in range(seed + 1, seed + 3)]
    ctl = np.concatenate([C.positions_pc(x["cloud_radius"], x["cloud_azimuth"]) for x in same])
    slope, at_finest, _ = _judged(C.against_control(census["data"]["clouds"], ctl, census["annulus"]))
    assert abs(slope) < 0.1 and abs(at_finest - 1.0) < 0.1, (slope, at_finest)


def test_the_disclosed_square_at_r_sun_as_measured(census):
    """Not judged (D220 part II item 1): recorded beside the S60 census's numbers and the sources'."""
    out, c = census["out"], census["c"]
    square = C.solar_pointing(c["R_SUN"])
    young = np.asarray(out.fields["cluster_age"]) <= 10.0
    for key, xy in (("clouds", census["data"]["clouds"]), ("clusters<=10Myr", census["data"]["clusters"][young])):
        corr = C.against_uniform(xy, square, multiple=10.0, seed=61)
        law = C.fit_power_law(corr, 100.0, 2000.0)
        got = (law.alpha, law.amplitude, corr.at(100.0), corr.at(300.0))
        assert got == pytest.approx(SQUARE_AFTER[key], abs=0.006), (key, got, SQUARE_BEFORE[key])


# --- the field alone (the constants' derivation, reproduced on one square) ---------------------------------------

SIDE_KPC = 6.08  # 1024 cells of 5.9375 pc
GRID = 1024


def _field_grid(field: ClusteringField) -> np.ndarray:
    h = SIDE_KPC / GRID
    x = -SIDE_KPC / 2 + (np.arange(GRID) + 0.5) * h
    X, Y = np.meshgrid(x, x, indexing="xy")
    return field.map(X, Y)


def _exact_expectation(f: np.ndarray) -> np.ndarray:
    """E[f(x) f(x + r)] / E[f]^2 over the square, binned as the instrument bins: the two-point function of points
    drawn by f, without their Poisson noise (zero-padded FFT, divided by the overlap of the square with itself)."""
    n = f.shape[0]
    h = SIDE_KPC / n * 1000.0
    pad = np.zeros((2 * n, 2 * n)); pad[:n, :n] = f
    ind = np.zeros((2 * n, 2 * n)); ind[:n, :n] = 1.0
    F, W = np.fft.rfft2(pad), np.fft.rfft2(ind)
    corr = np.fft.irfft2(F * np.conj(F), s=pad.shape) / np.maximum(np.fft.irfft2(W * np.conj(W), s=pad.shape), 0.5)
    reach = int(math.ceil(1200.0 / h))
    lag = np.arange(-reach, reach + 1)
    sub = corr[np.ix_(lag % (2 * n), lag % (2 * n))] / f.mean() ** 2
    r = np.hypot(*np.meshgrid(lag, lag, indexing="xy")) * h
    which = np.digitize(r.ravel(), C.EDGES_PC) - 1
    ok = (which >= 0) & (which < C.EDGES_PC.size - 1)
    total = np.bincount(which[ok], weights=sub.ravel()[ok], minlength=C.EDGES_PC.size - 1)
    count = np.bincount(which[ok], minlength=C.EDGES_PC.size - 1)
    return np.where(count > 0, total / np.maximum(count, 1), np.nan)


def test_the_field_alone_has_the_statistic_it_was_derived_to(census):
    out, c = census["out"], census["c"]
    field = ClusteringField.of(field_seed(int(out.inputs["texture_seed"])), c)
    assert field.seed == int(out.fields["census_clustering_seed"])
    f = _field_grid(field)
    exact = _exact_expectation(f)
    corr = C.Correlation(C.EDGES_PC, exact, np.ones(exact.size, dtype=np.int64), None, None, 1, 1, 0, "exact", 0.0)
    law = C.fit_power_law(corr, *FIT_PC)
    r = C.centres()
    near = (r > BEYOND_PC) & (r < 1200.0)
    assert abs(law.alpha - TARGET_SLOPE) < SLOPE_WINDOW and np.max(np.abs(exact[near] - 1.0)) < FLAT_WITHIN
    # Points drawn by the field (a grid cell by its share of f, uniform within it) through the instrument.
    rng = np.random.default_rng(61)
    p = f.ravel() / f.sum()
    k = rng.choice(p.size, size=10_000, p=p)
    h = SIDE_KPC / GRID
    iy, ix = np.divmod(k, GRID)
    xy = np.column_stack([-SIDE_KPC / 2 + (ix + rng.random(k.size)) * h, -SIDE_KPC / 2 + (iy + rng.random(k.size)) * h]) * 1000.0
    # Bins to 1.3 kpc only: the pairs counted in a 6 kpc square fall tenfold, and the fit's range is below 190 pc.
    square = C.Square(0.0, 0.0, SIDE_KPC * 1000.0)
    near_edges = C.EDGES_PC[C.EDGES_PC <= 1300.0]
    pts = C.fit_power_law(C.landy_szalay(xy, C.Comparison.uniform(square, 100_000, 61, near_edges)), *FIT_PC)
    assert abs(pts.alpha - law.alpha) < 3.0 * max(pts.alpha_error, 0.02), (pts.alpha, law.alpha)
    got = {"exact": (law.alpha, law.amplitude * (FIT_PC[0] / C.PIVOT_PC) ** law.alpha), "points": (pts.alpha,)}
    for key, want in FIELD_ALONE.items():
        if want is not None:
            assert got[key] == pytest.approx(want, abs=1e-3), (key, got[key])


# --- the young bright stars by age (D220 part II items 5 and 7c) ------------------------------------------------------

# The bright catalogue at the stage's own selection asked for 20 000 stars over the whole disc (log L_min 4.220, 19 694
# stars; the S61 probe's threshold), layer on, against its own law: the same catalogue under four other systems seeds,
# pooled, with the field's width 0 (the young stars then placed in their level-0 cell by the radial law and the young
# reader alone). Age bins at the octaves' survival ages, dt(lambda) = A1 lambda^a: 23.87, 31.18 and 40.71 Myr.
BRIGHT_TARGET = 20_000
# As measured at S61 (default galaxy): fitted slope over [47.5, 190] pc / the law at 47.5 pc / worst |1 + omega - 1|
# beyond 380 pc; and the pair-merged 1 + omega over the bins centred in [47.5, 190] pc. Before the field (the branch
# at 0969929, the same construction) every bin read 1 within its noise: +0.033 / 0.953, -0.138 / 1.105, +0.211 / 0.787,
# -0.046 / 1.039 (slope / law at 47.5 pc).
BRIGHT_MEASURED = {
    "20-23.87": (-0.570, 2.154, 0.0506, 1.296),
    "23.87-31.18": (-0.599, 2.100, 0.0115, 1.228),
    "31.18-40.71": (-0.007, 1.234, 0.0318, 1.229),
    "40.71-100": (-0.046, 1.039, 0.0205, 0.999),
}
# The templates by hand, the same construction (milky_way the default's luminosity function and seeds: the same
# counts; ngc_4414 log L_min 4.040, 20 258 stars), each about 45 s:
#   milky_way  -0.588 / 1.985 / 0.0494 | -0.553 / 2.065 / 0.0377 | -0.224 / 1.492 / 0.0287 | +0.011 / 0.967 / 0.0192 (merged 0.976)
#   ngc_4414   -0.703 / 2.329 / 0.0566 | -0.519 / 2.024 / 0.0365 | -0.140 / 1.450 / 0.0257 | +0.088 / 0.934 / 0.0249 (merged 0.999)
# The disclosed square at R_SUN (slope over [100, 2000] pc, A at 300 pc, 1 + omega at 100 and 300 pc), not judged:
# the S60 census in the probe -0.33 / 1.77 (20-40 Myr) and -0.36 / 2.02 (40-100 Myr); the branch before the field
# (0969929) -0.285 / 1.74 / 1.90 / 1.88 and -0.441 / 2.20 / 3.42 / 1.93; after, below. milky_way after: -0.208 / 1.55 /
# 2.14 / 1.42 and -0.111 / 1.61 / 1.28 / 1.42; ngc_4414 after: -0.359 / 1.86 / 2.88 / 1.80 and -0.065 / 1.45 / 2.23 / 2.31.
BRIGHT_SQUARE_AFTER = {"20-40": (-0.302, 1.75, 2.39, 1.72), "40-100": (-0.415, 2.14, 3.31, 1.79)}


@pytest.fixture(scope="module")
def bright(census):
    out, c = census["out"], census["c"]
    F, R, spec = out.fields, out.grid.R, out.grid.spec
    seed = int(out.inputs["systems_seed"])
    cells = BR.all_cells()
    galaxy = BR.BrightGalaxy(F, R, out.grid.t, spec.t_max, spec.n_t, c)
    l_min = 10.0 ** galaxy.threshold(cells, BRIGHT_TARGET)
    law = BR.BrightGalaxy(F, R, out.grid.t, spec.t_max, spec.n_t, dict(c, **{WIDTH: 0.0}))
    return {"galaxy": galaxy, "data": BR.materialise_bright(galaxy, seed, cells, l_min),
            "control": [BR.materialise_bright(law, s, cells, l_min) for s in range(seed + 1, seed + 1 + CONTROL_SEEDS)]}


def _aged(cat, lo: float, hi: float) -> np.ndarray:
    age = np.asarray(cat["bright_star_age"]) * 1000.0
    keep = (age >= lo) & (age <= hi) if lo <= 20.0 else (age > lo) & (age <= hi)
    return C.positions_pc(np.asarray(cat["bright_star_radius"])[keep], np.asarray(cat["bright_star_azimuth"])[keep])


def _merged(corr: C.Correlation, lo: float, hi: float) -> float:
    """1 + omega of the bins centred in [lo, hi] merged into one: Landy-Szalay on their summed pair counts."""
    m = (corr.r >= lo) & (corr.r <= hi)
    ddn = corr.dd[m] / (corr.n_data * (corr.n_data - 1) / 2.0)
    drn = corr.dr[m] / (corr.n_data * float(corr.n_random))
    rrn = (ddn - 2.0 * drn) / (corr.one_plus_omega[m] - 2.0)  # each bin's normalised RR, from its own 1 + omega
    return float(2.0 + (ddn.sum() - 2.0 * drn.sum()) / rrn.sum())


def test_the_young_bright_stars_lose_the_field_s_octaves_as_they_age(bright, census):
    """D220 part II item 7c, the predictions of item 5 measured, not tuned. **Judged**: the youngest bin (20-23.87 Myr,
    every octave) returns the hierarchy's slope, within 0.15 of -0.64; the oldest (40.71-100 Myr, no octave: the
    pattern alone places them) reads 1 within 0.05 - its fitted law at 47.5 pc, its pair-merged 1 + omega over
    [47.5, 190] pc and every bin beyond 380 pc (its single bins below 190 pc carry Poisson errors of 0.05-0.22 on
    1 957 stars, so "at every scale" is read on the merged bins).

    **Not met, recorded for the lead**: the youngest bin's "1 +- 0.05 beyond 380 pc" reads 0.0506 here (0.954 and
    0.949 at 341 and 440 pc, about 4 sigma below 1), 0.0494 on milky_way and 0.0566 on ngc_4414 - the clouds read
    0.0216. A deficit just past the field's scale, where a level-0 cell's fixed count pays for the excess it holds
    below it (the integral constraint of a placement inside the cell) [inferred]. And the middle bins do not return
    to 1 below their finest kept octave, as item 5 predicted: a log-normal map of the coarser octaves alone is flat
    below them at its own plateau, not at 1 - two octaves read 2.10 at 47.5 pc (the full field 2.15), one octave
    1.23 - so the bins differ little until the last octave goes. Pinned as measured.

    Cost: about 40 s on the census's run (the catalogue 14 s, the four controls 24 s)."""
    galaxy = bright["galaxy"]
    ages = galaxy.octave_ages
    assert ages == pytest.approx([40.7112, 31.1758, 23.8738], abs=1e-4)
    bins = {"20-23.87": (20.0, ages[2]), "23.87-31.18": (ages[2], ages[1]), "31.18-40.71": (ages[1], ages[0]),
            "40.71-100": (ages[0], 100.0)}
    got = {}
    for key, (lo, hi) in bins.items():
        control = np.concatenate([_aged(cat, lo, hi) for cat in bright["control"]])
        corr = C.against_control(_aged(bright["data"], lo, hi), control, census["annulus"])
        got[key] = (*_judged(corr), _merged(corr, *FIT_PC))
    slope = got["20-23.87"][0]
    assert abs(slope - TARGET_SLOPE) < SLOPE_WINDOW, got["20-23.87"]  # judged
    _, at_finest, worst, merged = got["40.71-100"]
    assert abs(at_finest - 1.0) < FLAT_WITHIN and abs(merged - 1.0) < FLAT_WITHIN and worst < FLAT_WITHIN, got["40.71-100"]
    for key, want in BRIGHT_MEASURED.items():
        assert got[key] == pytest.approx(want, abs=1e-3), (key, got[key])


def test_the_disclosed_square_of_the_young_bright_stars(bright, census):
    """Not judged (D220 part II items 1, 5 and 7e): the 6 kpc square at R_SUN against uniform randoms, before (above)
    and after the field."""
    square = C.solar_pointing(census["c"]["R_SUN"])
    for key, (lo, hi) in (("20-40", (20.0, 40.0)), ("40-100", (40.0, 100.0))):
        corr = C.against_uniform(_aged(bright["data"], lo, hi), square, multiple=10.0, seed=61)
        law = C.fit_power_law(corr, 100.0, 2000.0)
        got = (law.alpha, law.amplitude, corr.at(100.0), corr.at(300.0))
        assert got == pytest.approx(BRIGHT_SQUARE_AFTER[key], abs=0.006), (key, got)

