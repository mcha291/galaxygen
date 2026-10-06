"""The arms as a census of pieces (S60, BUILD_III Phase P5; DECISIONS.md D219).

Until S60 the stellar arms were five cosine modes with drawn phases on one winding (cut into seeded segments at
S59). The owner ruled them a census of arm pieces, and a conditional gate ruled the rest (D219, nine items, its
predictions, its gate, what is forbidden; the lead's readings (a)-(d) where the ruling leaves a choice). This
file holds the build to it:

- **a piece in log-polar coordinates, by hand** - one Gaussian ridge in the perpendicular distance to its locus, at
  pitches 0, 1, 13.5 and 45 degrees: its value at points, its mean, its ring's count and amplitude, its cell means,
  its profile on the solver's cells and its forcing, derived here and held against the modules; and a chain's
  window along itself, square at a join;
- **the thickness factor** - ½ at k h = 1, and the forcing bounded by ĉ_m R/(X h) on every ring of the gate's
  galaxies;
- **the census** - a chain laid by this file's own loop from the texture seed's streams, the births' count, a
  flocculent disc's single pieces, the Milky Way's pinned loci and their continuation;
- **the gate** on the 360 galaxies of S59's three legs: ring means, the budget in expectation and the realised
  power's scatter, positivity by the saturation alone, no bit of a law moving with the layer, the gas converging;
- **the layer off** - no row, every composed field its neutral value (the comparison of every field with ``main``,
  bit for bit, is the builder's and is recorded in D219);
- **the gas between rings** - the carried profile against a direct solve at mid-gap radii, both templates;
- **the gate's predictions, as measured**, each recorded held or not held; nothing was changed to make one hold;
- **the m-split** - the composed field's Fourier power by arm number beside the law's, a disclosed check;
- **the pinned loci** on the stellar pieces by construction, and **the masers' loci against the gas's and the young
  stars' crests**, a disclosed check read against its null (``tests/reid2019.py``);
- **the pins** - a class of three and a table, by D217's mechanism - and what S59's file held that still applies:
  the numeric pins, the table kind, the young stars' reader.

**The gate's two follow-ups, and how to read this file after the third pass.** The first follow-up (after eight of
the first build's nine Milky Way predictions failed): the taper at a chain's two ends only; no chain born inside a
bar's half-length and the budget's count the chains crossing; a piece's width bounded by half the ring's crossing
spacing. The second (after the lead read the second pass: nearly circular pieces smeared round their rings, chains
crossing, births at random azimuths, the count stepping where a chain starts): **a piece is a Gaussian in the
perpendicular distance to its locus within its extent** (the wrapped normal in azimuth retired: a nearly circular
piece is an arc); **no crossing** - a drawn piece that meets another chain ends there, joined and not tapered;
**births at the midpoint of the widest gap**; **the count a sum of taper weights**; the gas's mid-gap rings; the
young stars' reader on the gas pattern's one point function; the per-region determinism test. All of it is built
and asserted here, **every pinned record below is the third pass's**, and the tests' docstrings say what each
holds now; the first two builds' numbers are in D219's record. The third pass's predictions, read before they
were judged, are recorded held or not held in ``EXPECTED_HELD``.

**What of ``tests/test_segments.py`` came here and what went** is at the foot of this docstring's list in D219's
record; in short: the pins' tests, the table kind's and the reader's are ported onto the new pattern; the winding's
own tests (its rows, its knots, its continuity, its segment statistics, its door) are deleted with the winding.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

import gas_check
import reid2019
from galaxy import templates
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core import seeds as _seeds
from galaxy.core.fielddoc import TABLES, FieldDecl, Kind
from galaxy.core.grids import GridSpec
from galaxy.core.registry import ARM_CLASSES, INPUTS, Input, RegistryError
from galaxy.layer import arm_pieces as ap
from galaxy.layer import compose
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import RunError, run
from galaxy.specs import graph
from galaxy.stages import gas_pattern as gm
from galaxy.stages import gas_response as gr
from galaxy.stages import pattern as pt
from galaxy.stages import pieces as pc
from galaxy.stages import systems

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
COMPOSED = tuple(d.name for d in pc.COMPOSED)
PATTERN = (*COMPOSED, "gas_density_contrast", "star_formation_gas_contrast", *gm.GAS_PATTERN_READS, *pt.AMPLITUDE_FIELDS,
           "arm_class", "bar_present", "pitch_angle_drawn", "sun_azimuth", "arm_saturation", "arm_contrast")
READER = ("sfr_modulation", "gas_surface_density", "sf_threshold_surface_density", "sfr_surface_density", *PATTERN)
LAWS = (*pt.AMPLITUDE_FIELDS, "arm_power_budget", "arm_design_count", "arm_piece_width", "arm_saturation", "pitch_angle", "arm_class")
LEGS = ("milky_way", "ngc_4414", "ngc_4414 drawn")
# The scalars that are not numbers, as ruled: an unbarred galaxy's bar (D217 item 3, D164) and the Sun's azimuth
# without a bar or without the pin (D218 item 5). A barred, pinned galaxy has none.
UNBARRED_NAN = {"bar_half_length", "bar_axis_ratio", "bar_boxiness", "bar_profile_index", "bar_contrast", "bar_mass_share",
                "bar_corotation_radius", "bar_pattern_speed", "sun_azimuth"}
FWHM = 2.0 * math.sqrt(2.0 * math.log(2.0))
_RUNS: dict[object, object] = {}


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def inputs_of(template: str, **more) -> dict:
    return {**templates.overrides(templates.TEMPLATES[template]), **more}


def leg_inputs(leg: str, **more) -> dict:
    """S59's three legs: the two templates, and ``ngc_4414`` with its pitch pin taken off (its other pins kept)."""
    if leg == "ngc_4414 drawn":
        return {k: v for k, v in inputs_of("ngc_4414", **more).items() if k != "pitch_angle"}
    return inputs_of(leg, **more)


def template_run(prod, template: str, fields=READER, **more):
    key = (template, fields, tuple(sorted(more.items())))
    if key not in _RUNS:
        _RUNS[key] = run(the_model(prod), inputs_of(template, **more), only=fields)
    return _RUNS[key]


def patterns(prod, o):
    c = constants(the_model(prod))
    return compose.stellar_pattern(o.fields, o.grid.R), compose.gas_pattern(o.fields, o.grid.R, c), c


def misplaced(reader: np.ndarray, law: np.ndarray) -> np.ndarray:
    """The reviewer's statistic of S59, per radius: half the mean absolute difference of two azimuthal profiles,
    each over its own mean - the share of the ring's weight the one puts where the other does not."""
    a, b = reader / reader.mean(axis=1, keepdims=True), law / law.mean(axis=1, keepdims=True)
    return 0.5 * np.abs(a - b).mean(axis=1)


# --- the declarations ----------------------------------------------------------------------------------------------


def test_the_constants_are_the_ruling_s_and_the_stages_are_declared_as_ruled(prod):
    """D219 items 1-3, 5 and 7. The numbers are the ruling's; the census is the layer's, a table, synthetic, laid
    after the pattern stage; the composed fields are a composing stage's; the phases, the winding and
    ``arm_segment`` are gone, with the ``arm_phases`` stage."""
    model = the_model(prod)
    c = constants(model)
    assert (c["ARM_PIECE_WIDTH"], c["ARM_PIECE_WIDTH_ZERO_POINT"], c["ARM_PIECE_WIDTH_RADIUS"]) == (0.53, 0.27, 2.0)
    assert (c["ARM_CHAIN_LENGTH_GRAND_DESIGN"], c["ARM_CHAIN_LENGTH_GRAND_DESIGN_SCATTER"]) == (273.0, 143.0)
    assert (c["ARM_CHAIN_LENGTH_MULTI_ARMED"], c["ARM_CHAIN_LENGTH_MULTI_ARMED_SCATTER"], c["ARM_CHAIN_LENGTH_MIN"]) == (244.0, 131.0, 90.0)
    assert (c["ARM_PIECE_FLOCCULENT_EXTENT_MIN"], c["ARM_PIECE_FLOCCULENT_EXTENT_MAX"], c["ARM_LAYER_FLATTENING"]) == (37.0, 105.0, 7.3)
    assert (c["ARM_SEGMENT_EXTENT_MEDIAN"], c["ARM_SEGMENT_EXTENT_LOG_SCATTER"], c["ARM_SEGMENT_EXTENT_MIN"], c["ARM_SEGMENT_EXTENT_MAX"],
            c["ARM_SEGMENT_PITCH_RELATIVE_SCATTER"]) == (60.0, 0.35, 20.0, 180.0, 0.56)
    g = graph.analyse(model, prod[1], prod[2])
    assert g.ok, g.problems
    order = [s.id for s in g.order]
    assert "arm_phases" not in order and order.index("pattern") < order.index("arm_pieces") < min(order.index("stellar_pattern"), order.index("gas_pattern"))
    assert g.layer_stages == ("arm_pieces", "cloud_texture") and {"stellar_pattern", "gas_pattern"} <= set(g.composing_stages)
    assert "pattern" not in g.composing_stages  # the law's stage composes nothing since S60
    assert TABLES == ("arm_piece",)
    decls = {d.name: d for s in g.order for d in s.publishes}
    for name in pt.PIECE_FIELDS:
        d = decls[name]
        assert d.kind is Kind.TABLE_COLUMN and d.of == "arm_piece" and d.provenance == "synthetic" and d.stands_in_for and d.conserves and d.statistic
    for name in COMPOSED:
        assert decls[name].composed and decls[name].provenance == "seeded", name
    for name in LAWS:
        assert not decls[name].composed and decls[name].provenance != "synthetic", name
    gone = [n for n in decls if n.startswith(("arm_mode_phase", "arm_segment", "arm_winding"))]
    assert not gone and not hasattr(pt, "Winding") and decls["pattern_density_contrast"] is pc.DENSITY_CONTRAST
    assert decls["arm_class"].categories == ARM_CLASSES == ("grand_design", "multi_armed", "flocculent")
    # The width law: FWHM(R) = 0.53 h (0.27 + 0.73 R/(2h)), by hand on the default disc.
    o = run(model, None, only=("arm_piece_width", "disc_scale_length_spin"))
    h, R = float(o.fields["disc_scale_length_spin"]), o.grid.R
    assert np.allclose(o.fields["arm_piece_width"], 0.53 * h * (0.27 + 0.73 * R / (2.0 * h)), rtol=1e-14, atol=0.0)
    assert float(np.interp(8.15, R, o.fields["arm_piece_width"])) == pytest.approx(1.9494, abs=1e-4)


# --- a piece on a ring, by hand ------------------------------------------------------------------------------------


def hand_piece(r: float, phi: np.ndarray, start_radius: float, start_azimuth: float, pitch_deg: float, extent: float, fwhm: float, free=(True, True)) -> np.ndarray:
    """**The ruling's own formulas, by this file's own arithmetic** (the gate's second follow-up, item 1): "in
    log-polar coordinates x = ln(R/R0), y = phi − phi0 the locus is the line through the origin along (sin p_j,
    cos p_j); the perpendicular distance is d = R |x cos p_j − y sin p_j| and the position along it s = R (x sin
    p_j + y cos p_j)". A lone piece (its chain's two ends its own): a Gaussian in d of dispersion
    FWHM/2.3548, times the window in s - 1 from 0 to the piece's length R Δβ/cos p, tapered linearly over one
    FWHM from each end that is ``free``, cut square at one that is not. y is the azimuth within half a turn of the
    piece's middle; a positive pitch (and 0) runs to growing azimuth (turn = +1), a negative one the other way."""
    p = math.radians(pitch_deg)
    way = 1.0 if math.tan(p) >= 0.0 else -1.0
    x = math.log(r / start_radius)
    y = way * (np.asarray(phi, dtype=float) - start_azimuth)
    y = 0.5 * extent + np.remainder(y - 0.5 * extent + math.pi, 2.0 * math.pi) - math.pi
    d = r * np.abs(x * abs(math.cos(p)) - y * abs(math.sin(p)))
    s = r * (x * abs(math.sin(p)) + y * abs(math.cos(p)))
    length = r * extent / abs(math.cos(p))
    w = np.ones(s.shape)
    if free[0]:
        w = np.minimum(w, s / fwhm)
    if free[1]:
        w = np.minimum(w, (length - s) / fwhm)
    w = np.where((s >= 0.0) & (s <= length), np.maximum(w, 0.0), 0.0)
    return w * np.exp(-0.5 * (d / (fwhm / FWHM)) ** 2)


def chain_at(stars, laid, k: int, phi: np.ndarray) -> np.ndarray:
    """The excess E of the chain whose run ends in slot ``k`` of ``laid``'s one radius, at the azimuths ``phi``."""
    for last, value in stars._chains(laid, phi[None, :]):
        if last == k:
            return value[0]
    raise AssertionError(f"no chain's run ends in slot {k}")


def hand_variance(sigma: float) -> float:
    """The variance round a ring of a full-height Gaussian ridge of azimuthal dispersion σ seen within half a turn
    of its crest: ⟨E²⟩ − ⟨E⟩² = (σ/2√π) erf(π/σ) − (σ²/2π) erf(π/√2σ)², by hand."""
    return sigma / (2.0 * math.sqrt(math.pi)) * math.erf(math.pi / sigma) - sigma**2 / (2.0 * math.pi) * math.erf(math.pi / (math.sqrt(2.0) * sigma)) ** 2


HAND_R = np.linspace(1.0, 20.0, 77)
HAND_DISC_PITCH, HAND_FWHM, HAND_BUDGET = 20.0, 0.9, 0.02
# The carrier: a second chain, one long piece of the disc's own pitch whose two ends are far from the rings read,
# so that a ring the piece under test only brushes still has a count (a ring no chain's locus crosses has none,
# and so no amplitude: a lone arc of no pitch would show nothing at all).
HAND_CARRIER = (2.0, 2.6, 20.0, 3.1)


def hand_pattern(pitch_deg: float, start_radius: float = 5.0, start_azimuth: float = 0.3, extent: float = 1.2, carrier: bool = True):
    """One arm piece of the given pitch from (5 kpc, 0.3 rad) round 1.2 radians, on a disc of this file's making:
    no bar, the disc's pitch 20 degrees, every piece 0.9 kpc wide, a budget of 0.02 on every ring - and the
    carrier chain. Returns the stellar pattern, the gas pattern and the disc's κ and Σ."""
    rows = [(0.0, 0.0, start_radius, start_azimuth, pitch_deg, extent, 0.0)] + ([(1.0, 0.0, *HAND_CARRIER, 0.0)] if carrier else [])
    columns = [np.array(c) for c in zip(*rows)]
    stars = pc.ArmPattern(HAND_R, np.full(HAND_R.size, HAND_BUDGET), np.full(HAND_R.size, 2.0), np.full(HAND_R.size, HAND_FWHM),
                          pc.Pieces(*columns, turn=1.0), float("nan"), HAND_DISC_PITCH, float("nan"))
    kappa, density = 60.0 / np.sqrt(HAND_R), 80.0 * np.exp(-HAND_R / 3.0)
    gas = gm.GasPattern(HAND_R, stars, HAND_DISC_PITCH, float("nan"), kappa, density, 4.3e-6, 8.0, 0.4)
    return stars, gas, kappa, density


