"""S41 (BUILD_II V4, built on Opus to the rulings proposed in docs/HANDOFF_S41.md, for Fable's ratification).

P1: a cluster is drawn as an object - a point of the light its stars sum to. Its two light columns are the light
stage's tables read at the cluster's age and [Fe/H], times its mass; never a sample (rule B8).
P5: the #69 gate extended to the object classes. Every cloud, cluster and remnant column is either read by the viewer
(the region volume's object table, frontend/src/galaxy/region.ts, or the cluster points) or listed here as not drawn
yet - the inventory Fable rules on (D191): a column the viewer should draw, or one whose declaration should say why
it is not drawn, as rule D4's sentence does for a catalogue stage's scalars. A new object column fails this test
until it is placed in one list or the other.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages.photometry import correlated_temperature, population_at

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


@pytest.fixture(scope="module")
def coarse():
    ms, _, _ = production()
    return run(ms.get("basic"), grid=COARSE)


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


# The columns the viewer reads (frontend/src/galaxy/region.ts packObjects; GalaxyTab's cluster points), and the
# naming columns every census row carries (S40).
DRAWN = {
    "cloud": {"cloud_radius", "cloud_azimuth", "cloud_height", "cloud_size", "cloud_mass", "cloud_density_pdf_width",
              "cloud_density_gradient", "cloud_gradient_angle", "cloud_cluster_index"},
    "cluster": {"cluster_radius", "cluster_azimuth", "cluster_height", "cluster_luminosity", "cluster_light_temperature",
                "hii_stromgren_radius", "hii_halpha_emissivity", "bubble_radius", "bubble_shell_thickness",
                "bubble_shell_emissivity"},
    "remnant": {"remnant_radius", "remnant_azimuth", "remnant_height", "remnant_size", "remnant_shell_thickness",
                "remnant_shell_emissivity"},
}
# Published and not drawn yet (S41): Fable's inventory to rule on.
NOT_DRAWN = {
    "cloud": {"cloud_velocity_dispersion", "cloud_mach_number", "cloud_age", "cloud_state", "cloud_source_offset",
              "cloud_source_angle", "cloud_metallicity", "cloud_alpha"},
    "cluster": {"cluster_mass", "cluster_half_mass_radius", "cluster_age", "cluster_bound", "cluster_metallicity",
                "cluster_ionizing_photons", "cluster_wind_luminosity", "hii_electron_density", "hii_temperature",
                "hii_ionization_parameter", "hii_clumping", "hii_halpha_luminosity", "hii_balmer_decrement",
                "hii_oxygen_abundance", "hii_nitrogen_abundance", "hii_sulphur_abundance", "hii_density_bounded",
                "bubble_shell_velocity", "bubble_shell_density", "bubble_interior_pressure", "bubble_interior_temperature",
                "bubble_mechanical_luminosity", "bubble_phase", "bubble_stalled"},
    "remnant": {"remnant_age", "remnant_shell_velocity", "remnant_ambient_density", "remnant_shell_density",
                "remnant_phase", "remnant_kind"},
}


def test_every_object_column_is_drawn_or_listed(model):  # the conftest runs it for every registered model
    fields = Service().handle("/api/fields", f"model={model.name}").json()["fields"]
    for of in ("cloud", "cluster", "remnant"):
        published = {f["name"] for f in fields if f["domain"] == "object" and f.get("of") == of}
        assert not DRAWN[of] & NOT_DRAWN[of], of
        assert published == DRAWN[of] | NOT_DRAWN[of], (of, sorted(published ^ (DRAWN[of] | NOT_DRAWN[of])))
