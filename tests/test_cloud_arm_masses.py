"""The clouds' mass function's cut by the arm (S102, #231; branch q-231, FRAMES ONLY - the owner's to order).

Rosolowsky et al. 2021 (arXiv:2101.04697, Sect. 6.2.2, Table 5): "the truncation mass in the Spiral Arms is a factor
of 2.5 higher than the truncation mass in the Interarm regions". The zone's cut (Rice et al. 2016) is kept as the
geometric mean of the arm's and the inter-arm's [inferred]; the mask is the gas pattern's own (``GasPattern.arm_rings``
and ``ratio_of_means``' rule at ``ARM_GAS_RELATION_MASK_WIDTH``); each part of a cell's molecular mass expects its mass
over its own law's mean. The law by hand at two points, its limits, its closure (the mass in clouds stays the gas's),
and nothing moved with the layer off. Colombo et al. 2014's M 51 numbers are disclosed checks (the notes), not here.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core import seeds as _seeds
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import clouds as cl

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def constants():
    ms, _, _ = production()
    m = {x.name: x for x in ms}[DEFAULT_MODEL]
    return {k: v.value for k, v in m.constants.items()}


@pytest.fixture(scope="module")
def runs():
    ms, _, _ = production()
    m = {x.name: x for x in ms}[DEFAULT_MODEL]
    return run(m, grid=COARSE, layer=True), run(m, grid=COARSE, layer=False)


def test_the_factor_and_its_split_by_hand_at_two_radii(constants):
    """The constant is the source's 2.5; at 5 kpc (the inner Galaxy's law, cut 1e7) and at 12 kpc (the outer's, cut
    1.5e6) the arm's cut is M0 sqrt(2.5), the inter-arm's M0 / sqrt(2.5), their ratio 2.5 and their geometric mean M0;
    the slope and the smallest mass are the zone's."""
    c = constants
    assert c["GMC_MASS_TRUNCATION_ARM_FACTOR"] == 2.5
    assert c["R_SUN"] > 5.0 and c["R_SUN"] < 12.0
    for radius, slope, m0 in ((5.0, -1.6, 1.0e7), (12.0, -2.2, 1.5e6)):
        arm, inter, zone = cl.cut_laws(radius, c)
        assert zone == cl.law_for(radius, c) == (slope, 1.0e4, m0)
        assert arm[:2] == inter[:2] == (slope, 1.0e4)
        assert arm[2] == pytest.approx(m0 * 1.5811388300841898, rel=1e-15)
        assert inter[2] == pytest.approx(m0 / 1.5811388300841898, rel=1e-15)
        assert arm[2] / inter[2] == pytest.approx(2.5, rel=1e-15)
        assert math.sqrt(arm[2] * inter[2]) == pytest.approx(m0, rel=1e-15)
    # The means by hand (closed form of the inner law): the arm's mean cloud is the heavier - by about 1.466, worked by
    # hand: tops' M^0.4 less m^0.4, 717.8 / 485.4 = 1.479, over the M^-0.6 terms' 1.009 (S102 builder P's notes).
    a, b = -0.6, 0.4
    hand = lambda top: ((top**b - 1e4**b) / b) / ((top**a - 1e4**a) / a)  # noqa: E731
    arm, inter, _ = cl.cut_laws(5.0, c)
    assert cl.mass_function_mean(*arm) == pytest.approx(hand(1e7 * math.sqrt(2.5)), rel=1e-12)
    assert cl.mass_function_mean(*inter) == pytest.approx(hand(1e7 / math.sqrt(2.5)), rel=1e-12)
    assert cl.mass_function_mean(*arm) / cl.mass_function_mean(*inter) == pytest.approx(1.466, abs=0.002)
    # The outer law (slope -2.2) has its mean nearer the smallest mass: the step moves it less - about 1.109 by hand
    # (M^-0.2 terms 0.1054 / 0.0948 = 1.112, over the M^-1.2 terms' 1.003).
    arm, inter, _ = cl.cut_laws(12.0, c)
    assert cl.mass_function_mean(*arm) / cl.mass_function_mean(*inter) == pytest.approx(1.109, abs=0.003)


def _one_ring_shares(arm: float, inter: float) -> np.ndarray:
    shares = np.zeros((cl.CELL_RINGS, cl.CELL_SECTORS, 3))
    shares[:, :, 2] = 1.0
    shares[5, :, :] = (0.0, 0.0, 1.0)
    shares[5, 3, :] = (arm, inter, 1.0 - arm - inter)
    return shares