@pytest.mark.parametrize("pitch", (0.0, 1.0, 13.5, 45.0))
def test_one_ridge_in_log_polar_coordinates_by_hand(pitch):
    """The gate's second follow-up, item 4: "a one-ridge hand test in log-polar coordinates to 1e-11 at pitches 0°,
    1°, 13.5° and 45°". **Derived here, independently of the modules** (:func:`hand_piece`: the ruling's formulas):
    the piece at points, on its locus and off it, inside its taper and past its ends; its mean round the ring
    (the module's closed form against this file's rule of four million midpoints); the ring's count, bounded
    width and amplitude by hand - the taper weight min(1, s/w) of each chain where its locus crosses, w = min(the
    law's, π R sin p / N), B = √(budget / (N v)) - and so the field; the exact means over cells; the ring's
    profile on the solver's cells, its variance and its m-fold powers by this file's transform; and the gas's
    forcing, each term the ridge's own times m / (X (|sin p_j| + m h/R)).

    At a pitch of 0 the piece is **an arc of its drawn extent at its radius** - regular, and seen from the rings
    beside it as a Gaussian in the radial distance R |ln(R/R_s)| - and its locus crosses no ring, so it counts on
    none: the ring's count is the carrier's alone."""
    stars, gas, kappa, density = hand_pattern(pitch)
    lone = hand_pattern(pitch, carrier=False)[0]
    fine = -math.pi + (np.arange(4_000_000) + 0.5) * (2.0 * math.pi / 4_000_000)
    sin_d = math.sin(math.radians(HAND_DISC_PITCH))
    tangent = math.tan(math.radians(pitch))
    # Radii on the piece's own reach (where it has one), just outside its start, and a width off it.
    reach = 5.0 * math.exp(1.2 * abs(tangent))
    top = min(reach, 5.9)  # (the carrier's own reach ends at 6.2 kpc)
    radii = [5.0 + 0.3 * (top - 5.0), 5.0 + 0.9 * (top - 5.0), 4.9, 5.25] if pitch else [5.0, 4.9, 5.25, 5.6]
    worst = {"point": 0.0, "mean": 0.0, "field": 0.0, "cells": 0.0}
    for r in radii:
        piece = lambda phi: hand_piece(r, phi, 5.0, 0.3, pitch, 1.2, HAND_FWHM)  # noqa: E731
        carrier = lambda phi: hand_piece(r, phi, *HAND_CARRIER, HAND_FWHM)  # noqa: E731
        means = (float(piece(fine).mean()), float(carrier(fine).mean()))
        # The count by hand: the carrier is deep inside its own length (weight 1); the piece counts where its locus
        # crosses the ring, by its distance along itself to its nearer end over the width.
        along = r * math.log(r / 5.0) / abs(math.sin(math.radians(pitch))) if pitch and 5.0 <= r < reach else None
        length = r * 1.2 / abs(math.cos(math.radians(pitch)))
        distance = None if along is None else min(along, length - along)
        # w = min(law, w_g), Σ_c min(w_g, s_c) = π R sin p: the carrier's s is far over any width.
        half_spacing = math.pi * r * sin_d
        bound = half_spacing if distance is None else (half_spacing - distance if distance < 0.5 * half_spacing else 0.5 * half_spacing)
        width = min(HAND_FWHM, bound)
        assert width == HAND_FWHM  # the law's: these rings are wide (π R sin p = 5.4 kpc at 5 kpc)
        count = 1.0 + (0.0 if distance is None else min(1.0, distance / width))
        sigma_d = (width / FWHM) / (r * sin_d)
        amplitude = math.sqrt(HAND_BUDGET / (count * hand_variance(sigma_d)))
        laid = stars.laid(np.array([r]))
        assert float(laid.count[0]) == pytest.approx(count, rel=1e-13) and float(laid.width[0]) == width
        assert float(laid.amplitude[0]) == pytest.approx(amplitude, rel=1e-12) and float(laid.effective[0]) == float(laid.amplitude[0])
        assert float(stars.amplitude_at(np.array([r]))[0]) == float(laid.amplitude[0]) and float(stars.saturation(np.array([r]))[0]) == 1.0
        # The piece's own mean round the ring: the closed form against the fine rule.
        k = int(np.flatnonzero(laid.slots[0] == 0)[0])
        worst["mean"] = max(worst["mean"], abs(float(laid.mean[0, k]) - means[0]))
        # Points: on the locus and off it, in the taper, past the ends, opposite the piece.
        crest = 0.3 + (math.log(r / 5.0) / tangent if pitch else 0.0)
        phi = np.array([crest, crest + 0.07, crest - 0.2, 0.3, 0.3 + 0.05, 0.3 + 0.6, 0.3 + 1.2, 0.3 + 1.25, 0.3 - 0.1, 0.3 + 0.6 + math.pi - 1e-9, -2.0, 2.9])
        want = amplitude * ((piece(phi) - means[0]) + (carrier(phi) - means[1]))
        worst["field"] = max(worst["field"], float(np.abs(stars.arms_at(np.array([r]), phi) - want).max()))
        worst["point"] = max(worst["point"], float(np.abs(chain_at(stars, laid, k, phi) - piece(phi)).max()))
        assert np.array_equal(stars.contrast_at(np.array([r]), phi), 1.0 + stars.arms_at(np.array([r]), phi))
        # Exact means over cells: they tile the ring to nothing, and each is the fine rule's mean over the cell.
        edges = np.linspace(-math.pi, math.pi, 41)
        cells = stars.arm_cell_means(np.array([r]), edges)[0]
        by_rule = (amplitude * ((piece(fine) - means[0]) + (carrier(fine) - means[1]))).reshape(40, -1).mean(axis=1)
        worst["cells"] = max(worst["cells"], float(np.abs(cells - by_rule).max()))
        assert abs(cells.sum()) < 1e-14 and np.array_equal(stars.sector_means(r, edges), 1.0 + cells)
        # On the solver's cells: the profile, its variance and its m-fold powers "by the same quadrature".
        centres = gr.cell_centres(gr.CELLS)
        profile = amplitude * ((piece(centres) - means[0]) + (carrier(centres) - means[1]))
        assert np.abs(stars.ring_profile(np.array([r]))[0] - profile).max() < 1e-10
        spectrum = np.fft.rfft(profile) / gr.CELLS
        power, by_mode = stars.ring_power(np.array([r]))
        assert float(power[0]) == pytest.approx(float(((profile - profile.mean()) ** 2).mean()), rel=1e-10)
        assert by_mode[:, 0] == pytest.approx([(2.0 * abs(spectrum[m])) ** 2 for m in pt.ARM_MODES], rel=1e-9, abs=1e-18)
        # The forcing: each piece's ridge on the cells transformed, term m times m / (X (|sin p_j| + m h/R)).
        kap, dens = float(np.interp(r, HAND_R, kappa)), float(np.interp(r, HAND_R, density))
        x = kap**2 * r / (2.0 * math.pi * 4.3e-6 * dens * 1.0e6)
        m = np.arange(gr.CELLS // 2 + 1, dtype=float)
        by_hand = np.zeros(gr.CELLS)
        for ridge, own in ((piece(centres), pitch), (carrier(centres), 20.0)):
            with np.errstate(invalid="ignore"):  # (term 0, the mean, at a pitch of 0: nothing over nothing, and not used)
                factor = np.where(m > 0.0, m / (x * (abs(math.sin(math.radians(own))) + m * 0.4 / r)), 0.0)
            by_hand += np.fft.irfft(np.fft.rfft(amplitude * ridge) * factor, n=gr.CELLS)
        on_cells = gas.forcing(np.array([r]))[0]
        assert np.abs(on_cells - by_hand).max() < 1e-11 and abs(on_cells.mean()) < 1e-15
        assert np.all(factor <= r / (x * 0.4) * (1.0 + 1e-15))  # bounded by R/(X h) whatever the pitch
        # The gas answers it: mean 1, positive, by the solver.
        s = gas.solve_at(np.array([r]))[0]
        assert abs(s.mean() - 1.0) < 1e-12 and s.min() > 0.0
        # Without the carrier, a ring the lone piece's locus does not cross has no count and no arm.
        if distance is None:
            assert float(lone.count_at(np.array([r]))[0]) == 0.0 and np.all(lone.arms_at(np.array([r]), phi) == 0.0)
    assert worst["point"] < 1e-13 and worst["mean"] < 1e-11 and worst["field"] < 1e-11 and worst["cells"] < 1e-11, worst
    # The arc of no pitch: its ridge on a ring beside it is one height along its whole drawn extent.
    if not pitch:
        arc = hand_piece(5.25, np.array([0.3 + 0.4, 0.3 + 0.6, 0.3 + 0.8]), 5.0, 0.3, 0.0, 1.2, HAND_FWHM)
        assert np.ptp(arc) < 1e-15 and float(arc[0]) == pytest.approx(math.exp(-0.5 * (5.25 * math.log(5.25 / 5.0) / (HAND_FWHM / FWHM)) ** 2), rel=1e-14)


def hand_segment(r: float, phi: np.ndarray, start_radius: float, start_azimuth: float, pitch_deg: float, extent: float, before: float, after: float):
    """**This file's own arithmetic of the gate's third follow-up**: (the squared distance in the plane's unit from
    the points (r, phi) to one piece as a segment of its chain's polyline, the arc length along the chain at the
    nearest point) - "the perpendicular distance to the nearest piece where the point's foot falls inside that
    piece, the distance to the nearest piece end otherwise" - the piece seen at the image within half a turn of its
    middle, each end at its nearest image; ``before``/``after`` the chain's length before the piece's start and after
    its end (infinite: that side joined)."""
    p = math.radians(pitch_deg)
    way = 1.0 if math.tan(p) >= 0.0 else -1.0
    s, c = abs(math.sin(p)), abs(math.cos(p))
    length = extent / c
    x = math.log(r / start_radius)
    y = way * (np.asarray(phi, dtype=float) - start_azimuth)
    y = 0.5 * extent + np.remainder(y - 0.5 * extent + math.pi, 2.0 * math.pi) - math.pi
    t, d = x * s + y * c, x * c - y * s
    inside = (t >= 0.0) & (t <= length)
    best, arc = np.where(inside, d * d, np.inf), np.where(inside, before + t, 0.0)
    for at_y, at_t in ((0.0, 0.0), (extent, length)):
        dy = y - at_y
        dy = dy - 2.0 * math.pi * np.round(dy / (2.0 * math.pi))
        dx = x - at_t * s
        dd = dx * dx + dy * dy
        nearer = dd < best
        best, arc = np.where(nearer, dd, best), np.where(nearer, before + at_t, arc)
    return best, arc


def hand_polyline(r: float, phi: np.ndarray, rows: list, fwhm: float, joined_outer: bool = False) -> np.ndarray:
    """E of a chain by hand: the Gaussian of the least distance over its pieces (``rows``: start radius, start
    azimuth, pitch, extent, joined end to start) times the taper - over one width from each free end, read at the
    arc length of the nearest point; the outer end joined where ``joined_outer``."""
    lengths = [row[3] / abs(math.cos(math.radians(row[2]))) for row in rows]
    total = sum(lengths)
    best, arc = np.full(np.shape(phi), np.inf), np.zeros(np.shape(phi))
    for k, row in enumerate(rows):
        d2, a = hand_segment(r, phi, *row, sum(lengths[:k]), math.inf if joined_outer else sum(lengths[k + 1:]))
        nearer = d2 < best
        best, arc = np.where(nearer, d2, best), np.where(nearer, a, arc)
    w = fwhm / r
    taper = np.minimum(1.0, np.minimum(arc / w, (math.inf if joined_outer else (total - arc)) / w))
    return taper * np.exp(-best / (2.0 * (fwhm / FWHM / r) ** 2))


def test_two_pieces_at_a_kink_and_a_joined_end_by_hand():
    """The gate's third follow-up, item 1, **derived here independently of the module** (:func:`hand_segment`,
    :func:`hand_polyline`): a chain of two pieces - 20 degrees over 0.5 rad from (5 kpc, 0.3 rad), then a kink to
    5 degrees over 0.6 rad, the outer end joined to another chain. At a point in the kink's outside wedge the
    distance is to the corner, inside it to the nearer piece; the joined end is a round cap of the piece's own
    width at full height; the taper rises from the chain's free start along the chain, through the kink. The
    chain's value at points, its mean round the ring (against this file's rule of four million midpoints) and the
    exact means over cells, on rings below the kink, through it and above it; and the ring's count is the chain's
    taper weight where its locus crosses, from either side of the kink."""
    x1 = math.log(5.0) + 0.5 * math.tan(math.radians(20.0))
    r_kink = math.exp(x1)
    rows = [(5.0, 0.3, 20.0, 0.5), (r_kink, 0.8, 5.0, 0.6)]
    table = [(0.0, 0.0, 5.0, 0.3, 20.0, 0.5, 0.0, 0.0), (0.0, 1.0, r_kink, 0.8, 5.0, 0.6, 0.0, 2.0), (1.0, 0.0, *HAND_CARRIER, 0.0, 0.0)]
    columns = [np.array(c) for c in zip(*table)]
    p = pc.Pieces(*columns[:7], turn=1.0, join=columns[7])
    assert p.joins == 1 and p.before[0] == 0.0 and math.isinf(p.after[1]) and p.after[0] == p.after[1] and p.link_end[0] == 1 and p.link_start[1] == 0
    stars = pc.ArmPattern(HAND_R, np.full(HAND_R.size, HAND_BUDGET), np.full(HAND_R.size, 2.0), np.full(HAND_R.size, HAND_FWHM), p, float("nan"), HAND_DISC_PITCH, float("nan"))
    fine = -math.pi + (np.arange(4_000_000) + 0.5) * (2.0 * math.pi / 4_000_000)
    carrier = [HAND_CARRIER]
    worst = {"point": 0.0, "mean": 0.0, "cells": 0.0}
    for r in (4.9, 5.1, r_kink * 0.999, r_kink, r_kink * 1.001, 5.3, 5.5, 5.6):
        laid = stars.laid(np.array([r]))
        k = int(np.flatnonzero(laid.last[0] & np.isin(laid.slots[0], (0, 1)))[0])
        phi = np.concatenate([np.linspace(0.0, 1.8, 181), [0.8 + 0.2 * math.pi, 0.5, 2.9, -2.0]])
        want = hand_polyline(r, phi, rows, HAND_FWHM, joined_outer=True)
        worst["point"] = max(worst["point"], float(np.abs(chain_at(stars, laid, k, phi) - want).max()))
        on_ring = hand_polyline(r, fine, rows, HAND_FWHM, joined_outer=True)
        worst["mean"] = max(worst["mean"], abs(float(laid.mean[0, k]) - float(on_ring.mean())))
        edges = np.linspace(-math.pi, math.pi, 41)
        other = hand_polyline(r, fine, carrier, HAND_FWHM)
        by_rule = (laid.effective[0] * ((on_ring - on_ring.mean()) + (other - other.mean()))).reshape(40, -1).mean(axis=1)
        cells = stars.arm_cell_means(np.array([r]), edges)[0]
        worst["cells"] = max(worst["cells"], float(np.abs(cells - by_rule).max()))
        assert abs(cells.sum()) < 1e-14
    assert worst["point"] < 1e-13 and worst["mean"] < 1e-11 and worst["cells"] < 1e-11, worst
    # The kink by hand, on the ring a little above it: outside the kink (the side the chain turns away from) the
    # distance is to the corner, inside it to the nearer piece - and the module reads the same.
    r = r_kink * math.exp(0.0005)
    x = math.log(r / r_kink)
    for dphi, outside in ((-0.0001, True), (0.001, False)):  # (the wedge is as narrow as the turn, 15 degrees: at dx = 5e-4 it spans dphi -1.8e-4 to -4.4e-5)
        phi = np.array([0.8 + dphi])
        d_first, _ = hand_segment(r, phi, *rows[0], 0.0, math.inf)
        d_second, _ = hand_segment(r, phi, *rows[1], 0.0, math.inf)
        corner = x * x + dphi * dphi
        if outside:
            assert float(min(d_first[0], d_second[0])) == pytest.approx(corner, rel=1e-12)
        else:
            assert float(min(d_first[0], d_second[0])) < corner * (1.0 - 1e-6)
        laid = stars.laid(np.array([r]))
        k = int(np.flatnonzero(laid.last[0] & np.isin(laid.slots[0], (0, 1)))[0])
        assert float(chain_at(stars, laid, k, phi)[0]) == pytest.approx(math.exp(-min(d_first[0], d_second[0]) / (2.0 * (HAND_FWHM / FWHM / r) ** 2)), rel=1e-12)
    # The joined end: a round cap at full height - at a point past the end along the piece's line, the value is the
    # Gaussian of the distance to the end, not 0 as a square window gave.
    r_end = r_kink * math.exp(0.6 * math.tan(math.radians(5.0)))
    r = r_end * math.exp(-0.002)  # (the carrier chain reaches 6.17 kpc; this ring, 6.31 kpc, is still crossed by it and lies in the cap region, t > T, ahead of the end in azimuth)
    phi = np.array([0.8 + 0.6 + 0.01])
    laid = stars.laid(np.array([r]))
    k = int(np.flatnonzero(laid.last[0] & np.isin(laid.slots[0], (0, 1)))[0])
    d_end = math.log(r / r_end) ** 2 + 0.01 ** 2
    _, arc = hand_segment(r, phi, *rows[1], 0.0, math.inf)
    assert float(chain_at(stars, laid, k, phi)[0]) == pytest.approx(math.exp(-d_end / (2.0 * (HAND_FWHM / FWHM / r) ** 2)), rel=1e-12) and arc[0] == pytest.approx(0.6 / math.cos(math.radians(5.0)))
    # The count: the chain's taper weight at the kink is the first piece's length over the width, from either side.
    # (The carrier is inside its own end taper here: its free end at 6.17 kpc is 0.49 kpc along it from this ring.)
    carrier_end = HAND_CARRIER[0] * math.exp(HAND_CARRIER[3] * math.tan(math.radians(HAND_CARRIER[2])))
    carrier_weight = min(1.0, math.log(carrier_end / r_kink) / math.sin(math.radians(HAND_CARRIER[2])) * r_kink / HAND_FWHM)
    below, above = stars.count_at(np.array([r_kink * (1.0 - 1e-12), r_kink * (1.0 + 1e-12)])) - carrier_weight
    assert below == pytest.approx(min(1.0, r_kink * 0.5 / math.cos(math.radians(20.0)) / HAND_FWHM), rel=1e-9) and above == pytest.approx(below, rel=1e-9)


def test_the_thickness_factor_by_hand():
    """D219 item 5: "the thickness factor per harmonic turns f_m into |m| ĉ_m/(X(|sin p| + |m| h/R)), bounded by
    ĉ_m R/(X h) for every m and pitch, regular at sin p = 0"; the gate: "T = ½ at kh = 1"."""
    for m, sin_p in ((2.0, 0.2), (5.0, 0.05), (1.0, 1.0)):
        h_over_r = sin_p / m  # k h = m h / (R sin p) = 1
        assert float(pc.thickness_factor(m, sin_p, h_over_r)) == pytest.approx(0.5, rel=1e-15)
        assert float(pc.forcing_factor(m, 3.0, sin_p, h_over_r)) == pytest.approx(0.5 * m / (3.0 * sin_p), rel=1e-15)
    m = np.arange(1.0, 129.0)
    for sin_p in (0.0, 1e-12, 0.0175, 0.24, -0.5, 1.0):
        f = pc.forcing_factor(m, 2.5, sin_p, 0.04)
        assert np.all(np.isfinite(f)) and np.all(f <= 1.0 / (2.5 * 0.04) * (1.0 + 1e-15))
    assert float(pc.forcing_factor(4.0, 2.5, 0.0, 0.04)) == pytest.approx(1.0 / (2.5 * 0.04), rel=1e-15)  # the bound, met at sin p = 0
    assert float(pc.thickness_factor(3.0, 0.3, 0.0)) == 1.0  # a razor-thin layer: D216's forcing


# --- the census ----------------------------------------------------------------------------------------------------


def hand_chain(seed: int, chain: int, x: float, azimuth: float, pitch: float, mean: float, sd: float, x_edge: float):
    """A chain laid by this file's own loop from the texture seed's streams: (start radius, start azimuth, pitch,
    extent) per piece, and the drawn length in radians. Not cut where it meets another chain: :func:`cut_at_meeting`."""
    def stream(*path):
        return _seeds.rng(seed, "arm_pieces", "chain", chain, *path)

    g = stream("length")
    length = float(g.normal(mean, sd))
    while length < 90.0:
        length = float(g.normal(mean, sd))
    left, rows, k = math.radians(length), [], 0
    while left > 0.0 and x <= x_edge:
        g = stream("out", k)
        z = float(g.normal())
        extent = 60.0 * math.exp(0.35 * float(g.normal()))
        while not 20.0 <= extent <= 180.0:
            extent = 60.0 * math.exp(0.35 * float(g.normal()))
        extent = min(math.radians(extent), left)
        p = pitch * (1.0 + 0.56 * z)
        rows.append((math.exp(x), azimuth, p, extent))
        t = math.tan(math.radians(p))
        x, azimuth, left, k = x + extent * abs(t), azimuth + extent * (1.0 if t >= 0.0 else -1.0), left - extent, k + 1
    return rows, math.radians(length)


def line_of(row) -> tuple[float, float, float, float]:
    """A piece (start radius, start azimuth, pitch in degrees, extent) as its straight line in the plane of ln R
    and azimuth: (x0, y0, x1, y1), the azimuth not wrapped (turn = +1: the model's discs all turn one way)."""
    r, azimuth, pitch, extent = (float(v) for v in row)
    t = math.tan(math.radians(pitch))
    return math.log(r), azimuth, math.log(r) + extent * abs(t), azimuth + extent * (1.0 if t >= 0.0 else -1.0)


def meets(a, b) -> list[tuple[float, float]]:
    """Where the line ``a`` meets the line ``b`` or one of its images a turn either way: (share along a, share
    along b) for each meeting, by Cramer's rule - this file's own, not the model's."""
    out = []
    ax, ay, bx, by = a[2] - a[0], a[3] - a[1], b[2] - b[0], b[3] - b[1]
    det = ax * by - ay * bx
    if det == 0.0:
        return out
    base = 2.0 * math.pi * round((a[1] - b[1]) / (2.0 * math.pi))
    for turns in (-1, 0, 1):
        ox, oy = b[0] - a[0], b[1] + base + 2.0 * math.pi * turns - a[1]
        s, t = (ox * by - oy * bx) / det, (ox * ay - oy * ax) / det
        if 0.0 <= s <= 1.0 and 0.0 <= t <= 1.0:
            out.append((s, t))
    return out


def cut_at_meeting(rows: list, others: list) -> tuple[list, bool]:
    """A hand-laid chain ended where one of its pieces first meets a line of ``others``: (the rows kept, the last
    one shortened to the meeting; whether it was cut)."""
    kept = []
    for row in rows:
        # ... any chain's lines, its own earlier pieces included but for the one it is laid from (the fourth follow-up, A).
        shares = [s for other in others + [line_of(r) for r in kept[:-1]] for s, _ in meets(line_of(row), other) if s > 1e-12]
        if shares:
            return kept + [(row[0], row[1], row[2], min(shares) * row[3])], True
        kept.append(row)
    return kept, False


def crossings(table: np.ndarray) -> tuple[int, int]:
    """(proper crossings between two pieces at least one of which is drawn - of different chains, **or of one
    chain** (the fourth follow-up, A: "no chain crosses any chain, itself included"); between two pinned ones): two
    lines that meet inside both - not at an end of either, which is a join, a kink or a touch."""
    lines = [line_of(row[2:6]) for row in table]
    drawn = pinned = 0
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if any(1e-9 < s < 1.0 - 1e-9 and 1e-9 < t < 1.0 - 1e-9 for s, t in meets(lines[i], lines[j])):
                both = table[i, 6] == 1.0 and table[j, 6] == 1.0
                pinned, drawn = pinned + both, drawn + (not both)
    return drawn, pinned


def continued_inside_the_bar(table: np.ndarray, a: float) -> int:
    """How many drawn pieces continuing a pinned chain lie, in any part, inside the bar's half-length ``a`` (the
    fourth follow-up, A: an end inside it is not continued, and an inward continuation stops at it)."""
    pinned_chains = set(table[table[:, 6] == 1.0][:, 0].tolist())
    rows = table[(table[:, 6] == 0.0) & np.isin(table[:, 0], list(pinned_chains))]
    return int((rows[:, 2] < a * (1.0 - 1e-12)).sum())


def births_off_the_widest_gap(table: np.ndarray, R: np.ndarray, first_free: int) -> tuple[int, int, float]:
    """(chains born in a gap, chains born on a ring no chain crossed, the worst distance in radians of a birth
    from the midpoint of the widest gap) - the gate's second follow-up, item 3, by this file's own arithmetic.
    Chains are made in the order of their numbers, so the chains crossing a birth ring when chain c is born are
    those of a lower number (and every pinned piece). ``first_free`` is the first chain that is a birth."""
    lines = {int(c): [line_of(row[2:6]) for row in table[table[:, 0] == c]] for c in np.unique(table[:, 0])}
    in_gap, alone, worst = 0, 0, 0.0
    for chain in sorted(lines):
        if chain < first_free:
            continue
        own = table[table[:, 0] == chain]
        born = own[own[:, 1] == 0.0][0]
        x = math.log(float(born[2]))
        at = sorted((y0 + (x - x0) / (x1 - x0) * (y1 - y0)) % (2.0 * math.pi)
                    for c, parts in lines.items() if c < chain for x0, y0, x1, y1 in parts if x0 <= x < x1)
        if not at:
            alone += 1
            continue
        gaps = [(at[k + 1] - a) if k + 1 < len(at) else (at[0] + 2.0 * math.pi - a) for k, a in enumerate(at)]
        # (Two gaps of one width - the two halves a second chain leaves, opposite the first - differ here and in the
        #  model by rounding alone: a birth at the middle of either is at the widest gap's.)
        widest = [k for k, gap in enumerate(gaps) if gap >= max(gaps) - 1e-9]
        worst = max(worst, min(abs(math.remainder(float(born[3]) - (at[k] + 0.5 * gaps[k]), 2.0 * math.pi)) for k in widest))
        in_gap += 1
    return in_gap, alone, worst


def table_of(F) -> np.ndarray:
    return np.stack([np.asarray(F[n], dtype=float) for n in pt.PIECE_FIELDS], axis=1)


def test_the_census_by_hand_a_barred_disc_s_chains(prod):
    """D219 items 2-3 and the gate's second follow-up, items 2-3, on the bare default galaxy (barred, no pin: a
    grand design). Chains 0 and 1 start at the bar's two ends - R = a, φ_bar and φ_bar + π - and are this file's
    own laying of the streams' draws, to the bit of every row: a piece's deviate first, then its extent (drawn
    again outside 20°-180°), its pitch p(1 + 0.56 z), the chain's length a normal of 273° ± 143° drawn again under
    90°, the last piece cut to it - **and the second chain ended where it first meets the first**, by this file's
    own intersection of two straight lines in the plane of ln R and azimuth, if it meets it. Then the births:
    every ring with a budget past the bar is crossed by at least the law's arm number of chains, no chain was
    started where enough already crossed, **every birth stands at the midpoint of the widest gap between the
    chains crossing its ring**, and **no two chains cross**."""
    model = the_model(prod)
    o = run(model, {"texture_seed": 7}, only=PATTERN)
    F, R = o.fields, o.grid.R
    assert F["arm_class"] == "grand_design" and F["bar_present"] == "yes"
    a, pitch = float(F["bar_half_length"]), float(F["pitch_angle"])
    bar_angle = math.log(a) / math.tan(math.radians(pitch))
    rows = table_of(F)
    assert rows.shape[1] == 8 and np.all(rows[:, 6] == 0.0) and set(rows[:, 7].tolist()) <= {0.0, 1.0, 2.0}
    laid: list = []
    for chain, end in ((0, 0.0), (1, math.pi)):
        mine, length = hand_chain(7, chain, math.log(a), bar_angle + end, pitch, 273.0, 143.0, math.log(R[-1]))
        mine, cut = cut_at_meeting(mine, laid)
        theirs = rows[rows[:, 0] == chain]
        assert np.array_equal(theirs[:, 1], np.arange(len(mine)))
        want = np.array([(r, azimuth % (2.0 * math.pi), p, extent) for r, azimuth, p, extent in mine])
        assert np.allclose(theirs[:, 2:6], want, rtol=1e-12, atol=1e-12), chain
        assert float(theirs[0, 2]) == pytest.approx(a, rel=1e-15) and bool(theirs[-1, 7] == 2.0) == cut and np.all(theirs[:-1, 7] == 0.0)
        # The last piece is cut to the chain's drawn length - unless the chain left the grid, or met another, first.
        left_the_grid = mine[-1][0] * math.exp(mine[-1][3] * abs(math.tan(math.radians(mine[-1][2])))) > R[-1]
        assert cut or left_the_grid or float(theirs[:, 5].sum()) == pytest.approx(length, rel=1e-13)
        laid += [line_of(row) for row in mine]
    sp = compose.stellar_pattern(F, R)
    count, design, budget = np.asarray(F["arm_chain_count"]), np.asarray(F["arm_design_count"]), np.asarray(F["arm_power_budget"])
    has = budget > 0.0
    past = has & (R >= a)  # the first follow-up, item 2: no chain is born inside the bar's half-length
    assert np.all(count[past] >= design[past]) and np.all(design[has] >= 2.0) and np.all(design[~has] == 0.0)
    firsts = rows[rows[:, 1] == 0.0]
    assert np.all(firsts[:, 2] >= a * (1.0 - 1e-12)) and np.all(count[R < a] == 0.0)
    assert np.array_equal(count, sp.pieces.chains_crossing(R)) and sp.pieces.joins == int((rows[:, 7] != 0.0).sum())
    # A birth happens only where fewer chains cross than the law counts: each born chain's first ring held, without
    # it and the later-born, fewer than the law's number.
    starts = {int(ch): float(r) for ch, order, r in zip(rows[:, 0], rows[:, 1], rows[:, 2]) if order == 0.0}
    spans = {int(ch): (float(rows[rows[:, 0] == ch][:, 2].min()),
                       float((rows[rows[:, 0] == ch][:, 2] * np.exp(rows[rows[:, 0] == ch][:, 5] * np.abs(np.tan(np.radians(rows[rows[:, 0] == ch][:, 4]))))).max()))
             for ch in np.unique(rows[:, 0])}
    for chain, r in starts.items():
        if chain < 2:
            continue
        i = int(np.argmin(np.abs(R - r)))
        assert R[i] == pytest.approx(r, rel=1e-14)
        earlier = sum(1 for ch, (lo, hi) in spans.items() if ch < chain and lo <= R[i] < hi)
        assert earlier < design[i], (chain, r)
    # Every birth at the widest gap's midpoint; no two chains cross; a joined end is a chain's last.
    in_gap, alone, worst = births_off_the_widest_gap(rows, R, 2)
    assert in_gap == len(starts) - 2 and alone == 0 and worst < 1e-12
    assert crossings(rows) == (0, 0)
    # The table is what the stage says it is: by chain, inside out along each.
    assert np.all(np.diff(rows[:, 0]) >= 0.0)
    for chain in np.unique(rows[:, 0]):
        part = rows[rows[:, 0] == chain]
        assert np.array_equal(part[:, 1], np.arange(part.shape[0])) and np.all(np.diff(part[:, 2]) >= 0.0)
        # Pieces of a drawn chain are joined end to start, and only its last piece's outer end meets another chain.
        t = np.tan(np.radians(part[:, 4]))
        end_r, end_phi = part[:, 2] * np.exp(part[:, 5] * np.abs(t)), part[:, 3] + part[:, 5] * np.where(t >= 0.0, 1.0, -1.0)
        assert np.allclose(end_r[:-1], part[1:, 2], rtol=1e-12) and np.allclose(np.mod(end_phi[:-1] - part[1:, 3] + math.pi, 2.0 * math.pi), math.pi, atol=1e-12)
        assert np.all(part[:-1, 7] == 0.0) and part[-1, 7] in (0.0, 2.0)
    record = (rows.shape[0], len(starts), sp.pieces.joins)
    # (pieces, chains, joins)
    assert record == EXPECTED_DEFAULT_CENSUS, repr(record)


EXPECTED_DEFAULT_CENSUS: tuple = (32, 6, 1)


def test_a_flocculent_disc_is_single_pieces_and_an_unbarred_one_has_no_chain_from_a_bar(prod):
    """D219 item 3. ``ngc_4414`` is pinned flocculent: every chain is one piece, its extent inside 37°-105° as
    drawn - a piece that meets another chain ends there, and is then shorter (the second follow-up, item 2) - and
    at least the law's number cross every ring with a budget where it was laid. With the class pin taken off the same unbarred
    galaxy is multi-armed: chains of several pieces, their length drawn about 244°, and no chain starts at a
    bar's end (there is none). The pin moves no law."""
    model = the_model(prod)
    floc = run(model, inputs_of("ngc_4414"), only=PATTERN)
    multi = run(model, {k: v for k, v in inputs_of("ngc_4414").items() if k != "arm_class"}, only=PATTERN)
    assert floc.fields["arm_class"] == "flocculent" and multi.fields["arm_class"] == "multi_armed" and floc.fields["bar_present"] == "no"
    rows = table_of(floc.fields)
    assert np.all(rows[:, 1] == 0.0) and len(np.unique(rows[:, 0])) == rows.shape[0]
    whole = rows[rows[:, 7] == 0.0]
    extent = np.degrees(whole[:, 5])
    assert 37.0 <= extent.min() and extent.max() <= 105.0 and np.all(np.degrees(rows[:, 5]) <= 105.0)
    record = (rows.shape[0], int((rows[:, 7] != 0.0).sum()), round(float(extent.min()), 1), round(float(extent.max()), 1))
    # (pieces, those ended at a join, the least and the greatest extent of the others in degrees)
    assert record == EXPECTED_FLOCCULENT, repr(record)
    has = np.asarray(floc.fields["arm_power_budget"]) > 0.0
    assert np.all(np.asarray(floc.fields["arm_chain_count"])[has] >= np.asarray(floc.fields["arm_design_count"])[has])
    assert crossings(rows) == (0, 0) and births_off_the_widest_gap(rows, floc.grid.R, 0)[2] < 1e-12
    other = table_of(multi.fields)
    pieces_per_chain = np.bincount(other[:, 0].astype(int))
    assert pieces_per_chain.max() > 3 and other.shape[0] > rows.shape[0]
    for name in LAWS:
        if name != "arm_class":
            assert np.asarray(floc.fields[name]).tobytes() == np.asarray(multi.fields[name]).tobytes(), name


def test_the_milky_way_s_pinned_pieces_lie_on_the_measured_loci_and_are_continued_by_drawn_ones(prod):
    """D219 item 8 and the lead's reading (c). Each pinned row of Reid et al. 2019's Table 2 is a chain of its
    fitted pieces - two where its two pitches differ, one for the Local arm - **exactly on the fitted locus**
    over its β range (asserted to 1e-12: by construction, not a test of the model), the Sun at β = 0 by the
    pinned bar angle. Each is continued by drawn pieces flagged unpinned: outward past its low-β end, and inward
    past its high-β end as far as the bar's half-length (none where that end is already inside the bar). The
    3 kpc arm is not entered, and no chain starts at the bar's ends."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp, _, _ = patterns(prod, o)
    rows = table_of(F)
    sun, a = float(F["sun_azimuth"]), float(F["bar_half_length"])
    sense = pt.rotation_sense(float(F["pitch_angle"]))
    assert sense == -1.0 and F["arm_class"] == "grand_design"
    table = {row[0]: row for row in reid2019.TABLE2}
    assert reid2019.PINNED == ("Norma", "Sct-Cen", "Sgr-Car", "Local", "Perseus", "Outer") and "3-kpc(N)" not in reid2019.PINNED
    p = sp.pieces
    worst = 0.0
    for chain, name in enumerate(reid2019.PINNED):
        part = rows[rows[:, 0] == chain]
        pinned = part[part[:, 6] == 1.0]
        _, lo, hi, kink, r_kink, below, above = table[name]
        assert pinned.shape[0] == (1 if below == above else 2), name
        assert sorted(pinned[:, 4].tolist()) == sorted({below, above}) and float(pinned[:, 5].sum()) == pytest.approx(math.radians(hi - lo), rel=1e-14)
        # The locus by the source's formula against the model's own piece, at every degree of the range.
        beta, radius = reid2019.locus(table[name])
        phi = sun + sense * np.radians(beta)
        for b, r, f in zip(beta, radius, phi):
            pitch = below if b <= kink else above
            k = int(np.flatnonzero((p.chain == chain) & (p.pinned == 1.0) & (p.pitch_deg == pitch))[0])
            share = (math.log(r) - p.x_start[k]) / (p.x_end[k] - p.x_start[k])
            on_piece = p.phi_start[k] + share * (p.phi_end[k] - p.phi_start[k])
            assert -1e-9 <= share <= 1.0 + 1e-9
            worst = max(worst, abs(math.remainder(on_piece - f, 2.0 * math.pi)) * r)
        drawn = part[part[:, 6] == 0.0]
        # The fourth follow-up, A: continued outward from the end of greater radius and inward from the other, each
        # only if at or outside the bar's half-length; the inward part no further than a.
        ends = (reid2019.locus(table[name])[1][0], reid2019.locus(table[name])[1][-1])
        outer_end, inner_end = max(ends), min(ends)
        assert drawn.shape[0] == 0 or float(drawn[:, 2].min()) >= a * (1.0 - 1e-12), name
        if outer_end < a:
            assert drawn.shape[0] == 0, name
        elif inner_end < a:
            assert np.all(drawn[:, 2] >= outer_end * (1.0 - 1e-9)), name  # only the outward continuation
    assert worst < 1e-12  # kpc: the pinned pieces are the fitted loci
    # No chain is tied to the bar: none starts at (a, the bar's angle) or its opposite.
    bar_angle = sp.bar_angle
    at_bar = [r for r in rows if abs(r[2] - a) < 1e-9 and min(abs(math.remainder(r[3] - bar_angle, math.pi)), 1.0) < 1e-9 and r[1] == 0.0]
    assert not at_bar
    # No pinned piece is cut, and no drawn piece crosses another chain; the births stand in the widest gaps.
    assert np.all(rows[rows[:, 6] == 1.0][:, 7] == 0.0)
    drawn_crossings, pinned_crossings = crossings(rows)
    assert drawn_crossings == 0 and births_off_the_widest_gap(rows, R, 6)[2] < 1e-12 and continued_inside_the_bar(rows, a) == 0
    record = (rows.shape[0], len(np.unique(rows[:, 0])), int(rows[:, 6].sum()),
              [int((rows[(rows[:, 0] == c)][:, 6] == 0.0).sum()) for c in range(6)], int((rows[:, 7] != 0.0).sum()), pinned_crossings)
    # (pieces, chains, pinned pieces, the drawn pieces that continue each of the six pinned chains, the joins,
    #  the crossings of two measured pieces - which are never cut)
    assert record == EXPECTED_PINNED, repr(record)
    # A galaxy whose arms are pinned needs the Sun: without the bar's angle to it, or without a bar, it is refused.
    pins = templates.pinned(templates.TEMPLATES["milky_way"])
    for missing in ("sun_bar_angle", "bar_present"):
        given = {k: v for k, v in pins.items() if k != missing} | ({"bar_present": False} if missing == "bar_present" else {})
        with pytest.raises(ValueError, match="placed by the Sun's azimuth"):
            run(the_model(prod), given, SMALL, only=("arm_piece_chain",))


EXPECTED_FLOCCULENT: tuple = (37, 2, 37.7, 103.6)


def test_no_chain_crosses_any_chain_on_300_texture_seeds_of_the_milky_way(prod):
    """The gate's fourth follow-up, A, on 300 texture seeds of the Milky Way template (the reviewer of the third
    pass found Norma's continuation crossing Norma's own 19.5-degree stretch on 6 of 300): no chain crosses any
    chain, itself included; no continuation of a pinned chain starts inside the bar's half-length or runs inside
    it; every birth in the widest gap. The joins over the 300 seeds are recorded."""
    model = the_model(prod)
    joins = []
    for seed in range(300):
        o = run(model, inputs_of("milky_way", texture_seed=seed), only=(*pt.PIECE_FIELDS, "bar_half_length"))
        table = table_of(o.fields)
        drawn, pinned = crossings(table)
        assert drawn == 0 and pinned == 0 and continued_inside_the_bar(table, float(o.fields["bar_half_length"])) == 0, seed
        assert births_off_the_widest_gap(table, o.grid.R, 6)[2] < 1e-9, seed
        joins.append(int((table[:, 7] != 0.0).sum()))
    record = (min(joins), float(np.median(joins)), max(joins))
    assert record == EXPECTED_JOINS_300, repr(record)


EXPECTED_JOINS_300: tuple = (0, 5.0, 13)


# --- the gate ------------------------------------------------------------------------------------------------------


def test_gate_on_the_three_legs_of_the_suite_s_galaxies(prod):
    """D219's gate: "Ring means 1 to 1e-12 on cells; expected ring power = budget to 1e-10 by the analytic
    expectation, the realised power per ring published and its scatter pinned; min ≥ 0 on every suite seed by the
    saturation only, the cut counted; ... the gas converges under D216's criterion or raises; ... f_m ≤ ĉ_m R/(X h)
    on every ring and seed".

    **S59's three legs, 60 pattern seeds × 2 texture seeds each** - the Milky Way template (barred, its arms
    pinned), ``ngc_4414`` (unbarred, flocculent, its pitch pinned) and ``ngc_4414`` with its pitch pin off. On
    every one of the 360: nothing raises (so every ring converged); the stellar and the gas ring means are 1;
    the stellar field is nowhere negative **with nothing but the cut** and the gas positive; no bit of a law
    moves with the layer; no field holds a NaN but the ruled ones; N v(σ_d) B² is the budget wherever a ring
    has an amplitude; and every harmonic of the forcing is under the bound.

    **As read on the third pass** (the record below; the first two builds' are in D219's record). **The realised
    power over the budget**, over the rings that have an amplitude, 16th / 50th / 84th percentile: 0.47 / 0.72 /
    1.18 on the Milky Way's leg, 0.45 / 0.52 / 0.73 on ``ngc_4414``'s and 0.42 / 0.54 / 0.91 on the drawn-pitch
    leg - the scatter the gate asks to be pinned. The expectation is of the count's worth of full ridges at the
    disc's pitch and at independent azimuths; a realised ring holds chains in their tapers, pieces of other
    pitches, ridges that stand evenly apart (births in the widest gap: less variance than independent ones) and
    the flanks of pieces whose locus does not cross it. Read, not mended: nothing is divided by a realised power.
    **Rings cut**: 4, 0 and 152 of 19 800, 15 960 and 15 960 with a budget - every one a ring whose count is
    far under 1, the only chains crossing it just begun, where the budget's amplitude grows as the root of one
    over the count and the saturation takes it (the second follow-up's item 3 and item 1 together; said plainly in
    the builder's hand-back). **Rings with a budget and no amplitude**: 5 764 (5 760 of them inside the bar, where
    no chain is born), 240 and 737 - a ring on which every crossing chain's weight is still nothing, or whose
    designed ridge would be no ridge (4, 120 and 98 rings: the count under 1 close to the centre). No galaxy
    without arms. **Joins of a galaxy**, least / median / most: 3 / 8 / 50, 0 / 1.5 / 3 and 0 / 3 / 19. No two
    chains cross on any of the 360, two measured pieces included; every birth stands at the middle of the widest
    gap, or - 0, 120 and 639 chains - on a ring no chain crossed. The rings kept between the grid's, summed over a
    leg's 120 galaxies: 1 660 at a gap's middle and 1 260 at a quarter, 1 817 and 1 032, 5 539 and 5 755. No ring
    took more than 9 Newton steps."""
    model = the_model(prod)
    c = constants(model)
    worst = {"stars": 0.0, "gas": 0.0, "expected": 0.0, "bound": 0.0}
    read = {leg: {"ratio": [], "cut": 0, "no_arm": 0, "no_chain": 0, "least": math.inf, "least_gas": math.inf, "most_gas": 0.0, "zeros": 0,
                  "budget": 0, "pitch": [], "steps": 0, "armless": 0, "wide": 0, "joins": [], "alone": 0, "pinned": 0, "kept": [0, 0], "ratio_max": []} for leg in LEGS}
    for leg in LEGS:
        got = read[leg]
        for pattern_seed in range(60):
            for texture_seed in (0, 1):
                given = leg_inputs(leg, pattern_seed=pattern_seed, texture_seed=texture_seed)
                o = run(model, given, only=PATTERN)
                F, R = o.fields, o.grid.R
                label = (leg, pattern_seed, texture_seed)
                stars, gas = np.asarray(F["pattern_density_contrast"]), np.asarray(F["gas_density_contrast"])
                worst["stars"] = max(worst["stars"], float(np.abs(stars.mean(axis=1) - 1.0).max()))
                worst["gas"] = max(worst["gas"], float(np.abs(gas.sum(axis=1) / gas.shape[1] - 1.0).max()))
                assert stars.min() >= 0.0 and gas.min() > 0.0, label
                got["least"], got["least_gas"], got["most_gas"] = min(got["least"], float(stars.min())), min(got["least_gas"], float(gas.min())), max(got["most_gas"], float(gas.max()))
                got["zeros"] += int((stars == 0.0).sum())
                nan = {n for n, v in F.items() if not isinstance(v, (str, tuple)) and np.isnan(np.asarray(v, dtype=float)).any()}
                assert nan == (set() if leg == "milky_way" else UNBARRED_NAN), (label, sorted(nan))
                off = run(model, given, only=LAWS, layer=False).fields
                assert all(np.asarray(off[k]).tobytes() == np.asarray(F[k]).tobytes() for k in LAWS), label
                budget, amplitude = np.asarray(F["arm_power_budget"]), np.asarray(F["arm_piece_amplitude"])
                cut, chains = np.asarray(F["arm_piece_saturation"]), np.asarray(F["arm_chain_count"])
                assert np.array_equal(budget, 0.5 * sum(np.asarray(F[k]) ** 2 for k in pt.AMPLITUDE_FIELDS)), label
                has, live = budget > 0.0, amplitude > 0.0
                # The budget in expectation, analytically: N v(sigma_d) B^2 - the count the law's, or a pinned
                # galaxy's chains - with v by this file's own sum of the piece's harmonics.
                pitch = float(F["pitch_angle"])
                sin_p = math.sin(math.radians(pitch))
                sp = compose.stellar_pattern(F, R)
                count, width = sp.count_at(R), sp.width_at(R)
                with np.errstate(divide="ignore"):
                    half_spacing = np.where(count > 0.0, math.pi * R * sin_p / np.where(count > 0.0, count, 1.0), np.inf)
                # The first follow-up's item 3 with the second's item 3: the width is the law's or half the crossing
                # spacing of the count - the sum of the crossing chains' taper weights - whichever is less.
                assert np.allclose(width, np.minimum(np.asarray(F["arm_piece_width"]), half_spacing), rtol=1e-12, atol=0.0), label
                assert np.all(count <= chains + 1e-12) and np.all(count >= 0.0), label
                sigma_d = (width / FWHM) / (R * sin_p)
                v = np.array([hand_variance(float(sd)) for sd in sigma_d])
                wide = has & (count > 0.0) & ~(sigma_d < math.sqrt(math.pi))  # the designed ridge no ridge on its ring
                assert np.array_equal(live, has & (count > 0.0) & ~wide), label
                worst["expected"] = max(worst["expected"], float(np.abs(count[live] * v[live] * amplitude[live] ** 2 / budget[live] - 1.0).max(initial=0.0)))
                got["wide"] += int(wide.sum())
                # The census's two rules: no two chains cross, and every birth stands in the widest gap.
                table = table_of(F)
                drawn_crossings, pinned_crossings = crossings(table)
                in_gap, alone, off = births_off_the_widest_gap(table, R, len(given.get("arm_pieces") or ()))
                assert drawn_crossings == 0 and off < 1e-9 and np.all(table[table[:, 6] == 1.0][:, 7] == 0.0), label
                got["joins"].append(int((table[:, 7] != 0.0).sum()))
                got["alone"], got["pinned"] = got["alone"] + alone, max(got["pinned"], pinned_crossings)
                a_bar = float(F["bar_half_length"])
                assert not math.isfinite(a_bar) or continued_inside_the_bar(table, a_bar) == 0, label
                if math.isfinite(a_bar):  # no chain is born inside the bar's half-length: a first piece inside it is pinned
                    first = (np.asarray(F["arm_piece_order"]) == 0.0) & (np.asarray(F["arm_piece_start_radius"]) < a_bar * (1.0 - 1e-12))
                    assert np.all(np.asarray(F["arm_piece_pinned"])[first] == 1.0), label
                assert np.all((cut > 0.0) & (cut <= 1.0)), label
                realised_over_budget = np.asarray(F["arm_ring_power"])[live] / budget[live]
                got["ratio"].extend(realised_over_budget.tolist())
                got["ratio_max"].append(float(realised_over_budget.max(initial=0.0)))
                # The fourth follow-up, B: on a ring any chain crosses the count is at least 1, so B - and each
                # chain's B times its weight, the weight at most 1 - is at most sqrt(budget / v).
                assert np.all(count[chains > 0.0] >= 1.0) and np.all(amplitude[live] <= np.sqrt(budget[live] / v[live]) * (1.0 + 1e-12)), label
                got["cut"] += int((cut < 1.0).sum())
                got["no_arm"] += int((has & ~live).sum())
                got["no_chain"] += int((has & (chains == 0.0)).sum())
                got["budget"] += int(has.sum())
                got["pitch"].append(pitch)
                # The forcing's bound, f_m <= c_m R/(X h) with c_m the pieces' summed |c_m(j)| - the composition's own,
                # not the composed field's |c_m|, which cancellation between pieces makes smaller (the fourth
                # follow-up, D): each chain's m-th harmonic is under its stellar amplitude times R/(X h) whatever its
                # pitch, so a ring's m-th forcing amplitude is under the chains' summed amplitudes times that.
                gp = compose.gas_pattern(F, R, c)
                stellar = np.zeros((R.size, gr.CELLS // 2))
                for part, _, ridges in sp.piece_profiles(R):
                    stellar[part] = (2.0 * np.abs(np.fft.rfft(ridges, axis=2))[:, :, 1:] / gr.CELLS).sum(axis=1)
                taper = pt.bar_terms(R, pitch, float(F["bar_half_length"]))[0]
                bound = stellar / (1.0 - taper)[:, None] * (R / (gp.swing_x() * gp.layer_height))[:, None]
                f = gp.forcing_amplitudes()
                on = stellar > 1e-12 * stellar.max()
                worst["bound"] = max(worst["bound"], float((f[on] / bound[on]).max(initial=0.0)))
                got["armless"] += int(not live.any())  # a disc wound so tightly that no ring holds a ridge
                kept = gp.mid_gap[1]
                got["kept"] = [got["kept"][0] + int((kept == 1).sum()), got["kept"][1] + int((kept == 2).sum())]
                d = gp.diagnostics
                got["steps"] = max(got["steps"], d.worst_steps if d is not None else 0)
    assert worst["stars"] < 1e-12 and worst["gas"] < 2e-13 and worst["expected"] < 1e-10 and worst["bound"] <= 1.0, worst
    record = {}
    for leg in LEGS:
        got = read[leg]
        ratio = np.array(got["ratio"])
        low, mid, high = (round(float(q), 3) for q in np.percentile(ratio, (16.0, 50.0, 84.0)))
        record[leg] = (got["budget"], ratio.size, (low, mid, high), got["cut"], got["no_arm"], got["no_chain"], got["zeros"],
                       round(min(got["pitch"]), 3), round(max(got["pitch"]), 3), got["steps"], got["armless"], got["wide"],
                       (min(got["joins"]), float(np.median(got["joins"])), max(got["joins"])), got["alone"], got["pinned"], tuple(got["kept"]),
                       tuple(round(float(q), 3) for q in (min(got["ratio_max"]), np.median(got["ratio_max"]), max(got["ratio_max"]))))
    # (rings with a budget, rings with an amplitude, the realised power over the budget: 16th / 50th / 84th
    #  percentile, rings cut, rings with a budget and no amplitude, rings with a budget and no chain, exact zeros
    #  of the stellar field, the lowest and highest pitch, the most Newton steps a ring took, the galaxies in which
    #  no ring holds an amplitude at all, the rings whose designed ridge is no ridge on its ring; the joins of a
    #  galaxy: least, median, most; the chains born on a ring no chain crossed; the most crossings of two measured
    #  pieces in a galaxy; the rings kept at a gap's middle and at a quarter, summed over the leg; the per-galaxy
    #  maximum of the realised over the budgeted ring power: least, median, most over the leg - the fourth
    #  follow-up, B, predicted it under 1.5 on both templates)
    assert record == EXPECTED_GATE, repr(record)
    least = {leg: (round(read[leg]["least"], 4), round(read[leg]["least_gas"], 4), round(read[leg]["most_gas"], 3)) for leg in LEGS}
    assert least == EXPECTED_LEAST, repr(least)


# (pieces, chains, pinned pieces, the drawn pieces that continue each of the six pinned chains)
EXPECTED_PINNED: tuple = (53, 14, 11, [0, 1, 3, 2, 4, 4], 4, 0)  # S60 fourth pass: was (52, 14, 11, [2, 1, 3, 2, 4, 4], 7, 0)
EXPECTED_GATE: dict = {'milky_way': (19800, 14036, (0.474, 0.72, 1.184), 4, 5764, 5760, 0, 1.0, 24.333, 9, 0, 4, (3, 8.0, 50), 0, 0, (1660, 1260)), 'ngc_4414': (15960, 15720, (0.452, 0.524, 0.728), 0, 240, 0, 0, 28.9, 28.9, 7, 0, 120, (0, 1.5, 3), 120, 0, (1817, 1032)), 'ngc_4414 drawn': (15960, 15223, (0.415, 0.541, 0.906), 152, 737, 0, 0, 1.0, 24.096, 9, 0, 98, (0, 3.0, 19), 639, 0, (5539, 5755))}
# (the least value of the stellar field, the least and the largest of the gas's, over each leg's 120 galaxies)
# (the least value of the stellar field, the least and the largest of the gas's, over each leg's 120 galaxies)
EXPECTED_LEAST: dict = {'milky_way': (0.0542, 0.1138, 6.673), 'ngc_4414': (0.0909, 0.0809, 3.317), 'ngc_4414 drawn': (0.0007, 0.0, 6.794)}


def test_the_layer_off_lays_no_piece_and_every_composed_field_is_its_neutral(prod):
    """D219 item 7: "Layer off: no arm placed, every field bit-identical to main." Here: no row in the table, every
    composed field its declared neutral, every law the layer-on run's to the bit, and the census's streams not
    drawn (the run is the same whatever the texture seed). The comparison of every field of both templates and
    the default run with ``main`` is the builder's, made from a second checkout, and is recorded in D219."""
    model = the_model(prod)
    decls = {d.name: d for d in (*pc.COMPOSED, gm.GAS_DENSITY_CONTRAST, gm.STAR_FORMATION_GAS_CONTRAST)}
    for template in ("milky_way", "ngc_4414"):
        on = template_run(prod, template)
        off = run(model, inputs_of(template), only=PATTERN, layer=False)
        other = run(model, inputs_of(template, texture_seed=99), only=PATTERN, layer=False)
        for name in pt.PIECE_FIELDS:
            assert np.asarray(off.fields[name]).shape == (0,) and np.asarray(on.fields[name]).size > 0
        for name, d in decls.items():
            assert np.all(np.asarray(off.fields[name]) == d.neutral), name
        for name in LAWS:
            assert np.asarray(off.fields[name]).tobytes() == np.asarray(on.fields[name]).tobytes(), name
        for name in PATTERN:
            a, b = off.fields[name], other.fields[name]
            assert a == b if isinstance(a, str) else np.asarray(a).tobytes() == np.asarray(b).tobytes(), name
        assert compose.stellar_pattern(off.fields, off.grid.R) is None and compose.gas_pattern(off.fields, off.grid.R, constants(model)) is None


