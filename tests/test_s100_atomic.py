"""S100 (#130; D270): the atomic gas's own steady response to the arms, and the blend that places the diffuse gas and
the dust.

The gas pattern stage solves the same equation a second time at ``HI_DISPERSION_RATIO`` (1.4, Mogotsi et al. 2016's
sigma_HI / sigma_CO on matched pixels) times ``GAS_DISPERSION`` and publishes its exact cell means, with the bar's
lanes and without spurs, as ``atomic_gas_density_contrast``. The ``spurs`` stage, after the ism stage, places the gas
by the blend f g_mol + (1 - f) g_atom, f the ring's molecular fraction, and composes the spurs on the blend. The clouds
and the star formation law keep the molecular response bit for bit.

What is held here: the atomic response's ring mean; the molecular response's bits; the blend's ring mean; the blend
equal to the molecular contrast where f is 1 and to the atomic where f is 0; the published placement the blend, the
spurs composed on it, and the render's unspurred placement the same blend; the gate's check (ruling 3: the atomic
response's ratio of means against the molecular one's, beside Querejeta et al. 2024's "typically ~10 % lower"),
recorded as measured and never judged."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy import templates
from galaxy.api import v7_layer as v7
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import gas_pattern as gm
from galaxy.stages import spurs as sp

TEMPLATES = ("milky_way", "ngc_4414")
RATIO_HAND = 1.4  # Mogotsi et al. 2016, abstract: "a mean dispersion ratio sigmaHI/sigmaCO=1.4+/-0.2, independent of radius"
SOUND_SPEED_HAND = 6.0  # km/s, the model's GAS_DISPERSION, written here
MASK_WIDTH = 1.5  # kpc: the disclosed check's mask (tests/gas_check.py's GAS_ARM_MASK_WIDTH)
ATOMIC = "atomic_gas_density_contrast"
FIELDS = ("gas_density_contrast", "star_formation_gas_contrast", ATOMIC, "gas_molecular_fraction_profile",
          *sp.SPUR_FIELDS, *gm.GAS_PATTERN_READS)
_RUNS: dict[object, object] = {}


@pytest.fixture(scope="module")
def model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict:
    return {k: c.value for k, c in model.constants.items()}


def template_run(model, template: str, layer: bool = True):
    key = (template, layer)
    if key not in _RUNS:
        _RUNS[key] = run(model, templates.overrides(templates.TEMPLATES[template]), only=FIELDS, layer=layer)
    return _RUNS[key]


def test_the_ratio_is_the_measured_one_and_the_stage_s_own_read(model):
    c = model.constants["HI_DISPERSION_RATIO"]
    assert c.value == RATIO_HAND and c.unit == "dimensionless"
    assert "Mogotsi et al. 2016" in c.about and "[verified:" in c.about
    assert constants(model)["GAS_DISPERSION"] == SOUND_SPEED_HAND
    stage = gm.GAS_PATTERN
    assert "HI_DISPERSION_RATIO" in stage.reads_constants and "HI_DISPERSION_RATIO" not in gm.GAS_PATTERN_CONSTANTS
    assert [d.name for d in stage.publishes] == ["star_formation_gas_contrast", ATOMIC]
    a, g = gm.ATOMIC_GAS_DENSITY_CONTRAST, gm.GAS_DENSITY_CONTRAST
    assert (a.axes, a.unit, a.provenance, a.composed, a.neutral) == (g.axes, g.unit, g.provenance, g.composed, g.neutral)
    assert set(gm.BLEND_READS) <= set(sp.SPURS.requires)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_atomic_response_has_ring_mean_one_and_is_the_law_at_the_atomic_dispersion(model, template):
    o = template_run(model, template)
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    a = np.asarray(F[ATOMIC], dtype=float)
    assert np.all(np.isfinite(a)) and np.all(a >= 0.0)
    assert float(np.max(np.abs(a.mean(axis=1) - 1.0))) <= 2e-13
    gp = compose.gas_pattern(F, R, constants(model))
    atomic = gp.atomic(RATIO_HAND)
    assert atomic.sound_speed == pytest.approx(RATIO_HAND * SOUND_SPEED_HAND, rel=1e-15)
    assert np.array_equal(a, atomic.unspurred_cell_means(R, edges))
    # The atomic gas's pressure reaches further against the same pull: its rings are not the molecular one's.
    on = gp.carries
    assert on.any() and not np.array_equal(atomic.profiles[on], gp.profiles[on])
    assert np.array_equal(atomic.forcing(), gp.forcing())  # the same forcing (kept once)


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_molecular_response_keeps_its_bits(model, template):
    """The clouds read the pattern ``compose`` builds from fields, which is the molecular one; the star formation
    contrast is its cell means, solved afresh (no cache) to the same bits after the atomic solve."""
    o = template_run(model, template)
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    gp = compose.gas_pattern(F, R, constants(model))
    assert gp.sound_speed == SOUND_SPEED_HAND
    gm.forget_solutions()
    fresh = compose.gas_pattern(F, R, constants(model))
    assert np.array_equal(np.asarray(F["star_formation_gas_contrast"]), fresh.star_formation_cell_means(R, edges))
    assert np.array_equal(fresh.profiles, gp.profiles)


def test_the_blend_is_the_molecular_where_f_is_one_and_the_atomic_where_f_is_zero():
    rng = np.random.default_rng(130)
    mol, atom = rng.uniform(0.2, 3.0, (5, 16)), rng.uniform(0.2, 3.0, (5, 16))
    mol /= mol.mean(axis=1, keepdims=True)
    atom /= atom.mean(axis=1, keepdims=True)
    f = np.array([1.0, 0.0, 0.3, np.nan, 0.75])
    b = gm.placed_gas_contrast(mol, atom, f)
    assert np.array_equal(b[0], mol[0]) and np.array_equal(b[1], atom[1]) and np.array_equal(b[3], mol[3])
    assert np.allclose(b[2], 0.3 * mol[2] + 0.7 * atom[2], rtol=0.0, atol=1e-15)
    assert float(np.max(np.abs(b.mean(axis=1) - 1.0))) <= 1e-15


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_placement_is_the_blend_with_the_spurs_composed_on_it(model, template):
    o = template_run(model, template)
    F, R, edges = o.fields, o.grid.R, o.grid["phi"].edges
    gp = compose.gas_pattern(F, R, constants(model))
    f = np.asarray(F["gas_molecular_fraction_profile"], dtype=float)
    assert np.all(np.isfinite(f)) and np.all((f >= 0.0) & (f <= 1.0))
    blend = gm.placed_gas_contrast(gp.unspurred_cell_means(R, edges), F[ATOMIC], f)
    want = blend if gp.spurs is None else gp.spurs.compose_cells(R, edges, blend)
    g = np.asarray(F["gas_density_contrast"], dtype=float)
    assert np.array_equal(g, want)
    assert float(np.max(np.abs(g.mean(axis=1) - 1.0))) <= 2e-13 and np.all(g >= 0.0)
    # The render's unspurred placement is the same blend: composed with the spurs it is the placement to the bit.
    unspurred = v7.unspurred_placement(F, constants(model), R, edges)
    if gp.spurs is None:
        assert unspurred is None or np.array_equal(unspurred, np.maximum(blend, 0.0))
    else:
        assert np.array_equal(unspurred, np.maximum(blend, 0.0))
        assert np.array_equal(gp.spurs.compose_cells(R, edges, unspurred), np.maximum(g, 0.0))
    # Not the molecular placement any more where the disc holds atomic gas and arms.
    assert not np.array_equal(g, gp.cell_means(R, edges))


@pytest.mark.parametrize("template", TEMPLATES)
def test_with_the_layer_off_both_are_one(model, template):
    o = template_run(model, template, layer=False)
    assert np.all(np.asarray(o.fields[ATOMIC]) == 1.0) and np.all(np.asarray(o.fields["gas_density_contrast"]) == 1.0)


# The gate's check (ruling 3), disclosed and never judged: over 6-10 kpc the median ratio of means of the atomic
# response (the source's 1.5 kpc arm mask) and of the molecular one, and the median of their ring-by-ring quotient.
# Querejeta et al. 2024 (A&A 687, A293) measure the HI's contrast "typically ~10 % lower" than the H2's at a matched
# beam; S86's probe put the model's about 5 % under at 10 km/s. Recorded as measured at S100 (layer on, the
# production grid); a re-pin keeps the old numbers in its comment.
# (molecular median, atomic median, median of atomic / molecular): the atomic response 2.6 % and 1.9 % under the
# molecular one, ring by ring 1.5-3.6 % and 0.3-2.9 % - the sign of the source's, a quarter of its size.
CHECK_AS_MEASURED = {
    "milky_way": (1.431098351042905, 1.3994854586866592, 0.9744118269883251),
    "ngc_4414": (1.4294191678180297, 1.404955697896947, 0.9814358026650689),
}


@pytest.mark.parametrize("template", TEMPLATES)
def test_the_check_atomic_against_molecular_as_measured(model, template):
    o = template_run(model, template)
    R = o.grid.R
    gp = compose.gas_pattern(o.fields, R, constants(model))
    band = (R >= 6.0) & (R <= 10.0) & gp.carries
    mol = gp.arm_ratio(MASK_WIDTH)[band]
    atom = gp.atomic(RATIO_HAND).arm_ratio(MASK_WIDTH)[band]
    quotient = atom / mol
    got = (float(np.median(mol)), float(np.median(atom)), float(np.median(quotient)))
    print(f"{template}: ratio of means 6-10 kpc, molecular {got[0]:.4f}, atomic {got[1]:.4f}; atomic / molecular median "
          f"{got[2]:.4f} ({quotient.min():.4f} to {quotient.max():.4f}) - {100.0 * (1.0 - got[2]):.1f} % under")
    want = CHECK_AS_MEASURED[template]
    assert want is not None, got
    assert got == pytest.approx(want, rel=1e-6)
