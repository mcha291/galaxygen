# READING_CLOUD_LAYER — the molecular layer's thickness: the clouds' scale height (S67, D229)

**The lead's note (2026-10-18, entered at S67 on the owner's order).** The owner: "read a source for the clouds'
scale height and fix the layer in the model before I retune." Until S67 the cloud census drew each cloud's height
from a sech²(z/2h) layer at `CLOUD_LAYER_SHARE` 0.5 of the thin disc's scale height (177.8 pc on `milky_way`, 477 pc
on `ngc_4414`), "a stated guess with no source" (debt #95); D228 measured the clouds floating to 1.95 kpc and the
viewer's whole-galaxy clouds drawing near-black. One blind Opus reader (no repository access) read the sources
below; what is below the rule is its report in substance, the quotations as the reader gave them. **What the lead
took from it** (D229 rules on it): (1) the Milky Way's molecular layer at R0 is about 120 pc FWHM, roughly
independent of R from 2 kpc to R0 (Bronfman et al. 1988, via Ferrière 2001), with 118 pc (Bronfman et al. 2000) and
136 ± 17 pc (Clemens, Sanders & Scoville 1988) beside it and Malhotra 1994's σ_z 58 pc at R0 (FWHM 137) the high
reading; (2) massive clouds sit in a layer as thin as the CO layer or thinner (Stark & Lee 2005); (3) the layer flares
outside R0 (Nakanishi & Sofue 2006, FWHM 160-186 pc at 8-11 kpc) and the sources conflict inside R0 (Marasco et al.
2017 falling with R, Malhotra and Nakanishi & Sofue rising); (4) edge-on spirals' CO widths are σ = 31-89 pc plus 1-5
pc/kpc × R (Yim et al. 2014). The layer is entered as an absolute thickness, the level-0 constant
`MOLECULAR_LAYER_FWHM` = 120 pc, `[verified: Bronfman et al. 1988 via Ferrière 2001 §II.B]` (was §II.A; *re-read at Audit V (S70)*); the clouds' scale height is the sech² h whose FWHM that is,
h = FWHM / (4 artanh(1/√2)) = FWHM / 3.5255 = 34.04 pc (D229).

---

## The reading (the reader's report, 2026-10-18)

Conversions: a Gaussian's σ = FWHM / 2.3548 = HWHM / 1.1774; a sech²(z/2h) layer's FWHM = 3.5255 h.

- **Malhotra 1994** (ApJ 433, 687; astro-ph/9404028). A Gaussian σ_z rising with R: ~10 pc at 2.6 kpc, 30-52 pc over
  3.4-7.2 kpc; the fit "extrapolates to give a scale height 58 pc at R⊙" (FWHM 137 pc); the gradient 5.5 pc/kpc.
- **Clemens, Sanders & Scoville 1988** (ApJ 327, 139), read via Ferrière 2001 (RMP 73, 1031) §II.B: FWHM 136 ± 17 pc
  at R0, ∝ R^0.58.
- **Bronfman et al. 1988** (ApJ 324, 248), read via Ferrière 2001 §II.B: "a FWHM of 120 ± 18 pc, roughly independent
  of R" from 2 kpc to R0. **The value entered** (`MOLECULAR_LAYER_FWHM`).
- **Bronfman et al. 2000** (A&A 358, 521; astro-ph/0006104), Table 7 and §4.1: a mean half-width of 58-60 pc for
  R/R0 0.2-1.0, "118 pc (FWHM) for the layer of molecular gas traced by CO"; the OB stars' layer FWHM 73 pc, "62% the
  thickness of the molecular gas disk" (a disclosed check on the HII layer, not a pin).
- **Roman-Duval et al. 2016** (ApJ 818, 144): the inner Galaxy's FWHM ~110 pc; the diffuse molecular gas 130-200 pc;
  the outer Galaxy 110-300 pc.
- **Marasco et al. 2017** (arXiv 1707.00743): the HWHM from ~100 pc at the centre to ~50 pc at R0 (52 pc held fixed
  beyond 7 kpc) - falling with R inside R0, against Malhotra's and Nakanishi & Sofue's rise.
- **Su et al. 2021** (ApJ 910, 131): a thin component of FWHM ~85 pc and a thick one of ~280 pc.
- **Nakanishi & Sofue 2006** (PASJ; astro-ph/0610769), Table 1, the sech² FWHM: 48 pc at 0-1 kpc rising to 90 ± 30 pc
  at 7-8 kpc, 186 pc at 8-9 kpc, 160 pc at 10-11 kpc - the flaring outside R0.
- **Stark & Lee 2005** (ApJ 619, L159): clouds below ~2 × 10⁵ M☉ have a scale height of ~35 pc, "not significantly
  different" from the CO layer's; the most massive clouds sit in a thinner layer.
- **Yim et al. 2014** (arXiv 1408.5905), Table 3, edge-on spirals' CO: σ = 89 + 5.0 R pc (NGC 4157), 33 + 1.1 R pc
  (NGC 4565), 31 + 2.7 R pc (NGC 5907), R in kpc - the bracket `ngc_4414`'s one value is disclosed against.
- **HI at R0**, for scale: FWHM 230 pc (Dickey & Lockman 1990, via Ferrière 2001).
- **Heyer & Dame 2015** (ARA&A) was not read: the fetch returned 403.

Read 2026-10-18 by a blind reader (no repository access); quotations as the reader gave them.
