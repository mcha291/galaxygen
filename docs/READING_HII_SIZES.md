# READING_HII_SIZES — an HII region's size once it has outgrown its natal clump (S102, batch Q, D272; register #232)

**What this file is (2026-11-17, S102, batch Q's lane H).** The reading register entry #232 asked for, and the build
it led to. S101's reader (an Opus reader, read-only; its note `s101_R232.md` in the session's scratchpad) fetched the
sources in section 1 and printed the model's numbers under each candidate law on S99's saved census. The gate ruled
the build (the D-type region, stopped at stagnation, capped at the cloud: rulings R1-R6 of lane H's brief). Lane H's
builder (Opus) re-read each equation that entered code at its source page in S102 and built it into
`model/galaxy/stages/nebular.py` (`materialise_nebular`); its tests are `tests/test_hii_expansion.py`. What the gate
takes from it goes in `DECISIONS.md` D272 and register #232.

**Tags.** READ `[verified: source, place]` — quoted from a page fetched in S101 or S102, said which; RECALL `[recall]`
— known, not fetched; NOT READ — named and not reached; `[inferred]` — the reader's or the builder's own arithmetic or
reading of two definitions. A "summarising fetch" (the fetch tool answers a question on the page) is how every page
here was read: equations were asked for verbatim and are quoted as returned.

---

## 1. What was read

### 1.1 The law: Bisbas et al. 2015 (StarBench), arXiv:1507.05621 — READ (ar5iv, S101 and again S102, first 100k characters)

- Eq. 13, Hosokawa & Inutsuka 2006's form: R_HI(t) = R_St (1 + (7/4) sqrt(4/3) c_i t / R_St)^(4/7). The factor
  sqrt(4/3) "arises from our inclusion of the inertia of the shocked gas due to its own movement" `[verified: Bisbas
  et al. 2015 §2.1.2 eq. 13, re-read S102]`. Spitzer's eq. 9 lacks it. S101's reader: the abstract finds "much better
  agreement" with HI06 at early times than with Spitzer.
- Eq. 17 (Raga-II): R_STAG = R_St (8/3)^(2/3) (c_i/c_o)^(4/3), reached "at t=t_STAG in which R-dot_HI(t_STAG)=0"; it
  comes from the inertial equation of motion (their eqs. 11-12), the model eq. 13 is the early-time limit of
  `[verified: ibid. §2.2.2, re-read S102]`. Eq. 14 (Raga-I) is the same without (8/3)^(2/3).
- R_St is "the initial Strömgren radius"; c_i the ionized gas's sound speed; t is not defined in words (the figures'
  axis is time in Myr) — the time since the Strömgren sphere formed `[inferred]`.
- Their assumptions: a uniform medium, a constant source, a sphere.

### 1.2 The ambient's pressure: Tremblin et al. 2014, arXiv:1406.1801 — READ (ar5iv, S101 and again S102)

- Eq. 8: "we replaced the initial temperature T0 in the sound speed c0 by an effective turbulent temperature",
  T_eff = <T0 + (mu m_H / k_b) sigma0^2 / 3> `[verified: Tremblin et al. 2014 eq. 8, re-read S102]`.
- Eq. 16: P_turb ~ <rho>(c0^2 + <sigma>^2/3), "c0 the sound speed (0.2 km/s)" `[verified: ibid. eq. 16, re-read
  S102]`. The page does not say which gas c0 = 0.2 km/s is; the model's own cloud gas (10 K molecular, Bergin &
  Tafalla 2007's "0.2 km/s at 10 K", `MOLECULAR_GAS_TEMPERATURE` and `MOLECULAR_MEAN_WEIGHT`: 0.19 km/s) gives it, so
  **no constant was added**: Tremblin is cited for the form only.
