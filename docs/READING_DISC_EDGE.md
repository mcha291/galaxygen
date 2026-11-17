# READING_DISC_EDGE — do real discs end as sharply as the model's? Truncations, breaks and the Milky Way's edge (S103, D273; S104's measurement, D274; register #226, #237)

**What this file is (2026-11-17, S103, BUILD_VII row 105, the reading row).** S102 named and declared the model's
edge where it is computed: the disc ends where the infall's high-angular-momentum tail ends (`milky_way` 0 from 24.19
kpc, `ngc_4414` from 18.64 kpc), and the star-formation threshold's switch turns the gas's 26-fold fall into the
stars' 3 500-fold (register #226's S102 paragraphs; `tests/test_disc_edge.py`). What was left is the reading: whether
real discs end within 0.3 kpc. S103's reader RB (an Opus agent, read-only; its note `s103_RB.md` in the session's
scratchpad, section B) read it, and a second reader RT (note `s104_RT.md`, section A) read the code at the edge and
star formation below the threshold. The gate's ruling is item 3 of `DECISIONS.md` D273 as corrected by its item 8.

**Tags.** READ — the page fetched at S103 (a summarising fetch; sentences and rows asked for verbatim and quoted as
returned), the place named; RECALL — memory; NOT READ — named and not reached; `[inferred]` — the reader's own
arithmetic. Nothing here moved a constant, a pin or a model byte.

---

## Part S103 — the reading (reader RB)

### S103.1 The model's edge `[inferred: the reader's arithmetic on the register's numbers]`

`milky_way`'s light falls 340-fold between 23.66 and 24.04 kpc on the render's arrays (3 500-fold in the stars'
surface density within 0.3 kpc, S102); the stellar-mass scale length is 2.440 kpc (`milky_way`) and 1.675 kpc
(`ngc_4414`). So the edge is at 23.7 / 2.44 = **9.7 scale lengths** (`milky_way`) and ~18 / 1.675 = **10.7**
(`ngc_4414`), and a 3 500x fall in 0.3 kpc is an e-folding length of 0.3 / ln 3500 = **37 pc**.

### S103.2 What was read

- **Pohlen & Trujillo 2006**, astro-ph/0603682 — READ (ar5iv, 0-200k). Table 4 / Sect. 5.1: Type I 11 ± 3 %, Type II
  66 ± 5 %, Type III 32 ± 5 %. Type II-CT: "the break happens already at 2.5±0.6 times the inner scalelength"
  (1.4-4.2), μ_br = 23.5 ± 0.8 r'; "hin/hout = 2.1±0.5", range 1.3-3.6. Type II-OLR: 1.7 h_in (1.4-2.4). Type III:
  "4.9±0.6 times the inner scalelength" (3.7-5.8). Type I (Sect. 5.2): "we do not find a break down to 6-8 times the
  measured scalelength", traced to ~27.0 r'-mag/arcsec² (Sect. 3.3). Sect. 5: "none of the Type III profiles show an
  additional outer truncation within our sensitivity limit". Sharpness: no quantitative measure; III-d "a rather sharp
  transition" (Sect. 4.1).
- **van der Kruit 2008 review**, arXiv:0712.0447 — READ (ar5iv). Sect. 1, quoting van der Kruit & Searle 1981: "This
  cut-off is very sharp with an e-folding of less than about 1 kpc." Observed R_max/h "ranging between about 2 and 5"
  (Sect. 2); a model prediction "a truncation at about 4.5 scalelengths". Face-on: "Unless special care is taken we
  will always find a (much) less sharp truncation in face-on than in edge-on systems." van der Kruit & Searle
  1981/1982 and van der Kruit 2007 (astro-ph/0702486) themselves: NOT READ.
