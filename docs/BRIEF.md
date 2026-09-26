# BRIEF — for S35: BUILD_II Phase 9, nebular and shock emission (Fable's own row)

**For the session.** Open `session-35` from `main`; read this file, `BUILD_II.md` Phase 9 (lines 645–690),
`RENDER_PHYSICS.md` §§2, 3, 4, 6, 7 (components not colours; the line list; **emissivity is volumetric**;
clumping from the log-normal; the Hα ↔ SFR consistency rule), `stages/light.py` (`halpha_surface_brightness`
= Σ_SFR × `HALPHA_PER_SFR`, D166, which this phase turns into a check), `stages/clouds.py` (the census: mass,
size, Mach, `cloud_density_pdf_width` σ_s, metallicity, α; the per-cell pattern), `stages/clusters.py` (Q per
cluster; `per_mass_at`), `stages/ism.py` (P, f_H₂, A_V), `stages/population.py` (the PN count, for the PNLF row),
`core/units.py` (the closed vocabulary: a volumetric emissivity is a **new unit**, one line in the decision, D177).
Debts from #100, decisions from D184; MANUAL_TODO's `s34` row takes S34's merge SHA. **Three sourcing decisions
and one dependency ruling, all before a number is printed (D113):**
1. **Emissivities — grid or fits.** Rule before reading any row: tabulated photoionization grids (a
   Cloudy-derived table, a data dependency like the isochrones — e.g. a published grid with its citation,
   fetched by `tools/`) against analytic emissivity fits (no dependency; a calibration debt). Record the ruling
   and its reason in D184; the alternative stays named in the stage's docstring (B12).
2. **Case B recombination** — Osterbrock & Ferland 2006 (Table 4.4: j_Hβ / n_e n_p, Hα/Hβ 2.86 at 10⁴ K `[recall]`)
   NEEDS SOURCING: a read-only agent fetches the table values (Storey & Hummer 1995's are on arXiv/ADS and
   may be the readable source; Draine 2011 §14.2 another). Nothing enters from recall.
3. **Nitrogen** is partly secondary: its abundance does not follow [α/Fe]. Source the N/O–O/H relation
   (Pilyugin et al. 2010/2012, or Vila-Costas & Edmunds 1993) before writing one; else [N II] is not published
   and the report says why.
4. **Diffuse ionized gas**: an escape fraction of ionizing photons from HII regions and the DIG's share of Hα
   (Oey et al. 2007 "~59% of Hα from the DIG" in a sample `[recall]`; Haffner et al. 2009 review) — sourced or the DIG is
   a stated zero with the debt. The DIG is what puts a glow between the knots (BUILD_II).

## What to build
- A `nebular` stage (cp5, after clusters; reads Q per cluster or Σ_Q(R), the cloud/ISM densities, the
  abundances, σ_s): **volumetric emissivities at region scale** (per unit volume, the new unit) for Hα, Hβ,
  [O III] 5007 (4959 by the fixed ratio), [S II] 6717+6731, [N II] 6583 (6548 by ratio) — per cluster/cloud as
  object columns or per cell as the contract asks (read §4 and decide; say which in D184) — **and** the
  surface integrals at galaxy scale, each declaration saying which it is. Clumping ⟨n²⟩/⟨n⟩² = exp(σ_s²) from
  the census's own PDF width (one mechanism, two payoffs, §6). DIG as a separate component with its escape
  fraction. [S II]/Hα published as the shock diagnostic (no new field beyond the lines).
- **`HALPHA_PER_SFR` becomes a check**: the Q-derived Hα integrated over the galaxy against Σ_SFR × the
  constant, stated in the row's own text as a consistency check, not validation (the SFR is upstream).
- **Rows**: the Milky Way's integrated Hα luminosity (sourced with an uncertainty, or no row), the HII-region
  luminosity function slope (Kennicutt, Edgar & Hodge 1989 — read what it measures), the PNLF cutoff M* ≈
  −4.5 `[recall]` (Ciardullo — sourced before entry) against Phase 4's PN population. Each sourced before entry, D177's rule; rows
  from 34. No new inputs; level-0 constants with citations; about lines name no constant (D5).

## Gate
Both models pass graph, preflight, determinism; `python -m galaxy.specs` exits 0; rows 1–33 unmoved (15 =
5.20971, 29 = −7.914, 30 = 0.0176069, 31 = 0.0065332; 32/33 stay misses); **the Hα surface integral of the
volumetric emissivities equals the galaxy-scale Hα to a stated tolerance** (§7's rule); the Case B Hα/Hβ ratio
reproduced where no dust is applied; existing fields bit-identical; new tests on the coarse grid; a
timings row per new route if any (probably none: emissivities ride the region/clouds/clusters responses or
`/api/arrays`).

## Traps
- A new unit is a `core/units.py` edit *plus* a line in D184 (D177); a new object class is an OBJECTS edit.
- Do not publish spectra per cell (§3a); lines are a list of emissivities, the renderer composes.
- Machine: `uv run`; the Bash tool fails over ~8 KB (write scripts to files); cp1252 console; LF newlines;
  `grep -c` exits 1 on zero matches and kills `&&` chains; `git commit/merge -F -` fails — use a file.
- **Do not merge or delete** the sealed audit branches listed in MANUAL_TODO §2.

## At close
Board row 35 ☑ (Fable 5.1); `progress.py`; the suite backgrounded, merge gated on its EXIT line; D184 with the
four rulings, the numbers and the Hα closure; RESUMING (≤ 120) and this file for **S36 (Phase 10, mechanical
feedback, Opus)**; `MANUAL_TODO.md` row `s35` with `s34`'s SHA; merge `--no-ff`, push, `verify_clone --ref main`.
