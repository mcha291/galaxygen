"""Special functions the model needs and numpy does not ship: I₁, K₀, K₁, and erf.

The exponential disc's circular velocity is analytic in terms of I₀, I₁, K₀ and
K₁ (Freeman 1970) ``[recall: Freeman 1970, ApJ 160, 811; the standard form is
reproduced in Binney & Tremaine §2.6.1]``. numpy ships ``i0`` and nothing else,
and adding scipy for four functions would replace a two-package pinned
environment with a large binary dependency for no gain in accuracy that matters
here ``[inferred]``.

So the polynomial approximations of Abramowitz & Stegun §9.8 are implemented
directly: 9.8.3–9.8.4 for I₁, 9.8.5–9.8.6 for K₀, 9.8.7–9.8.8 for K₁
``[recall: Abramowitz & Stegun, Handbook of Mathematical Functions, §9.8]``.
Their stated accuracy is |ε| < 2×10⁻⁷ for K and < 8×10⁻⁹ (relative, scaled) for
I₁; ``tests/test_special.py`` pins values against independently known ones so a
transcription slip fails loudly rather than shifting a rotation curve by a
percent. A percent in v_c is 2.5 km/s at R₀, which is most of acceptance row 3's
error bar — this is exactly the class of error a golden-value test exists to
catch ``[inferred]``.

Domain: x > 0. K₀ and K₁ diverge at the origin and the callers never evaluate
there (grid *centres* are used, never edges), so a non-positive argument is an
error rather than an ``inf``.

``erf`` — and the normal CDF over it — arrives at S8 for the same reason and from
the same book: giant-planet occurrence is the probability that a log-normal disc
mass clears a threshold, evaluated on 800 000 grid cells, and ``math.erf`` is a
scalar function. A&S 7.1.26 gives |ε| < 1.5×10⁻⁷ over the whole line, which is
four orders below the uncertainty on anything it is multiplied by
``[recall: Abramowitz & Stegun §7.1.26]``.
"""

from __future__ import annotations

import numpy as np

__all__ = ("i0", "i1", "k0", "k1", "erf", "normal_cdf")


class DomainError(ValueError):
    """K₀ and K₁ are defined for x > 0; I₁ for x >= 0."""


def _asarray(x: object, what: str, *, positive: bool) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    bad = np.any(a <= 0.0) if positive else np.any(a < 0.0)
    if bad or np.any(~np.isfinite(a)):
        raise DomainError(f"{what}: argument must be finite and {'> 0' if positive else '>= 0'}")
    return a


def i0(x: object) -> np.ndarray:
    """Modified Bessel I₀. numpy's own implementation; re-exported so callers import one module."""
    return np.i0(_asarray(x, "i0", positive=False))


def i1(x: object) -> np.ndarray:
    """Modified Bessel I₁ (A&S 9.8.3, 9.8.4)."""
    a = _asarray(x, "i1", positive=False)
    small = a <= 3.75
    t = (np.where(small, a, 3.75) / 3.75) ** 2
    near = a * (
        0.5
        + t * (0.87890594 + t * (0.51498869 + t * (0.15084934 + t * (0.02658733 + t * (0.00301532 + t * 0.00032411)))))
    )
    big = np.where(small, 3.75, a)
    u = 3.75 / big
    far = (
        0.39894228
        + u
        * (
            -0.03988024
            + u
            * (
                -0.00362018
                + u * (0.00163801 + u * (-0.01031555 + u * (0.02282967 + u * (-0.02895312 + u * (0.01787654 - u * 0.00420059)))))
            )
        )
    ) * np.exp(big) / np.sqrt(big)
    return np.where(small, near, far)


def k0(x: object) -> np.ndarray:
    """Modified Bessel K₀ (A&S 9.8.5, 9.8.6)."""
    a = _asarray(x, "k0", positive=True)
    small = a <= 2.0
    near_x = np.where(small, a, 2.0)
    t = (near_x / 2.0) ** 2
    near = -np.log(near_x / 2.0) * np.i0(near_x) + (
        -0.57721566
        + t * (0.42278420 + t * (0.23069756 + t * (0.03488590 + t * (0.00262698 + t * (0.00010750 + t * 0.00000740)))))
    )
    far_x = np.where(small, 2.0, a)
    u = 2.0 / far_x
    far = (
        1.25331414
        + u * (-0.07832358 + u * (0.02189568 + u * (-0.01062446 + u * (0.00587872 + u * (-0.00251540 + u * 0.00053208)))))
    ) / (np.sqrt(far_x) * np.exp(far_x))
    return np.where(small, near, far)


def k1(x: object) -> np.ndarray:
    """Modified Bessel K₁ (A&S 9.8.7, 9.8.8)."""
    a = _asarray(x, "k1", positive=True)
    small = a <= 2.0
    near_x = np.where(small, a, 2.0)
    t = (near_x / 2.0) ** 2
    near = (
        near_x * np.log(near_x / 2.0) * i1(near_x)
        + 1.0
        + t * (0.15443144 + t * (-0.67278579 + t * (-0.18156897 + t * (-0.01919402 + t * (-0.00110404 - t * 0.00004686)))))
    ) / near_x
    far_x = np.where(small, 2.0, a)
    u = 2.0 / far_x
    far = (
        1.25331414
        + u * (0.23498619 + u * (-0.03655620 + u * (0.01504268 + u * (-0.00780353 + u * (0.00325614 - u * 0.00068245)))))
    ) / (np.sqrt(far_x) * np.exp(far_x))
    return np.where(small, near, far)


# --- the error function (A&S 7.1.26) -----------------------------------------

_ERF_P = 0.3275911
_ERF_A = (0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429)


def erf(x: object) -> np.ndarray:
    """The error function, |ε| < 1.5×10⁻⁷ ``[recall: A&S 7.1.26]``. Odd, so |x| is enough."""
    v = np.asarray(x, dtype=float)
    a = np.abs(v)
    t = 1.0 / (1.0 + _ERF_P * a)
    poly = t * (_ERF_A[0] + t * (_ERF_A[1] + t * (_ERF_A[2] + t * (_ERF_A[3] + t * _ERF_A[4]))))
    return np.sign(v) * (1.0 - poly * np.exp(-a * a))


def normal_cdf(x: object) -> np.ndarray:
    """P(Z ≤ x) for a standard normal — the shape a threshold on a log-normal takes."""
    return 0.5 * (1.0 + erf(np.asarray(x, dtype=float) / np.sqrt(2.0)))
