# BRIEF — for S28: BUILD_II Phase 3, photometric rows, the ionizing budget and winds (Opus subagent)

**For the orchestrating session.** Open `session-28` (main checkout stays on `main`); hand an Opus
subagent, in a worktree (`git checkout session-28`, `git config --worktree core.hooksPath tools/hooks`),
this file, `BUILD_II.md` Phase 3 (reconciled: the isochrone ruling is D164's, PARSEC), `RULES.md`,
`RESUMING.md`'s "Writing a stage", `stages/photometry.py`, `light.py`, `tools/fetch_parsec.py`. It
neither pushes nor writes DECISIONS.md; it commits on the branch and reports the instruments' numbers
verbatim. Debts from #82, decisions from D177; MANUAL_TODO's `s27` row takes S27's merge SHA.
**Two rulings made here, before any number is read (D113):** (a) **Q(H⁰)** is a sourced tabulated
q₀(T_eff) calibration for O and early-B stars (NEEDS SOURCING: Sternberg, Hoffmann & Pauldrach 2003;
Martins, Schaerer & Hillier 2005 — a read-only agent fetches the table's rows; nothing from recall),
with the blackbody integral above 13.6 eV the *named alternative* the tests compare against; (b) the
rows judge **intrinsic** light against BHG16 Table 2 only if the table's own caption says its magnitudes
are extinction-corrected — read it first and put the answer in each row's note.

## What to build
- **The table gains bands.** `tools/fetch_parsec.py` already asks CMD for UBVRIJHK and keeps four columns;
  keep the band magnitudes and regenerate `parsec_isochrones.npz` (a network fetch; raw tables stay out).
- **Per-band light per unit mass formed** integrated along every isochrone, the way `light.py` did for
  bolometric light, so galaxy-level numbers come from the *field* (the whole history), not the sample.
- **Publish**: galaxy-level `absolute_magnitude_b`, `absolute_magnitude_v` (the other bands as
  scalars), `colour_b_v`, `mass_to_light_v`, `photometric_scale_length` (fitted to Σ_V(R), not the
  mass); per star `star_magnitude_v` at least. Every about line without a constant name (D5).
- **The ionizing budget**: `star_ionizing_photons` per star (Q from L and T_eff by ruling (a)) and the
  population integral `ionizing_photon_rate`(R). State what fraction of Q the table cannot see: the
  youngest isochrone reaches 64 M☉ at 4 Myr and heavier stars are NaN.
- `star_wind_luminosity` (½ Ṁ v_∞², NEEDS SOURCING: Vink, de Koter & Lamers 2001); a Wolf–Rayet flag
  declared as a **stated proxy** (hot, luminous, post-main-sequence, high initial mass).
- **Rows 25–28** in `spec.py`: M_B −20.70, M_V −21.37, B − V 0.73, Υ_V 1.70 `[verified: BHG16
  Table 2]` — the uncertainties are the table's to state (a zero-width target is untestable, D100,
  debt #17); delegate the read of the table itself, take ugriz and the other colours from it, and
  note its caveat that SDSS magnitudes and colour indices use different calibrations.
- **The input-sweep instrument** for Tully–Fisher: a row judged over a sweep of `halo_mass`, not seeds
  (B1: instrument first; the B-band zero point and slope NEED SOURCING). If the sourcing does not
  close, build the instrument and leave the row not-yet-computable with the reason in its note.

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; every new row reads
the same in both models (the light is radial); a failing new row is a recorded miss with a debt, a
reason and a prediction, never a widened target; rows 1–24 unmoved (15 = 5.20971, #80); the per-band
integrals reproduce the bolometric one with a stated bolometric correction (assert it);
`tests/test_photometry.py`'s pins re-pinned with the old number in the comment.

## Traps
- Every `model`-parametrised test runs for `basic` and `azimuthal`; keep new tests on the COARSE grid.
- The catalogue's `star_luminosity`/`star_temperature` are looked up inside `materialise` (D60): a new
  per-star column follows the same path, every ring and sector whatever a request asked for.
- The brightest-N mode (D168) ranks by bolometric luminosity; report whether it should rank by
  `star_magnitude_v` and leave the switch to the orchestrator.
- `tools/timings.py` has a row per route; a new route needs a row and `tests/test_timings.py` pins them.
- Machine: `uv run` only; the Bash tool fails over ~8 KB; cp1252 console (`encoding="utf-8"`, LF
  newlines); `grep -c` exits 1 on zero matches; long runs backgrounded with `EXIT=$?` on the log.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp` (MANUAL_TODO §2).

## At close (orchestrator)
Read the core diff first, then the tests. Board row 28 ☑ with the subagent's model; `progress.py`; the
suite backgrounded, merge gated on its EXIT line; D177 with rulings (a) and (b), the rows' numbers in
both models and the table's provenance; RESUMING (≤ 120) and this file for **S29 (Phase 4, Opus)**;
`MANUAL_TODO.md` row `s28` with `s27`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
