"""The gas's own arm pattern (checkpoint 3; S51, D210; since S57 the gas's steady response to the stellar arms, D216).

The stellar pattern (``pattern``) is a sum of cosine modes whose crests the randomness layer places. The gas
is not that field: it answers the modes' potential. From S51 to S56 the answer was stated as a shape - a von
Mises ridge of a measured width, its amplitude set from a measured ratio of means, since S56 laid round each
ring in the order of the stellar modes' sum. Gate G2 of S57 (DECISIONS.md D216) retired the shape for a law:
on every ring the gas takes **the steady response of isothermal gas that turns with the arms**, solved by
``gas_response`` (the instrument, certified in ``tests/test_gas_response.py``), and nothing of the ridge is
put in.

- **The frame** (D216 items 1-2). Every arm mode turns with the gas, Ω_p(R) = Ω(R): the swing-amplified arms
  of the reading (``docs/READING_GAS_SHOCK.md`` Part B) and the only frame in which a ring's several modes are
  steady together. So nothing flows through an arm and nothing shocks in it: there is no sonic point and no
  jump. The derived ``bar`` stage publishes that frame as ``arm_pattern_speed``; nothing here reads it, and
  the flow handed to the solver is 0 by construction.
- **The law** (item 5), on each grid ring, with χ = φ − ln R · cot p the pattern coordinate and s(χ) the gas's
  surface density over its ring mean:

      ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(m χ − θ_m)

  ε = a/(κ R sin p), a the cold gas's velocity dispersion taken as its isothermal sound speed (the one the
  star-formation threshold reads: there is no second); f_m = m A_m/(X sin p), X = κ²R/(2πGΣ) the arm-number
  law's own variable with checkpoint 1's total disc Σ (``pattern.local_swing_x``); A_m the mode's cosine
  amplitude **before the bar's taper** - the published amplitude over (1 − taper), which is the arm amplitude
  times :meth:`GasPattern.unit_amplitudes`; θ_m the layer's phases. **The forcing's amplitude carries the
  saturation** (gate G3 item 3): A_m is the stellar field's actual cosine amplitude on the ring with the
  taper taken back out - the arm amplitude times the root of the mode's gain times the pattern stage's
  saturation factor, which is under 1 where the modes' linear sum would reach the mean - "because the gas
  answers the stars that exist". Uniform potential vorticity closes the equation (item 3). It is the
  Euler-Lagrange equation of a strictly convex functional, so on every ring the solution exists, is unique,
  is positive and has mean 1. A ring that carries no mode has s = 1.
- **Nothing is put in and nothing is mended.** No amplitude, width, mask or contrast enters; no thickness
  factor, no constant added, no f scaled; nothing clipped, floored, capped or divided by a sampled mean. A
  ring the solver cannot converge raises (``gas_response.ConvergenceError``) and is not caught: there is no
  fallback and no linear substitute (item 7). The solver holds a cell's residual under 1e-10 or under the
  cell's rounding floor where that is larger (gate G3 item 2), so a tightly wound galaxy's rings - a drawn
  pitch under about 2.7 degrees, ε of order 1, a total forcing of 60-80 - converge as every other ring does.
  That regime is published as the law gives it, nothing clipped: s from 1e-44 to 14, the arm-to-arm spacing
  then comparable to the disc's thickness and the razor-thin forcing overstated by about that factor (a
  finding under the razor-thin debt, below).
- **The bar** (item 8). g = w_arm s + w_bar (1 + B cos 2(φ − φ_bar)), w_bar the bar's taper, w_arm = 1 − w_bar
  (their sum is checked), B the stellar ``bar_contrast``; the taper, the winding phase and the bar's angle are
  the stellar pattern's own (``pattern.bar_terms``). The taper acts once, here, on the response to the
  untapered forcing. So g ≥ w_bar (1 − B) > 0 and the ring's mean is 1. The bar inside the forcing turns at
  its own speed and is Phase P3's.
- **At a point** (item 9). The equation is solved once per grid ring on ``gas_response.CELLS`` cells. A point
  at (R, φ) reads the two neighbouring grid rings' profiles **at its own χ** (the winding at the point's own
  radius), linear in χ between the cells' centres and linear in R between the two rings, held at the end
  rings beyond the grid; the taper and the bar's term are taken at the point's own radius. Both blends are
  convex blends of positive profiles of mean 1, so the gas is positive and its mean round the ring is 1 at
  every radius. :meth:`GasPattern.sector_means` is the exact mean of that same interpolant, so sectors that
  tile a ring average to 1 to rounding.
- **The published field is the law's mean over each grid cell** (gate G3 item 4, which rewords items 9 and
  11 i): on each grid ring, the interpolant integrated exactly over each of the grid's φ cells
  (:meth:`GasPattern.cell_means`, the arithmetic of the sector means; the bar's cosine by its own integral).
  So a ring's cells average to 1 to rounding on every φ grid, with no division - a field of centre samples
  did only on grids whose cell count divides the solver's (7e-14 off at 360 cells, 2e-3 at 36) - and each
  cell holds the gas the law puts in it. ``contrast_at``, ``response_at``, ``azimuths`` and the censuses keep
  the point function: a cell's expected count is its area times its mean, a placed object reads the law at
  its own point, and the two are the same measure.
- **The offset** (D210 ruling 3, now derived; gate G3 item 7): zero for a lone mode, exactly, by the
  equation's symmetry about the mode's crest. With several modes the gas's crest and the crest of the stellar
  modes' sum need not be one cell, because each mode is answered with its own weight (m/(1 + m²ε²) in the
  linear limit, against the stars' 1): on the default galaxy they are within one solver cell (0.25 degrees)
  on every ring over 6-10 kpc and on 161 of the 165 rings that carry a mode (two rings read two cells; on
  two, where six equal crests stand, the tallest is another arm's); on ``ngc_4414`` they are up to five cells
  (1.25 degrees) apart over 6-10 kpc. No offset is put in and none is published.
- **Declared approximations, each a debt** (items 4-5): steadiness (the response relaxes on the ridge's
  sound crossing, about as long as an arm lives); the razor-thin WKB potential, which overstates the high
  arm numbers; the stellar mode's fractional amplitude applied to the total disc.

**What became of the ridge's numbers** (item 11 iv; gate G3 items 6-7). The measured ratio of means, the mask
it is measured in and the measured width build nothing. They survive as the target and the definition of a
*disclosed check*, made by the measurement functions at the foot of this module and pinned in the tests,
layer on: the ratio of the means of s inside the source's arm mask against outside it (:func:`mask_share`,
:func:`ratio_of_means`), and the full width at half maximum of a ring's tallest crest (:func:`crest_width`)
over the period of the mode the gas answers most strongly, the one of largest forcing m·A_m. No stage
computes with them, and the mask's width and the measured width are no constants of the model: they left its
registry at gate G3 ("a stage may not declare reads it does not make") and live in ``tests/`` with their
sources; the measuring functions take the mask's width as an argument. The measured ratio's class means stay
constants: the ``bar`` stage derives the check's target from them.

**One solve per pattern.** A pattern object solves its rings the first time a profile is asked for and keeps
them. Several stages of one run build the same pattern (the stage here, the cloud census, its texture, the
cluster census), so the last few solutions are also kept by content - a digest of the forcing amplitudes,
the phases and ε - and handed back as they were made (:func:`respond`). The solver gives a ring the same bits
alone as in any batch, so a pattern's profiles are the same bits with the cache or without it (tested).

**Why its own stage, and why seeded.** It reads no seed of its own and draws nothing; it reads the
pattern's amplitudes, pitch and bar, which carry seeded draws, and the layer's phases, so ``graph`` labels
its one field seeded through those requirements (D55: a stage that reads a seeded or a synthetic field
publishes seeded fields).
"""

