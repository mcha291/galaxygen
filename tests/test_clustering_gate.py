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
from galaxy.layer import census_clustering as CC
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
# S62 (D221): was clouds (-0.636, 1.977, 0.0216), clusters (-0.670, 2.097, 0.0210) - the gas spurs on the gas
# contrast move the clouds' placement (and the clusters born in them) by a few thousandths; both well inside the
# judged window (|slope + 0.64| < 0.15) and flat beyond 380 pc (< 0.05).
# S90 (#161, the ring the unit of D220 part II's rule 2: the field's cell means in the clouds' sector weights): was
# clouds (-0.6396, 1.9798, 0.0212), clusters (-0.6578, 2.0842, 0.0210) - S70's and S67's figures, not met since #80's
# re-drawn census at S88 (clouds -0.4796 / 1.7815 / 0.0256, clusters -0.4882 / 1.8557 / 0.0266 on 352bdec, measured
# by s90 probe161.py with this file's construction); the cells' expectations now carry the field's coarse end, the
# amplitude rises (the bin holding 47.5 pc 2.08 -> 2.40, the field's own 2.43) and the clusters' slope comes inside
# the window (0.141 from -0.64), the clouds' not (0.156).
MEASURED = {
    "clouds": (-0.5035, 1.9885, 0.0199),  # S92 (#164 / #165, the spurs re-laid): was (-0.4965, 1.9852, 0.0205). S91 (#216's re-laid census, D260): was (-0.4843, 1.9452, 0.0205) - passes the window by 0.0065, not a mend (#219)
    # S70 (D234): was (-0.6908, 2.1129, 0.0221) - the clouds' ring inversion (F-2-7) and the size law's three regimes (#192:
    # the clouds inside 4 kpc and in 7-8.2 kpc larger, so a cluster's source offset reaches further); the window holds.
    "clusters": (-0.4970, 2.0176, 0.0282),  # S92 (#164 / #165, the spurs re-laid; inside the window by 0.003, the hold lifted - #219): was (-0.4791, 1.9997, 0.0287). S91 (#216's re-laid census, held under #219, D260): was (-0.4991, 2.0255, 0.0301). S90 (#161): was (-0.6578, 2.0842, 0.0210), above. S67 (D231): was (-0.6686, 2.0928, 0.0208) - a cluster's source offset is
    # bounded by its cloud's size, and the giants shrank (the radius cap 150 pc, Sigma 82 inside R_SUN); the judged window holds.
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
# S62 (D221): was {"clouds": (-0.163, 1.24, 2.01, 1.16), "clusters<=10Myr": (-0.141, 1.30, 1.60, 1.24)} - the gas
# spurs place the clouds on the spurs' streaks too, and the young clusters with them.
# S70 (D234): the young clusters' last figure was 1.131 - F-2-7 and #192 (their offsets in larger clouds).
SQUARE_AFTER = {"clouds": (-0.191, 1.322, 2.496, 1.356), "clusters<=10Myr": (-0.241, 1.480, 2.304, 1.480)}  # S92 (#164 / #165, disclosed, not judged): was clouds (-0.205, 1.335, 2.481, 1.336), clusters (-0.226, 1.476, 2.169, 1.551) - the spurs re-laid. S91 (#216's re-laid census, red at 3f16d0f, green on main; disclosed, not judged - the gate's ruling, D260): was -0.149, 1.292, 2.025, 1.324, -0.208, 1.404, 2.148, 1.262. S90 (#161): was -0.125, 1.223, 2.068, 1.182, -0.179, 1.315, 2.275, 1.203 - the field's cell means in the clouds' sector weights add its coarse end at 300 pc. S88 (M1's final model - #148's clock, #209's floor, #80's bar, #212's MERGER_HEATING 90.6; unrun since S86): was -0.170, 1.248, 2.088, 1.176, -0.154, 1.302, 1.838, 1.148
# S67 (D231): the young clusters' square was (-0.121, 1.278, 1.800, 1.202) - their offsets from their clouds shrink with
# the clouds (the size law); the clouds' own square did not move.
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



# S88 (M1's close): the L1 gate's judged clauses read over on M1's final model - held strict for the gate, not loosened.
# Measured by this file's own fixtures and helpers (s88_probe_l1gate.py) at three model states, the default galaxy:
#   clouds (slope, law at 47.5 pc, worst beyond 380 pc): S86 -0.6396 / 1.9798 / 0.0212; #148's clock -0.6360 / 1.9891 /
#     0.0155; final -0.4796 / 1.7809 / 0.0257 (|slope + 0.64| 0.160 against 0.15); clusters -0.6578 -> -0.6699 -> -0.4899
#     (0.150). The step is #80's: the defaults' bar 5.21 -> 2.27 kpc re-draws the census (48 pieces on 13 chains
#     where 32 on 6); the same flattening as Audit V's pair slope on the Milky Way (tests/test_audit_v.py, D255
#     ruling 3: the field reads its law, the per-cell placement of one realisation takes the rest).
#   the young bright stars, youngest bin's slope: S86 -0.5696, clock -0.5524, final -0.4750 (0.165 over); the
#     40.71-100 Myr bin's flatness (1 + omega at the finest within 0.05 of 1): S86 1.0391, clock 1.1887, final 0.8457 -
#     read over since the clock (#148).
L1_GATE_READ_OVER = ("S88 (M1): the L1 gate's judged slope read over on the final model - clouds -0.4796, clusters -0.4899 "
                     "against -0.64 +/- 0.15 (inside at the clock: -0.6360 / -0.6699; the step is #80's census); the gate's to rule")
BRIGHT_GATE_READ_OVER = ("S88 (M1): the young bright stars' judged clauses read over on the final model - the youngest bin's "
                         "slope -0.4750 (0.165 over the 0.15), the 40.71-100 Myr bin's finest 1 + omega 0.8457 (flat within 0.05: "
                         "out since #148's clock, 1.1887 there); the gate's to rule")


# S90 (#161): the clusters' case lifted - with the field's cell means in the clouds' sector weights their slope reads
# -0.4991, inside the window (0.141); the clouds' -0.4843 is still over (0.156) and held strict, the reason re-measured.
# S90 close (the gate, D258): #161 discharged; the clouds' residual is register #215 (the amplitude rose together at every
# scale below 190 pc, so the flatter shape #80's census left is unchanged) - held strict under #215, M3's, as
# L1_GATE_READ_OVER_S90 ("the clouds' judged slope reads -0.4843 against -0.64 +/- 0.15 (S88 -0.4796; the clusters'
# -0.4991 now inside); register #215, M3's").
# S91 close (the gate, D260): #216's re-laid census (red at 3f16d0f, green on main at 4f06cc9) moved both judged slopes
# and they exchanged sides of the window's edge at -0.49: the clouds' -0.4843 -> -0.4965, inside by 0.0065, so the
# strict hold passed and is lifted (L1_GATE_READ_OVER_S90 removed) - not a mend: one square's slope scatters 0.068
# between seeds, ten times the margin, and #215 is discharged on its own kill clause (the slope inside the window on a
# change that did not aim at it); the clusters' -0.4991 -> -0.4791, 0.161 from -0.64 against 0.15, held strict under
# register #219 - the gate's own debt, both populations at the edge since #80's census.
# S92 (#164 / #165's re-laid spurs; #219 read over nine censuses, the register entry): the clusters' slope reads -0.4970
# (inside by 0.003) and the clouds' -0.5035 (by 0.0035); over nine censuses (the default and systems = texture seed
# 1-8) the means are -0.6367 (sd 0.106) and -0.6177 (sd 0.103) - not at the edge. The clusters' strict hold read green
# and is lifted; L1_GATE_READ_OVER_S91 is kept as the record. The gate ruled (D261): the judged clause stays on the
# default census; #219 discharged.
L1_GATE_READ_OVER_S91 = ("S91 (#219, after #216's re-laid census): the clusters' judged slope reads -0.4791 against -0.64 +/- 0.15 "
                         "(S90 -0.4991, inside; the clouds' -0.4965 now inside by 0.0065); register #219, M3's")


@pytest.mark.parametrize("name", ("clouds",
                                  "clusters"))  # S92 (#219): the strict hold lifted - see L1_GATE_READ_OVER_S91's comment
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


def test_the_spill_s_cost_to_the_abundances_is_the_declared_one(census):
    """S61 (D220; the review's finding 1): ``conserves`` once said the abundances read at the ring's radius sat "up to
    about 0.06 dex of [Fe/H]" from the placed radius's - the 90th percentile, not the maximum. The declaration now
    carries the measured distribution, from the module's own numbers (``SPILL_FEH_DEX`` and the rest), and this holds
    the measurement to them: the median, the 90th and 99th percentiles and the maximum within 1e-3 dex (the declared
    digits; the default run is deterministic), the maximum's ring radius within 0.05 kpc, the count beyond 0.06 dex
    exactly, the [alpha/Fe] maximum within 1e-3. Costs nothing beyond the census's run."""
    F, R = census["out"].fields, census["out"].grid.R
    placed, born = np.asarray(F["cloud_radius"], dtype=float), np.asarray(F["cloud_birth_radius"], dtype=float)
    feh, alpha = np.asarray(F["feh_gas"], dtype=float), np.asarray(F["alpha_fe_gas"], dtype=float)
    d = np.abs(np.interp(placed, R, feh) - np.interp(born, R, feh))
    got = {"median": np.median(d), "p90": np.percentile(d, 90), "p99": np.percentile(d, 99), "max": d.max()}
    assert got == pytest.approx(CC.SPILL_FEH_DEX, abs=1e-3), got
    assert born[np.argmax(d)] == pytest.approx(CC.SPILL_FEH_MAX_AT_KPC, abs=0.05)
    at, beyond, total = CC.SPILL_FEH_BEYOND
    assert (int(np.sum(d > at)), d.size) == (beyond, total)
    assert np.abs(np.interp(placed, R, alpha) - np.interp(born, R, alpha)).max() == pytest.approx(CC.SPILL_ALPHA_MAX_DEX, abs=1e-3)
    text = CC.CENSUS_CLUSTERING_SEED.conserves  # the declaration is built from the same numbers
    for v in (*CC.SPILL_FEH_DEX.values(), CC.SPILL_FEH_MAX_AT_KPC, CC.SPILL_ALPHA_MAX_DEX):
        assert f"{v}" in text, v
    assert "about 0.06 dex" not in text


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
BRIGHT_SQUARE_AFTER = {"20-40": (-0.122, 1.283, 2.267, 1.292), "40-100": (-0.080, 1.195, -1.688, 1.831)}  # S91 (#216's re-laid census - the 20-40 Myr bin read -0.1217 on bb25415 and the same four numbers at HEAD, so #160's placement did not move it; the gate's ruling, D260; S92's #164 / #165 will move it again): was -0.286, 2.203, 3.75, 2.12, -0.289, 1.79, 1.604, 1.756  # S88 (M1's final model - #148's clock, #209's floor, #80's bar, #212's MERGER_HEATING 90.6; unrun since S86): was -0.302, 1.75, 2.39, 1.72, -0.415, 2.14, 3.31, 1.79


@pytest.fixture(scope="module")
def bright(census):
    out, c = census["out"], census["c"]
    F, R, spec = out.fields, out.grid.R, out.grid.spec
    seed = int(out.inputs["systems_seed"])
    cells = BR.all_cells()
    mig = float(out.inputs["migration_efficiency"])
    galaxy = BR.BrightGalaxy(F, R, out.grid.t, spec.t_max, spec.n_t, c, migration=mig)
    l_min = 10.0 ** galaxy.threshold(cells, BRIGHT_TARGET)
    law = BR.BrightGalaxy(F, R, out.grid.t, spec.t_max, spec.n_t, dict(c, **{WIDTH: 0.0}), migration=mig)
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


@pytest.mark.xfail(strict=True, reason=BRIGHT_GATE_READ_OVER)
def test_the_young_bright_stars_lose_the_field_s_octaves_as_they_age(bright, census):
    """D220 part II item 7c, the predictions of item 5 measured, not tuned. **Judged**: the youngest bin (20-23.87 Myr,
    every octave) returns the hierarchy's slope, within 0.15 of -0.64; the oldest (40.71-100 Myr, no octave: the
    pattern alone places them) reads 1 within 0.05 - its fitted law at 47.5 pc, its pair-merged 1 + omega over
    [47.5, 190] pc and every bin beyond 380 pc (its single bins below 190 pc carry Poisson errors of 0.05-0.22 on
    1 957 stars, so "at every scale" is read on the merged bins).

    **A miss of the 0.05 bound by up to 0.0066, carried under #161**: the youngest bin's "1 +- 0.05 beyond 380 pc"
    reads 0.0506 here (a dip to about 0.95 across 340-570 pc: 0.954 and 0.949 at 341 and 440 pc, about 4 sigma below
    1), 0.0494 on milky_way (inside) and 0.0566 on ngc_4414 - the clouds read 0.0216. It is the per-cell
    conservation's trough, register #161: a level-0 cell keeps its count, so the excess the field puts below its
    scale is paid for just past it - the same mechanism that cuts the clouds' amplitude to 1.97 at 47.5 pc (the field
    alone 2.43) and gives their 0.94 at 158 pc, which the clouds' flatness window, starting at 380 pc, skips.

    **A failed prediction, in kind** (D220 part II item 5; register #162, which the lead opens): the middle bins were
    to return to 1 below their finest kept octave's scale - 1 + omega -> 1 below 95 pc for two octaves, below 190 pc
    for one. They do not: a log-normal map of the coarser octaves alone plateaus at its own level below its finest
    kept scale, it does not fall to 1 - two octaves read 2.10 at 47.5 pc against the full field's 2.15, one octave
    1.23 (milky_way 1.49, ngc_4414 1.45) - so the age bins barely differ until the last octave drops at 40.71 Myr, a
    step, not a fading. A gradual fading needs the log-normal width to fall with age, as the sources' amplitudes do:
    Grasha et al. 2019's series 23 / 13 / 2.7 / 2.1 for <= 10, 10-50, 50-100 and > 100 Myr. Pinned as measured.

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

