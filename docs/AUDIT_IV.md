# AUDIT_IV — Session 43: the renderer's own audit (S38–S42: V1–V4 and the owner's four answers)

Once, on Fable, after the build, as the project does (S10's two runs, S21's aim (a), S37's Audit III); commissioned
by the owner on 2026-09-30 ("run the tags and do them with each session from now on, then proceed to do Audit IV",
D193 (b)). **Nothing here changes a number in the model or the viewer** (B3): a finding that would is a debt or a
ruling for the owner, with the sentence that decides it. Decision D194 records the findings, the method and the
counts; D193 records the commission.

## 0. The aim, stated before any code file was opened (D113), and how it is to read

Written on `session-43` after the rulings' commit (88a86ed) and before `spectra.py`, `service.py`, `http.py`,
`nebular.py`'s grid reading, `region.ts`, `RegionVolume.tsx`, `FieldVolume.tsx`, `colors.ts`, `psf.ts`,
`filters.json`, `instruments.json`, the two fetch tools or any of the S38–S42 tests were opened in this session.
What the aim names, it names from D188–D192, BRIEF.md's option 1, RENDER_PHYSICS §0 and the register's #107–#120.

1. **Every constant, table and cited choice that entered code S38–S42 re-read against the sentence it cites**, by a
   read-only agent that did not write them, labelled MATCH / DIFFERS / ADOPTED-NOT-MEASURED / MISATTRIBUTED /
   UNREACHABLE as Audit III's re-reader did (D186's method notes: every re-read labelled READ / second-hand /
   DERIVED / RECALL; equation numbers counted from the LaTeX; nothing from recall). The list the decisions name,
   which the brief will make exact once the files are opened:
   - *V1 (D188):* the eight Bessell bands' reference wavelengths, widths and zero points read from the SVO Filter
     Profile Service pages (Generic/Bessell U B V R I, Generic/Bessell_JHKLM J H K, "Bessell & Brett 1988"); the
     SED's joins (power law between bands, blackbody tails beyond U and K) and the twelve band-consistency passes —
     stated choices, to be labelled as such; the anchor at SVO's λ_ref (the pivot) rather than λ_eff; SVO's Vega
     against YBC's (#107, `[inferred]`).
   - *V2 (D189):* `spectra.GRAIN_TABLE` — 110 rows transcribed from Draine's `kext_albedo_WD_MW_3.1_60_D03.all`
     read as a page — every row against the file (the test checks the rows against each other; the audit checks
     them against the source); the per-filter A_λ/A_V it yields (A_B/A_V 1.302, A_R 0.794, A_J 0.298, A_H 0.187,
     A_K 0.113); the Henyey–Greenstein form cited to Bosschaart & Olofsson 2026 (arXiv:2604.08379 eq. 3) and the
     in-plane average `[inferred]`; the 21-point phase table's end values (0.485 face-on, 1.51 edge-on, mean 1);
     the "ir" set's J H K boxes at the SVO numbers and the TIR box 8–1000 µm; `clouds.CLOUD_LAYER_SHARE` 0.5 (#95's
     guess, disclosed) and the DIG's 1.4 kpc (Haffner §II.A, re-read at S37); the sech² layers; the TIR box's
     stated coverage (6.8 × 10⁻⁴ of Σ_IR beyond 1 mm) recomputed from the modified blackbody at the published β.
   - *V3 (D190):* `cloud_extinction_v` 2.9696 mag — 3/2 of a uniform sphere's mean column at Heyer et al.'s
     42 M☉ pc⁻² over 1.4 m_H, 1.086 × Draine's C_ext(V)/H — recomputed; the region regime's `LEVEL_KPC` (4, 1,
     0.25, 0.0625) and the 256-object budget (display choices, to be labelled); `region.ts`'s value noise (four
     octaves, weights 1/2^k, `FIELD_SIGMA` measured 0.2088), σ_s² = ln(1 + b²ℳ²) with Federrath's b (read at S32),
     the e^σ_s pillar rule and the 0.05 tilt clamp (#110, `[inferred]`).
   - *V4 (D191) and P6 (D192):* `cluster_luminosity` as mass × `population_at`'s light per mass — the identity
     the test asserts, not a source; `/api/blackbody`'s 193 temperatures 1000–100 000 K, the log-share
     interpolation and the 2.2 × 10⁻³ bound; Planck's law's constants where the share table is computed; the
     white point 6500 K (display, `FieldVolume`); the exposure rule on bolometric L (display, ruled).
   - *S42 (D192):* the FSPS grid at commit `bd187a0d07dac17b55c4dc7c60d83f63694c1b4e` — `nebular/ZAU_ND_prsc.lines`'s
     axes (11 log Z −1.98…+0.2, 10 ages 0.5–20 Myr, 7 log U −4…−1), the file order and the "Lsun/Q" unit read in
     `sps_setup.f90`, the interpolation in `add_nebular.f90`, the six lines' wavelengths and identities as the file
     labels them; **what the grid's log Z axis means** (Z/Z☉ on which solar scale, from FSPS's own `zlegend` and
     Byler et al. 2017 §2, arXiv:1611.08305) against the model's log(Z/Z☉) = 12 + log(O/H) − 8.69 (Asplund's
     8.69) — the one place a solar-scale mismatch would move every region's read point; the grid's abundance
     pattern (Dopita et al. 2000's N/O on Anders & Grevesse, #118) and n_H = 100 cm⁻³; `LINE_WAVELENGTHS` in air
     against the NIST values; the Case B decrement 2.863 (Storey & Hummer, re-read at S37) as the Hβ layers use
     it; the SVO WFC3/UVIS2 VOTables (F814W, F555W, F438W; F673N, F656N, F502N) — system throughput, the pivot
     wavelengths, the 241-point resample's 1.07 % error — and **the air-or-vacuum convention read from STScI's own
     WFC3 throughput tables** (the source SVO cites; #120); the Airy sprite's J1 from its integral definition and
     the Rayleigh zero at 1.2197π (a mathematical fact, to be checked, not sourced); `MAX_URL` 4096 and the POST
     path's refusals (411, 413 past 1 MiB, 415) against RFC 9110's semantics and **the Azure Container Apps ingress's
     request-line and header limits read from Microsoft's documentation** (D192 left that check to the deployment).
   A DIFFERS is a finding; an adopted or inferred value presented as measured is A-14's class; a display choice is
   labelled and not judged.
2. **Every gate, balance and redistribution the renderer asserted re-derived at a mesh the build did not use**, in
   `tests/test_audit_iv.py` (the one test file the audit adds), beside the default mesh's number: the V1 gate (the
   frame's B − V and M_V against the light stage's scalars *at that mesh*, and all eight bands); the V2 balance
   (absorbed share ring by ring against `dust_absorbed_surface_brightness`, emitted over absorbed, light
   conservation per filter, the face-on Σ_V(R) profile against the ring mean with its derived per-ring tolerance);
   the two Hα layers summing to the published nebular Hα ring by ring, and since S42 the line components
   (`lines_hii`, `lines_dig`) against the per-ring `*_surface_brightness_hii` and the Hβ layers; V3's catalogue
   against field (the clusters' HII Hα over the field's HII Hα at level 0 and over a level-1 sector, against the
   census's second moment √⟨L²⟩/⟨L⟩ at that mesh) and a census identical at levels 0–3 over a cell whose sample
   differs; **the render's own redistribution across levels** — a level-k window's `stars`, `halpha_hii` and
   `lines_hii` summed over its cells against the level-0 cells that hold it (a property the build did not name as
   a gate); V4's `cluster_luminosity` identity and the bolometric-over-filter ratio (the 2.12 pinned at the coarse
   grid) at the new mesh; `/api/blackbody`'s table against the integral. **The mesh:** Audit III's `GridSpec(n_R=180,
   n_t=600, n_z=8)` has been in the suite since S37 (`tests/test_audit_iii.py`), so the renderer's builders could
   have seen it; the audit therefore uses a third mesh, chosen when the grid's constraints are read (§2 says which
   and why), and reports Audit III's mesh beside it where a number is cheap. "What would have to be true for them
   to differ" is stated per row.
