"""Audit IV (S43): the renderer's gates, balances and redistributions re-derived at a mesh the build did not use.

V1–V4 and S42 asserted their gates on the default grid (``tests/test_render.py``, ``test_region_synthesis.py``) and
their identities on the coarse (120, 400, 6) (``test_v4.py``, ``test_nebular.py``). Audit III's (180, 600, 8) has
been in the suite since S37, so the renderer's builders could have seen it; this file runs the same identities once
on a third mesh — 150 rings, 500 steps, 10 heights and **240 azimuths** (the render's 8 × 8 sub-sampling meets a
different cell-to-grid ratio) — so that a closure that held only where it was tuned would show. Nothing here pins a
physics number a later session would move: the identities are exact (the layers' sums, the light conservation, the
cluster's light, the census across levels) or bounded by a cost the mesh sets (the gate's cell sum against the
stage's trapezoid, the census's own noise). What would have to be true for a row to differ is stated beside it.
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
from galaxy.core.special import expn
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.stages import nebular as nb
from galaxy.stages import spectra
from galaxy.stages import systems as sy
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.photometry import BANDS, PASSBANDS, band_flux_at, band_nu_l_nu, population_at

ROOT = Path(__file__).resolve().parents[1]
AUDIT_MESH = GridSpec(n_R=150, n_t=500, n_z=10, n_phi=240)
FILTERS = json.loads((ROOT / "frontend" / "src" / "galaxy" / "filters.json").read_text(encoding="utf-8"))
RGB = FILTERS["sets"]["rgb"]["curves"]
SHO = FILTERS["sets"]["sho"]["curves"]
IR = FILTERS["measured"]["ir"]["curves"]
V_ROW = {"name": "V (grain table)", "shape": "gaussian", "centre": 5470.0, "fwhm": 852.44}
HALPHA_BOX = json.dumps([{"name": "Halpha", "shape": "box", "centre": 6562.8, "width": 30}])
PARENT = 300


@pytest.fixture(scope="module")
def svc():
    return Service(grid=AUDIT_MESH)


def _get(svc: Service, path: str, query):
    r = svc.handle(path, query)
    assert r.status == 200, (path, r.body[:300])
    return wire.decode(r.body)


def _render(svc: Service, model: str, curve_list, **extra: str):
    return _get(svc, "/api/render", {"model": [model], "filters": [json.dumps(curve_list)], **{k: [v] for k, v in extra.items()}})


def _scalars(svc: Service, model: str, *names: str) -> dict:
    header, arrays = _get(svc, "/api/arrays", {"model": [model], "fields": [",".join(names)]})
    return {**header["scalars"], **arrays}


def _cell_areas(header: dict) -> np.ndarray:
    r_axis, phi_axis = header["window"]["R"], header["window"]["phi"]
    R = r_axis["lo"] + (np.arange(r_axis["n"]) + 0.5) * r_axis["width"]
    return (R * r_axis["width"] * phi_axis["width"] * PC_PER_KPC**2)[:, None] * np.ones(phi_axis["n"])


def _magnitude(response: float, band: str) -> float:
    curve = spectra.band_curve(band)
    lam = curve.grid()
    mean = response / np.trapezoid(curve.at(lam), lam)
    zero = float(band_nu_l_nu(np.array(1.0), band)) / PASSBANDS[band].reference
    return float(-2.5 * np.log10(mean / zero))


def _table_bands(*bands: str):
    return [spectra.band_curve(b).json() for b in bands]


def test_the_mesh_is_one_the_build_did_not_use(svc):
    g = svc.grid
    assert (g.R.size, g.t.size, g.axes["z"].n, g.axes["phi"].n) == (150, 500, 10, 240)
    d = GridSpec()
    assert (g.R.size, g.t.size) not in {(120, 400), (180, 600), (48, 64), (d.n_R, d.n_t)}


# --- V1 (D188): the frame through the table's own bands is the light stage's scalars at this mesh ------------


def test_the_v1_gate_holds_at_the_audit_mesh(svc, model):
    """The tolerance's mesh-dependent cost is the cell sum (R dR dφ at cell centres) against the stage's trapezoid
    in R: 1.5e-4 mag at 400 rings (S38). It scales with the ring width squared, so at 150 rings it may reach the
    order of the gate's 1e-3; the number is printed and the gate asserted, and what would make it differ is a
    spectrum whose band consistency depended on the ring count — it does not, the passes act per cell."""
    header, arrays = _render(svc, model.name, _table_bands(*BANDS))
    total = (arrays["stars"] * _cell_areas(header)[..., None]).sum(axis=(0, 1)) + np.asarray(header["bulge"])
    table = _scalars(svc, model.name, "colour_b_v", "absolute_magnitude_v", *(f"absolute_magnitude_{b.lower()}" for b in BANDS))
    mags = {b: _magnitude(total[k], b) for k, b in enumerate(BANDS)}
    d_bv = (mags["B"] - mags["V"]) - table["colour_b_v"]
    d_v = mags["V"] - table["absolute_magnitude_v"]
    worst = max(abs(mags[b] - table[f"absolute_magnitude_{b.lower()}"]) for b in BANDS)
    print(model.name, "audit mesh: B-V", mags["B"] - mags["V"], "M_V", mags["V"], "table", table["colour_b_v"], table["absolute_magnitude_v"],
          "dB-V", d_bv, "dM_V", d_v, "worst band", worst)
    assert abs(d_bv) < 1e-3 and abs(d_v) < 1e-3 and worst < 1e-3


# --- V2 (D189): the frame's dust removes what it emits; the light is conserved; the layers sum -----------------

def _layered_removed_share(tau: np.ndarray, ratio: np.ndarray) -> np.ndarray:
    """(R, filter): the share the dust takes out of each ring's starlight with the stars and the dust in their own sech²
    layers (S52, D211), ``ratio`` the dust's height over the stars' per ring: each star's light through the dust above and
    below it at every inclination, ½[E₂(τA) + E₂(τ(1 − A))], over the stars' height x = z / 2h★ by the trapezoid on a
    step of min(0.25, ratio / 6) to x = 18; A = ½[1 − tanh(x / ratio)]. Zero where the dust has no layer (NaN)."""
    tau = np.asarray(tau, dtype=float)
    out = np.zeros_like(tau)
    for i, r in enumerate(np.asarray(ratio, dtype=float)):
        if not np.isnan(r):
            step = min(0.25, r / 6.0)
            x = np.arange(0.0, 18.0, step)
            weight = np.full_like(x, step) * 0.5 / np.cosh(x) ** 2
            weight[0] *= 0.5
            above = 0.5 * (1.0 - np.tanh(x / r))
            t = np.maximum(tau[i], 0.0)[:, None]
            out[i] = 1.0 - ((expn(2, t * above) + expn(2, t * (1.0 - above))) * weight).sum(axis=-1)
    return out


def test_the_v2_balance_holds_at_the_audit_mesh(svc, model):
    """Absorbed = emitted in the frame. The two sides are read from the arrays as test_render reads them; against the
    published totals each side carries the frame's cells against the stage's trapezoid (3.4e-4 at 400 rings), which
    grows with the ring width; the frame-against-frame ratio carries only the TIR box's coverage. Would differ if
    the thermal shape were not the dust stage's own at this mesh's temperatures — it is the same function. Since S52
    (D211) the shares are the stars' and the dust's layers' (the header's two heights), not a mixed slab's."""
    header, arrays = _render(svc, model.name, [*RGB, V_ROW])
    f = _scalars(svc, model.name, "disc_surface_brightness", "dust_absorbed_luminosity", "dust_infrared_luminosity",
                 "dust_absorbed_surface_brightness", "dust_infrared_surface_brightness")
    area = _cell_areas(header).sum(axis=1)
    albedo = np.asarray(header["components"]["dust_extinction"]["albedo"])
    ratio = np.asarray(arrays["dust_height"], dtype=float) / float(header["layers"]["stars"])
    share = _layered_removed_share((1.0 - albedo) * -np.log(arrays["dust_extinction"]), ratio)
    absorbed = share[:, 3] * f["disc_surface_brightness"]
    lit = f["dust_absorbed_surface_brightness"] > 1e-9 * f["dust_absorbed_surface_brightness"].max()
    assert absorbed[lit] == pytest.approx(f["dust_absorbed_surface_brightness"][lit], rel=1e-8)
    frame_absorbed = float((absorbed * area).sum())
    _, ir = _render(svc, model.name, IR)
    per_ir = (ir["dust_thermal"] * area[:, None]).sum(axis=0)
    frame_emitted = float(per_ir.sum())
    a, e = frame_absorbed / f["dust_absorbed_luminosity"], frame_emitted / f["dust_infrared_luminosity"]
    hot = f["dust_infrared_surface_brightness"] > 0
    outside = 1.0 - float((ir["dust_thermal"][hot, 0] * area[hot]).sum() / (f["dust_infrared_surface_brightness"][hot] * area[hot]).sum())
    print(model.name, "audit mesh: absorbed", a, "emitted", e, "emitted/absorbed", frame_emitted / frame_absorbed, "outside TIR", outside)
    assert per_ir[1:].sum() < 1e-12 * per_ir[0]
    assert abs(frame_emitted / frame_absorbed - 1.0) < 1e-3
    assert abs(a - 1.0) < 3e-3 and abs(e - 1.0) < 3e-3  # the cell-sum cost at 150 rings, stated (3.4e-4 at 400)
    # The light's three fates add to the light, in every filter, at every ring (exact).
    light = arrays["stars"].mean(axis=1)
    tau = -np.log(arrays["dust_extinction"])
    escaped = light * (1.0 - _layered_removed_share(tau, ratio))
    scattered = arrays["dust_scattered"].mean(axis=1)
    absorbed_f = light * _layered_removed_share((1.0 - albedo) * tau, ratio)
    assert escaped + scattered + absorbed_f == pytest.approx(light, rel=1e-9)


