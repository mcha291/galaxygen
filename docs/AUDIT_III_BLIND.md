<!-- Audit III (S37, D186): the blind reading of rows 32 and 34, by a read-only agent forbidden the repository, copied verbatim from the S37 scratchpad at S42 so the rows can cite it (the owner adopted both windows on 2026-09-27). -->

# Audit III - blind reading: GC-system stellar mass and the Galaxy's Q(H0)

Set from the sources only, without seeing the model or the repository. No file in the project was opened or searched.
Labels: READ = I read the sentence or number in the primary text myself; READ second-hand = I read it quoted in another paper; NOT READ = from memory or inferred, not checked.

---

## Target A - total stellar mass of the Milky Way globular-cluster system

### Adopted target

- **M/L_V = 1.9 (range 1.6 to 2.2)**, applied to the Harris (2010 edition) summed V luminosity of 1.72e7 L_sun.
- **Central value about 3.3e7 M_sun. Window [2.7e7, 4.0e7] M_sun.**

### Luminosity sum (computed here)

I read the catalogue directly from https://physics.mcmaster.ca/~harris/mwgc.dat, Part II, column (8) "Absolute visual magnitude (cluster luminosity), M_V,t = V_t - (m-M)V". The catalogue header says the file covers "157 objects classified as globular clusters". (READ)

- 156 clusters have M_V,t. GLIMPSE02 has none.
- With M_V,sun = 4.81, the sum of L_V = 10^(-0.4 (M_V,t - 4.81)) is **1.716e7 L_sun**.
  - With M_V,sun = 4.83 the sum is 1.748e7 (+1.9%).
  - Omega Cen (NGC 5139, M_V = -10.26) is 1.067e6 L_sun, 6.2% of the total. Without it the sum is 1.610e7.
  - Split by [Fe/H]:

    | [Fe/H] | Clusters | L_V (L_sun) | Share |
    |---|---|---|---|
    | <= -1 | 106 | 1.288e7 | 75% |
    | > -1 | 45 | 4.21e6 | 24.5% |
    | none listed | 5 | 7.5e4 | about 0.4% |

  - Clusters fainter than M_V = -5 add only 8.4e4 L_sun in total, so faint missing clusters barely matter. Missing massive clusters hidden behind the bulge would matter; that incompleteness is plausibly 0 to +10% (NOT READ; my judgement).
- (m-M)_V is the apparent visual modulus, so M_V,t is already corrected for extinction (READ, catalogue key to columns).

### M/L sources (what each says)

1. **Bland-Hawthorn & Gerhard 2016, section 6.1.2** (READ, arXiv:1602.07702 PDF text): "With a mass-to-light ratio M/LV = 1.4 +/- 0.5 for metal-poor Galactic globular clusters (Kimmig et al. 2015), the ..."
   - This value is used there to convert halo BHB counts to mass. It is not a system-wide GC value.
   - Kimmig et al. 2015 (AJ 149, 53) covers 25 clusters, central (virial) dispersions. The search-result summary says "lower than expected M/Ls for the metal-rich clusters" (READ second-hand, search snippet; the paper itself was NOT READ).
2. **Harris notes, mwgc.ref** (READ): "A mean stellar mass of (1/3) M_sun and a mean mass to light ratio of M/L = 2 are assumed here for purposes of this calculation" (the relaxation-time calculation). This is an assumption, not a measurement.
3. **Baumgardt & Hilker 2018** (READ, arXiv:1804.08359):
   - The abstract states 112 clusters but gives no mean M/L.
   - The text says: "The M/L ratios do not show a significant correlation with any of the other cluster parameters."
   - I computed statistics from their Table 2 (Mass, M/L_V columns), parsed from the arXiv PDF:

     | Statistic (112 clusters) | Value |
     |---|---|
     | Unweighted mean M/L_V | 2.36 (pulled up by low-mass outliers, e.g. Pal 13 10.7, Arp 2 10.0, E3 8.1) |
     | Median | 2.04 |
     | Mass-weighted (sum M / sum L_implied) | **1.98** |
     | Sum of dynamical masses | **3.23e7 M_sun** |

   - Matching their masses by name to Harris L (111 matched): sum M / sum L_Harris = **2.07**.
   - The 45 Harris clusters that are not in BH18 carry L = 1.59e6 L_sun.
4. **Baumgardt, Sollima & Hilker 2020, PASA** (arXiv:2009.09611; READ, section 3.3): "We obtain an average mass-to-light ratio of M/LV = 1.83 +/- 0.03 M_sun/L_sun and a standard deviation of M/L = 0.24 +/- 0.03 M_sun/L_sun around the mean using our magnitudes compared to M/LV = 1.92 +/- 0.05 M_sun/L_sun and M/L = 0.49 +/- 0.05 M_sun/L_sun that we derive from the literature magnitudes."
   - The abstract (READ) says: "absolute mass-to-light ratios that are confined to the narrow range 1.4<M/L_V<2.5".
   - Their Table 1 (READ) gives a mean offset of +0.03 mag from Harris (2010) for V < 8. For bright clusters the Harris magnitudes are therefore on their scale to a few percent.
