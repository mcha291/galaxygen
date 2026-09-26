# BRIEF — for S34: BUILD_II Phase 5, globular clusters and the stellar halo (Opus subagent)

**For the orchestrating session.** Open `session-34` from `main`; hand an Opus subagent, in a worktree
(`git checkout session-34`, `git config --worktree core.hooksPath tools/hooks`), this file, `BUILD_II.md`
Phase 5 in full (lines 422–515: the η relation, the Harris catalogue, the stellar halo, why satellites
were cut — do not reinstate them), `RULES.md`, `RESUMING.md`'s "Writing a stage", `stages/clusters.py`
(S33: `bound_cluster_mass_total` is the hook, `bound_mass()`; the census's efficiency and bound fraction),
`stages/assembly.py` and `stages/halo.py` (what `mergers[]`, M₂₀₀ and the assembly history publish),
`specs/spec.py` (rows 1–31; how a row cites its source and states what it measures, D177), `models/level0.py`.
It neither pushes nor writes DECISIONS.md. Debts from #98, decisions from D183; MANUAL_TODO's `s33` row
takes S33's merge SHA. **Rulings made here (D113):** (a) **η is the check, not the mechanism**: the GC
system mass is the bound cluster mass S33 publishes times a survival fraction over the history, and the
survival is what the phase builds — SOURCED (Portegies Zwart, McKee & Gieles 2010 §5–6 on dissolution
timescales, or Kruijssen 2015 / Gieles & Baumgardt 2008 t_dis ∝ M^0.62 with its normalisation; a read-only
agent fetches the sentences) — otherwise the phase publishes the gap (#97) and no survival; (b) the
**residual around the mean is seeded** on `world_seed` at Boylan-Kolchin's 0.28 dex (§4b, derive-the-
mean-seed-the-residual), never the mean alone; (c) the **metal-poor share** is η_b/η from the same source,
tied to `mergers[]` (accreted = metal-poor) without a new mechanism; (d) the **stellar halo** is the
integral of the debris over `mergers[]` — the mass ratios and times the model already has — with a
stripped fraction only if sourced; otherwise the whole satellite mass, stated.

## What to build
- A `globular_clusters` stage (checkpoint 2 or 5, wherever its readers put it: it reads M₂₀₀,
  `mergers[]`, the assembly history and S33's bound mass) publishing `gc_system_mass` (η·M_halo via the
  survival, the residual seeded), `gc_metal_poor_fraction`, `gc_count_estimate` only if a mean cluster
  mass is sourced (BUILD_II: "acceptance row on mass, not count"), and the survival fraction itself.
- A `stellar_halo` stage or fields on the same stage: `halo_stellar_mass` from the debris integral, its
  radial profile if the source gives one (a power law with a sourced slope, else no profile).
- **Rows 32 and 33**, sourced before entry: the GC system mass read off the Harris catalogue
  (`https://physics.mcmaster.ca/~harris/mwgc.dat`, the catalogue's own statement, an agent reads it and
  states what it covers — #84's rule), and the stellar halo mass from Bland-Hawthorn & Gerhard 2016 §6
  `Ms` with its uncertainty. A row whose source does not state what it measures names no field (D177).
- Debt #97 either closes (the surviving mass reproduces η within 0.28 dex) or the report says what the
  survival had to assume to get there, and the debt stays with that number.
- No new inputs; level-0 constants with citations; about lines name no constant (D5).

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–31 unmoved
(15 = 5.20971, 29 = −7.914, 30 = 0.0176069, 31 = 0.0065332); rows 32–33 report pass or a recorded miss in
`spec.MISSES` with its debt and a killing prediction (D33, D87), never a widened target (B5); the
consistency check BUILD_II states (3.5e-5 × 1.1e12 ≈ 3.9e7 M☉) reproduced by the stage; the 228 fields per
model bit-identical (sha256 before and after); the seeded residual's draw asserted deterministic across
processes; existing pins untouched unless one moves, then the old number in the comment.

## Traps
- `world_seed` binds at the checkpoint of its earliest reader; `graph` requires that to equal the input's
  `checkpoint_hypothesis` (S17) — check where `world_seed` binds today before reading it.
- The Harris catalogue is a data file, not a paper: read its header for what it lists and quote it.
- Machine: `uv run`; the Bash tool fails over ~8 KB (write scripts to files); cp1252 console; LF newlines;
  `grep -c` exits 1 on zero matches and kills `&&` chains; `git commit -F -` fails — use a file; long
  runs backgrounded with `EXIT=$?`.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2.

## At close (orchestrator)
Core diff first, then tests. Board row 34 ☑ with the subagent's model; `progress.py`; the suite backgrounded,
merge gated on its EXIT line; D183 with rulings (a)–(d), the survival's numbers and rows 32–33's verdicts;
RESUMING (≤ 120) and this file for **S35 (Phase 9, nebular emission, Fable)**; `MANUAL_TODO.md` row `s34`
with `s33`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
