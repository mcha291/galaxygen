"""The dust in its own layer and round each ring (S50, D206 and D207; debt #109's layer, debt #128's record;
round each ring by the gas's own contrast since S51, D210 Phase 2; heated in its own layer since S52, D211).

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
- **debt #128's first half, applied (S52, D211)**: until S52 the dust stage heated the dust as one uniformly
  mixed slab. What the layered geometry absorbs — the escape of light emitted isotropically by stars in their
  layer through a dust in its own — was computed at S50 by an independent quadrature and pinned, not applied:
  0.766 of the slab's, an infrared share of 0.262 of the disc's light against the published 0.342. Since S52 the
  stage absorbs in that geometry (``dust.layered_absorbed_fraction``, a fixed quadrature on another path), and
  the same independent quadrature is what its numbers are checked against here;
- **debt #128's second half, measured and not applied**: the heating at the ring's mean column against the light
  and the dust placed round the ring.
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


# --- debt #128's first half: the heating in the layers the dust is drawn in (S52, D211) -----------------


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


def test_the_layered_geometry_is_applied(galaxy, prod):
    """Debt #128's first half, closed at S52 (D211). The picture's dust sits in the gas's thin layer since D206; until
    S52 the dust stage heated it as if it filled the stars'. A thin layer under a thick stellar disc absorbs at most
    about half of an opaque ring's light (the half that sets out towards it), where the mixed slab absorbs nearly
    all of it.

    **The record, S50, and D211's predictions (B4), judged on these numbers:** the layered geometry absorbs 0.766 of
    the slab's (1.5675e10 -> 1.2006e10 Lsun; predicted 0.766 to 0.3 %, **held**, 0.76594); the infrared share of the
    disc's light 0.3415 -> 0.2616 (± 0.001, **held**, 0.26157); ring by ring 0.590 of the slab's at 0.5 kpc (τ_abs
    11), 0.913 at R₀, 0.995 at 12 kpc (± 0.005, **held**: 0.5902, 0.9128, 0.9945). The stage's absorbed light
    against the independent 4000-point quadrature: 7.6e-7 at worst per ring (the reference's own midpoint error),
    1.2e-9 over the disc."""
    f, R = galaxy.fields, np.asarray(galaxy.grid.R)
    model = prod[0].get(DEFAULT_MODEL)
    light = np.asarray(f["disc_surface_brightness"], dtype=float)
    tau = (1.0 - float(model.constants["DUST_ALBEDO_V"].value)) * dust.optical_depth(f["dust_extinction_v"])
    ratio = np.asarray(f["gas_scale_height"], dtype=float) / float(f["thin_disc_scale_height"])
    area = 2.0 * math.pi * R * PC_PER_KPC**2
    slab = float(np.trapezoid(light * dust.slab_absorbed_fraction(tau) * area, R))
    escape = np.array([layered_escape(t, r) if t > 0.0 and np.isfinite(r) else 1.0 for t, r in zip(tau, ratio)])
    layered = float(np.trapezoid(light * (1.0 - escape) * area, R))
    # Applied: the stage's own number is the independent quadrature's, to the reference's own error.
    assert float(f["dust_absorbed_luminosity"]) == pytest.approx(layered, rel=1e-8)  # S52 (D211): was the slab's, 1.5675e10
    per_ring = np.asarray(f["dust_absorbed_surface_brightness"], dtype=float)
    np.testing.assert_allclose(per_ring, light * (1.0 - escape), rtol=2e-6, atol=0.0)
    assert np.array_equal(per_ring > 0.0, np.isfinite(ratio))  # no gas height, nothing absorbed (D211 ruling 2)
    assert slab == pytest.approx(1.5675e10, rel=1e-4) and layered == pytest.approx(1.2006e10, rel=1e-4)
    assert layered / slab == pytest.approx(0.7659, abs=0.002)
    assert slab / float(f["disc_luminosity"]) == pytest.approx(0.3415, abs=0.001)  # the infrared share until S52
    assert layered / float(f["disc_luminosity"]) == pytest.approx(0.2616, abs=0.001)  # the published one since
    # Ring by ring: 0.59 of the slab's at 0.5 kpc (τ_abs 11), 0.91 at the solar radius, the same beyond 12 kpc.
    absorbed = (1.0 - escape) / np.where(tau > 0.0, dust.slab_absorbed_fraction(tau), 1.0)
    assert at(R, absorbed, 0.5) == pytest.approx(0.590, abs=0.005)
    assert at(R, absorbed, 8.2) == pytest.approx(0.913, abs=0.005)
    assert at(R, absorbed, 12.0) == pytest.approx(0.995, abs=0.005)


# --- the stage's quadrature (S52, D211) ---------------------------------------------------------------


@pytest.mark.parametrize("tau", [0.05, 0.5, 2.0, 12.0, 50.0])
def test_the_layered_fraction_is_the_slab_s_closed_form_when_the_layers_are_one(tau):
    """D211: if this fails the implementation is wrong, not the reading. 4e-14 at worst, measured at S52."""
    got = float(dust.layered_absorbed_fraction(np.array([tau]), np.array([1.0]))[0])
    assert got == pytest.approx(float(dust.slab_absorbed_fraction(np.array([tau]))[0]), rel=1e-12)


@pytest.mark.parametrize("ratio", [0.06, 0.32, 1.0, 3.7])
@pytest.mark.parametrize("tau", [0.05, 0.5, 2.0, 12.0, 50.0])
def test_the_layered_fraction_is_the_independent_quadrature_s(tau, ratio):
    """The stage's fixed quadrature (E₁ in the dust's share) against the 4000-point midpoint in the stars' share
    (E₂): two paths. They differ by the midpoint's own error, which grows once the dust's layer is the thicker
    (8.4e-6 at worst at ratio 2.5, read at S52), and is at rounding where the dust is the thinner."""
    got = float(dust.layered_absorbed_fraction(np.array([tau]), np.array([ratio]))[0])
    assert got == pytest.approx(1.0 - layered_escape(tau, ratio), rel=1e-5 if ratio > 0.5 else 1e-12)


def fine_escape(tau: float, ratio: float) -> float:
    """A third path, for the bound: the escape ∫ ½ sech²(x) [E₂(τA) + E₂(τ(1 − A))] dx over the stars' height x in
    units of 2h★, x ≥ 0, by the trapezoid on a step of min(0.01, ratio / 80) to x = 24 — exponentially convergent
    for a smooth integrand decaying as e^(−2x); it returns the slab's closed form at ratio 1 to 1.4e-14."""
    x = np.arange(0.0, 24.0, min(0.01, ratio / 80.0))
    weight = np.full_like(x, x[1])
    weight[0] *= 0.5
    above = 0.5 * (1.0 - np.tanh(x / ratio))
    return float((0.5 / np.cosh(x) ** 2 * (expn(2, tau * above) + expn(2, tau * (1.0 - above))) * weight).sum())