5. **McLaughlin & van der Marel 2005** (READ, astro-ph/0605132 text):
   - Population-synthesis M/L_V comes from Bruzual & Charlot 2003 with a Chabrier disk IMF, at an assumed age of 13 +/- 2 Gyr.
   - On dynamical versus population values: "the median Vdyn/Vpop = 0.82, which has a standard error of +/- 0.07".
   - The typical population-synthesis value for old metal-poor GCs, about 1.8 to 2.0, is NOT READ (memory). I did not extract Table 8.

### Why M/L_V = 1.9

- It is the measured system-wide dynamical mean.
  - BSH20 gives 1.83 on their own magnitudes and 1.92 on literature magnitudes. The Harris magnitudes are literature magnitudes, so 1.92 is the consistent pairing with a Harris luminosity sum.
  - The BH18 mass-weighted value is 1.98.
- It lies inside the population-synthesis expectation after MvdM05's dyn/pop factor of 0.82 (NOT READ for the absolute value).
- I do not adopt Kimmig's 1.4:
  - It is quoted in BHG16 for metal-poor clusters only.
  - It comes from 25 clusters' central dispersions.
  - BSH20 show that literature-magnitude scatter inflated older per-cluster M/L values.
- Harris's M/L = 2 is an assumption made for a timescale, not a measurement.

### Resulting numbers (sum L_V = 1.716e7 L_sun unless noted)

| M/L_V adopted | Source | Total mass (M_sun) |
|---|---|---|
| 1.4 (+/- 0.5) | Kimmig 2015 via BHG16 | 2.40e7 (1.54e7 to 3.26e7) |
| 1.6 | window low edge (1.83 - 1 sigma scatter) | 2.75e7 |
| 1.83 | BSH20, own magnitudes | 3.14e7 |
| 1.92 | BSH20, literature magnitudes | 3.30e7 |
| 1.98 | BH18 mass-weighted | 3.40e7 |
| 2.0 | Harris assumption | 3.43e7 |
| 2.07 | BH18 masses / Harris L, 111 matched | 3.55e7 |
| hybrid | BH18 masses (3.23e7) + 45 others x 1.83 to 2.07 | 3.52e7 to 3.56e7 |
| 2.2 | window high edge | 3.78e7 |
| 2.36 | BH18 unweighted mean (not appropriate) | 4.05e7 |

### What moves the window, and by how much

| Choice | Effect |
|---|---|
| M/L (dominant) | Each 0.1 in M/L_V is 1.7e6 M_sun (about 5%) |
| Kimmig instead of BSH20 | -27% |
| M_V,sun 4.83 instead of 4.81 | +1.9% |
| Dropping Omega Cen (stripped nucleus?) | -6.2% |
| Undiscovered or obscured clusters | plausibly 0 to +10% (my judgement) |
| Metal-rich 24.5% of light at a different M/L | +/-0.3 on that quarter is +/-4% on the total |
| Harris vs BSH20 magnitude scale | a few percent |
| "Stellar mass" including remnants | Dynamical masses include white dwarfs and neutron stars. A model that counts only luminous stars would sit lower. |

**Window [2.7e7, 4.0e7].** It covers M/L 1.6 to 2.2 on the Harris sum, the BH18 direct-mass hybrid (3.55e7), and +10% incompleteness at the upper end. Kimmig's central value (2.40e7) lies outside, below it.

---

## Target B - Galaxy's intrinsic hydrogen-ionizing photon rate Q(H0)

### Adopted target

- **McKee & Williams 1997: Q = (2.6 +/- 1.3)e53 photons/s. Window [1.3e53, 3.9e53].**

### What each candidate is (sentences and locations)

- **Chomiuk & Povich 2011, section 3.1** (READ, arXiv:1110.4105 PDF text):
  - "Bennett et al. (1994) used Cosmic Background Explorer (COBE) observations of N II 205 um emission to measure the rate of Lyman continuum photons in the Milky Way, and correcting for dust absorption and photon escape, they found Nc = (3.5 +/- 1.8) x 10^53 phot s-1. Subsequently, McKee & Williams (1997) used the same COBE data and slightly different assumptions to measure a Lyman continuum photon rate of Nc = (2.6 +/- 1.3) x 10^53 phot s-1."
  - "Gusten & Mezger (1982) ... taking into account the thermal radio emission from 'extended low-density' H II regions and including Lyman continuum photons escaping from giant H II regions. They measured Nc = (2.7 +/- 0.8) x 10^53 phot s-1".
  - "Mezger (1987) calculated a slightly lower value ... Nc = (2.1 +/- 0.6) x 10^53 phot s-1, discrepant from their earlier value due to their use of R = 8.5 kpc for the distance to the Galactic center (as opposed to R = 10 kpc used by Gusten & Mezger 1982)."
  - "Murray & Rahman (2010) used ... WMAP observations of free-free emission to measure a dust-corrected Lyman continuum photon rate of Nc = 3.2 x 10^53 phot s-1."
  - "The COBE and WMAP studies utilize the integrated light of the Milky Way and average over its entire stellar population".
  - Section 5 discussion: Murray & Rahman "multiply their measured Nc by two to correct for distant H II regions missing from their catalog; ... multiply by 1.5 to account for the diffuse component ...; and ... multiply by 1.37 to correct for Lyman continuum escape and absorption by dust (detail given in McKee & Williams 1997)".
