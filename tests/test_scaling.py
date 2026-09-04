"""tools/scaling.py: the instrument behind rule B7, checked on what it can be checked on.

The exponents themselves are measured, not asserted — a timing in CI is a
reading of the runner. What is asserted is that the tool's arithmetic is right,
that the naive convolution it times as the control is the same physics as the
binned kernel the stage uses, and that the binned kernel's cost does not grow
with N_t by construction.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.stages import chemistry_dtd as C
from scaling import exponent, naive_snia_rate


def test_the_exponent_is_a_log_log_slope():
    n = (500, 1000, 2000, 4000)
    assert exponent(n, [1e-3 * k for k in n]) == pytest.approx(1.0)
    assert exponent(n, [1e-6 * k * k for k in n]) == pytest.approx(2.0)
    assert exponent(n, [0.5] * 4) == pytest.approx(0.0)


def test_the_naive_convolution_and_the_binned_kernel_agree():
    """Same DTD, two algorithms: a burst's Ia iron arrives on the same schedule to a few percent."""
    n_t, dt = 4000, 13.8 / 4000
    psi = np.zeros((2, n_t))
    psi[:, 100] = 1.0
    psi[1, 900] = 0.5
    naive = naive_snia_rate(psi, dt, 0.15, 1.1)
    delays, weights = C.dtd_bins(0.15, 13.8, 1.1)
    binned = C.snia_rate(psi, dt, delays, weights)
    assert naive.sum(axis=1) == pytest.approx(binned.sum(axis=1), rel=0.02)
    # Cumulative arrival within a few percent of the total at every time.
    cn, cb = np.cumsum(naive, axis=1), np.cumsum(binned, axis=1)
    assert np.max(np.abs(cn - cb)) < 0.05 * cn[:, -1].max()


def test_the_binned_kernel_touches_a_fixed_number_of_shifts():
    """The whole of the linear-in-N_t argument: K shifts, whatever the grid (GALAXY_INPUTS.md §10)."""
    for n_t in (500, 8000):
        delays, weights = C.dtd_bins(0.15, 13.8, 1.1)
        shifts = {max(1, int(round(tau / (13.8 / n_t)))) for tau in delays}
        assert len(shifts) <= C.DTD_BINS
        assert delays.size == C.DTD_BINS
