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
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.stages import spectra
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.dust import slab_absorbed_fraction
from galaxy.stages.photometry import BANDS, PASSBANDS, band_nu_l_nu, lookup, lookup_columns, population_over

ROOT = Path(__file__).resolve().parents[1]
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
INSTRUMENTS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "instruments.json").read_text(encoding="utf-8"))
SETS = {**FILTERS["sets"], **INSTRUMENTS["sets"]}  # the named instruments since S42 (tools/fetch_filters.py)
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)

# The gate's tolerance, stated (module docstring), and what the second cut measured at S38.
TOLERANCE = 1e-3
MEASURED_B_V = 0.630641  # the table's 0.630552
MEASURED_M_V = -21.216042  # the table's -21.215871
# The first cut's record (S38): one blackbody at the colour temperature.
FIRST_CUT_B_V = 0.642807
FIRST_CUT_M_V = -21.928533
# The record beside the gate (S39): the same frame with the dust composed face-on (``face_on``).
# Keyed per model, "basic" deliberately (S46, D197); the render tests below run the default model.
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
    table = scalars(full, DEFAULT_MODEL, *(f"absolute_magnitude_{b.lower()}" for b in BANDS))
    for k, band in enumerate(BANDS):
        assert band_magnitude(total[k], band) == pytest.approx(table[f"absolute_magnitude_{band.lower()}"], abs=TOLERANCE), band


