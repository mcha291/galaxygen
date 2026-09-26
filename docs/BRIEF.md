# BRIEF — for S32: BUILD_II Phase 8, the cloud catalogue and the cell hierarchy (Fable, own row)

Read `RULES.md` in full, `RESUMING.md`, `BUILD_II.md` Phase 8, `RENDER_PHYSICS.md` §0, §5 and §7, then
`stages/systems.py` (the cell grid `cell_edges` / `cells_in` / `cell_counts`, `materialise`, `Catalogue`, the
`(cell, index)` name, D60), `api/service.py` `_region` and `CellCache` (D168), `core/fielddoc.py` (`Kind.COLUMN`,
`of=`), `stages/ism.py` (`gas_molecular_surface_density`, `gas_midplane_pressure`), `stages/supernovae.py`
and `stages/dust.py` (the sourced-constant pattern). Branch `session-32`; commit and push at every
sub-deliverable; debts from #94, decisions from D181. **The sourcing is done** (a read-only agent, S31's
close; the numbers are in D181's candidate notes below and must be entered from them, not from recall):
- Mass function: Rice et al. 2016 (arXiv:1602.02791) inner Galaxy dN/dM ∝ M^γ, γ = −1.6 ± 0.1, truncation
  M₀ = (1.0 ± 0.2) × 10⁷ M☉; outer Galaxy γ = −2.2 ± 0.1, M₀ = (1.5 ± 0.5) × 10⁶; Rosolowsky 2005 eqs. 3–4
  for the form (inner MW −1.53 ± 0.07, M₀ ≈ 3 × 10⁶, the named alternative). Catalogued GMCs hold 25
  (+10.7, −5.8)% of the Milky Way's H₂ (Rice, abstract).
- Larson: Heyer et al. 2009 (0809.1397) eq. 10, σ_v = (πGΣ/5)^½ R^½, median Σ_GMC 42 M☉ pc⁻² (SRBY's 206
  the alternative). Larson 1981's σ_v = 1.10 L^0.38 and Solomon 1987's (1.0 ± 0.1) S^0.5 are secondhand
  (MODERATE) — alternatives, not the ruleset.
- Density PDF: Federrath, Klessen & Schmidt 2008 eq. 4 σ_s² = ln(1 + b²ℳ²); b = 0.36 ± 0.03 solenoidal,
  1.05 ± 0.19 compressive (Table 1); Federrath 2010 §3.6 "b ≈ 0.3–0.4 in 3D" for ζ ≳ 0.5.
- Lifetimes: Kawamura 2009 20–30 Myr with phases 6 / 13 / 7 Myr (Type I / II / III); Murray 2011 **17 ± 4
  Myr** (the plan's "27" is not in the paper); Chevance 2020 10–30 Myr, dispersal 1–5 Myr; Kruijssen 2019
  NGC 300 t_CO 10.8 (+2.1, −1.7), t_fb 1.5 ± 0.2 Myr, decorrelation length 100–150 pc.
- Not sourced: the gas temperature / Mach range (Heyer & Dame 2015 unreadable) — the sound speed needs a
  sourced T or the Mach number is not published; the ionizing-source offset and density gradient have no
  measured number anywhere — they are seeded draws with the distribution stated `[inferred]`.

## Rulings to make before any number is read (D113), and what to build
- **Clouds are an object class** beside stars: `FieldDecl(kind=Kind.COLUMN, of="cloud")` and a category
  column for the state; a `core/` edit only if the object machinery assumes one class (check `service.py`'s
  `columns` filter and `wire`). Drawn per cell by the same cell-and-index machinery, `(cell, index)` the
  name, so a region's clouds are a sweep's (D60).
- **The population**: the mass function normalised to Σ_H₂(R) × the pattern's contrast per cell (the
  molecular mass in clouds integrates back to the ISM's molecular gas mass — RENDER_PHYSICS §7's rule for
  clouds, asserted); the inner/outer γ and M₀ switch at a radius the ruling names (the sources say "inner"
  and "outer" Galaxy — read Rice's definition; else one law with the other as alternative); radius from
  Heyer's Σ_GMC; the Mach number from σ_v(R) over a sound speed only if T is sourced; `mach_number`,
  `density_gradient`, `ionizing_source_offset`, `age`, `state` (embedded / blown open / dispersing /
  remnant against Kawamura's phases), `metallicity` from the gas at the cloud's radius.
- **The cell hierarchy**: a level-k cell is one of 4^k children of a level-0 cell with its own seeded
  stream; `/api/region` takes `level=`; a child's density is its parent's at the child's centre. **Gate**:
  the same bounds and level twice → the same stars and clouds; overlapping bounds agree on the overlap;
  **a parent's stars are its children's** (union) and a smaller sample is a prefix of a larger one within a
  cell. This is a determinism contract that can hold at one level and break at another — test every level.
- No new inputs. Every constant in level0 with its citation; nothing from recall; about lines name no
  constant. A `timings.py` row for `level=`. Both models publish the clouds.

## Traps
- `materialise` takes every ring and sector whatever a request asked for (D60); a cloud draw must too.
- The catalogue is priced per cell (D168's `CellCache`): key the cache by level as well.
- The viewer is V3's: publish, do not draw. Machine: `uv run`; 8 KB Bash cap; LF; `grep -c` exits 1 on
  zero; long runs backgrounded with `EXIT=$?`. **Do not merge or delete** the sealed branches (MANUAL_TODO §2).

## At close
Board row 32 ☑ (Fable 5.1); `progress.py`; the suite; D181 with the rulings, the redistribution and union
checks' numbers, cloud counts and the mass in clouds; RESUMING (≤ 120) and this file for **S33 (Phase 11,
clusters, Opus)**; `MANUAL_TODO.md` row `s32` with `s31`'s SHA; merge `--no-ff`, push, `verify_clone`.
