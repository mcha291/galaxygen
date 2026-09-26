"""Supernovae: the core-collapse and type Ia rates the model already implies (checkpoint 4, S30).

BUILD_II Phase 6. Nothing here is new physics: both rates were already inside the model and
this stage publishes them.

**Core collapse is star formation times the IMF.** Every star born above the lowest initial
mass that ends in a core collapse explodes within a few tens of Myr — a single timestep's
worth of the history — so the rate is the star formation rate times the number of such stars
per unit mass formed. That number is one more integral of the Kroupa IMF the ``population``
stage already integrates (``systems.py``'s constants, read here rather than restated, rule A9):
counted, never sampled (rule B8). Every star above the limit, up to the IMF's upper end,
counts as one supernova; stars that collapse to a black hole without exploding are not
removed, because no source for which ones do has been read.

**Type Ia is the chemistry's own convolution, counted.** ``chemistry_dtd`` convolves the star
formation history with the delay-time distribution and multiplies it by the Ia iron yield per
unit mass formed; that iron divided by the iron one event makes is the number of events. The
convolution is one function (``chemistry_dtd.type_ia_history``) that both stages call, so the
rate cannot drift from the iron it implies (rule B13). The iron per event is sourced (Maoz &
Graur 2017); the number of events per unit mass formed is therefore a *result*, and it can be
compared with the one Maoz & Graur measure (the stage's report, not an acceptance row).

**What the rates do not see.** The spheroid is old stars the disc's history never formed (the
halo stage derives it, S17), so its type Ia supernovae are not in this rate; the stellar halo
does not exist yet (Phase 5). Both are recorded where the rate is published.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.chemistry_dtd import type_ia_history
from galaxy.stages.systems import IMF_BREAK, IMF_HIGH_SLOPE, IMF_LOW_SLOPE, IMF_MAX, IMF_MIN

YR_PER_GYR = 1.0e9  # the history's clock is in Gyr, the rates are per year


def _segment(lo: float, hi: float, slope: float) -> float:
    """∫ m^slope dm over [lo, hi], zero when the interval is empty."""
    if hi <= lo:
        return 0.0
    p = slope + 1.0
    return (hi**p - lo**p) / p


def imf_stars_above(m_lo: float) -> float:
    """Stars born above ``m_lo`` per solar mass formed: the Kroupa IMF's number above over its mass.

    The same broken power law ``systems.imf_mean_mass`` integrates — its break, slopes and
    limits imported, not restated — counted analytically, segment by segment.
    """
    k = IMF_BREAK ** (IMF_LOW_SLOPE - IMF_HIGH_SLOPE)  # continuity at the break
    mass = _segment(IMF_MIN, IMF_BREAK, IMF_LOW_SLOPE + 1.0) + k * _segment(IMF_BREAK, IMF_MAX, IMF_HIGH_SLOPE + 1.0)
    number = (
        _segment(max(m_lo, IMF_MIN), IMF_BREAK, IMF_LOW_SLOPE)
        + k * _segment(max(m_lo, IMF_BREAK), IMF_MAX, IMF_HIGH_SLOPE)
    )
    return number / mass


def ring_integral(surface_rate: np.ndarray, R: np.ndarray) -> float:
    """A surface rate integrated over the disc exactly as ``sfr`` integrates Σ_SFR (trapezoid in R)."""
    return float(np.trapezoid(surface_rate * 2.0 * math.pi * R, R))


# --- declarations -------------------------------------------------------------

_RATE_RAMP = Ramp("magma", scale="log")

CORE_COLLAPSE_PER_MASS = FieldDecl(
    name="core_collapse_per_mass_formed", label="Core-collapse supernovae per solar mass formed",
    unit="1/Msun", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "How many stars of each solar mass formed are born heavy enough to end in a core collapse: "
        "the Kroupa IMF's number above 8.5 M☉ over its mass, integrated, not sampled. 8.5 M☉ is "
        "Smartt 2009's lowest initial mass for a type II-P progenitor (+1/−1.5 M☉); Heger et al. "
        "2003 adopt 9, which would lower this by 7%. About one per hundred solar masses — the "
        "number Maoz & Graur 2017 quote. Every star above the limit counts, including those that may "
        "collapse without exploding."
    ),
)
TYPE_IA_PER_MASS = FieldDecl(
    name="type_ia_per_mass_formed", label="Type Ia supernovae per solar mass formed",
    unit="1/Msun", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The Ia iron the chemistry returns per solar mass formed, over the whole delay-time "
        "distribution, divided by 0.7 M☉ of iron per event (Maoz & Graur 2017). A result of the "
        "chemistry's yield, not an input: Maoz & Graur measure 1.3 ± 0.1 per thousand solar masses "
        "formed over a Hubble time, and this reads about twice that — the yield the chemistry "
        "adopts asks for more events than the measured efficiency supplies."
    ),
)
CORE_COLLAPSE_RATE = FieldDecl(
    name="core_collapse_rate", label="Core-collapse supernova rate", unit="1/yr/kpc2",
    kind=Kind.FIELD, axes=("R",), ramp=_RATE_RAMP, meaningful_zero=True,
    about=(
        "Today's core-collapse supernovae per year per kpc²: the present star formation surface "
        "density times the stars per solar mass born above the core-collapse limit. The "
        "progenitors live a few tens of Myr, so the rate is prompt and follows today's star "
        "formation exactly — zero outside the threshold radius."
    ),
)
CORE_COLLAPSE_RATE_TOTAL = FieldDecl(
    name="core_collapse_rate_total", label="Core-collapse supernovae per year",
    unit="1/yr", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The core-collapse surface rate integrated over the disc as the star formation rate is: "
        "exactly the SFR times the stars per solar mass above the limit. Judged against Adams et al. "
        "2013's Galactic rate, whose uncertainty spans more than a factor of ten."
    ),
)
TYPE_IA_RATE = FieldDecl(
    name="type_ia_rate", label="Type Ia supernova rate", unit="1/yr/kpc2",
    kind=Kind.FIELD, axes=("R",), ramp=_RATE_RAMP, meaningful_zero=True,
    about=(
        "Today's type Ia supernovae per year per kpc²: the chemistry's own delay-time convolution of "
        "the disc's star formation history, counted in events rather than iron. Unlike the core "
        "collapses it remembers the past: the inner disc, which formed its stars early, still "
        "explodes where it no longer forms stars. The spheroid's old stars are not in it."
    ),
)
TYPE_IA_RATE_TOTAL = FieldDecl(
    name="type_ia_rate_total", label="Type Ia supernovae per year",
    unit="1/yr", kind=Kind.SCALAR, meaningful_zero=True,
    about=(
        "The disc's type Ia rate integrated over its area. Judged against Adams et al. 2013's "
        "Galactic rate. It counts the disc alone: the spheroid holds about a sixth of the stellar "
        "mass, all of it old, and its supernovae are missing here, so this is low by whatever they "
        "contribute."
    ),
)
CORE_COLLAPSE_RATE_HISTORY = FieldDecl(
    name="core_collapse_rate_history", label="Core-collapse supernova rate history", unit="1/yr/kpc2",
    kind=Kind.FIELD, axes=("R", "t"), ramp=_RATE_RAMP, meaningful_zero=True,
    about=(
        "Core-collapse supernovae per year per kpc² at every radius and time: the star formation "
        "history times the stars per solar mass above the limit, prompt to within a timestep. What "
        "the habitable zone's supernova hazard reads, and what a remnant count will."
    ),
)
TYPE_IA_RATE_HISTORY = FieldDecl(
    name="type_ia_rate_history", label="Type Ia supernova rate history", unit="1/yr/kpc2",
    kind=Kind.FIELD, axes=("R", "t"), ramp=_RATE_RAMP, meaningful_zero=True,
    about=(
        "Type Ia supernovae per year per kpc² at every radius and time: the chemistry's delay-time "
        "convolution of the disc's star formation history, in events. Its last column is today's "
        "rate. The spheroid's old stars are not in it."
    ),
)


def compute_supernovae(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    c = ctx.constants
    psi = np.asarray(ctx.fields["sfr_surface_density_history"], dtype=float)
    psi_now = np.asarray(ctx.fields["sfr_surface_density"], dtype=float)

    per_cc = imf_stars_above(float(c["CORE_COLLAPSE_MIN_MASS"]))
    # Every Ia's iron over the iron one event makes: events per unit mass formed, over the whole DTD.
    per_ia = float(c["Y_FE_IA"]) / float(c["IA_IRON_MASS"])
    ia_hist = per_ia * type_ia_history(
        psi, ctx.grid.spec.t_max, ctx.grid.spec.n_t, float(c["DTD_MIN_DELAY"]), float(c["DTD_INDEX"])
    )
    cc_now = per_cc * psi_now
    ia_now = ia_hist[:, -1]
    return {
        "core_collapse_per_mass_formed": per_cc,
        "type_ia_per_mass_formed": per_ia,
        "core_collapse_rate": cc_now,
        "core_collapse_rate_total": ring_integral(cc_now, R),
        "type_ia_rate": ia_now,
        "type_ia_rate_total": ring_integral(ia_now, R),
        "core_collapse_rate_history": per_cc * psi,
        "type_ia_rate_history": ia_hist,
    }


SUPERNOVAE = IMPLEMENTATIONS.register(
    Stage(
        id="supernovae",
        slot="supernovae",
        checkpoint=4,
        about=(
            "Core-collapse and type Ia supernova rates: star formation times the IMF above the "
            "core-collapse limit, and the chemistry's own delay-time convolution counted in events. "
            "Two acceptance rows judge today's totals."
        ),
        compute=compute_supernovae,
        reads_constants=("CORE_COLLAPSE_MIN_MASS", "IA_IRON_MASS", "Y_FE_IA", "DTD_MIN_DELAY", "DTD_INDEX"),
        requires=("sfr_surface_density_history", "sfr_surface_density"),
        publishes=(
            CORE_COLLAPSE_PER_MASS, TYPE_IA_PER_MASS, CORE_COLLAPSE_RATE, CORE_COLLAPSE_RATE_TOTAL,
            TYPE_IA_RATE, TYPE_IA_RATE_TOTAL, CORE_COLLAPSE_RATE_HISTORY, TYPE_IA_RATE_HISTORY,
        ),
    )
)
