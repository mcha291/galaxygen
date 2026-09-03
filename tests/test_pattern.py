"""The bar, the arms, and the first seeded stage.

The S-spread check is here as a cheap version of the measurement recorded in
DECISIONS.md D57: ruling 3 says to run it once and leave it, so the full sweep
lives in that entry and this asserts only the conclusion it reached.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages.pattern import ARM_MULTIPLICITIES, shear_rate

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


def out(model, **inputs):
    return run(model, inputs or None)


# --- the derived half ---------------------------------------------------------


def test_the_bar_scales_with_the_disc(model):
    o = out(model)
    assert o.fields["bar_half_length"] == pytest.approx(2.0 * o.fields["thin_disc_scale_length"])
    assert 4.8 <= o.fields["bar_half_length"] <= 5.2          # row 15


def test_the_bar_length_is_reproducible_not_drawn(model):
    """Row 15 is pointwise, so it must not move with the seed — which is why D55 split the stages."""
    values = {run(model, {"pattern_seed": s}).fields["bar_half_length"] for s in range(5)}
    assert len(values) == 1


def test_the_disc_shears_like_a_flat_curve(model):
    o = out(model)
    assert 0.7 < o.fields["shear_rate"] < 1.1
    assert 0.0 < o.fields["disc_dominance"] < 1.0


def test_shear_rate_recognises_its_limiting_cases():
    """Γ is a finite difference, so the curved case carries a discretisation error."""
    R = np.linspace(0.1, 20.0, 300)
    assert shear_rate(R, 30.0 * R, 5.0) == pytest.approx(0.0, abs=1e-6)          # solid body
    assert shear_rate(R, np.full_like(R, 220.0), 5.0) == pytest.approx(1.0, abs=1e-6)  # flat
    # Keplerian is exactly 1.5; np.gradient on this spacing returns 1.4963.
    assert shear_rate(R, 500.0 / np.sqrt(R), 5.0) == pytest.approx(1.5, abs=0.01)


# --- the seeded half ----------------------------------------------------------


def test_the_pattern_is_seeded_and_reproducible(model):
    """Rule A10: seeded means reproducible given the seed, not determined by the physics."""
    a = run(model, {"pattern_seed": 7}).fields
    b = run(model, {"pattern_seed": 7}).fields
    c = run(model, {"pattern_seed": 8}).fields
    for name in ("bar_corotation_radius", "bar_pattern_speed", "pitch_angle"):
        assert a[name] == b[name], name          # reproducible
        assert a[name] != c[name], name          # and not determined


def test_the_pattern_speed_is_a_definition_not_a_draw(model):
    """Ω_b = v_c(R_CR)/R_CR exactly; all of its scatter is inherited from the fast-bar draw."""
    o = out(model)
    R_cr = o.fields["bar_corotation_radius"]
    v_cr = float(np.interp(R_cr, o.grid.R, o.fields["circular_velocity_resolved"]))
    assert o.fields["bar_pattern_speed"] == pytest.approx(v_cr / R_cr, rel=1e-12)


def test_the_bar_is_fast(model):
    o = out(model)
    ratio = o.fields["bar_corotation_radius"] / o.fields["bar_half_length"]
    assert 0.6 < ratio < 1.9      # 1.2 ± 0.2, drawn, so a few sigma either way


def test_arm_multiplicity_is_drawn_from_the_closed_set(model):
    seen = {run(model, {"pattern_seed": s}).fields["arm_multiplicity"] for s in range(30)}
    assert seen <= set(ARM_MULTIPLICITIES)
    assert len(seen) > 1, "a draw that never varies is not a draw"


def test_the_draw_dominates_the_pitch_angle(model):
    """Ruling 3's claim, and S4 measured it: 0.3% of the variance is trend (D57).

    The cheap version — the shear the model can reach barely moves, so the trend
    has almost no lever, while the draw has a 6 degree dispersion.
    """
    shears = [
        run(model, {"halo_mass": hm, "disc_spin": spin}, grid=COARSE).fields["shear_rate"]
        for hm in (3e11, 4e12) for spin in (0.010, 0.030)
    ]
    trend_spread = abs(-8.0) * (max(shears) - min(shears))
    draws = [run(model, {"pattern_seed": s}, grid=COARSE).fields["pitch_angle"] for s in range(12)]
    assert trend_spread < 2.0
    assert float(np.std(draws)) > 3.0 * trend_spread


# --- the statistical rows -----------------------------------------------------


def test_the_ensemble_is_an_ensemble_of_galaxies(model):
    """Every seed moves together, so the members differ only in their draws."""
    e = spec.ensemble(model, ("bar_pattern_speed", "bar_corotation_radius"), n=8, grid=COARSE)
    assert set(e) == {"bar_pattern_speed", "bar_corotation_radius"}
    assert all(len(v) == 8 for v in e.values())
    assert len(set(e["bar_pattern_speed"])) == 8      # every member is distinct


def test_rows_16_and_17_are_judged_statistically(model):
    results = {r.n: r for r in spec.run(model, ensemble=spec.ensemble(model))}
    for n in (16, 17):
        assert results[n].status == "pass"
        assert "central 95%" in results[n].reason and "n=20" in results[n].reason


def test_an_ensemble_too_small_is_refused(model):
    small = spec.ensemble(model, ("bar_pattern_speed",), n=5, grid=COARSE)
    results = {r.n: r for r in spec.run(model, ensemble=small, grid=COARSE)}
    assert results[16].status == "not-yet-computable"
    assert "needs >= 20" in results[16].reason
