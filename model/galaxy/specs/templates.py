"""A template's blind checks, judged (BUILD_III Phase T; DECISIONS.md D213, ruling 6).

A fitted template states measured properties its fit never saw, each with the window a reader fixed
before any model output for that galaxy existed (``galaxy/templates.py``; rule D113). This module runs
the template on the production grid, reads the model's quantity for each and says pass or fail.

**These are not acceptance rows.** They are reported in their own table, after the acceptance table
and apart from it, and are never counted among its rows: an acceptance row judges the default galaxy
against the Milky Way, a check judges one template against its own galaxy. The convention is the
acceptance table's all the same (``spec.MISSES``): a failing check is a recorded miss with its debt
and its reason in :data:`CHECK_MISSES`, it still prints ``fail`` (rule B5 relaxes nothing) and the run
stays green on it; a failing check with no entry fails the run, and so does a recorded miss that has
started passing — the recorded explanation is then wrong or spent.

**A verdict says whether it is blind.** A check's window was fixed blind; a verdict is blind only if
the fit it is read on was fixed before any check was read. ``ngc_4414``'s five were read once on its
first fit ("fit A", D213), which was then withdrawn for a defect in its objective, so every verdict
on the fit that stands is **disclosed** (D192: read is read) and prints that word in its row, with
fit A's value and verdict - the blind reading, spent - beside it.

**The colour check is the render's frame.** B − V "face-on, through the dust" is what the viewer draws
of a face-on disc: ``/api/render``'s stars through the table's own B and V, each cell's light through
its own mixed dust with the scattered light and the thermal emission composed in, summed over the
frame with the bulge, each band turned into a Vega magnitude. The four functions that do it
(:func:`cell_areas`, :func:`band_magnitude`, :func:`frame_total`, :func:`face_on`) were
``tests/test_render.py``'s until S54 and are the ones it still pins the default galaxy's frame with:
one computation, two readers.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy import templates as _templates
from galaxy.specs import Problem, utf8_stdout

STATUSES = ("pass", "fail", "not-yet-computable")


# --- the frame's photometry (tests/test_render.py's, until S54) ----------------------------


def cell_areas(header: Mapping[str, Any]) -> np.ndarray:
    """pc² of every (R, φ) cell of a render's window: R dR dφ at the cell's centre radius."""
    from galaxy.stages.disc import PC_PER_KPC

    r_axis, phi_axis = header["window"]["R"], header["window"]["phi"]
    R = r_axis["lo"] + (np.arange(r_axis["n"]) + 0.5) * r_axis["width"]
    return (R * r_axis["width"] * phi_axis["width"] * PC_PER_KPC**2)[:, None] * np.ones(phi_axis["n"])


def band_magnitude(response: Any, band: str) -> np.ndarray:
    """A Vega magnitude from a response through ``band_curve(band)``: the mean L_λ over the curve against a
    zero-magnitude source's at 10 pc (``photometry.band_nu_l_nu`` of unit flux over the reference wavelength)."""
    from galaxy.stages import spectra
    from galaxy.stages.photometry import PASSBANDS, band_nu_l_nu

    curve = spectra.band_curve(band)
    lam = curve.grid()
    mean = np.asarray(response) / np.trapezoid(curve.at(lam), lam)
    zero = float(band_nu_l_nu(np.array(1.0), band)) / PASSBANDS[band].reference
    return -2.5 * np.log10(mean / zero)


