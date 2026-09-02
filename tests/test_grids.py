"""Grids: the plan's defaults, and N_R / N_t as independent knobs."""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import DEFAULT, Axis, GridError, GridSpec


def test_defaults_follow_the_plan():
    # GALAXY_PLAN.md §5a: N_R = 400, N_t = 2000, N_z ≈ 60.
    assert (DEFAULT.n_R, DEFAULT.n_t, DEFAULT.n_z) == (400, 2000, 60)
    g = DEFAULT.build()
    assert g.shape(("R", "t")) == (400, 2000)
    assert g.shape(("R", "t", "z", "phi")) == (400, 2000, 60, 360)
    assert g.shape(()) == ()


def test_axes():
    g = DEFAULT.build()
    assert len(g.R) == 400 and g.R[0] > 0 and g.R[-1] < 30
    assert g["R"].edges[0] == 0 and g["R"].edges[-1] == 30 and len(g["R"].edges) == 401
    assert np.allclose(np.diff(g.R), 30 / 400)
    assert g.t[-1] < 13.8 and g.t[0] > 0
    assert g.z.min() >= 0
    assert g.phi[-1] < 2 * math.pi
    assert g["R"].unit == "kpc" and g["t"].unit == "Gyr" and g["z"].unit == "kpc" and g["phi"].unit == "rad"
    assert math.isclose(g["R"].width, 0.075)


def test_knobs_are_independent():
    a = GridSpec()
    b = a.replace(n_R=100)
    assert np.array_equal(a.build().t, b.build().t)
    assert b.build().shape(("R",)) == (100,)
    c = a.replace(n_t=10)
    assert np.array_equal(a.build().R, c.build().R)
    assert c.build().shape(("t",)) == (10,)


def test_validation():
    with pytest.raises(GridError):
        GridSpec(n_R=0).build()
    with pytest.raises(GridError):
        GridSpec(R_max=-1.0).build()
    with pytest.raises(GridError):
        Axis("q", "kpc", 3, 0.0, 1.0)
    with pytest.raises(GridError):
        Axis("R", "kpc", True, 0.0, 1.0)  # type: ignore[arg-type]
    with pytest.raises(GridError):
        Axis("R", "kpc", 3, 1.0, 1.0)


def test_repr_mentions_spec():
    assert "GridSpec" in repr(GridSpec(n_R=3).build())
