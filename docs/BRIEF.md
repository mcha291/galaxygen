# BRIEF — for S39: V2, volumetric emissivity and emitting dust in the field regime (Opus subagent)

**For the orchestrating session.** Open `session-39` from `main` **and move the main checkout back to `main`
before launching** (two checkouts cannot hold one branch, D188). Hand an Opus subagent, in a worktree
(`git checkout session-39`, `git config --worktree core.hooksPath tools/hooks`), this file, `BUILD_II.md` "V2"
(lines 770–778), `RENDER_PHYSICS.md` §§0 (what V1 left of the exception), 2, 4, 6, 7, 8, `RENDER_PLAN.md` Part 2
(R1 additive HDR, R4 dust as subtraction, R5 bloom) and Part 3 check 2 (the face-on Σ_V(R) profile),
`stages/spectra.py` (V1's spectrum function and `/api/render`: the components' arrays; extend it, do not fork it),
`stages/nebular.py` (`halpha_surface_brightness_hii/_dig/_nebular`, `dig_scale_height`, the HII regions'
per-volume emissivity), `stages/dust.py` (τ_sca, E(B − V), g, Σ_abs, T_d, Σ_IR, the grain table's per-band
extinction — the curve S31 read and #108 asks for per filter), `stages/ism.py` (A_V), `frontend/src/galaxy/
FieldVolume.tsx` and `regimes.ts` (the ray-marcher; the inventions left: Hα knots, the dust's lead and clumps,
`CHANNEL_EXTINCTION`), `filters.json`. It neither pushes nor writes DECISIONS.md. Debts from #109, decisions
from D189; MANUAL_TODO's `s38` row takes S38's merge SHA. **Rulings made here (D113):** (a) **the dust
component becomes two**: extinction per filter from the grain table's curve (the table in the repository since
S31: one column per band, the ratio A_λ/A_V read at each filter's reference wavelength — no new source) and
**thermal emission** as the published Σ_IR at T_d through the filter (a modified blackbody at the published β,
per cell), plus **scattered light** as the published τ_sca × the stellar response × the phase function at the
published g (Henyey–Greenstein is the standard form — read it in a source or state it `[inferred]`); (b) **the
line component is volumetric**: the ray-marcher integrates the nebular fields with the DIG's published scale
height and the HII share concentrated by the pattern's contrast, replacing the seeded knots; the clump lattice
goes; (c) the gate is energy balance **in the frame**: the light the frame's dust removes (per filter, summed
over the image) equals the infrared the frame's dust emits, both read back from the render arrays, to a stated
tolerance, plus RENDER_PLAN Part 3's check 2 — the face-on surface-brightness profile read from the frame equals
the published Σ_V(R) to a stated tolerance.

## What to build
- `/api/render` gains component arrays `dust_extinction` (n_R, n_φ or n, per filter: the transmission factor
  10^(−0.4 A_λ) from A_V and the curve), `dust_scattered` (per filter), `dust_thermal` (per filter, the modified
  blackbody through the curve — zero in optical sets, real in an infrared set: add an "ir" set with stated boxes
  at J H K and one far-infrared box so the balance can be read), and the volumetric line component per cell with
  the DIG layer's scale height in the header; the header's `components` names each with its fields and about.
- The viewer: `FieldVolume` integrates the line volumetrically (limb brightening for free, §4), applies the
  per-filter extinction, adds scattered and thermal dust; `CHANNEL_EXTINCTION`, the knots and the clump lattice
  are removed and `regimes.ts`'s docstring says what invention remains (nothing at galaxy scale, or name it).
- **Tests**: a Python test integrates absorbed vs emitted over the frame from the arrays (the balance) and reads
  Σ_V(R) back from the frame against the published field; vitest for the new viewer maths; the timings rows
  re-measured (the render row's bytes grow: state them). Both models. No stage changes unless a field is missing
  — then name it and keep every existing field bit-identical.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–36 unmoved; the 296/297
fields per model bit-identical (or the additions named); the frame's energy balance to a stated tolerance; the
face-on Σ_V(R) from the frame within a stated tolerance of the published field; the V1 gate still closes (frame
B − V and M_V, now with extinction OFF — say how the test turns it off); frontend build clean, vitest green;
pins moved only with the old number in a comment.

## Traps
- No downloads (the instrument filter files are the owner's call, #108). Read pages, cite URLs.
- The owner watches :5173 live: one consistent edit per file. Do not start the dev server; use a scratch port.
- Machine: `uv run`; `npm --prefix frontend run test -- --run` and `run build`; the Bash tool fails over ~8 KB;
  cp1252 console; LF newlines; `grep -c` exits 1 on zero matches; `git commit -F -` fails, use a file.
- **Do not merge or delete** the sealed audit branches (MANUAL_TODO §2) or `claude/blissful-poitras-2cbbd3`.

## At close (orchestrator)
Core diff first, then tests. Board row 39 ☑ with the subagent's model; `progress.py`; the suite backgrounded,
merge gated on its EXIT line; D189; RESUMING (≤ 120) and this file for **S40 (V3, region synthesis, Fable)**;
`MANUAL_TODO.md` row `s39` with `s38`'s SHA; merge `--no-ff`, push, `verify_clone --ref main` on a quiet machine.
