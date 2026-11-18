# READING_DISC_EDGE — do real discs end as sharply as the model's? Truncations, breaks and the Milky Way's edge (S103, D273; register #226)

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
