"""Audit III (S37): the second build's redistributions and balances re-derived at a mesh the build did not use.

Every phase asserted its own redistribution on the default or the coarse grid (RENDER_PHYSICS section 7).
This file runs the same identities once on a mesh none of those tests use, so that a closure that held only
where it was tuned would show. Nothing here pins a physics number that a later session would move: the
identities are exact (the balance, the pattern's mean, the recomputed bound mass, the remnants' expectation)
or bounded by the census's own Poisson noise (the clouds, the clusters' photons, the HII regions).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages import clusters as cs
from galaxy.stages import systems as sy
from galaxy.stages.disc import PC_PER_KPC

AUDIT_MESH = GridSpec(n_R=180, n_t=600, n_z=8)  # neither the default GridSpec() nor the tests' coarse (120, 400, 6)
PARENT = 300


@pytest.fixture(scope="module")
def audit():
    ms, _, _ = production()
    model = ms.get("basic")
    o = run(model, grid=AUDIT_MESH)
    return o, {k: v.value for k, v in model.constants.items()}


def _integral(field, R):
    return float(np.trapezoid(np.asarray(field, dtype=float) * 2.0 * math.pi * R, R))


def test_the_mesh_is_one_the_build_did_not_use(audit):
    o, _ = audit
    assert (o.grid.R.size, o.grid.t.size) == (180, 600)
    d = GridSpec()
    assert (o.grid.R.size, o.grid.t.size) not in {(120, 400), (d.n_R, d.n_t)}


def test_the_exact_identities_hold_at_the_audit_mesh(audit):
    o, c = audit
    F, R = o.fields, o.grid.R
    # D180: absorbed = emitted, per radius and in total
    a = np.asarray(F["dust_absorbed_surface_brightness"]); e = np.asarray(F["dust_infrared_surface_brightness"])
    assert float(np.max(np.abs(e[a > 0] / a[a > 0] - 1.0))) < 1e-9
    assert abs(float(F["dust_infrared_luminosity"]) / float(F["dust_absorbed_luminosity"]) - 1.0) < 1e-12
    # the pattern's contrast averages to 1 around every ring
    assert float(np.max(np.abs(np.asarray(F["pattern_density_contrast"]).mean(axis=1) - 1.0))) < 1e-9
    # D183: the bound mass the globular-cluster stage recomputes is the clusters stage's field
    assert cs.bound_mass(F["stars_formed_history"], R, float(c["CLUSTER_BOUND_FRACTION"])) == pytest.approx(float(F["bound_cluster_mass_total"]), rel=1e-12)
    # D185: the remnants' expectation is the rates times the lifetime, integrated
    rates = _integral(np.asarray(F["core_collapse_rate"]) + np.asarray(F["type_ia_rate"]), R) * float(c["REMNANT_VISIBLE_LIFETIME"])
    assert float(F["remnant_count_total"]) == pytest.approx(rates, rel=1e-9)
    # D184: the nebular field integrates to its own scalar
    assert _integral(F["halpha_surface_brightness_nebular"], R) * PC_PER_KPC**2 == pytest.approx(float(F["halpha_luminosity_nebular"]), rel=1e-12)


def test_the_censuses_redistribute_within_their_own_noise_at_the_audit_mesh(audit):
    o, c = audit
    F, R = o.fields, o.grid.R
    # D181: the clouds hold the molecular mass, to the heavy tail's noise
    m_h2 = _integral(F["gas_molecular_surface_density"], R) * PC_PER_KPC**2
    m = np.asarray(F["cloud_mass"], dtype=float)
    noise = math.sqrt(float((m**2).sum())) / float(m.sum())
    assert float(F["cloud_mass_total"]) / m_h2 == pytest.approx(1.0, abs=3.0 * noise)
    # D182: the clusters' photons close on the light stage's, to the census's noise
    q = np.asarray(F["cluster_ionizing_photons"], dtype=float)
    q_noise = math.sqrt(float((q**2).sum())) / float(q.sum())
    assert float(q.sum()) / float(F["ionizing_photon_rate_total"]) == pytest.approx(1.0, abs=3.0 * q_noise + 0.02)
    # D184: the HII regions integrate to the field, to the census's noise
    L = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    field = _integral(F["halpha_surface_brightness_hii"], R) * PC_PER_KPC**2
    l_noise = math.sqrt(float((L**2).sum())) / float(L.sum())
    leak = float(F["dig_halpha_fraction"]) - float(c["HII_ESCAPE_FRACTION"])
    assert float(L.sum()) / field == pytest.approx(1.0, abs=3.0 * l_noise + leak + 0.02)
    # D185: the remnants drawn against their expectation, Poisson
    n = int(np.asarray(F["remnant_age"]).size)
    expected = float(F["remnant_count_total"])
    assert abs(n - expected) < 3.0 * math.sqrt(expected)


def test_the_hierarchy_union_holds_at_the_audit_mesh(audit):
    o, _ = audit
    F, R, t = o.fields, o.grid.R, o.grid.t
    seed = int(o.inputs["systems_seed"])
    parent = sy.materialise(F, R, t, seed, 20000, cells=[PARENT], migration=3.6)
    for level in (1, 2, 3):
        kids = [sy.child_id(PARENT, level, q) for q in range(sy.children_per_cell(level))]
        cat = sy.materialise(F, R, t, seed, 20000, cells=kids, migration=3.6, level=level)
        inherited = np.asarray(cat["level"]) == 0
        assert int(inherited.sum()) == parent.size
        order = np.argsort(np.asarray(cat["index"])[inherited])
        for name in parent:
            if name in cat and name not in ("level", "cell", "index"):
                assert np.array_equal(np.asarray(cat[name])[inherited][order], np.asarray(parent[name]), equal_nan=True), (level, name)