@pytest.mark.parametrize("ratio", [0.01, 0.06, 0.3, 1.5, 3.7, 10.0])
def test_the_layered_fraction_s_stated_bound(ratio):
    """The bound the function's docstring states: under 3e-11 of the absorbed share for ratios 0.01–10 and τ to
    1000 (2.5e-11 at worst, read at S52)."""
    tau = np.array([1e-6, 1e-4, 0.05, 0.5, 2.0, 12.0, 50.0, 300.0, 1000.0])
    got = dust.layered_absorbed_fraction(tau, np.full_like(tau, ratio))
    want = np.array([1.0 - fine_escape(t, ratio) for t in tau])
    np.testing.assert_allclose(got, want, rtol=3e-11, atol=0.0)


def test_the_layered_fraction_s_limits():
    """Zero without depth or without a layer; monotone in τ; and its two limits, derived. **A sheet of dust at the
    stars' midplane** (ratio -> 0): every star sees all the dust on one side, half its light sets out towards it,
    so the escape is ½ + ½ E₂(τ) and the absorbed share ½(1 − E₂(τ)); approached as O(ratio). **A sheet of stars
    in the middle of the dust** (ratio -> ∞): each star has half the column above and half below, so the escape
    is E₂(τ/2) and the absorbed share 1 − E₂(τ/2); approached as O(1/ratio²)."""
    zero = dust.layered_absorbed_fraction(np.array([0.0, 0.0, 2.0, 0.0]), np.array([0.3, np.nan, np.nan, np.inf]))
    assert np.all(zero == 0.0)  # no depth, or no dust layer (the ratio is NaN)
    small = dust.layered_absorbed_fraction(np.array([1e-9]), np.array([0.3]))[0]
    assert 0.0 < small < 1e-7
    tau = np.array([0.05, 0.5, 2.0, 12.0, 50.0])
    sheet = 0.5 * (1.0 - expn(2, tau))
    screen = 1.0 - expn(2, 0.5 * tau)
    np.testing.assert_allclose(dust.layered_absorbed_fraction(tau, np.zeros_like(tau)), sheet, rtol=1e-13)
    near = dust.layered_absorbed_fraction(tau, np.full_like(tau, 1e-6)) - sheet
    assert np.all(np.abs(near) < 2e-6) and np.all(near > 0.0)
    far = [dust.layered_absorbed_fraction(tau, np.full_like(tau, r)) - screen for r in (30.0, 100.0)]
    assert np.all(np.abs(far[1]) < np.abs(far[0])) and np.all(np.abs(far[1]) < 2e-5)
    np.testing.assert_allclose(dust.layered_absorbed_fraction(tau, np.full_like(tau, 1e4)), screen, rtol=1e-12)
    # A stellar layer of no height (the ratio infinite) is the sheet itself, not "no dust".
    np.testing.assert_allclose(dust.layered_absorbed_fraction(tau, np.full_like(tau, np.inf)), screen, rtol=1e-12)
    grid = np.geomspace(1e-9, 1e3, 2001)
    for ratio in (0.01, 0.06, 0.3, 1.0, 3.7, 10.0):
        kept = dust.layered_absorbed_fraction(grid, np.full_like(grid, ratio))
        assert np.all((kept > 0.0) & (kept < 1.0 + 3e-11)), ratio
        # Monotone until what escapes is down to the quadrature's bound (2.6e-11 at τ = 895, ratio 3.7, read at S52).
        clear = (1.0 - kept[1:]) > 1e-9
        assert np.all(np.diff(kept)[clear] > 0.0) and np.all(np.diff(kept) > -1e-11), ratio
    # The geometry's order at a fixed depth: the thinner the dust's layer under the stars', the less it absorbs.
    order = dust.layered_absorbed_fraction(np.full(5, 2.0), np.array([0.0, 0.06, 0.32, 1.0, 3.7]))
    assert np.all(np.diff(order) > 0.0)
    assert order[3] == pytest.approx(float(dust.slab_absorbed_fraction(np.array([2.0]))[0]), rel=1e-12)