3. **Every green the renderer and S42 added, conditioned** (AUDIT_RUN2 §5): what makes it green, and does it survive
   the alternative named beside it. The renderer's greens are its gates rather than acceptance rows — the V1
   tolerance of 10⁻³ mag (4 × the two measured costs; does the gate survive the plain point-anchored SED, recorded
   at 0.077 mag, and the first cut's blackbody, 0.71 mag?), the V2 balance's 10⁻³ (the TIR box's coverage; does it
   survive a box to 3 mm, or β at Planck's ±0.10?), the profile's derived tolerance (does the disc-edge ring's
   −1.1 % survive a finer azimuthal sampling?), V3's |z̄| < 0.5 over sixty windows (does it survive a different
   tiling, or the level-2 forty?) — **and acceptance row 34**, green since S42 on McKee & Williams' [1.3, 3.9] ×
   10⁵³ at 1.6527 × 10⁵³: green on a factor-three window; does it survive Bennett's [1.7, 5.3] (no, by 3 %, D192),
   and does it survive the ionizing budget corrected by #84/#100's 0.71 (Q / 0.71 = 2.33 × 10⁵³)? Rows 29, 30, 31
   and 35 were conditioned at S37 and are not redone; if the numbers moved since (row 31's 0.653 per century) the
   S37 conditioning is re-read against the current pin.
4. **The forbidden-line row set blind** (#117). The model's four ratios over Hα were printed at S42 before any target
   was read (Hα-weighted and per ring), so no target for them can be chosen clean by anyone who has seen the
   repository. A reading agent **forbidden the repository and given no number from the model** sets a Milky Way
   HII-region line-ratio target — [N II] 6583/Hα, [S II] (6716 + 6731)/Hα or [O III] 5007/Hα (or over Hβ, with the
   decrement it assumes stated), against galactocentric radius over ~3–15 kpc — as a value at a stated radius with
   a width, a gradient with a width, or both, from primary literature, every number labelled READ / READ second-hand
   / NOT READ as Audit III's blind reader did (`AUDIT_III_BLIND.md`). Its report is saved verbatim as
   `docs/AUDIT_IV_BLIND.md` so a row can cite it; **the row itself is the next session's** (B3), entered blind against
   this window with the disclosure written. The same reader also sets, blind, **the diffuse ionized gas's
   [N II]/Hα and [S II]/Hα** (#119: the model publishes none, so the reading is clean by construction and is what
   #119's closer would enter as two sourced scalars) — labelled as a second target, not the row.
5. **The register's items #107–#120 re-stated in one line each**: still-open / closable-now / wrongly-described,
   with the sentence that decides it; #98 and #100 re-read where S42's re-scoping touched them.
6. **What the audit's own judgement adds** (each a reading or a probe, none a change): #118's grid edge — the
   share of the default census clamped at +0.2 dex (26.4 %) against what FSPS's extrapolation would give at one
   ring (the size of the stated choice, not a ruling on it), and whether the grid's log Z axis and the model's
   solar scale agree (item 1); #120's air-or-vacuum question decided from STScI's tables (item 1) and, if the
   curves are vacuum, the shift's size on each line's share against the tool's recorded both-ways numbers; the
   POST path against the ingress limit as documented (item 1) and against the server's own refusals re-run
   through the real transport; the render route's cold cost after S42 (+0.4 s, "not investigated further", D192)
   measured once more so the record says where it went; the V4 inventory (30 drawn / 37 not) counted from the
   declarations in both models rather than read from the test.

Sources are to be read from primary text wherever it exists (arXiv LaTeX, SVO's VOTables and pages, STScI's
throughput tables, FSPS on GitHub at the pinned commit, Draine's table file, Microsoft's Container Apps
documentation, RFC 9110) and never from recall; section and equation numbers counted where an about line or a
docstring cites one. The agents' reports are quoted below as they were written; the verdicts are theirs, the
findings (§6) are the session's. The two readers' briefs are the session's scratchpad's
`audit4_brief_reread.md` and `audit4_brief_blind.md`, written after this section and after the files were opened,
and are quoted in §1 and §4 with their reports.

**How it read.** The two briefs were written after §0 and after the files were opened (`scratchpad/audit4_brief_reread.md`,
`audit4_brief_blind.md`); the re-reader's report is §1 verbatim, the blind reader's is `docs/AUDIT_IV_BLIND.md` verbatim
and summarised in §4. The re-derivations are `tests/test_audit_iv.py` (§2), the greens `scratchpad/audit4_greens.py`
(§3), the grid's offset `scratchpad/audit4_offset.py` (§6). Before any finding was written the session read the five
load-bearing sources itself (B9): Zhao et al. 2026's abstract page and HTML (Eqs. 5, 8, 9.1, 9.2 as the blind reader
quotes them, R☉ = 8.15 kpc, 243 regions with distances), FSPS `add_nebular.f90` at the pinned commit (`dz = MAX(MIN(dz,1.0),0.0)
!no extrapolation`, and the same for `du`, `da`), Byler et al. 2017 §2 (Dopita et al. 2000 on Anders & Grevesse 1989;
the oxygen row "−3.07 / −0.22"; R_in = 10¹⁹ cm, n_H = 100), Draine's table (the `3.98107E+02` and `3.80189E+02` rows as
the re-reader gives them) and the WFC3 Instrument Handbook §6.5 (measured in air, converted to vacuum by Morton 1991;
F502N 5009.6, F656N 6561.4, F673N 6765.9). Every quotation below that the session relies on was seen at the source.

## 1. The sources re-read (the re-reader's report, verbatim)

Read-only, on `session-43` (files read in the checkout; nothing in the repository created, edited or deleted). Every source below was fetched this session into the scratchpad (`audit4_reread_src/`, outside the tree); arXiv sources were read from their LaTeX e-prints, SVO from its VOTables (`fps.php?ID=…`) and HTML pages, FSPS from `raw.githubusercontent.com` at commit `bd187a0d07dac17b55c4dc7c60d83f63694c1b4e`, Draine's table from Princeton, RFC 9110 from rfc-editor.org, the WFC3 Instrument Handbook from hst-docs.stsci.edu, NIST ASD/CODATA from physics.nist.gov, Azure from learn.microsoft.com, Envoy from its `http_connection_manager.proto`. Provenance labels: **READ** (primary text/file this session), **READ 2nd** (quoted on a service page or in another paper), **DERIVED** (my arithmetic from READ numbers, shown), **RECALL** (none used for a verdict). Probe scripts and downloads: `scratchpad/audit4_reread_fetch.sh`, `audit4_reread_probe1.py`, `audit4_reread_src/`.

Verdict scheme as Audit III's (D186): MATCH / DIFFERS / ADOPTED-NOT-MEASURED / MISATTRIBUTED / UNREACHABLE.

---

### A. V1 (S38, D188) — the stellar SED and the band definitions

| item | code value | source value and the sentence/row read | location | verdict |
|---|---|---|---|---|
| 1. `PASSBANDS` U | 3584.78 / 652.84 / 3.96526e-9 | VOTable PARAMs: `WavelengthRef=3584.7769658367`, `WavelengthPivot=3584.7769658367`, `FWHM=652.83840427838`, `ZeroPoint=1699.7104727667` unit Jy, `MagSys=Vega`, `ZeroPointType=Pogson`, `PhotCalID=Generic/Bessell.U/Vega`. SVO's own DESCRIPTION of WavelengthRef: "Reference wavelength. Defined as the same than the pivot wavelength." ZP(Jy)·c/λ_ref² = 1699.71e-23·2.99792458e18/3584.777² = 3.965257e-9 (DERIVED); code 3.96526e-9. (READ) | `https://svo2.cab.inta-csic.es/theory/fps/fps.php?ID=Generic/Bessell.U` | MATCH |
| 1. B | 4371.07 / 947.62 / 6.13268e-9 | Ref = Pivot = 4371.0712428546; FWHM 947.6162982514; ZP 3908.4589846433 Jy → 6.132683e-9 (DERIVED) | `…ID=Generic/Bessell.B` | MATCH |
| 1. V | 5477.70 / 852.44 / 3.62708e-9 | Ref = Pivot = 5477.6973781164; FWHM 852.44324740285; ZP 3630.2172842325 Jy → 3.627081e-9; the HTML page prints "ZP λ … 3.62708e-9" verbatim. (SVO's Description for V reads "Bessell B generic filter" — SVO's own slip.) | `…ID=Generic/Bessell.V`; `index.php?id=Generic/Bessell.V` | MATCH |
| 1. R | 6498.09 / 1567.06 / 2.17037e-9 | Ref = Pivot = 6498.0882122268; FWHM 1567.0588235294; ZP 3056.9282531388 Jy → 2.170375e-9 | `…ID=Generic/Bessell.R` | MATCH |
| 1. I | 8020.14 / 1543.11 / 1.12588e-9 | Ref = Pivot = 8020.1418547799; FWHM 1543.1148202988; ZP 2415.6497711876 Jy → 1.125876e-9 | `…ID=Generic/Bessell.I` | MATCH |
| 1. J | 12303.17 / 2065.62 / 3.12398e-10 | Ref = Pivot = 12303.168996055; FWHM 2065.625; ZP 1577.3242074215 Jy → 3.123976e-10. `ProfileReference=https://ui.adsabs.harvard.edu/abs/1988PASP..100.1134B`, Description "Bessell & Brett 1988 J filter", **Comments "includes ~1.2 KPNO atmosphere."**, `components=Filter + Atmosphere` | `…ID=Generic/Bessell_JHKLM.J` | MATCH (note: curve includes atmosphere) |
| 1. H | 16396.38 / 2983.81 / 1.13166e-10 | Ref = Pivot = 16396.382856007; FWHM 2983.8095238095; ZP 1014.8280770305 Jy → 1.131663e-10; same atmosphere comment | `…ID=Generic/Bessell_JHKLM.H` | MATCH |
| 1. K | 22027.46 / 3959.11 / 3.93276e-11 | Ref = Pivot = 22027.455542741; FWHM 3959.1111111111; ZP 636.5104728577 Jy → 3.932761e-11; same atmosphere comment | `…ID=Generic/Bessell_JHKLM.K` | MATCH |
| 1. `filters.json` "rgb" R/V/B and "ir" K/H/J | 6498.09/1567.06, 5477.7/852.44, 4371.07/947.62; 22027.46/3959.11, 16396.38/2983.81, 12303.17/2065.62 | same PARAMs as above | same | MATCH |
| **Field answer for item 1** | "λ_ref, the pivot" | SVO's λ_ref **is** its pivot by definition (all 8 filters: WavelengthRef == WavelengthPivot to 13 digits; DESCRIPTION quoted above); λ_eff (Vega-weighted) and λ_mean differ (V: eff 5445.43, mean 5512.10). Zero-point system: **Vega, Pogson, ZeroPoint in Jy**; the code's erg/cm²/s/Å values are ZP(Jy)·c/λ_ref² (all 8 agree to ≤4e-6 relative, DERIVED), and the page's "ZP λ" column prints the same numbers. SVO's Vega spectrum: "the system uses the alpha_lyr_stis_010.fits spectrum from the CALSPEC database" (Rodrigo et al. 2024, arXiv:2406.03310 LaTeX line 980, READ); pivot definition λ_piv = √(∫λT dλ / ∫T dλ/λ²), "This is the reference wavelength for the FPS" (same, lines 984–990). | | |
| 2. Which curves CMD/YBC's UBVRIJHK are on (`[inferred]`: "U B V R I as SVO's Generic/Bessell (Bessell 1990), J H K as Bessell_JHKLM") | | CMD's photometric-systems page (reachable now over http): row "UBVRIJHK · ubvrijhk · UBV(RI)cJHK · 3642AA-2.15mum · Vega · Maiz-Apellaniz (2006), Bessell (1990), Bessell & Brett (1988) · **combination of previous 2 systems**", the two being "Johnson · ubv · UBV · Maiz-Apellaniz (2006) · zeropoints from Maiz-Apellaniz (2006)" and "Bessell & Brett · bessell · UxBxBV(RI)cJHKLL'M · Bessell (1990), Bessell & Brett (1988)" (READ). So CMD's **U, B, V are Maíz Apellániz 2006's recalibrated Johnson curves, not Bessell 1990's**; (RI)c are Bessell 1990; JHK Bessell & Brett 1988. CMD's form lists the system as "UBVRIJHK (cf. Maiz-Apellaniz 2006 + Bessell 1990)" (READ, `http://stev.oapd.inaf.it/cgi-bin/cmd`). YBC's Vega: "we use the latest Vega spectrum … Currently it is alpha_lyr_stis_008.fits from ftp://ftp.stsci.edu/cdbs/current_calspec/ … CALSPEC database (Bohlin 2014)" (Chen et al. 2019, arXiv:1910.09037 LaTeX lines 337–343, READ); SVO uses alpha_lyr_stis_010.fits (item 1) — **two different Vega spectra**, so the per-band zero-point term the code names `[inferred]` is real. SVO's Generic/Bessell.U–I VOTables carry **no ProfileReference** (only "Bessell U generic filter"); the "(Bessell 1990)" attribution is the code's. | `http://stev.oapd.inaf.it/cmd_3.9/photsys.html`; `http://stev.oapd.inaf.it/cgi-bin/cmd`; arXiv:1910.09037 (Chen+19); arXiv:2406.03310 (Rodrigo+24) | **DIFFERS** (U B V); R I J H K MATCH in attribution |
| 3. SED join and tails | power-law join, blackbody tails | `spectra.py` line 22–24: "[inferred: the join and the tails are stated choices, not a model atmosphere]"; `band_consistent` docstring names its 12 passes "A1: a step count fixed in advance". Disclosed. | `spectra.py` 18–29, 300–306 | ADOPTED (disclosed) |
| 3. `_C2` = h c / k ×1e8 | PLANCK 6.62607015e-27 erg s, BOLTZMANN 1.380649e-16 erg/K, LIGHT_SPEED 2.99792458e10 cm/s | NIST CODATA pages: h "6.626 070 15 × 10⁻³⁴ J Hz⁻¹ … (exact)"; k "1.380 649 × 10⁻²³ J K⁻¹ … (exact)"; c "299 792 458 m s⁻¹ … (exact)" (READ). _C2 = 1.43877688e8 Å K (DERIVED). | `physics.nist.gov/cgi-bin/cuu/Value?h`, `?k`, `?c`; `massive_stars.py` 52–54 | MATCH |
| 4. `LINE_WAVELENGTHS` (air, `[recall]`) | Hα 6562.8, Hβ 4861.3, [O III] 5006.8, [S II] 6716.4 / 6730.8, [N II] 6583.5 | NIST ASD (standard air, Å, READ): H I Balmer-α centre of gravity "6562.79 (obs) / 6562.819 (Ritz)" with components 6562.70970–6562.85175; Balmer-β "4861.35 / 4861.333"; O III "5006.843" (M1, 2s²2p² ³P₂–¹D₂); S II "6716.440 (obs) / 6716.431 (Ritz)" and "6730.815 / 6730.798"; N II "6583.45". Code within 0.05 Å of all six. Vacuum: FSPS `emlines_info.dat` gives 4862.7629, 5008.3137, 6564.7229, 6585.3687, 6718.3965, 6732.7805; NIST air × Morton 1991 (n = 1 + 2.735182e-4 + 131.4182/λ² + 2.76249e8/λ⁴, READ 2nd from SDSS's vacwavelength page, the formula the WFC3 IHB also names) gives 4862.692, 5008.241, 6564.635, 6585.272, 6718.298, 6732.676 (DERIVED) — **FSPS's vacuum values sit +0.07 to +0.10 Å above air×n for all six** (ratios 1.000290–1.000294 against n−1 = 2.77–2.79e-4). The conversion does not connect them exactly; Byler §2.1.4 says "Cloudy reports air wavelengths … we convert these to vacuum … Morton (1991) … lines were matched to … NIST … set to the true vacuum value", which the file does not bear out at the 0.1 Å level. | `physics.nist.gov/cgi-bin/ASD/lines1.pl?spectra=H+I…unit=0` (and O III, S II, N II); `classic.sdss.org/dr7/products/spectra/vacwavelength.php`; FSPS `data/emlines_info.dat` | MATCH (recall → read); flag on FSPS's vacuum values |

### B. V2 (S39, D189) — the dust's three components

| item | code value | source value and the row read | location | verdict |
|---|---|---|---|---|
| 5. `GRAIN_TABLE` rows | **104 rows** (D189 and AUDIT_IV §0 say 110) | File header (READ): "1.398E-26 = M_dust per H nucleon (gram/H) for this dust model"; "1.653E+02 = M_gas/M_dust for this dust model (assuming He/H=0.096)"; "lambda = wavelength in vacuo (micron)"; 1077 data rows 1e4→1e-4 µm. Field-by-field diff of all 104 rows: **103 exact matches, 1 differs** — code row `(398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00)`; file row "3.98107E+02 0.0000 -0.0000 3.184E-26 2.277E+00"; the code's four values are the file's **380.189 µm** row ("3.80189E+02 0.0000 -0.0001 3.493E-26 2.498E+00") entered under the wrong λ. The test's identity K_abs·M_dust/H = (1−albedo)·C_ext holds for the shifted row, so it could not catch this. V row "5.47000E-01 0.6774 0.5383 4.868E-22 1.123E+04 0.53230 V filter" ✓; 2175 row "2.17500E-01 0.5046 0.5544 1.308E-21 4.633E+04 0.58365 2175 A feature" ✓; every named-row comment ✓; `GRAIN_DUST_MASS_PER_H` ✓. | `https://www.astro.princeton.edu/~draine/dust/extcurvs/kext_albedo_WD_MW_3.1_60_D03.all` | **DIFFERS** (1 of 104 rows; row count ≠ 110) |
| 6. Henyey–Greenstein form | (1−g²)/(4π(1+g²−2g cosθ)^{3/2}) | §5.1 "Fitting method": "In its single-component form, the HG phase function is defined as" eq. (3) alttext `HG(g,\theta)=\frac{1}{4\pi}\frac{1-g^{2}}{(1-2g\cos(\theta)+g^{2})^{3/2}}` (READ). Bibliography: "Henyey and Greenstein (1941) … Diffuse radiation in the Galaxy. ApJ 93, pp. 70–83" ✓. `disc_phase` "[inferred: the geometry]" disclosed. | `https://arxiv.org/html/2604.08379` §5.1 eq. 3 | MATCH; in-plane average ADOPTED (disclosed) |
| 7. Per-filter A_λ/A_V (D189: B 1.302, V 0.998, R 0.794, J 0.298, H 0.187, K 0.113; R_V mono 3.31) | | Log–log interpolation of the **full file's** C_ext/H at the PASSBANDS pivots over the V row (DERIVED): U 1.5751, B 1.3021, V 0.9982, R 0.7935, I 0.5828, J 0.2981, H 0.1867, K 0.1132 — the six numbers confirmed (the 104-row subset gives the same to 3e-4). R_V: 1/(1.3021−1) = 3.31 only with A_V ≡ 1 at the table's 5470 Å row; with both bands at their pivots A_V/(A_B−A_V) = 0.9982/0.3039 = **3.28** — a definition, stated here. Draine 2003's own table (ms.tex label `tab:model_IRoptuv`, the 4th `\begin{table}`, "Absorption and Scattering for 5µm>λ>0.1µm"; model column A_λ/A_Ic, READ): V 1.735, B 2.273, R_C 1.368, J 0.514, H 0.324, K 0.197 → A_λ/A_V = B 1.310, R_C 0.7885, J 0.2963, H 0.1867, K 0.1135 at λ_eff 0.4405/0.6492/1.22/1.63/2.19 µm ("λ_eff for JHKLL′M from BB88; Cousins UBVR_CI_C from FIG96") — the same curve read at slightly different wavelengths. | file above; arXiv:astro-ph/0304489 `ms.tex` lines 2060–2135 | MATCH (R_V 3.31 definitional) |
| 8. TIR box 8–1000 µm (`[recall]`) | 8–1000 µm | KE12 `definitions.tex` 108–113: "A commonly used definition integrates the dust emission over the wavelength range 3--1100 µm (Dale & Helou 2002), and following those authors we refer to this as the total-infrared or TIR luminosity. Note however that other definitions based on a narrower wavelength band … are often used". Dale & Helou 2002 (`ms.tex` 160–162): "the integrated 3--1000 µm infrared luminosity best reproduces model star formation rates (Mann et al. 2002) … Sanders & Mirabel (1996) have also derived a relation for the 8-1000 µm bolometric flux of luminous infrared galaxies"; "recovers the total 3-1100 µm flux (TIR)". Conventions: **TIR = 3–1100 µm** (DH02, KE12), 3–1000 µm (Mann+02), **8–1000 µm = Sanders & Mirabel's L_IR**. DH02 Table 2: the 3–5 µm band holds 0.5–3.0 % and 5–13 µm 3.4–15 % of TIR, so an 8–1000 box drops of order 2–8 % of the 3–1100 total. | arXiv:1204.3552 `definitions.tex`; arXiv:astro-ph/0205085 `ms.tex` | ADOPTED-NOT-MEASURED (disclosed as recall; the label "TIR" belongs to 3–1100 µm) |
| 9. `CLOUD_LAYER_SHARE` 0.5; sech² layers | 0.5; sech²(z/2h)/4h | clouds.py 82–84 "a stated guess with no source (debt #95) [inferred]" and the column about (line 342). Normalisation: ∫sech²(z/2h)dz = 2h[tanh(z/2h)]_{−∞}^{∞} = 4h, so ∫sech²(z/2h)/4h dz = 1 (DERIVED; numeric 1.000). | `clouds.py`, `service.py` 1124–1133 | ADOPTED (disclosed); norm MATCH |
| 10. Dust MBB constants | 16.43 cm²/g at 155.9 µm, β 1.62 | `thermal_share` calls `_dust.emission_per_mass` / `_dust.emitted_per_mass` with `kappa_ref, wavelength_ref_um, beta` passed from `model.constants[RENDER_DUST_CONSTANTS]` (service.py 1224–1228); grep of `spectra.py`/`service.py` for 16.4/155.9/1.62 finds only the grain-table row "155.900 … 1.643e01 # MIPS 3". No second copy. | `spectra.py` 552–583; `service.py` 101, 1224 | MATCH |

### C. V3 (S40, D190) and V4 (S41, D191)

| item | code value | source value and sentence | location | verdict |
|---|---|---|---|---|
| 11. `SOLAR_MASS_G` | 1.98841e33 g | IAU 2015 B3 table: "1 (GM)ᴺ☉ = 1.327 124 4 × 10²⁰ m³ s⁻²" (READ); CODATA G "6.674 30 × 10⁻¹¹ m³ kg⁻¹ s⁻²" (READ); GM/G = 1.988410e30 kg (DERIVED). (dust.py's `GRAMS_PER_MSUN = 1.98847e33` is a second value in the repository.) | arXiv:1510.07674 `main.tex` 159–161; `physics.nist.gov/cgi-bin/cuu/Value?bg` | MATCH |
| 11. `PROTON_MASS_G` | 1.67262192e-24 | NIST: "1.672 621 925 95 × 10⁻²⁷ kg" (CODATA 2022, READ); code is the value truncated to 9 digits. | `…Value?mp` | MATCH |
| 11. `CM_PER_PC_` | 3.0856775814913673e18 | au = 149 597 870 700 m (B3 endnote quoting IAU 2012 B2, READ); 648000/π × 1.495978707e13 cm = 3.0856775814913674e18 (DERIVED) | B3 `main.tex` 273–275 | MATCH |
| 11. `MAG_PER_OPTICAL_DEPTH` | 2.5/ln 10 = 1.085736 | definition | — | MATCH |
| 11. `cloud_extinction_v` 2.9696 mag | | Σ = 42 M☉ pc⁻² (Heyer+09, not redone) = 42·1.98841e33/(3.0856775814913673e18)² = 8.7711e-3 g cm⁻²; μ = `HII_MASS_PER_HYDROGEN` 1.4 ("[inferred: the composition's, not a measurement]", level0.py 1138–1143); N_H(centre) = (3/2)Σ/(μ m_H) = 5.6185e21 cm⁻²; A_V = 1.085736 × 4.868e-22 × 5.6185e21 = **2.9696** (DERIVED). The 3/2 geometry: "[inferred: the geometry]" (clouds.py 218). | `clouds.py` 197–222 | MATCH; geometry ADOPTED (disclosed) |
| 12. `region.ts` constants | LEVEL_KPC 4/1/0.25/0.0625; OCTAVES 4; OCTAVE_SIGMA 0.1794; OCTAVE_NORM √(85/64); FIELD_SIGMA 0.2088; tilt floor 0.05/cap 0.95; MAX_OBJECTS 256; BUDGET 128/64/64; L_SUN 3.828e33; CM_PER_PC | Each has its sentence: "The steps are the hierarchy's own factor, not a display choice; the anchor is REGIME_KPC.stars" (regimes.ts `REGIME_KPC = { field: 25, stars: 4 }` ✓); OCTAVE_SIGMA/FIELD_SIGMA "measured (region.test.ts)"; OCTAVE_NORM = 1.1524, ×0.1794 = 0.2067 as the comment says (DERIVED); tilt "clamped so the tilted mean stays positive [inferred: a linear tilt]"; MAX_OBJECTS/BUDGET "a display budget, stated"; L_SUN = B3's "1 Lᴺ☉ = 3.828 × 10²⁶ W" (READ) ✓; CM_PER_PC as item 11 ✓; MAG_PER_TAU "a definition". | `region.ts` 13–20, 54–93, 104–120; `regimes.ts` 189 | ADOPTED (disclosed); constants MATCH |
| 13. `psf.ts` J1, Airy, first zero | integral "(1/π)∫₀^π cos(τ − x sin τ) dτ" evaluated as the 128-point mean over the period; zero found by bisection | The trapezoid of that integrand equals J1's power series Σ(−1)^m (x/2)^{2m+1}/(m!(m+1)!) to 1e-12 at x = 0.5, 1, 3, 3.8317, 10 (DERIVED); the bisection gives 3.8317059702, /π = 1.21967 (DERIVED). Table value: MathWorld's zeros table lists j₁,₁ = **3.8317** (READ 2nd); DLMF Table 10.21.1 itself UNREACHABLE (Cloudflare challenge on `dlmf.nist.gov/10.21`, and WebFetch's excerpt omits the table). 1.22 λ/D ✓. `AIRY_FIRST_RING` "a display choice" ✓; radius ∝ pivot ✓. | `psf.ts` 50–101; `mathworld.wolfram.com/BesselFunctionZeros.html` | MATCH (table READ 2nd) |
| 14. `/api/blackbody` and `channelShare` | logspace(3,5,193); log-share linear in log T; clamp at ends; test bound | 192 intervals over 2 dex = 1/96 dex ✓. `colors.ts` 75–85: x clamped to [logK₀, logK_last]; `s = a·(b/a)^f` with f the fraction in log₁₀K — i.e. log s linear in log T, linear fallback when a row is 0; the route's sentence "log10(share) linear in log10(kelvin); a temperature off the grid takes its end's row" is what the viewer does ✓. `test_render.py` 795 asserts `< 2.5e-3` (docstring: "within 2.5e-3 … worst 2.2e-3, WFC3") — 2.2e-3 is the measured worst, 2.5e-3 the bound. White 6500 K "[inferred: near sRGB's D65 white, a display choice]" ✓. | `service.py` 105–109, 668–688; `colors.ts` 63–89 | MATCH (model's own) |

### D. S42 (D192) — the FSPS/Byler grid, the instrument curves, the POST path

| item | code value | source value and the sentence/row read | location | verdict |
|---|---|---|---|---|
| 15a. `ZAU_ND_prsc.lines` header/axes/order | header `#166`, `770`; SHAPE (11,10,7); Z outer, U inner | Header line: "#166 cols 770 rows 11 logZ 10 Age 7 logU" (READ); 166 wavelengths; coordinates a product grid, first rows (−1.98, 5e5, −4.0), (−1.98, 5e5, −3.5) … (−1.98, 1e6, −4.0): Z outermost, U innermost ✓. **Axes as read:** log Z = −1.98, −1.50, −0.98, −0.58, −0.39, −0.30, −0.20, −0.10, 0.00, 0.10, 0.20; age = 0.5, 1, 2, 3, 4, 5, 6, 7, 10, **20** Myr; log U = −4.0 … −1.0 step 0.5. Clamp ends +0.2 dex and 0.5 Myr ✓. | raw FSPS `nebular/ZAU_ND_prsc.lines` | MATCH |
| 15b. `sps_setup.f90` / `sps_vars.f90` | "Units are Lsun/Q"; 11, 10, 7, 166 | sps_setup.f90 **line 964**: "!read in nebular emission line luminosities.  Units are Lsun/Q" (line 934 for the continuum: "Units are Lsun/Hz/Q"). sps_vars.f90 line 375 `nemline=166`, line 377 `nebnz=11, nebnage=10, nebnip=7` ✓. | raw FSPS `src/` | MATCH |
| 15c. `add_nebular.f90` interpolation | "trilinear in log luminosity as FSPS does but clamped at the edges where FSPS extrapolates" (nebular.py 17–18, 128; D192 lines 6543, 6671 "Extrapolating off the grid as FSPS does") | sps_setup.f90 991–992: `nebem_age = LOG10(nebem_age)`; `nebem_line = LOG10(nebem_line + 10**(-95.d0))`. add_nebular.f90: `dz = MAX(MIN(dz,1.0),0.0) !no extrapolation`, `du = MAX(MIN(du,1.0),0.0) !no extrapolation`, `da = MAX(MIN(da,1.0),0.0) !no extrapolations`; "!interpolate logLum in Zgas, logU, age"; result `10**tmpnebline*qq`. FSPS is trilinear in log L over (log Z, log age, log U) **and clamps at the grid's edges**. The model's interpolation is FSPS's; its claim that FSPS extrapolates is not. | raw FSPS `src/add_nebular.f90`, `src/sps_setup.f90` | **DIFFERS** (the sentence about FSPS) |
| 15d. `emlines_info.dat` | six vacuum wavelengths and labels; picked by wavelength within 0.01 Å | Rows (0-based index in both files): 59 "4862.7629,Ba-beta 4861"; 62 "5008.3137,[O III] 5007"; 74 "6564.7229,Ba-alpha 6563"; 75 "6585.3687,[N II] 6584"; 77 "6718.3965,[S II] 6716"; 78 "6732.7805,[S II] 6731" — the `.lines` wavelength row has the same values at the same indices, so the tool's nearest-wavelength pick lands on those columns. (Their offset from NIST-air × Morton: item 4.) | raw FSPS `data/emlines_info.dat` | MATCH |
| 15e. **What the grid's log Z means** | model enters log(Z/Z☉) = 12+log(O/H) − 8.69 (Asplund 2009) | Byler §2.1.2 (Gas Chemical Content): "We adopt the gas phase abundances specified by Dopita et al. (2000), which are based on the solar abundances from Anders & Grevesse (1989) … Metal abundances are solar-scaled, with the exception of nitrogen … we follow the piecewise relationship between nitrogen and oxygen specified by Dopita et al. (2000)" (no formula printed). Table "Solar Metallicity (Z☉) and Depletion Factors (D) adopted for each element": "O & −3.07 & −0.22" → at grid log Z = 0 the **total** oxygen is 12+log(O/H) = **8.93** and the gas-phase (after log D = −0.22) **8.71**; "Solar abundances are from Anders & Grevesse (1989)" (READ). FSPS's `zsol = 0.01524` (sps_vars.f90, `#elif (PARSEC)`) is the isochrones' Z☉, not the nebular axis's. **Offset:** a region at 12+log(O/H) = 8.69 is read at grid log Z = 0, whose total O/H is 0.24 dex higher (or 0.02 dex higher gas-phase). The model's oxygen (from [Fe/H]+[α/Fe] on Asplund's 8.69) is a total abundance, so the relevant offset is **+0.24 dex**: every region is read 0.24 dex too metal-rich in the grid's own terms (and the clamp at +0.2 dex bites 0.24 dex earlier than it should). | arXiv:1611.08305 `main.tex` 137–166 | **DIFFERS** (0.24 dex) |
| 15f. Byler §2 physics | n_H = 100, spherical, radiation-bounded, U at the inner radius | §2.1.1: "we adopt a spherical shell cloud geometry … point source at the center … R_in, is fixed at 10¹⁹ cm (∼3 pc) and we assume a constant gas density of n_H = 100 cm⁻³"; §2.1.4 eq. (logU) "U ≡ Q_H/(4πR²·n_H·c)"; "Cloudy defines U at R = R_in … we define U as the ionization parameter calculated at the inner radius of the gas cloud … The distinction does not matter for a thin spherical shell"; §2.1.5 "The Cloudy models are radiation-bounded". Stellar populations in the paper: "Padova+Geneva" and MIST (§5.1) — **"PARSEC"/"prsc" does not occur in the paper**; the paper's grid (§2.2) is "log₁₀U₀: −4.0 … −1.0; log₁₀Z/Z☉: −2.0, −1.5, −1.0, −0.6, −0.4, −0.3, −0.2, −0.1, 0.0, 0.1, 0.2; Age: 0.5, 1, 2, 3, 4, 5, 6, 7, 10 Myr" (9 ages), which the prsc file does not reproduce (4 Z values shifted, a 20 Myr row added). The model's log U (nebular.py 274) is Q/(4πR²·√⟨n²⟩·c) at its Strömgren or cloud radius — a filled sphere's outer radius, not Byler's fixed inner face. | arXiv:1611.08305 `main.tex` 130–135, 207–247 | MATCH on n_H/geometry/bounding; U-radius convention differs (recorded for the next session) |
| 16. `HBETA_HII` / `HBETA_DIG` | | nebular.py 542: `hii * case_b_hbeta(t_gas) / case_b_halpha(t_gas)`; 534/543: `dig / decrement_dig` with the decrement at `DIG_TEMPERATURE` from the same tables. No fixed 2.863. | `nebular.py` 534–543 | MATCH |
| 17a. `instruments.json` pivots/FWHM | F814W 8029.30/1996.72; F555W 5307.90/1641.20; F438W 4325.15/669.74; F673N 6765.97/120.28; F656N 6561.53/17.87; F502N 5009.81/66.79 | SVO `WavelengthPivot`/`FWHM` (READ): 8029.3017069258/1996.7218708327; 5307.9010105998/1641.2004007899; 4325.1499682308/669.74416121529; 6765.9657342094/120.28383448445; 6561.5317949059/17.873778332138; 5009.8061127441/66.792892816792. Peaks: SVO 0.230607/0.28502/0.24258/0.24567/0.22880/0.26297 vs json's resampled 0.23051/0.28491/0.24252/0.24567/0.2288/0.26295. `ProfileReference = https://www.stsci.edu/hst/instrumentation/wfc3/performance/throughputs`; `DetectorType = 1` (photon counter); `components = Filter + CCD + Instrument`; Comments: "Using filter throughputs determined in the lab in combination with the measured QE of the flight detectors and sensitivities of WFC3's optics. These values were derived with STsynphot … photometric calibration released on October 2020 (Bajaj et al 2020, Calamida et al. 2021)" — the system throughput, as the code says. **SVO says nothing about air or vacuum** (no such word in the VOTables or the pages). | `fps.php?ID=HST/WFC3_UVIS2.F814W` … `.F502N`; `index.php?id=HST/WFC3_UVIS2.F656N` | MATCH |
| 17b. Air or vacuum (decided) | tool: "SVO does not say"; factor 1.000277 `[inferred]`; the model evaluates its **air** line wavelengths against these curves | WFC3 Instrument Handbook §6.5 (READ): "All measurements of the UVIS filters which involve wavelengths, as tabulated in Table 6.2 and plotted in Figures 6.3 through 6.10 and in Appendix A, were done in air. The data have been converted to vacuum wavelengths using the formula given by D. C. Morton (1991, ApJS 77, 119)." Table 6.2 footnote: "Filter transmissions were measured in air, but the equivalent vacuum wavelengths are reported in this table." STScI throughputs page: "NOTE: The filter transmission measurements were made in air, not vacuum." **STScI's WFC3/UVIS throughput files are on vacuum wavelengths.** IHB Table 6.2 (UVIS1) pivots, vacuum: F502N 5009.6, F656N 6561.4, F673N 6765.9 (F438W 4326.2, F555W 5308.4, F814W 8039.1); "Pivot wavelength … (see Section 9.3 and Tokunaga & Vacca 2005, PASP, 117, 421)". Morton 1991 n − 1 (formula READ 2nd): **2.792e-4 at 5000 Å, 2.767e-4 at 6600 Å** (DERIVED); the tool's 2.77e-4 is within 2e-6. What it moves (json's own `lines_air_vacuum`): F656N Hα 0.9617 → 0.9453, F673N [S II] 6716 0.9826 → 0.9577, 6731 0.8565 → 0.8632, F502N [O III] 0.9025 → 0.8987. | `hst-docs.stsci.edu/wfc3ihb/chapter-6-uvis-imaging-with-wfc3/6-5-uvis-spectral-elements`; `stsci.edu/hst/instrumentation/wfc3/performance/throughputs` | **DIFFERS in effect** (curves are vacuum; the lines are placed at air wavelengths) |
| 18a. HTTP refusals | 411 no/invalid Content-Length; 413 body > 1 MiB; 415 not form-encoded; POST body appended to the query | RFC 9110 **§15.5.12** 411: "the server refuses to accept the request without a defined Content-Length" ✓; **§15.5.14** 413: "the request content is larger than the server is willing or able to process" ✓; **§15.5.16** 415: "the content is in a format not supported by this method on the target resource … might be due to the request's indicated Content-Type" ✓; **§9.3.3** POST: "process the representation enclosed in the request according to the resource's own specific semantics … Providing a block of data, such as the fields entered into an HTML form, to a data-handling process" ✓ (the server's `no-store` also satisfies "Responses to POST requests are only cacheable when…"). (The brief's "§15.5.10" is 409 Conflict; the code cites no section numbers.) | `rfc-editor.org/rfc/rfc9110.txt` | MATCH (3/3 statuses) |
| 18b. Proxy limits | `MAX_URL` 4096 "inside every proxy's limit"; `MAX_BODY` 1 MiB; `main.bicep` ingress `external: true, targetPort 8000, transport 'auto', allowInsecure false` — no limit set | Microsoft (ingress-overview, quotas, FAQ, ingress-environment-configuration, networking — all READ): **no request-line, header-size, URL-length or body-size limit is documented**; documented are "Support for HTTP/1.1 and HTTP/2", "Request time out is 240 seconds", premium-mode "Request header count … Default 100", and (networking) "Envoy routes internal traffic inside clusters. Downstream connections support HTTP/1.1 and HTTP/2." Envoy `http_connection_manager.proto` `max_request_headers_kb`: "If unconfigured, the default max request headers allowed is 60 KiB … Requests that exceed this limit will receive a 431 response" (READ). A 4 KB request line is inside 60 KiB; a 1 MiB form body has no documented ceiling on either side (Envoy streams bodies unless a buffer filter is configured). | `learn.microsoft.com/en-us/azure/container-apps/{ingress-overview,quotas,faq,ingress-environment-configuration,networking}`; `github.com/envoyproxy/envoy …/http_connection_manager.proto` | ADOPTED (disclosed as the viewer's own bound; no Microsoft statement) |
| 19 | skipped per brief | | | — |

### E. In passing

| item | code | source | verdict |
|---|---|---|---|
| 20. README FSPS/Byler/SVO citations | "MIT License, Copyright (c) 2009-2021 Charlie Conroy & contributors; FSPS: Conroy, Gunn & White 2009, ApJ, 699, 486; Conroy & Gunn 2010, ApJ, 712, 833"; Byler 2017 "ApJ (doi:10.3847/1538-4357/aa6c66, arXiv:1611.08305)"; SVO acknowledgement + Rodrigo+24 (2024A&A...689A..93R), Rodrigo, Solano & Bayo 2012 (2012ivoa.rept.1015R), Rodrigo & Solano 2020 (2020sea..confE.182R) | FSPS README at the commit: "When using this code please cite the following papers: Conroy, Gunn, & White 2009, ApJ, 699, 486; Conroy & Gunn 2010, ApJ, 712, 833" ✓; LICENSE "The MIT License (MIT) Copyright (c) 2009-2021 Charlie Conroy & contributors." ✓. arXiv abs page for 1611.08305 carries "DOI: https://doi.org/10.3847/1538-4357/aa6c66" ✓ (the README gives no volume/page, so "ApJ 840, 44" is the brief's, not the README's). SVO front page: "This research has made use of the SVO Filter Profile Service "Carlos Rodrigo", funded by MCIN/AEI/10.13039/501100011033/ through grant PID2023-146210NB-I00" and "Rodrigo, C., Cruz, P., Aguilar, J.F., et al. 2024; …/2024A%26A...689A..93R … Rodrigo, C., Solano, E., Bayo, A., 2012; …/2012ivoa.rept.1015R … Rodrigo, C., Solano, E., 2020; …/2020sea..confE.182R" ✓ (bibcodes READ from SVO's own links; ADS abstract pages returned a "Human Verification" page — UNREACHABLE for the records themselves; the 2024 title "Photometric segregation of dwarf and giant FGK stars using the SVO Filter Profile Service and photometric tools", A&A 689, A93, READ 2nd from search). | MATCH |
| 21. RENDER_PHYSICS §10; PAH; Q(H⁰) | line 443 "the Henyey–Greenstein phase function — read at S39 (Bosschaart & Olofsson 2026, arXiv:2604.08379 eq. 3)"; 444 PAH still owed; 446 Q(H⁰) still owed | Consistent with item 6. Grep of `spectra.py`/`service.py` for PAH/3.3/6.2/7.7 hits only grain-table numerals (0.354814, 0.355000, 0.440500, 0.891251); no PAH or Q(T_eff, L) code entered S38–S42. | MATCH |

---

### Summary counts (items 1–21; item 19 skipped by the brief → 20 judged)

- **MATCH: 12** — items 1, 4, 6, 7, 10, 11, 13, 14, 16, 18, 20, 21
- **DIFFERS: 4** — items 2 (CMD's U B V curves), 5 (one grain-table row), 15 (FSPS clamps too; the grid's solar scale, +0.24 dex), 17 (the WFC3 curves are vacuum)
- **ADOPTED-NOT-MEASURED / ADOPTED (disclosed): 4** — items 3, 8, 9, 12 (8 is the one with an undisclosed alternative: TIR is 3–1100 µm)
- **MISATTRIBUTED: 0** in the code (the brief's own slips are listed below)
- **UNREACHABLE: 0 whole items**; two sub-readings fell back to second-hand: DLMF Table 10.21.1 (item 13; MathWorld's 3.8317 used) and the three ADS records (item 20; SVO's own links used)
- **Item 5's rows: 104 rows in the code (not 110): 103 MATCH, 1 DIFFERS.**
- Provenance: all verdict numbers READ or DERIVED; RECALL used for none.

### Every non-MATCH item and the sentence that decides it

1. **Item 2 — DIFFERS.** CMD's photometric-systems page: "UBVRIJHK · ubvrijhk · UBV(RI)cJHK … Maiz-Apellaniz (2006), Bessell (1990), Bessell & Brett (1988) · combination of previous 2 systems", the first being "Johnson · ubv · UBV · Maiz-Apellaniz (2006)". CMD's U B V curves are Maíz Apellániz 2006's Johnson, not SVO's Generic/Bessell (which SVO gives no profile reference for). `http://stev.oapd.inaf.it/cmd_3.9/photsys.html`. And the Vega spectra differ: YBC "alpha_lyr_stis_008.fits" (arXiv:1910.09037 l. 341) vs SVO "alpha_lyr_stis_010.fits" (arXiv:2406.03310 l. 980). Closes #107's open half as a finding, not a confirmation.
2. **Item 5 — DIFFERS (1/104 rows).** File: "3.98107E+02 0.0000 -0.0000 3.184E-26 2.277E+00 0.40000"; code: `(398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00)` = the file's "3.80189E+02" row. `https://www.astro.princeton.edu/~draine/dust/extcurvs/kext_albedo_WD_MW_3.1_60_D03.all`. Effect confined to the log–log interpolation between 251 and 631 µm (C_ext 9.7 % high at 398 µm); the optical ratios are untouched.
3. **Item 8 — ADOPTED-NOT-MEASURED.** KE12: "integrates the dust emission over the wavelength range 3--1100 µm (Dale & Helou 2002), and following those authors we refer to this as the total-infrared or TIR luminosity"; DH02: "Sanders & Mirabel (1996) have also derived a relation for the 8-1000 µm bolometric flux of luminous infrared galaxies". The box's 8–1000 µm is Sanders & Mirabel's L_IR; the name "TIR" belongs to 3–1100 µm. arXiv:1204.3552 `definitions.tex` 108–113; arXiv:astro-ph/0205085 `ms.tex` 160–162.
4. **Item 15c — DIFFERS.** `add_nebular.f90`: "dz = MAX(MIN(dz,1.0),0.0) !no extrapolation" (and du, da). FSPS clamps; nebular.py 17–18 / D192 6543 & 6671 say it extrapolates. `https://raw.githubusercontent.com/cconroy20/fsps/bd187a0d07dac17b55c4dc7c60d83f63694c1b4e/src/add_nebular.f90`.
5. **Item 15e — DIFFERS (+0.24 dex).** Byler §2.1.2: "We adopt the gas phase abundances specified by Dopita et al. (2000), which are based on the solar abundances from Anders & Grevesse (1989)"; table row "O & −3.07 & −0.22" (12+log(O/H) = 8.93 total, 8.71 gas-phase at log Z = 0). The model's 12+log(O/H) − 8.69 reads the grid 0.24 dex too rich (0.02 dex if its oxygen were gas-phase). arXiv:1611.08305 `main.tex` 139, 144–164. Also: the paper's grid is Padova+Geneva/MIST with 9 ages; the `prsc` file (11 Z values, 4 of them shifted; 10 ages to 20 Myr) is FSPS's later product, cited to a paper that does not describe it.
6. **Item 17b — DIFFERS in effect.** WFC3 IHB §6.5: "All measurements of the UVIS filters which involve wavelengths … were done in air. The data have been converted to vacuum wavelengths using the formula given by D. C. Morton (1991, ApJS 77, 119)." The curves the viewer sends are on vacuum wavelengths; the model places its lines at air wavelengths against them (Hα through F656N 0.9617 vs 0.9453 at vacuum). `https://hst-docs.stsci.edu/wfc3ihb/chapter-6-uvis-imaging-with-wfc3/6-5-uvis-spectral-elements`. Morton 1991 n − 1 = 2.792e-4 (5000 Å), 2.767e-4 (6600 Å), so the tool's 1.000277 is the right factor to within 2e-6.
7. **Items 3, 9, 12, 18b — ADOPTED (disclosed):** the join/tails "[inferred: the join and the tails are stated choices]", `CLOUD_LAYER_SHARE` "a stated guess with no source (debt #95) [inferred]", region.ts's "measured"/"display budget"/"[inferred: a linear tilt]" sentences, and `MAX_URL`'s "4 KB is inside every proxy's limit" (Microsoft documents no such limit; Envoy's default is "60 KiB … 431").

### Found in passing (not asked)

- **Row count:** `GRAIN_TABLE` holds 104 rows; D189 (DECISIONS 6230) and AUDIT_IV §0 say 110.
- **Two solar masses:** `dust.py` `GRAMS_PER_MSUN = 1.98847e33` vs `SOLAR_MASS_G = 1.98841e33` in `clouds.py`/`nebular.py` (and `massive_stars.SOLAR_MASS` = GM/G computed).
- **FSPS's vacuum line wavelengths** sit +0.07 to +0.10 Å above NIST-air × Morton 1991 for all six lines (item 4), despite Byler's "set to the true vacuum value"; harmless for a 18 Å filter, worth a line in `fetch_nebular.py`'s docstring.
- **D189's "monochromatic R_V 3.31"** is 1/(A_B/A_V − 1) with A_V ≡ 1 at 5470 Å; with both bands at their pivots it is 3.28.
- **SVO's Bessell J H K curves include an atmosphere** ("includes ~1.2 KPNO atmosphere", components "Filter + Atmosphere") — the code's "Bessell & Brett 1988 J/H/K filter" description omits it; the isochrone table's JHK are on the same Bessell & Brett system, so this is a note, not an error.
- **SVO's own slip:** Generic/Bessell.V's Description reads "Bessell B generic filter".
- **`test_render.py` 775–795:** docstring "within 2.5e-3 … (worst 2.2e-3)", assert `< 2.5e-3` — consistent; the brief's "2.2e-3 bound" is the measured worst.
- **`clouds.py` 77–80 `K_OVER_MH`** still carries "[recall: 1.380649e-23 J/K, 1.67262e-27 kg]"; both are READ now (NIST: k exact; m_p 1.672 621 925 95e-27), so the tag can be lifted (pre-S38 code, noted only).
- **The brief's own citation slips** (so the auditor does not copy them into AUDIT_IV): RFC 9110 §15.5.10 is 409 Conflict (411 is §15.5.12); arXiv:1905.04955 is an unrelated statistics e-print (YBC is Chen et al. 2019, arXiv:1910.09037, A&A 632, A105); the README does not print "ApJ 840, 44" for Byler; "110 rows".
- **Byler's U convention** for the next session's comparison: U at the fixed inner face R_in = 10¹⁹ cm of a thin shell, n_H = 100; the model's log U is at the Strömgren/cloud radius of a filled sphere with n = √⟨n²⟩ (nebular.py 274).

## 2. The gates, balances and redistributions, re-derived at a mesh the build did not use

Method: `Service(grid=GridSpec(n_R=150, n_t=500, n_z=10, n_phi=240))` — not the default (400, 2000, 60, 360), not the
tests' coarse (120, 400, 6), not test_render's small (48, 64, 8, 36) and not Audit III's (180, 600, 8), which has been in
the suite since S37 and so is a mesh the renderer's builders could have tuned against; 240 azimuths also change the ratio
of grid cells to the render's 8 × 8 sub-samples per region cell. Every identity the renderer asserted is computed again
from the routes (`tests/test_audit_iv.py`, both models where the gate is per model), beside the default mesh's number.
"What would have to be true for them to differ" is stated per row `[verified: tests/test_audit_iv.py, its printed lines]`.

| identity (decision) | default mesh | audit mesh | the cost that moves it | verdict |
|---|---|---|---|---|
| V1 gate: frame B − V − table (D188) | +8.9 × 10⁻⁵ | +1.58 × 10⁻⁴ | the cell sum against the stage's trapezoid, ∝ dR² | holds inside 10⁻³, both models; the frame at this mesh is 0.630828 against the stage's own 0.630670 |
| V1 gate: frame M_V − table | −1.7 × 10⁻⁴ | −6.57 × 10⁻⁴ | the same, 3.9× at 2.67× the ring width | holds; the worst of the eight bands is V's 6.6 × 10⁻⁴. Would differ only if the band-consistency passes depended on the ring count — they act per cell |
| V2 balance: emitted / absorbed in the frame (D189) | 0.999321 | 0.999317 | the TIR box's coverage (6.80 × 10⁻⁴ → 6.83 × 10⁻⁴ of Σ_IR beyond 1 mm) | holds to 4 × 10⁻⁶: the frame-against-frame ratio is the coverage alone, at any mesh |
| V2: absorbed / `dust_absorbed_luminosity`; emitted / `dust_infrared_luminosity` | 1.000344 / 0.999664 | 1.001345 / 1.000662 | the cell sum against the trapezoid, 3.9× (∝ dR²) | holds inside the stated 3 × 10⁻³ at 150 rings; **the 10⁻³ tolerance of test_render is a 400-ring number** for the published-total halves, and the file says so |
| V2: light conserved per filter, per ring (escaped + scattered + absorbed = the stars) | 10⁻⁹ | 10⁻⁹ | exact | identity |
| V2: the absorbed field from the V-row share, ring by ring | 10⁻⁸ | 10⁻⁸ | the direction quadrature | identity |
| V2/S42: HII + DIG layers = the nebular Hα per ring; `lines_hii` = the [S II] pair and [O III] placed by the contrast; `absent.lines` empty | exact | exact | — | identity |
| S42: each ring's [N II]/Hα in the field = the census's Hα-weighted ratio there (`nebular.ring_ratios` recomputed from `/api/clusters` over the whole disc) | — | 10⁻⁹ | the census read whole: a window that cuts the disc at 20 kpc moves the outer rings' interpolated values (found while writing the test) | identity |
| V3: the clusters' HII Hα / the field's, the disc at level 0 (D190) | 0.9801 (12 597 clusters, √⟨L²⟩/⟨L⟩ 6.898) | **0.9486** (12 675 clusters, 6.700) | the census's own second moment: σ(N) = 6.70/√12 675 = 0.0595, z = **−0.86** | holds; a different realisation at a different mesh, inside 1σ. Would differ if the regions' Hα were not the clusters' Q through the same Case B |
| V3: the same, r 4–12 kpc, φ 0–2 at level 1 | 0.9744 (2 499) | 0.9932 (2 484), z −0.05 | σ(N) 0.134 | holds |
| V3: a census identical at levels 0–3 over cell 300 (clouds, clusters) | holds | holds (a different sample) | exact | identity |
| **the render across levels** (not a gate the build named): a window of level-0 cells (rings 6–9, sectors 0–5) summed at levels 0, 1, 2 — stars, `halpha_hii`, `lines_hii`, `halpha_dig` | — | ≤ 6.3 × 10⁻⁵ (stars), ≤ 4.6 × 10⁻⁴ (`lines_hii`, level 2) | the 8 × 8 midpoint rule's own error (the children are a finer rule on the same bilinear integrand) | holds at 2 × 10⁻³; **a window that is not cell-aligned differs by its area** (a level-0 sector reaches 1.374 rad where the window says 1.2; found while writing the test: the test's first form compared 7.6 % more area, not more light) |
| V4: `cluster_luminosity` = mass × the light per mass at (age, [Fe/H]) (D191) | 10⁻¹² | 10⁻¹² | exact | identity |
| V4/P6: the ramp's painting over the population's light through rgb, R / G / B (D191, #114) | 1.89 / 2.12 / 2.43 (coarse) | 1.886 / 2.110 / 2.421 (12 940 clusters) | the census's age–metallicity mix | holds: the 2.1× is the mix's, not the mesh's |
| V4: the clusters' share of the disc's bolometric light | 0.249 (default), 0.236 (coarse) | 0.242 | the census | holds |

No gate moved outside the cost the mesh sets. Two things the mesh taught: the V1 and V2 tolerances that compare the
frame to a *published total* carry a dR² term (1.7 × 10⁻⁴ and 3.4 × 10⁻⁴ at 400 rings, 6.6 × 10⁻⁴ and 1.3 × 10⁻³ at 150) and
would fail their fixed 10⁻³ below about 170 rings — stated, not a defect, since the default mesh is the viewer's; and the
frame-against-frame identities (emitted over absorbed, the layers, the levels) are mesh-free.

## 3. The renderer's greens and row 34, conditioned (AUDIT_RUN2 §5)

Read on the default grid, `scratchpad/audit4_greens.py` (its log quoted) `[verified: scratchpad/audit4_greens.log, 2026-09-30]`.

| green | green on | the alternative beside it | survives? | verdict |
|---|---|---|---|---|
| V1 gate, 10⁻³ mag (D188) | the twelve band-consistency passes: B − V +8.9 × 10⁻⁵, M_V −1.7 × 10⁻⁴ | the plain point-anchored SED (0 passes): **B − V +0.0595, M_V +0.0171**; 4 passes: +0.0051, −0.0022 | **no** at 0 or 4 passes; the gate is met *because* the passes drive each band's mean to the table's value | green by construction — the passes are A1's fixed iteration toward the very numbers the gate reads; what the gate then measures is the cell quadrature and the ring interpolation, and it says nothing about the spectrum between the bands (#107: 0.708 of the bolometric light through a box) |
| V2 balance, 10⁻³ (D189) | the TIR box's coverage 6.80 × 10⁻⁴ at β 1.62 | β at Planck's ±0.10: coverage 0.999162 (1.52) / 0.999450 (1.72), i.e. 8.4 × 10⁻⁴ / 5.5 × 10⁻⁴ outside; a 3–1000 µm box: identical to 5 × 10⁻⁷ | yes | green because the two sides are the same function of the same fields (B3's "two computations" is the direction quadrature against the stage's E₃, which holds to 2 × 10⁻¹¹); the box's short edge (8 vs 3 µm) is worth nothing for 15–21 K dust; the label "TIR" is the wrong name for 8–1000 µm (§1 item 8) |
| V2 profile, per-ring derived tolerance (D189) | every ring inside a bound built from the profile's own kinks and the contrast's sampling; worst 9.2 × 10⁻⁴ | no alternative tolerance exists to test — the bound is derived, the one green of the renderer that conditions itself | — | recorded; at the audit mesh the profile test is not repeated (its bound derivation is the default mesh's), the cell means across levels (§2) cover its mechanism |
| V3 sixty windows, \|z̄\| < 0.5 (D190) | 2 kpc × 15 sectors: z̄ +0.153, sd 1.159, 90 % inside 2σ | 1.6 kpc × 12 sectors (60 windows, N 94–417): **z̄ +0.096, sd 0.903, 97 % inside 2σ, 100 % inside 3σ**, ratio mean 1.062, median 0.948; the suite's tiling rotated half a sector (56 windows): z̄ +0.239, sd 1.119, 93 % / 95 % | yes, both | green by the census's second moment, as ruled; the sd runs 0.90–1.16 across tilings, so D190's "one galaxy-wide moment slightly understates the scatter" is itself a tiling effect of ±0.13 — the bound 0.7–1.5 holds either way |
| **row 34**, Q(H⁰) 1.6527 × 10⁵³ in McKee & Williams' [1.3, 3.9] × 10⁵³ (D192) | a factor-three window the disc's whole history lands in | Bennett's [1.7, 5.3] × 10⁵³: misses by 3 % (D192); **the ionizing budget corrected by #84/#100's 0.7095: Q / 0.7095 = 2.329 × 10⁵³**, inside McKee & Williams' *and* inside Bennett's | yes — and the alternative *strengthens* it | green on the blind window; the one number that could move it (the isochrones' Q against Starburst99's) moves it toward the centre of both windows, so the row is not a knife-edge either way; what it does not test is the young light (D192's conditioning stands) |

Two of the four renderer greens are met by construction (V1's passes, V2's shared function), one is self-bounding
(the profile), one is a population statistic that survives a re-tiling (V3); row 34 survives its named alternative.

## 4. The forbidden-line target, read blind (#117), and the diffuse gas's ratios (#119)

The reader was forbidden the repository and given no model number (`scratchpad/audit4_brief_blind.md`); its report is
`docs/AUDIT_IV_BLIND.md` verbatim. It set, before any comparison:

- **Target A (the row).** d log([N II] 6583/Hα)/dR of the model's Hα-weighted ring means, **rings between 8.2 and 15.4 kpc
  only**, = **−0.025 dex kpc⁻¹, 1σ ±0.009, acceptance window [−0.045, −0.005] dex kpc⁻¹** (a stated ~2σ, because the
  source fits binned medians and its two-zone fit gives −0.028 ± 0.009 outside 9.65 kpc and −0.077 ± 0.018 inside), from
  Zhao et al. 2026, AJ 172, 168, arXiv:2607.27662 (LAMOST MRS-N; 255 confirmed Galactic HII regions, 243 with distances,
  whole-region stacked spectra, R☉ 8.15 kpc): their Eq. 8 "12+log(O/H) = 8.763(±0.046) − 0.014(±0.005) R_gal" over
  8.16–15.36 kpc divided by Eq. 5's "8.90 + 0.57 × log([N II]/Hα)" (the PP04 N2 calibration, linear in the ratio, so the
  O/H slope *is* the ratio's slope over 0.57) `[verified: arxiv.org/html/2607.27662 Eqs. 5, 8, 9.1, 9.2, read by the session
  on 2026-09-30 after the blind report]`. Secondary check, not the row: [N II]/Hα at R₀ = **0.27, window 0.20–0.40** (Madsen,
  Reynolds & Haffner 2006's O-star HII-region average, whole regions in WHAM's beam; the row-level spread flagged
  rendering-uncertain by the reader). The reader's **direction note**: the ratio should fall outward slowly, about a third
  of the N/H gradient, because T_e rises at +345–359 K kpc⁻¹ and nearly cancels the abundance fall; "a model whose
  [N II]/Hα follows N/H (≈ −0.06 to −0.08 dex kpc⁻¹) fails".
- **Target B (a reading, not a row).** The WIM's [N II] 6583/Hα ≈ **0.5 (0.3–1.0)** and [S II] 6716/Hα ≈ **0.3–0.5**
  (doublet ≈ ×1.7), ≈ ×2 and ≈ ×3–4 the classical HII regions' 0.27 and 0.11, rising as I_Hα falls and |z| rises; in the
  plane (|z| < 0.3 kpc) the DIG reads 0.33 and 0.38 (doublet), ×1.1 and ×1.9; the WIM ≈ 2000 K hotter than HII regions;
  [N II]/Hα(T) = 1.62 × 10⁵ T₄^0.4 e^(−2.18/T₄)(N⁺/N)(N/H) (Madsen 2006 Eq. 2) — 0.37 at 7000 K, 0.58 at 8000 K, 0.83 at
  9000 K for N⁺/N 0.8, N/H 7.5 × 10⁻⁵; [S II]/[N II] set by S⁺/S (0.3–0.7 WIM, 0.25 HII), not by T. READ from Madsen
  2006, Haffner 1999, Haffner 2009 and Wen et al. 2024 as labelled in the report.

**What the session then measured, after the window was set** (`scratchpad/audit4_offset.py`, the default census; B3: no
row is entered here): the model's Hα-weighted ring means give **d log([N II]/Hα)/dR = −0.0815 dex kpc⁻¹ over 8.2–15.4
kpc** and **[N II]/Hα = 0.205 at 8.2 kpc**. Against the blind window the gradient **misses by 4σ in the reader's
"killing direction"** — the model's ratio falls at the N/H gradient's pace, three times the measured slope — while the
value at R₀ sits inside 0.20–0.40 at its lower edge. Read on the grid's own solar scale (A4-1, oxygen − 8.93) the ring
means move (0.151 / 0.0905 / 0.046 at 4 / 8 / 12 kpc against 0.200 / 0.166 / 0.097 as built) but the slope over 8–12
kpc is still ≈ −0.07 dex kpc⁻¹: the miss is not the offset's. It is the chemistry's or the grid's temperature run with
Z, and the next session enters the row as it stands — **blind window, disclosed that the audit computed the statistic
once the window existed** — and records the miss with #117's prediction (a miss in direction is the chemistry's).

## 5. The register's renderer items, re-stated

One line each: still-open / closable-now / wrongly-described, with the sentence that decides it.

| # | one line | state |
|---|---|---|
| 107 | the SED's joins and tails are stated choices; 0.708 of L_bol through a box; the CMD/YBC curves and Vega `[inferred]` | still open; **its inferred half is now a finding (A4-5)**: CMD's U B V are Maíz Apellániz 2006's Johnson curves, YBC's Vega is `alpha_lyr_stis_008`, SVO's `stis_010` — re-described, not closable by reading |
| 109 | the dust in the stars' layer; the ir set measured not drawn; the slab's phase table inferred | still open; §1 item 8 adds that the ir set's "TIR" box is Sanders & Mirabel's 8–1000 µm L_IR, not Dale & Helou's 3–1100 µm TIR (worth 5 × 10⁻⁷ of Σ_IR here; the name is the record's) |
| 110 | the noise's octaves, tilt and pillar rule are shapes the vector does not constrain | still open as described (§1 item 12: every constant carries its sentence) |
| 111 | the display budget drops light the field gave up | still open as described |
| 112 | the screen-space composite darkens a star in front of a cloud | still open as described |
| 113 | the stars stay on the level-0 sample; no test sums the sample's light against the render | still open; §2's level test now covers the *render's* side of that sum (a window's light is the same at levels 0–2), the sample's side is still owed |
| 114 | a point is painted bolometric through a blackbody's share | still open; §2 re-measures 1.886 / 2.110 / 2.421 at the audit mesh — the mix's, not the mesh's |
| 115 | the young population twice; a dissolved cluster a point | still open as described |
| 116 | the cluster's extent undrawn | still open as described |
| 117 | the forbidden lines have no row; the numbers known | **closable now, as a miss**: the blind window exists (§4, [−0.045, −0.005] dex kpc⁻¹) and the model reads −0.0815; the next session enters row 37 blind-with-disclosure and records the miss |
| 118 | a quarter of the regions read the grid's edge, clamped; the grid's gas is not the region's | **wrongly described in two places**: (i) "FSPS extrapolates" — it clamps (`add_nebular.f90`, A4-2), so the model's reading *is* FSPS's; (ii) the edge bites because the model enters oxygen − 8.69 on a grid whose log Z = 0 is 8.93 (A4-1): on the grid's scale 3.0 % of regions are clamped, not 26.4 %. The gas-pattern half (N/O, S/O, n_H = 100) stands; add Byler's U at a fixed inner face against the model's at the Strömgren radius |
| 119 | the diffuse gas carries only its recombination lines | still open; **its closer's numbers are now read** (§4 Target B: WIM 0.5 and 0.3–0.5 ×1.7; in-plane 0.33 / 0.38) — the ruling is which layer the model's 1.4 kpc DIG is (the WIM proper) |
| 120 | the sprite is display; SVO's air-or-vacuum unstated | **half decided (A4-4)**: STScI's curves are vacuum (IHB §6.5), the model places air lines on them — Hα in F656N 0.962 → 0.945, [S II] 6716 in F673N 0.983 → 0.958, 6731 0.857 → 0.863, [O III] 0.903 → 0.899; the fix is one convention flag or a shifted curve; the sprite half stands |
| 98 / 100 | (re-read where S42 touched them) row 32's miss on the blind window; the 0.71 | unchanged; §3 shows the 0.71 moves row 34 toward the centre of both windows |

Counts: 14 items; 9 still open as described; 1 closable now (#117, as a miss); 2 wrongly or incompletely described
(#118 twice; #120 half decided); 2 re-described with new readings (#107, #119). No item is discharged here (B3).

## 6. Findings, numbered for D194 and the register

Each names the decision it needs. None is applied here (B3).

- **A4-1 (defect, changes model output). The nebular grid is read 0.24 dex too metal-rich.** Byler et al. 2017 §2.1.2: "We
  adopt the gas phase abundances specified by Dopita et al. (2000), which are based on the solar abundances from Anders &
  Grevesse (1989)"; their table gives oxygen −3.07 (12+log(O/H) = 8.93) with depletion −0.22 (8.71 gas-phase) at log Z = 0
  `[verified: arXiv:1611.08305 §2.1.2 and Table 1, read at S43]`. `nebular.py` enters log Z = 12+log(O/H) − 8.69 (Asplund),
  so a region at Asplund's solar oxygen is read at the grid point whose total oxygen is 0.24 dex higher. Measured on the
  default census (`audit4_offset.py`): on the grid's own scale **3.0 % of regions are clamped at +0.2 dex, not 26.4 %**;
  the Hα-weighted [O III]/Hα reads 0.75 (was 0.48), [N II]/Hα 0.082 (was 0.131), the [S II] pair unchanged (0.053 / 0.041);
  per ring [N II]/Hα 0.151 / 0.091 / 0.046 at 4 / 8 / 12 kpc. *Decision (the next session's, with a ruling):* which oxygen
  the grid's axis is entered on — the total 8.93 (the model's oxygen is a total abundance) or the gas-phase 8.71 (what the
  ionized gas has) — then `test_nebular`'s pins move with it and #118's clamp sentence is rewritten. Registered as **#121**.
- **A4-2 (record, and one sentence of D192 wrong). FSPS clamps at the grid's edges; it does not extrapolate.**
  `add_nebular.f90` at the pinned commit: `dz = MAX(MIN(dz,1.0),0.0) !no extrapolation`, the same for `du` and `da`
  `[verified: raw.githubusercontent.com/cconroy20/fsps/bd187a0d…/src/add_nebular.f90, read at S43]`. `nebular.py`'s docstring
  ("clamped at the edges where FSPS extrapolates"), D192 (twice: "clamped at the edges where FSPS extrapolates"; "Chosen
  against: extrapolating off the grid as FSPS does") and #118's text say otherwise. **That sentence was written at S42's
  review from an incomplete grep of the FSPS source, not from the interpolation routine; it is wrong, and this audit says
  so plainly.** The model's trilinear-in-log-L, clamped reading is exactly FSPS's. *Decision:* the record — part of **#122**.
- **A4-3 (defect, a data row). `spectra.GRAIN_TABLE`'s 398.107 µm row carries the file's 380.189 µm values.** File:
  `3.98107E+02 0.0000 -0.0000 3.184E-26 2.277E+00`; code: `(398.107, 0.0000, -0.0001, 3.493e-26, 2.498e00)`, which is the
  file's `3.80189E+02` row `[verified: astro.princeton.edu/~draine/dust/extcurvs/kext_albedo_WD_MW_3.1_60_D03.all, both
  rows read at S43]`. 103 of the table's **104** rows match (D189 and §0 said 110). The test's identity K_abs · M_dust/H =
  (1 − albedo) C_ext holds for a shifted row, so it could not catch this; the effect is confined to the log–log
  interpolation between 251 and 631 µm (C_ext 9.7 % high at 398 µm), which no filter the viewer offers reads — the
  thermal shape is the dust stage's own κ, not the table's. *Decision:* the next session corrects the row and adds a test
  that pins each kept row's λ against the file's own λ list (a row can be right and misplaced). Registered as **#123**.
- **A4-4 (defect in effect, #120's half decided). STScI's WFC3/UVIS throughputs are on vacuum wavelengths; the model
  places its air lines on them.** WFC3 IHB §6.5: "All measurements of the UVIS filters which involve wavelengths … were
  done in air. The data have been converted to vacuum wavelengths using the formula given by D. C. Morton (1991, ApJS 77,
  119)" `[verified: hst-docs.stsci.edu/wfc3ihb …/6-5-uvis-spectral-elements, read at S43]`; SVO's VOTables say nothing
  either way (§1 item 17a). The tool's recorded both-ways numbers are the size of it: Hα in F656N 0.9617 → 0.9453, [S II]
  6716 in F673N 0.9826 → 0.9577, 6731 0.8565 → 0.8632, [O III] in F502N 0.9025 → 0.8987; Morton 1991's n − 1 is
  2.792 × 10⁻⁴ at 5000 Å and 2.767 × 10⁻⁴ at 6600 Å, so the tool's 1.000277 is the right factor. *Decision:* the next session
  either shifts the instrument curves to air in `fetch_filters.py` (one factor, the sets regenerated) or gives a filter set
  a `wavelengths: "vacuum"` flag the line integral honours; `test_render`'s 0.962 / 0.903 pins move with it. #120 keeps
  its sprite half; its convention half is decided and becomes the fix.
- **A4-5 (#107's inferred half, found). CMD's U B V are not SVO's Generic/Bessell, and YBC's Vega is not SVO's.** CMD's
  photometric-systems page: "UBVRIJHK … Maiz-Apellaniz (2006), Bessell (1990), Bessell & Brett (1988) · combination of
  previous 2 systems", the first being "Johnson · ubv · UBV · Maiz-Apellaniz (2006)" `[verified: stev.oapd.inaf.it/cmd_3.9/
  photsys.html, read at S43 — reachable over http where S38 failed on TLS]`; YBC uses `alpha_lyr_stis_008.fits` (Chen et al.
  2019, arXiv:1910.09037), SVO `alpha_lyr_stis_010.fits` (Rodrigo et al. 2024, arXiv:2406.03310 l. 980). So the per-band
  zero-point term the code names `[inferred]` is real and now has two named parts; (RI)c and JHK match in attribution
  (SVO's J H K "include ~1.2 KPNO atmosphere", a note). *Decision:* #107 re-described; what closes it is the Maíz Apellániz
  2006 U B V curves and the stis_008 Vega read as the anchors' definitions — a reading, then a re-pin of V1's 8.9 × 10⁻⁵.
- **A4-6 (adopted, mislabelled). The "TIR" box is Sanders & Mirabel's 8–1000 µm L_IR; TIR is 3–1100 µm** (Dale & Helou
  2002; Kennicutt & Evans 2012: "we refer to this as the total-infrared or TIR luminosity") `[verified: arXiv:1204.3552
  definitions.tex 108–113; arXiv:astro-ph/0205085 ms.tex 160–162, read at S43]`. For 15–21 K dust the short edge is worth
  5 × 10⁻⁷ of Σ_IR (§3); the label is wrong, the number is not. *Decision:* the record (#122); the `[recall]` tag in
  `filters.json` lifts to a citation.
- **A4-7 (the greens).** V1's gate dies without its passes (B − V +0.0595, M_V +0.017 at 0 passes; +0.005, −0.002 at 4) —
  green by construction; V2's balance survives β ± 0.10 and a 3–1000 µm box (the two sides are one function); V3's
  sixty-window statistic survives two re-tilings (z̄ +0.10 / +0.24, sd 0.90 / 1.12); row 34 survives its named
  alternative and is strengthened by it (Q / 0.7095 = 2.33 × 10⁵³ inside both windows). *Decision:* none; recorded here and
  in `test_s22_rulings`' conditioning of row 34 at the next touch.
- **A4-8 (the mesh).** Every gate and identity holds at (150, 500, 10, 240); the frame-against-published-total tolerances
  carry a dR² term that would fail 10⁻³ below ~170 rings; the render's light is the same across levels to 4.6 × 10⁻⁴ on a
  cell-aligned window; the disc's catalogue-against-field reads 0.949 at z −0.86 for this mesh's census. *Decision:*
  `tests/test_audit_iv.py` stays in the suite (as Audit III's does); no number moves.
- **A4-9 (the blind row).** #117's window is set (§4) and the model, measured after, misses it by 4σ in the direction the
  reader named. *Decision (the next session's):* enter row 37 as the blind-with-disclosure row, a recorded miss under
  #117, its prediction "the gradient is the chemistry's" — and read the T_e run of the grid against the Galactic +345–359
  K kpc⁻¹ before blaming the chemistry (the grid's T_e is its own; the model's `hii_temperature` is a separate column the
  grid does not read).
- **A4-10 (the POST path and the ingress).** The three refusals are RFC 9110's own statuses (§15.5.12, .14, .16); Microsoft
  documents no request-line, header or body limit for Container Apps ingress; Envoy's default is 60 KiB of request headers
  (431 past it), so 4 KB is inside and a 1 MiB body has no documented ceiling; `test_api`'s POST test re-run through the
  real transport passes `[verified: tests/test_api.py::test_a_post_is_the_get_with_its_query_in_the_body, 2026-09-30]`.
  *Decision:* none; `transport.js`'s "inside every proxy's limit" is now "inside Envoy's documented default" (#122).
- **A4-11 (the record, gathered as #122).** D189's "110 rows" is 104; `nebular.py`'s and D192's "FSPS extrapolates"; the
  `prsc` file's axes (11 Z with four shifted, a 20 Myr row) are FSPS's later product and not the nine-age Padova/MIST grid
  Byler's paper tabulates — cite "Byler et al. 2017's method as FSPS ships it"; FSPS's vacuum line wavelengths sit
  +0.07–0.10 Å above NIST air × Morton 1991; `LINE_WAVELENGTHS`' `[recall]` is now READ at NIST (all six within 0.05 Å) and
  `clouds.K_OVER_MH`'s `[recall]` is READ at CODATA; two solar masses in the code (`dust.GRAMS_PER_MSUN` 1.98847e33 against
  `SOLAR_MASS_G` 1.98841e33, IAU 2015's GM/G); D189's "monochromatic R_V 3.31" is 3.28 with both bands at their pivots; the
  ir set's "TIR"; Byler's U at a fixed inner face of a thin shell against the model's at the Strömgren radius of a filled
  sphere (#118's text). None moves a number. *Decision:* an about-line and docstring pass in the next session that touches
  these files. Registered as **#122**.

**Counts.** 20 items re-read (21 briefed, one skipped by the brief): **12 match, 4 differ** (CMD's U B V curves and Vega;
one grain row of 104; FSPS clamps and the grid's solar scale; the WFC3 curves are vacuum), **4 adopted and disclosed**
(one of them, the ir box, under the wrong name), 0 misattributed in code, 0 unreachable (two sub-readings second-hand:
DLMF's table via MathWorld, three ADS records via SVO's own links); 103 of 104 grain rows match; all 24 SVO Bessell numbers
match with the field named (λ_ref ≡ pivot; Vega, Pogson, Jy → erg/cm²/s/Å). Thirteen gates and identities re-derived at a
fourth mesh, all inside the cost the mesh sets, one property (the render across levels) checked for the first time. Four
greens and row 34 conditioned: two green by construction, one self-bounding, one survives re-tiling, row 34 strengthened
by its alternative. One blind window set (and one clean reading for #119); the model misses the window by 4σ, measured
after. Fourteen register items re-stated: 9 open as described, 1 closable as a miss, 2 wrongly described, 2 re-described.
Three new debts (#121–#123). No number moved.
