# BRIEF — for S31: BUILD_II Phase 7, dust that radiates (Opus subagent)

**For the orchestrating session.** S30 closed and merged (D179); open `session-31` from `main`. Hand
an Opus subagent, in a worktree (`git checkout session-31`, `git config --worktree core.hooksPath
tools/hooks`), this file, `BUILD_II.md` Phase 7, `RULES.md`, `RESUMING.md`'s "Writing a stage",
`RENDER_PHYSICS.md` §§3–4 and §7, `stages/ism.py` (P, f_H₂, dust-to-gas, Σ_dust, A_V; D163),
`stages/light.py` (Σ_L, the band sums, the ionizing budget). It neither pushes nor writes DECISIONS.md.
**Rulings made here (D113):** (a) the three dust constants — R_V, the V albedo and the scattering
asymmetry g — are SOURCED from one dust model read at the source (NEEDS SOURCING: Draine 2003 ARA&A
41, 241 Table 4 / Weingartner & Draine 2001 for R_V = 3.1; a read-only agent fetches the values
verbatim), the Milky Way R_V = 3.1 grain model the ruleset and any other R_V the named alternative;
(b) the thermal emission is a modified blackbody with a sourced emissivity index β (Planck 2014 or
Draine & Li 2007 — read it) and the dust temperature from the heating balance, not from a fit; (c) the
PAH fraction's metallicity dependence enters only if a source is read (Draine et al. 2007 SINGS; Engelbracht
et al. 2008), otherwise a constant fraction with the dependence a debt.

## What to build (BUILD_II Phase 7, reconciled: D163's ism stage exists; this is the extension)
- **Scattering**: `dust_albedo_v`, `dust_scattering_asymmetry`, `extinction_ratio_r_v` as level-0
  constants with citations (three constants, not fields); publish what the viewer needs to light a dust
  lane's rim: the scattered fraction per line of sight is the viewer's integral, the constants are the
  model's (D5). Say in the report what V2 will read.
- **Thermal emission**: `dust_temperature`(R) from the heating balance — the light absorbed per unit
  dust mass at each radius from the `light` stage's Σ_L and the ISM's τ_V — and
  `dust_infrared_surface_brightness`(R), a modified blackbody at that temperature with the sourced β;
  the total infrared luminosity as a scalar.
- **PAH**: `pah_fraction`(R) and the radiation field `radiation_field_g0`(R) (G₀ from the young light,
  a sourced normalisation — Habing 1968 / Draine 1978; read it), coupled to Z(R) by ruling (c).
- **The energy-balance test (the gate, RENDER_PHYSICS §7)**: total ultraviolet + optical light absorbed
  equals total infrared emitted, per radius and integrated, asserted in the suite with the tolerance
  measured. This is the class of test D163's factor-162 extinction defect never had.
- No new inputs (A2, A4). New units (e.g. `Lsun/pc2` exists; check `K`, `1/s`) via `core/units.py` with
  a line in the report. About lines must not name constants (D5). Both models publish everything (the
  dust reads shared fields), so nothing is optional.
- No acceptance row unless its target has a source with an uncertainty (D100, #17): the Milky Way's
  total infrared luminosity or dust temperature only if a source quotes one — propose row 32 (after
  S30's 30–31) with its citation, or publish and leave it to Audit III.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–31 unmoved
(15 = 5.20971 recorded miss #80; 29 = −7.914); the energy balance asserted per radius and in total;
the dust temperature finite and between 10 and 60 K everywhere the disc has dust (a sanity assertion,
not a target); existing pins untouched unless one moves, then the old number in the comment; new tests
on the coarse grid where the claim allows; if `ism` or `light` cost moves, `tools/timings.py` re-run.

## Traps
- `dust_extinction_v` is published per (R) and the viewer subtracts it per line of sight (D167): do not
  change its definition; add beside it.
- Every `model`-parametrised test runs for `basic` and `azimuthal`.
- Machine: `uv run` only; the Bash tool fails over ~8 KB; cp1252 console (`encoding="utf-8"`, LF
  newlines); `grep -c` exits 1 on zero matches; long runs backgrounded with `EXIT=$?` on the log.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2.

## At close (orchestrator)
Core diff first, then the tests. Board row 31 ☑ with the subagent's model; `progress.py`; the suite
backgrounded, merge gated on its EXIT line; D180 with rulings (a)–(c), the energy balance's numbers, the
dust temperature profile; RESUMING (≤ 120) and this file for **S32 (Phase 8, clouds, Fable)**;
`MANUAL_TODO.md` row `s31` with `s30`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