def test_the_line_layers_and_the_s42_lines_sum_to_their_fields_at_the_audit_mesh(svc, model):
    """Exact identities: HII + DIG = the published nebular Hα per ring; the S42 line component through SHO is the
    [S II] pair in red and [O III] in blue, placed by the gas's own contrast (S51, D210); Hβ in both layers is Hα over the decrement at
    the gas's temperature; and each ring's [N II] over Hα is the census's own Hα-weighted ratio there (nebular.ring_ratios)."""
    header, arrays = _render(svc, model.name, SHO)
    names = ("hbeta", "oiii_5007", "nii_6583", "sii_6716", "sii_6731")
    f = _scalars(svc, model.name, "halpha_surface_brightness_nebular", "halpha_surface_brightness_hii", "halpha_surface_brightness_dig",
                 "gas_density_contrast", "hbeta_surface_brightness_dig", *(f"{n}_surface_brightness_hii" for n in names))
    ring = arrays["halpha_hii"][..., 1].mean(axis=1) + arrays["halpha_dig"][:, 1]
    assert ring == pytest.approx(f["halpha_surface_brightness_nebular"], rel=1e-12, abs=0.0)
    placed = np.maximum(f["gas_density_contrast"], 0.0)
    sii = (f["sii_6716_surface_brightness_hii"] + f["sii_6731_surface_brightness_hii"])[:, None] * placed
    assert np.allclose(arrays["lines_hii"][..., 0], sii, rtol=1e-12, atol=0.0)
    assert np.allclose(arrays["lines_hii"][..., 2], f["oiii_5007_surface_brightness_hii"][:, None] * placed, rtol=1e-12, atol=0.0)
    assert not arrays["lines_hii"][..., 1].any() and header["absent"]["lines"] == []
    # The census's ratio per ring is the field's (the same function, the same regions).
    _, c = _get(svc, "/api/clusters", {"model": [model.name], "r_min": ["0"], "r_max": [str(svc.grid.spec.R_max)], "phi_min": ["0"], "phi_max": [str(2 * math.pi)]})
    R = svc.grid.R
    w = np.asarray(c["hii_halpha_luminosity"], dtype=float)
    expected = nb.ring_ratios(np.asarray(c["cluster_radius"], dtype=float), w, np.asarray(c["hii_nii_6583_ratio"], dtype=float), R)
    ha = f["halpha_surface_brightness_hii"]
    lit = ha > 0
    assert f["nii_6583_surface_brightness_hii"][lit] / ha[lit] == pytest.approx(expected[lit], rel=1e-9)


