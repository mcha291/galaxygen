"""S45 (D196): row 37's diagnosis by the miss's own prediction — the parts of the [N II]/Hα gradient over 8.2–15.4 kpc,
measured so that the readings D196 states can be applied. Every number here is pinned so the diagnosis re-runs.

On the default run (``basic`` at S45; ``azimuthal`` since S46, D197, whose regions are basic's bit for bit), the regions whose ``cluster_radius`` lies in [8.2, 15.4] kpc, Hα-weighted
(``hii_halpha_luminosity``) throughout: (a) Z′, the regions' oxygen gradient, beside the gas rings' α gradient;
(b) the grid's local responses G_Z, G_age, G_U of log([N II]/Hα) at each region's own point, and age′, U′;
(c) the three first-order products against the published gradient; (d) the substitution probes (D114) through the
stage's own ring sum and the row's own fit; (e) G_Z against PP04's 1/0.57 per dex; (f) row 22 beside Z′.

Re-run: ``uv run pytest -q tests/test_s45_diagnosis.py -s -p no:cacheprovider``.

**Since S55 (D214, gate G1 change 9) the diagnosis reads the layer-off run**, the census the acceptance table judges
row 37 on (invariant I3): the HII regions placed by no pattern, another draw at the same expected counts. Six pins
moved with that redraw and say so (the published gradient, the regions below the age floor, age′, U′, the sum's
distance from the published gradient, the regions near the inner edge) and one was re-pinned at the edge of its
tolerance (G_U's 84th percentile). **The diagnosis's conclusion did not move**: the metallicity path's product
G_Z · Z′ is −0.0957 layer-off (−0.0956 on the layer-on census), the age and U paths are a hundredth of it, and the
substitution probes read the same - Z alone carries the gradient.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import nebular as nb

LINE = "nii_6583"
H = 0.05  # dex: the half-step of every central difference (D196 (b))
NEAR = 0.5  # kpc: the probes freeze at the regions within this of the fit's inner edge (D196 (d))
PP04 = 1.0 / 0.57  # per dex of 12 + log(O/H): N2 = (12 + log O/H − 8.90) / 0.57 (Zhao et al. 2026 Eq. 5)


@pytest.fixture(scope="module")
def models():
    ms, _, _ = production()
    return {n: ms.get(n) for n in ms.names()}


@pytest.fixture(scope="module")
def default(models):
    # S55 (D214, gate G1 change 9): the diagnosis reads the census the row is judged on - the layer-off run
    # (invariant I3). Until S55 it read the layer-on census; the pins that moved with the redraw say so below.
    return run(models[DEFAULT_MODEL], layer=False)


def _wmean(x: np.ndarray, w: np.ndarray) -> float:
    return float(np.sum(w * x) / np.sum(w))


def _wpercentiles(x: np.ndarray, w: np.ndarray, qs=(16.0, 50.0, 84.0)) -> tuple[float, ...]:
    """Weighted percentiles: the sorted values against their cumulative weight at each value's midpoint."""
    order = np.argsort(x)
    xs, ws = x[order], w[order]
    cum = (np.cumsum(ws) - 0.5 * ws) / ws.sum()
    return tuple(float(np.interp(q / 100.0, cum, xs)) for q in qs)