# --- D207, and D210 since S51: the dust round each ring ----------------------------------------------

# A φ grid fine enough for the gas ridge's ring mean to be 1 to rounding. The ridge is a von Mises in m φ; on n_φ
# equal cells its grid mean picks up the harmonics whose order times m is a multiple of n_φ — on SMALL's 36 cells
# with four arms the ninth, I₉(κ)/I₀(κ) = 6.9e-4, so a ring's grid mean is 1 to 5.8e-4 there (read at S51). On
# 108 cells the first alias is the 27th harmonic, under 1e-15; the default grid's 360 is exact as well.
# S56 (D215): that was one four-armed mode's ridge, which is analytic. A ring of several modes is ranked - the
# ridge's values laid in the order of the modes' sum - and that ridge has corners, so on any grid a ring's sampled
# mean leaves 1 (by up to 9e-4 on the default 360 cells); the stage divides such a ring by its sampled mean (as it
# always did on 36 cells), which is what keeps the mean below to 1e-12 on this grid.
FINE_PHI = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=108)


def published(api: Service, model: str, *names: str) -> dict[str, np.ndarray]:
    got = api.handle("/api/arrays", {"model": [model], "fields": [",".join(names)]})
    arrays = wire.decode(got.body)[1]
    return {n: np.asarray(arrays[n], dtype=float) for n in names}


def test_the_dust_is_placed_round_each_ring_by_the_gas_s_own_contrast(model):
    """`dust_placement` is the published gas contrast (D210), clipped at zero as every placement is: the dust's
    column at a cell over its ring's mean, the gas the dust is a share of. Until S51 it was the stellar pattern's
    contrast (D207). It averages to 1, so every ring keeps its dust, and the ring's own arrays are untouched by it."""
    api = Service(grid=FINE_PHI)
    header, arrays = render(api, model.name)
    gas = published(api, model.name, "gas_density_contrast")["gas_density_contrast"]
    placement = header["placement"]
    assert placement["dust"] == "dust_placement" and header["axes"]["dust_placement"] == ["R", "phi"]
    entry = placement["arrays"]["dust_placement"]
    assert entry["unit"] == "dimensionless" and entry["fields"] == ["gas_density_contrast"]
    assert "the gas's own density contrast" in entry["about"] and "not the scattered light" in entry["about"]
    np.testing.assert_array_equal(np.asarray(arrays["dust_placement"]), np.maximum(gas, 0.0))
    # S57 (D216 G3 item 4): the first build had re-pinned this to 1.715e-6 - its field was the gas's response at the
    # cells' centres, whose sampled mean on this grid's 108 cells is off 1 by that. The published field is the
    # law's exact mean over each grid cell's extent in azimuth, at the ring's own radius: a ring's cells average to 1 to rounding on any grid, with nothing divided.
    assert float(np.abs(np.asarray(arrays["dust_placement"]).mean(axis=1) - 1.0).max()) < 1e-12
    # The scattered light is the model's own share of the placed stars and is not a function of this array.
    assert np.asarray(arrays["dust_extinction"]).shape == (FINE_PHI.n_R, 3)  # still the ring's mean column
    assert "dust_placement" not in header["components"]
    assert "times the dust's placement" in header["components"]["dust_extinction"]["about"]


