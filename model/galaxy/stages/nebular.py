"""Nebular emission: the HII region around every young cluster, the diffuse ionized gas, and the galaxy's
Hα as a redistribution of its ionizing photons (checkpoint 5, S35, BUILD_II Phase 9).

**What this stage is, and is not.** RENDER_PHYSICS.md §2 asks for the ionized-gas component as a set of
shape parameters per emitter — Q(H⁰), n_e, T_e, the ionization parameter, O/H, S/H, N/H — and §4 for its
emissivity **per unit volume** at region scale, so a shell limb-brightens when a renderer integrates along a
ray. This stage publishes exactly that for every cluster's HII region, as columns of the cluster object
(§5b: the region is the cluster's), plus the recombination lines the parameters determine in closed form
(Case B, Storey & Hummer 1995). **The collisionally excited lines ([O III] 5007, [N II] 6583, [S II]
6716 and 6731)** need the ionization fractions a photoionization model gives: S35 ruled that a tabulated
grid of the isochrone kind (Byler et al. 2017 as shipped in FSPS: 11 log Z × 10 ages × 7 log U, L☉ per
ionizing photon, n_H = 100 cm⁻³, U ≡ Q/(4πR²n_H c), radiation-bounded spherical shells `[verified:
arXiv:1611.08305 §II, read at S35]`) is the dependency to take, read off the very parameters published
here, and the owner gave the word to fetch it on 2026-09-27 (S42). `tools/fetch_nebular.py` takes the
PARSEC-ionized, dust-free file at a pinned FSPS commit into `galaxy/data/nebular_lines.npz`; each region
reads it at its gas's log(Z/Z☉) (its [α/H], the oxygen the stage already computes), its cluster's age and
its own log U, interpolated linearly in log luminosity as FSPS does (``add_nebular.f90``) but **clamped at
the grid's edges** rather than extrapolated. What is published is each line **over the grid's own Hα at
that point**, times the region's Case B Hα: the lines inherit the region's photon budget (escape, leaking)
and the grid only says how they split. `[inferred]`: the grid's gas carries its own abundance pattern,
not the model's published N/H and S/H (those columns are not read by it), and its density is 100 cm⁻³
whatever the region's. The diffuse ionized gas gets no forbidden lines: its enhanced [N II] and [S II]
come from a softer, diluted field the grid does not model, and they are named absent by the render route.
The analytic alternative (a two-level atom on NIST transition probabilities and the PyNeb collision
strengths) was read at S35 and set aside: without the ionization fractions it makes no line.

**Every number below was read at S35 (`phase9_sourcing.md`; rule B9).**

- *Case B*: 4πj/(n_e n_p) for Hβ and Hα and the total recombination coefficient α_B, at n_e = 10² cm⁻³,
  from Storey & Hummer 1995's tables (CDS VI/64, files r1b*.d and e1b.d) `[verified: MNRAS 272, 41;
  cdsarc.cds.unistra.fr/ftp/VI/64]`, interpolated in log T. From them: 0.452 Hα photons per recombination
  at 10⁴ K, Hα/Hβ = 2.863 (Kennicutt 1998 eq. 2 confirms the first to 0.2%).
- *T_e from the gas abundance*: Martínez-Hernández, Méndez-Delgado et al. 2026 eq. 5, 12 + log(O/H) =
  9.29 − 0.96 (T_e/10⁴ K), valid 6000–20000 K `[verified: arXiv:2601.13337]`; O/H from the model's
  [Fe/H] + [α/Fe] on Asplund et al. 2009's solar 8.69 `[verified: arXiv:0909.0948]`.
- *Nitrogen is partly secondary*: Nicholls et al. 2017 eq. 3, log(N/O) = log(10^a + 10^(log(O/H)+b)),
  a = −1.732, b = 2.19, "a starting point for modelling" for the Milky Way's well-mixed gas `[verified:
  arXiv:1612.03546]`; sulphur an α element on Asplund's 7.12.
- *The region*: a Strömgren sphere in its cloud — ionization balance Q = α_B ⟨n_e n_p⟩ (4/3)πR³, with
  the clumping ⟨n²⟩ = e^{σ_s²} ⟨n⟩² from the census's own log-normal width (RENDER_PHYSICS §6: one
  mechanism, two payoffs; the second moment of a log-normal is an identity, not a calibration) — capped at
  the cloud's radius, beyond which the region is density-bounded and leaks. The mass per hydrogen atom,
  1.4 m_H, is the composition's `[inferred]`.
- *Diffuse ionized gas*: 30% of each region's ionizing photons escape it (the model Zurita et al. 2002
  fitted to NGC 157, "30% of emitted Lyman continuum photons escape from each H II region", the range
  30–60% named) `[verified: Haffner et al. 2009, arXiv:0901.0941 §IV]`; none leave the galaxy (Leitherer
  et al. 1995's < 3% `[verified: Kennicutt 1998 §3, arXiv:astro-ph/9807187]`); the layer's temperature
  6000–10000 K and scale height 1000–1800 pc are Haffner's ranges, their midpoints taken `[inferred]`.
  Oey et al. 2007's f_WIM = 0.59 ± 0.19 over 109 galaxies and Haffner's "about 1/8th" of the local stellar
  photons are the readings the construction stands against, not its inputs (debt #101).
- *The check that replaces a calibration* (D166 → S35): the galaxy's Hα is now Σ_Q(R) times Case B, and
  `HALPHA_PER_SFR` (Kennicutt & Evans 2012, log C = 41.27, Kroupa, Starburst99 `[verified: arXiv:1204.3552
  Table 1, §3.1]`) is a consistency check on it — the SFR is upstream of both, so it validates nothing.

**Determinism (D60), and provenance (D55).** No seed is read here: every column is a function of the
cluster's and its cloud's columns, so a region drawn alone is its slice of the sweep by construction. The
stage reads seeded columns, so everything it publishes is *seeded* by rule D55 — the radial Hα fields too,
although they read only radial fields: a stage has one provenance.
"""

