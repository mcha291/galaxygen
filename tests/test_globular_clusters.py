"""Globular clusters and the stellar halo (S34, BUILD_II Phase 5): the survival of the bound clusters, the
seeded residual, the metal-poor share, the accreted debris, and rows 32-33 with their sources' arithmetic.

The claims that hold on any grid are asserted on the coarse one; the numbers the report quotes are pinned
on the default grid, which a partial run (``only=``) reaches in a fraction of a second.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core import seeds as _seeds
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages import globular_clusters as gc
from galaxy.stages import stellar_halo as sh
from galaxy.stages.clusters import bound_mass

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
WANT = (
    "gc_system_mass", "gc_count_estimate", "gc_survival_fraction", "gc_metal_poor_fraction", "halo_stellar_mass",
    "halo_stellar_density", "stars_formed_history", "halo_virial_mass",
)

# The Harris catalogue's Part II, column M_V,t, in file order (157 rows; GLIMPSE02 has none), read at S34 from
# https://physics.mcmaster.ca/~harris/mwgc.dat (December 2010 revision) in two independent transcriptions
# that agree to the digit; the second carried V_t and (m-M)V, and M_V,t = V_t - (m-M)V held on every row.
HARRIS_MV = (
    -9.42, -6.75, -8.43, -2.46, -7.80, -2.52, -4.73, -5.13, -7.97, -8.33, -7.86, -6.31, -9.42, -0.35, -5.73, -9.39,
    -4.12, -5.69, -7.45, -6.01, -1.35, -6.17, -7.79, -6.35, -7.37, -8.17, -8.71, -6.76, -10.26, -8.88, -8.74, -1.81,
    -6.98, -7.69, -7.83, -7.32, -8.85, -5.17, -7.23, -8.81, -7.81, -7.18, -4.06, -8.44, -6.60, -4.80, -8.23, -7.19,
    -6.94, -6.85, -8.36, -4.82, -7.12, -4.02, -8.55, -8.06, -7.31, -6.45, -6.29, -7.48, -7.15, -5.51, -9.18, -9.13,
    -7.96, -7.36, -7.78, -7.30, -8.34, -8.21, -6.96, -7.95, -6.42, -8.51, -8.07, -6.47, -6.15, -5.88, -5.74, -4.48,
    -6.46, -6.95, -7.32, -7.50, -4.41, -6.17, -9.41, -9.10, -7.90, -6.64, -6.79, -6.67, -6.98, -7.42, -8.75, -9.63,
    -7.59, -7.22, -6.91, -7.20, -3.71, -7.00, -8.25, -6.35, -7.65, -4.75, -6.57, -8.29, -6.35, -6.94, -8.52, -6.11,
    -4.87, -7.77, -4.86, -6.44, -6.67, -4.14, -8.28, -4.19, None, -7.69, -7.49, -8.16, -7.12, -7.64, -6.66, -6.66,
    -8.50, -5.51, -7.12, -5.91, -7.50, -9.98, -5.66, -7.83, -6.70, -7.73, -7.84, -7.41, -5.01, -5.79, -5.29, -7.57,
    -5.07, -6.92, -5.61, -8.57, -7.45, -7.04, -7.67, -9.19, -9.03, -7.45, -4.47, -3.76, -5.81,
)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {m.name: m for m in ms}


@pytest.fixture(scope="module")
def constants(models):
    return {k: v.value for k, v in models["basic"].constants.items()}


@pytest.fixture(scope="module")
def default(models):
    return run(models["basic"], only=(*WANT, "bound_cluster_mass_total"))


@pytest.fixture(scope="module")
def coarse(models):
    return run(models["basic"], grid=COARSE, only=(*WANT, "bound_cluster_mass_total"))


def _mean(o, c):
    return float(o.fields["gc_survival_fraction"]) * bound_mass(o.fields["stars_formed_history"], o.grid.R, c["CLUSTER_BOUND_FRACTION"])


def test_the_sourced_constants_and_their_arithmetic(constants):
    """Boylan-Kolchin's ratios, scatter and mean mass; Lamers et al.'s disruption; PZMG10's mass function; BHG16's halo."""
    c = constants
    assert (c["GC_HALO_MASS_RATIO"], c["GC_METAL_POOR_HALO_MASS_RATIO"]) == (3.5e-5, 2.25e-5)  # midpoints of 3-4, 2-2.5
    assert (c["GC_SYSTEM_SCATTER"], c["GC_MEAN_MASS"]) == (0.28, 2.5e5)
    assert (c["CLUSTER_DISRUPTION_T0"], c["CLUSTER_DISRUPTION_INDEX"]) == (3.3, 0.62)
    assert (c["CLUSTER_MASS_FUNCTION_INDEX"], c["CLUSTER_MASS_FUNCTION_SCALE"], c["CLUSTER_MASS_MIN"]) == (2.0, 2.0e5, 1.0e2)
    assert (c["STELLAR_HALO_INNER_SLOPE"], c["STELLAR_HALO_OUTER_SLOPE"]) == (-2.5, -4.5)
    assert (c["STELLAR_HALO_BREAK_RADIUS"], c["STELLAR_HALO_FLATTENING"]) == (25.0, 0.65)
    # BUILD_II's consistency check: 3.5e-5 x 1.1e12 ~ 3.9e7 Msun, ~160 clusters at a typical 2.4e5.
    assert c["GC_HALO_MASS_RATIO"] * 1.1e12 == pytest.approx(3.85e7)
    # Lamers et al. 2005: t0 = 3.3 Myr 'implies a total disruption time of a 10^4 Msun cluster of 1.3 +/- 0.5 Gyr';
    # with the model's own stellar-evolution remainder (1 - R = 0.7) the formula gives 1.288 Gyr.
    mu_ev = 1.0 - c["RETURN_FRACTION"]
    life = gc.disruption_time(1.0e4, c["CLUSTER_DISRUPTION_T0"], c["CLUSTER_DISRUPTION_INDEX"], mu_ev) / 1.0e3
    assert life == pytest.approx(1.2885, abs=5e-4) and abs(life - 1.3) < 0.5
    assert gc.disruption_time(1.0e5, 3.3, 0.62, mu_ev) / 1.0e3 == pytest.approx(5.371, abs=1e-3)
    # Eq. 6 at its ends: at age 0 only stellar evolution has acted; at the disruption time nothing is left.
    assert gc.remaining_fraction(np.array([0.0]), np.array([1.0e4]), 3.3, 0.62, mu_ev)[0] == pytest.approx(mu_ev)
    assert gc.remaining_fraction(np.array([life * 1.0e3 * 1.0001]), np.array([1.0e4]), 3.3, 0.62, mu_ev)[0] == 0.0
    # d(M^gamma)/dt = -gamma/t0 (M in Msun, t in Myr): the bracket falls linearly in age.
    half = gc.remaining_fraction(np.array([life * 500.0]), np.array([1.0e4]), 3.3, 0.62, mu_ev)[0]
    assert half ** 0.62 == pytest.approx(0.5 * mu_ev ** 0.62)
    # The mass mesh reaches a hundred Schechter scales, where the law is e^-100.
    M = gc.mass_mesh(1.0e2, 2.0e5)
    assert M[0] == 1.0e2 and M[-1] == pytest.approx(2.0e7) and M.size == gc.MASS_POINTS


def test_the_bound_mass_is_s33s_and_the_system_is_its_survivors(coarse, constants):
    """Ruling (a): the stage recomputes S33's integral with S33's function; the mean is survival x bound."""
    o, c = coarse, constants
    F = o.fields
    assert bound_mass(F["stars_formed_history"], o.grid.R, c["CLUSTER_BOUND_FRACTION"]) == F["bound_cluster_mass_total"]
    assert 0.0 < F["gc_survival_fraction"] < 1.0
    per_step = sh.formed_per_step(F["stars_formed_history"], o.grid.R)
    age = (o.grid.spec.t_max - o.grid.t) * 1.0e3
    assert F["gc_survival_fraction"] == gc.survival_fraction(per_step, age, c, 1.0 - c["RETURN_FRACTION"])
    # No time, no loss: a history formed at age 0 keeps every cluster (the survival is mu/mu_ev = 1).
    assert gc.survival_fraction(np.array([1.0]), np.array([0.0]), c, 0.7) == pytest.approx(1.0, abs=1e-12)
    # Older is never more: the survival falls monotonically with a single burst's age.
    s = [gc.survival_fraction(np.array([1.0]), np.array([a]), c, 0.7) for a in (1e2, 1e3, 3e3, 1e4)]
    assert all(x > y for x, y in zip(s, s[1:]))
    # A longer disruption time keeps more (the N-body alternative, five times longer).
    slow = dict(c, CLUSTER_DISRUPTION_T0=5.0 * c["CLUSTER_DISRUPTION_T0"])
    assert gc.survival_fraction(per_step, age, slow, 0.7) > F["gc_survival_fraction"]


def test_the_halo_relation_is_the_check_and_debt_97_closes_on_it(default, constants):
    """The surviving mass against eta M_halo, within Boylan-Kolchin's 0.28 dex, at the default."""
    o, c = default, constants
    F = o.fields
    assert F["gc_survival_fraction"] == pytest.approx(0.0250196, rel=1e-5)
    assert F["bound_cluster_mass_total"] == pytest.approx(2.78579e9, rel=1e-5)  # S33's, unmoved (D182)
    mean = _mean(o, c)
    assert mean == pytest.approx(6.96994e7, rel=1e-5)
    eta_m = c["GC_HALO_MASS_RATIO"] * F["halo_virial_mass"]
    assert eta_m == pytest.approx(3.85e7)
    dex = math.log10(mean / eta_m)
    assert dex == pytest.approx(0.2578, abs=5e-4)
    assert abs(dex) <= c["GC_SYSTEM_SCATTER"]  # the stated precision: the relation's own scatter
    # Before survival the bound mass was 72.4 x eta M_halo (D182); the survival removes 97.5% of it.
    assert F["bound_cluster_mass_total"] / eta_m == pytest.approx(72.36, abs=0.01)