def test_a_cloud_s_part_and_mass_by_hand(constants, runs):
    """In a cell holding half its mass in the mask and half out of it (ring 5, sector 3), the parts' probabilities are
    their expected counts' shares, (1/2 / <M>_arm) : (1/2 / <M>_inter); a uniform below the arm's probability is the
    arm's law at u / p_arm, one above it the inter-arm's at (u - p_arm) / p_inter. A cell of the same ring wholly
    unmasked draws the zone's law at u itself, bit for bit."""
    c = constants
    R = runs[0].grid.R
    shares = _one_ring_shares(0.5, 0.5)
    rings, _ = cl.cell_edges(R)
    arm, inter, zone = cl.cut_laws(0.5 * (rings[5] + rings[6]), c)
    n_arm, n_inter = 0.5 / cl.mass_function_mean(*arm), 0.5 / cl.mass_function_mean(*inter)
    p_arm = n_arm / (n_arm + n_inter)
    u = np.array([0.25 * p_arm, p_arm + 0.5 * (1.0 - p_arm)])
    got = cl.ring_cloud_masses(u, np.array([3, 3]), 5, R, c, shares)
    assert got[0] == pytest.approx(float(cl.mass_function_sample(np.array([0.25]), *arm)[0]), rel=1e-12)
    assert got[1] == pytest.approx(float(cl.mass_function_sample(np.array([0.5]), *inter)[0]), rel=1e-12)
    v = np.linspace(0.0, 0.999, 7)
    assert np.array_equal(cl.ring_cloud_masses(v, np.full(7, 4), 5, R, c, shares), cl.mass_function_sample(v, *zone))
    # A ring the cut does not move: the zone's law, the arithmetic before S102.
    assert np.array_equal(cl.ring_cloud_masses(v, np.full(7, 3), 6, R, c, shares), cl.mass_function_sample(v, *cl.law_for(0.5 * (rings[6] + rings[7]), c)))


def test_the_limits(constants, runs):
    """A cell wholly in the mask draws the arm's law at u, wholly out of it the inter-arm's - every cloud at most its
    part's cut; no shares (the layer off) is the zone's law everywhere."""
    c = constants
    R = runs[0].grid.R
    rings, _ = cl.cell_edges(R)
    arm, inter, _ = cl.cut_laws(0.5 * (rings[5] + rings[6]), c)
    v = np.linspace(0.0, 1.0, 11)
    assert np.allclose(cl.ring_cloud_masses(v, np.full(11, 3), 5, R, c, _one_ring_shares(1.0, 0.0)), cl.mass_function_sample(v, *arm), rtol=1e-14)
    assert np.allclose(cl.ring_cloud_masses(v, np.full(11, 3), 5, R, c, _one_ring_shares(0.0, 1.0)), cl.mass_function_sample(v, *inter), rtol=1e-14)
    assert cl.ring_cloud_masses(v, np.full(11, 3), 5, R, c, _one_ring_shares(0.0, 1.0)).max() <= inter[2] * (1 + 1e-12)
    assert np.array_equal(cl.ring_cloud_masses(v, np.full(11, 3), 5, R, c, None), cl.mass_function_sample(v, *cl.law_for(0.5 * (rings[5] + rings[6]), c)))
    assert cl.inverse_means(None, R, c) is None and not cl.masked_rings(None).any()