from __future__ import annotations

import functools
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np

from galaxy.core.fielddoc import FieldDecl, Kind, Palette, Ramp
from galaxy.core.registry import IMPLEMENTATIONS
from galaxy.core.stage import Context, Stage
from galaxy.stages.disc import PC_PER_KPC
from galaxy.stages.dust import CM_PER_PC
from galaxy.stages.massive_stars import SOLAR_LUMINOSITY
from galaxy.stages.systems import Catalogue

# --- Case B, Storey & Hummer 1995 (CDS VI/64), n_e = 1e2 cm^-3 ------------------------------------------
# T (K), 4 pi j_Hbeta / (n_e n_p), 4 pi j_Halpha / (n_e n_p)  [erg cm^3 s^-1]  (files r1b0030.d ... r1b0300.d,
# E_NU=4 and E_NU=3 blocks, entry 2), read at S35 by a read-only agent from the primary files.
CASE_B_T = np.array([3000.0, 5000.0, 7500.0, 10000.0, 12500.0, 15000.0, 20000.0, 30000.0])
CASE_B_HBETA = np.array([3.265e-25, 2.199e-25, 1.579e-25, 1.235e-25, 1.014e-25, 8.600e-26, 6.579e-26, 4.440e-26])
CASE_B_HALPHA = np.array([1.048e-24, 6.687e-25, 4.625e-25, 3.536e-25, 2.860e-25, 2.398e-25, 1.807e-25, 1.199e-25])
# alpha_B (cm^3 s^-1), the total Case B recombination coefficient, file e1b.d ("alpha-tot"), same n_e. The
# table starts at 5000 K; the file's 3000 K row (6.708e-13, re-read at S37) is not needed, the temperature
# relation being clamped at 6000 K.
ALPHA_B_T = np.array([5000.0, 7500.0, 10000.0, 12500.0, 15000.0, 20000.0, 30000.0])
ALPHA_B = np.array([4.522e-13, 3.273e-13, 2.585e-13, 2.144e-13, 1.836e-13, 1.428e-13, 9.911e-14])

# Physical constants: definitions and CODATA values, not calibrations.
SPEED_OF_LIGHT = 2.99792458e10  # cm/s, exact
PROTON_MASS = 1.67262192e-24  # g (the census's K_OVER_MH uses the same value)
SOLAR_MASS_G = 1.98841e33  # g, IAU 2015 nominal GM_sun / G
CM_PER_KPC = CM_PER_PC * PC_PER_KPC

CLUSTER_READS: tuple[str, ...] = ("cluster_ionizing_photons", "cluster_metallicity", "cluster_age", "cluster_radius")
CLOUD_READS: tuple[str, ...] = ("cloud_mass", "cloud_size", "cloud_density_pdf_width", "cloud_alpha", "cloud_cluster_index")
HII_STATES: tuple[str, ...] = ("bounded", "leaking")
HII_COLUMNS: tuple[str, ...] = (
    "hii_stromgren_radius", "hii_electron_density", "hii_temperature", "hii_ionization_parameter", "hii_clumping",
    "hii_halpha_luminosity", "hii_halpha_emissivity", "hii_balmer_decrement", "hii_oxygen_abundance",
    "hii_nitrogen_abundance", "hii_sulphur_abundance",
    "hii_oiii_5007_ratio", "hii_nii_6583_ratio", "hii_sii_6716_ratio", "hii_sii_6731_ratio",
)
# The forbidden lines the grid is read for (S42), each published over the region's Halpha.
FORBIDDEN: tuple[str, ...] = ("oiii_5007", "nii_6583", "sii_6716", "sii_6731")
LINE_TABLE = Path(__file__).resolve().parents[1] / "data" / "nebular_lines.npz"


@functools.cache
def _line_grid() -> dict[str, np.ndarray]:
    with np.load(LINE_TABLE) as a:
        table = {k: a[k] for k in ("log_z", "log_age_yr", "log_u", "lines", "log_lsun_per_photon")}
    table["lines"] = np.array([str(n) for n in table["lines"]])
    return table


