# BRIEF — for S29: BUILD_II Phase 4, stellar remnants and planetary nebulae (Opus subagent)

**For the orchestrating session.** Open `session-29` (main checkout on `main`); hand an Opus subagent,
in a worktree (`git checkout session-29`, `git config --worktree core.hooksPath tools/hooks`), this
file, `BUILD_II.md` Phase 4, `RULES.md`, `RESUMING.md`'s "Writing a stage", `stages/photometry.py`
(`lookup_columns`, present mass and phase), `stages/massive_stars.py` (S28's pattern: a sourced table
with a named alternative), `stages/systems.py` (columns inside `materialise`, D60), `stages/light.py`
(population integrals). It neither pushes nor writes DECISIONS.md. Debts from #85, decisions from
D178; MANUAL_TODO's `s28` row takes S28's merge SHA. **Rulings made here (D113):** (a) the
initial–final mass relation is **sourced** (NEEDS SOURCING: Cummings et al. 2018, ApJ 866, 21, the
white-dwarf IFMR; a read-only agent fetches the fitted segments verbatim) and the remnant classes' mass
boundaries are the source's, not recalled; (b) the black-hole mass's metallicity dependence enters only
if a source is read for it (NEEDS SOURCING: Spera, Mapelli & Bressan 2015 or Fryer et al. 2012),
otherwise a stated fraction of the initial mass with the dependence a debt, not invented; (c) the
planetary-nebula duration is a sourced number or the flag is not built (NEEDS SOURCING: ~10⁴ yr; the
PNLF cutoff M* ≈ −4.5 is Phase 9's row, only its citation read here, Ciardullo et al.).

## What to build (BUILD_II Phase 4, reconciled)
- **`star_remnant`**, a category column on the catalogue: `none / white_dwarf / neutron_star /
  black_hole` (and `planetary_nebula` if (c) closes), from the star's initial mass and age against the
  isochrone lifetimes the table already holds (a dead star is NaN in L and T_eff, D164) and the IFMR.
  Every value is looked up inside `materialise`, every ring and sector whatever a request asked for.
- **`star_remnant_mass`** (a column) and **`remnant_mass_fraction`** (a scalar) — the latter a
  **population integral** over the history, as `light.py` integrates light, not the sample. Relate it to
  `RETURN_FRACTION`'s locked mass (`stellar_mass_total` counts locked mass; this phase says what it is):
  assert remnant + living mass reconciles with it, the tolerance measured, any gap explained.
- **Planetary nebulae**: a star within the sourced phase duration of the end of its AGB life is flagged
  (a `planetary_nebula` category or a flag column) with `star_pn_age` or the duration published as a
  constant; the emissivity is Phase 9's. Say how many PNe the default galaxy carries and compare to
  the Milky Way's estimated population only if a source for that count is read.
- **No new inputs** (A2, A4). New constants in level0 with citations; module-level constants only where
  `materialise` cannot read `ctx.constants`, as S28 did, and say so.
- No acceptance row is added unless its target has a source with an uncertainty (D100, #17). If the
  remnant fraction has one (BUILD_II's "10–15%" NEEDS SOURCING), add row 30 citing it; otherwise
  publish the number and leave the row for Audit III.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–29 unmoved
(15 = 5.20971 recorded miss #80; 29 = −7.914); the remnant classes partition the dead stars exactly
(no star two things, none `none` while dead); the mass reconciliation asserted; the new columns'
per-region determinism (D60) asserted; new tests on the coarse grid where the claim allows; existing
pins untouched unless one moves, and then the old number in the comment.

## Traps
- The catalogue is priced per cell (D168's `CellCache`); a new column must not add a per-request pass
  over every ring — follow `lookup_columns`' path.
- About lines must not name constants (D5). The units vocabulary is closed: a new unit is a `core/`
  edit plus a line in the decision candidate.
- `tools/timings.py` rows pin the routes; a new column changes no route. If `systems` cost moves, say
  by how much (S28's light moved 0.30 → 0.40 s cold and the timings were re-published).
- Machine: `uv run` only; the Bash tool fails over ~8 KB; cp1252 console (`encoding="utf-8"`, LF
  newlines); `grep -c` exits 1 on zero matches; long runs backgrounded with `EXIT=$?` on the log.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp` (MANUAL_TODO §2).

## At close (orchestrator)
Read the core diff first, then the tests. Board row 29 ☑ with the subagent's model; `progress.py`; the
suite backgrounded, merge gated on its EXIT line; D178 with rulings (a)–(c) and their sources, the
remnant fraction and its reconciliation, the PN count; RESUMING (≤ 120) and this file for **S30 (Phase
6, Opus)**; `MANUAL_TODO.md` row `s29` with `s28`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
