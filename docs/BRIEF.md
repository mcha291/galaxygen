# BRIEF — for S46: the owner's choice after row 37's diagnosis

**The state (2026-10-01).** S45 is merged (D196). Row 37's miss (−0.1035 dex/kpc against the blind [−0.045, −0.005]) is
taken apart in `tests/test_s45_diagnosis.py`, pinned: **the metallicity path is the whole gradient** (the regions' age
and U frozen at 8.2 kpc → −0.1177; log Z frozen → −0.0016; all frozen → −0.0005); **the grid responds at 1.22 per dex of
log Z, 0.70 of PP04's empirical 1.75**, so the grid is not too steep; **the regions' oxygen gradient is −0.078 dex/kpc,
steeper than the Cepheids' −0.064 ± 0.003** that row 22 is set from, by 0.014 — worth −0.017 of the ratio gradient
(**#124**, the gas gradient, opened). At the Cepheids' own gradient the model would still read −0.078, 3.7σ out, so the
rest of the miss is a **conflict between Zhao et al. 2026's LAMOST N2 gradient and the Galaxy's Cepheid abundance
gradient**, preserved as named rulesets (B12). #117 re-described; row 37's miss text rewritten with the prediction
below. Option 4 done: `prod` checked through the real transport, CI's image built. **No number moved.** Register: **63
open = 11 permanent + 52 carried, 44 discharged.** Specs 12 / 20 / 5 of 37 both models; vitest 121.

## What S46 could do — the owner chooses; none is started without the word (numbers from #125, D197, row 38)
1. **The blind third measurement** (#117's and #124's closer, D196). A reader forbidden the repository sets, before any
   model number is read against it: the direct-method (T_e) HII-region O/H gradient of the Milky Way over 8–15 kpc
   with its 1σ — Esteban & García-Rojas 2018 (MNRAS 478, 2315) and Arellano-Córdova et al. 2020 (MNRAS 496, 1051) as the
   candidates, the reader choosing and saying why — written to `docs/AUDIT_V_BLIND.md` in Audit IV's shape. The reading
   the aim must pre-state: flatter than −0.03 dex/kpc → the Galaxy's HII gas is flatter than its Cepheids and the
   model's gas gradient is the defect in full (a chemistry ruling, item 2); steeper than −0.05 → LAMOST's N2 gradient is
   the outlier and row 37's source carries the conflict; between → both. Then the model's `hii_oxygen_abundance`
   gradient (−0.078) is read against it once, disclosed as measured after, and a row 38 may be entered if the window
   has width. Half a session; the reader is a Fable or Opus agent spawned by the session with the brief written first.
2. **The chemistry ruling (#124).** Only after item 1. What makes the gas steeper than the stars it just formed:
   `chemistry_dtd`'s present-day enrichment profile or `ism`'s mixing — read the stage, name the mechanism, state the
   prediction, then change one function (D114); rows 22 and 23 are re-read after (B10), and row 37 with them. Not to
   be done in the same session as item 1 unless the window is wide.
3. **The redeploy (option 4, ready).** The live viewer predates S42–S45. The image for `main`'s tip is built by CI on
   every push (`.github/workflows/image.yml`, tagged by short SHA). The owner runs, from the repository root:
   `./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag <short SHA of main's tip>` (the S45 tag-record commit's, after
   this merge). A session can re-check `prod` (:8018) first if asked; the deploy itself is the owner's.
4. **#119** (the DIG's two sourced ratios), **#107** (the SED's anchors: a download), **Audit V** of S44–S45's constants
   (8.93, Morton's coefficients, the grain row, 1.98841e33, the diagnosis's pins) — as S44's BRIEF described them.

## Gate for whichever is chosen
The named test files green with every moved pin's reason in its comment; specs reported for both models; vitest and
`npx vite build` clean if the viewer changes; **`uv run python tools/bootstrap.py` before the full suite** (agent
worktrees rewrite the hooks path, S44); the suite backgrounded with its own `EXIT=` line; merge, push, **tag `s46` on
the merge and push it**, `ls-remote` read back, the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- Never force-push; never touch :5173; a scratch check uses `.claude/launch.json` "prod" (:8018, `npx vite build` first),
  stopped after. `uv run` only; LF newlines; the Bash tool fails over ~8 KB; `grep -c` exits 1 on zero; `git commit -F -`
  fails; bare `python` is not on the path. Do not merge or delete the sealed branches (MANUAL_TODO §2). Download nothing
  without the owner's word (item 1's papers are read by the agent at their sources, not fetched into the repository).
- A number the model has printed gets only a blind or a disclosed row (#117, D192, D195, D196): the model's gas gradient
  −0.078 is printed, so item 1's window is set before it is compared, and the comparison is disclosed in the row.
- The specs report's summary lines do not survive a Bash-tool background move; redirect `python -m galaxy.specs` to a
  file. The full suite is ~17 min; `test_s21b_the_catalogue_is_priced_per_cell…` is load-flaky — re-run alone, say so.
- Builders in parallel worktrees own disjoint files; a record pass runs last; brief them to grep the inventories
  (`test_graph`, `test_audit`'s `lost`, `test_sfh_azimuthal`'s row range, `test_nebular`'s scalar loop).
- `OXYGEN_ABUNDANCE_SOLAR` (8.69) is the T_e and PAH relations' scale; the grid's is `NEBULAR_GRID_OXYGEN_SOLAR` (8.93).
  The grid reads log Z, age and U only — it carries its own N/O; the model's N/H column is not a lever (D196).
