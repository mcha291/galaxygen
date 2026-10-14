"""The gas spurs (feathers) off the arm chains' gas ridges (S62, BUILD_III Phase L2; DECISIONS.md D221 items 7-8, as the
lead amended item 7 at S62).

What is held, in the gate's order (item 8 and the brief):

- **the declarations and the graph**: the layer's table ``gas_spur`` on ``texture_seed`` (``layer/spurs.py``), the
  composing stage ``spurs`` that now publishes ``gas_density_contrast`` after the star formation history, the gas
  pattern's stage left with the star-formation contrast, and the three stages that place by the gas reading the table;
- **a spur's shape, by hand**: its point function against the law written here, continuous across its foot and its
  tip; its ring integral and its cell integrals in closed form against dense quadrature;
- **the composition**: the ring mean of the gas contrast exact (1e-12) with spurs, on every ring of the three suite
  galaxies and on other azimuthal grids; the published field the point function's exact cell means;
- **the spacing**: 10 λ_J,sp from the published fields at every foot (to 1 %), and the walk's read of the ridge
  against the point function (the lead's ruling 3, a declared approximation); the spacing in kpc at three radii of
  the Milky Way template - a **disclosed check** against M51's 200-1000 pc (PAWS 276 pc), recorded, not judged;
- **where spurs are**: none in ``ngc_4414`` (flocculent), whose gas contrast is the gas pattern's to the bit;
- **the draw**: rerolling the spurs' stream moves the feet and nothing else of the law; layer off, no row and the
  neutral field.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy import templates
from galaxy.core.fielddoc import TABLES, Kind
from galaxy.core.seeds import rng as seeded_rng
from galaxy.layer import compose
from galaxy.layer import spurs as ls
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs import graph as _graph
from galaxy.stages import gas_pattern as gm
from galaxy.stages import spurs as sp
from galaxy.stages.pattern import ring_bracket

R_SUN = 8.122
G_HAND = 4.30091727e-6  # kpc (km/s)^2 / Msun, written here
SOUND_SPEED_HAND = 6.0  # km/s: the model's GAS_DISPERSION, written here
GALAXIES = ("milky_way", "ngc_4414", "default")
FIELDS = ("gas_density_contrast", "star_formation_gas_contrast", "gas_surface_density", "arm_class", *sp.SPUR_FIELDS, *gm.GAS_PATTERN_READS)
_RUNS: dict[object, object] = {}


def inputs_of(galaxy: str) -> dict:
    return {} if galaxy == "default" else templates.overrides(templates.TEMPLATES[galaxy])


@pytest.fixture(scope="module")
def default_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def galaxy_run(model, galaxy: str, layer: bool = True, **more):
    key = (galaxy, layer, tuple(sorted(more.items())))
    if key not in _RUNS:
        _RUNS[key] = run(model, {**inputs_of(galaxy), **more}, only=FIELDS, layer=layer)
    return _RUNS[key]


def constants(model) -> dict[str, float]:
    return {k: c.value for k, c in model.constants.items()}


def gas_of(model, o):
    gp = compose.gas_pattern(o.fields, o.grid.R, constants(model))
    assert gp is not None and not gp.flat
    return gp


def one_spur(turn: float = 1.0, radius: float = 6.0, amplitude: float = 2.0, **more) -> sp.Spurs:
    shape = dict(pitch_deg=63.0, length=0.24, width=0.06, fall=7.0) | more
    return sp.Spurs([radius], [1.0], [amplitude], [shape["pitch_deg"]], [shape["length"]], [shape["width"]], [shape["fall"]], turn=turn)


def hand_excess(spurs: sp.Spurs, R: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """E of the table's first spur by the law in the module's docstring, written again here."""
    p = math.radians(spurs.pitch_deg[0])
    s, c = math.sin(p), math.cos(p)
    T = spurs.length[0] / spurs.radius[0]
    lam = math.log(spurs.fall[0]) / T
    sigma = spurs.width[0] / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    dx = np.log(R / spurs.radius[0])
    middle = 0.5 * T * c
    psi = middle + np.mod(spurs.turn * (phi - spurs.azimuth[0]) - middle + math.pi, 2 * math.pi) - math.pi
    d, t = dx * c - psi * s, dx * s + psi * c
    var = (sigma / R) ** 2
    A = spurs.amplitude[0]
    return np.where(t < 0, A * np.exp(-(d**2 + t**2) / (2 * var)),
                    np.where(t > T, A / spurs.fall[0] * np.exp(-(d**2 + (t - T) ** 2) / (2 * var)),
                             A * np.exp(-lam * t - d**2 / (2 * var))))


def along_spur(spurs: sp.Spurs, t: np.ndarray, d: float) -> tuple[np.ndarray, np.ndarray]:
    """(R, φ) at along-coordinate t and across-coordinate d (plane units) of the first spur."""
    p = math.radians(spurs.pitch_deg[0])
    s, c = math.sin(p), math.cos(p)
    dx, psi = t * s + d * c, t * c - d * s
    return spurs.radius[0] * np.exp(dx), spurs.azimuth[0] + spurs.turn * psi


# --------------------------------------------------------------------------------------------------------------
# The declarations and the graph
# --------------------------------------------------------------------------------------------------------------


def test_the_table_the_stages_and_the_graph_s_order(default_model, prod):
    assert TABLES == ("arm_piece", "cell", "gas_spur")
    assert [d.name for d in ls.GAS_SPUR_COLUMNS] == list(sp.SPUR_FIELDS) and sp.SPUR_READS == sp.SPUR_FIELDS
    for d in ls.GAS_SPUR_COLUMNS:
        assert d.kind is Kind.TABLE_COLUMN and d.of == "gas_spur" and d.provenance == "synthetic"
        assert d.stands_in_for and d.conserves and d.statistic and "not shown by the viewer" in d.about
    layer_stage, spurs_stage = ls.GAS_SPURS, sp.SPURS
    assert layer_stage.layer_stage and layer_stage.reads_seeds == ("texture_seed",) and layer_stage.checkpoint == 4
    assert set(ls.SPUR_CONSTANTS) <= set(layer_stage.reads_constants)
    assert {"gas_surface_density", "arm_class", *gm.GAS_PATTERN_READS} == set(layer_stage.requires)
    assert [d.name for d in spurs_stage.publishes] == ["gas_density_contrast"] and spurs_stage.publishes[0] is gm.GAS_DENSITY_CONTRAST
    assert set(sp.SPUR_READS) <= set(spurs_stage.requires) and spurs_stage.reads_seeds == ()
    # The gas pattern's stage keeps the contrast the star formation law reads, which carries neither lanes nor spurs.
    assert [d.name for d in gm.GAS_PATTERN.publishes] == ["star_formation_gas_contrast"]
    impls = prod[1]
    for stage in ("clouds", "cloud_texture", "clusters"):
        assert set(sp.SPUR_READS) <= set(impls.get(stage).requires), stage
    for stage in ("bright_stars", "systems", "planets", "sfh_azimuthal"):
        assert not set(sp.SPUR_READS) & set(impls.get(stage).requires), stage
    # The graph's order: the pattern, its gas answer, the star formation history that reads it, the spurs' census
    # after the gas column, the field they compose, then the censuses that place by it.
    order = [s.id for s in _graph.build(default_model, impls, prod[2]).order]
    at = {name: order.index(name) for name in ("gas_pattern", "sfh_azimuthal", "gas_spurs", "spurs", "clouds", "cloud_texture", "clusters")}
    assert at["gas_pattern"] < at["sfh_azimuthal"] < at["gas_spurs"] < at["spurs"] < at["clouds"] < at["cloud_texture"]
    assert at["spurs"] < at["clusters"]


# --------------------------------------------------------------------------------------------------------------
# A spur's shape, by hand
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("turn", (1.0, -1.0))
def test_a_spur_is_the_law_written_here_and_continuous_at_its_foot_and_tip(turn):
    spurs = one_spur(turn)
    T = spurs.span[0]
    for d in (0.0, 0.5 * spurs.sigma[0] / 6.0, 2.0 * spurs.sigma[0] / 6.0):
        t = np.linspace(-0.5 * T, 1.5 * T, 4001)
        R, phi = along_spur(spurs, t, d)
        got = spurs.at(R, phi)
        assert np.allclose(got, hand_excess(spurs, R, phi), rtol=1e-12, atol=1e-300)  # 3.0e-13 at most, measured
        # Across the foot and the tip: the two sides agree to the step's own size, and no step between neighbours
        # is larger than the Gaussian's own slope allows at the sampling (A h / σ√e, h the step in kpc).
        for edge in (0.0, T):
            R2, phi2 = along_spur(spurs, np.array([edge - 1e-12, edge + 1e-12]), d)
            pair = spurs.at(R2, phi2)
            assert abs(pair[1] - pair[0]) < 1e-9 * spurs.amplitude[0], (edge, pair)
        h = (t[1] - t[0]) * 6.0
        bound = spurs.amplitude[0] * max(h / (spurs.sigma[0] * math.sqrt(math.e)), h * spurs.decay[0] / 6.0) * 1.05
        assert np.abs(np.diff(got)).max() < bound
    # Its height at the foot is the amplitude, a seventh of it at the tip, on the axis.
    R, phi = along_spur(spurs, np.array([0.0, T]), 0.0)
    assert np.allclose(spurs.at(R, phi), [2.0, 2.0 / 7.0], rtol=1e-14)


NODES, WEIGHTS = np.polynomial.legendre.leggauss(32)


def split_quadrature(spurs: sp.Spurs, R: float, lo: float, hi: float, panels: int = 64) -> float:
    """∫ E dψ from ``lo`` to ``hi`` on the ring at R (ψ from the first spur's foot in its trailing sense), by Gauss-Legendre
    on panels cut at the two kinks of E in ψ - t = 0 and t = T, where the fall along the spur starts and ends: a rule
    that does not split there carries the kink's h² error (a few 1e-8 on the foot's own ring)."""
    p = math.radians(spurs.pitch_deg[0])
    s, c = math.sin(p), math.cos(p)
    dx = math.log(R / spurs.radius[0])
    cuts = sorted({lo, hi, *(v for v in (-dx * s / c, (spurs.span[0] - dx * s) / c) if lo < v < hi)})
    total = 0.0
    for a, b in zip(cuts[:-1], cuts[1:]):
        edges = np.linspace(a, b, panels + 1)
        half, mid = 0.5 * np.diff(edges), 0.5 * (edges[1:] + edges[:-1])
        psi = (mid[:, None] + half[:, None] * NODES[None, :]).reshape(-1)
        values = hand_excess(spurs, np.full(psi.size, R), spurs.azimuth[0] + spurs.turn * psi).reshape(panels, -1)
        total += float((half[:, None] * WEIGHTS[None, :] * values).sum())
    return total


@pytest.mark.parametrize("turn", (1.0, -1.0))
@pytest.mark.parametrize("radius", (5.97, 6.0, 6.05, 6.17, 6.25, 6.3))
def test_a_spur_s_ring_integral_and_cell_integrals_are_the_closed_forms(turn, radius):
    spurs = one_spur(turn)
    sigma = spurs.sigma[0] / radius
    closed = float(spurs.ring_mean(np.array([radius]))[0])
    reference = split_quadrature(spurs, radius, -12.0 * sigma, spurs.span[0] * spurs.cos[0] + 12.0 * sigma)
    assert 2 * math.pi * closed == pytest.approx(reference, rel=1e-12, abs=1e-18)
    # Cells, on a grid of 360 and on a ragged one: they add up to the ring's whole integral, and each of the six that
    # hold the most is its own integral by the same split rule.
    for edges in (np.linspace(-math.pi, math.pi, 361), np.sort(np.concatenate([[-math.pi, math.pi], np.random.default_rng(3).uniform(-math.pi, math.pi, 50)]))):
        cells = spurs.cell_integrals(np.array([radius]), edges)[0]
        assert cells.sum() == pytest.approx(2 * math.pi * closed, rel=1e-13, abs=1e-18)
        for k in np.argsort(-cells)[:6]:
            ends = sorted(turn * (edges[k:k + 2] - spurs.azimuth[0]))
            assert cells[k] == pytest.approx(split_quadrature(spurs, radius, ends[0], ends[1]), rel=1e-11, abs=1e-14 * cells.sum())


def test_a_ring_the_spur_does_not_reach_reads_nothing():
    spurs = one_spur()
    far = np.array([5.0, 8.0])
    assert not spurs.reads(far).any() and np.all(spurs.ring_mean(far) == 0.0) and np.all(spurs.at(far, np.zeros(2)) == 0.0)
    g = np.array([[0.7, 1.3], [1.1, 0.9]])
    assert np.array_equal(spurs.compose_cells(far, np.array([-math.pi, 0.0, math.pi]), g), g)


# --------------------------------------------------------------------------------------------------------------
# The composition on the suite's galaxies
# --------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("galaxy", GALAXIES)
def test_the_gas_contrast_s_ring_mean_is_exact_with_spurs_on_every_ring(default_model, galaxy):
    o = galaxy_run(default_model, galaxy)
    g = np.asarray(o.fields["gas_density_contrast"])
    assert np.abs(g.mean(axis=1) - 1.0).max() < 1e-12
    gp = gas_of(default_model, o)
    for edges in (np.linspace(-math.pi, math.pi, 37), np.linspace(-math.pi, math.pi, 1001)):
        assert np.abs(gp.cell_means(o.grid.R, edges).mean(axis=1) - 1.0).max() < 1e-12
    if galaxy == "ngc_4414":
        assert gp.spurs is None
    else:
        assert gp.spurs is not None and gp.spurs.count > 0
        mean = gp.spurs.ring_mean(o.grid.R)
        assert 0.0 < mean.max() < 0.1 and np.all(gp.cell_means(o.grid.R, o.grid["phi"].edges) >= 0.0)


def test_the_published_field_is_the_point_function_s_exact_cell_means(default_model):
    o = galaxy_run(default_model, "milky_way")
    gp = gas_of(default_model, o)
    edges = o.grid["phi"].edges
    published = np.asarray(o.fields["gas_density_contrast"])
    assert np.array_equal(published, gp.cell_means(o.grid.R, edges))
    # On the ring that holds the most spur, the published cells against a dense mean of the point function.
    i = int(np.argmax(gp.spurs.ring_mean(o.grid.R)))
    n = (edges.size - 1) * 96
    phi = edges[0] + (np.arange(n) + 0.5) * ((edges[-1] - edges[0]) / n)
    dense = gp.contrast_at(np.full(n, o.grid.R[i]), phi).reshape(edges.size - 1, -1).mean(axis=1)
    assert np.abs(published[i] - dense).max() < 5e-5  # the midpoint rule's h² on a spur 0.43 degrees wide at 96 points a degree: 2.6e-5, measured (S62)


# --------------------------------------------------------------------------------------------------------------
# The spacing, the walk's read, and the disclosed check
# --------------------------------------------------------------------------------------------------------------


def hand_ridge(gp, piece: int, radius: float) -> float:
    """The walk's read of the ridge, written again: the two bracketing grid rings' unspurred contrast at the chain's
    crossing there, linear in R."""
    lower, upper, share = ring_bracket(gp.R, np.array([radius]))
    rings = np.array([int(lower[0]), int(upper[0])])
    az = gp.stars.pieces.along(np.full(2, piece), np.log(gp.R[rings]))
    g = gp.unspurred_contrast_at(gp.R[rings], az)
    return float((1.0 - share[0]) * g[0] + share[0] * g[1])


def test_the_spacing_is_ten_jeans_lengths_of_the_ridge_from_the_published_fields(default_model):
    o = galaxy_run(default_model, "milky_way")
    f, gp, c = o.fields, gas_of(default_model, o), constants(default_model)
    assert (c["GAS_DISPERSION"], c["G"], c["SPUR_SPACING_JEANS"]) == (SOUND_SPEED_HAND, G_HAND, 10.0)
    sigma = np.interp(f["gas_spur_radius"], o.grid.R, f["gas_surface_density"])
    peak = sigma * f["gas_spur_contrast"]
    jeans = SOUND_SPEED_HAND**2 / (G_HAND * 1e6 * peak)
    assert np.allclose(f["gas_spur_peak_surface_density"], peak, rtol=1e-12)
    assert np.allclose(f["gas_spur_jeans_length"], jeans, rtol=1e-12) and np.allclose(f["gas_spur_spacing"], 10 * jeans, rtol=1e-12)
    # Along each chain each foot stands one local spacing on from the last.
    for chain in np.unique(f["gas_spur_chain"]):
        rows = np.flatnonzero(f["gas_spur_chain"] == chain)
        assert np.allclose(np.diff(f["gas_spur_arc"][rows]), f["gas_spur_spacing"][rows][:-1], rtol=1e-12)
    # The foot's contrast is the walk's read, re-derived here, to 1 %: each foot's piece found from its chain's arc.
    pieces = gp.stars.pieces
    for k in range(f["gas_spur_radius"].size):
        members, arc = ls.chain_geometry(pieces, float(f["gas_spur_chain"][k]))
        ends = np.concatenate([[0.0], np.cumsum(arc)])
        i = int(min(np.searchsorted(ends, f["gas_spur_arc"][k], side="right") - 1, members.size - 1))
        assert hand_ridge(gp, int(members[i]), float(f["gas_spur_radius"][k])) == pytest.approx(f["gas_spur_contrast"][k], rel=0.01)


def test_the_walk_s_read_against_the_point_function_as_measured(default_model):
    """The lead's ruling 3: the walk reads the ridge on the two grid rings either side of a foot - a declared
    approximation. Over ten feet spread through the Milky Way template's table the largest relative difference from
    the gas pattern's own point function at the foot is 0.0516 (S62), under ``WALK_READ_DIFFERENCE``."""
    o = galaxy_run(default_model, "milky_way")
    f, gp = o.fields, gas_of(default_model, o)
    sample = np.linspace(0, f["gas_spur_radius"].size - 1, 10).astype(int)
    point = gp.unspurred_contrast_at(f["gas_spur_radius"][sample], f["gas_spur_azimuth"][sample])
    rel = np.abs(f["gas_spur_contrast"][sample] - point) / point
    assert rel.max() <= ls.WALK_READ_DIFFERENCE
    assert rel.max() == pytest.approx(0.0516, abs=5e-4)


