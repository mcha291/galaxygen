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
    # Not zero with n = 0: the accretion timescale is then the same everywhere, but the
    # surface density still falls outwards and that alone tilts the enrichment.
    assert grads[0] == pytest.approx(-0.011, abs=0.003)
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
    # Measured, so a change is loud. S3's more compact infall raised this from 0.28
    # to 0.52 — a steeper surface density does more of the tilting — so differential
    # infall now supplies about half of it rather than seven tenths.
    assert spread(0.0) < 0.7 * spread(1.0)
    assert spread(0.0) / spread(1.0) == pytest.approx(0.52, abs=0.08)


def test_migration_flattens_old_stars_and_leaves_gas_alone(model):
    """Row 22 must not see migration and row 23 must (D48)."""
    none = out(model, migration_efficiency=0.0)
    lots = out(model, migration_efficiency=7.0)
    assert none.fields["metallicity_gradient"] == pytest.approx(lots.fields["metallicity_gradient"])
    assert abs(lots.fields["metallicity_gradient_old"]) < abs(none.fields["metallicity_gradient_old"])
    assert lots.fields["metallicity_gradient_old"] > none.fields["metallicity_gradient_old"]


def test_migration_over_flattens_the_old_population(model):
    """A coupling S3 exposed by fixing the disc size, not by touching migration.

    At S2 the young/old gradient ratio was 2.3 against an observed 1.75, and the
    kernel looked about right. S3 corrected the infall extent (debt #13), the
    stellar disc shrank from 3.74 to 2.52 kpc, and the same 3.6 kpc kernel now
    smooths across most of the disc: the ratio is 4.6. The kernel's effect depends
    on the disc it acts on, so its strength cannot be judged independently of the
    structure — which is why this is recorded against debt #15 rather than fixed
    by moving migration_efficiency to whatever reproduces 1.75.
    """
    o = out(model)
    young, old = o.fields["metallicity_gradient_young"], o.fields["metallicity_gradient_old"]
    assert abs(old) < abs(young)
    assert young / old == pytest.approx(4.6, abs=0.5)


def test_metallicity_rises_then_is_slightly_diluted_late(model):
    """Late primordial infall outpacing a fading star formation rate is real, not a bug.

    The rise is the whole history; the small late decline is dilution winning once
    the gas is depleted enough that the Kennicutt-Schmidt rate has fallen away while
    accretion is still going on. It is worth pinning because a *large* decline would
    be a sign integration had gone wrong.
    """
    o = out(model)
    z = o.fields["metallicity_history"]
    at_sun = int(np.argmin(np.abs(o.grid.R - R_SUN)))
    track = z[at_sun]
    assert track[0] == 0.0  # primordial infall: the model starts with no metals
    assert np.all(z >= 0.0)
    assert track[-1] > 0.9 * track.max()  # the decline is slight, not a collapse
    decline = float(track.max() - track[-1]) / track.max()
    assert decline < 0.02, decline


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
