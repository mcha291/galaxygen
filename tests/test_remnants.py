"""Stellar remnants and planetary nebulae (BUILD_II Phase 4, S29): the rulings, the partition, the integral."""

from __future__ import annotations

import numpy as np
import pytest

from galaxy.core.grids import GridSpec
from galaxy.models.level0 import LEVEL0
from galaxy.stages import remnants as rm
from galaxy.stages.photometry import imf_weights, isochrones, lookup

COARSE = GridSpec(n_R=120, n_t=400, n_z=6)
RETURN = LEVEL0["RETURN_FRACTION"].value
WANTED = (
    "star_mass", "star_age", "star_metallicity", "star_luminosity", "star_remnant", "star_remnant_mass",
    "remnant_mass_fraction", "planetary_nebula_count", "stellar_mass_total", "stars_formed_history",
    "feh_history", "bulge_stellar_mass", "bulge_scale_radius",
)


@pytest.fixture(scope="module")
def runs():
    """Both models on the coarse grid, the catalogue and the population scalars."""
    from galaxy.core.registry import production
    from galaxy.run import run

    models, impls, table = production()
    return {m.name: run(m, None, COARSE, impls=impls, table=table, only=WANTED) for m in models}


def _budget(o, bulge: bool = True) -> rm.MassBudget:
    from galaxy.stages.light import bulge_abundance

    f, R, t = o.fields, o.grid.R, o.grid.t
    ret = RETURN
    locked = np.asarray(f["stars_formed_history"], dtype=float)
    feh_bulge = bulge_abundance(R, locked / (1.0 - ret), f["feh_history"], float(f["bulge_scale_radius"]))
    return rm.budget(locked, f["feh_history"], R, t, float(o.grid.spec.t_max), ret,
                     float(f["bulge_stellar_mass"]) if bulge else 0.0, float(t[-1] - t[0]), feh_bulge)


# --- ruling (a): the IFMR and the class boundaries, as read ----------------------------------------


def test_the_ifmr_is_cummings_parsec_fit_as_read():
    """Cummings et al. 2018, §VI.2, eqs. 1-3 (PARSEC-based), read twice at S29 and entered as printed.

    The three segments were fitted separately and do not quite meet: at 2.80 M☉ eq. 2 starts
    0.0036 M☉ below where eq. 1 ends, at 3.65 eq. 3 starts 0.0009 below eq. 2 — the fit's own
    joins, kept rather than smoothed, a tenth of the relation's 0.06 M☉ scatter and less."""
    assert rm.IFMR_PARSEC == ((0.87, 2.80, 0.0873, 0.476), (2.80, 3.65, 0.181, 0.210), (3.65, 8.20, 0.0835, 0.565))
    assert rm.IFMR_MIST == ((0.83, 2.85, 0.080, 0.489), (2.85, 3.60, 0.187, 0.184), (3.60, 7.20, 0.107, 0.471))
    for segments in (rm.IFMR_PARSEC, rm.IFMR_MIST):
        assert all(a[1] == b[0] for a, b in zip(segments[:-1], segments[1:]))
    m = np.array([1.0, 2.8 - 1e-9, 2.8, 3.65 - 1e-9, 3.65, 6.0, 8.2, 8.5, 0.79])
    expect = [0.0873 + 0.476, 0.0873 * 2.8 + 0.476, 0.181 * 2.8 + 0.210, 0.181 * 3.65 + 0.210, 0.0835 * 3.65 + 0.565,
              0.0835 * 6.0 + 0.565, 0.0835 * 8.2 + 0.565, 0.0835 * 8.5 + 0.565, 0.0873 * 0.79 + 0.476]
    assert rm.white_dwarf_mass(m) == pytest.approx(expect, abs=1e-8)
    w = rm.white_dwarf_mass(m)
    assert w[2] - w[1] == pytest.approx(-0.00364, abs=1e-5) and w[4] - w[3] == pytest.approx(-0.000875, abs=1e-6)


