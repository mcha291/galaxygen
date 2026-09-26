"""The filter integral and /api/render (S38, BUILD_II V1; RENDER_PHYSICS §§0, 2, 3a).

**The gate.** The whole galaxy rendered through the viewer's own "rgb" set (read from the
viewer's data file, so the check runs on the curves the viewer sends), the stellar responses
integrated over every (R, φ) cell of the frame plus the bulge — the linear buffer before the
tone map, which only multiplies it — and turned into B − V and M_V against Phase 3's published
``colour_b_v`` and ``absolute_magnitude_v``, which are the eight-band table's.

**The zero point.** A response is energy through a curve, not a Vega magnitude, so each filter
is tied to the table's band of the same name at the table's own Sun (1 M☉, 4.57 Gyr, solar;
``test_photometry``): the blackbody at that star's T_eff and L, through the curve, is given
that star's tabulated magnitude. Everything the gate then measures is how far the first cut's
spectrum — one blackbody at the disc's colour temperature — sits from the populations the table
integrates, relative to how far a blackbody sits from the Sun.

**What it measured (S38), and the tolerance that covers it.** Basic and azimuthal alike (their
light fields are the same): the frame's B − V 0.64281 against 0.63055 (+0.0123) and M_V
−21.9285 against −21.2159 (−0.713 mag). The colour is close because the Sun's colour and the
galaxy's are close; the magnitude is not, because a population's light is spread wider than one
blackbody's — its giants' in the infrared, its young stars' in the ultraviolet (the table's
BC_V is −0.87, a 5600 K blackbody's about −0.1) — and one blackbody at the colour temperature
puts twice the V light in the band. Per ring, the blackbody's B − V against the table's runs from
−0.080 to +0.252 (luminosity-weighted mean +0.065): the colour temperature is a chromaticity
read on a 1%-spaced grid, and two rings with table B − V 0.70 and 0.54 read the same 5612 K. The
tolerance is stated to cover these and nothing more — 0.02 in B − V, 0.75 mag in M_V — and the
measured numbers are pinned beside it, so the first cut cannot drift inside the tolerance
unseen. The second cut (the populations' own temperature mix, or the eight bands as an SED) is
what closes the magnitude; this gate says by how much it has to.
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
from galaxy.stages.photometry import lookup, lookup_columns, population_over

ROOT = Path(__file__).resolve().parents[1]
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
SETS = FILTERS["sets"]
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)

# The gate's tolerance, stated (module docstring), and what it measured at S38.
TOLERANCE_B_V = 0.02
TOLERANCE_M_V = 0.75
MEASURED_B_V = 0.642807  # the frame's; the table's 0.630552
MEASURED_M_V = -21.928533  # the frame's; the table's -21.215871


def curves(name: str) -> str:
    return json.dumps(SETS[name]["curves"])


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


def zero_points(set_curves: list[dict], bands: dict[str, int]) -> dict[str, float]:
    """Each named filter's magnitude zero point, fixed at the table's own Sun (module docstring)."""
    L, T = lookup(np.array([1.0]), np.array([4.57]), np.array([0.0]))
    sun = lookup_columns(np.array([1.0]), np.array([4.57]), np.array([0.0]), tuple(bands))
    share = spectra.blackbody_response(spectra.parse_curves(set_curves), T)[0]
    return {band: float(sun[band][0] + 2.5 * math.log10(L[0] * share[k])) for band, k in bands.items()}


def frame_magnitudes(header: dict, arrays: dict) -> dict[str, float]:
    """B − V and M_V of the whole frame: the stellar responses summed over its cells, and the bulge."""
    total = (arrays["stars"] * cell_areas(header)[..., None]).sum(axis=(0, 1)) + np.asarray(header["bulge"])
    names = [c["name"] for c in header["filters"]]
    bands = {"B": names.index("B"), "V": names.index("V")}
    zp = zero_points(SETS["rgb"]["curves"], bands)
    m = {band: zp[band] - 2.5 * math.log10(total[k]) for band, k in bands.items()}
    return {"B_V": m["B"] - m["V"], "M_V": m["V"]}


# --- the gate -------------------------------------------------------------------------------


def test_the_frame_s_colour_and_magnitude_are_the_table_s_within_the_first_cut_s_tolerance(full, model):
    header, arrays = render(full, model.name, "rgb")
    got = frame_magnitudes(header, arrays)
    table = scalars(full, model.name, "colour_b_v", "absolute_magnitude_v")
    print(model.name, got, table)
    assert table["colour_b_v"] == pytest.approx(0.6306, abs=5e-5)  # row pins elsewhere; the target here
    assert table["absolute_magnitude_v"] == pytest.approx(-21.2159, abs=5e-5)
    assert abs(got["B_V"] - table["colour_b_v"]) < TOLERANCE_B_V
    assert abs(got["M_V"] - table["absolute_magnitude_v"]) < TOLERANCE_M_V
    # The measurement itself, pinned, so the first cut cannot move inside its tolerance unseen.
    assert got["B_V"] == pytest.approx(MEASURED_B_V, abs=2e-6)
    assert got["M_V"] == pytest.approx(MEASURED_M_V, abs=2e-6)


def test_the_blackbody_against_the_table_ring_by_ring_is_what_the_gate_states(full):
    """The same populations in the table's B and V, per ring (light.py's sum), against the first cut's."""
    header, arrays = render(full, "basic", "rgb")
    f = scalars(full, "basic", "stars_formed_history", "feh_history", "disc_surface_brightness")
    grid = full.grid
    dt = float(grid.spec.t_max) / float(grid.spec.n_t)
    youngest = float(grid.spec.t_max) - (grid.t + 0.5 * dt)
    step = population_over(youngest, youngest + dt, f["feh_history"])
    formed = np.asarray(f["stars_formed_history"]) / (1.0 - full.models.get("basic").constants["RETURN_FRACTION"].value)
    b, v = (formed * step["B"]).sum(axis=1), (formed * step["V"]).sum(axis=1)
    per_ring = arrays["stars"].mean(axis=1)  # the contrast averages to 1 around a ring
    names = [c["name"] for c in header["filters"]]
    zp = zero_points(SETS["rgb"]["curves"], {"B": names.index("B"), "V": names.index("V")})
    lit = (b > 0) & (v > 0) & (per_ring[:, 1] > 0)
    table = -2.5 * np.log10(b[lit] / v[lit])
    first_cut = (zp["B"] - 2.5 * np.log10(per_ring[lit, names.index("B")])) - (zp["V"] - 2.5 * np.log10(per_ring[lit, names.index("V")]))
    d = first_cut - table
    weight = (f["disc_surface_brightness"] * grid.R)[lit]
    assert d.min() == pytest.approx(-0.0796, abs=1e-3)
    assert d.max() == pytest.approx(0.2517, abs=1e-3)
    assert np.average(d, weights=weight) == pytest.approx(0.0647, abs=1e-3)