def test_the_survivors_are_mostly_young(default, constants):
    """What #97's closure stands on: the survivors' ages. Pinned so a reader can see the numbers moving."""
    o, c = default, constants
    per_step = sh.formed_per_step(o.fields["stars_formed_history"], o.grid.R)
    age = (o.grid.spec.t_max - o.grid.t) * 1.0e3
    total = gc.survival_fraction(per_step, age, c, 0.7)

    def older_than(gyr, cc=c):
        w = np.where(age >= gyr * 1.0e3, per_step, 0.0)
        return gc.survival_fraction(w, age, cc, 0.7) * w.sum() / per_step.sum()

    assert older_than(1.0) / total == pytest.approx(0.531, abs=1e-3)
    assert older_than(10.0) / total == pytest.approx(0.0074, abs=5e-4)
    bound = o.fields["bound_cluster_mass_total"]
    eta_m = c["GC_HALO_MASS_RATIO"] * o.fields["halo_virial_mass"]
    assert math.log10(older_than(10.0) * bound / eta_m) == pytest.approx(-1.872, abs=2e-3)
    # The N-body tidal-field time-scale (Lamers et al.: 'a factor 5 shorter than derived from N-body'):
    slow = dict(c, CLUSTER_DISRUPTION_T0=5.0 * c["CLUSTER_DISRUPTION_T0"])
    assert math.log10(older_than(10.0, slow) * bound / eta_m) == pytest.approx(0.085, abs=2e-3)
    assert gc.survival_fraction(per_step, age, slow, 0.7) / total == pytest.approx(6.14, abs=0.01)