# --- the gas between rings ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("template", ("milky_way", "ngc_4414"))
def test_the_gas_carried_between_rings_and_the_rings_solved_between_the_grid_s(prod, template):
    """D219 item 6 as the gate's first follow-up words it: "where the mid-gap misplaced weight passes 1 %, solve a
    ring at the mid-gap and carry from it, recursing at most twice (quartering), then record what remains; the check
    is that solve." Held here: the model's own check is every gap's middle against the grid's rings alone; a ring
    is kept exactly where that passed 1 %; each half of such a gap is checked the same way against the store that
    now holds the middle, and its quarter kept where it passed; nothing deeper is kept; a kept ring is the law
    solved at its radius (``GasPattern.solve_at``), its inputs the radius' own.

    **What remains, recorded** (S59's statistic at the middle of every gap of the finished store, against a direct
    solve there). The carried profile misplaces under a fifth of a percent in the median gap, and **still over
    1 % in a few**: each holds a radius at which the stellar field itself changes abruptly - a join, where a chain
    ends at full height and the ring's count steps by one; the inner free end of a lone chain, where the count
    tends to nothing and the amplitude to its cut; a nearly circular piece, whose whole length crosses a few tens
    of parsecs of radius. Halving a gap twice narrows such a place and cannot remove it. Not mended: the record.

    The carried profile's mean round the ring is 1 by its own exact normaliser at every radius; the pattern's
    sector means are the point function's integrals; at a solved ring's own radius nothing is carried."""
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    sp, gp, _ = patterns(prod, o)
    kept_at, kept_level = gp.mid_gap
    store = gp._rings()
    radii, level, checked = store["radii"], store["level"], store["checked"]
    cells = gr.cell_centres(gr.CELLS)
    assert store["complete"] is True and np.array_equal(radii[level == 0], R) and level.max() <= gm.MID_GAP_DEPTH == 2 and gm.MISPLACED_LIMIT == 0.01
    asked, miss = checked[0]
    assert np.array_equal(asked, 0.5 * (R[:-1] + R[1:])) and np.array_equal(radii[level == 1], asked[miss > 0.01])
    worst_first = float(miss.max())
    if len(checked) > 1:
        halves, miss_halves = checked[1]
        middles = asked[miss > 0.01]
        assert halves.size == 2 * middles.size and np.array_equal(radii[level == 2], halves[miss_halves > 0.01])
        # ... each half's middle is a quarter of a kept gap.
        step = R[1] - R[0]
        assert np.allclose(np.sort(np.concatenate([middles - 0.25 * step, middles + 0.25 * step])), halves, rtol=0.0, atol=1e-9)
    else:
        assert not (level == 2).any()
    assert np.array_equal(np.sort(kept_at), radii[level > 0]) and np.abs(store["profiles"][level > 0] - gp.solve_at(radii[level > 0])).max(initial=0.0) < 1e-12
    # The model's check, re-made here for the first level: the grid's rings alone, carried to each gap's middle.
    gm.forget_solutions()  # (or the pattern below would be handed this one's finished store)
    bare = gm.GasPattern.from_fields(F, R, constants(the_model(prod)), sp)
    lower = np.arange(R.size - 1)
    carried = 0.5 * (bare.carried(lower, asked, np.broadcast_to(cells, (asked.size, cells.size)))
                     + bare.carried(lower + 1, asked, np.broadcast_to(cells, (asked.size, cells.size))))
    assert bare._rings()["complete"] is False  # (read on the grid's rings' own indices: the mid-gap rings were not looked for)
    assert np.abs(misplaced(carried, gp.solve_at(asked)) - miss).max() < 1e-12
    # What remains, at the middle of every gap of the finished store.
    mids = 0.5 * (radii[:-1] + radii[1:])
    left = misplaced(gp.response_at(mids[:, None], cells[None, :]), gp.solve_at(mids))
    now = np.asarray(F["sfr_surface_density"])  # the present-day star formation rate per ring
    forming = np.interp(mids, R, now) > 1e-6 * now.max()
    over = np.flatnonzero((left > 0.01) & forming)
    record = (int((level == 1).sum()), int((level == 2).sum()), round(100.0 * worst_first, 2), int(forming.sum()),
              [round(float(mids[i]), 3) for i in over], round(100.0 * float(left[forming].max()), 2),
              round(100.0 * float(np.median(left[forming & (left > 0.0)])), 3))
    # (rings kept at a gap's middle, at a quarter; the worst misplaced weight % of the grid's rings alone; the
    #  star-forming gaps of the finished store; those still over 1 %, by radius; the worst %; the median % over the
    #  gaps that carry an arm)
    assert record == EXPECTED_GAPS.get(template), repr(record)
    # The carried profile is a redistribution: sectors that tile the ring average to 1, at any radius.
    edges = np.linspace(0.0, 2.0 * math.pi, 65)
    means = np.array([gp.sector_means(float(r), edges) for r in mids[::9]])
    assert np.abs(means.mean(axis=1) - 1.0).max() < 5e-14 and means.min() > 0.0
    # ... and the sector means are the point function's integrals (a midpoint rule of 400 to a sector).
    r = float(mids[forming][int(np.argmax(left[forming]))])
    samples = (edges[:-1, None] + (edges[1] - edges[0]) * ((np.arange(400) + 0.5) / 400.0)[None, :])
    assert np.abs(gp.sector_means(r, edges) - gp.contrast_at(r, samples).mean(axis=1)).max() < 2e-6
    # At a solved ring's own radius nothing is carried: the point function is the ring's interpolant, to the bit.
    i = int(np.argmin(np.abs(R - 8.0)))
    phi = np.linspace(-3.0, 9.0, 501)
    assert np.array_equal(gp.response_at(R[i], phi), gr.interpolate(gp.profiles[i], phi))
    k = int(np.flatnonzero(radii == R[i])[0])
    assert np.array_equal(gp.carried(np.array([k]), R[i : i + 1], phi[None, :])[0], gr.interpolate(gp.profiles[i], phi))
    # The published field is the grid's rings' own, the same bits with the mid-gap rings looked for or not.
    edges_phi = o.grid["phi"].edges
    assert np.array_equal(gp.cell_means(R, edges_phi), bare.cell_means(R, edges_phi)) and np.array_equal(gp.cell_means(R, edges_phi), np.asarray(F["gas_density_contrast"]))


