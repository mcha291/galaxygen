"""S41 (BUILD_II V4, built on Opus to the rulings proposed in docs/HANDOFF_S41.md, for Fable's ratification).

P1: a cluster is drawn as an object - a point of the light its stars sum to. Its two light columns are the light
stage's tables read at the cluster's age and [Fe/H], times its mass; never a sample (rule B8).
P5: the #69 gate extended to the object classes. Every cloud, cluster and remnant column is either read by the viewer
(the region volume's object table, frontend/src/galaxy/region.ts, or the cluster points) or listed here as not drawn
- the inventory Fable ruled on at D191: 25 drawn, 38 not (8 cloud, 24 cluster, 6 remnant; the handoff had counted 39),
and every not-drawn column's declaration carries the object-class twin of rule D4's sentence ("Not drawn by the
viewer", D191) saying why - it reaches the picture through what it sets, nothing in a filter's image sees it, or
it is owed (debts #115, #116). A new object column fails this test until it is placed in one list or the other, and
a column moved to DRAWN must lose the sentence (its module's NOT_DRAWN_WHY entry). S59 (D218): the randomness
layer's `arm_segment` class, the winding's seeded segments, joins the inventory - two columns, neither drawn.

D191's measurements, pinned: the ramp's painting (L_bol through a blackbody's share at the colour temperature) puts
about twice the population's own light through the viewer's optical filters (#114), and the clusters carry a
quarter of the disc's bolometric light while the sampled catalogue holds almost none of it (#115).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import spectra
from galaxy.stages.photometry import band_flux_at, band_nu_l_nu, correlated_temperature, population_at

ROOT = Path(__file__).resolve().parents[1]

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def coarse():
    ms, _, _ = production()
    return run(ms.get(DEFAULT_MODEL), grid=COARSE)


def test_a_clusters_light_is_its_mass_times_the_tables_at_its_age(coarse):
    F = coarse.fields
    mass = np.asarray(F["cluster_mass"], dtype=float)
    age_gyr = np.asarray(F["cluster_age"], dtype=float) / 1000.0
    feh = np.asarray(F["cluster_metallicity"], dtype=float)
    light, colour = population_at(age_gyr, feh)
    assert np.allclose(np.asarray(F["cluster_luminosity"]), mass * light, rtol=1e-12)
    assert np.array_equal(np.asarray(F["cluster_light_temperature"]), correlated_temperature(colour), equal_nan=True)
    # Young clusters are blue, old ones redder, and every one has light (0-20 Myr: no cluster is dark yet).
    T = np.asarray(F["cluster_light_temperature"], dtype=float)
    age = np.asarray(F["cluster_age"], dtype=float)
    assert np.all(np.isfinite(T)) and np.all(np.asarray(F["cluster_luminosity"]) > 0)
    assert np.median(T[age < 4]) > np.median(T[age > 15])


def test_the_ramps_painting_is_bolometric_and_the_clusters_are_a_quarter_of_the_light(coarse):
    """D191 (#114, #115). A point's channel is L_bol x a blackbody's share at T_cct (P1, the stars' convention; P6
    makes the share explicit); the population's own eight-band SED through the same curve is what V1 draws the field
    by. Summed over the census the ramp paints 1.89 / 2.12 / 2.43 times the population's R / G / B light - V1's
    "about twice" (D188) at the object grain - with the error running from +0.18 mag at the youngest to +1.31 mag at
    the oldest, so the old clusters are painted a magnitude too bright against the young. And the clusters hold
    0.236 of the disc's bolometric light on this grid (0.249 at the default grid), the young population the sampled
    catalogue barely carries; 0.47 of them by count are dissolved, holding 0.165 of the clusters' light."""
    F = coarse.fields
    L = np.asarray(F["cluster_luminosity"], dtype=float)
    T = np.asarray(F["cluster_light_temperature"], dtype=float)
    age = np.asarray(F["cluster_age"], dtype=float) / 1000.0
    feh = np.asarray(F["cluster_metallicity"], dtype=float)
    mass = np.asarray(F["cluster_mass"], dtype=float)
    state = np.asarray(F["cluster_bound"])
    rgb = spectra.parse_curves(json.loads((ROOT / "frontend/src/galaxy/filters.json").read_text(encoding="utf-8"))["sets"]["rgb"]["curves"])
    flux = band_flux_at(age, feh, spectra.SED_BANDS)
    sed = np.stack([band_nu_l_nu(flux[b], b) for b in spectra.SED_BANDS], axis=-1) * mass[:, None]  # L☉ per band
    population = spectra.stellar_response(sed, T, rgb)
    ramp = L[:, None] * spectra.blackbody_response(rgb, T)
    summed = ramp.sum(axis=0) / population.sum(axis=0)
    assert summed == pytest.approx([1.889, 2.118, 2.434], rel=2e-2), summed
    error = 2.5 * np.log10(ramp[:, 1] / population[:, 1])
    assert np.median(error[age < 0.004]) == pytest.approx(0.182, abs=0.03)
    assert np.median(error[age > 0.015]) == pytest.approx(1.309, abs=0.03)
    # S51 (D210): was 0.2516 - the clouds on the gas's ridge, another draw of the coarse grid's census (-3.2 %, inside
    # the clusters' light's 4.4 % seed-to-seed spread); S49 (D204, #126): the light integrated along the isochrone's
    # points; was 0.2358
    # S56 (D215): was 0.2436 - the ridge follows five arm modes, another draw of the coarse grid's census again
    # (+3.6 %, inside the same spread)
    # S59 (D218): was 0.2523 - the arms' winding is laid in seeded segments, so the gas is turned round each ring and
    # the clouds fall in other cells: another draw of the coarse grid's census again (+4.8 % on S58's reading,
    # 0.2489, which sat inside this pin's 2 %; 1.1 of the same spread). disc_luminosity has not moved, to the bit.
    assert L.sum() / float(F["disc_luminosity"]) == pytest.approx(0.2608, rel=2e-2)
    dissolved = state == 2
    assert dissolved.mean() == pytest.approx(0.470, abs=0.02) and L[dissolved].sum() / L.sum() == pytest.approx(0.165, abs=0.02)