def test_the_milky_way_s_spurs_and_spacing_as_measured_a_disclosed_check(default_model):
    """A **disclosed check**, not judged (the lead's ruling 1): M51's measured spacings are ~200 pc inner rising to
    500-1000 pc (La Vigne et al. 2006), PAWS' nine gas spurs 276 pc mean (Schinnerer et al. 2017), 80-2000 pc over
    twenty galaxies (Mandowara et al. 2022). On the Milky Way template the law gives kiloparsecs: the ridge's
    contrast is 1.1-1.6 times the ring's mean where M51's dust lanes stand 10-30 times above the Galaxy's column."""
    o = galaxy_run(default_model, "milky_way")
    f, gp = o.fields, gas_of(default_model, o)
    assert f["gas_spur_radius"].size == 48 and np.unique(f["gas_spur_chain"]).size == 12
    # At three radii: 10 λ_J,sp where each chain crosses, from the published fields and the walk's read.
    pieces = gp.stars.pieces
    table = {}
    for radius in (4.0, R_SUN, 10.0):
        slots = pieces.slots(np.array([radius]))[0]
        live = slots < pieces.count
        sigma = float(np.interp(radius, o.grid.R, f["gas_surface_density"]))
        spacing = sorted(10 * SOUND_SPEED_HAND**2 / (G_HAND * 1e6 * sigma * hand_ridge(gp, int(k), radius)) for k in slots[live])
        table[radius] = (sigma, [round(s, 2) for s in spacing])
    # As measured at S62, kpc, the chains crossing each radius in order of spacing (Σ_gas 22.84, 10.92 and 8.12 M☉/pc²;
    # c_s 6 km/s): the ridge's contrast g read as the walk reads it, 10 c_s² / (G Σ_gas g).
    assert [round(table[r][0], 2) for r in (4.0, R_SUN, 10.0)] == [22.84, 10.92, 8.12]
    assert table[4.0][1] == [1.54, 3.97] and table[R_SUN][1] == [5.27, 5.92, 6.25, 6.52, 6.78]
    assert table[10.0][1] == [6.95, 7.07, 8.26, 8.76, 8.85, 10.27]
    assert all(s > 1.0 for s in table[R_SUN][1])  # outside M51's 0.2-1 kpc: recorded, not judged


