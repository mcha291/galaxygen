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


def test_the_line_is_the_nebular_field_through_each_curve(full):
    header, arrays = render(full, "basic", "sho")
    f = scalars(full, "basic", "halpha_surface_brightness_nebular", "dust_extinction_v", "dust_colour_excess_b_v")
    assert header["components"]["halpha"]["transmission"] == [0.0, 1.0, 0.0]  # [S II], Halpha, [O III] boxes
    assert np.array_equal(arrays["halpha"][:, 1], f["halpha_surface_brightness_nebular"])
    assert not arrays["halpha"][:, [0, 2]].any()
    # The dust is the published fields, untouched.
    assert np.array_equal(arrays["dust_extinction_v"], f["dust_extinction_v"])
    assert np.array_equal(arrays["dust_colour_excess_b_v"], f["dust_colour_excess_b_v"])
    # The lines the model does not publish are named, not drawn dark (rule B9).
    assert set(header["absent"]["lines"]) == {"hbeta", "oiii_5007", "sii_6716", "sii_6731", "nii_6583"}


# --- the route --------------------------------------------------------------------------------


def test_the_render_runs_the_closure_of_what_it_reads_and_names_it(small, model):
    got = small.handle("/api/render", {"model": [model.name], "filters": [curves("rgb")]})
    assert got.status == 200
    assert "light" in got.stages and "nebular" in got.stages
    assert "systems" not in got.stages and "planets" not in got.stages  # no catalogue is materialised
    header, arrays = wire.decode(got.body)
    assert header["stages"] == list(got.stages)
    assert arrays["stars"].shape == (48, 36, 3) and arrays["halpha"].shape == (48, 3)
    assert header["axes"]["stars"] == ["R", "phi", "filter"] and header["axes"]["dust_extinction_v"] == ["R"]


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
    assert np.array_equal(part["stars"], whole["stars"][rows][:, cols])
    assert np.array_equal(part["halpha"], whole["halpha"][rows])
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
    assert deep["stars"].shape == (header["window"]["cells"]["count"], 3) and np.all(deep["stars"] > 0)


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
