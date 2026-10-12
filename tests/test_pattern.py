"""The bar, the arms, and the first seeded stage.

The S-spread check is here as a cheap version of the measurement recorded in
DECISIONS.md D57: ruling 3 says to run it once and leave it, so the full sweep
lives in that entry and this asserts only the conclusion it reached.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.layer import compose
from galaxy.run import run
from galaxy.specs import spec
from galaxy.stages.pattern import AMPLITUDE_FIELDS, ARM_MULTIPLICITIES, shear_rate
from galaxy.stages.pieces import ArmPattern  # S60 (D219): the pattern object lives with the pieces

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)


def out(model, **inputs):
    return run(model, inputs or None)


# --- the derived half ---------------------------------------------------------


def test_the_bar_scales_with_the_disc(model):
    o = out(model)
    # The lambda_d scale length since S25, when the pattern moved ahead of star formation (D174);
    # the thin disc's fitted stellar one, a star-formation result, until then.
    assert o.fields["bar_half_length"] == pytest.approx(2.0 * o.fields["disc_scale_length_spin"])
    # Row 15: 5.2097 since S25, out by 0.01 and a recorded miss (debt #80); 4.8828 and inside before.
    assert o.fields["bar_half_length"] == pytest.approx(5.2097, abs=2e-3)


def test_the_bar_length_is_reproducible_not_drawn(model):
    """Row 15 is pointwise, so it must not move with the seed — which is why D55 split the stages."""
    values = {run(model, {"pattern_seed": s}, grid=COARSE).fields["bar_half_length"] for s in range(5)}
    assert len(values) == 1


def test_the_bar_stage_derives_the_gas_ratio_without_a_draw(model):
    """S51 (D210 as amended): gas_arm_contrast is the derived stage's, between the two class means, and
    no pattern seed moves it (the source's spread is over segments and bins, not galaxies; #131)."""
    from galaxy.stages.pattern import BAR

    assert "gas_arm_contrast" in {d.name for d in BAR.publishes}
    c = model.constants
    lo, hi = c["GAS_ARM_CONTRAST_OTHER"].value, c["GAS_ARM_CONTRAST_GRAND_DESIGN"].value
    values = {run(model, {"pattern_seed": s}, grid=COARSE).fields["gas_arm_contrast"] for s in range(5)}
    assert len(values) == 1
    assert lo <= values.pop() <= hi


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
    a = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    b = run(model, {"pattern_seed": 7}, grid=COARSE).fields
    c = run(model, {"pattern_seed": 8}, grid=COARSE).fields
    for name in ("bar_corotation_radius", "bar_pattern_speed", "pitch_angle"):
        assert a[name] == b[name], name          # reproducible
        assert a[name] != c[name], name          # and not determined


def test_the_pattern_speed_is_a_definition_not_a_draw(model):
    """Ω_b = v_c(R_CR)/R_CR exactly; all of its scatter is inherited from the fast-bar draw."""
    o = out(model)
    R_cr = o.fields["bar_corotation_radius"]
    v_cr = float(np.interp(R_cr, o.grid.R, o.fields["circular_velocity"]))  # the checkpoint-1 curve since S25
    assert o.fields["bar_pattern_speed"] == pytest.approx(v_cr / R_cr, rel=1e-12)


def test_the_bar_is_fast(model):
    o = out(model)
    ratio = o.fields["bar_corotation_radius"] / o.fields["bar_half_length"]
    assert 0.6 < ratio < 1.9      # 1.2 ± 0.2, drawn, so a few sigma either way


def test_arm_multiplicity_is_a_label_from_the_closed_set_and_no_longer_a_draw(model):
    """S56 (D215): until S56 this test read "drawn from the closed set ... a draw that never varies is not a draw" -
    the arm number was one seeded draw, weighted by the swing window. The draw retired: the window at every radius
    splits the arms' power among the five modes, and ``arm_multiplicity`` is the label of the mode carrying the most
    mass-weighted power. It is a member of the closed set, and it follows the disc, not the pattern seed: the seed
    reaches it only through the saturation, which weighs the rings, and at the default inputs every one of thirty
    seeds reads 6 (D215 ruling 11, the window on X at m = 1; on the X / 2 window of S56's first two passes: 3)."""
    only = ("arm_multiplicity", *AMPLITUDE_FIELDS)
    seen = {run(model, {"pattern_seed": s}, grid=COARSE, only=only).fields["arm_multiplicity"] for s in range(30)}
    assert seen == {6.0} and seen <= set(ARM_MULTIPLICITIES), "the label is the disc's, not the seed's"
    # The disc moves it: a disc-dominated disc's label is four arms where the default's and a halo-dominated one's
    # are six (the label weighs the published amplitudes, the bar's taper in them, so it leans to the outer disc's
    # arm numbers; on the X / 2 window these read 6 and 2 beside the default's 3).
    halo = run(model, {"disc_spin": 0.03, "baryon_retention": 0.15}, grid=COARSE, only=only).fields["arm_multiplicity"]
    disc = run(model, {"disc_spin": 0.01, "baryon_retention": 0.5}, grid=COARSE, only=only).fields["arm_multiplicity"]
    assert (halo, disc) == (6.0, 4.0)
    # Five radial fields, one per arm number of the closed set, each non-negative and under 1.
    o = run(model, grid=COARSE, only=only)
    assert AMPLITUDE_FIELDS == tuple(f"arm_mode_amplitude_{int(m)}" for m in ARM_MULTIPLICITIES)
    for name in AMPLITUDE_FIELDS:
        a = np.asarray(o.fields[name])
        assert a.shape == (o.grid.R.size,) and np.all((a >= 0.0) & (a < 1.0)) and a.max() > 0.05, name


def test_the_contrast_averages_to_one_around_every_ring(model):
    """The pattern redistributes, it does not add: Σ(R, φ)/Σ(R) has mean 1 on every ring (BUILD_II Phase 1b's gate).

    BUILD_II cited this test as already existing; it did not (S26). On the grid and analytically.
    """
    o = out(model)
    field = np.asarray(o.fields["pattern_density_contrast"])
    assert field.shape == (o.grid.R.size, o.grid.phi.size)
    assert np.all(field >= 0.0)
    assert np.allclose(field.mean(axis=1), 1.0, atol=1e-9)
    # S56 (D215): the pattern object holds the modes' amplitudes on the run's grid radii, and comes from compose.
    shape = compose.stellar_pattern(o.fields, o.grid.R)
    assert isinstance(shape, ArmPattern) and not shape.flat
    edges = np.linspace(0.0, 2.0 * np.pi, 13)
    for R in (1.0, 3.0, 6.0, 12.0):
        assert float(shape.sector_means(R, edges).mean()) == pytest.approx(1.0, abs=1e-9)


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


def test_rows_16_and_17_are_judged_statistically(model, judged):
    results = {r.n: r for r in judged[model.name]}
    for n in (16, 17):
        assert results[n].status == "pass"
        assert "median" in results[n].reason and "central 95%" in results[n].reason and "n=41" in results[n].reason


def test_an_ensemble_too_small_is_refused(model):
    small = spec.ensemble(model, ("bar_pattern_speed",), n=5, grid=COARSE)
    results = {r.n: r for r in spec.run(model, ensemble=small, grid=COARSE)}
    assert results[16].status == "not-yet-computable"
    assert "needs >= 41" in results[16].reason