def test_the_hii_regions_follow_the_gas_and_the_stars_their_own_contrast(model):
    """D210 ruling 7: the HII regions sit in the clouds, which are gas, so their lines are placed by the gas's
    contrast — the same array as the dust's; the stars keep the stellar pattern's contrast."""
    api = Service(grid=SMALL)
    header, arrays = render(api, model.name)
    f = published(api, model.name, "gas_density_contrast", "pattern_density_contrast")
    gas, stellar = np.maximum(f["gas_density_contrast"], 0.0), np.maximum(f["pattern_density_contrast"], 0.0)
    np.testing.assert_array_equal(np.asarray(arrays["dust_placement"]), gas)
    for name in ("halpha_hii", "lines_hii"):
        value = np.asarray(arrays[name], dtype=float)
        ring = value[:, :1, :] / np.where(gas[:, :1] > 0.0, gas[:, :1], 1.0)[..., None]  # its ring's value, per filter
        np.testing.assert_allclose(value, ring * gas[..., None], rtol=1e-13, atol=0.0, err_msg=name)
        fields = header["components"][name]["fields"]
        assert "gas_density_contrast" in fields and "pattern_density_contrast" not in fields, name
        assert "gas's own density contrast" in header["components"][name]["about"], name
    stars = np.asarray(arrays["stars"], dtype=float)
    ring = stars[:, :1, :] / np.where(stellar[:, :1] > 0.0, stellar[:, :1], 1.0)[..., None]
    np.testing.assert_allclose(stars, ring * stellar[..., None], rtol=1e-13, atol=0.0)
    assert "pattern_density_contrast" in header["components"]["stars"]["fields"]
    assert "gas_density_contrast" not in header["components"]["stars"]["fields"]


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
    """D207's prediction and D210's, and the measurements — the stars on the stellar contrast c, the dust on the
    gas's ridge g since S51.

    **The record, S50 (D207), the dust on c as well:** with the dust alone placed a ring's face-on V light rose
    0.80 % at 4 kpc, 0.82 % at 6 and 0.31 % at R₀, under the foreground screen's 9.20 %, 3.27 % and 0.89 % (half
    the stars are in front of the layer); with the stars on the same factor it fell 0.04 %, 0.98 % and 1.28 %; an
    arm's crest let through 0.747 of its light at R₀ and a gap 0.874 (0.590 and 0.747 at 6 kpc): the arms dimmed
    and reddened by their own dust, not crossed by lanes.

    **Read at S51 (D210), the dust on g:** dust alone +1.84 %, +4.63 %, +1.97 % at 4, 6 and 8.2 kpc, under the
    screen's +20.8 %, +18.1 %, +5.63 % (D207's prediction still holds); with the stars on c the ring's light
    rises 0.79 % at 4 kpc and 1.72 % at 6 kpc but **still falls 0.85 % at R₀** (from 1.28 %). At R₀ the ridge's
    crest lets through 0.579 (D207: 0.747), a gap 0.886 (0.874) and the stellar arm's flank, where c is its ring
    mean, 0.883 — the even ring's 0.805: the dust has left the flank for the crest's stripe.

    **D210's predictions, judged on these numbers (B4, nothing changed to make one hold):** (i) the ring's light
    rises at R₀ — **failed**, −0.85 %: the ridge sits on the stellar crest (c = 1.40 there), and at R₀'s small
    depth (τ_V 0.47) the light lost is nearly linear in the column, so it goes as the overlap of c and g round the
    ring, which exceeds 1 when both peak together; the gain from the gaps is second order. At 4 and 6 kpc, deeper,
    the saturation of the crest wins and the ring brightens;
    (ii) under the screen's gain — held, −0.85 % against +5.63 % (and against S50's +0.89 %); (iii) the crest
    transmits less than 0.747 and a gap more than 0.874 at R₀ — held, 0.579 and 0.886.

    **Read again at S56 (D215), on five arm modes** (the stars on their sum c; the gas's ridge g one arm's ridge
    values laid round the ring in the order of that sum - S51's histogram on every ring; on the window of ruling 11
    the mask is at its cap at R₀ as S51's was, and the crest is 3.06 of the ring's mean where one mode's was 3.07):
    dust alone +2.33 %, +4.49 %, +1.99 % at 4, 6 and 8.2 kpc, under the screen's +26.4 %, +17.5 %, +5.68 % (D207's
    prediction still holds); with the stars on c the ring's light rises 0.92 % at 4 kpc and 1.64 % at 6 kpc and
    **falls 0.89 % at R₀**. So D210's prediction (i) **fails on this field as it failed at S51** (−0.85 %), for the
    reason given there: the ridge's crest is where the stellar sum is highest (c = 1.76 there). (ii) held, −0.89 %
    against +5.68 %; (iii) held, the crest lets through 0.578, a gap 0.887, the stellar flank 0.884 (the even
    ring's 0.805). (S56's first reading of the gas, the exponential of the modes' sum, was built and retired in the
    same session; on its far narrower ridge the ring's light rose 2.18 %. Its second pass, the ranked ridge on the
    X / 2 window, read −1.15 % at R₀.)

    **Read again at S57 (D216), the dust on the gas's steady response to the arm modes** (g the solved response:
    its crest as broad as the stellar arm and on it, its gaps nearly empty - the trough 0.025 of the ring's mean at
    R₀): dust alone +2.74 %, +5.47 %, +1.25 % at 4, 6 and 8.2 kpc, under the screen's +31.1 %, +21.7 %, +3.61 %
    (D207's prediction still holds); with the stars on c the ring's light rises 1.27 % at 4 kpc and 1.21 % at 6 kpc
    and **falls 1.82 % at R₀**. D210's (i) fails as before, **and by more than D207's own −1.28 %**: with the dust
    on a broad crest that sits on the stellar arm, more of it lies where the light is than when it followed the
    stars' contrast itself. (ii) held, −1.82 % against +3.61 %; (iii) held, the crest lets through 0.605, a gap
    0.994, the stellar flank 0.815. No lane crosses an arm on this field either: the arms dim by their own dust.

    **Read again at S58 (D217), the gas inside the bar's reach on the bar's lanes and the two-armed mode on the
    bar's axis** (g = w_arm s + w_bar L: at 4 kpc a base of two thirds of the ring's mean and two lanes of seven
    times it, the bar carrying 0.70 of the weight; the stars with the bar's body in c): dust alone +7.14 %, +5.31 %,
    +1.25 % at 4, 6 and 8.2 kpc, under the screen's +77.8 %, +21.0 %, +3.61 % (D207's prediction still holds); with
    the stars on c the ring's light rises 6.51 % at 4 kpc and 1.23 % at 6 kpc and falls 1.82 % at R₀ as at S57 -
    the solar ring is outside the bar's reach and is the ring it was. At 4 kpc the dust is gathered into lanes that
    cover little of the ring, so far more of the ring's light gets out: these are the model's first dust lanes
    across a bar, a synthetic template of a declared, unsourced width (D217 item 8). (i)-(iii) read at R₀ as at
    S57; the stellar flank there lets through 0.863 where it read 0.815 - the cell where c is nearest 1 is another
    cell with the two-armed mode's phase moved.

    **Read again at S59 (D218), the arms' winding laid in seeded segments.** Beyond the bar's half-length (5.21 kpc)
    a ring's stars and gas are turned together by the winding's phase there, and the ring reads as it did: 6 and
    8.2 kpc below are S58's rows to the fourth figure. Inside it the arm modes turn against the bar's body and
    lanes, which stay on the bar's axis, so c and g are other sums of the same parts: at 4 kpc dust alone +8.12 %
    under the screen's +88.8 %, and +6.91 % with the stars on c. The flank - the one cell where c is nearest 1 - is
    another cell on all three rings (0.831 at R₀, 0.626 at 6 kpc, 0.526 at 4 kpc)."""
    out = run(prod[0].get(DEFAULT_MODEL), only=FIELDS + ("pattern_density_contrast", "gas_density_contrast"))
    f, R = out.fields, np.asarray(out.grid.R)
    c = np.maximum(np.asarray(f["pattern_density_contrast"], dtype=float), 0.0)
    g = np.maximum(np.asarray(f["gas_density_contrast"], dtype=float), 0.0)
    tau = dust.optical_depth(f["dust_extinction_v"])
    ratio = np.asarray(f["gas_scale_height"], dtype=float) / float(f["thin_disc_scale_height"])
    read = {}
    for radius in (4.0, 6.0, 8.2):
        i = int(np.argmin(np.abs(R - radius)))
        even = float(face_on_layered(np.array([tau[i]]), ratio[i])[0])
        through = face_on_layered(tau[i] * g[i], ratio[i])
        dust_only = float(through.mean()) / even - 1.0
        both = float((c[i] * through).mean()) / even - 1.0
        screen = float(np.exp(-tau[i] * g[i]).mean()) / math.exp(-tau[i]) - 1.0
        crest = float(face_on_layered(np.array([tau[i] * g[i].max()]), ratio[i])[0])
        gap = float(face_on_layered(np.array([tau[i] * g[i].min()]), ratio[i])[0])
        flank = float(through[int(np.argmin(np.abs(c[i] - 1.0)))])  # the stellar arm's flank: c at its ring mean
        assert 0.0 < dust_only < screen, radius  # D207's prediction (B4), still held
        read[radius] = (dust_only, both, screen, crest, gap, flank)
    # S56 (D215): were (0.0184, 0.0079, 0.2083), (0.0463, 0.0172, 0.1806) and (0.0197, -0.0085, 0.0563) on one
    # four-armed mode (S51); S50: (0.0080, -0.0004, 0.0920), (0.0082, -0.0098, 0.0327), (0.0031, -0.0128, 0.0089).
    # S57 (D216): were (0.0233, 0.0092, 0.2639), (0.0449, 0.0164, 0.1754) and (0.0199, -0.0089, 0.0568) on S56's
    # ranked ridge.
    # S58 (D217): were (0.0274, 0.0127, 0.3110) and (0.0547, 0.0121, 0.2170) on S57's field, the bar's part of the
    # gas the stellar bar's cosine; R₀'s row below is unmoved.
    # S59 (D218): was (0.0714, 0.0651, 0.7778) at 4 kpc - inside the bar's half-length the arm modes, on the winding
    # laid in seeded segments, turn against the bar's body and lanes; the rows at 6 kpc and R₀, beyond it, are unmoved.
    assert read[4.0][:3] == pytest.approx((0.0812, 0.0691, 0.8885), abs=0.0005)
    assert read[6.0][:3] == pytest.approx((0.0531, 0.0123, 0.2104), abs=0.0005)
    assert read[8.2][:3] == pytest.approx((0.0125, -0.0182, 0.0361), abs=0.0005)
    # D210 (i), read and failed: the ring's light at R₀ still falls with the dust on the gas's pattern (S51 read
    # -0.85 %, S56's ranked ridge on five modes -0.89 %). S57 (D216): was `and read[8.2][1] > -0.0128` - "less than
    # D207's -1.28 %", which held on the narrow ridge and **does not hold on the gas's steady response: -1.82 %**.
    # The response's crest is as broad as the stellar arm and sits on it, so more of the dust lies where the light
    # is than when the dust followed the stars' own contrast (D207). Recorded as read, nothing changed to mend it.
    assert read[8.2][1] < 0.0 and read[8.2][1] < -0.0128
    # D210 (ii), held: under the screen's gain.
    assert read[8.2][1] < read[8.2][2]
    # D210 (iii), held: at R₀ the ridge's crest lets through less than D207's arm (0.747), a gap more than its 0.874.
    # S57 (D216): was (0.578, 0.887, 0.884); S56 (D215): was (0.579, 0.886, 0.883). The gaps are nearly empty of gas
    # now (the trough 0.025 of the ring's mean at R₀), so a gap lets through 0.994.
    # S58 (D217): was (0.605, 0.994, 0.815) - the crest and the gap are R₀'s as they were; the flank is the cell where
    # the stellar contrast is nearest its ring mean, another cell with the two-armed phase moved.
    # S59 (D218): was (0.606, 0.994, 0.863) - the crest and the gap are R₀'s as they were; the flank is another cell
    # again, the ring turned by the segments' winding (cell 239, where the gas stands at 0.84 of its mean; S58's was
    # cell 147, at 0.66).
    assert read[8.2][3:] == pytest.approx((0.606, 0.994, 0.831), abs=0.002)
    assert read[8.2][3] < 0.747 and read[8.2][4] > 0.874
    # S57 (D216): was (0.469, 0.765, 0.738); S56 (D215): was (0.467, 0.765, 0.754); S50 crest and gap: (0.590, 0.747)
    # S58 (D217): was (0.454, 0.935, 0.706)
    # S59 (D218): was (0.450, 0.911, 0.676) - the flank is another cell, the crest and the gap the ring's as they were
    assert read[6.0][3:] == pytest.approx((0.450, 0.911, 0.626), abs=0.002)
    # S57 (D216): was (0.452, 0.577, 0.520); S56 (D215): was (0.451, 0.576, 0.531)
    # S58 (D217): was (0.441, 0.630, 0.519) - the crest at 4 kpc is a lane's
    # S59 (D218): was (0.404, 0.641, 0.503) - inside the bar's half-length the arms turn against the lanes
    assert read[4.0][3:] == pytest.approx((0.403, 0.641, 0.526), abs=0.002)