- **Their sigma is three-dimensional** `[inferred]`: the /3 splits it over three directions, and their eq. 14 is
  Larson's sigma = 1.1 km/s (r/pc)^0.38, a 3-D dispersion `[recall]`. The model's `cloud_velocity_dispersion` is
  Heyer et al. 2009's virial line-of-sight dispersion (one-dimensional). Built as ruled (sigma_cloud^2/3); if the
  model's sigma is 1-D, the turbulent pressure is three times what is built and every stagnation radius 3^(-2/3) = 0.48
  of it. **A ruling for the gate**, not mended.

### 1.3 The data: Barnes et al. 2025, arXiv:2510.11778v1 — READ (arxiv.org/html, S101 and again S102, first 100k characters)

- Sect. 5.1: Eq. 1 log(r_circ) = 0.479 log(L_Ha) - 16.820; Eq. 3 log(r_mom,deconv) = 0.523 log(L_Ha) - 18.859
  `[verified: Barnes et al. 2025 §5.1, re-read S102]`.
- **Units: NOT READ.** Sect. 5.1 states none for r or L; the only nearby unit is "reaching down to ~1 pc" for one
  radius. pc and erg/s are `[inferred]` (S101: r_circ ~ 24 pc at 1e38, the stated ~20 pc median). So the comparison
  below is **not in the tests** (lane H's brief, R5) and is recorded here as inferred.
- Whether L is extinction-corrected in Sect. 5.1: not said there (Sect. 3.3 corrects the MUSE luminosities).

### 1.4 Read by S101's reader and not re-read in S102

Hunt & Hirashita 2009 (arXiv:0910.2804; n ~ 1/D, "a sequence with different initial gas densities", rejected as a
per-region law); Wisnioski et al. 2012 and Cosens et al. 2018 (ground-based size-L relations at 40-325 pc resolution:
blends); Shu et al. 2002 (champagne flows, abstract only, no size law). See `s101_R232.md` sections 2 and 4.
Spitzer 1978, Dyson & Williams, Raga et al. 2012, Hosokawa & Inutsuka 2006 itself, Franco et al. 1990: NOT READ (the
first four through Bisbas and Tremblin).

---

## 2. The law as built (S102)

- R_St: today's Strömgren radius in the cloud's clumped gas, with the 30 % escape — **unchanged, still published as
  `hii_stromgren_radius` bit for bit** (both templates, measured).
- t: `cluster_age`, the cloud's age less the embedded phase (`GMC_PHASE_EMBEDDED`): the time since the cluster made
  its O stars and its region appeared (S33's ruling; Kawamura et al. 2009 define the embedded phase by their absence).
- c_i: `SHELL_SOUND_SPEED`, 10 km/s, Weaver et al. 1977's C_II, already a level-0 constant the bubbles stage reads;
  now the nebular stage reads it too (it was in level 0 already: no move under D29).
- c_0eff^2 = c_s^2 + sigma_v^2/3, c_s the clouds stage's own `sound_speed(MOLECULAR_GAS_TEMPERATURE,
  MOLECULAR_MEAN_WEIGHT)` (0.19 km/s), sigma_v = `cloud_velocity_dispersion` (a new read of the stage).
- R_HII = min(R_D(t), R_STAG), then capped at `cloud_size` as R_St is. Leaking (`hii_density_bounded`) stays R_St's
  test against the cloud, as before; a region capped at the cloud only after expanding keeps all its photons (it is
  ionization-bounded at the cloud's radius at the expanded density). **This is the builder's reading of "the cap
  unchanged in kind", ruled by R2's closure**; the alternative — leak (r_cloud/R_HII)^3 of the photons — would move
  the Halpha of 54 % of the regions and is the gate's to rule if it wants it.
- Photon balance: Q = alpha_B n^2 (4/3) pi R^3 at R_St (with the clump's <n^2>) and at R_HII, so n_e = n_rms
  (R_St/R_HII)^(3/2). The clumping column stays the natal clump's and applies at R_St only. `hii_electron_density`,
  `hii_halpha_emissivity` (L over the new volume), `hii_ionization_parameter` (Q / 4 pi R^2 n_e c at the new radius
  and density) and the [S II] pair's split (at n_e) follow the expanded region. **The Halpha of every region is
  unchanged, bit for bit** (both templates; asserted as a closure in `tests/test_hii_expansion.py`).
- New columns (`of="cluster"`, both not drawn): `hii_radius` (pc), and `hii_radius_limit`, a category column
  (expansion / stagnation / cloud) in the house style of `hii_density_bounded`.
- R_STAG < R_St would need sigma_v > ~18 km/s; no cloud of either template has it (no region is below R_St).

## 3. What it does — before (main 8db2cee) -> after, the default grid

| | milky_way (= the default galaxy) | ngc_4414 |
|---|---|---|
| regions | 13 124 | 7 632 |
| radius median / p99 / max, pc | 0.77 / 7.67 / 25.7 -> **11.9 / 39.7 / 70.6** | 0.54 / 6.85 / 24.6 -> **10.0 / 40.0 / 79.7** |
| limit by count: expansion / stagnation / cloud | 33.5 / 12.8 / 53.7 % | 30.5 / 31.3 / 38.2 % |
| limit by Halpha | 76.3 / 1.3 / 22.4 % | 77.7 / 2.2 / 20.2 % |
| n_e median, cm^-3 | 153.7 -> **2.31** | 174.0 -> **2.40** |
| log U median | -2.831 -> **-3.457** | -2.912 -> **-3.557** |
| on the grid's log U = -4 floor (clamped) | 0 -> **10.6 %** of regions, 0.02 % of Halpha | 0 -> **16.9 %**, 0.02 % |
| metal-rich Z edge / 0.5 Myr age floor | 3.1 % / 2.6 % (unchanged) | 7.4 % / 2.7 % (unchanged) |
| [O III] / [N II] / [S II]6716 / [S II]6731, Halpha-weighted | 0.777 / 0.080 / 0.054 / 0.043 -> **0.689 / 0.100 / 0.080 / 0.057** | 0.955 / 0.059 / 0.053 / 0.041 -> **0.842 / 0.074 / 0.077 / 0.055** |
| regions with R > 19.5 pc (half the 39 pc pixel), their Halpha share | 7, 6.0 % -> **1 956, 51.1 %** | 3, 5.6 % -> **907, 53.8 %** |
| bubbles' median radius, pc (p99) | 9.58 (105) -> **86.7 (384)** | 5.95 (95) -> **52.2 (372)** |
| bubbles stalled | 97.4 % -> **81.2 %** | 98.2 % -> **87.7 %** |
| `halpha_sfr_ratio`, census / field Halpha, `dig_halpha_fraction`, LF slope | unchanged, bit for bit (0.7123; 4.152e7 / 6.438e7 Lsun; 0.30; -2.0489) | unchanged (0.7431; 1.686e7 / 2.478e7; 0.30; -1.9751) |
| [N II]/Halpha gradient (layer on) | -0.098643 -> -0.103320 dex/kpc | -0.041474 -> -0.043314 |

The brief's "26 % were clamped at the +0.2 dex edge" is S44's figure on the 8.69 scale; on today's 8.93 scale the
metal-rich edge holds 3.1 % (milky_way), unchanged. The new clamp is the other axis: low U.

**The bubbles.** `bubbles.py` reads `hii_electron_density` as its ambient density (no code change, as ruled): a 67x
thinner ambient lets the Weaver bubbles grow ~9x; their median is now 7.3x the region's radius (was 16.6x the Strömgren
sphere), and the p99 384 pc is larger than any cloud. S101's inconsistency (a bubble stalled against an HII region far
smaller than itself) is halved in ratio, not removed, and the bubbles' absolute sizes are now beyond any GMC. **Reported,
not mended**: whether a bubble in a region capped at its cloud should see the cloud's edge is the gate's.

## 4. The comparison with HST-resolved sizes — DISCLOSED, units inferred, not in the tests

Per luminosity decade, median radius against Barnes et al. 2025 at the decade's median L (pc and erg/s `[inferred]`):

| log L_Ha | N (MW) | R_St (before) | R_HII (after) | Barnes Eq. 3 (deconvolved) | Barnes Eq. 1 (circularised) |
|---|---|---|---|---|---|
| 37-38 | 2 060 | 2.81 | **12.9** | 4.68 | 11.6 |
| 38-39 | 258 | 7.12 | **22.8** | 13.9 | 31.5 |
| 39-40 | 13 | 19.1 | **36.0** | 41.1 | 85.1 |

NGC 4414: 13.9 / 25.0 / 30.2 pc against 4.7-11.8 / 13.8-31.3 / 39.4-81.9. Between 10^37 and 10^38 the model's regions
are now above both of Barnes's radius definitions; from 10^38 to 10^39 inside the band; above 10^39 below it. The slope
d log R / d log L over 10^37-10^39 fell from 0.44 to **0.19** (0.46 -> 0.21, NGC 4414), against 0.47-0.52 in Barnes's
fits: the law makes the faint regions large (they are older, and age, not Q, sets their size) and the bright ones not
large enough. The filling-factor analogue (R_St/R_HII)^3 has median 2e-4 (all) and 0.011 (L >= 1e37) against Barnes's
median epsilon 0.22 (S101's reading of their Sect. 5.2) — the expanded regions are far emptier of clumps than the
observed ones `[inferred: the two are not the same quantity]`.

## 5. The alternative ruleset — the region as the inner skin of the model's own Weaver bubble

R_HII = max(R_St, `bubble_radius`), the Halpha the bubble's photon-limited shell (`bubble_shell_emissivity`). For: no
new law (Weaver 1977, read at S36), and it removes the bubble-in-a-smaller-region inconsistency by construction. Against:
the bubble's ambient is itself the HII density (S36's assumption), the bubbles are already printed (disclosed checks
only), and their p99/max exceeded any GMC before this build. **Why the D-type was built**: it is the physics of the
ionized gas itself (a front driven by the region's own pressure into its cloud, the StarBench codes' agreed form),
needs only columns the model holds, and leaves the wind bubble its own object; the bubble ruleset makes the region's
size a by-product of the wind model, which #103's shell physics is inferred.

## 6. Not covered

- **Complexes and envelopes (#181)**: a region of tens to hundreds of pc in a picture is a complex of clusters or a
  low-density envelope (Barnes's third of nebulae are complexes; ground-based sizes are blends). Still no law.
- **Champagne breakout**: 54 % (milky_way) of the regions reach their cloud's radius and are capped there; past it the
  front meets the inter-cloud gas. Shu et al. 2002 (abstract) gives no size law; the cap stands.
- **Q falling with age**: the law holds Q fixed. The model's old regions (10-20 Myr, 50 % of the regions, 3.9 % of the
  Halpha) grow at their tiny Q to a median 12 pc; a falling Q would let them recombine and shrink.
- **Dust inside the region**: Hunt & Hirashita 2009 call sizes "dust-extinction limited"; dust would shrink them.
- The neutral shell's own emission, the front's overshoot of equilibrium (Williams et al. 2018, NOT READ), the
  turbulence of an already dispersing cloud, and sigma's dimension (1.2).

## 7. For the viewer lane

`/api/clusters`' header `knots` keeps `size: hii_stromgren_radius` and gains `expanded_size: hii_radius`. The viewer
draws `hii_halpha_emissivity` over `hii_stromgren_radius` (`frontend/src/galaxy/region.ts`); since this build the
emissivity is uniform over `hii_radius`, so **a sphere drawn at R_St from it carries (R_St/R_HII)^3 of the region's
light** (median 2e-4) until the viewer reads `hii_radius`. The knots (line_response, from `hii_halpha_luminosity`) are
unaffected.
