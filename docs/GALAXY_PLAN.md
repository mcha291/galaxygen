# Galaxy generator — implementation plan

## Status

`█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░` **58 / 67 sessions** · repo initialised: yes

| | S | Session | Surface | Model planned | Model used | Tag | Closed |
|---|---|---|---|---|---|---|---|
| ☑ | 0 | Instruments, registry, stub second model | desktop | **Fable** | **Fable** | s00 | 2026-09-03 |
| ☑ | 1 | Halo & disc | web | Opus | **Opus 5** | s01 | 2026-09-02 |
| ☑ | 2 | SFH & chemistry (simple) | web | Opus | **Opus 5** | s02 | 2026-09-03 |
| ☑ | 3 | Assembly & mergers | web | Opus | **Opus 5** | s03 | 2026-09-03 |
| ☑ | 4 | Pattern: bar, arms | web | Opus | **Opus 5** | s04 | 2026-09-03 |
| ☑ | 5 | Systems: catalogue | web | Opus | **Opus 5** | s05 | 2026-09-03 |
| ☑ | 6 | API | web | Opus | **Opus 5** | s06 | 2026-09-03 |
| ☑ | 7 | Viewer, galaxy view, stage previews | web | Opus | **Opus 5** | s07 | 2026-09-04 |
| ☑ | 8 | Planets & system view | web | Opus | **Opus 5** | s08 | 2026-09-04 |
| ☑ | 9 | Advanced model | desktop | **Fable** | **Fable 5.1** | s09 | 2026-09-04 |
| ☑ | 10 | Audit | desktop | **Fable** ×2 | **Fable 5.1** (runs 1, 2) | s10 | 2026-09-05 |
| ☑ | 11 | Integrate the S10 audits (beta, the gamma pair) | desktop | — | **Fable 5.1** | s11 | 2026-09-07 |
| ☑ | 12 | The maintainer's one-line fixes (D-9, D-13, #33, #35, #37, #40) | desktop | — | **Fable 5.1** | s12 | 2026-09-07 |
| ☑ | 13 | The physics decisions: step infall, Sagittarius, c_vir → c₂₀₀, hydrogen, the median criterion; bulge and catalogue probed | desktop | — | **Fable 5.1** | s13 | 2026-09-07 |
| ☑ | 14 | The halo contracts around the disc (#6; row 3 turns round, wants z_f 0.7–1.0); the extended component probed (#18) | desktop | — | **Fable 5.1** | s14 | 2026-09-07 |
| ☑ | 15 | Row 3's cause, derived: the epoch's default from the ΛCDM median (2.5 → 1.66, #12 discharged); the calibration ruled out as the lever (#46); row 3 at 260.1 under #11 with the bulge and the component its prediction | desktop | **Fable** | **Fable 5.1** | s15 | 2026-09-09 |
| ☑ | 16 | The extended component, derived as the high-j tail of the halo's angular momentum (#18 discharged, #47 opened); the timescale was not the decision; the derived threshold probed for S18 | desktop | **Fable** | **Fable 5.1** | s16 | 2026-09-09 |
| ☑ | 17 | The spheroid derived as the low-j end of the halo's angular momentum, and M_• (rows 10–14, 18; #17 discharged for row 14, #48 opened); the bulge is worth 1.6 km/s and not D110's 5–8, so row 3 misses by 0.3 and rows 3 and 12 have one cause | desktop | Opus | **Opus 5** | s17 | 2026-09-09 |
| ☑ | 18 | The thick disc: the merger's radial kick derived and built (worth 0.3 kpc on row 5; its prediction dead, #19), Kennicutt's threshold derived (#47: the gas rows land, row 9 leaves), the basis-free disc solver; row 3 landed on the kick; the shape is the first infall's (#49 opened) | desktop | **Fable** | **Fable 5.1** | s18 | 2026-09-10 |
| ☑ | 19 | The catalogue migrates: birth radius **and birth time** drawn together from the chemistry's backward weights (#31 discharged, #32 re-ruled, #50 opened); the thin/thick criterion published; every published field previewed, in both models | web | Opus | **Opus 5** | s19 | 2026-09-10 |
| ☑ | 20 | The valley probed six ways, the repo unchanged, and not opened: every valley the detector finds is the plateau spike, the early population a plain (#27's prediction replaced; #49's killed, #26 and the drain ruled for S22); `MERGER_HEATING` derived from the thick disc's dispersion net of the secular heating (120 → 88.8, #42: row 7 lands, row 3 leaves by 0.03) | desktop | **Fable** | **Fable 5.1** | s20 | 2026-09-11 |
| ☑ | 21 | Audit II, run twice with two stated aims on two sealed branches, never merged into each other (§5d, D99). **(a)**, `session-21-a`: every prediction since S13 run with the repo unchanged — #50's dead and its bracket was a fraction read as a ratio, the bar holds row 3 (249.6) and kills row 14 (144), D128's burst works at 1–2 Gyr and not in the first, #46's sweep cannot judge; #51–#52, D130–D131, `AUDIT_II_A.md`. **(b)**, `claude/keen-lamport-lldlvp`: the instruments and the viewer — rule D4 counted at the stages and found honest, the catalogue priced per **cell** so D115's flake is a misfit, the detector's blind spot in closed form, four fields the viewer cannot show; #65–#73, D144–D150, `AUDIT_S21B.md`. S22 ports both | desktop + web | **Fable** ×1, Opus ×1 | **Fable 5.1** (a), **Opus 5** (b) | — (D99) | 2026-09-11 |
| ☑ | 22 | Close-out. Both S21 lists **ported** onto `main`, neither branch merged (D99); the two lists diffed (D158); **every open debt ruled — 17 discharged, 15 permanent, 12 carried, none unruled** (D159), with #79 opened at the checklist: acceptance row 21 is published by no stage of either model and has never been judged; two of S21 (a)'s own conclusions corrected and one cross-list finding neither run could reach (D160). **The tag batch was still owed** — attempted here and refused, HTTP 403 on a tag ref, D40 reproduced (D161); **run from the desktop on 2026-09-27 on the owner's word, 39 tags listed under D161, ticked at S42's close (D192)** | web | Opus | **Opus 5** | s22 | 2026-09-12 (◐ until 2026-09-30) |
| ☑ | 23 | **Recorded retrospectively (D171).** The viewer rebuilt as a Vite + React + three.js app with the workflow, per-checkpoint previews, the formation-history scrubber (RENDER_PLAN H1) and a PSF (R2); the bar and arms published as an (R, φ) density contrast with **two experimental amplitude inputs** (M1); histories at 200 steps; the Azure deploy; the repository restructured into `docs/`, `model/`, `interface/` (0f78156). No session branch, no decision entries at the time | desktop | — | **Opus 5** | s23 | 2026-09-13 |
| ☑ | 24 | **Recorded retrospectively (D171).** The render plan's model side: the PARSEC table and per-star photometry (M2, D164); the `ism` stage, #79 revisited and discharged, row 21 judged for the first time (D163); the disc's unresolved light, dust and bloom (D165); Hα and the bulge's light (D166); the ray-marched field regime and the three regimes (D167); the brightest-N mode (D168); [α/Fe] on the catalogue (D169); **one model, `basic`** (D170). Ran on `main` with no session branch | desktop | — | **Opus 5**, Opus 5.5, **Fable 5.1** | s24 | 2026-09-25 |
| ☑ | 25 | **BUILD_II Phases 0 + 1.** A1 rewritten — the stage graph acyclic, iteration inside a stage when termination is guaranteed; the 8× it cited was never measured (D173); **#26 and #3 re-ruled carried**: a probe shows the retained budget is the root of a contraction map inside checkpoint 1, f* 0.338 against the input's 0.35. The pattern branch ahead of `sfh` on the checkpoint-1 curve **and the λ_d scale length** (the plan missed the second `sfh` field); **checkpoints 3 and 4 swap** (Pattern, then star formation) so Phase 2 can read the pattern; rows 15–17 measured before and after — **row 15 4.883 → 5.210, out by 0.01, recorded under new #80** (a recalled ratio's referent moved; not retuned), 16 and 17 pass; the arm number's 2-or-4 draw recorded (D174) | desktop | **Fable** | **Fable 5.1** | s25 | 2026-09-26 |
| ☑ | 26 | **Phase 1b.** The swing-amplification window derived from `disc_dominance` and `shear_rate` (X₂ = 2/f_d, the review's 1/f_d ≤ m ≤ 2/f_d); the arm number drawn from {2…6} with odds the window sets — 2 or 3 at the defaults, four to six for a halo-dominated disc (flocculent reachable); the arm amplitude's mean derived from the window between the flocculent and grand-design arm–interarm contrasts (Elmegreen+ 2011, recomputed from Table 2), residual seeded; the bar amplitude seeded about the S4G median A₂ (Díaz-García+ 2016, 587 rows reduced); **`arm_amplitude` and `bar_amplitude` removed, 7 controls**; rows 15–17 unmoved; **#23 discharged** (D175) | desktop | **Fable** | **Fable 5.1** | s26 | 2026-09-26 |
| ☑ | 27 | **Phase 2.** `sfh_azimuthal` **extends** `sfh` (new `Stage.extends`: the shared histories computed by `sfh` in its own view, so they stay derived) and publishes one (R, φ) field, `sfr_modulation` — the law applied per cell to gas that follows the contrast, ring mean 1 to 10⁻¹⁶, total SFR conserved to 10⁻¹⁶ (the plan's "gas-weighted mean 1" and "integrates to the axisymmetric SFR" cannot both hold; the gate's chosen); the `azimuthal` model from `BASIC`'s tuple, one slot different; every acceptance row identical in both models; the catalogue's young stars (< 0.1 Gyr, #81) placed by the modulation with cell counts and names unchanged; the toggle returns data-driven; timings' dead `advanced` rows now measure `azimuthal` (D176). Built by an Opus subagent in a worktree, reviewed and closed by the orchestrator | desktop | Opus | **Opus 5.5** (subagent), Fable 5.1 (review, close) | s27 | 2026-09-26 |
| ☑ | 28 | **Phase 3.** The PARSEC table gains U B V R I J H K, M_bol and the present mass (1.1 → 3.2 MB, the old columns bit-identical); the galaxy's magnitudes in eight bands, B − V, Υ_V, a V scale length (4.40 kpc against the mass's 2.44), BC_V = −0.838 closing on the bolometric light to 2e-5; **Q(H⁰) by ruling (a)**: SHP03 Table 1 entered verbatim, the blackbody the named alternative (O5 0.92×, B0 0.36×), the table governs a third of the budget and the unseen > 64 M☉ stars about half (#84); Vink's wind without Γ_e (#83); the Wolf–Rayet proxy; **rows 25–28 not-yet-computable by ruling (b)** — BHG16 Table 2 never says its magnitudes are extinction-corrected (#82) — and **row 29, the Tully–Fisher slope over a sweep of `halo_mass`, passes: −7.91 against Sakai 2000's −7.85 ± 0.71** (the `sweep` mode, the first population row); the light stage's step-centre read did not converge and is now step-averaged (D177) | desktop | Opus | **Opus 5.5** (subagent), Fable 5.1 (review, close) | s28 | 2026-09-26 |
| ☑ | 29 | **Phase 4.** `star_remnant` (none / white dwarf / neutron star / black hole / planetary nebula) and `star_remnant_mass` on the catalogue by Cummings+ 2018's PARSEC initial–final mass relation, Smartt 2009's 8.5 and Heger+ 2003's 25 M☉ boundaries, Özel's measured 1.33 and 7.8 M☉ (metallicity dependence unread, #86); planetary nebulae flagged by Badenes+ 2015's 27 kyr, 1.47 × 10⁴ in the galaxy; `remnant_mass_fraction` 0.2147 as a population integral; **the finding: locked mass is 84% stars + remnants — the isochrones return 0.41 against the instantaneous 0.30 (#85, not retuned)**; row 30 owed to Audit III (local Σ_WD 4.757 vs McKee+ 2015's 4.9 ± 0.8, read before it could be ruled, #87); dead is the table's NaN; the population stage now waits on the chemistry (D178) | desktop | Opus | **Opus 5.5** (subagent), Fable 5.1 (review, close) | s29 | 2026-09-26 |
| ☑ | 30 | **Phase 6.** `supernovae` stage: core collapse as SFR × the Kroupa stars above Smartt 2009's 8.5 M☉, type Ia as the chemistry's own DTD convolution counted at Maoz & Graur 2017's 0.7 M☉ of iron per event (one function both stages call); **rows 30–31 pass against Adams+ 2013** (1.76 and 0.653 per century in 3.2 (+7.3, −2.6) and 1.4 (+1.4, −0.8)) — the Ia pass thin: the disc makes 1.87× the measured Ia per mass formed because `Y_FE_IA` is a recalled yield (#88), the spheroid's Ia are missing (#89); the galactic habitable zone built from Gowanlock+ 2011's criteria (Lineweaver 2004 unreadable) and deliberately unjudged, its eq.-5 reading an open debt (#90); three units. Ran in parallel with S29 and merged after it (D179) | desktop | Opus | **Opus 5.5** (subagent), Fable 5.1 (review, close) | s30 | 2026-09-26 |
| ☑ | 31 | **Phase 7.** `dust` stage: one grain model (WD01/Draine 2003, R_V 3.1) read from Draine's own table — albedo_V 0.677, g 0.538, FUV extinction and albedo, κ(156 µm); the heating balance inverted in closed form (T_d 15–21 K across the disc, 19.5 K at R₀), the infrared emission integrated by quadrature so the **energy balance is asserted to 10⁻¹² per radius and 10⁻¹⁵ in total**; L_IR 1.62 × 10¹⁰ L☉ = 0.33 of the disc's light; G₀(R₀) 2.6; PAH fraction by Rémy-Ruyer+ 2015's metallicity fit (9% at R₀, twice Draine & Li's; #92); g published as a scalar for V2 (ruled); the slab absorbs grey (#91); row 32 owed to Audit III (#93); three units; `expn` in core (D180) | desktop | Opus | **Opus 5.5** (subagent), Fable 5.1 (review, close) | s31 | 2026-09-26 |
| ☑ | 32 | **Phase 8.** `clouds` stage: the molecular gas as a census of 1.67 × 10⁴ objects (`of="cloud"`, the vocabulary widened) drawn per cell — Rice+ 2016's truncated power law inner/outer, Heyer+ 2009's Σ = 42 and size–linewidth, Mach 5–30 at 10 K, Federrath's b = 0.4, Kawamura+ 2009's three phases as the state; the mass in clouds is 1.037 of the ISM's molecular mass, inside the count's noise (#94: all gas in clouds from an unsourced 10⁴ M☉; #95: source offset, gradient, height, no remnant state unsourced). **The cell hierarchy**: `level=` 0–3 on `/api/region` and `/api/system`, a child holding its parent's stars plus its own at 4^k the density; union, prefix and determinism asserted at every level, the level-0 catalogue bit-identical; `/api/clouds`; three timings rows (D181) | desktop | **Fable** | **Fable 5.1** | s32 | 2026-09-26 |
| ☑ | 33 | **Phase 11.** `clusters` stage: 1.29 × 10⁴ young clusters as an object class (`of="cluster"`), one per cloud past its embedded phase, named by the new `cloud_cluster_index`; mass at an efficiency **derived** from the local depletion time over one cloud lifetime (0.0206 galaxy-wide; Murray's adopted 0.08 rejected after it made the clusters form 4.5× faster than the SFR), bound 7% (Lada & Lada 2003), half-mass density 10³ (PZMG 2010); Q and wind per cluster are IMF integrals at the cluster's age — **ΣQ / the light stage's young Q = 1.0088**, every residual factor named; `bound_cluster_mass_total` 72× η M_halo before survival (#97); the census inherits the cloud slopes, not β = 2 (#96); `/api/clusters`, two timings rows (D182) | desktop | Opus | **Opus 5.5** | s33 | 2026-09-26 |
| ☑ | 34 | **Phase 5.** `stellar_halo`, `cluster_survival`, `globular_clusters` stages: the GC system mass = S33's bound mass × Lamers 2005's survival (open-cluster t₀ 3.3 Myr, γ 0.62; PZMG's function from 10² M☉) — the mean **+0.26 dex from η M_halo, inside the 0.28 dex scatter, but 53% of the survivors are under 1 Gyr and 0.7% over 10 Gyr** (#97 stays; the old survivors alone read −1.87 dex, +0.09 at the N-body t₀); the residual seeded on `world_seed`; metal-poor share 0.643; stellar halo 3.0 × 10⁹ from `mergers[]`, satellites whole; **rows 32 (Harris, 0.47 dex high, #98) and 33 (BHG16, 0.64 dex high, #99) recorded misses**; spec 10/19/4 of 33 (D183) | desktop | Opus | **Opus 5.5** | s34 | 2026-09-26 |
| ☑ | 35 | **Phase 9.** `nebular` stage: every cluster's HII region as the §3a shape parameters (R_S, n_e rms, T_e from metallicity, log U, clumping e^σ_s², O/N/S) and its Hα **per unit volume** (new units `1/cm3`, `erg/s/cm3`), Case B from Storey & Hummer's own rows (Hα/Hβ 2.863, 0.452 per photon); the diffuse layer from a 30% escape (Zurita/Haffner); the galaxy's Hα as Σ_Q redistributed, census = field to 0.990 (noise 0.059); `HALPHA_PER_SFR` now a check reading **0.71** (the isochrones' Q vs Starburst99's, #100); emissivity ruling: Byler+2017/FSPS grid of the isochrone kind, **its fetch awaiting the owner's word, the forbidden lines with it**; rows 34 (Bennett Q, miss by 3%, #100), 35 (KEH89 slope, −2.008 pass), 36 (PNLF, n-y-c); DIG by construction #101 (D184) | desktop | **Fable** | **Fable 5.1** | s35 | 2026-09-26 |
| ☑ | 36 | **Phase 10.** `bubbles` + `feedback` stages: Weaver+1977's bubble per cluster at its mean injected power (winds + 10⁵¹ erg per core collapse), **stalled at the ionized gas's sound speed** (12 521 of 12 860; median 9 pc), the shell's density, thickness, T, P and photon-limited Hα per volume; the supernova-remnant census (`of="remnant"`, OBJECTS widened): 1 464 vs 1 448 expected from Phase 6's rates × Frail's 60 kyr, Sedov (ξ 1.15167) then Cioffi's snowplow, radius 1.8–59 pc; `hot_phase_porosity` 0.033 at R₀; `gas_midplane_density` = P/σ² on ism; `star_bubble_radius` on the catalogue (254 fields bit-identical); `/api/remnants`; #102 (remnants untied from clusters, no arms), #103 (lifetime-set count, inferred shell) (D185) | desktop | Opus | **Opus 5.5** | s36 | 2026-09-26 |
| ☑ | 37 | **Audit III** (`docs/AUDIT_III.md`). 63 constants re-read at their sources by a read-only agent: **46 match, 2 differ, 10 adopted-not-measured, 5 misattributed**; every module table matches. Findings: a dropped square root makes the Ia sterilization volume 12.6× too large (#104); η = 3.5 × 10⁻⁵ is Boylan-Kolchin's assumption, the measurement 2.9 ± 0.2 puts S34's GC mass 0.34 dex outside (#105); five misattributions (#106). 13 redistributions re-derived at GridSpec(180, 600, 8), all inside their noise (`tests/test_audit_iii.py`); greens 29/30/31/35 conditioned, row 31 dies at the measured Ia efficiency; rows 32 and 34 read blind: [2.7, 4.0] × 10⁷ (model misses) and McKee & Williams' [1.3, 3.9] × 10⁵³ (model passes) — the owner's ruling; #80–#103 re-stated. No number moved (B3) (D186) | desktop | **Fable** | **Fable 5.1** | s37 | 2026-09-26 |
| ☑ | 38 | **V1.** The filter integral runs server-side (option (a), the ruling §0 left open): `/api/render` takes the viewer's filter curves and returns per-cell responses per component (stars, Hα, dust), never composited; the stellar spectrum per cell is the population's **eight-band SED** (16 new light fields, SVO band definitions read from pages, band-consistent joins) — **frame B − V 0.630641 vs 0.630552, M_V −21.216042 vs −21.215871, tolerance 10⁻³** (the first cut's single blackbody missed M_V by 0.71 mag and was sent back); viewer: Filters selector RGB/SHO/HOO, the young-light invention removed; left for V2: the line's knots, the dust's clumps, per-filter extinction (#108); the SED's joins inferred, 0.71 of L_bol (#107); no named instrument (a download, the owner's). Opened with Audit III's fixes applied (D187) | desktop | Opus | **Opus 5.5** | s38 | 2026-09-27 |
| ☑ | 39 | **V2.** The dust in three components — extinction per filter from Draine's grain table (110 rows transcribed into `spectra.GRAIN_TABLE`, the table was not in the repository), scattered light by the slab's own convention (the ruling's optically-thin form scattered 12× too much at the centre and was set aside), thermal emission through the filter — and the line in two volumetric layers (HII in the clouds' layer, DIG at 1.4 kpc); **the frame's energy balance closes to 7 × 10⁻⁴ and the face-on Σ_V(R) to 10⁻³ per ring**; the V1 gate unmoved; the viewer's knots, clump lattice, dust lead and `CHANNEL_EXTINCTION` removed — **nothing structural is invented at galaxy scale**; the dust in the stars' layer, the IR set measured not drawn (#109) (D189) | desktop | Opus | **Opus 5.5** | s39 | 2026-09-27 |
| ☑ | 40 | **V3.** The region regime below 4 kpc draws the censuses from their published vectors: the level follows the view's width (one per factor four under 4 kpc); each cloud a log-normal interior at the published σ_s seeded by its (cell, index) path, its cluster's Strömgren cavity carved and the clumps above e^σ_s inside it left as pillars; HII spheres and bubble and remnant shells marched per pixel (limb-brightened for free); the field's HII fades inside the window; `cloud_extinction_v` 2.97 mag, one scalar; the census routes name every row and a level filter's header counts the body (a defect since S32). **Catalogue against field 0.980 (disc) / 0.974 (level-1 sector); sixty level-1 windows z mean +0.15 against the census's own σ(N); a census identical at levels 0–3.** Stated: stars stay on the level-0 sample, a screen-space composite, a display budget of 256 objects, the noise's shapes inferred (#110–#113) (D190). Built across a usage limit: rulings before it, review after | desktop | **Fable** | **Fable 5.1** (rulings, review) / **Opus 5.5** (build) | s40 | 2026-09-30 |
| ☑ | 41 | **V4.** Clusters drawn as objects: two columns on the cluster census — `cluster_luminosity` (mass × the light per mass formed at its age and [Fe/H], the light stage's tables) and `cluster_light_temperature` (that light's correlated colour temperature) — and a point of that light in the region regime, painted as a star is, the census loaded once and shared with the region volume. **The #69 gate extended to the object classes: every `of="cloud" / "cluster" / "remnant"` column is drawn (25) or carries "Not drawn by the viewer" with why in its declaration (38: through what it sets, invisible to a filter, or owed), asserted per model.** Rulings P1–P5 proposed by Opus before the build and ratified at the review with two findings measured there: the ramp's painting is bolometric — the census summed reads 2.1× its own G light through the viewer's filters, +0.18 mag at the youngest to +1.31 at the oldest (#114, D188's finding left in the point regime; S42's P6 keeps it) — and the clusters hold a quarter of the disc's light that the sampled catalogue barely carries (7 stars under 20 Myr in a 2 kpc window), half of them dissolved yet pointed (#115); the cluster's extent unpainted (#116). #111 not closed by V4. `halpha_surface_brightness` retired (RENDER_PHYSICS §0). Instrument PSFs and the tag batch the owner's (P2, P4; the batch ran on 2026-09-27 — 39 tags on the remote — recorded at S42's close). Both models draw both regimes (P3). Specs 11/20/5 unchanged (D191) | desktop | Opus | **Opus 5.5** (proposals, build) / **Fable 5.1** (rulings, review, close) | s41 | 2026-09-30 |
| ☑ | 42 | **The owner's four answers of 2026-09-27, built on Opus while Fable's limit reset, ruled at Fable's review.** (1) "download it": Byler et al. 2017's nebular grid as FSPS ships it, pinned (`tools/fetch_nebular.py` → `data/nebular_lines.npz`); the nebular stage reads it per region, clamped, and publishes the four forbidden lines over Hα, per-ring lines and Hβ in both layers; `/api/render` carries `lines_hii` / `lines_dig`, `absent.lines` is empty, each resolved region coloured by its own lines — **30 object columns drawn, 37 ruled not drawn**. (2) "follow the audit's recommendation": rows 32 and 34 take Audit III's blind windows (`AUDIT_III_BLIND.md`), row 34 passes on McKee & Williams 1997 and its miss is removed with the reason written, row 32 still misses (#98 re-read: 0.25 dex above the blind top, η M_halo now inside); **specs 12/19/5 of 36, both models**. (3) "yes": HST WFC3/UVIS's six system throughputs from SVO (`tools/fetch_filters.py` → `instruments.json`, sets `wfc3`, `wfc3n`) with an Airy sprite per channel. (4) "run the tag batch for me": run 2026-09-27, 39 tags on the remote, `s06`'s literal corrected, the listing under D161, S22 ☑. Then a form-encoded POST as the GET past 4 KB (an API change, ratified) and **P6 ratified**: stars and clusters drawn through the filter set by `/api/blackbody`'s share table, the exposure rule left on bolometric L as a stated display choice; **P6 does not close #114** (the blackbody's bolometric correction stays). #108 discharged, #100 re-scoped to the 0.71, #117–#120 opened (D192) | desktop | Opus | **Opus 5.5** (build) / **Fable 5.1** (rulings, review, close) | s42 | 2026-09-30 |
| ☑ | 43 | **The owner's choice of 2026-09-30, then Audit IV** (`docs/AUDIT_IV.md`). Tags per session from now on — rule C2e amended, `s40`–`s42` on the remote, the queue retired (D193). Then the renderer S38–S42 audited in Audit III's shape, the aim written before any source file was opened: 20 items re-read at their sources by a read-only agent — **12 match, 4 differ, 4 adopted**; 103 of the grain table's 104 rows match. Findings: **the nebular grid is read 0.24 dex too metal-rich** (Byler's log Z = 0 is Anders & Grevesse's 8.93, the model enters oxygen − 8.69: on the grid's scale 3.0 % of regions clamp, not 26.4 %; #121); **FSPS clamps, it does not extrapolate** — D192's sentence was wrong (#122, the record); one grain row misplaced (#123); STScI's WFC3 curves are vacuum and the model's lines air (#120 half decided); CMD's U B V are Maíz Apellániz 2006's, not SVO's Bessell (#107). Thirteen gates re-derived at `GridSpec(150, 500, 10, 240)`, all inside the mesh's own cost (`tests/test_audit_iv.py`; the render's light the same across levels, first checked); greens conditioned (V1 green by its passes, V2 by one function, V3 survives re-tiling, row 34 strengthened by the 0.71). **The forbidden-line row set blind** (`AUDIT_IV_BLIND.md`): d log([N II]/Hα)/dR over 8.2–15.4 kpc = −0.025 ± 0.009, window [−0.045, −0.005] dex kpc⁻¹ (Zhao et al. 2026, verified at the source); the model, measured after, reads −0.0815 — a 4σ miss for the next session's row 37 (#117). No number moved (B3) (D194) | desktop | **Fable** | **Fable 5.1** (rulings, aim, review); the two readers Opus 5.5 | s43 | 2026-09-30 |
| ☑ | 44 | **Audit IV's fixes** (D195; B3: S43 checked, S44 fixes). Rulings first, as the first commit: **#121** the grid's axis entered on its own total oxygen 8.93 (Byler §2.1.2 on Anders & Grevesse; `NEBULAR_GRID_OXYGEN_SOLAR`) — 3.0 % of the regions clamp (26.4 % before), Hα-weighted [O III]/Hα 0.752 (0.477), [N II]/Hα 0.082 (0.131), [S II] unchanged; **#120's convention** as a `wavelengths` key on a curve, vacuum on the WFC3 sets (IHB §6.5) and honoured by `line_response` through Morton 1991 — Hα in F656N 0.945 (0.962), [O III] in F502N 0.899 (0.903), the curves not shifted; **#123** the grain row corrected from the file, the keys pinned to the file's list and the far-infrared run bounded (1.4× each way); **#122**'s nine sentences, D192's "FSPS extrapolates" corrected in D195, one solar mass; **row 37 entered blind-with-disclosure as a recorded miss under #117**: `nii_halpha_gradient_hii` −0.1035 dex kpc⁻¹ against the blind [−0.045, −0.005], 6.5σ — steeper than the −0.0815 S43 measured, the offset moved it out, not in. Specs **12 / 20 / 5 of 37**; vitest 121; 62 open = 11 + 51, 44 discharged | desktop | **Fable** | **Fable 5.1** (rulings, review, record); three builders Opus 5.5 | s44 | 2026-10-01 |
| ☑ | 45 | **Row 37's diagnosis by the miss's own prediction** (D196; the owner's choice of 2026-10-01), the aim and the readings R1a–c / R2 / R3 written before any number. `tests/test_s45_diagnosis.py` (an Opus builder) reproduces the published −0.1035 to 0.0 and takes it apart: **the metallicity path is the whole gradient** (age and U frozen −0.1177, Z frozen −0.0016, mixing −0.0005); the grid responds at **1.22 per dex of log Z, 0.70 of PP04's empirical 1.75** — not too steep; the regions' oxygen gradient is **−0.078 dex/kpc, steeper than the Cepheids' −0.064 ± 0.003** by 0.014 (worth −0.017 of the ratio gradient; **#124 opened**). At the Cepheids' gradient the model would still read −0.078, 3.7σ out: **the miss has two named parts** — #124's bounded share and a conflict between LAMOST's N2 gradient and the Galaxy's Cepheid abundance gradient, preserved as rulesets (B12). #117 re-described, its closer a blind direct-method HII-region O/H gradient; row 37's miss text rewritten. Option 4: `prod` checked through the real transport (vacuum echo, 0.9453 / 0.8987, row 37's scalar), the image built by CI, the deploy command in BRIEF. No number moved; specs 12 / 20 / 5 of 37; 63 open = 11 + 52, 44 discharged | desktop | **Fable** | **Fable 5.1** (aim, readings, ruling, record); the instrument Opus 5.5 | s45 | 2026-10-01 |
| ☑ | 46 | **The viewer reviewed and begun** (the owner's choice of 2026-10-01: the model pinned, the viewer finished). `RENDER_PLAN_II.md`: where the viewer stands (a survey of the code, a walk of the built viewer on `prod`, the design record: one of 21 design components ported, no image-level test, the stars regime black in the app's pane with five WebGL context losses), every candidate costed, a sequence proposed (D197 (1)). Built: **`azimuthal` the default** across the registry (`put_first`: a default built from another declaration imports last), the API, the specs' order, the viewer and the tests' default run — no measured pin moved, the models sharing every field but the star columns (D197 (2)); **the field march's terracing fixed** — each step's layers read at jittered sub-samples (n by the step's in-plane length over the plane cell, ≤ 8), the exact column per sub-interval, the box at 16 h; the old march was off a converged reference by up to 8 × 10⁻³ at grazing views, the new within 2 × 10⁻⁴ (the builder's WebGL harness); verified on `prod` before and after (`design/screenshots/s46/field-grazing-*.jpg`) (D197 (3)); **the viewer lands on the Galaxy view of the default galaxy and "Edit galaxy" opens the staged process** — rule D1 amended on the owner's word, the reference client keeping stage one (D198). No model number moved; specs azimuthal first, 12 / 20 / 5 of 37 both models; vitest 131; 63 open = 11 + 52, 44 discharged | desktop | **Fable** | **Fable 5.1** (review, rulings, record); three builders Opus 5.5 | s46 | 2026-10-01 |
| ☑ | 47 | **The tuning panel and the one task list** (D199). The field view's display choices as sliders for the owner to find the combination by eye — march resolution, pixel budget, steps, sub-samples, dither, filtering; field gain and floor, white point; bloom and tone mapping; sprite size and point gain — today's values as defaults in one module (`tuning.ts`), the default shader byte-identical to S46's once its three declared edits are undone; verified on `prod` before it reached the owner's tab. `docs/VIEWER_TASKS.md`: every remaining viewer task in one list (T1–T23). The "brightest" view reviewed as a base: **its stars are the brightest of a one-in-10⁵ number sample** (the top 3 162 carry 86–94 % of a pool whose light is 10⁻⁵ of the galaxy's). **The owner lifted the model pin for two pieces** — the bright-end-complete selection and the photometric points with single counting — S48's (D200). No model number moved; vitest 140; 63 open = 11 + 52, 44 discharged | desktop | **Fable** | **Fable 5.1** (ruling, review, record); the panel Opus 5.5 | s47 | 2026-10-01 |
| ☑ | 48 | **The bright-end-complete star catalogue and the per-object filter response** — the two model pieces the owner lifted the pin for (D200–D203). One decomposition, the mass formed on each isochrone, reproduces the light stage to 10⁻¹³; the luminosity function along each isochrone's own points; **the bright catalogue as an ordered Poisson process per finest cell** (`stages/bright.py`, stage `bright_stars`, `/api/bright`): complete above a threshold, a prefix by 0.05 dex interval, per-region; ages under 20 Myr left to the clusters. The 3 162 brightest disc stars are everything above 33 960 L☉; 3.35 × 10⁶ stars above 10³ L☉. **`spectra.object_response`**: the field's filter machinery factorised into one-dimensional tables, within 2 × 10⁻⁵ mag of the exact integral in five sets, 10⁵ objects in 0.7 s (D201: the ruled linearisation failed its own gate and was replaced). **The wiring**: `filters=` on `/api/bright` and `/api/clusters`; `l_min` on `/api/render` returns the unresolved remainder — **unresolved + young + bright ≡ the total to 10⁻¹³**, the clusters carry 0.985 / 0.990 / 1.000 of the young light through rgb; at 10³ L☉ the disc's light is 24.6 % young, 18.4 % bright, 57.0 % unresolved. D203: the first draw left the stars too red (B 0.83 of budget); a star's segment is now drawn by its exact count in the interval and every band is within 1σ. **Found: the field's light tables alias the giant branch — the disc's light is 6.7 % high bolometric, 5–12 % by band (#126, registered, the owner's word asked);** the SED's band curves cannot hold the steepest spectra (#125). Specs 12 / 20 / 5 of 37; 65 open = 11 + 54, 44 discharged | desktop | **Fable** | **Fable 5.1** (design, rulings, review, record); four builds Opus 5.5 | s48 | 2026-10-01 |
| ☑ | 49 | **The field's light tables fixed on the owner's word** (#126, D204: "go with option A, fix it now"). `population_light` integrated along each isochrone's own points — one quadrature in `photometry.py`, shared with the bright catalogue, whose renormalisation and second budget are gone (its totals equal the field's exactly). **The disc's light 4.8958 → 4.5898 × 10¹⁰ L☉ (−6.25 %), M_V −21.216 → −21.110, B − V 0.631 → 0.569, Υ_V 1.85 → 2.04, the bulge's light −42 %** (one old isochrone took its whole error), the radial profile no longer jagged ring to ring (the old K anchors read 32 / 23 / 4 at 5.7 / 7.5 / 9.4 kpc); T_d(R₀) 19.5 → 18.8 K, L_IR 1.62 → 1.57 × 10¹⁰; the light at 10³ L☉ 26.3 % young / 18.8 % bright / 54.9 % unresolved. 43 pins re-read with reasons; **no acceptance verdict changed** (12 / 20 / 5 of 37), no gate or identity failed, no constant had been fitted to the old tables. The independent brute-force gate: 6.3 × 10⁻⁸ on the same reading, 1.13 × 10⁻³ against the IMF-weighted trapezoid — recorded, not loosened (#127). 65 open = 11 + 54, 45 discharged | desktop | **Fable** | **Fable 5.1** (ruling, review, record); the fix Opus 5.5 | s49 | 2026-10-01 |
| ☑ | 50 | **The star-first viewer mode, after a side track on the owner's word** (D205–D209). *Sidetrack session 1* (branch `sidetrack-session-1`, D205–D207): the brightest mode's component layers (starlight, ionized gas, dust as it acts and where it is, the cloud census, the cell outlines), the filter sets and a stars switch in that mode, `docs/RESEARCH_AREAS.md` (the spiral's shape a template), **the dust in its own layer** — `gas_scale_height` per ring, Σ/4ρ₀, 113 pc at R₀, missing past the stellar disc's edge; `/api/render`'s `dust_height`; the march composing light and dust in order (0.6 % of the two layers' integral) — so an inclined disc shows the lane (#109's layer closed, **#128 opened**: the heating is still one mixed slab, the layered geometry would absorb 0.766 of it), and **the dust placed round each ring** by the pattern's contrast (`dust_placement`: the arms muted and reddened, not laned). *S50 proper* (D208): **the star-first mode** replaces brightest — the N brightest disc stars in view and every cluster as points of their own light through the set, each sprite summing to its light over the sky one pixel covers there, over `/api/render?l_min=`'s remainder; one exposure; the dust in front of each point (T20); a click opens the object's columns (T23). **The closure on screen 0.9995 / 0.9997 / 1.0006** through rgb (`window.__galaxygenFrameSum`). D209: clicking a star to open its planetary system removed. T12 not built (no headless browser); **the full suite was not run at the close, on the owner's word** (last `EXIT=0` on D207's code; S50 proper changed no Python). 66 open = 11 + 55, 45 discharged | desktop | **Fable** | **Opus 5.5** | s50 | 2026-10-03 |
| ☑ | 51 | **The gas's own arm pattern** (D210; `RESEARCH_AREAS.md` §1 direction d, the owner's choice). *A reading session first* — three Opus readers, every number read on a fetched page (`docs/READING_GAS_PATTERN.md`): the gas's arm–interarm contrast is a ratio of means inside a mask (PHANGS: 2.73 for grand designs, 1.90 for the rest), the ridge half the stellar arm's width (0.17 of the arm-to-arm period, M51), no systematic offset for co-rotating arms. **`gas_pattern`** (checkpoint 3) publishes `gas_density_contrast`: a von Mises ridge in the stellar arm's own phase, on its crest, its amplitude derived from the ratio of means over the source's 1.5 kpc mask; `gas_arm_contrast` is the `bar` stage's, derived, no draw (amended and disclosed: the first default draw read 10.0 from a spread over segments, not galaxies). Crest 3.07, trough 0.53 at the defaults. **The render** places the dust and the HII regions' light by it: a thin dark lane along each arm's spine, seen face-on under rgb (`docs/design/screenshots/s51-*.jpg`); a ring's light at R₀ still falls, −0.85 % (predicted to rise: failed, pinned). **The model:** today's star formation and the cloud census on the ridge — the young stars' mean modulation 1.78 → 2.63; 16 822 clouds, 12 930 clusters (a redraw, the expectation identical); rows 35 and 37 read the census and moved (−1.989, −0.1055; statuses unchanged, 12 / 20 / 5). 69 open = 11 + 58, 45 discharged (#129–#131 new) | desktop | **Fable** | **Fable 5.1 lead; Opus 5.5 readers and builders** | s51 | 2026-10-03 |
| ☑ | 52 | **The dust heated in the geometry it is drawn in** (D211; debt #128's first half, on the owner's word given during S51: an Opus agent built it uncommitted, the lead reviewed the whole diff before committing). The dust stage's absorbed fraction is the layered geometry's — stars emitting from a sech² layer of the thin disc's height, the dust absorbing in the gas's own — as a fixed 96-node quadrature (`dust.layered_absorbed_fraction`, under 3e-11 against a second path, the slab's closed form at equal layers to 4e-14), and the render's scattered share with it; G₀ keeps the mixed slab (its sources sit in the gas). **Every prediction held:** L_IR 1.5675e10 → **1.2006e10 L☉** (0.766), the infrared share 0.3415 → **0.2616**, T_d(R₀) 18.82 → **18.52 K**, the inner disc 1.4 K cooler, the frame's balance to 1e-9, every stellar and radial field and the spec table identical. The placement round the ring is measured in the new geometry (1.0007 over the disc, 1.014 at R₀) and **not applied** — it would make every dust number seeded; #128 stays carried for that half. 69 open = 11 + 58, 45 discharged | desktop | **Fable** | **Fable 5.1 lead and review; an Opus 5.5 builder** | s52 | 2026-10-03 |
| ☑ | 53 | **BUILD_III adopted; its Phase 0** (D212; `BUILD_III.md`, the third build, on the owner's "adopt the plan"). The owner's ten rulings recorded; the rule amendments entered from the plan's Appendix A — A10's fourth kind of quantity, *synthetic*; A5's templates; D1's landing on the default template; D5 and `RENDER_PHYSICS.md` §8, which let the viewer evaluate a function the model publishes and nothing of its own; `RESEARCH_AREAS.md` and `VIEWER_TASKS.md` pointed at the plan. **Two instruments (B1), each by an Opus builder:** `tools/goal_metrics.py` — six statistics of a picture at one standard scale (radial colour, the azimuthal Fourier amplitudes m = 1–8, the blue arm–interarm contrast, the dark-lane fraction, the unsharp-masked power spectrum's slope, compact sources), each returning its known value on synthetic pictures; and **the picture test, T12** — `npm --prefix frontend run picture`, four captures of the default galaxy on headless Chromium through Playwright against committed frames (byte-identical run to run; a field gain of 1.05 fails all four). Pillow and Playwright are development-only. **The baseline table** (both goal pictures, the default galaxy at each goal's camera in both modes) is in D212: the render's odd Fourier amplitudes are 0.002 against the goals' 0.05–0.10, its dark-lane fraction 0.000–0.001 against NGC 4414's 0.157, its texture slope −3.3 (field) and −0.6 (points) against −2.0. No model code, number or row moved; 69 open = 11 + 58, 45 discharged | desktop | **Opus** | **Opus 5.5 lead; two Opus 5.5 builders** | s53 | 2026-10-03 |
| ☑ | 54 | **Phase T — the templates** (D213). A blind reading first (`READING_NGC_4414.md`: seventeen properties, a window each, fixed before any model output; the curve declines, there is no bar). `galaxy/templates.py`: `milky_way` states nothing and is the defaults bit for bit; `template=` on every route that takes inputs; `/api/templates`, metadata only. **The fit stopped the session once**: the objective as first ruled ran three unmeasured controls to their bounds and four of five blind checks missed; a conditional gate (BUILD_III §3d) went to Fable, who ruled that a control is free only if a target measures it, the refit's checks are *disclosed*, a bound is a finding, and no unspent window is spent. `ngc_4414` as refitted: peak 239 km/s, scale length 1.68 kpc, 3.9 × 10¹⁰ M☉, all inside their windows, the assembly epoch on its bound; **all five checks miss** (shape 0.653, star formation 0.65 M☉ yr⁻¹, hydrogen 4.8 × 10⁹, M_K −23.27, B − V 0.636), recorded with debts #132–#136, the first fit's blind reading kept beside them. **The viewer** lands on the default template, carries a switcher with captured thumbnails, a lens per template (NGC 4414 at 55° through 5°, `wfc3`), "Edit galaxy" from the template's inputs, and compare-with-a-picture; the picture test takes six captures by template. The 37 rows unmoved; 74 open = 11 + 63, 45 discharged | desktop | Opus | **Opus 5.5 lead; an Opus 5.5 reader and two builders; Fable 5.1 at a conditional gate** | s54 | 2026-10-04 |
| ☑ | 55 | **Phase R — the separation** (D214; gate G1). The fourth kind of quantity is in the code: `synthetic` provenance with what a field stands in for, what it conserves and its statistic; `texture_seed`, a fifth seed no stage reads until P1; `galaxy/layer/` — the noise primitives (a 32-bit integer hash a shader can match, unit-variance value noise, octaves to a stated slope, shear, a unit-mean log-normal map per cell, 632 committed vectors), `compose`, the one place that tests the switch, and the layer stage `cloud_texture` (Appendix B's four cloud columns, same streams, same values). `run(layer=)`, `layer=off` on every route that takes inputs, every cache keyed by it; the 37 rows and the template checks judged layer-off; the viewer's "physics only". **Behaviour-preserving, confirmed against the `s54` tag bit for bit** with the layer on. Layer-off the three composed fields are 1, `azimuthal` equals `basic` on every shared field, and only rows 35 and 37 move (−2.081, −0.1030; statuses unchanged). **The reviewer found the layer conserves expected totals, not realised ones**: a census draws each cell's count at a weighted expectation, so the switch re-draws which objects exist (cloud mass −1.9 %, the census's Hα −8.1 %; noise over seeds, not bias; fourteen census statistics move, five of them radial fields). **G1 (Fable): the design stands**; the invariants are restated on expected totals (BUILD_III §1 amended), `composed` becomes a declaration, the interior's three numbers are constants, and **the ring-first draw is ordered for L1** (#137). Rule A10's last sentence waits on the owner. 75 open = 11 + 64, 45 discharged | desktop | Opus; **Fable at G1** | **Opus 5.5 lead; three Opus 5.5 builders and a reviewer; Fable 5.1 at G1** | s55 | 2026-10-04 |
| ☑ | 56 | **Phase P1 — several arm modes at once; the gas follows any pattern** (D215). The owner's two answers first: rule A10 amended to expected ring totals until L1, the plan's order kept; `ngc_4414` keeps its fit. **Three gate turns.** A probe before the build contradicted the plan (no mode survives in the outer disc; the conserved-power sum goes negative in a sixth of galaxies): Fable ruled that the power follows the disc's gain, capped at one, and the modes saturate together — a law, no floor. The gas built as worded spiked (a crest of 11 at R₀) and did not fade: Fable ruled the ridge **by rank** along each ring, fading with the forcing amplitude — a one-session instrument (#140). **Then an independent reviewer found the window had been probed and built on X_m/2 — the lead's error**; Fable's third ruling: the law is the local swing window on the correct variable. Built: five radial mode amplitudes and a saturation field (the law), five synthetic phases on `texture_seed` (a new layer stage, its first reader), `arm_multiplicity` a derived label, a hand-derived test of the window. One mode returns S55's field to the byte; the Fourier gate holds to 4e-15; no cell negative on 240 seeds; layer-off every field is S55's but the label, and no row moved. **The Milky Way template is now four-to-six-armed outside the bar** (arm power m = 2…6: 0.08 / 0.21 / 0.24 / 0.25 / 0.22; the pattern whole to 11.1 kpc, gone at 12.3), which **fails the blind reading** (`READING_ARM_MODES.md`: two arms inside half the optical radius, A3/A2 0.33–0.58, never m = 5–6) — debt #138 to P3's close, and the owner asked: keep the law, or S26's global window. 78 open = 11 + 67, 45 discharged | desktop | Opus; Fable if the probe contradicts | **Opus 5.5 lead; an Opus 5.5 builder (three passes), a reader, a reviewer; Fable 5.1 at three gate turns** | s56 | 2026-10-04 |
| ☑ | 57 | **Phase P2 — the gas's steady response, ring by ring** (D216; gates G2 and G3). A reading by three blind readers (`READING_GAS_SHOCK.md`: the shock's equations from Shu, Milione & Roberts 1973 and three restatements, the checkable published cases, pattern speeds, and what simulations say of swing-amplified arms). **Gate G2 ruled the plan's mechanism away:** for arms whose power is set ring by ring the frame is Ω_p(R) = Ω(R), nothing flows through an arm, and **no arm shocks**; the gas's response is the steady corotating one under uniform potential vorticity, ε² d²ln s/dχ² = s − 1 − Σ_m f_m cos(mχ − θ_m), the zero-flow member of the shock's own equations, with f_m = m A_m/(X sin p) in the arm-number law's own X. **The instrument first** (`gas_response`): Sormani et al. 2017's no-shock threshold 0.72023 against 0.7202, the hand-derived linear limits, the ring mean 1 by the equation; the shocked branch deferred to P3's bar. **Built** (`gas_pattern`): the ranked ridge retired (#140 discharged, its cost repaid: the cloud census 3.67 → 1.17 s cold), the bar composed as a blend, `arm_pattern_speed` published as a statement of the frame, the ridge's two constants out of the registry. **The reviewer and gate G3:** the law and the solver right; the fixed tolerance sat inside the rounding of doubles on tightly wound galaxies (20 of 600 seeds raised) — a cell now converges at the larger of 1e-10 and its rounding floor, and nothing raises; the published field is the law's mean over each cell (ring totals exact on any grid, no division). **Read:** outside the bar the predictions held (R₀ crest 2.80, trough 0.017); **the disclosed check, not a row** (I3): ratio of means 2.57 against PHANGS's 2.73, a hit, `ngc_4414` 1.88; **the width misses** on every ring, 2.5–3.1× the measured 0.17; no offset put in. Layer off all 343 earlier fields bit-identical, 12 / 20 / 5 of 37 unmoved; layer on 16 667 clouds, 12 829 clusters. #81, #129, #131 re-ruled; #141–#144 opened (the steady state, the razor-thin forcing, the amplitude on the whole disc, the infall's shocks). 81 open = 11 + 70, 46 discharged | desktop | Opus; **Fable at G2, G3** | **Opus 5.5 lead (two sittings); three Opus 5.5 readers, two builders (one in three passes), a reviewer (two passes); Fable 5.1 at G2, G3 and five follow-ups** | s57 | 2026-10-04 |
| ◐ | 58 | **Phase P3.** The bar as a body (the old stars concentrated along its axis, no ring total moved), its absence derived from a sourced criterion (rows 15–17 not applicable to an unbarred galaxy), its gas lanes a synthetic template | desktop | Opus | — | s58 | — |
| ☐ | 59 | **Phase P4.** Pitch varying along an arm in seeded segments from the measured distributions; the templates' pins (the Milky Way's arm segments and bar angle, NGC 4414 unbarred and flocculent) | desktop | Opus | — | s59 | — |
| ☐ | 60 | **Phase L1.** `census_clustering`, a synthetic field of unit mean per level-0 cell, on the clouds' expected counts; clusters through their clouds; the 20–100 Myr bright stars near where they formed | desktop | Opus | — | s60 | — |
| ☐ | 61 | **Phase L2.** `gas_fluctuation` published as sourced parameters with a Python evaluator and committed vectors a GLSL twin must match; it modulates the diffuse dust only; spurs at the ridge's Jeans spacing | desktop | Opus | — | s61 | — |
| ☐ | 62 | **Phase V5.** `/api/render` returns the starlight by age (young, middle, old), each placed by its own weight and summing to `stars`; the field mode draws the three | desktop | Opus | — | s62 | — |
| ☐ | 63 | **Phase V6.** The censuses at whole-galaxy scale: clouds as extinction (the ring's dust mass unchanged), HII regions as knots, clusters with their half-mass radius (T6), bright stars by tiles (T28), the depth-aware composite (T5) | desktop | Opus | — | s63 | — |
| ☐ | 64 | **Phase V7.** The layer in the shader: the noise's GLSL twin against the vectors, the diffuse dust modulated per pixel, the spurs, the bar's body and lanes, the physics-only switch | desktop | Opus | — | s64 | — |
| ☐ | 65 | **Phase V8.** The display defaults per template (T1), the sprite scaled by the template's distance and pixel scale (T9), NGC 4414's instrument look, the goal captures and the metrics' final table against S53's baseline | desktop | Opus | — | s65 | — |
| ☐ | 66 | **Audit V.** Every citation since S51 read again, every synthetic field's conservation and statistic re-measured, I1–I5 re-derived, a picture traced feature by feature; Fable's verdict on the findings | desktop | Opus; **Fable at G4** | — | s66 | — |

**Surface** is where the session ran — desktop, web, terminal. **Model** is which
model ran it. They are different things and neither substitutes for the other.
*Model used* is filled at close from what actually ran, which may differ from
what was planned; the S10 comparison (below) is worthless if this is recorded
from intention rather than fact.

☐ not started · ◐ in progress or split · ☑ closed and verified

**Since S43 a session tags its own merge at close** (rule C2e as amended on the
owner's word, D193): `git tag -a`, `git push origin s<NN>`, `git ls-remote --tags
origin` read back, the row in `MANUAL_TODO.md` §1 written applied. **Until then tags
were deferred to a batch.** The web sessions ran behind an egress proxy that refused
tag refs — `git push origin s01` returned HTTP 403 while branch and `main` pushes
succeeded `[verified: DECISIONS.md D40]` — so no session tagged: each appended its
`git tag` command to `MANUAL_TODO.md`, and they were applied from the desktop in two
runs (2026-09-27, `s00`–`s39`, D192; 2026-09-30, `s40`–`s42`, D193). **The Tag column
names the tag on the remote**; `MANUAL_TODO.md` is where the truth about which tags
exist lives, and a test asserts it carries a row for every ☑ session.

**Next:** S58 (`BRIEF.md`): BUILD_III's Phase P3, the bar — a body, an absence, its lanes; the reading is done (`READING_BAR.md`),
and #138 is re-read at its close (D215, D216). The third build (§5f, `BUILD_III.md`, D212) runs S53–S66, every row led by Opus,
Fable at four gates and at a stop condition (S54 one turn, D213; G1 at S55, D214; S56 three turns, D215; G2 and G3 at S57, D216). **The model work the plan does not
name stays pinned**: the blind direct-method gradient (#117, #124), #119, #107 and #128's placement half wait for the word. Row 37 is diagnosed (S45, D196); Audit IV's fixes are applied (S44, D195). Both builds are closed — S0–S22 (§5d) and S25–S42 (§5e,
`BUILD_II.md`), every "done means" item met, the tags on the remote (D161, D192, D193). S23 and S24 were
recorded after the fact (D171): their work ran on `main` between 2026-09-13 and
2026-09-25 without a session branch or a close, and the rows say so.

> **S22 was ◐ from 2026-09-12 to 2026-09-30, and not for rule C2d's reason.** C2d's ◐ means
> a session ran out and its branch stays open for the next one to continue. S22 did not stop
> early: it finished every deliverable a session can finish, and merged. The ◐ was there
> because **one of its four deliverables could not be done from a session at all** — the tag
> batch needs a credential that can push a tag ref, and the egress proxy refuses one (D40,
> D161). It ticked to ☑ when the batch ran from the desktop on the owner's word (2026-09-27)
> and its listing was pasted under D161 (S42's close, D192). The board said so until then,
> which is the whole purpose of the column.

**Open debts:** 81 (`GALAXY_INPUTS.md` §11). **Discharged:** 46.

> S22 ruled all 43 that were open when it started: 17 discharged, **14 ruled permanent**
> and **12 carried**, none left unruled — and opened one of its own, #79, the acceptance
> row no model has ever been able to compute (§5d's "done means", checked rather than
> assumed). A permanent item stays
> counted open on purpose — it is a limitation of the model's scope or of the sources, and
> one that stopped being counted would stop being read. The three-way map is at the head of
> the register and a test asserts it.

> This board is the single source of truth for what is done. `RESUMING.md` does
> not repeat it (rule A9 — one opinion, in one place). The progress bar is
> **generated** from the checkboxes by `tools/progress.py`, and a test asserts
> they agree, because a hand-maintained bar drifts from the thing it summarises.

---

Companion to `GALAXY_INPUTS.md`, which holds the model. This holds the build.

Everything here is `[inferred]` design unless tagged otherwise. The working rules
this plan invokes are stated in `RULES.md`, inside this project — nothing here
reaches outside it for justification.

---

## 1. Three architectural commitments, made before any physics

Three things that a project with one model can discover late, and this project
cannot, because two models make each of them load-bearing rather than convenient.

**Field declaration at S0** (rule A8). Every published field carries a label,
unit, kind, ramp, meaningful-zero flag and an `about` line, declared in the stage
that computes it, with `preflight` asserting nothing is undeclared and no
declaration orphaned. **Two models publish different field sets** — advanced
chemistry publishes per-element abundances the simple model does not. Without a
declared contract, a downstream stage will read a field that exists in one model
and not the other, and the failure is silent rather than loud.

**The graph audit at S0.** `graph.py` computes the earliest field each input can
affect; that is what decides which checkpoint each control belongs to. Staged
previews with per-stage rerolls are a **requirement** here, not something
discovered midway, so the audit that grounds them is a prerequisite rather than a
by-product. The stage grouping in §3 is a **hypothesis to be checked against the
audit**, not a decree.

**A stub second model at S0.** The single largest risk in this build is that
eight sessions of simple-model work rot the two-model boundary, and the advanced
model turns out not to fit. Mitigation: S0 ships a second registered model that
differs *trivially* — one constant — purely so the registry, the field
reconciliation and the model switch are exercised from the first session onward.
Build the instrument before the thing it certifies (rule B1).

---

## 2. Layering

```
galaxy/
  core/          fielddoc, registry, seeds, grids, units
  models/        model declarations: which stage impl, which constants
  stages/        stage implementations (shared where identical)
  model/         executable specs: graph, determinism, convergence,
                 performance, preflight, spec
  api/           HTTP layer. JSON metadata + binary arrays. No rendering.
viewer/          static HTML/JS. Talks only to api/. Replaceable.
```

### The model boundary

A **model** is not a pipeline. It is a declaration:

```
Model = {
  name, inputs[], constants{},
  stages: {stage_name -> implementation_id},
  publishes: derived from the chosen implementations
}
```

Stages are shared wherever the implementation is identical — `halo`, `potential`
and `disc` are the same code in both models. Only where an advanced
implementation exists does the model choose. **A third model slots in by
declaring a stage map**, not by forking a pipeline.

The contract between stages is the **field set**, never the implementation.
Downstream code that wants `[Fe/H](R,t)` gets it identically whether the simple
or the multi-element chemistry produced it. Fields present in only one model are
declared optional and any reader must handle absence — `preflight` asserts this
per model, so a stage cannot quietly assume the richer model.

### The UI boundary

The viewer receives only: stage metadata, field metadata, and arrays. It never
receives model internals and it never computes physics. Replacing it means
reimplementing against the same endpoints.

**One fetch, asserted** (rules D2, D3, D4). Exactly one `fetch` in the client
transport with CI asserting the count; a `/api/version` content hash; and no
endpoint running more of the pipeline than its answer requires.

The failure this prevents is a metadata endpoint that quietly calls into the
pipeline — cheap warm, ruinous cold, and **invisible to every check ever run
against a warm cache** `[recall]`. So: **cold timings from the first API commit,
published every session** (rule B2).

---

## 3. Stages and previews

Six stages. The grouping is a hypothesis; `model_graph.py` rules.

| # | Stage | Inputs / seeds it owns | Preview |
|---|---|---|---|
| 1 | **Halo & disc** | `halo_mass`, `spin`, `halo_assembly_z`, `baryon_retention` | Rotation curve; face-on surface density (smooth, axisymmetric) |
| 2 | **Assembly** | `mergers[]` | Accretion history; edge-on view showing the thick disc appear |
| 3 | **Pattern** | `pattern_seed` | Bar and arms on the disc's own dynamics (ahead of star formation since S25, D174: the arms shape where stars form) |
| 4 | **Star formation & chemistry** | `infall_timescale`, `inside_out_index`, `migration_efficiency` | Age–metallicity relation, radial gradient, SFH; face-on coloured by [Fe/H]. **First recognisable galaxy** |
| 5 | **Systems** | `systems_seed` | Galaxy view — the star catalogue |
| 6 | **Planets** | `planets_seed` | System view |

Every stage renders the **same two views** — face-on and edge-on — plus a
stage-specific plot. Each preview shows only the fields that exist at that point,
so the galaxy visibly assembles: smooth disc, then thickened, then chemically
structured, then armed, then resolved into stars. That progression is honest
rather than decorative; it is what the model actually knows at each step.

### Locking

Confirming a stage locks its prefix, under rule D1: a lock means *do not re-roll
this* and never *freeze this against upstream changes*. Confirmed controls are
disabled rather than hidden, reopening a stage discards every later one, and a
page load lands on stage one.

**Reroll is a distinct action from edit.** Rerolling stage 3's `pattern_seed`
invalidates 4–6 but not 1–2 (until S25 the pattern was stage 4 and rerolling it
spared star formation; since D174 star formation follows the pattern). This is the
whole point of per-stage seeds and it falls out of the graph audit rather than
being hand-wired.

---

## 4. The two views

### Galaxy view

10⁶ stars will not render as 10⁶ DOM nodes or draw calls. The rendering strategy
**mirrors the model's own field/object split**:

- **The field renders as an image.** Stellar density, integrated and coloured by
  the populations stage, drawn as a texture. This is what you see at galaxy zoom.
- **A materialised sample renders as points.** A seeded subset — order 10⁴–10⁵ —
  drawn as clickable objects, stable across sessions because it comes from
  `hash(systems_seed, star_id)`.
- **Zooming materialises more.** Below some angular scale the field is replaced
  by actual stars within the view volume, generated on demand and never stored.

The consequence to state plainly: **at full galaxy zoom you are looking at a
field, not at stars.** Clicking requires the materialised sample. Building the
sample first and the LOD ladder later is the right order.

### System view

Star, planets, belts, moons. Small N, trivial to render. Selecting a star in
galaxy view transitions here; the system is generated from
`hash(planets_seed, star_id)` at that moment and discarded on exit.

### What the viewer must not do

No physics, no persistence of generated objects, no second opinion about how a
field is rendered (rules D5, A9). **Ramps come from the field declaration, in the
stage that computes the field, and from nowhere else.** The failure mode is a
client-side colour table that silently wins over the authoritative one and
renders a field as something it is not `[recall]`.

---

## 5. Session protocol

Every session is a fresh context. The repo lives at
`https://github.com/mcha291/galaxygen.git` and every session clones it fresh
(rule C1). **Verified reachable from the sandbox** `[verified: clone succeeded,
this session]`; **push requires a token** `[verified: unauthenticated push
rejected, this session]`.

This replaces file-passing entirely, which matters most for the cross-account
Fable sessions — they clone the same URL and nothing has to be carried.

### Fixed opening and closing

**Open:** clone the remote into a fresh directory → read `RESUMING.md` (capped,
see below) → read `BRIEF.md` → start on branch `session-NN`. Nothing else is read
by default.

**Mid-session:** commit and push at every completed sub-deliverable (rule C2b).
The binding constraint is usage quota, and a session halted by it loses
everything after its last push. See **Partial close** below.

**Close, in order:**
0. **Tick this session's box in the status board** at the top of
   `GALAXY_PLAN.md`. Fill in **surface, model actually used**, tag and close
   date; set the next session's row to ◐ if it has already begun. Record the
   model from what ran, not from what the plan said. Then run
   `python tools/progress.py`, which regenerates every derived number. A session that closes
   without doing this leaves the board lying, and the board is what you look at
   to know where the build is.
1. Full suite once, quiet mode.
2. Append to `DECISIONS.md` and any new rule to `LESSONS.md`, **tagged** by stage
   type so future sessions read only what applies to them.
3. Rewrite `RESUMING.md` in place — it does not grow.
4. Write `BRIEF.md` for the next session: what to build, which files to touch,
   the gate, and known traps. This is the single highest-leverage artefact in the
   whole protocol; it is what lets the next session skip reading the plan.
5. Commit, `--no-ff` merge to `main` with the subject `Merge S<N> into main: …`,
   push branch and main. **Then tag the merge** (rule C2e since D193): `git tag -a
   s<NN> <merge sha> -m "S<N>: …"`, `git push origin s<NN>`, read `git ls-remote
   --tags origin` back, and write this session's row in `MANUAL_TODO.md` §1 as
   applied with the SHA. (Until D193 the step was "do not tag; queue the command".)
   **Never force-push** (rule C2a).
6. **Verify by cloning the remote into a clean directory and running the suite
   there** (rule C2) — not by re-running in the working copy, which cannot detect
   a file that was never `git add`ed.

### Token discipline — the rules that actually move the number

The dominant recurring cost in a multi-session build is **re-reading state at
session start**, and it grows with the project unless capped. An uncapped
resuming document reaches a few hundred lines by the end of a build of this size,
and every session pays it — eleven times over. `[inferred]`

| Rule | Why |
|---|---|
| **`RESUMING.md` hard cap: 120 lines.** Enforced by a test | Otherwise it grows monotonically and every session pays |
| **`BRIEF.md` replaces reading this plan.** Written by the previous session, ~40 lines | The plan is read once, at S0 |
| **Lessons are tagged by stage type**; a session reads only its tags | 27 untagged lessons is a per-session tax on all of them |
| **The acceptance table lives in `spec.py`, never in prose read at runtime** | A session runs the spec and reads pass/fail, not 24 rows |
| **Tests run quiet; only failures print.** Affected subset mid-session, full suite once at close | A suite printing 339 passing test names is pure waste |
| **Never read a file you are about to overwrite** | Common and invisible |
| **Bundle verification is a fixed script, not an exploration** | It is the same six commands every time |

### Subagent delegation — delegate reading, not deciding

The test is the **ratio of output to input**. Delegate when a task consumes a lot
of context and returns little; keep when the output feeds further design in the
same session.

**Delegate:**
- Literature verification of acceptance values — searches are read-heavy, the
  return is a number and a citation
- Auditing a large existing spec for a short answer — one agent reads it, returns
  a list
- Writing test suites against a settled contract
- Independent stage implementations that do not interact

**Do not delegate:**
- Any ruling, or any design whose output feeds more design this session
- Anything where the subagent's return is large — it gets read back anyway
- The audit sessions. Finding a defect nobody saw requires the whole context

### Credentials

Push needs a fine-grained personal access token, and it must be supplied each
session because containers do not persist. Scope it as tightly as the work
allows: **this repository only, `Contents: read and write`, short expiry.**
Nothing else is needed — no org scope, no workflow scope.

Two shapes, pick one:

- **Push to `main` directly.** Lower friction. Safe because sessions are
  sequential and rule C2a forbids force-pushing, so a rejected push is a signal
  rather than an obstacle to overcome.
- **Push the session branch only; merge by PR.** One click per session, and the
  blast radius of any mistake is one branch. Recommended if the token's lifetime
  is long.

Rule C2c covers the rest: the token stays out of the working tree, and a
pre-commit hook refuses staged content matching `ghp_` or `github_pat_`.

### Subagents and the remote

Subagents share the main agent's checkout and **do not push**. Delegated work
returns to the session, which commits it. *Justification: a subagent pushing
independently would need its own credentials and could interleave commits in an
order nobody chose* `[inferred]`.

### Which sessions to run on Fable

**Fable draws on a separate limit**, so its marginal cost against the rest of the
build is near zero and unused quota is simply wasted. That removes the trade-off
this section originally agonised over: the question is not whether the capability
gap justifies the cost, but which sessions are longest and hardest.

Anthropic's guidance is a **procedure rather than a claim** — start on Opus 5 and
move to Fable when evals at higher effort still fall short `[recall: Claude
Platform docs, "Choosing the right model"]`. The stated strengths are long
autonomous sessions, investigating before acting, and verifying work more often
`[recall: Claude Code docs, model configuration]`.

**S10 — audit. The strongest case, and it is structural rather than a hunch.**
S1–S8 all have gates: acceptance checks pass or they do not, so a weaker model
fails *visibly*. S10's output is "here are the defects I found", and that cannot
be checked for false negatives. **Capability matters most exactly where
verification is weakest.**

**Run S10 twice, once on each model, and diff the defect lists.** It is the one
session whose output is directly comparable, it converts an impression into a
measurement, and an audit run twice is not wasted work even when the two agree.
Record the comparison in `DECISIONS.md` — it is the only controlled evidence this
project will produce about whether the model choice mattered.

**S9 — advanced model. Second.** Long-horizon, and it contains a specific trap
(the complexity-class change in the DTD) that must be verified rather than
assumed.

**S0 — ran on Fable, and the result is evidence but not a comparison.** S0 found
a real arithmetic error in this very board — the debt line claimed 9 open and 2
discharged against a register of 9 items of which 2 were struck `[verified:
DECISIONS.md D15]` — and turned the fix into a generated number that cannot drift
again. That is a data point. It is **not** a controlled result: there is no
counterfactual S0, and the session was also unusually well specified. Do not
treat it as settling the question that S10's double run is designed to answer.

**After S14 — what the double run said, and the rule it leaves.** S10 ran six
times on four lists and the model did not visibly matter; the stated aim did
`[verified: DECISIONS.md D102]`. What did separate the sessions since is the
kind of work: the sessions that overturned a register assumption by probing
first (D110, D113, D114) and the one that caught a solver defect by probing a
third ruleset (D113) were judgement sessions, where a wrong answer passes
every gate. So the rule for what remains (§5d): **Fable where verification is
weakest** — a decision about what the model derives, a mechanism that could be
tuned into passing, an audit — and **Opus where the contract is decided and the
gate is in `spec.py`**, which is how S1–S8 were built and passed.

---

## 5b. Sessions

Eleven. **All physics is headless through S5** — the viewer arrives at S7 with
everything to show at once, so the rendering harness is written once instead of
five times.

That ordering is not only cheaper, it is what rule B1 requires. It has already
paid once in this project: the benchmark written to measure the advanced model's
cost found a defect in a proposal made a turn earlier, and no picture would have
shown it `[verified: bench2.py §1]`. **Instruments before pictures.**

| S | Deliverable | Gate | Notes |
|---|---|---|---|
| **0** | Repo init, `tools/progress.py`. `core/` + registry, fielddoc, seeds, grids. `graph`, `preflight`, `determinism`. `spec.py` as **data**. **Stub second model.** No physics | Graph acyclic per model; both models preflight; determinism holds; `spec.py` lists 24 quantities and reports each not-yet-computable | **Fable.** `convergence`/`performance` deferred to S10 — they need something to measure (rule B1) |
| **1** | Halo & disc (shared impl) | λ_d = 0.0144 from a **joint** fit to stellar mass and scale length; R₂₀₀ arithmetic | Delegate: verify M₂₀₀, R_vir values |
| **2** | SFH + chemistry, simple | Gradient ≈ −0.06 dex/kpc; SFR ≈ 1.65 M☉/yr | |
| **3** | Assembly + `mergers[]` with `gas_fraction` | f_Σ = 12% ± 4%; **debt #9: run a merger-free galaxy, check whether α-bimodality appears anyway** | |
| **4** | Pattern: bar, arms | `PITCH_YU` seeded; S-spread recorded once | |
| **5** | Systems: catalogue, headless | 10⁶ stars < 10 s; per-region determinism | |
| **6** | API. Headless and fully tested | **One `fetch`**; `/api/version` hash; **cold timings published** | Testable without a browser — separated from S7 deliberately (rules D2–D4) |
| **7** | Viewer: galaxy view, checkpoints, previews for stages 1–5 | Field-as-image + clickable seeded sample; reopening a stage discards later ones | Largest quota risk — visual work iterates blind |
| **8** | Planets stage + system view | Occurrence vs [Fe/H]; belts derived from resonances; **planet scalar set declared and closed** | No external dependency — see §5c |
| **9** | Advanced: multi-element + DTD, migration, outflows, coupling | **Exponent 1.0 in N_t**, not 2.0 (`bench2.py`); coupling multiplier measured | **Fable** |
| **10** | Audit: `convergence`, `performance`, calibration debt | N_R and N_t swept **independently** | **Fable, run twice** — diff the defect lists |

### On splitting

**The binding constraint is usage quota, not wall clock.** A session can run as
long as it likes; what it cannot do is exceed its allowance and stop mid-way.
That makes the split criterion a **token-volume judgement**, which belongs with
the token discipline above rather than being read off the session table.

The signal to watch is not elapsed time but **iteration depth** — how many
test-fix cycles a session has burned. A session that cleared its gate on the
first or second attempt is nowhere near the limit; one grinding through a
rendering loop or a failing acceptance check is consuming quota fast and has
little to show per token. S7 is the likeliest, because visual work cannot be
tested headlessly and so iterates blind.

Splitting costs one session-open — a clone plus two capped documents, small under
the discipline above. It **saves** an entire iteration loop being carried in a
context that is already long.

So: split freely, with one exception. **S9 must not split.** Its two halves touch
the same stages, and splitting means reading the chemistry implementation into
context twice — the one case where the handoff costs more than it saves.

### Partial close — what a session does when it senses the limit

The close ritual assumes a session finishes. **A session that stops because it
ran out of allowance must not leave the next one to reconstruct where it got to**
— reconstruction is exactly the expensive thing this protocol exists to avoid.

So, from the start rather than as a panic measure (rule C2d):

1. **Commit at every completed sub-deliverable**, not only at close, and push the
   branch each time. A stranded session loses only what came after its last push.
2. **Keep `BRIEF.md` written-ahead.** At the point a session's plan is clear,
   write the next brief *as if stopping now*, and refine it at close. A brief
   that already exists costs nothing to update and everything to write from
   scratch after the fact.
3. **On sensing the limit, stop and close partially**: commit, push, append what
   was done and what remains to `BRIEF.md`, set this session's board row to ◐
   with a note. Do not start new work in the hope of finishing it.
4. A partial close does **not** merge to `main`. The branch stays open and the
   next session continues on it. A partial close does not tag either (rule C2e:
   the tag marks a merge, and there is none).

---

## 5a. What each session reads

**All three documents are committed in S0's first commit.** After that they are
in the repo and can be consulted by section rather than read whole.

| | S0 | S1–S10 |
|---|---|---|
| `RULES.md` | **In full** | **In full** — it is capped and every rule applies |
| `GALAXY_PLAN.md` | **In full** | Not read. `BRIEF.md` replaces it (rule C4) |
| `GALAXY_INPUTS.md` | §7 and §11 only | By section, when a `BRIEF` names one |
| `RESUMING.md` | Written, not read | **In full** — capped at 120 lines (rule C3) |
| `BRIEF.md` | — | **In full** — ~40 lines |

`GALAXY_INPUTS.md` is a **source document, not a session-time read.** S0's job
includes consuming the durable parts of it into code, after which they are never
read as prose again:

- **§7's 24 acceptance quantities → `spec.py` as data**, with a runner that
  reports each as pass, fail, or not-yet-computable. From S1 onward a session
  runs the spec and reads pass/fail (rule C6).
- **§11's input table → the registry.** Names, defaults, units, ranges.
- **§4b's three categories → already lifted to rule A10.**

What stays in `GALAXY_INPUTS.md` is reasoning — why a quantity is derived rather
than input, which conflicts are preserved, what each debt is. A session consults
those when its brief says to, not by default.

### The three gaps S0 must close itself

None of these is settled in any document, and the registry cannot be written
without them:

1. **The closed unit vocabulary** for field declarations — kpc, Gyr, M☉, dex,
   km/s, M☉/yr, dimensionless, and whatever else the six stages need. Closed
   means a field cannot invent one.
2. **The `kind` vocabulary** — continuous scalar field, category, per-object
   scalar, catalogue column.
3. **Grid defaults.** `N_R = 400` radial annuli, `N_t = 2000` timesteps, `N_z`
   ≈ 60 for the (R, z) potential grid. N_R is measured nearly free up to 400 —
   exponent 0.13 in N_R against 1.0+ in N_t `[verified: bench2.py §3]` — so the
   two are separate quality knobs, never one (rule A6, and `convergence.py` at
   S10).

---

## 5c. The planets handoff has no external dependency

An earlier draft made S8 block on enumerating another project's input list. **That
dependency is removed.**

The planets stage publishes a **self-defined, closed set of planet scalars** —
mass, insolation, volatile inventory, rotation, obliquity, atmosphere class —
declared under rule A8 like every other field, chosen for what the formation
model actually determines rather than for what some consumer currently accepts.
`preflight` asserts the set is closed and documented. That is the whole gate.

This is better design independently of scope. A stage shaped by a downstream
consumer's current input list inherits that consumer's arbitrary choices; a stage
that publishes what it knows lets integration adapt to it. Any future consumer
writes an adapter.

**Recorded as a note, not a blocker:** if this project is later joined to a
surface-scale world generator, the two scalar sets must be reconciled, and
whichever side is authoritative for a given quantity must be declared once. That
reconciliation is an integration task with its own session, not a prerequisite
for S8.

---

## 5d. Completing the project — S15 to S22 (written after S14, at the owner's request)

The build (S0–S10) closed on schedule; S11–S14 then diverged from §5b into
integration, fixes and physics decisions, each session taking whatever the last
one's `BRIEF.md` put first. That was the right order for the work but it is not
a plan, and a plan is what tells a maintainer when the project is *done*.

**Done means** `[inferred]`: every acceptance row either passes or is a recorded
miss whose cause is a *mechanism the model lacks*, not a constant it could tune
(rule B5); every item in the register is discharged, or ruled permanent with the
reason written in — a property of the model's scope, like the simple model's
one-abundance chemistry (#15), or of the sources, like the zero-width targets
(#17); the viewer shows every published field; the tag batch in `MANUAL_TODO.md`
has been applied from a desktop; and `verify_clone` is OK on `main`.

Eight sessions. Each opens per RESUMING.md, works on `session-NN`, and closes by
§5's ritual, tags queued (C2e). Gates are read from `python -m galaxy.specs`,
never from prose. **Probe before build** in every physics session: S13 and S14
each found, with a fifty-line probe, that the register's stated lever had the
wrong sign or the wrong magnitude (D110, D113).

| S | Deliverable | Gate | Model, and why |
|---|---|---|---|
| **15** | **Row 3's cause, derived** (#12, #46, #11). Three levers, none free: the assembly epoch (0.7–1.0 closes the row alone; the cited range is 2–3), the contraction's calibration (a mass- and epoch-dependent (A, w) is the untried form; A = 1.6 alone reads 256.8), and a less compact baryon distribution (the bulge is worth 5–8 the right way, D110). Decide which the model *derives*; sweep nothing to the answer | Row 3 inside 245–251 with its cause a derived quantity, or a miss whose prediction names a mechanism; row 19 unmoved; v_esc(R₀) inside 530–580 as the second discriminant | **Fable.** A row can be closed by tuning and no gate would see it — verification is weakest exactly here |
| **16** | **The extended component with its own timescale** (#18, #43, #45). D114 showed a share at k R_d on the disc's timescale buys row 20 with row 2; the component must arrive late or diffuse enough to stay under the threshold. Derive the timescale (the halo's angular momentum arriving late is the physical candidate), then build it in `sfh` behind `infall_profile` | Rows 2 and 20 inside with rows 4 and 22 unmoved; row 3 read with it; `NET_YIELD` and `WIND_SPEED` refitted and recorded (rule B10) | **Fable.** The timescale is a derivation decision (D114), and #45 says a wider first component is the wrong answer that passes |
| **17** | **The bulge stage and M_•** (#11, #2, #17, ruling 10). Hernquist spheroid drawn from the disc in proportion, as D110 probed; rows 10–14; M_• as derived mean plus seeded residual, row 18 statistical; row 14 needs the source's uncertainty entered first (#17) | Rows 10, 12, 13 inside; row 11 no longer passing on the cancellation; rows 14 and 18 statistical per their debts; row 3 moves −5 to −8 and is re-read | **Opus.** The contract is decided (D110, §13) and every row is in `spec.py` — a gated build, as S1–S8 were |
| **18** | **The thick disc** (#19). Radial heating with the vertical kick is the prediction: a merger that thickens the disc also spreads it, so rows 5 and 11 can be right together and row 9 comes off the cancellation | Rows 5, 7, 9 and 11 inside together in the simple model, row 9 not on a cancellation (a sweep of the merger's `gas_fraction` leaves it inside) | **Fable.** A cancellation can be tuned into passing; the gate is the sweep, and judging it is the session |
| **19** | **The catalogue migrates, and the viewer shows the new fields** (#31, #32). Birth radius drawn around the present one with the migration kernel's width, the abundance looked up there, both models (D110); new golden values; previews for `halo_contraction` and whatever S15–S18 published | The catalogue's [Fe/H] spread at R₀ equals the chemistry's `feh_spread_sun`; determinism and per-region checks OK on the new golden values; every published field has a preview | **Opus.** A specified change in `systems.materialise` with its own golden values; the viewer work is the S7 kind |
| **20** | **The advanced model's [α/Fe] valley** (#27, #42, #26). The mechanism that makes the inner disc fast without steepening the infall law everywhere — the bulge's inflow is the named candidate — then rows 5–11 and 24 in the advanced model, and rows 6 and 7 judged together with both heating constants re-examined | Row 24 `bimodal_wide` at the default grid, stated (the N_t = 8 trap); row 22 still inside; rows 6 and 7 inside together | **Fable.** The hardest open physics, and the one with a known false positive (a coarse grid manufactures the valley) |
| **21** | **Audit II, run twice with two stated aims** (D102's lesson). Aim (a): every prediction the register and `spec._MISSES` made since S13, killed or held with a number (rule B4). Aim (b): the instruments and the viewer — cold paths (D4), the flaky per-star slope (D115), the audit tests' pins. **Reserved numbers**, fixed when S21 opens (decisions are numbered sequentially and S15–S20 each append theirs): fourteen debts and fourteen decisions for (a) starting at the next free numbers, the following fourteen of each for (b), so the lists port without renumbering (D99). Written at D116 as #47–#60 / D117–D130 and #61–#75 / D131–D145, before S15 took D117 | Two lists, diffed; every prediction has a verdict; no green row unconditioned (AUDIT_RUN2 §5) | **One on Fable, one on Opus**, aims different by design — extends the only controlled evidence the project has (D102) |
| **22** | **Close-out.** Port both audit lists onto `main` (never merge the branches, D99); rule every open debt discharged, permanent or carried, with the reason; apply the tag batch from a desktop and delete the stale `s01` (MANUAL_TODO); final RESUMING/BRIEF for whoever maintains it | Tags on the remote, `git ls-remote --tags` listed in DECISIONS; register with no unruled item; `verify_clone` OK | **Opus.** Procedure with a checklist; the judgement was spent in S21 |

**What this does not promise.** Rows whose cause is the model's scope stay
misses by design: the simple model's gradients (#15) are a third of the observed
because it has one abundance and no wind, and that is what the advanced model is
for. Debts #3, #5, #10, #21–#23, #25, #33, #34, #36, #39 and #44 are the kind S22
rules on rather than closes — each is a measured limitation with its number
already in the register, and a session spent closing one would be a session
inventing a variable (rule A4). The order above is by dependency, not by
importance: S15 before S16 because the component is judged against row 3, S17
before S20 because the valley's candidate mechanism is the bulge's inflow, S19
last of the builds because it re-pins every seeded number the earlier sessions
move.

## 5e. The second build — S25 to S42 (written 2026-09-26, at the owner's request; S42 added at its close, D192)

Two documents the owner wrote, reconciled against the repository and adopted
(D172): **`BUILD_II.md`**, twelve phases that make the arms form stars, publish
what light needs, and build the model side of the render contract; and
**`RENDER_PHYSICS.md`**, the model/renderer contract itself. The board rows
above carry the deliverables; `BUILD_II.md` carries the phase text, the gates,
the sourcing owed and the sequence, and it is what a session reads with
`BRIEF.md` in place of this plan.

**What changed since §5d's "done".** The build closed at S22 with one model
kept for contrast and no light. S23–S24 then built RENDER_PLAN's model side on
`main` without sessions — photometry, the ISM, the unresolved light, three
rendering regimes — and collapsed the two models into `basic` (D170). The second
build is the physics that work exposed as missing: an arm that makes stars, an
ionizing budget, clouds, lines, winds, and a renderer that draws only what is
published.

**The protocol, adapted** (`BUILD_II.md`, "How the rows run"):

- One board row is one phase on one `session-NN` branch, merged `--no-ff` and
  closed by §5's ritual. **Numbers are sequential** — debts from #80, decisions
  from D173 — with no reserved blocks, because the rows are sequential.
- The rows marked **Fable** are the orchestrating session's own: rulings,
  derivations, interface contracts, the audit (§5's rule: Fable where
  verification is weakest). The rows marked **Opus** are delegated to an Opus
  subagent in a worktree on the session branch with the phase text and the
  gate; it neither pushes nor writes `DECISIONS.md`, and the orchestrator
  reviews, runs the suite, writes the decision and closes. Two independent
  Opus rows may run at once; merges stay one at a time, in row order.
- **Probe before build**, as §5d required; **read the citation before trusting
  the row it lands** (S21 (a), A-14).

**Sequence.** 25 → 26 → 27 is the one hard chain on the model side; 28 is the
highest value and the prerequisite for 29, 35 and 36; 31 → 32 → {33, 35, 36}
is the chain the rendering depends on; 34 follows 33 so the globular-cluster
relation lands as a check; 37 audits; 38–41 build the renderer against the
contract, each row removing one structure the present viewer invents
(`RENDER_PHYSICS.md` §0).

**Done means**, for this build `[inferred]`: `azimuthal` and `basic` both pass
preflight and read the same acceptance table at the defaults; every new row
passes or is a recorded miss whose cause is a mechanism (B5); every constant
that entered from a NEEDS-SOURCING has its citation read; the energy-balance,
redistribution and catalogue-against-field tests are in the suite; every
visible feature of the viewer traces to a published field; and the tag batch
has been run from a desktop, which is the one item §5d could not close.

## 5f. The third build — S53 to S66 (written 2026-10-03, at the owner's request; D212)

**`BUILD_III.md`** is the plan, adopted by the owner on 2026-10-03 with ten rulings (its §7, recorded in D212): two
templates (the Milky Way and NGC 4414), **the physics model beside a randomness layer** — a fourth kind of quantity,
*synthetic*, on its own seed, conserving every total, citing its statistic, naming the physics it stands in for —
the ten model items and the gas shock ring by ring, and the viewer's rendering brought up to them. The board rows
above carry the deliverables; `BUILD_III.md` carries each phase's ruling, its reading and its gate, and it is what a
session reads with `BRIEF.md` in place of this plan.

- **Every row is led by Opus; Fable is called at four gates** — G1 (S55: do the invariants mean what they say), G2
  and G3 (S57: the shock's equations, then the solver's review), G4 (S66: the audit's verdict) — each one short turn
  on a `docs/HANDOFF_S<NN>.md` of at most 150 lines (`BUILD_III.md` §3). An Opus lead that meets a stop condition
  (§3d) closes partially and writes a handoff; it does not improvise a ruling on physics.
- **The model's phases run first, the viewer's after** (the owner's ruling 9): S54–S61, then S62–S65, then the audit.
- **The goal pictures are display targets, never rows** (C6, D113), and are not in the repository (ruling 5): the
  baseline of `tools/goal_metrics.py`'s numbers is in D212 and the final table is S65's.
- **`basic` is frozen** (ruling 7): registered, not merged, used once at S55 as the layer-off oracle.

**Done means**, for this build `[inferred]`: with the layer off the acceptance table is S52's row for row unless a
phase's decision says which mechanism moved a row; no row reads a synthetic field; every synthetic field has its
three declarations and its conservation test; the viewer evaluates only what the model publishes and matches the
committed vectors; both templates load, and NGC 4414's five checks are read and recorded, pass or miss; and the goal
metrics' final table is set beside this session's baseline and beside the plan's own "what will remain".

## 6. What the executable specs assert

| Spec | Addition |
|---|---|
| `graph.py` | Acyclic **per model**, and the stage→checkpoint map is derived from it |
| `preflight.py` | Field declarations reconcile **across models**; optional fields have handled absence |
| `determinism.py` | Per-region determinism: `hash(seed, star_id)` is order-independent |
| `convergence.py` | **N_R and N_t swept separately.** They are not one quality knob — measured exponent 0.13 in N_R against 1.0+ in N_t `[verified: bench2.py §3]` |
| `performance.py` | Asserts the DTD stays linear in N_t. This is the one place the advanced model can change complexity class |
| `spec.py` | The 24 acceptance quantities, with entries 13/14/16/17 **statistical rather than pointwise** (`GALAXY_INPUTS.md` §4b) |

---

## 7. Risks, ranked

1. ~~The λ circularity.~~ **Discharged by ruling 8.** Replaced as top risk by:
   **the λ_d prior.** Default and prior must be drawn from the same population —
   seeding rolls from a halo-λ log-normal would make every generated galaxy three
   times too extended, and the error would look like a plausible galaxy.
2. **The advanced model is unfalsifiable in the generator.** Its headline outputs
   can only be checked against our galaxy, not a random one
   (`GALAXY_INPUTS.md` §10). S8–S9 must ship with that stated, or they will look
   like progress they are not.
3. **Two-model boundary rot.** Mitigated by the S0 stub, and only by it.
4. **Browser rendering at 10⁶.** Mitigated by field-as-image; the LOD ladder is
   the part most likely to slip.
5. **Warm-cache self-deception.** This class of defect can survive every check
   ever run against it, because the checks run warm `[recall]`. Cold timings from
   S6, published, every session (rule B2).
6. **Acceptance table internal inconsistency.** The 24 quantities are not
   mutually consistent (`GALAXY_INPUTS.md` §7); a model fitting all of them
   exactly is fitting a contradiction.

---

## 8. Rulings needed before S0

**All settled.** The input vector is closed and S0 can declare it.

### The seven

| # | Input | MW default |
|---|---|---|
| 1 | `halo_mass` M₂₀₀ | 1.1 × 10¹² M☉ |
| 2 | `disc_spin` λ_d | 0.0144 |
| 3 | `halo_assembly_z` | z ≈ 2–3 |
| 4 | `baryon_retention` | ~0.35 |
| 5 | `infall_timescale` τ₀ | ~7 Gyr at R₀ |
| 6 | `inside_out_index` n | — |
| 7 | `migration_efficiency` | — |

Plus `world_seed`, `systems_seed`, `planets_seed`, `pattern_seed`, and
`mergers[]` — the last now carrying `gas_fraction` per ruling 11. **Ceiling 12;
five slots of headroom.**

### Rulings that changed the build

- **8** discharged debts #1 and #7. S1's gate is no longer "resolve the λ
  circularity" but "reproduce λ_d = 0.0144 from a joint fit to stellar mass and
  scale length."
- **11** cut an input and made the model falsifiable. **S4 gains a gate**: run a
  merger-free galaxy and check whether α-bimodality appears anyway (debt #9).
- **10** added a sixth seeded residual and no machinery.
