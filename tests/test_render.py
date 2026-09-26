"""The filter integral and /api/render (S38, BUILD_II V1; RENDER_PHYSICS §§0, 2, 3a).

**The gate.** The whole galaxy rendered through the table's own B and V — Gaussians at the SVO
reference wavelengths and FWHMs of the passbands the isochrone magnitudes are in
(``photometry.PASSBANDS``, ``spectra.band_curve``) — the stellar responses integrated over every
(R, φ) cell of the frame plus the bulge (the linear buffer before the tone map, which only multiplies
it), each turned into a Vega magnitude by the band's own zero point: the mean L_λ through the curve
against 4π (10 pc)² f_λ,Vega. Against Phase 3's ``colour_b_v`` 0.6306 and ``absolute_magnitude_v``
−21.2159, which are the table's.

**The second cut (ruled by the orchestrator at S38) and what it costs.** The stellar spectrum is the
population's own: the eight band points λL_λ per ring (``disc_sed_*``, ``bulge_sed_*``), joined by
power laws, blackbody tails beyond U and K. Anchored at the bands' reference wavelengths as they
are, the joined spectrum's mean over a band is not its value at the band's centre — the spectrum
peaks near B, and read over B's 950 Å it is fainter than at B's centre — and the frame read B 0.077
mag and V 0.017 mag faint, B − V 0.690 (+0.060); ring by ring the worst was B 0.089 (0.71 kpc) and
V 0.034 (0.94 kpc). So the points are moved, twelve fixed multiplicative passes
(``spectra.band_consistent``), until each band's mean is the table's value: the worst ring's residual
is then 5.0e-5 mag in V and 9.2e-5 in B − V. The frame adds its own quadrature (cells of R dR dφ at
their centres against the stage's trapezoid in R), 1.5e-4 mag in every band alike. **The tolerance is
1e-3 mag in M_V and in B − V**: those two costs, 2.5e-4 together at worst, with a factor of four for
what the Gaussian stand-ins do that the measured curves would not. Measured at S38: B − V 0.630641
(+8.9e-5), M_V −21.216042 (−1.7e-4), pinned beside the tolerance.

**The first cut, recorded (S38).** One blackbody at the colour temperature carrying the bolometric
light, tied to the table at its own Sun: frame B − V 0.642807 and M_V −21.928533 — twice the table's
V light, the table's BC_V being −0.87 against a 5600 K blackbody's −0.1 — and ring by ring its B − V
−0.080 to +0.252 from the table's (luminosity-weighted +0.065). Pinned below as the record the second
cut is measured against; it is not the gate.

**Extinction off, since S39.** The gate composes the stars and the bulge alone: the render returns
every component as its own array (§2, components not colours), and the dust's three
(``dust_extinction``, ``dust_scattered``, ``dust_thermal``) are simply not multiplied in or added.
The same frame with the dust composed face-on is pinned beside it as a record, not a gate.

**V2's gate (S39): the frame's energy balance and its face-on profile** — see the section below.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.stages import spectra
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.dust import slab_absorbed_fraction
from galaxy.stages.photometry import BANDS, PASSBANDS, band_nu_l_nu, lookup, lookup_columns, population_over

ROOT = Path(__file__).resolve().parents[1]
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
SETS = FILTERS["sets"]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)

# The gate's tolerance, stated (module docstring), and what the second cut measured at S38.
TOLERANCE = 1e-3
MEASURED_B_V = 0.630641  # the table's 0.630552
MEASURED_M_V = -21.216042  # the table's -21.215871
# The first cut's record (S38): one blackbody at the colour temperature.
FIRST_CUT_B_V = 0.642807
FIRST_CUT_M_V = -21.928533
# The record beside the gate (S39): the same frame with the dust composed face-on (``face_on``).
FACE_ON_B_V = {"basic": 0.647469, "azimuthal": 0.647469}  # +0.0168 on the gate's
FACE_ON_M_V = {"basic": -20.804991, "azimuthal": -20.804991}  # 0.411 mag fainter


def curves(name: str) -> str:
    return json.dumps(SETS[name]["curves"])


def table_bands(*bands: str) -> str:
    return json.dumps([spectra.band_curve(b).json() for b in bands])


def render(api: Service, model: str, name: str, **extra: str):
    query = {"model": [model], "filters": [curves(name)], "set": [name], **{k: [v] for k, v in extra.items()}}
    got = api.handle("/api/render", query)
    assert got.status == 200, got.body[:300]
    return wire.decode(got.body)


@pytest.fixture(scope="module")
def full():
    """One cold service on the default grid: the gate is against the published default galaxy."""
    return Service()


@pytest.fixture
def small():
    return Service(grid=SMALL)


def scalars(api: Service, model: str, *names: str) -> dict[str, float]:
    got = api.handle("/api/arrays", {"model": [model], "fields": [",".join(names)]})
    header, arrays = wire.decode(got.body)
    return {**header["scalars"], **arrays}


def cell_areas(header: dict) -> np.ndarray:
    """pc² of every (R, φ) cell of the window: R dR dφ at the cell's centre radius."""
    r_axis, phi_axis = header["window"]["R"], header["window"]["phi"]
    R = r_axis["lo"] + (np.arange(r_axis["n"]) + 0.5) * r_axis["width"]
    return (R * r_axis["width"] * phi_axis["width"] * PC_PER_KPC**2)[:, None] * np.ones(phi_axis["n"])


def band_magnitude(response: np.ndarray, band: str) -> np.ndarray:
    """A Vega magnitude from a response through ``band_curve(band)``: the mean L_λ over the curve against a
    zero-magnitude source's at 10 pc (``photometry.band_nu_l_nu`` of unit flux over the reference wavelength)."""
    curve = spectra.band_curve(band)
    lam = curve.grid()
    mean = np.asarray(response) / np.trapezoid(curve.at(lam), lam)
    zero = float(band_nu_l_nu(np.array(1.0), band)) / PASSBANDS[band].reference
    return -2.5 * np.log10(mean / zero)


def frame_total(header: dict, arrays: dict) -> np.ndarray:
    """Each filter's response summed over the frame's cells, plus the bulge's: L☉."""
    return (arrays["stars"] * cell_areas(header)[..., None]).sum(axis=(0, 1)) + np.asarray(header["bulge"])


