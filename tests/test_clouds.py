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
from galaxy.run import run
from galaxy.stages import clouds as cl

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {m.name: m for m in ms}


@pytest.fixture(scope="module")
def default(models):
    o = run(models["basic"])
    return o, {k: v.value for k, v in models["basic"].constants.items()}


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
    sweep = cl.materialise_clouds(F, R, 0, c)
    part = cl.materialise_clouds(F, R, 0, c, cells=[300, 301, 517])
    off_part = 0
    for cell, count in part.counts:
        off = sum(n for cc, n in sweep.counts if cc < cell)
        for name in cl.CLOUD_COLUMNS + ("cloud_state",):
            assert np.array_equal(part[name][off_part:off_part + count], sweep[name][off:off + count]), (cell, name)
        off_part += count
    a = run(models["azimuthal"], grid=COARSE).fields
    b = run(models["basic"], grid=COARSE).fields
    for name in cl.CLOUD_COLUMNS + ("cloud_state",):
        assert np.array_equal(a[name], b[name]), name
    # A different systems seed rerolls the clouds with the stars; the expectation does not move.
    other = run(models["basic"], {"systems_seed": 3}, grid=COARSE).fields
    assert other["cloud_count_total"] == b["cloud_count_total"]
    assert not np.array_equal(other["cloud_mass"], b["cloud_mass"])


def test_positions_and_abundances(default):
    o, c = default
    F, R = o.fields, o.grid.R
    r, phi = np.asarray(F["cloud_radius"]), np.asarray(F["cloud_azimuth"])
    assert r.min() >= R[0] and r.max() <= R[-1] and phi.min() >= 0.0 and phi.max() <= 2.0 * math.pi
    assert np.allclose(F["cloud_metallicity"], np.interp(r, R, F["feh_gas"]))
    assert np.allclose(F["cloud_alpha"], np.interp(r, R, F["alpha_fe_gas"]))
    # Half the thin disc's scale height, stated as a guess (debt #95).
    h = 0.5 * F["thin_disc_scale_height"] / 1000.0
    assert np.median(np.abs(F["cloud_height"])) == pytest.approx(2.0 * h * math.atanh(0.5), rel=0.15)
    # The embedded source lies inside the cloud; the gradient's steepness in [0, 1].
    assert np.all(F["cloud_source_offset"] <= F["cloud_size"] + 1e-9)
    assert np.all((F["cloud_density_gradient"] >= 0.0) & (F["cloud_density_gradient"] <= 1.0))


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
    assert set(scalars) == {"cloud_count_total", "cloud_forcing_parameter", "cloud_lifetime"}
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