EXPECTED_GAPS: dict = {"milky_way": (12, 11, 21.35, 345, [3.572, 3.591, 5.784, 6.028, 7.116, 8.184, 10.941], 65.62, 0.13), "ngc_4414": (18, 16, 13.2, 282, [0.141, 0.159, 0.197, 0.272, 0.778, 0.816, 3.103, 3.122, 3.141, 3.159, 3.178], 5.09, 0.19)}


# --- the gate's predictions, read as measured ----------------------------------------------------------------------


def tenth_over_half(s: np.ndarray) -> float:
    """The mean of the highest tenth of a ring's cells over the mean of its lower half."""
    ranked = np.sort(s)
    return float(ranked[-(ranked.size // 10):].mean() / ranked[: ranked.size // 2].mean())


def measured(prod, template: str) -> dict:
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    sp, gp, _ = patterns(prod, o)
    i0, i8 = int(np.argmin(np.abs(R - 8.15))), int(np.argmin(np.abs(R - 8.0)))
    band = (R >= 6.0) & (R <= 10.0)
    round_ring = np.linspace(0.0, 2.0 * math.pi, 7200, endpoint=False)
    stars = sp.contrast_at(R[i0], round_ring)
    ratio = gp.arm_ratio(gas_check.GAS_ARM_MASK_WIDTH)
    s = gp.profiles
    f = gp.forcing_amplitudes()
    inner = (R < 3.0) & gp.carries
    p = sp.pieces
    pinned_crossing = len({int(p.chain[k]) for k in range(p.count) if p.pinned[k] and p.x_start[k] <= math.log(R[i0]) < p.x_end[k]})
    mid = (R > 5.0) & (R < 13.0)
    change = np.abs(np.diff(sp.ring_profile(R[mid]), axis=0)).mean(axis=1)  # mean |c(k+1) − c(k)| round the ring
    return {
        "chains at R0": int(F["arm_chain_count"][i0]), "pinned chains at R0": pinned_crossing, "n at R0": round(float(F["arm_design_count"][i0]), 2),
        "count at R0": round(float(sp.count_at(R[i0:i0 + 1])[0]), 3),
        "FWHM at R0": round(float(sp.width_at(R[i0:i0 + 1])[0]), 3), "spacing at R0": round(float(sp.spacing_at(R[i0:i0 + 1])[0]), 2), "B at R0": round(float(F["arm_piece_amplitude"][i0]), 3),
        "crest over trough at R0": round(float(stars.max() / stars.min()), 2),
        # (the forcing's harmonics' summed amplitudes: over m = 2..6 - the sum as `main` defined it, which the gate's 0.6-0.9 was a
        #  prediction for and which is judged - over the first 128, the number the first two passes read, and
        #  over every harmonic the solver's cells hold - a window cut square at a join has a long tail)
        "sum f at 8, m = 2..6": round(float(f[i8, 1:6].sum()), 3), "sum f at 8, first 128": round(float(f[i8, :128].sum()), 3), "sum f at 8, every harmonic": round(float(f[i8].sum()), 3),
        "gas min at 8": round(float(s[i8].min()), 3), "top tenth over lower half at 8": round(tenth_over_half(s[i8]), 2),
        "ratio of means 6-10": round(float(np.nanmedian(ratio[band])), 3), "rings under 1.37": int((ratio[band] < 1.37).sum()),
        # (None where no ring inside 3 kpc is forced: a barred disc's bar, inside which no chain is born)
        "inner gas min": round(float(s[inner].min()), 3) if inner.any() else None,
        "inner ratio": round(float(np.nanmedian(ratio[inner])), 2) if inner.any() else None,
        "largest ring-to-ring change 5-13": (round(float(change.max()), 3), round(float(R[mid][int(np.argmax(change))]), 3)),
        "pieces": p.count, "chains": len(np.unique(p.chain)), "joins": p.joins,
    }


def test_the_gate_s_predictions_as_measured(prod):
    """D219, the predictions of the gate's second follow-up for the third pass, each read on the built model before
    anything else was judged and recorded in ``EXPECTED_HELD`` held or not held. **Nothing was changed to make one
    hold; a failed prediction is recorded, never mended.** (The first build's and the second pass's predictions and
    how they read are in D219's record.)

    *Milky Way template*: "chains at R₀ 5 (the drawn chain born at the bar's end meets a pinned chain inside 8 kpc
    under D2), or 6"; "the m-split over 6–10 kpc peaks at m = 5 or 6 with m = 2 under 0.5"; "crest over trough
    2.5–3"; "Σf at 8 kpc 0.6–0.9, the gas minimum 0.65–0.75, the PHANGS ratio 1.4–1.6"; "the largest ring-to-ring
    change of the stellar profile under 0.05"; "joins 2–4 on the default seeds"; "the maser and young-star checks
    keep their 1st-percentile power". *``ngc_4414``*: "D2 shortens many of its 36 pieces, ratio 1.2–1.3, still a
    miss". The numbers are ``EXPECTED_PREDICTIONS``, ``EXPECTED_SPLIT`` and ``EXPECTED_MASERS``."""
    got = {template: measured(prod, template) for template in ("milky_way", "ngc_4414")}
    assert got == EXPECTED_PREDICTIONS, repr(got)
    assert held_of(got) == EXPECTED_HELD, repr(held_of(got))


EXPECTED_PREDICTIONS: dict = {'milky_way': {'chains at R0': 6, 'pinned chains at R0': 2, 'n at R0': 4.72, 'count at R0': 6.0, 'FWHM at R0': 0.997, 'spacing at R0': 1.99, 'B at R0': 0.493, 'crest over trough at R0': 2.51, 'sum f at 8': 2.066, 'sum f at 8, every harmonic': 3.268, 'gas min at 8': 0.654, 'top tenth over lower half at 8': 1.79, 'ratio of means 6-10': 1.482, 'rings under 1.37': 0, 'inner gas min': None, 'inner ratio': None, 'largest ring-to-ring change 5-13': (0.074, 7.312), 'pieces': 52, 'chains': 14, 'joins': 7}, 'ngc_4414': {'chains at R0': 6, 'pinned chains at R0': 0, 'n at R0': 5.12, 'count at R0': 5.593, 'FWHM at R0': 1.825, 'spacing at R0': 4.42, 'B at R0': 0.478, 'crest over trough at R0': 2.01, 'sum f at 8': 1.446, 'sum f at 8, every harmonic': 2.081, 'gas min at 8': 0.712, 'top tenth over lower half at 8': 1.54, 'ratio of means 6-10': 1.299, 'rings under 1.37': 39, 'inner gas min': 0.137, 'inner ratio': 1.5, 'largest ring-to-ring change 5-13': (0.038, 6.487), 'pieces': 37, 'chains': 37, 'joins': 2}}
# The second follow-up's predictions for the third pass, read before they were judged: held or not held, as measured.
EXPECTED_HELD: dict = {'chains at R0 5 or 6': True, 'm-split over 6-10 kpc peaks at m = 5 or 6': False, 'm = 2 under 0.5': False, 'crest over trough 2.5-3': True, 'sum f at 8 kpc 0.6-0.9': False, 'gas minimum 0.65-0.75': True, 'PHANGS ratio 1.4-1.6': True, 'largest ring-to-ring change under 0.05': False, 'joins 2-4': False, "the masers' check keeps its 1st-percentile power": True, "the young stars' check keeps its 1st-percentile power": True, 'ngc_4414: D2 shortens many of its pieces': False, 'ngc_4414 ratio 1.2-1.3': True, 'ngc_4414 still a miss': True}


def held_of(got: dict) -> dict:
    """The second follow-up's predictions against what was measured: True where one held."""
    mw, n4 = got["milky_way"], got["ngc_4414"]
    split = EXPECTED_SPLIT["milky_way"][0]
    masers = EXPECTED_MASERS
    return {
        "chains at R0 5 or 6": mw["chains at R0"] in (5, 6),
        "m-split over 6-10 kpc peaks at m = 5 or 6": pt.ARM_MODES[int(np.argmax(split))] in (5, 6),
        "m = 2 under 0.5": split[0] < 0.5,
        "crest over trough 2.5-3": 2.5 <= mw["crest over trough at R0"] <= 3.0,
        "sum f at 8 kpc 0.6-0.9": 0.6 <= mw["sum f at 8, m = 2..6"] <= 0.9,  # judged on m = 2..6, the sum as main defined it (the reviewer of the third pass)
        "gas minimum 0.65-0.75": 0.65 <= mw["gas min at 8"] <= 0.75,
        "PHANGS ratio 1.4-1.6": 1.4 <= mw["ratio of means 6-10"] <= 1.6,
        "largest ring-to-ring change under 0.05": mw["largest ring-to-ring change 5-13"][0] < 0.05,
        "joins 2-4": 2 <= mw["joins"] <= 4,
        "the masers' check keeps its 1st-percentile power": masers["gas"][5] <= 1,
        "the young stars' check keeps its 1st-percentile power": masers["young stars"][5] <= 1,
        "ngc_4414: D2 shortens many of its pieces": n4["joins"] >= n4["pieces"] // 3,
        "ngc_4414 ratio 1.2-1.3": 1.2 <= n4["ratio of means 6-10"] <= 1.3,
        "ngc_4414 still a miss": n4["ratio of means 6-10"] < 1.37,
    }


def test_the_fourth_follow_up_s_predictions_as_measured(prod):
    """The gate's fourth follow-up, B, its predictions read before judged: "that maximum [of the realised over the
    budgeted ring power per galaxy] under 1.5 on both templates; the end-of-bar excess on the bare default galaxy
    at most the arms' own at 8 kpc; ``ngc_4414``'s B at 0.11 kpc under sqrt(budget/v) there". Read on the templates
    at their default seeds and on the bare default galaxy; the third item holds by construction since B and is
    read as a number. Recorded held or not held in ``EXPECTED_FOURTH_HELD``; nothing is changed to make one hold."""
    got = {}
    for name in ("milky_way", "ngc_4414", "default"):
        o = template_run(prod, name) if name != "default" else run(the_model(prod), None, only=PATTERN)
        F, R = o.fields, o.grid.R
        sp = compose.stellar_pattern(F, R)
        budget, power, amplitude = np.asarray(F["arm_power_budget"]), np.asarray(F["arm_ring_power"]), np.asarray(F["arm_piece_amplitude"])
        live = amplitude > 0.0
        entry = {"max realised over budget": (round(float((power[live] / budget[live]).max()), 3), round(float(R[live][int(np.argmax(power[live] / budget[live]))]), 3))}
        ring = np.linspace(0.0, 2.0 * math.pi, 7200, endpoint=False)
        if name == "default":
            a = float(F["bar_half_length"])
            past = R[(R >= a) & live][:3]
            entry["arms' excess past the bar's end"] = round(float(max(np.abs(sp.arms_at(np.array([r]), ring)).max() for r in past)), 3)
            entry["arms' excess at 8 kpc"] = round(float(np.abs(sp.arms_at(R[int(np.argmin(np.abs(R - 8.0))) : int(np.argmin(np.abs(R - 8.0))) + 1], ring)).max()), 3)
        if name == "ngc_4414":
            i = int(np.argmin(np.abs(R - 0.11)))
            sigma_d = float(sp.design_dispersion_at(R[i : i + 1])[0])
            entry["B at 0.11 kpc"] = round(float(amplitude[i]), 3)
            entry["sqrt(budget / v) at 0.11 kpc"] = round(math.sqrt(budget[i] / hand_variance(sigma_d)), 3) if budget[i] > 0.0 and sigma_d < math.sqrt(math.pi) else None
            entry["count at 0.11 kpc"] = round(float(sp.count_at(R[i : i + 1])[0]), 3)
        got[name] = entry
    assert got == EXPECTED_FOURTH, repr(got)
    held = {
        "max realised over budget under 1.5 on both templates": got["milky_way"]["max realised over budget"][0] < 1.5 and got["ngc_4414"]["max realised over budget"][0] < 1.5,
        "end-of-bar excess at most the arms' own at 8 kpc": got["default"]["arms' excess past the bar's end"] <= got["default"]["arms' excess at 8 kpc"],
        "ngc_4414's B at 0.11 kpc under sqrt(budget/v)": got["ngc_4414"]["sqrt(budget / v) at 0.11 kpc"] is None or got["ngc_4414"]["B at 0.11 kpc"] <= got["ngc_4414"]["sqrt(budget / v) at 0.11 kpc"],
    }
    assert held == EXPECTED_FOURTH_HELD, repr(held)


EXPECTED_FOURTH: dict = {"milky_way": {"max realised over budget": (2.343, 4.463)}, "ngc_4414": {"max realised over budget": (2.935, 3.263), "B at 0.11 kpc": 0.782, "sqrt(budget / v) at 0.11 kpc": 0.782, "count at 0.11 kpc": 1.0}, "default": {"max realised over budget": (0.759, 5.213), "arms' excess past the bar's end": 0.329, "arms' excess at 8 kpc": 0.312}}
EXPECTED_FOURTH_HELD: dict = {"max realised over budget under 1.5 on both templates": False, "end-of-bar excess at most the arms' own at 8 kpc": False, "ngc_4414's B at 0.11 kpc under sqrt(budget/v)": True}


def test_disclosed_check_the_split_of_a_ring_s_power_by_arm_number(prod):
    """D219 item 4: "The split by m survives as a disclosed check: the composed field's realised Fourier power by m
    against the law's A_m², published, read, not tuned." Per template, summed over the rings of 6-10 kpc: the
    square of the composed arm field's m-fold amplitude beside the square of the law's amplitude, m = 2 … 6; and
    the realised ring variance over the budget.

    **As read on the third pass: the pieces still do not split a ring's power as the law does, and less badly.** On
    the Milky Way template the two-fold power over 6-10 kpc is 1.29 - the largest of the five still, about 140
    times the law's 0.009, and under half the second pass's 2.82 (births in the widest gap took the rest) - and
    the five- and six-fold 0.35 and 0.46 against the law's 2.44 and 2.44. On ``ngc_4414`` the five are nearly
    equal, 0.28 to 0.70, where the law rises from 0.04 to 2.41. The realised ring variance is 0.875 and 0.805
    of the budget there. Recorded; nothing is tuned to it. The published powers are the ring's profile's on the
    solver's cells ("its ring mean and variance by the same quadrature"), held here to this file's transform."""
    record = {}
    for template in ("milky_way", "ngc_4414"):
        o = template_run(prod, template)
        F, R = o.fields, o.grid.R
        sp, _, _ = patterns(prod, o)
        band = (R >= 6.0) & (R <= 10.0)
        realised = [float(np.asarray(F[f"arm_mode_power_{m}"])[band].sum()) for m in pt.ARM_MODES]
        law = [float((np.asarray(F[pt.amplitude_field(m)])[band] ** 2).sum()) for m in pt.ARM_MODES]
        budget, power = np.asarray(F["arm_power_budget"]), np.asarray(F["arm_ring_power"])
        record[template] = ([round(v, 3) for v in realised], [round(v, 3) for v in law], round(float(power[band].sum() / budget[band].sum()), 3))
        # The published powers are the ring's profile's on the solver's cells: this file's transform of the point function there.
        i = int(np.argmin(np.abs(R - 8.0)))
        profile = sp.arms_at(R[i], gr.cell_centres(gr.CELLS))
        spectrum = 2.0 * np.fft.rfft(profile) / gr.CELLS
        for m in pt.ARM_MODES:
            assert abs(spectrum[m]) ** 2 == pytest.approx(float(F[f"arm_mode_power_{m}"][i]), rel=1e-12)
        assert float(F["arm_ring_power"][i]) == pytest.approx(float(((profile - profile.mean()) ** 2).mean()), rel=1e-10)
    assert record == EXPECTED_SPLIT, repr(record)


# (the realised m-fold power summed over 6-10 kpc, m = 2 ... 6; the law's; the realised ring variance over the budget there)
EXPECTED_SPLIT: dict = {"milky_way": ([1.293, 0.599, 0.749, 0.348, 0.464], [0.009, 1.064, 2.126, 2.44, 2.437], 0.875), "ngc_4414": ([0.275, 0.677, 0.693, 0.673, 0.698], [0.039, 0.619, 1.165, 1.757, 2.408], 0.805)}


# --- the pinned loci, and the masers against the gas and the young stars ---------------------------------------------


def test_the_composed_stellar_crest_against_the_pinned_loci(prod):
    """D219 item 8: "the composed stellar crest lies within 0.1 width of each pinned locus over its β range — by
    construction, asserted, not a test of the model". **What holds by construction is asserted in the test of the
    pinned pieces: each pinned piece's own ridge is the fitted locus, to 1e-12 kpc. The sentence as worded does
    not hold, and is measured here** (the first follow-up's item 5: "read and disclosed"): the crest of the
    *composed* field - a local maximum along a radius of the sum of every piece - against each locus, in units
    of the width law's FWHM at the locus' radius. On the third pass: within a tenth of a width on 95 % of the
    points of Sagittarius-Carina, every point of the Local arm, 83 % of Perseus and 76 % of the Outer arm (the
    median distance 0.01-0.05 width), and on 22 % and 12 % of Norma and Scutum-Centaurus (medians 0.26 and
    0.16): those two lie inside 5.2 kpc, in the bar's reach, where the arms' amplitude is tapered away and few
    chains set it, and Norma's first stretch is the nearly circular piece of −1 degree. Recorded, not mended."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    sp, _, _ = patterns(prod, o)
    sun, sense = float(F["sun_azimuth"]), pt.rotation_sense(float(F["pitch_angle"]))
    r = np.arange(0.5, 20.0, 0.005)
    record = {}
    for row in reid2019.TABLE2:
        if row[0] not in reid2019.PINNED:
            continue
        beta, radius = reid2019.locus(row)
        v = sp.contrast_at(r[:, None], (sun + sense * np.radians(beta))[None, :])
        peak = (v[1:-1] > v[:-2]) & (v[1:-1] >= v[2:])
        near = np.array([np.abs(r[1:-1][peak[:, j]] - radius[j]).min() if peak[:, j].any() else np.inf for j in range(beta.size)])
        widths = near / np.interp(radius, R, np.asarray(F["arm_piece_width"]))
        record[row[0]] = (round(float(np.median(widths)), 2), round(float((widths <= 0.1).mean()), 2))
    # (the median distance from the locus to the nearest composed crest, in the model's arm widths; the share of the
    #  locus within a tenth of a width)
    assert record == EXPECTED_CREST, repr(record)


EXPECTED_CREST: dict = {'Norma': (0.26, 0.22), 'Sct-Cen': (0.16, 0.12), 'Sgr-Car': (0.01, 0.95), 'Local': (0.01, 1.0), 'Perseus': (0.01, 0.83), 'Outer': (0.05, 0.76)}


def test_disclosed_check_the_masers_loci_against_the_gas_s_and_the_young_stars_crests(prod):
    """D219 item 8: "the model is tested by the gas and young stars' crest against the maser loci within the masers'
    σ (0.34 kpc at R₀), a disclosed check with its null stated". **A disclosed check, not a spec row** (I3). The
    statistic is ``tests/reid2019.py``'s: for each of the five arms, over its β range, the radial distance from
    the fitted locus to the nearest crest of the field along the point's azimuth, in the masers' own σ(R) =
    336 + 36 (R − 8.15) pc; the median of the five arms' medians. Read on the gas's contrast and on the young
    stars' placement law (the reader's point function), on the Milky Way template at its default seeds - and
    against **the null**: the same field with the Sun placed at each of 360 azimuths.

    **As read on the third pass** (the record): the gas's crests stand a median of 0.08 maser σ from the loci
    (Norma-Outer 0.65, Scutum-Centaurus 0.61, Sagittarius-Carina 0.02, Perseus 0.08, the Local arm 0.07; all
    points pooled 0.13) and the young stars' 0.11 (0.50, 0.23, 0.03, 0.09, 0.11; pooled 0.12). **Against the
    null** - the Sun at each of 360 azimuths - the gas's statistic has a median of 0.57 σ (5-95 %: 0.35-1.05)
    and the young stars' 0.50 (0.31-0.82): **no rotation of the Sun reads as low as the model's own** (the as-built
    values are under the 1st percentile of their nulls; the second pass read 0.22 σ at the 1st percentile, the
    first 0.39 at the 14th). The check tells the pinned Milky Way from a rotated one; that is all it tells -
    the pinned loci are put in, and the gas and the young stars follow them by construction."""
    o = template_run(prod, "milky_way")
    F, R = o.fields, o.grid.R
    _, gp, c = patterns(prod, o)
    reader = systems.young_reader(F, R, c)
    sun, sense = float(F["sun_azimuth"]), pt.rotation_sense(float(F["pitch_angle"]))
    fields = {"gas": lambda r, phi: gp.contrast_at(r[:, None], phi[None, :]), "young stars": lambda r, phi: reader.at(r, phi)}
    record = {}
    for name, contrast in fields.items():
        null, per_arm, pooled = reid2019.rotation_null(contrast, sun, sense)
        built = float(null[0])
        record[name] = (round(built, 2), {arm: round(v, 2) for arm, v in per_arm.items()}, round(pooled, 2), round(float(np.median(null)), 2),
                        tuple(round(float(q), 2) for q in np.percentile(null, (5.0, 95.0))), round(100.0 * float((null <= built).mean())),
                        round(100.0 * float((null <= 1.0).mean())))
    # (as built: the median over the five arms in maser sigmas; each arm's; all points pooled; the null's median;
    #  its 5th and 95th percentiles; the percentile of the as-built value in its null; the share of rotations at
    #  or under one sigma)
    assert record == EXPECTED_MASERS, repr(record)


EXPECTED_MASERS: dict = {'gas': (0.08, {'Norma-Outer': 0.65, 'Sct-Cen': 0.61, 'Sgr-Car': 0.02, 'Perseus': 0.08, 'Local': 0.07}, 0.13, 0.57, (0.35, 1.05), 0, 92), 'young stars': (0.11, {'Norma-Outer': 0.5, 'Sct-Cen': 0.23, 'Sgr-Car': 0.03, 'Perseus': 0.09, 'Local': 0.11}, 0.12, 0.5, (0.31, 0.82), 0, 98)}


# --- the young stars' reader on the new pattern (ported from S59's file) ---------------------------------------------


def test_the_young_stars_reader_is_the_law_of_the_gas_s_point_function(prod):
    """S59's ruling on the reader (D218) as the second follow-up to D219's gate words it (item 3): "the young
    stars' reader applies each bracketing grid ring's law to the gas pattern's point function at the point,
    M(r,φ) = (1 − a) Ψ_i(g(r,φ))/⟨Ψ_i(g(r,·))⟩ + a Ψ_j(g(r,φ))/⟨Ψ_j(g(r,·))⟩, the point function using the mid-gap
    rings of item 6; nothing ring-only is interpolated" - each ring's term a redistribution at every radius. What S60 changes is how a ring's profile
    reaches a point at another radius - carried along the pieces' loci, not turned by a common winding - and the
    reader follows by construction (D219 item 7). Held here: at a grid radius the reader is that ring's law of
    the pattern's own contrast, the ratio constant round the ring; between two rings each ring's term averages
    to 1 round the ring (the normaliser's quadrature) and so does the reader; its sector means are the
    function's integrals; and the published table, at every cell, is the same law at the cell's mean contrast."""
    for template in ("milky_way", "ngc_4414"):
        o = template_run(prod, template)
        F, R = o.fields, o.grid.R
        _, gp, c = patterns(prod, o)
        reader = systems.young_reader(F, R, c)
        phi = (np.arange(2880) + 0.5) * (2.0 * math.pi / 2880)
        # At a grid radius: the law of the pattern's own star-formation contrast there, over its mean.
        for radius in (2.0, 5.0, 8.0, 11.0):
            i = int(np.argmin(np.abs(R - radius)))
            contrast = gp.star_formation_contrast_at(R[i], phi)
            law = reader._law(np.array([i]), contrast[None, :])[0]
            got = reader.at(R[i : i + 1], phi)[0]
            if law.mean() > 0.0:
                assert np.abs(got * law.mean() - law).max() < 2e-3 * law.mean() and abs(got.mean() - 1.0) < 5e-4, (template, radius)
        # Between two rings: a redistribution, and positive.
        mids = 0.5 * (R[:-1] + R[1:])[10:160:7]
        between = reader.at(mids, phi)
        assert np.abs(between.mean(axis=1) - 1.0).max() < 2e-3 and between.min() >= 0.0, template
        # The normaliser's quadrature: two steps to a cell against 64, at radii between the rings.
        low, high, _ = pt.ring_bracket(R, mids[::5])
        coarse, finer = reader._means(mids[::5], low, high), reader._means(mids[::5], low, high, per_cell=64)
        assert max(float(np.abs(a / b - 1.0).max()) for a, b in zip(coarse, finer)) < 2e-4, template
        # Its sector means are its integrals: against 400 midpoints to a sector.
        edges = np.linspace(0.0, 2.0 * math.pi, 65)
        samples = (edges[:-1, None] + (edges[1] - edges[0]) * ((np.arange(400) + 0.5) / 400.0)[None, :]).ravel()
        radii = mids[::5]
        want = reader.at(radii, samples).reshape(radii.size, 64, 400).mean(axis=2)
        assert np.abs(reader.sector_means_at(radii, edges) - want).max() < READER_SECTOR_BOUND[template], template
        # The published table is the law at the cell's mean contrast, over the ring's mean (D218's third follow-up).
        table, cellwise = np.asarray(F["sfr_modulation"]), np.asarray(F["star_formation_gas_contrast"])
        rings = np.arange(5, R.size, 31)
        law = reader._law(rings, cellwise[rings])
        mean = law.mean(axis=1, keepdims=True)
        assert np.array_equal(np.where(mean > 0.0, law / np.where(mean > 0.0, mean, 1.0), 1.0), table[rings]), template


READER_SECTOR_BOUND = {"milky_way": 1e-3, "ngc_4414": 1e-3}


# --- the pins --------------------------------------------------------------------------------------------------------


def test_a_pin_is_a_class_a_named_class_a_number_or_a_table(prod):
    """D217's mechanism (a pin reaches a run by its template's name alone), D218's (a pin with a unit is a measured
    number, held to the range of what it replaces), and S60's two shapes (D219 items 3 and 8): **a named class** -
    one of a closed list, a text - and **a table** - rows of the source's own columns. Each is validated where a
    template is built and where a run resolves its inputs, refused as a request's own parameter, and served by
    ``/api/templates`` in the shape ``service.pin_json`` documents."""
    model = the_model(prod)
    assert [INPUTS[n].shape for n in ("bar_present", "arm_class", "pitch_angle", "sun_bar_angle", "arm_pieces")] == ["class", "named", "number", "number", "table"]
    only = ("arm_class", "arm_piece_chain", "pitch_angle", "sun_azimuth")
    # The class of three.
    assert run(model, None, SMALL, only=only).fields["arm_class"] == "grand_design"
    assert run(model, {"bar_present": False}, SMALL, only=only).fields["arm_class"] == "multi_armed"
    for name in ARM_CLASSES:
        assert run(model, {"arm_class": name}, SMALL, only=only).fields["arm_class"] == name
    for bad in (True, 2.0, "grand design", "", ("flocculent",)):
        with pytest.raises(RunError, match="is one of"):
            run(model, {"arm_class": bad}, SMALL, only=only)
    # The table: rows of the declared columns, each held to what the source's form allows.
    good = ("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4)
    pins = {"bar_present": True, "sun_bar_angle": 30.0}
    assert int(run(model, {**pins, "arm_pieces": (good,)}, SMALL, only=only).fields["arm_piece_chain"].size) > 0
    assert INPUTS["arm_pieces"].pinned([list(good)]) == (good,)  # a list of lists is taken as rows
    for bad, why in (
        ((), "a table"), ("Local", "a table"), ((good[:-1],), "a row holds"), (((1.0, *good[1:]),), "is a name"),
        ((("Local", "x", *good[2:]),), "finite number in deg"), (((*good[:4], float("nan"), *good[5:]),), "finite number in kpc"),
        ((good, good), "named twice"), ((("Local", 34.0, -8.0, 9.0, 8.26, 11.4, 11.4),), "run from beta_from"),
        ((("Local", -8.0, 34.0, 40.0, 8.26, 11.4, 11.4),), "kink lies inside"), ((("Local", -8.0, 34.0, 9.0, 0.0, 11.4, 11.4),), "radius is positive"),
        ((("Local", -8.0, 34.0, 9.0, 8.26, 0.0, 11.4),), "not zero and under 90"), ((("Local", -8.0, 34.0, 9.0, 8.26, 11.4, 90.0),), "not zero and under 90"),
        ((("Local", -400.0, 34.0, 9.0, 8.26, 11.4, 11.4),), "within a turn"),
    ):
        with pytest.raises(RunError, match=why):
            run(model, {**pins, "arm_pieces": bad}, SMALL, only=only)
    # A template is held to the same, when it is built; and pinned arms need the Sun.
    mw = templates.TEMPLATES["milky_way"]
    import dataclasses
    with pytest.raises(templates.TemplateError, match="is one of"):
        dataclasses.replace(mw, pins=(*mw.pins, templates.Pin("arm_class", "spiral", "[inferred]"))).validate()
    with pytest.raises(templates.TemplateError, match="named twice"):
        dataclasses.replace(mw, pins=tuple(p if p.name != "arm_pieces" else templates.Pin("arm_pieces", (good, good), "[inferred]") for p in mw.pins)).validate()
    with pytest.raises(templates.TemplateError, match="placed by the Sun's azimuth"):
        dataclasses.replace(mw, pins=tuple(p for p in mw.pins if p.name != "sun_bar_angle")).validate()
    with pytest.raises(templates.TemplateError, match="a class, True or False"):
        dataclasses.replace(mw, pins=(templates.Pin("bar_present", "yes", "[inferred]"),)).validate()
    with pytest.raises(RegistryError, match="only a pin names classes or columns"):
        Input("x", "x", "control", "x", unit="deg", default=1.0, classes=("a", "b"))
    # No request offers a pin, of any shape; /api/inputs lists none.
    api = Service(grid=SMALL)
    for query in ("fields=arm_class&arm_class=flocculent", "fields=arm_class&template=ngc_4414&arm_class=grand_design", "fields=arm_class&arm_pieces=[]"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    listed = api.handle("/api/inputs").json()
    assert not {"arm_class", "arm_pieces"} & {i["name"] for kind in ("controls", "seeds", "events") for i in listed[kind]}
    # The wire: /api/templates serves each pin in its shape.
    served = {t["name"]: {p["name"]: p for p in t["pins"]} for t in api.handle("/api/templates").json()["templates"]}
    assert set(served["milky_way"]) == {"bar_present", "sun_bar_angle", "arm_pieces"} and set(served["ngc_4414"]) == {"bar_present", "pitch_angle", "arm_class"}
    klass = served["ngc_4414"]["arm_class"]
    assert set(klass) == {"name", "label", "unit", "value", "source", "classes"} and klass["value"] == "flocculent" and klass["unit"] is None
    assert klass["classes"] == ["grand_design", "multi_armed", "flocculent"]
    rows = served["milky_way"]["arm_pieces"]
    assert set(rows) == {"name", "label", "unit", "value", "source"} and rows["unit"] is None and set(rows["value"]) == {"columns", "rows"}
    assert rows["value"]["columns"] == [{"name": "arm", "unit": None}, {"name": "beta_from", "unit": "deg"}, {"name": "beta_to", "unit": "deg"},
                                        {"name": "beta_kink", "unit": "deg"}, {"name": "radius_kink", "unit": "kpc"},
                                        {"name": "pitch_below", "unit": "deg"}, {"name": "pitch_above", "unit": "deg"}]
    assert rows["value"]["rows"][0] == ["Norma", 5.0, 54.0, 18.0, 4.46, -1.0, 19.5] and len(rows["value"]["rows"]) == 6
    assert set(served["milky_way"]["bar_present"]) == set(served["milky_way"]["sun_bar_angle"]) == {"name", "label", "unit", "value", "source"}
    assert served["milky_way"]["bar_present"]["value"] is True and served["milky_way"]["sun_bar_angle"]["value"] == 30.0
    # A response's inputs echo the pins the template gave: the table as rows.
    head = api.handle("/api/arrays", "fields=arm_class&template=milky_way").frame()[0]
    assert head["inputs"]["arm_pieces"][3] == ["Local", -8.0, 34.0, 9.0, 8.26, 11.4, 11.4] and head["inputs"]["sun_bar_angle"] == 30.0
    assert api.handle("/api/arrays", "fields=arm_class&template=ngc_4414").frame()[0]["inputs"]["arm_class"] == "flocculent"


def test_a_measured_number_is_a_pin_and_the_sun_moves_nothing_else(prod):
    """Ported from S59's file (D218 items 5-6 and the follow-up's item 7), unchanged in what it holds: a pin with
    a unit is a finite number held to the range of what it replaces; ``sun_bar_angle`` gives ``sun_azimuth`` and
    moves no other field; ``pitch_angle`` replaces the draw, which is published beside it; a run made with a pin
    is not resumed without it."""
    model = the_model(prod)
    only = ("sun_azimuth", "pitch_angle", "pitch_angle_drawn", "bar_half_length", "pattern_density_contrast", "gas_density_contrast")
    bare = run(model, None, SMALL, only=only)
    sun = run(model, {"sun_bar_angle": 30.0}, SMALL, only=only)
    assert math.isnan(float(bare.fields["sun_azimuth"])) and math.isfinite(float(sun.fields["sun_azimuth"]))
    for name in only[1:]:
        assert np.asarray(bare.fields[name]).tobytes() == np.asarray(sun.fields[name]).tobytes(), name
    assert math.isnan(float(run(model, {"sun_bar_angle": 30.0, "bar_present": False}, SMALL, only=only).fields["sun_azimuth"]))
    other = run(model, {"sun_bar_angle": 28.0}, SMALL, only=only)
    assert float(other.fields["sun_azimuth"]) - float(sun.fields["sun_azimuth"]) == pytest.approx(math.radians(-2.0), abs=1e-12)
    pitched = run(model, {"pitch_angle": 20.0}, SMALL, only=only)
    assert float(pitched.fields["pitch_angle"]) == 20.0 and float(pitched.fields["pitch_angle_drawn"]) == float(bare.fields["pitch_angle"])
    for bad in (True, "30", float("nan"), float("inf")):
        with pytest.raises(RunError, match="finite number in deg"):
            run(model, {"sun_bar_angle": bad}, SMALL, only=only)
    with pytest.raises(RunError, match="True or False"):
        run(model, {"bar_present": 1.0}, SMALL, only=only)
    with pytest.raises(RunError, match="cannot resume: (pin|input) 'pitch_angle'"):
        run(model, {}, SMALL, resume=pitched, only=only)
    for value, ok in ((1.0, True), (60.0, True), (0.999, False), (60.001, False), (-5.0, False)):
        if ok:
            assert float(run(model, {"pitch_angle": value}, SMALL, only=only).fields["pitch_angle"]) == value
        else:
            with pytest.raises(RunError, match="held to the range of what it replaces, 1 to 60 deg"):
                run(model, {"pitch_angle": value}, SMALL, only=only)
    for value, ok in ((0.0, True), (359.9, True), (360.0, False), (-0.1, False)):
        if ok:
            run(model, {"sun_bar_angle": value}, SMALL, only=only)
        else:
            with pytest.raises(RunError, match="0 up to, not including, 360 deg"):
                run(model, {"sun_bar_angle": value}, SMALL, only=only)
    api = Service(grid=SMALL)
    for query in ("fields=sun_azimuth&sun_bar_angle=30", "fields=pitch_angle&pitch_angle=20", "fields=pitch_angle&template=ngc_4414&pitch_angle=20"):
        got = api.handle("/api/arrays", query)
        assert got.status == 400 and "is a template's pin, not an input a request may set" in got.json()["error"], query
    head = api.handle("/api/arrays", "fields=sun_azimuth,pitch_angle,pitch_angle_drawn&template=ngc_4414").frame()[0]
    assert head["inputs"]["pitch_angle"] == 28.9 and head["scalars"]["pitch_angle"] == 28.9 and head["scalars"]["sun_azimuth"] is None


# --- the table kind (ported from S59's file) -------------------------------------------------------------------------


def test_the_pieces_are_a_table_served_whole_and_no_catalogue(prod):
    """S59's plumbing decision (D218), kept for the table that replaced ``arm_segment``: the census's columns are
    a table's - domain ``table``, read whole by the model's own stages, no object class, no census route, no ramp -
    and the API serves them whole with the run's other arrays."""
    assert TABLES == ("arm_piece",) and Kind.TABLE_COLUMN.domain == "table" and not Kind.TABLE_COLUMN.categorical
    for d in ap.ARM_PIECES:
        assert d.kind is Kind.TABLE_COLUMN and d.of == "arm_piece" and d.ramp is None and not d.axes
    base = dict(name="x", label="x", unit="rad", about="x", kind=Kind.TABLE_COLUMN)
    from galaxy.core.fielddoc import DeclarationError, Ramp
    with pytest.raises(DeclarationError, match="one of the tables"):
        FieldDecl(**base, of="arm_segment")
    with pytest.raises(DeclarationError, match="is not drawn and takes no ramp"):
        FieldDecl(**base, of="arm_piece", ramp=Ramp("viridis"))
    api = Service(grid=SMALL)
    ask = "fields=" + ",".join((*pt.PIECE_FIELDS, "arm_class")) + "&template=milky_way"
    got = api.handle("/api/arrays", ask)
    assert got.status == 200
    head, arrays = got.frame()
    o = run(the_model(prod), inputs_of("milky_way"), SMALL, only=pt.PIECE_FIELDS)
    assert set(arrays) == set(pt.PIECE_FIELDS) and "arm_pieces" in head["stages"] and not {"systems", "clouds", "clusters"} & set(head["stages"])
    for name in pt.PIECE_FIELDS:
        assert arrays[name].dtype == np.float64 and arrays[name].ndim == 1 and arrays[name].size > 0
        assert arrays[name].tobytes() == np.asarray(o.fields[name]).tobytes() and o.decls[name].kind is Kind.TABLE_COLUMN, name
    _, narrow = api.handle("/api/arrays", ask + "&precision=f4&t_samples=8").frame()
    assert all(narrow[n].dtype == np.float32 and np.array_equal(narrow[n], arrays[n].astype(np.float32)) for n in pt.PIECE_FIELDS)
    _, off = api.handle("/api/arrays", ask + "&layer=off").frame()
    assert all(off[name].shape == (0,) for name in pt.PIECE_FIELDS)
    window = "r_min=7&r_max=9&phi_min=0&phi_max=0.4"
    for path, query in (("/api/region", window), ("/api/clouds", window), ("/api/clusters", window), ("/api/remnants", window),
                        ("/api/bright", window + "&n=50")):
        r = api.handle(path, query)
        assert r.status == 200, (path, r.body[:200])
        header, rows = wire.decode(r.body)
        assert header["columns"] and not [c for c in (*header["columns"], *rows) if c.startswith("arm_piece")], path