def per_ring_residuals(api: Service, iterations: int | None) -> np.ndarray:
    """(rings with light, 8): each band's mean through its curve against the table's value at that ring, mag;
    the spectrum's anchors as published (``iterations`` 0) or made band-consistent."""
    names = [f"disc_sed_{b.lower()}" for b in BANDS]
    f = scalars(api, DEFAULT_MODEL, *names, "disc_light_temperature")
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
    f = scalars(full, DEFAULT_MODEL, "disc_surface_brightness", "disc_light_temperature", "bulge_luminosity", "bulge_light_temperature",
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
    formed = np.asarray(f["stars_formed_history"]) / (1.0 - full.models.get(DEFAULT_MODEL).constants["RETURN_FRACTION"].value)
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
    published = scalars(full, DEFAULT_MODEL, "disc_luminosity")["disc_luminosity"]
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
    # The lines the model does not publish are named, not drawn dark (rule B9): since S42 it publishes all six.
    assert header["absent"]["lines"] == []  # Hbeta and the four forbidden lines until S42


def test_the_other_lines_are_their_fields_through_each_curve_at_their_wavelengths(full, model):
    """S42 (the owner's word on D184): the HII regions' Hbeta and forbidden lines, each through each curve at its
    own wavelength, summed and placed as the regions' Halpha is; the diffuse gas's Hbeta per ring. Through the
    Hubble palette's boxes [S II] lands in red, [O III] in blue, and nothing but Halpha in the Halpha box (the
    [N II] line at 6583.5 A sits 6 A outside its 30 A)."""
    header, arrays = render(full, model.name, "sho")
    names = ("hbeta", "oiii_5007", "nii_6583", "sii_6716", "sii_6731")
    f = scalars(full, model.name, *(f"{n}_surface_brightness_hii" for n in names), "hbeta_surface_brightness_dig",
                "halpha_surface_brightness_hii", "pattern_density_contrast")
    placed = np.maximum(f["pattern_density_contrast"], 0.0)
    lines = header["components"]["lines_hii"]["lines"]
    assert {n: lines[n]["transmission"] for n in names} == {
        "hbeta": [0.0, 0.0, 0.0], "oiii_5007": [0.0, 0.0, 1.0], "nii_6583": [0.0, 0.0, 0.0],
        "sii_6716": [1.0, 0.0, 0.0], "sii_6731": [1.0, 0.0, 0.0],
    }
    sii = (f["sii_6716_surface_brightness_hii"] + f["sii_6731_surface_brightness_hii"])[:, None] * placed
    assert np.allclose(arrays["lines_hii"][..., 0], sii, rtol=1e-12, atol=0.0)
    assert not arrays["lines_hii"][..., 1].any()
    assert np.allclose(arrays["lines_hii"][..., 2], f["oiii_5007_surface_brightness_hii"][:, None] * placed, rtol=1e-12, atol=0.0)
    assert not arrays["lines_dig"].any()  # Hbeta falls in none of the three boxes
    assert header["layers"]["lines_hii"] == header["layers"]["halpha_hii"] and header["layers"]["lines_dig"] == header["layers"]["halpha_dig"]
    # Through the broadband set Hbeta lands in B, in both layers.
    header, arrays = render(full, model.name, "rgb")
    b = header["components"]["lines_dig"]["lines"]["hbeta"]["transmission"]
    assert b[2] == pytest.approx(0.4762, abs=1e-4) and b[2] > b[1] > b[0] and np.allclose(arrays["lines_dig"], f["hbeta_surface_brightness_dig"][:, None] * np.array(b), rtol=1e-12, atol=0.0)
    # Every HII line is its ring's Halpha times a ratio the census's regions set: finite and non-negative.
    for n in names:
        x = f[f"{n}_surface_brightness_hii"]
        assert np.all(np.isfinite(x) & (x >= 0.0)) and np.all((x > 0) <= (f["halpha_surface_brightness_hii"] > 0)), n


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
# Keyed per model, "basic" deliberately (S46, D197).
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
    header, arrays = full_render(full, DEFAULT_MODEL, tiles)
    v_header, v_arrays = full_render(full, DEFAULT_MODEL, [V_ROW])
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
    header, arrays = full_render(full, DEFAULT_MODEL, [*SETS["rgb"]["curves"], V_ROW])
    area = ring_areas(header)
    light = arrays["stars"].mean(axis=1)  # (R, filter)
    tau = -np.log(arrays["dust_extinction"])
    escaped = light * (1.0 - removed_share(tau))
    scattered = arrays["dust_scattered"].mean(axis=1)
    absorbed = light * removed_share(absorbing_depth(header, arrays))
    assert escaped + scattered + absorbed == pytest.approx(light, rel=1e-9)
    f = scalars(full, DEFAULT_MODEL, "dust_scattering_optical_depth")
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
    for name in ("stars", "halpha_hii", "lines_hii", "dust_scattered"):
        assert arrays[name].shape == (48, 36, 3) and header["axes"][name] == ["R", "phi", "filter"], name
    for name in ("halpha_dig", "lines_dig", "dust_extinction", "dust_thermal"):
        assert arrays[name].shape == (48, 3) and header["axes"][name] == ["R", "filter"], name
    assert set(arrays) == {"stars", "halpha_hii", "lines_hii", "halpha_dig", "lines_dig", "dust_extinction", "dust_scattered", "dust_thermal"}


def test_the_stars_are_the_published_spectrum_placed_by_the_contrast(small):
    header, arrays = render(small, DEFAULT_MODEL, "rgb", white="6500")
    disc = [f"disc_sed_{b.lower()}" for b in BANDS]
    bulge_names = [f"bulge_sed_{b.lower()}" for b in BANDS]
    f = scalars(small, DEFAULT_MODEL, *disc, *bulge_names, "disc_light_temperature", "pattern_density_contrast", "bulge_light_temperature")
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
    _, whole = render(small, DEFAULT_MODEL, "rgb")
    header, part = render(small, DEFAULT_MODEL, "rgb", r_min="7", r_max="9", phi_min="6.0", phi_max="6.6")
    r, p = header["window"]["R"], header["window"]["phi"]
    assert p["wraps"] and p["first"] + p["n"] > 36
    rows = np.arange(r["first"], r["first"] + r["n"])
    cols = (p["first"] + np.arange(p["n"])) % 36
    for name in ("stars", "halpha_hii", "lines_hii", "dust_scattered"):
        assert np.array_equal(part[name], whole[name][rows][:, cols]), name
    for name in ("halpha_dig", "lines_dig", "dust_extinction", "dust_thermal"):
        assert np.array_equal(part[name], whole[name][rows]), name
    # A window narrower than a cell still selects the cell holding it.
    header, one = render(small, DEFAULT_MODEL, "rgb", r_min="8.1", r_max="8.1", phi_min="1.0", phi_max="1.0")
    assert one["stars"].shape == (1, 1, 3)


def test_region_cells_carry_their_mean_and_the_cells_integrate_to_the_frame(small):
    header, frame = render(small, DEFAULT_MODEL, "rgb")
    total = (frame["stars"] * cell_areas(header)[..., None]).sum(axis=(0, 1))
    header, cells = render(small, DEFAULT_MODEL, "rgb", level="0")
    assert header["window"]["cells"]["count"] == 1024 and cells["cell"].tolist() == list(range(1024))
    from galaxy.stages import systems

    bounds = [systems.cell_bounds(small.grid.R, c, 0) for c in range(1024)]
    area = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * PC_PER_KPC**2
    by_cells = (cells["stars"] * area[:, None]).sum(axis=0)
    # The cells span R[0]..R[-1], the frame 0..R_max: they differ by the half-cells at the ends and the
    # quadrature, 1.4e-3 on this coarse grid (4e-5 on the default one, S38).
    assert by_cells == pytest.approx(total, rel=3e-3)
    header, deep = render(small, DEFAULT_MODEL, "rgb", level="2", r_min="7", r_max="9", phi_min="0", phi_max="0.4")
    n = header["window"]["cells"]["count"]
    assert deep["stars"].shape == (n, 3) and np.all(deep["stars"] > 0)
    for name in ("halpha_hii", "lines_hii", "halpha_dig", "lines_dig", "dust_extinction", "dust_scattered", "dust_thermal"):
        assert deep[name].shape == (n, 3) and header["axes"][name] == ["cell", "filter"], name
    assert np.all((deep["dust_extinction"] > 0) & (deep["dust_extinction"] < 1))


def test_float32_halves_the_payload_and_keeps_the_numbers(small):
    _, f8 = render(small, DEFAULT_MODEL, "rgb")
    _, f4 = render(small, DEFAULT_MODEL, "rgb", precision="f4")
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


def test_air_to_vacuum_is_morton_1991():
    """n − 1 by Morton 1991's formula (as STScI cites it, WFC3 IHB section 6.5), worked by hand at σ = 2 µm⁻¹:
    6432.8 + 2 949 810/142 + 25 540/37 = 27 896.4, so 2.7896e-4 at 5000 Å; 2.7895e-4 at [O III] 5006.8 and
    2.7624e-4 at Hα 6562.8. S43 recorded 2.792e-4 at 5000 Å and 2.767e-4 at 6600 Å (the formula gives 2.7620e-4
    there): neither reproduces from the formula as D195 writes it, and the line transmissions do not feel the
    difference (2e-7 of 5007 Å is 0.001 Å)."""
    assert spectra.air_to_vacuum(5000.0) / 5000.0 - 1.0 == pytest.approx(2.78964e-4, abs=1e-9)
    assert spectra.air_to_vacuum(5006.8) / 5006.8 - 1.0 == pytest.approx(2.7895e-4, abs=5e-9)
    assert spectra.air_to_vacuum(6562.8) / 6562.8 - 1.0 == pytest.approx(2.7624e-4, abs=5e-9)
    assert spectra.air_to_vacuum(6600.0) / 6600.0 - 1.0 == pytest.approx(2.7620e-4, abs=5e-9)


def test_a_vacuum_curve_reads_the_line_at_its_vacuum_wavelength():
    """A 1 Å box centred on Hα's vacuum wavelength: declared vacuum it passes the air line whole, declared air
    (or saying nothing) it misses it, 1.8 Å away. The key is echoed as sent, air when not sent."""
    box = {"name": "b", "shape": "box", "centre": spectra.air_to_vacuum(6562.8), "width": 1.0}
    vacuum, air, unsaid = spectra.parse_curves([box | {"wavelengths": "vacuum"}, box | {"wavelengths": "air"}, box])
    assert list(spectra.line_response([vacuum, air, unsaid], 6562.8)) == [1.0, 0.0, 0.0]
    assert [c.json()["wavelengths"] for c in (vacuum, air, unsaid)] == ["vacuum", "air", "air"]
    # The continuum integral reads a curve as sent under either convention.
    kelvin = np.array([5000.0])
    assert spectra.blackbody_response([vacuum], kelvin) == spectra.blackbody_response([air], kelvin)
    with pytest.raises(spectra.CurveError, match="wavelengths must be one of"):
        spectra.parse_curves([box | {"wavelengths": "nm"}])


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
        assert "[inferred]" in entry["about"] or "[verified: SVO" in entry["about"] or "[inferred]" in FILTERS["about"], name
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
    c = {k: v.value for k, v in Service().models.get(DEFAULT_MODEL).constants.items()}
    row = {r[0]: r for r in spectra.GRAIN_TABLE}
    assert (row[0.547][1], row[0.547][2]) == (c["DUST_ALBEDO_V"], c["DUST_SCATTERING_G"])
    assert row[0.151356][3] / row[0.547][3] == c["DUST_EXTINCTION_RATIO_FUV"] and row[0.151356][1] == c["DUST_ALBEDO_FUV"]
    assert (row[155.9][0], row[155.9][4]) == (c["DUST_OPACITY_WAVELENGTH"], c["DUST_OPACITY_REFERENCE"])


# The file's named rows (a filter's or a line's wavelength, printed beside it in the file and in GRAIN_TABLE's
# comments): the rows that lie on the file's list but off its 0.01-dex grid.
GRAIN_NAMED_ROWS = {0.2175, 0.35, 0.355, 0.3635, 0.41, 0.4405, 0.4685, 0.47, 0.4861, 0.547, 0.555, 0.6165, 0.6415,
                    0.6492, 0.6562, 1.25, 1.65, 2.2, 155.9}


def test_the_grain_table_keys_are_the_file_s_wavelengths():
    """A row can be right and misplaced (S43, #123: the 380.189 µm row sat under the 398.107 key and passed the
    identity above), so the keys are pinned to the file's own list as well as the rows to the identity. The file
    runs from 10⁴ µm down to 10⁻⁴ in steps of 0.01 dex printed to six significant figures, with its named rows
    between: every kept λ is 10^(k/100) for an integer k, or one of the 19 named rows. Three grid rows differ
    from the six-figure rounding of 10^(k/100) by one unit in the sixth figure (0.309029 for 0.309030, 0.354814
    for 0.354813, 0.630958 for 0.630957; relative 3.2e-6, 2.8e-6, 1.6e-6: the file's own printing, as
    transcribed at S39 and not re-read here), so the grid is held to one unit in the sixth figure, not to exact
    equality and not to rel=1e-6, which those three exceed."""
    off_grid = set()
    for lam in (r[0] for r in spectra.GRAIN_TABLE):
        k = round(100.0 * math.log10(lam))
        unit = 10.0 ** (math.floor(math.log10(lam)) - 5)  # one unit in the sixth significant figure
        if abs(float(f"{10.0 ** (k / 100.0):.6g}") - lam) > 1.0001 * unit:
            off_grid.add(lam)
    assert off_grid == GRAIN_NAMED_ROWS
    assert len(spectra.GRAIN_TABLE) == 104


def _far_infrared_residual(table):
    """The largest departure, in dex, of log10(C_ext/H) from a cubic in log10 λ fitted over the rows at λ ≥ 100 µm."""
    far = np.array([r for r in table if r[0] >= 100.0])
    x, y = np.log10(far[:, 0]), np.log10(far[:, 3])
    return float(np.abs(y - np.polyval(np.polyfit(x, y, 3), x)).max())


def test_the_far_infrared_rows_run_smoothly():
    """The nine rows at λ ≥ 100 µm depart from a least-squares cubic in log–log by at most 0.0078 dex (at 398.107
    µm); with the misplaced row restored (the 380.189 row's 3.493e-26 under the 398.107 key) the departure is
    0.0157 dex, and the bound is set between them at 0.011 — 1.4× over the one and 1.4× under the other, not the
    2× each way the ruling asked for (D195 (3)). No smoothness statistic at this sampling does better: the file's
    own run steepens to a log–log slope of −2.14 at 250–400 µm and flattens to −1.87 and −1.69 beyond, so the
    corrected row is itself the far-infrared's largest departure from any smooth fit, and the misplaced row, one
    0.02-dex step along the same run (0.040 dex in C_ext), is of the same order. The second difference of the
    consecutive rows does not separate them (max 0.266 corrected against 0.388 misplaced, the close pairs at
    155.9/158.489 and 245.471/251.189 carrying the rounding), and the local slope not at all (the misplaced row's
    slopes, −1.94 and −2.08, lie inside the corrected run's range). The cubic's residual is the separation there
    is; it is recorded here as a weak guard, the key test and the identity being the strong ones."""
    bound = 0.011
    corrected = _far_infrared_residual(spectra.GRAIN_TABLE)
    misplaced = [r if r[0] != 398.107 else (398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00) for r in spectra.GRAIN_TABLE]
    assert corrected == pytest.approx(0.0078, abs=1e-4) and corrected < bound
    assert _far_infrared_residual(misplaced) > bound


def test_the_extinction_curve_at_the_viewer_s_filters():
    """A_λ/A_V read at each filter's reference wavelength, pinned: the rgb set's R, V, B and the ir set's J, H, K.
    B over V is 1.302, a monochromatic R_V of 3.31 with A_V ≡ 1 at the table's 5470 Å row (3.28 with both bands
    read at their pivots, S43), against the broadband 3.1 the dust stage's E(B − V) divides by."""
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
    header, arrays = render(small, DEFAULT_MODEL, "rgb")
    f = scalars(small, DEFAULT_MODEL, "dust_extinction_v", "dust_scattering_optical_depth", "dust_scattering_asymmetry")
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
    sigma_ir = scalars(small, DEFAULT_MODEL, "dust_infrared_surface_brightness")["dust_infrared_surface_brightness"]
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


def test_the_named_instrument_draws_the_lines_through_its_measured_curves(full):
    """S42 (the owner's word on #108): WFC3's narrowband palette through the model. Each line lands in its own
    channel at the measured curve's throughput there, and the Halpha filter holds no [N II]. The curves are STScI's,
    on vacuum wavelengths, and say so; the model's air lines are converted by Morton 1991 before they are read
    (S44, D195, #120)."""
    header, arrays = render(full, DEFAULT_MODEL, "wfc3n", white="6500")
    lines = header["components"]["lines_hii"]["lines"]
    assert [c["wavelengths"] for c in header["filters"]] == ["vacuum"] * 3
    # S44: was 0.962 with the air line placed on STScI's vacuum curve (D195, #120)
    assert header["components"]["halpha_hii"]["transmission"][1] == pytest.approx(0.945, abs=2e-3)  # F656N at 6562.8 A
    # S44: was 0.903 with the air line placed on STScI's vacuum curve (D195, #120)
    assert lines["oiii_5007"]["transmission"][2] == pytest.approx(0.899, abs=2e-3)  # F502N
    assert lines["sii_6716"]["transmission"][0] > 0.95 and lines["sii_6731"]["transmission"][0] > 0.85  # F673N: 0.958, 0.863
    assert lines["nii_6583"]["transmission"][1] < 0.02 and lines["hbeta"]["transmission"] == [0.0, 0.0, 0.0]
    assert np.all(np.isfinite(arrays["stars"])) and all(v > 0 for v in header["white"]["response"])


# --- S42 (P6, proposed): the points through the filter set -------------------------------------------------


def test_the_blackbody_table_is_the_integral_and_runs_no_stage(small):
    """/api/blackbody: each filter's share of a blackbody's light on 193 temperatures, and the white point's.
    It runs no stage (a function of the curves alone, rule D4), refuses what /api/render refuses, and read as it
    says (log share linear in log T) it is within 2.5e-3 of the integral between its rows for every set the
    viewer offers (worst 2.2e-3, WFC3 at the grid's cool end)."""
    from galaxy.api.service import BLACKBODY_GRID

    got = small.handle("/api/blackbody", {"filters": [curves("rgb")], "white": ["6500"]})
    assert got.status == 200 and got.stages == ()
    table = got.json()
    parsed = spectra.parse_curves(SETS["rgb"]["curves"])
    assert np.allclose(table["share"], spectra.blackbody_response(parsed, BLACKBODY_GRID), rtol=1e-12, atol=0.0)
    assert table["white"]["response"] == pytest.approx(spectra.blackbody_response(parsed, np.array([6500.0]))[0].tolist(), rel=1e-12)
    assert small.handle("/api/blackbody", {}).status == 400
    assert small.handle("/api/blackbody", {"filters": [curves("rgb")], "white": ["500"]}).status == 400
    mid = np.sqrt(BLACKBODY_GRID[1:] * BLACKBODY_GRID[:-1])  # the farthest points from the rows
    for name, entry in SETS.items():
        parsed = spectra.parse_curves(entry["curves"])
        rows = spectra.blackbody_response(parsed, BLACKBODY_GRID)
        read = np.sqrt(rows[1:] * rows[:-1])  # log-linear at the midpoint in log T
        assert np.abs(read / spectra.blackbody_response(parsed, mid) - 1).max() < 2.5e-3, name


def test_a_point_through_the_filters_is_its_light_where_the_filters_see_it(small):
    """What P6 changes, in numbers (RGB): a white-point star is drawn as before; a hot one is dimmer through the
    optical filters than its bolometric light, because most of its light is below them, and a cool one redder -
    the ramp drew every star at its bolometric light in its hue."""
    table = small.handle("/api/blackbody", {"filters": [curves("rgb")], "white": ["6500"]}).json()
    k, share, white = np.log10(table["kelvin"]), np.array(table["share"]), np.array(table["white"]["response"])

    def channels(t: float) -> np.ndarray:
        return np.array([10 ** np.interp(np.log10(t), k, np.log10(share[:, c])) for c in range(3)]) / white

    assert channels(6500.0) == pytest.approx([1.0, 1.0, 1.0], abs=2e-3)
    hot, cool = channels(30_000.0), channels(3_000.0)
    assert hot.max() < 0.35 and hot[2] > hot[1] > hot[0]  # an O star: blue, and a third of its light or less
    assert cool[0] > cool[1] > cool[2] and cool[2] < 0.1


# --- S48 (D200, D201, #114): one object's light through the curves ------------------------------------------

# The gate's sample: every tenth isochrone of the table (40 of 396: every metallicity, ages across the grid), fifty
# points along each evenly in the table's own order (so the pre-main sequence, the main sequence, the giant branch,
# the core-helium burners, the early and thermally pulsing AGB all appear: 299 / 411 / 191 / 198 / 116 / 90 / 91 /
# 244 / 360 by PARSEC label 0-8), among the points 1000-100 000 K the table spans.
GATE_THRESHOLD_WEIGHTED = 0.02  # mag, luminosity-weighted (D200)
GATE_THRESHOLD_MAX = 0.1  # mag (D200)


def _isochrone_points(hot: bool = False):
    from galaxy.stages.photometry import EXTRA, isochrones

    tab = isochrones()
    mags, log_t, log_l, label = [], [], [], []
    for key in sorted(tab.tracks)[::10]:
        _, ll, lt = tab.tracks[key]
        extra = tab.extra[key]
        if hot:
            pick = np.flatnonzero(lt > 5.0)
        else:
            inside = np.flatnonzero((lt >= 3.0) & (lt <= 5.0))
            pick = inside[np.unique(np.linspace(0, inside.size - 1, 50).round().astype(int))]
        mags.append(extra[pick, :8]), log_t.append(lt[pick]), log_l.append(ll[pick])
        label.append(extra[pick, EXTRA.index("label")])
    return (np.concatenate(mags), 10.0 ** np.concatenate(log_t), 10.0 ** np.concatenate(log_l), np.concatenate(label))


def _floored(anchors: np.ndarray) -> np.ndarray:
    return np.maximum(anchors, spectra.ANCHOR_FLOOR * anchors.max(axis=-1, keepdims=True))


def _mag(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return 2.5 * np.abs(np.log10(a / b))


@pytest.fixture(scope="module")
def objects():
    """The 2 000 points, their anchors as given and floored (the exact reference is ``stellar_response`` on the
    floored anchors, so it is sound at every point), and per set the reference and ``object_response``."""
    mags, kelvin, light, label = _isochrone_points()
    anchors = spectra.object_nu_l_nu(mags)
    floored = _floored(anchors)
    sets = {}
    for name, entry in SETS.items():
        parsed = spectra.parse_curves(entry["curves"])
        sets[name] = (parsed, spectra.stellar_response(floored, kelvin, parsed), spectra.object_response(anchors, kelvin, parsed))
    return {"anchors": anchors, "floored": floored, "kelvin": kelvin, "light": light, "label": label, "sets": sets}


def test_the_object_tables_are_on_the_blackbody_route_s_temperatures():
    from galaxy.api.service import BLACKBODY_GRID

    assert np.array_equal(spectra.RESPONSE_TEMPERATURES, BLACKBODY_GRID)


def test_an_object_s_anchors_are_its_magnitudes_through_the_zero_points():
    mags = np.array([[5.6, 5.4, 4.8, 4.4, 4.1, 3.6, 3.3, 3.3], [np.nan] * 8])
    got = spectra.object_nu_l_nu(mags)
    for k, band in enumerate(BANDS):
        assert got[0, k] == pytest.approx(float(band_nu_l_nu(10 ** (-0.4 * mags[0, k]), band)), rel=1e-15)
    assert np.all(np.isnan(got[1]))  # a dead star: no magnitudes, no light (B9)
    with pytest.raises(ValueError, match="8 bands"):
        spectra.object_nu_l_nu(np.zeros(7))


@pytest.mark.parametrize("name", ["bands", *SETS])
def test_the_tables_are_the_trapezoid_between_their_rows(name):
    """Each segment's ln G(s) = ln Σ q_i e^{w_i s}, read linearly between the slope rows, against the sum itself at
    the rows' midpoints: within h²/32 = 1.25e-5 (ln G is convex in s, its curvature the variance of w ≤ 1/4; worst
    measured 4.7e-6, the eight band curves). Each tail factor, read linearly in ln between the temperature rows,
    within 1e-4 of the sum at the midpoints (worst 3.3e-5, the band curves). Equal sets share their tables."""
    parsed = [spectra.band_curve(b) for b in BANDS] if name == "bands" else spectra.parse_curves(SETS[name]["curves"])
    factors = spectra.response_factors(parsed)
    slopes = 0.5 * (spectra.RESPONSE_SLOPES[1:] + spectra.RESPONSE_SLOPES[:-1])
    kelvin = np.sqrt(spectra.RESPONSE_TEMPERATURES[1:] * spectra.RESPONSE_TEMPERATURES[:-1])
    tables = {k: (table[..., 0], member) for k, table, member in factors.segments}
    log_x, ends = np.log(spectra.SED_WAVELENGTHS), spectra.SED_WAVELENGTHS
    for c, curve in enumerate(parsed):
        lam = curve.grid()
        q = np.zeros_like(lam)
        q[:-1] += 0.5 * np.diff(lam)
        q[1:] += 0.5 * np.diff(lam)
        q *= curve.at(lam)
        x = np.log(np.clip(lam, ends[0], ends[-1]))
        k = np.clip(np.searchsorted(log_x, x, side="right") - 1, 0, 6)
        w = (x - log_x[k]) / (log_x[k + 1] - log_x[k])
        inside = (lam >= ends[0]) & (lam <= ends[-1]) & (q > 0.0)
        for seg in range(7):
            at = inside & (k == seg)
            if at.any():
                log_g, member = tables[seg]
                read = log_g[:, int(np.flatnonzero(member[:, c])[0])]
                direct = np.log(np.exp(np.outer(slopes, w[at])) @ q[at])
                assert np.abs(0.5 * (read[1:] + read[:-1]) - direct).max() < 1.25e-5, (name, c, seg)
        for side, (beyond, end) in enumerate((((lam < ends[0]) & (q > 0.0), 0), ((lam > ends[-1]) & (q > 0.0), -1))):
            assert factors.has_tails[side, c] == beyond.any()
            if beyond.any():
                direct = (spectra.planck_share(lam[beyond], kelvin) / spectra.planck_share(ends[end:][:1], kelvin)) @ q[beyond]
                read = np.exp(0.5 * (factors.log_tails[side, 1:, c] + factors.log_tails[side, :-1, c]))
                big = direct > 1e-200
                assert np.abs(read[big] / direct[big] - 1.0).max() < 1e-4, (name, c, side)
    assert spectra.response_factors(spectra.parse_curves(json.loads(json.dumps([p.json() for p in parsed])))) is factors


def test_an_object_s_response_scales_with_its_light_exactly(objects):
    """Homogeneity: every anchor ×10 is every response ×10, to 1e-9, and the shapes broadcast."""
    a, t = objects["anchors"][::50], objects["kelvin"][::50]
    for name, (parsed, _, _) in objects["sets"].items():
        one = spectra.object_response(a, t, parsed)
        assert np.allclose(spectra.object_response(10.0 * a, t, parsed), 10.0 * one, rtol=1e-9, atol=0.0), name
    got = spectra.object_response(a[:6].reshape(2, 3, 8), t[:6].reshape(2, 3), parsed)
    assert got.shape == (2, 3, 3) and np.allclose(got.reshape(6, 3), one[:6], rtol=1e-14, atol=0.0)


def test_an_object_without_light_is_dark_and_without_a_temperature_missing():
    """No light is zero; a NaN anchor, or light with no temperature, is missing (B9); a vanished anchor is floored
    (D201) and the response is the field's machinery on the floored anchors."""
    rgb = spectra.parse_curves(SETS["rgb"]["curves"])
    lit = spectra.object_nu_l_nu(np.array([5.6, 5.4, 4.8, 4.4, 4.1, 3.6, 3.3, 3.3]))
    anchors = np.stack([np.zeros(8), lit, lit, lit, np.full(8, np.nan), lit])
    kelvin = np.array([np.nan, np.nan, 0.0, 5800.0, 5800.0, 300_000.0])
    got = spectra.object_response(anchors, kelvin, rgb)
    assert np.all(got[0] == 0.0) and np.all(np.isnan(got[1:3])) and np.all(np.isnan(got[4]))
    assert np.all(got[3] > 0.0) and np.all(np.isfinite(got[5]))  # beyond the grid: the end row's tails
    vanished = lit * np.array([0.0, 1, 1, 1, 1, 1, 1, 1])
    got = spectra.object_response(vanished, np.array(5800.0), rgb)
    assert got == pytest.approx(spectra.stellar_response(_floored(vanished), np.array(5800.0), rgb), rel=1e-4)


def test_the_floor_and_the_stars_the_join_cannot_carry(objects):
    """Through the eight band curves themselves the exact path should return each star's own magnitudes. Unfloored
    it misses at 39 of the 2 000 points, all thermally pulsing AGB stars (label 8) whose circumstellar dust puts
    M_B up to +95 beside M_K +4.5: by up to 8.5 / 49.6 / 9.8 mag in U / B / V. Floored at 1e-12 of the peak (D201;
    14 of the 39 have an anchor under it — U at 14, B 6, V 5, R 2, I 1), 7 of the 39 then hold every band above
    the floor to 0.01 mag and **32 still do not**: U at 25 of them by up to 2.65 mag, B at 6 by up to 0.38, V at 3
    by up to 0.09; R to K hold. Those stars are steep but above the floor: twelve multiplicative passes of
    ``band_consistent`` do not pull a band's mean down past the light its Gaussian's wings take from a neighbour
    tens of magnitudes brighter. The floor is not the remedy for them; the field's machinery is what it is (D201:
    ``stellar_response`` unchanged). ``object_response`` is that machinery: within 1e-5 mag of it here too."""
    bands = [spectra.band_curve(b) for b in BANDS]
    norm = np.array([np.trapezoid(c.at(c.grid()), c.grid()) for c in bands])
    a, f, t = objects["anchors"], objects["floored"], objects["kelvin"]
    under = a < spectra.ANCHOR_FLOOR * a.max(axis=1, keepdims=True)
    before = _mag(spectra.stellar_response(a, t, bands), a / spectra.SED_WAVELENGTHS * norm)
    exact = spectra.stellar_response(f, t, bands)
    after = np.where(under, 0.0, _mag(exact, f / spectra.SED_WAVELENGTHS * norm))
    missed = before.max(axis=1) > 0.01
    assert missed.sum() == 39 and set(objects["label"][missed]) == {8.0}
    assert before[missed].max(axis=0)[:3] == pytest.approx([8.4646, 49.6082, 9.8395], abs=2e-4)
    assert under.any(axis=1).sum() == 14 and list(under.sum(axis=0)) == [14, 6, 5, 2, 1, 0, 0, 0]
    still = after.max(axis=1) > 0.01
    assert still.sum() == 32 and np.all(missed[still])
    assert list((after > 0.01).sum(axis=0)) == [25, 6, 3, 0, 0, 0, 0, 0]
    assert after.max(axis=0)[:3] == pytest.approx([2.6525, 0.3791, 0.0906], abs=2e-4)
    assert _mag(spectra.object_response(a, t, bands), exact).max() < 1e-5


# Per set, the worst over its filters of the median / max / luminosity-weighted |Δ mag| at all 2 000 points,
# measured at S48.
GATE = {
    "rgb": (5.4e-8, 2.83e-6, 8.3e-8),
    "sho": (3.16e-6, 9.51e-6, 3.26e-6),
    "hoo": (3.16e-6, 9.51e-6, 3.26e-6),
    "wfc3": (1.93e-6, 1.89e-5, 2.07e-6),
    "wfc3n": (3.16e-6, 9.50e-6, 3.27e-6),
}


@pytest.mark.parametrize("name", list(GATE))
def test_the_object_response_against_the_exact_integral(objects, name):
    """**D200's gate, D201's method**: ``object_response`` against the exact ``stellar_response`` on the same
    floored anchors at all 2 000 isochrone points, per filter, |Δ mag| = 2.5 |log10(approx / exact)|. Worst over each
    set's filters, median / max / luminosity-weighted, measured at S48 (``GATE``): rgb 5e-8 / 2.8e-6 / 8e-8; sho and
    hoo 3.2e-6 / 9.5e-6 / 3.3e-6; wfc3 1.9e-6 / 1.9e-5 / 2.1e-6; wfc3n 3.2e-6 / 9.5e-6 / 3.3e-6 — the tables'
    interpolation (the band curves' slope rows, 4.7e-6 in ln G, carried through the twelve passes). D200's threshold
    (weighted under 0.02 mag, worst under 0.1) holds for every set, the narrowband ones included.

    Not to be retried: S48's first commit linearised the machinery in log about a blackbody at T. On wfc3 at the
    points the exact path held, weighted 0.0198 mag and worst 0.34 (TP-AGB); second-order 4.76; blends 0.26-0.42."""
    parsed, exact, approx = objects["sets"][name]
    light = objects["light"]
    dm = _mag(approx, exact)
    median, worst, weighted = np.median(dm, axis=0).max(), dm.max(), ((dm * light[:, None]).sum(axis=0) / light.sum()).max()
    assert [median, worst, weighted] == pytest.approx(GATE[name], rel=0.05)
    assert weighted < GATE_THRESHOLD_WEIGHTED and worst < GATE_THRESHOLD_MAX


def test_an_object_beyond_the_grid_reads_the_end_row():
    """The 87 points of the same isochrones hotter than 100 000 K are given the end row's tails (10⁵ K's, below U
    and beyond K): within 0.002 mag of the exact path at their own temperatures through every set (measured at S48:
    rgb 1e-5, the narrowband sets 0.0009, wfc3 0.0014 in F438W)."""
    mags, kelvin, _, _ = _isochrone_points(hot=True)
    anchors = spectra.object_nu_l_nu(mags)
    assert kelvin.size == 87
    for name, entry in SETS.items():
        parsed = spectra.parse_curves(entry["curves"])
        exact = spectra.stellar_response(_floored(anchors), kelvin, parsed)
        assert _mag(spectra.object_response(anchors, kelvin, parsed), exact).max() < 0.002, name


def test_ten_to_the_five_objects_in_about_a_second(objects):
    """10⁵ objects through rgb with the tables warm: 0.7 s at S48 (bound 3 s), where the exact path took 1.3 s for
    2 000. The tables, once per filter set: 0.03 s for rgb, 0.4-0.5 s for the box and sampled sets, 0.1 s for the
    eight band curves (shared by every set)."""
    import time

    parsed = objects["sets"]["rgb"][0]
    pick = np.random.default_rng(0).integers(0, objects["kelvin"].size, 100_000)
    a, t = objects["anchors"][pick], objects["kelvin"][pick]
    start = time.perf_counter()
    got = spectra.object_response(a, t, parsed)
    assert time.perf_counter() - start < 3.0 and got.shape == (100_000, 3)


def test_today_s_painting_against_the_object_s_light(objects):
    """#114 re-made on stars: a point painted as its bolometric light through a blackbody's share at its
    temperature (``L × blackbody_response``, what the viewer draws today) against its light through the filters
    (the exact ``stellar_response`` of its eight bands). Summed over the 2 000 isochrone points, the painting reads
    1.151 / 1.093 / 1.043 of the stars' light in R / G / B; per point the median is 1.107 / 1.139 / 1.259. S41's
    1.89 / 2.12 / 2.43 was the cluster census, each cluster one blackbody at its population's colour temperature:
    the factor of two is a population's light not being one blackbody, a star's much less so. (A light-weighted
    mean of the per-point ratio is not a number: the dust-shrouded AGB stars read 10²⁰ — L_bol over almost no
    optical light.)"""
    parsed, exact, _ = objects["sets"]["rgb"]
    paint = objects["light"][:, None] * spectra.blackbody_response(parsed, objects["kelvin"])
    assert paint.sum(axis=0) / exact.sum(axis=0) == pytest.approx([1.1511, 1.0929, 1.0427], abs=2e-4)
    assert np.median(paint / exact, axis=0) == pytest.approx([1.1065, 1.1388, 1.2591], abs=2e-4)