from __future__ import annotations

import hashlib
import math
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.layer import compose as _compose
from galaxy.stages import gas_response as _response
from galaxy.stages.pattern import (
    AMPLITUDE_FIELDS,
    ARM_MODES,
    PATTERN_READS,
    PHASE_FIELDS,
    bar_terms,
    effective_arm_number,
    invert_azimuths,
    local_swing_x,
)

CELLS = _response.CELLS  # the solver's fixed cells round a ring; a profile is held on their centres

# What the gas's pattern is built from, and so what every stage that places by it requires (S57, D216): the
# stellar pattern's own reads - the modes and their phases, never ``arm_multiplicity`` - the arm amplitude
# the taper is taken back out with, and checkpoint 1's disc: its epicyclic frequency and total surface density.
GAS_PATTERN_READS: tuple[str, ...] = ("arm_contrast", *PATTERN_READS, "epicyclic_frequency", "disc_surface_density")
GAS_PATTERN_CONSTANTS: tuple[str, ...] = ("G", "GAS_DISPERSION")

SOLUTIONS_KEPT = 4  # how many patterns' solved rings the content-keyed cache holds (about 4.6 MB each)

_M = np.asarray(ARM_MODES, dtype=float)
_SOLUTIONS: dict[bytes, tuple[np.ndarray, _response.Diagnostics]] = {}
_SOLUTIONS_LOCK = threading.Lock()