# --- no step in the count but where a chain ends untapered (the second follow-up, item 3) -----------------------------


def untapered_ends(table: np.ndarray) -> np.ndarray:
    """The radii, kpc, at which a chain stops crossing rings with no taper, from the table alone: an end of a piece
    that meets another chain (``arm_piece_join``), and a kink at which two pieces of one chain both end or both
    start - a measured arm that turns back in radius."""
    out = []
    ends = []  # (chain, ln R, azimuth, outer?)
    for row in table:
        x0, y0, x1, y1 = line_of(row[2:6])
        ends += [(row[0], x0, y0, False), (row[0], x1, y1, True)]
        if row[7] == 1.0:
            out.append(math.exp(x0))
        if row[7] == 2.0:
            out.append(math.exp(x1))
    for i, (chain, x, y, outer) in enumerate(ends):
        for other, u, v, kind in ends[i + 1:]:
            if other == chain and kind == outer and abs(u - x) < 1e-9 and abs(math.remainder(v - y, 2.0 * math.pi)) < 1e-9:
                out.append(math.exp(x))
    return np.array(sorted(out))


@pytest.mark.parametrize("template", ("milky_way", "ngc_4414", "default"))
def test_the_count_is_continuous_but_where_a_chain_ends_untapered(prod, template):
    """The gate's second follow-up, item 3: "The count on a ring is the sum over crossing chains of their taper
    weights, so B and the bounded width are continuous in R"; its gate: "the count continuous (no ring-to-ring step
    in B above the taper's own rate)". Read at every radius where the set of crossing pieces changes - a start,
    a kink, an end - a part in 1e10 inside and outside it: **the count does not step at a chain's free start or
    end (its weight is 0 there) nor at a kink (the taper runs along the chain)** - but where the crossing set becomes
    empty or stops being so, where since the fourth follow-up N steps between 0 and 1 and the field does not - and so neither do the width and
    B, which are continuous functions of it and of the law wherever the count is not 0.

    **It does step where a chain ends with no taper, as ruled**: at a join ("joined, without taper") the chain's
    weight goes from what it was to nothing, and at the turn of a measured arm that kinks back in radius. Those
    radii are found from the table by this file's own reading and every step is at one of them; they are counted
    and the largest relative step in B across one is recorded. Said plainly: "B continuous in R" does not hold
    at a join; the two sentences of the ruling meet there, and the build follows both - no taper at a join, the
    count a sum of taper weights."""
    o = template_run(prod, template) if template != "default" else run(the_model(prod), None, only=PATTERN)
    F, R = o.fields, o.grid.R
    sp = compose.stellar_pattern(F, R)
    table = table_of(F)
    edges = np.exp(sp.pieces.breaks)
    edges = edges[(edges > R[0]) & (edges < R[-1])]
    step = sp.count_at(edges * (1.0 + 1e-10)) - sp.count_at(edges * (1.0 - 1e-10))
    hard = untapered_ends(table)
    at_hard = np.array([hard.size > 0 and float(np.abs(hard / r - 1.0).min()) < 1e-8 for r in edges])
    # ... and, since the fourth follow-up (B: the count is at least 1 on a ring any chain crosses), the radii at which the
    # crossing set becomes empty or stops being so: there N steps between 0 and 1, and B between 0 and sqrt(budget/v),
    # while the field does not (the chain's weight is 0 there).
    crossing_below, crossing_above = sp.pieces.chains_crossing(edges * (1.0 - 1e-10)), sp.pieces.chains_crossing(edges * (1.0 + 1e-10))
    at_hard |= (crossing_below == 0) | (crossing_above == 0)
    assert np.abs(step[~at_hard]).max(initial=0.0) < 1e-6
    # ... and between two such radii the count is continuous: a part in 1e9 of radius moves it by a part in 1e6 at most.
    between = 0.5 * (edges[1:] + edges[:-1])
    assert np.abs(sp.count_at(between * (1.0 + 1e-9)) - sp.count_at(between)).max(initial=0.0) < 1e-5
    stepped = np.abs(step) > 1e-6
    budget = sp.amplitude_at(edges * (1.0 - 1e-10)), sp.amplitude_at(edges * (1.0 + 1e-10))
    both = stepped & (budget[0] > 0.0) & (budget[1] > 0.0)
    jump = float(np.abs(budget[1][both] / budget[0][both] - 1.0).max(initial=0.0))
    record = (int(edges.size), int(stepped.sum()), sp.pieces.joins, round(jump, 3))
    # (radii where the crossing set changes, those at which the count steps, the galaxy's joins, the largest
    #  relative step of B at one of them where there is an amplitude on both sides)
    assert record == EXPECTED_STEPS.get(template), repr(record)


