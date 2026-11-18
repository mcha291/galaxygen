"""The forcing's pitch along a chain (S102, batch Q, lane G; register #230).

Until S102 the gas's forcing read, for each chain's term on a ring, the |sin p| of the chain's lead piece - the one
whose locus crosses the ring, else the nearest (D219's third follow-up, item 1: "the forcing's pitch for a ring's
term is the nearest piece's"). That is a square edge in R, and ``forcing_factor`` = m / (X (|sin p| + m h/R))
stepped with it wherever the lead changed: on the Milky Way at 5.91 and 6.04 kpc, where Reid et al. 2019's Sgr-Car
arm holds a 1-degree stretch 133 pc long, the direct solve's row-to-row misplaced weight read 0.161 and 0.155.

The rule since S102 (:meth:`galaxy.stages.pieces.Pieces.chain_sines`): the chain's |sin p| at R is the mean of its
pieces' |sin p| weighted by each piece's radial overlap with a Gaussian in R of standard deviation h_z - the stellar
layer's scale height, the one the thickness factor already reads - centred on R `[inferred: gravity from a layer of
height h does not resolve a kink shorter than h]`. Measured by substitution first (s102_G.md): the misplaced weight
under 0.01 on every 6.25 pc row of 4-10 kpc on the Milky Way and the default galaxy but one (4.4625 kpc, 0.0405: the
count's weight at chain 0's turning point, another mechanism), the ratio of means over 6-10 kpc 1.4311 -> 1.4287.

**The continuity bound, from the kernel.** With w_j(R) = the Gaussian's mass on piece j's span I_j, the chain's
s(R) = E_g[s~] under the density g(r) ∝ N(r; R, h) k(r) on the union of the spans (k(r) the number of the chain's
spans covering r, s~(r) the mean of their sines there), so ds/dR = Cov_g(r, s~) / h². A chain's pieces are joined
end to end, so the spans' union is one interval; the Gaussian cut to an interval is log-concave and its variance
at most h², hence Var_g(r) <= K h² with K the most spans covering one radius; and the variance of s~ is at most
(range/2)² (Popoviciu). So |ds/dR| <= sqrt(K) * range / (2 h), range = the chain's largest minus smallest |sin p|.
For the pitch's part of the factor, |d ln f / ds| = 1 / (s + m h/R) <= R / (m h).
"""

from __future__ import annotations

import copy
import dataclasses
import math

import numpy as np
import pytest

from galaxy import templates
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import pattern as pt
from galaxy.stages import pieces as pc
from galaxy.stages.gas_pattern import GAS_PATTERN_READS, MISPLACED_LIMIT, misplaced_weight

FIELDS = ("gas_density_contrast", "pattern_density_contrast", "gas_arm_contrast", "arm_pattern_speed",
          "circular_velocity", "arm_saturation", *GAS_PATTERN_READS)
H_HAND = 2.6 / 7.3  # kpc: a made-up disc's layer height (as tests/test_gas_pattern.py's LAYER_HEIGHT_HAND)
_GAS: dict[str, object] = {}


def gas_of(prod, template: str):
    """A template's gas pattern, unspurred, on the production grid: once per session."""
    if template not in _GAS:
        model = prod[0].get(DEFAULT_MODEL)
        o = run(model, templates.overrides(templates.TEMPLATES[template]), only=FIELDS)
        c = {k: cc.value for k, cc in model.constants.items()}
        _GAS[template] = dataclasses.replace(compose.gas_pattern(o.fields, o.grid.R, c), spurs=None)
    return _GAS[template]


def two_piece_chain(turn: float = 1.0) -> tuple[pc.Pieces, tuple[float, float, float], tuple[float, float]]:
    """One chain written here: 4 -> 5 kpc at 20 degrees, then 5 -> 7 kpc at 5 degrees, joined at the kink."""
    r0, r1, r2, p0, p1 = 4.0, 5.0, 7.0, 20.0, 5.0
    e0 = math.log(r1 / r0) / math.tan(math.radians(p0))
    e1 = math.log(r2 / r1) / math.tan(math.radians(p1))
    pieces = pc.Pieces([0.0, 0.0], [0.0, 1.0], [r0, r1], [0.0, turn * e0], [p0, p1], [e0, e1], [0.0, 0.0], turn)
    return pieces, (r0, r1, r2), (math.sin(math.radians(p0)), math.sin(math.radians(p1)))


def overlap_by_hand(R: float, lo: float, hi: float, h: float) -> float:
    return 0.5 * (math.erf((hi - R) / (math.sqrt(2.0) * h)) - math.erf((lo - R) / (math.sqrt(2.0) * h)))


