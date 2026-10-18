"""The molecular-cloud census (S32, BUILD_II Phase 8, D181): an object class beside stars.

Every number a ruling rests on was read from a source at S32 and entered in level0 with its
citation; the tests here check the arithmetic the census is built from, the redistribution rule
(RENDER_PHYSICS §7: the mass in clouds integrates back to the ISM's molecular mass), per-region
determinism (D60) and that both models draw the same clouds. Pinned as measurements, never as
targets (rule B5).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import clouds as cl

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {m.name: m for m in ms}


@pytest.fixture(scope="module")
def default(models):
    o = run(models[DEFAULT_MODEL])
    return o, {k: v.value for k, v in models[DEFAULT_MODEL].constants.items()}


def test_the_mass_function_arithmetic():
    """⟨M⟩ and the inverse CDF of a truncated power law, against quadrature and its own ends."""
    slope, lo, hi = -1.6, 1.0e4, 1.0e7
    m = np.geomspace(lo, hi, 200001)
    pdf = m**slope
    mean = float(np.trapezoid(m * pdf, m) / np.trapezoid(pdf, m))
    assert cl.mass_function_mean(slope, lo, hi) == pytest.approx(mean, rel=1e-4)
    u = np.linspace(0.0, 1.0, 11)
    drawn = cl.mass_function_sample(u, slope, lo, hi)
    assert drawn[0] == pytest.approx(lo) and drawn[-1] == pytest.approx(hi) and np.all(np.diff(drawn) > 0)
    # Rice et al. 2016's inner law: the mass is set by the top of the function, the count by the bottom.
    assert cl.mass_function_mean(-1.6, 1.0e4, 1.0e7) == pytest.approx(2.26e5, rel=0.02)
    assert cl.mass_function_mean(-1.6, 1.0e3, 1.0e7) < 0.3 * cl.mass_function_mean(-1.6, 1.0e4, 1.0e7)


def test_size_dispersion_and_mach_follow_the_sourced_relations(default):
    """R = √(M/πΣ) at Heyer's 42 M☉ pc⁻²; σ_v = (πGΣ/5)^½ R^½ (Heyer et al. 2009 eq. 10); c_s(10 K) ≈ 0.19 km/s."""
    o, c = default
    F = o.fields
    sigma = c["GMC_SURFACE_DENSITY"]
    assert sigma == 42.0
    assert np.allclose(F["cloud_size"], np.sqrt(F["cloud_mass"] / (math.pi * sigma)))
    assert np.allclose(F["cloud_velocity_dispersion"], np.sqrt(math.pi * cl.G_PC * sigma / 5.0 * F["cloud_size"]))
    c_s = cl.sound_speed(c["MOLECULAR_GAS_TEMPERATURE"], c["MOLECULAR_MEAN_WEIGHT"])
    assert c_s == pytest.approx(0.19, abs=0.01)  # Bergin & Tafalla 2007: 0.2 km/s at 10 K
    assert np.allclose(F["cloud_mach_number"], F["cloud_velocity_dispersion"] / c_s)
    b = c["TURBULENCE_FORCING_B"]
    assert F["cloud_forcing_parameter"] == b == 0.4
    assert np.allclose(F["cloud_density_pdf_width"] ** 2, np.log1p(b * b * F["cloud_mach_number"] ** 2))
    # Measured at S32: a 10^4 M☉ cloud is 8.7 pc across and Mach 5; the largest, 10^7, 275 pc and Mach 30.
    assert F["cloud_size"].min() == pytest.approx(8.7, abs=0.2) and F["cloud_mach_number"].min() == pytest.approx(5.3, abs=0.2)
    assert 20.0 < F["cloud_mach_number"].max() < 35.0


