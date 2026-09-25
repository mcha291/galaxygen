"""The thin/thick split, and the compensation the gate hides.

Until D170 the simple model split on the merger, and its row 9 passed from S3 to S17
for the wrong reason (debt #19); that model and its sweep went with it. The one model
splits on the [α/Fe] valley (vertical_alpha), there is none (debt #27), and the thick
disc is empty: rows 5, 7, 8, 9 and 11 are recorded, not hidden. What stays here is the
merger's radial kick from the assembly stage (D124) and the sheet arithmetic.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.run import run
from galaxy.stages.vertical import scale_height

R_SUN = 8.2


def out(model, **inputs):
    return run(model, inputs or None)


# The split is the [α/Fe] valley (vertical_alpha; the merger-based split went with the
# simple model at D170), and there is no valley (debt #27), so the thick disc is empty.


def test_the_gate_and_what_it_reads(model):
    """Row 9: no valley, so the ratio is exactly zero, recorded (debt #27), not hidden."""
    o = out(model)
    assert o.fields["thick_thin_surface_density_ratio"] == 0.0  # recorded, not hidden (row 9)


def test_the_thick_disc_carries_the_mergers_radial_kick(model):
    """S18 (D124): the stars present at the merger are moved by its radial spread, mass conserved.

    The spread is derived from the vertical kick read isotropically - 1.09 kpc at R0, 0.22 at 2 kpc
    since S20 re-derived the kick's constant (1.47 and 0.30 at 120 km/s, D124, D128). The assembly
    stage publishes it whatever the vertical split does with it.
    """
    o = out(model)
    R = o.grid.R
    spread = o.fields["disc_radial_spread"]
    assert float(np.interp(R_SUN, R, spread[:, 0])) == pytest.approx(1.09, abs=0.02)  # 1.47 until S20
    assert float(np.interp(2.0, R, spread[:, 0])) == pytest.approx(0.22, abs=0.02)  # 0.30 until S20
    born_after = o.grid.t > o.fields["last_major_merger_time"]
    assert np.all(spread[:, born_after] == 0.0)


def test_no_major_merger_means_no_thick_disc(model):
    """The split never names the merger, so this is a result, not a circularity (debt #20)."""
    free = out(model, mergers=())
    assert free.fields["thick_disc_stellar_mass"] == 0.0
    assert free.fields["thick_thin_surface_density_ratio"] == 0.0
    # Since S17 row 1 carries the spheroid too, and the spheroid is neither thin nor thick.
    disc = free.fields["stellar_mass_total"] - free.fields["bulge_stellar_mass"]
    assert free.fields["thin_disc_stellar_mass"] == pytest.approx(disc, rel=0.02)
    assert free.fields["alpha_sequence"] == "single"  # debt #9's answer, from a criterion that never named the merger


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
    file that quotes rule A9. The vertical stage declares the read (one since D170).
    """
    from galaxy.stages.vertical_alpha import VERTICAL_ALPHA

    assert "G" in VERTICAL_ALPHA.reads_constants
    G = float(prod[0].get("basic").constants["G"].value)
    assert scale_height(20.0, 50.0, G) == pytest.approx(20.0**2 / (2.0 * np.pi * G * 50.0 * 1000.0**2))
    assert scale_height(20.0, 50.0, 2.0 * G) == pytest.approx(0.5 * scale_height(20.0, 50.0, G))
