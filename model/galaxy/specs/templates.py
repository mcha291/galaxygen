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
import math
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from galaxy import templates as _templates
from galaxy.specs import Problem, utf8_stdout

STATUSES = ("pass", "fail", "not-yet-computable")
# The checks are read as the acceptance rows are (S55, D214; invariant I3): on the layer-off run, the physics
# alone. The four field checks are radial and are the same bits with the layer on or off. The colour check reads
# the face-on render, whose frame sums each ring's light round the ring while the dust's depth is the ring's own,
# so a placement that averages to 1 leaves it to rounding: ngc_4414's reads 0.6355279197562069 layer-off against
# 0.6355279197563419 layer-on on the production grid, 1.4e-13 apart (measured at S55; tests/test_layer.py), in the
# mixed slab. S70 (D234, #128(b)): the frame is read through the layered dust since (face_on), ngc_4414's layer-off
# 0.6517106309907312, the Milky Way's 0.5738774 (were 0.6355279 and 0.5729334 in the mixed slab; measured at S70).
JUDGED_LAYER = False
JUDGED_SETTING = "off"


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


# S70 (D234; Audit V F-5-6, #128(b)): the face-on frame read through the dust in its own layer. The quadrature of
# the stars' height, u = z / 2h★ on [−FACE_ON_SPAN, FACE_ON_SPAN] by the trapezoid at a step of at most
# FACE_ON_STEP and a fortieth of the thinnest ring's ratio (the stars' share outside the span is 2e-35).
FACE_ON_SPAN = 40.0
FACE_ON_STEP = 2.0e-3


def mixed_face_on_transmission(tau: np.ndarray) -> np.ndarray:
    """The share of a column's starlight a face-on line of sight keeps when stars and dust are one uniform mixed
    slab of extinction depth τ: (1 − e^−τ)/τ, 1 where there is no dust. The check's geometry from S39 until S70."""
    tau = np.asarray(tau, dtype=float)
    return np.where(tau > 1e-12, -np.expm1(-tau) / np.where(tau > 1e-12, tau, 1.0), 1.0)


def layered_face_on_transmission(tau: np.ndarray, ratio: np.ndarray, cloud_share: Any = None, cloud_ratio: float | None = None) -> np.ndarray:
    """The share of a column's starlight a face-on line of sight keeps when the stars and the dust are two sech²
    layers, the dust's scale height ``ratio`` times the stars' (S70, D234, #128(b)): the geometry the dust stage
    heats in and the render names since S52 (D211). A star at u = z / 2h★ (its share ½ sech² u du) sees the dust
    above it, A(u) = ½[1 − tanh(u / ratio)] of the column, so the frame keeps ∫ ½ sech²(u) exp(−τ A(u)) du
    ``[inferred: derived here, as dust.layered_absorbed_fraction's A(s)]``. At ratio 1 it is the mixed slab's
    (1 − e^−τ)/τ; a thin dust sheet (ratio → 0) keeps ½(1 + e^−τ); a thin star sheet (ratio → ∞) e^(−τ/2).
    ``tau`` (R, F) and ``ratio`` (R, 1) broadcast; a NaN ratio (no dust layer) keeps the mixed slab's. Since S89 (#168)
    the clouds' share of the dust (``cloud_share``, (R, 1)) lies in the clouds' own layer, ``cloud_ratio`` times the
    stars' height: the dust above a star is (1 − f) A(u) + f A_c(u), as the dust stage heats it."""
    tau = np.asarray(tau, dtype=float)
    ratio = np.broadcast_to(np.asarray(ratio, dtype=float), tau.shape)
    out = mixed_face_on_transmission(tau)
    ok = (tau > 1e-12) & np.isfinite(ratio) & (ratio > 0.0)
    if not ok.any():
        return out
    clouds = cloud_share is not None and cloud_ratio is not None and np.isfinite(cloud_ratio) and cloud_ratio > 0.0
    least = float(ratio[ok].min()) if not clouds else min(float(ratio[ok].min()), float(cloud_ratio))
    step = min(FACE_ON_STEP, least / 40.0)
    u = np.linspace(-FACE_ON_SPAN, FACE_ON_SPAN, int(math.ceil(2.0 * FACE_ON_SPAN / step)) + 1)
    stars = 0.5 / np.cosh(u) ** 2
    t, r = tau[ok][:, None], ratio[ok][:, None]
    above = 0.5 * (1.0 - np.tanh(u[None, :] / r))
    if clouds:
        f = np.broadcast_to(np.clip(np.nan_to_num(np.asarray(cloud_share, dtype=float), nan=0.0), 0.0, 1.0), tau.shape)[ok][:, None]
        above = (1.0 - f) * above + f * 0.5 * (1.0 - np.tanh(u[None, :] / float(cloud_ratio)))
    out[ok] = np.trapezoid(stars[None, :] * np.exp(-t * above), u, axis=-1)
    return out


