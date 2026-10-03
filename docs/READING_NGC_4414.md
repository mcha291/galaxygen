# READING_NGC_4414 — the measured properties of NGC 4414 and the blind windows (S54, BUILD_III Phase T)

**The lead's note (2026-10-03).** One Opus reader, briefed by BUILD_III §3e and forbidden the repository, wrote
everything below the rule; it is entered as written. The windows were fixed before any model output for this
galaxy existed (D113) and are not widened afterwards. What the lead chose from it — the three fit targets, the
five checks, the camera — is D213's, written before the fit was run. The windows D213 does not use (HI and H₂
apart, the outer speed, the face-on M_B, the infrared luminosity, the bulge) stay blind until a session prints
the model's number against them.

---

## The reader's note

Read 2026-10-03 on fetched pages only (arXiv HTML, VizieR/CDS tables and ReadMe files, the HyperLeda object page, one IOP abstract). Nothing under the galaxygen repository was opened; no model output informed any window. Every number below was read on the page named by its source key; keys expand to full `[verified: …]` tags in section 2. Numbers I computed from read numbers are marked **(derived)** with the arithmetic shown. Recalled numbers are tagged `[recall — NOT READ]` and appear in no table and no window.

**Adopted distance for every window: D = 17.7 Mpc (μ = 31.24), Cepheid, HST Key Project final value [F01].** 1″ = 85.81 pc **(derived:** 17.7e6 pc × 4.8481e-6**)**. Distance bracket used as the systematic in every distance-dependent window: the three Cepheid values read, **16.6 – 17.7 – 19.1 Mpc** (μ = 31.10 / 31.24 / 31.41), i.e. lengths and dynamical masses ×0.938 / ×1.079, luminosities and flux-based masses ×0.880 / ×1.164 (−0.056 / +0.066 dex), magnitudes +0.14 / −0.17.

## 1. Summary table (read numbers only)