def _axis(values: np.ndarray, axis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The lower grid index and the fraction toward the next, clamped to the grid (no extrapolation)."""
    x = np.clip(np.asarray(values, dtype=float), axis[0], axis[-1])
    i = np.clip(np.searchsorted(axis, x, side="right") - 1, 0, axis.size - 2)
    return i, (x - axis[i]) / (axis[i + 1] - axis[i])


def grid_line_ratios(log_z: np.ndarray, log_age_yr: np.ndarray, log_u: np.ndarray) -> dict[str, np.ndarray]:
    """Each forbidden line over Halpha, read off the Byler et al. 2017 grid at (log Z/Z_sun, log age, log U):
    trilinear in log luminosity per ionizing photon, clamped at the grid's edges. NaN where an input is."""
    g = _line_grid()
    shape = np.broadcast(np.asarray(log_z), np.asarray(log_age_yr), np.asarray(log_u)).shape
    lz, la, lu = (np.broadcast_to(np.asarray(v, dtype=float), shape).ravel() for v in (log_z, log_age_yr, log_u))
    bad = ~(np.isfinite(lz) & np.isfinite(la) & np.isfinite(lu))
    (iz, fz), (ia, fa), (iu, fu) = (_axis(np.where(bad, ax[0], v), ax) for v, ax in
                                    ((lz, g["log_z"]), (la, g["log_age_yr"]), (lu, g["log_u"])))
    cube = g["log_lsun_per_photon"].astype(float)
    log_l = np.zeros((lz.size, cube.shape[-1]))
    for dz in (0, 1):
        for da in (0, 1):
            for du in (0, 1):
                w = (fz if dz else 1 - fz) * (fa if da else 1 - fa) * (fu if du else 1 - fu)
                log_l += w[:, None] * cube[iz + dz, ia + da, iu + du]
    names = list(g["lines"])
    ha = log_l[:, names.index("halpha")]
    return {n: np.where(bad, np.nan, 10.0 ** (log_l[:, names.index(n)] - ha)).reshape(shape) for n in FORBIDDEN}


def ring_ratios(radius_kpc: np.ndarray, weight: np.ndarray, ratio: np.ndarray, R: np.ndarray) -> np.ndarray:
    """The regions' Halpha-weighted mean of one line ratio in each ring of ``R`` (the ring nearest each
    region), a ring without a region taking its nearest occupied neighbours' by linear interpolation in R;
    zero everywhere if no region has light."""
    r = np.asarray(radius_kpc, dtype=float)
    w = np.asarray(weight, dtype=float)
    x = np.asarray(ratio, dtype=float)
    ok = np.isfinite(r) & np.isfinite(w) & np.isfinite(x) & (w > 0)
    if not ok.any():
        return np.zeros_like(R, dtype=float)
    edges = np.concatenate([[-np.inf], 0.5 * (R[1:] + R[:-1]), [np.inf]])
    ring = np.searchsorted(edges, r[ok], side="right") - 1
    num = np.bincount(ring, weights=w[ok] * x[ok], minlength=R.size)
    den = np.bincount(ring, weights=w[ok], minlength=R.size)
    lit = den > 0
    return np.interp(R, R[lit], num[lit] / den[lit])


def _log_interp(t: np.ndarray, table_t: np.ndarray, table_v: np.ndarray) -> np.ndarray:
    """A table in log T, log value; clamped at the table's ends."""
    lt = np.log10(np.clip(np.asarray(t, dtype=float), table_t[0], table_t[-1]))
    return 10.0 ** np.interp(lt, np.log10(table_t), np.log10(table_v))


def case_b_hbeta(t: np.ndarray) -> np.ndarray:
    """4πj_Hβ/(n_e n_p), erg cm³ s⁻¹, at T (K)."""
    return _log_interp(t, CASE_B_T, CASE_B_HBETA)


def case_b_halpha(t: np.ndarray) -> np.ndarray:
    """4πj_Hα/(n_e n_p), erg cm³ s⁻¹, at T (K)."""
    return _log_interp(t, CASE_B_T, CASE_B_HALPHA)


def alpha_b(t: np.ndarray) -> np.ndarray:
    """The total Case B recombination coefficient, cm³ s⁻¹, at T (K)."""
    return _log_interp(t, ALPHA_B_T, ALPHA_B)


def halpha_per_recombination(t: np.ndarray) -> np.ndarray:
    """erg of Hα per recombination (= per ionizing photon absorbed by hydrogen): E_Hα(T)/α_B(T)."""
    return case_b_halpha(t) / alpha_b(t)


def electron_temperature(oxygen_12: np.ndarray, c: Mapping[str, float]) -> np.ndarray:
    """T_e (K) from 12 + log(O/H): the DESIRED relation inverted and clamped to its validity range."""
    t = (float(c["TE_METALLICITY_INTERCEPT"]) - np.asarray(oxygen_12, dtype=float)) / float(c["TE_METALLICITY_SLOPE"]) * 1.0e4
    return np.clip(t, float(c["TE_VALID_MIN"]), float(c["TE_VALID_MAX"]))


def abundances(feh: np.ndarray, alpha_fe: np.ndarray, c: Mapping[str, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(12+log O/H, 12+log N/H, 12+log S/H): oxygen and sulphur as α elements on the solar scale, nitrogen by
    the primary-plus-secondary relation."""
    alpha_shift = np.asarray(feh, dtype=float) + np.asarray(alpha_fe, dtype=float)
    oxygen = float(c["OXYGEN_ABUNDANCE_SOLAR"]) + alpha_shift
    sulphur = float(c["SULPHUR_ABUNDANCE_SOLAR"]) + alpha_shift
    log_oh = oxygen - 12.0
    log_no = np.log10(10.0 ** float(c["NO_PRIMARY_LOG"]) + 10.0 ** (log_oh + float(c["NO_SECONDARY_LOG"])))
    return oxygen, oxygen + log_no, sulphur


def mean_hydrogen_density(mass_msun: np.ndarray, radius_pc: np.ndarray, mass_per_h: float) -> np.ndarray:
    """⟨n_H⟩ (cm⁻³) of a uniform sphere of this mass and radius."""
    volume = 4.0 / 3.0 * math.pi * (np.asarray(radius_pc, dtype=float) * CM_PER_PC) ** 3
    return np.asarray(mass_msun, dtype=float) * SOLAR_MASS_G / (mass_per_h * PROTON_MASS) / volume


def stromgren_radius_cm(q: np.ndarray, n_squared: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """R_S from ionization balance, Q = α_B ⟨n²⟩ (4/3)πR³."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r3 = 3.0 * np.asarray(q, dtype=float) / (4.0 * math.pi * np.asarray(alpha, dtype=float) * np.asarray(n_squared, dtype=float))
    return np.cbrt(np.where(np.isfinite(r3), r3, 0.0))


def luminosity_function_slope(l_erg: np.ndarray, l_min: float, bin_dex: float = 0.2) -> float:
    """dN/dL ∝ L^α over the regions above ``l_min``: α is the least-squares slope of log N per log-L bin
    against the bin's centre, minus one. NaN with fewer than three occupied bins."""
    l = np.asarray(l_erg, dtype=float)
    l = l[np.isfinite(l) & (l >= l_min)]
    if l.size < 3:
        return float("nan")
    lo = math.log10(l_min)
    hi = math.log10(l.max()) + 1.0e-9
    edges = np.arange(lo, hi + bin_dex, bin_dex)
    counts, _ = np.histogram(np.log10(l), bins=edges)
    centres = 0.5 * (edges[1:] + edges[:-1])
    keep = counts > 0
    if keep.sum() < 3:
        return float("nan")
    slope = np.polyfit(centres[keep], np.log10(counts[keep]), 1)[0]
    return float(slope - 1.0)


def materialise_nebular(clusters: Catalogue, clouds: Catalogue, constants: Mapping[str, float]) -> Catalogue:
    """The HII region of every cluster in ``clusters`` (a :func:`clusters.materialise_clusters` catalogue), whose
    cloud is the host row of ``clouds`` in order — the k-th cluster is the k-th cloud with a cluster index —
    with the clusters' ``counts``. No draw: a region alone is its slice of the sweep (D60)."""
    c = constants
    hosts = np.flatnonzero(np.asarray(clouds["cloud_cluster_index"], dtype=float) >= 0.0)
    q = np.asarray(clusters["cluster_ionizing_photons"], dtype=float)
    if hosts.size != q.size:
        raise ValueError(f"{q.size} clusters but {hosts.size} hosting clouds")
    if not q.size:
        empty = np.zeros(0)
        return Catalogue.of({n: empty for n in HII_COLUMNS} | {"hii_density_bounded": empty.astype(np.int64)}, clusters.counts)

    def cloud(name: str) -> np.ndarray:
        return np.asarray(clouds[name], dtype=float)[hosts]

    feh = np.asarray(clusters["cluster_metallicity"], dtype=float)
    oxygen, nitrogen, sulphur = abundances(feh, cloud("cloud_alpha"), c)
    t_e = electron_temperature(oxygen, c)
    alpha = alpha_b(t_e)
    clumping = np.exp(cloud("cloud_density_pdf_width") ** 2)
    n_mean = mean_hydrogen_density(cloud("cloud_mass"), cloud("cloud_size"), float(c["HII_MASS_PER_HYDROGEN"]))
    n_squared = clumping * n_mean**2
    q_trapped = (1.0 - float(c["HII_ESCAPE_FRACTION"])) * q
    r_s = stromgren_radius_cm(q_trapped, n_squared, alpha)
    r_cloud = cloud("cloud_size") * CM_PER_PC
    leaking = r_s > r_cloud
    radius = np.where(leaking, r_cloud, r_s)
    with np.errstate(divide="ignore", invalid="ignore"):
        absorbed = np.where(leaking, q_trapped * (r_cloud / np.where(r_s > 0, r_s, 1.0)) ** 3, q_trapped)
    l_halpha = absorbed * halpha_per_recombination(t_e)  # erg/s
    volume = 4.0 / 3.0 * math.pi * radius**3
    with np.errstate(divide="ignore", invalid="ignore"):
        emissivity = np.where(volume > 0, l_halpha / np.where(volume > 0, volume, 1.0), 0.0)
        log_u = np.log10(q_trapped / (4.0 * math.pi * radius**2 * np.sqrt(n_squared) * SPEED_OF_LIGHT))
    lines = grid_line_ratios(oxygen - float(c["OXYGEN_ABUNDANCE_SOLAR"]),
                             np.log10(np.asarray(clusters["cluster_age"], dtype=float) * 1.0e6),
                             np.where(np.isfinite(log_u), log_u, np.nan))
    out = {
        "hii_stromgren_radius": radius / CM_PER_PC,
        "hii_electron_density": np.sqrt(n_squared),
        "hii_temperature": t_e,
        "hii_ionization_parameter": np.where(np.isfinite(log_u), log_u, np.nan),
        "hii_clumping": clumping,
        "hii_halpha_luminosity": l_halpha / SOLAR_LUMINOSITY,
        "hii_halpha_emissivity": emissivity,
        "hii_balmer_decrement": case_b_halpha(t_e) / case_b_hbeta(t_e),
        "hii_oxygen_abundance": oxygen,
        "hii_nitrogen_abundance": nitrogen,
        "hii_sulphur_abundance": sulphur,
        **{f"hii_{n}_ratio": lines[n] for n in FORBIDDEN},
        "hii_density_bounded": leaking.astype(np.int64),
    }
    return Catalogue.of(out, clusters.counts)


def leaked_fraction(clusters: Catalogue, regions: Catalogue, constants: Mapping[str, float]) -> float:
    """The share of the clusters' ionizing photons that reach the diffuse gas: the escape fraction plus what
    the density-bounded regions leak."""
    q = np.asarray(clusters["cluster_ionizing_photons"], dtype=float)
    total = float(q.sum())
    if total <= 0.0:
        return float(constants["HII_ESCAPE_FRACTION"])
    absorbed = np.asarray(regions["hii_halpha_luminosity"], dtype=float) * SOLAR_LUMINOSITY / halpha_per_recombination(
        np.asarray(regions["hii_temperature"], dtype=float)
    )
    return 1.0 - float(absorbed.sum()) / total


# --- declarations ------------------------------------------------------------------------------------------


# S41 (V4, D191): the HII-region columns the viewer does not read, each with why - the object-class twin of the
# sentence the stage's scalars carry under rule D4 (debt #69); tests/test_v4.py holds the inventory. S42 (D192)
# drew `hii_balmer_decrement` and the four `hii_*_ratio` columns (region.ts regionLineColour), so they have no entry.
NOT_DRAWN_WHY: dict[str, str] = {
    "hii_electron_density": "drawn through `hii_halpha_emissivity`, which is this density squared times the Case B "
                            "coefficient; a density has no look but its emission measure.",
    "hii_temperature": "drawn through the emissivity's Case B coefficient at this temperature; a temperature itself "
                       "is a line ratio's to show.",
    "hii_ionization_parameter": "the axis the photoionization grid reads the forbidden lines along: drawn through "
                                "the four `hii_*_ratio` columns it sets (S42), never as itself.",
    "hii_clumping": "drawn through `hii_halpha_emissivity` (the emission measure's correction) and through the cloud's "
                    "log-normal interior, which is the same width.",
    "hii_halpha_luminosity": "the emissivity integrated over the sphere: the march integrates `hii_halpha_emissivity` "
                             "over the radius, and the sum is the gate's number (D190), not a look.",
    "hii_oxygen_abundance": "drawn through the electron temperature it sets (the emissivity's Case B coefficient) and "
                            "through the forbidden lines: it is the metallicity the grid is read at (S42).",
    "hii_nitrogen_abundance": "not read by anything drawn: the [N II] line the region carries (S42) comes off the grid "
                              "at the gas's oxygen, with the grid's own N/O, not this column (debt #118).",
    "hii_sulphur_abundance": "not read by anything drawn: the [S II] lines the region carries (S42) come off the grid "
                             "at the gas's oxygen, with the grid's own S/O, not this column (debt #118).",
    "hii_density_bounded": "drawn through the radius: a leaking region's sphere is its whole cloud, which "
                           "`hii_stromgren_radius` already says; the category itself is not a look.",
}


def _not_drawn(name: str) -> str:
    why = NOT_DRAWN_WHY.get(name)
    return f" **Not drawn by the viewer** (D191): {why}" if why else ""


def _column(name: str, label: str, unit: str, about: str, ramp: Ramp = Ramp("viridis")) -> FieldDecl:
    return FieldDecl(name=name, label=label, unit=unit, kind=Kind.COLUMN, of="cluster",
                     ramp=ramp, meaningful_zero=True, provenance="seeded", about=about + _not_drawn(name))


_D4 = (" **Not shown by the viewer** (rule D4, as debt #69 was ruled at S22): a galaxy scalar of the stage that "
       "publishes the HII-region columns, which `scalarsAt` excludes; `/api/arrays` serves it.")

HII_RADIUS = _column("hii_stromgren_radius", "HII region radius", "pc",
                     "The Strömgren radius of the cluster's region in its cloud's clumped gas — ionization balance "
                     "between the photons the region keeps and the recombinations the mean square density "
                     "supports — or the cloud's radius where the region would outgrow it and leaks instead. "
                     "A renderer draws the ionized sphere at this radius around the cluster.", ramp=Ramp("viridis", scale="log"))
HII_DENSITY = _column("hii_electron_density", "Electron density (rms)", "1/cm3",
                      "The root mean square hydrogen density of the region's gas: the cloud's mean density times "
                      "the square root of its clumping, because emission measure goes as n² and the mean gets it "
                      "wrong by that factor (RENDER_PHYSICS §6).", ramp=Ramp("magma", scale="log"))
HII_TEMPERATURE = _column("hii_temperature", "Electron temperature", "K",
                          "From the gas's oxygen abundance by the temperature–metallicity relation of star-forming "
                          "regions (Martínez-Hernández et al. 2026), clamped to the 6000–20000 K it was fitted over; "
                          "the inner disc's metal-rich gas sits at the floor.", ramp=Ramp("inferno"))
HII_LOG_U = _column("hii_ionization_parameter", "Ionization parameter log U", "dex",
                    "log of the ionizing photon density over the gas density at the region's radius, in the "
                    "definition the photoionization grids use (U = Q / 4πR² n c): the axis along which the "
                    "tabulated grid is read for the collisionally excited lines (S35's ruling, fetched at S42).",
                    ramp=Ramp("plasma"))
HII_CLUMPING = _column("hii_clumping", "Clumping ⟨n²⟩/⟨n⟩²", "dimensionless",
                       "e^(σ_s²) from the cloud census's log-normal width: the same mechanism that structures the "
                       "cloud corrects its emission measure.", ramp=Ramp("viridis", scale="log"))
HII_HALPHA = _column("hii_halpha_luminosity", "Hα luminosity", "Lsun",
                     "The photons the region keeps, times the Hα energy per recombination at its temperature "
                     "(Case B, Storey & Hummer 1995). Intrinsic: no dust between the region and the eye is applied here.",
                     ramp=Ramp("magma", scale="log"))
HII_EMISSIVITY = _column("hii_halpha_emissivity", "Hα volume emissivity", "erg/s/cm3",
                         "The region's Hα per unit volume, uniform inside its radius — RENDER_PHYSICS §4's contract: a "
                         "renderer integrates it along the ray, so a shell brightens at its limb by itself.",
                         ramp=Ramp("magma", scale="log"))
HII_DECREMENT = _column("hii_balmer_decrement", "Hα/Hβ", "dimensionless",
                        "The Case B ratio at the region's temperature, 2.86 at 10⁴ K and 3.0 at 5000: what a renderer "
                        "reddens; the Hβ line is this quotient of the Hα.", ramp=Ramp("viridis"))
HII_OXYGEN = _column("hii_oxygen_abundance", "12 + log(O/H)", "dex",
                     "The gas's oxygen at the cluster's radius: [Fe/H] plus [α/Fe] on the solar scale (Asplund et al. 2009).",
                     ramp=Ramp("plasma"))
HII_NITROGEN = _column("hii_nitrogen_abundance", "12 + log(N/H)", "dex",
                       "Nitrogen does not track the α elements: a primary floor plus a secondary term that grows with "
                       "O/H (Nicholls et al. 2017's fit to Milky Way stars), so N/O rises from −1.7 in metal-poor gas "
                       "toward −0.7 in the inner disc.", ramp=Ramp("plasma"))
HII_SULPHUR = _column("hii_sulphur_abundance", "12 + log(S/H)", "dex",
                      "Sulphur as an α element on the solar scale (Asplund et al. 2009).", ramp=Ramp("plasma"))
_LINE_LABELS = {"oiii_5007": "[O III] 5007", "nii_6583": "[N II] 6583", "sii_6716": "[S II] 6716", "sii_6731": "[S II] 6731"}
_GRID = ("Read off Byler et al. 2017's photoionization grid (as FSPS ships it; tools/fetch_nebular.py) at the "
         "region's gas metallicity, its cluster's age and its log U, clamped at the grid's edges: the line over the "
         "grid's own Halpha at that point, so the region's Halpha luminosity or emissivity times this is the line's. ")
HII_LINE_RATIOS = tuple(
    _column(f"hii_{n}_ratio", f"{label} / Hα", "dimensionless",
            _GRID + {"oiii_5007": "Doubly ionized oxygen: it rises with log U and with the hotter, younger clusters, and "
                                  "falls in metal-rich gas, which cools through the infrared lines instead.",
                     "nii_6583": "Singly ionized nitrogen from the partially ionized edge: strong in metal-rich, low-U "
                                 "regions; the grid's own N/O, not the model's published N/H, sets it.",
                     "sii_6716": "Singly ionized sulphur, the doublet's blue line: from the region's outskirts, strongest "
                                 "at low log U.",
                     "sii_6731": "The doublet's red line; the pair's ratio is the grid's at its 100 cm⁻³, not a "
                                 "measure of this region's density."}[n],
            ramp=Ramp("viridis", scale="log"))
    for n, label in _LINE_LABELS.items()
)
HII_BOUNDED = FieldDecl(
    name="hii_density_bounded", label="Region bounded by", unit="dimensionless", kind=Kind.CATEGORY_COLUMN, of="cluster",
    categories=HII_STATES, ramp=Palette(("#3b6fb6", "#e0a030")), provenance="seeded",
    about=(
        "Bounded: the ionization front stops inside the cloud. Leaking: the cluster's photons would ionize "
        "more than the cloud holds, so the region is the whole cloud and the excess joins the diffuse gas."
        + _not_drawn("hii_density_bounded")
    ),
)

HALPHA_HII = FieldDecl(
    name="halpha_surface_brightness_hii", label="Hα from HII regions Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
    about=(
        "The ionizing photons the HII regions keep — the disc's photon rate per area less the share that "
        "escapes each region — times the Hα energy per recombination at the gas's temperature at that "
        "radius. A galaxy-scale surface quantity (RENDER_PHYSICS §4); the census's regions integrate back to "
        "it within their noise and the leak of the density-bounded ones, which a test asserts."
    ),
)
HALPHA_DIG = FieldDecl(
    name="halpha_surface_brightness_dig", label="Hα from the diffuse ionized gas Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
    about=(
        "The escaped share of the disc's ionizing photons, absorbed in the warm ionized layer and emitted as "
        "Hα at that layer's temperature: the glow between the knots. Face-on it is a surface quantity; the "
        "layer's scale height is published for the renderer to spread it vertically."
    ),
)
HALPHA_NEBULAR = FieldDecl(
    name="halpha_surface_brightness_nebular", label="Hα surface brightness, nebular Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
    about=(
        "HII regions plus diffuse gas: every ionizing photon the disc emits makes Hα somewhere, since none "
        "leave the galaxy (Leitherer et al. 1995's limit of 3%). This is the field that replaces the star "
        "formation rate times a constant (D166): that constant is now a check on this, not this."
    ),
)
DIG_SCALE_HEIGHT = FieldDecl(
    name="dig_scale_height", label="Diffuse ionized layer scale height", unit="kpc", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The warm ionized medium's scale height — the midpoint of the 1000–1800 pc Haffner et al. 2009 read for "
        "the Milky Way's layer, 'significantly larger than that of the neutral hydrogen layer' — published so "
        "the renderer spreads the diffuse Hα vertically without holding a number of its own (D5)." + _D4
    ),
)
HALPHA_TOTAL = FieldDecl(
    name="halpha_luminosity_nebular", label="Hα luminosity, nebular", unit="Lsun", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The nebular surface brightness integrated over the disc: the galaxy's intrinsic Hα from its ionizing "
        "photons, regions and diffuse gas together." + _D4
    ),
)
DIG_FRACTION = FieldDecl(
    name="dig_halpha_fraction", label="Diffuse share of the Hα", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The share of the census's ionizing photons that reach the diffuse gas: the escape fraction every region "
        "is given plus what the density-bounded regions leak. Oey et al. 2007 measure 0.59 ± 0.19 of the Hα as "
        "diffuse over 109 galaxies, and Haffner et al. 2009 put the local warm ionized medium at about an "
        "eighth of the stellar photons; the model's value is the construction's, and debt #101 says so." + _D4
    ),
)
HALPHA_SFR_RATIO = FieldDecl(
    name="halpha_sfr_ratio", label="Hα per SFR, Q-derived over Kennicutt & Evans", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=True, provenance="seeded",
    about=(
        "The nebular Hα over the star formation rate times Kennicutt & Evans 2012's calibration (log C = 41.27, "
        "Kroupa IMF, Starburst99). **A consistency check, not a validation**: the star formation rate is upstream "
        "of both sides, so this measures the model's ionizing photons per unit star formation against theirs "
        "— the isochrones' Q against Starburst99's — and nothing about the galaxy." + _D4
    ),
)
HBETA_HII = FieldDecl(
    name="hbeta_surface_brightness_hii", label="Hβ from HII regions Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
    about="The HII regions' Hα over the Case B decrement at the gas's temperature at that radius (Storey & Hummer 1995).",
)
HBETA_DIG = FieldDecl(
    name="hbeta_surface_brightness_dig", label="Hβ from the diffuse ionized gas Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
    axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
    about="The diffuse gas's Hα over the Case B decrement at the layer's temperature.",
)
LINES_HII = tuple(
    FieldDecl(
        name=f"{n}_surface_brightness_hii", label=f"{label} from HII regions Σ(R)", unit="Lsun/pc2", kind=Kind.FIELD,
        axes=("R",), ramp=Ramp("magma", scale="log"), meaningful_zero=True, provenance="seeded",
        about=(f"The HII regions' Hα at this radius times the census's regions' Hα-weighted {label}/Hα in the ring "
               "(a ring without a region takes its neighbours'): the line the grid gives the regions that are there. "
               "The diffuse gas adds none (the grid does not model its field)."),
    )
    for n, label in _LINE_LABELS.items()
)
HII_LF_SLOPE = FieldDecl(
    name="hii_luminosity_function_slope", label="HII-region luminosity function slope", unit="dimensionless", kind=Kind.SCALAR,
    meaningful_zero=False, provenance="seeded",
    about=(
        "dN/dL ∝ L^α over the regions brighter than 10³⁷ erg/s in Hα, the completeness floor below which "
        "Kennicutt, Edgar & Hodge 1989 find the observed functions flatten: the slope of log N per 0.2 dex bin "
        "against log L, less one. Acceptance row 35." + _D4
    ),
)