# The columns the viewer reads (frontend/src/galaxy/region.ts packObjects; GalaxyTab's cluster points), and the
# naming columns every census row carries (S40).
DRAWN = {
    "cloud": {"cloud_radius", "cloud_azimuth", "cloud_height", "cloud_size", "cloud_mass", "cloud_density_pdf_width",
              "cloud_density_gradient", "cloud_gradient_angle", "cloud_cluster_index"},
    "cluster": {"cluster_radius", "cluster_azimuth", "cluster_height", "cluster_luminosity", "cluster_light_temperature",
                "hii_stromgren_radius", "hii_halpha_emissivity", "bubble_radius", "bubble_shell_thickness",
                "bubble_shell_emissivity",
                # S42: a region is coloured by all its lines (region.ts regionLineColour).
                "hii_balmer_decrement", "hii_oiii_5007_ratio", "hii_nii_6583_ratio", "hii_sii_6716_ratio", "hii_sii_6731_ratio"},
    "remnant": {"remnant_radius", "remnant_azimuth", "remnant_height", "remnant_size", "remnant_shell_thickness",
                "remnant_shell_emissivity"},
    "arm_segment": set(),  # S59 (D218): the winding's seeded segments, a new object class; the viewer reads neither column
}
# Published and not drawn (S41, ruled at D191): each carries the "Not drawn by the viewer" sentence.
NOT_DRAWN = {
    "cloud": {"cloud_velocity_dispersion", "cloud_mach_number", "cloud_age", "cloud_state", "cloud_source_offset",
              "cloud_source_angle", "cloud_metallicity", "cloud_alpha"},
    "cluster": {"cluster_mass", "cluster_half_mass_radius", "cluster_age", "cluster_bound", "cluster_metallicity",
                "cluster_ionizing_photons", "cluster_wind_luminosity", "hii_electron_density", "hii_temperature",
                "hii_ionization_parameter", "hii_clumping", "hii_halpha_luminosity",
                "hii_oxygen_abundance", "hii_nitrogen_abundance", "hii_sulphur_abundance", "hii_density_bounded",
                "bubble_shell_velocity", "bubble_shell_density", "bubble_interior_pressure", "bubble_interior_temperature",
                "bubble_mechanical_luminosity", "bubble_phase", "bubble_stalled"},
    "remnant": {"remnant_age", "remnant_shell_velocity", "remnant_ambient_density", "remnant_shell_density",
                "remnant_phase", "remnant_kind"},
    # S59 (D218): the two columns of the layer's `arm_segment` class. No route sends them to the viewer and nothing
    # draws a row; they reach the picture as the winding they set (layer/arm_phases.py NOT_DRAWN_WHY).
    "arm_segment": {"arm_segment_extent", "arm_segment_pitch_residual"},
}


def test_every_object_column_is_drawn_or_listed(model):  # the conftest runs it for every registered model
    fields = Service().handle("/api/fields", f"model={model.name}").json()["fields"]
    by_name = {f["name"]: f for f in fields}
    for of in ("cloud", "cluster", "remnant", "arm_segment"):  # S59 (D218): was the first three
        published = {f["name"] for f in fields if f["domain"] == "object" and f.get("of") == of}
        assert not DRAWN[of] & NOT_DRAWN[of], of
        assert published == DRAWN[of] | NOT_DRAWN[of], (of, sorted(published ^ (DRAWN[of] | NOT_DRAWN[of])))
        # D191: the ruling lives in the declaration (rule A9), as debt #69's does for the scalars.
        for name in NOT_DRAWN[of]:
            assert "**Not drawn by the viewer** (D191)" in by_name[name]["about"], name
        for name in DRAWN[of]:
            assert "Not drawn by the viewer" not in by_name[name]["about"], name
    # 25 / 38 at S41 (D191); S42 drew the Balmer decrement and the four forbidden-line ratios (D192).
    # S59 (D218): was 30 / 37 - the winding's two segment columns, not drawn.
    assert sum(len(v) for v in DRAWN.values()) == 30 and sum(len(v) for v in NOT_DRAWN.values()) == 39
