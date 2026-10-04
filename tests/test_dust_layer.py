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
    values laid round the ring in the order of that sum - S51's histogram on every ring, the crest 2.93 of the
    ring's mean at R₀ where one mode's was 3.07): dust alone +2.39 %, +4.44 %, +1.75 % at 4, 6 and 8.2 kpc, under
    the screen's +27.0 %, +17.3 %, +5.00 % (D207's prediction still holds); with the stars on c the ring's light
    rises 0.83 % at 4 kpc and 1.88 % at 6 kpc and **falls 1.15 % at R₀**. So D210's prediction (i) **fails on this
    field as it failed at S51** (−0.85 %), for the reason given there: the ridge's crest is where the stellar sum is
    highest (c = 1.62 there). (ii) held, −1.15 % against +5.00 %; (iii) held, the crest lets through 0.588, a gap
    0.881, the stellar flank 0.870 (the even ring's 0.805). (S56's first reading of the gas, the exponential of the
    modes' sum, was built and retired in the same session; on its far narrower ridge the ring's light rose 2.18 %.)"""
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
    assert read[4.0][:3] == pytest.approx((0.0239, 0.0083, 0.2704), abs=0.0005)
    assert read[6.0][:3] == pytest.approx((0.0444, 0.0188, 0.1735), abs=0.0005)
    assert read[8.2][:3] == pytest.approx((0.0175, -0.0115, 0.0500), abs=0.0005)
    # D210 (i), read and failed: the ring's light at R₀ still falls with the dust on the ridge (less than D207's
    # -1.28 %; S51 read -0.85 %, S56's ranked ridge on five modes -1.15 %).
    assert read[8.2][1] < 0.0 and read[8.2][1] > -0.0128
    # D210 (ii), held: under the screen's gain.
    assert read[8.2][1] < read[8.2][2]
    # D210 (iii), held: at R₀ the ridge's crest lets through less than D207's arm (0.747), a gap more than its 0.874.
    assert read[8.2][3:] == pytest.approx((0.588, 0.881, 0.870), abs=0.002)  # S56 (D215): was (0.579, 0.886, 0.883)
    assert read[8.2][3] < 0.747 and read[8.2][4] > 0.874
    # S56 (D215): was (0.467, 0.765, 0.754); S50 crest and gap: (0.590, 0.747)
    assert read[6.0][3:] == pytest.approx((0.469, 0.764, 0.732), abs=0.002)
    assert read[4.0][3:] == pytest.approx((0.450, 0.577, 0.520), abs=0.002)  # S56 (D215): was (0.451, 0.576, 0.531)


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
    order of that sum). The mixed slab: 1.0052 over the disc, 1.034 at R₀, 1.001 at 2 kpc. The layered geometry:
    **1.0014 over the disc, 1.025 at R₀, 0.9995 at 2 kpc** (0.9992 at 4 kpc, 1.076 at 12 kpc). The placement's
    effect on the disc's absorbed power is +0.14 % where it was +0.07 %: the same histogram of dust round each ring
    as one mode's, set on a stellar crest that is higher where five modes meet (c reaches 1.62 at R₀, not 1.40).
    Still measured and not applied (#128's second half). Read on **every** azimuth now: a ranked ridge has corners,
    and a ring's mean over every fourth of its cells is the full grid's only to 7e-3 (every second, 1e-3) where one
    mode's analytic ridge gave 5e-10 - so the layered quadrature runs on 360 cells a ring, four times the work."""
    model = prod[0].get(DEFAULT_MODEL)
    out = run(model, only=FIELDS + ("pattern_density_contrast", "gas_density_contrast"))
    f, R = out.fields, np.asarray(out.grid.R)
    c = np.maximum(np.asarray(f["pattern_density_contrast"], dtype=float), 0.0)
    g = np.maximum(np.asarray(f["gas_density_contrast"], dtype=float), 0.0)
    tau = (1.0 - float(model.constants["DUST_ALBEDO_V"].value)) * dust.optical_depth(f["dust_extinction_v"])
    light = np.asarray(f["disc_surface_brightness"], dtype=float) * 2.0 * math.pi * R * PC_PER_KPC**2
    mean = dust.slab_absorbed_fraction(tau)
    placed = np.array([np.mean(ci * dust.slab_absorbed_fraction(t * gi)) for t, ci, gi in zip(tau, c, g)])
    # S56 (D215): was 1.0045 (S51, one mode's ridge); S50: 1.0126
    assert float(np.trapezoid(light * placed, R) / np.trapezoid(light * mean, R)) == pytest.approx(1.0052, abs=0.0005)
    assert at(R, placed / mean, 8.2) == pytest.approx(1.034, abs=0.002)  # S56 (D215): was 1.023; S50: 1.041
    assert at(R, placed / mean, 2.0) == pytest.approx(1.001, abs=0.002)  # S50: 1.001
    # S56 (D215): was `every = 4` - every fourth azimuth carried the ring's mean of the placement to rounding on
    # one mode's analytic ridge. A ranked ridge's subsample does not (7e-3 on every fourth, 1e-3 on every second:
    # measured below), so the layered quadrature reads every cell.
    for step, off in ((4, 7e-3), (2, 1.1e-3)):
        sub = (c[:, ::step] * dust.slab_absorbed_fraction(tau[:, None] * g[:, ::step])).mean(axis=1)
        assert float(np.max(np.abs(sub[placed > 0.0] / placed[placed > 0.0] - 1.0))) == pytest.approx(off, rel=0.2), step
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
    # S56 (D215): was 1.0007 (one mode's ridge); S52 (D211): was 1.0045 (mixed slab)
    assert float(np.trapezoid(light * placed, R) / np.trapezoid(light * mean, R)) == pytest.approx(1.0014, abs=0.0005)
    assert at(R, q, 8.2) == pytest.approx(1.025, abs=0.002)  # S56 (D215): was 1.014; S52 (D211): was 1.023 (mixed slab)
    assert at(R, q, 2.0) == pytest.approx(0.9995, abs=0.002)  # S52 (D211): was 1.001 (mixed slab)
    assert at(R, q, 4.0) == pytest.approx(0.9992, abs=0.002)  # S56 (D215): was 0.9974