- **Martín-Navarro et al. 2012**, arXiv:1208.2893 — READ (ar5iv). Break ~8 ± 1 kpc (0.77 ± 0.06 R25); truncation
  ~14 ± 2 kpc (1.09 ± 0.05 R25), "close to the outermost optical extent"; h_B/h_T = 1.9 ± 0.4; in stellar mass density
  h0/h_T = 2.8 ± 0.3; **the post-truncation scale length h_T = 1.5 ± 0.1 kpc**; μ(r') at truncation 24.1 ± 0.2 (text)
  / 24.2 (Table 5). Breaks "might be a phenomena related to a threshold in the star formation"; truncations "more
  likely a real drop in the stellar mass density", tied to the maximum angular momentum. r/h = 5 is their boundary
  between breaks and truncations.
- **Chamba, Trujillo & Knapen 2022**, arXiv:2209.05497 (A&A 667, A87) — READ (arxiv html, 0-100k). The edge is "the
  outermost radial location associated with a significant drop in either past or ongoing in-situ star formation";
  spirals' Σ*(R_edge) "1.1±0.04M⊙/pc2" (upper limits, no PSF correction). Sharpness not quantified; at low inclination
  "a very soft bump (or shallow change in slope)", edge-ons "a sharper cut off"; spirals' signature "a sudden
  reddening"; R_edge/R_e "about 3–4". Trujillo et al. 2020: NOT READ.
- **Minniti et al. 2011**, arXiv:1105.3151 — READ (ar5iv). "there is an edge of the stellar disk of the Milky Way at
  R=13.9±0.5 kpc" (R0 = 8 kpc). Sect. III: "It is difficult to measure the sharpness of the cutoff"; "a break in the
  slope of the distribution would also be consistent with the data".
- **López-Corredoira et al. 2018**, arXiv:1804.03064 — READ (ar5iv). "the presence of disk stars at R>26 kpc (99.7%
  C.L.) and even at R>31 kpc (95.4% C.L.)"; "This analysis corroborates through statistical spectroscopy the lack of a
  radial truncation in the stellar disk"; "The surface density may not fall off abruptly" (the flare carries stars to
  greater heights).
- Carraro et al. 2010: NOT READ.

### S103.3 Against the model `[inferred]`

| quantity | measured (READ) | model |
|---|---|---|
| truncation radius / h | edge-on 2-5 (van der Kruit's review); ~4-5 boundary (MN12); breaks 2.5 ± 0.6 (PT06 II-CT), Type III 4.9; Type I unbroken to 6-8 h | 9.7 h (MW), 10.7 h (N4414) |
| truncation radius, kpc | 14 ± 2 kpc (MN12's sample); the Milky Way 13.9 kpc (Minniti) or none to > 26-31 kpc (López-Corredoira) | 23.7 kpc (MW), ~18 kpc (N4414) |
| outer e-folding | h_T = 1.5 ± 0.1 kpc (MN12); "less than about 1 kpc" (vdK&S 1981 via the review, an upper bound, edge-on); h_in/h_out 2.1 (1.3-3.6) for breaks | 0.037 kpc |
| fall over 0.3 kpc | 1.22x at h_T = 1.5 kpc; 1.35x at 1 kpc | 3 500x (340x on the render's arrays) |
| face-on | "a very soft bump" (Chamba 2022); "(much) less sharp" face-on (vdK) | a step in the face-on light |

The model's edge is **outside the measured range on both counts**: about twice as far out in scale lengths as measured
truncations (9.7-10.7 h against 2-5 h; Type I discs show no break to 6-8 h, so an edge beyond 8 h is not excluded by
Pohlen & Trujillo, but no truncation that far out was read), and some 25-40x sharper than any measured outer length
(37 pc against MN12's 1.5 ± 0.1 kpc and the edge-on "less than about 1 kpc" bound). **No fall that steep is measured
anywhere read**, edge-on or face-on. For the Milky Way the sources disagree (an edge at 13.9 kpc against disc stars
past 26-31 kpc); neither supports a step at 23.7 kpc. Chamba's 1.1 M☉/pc² is a check on where an edge sits (Σ* at the
model's edge, not computed here), not a softening law.

### S103.4 Candidates, and the gate's ruling

The reader's candidates for a sourced softening: (1) beyond the edge an outer exponential of h_out = h_in / 2.1 (PT06
Type II-CT) or h_in / 2.8 in stellar mass (MN12) — one new constant, a ratio READ; (2) an absolute h_T = 1.5 kpc (MN12)
— less portable to NGC 4414; (3) the physical route MN12 name (maximum angular momentum) and López-Corredoira's (the
flare) — no closed form read.

**The gate's first ruling (D273 item 3), corrected on the second reading (item 8, below).** Item 3 ruled the entry's
reading done and the destination batch R, with the mend "at the cause": two hard switches meeting, the mend what the
threshold law's source says about star formation below the threshold. **That last clause is WITHDRAWN** (item 8): the
switch is not a step, and the cliff is the gas's own. What stands of item 3: the measured fall-off length (1.5 kpc,
MN12) as a disclosed check, and no outer exponential pasted onto the stars.

### S103.5 The second reading: star formation below the threshold, and the gas's own end (reader RT)

S103's second reader RT (Opus, read-only; note `s104_RT.md` in the session's scratchpad, section A) read the code at
the edge and the sources below the threshold. Same tags; every web number through an extracting fetch.

