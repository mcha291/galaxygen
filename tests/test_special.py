"""The Bessel approximations, pinned against independently known values.

These are transcribed polynomial coefficients. A single mistyped digit shifts a
rotation curve by a fraction of a percent, which is exactly the size of
acceptance row 3's error bar and would look like physics rather than a typo
(rule B1: build the instrument before the thing it certifies).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.special import DomainError, i0, i1, k0, k1

# Independently known values, to ten significant figures.
KNOWN = {
    #  x      K0(x)          K1(x)          I1(x)
    0.5: (0.9244190712, 1.6564411200, 0.2578943054),
    1.0: (0.4210244382, 0.6019072302, 0.5651591040),
    2.0: (0.1138938727, 0.1398658818, 1.5906368546),
    3.0: (0.0347395044, 0.0401564311, 3.9533702174),
    5.0: (0.0036910983, 0.0040446134, 24.3356421424),
}


@pytest.mark.parametrize("x", sorted(KNOWN))
def test_golden_values(x):
    want_k0, want_k1, want_i1 = KNOWN[x]
    assert float(k0(x)) == pytest.approx(want_k0, abs=2e-7)
    assert float(k1(x)) == pytest.approx(want_k1, abs=2e-7)
    assert float(i1(x)) == pytest.approx(want_i1, rel=2e-7)


def test_the_branch_at_the_join_is_continuous():
    """A&S switches formula at x = 2 (K) and x = 3.75 (I₁); a bad branch shows as a step."""
    for f, cut in ((k0, 2.0), (k1, 2.0), (i1, 3.75)):
        lo, hi = float(f(cut - 1e-9)), float(f(cut + 1e-9))
        assert lo == pytest.approx(hi, rel=1e-6), f.__name__


def test_wronskian_identity():
    """I₀(x)K₁(x) + I₁(x)K₀(x) = 1/x exactly. Ties all four together in one relation."""
    x = np.array([0.05, 0.3, 1.0, 1.999, 2.001, 4.0, 9.0])
    assert np.allclose(i0(x) * k1(x) + i1(x) * k0(x), 1.0 / x, rtol=1e-6)


def test_vectorised_and_scalar_agree():
    x = np.array([0.5, 1.5, 2.5])
    assert np.allclose(k0(x), [float(k0(v)) for v in x])
    assert i1(np.zeros(3)).tolist() == [0.0, 0.0, 0.0]


def test_domain_is_refused_not_silently_infinite():
    for f in (k0, k1):
        with pytest.raises(DomainError):
            f(0.0)
        with pytest.raises(DomainError):
            f(-1.0)
    with pytest.raises(DomainError):
        i1(np.array([1.0, np.inf]))


def test_G_is_the_IAU_nominal_solar_mass_parameter():
    """The one constant in Level 0 whose value is arithmetic rather than a citation."""
    from galaxy.models.level0 import LEVEL0

    GM_sun = 1.32712440018e20  # m³/s², IAU nominal
    kpc = 3.0856775814913673e19  # m
    expected = GM_sun / (kpc * 1e6)  # -> kpc (km/s)² / M☉
    assert LEVEL0["G"].value == pytest.approx(expected, rel=1e-9)
    assert LEVEL0["G"].unit == "kpc.km2/s2/Msun"
    # And the sanity check that motivates those units: a circular orbit.
    v2 = LEVEL0["G"].value * 1.0e12 / 100.0
    assert math.sqrt(v2) == pytest.approx(207.4, abs=0.1)  # km/s at 100 kpc, 10^12 M☉
