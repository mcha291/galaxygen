"""S100 (#95, D270): a cluster's offset from its cloud by its age - Grasha et al. 2019's two printed medians.

The ruling (S100 builder G1's brief): a cluster younger than 10 Myr lies at a median of 2 cloud radii from its
cloud's centre, an older one at a median of 3 (Grasha et al. 2019, arXiv:1812.06109, sec. 4.1.1: 71 +- 3 pc and
107 +- 4 pc on a median cloud radius of 36 pc, M 51). The shape stays the present draw's, rescaled: the layer's
unit draw - the cloud's size times the cube root of a uniform on ``(texture_seed, "cloud", ring, "source_offset")``,
``cloud_source_offset`` - keeps its bits, and the clusters stage multiplies it by the ruled median over the unit
draw's own, 0.5^(1/3), at the cluster's age (the age exists only there). No new random draw.

What is held here: the two medians on each template within four of the median's sampling errors; the unit draw's
bits; the cloud columns' independence of the scaling (the same census materialised with the scaling at 1 and at
the ruled medians); the census's naming (a cluster is its cloud's cell and index) whatever the offset; the layer off
places every cluster at its cloud's centre still.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy import templates
from galaxy.core.registry import production
from galaxy.layer import cloud_texture as CT
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import clouds as CL
from galaxy.stages import clusters as CU

TEMPLATES = ("milky_way", "ngc_4414")
UNIT_MEDIAN = 0.5 ** (1.0 / 3.0)  # the median of the cube root of a uniform: the unit draw's median in cloud radii


@pytest.fixture(scope="module")
def gmodel():
    return production()[0].get(DEFAULT_MODEL)


@pytest.fixture(scope="module")
def constants(gmodel):
    return {k: v.value for k, v in gmodel.constants.items()}


@pytest.fixture(scope="module")
def runs(gmodel):
    return {name: run(gmodel, templates.overrides(templates.TEMPLATES[name]), layer=True) for name in TEMPLATES}


def _hosts(F) -> np.ndarray:
    return np.asarray(F["cloud_cluster_index"]) >= 0.0


def _offset_in_radii(F) -> np.ndarray:
    """Each cluster's distance from its cloud's centre in the plane, in its cloud's radii, from the published
    positions alone."""
    h = _hosts(F)
    r0, p0 = np.asarray(F["cloud_radius"])[h], np.asarray(F["cloud_azimuth"])[h]
    r1, p1 = np.asarray(F["cluster_radius"]), np.asarray(F["cluster_azimuth"])
    d_pc = np.hypot(r1 * np.cos(p1) - r0 * np.cos(p0), r1 * np.sin(p1) - r0 * np.sin(p0)) * 1000.0
    return d_pc / np.asarray(F["cloud_size"])[h]


def test_the_constants_are_the_source_s_two_medians_and_its_age():
    assert CU.CLUSTER_OFFSET_MEDIAN_YOUNG == 2.0 and CU.CLUSTER_OFFSET_MEDIAN_OLD == 3.0
    assert CU.CLUSTER_OFFSET_AGE_SPLIT == 10.0
    # The step at the source's own age: under 10 Myr the young median, at and over it the old.
    k = CU.offset_scale(np.array([0.0, 9.999, 10.0, 20.0]))
    assert np.allclose(k * UNIT_MEDIAN, [2.0, 2.0, 3.0, 3.0], rtol=0, atol=1e-15)


@pytest.mark.parametrize("name", TEMPLATES)
def test_the_two_medians_on_each_template(runs, name):
    """The median offset in cloud radii is 2 under 10 Myr and 3 over, within four sampling errors of a median:
    for x = s cbrt(u), s = median / 0.5^(1/3), the density at the median is 3 (0.5)^(2/3) / s, so the median of n
    draws has a standard error s / (6 (0.5)^(2/3) sqrt(n))."""
    F = runs[name].fields
    rel = _offset_in_radii(F)
    age = np.asarray(F["cluster_age"])
    for young, target in ((True, 2.0), (False, 3.0)):
        sel = (age < 10.0) if young else (age >= 10.0)
        n = int(sel.sum())
        assert n > 1000, (name, young, n)
        s = target / UNIT_MEDIAN
        se = s / (6.0 * 0.5 ** (2.0 / 3.0) * math.sqrt(n))
        assert abs(float(np.median(rel[sel])) - target) < 4.0 * se, (name, young, float(np.median(rel[sel])), se)
    # Exactly the unit draw times the age's factor: no other draw enters the cluster's offset.
    h = _hosts(F)
    assert np.allclose(rel, np.asarray(F["cloud_source_offset"])[h] * CU.offset_scale(age) / np.asarray(F["cloud_size"])[h],
                       rtol=1e-9, atol=0)


@pytest.mark.parametrize("name", TEMPLATES)
def test_the_unit_draw_keeps_its_bits(runs, constants, name):
    """``cloud_source_offset`` is the cloud's size times the cube root of the ring stream's uniform, as since S61:
    the scaling by age is the cluster's, not the cloud's."""
    out = runs[name]
    F, R = out.fields, out.grid.R
    layout = CL.cloud_layout(F, R, int(out.inputs["systems_seed"]), constants)
    u = CL.ring_draws(int(out.inputs["texture_seed"]), "cloud", layout, ("source_offset",))["source_offset"]
    assert np.array_equal(np.asarray(F["cloud_source_offset"]), np.asarray(F["cloud_size"]) * np.cbrt(u))
    drawn = CT.draw(int(out.inputs["texture_seed"]), layout, np.asarray(F["cloud_size"]))
    for k, v in drawn.items():
        assert np.array_equal(np.asarray(F[k]), v), k


def test_the_cloud_columns_and_every_other_cluster_column_do_not_depend_on_the_scaling(runs, constants, monkeypatch):
    """The same census materialised with the scaling at 1 (the medians set to the unit draw's own - the model
    before S100) and at the ruled medians: every cloud column is the census's and every cluster column but the
    placement is the same bit for bit; the placement differs."""
    out = runs["milky_way"]
    F, R = out.fields, out.grid.R
    seed = int(out.inputs["systems_seed"])
    clouds = CU.census_of_clouds(F, R, seed, constants)
    now = CU.materialise_clusters(clouds, F, R, seed, constants)
    monkeypatch.setattr(CU, "CLUSTER_OFFSET_MEDIAN_YOUNG", UNIT_MEDIAN)
    monkeypatch.setattr(CU, "CLUSTER_OFFSET_MEDIAN_OLD", UNIT_MEDIAN)
    before = CU.materialise_clusters(clouds, F, R, seed, constants)
    assert before.counts == now.counts
    for k in (*CU.CLUSTER_COLUMNS, "cluster_bound"):
        if k in ("cluster_radius", "cluster_azimuth"):
            assert not np.array_equal(before[k], now[k]), k
        else:
            assert np.array_equal(before[k], now[k]), k
    # The unit scaling is the volume-uniform draw: inside the cloud, at the column's length.
    h = _hosts(F)
    r0, p0 = np.asarray(F["cloud_radius"])[h], np.asarray(F["cloud_azimuth"])[h]
    d = np.hypot(before["cluster_radius"] * np.cos(before["cluster_azimuth"]) - r0 * np.cos(p0),
                 before["cluster_radius"] * np.sin(before["cluster_azimuth"]) - r0 * np.sin(p0)) * 1000.0
    assert np.allclose(d, np.asarray(F["cloud_source_offset"])[h], rtol=1e-9, atol=1e-9)
    # And the stage publishes the census at the ruled medians.
    for k in (*CU.CLUSTER_COLUMNS, "cluster_bound"):
        assert np.array_equal(now[k], F[k]), k


@pytest.mark.parametrize("name", TEMPLATES)
def test_the_naming_is_the_cloud_s_cell_and_index_wherever_the_offset_puts_it(runs, constants, name):
    """D60 / D220: a cluster is named by its cloud's cell and its rank among the cell's clusters, whatever cell its
    position falls in; the census's cells hold exactly the hosting clouds' clusters, in order."""
    out = runs[name]
    F, R = out.fields, out.grid.R
    seed = int(out.inputs["systems_seed"])
    clouds = CU.census_of_clouds(F, R, seed, constants)
    clusters = CU.materialise_clusters(clouds, F, R, seed, constants)
    index = np.asarray(F["cloud_cluster_index"])
    expected, offset = [], 0
    for cell, count in clouds.counts:
        k = int((index[offset:offset + count] >= 0.0).sum())
        named = index[offset:offset + count][index[offset:offset + count] >= 0.0].astype(int)
        assert np.array_equal(named, np.arange(k)), cell
        if k:
            expected.append((cell, k))
        offset += count
    assert list(clusters.counts) == expected
    assert np.array_equal(np.asarray(F["cluster_birth_radius"]), np.asarray(F["cloud_birth_radius"])[_hosts(F)])


def test_the_layer_off_places_every_cluster_at_its_cloud_s_centre(gmodel):
    out = run(gmodel, templates.overrides(templates.TEMPLATES["ngc_4414"]), layer=False)
    F = out.fields
    h = _hosts(F)
    assert np.array_equal(np.asarray(F["cluster_radius"]), np.asarray(F["cloud_radius"])[h])
    assert np.array_equal(np.asarray(F["cluster_azimuth"]), np.mod(np.asarray(F["cloud_azimuth"])[h], 2.0 * math.pi))
