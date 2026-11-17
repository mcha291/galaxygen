"""S104 (batch R, lane RC; D272 item 7, D273 items 5-6; docs/READING_ROW_105.md): the disclosed checks the reading row
sourced - the unchanged model measured against published numbers and recorded AS MEASURED, the source's number beside
it. DISCLOSED, not judged: each source was read after the model's number was known or near it (D273), so no window here
is a bound and a miss is named, never mended here (B5, D1). Every record is the default galaxy (the registry's
defaults, which ``milky_way``'s template restates) on the production grid, one run shared by the module."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import production
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages import photometry as ph
from galaxy.stages import remnants as rm

M_K_SUN = 3.27  # Just et al. 2015 (arXiv:1504.05808) sect. 3.2, READ at S103 (citing Casagrande et al. 2012)


@pytest.fixture(scope="module")
def default():
    ms, _, _ = production()
    model = ms.get(DEFAULT_MODEL)
    return run(model), {k: v.value for k, v in model.constants.items()}


def _solar_column(res, C) -> dict[str, float]:
    """The column through the disc at the grid ring nearest R_SUN: its K light (each formation step's mass formed
    times a Kroupa population's K flux per unit mass formed, averaged over the step's ages - ``light.py``'s own sum),
    its mass as the model counts it (``stellar_surface_density``: the locked mass, formed x (1 - RETURN_FRACTION)),
    the same mass by what it is (``remnants``' population integral: the living stars at their present mass, the white
    dwarfs, neutron stars and black holes), and the K light by PARSEC phase label and by age."""
    F, R, t, spec = res.fields, res.grid.R, res.grid.t, res.grid.spec
    i0 = int(np.argmin(np.abs(R - float(C["R_SUN"]))))
    formed = np.asarray(F["stars_formed_history"], float)[i0] / (1.0 - float(C["RETURN_FRACTION"]))
    dt = float(spec.t_max) / float(spec.n_t)
    youngest = float(spec.t_max) - (t + 0.5 * dt)
    feh = np.asarray(F["feh_history"], float)[i0 : i0 + 1]
    sun = 10.0 ** (0.4 * M_K_SUN)
    k_step = formed * ph.population_over(youngest, youngest + dt, feh)["K"][0] * sun  # L_K,sun / pc2 per step
    per = rm._per_formed(youngest, youngest + dt, feh)[0]
    kind = {q: float((formed * per[:, k]).sum()) for k, q in enumerate(rm.MASS_QUANTITIES) if q != "living_initial"}
    # the K flux per isochrone split by the PARSEC label at each segment's heavier end
    tab, K = ph.isochrones(), ph.BANDS.index("K")
    groups = ((0, 1), (2, 3), (4, 6), (7, 8))  # MS (with the pre-MS), SGB + RGB, core He burning, AGB
    per_iso = np.zeros((tab.log_ages.size, tab.mhs.size, len(groups)))
    for (a, z) in tab.tracks:
        seg = ph.segments(a, z)
        flux = seg.number * ph.log_linear_integral(seg.neg_mag[:, 0, K], seg.neg_mag[:, 1, K], 0.0, 1.0)
        for g, (lo, hi) in enumerate(groups):
            per_iso[a, z, g] = float(flux[(seg.label[:, 1] >= lo) & (seg.label[:, 1] <= hi)].sum())
    by_phase = (formed[:, None] * ph.steps_over(ph.cumulative_over_age(ph.on_fine_ages(per_iso)), youngest, youngest + dt, feh)[0]).sum(axis=0) * sun
    age = youngest + 0.5 * dt
    return {
        "R": float(R[i0]), "mass": float(np.asarray(F["stellar_surface_density"], float)[i0]), "K": float(k_step.sum()),
        **kind, "MS": float(by_phase[0]), "RGB": float(by_phase[1]), "CHeB": float(by_phase[2]), "AGB": float(by_phase[3]),
        "K_young": float(k_step[age < 1.0].sum()), "K_1_6": float(k_step[(age >= 1.0) & (age < 6.0)].sum()),
        "K_old": float(k_step[age >= 6.0].sum()),
    }


def test_135_the_k_band_mass_to_light_ratio_in_the_solar_cylinder_disclosed(default):
    """#135, DISCLOSED as measured at S104 (D273 item 5). The source: Just et al. 2015 (arXiv:1504.05808), READ at
    S103 (sects. 3.3-3.4) and again at S104 (sects. 3.2-3.4, an extracting fetch of ar5iv): M/L_K 0.31 +/- 0.02 in the
    local volume, 0.34 for the solar cylinder - Sigma_K 98.7 L_K,sun/pc2 (giants 82.5, 84 %; dwarfs 16.2, 16 %) and a
    stellar column of 33.3 Msun/pc2 counting white and brown dwarfs (locally: main sequence 0.0315, giants 0.00058,
    brown dwarfs 0.002, white dwarfs 0.0032 Msun/pc3 of 0.0373). Empirical masses, no IMF.

    The model, the column at R_SUN (8.2125 kpc, the nearest ring): Sigma_K 66.89, the locked mass 36.04, M/L_K
    **0.539 - a miss of 1.6x against 0.34** (the entry's "about 0.73", 2.1x, is the whole galaxy's: 0.703 now). The
    cause, by measurement: **too little K light, not too much mass.** The mass as the model counts it is 1.08x Just's;
    by what it is, living stars 24.84 + white dwarfs 4.49 + neutron stars 0.53 + black holes 0.92 = 30.78, under
    Just's 33.3 (the model has no brown dwarfs, Just's ~5 %); the other 5.26 is mass the isochrones return beyond
    the instantaneous RETURN_FRACTION 0.30 and still counted locked. The K light is 0.68x Just's, in every phase:
    the giants (SGB+RGB 23.27, core He burning 10.30, AGB 21.01) 54.6 against 82.5 (0.66x), the main sequence 12.31
    against the dwarfs' 16.2 (0.76x) - PARSEC's labels against Just's split by M_K, so the phases are compared only
    roughly. By age, stars younger than 1 Gyr give 0.26 of the K light, 1-6 Gyr 0.48, older 0.25. On the physical
    mass the ratio is 0.460 (1.35x Just's): the locked-mass bookkeeping carries a quarter of the miss, the light the
    rest. No mend (D273: the cause named before anything is mended)."""
    res, C = default
    col = _solar_column(res, C)
    assert col["R"] == pytest.approx(8.2125)
    assert col["K"] == pytest.approx(66.89, rel=2e-3)
    assert col["mass"] == pytest.approx(36.04, rel=2e-3)
    assert col["mass"] / col["K"] == pytest.approx(0.539, abs=2e-3)  # Just et al. 2015: 0.34 (solar cylinder), 0.31 +/- 0.02 (local)
    assert [col[k] for k in ("living", "white_dwarf", "neutron_star", "black_hole")] == pytest.approx([24.84, 4.489, 0.530, 0.916], rel=3e-3)
    physical = col["living"] + col["white_dwarf"] + col["neutron_star"] + col["black_hole"]
    assert physical == pytest.approx(30.78, rel=2e-3) and physical / col["K"] == pytest.approx(0.460, abs=2e-3)  # Just: 33.3 Msun/pc2
    assert col["MS"] + col["RGB"] + col["CHeB"] + col["AGB"] == pytest.approx(col["K"], rel=1e-9)  # the phase split closes
    assert [col[k] for k in ("MS", "RGB", "CHeB", "AGB")] == pytest.approx([12.31, 23.27, 10.30, 21.01], rel=3e-3)  # Just: dwarfs 16.2, giants 82.5
    assert [col[k] / col["K"] for k in ("K_young", "K_1_6", "K_old")] == pytest.approx([0.262, 0.484, 0.254], abs=3e-3)
    # the whole galaxy, the entry's number: stellar_mass_total over L_K from absolute_magnitude_k
    F = res.fields
    l_k = 10.0 ** (-0.4 * (float(F["absolute_magnitude_k"]) - M_K_SUN))
    assert float(F["stellar_mass_total"]) / l_k == pytest.approx(0.703, abs=2e-3)  # S54's "about 0.73" (M_K -23.77)


def test_162_the_clusters_correlation_at_300_pc_by_age_disclosed(default):
    """#162, DISCLOSED as measured at S104 (D273 item 5). The source: Turner et al. 2022 (arXiv:2209.02872) Table 4,
    READ at S103: 1 + omega at 300 pc of eleven PHANGS-HST galaxies' clusters, medians over the rows 3.43 at <= 10 Myr
    and 2.26 above `[inferred]` (S103's medians, not printed in the paper). The model: the cluster census (0-20 Myr,
    every cluster past its cloud's embedded phase, every mass) through ``specs.clustering`` - Landy & Szalay 1993
    against uniform randoms ten times the data, ``A`` the power law's 1 + omega at 300 pc fitted over 100-2000 pc, and
    the 300 pc bin read directly. How it differs from Turner's: one galaxy seen face-on in 2-D positions (Turner's are
    projected sky positions in angle converted to pc), every cluster (Turner's are detected, so mass- and
    luminosity-limited), a 6 kpc square at R_SUN (the project's PHANGS-like pointing, ``solar_pointing``) where Turner
    uses each galaxy's HST footprint and a fit range per galaxy not printed in pc, and the model's "above 10 Myr" is
    10-20 Myr only (the census ends at 20 Myr). The square (the clustering gate's own convention; its <= 10 Myr numbers
    are the gate's disclosed SQUARE_AFTER row, the anchor): **A 1.375 at <= 10 Myr and 1.197 at 10-20 Myr against
    3.43 and 2.26 - a miss, both under**; the 300 pc bin itself 1.066 and 1.093 (the fall with age inverted there);
    ln A(>10) / ln A(<=10) 0.56 against Turner's 0.66 `[inferred]`. The whole disc (the annulus to the grid's edge)
    reads A 10.33 and 10.78, set by the disc's radial profile against uniform randoms - over, and no fall with age.
    ``ngc_4414`` (s104_RC_cl_n4414.log, not pinned): the square 1.342 / 1.273, the annulus 18.03 / 18.07."""
    from galaxy.specs import clustering as CL

    res, C = default
    F, R = res.fields, res.grid.R
    age = np.asarray(F["cluster_age"], float)
    assert age.size == 13124 and float(age.max()) < 20.0
    xy = CL.positions_pc(np.asarray(F["cluster_radius"], float), np.asarray(F["cluster_azimuth"], float))
    got = {}
    for fname, fp in (("square", CL.solar_pointing(float(C["R_SUN"]))), ("annulus", CL.Annulus(float(R[0]) * 1000.0, float(R[-1]) * 1000.0))):
        for key, sel in (("<=10", age <= 10.0), (">10", age > 10.0)):
            corr = CL.against_uniform(xy[sel], fp, multiple=10.0, seed=61)
            law = CL.fit_power_law(corr, 100.0, 2000.0)
            got[fname, key] = (corr.n_data, law.amplitude, law.alpha, corr.at(300.0))
    # (clusters in the footprint, A at 300 pc from the 100-2000 pc fit, the slope, 1 + omega in the 300 pc bin)
    assert got["square", "<=10"][0] == 281 and got["square", ">10"][0] == 259
    assert got["square", "<=10"][1:] == pytest.approx((1.375, -0.202, 1.066), abs=3e-3)  # Turner median 3.43; test_clustering_gate SQUARE_AFTER
    assert got["square", ">10"][1:] == pytest.approx((1.197, -0.141, 1.093), abs=3e-3)  # Turner median 2.26 (their > 10 Myr reaches far older)
    assert got["annulus", "<=10"][1:] == pytest.approx((10.335, -0.375, 9.247), rel=2e-3)
    assert got["annulus", ">10"][1:] == pytest.approx((10.777, -0.364, 9.425), rel=2e-3)