def test_the_named_alternative_the_mist_based_fit():
    """The same paper's MIST-based fit, compared and not averaged (B12). Per star at S29: PARSEC −
    MIST = −0.0057 M☉ at 1 M☉, +0.0068 at 3.2 and −0.047 at 6. Over an old solar population's white
    dwarfs (10^10 yr) the PARSEC relation's mass is 0.99315 of MIST's: the choice moves the white
    dwarfs' mass by seven tenths of a per cent, the size of the ruling stated rather than hidden."""
    diff = rm.white_dwarf_mass(np.array([1.0, 3.2, 6.0])) - rm.white_dwarf_mass(np.array([1.0, 3.2, 6.0]), "mist")
    assert diff == pytest.approx([-0.0057, 0.0068, -0.047], abs=1e-6)
    tab = isochrones()
    solar = int(np.abs(tab.mhs).argmin())
    top = isochrones().track(int(np.argmin(np.abs(tab.log_ages - 10.0))), solar)[0][-1]
    m = np.geomspace(top, rm.WHITE_DWARF_MAX_INITIAL_MASS, 20001)
    phi = imf_weights(m)
    ratio = np.trapezoid(phi * rm.white_dwarf_mass(m), m) / np.trapezoid(phi * rm.white_dwarf_mass(m, "mist"), m)
    print(f"old solar population's white dwarfs: PARSEC / MIST = {ratio:.5f}")
    assert ratio == pytest.approx(0.99315, abs=5e-5)


def test_the_class_boundaries_and_the_masses_are_the_sources():
    """Smartt 2009 m_min 8.5 M☉; Heger et al. 2003 fallback black holes above ~25 M☉; Özel & Freire 2016's
    double neutron stars 1.33 M☉; Özel et al. 2010's Galactic black holes 7.8 M☉; Badenes et al. 27 kyr."""
    assert (rm.WHITE_DWARF_MAX_INITIAL_MASS, rm.BLACK_HOLE_MIN_INITIAL_MASS) == (8.5, 25.0)
    assert (rm.NEUTRON_STAR_MASS, rm.BLACK_HOLE_MASS, rm.PLANETARY_NEBULA_DURATION) == (1.33, 7.8, 27.0e3)
    m = np.array([0.8, 8.49, 8.5, 24.99, 25.0, 100.0])
    assert rm.fate(m).tolist() == [rm.WHITE_DWARF, rm.WHITE_DWARF, rm.NEUTRON_STAR, rm.NEUTRON_STAR, rm.BLACK_HOLE, rm.BLACK_HOLE]
    assert rm.remnant_mass(m)[2:].tolist() == [1.33, 1.33, 7.8, 7.8]
    assert rm.REMNANT_CATEGORIES[rm.NONE] == "none" and len(rm.REMNANT_CATEGORIES) == 5


# --- per star: dead is the table's mark, the death age the table's own reading ----------------


def test_the_death_age_is_the_lookups_own_reading():
    """A star is NaN in L exactly when its (clamped) age is past its death age: 200 000 random stars
    across the table's masses, ages and metallicities, not one disagreement (S29)."""
    rng = np.random.default_rng(29)
    n = 200_000
    m = np.exp(rng.uniform(np.log(0.7), np.log(80.0), n))
    age = np.exp(rng.uniform(np.log(1e-3), np.log(14.0), n))
    feh = rng.uniform(-2.6, 0.6, n)
    L, _ = lookup(m, age, feh)
    tab = isochrones()
    clamped = np.clip(age, 10.0 ** tab.log_ages[0] / 1e9, 10.0 ** tab.log_ages[-1] / 1e9)
    death = rm.death_age(m, feh)
    predicted_dead = np.isnan(death) | (death < clamped)
    disagree = int((predicted_dead != np.isnan(L)).sum())
    print(f"dead {int(np.isnan(L).sum())} of {n}; disagreements {disagree}")
    assert disagree == 0