| # | Property | Value (as read) | Uncertainty (as read) | Window at 17.7 Mpc | Distance the source assumed | Source | Coverage | Model quantity compared |
|---|---|---|---|---|---|---|---|---|
| 1 | Distance modulus (Cepheid, metallicity-corrected) | 31.24 → 17.70 Mpc | ±0.05 random; systematic budget 0.10 mag | not a check (16.6–19.1 Mpc bracket) | — | F01 Table 4; GC22 Table 4 | one galaxy, one method, 8–9 Cepheids | — |
| 2 | Inclination | 52.3° (HI), 52° (HI), 55° (CO+HI), 56.6° (HyperLeda), 57.2° (3.6 µm outer isophote, derived) | ±1.5, ±4, ±2 | camera: **[52, 57]°** | none | dB14, P16, W04, HL, S4G-P4 | disc inside 240″ | camera only |
| 3 | Position angle | 155 (RC3), 157, 159±2, 159.6±1.2, 160±2, 162.3 | as shown | camera: **[156, 162]°** | none | RC3, V02, W04, S4G-P4, P16, HL | — | camera only |
| 4 | Peak rotation speed V_max (inner, peak "at about 35″" = 3.0 kpc) | 237 km/s | ±10 (i = 52 ± 4) | **[222, 247] km/s** | none | P16 Table 5; V02 §4.2 for the radius | HI, 30″ beam, tilted rings, WSRT/HALOGAS | v_c at R ≈ 3 kpc (or the curve's maximum) |
| 5 | Outer flat rotation speed V_flat (R = 240–480″ = 20.6–41.2 kpc) | 185 km/s; 184 km/s | ±10 | **[170, 202] km/s** | none | P16 Table 5; dB14 §3.2 | warped, disturbed outer HI disc; i held at 52.3° | v_c at R = 21–41 kpc |
| 6 | Rotation-curve shape S = V_flat / V_max | 0.78 (derived) | ±0.054 (derived) | **[0.71, 0.86]** | none | P16 Table 5 | same data as rows 4–5 | v_c(21–41 kpc) / max v_c(R < 21 kpc) |
| 7 | Stellar disc scale length, 3.6 µm, inner disc (R < 95″) | 19.22″; segments 18.72″ and 20.48″ | not given | **[1.5, 1.9] kpc** (18.7–20.5″) | angular | S4G-P4 table7; Wat19 table4 | 3.6 µm, disc + nucleus fit, quality 5 | stellar disc scale length by mass |
| 8 | Stellar mass | log M* = 10.65 | ±0.10 dex (excl. distance) | **[3.4, 5.9] ×10¹⁰ M☉** | 17.7 | z0MGS table4 | whole galaxy, WISE 3.4 µm × Υ = 0.36, Kroupa-type IMF | total stellar mass (disc + bulge) |
| 9 | HI mass | 4.5e9 M☉ (60.4 Jy km/s); 5.43e9 (GBT map) | ±0.27e9 (GBT) | **[3.8, 6.3] ×10⁹ M☉** | 17.8 | dB14 §2.1; Pin18 §4.4 | whole HI disc to R ≈ 480″ | atomic hydrogen mass (no He) |
| 10 | H₂ mass | 7.02e9 M☉ (2453 Jy km/s) | ±0.81e9 formal, ±15 % calibration | **[3.6, 8.4] ×10⁹ M☉** | 19.1 | H03 Table 4 | 6′ square (1.67 D25), X_CO = 2e20, no He | molecular hydrogen mass (no He) |
| 11 | Star formation rate | log SFR = 0.46 (2.88 M☉/yr) | ±0.20 dex | **[1.8, 4.7] M☉/yr** | 17.7 | z0MGS table4 | whole galaxy, FUV + WISE 22 µm, Kroupa & Weidner IMF | total SFR |
| 12 | K_s total magnitude (observed; nearly dust-free band) | 6.939; 6.98 | ±0.010; ±0.04 | M_K ∈ **[−24.62, −24.12]** (Vega) | — | 2MRS/MK06; HL | 2MASS extrapolated total | dust-free M_K |
| 13 | B total, corrected to face-on (B_T⁰) | 10.62 (RC3); 10.49 (HyperLeda btc) | B_T ±0.13; bt ±0.07 | M_B(face-on, attenuated) ∈ **[−20.96, −20.43]** | — | RC3; HL | whole galaxy; Galactic + inclination correction, NOT dust-free | dust-attenuated face-on B frame |
| 14 | (B−V) total, corrected to face-on | 0.77 (RC3 (B−V)_T⁰) = 0.77 (HyperLeda bvtc) | observed 0.84 ±0.01 (RC3) vs 0.79 (HL) | **[0.72, 0.82]** | none | RC3; HL | whole galaxy; Galactic + inclination correction, NOT dust-free | attenuated face-on B − V (not the stars-alone colour) |
| 15 | Infrared luminosity L(8–1000 µm) | log L = 10.56 L☉ | not given | **[10.48, 10.65]** | 17.68 | San03 table1 | IRAS four-band formula, whole galaxy | infrared (dust) luminosity |
| 16 | Morphology | SA(rs)c? (RC3); SA(rs)bc / SA(s)c, arm class F (3.6 µm); Elmegreen arm class 3 | — | no bar; flocculent | — | RC3, H03 Table 1, Buta15 | — | bar (model always has one — mismatch), arms |
| 17 | Bulge / nucleus | 4.2 % of 3.6 µm light in an unresolved nucleus, no bulge component; dynamical nuclear components 6.5e9 M☉ | — | named alternative: **[1.4, 6.5] ×10⁹ M☉** | angular; 19.2 | S4G-P4 table7; V02 Table 7 | 3.6 µm light; mass model R < 0.4 kpc | bulge mass |

## 2. Per-source notes

**F01** `[verified: Freedman et al. 2001, ApJ 553, 47, arXiv:astro-ph/0012376, Tables 3 and 4, https://arxiv.org/html/astro-ph/0012376]` — the Key Project final paper. Table 4 row NGC 4414: μ_V = 31.48 ± 0.14, μ_I = 31.33 ± 0.10, E(V−I) = 0.15 ± 0.04, μ₀ = 31.10 ± 0.05, D₀ = 16.60 Mpc, **μ_Z = 31.24, D_Z = 17.70 Mpc**, 12+log(O/H) = 9.20 ± 0.15 (the Cepheid field's abundance; the table's Z column). Table 3: μ_old = 31.37 ± 0.09 (9 Cepheids), revised 31.18 ± 0.09, period-cut 31.10 ± 0.05 (8 Cepheids). Text: the bias correction for NGC 4414 is "as large as … −0.08 mag". Coverage: one galaxy, one method; LMC modulus 18.50 assumed.

**T98** `[verified: Turner et al. 1998, ApJ 505, 207, abstract, https://iopscience.iop.org/article/10.1086/306150]` — read through a summarising fetch (abstract only): distance modulus 31.41 ± 0.17 (random) ± 0.16 (systematic), 19.1 ± 1.5 ± 1.4 Mpc; 11 Cepheids, periods 19–70 d. The body, the reddening and the galaxy parameters were not read.

**GC22** `[verified: Gallego-Cano et al. 2022, arXiv:2204.10668, Sect. 3.2 and Appendix A Table 4, https://ar5iv.labs.arxiv.org/html/2204.10668]` — H₀ from SN 1974G and SN 2021J in NGC 4414. Adopts μ = 31.24 ± 0.05 (stat) from F01; systematic budget in mag: LMC zero point 0.026, WFPC2 zero point 0.022, reddening 0.022, metallicity 0.087, PL bias 0.022, crowding 0.022 → **0.101 mag (derived quadrature)**. States that no TRGB distance is possible from archival HST data. The latest revision found: none replaces the Cepheid value.

**dB14** `[verified: de Blok et al. 2014, A&A (HALOGAS), arXiv:1405.2160, Sect. 1, Table 1, Sects. 2.1, 3.1.1, 3.2, 5, https://ar5iv.labs.arxiv.org/html/1405.2160]` — deep WSRT HI (10 × 12 h; tapered beam 39.0″ × 33.5″, 4.12 km/s channels). Adopted D = 17.8 Mpc. Total flux 60.4 Jy km/s → M_HI = 4.5e9 M☉; quotes Braine et al. 1993 as 64.9 Jy km/s = 4.8e9 M☉ at the same distance. W20 = 391, W50 = 333 km/s (not corrected for channel width). Inner disc = R < 240″, holds 3.3e9 M☉ (72 %); outer disc 240″ < R < 480″ (diameters 41.5 and 83.0 kpc at 17.8 Mpc). Tilted rings (30″ wide): V_sys = 711.5 ± 4.6; **constant i = 52.3° ± 1.5°** (receding 52.7 ± 1.3, approaching 52.4 ± 2.5); PA ≃ 155° at the centre, ~161° at R ~ 125″, ~155° at 240″. Shape, verbatim: "the sharp rise in the center followed by the gentle decline out to R ∼ 240″"; approaching and receding curves differ by +0.1 ± 13.4 km/s. Outer disc modelled with an assumed flat curve at **184 km/s**, i = 52.3°, a U-shaped warp, a centre shift of 71″ and a −20 km/s radial term. **The rotation curve itself is only a figure (Fig. 7): no tabulated v(R) was readable.** Table 1 (copied from Heald 2011, 2012): SAc, i = 50°, D25 = 4.5′, M_B = −19.12, V_rot = 224.7 km/s, SFR = 4.2 M☉/yr.

**P16** `[verified: Ponomareva, Verheijen & Bosma 2016, MNRAS 463, 4052, arXiv:1609.00378, Tables 1, 4, 5, 6 and the notes on individual galaxies, https://arxiv.org/html/1609.00378]` — uniform re-analysis of the same HALOGAS cube (30″ × 30″ beam). Table 5 (tilted rings): V_sys = 715 ± 7, kinematic PA = 160 ± 2, kinematic i = 52 ± 4, **V_max = 237 ± 10, V_flat = 185 ± 10 km/s**. Note: "The rotation curve is declining." Table 4 (global profile): W50 = 375 ± 6, W20 = 395 ± 6. Table 6: ∫S dv = 25.2 Jy km/s, M_HI = 1.86e9 M☉, D_HI = 18.8 kpc (conflict, section 4). Table 1: optical PA 166, i 55, distance 17.70; its other columns (log d25 = 1.29, m[3.6] = 6.56, μ₀ = 23.03, log h_r = 1.69) do not make a self-consistent row in the HTML rendering and are **not used**.

**V02** `[verified: Vallejo, Braine & Baudry 2002, A&A, arXiv:astro-ph/0202391, abstract, Table 1, Sects. 2.3, 3, 4, Tables 7 and 8, https://arxiv.org/html/astro-ph/0202391]` — CO(1–0) Plateau de Bure rotation curve (3.28″ × 3.0″ beam) + VLA HI + HST B, V, I. Table 1: i = 55°, PA = 157°, type Sc, D25 = 4′, D = 19.2 ± 2 Mpc, V_sys = 716. "no bar and poorly defined spiral structure"; nucleus unobscured. Gas: molecular 6.5e9 M☉ **including He** (own N(H₂)/I_CO from a virial analysis; value not printed), atomic 8.4e9 M☉ including He, total 1.5e10 M☉. Mass model (Miyamoto–Nagai, Table 7): nuclei 2.5e9 (a = 70 pc) and 4.0e9 M☉ (a = 380 pc); stellar+gaseous disc 86e9 (a = 2500 pc) with a −16e9 "negative component"; "total visible mass is about 7.65 × 10¹⁰ M☉". The peak of the rotation curve is "at about 35″"; the HI curve reaches 33.5 kpc (360″). Dark matter "small, possibly negligible" inside 5–7 kpc; visible mass dominates to ~10 kpc (100″). M/L (solar, at 19.2 Mpc; M/L ∝ 1/D): observed B 1.7, V 1.9, I 1.4, K′ 0.46 at 55–70″; extinction-corrected ("should be viewed as upper limits") B 0.85, V 1.1, I 1.0, K′ 0.42; extinction there A_B 0.76, A_V 0.58, A_I 0.33, A_K′ 0.05; in the molecular ring ~1.6 (B), 1.3 (V), 0.9 (I), 0.2 (K′). Rotation values are in figures only.

**W04** `[verified: Wong, Blitz & Bosma 2004, ApJ, arXiv:astro-ph/0401187, Tables 1 and 3, Sect. 5.3.2, https://arxiv.org/html/astro-ph/0401187]` — BIMA CO (6.53″ × 4.88″) + VLA HI (17.5″ × 15.3″). Kinematic fit: V_sys = 720 ± 5, **PA = 159 ± 2, i = 55 ± 2**. R25 = 110″. "little evidence for a bar in the K-band image"; inflow < 4 % of the circular speed; HI warp beyond R > 150″.

**H03** `[verified: Helfer et al. 2003, ApJS 145, 259 (BIMA SONG), arXiv:astro-ph/0304294, Tables 1, 4, 5, https://arxiv.org/html/astro-ph/0304294]` — Table 1: i = 55, PA = 159, RC3 type SA(rs)c?, d = 19.1 Mpc, D25 = 3.6′, B_T = 10.96, **Elmegreen arm class 3** (classes 1–4 are flocculent). Table 4 (BIMA + 12 m on-the-fly, 6′ square = 1.67 D25): **S_CO = 2453 ± 282 Jy km/s**, M(H₂) = 7.02 ± 0.81 ×10⁹ M☉ with M = 7845 S d², X_CO = 2 × 10²⁰, no heavy elements; systematic 15 %. Table 5: peak face-on Σ_mol = 130 M☉/pc², central 59.

**Pin18** `[verified: Pingel et al. 2018, ApJ, arXiv:1808.02041, Sect. 4.4, https://arxiv.org/html/1808.02041]` — GBT map: total HI mass (5.43 ± 0.27) × 10⁹ M☉, "∼1 × 10⁹ M☉ more" than WSRT over the same area; distance quoted as 18 ± 2 Mpc; inner disc within 240″ "(∼21 kpc)".

**H11** `[verified: Heald et al. 2011, A&A 526, A118, arXiv:1012.0816, Table 1 and Sect. 2, https://arxiv.org/html/1012.0816]` — sample table: d(Tully 1988) = 9.7, d_best = 17.8, i = 50, D25 = 4.5′, M_B = −19.12, v_rot = 224.7 (HyperLeda), SFR = 1.3 M☉/yr (Hα + TIR after Kennicutt 2009). Parameters other than v_rot, d_best and SFR "are taken from Tully (1988)".

**Th17** `[verified: Thater et al. 2017, A&A, arXiv:1610.04269, Sect. 1, Table 1, Sect. 5.1, Table 4, https://arxiv.org/html/1610.04269]` — adopted D = 18.0 ± 3.0 Mpc (NED mean); precise distances "between 16.6 and 21.1 Mpc"; bulge effective radius 3.9 ± 1.4″ (Fisher & Drory 2009); σ_e = 115.5 ± 3 km/s; dynamical M/L (dust-corrected F606W/r band, central 1.5–40″) 1.75–2.14, Schwarzschild 1.80 ± 0.09; black hole < 1.56e6 M☉; "unbarred".

**K09 / MK06** `[verified: Kennicutt et al. 2009, ApJ 703, 1672, arXiv:0908.0203 eqs. in Sect. 6 and VizieR J/ApJ/703/1672 table2, https://cdsarc.cds.unistra.fr/ftp/J/ApJ/703/1672/ReadMe]`, `[verified: Moustakas & Kennicutt 2006, ApJS 164, 81, VizieR J/ApJS/164/81 galaxies table and ReadMe, https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/164/81]` — integrated drift-scan spectrum, **180″ scan × 120″ aperture, PA 90** (not the whole disc): F(Hα) = 4142.6 ± 26.4, F(Hβ) = 833.37 ± 16.61 (10⁻¹⁵ erg/s/cm²), corrected for Galactic extinction and stellar absorption, **not** for internal extinction; D = 17.7. Also U = 11.025, B = 10.879, V = 10.059 (±0.13), J = 7.917, H = 7.223, K_s = 6.939; E(B−V)_Gal = 0.019; type SA(rs)c; 3.63′ × 2.04′. K09: SFR[Salpeter] = 7.9e-42 [L(Hα)_obs + a L_TIR], SFR[Kroupa] = 5.5e-42 […], a = 0.0024 ± 0.0001 ± 0.0006.

**z0MGS** `[verified: Leroy et al. 2019, ApJS 244, 24, VizieR J/ApJS/244/24 table4 and ReadMe; IMF in arXiv:1910.13470 Sect. 3, https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/244/24]` — D = 17.7 (uncertainty 0.06 dex), log M* = 10.65 ± 0.10 (Υ₃.₄ = 0.36, method SSFRLIKE), log SFR = 0.46 ± 0.20 (FUV+WISE4), offset from main sequence +0.14, flag S (heavy star contamination). Uncertainties exclude distance. IMF: Kroupa & Weidner 2003.

**S4G** `[verified: Sheth et al. 2010 catalogue v2, VizieR J/PASP/122/1397; Salo et al. 2015, VizieR J/ApJS/219/4 galaxies and table7; Buta et al. 2015, VizieR J/ApJS/217/32; https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/219/4]` — [3.6] = 9.429 AB (asymptotic), log M* = 10.883 at D_mean = 18.312 ± 2.402 Mpc (calibration and IMF not read); semi-major axis at 25.5 AB mag/arcsec² = 153.5″, ellipticity there 0.222. Pipeline 4: outer isophotes (45–75) PA = 159.6 ± 1.2, ellipticity 0.458 ± 0.011; one-component Sérsic n = 1.514, R_e = 31.43″; **final model "_dn", quality 5: exponential disc 95.8 % of the flux, h_r = 19.22″, q = 0.542, μ₀ = 17.829; unresolved nucleus 4.2 %; no bulge, no bar component.** Buta: SA(rl)bc (phase 1), SA(s)c / E3 (phase 2), mean T = 4.5, family index 0.00, "flocculent spiral", arm class F.

**Wat19** `[verified: Watkins et al. 2019, A&A 625, A36, VizieR J/A+A/625/A36 table4 and ReadMe, https://cdsarc.cds.unistra.fr/ftp/J/A+A/625/A36/ReadMe]` — 3.6 µm profile, break type IIId+IIId+IIs; segments 24.74–39.75″: h = 18.72″; 39.75–95.25″: h = 20.48″; 95.25–143.25″: h = 37.44″; 143.25–162.4″: h = 41.76″; μ₃.₆ at the breaks 20.04, 23.02, 24.46.

**RC3** `[verified: de Vaucouleurs et al. 1991 (RC3), VizieR VII/155/rc3, https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=VII/155]` — type code .SAT5$. (T = 5.0 ± 0.3), log D25 = 1.56 ± 0.02 (3.63′), log R25 = 0.25 ± 0.03, PA 155, **B_T = 10.96 ± 0.13, B_T⁰ = 10.62, (B−V)_T = 0.84 ± 0.01, (B−V)_T⁰ = 0.77**, (B−V)_e = 0.87, (U−B)_T = 0.16, (U−B)_T⁰ = 0.09, A_i = 0.38, A_g = 0.02, log A_e = 0.96, m21 = 12.87, W20 = 411 ± 16, W50 = 377 ± 12.

**HL** `[verified: HyperLeda object page for NGC 4414 (PGC 40692), parameter table, read 2026-10-03, http://atlas.obs-hp.fr/hyperleda/ledacat.cgi?o=NGC4414]` — type Sc, t = 5.2 ± 0.6, logd25 = 1.29 ± 0.04, logr25 = 0.24 ± 0.03, PA 162.3, ut 11.15 ± 0.07, **bt 10.99 ± 0.07, vt 10.20 ± 0.09**, it 9.07 ± 0.09, **kt 6.98 ± 0.04**, bve 0.79, ag 0.08, ai 0.41, **incl 56.6**, **btc 10.49**, itc 9.03, **bvtc 0.77**, ubtc 0.10, vmaxg 181.5 ± 4.4 (apparent), **vrot 217.5 ± 5.4** (inclination-corrected maximum, from line widths), vdis 113.0 ± 3.7, mod0 = 31.11 ± 0.02, mabs = −20.62.

**San03** `[verified: Sanders et al. 2003, AJ 126, 1607 (IRAS RBGS), VizieR J/AJ/126/1607 table1 and ReadMe, https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/126/1607]` — F12 = 2.78, F25 = 3.61, F60 = 29.55, F100 = 70.69 Jy; D = 17.68 Mpc (primary distance); log L(40–400 µm) = 10.43, **log L(8–1000 µm) = 10.56 L☉**.

**Other catalogue rows** (all VizieR, read 2026-10-03): `[verified: Thilker et al. 2007, ApJS 173, 538, table1 + ReadMe]` D = 18.6, log SFR = 0.910 (UV + TIR, Kennicutt 1998 calibration, no cirrus correction), log M_HI = 9.58. `[verified: Haynes et al. 2018 (ALFALFA), ApJ 861, 49, table2]` W50 = 384 ± 3, W20 = 419, flux 49.27 ± 0.14 Jy km/s, D = 16.6 ± 1.7, log M_HI = 9.50 ± 0.10. `[verified: Courtois et al. 2009, AJ 138, 1938, table4]` GBT flux 58.16, Green Bank 140-ft flux 68.09 Jy km/s, W = 378 ± 7. `[verified: Tully et al. 2013 / 2016 (Cosmicflows-2/3), AJ 146, 86 / AJ 152, 50]` μ = 31.26 ± 0.09 / ± 0.17, 17.86 Mpc. `[verified: Huchra et al. 2012 (2MRS), ApJS 199, 26, table3]` K_tot = 6.939 ± 0.010, H 7.223, J 7.917, b/a = 0.66. `[verified: Tully et al. 2008, ApJ 676, 184, table1]` B 10.92, R 9.58, I 9.02, H 7.83, b/a 0.56, W20 409. `[verified: Ho et al. 2009, ApJS 183, 1, table1]` σ = 117.0 ± 4.0 km/s. URL pattern: https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=<catalogue id>.

## 3. The windows, with arithmetic

All at D = 17.7 Mpc; the distance bracket of the header is applied where a quantity scales with distance.

**W-A. Peak rotation speed, [222, 247] km/s, at R ≈ 3.0 kpc (35″).** P16: 237 ± 10 with i = 52 ± 4. Upper edge 237 + 10 = 247. Lower edge: the same line-of-sight speed deprojected with the steepest inclination read, 57° (W04's 55 + 2; HL 56.6; S4G isophotes 57.2): 237 × sin 52°/sin 57° = 237 × 0.7880/0.8387 = 222.7. Inclination is the dominant systematic; distance does not enter. Compares with v_c at 3 kpc (or the model curve's maximum). Mismatch: a 30″ beam (2.6 kpc) smears a peak that sits at 35″; the CO curve at 3″ resolution exists (V02) but only as a figure. Cross-check **(derived, not a measurement)**: V02's Table 7 mass model gives v_c(3.26 kpc) = 247 km/s at 19.2 Mpc and i = 55°.

**W-B. Outer flat speed, [170, 202] km/s, over R = 20.6–41.2 kpc.** P16: 185 ± 10; dB14 assumes 184. The outer disc is warped and the inclination there is assumed, not fitted: ±5° about 52° gives ×sin52/sin57 = 0.940 and ×sin52/sin47 = 1.077, i.e. −11.2 / +14.3 km/s. Quadrature with ±10: −15.0 / +17.5 → [170.0, 202.5]. Compares with v_c at 21–41 kpc.

**W-C. Shape number S = V_flat/V_max, [0.71, 0.86].** S = 185/237 = 0.781. Random: √((10/185)² + (10/237)²) = 0.0686. Outer-inclination systematic on V_flat only: −6.0 % / +7.7 %. Quadrature: −9.1 % / +10.3 % → [0.710, 0.862]. A constant inclination error cancels. Definition for the model: v_c averaged over 21–41 kpc divided by the maximum of v_c inside 21 kpc. Meaning: the curve must fall by 14–29 % from its inner peak.

**W-D. Disc scale length, [1.5, 1.9] kpc.** Read values for the main disc at 3.6 µm: 19.22″ (S4G-P4), 18.72″ and 20.48″ (Wat19 segments inside 95″). In kpc: 18.72 × 0.08581 = 1.606; 19.22 → 1.649; 20.48 → 1.757. Distance bracket ×0.938 / ×1.079 → [1.51, 1.90]. Compares with the stellar disc's scale length by mass. Mismatch: 3.6 µm light is not mass (a few per cent of hot dust and a radial M/L trend); beyond 95″ (8.2 kpc) the profile flattens to h = 37–42″ (3.2–3.6 kpc), about 5 % of the light **(derived:** (1 + 4.75) e^−4.75**)**. No optical (V) scale length was readable, so no window for the photometric V length.

**W-E. Stellar mass, [3.4, 5.9] × 10¹⁰ M☉ (log 10.53–10.77), Kroupa-type IMF.** z0MGS: 10.65 ± 0.10 at 17.7 Mpc. Distance in quadrature: lower √(0.10² + 0.056²) = 0.115, upper √(0.10² + 0.066²) = 0.120 → [10.535, 10.770]. Independent ceiling **(derived)**: V02's visible mass 7.65e10 at 19.2 Mpc scales as D → ×(17.7/19.2) = 0.922 → 7.05e10; minus gas 1.5e10 × (17.7/19.2)² = 1.27e10 → **5.78e10 M☉ of stars at most** (it assumes no dark matter inside the optical disc), which coincides with the window's upper edge. Dominant systematic: the stellar mass-to-light ratio / IMF.

**W-F. HI mass, [3.8, 6.3] × 10⁹ M☉.** M_HI = 2.356e5 D² S; at 17.7 Mpc that is 7.381e7 × S (checked against dB14: 60.4 Jy km/s ↔ 4.5e9 at 17.8). Read fluxes: 58.16 (GBT) → 4.29e9; 60.4 (WSRT) → 4.46e9; 64.9 (WSRT 1993) → 4.79e9; 68.09 (140-ft) → 5.03e9; the GBT map's 5.43e9 at 17.8 → 5.37e9. Range [4.29, 5.37]; distance ×0.880 / ×1.164 → [3.78, 6.25]. No helium. Compares with the atomic hydrogen mass. Mismatch: 28 % of it lies in a disturbed outer disc beyond 20.6 kpc.

**W-G. H₂ mass, [3.6, 8.4] × 10⁹ M☉ (no helium).** H03 at 17.7: 7845 × 2453 × 17.7² = 6.03e9. Formal 11.5 % ⊕ calibration 15 % = 18.9 % → [4.89, 7.17]; distance → [4.30, 8.35]. Conversion-factor systematic: V02's own conversion gives 6.5e9 including He at 19.2 → 5.52e9 at 17.7 → 4.06e9 of H₂ if the helium factor is 1.36 `[recall — NOT READ: the factor V02 used is not printed]`; × 0.880 = 3.57e9. Window = [3.6, 8.4]. The CO-to-H₂ factor dominates. Total hydrogen (W-F + W-G centres): 4.46 + 6.03 = 10.5e9, range [7.4, 14.7].

**W-H. Star formation rate, [1.8, 4.7] M☉/yr, Kroupa-type IMF.** z0MGS: 0.46 ± 0.20 dex; distance in quadrature → −0.208 / +0.211 → 10^0.252 = 1.79 to 10^0.671 = 4.69. Cross-check **(derived from read inputs and K09's read formula)**: L(Hα)_obs = 4π(5.4617e25 cm)² × 4.1426e-12 = 1.553e41 erg/s; L(8–1000) = 10^10.56 × 3.828e33 = 1.390e44; 0.0024 × that = 3.34e41; sum 4.89e41 → 2.69 M☉/yr (Kroupa), 3.86 (Salpeter). Caveats: the Hα aperture is 180″ × 120″; Sanders' 8–1000 µm stands in for K09's TIR.

**W-I. M_K, [−24.62, −24.12] (Vega).** K = 6.939 (2MASS total) → −24.30; 6.98 (HL) → −24.26. Faint edge: −24.26 + 0.14 (D = 16.6) = −24.12. Bright edge: −24.30 − 0.17 (D = 19.1) − 0.15 (internal K extinction between V02's 0.05 outside and 0.2 inside the ring) = −24.62. Compares with the dust-free M_K: the closest like-for-like photometric check. Mismatch: 2MASS totals can miss outer light; Galactic extinction negligible at E(B−V) = 0.019.

**W-J. M_B, face-on and still attenuated, [−20.96, −20.43].** RC3 B_T⁰ = 10.62 → −20.62; HL btc = 10.49 → −20.75. Faint edge −20.62 + √(0.13² + 0.14²) = −20.43; bright edge −20.75 − √(0.13² + 0.17²) = −20.96. **Correction state: Galactic extinction removed and the inclination-dependent part of the internal extinction removed by a statistical formula in the axis ratio (A_i = 0.38 RC3, 0.41 HL); the face-on dust column is still in front of the stars.** Compares with the dust-attenuated face-on B frame, not with the stars-alone magnitude. For the stars-alone M_B only a one-sided bound holds: brighter than −20.43. Same in V **(derived:** V_T⁰ = 10.62 − 0.77 = 9.85; 10.49 − 0.77 = 9.72**)**: [−21.73, −21.20]. Observed, inclined, Galactic-corrected only: B = 10.879 → −20.36; V = 10.059 → −21.18.

**W-K. B − V, face-on and still attenuated, [0.72, 0.82].** RC3 (B−V)_T⁰ = 0.77 and HL bvtc = 0.77 agree; the observed totals differ (0.84 ± 0.01 RC3; 10.99 − 10.20 = 0.79 HL; 0.82 MK06 Galactic-corrected), so ±0.05. Compares with (attenuated face-on B) − (attenuated face-on V). **It is not the stars-alone colour**: the stars-alone B−V must be bluer than 0.82, by an amount no source read here measures (V02's line-of-sight A_B − A_V is 0.18 at 55–70″ and ~0.3 in the molecular ring).

**W-L. Infrared luminosity, log L = [10.48, 10.65] L☉.** San03: 10.56 at 17.68 (+0.001 to 17.7). Method systematic ±0.05 dex **assumed by me** (IRAS-only 8–1000 µm formula; cold dust beyond 100 µm unconstrained), in quadrature with distance −0.056 / +0.066 → −0.075 / +0.083. Compares with the infrared (dust) luminosity. Dust temperature: only the IRAS ratio F60/F100 = 0.418 was read; no temperature, no dust mass → no window.

**Camera (not a check).** Inclination [52, 57]°, suggested 54.5°: kinematic 52.3 ± 1.5 and 52 ± 4 (HI), 55 ± 2 (CO+HI); photometric 55.8° from RC3 log R25 = 0.25 and 57.2° from the 3.6 µm outer ellipticity 0.458, both **(derived, thin disc, arccos of the axis ratio)**; HL 56.6°. Position angle [156, 162]°, suggested 159°.

## 4. Conflicts between sources (kept as named alternatives)

1. **Distance.** 16.60 Mpc (F01, no metallicity correction) / 17.70 (F01, metallicity-corrected; adopted by dB14, P16, z0MGS, MK06, San03) / 19.1 (T98) / 19.2 ± 2 (V02) / 17.86 (Cosmicflows) / 16.7 (HL mod0 = 31.11) / 18.3 ± 2.4 (S4G mean) / 18.0 ± 3.0 (Th17, NED mean) / 16.6 ± 1.7 (ALFALFA) / 9.7 (Tully 1988, still behind H11's M_B).
2. **Rotation speed.** V_max 237 ± 10 (P16, i = 52) / HL vrot 217.5 ± 5.4 (width-based, i = 56.6) / 224.7 (H11, from an earlier HyperLeda) / V_flat 185 ± 10. Three different quantities; the windows keep them apart. W50: 333 (dB14) vs 375 ± 6 (P16) vs 384 ± 3 (ALFALFA) vs 377 ± 12 (RC3).
3. **Inclination.** 52.3 ± 1.5 (HI kinematic) vs 55 ± 2 (CO+HI) vs 56.6–57.2 (photometric) vs 50 (Tully 1988).
4. **HI flux.** 60.4 / 64.9 (WSRT), 58.16 / ~72.7 (GBT, pointed / mapped), 68.09 (140-ft) against 49.27 (ALFALFA → 3.64e9 at 17.7, just below W-F), log M_HI = 9.58 at 18.6 (Thilker → 3.44e9) and **25.2 Jy km/s (P16 Table 6 → 1.86e9), a factor 2.4 below dB14 from the same cube.** The last three are outside W-F.
5. **Stellar mass.** 4.5e10 (z0MGS, Υ = 0.36) / ≤ 5.8e10 (dynamical, V02 rescaled) / **7.1e10 (S4G: 10.883 − 0.030 for 18.31 → 17.7 Mpc)**. The S4G value exceeds the dynamical stellar ceiling and is outside W-E.
6. **SFR.** 2.88 (z0MGS) / 2.7–3.9 (Hα + IR, derived) / 4.2 (dB14 quoting Heald 2012; IMF not read) / 1.3 (H11 Table 1 — consistent with 4.2 only if computed at 9.7 Mpc: 4.2 × (9.7/17.8)² = 1.25) / **8.1 at 18.6 Mpc (Thilker; 7.4 at 17.7, Salpeter, no cirrus correction; × 5.5/7.9 = 5.1 on a Kroupa scale)** — outside W-H.
7. **H₂.** 7.02e9 at 19.1 (H03, X = 2e20, no He) vs 6.5e9 incl. He at 19.2 (V02, own conversion).
8. **Disc scale length.** 18.7–20.5″ (S4G, Wat19 inner) vs 37–42″ (Wat19 outer segments) vs log h_r = 1.69 → 49″ (P16 Table 1, row not self-consistent) vs V02's Miyamoto–Nagai a = 2.5 kpc at 19.2 Mpc (not an exponential length).
9. **Optical diameter.** log D25 = 1.56 (RC3, 3.63′) vs 1.29 (HL, 1.95′) vs 4.5′ (Tully 1988) vs 4′ (V02).
10. **Face-on B.** 10.62 (RC3) vs 10.49 (HL). RC3's own columns give 10.96 − 0.02 − 0.38 = 10.56, 0.06 mag from its printed 10.62; unexplained.
11. **M_B = −19.12** in dB14/H11 Table 1 is Tully (1988)'s value at 9.7 Mpc and is inconsistent with the 17.8 Mpc printed beside it.
12. **Morphology / bulge.** RC3 SA(rs)c? vs Buta SA(rl)bc / SA(s)c; S4G fits no bulge (nucleus 4.2 % of the light) while V02 needs 6.5e9 M☉ in two nuclear components and Fisher & Drory (via Th17) give a bulge R_e = 3.9 ± 1.4″.

## 5. What could not be read

- **Braine, Combes & van Driel 1993** (A&A 280, 451) and **Braine, Brouillet & Baudry 1997** (A&A 318, 19): not on arXiv, ADS abstract pages return HTTP 405 to the fetcher. Their HI flux (64.9 Jy km/s) is known only second-hand from dB14; the CO-to-H₂ factor V02 uses is not printed anywhere I could read.
- **Thornley & Mundy 1997** (ApJ 490, 682): not on arXiv; no rotation-curve values, HI mass or Hα numbers read first-hand.
- **Vallejo, Braine & Baudry 2003** (Ap&SS 284, 715): Springer page not fetched.
- **de Blok et al. 2014 on aanda.org**: HTTP 403; the arXiv version was read instead. **Its rotation curve, and V02's, exist only as figures — no v(R) at stated radii could be read from any page.**
- **Heald et al. 2012** (the source of SFR = 4.2): not found; read only as quoted by dB14.
- **Braine & Herpin 2004** (arXiv:astro-ph/0412283, CO beyond the optical edge): no HTML rendering.
- **HyperLeda primary site** (leda.univ-lyon1.fr): connection refused; the OHP mirror was read. **NED object page**: not fetched; RC3's decoded type "SA(rs)c?" was read in H03 and MK06 instead.
- **Elmegreen & Elmegreen 1987, Young et al. 1995 (FCRAO), Kennicutt et al. 2008 (11HUGS)**: no VizieR rows found under the catalogue ids tried. Arm class 3 was read in H03.
- **Metallicity gradient**: none found. NGC 4414 is not in Pilyugin et al. 2014 (VizieR J/AJ/147/131, checked). Only one abundance read: 12+log(O/H) = 9.20 ± 0.15 at the Cepheid field (F01).
- **Dust mass and dust temperature**: nothing read beyond IRAS fluxes and the ISO-LWS line fluxes ([C II] 158 µm = 7.53 ± 0.09 in Brauher et al. 2008's units).
- **Optical (B/V/R/I) disc scale length and a bulge-to-disc ratio in an optical band**: not found.
- **Arm pitch angle**: not found (only a magnetic pitch angle of about 20° in arXiv:astro-ph/0208180, which is not an arm pitch).
- **Turner et al. 1998**: abstract only, through a summarising fetch; reddening and Cepheid-field details not relied on.

## 6. Recommendations

**Best determined — suitable for the fit:**
1. **V_max, [222, 247] km/s at 3 kpc** — distance-free, two independent tracers agree on the shape (HI; CO to 3″), the dominant error is a 5° inclination spread.
2. **Disc scale length, [1.5, 1.9] kpc** — three concordant 3.6 µm values; the error is almost all distance.
3. **M_K, [−24.62, −24.12]** — the stellar content measured where dust matters least and with no IMF assumption; better as a fit target than the stellar mass, whose window is IMF-dominated.
4. **HI mass, [3.8, 6.3] × 10⁹ M☉** — five concordant fluxes from four telescopes.

**Five honest independent checks (the fit must not see them):**
1. **Rotation-curve shape S ∈ [0.71, 0.86]** — independent of the amplitude used in the fit; it tests the concentration of the mass (a compact disc under a modest halo).
2. **Star formation rate ∈ [1.8, 4.7] M☉/yr** (Kroupa-type IMF).
3. **H₂ mass ∈ [3.6, 8.4] × 10⁹ M☉** — tests the molecular fraction: the read centres give H₂/HI ≈ 1.35, a molecule-rich disc.
4. **B − V (face-on, attenuated) ∈ [0.72, 0.82]** — against the model's attenuated face-on frames; the stars-alone colour has no like-for-like observation.
5. **Stellar mass ∈ [3.4, 5.9] × 10¹⁰ M☉** — given M_K in the fit, this checks the model's K-band mass-to-light ratio against a 3.4 µm estimate and a dynamical ceiling.

**Named alternatives, in order:** outer flat speed [170, 202] km/s; face-on attenuated M_B [−20.96, −20.43]; infrared luminosity log L [10.48, 10.65] (correlated with the SFR check — do not count both as independent); bulge mass [1.4, 6.5] × 10⁹ M☉ (lower: 4.2 % × 3.4e10; upper: V02's 6.5e9 × 0.922 = 6.0e9 × 1.079), which is weak because the sources disagree on whether a bulge exists; a one-sided bound on the stars-alone M/L_V ≤ 1.27 (V02's corrected 1.1 × 19.2/16.6).

**Structural mismatches to state up front, whatever the fit does:**
- **NGC 4414 has no bar** (RC3 SA; Buta family index 0.00; V02 "no bar"; W04 "little evidence for a bar"; S4G fits none). A model that always carries a bar has no bar length to check here.
- **The arms are flocculent** (Elmegreen class 3; Buta class F). An arm count and a pitch angle have no measured counterpart.
- **The rotation curve declines**, and the outer HI disc is warped and disturbed; a model curve that stays flat will pass W-A and fail W-C.
- If the model's stellar mass or SFR uses a Salpeter IMF, windows W-E and W-H must be read on that scale (× 7.9/5.5 = 1.44 for the SFR, by K09's two calibrations); the factor for the mass was not read.
