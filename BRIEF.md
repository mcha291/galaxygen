# BRIEF — for S18: the thick disc (§5d; Fable, a judgement session)

S0–S10 are closed; S11–S17 integrated, fixed and decided (D99–D123). S17 built the central
spheroid as the low-j end of the halo's angular-momentum distribution and M_• as a seeded
residual (D121). Open per RESUMING.md, read RULES.md, then this; §11 is the register (31
open). Branch `session-18`; your decision is **D124**.

## What S17 left you, and it is not what S16 left
- **Debt #19 is yours and every one of its rows moved the wrong way.** Row 5 is 1.18 kpc
  against 1.8–2.2 (1.27 at S16), row 7 is 1309 pc against 720–1080 (1126), row 11 is
  1.09e10 against 3–9e9 (1.30e10). The spheroid took 13% of the budget out of the disc,
  so Σ(R₀) fell and every scale height rose. Row 9 still passes, at 0.135 (0.147), and
  **it is still the cancellation** debt #19 records: row 5 too small and row 11 too big.
- **Row 2 is inside now (1.82) and it left debt #47's miss list without #47 being built.**
  Read that as a loss, not a gain: the row is no longer evidence about the threshold, and
  its own KS_NORM band straddles the window (−1σ 1.97 out, +1σ 1.73 in). §5d's gate for
  you named rows 5, 7, 9 and 11; row 2 is not in it and should not become a target.
- Row 20 is 6.03e9 against 8.0e9 and still under #47. **The derived Toomre threshold
  (α κ σ_g/3.36G, D119's probe) is the mechanism to judge with the heating**, and its numbers
  were measured on the S16 disc — re-probe on this one before believing them. Row 6 (simple)
  is 321 pc, inside but 29 pc off the *ceiling*; it was 24 pc off the floor two sessions ago
  and nothing about the heating changed (debt #42). If your radial heating lands row 7, show
  that row 6 landed on σ_z and not on the Σ it divides by.

## What is different about the model since you last read it
1. `stellar_mass_total` is the disc's stars **plus the spheroid** — rows 10 + 11 + 12, which
   is what row 1's target always meant. The populations sum to `stellar_mass_total −
   bulge_stellar_mass`, and several tests assert exactly that. Do not "fix" one of them.
2. The halo publishes four bulge scalars and contracts around disc + tail + spheroid. Anything
   that changes what the disc holds changes the contraction; read `halo_circular_velocity_sun`
   (163.2) after any budget change. `nucleus` is a stage at checkpoint 1 drawing `world_seed`:
   a seed binds at its earliest reader's checkpoint and `graph` requires §3's hypothesis.
3. `NET_YIELD` 0.01184 and `WIND_SPEED` 982.2 — refit by bisection to solar at R₀ if the gas
   at R₀ moves (B10, debt #43), and say by how much even when it is 1%.

## The gate (§5d)

Rows 5, 7, 9 and 11 inside together in the simple model, with row 9 **not** on a
cancellation — judged by a sweep of the merger's `gas_fraction` that leaves it inside, not by
a single reading. Rows 2 and 20 are judged with the threshold if you take it; if row 9 cannot
be restored with the threshold derived, debt #47 says the split criterion is what is wrong
(#19), not the threshold.

## Traps
- **Probe before build, and re-probe on this disc.** S13, S14 and S17 each found the
  register's stated lever had the wrong sign or magnitude; S17's bulge was worth 1.6 km/s
  against a recorded 5–8 because D110's probe was read on a different halo (D121).
- **A miss that starts passing fails the run** (debt #29). Remove it *and write down why it
  passed* — S17 had two, and neither passed for the mechanism its debt named.
- Every pin that reads the potential or the stellar surface density moves: test_halo,
  test_sfh, test_audit, test_chemistry, test_chemistry_dtd, test_vertical, test_systems,
  test_spec's SUMMARY/FAILED/DEBTS. D121 lists the S17 set. Re-pin with the old number beside.
- Probing: a constant via `tests/test_audit.py::with_constant`; a profile via
  `sfh.infall_profile` / `halo.disc_enclosed_mass` substitution (D114); a stage's compute via
  `object.__setattr__(S.SFH, "compute", fn)` — the Stage holds its own reference.
- The full suite outlasts the Bash tool's cap: run it in the background with the exit status
  appended to its log and gate the merge on that status. Scratch scripts `s18_<what>.py`;
  `uv run python` only. **Do not merge or delete `session-10-beta`, `session-10-gamma`,
  `session-10-gamme-run-2`.** S19 owns viewer previews for S15–S18's new fields.
