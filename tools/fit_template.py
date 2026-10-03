"""Fit a template's seven controls to its measured targets (BUILD_III Phase T; DECISIONS.md D213, ruling 3).

    uv run python tools/fit_template.py ngc_4414
    uv run python tools/fit_template.py ngc_4414 --check     # the committed values' residuals, no search

**What is minimised** is the template's own objective, exactly as D213 fixes it: the sum over the
targets of the squared residual in units of the target's half-window, plus ``Fit.tiebreak`` (10^-3)
times the sum over the controls of the squared departure from the registry's default in units of the
control's published range. Three numbers do not fix seven controls; the tie-break keeps a control
nothing measures at the Milky Way's value. The template's seeds and merger list are held as the
template states them.

**The search** is numpy alone, deterministic, bounded by the published ranges, with every count fixed
in advance. From the registry's defaults it takes ``ITERATIONS`` steps. A step differences the three
targets in each control (two model evaluations per control: central, or a one-sided pair where a
control stands within the width of a bound), at a width that cycles through ``FD_STEPS``, and then
tries ``len(DAMPING)`` damped Gauss-Newton (Levenberg-Marquardt) steps of the linearised sum of
squares, each solved with the controls held inside their ranges (:func:`bounded_step`). It moves to
the lowest objective among those trial points *and the differencing points themselves* - so every
step is also a coordinate search at that width - and only if that is lower than where it stands.
The number of model evaluations is ``1 + ITERATIONS * (2 * controls + len(DAMPING))`` whatever
happens.

**The search's coordinates** are the logarithm of every control whose range starts above zero and
the control itself otherwise (:class:`Problem`). The coordinates are the search's own; the objective
is D213's, each departure counted in the control's own linear range.

*Why this and not a coordinate search or a simplex alone:* the objective is a sum of squares in a
long valley - the targets confine it across, and along it (less halo, more of the baryons kept) the
objective falls slowly - which a coordinate search crosses slowest and Gauss-Newton fastest. *Why
not Gauss-Newton alone:* the model's three numbers are not continuous in ``halo_mass`` and
``disc_spin``. They carry steps of up to 0.014 half-windows about every 0.003 of the range (probed
at S54 before the first fit: quantities snapped to the radial grid), so a narrow difference reads a
tooth and not the trend, and a Gauss-Newton step judged on a stepped objective can be refused for
ever. Three earlier forms of this search were run and discarded for where they stopped, not for what
they found: steps clipped after the solve (0.77: not a descent direction on a bound); one width and
the trial steps only (0.25, where another start reached 0.20); the controls themselves as
coordinates (still creeping at 0.246 after 24 steps: the valley is a hyperbola in the controls and
near a line in their logarithms).

**An evaluation is cheap** because it runs only the closure above the targets' fields
(``run(..., only=...)``, rule D4) on the production grid.

**Nothing is written.** The tool prints the residuals table, the controls table and the literals to
copy into ``galaxy/templates.py`` by hand with the date; ``tests/test_templates.py`` checks that the
committed values are where the search stops and reproduce the committed model numbers. **A target
the search cannot reach is a finding**: it is printed and published, and no window or weight is
moved to remove it (rule B5; BUILD_III section 9).
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

ITERATIONS = 24  # steps: eight cycles of the three widths
# The differencing widths, in units of each search coordinate's span, cycled step by step. Wide first: a
# difference over 0.08 of the span crosses some twenty of the model's teeth and reads the trend to about
# 1 %, one over 0.02 crosses five and reads it to a few per cent.
FD_STEPS = (4e-2, 2e-2, 1e-2)
DAMPING = (0.0, 0.1, 1.0, 10.0)  # the trial steps' damping, in units of the normal matrix's own diagonal
METHOD = (
    f"damped Gauss-Newton (Levenberg-Marquardt) with a coordinate search in every step: {ITERATIONS} steps from the "
    "registry's defaults, in the logarithm of each control whose range starts above zero, the targets differenced in "
    f"each coordinate at {', '.join(f'{h:g}' for h in FD_STEPS)} of its span in turn, {len(DAMPING)} damped trial "
    "steps solved inside the published ranges, the lowest of the trial and differencing points taken when it is lower"
)


@dataclass(frozen=True)
class Result:
    controls: dict[str, float]  # the fitted values, in the registry's order
    model: dict[str, float]  # target name -> the model's number there
    residuals: dict[str, float]  # target name -> (model - value) / half-window
    objective: float
    misfit: float  # the targets' part of the objective
    tiebreak: float  # the controls' part, weight included
    evaluations: int
    seconds: float
    history: tuple[float, ...]  # the objective after each step


class Problem:
    """A template's fit as a function of the search coordinates ``s`` in [0, 1], one per control.

    A control whose range starts above zero is searched in its logarithm (``s`` runs evenly in log from lo to
    hi), the others linearly: the targets are near power laws of the positive controls - the stellar mass
    goes as the halo's mass times the share of the baryons kept, the scale length as the spin times the cube
    root of the halo's mass - so the valley the search follows is a hyperbola in the controls and near a line
    in their logarithms. The coordinates are the search's own; the objective is D213's, with every departure
    from a default counted in the control's own linear range (:meth:`departures`).
    """

    def __init__(self, template: Any, grid: Any = None) -> None:
        from galaxy.core.registry import controls, production
        from galaxy.run import run

        if template.fit is None:
            raise SystemExit(f"template {template.name!r} is not a fitted one: it states no targets")
        models, _, table = production()
        self._run = run
        self.template = template
        self.model = models.get(template.model)
        self.controls = [c for c in controls(table) if c.name in self.model.input_names(table)]
        if any(not c.has_range or c.unset for c in self.controls):
            raise SystemExit("every control needs a default and a published range to be fitted")
        self.lo = np.array([c.lo for c in self.controls], dtype=float)
        self.hi = np.array([c.hi for c in self.controls], dtype=float)
        self.span = self.hi - self.lo
        self.default = np.array([c.default for c in self.controls], dtype=float)
        self.log = self.lo > 0.0
        self._floor = np.where(self.log, self.lo, 1.0)
        self.decades = np.where(self.log, np.log(self.hi / self._floor), 1.0)  # ln(hi / lo) where searched in log
        self.s0 = self.s_of({c.name: c.default for c in self.controls})
        self.targets = template.fit.targets
        self.weight = float(template.fit.tiebreak)
        self.fields = tuple(dict.fromkeys(t.field for t in self.targets))
        # What the fit does not move: the template's seeds and its merger list.
        self.held = {**template.seeds, **({} if template.mergers is None else {"mergers": template.mergers})}
        self.grid = grid
        self.evaluations = 0

    def s_of(self, values: Mapping[str, float]) -> np.ndarray:
        x = np.array([values[c.name] for c in self.controls], dtype=float)
        return np.where(self.log, np.log(np.where(self.log, x, 1.0) / self._floor) / self.decades, (x - self.lo) / self.span)

    def x_of(self, s: np.ndarray) -> np.ndarray:
        s = np.asarray(s, dtype=float)
        x = np.where(self.log, self._floor * np.exp(s * self.decades), self.lo + s * self.span)
        # A coordinate on its bound is the control on its bound, exactly: exp(log(hi / lo)) is not hi / lo.
        return np.where(s >= 1.0, self.hi, np.where(s <= 0.0, self.lo, np.clip(x, self.lo, self.hi)))

    def values(self, s: np.ndarray) -> dict[str, float]:
        return {c.name: float(v) for c, v in zip(self.controls, self.x_of(s))}

    def departures(self, s: np.ndarray) -> np.ndarray:
        """Each control's departure from its default in units of its published range: the tie-break's terms."""
        return (self.x_of(s) - self.default) / self.span

    def departure_slopes(self, s: np.ndarray) -> np.ndarray:
        """d departure / d s, for the linearised tie-break."""
        return np.where(self.log, self.x_of(s) * self.decades / self.span, 1.0)

    def model_numbers(self, s: np.ndarray) -> np.ndarray:
        """The model's number for each target at ``s``: one run of the closure above the targets' fields."""
        from galaxy.templates import measure

        self.evaluations += 1
        out = self._run(self.model, {**self.held, **self.values(s)}, self.grid, only=self.fields)
        return np.array([
            measure(t.statistic, out.fields[t.field], out.grid.R, t.inside_kpc) for t in self.targets
        ])

    def residuals_of(self, numbers: np.ndarray) -> np.ndarray:
        return np.array([t.residual_of(m) for t, m in zip(self.targets, numbers)])

    def parts(self, r: np.ndarray, s: np.ndarray) -> tuple[float, float]:
        """(the targets' squared residuals, the weighted squared departures from the defaults)."""
        d = self.departures(s)
        return float(r @ r), self.weight * float(d @ d)

    def objective(self, r: np.ndarray, s: np.ndarray) -> float:
        return sum(self.parts(r, s))

    def probe(self, s: np.ndarray) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
        """One evaluation: (the objective, the point, the model's numbers, the residuals) at ``s``."""
        numbers = self.model_numbers(s)
        r = self.residuals_of(numbers)
        return self.objective(r, s), s, numbers, r

    def jacobian(self, s: np.ndarray, r: np.ndarray, h: float) -> tuple[np.ndarray, list]:
        """d residual / d s at width ``h``, two evaluations per control: central, or a one-sided pair where the
        control is within ``h`` of a bound. Returns the differencing points too, each as :meth:`probe` gives it."""
        J = np.zeros((len(self.targets), s.size))
        probes = []
        for j in range(s.size):
            step = np.zeros(s.size)
            step[j] = h
            if s[j] - h < 0.0:
                a, b = self.probe(s + step), self.probe(s + 2.0 * step)
                J[:, j] = (-3.0 * r + 4.0 * a[3] - b[3]) / (2.0 * h)
            elif s[j] + h > 1.0:
                a, b = self.probe(s - step), self.probe(s - 2.0 * step)
                J[:, j] = (3.0 * r - 4.0 * a[3] + b[3]) / (2.0 * h)
            else:
                a, b = self.probe(s + step), self.probe(s - step)
                J[:, j] = (a[3] - b[3]) / (2.0 * h)
            probes += [a, b]
        return J, probes


def bounded_step(normal: np.ndarray, rhs: np.ndarray, s: np.ndarray, damping: float) -> np.ndarray:
    """The step that minimises the damped linearised objective with every coordinate kept inside [0, 1].

    Marquardt's damping (``damping`` times the normal matrix's own diagonal), and the bounds by an active
    set: solve for the free coordinates; of those the solution carries out of range, hold on its bound the
    one that reaches its bound first along the step; solve again for the rest; at most once per coordinate.
    A step clipped after the solve instead is not a descent direction once a control stands on its bound -
    the first form of this search stalled there.
    """
    n = s.size
    M = normal + damping * np.diag(np.diag(normal))
    delta = np.zeros(n)
    free = np.ones(n, dtype=bool)
    for _ in range(n):
        held = ~free
        solved = np.linalg.solve(M[np.ix_(free, free)], rhs[free] - M[np.ix_(free, held)] @ delta[held])
        trial = s[free] + solved
        out = (trial < 0.0) | (trial > 1.0)
        if not out.any():
            delta[free] = solved
            break
        # The fraction of the step each offender completes before its bound: the smallest is reached first.
        bound = np.where(trial < 0.0, 0.0, 1.0)
        reach = np.where(out, (bound - s[free]) / np.where(out, solved, 1.0), np.inf)
        first = int(np.argmin(reach))  # the first of equals: deterministic
        index = np.flatnonzero(free)[first]
        delta[index] = bound[first] - s[index]
        free[index] = False
        if not free.any():
            break
    return delta


def fit(
    template: Any, grid: Any = None, *, start: Mapping[str, float] | None = None, iterations: int = ITERATIONS,
) -> Result:
    """The search, from the registry's defaults. Deterministic; the evaluation count is fixed.

    ``start`` and ``iterations`` are for probing the search itself (another starting point, a longer run);
    the committed fit is the one with neither given.
    """
    began = time.perf_counter()
    p = Problem(template, grid)
    s = p.s0.copy() if start is None else p.s_of(start)
    best, _, numbers, r = p.probe(s)
    history = []
    root = float(np.sqrt(p.weight))
    for k in range(iterations):
        J, candidates = p.jacobian(s, r, FD_STEPS[k % len(FD_STEPS)])
        # The whole residual vector: the targets, then the tie-break's sqrt(weight) * departure.
        A = np.vstack([J, root * np.diag(p.departure_slopes(s))])
        rho = np.concatenate([r, root * p.departures(s)])
        normal, rhs = A.T @ A, -A.T @ rho
        for damping in DAMPING:
            candidates.append(p.probe(np.clip(s + bounded_step(normal, rhs, s, damping), 0.0, 1.0)))
        lowest = min(candidates, key=lambda c: c[0])  # the first of equals: deterministic
        if lowest[0] < best:
            best, s, numbers, r = lowest
        history.append(best)
    misfit, tiebreak = p.parts(r, s)
    return Result(
        controls=p.values(s),
        model={t.name: float(m) for t, m in zip(p.targets, numbers)},
        residuals={t.name: float(x) for t, x in zip(p.targets, r)},
        objective=best, misfit=misfit, tiebreak=tiebreak,
        evaluations=p.evaluations, seconds=time.perf_counter() - began, history=tuple(history),
    )


def at(template: Any, values: Mapping[str, float] | None = None, grid: Any = None) -> Result:
    """The objective and the targets at given control values (the template's own by default): what the test of
    the committed fit reads. One model evaluation, no search."""
    from galaxy.templates import resolve

    began = time.perf_counter()
    p = Problem(template, grid)
    s = p.s_of(resolve(template) if values is None else values)
    best, _, numbers, r = p.probe(s)
    misfit, tiebreak = p.parts(r, s)
    return Result(
        controls=p.values(s),
        model={t.name: float(m) for t, m in zip(p.targets, numbers)},
        residuals={t.name: float(x) for t, x in zip(p.targets, r)},
        objective=best, misfit=misfit, tiebreak=tiebreak,
        evaluations=p.evaluations, seconds=time.perf_counter() - began, history=(),
    )


def tables(template: Any, result: Result) -> str:
    """The residuals table and the controls table, as the decision record carries them."""
    from galaxy.core.registry import INPUTS

    lines = [f"fit of template {template.name} ({template.label}), model {template.model}", "", "residuals"]
    head = f"  {'target':<20} {'window':<24} {'measured':>12} {'model':>12} {'residual':>10}  verdict"
    lines += [head, "  " + "-" * (len(head) - 2)]
    for t in template.fit.targets:
        m = result.model[t.name]
        window = f"[{t.window[0]:.6g}, {t.window[1]:.6g}] {t.unit}"
        verdict = "inside" if t.holds(m) else "OUTSIDE its window: a finding, published and not tuned away (B5)"
        lines.append(f"  {t.name:<20} {window:<24} {t.value:>12.6g} {m:>12.6g} {result.residuals[t.name]:>+10.4f}  {verdict}")
    lines.append("  (residual = (model - measured) / half-window; a window's half-width is (hi - lo) / 2)")
    lines += ["", "controls"]
    head = f"  {'control':<22} {'default':>12} {'fitted':>14} {'lo':>9} {'hi':>9} {'moved / range':>14}"
    lines += [head, "  " + "-" * (len(head) - 2)]
    for name, value in result.controls.items():
        inp = INPUTS[name]
        moved = (value - inp.default) / (inp.hi - inp.lo)
        edge = "  at its bound" if value <= inp.lo or value >= inp.hi else ""
        lines.append(f"  {name:<22} {inp.default:>12.6g} {value:>14.8g} {inp.lo:>9.4g} {inp.hi:>9.4g} {moved:>+14.5f}{edge}")
    lines += [
        "",
        f"objective {result.objective:.6f} = targets {result.misfit:.6f} + tie-break {result.tiebreak:.6f} "
        f"(weight {template.fit.tiebreak:g})",
    ]
    if result.history:
        lines.append("objective after each step: " + " ".join(f"{h:.4f}" for h in result.history))
        moved = [k for k, (a, b) in enumerate(zip((float("inf"), *result.history), result.history), start=1) if b < a]
        last = moved[-1] if moved else 0
        lines.append(
            f"the last step that lowered it was step {last} of {len(result.history)}: the {len(result.history) - last} "
            "after it found no lower point at any width"
        )
    return "\n".join(lines)


def literals(template: Any, result: Result) -> str:
    """What is copied into galaxy/templates.py by hand."""
    lines = ["to copy into galaxy/templates.py (controls, then each target's model and residual, then the objective):"]
    lines += [f'        "{name}": {value!r},' for name, value in result.controls.items()]
    for t in template.fit.targets:
        lines.append(f"    {t.name}: model={result.model[t.name]!r}, residual={result.residuals[t.name]!r},")
    lines.append(f"    objective_value={result.objective!r}, evaluations={result.evaluations},")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Fit a template's controls to its measured targets (D213).")
    parser.add_argument("template", help="a fitted template's name, e.g. ngc_4414")
    parser.add_argument("--check", action="store_true", help="no search: the committed values' residuals")
    args = parser.parse_args(argv)

    from galaxy import templates

    if args.template not in templates.TEMPLATES:
        raise SystemExit(f"no template {args.template!r}; registered: {list(templates.TEMPLATES)}")
    template = templates.TEMPLATES[args.template]
    result = at(template) if args.check else fit(template)
    print(tables(template, result))
    print()
    print(f"method: {'the committed values, no search' if args.check else METHOD}")
    print(f"model evaluations: {result.evaluations}; wall time {result.seconds:.1f} s")
    if not args.check:
        print()
        print(literals(template, result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
