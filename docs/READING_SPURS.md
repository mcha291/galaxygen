# READING_SPURS — feathers off a spiral arm: spacing, pitch, length, the theories, and a fluctuation's lifetime against the shear (for BUILD_III Phase L2)

**The lead's note (2026-10-13, entered at S62's open).** One Opus reader, briefed by BUILD_III §3e and forbidden the
repository, read 24 primary sources (arXiv text where it exists; Elmegreen 1980 and Balbus 1988 from OCR of scanned
pages, so only ranges and the text's means are quoted from them); what is below the rule is its note as returned, its
headings one level down. **What the reading says that the plan's text did not foresee** (the lead's summary; D221
rules on it): (1) feathers are seen in a fifth of spirals, in 83 % of those with a well-defined dust lane and in none
of 52 Scd–Sd galaxies — a flocculent disc gets none; (2) the spacing in Jeans lengths of the ridge is 10 in the
thick-disc theory (Kim & Ostriker 2006) and in M51 (10.4), 2.5 in the thin-disc theory, and the sources quote each
other's numbers inconsistently; (3) no measured spacing in Toomre lengths exists, and no directly measured persistence
time of an interarm fluctuation — the shear time 1/A is the sourced lifetime, with cloud lifetimes of 20–30 Myr
tracking it in M51 and a feedback cap near 30 Myr; (4) gas spurs are 155–475 pc long and 40–80 pc wide in their thin
parts, stellar spurs kiloparsecs long: the two are different objects.

---

## READING_SPURS - spurs / feathers and the shear stretch (BUILD_III Phase L2, S62)

Reader: Opus reading agent, 2026-10-13. Read-only; nothing in the repository was read or edited.
All PDFs were fetched from arXiv (or the ADS scan service for Elmegreen 1980 and Balbus 1988),
converted to text with pypdf, and the passages read. Texts in `l2_spurs/txt/`, PDFs in `l2_spurs/pdf/`.
Tag format: `[verified: author year, journal / arXiv id, section or table, URL]`.
`[derived]` = arithmetic done by this reader on verified numbers (shown). `[recall - NOT READ]` = not read on a fetched page; never in the summary table.
"Secondary" = a number read on a fetched page, but that page is quoting another paper (the original was not read unless stated).

