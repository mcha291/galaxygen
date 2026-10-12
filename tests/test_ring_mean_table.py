"""The normaliser table (D219, the gate's seventh follow-up, part i): a chain's ring mean <E_j>(R) tabulated in R and
read linearly between knots by the point function, the exact mean kept for the knots and for every published field.

**What is pinned here, as measured on 2026-10-11 after the gate's eleventh follow-up (the count's floor on every
ring a chain reaches, the weights and the height's taper at the law's width; re-read with the layer-on pins). The
earlier records are kept at the foot of this docstring.**

- the interpolant's error |a Σ_j (table − exact)| - the error in the ring's mean contrast - over the three legs
  (``milky_way``, ``ngc_4414``, the default inputs) and five seeds each, at every interval's midpoint and at five
  random points an interval: under 1e-6 at the median and 1e-5 at worst (the ruling's bounds, never raised; the
  knots are doubled where an interval fails). The build's own rule holds every interval's quarters and middle under
  1e-6, so the median is far under it and the worst, at a random point, barely over it. Measured (seeds 0-4):
  medians 5.3e-8 to 2.8e-7; worst 9.97e-7 to 1.25e-6 (milky_way seed 1 at R 5.82, a random point); ngc_4414's
  worst 9.97e-7 to 1.14e-6, the default leg's 9.99e-7 to 1.15e-6.
- the knot count a leg: thousands on a 400-ring grid - milky_way 3 456 / 11 648 / 3 737 / 4 439 / 3 640, ngc_4414
  3 383 / 3 987 / 3 757 / 3 524 / 4 000, default 2 780 / 11 660 / 3 350 / 4 064 / 3 292 at seeds 0-4 (the grid's
  rings, the gaps' middles and quarters, the pieces' ends and reach boundaries, then the halvings). The intervals
  at the floor: 32-482 a seed, the reach boundaries' adjacent-float pairs, totalling 2e-14 to 6e-13 kpc a seed, but
  for milky_way seed 3's 5.9e-9 kpc: Norma's turn-back, the one step of the ring's numbers in R that remains
  (#156; ``tests/test_pieces.py::test_the_ring_s_numbers_do_not_step_in_r_at_a_join``). The first crossings' and
  the width bound's jumps are gone with the eleventh follow-up.
- at a knot the table's bits are the exact mean's bits, so every published field is unchanged by the table.
- **the one property the table touches**: the point function's mean round a ring at a non-knot radius is 1 to
  the pinned error, not to rounding (I2 holds: the realised totals are conserved from L1 by construction); at a
  knot it is 1 to the quadrature's own error. The exact sector means (``sector_means``) tile a ring to 1 at any
  radius to rounding, as before.

*After the ninth follow-up (kept):* medians 0 to 2.7e-7; worst 9.98e-7 to 1.23e-6 (milky_way seed 1 at R 7.67);
ngc_4414's worst 9.98e-7 to 1.06e-6, the default leg's 9.98e-7 to 1.08e-6; knots milky_way 2 888 / 10 507 / 3 299 /
3 893 / 3 303, ngc_4414 3 847 / 4 578 / 3 987 / 4 053 / 4 075, default 2 276 / 9 833 / 2 801 / 3 113 / 2 844; the
floor's intervals 40-493 a seed, 2e-14 to 7e-13 kpc but default seed 1's 8.4e-9 (a first crossing or the width
bound's branch).

*The cost builder's record (before the ninth follow-up; kept):* medians 0 to 2.8e-7; worst 9.97e-7 to 1.22e-6
(milky_way seed 1 at R 6.79); ngc_4414's worst 1.00e-6 to 1.01e-6, the default leg's 9.98e-7 to 1.19e-6; knots
milky_way 3 159 / 10 208 / 3 375 / 4 096 / 3 502, ngc_4414 3 847 / 4 578 / 3 768 / 3 906 / 4 999, default 2 256 /
9 862 / 3 117 / 3 180 / 2 874; the floor's intervals 39-472 a seed (the reach boundaries' adjacent-float pairs and
the jumps' last intervals), under 1e-6 kpc in all.
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
    cannot mend and which no star's radius falls in - their total width is under a micro-kpc a leg. (Since the
    gate's ninth follow-up a joined end no longer steps the count; the floor holds the reach boundaries' adjacent
    floats and the steps of other classes, recorded in ``tests/test_pieces.py``.)"""
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


def test_below_the_first_knot_the_point_function_reads_the_exact_mean(patterns):
    """Under the table's first knot (the grid's first radius, 37.5 pc) the point function reads the exact mean,
    not knot 0's clamped one (the gate's twelfth follow-up to D219, item 1). Before the fix ``ngc_4414`` (unbarred,
    a = 1.10 at the centre) read a ring mean of 1.036-1.043 at R 2e-4..0.03 kpc on seeds 0/1/7, still 1e-4 off at
    0.999 R[0]; the barred legs read 0 arms there (the bar's taper). Now the table-read Laid's means are the exact
    ones bit for bit there, and the ring mean by the 11 520-point rule is 1 to the rule's own error (measured
    1.1e-9 to 2.4e-9 on ngc_4414 seeds 0/1/7), the bound the grid radii are held to above."""
    phi = -math.pi + (np.arange(11520) + 0.5) * (2.0 * math.pi / 11520)
    worst = {}
    for (leg, seed), (stars, _) in patterns.items():
        knots, _ = stars.ring_mean_table()
        r = np.geomspace(1e-4, 0.999 * knots[0], 200)
        assert np.array_equal(stars.laid(r).mean, stars.laid(r, exact=False).mean), (leg, seed)
        if leg != "ngc_4414":
            continue
        off = np.abs(stars.contrast_at(r[:, None], phi[None, :]).mean(axis=1) - 1.0)
        worst[seed] = float(off.max())
    assert worst and max(worst.values()) < 1e-7, worst  # the rule's error, as at the grid radii; WORST_BOUND a fortiori


def test_the_table_s_build_raises_when_its_rounds_run_out(prod, monkeypatch):
    """``_build_table`` stops honestly (the gate's twelfth follow-up to D219, item 8): forced with a tolerance no
    interval can meet (1e-30, which also keys the pattern apart in the table store) and one halving round, it raises
    ArithmeticError naming the pattern, the rounds and the worst remaining interval - never a silent table."""
    import dataclasses

    o = run(prod[0].get(DEFAULT_MODEL), inputs_of("ngc_4414", 0), only=tuple(pt.PATTERN_READS))
    stars = dataclasses.replace(compose.stellar_pattern(o.fields, o.grid.R))  # a fresh instance: no table held
    monkeypatch.setattr(pc, "TABLE_TOLERANCE", 1e-30)
    monkeypatch.setattr(pc, "TABLE_ROUNDS", 1)
    with pytest.raises(ArithmeticError, match=r"normaliser table of pattern [0-9a-f]{16} .* after 1 halving rounds; the worst \["):
        stars.ring_mean_table()
