"""Audit VI (S94), strand 2: what BUILD_V's three batches built, re-measured on seeds and a mesh they did not pin.

M1-M3 (S86-S93) discharged register items on tests their builders wrote. This file re-measures those claims by
estimators written here (B3: a check that takes the build's own path checks only the build), on **texture seeds 5151,
6060 and 31337** and the mesh **96 rings, 320 steps, 6 heights, 72 azimuths** (``AUDIT_VI_GRID``), neither of which
any earlier test pins. A claim that fails its measurement here is the audit's finding, not this file's bug: it is held
under ``xfail(strict=True)`` naming the finding (F-2-n, ``docs/AUDIT_VI.md``), its measured number in the assertion's
message. Nothing here changes the model (B3); the builder's note (the session's scratchpad, s94_2.md) has the runs.
"""

from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from galaxy import templates
from galaxy.core import seeds as _seeds
from galaxy.core.grids import GridSpec
from galaxy.layer import arm_pieces as ap
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.stages.pattern import PIECE_FIELDS, bar_terms

ROOT = Path(__file__).resolve().parents[1]
AUDIT_VI_GRID = GridSpec(n_R=96, n_t=320, n_z=6, n_phi=72)
SEEDS = (5151, 6060, 31337)
TEMPLATE_NAMES = ("milky_way", "ngc_4414")


def _python(code: str, **env: str) -> str:
    """Run ``code`` in a fresh interpreter (its own PYTHONHASHSEED / thread count) and return its stdout."""
    full = {**os.environ, **env}
    done = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=full, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    assert done.returncode == 0, done.stderr[-3000:]
    return done.stdout


# ---------------------------------------------------------------------------------------------------------------------
# 1. #173: the migration test's once-seen failure - hash order or left state
# ---------------------------------------------------------------------------------------------------------------------

_MIGRATION = """
from galaxy.core.registry import production
from galaxy.run import run
m = production()[0].get("basic")
only = ("metallicity_gradient_old", "metallicity_gradient")
a = run(m, {"migration_efficiency": 0.0}, only=only).fields
b = run(m, {"migration_efficiency": 7.0}, only=only).fields
print(" ".join(float(x).hex() for x in (a["metallicity_gradient_old"], b["metallicity_gradient_old"],
                                        a["metallicity_gradient"], b["metallicity_gradient"])))
"""