def test_a_planetary_nebula_is_a_white_dwarf_progenitor_less_than_27_kyr_dead():
    tab = isochrones()
    feh = np.zeros(6)
    death = float(rm.death_age(np.array([1.1]), np.array([0.0]))[0])
    ages = death + np.array([-1e-3, 1e-5, 2.6e-5, 2.8e-5, 1.0, 5.0]) * np.array([1, 1, 1, 1, 1, 1])
    m = np.full(6, 1.1)
    L, _ = lookup(m, ages, feh)
    kind, mass = rm.classify(m, ages, feh, L)
    names = [rm.REMNANT_CATEGORIES[k] for k in kind]
    print(f"a 1.1 Msun solar star dies at {death:.4f} Gyr: {names}")
    assert np.isfinite(L[0]) and np.all(np.isnan(L[1:]))
    assert names == ["none", "planetary_nebula", "planetary_nebula", "white_dwarf", "white_dwarf", "white_dwarf"]
    assert np.isnan(mass[0]) and mass[1:] == pytest.approx(0.0873 * 1.1 + 0.476)
    assert 10.0 ** tab.log_ages[0] / 1e9 < death < 10.0 ** tab.log_ages[-1] / 1e9
    # A core-collapse progenitor just dead is a neutron star, never a nebula.
    d12 = float(rm.death_age(np.array([12.0]), np.array([0.0]))[0])
    L12, _ = lookup(np.array([12.0]), np.array([d12 + 1e-6]), np.zeros(1))
    assert rm.REMNANT_CATEGORIES[rm.classify(np.array([12.0]), np.array([d12 + 1e-6]), np.zeros(1), L12)[0][0]] == "neutron_star"


# --- the catalogue ------------------------------------------------------------------------------


def test_the_classes_partition_the_dead_exactly(runs):
    """No star is two things, none is `none` while dead, none is a remnant while alive; each class is
    its initial mass's; the columns are the functions of the star's own columns (D60), never drawn."""
    for name, o in runs.items():
        c = {k: np.asarray(o.fields[k]) for k in WANTED[:6]}
        dead = np.isnan(c["star_luminosity"])
        kind, m = c["star_remnant"], c["star_mass"]
        assert np.array_equal(kind != rm.NONE, dead)
        assert set(np.unique(kind).tolist()) <= set(range(len(rm.REMNANT_CATEGORIES)))
        wd_like = np.isin(kind, (rm.WHITE_DWARF, rm.PLANETARY_NEBULA))
        assert np.all(m[wd_like] < 8.5)
        assert np.all((m[kind == rm.NEUTRON_STAR] >= 8.5) & (m[kind == rm.NEUTRON_STAR] < 25.0))
        assert np.all(m[kind == rm.BLACK_HOLE] >= 25.0)
        assert np.array_equal(np.isnan(c["star_remnant_mass"]), ~dead)
        np.testing.assert_array_equal(c["star_remnant_mass"][dead], rm.remnant_mass(m[dead]))
        again = rm.classify(m, c["star_age"], c["star_metallicity"], c["star_luminosity"])
        np.testing.assert_array_equal(again[0], kind)
        np.testing.assert_array_equal(again[1], c["star_remnant_mass"])
        counts = dict(zip(rm.REMNANT_CATEGORIES, np.bincount(kind, minlength=5).tolist()))
        print(f"{name}: {c['star_mass'].size} stars, dead {int(dead.sum())}: {counts}")


def test_a_region_carries_the_whole_discs_remnants(runs):
    """Per-region determinism of the new columns (D60): three cells asked for alone give, star for
    star, what the whole-disc sweep gives those cells — in both models."""
    from galaxy.stages.systems import materialise

    for name, o in runs.items():
        R, t = o.grid.R, o.grid.t
        kw = dict(migration=float(o.inputs["migration_efficiency"]))
        whole = materialise(o.fields, R, t, 0, 200_000, None, **kw)
        region = materialise(o.fields, R, t, 0, 200_000, [17, 400, 900], **kw)
        start, at = {}, 0
        for cell, count in whole.counts:
            start[cell] = (at, count)
            at += count
        row = 0
        for cell, count in region.counts:
            s, n = start[cell]
            assert n == count
            for column in ("star_remnant", "star_remnant_mass", "star_luminosity"):
                assert np.array_equal(region[column][row:row + count], whole[column][s:s + n], equal_nan=True), (name, cell, column)
            row += count
        assert row == region.size > 0
        print(f"{name}: {region.size} stars in the region, {int((region['star_remnant'] != 0).sum())} dead")