EXPECTED_STEPS: dict = {"milky_way": (64, 6, 4, 0.349), "ngc_4414": (63, 4, 2, 0.155), "default": (31, 2, 1, 0.015)}  # S60 fourth pass: was {"milky_way": (65, 7, 7, 0.031), "ngc_4414": (63, 2, 2, 0.155), "default": (31, 1, 1, 0.015)}


# --- no square edge anywhere: continuity across every kink and join (the gate's third follow-up) ---------------------


def vertices_of(p: pc.Pieces) -> list:
    """Every kink and join of the census as (ln R, azimuth, the piece whose end it is, the piece whose start, kind):
    a kink is an end at which a piece of the same chain stands (``link_end``); a join is an end of a drawn piece
    that meets another chain (``join``)."""
    out = []
    for j in range(p.count):
        if p.link_end[j] >= 0:
            out.append((float(p.x_end[j]), float(p.phi_end[j]), j, int(p.link_end[j]), "kink"))
        if p.join[j] == pc.JOIN_OUTER:
            out.append((float(p.x_end[j]), float(p.phi_end[j]), j, -1, "join"))
        if p.join[j] == pc.JOIN_INNER:
            out.append((float(p.x_start[j]), float(p.start_azimuth[j]), -1, j, "join"))
    return out