- **Bennett et al. 1994** (ApJ 434, 587): the abstract gives about 3.5e53 photons/s from N+ (READ second-hand, via a Semantic Scholar abstract that the fetch tool paraphrased). The +/-1.8 and "correcting for dust absorption and photon escape" are READ second-hand via Chomiuk & Povich.
- **McKee & Williams 1997** (ApJ 476, 144): abstract read partly via the IOPscience page (READ):
  - "Allowing for the ionizing radiation that is absorbed by dust (about 25% of the total), we find that the maximum ionizing photon luminosity of a Galactic OB association is S_u = 4.9 x 10^51 photons s^-1".
  - "The total ionizing luminosity of this distribution of OB associations can account for the thermal radio emission and the N II far-infrared emission of the Galaxy."
  - From Higdon & Lingenfelter 2013 (arXiv:1302.1223; READ second-hand): "Based on analyses of thermal radio emissions and a published study (Bennett et al. 1994) of FIRAS N II far infrared line emissions, McKee & Williams estimate a total Galactic ionization rate, QG0, of 1.9x10^53 s-1. However, based on their prescription this value should decrease by a factor, (Rs/8.5)^2 ~ 0.8, due the decrease in the distance of the Sun from the Galactic Center".
  - So MW97 have about 1.9e53 photons absorbed by gas, times the 1.37 correction (dust plus escape), giving 2.6e53 intrinsic. This decomposition is inferred from the two second-hand sentences; the MW97 body was NOT READ.
- **Murray & Rahman 2010** (arXiv:0906.1026): abstract READ: "The total dust-corrected ionizing photon luminosity is Q=3.2x10^{53} photons/s, in good agreement with previous estimates." No uncertainty is given.
- **Gusten & Mezger 1982; Mezger 1987**: NOT READ in the originals; both READ second-hand via Chomiuk & Povich as above.

### Why McKee & Williams 1997

- It is the whole-Galaxy intrinsic rate. It is built from both independent Galaxy-wide tracers: thermal radio (free-free) and COBE [N II] 205 um.
- It states its corrections explicitly: dust about 25% of the total, plus escape. It supplies the 1.37 correction factor that Murray & Rahman later borrowed.
- Bennett 1994 is the primary [N II] measurement, but its conversion from [N II] to Q rests on assumptions (N+/N, n_e) that MW97 revisited. Both quote about +/-50%, and they agree within errors.
- Murray & Rahman 2010 is an independent primary dataset, but:
  - it carries three multiplicative corrections (x2 incompleteness, x1.5 diffuse, x1.37), a total factor of 4.1;
  - it quotes no uncertainty.
- Gusten & Mezger 1982 and Mezger 1987 count radio H II regions plus ELD emission, and their Q scales with R0 squared. GM82 used R0 = 10 kpc. They are older and less complete in their treatment of the diffuse and escaping photons.

### Windows the other candidates would give

| Source | Quoted Q (1e53 photons/s) | 1-sigma window (1e53 photons/s) |
|---|---|---|
| Bennett 1994 | 3.5 +/- 1.8 | [1.7, 5.3] |
| **McKee & Williams 1997 (adopted)** | **2.6 +/- 1.3** | **[1.3, 3.9]** |
| Murray & Rahman 2010 | 3.2, no error | Assigning the same 50% as the COBE work gives [1.6, 4.8]. Holding the three correction factors fixed, a 2x incompleteness uncertainty alone spans roughly [1.6, 3.2]. |
| Gusten & Mezger 1982 | 2.7 +/- 0.8 | [1.9, 3.5] |
| Mezger 1987 | 2.1 +/- 0.6 | [1.5, 2.7] |

Rescaling to R0 = 8.2 kpc with Q proportional to R0^2 (my arithmetic; R0 = 8.2 from BHG16, READ):

| Source | Assumed R0 | Rescaled Q (1e53 photons/s) |
|---|---|---|
| GM82 | 10 kpc (read second-hand) | 1.8 |
| Mezger 1987 | 8.5 kpc (read second-hand) | 1.95 |
| MW97 | 8.5 kpc (assumed from the H&L sentence) | 2.4 +/- 1.2, window [1.2, 3.6] |

All five overlap in 1.9e53 to 2.7e53.

---

## Summary for the auditor

- **A:** M/L_V 1.9 (BSH20), sum L_V = 1.716e7 L_sun (Harris 2010, 156 clusters, M_V,sun = 4.81). **Window [2.7e7, 4.0e7] M_sun**, centre 3.3e7.
- **B:** McKee & Williams 1997, (2.6 +/- 1.3)e53 photons/s, intrinsic and Galaxy-wide. **Window [1.3e53, 3.9e53].**