# --- V3 (D190): catalogue against field at this mesh's census, and the census identical across levels ----------


def _clusters_against_field(svc: Service, window: str, level: int):
    _, a = _get(svc, "/api/render", f"{window}&level={level}&filters={HALPHA_BOX}")
    R = svc.grid.R
    bounds = [sy.cell_bounds(R, int(c), level) for c in a["cell"]]
    area_pc2 = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * 1e6
    field = float((np.asarray(a["halpha_hii"], dtype=float)[:, 0] * area_pc2).sum())
    _, c = _get(svc, "/api/clusters", f"{window}&level={level}")
    lum = np.asarray(c["hii_halpha_luminosity"], dtype=float)
    return float(lum.sum()) / field, lum


def test_the_clusters_halpha_integrates_back_to_the_field_at_the_audit_mesh(svc):
    """Judged against the census's own second moment at this mesh, √⟨L²⟩/⟨L⟩ / √N (D190's statistic), never one
    window's realised noise. Would differ if the regions' Hα were not the clusters' Q through the same Case B — it is."""
    disc, lum = _clusters_against_field(svc, "r_min=0.5&r_max=20&phi_min=0&phi_max=6.283185307179586", 0)
    c_pop = math.sqrt(float((lum**2).mean())) / float(lum.mean())
    z_disc = (disc - 1.0) / (c_pop / math.sqrt(lum.size))
    sector, lum1 = _clusters_against_field(svc, "r_min=4&r_max=12&phi_min=0&phi_max=2", 1)
    z_sector = (sector - 1.0) / (c_pop / math.sqrt(lum1.size))
    print("audit mesh: disc", disc, lum.size, "c_pop", c_pop, "z", z_disc, "| sector", sector, lum1.size, "z", z_sector)
    assert lum.size > 5000 and lum1.size > 500
    assert abs(z_disc) < 3.0 and abs(z_sector) < 3.0
    assert disc == pytest.approx(1.0, abs=3.0 * c_pop / math.sqrt(lum.size) + 0.02)


