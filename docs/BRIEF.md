# BRIEF — for S38: V1, the spectrum function and the filter sets (Opus subagent), after Audit III's fixes

**For the orchestrating session.** Open `session-38` from `main`. **First, before any worktree branches**, the
orchestrator applies Audit III's two code findings as one commit on `session-38` (B3: the audit checked, this
session fixes): (i) **#104** — `habitable_zone.sterilization_distance` takes the square root Gowanlock et al.
2011 eq. 5 prints (exponent −0.2), the zone's probes re-pin to the second reading's numbers (hazard at R₀ 0.20
per Gyr, count peaking at 6.6 kpc, D179), #90's reading question closes; (ii) **#105** — `GC_HALO_MASS_RATIO`
2.9 × 10⁻⁵, `GC_METAL_POOR_HALO_MASS_RATIO` and `GC_MEAN_MASS` re-cited to Harris, Blakeslee & Harris 2017
(arXiv:1701.04845) with the measured values (η_b: read it there or keep BK17's adopted 2–2.5 and say so), the
scatter as an rms, arXiv ids corrected to 1705.01548, the consistency test's number moved with the old one in
its comment; and (iii) **#106**'s about-line pass (the Haffner sections, Hoopes & Walterbos, Rémy-Ruyer §1, KE12
§3.8 eq. 12, `HII_LF_MIN_LUMINOSITY`'s unit label, the stale α_B comment; `HALPHA_PER_SFR` stays 4.86 × 10⁷
unless the pins allow 4.8644 × 10⁷). Run the suite; D187 opens with these. Then hand an Opus subagent, in a
worktree (`git checkout session-38`, `git config --worktree core.hooksPath tools/hooks`), this file, `BUILD_II.md`
"V1–V4" (lines 758–790), `RENDER_PHYSICS.md` §§0 (the open ruling, lines 92–101), 2, 2a, 3, 3a, 8, `RENDER_PLAN.md`
Part 2 and Part 3, `frontend/src/galaxy/regimes.ts` (YOUNG_SHARE 0.3, YOUNG_KELVIN 12000, YOUNG_CLUMP — the
display constants V1 removes), `FieldVolume.tsx`, `colors.ts`, `api/service.py` (`/api/arrays`, `/api/fields`; a
new route is a `Route` plus a timings row), `stages/light.py` (the eight bands, `disc_light_temperature`,
`population_light`), `stages/photometry.py` (`band_flux_at`). It neither pushes nor writes DECISIONS.md. Debts
from #107, decisions from D187 (D187 = the fixes; D188 = V1); MANUAL_TODO's `s37` row takes S37's merge SHA.
**Ruling made here (D113): the filter integral runs server-side, option (a)** — the viewer sends a named filter
set (or its curves) and the model returns each component's per-channel response per cell (three or four floats
per cell per component), so the viewer still computes no physics (D5) and the payload is today's texture's.

## What to build
- A `/api/render` route (model, filters=<name>|curves, r/phi window optional, level): per cell the stellar
  component's response in each filter of the set from the population's own temperature mix (`disc_light_
  temperature` and the band tables — a per-cell blackbody mix at the published temperature is the first cut,
  the eight-band table the check), plus the published line components (Hα from the nebular fields) and the dust
  (A_V per line of sight) as separate arrays, never composited server-side (§2: components, not colours).
- Filter sets held by the **viewer** as data (§2a): broadband RGB (three wide filters with stated curves —
  sourced: Bessell 1990 or a CIE-like tristimulus, read and cited), SHO/HOO (three narrow filters at the line
  wavelengths, widths stated), one named instrument (e.g. HST WFC3 F435W/F555W/F814W curves from a public SVO
  Filter Profile Service file — a **download**: list filename, source, size and ask the owner; if not approved,
  ship the two analytic sets only and say so).
- The field regime's young light: `YOUNG_SHARE`/`YOUNG_KELVIN`/`YOUNG_CLUMP` removed; the stellar component's
  colour per cell is the published temperature mix. The clump lattice and Hα knots stay for V2 (§0's dated
  exception narrows, the docstring says which invention is left).
- **Gate:** the integrated B − V and M_V of the rendered whole-galaxy frame, read back from the frame (a tone-map
  inverse or the linear buffer before it), equal Phase 3's `colour_b_v` 0.6306 and `absolute_magnitude_v`
  −21.2159 to the tone map's stated tolerance; a test drives `Service().handle("/api/render", …)` and integrates
  the response without a browser; the viewer's Vitest suite for the filter maths; `tests/test_viewer.py` if
  chromium exists (it does not here: the test skips, say so).

## Traps
- The viewer computes no physics (D5): the filter integral is the model's; the viewer multiplies published
  responses by its tone map only. A constant the renderer needs is a published scalar (D180).
- The owner watches :5173 live: one consistent edit per file (a half-applied edit blanks the canvas).
- Machine: `uv run`; `npm --prefix frontend run dev|test`; the Bash tool fails over ~8 KB (scripts to files);
  cp1252 console; LF newlines; `grep -c` exits 1 on zero matches; `git commit -F -` fails, use a file.
- **Do not merge or delete** the sealed audit branches (MANUAL_TODO §2) or `claude/blissful-poitras-2cbbd3`.

## At close (orchestrator)
Core diff first, then tests. Board row 38 ☑ with the subagent's model; `progress.py`; the suite backgrounded,
merge gated on its EXIT line; D188; RESUMING (≤ 120) and this file for **S39 (V2, Opus)**; `MANUAL_TODO.md` row
`s38` with `s37`'s SHA; merge `--no-ff`, push, `verify_clone --ref main` on a quiet machine.
