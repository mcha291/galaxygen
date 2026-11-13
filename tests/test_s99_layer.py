"""S99 (#227, D268 ruling 7): the stellar layer is one height per galaxy, the mass scale length over the flattening.

Until S99 ``thin_disc_scale_height`` was the isothermal sheet's law, sigma_z^2 / (2 pi G Sigma), read at the Milky
Way's ``R_SUN`` = 8.2 kpc on every template: 926 pc on ``ngc_4414``, 4.9 of its scale lengths out, against 346 pc on
the Milky Way (register #227; ``docs/READING_DISC_HEIGHT.md``). Kregel, van der Kruit & de Grijs 2002 fit one
exponential height per galaxy over the whole disc, its constancy with radius assumed, h_R / h_z = 7.3 +/- 2.2
(volume-corrected) - ``ARM_LAYER_FLATTENING``, which the pattern stage already holds. The owner's ruling (D268, 7):
the layer's height is the stellar disc's fitted mass scale length that sfh publishes (``thin_disc_scale_length``,
not ``disc_scale_length_spin``) over that flattening, on every galaxy; the law's value at ``R_SUN`` stays published,
bit for bit, as ``thin_disc_scale_height_dynamical`` - a check on the layer, which debt #42's heating tests read.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy import templates
from galaxy.core.grids import GridSpec
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs.graph import build
from galaxy.stages import habitable_zone as hz
from galaxy.stages import ism
from galaxy.stages.vertical import scale_height

R_SUN = 8.2
HEIGHTS = ("thin_disc_scale_height", "thin_disc_scale_height_dynamical", "thin_disc_scale_length",
           "disc_scale_length_spin", "thin_disc_dispersion", "thin_disc_surface_density",
           "thick_disc_surface_density", "gas_surface_density")
GALAXIES = ("bare", "milky_way", "ngc_4414")

# What `thin_disc_scale_height` published at session-99's head (93ff47f), before the change: the law at R_SUN,
# measured on this machine (the azimuthal model, the production grid; S99 builder L's s99_L_before.json). The
# dynamical check must be these bit for bit.
BEFORE = {
    "bare": 345.89925566267607,
    "milky_way": 345.89925566267607,
    "ngc_4414": 926.4049289366312,
}


def inputs_of(galaxy: str) -> dict:
    return {} if galaxy == "bare" else templates.resolve(templates.get(galaxy))


@pytest.fixture(scope="module")
def runs(prod):
    model = prod[0].get(DEFAULT_MODEL)
    return {g: run(model, inputs_of(g), only=HEIGHTS) for g in GALAXIES}


@pytest.mark.parametrize("galaxy", GALAXIES)
def test_the_layer_is_the_mass_scale_length_over_the_flattening(prod, runs, galaxy):
    model = prod[0].get(DEFAULT_MODEL)
    f = runs[galaxy].fields
    flattening = float(model.constants["ARM_LAYER_FLATTENING"].value)
    assert flattening == 7.3
    expected = float(f["thin_disc_scale_length"]) * 1000.0 / flattening
    assert float(f["thin_disc_scale_height"]) == pytest.approx(expected, rel=1e-12)
    # The stellar fit's length, not checkpoint 1's spin length (the scout's finding; the owner's numbers).
    assert abs(float(f["thin_disc_scale_length"]) / float(f["disc_scale_length_spin"]) - 1.0) > 0.03


def test_the_owners_two_numbers(runs):
    """D268 ruling 7: 334 pc on the Milky Way, 229 pc on NGC 4414 (334.2 / 229.5 by the scout's probe)."""
    assert float(runs["milky_way"].fields["thin_disc_scale_height"]) == pytest.approx(334.19, abs=0.01)
    assert float(runs["ngc_4414"].fields["thin_disc_scale_height"]) == pytest.approx(229.47, abs=0.01)
    # The bare defaults are the Milky Way's disc: the template pins only the bar, which the height does not read.
    assert float(runs["bare"].fields["thin_disc_scale_height"]) == float(runs["milky_way"].fields["thin_disc_scale_height"])


@pytest.mark.parametrize("galaxy", GALAXIES)
def test_the_dynamical_height_is_the_law_at_r_sun(prod, runs, galaxy):
    """The check keeps the law, sigma_z^2 / (2 pi G Sigma) at R_SUN with the whole disc's Sigma there."""
    model = prod[0].get(DEFAULT_MODEL)
    o = runs[galaxy]
    f = o.fields
    total = float(np.interp(R_SUN, o.grid.R, np.asarray(f["thin_disc_surface_density"])
                            + np.asarray(f["thick_disc_surface_density"]) + np.asarray(f["gas_surface_density"])))
    law = float(scale_height(f["thin_disc_dispersion"], total, float(model.constants["G"].value))) * 1000.0
    assert float(f["thin_disc_scale_height_dynamical"]) == pytest.approx(law, rel=1e-12)


@pytest.mark.machine_pinned
@pytest.mark.parametrize("galaxy", GALAXIES)
def test_the_dynamical_height_is_what_the_layer_published_before_s99_bit_for_bit(runs, galaxy):
    assert float(runs[galaxy].fields["thin_disc_scale_height_dynamical"]) == BEFORE[galaxy]


def test_one_height_per_galaxy_whatever_the_call(prod):
    """Not a draw and not a profile: one scalar, the same however the run is asked for it - alone, with the layer
    off, on other seeds, inside a run of its readers."""
    models, _, table = prod
    model = models.get(DEFAULT_MODEL)
    only = ("thin_disc_scale_height",)
    alone = run(model, only=only).fields["thin_disc_scale_height"]
    assert np.ndim(alone) == 0
    off = run(model, only=only, layer=False).fields["thin_disc_scale_height"]
    seeds = {n: 7 for n, i in table.items() if i.kind == "seed"}
    assert seeds
    seeded = run(model, seeds, only=only).fields["thin_disc_scale_height"]
    readers = run(model, only=("gas_midplane_pressure", "sterilization_rate_history")).fields["thin_disc_scale_height"]
    assert float(alone) == float(off) == float(seeded) == float(readers)


def test_every_reader_reads_the_one_scalar(prod):
    """The readers (#227: dust, ism, bright, systems, habitable_zone; the render through the API) require the field;
    no stage but the vertical slot's publishes it, and none reads the dynamical check."""
    models, impls, table = prod
    graph = build(models.get(DEFAULT_MODEL), impls, table)
    publishers = [st.id for st in graph.order if any(d.name == "thin_disc_scale_height" for d in st.publishes)]
    assert publishers == ["vertical_alpha"]
    readers = {st.id for st in graph.order if "thin_disc_scale_height" in st.requires}
    assert {"ism", "dust", "habitable_zone"} <= readers
    assert not [st.id for st in graph.order if "thin_disc_scale_height_dynamical" in st.requires]
    vertical = next(st for st in graph.order if st.id == "vertical_alpha")
    assert "ARM_LAYER_FLATTENING" in vertical.reads_constants and "thin_disc_scale_length" in vertical.requires


@pytest.mark.parametrize("galaxy", ("bare", "ngc_4414"))
def test_the_readers_follow_the_layer(prod, galaxy):
    """ism's midplane pressure and the hazard's 4h read the layer's height, not the check."""
    model = prod[0].get(DEFAULT_MODEL)
    c = model.constants
    f = run(model, inputs_of(galaxy), only=("gas_midplane_pressure", "sterilization_rate_history",
                                            "stellar_surface_density")).fields
    h = float(f["thin_disc_scale_height"])
    assert h != float(f["thin_disc_scale_height_dynamical"])
    p = ism.midplane_pressure(np.asarray(f["gas_surface_density"]), np.asarray(f["stellar_surface_density"]), h,
                              float(c["H2_GAS_DISPERSION"].value))
    assert np.allclose(f["gas_midplane_pressure"], p, rtol=1e-12, atol=0.0)
    d_cc = c["STERILIZATION_DISTANCE"].value / 1000.0
    d_ia = hz.sterilization_distance(c["IA_ABSOLUTE_MAGNITUDE"].value, c["STERILIZATION_DISTANCE"].value,
                                     c["STERILIZATION_MAGNITUDE"].value) / 1000.0
    expect = (np.asarray(f["core_collapse_rate_history"]) * d_cc**3 + np.asarray(f["type_ia_rate_history"]) * d_ia**3) \
        * (4.0 / 3.0 * math.pi) / (4.0 * h / 1000.0)
    assert np.allclose(f["sterilization_rate_history"], expect, rtol=1e-12, atol=0.0)


def test_the_two_models_agree_as_they_did(prod):
    """azimuthal swaps only the sfh slot for one that publishes every field sfh does: the layer and its check read
    the same on both models, as the old layer did."""
    models = prod[0]
    a = run(models.get("azimuthal"), only=HEIGHTS).fields
    b = run(models.get("basic"), only=HEIGHTS).fields
    for k in ("thin_disc_scale_height", "thin_disc_scale_height_dynamical", "thin_disc_scale_length"):
        assert float(a[k]) == float(b[k]), k


# S100 (D270, the gate's ruling): where the history's fit publishes no length the layer is the dynamical law's.
# sfh.fit_scale_length needs three rings with stars inside 1 kpc < R < 3 R_d; helpers.TINY's eight rings (3.75 kpc
# wide) put two there, so the fitted length is NaN, and from S99 to S100 the layer's height was NaN with it: the gas
# height NaN on every ring and the gas fluctuation field raising (its own rule: a field needs one published height).
# The fallback is the law the model held until S99 (74.6 pc on TINY, as at 93ff47f); it is flagged to the owner.
TINY = GridSpec(n_R=8, n_t=5, n_z=4, n_phi=6)
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)