def test_the_census_redistributes_the_molecular_gas(default):
    """RENDER_PHYSICS §7 for clouds: the mass in clouds is the ISM's molecular mass to within the count's noise."""
    o, c = default
    F, R = o.fields, o.grid.R
    m_h2 = float(np.trapezoid(np.asarray(F["gas_molecular_surface_density"]) * 1.0e6 * 2.0 * math.pi * R, R))
    expected = cl.expected_counts(F, R, c)
    assert F["cloud_count_total"] == pytest.approx(expected.sum())
    # The expectation reproduces the molecular mass exactly, ring by ring: mean mass times expected count.
    rings, _ = cl.cell_edges(R)
    per_ring = cl.ring_molecular_mass(F["gas_molecular_surface_density"], R)
    means = np.array([cl.mass_function_mean(*cl.law_for(0.5 * (rings[i] + rings[i + 1]), c)) for i in range(cl.CELL_RINGS)])
    assert np.allclose((expected * means[:, None]).sum(axis=1), per_ring, rtol=1e-9)
    assert per_ring.sum() == pytest.approx(m_h2, rel=1e-6)
    # The realised census: within five times its own Poisson-like noise of the molecular mass.
    m = np.asarray(F["cloud_mass"])
    noise = math.sqrt(float((m * m).sum())) / m.sum()
    assert abs(F["cloud_mass_total"] / m_h2 - 1.0) < 5.0 * noise, (F["cloud_mass_total"] / m_h2, noise)
    assert F["cloud_mass_total"] == pytest.approx(m.sum())
    # Measured at S32: 16 704 clouds of 16 693 expected; 1.037 of the molecular mass at a noise of 0.035.
    assert len(m) == pytest.approx(F["cloud_count_total"], rel=0.02)
    assert 0.9 < F["cloud_mass_total"] / m_h2 < 1.1


def test_states_follow_the_sourced_phases(default):
    """Kawamura et al. 2009's 6 / 13 / 7 Myr: ages uniform over their sum, the state the phase the age falls in."""
    o, c = default
    F = o.fields
    phases = (c["GMC_PHASE_EMBEDDED"], c["GMC_PHASE_BLOWN_OPEN"], c["GMC_PHASE_DISPERSING"])
    assert F["cloud_lifetime"] == pytest.approx(sum(phases)) == 26.0
    age, state = np.asarray(F["cloud_age"]), np.asarray(F["cloud_state"])
    assert age.min() >= 0.0 and age.max() <= 26.0
    edges = np.cumsum(phases)
    assert np.all(state == np.clip(np.searchsorted(edges, age, side="right"), 0, 2))
    share = np.bincount(state, minlength=3) / state.size
    assert share == pytest.approx(np.array(phases) / 26.0, abs=0.02)
    assert tuple(cl.CLOUD_STATES) == ("embedded", "blown_open", "dispersing")


