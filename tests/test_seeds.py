"""Seed derivation: pure, order-independent, and pinned by golden values."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core import seeds
from galaxy.specs.determinism import GOLDEN_CHILD, GOLDEN_DRAW, GOLDEN_STABLE_INT


def test_child_is_order_independent():
    ids = list(range(200))
    perm = [int(i) for i in np.random.default_rng(3).permutation(200)]
    forward = {i: seeds.child(7, i) for i in ids}
    shuffled = {i: seeds.child(7, i) for i in perm}
    assert forward == shuffled


def test_children_distinct_on_sample():
    assert len({seeds.child(0, i) for i in range(2000)}) == 2000


def test_seed_and_path_both_matter():
    assert seeds.child(0, 1) != seeds.child(1, 1)
    assert seeds.child(0, "halo") != seeds.child(0, "disc")
    assert seeds.child(0, "a", 1) != seeds.child(0, "a", 2)
    assert seeds.child(0, 1, "a") != seeds.child(0, "a", 1)
    assert seeds.child(0) != seeds.child(0, 0)


def test_rng_streams_reproducible_and_independent():
    r1 = seeds.rng(5, "x").random(3)
    r2 = seeds.rng(5, "x").random(3)
    r3 = seeds.rng(5, "y").random(3)
    assert np.array_equal(r1, r2)
    assert not np.array_equal(r1, r3)


def test_golden_values():
    # Pinned at S0 (numpy 2.5.2). A change here is a stream change, not a test to update casually.
    assert seeds.stable_int("galaxy") == GOLDEN_STABLE_INT
    assert seeds.child(0, "stub", 7) == GOLDEN_CHILD
    assert seeds.rng(12345, "golden").random() == GOLDEN_DRAW


def test_string_hash_is_not_python_hash():
    # Python's str hash is salted per process; ours must be a fixed function of the bytes.
    assert seeds.stable_int("galaxy") != hash("galaxy") or seeds.stable_int("galaxy") == GOLDEN_STABLE_INT
    assert seeds.stable_int("") == seeds.stable_int("")
    assert seeds.stable_int("a") != seeds.stable_int("b")


@pytest.mark.parametrize("seed", [-1, 1.5, "7", True, None])
def test_bad_seed(seed):
    with pytest.raises(seeds.SeedError):
        seeds.child(seed)  # type: ignore[arg-type]


@pytest.mark.parametrize("part", [-1, 1.5, True, None, b"x"])
def test_bad_path_part(part):
    with pytest.raises(seeds.SeedError):
        seeds.child(0, part)  # type: ignore[arg-type]


def test_numpy_integers_accepted():
    assert seeds.child(np.int64(3), np.uint32(4)) == seeds.child(3, 4)
    assert seeds.child(0, 2**40) != seeds.child(0, 2**40 + 1)