def compute_nebular(ctx: Context) -> Mapping[str, Any]:
    c = ctx.constants
    R = ctx.grid.R
    f = ctx.fields
    clusters = Catalogue.of({n: f[n] for n in CLUSTER_READS})
    clouds = Catalogue.of({n: f[n] for n in CLOUD_READS})
    regions = materialise_nebular(clusters, clouds, c)

    # Galaxy scale: the disc's photon rate per area, split by the escape fraction, at the gas's temperature.
    sigma_q = np.asarray(f["ionizing_photon_rate"], dtype=float)  # 1/s/kpc2
    oxygen, _, _ = abundances(f["feh_gas"], f["alpha_fe_gas"], c)
    t_gas = electron_temperature(oxygen, c)
    escape = float(c["HII_ESCAPE_FRACTION"])
    per_pc2 = 1.0 / PC_PER_KPC**2 / SOLAR_LUMINOSITY
    hii = (1.0 - escape) * sigma_q * halpha_per_recombination(t_gas) * per_pc2
    dig = escape * sigma_q * float(halpha_per_recombination(np.array([float(c["DIG_TEMPERATURE"])]))[0]) * per_pc2
    total = hii + dig
    weight = np.asarray(regions["hii_halpha_luminosity"], dtype=float)
    radius = np.asarray(clusters["cluster_radius"], dtype=float)
    lines = {f"{n}_surface_brightness_hii": hii * ring_ratios(radius, weight, regions[f"hii_{n}_ratio"], R) for n in FORBIDDEN}
    decrement_dig = float((case_b_halpha(np.array([float(c["DIG_TEMPERATURE"])])) / case_b_hbeta(np.array([float(c["DIG_TEMPERATURE"])])))[0])
    l_nebular = float(np.trapezoid(total * 2.0 * math.pi * R, R)) * PC_PER_KPC**2  # Lsun
    sfr = float(np.trapezoid(np.asarray(f["sfr_surface_density"], dtype=float) * 2.0 * math.pi * R, R))  # Msun/yr
    return {
        **regions,
        "halpha_surface_brightness_hii": hii,
        "halpha_surface_brightness_dig": dig,
        "halpha_surface_brightness_nebular": total,
        "hbeta_surface_brightness_hii": hii * case_b_hbeta(t_gas) / case_b_halpha(t_gas),
        "hbeta_surface_brightness_dig": dig / decrement_dig,
        **lines,
        "dig_scale_height": float(c["DIG_SCALE_HEIGHT"]),
        "halpha_luminosity_nebular": l_nebular,
        "dig_halpha_fraction": leaked_fraction(clusters, regions, c),
        "halpha_sfr_ratio": l_nebular / (sfr * float(c["HALPHA_PER_SFR"])) if sfr > 0 else float("nan"),
        "hii_luminosity_function_slope": luminosity_function_slope(
            np.asarray(regions["hii_halpha_luminosity"], dtype=float) * SOLAR_LUMINOSITY, float(c["HII_LF_MIN_LUMINOSITY"])
        ),
    }