def respond(forcing: np.ndarray, phases, eps: np.ndarray, *, cache: bool = True) -> tuple[np.ndarray, _response.Diagnostics]:
    """The steady response of each ring given: ``(s, diagnostics)``, s shaped (rings, CELLS) on the cells' centres.

    ``forcing`` f_m, shaped (rings, modes), dimensionless; ``phases`` θ_m in radians, one per mode; ``eps`` ε,
    shaped (rings,), dimensionless. The flow through the pattern is 0 (D216 item 1). Raises what the solver
    raises - ``gas_response.ConvergenceError`` for a ring it could not converge - and catches nothing.

    ``cache``: the last ``SOLUTIONS_KEPT`` solutions are kept under a digest of the three arguments' bytes and
    returned as they were made (read-only arrays); ``cache=False`` solves afresh and keeps nothing. The bits
    are the same either way.
    """
    f = np.ascontiguousarray(forcing, dtype=float)
    theta = np.ascontiguousarray(phases, dtype=float)
    e = np.ascontiguousarray(eps, dtype=float)
    key = b""
    if cache:
        digest = hashlib.sha256()
        for part in (np.asarray(f.shape, dtype=np.int64), f, theta, e):
            digest.update(part.tobytes())
        key = digest.digest()
        with _SOLUTIONS_LOCK:
            held = _SOLUTIONS.get(key)
        if held is not None:
            return held
    s, diagnostics = _response.solve(_response.forcing(ARM_MODES, f, theta, CELLS), e, 0.0)
    s.setflags(write=False)
    for name in ("steps", "halvings", "deepest", "residual", "residual_sum", "floor"):
        getattr(diagnostics, name).setflags(write=False)
    if cache:
        with _SOLUTIONS_LOCK:
            _SOLUTIONS[key] = (s, diagnostics)
            while len(_SOLUTIONS) > SOLUTIONS_KEPT:  # the oldest out: a dict keeps the order things went in
                del _SOLUTIONS[next(iter(_SOLUTIONS))]
    return s, diagnostics


def forget_solutions() -> None:
    """Empty the content-keyed cache (the tests compare a pattern's bits with it and without)."""
    with _SOLUTIONS_LOCK:
        _SOLUTIONS.clear()


