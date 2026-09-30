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