def test_a_flocculent_disc_carries_no_spur_and_its_gas_contrast_is_the_pattern_s(default_model):
    o = galaxy_run(default_model, "ngc_4414")
    assert o.fields["arm_class"] == "flocculent" and o.fields["gas_spur_radius"].size == 0
    gp = gas_of(default_model, o)
    assert gp.spurs is None
    assert np.array_equal(o.fields["gas_density_contrast"], gp.cell_means(o.grid.R, o.grid["phi"].edges))


# --------------------------------------------------------------------------------------------------------------
# The draw and the switch
# --------------------------------------------------------------------------------------------------------------


def test_rerolling_the_spurs_stream_moves_the_feet_and_nothing_else_of_the_law(default_model):
    o = galaxy_run(default_model, "milky_way")
    gp, c = gas_of(default_model, o), constants(default_model)
    sigma = o.fields["gas_surface_density"]
    one = ls.columns(ls.lay(gp, sigma, "grand_design", c, lambda *path: seeded_rng(1, "gas_spurs", *path)))
    two = ls.columns(ls.lay(gp, sigma, "grand_design", c, lambda *path: seeded_rng(2, "gas_spurs", *path)))
    assert not np.array_equal(one["gas_spur_arc"][:3], two["gas_spur_arc"][:3])
    for table in (one, two):
        # The law holds at every foot of either draw: the spacing is the ridge's 10 λ_J there and the shape the constants'.
        jeans = SOUND_SPEED_HAND**2 / (G_HAND * 1e6 * np.interp(table["gas_spur_radius"], o.grid.R, sigma) * table["gas_spur_contrast"])
        assert np.allclose(table["gas_spur_spacing"], 10 * jeans, rtol=1e-12)
        assert np.all(table["gas_spur_pitch"] == 63.0) and np.all(table["gas_spur_length"] == 0.24)
        assert np.all(table["gas_spur_width"] == 0.06) and np.all(table["gas_spur_fall"] == 7.0)
        # Each chain's feet lie on the chain, in order along it.
        for chain in np.unique(table["gas_spur_chain"]):
            rows = np.flatnonzero(table["gas_spur_chain"] == chain)
            _, arc = ls.chain_geometry(gp.stars.pieces, float(chain))
            assert np.all(np.diff(table["gas_spur_arc"][rows]) > 0.0) and 0.0 <= table["gas_spur_arc"][rows[0]] and table["gas_spur_arc"][rows[-1]] < arc.sum()


def test_layer_off_lays_no_spur_and_the_gas_contrast_is_neutral(default_model):
    o = galaxy_run(default_model, "milky_way", layer=False)
    assert all(np.size(o.fields[n]) == 0 for n in sp.SPUR_FIELDS)
    assert np.all(np.asarray(o.fields["gas_density_contrast"]) == 1.0)
    assert compose.gas_pattern(o.fields, o.grid.R, constants(default_model)) is None
