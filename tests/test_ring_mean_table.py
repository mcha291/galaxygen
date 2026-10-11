"""The normaliser table (D219, the gate's seventh follow-up, part i): a chain's ring mean <E_j>(R) tabulated in R and
read linearly between knots by the point function, the exact mean kept for the knots and for every published field.

**What is pinned here, as measured on 2026-10-11 (the fifth pass's census; re-read with the layer-on pins):**

- the interpolant's error |a Σ_j (table − exact)| - the error in the ring's mean contrast - over the three legs
  (``milky_way``, ``ngc_4414``, the default inputs) and five seeds each, at every interval's midpoint and at five
  random points an interval: under 1e-6 at the median and 1e-5 at worst (the ruling's bounds, never raised; the
  knots are doubled where an interval fails). The build's own rule holds every midpoint under 1e-6, so the median
  is far under it; the worst is at a random point of a narrow central interval. Measured: medians 0 to 3.6e-7,
  worst 1.2e-6 (milky_way, default) to 5.7e-6 (ngc_4414 at R ~ 0.045 kpc).
- the knot count a leg: thousands on a 400-ring grid (milky_way 3 156, ngc_4414 3 829, default 2 250 at seed 0;
  the grid's rings, the gaps' middles and quarters, the pieces' ends and reach boundaries, then the halvings).
- at a knot the table's bits are the exact mean's bits, so every published field is unchanged by the table.
- **the one property the table touches**: the point function's mean round a ring at a non-knot radius is 1 to
  the pinned error, not to rounding (I2 holds: the realised totals are conserved from L1 by construction); at a
  knot it is 1 to the quadrature's own error. The exact sector means (``sector_means``) tile a ring to 1 at any
  radius to rounding, as before.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy import templates
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import pattern as pt
from galaxy.stages import pieces as pc

LEGS = ("milky_way", "ngc_4414", "default")
SEEDS = (0, 1, 2, 3, 4)
MEDIAN_BOUND, WORST_BOUND = 1e-6, 1e-5  # the ruling's: never raised


def inputs_of(leg: str, seed: int) -> dict:
    base = {} if leg == "default" else templates.overrides(templates.TEMPLATES[leg])
    return {**base, "pattern_seed": seed, "texture_seed": seed}


@pytest.fixture(scope="module")
def patterns(prod):
    model = prod[0].get(DEFAULT_MODEL)
    out = {}
    for leg in LEGS:
        for seed in SEEDS:
            o = run(model, inputs_of(leg, seed), only=tuple(pt.PATTERN_READS))
            out[leg, seed] = compose.stellar_pattern(o.fields, o.grid.R), o.grid.R
    return out


def errors(stars: pc.ArmPattern, R: np.ndarray) -> np.ndarray:
    """|a Σ_j (table − exact)| at each radius of ``R``: the table-read Laid against the exact one."""
    exact, table = stars.laid(R), stars.laid(R, exact=False)
    chains = stars.ring_mean_table()[1].shape[1]
    gap = stars._means_matrix(table, chains) - stars._means_matrix(exact, chains)
    return np.abs(exact.effective * gap.sum(axis=1))


FLOOR = 1e-9  # an interval narrower than this share of its radius holds a jump of the exact mean itself (pieces.TABLE_ROUNDS)


def test_the_table_s_error_is_under_the_ruling_s_bounds_on_three_legs_and_five_seeds(patterns):
    """Midpoints and five random points an interval, every leg and seed: median under 1e-6, worst under 1e-5.

    The intervals at the rounding floor are counted apart: each holds a jump of the exact mean in R (the ring's
    count, and so its bounded width, steps where a chain's crossing set changes at a joined end), which halving
    cannot mend and which no star's radius falls in - their total width is under a micro-kpc a leg."""
    rng = np.random.default_rng(2026)
    worst, medians, knots_of, jumps = {}, {}, {}, {}
    for (leg, seed), (stars, _) in patterns.items():
        knots, means = stars.ring_mean_table()
        assert knots.size > 100 and np.all(np.diff(knots) > 0.0), (leg, seed, knots.size)
        lo, hi = knots[:-1], knots[1:]
        wide = (hi - lo) > FLOOR * hi
        jumps[leg, seed] = (int((~wide).sum()), float((hi - lo)[~wide].sum()))
        lo, hi = lo[wide], hi[wide]
        mid = 0.5 * (lo + hi)
        rand = (lo[:, None] + rng.random((lo.size, 5)) * (hi - lo)[:, None]).reshape(-1)
        at_mid = errors(stars, mid)
        err = np.concatenate([at_mid, errors(stars, rand)])
        assert np.isfinite(err).all(), (leg, seed)
        medians[leg, seed], worst[leg, seed], knots_of[leg, seed] = float(np.median(err)), float(err.max()), int(knots.size)
        assert at_mid.max() <= MEDIAN_BOUND, (leg, seed, "the build's own rule: every midpoint under 1e-6")
    assert max(medians.values()) < MEDIAN_BOUND, medians
    assert max(worst.values()) < WORST_BOUND, worst
    assert max(width for _, width in jumps.values()) < 1e-6, jumps
    # The knots a leg: the grid's 400 rings, the gaps' middles and quarters, the pieces' ends and reach boundaries,
    # then the halvings - thousands, never a handful (a table of a few knots would mean the check did not run).
    assert min(knots_of.values()) > 1000 and max(knots_of.values()) < 50_000, knots_of


def test_at_a_knot_the_table_is_the_exact_mean_bit_for_bit(patterns):
    """The published fields are made from the exact mean at knots; the table there is the same number."""
    for (leg, seed), (stars, R) in patterns.items():
        knots, _ = stars.ring_mean_table()
        assert np.isin(R[R > 0.0], knots).all(), (leg, seed, "every grid radius is a knot")
        exact, table = stars.laid(knots), stars.laid(knots, exact=False)
        assert np.array_equal(exact.mean, table.mean) and np.array_equal(exact.effective, table.effective), (leg, seed)
        sample = knots[:: max(1, knots.size // 50)]
        assert np.array_equal(stars.laid(sample).mean, stars.laid(sample, exact=False).mean), (leg, seed)


def test_the_ring_mean_property_holds_to_the_pinned_error_between_knots_and_to_rounding_at_them(patterns):
    """The point function's mean round a ring, by a 11 520-point rule: 1 within 1e-5 at non-knot radii (the pinned
    worst), 1 within the rule's own error at grid radii; the exact sector means tile a ring to 1 to rounding anywhere."""
    phi = -math.pi + (np.arange(11520) + 0.5) * (2.0 * math.pi / 11520)
    edges = np.linspace(0.0, 2.0 * math.pi, 37)
    for leg in LEGS:
        stars, R = patterns[leg, 0]
        knots, _ = stars.ring_mean_table()
        mid = 0.5 * (knots[:-1] + knots[1:])
        between = mid[np.linspace(0, mid.size - 1, 7).astype(int)]
        at_knots = R[np.linspace(20, R.size - 20, 5).astype(int)]
        off = np.abs(stars.contrast_at(between[:, None], phi[None, :]).mean(axis=1) - 1.0)
        on = np.abs(stars.contrast_at(at_knots[:, None], phi[None, :]).mean(axis=1) - 1.0)
        assert off.max() < WORST_BOUND, (leg, off)
        assert on.max() < 1e-7, (leg, on)  # the rule's error on the kinked integrand, not the table's
        for r in (*between[:3], *at_knots[:2]):
            assert abs(float(stars.sector_means(float(r), edges).mean()) - 1.0) < 1e-12, (leg, r)
