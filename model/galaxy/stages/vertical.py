"""Vertical structure: the thin/thick split the merger made (checkpoint 3).

GALAXY_PLAN.md §3 gives the thick disc to stage 2, but checkpoint 2 runs before
any star exists, so the heating lives there and the population it sorts lives
here (DECISIONS.md D50). This stage is the plan's §3 hypothesis failing in a
useful way rather than a defect.

**The split is the merger.** A star is thick-disc if it was born before the last
major merger and thin-disc otherwise — so the thick disc is a *consequence* of
the merger list rather than a component switched on beside it, and a galaxy with
no major merger has no thick disc at all. That is what makes debt #9's control
run meaningful.

**Scale heights are arithmetic** once sigma_z exists (GALAXY_INPUTS.md §4b puts
h_z at verdict A). For a self-gravitating isothermal sheet the density goes as
sech^2(z / 2 h_z) with

    h_z = sigma_z^2 / (2 pi G Sigma)

and Sigma is the *whole* disc's surface density, because every component feels
the same potential. Note the 2: GALAXY_PLAN.md's brief for this session wrote
`sigma_z^2 / pi G Sigma`, which is the isothermal-sheet result without it and
gives scale heights twice too large.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.sfh import fit_scale_length, surface_to_mass

SCALE_LENGTH_FIT = (1.0, 12.0)  # kpc
POPULATIONS: tuple[str, ...] = ("thin", "thick")


def scale_height(sigma_z: np.ndarray | float, sigma_total: np.ndarray | float, G: float) -> np.ndarray:
    """Isothermal self-gravitating sheet, in kpc; ``sigma_total`` in M☉/pc².

    ``G`` is the registered constant, passed in: until S12 this file carried its own
    copy of the number, so a change to level0's G would have left every scale height
    on the old value (rule A9; AUDIT_RUN2.md D-9).
    """
    return np.asarray(sigma_z) ** 2 / (2.0 * math.pi * G * np.asarray(sigma_total) * PC_PER_KPC**2)


def _decl(name, label, unit, about, **kw):
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.SCALAR,
                     meaningful_zero=True, about=about, **kw)


BIRTH_POPULATION = FieldDecl(
    name="birth_population", label="Population a star born here belongs to", unit="dimensionless",
    kind=Kind.CATEGORY_FIELD, axes=("R", "t"), categories=POPULATIONS,
    ramp=Palette(("#4c9be8", "#e8894c")), meaningful_zero=True,
    about=(
        "The thin/thick criterion itself, over birth radius and birth time: this stage's mask, "
        "published rather than left implicit. It is the merger in the simple model and the [α/Fe] "
        "valley in the advanced one, and it is what the catalogue reads to label a star — until "
        "S19 the catalogue rebuilt the criterion from the same ingredients, which in the advanced "
        "model was a second, differing definition wearing the right name (rule A9). All thin means "
        "the model found no thick disc, which is an answer and not an absence."
    ),
)

THIN_SURFACE = FieldDecl(
    name="thin_disc_surface_density", label="Thin disc Σ(R)", unit="Msun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("inferno", scale="log"), meaningful_zero=True,
    about="The thin population: born after the last major merger (simple model) or α-poor at birth (advanced).",
)
THICK_SURFACE = FieldDecl(
    name="thick_disc_surface_density", label="Thick disc Σ(R)", unit="Msun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("cividis", scale="log"), meaningful_zero=True,
    about="The thick population: born before the last major merger (simple model) or α-enhanced at birth (advanced). Zero if the criterion selects nothing.",
)

THIN_MASS = _decl("thin_disc_stellar_mass", "Thin disc stellar mass", "Msun",
                  "Acceptance row 10. A result of when the merger arrived, not an assumption.")
THICK_MASS = _decl("thick_disc_stellar_mass", "Thick disc stellar mass", "Msun",
                   "Acceptance row 11. Everything formed before the last major merger.")
THIN_LENGTH = _decl("thin_disc_scale_length_fitted", "Thin disc scale length", "kpc",
                    "Fitted to the thin population alone; thin_disc_scale_length is the whole disc.")
THICK_LENGTH = _decl("thick_disc_scale_length", "Thick disc scale length", "kpc",
                     "Acceptance row 5. Shorter than the thin disc's because the disc was smaller then.")
THIN_HEIGHT = _decl("thin_disc_scale_height", "Thin disc scale height", "pc",
                    "Acceptance row 6, at R₀. Arithmetic once σ_z exists (verdict A).")
THICK_HEIGHT = _decl("thick_disc_scale_height", "Thick disc scale height", "pc",
                     "Acceptance row 7, at R₀. The merger's kick, squared, divided by the same Σ.")
SURFACE_RATIO = _decl("thick_thin_surface_density_ratio", "Thick/thin surface density ratio",
                      "dimensionless",
                      "Acceptance row 9 and this session's gate, at R₀. Set by when the merger "
                      "arrived: earlier means a smaller thick disc.")
LOCAL_RATIO = _decl("thick_thin_local_density_ratio", "Thick/thin local density ratio",
                    "dimensionless",
                    "Acceptance row 8: the surface-density ratio divided by the scale-height "
                    "ratio, so rows 8 and 9 are not independent and must not be tuned separately.")
THIN_DISPERSION = _decl("thin_disc_dispersion", "Thin disc σ_z at R₀", "km/s",
                        "Mass-weighted over the thin population; sets its scale height.")
THICK_DISPERSION = _decl("thick_disc_dispersion", "Thick disc σ_z at R₀", "km/s",
                         "Mass-weighted over the thick population. The merger kick dominates it.")


def split(ctx: Context, thick_mask: np.ndarray) -> Mapping[str, Any]:
    """The populations and their scale heights, given an ``(R, t)`` mask of thick-disc star formation.

    Shared by both implementations of the slot: the simple model's mask is a
    function of time alone (born before the last major merger, broadcast over
    R), the advanced model's is chemical and varies with radius. Everything
    downstream of the mask is arithmetic and lives here once (rule A9).
    """
    R = ctx.grid.R
    R_sun = float(ctx.constants["R_SUN"])
    G = float(ctx.constants["G"])

    # M☉/pc² locked in per step, at the radii those stars occupy today: the sfh stage has
    # already moved them through the merger's radial spread (S18), so a population sorted
    # here carries the radial heating as well as the vertical one.
    formed = np.asarray(ctx.fields["stars_formed_history"])
    sigma_z = np.asarray(ctx.fields["disc_heating"])          # km/s, by birth time
    thick_mask = np.broadcast_to(thick_mask, formed.shape)

    thick = (formed * thick_mask).sum(axis=1)
    thin = (formed * ~thick_mask).sum(axis=1)

    def dispersion_at_sun(mask: np.ndarray) -> float:
        at_sun = int(np.argmin(np.abs(R - R_sun)))
        weights = formed[at_sun] * mask[at_sun]
        if weights.sum() <= 0.0:
            return 0.0
        # Mass-weighted in quadrature: sigma_z is a dispersion, not a velocity.
        return float(np.sqrt(np.average(sigma_z ** 2, weights=weights)))

    sig_thin, sig_thick = dispersion_at_sun(~thick_mask), dispersion_at_sun(thick_mask)
    total_at_sun = float(np.interp(R_sun, R, thin + thick + ctx.fields["gas_surface_density"]))
    h_thin = float(scale_height(sig_thin, total_at_sun, G)) * PC_PER_KPC
    h_thick = float(scale_height(sig_thick, total_at_sun, G)) * PC_PER_KPC if sig_thick > 0.0 else 0.0

    s_thin = float(np.interp(R_sun, R, thin))
    s_thick = float(np.interp(R_sun, R, thick))
    ratio = s_thick / s_thin if s_thin > 0.0 else 0.0

    return {
        "birth_population": np.broadcast_to(thick_mask, formed.shape).astype(np.int64),
        "thin_disc_surface_density": thin,
        "thick_disc_surface_density": thick,
        "thin_disc_stellar_mass": surface_to_mass(thin, R),
        "thick_disc_stellar_mass": surface_to_mass(thick, R),
        "thin_disc_scale_length_fitted": fit_scale_length(thin, R, *SCALE_LENGTH_FIT),
        "thick_disc_scale_length": fit_scale_length(thick, R, *SCALE_LENGTH_FIT) if s_thick > 0.0 else 0.0,
        "thin_disc_scale_height": h_thin,
        "thick_disc_scale_height": h_thick,
        "thick_thin_surface_density_ratio": ratio,
        "thick_thin_local_density_ratio": ratio * (h_thin / h_thick) if h_thick > 0.0 else 0.0,
        "thin_disc_dispersion": sig_thin,
        "thick_disc_dispersion": sig_thick,
    }


def compute(ctx: Context) -> Mapping[str, Any]:
    """The simple model's split: born before the last major merger."""
    onset = float(ctx.fields["last_major_merger_time"])
    return split(ctx, (ctx.grid.t < onset)[None, :])


VERTICAL = IMPLEMENTATIONS.register(
    Stage(
        id="vertical",
        slot="vertical",
        checkpoint=3,
        about=(
            "Sorts the stellar populations into thin and thick by whether they predate the last "
            "major merger, and turns their velocity dispersions into scale heights. The simple "
            "model's vertical stage; the advanced model reads the split off [α/Fe] instead."
        ),
        compute=compute,
        reads_constants=("R_SUN", "G"),
        requires=(
            "stars_formed_history", "gas_surface_density",
            "disc_heating", "last_major_merger_time",
        ),
        publishes=(
            BIRTH_POPULATION,
            THIN_SURFACE, THICK_SURFACE, THIN_MASS, THICK_MASS, THIN_LENGTH, THICK_LENGTH,
            THIN_HEIGHT, THICK_HEIGHT, SURFACE_RATIO, LOCAL_RATIO,
            THIN_DISPERSION, THICK_DISPERSION,
        ),
    )
)
