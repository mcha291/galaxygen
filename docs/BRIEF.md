# BRIEF — for S48: the bright-end-complete catalogue and the per-object filter response (the pin lifted for these)

**The state (2026-10-01).** S47 is merged (D199): the tuning panel (the field view's display choices as sliders, today's
values as defaults, `frontend/src/galaxy/tuning.ts`) and `docs/VIEWER_TASKS.md`, the one list of what remains for the
viewer (T1–T23). The owner reviewed building up from the "brightest" view, was shown that its stars are the brightest of
a one-in-10⁵ number sample (the top 3 162 carry 86–94 % of a pool whose light is 10⁻⁵ of the galaxy's and is not
converged at the bright end), and ruled: **"lift the pin for those two and implement them first"** — T21 the
bright-end-complete selection and T2/T3 the photometric points with single counting. Everything else in the model stays
pinned. The owner's servers run on :8017 and :5173; never stop them. T1 (the display defaults) waits on the owner's
slider combination.

## What S48 does (numbers from #125, D200, row 38; the design is the session's ruling, written before code moved)
1. **D200, the design, first commit.** One decomposition: `M(R, isochrone age, metallicity)`, the mass formed per pc²,
   from the same step weights the light stage uses (`photometry.steps_over` is linear in the per-isochrone table), so
   every linear quantity — light, stars above a luminosity, band flux above it — is `M` times a per-isochrone table and
   the totals reproduce `light.py` to 10⁻⁹. The bright catalogue: per level-3 child cell an **ordered Poisson process
   in luminosity** (`Γ_i` cumulative unit exponentials, `L_i = Λ⁻¹(Γ_i)`): complete above any threshold, a prefix as
   the threshold drops, per-region (D60), no rejection (B8). Ages under 20 Myr (the cluster census's window) are left
   to the clusters: the young population counted once. The bulge stays in the field. The per-object filter response:
   the field's own `stellar_response` linearised in log about a blackbody at the object's temperature, its error
   measured against the exact integral (threshold: luminosity-weighted < 0.02 mag on the broadband sets).
2. **Two builders were started at S47's close on branches cut from `session-47`** — `session-48-bright`
   (`stages/bright.py`, the stage `bright_stars`, `/api/bright`, `tests/test_bright.py`, the inventories) and
   `session-48-response` (`spectra.object_response`, `object_nu_l_nu`, the accuracy gate in `tests/test_render.py`) —
   disjoint files. Review each against its brief's gates; the luminosity function's renormalisation factors against
   the field's tables are a finding to register if any exceeds 10 % (the field's fixed mass grid on the giant branch).
3. **The wiring (after both merge; one builder, `api/service.py`):** `filters=` on `/api/bright` and `/api/clusters`
   returning each object's response per filter (clusters from `band_flux_at(age, feh)` × mass); `/api/render` takes
   `l_min` and returns `stars_unresolved` — the field's stars minus the young population (the clusters') and minus the
   old stars above `l_min`, from the same tables — with the closure asserted: unresolved + young + bright ≡ the total
   per ring and band to 10⁻⁹, and the realised census and catalogue sums within their noise.
4. **Then the viewer (S49–S50, `VIEWER_TASKS.md` §4):** the star-first mode — the bright stars and the clusters as
   points on the field's own surface-brightness scale (response over the pixel's footprint), the unresolved field
   under them, the filter sets in the mode, dust in front of each point (T20), picking.

## Gate
`tests/test_bright.py`, `test_render`, `test_graph`, `test_api`, `test_v4`, `test_spec` green; specs 12 / 20 / 5 of 37 both
models unchanged (no new row: a row on these numbers needs a blind window first, #117's lesson); `tools/timings.py`'s
new rows printed cold and warm (B2, B6); `bootstrap.py` before the full suite; the suite's own `EXIT=` line; merge,
push, tag `s48`, `ls-remote`, the MANUAL_TODO row, `verify_clone --ref main`.

## Traps
- The field's quadrature is the total; the luminosity function distributes it. Do not "fix" `population_light`'s mass
  grid in passing: it moves every photometric number and is accuracy work (pinned). Register what the factors show.
- The light stage reads [Fe/H] at the present radius, the catalogue at birth radius: the bright catalogue follows the
  light stage (the closure is with the field). Say so in the stage's about.
- A star's identity in the bright catalogue is (level-3 child, rank), a namespace of its own: it is not a row of the
  number-sampled catalogue and has no planetary system yet (a later task).
- Scripts go in the scratchpad, never the system temp directory (a stray `numbers.py` there shadows the stdlib).
- :5173 and :8017 are the owner's; a scratch check uses `prod` (:8018) after `npx vite build`, stopped after. Builders
  in parallel worktrees own disjoint files; `api/service.py` is touched by both the route and the wiring — sequence them.