@pytest.mark.parametrize("template", ("milky_way", "ngc_4414"))
def test_no_square_edge_across_any_kink_or_join(prod, template):
    """The gate's third follow-up, item 1: "Nothing physical is discontinuous there, so no square edge may remain
    anywhere: asserted by a continuity test across every kink and join on both templates." Around every kink and
    join of the census (:func:`vertices_of`), on rings 0.3 width below, through and above the vertex, the pieces'
    field (``arms_at``, the body left out: its interpolant is its own) is sampled along the ring across the
    vertex, across the kink's bisector and across the lines the third pass's windows were cut square on (each
    piece's perpendicular at its end), at a spacing of a ten-thousandth of the width; the largest change between
    neighbouring samples must be under **the Lipschitz bound derived from the amplitude and the width**, not one
    fitted: a chain's excess is a taper of slope 1/w in the arc length times a Gaussian of dispersion σ whose
    slope is at most 1/(σ√e), so along the ring |ΔE_c| ≤ (1/w + 1/(σ√e)) R Δφ and the field changes by at most the
    amplitude times the chains in reach times that; and the change must shrink with the spacing (the largest
    change at half the spacing under three quarters of it - a jump would not shrink). **The ring-to-ring change**
    of the stellar profile over 5-13 kpc is read in the predictions (``largest ring-to-ring change 5-13``).

    As read on the fourth pass: the largest change over a spacing is a small fraction of the bound on both
    templates (the record below), and halves with the spacing."""
    o = template_run(prod, template)
    F, R = o.fields, o.grid.R
    sp = compose.stellar_pattern(F, R)
    p = sp.pieces
    vertices = vertices_of(p)
    assert vertices, "a template with no kink and no join tests nothing"
    worst = {"share of bound": 0.0, "ratio at half spacing": 0.0, "kinks": 0, "joins": 0}
    for x_v, phi_v, ended, started, kind in vertices:
        worst[kind + "s"] += 1
        r_v = math.exp(x_v)
        w_v = float(sp.width_at(np.array([r_v]))[0])
        for dx in (-0.3, 0.0, 0.3):
            r = r_v * math.exp(dx * w_v / r_v)
            x = math.log(r)
            laid = sp.laid(np.array([r]))
            if not laid.live.any() or laid.effective[0] <= 0.0:
                continue
            w, a = float(laid.width[0]), float(laid.effective[0])
            sigma = w / FWHM
            chains = int(laid.last[0].sum())
            bound = a * chains * (1.0 / w + 1.0 / (sigma * math.sqrt(math.e)))  # per kpc along the ring
            # The azimuths to centre on: the vertex, and each piece's old square edge (its perpendicular at the
            # end or start) where it crosses this ring.
            centres = [phi_v]
            for j, at_end in ((ended, True), (started, False)):
                if j < 0:
                    continue
                xj = x - p.x_start[j]
                t = p.length[j] if at_end else 0.0
                centres.append(float(p.phi_start[j] + p.sense[j] * (t - xj * p.sin_abs[j]) / p.cos_abs[j]))
            for centre in centres:
                for spacing, key in ((1e-4, "full"), (5e-5, "half")):
                    dphi = spacing * w / r
                    phi = centre + dphi * np.arange(-int(0.5 * w / r / dphi), int(0.5 * w / r / dphi) + 1)
                    v = sp.arms_at(np.array([r]), phi)
                    change = float(np.abs(np.diff(v)).max())
                    if key == "full":
                        full = change
                        worst["share of bound"] = max(worst["share of bound"], change / (bound * r * dphi))
                    else:
                        worst["ratio at half spacing"] = max(worst["ratio at half spacing"], change / full if full > 1e-13 else 0.0)
    assert worst["share of bound"] <= 1.0 and worst["ratio at half spacing"] <= 0.75, worst
    record = (worst["kinks"], worst["joins"], round(worst["share of bound"], 3), round(worst["ratio at half spacing"], 3))
    # (kinks, joins, the largest change over a spacing as a share of the Lipschitz bound, the largest ratio of the
    #  change at half the spacing to that at the full spacing)
    assert record == EXPECTED_CONTINUITY[template], repr(record)