@pytest.mark.parametrize("path, key", [("/api/clouds", ("cloud_radius", "cloud_azimuth")), ("/api/clusters", ("cluster_radius", "cluster_azimuth"))])
def test_a_census_is_the_same_at_every_level_at_the_audit_mesh(svc, path, key):
    b = sy.cell_bounds(svc.grid.R, PARENT, 0)
    eps = 1e-6
    window = f"r_min={b['r_lo'] + eps}&r_max={b['r_hi'] - eps}&phi_min={b['phi_lo'] + eps}&phi_max={b['phi_hi'] - eps}"
    rows_at = []
    for level in range(4):
        _, a = _get(svc, path, f"{window}&level={level}")
        names = sorted(n for n in a if np.asarray(a[n]).ndim == 1)
        rows_at.append({(float(a[key[0]][i]), float(a[key[1]][i])): tuple(float(a[n][i]) for n in names) for i in range(len(a[key[0]]))})
    assert len(rows_at[0]) > 10
    for level in (1, 2, 3):
        assert rows_at[level] == rows_at[0], (path, level)


def test_the_render_redistributes_across_levels(svc):
    """A property the build did not name as a gate: a window's light summed over its level-k cells is the same
    light summed over the level-0 cells that hold them, for every component. Each cell's mean is an 8 × 8 midpoint
    rule on the bilinear grid (RENDER_CELL_SAMPLES), so the children together are a finer midpoint rule on the same
    integrand and the two differ by the rule's own error, bounded here at 2e-3 of the window's light and printed."""
    # A window that is exactly level-0 cells (rings 6-9, sectors 0-5), so every level covers the same area.
    lo, hi = sy.cell_bounds(svc.grid.R, 6 * sy.CELL_SECTORS, 0), sy.cell_bounds(svc.grid.R, 9 * sy.CELL_SECTORS + 5, 0)
    eps = 1e-6
    window = f"r_min={lo['r_lo'] + eps}&r_max={hi['r_hi'] - eps}&phi_min={lo['phi_lo'] + eps}&phi_max={hi['phi_hi'] - eps}"
    totals = {}
    for level in (0, 1, 2):
        _, a = _get(svc, "/api/render", f"{window}&level={level}&filters={json.dumps(RGB)}")
        bounds = [sy.cell_bounds(svc.grid.R, int(c), level) for c in a["cell"]]
        area = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * 1e6
        totals[level] = {n: (np.asarray(a[n], dtype=float) * area[:, None]).sum(axis=0) for n in ("stars", "halpha_hii", "lines_hii", "halpha_dig")}
    for name in totals[0]:  # the optical set sees no dust_thermal, so it is not compared here
        lit = totals[0][name] > 0
        for level in (1, 2):
            rel = float(np.abs(totals[level][name][lit] / totals[0][name][lit] - 1.0).max())
            print("audit mesh: level", level, name, "against level 0", rel)
            assert rel < 2e-3, (name, level, rel)  # 4.6e-4 at worst (lines_hii, level 2) at S43