def face_on(header: dict, arrays: dict) -> dict:
    """The frame's stars with the dust composed face-on (S39): light mixed through its own dust leaves (1 − T)/τ
    of itself, τ = −ln T the column's depth in each filter; the scattered light joins it at the face-on phase
    factor; the thermal emission is added undimmed (optically thin)."""
    tau = -np.log(arrays["dust_extinction"])[:, None, :]
    own = np.where(tau > 1e-12, -np.expm1(-tau) / np.where(tau > 1e-12, tau, 1.0), 1.0)
    phase = header["components"]["dust_scattered"]["phase"]["factor"][-1]
    lit = (arrays["stars"] + phase * arrays["dust_scattered"]) * own + arrays["dust_thermal"][:, None, :]
    return {**arrays, "stars": lit}


# --- the gate -------------------------------------------------------------------------------


def test_the_frame_s_colour_and_magnitude_are_the_table_s(full, model):
    got = full.handle("/api/render", {"model": [model.name], "filters": [table_bands("B", "V")]})
    header, arrays = wire.decode(got.body)
    total = frame_total(header, arrays)
    m_b, m_v = band_magnitude(total[0], "B"), band_magnitude(total[1], "V")
    table = scalars(full, model.name, "colour_b_v", "absolute_magnitude_v")
    print(model.name, m_b - m_v, m_v, table)
    assert table["colour_b_v"] == pytest.approx(0.6306, abs=5e-5)  # the targets, as published
    assert table["absolute_magnitude_v"] == pytest.approx(-21.2159, abs=5e-5)
    assert abs((m_b - m_v) - table["colour_b_v"]) < TOLERANCE
    assert abs(m_v - table["absolute_magnitude_v"]) < TOLERANCE
    # The measurement itself, pinned, so it cannot drift inside the tolerance unseen.
    assert m_b - m_v == pytest.approx(MEASURED_B_V, abs=2e-6)
    assert m_v == pytest.approx(MEASURED_M_V, abs=2e-6)
    # The record (S39), not the gate: the same frame with the dust composed face-on, as the viewer draws a
    # face-on disc — each cell's light through its mixed dust, (1 - T)/tau of itself, plus the scattered light
    # at the face-on phase factor, dimmed alike; the bulge left undimmed (a stated simplification).
    dimmed = frame_total(header, face_on(header, arrays))
    d_b, d_v = band_magnitude(dimmed[0], "B"), band_magnitude(dimmed[1], "V")
    print(model.name, "face-on with dust", d_b - d_v, d_v)
    assert d_b - d_v == pytest.approx(FACE_ON_B_V[model.name], abs=2e-6)
    assert d_v == pytest.approx(FACE_ON_M_V[model.name], abs=2e-6)


def test_every_band_of_the_frame_is_the_table_s(full):
    """All eight, not only B and V: the frame against each published magnitude, within the gate's tolerance."""
    got = full.handle("/api/render", {"filters": [table_bands(*BANDS)]})
    header, arrays = wire.decode(got.body)
    total = frame_total(header, arrays)
    table = scalars(full, "basic", *(f"absolute_magnitude_{b.lower()}" for b in BANDS))
    for k, band in enumerate(BANDS):
        assert band_magnitude(total[k], band) == pytest.approx(table[f"absolute_magnitude_{band.lower()}"], abs=TOLERANCE), band


def per_ring_residuals(api: Service, iterations: int | None) -> np.ndarray:
    """(rings with light, 8): each band's mean through its curve against the table's value at that ring, mag;
    the spectrum's anchors as published (``iterations`` 0) or made band-consistent."""
    names = [f"disc_sed_{b.lower()}" for b in BANDS]
    f = scalars(api, "basic", *names, "disc_light_temperature")
    sed = np.stack([f[n] for n in names], axis=-1)
    points = sed if iterations == 0 else spectra.band_consistent(sed, f["disc_light_temperature"], *(() if iterations is None else (iterations,)))
    bands = [spectra.band_curve(b) for b in BANDS]
    response = spectra.sed_response(points, f["disc_light_temperature"], bands)
    norm = np.array([np.trapezoid(c.at(c.grid()), c.grid()) for c in bands])
    lit = sed[:, 2] > 0
    return -2.5 * np.log10((response[lit] / norm) / (sed[lit] / spectra.SED_WAVELENGTHS))


def test_what_the_interpolation_costs_ring_by_ring(full):
    """The joined spectrum through each band's curve against the band's own value, per ring: as anchored
    (the record), and after the twelve passes the route makes (what the gate's tolerance covers)."""
    raw = per_ring_residuals(full, 0)
    assert np.abs(raw[:, BANDS.index("B")]).max() == pytest.approx(0.0890, abs=5e-4)
    assert np.abs(raw[:, BANDS.index("V")]).max() == pytest.approx(0.0336, abs=5e-4)
    fixed = per_ring_residuals(full, None)
    v, b_v = fixed[:, BANDS.index("V")], fixed[:, BANDS.index("B")] - fixed[:, BANDS.index("V")]
    assert np.abs(v).max() < 6e-5 and np.abs(b_v).max() < 1e-4  # 5.0e-5 and 9.2e-5 at S38
    assert np.abs(fixed).max() < 1e-4  # every band, every ring


def first_cut_zero_points(bands: dict[str, spectra.Curve]) -> dict[str, float]:
    """The first cut's zero points: each band's blackbody at the table's own Sun given the Sun's magnitude."""
    L, T = lookup(np.array([1.0]), np.array([4.57]), np.array([0.0]))
    sun = lookup_columns(np.array([1.0]), np.array([4.57]), np.array([0.0]), tuple(bands))
    share = spectra.blackbody_response(list(bands.values()), T)[0]
    return {band: float(sun[band][0] + 2.5 * math.log10(L[0] * share[k])) for k, band in enumerate(bands)}


