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
- **What sigma_0 is.** The sentence after eq. 8, READ: "where μ is the mean molecular weight, T0 and σ0 the
  temperature and velocity field of the simulation before the ionization starts, and the rms average is computed on
  the whole box" `[verified: Tremblin et al. 2014, after eq. 8, re-read S102]`. sigma_0 is the simulation's velocity
  field, its rms over the box: a three-dimensional rms velocity, and the /3 is the kinetic form (a third per axis).
  The text nowhere calls it a line-of-sight dispersion; their eqs. 14-15 (sigma = 1.1 km/s (r/pc)^0.38, n = 3400
  cm^-3 (r/pc)^-1.1) are Larson's laws, whose dimension the text does not state (3-D by Larson 1981 `[recall]`).
- **The gate's ruling 1 (S102), built in the second commit:** the model's `cloud_velocity_dispersion` is Heyer et al.
  2009's virial line-of-sight dispersion (one-dimensional; `clouds.py`'s about), whose variance is Tremblin's
  sigma_0^2/3 already, so **c_0^2 = c_s^2 + sigma_v^2**. The first commit's sigma_v^2/3 made every stagnation radius
  3^(2/3) = 2.08x what this gives (in the turbulence-dominated limit).

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
- c_0eff^2 = c_s^2 + sigma_v^2 (the gate's ruling 1; the first commit had sigma_v^2/3), c_s the clouds stage's own
  `sound_speed(MOLECULAR_GAS_TEMPERATURE, MOLECULAR_MEAN_WEIGHT)` (0.19 km/s), sigma_v = `cloud_velocity_dispersion`
  (one-dimensional; a new read of the stage).
- R_HII = min(R_D(t), R_STAG), then capped at `cloud_size` as R_St is. Leaking (`hii_density_bounded`) stays R_St's
  test against the cloud, as before. **The cap (the gate's ruling 2, `[inferred]`):** a region whose front reaches
  its cloud's edge keeps all its photons, ionization-bounded at the cloud's radius at the density photon balance
  gives it there. **The alternative, named and not built:** a region whose front would have passed the cloud's edge
  leaks 1 - (r_cloud / R_D)^3 of its photons to the diffuse gas — it would move the Halpha of about half the regions
  (45 % capped on milky_way) and the census/field closure, and no size law for a champagne flow was read.
- **The bubbles keep their medium (the gate's ruling 4, `[inferred]`).** The Strömgren state's rms density is
  published as `hii_natal_density` (not drawn) and `bubbles.py` reads it in place of `hii_electron_density` (one
  name in the reader). The reason: the wind bubble (Weaver, stalled) and the D-type front are two laws for one cavity,
  computed apart; a law coupling them (a wind bubble inside an expanding HII region) was not read, so each keeps the
  medium it was derived in. The first commit let the bubbles read the expanded density: a stalled radius goes as
  density^-1/2, and they grew to a median 86.7 pc (p99 384 pc) inside regions of median 12 pc — not a state the
  model can stand behind. With the natal density the bubbles are main's, bit for bit.
- Photon balance: Q = alpha_B n^2 (4/3) pi R^3 at R_St (with the clump's <n^2>) and at R_HII, so n_e = n_rms
  (R_St/R_HII)^(3/2). The clumping column stays the natal clump's and applies at R_St only. `hii_electron_density`,
  `hii_halpha_emissivity` (L over the new volume), `hii_ionization_parameter` (Q / 4 pi R^2 n_e c at the new radius
  and density) and the [S II] pair's split (at n_e) follow the expanded region. **The Halpha of every region is
  unchanged, bit for bit** (both templates; asserted as a closure in `tests/test_hii_expansion.py`).
- New columns (`of="cluster"`, all not drawn): `hii_radius` (pc), `hii_radius_limit`, a category column
  (expansion / stagnation / cloud) in the house style of `hii_density_bounded`, and `hii_natal_density` (1/cm3).
- R_STAG < R_St would need c_0 > ~16 km/s; no cloud of either template has it (no region is below R_St).

## 3. What it does — before (main 8db2cee) -> after (the gate's rulings, second commit), the default grid

The first commit's numbers (sigma_v^2/3, the bubbles on the expanded density) are in [brackets] where they differ.

| | milky_way (= the default galaxy) | ngc_4414 |
|---|---|---|
| regions | 13 124 | 7 632 |
| radius median / p99 / max, pc | 0.77 / 7.67 / 25.7 -> **11.0 / 36.4 / 70.6** [11.9 / 39.7 / 70.6] | 0.54 / 6.85 / 24.6 -> **9.57 / 36.2 / 79.7** [10.0 / 40.0 / 79.7] |
| limit by count: expansion / stagnation / cloud | **23.1 / 32.1 / 44.8 %** [33.5 / 12.8 / 53.7] | **20.1 / 46.1 / 33.8 %** [30.5 / 31.3 / 38.2] |
| limit by Halpha | **70.4 / 7.3 / 22.3 %** [76.3 / 1.3 / 22.4] | **72.4 / 7.5 / 20.1 %** [77.7 / 2.2 / 20.2] |
| n_e median, cm^-3 | 153.7 -> **3.20** [2.31] | 174.0 -> **4.75** [2.40] |
| log U median | -2.831 -> **-3.426** [-3.457] | -2.912 -> **-3.508** [-3.557] |
| on the grid's log U = -4 floor (clamped) | 0 -> **8.5 %** of regions, 0.01 % of Halpha [10.6 %, 0.02 %] | 0 -> **8.6 %**, 0.01 % [16.9 %, 0.02 %] |
| metal-rich Z edge / 0.5 Myr age floor | 3.1 % / 2.6 % (unchanged) | 7.4 % / 2.7 % (unchanged) |
| [O III] / [N II] / [S II]6716 / [S II]6731, Halpha-weighted | 0.777 / 0.080 / 0.054 / 0.043 -> **0.689 / 0.0996 / 0.0799 / 0.0562** [0.689 / 0.100 / 0.080 / 0.057] | 0.955 / 0.059 / 0.053 / 0.041 -> **0.842 / 0.0740 / 0.0767 / 0.0540** [0.842 / 0.074 / 0.077 / 0.055] |
| regions with R > 19.5 pc (half the 39 pc pixel), their Halpha share | 7, 6.0 % -> **1 482, 49.0 %** [1 956, 51.1 %] | 3, 5.6 % -> **725, 51.9 %** [907, 53.8 %] |
| bubbles' median radius, pc (p99); stalled | 9.58 (105); 97.4 % -> **unchanged, bit for bit** [86.7 (384); 81.2 %] | 5.95 (95); 98.2 % -> **unchanged** [52.2 (372); 87.7 %] |
| `halpha_sfr_ratio`, census / field Halpha, `dig_halpha_fraction`, LF slope | unchanged, bit for bit (0.7123; 4.152e7 / 6.438e7 Lsun; 0.30; -2.0489) | unchanged (0.7431; 1.686e7 / 2.478e7; 0.30; -1.9751) |
| [N II]/Halpha gradient (layer on = layer off, row 37) | -0.098643 -> **-0.103318** dex/kpc [-0.103320] | -0.041474 -> -0.043316 |

The brief's "26 % were clamped at the +0.2 dex edge" is S44's figure on the 8.69 scale; on today's 8.93 scale the
metal-rich edge holds 3.1 % (milky_way), unchanged. **The log U floor (the gate's ruling 5): recorded as it is, no
mend** — 8.5 % / 8.6 % of the regions read the grid's -4 floor (down to -4.56), clamped as FSPS clamps; they carry
0.01 % of the Halpha.

**Row 37** (the layer-off [N II]/Halpha gradient, a recorded miss): -0.0977 -> -0.1033, re-pinned as an as-measured
record (the gate's ruling 3); still a miss, outside the blind window [-0.045, -0.005].

## 4. The comparison with HST-resolved sizes — DISCLOSED, units inferred, not in the tests

Per luminosity decade, median radius against Barnes et al. 2025 at the decade's median L (pc and erg/s `[inferred]`):

| log L_Ha | N (MW) | R_St (before) | R_HII (after) | Barnes Eq. 3 (deconvolved) | Barnes Eq. 1 (circularised) |
|---|---|---|---|---|---|
| 37-38 | 2 060 | 2.81 | **12.7** [12.9] | 4.68 | 11.6 |
| 38-39 | 258 | 7.12 | **22.0** [22.8] | 13.9 | 31.5 |
| 39-40 | 13 | 19.1 | **32.2** [36.0] | 41.1 | 85.1 |

NGC 4414: 13.3 / 24.4 / 30.2 pc against 4.7-11.8 / 13.8-31.3 / 39.4-81.9.

**Two DISCLOSED MISSES of the law as built** (against Barnes's fits, units inferred; nothing tuned to them):

1. **The slope.** d log R / d log L over 10^37-10^39 fell from 0.44 to **0.20** (0.46 -> 0.21, NGC 4414), against
   0.47-0.52 measured. Cause, by arithmetic: once c_i t >> R_St, R_D ~ R_St^(3/7) (c_i t)^(4/7), so the luminosity's
   power in R_St is cut by 3/7 — 0.44 x 3/7 = 0.19, what is read.
2. **The faint end sits above Eq. 1** (10^37-10^38: 12.7 pc against 11.6 circularised, 4.7 deconvolved). Cause: at
   that decade's median age, 3.0 Myr, c_i t is 31 pc whatever Q is, so R_D(3 Myr) from R_St = 2.8 pc is 17 pc before
   the cap or stagnation cuts it to 12.7; the constant-Q assumption grows the old faint regions at their age (the
   10-20 Myr half of the census has median 10.7 pc), and the cap at the cloud (45 % of regions) is all that stops many.

From 10^38 to 10^39 the medians sit inside the band; above 10^39 below Eq. 3. The filling-factor analogue
(R_St/R_HII)^3 has median 2.6e-4 (all) and 0.011 (L >= 1e37) against Barnes's median epsilon 0.22 (S101's reading of
their Sect. 5.2) `[inferred: the two are not the same quantity]`.

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
- **Champagne breakout**: 45 % (milky_way) of the regions reach their cloud's radius and are capped there; past it the
  front meets the inter-cloud gas. Shu et al. 2002 (abstract) gives no size law; the cap stands.
- **Q falling with age**: the law holds Q fixed. The model's old regions (10-20 Myr, 50 % of the regions, 3.9 % of the
  Halpha) grow at their tiny Q to a median 10.7 pc; a falling Q would let them recombine and shrink. *Built at S104:
  Part S104 below.*
- **Dust inside the region**: Hunt & Hirashita 2009 call sizes "dust-extinction limited"; dust would shrink them.
- The neutral shell's own emission, the front's overshoot of equilibrium (Williams et al. 2018, NOT READ), the
  turbulence of an already dispersing cloud.

## 7. For the viewer lane

`/api/clusters`' header `knots` keeps `size: hii_stromgren_radius` and gains `expanded_size: hii_radius`. The viewer
draws `hii_halpha_emissivity` over `hii_stromgren_radius` (`frontend/src/galaxy/region.ts`); since this build the
emissivity is uniform over `hii_radius`, so **a sphere drawn at R_St from it carries (R_St/R_HII)^3 of the region's
light** (median 2e-4) until the viewer reads `hii_radius`. The knots (line_response, from `hii_halpha_luminosity`) are
unaffected.

---

## Part S104 — the region grown at its ionizing rate's history (batch R, lane RH; register #235)

**Why.** S103's reading (`s103_RB.md` A2, the gate's S103 item 2) named a defect of section 2's law: the region is
grown to its cluster's age with R_St from TODAY's ionizing rate held fixed, while the model's own table
(`population_light().ionizing_per_mass`, read by `per_mass_at` as the clusters stage reads it) has the rate falling
20-140x by 4-20 Myr (Q_peak / Q_now over the default census: median 22.6, p99 134, max 144). Bisbas's law assumes a
constant source; an old faint region was not faint when its front was driven.

**Read.** Williams, Bisbas, Haworth & Mackey 2018, arXiv:1805.09273 — READ (ar5iv, S104, summarising fetch). §4.4
eq. 48, as returned: beta r_i r_i'' + ½ beta (7 − beta) r_i'^2 + (3/2) r_i' c_0 / (1 + C r_i'^2/c_0^2) = [(c_0 + 3B r_i')
/ (c_0 + B r_i')] c_0^2 [(R_Stag/r_i)^(3/2) − 1] + ½ c_0 r_i Q̇_0/Q_0, B = (1+beta)/2, C = 2.25, beta = 1 − c_0²/c_i²
(eq. 33); "we have included the source term required if the luminosity of the source varies"; c_0 the neutral gas's
sound speed; their R_Stag = (c_i/c_0)^(4/3) R_St, without Bisbas eq. 17's (8/3)^(2/3) `[verified: Williams et al. 2018
§4.3-4.4, read S104]`. In the thin-shell limit it holds eq. 13 exactly (checked by hand `[inferred]`). **Not built (A2):**
it is an ODE, no closed form, and the paper tests it only on a rise to 120 % (its Fig. 5); on a falling source it says
only that the front "will become a recombination front", the same jump conditions "in the D-type limit". The model's
rate falls 20-140x in a few Myr while recombination takes ~1e4 yr: a recombination front outside that limit.

**The law as built (A1), the gate's ruling on the measured table.**
- Q_ref is the **peak** of the cluster's rate over [0, age] off the model's table (no new constant): exact, since the
  table is read linearly between isochrones, so the maximum is at an isochrone no older than the age or at the age
  (`photometry.peak_per_mass_at`; a dense sampling agrees to 0). On this table the rate is flat for its first 4 Myr and
  never rises after, so the peak **is** the birth rate for every region of both templates.
- The shell (`hii_shell_radius`): R_St,peak (the Strömgren sphere of the peak rate's kept photons in the clump's gas),
  then S102's law unchanged — min(R_D(age), R_STAG), capped at the cloud; `hii_radius_limit` says which limit the shell
  stopped at.
- Inside the shell, `[inferred]`: the gas sits at the density photon balance with the peak rate gives at the shell,
  n_i = n_rms (R_St,peak / R_shell)^(3/2) (a capped shell's density by photon balance at the peak rate at the cloud's
  edge, S102's ruling 2 carried); today's fewer photons ionize it to **R_ion = R_shell (Q_now / Q_peak)^(1/3)** =
  `hii_radius`, where α_B n_i² (4/3)π R_ion³ is today's kept photons (closes to 2e-15 over the census). Recombination
  is taken as instantaneous and the cavity's gas as held at n_i (no refilling, no collapse of the shell). A region
  whose peak Strömgren sphere passed its cloud is its cloud at the clump's density, ionized to today's Strömgren
  radius, at most the cloud.
- **Why the peak** (the gate's reasons): regions under 3.98 Myr (20.3 % on milky_way, 19.3 % on ngc_4414) stay batch
  Q's bit for bit; R_ion ≥ the natal Strömgren radius `hii_stromgren_radius` by construction (the gas inside the shell
  is never denser than the clump), so no floor is needed (0 regions below it, measured); the shell differs under 1 %
  between the three definitions measured (birth = peak, time-mean), so the choice only sets R_ion — the peak and
  time-mean R_ion differ 17-18 % in the median — and the front was driven at the peak.
- Unchanged, measured bit for bit against batch Q (fccecee) on both templates: every region's Hα (today's photons,
  today's leaking rule), `hii_stromgren_radius`, `hii_natal_density`, `hii_density_bounded`, the temperature and
  decrement, all 22 bubble and remnant columns; the cluster and cloud counts (13 124 / 17 127; 7 632 / 9 891).

**Before (batch Q, fccecee) -> after (S104), the production grid.** The time-mean definition's figures in [brackets].

| | milky_way | ngc_4414 |
|---|---|---|
| radius median / p99 / max, pc | 10.99 / 36.4 / 70.6 -> **5.47 / 26.3 / 52.9** [6.40 / 27.6 / 52.9] | 9.57 / 36.2 / 79.7 -> **4.25 / 25.5 / 47.6** [5.00 / 26.8 / 47.6] |
| shell median / p99 / max, pc | (= the radius) -> 12.56 / 60.8 / 110 [12.46 / 54.3 / 100] | -> 10.58 / 60.8 / 112.9 [10.17 / 54.8 / 112.9] |
| shell's limit by count: expansion / stagnation / cloud | 23.1 / 32.1 / 44.8 % -> **22.5 / 4.1 / 73.4 %** | 20.1 / 46.1 / 33.8 % -> **19.1 / 32.4 / 48.6 %** |
| by Halpha | 70.4 / 7.3 / 22.3 % -> 70.4 / 4.2 / 25.4 % | 72.4 / 7.5 / 20.1 % -> 70.7 / 6.1 / 23.2 % |
| n_e median, cm^-3 | 3.20 -> **9.42** [7.15] | 4.75 -> **7.57** [6.65] |
| log U median; on the grid's -4 floor (regions, Halpha) | -3.426; 8.5 %, 0.011 % -> **-3.244; 4.5 %, 0.003 %** | -3.508; 8.6 % -> **-3.358; 6.6 %** |
| regions with R > 19.5 pc (half the 39 pc pixel), Halpha share | 1 482, 49.0 % -> **431, 44.8 %** | 725, 51.9 % -> **222, 47.3 %** |
| slope d log R / d log L: 1e37-1e39 (S102's) / all regions / log L ≥ 38 | 0.197 / 0.100 / 0.254 -> **0.239 / 0.199 / 0.268** | 0.210 / 0.249 / 0.243 -> **0.253 / 0.243 / 0.250** |
| decade medians 1e37 / 1e38 / 1e39, pc | 12.73 / 21.99 / 32.23 -> **11.91 / 21.70 / 32.23** | 13.27 / 24.41 / 30.16 -> **12.63 / 24.41 / 30.16** |
| Barnes Eq. 3 / Eq. 1 at the decade's median L, pc | 4.68 / 13.9 / 41.1 and 11.6 / 31.5 / 85.1 | 4.73 / 13.8 / 39.4 and 11.8 / 31.3 / 81.9 |
| R_ion below the natal Strömgren radius | 0 | 0 |
| Halpha-weighted [O III] / [N II] / [S II] pair; row 37's gradient (default model) | 0.689 / 0.0996 / 0.0799 / 0.0562; -0.103318 -> 0.690 / 0.0993 / 0.0782 / 0.0552; -0.103575 | not measured |

By luminosity on milky_way (median radius, batch Q -> S104): under 1e35 erg/s 7.81 -> 3.07 pc; 1e35-36 11.26 -> 3.87;
1e36-37 12.13 -> 7.44; 1e37-38 12.73 -> 11.91 (35 % of these past 4 Myr); 1e38-39 21.99 -> 21.70; above 1e39 unchanged.

**What it does and does not do, plainly.**
1. It removes the named inconsistency and shrinks the regions below 1e37 erg/s by 2-3x (mostly old regions whose
   rate has fallen). It does **NOT** bring the slope above Barnes et al.'s completeness into range: over log L ≥ 38
   (their 50 % point, Sect. 4.1 as read in S103 — a disclosed cut, not a fit) 0.254 -> **0.268** on milky_way (0.243 ->
   0.250 on ngc_4414) against their 0.47-0.52. Those regions are young and the model's rate is flat to 4 Myr, so the
   mend barely reaches them. Below log L 38 Barnes's catalogue is 5-50 % complete and by the authors' word misses the
   diffuse extended regions: the faint decade's comparison (11.9 pc against Eq. 1's 11.6, Eq. 3's 4.7) is disclosed,
   not a target. Units of r and L in their Sect. 5.1 are still `[inferred]` (pc, erg/s).
2. The `[inferred]` steps: recombination instantaneous; the cavity's gas held at n_i; a capped shell's density by
   photon balance at the peak rate at the cloud's edge. The shell is driven at the peak rate for the whole age, even
   after the rate has fallen, so it overshoots what a falling source would drive.
3. **The table's flat first 4 Myr is an isochrone floor** (`per_mass_at` reads the youngest isochrone for the first
   4 Myr), where Starburst99's instantaneous burst (912_inst_b.dat, col. 2, S103's reader's READ row) falls 32 % by
   3 Myr. It is the next cause to look at for the bright, young regions' sizes; **not mended here**.
4. The shell's limits move: on milky_way stagnation now binds 4 % of the regions (was 32 %) and the cloud 73 % (was
   45 %), because R_STAG scales with R_St, now the peak rate's (larger by (Q_peak/Q_now)^(1/3), median 2.8x): the
   stagnation radius moves past the cloud's edge for most aged regions.
5. A2, Williams et al. 2018 eq. 48: READ, not built (above).
