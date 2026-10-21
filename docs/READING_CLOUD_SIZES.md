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