# --- V4 (D191) and P6 (D192): the cluster's light identity, and the bolometric painting measured again ---------


def test_a_clusters_light_is_its_mass_times_the_tables_and_the_ramp_is_bolometric_at_the_audit_mesh(svc):
    """The identity is exact at any mesh. The painting's excess (2.12 in G at the coarse grid, D191) is a property of
    the census's age and metallicity mix, which the mesh moves a little: measured here and bounded, not pinned."""
    F = svc.compute(svc.models.get(DEFAULT_MODEL), {}, ["cluster_luminosity", "cluster_light_temperature", "cluster_mass", "cluster_age",
                                                  "cluster_metallicity", "disc_luminosity"])[0].fields
    mass = np.asarray(F["cluster_mass"], dtype=float)
    age = np.asarray(F["cluster_age"], dtype=float) / 1000.0
    feh = np.asarray(F["cluster_metallicity"], dtype=float)
    light, _ = population_at(age, feh)
    L = np.asarray(F["cluster_luminosity"], dtype=float)
    assert np.allclose(L, mass * light, rtol=1e-12)
    T = np.asarray(F["cluster_light_temperature"], dtype=float)
    rgb = spectra.parse_curves(RGB)
    flux = band_flux_at(age, feh, spectra.SED_BANDS)
    sed = np.stack([band_nu_l_nu(flux[b], b) for b in spectra.SED_BANDS], axis=-1) * mass[:, None]
    population = spectra.stellar_response(sed, T, rgb)
    ramp = L[:, None] * spectra.blackbody_response(rgb, T)
    summed = ramp.sum(axis=0) / population.sum(axis=0)
    share = L.sum() / float(F["disc_luminosity"])
    print("audit mesh: ramp over population R G B", summed, "clusters' share of the disc light", share, "N", L.size)
    assert 1.6 < summed[0] < 2.2 and 1.8 < summed[1] < 2.5 and 2.0 < summed[2] < 2.9  # 1.89 / 2.12 / 2.43 at (120, 400, 6)
    assert 0.18 < share < 0.30  # 0.236 coarse, 0.249 default
