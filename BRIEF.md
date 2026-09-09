# BRIEF — for S17: the bulge stage and M_• (§5d; Opus, a gated build)

S0–S10 are closed; S11–S16 integrated, fixed and decided (D99–D120); S16 built the extended
component as the high-j tail of the halo's angular momentum (D119). Open per RESUMING.md, read
RULES.md, then this; §11 is the register (30 open). Branch `session-17`; your decision is **D121**.

## What S16 left you, and the numbers you start from

- **Row 3 reads 252.9**, high by 2, a miss under debt #11 whose prediction is *you*: the bulge
  is worth −5 to −8 km/s at R₀ (D110's probe: a Hernquist spheroid drawn from the stellar disc
  in proportion; a flat disc rotates faster than the same mass in a sphere). **Re-probe first**
  — D110 was read on the S13 halo (uncontracted, z_f 2.5); the halo now contracts around the
  total and responds to what you move (`halo.contracted_halo(..., enclosed=...)`). Below 245
  the record says debt #46's invariant is too weak, not too strong.
- Rows 10–13 are yours: 10 reads 3.70e10 (passes only because 11 fails high at 1.30e10, the
  cancellation D110 names), 12 and 13 are not-yet-computable, 14 has a zero-width target
  (#17: enter the source's uncertainty first, or it stays "no testable target"). Row 18 is
  M_• as a derived mean plus a seeded residual (ruling 10, GALAXY_INPUTS.md §13): statistical.
- The stellar disc is 5.00e10 with fitted R_d 2.49; the tail took 7.6% of the budget beyond
  12 kpc and the halo's share at R₀ is 163.3 (r_i/r_f 1.47). Gas 8.55e9, hydrogen 6.24e9.

## The contract, and the one design trap

1. **Where the bulge enters.** `v_tangential_sun` (row 3) is computed in `sfh` off stars, gas
   and the halo's scalar; two stages may not publish one field (preflight). Either the bulge
   stage runs *before* `sfh` and `sfh` reads its profile (then its mass cannot be a fraction
   of the stars `sfh` has not built yet — derive it from the budget, or from the bar's inner
   disc, §4's "mergers + bar buckling"), or it runs after and republishes nothing kinematic —
   in which case row 3 cannot see it. Decide before writing a line; D110 drew it from the disc
   in proportion *in a probe*, which a stage cannot do without a fixed point (rule A1).
2. **The halo contracts around the total baryons** (S16): give `enclosed` the spheroid too, on
   the halo's mesh, or the response is computed around a disc that no longer exists.
3. **What is derived and what is seeded** (A10): bulge mass and fraction derived; M_• mean from
   M–σ (Ho 2014 eq. 2, §13) with the residual seeded by the classical fraction (0–25%, BHG16).
   Row 14's σ is a Hernquist virial estimate — a derivation, with its assumption in the about.
4. **The gate** (§5d): rows 10, 12, 13 inside; row 11 off its cancellation; 14 and 18 statistical; row 3 re-read.

## What the instruments will tell you, and what they will not

- `uv run python -m galaxy.specs`: exit 0 means every failing row is a recorded miss,
  nothing drifted across its width, and every stage was profiled. Never widen a target
  (B5); record a miss with a prediction. A miss that starts passing fails the run.
- Probing: a constant via `tests/test_audit.py::with_constant`; a profile via `sfh.infall_profile` /
  `halo.disc_enclosed_mass` substitution (D114); a stage's compute via `object.__setattr__(S.SFH,
  "compute", fn)` — the Stage holds its own reference; patching the module does nothing (S16).

## Traps

- **Every pin that reads the potential or the stellar surface density moves**: test_halo,
  test_sfh, test_audit (#12, #28, #41, #42, #44, #45, the thick-disc probe), test_chemistry_dtd
  (f_esc 0.7536), test_spec's SUMMARY/FAILED/DEBTS and its row 20 regex, rows 6/7/9/16/17. D119
  lists the S16 set. Re-pin with the old number beside the new; refit `NET_YIELD` (0.0117) and
  `WIND_SPEED` (993) by bisection to solar at R₀ if the gas at R₀ moves (B10, debt #43).
- Row 7 (simple) is a recorded miss since S16 (1126 > 1080, #19) and row 6 advanced 384 (#42);
  the thick disc rows are S18's — do not tune the heating constants.
- The full suite outlasts the Bash tool's 10-minute cap: run it in the background with the exit
  status appended to its log, and gate the merge on that status (D115, D120). Scratch scripts
  `s17_<what>.py`; models register on `import galaxy.models`; `uv run python` only on Windows.
- **Do not merge or delete `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`**.
  New fields need no viewer preview from you; S19 owns previews (§5d).