def test_per_region_determinism_and_both_models_agree(models, default):
    """D60 for clouds: cells drawn alone are the sweep's cells; the azimuthal model draws the same census."""
    o, c = default
    F, R = o.fields, o.grid.R
    # S61 (D220 item 5): was materialise_clouds(F, R, 0, c) - a layer-on census's texture is drawn on texture_seed.
    sweep = cl.materialise_clouds(F, R, 0, c, texture_seed=0)
    sweep_layout = cl.layout_of(sweep)
    # S61 (D220 item 3): a cell alone draws its ring's count and uniform arrays whole and derives its own rows only;
    # it is the sweep's cell, column for column and identity for identity, alone, beside its ring's neighbour, and
    # beside a cell of another ring.
    for cells in ([300, 301, 517], [301], [517], [301, 300]):
        part = cl.materialise_clouds(F, R, 0, c, cells=cells, texture_seed=0)
        layout = cl.layout_of(part)
        assert [cc for cc, _ in part.counts] == [cc for cc in cells if cc in dict(sweep.counts)]
        off_part = 0
        for cell, count in part.counts:
            off = sum(n for cc, n in sweep.counts if cc < cell)
            for name in cl.CLOUD_COLUMNS + ("cloud_state", "cloud_cluster_index"):
                assert np.array_equal(part[name][off_part:off_part + count], sweep[name][off:off + count]), (cells, cell, name)
            assert np.array_equal(layout.ring[off_part:off_part + count], sweep_layout.ring[off:off + count])
            assert np.array_equal(layout.index[off_part:off_part + count], sweep_layout.index[off:off + count])
            assert dict(sweep.counts)[cell] == count
            off_part += count
    # The ring's objects: each ring's count is its rows in the sweep, and within a cell they are in ring order.
    for r, n in sweep_layout.sizes.items():
        assert int((sweep_layout.ring == r).sum()) == n
    start = 0
    for cell, count in sweep.counts:
        assert np.all(np.diff(sweep_layout.index[start:start + count]) > 0) and np.all(sweep_layout.ring[start:start + count] == cell // cl.CELL_SECTORS)
        start += count
    a = run(models["azimuthal"], grid=COARSE).fields
    b = run(models[DEFAULT_MODEL], grid=COARSE).fields
    for name in cl.CLOUD_COLUMNS + ("cloud_state",):
        assert np.array_equal(a[name], b[name]), name
    # A different systems seed rerolls the clouds with the stars; the expectation does not move.
    other = run(models[DEFAULT_MODEL], {"systems_seed": 3}, grid=COARSE).fields
    assert other["cloud_count_total"] == b["cloud_count_total"]
    assert not np.array_equal(other["cloud_mass"], b["cloud_mass"])


def test_the_ring_first_draw_places_the_same_clouds(models):
    """S61 (D220 items 1-2, 4): a ring's count is one Poisson draw at the ring's expected total, which no placement
    enters, and every per-object draw an array on the ring's stream; the layer assigns the sector and the azimuth
    and nothing else. So the layer-on and layer-off censuses are the same clouds ring by ring - the same count, and
    the same radii, masses, ages and heights as multisets - and only the sector and the azimuth differ."""
    m = models[DEFAULT_MODEL]
    c = {k: v.value for k, v in m.constants.items()}
    on, off = run(m, grid=COARSE, layer=True), run(m, grid=COARSE, layer=False)
    R = on.grid.R
    assert np.array_equal(cl.ring_expected(on.fields, R, c), cl.ring_expected(off.fields, R, c))
    # The ring's expected total is the sum of its cells' expectations: to the bit off, to rounding on (I2).
    assert np.array_equal(cl.ring_expected(off.fields, R, c), cl.expected_counts(off.fields, R, c).sum(axis=1))
    assert np.allclose(cl.ring_expected(on.fields, R, c), cl.expected_counts(on.fields, R, c).sum(axis=1), rtol=1e-12, atol=0)
    seed = int(on.inputs["systems_seed"])
    lay_on, lay_off = cl.cloud_layout(on.fields, R, seed, c), cl.cloud_layout(off.fields, R, seed, c)
    assert lay_on.sizes == lay_off.sizes and sum(lay_on.sizes.values()) == len(on.fields["cloud_radius"]) == len(off.fields["cloud_radius"])
    for r in lay_on.sizes:
        here_on, here_off = lay_on.ring == r, lay_off.ring == r
        # S61 (D220 part II as amended): was "cloud_radius" - the layer places a cloud's radius within its cell too;
        # the radius the ring drew is `cloud_birth_radius`, and it is the same on and off.
        for name in ("cloud_birth_radius", "cloud_mass", "cloud_age", "cloud_height", "cloud_size", "cloud_metallicity"):
            a = np.sort(np.asarray(on.fields[name])[here_on])
            b = np.sort(np.asarray(off.fields[name])[here_off])
            assert np.array_equal(a, b), (r, name)
        # With the layer off the cloud stands at the radius its ring drew.
        assert np.array_equal(np.asarray(off.fields["cloud_radius"])[here_off], np.asarray(off.fields["cloud_birth_radius"])[here_off])
        # The same objects by identity: (ring, i) carries each cloud's draws, wherever it was allocated.
        order_on, order_off = np.argsort(lay_on.index[here_on]), np.argsort(lay_off.index[here_off])
        assert np.array_equal(np.asarray(on.fields["cloud_mass"])[here_on][order_on], np.asarray(off.fields["cloud_mass"])[here_off][order_off])
    # Layer off the sectors are uniform round the ring; layer on they follow the gas's weights.
    _, weights = cl.sector_placement(on.fields, R, c)
    assert cl.sector_placement(off.fields, R, c)[1] is None and weights is not None
    u = np.linspace(0.0, 1.0, 64, endpoint=False) + 1.0 / 128.0
    assert np.array_equal(np.bincount(cl.allocate(u, None), minlength=cl.CELL_SECTORS), np.full(cl.CELL_SECTORS, 2))
    w = np.zeros(cl.CELL_SECTORS)
    w[[3, 7]] = (1.0, 3.0)
    assert np.array_equal(np.bincount(cl.allocate(u, w), minlength=cl.CELL_SECTORS)[[3, 7]], [16, 48])
    sectors_on = np.array([cell % cl.CELL_SECTORS for cell, n in lay_on.counts for _ in range(n)])
    assert not np.array_equal(sectors_on, np.array([cell % cl.CELL_SECTORS for cell, n in lay_off.counts for _ in range(n)]))


def test_positions_and_abundances(default):
    o, c = default
    F, R = o.fields, o.grid.R
    r, phi = np.asarray(F["cloud_radius"]), np.asarray(F["cloud_azimuth"])
    assert r.min() >= R[0] and r.max() <= R[-1] and phi.min() >= 0.0 and phi.max() <= 2.0 * math.pi
    # S61 (D220 part II as amended): the abundances are read at the radius the ring drew (was `r`, the same number
    # until the layer placed a cloud within its cell); the placed radius stays in the cloud's level-0 ring.
    born = np.asarray(F["cloud_birth_radius"])
    assert np.allclose(F["cloud_metallicity"], np.interp(born, R, F["feh_gas"]))
    assert np.allclose(F["cloud_alpha"], np.interp(born, R, F["alpha_fe_gas"]))
    # Both lie in the cloud's cell's ring - the ring's radius to within one grid step (the inverse CDF is linear
    # between grid radii, and the step that holds the ring's edge carries half its weight) - so no farther apart
    # than a ring's width and a step.
    rings, _ = cl.cell_edges(R)
    assert np.all(np.abs(r - born) < (rings[1] - rings[0]) + (R[1] - R[0])) and not np.array_equal(r, born)
    # S67 (D229): the molecular layer's measured FWHM, 120 pc, an absolute thickness (was half the thin disc's scale
    # height, a guess, debt #95): the sech²(z/2h) whose FWHM that is, h = 34.04 pc, at every radius.
    h = cl.cloud_layer_height({"MOLECULAR_LAYER_FWHM": 120.0})
    assert h == pytest.approx(0.120 / 3.5254943, rel=1e-7)
    assert np.median(np.abs(F["cloud_height"])) == pytest.approx(2.0 * h * math.atanh(0.5), rel=0.15)
    # The embedded source lies inside the cloud; the gradient's steepness in [0, 1].
    assert np.all(F["cloud_source_offset"] <= F["cloud_size"] + 1e-9)
    assert np.all((F["cloud_density_gradient"] >= 0.0) & (F["cloud_density_gradient"] <= 1.0))


def test_the_cloud_layer_s_half_maximum_is_at_half_the_measured_fwhm():
    """S67 (D229), by hand: the clouds' sech²(z/2h) layer whose scale height is derived from MOLECULAR_LAYER_FWHM falls
    to half its midplane density at z = ±FWHM/2 and is above half inside it - the h is the one whose FWHM is the
    measured layer's; and the constant is level 0's 120 pc (Bronfman et al. 1988 via Ferriere 2001)."""
    from galaxy.models.level0 import LEVEL0

    fwhm = float(LEVEL0["MOLECULAR_LAYER_FWHM"].value)
    assert fwhm == 120.0 and LEVEL0["MOLECULAR_LAYER_FWHM"].unit == "pc"
    h = cl.cloud_layer_height({"MOLECULAR_LAYER_FWHM": fwhm}) * 1000.0  # pc
    assert h == pytest.approx(34.0378, abs=1e-4)

    def profile(z):
        return 1.0 / math.cosh(z / (2.0 * h)) ** 2

    assert profile(fwhm / 2.0) == pytest.approx(0.5, abs=1e-12) and profile(-fwhm / 2.0) == pytest.approx(0.5, abs=1e-12)
    assert profile(0.999 * fwhm / 2.0) > 0.5 > profile(1.001 * fwhm / 2.0)
    # The draw's clip at ±0.999999 is kept (D229 item 3): the farthest a cloud can sit is 2h·artanh(0.999999), 14.5 h.
    assert 2.0 * math.atanh(0.999999) == pytest.approx(14.51, abs=0.01)


def test_the_clouds_header_carries_the_stage_scalars(model):
    """Rule D4 keeps a catalogue stage's galaxy scalars off the viewer's scalars surface (D148); the
    census route carries them in its header instead, so a renderer reads b and the lifetime there."""
    from galaxy.api.service import Service

    s = Service()
    from galaxy.api import wire

    r = s.handle("/api/clouds", f"model={model.name}&r_min=7&r_max=9&phi_min=0&phi_max=0.5")
    assert r.status == 200
    header, _ = wire.decode(r.body)
    scalars = header["scalars"]
    assert set(scalars) == {"cloud_count_total", "cloud_forcing_parameter", "cloud_lifetime", "cloud_extinction_v"}  # S40: A_V
    # S55 (D214 section 5 as ruled at gate G1, change 4): the cloud-interior noise's octave count, lacunarity and
    # gain ride in the header under their own key, not among the scalars - they are constants of the model, not a
    # stage's fields - so a renderer reads them instead of holding them (rule D5 as amended).
    assert header["cloud_interior"] == {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
    assert scalars["cloud_extinction_v"] == pytest.approx(2.9696, abs=1e-3)  # 42 Msun/pc2 x 3/2 through Draine's V row
    assert scalars["cloud_lifetime"] == pytest.approx(26.0)
    assert 0.0 < scalars["cloud_forcing_parameter"] < 1.0
    # The same numbers /api/arrays serves when the stage itself runs; the realised mass is that route's alone.
    served, _ = wire.decode(s.handle("/api/arrays", f"model={model.name}&fields=cloud_count_total,cloud_mass_total").body)
    assert served["scalars"]["cloud_count_total"] == pytest.approx(scalars["cloud_count_total"])
    assert served["scalars"]["cloud_mass_total"] > 0.0
    fields = s.handle("/api/fields", f"model={model.name}").json()["fields"]
    for f in fields:
        if f["name"].startswith("cloud_") and f["domain"] == "galaxy":
            assert "Not shown by the viewer" in f["about"] and "rule D4" in f["about"], f["name"]



# The cells the pattern mesh is held on (ring, sector), with their total-variation distance as measured at S61: the
# worst pointwise error of all 1 024 (32 %; the bar's end, 5.21 kpc, inside ring 5's 4.71-5.65 kpc), the largest
# distance of all 1 024 (the bar's other end), the highest-contrast ridge cell (contrast 6.7), and an outer cell,
# where the mesh is exact (every cell from ring 14, 13.1 kpc, outward).
# S62 (D221 item 7 as amended): (20, 5) was 0.0 - a gas spur reaches the outer cell, so the pattern is no longer flat there.
MESH_TV = {(5, 18): 2.853e-3, (5, 2): 3.394e-3, (2, 0): 8.25e-4, (20, 5): 1.886e-6}
MESH_TV_BOUND = 5e-3


def test_the_pattern_mesh_misplaces_little_of_a_cell_s_weight(default):
    """S61 (D220; the review's finding 3): the clouds read the gas pattern on a mesh of 16 x 24 steps per level-0 cell,
    bilinear between (``census_clustering.mesh_factor``); against the point function at every lattice point of all
    1 024 cells (measured at S61) the worst point is 32 % off - ring 5, sector 18, the bar's end - but what a draw sees,
    the total-variation distance of the cell's normalised weights, is at most 3.4e-3. Held here on four cells: each
    below 5e-3, as measured to 1e-6, the outer one a spur's flank since S62 (it was exact). 0.07 s beyond the module's run (measured under the suite's
    load)."""
    from galaxy.layer import compose
    from galaxy.layer import census_clustering as CC
    from galaxy.stages.systems import cell_edges

    o, c = default
    F, R = o.fields, o.grid.R
    pattern, field = compose.gas_pattern(F, R, c), compose.census_clustering(F, c)
    rings, sectors = cell_edges(R)
    sigma_h2 = np.asarray(F["gas_molecular_surface_density"], dtype=float)
    got = {}
    for ring, sector in MESH_TV:
        cell = (float(rings[ring]), float(rings[ring + 1]), float(sectors[sector]), float(sectors[sector + 1]))
        r_mid, phi_mid = field.lattice(*cell)
        rr, pp = np.meshgrid(r_mid, phi_mid, indexing="ij")
        base = field.map(rr * np.cos(pp), rr * np.sin(pp)) * (np.interp(r_mid, R, sigma_h2) * r_mid)[:, None]
        mesh = base * CC.mesh_factor(pattern, cell, r_mid, phi_mid)
        point = base * np.maximum(pattern.contrast(r_mid, phi_mid), 0.0)
        got[(ring, sector)] = 0.5 * float(np.sum(np.abs(mesh / mesh.sum() - point / point.sum())))
    assert all(tv < MESH_TV_BOUND for tv in got.values()), got
    assert got == pytest.approx(MESH_TV, abs=1e-6), got
    assert 0.0 < got[(20, 5)] < 1e-5, got  # S62: was `== 0.0` - a spur's flank in the outer cell
