"""The thin/thick split, and the compensation the gate hides.

Row 9 passes. It passes for the wrong reason, and that is asserted here so that
nobody reads the green as a working thick disc (debt #19).
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import MergerEvent
from galaxy.run import run
from galaxy.stages.vertical import scale_height

R_SUN = 8.2


def out(model, **inputs):
    return run(model, inputs or None)


# The simple model's split is the merger; the advanced model's is the [α/Fe]
# valley, and at S9 there is no valley (debt #27), so its thick disc is empty.
MERGER_SPLIT = {"simple": True, "advanced": False}


def test_the_gate_passes(model):
    o = out(model)
    if MERGER_SPLIT[model.name]:
        assert 0.08 <= o.fields["thick_thin_surface_density_ratio"] <= 0.16
    else:
        assert o.fields["thick_thin_surface_density_ratio"] == 0.0  # recorded, not hidden (row 9)


def test_the_gate_passes_on_two_errors_cancelling(model):
    """Debt #19. Shrinking the thick disc to its observed mass collapses the ratio.

    If these two moved independently, gas_fraction could fix row 11 and leave row 9
    alone. They do not, because the thick disc is far too centrally concentrated.
    """
    if not MERGER_SPLIT[model.name]:
        pytest.skip("the advanced model has no thick disc to compensate with (debt #27)")
    o = out(model)
    assert o.fields["thick_disc_stellar_mass"] > 9.0e9      # row 11 fails high
    assert o.fields["thick_disc_scale_length"] < 1.8        # row 5 fails low
    richer = out(model, mergers=(MergerEvent(3.8, 0.25, 0.8, "probe"),))
    assert 3.0e9 <= richer.fields["thick_disc_stellar_mass"] <= 9.0e9   # row 11 now passes
    assert richer.fields["thick_thin_surface_density_ratio"] < 0.08     # ...and row 9 breaks


def test_no_major_merger_means_no_thick_disc(model):
    """Simple: the split *names* the merger, so this is circular (debt #20). Advanced: it is a result."""
    free = out(model, mergers=())
    assert free.fields["thick_disc_stellar_mass"] == 0.0
    assert free.fields["thick_thin_surface_density_ratio"] == 0.0
    assert free.fields["thin_disc_stellar_mass"] == pytest.approx(free.fields["stellar_mass_total"], rel=0.02)
    if not MERGER_SPLIT[model.name]:
        assert free.fields["alpha_sequence"] == "single"  # debt #9's answer, from a criterion that never named the merger


def test_the_thick_disc_is_hotter_than_the_thin_one(model):
    if not MERGER_SPLIT[model.name]:
        pytest.skip("no thick disc in the advanced model at S9 (debt #27)")
    o = out(model)
    assert o.fields["thick_disc_dispersion"] > 2.0 * o.fields["thin_disc_dispersion"]
    assert o.fields["thick_disc_scale_height"] > 3.0 * o.fields["thin_disc_scale_height"]


def test_scale_heights_are_arithmetic_from_the_dispersions(model):
    """Verdict A: h_z has no freedom once sigma_z and Sigma exist."""
    o = out(model)
    R = o.grid.R
    total = float(np.interp(R_SUN, R, o.fields["thin_disc_surface_density"]
                            + o.fields["thick_disc_surface_density"]
                            + o.fields["gas_surface_density"]))
    for disp, height in (("thin_disc_dispersion", "thin_disc_scale_height"),
                         ("thick_disc_dispersion", "thick_disc_scale_height")):
        if o.fields[disp] == 0.0:
            assert o.fields[height] == 0.0  # an empty population has no height, not a small one
            continue
        expected = float(scale_height(o.fields[disp], total)) * 1000.0
        assert o.fields[height] == pytest.approx(expected, rel=1e-9)


def test_rows_8_and_9_are_not_independent(model):
    """Row 8 is row 9 divided by the scale-height ratio, so they cannot be tuned apart."""
    o = out(model)
    f = o.fields
    if f["thick_disc_scale_height"] == 0.0:
        assert f["thick_thin_local_density_ratio"] == 0.0
        return
    assert f["thick_thin_local_density_ratio"] == pytest.approx(
        f["thick_thin_surface_density_ratio"] * f["thin_disc_scale_height"] / f["thick_disc_scale_height"]
    )


def test_the_populations_add_up_to_the_stellar_mass(model):
    o = out(model)
    f = o.fields
    total = f["thin_disc_stellar_mass"] + f["thick_disc_stellar_mass"]
    assert total == pytest.approx(f["stellar_mass_total"], rel=0.02)