def test_the_rule_by_hand_on_a_two_piece_chain():
    """The chain's |sin p| at two radii by hand (the weighted mean of the two pieces' sines, the weights the Gaussian's
    mass on each span), and its limits: the inner piece's sine far inside, the outer's far outside, the crossing
    piece's as h goes to 0."""
    pieces, (r0, r1, r2), (s0, s1) = two_piece_chain()
    for R in (5.0, 4.8):
        w0, w1 = overlap_by_hand(R, r0, r1, H_HAND), overlap_by_hand(R, r1, r2, H_HAND)
        got = pieces.chain_sines(np.array([R]), H_HAND)[0]
        assert got.shape == (3,) and got[2] == 1.0  # one entry per piece, the pad's 1
        assert got[0] == got[1] == pytest.approx((w0 * s0 + w1 * s1) / (w0 + w1), rel=1e-12)
    # At the kink the two spans are 1 and 2 kpc long and h 0.356: the weights are near a half each.
    assert float(pieces.chain_sines(np.array([5.0]), H_HAND)[0, 0]) == pytest.approx(0.5 * (s0 + s1), rel=2e-3)
    far = pieces.chain_sines(np.array([1.0, 12.0]), H_HAND)
    assert far[0, 0] == pytest.approx(s0, rel=1e-12) and far[1, 0] == pytest.approx(s1, rel=1e-12)
    thin = pieces.chain_sines(np.array([4.5, 6.0]), 1e-4)
    assert thin[0, 0] == pytest.approx(s0, rel=1e-12) and thin[1, 0] == pytest.approx(s1, rel=1e-12)
    # A piece with no radial span (pitch 0) holds no weight.
    e0 = math.log(r1 / r0) / math.tan(math.radians(20.0))
    flat = pc.Pieces([0.0, 0.0], [0.0, 1.0], [r0, r1], [0.0, e0], [20.0, 0.0], [e0, 1.0], [0.0, 0.0], 1.0)
    assert float(flat.chain_sines(np.array([5.0]), H_HAND)[0, 0]) == pytest.approx(s0, rel=1e-12)


def test_the_profiles_hand_the_rule_to_the_forcing_and_without_a_height_the_lead_s():
    """``piece_profiles`` holds the chain's sine at the run's last slot: the rule's with the layer's height, the lead
    piece's without one."""
    pieces, (r0, r1, r2), (s0, s1) = two_piece_chain()
    R = np.array([4.6, 4.95, 5.05, 5.6])
    stars = pc.ArmPattern(R, np.full(R.shape, 0.04), np.full(R.shape, 2.0), np.ones(R.shape), pieces,
                          float("nan"), 13.5, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"),
                          50.0 * np.exp(-(R - 8.0) / 2.6))
    want = pieces.chain_sines(R, H_HAND)[:, 0]
    (rows, sines, _), = list(stars.piece_profiles(R, H_HAND))
    held = sines.max(axis=1)
    assert np.array_equal(held, want) and np.all((sines == 0.0) | (sines == held[:, None]))
    (rows, lead, _), = list(stars.piece_profiles(R))
    assert np.array_equal(lead.max(axis=1), [s0, s0, s1, s1])


def test_a_single_piece_chain_is_unchanged_bit_for_bit(prod):
    """``ngc_4414``'s chains are one piece each: the forcing's sines with the layer's height are the lead's, bit for
    bit, on every grid ring."""
    gp = gas_of(prod, "ngc_4414")
    p = gp.stars.pieces
    assert p.count == np.unique(p.chain).size  # one piece per chain
    for (_, a, _), (_, b, _) in zip(gp.stars.piece_profiles(gp.R, gp.layer_height), gp.stars.piece_profiles(gp.R)):
        assert np.array_equal(a, b)
    sines = p.chain_sines(gp.R, gp.layer_height)[:, :p.count]
    held = np.isfinite(sines)  # NaN only where the Gaussian's mass on the span underflows: the lead's there
    assert held.any() and np.array_equal(sines[held], np.broadcast_to(p.sin_abs[:p.count], sines.shape)[held])
    off = np.maximum(np.exp(p.x_start[:p.count])[None, :] - gp.R[:, None], gp.R[:, None] - np.exp(p.x_end[:p.count])[None, :])
    assert np.all(off[~held] > 20.0 * gp.layer_height)