def test_the_first_cut_is_recorded(full):
    """S38's first cut, for the record: the bolometric light as one blackbody at the colour temperature,
    through the viewer's rgb B and V as they stood (4361/890 and 5448/840 A), tied to the table's own Sun."""
    b_v = {"B": spectra.Curve("B", "gaussian", centre=4361.0, width=890.0), "V": spectra.Curve("V", "gaussian", centre=5448.0, width=840.0)}
    zp = first_cut_zero_points(b_v)
    f = scalars(full, "basic", "disc_surface_brightness", "disc_light_temperature", "bulge_luminosity", "bulge_light_temperature",
                "stars_formed_history", "feh_history")
    grid = full.grid
    per_ring = spectra.blackbody_stellar_response(f["disc_surface_brightness"], f["disc_light_temperature"], list(b_v.values()))
    ring_area = grid.R * grid.axes["R"].width * 2.0 * math.pi * PC_PER_KPC**2  # the frame's cells, summed round each ring
    bulge = f["bulge_luminosity"] * spectra.blackbody_response(list(b_v.values()), np.array([f["bulge_light_temperature"]]))[0]
    total = (per_ring * ring_area[:, None]).sum(axis=0) + bulge
    m = {band: zp[band] - 2.5 * math.log10(total[k]) for k, band in enumerate(b_v)}
    assert m["B"] - m["V"] == pytest.approx(FIRST_CUT_B_V, abs=5e-6)
    assert m["V"] == pytest.approx(FIRST_CUT_M_V, abs=5e-6)
    # Ring by ring, the first cut's B - V against the same populations' in the table (light.py's sum).
    dt = float(grid.spec.t_max) / float(grid.spec.n_t)
    youngest = float(grid.spec.t_max) - (grid.t + 0.5 * dt)
    step = population_over(youngest, youngest + dt, f["feh_history"])
    formed = np.asarray(f["stars_formed_history"]) / (1.0 - full.models.get("basic").constants["RETURN_FRACTION"].value)
    b, v = (formed * step["B"]).sum(axis=1), (formed * step["V"]).sum(axis=1)
    lit = (b > 0) & (v > 0) & (per_ring[:, 1] > 0)
    d = ((zp["B"] - 2.5 * np.log10(per_ring[lit, 0])) - (zp["V"] - 2.5 * np.log10(per_ring[lit, 1]))) - (-2.5 * np.log10(b[lit] / v[lit]))
    weight = (f["disc_surface_brightness"] * grid.R)[lit]
    assert d.min() == pytest.approx(-0.0796, abs=1e-3)
    assert d.max() == pytest.approx(0.2517, abs=1e-3)
    assert np.average(d, weights=weight) == pytest.approx(0.0647, abs=1e-3)


def test_the_viewer_s_rgb_b_and_v_are_the_table_s_bands():
    """The broadband set the viewer sends draws its blue and green through the gate's own B and V."""
    by_name = {c["name"]: c for c in SETS["rgb"]["curves"]}
    for band in ("B", "V", "R"):
        assert spectra.parse_curves([by_name[band]])[0] == spectra.band_curve(band), band


def test_the_joined_spectrum_carries_most_of_the_published_light(full):
    """Through a box spanning the whole continuum grid the spectrum returns its bolometric light: 0.708 of
    disc_luminosity at S38. The rest is below U, where a blackbody at the colour temperature scaled to U
    falls far short of the young stars' ultraviolet: a stated limit of the tails, not of the bands."""
    wide = json.dumps([{"name": "all", "shape": "box", "centre": 150_500.0, "width": 299_000.0}])
    header, arrays = wire.decode(full.handle("/api/render", {"filters": [wide]}).body)
    frame = float((arrays["stars"][..., 0] * cell_areas(header)).sum())
    published = scalars(full, "basic", "disc_luminosity")["disc_luminosity"]
    assert frame / published == pytest.approx(0.708, abs=2e-3)


def test_the_line_is_the_nebular_field_in_two_layers(full, model):
    """S39: the HII regions' share placed by the contrast in the clouds' layer, the diffuse gas's per ring in its
    own published layer; around every ring the two are the published nebular line (V1's one array, split)."""
    header, arrays = render(full, model.name, "sho")
    f = scalars(full, model.name, "halpha_surface_brightness_nebular", "halpha_surface_brightness_hii",
                "halpha_surface_brightness_dig", "dig_scale_height", "thin_disc_scale_height", "pattern_density_contrast")
    for name in ("halpha_hii", "halpha_dig"):
        assert header["components"][name]["transmission"] == [0.0, 1.0, 0.0]  # [S II], Halpha, [O III] boxes
    assert np.array_equal(arrays["halpha_dig"][:, 1], f["halpha_surface_brightness_dig"])
    placed = f["halpha_surface_brightness_hii"][:, None] * np.maximum(f["pattern_density_contrast"], 0.0)
    assert np.array_equal(arrays["halpha_hii"][..., 1], placed)
    assert not arrays["halpha_hii"][..., [0, 2]].any() and not arrays["halpha_dig"][:, [0, 2]].any()
    ring = arrays["halpha_hii"][..., 1].mean(axis=1) + arrays["halpha_dig"][:, 1]
    assert ring == pytest.approx(f["halpha_surface_brightness_nebular"], rel=1e-12, abs=0.0)
    layers = header["layers"]
    assert layers["halpha_dig"] == f["dig_scale_height"] == 1.4
    assert layers["halpha_hii"] == pytest.approx(0.5 * f["thin_disc_scale_height"] / 1000.0, rel=1e-15)  # the clouds' layer
    assert layers["stars"] == layers["dust"] == pytest.approx(f["thin_disc_scale_height"] / 1000.0, rel=1e-15)
    for name, entry in header["components"].items():
        assert entry["fields"] and entry["about"] and entry["layer"] in layers, name
    # The lines the model does not publish are named, not drawn dark (rule B9).
    assert set(header["absent"]["lines"]) == {"hbeta", "oiii_5007", "sii_6716", "sii_6731", "nii_6583"}


# --- V2's gate (S39): the frame's energy balance and its face-on profile --------------------------
#
# **The balance, and how its two sides are made commensurable.** The dust stage absorbs grey at V: every
# wavelength of a ring's starlight loses the share a(τ) = 1 − P_esc((1 − albedo_V) τ_V) of a uniform mixed
# slab, and the absorbed power is that share of the bolometric light. The frame's filters are not bolometric
# (its stellar continuum carries 0.708 of disc_luminosity, S38) and no sum of them is, so the removed light is
# made commensurable **by its share, not its sum**: in each filter the frame's dust removes, from the light
# emitted in its mixed slab and averaged over every direction a frame could be taken from, a share read from
# ``dust_extinction`` alone (τ = −ln T, the absorbing part by the header's albedo at the filter) — and through
# a curve at the grain table's own V row (5470 Å, where the stage's albedo was read) that share times the
# published bolometric light is the power the frame says the dust absorbs. The direction average is taken the
# frame's way, a mixed slab seen at every inclination μ, removed share 1 − μ(1 − e^(−τ/μ))/τ, integrated over μ by
# quadrature — not the stage's closed form (1/2 − E₃(τ))/τ, which it equals (B3: two computations).
# The infrared side needs no such step: ``dust_thermal`` through the "ir" set's TIR box, 8–1000 µm, holds all
# but what the modified blackbody puts outside it, summed over the frame. **Tolerance 1e-3** between the two
# sides: the one cost that separates them is the TIR box's coverage — 6.8e-4 of the frame's Σ_IR lies outside
# 8–1000 µm, almost all of it longward of 1 mm in the outer disc's 2–10 K dust (the continuum grid stops at 1 mm)
# — measured ring by ring from the arrays and pinned; against the published totals both sides also carry the
# frame's cells (R dR dφ at their centres) against the stage's trapezoid in R, +3.4e-4 on each. Measured at S39:
# absorbed 1.000344, emitted 0.999664 of the published totals, emitted over absorbed 0.999321.

