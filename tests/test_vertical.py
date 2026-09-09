"""The thin/thick split, and the compensation the gate hides.

Row 9 passed from S3 to S17 for the wrong reason, and that was asserted here so that
nobody read the green as a working thick disc (debt #19). Since S18 it fails: the
derived star formation threshold holds the reservoir the pre-merger disc formed its
outer stars from, and the merger's radial kick - the mechanism §5d predicted would
spread the thick disc - is worth 0.3 kpc on row 5 and 0.015 on this row (D124). The
sweep §5d's gate asks for is asserted here: rows 9 and 11 are never inside together.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.registry import MergerEvent
from galaxy.run import run
from galaxy.stages.vertical import scale_height

R_SUN = 8.2


def out(model, **inputs):
    return run(model, inputs or None)


# The simple model's split is the merger; the advanced model's is the [α/Fe]
# valley, and at S9 there is no valley (debt #27), so its thick disc is empty.
MERGER_SPLIT = {"simple": True, "advanced": False}


def test_the_gate_and_what_it_reads(model):
    """Row 9: 0.051 in the simple model since S18 (0.135 until then, on the cancellation), recorded (D124)."""
    o = out(model)
    if MERGER_SPLIT[model.name]:
        assert o.fields["thick_thin_surface_density_ratio"] == pytest.approx(0.051, abs=0.004)  # 0.135 until S18; 0.147 until S17
        assert not 0.08 <= o.fields["thick_thin_surface_density_ratio"] <= 0.16
    else:
        assert o.fields["thick_thin_surface_density_ratio"] == 0.0  # recorded, not hidden (row 9)


def test_the_gate_is_still_a_cancellation_across_the_sweep(model):
    """Debt #19, judged as §5d says: by a sweep of the merger's gas_fraction, not a reading.

    Rows 9 and 11 must be inside together somewhere in the sweep for the gate to be met. They
    are not: shrinking the pre-merger episode lands row 11 and collapses row 9, because the
    thick disc is still too centrally concentrated (row 5), and the radial kick S18 built moves
    row 5 by 0.3 kpc where 0.8 is needed (D124).
    """
    if not MERGER_SPLIT[model.name]:
        pytest.skip("the advanced model has no thick disc to compensate with (debt #27)")
    o = out(model)
    assert o.fields["thick_disc_stellar_mass"] > 9.0e9      # row 11 fails high (9.6e9; 1.09e10 until S18)
    assert o.fields["thick_disc_scale_length"] < 1.8        # row 5 fails low (1.17)
    by = {g: out(model, mergers=(MergerEvent(3.8, 0.25, g, "probe"), MergerEvent(8.8, 0.02, 0.01, "probe"))).fields
          for g in (0.3, 0.4, 0.5, 0.6, 0.7)}
    together = [g for g, f in by.items() if 3.0e9 <= f["thick_disc_stellar_mass"] <= 9.0e9 and 0.08 <= f["thick_thin_surface_density_ratio"] <= 0.16]
    assert together == []
    assert 3.0e9 <= by[0.6]["thick_disc_stellar_mass"] <= 9.0e9 and by[0.6]["thick_thin_surface_density_ratio"] < 0.03  # row 11 in, row 9 gone
    assert 0.08 <= by[0.3]["thick_thin_surface_density_ratio"] <= 0.16 and by[0.3]["thick_disc_stellar_mass"] > 1.4e10   # row 9 in, row 11 far out
    assert all(f["thick_disc_scale_length"] < 1.8 for f in by.values())  # row 5 never lands on this lever


def test_the_thick_disc_carries_the_mergers_radial_kick(model):
    """S18 (D124): the stars present at the merger are moved by its radial spread, mass conserved.

    The spread is derived from the vertical kick read isotropically - 1.47 kpc at R0, 0.30 at 2 kpc -
    and the vertical stage sorts the moved stars, so the thick disc's scale length carries it: 1.17
    against 0.93 on the unspread history. A minor merger delivers the same gas and kicks nothing.
    """
    o = out(model)
    R = o.grid.R
    spread = o.fields["disc_radial_spread"]
    assert float(np.interp(R_SUN, R, spread[:, 0])) == pytest.approx(1.47, abs=0.02)
    assert float(np.interp(2.0, R, spread[:, 0])) == pytest.approx(0.30, abs=0.02)
    born_after = o.grid.t > o.fields["last_major_merger_time"]
    assert np.all(spread[:, born_after] == 0.0)
    if not MERGER_SPLIT[model.name]:
        return
    minor = out(model, mergers=(MergerEvent(3.8, 0.02, 0.5, "probe: same gas, no kick"), MergerEvent(8.8, 0.02, 0.01, "probe")))
    assert np.all(minor.fields["disc_radial_spread"] == 0.0)
    assert minor.fields["thick_disc_stellar_mass"] == 0.0  # a minor merger makes no thick disc by the simple model's own criterion
    assert o.fields["thick_disc_scale_length"] == pytest.approx(1.17, abs=0.02)
    # the same stars, unspread: reconstruct the pre-merger population from the birth history
    from galaxy.stages.disc import PC_PER_KPC
    from galaxy.stages.sfh import fit_scale_length
    from galaxy.stages.vertical import SCALE_LENGTH_FIT
    dt = o.grid.spec.t_max / o.grid.spec.n_t
    ret = float(model.constants["RETURN_FRACTION"].value)
    unspread = ((1.0 - ret) * PC_PER_KPC * o.fields["sfr_surface_density_history"] * dt)[:, ~born_after].sum(axis=1)
    assert fit_scale_length(unspread, R, *SCALE_LENGTH_FIT) == pytest.approx(0.93, abs=0.02)
    thick = o.fields["thick_disc_surface_density"]
    area = 2.0 * np.pi * R * o.grid["R"].width
    assert float((thick * area).sum()) == pytest.approx(float((unspread * area).sum()), rel=1e-9)  # mass conserved, ring by ring


def test_no_major_merger_means_no_thick_disc(model):
    """Simple: the split *names* the merger, so this is circular (debt #20). Advanced: it is a result."""
    free = out(model, mergers=())
    assert free.fields["thick_disc_stellar_mass"] == 0.0
    assert free.fields["thick_thin_surface_density_ratio"] == 0.0
    # Since S17 row 1 carries the spheroid too, and the spheroid is neither thin nor thick.
    disc = free.fields["stellar_mass_total"] - free.fields["bulge_stellar_mass"]
    assert free.fields["thin_disc_stellar_mass"] == pytest.approx(disc, rel=0.02)
    if not MERGER_SPLIT[model.name]:
        assert free.fields["alpha_sequence"] == "single"  # debt #9's answer, from a criterion that never named the merger


def test_the_thick_disc_is_hotter_than_the_thin_one(model):
    if not MERGER_SPLIT[model.name]:
        pytest.skip("no thick disc in the advanced model at S9 (debt #27)")
    o = out(model)
    # 40.4 against 20.4 since S18 (the thin disc at R0 is a little older with the derived threshold holding
    # its recent star formation lower); 40.7 against 20.1 until then. The factor is 1.98.
    assert o.fields["thick_disc_dispersion"] > 1.9 * o.fields["thin_disc_dispersion"]
    assert o.fields["thick_disc_scale_height"] > 3.0 * o.fields["thin_disc_scale_height"]


def test_scale_heights_are_arithmetic_from_the_dispersions(model):
    """Verdict A: h_z has no freedom once sigma_z and Sigma exist."""
    o = out(model)
    R = o.grid.R
    total = float(np.interp(R_SUN, R, o.fields["thin_disc_surface_density"]
                            + o.fields["thick_disc_surface_density"]
                            + o.fields["gas_surface_density"]))
    for disp, height in (("thin_disc_dispersion", "thin_disc_scale_height"),
                         ("thick_disc_dispersion", "thick_disc_scale_height")):
        if o.fields[disp] == 0.0:
            assert o.fields[height] == 0.0  # an empty population has no height, not a small one
            continue
        expected = float(scale_height(o.fields[disp], total, float(model.constants["G"].value))) * 1000.0
        assert o.fields[height] == pytest.approx(expected, rel=1e-9)


def test_rows_8_and_9_are_not_independent(model):
    """Row 8 is row 9 divided by the scale-height ratio, so they cannot be tuned apart."""
    o = out(model)
    f = o.fields
    if f["thick_disc_scale_height"] == 0.0:
        assert f["thick_thin_local_density_ratio"] == 0.0
        return
    assert f["thick_thin_local_density_ratio"] == pytest.approx(
        f["thick_thin_surface_density_ratio"] * f["thin_disc_scale_height"] / f["thick_disc_scale_height"]
    )


def test_the_populations_add_up_to_the_stellar_mass(model):
    o = out(model)
    f = o.fields
    total = f["thin_disc_stellar_mass"] + f["thick_disc_stellar_mass"]
    # Rows 10 + 11 are the disc; row 1 is rows 10 + 11 + 12 since S17, which is what its own
    # target means (AUDIT_RUN2 §5, D-5). The spheroid is sorted into neither population: it is
    # not in the star formation history the vertical stage splits.
    assert total == pytest.approx(f["stellar_mass_total"] - f["bulge_stellar_mass"], rel=0.02)


def test_scale_height_reads_the_registered_G_not_a_copy(prod):
    """AUDIT_RUN2.md D-9, fixed at S12: the sheet formula took G from a literal in vertical.py.

    A change to level0's G would have left every scale height on the old value, in the
    file that quotes rule A9. Both vertical stages now declare the read.
    """
    from galaxy.stages.vertical import VERTICAL
    from galaxy.stages.vertical_alpha import VERTICAL_ALPHA

    for st in (VERTICAL, VERTICAL_ALPHA):
        assert "G" in st.reads_constants
    G = float(prod[0].get("simple").constants["G"].value)
    assert scale_height(20.0, 50.0, G) == pytest.approx(20.0**2 / (2.0 * np.pi * G * 50.0 * 1000.0**2))
    assert scale_height(20.0, 50.0, 2.0 * G) == pytest.approx(0.5 * scale_height(20.0, 50.0, G))