@pytest.mark.parametrize("model_name", ("azimuthal", "basic"))
def test_s100_on_a_grid_too_coarse_for_the_fit_the_layer_is_the_dynamical_height(prod, model_name):
    model = prod[0].get(model_name)
    f = run(model, None, TINY, only=HEIGHTS).fields
    assert math.isnan(float(f["thin_disc_scale_length"]))
    h = float(f["thin_disc_scale_height"])
    assert math.isfinite(h)
    assert h == float(f["thin_disc_scale_height_dynamical"])
    assert h == pytest.approx(74.611296, abs=1e-6)
    # And a full run completes (it raised from S99 to S100), the gas published on at least one ring.
    out = run(model, None, TINY)
    assert np.isfinite(np.asarray(out.fields["gas_scale_height"], dtype=float)).any()


@pytest.mark.parametrize("galaxy", (*GALAXIES, "bare_small"))
def test_s100_where_the_fit_publishes_a_length_the_layer_is_it_over_the_flattening_bit_for_bit(prod, runs, galaxy):
    if galaxy == "bare_small":
        f = run(prod[0].get(DEFAULT_MODEL), None, SMALL, only=HEIGHTS).fields
    else:
        f = runs[galaxy].fields
    length = float(f["thin_disc_scale_length"])
    assert math.isfinite(length) and length > 0.0
    assert float(f["thin_disc_scale_height"]) == length * 1000.0 / 7.3
