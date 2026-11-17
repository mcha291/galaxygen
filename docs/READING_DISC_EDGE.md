# READING_DISC_EDGE — do real discs end as sharply as the model's? Truncations, breaks and the Milky Way's edge (S103, D273; register #226)

**What this file is (2026-11-17, S103, BUILD_VII row 105, the reading row).** S102 named and declared the model's
edge where it is computed: the disc ends where the infall's high-angular-momentum tail ends (`milky_way` 0 from 24.19
kpc, `ngc_4414` from 18.64 kpc), and the star-formation threshold's switch turns the gas's 26-fold fall into the
stars' 3 500-fold (register #226's S102 paragraphs; `tests/test_disc_edge.py`). What was left is the reading: whether
real discs end within 0.3 kpc. S103's reader RB (an Opus agent, read-only; its note `s103_RB.md` in the session's
scratchpad, section B) read it. The gate's ruling is item 3 of `DECISIONS.md` D273.

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

**The gate's ruling (D273 item 3):** the entry's reading is done; it stays carried with a sourced destination, **batch
R**. The cause is two hard switches meeting (the infall tail's end and the star-formation threshold), so the mend is
at the cause — what the threshold law's source says about star formation below the threshold (a soft cut-off is in
Kennicutt's and Schaye 2004's own text: READ before build) — **not an outer exponential pasted on**; the measured
fall-off length (1.5 kpc, MN12) is then the disclosed check. Kennicutt's and Schaye 2004's text on the soft cut-off:
NOT READ at S103.