def test_the_residual_is_a_seeded_lognormal_on_world_seed(models, constants):
    """Ruling (b): drawn at 0.28 dex on world_seed under the stage's slot; the count is the mass over 2.5e5."""
    m, c = models["basic"], constants
    for seed in (0, 7):
        o = run(m, {"world_seed": seed}, grid=COARSE, only=("gc_system_mass", "gc_count_estimate", "gc_survival_fraction", "stars_formed_history"))
        dex = _seeds.rng(seed, "globular_clusters", "residual").normal(0.0, c["GC_SYSTEM_SCATTER"])
        assert o.fields["gc_system_mass"] == _mean(o, c) * math.pow(10.0, float(dex))
        assert o.fields["gc_count_estimate"] == o.fields["gc_system_mass"] / 2.5e5
    a = run(m, {"world_seed": 0}, grid=COARSE, only=("gc_system_mass",)).fields["gc_system_mass"]
    b = run(m, {"world_seed": 1}, grid=COARSE, only=("gc_system_mass",)).fields["gc_system_mass"]
    s = run(m, {"systems_seed": 5, "pattern_seed": 5}, grid=COARSE, only=("gc_system_mass",)).fields["gc_system_mass"]
    assert a != b and s == a  # world_seed alone moves it


def test_the_metal_poor_share_is_the_accreted_one(models, default, constants):
    """Ruling (c): eta_b/eta when the merger list accreted any stars; none when it accreted none."""
    c = constants
    assert default.fields["gc_metal_poor_fraction"] == pytest.approx(2.25 / 3.5)
    assert default.fields["gc_metal_poor_fraction"] == pytest.approx(0.642857, abs=1e-6)
    free = run(models["basic"], {"mergers": ()}, grid=COARSE, only=("gc_metal_poor_fraction", "halo_stellar_mass"))
    assert free.fields["halo_stellar_mass"] == 0.0 and free.fields["gc_metal_poor_fraction"] == 0.0
    assert gc.metal_poor_fraction(1.0, c) == c["GC_METAL_POOR_HALO_MASS_RATIO"] / c["GC_HALO_MASS_RATIO"]


