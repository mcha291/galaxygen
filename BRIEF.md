# BRIEF — for S16: the extended component with its own timescale (§5d)

S0–S10 are closed; S11–S14 integrated, fixed and decided (D99–D115); S15 derived the
assembly epoch's default and ruled the contraction's calibration out as row 3's lever
(D117, 2026-09-09). Open per RESUMING.md, read RULES.md in full, then this. GALAXY_INPUTS.md
§11 is the register (30 open). Work on `session-16`; the close ritual applies; C2e queues tags.
**Probe before build** (§5d): S13, S14 and S15 each overturned the register's stated lever
with a fifty-line probe before writing anything (D110, D113, D117).

## What S15 found, and what it leaves S16

- `halo_assembly_z` defaults to **1.66** (2.5 until S15): the ΛCDM median for the default
  mass, c₂₀₀ 8.24 before the response, a test reproduces the arithmetic. The 2.5 had been
  validated against measurements of the *contracted* halo; `halo_concentration_contracted`
  now publishes what those measure (15.4, inside 10–18; 18.5 at 2.5).
- **Row 3 reads 260.1**, a miss under debt #11, high by 9–15 km/s. Its prediction: the bulge
  (D110, 5–8 km/s, S17) and *your* component (D114, 4–13, at z_f 2.5) close it together at
  z_f = 1.66. The contraction's calibration is not the lever: Gnedin 2011 has no (M, z) form
  (read this session), Cautun 2020's Auriga response agrees with Gnedin 2004 at R₀ to 2 km/s,
  and A = 1.6 reads 245.6 and is not adopted (D117, debt #46).
- `halo_density_sun` (0.0087 M☉/pc³) does **not** discriminate: inside the measured span at
  every epoch. v_esc(R₀) is 569, inside 530–580; `WIND_SPEED` refit 1028 → 999 (debt #43).

## The decision S16 takes — the timescale, before any constant

1. **D114's premise failed**: a share s at k R_d on the disc's own inside-out timescale buys
   row 20 with row 2 (1.98–2.45 against ≤ 1.84) because the gas arrives above the SF
   threshold. The component needs a timescale of its own; §5d names the halo's angular
   momentum arriving late as the physical candidate. Derive it, do not sweep it.
2. **Re-read D114's table at z_f 1.66 first** — it was read at 2.5 and the halo's response
   is larger now (r_i/r_f 1.50). Substitute `sfh.infall_profile` and `halo.disc_enclosed_mass`
   from a script; the repo unchanged until the timescale is decided.
3. **The gate** (§5d): rows 2 and 20 inside with rows 4 and 22 unmoved; row 3 read with it;
   `NET_YIELD` and `WIND_SPEED` refitted and recorded (B10). Rows 3 and 4 remain the check
   that the component is *high* enough in angular momentum (debt #18); #45 says a wider
   first component is the wrong answer that passes.
4. Build it in `sfh` behind `infall_profile` (D114 factored it out for this). The halo
   contracts around whatever `disc_enclosed_mass` describes — give it the component too.

## What the instruments will tell you, and what they will not

- `uv run python -m galaxy.specs`: exit 0 means every failing row is a recorded miss,
  nothing drifted across its width, and every stage was profiled. Never widen a target
  (B5); record a miss with a prediction. A miss that starts passing fails the run.
- Probing a constant: `tests/test_audit.py::with_constant`; a ruleset: `tests/test_halo.py::
  _with_contraction`; an input: `run(model, {...}, only=(fields,))`. A verdict needs a number.
- A default is a measured value or a derivation a test reproduces (D30, D117); a validation
  must compare like with like — publish the quantity the measurement measures (D117).

## Traps

- **Every pin that reads the potential moves** when the infall moves: test_halo, test_sfh,
  test_audit (#12, #45), test_chemistry_dtd (f_esc 0.7552), test_spec's DEBTS map, rows 16/17.
  Re-pin with the old number beside the new (S13's lesson); D117 lists the S15 set.
- Decisions are numbered sequentially by a test: yours is D119. §5d's audit reservation is
  now stated as counts fixed when S21 opens, not numbers.
- Name scratch scripts `s16_<what>.py` (`numbers.py` shadowed the stdlib); models register on
  `import galaxy.models`. Windows: `uv run python` only; Bash over ~8 KB fails; worktree hooksPath.
- **Do not merge or delete `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`**.
- The new halo scalars have no viewer preview; S19 owns previews (§5d), not you.
