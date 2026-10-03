"""S40 (BUILD_II V3): the region regime's two gates, driven through the routes without a browser.

1. Catalogue against field (RENDER_PHYSICS section 7): the clusters' HII-region Halpha summed over a window equals the
   field's HII Halpha integrated over the same level-k cells (/api/render at that level, a 30 A box at 6562.8 A),
   within the census's own noise sqrt(sum L^2)/sum L and the galaxy-wide 1% of D184.
2. Determinism across levels: over one level-0 cell, the clouds and the clusters /api/clouds and /api/clusters
   return at levels 1, 2 and 3 are the level-0 rows, column for column - a nebula the same at every approach.

Measured at S40 (Opus build to Fable's rulings, D190). Small windows are recorded, not gated: the HII luminosities
are heavy-tailed (a few bright regions carry the sum), so a window of a few hundred clusters usually reads low and
occasionally far high, and the realised sqrt(sum L^2)/sum L understates that spread. The ruling (D190): a window is
judged against the population's second moment, sigma(N) = sqrt(<L^2>)/<L> / sqrt(N), and many windows by their
z-scores' mean - the third test below.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.stages import systems as sy

HALPHA_BOX = json.dumps([{"name": "Halpha", "shape": "box", "centre": 6562.8, "width": 30}])


@pytest.fixture(scope="module")
def svc():
    return Service()


def _get(svc, path, query):
    r = svc.handle(path, query)
    assert r.status == 200, (path, query, r.body[:300])
    return wire.decode(r.body)


def _window(r0, r1, p0, p1):
    return f"r_min={r0}&r_max={r1}&phi_min={p0}&phi_max={p1}"


def _clusters_against_field(svc, window, level):
    _, a = _get(svc, "/api/render", f"{window}&level={level}&filters={HALPHA_BOX}")
    R = svc.grid.R
    bounds = [sy.cell_bounds(R, int(c), level) for c in a["cell"]]
    area_pc2 = np.array([0.5 * (b["r_hi"] ** 2 - b["r_lo"] ** 2) * (b["phi_hi"] - b["phi_lo"]) for b in bounds]) * 1e6
    field = float((np.asarray(a["halpha_hii"], dtype=float)[:, 0] * area_pc2).sum())
    _, c = _get(svc, "/api/clusters", f"{window}&level={level}")
    lum = np.asarray(c["hii_halpha_luminosity"], dtype=float)
    noise = math.sqrt(float((lum**2).sum())) / float(lum.sum())
    return float(lum.sum()) / field, noise, lum.size


@pytest.mark.parametrize(
    "window, level, measured",
    [
        # S51 (D210): the clouds, so the clusters, on the gas's own ridge - another draw of the same census - and
        # /api/render's HII Halpha placed by the same gas contrast (Phases 2 and 3 together, read by the lead). The
        # disc's ratio does not depend on where the field is placed round a ring; the sector's does.
        (_window(0.5, 20.0, 0.0, 2.0 * math.pi), 0, 1.0140),  # the disc: 12 670 clusters, noise 0.060; S51 (D210): was 0.9801 (12 597, 0.061)
        (_window(4.0, 12.0, 0.0, 2.0), 1, 0.9942),  # a quarter-disc sector at level 1: 2 476 clusters, noise 0.161; S51 (D210): was 0.9744 (2 499, 0.138)
    ],
)
def test_the_clusters_halpha_integrates_back_to_the_field(svc, window, level, measured):
    ratio, noise, n = _clusters_against_field(svc, window, level)
    assert ratio == pytest.approx(1.0, abs=3.0 * noise + 0.02)  # the census's noise and D184's galaxy-wide 1%
    assert ratio == pytest.approx(measured, abs=1e-3)  # the record, dated S40
    assert n > 1000


def test_small_windows_are_recorded_not_gated(svc):
    """The heavy tail at work: two windows of a few hundred clusters read 0.67 and 0.51 (1.4 and 2.0 of their own
    realised noise low; 1.4 and 1.1 of the population's sigma(N), D190). Pinned as the record, no pass/fail on the ratio."""
    r1, n1, k1 = _clusters_against_field(svc, _window(6.0, 10.0, 0.0, 1.2), 1)
    r2, n2, k2 = _clusters_against_field(svc, _window(7.0, 9.0, 0.0, 0.8), 2)
    # S51 (D210): the clusters and the field's HII Halpha both on the gas's ridge; was 0.6745 / 832, 0.5107 / 246,
    # z -1.36 / -1.11
    assert r1 == pytest.approx(0.6971, abs=1e-3) and k1 == 806
    assert r2 == pytest.approx(0.4670, abs=1e-3) and k2 == 212
    assert (r1 - 1.0) / (C_POP / math.sqrt(k1)) == pytest.approx(-1.26, abs=0.02)
    assert (r2 - 1.0) / (C_POP / math.sqrt(k2)) == pytest.approx(-1.14, abs=0.02)


# sqrt(<L^2>) / <L> over the disc's 12 597 HII regions (S40 review): the census's own second moment, so that a window
# of N regions scatters by C_POP / sqrt(N) about the field - 0.24 at N 832, 0.44 at N 246, 0.06 over the disc.
C_POP = 6.798  # S51 (D210): was 6.898 - 12 670 regions, another draw of the census (the clouds on the gas's ridge)


def test_many_windows_scatter_as_the_census_does_not_as_any_one_reads(svc):
    """The ruling on the small windows (D190). A window's realised noise is correlated with its reading - a window
    that misses the bright tail reads low and estimates its own noise low - so no one window's ratio is a gate. Sixty
    level-1 windows tiling r 4-12 kpc (2 kpc rings, 15 sectors; 100-342 clusters each, median 163), each judged
    against the population's sigma(N): z mean +0.15, sd 1.16, 90% inside 2 sigma and 98% inside 3; the ratios' mean
    1.085 and median 0.857, the heavy tail's skew. The gate is the mean z; the median and the mean are the record."""
    _, disc = _get(svc, "/api/clusters", _window(0.5, 20.0, 0.0, 2.0 * math.pi))
    lum = np.asarray(disc["hii_halpha_luminosity"], dtype=float)
    c_pop = math.sqrt(float((lum**2).mean())) / float(lum.mean())
    assert c_pop == pytest.approx(C_POP, abs=1e-2)
    ratios, sizes = [], []
    for r0 in (4.0, 6.0, 8.0, 10.0):
        for k in range(15):
            p0, p1 = round(k * 2.0 * math.pi / 15, 6), round((k + 1) * 2.0 * math.pi / 15, 6)
            q, _, n = _clusters_against_field(svc, _window(r0, r0 + 2.0, p0, p1), 1)
            ratios.append(q)
            sizes.append(n)
    q, n = np.array(ratios), np.array(sizes)
    # S51 (D210): was >= 100 - the clusters crowd the gas's narrow ridge, so the thinnest interarm window holds 95
    assert n.min() >= 90 and len(q) == 60
    z = (q - 1.0) / (c_pop / np.sqrt(n))
    assert abs(float(z.mean())) < 0.5  # three standard errors of the mean at sd 1.16 over sixty windows
    assert 0.7 < float(z.std()) < 1.5  # one galaxy-wide moment for a luminosity function that varies with radius
    assert float(np.mean(np.abs(z) < 3.0)) >= 0.95
    # the record, dated S40; S51 (D210): z mean 0.15 -> 0.139 (sd 1.16 -> 1.09, 90 % inside 2 and 97 % inside 3),
    # median 0.8567 -> 0.9061, mean 1.0853 -> 1.0782 - the clusters and the field's HII Halpha both on the gas's ridge
    assert float(z.mean()) == pytest.approx(0.139, abs=0.01)
    assert float(np.median(q)) == pytest.approx(0.9061, abs=1e-3)
    assert float(q.mean()) == pytest.approx(1.0782, abs=1e-3)


@pytest.mark.parametrize("path, key", [("/api/clouds", ("cloud_radius", "cloud_azimuth")), ("/api/clusters", ("cluster_radius", "cluster_azimuth"))])
def test_a_census_is_the_same_at_every_level(svc, path, key):
    b = sy.cell_bounds(svc.grid.R, 300, 0)
    eps = 1e-6
    window = _window(b["r_lo"] + eps, b["r_hi"] - eps, b["phi_lo"] + eps, b["phi_hi"] - eps)
    rows_at = []
    for level in range(4):
        _, a = _get(svc, path, f"{window}&level={level}")
        names = sorted(n for n in a if np.asarray(a[n]).ndim == 1)
        rows = {
            (float(a[key[0]][i]), float(a[key[1]][i])): tuple(float(a[n][i]) for n in names)
            for i in range(len(a[key[0]]))
        }
        rows_at.append(rows)
    assert len(rows_at[0]) > 10  # 58 clouds and 42 clusters at S40
    for level in (1, 2, 3):
        assert rows_at[level] == rows_at[0], (path, level)


@pytest.mark.parametrize("path", ["/api/clouds", "/api/clusters", "/api/remnants"])
def test_every_census_row_is_named_and_the_header_counts_the_body(svc, path):
    """S40: each row carries its (cell, index) - the path the viewer seeds a cloud's interior by - and a level filter
    recomputes the header's per-cell counts from the rows it keeps (until S40 they stayed the unfiltered cells':
    257 counted against 155 returned for the clouds of r 7-9, phi 0-0.4 at level 2)."""
    window = _window(7.0, 9.0, 0.0, 0.4)
    _, base = _get(svc, path, f"{window}&level=0")
    named0 = set(zip(np.asarray(base["cell"]).tolist(), np.asarray(base["index"]).tolist()))
    for level in (0, 2):
        h, a = _get(svc, path, f"{window}&level={level}")
        n = len(a["cell"])
        assert sum(h["cells"]["counts"]) == n
        cells = np.asarray(a["cell"])
        for cell, count in zip(h["cells"]["ids"], h["cells"]["counts"]):
            assert int((cells == cell).sum()) == count
        assert set(zip(cells.tolist(), np.asarray(a["index"]).tolist())) <= named0  # a kept row keeps its name