**The code (facts).**
- The switch is a tanh, not a step: `stages/sfh.py` `THRESHOLD_WIDTH = 0.25`, `star_formation_rate` Ψ = KS_NORM
  Σ_gas^KS_INDEX s, s = 0.5 [1 + tanh((Σ_gas − Σ_crit) / (0.25 Σ_crit))]. The docstring calls the tanh "a numerical
  requirement" (a step made the rate wander with the grid); **the width 0.25 has no cited source**.
- The threshold: Σ_crit = α κ(R) σ_g / (3.36 G), `TOOMRE_ALPHA` 0.69 and `GAS_DISPERSION` 6 km/s in `level0.py`,
  marked recall there — **both now READ** in Martin & Kennicutt 2001 sect. 5 (α_Q median 0.69, scatter about ±0.2;
  σ_g 6 km/s assumed). 3.26 M☉/pc² at 23.66 kpc on `milky_way`.
- The tail's end: `stages/halo.py` `angular_momentum_excess` — Bullock et al. 2001's M(<j) = M μ j/(j0 + j), dM/dj
  cut at j_max = j0/(μ − 1): a hard end.
- The numbers at the edge (S102's probe log, `milky_way`): Σ_gas 2.585 -> 0.101 M☉/pc² from 23.663 to 24.188 kpc
  (25.6-fold, an e-fold of 0.16 kpc); Σ_crit 3.264 -> 3.189; the SFR 1.505e-4 -> 4.364e-9; Σ* 0.2524 -> 7.307e-5. The
  gas is already under the threshold from about 14 kpc out (5.09 against 5.76 at 14.1 kpc): the outer disc forms stars
  only through the tanh's lower wing. Of the SFR's 3.5e4-fold fall, the Kennicutt-Schmidt power gives 25.6^1.4 = 94x
  and the tanh 370x `[inferred, from sfh.py and the log]`.

**Below the threshold, what the sources say.**
- Kennicutt 1989 (ApJ 344, 685): NOT READ (ADS scan only). The "soft cut-off in Kennicutt's own text" stays unread.
- Martin & Kennicutt 2001, astro-ph/0103181 — READ: sect. 3.2 "the drop in SFR per unit area at the threshold is very
  sharp", by a factor 3 to 400 over one ~10 arcsec resolution element (the element in kpc NOT READ); some profiles
  "do not show such strong discontinuities"; sect. 3.5.2 local dense regions "may allow cloud formation (and
  subsequently star formation) even where" the averaged gas is sub-critical. No law below the threshold.
- Schaye 2004, astro-ph/0205125 — READ: the warm-to-cold transition "fairly sudden"; "Below the threshold surface
  density both the fraction of gas in the cold phase and the molecular fraction decline rapidly" (sect. VI); a sharp
  threshold in the local gas, no sub-threshold law, no width.