IR = FILTERS["measured"]["ir"]["curves"]
V_ROW = {"name": "V (grain table)", "shape": "gaussian", "centre": 5470.0, "fwhm": 852.44}
BALANCE_TOLERANCE = 1e-3
# Measured at S39 (default grid), pinned beside the tolerance.
MEASURED_ABSORBED = {"basic": 1.000344, "azimuthal": 1.000344}  # the frame's absorbed power over dust_absorbed_luminosity
MEASURED_EMITTED = {"basic": 0.999664, "azimuthal": 0.999664}  # the frame's TIR over dust_infrared_luminosity
TIR_OUTSIDE = {"basic": 6.79639e-4, "azimuthal": 6.79639e-4}  # the share of the frame's Sigma_IR outside 8-1000 um
REMOVED_SHARE = {m: [0.361486, 0.374444, 0.372646, 0.374459] for m in ("basic", "azimuthal")}  # R, V, B, V row
CURVE_OVER_GREY = 0.744368
THIN_OVER_SLAB = 12.184149
PROFILE_WORST = {"basic": 9.18151e-4, "azimuthal": 9.18151e-4}


def full_render(api: Service, model: str, curve_list: list) -> tuple[dict, dict]:
    got = api.handle("/api/render", {"model": [model], "filters": [json.dumps(curve_list)]})
    assert got.status == 200, got.body[:300]
    return wire.decode(got.body)
# Gauss-Legendre in ln(mu) over [1e-12, 1]: the removed share has a 1/mu tail from mu ~ tau to 1, smooth in ln(mu).
_U, _W = np.polynomial.legendre.leggauss(200)
_LN_MIN = math.log(1e-12)
MU = np.exp(0.5 * _LN_MIN * (1.0 - _U))
MU_WEIGHT = 0.5 * (-_LN_MIN) * _W * MU


def removed_share(tau: np.ndarray) -> np.ndarray:
    """The share of a uniform mixed slab's light its dust takes out, seen at every inclination and averaged over
    them uniformly in μ = |cos i| (every direction alike): ∫₀¹ [1 − μ(1 − e^(−τ/μ))/τ] dμ, by quadrature."""
    t = np.asarray(tau, dtype=float)[..., None]
    safe = np.where(t > 0.0, t, 1.0)
    escaped = np.where(t > 0.0, MU * -np.expm1(-safe / MU) / safe, 1.0)
    return ((1.0 - escaped) * MU_WEIGHT).sum(axis=-1)


def ring_areas(header: dict) -> np.ndarray:
    return cell_areas(header).sum(axis=1)


def absorbing_depth(header: dict, arrays: dict) -> np.ndarray:
    """(R, filter): the absorbing part of each filter's face-on depth, read from the frame's transmission."""
    albedo = np.asarray(header["components"]["dust_extinction"]["albedo"])
    return (1.0 - albedo) * -np.log(arrays["dust_extinction"])


def test_the_frame_s_quadrature_over_directions_is_the_slab_s_escape():
    """The frame's direction average against the stage's closed form, over the optical depths the disc spans."""
    tau = np.geomspace(1e-6, 30.0, 400)
    assert np.abs(removed_share(tau) - slab_absorbed_fraction(tau)).max() < 1e-10  # 2.2e-11 at S39


def test_the_frame_s_dust_removes_what_it_emits(full, model):
    """V2's gate: what the frame's dust absorbs equals what it emits, both read back from the render arrays."""
    header, arrays = full_render(full, model.name, [*SETS["rgb"]["curves"], V_ROW])
    f = scalars(full, model.name, "disc_surface_brightness", "dust_absorbed_luminosity", "dust_infrared_luminosity",
                "dust_absorbed_surface_brightness")
    area = ring_areas(header)
    share = removed_share(absorbing_depth(header, arrays))  # (R, filter)
    # Per filter over the image: the light each filter loses, as a share of that filter's light (R, V, B, V row).
    light = arrays["stars"].mean(axis=1) * area[:, None]
    per_filter = (light * share).sum(axis=0) / light.sum(axis=0)
    print(model.name, "removed share per filter", per_filter)
    assert per_filter == pytest.approx(REMOVED_SHARE[model.name], abs=2e-6)
    # Commensurable: the V row's share of the bolometric light, ring by ring, is the absorbed field itself ...
    absorbed = share[:, 3] * f["disc_surface_brightness"]
    lit = f["dust_absorbed_surface_brightness"] > 1e-9 * f["dust_absorbed_surface_brightness"].max()
    # (to the direction quadrature's 2e-11 in the share, 5.4e-9 of it where the outer disc's tau is 1e-4)
    assert absorbed[lit] == pytest.approx(f["dust_absorbed_surface_brightness"][lit], rel=1e-8)
    # ... and over the image, against the published total.
    frame_absorbed = float((absorbed * area).sum())
    # The infrared, through the ir set: the frame's thermal emission over the image, every filter summed.
    ir_header, ir = full_render(full, model.name, IR)
    per_ir = (ir["dust_thermal"] * area[:, None]).sum(axis=0)
    frame_emitted = float(per_ir.sum())
    print(model.name, "absorbed", frame_absorbed / f["dust_absorbed_luminosity"], "emitted",
          frame_emitted / f["dust_infrared_luminosity"], "per ir filter", per_ir)
    assert per_ir[1:].sum() < 1e-12 * per_ir[0]  # J, H and K see none of 20 K dust
    assert abs(frame_emitted / frame_absorbed - 1.0) < BALANCE_TOLERANCE
    assert abs(frame_absorbed / f["dust_absorbed_luminosity"] - 1.0) < BALANCE_TOLERANCE
    assert abs(frame_emitted / f["dust_infrared_luminosity"] - 1.0) < BALANCE_TOLERANCE
    assert frame_absorbed / f["dust_absorbed_luminosity"] == pytest.approx(MEASURED_ABSORBED[model.name], abs=2e-6)
    assert frame_emitted / f["dust_infrared_luminosity"] == pytest.approx(MEASURED_EMITTED[model.name], abs=2e-6)
    # What the TIR box leaves out, ring by ring from the arrays alone: its share of each ring's published Σ_IR.
    sigma_ir = scalars(full, model.name, "dust_infrared_surface_brightness")["dust_infrared_surface_brightness"]
    hot = sigma_ir > 0
    coverage = float((ir["dust_thermal"][hot, 0] * area[hot]).sum() / (sigma_ir[hot] * area[hot]).sum())
    print(model.name, "outside the TIR box", 1.0 - coverage)
    assert 1.0 - coverage == pytest.approx(TIR_OUTSIDE[model.name], abs=2e-6)


