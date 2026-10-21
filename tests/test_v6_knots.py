"""S64 (BUILD_III Phase V6; RULING_S64 R5-R6): the HII regions as knots at whole-galaxy scale, the API side.

R5: ``/api/clusters`` with ``filters=`` carries ``line_response`` (N x filters, Lsun): each cluster's HII region's
Halpha through each curve plus every other line the field's HII layers carry (Hbeta by the region's Balmer
decrement, the four forbidden lines by their ratios), each at its own wavelength - the lines of ``/api/render``'s
``halpha_hii`` and ``lines_hii``, one for one. The header ``knots`` names the light, the size (R6: the Stromgren
radius) and the naming cell, the level-0 layout, and the rule: in a level-0 cell c the field's HII layers are scaled
by 1 - D_c / K_c. Gate (ii): over whole cells, points + scaled field = the census's Halpha when every knot is drawn and
the field's when none is, each to 1e-12, with the field's cell values from ``/api/render?level=0`` (the probe's
``pBC_knots.py``). Every check recomputes from published columns with this file's own arithmetic, never the module's.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pytest

import layer_reference
from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.stages import spectra
from galaxy.stages.systems import cell_bounds

RINGS, SECTORS = 32, 32
CASES = [(t, layer) for t in ("milky_way", "ngc_4414") for layer in ("on", "off")]
# Three curves that see the lines differently: a box round Halpha and [N II] and [S II], one round Hbeta and [O III],
# and one on vacuum wavelengths round Halpha alone (air to vacuum, as the render reads it).
CURVES = json.dumps([
    {"name": "red", "shape": "box", "centre": 6650.0, "width": 220.0},
    {"name": "blue", "shape": "box", "centre": 4935.0, "width": 180.0},
    {"name": "ha", "shape": "gaussian", "centre": 6564.6, "fwhm": 12.0, "wavelengths": "vacuum"},
])
# A box round Halpha alone, for the field's cell values (the probe's).
HALPHA_BOX = json.dumps([{"name": "ha", "shape": "box", "centre": 6564.0, "width": 200.0}])
# The knots' Halpha over the field's whole-disc Halpha (sum of hii_halpha_luminosity over the trapezoid integral of
# halpha_surface_brightness_hii * 2 pi R), measured at S64 (the probe's 0.921 and 1.081): a check on the census
# against the field, recorded, never a target. Layer on and off alike (the ring-first draw).
DISC_RATIO = {"milky_way": 0.9215601826222295, "ngc_4414": 1.081882028213476}
# S70 (D234): was {"milky_way": 0.9207954271231651, "ngc_4414": 1.0814612378969841} - the clouds' three regimes (#192,
# NGC 4414 on its own molecular ring) and the ring draw's fix (clouds.ring_birth_radius); the HII regions follow
# their clouds.
# The per-ring ratio's range over the lit rings (measured, recorded: the census's own heavy-tailed Poisson noise).
# S70 (D234): milky_way was (0.531, 1.428) - the clouds' three regimes (#192) and the ring draw's fix; ngc_4414's
# range moved inside the 1e-3 it is read to (0.371131, 2.149445).
RING_RANGE = {"milky_way": (0.535, 1.428), "ngc_4414": (0.371, 2.149)}
FORBIDDEN = ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")
# The share of the field's HII Halpha in level-0 cells that name no knot (measured at S64, recorded): Halpha no knot
# realised, which the knots replace when all are drawn (the rule gives such a cell 1 - d, d the disc's drawn share).
EMPTY_CELLS_FIELD = {("milky_way", "on"): 0.012877, ("milky_way", "off"): 0.012878, ("ngc_4414", "on"): 0.055367, ("ngc_4414", "off"): 0.057198}


@pytest.fixture(scope="module")
def service():
    return Service()


_held: dict = {}


def get(service, path, **q):
    key = (path, tuple(sorted(q.items())))
    if key not in _held:
        r = service.handle(path, {k: [str(v)] for k, v in q.items()})
        assert r.status == 200, r.body[:400]
        _held[key] = wire.decode(r.body)
    return _held[key]


def knots(service, template, layer, curves=CURVES):
    return get(service, "/api/clusters", template=template, layer=layer, filters=curves)


@pytest.mark.parametrize("template,layer", CASES)
def test_line_response_is_each_region_s_lines_through_each_curve(service, template, layer):
    """(a) line_response per cluster against this file's arithmetic: Halpha, Hbeta = Halpha / decrement and each
    forbidden line = Halpha x ratio, each through each curve at its wavelength (vacuum where the curve asks), summed."""
    header, a = knots(service, template, layer)
    curves = spectra.parse_curves(json.loads(CURVES))
    L = np.asarray(a["hii_halpha_luminosity"], dtype=float)
    lines = {"halpha": L, "hbeta": L / np.asarray(a["hii_balmer_decrement"], dtype=float)}
    lines |= {n: L * np.asarray(a[f"hii_{n}_ratio"], dtype=float) for n in FORBIDDEN}
    want = np.zeros((L.size, len(curves)))
    for n, light in lines.items():
        air = spectra.LINE_WAVELENGTHS[n]
        for k, c in enumerate(curves):
            at = spectra.air_to_vacuum(air) if c.wavelengths == "vacuum" else air
            want[:, k] += light * float(c.at(np.array([at]))[0])
    got = np.asarray(a["line_response"], dtype=float)
    assert got.shape == (L.size, 3) and np.isfinite(got).all() and (L > 0).all()
    np.testing.assert_allclose(got, want, rtol=1e-12, atol=0)
    # The vacuum curve sees Halpha at its vacuum wavelength: through it the knot is (nearly) its Halpha alone.
    assert np.all(got[:, 2] > 0.9 * L)
    assert header["line_response"]["unit"] == "Lsun" and "never both whole" in header["line_response"]["about"]


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_the_knots_carry_the_field_s_lines_one_for_one(service, template):
    """The knots' lines are the field's: halpha_hii's Halpha and lines_hii's lines, by name and wavelength."""
    header, _ = knots(service, template, "on")
    rh, _ = get(service, "/api/render", template=template, filters=CURVES)
    field = ["halpha", *rh["components"]["lines_hii"]["lines"]]
    k = header["knots"]
    assert sorted(k["lines"]) == sorted(field) and k["unmatched"] == []
    lines = header["line_response"]["lines"]
    assert list(lines) == list(k["lines"])
    for n, entry in k["lines"].items():
        assert entry["wavelength"] == lines[n]["wavelength"] == spectra.LINE_WAVELENGTHS[n]
        if n != "halpha":
            assert lines[n]["transmission"] == rh["components"]["lines_hii"]["lines"][n]["transmission"]
    assert lines["halpha"]["transmission"] == rh["components"]["halpha_hii"]["transmission"]
    # The knots entry is the same with filters= or without.
    plain, _ = get(service, "/api/clusters", template=template, layer="on")
    assert plain["knots"] == k


@pytest.mark.parametrize("template,layer", CASES)
def test_the_knots_against_the_field_per_ring_and_over_the_disc(service, template, layer):
    """(b) The knots' Halpha over the field's, per level-0 ring (by the naming cell) and over the disc: recorded, the
    disc-wide pinned at 1e-6 relative as a measured check, never a target."""
    _, a = get(service, "/api/clusters", template=template, layer=layer)
    _, f = get(service, "/api/arrays", template=template, layer=layer, fields="halpha_surface_brightness_hii")
    R = service.grid.R
    hii = np.asarray(f["halpha_surface_brightness_hii"], dtype=float)
    L = np.asarray(a["hii_halpha_luminosity"], dtype=float)
    total = float(np.trapezoid(hii * 2.0 * math.pi * R, R)) * 1.0e6
    assert L.sum() / total == pytest.approx(DISC_RATIO[template], rel=1e-6)
    edges = np.linspace(R[0], R[-1], RINGS + 1)
    ring_field = np.array([
        float(np.trapezoid(np.where((R >= edges[i]) & (R <= edges[i + 1]), hii * 2.0 * math.pi * R * 1.0e6, 0.0), R))
        for i in range(RINGS)
    ])
    ring_knots = np.bincount(np.asarray(a["cell"]) // SECTORS, weights=L, minlength=RINGS)
    lit = ring_knots > 0
    ratio = ring_knots[lit] / ring_field[lit]
    lo, hi = RING_RANGE[template]
    assert ratio.min() == pytest.approx(lo, abs=1e-3) and ratio.max() == pytest.approx(hi, abs=1e-3)


@pytest.mark.parametrize("template,layer", CASES)
def test_gate_ii_points_plus_the_scaled_field_close_on_whole_cells(service, template, layer):
    """(c) Gate (ii): with the field's cell values from /api/render?level=0 (a box round Halpha, over its transmission,
    times the cell's area) and K_c the Halpha of the knots each cell names, the scaled field F_c (1 - D_c / K_c) plus
    the drawn D_c is the census's Halpha with every knot drawn and the field's with none, to 1e-12; any subset gives
    a share in [0, 1]. The render's cells are the knots' naming cells: the same ids, the same edges as the layout."""
    header, a = get(service, "/api/clusters", template=template, layer=layer)
    rh, ra = get(service, "/api/render", template=template, layer=layer, filters=HALPHA_BOX, level=0)
    R = service.grid.R
    cells = np.asarray(ra["cell"], dtype=np.int64)
    layout = header["knots"]["layout"]
    assert sorted(cells.tolist()) == list(range(RINGS * SECTORS))
    for c in (0, 31, 32 * 7 + 3, 1023):
        b = cell_bounds(R, c, 0)
        ring, sector = divmod(c, SECTORS)
        assert (b["r_lo"], b["r_hi"]) == (layout["ring_edges"][ring], layout["ring_edges"][ring + 1])
        assert (b["phi_lo"], b["phi_hi"]) == (layout["sector_edges"][sector], layout["sector_edges"][sector + 1])
    named = np.asarray(a["cell"], dtype=np.int64)
    assert set(named.tolist()) <= set(cells.tolist())
    transmission = rh["components"]["halpha_hii"]["transmission"][0]
    area = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) * 1.0e6
                     for b in (cell_bounds(R, int(c), 0) for c in cells)])
    F = np.asarray(ra["halpha_hii"], dtype=float)[:, 0] / transmission * area
    L = np.asarray(a["hii_halpha_luminosity"], dtype=float)
    K = np.bincount(named, weights=L, minlength=RINGS * SECTORS)[cells]

    def share(D):
        # The rule (the lead's amendment of R5): 1 - D_c / K_c; a cell naming no knot 1 - d, d the drawn share of all.
        d = D.sum() / K.sum()
        return np.where(K > 0, 1.0 - np.divide(D, K, out=np.zeros_like(D), where=K > 0), 1.0 - d)

    every, none = K.copy(), np.zeros_like(K)
    # Every knot drawn: the field term is 0 in EVERY cell, a knotless one too, and the screen is the census; none: the field.
    named_any = K > 0
    assert (F * share(every)).sum() == 0.0
    assert (F * share(every)).sum() + every.sum() == pytest.approx(L.sum(), rel=1e-12)
    assert (F * share(none)).sum() + none.sum() == pytest.approx(F.sum(), rel=1e-12)
    # The field's HII Halpha in cells that name no knot - Halpha no knot realised: a measured check, recorded.
    assert F[~named_any].sum() / F.sum() == pytest.approx(EMPTY_CELLS_FIELD[(template, layer)], abs=5e-5)
    # Between: half the knots drawn (every other row), each cell's share in [0, 1], a knotless cell's the disc's.
    drawn = np.bincount(named[::2], weights=L[::2], minlength=RINGS * SECTORS)[cells]
    s = share(drawn)
    assert s.min() >= 0.0 and s.max() <= 1.0
    assert np.all(s[~named_any] == 1.0 - drawn.sum() / K.sum())
    assert (F * s).sum() + drawn.sum() == pytest.approx(float(np.sum(F * s + drawn)), rel=1e-12)
    # K_c / F_c per cell, recorded (the probe's median 0.388, p90 1.67 on the Milky Way, layer on).
    ok = F > 0
    if template == "milky_way" and layer == "on":
        assert float(np.median(K[ok] / F[ok])) == pytest.approx(0.388, abs=0.002)
        assert float(np.percentile(K[ok] / F[ok], 90)) == pytest.approx(1.67, abs=0.01)


@pytest.mark.parametrize("template", ["milky_way", "ngc_4414"])
def test_the_same_knots_with_the_layer_on_and_off(service, template):
    """(d) The ring-first draw: layer on and off, the same knots - the same rows' Halpha, the same Halpha per ring
    (K summed over a ring's cells, to rounding) - placed round each ring by the pattern or not, so K_c per cell moves."""
    _, on = get(service, "/api/clusters", template=template, layer="on")
    _, off = get(service, "/api/clusters", template=template, layer="off")
    L1, L0 = (np.asarray(x["hii_halpha_luminosity"], dtype=float) for x in (on, off))
    assert L1.size == L0.size and np.array_equal(np.sort(L1), np.sort(L0))
    k1, k0 = (np.bincount(np.asarray(x["cell"]) // SECTORS, weights=np.asarray(x["hii_halpha_luminosity"], dtype=float),
                          minlength=RINGS) for x in (on, off))
    np.testing.assert_allclose(k1, k0, rtol=1e-12, atol=0)


def test_the_headers_state_the_rule(service):
    """(e) The clusters header's knots entry and the render's two HII abouts state the rule and the closure."""
    header, _ = get(service, "/api/clusters", template="milky_way", layer="on")
    k = header["knots"]
    assert (k["light"], k["size"], k["cell"], k["column"]) == ("hii_halpha_luminosity", "hii_stromgren_radius", "cell", "line_response")
    assert "1 - D_c / K_c" in k["rule"] and "1 - d, d the drawn share of the whole disc's knots' Halpha" in k["rule"]
    assert "census exactly" in k["rule"] and "a knotless one too" in k["closure"] and "1.29 %" in k["closure"]
    assert "never negative" in k["closure"] and "bubble" in k["about"] and "2.7 %" in k["about"]
    assert "line_response" not in header["columns"]
    rh, _ = get(service, "/api/render", template="milky_way", filters=CURVES)
    for name in ("halpha_hii", "lines_hii"):
        assert k["rule"] in rh["components"][name]["about"], name


def test_the_s55_digest_takes_the_knots_apart(service):
    """(f) The S55 digest: the clusters' knots entry and line_response are digested apart and reported added
    (D223's handling); the render's HII abouts are held to S55's words with the knots' sentence taken out."""
    got = layer_reference.route_digest(service, "/api/clusters", {
        "model": ["basic"], "r_min": ["7.5"], "r_max": ["9"], "phi_min": ["0.2"], "phi_max": ["0.9"],
        "filters": [layer_reference.curves()], "layer": ["off"]})
    assert got["added"] == ["line_response", "knots"]
    assert "line_response" not in [a[0] for a in got["arrays"]]