def blend_weights(taper: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(w_arm, w_bar) = (1 − taper, taper): the two weights of the composition (D216 item 8), their sum checked.

    The sum is 1 in the law; in doubles (1 − t) + t is 1 or one unit in the last place under it, and anything
    else - a taper that is not a number, or outside [0, 1] - is refused here and not composed.
    """
    w_bar = np.asarray(taper, dtype=float)
    w_arm = 1.0 - w_bar
    if not np.all((w_bar >= 0.0) & (w_bar <= 1.0) & (np.abs((w_arm + w_bar) - 1.0) <= np.finfo(float).eps)):
        raise ArithmeticError("the arm's and the bar's weights do not sum to 1: the bar's taper is not in [0, 1]")
    return w_arm, w_bar


GAS_DENSITY_CONTRAST = FieldDecl(
    name="gas_density_contrast", label="Gas density contrast Σ_gas(R, φ)/Σ_gas(R)",
    unit="dimensionless", kind=Kind.FIELD, axes=("R", "phi"),
    ramp=Ramp("magma", lo=0.0, hi=4.0), meaningful_zero=True, provenance="seeded",
    # S55 (D214, gate G1 change 3): composed - the gas's response to where the arms are - and 1 everywhere
    # with the randomness layer off.
    composed=True, neutral=1.0,
    about=(
        "Σ_gas(R, φ)/Σ_gas(R): mean 1 round every ring, so every radial gas profile is unchanged. Each "
        "value is the mean over its azimuthal cell on its ring - the gas the cell holds, not a sample at its "
        "centre - so a ring's cells average to 1 to rounding on any grid, with nothing divided; a census "
        "placing an object reads the same law at the object's own point. "
        "The steady response of isothermal gas to the stellar arm modes' potential, in the frame that turns "
        "with the gas - the frame the arms themselves turn in, so no gas flows through an arm and nothing "
        "shocks there. On each ring the logarithm of the gas's surface density is bent by the pressure of "
        "its own velocity dispersion against the pull of the arm modes, each mode pulling in proportion to "
        "its amplitude as the stars carry it - the saturation in it - and its arm number, and in inverse "
        "proportion to the disc's stability parameter and "
        "the sine of the pitch; the equation is solved on a fixed set of cells round the ring, and a point "
        "between two rings reads both at its own winding phase. Nothing sets the contrast or the width: they "
        "come out of the equation. The gas piles on the stellar crests: the offset is zero for a lone mode, "
        "exactly, by the equation's symmetry; with several modes the gas's crest and the crest of the stellar "
        "modes' sum are within a quarter of a degree over the mid disc at the defaults, and a degree or so "
        "apart in other galaxies, because each mode is answered with its own weight; no offset is put in and "
        "none is published. "
        "Where the modes' pull together exceeds the pressure's reach the gas between the arms is nearly "
        "emptied, the crest standing two to three times the ring's mean in the mid disc and fading to "
        "nothing where the disc amplifies no arm. The crest is two and a half to three times as broad as "
        "the one measured gas arm, about half the period of the mode the gas answers most strongly: the "
        "steady, razor-thin response is an approximation and that is its recorded miss. A tightly wound "
        "galaxy - a drawn pitch of a few degrees - is forced far harder, and its inner rings swing from "
        "nearly empty to many times the mean: the law as it stands, nothing clipped, and a finding against "
        "the razor-thin forcing. Inside the bar the response gives way "
        "to the stellar bar's own two-fold term, "
        "blended by the bar's taper, so the field is nowhere below the bar's own trough and nowhere "
        "negative; nothing is clipped. It reads no gas column. A composed field: with the randomness layer "
        "off it is 1 everywhere - the equation and its inputs are unchanged, and nothing says where the "
        "arms are."
    ),
)


@dataclass(frozen=True, slots=True, eq=False)
class GasPattern:
    """Everything the gas contrast needs, read from published fields in one place (rule A9).

    The interface is ``ArmPattern``'s (``flat``, ``contrast``, ``contrast_at``, ``sector_means``,
    ``azimuths``), so a stage that places by the stellar pattern can place by this one instead.

    **Evaluable at a point** (D216 item 9): the response is solved once on each grid ring; a point reads the
    two neighbouring rings' profiles at its own χ, linear in χ between the cells' centres and linear in R
    between the rings (held at the end rings beyond the grid). At a grid radius that is the ring's own
    profile, exactly. ``contrast``, ``contrast_at``, ``response_at`` and ``azimuths`` are that point function;
    ``sector_means`` and ``cell_means`` are its exact means over sectors of a ring, and ``cell_means`` on the
    grid's own φ cells is the field the stage publishes (gate G3 item 4).

    Built through ``galaxy.layer.compose`` (the one reader of the layer's switch) and by tests.
    """

    R: np.ndarray                # the grid radii, kpc: one solved ring each
    unit: np.ndarray             # (modes, R): u_m = A_m / (A (1 − bar taper)), the arm modes at unit amplitude
    phases: tuple[float, ...]    # θ_m, rad, one per mode of ARM_MODES
    arm: float                   # A, the published arm_contrast: A u_m is the mode's amplitude before the taper
    bar: float                   # B, the stellar bar_contrast
    pitch_deg: float
    bar_length: float            # kpc
    epicyclic: np.ndarray        # (R,): κ, km/s/kpc
    surface_density: np.ndarray  # (R,): checkpoint 1's total disc Σ, M☉/pc²
    gravity: float               # G, kpc (km/s)²/M☉
    sound_speed: float           # a, km/s
    flat: bool = field(init=False)
    _solved: dict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("R", "unit", "epicyclic", "surface_density"):
            object.__setattr__(self, name, np.asarray(getattr(self, name), dtype=float))
        object.__setattr__(self, "phases", tuple(float(p) for p in self.phases))
        n = self.R.size
        if self.unit.shape != (len(ARM_MODES), n) or len(self.phases) != len(ARM_MODES):
            raise ValueError(
                f"a gas pattern holds {len(ARM_MODES)} modes on its {n} radii; got unit amplitudes "
                f"{self.unit.shape} and {len(self.phases)} phases"
            )
        if self.epicyclic.shape != (n,) or self.surface_density.shape != (n,):
            raise ValueError(
                f"a gas pattern holds the disc's epicyclic frequency and surface density on its {n} radii; got "
                f"{self.epicyclic.shape} and {self.surface_density.shape}"
            )
        # No perturbation to apply: a pattern the grid could not resolve or the layer did not realise (a NaN
        # among its own numbers), or no arm mode anywhere and no bar. (The disc's κ and Σ are not asked here:
        # a ring that carries a mode on a disc that is not a number is the solver's to refuse, loudly.)
        scalars = (self.arm, self.bar, self.pitch_deg, self.bar_length, *self.phases)
        finite = all(math.isfinite(v) for v in scalars) and bool(np.all(np.isfinite(self.unit)))
        no_arms = self.arm == 0.0 or not self.unit.any()
        object.__setattr__(self, "flat", not finite or (no_arms and self.bar == 0.0))
        object.__setattr__(self, "_solved", {})

    @staticmethod
    def unit_amplitudes(R: np.ndarray, amplitudes: np.ndarray, arm: float, pitch_deg: float, bar_length: float) -> np.ndarray:
        """u_m(R) = A_m(R) / (A (1 − bar taper)) at the grid radii: the published amplitudes with the arm
        amplitude and the bar's taper taken back out (the saturation stays in), so A u_m is the mode's cosine
        amplitude before the taper. Zero where the denominator is (no arm amplitude at all, or a radius where
        the taper is whole)."""
        taper, _, _ = bar_terms(R, pitch_deg, bar_length)
        scale = arm * (1.0 - taper)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(scale > 0.0, np.asarray(amplitudes, dtype=float) / np.where(scale > 0.0, scale, 1.0), 0.0)

    @classmethod
    def from_fields(cls, fields: Mapping[str, Any], R: np.ndarray, constants: Mapping[str, Any]) -> "GasPattern | None":
        """The gas pattern of a run's published fields on the run's grid radii ``R``, or None where the fields
        hold no pattern. It reads the modes; ``arm_multiplicity`` is not among what it reads (D215)."""
        if any(n not in fields for n in GAS_PATTERN_READS) or any(k not in constants for k in GAS_PATTERN_CONSTANTS):
            return None
        pitch, bar_length, arm = float(fields["pitch_angle"]), float(fields["bar_half_length"]), float(fields["arm_contrast"])
        amplitudes = np.stack([np.asarray(fields[n], dtype=float) for n in AMPLITUDE_FIELDS])
        return cls(
            R, cls.unit_amplitudes(R, amplitudes, arm, pitch, bar_length),
            tuple(float(fields[n]) for n in PHASE_FIELDS),
            arm, float(fields["bar_contrast"]), pitch, bar_length,
            fields["epicyclic_frequency"], fields["disc_surface_density"],
            float(constants["G"]), float(constants["GAS_DISPERSION"]),
        )

    # --- the law's inputs on the grid rings ------------------------------------------------------------

    @property
    def sin_pitch(self) -> float:
        """sin p, of the pitch the winding is made with (``pattern.bar_terms`` keeps it inside 1-89 degrees)."""
        return math.sin(math.radians(min(max(self.pitch_deg, 1.0), 89.0)))

    def swing_x(self) -> np.ndarray:
        """X(R) = κ²R/(2πGΣ) on the grid rings: the arm-number law's own variable, by its own function."""
        return local_swing_x(self.R, self.epicyclic, self.surface_density, self.gravity)

    def forcing_amplitudes(self) -> np.ndarray:
        """f_m = m A u_m/(X sin p) on the grid rings, shaped (R, modes): each mode's forcing, the amplitude
        the one before the bar's taper. No factor is added and nothing is scaled (D216 item 5)."""
        return _response.forcing_amplitudes(ARM_MODES, (self.arm * self.unit).T, self.swing_x(), self.sin_pitch)

    def epsilon(self) -> np.ndarray:
        """ε = a/(κ R sin p) on the grid rings, shaped (R,)."""
        return _response.epsilon(self.sound_speed, self.epicyclic, self.R, self.sin_pitch)

    # --- the solved rings ------------------------------------------------------------------------------

    def _rings(self) -> dict:
        """The grid rings' solved profiles, made the first time they are asked for: ``profiles`` (R, CELLS),
        ``carries`` (R,) and the solver's ``diagnostics`` for the rings that carry a mode (None where none does)."""
        solved = self._solved
        if not solved:
            f, eps = self.forcing_amplitudes(), self.epsilon()
            carries = (f != 0.0).any(axis=1)
            profiles = np.ones((self.R.size, CELLS))  # a ring with no mode: s = 1
            diagnostics = None
            if carries.any():
                s, diagnostics = respond(f[carries], self.phases, eps[carries])
                profiles[carries] = s
            profiles.setflags(write=False)
            solved.update(profiles=profiles, carries=carries, diagnostics=diagnostics)
        return solved

    @property
    def profiles(self) -> np.ndarray:
        """s on the cells' centres of every grid ring, shaped (R, CELLS); read-only. 1 on a ring with no mode."""
        return self._rings()["profiles"]

    @property
    def carries(self) -> np.ndarray:
        """(R,) bool: the grid rings that carry a mode - the ones the solver solved."""
        return self._rings()["carries"]

    @property
    def diagnostics(self) -> "_response.Diagnostics | None":
        """What Newton did on the rings that carry a mode, in their order (None where no ring does)."""
        return self._rings()["diagnostics"]

    # --- at a point ------------------------------------------------------------------------------------

    def _between(self, R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(lower ring, upper ring, share of the upper) for each radius: linear in R between two grid rings,
        the end ring alone beyond the grid. At a grid radius the share is 0 or 1 and the ring is its own."""
        grid = self.R
        if grid.size < 2:
            zero = np.zeros(np.shape(R), dtype=np.int64)
            return zero, zero, np.zeros(np.shape(R))
        lower = np.minimum(np.maximum(np.searchsorted(grid, R, side="right") - 1, 0), grid.size - 2)
        share = (R - grid[lower]) / (grid[lower + 1] - grid[lower])
        return lower, lower + 1, np.minimum(np.maximum(share, 0.0), 1.0)  # held at the end rings (item 9)

    def response_at(self, R: np.ndarray, chi: np.ndarray) -> np.ndarray:
        """s at points: ``R`` in kpc and ``chi`` in radians broadcast against each other. Each point reads its
        two neighbouring grid rings at its own χ - ``gas_response.interpolate``'s own arithmetic on the two
        cells χ lies between, the ring picked point by point - and blends them linearly in R."""
        profiles = self.profiles
        R, chi = np.broadcast_arrays(np.asarray(R, dtype=float), np.asarray(chi, dtype=float))
        lower, upper, share = self._between(R)
        below, above, weight, _ = _response.bracket(chi, CELLS)

        def read(ring: np.ndarray) -> np.ndarray:
            first, second = profiles[ring, below], profiles[ring, above]
            rising = second >= first
            return np.where(rising, first, second) + np.where(rising, weight, 1.0 - weight) * np.abs(second - first)

        return (1.0 - share) * read(lower) + share * read(upper)

    def contrast_at(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """The contrast at points: ``R`` and ``phi`` broadcast against each other, elementwise.
        g = w_arm s + w_bar (1 + B cos 2(φ − φ_bar)), the taper and the bar's term at the point's own radius."""
        R = np.asarray(R, dtype=float)
        phi = np.asarray(phi, dtype=float)
        taper, phase, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        w_arm, w_bar = blend_weights(taper)
        return w_arm * self.response_at(R, phi - phase) + w_bar * (1.0 + self.bar * np.cos(2.0 * (phi - bar_angle)))

    def contrast(self, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Σ_gas(R, φ)/Σ_gas(R) at the points of an (R, φ) mesh: the point function at each (R_i, φ_j) - what a
        census inverts for an azimuth. Its mean round a ring is 1 over the ring itself; a mesh's samples
        average to 1 only to their sampling, and nothing is divided. (The field the stage publishes is not
        this: it is :meth:`cell_means`.)"""
        return self.contrast_at(np.asarray(R, dtype=float)[:, None], np.asarray(phi, dtype=float)[None, :])

    def cell_means(self, R: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """The contrast's mean over each azimuthal cell between ``edges`` (radians, ascending) at each radius of
        ``R``, shaped (R, cells): what the stage publishes on the grid (gate G3 item 4). The exact mean of the
        point function over the cell - the two neighbouring rings' interpolants integrated piece by piece
        (``gas_response.sector_mean``) and blended as a point blends them, the bar's cosine by its own
        integral - so cells that tile the ring average to 1 to rounding on any grid, with no division, and a
        cell's value is never under w_bar (1 − B). At one radius it is :meth:`sector_means`' arithmetic."""
        solved = self._rings()
        profiles, carries = solved["profiles"], solved["carries"]
        R = np.asarray(R, dtype=float)
        edges = np.asarray(edges, dtype=float)
        lo, hi = edges[:-1], edges[1:]
        taper, phase, bar_angle = bar_terms(R, self.pitch_deg, self.bar_length)
        w_arm, w_bar = blend_weights(taper)
        lower, upper, share = self._between(R)

        def ring_means(ring: np.ndarray) -> np.ndarray:
            out = np.ones((R.size, lo.size))  # a ring with no mode is 1 on every cell: so is every sector of it
            on = carries[ring]
            if on.any():
                out[on] = _response.sector_mean(profiles[ring[on]], lo[None, :] - phase[on, None], hi[None, :] - phase[on, None])
            return out

        arms = (1.0 - share)[:, None] * ring_means(lower) + share[:, None] * ring_means(upper)
        bar = (np.sin(2.0 * (hi - bar_angle)) - np.sin(2.0 * (lo - bar_angle))) / (2.0 * (hi - lo))
        return w_arm[:, None] * arms + w_bar[:, None] * (1.0 + self.bar * bar[None, :])

    def sector_means(self, R: float, edges: np.ndarray) -> np.ndarray:
        """The contrast averaged over each sector between ``edges`` (radians, ascending) at one radius: the exact
        mean of the point function - the two neighbouring rings' interpolants integrated piece by piece
        (``gas_response.sector_mean``) and blended as a point blends them, the bar's term by its own integral.
        Sectors that tile the ring average to 1 to rounding."""
        solved = self._rings()
        profiles, carries = solved["profiles"], solved["carries"]
        radius = np.array([float(R)])
        taper, phase, bar_angle = bar_terms(radius, self.pitch_deg, self.bar_length)
        w_arm, w_bar = blend_weights(taper)
        edges = np.asarray(edges, dtype=float)
        lo, hi = edges[:-1], edges[1:]
        lower, upper, share = self._between(radius)

        def ring_mean(ring: int) -> np.ndarray | float:
            if not carries[ring]:
                return 1.0  # a ring with no mode is 1 on every cell: so is every sector of it
            return _response.sector_mean(profiles[ring], lo - phase[0], hi - phase[0])

        arms = (1.0 - share[0]) * ring_mean(int(lower[0])) + share[0] * ring_mean(int(upper[0]))
        bar = (np.sin(2.0 * (hi - bar_angle)) - np.sin(2.0 * (lo - bar_angle))) / (2.0 * (hi - lo))
        return w_arm[0] * arms + w_bar[0] * (1.0 + self.bar * bar)

    def azimuths(self, u: np.ndarray, radius: np.ndarray, lo: float, hi: float, steps: int = 24) -> np.ndarray:
        """Azimuths within [lo, hi] drawn from the contrast at each star's own radius — by inverse CDF (rule B8)."""
        grid = np.linspace(lo, hi, steps + 1)
        return invert_azimuths(u, grid, self.contrast(radius, grid))

    # --- the disclosed check's measurements (D216 item 11 iv): they build nothing --------------------

    def stellar_sum(self) -> np.ndarray:
        """ψ = Σ_m u_m cos(m χ_k − θ_m) on the cells' centres of every grid ring, shaped (R, CELLS): the
        stellar arm modes' sum at unit amplitude, whose highest part of a ring the source's mask is laid on."""
        chi = _response.cell_centres(CELLS)
        psi = np.zeros((self.R.size, CELLS))
        for k, m in enumerate(ARM_MODES):
            psi += self.unit[k][:, None] * np.cos(float(m) * chi[None, :] - self.phases[k])
        return psi

    def arm_ratio(self, mask_width: float) -> np.ndarray:
        """The ratio of means on every grid ring, shaped (R,): the mean of s over the source's arm mask - the
        share :func:`mask_share` of the ring, taken where the stellar modes' sum is highest - over its mean on
        the rest of the ring. ``mask_width`` in kpc, the mask's full width perpendicular to an arm. NaN on a
        ring that carries no mode. A measurement of the solved rings: nothing is built from it."""
        profiles, carries = self.profiles, self.carries
        share = mask_share(effective_arm_number(self.unit), self.R, self.sin_pitch, mask_width)
        psi = self.stellar_sum()
        out = np.full(self.R.size, np.nan)
        for i in np.flatnonzero(carries & np.isfinite(share)):
            out[i] = ratio_of_means(profiles[i], psi[i], float(share[i]))
        return out

    def strongest_forcing(self) -> np.ndarray:
        """The arm number of the mode of largest forcing m·A_m on every grid ring, shaped (R,): the mode the gas
        answers most strongly (f_m = m A_m/(X sin p), and X sin p is the ring's own). Gate G3 item 6."""
        return _M[np.argmax(_M[:, None] * self.unit, axis=0)]

    def arm_width(self, arm_number: np.ndarray | None = None) -> np.ndarray:
        """The full width at half maximum of every grid ring's tallest crest of s (:func:`crest_width`) as a
        fraction of the period 2π/m, shaped (R,); NaN on a ring that carries no mode. A measurement only.

        m is the mode of largest forcing m·A_m (:meth:`strongest_forcing`): the check's definition, fixed at gate
        G3 (item 6) - not the largest amplitude, which on most rings is a tie the first build broke towards the
        lower arm number, the kindest reading. ``arm_number`` (R,) reads the same widths against another
        mode's period, for the record the tests keep of the other readings."""
        profiles, carries = self.profiles, self.carries
        m = self.strongest_forcing() if arm_number is None else np.asarray(arm_number, dtype=float)
        out = np.full(self.R.size, np.nan)
        for i in np.flatnonzero(carries):
            out[i] = crest_width(profiles[i]) / (2.0 * math.pi / m[i])
        return out


# --------------------------------------------------------------------------------------------------------------
# The disclosed check's two measurements (D216 item 11 iv; the gate's follow-up). They read a solved ring and
# build nothing: no stage calls them. Their definitions are fixed by the ruling, before the build's numbers.
# --------------------------------------------------------------------------------------------------------------


def mask_share(arm_number, radius, sin_pitch, mask_width) -> np.ndarray:
    """The share of a ring the source's arm mask covers: m W/(2π R sin p), at most a half (S56's definition,
    D215, unchanged): a mask of full width W perpendicular to an arm, for the ring's power-weighted arm number
    m (``pattern.effective_arm_number``). ``radius`` and ``mask_width`` in kpc. NaN where the arm number is."""
    m = np.asarray(arm_number, dtype=float)
    return np.minimum(m * mask_width / (2.0 * math.pi * np.asarray(radius, dtype=float) * sin_pitch), 0.5)


def ratio_of_means(profile: np.ndarray, order_by: np.ndarray, share: float) -> float:
    """The mean of ``profile`` over the ``share`` of a ring's cells on which ``order_by`` is highest, over its
    mean on the rest. Both arrays are on the ring's equal cells; the cell the share cuts is counted by the
    fraction of it inside, and the order is stable (equal values keep the cells' own order)."""
    profile = np.asarray(profile, dtype=float)
    ranked = profile[np.argsort(-np.asarray(order_by, dtype=float), kind="stable")]
    cells = float(share) * ranked.size
    whole = min(int(math.floor(cells)), ranked.size)
    inside = float(ranked[:whole].sum()) + ((cells - whole) * float(ranked[whole]) if whole < ranked.size else 0.0)
    outside = float(ranked.sum()) - inside
    return (inside / cells) / (outside / (ranked.size - cells))


def crest_width(profile: np.ndarray) -> float:
    """The full width at half maximum of a ring's tallest crest, in radians of the pattern coordinate.

    The half level is midway between the ring's trough and its crest. From the tallest cell the profile is
    followed each way to where it first falls to that level, the crossing placed linearly between the two
    cells it lies between. NaN for a ring with no crest (a flat profile).
    """
    s = np.asarray(profile, dtype=float)
    n = s.size
    half = 0.5 * (float(s.max()) + float(s.min()))
    if not s.max() > half:
        return float("nan")
    ahead = np.roll(s, -int(np.argmax(s)))  # the crest first; then the cells after it, round the ring

    def reach(run: np.ndarray) -> float:
        """Cells from the crest to the first crossing of the half level along ``run`` (run[0] is the crest)."""
        k = int(np.argmax(run <= half))  # the first cell at or under the level: there is one, the trough
        return (k - 1) + (run[k - 1] - half) / (run[k - 1] - run[k])

    behind = np.concatenate([ahead[:1], ahead[:0:-1]])  # the crest, then the cells before it
    return (reach(ahead) + reach(behind)) * (2.0 * math.pi / n)


def compute_gas_pattern(ctx: Context) -> Mapping[str, Any]:
    R = ctx.grid.R
    # Everything is read, nothing drawn: the stellar pattern's modes, the layer's phases and checkpoint 1's disc.
    # A composed field (S55, D214): with the layer off compose gives the neutral value the declaration states,
    # everywhere. With it on, the pattern object comes from compose too, and a pattern with nothing to place
    # (unresolved, or no arm mode and no bar) is the neutral.
    cells = (R.size, ctx.grid.phi.size)

    def response() -> np.ndarray:
        shape = _compose.gas_pattern(ctx.fields, R, ctx.constants)
        if shape is None or shape.flat:
            return _compose.neutral(GAS_DENSITY_CONTRAST, cells)
        # The law's mean over each of the grid's φ cells, on each grid ring (gate G3 item 4): the interpolant
        # integrated exactly, so a ring's cells average to 1 to rounding on any grid and nothing is divided.
        return shape.cell_means(R, ctx.grid["phi"].edges)

    return {"gas_density_contrast": _compose.field(ctx.fields, GAS_DENSITY_CONTRAST, cells, response)}


GAS_PATTERN = IMPLEMENTATIONS.register(
    Stage(
        id="gas_pattern", slot="gas_pattern", checkpoint=3,
        about=(
            "The gas's own arm pattern: on every ring the steady response of isothermal gas to the stellar "
            "arm modes' potential in the frame that turns with the gas - no flow through the arms, no shock - "
            "solved ring by ring under uniform potential vorticity, and blended with the stellar bar's own "
            "term by the bar's taper (D216). Reads the stellar pattern's modes and phases and the disc's "
            "epicyclic frequency and surface density, and no gas column. Neither a contrast nor a width is "
            "put in: the measured ones are a disclosed check's target, held in the tests. The field it "
            "publishes is the response's mean over each grid cell, so every ring keeps its gas on any grid "
            "with nothing divided. It draws nothing; "
            "its field is seeded through the pattern's drawn pitch and amplitudes and the layer's phases."
        ),
        compute=compute_gas_pattern,
        reads_constants=GAS_PATTERN_CONSTANTS,
        requires=GAS_PATTERN_READS,
        publishes=(GAS_DENSITY_CONTRAST,),
    )
)
