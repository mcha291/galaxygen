# READING_DISC_HEIGHT — the stellar disc's scale height: one per galaxy, its constancy with radius, its flattening (S98, D267)

**What this file is (2026-11-12, S98, BUILD_VI row 98).** The reading register entry #227 asked for: S97's trace
(`READING_PICTURES.md` section 13; the analyst's note `s97_R.md`, gap 3) found `thin_disc_scale_height` read at the
Milky Way's `R_SUN` = 8.2 kpc on every template, and asked of Kregel, van der Kruit & de Grijs 2002 at which radius
each h_z is fitted and whether the paper holds it constant with radius. S98's reader A (an Opus reader; its note
`s98_A.md` in the session's scratchpad) fetched the sources below in this session — the PDFs from arxiv.org, their
text by `pdftotext -layout`, Ranaivoharimina et al. 2024 as arXiv HTML by a summarising fetch with the equation asked
verbatim. What the gate took from it is in `DECISIONS.md` D267 and register #227; what it does to the pictures is
`READING_PICTURES.md` section 14.

**Tags.** `[verified: source, place]` — quoted from a page fetched in S98; `[inferred]` — the reader's own arithmetic
or reading of two definitions, no number moved; `[secondary: ...]` — a source known only as another paper quotes it;
"medium confidence" where the reader says so (a text layer's column alignment). NOT FOUND and NOT READ are said plainly
where they apply. Nothing here moved a constant, a pin or a model byte.

---

## Part S98 — what an observed disc height is, and what the sources say against the model's law (2026-11-12, BUILD_VI row 98; reader A)

### S98.1 Kregel, van der Kruit & de Grijs 2002 — one exponential height per galaxy, its constancy assumed

- **Source.** Kregel, van der Kruit & de Grijs 2002, MNRAS 334, 646, arXiv:astro-ph/0204154 — READ, the full text.
  Sample: 34 ESO-LV southern edge-on spirals, I band; H0 = 75.
- **What the height is.** Sect. 3.1, eq. (1): L(R,z) = L0 e^-R/hR e^-z/hz, "hR and hz are the radial scalelength and
  the vertical scaleheight (in terms of the vertical scale parameter z0; hz = 0.5 z0)" `[verified: Kregel et al. 2002,
  Sect. 3.1]` — hz is the EXPONENTIAL scale height. The model's `scale_height` (`stages/vertical.py` lines 45-52),
  σ² / (2πGΣ) = z0/2 of the isothermal sech²(z/z0) sheet, has the far wing exp(−2z/z0) = exp(−z/h): the same convention
  as hz `[inferred: the reader's reading of the two definitions, no number moved]`.
- **Where it is fitted: over the whole disc, one value per galaxy.** Sect. 3.2: a 2-D least-squares fit of eqs. (2)-(4)
  (disc + bulge) to the masked I-band image; the mask is |z| < 1.5 hz ("to solely study the old stellar population");
  data outside the 1σ contour of the model are excluded; an outer fitting boundary is set by eye inside any
  truncation. No radial range in scale lengths is named: the fit is over all R inside that boundary and outside the
  mask. Table 1 (columns 12-14) gives one hz per galaxy `[verified: Kregel et al. 2002, Sect. 3.2, Table 1]`.
- **Constancy with radius: ASSUMED, on de Grijs & Peletier 1997, not measured in this paper.** Sect. 3.1: "The
  vertical exponential behaviour is taken to be independent of radius following de Grijs & Peletier (1997). They
  showed that, in the discs of most of the spirals in our sample (at least all late-type galaxies, which is about two
  thirds), the scaleheight does not increase with radius." Sect. 4 (the truncations): flaring as their cause would
  need "a rate larger than 1 hz per hR"; "such thickening is not observed (de Grijs & Peletier 1997; Morrison et al.
  1994; Fry et al. 1999)" `[verified: Kregel et al. 2002, Sects. 3.1, 4]`.
- **The flattening and its scatter.** Sect. 5.1: "about 70 percent of spirals seem to have a flattening between 6 and
  8. The average flattening of the diameter-limited distribution is hR/hz = 8.5 +/- 2.9 (1 sigma), while that of the
  volume corrected distribution is hR/hz = 7.3 +/- 2.2 (1 sigma)." And: "the spread in the hR-hz plane is real,
  suggesting that the physical relation between hR and hz cannot be described by a simple linear functionality
  expected for discs of constant flattening" `[verified: Kregel et al. 2002, Sect. 5.1]`. The model's
  `ARM_LAYER_FLATTENING` 7.3 ± 2.2 is the volume-corrected value: **MATCH**.
- **Against V_max and type.** Sect. 5.1: hz rises with vmax (Spearman 0.74; "more massive spiral galaxies have both
  larger and thicker discs"); "We observe no clear trend with morphological type" (hR, hz against type); the
  flattening's range and maximum "seem to increase with both maximum rotational velocity and total H i mass", a
  weaker trend with Hubble type, and "the minimum disc flattening seems to be independent of all of these parameters".
  No fitted relation hR/hz(vmax) is printed (Fig. 6c only). Volume-corrected: "about 90 percent of the spirals has hz <
  0.6 kpc" `[verified: Kregel et al. 2002, Sect. 5.1]`.
- **The rows near NGC 4414 (Sb-Sc, vmax 200-260 km/s)**, Table 1 as `pdftotext` laid it out — the asterisks marking
  Tully-Fisher vmax were lost; **medium confidence on the column alignment**: 263-G15 Sc vmax 260, hz 0.43 kpc, hR/hz
  10.8 ± 0.9; 269-G15 Sc 233, 0.87, 6.9 ± 1.6; 435-G50 Sc 231, 0.28, 7.8 ± 1.6; 435-G14 Sbc 204, 0.53, 5.3 ± 1.1;
  446-G18 Sb 209, 0.60, 12.9 ± 1.6; 487-G02 Sb 226, 0.38, 6.4 ± 0.8. The six rows' hR/hz: mean 8.35, range 5.3-12.9;
  the three Sc 8.5 `[inferred: the reader's arithmetic]` — six rows, not a fit. hR is the I-band (photometric) scale
  length. NGC 4414 is not in the sample.

### S98.2 de Grijs & Peletier 1997 — constant to first order, rising with radius in early types

- **Source.** de Grijs & Peletier 1997, A&A 320, L21, arXiv:astro-ph/9702215 — READ, the full text (4 pages).
- **Sample and method.** 48 edge-on (i ≥ 87°) ESO-LV galaxies, diameter-limited; B, V, R, I. Vertical profiles at
  several radii, an exponential fitted between 1.5 and 4 scale heights; the gradient of hz along the major axis fitted
  between 1.5 and 3.5 (and 2.0-4.0) I-band scale lengths; the bulge negligible outside 1.8 ± 0.3 scale lengths.
- **What it prints.** The abstract: "Although the exponential disk scale height is constant to first order
  approximation, we show that for the large majority of galaxies in our sample, the scale height increases with
  distance along the major axis. The effect is strongest for early-type galaxies, where the increase of the scale
  height can be as much as a factor of 1.5 per scalelength, but is almost 0 for the latest-type galaxies"
  `[verified: de Grijs & Peletier 1997, abstract]`. The relation by type is a figure only (Fig. 2); no table of
  gradients. The paper's interpretation: a thick disc with a longer scale length (early types).
- **Quoted there as background** `[secondary: as quoted by de Grijs & Peletier; the originals not fetched]`: van der
  Kruit & Searle 1981-82 found z0 "in good approximation independent of position along the major axis"; Shaw &
  Gilmore 1990, 10 edge-ons, radial variation "typically within +/- 3% of the derived mean".

### S98.3 Ranaivoharimina et al. 2024 — a slow rise from the centre to R₂₅, and hz against hR

- **Source.** Ranaivoharimina et al. 2024 (accepted, ApJ), arXiv:2410.09762 — READ as arXiv HTML by a **summarising
  fetch**, the equation asked verbatim. Sample: 46 S4G edge-ons, 3.6 µm.
- **The flare.** Sect. III.3: radial profiles of hz from a 1-D "box" model fitted with a SINGLE sech or exponential
  component (a thick disc's light is inside it). Eq. (13), as the fetch gave it: "h_z(R25)/h_z(R=0) = -0.13 T + 2.37
  +/- 0.36", "with h_z(R25)/h_z(R=0) the disk flaring amplitude and T the morphological type"; "only two galaxies
  (IC5052 and NGC5023) have less than 10 % disk flaring amplitude" `[verified: Ranaivoharimina et al. 2024, Sect.
  III.3, eq. 13 (summarising fetch)]`. At T = 5 (Sc) that is 1.72 between the centre and R₂₅ `[inferred]`: a slow rise
  over the whole optical disc, not tens.
- **hz against hR.** Sect. III.4.1, eq. (14): log10(hz/kpc) = 0.90 log10(hR/kpc) − 0.81 ± 0.04, scatter 0.11 dex; q_R =
  hR/hz uncorrelated with hR after the inclination correction ("seems to be constant"; no mean printed, per the fetch)
  `[verified: Ranaivoharimina et al. 2024, Sect. III.4.1, eq. 14 (summarising fetch)]`. Eq. (14) at hR = 2.333 kpc
  (NGC 4414's `photometric_scale_length`) gives hz 0.33 kpc; at the mass length 1.675 kpc, 0.25 kpc `[inferred: the
  reader's arithmetic; 3.6 µm; the paper's hR is its own fit]`. NGC 4414 is not in the sample.

### S98.4 NGC 4414's own thickness — NOT FOUND

One web search found no measured scale height for NGC 4414; at an inclination of about 52-57° none is expected from
its own image. It is not in Kregel et al.'s nor in Ranaivoharimina et al.'s sample (checked by the reader).
`READING_NGC_4414.md` has no row on the galaxy's thickness (S97, `s97_R.md`).

### S98.5 What the sources say against the model's law

- **The model** (S97's trace, `s97_R.md` gap 3; register #227): `thin_disc_scale_height` is one scalar per galaxy, the
  law h_z = σ_z² / (2πGΣ) evaluated at `R_SUN` = 8.2 kpc on every template — **926.4 pc** on `ngc_4414` (4.90 mass
  scale lengths out), **345.9 pc** on `milky_way` (3.36). Read ring by ring, the same law gives on `ngc_4414` 29 pc at 1
  kpc, 47 at 2, 76 at 3, 128 at 4, 209 at 5, 351 at 6, 558 at 7, 933 at 8.2, 1304 at 10 kpc, and on `milky_way` 46, 61,
  79, 105, 139, 188, 248, 348, 582 — a **flare of a factor 32 between 1 and 8.2 kpc on `ngc_4414`, 7.5 on the Milky
  Way**, because σ_z is set by birth time only, not by radius. Its stellar-mass-weighted mean is 222 pc (`ngc_4414`) and
  215 pc (`milky_way`).
- **The sources.** Every source read has the old disc's exponential height constant to first order with radius (van
  der Kruit & Searle as quoted; Kregel et al. assume it on de Grijs & Peletier's measurement), rising by at most about
  1.5 per scale length in early types and by about nothing in the latest (de Grijs & Peletier), 1.3-2.4 from the
  centre to R₂₅ in a single-component fit (Ranaivoharimina et al.). **No source shows a flare of tens inside the
  optical disc.** An observed "hz" is ONE number per galaxy from a fit over the disc outside the bulge — Kregel et al.:
  2-D over the whole disc inside the truncation; de Grijs & Peletier: 1.5-3.5 scale lengths.
- **No source names "the height at a fixed number of scale lengths."** The nearest is de Grijs & Peletier's window,
  1.5-3.5 (or 2-4) I-band scale lengths, and Kregel et al.'s whole-disc fit.
- **The flare is a defect, not a wrong number against a source**: the law flaring 7.5- to 32-fold inside the optical
  disc contradicts every source read; S97's trace places it in σ_z set by birth time only. A height taken from the
  flattening (ruleset A below) removes it from the render, not from the catalogues' per-star heights.
- **How sure** (the reader): high on what the sources print (full texts, Ranaivoharimina et al. by a summarising
  fetch); medium on ruleset A being the right reading (a design call).

### S98.6 The reader's three rulesets for #227 (each with what it would move)

- **Ruleset A — the flattening (the reader's recommendation).** h_z = h_R / 7.3 (± 2.2), Kregel et al.'s
  volume-corrected mean — the constant the pattern stage already holds, so the model holds one stellar height, not
  two; constant with radius, as the source assumes. It moves `ngc_4414` 926 → **229 pc** on the mass length (1.675
  kpc) or **320 pc** on the photometric one (2.333); the Milky Way 346 → **334 pc** (mass, 2.440) or **571 pc**
  (photometric, 4.167). Which length stands for Kregel et al.'s I-band hR must be ruled (the source's is a light
  length; the pattern stage uses checkpoint 1's spin length). It does not cover hz's vmax trend (a figure, no fit
  printed), the spread (a draw on 2.2 would be a choice), the age split (#184), or the flare. The test it would carry:
  the published `thin_disc_scale_height` over the scale length = 7.3 on every template; the seven readers re-read.
- **Ruleset B — the law at the sources' window.** Keep σ_z² / (2πGΣ) but evaluate it at a fixed number of the
  template's own scale lengths (e.g. the middle of de Grijs & Peletier's 1.5-3.5) instead of `R_SUN`. S97's numbers:
  at 2.2 h_R 155 / 110 pc (Milky Way / NGC 4414), at 3.36 h_R 348 / 292 pc — steeply dependent on the radius chosen,
  because the law flares exponentially, which the sources contradict. Weaker: the window is a fit range, not a rule
  for "the" height.
- **Ruleset C — the law's stellar-mass-weighted mean** (215 / 222 pc on the Milky Way / NGC 4414): no source defines
  hz so. Not recommended.
- **The gate's ruling (D267):** #227 a build with its source read — the model holds one stellar height, the flattening
  it already holds (ruleset A); which scale length (mass 229 / 334 pc, recommended, or photometric 320 / 571 pc) and
  whether the Milky Way keeps the law at `R_SUN` as its solar-neighbourhood reading beside it are the owner's
  (BUILD_VI §6); the law's flare is the entry's second half. Noted at the gate: neither template publishes a thick
  disc — #27's, permanent.

### S98.7 Not read

Kregel et al.'s Figs. 5e and 6c (figures, no fits printed); de Grijs & Peletier's Fig. 2 slopes (a figure only);
Ranaivoharimina et al.'s per-galaxy tables (the fetch summarised; only the equations were asked verbatim); van der
Kruit & Searle 1981-82 and Shaw & Gilmore 1990 (only as quoted). No model run (a reader).
