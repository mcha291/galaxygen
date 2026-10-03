"""The dust in its own layer and round each ring (S50, D206 and D207; debt #109's layer, debt #128's record).

The ism stage publishes ``gas_scale_height`` — the gas's column over four times its midplane density, the
h of the render's one layer form — and ``/api/render`` returns it ring by ring as the dust's layer
(``layers.dust`` names the array ``dust_height``). What is asserted here:

- **the identity**, to rounding: a sech²(z / 2h) / 4h layer at the published height holds the published
  column at the published midplane density (4 h ρ₀ = Σ), in both models;
- **the measurements**, pinned as read at S50 on the default galaxy (not rows: no observed height was read
  before the ruling, D113): 21 pc at the centre, 113 pc at the solar radius, a flare that passes the stars'
  own height near 13 kpc, a dust-mass-weighted mean of 65 pc;
- **the render's contract**: the array is the field in kpc, named by ``layers.dust``, per ring or per region
  cell, beside the components and never among them;
- **debt #128's record**: the dust stage's heating is still one uniformly mixed slab. What the layered
  geometry would absorb instead is computed here by an independent quadrature — the escape of light emitted
  isotropically by stars in their layer through a dust in its own — and pinned, not applied: 0.766 of the
  slab's, an infrared share of 0.262 of the disc's light against the published 0.342.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import RENDER_DUST_HEIGHT, Service
from galaxy.core.grids import GridSpec
from galaxy.core.special import expn
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import dust, ism
from galaxy.stages.disc import PC_PER_KPC

ROOT = Path(__file__).resolve().parents[1]
RGB = json.dumps(json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))["sets"]["rgb"]["curves"])
SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
FIELDS = (
    "gas_surface_density", "gas_midplane_density", "gas_scale_height", "thin_disc_scale_height",
    "dust_surface_density", "dust_extinction_v", "disc_surface_brightness", "disc_luminosity",
    "dust_absorbed_luminosity",
)


@pytest.fixture(scope="module")
def galaxy(prod):
    """The default galaxy on the default grid: what the pins were read on."""
    return run(prod[0].get(DEFAULT_MODEL), only=FIELDS)


def at(R: np.ndarray, values: np.ndarray, radius: float) -> float:
    return float(np.asarray(values)[int(np.argmin(np.abs(R - radius)))])


# --- the field ------------------------------------------------------------------------------------


def test_the_layer_holds_the_published_column_at_the_published_midplane_density(model):
    f = run(model, grid=SMALL, only=FIELDS[:4]).fields
    sigma, rho, h = (np.asarray(f[n], dtype=float) for n in ("gas_surface_density", "gas_midplane_density", "gas_scale_height"))
    held = np.isfinite(h)
    assert held.any() and (rho[held] > 0.0).all()
    # A sech²(z / 2h) / 4h layer's midplane density is its column over 4h.
    np.testing.assert_allclose(4.0 * h[held] * rho[held], sigma[held], rtol=1e-13)
    # No number where the stage has none to give: no midplane density, or a "layer" taller than the distance
    # over which the stars that hold it change.
    out = run(model, grid=SMALL, only=("stellar_surface_density",))
    scale = ism.local_scale_length(out.fields["stellar_surface_density"], out.grid.R)
    quotient = np.where(rho > 0.0, sigma / np.where(rho > 0.0, 4.0 * rho, 1.0), np.inf)
    np.testing.assert_array_equal(held, quotient < scale)
    assert not held.all()  # the default galaxy's stellar disc ends inside the grid
    assert ism.GAS_SCALE_HEIGHT.unit == "pc" and ism.GAS_SCALE_HEIGHT.axes == ("R",)


def test_no_midplane_density_is_no_height_not_a_height_of_zero():
    h = ism.layer_height(np.array([10.0, 5.0, 0.0, 3.0]), np.array([0.025, 0.0, 0.0, 0.01]))
    assert h[0] == pytest.approx(100.0) and h[3] == pytest.approx(75.0)
    assert np.isnan(h[1]) and np.isnan(h[2])  # rule B9
    # Given the scale its support changes over, a quotient not smaller than it is refused too.
    bounded = ism.layer_height(np.array([10.0, 3.0, 3.0]), np.array([0.025, 0.01, 0.01]), np.array([90.0, 2500.0, 75.0]))
    assert np.isnan(bounded[0]) and bounded[1] == pytest.approx(75.0) and np.isnan(bounded[2])


def test_the_local_scale_length_is_an_exponential_s_own():
    R = np.linspace(0.5, 20.0, 400)
    scale = ism.local_scale_length(40.0 * np.exp(-R / 2.5), R)
    assert scale == pytest.approx(2500.0, rel=1e-9)  # pc; exact for an exponential, edges included
    flat = ism.local_scale_length(np.array([3.0, 3.0, 3.0, 0.0]), np.array([1.0, 2.0, 3.0, 4.0]))
    assert np.isinf(flat[0]) and np.isinf(flat[1]) and np.isnan(flat[3])


def test_the_heights_as_read_at_s50(galaxy):
    """Pinned measurements of the default galaxy (D206's probe, then the field itself): the layer is thin where
    the stars are dense and flares as they thin out, passing the stars' own height in the outer disc."""
    f, R = galaxy.fields, np.asarray(galaxy.grid.R)
    h = np.asarray(f["gas_scale_height"], dtype=float)
    h_star = float(f["thin_disc_scale_height"])
    assert at(R, h, 0.1) == pytest.approx(21.31, abs=0.05)
    assert at(R, h, 2.0) == pytest.approx(31.20, abs=0.05)
    assert at(R, h, 4.0) == pytest.approx(46.89, abs=0.05)
    assert at(R, h, 8.2) == pytest.approx(113.08, abs=0.1)
    assert at(R, h, 8.2) / h_star == pytest.approx(0.318, abs=0.002)  # a third of the thin disc's 355.7 pc
    assert at(R, h, 15.0) == pytest.approx(437.9, abs=0.5)
    inside = R <= 20.0
    # A flare, monotonic across the stellar disc from the second ring out (the first reads 21.69 against the
    # second's 21.31: the innermost cell of the stellar profile).
    assert np.all(np.diff(h[inside][1:]) > 0.0) and h[0] == pytest.approx(21.69, abs=0.05)
    assert float(R[inside][np.argmin(np.abs(h[inside] - h_star))]) == pytest.approx(13.09, abs=0.08)
    held = np.isfinite(h)
    weight = np.asarray(f["dust_surface_density"], dtype=float) * R
    assert float(np.trapezoid((weight * h)[held], R[held]) / np.trapezoid(weight[held], R[held])) == pytest.approx(65.33, abs=0.1)
    # Past the stellar disc's edge the quotient runs away (1.2 kpc at 23 kpc, 10 kpc at 24, 118 kpc at 26) and
    # the field holds no number from the first ring of the edge, 23.66 kpc, where the stars' scale length drops
    # under the layer's height (it is 3.1 kpc against 1.3 one ring inside, and never under 2.3 heights inside
    # that): every ring inside has a height, none outside, and the dust left without one is 1.5 × 10⁻⁵ of the
    # dust's mass, dimming by a thousandth of a magnitude face-on at most.
    assert at(R, h, 23.0) == pytest.approx(1199.0, abs=2.0)
    first = int(np.argmin(held))
    assert held[:first].all() and not held[first:].any()
    assert float(R[first]) == pytest.approx(23.66, abs=0.04)
    assert h[first - 1] == pytest.approx(1319.3, abs=2.0)
    assert float(np.asarray(f["dust_extinction_v"])[first]) < 1.1e-3
    assert float(np.trapezoid(weight[~held], R[~held]) / np.trapezoid(weight, R)) < 2e-5


# --- the render -----------------------------------------------------------------------------------


def render(api: Service, model: str, **extra: str):
    got = api.handle("/api/render", {"model": [model], "filters": [RGB], **{k: [v] for k, v in extra.items()}})
    assert got.status == 200, got.body[:300]
    return wire.decode(got.body)


def test_the_render_s_dust_layer_is_the_field_ring_by_ring(model):
    api = Service(grid=SMALL)
    header, arrays = render(api, model.name)
    got = api.handle("/api/arrays", {"model": [model.name], "fields": ["gas_scale_height,thin_disc_scale_height"]})
    scalars, fields = wire.decode(got.body)
    layers = header["layers"]
    assert layers["dust"] == RENDER_DUST_HEIGHT == "dust_height"
    assert layers["stars"] == pytest.approx(scalars["scalars"]["thin_disc_scale_height"] / 1000.0, rel=1e-15)
    height = np.asarray(arrays["dust_height"])
    assert header["axes"]["dust_height"] == ["R"] and height.shape == (SMALL.n_R,)
    np.testing.assert_array_equal(height, np.asarray(fields["gas_scale_height"]) / 1000.0)  # kpc, nothing else
    entry = layers["arrays"]["dust_height"]
    assert entry["unit"] == "kpc" and entry["fields"] == ["gas_scale_height"] and entry["about"]
    # Beside the components, never one of them: it has no filter axis and no entry among them.
    assert "dust_height" not in header["components"]
    for name in ("dust_extinction", "dust_scattered", "dust_thermal"):
        assert header["components"][name]["layer"] == "dust"
    assert "gas_scale_height" not in header["components"]["dust_extinction"]["fields"]
    # The form says how a layer's height may be given.
    assert "name of the array" in layers["form"]


def test_a_window_and_a_level_carry_the_layer_too():
    api = Service(grid=SMALL)
    whole = np.asarray(render(api, DEFAULT_MODEL)[1]["dust_height"])
    header, arrays = render(api, DEFAULT_MODEL, r_min="4", r_max="10", phi_min="0.5", phi_max="1.5")
    first, n = header["window"]["R"]["first"], header["window"]["R"]["n"]
    np.testing.assert_array_equal(np.asarray(arrays["dust_height"]), whole[first:first + n])
    header, arrays = render(api, DEFAULT_MODEL, level="1", r_min="4", r_max="10", phi_min="0.5", phi_max="1.5")
    cells = np.asarray(arrays["dust_height"])
    assert header["axes"]["dust_height"] == ["cell"] and cells.shape == (header["window"]["cells"]["count"],)
    # A cell's height is a mean of its rings': inside the rings' own range over the window, and above the
    # inner disc's (the flare).
    assert np.nanmin(cells) > np.nanmin(whole) and np.nanmax(cells) < np.nanmax(whole[np.isfinite(whole)])
    f4 = np.asarray(render(api, DEFAULT_MODEL, precision="f4")[1]["dust_height"])
    assert f4.dtype == np.float32 and np.allclose(f4, whole, rtol=1e-6, equal_nan=True)


# --- debt #128: the heating is still one mixed slab ---------------------------------------------------


def layered_escape(tau: float, ratio: float, n: int = 4000) -> float:
    """The share of light emitted isotropically by stars in a sech² layer that escapes a purely absorbing dust
    of vertical depth ``tau`` in a sech² layer ``ratio`` times as high: over the stars' cumulative share s, half
    of [E₂(τ A) + E₂(τ B)], A the dust's share above the emitter and B the share below it."""
    s = (np.arange(n) + 0.5) / n
    z = 2.0 * np.arctanh(2.0 * s - 1.0)  # the emitter's height in the stars' scale heights
    above = 0.5 * (1.0 - np.tanh(z / (2.0 * ratio)))
    return float(np.mean(0.5 * (expn(2, tau * above) + expn(2, tau * (1.0 - above)))))


@pytest.mark.parametrize("tau", [0.05, 0.5, 2.0, 12.0])
def test_the_layered_escape_is_the_slab_s_when_the_layers_are_one(tau):
    """The quadrature against the dust stage's closed form, (1/2 − E₃(τ))/τ: two computations (B3)."""
    slab = 1.0 - float(dust.slab_absorbed_fraction(np.array([tau]))[0])
    # 5.6 × 10⁻⁶ at τ = 12, the midpoint rule across E₂'s logarithmic corner at the emitter's own height.
    assert layered_escape(tau, 1.0) == pytest.approx(slab, rel=2e-5)


def test_what_the_layered_geometry_would_absorb_is_recorded_not_applied(galaxy, prod):
    """Debt #128. The picture's dust sits in the gas's thin layer since D206; the dust stage still heats it as
    if it filled the stars'. A thin layer under a thick stellar disc absorbs at most about half of an opaque
    ring's light (the half that sets out towards it), where the mixed slab absorbs nearly all of it."""
    f, R = galaxy.fields, np.asarray(galaxy.grid.R)
    model = prod[0].get(DEFAULT_MODEL)
    light = np.asarray(f["disc_surface_brightness"], dtype=float)
    tau = (1.0 - float(model.constants["DUST_ALBEDO_V"].value)) * dust.optical_depth(f["dust_extinction_v"])
    ratio = np.asarray(f["gas_scale_height"], dtype=float) / float(f["thin_disc_scale_height"])
    area = 2.0 * math.pi * R * PC_PER_KPC**2
    slab = float(np.trapezoid(light * dust.slab_absorbed_fraction(tau) * area, R))
    assert slab == pytest.approx(float(f["dust_absorbed_luminosity"]), rel=1e-12)  # the stage's own number
    escape = np.array([layered_escape(t, r) if t > 0.0 and np.isfinite(r) else 1.0 for t, r in zip(tau, ratio)])
    layered = float(np.trapezoid(light * (1.0 - escape) * area, R))
    assert layered / slab == pytest.approx(0.7659, abs=0.002)
    assert slab / float(f["disc_luminosity"]) == pytest.approx(0.3415, abs=0.001)  # the published infrared share
    assert layered / float(f["disc_luminosity"]) == pytest.approx(0.2616, abs=0.001)
    # Ring by ring: 0.59 of the slab's at 0.5 kpc (τ_abs 11), 0.91 at the solar radius, the same beyond 12 kpc.
    absorbed = (1.0 - escape) / np.where(tau > 0.0, dust.slab_absorbed_fraction(tau), 1.0)
    assert at(R, absorbed, 0.5) == pytest.approx(0.590, abs=0.005)
    assert at(R, absorbed, 8.2) == pytest.approx(0.913, abs=0.005)
    assert at(R, absorbed, 12.0) == pytest.approx(0.995, abs=0.005)


# --- D207: the dust round each ring -------------------------------------------------------------------


def test_the_dust_is_placed_round_each_ring_by_the_pattern_s_contrast(model):
    """`dust_placement` is the published contrast, clipped at zero as the stars' and the HII regions' placement is:
    the dust's column at a cell over its ring's mean. It averages to 1, so every ring keeps its dust, and the
    ring's own arrays are untouched by it."""
    api = Service(grid=SMALL)
    header, arrays = render(api, model.name)
    got = api.handle("/api/arrays", {"model": [model.name], "fields": ["pattern_density_contrast"]})
    contrast = np.asarray(wire.decode(got.body)[1]["pattern_density_contrast"])
    placement = header["placement"]
    assert placement["dust"] == "dust_placement" and header["axes"]["dust_placement"] == ["R", "phi"]
    entry = placement["arrays"]["dust_placement"]
    assert entry["unit"] == "dimensionless" and entry["fields"] == ["pattern_density_contrast"] and entry["about"]
    np.testing.assert_array_equal(np.asarray(arrays["dust_placement"]), np.maximum(contrast, 0.0))
    assert float(np.abs(np.asarray(arrays["dust_placement"]).mean(axis=1) - 1.0).max()) < 1e-12
    # The same factor the HII regions' light is placed by; the scattered light is the model's own share of the
    # placed stars and is not a function of this array.
    assert np.asarray(arrays["dust_extinction"]).shape == (SMALL.n_R, 3)  # still the ring's mean column
    assert "dust_placement" not in header["components"]
    assert "times the dust's placement" in header["components"]["dust_extinction"]["about"]


def test_the_placement_rides_a_window_and_a_level_too():
    api = Service(grid=SMALL)
    whole = np.asarray(render(api, DEFAULT_MODEL)[1]["dust_placement"])
    header, arrays = render(api, DEFAULT_MODEL, r_min="4", r_max="10", phi_min="0.5", phi_max="1.5")
    r, p = header["window"]["R"], header["window"]["phi"]
    np.testing.assert_array_equal(np.asarray(arrays["dust_placement"]), whole[r["first"]:r["first"] + r["n"], p["first"]:p["first"] + p["n"]])
    header, arrays = render(api, DEFAULT_MODEL, level="1", r_min="4", r_max="10", phi_min="0.5", phi_max="1.5")
    cells = np.asarray(arrays["dust_placement"])
    assert header["axes"]["dust_placement"] == ["cell"] and cells.shape == (header["window"]["cells"]["count"],)
    assert whole.min() <= cells.min() and cells.max() <= whole.max()  # a cell's mean of the factor


def face_on_layered(tau: np.ndarray, ratio: float, n: int = 2000) -> np.ndarray:
    """The share of a ring's starlight a face-on view receives through the dust in front of it: over the stars'
    cumulative share s, exp(-tau A(s)), A the dust's share above the star (the layers as D206 draws them)."""
    s = (np.arange(n) + 0.5) / n
    above = 0.5 * (1.0 - np.tanh(2.0 * np.arctanh(2.0 * s - 1.0) / (2.0 * ratio)))
    return np.exp(-np.asarray(tau, dtype=float)[..., None] * above).mean(axis=-1)


def test_what_the_placement_does_to_a_ring_as_read_at_s50(prod):
    """D207's prediction, and the measurement. With the dust alone placed, a ring's face-on V light rises by less
    than the foreground screen's gain at every radius (half the stars are in front of the layer). With the stars
    placed by the same factor — as they are — light and dust coincide, and the ring's light falls a little
    instead: the arms are dimmed and reddened, not crossed by lanes."""
    out = run(prod[0].get(DEFAULT_MODEL), only=FIELDS + ("pattern_density_contrast",))
    f, R = out.fields, np.asarray(out.grid.R)
    c = np.maximum(np.asarray(f["pattern_density_contrast"], dtype=float), 0.0)
    tau = dust.optical_depth(f["dust_extinction_v"])
    ratio = np.asarray(f["gas_scale_height"], dtype=float) / float(f["thin_disc_scale_height"])
    read = {}
    for radius in (4.0, 6.0, 8.2):
        i = int(np.argmin(np.abs(R - radius)))
        even = float(face_on_layered(np.array([tau[i]]), ratio[i])[0])
        dust_only = float(face_on_layered(tau[i] * c[i], ratio[i]).mean()) / even - 1.0
        both = float((c[i] * face_on_layered(tau[i] * c[i], ratio[i])).mean()) / even - 1.0
        screen = float(np.exp(-tau[i] * c[i]).mean()) / math.exp(-tau[i]) - 1.0
        on_arm = float(face_on_layered(np.array([tau[i] * c[i].max()]), ratio[i])[0])
        gap = float(face_on_layered(np.array([tau[i] * c[i].min()]), ratio[i])[0])
        assert 0.0 < dust_only < screen, radius  # the prediction (B4)
        read[radius] = (dust_only, both, screen, on_arm, gap)
    assert read[4.0][:3] == pytest.approx((0.0080, -0.0004, 0.0920), abs=0.0005)
    assert read[6.0][:3] == pytest.approx((0.0082, -0.0098, 0.0327), abs=0.0005)
    assert read[8.2][:3] == pytest.approx((0.0031, -0.0128, 0.0089), abs=0.0005)
    # What an arm and a gap let through at the solar ring: 0.747 against 0.874, so the dust takes 15 % more of
    # an arm's light than of a gap's — against a stellar contrast of 1.40 to 0.60 it mutes the arm, it does not
    # darken it below the gap.
    assert read[8.2][3:] == pytest.approx((0.747, 0.874), abs=0.002)
    assert read[6.0][3:] == pytest.approx((0.590, 0.747), abs=0.002)


def test_the_heating_is_still_the_ring_s_mean_column_s(prod):
    """Debt #128's second half (D207). The dust stage absorbs at each ring's mean column. With light and dust
    both placed by the contrast the same mixed slab would absorb more — the arms hold more of both — by 1.3 %
    over the disc and 4 % at the solar ring: measured here, not applied."""
    model = prod[0].get(DEFAULT_MODEL)
    out = run(model, only=FIELDS + ("pattern_density_contrast",))
    f, R = out.fields, np.asarray(out.grid.R)
    c = np.maximum(np.asarray(f["pattern_density_contrast"], dtype=float), 0.0)
    tau = (1.0 - float(model.constants["DUST_ALBEDO_V"].value)) * dust.optical_depth(f["dust_extinction_v"])
    light = np.asarray(f["disc_surface_brightness"], dtype=float) * 2.0 * math.pi * R * PC_PER_KPC**2
    mean = dust.slab_absorbed_fraction(tau)
    placed = np.array([np.mean(ci * dust.slab_absorbed_fraction(t * ci)) for t, ci in zip(tau, c)])
    assert float(np.trapezoid(light * placed, R) / np.trapezoid(light * mean, R)) == pytest.approx(1.0126, abs=0.0005)
    assert at(R, placed / mean, 8.2) == pytest.approx(1.041, abs=0.002)
    assert at(R, placed / mean, 2.0) == pytest.approx(1.001, abs=0.002)