def test_the_milky_way_s_chains_are_continuous_under_the_kernel_s_bound(prod):
    """Along every chain of ``milky_way``, 3-15 kpc on 6.25 pc rows: the chain's |sin p| changes from row to row by
    at most ΔR sqrt(K) range / (2h), and the pitch's part of the m = 2 factor by at most that over (s + 2h/R) - the
    bound of the module's docstring. The lead piece's rule broke it (the Sgr-Car stretch at 5.91 kpc)."""
    gp = gas_of(prod, "milky_way")
    p, h = gp.stars.pieces, gp.layer_height
    assert h == pytest.approx(0.35683, abs=1e-5)
    dR = 0.00625
    R = np.round(np.arange(3.0, 15.0 + 1e-9, dR), 6)
    sines = p.chain_sines(R, h)
    lo, hi = np.exp(p.x_start[:p.count]), np.exp(p.x_end[:p.count])
    worst = 0.0
    for chain in np.unique(p.chain):
        members = np.flatnonzero(p.chain == chain)
        s = sines[:, members[0]]
        ok = np.isfinite(s[1:]) & np.isfinite(s[:-1])
        span = float(p.sin_abs[members].max() - p.sin_abs[members].min())
        mid = np.linspace(lo[members].min(), hi[members].max(), 4001)
        k = int(max(1, ((mid[:, None] >= lo[members]) & (mid[:, None] < hi[members])).sum(axis=1).max()))
        bound = dR * math.sqrt(k) * span / (2.0 * h)
        step = np.abs(np.diff(s))[ok]
        assert step.size and np.all(step <= bound * (1.0 + 1e-9) + 1e-15), (chain, float(step.max()), bound)
        # The pitch's part of m / (X (s + m h/R)), m = 2, the two rows' sines at one radius (X and R held).
        c = 2.0 * h / R[1:][ok]
        rel = np.abs(np.log(s[1:][ok] + c) - np.log(s[:-1][ok] + c))
        assert np.all(rel <= bound / (np.minimum(s[1:], s[:-1])[ok] + c) * (1.0 + 1e-9) + 1e-15)
        worst = max(worst, float(step.max() / bound) if bound > 0.0 else 0.0)
    print(f"milky_way: the largest row step over its bound {worst:.3f}")
    # The old rule: chain 2's lead steps 0.3407 -> 0.0175 at 5.9125 kpc, over the bound.
    i = int(np.searchsorted(R, 5.9125))
    laid = gp.stars.laid(R[i - 1:i + 1])
    two = laid.lead & (p.chain_of[laid.slots] == 2.0)
    old = [float(p.sin_abs[laid.slots[r][two[r]]][0]) for r in range(2)]
    assert old == pytest.approx([0.3407, 0.0175], abs=1e-4)
    k = int(np.flatnonzero(p.chain == 2.0)[0])
    assert abs(old[1] - old[0]) > 30.0 * float(np.abs(np.diff(sines[i - 1:i + 1, k]))[0])


def test_the_milky_way_s_old_band_is_no_longer_flagged(prod):
    """5.85-6.15 kpc on 6.25 pc rows: the direct solve's row-to-row misplaced weight under the carry's own 1 % on
    every row (it read 0.161 at 5.9125 and 0.155 at 6.04375 under the lead's rule), and no mid-gap ring kept inside
    the band (there were five: 5.906, 5.925, 6.0, 6.056, 6.075)."""
    gp = gas_of(prod, "milky_way")
    R = np.round(np.arange(5.85, 6.15 + 1e-9, 0.00625), 6)
    S = gp.solve_at(R)
    miss = misplaced_weight(S[1:], S[:-1])
    print(f"milky_way 5.85-6.15: the largest row-to-row misplaced weight {miss.max():.4f} at {R[1 + int(np.argmax(miss))]:.5f}")
    assert np.all(miss < MISPLACED_LIMIT)
    radii, _ = gp.mid_gap
    assert not np.any((radii > 5.85) & (radii < 6.15)), radii


# --- the count's taper at a turn back in R (S102, the gate's ruling on #230's 4.456 kpc step) --------------------