NEBULAR = IMPLEMENTATIONS.register(
    Stage(
        id="nebular", slot="nebular", checkpoint=5,
        about=(
            "The ionized gas: every young cluster's HII region as the parameters a renderer draws it from — "
            "radius, density, temperature, ionization parameter, abundances — with its Hα per unit volume in "
            "closed form; the diffuse ionized layer; and the disc's Hα as its ionizing photons redistributed."
        ),
        compute=compute_nebular,
        reads_constants=(
            "HALPHA_PER_SFR", "HII_ESCAPE_FRACTION", "HII_MASS_PER_HYDROGEN", "HII_LF_MIN_LUMINOSITY",
            "DIG_TEMPERATURE", "DIG_SCALE_HEIGHT", "TE_METALLICITY_INTERCEPT", "TE_METALLICITY_SLOPE",
            "TE_VALID_MIN", "TE_VALID_MAX", "NO_PRIMARY_LOG", "NO_SECONDARY_LOG", "OXYGEN_ABUNDANCE_SOLAR",
            "NITROGEN_ABUNDANCE_SOLAR", "SULPHUR_ABUNDANCE_SOLAR",
        ),
        requires=(*CLUSTER_READS, *CLOUD_READS, "ionizing_photon_rate", "feh_gas", "alpha_fe_gas", "sfr_surface_density"),
        publishes=(
            HII_RADIUS, HII_DENSITY, HII_TEMPERATURE, HII_LOG_U, HII_CLUMPING, HII_HALPHA, HII_EMISSIVITY, HII_DECREMENT,
            HII_OXYGEN, HII_NITROGEN, HII_SULPHUR, *HII_LINE_RATIOS, HII_BOUNDED,
            HALPHA_HII, HALPHA_DIG, HALPHA_NEBULAR, HBETA_HII, HBETA_DIG, *LINES_HII, DIG_SCALE_HEIGHT, HALPHA_TOTAL, DIG_FRACTION, HALPHA_SFR_RATIO, HII_LF_SLOPE,
        ),
    )
)
