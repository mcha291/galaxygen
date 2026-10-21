# BRIEF — S70: Audit V's fixes (an Opus lead; the verdict is `AUDIT_V.md` §6, the order is its last paragraph)

**The state (2026-10-21).** S69 is merged (D233): Audit V — 61 findings, the verdict on each, no number moved (B3).
Register 128 open = 11 + 117, 51 discharged; next number **#197**, decisions from **D234**, board row 70 is this
session, acceptance rows from 38. **The owner's standing order:** run the sessions back to back, stop only for a ruling
that is theirs; re-read their latest word on models and the rationing rule (two agents at once, one heavy; the 80 %
weekly stop was waived for Audit V on 2026-10-21 — ask again before assuming it is waived here).

## Build: the fixes, in `AUDIT_V.md` §6's order (B3: the audit checked, this session fixes; one commit per class)
1. **The invariants' tests** (#194, F-3-1 first): each placed census's `FieldDecl`s gain a declared placement set (the
   columns the layer may move); a test matches each census's objects by (drawn ring, index) on/off and under a texture
   reroll and holds every other column bit for bit. Then F-3-2 (SMALL `ngc_4414` + one non-default seed pair), F-3-4
   (the stars' expectation from the stage), F-3-5 (`only_if`), F-3-6 (a composing stage's non-composed outputs on/off at
   a second template and seed), F-3-9 (the layer-read guard), F-3-12 (`same_expected_total`), F-3-13 ("does not keep" in
   every synthetic declaration), F-3-15 (recompute one cell's normaliser from (seed, cell)). Text amendments in
   `BUILD_III.md` §1 and the test's comments: F-3-3, F-3-7, F-3-8, F-3-10, F-3-11 (pin `EXPECTED_TOTAL_UNITS` to the
   measured 1 or rename it a margin; assert the 1e-13 per ring or strike the clause); F-3-14's clause in rule 3.
2. **The citations, one pass** (`AUDIT_V.md` §1; the readers' notes name every line): #193's disclosure in `level0.py`
   with 1.73 as the named alternative; F-1A-4's clause struck; F-1A-2/3/5/9, F-1B-1/4/5/8 in the about-lines; the
   reading rows F-1A-6–14, F-1B-6 corrected and marked "re-read at Audit V"; F-1B-7's five sources read once. **#191–#193
   as the owner ruled** (D233's last paragraph): #192 moves the clouds' sizes — the affected pins (row 37, the clustering
   snapshots, the frames) re-pinned `# S70 (D234): was <old>` with the reason; #191 and #193 move nothing.
3. **The viewer's two gaps:** F-4-2 the cell outlines from `gas_fluctuation.edges` (the four star-first captures move
   by the grid alone — regenerate and say so); F-4-3 the clouds' axis ratio and angle as two columns of `/api/clouds`,
   derived exactly as `cloudOpacity.ts` does today, the viewer reading them (no picture moves; the physics-only frame
   byte for byte). F-4-5: one capture with dither off, recorded, nothing changed. §8 of `RENDER_PHYSICS.md` gains D233's
   sentence on per-component intensities.
4. **The register pass** (`AUDIT_V.md` §5; in ONE commit with `tests/test_audit.py`'s two pins): strike #137 (its ulp
   residue noted under #196 or #194); re-write #39 as live; narrow #114, #115; re-rule #15 for `basic`; widen #128(b) and
   re-read `ngc_4414`'s `colour_b_v_face_on` through the layered dust (a check, not a row); correct #21, #80, #87, #93,
   #43, #33; give #154 a surviving pin; re-point #110, #159–#162, #166 to this session or re-rule carried with the reason;
   re-name #171's and #173's closers (take #173's randomised-order run into `test_audit_v.py`); one sentence on 53–64.
5. **#196's bounds measured over the population** at the production grid and two seeds, written "measured over N"
   (D117), the declarations and `test_audit_v.py` holding them; #195's declaration says the measured share and why; the
   xfails resolved or re-ruled with the measurement; F-2-5's wording; F-2-3's 2e-13; F-2-8's inner-ring slope entered.
6. **Gate:** `tests/test_audit_v.py` green with no strict xfail left unexplained; `test_layer.py` green with the new
   per-object test; the specs' 12 / 20 / 5 unmoved unless an owner's ruling moved a number (then the row named); the
   picture test byte for byte except the four star-first captures F-4-2 moves; the suite once on the final state; the
   register's counts re-derived and pinned in the same commit. **Agents:** one builder per class (1–2 at once, one heavy),
   one reviewer of the invariants' test (it is the audit's chief finding — measure what it catches by breaking a column).

## Read
- `AUDIT_V.md` §6 then §1–§5 (every file:line the fixes need; the readers' notes are not in the repo); D233; `BUILD_III.md` §1.

## Told to the owner (nothing awaited; their word first if they answer)
- (a) **Ruled 2026-10-21 (D233):** #191 `BAR_GAS_RATIO` redefined as the ratio of medians; #192 the source's three Σ_GMC
  regimes with a declared boundary per template (a number moves — re-pin with the reason); #193 2.43 kept, 1.73 named.
- (d) Their Milky Way default (`cloudsExtinction: false`) leaves half the disc's dust undrawn and a ring edge at
  4.7 kpc in the physics-only frame (F-4-1); the sample stars read as cluster-sized dots at point gain 4 (F-4-6).
- (e) The frames did not move at S69; `AUDIT_V.md` §5's two sentences say where they stand beside the goals.
- (f) Carried, theirs: #172, #176, #164, #159, #142, #145, #147, the 88-minute gate test, the gateway csproj's "v",
  #183–#186, #188.

## Traps learned at S69
- **Blind readers find the drift**: keep the audit's readers away from DECISIONS/RESUMING/BRIEF/GALAXY_PLAN.
- **A bound from ten samples is not a bound**: measure over the population before a declaration says "at most".
- **The register's count is pinned twice in `tests/test_audit.py`** (the tuple and the carried row's literal): re-pin
  both in the commit that moves the register and re-run `-k register` — S68's verify_clone failed on it.
- Still standing: Bash under 8 KB; pytest's exit code to a file; one picture-test run at a time (:8019); an agent worktree
  rewrites `core.hooksPath` (`tools/bootstrap.py` before the suite); layer off nothing may move; nothing is tuned to a goal picture.
