# BRIEF — for S36: BUILD_II Phase 10, mechanical feedback (Opus subagent)

**For the orchestrating session.** Open `session-36` from `main`; hand an Opus subagent, in a worktree
(`git checkout session-36`, `git config --worktree core.hooksPath tools/hooks`), this file, `BUILD_II.md`
Phase 10 (lines 697–723), `RULES.md`, `RESUMING.md`'s "Writing a stage", `RENDER_PHYSICS.md` §§2, 4, 5b, 7,
`stages/nebular.py` (S35: the HII region as columns of the cluster object, its rms density and clumping —
the **ambient density** a bubble expands into — and the volumetric-emissivity pattern), `stages/clusters.py`
(`cluster_wind_luminosity`, `cluster_age`; `per_mass_at`), `stages/systems.py` (the star columns
`star_wind_luminosity`, `star_remnant`, the per-cell machinery), `stages/supernovae.py` (the rates Phase 6
publishes), `stages/massive_stars.py`, `models/level0.py` (S35's constants show the citation style),
`api/service.py` (`_clusters`, `draw()`). It neither pushes nor writes DECISIONS.md. Debts from #102,
decisions from D185; MANUAL_TODO's `s35` row takes S35's merge SHA. **Rulings made here (D113):**
(a) **the wind bubble is Weaver et al. 1977's** similarity solution — R(t) = 0.76 (L_w/ρ₀)^{1/5} t^{3/5} `[recall]` in
its own units, the shell's velocity and the hot interior's pressure from the same solution — NEEDS
SOURCING: a read-only agent fetches eqs. 21 (radius) and 22 (velocity) and the shell density enhancement
from Weaver, McCray, Castor, Shapiro & Moore 1977, ApJ 218, 377 (ADS scan) or from a review that quotes
them with attribution; nothing enters from recall; (b) **the ambient density** is the HII region's rms
density from S35 (`hii_electron_density`, per cluster) and, for a single star's bubble, the cloud's mean
density at that star's cell if it is inside a cloud, else the ISM's midplane density from `ism` — state
which and why; (c) **supernova remnants are the late state of the same object**: the Sedov–Taylor
solution R = ξ (E t²/ρ)^{1/5} with ξ sourced (Sedov 1959 / Taylor 1950 give 1.15 for γ = 5/3 `[recall]` — read it in a
source, e.g. Draine 2011 or Ostriker & McKee 1988), E = 10⁵¹ erg per event `[recall]` sourced before entry, the count per cell
from Phase 6's rates × the cell's area × the visible age (a sourced radiative-phase transition or a stated
guess with the debt); (d) **per star as well as per cluster** — a single O star's bubble is driven by
`star_wind_luminosity` from the catalogue; a superbubble by the cluster's summed wind plus its supernovae.

## What to build
- A `bubbles` stage (cp5, after nebular; both models via BASIC's tuple) publishing per cluster (`of="cluster"`)
  `bubble_radius` (pc), `bubble_shell_velocity` (km/s), `bubble_shell_density` (1/cm3), `bubble_interior_pressure`
  or `_temperature`, `bubble_phase` (category: wind / supernova-driven / fading), and — a **new object class or
  columns on the star**: rule which. Prefer star columns (`star_bubble_radius`) for single stars so the catalogue
  stays one object per star (D60 pins hold; every table over every cell). Supernova remnants: a census per cell
  (`of="remnant"` widens OBJECTS, name the `core/` edit) with `remnant_radius`, `remnant_age`, `remnant_phase`
  (Sedov / radiative), drawn on `systems_seed` under `("remnant", cell, …)`, their expected count per cell = the
  supernova rate surface density × the cell's area × the visible lifetime.
- Volumetric contract (§4): a shell Hα emissivity in `erg/s/cm3` by Case B (`nebular.case_b_halpha` is importable)
  so a renderer draws the limb-brightened rim; [S II]/Hα is Phase 9's grid's when it arrives — do not invent it.
- **The hot phase**: the summed interior pressure or the superbubble volume fraction per radius as a galaxy
  field, connecting to Phase 6's rates (BUILD_II: "scaled up, the same mechanism gives superbubbles and the hot
  phase").
- `/api/clusters` gains the bubble columns (the same `draw()` chain); a `/api/remnants` route with a timings row.
- No new inputs; level-0 constants with citations; about lines name no constant (D5); census scalars under rule D4.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–36 unmoved (15 =
5.20971, 29 = −7.914, 30 = 0.0176069, 31 = 0.0065332, 35 = −2.008; 32–34 stay misses, 36 n-y-c); the bubble
radius against Weaver's solution at a hand-checked point (a test); the remnant census's per-region determinism
(D60); the remnants' count integrates to rate × lifetime × area (a redistribution test, §7); the 254 fields per
model bit-identical (sha256 before and after); pins moved only with the old number in a comment (test_graph
ORDER/SEEDED, test_audit's lost-scalar list, OBJECTS).

## Traps
- The Bash tool fails over ~8 KB (write scripts to files); cp1252 console (no non-ASCII prints); LF newlines;
  `grep -c` exits 1 on zero matches and kills `&&` chains; `git commit -F -` fails, use a file; `uv run` only.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2.

## At close (orchestrator)
Core diff first, then tests. Board row 36 ☑ with the subagent's model; `progress.py`; the suite backgrounded,
merge gated on its EXIT line; D185 with rulings (a)–(d) and the numbers; RESUMING (≤ 120) and this file for
**S37 (Audit III, Fable)**; `MANUAL_TODO.md` row `s36` with `s35`'s SHA; merge `--no-ff`, push, `verify_clone`.