def test_the_grey_absorption_against_the_curve_in_the_frame(full):
    """A record, not a gate (debt of S31: "grey at V", wrong in both directions): through eight boxes tiling the
    frame's stellar continuum, 0.1–30 µm, the light the frame's dust removes with the grain model's own curve
    against the light it would remove grey at the V row. The frame's continuum lacks the young stars' ultraviolet
    (0.708 of the light, S38), where the curve absorbs most, so the ratio errs low by an unknown amount."""
    edges = np.geomspace(1000.0, 300_000.0, 9)
    tiles = [{"name": f"t{k}", "shape": "box", "centre": 0.5 * (edges[k] + edges[k + 1]), "width": edges[k + 1] - edges[k]}
             for k in range(8)]
    header, arrays = full_render(full, "basic", tiles)
    v_header, v_arrays = full_render(full, "basic", [V_ROW])
    area = ring_areas(header)
    light = arrays["stars"].mean(axis=1) * area[:, None]
    curve = float((light * removed_share(absorbing_depth(header, arrays))).sum())
    grey = float((light * removed_share(absorbing_depth(v_header, v_arrays))[:, :1]).sum())
    print("curve over grey", curve / grey)
    assert curve / grey == pytest.approx(CURVE_OVER_GREY, abs=2e-6)


def test_the_frame_s_light_is_conserved_by_its_scattering(full):
    """The frame's three fates of the starlight, read back from the arrays over every direction, add to the light:
    what escapes its mixed slab unextinguished (1 minus the frame's removed share at the full depth), what
    ``dust_scattered`` carries (all directions: the phase table averages to one), and what the dust absorbs. So
    the light that leaves is the light the dust stage says escapes, 1 − a(τ_abs), in every filter.

    **The record (S39).** The ruling's first form, optically thin single scattering τ_sca × the stars, measured
    here against the scattered light the route returns: twelve times it over the whole galaxy, because the disc's
    centre has τ_sca ≈ 30, where a thin scatterer throws thirty times the light it holds (A_V 50 at the centre)."""
    header, arrays = full_render(full, "basic", [*SETS["rgb"]["curves"], V_ROW])
    area = ring_areas(header)
    light = arrays["stars"].mean(axis=1)  # (R, filter)
    tau = -np.log(arrays["dust_extinction"])
    escaped = light * (1.0 - removed_share(tau))
    scattered = arrays["dust_scattered"].mean(axis=1)
    absorbed = light * removed_share(absorbing_depth(header, arrays))
    assert escaped + scattered + absorbed == pytest.approx(light, rel=1e-9)
    f = scalars(full, "basic", "dust_scattering_optical_depth")
    thin = spectra.scattering_depth(f["dust_scattering_optical_depth"], spectra.parse_curves([V_ROW]))[:, 0] * light[:, 3]
    ratio = float((thin * area).sum() / (scattered[:, 3] * area).sum())
    print("thin over slab", ratio)
    assert ratio == pytest.approx(THIN_OVER_SLAB, abs=2e-6)


# **RENDER_PLAN Part 3's check 2: the face-on profile.** Σ_V(R) read from the frame's level-0 region cells —
# each cell's mean the render takes by bilinear sub-sampling at 8 × 8 midpoints, R-weighted (``_cell_means``) —
# averaged round each ring of cells and turned from the table's V response into solar V luminosities, against
# the published disc_surface_brightness_v averaged exactly over the same ring (its grid values joined linearly,
# as the sub-sampling joins them, integrated R dR on 20 001 points). **The tolerance is derived per ring, not
# chosen**: the midpoint rule on 8 points of a piecewise-linear profile times R errs by at most h²/8 · |Δslope|·R
# at each kink it straddles plus h²/24 · |2 slope| over each linear piece (h the ring's width over 8), as a share
# of the ring's light; the azimuthal sub-sampling (256 points round a ring against 360 grid cells) errs by what
# it does to the published contrast's own ring mean; the spectrum's band consistency adds 6e-5 mag (S38).