- Bigiel et al. 2010, arXiv:1007.3498 — READ: outer discs, SFE against Σ_HI "indices of 0.7+/-0.1"; depletion times
  "~10^11 yr"; "no clear evidence for step-function type star formation thresholds"; the fit's normalisation NOT
  PRINTED (Fig. 9, an image); the page's last 15 000 characters not read.
- Thilker et al. 2007, arXiv:0712.3555 — READ: XUV discs in ~29 %; "GALEX shows extensive SF in subcritical zones for
  which Q>1"; outer-disc SFR "a few percent" of the total. No law.
- Elmegreen & Hunter 2006, astro-ph/0509190 — READ: a local rate above a local Σ_c over a log-normal of local columns
  (eqs. 1-4; C not given a number); "it will rarely truncate suddenly". Elmegreen & Hunter 2015: NOT FETCHED.
- Krumholz 2013 (KMT+), arXiv:1309.5100 — READ (equations transcribed): eq. 15 Σ_SFR = f_H2 ε_ff Σ / t_ff; eq. 21
  (stars and dark matter dominate the midplane) t_dep ≈ 3.1 Gyr / Σ_0^(1/4) + 100 Gyr / [(f_c/5) Z' ρ_sd,−2^(1/2) Σ_0];
  eq. 22 (gas dominates) the second term 360 Gyr / [(f_c/5) Z' Σ_0²]; f_c ~5 at ~1 kpc; it reproduces Bigiel et al.
  2010's data set. **No threshold at all**: it replaces the law everywhere.

**The gas's own end.**
- Bullock et al. 2001, astro-ph/0011001 — READ: eq. 8 and "The profile has an implicit maximum specific angular
  momentum jmax=j0/(mu-1)" (sect. III.1); of the disc built from it (sect. VI, Fig. 21): "Such an edge is clearly
  unphysical; they arise from our simplified functional characterization of the M(<j) profiles of halos." and "True
  profiles are likely to have smoother edges, the study of which requires simulations with higher mass-resolution." No
  form for the smoother edge is given. **The model's own source calls the model's cliff an artefact of its fit.**
- Wang et al. 2016, arXiv:1605.01489 — READ: D_HI at Σ_HI = 1 M☉/pc² (sect. 2); log D_HI = 0.506 log M_HI − 3.293, rms
  ~0.06 dex (eq. 2); outer profiles "well described by an exponential function with a scale length ~0.2 RHI" (sect.
  3.1). The model's gas reaches 1 M☉/pc² near 23.96 kpc, so 0.2 R_HI ≈ 4.8 kpc: **the model's gas edge is about thirty
  times steeper** `[inferred]`.
- Bland-Hawthorn et al. 2017, arXiv:1709.08733 — READ: HI discs argued to truncate at ~10^19.5 cm⁻² where the gas goes
  "from largely neutral to largely ionized"; the total hydrogen modelled as a continuing exponential (an assumption);
  no width of the edge. Maloney 1993, Bluedisks: NOT READ.

**What a model could carry** `[inferred]`. Under any star-formation law of index one or more the stars cannot fall more
gently than the gas, so **no law below the threshold mends the edge**: removing the tanh would still leave a 94x (KS
1.4) to ~670x (KMT+ eq. 21) fall within 0.5 kpc. The reader's candidates for the lower wing — K1 KMT+ (the only fully
printed law; it moves the inner disc too), K2 Bigiel's index (normalisation not printed: not a law by D1), K3
Elmegreen & Hunter's log-normal (C unprinted), K4 the tanh kept and checked against MK01's 3-400x — each give the young
stars an e-fold of at most 0.16/N kpc, missing the measured 1.5 kpc by 10-30x. If instead the gas e-folded at Wang's
~0.2 R_HI (~4.8 kpc), with Σ_SFR ~ Σ^1.7-2 the stars would e-fold at ~2.4-2.8 kpc, the measured order — a reading,
not a prediction to be judged (B5).

**The gate's ruling (D273 item 8, correcting item 3):** #226 stays carried, destination **batch R, a lane that
MEASURES first** — the gas's outer profile carried to Wang et al.'s exponential beyond the radius where the tail's own
profile becomes steeper than it (the mass-conserving form and the join `[inferred]`, the builder's table before any
build; R_HI by the model's own 1 M☉/pc² radius) — and the gate rules on the measurement. The tanh's unsourced width
0.25 is named in the entry as its own clause. Krumholz 2013 eq. 21 recorded, not taken.

---

## Part S104 — the measurement (batch R, lane RG; register #226, #237)

S104's builder RG (Opus; note `s104_RG.md` in the session's scratchpad) measured what D273 item 8 asked for, in the
worktree `galaxygen-s95-t` on `r-edge` cut from fccecee (batch Q's close). **Nothing was built**: every candidate is
a run-time monkeypatch, `r-edge` holds no commit and no tracked file moved. Production grid (n_R 400, dR 0.075 kpc,
R_max 29.96 kpc), layer off (the physics fields only). The `default` galaxy is bit-identical to `milky_way` on every
field read. The gate's ruling is item 2 of `DECISIONS.md` D274. Same tags as Part S103.

### S104.1 The sources (D1)

- **Wang et al. 2016**, arXiv:1605.01489 — READ (arxiv.org/html, an extracting fetch asked twice for verbatim).
  Sect. 2: D_HI is the major axis "where the azimuthally averaged ΣHI reaches 1 M⊙ pc−2"; R_HI = 0.5 D_HI (sect. 3.1).
  Sect. 3.1: the median profiles of the dwarfs and spirals have "a homogeneous shape in the outer regions around the
  position of RHI", "well described by an exponential function with a scale length ∼0.2 R_HI". **No scatter is
  printed for the 0.2** (only a 25-75 % band for the WHISP Sa sample), **no explicit radial range** (only "around the
  position of R_HI"); the fit excludes the early-type samples (Atlas3D, WHISP Sa). Eq. 2: log D_HI = (0.506 ± 0.003)
  log M_HI − (3.293 ± 0.009), rms ~0.06 dex. Whether Σ_HI includes helium: NOT STATED (the model's HI here is hydrogen
  only, gas × (1 − f_H2) × (1 − Y), Y = 0.27; the total-gas radius beside it).
- **Sharma & Steinmetz 2005**, astro-ph/0406533 — READ (ar5iv, the first 100k of 104k characters). Sect. V eq. 27
  P(j) = j^(α−1) e^(−j/j_d) / (j_d^α Γ(α)); eq. 28 j_d = j_tot/α. Abstract: the gas's log α mean −0.04, sd 0.11; about
  90-95 % of haloes α < 1.3; exponential discs in NFW haloes "would require 1.3<α<1.6"; particle profiles "do not
  truncate abruptly"; no j_max in the α model.
- Bullock et al. 2001 sect. VI (no smooth form; Part S103.5), Martín-Navarro et al. 2012 (1.5 ± 0.1 kpc), Pohlen &
  Trujillo 2006 (2.5 ± 0.6 h; h_in/h_out 2.1, 1.3-3.6), Thilker et al. 2007 ("a few percent" outer SFR): as read at
  S103, used as checks only.

### S104.2 The model's profiles today (fccecee; `milky_way` / `ngc_4414`)

| | milky_way | ngc_4414 |
|---|---|---|
| edge onset (last ring before the stars' local e-fold < 0.5 kpc) | 23.587 kpc | 18.112 kpc |
| stars' fall over the gate's window (23.663 -> 24.188 / 18.112 -> 18.637) | 3 437x | 1.33e5x |
| stars' fall, onset -> 29.96 kpc | 5.1e4 | 1.3e9 |
| the tail: inner radius / last ring > 0 / share | 12.28 / 24.11 / 0.0756 | 8.80 / 18.56 / 0.0816 |
| the gas's e-fold across the cliff (onset -> +0.525) | 0.28 kpc (0.16 on the window) | 0.13 kpc |
| the gas beyond: e-fold, level | 2.605 kpc = R_d(spin), ~0.1 M☉/pc² | 1.755, 0.045 |
| R_HI: HI hydrogen = 1 / total gas = 1 | 23.93 / 24.00 kpc | 18.47 / 18.51 |
| 0.2 R_HI against the cliff's e-fold | 4.79 kpc against 0.16-0.28 (17-30x steeper) | 3.69 against 0.13 (28x) |
| gas / Σ_crit | max 0.95 (7.3 kpc); < 0.9 from 11.2 kpc; 0.79 at the onset | never ≥ 0.9; 0.84 at the onset |
| stellar R_d / inner fit (0.3-0.8 of the edge) | 2.440 / 2.97 kpc | 1.675 / 2.78 kpc |
| the edge in scale lengths | 9.7 | 10.8 |
| 2 R_HI / D_HI (Wang eq. 2 from the model's M_HI) | 1.02 (M_HI 6.48e9) | 1.05 (3.65e9) |

H2 at the edge is ~1 % of the gas, so HI and the total gas cross 1 M☉/pc² within 0.07 kpc. **The gas is under the
threshold everywhere**: no radius "where the gas drops under Σ_crit" exists; what drops at the edge is gas / Σ_crit,
0.79 -> 0.03. Every star the model forms, it forms in the tanh's lower wing — **#237**, opened at S104.

The trace (code): `halo.py` `angular_momentum_excess` (Bullock's dM/dj with the hard cut at j_max) is ONE
construction read twice — the tail beyond the outer crossing (`infall_tail_surface_density`, the share, the inner
radius) and the core (the bulge's mass, scale and dispersion); the tail's mesh mass also enters the halo's second
contraction. `halo.py` interpolates the tail onto the grid and drops what lies beyond R_max (today nothing: the tail
ends at 24.1 / 18.6 kpc). `sfh.py` sums the exponential infall (normalised on the grid, to 30 kpc) and the tail, the
budget closing to every retained baryon by construction; everything after `sfh` moves with it.

### S104.3 The candidates (monkeypatches) and what each moves

- **C1, the graft:** beyond R_j — the first ring past the tail's peak whose infall log-slope is steeper than −1/h —
  the infall continues as total(R_j) exp(−(R − R_j)/h), h = 0.2 R_HI with R_HI the model's own HI 1 M☉/pc² radius,
  iterated to its fixed point (`milky_way` 4.786 -> 5.414 -> 5.504 -> 5.517 -> 5.520 kpc; `ngc_4414` 3.693 -> 4.447).
  `[inferred]`: Wang's gas shape applied to the INFALL, the join at R_j, the fixed point. The halo not re-run.
- **C1u:** C1 with the whole on-grid infall scaled by one factor to close the budget (0.9696 / 0.9552).
- **C1m:** C1 closed by scaling the tail inside R_j alone (0.628 / 0.487).
- **C2, the cause:** Sharma & Steinmetz's gamma (eqs. 27-28) for Bullock's μ in `angular_momentum_excess`, the mean j
  matched; α = 0.912 (their gas mean), with 0.708 / 1.175 (± 1 sd) and 1.41 as sensitivity. Moves the tail AND the
  bulge (one construction).

| `milky_way` (`ngc_4414`) | before | C1 | C1u | C1m | C2 (α 0.912) |
|---|---|---|---|---|---|
| added mass (share of the on-grid infall) | — | 1.60e9 M☉, 3.1 % (1.84e9, 4.7 %) | 0 | −6.4e8 (−1.0e9) | conserved on the mesh; 18 % (6 %) of the tail off the grid |
| the gas's e-fold beyond the old edge | 2.61 (1.76) kpc | 5.84 (4.64) | 5.80 (4.61) | 5.57 (4.46) | 5.92 (5.05) |
| the stars' e-fold beyond | 2.19 (1.24)* | 1.32 (1.29) | 1.34 (1.32) | 1.69 (1.80) | 2.28 (2.09) |
| the stars' fall over the window | 3 437 (1.33e5) | 1.50 (1.46) | 1.51 (1.50) | 1.47 (1.59) | 1.32 (1.46) |
| the stars' fall, onset -> 29.96 kpc | 5.1e4 (1.3e9) | 105 (6 856) | 100 (6 385) | 45 (911) | 16 (344) |
| stellar mass | 4.742e10 (3.900e10) | +0.09 % (+0.24 %) | −3.0 % (−4.2 %) | −2.0 % (−3.4 %) | −0.02 % (−1.2 %) |
| gas within 30 kpc | 1.117e10 (6.63e9) | +13.9 % (+26.4 %) | +12.8 % (+24.7 %) | +2.6 % (+4.7 %) | −4.9 % (+4.6 %) |
| SFR | 1.860 (0.686) M☉/yr | +1.5 % (+5.5 %) | −2.2 % (+0.3 %) | −14 % (−28 %) | −16 % (−24 %) |
| SFR beyond the old edge + 0.2 (share) | 4.4e-4 (9.2e-4) | 0.028, 1.5 % (0.038, 5.3 %) | 0.024, 1.3 % (0.032, 4.7 %) | 0.003 (0.001) | 4.7e-4 (8.5e-4) |
| R_HI | 23.93 (18.47) | 27.60 (22.24) | 27.43 (22.04) | 25.18 (19.14) | 22.67 (18.54) |
| 2 R_HI / D_HI | 1.02 (1.05) | 1.08 (1.09) | 1.08 (1.09) | 1.05 (1.05) | 1.00 (1.02) |
| the break, in R_d (PT06 2.5 ± 0.6) | 9.7 (10.8), a cliff | 9.7 (10.8) | same | no break | no break |
| h_in / h_out: R_d / h_out; inner fit / h_out (PT06 2.1, 1.3-3.6) | — | 1.84, 2.19 (1.30, 2.05) | 1.81, 2.12 (1.27, 1.97) | 1.44, 1.20 | 1.07, 0.76 (0.80, 0.77): the outer disc SHALLOWER |
| largest change in the stars inside 0.8 of the onset | — | 9e-6 (0) | −10.5 % (−11.3 %) | −81 % (−92 %) | −93 % (−88 %) |
| Σ* at 8.15 kpc | 37.05 (10.55) | 37.05 (10.55) | 35.66 (9.80) | — | 38.88 (11.19) |
| bulge mass / tail share | 7.71e9 / 0.0756 | same | same | same | 7.14e9 / 0.0534 (5.87e9 / 0.0632) |
| v_c(R₀) | 238.78 (199.74) km/s | −0.03 (−0.08)** | −1.71 (−2.54) | +0.11 | +2.35 (+2.35) |
| H2 fraction (row 21) | 0.205 (0.246) | 0.180 (0.195) | 0.179 (0.194) | 0.196 | 0.214 (0.230) |
| gas / stars at the grid's end, 29.96 kpc | 0.011 / 4.9e-6 (7e-5 / 6e-10) | 0.90 / 2.3e-3 (0.24 / 1.1e-4) | 0.87 / 2.1e-3 | 0.58 / 5.6e-4 | 0.40 / 2.2e-4 |
| the gas layer's height finite to (the dust layer's edge) | 23.59 (18.11) | 23.66 (19.46) | 23.59 (19.24) | — | 17.29 (14.74) |

\* the thin exponential infall under the cliff, at 1e-4 of the disc. ** the halo not re-contracted in the probe.
C2's sensitivity (`milky_way`): α 0.708 / 1.175 / 1.41 give the bulge 1.01e10 / 4.50e9 / 3.18e9 (row 12: +31 % /
−42 % / −59 %), the tail's share 0.066 / 0.039 / 0.027, the SFR 1.46 / 1.65 / 1.68, the stars at 18.9 kpc −91 % /
−96 % / −98 %; every α gives h_in / h_out 0.65-0.74 (no break, a Type III-like outer disc). `ngc_4414` the same.

### S104.4 What is unphysical or unknown in C1 `[inferred, the builder's list]`

- Wang's 0.2 R_HI is a **stacked median shape of today's HI**, used here as the shape of everything that ever
  accretes: no source says the infall follows today's HI.
- **No scatter** is printed for the 0.2, and **no radial range** beyond "around R_HI": the graft runs it to 30 kpc
  (1.1-1.6 R_HI).
- R_HI is the model's own output fed back (a five-step fixed point); the join R_j is a slope criterion `[inferred]`;
  the early types are excluded from Wang's fit (the templates are Sbc and Sc: inside it).
- **It is not mass-conserving**: +3.1 % / +4.7 % of the infall budget from nowhere, the gas within 30 kpc +14 % /
  +26 % (row 20's hydrogen 8.15e9 -> 9.29e9 on `milky_way`, its miss −0.01 -> −0.16); closing the budget costs the
  inner disc (C1u: 3-11 %; the tanh's wing amplifies a 3 % infall cut threefold in the outer stars) or guts the outer
  disc (C1m).
- **A new edge at the grid's end**: under C1 the gas is still 0.90 / 0.24 M☉/pc² at 29.96 kpc and the arrays stop
  there; the exponential beyond 30 kpc would hold a further ~1.1e9 / ~2.3e8 M☉ `[inferred]`, dropped by the infall's
  on-grid normalisation. Whether a viewer sees a ring there was not measured on the render.
- **The break does not move**: it stays at R_j = 9.7 / 10.8 R_d, outside 2.5 ± 0.6 — C1 softens the edge, it does
  not move it. The halo does not see the added mass in the probe; Bullock gives no form for the "smoother edges", so
  no source says where in j the real fall begins.
- In its favour (read after the candidate was chosen): the stars beyond e-fold at 1.32 / 1.29 kpc against
  Martín-Navarro's 1.5 ± 0.1 (12-14 % steeper); h_in / h_out 2.19 / 2.05 inside Pohlen & Trujillo's 1.3-3.6; the
  outer SFR share 1.5 % / 5.3 %, Thilker's "a few percent" order; Wang's size-mass relation holds before and after.

C2 is the cleaner code (one line, a constant μ -> α) but a different model of the whole distribution: with any READ α
the outer disc between the tail's start and the old edge loses 88-98 % of its stars, the bulge moves, there is no
break at all, R_HI moves in, 18 % of the tail falls off the grid — and Sharma & Steinmetz say their gas αs do not make
exponential discs, the model's premise for an exponential plus a tail.

**The cost had it been built** (the builder's forecast, not run): C1 ~10-12 test nodes in ~7 files
(`test_disc_edge` restated, `test_sfh`, `test_audit`'s rows 20-21, `test_dust_layer`'s edge, `test_templates`'
hydrogen checks); C1u ~20+ nodes across ~10 files and the acceptance table; C2 larger still.

**The gate's ruling (D274 item 2):** no candidate is a law the gate can take — C1 is a measured shape applied where its
source does not apply it, with a join rule, a budget rule and a grid end that are choices; C2, the mend at the cause,
is measured and fails. #226 stays carried, **the owner's**: (i) the edge stays as S102 declared it, outside the
measured range and said so; or (ii) C1 as a DISCLOSED graft (the added mass declared, the grid's end settled first),
built on the owner's word. **The gate recommends (ii)** and says what counts against it: the two agreements in its
favour were read after the candidate was chosen, the break stays at the wrong radius, and 3-5 % of the budget appears
from nowhere. Nothing built held. The fact found on the way opens **#237** (the threshold's width, a reading).

**Not read / not measured:** Sharma & Steinmetz's last 4k characters and Fig. 24's values (an image); whether
Wang's Σ_HI includes helium; a smooth M(<j) edge in any source; the render at 30 kpc under C1; the halo re-contracted
with C1's mass.