def frame_total(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> np.ndarray:
    """Each filter's response summed over the frame's cells, plus the bulge's: L☉."""
    return (arrays["stars"] * cell_areas(header)[..., None]).sum(axis=(0, 1)) + np.asarray(header["bulge"])


def face_on(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> dict[str, Any]:
    """The frame's stars with the dust composed face-on (S39): light mixed through its own dust leaves (1 − T)/τ
    of itself, τ = −ln T the column's depth in each filter; the scattered light joins it at the face-on phase
    factor; the thermal emission is added undimmed (optically thin)."""
    tau = -np.log(arrays["dust_extinction"])[:, None, :]
    own = np.where(tau > 1e-12, -np.expm1(-tau) / np.where(tau > 1e-12, tau, 1.0), 1.0)
    phase = header["components"]["dust_scattered"]["phase"]["factor"][-1]
    lit = (arrays["stars"] + phase * arrays["dust_scattered"]) * own + arrays["dust_thermal"][:, None, :]
    return {**arrays, "stars": lit}


FACE_ON_BANDS = ("B", "V")
FACE_ON_NEEDS = ("stars", "dust_extinction", "dust_scattered", "dust_thermal")


def face_on_colour(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> float:
    """B − V of a render's frame through its dust, the render having been asked for the table's B and V."""
    dimmed = frame_total(header, face_on(header, arrays))
    return float(band_magnitude(dimmed[0], FACE_ON_BANDS[0]) - band_magnitude(dimmed[1], FACE_ON_BANDS[1]))


# --- the ledger ----------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CheckMiss:
    """A check the model is known not to meet, with the reason on the record (rule B5)."""

    debt: int  # entry in the calibration debt register, GALAXY_INPUTS.md section 11
    since: str  # the session that measured the miss
    reason: str
    prediction: str = ""  # what would change it, stated so that it can fail (rule B4)

    def __post_init__(self) -> None:
        if self.debt < 1 or not self.since.startswith("S"):
            raise ValueError("a recorded miss needs a debt number and a session")
        if not self.reason.strip():
            raise ValueError("a recorded miss needs a reason")


# template name -> check name -> its recorded miss. An entry is the lead's: it carries the debt's
# number, which is taken when the entry is written (never reserved), e.g.
#     "ngc_4414": {"curve_shape": CheckMiss(debt=<n>, since="S54", reason="...", prediction="...")},
CHECK_MISSES: Mapping[str, Mapping[str, CheckMiss]] = {
    # S54 (D213, as amended at the gate): all five read on the refit, every verdict disclosed. No third fit of
    # this template is made in the build, so each miss stands until the model changes under it.
    "ngc_4414": {
        "curve_shape": CheckMiss(
            debt=132,
            since="S54",
            reason=(
                "0.653 against [0.71, 0.86]: the curve falls too far. The fit holds the peak down by assembling "
                "the halo as late as the range allows (the assembly epoch on its bound), and a halo that weak "
                "leaves the outer curve low: the peak and the shape pull the one control opposite ways."
            ),
            prediction=(
                "A halo whose concentration can fall without its outer mass falling - the concentration floor, or "
                "the concentration-mass relation - lifts the shape toward the window at the same peak; a shape "
                "that stays low with the assembly epoch inside its range kills this."
            ),
        ),
        "star_formation_rate": CheckMiss(
            debt=134,
            since="S54",
            reason=(
                "0.653 against [1.8, 4.7] Msun/yr: no fit target measures a history, so the two history controls "
                "are the Milky Way's, and at them a disc this compact has burnt its gas."
            ),
            prediction=(
                "With a gas measurement among the targets (the reader's own split, the owner's to order) the "
                "history controls are measured and the rate rises with the gas; a rate still under 1.8 at the "
                "measured hydrogen mass kills this and puts the miss in the star formation law."
            ),
        ),
        "hydrogen_mass": CheckMiss(
            debt=134,
            since="S54",
            reason=(
                "4.80e9 against [7.4, 14.7]e9 Msun: the same reservoir as the star formation rate's miss. The "
                "window also holds HI beyond the model's 30 kpc edge (28 % of it lies past 20.6 kpc)."
            ),
            prediction="As the star formation rate's: the two move together or the reading of one cause is wrong.",
        ),
        "absolute_magnitude_k": CheckMiss(
            debt=135,
            since="S54",
            reason=(
                "-23.27 against [-24.62, -24.12], 0.85 mag faint, with the stellar mass 0.06 dex under the "
                "measured one: about 0.15 mag is the mass and the rest is the model's K light per unit stellar "
                "mass, which is low on the default galaxy too (-23.77 at 4.75e10 Msun)."
            ),
            prediction=(
                "The default galaxy's K-band mass-to-light ratio read against a sourced one closes it or names "
                "the isochrones' K band; a K light per unit mass inside the sourced range kills this."
            ),
        ),
        "colour_b_v_face_on": CheckMiss(
            debt=136,
            since="S54",
            reason=(
                "0.636 against [0.72, 0.82]: the face-on frame through the dust is bluer than the catalogues' "
                "face-on colour, as the default galaxy's is (0.57)."
            ),
            prediction=(
                "The window is corrected to face-on by a formula in the axis ratio and still holds the face-on "
                "dust; a model frame with the dust's reddening applied as the catalogues' correction leaves it "
                "would land inside, and one that stays bluer than 0.72 puts the miss in the stars' colour."
            ),
        ),
    },
}


# --- the evaluation ------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Result:
    template: str
    name: str
    label: str
    status: str
    reason: str
    value: float | None = None
    standing: str = "blind"  # blind | disclosed: the template's own word for this check
    first: Any = None  # the check's first reading on a withdrawn fit (templates.FirstReading), where it has one


def judge(template: _templates.Template, check: _templates.Check, value: float | None, why: str = "") -> Result:
    """One check against its window. ``value`` None is "the model does not publish this" (rule B9)."""
    kept = {"standing": check.standing, "first": check.first_reading}
    if value is None or not np.isfinite(value):
        return Result(template.name, check.name, check.label, "not-yet-computable",
                      why or "the model publishes no number for it", **kept)
    ok = check.holds(value)
    lo, hi = check.window
    return Result(
        template.name, check.name, check.label, "pass" if ok else "fail",
        f"{value:.6g} {'in' if ok else 'not in'} [{lo:.6g}, {hi:.6g}] {check.unit}", float(value), **kept,
    )


def evaluate_template(template: _templates.Template, service: Any) -> list[Result]:
    """Run ``template`` far enough to read each of its checks, on ``service``'s grid, and judge them.

    The field checks read the closure above their fields (rule D4); the colour check reads the render the
    viewer would be sent for this template, through the table's B and V.
    """
    if not template.checks:
        return []
    if template.model not in service.models:
        return [judge(template, c, None, f"model {template.model!r} is not registered") for c in template.checks]
    model = service.models.get(template.model)
    declared = service._declared(model)
    fields = tuple(dict.fromkeys(c.field for c in template.checks if c.field is not None and c.field in declared))
    out, _ = service.compute(model, _templates.overrides(template), fields)
    results: list[Result] = []
    for check in template.checks:
        if check.statistic == "face_on_colour":
            results.append(judge(template, check, *_frame_colour(template, service)))
        elif check.field not in out.fields:
            results.append(judge(template, check, None, f"field {check.field!r} is not published by model {model.name!r}"))
        else:
            value = _templates.measure(check.statistic, out.fields[check.field], out.grid.R, check.inside_kpc)
            results.append(judge(template, check, value))
    return results


def _frame_colour(template: _templates.Template, service: Any) -> tuple[float | None, str]:
    from galaxy.stages import spectra

    curves = json.dumps([spectra.band_curve(b).json() for b in FACE_ON_BANDS])
    got = service.handle("/api/render", {"template": [template.name], "model": [template.model], "filters": [curves]})
    if not got.ok:
        return None, f"/api/render answered {got.status} for this template"
    header, arrays = got.frame()
    missing = [n for n in FACE_ON_NEEDS if n not in arrays]
    if missing or header.get("bulge") is None:
        return None, f"the render carries no {missing or 'bulge'}, so the frame has no dust to be seen through"
    return face_on_colour(header, arrays), ""


def evaluate(names: Iterable[str] | None = None, *, service: Any = None, grid: Any = None) -> dict[str, list[Result]]:
    """Every template's checks (or ``names``'), each template on the production grid unless ``grid`` says otherwise."""
    if service is None:
        from galaxy.api.service import Service

        service = Service() if grid is None else Service(grid=grid)
    wanted = tuple(_templates.TEMPLATES) if names is None else tuple(names)
    return {name: evaluate_template(_templates.get(name), service) for name in wanted}


def summary(results: Iterable[Result]) -> dict[str, int]:
    counts = {s: 0 for s in STATUSES}
    for r in results:
        counts[r.status] += 1
    return counts


def problems(
    results: Mapping[str, list[Result]], ledger: Mapping[str, Mapping[str, CheckMiss]] | None = None,
) -> list[Problem]:
    """Everything a spec run should fail on. A recorded, still-failing check is not one."""
    ledger = CHECK_MISSES if ledger is None else ledger
    out: list[Problem] = []
    for template, judged in results.items():
        known = ledger.get(template, {})
        for r in judged:
            if r.status == "fail" and r.name not in known:
                out.append(Problem(
                    template, "template-check",
                    f"check {r.name} ({r.label}) fails and is not a recorded miss for template {template!r}: {r.reason}",
                ))
            if r.status == "pass" and r.name in known:
                out.append(Problem(
                    template, "stale-check-miss",
                    f"check {r.name} ({r.label}) is registered as a miss for template {template!r} since "
                    f"{known[r.name].since} (debt #{known[r.name].debt}) but now passes: {r.reason}. "
                    "Remove the entry or find out why.",
                ))
        for name in known:
            if name not in {r.name for r in judged}:
                out.append(Problem(template, "unknown-check-miss", f"the ledger names check {name!r}, which template {template!r} does not state"))
    for template in ledger:
        if template not in results and template not in _templates.TEMPLATES:
            out.append(Problem(template, "unknown-check-miss", f"the ledger names template {template!r}, which is not registered"))
    return out


def report(
    results: Mapping[str, list[Result]] | None = None, ledger: Mapping[str, Mapping[str, CheckMiss]] | None = None,
) -> str:
    ledger = CHECK_MISSES if ledger is None else ledger
    if results is None:
        results = evaluate()
    lines = [
        "template checks",
        "  NOT acceptance rows: each is a measured property of one template's own galaxy that its fit never saw, on a",
        "  window fixed before the model's number existed (D213). Reported beside the acceptance table, never counted in it.",
        "  A verdict marked disclosed is read on a fit decided after the check had already been read once: it is not",
        "  blind. That first reading - blind, spent, on a fit since withdrawn - is printed beside it.",
    ]
    for name, judged in results.items():
        template = _templates.get(name)
        if not judged:
            lines.append(f"  template {name} ({template.label}): states no checks")
            continue
        s = summary(judged)
        known = ledger.get(name, {})
        recorded = sum(1 for r in judged if r.status == "fail" and r.name in known)
        head = (
            f"  template {name} ({template.label}), model {template.model}: {s['pass']} pass, {s['fail']} fail, "
            f"{s['not-yet-computable']} not-yet-computable of {len(judged)} checks"
        )
        if recorded:
            head += f" ({recorded} of the failures recorded as misses)"
        lines.append(head)
        width = max(len(r.name) for r in judged)
        for r in judged:
            tag = ""
            if r.name in known and r.status == "fail":
                tag = f" [recorded miss, debt #{known[r.name].debt}, since {known[r.name].since}]"
            first = ""
            if r.first is not None:
                first = f"; first reading ({r.first.fit}, {r.first.standing}): {r.first.value:.6g}, {r.first.verdict}"
            lines.append(f"    {r.name:<{width}} {r.status:<19} {r.standing:<10} {r.label}: {r.reason}{first}{tag}")
    for p in problems(results, ledger):
        lines.append(f"    FAIL {p}")
    return "\n".join(lines)


def main() -> int:
    utf8_stdout()
    results = evaluate()
    print(report(results))
    return 1 if problems(results) else 0


if __name__ == "__main__":
    sys.exit(main())