def test_the_face_on_profile_is_the_published_one(full, model):
    from galaxy.api.service import RENDER_CELL_SAMPLES
    from galaxy.stages import systems

    V = spectra.band_curve("V")
    got = full.handle("/api/render", {"model": [model.name], "filters": [json.dumps([V.json()])], "level": ["0"]})
    header, arrays = wire.decode(got.body)
    f = scalars(full, model.name, "disc_surface_brightness_v", "pattern_density_contrast")
    lam = V.grid()
    zero = float(band_nu_l_nu(np.array(1.0), "V")) / PASSBANDS["V"].reference
    m_sun = full.models.get(model.name).constants["SOLAR_ABSOLUTE_MAGNITUDE_V"].value
    sigma_v = arrays["stars"][:, 0] / np.trapezoid(V.at(lam), lam) / zero * 10.0 ** (0.4 * m_sun)
    grid = full.grid
    R, dR, published = grid.R, grid.axes["R"].width, f["disc_surface_brightness_v"]
    bounds = [systems.cell_bounds(R, int(c), 0) for c in arrays["cell"]]
    slope = np.diff(published) / dR
    # The azimuthal sub-sampling's own error: the published contrast's ring mean at the 256 sample azimuths.
    n_phi = f["pattern_density_contrast"].shape[1]
    sectors = len({b["phi_lo"] for b in bounds})
    p = (np.arange(sectors * RENDER_CELL_SAMPLES) + 0.5) * 2.0 * math.pi / (sectors * RENDER_CELL_SAMPLES)
    y = p / (2.0 * math.pi / n_phi) - 0.5
    j0 = np.floor(y).astype(int)
    fy = y - j0
    c = f["pattern_density_contrast"]
    sampled = ((1.0 - fy) * c[:, j0 % n_phi] + fy * c[:, (j0 + 1) % n_phi]).mean(axis=1)
    phi_error = np.abs(sampled / c.mean(axis=1) - 1.0)
    worst = 0.0
    for lo, hi in sorted({(b["r_lo"], b["r_hi"]) for b in bounds}):
        frame = sigma_v[[k for k, b in enumerate(bounds) if b["r_lo"] == lo]].mean()
        rr = np.linspace(lo, hi, 20_001)
        exact = np.trapezoid(np.interp(rr, R, published) * rr, rr) / np.trapezoid(rr, rr)
        h = (hi - lo) / RENDER_CELL_SAMPLES
        nodes = (R > lo) & (R < hi)
        kinks = np.abs(np.diff(slope))[nodes[1:-1]] * R[1:-1][nodes[1:-1]]
        near = (R >= lo - dR) & (R <= hi + dR)
        pieces = 2.0 * np.abs(slope[near[:-1]]).max() * (hi - lo)
        light = exact * 0.5 * (hi + lo) * (hi - lo)
        bound = (h**2 / 8.0 * kinks.sum() + h**2 / 24.0 * pieces) / light + phi_error[near].max() + 5.5e-5
        rel = frame / exact - 1.0
        assert abs(rel) <= bound, (lo, hi, rel, bound)
        if exact > 1e-3 * published.max():
            worst = max(worst, abs(rel))
    print(model.name, "worst ring inside the disc", worst)
    assert worst == pytest.approx(PROFILE_WORST[model.name], abs=1e-6)


# --- the route --------------------------------------------------------------------------------


def test_the_render_runs_the_closure_of_what_it_reads_and_names_it(small, model):
    got = small.handle("/api/render", {"model": [model.name], "filters": [curves("rgb")]})
    assert got.status == 200
    assert "light" in got.stages and "nebular" in got.stages
    assert "systems" not in got.stages and "planets" not in got.stages  # no catalogue is materialised
    header, arrays = wire.decode(got.body)
    assert header["stages"] == list(got.stages)
    for name in ("stars", "halpha_hii", "dust_scattered"):
        assert arrays[name].shape == (48, 36, 3) and header["axes"][name] == ["R", "phi", "filter"], name
    for name in ("halpha_dig", "dust_extinction", "dust_thermal"):
        assert arrays[name].shape == (48, 3) and header["axes"][name] == ["R", "filter"], name
    assert set(arrays) == {"stars", "halpha_hii", "halpha_dig", "dust_extinction", "dust_scattered", "dust_thermal"}


def test_the_stars_are_the_published_spectrum_placed_by_the_contrast(small):
    header, arrays = render(small, "basic", "rgb", white="6500")
    disc = [f"disc_sed_{b.lower()}" for b in BANDS]
    bulge_names = [f"bulge_sed_{b.lower()}" for b in BANDS]
    f = scalars(small, "basic", *disc, *bulge_names, "disc_light_temperature", "pattern_density_contrast", "bulge_light_temperature")
    parsed = spectra.parse_curves(SETS["rgb"]["curves"])
    per_ring = spectra.stellar_response(np.stack([f[n] for n in disc], axis=-1), f["disc_light_temperature"], parsed)
    want = per_ring[:, None, :] * np.maximum(f["pattern_density_contrast"], 0.0)[..., None]
    assert np.allclose(arrays["stars"], want, rtol=1e-14, atol=0.0)
    bulge = spectra.stellar_response(np.array([f[n] for n in bulge_names]), np.array(f["bulge_light_temperature"]), parsed)
    assert header["bulge"] == pytest.approx(bulge.tolist(), rel=1e-14)
    assert header["components"]["stars"]["bands"] == list(BANDS)
    assert header["white"]["response"] == pytest.approx(spectra.blackbody_response(parsed, np.array([6500.0]))[0].tolist(), rel=1e-14)
    assert header["set"] == "rgb" and [c["name"] for c in header["filters"]] == ["R", "V", "B"]


def test_a_window_is_the_slice_of_the_whole_and_wraps_at_phi_zero(small):
    _, whole = render(small, "basic", "rgb")
    header, part = render(small, "basic", "rgb", r_min="7", r_max="9", phi_min="6.0", phi_max="6.6")
    r, p = header["window"]["R"], header["window"]["phi"]
    assert p["wraps"] and p["first"] + p["n"] > 36
    rows = np.arange(r["first"], r["first"] + r["n"])
    cols = (p["first"] + np.arange(p["n"])) % 36
    for name in ("stars", "halpha_hii", "dust_scattered"):
        assert np.array_equal(part[name], whole[name][rows][:, cols]), name
    for name in ("halpha_dig", "dust_extinction", "dust_thermal"):
        assert np.array_equal(part[name], whole[name][rows]), name
    # A window narrower than a cell still selects the cell holding it.
    header, one = render(small, "basic", "rgb", r_min="8.1", r_max="8.1", phi_min="1.0", phi_max="1.0")
    assert one["stars"].shape == (1, 1, 3)


def test_region_cells_carry_their_mean_and_the_cells_integrate_to_the_frame(small):
    header, frame = render(small, "basic", "rgb")
    total = (frame["stars"] * cell_areas(header)[..., None]).sum(axis=(0, 1))
    header, cells = render(small, "basic", "rgb", level="0")
    assert header["window"]["cells"]["count"] == 1024 and cells["cell"].tolist() == list(range(1024))
    from galaxy.stages import systems

    bounds = [systems.cell_bounds(small.grid.R, c, 0) for c in range(1024)]
    area = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * PC_PER_KPC**2
    by_cells = (cells["stars"] * area[:, None]).sum(axis=0)
    # The cells span R[0]..R[-1], the frame 0..R_max: they differ by the half-cells at the ends and the
    # quadrature, 1.4e-3 on this coarse grid (4e-5 on the default one, S38).
    assert by_cells == pytest.approx(total, rel=3e-3)
    header, deep = render(small, "basic", "rgb", level="2", r_min="7", r_max="9", phi_min="0", phi_max="0.4")
    n = header["window"]["cells"]["count"]
    assert deep["stars"].shape == (n, 3) and np.all(deep["stars"] > 0)
    for name in ("halpha_hii", "halpha_dig", "dust_extinction", "dust_scattered", "dust_thermal"):
        assert deep[name].shape == (n, 3) and header["axes"][name] == ["cell", "filter"], name
    assert np.all((deep["dust_extinction"] > 0) & (deep["dust_extinction"] < 1))


