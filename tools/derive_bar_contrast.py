"""Derive the Milky Way template's bar amplitude from the Galaxy's printed non-axisymmetric long-bar mass (S99, debt
#146; DECISIONS.md D268 ruling 8; the gate's rulings 1, 2 and 5 of S99).

    uv run python tools/derive_bar_contrast.py            # the scan, the root-find, the value to four figures
    uv run python tools/derive_bar_contrast.py --check    # the committed value's measure, no search

**What is solved.** The amplitude B (``bar_contrast``) at which ``galaxy.specs.bar_mass.measure`` on the finished
model - ``template=milky_way`` with B in place of its pin, the randomness layer on (with it off the stellar density is
round every ring and the measure 0 by construction) - reads Portail et al. 2017's 0.46 x 10^10 Msun (the bulge cut
the paper's own ellipse, 2.2 x 1.4 kpc). Nothing else of the template moves: its other pins, its seeds and every
constant are as committed (rules C6, B5: no cap, axis ratio or constant moves to make it fit).

**How.** The bracket is the pin's whole range, 0 to the draw's cap ``BAR_CONTRAST_CAP`` (0.9). The measure is first
read at ``SCAN`` evenly spaced amplitudes over it; **the tool refuses** - and says which of the gate's stop conditions
is met - if the measure is not strictly increasing over the scan, or if the target lies outside the scan's values
(beyond the cap, or out of the body's reach). Then the Illinois variant of regula falsi inside the scan's bracketing
pair, to ``TOLERANCE`` in B, deterministic, numpy alone. The value is stored to four significant figures
(``model/galaxy/templates.py``, the ``bar_contrast`` pin) and the template's own measure at that value is what
``tests/test_bar_mass.py`` holds inside the source's +/- 0.03 x 10^10.
"""

from __future__ import annotations

import argparse
import math
import sys

import numpy as np

from galaxy import templates
from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs import bar_mass
from galaxy.stages.pattern import BAR_CONTRAST_CAP

SCAN = 7
TOLERANCE = 1e-6
MAX_STEPS = 60


def inputs(amplitude: float) -> dict:
    """``template=milky_way``'s inputs with its amplitude pin at ``amplitude``."""
    return {**templates.overrides(templates.MILKY_WAY), "bar_contrast": float(amplitude)}


def measured(model, amplitude: float) -> dict[str, float]:
    """bar_mass.measure on the finished model at ``amplitude``, the layer on (rule D4: the fields it reads)."""
    return bar_mass.measure(run(model, inputs(amplitude), only=bar_mass.READS))


class Refused(RuntimeError):
    """A stop condition of the gate's ruling 6 is met: nothing is derived."""


def derive(model=None, target: float = bar_mass.PORTAIL_NON_AXISYMMETRIC_MASS, lo: float = 0.0,
           hi: float = BAR_CONTRAST_CAP, say=print) -> tuple[float, list[tuple[float, float]]]:
    """(B, the (B, M) pairs read): the amplitude at which the measure reads ``target`` Msun inside [lo, hi]."""
    model = model or production()[0].get(DEFAULT_MODEL)
    seen: list[tuple[float, float]] = []

    def m(b: float) -> float:
        value = measured(model, b)["mass"]
        seen.append((b, value))
        say(f"  B = {b:.9f}: M = {value / 1e10:.6f} e10 Msun")
        return value - target

    grid = np.linspace(lo, hi, SCAN)
    values = [m(float(b)) for b in grid]
    if not all(b > a for a, b in zip(values, values[1:])):
        raise Refused("the measure is not monotone in the amplitude over the bracket (ruling 6)")
    if values[-1] < 0.0:
        raise Refused(f"the target needs an amplitude beyond the cap {hi} (ruling 6): M({hi}) = {(values[-1] + target) / 1e10:.4f} e10")
    if values[0] > 0.0:
        raise Refused("the target lies below the measure at the bracket's foot (ruling 6)")
    k = next(i for i in range(SCAN - 1) if values[i] <= 0.0 <= values[i + 1])
    a, b, fa, fb = float(grid[k]), float(grid[k + 1]), values[k], values[k + 1]
    for _ in range(MAX_STEPS):
        c = (a * fb - b * fa) / (fb - fa)
        fc = m(c)
        if fc * fb < 0.0:
            a, fa = b, fb
        else:
            fa = fa / 2.0  # Illinois: the end that stays is halved, so both ends close in
        b, fb = c, fc
        if fc == 0.0 or abs(b - a) < TOLERANCE or abs(fc) < 1e-6 * target:
            break
    root = b if abs(fb) <= abs(fa) else a
    return root, seen


def four_figures(x: float) -> float:
    return float(f"{x:.4g}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="the committed value's measure, no search")
    args = parser.parse_args(argv)
    model = production()[0].get(DEFAULT_MODEL)
    committed = float(templates.pinned(templates.MILKY_WAY)["bar_contrast"])
    if not args.check:
        try:
            root, _ = derive(model)
        except Refused as stop:
            print("REFUSED:", stop)
            return 2
        print(f"root B = {root:.9f}; to four figures {four_figures(root)} (committed {committed})")
    m = measured(model, committed)
    print(f"committed B = {committed}: " + ", ".join(f"{k} {v:.6g}" for k, v in m.items()))
    off = abs(m["mass"] - bar_mass.PORTAIL_NON_AXISYMMETRIC_MASS) / bar_mass.PORTAIL_NON_AXISYMMETRIC_ERROR
    print(f"the committed value's measure is {off:.3f} of the source's error from the target")
    return 0 if math.isfinite(off) else 1


if __name__ == "__main__":
    sys.exit(main())