def test_closure_the_mass_stays_the_gas_s_and_the_number_is_sub_linear(constants, runs):
    """With the layer on, on the default galaxy: the mask is laid (some rings move); every cell's three shares sum to
    1; the expected mass - each cell's expected count times its mean cloud - is each ring's molecular mass to rounding
    (the placement's weights at mean 1 round each ring); the cells' expectations sum to the ring's; an arm part expects
    fewer clouds per unit mass than an inter-arm part; and the realised census's mass is the gas's to its noise."""
    c = constants
    on, _ = runs
    F, R = on.fields, on.grid.R
    placement = cl.sector_placement(F, R, c)
    shares = cl.arm_cut(F, R, c, placement)
    assert shares is not None
    moved = cl.masked_rings(shares)
    assert moved.any() and not moved.all()
    assert np.allclose(shares.sum(axis=-1), 1.0, rtol=0, atol=1e-12) and np.all(shares >= 0.0)
    assert np.any(shares[moved][:, :, 0] > 0.0) and np.any(shares[moved][:, :, 1] > 0.0)
    expected = cl.expected_counts(F, R, c, placement=placement)
    inverse = cl.inverse_means(shares, R, c)
    ring_mass = cl.ring_molecular_mass(F["gas_molecular_surface_density"], R)
    expected_mass = np.sum(expected[moved] / inverse[moved], axis=1)
    assert np.allclose(expected_mass, ring_mass[moved], rtol=1e-12, atol=0)
    assert np.allclose(expected.sum(axis=1), cl.ring_expected(F, R, c), rtol=1e-12, atol=0)
    rings, _ = cl.cell_edges(R)
    for i in np.flatnonzero(moved):
        arm, inter, _ = cl.cut_laws(0.5 * (rings[i] + rings[i + 1]), c)
        assert 1.0 / cl.mass_function_mean(*arm) < 1.0 / cl.mass_function_mean(*inter)
    realised = float(np.sum(F["cloud_mass"]))
    assert realised == pytest.approx(float(ring_mass.sum()), rel=0.15)  # the heavy tail's noise (test_audit_iii's ensemble)
    assert F["cloud_mass_total"] == realised


def test_the_census_and_the_api_s_ring_draw_agree(constants, runs):
    """``v6_clouds.ring_cloud_dust`` re-derives each ring's masses from the streams; on a moved ring it allocates the
    sectors as the census does and reads the masses through ``ring_cloud_masses``: the census's masses ring by ring,
    the same multiset."""
    c = constants
    on, _ = runs
    F, R = on.fields, on.grid.R
    seed = int(on.inputs["systems_seed"])
    placement = cl.sector_placement(F, R, c)
    shares = cl.arm_cut(F, R, c, placement)
    weights = cl.count_weights(placement, shares, R, c)
    layout = cl.cloud_layout(F, R, seed, c)
    mass = np.asarray(F["cloud_mass"], dtype=float)
    for r, n in layout.sizes.items():
        if not n:
            continue
        sector = cl.allocate(_seeds.rng(seed, "cloud", r, "sector").random(n), None if weights is None else weights[r])
        drawn = cl.ring_cloud_masses(_seeds.rng(seed, "cloud", r, "mass").random(n), sector, r, R, c, shares)
        assert np.array_equal(np.sort(drawn), np.sort(mass[layout.ring == r])), r


def test_layer_off_nothing_moves(constants, runs, monkeypatch):
    """With the layer off no mask is laid, and the census is the arithmetic before S102 to the bit: each ring's
    expectation its molecular mass over the zone's mean, each cloud's mass the zone's law at its uniform, and the
    whole catalogue the same as with the cut removed."""
    c = constants
    _, off = runs
    F, R = off.fields, off.grid.R
    placement = cl.sector_placement(F, R, c)
    assert placement[1] is None and cl.arm_cut(F, R, c, placement) is None
    rings, _ = cl.cell_edges(R)
    ring_mass = cl.ring_molecular_mass(F["gas_molecular_surface_density"], R)
    mean = np.array([cl.mass_function_mean(*cl.law_for(0.5 * (rings[i] + rings[i + 1]), c)) for i in range(cl.CELL_RINGS)])
    assert np.array_equal(cl.ring_expected(F, R, c), ring_mass / mean)
    assert np.array_equal(cl.expected_counts(F, R, c).sum(axis=1), ring_mass / mean)
    seed = int(off.inputs["systems_seed"])
    layout = cl.cloud_layout(F, R, seed, c)
    mass = np.asarray(F["cloud_mass"], dtype=float)
    for r, n in layout.sizes.items():
        if n:
            by_hand = cl.mass_function_sample(_seeds.rng(seed, "cloud", r, "mass").random(n), *cl.law_for(0.5 * (rings[r] + rings[r + 1]), c))
            assert np.array_equal(mass[layout.ring == r], by_hand[layout.index[layout.ring == r]]), r
    now = cl.materialise_clouds(F, R, seed, c, texture=False)
    monkeypatch.setattr(cl, "arm_cut", lambda *a, **k: None)
    before = cl.materialise_clouds(F, R, seed, c, texture=False)
    assert before.counts == now.counts
    for name in now:
        assert np.array_equal(np.asarray(now[name]), np.asarray(before[name])), name
    for name in cl.CLOUD_COLUMNS + ("cloud_state",):
        if name in F and name not in cl.TEXTURE_COLUMNS:
            assert np.array_equal(np.asarray(F[name]), np.asarray(now[name])), name