def face_on_ratio(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> np.ndarray | None:
    """(R,) the dust's scale height over the stars' on each of the frame's rings, from the layers the render's header
    names (S52, D211), or None where it names no dust layer of its own (the dust then in the stars' layer)."""
    layers = header.get("layers") or {}
    stars, dust = layers.get("stars"), layers.get("dust")
    if not isinstance(stars, (int, float)) or not isinstance(dust, str) or dust not in arrays:
        return None
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(arrays[dust], dtype=float) / float(stars)


def face_on_clouds(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> tuple[np.ndarray | None, float | None]:
    """(R,) the clouds' share of each ring's dust and the clouds' layer's height over the stars', from the header's
    ``layers.dust_clouds`` (S89, #168), or (None, None) where it names none (every grain in the dust's layer)."""
    layers = header.get("layers") or {}
    clouds, stars = layers.get("dust_clouds"), layers.get("stars")
    if not isinstance(clouds, Mapping) or not isinstance(stars, (int, float)) or clouds.get("share") not in arrays:
        return None, None
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(arrays[clouds["share"]], dtype=float), float(clouds["height"]) / float(stars)


def face_on(header: Mapping[str, Any], arrays: Mapping[str, Any], layered: bool = True) -> dict[str, Any]:
    """The frame's stars with the dust composed face-on (S39): each column's light keeps the share a face-on line of
    sight lets through its dust, τ = −ln T the column's depth in each filter - since S70 (D234, #128(b)) with the
    stars and the dust in their own layers at each ring's ratio of heights (:func:`layered_face_on_transmission`),
    the geometry the dust stage has used since S52; until S70 one mixed slab, (1 − T)/τ (``layered=False``, kept
    for the record). The scattered light joins it at the face-on phase factor; the thermal emission is added
    undimmed (optically thin)."""
    tau = -np.log(arrays["dust_extinction"])
    ratio = face_on_ratio(header, arrays) if layered else None
    share, cloud_ratio = face_on_clouds(header, arrays) if ratio is not None else (None, None)
    own = (mixed_face_on_transmission(tau) if ratio is None
           else layered_face_on_transmission(tau, ratio[:, None], None if share is None else share[:, None], cloud_ratio))[:, None, :]
    phase = header["components"]["dust_scattered"]["phase"]["factor"][-1]
    lit = (arrays["stars"] + phase * arrays["dust_scattered"]) * own + arrays["dust_thermal"][:, None, :]
    return {**arrays, "stars": lit}


FACE_ON_BANDS = ("B", "V")
FACE_ON_NEEDS = ("stars", "dust_extinction", "dust_scattered", "dust_thermal")


def face_on_colour(header: Mapping[str, Any], arrays: Mapping[str, Any]) -> float:
    """B − V of a render's frame through its dust, the render having been asked for the table's B and V."""
    dimmed = frame_total(header, face_on(header, arrays))
    return float(band_magnitude(dimmed[0], FACE_ON_BANDS[0]) - band_magnitude(dimmed[1], FACE_ON_BANDS[1]))


# --- the per-radius checks (S99, #136) -----------------------------------------------------


@dataclass(frozen=True, slots=True)
class RadialCheck:
    """A check read per radius off one published radial field (S99, #136): the field read at every grid ring inside a
    band of radii and at the band's two edges, the largest of those reads judged against the window - an upper limit
    read as a window from 0. Judged, reported and recorded as a miss exactly as a template's own checks are
    (:func:`judge`, :data:`CHECK_MISSES`); it lives here, beside the ledger, not in the template's data. The band is
    given in arcseconds, turned into kpc by the template's own distance (``instrument.distance_mpc``), or as the name
    of one of the template's pins whose value is a band of radii in kpc."""

    name: str
    label: str
    unit: str
    window: tuple[float, float]
    quantity: str
    mismatch: str
    source: str
    field: str
    arcsec: tuple[float, float] | None = None
    pin: str | None = None
    standing: str = "disclosed"
    standing_about: str = ""
    first_reading: Any = None

    def __post_init__(self) -> None:
        if (self.arcsec is None) == (self.pin is None):
            raise ValueError(f"check {self.name}: a band is given in arcseconds or by a pin, one of the two")
        if not self.window[0] < self.window[1] or not self.source.strip() or not self.standing_about.strip():
            raise ValueError(f"check {self.name}: a window lo < hi, a source and the sentence that says it is disclosed")

    def holds(self, model: float) -> bool:
        return self.window[0] <= model <= self.window[1]

    def band_kpc(self, template: _templates.Template) -> tuple[float, float]:
        """The band in kpc: arcseconds at the template's own distance, or the pin's (first) band."""
        if self.arcsec is not None:
            kpc_per_arcsec = float(template.instrument.distance_mpc) * 1.0e3 * math.pi / (180.0 * 3600.0)
            return self.arcsec[0] * kpc_per_arcsec, self.arcsec[1] * kpc_per_arcsec
        value = next(p.value for p in template.pins if p.name == self.pin)
        return float(value[0][0]), float(value[0][1])

    def measure(self, template: _templates.Template, field: Any, radius: Any) -> float:
        """The largest read of the field over the band: at its two edges (linear between rings) and every ring inside."""
        lo, hi = self.band_kpc(template)
        radius, field = np.asarray(radius, dtype=float), np.asarray(field, dtype=float)
        inside = (radius > lo) & (radius < hi)
        return float(max(np.interp(lo, radius, field), np.interp(hi, radius, field), *field[inside]))


# Vallejo, Braine & Baudry 2002 (V02) read at S96 (docs/READING_DUST.md Part S96, S96.2): their Table 8's extinction
# at 55-70 arcsec, A_B 0.76 and A_V 0.58, and "roughly 1.6 mag in B, 1.3 in V" in the molecular ring - "upper limits"
# - so E(B - V) = A_B - A_V at most 0.18 and about 0.3 [inferred]: half the HI column in front of the light through a
# grain model, not a measured colour excess, and not said to be face-on. The catalogues (RC3, HyperLeda) hold no
# face-on attenuation to set beside the model's: they correct to face-on by a formula in the axis ratio that is zero
# face-on (READING_NGC_4414.md W-J), so this per-radius read is the closest a source comes (#136's closer, rewritten
# at S96, F-96B-2). The numbers were read with the model's value at those radii unknown; the model's was first read at
# S99 (lane M) and is recorded below, nothing tuned.
_V02 = (
    "[verified: Vallejo, Braine & Baudry 2002, A&A, arXiv:astro-ph/0202391, sect. 4.3 and Table 8, read at S96 "
    "(docs/READING_DUST.md Part S96): 55'' < r < 70'' A_B 0.76, A_V 0.58; the molecular ring 'roughly 1.6 mag in B, "
    "1.3 in V'; 'These values should be viewed as upper limits'] [inferred: E(B - V) = A_B - A_V]"
)
_V02_DISCLOSED = (
    "Its window was read before the model's value at those radii, but it is judged on the template's second fit, "
    "decided after four of its five own checks had been read on the first."
)
_V02_MISMATCH = (
    "V02's is half the HI column in front of the light through a grain model, along the line of sight or face-on "
    "(not said), from atomic gas only; the model's is the whole disc's dust face-on. The catalogues hold no face-on "
    "attenuation (RC3 and HyperLeda correct to face-on by a formula zero face-on)"
)
RADIAL_CHECKS: Mapping[str, tuple[RadialCheck, ...]] = {
    "ngc_4414": (
        RadialCheck(
            name="colour_excess_55_70_arcsec",
            label="E(B − V) face-on at 55–70″, at most",
            unit="mag",
            window=(0.0, 0.18),
            quantity="the largest dust_colour_excess_b_v over 55-70 arcsec at the template's own distance",
            mismatch=_V02_MISMATCH,
            source=_V02,
            field="dust_colour_excess_b_v",
            arcsec=(55.0, 70.0),
            standing_about=_V02_DISCLOSED,
        ),
        RadialCheck(
            name="colour_excess_molecular_ring",
            label="E(B − V) face-on in the molecular ring, about, at most",
            unit="mag",
            window=(0.0, 0.3),
            quantity="the largest dust_colour_excess_b_v over the template's pinned molecular ring",
            mismatch=_V02_MISMATCH,
            source=_V02,
            field="dust_colour_excess_b_v",
            pin="molecular_ring",
            standing_about=_V02_DISCLOSED,
        ),
    ),
}


def stated(name: str) -> tuple[str, ...]:
    """Every check judged for template ``name``: its own, then the per-radius ones held here."""
    return (*(c.name for c in _templates.get(name).checks), *(c.name for c in RADIAL_CHECKS.get(name, ())))


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
                "0.646 against [0.72, 0.82]: the face-on frame through the dust is bluer than the catalogues' "
                "face-on colour, as the default galaxy's is (0.57). S70 (D234, #128(b)): was 0.636 - the frame read "
                "through the mixed slab the dust stage left at S52; through the stars' and the dust's own layers it "
                "is 0.016 redder and 0.21 mag brighter in V (measured, the mechanism not separated), still bluer "
                "than the window. 0.652 at S70, 0.6460 after M1 (S88), 0.6458 since S89 (#168: the clouds' share of "
                "the dust in the clouds' layer). S89 took the three dust terms apart: the stars alone 0.6607, through "
                "the extinction 0.6453 - bluer, the dust lying in the inner disc where the light is reddest - the "
                "scattered light +0.0005, the thermal nothing (docs/READING_DUST.md)."
            ),
            prediction=(
                "The window is corrected to face-on by a formula in the axis ratio and still holds the face-on "
                "dust; a model frame with the dust's reddening applied as the catalogues' correction leaves it "
                "would land inside, and one that stays bluer than 0.72 puts the miss in the stars' colour."
            ),
        ),
        # S99 (#136): the per-radius checks (RADIAL_CHECKS), read first at S99 on the production grid, layer off.
        "colour_excess_55_70_arcsec": CheckMiss(
            debt=136,
            since="S99",
            reason=(
                "0.3476 against at most 0.18 (V02's Table 8, an upper limit): the model's face-on E(B - V) over 55-70 "
                "arcsec (4.72-6.01 kpc at 17.7 Mpc) falls from 0.3476 at the inner edge to 0.161 at the outer, "
                "under the limit only past about 5.8 kpc. The catalogues hold no face-on attenuation; V02's is half "
                "the HI column through a grain model, from the atomic gas alone, the model's the whole disc's dust."
            ),
            prediction=(
                "A model whose dust follows the gas V02 reads (the HI) lands under 0.18 here; one whose excess here "
                "stays over 0.18 with its dust at the HI's column puts the miss in the grain model's E(B - V) per "
                "column."
            ),
        ),
        "colour_excess_molecular_ring": CheckMiss(
            debt=136,
            since="S99",
            reason=(
                "31.21 against about 0.3 at most (V02's 'roughly 1.6 mag in B, 1.3 in V', an upper limit): the "
                "model's face-on E(B - V) in the pinned ring (0.43-4.29 kpc) rises inward from 0.461 at its outer edge "
                "to 31.21 at its inner, a hundred times the limit there and over it at every radius of the ring. "
                "V02's screen is half the atomic gas and leaves out the molecular (their words); the model's is the "
                "whole disc's dust. The catalogues hold no face-on attenuation. The integrated face-on frame is "
                "bluer through this dust than without it (colour_b_v_face_on, S89's split)."
            ),
            prediction=(
                "V02's ring value leaves out the molecular gas (their words); a sourced extinction through the ring's "
                "H2 column that also reads several magnitudes kills this as a model miss and makes it the source's "
                "bound; one near 0.3 puts it in the model's dust-to-gas ratio or its molecular column inside 4.3 kpc."
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
    radial = RADIAL_CHECKS.get(template.name, ())
    wanted = (*(c.field for c in template.checks), *(c.field for c in radial))
    fields = tuple(dict.fromkeys(f for f in wanted if f is not None and f in declared))
    out, _ = service.compute(model, _templates.overrides(template), fields, layer=JUDGED_LAYER)
    results: list[Result] = []
    for check in template.checks:
        if check.statistic == "face_on_colour":
            results.append(judge(template, check, *_frame_colour(template, service)))
        elif check.field not in out.fields:
            results.append(judge(template, check, None, f"field {check.field!r} is not published by model {model.name!r}"))
        else:
            value = _templates.measure(check.statistic, out.fields[check.field], out.grid.R, check.inside_kpc)
            results.append(judge(template, check, value))
    # S99 (#136): the per-radius checks, after the template's own, judged the same way.
    for check in radial:
        if check.field not in out.fields:
            results.append(judge(template, check, None, f"field {check.field!r} is not published by model {model.name!r}"))
        else:
            results.append(judge(template, check, check.measure(template, out.fields[check.field], out.grid.R)))
    return results


def _frame_colour(template: _templates.Template, service: Any) -> tuple[float | None, str]:
    from galaxy.stages import spectra

    curves = json.dumps([spectra.band_curve(b).json() for b in FACE_ON_BANDS])
    got = service.handle("/api/render", {
        "template": [template.name], "model": [template.model], "filters": [curves], "layer": [JUDGED_SETTING],
    })
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
        "  Read on the layer-off run, as the acceptance rows are (invariant I3, D214).",
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