# --- the population integral: what the locked mass is made of -----------------------------------


def test_every_isochrone_closes_its_own_budget():
    """Per isochrone, per unit mass formed: the living at initial mass plus the dead's initial mass is
    the whole IMF (checked by a quadrature of the test's own, B3); the remnants weigh less than the
    stars they came from; the living weigh no more at present mass than at birth."""
    tab = isochrones()
    table = rm.population_mass()
    k = {q: i for i, q in enumerate(rm.QUANTITIES)}
    m = np.geomspace(0.08, 150.0, 400_001)
    phi = imf_weights(m)
    formed = np.trapezoid(phi * m, m)
    worst = 0.0
    for (a, z), (mass, _, _) in tab.tracks.items():
        dead = np.trapezoid(np.where(m > mass[-1], phi * m, 0.0), m) / formed
        worst = max(worst, abs(table[a, z, k["living_initial"]] + dead - 1.0))
        remnant = table[a, z, k["white_dwarf"]] + table[a, z, k["neutron_star"]] + table[a, z, k["black_hole"]]
        assert remnant < dead + 1e-12
        assert table[a, z, k["living"]] <= table[a, z, k["living_initial"]] * (1.0 + 1e-9)
    print(f"worst |living + dead - 1| {worst:.2e}")
    assert worst < 2e-4  # the test's own grid straddles each isochrone's end; the module's does not
    solar, old = int(np.abs(tab.mhs).argmin()), tab.log_ages.size - 1
    locked = table[old, solar, k["living"]] + table[old, solar, [k["white_dwarf"], k["neutron_star"], k["black_hole"]]].sum()
    print(f"12.6 Gyr solar population: stars and remnants {locked:.4f} of the mass formed")
    assert 1.0 - locked == pytest.approx(0.4276, abs=5e-4)  # its return fraction: S29, 0.42763


def test_the_locked_mass_is_what_the_model_counts_and_what_it_is_made_of(runs):
    """The integral's mass formed, times (1 − R), is stellar_mass_total to rounding: it is the same
    mass. What the isochrones say that mass is — living stars at present mass plus remnants — is
    0.83615 of it (coarse grid, S29; 0.83610 on the default grid), both models: the instantaneous
    return of 0.30 against the 0.41470 a Kroupa population along the PARSEC tracks has returned by
    today, over this history. Recorded, not tuned: the gap is the return fraction's (a candidate debt),
    and remnant_mass_fraction is a share of what the isochrones say is there."""
    for name, o in runs.items():
        b = _budget(o)
        ratio = (b.living + b.remnant) / b.locked
        print(f"{name}: locked {b.locked:.6e} vs stellar_mass_total {float(o.fields['stellar_mass_total']):.6e}; "
              f"living {b.living:.4e} WD {b.white_dwarf:.4e} NS {b.neutron_star:.4e} BH {b.black_hole:.4e}; "
              f"(living + remnant) / locked {ratio:.6f}; effective return {1 - (b.living + b.remnant) / b.formed:.5f}")
        assert b.locked == pytest.approx(float(o.fields["stellar_mass_total"]), rel=1e-12)
        assert float(o.fields["remnant_mass_fraction"]) == b.remnant_fraction
        assert ratio == pytest.approx(RECONCILED, abs=2e-4)
        assert 1.0 - (b.living + b.remnant) / b.formed == pytest.approx(0.4147, abs=2e-4)


RECONCILED = 0.83615  # S29, coarse grid: (living + remnant) / stellar_mass_total