Notation used below. lambda_J = c_s^2 / (G Sigma) (the 2D "Jeans length" as used by LVO06, KO02, KO06, SO06; KO02/KO06 evaluate Sigma at the arm's density peak, `lambda_J,sp`; SO06 also use the ambient/initial Sigma, `lambda_J,background`). lambda_T (Toomre) = 4 pi^2 G Sigma / kappa^2 in Meidt 2023 (eq. 1) - note this is TWICE the brief's 2 pi^2 G Sigma / kappa^2. W = arm width (FWHM or width at the half-way density). Lx = arm-to-arm distance. Spacings are measured ALONG THE ARM unless stated.

---

### 1. Summary table

| # | Quantity (definition) | Value | Range across sources | Source tag |
|---|---|---|---|---|
| 1a | Feather spacing along the arm, deprojected, HST extinction + BIMA SONG CO, M51 (NGC 5194) | ~200 pc (inner) rising to 500-1000 pc (outer) | | [verified: La Vigne, Vogel & Ostriker 2006, ApJ 650, 818 / astro-ph/0606761, Sec. 4.7, Fig. 21, https://arxiv.org/abs/astro-ph/0606761] |
| 1b | Mean feather spacing / lambda_J (lambda_J = c_s^2/(G Sigma_gas) along the primary dust lane, c_s = 7 km/s adopted) | 10.4 (M51), 1.7 (NGC 628, flagged as an underestimate: HI only azimuthally averaged, CO S/N low) | 1.7-10.4; M51 groups "center on 7-10" | [verified: LVO 2006, Sec. 4.7 and Sec. 5, astro-ph/0606761] |
| 1c | Mean feather separation along arm, NGC 3433 and NGC 5985 | 310, 380, 430 pc (NGC 3433 arms 1-2); 445, 770 pc (NGC 5985) | | [verified: LVO 2006, Sec. 4.7 (p. 17-18), astro-ph/0606761] |
| 1d | Feather/spur separation along arm, 20 galaxies, measured by grid off LVO06 figures, inclination-corrected | 80 pc (NGC 3177, R=0.3 kpc) to 2000 pc (NGC 2336, R=14.5 kpc); spacing grows with R | "200-2000 pc" (their summary) | [verified: Mandowara, Sormani, Sobacchi & Klessen 2022, arXiv:2110.04108, Sec. 6, Table 4, Fig. 13, https://arxiv.org/abs/2110.04108] |
| 1e | Gas-spur spacing between spur bases, M51 northern arm, PAWS CO(1-0) at ~1" (~40 pc), deprojected | 4"-11", mean ~7.5" (9 spurs) | = 147-405 pc, mean ~276 pc at D = 7.6 Mpc [derived: 36.8 pc/"] | [verified: Schinnerer et al. 2017, ApJ 836, 62 / arXiv:1701.02184, Sec. 3.1.1, https://arxiv.org/abs/1701.02184] |
| 1f | Separation of adjacent stellar spurs (B and I plates, 7 galaxies, 28 spurs) | 0.5-10.5 kpc | | [verified: Elmegreen 1980, ApJ 242, 528, Table 2 and Sec. IV, https://articles.adsabs.harvard.edu/pdf/1980ApJ...242..528E] |
| 1g | Spur spacing / lambda_J,sp, MJI theory, razor-thin MHD (KO02 Table 1: K_y,max = lambda_J,sp / lambda_y) | ~2.5 (summary, equipartition B); "2-5" (Sec. 4.2) | K_y,max 0.16-0.54 => 1.9-6.3 [derived: 1/K] | [verified: Kim & Ostriker 2002, ApJ 570, 132 / astro-ph/0111398, Sec. 5.1, Table 1, https://arxiv.org/abs/astro-ph/0111398] |
| 1h | Same, thick-disk / 3D MHD | ~10 (abstract, Sec. 6) | K_y 0.08-0.32 (Tables 1-2) => 3.1-12.5 [derived] | [verified: Kim & Ostriker 2006, ApJ 646, 213 / astro-ph/0603751, abstract, Sec. 6 item 1, Tables 1-2, https://arxiv.org/abs/astro-ph/0603751] |
| 1i | Spur spacing / lambda_J, global MHD | lambda_spur / lambda_J,arm ~ 5; lambda_spur / lambda_J,background ~ 1-2; clump spacing 3-5 lambda_J,arm | | [verified: Shetty & Ostriker 2006, ApJ / astro-ph/0605142, Sec. 5.1-5.2, Table 3, https://arxiv.org/abs/astro-ph/0605142] |
| 1j | Spur spacing / arm width W | KO02: 1.3-6.1 (Table 1 col. 9); SO06: ~3 (Q0 = 2), ~1 (Q0 = 1) | 1-6 | [verified: KO02 Table 1; SO06 Sec. 5.2] |
| 1k | Feather spacing of the fastest-growing linear mode, M51 at R = 2 kpc | 530 pc; lambda_feather / lambda_J = 7.9 | | [verified: Lee 2014, arXiv:1407.5215, Sec. 5.2 and Sec. 6.1 eq. 34, https://arxiv.org/abs/1407.5215] |
| 1l | Wiggle-instability (no self-gravity) wavelength | 179-2000 pc over the parameter scan (2000 pc = box length) ; ~0.07 Lx (F = 5%, linear theory); 0.1-0.2 Lx with B fields | | [verified: Mandowara 2022 Table 3; Kim, Kim & Kim 2014, arXiv:1405.5874, abstract; Kim, Kim & Kim 2015, arXiv:1506.07178, abstract] |
| 1m | Filament spacing in the general ISM web (JWST/MIRI, 4 PHANGS galaxies; NOT spurs adjacent to arms) | "fall very near the (turbulent 3D) Jeans length"; structure studied on 200-500 pc scales | | [verified: Meidt et al. 2023, arXiv:2212.06434, Sec. 3.1, 4, 5, https://arxiv.org/abs/2212.06434] |
| 2a | Spur pitch angle (angle between spur and the circle at its starting radius; inclination corrected) | 63 +/- 12 deg (28 spurs); "about 60 deg" (abstract); ~50 deg more than the arms; never less than the arm's | 33-80 deg per spur (Table 1, OCR) | [verified: Elmegreen 1980, Table 1, Sec. IV] |
| 2b | Feather pitch angle, 8 um local-correlation method, arm vs interarm | M81: arm -17 deg, interarm peak -28 deg; M51: arm -19 deg, arm secondary bump ~52 deg, interarm ~-40 deg (text) / peak ~-65 deg, plateau -50 to -40 deg (Fig. 12 caption) | | [verified: Puerari, Elmegreen & Block 2014, arXiv:1408.3658, results text and Figs. 8, 9, 11, 12, https://arxiv.org/abs/1408.3658] |
| 2c | Feather shape | emerge from the primary dust lane as LEADING features, curve to TRAILING downstream; neighbours share pitch angle and curvature | | [verified: LVO 2006, Sec. 4.1, 4.4.5] |
| 2d | Spur length | stellar spurs 0.64-4.8 kpc (Table 1, OCR); CO extent 475 / 420 / 155 pc (3 M51 spurs); M51 gas spurs mean 6.5" (~240 pc [derived]); feathers may span the whole interarm and join the next arm's dust lane (15 of 45 galaxies) | 0.15-4.8 kpc | [verified: Elmegreen 1980 Table 1; Corder et al. 2008, arXiv:0811.2903, results text and Sec. 5; Schinnerer 2017 Sec. 3.1.1; LVO 2006 Sec. 4.4.3] |
| 2e | Spur width | 560 +/- 260 pc (stellar spurs); 40-80 pc thin parts of M51 gas spurs | | [verified: Elmegreen 1980 Sec. IV; Schinnerer 2017 Sec. 3.1.1] |
| 2f | Gas column along a feather | falls by at least a factor 5-10 with distance from the primary dust lane (CO) | | [verified: LVO 2006, Sec. 4.6] |
| 3 | Mechanism / coverage | Feathers clearly detected in 45 of 223 (20%) spirals; 83% where the primary dust lane is "good"; 0/52 Scd-Sd; MJI (KO02/KO06/SO06/Lee) predicts ~2.5-10 lambda_J,sp; wiggle instability reproduces the range of spacings only with "unrealistically small" pitch sin i = 0.02 for the radial trend; correlated SN feedback gives transient spurs 2-3 kpc apart in a TIGRESS box | | [verified: LVO 2006 abstract, Table 1, Sec. 4.3; Mandowara 2022 Sec. 6; Kim, Kim & Ostriker 2020, arXiv:2006.05614, Fig. 10 text and summary] |
| 4a | Shear time | tau_beta = inverse Oort A = 2 / [Omega (1 - beta)], beta = dlnV/dlnR | | [verified: Jeffreson & Kruijssen 2018, MNRAS 476, 3688 / arXiv:1803.01850, Sec. 2.6 eq. 23, https://arxiv.org/abs/1803.01850] |
| 4b | GMC lifetime in M51 interarm (PAWS) | 20-30 Myr; tracks A^-1 at R < 60-70"; A^-1 ~ 30 Myr at R ~ 70" | re-analysis with pattern speed: 60-500 Myr | [verified: Meidt et al. 2015, arXiv:1504.04528, abstract, Sec. 6.2, Fig. 7; Koda 2021, RNAAS / arXiv:2110.06259, Table 1] |
| 4c | GMC lifetime, 9 PHANGS galaxies | 10-30 Myr; follows galactic dynamical times (incl. shear) where Sigma_H2 > 8 Msun/pc^2 | | [verified: Chevance et al. 2020, arXiv:1911.03479, abstract, Sec. 5.2, https://arxiv.org/abs/1911.03479] |
| 4d | Shear time in M51's arms; GMA lifetime | 1/A comparable to free fall ~5-10 Myr (shear gradients 200-600 km/s/kpc); GMAs live ~arm crossing 2-5 x 10^7 yr; interarm GMCs ~10^8 yr | | [verified: Koda et al. 2009, arXiv:0907.1656, p. 3, https://arxiv.org/abs/0907.1656] |
| 4e | Time for a material spur to change pitch by ~x2 | t_diffrot = (3.4 +/- 8.6) x 10^8 yr; t_SDW = (8.2 +/- 9.8) x 10^7 yr; "in about 10^8 yr a material spur would change its pitch angle by roughly a factor of 2" | | [verified: Elmegreen 1980, Sec. III, IV, Table 2] |
| 4f | Spur formation / life in simulations | arm clump -> spur in 60 Myr (50 K) and 40 Myr (1000 K); feedback spurs "last for ~30 Myr"; wiggle linear growth ~10 Myr (R ~ 0.5 kpc) to ~30 Myr (R ~ 2 kpc), "about a half of the orbital time-scale"; MJI spurs self-gravitating within ~2.5 orbits (t_orb = 2.4 x 10^8 yr at Omega = 26) | 10 Myr - ~600 Myr | [verified: Dobbs & Bonnell 2006, astro-ph/0602100, Figs. 4-5; Kim, Kim & Ostriker 2020 summary section, item 2; Wada & Koda 2004, astro-ph/0308203, text at Figs. 4-6; KO02 Sec. 2.2, 4.3] |
| 5a | Interarm gas anisotropy | interarm features have larger pitch than the arms (M81 -28 vs -17 deg; M51 -40 or -65 vs -19 deg); elongated feathers "swept back more sharply in the interarm"; flocculent feathers "likely ... sheared by differential rotation" (17 of 24 flocculents) | | [verified: Puerari 2014 results text, Figs. 8, 12; LVO 2006 Sec. 4.2, 4.4.3] |

---

### 2. Per-source notes

### La Vigne, Vogel & Ostriker 2006 (LVO06) - ApJ 650, 818; astro-ph/0606761
- Sample: all RC3 galaxies with cz < 5000 km/s, B_T < 15, i < 60 deg, Sa-Sd, with well-exposed WFPC2 images: 223. Feathers (multiple, roughly regularly spaced dust lanes emerging from the primary dust lane, PDL, at similar large angles) clearly detected in 45 (20%). Table 1: 83% of galaxies with "good" PDL delineation show feathers. Sec. 4.3: Sb-Sc 26-33%; Sab 4/24; Sa 1/28; Scd 0/37, Sd 0/15. SA 21%, SAB 22%, SB 19%.
- Shape (Sec. 4.1, 4.4.5): emerge from PDL as leading, curve to trailing on the outer arm edge; neighbours similar pitch and curvature. Elongated feathers in 29 galaxies; in 15, the farthest feathers merge with the next arm's PDL; some coalesce and can be traced through > 180 deg. Lattices in 14 galaxies (9 SB, 5 SAB), absent in unbarred. Feather -> stellar spur transition in 11 galaxies. "Beads on a string" in 38 of 45.
- Spitzer 8 um (9 galaxies): bright interarm filaments coincide with elongated feathers; pitch decreases with distance from the arm (Sec. 4.5).
- CO (BIMA SONG; NGC 628, NGC 5194): feather bases coincide with CO peaks "nearly one to one"; gas column in feathers drops by >= 5-10 with distance from PDL (Sec. 4.6).
- Spacing (Sec. 4.7, Figs. 19-22): CO sampled along PDLs at 3" (half beam); Sigma_gas = Sigma_H2 (X = 2.2e20) + azimuthally averaged HI; lambda_J = c_s^2/(G Sigma) with c_s = 7 km/s adopted for both. Spacing deprojected, measured along the arm, averaged per group of feathers. M51: ~200 pc inner to 500-1000 pc outer; ratio spacing/lambda_J has no radial trend; "a factor of 4-6 higher in NGC 5194" than NGC 628, differs between M51's arms; mean 10.4 lambda_J (M51), 1.7 lambda_J (NGC 628, "likely an underestimate"). Text: the M51 ratio range "centers on the values of 7-10 predicted by KO". Spacing grows as Sigma falls along each arm.
- What fraction this covers: spacing measured in 4 of 45 feathered galaxies (ratio to lambda_J in 2); the authors say most images "did not lend themselves to reliable estimates of feather spacings".
- Their quotes of theory (secondary): KO "2-5 times the local Jeans wavelength ... approximately 750 pc"; WK04 "100-200 pc"; DB06 "~700 pc"; Sec. 4.7 then says KO and KO06 predict "up to 7-10 times the local Jeans length" for magnetized models (see conflicts).

### Elmegreen 1980 - ApJ 242, 528 (ADS scan, OCR text)
- 7 galaxies (NGC 628, 2403, 3031, 4321, 5194, 5236, 5457), B and I photographic plates, i <= 60 deg; 28 prominent spurs (stellar features). Pitch angle defined as the angle between the spur and the circle at the spur's starting radius; inclination corrected; error +/- 5 deg; widths and lengths +/- 100 pc.
- Results (Sec. IV): widths 560 +/- 260 pc; pitch 63 +/- 12 deg, ~50 deg more than the arms; spurs always on the outer edge of arms; never smaller pitch than the arm. Table 1 (OCR, column alignment assumed): widths 200-1280 pc, lengths 0.64-4.8 kpc, pitch 33-80 deg.
- Separation of adjacent parallel spurs 0.5-10.5 kpc (measured at the mean of the two spurs' midpoints, inclination corrected); t_separ = D / (R [Omega - Omega_p]) = (4.6 +/- 3.0) x 10^7 yr (small scatter, argued as wave origin).
- Shear times (Sec. III): t_diffrot = time to change a spur's pitch by ~x2 from differential rotation between its endpoints; t_SDW from passage through the density wave. Values (3.4 +/- 8.6) x 10^8 yr and (8.2 +/- 9.8) x 10^7 yr. Because spurs show in I band and pitch scatter is small, she concludes spurs are long-lived, wave-like, not material.

### Balbus 1988 - ApJ 324, 60 (ADS scan, OCR text)
- Local linear analysis, polytropic single fluid, all in-plane wavenumbers; two preferred growth directions (along the arm, or perpendicular); flow expansion + downstream shear "shape and stretch a wave crest into the characteristic spur shape". Spacing estimate: ~660 pc for c0 = 6 km/s (OCR of the surface-density normalisation is garbled and could not be read); quotes observed periodic spurs at "1 kpc or so". Growth times "several 10^7 yr" for solar-neighbourhood values. [verified: Balbus 1988, Sec. on spurs and Sec. summary (c), https://articles.adsabs.harvard.edu/pdf/1988ApJ...324...60B]

### Kim & Ostriker 2002 (KO02) - ApJ 570, 132; astro-ph/0111398
- Local 2D razor-thin, isothermal c_s = 7 km/s, self-gravitating, magnetized shearing box; Omega_p = Omega_0/2, sin i = 0.1, R0 = 10 kpc => Lx = 3.1 kpc; t_orb = 2.4e8 yr at Omega_0 = 26 km/s/kpc.
- lambda_J,sp = c_s^2 / (G Sigma_max) (eq. 11; M51 check: c_s = 10 km/s, Sigma_max = 170 Msun/pc^2 => 140 pc).
- Table 1: spacing along the arm lambda_y/W = 1.3-6.1, lambda_y/Lx = 0.20-0.67, K_y,max = lambda_J,sp / lambda_y = 0.16-0.54. Sec. 5.1: lambda_y ~ 2.5 lambda_J,sp (~750 pc) for MJI-unstable models; lambda_y/W ~ 3.5 (beta = 10) and 1.5 (beta = 1). Sec. 4.2: "spur spacing is ~2-5 lambda_J,sp". ME3: spacing ~0.7 kpc.
- Unmagnetized quasi-axisymmetrically stable models generally stable => magnetic fields "essential" (their claim).
- M51 test (Sec. 5.2): 5 spurs at R = 2.7 kpc, mean 350 pc (HST Heritage), K_y,max ~ 0.4.
- Shape: wavefront slope dy/dx = -k_x/k_y = T(tau) from background shear and expansion (eq. 12, after B88) - entering waves "shear around and expand to create nearly-radial wavefronts as they exit the arm"; far downstream "strongly trailing". Structures form within ~2.5 orbits (ME models, Sec. 4.3). Fragments ~4e6 Msun ~ local Jeans mass.

### Kim & Ostriker 2006 (KO06) - ApJ 646, 213; astro-ph/0603751
- 2D thick-disk and 3D stratified MHD; c_s = 7 km/s; Lx = 3.14 kpc; Sigma_0 = 11 Msun/pc^2.
- Spacing ~10 lambda_J,sp (lambda_J,sp = c_s^2/(G Sigma_sp)), "3-5 times larger" than thin-disk; 3D magnetized models form 4 spurs at lambda_y = Lx/2 = 1.6 kpc. Table 1 K_y 0.08-0.32; Table 2 0.08-0.14. Footnote 5: spacing depends on resolution (Ny = 128 gives 3 spurs, 256 gives 4) - the spacing is quantised by the box (Ly = 2 Lx).
- Wiggle instability appears in 2D unmagnetized/weak-B runs but NOT in their 3D models. Bound clouds (1-3)e7 Msun.

### Shetty & Ostriker 2006 (SO06) - astro-ph/0605142
- Global MHD with self-gravity. "True spurs" (from arm clumps) vs "background filaments" (swing-amplified). Background features at R = 9.9 kpc: separation 1.3-1.7 kpc vs lambda_J = 1.4 kpc (Table 3; K = 0.8-1.1). True spurs at R ~ 4.5 kpc: lambda_spur ~ 0.6 kpc ~ lambda_J,background; lambda_spur / lambda_J,arm ~ 5; Q0 = 1: lambda_spur/lambda_J,background ~ 2, /lambda_J,arm ~ 5. Clump spacing ~630 pc ~ 5 lambda_J,arm (SMHD2); 3-5 lambda_J,arm others. W ~ 210 pc (Q0 = 2) gives lambda/W ~ 3; Q0 = 1: W ~ 600 pc, lambda/W ~ 1. Inside corotation spurs emanate on the convex (outer) side.
- Quotes LVO as "~7-11 lambda_J in M51 and ~1.5 lambda_J in NGC 0628" (secondary; LVO's own conclusion gives 10.4 and 1.7).

### Chakrabarti, Laughlin & Shu 2003 - astro-ph/0306472
- Global hydro, self-gravitating singular isothermal disk, rigid spiral potential; branches from ultraharmonic resonances; reserve "spurs" for distinctly LEADING features, "feathers" for transient local gravitational-instability features (Sec. 1). No spacing number found in the text. Terminology conflicts with LVO/KO.

### Lee & Shu 2012 (ApJ 756, 45; arXiv:1207.0875) and Lee 2014 (arXiv:1407.5215)
- Linear normal-mode "feathering instability" of a two-armed spiral shock, razor thin, magnetized, self-gravitating; feathers as parasitic instabilities of the shock (LS12 abstract).
- Lee 2014: M51 at R = 2 kpc, fastest mode spacing 530 pc (neighbouring modes +/- 30 pc), "not sensitive to the value of spiral forcing"; lambda_feather / lambda_J = 7.9 with Sigma_peak/Sigma_0 ~ 13 (eq. 34); self-gravity raises growth and lowers spacing; B suppresses the velocity fluctuation but barely changes the growth rate. e-folding t0 = 0.148 t_cross at R = 2 kpc, growth e^5.43 per arm crossing; Fig. 9 caption gives t_cross = 35.3 Myr (=> t0 ~ 5 Myr [derived], assuming Fig. 9 is the same model - not confirmed on the page).

### Wada & Koda 2004 - astro-ph/0308203
- 2D, non-self-gravitating isothermal global hydro. Wiggle instability; ripple scale "roughly the width of the shock-compressed layer, which is about 100-200 pc"; linear growth ~10 Myr at R ~ 500 pc and ~30 Myr at R ~ 2 kpc ("about a half of the orbital time-scale"); stable for flat rotation curve / pitch < ~10 deg (as summarised by LVO; the criterion is in WK04's abstract).

### Kim, Kim & Kim 2014 (arXiv:1405.5874) and 2015 (arXiv:1506.07178)
- 2014: wiggle instability is real, from potential vorticity generated at a deformed shock (not Kelvin-Helmholtz); F = 5%: most unstable wavelength ~0.07 Lx, growth rate ~ Omega. Discussion: WI perturbations are weak in the interarm; observed feathers/clouds in M51 have separations ~0.5-2 kpc, consistent with the arm-peak Jeans length => "WI alone is unlikely responsible for interarm feathers".
- 2015: magnetic fields suppress the WI (through weaker background compression); for F = 5%, beta <~ 10 or F = 10%, beta ~ 5-10, most unstable wavelength 0.1-0.2 Lx, "consistent with a mean spacing of observed feathers".

### Mandowara, Sormani, Sobacchi & Klessen 2022 - arXiv:2110.04108 (MNRAS)
- Local 2D isothermal non-self-gravitating. WI = Kelvin-Helmholtz + repeated shock passages. Units: 1/Omega_0 = 48.9 Myr, length 1 kpc, velocity 20 km/s. Table 3: wavelength 179-2000 pc; growth rates 0.12-1.0 Omega_0 (=> e-folding 49-400 Myr [derived]); spacing falls with lower c_s, stronger potential, smaller Lx.
- Table 4: 20 LVO galaxies, spacing measured by superimposing a grid on LVO's figures, inclination corrected, checked against LVO's own NGC 3433/5985 numbers. E.g. NGC 5194: 270-470 pc at R = 0.6-4.3 kpc, one 1310 pc at 4.2 kpc; NGC 5236: 410-830 pc at R = 2.3-6.2 kpc; NGC 1300: 990-1350 pc at 7.6-11.5 kpc; NGC 4736: 167 pc at 1-1.3 kpc. Radial trend reproduced only with sin i = 0.02 (sin i ~ 0.1 gives too steep a trend).

### Kim, Kim & Ostriker 2020 (TIGRESS) - arXiv:2006.05614
- 3D local, stratified, self-gravitating, SN feedback (TIGRESS). Correlated SN feedback makes spurs downstream of the arm with or without B; spurs protrude nearly perpendicular, then trail. "Transient and last for ~30 Myr before being destroyed by nearby feedback and turbulence"; mean spacing ~2-3 kpc (Fourier ny = 2-3 over the box), larger in unmagnetized/weaker-arm models. WI suppressed in 3D. Cites Schinnerer 2017 as ~0.33 kpc (secondary).

### Dobbs & Bonnell 2006 - astro-ph/0602100 (MNRAS letter)
- 3D SPH, non-self-gravitating, four-armed rigid potential, pitch 15 deg, T = 50-10^4 K. Spurs form only for T <~ 1000 K. Spurs = arm clumps sheared by divergent orbits; feathering = spurs further sheared into near-parallel lanes of small pitch near the next arm. Spacing ~0.7 kpc after 160 Myr (50 K); estimate L ~ t_arm sigma ~ 600 pc with t_arm ~ 6e7 yr, sigma ~ 10 km/s. Clump at 100 Myr -> spur at 160 Myr (Fig. 4, 50 K); 180 -> 220 Myr (Fig. 5, 1000 K). Quotes Russell & Roberts 1992: spur pitch 30-50 deg (secondary).

### Corder, Sheth, Scoville et al. 2008 - arXiv:0811.2903 (ApJ)
- OVRO CO(1-0), one M51 field (inner NW arm), D = 8.4 Mpc, resolution 112 x 85 pc. Three spurs: CO over 475, 420, 155 pc; masses 3.4, 5.3, ~3.9e6 Msun; Sigma = 49, 56, >72 Msun/pc^2 vs arm mean 300. Spurs extend ~500 pc from the arm. Quotes Elmegreen 1980 as ~60 deg pitch, ~560 pc width (secondary; matches the primary).

### Schinnerer et al. 2017 - ApJ 836, 62; arXiv:1701.02184 (PAWS)
- M51 northern arm segment, CO(1-0) at ~1" (~40 pc), D = 7.6 Mpc, i = 22 deg. At 6" five roughly equidistant CO peaks; at 1" nine gas spurs nearly perpendicular to the arm, all matching LVO extinction feathers. Base spacing 4-11" (deprojected), mean ~7.5"; mean length 6.5" (S4 25% shorter, S9 40% longer); thin widths 1-2" (40-80 pc). No regular CO-peak spacing at 40 pc resolution; regular spacing appears at 3" (~110 pc). GMC properties no different in arm vs spur. Cloud crossing times ~5 Myr (arm), ~8 Myr (spur); star formation in spurs over "several Myr".

### Koda et al. 2009 - arXiv:0907.1656 (ApJL)
- M51 CARMA+NRO CO. GMAs assembled in arms, sheared apart leaving them; "shear gradients are 200-600 km/s/kpc"; "the shear timescale, defined as the inverse of Oorts A-constant, is comparable to the free-fall timescale (~5-10 Myr)"; GMAs elongated along the arms; GMA lifetimes ~arm crossing 2-5e7 yr; > 100 GMCs > 4e5 Msun throughout the interarm => interarm lifetimes ~ crossing time 1e8 yr. Spur masses a few 1e6-1e7 Msun.

### Meidt et al. 2015 - arXiv:1504.04528 (ApJ)
- PAWS M51 interarm GMCs (> 1e5 Msun), lifetime = fraction lost x interarm travel time: 20-30 Myr; agrees with A^-1 at R < 70" (rejects constant 31 Myr at 3 sigma over 40-85"); beyond ~60-70" lifetime exceeds A^-1, feedback takes over; at R ~ 70", A^-1 ~ 30 Myr => feedback lifetime ~30 Myr. Travel time assumes a non-rotating pattern (see Koda 2021).

### Koda 2021 - arXiv:2110.06259 (RNAAS)
- Same method and data, travel time measured in the pattern frame (Omega_p = 90 km/s/kpc inside 2.0 kpc, 55 outside, from Meidt 2013): t_travel 105-517 Myr, lifetimes 64-497 Myr at R = 1.64-2.96 kpc (Table 1); summary "60-500 Myr".

### Jeffreson & Kruijssen 2018 - MNRAS 476, 3688; arXiv:1803.01850
- Sec. 2.6: shear time "the time-scale on which a cloud is pulled apart by differential rotation", "given by the inverse Oort constant", eq. 23: tau_beta = 2 / [Omega (1 - beta)] (beta = dlnV/dlnR; extracted text garbled, form consistent with 1/A). Shear works against collapse and LENGTHENS the statistically measured cloud lifetime (cloud dispersed and reformed: phases add).

### Chevance et al. 2020 - arXiv:1911.03479 (MNRAS)
- 9 PHANGS-ALMA galaxies, ~100 pc. GMC lifetimes 10-30 Myr; at Sigma_H2 > 8 Msun/pc^2 lifetimes follow galactic dynamical times (JK18 model; dominated by midplane free fall and shear), below that the internal dynamical time. GMCs and HII regions separated by 100-300 pc. Dispersal 1-5 Myr after massive stars emerge.

### Henshaw et al. 2020 - Nature Astronomy; arXiv:2007.01877
- NGC 4321 southern arm (ALMA CO(2-1)): velocity oscillation wavelength 405 (+92/-76) pc along the arm crest; density-peak separation 366 (+88/-77) pc; "agrees with the 410 pc spacing of embedded star clusters". This is spacing of complexes ALONG the arm ridge (beads), not of interarm spurs.

### Meidt et al. 2023 (arXiv:2212.06434) and Thilker et al. 2023 (arXiv:2301.00881), PHANGS-JWST
- Meidt 2023: 4 galaxies (IC 5332, NGC 628, NGC 1365, NGC 7496); FilFinder filaments 50 pc - 1 kpc; azimuthal spacings (NGC 628, IC 5332) or radial (barred NGC 1365, 7496) averaged in 300 pc annuli; "this approach does not measure the spacings between spur features adjacent to the spiral arms". Spacings "fall very near the [turbulent 3D] Jeans length" and agree less with lambda_T = 4 pi^2 G Sigma/kappa^2 or lambda_2D = 2 pi^2 G Sigma/... ; filaments in barred galaxies more azimuthal, in NGC 628/IC 5332 more radial. No numeric spacing table found in the text (values only in Fig. 3).
- Thilker 2023 (NGC 628 dust filament network 25-400 pc): 40% of sight lines co-spatial emission/attenuation, ~30% of MIR flux in the network, 75-80% of HII regions and 60% of < 5 Myr clusters inside it. No pitch or spacing number.

---

### 3. Conflicts, side by side (not reconciled)

**C1. Spacing in units of lambda_J (theory).**
- KO02 Sec. 5.1: ~2.5 lambda_J,sp; Sec. 4.2: "~2-5"; Table 1: 1.9-6.3 [derived].
- KO06: ~10 lambda_J,sp (3D / thick disk), Table 1-2: 3.1-12.5 [derived].
- SO06: ~5 lambda_J,arm, ~1-2 lambda_J,background.
- Lee 2014: 7.9 lambda_J.
- LVO06's description of KO+KO06: "up to 7-10 times the local Jeans length" (Sec. 4.7) and, in Sec. 1.2, KO "2-5 times".

**C2. Spacing in units of lambda_J (observed).**
- LVO06 conclusion: 10.4 (M51), 1.7 (NGC 628).
- LVO06 Sec. 4.7: M51 range "centers on 7-10".
- SO06 quoting LVO: "~7-11" (M51), "~1.5" (NGC 628).
- KO02 own M51 measurement: K = 0.4 => 2.5 lambda_J,sp (c_s = 10 km/s, Sigma_max = 170, 5 spurs at 2.7 kpc, spacing 350 pc).

**C3. Spacing in kpc (M51).**
- KO02: 350 pc (5 spurs, R = 2.7 kpc).
- LVO06: ~200 pc inner to 500-1000 pc outer.
- Schinnerer 2017: mean 7.5" (~276 pc [derived]), range 4-11".
- Mandowara Table 4 (off LVO figures): 270-470 pc, one 1310 pc.
- Lee 2014 (theory, R = 2 kpc): 530 pc.
- KKK14 (quoting Elmegreen & Elmegreen 1983 and Schinnerer 2013): "~(0.5-2) kpc".
- Elmegreen 1980 (stellar spurs, all 7 galaxies): adjacent spurs 0.5-10.5 kpc.

**C4. Pitch angle.**
- Elmegreen 1980 primary: 63 +/- 12 deg measured from the CIRCLE; "about 60 deg" in abstract; "roughly 50 deg more than" the arms.
- LVO06 quoting E80: "roughly 50 deg with respect to spiral arms".
- Corder 2008 quoting E80: "~60 degrees".
- DB06 quoting Russell & Roberts 1992: "30-50 deg" (definition not given on the page).
- Puerari 2014: interarm (feather continuations) M81 -28 deg, M51 -40 deg (text) vs ~-65 deg peak with -50 to -40 plateau (Fig. 12 caption) - the same paper gives two values for M51.

**C5. Does the wiggle instability make the observed feathers?**
- Mandowara 2022: "able to reproduce the typical range of feather separations", but the radial trend only with sin i = 0.02.
- KKK2015: WI wavelength 0.1-0.2 Lx "consistent with a mean spacing of observed feathers".
- KKK2014: WI "alone is unlikely responsible for interarm feathers" (0.07 Lx, weak interarm).
- KO06 and TIGRESS 2020: WI absent / suppressed in 3D.
- LVO06: WK04 models "probably not relevant for observed feathers" (no self-gravity, arm/interarm 100 vs ~10 observed).

**C6. Are magnetic fields needed?**
- KO02: "magnetic effects are key"; unmagnetized stable models stay stable.
- TIGRESS 2020: feedback spurs form "regardless of the presence of magnetic fields".
- DB06: spurs without self-gravity or B, if T <~ 1000 K.

**C7. Lifetime of a structure against shear.**
- Meidt 2015: GMC lifetime 20-30 Myr, set by A^-1 in M51's inner disk.
- Koda 2021: same data, 60-500 Myr.
- Koda 2009: arm GMAs 20-50 Myr; interarm GMCs ~100 Myr; 1/A in arms ~5-10 Myr.
- Chevance 2020: 10-30 Myr (9 galaxies).
- Elmegreen 1980: spurs long-lived (wave), though material pitch would halve in ~1e8 yr.
- TIGRESS 2020: feedback spurs ~30 Myr; DB06: clump -> spur in 40-60 Myr.
- JK18: shear LENGTHENS the measured cloud lifetime (dispersed-and-reformed phases add), i.e. 1/A is not simply a cap.

**C8. Spacing / arm width.** KO02 1.3-6.1; SO06 ~3 (Q0 = 2) vs ~1 (Q0 = 1); KO02 and SO06 quote Elmegreen & Elmegreen 1983 as ~3 (secondary; E&E 1983 not read).

**C9. Toomre length definition.** The brief's 2 pi^2 G Sigma / kappa^2 vs Meidt 2023 eq. 1, lambda_T = 4 pi^2 G Sigma / kappa^2 (the "smallest scale stabilized by rotation"). Meidt 2023's lambda_2D = 2 pi^2 G Sigma/... is the most unstable 2D wavelength in sigma, not kappa (equation partly garbled in extraction).

---

### 4. What could not be read / limits

- Not read: Elmegreen & Elmegreen 1983 (beads ~3 arm widths; seen only as quoted in KO02/SO06); Russell & Roberts 1992 (seen only via DB06); Lynds 1970; Scoville et al. 2001; Elmegreen 1994; Wada 2008; Kim & Kim 2014 global WI paper (cited by Puerari, not fetched); Dobbs & Pringle 2010; Chandar et al. 2011 (feather clusters ~1e8 yr, seen only via Puerari 2014); Meidt 2022 (rotation-modified fragmentation scale); Schinnerer 2013; Grasha et al. on cluster clustering.
- Lee & Shu 2012 read only in its abstract and a grep (no spacing number found in it); Chakrabarti et al. 2003 read in abstract and introduction only (no spacing number found).
- Elmegreen 1980 and Balbus 1988 are OCR of ADS scans: Table 1/2 column alignment in E80 is assumed (only ranges and the text's means are quoted); Balbus's spacing formula normalisation is garbled.
- Several equations (KO02 eq. 11-13, JK18 eq. 23, Meidt 2023 eq. 3, 5) came through pypdf garbled; only forms confirmed by the surrounding text or a numeric check (KO02 M51: 140 pc) are quoted.
- Journal references for arXiv:1405.5874, 1506.07178, 2110.04108, 2006.05614, 1504.04528, 2212.06434 were not shown on their arXiv abstract pages; cited by arXiv id. ApJ 650, 818 (LVO06) and ApJ 756, 45 (LS12) confirmed on arXiv.
- No source gives a measured spur-spacing / Toomre-length ratio; no source gives a measured persistence time of an interarm density fluctuation directly (only cloud lifetimes, simulation spur lifetimes, and shear-time arguments).
- No survey with a statistically large, uniform measurement of feather pitch angle relative to the arm was found beyond Elmegreen 1980 (28 spurs) and Puerari 2014 (2 galaxies).

---

### 5. Recommendation (named alternatives; the lead rules)

**(1) Spacing of spurs along the ridge.**
- A model could adopt lambda_spur = K^-1 lambda_J,sp with lambda_J,sp = c_s^2 / (G Sigma_ridge,peak) and K^-1 ~ 10 (KO06 3D thick disk; LVO06's M51 mean 10.4), or K^-1 ~ 2.5 (KO02 razor-thin), or K^-1 ~ 5 (SO06 global; Lee 2014's 7.9 lies between).
- Or a model could tie it to the arm width: lambda_spur ~ 3 W (SO06 Q0 = 2; KO02 MS models 3-4; Elmegreen & Elmegreen 1983 as quoted), or ~1-1.5 W (SO06 Q0 = 1; KO02 equipartition).
- Or to the AMBIENT Jeans length: lambda_spur ~ 1-2 lambda_J,background (SO06).
- Check value whichever is adopted: M51 measured 270-470 pc at R ~ 0.6-4.3 kpc (Mandowara Table 4), ~276 pc mean (Schinnerer 2017), 350 pc at 2.7 kpc (KO02), 200 pc -> 500-1000 pc inner to outer (LVO06); across 20 galaxies 80-2000 pc, growing with R. The LVO06 c_s = 7 km/s convention matters: the ratio depends on c_s^2.
- Spacing should rise as the ridge Sigma falls (LVO06 Sec. 4.7, all theories).
- Phases: synthetic per the plan; no source contradicts random phases, but LVO06 notes feathers "clump" in groups with larger gaps between groups.

**(2) Pitch relative to the arm and length.**
- A model could adopt a spur pitch of ~63 deg from the circle (Elmegreen 1980, 28 stellar spurs; ~50 deg more than the arm), or the interarm feather pitch from Puerari 2014 (M81 -28 deg against an arm at -17 deg; M51 -40 deg against -19 deg).
- Shape: rather than one pitch, a model could adopt the kinematic wavefront of KO02 eq. 12 / Balbus 1988 (initial k_x(0)/k_y, then sheared and expanded by the downstream flow): leading or radial at the ridge, trailing downstream, as LVO06 observes.
- Length: a model could adopt ~0.2-0.5 kpc for gas spurs in a strong-arm inner disk (Schinnerer 2017 mean ~240 pc; Corder 2008 155-475 pc), or 0.6-4.8 kpc for stellar spurs (Elmegreen 1980), or let the longest run across the interarm into the next arm's lane (LVO06, 15 of 45 galaxies). Gas column falling by x5-10 from the ridge (LVO06) is the measured profile along a feather.
- Width: 40-80 pc thin gas spurs (Schinnerer) or ~560 pc stellar spurs (Elmegreen 1980).

**(3) Which theory sets the spacing.**
- A model could adopt the magneto-Jeans picture (KO02/KO06/SO06/Lee 2014): spacing in lambda_J,sp, growth within ~1-2.5 orbits, observationally supported in M51 by spacing-vs-Sigma (LVO06; covers 2 galaxies with Jeans ratios, 4 with spacings).
- Or the wiggle instability (WK04; KKK14/15; Mandowara 2022): spacing ~0.07-0.2 Lx, no self-gravity; reproduces the 200-2000 pc range but the radial trend only with sin i = 0.02, and is absent in 3D (KO06, TIGRESS 2020).
- Or correlated SN feedback (TIGRESS 2020): transient spurs, 2-3 kpc spacing in one box, lifetime ~30 Myr.
- Or sheared arm clumps without self-gravity (DB06): spacing ~ t_arm x sigma ~ 600 pc.
- Coverage: none of these is tested on more than the M51 / NGC 628 Jeans comparison; feathers themselves are seen in ~20% of spirals overall and 83% of those with strong dust lanes (LVO06).

**(4) Lifetime / shear stretch.**
- A model could adopt t_life = 1/A = 2 / [Omega (1 - beta)] (JK18 eq. 23; Meidt 2015's M51 result, 20-30 Myr, tracks it at R < 60-70"), capped at a feedback time ~30 Myr where 1/A is longer (Meidt 2015; TIGRESS 2020's spurs ~30 Myr).
- Or a fixed 10-30 Myr (Chevance 2020, 9 galaxies, Sigma_H2 > 8 Msun/pc^2).
- Or a long lifetime, 60-500 Myr (Koda 2021 re-analysis) / ~1e8 yr interarm (Koda 2009), with the shear acting on a persistent structure (Elmegreen 1980: pitch halves in ~1e8 yr for a material spur).
- Or the formation-to-spur time of DB06, 40-60 Myr.
- In 1/A units: Meidt 2015's lifetime ~ 1 x A^-1 in M51's inner disk; Koda 2009's arm A^-1 ~5-10 Myr against 20-50 Myr GMA lives (2-10 x A^-1 [derived]).

**(5) Anisotropy of the interarm gas.**
- A model could adopt trailing interarm filaments with pitch larger than the arm's: +11 deg (M81) [derived: -28 minus -17] or +21 to +46 deg (M51) [derived: -40 or -65 minus -19] over the arm's (Puerari 2014, the two readings of M51 given), or ~+50 deg (Elmegreen 1980).
- Or no fixed angle: an isotropic seed sheared by A over the adopted lifetime (LVO06's flocculent feathers "sheared by differential rotation"; DB06), which makes the trailing angle an output, not an input.
- In barred galaxies the PHANGS-JWST filament web is more azimuthal, in NGC 628 / IC 5332 more radial (Meidt 2023, qualitative only).
