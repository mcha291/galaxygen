# BRIEF — for S37: Audit III, the second build's own audit (Fable's own row)

**For the session.** Open `session-37` from `main`; read this file, `BUILD_II.md` "Audit III" (lines 745–755),
`AUDIT_RUN2.md` §5 (the green-row conditioning method), `AUDIT_II_A.md` §3 (how S21 (a) conditioned the greens
and what A-14 found: a "cited 35" that was an adopted value with the measurement at 39 ± 4), `RULES.md` B3, B9,
B12, B14, `GALAXY_INPUTS.md` §11 items #80–#103 (the second build's debts: every "read at S3x" tag names what
must be re-read), `DECISIONS.md` D173–D185. **This is a judgement session, once, on Fable; it changes no
physics.** Debts from #104, decisions from D186; MANUAL_TODO's `s36` row takes S36's merge SHA. **The aim,
stated before any file is opened (D113):**
1. **Every NEEDS-SOURCING that entered code S25–S36 has its citation re-read** by a read-only agent that did
   not write it, against the sentence the constant quotes: level-0 constants tagged `read at S2x/S3x`, the
   module tables (Case B rows, Q tables, the grain table, Storey & Hummer, Weaver's numbers), the spec rows
   32–36's targets and what each source says it measures (#84's rule). Report per constant: MATCHES / DIFFERS
   (with both numbers) / UNREACHABLE. A DIFFERS is a finding; a value that turns out adopted rather than
   measured (A-14's class) is a finding.
2. **Every redistribution and balance re-derived by hand**, at a mesh the build did not use (`GridSpec(n_R=180,
   n_t=600, n_z=8)` or another not in the tests): the clouds hold the molecular mass (D181), the clusters form
   at the SFR (D182), ΣQ closes on the light stage (D182), the HII census integrates to the field (D184), the
   remnants redistribute the rates (D185), the dust energy balance (D180), the pattern's contrast averages to
   1, the hierarchy's union at levels 1–3, `bound_cluster_mass_total` recomputed equals the field (D183). Each
   is a number at the new mesh beside the build's number, and a statement of what would have to be true for
   them to differ.
3. **Every green row added by the second build conditioned** (AUDIT_RUN2 §5): rows 29, 30, 31, 35 — which
   constant could have made each green, was the window read before the model's number, and does the green
   survive the alternative named in the constant's about line (e.g. row 35 under the outer cloud slope alone;
   row 31 at Maoz & Graur's measured efficiency, S30's candidate debt).
4. **The disclosed rows re-read blind**: rows 32 (#98: the M/L chosen with the model's number known) and 34
   (#100: Bennett chosen over McKee & Williams) — a reading agent given the source and not the model's number
   states which window it would enter and why; recorded either way.
5. **What the register owes an honest count**: #80–#103 each re-stated in one line as still-open / closable-now /
   wrongly-described, with the sentence that decides it. No debt is discharged in this session without the
   remedy its item names.

## Output
`docs/AUDIT_III.md` (new; the structure of AUDIT_II_A.md): §1 the sources re-read (a table: constant, quoted
sentence, re-read result), §2 the redistributions at the new mesh, §3 the green rows, §4 the disclosed rows
blind, §5 the register's re-statement, §6 findings numbered A3-1… with the decision each needs. Findings that
change a number are **not applied here** (B3: the audit checks, the next session fixes); they are debts or a
ruling for the owner, each with the sentence that decides it. D186 records the aim, the method, the counts
(re-read / matched / differed / unreachable), and the findings. Board row 37 ☑ (Fable 5.1).

## Gate
The suite unchanged and green (the audit adds `tests/test_audit_iii.py` only for the redistributions it re-derives,
on the new mesh, pinning nothing that a later session's physics would move without a stated reason); `python -m
galaxy.specs` exits 0; no physics file edited (`git diff --stat main` names only docs/ and the one test file).

## Traps
- Read the constant's own tag before the source: the finding is the gap between the two, not the source alone.
- The owner's open word on the Byler/FSPS grid (D184) is not this session's to decide; record it as owed.
- Machine: `uv run`; the Bash tool fails over ~8 KB (scripts to files); cp1252 console; LF newlines; `grep -c`
  exits 1 on zero matches; `git commit -F -` fails, use a file; long runs backgrounded with `EXIT=$?`.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2; do not merge or delete
  `claude/blissful-poitras-2cbbd3` (a live worktree, `galaxygen-audit-run-2-8c6fb0`).

## At close
Board row 37 ☑; `progress.py`; the suite backgrounded, merge gated on its EXIT line; D186; RESUMING (≤ 120) and
this file for **S38 (V1, the renderer's filter integral, Opus)**; `MANUAL_TODO.md` row `s37` with `s36`'s SHA;
merge `--no-ff`, push, `verify_clone --ref main` on a quiet machine.