def test_173_the_migration_node_s_numbers_do_not_follow_the_hash_seed():
    """#173 (S65, D225): ``test_chemistry.py::test_migration_flattens_old_stars_and_leaves_gas_alone[basic]`` once
    read 0.8845979 against 0.9284296 in a whole-suite run and never again. Candidate (a), a hash-order dependence: the
    node's four numbers (the old population's gradient with migration 0 and 7, the gas's gradient with each) computed
    in two fresh interpreters under PYTHONHASHSEED 0 and 12345 are the same bits. Measured at S94 (s94_2.md): the node
    alone under hash seeds 0, 1, 2, 12345 and a random one reads -0.2801196316960978 / -0.005541389266041417 every
    time, and the file whole in its order and three shuffled orders passes - candidate (b) not seen either; the
    once-seen numbers are not this model's (the old gradient is negative here, so the record predates a later model).
    Fails if the numbers part between the two hash seeds, or the node's inequality fails."""
    one = _python(_MIGRATION, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1").split()
    two = _python(_MIGRATION, PYTHONHASHSEED="12345", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1").split()
    assert one == two, (one, two)
    old_none, old_lots, gas_none, gas_lots = (float.fromhex(v) for v in one)
    assert abs(old_lots) < abs(old_none) and old_lots > old_none, (old_none, old_lots)
    assert gas_none == pytest.approx(gas_lots), (gas_none, gas_lots)


# ---------------------------------------------------------------------------------------------------------------------
# Shared: the default model's runs on the audit mesh, both templates, the three seeds
# ---------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def audit_model(prod):
    return prod[0].get(DEFAULT_MODEL)


@pytest.fixture(scope="module")
def K(audit_model):
    return {k: c.value for k, c in audit_model.constants.items()}


def _inputs(tpl: str, seed: int) -> dict:
    return {**templates.overrides(templates.TEMPLATES[tpl]), "texture_seed": seed}


@pytest.fixture(scope="module")
def runs(audit_model):
    """{(template, seed): the layer-on run on AUDIT_VI_GRID}."""
    return {(t, s): run(audit_model, _inputs(t, s), grid=AUDIT_VI_GRID, layer=True)
            for t in TEMPLATE_NAMES for s in SEEDS}


# ---------------------------------------------------------------------------------------------------------------------
# 2. #216: the arm census's births do not follow the last bit
# ---------------------------------------------------------------------------------------------------------------------


def _lay(out, inputs, K, seed, design_count=None):
    """The census re-laid outside the stage from the run's own published inputs to it (``ap.census``, the stream
    keyed as the stage keys it: the texture seed, the slot ``arm_pieces``)."""
    f = out.fields
    R = out.grid.R
    pitch, bar = float(f["pitch_angle"]), float(f["bar_half_length"])
    law = ap.Law.of(pitch, str(f["arm_class"]), K)
    count = np.asarray(f["arm_design_count"], dtype=float) if design_count is None else design_count
    return ap.columns(ap.census(R, count, law, str(f["arm_class"]), bar, bar_terms(R, pitch, bar)[2],
                                inputs.get("arm_pieces") or (), float(f["sun_azimuth"]),
                                lambda *p: _seeds.rng(seed, "arm_pieces", *p)))


def _same_census(a, b) -> bool:
    """What a birth decides: how many pieces, on which chain, starting where (radius kpc and azimuth rad within
    1e-9, the azimuth's difference read round the turn - a one-ulp nudge moves a start by ulps, another birth by far
    more)."""
    ca, cb = np.asarray(a["arm_piece_chain"]), np.asarray(b["arm_piece_chain"])
    if ca.shape != cb.shape or not np.array_equal(ca, cb):
        return False
    ra, rb = (np.asarray(c["arm_piece_start_radius"], dtype=float) for c in (a, b))
    pa, pb = (np.asarray(c["arm_piece_start_azimuth"], dtype=float) for c in (a, b))
    turn = np.abs(np.remainder(pa - pb + math.pi, 2.0 * math.pi) - math.pi)
    return bool(np.all(np.abs(ra - rb) <= 1e-9) and np.all(turn <= 1e-9))


@pytest.mark.parametrize("tpl", TEMPLATE_NAMES)
def test_216_the_arm_census_is_unmoved_by_a_one_ulp_nudge_of_what_the_births_compare(runs, K, tpl, monkeypatch):
    """#216 (S91, D260): the births compare the law's arm number with the crossings (``counted``) and take the widest
    azimuthal gap (``Laying.widest_gap``); both are now read with a stated tolerance, so a one-ulp change of either
    must leave the census unmoved. Re-measured on three seeds the build did not pin and this file's mesh: the census
    re-laid outside the stage (checked first to be the published table, column by column, bit for bit), then (i) the
    whole design count moved one ulp up and one ulp down (``np.nextafter``), (ii) every crossing's azimuth moved one
    ulp up and one ulp down (``Laying.identified_crossings`` wrapped here, monkeypatched, the model's file untouched).
    Fails if any nudge moves the number of pieces, a piece's chain, or the ring a piece starts on."""
    for seed in SEEDS:
        out, inputs = runs[tpl, seed], _inputs(tpl, seed)
        base = _lay(out, inputs, K, seed)
        for name in PIECE_FIELDS:
            assert np.array_equal(np.asarray(base[name]), np.asarray(out.fields[name]), equal_nan=True), (seed, name)
        count = np.asarray(out.fields["arm_design_count"], dtype=float)
        for direction in (np.inf, -np.inf):
            nudged = _lay(out, inputs, K, seed, design_count=np.nextafter(count, direction))
            assert _same_census(nudged, base), (tpl, seed, "design count", direction)
        original = ap.Laying.identified_crossings
        for direction in (np.inf, -np.inf):
            def nudged_crossings(self, x, _d=direction):
                return [(float(np.nextafter(a, _d)), who) for a, who in original(self, x)]
            monkeypatch.setattr(ap.Laying, "identified_crossings", nudged_crossings)
            nudged = _lay(out, inputs, K, seed)
            monkeypatch.setattr(ap.Laying, "identified_crossings", original)
            assert _same_census(nudged, base), (tpl, seed, "crossing azimuths", direction)


# ---------------------------------------------------------------------------------------------------------------------
# 3. #218: every draw path's bits at one BLAS thread and at the machine's count
# ---------------------------------------------------------------------------------------------------------------------

_DRAWS = """
import hashlib
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
api = Service(grid=GridSpec(n_R=96, n_t=320, n_z=6, n_phi=72), cache=2)
common = {"template": ["milky_way"], "texture_seed": ["6060"], "pattern_seed": ["4141"]}
window = {"r_min": ["7.3"], "r_max": ["9.1"], "phi_min": ["0.4"], "phi_max": ["1.3"]}
asks = [
    ("region", "/api/region", {**window, "stars": ["4000"]}),
    ("region_l2", "/api/region", {**window, "stars": ["4000"], "level": ["2"]}),
    ("clouds", "/api/clouds", dict(window)),
    ("clusters", "/api/clusters", dict(window)),
    ("remnants", "/api/remnants", dict(window)),
    ("bright", "/api/bright", {**window, "l_min": ["3000"]}),
    ("layer", "/api/layer", {}),
]
for name, path, q in asks:
    r = api.handle(path, {**common, **q})
    assert r.status == 200, (name, r.status, r.body[:300])
    print(name, len(r.body), hashlib.sha256(r.body).hexdigest())
"""


def test_218_every_draw_reads_the_same_bits_at_one_thread_and_at_the_machine_s_count():
    """#218 (S92-S93, D261-D262): a BLAS product's summation order follows its thread count, so S93 made every product
    on a draw path a sum the model orders itself; ``tests/test_ordered_products.py`` guards the source (an ``ast``
    scan, no run) and says itself that "the pair of runs at two thread counts in separate processes is not built
    here". Built here, on a seed pair, a mesh and a window the build's runs did not use: the Milky Way at texture seed
    6060 and pattern seed 4141 on AUDIT_VI_GRID, the star sample (levels 0 and 2), the clouds, the clusters, the
    remnants and the bright catalogue of the window R 7.3-9.1 kpc, phi 0.4-1.3 rad, and the layer's own entry, each
    answer's bytes digested in a fresh interpreter at OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = 1 and with both unset
    (the machine's count). Fails if any answer's bytes differ."""
    one = _python(_DRAWS, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    unrestricted = {k: v for k, v in os.environ.items() if k not in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                                      "MKL_NUM_THREADS")}
    done = subprocess.run([sys.executable, "-c", _DRAWS], cwd=ROOT, env=unrestricted, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    assert done.returncode == 0, done.stderr[-3000:]
    a, b = one.splitlines(), done.stdout.splitlines()
    assert len(a) == 7, one
    assert a == b, [(x, y) for x, y in zip(a, b) if x != y]


# ---------------------------------------------------------------------------------------------------------------------
# 4. #175: the remainder's kept windows are a split of the unsplit middle part
# ---------------------------------------------------------------------------------------------------------------------


def _curves(name: str) -> str:
    import json

    sets = json.loads((ROOT / "frontend/src/galaxy/filters.json").read_text(encoding="utf-8"))["sets"]
    return json.dumps(sets[name]["curves"])


def _rgb() -> str:
    return _curves("rgb")


def test_175_the_remainder_s_kept_windows_split_the_middle_part_the_unsplit_answer_ships(audit_api):
    """#175 (S93, D262): ``only=remainder`` with ``kept=1`` adds three per-ring arrays, the middle part's light in
    three of its four age windows, and its builder's test sums them with the fourth taken as what is left - which
    holds by construction. Asked here instead against the answer WITHOUT ``kept=``, the unsplit array S64 shipped
    (the viewer's switch between the two is live): ngc_4414 at texture seed 31337 on this file's mesh, the RGB set,
    l_min 2000 Lsun (between two grid thresholds). The kept answer's middle part is the unsplit answer's to 1e-12
    (every array the two share, the same to 1e-12); each kept window is non-negative and the three sum to at most the
    middle part (the fourth, the rest, non-negative, to 1e-12); and the windows tile the middle part's age range
    without a gap or an overlap. Fails if asking ``kept=1`` moves the remainder, or a window is negative, or the
    windows overlap."""
    q = dict(template="ngc_4414", texture_seed=31337, only="remainder", filters=_rgb(), l_min=2000)
    h0, a0 = _answer(audit_api, "/api/render", **q)
    h1, a1 = _answer(audit_api, "/api/render", **q, kept=1)
    shared = sorted(set(a0) & set(a1))
    assert "stars_unresolved_middle" in shared, (sorted(a0), sorted(a1))
    for name in shared:
        x, y = np.asarray(a0[name], dtype=float), np.asarray(a1[name], dtype=float)
        scale = np.maximum(np.abs(x), 1e-300)
        assert x.shape == y.shape and np.all(np.abs(x - y) <= 1e-12 * scale), (name, float(np.max(np.abs(x - y))))
    kept = h1["remainder"]["middle_kept"]
    parts = [np.asarray(a1[kept["arrays"][k]], dtype=float) for k in ("3", "2", "1")]
    middle = np.asarray(a1["stars_unresolved_middle"], dtype=float)
    assert all(np.all(p >= 0.0) for p in parts)
    rest = middle - sum(parts)
    assert np.all(rest >= -1e-12 * np.maximum(middle, 1e-300)), float(np.min(rest / np.maximum(middle, 1e-300)))
    assert float(np.sum(sum(parts))) > 0.0
    ages = [tuple(map(float, kept["ages_gyr"][k])) for k in ("3", "2", "1", "rest")]
    spans = sorted(ages)
    assert all(lo < hi for lo, hi in spans), ages
    assert all(abs(spans[i][1] - spans[i + 1][0]) <= 1e-12 for i in range(len(spans) - 1)), ages


# ---------------------------------------------------------------------------------------------------------------------
# 5. T2 / #114: the cluster points' light through a filter set closes on the render's young part
# ---------------------------------------------------------------------------------------------------------------------


def test_114_the_clusters_summed_response_through_sho_is_the_young_part_s_colour(audit_api):
    """T2 / #114 (S91, D260): ``/api/clusters`` with ``filters=`` gives each cluster's own band light through each
    curve, and summed over the census it closes on the render's young part (``stars_young`` times its placing weight,
    per cell, times the cell's area): the build read the RGB set at 6500 K on the default seed - 0.940 / 0.938 / 0.933
    over the disc, the 6 % the census's draw against its expectation, the colour to 1 %. Re-measured on the Hubble
    palette (``sho``, three narrow bands, not pinned by the build), the Milky Way at texture seed 5151, this file's
    mesh, the cells' areas integrated here: the clusters over the young part per filter within 0.80-1.20 (the census's
    light spreads 4.4 % seed to seed, D210: about four of it), and the three filters' ratios within 3 % of each other
    (the colour). Fails if the filter path tints the census against the field's young part."""
    from galaxy.stages import systems as sy

    q = dict(template="milky_way", texture_seed=5151, filters=_curves("sho"), white=6500, r_min=0, r_max=1000,
             phi_min=0, phi_max=2.0 * math.pi)
    rh, ra = _answer(audit_api, "/api/render", level=0, **q)
    R = audit_api.grid.R
    edges, sectors = sy.cell_edges(R)
    cell = np.asarray(ra["cell"], dtype=np.int64)
    ring, sector = np.divmod(cell, sy.CELL_SECTORS)
    area = 0.5 * (edges[ring + 1] ** 2 - edges[ring] ** 2) * (sectors[sector + 1] - sectors[sector]) * 1e6  # pc2
    weight = rh["ages"]["parts"]["young"]["weight"]
    young = (np.asarray(ra["stars_young"], dtype=float) * np.asarray(ra[weight], dtype=float)[:, None]
             * area[:, None]).sum(axis=0)
    _, ca = _answer(audit_api, "/api/clusters", **q)
    clusters = np.asarray(ca["response"], dtype=float).sum(axis=0)
    ratio = clusters / young
    assert ratio.size == 3 and np.all(young > 0.0), (young, clusters)
    assert np.all((ratio > 0.80) & (ratio < 1.20)), ratio
    assert float(ratio.max() / ratio.min()) < 1.03, ratio


# ---------------------------------------------------------------------------------------------------------------------
# 7. #197 (with #161's ring as the unit): every catalogue's ring draw on its ring's own interval
# ---------------------------------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def audit_api():
    from galaxy.api.service import Service

    return Service(grid=AUDIT_VI_GRID, cache=2)


def _answer(api, path, **q):
    from galaxy.api import wire

    r = api.handle(path, {k: [str(v)] for k, v in q.items()})
    assert r.status == 200, (path, q, r.body[:300])
    return wire.decode(r.body)


def _cell_column(arrays, prefix):
    names = [k for k in arrays if k == "cell" or k == f"{prefix}_cell"]
    assert len(names) == 1, sorted(arrays)
    return np.asarray(arrays[names[0]], dtype=np.int64)


DISC = {"r_min": 0.0, "r_max": 30.0, "phi_min": 0.0, "phi_max": 2.0 * math.pi}


@pytest.mark.parametrize("tpl", TEMPLATE_NAMES)
def test_197_no_star_remnant_or_cloud_is_drawn_outside_its_level_0_ring(audit_api, tpl):
    """#197 (S90, D258): the star sample's level-0 radii, the remnants' and the clouds' birth radii are drawn on the
    ring's own interval (``systems.ring_birth_radius``) - before it about 5 % of stars and remnants stood up to 70 pc
    below their ring. Re-measured through the routes (the whole disc, level 0) on two texture seeds the build did not
    pin and this file's mesh, each row's radius against its own cell's ring edges (``cell_edges`` of the mesh, the
    ring the cell id names): no row outside [lo, hi] (a 1e-9 kpc allowance for the edge's own arithmetic).
    Fails if any row stands outside its ring."""
    from galaxy.stages.systems import CELL_SECTORS, cell_edges

    edges, _ = cell_edges(audit_api.grid.R)
    report = {}
    for seed in SEEDS[:2]:
        # brightest= past the sample's size: every star kept, each row named by its cell (level 0 names none).
        asks = (("star", "/api/region", "star_radius", {"brightest": 200000}), ("remnant", "/api/remnants", "remnant_radius", {}),
                ("cloud", "/api/clouds", "cloud_birth_radius", {}))
        for prefix, path, column, extra in asks:
            _, arrays = _answer(audit_api, path, template=tpl, texture_seed=seed, **DISC, **extra)
            ring = _cell_column(arrays, prefix) // CELL_SECTORS
            r = np.asarray(arrays[column], dtype=float)
            below = edges[ring] - r
            above = r - edges[ring + 1]
            report[seed, prefix] = (r.size, int((below > 1e-9).sum()), int((above > 1e-9).sum()),
                                    float(max(below.max(initial=0.0), above.max(initial=0.0))))
    assert all(0 < n < 200000 for n, _, _, _ in report.values()), report
    assert all(lo == 0 and hi == 0 for _, lo, hi, _ in report.values()), report


# ---------------------------------------------------------------------------------------------------------------------
# 8. #164, #165, #213: a spur's height over the ring's trough; the walk ends at the arms' budget's edge
# ---------------------------------------------------------------------------------------------------------------------

TROUGH_SAMPLES = 8192


def test_164_165_213_a_spur_is_the_crest_s_excess_over_its_ring_s_trough_inside_the_budget(runs, K):
    """#164 / #165 (S92, D261) and #213 (S90, D258), re-derived from the published ``gas_spur`` table on the Milky Way
    at the three seeds and this file's mesh. #213: no foot stands past the last grid ring whose
    ``arm_piece_amplitude`` (published) is above 0. #165: the table's peak column over the ring's gas column
    (``gas_surface_density``, linear in R) is the crest the walk read; #164: the height ``gas_spur_contrast`` is that
    crest less the ring's trough - the trough read here as the least of the unspurred gas contrast on 8192 azimuths
    of each bracketing grid ring (the build reads 1440 cell centres), linear in R between them; agreement within
    2e-3 (the two samplings' own difference) on every foot whose height is above 0. Fails if a foot stands past the
    budget's edge, or a height is not the crest's excess over the trough."""
    from galaxy.layer import compose

    phis = -math.pi + (np.arange(TROUGH_SAMPLES) + 0.5) * (2.0 * math.pi / TROUGH_SAMPLES)
    report = {}
    for seed in SEEDS:
        out = runs["milky_way", seed]
        f, R = out.fields, out.grid.R
        amp = np.asarray(f["arm_piece_amplitude"], dtype=float)
        edge = float(R[np.flatnonzero(amp > 0.0)[-1]])
        radius = np.asarray(f["gas_spur_radius"], dtype=float)
        height = np.asarray(f["gas_spur_contrast"], dtype=float)
        peak = np.asarray(f["gas_spur_peak_surface_density"], dtype=float)
        assert radius.size > 0, seed
        assert float(radius.max()) <= edge, (seed, float(radius.max()), edge)
        crest = peak / np.interp(radius, R, np.asarray(f["gas_surface_density"], dtype=float))
        gas = compose.gas_pattern(f, R, K)
        upper = np.clip(np.searchsorted(R, radius, side="right"), 1, R.size - 1)
        lower = upper - 1
        rings = np.unique(np.concatenate([lower, upper]))
        floor = {int(i): float(np.min(gas.unspurred_contrast_at(np.full(phis.size, R[i]), phis))) for i in rings}
        w = (radius - R[lower]) / (R[upper] - R[lower])
        trough = (1.0 - w) * np.array([floor[int(i)] for i in lower]) + w * np.array([floor[int(i)] for i in upper])
        up = height > 0.0
        miss = np.abs(crest[up] - trough[up] - height[up])
        report[seed] = (radius.size, int(up.sum()), float(radius.max()), edge, float(miss.max(initial=0.0)))
        assert np.all(crest >= trough - 2e-3), (seed, float(np.min(crest - trough)))
    assert all(m <= 2e-3 for *_, m in report.values()), report


# ---------------------------------------------------------------------------------------------------------------------
# 10. T10 / #119: the diffuse gas's [N II] and [S II] against the relation they cite
# ---------------------------------------------------------------------------------------------------------------------


def test_119_the_diffuse_gas_s_line_ratios_are_madsen_s_relation_at_the_layer_s_temperature(runs, K):
    """T10 / #119 (S93, D262): the nebular stage publishes the diffuse gas's [N II] 6583, [S II] 6716 and 6731 as
    Madsen, Reynolds & Haffner 2006's eqs. 2-3 at the layer's temperature (``DIG_TEMPERATURE``) on the four level-0
    constants, 6731 by Sanders et al. 2016's low-density doublet ratio (R_max 1.4484). Written here from the register's
    own transcription of the relation (``docs/GALAXY_INPUTS.md`` #119: [N II]/Halpha = 1.62e5 T4^0.4 exp(-2.18/T4)
    (N+/N)(N/H); [S II] 6716/[N II] = 4.62 exp(0.04/T4)(S+/S)(S/H)/((N+/N)(N/H))), not the stage's function: each
    published per-ring line array over the published diffuse Halpha, on every ring that has any, on both templates and
    every seed, equals it to 1e-12, and the published scalars too; 6716/6731 is 1.4484 to 2e-4 (the register's
    R_max - the stage reads Sanders' fit at 1 cm^-3, 1.44818, which the cited table rounds). Fails if a ring's ratio
    is not the cited relation (a per-ring abundance or temperature entering unannounced)."""
    t4 = float(K["DIG_TEMPERATURE"]) / 1.0e4
    n_term = float(K["DIG_N_PLUS_FRACTION"]) * float(K["DIG_NITROGEN_ABUNDANCE"])
    nii = 1.62e5 * t4 ** 0.4 * math.exp(-2.18 / t4) * n_term
    sii = nii * 4.62 * math.exp(0.04 / t4) * float(K["DIG_S_PLUS_FRACTION"]) * float(K["DIG_SULPHUR_ABUNDANCE"]) / n_term
    # The register's numbers at the layer's 8000 K: 0.5827 and 0.4387.
    assert nii == pytest.approx(0.5827, abs=1e-4) and sii == pytest.approx(0.4387, abs=1e-4), (nii, sii)
    for (tpl, seed), out in runs.items():
        f = out.fields
        ha = np.asarray(f["halpha_surface_brightness_dig"], dtype=float)
        lit = ha > 0.0
        assert lit.sum() > 10, (tpl, seed)
        for name, want in (("nii_6583", nii), ("sii_6716", sii)):
            got = np.asarray(f[f"{name}_surface_brightness_dig"], dtype=float)[lit] / ha[lit]
            assert np.max(np.abs(got / want - 1.0)) < 1e-12, (tpl, seed, name, float(got.min()), float(got.max()), want)
        assert float(f["dig_nii_6583_ratio"]) == pytest.approx(nii, rel=1e-12)
        assert float(f["dig_sii_6716_ratio"]) == pytest.approx(sii, rel=1e-12)
        doublet = np.asarray(f["sii_6716_surface_brightness_dig"], dtype=float)[lit] / np.asarray(
            f["sii_6731_surface_brightness_dig"], dtype=float)[lit]
        assert np.max(np.abs(doublet / 1.4484 - 1.0)) < 2e-4, (tpl, seed, float(doublet.min()), float(doublet.max()))


# ---------------------------------------------------------------------------------------------------------------------
# S96 (strand 2 completed): #160, #113 / #171 and #161, the three items S94's builder did not reach
# ---------------------------------------------------------------------------------------------------------------------

S96_RINGS = (7, 8)  # level-0 rings 7-8 of the audit mesh: 6.650-8.506 kpc (cell_edges of AUDIT_VI_GRID)
S96_SYSTEMS_SEED = 77


def _ring_window(api, rings) -> dict:
    """The whole azimuth of level-0 rings ``rings[0]..rings[-1]``, the radii kept a micron inside their outer edges so
    ``cells_in`` names those rings and no neighbour."""
    from galaxy.stages.systems import cell_edges

    edges, _ = cell_edges(api.grid.R)
    return {"r_min": float(edges[rings[0]]) + 1e-6, "r_max": float(edges[rings[-1] + 1]) - 1e-6,
            "phi_min": 0.0, "phi_max": 2.0 * math.pi}


def _level0(api, radius, azimuth):
    """(ring, sector) of each row, from its own radius and azimuth against the mesh's cell edges - read here, not from
    any cell column the route ships."""
    from galaxy.stages.systems import CELL_RINGS, CELL_SECTORS, cell_edges

    edges, _ = cell_edges(api.grid.R)
    ring = np.clip(np.searchsorted(edges, np.asarray(radius, dtype=float), side="right") - 1, 0, CELL_RINGS - 1)
    turn = np.mod(np.asarray(azimuth, dtype=float), 2.0 * math.pi)
    sector = np.clip((turn / (2.0 * math.pi / CELL_SECTORS)).astype(np.int64), 0, CELL_SECTORS - 1)
    return ring, sector


def test_160_the_two_catalogues_old_stars_share_one_azimuthal_placement_per_ring(audit_api):
    """#160 (S61; built S91 on the owner's ruling of 2026-11-10, struck at S95, D264): one placement rule for the old
    stars of both catalogues - the star sample's ``c-bar (1 - p)``, in ``bright.part_weights`` too. The build's test
    (``test_bright.py::test_the_two_catalogues_place_their_old_stars_by_one_rule``) compares the two WEIGHT tables on
    the default Milky Way, the bright catalogue's against ``Placement.sub_ring_weights`` to 1e-12 - the model's own
    functions, no star drawn. Measured here on the REALISED stars instead: ngc_4414 at texture seed 31337, systems
    seed 77, this file's mesh, level-0 rings 7 and 8 (6.65-8.51 kpc) whole; the star sample at stars=3 000 000 (all
    of a ring's stars are drawn, about 148 000 here) and the bright catalogue at l_min = 1800 Lsun (about 61 000
    expected in the window; l_min 1000 holds 148 500 and takes 51 s, l_min 100 is refused above 200 000). Old = older
    than YOUNG_STAR_AGE (0.1 Gyr) in both, by each row's own age column; each row's sector from its own azimuth. The
    estimator: per ring, the 2 x 32 contingency table of old-star counts by sector, the two-sample Pearson chi-square
    (31 degrees of freedom: mean 31, sd sqrt(62) = 7.9), held below mean + 4 sd = 62.5. Not vacuous: each catalogue's
    counts against a uniform azimuth read a chi-square over ten times its degrees of freedom (the arms' contrast,
    shares 0.78-1.45 of the mean). Its power, stated: with about 2 x 10^4 to 9 x 10^4 old stars a catalogue per ring
    the test resolves a per-sector share difference of about 3-5 %; the pre-S91 difference (3.9e-3 of a sector's
    expectation, S61; 1.37e-2 per finest sector) was below it, so this holds the two realised catalogues to one law
    at the noise and does not, alone, distinguish the S91 rule from the one it replaced (the build's weight test
    does). Measured at S96: chi-square 36.1 (ring 7: 94 109 / 22 394 old stars) and 20.1 (ring 8: 53 517 / 14 810).
    Fails if the two catalogues' old stars are placed round a ring by different laws beyond their Poisson noise."""
    from galaxy.stages.systems import YOUNG_STAR_AGE

    common = dict(template="ngc_4414", texture_seed=31337, systems_seed=S96_SYSTEMS_SEED, **_ring_window(audit_api, S96_RINGS))
    _, sa = _answer(audit_api, "/api/region", stars=3_000_000, **common)
    _, ba = _answer(audit_api, "/api/bright", l_min=1800, **common)
    s_ring, s_sector = _level0(audit_api, sa["star_radius"], sa["star_azimuth"])
    b_ring, b_sector = _level0(audit_api, ba["bright_star_radius"], ba["bright_star_azimuth"])
    s_old = np.asarray(sa["star_age"], dtype=float) > YOUNG_STAR_AGE
    b_old = np.asarray(ba["bright_star_age"], dtype=float) > YOUNG_STAR_AGE
    dof = 31
    bound = dof + 4.0 * math.sqrt(2.0 * dof)
    report = {}
    for ring in S96_RINGS:
        a = np.bincount(s_sector[(s_ring == ring) & s_old], minlength=32).astype(float)
        b = np.bincount(b_sector[(b_ring == ring) & b_old], minlength=32).astype(float)
        na, nb = a.sum(), b.sum()
        both = a + b
        ea, eb = both * na / (na + nb), both * nb / (na + nb)
        chi = float(np.sum((a - ea) ** 2 / ea + (b - eb) ** 2 / eb))
        flat_a = float(np.sum((a - na / 32) ** 2 / (na / 32)))
        flat_b = float(np.sum((b - nb / 32) ** 2 / (nb / 32)))
        report[ring] = dict(old=(int(na), int(nb)), chi2=round(chi, 1), bound=round(bound, 1),
                            against_uniform=(round(flat_a), round(flat_b)),
                            shares=(round(float(a.min() / na * 32), 3), round(float(a.max() / na * 32), 3),
                                    round(float(b.min() / nb * 32), 3), round(float(b.max() / nb * 32), 3)))
    assert all(min(r["old"]) > 10_000 for r in report.values()), report
    assert all(min(r["against_uniform"]) > 10 * dof for r in report.values()), report
    assert all(r["chi2"] < bound for r in report.values()), report


def test_171_the_sample_s_luminosity_function_is_the_bright_table_s_at_its_shape(audit_api, audit_model, K):
    """#171 / #113 (S65; built S93: ``photometry.lookup`` reads a star along equivalent evolutionary points; struck
    at S93, D262). Before the mend the sample's count above 10^3 Lsun was 0.14 of the bright table's (S65); the
    build's tests pin the lookup's light per mass formed within 0.07 (``tests/test_photometry.py``) and its closer
    re-read the sample's ages with 400 fresh IMF masses each over the whole disc (scratch, not a test). Measured here
    on the REALISED sample against the published table: the Milky Way at texture seed 6060, systems seed 4242, this
    file's mesh, level-0 rings 7 and 8 (6.65-8.51 kpc) whole; the sample at stars=4 000 000 (about 440 000 in the
    window), its rows older than the cluster window (the table's population) counted above 0.1, 1, 10, 100, 1000 Lsun;
    the table (``/api/bright?table=1``) summed over the window's 64 cells at the same grid thresholds, times the
    sampling fraction s = stars (1 - RETURN_FRACTION) <m> / (the 32 rings' stellar mass, ``cell_masses`` of a run's
    ``stellar_surface_density``) - the sample's own ring expectation over the stars the ring formed.
    **migration_efficiency = 0**: the table reads each ring's own formation history and the sample its arrival law,
    so with migration on the window's age mix differs between them and the ratio reads migration, not the lookup
    (measured at S96 with the default migration: 0.968 / 0.898 / 0.883 / 0.838 / 0.764 at 0.1-1000 Lsun, 5 x 10^6
    stars - the note's F-2-4); with it off the two share one age law and the ratio is the lookup's. Asserted: the
    faint end (0.1 Lsun) within 5 % of 1 (it checks s); the shape - each threshold's ratio over the faint end's - within
    3 sigma of 1 (sigma binomial: sqrt(1/n_L - 1/n_faint)) at every threshold whose expected sample count is at least
    30, which must reach 100 Lsun. 10^3 Lsun expects about 18 sample stars at this size, so it is reported, not held.
    Measured at S96 (5 x 10^6 stars, the same window): 1.029 +- 0.004 / 1.027 / 1.023 / 1.019 +- 0.065 / 1.26 +- 0.24
    at 0.1 / 1 / 10 / 100 / 1000 Lsun. Fails if the sample's bright end again falls short of the table's."""
    from galaxy.stages.systems import cell_masses, cluster_window, imf_mean_mass

    stars = 4_000_000
    inputs = {**_inputs("milky_way", 6060), "migration_efficiency": 0.0}
    sigma = run(audit_model, inputs, grid=AUDIT_VI_GRID, only=("stellar_surface_density",)).fields["stellar_surface_density"]
    mass, _ = cell_masses(np.asarray(sigma, dtype=float), audit_api.grid.R)
    s = stars * (1.0 - float(K["RETURN_FRACTION"])) * imf_mean_mass() / float(mass.sum())
    common = dict(template="milky_way", texture_seed=6060, systems_seed=4242, migration_efficiency=0.0)
    _, sa = _answer(audit_api, "/api/region", stars=stars, **common, **_ring_window(audit_api, S96_RINGS))
    _, ta = _answer(audit_api, "/api/bright", table=1, **common)
    threshold = np.asarray(ta["threshold"], dtype=float)
    table = np.asarray(ta["expected"], dtype=float).reshape(32, 32, -1)[S96_RINGS[0]:S96_RINGS[-1] + 1].sum(axis=(0, 1))
    older = np.asarray(sa["star_age"], dtype=float) > cluster_window(K)
    lum = np.asarray(sa["star_luminosity"], dtype=float)[older]
    rows = {}
    for L in (0.1, 1.0, 10.0, 100.0, 1000.0):
        k = int(np.argmin(np.abs(np.log10(threshold) - math.log10(L))))
        assert abs(math.log10(threshold[k]) - math.log10(L)) < 1e-9, threshold[k]
        rows[L] = (int(np.sum(lum > threshold[k])), s * float(table[k]))
    n0, e0 = rows[0.1]
    report = {L: (n, round(e, 1), round(n / e, 4)) for L, (n, e) in rows.items()}
    assert abs(n0 / e0 - 1.0) < 0.05, report
    held = []
    for L, (n, e) in rows.items():
        if L == 0.1 or e < 30.0:
            continue
        shape = (n / e) / (n0 / e0)
        sigma_shape = shape * math.sqrt(max(1.0 / max(n, 1) - 1.0 / n0, 0.0))
        held.append((L, round(shape, 4), round(sigma_shape, 4)))
        assert abs(shape - 1.0) <= 3.0 * sigma_shape, (L, shape, sigma_shape, report)
    assert max(L for L, *_ in held) >= 100.0, (held, report)


def test_161_the_ring_keeps_its_clouds_count_and_mass_with_the_layer_on_and_off(audit_api):
    """#161 (S61; built S90, the ring as the unit of the clouds' sector weights: the clustering field's cell means
    enter the sector allocation and the ring keeps its total). The build's test (``test_audit_v.py::
    test_census_clustering_keeps_every_ring_s_clouds``, Audit V's mesh 130 x 450 x 9 x 200, texture seeds 4242 / 777)
    counts clouds per ring by their placed (radius, azimuth) and by the drawn radius, on and off the field / layer,
    equal, mass to 1e-12. Measured here through ``/api/clouds`` over the whole disc, both templates, texture seed
    31337, systems seed 77, this file's mesh, layer=on against layer=off, each cloud's ring read three ways - its
    ``cell`` (the allocation's), its placed ``cloud_radius`` against the mesh's ring edges, and its drawn
    ``cloud_birth_radius`` likewise: the per-ring count identical and the per-ring cloud mass (``math.fsum``) equal to
    1e-12 relative, on and off, by each reading; and the per-cell counts NOT identical (the layer moves clouds between
    a ring's sectors - the test is not vacuous). Fails if the layer moves a cloud, or its mass, between rings."""
    from galaxy.stages.systems import CELL_COUNT, CELL_RINGS, CELL_SECTORS

    report = {}
    for tpl in TEMPLATE_NAMES:
        got = {}
        for layer in ("on", "off"):
            _, a = _answer(audit_api, "/api/clouds", template=tpl, texture_seed=31337, systems_seed=S96_SYSTEMS_SEED,
                           layer=layer, **DISC)
            cell = np.asarray(a["cell"], dtype=np.int64)
            mass = np.asarray(a["cloud_mass"], dtype=float)
            placed, _ = _level0(audit_api, a["cloud_radius"], a["cloud_azimuth"])
            drawn, _ = _level0(audit_api, a["cloud_birth_radius"], np.zeros(mass.size))
            got[layer] = dict(cells=np.bincount(cell, minlength=CELL_COUNT), mass=mass,
                              rings={"cell": cell // CELL_SECTORS, "placed": placed, "drawn": drawn})
        on, off = got["on"], got["off"]
        for how in ("cell", "placed", "drawn"):
            n_on = np.bincount(on["rings"][how], minlength=CELL_RINGS)
            n_off = np.bincount(off["rings"][how], minlength=CELL_RINGS)
            m_on = np.array([math.fsum(on["mass"][on["rings"][how] == r]) for r in range(CELL_RINGS)])
            m_off = np.array([math.fsum(off["mass"][off["rings"][how] == r]) for r in range(CELL_RINGS)])
            worst = float(np.max(np.abs(m_on - m_off) / np.maximum(np.abs(m_off), 1e-300)))
            report[tpl, how] = (int(n_on.sum()), int(np.abs(n_on - n_off).sum()), worst)
            assert np.array_equal(n_on, n_off), (tpl, how, (n_on - n_off).tolist())
            assert worst <= 1e-12, (tpl, how, worst)
        moved = int(np.abs(on["cells"] - off["cells"]).sum())
        report[tpl, "cells moved"] = moved
        assert moved > 0, report
    assert all(v[0] > 1000 for k, v in report.items() if k[1] != "cells moved"), report