def test_the_stellar_halo_is_the_accreted_debris(default, coarse, constants):
    """Ruling (d): every satellite whole, its mass ratio times the host's disc stars formed before it."""
    for o in (coarse, default):
        F = o.fields
        per_step = sh.formed_per_step(F["stars_formed_history"], o.grid.R)
        t = o.grid.t
        expect = 0.25 * per_step[t < 3.8].sum() + 0.02 * per_step[t < 8.8].sum()
        assert F["halo_stellar_mass"] == pytest.approx(expect, rel=1e-12)
    F = default.fields
    per_step = sh.formed_per_step(F["stars_formed_history"], default.grid.R)
    t = default.grid.t
    assert per_step[t < 3.8].sum() == pytest.approx(9.625e9, rel=1e-3)
    assert per_step[t < 8.8].sum() == pytest.approx(3.1086e10, rel=1e-3)
    assert F["halo_stellar_mass"] == pytest.approx(3.02802e9, rel=1e-5)


def test_the_halo_profile_holds_the_halo_mass(default, constants):
    """The oblate broken power law, integrated over its whole volume, is the mass it was normalised to."""
    c = constants
    inner, outer, rb, q = (c["STELLAR_HALO_INNER_SLOPE"], c["STELLAR_HALO_OUTER_SLOPE"],
                           c["STELLAR_HALO_BREAK_RADIUS"], c["STELLAR_HALO_FLATTENING"])
    rho_b = sh.broken_power_law_norm(1.0e9, inner, outer, rb, q)  # Msun/kpc^3
    # M = 4 pi q int rho(m) m^2 dm, on a log mesh from 1e-8 kpc to 1e5 kpc.
    m = np.geomspace(1e-8, 1e5, 400001)
    rho = rho_b * np.where(m < rb, (m / rb) ** inner, (m / rb) ** outer)
    assert 4.0 * math.pi * q * np.trapezoid(rho * m**3, np.log(m)) == pytest.approx(1.0e9, rel=1e-4)
    d = default.fields["halo_stellar_density"]
    R = default.grid.R
    assert d.shape == R.shape and np.all(d > 0.0)
    inside = (R > 1.0) & (R < 20.0)
    slope = np.diff(np.log(d[inside])) / np.diff(np.log(R[inside]))
    assert np.allclose(slope, inner)
    assert float(np.interp(8.2, R, d)) == pytest.approx(1.444e-4, rel=1e-3)  # Msun/pc^3 in the plane at R0
    with pytest.raises(ValueError):
        sh.broken_power_law_norm(1.0, -3.5, -4.5, 25.0, 0.65)


def test_the_harris_catalogue_arithmetic():
    """Row 32's target: the catalogue's own luminosities, summed, at BHG16's M/L_V = 1.4 +/- 0.5."""
    assert len(HARRIS_MV) == 157 and sum(v is None for v in HARRIS_MV) == 1
    lum = sum(10.0 ** (-0.4 * (v - 4.81)) for v in HARRIS_MV if v is not None)
    assert lum == pytest.approx(spec.HARRIS_LUMINOSITY_V, rel=1e-12)
    q = {x.n: x for x in spec.QUANTITIES}[spec.ROW_GC_SYSTEM_MASS]
    assert (q.lo, q.hi) == (0.9 * lum, 1.9 * lum) and q.mode == "statistical" and q.field == "gc_system_mass"
    assert 2.0 * lum == pytest.approx(3.4324e7, rel=1e-4)  # the catalogue's own M/L = 2, the named alternative


def test_rows_32_and_33_are_recorded_misses(judged):
    """Both rows fail and are recorded (rule B5), each with its debt and a prediction that could kill it."""
    for name, results in judged.items():
        by_n = {r.n: r for r in results}
        r32, r33 = by_n[spec.ROW_GC_SYSTEM_MASS], by_n[spec.ROW_STELLAR_HALO_MASS]
        assert r32.status == "fail" and r32.value == pytest.approx(7.13032e7, rel=1e-5)
        assert r33.status == "fail" and r33.value == pytest.approx(3.02802e9, rel=1e-5)
    assert spec.MISSES[spec.ROW_GC_SYSTEM_MASS].debt == 98 and spec.MISSES[spec.ROW_GC_SYSTEM_MASS].since == "S34"
    assert spec.MISSES[spec.ROW_STELLAR_HALO_MASS].debt == 99 and spec.MISSES[spec.ROW_STELLAR_HALO_MASS].since == "S34"
    q33 = {x.n: x for x in spec.QUANTITIES}[spec.ROW_STELLAR_HALO_MASS]
    assert (q33.lo, q33.hi, q33.mode) == (4.0e8, 7.0e8, "pointwise")