def test_float32_halves_the_payload_and_keeps_the_numbers(small):
    _, f8 = render(small, "basic", "rgb")
    _, f4 = render(small, "basic", "rgb", precision="f4")
    assert f4["stars"].dtype == np.float32
    assert np.array_equal(f4["stars"], f8["stars"].astype(np.float32))


@pytest.mark.parametrize(
    "query, fragment",
    [
        ({}, "filters= is the viewer's filter set"),
        ({"filters": ["rgb"]}, "must be a JSON list"),  # the model holds no named set (§2a)
        ({"filters": ["[]"]}, "1 to 8 curves"),
        ({"filters": ['[{"name": "x", "shape": "lorentzian", "centre": 5000, "fwhm": 10}]']}, "shape must be one of"),
        ({"filters": ['[{"name": "x", "shape": "gaussian", "centre": 500, "fwhm": 10}]']}, "centre must lie"),
        ({"filters": ['[{"name": "x", "shape": "box", "centre": 5000, "fwhm": 10}]']}, "unknown keys"),
        ({"filters": ['[{"name": "x", "shape": "sampled", "wavelength": [5000, 4000], "transmission": [1, 1]}]']}, "must increase"),
        ({"filters": [curves("rgb")], "white": ["10"]}, "white="),
        ({"filters": [curves("rgb")], "precision": ["f2"]}, "precision="),
        ({"filters": [curves("rgb")], "level": ["9"]}, "level="),
    ],
)
def test_a_bad_render_request_is_refused_and_says_why(small, query, fragment):
    got = small.handle("/api/render", query)
    assert got.status == 400 and fragment in got.json()["error"]
    assert got.stages == ()


# --- the spectrum function --------------------------------------------------------------------


@pytest.mark.parametrize("kelvin", [2500.0, 5772.0, 12000.0, 40000.0])
def test_the_blackbody_shape_carries_unit_light(kelvin):
    lam = np.geomspace(50.0, 1e7, 400_000)
    assert np.trapezoid(spectra.planck_share(lam, np.array(kelvin)), lam) == pytest.approx(1.0, abs=2e-6)


def test_a_sampled_curve_is_the_curve_it_samples():
    gaussian = {"name": "g", "shape": "gaussian", "centre": 5448.0, "fwhm": 840.0}
    parsed = spectra.parse_curves([gaussian])[0]
    lam = np.linspace(5448.0 - 4 * 840.0, 5448.0 + 4 * 840.0, 3001)
    sampled = {"name": "s", "shape": "sampled", "wavelength": lam.tolist(), "transmission": parsed.at(lam).tolist()}
    both = spectra.parse_curves([gaussian, sampled])
    got = spectra.blackbody_response(both, np.array([4000.0, 6500.0, 15000.0]))
    assert got[:, 1] == pytest.approx(got[:, 0], rel=1e-6)
    assert spectra.line_response(both, 6562.8) == pytest.approx([parsed.at(np.array([6562.8]))[0]] * 2, rel=1e-4)


def test_a_redder_temperature_is_redder_through_the_rgb_set():
    share = spectra.blackbody_response(spectra.parse_curves(SETS["rgb"]["curves"]), np.array([3500.0, 6500.0, 20000.0]))
    red_over_blue = share[:, 0] / share[:, 2]
    assert red_over_blue[0] > red_over_blue[1] > red_over_blue[2]


def test_no_light_is_zero_and_light_without_a_temperature_is_missing():
    parsed = spectra.parse_curves(SETS["rgb"]["curves"])
    got = spectra.blackbody_stellar_response(np.array([0.0, 5.0, 5.0]), np.array([np.nan, np.nan, 5000.0]), parsed)
    assert np.all(got[0] == 0.0) and np.all(np.isnan(got[1])) and np.all(got[2] > 0.0)
    # The spectrum: no light is zero everywhere; light with no temperature is missing wherever a curve
    # reaches a tail (the rgb Gaussians' ±4 FWHM reach below U) and present where one stays inside U-K.
    sed = np.array([np.zeros(8), np.linspace(1.0, 2.0, 8), np.linspace(1.0, 2.0, 8)])
    kelvin = np.array([np.nan, np.nan, 5000.0])
    got = spectra.stellar_response(sed, kelvin, parsed)
    assert np.all(got[0] == 0.0) and np.all(np.isnan(got[1])) and np.all(got[2] > 0.0)
    inside = spectra.parse_curves([{"name": "v", "shape": "box", "centre": 5500.0, "width": 800.0}])
    assert np.isfinite(spectra.sed_response(sed, kelvin, inside)[1, 0])


def test_the_joined_spectrum_passes_through_its_points_and_its_tails_meet_them():
    sed = np.array([2.0, 3.0, 3.5, 3.2, 2.8, 1.9, 1.2, 0.7])
    at = spectra.sed_density(spectra.SED_WAVELENGTHS, sed, np.array(4500.0))
    assert at == pytest.approx(sed / spectra.SED_WAVELENGTHS, rel=1e-12)
    eps = 1e-6
    for end in (0, -1):
        lam = spectra.SED_WAVELENGTHS[end] * np.array([1.0 - eps, 1.0 + eps])
        inside_and_tail = spectra.sed_density(lam, sed, np.array(4500.0))
        assert inside_and_tail[0] == pytest.approx(inside_and_tail[1], rel=1e-4)  # continuous at U and at K


def test_the_viewer_s_sets_are_curves_the_model_takes():
    for name, entry in SETS.items():
        parsed = spectra.parse_curves(entry["curves"])
        assert len(parsed) == 3, name
        assert "[inferred]" in entry["about"] or "[inferred]" in FILTERS["about"], name
    assert 1000.0 <= FILTERS["white"]["kelvin"] <= 100_000.0
    # The measured set (S39): the TIR box and J, H, K at the model's own band definitions.
    ir = spectra.parse_curves(IR)
    assert [c.name for c in ir] == ["TIR", "K", "H", "J"] and "[inferred]" in FILTERS["measured"]["ir"]["about"]
    assert (ir[0].centre - 0.5 * ir[0].width, ir[0].centre + 0.5 * ir[0].width) == (80_000.0, 10_000_000.0)
    for curve in ir[1:]:
        assert (curve.centre, curve.width) == (PASSBANDS[curve.name].reference, PASSBANDS[curve.name].fwhm)