EXPECTED_CONTINUITY: dict = {"milky_way": (38, 7, 0.072, 0.5), "ngc_4414": (0, 2, 0.049, 0.5)}


# --- per-region determinism (D60) on the pattern of pieces ---------------------------------------------------------------


@pytest.mark.parametrize("path, where", [("/api/region", ("star_radius", "star_azimuth")), ("/api/clouds", ("cloud_radius", "cloud_azimuth")),
                                         ("/api/clusters", ("cluster_radius", "cluster_azimuth"))])
def test_a_cell_is_the_same_alone_in_a_window_and_in_a_sweep_at_every_level(path, where):
    """**Per-region determinism is the catalogue's contract** (D60), on the Milky Way template with the layer on -
    its arms the census of pieces, the gas carried between the solved rings, the young stars read by the law at a
    point: a cell's stars, and a cell's clouds and clusters, are the same rows - every column, to the bit -
    whether the cell is asked for alone, inside a window of several cells, or inside a sweep round the whole
    ring, at levels 0 to 3 (at level k the cell is the level-k child that holds the point (8.1 kpc, 1.0 rad))."""
    svc = Service()
    R = svc.grid.R
    record = []
    for level in range(4):
        cell = systems.cells_in(R, 8.1, 8.1, 1.0, 1.0, level)[0]
        b = systems.cell_bounds(R, cell, level)
        parent = systems.parent_of(cell, level)[0]
        eps = 1e-9
        inside = (b["r_lo"] + eps, b["r_hi"] - eps, b["phi_lo"] + eps, b["phi_hi"] - eps)
        asks = ("r_min=%r&r_max=%r&phi_min=%r&phi_max=%r" % inside,
                "r_min=7.6&r_max=8.6&phi_min=0.7&phi_max=1.3",
                "r_min=8.05&r_max=8.15&phi_min=0&phi_max=6.283185307179586")
        got = []
        for ask in asks:
            response = svc.handle(path, f"{ask}&level={level}&template=milky_way")
            assert response.status == 200, (path, level, response.body[:200])
            header, rows = wire.decode(response.body)
            assert header["level"] == level
            radius, azimuth = np.asarray(rows[where[0]]), np.asarray(rows[where[1]])
            mine = (radius >= inside[0]) & (radius <= inside[1]) & (azimuth >= inside[2]) & (azimuth <= inside[3])
            if path != "/api/region":
                # A cloud or a cluster is its level-0 cell's, wherever its own position lies (one drawn near a cell's
                # edge can stand in the next cell's footprint), and a level filters by that position: the cell's
                # objects inside the child's footprint.
                mine &= np.asarray(rows["cell"]) == parent
            names = sorted(n for n in rows if np.asarray(rows[n]).shape[:1] == radius.shape)
            order = np.lexsort((azimuth[mine], radius[mine]))
            got.append({n: np.asarray(rows[n])[mine][order] for n in names})
        assert got[0][where[0]].size > 0 or level > 0, (path, level)  # (a child cell may hold no cloud or cluster)
        for other in got[1:]:
            assert set(other) == set(got[0])
            for n in got[0]:
                assert np.array_equal(got[0][n], other[n], equal_nan=True), (path, level, n)
        record.append(int(got[0][where[0]].size))
    print(path, "rows of the cell at levels 0-3:", record)
