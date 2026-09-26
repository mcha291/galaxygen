"""graph: acyclic per model, checkpoint order, hypotheses, provenance."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import INPUTS
from galaxy.specs import graph
from helpers import decl, impls, model, stage


def codes(problems):
    return sorted(p.code for p in problems)


def chk(m, *stages):
    return graph.check([m], impls(*stages), INPUTS)


# Execution orders. Kahn's algorithm runs in rounds with a (checkpoint, id) tie-break,
# so the vertical stage — which reads the chemistry's valley and so cannot start until
# the chemistry is done — lands a round after it (one model since D170).
# Since S18 the assembly stage reads the checkpoint-1 curve (the merger's radial kick becomes a
# displacement through its epicyclic frequency), so the disc runs before it; until then the
# tie-break put assembly second. Since the catalogue samples azimuth from the pattern's arms, the
# systems stage waits for pattern too, a round later than formation.
# Since S25 (BUILD_II Phase 1, D174) the bar reads the checkpoint-1 curve and the lambda_d scale
# length instead of sfh's resolved curve and fitted thin-disc length, so it is ready in assembly's
# round and the pattern a round later, both ahead of sfh: the pattern branch precedes star
# formation, which is what azimuthal star formation (Phase 2) needs.
# Since S27 (BUILD_II Phase 2) the azimuthal model maps the sfh slot to sfh_azimuthal, which also
# waits for the pattern (it reads the contrast); the pattern already ran a round ahead of sfh, so
# the order is basic's with the one id swapped.
# Since S29 (BUILD_II Phase 4) the population stage integrates what the locked mass is made of over
# the formation history and its [Fe/H], so it waits for the chemistry: it moves from the chemistry's
# round into the next (after light and vertical_alpha by the tie-break), and formation, which reads
# its mean stellar mass, a round later again, after systems. Until S29 the order ran "...,
# chemistry_dtd, population, light, vertical_alpha, formation, ism, systems, planets".
# Since S31 (BUILD_II Phase 7) the dust stage reads ism's dust and light's starlight, so it runs the
# round after ism's (ism shares its round with systems, formation and habitable_zone), beside planets
# and ahead of it by the (checkpoint, id) tie-break; until S31 the order ended "..., formation,
# habitable_zone, planets".
# Since S32 (BUILD_II Phase 8) the clouds stage reads ism's molecular gas and the pattern, so it runs
# in dust's round, between dust and planets by the tie-break.
# Since S33 (BUILD_II Phase 11) the clusters stage reads the cloud columns, so it runs the round after
# clouds', last in both orders; until S33 both ended "..., habitable_zone, dust, clouds, planets".
# Since S34 (BUILD_II Phase 5) the stellar halo reads the history (checkpoint 4, in supernovae's round,
# ahead of it by the tie-break), the survival of the bound clusters reads the halo's mass (the next
# round, ahead of population) and the globular clusters read the survival (the round after, ahead of
# systems). Until S34 the order ran "..., chemistry_dtd, supernovae, light, vertical_alpha, population,
# ism, systems, ...".
# Since S35 (BUILD_II Phase 9) the nebular stage reads the cluster and cloud columns, so it runs the round
# after clusters', last in both orders; until S35 both ended "..., planets, clusters".
# Since S36 (BUILD_II Phase 10) the catalogue reads ism's midplane density (a star's wind bubble expands into
# it), so systems runs the round after ism's, behind clouds by the tie-break, and the planets after clusters;
# the bubbles stage reads the HII regions, so it runs last. Until S36 both read "..., ism, globular_clusters,
# systems, formation, habitable_zone, dust, clouds, planets, clusters, nebular". No value moves with the order.
ORDER = {
    "basic": (
        "halo", "disc", "nucleus", "assembly", "bar", "pattern", "sfh", "chemistry_dtd", "stellar_halo",
        "supernovae", "light", "vertical_alpha", "cluster_survival", "population", "ism", "globular_clusters",
        "formation", "habitable_zone", "dust", "clouds", "systems", "clusters", "planets", "nebular", "bubbles",
    ),
    "azimuthal": (
        "halo", "disc", "nucleus", "assembly", "bar", "pattern", "sfh_azimuthal", "chemistry_dtd", "stellar_halo",
        "supernovae", "light", "vertical_alpha", "cluster_survival", "population", "ism", "globular_clusters",
        "formation", "habitable_zone", "dust", "clouds", "systems", "clusters", "planets", "nebular", "bubbles",
    ),
}
# The seeded fields per model. The azimuthal model adds exactly one: its star-formation modulation
# reads the seeded contrast, and every field sfh_azimuthal shares with sfh stays derived because
# sfh computes it, in sfh's own view (Stage.extends, S27) -- so nothing downstream turns seeded.
SEEDED_BASIC = {
    "black_hole_mass",
    # S36 (BUILD_II Phase 10): the bubbles stage reads the seeded cluster and HII-region columns and draws the
    # remnant census on systems_seed, so all it publishes is seeded (D55), the hot phase's radial field too;
    # the catalogue's new column is seeded with the catalogue. ism's midplane density stays derived.
    "bubble_radius", "bubble_shell_velocity", "bubble_shell_density", "bubble_shell_thickness", "bubble_interior_pressure",
    "bubble_interior_temperature", "bubble_shell_emissivity", "bubble_mechanical_luminosity", "bubble_phase", "bubble_stalled",
    "remnant_radius", "remnant_azimuth", "remnant_height", "remnant_size", "remnant_age", "remnant_shell_velocity",
    "remnant_ambient_density", "remnant_shell_density", "remnant_shell_thickness", "remnant_shell_emissivity",
    "remnant_phase", "remnant_kind", "hot_phase_porosity", "remnant_count_total", "star_bubble_radius",
    # S35 (BUILD_II Phase 9): the nebular stage reads the seeded cluster and cloud columns, so everything it
    # publishes is seeded (D55: a stage has one provenance), the radial Halpha fields and the scale height too.
    "halpha_surface_brightness_hii", "halpha_surface_brightness_dig", "halpha_surface_brightness_nebular", "dig_scale_height",
    "hii_stromgren_radius", "hii_electron_density", "hii_temperature", "hii_ionization_parameter", "hii_clumping",
    "hii_halpha_luminosity", "hii_halpha_emissivity", "hii_balmer_decrement", "hii_oxygen_abundance",
    "hii_nitrogen_abundance", "hii_sulphur_abundance", "hii_density_bounded",
    "halpha_luminosity_nebular", "dig_halpha_fraction", "halpha_sfr_ratio", "hii_luminosity_function_slope",
    # S34 (BUILD_II Phase 5): the globular cluster system, drawn on world_seed; the survival fraction and the
    # metal-poor share are a separate stage and stay derived (D55), as the stellar halo does.
    "gc_system_mass", "gc_count_estimate",
    # The molecular-cloud census (S32): every column and scalar of a stage that reads systems_seed.
    "cloud_radius", "cloud_azimuth", "cloud_height", "cloud_mass", "cloud_size", "cloud_velocity_dispersion",
    "cloud_mach_number", "cloud_density_pdf_width", "cloud_age", "cloud_state", "cloud_source_offset",
    "cloud_source_angle", "cloud_density_gradient", "cloud_gradient_angle", "cloud_metallicity", "cloud_alpha",
    "cloud_count_total", "cloud_mass_total", "cloud_forcing_parameter", "cloud_lifetime",
    # S33: which cluster a cloud holds, and the cluster census (a stage that reads systems_seed).
    "cloud_cluster_index",
    "cluster_radius", "cluster_azimuth", "cluster_height", "cluster_mass", "cluster_half_mass_radius", "cluster_age",
    "cluster_bound", "cluster_metallicity", "cluster_ionizing_photons", "cluster_wind_luminosity",
    "bound_cluster_mass_total", "cluster_formation_efficiency",
    "bar_corotation_radius", "bar_pattern_speed", "pitch_angle", "arm_multiplicity",
    "arm_contrast", "bar_contrast", "pattern_density_contrast",
    "star_radius", "star_azimuth", "star_height", "star_age", "star_birth_radius",
    "star_metallicity", "star_alpha", "star_mass", "star_luminosity", "star_temperature", "star_population", "catalogue_size",
    # S28 (BUILD_II Phase 3): the rest of the table's point and what the massive stars do with it.
    "star_magnitude_v", "star_ionizing_photons", "star_wind_luminosity", "star_wolf_rayet",
    # S29 (BUILD_II Phase 4): what a dead star is, looked up from the same columns.
    "star_remnant", "star_remnant_mass",
    "planet_semi_major_axis", "planet_mass", "planet_radius", "planet_insolation",
    "planet_orbital_period", "planet_rotation_period", "planet_obliquity",
    "planet_volatile_fraction", "planet_atmosphere", "star_planet_count",
    "planet_count_sample", "mean_planets_per_star", "giant_fraction_sample",
}
SEEDED = {"basic": SEEDED_BASIC, "azimuthal": SEEDED_BASIC | {"sfr_modulation"}}


def test_production_graphs_hold(prod):
    models, impls_, table = prod
    assert graph.check(models, impls_, table) == []
    for m in models:
        g = graph.analyse(m, impls_, table)
        assert g.ok
        assert tuple(s.id for s in g.order) == ORDER[m.name]
        # The nucleus is the first seeded stage since S17; the pattern was until then.
        # Provenance is derived per stage, so a stage that reads a seed or a seeded field
        # publishes seeded fields and every other field is derived (D55) — which is why the
        # spheroid's own scalars are the halo's and only M_• is here. S8's split keeps the
        # occurrence fields on the derived side.
        seeded = {n for n, p in g.provenance.items() if p == "seeded"}
        assert seeded == SEEDED[m.name], sorted(seeded ^ SEEDED[m.name])
        assert g.provenance["giant_occurrence"] == "derived", (
            "the occurrence fields are a function of the inputs; the split at checkpoint 6 is what "
            "keeps them so (rule A10)"
        )
        # S1 binds the four checkpoint-1 controls and no others; graph.py checks each
        # against GALAXY_PLAN.md §3's hypothesis and none of them disagrees. world_seed
        # joined them at S17: nothing read it until the nucleus stage did (debt #39's
        # inert dimension), and it binds at checkpoint 1, which is its own hypothesis.
        bound = {n: c for n, c in g.input_checkpoint.items() if c is not None}
        assert bound == {
            "halo_mass": 1, "disc_spin": 1, "halo_assembly_z": 1, "baryon_retention": 1,
            "world_seed": 1,
            # S25 (D174): the pattern is checkpoint 3 and star formation 4, so the three
            # star-formation controls and pattern_seed moved. S26 (D175) removed the two
            # experimental amplitude inputs: seven controls again.
            "infall_timescale": 4, "inside_out_index": 4, "migration_efficiency": 4,
            "mergers": 2,
            "pattern_seed": 3, "systems_seed": 5, "planets_seed": 6,
        }
    assert "graph" in graph.report(models, impls_, table)


def test_cycle_detected_and_refused():
    a = stage("a", ("fa",), requires=("fb",))
    b = stage("b", ("fb",), requires=("fa",))
    m = model("m", a, b)
    assert "cycle" in codes(chk(m, a, b))
    with pytest.raises(graph.GraphError):
        graph.build(m, impls(a, b), INPUTS)


def test_order_is_topological_and_deterministic():
    a = stage("a", ("fa",))
    b = stage("b", ("fb",), requires=("fa",))
    c = stage("c", ("fc",), requires=("fb",))
    g = graph.build(model("m", c, a, b), impls(a, b, c), INPUTS)
    assert tuple(s.id for s in g.order) == ("a", "b", "c")
    x = stage("x", ("fx",), checkpoint=2)
    y = stage("y", ("fy",), checkpoint=1)
    g = graph.build(model("m", x, y), impls(x, y), INPUTS)
    assert tuple(s.id for s in g.order) == ("y", "x")
    assert g.producer == {"fx": "x", "fy": "y"}


def test_missing_producer_and_duplicate_field():
    b = stage("b", ("fb",), requires=("fa",))
    assert "missing-producer" in codes(chk(model("m", b), b))
    with pytest.raises(graph.GraphError):
        graph.build(model("m", b), impls(b), INPUTS)
    p1 = stage("p1", ("f",))
    p2 = stage("p2", ("f",))
    assert "duplicate-field" in codes(chk(model("m", p1, p2), p1, p2))


def test_unknown_implementation_and_slot_mismatch():
    from galaxy.core.registry import Model

    m = Model("m", "about", (("halo", "nope"),), {})
    assert "unknown-implementation" in codes(graph.check([m], {}, INPUTS))
    s = stage("impl", slot="chem")
    m = Model("m", "about", (("halo", "impl"),), {})
    assert "slot-mismatch" in codes(graph.check([m], impls(s), INPUTS))


def test_checkpoint_order():
    p = stage("p", ("f",), checkpoint=2)
    early = stage("c", ("g",), requires=("f",), checkpoint=1)
    assert "checkpoint-order" in codes(chk(model("m", p, early), p, early))
    same = stage("c", ("g",), requires=("f",), checkpoint=2)
    assert chk(model("m", p, same), p, same) == []
    opt = stage("c", ("g",), requires_optional=(decl("f", optional=True).name,), checkpoint=1)
    po = stage("p", (decl("f", optional=True),), checkpoint=2)
    assert "checkpoint-order" in codes(chk(model("m", po, opt), po, opt))


def test_hypothesis_checked_against_derived_checkpoint():
    late = stage("s", ("f",), reads_inputs=("halo_mass",), checkpoint=2)
    probs = chk(model("m", late), late)
    assert codes(probs) == ["hypothesis"]
    assert "checkpoint 1" in probs[0].detail and "checkpoint 2" in probs[0].detail
    ok = stage("s", ("f",), reads_inputs=("halo_mass",), checkpoint=1)
    g = graph.analyse(model("m", ok), impls(ok), INPUTS)
    assert g.ok and g.input_checkpoint["halo_mass"] == 1
    assert "halo_mass" not in g.unbound_inputs and "disc_spin" in g.unbound_inputs
    # pattern_seed's hypothesis is checkpoint 3 since S25 (4 until then, D174).
    seeded = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("pattern_seed",), checkpoint=3)
    assert chk(model("m", seeded), seeded) == []
    seeded4 = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("pattern_seed",), checkpoint=4)
    assert codes(chk(model("m", seeded4), seeded4)) == ["hypothesis"]


def test_provenance_is_computed_and_compared():
    s = stage("s", ("f",), reads_seeds=("world_seed",))  # declared derived, computed seeded
    assert codes(chk(model("m", s), s)) == ["provenance"]
    s = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("world_seed",))
    assert chk(model("m", s), s) == []
    d = stage("d", ("g",), requires=("f",))  # downstream of seeded, declared derived
    assert codes(chk(model("m", s, d), s, d)) == ["provenance"]
    d = stage("d", (decl("g", provenance="seeded"),), requires=("f",))
    assert chk(model("m", s, d), s, d) == []
    s_opt = stage("s", (decl("f", provenance="seeded", optional=True),), reads_seeds=("world_seed",))
    d_opt = stage("d", ("g",), requires_optional=("f",))
    assert codes(chk(model("m", s_opt, d_opt), s_opt, d_opt)) == ["provenance"]
    claims = stage("s", (decl("f", provenance="seeded"),))  # declared seeded, reads no seed
    assert codes(chk(model("m", claims), claims)) == ["provenance"]


def test_an_extension_republishes_its_base_at_the_bases_provenance():
    """S27: a stage that extends another publishes the base's fields at the base's provenance.

    The base computes them in its own restricted view (``Extension``), so the extension's extra
    seeded read reaches only its own field; a downstream reader of the shared field stays derived.
    """
    from galaxy.core.stage import extend

    seeded = stage("s", (decl("f", provenance="seeded"),), reads_seeds=("world_seed",))
    other = stage("o", ("g",))
    base = stage("b", ("h",), slot="x", requires=("g",))
    ext = extend(base, id="e", about="an extension", own=lambda ctx, shared: {"k": np.ones(ctx.grid.shape(("R",)))},
                 requires=("f",), publishes=(decl("k", provenance="seeded"),))
    down = stage("d", ("j",), requires=("h",))
    m = model("m", seeded, other, ext, down)
    g = graph.analyse(m, impls(seeded, other, ext, down), INPUTS)
    assert g.ok, g.problems
    assert g.provenance["h"] == "derived" and g.provenance["j"] == "derived" and g.provenance["k"] == "seeded"
    # Without the extension the same reads make every field of the stage seeded (D55).
    flat = stage("e", ("h", decl("k", provenance="seeded")), slot="x", requires=("g", "f"))
    assert codes(chk(model("m", seeded, other, flat, down), seeded, other, flat, down)) == ["provenance", "provenance"]


def test_unknown_input():
    s = stage("s", ("f",), reads_inputs=("nope",))
    assert "unknown-input" in codes(chk(model("m", s), s))
    r = stage("r", ("f",), reads_inputs=("disc_spin",))
    assert "unknown-input" in codes(chk(model("m", r, inputs=("halo_mass",)), r))


def test_needed_for_is_the_closure_above_the_wanted_fields():
    a = stage("a", ("fa",))
    b = stage("b", ("fb",), requires=("fa",))
    c = stage("c", ("fc",), requires=("fb",))
    side = stage("side", ("fs",))
    opt = stage("opt", ("fo",), requires_optional=("fs",))
    m = model("m", a, b, c, side, opt)
    g = graph.analyse(m, impls(a, b, c, side, opt), INPUTS)
    assert [s.id for s in g.needed_for(["fc"])] == ["a", "b", "c"]
    assert [s.id for s in g.needed_for(["fb"])] == ["a", "b"]
    assert [s.id for s in g.needed_for(["fa", "fs"])] == ["a", "side"]
    assert g.needed_for([]) == () and g.needed_for(["not_a_field"]) == ()
    # An optional requirement this model does publish is a real dependency.
    assert [s.id for s in g.needed_for(["fo"])] == ["side", "opt"]
    # ... and where nothing publishes it, the closure is just the reader.
    without = model("without", opt)
    assert [s.id for s in graph.analyse(without, impls(opt), INPUTS).needed_for(["fo"])] == ["opt"]
