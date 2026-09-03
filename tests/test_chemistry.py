"""Chemistry: the gradient, what sets it, and what does not.

The central measurement here is a negative one. The gradient is *exactly*
insensitive to the yield, which kills the obvious explanation for it being too
flat and pins the blame on the infall law instead (rule B4).
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.core.registry import INPUTS, Constant, Model
from galaxy.run import run
from galaxy.stages.chemistry import GRADIENT_FIT_RANGE, gradient

R_SUN = 8.2


def out(model, **inputs):
    return run(model, inputs or None)


def with_constant(model, name, value):
    c = dict(model.constants)
    c[name] = Constant(value, c[name].unit, "probe")
    return Model(name="probe", about="probe", stages=model.stages, constants=c)


def test_the_solar_neighbourhood_comes_out_solar(model):
    """What the effective yield is set by, and the only thing it is set by (D47)."""
    o = out(model)
    feh_sun = float(np.interp(R_SUN, o.grid.R, o.fields["feh_gas"]))
    assert abs(feh_sun) < 0.1


def test_the_gradient_does_not_depend_on_the_yield(model):
    """The measurement behind debt #15: the yield sets the level, the infall sets the tilt.

    This is why calibrating NET_YIELD costs no acceptance row — and why the flat
    gradient cannot be blamed on the yield being wrong.
    """
    grads, levels = [], []
    for y in (0.005, 0.011, 0.035):
        o = run(with_constant(model, "NET_YIELD", y))
        grads.append(o.fields["metallicity_gradient"])
        levels.append(float(np.interp(R_SUN, o.grid.R, o.fields["feh_gas"])))
    assert max(grads) - min(grads) < 1e-6, grads
    # ...while the level moves by exactly the log of the yield ratio.
    assert levels[2] - levels[0] == pytest.approx(np.log10(0.035 / 0.005), abs=0.02)


def test_the_gradient_is_set_by_the_inside_out_index(model):
    """Steeper inside-out growth, steeper gradient — and n near 3 would be needed for −0.06."""
    grads = [out(model, inside_out_index=n)["metallicity_gradient"] if False else
             out(model, inside_out_index=n).fields["metallicity_gradient"] for n in (0.0, 1.0, 2.0)]
    assert grads[0] > grads[1] > grads[2]
    assert grads[0] == pytest.approx(0.0, abs=0.005)  # no inside-out growth, no gradient
    # The observed −0.06 is out of reach of the cited n = 1 (debt #15).
    assert grads[1] > -0.049


def test_infall_dilution_is_what_tilts_it(model):
    """Turn the tilt off by making the accretion timescale radius-independent."""
    lo, hi = GRADIENT_FIT_RANGE

    def spread(n):
        o = out(model, inside_out_index=n)
        w = (o.grid.R > lo) & (o.grid.R < hi)
        feh = o.fields["feh_gas"][w]
        return float(np.nanmax(feh) - np.nanmin(feh))

    # Not "no spread": with n = 0 the accretion timescale is the same everywhere but
    # the surface density still falls outwards, so some enrichment contrast survives.
    # Measured, so that a change is loud: it is about 28% of the n = 1 spread, i.e.
    # differential infall supplies roughly seven tenths of the tilt and the falling
    # surface density the rest.
    assert spread(0.0) < 0.4 * spread(1.0)
    assert spread(0.0) / spread(1.0) == pytest.approx(0.28, abs=0.06)


def test_migration_flattens_old_stars_and_leaves_gas_alone(model):
    """Row 22 must not see migration and row 23 must (D48)."""
    none = out(model, migration_efficiency=0.0)
    lots = out(model, migration_efficiency=7.0)
    assert none.fields["metallicity_gradient"] == pytest.approx(lots.fields["metallicity_gradient"])
    assert abs(lots.fields["metallicity_gradient_old"]) < abs(none.fields["metallicity_gradient_old"])
    assert lots.fields["metallicity_gradient_old"] > none.fields["metallicity_gradient_old"]


def test_old_stars_are_flatter_than_young_ones(model):
    o = out(model)
    young, old = o.fields["metallicity_gradient_young"], o.fields["metallicity_gradient_old"]
    assert abs(old) < abs(young)
    # Both are about a third of the observed values, but their *ratio* is close to
    # the observed 0.07/0.04 = 1.75 — so the kernel is roughly right and the
    # gradient it flattens is not (debt #15).
    assert 1.5 < young / old < 3.0


def test_metallicity_rises_and_never_runs_backwards(model):
    o = out(model)
    z = o.fields["metallicity_history"]
    at_sun = int(np.argmin(np.abs(o.grid.R - R_SUN)))
    assert np.all(np.diff(z[at_sun]) >= -1e-12)
    assert z[at_sun][0] == 0.0  # primordial infall: the model starts with no metals
    assert np.all(z >= 0.0)


def test_absent_metals_are_not_shown_as_a_number(model):
    """Rule B9: a cell with no metals is −inf or nan, never a floor that reads as measured."""
    o = out(model)
    feh = o.fields["feh_history"]
    assert np.isnan(feh[:, 0]).all()
    assert not np.isnan(o.fields["feh_gas"][o.grid.R < 20.0]).any()


def test_the_gradient_converges(model):
    grads = [
        run(model, grid=GridSpec(n_R=nr, n_t=nt, n_z=6)).fields["metallicity_gradient"]
        for nr, nt in ((200, 1000), (400, 2000), (800, 2000), (400, 4000))
    ]
    assert (max(grads) - min(grads)) / abs(np.mean(grads)) < 0.02, grads


def test_the_fit_range_is_where_gradients_are_measured():
    assert GRADIENT_FIT_RANGE == (4.0, 12.0)
    R = np.linspace(0.1, 30.0, 300)
    assert gradient(-0.06 * R, R) == pytest.approx(-0.06)
    assert np.isnan(gradient(np.full_like(R, np.nan), R))