def _wslope(R: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    return float(np.polyfit(R, y, 1, w=np.sqrt(w))[0])


def _response(f, x: np.ndarray, axis: np.ndarray, h: float) -> tuple[np.ndarray, int, int]:
    """d log10 r / dx at each point, central by ±h on the point clamped to the axis span; one-sided where x ± h
    would leave the span. Returns (response, how many took the one-sided difference, how many lay outside)."""
    lo, hi = float(axis[0]), float(axis[-1])
    x0 = np.clip(x, lo, hi)
    up = np.where(x0 + h > hi, x0, x0 + h)
    dn = np.where(x0 - h < lo, x0, x0 - h)
    g = (np.log10(f(up)) - np.log10(f(dn))) / (up - dn)
    return g, int(np.count_nonzero((up == x0) | (dn == x0))), int(np.count_nonzero((x < lo) | (x > hi)))


def _diagnose(models, default) -> dict:
    F = default.fields
    R = np.asarray(default.grid.R, dtype=float)
    solar = float(models[DEFAULT_MODEL].constants["NEBULAR_GRID_OXYGEN_SOLAR"].value)
    radius_all = np.asarray(F["cluster_radius"], dtype=float)
    w_all = np.asarray(F["hii_halpha_luminosity"], dtype=float)
    oxygen_all = np.asarray(F["hii_oxygen_abundance"], dtype=float)
    lz_all = oxygen_all - solar
    la_all = np.log10(np.asarray(F["cluster_age"], dtype=float) * 1.0e6)
    lu_all = np.asarray(F["hii_ionization_parameter"], dtype=float)
    ratio_all = np.asarray(F[f"hii_{LINE}_ratio"], dtype=float)
    halpha_ring = np.asarray(F["halpha_surface_brightness_hii"], dtype=float)
    g = nb._line_grid()
    d: dict = {"n_regions": int(radius_all.size)}

    # (d)'s instrument: the stage's own ring sum (ring_ratios over every region) times the HII Hα ring, by the row's fit.
    def ring_gradient(ratio: np.ndarray) -> float:
        nii_ring = halpha_ring * nb.ring_ratios(radius_all, w_all, ratio, R)
        return nb.nii_halpha_gradient(R, halpha_ring, nii_ring)

    published = float(F["nii_halpha_gradient_hii"])
    d["published"] = published
    d["identity"] = ring_gradient(ratio_all) - published
    d["identity_ring"] = float(np.max(np.abs(halpha_ring * nb.ring_ratios(radius_all, w_all, ratio_all, R)
                                             - np.asarray(F[f"{LINE}_surface_brightness_hii"], dtype=float))))

    # The fit range's regions, finite and lit.
    sel = ((radius_all >= nb.NII_GRADIENT_R_INNER) & (radius_all <= nb.NII_GRADIENT_R_OUTER) & (w_all > 0)
           & np.isfinite(ratio_all) & np.isfinite(lz_all) & np.isfinite(la_all) & np.isfinite(lu_all))
    r, w, lz, la, lu = radius_all[sel], w_all[sel], lz_all[sel], la_all[sel], lu_all[sel]
    d["n_fit"] = int(sel.sum())

    # (a) Z′: the regions' weighted oxygen slope; the gas rings' (feh_gas + alpha_fe_gas) slope, unweighted.
    d["Zp"] = _wslope(r, oxygen_all[sel], w)
    rings = (R >= nb.NII_GRADIENT_R_INNER) & (R <= nb.NII_GRADIENT_R_OUTER)
    alpha_ring = np.asarray(F["feh_gas"], dtype=float) + np.asarray(F["alpha_fe_gas"], dtype=float)
    d["Zp_ring"] = float(np.polyfit(R[rings], alpha_ring[rings], 1)[0])
    d["n_rings"] = int(rings.sum())

    # (b) the grid's local responses at each region's own point, and the age and U trends.
    def nii(lz_, la_, lu_):
        return nb.grid_line_ratios(lz_, la_, lu_)[LINE]

    G_Z, d["oneside_Z"], d["outside_Z"] = _response(lambda x: nii(x, la, lu), lz, g["log_z"], H)
    G_age, d["oneside_age"], d["outside_age"] = _response(lambda x: nii(lz, x, lu), la, g["log_age_yr"], H)
    G_U, d["oneside_U"], d["outside_U"] = _response(lambda x: nii(lz, la, x), lu, g["log_u"], H)
    for name, G in (("G_Z", G_Z), ("G_age", G_age), ("G_U", G_U)):
        d[name] = _wmean(G, w)
        d[name + "_pct"] = _wpercentiles(G, w)
    # What the model's own (clamped) evaluation responds: zero for a region outside the axis span.
    d["G_Z_clamped"] = _wmean(np.where((lz < g["log_z"][0]) | (lz > g["log_z"][-1]), 0.0, G_Z), w)
    d["G_age_clamped"] = _wmean(np.where(la < g["log_age_yr"][0], 0.0, G_age), w)
    d["agep"] = _wslope(r, la, w)
    d["Up"] = _wslope(r, lu, w)

    # (c) the first-order products.
    d["P_Z"] = d["G_Z"] * d["Zp"]
    d["P_age"] = d["G_age"] * d["agep"]
    d["P_U"] = d["G_U"] * d["Up"]
    d["P_sum"] = d["P_Z"] + d["P_age"] + d["P_U"]
    d["P_sum_minus_published"] = d["P_sum"] - published

    # (d) the substitution probes: freeze beyond 8.2 kpc at the weighted means of the regions within 8.2 ± 0.5.
    ok_all = np.isfinite(ratio_all) & (w_all > 0) & np.isfinite(lz_all) & np.isfinite(la_all) & np.isfinite(lu_all)
    near = ok_all & (np.abs(radius_all - nb.NII_GRADIENT_R_INNER) <= NEAR)
    d["n_near"] = int(near.sum())
    d["lz0"] = _wmean(lz_all[near], w_all[near])
    d["la0"] = _wmean(la_all[near], w_all[near])
    d["lu0"] = _wmean(lu_all[near], w_all[near])
    beyond = radius_all > nb.NII_GRADIENT_R_INNER
    lz_f = np.where(beyond, d["lz0"], lz_all)
    la_f = np.where(beyond, d["la0"], la_all)
    lu_f = np.where(beyond, d["lu0"], lu_all)
    # The stage's NaN-safety kept: a region whose ratio the stage left NaN stays NaN (ring_ratios drops it).
    keep_nan = np.where(np.isfinite(ratio_all), 1.0, np.nan)
    d["probe_ageU"] = ring_gradient(nii(lz_f, la_all, lu_all) * keep_nan)  # (i) Z frozen: the age/U share
    d["probe_Z"] = ring_gradient(nii(lz_all, la_f, lu_f) * keep_nan)  # (ii) age, U frozen: the Z share
    d["probe_none"] = ring_gradient(nii(lz_f, la_f, lu_f) * keep_nan)  # (iii) all frozen: the ring mixing alone
    d["probe_reeval"] = ring_gradient(nii(lz_all, la_all, lu_all) * keep_nan)  # nothing frozen, re-evaluated

    # (e) PP04; (f) row 22.
    d["G_Z_over_PP04"] = d["G_Z"] / PP04
    d["G_Z_median_over_PP04"] = d["G_Z_pct"][1] / PP04
    d["row22"] = float(F["metallicity_gradient"])
    return d


def _summary(d: dict) -> str:
    p = lambda t: "/".join(f"{v:+.4f}" for v in t)  # noqa: E731
    return "\n".join([
        "",
        f"S45 diagnosis (D196) - {d['n_regions']} regions, {d['n_fit']} in 8.2-15.4 kpc, {d['n_rings']} rings",
        f"(a) Z' regions (Ha-weighted)    {d['Zp']:+.5f} dex/kpc",
        f"    feh_gas+alpha_fe_gas rings   {d['Zp_ring']:+.5f} dex/kpc",
        f"(b) G_Z   mean {d['G_Z']:+.4f}  16/50/84 {p(d['G_Z_pct'])}  one-sided {d['oneside_Z']} (outside span {d['outside_Z']});"
        f" clamped-as-zero mean {d['G_Z_clamped']:+.4f}",
        f"    G_age mean {d['G_age']:+.4f}  16/50/84 {p(d['G_age_pct'])}  one-sided {d['oneside_age']} (outside span {d['outside_age']});"
        f" clamped-as-zero mean {d['G_age_clamped']:+.4f}",
        f"    G_U   mean {d['G_U']:+.4f}  16/50/84 {p(d['G_U_pct'])}  one-sided {d['oneside_U']} (outside span {d['outside_U']})",
        f"    age' {d['agep']:+.5f} dex/kpc   U' {d['Up']:+.5f} dex/kpc",
        f"(c) G_Z*Z' {d['P_Z']:+.5f}  G_age*age' {d['P_age']:+.5f}  G_U*U' {d['P_U']:+.5f}  sum {d['P_sum']:+.5f}"
        f"  vs published {d['published']:+.5f}  (sum - published {d['P_sum_minus_published']:+.5f})",
        f"(d) identity: ring_gradient(published ratios) - published {d['identity']:+.2e}; ring vector max |diff| {d['identity_ring']:.2e}",
        f"    frozen at the {d['n_near']} regions within 8.2 +- 0.5 kpc: lz0 {d['lz0']:+.4f}  la0 {d['la0']:.4f}  lu0 {d['lu0']:+.4f}",
        f"    (i) Z frozen (age/U share)    {d['probe_ageU']:+.5f} dex/kpc",
        f"    (ii) age,U frozen (Z share)   {d['probe_Z']:+.5f} dex/kpc",
        f"    (iii) all frozen (mixing)     {d['probe_none']:+.5f} dex/kpc",
        f"    re-evaluated, none frozen     {d['probe_reeval']:+.5f} dex/kpc",
        f"(e) PP04 {PP04:.4f}/dex: G_Z mean/PP04 {d['G_Z_over_PP04']:.4f}, median/PP04 {d['G_Z_median_over_PP04']:.4f}",
        f"(f) row 22 metallicity_gradient {d['row22']:+.5f} dex/kpc beside Z' {d['Zp']:+.5f}",
    ])


def test_row_37s_parts(models, default):
    """D196 (a)–(f), printed in one block and pinned."""
    d = _diagnose(models, default)
    print(_summary(d))
    T = "S45 diagnosis (D196)"
    assert d["identity"] == pytest.approx(0.0, abs=1e-9), T  # the stage's ring sum reproduced exactly
    assert d["identity_ring"] == pytest.approx(0.0, abs=1e-9), T
    assert d["probe_reeval"] == pytest.approx(d["published"], abs=1e-9), T
    # S45 diagnosis (D196); S51 (D210): was -0.1035, the census redrawn
    assert d["published"] == pytest.approx(-0.1030, abs=0.002)  # S55 (D214): was -0.1055, read layer-off
    assert d["n_regions"] == pytest.approx(12860, abs=130)  # S45 diagnosis (D196)
    assert d["n_fit"] == pytest.approx(5337, abs=55)  # S45 diagnosis (D196)
    assert d["n_rings"] == 96  # S45 diagnosis (D196)
    # (a)
    assert d["Zp"] == pytest.approx(-0.0784, abs=0.002)  # S45 diagnosis (D196)
    assert d["Zp_ring"] == pytest.approx(-0.0780, abs=0.002)  # S45 diagnosis (D196)
    # (b)
    assert d["G_Z"] == pytest.approx(1.224, abs=0.02)  # S45 diagnosis (D196)
    assert d["G_Z_pct"] == pytest.approx((0.958, 1.279, 1.522), abs=0.02)  # S45 diagnosis (D196)
    assert d["G_Z_clamped"] == pytest.approx(1.224, abs=0.02)  # S45 diagnosis (D196)
    assert (d["oneside_Z"], d["outside_Z"]) == (0, 0)  # S45 diagnosis (D196): no fit-range region near a Z edge
    assert d["G_age"] == pytest.approx(0.213, abs=0.02)  # S45 diagnosis (D196)
    assert d["G_age_pct"] == pytest.approx((0.004, 0.074, 0.745), abs=0.02)  # S45 diagnosis (D196)
    assert d["G_age_clamped"] == pytest.approx(0.213, abs=0.02)  # S45 diagnosis (D196)
    assert d["oneside_age"] == pytest.approx(770, abs=8)  # S45 diagnosis (D196); S51 (D210): was 759, the census redrawn on the gas's ridge
    # S45 diagnosis (D196): below the 0.5 Myr floor; S51 (D210): was 126, the census redrawn on the gas's ridge
    assert d["outside_age"] == pytest.approx(136, abs=3)  # S55 (D214): was 119, read layer-off
    assert d["G_U"] == pytest.approx(-0.378, abs=0.02)  # S45 diagnosis (D196)
    # S45 diagnosis (D196). The 84th percentile: S55 (D214): was -0.177, read layer-off (0.019 of its 0.02 tolerance)
    assert d["G_U_pct"] == pytest.approx((-0.483, -0.450, -0.196), abs=0.02)
    assert (d["oneside_U"], d["outside_U"]) == (0, 0)  # S45 diagnosis (D196)
    # S45 diagnosis (D196); S51 (D210): was -0.0081, the census redrawn on the gas's ridge
    assert d["agep"] == pytest.approx(-0.0059, abs=0.002)  # S55 (D214): was 0.0005, read layer-off
    # S45 diagnosis (D196); S51 (D210): was 0.0005, the census redrawn on the gas's ridge
    assert d["Up"] == pytest.approx(-0.0005, abs=0.002)  # S55 (D214): was 0.0034, read layer-off
    # (c)
    assert d["P_Z"] == pytest.approx(-0.0960, abs=0.002)  # S45 diagnosis (D196)
    assert d["P_age"] == pytest.approx(0.0001, abs=0.002)  # S45 diagnosis (D196); S51 (D210): was -0.0017, the census redrawn on the gas's ridge
    assert d["P_U"] == pytest.approx(-0.0013, abs=0.002)  # S45 diagnosis (D196); S51 (D210): was -0.0002, the census redrawn on the gas's ridge
    assert d["P_sum"] == pytest.approx(-0.0979, abs=0.002)  # S45 diagnosis (D196)
    # S45 diagnosis (D196); S51 (D210): was 0.0056, the census redrawn on the gas's ridge
    assert d["P_sum_minus_published"] == pytest.approx(0.0062, abs=0.002)  # S55 (D214): was 0.0088, read layer-off
    # (d)
    # S45 diagnosis (D196)
    assert d["n_near"] == pytest.approx(777, abs=8)  # S55 (D214): was 786 (783 on the layer-on census at S54), read layer-off
    assert d["lz0"] == pytest.approx(-0.175, abs=0.002)  # S45 diagnosis (D196); S51 (D210): was -0.170, the census redrawn on the gas's ridge
    assert d["la0"] == pytest.approx(6.365, abs=0.01)  # S45 diagnosis (D196); S51 (D210): was 6.288, the census redrawn on the gas's ridge
    assert d["lu0"] == pytest.approx(-2.145, abs=0.02)  # S45 diagnosis (D196); S51 (D210): was -2.014, the census redrawn on the gas's ridge
    assert d["probe_ageU"] == pytest.approx(-0.0028, abs=0.002)  # S45 diagnosis (D196): (i) Z frozen; S51 (D210): was -0.0016, the census redrawn on the gas's ridge
    assert d["probe_Z"] == pytest.approx(-0.1158, abs=0.002)  # S45 diagnosis (D196): (ii) age, U frozen; S51 (D210): was -0.1177, the census redrawn on the gas's ridge
    assert d["probe_none"] == pytest.approx(-0.0005, abs=0.002)  # S45 diagnosis (D196): (iii) all frozen
    # (e)
    assert PP04 == pytest.approx(1.754, abs=1e-3)  # S45 diagnosis (D196)
    assert d["G_Z_over_PP04"] == pytest.approx(0.697, abs=0.01)  # S45 diagnosis (D196)
    assert d["G_Z_median_over_PP04"] == pytest.approx(0.729, abs=0.01)  # S45 diagnosis (D196)
    # (f)
    assert d["row22"] == pytest.approx(-0.0698, abs=0.002)  # S45 diagnosis (D196)