def test_the_frame_integral_is_the_published_light(full):
    """Through a box spanning the whole continuum grid a blackbody passes all but its tails, so the frame
    integrates back to disc_luminosity: the cell sum against the stage's trapezoid less the tails, 7.4e-5 apart
    at S38."""
    wide = json.dumps([{"name": "all", "shape": "box", "centre": 150_500.0, "width": 299_000.0}])
    got = full.handle("/api/render", {"filters": [wide]})
    header, arrays = wire.decode(got.body)
    frame = float((arrays["stars"][..., 0] * cell_areas(header)).sum())
    published = scalars(full, "basic", "disc_luminosity")["disc_luminosity"]
    assert frame == pytest.approx(published, rel=2e-4)


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


def test_the_stars_are_the_published_light_at_its_temperature_placed_by_the_contrast(small):
    header, arrays = render(small, "basic", "rgb", white="6500")
    f = scalars(small, "basic", "disc_surface_brightness", "disc_light_temperature", "pattern_density_contrast",
                "bulge_luminosity", "bulge_light_temperature")
    parsed = spectra.parse_curves(SETS["rgb"]["curves"])
    share = spectra.blackbody_response(parsed, f["disc_light_temperature"])
    want = f["disc_surface_brightness"][:, None, None] * np.maximum(f["pattern_density_contrast"], 0.0)[..., None] * share[:, None, :]
    assert np.allclose(arrays["stars"], want, rtol=1e-14, atol=0.0)
    bulge = f["bulge_luminosity"] * spectra.blackbody_response(parsed, np.array([f["bulge_light_temperature"]]))[0]
    assert header["bulge"] == pytest.approx(bulge.tolist(), rel=1e-14)
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
    got = spectra.stellar_response(np.array([0.0, 5.0, 5.0]), np.array([np.nan, np.nan, 5000.0]), parsed)
    assert np.all(got[0] == 0.0) and np.all(np.isnan(got[1])) and np.all(got[2] > 0.0)


def test_the_viewer_s_sets_are_curves_the_model_takes():
    for name, entry in SETS.items():
        parsed = spectra.parse_curves(entry["curves"])
        assert len(parsed) == 3, name
        assert "[inferred]" in entry["about"] or "[inferred]" in FILTERS["about"], name
    assert 1000.0 <= FILTERS["white"]["kelvin"] <= 100_000.0
