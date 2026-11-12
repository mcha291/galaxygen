# READING_CLOUD_SIZES — the clouds' surface density and their largest radius (S67, D231)

**The lead's note (2026-10-18, entered at S67 on the owner's choice "Smaller giant clouds (model)").** Until S67
every cloud's radius was √(M / πΣ) at one surface density, `GMC_SURFACE_DENSITY` = 42 M☉ pc⁻² (Heyer et al.
2009's median); with Rice et al. 2016's inner truncation at 10⁷ M☉ the inner Galaxy's largest clouds came out
150-275 pc in radius and the viewer drew them as 300-500 pc dark discs. One blind Opus reader (no repository access)
read the sources below on 2026-10-18; what is below the rule is its report in substance. **What the lead took from
it** (D231 rules on it): (1) Heyer et al.'s 42 is measured over R 4.1-8.1 kpc only, within the 13CO area, with no
radial dependence found there; (2) Lada & Dame 2020, correcting the CO-to-H₂ factor for its radial gradient
(X_CO(R)), find 82 ± 10 M☉ pc⁻² in the molecular ring and inside it and "a single mass surface density of Σ_GMC =
35" outside it - the corrected values supersede the 42, which is their uncorrected reading of the same region;
their constant-X_CO 13 ± 4 at 9-14 kpc and their eq. 1 (Σ = 54.5 − 3.7 R) are the uncorrected readings, not entered;
(3) the largest Milky Way clouds have radii of ~60-150 pc, Miville-Deschenes et al. 2017's largest ~150 pc,
"comparable to the molecular disk's scale height"; (4) giants are denser than the median (W43: R_eq ~70 pc at
7.1 × 10⁶ M☉, Σ ≈ 460; Sgr B2 denser still). Entered as three level-0 constants: `GMC_SURFACE_DENSITY_INNER` = 82,
`GMC_SURFACE_DENSITY_OUTER` = 35 (`[verified: Lada & Dame 2020]`), the boundary the model's `R_SUN` (the one the mass
function's truncation already uses), and `GMC_RADIUS_MAX` = 150 pc (`[verified: Miville-Deschenes et al. 2017]`),
the mass kept, so a capped cloud's surface density rises.

