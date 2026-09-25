"""S25's own measurement (BUILD_II Phase 0, D173): the retained budget as a root inside checkpoint 1.

Debts #3 and #26 were ruled permanent at S22 on one clause: the retained baryon budget is
what the halo contracts around (checkpoint 1) and what a mass-loaded wind would remove
(checkpoint 3), a fixed point across checkpoints, and rule A1 forbids one. S25 rewrote A1 —
the stage graph is acyclic; iteration lives inside a stage when its termination is
guaranteed in advance — and the question became the one BUILD_II Phase 0 poses: can the
retained fraction be the root of a monotone function of itself, as the contraction is?

This pins the probe that answered it, run with the repository unchanged. With
``g(f) = 1 / (1 + eta_bar(f) s)`` the share of an arriving budget that the chemistry's own
energy-driven wind would leave in a disc retaining ``f`` — ``eta_bar`` the SFR-weighted mass
loading ``(WIND_SPEED / v_esc)^WIND_INDEX`` read from the published escape velocity, ``s``
the stars' share of the retained baryons — ``F(f) = f - g(f)`` was monotone across the input
range 0.05–0.5 with ``|dg/df|`` 0.76 at the low end and under 0.02 near the root, and the
root read 0.338 against the input's default 0.35 (0.424 at checkpoint 1's potential weighted
by Sigma^KS_INDEX). A structural property and an order of magnitude, pinned as a measurement
and never as a target (rule B5); the numbers in the docstring are the ten-point sweep's, the
assertions below the four-point one the suite can afford.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.run import run
from galaxy.stages.chemistry_dtd import escape_velocity  # the wind reads this; a checkpoint-1 stage could too

RETENTIONS = (0.2, 0.3, 0.4, 0.5)


def _kept_share(model, f: float) -> tuple[float, float]:
    """(g at checkpoint 3's escape velocity, g at checkpoint 1's) for a disc retaining ``f``."""
    o = run(model, {"baryon_retention": f})
    F, R = o.fields, o.grid.R
    c = {k: v.value for k, v in model.constants.items()}
    v3 = np.asarray(F["escape_velocity"])
    v1 = escape_velocity(
        np.asarray(F["halo_potential_midplane"]), np.asarray(F["circular_velocity"]),
        np.asarray(F["halo_circular_velocity"]), R, float(F["baryon_mass_total"]), c["G"],
    )
    eta3 = (c["WIND_SPEED"] / np.maximum(v3, 1.0)) ** c["WIND_INDEX"]
    eta1 = (c["WIND_SPEED"] / np.maximum(v1, 1.0)) ** c["WIND_INDEX"]
    w3 = np.asarray(F["sfr_surface_density"]) * R
    w1 = np.asarray(F["disc_surface_density"]) ** c["KS_INDEX"] * R
    stars, gas = float(F["stellar_mass_total"]), float(F["gas_mass_30kpc"])
    s = stars / (stars + gas)
    return 1.0 / (1.0 + float(np.sum(eta3 * w3) / np.sum(w3)) * s), 1.0 / (1.0 + float(np.sum(eta1 * w1) / np.sum(w1)) * s)


@pytest.fixture(scope="module")
def sweep():
    models, _, _ = production()
    basic = next(m for m in models if m.name == "basic")
    return np.array([(f, *_kept_share(basic, f)) for f in RETENTIONS])


def test_debts_3_and_26_the_retained_budget_is_a_root_inside_checkpoint_1(sweep):
    """The map f -> g(f) is a contraction, so F = f - g is monotone and its root is one and found by bisection."""
    f = sweep[:, 0]
    for col, where in ((1, "checkpoint 3"), (2, "checkpoint 1")):
        g = sweep[:, col]
        gain = np.abs(np.diff(g) / np.diff(f))
        assert np.all(gain < 1.0), f"{where}: the map is not a contraction, gain {gain}"
        F = f - g
        assert np.all(np.diff(F) > 0.0), f"{where}: F is not monotone, {F}"
        assert F[0] < 0.0 < F[-1], f"{where}: no root inside [0.2, 0.5], F = {F}"


def test_the_root_at_the_defaults_is_the_input_the_model_carries(sweep):
    """f* = 0.338 at checkpoint 3's reading, against baryon_retention's default 0.35 (D173).

    Read at the present potential and SFR profile — the history-integrated loading is
    larger, so a built derivation reads lower; the number is the probe's, not a target.
    """
    f, g3 = sweep[:, 0], sweep[:, 1]
    F = f - g3
    i = int(np.where(np.diff(np.sign(F)) != 0)[0][0])
    root = f[i] - F[i] * (f[i + 1] - f[i]) / (F[i + 1] - F[i])
    assert root == pytest.approx(0.338, abs=0.01)