def turning_chain() -> tuple[pc.ArmPattern, dict]:
    """Chain 0 runs out from 4 to 5 kpc at 20 degrees and turns back in to 4.8 kpc at -20 degrees (two outer ends
    meet at 5 kpc: a turn); chain 1 runs straight across, 2 -> 9 kpc at 20 degrees."""
    a, b = 20.0, -20.0
    e_a = math.log(5.0 / 4.0) / math.tan(math.radians(a))
    e_b = math.log(5.0 / 4.8) / abs(math.tan(math.radians(b)))
    e_c = math.log(9.0 / 2.0) / math.tan(math.radians(a))
    pieces = pc.Pieces([0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [4.0, 4.8, 2.0], [0.0, e_a + e_b, 1.0], [a, b, a], [e_a, e_b, e_c],
                       [0.0, 0.0, 0.0], 1.0)
    R = np.array([4.5, 4.9, 4.95, 5.2])
    stars = pc.ArmPattern(R, np.full(R.shape, 0.04), np.full(R.shape, 2.0), np.ones(R.shape), pieces,
                          float("nan"), 13.5, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"),
                          50.0 * np.exp(-(R - 8.0) / 2.6))
    return stars, dict(e_a=e_a, e_b=e_b, a=a, b=b)


def test_the_count_tapers_at_a_turn_back_by_hand():
    """At 4.95 kpc chain 0 crosses both its pieces; its weight is the larger of min(1, s/w) at the two crossings, s the
    length along the chain to its nearer end - the free inner ends, or the turn at 5 kpc - in kpc at the ring."""
    stars, g = turning_chain()
    p = stars.pieces
    assert p.turn_after[0] == 0.0 and p.turn_after[1] == 0.0 and math.isinf(p.turn_before[0]) and math.isinf(p.turn_before[1])
    assert math.isinf(p.turn_after[2]) and math.isinf(p.turn_before[2])  # the straight chain has no turn
    R = 4.95
    law = float(stars.law_width_at(np.array([R]))[0])
    length_a = g["e_a"] / math.cos(math.radians(g["a"]))
    length_b = g["e_b"] / math.cos(math.radians(g["b"]))
    t_a = math.log(R / 4.0) / math.log(5.0 / 4.0) * length_a
    t_b = math.log(R / 4.8) / math.log(5.0 / 4.8) * length_b
    s_a = min(t_a, length_a - t_a) * R  # the free start, or the turn
    s_b = min(t_b, length_b - t_b) * R
    weight = max(min(1.0, s_a / law), min(1.0, s_b / law))
    _, count = stars.ring_state(np.array([R]))
    assert float(count[0]) == pytest.approx(1.0 + weight, rel=1e-12)  # chain 1 holds its whole weight here
    assert weight < 0.5  # 50 pc from the turn: most of chain 0's share is gone
    _, beyond = stars.ring_state(np.array([5.0 * (1.0 + 1e-9)]))
    assert float(beyond[0]) == pytest.approx(1.0, abs=1e-6)


def test_the_count_is_continuous_across_every_turn_of_the_milky_way_and_unchanged_without_one(prod):
    """At every turn back in R of ``milky_way``'s chains, N just inside and just outside the turning radius agree;
    a census with no turn (``ngc_4414``, one piece per chain) and the Milky Way's rings that no turning chain reaches
    read N to the bit as with the turns taken out."""
    gp = gas_of(prod, "milky_way")
    st, p = gp.stars, gp.stars.pieces
    n = p.count
    radii = []
    for j in range(n):
        if p.turn_after[j] == 0.0:
            radii.append(float(np.exp(p.x_end[j])))
        if p.turn_before[j] == 0.0:
            radii.append(float(np.exp(p.x_start[j])))
    assert radii and any(abs(r - 4.46) < 0.01 for r in radii)
    for r in sorted(set(radii)):
        _, inside = st.ring_state(np.array([r * (1.0 - 1e-9)]))
        _, outside = st.ring_state(np.array([r * (1.0 + 1e-9)]))
        assert abs(float(inside[0]) - float(outside[0])) < 1e-6, r
    R = np.round(np.arange(0.5, 20.0, 0.0125), 6)
    _, now = st.ring_state(R)
    turns = np.isfinite(p.turn_before[:n]) | np.isfinite(p.turn_after[:n])
    turning_chains = np.unique(p.chain[turns])
    off = copy.copy(st.pieces)
    object.__setattr__(off, "turn_before", np.full(n + 1, np.inf))
    object.__setattr__(off, "turn_after", np.full(n + 1, np.inf))
    plain = copy.copy(st)
    object.__setattr__(plain, "pieces", off)
    _, before = plain.ring_state(R)
    slots = p.slots(R)
    near = np.isin(p.chain_of[slots], turning_chains).any(axis=1)
    lo = np.exp(p.x_start[:n][np.isin(p.chain, turning_chains)]).min() - 2.0
    hi = np.exp(p.x_end[:n][np.isin(p.chain, turning_chains)]).max() + 2.0
    far = ~near & ((R < lo) | (R > hi))
    assert far.any() and np.array_equal(now[far], before[far])
    q = gas_of(prod, "ngc_4414").stars.pieces
    assert np.all(np.isinf(q.turn_before)) and np.all(np.isinf(q.turn_after))
