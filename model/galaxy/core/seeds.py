"""Seed derivation: reproducible, order-independent child streams.

``child(seed, *path)`` and ``rng(seed, *path)`` are pure functions of their
arguments, built on :class:`numpy.random.SeedSequence` with the path as the
``spawn_key``. Because nothing is drawn from a shared stream, the result for
one object cannot depend on which objects were generated before it: this is the
per-region determinism that ``specs/determinism.py`` checks empirically.

String path parts are hashed with BLAKE2b, never with Python's ``hash()``,
which is salted per process for ``str`` and would make every run differ.

A seeded quantity is fully reproducible and not at all determined (rule A10);
the seed is an argument, so "same arguments, same output" holds.
"""

from __future__ import annotations

import hashlib

import numpy as np

PathPart = int | str


class SeedError(ValueError):
    """A seed or path part outside what derivation accepts."""


def stable_int(text: str) -> int:
    """A 64-bit integer for a string, identical across processes and platforms."""
    return int.from_bytes(hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest(), "little")


def _part(part: PathPart) -> int:
    if isinstance(part, bool):
        raise SeedError("path parts may be int or str, not bool")
    if isinstance(part, (int, np.integer)):
        if part < 0:
            raise SeedError(f"path parts must be non-negative, got {part}")
        return int(part)
    if isinstance(part, str):
        return stable_int(part)
    raise SeedError(f"path parts may be int or str, got {type(part).__name__}")


def _seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise SeedError(f"seed must be an int, got {type(seed).__name__}")
    if seed < 0:
        raise SeedError(f"seed must be non-negative, got {seed}")
    return int(seed)


def sequence(seed: int, *path: PathPart) -> np.random.SeedSequence:
    """The SeedSequence for ``(seed, path)``. Pure."""
    return np.random.SeedSequence(_seed(seed), spawn_key=tuple(_part(p) for p in path))


def rng(seed: int, *path: PathPart) -> np.random.Generator:
    """An independent Generator for ``(seed, path)``. Pure: order of calls is irrelevant."""
    return np.random.default_rng(sequence(seed, *path))


def child(seed: int, *path: PathPart) -> int:
    """A 64-bit child seed for ``(seed, path)``, e.g. ``child(systems_seed, star_id)``."""
    return int(sequence(seed, *path).generate_state(1, dtype=np.uint64)[0])