**S70 (D234; the owner's ruling D233 on #192, Audit V F-1B-2):** the two regimes split at `R_SUN` were the reader's
extrapolation - the source gives 82 ± 10 for the molecular ring alone (4-7 kpc, §IV.2 and §VI; "likely an upper
limit", §V) and 35 elsewhere, inside 4 kpc and between the ring and the Sun included. Entered since as the
source's three regimes by the birth radius: `GMC_SURFACE_DENSITY_RING` = 82 in [`GMC_MOLECULAR_RING_INNER`,
`GMC_MOLECULAR_RING_OUTER`) = [4, 7) kpc, `GMC_SURFACE_DENSITY_DISC` = 35 inside and beyond it (the two constants
renamed from `_INNER` and `_OUTER`); a template pins its own ring (`molecular_ring`), NGC 4414's 0.43-4.29 kpc
from Vallejo, Braine & Baudry 2002's obscured molecular ring (5″-50″ at 17.7 Mpc). *(re-read at Audit V, S70)*

---

## The reading (the reader's report, 2026-10-18)

Σ is mass over projected area and R the equal-area radius, √(A/π), unless stated.

- **Heyer, Krawczyk, Duval & Jackson 2009** (ApJ 699, 1092; arXiv:0809.1397) §2.2, §4. Median Σ **42** M☉ pc⁻²
  (standard deviation 37), 13CO in LTE within the SRBY area A1 (Solomon et al. 1987's clouds re-observed); within the
  half-power isophote ~200. "No dependence of mass surface density is found with galactocentric radius" - over
  R 4.1-8.1 kpc only. **Until S67 the value entered; superseded by Lada & Dame's corrected 82.**
- **Roman-Duval et al. 2010** (ApJ 723, 492). Median 144 within the 4σ 13CO contour; M = 228 R^2.36; bin means ~170
  at 4-6 kpc falling to 120 at 7.5 kpc (threshold-biased high).
- **Miville-Deschenes, Murray & Lee 2017** (ApJ 834, 57; arXiv:1610.05918). A whole-Galaxy 12CO catalogue: Σ mean 28.6
  (41.9 in the inner Galaxy, R ≤ 8.5 kpc; 10.4 outer), M = 36.7 R^2.2, masses to 2.2 × 10⁷ M☉, radii to **~150 pc**,
  "comparable to the molecular disk's scale height"; half the mass in clouds above 8.4 × 10⁵ M☉, with R ~60 pc (Σ over
  pixel area, R a moment radius). **The cap entered** (`GMC_RADIUS_MAX`).
- **Lada & Dame 2020** (ApJ 898, 3; arXiv:2006.08632), R = √(A/π). M = 78.6 R^1.98 (on Rice et al. 2016's catalogue),
  57.5 R^2.10 (on Miville-Deschenes et al.'s); the inner Galaxy (3-5 kpc) mean 84.5, the outer (11-13 kpc) 11.7;
  13 ± 4, flat, at 9-14 kpc; eq. 1, Σ = 54.5 − 3.7 R (12CO at a constant X_CO, fitted outside 4-8 kpc). After the
  X_CO(R) correction: **82 ± 10 inside the molecular ring** and "a single mass surface density of **Σ_GMC = 35**"
  outside it; at 8-9 kpc CO gives 26.6 against extinction's 41-52. **The two values entered**
  (`GMC_SURFACE_DENSITY_INNER`, `GMC_SURFACE_DENSITY_OUTER`; since S70 `_RING` and `_DISC`, three regimes by radius).
- **Rice et al. 2016** (ApJ 822, 52; arXiv:1602.02791). The inner Galaxy's mass function a truncated power law, γ −1.6,
  M₀ (1.0 ± 0.2) × 10⁷ M☉; the outer an untruncated −2.2 with M₀ 1.5 × 10⁶ (already the model's, S32).
- **W43** (Nguyen Luong et al. 2011, A&A 529, A41): R_eq ~70 pc, 7.1 × 10⁶ M☉ (Σ ≈ 460). **Sgr B2** (Schmiedeke et al.
  2016): 8.0 × 10⁶ M☉ within a 45 pc diameter.
- **Extragalactic.** PHANGS clouds Σ ~100 (Rosolowsky et al. 2021, inside the FWHM): bar 130, disc 96, arm 87,
  interarm 75; barred centres ~20× the discs' sightline Σ (Sun et al. 2020); M51's centre 212, arms 185, interarm 143
  (Colombo et al. 2014).
- Heyer & Dame 2015 was not read (403).

---

## Part S89 — what #181's, #182's, #94's and #95's closers need (2026-11-04, no web access)

Read beside today's model at S89 (BUILD_V row 89). None of the four is built; each needs a source the repository does
not hold, or a ruling.

- **#182, the giants.** The two mass-radius relations above (Miville-Deschênes et al. 2017, M = 36.7 R^2.2; Lada & Dame
  2020, M = 78.6 R^1.98) put a 10⁷ M☉ cloud at R = 296 and 378 pc and a 10⁶ M☉ cloud at 104 and 118 pc; the model's
  regimes give 62 pc (Σ 82) and 95 pc (Σ 35) at 10⁶ and cap every cloud at 150 pc. A relation in place of the cap makes
  the giants larger than the owner chose at S67 ("Smaller giant clouds (model)", D231), and the catalogues' R is a
  radius of a CO footprint, not √(M/πΣ_GMC): a ruling, the owner's. A Σ_GMC profile across the molecular
  ring's edge (Lada & Dame's regimes are joined by none; their ring's 82 is "likely an upper limit", blending, §V) and
  NGC 4414's own cloud census are not held.
- **#182's radii restated (re-read at Audit VI, F-1B-3).** The two relations above are on different radii and
  catalogues. Miville-Deschênes et al. 2017's R is an inertia-matrix radius, R = D tan(R_ang) with R_ang =
  (R_max R_min R_min)^(1/3) (their eq. 18), not an equal-area one; on Lada & Dame's equal-area radius √(A/π) their
  clouds read **M = 57.5 R^2.10** (Lada & Dame 2020, §III.1), which puts a 10⁷ M☉ cloud at about **313 pc** and a 10⁶
  at 104 pc (`[inferred]`: (M/57.5)^(1/2.10), computed at S95). Lada & Dame's 78.6 R^1.98 is their fit to Rice et al.
  2016's catalogue ("for the clouds in the R+16 catalog"), not to clouds of their own. On one radius the two
  catalogues' 10⁷ M☉ clouds sit at about 313 and 378 pc; the paragraph's conclusion is unchanged — a relation in
  place of the cap makes the giants larger than the owner chose (re-read at Audit VI, F-1B-3).
- **#181, the HII complexes.** A size-luminosity relation for giant HII regions in nearby discs and their luminosity
  function (candidates `[recall — NEEDS SOURCING]`: Kennicutt 1984's giant HII region sizes; the PHANGS-MUSE nebular
  catalogue's HII region sizes and luminosities). With one read, the census's regions in one clustering cell can be
  merged into one Strömgren volume of their summed photons at the cell level whose merged sizes match it; without it the
  level is a guess.
- **#94, the diffuse molecular gas.** A diffuse (non-cloud) share of the Milky Way's CO or H₂ with its error (Roman-Duval
  et al. 2016's diffuse component is the nearest candidate `[recall — NEEDS SOURCING]`; the reader above gave only its
  layer, 130-200 pc), or a sourced completeness limit for the mass function's lower end (10⁴ M☉ is `[inferred]`).
- **#95, the cloud vector's draws.** An HII-region-to-cloud offset distribution (a PHANGS cloud-HII-region cross-match
  `[recall]`), a measured density gradient across clouds, a remnant shell's visibility time: each a constant with its
  citation in place of the stated draw.

## Part S96 — the diffuse molecular share (#94), a cluster's offset from its cloud (#95), HII regions' sizes and luminosity function (#181) (2026-11-12, read at the reading session; reader B)

S96's reader B fetched the sources below in this session (its note `s96_B.md` in the session's scratchpad; the PDFs of
Roman-Duval et al. 2016 and Grasha et al. 2017a and their text are in its `s96_B_dl` directory). `[verified: source,
place]` marks what it quoted from a fetched page; `[inferred]` its own arithmetic.

### S96.1 #94 — what share of the molecular gas is in clouds

- **Roman-Duval et al. 2016**, ApJ 818, 144, arXiv:1601.00937v1 (abstract page and the PDF through `pdftotext -layout`).
  Abstract: "a high column density component detected in 13CO and 12CO, and a low column density component detected in
  12CO, but not in 13CO"; "The diffuse component, which globally represents 25% (1.5x10^8 Msun) of the total molecular gas
  mass (6.5x10^8 Msun), is more extended perpendicular to the Galactic plane. The fraction of diffuse gas increases from
  10-20% at a galactocentric radius of 3--4 kpc to 50% at 15 kpc, and increases with decreasing surface density." "Only
  14% of the molecular gas mass traced by 12CO emission is identified as part of molecular clouds in 13CO surveys by cloud
  identification algorithms." Sec. 4.4: masses integrated "between 3 kpc and 15 kpc"; "Statistical errors on integrated
  masses are 1%. Systematic uncertainties are 30% due to errors on the assumed abundances (13CO/12CO and 12CO/H2) and the
  possibly inaccurate assumption of pure LTE at low column densities, which systematically underestimates masses in the
  diffuse regime." `[verified: Roman-Duval et al. 2016, abstract, sec. 4.4]`.
- **Table 5, M(H₂)** (pdftotext layout, columns aligned by eye): diffuse 9.3 × 10⁷ inner / 6.0 × 10⁷ outer / 1.5 × 10⁸
  total; dense 4.6 × 10⁸ / 3.9 × 10⁷ / 4.9 × 10⁸; total 5.5 × 10⁸ / 9.9 × 10⁷ / 6.5 × 10⁸ — diffuse 17 % inner, 61 % outer
  `[inferred, divided by the reader]`. Sec. 4.5: the dense fraction against the face-on H₂ surface density in 100 pc
  pixels, "fDG = 0.02 Sigma^(0.24+-0.01)" (Σ in M☉ kpc⁻²; the symbol garbled in the text layer, the form and numbers
  legible), "<20--30%" at low Σ, "80-90%" at 10⁷ M☉ kpc⁻².
- **The paper's own caveats:** opacity-broadened ¹²CO wings of dense gas are counted as diffuse, "we may be
  overestimating the emission and mass of truly diffuse gas"; "at least 40% of the 'diffuse' gas mass fraction reported
  here in the outer Galaxy corresponds to truly diffuse gas"; "The fraction of diffuse gas scales linearly with the
  CO-to-H2 conversion factor assumed ... the diffuse gas fraction derived here represents a lower limit".
- **Miville-Deschênes et al. 2017**, arXiv:1610.05918 (abstract): "a catalog of 8107 molecular clouds" that "includes 98%
  of the 12CO emission observed within b +-5 deg"; "The total H2 mass in the catalog is 1.2x10^9 Msun" `[verified:
  Miville-Deschênes et al. 2017, abstract]`.
- **What it says** `[inferred]`: the two do not conflict in data but in what a cloud is — ¹²CO segmented into clouds
  (MD17) leaves ~2 % of the emission outside; the ¹³CO-detected split (RD16) leaves 25 % "diffuse" (a lower limit by X_CO,
  an upper limit by line wings, ±30 % systematic). RD16's global 25 % is under #94's ~30 % kill; its outer disc (50–61 %)
  is above it. The register's "Roman-Duval et al. 2016's own diffuse fraction `[recall — NEEDS SOURCING]`" is now read.
- **Not searched.** A completeness limit for the cloud mass function's lower end (the 10⁴ M☉ stays `[inferred]`).

### S96.2 #95 — Grasha et al. 2019: young clusters from their nearest cloud

- **Source.** Grasha et al. 2019, MNRAS 483, 4707, arXiv:1812.06109 (HTML; M 51 = NGC 5194, LEGUS class 1–2 clusters ×
  PAWS GMCs, 7.66 Mpc), sec. 4.1.1: "the median of the shortest distance for the closest star cluster-GMC pair is 87+-2
  parsec"; "the star clusters younger and older than 10 Myr exhibit median distances of 71+-3 pc and 107+-4 pc"; "star
  clusters that are younger than 10 Myr lie at distances twice the size of the cloud's radius whereas clusters older than
  10 Myr are found at median distances three times the size of the molecular cloud"; "The median radius of the GMC
  population in NGC 5194 is 36 parsec"; inside 2.7 kpc 66 ± 2 pc (young 59 ± 2, older 74 ± 4), outside 132 ± 6 (118 ± 9,
  143 ± 7) `[verified: Grasha et al. 2019, sec. 4.1.1]`. Sec. 4.1.2 (the fetch's paraphrase, not verbatim): median ages
  ~4 Myr within 1 R_GMC, 6 Myr at 1–2 R_GMC, 30 Myr at 2–3, 50 Myr unassociated. Abstract: "After ~6 Myr, the majority of
  the star clusters lose association with their molecular gas." Only medians are printed; the distributions are in
  figures, not tabulated (not read).
- **What it measures** `[inferred]`: a projected distance to the *nearest* cloud, not the parent — both biases shorten it,
  so 2 R_GMC (71 pc) for clusters under 10 Myr is a rough lower bound on a parent offset. The model draws the offset
  uniform over the cloud's volume (`cloud_texture.py`, size × ∛u): median 0.79 cloud radii, never beyond 1 (F-96B-1).
- **Zakardjian et al. 2023**, arXiv:2305.03650 (abstract only): 19 PHANGS galaxies, GMC–HII association by "spatial
  overlap" of footprints — an association, not an offset distribution. A PHANGS-JWST 21 µm paper (arXiv:2212.01526;
  80 pc median to the nearest GMC in NGC 628) is a search snippet: **NOT READ**.
- **Not searched.** A cloud's density gradient; a remnant shell's visible lifetime.

### S96.3 #181 — HII regions' sizes are the resolution's; the luminosity function at 67 pc

- **Groves et al. 2023**, MNRAS 520, 4902, arXiv:2301.03811 (abstract and HTML, the first 100k characters): 19
  PHANGS-MUSE discs, 30 790 nebulae, "A total of 23,244 nebulae (75%) are classified as HII regions". Sec. 4.2: "the size
  is taken as the circularized radius that results in an equal area to the area of the H ii region mask"; the authors
  "purposefully do not include size measurements in our catalogue"; "the vast majority of our regions are unresolved",
  "most of our regions are unresolved or only marginally resolved", "a median physical resolution of ~70 pc" (Table 1:
  23–104 pc); Table 3's median radii ~23 pc (NGC 5068) to ~83 pc (NGC 1512), 10th–90th percentiles ~19 to ~126 pc, with
  "the clear correlation with galaxy distance". "Most (80%) of the H ii regions we detect have L(Halpha) << 10^38 erg s-1",
  ~3 % (~800) "giant H ii regions" above 10³⁹; "typical completeness limits are 10^36 - 10^37 erg s-1" `[verified: Groves
  et al. 2023, sec. 4.2, Tables 1 and 3]`. **No size–luminosity relation is printed.**
- **Santoro et al. 2022**, A&A 658, A188, arXiv:2111.09362 (abstract): "about 23,000 HII regions detected at an average
  physical resolution of 67pc", 19 spirals; "The mean LF slope alpha in our sample is =1.73 with a sigma of 0.15"; "alpha
  decreases with the galaxy's star formation rate surface density" `[verified: Santoro et al. 2022, abstract]`. The fit
  range is not in the abstract (not read).
- **Hunt & Hirashita 2009**, arXiv:0910.2804 (abstract and ar5iv, the first 100k characters): extragalactic HII regions
  follow the Galactic size–density relation n ∝ D⁻¹ ("rather than a relation with constant luminosity") over "roughly six
  orders of magnitude"; densities and sizes "good to a factor of 2 or so"; ground-based sizes of giant regions shrink at
  HST resolution — M82-A ~450 pc to 4.5 pc, Mrk 71 ~560 pc to 14.4 pc (the fetch's paraphrase). No observed
  size–luminosity relation is stated (only the Strömgren N_ion ~ D³ n²).
- **Kennicutt 1984** (ApJ 287, 116): the ADS abstract page returned HTTP 405 — **UNREACHABLE**. A search snippet's "slope
  3.5" (log L – log D, arXiv:astro-ph/9412016, not fetched) is **NOT READ** and out of the record.
- **What it says** `[inferred]`: published HII-region sizes are set by the observations' resolution (PHANGS's regions
  "unresolved or only marginally resolved" at ~70 pc, their sizes tracking distance; the ground-based "giant" sizes
  collapsing 10–100× at HST resolution), so no physical size–luminosity relation for complexes is there to fix a merge
  level. What is measured at a stated resolution is the luminosity function: mean slope 1.73, σ 0.15 over 19 discs, at 67
  pc. NGC 604's "hundreds of pc" stays `[recall]`.

## Part S99 — the knots as regions measured: the census, Santoro et al.'s estimator, two merges and the merged radius (2026-11-12, BUILD_VI row 99; the measurer)

**The note.** S99's measurer (`s99_KP.md`; read and run only, no repository file changed, no test run) took the
census through `Service()` in memory, the production grid (400 rings, 0.037-29.96 kpc), `/api/clusters
template=<t>`, the layer on, the whole disc; positions in the plane (heights ignored: |z| median 37-38 pc, p99 ~180
pc); Hα in L☉ as published (erg/s = × 3.828 × 10³³). Scripts and logs in the session's scratchpad (`s99_KP_lf.py`,
`s99_KP_more.py`, `s99_KP_dump.py`). Santoro et al. 2022 was read at arxiv.org/html (Sects. 4.1 and 5)
`[verified: Santoro et al. 2022, place]`; `[inferred]` the measurer's own reading. The gate's ruling is D269 ruling 6.

### S99.1 The census as it is

| | `milky_way` | `ngc_4414` |
|---|---|---|
| HII regions (every cluster has L_Hα > 0) | 13 124 | 7 632 |
| L_Hα, L☉: median / p90 / p99 / max | 191 / 5.69e3 / 4.81e4 / 4.75e5 | 100 / 3.82e3 / 3.06e4 / 7.40e5 |
| Strömgren radius, pc: median / p90 / p99 / max | 0.77 / 2.92 / 7.67 / 25.7 | 0.54 / 2.63 / 6.85 / 24.6 |
| density-bounded regions | 0 | 0 |
| row 35 (binned, L ≥ 10³⁷ erg/s), unmerged | −2.049 (inside −2.5…−1.5) | −1.975 |
| Santoro's MLE + KS floor, unmerged | 1.832 ± 0.016 (L_min 8.3e36) — inside 1.73 ± 0.15 | 1.467 ± 0.008 (L_min 3.8e35) — outside |
| MLE at a fixed floor 10³⁷, unmerged | 1.871 ± 0.018 (inside, at the edge) | 1.911 ± 0.029 (outside, at the edge) |
| the frame's pixel (`captures.json`) | 39.06 pc | 29.30 pc (major axis) |

The register's 12 710 regions on `milky_way` were S67's; on S99's model (#227's layer built) 13 124. Above 10³⁷ erg/s:
2 331 (the Milky Way) and 975 (NGC 4414). The electron density the radius is formed in (the host cloud's ⟨n²⟩^½):
median 154 / 174 cm⁻³, p90 541 / 686, max 767. **The model's luminosity function is curved, not a power law**: the
continuous MLE slope at a fixed floor runs on the Milky Way 1.34 (10³⁵ erg/s), 1.50 (10³⁶), 1.62 (3 × 10³⁶), 1.87
(10³⁷), 2.05 (3 × 10³⁷), 2.22 (10³⁸); on NGC 4414 1.37, 1.53, 1.65, 1.91, 2.19, 2.23.

### S99.2 Santoro et al. 2022's estimator, as quoted

- The form, a PDF: "p(L) = (alpha-1) L_min^(alpha-1) L^(-alpha)" for L ≥ L_min (Sect. 4.1).
- Not binned: binned least squares "can give incorrect results under relatively common conditions"; the MLE "does not
  depend on any binning scheme"; the python `powerlaw` package, which "follows the prescription given in Clauset et al.
  (2009)".
- L_min: an "MLE fit by recursively fixing L_min equal to each empirical data point", the model kept "the one that
  minimizes the KS statistic", the search limited to "an interval of +-1 sigma around the median of the distribution";
  per galaxy, on extinction-corrected Hα. Slopes "in the interval of alpha=1.5-2 with a mean value of 1.73 and a sigma
  of 0.15"; resolution 67 pc (abstract), "about 70 pc" (Sect. 1).
- Sect. 5: blending "will cause nearby H ii regions to blend and be detected as a single H ii region, leading to a
  flattening of the LF"; L_min is "driven by resolution of the observations".
- Their α is positive (dN/dL ∝ L^−α); row 35 publishes the exponent, negative.
- **The measurer's implementation** `[inferred]`: the continuous Clauset MLE α = 1 + n / Σ ln(L / L_min), error (α −
  1) / √n, the KS distance over the tail, L_min over the data points within the median ± 1 std of log₁₀ L (the
  measurer's reading of "the distribution"; `powerlaw` is not in the environment and nothing was installed).
- **The caveat that decides the comparison**: Santoro's window sits where their catalogue's completeness puts it
  (completeness 10³⁶-10³⁷ erg/s, Groves et al. 2023); the model's census is complete to ~10³³, so the same rule
  searches 6.5 × 10³⁴-8 × 10³⁶ (the Milky Way) and 2.7 × 10³⁴-5.5 × 10³⁶ (NGC 4414), where the model's function is
  flatter. **The estimator transplanted to a complete synthetic census is not the same test.**

### S99.3 The two merges

(a) **A square lattice of 67 pc** in the plane, origin at the centre and shifted by half a cell (33.5 pc):

| | `milky_way` (origin / shifted) | `ngc_4414` (origin / shifted) |
|---|---|---|
| complexes | 10 570 / 10 587 | 6 142 / 6 164 |
| Hα share in multi-region complexes | 0.165 / 0.130 | 0.108 / 0.128 |
| Santoro MLE + KS | 1.900 / 1.896 — outside | 1.450 / 1.462 — outside |
| MLE at 10³⁷; row 35 | 1.864 / 1.858; −2.050 / −2.049 | 1.911 / 1.911; −1.976 / −1.977 |

On the Milky Way multiplicity 1: 9 055, 2: 1 051, 3-4: 340, 5-9: 109, 10-29: 15; the extent of multi-region complexes
median 55 pc, max 146-156. The origin moves α by ≤ 0.012 and the Hα share by 3.5 points.

(b) **Friends-of-friends in the plane**, linking 60 / 70 / 80 pc:

| | `milky_way` | `ngc_4414` |
|---|---|---|
| complexes | 8 607 / 8 045 / 7 522 | 4 951 / 4 636 / 4 390 |
| Hα share in multi-region complexes | 0.292 / 0.333 / 0.365 | 0.234 / 0.284 / 0.310 |
| largest complex (regions, 2 r_max) | 144, 682 pc / 181, 931 pc / 322, 1753 pc | 55, 703 / 56, 659 / 99, 870 pc |
| Santoro MLE + KS | 1.956 / 1.954 / 1.940 — outside | 1.952 / 1.999 / 2.006 — outside |
| MLE at 10³⁷; row 35 | 1.830 / 1.814 / 1.802; −2.034 / −2.025 / −2.013 | 1.905 / 1.907 / 1.901; −1.977 / −1.973 / −1.973 |

**It percolates**: on the Milky Way the largest complex at 70 pc holds 181 regions over 931 pc (R 0.20-0.91 kpc,
109° of azimuth), at 80 pc 322 regions over 1.75 kpc, a ring round the centre; outside 1.5 kpc the largest at 70 pc is
114 regions, 805 pc along R 2.05-2.38 kpc. The nearest-neighbour separation is 59 pc (the Milky Way) and 57 pc (NGC
4414) at the median; 52 % of regions lie within 70 pc of another.

**What the merges do to the test**: at a fixed floor every merge flattens the slope (as Santoro's Sect. 5 says blending
does) by 0.04-0.07 on the Milky Way and ~0.01 on NGC 4414; with the KS-chosen floor it steepens, because the merged
census's median moves up and the window with it. **No merge moves the slope by more than 0.07 at a fixed floor, while
the floor alone moves it from 1.3 to 2.2; under Santoro's floor rule the unmerged Milky Way passes (1.83) and every
merge fails (1.90-1.96), NGC 4414 fails unmerged (1.47) and merged (1.45-2.01). The test cannot tell a merge from
none.** Row 35 stays inside its window under every merge.

### S99.4 The merged region's radius

`nebular.materialise_nebular` forms R_S from Q_trapped = (1 − 0.30) Q = α_B ⟨n²⟩ (4/3) π R³, ⟨n²⟩ = e^{σ_s²} ⟨n⟩²,
⟨n⟩ the host cloud's mean, capped at the cloud's size. For a complex the measurer took the members' summed Q, trapped by
the same 0.30 escape, in the brightest member's ⟨n²⟩ and α_B at its T_e, uncapped (the cap would only lower it):

| friends-of-friends 70 pc | median | p90 | p99 | max |
|---|---|---|---|---|
| `milky_way`, pc | 1.11 | 3.72 | 9.41 | 25.7 |
| `ngc_4414`, pc | 0.96 | 3.41 | 8.73 | 24.6 |

The lattice and the other lengths alike (the Milky Way's lattice median 0.93, max 25.7); the volume-sum radius gives the
same to 1 %. **Over half a pixel** (19.5 pc, 14.6 pc): 7 complexes on the Milky Way and 11-12 on NGC 4414 under every
rule — the same handful as unmerged (7 and 11); over a whole pixel, none. The sphere of the sum spans its members in
5-8 of 1 500-1 800 multi-region complexes on the Milky Way and none of ~900 on NGC 4414: a complex's members lie 55-100
pc apart, its ionized volume a few pc — **the merged "region" is not one ionized volume in the model's gas**. Drawn at
the 67 pc resolution element (≥ 1.7 px) every complex would be a disc: a size the catalogue's telescope sets, not the
model (D5).

### S99.5 Hunt & Hirashita 2009 — the page not reached

One fetch was allowed (arxiv.org/abs/0910.2804): it returned the abstract only — the measurer's choice of URL. So the
normalisation, the scatter and the sample of the size-density relation stay **NOT READ**. The abstract: extragalactic
regions "follow the same size (D)--density (n) relation as Galactic ones", which "reflects a sequence with different
initial gas densities". From the form alone `[inferred: the measurer's arithmetic]`, with n = k / D the diameter is
D = 6 Q / (π α_B k²), linear in Q: across the friends-of-friends census (the Milky Way's merged L median 495, p99 8.05
× 10⁴, max 4.75 × 10⁵ L☉) diameters would span 1 : 163 : 960 for any k — a median complex of 1 pc puts the brightest
at ~1 kpc. A build would need the printed k with its scatter from the paper's body, a statement of which sizes
(HST-resolved, not ground-based blends) it rests on, and a rule replacing the cloud's density in
`materialise_nebular` — a change of the region's physics, not of the knot's drawing.

### S99.6 What the viewer would have to change (read only)

Today one knot is one cluster row of `/api/clusters` (`api/v6_knots.py`: the light column `hii_halpha_luminosity`, the
header's size `hii_stromgren_radius`, rule R5 the level-0 cell closure); `frontend/src/galaxy/plummer.ts` draws a point
(the sprite, or the instrument's PSF) until 2 × extent reaches the pixel's side, then a light-conserving disc. For a
complex to be one knot the API must serve complex rows (summed `line_response` and L, a centroid, a size column, one
naming cell per complex) — a grouping step after `materialise_nebular`; a friends-of-friends or a Cartesian lattice
crosses the level-0 cells the census is drawn by, so a complex would depend on its neighbours' draws (D60's "a region
alone is its slice" breaks unless the merge is confined to a cell). `knots.ts`, `plummer.ts`'s disc path, FluxPoints
and the header-named size column would not change.

### S99.7 What the numbers support, and the gate's ruling

The measurer: (i) the merge as the model's catalogue, tested by the luminosity function and drawn at the physical
radius — the test cannot rule on it, and at a 39 pc pixel the merge draws **fewer, brighter points** (the Milky Way at
70 pc: 8 045 knots instead of 13 124, median L 495 against 191 L☉, a third of the Hα moved to centroids) and no new
size; what would visibly change is the bloom, a display effect. (ii) **Permanent**: the knots stay one Strömgren
sphere each; at a 39 pc pixel nothing visible changes from today. The numbers support (ii) for the size.
**The gate's ruling (D269 ruling 6): #181 permanent, on the measurement** (the entry's own named alternative, S96).
What stands between the model and the goal pictures' pink regions is the density the photons see: **#232** opened
(carried) — the regions' sizes are set in the cloud's clumped gas (150-770 cm⁻³); the reading owed is a size-density
relation's normalisation (Hunt & Hirashita 2009, the page not reached at S99).

**Not done** (the measurer): no repository file changed, no test run, no bundle or frame touched; heights ignored in
the merges; no extinction applied to L (Santoro et al. correct theirs; the model's L is intrinsic).