# --- the dust's spectrum functions (S39) --------------------------------------------------------------


def test_the_grain_table_rows_are_the_file_s():
    """The transcription checks itself: every row's absorption cross-section two ways, K_abs × M_dust/H against
    (1 − albedo) C_ext, agrees to the four printed digits (worst 6.4e-4, at 0.178 µm); and the rows the dust
    stage's S31 constants quote are the rows here, digit for digit."""
    g = np.array(spectra.GRAIN_TABLE)
    assert np.all(np.diff(g[:, 0]) > 0)
    identity = g[:, 4] * spectra.GRAIN_DUST_MASS_PER_H / ((1.0 - g[:, 1]) * g[:, 3]) - 1.0
    assert np.abs(identity).max() < 1.5e-3
    c = {k: v.value for k, v in Service().models.get("basic").constants.items()}
    row = {r[0]: r for r in spectra.GRAIN_TABLE}
    assert (row[0.547][1], row[0.547][2]) == (c["DUST_ALBEDO_V"], c["DUST_SCATTERING_G"])
    assert row[0.151356][3] / row[0.547][3] == c["DUST_EXTINCTION_RATIO_FUV"] and row[0.151356][1] == c["DUST_ALBEDO_FUV"]
    assert (row[155.9][0], row[155.9][4]) == (c["DUST_OPACITY_WAVELENGTH"], c["DUST_OPACITY_REFERENCE"])


def test_the_extinction_curve_at_the_viewer_s_filters():
    """A_λ/A_V read at each filter's reference wavelength, pinned: the rgb set's R, V, B and the ir set's J, H, K.
    B over V is 1.302, a monochromatic R_V of 3.31 against the broadband 3.1 the dust stage's E(B − V) divides by."""
    ratio = spectra.extinction_ratio(np.array([6498.09, 5477.70, 4371.07, 12303.17, 16396.38, 22027.46]))
    assert ratio == pytest.approx([0.793528, 0.998188, 1.302122, 0.298354, 0.186688, 0.113246], abs=2e-6)
    assert spectra.extinction_ratio(np.array(5470.0)) == pytest.approx(1.0, abs=1e-14)
    assert spectra.albedo(np.array([5470.0, 1513.56])) == pytest.approx([0.6774, 0.4068], abs=1e-15)
    # A sampled curve is read at its transmission-weighted mean: a symmetric one at its centre.
    lam = np.linspace(5000.0, 6000.0, 101)
    sampled = spectra.parse_curves([{"name": "s", "shape": "sampled", "wavelength": lam.tolist(),
                                     "transmission": np.exp(-(((lam - 5500.0) / 200.0) ** 2)).tolist()}])[0]
    assert sampled.reference() == pytest.approx(5500.0, rel=1e-9)


def test_the_dust_arrays_are_the_published_fields_through_the_curve(small):
    header, arrays = render(small, "basic", "rgb")
    f = scalars(small, "basic", "dust_extinction_v", "dust_scattering_optical_depth", "dust_scattering_asymmetry")
    parsed = spectra.parse_curves(SETS["rgb"]["curves"])
    ratio = spectra.extinction_ratio(spectra.filter_references(parsed))
    assert np.allclose(arrays["dust_extinction"], 10.0 ** (-0.4 * f["dust_extinction_v"][:, None] * ratio), rtol=1e-14, atol=0)
    # Through the table's own V row the scattering depth is the published field itself.
    one = spectra.parse_curves([V_ROW])
    assert spectra.scattering_depth(f["dust_scattering_optical_depth"], one)[:, 0] == pytest.approx(
        f["dust_scattering_optical_depth"], rel=1e-14)
    tau = spectra.scattering_depth(f["dust_scattering_optical_depth"], parsed)
    depth = spectra.extinction_depth(f["dust_extinction_v"], parsed)
    assert np.exp(-depth) == pytest.approx(arrays["dust_extinction"], rel=1e-14)
    share = spectra.scattered_share(depth, tau)
    assert np.allclose(arrays["dust_scattered"], share[:, None, :] * arrays["stars"], rtol=1e-12, atol=0)
    assert np.all((share >= 0.0) & (share < 1.0))
    phase = header["components"]["dust_scattered"]["phase"]
    assert phase == spectra.phase_table(f["dust_scattering_asymmetry"])
    # 20 K dust puts nothing measurable through an optical filter.
    sigma_ir = scalars(small, "basic", "dust_infrared_surface_brightness")["dust_infrared_surface_brightness"]
    assert np.all(arrays["dust_thermal"] <= 1e-30 * sigma_ir.max())


@pytest.mark.parametrize("g", [0.0, 0.5383, 0.9])
def test_the_phase_function_moves_light_and_makes_none(g):
    # Henyey-Greenstein over the sphere is one; the disc's factor, over every view uniformly in |cos i|, is one.
    mu = np.linspace(-1.0, 1.0, 200_001)
    assert 2.0 * math.pi * np.trapezoid(spectra.henyey_greenstein(g, mu), mu) == pytest.approx(1.0, abs=2e-4 if g == 0.9 else 1e-8)
    views = np.linspace(0.0, 1.0, 20_001)
    assert np.trapezoid(spectra.disc_phase(g, views), views) == pytest.approx(1.0, abs=1e-8)
    assert spectra.disc_phase(g, np.array(1.0)) == pytest.approx((1 - g * g) / (1 + g * g) ** 1.5, rel=1e-12)
    table = spectra.phase_table(g)
    assert len(table["factor"]) == spectra.PHASE_POINTS and table["cos_view"][0] == 0.0 and table["cos_view"][-1] == 1.0


@pytest.mark.parametrize("kelvin", [3.0, 8.0, 19.5, 40.0])
def test_the_thermal_shape_carries_the_dust_stage_s_power(kelvin):
    """The modified blackbody per Å integrates to one over the dust stage's own span, 1 µm – 1 m, so a curve
    holding all of it returns Σ_IR (the frame's TIR box holds all but what lies outside 8–1000 µm)."""
    lam = np.geomspace(1.0e4, 1.0e10, 400_001)
    share = spectra.thermal_share(lam, np.array(kelvin), 16.43, 155.9, 1.62)
    assert np.trapezoid(share, lam) == pytest.approx(1.0, abs=1e-6)
    assert np.all(spectra.thermal_share(lam[:5], np.array([np.nan, 0.0]), 16.43, 155.9, 1.62) == 0.0)