def test_the_published_scalars(runs):
    """remnant_mass_fraction and planetary_nebula_count at the defaults on the coarse grid, both models
    (S29): 0.214597 and 14 731.4. On the default grid 0.214686 and 14 732.2, the grid moving each by
    under 5 × 10⁻⁴ of itself."""
    for name, o in runs.items():
        fraction, pne = float(o.fields["remnant_mass_fraction"]), float(o.fields["planetary_nebula_count"])
        print(f"{name}: remnant_mass_fraction {fraction:.6f}, planetary_nebula_count {pne:.1f}")
        assert fraction == pytest.approx(0.21460, abs=5e-5)
        assert pne == pytest.approx(14731.4, abs=5.0)


def test_the_sample_agrees_with_the_integral(runs):
    """B3: the catalogue counts what the integral computes. 200 000 stars, their remnant mass over
    living-at-present-mass plus remnant, against the disc's integral (the catalogue has no bulge);
    ages and [Fe/H] reach the two by different routes (the arrival law and the birth radius against
    the history at today's radius). Measured at S29: agreement well inside three standard errors."""
    from galaxy.stages.photometry import lookup_columns
    from galaxy.stages.systems import materialise

    for name, o in runs.items():
        integral = _budget(o, bulge=False).remnant_fraction
        cat = materialise(o.fields, o.grid.R, o.grid.t, 7, 200_000, None, migration=float(o.inputs["migration_efficiency"]))
        c = {k: np.asarray(v) for k, v in cat.items()}
        now = lookup_columns(c["star_mass"], c["star_age"], c["star_metallicity"], ("mass_now",))["mass_now"]
        alive = np.isfinite(c["star_luminosity"])
        x = np.where(alive, 0.0, c["star_remnant_mass"])
        y = np.where(alive, now, x)
        share = x.sum() / y.sum()
        error = np.sqrt(np.sum((x - share * y) ** 2)) / y.sum()
        print(f"{name}: sample {share:.5f} +- {error:.5f} against the integral's {integral:.5f}")
        assert abs(share - integral) < 3.0 * error


def test_the_solar_neighbourhood_for_audit_iii(runs):
    """Not a row (D100): the one read target with an uncertainty is local. McKee, Parravano &
    Hollenbach 2015, Table 1: white dwarfs 4.9 ± 0.8 M☉/pc² of 33.4 ± 3 in stars and remnants at the
    Sun (arXiv:1509.05334, read at S29). The model's counterparts at R₀, printed and pinned so the
    audit reads them: Σ_WD and the white dwarfs' share of stars plus remnants there."""
    from galaxy.stages.remnants import _per_formed

    o = runs["basic"]
    R, t = o.grid.R, o.grid.t
    at = int(np.argmin(np.abs(R - LEVEL0["R_SUN"].value)))
    dt = float(o.grid.spec.t_max) / t.size
    youngest = float(o.grid.spec.t_max) - (t + 0.5 * dt)
    formed = np.asarray(o.fields["stars_formed_history"], dtype=float)[at] / (1.0 - RETURN)
    per = _per_formed(youngest, youngest + dt, np.asarray(o.fields["feh_history"], dtype=float)[at])
    k = {q: i for i, q in enumerate(rm.QUANTITIES)}
    local = formed @ per
    white = local[k["white_dwarf"]]
    total = local[k["living"]] + local[[k["white_dwarf"], k["neutron_star"], k["black_hole"]]].sum()
    print(f"R = {R[at]:.2f} kpc: Sigma_WD {white:.3f} Msun/pc2 of {total:.3f}, share {white / total:.4f}")
    assert white == pytest.approx(4.757, abs=5e-3)
    assert white / total == pytest.approx(LOCAL_WD_SHARE, abs=5e-4)


# S29, coarse grid, R = 8.12 kpc: Σ_WD 4.757 M☉/pc² of 32.068 in stars and remnants. Seen after the ruling
# that no row is added here, and so left to Audit III rather than made a row by this session (D113).
LOCAL_WD_SHARE = 0.1483
