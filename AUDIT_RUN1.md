# Audit — S10, run 1

The first of two independent audits (GALAXY_PLAN.md §5 asks for the session to
be run twice and the defect lists diffed). **Run 2 must not read this file**
before writing `AUDIT_RUN2.md`; the diff is made afterwards and goes in
DECISIONS.md. Every number here is from the instruments this run built —
`galaxy/specs/convergence.py`, `galaxy/specs/performance.py` — or from a probe
run recorded in DECISIONS.md D94–D96.

## 1. Convergence: nothing drifts

N_R ∈ {200, 400, 800}, N_t ∈ {1000, 2000, 4000}, N_z ∈ {30, 60, 120}, each
alone, both models, every published acceptance scalar `[verified: DECISIONS.md D94]`.

- **0 drifts of 54 row×axis pairs in the simple model, 0 of 57 in the advanced.**
  The largest movement anywhere is v_tan under N_t, 0.33 km/s of a 6 km/s target;
  the stellar mass moves 0.2% under N_t and 0.002% under N_R.
- N_z moves the advanced gradient by 3 × 10⁻⁷ dex/kpc: reading the halo potential
  off the first z-row as the midplane value (D89) is harmless.
- Row 20 is **untestable** on every axis (zero-width target, debt #17); rows 16 and
  17 are seeded and reported without a verdict (drift 0.05 km/s/kpc at the default
  seed).
- Rows 5, 7, 8, 9, 11 in the advanced model read 0 at every grid — converged, and
  wrong for a reason the register holds (debt #27). A sweep cannot see that.

## 2. Performance: where the time goes

Cold and warm in one fresh process per model `[verified: DECISIONS.md D95]`:

- Cold ≈ warm at every stage (ratios ~1): there is no cache to read, so the
  profile is a profile.
- **simple, 0.43 s**: systems 28%, planets 27%, sfh 16%, formation 15%, chemistry
  9%, vertical 2%, everything else under 1%.
- **advanced, 0.66 s**: chemistry_dtd **41%** (0.27 s), systems 18%, planets 17%,
  sfh 11%, formation 10%. The advanced chemistry is the one stage worth optimising
  and the profile says which: its per-timestep Python loop and 28 transport
  kernels of 400 × 400.
- **Catalogue per cell** at 20 000 stars: layout 14 ms; one cell 1.1 ms (23
  stars), nine 2.6 ms (206), every cell 116 ms (19 998). Cost is proportional to
  the stars asked for. D61's fear — every cell's streams built whether asked for
  or not — is not what the code does now; **debt #24's remainder is discharged.**

## 3. Calibration audit (rule B10)

Every constant fitted or chosen against a mechanism, re-examined against the
mechanisms that have since arrived. Verdicts: *holds* (no dependency on what
changed), *explained* (the fit is now a result of a mechanism), *flag*
(re-examine when a named thing changes), *defect*.

| Constant | Fitted against | Changed since? | Verdict |
|---|---|---|---|
| `NET_YIELD` 0.011 (simple) | no outflows | the advanced model has them | **explained**: f_esc(R₀) = 0.75 makes it (S9, debt #16) |
| `WIND_SPEED` 1010 (advanced) | a massless wind, solar gas at R₀ | — | **flag**: a mass-loaded wind changes the gas budget and the calibration with it (debt #26) |
| `PLANETESIMAL_EFFICIENCY` 0.171 | 5 % occurrence at [Fe/H] = 0, 1 M☉ | the advanced model's [Fe/H] field | *holds*: a function evaluation, model-independent; but the sampled giant fraction is 1.02 % (simple) against **1.65 %** (advanced) because the advanced inner disc is iron-rich, 19 % occurrence at 2 kpc against 2.6 % (debt #26) `[verified: DECISIONS.md D96]` |
| `MERGER_HEATING` 120 | the merger split's thick disc at ~30 km/s | the advanced split is chemical | **flag**: in the advanced model the heated old stars are counted thin (thin σ_z 22.8 against 20.1 km/s) and no row reads the kick; re-examine when the valley opens (debt #27) |
| `BAR_LENGTH_RATIO` 2.0 | a cited 1.5–2.5 | — | **defect**: row 15 passes at 4.98 kpc because 2.0 × 2.49 ≈ 5.0; a choice inside a range, not a prediction (debt #21 amended) |
| `CONCENTRATION_NORM` 4.1 | c_vir quoted, c₂₀₀ used | — | *flag*, unchanged: 10 km/s of lever on row 3 across the cited z_f (debt #12); nothing this session adds decides it |
| `GAS_DISC_SCALE_RATIO` 1.0 | two independent arguments | — | *holds* (debt #13 discharged S3) |
| `SECULAR_HEATING` 25, index 0.5 | the observed AVR at 10 Gyr | — | *holds*: set from an observation, not a mechanism |
| `DISC_MASS_SCATTER` 0.3 dex | a cited width | — | *holds*; β = 2.99 is its consequence (debt #25) |
| `migration_efficiency` 3.6 kpc (input) | a citation | the advanced tilt | *flag*: 2.5 kpc closes row 23 there (debt #28) |
| `KS_NORM`, `KS_INDEX`, `SF_THRESHOLD` | measured | — | *holds*: deliberately unfitted (row 2 is a prediction) |
| `baryon_retention` 0.35, `disc_spin` 0.0173 (inputs) | the budget; a joint fit to two rows | — | *holds* (debt #10 still wants its re-ruling) |

## 4. Defect list (to diff against run 2)

1. **Row 15 passes by construction** (`BAR_LENGTH_RATIO`), see §3.
2. **The advanced inner disc's iron reaches the planets stage**: occurrence 19 % at
   2 kpc, sampled giant fraction up 60 % over the simple model, on debt #26 alone.
3. **Row 20 cannot be judged** by any instrument: zero-width target (debt #17) —
   the model's 28 % shortfall is real (debt #18) and the table's defect hides it.
4. **`chemistry_dtd` is 41 % of the advanced run** and the only stage over a fifth
   of either model; no other stage is worth an optimisation session.
5. **The advanced model has no thick disc** (debt #27) — seven rows on one cause;
   the audit confirms it is converged and recorded, not a grid effect.
6. **The UNSET ratchet was loose**: `tests/test_registry.py` allowed one unset
   default for six sessions after the last one was set; lowered to zero this run.

## 5. Not found

No scalar moved with the grid; no recorded miss had started passing; no
constant read by no stage; no route without a cold timing; no input without a
range. The instruments that would have found each of these ran and found nothing,
which is what this section is for (rule B5).