def test_the_heating_is_still_the_ring_s_mean_column_s(prod):
    """Debt #128's second half (D207; D211 ruling 5). The dust stage absorbs at each ring's mean column. With the
    light and the dust placed round each ring it would absorb another amount: measured here, not applied (applying
    it would make the dust stage read seeded fields, and every dust number would move with the pattern's seed).

    **The record, in the mixed slab the stage heated in until S52.** S50 (D207), light and dust both on the stellar
    contrast: 1.0126 of the mean column's over the disc, 1.041 at the solar ring, 1.001 at 2 kpc (the slab
    saturated). S51 (D210), the light on the stellar contrast c and the dust on the gas's ridge g: 1.0045 over the
    disc, 1.023 at R₀, 1.001 at 2 kpc — the dust's ridge is narrower than the stars' arm, so less of it lies where
    the light is heaviest.

    **Read at S52 (D211), in the layered geometry the stage now heats in** (c and g as at S51, each cell's absorbed
    share the layered one at its column and the ring's ratio of heights): **1.0007 over the disc, 1.014 at R₀,
    0.9995 at 2 kpc** (0.9974 at 4 kpc, 1.069 at 12 kpc, where little light is): the placement's effect on the
    disc's absorbed power falls from 0.45 % to 0.07 %. A thin layer's share saturates sooner than the mixed slab's
    (it keeps little more than the half of the light that sets out towards it), so round a ring the gaps, which lose
    dust, lose more absorption than the crest gains, and that concavity now nearly cancels the gain from the gas's
    crest sitting on the stellar arm's (c and g peaking together). Read on every fourth azimuth of the 360 (the mixed slab's numbers on them are the full grid's to
    5e-10, asserted below), so that the layered quadrature runs on 90 cells a ring, not 360.

    **Read again at S56 (D215), on five arm modes** (c their sum, g S51's ridge values laid round each ring in the
    order of that sum; the window of ruling 11). The mixed slab: 1.0042 over the disc, 1.024 at R₀, 1.001 at 2 kpc.
    The layered geometry: **0.9998 over the disc, 1.014 at R₀, 0.9995 at 2 kpc** (0.9980 at 4 kpc, 1.017 at
    12 kpc). The placement's effect on the disc's absorbed power is −0.02 % where it was +0.07 %: the same
    histogram of dust round each ring as one mode's, on a stellar pattern of three to six modes whose arms end at
    12.3 kpc. Still measured and not applied (#128's second half). Read on **every** azimuth now: a ranked ridge has
    corners, and a ring's mean over every fourth of its cells is the full grid's only to 5e-3 (every second, 1e-3)
    where one mode's analytic ridge gave 5e-10 - so the layered quadrature runs on 360 cells a ring, four times the
    work. (S56's second pass, on the X / 2 window: 1.0052 and 1.034 in the slab; 1.0014, 1.025, 0.9992 at 4 kpc
    layered.)

    **Read again at S57 (D216), g the gas's steady response to the arm modes.** The mixed slab: 1.0069 over the
    disc, 1.052 at R₀, 1.001 at 2 kpc. The layered geometry: **1.0029 over the disc, 1.044 at R₀, 0.9995 at 2 kpc**
    (0.9950 at 4 kpc). The placement's effect on the disc's absorbed power is +0.29 % where S56's ranked ridge read
    −0.02 %: the response's crest is as broad as the stellar arm and sits on it, so the dust and the light peak
    together over more of the ring. Still measured and not applied (#128's second half). The response is smooth,
    and a subsample of the ring carries its mean again (3.2e-6 on every fourth cell); the quadrature still reads
    every cell.

    **Read again at S58 (D217), the gas inside the bar's reach on the bar's lanes.** The mixed slab: **0.9499 over
    the disc**, 1.052 at R₀ (the solar ring is the ring it was), 0.849 at 2 kpc. The layered geometry: **0.9652
    over the disc, 1.044 at R₀, 0.904 at 2 kpc** (0.941 at 4 kpc). The placement's effect on the disc's absorbed
    power is −3.5 % where S57 read +0.29 %: inside the bar most of each ring holds four tenths of its mean column
    and two lanes hold seven times it, saturated - so the ring absorbs less than at its mean column. Still measured
    and not applied; with lanes the gap between the ring's mean column and the placed one is no longer small, and
    #128's second half is a larger debt than it was (reported). A subsample of a ring no longer carries its mean
    inside the bar's reach (the lanes are a few cells wide: 7e-5 on every fourth cell).

    **Read again at S59 (D218), the arms' winding laid in seeded segments.** Beyond the bar's half-length (5.21 kpc)
    each ring's c and g are turned together and its absorbed share is the one it was (to 4e-9 in the mixed slab, the
    cells' sampling of a turned ring); inside it the arm modes turn against the bar's body and lanes. The mixed slab: 0.9504 over the
    disc, 1.052 at R₀, 0.853 at 2 kpc. The layered geometry: **0.9656 over the disc, 1.044 at R₀, 0.907 at 2 kpc**
    (0.939 at 4 kpc). The placement's effect on the disc's absorbed power is −3.4 % where S58 read −3.5 %. Still
    measured and not applied."""
    model = prod[0].get(DEFAULT_MODEL)
    out = run(model, only=FIELDS + ("pattern_density_contrast", "gas_density_contrast"))
    f, R = out.fields, np.asarray(out.grid.R)
    c = np.maximum(np.asarray(f["pattern_density_contrast"], dtype=float), 0.0)
    g = np.maximum(np.asarray(f["gas_density_contrast"], dtype=float), 0.0)
    tau = (1.0 - float(model.constants["DUST_ALBEDO_V"].value)) * dust.optical_depth(f["dust_extinction_v"])
    light = np.asarray(f["disc_surface_brightness"], dtype=float) * 2.0 * math.pi * R * PC_PER_KPC**2
    mean = dust.slab_absorbed_fraction(tau)
    placed = np.array([np.mean(ci * dust.slab_absorbed_fraction(t * gi)) for t, ci, gi in zip(tau, c, g)])
    # S57 (D216): was 1.0042 (S56's ranked ridge); S56 (D215): was 1.0045 (S51, one mode's ridge); S50: 1.0126
    # S58 (D217): was 1.0069 over the disc and 1.001 at 2 kpc. Inside the bar's reach the dust lies on the bar's
    # lanes: most of each ring is thinned to four tenths of its mean column and absorbs less, and the lanes, at seven
    # times it, are saturated and absorb little more - the placement takes 15 % off what a ring at 2 kpc absorbs and
    # 5.0 % off the disc's. The solar ring is the ring it was.
    # S59 (D218): were 0.9499 over the disc and 0.8485 at 2 kpc - inside the bar's half-length the arm modes, on the
    # winding laid in seeded segments, turn against the bar's body and lanes; the solar ring is the ring it was.
    assert float(np.trapezoid(light * placed, R) / np.trapezoid(light * mean, R)) == pytest.approx(0.9504, abs=0.0005)
    assert at(R, placed / mean, 8.2) == pytest.approx(1.052, abs=0.002)  # S57 (D216): was 1.024; S56 (D215): was 1.023; S50: 1.041
    assert at(R, placed / mean, 2.0) == pytest.approx(0.8525, abs=0.002)  # S59 (D218): was 0.8485; S58 (D217): was 1.001; S50: 1.001
    # S56 (D215): was `every = 4` - every fourth azimuth carried the ring's mean of the placement to rounding on
    # one mode's analytic ridge. A ranked ridge's subsample did not (4.8e-3 on every fourth, 1.1e-3 on every second),
    # so the layered quadrature reads every cell.
    # S57 (D216): were 4.8e-3 and 1.1e-3 (rel 0.2). The gas's response is smooth again and a subsample carries the
    # ring's mean: 3.2e-6 on every fourth cell, 1.2e-10 on every second. The quadrature still reads every cell.
    # S58 (D217): were `< 1e-5` and `< 1e-9`. A lane is a few cells wide inside the bar's reach, and a subsample of
    # the ring does not carry its mean there: 7.0e-5 on every fourth cell, 5.1e-6 on every second (beyond the
    # bar's reach the response is as smooth as it was). The quadrature reads every cell.
    read_sub = {}
    for step in (4, 2):
        sub = (c[:, ::step] * dust.slab_absorbed_fraction(tau[:, None] * g[:, ::step])).mean(axis=1)
        read_sub[step] = float(np.max(np.abs(sub[placed > 0.0] / placed[placed > 0.0] - 1.0)))
        beyond = (placed > 0.0) & (R > 7.0)
        assert float(np.max(np.abs(sub[beyond] / placed[beyond] - 1.0))) < {4: 1e-5, 2: 1e-9}[step], step
    # S59 (D218): were 7.0e-5 and 5.13e-6 - the rings are turned by the segments' winding, so a subsample reads
    # other cells of them; beyond 7 kpc the two bounds above hold as they did (1.9e-8 and 2.1e-14).
    assert read_sub[4] == pytest.approx(7.2e-5, rel=0.05) and read_sub[2] == pytest.approx(5.65e-6, rel=0.05)
    every = 1
    sub = (c[:, ::every] * dust.slab_absorbed_fraction(tau[:, None] * g[:, ::every])).mean(axis=1)
    assert np.allclose(sub, placed, rtol=1e-8, atol=0.0)
    # The layered geometry (S52, D211): the stage's own mean column, against the same placement.
    ratio = np.asarray(f["gas_scale_height"], dtype=float) / float(f["thin_disc_scale_height"])
    mean = dust.layered_absorbed_fraction(tau, ratio)
    placed = (c[:, ::every] * dust.layered_absorbed_fraction(tau[:, None] * g[:, ::every], ratio[:, None])).mean(axis=1)
    held = mean > 0.0
    assert np.array_equal(held, np.isfinite(ratio)) and np.all(placed[~held] == 0.0)
    q = np.where(held, placed / np.where(held, mean, 1.0), np.nan)
    # S57 (D216): was 0.9998 (S56's ranked ridge); S56 (D215): was 1.0007 (one mode's ridge); S52 (D211): was 1.0045 (mixed slab)
    # S58 (D217): was 1.0029 - the placement takes 3.5 % off the disc's absorbed power in the layered geometry: inside
    # the bar's reach the dust is on the lanes, and a ring thinned to four tenths of its mean column absorbs less
    # than the lanes' few saturated cells add. **Still measured and not applied** (#128's second half): the dust
    # stage heats at each ring's mean column, and with lanes that is no longer within a few parts in a thousand of
    # the placed geometry - reported to the lead.
    # S59 (D218): was 0.9652 - the rings inside the bar's half-length, where the arms turn against the lanes
    assert float(np.trapezoid(light * placed, R) / np.trapezoid(light * mean, R)) == pytest.approx(0.9656, abs=0.0005)
    # S57 (D216): was 1.014 (S55's, read again at S56); S52 (D211): was 1.023 (mixed slab)
    assert at(R, q, 8.2) == pytest.approx(1.044, abs=0.002)
    assert at(R, q, 2.0) == pytest.approx(0.9067, abs=0.002)  # S59 (D218): was 0.9036; S58 (D217): was 0.9995; S52 (D211): was 1.001 (mixed slab)
    assert at(R, q, 4.0) == pytest.approx(0.9387, abs=0.002)  # S59 (D218): was 0.9408; S58 (D217): was 0.9950; S57 (D216): was 0.9980; S56 (D215): was 0.9974
