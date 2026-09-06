# Decisions

Every non-obvious decision, with what settled it. Appended per session; never
rewritten. Tags follow rule B14: `[verified: …]` cites something in this repo or
a named external source, `[recall]` is evidence from elsewhere, `[inferred]` is
reasoning.

## Session 0 — instruments, registry, stub second model

### D1. Top-level package `galaxy/`; the plan's `model/` is `galaxy/specs/`

**Decision.** Code lives in one importable package, `galaxy/`, laid out as
GALAXY_PLAN.md §2 shows: `core/`, `models/`, `stages/`, and the executable
specs. The specs directory is named `specs/`, not `model/`.

**Settled by.** `model/` and `models/` as sibling packages differ by one letter,
and `from galaxy.model import …` versus `from galaxy.models import …` is a
typo class that would recur for ten typing-bound sessions `[inferred]`. The plan
itself calls the directory's contents "executable specs" `[verified:
GALAXY_PLAN.md §2 layering block]`. Wherever S0_PROMPT.md or GALAXY_PLAN.md says
`model/`, read `galaxy/specs/`. `api/` and `viewer/` are not created until S6/S7.

### D2. Toolchain: uv, Python 3.14 pinned, lockfile committed, numpy 2.x

**Decision.** `uv` manages the interpreter and environment; `.python-version`
pins 3.14; `uv.lock` is committed; numpy is constrained to `>=2.3,<3`. Every
command in the docs is `uv run …`.

**Settled by.** The S0 machine had no `python` on PATH, only `uv` `[recall: S0
session observation]`. A fresh clone plus `uv sync --frozen` reproduces the
exact environment (rule C1), and numpy's Generator streams are only guaranteed
stable within a bit-generator, not across distribution-method changes, so the
environment must be pinned and drift detected — the golden-value test is that
detector `[verified: tests/test_seeds.py::test_golden_values;
galaxy/specs/determinism.py GOLDEN_*]`.

### D3. The closed unit vocabulary (gap 1)

**Decision.** 30 units in `galaxy/core/units.py`, keyed by ASCII symbol
(`Msun`, `km/s`, `dex/kpc`, `Msun/pc2` …) with a display form (`M☉`) and a
coarse dimension tag. No conversion factors. Percentages are `dimensionless`;
integer counts are `count`. Adding a unit is an edit to that file with a
DECISIONS entry; a field cannot invent one (`UnknownUnit`).

**Settled by.** Rule A8 requires a closed vocabulary; the acceptance table and
the six stages need mass, length, time, velocity, angular frequency, surface and
volume density, SFR and its surface density, log abundance and its gradient,
temperature, luminosity, magnitude, insolation, angles `[verified:
GALAXY_INPUTS.md §7; GALAXY_PLAN.md §3, §5c]`. ASCII keys because non-ASCII
look-alikes (☉ vs ⊙) are an invisible typo class in code and JSON `[inferred]`.
One surface-density unit (`Msun/pc2`) because two convertible units in a closed
set invite silent factor errors `[inferred]`. Conversion factors are factual
claims needing citations and nothing at S0 converts anything.

### D4. The kind vocabulary (gap 2): six kinds = three domains × two value classes

**Decision.** `Kind` is closed: `field`, `category_field` (grid domain);
`scalar`, `category_scalar` (galaxy domain); `column`, `category_column`
(object domain). Grid kinds declare `axes` from the closed, ordered set
`(R, t, z, phi)`; object kinds declare `of` from the closed set
`(system, star, planet, belt, moon)`; categorical kinds declare `categories`
and are unitless.

**Settled by.** The prompt's candidates — continuous scalar field, category,
per-object scalar, catalogue column — factor into *where the value lives*
(decides storage and shape) and *what kind of value it is* (decides ramp vs
palette and how a check compares it) `[inferred]`. "Per-object scalar" and
"catalogue column" are the same kind: whether objects are materialised in bulk
(systems) or on demand (planets) is a storage question, not a declaration
question. Galaxy-level scalars are fields because the acceptance table reads
them (D17). `category_scalar` exists because bulge type is a derived
galaxy-level category `[verified: GALAXY_INPUTS.md §11 ruling 10]`. Canonical
axis order makes `(t, R)` undeclarable, so a transposed array is caught by the
runner rather than rendered sideways.

### D5. Ramps: required for grid and object kinds, optional for galaxy-level

**Decision.** `Ramp(cmap, scale, lo, hi)` for continuous kinds, `Palette` (one
`#rrggbb` per category) for categorical, from a closed cmap set. A grid or
object field without a ramp is a declaration error; a galaxy-level scalar may
omit it.

**Settled by.** Rule A9: one rendering opinion, held by the declaration. A
single number is not drawn, so forcing a ramp on it would be a fake opinion
`[inferred]`.

### D6. Grid defaults (gap 3): the plan's numbers, taken; extents provisional

**Decision.** `GridSpec(n_R=400, n_t=2000, n_z=60)` as GALAXY_PLAN.md §5a
proposes `[verified: GALAXY_PLAN.md §5a]`. Provisional and flagged for the
stage that first needs them: `n_phi=360` (S4), `R_max=30 kpc` (row 20 quotes
gas mass inside 30 kpc `[verified: GALAXY_INPUTS.md §7 row 20]`),
`t_max=13.8 Gyr` `[recall: age of the universe]`, `z_max=5 kpc` with z ≥ 0 by
plane symmetry (about 5.5 thick-disc scale heights `[verified: GALAXY_INPUTS.md
§7 row 7]`), linear spacing. The grid is a runtime parameter of `run()`, never
a model constant.

**Settled by.** Nothing at S0 can measure convergence, and the plan's exponents
(0.13 in N_R against 1.0+ in N_t) are the only measurement available; the
numbers are earned or revised by `convergence.py` at S10 `[inferred]`. Keeping
the grid out of the model means the two models cannot differ in grid shape, so
cross-model field comparison is always shape-compatible, and the S10 sweep can
vary N_R and N_t independently as the plan requires.

### D7. The stub second model is named `advanced` and differs by `CANARY`

**Decision.** Two registered models: `simple` and `advanced`. Both map one slot
`stub` to the `stub` implementation, which reads constant `CANARY` and publishes
field `canary` (dimensionless, over R, equal to the constant). `simple` has
`CANARY = 1.0`, `advanced` has `2.0`. `tests/test_models.py` asserts: exactly
two models, identical stage maps, exactly one differing constant, distinguishable
outputs, and that each model's canary equals its own constant.

**Settled by.** GALAXY_PLAN.md §1 asks for a second model differing trivially so
the registry, switch and reconciliation are exercised from S0 `[verified:
GALAXY_PLAN.md §1]`. Naming it `advanced` means the switch S7 builds targets the
final name and S9 swaps the stage map, not the name `[inferred]`. A model with no
stage would pass every gate vacuously (rule B4), so the stub stage exists to
make the gates falsifiable. The canary equals a constant rather than faking a
physical quantity so it cannot be mistaken for physics. S1 deletes the stub and
moves `CANARY` (BRIEF.md).

### D8. The input registry: 12 entries from GALAXY_INPUTS.md §3, four UNSET

**Decision.** `INPUTS` holds 7 controls, 4 seeds, 1 event list, with defaults,
units, `about`, and each one's checkpoint hypothesis. `halo_assembly_z` (S1),
`inside_out_index` (S2), `migration_efficiency` (S2) and `mergers` (S3) have
`default=UNSET` with an owning session. No control has a range yet. The ceiling
of 12 counts controls only. Tests ratchet: unset defaults ≤ 4, controls without
range ≤ 7, both may only fall.

**Settled by.** GALAXY_PLAN.md §5a says the input table is §11; §11 is the
rulings table and debt register, and the table is §3 as amended by rulings 7,
8, 9 and 11 `[verified: GALAXY_INPUTS.md §3, §11; GALAXY_PLAN.md §8]`. §3 gives
no single value for `halo_assembly_z` ("z ≈ 2–3"), none for `inside_out_index`
or `migration_efficiency`, and the merger history is S3's; rule A5 wants
measured defaults and rule B9 forbids showing an invented number as one, so
UNSET with an owner is the honest state `[inferred]`. Seeds and event lists are
exempt from the ceiling `[verified: GALAXY_INPUTS.md §3 table foot]`. The
runner errors on an UNSET input only when a stage reads it (D19).

### D9. Constants are UPPER_SNAKE, per model, with units; dead constants fail

**Decision.** `Model.constants` maps `UPPER_SNAKE` names to
`Constant(value, unit, about)`. A stage lists what it reads in
`reads_constants`; preflight fails on a constant a stage reads but the model
lacks, and on a constant the model declares that no stage reads.

**Settled by.** The first smoke run rejected `CANARY` under the lowercase
identifier rule that fields, inputs and stages use; separating the patterns
means a constant can never be confused with a field `[verified:
galaxy/core/fielddoc.py CONST_IDENT]`. A constant nobody reads is a claim with
no consumer, and GALAXY_PLAN.md §2 puts constants in the model declaration, so a
constant only the advanced model's stage reads exists only in `advanced`
`[inferred]`.

### D10. Provenance is declared per field and checked per model

**Decision.** `FieldDecl.provenance` is `derived` or `seeded` (rule A10).
`graph.py` computes the truth — seeded if the stage reads a seed or requires a
seeded field, transitively — and fails on disagreement either way.

**Settled by.** Rule A10 says the model must say which; making the declaration
checkable turns a documentation rule into a failing test (rule B13)
`[inferred]`. Known limitation: a field seeded in one model and derived in
another (via an optional seeded dependency) would fail the check in one of
them; the session that first hits this decides, and records it here.

### D11. Optional fields are read only through `.get()` / `.has()`

**Decision.** A stage lists optional fields in `requires_optional`;
`ctx.fields[name]` raises `OptionalFieldAccess` for them even when the field is
present. Preflight fails a strict `requires` of an optional field, a
`requires_optional` of a field declared non-optional everywhere, and a field
published by some models but not all that is not declared optional.

**Settled by.** GALAXY_PLAN.md §2 requires readers to handle absence and
preflight to assert it `[verified: GALAXY_PLAN.md §2 model boundary]`. Absence
handling cannot be verified by reading code; making the only access path one
that returns `None` makes the unhandled case unreachable (rule B13) `[inferred]`.

### D12. Stages compute inside a restricted context

**Decision.** `Context` exposes `inputs`, `seeds`, `constants` and `fields` as
read-only views over declared names only; anything else raises
`UndeclaredAccess`. Returned fields must be exactly the declared names, with the
shape and value class the kind implies.

**Settled by.** The graph the specs audit must be the graph that runs; a stage
that quietly read an undeclared input would make `graph.py`'s checkpoint
derivation wrong without any failing check `[inferred]`. Rule B13.

### D13. Orphans are found by scanning `galaxy.stages` modules

**Decision.** Preflight imports every module under `galaxy.stages` and treats
each module-level `Stage` or `FieldDecl` (including ones inside tuples) as a
declaration that must be registered and used by some model.

**Settled by.** A global registry of declarations that fills on construction
would be polluted by every synthetic declaration the tests build, and depends
on import order `[inferred]`. Scanning is explicit, side-effect free, and the
tests point it at a throwaway package to prove it fires.

### D14. The pre-commit hook matches token shapes, not bare prefixes

**Decision.** `tools/hooks/pre-commit` refuses staged added lines matching
`gh[p]_[A-Za-z0-9]{20,}` or `github_[p]at_[A-Za-z0-9_]{20,}`. It is installed
per clone by `tools/bootstrap.py` via `git config core.hooksPath tools/hooks`,
and `tests/test_hook.py` asserts that setting (skipped under `CI`).

**Settled by.** Rule C2c names the prefixes `ghp_` and `github_pat_`, and
RULES.md, GALAXY_PLAN.md and S0_PROMPT.md all contain those bare prefixes in
prose; the first commit had to include them unchanged `[verified: RULES.md
C2c; GALAXY_PLAN.md §5 Credentials; S0_PROMPT.md deliverables]`. Real tokens
carry ≥ 36 token characters after the prefix `[recall: GitHub token formats]`,
so matching the shape catches tokens and lets prose through. Hooks are not
tracked by git, so the install is a per-clone step made unforgettable by a test
(rule B13).

### D15. `progress.py` regenerates the whole summary, and the debt count was wrong

**Decision.** The tool derives the bar, the "N / 11 sessions" count, the
"repo initialised" flag, the "Next: S<n>" pointer, and the debt counts (from the
register in GALAXY_INPUTS.md §11, struck items = discharged). At S0 close the
board's "Open debts: 9 … Discharged: 2" becomes "Open debts: 7 … Discharged: 2".

**Settled by.** The register has 9 numbered items of which 2 are struck
`[verified: GALAXY_INPUTS.md §11 register]`; 9 open + 2 discharged does not add
up, which is exactly the quiet drift the prompt asks the tool to prevent. The
same argument that generates the bar generates every other derived number on
the board `[inferred]`. If debts move to their own file, change
`progress.INPUTS` and the register header constant.

### D16. Statistical acceptance: central 95 % of ≥ 20 seeded values intersects the target

**Decision.** Rows 13, 14, 16, 17, 18 are `statistical` (debt #8). They pass
when the 2.5–97.5 percentile interval of an ensemble of at least 20 seeded runs
intersects `[lo, hi]`. Without an ensemble they are not-yet-computable.

**Settled by.** Debt #8 makes these rows statistical `[verified:
GALAXY_INPUTS.md §11 debt 8]` but no document says what passing means. Interval
intersection handles both a target with its own error bar (row 16) and a bare
value (row 14) with one rule `[inferred]`. S3/S4 may revise the criterion; rule
B5 forbids relaxing a target.

### D17. The 24 rows: field names are the contract; four rows carry caveats

**Decision.** Each `Quantity` names the scalar field the runner reads, so from
S1 on a stage publishes under exactly that name or the row stays
not-yet-computable. Row 22's interval `[−0.069, −0.049]` is the union of the two
cited measurements `[inferred]`, from the intervals in `[verified: GALAXY_INPUTS.md §7 row 22]`. Rows
20 and 21 are quoted without uncertainty and keep zero-width intervals. Rows 23
and 24 have no field yet (S2 operationalises). Row 18 is expected to miss by
about 0.75 dex and must not be re-scoped `[verified: GALAXY_INPUTS.md §3 M_•]`.
A unit or kind mismatch between a row and the published field is a `fail`.

**Settled by.** Rule C6 puts the table in `spec.py` as data; rule B5 forbids
widening; rule B9 forbids inventing an uncertainty `[inferred]`.

### D18. Seeds: `SeedSequence(seed, spawn_key=path)`, strings via BLAKE2b, streams keyed by slot

**Decision.** `seeds.child(seed, *path)` and `seeds.rng(seed, *path)` are pure
functions; string path parts hash with BLAKE2b, never `hash()`.
`ctx.rng(seed_name, *path)` prefixes the path with the stage *slot*. Three
golden values are pinned in `galaxy/specs/determinism.py`.

**Settled by.** Per-region determinism (`hash(seed, star_id)` order-independent)
follows from purity, and `check_region` tests it empirically rather than
assuming it `[verified: galaxy/specs/determinism.py check_region]`. Python
salts `str.hash()` per process `[recall: Python hash randomisation]`. Keying by
slot means two implementations of one slot draw the same numbers at a fixed
seed and differ only in what they do with them, which is what a model
comparison wants `[inferred]`.

### D19. The runner resolves only the inputs a model's stages read

**Decision.** `run()` raises `MissingInput` for an UNSET input only if some
stage in the model reads it; unread UNSET inputs are simply absent from
`Outputs.inputs`.

**Settled by.** Otherwise no model could run until S3 sets the merger default,
and rule B9 forbids substituting a placeholder number `[inferred]`.

### D20. Checkpoint hypotheses are data on the inputs and checked by `graph.py`

**Decision.** Each `Input` carries `checkpoint_hypothesis` from GALAXY_PLAN.md
§3. `graph.py` derives the actual checkpoint (earliest stage that reads the
input) and fails when both exist and differ; unread inputs are reported as
unbound, not failed. A stage may only require fields from its own or an earlier
checkpoint.

**Settled by.** The plan calls §3's grouping a hypothesis to be checked against
the audit `[verified: GALAXY_PLAN.md §1, §3]`; rule B4 says state it as a
prediction that can fail. At S0 all 12 are unbound; the S10 audit expects zero.

### D21. Every model-touching test runs per registered model

**Decision.** `tests/conftest.py` parametrises any test taking a `model`
argument over `production()` models.

**Settled by.** GALAXY_PLAN.md §7 risk 3, two-model boundary rot, is mitigated
by the stub *only if* the stub is exercised everywhere `[verified:
GALAXY_PLAN.md §7]`.

### D22. LF line endings and explicit UTF-8 everywhere

**Decision.** `.gitattributes` forces LF; every file read or write in tools
and tests passes `encoding="utf-8"`; spec entry points reconfigure stdout to
UTF-8.

**Settled by.** The hook is a POSIX `sh` script and a CRLF shebang breaks it;
the first spec report crashed on a Windows cp1252 console printing `₂`
`[verified: galaxy/specs/__init__.py utf8_stdout]`.

### D23. `BRIEF.md` has an enforced ceiling of 60 lines

**Decision.** Rule C4 says about 40 lines; `tests/test_docs.py` fails above 60.

**Settled by.** A target without a test drifts (rule C3's own argument)
`[inferred]`; 60 leaves room for a trap list without letting the brief become
a plan.

### D24. CI is one GitHub Actions workflow; S0_PROMPT.md is committed

**Decision.** `.github/workflows/ci.yml` runs `uv sync --frozen`, `pytest` and
`python -m galaxy.specs` on every push. S0_PROMPT.md is tracked as the record
of this session's brief.

**Settled by.** Rules A6 and D2 want machine checks in CI `[verified:
RULES.md A6, D2]`; the plan names S0_PROMPT.md as S0's brief `[verified:
GALAXY_PLAN.md status "Next" line]`. Editing the workflow needs a token with
workflow permission (LESSONS.md).

## Between S0 and S1 — corrections to the design documents

Not a session. Doc-only corrections arising from a design review after S0 closed;
no code changed. Recorded here so the documents' history is not silent.

### D25. The board's Model column conflated surface with model

**Decision.** The board splits into **Surface**, **Model planned** and **Model
used**. S0 is recorded as surface `desktop`, planned Fable, used Fable.

**Settled by.** "Desktop" is a place, not a model, and the column's declared
meaning was model — the same category error rule A8 exists to prevent, in the
document that argues for it `[inferred]`. *Model used* is separate from *planned*
because the S10 double run is the project's only controlled evidence on whether
model choice matters, and it is worthless if the model is recorded from intention
rather than from what ran. `tools/progress.py` is unaffected: its `ROW` regex
matches only the status and index columns `[verified: tools/progress.py ROW]`.

### D26. The binding constraint on a session is quota, not wall clock

**Decision.** Rule C2b restated: commit and push at **every completed
sub-deliverable**, not once at close. New rule **C2d**: a session that stops
early closes partially — commit, push, write what remains into `BRIEF.md`, mark
the board row ◐, and **do not merge or tag**. The split criterion moves from the
session table to the token discipline, and its signal is **iteration depth**
rather than elapsed time.

**Settled by.** The original justification named a time limit. Time is not the
constraint; usage allowance is, and it stops a session without warning and
without regard to how much was accomplished `[recall: stated by the project
owner]`. A protocol whose only close ritual is the clean one leaves a stranded
session's successor to reconstruct where it got to, which is the most expensive
failure available here `[inferred]`.

### D27. S0's result is evidence about Fable, not a comparison

**Decision.** The Fable section records that S0 ran on Fable and found a real
arithmetic error in the board it was handed (D15), while stating plainly that
this is **not** a controlled result.

**Settled by.** There is no counterfactual S0, and the session was unusually well
specified, so the observation cannot be attributed to the model `[inferred]`. The
S10 double run exists to answer this question; letting an uncontrolled result
pre-empt it would waste the one comparison the build affords (rule B4).

## Session 1 — halo & disc

Surface: web (Claude Code on the web). Model: Opus 5 `[verified: the session's own
`get_session`, `configured_model` and `last_served_model` both `claude-opus-5`]`.

### D28. `core/special.py`: I₁, K₀, K₁ from Abramowitz & Stegun, not from scipy

**Decision.** Freeman's exponential-disc rotation curve needs I₀, I₁, K₀ and K₁.
numpy ships `i0` and nothing else, so the other three are the A&S §9.8 polynomial
approximations, implemented in `galaxy/core/special.py` with golden values pinned
to ten significant figures and the Wronskian identity `I₀K₁ + I₁K₀ = 1/x` as a
cross-check that ties all four together.

**Settled by.** scipy would replace a two-package pinned environment (D2) with a
large binary dependency for four functions, and the accuracy that matters here is
2 × 10⁻⁷, which the approximations deliver `[verified:
tests/test_special.py::test_golden_values]` `[inferred]`. The alternative to the
Bessel form is treating the disc as spherical, which is wrong by more than 10 % in
v_c at R₀ — six times acceptance row 3's error bar `[verified:
tests/test_disc.py::test_freeman_beats_the_spherical_approximation]`. These are
transcribed coefficients, so a golden-value test is the instrument that catches a
mistyped digit before it looks like physics (rule B1).

### D29. Level 0 constants live in one module; only constants a stage reads exist

**Decision.** `galaxy/models/level0.py` holds `G`, `H0`, `F_BARYON`,
`CONCENTRATION_NORM`, `R_SUN` and `V_SUN_PECULIAR`; each model spreads it and adds
only what it differs on. `G` is stated as arithmetic — the IAU nominal GM☉ divided
by a kpc and by (km/s)² — and a test reproduces that arithmetic rather than
trusting the literal.

**Settled by.** Two copies of a constant is the duplicate rule A9 forbids: the one
that loses is dead and the one that wins is a bug wearing the right name
`[inferred]`. Ω_M and Ω_Λ are *not* declared, because preflight fails a model
carrying a constant no stage reads (D9) and nothing at S1 reads them — the
no-dead-constants rule doing its job rather than being worked around. `G` is
arithmetic because GM☉ is known to ten digits while G and M☉ separately are known
to four `[verified: tests/test_special.py::test_G_is_the_IAU_nominal_solar_mass_parameter]`.

### D30. λ_d's default moves from 0.0144 to 0.0173 — ruling 8's argument stands, its arithmetic does not

**Decision.** `disc_spin` defaults to 0.0173. Ruling 8's reasoning is untouched and
its default is not.

**Settled by.** This is S1's gate, run as the falsifiable prediction rule B4 asks
for, and it fails. Ruling 8 obtained λ_d = R_d√2/R_vir = 2.6 × 1.414 / 255 = 0.0144
`[verified: GALAXY_INPUTS.md §6]`. But 255 kpc is Huang+16's virial radius for
M_vir ≈ 0.9 × 10¹² M☉, and asking what overdensity that pair implies gives ≈ 95
ρ_crit — the Bryan & Norman top-hat value Δ_vir ≈ 101 for Ω_M = 0.3 at z = 0
`[recall: Bryan & Norman 1998]`, not 200 `[verified:
tests/test_disc.py::test_the_255_kpc_is_a_top_hat_radius_not_R200]`. MMW98's
relation takes r₂₀₀ `[recall: Mo, Mao & White 1998 §2]`, and this model's r₂₀₀ for
the default M₂₀₀ = 1.1 × 10¹² M☉ is 212.9 kpc. Two different radius definitions and
two different masses were mixed, so the constant was calibrated against a mechanism
the model does not implement, and rule B10 says it then has no claim on its value.
Re-derived: λ_d = √2 × 2.6 / 212.9 = 0.0173.

Keeping 0.0144 would have given R_d = 2.17 kpc — inside acceptance row 4's window,
at its edge, and 17 % below the measured 2.6 kpc, so launching with nothing touched
would not have generated the Milky Way (rule A5). What survives untouched is
everything ruling 8 actually argued: the parameter is the *disc's* spin and not the
halo's, the factor of three was a parameter confusion, and the Milky Way is typical
rather than a 1.9σ outlier — 0.0144 and 0.0173 both sit inside the λ_d = 0.01–0.03
Burkert+10 need for m_d ≈ 0.05 `[verified: GALAXY_INPUTS.md §6]`. **Recorded as debt
#10 and flagged for a re-ruling**: S1 implements a mechanism and moves a number; it
does not have standing to overturn a ruling.

MMW98's structure factors f_c^(−1/2) f_R are not modelled and are absorbed into λ_d,
which is why λ_d is an inferred effective parameter rather than a measured one. That
is the pre-existing debt #6 (adiabatic contraction), not a new one.

### D31. The "joint" fit is separable at S1, and saying so is the point

**Decision.** The fit is implemented as GALAXY_INPUTS.md §6 describes — m_d pinned
by the stellar mass, λ_d by the scale length given R₂₀₀ — and recorded as
**separable**, not joint.

**Settled by.** In the simple MMW98 form R_d does not depend on m_d at all, so the
two observables constrain one parameter each and "joint" overstates what is
happening `[verified: tests/test_disc.py::test_joint_fit_reproduces_the_defaults]`.
The coupling §6 appeals to — that λ_d and m_d must move together `[verified:
Burkert+10 via §6]` — enters only through the structure factors this model does not
carry. Calling it joint would claim a constraint the model does not have, which is
rule A3's failure mode one level up `[inferred]`.

### D32. `baryon_retention` stays at 0.35, and is deliberately *not* fitted

**Decision.** 0.35 is confirmed, not tightened. `stellar_mass_total` is therefore
the whole baryon budget, 5.86 × 10¹⁰ M☉, which passes acceptance row 1 at the top of
its window.

**Settled by.** `baryon_retention` names the fraction of f_b M₂₀₀ the galaxy kept —
stars *and* gas `[verified: GALAXY_INPUTS.md §4b]`. At 0.35 it gives m_d = 0.053,
and 0.053 × M₂₀₀ = 5.9 × 10¹⁰ reconciles row 1's 5 ± 1 × 10¹⁰ of stars with row 20's
8 × 10⁹ of gas, which is exactly what a baryon budget should do and matches ruling
9's m_d ≈ 0.055. Fitting it instead to the stellar mass alone would return 0.299 and
make rows 1 and 3 both pass — and would be tuning a parameter with a clear physical
definition to cover for a missing gas phase, leaving it with no claim on its value
the moment S2 adds one (rule B10) `[inferred]`. The miss it leaves is recorded
instead, as debt #11.

### D33. A failing acceptance row can be a *recorded miss*, and stays red

**Decision.** `spec.MISSES` maps a row to the debt it belongs to, the session that
measured it, a reason, and a prediction that could kill the reason. A registered row
still evaluates to `fail` and still prints as `fail`; what changes is that
`python -m galaxy.specs` exits non-zero only on an **unexplained** failure — or on a
registered miss that has started **passing**, because the explanation is then stale.

**Settled by.** Rule B5 says record a failed check rather than relax it, and
GALAXY_INPUTS.md §3 says row 18 is *expected* to miss by ~0.75 dex and must not be
re-scoped. S0's runner had no way to express that: any acceptance failure failed the
process, so the first honest miss would have turned CI permanently red and made every
later regression invisible `[inferred]`. The three alternatives were all worse —
widening a target (forbidden by B5), not publishing the field (row 3 would report
not-yet-computable, which is a lie about a number the model computes, rule B9), or
living with red CI (which trains everyone to ignore it). The stale check is what
keeps the register from becoming a dumping ground: an entry that stops failing is an
error, so an explanation cannot quietly outlive its cause (rule B10).

### D34. The row 3 miss is published with its size and its cause

**Decision.** `v_tangential_sun` = 256.1 km/s against 248 ± 3, a miss of +5.1 km/s,
registered as debt #11 with the prediction that S2's gas phase closes it.

**Settled by.** S1 has one baryonic component, so the ~8 × 10⁹ M☉ of gas that
extends to 30 kpc and the ~1.5 × 10¹⁰ M☉ bulge inside 1 kpc are both in an
exponential of scale length 2.6 kpc, over-concentrating mass inside R₀. Taking just
the gas back out gives 246.4 km/s, inside the window `[verified:
tests/test_disc.py::test_the_recorded_cause_of_the_row_3_miss]`. Stating the size
before S2 runs is what makes it a prediction rather than a story (rule B4). Row 3 is
not used in the fit, so it is an independent check: the fit to rows 1 and 4 predicts
a third observable to 2 %.

### D35. `halo_assembly_z` defaults to 2.5, and its consequence is what justifies it

**Decision.** Default 2.5, range 0.5–5.0.

**Settled by.** GALAXY_INPUTS.md §3 gives "z ≈ 2–3" and no single value, so the
midpoint is `[inferred]` and is not presented as measured (rule B9). What lifts it
above a guess is a check on its consequence rather than on itself: c₂₀₀ = 4.1(1 +
z_f) = 14.4, inside the 10–18 the Milky Way's own concentration measurements span
`[verified: GALAXY_INPUTS.md §4b]`. Recorded honestly as debt #12: v_c(R₀) moves
about 10 km/s across the cited 2–3, three times row 3's error bar, and the midpoint
was chosen before row 3 was computed rather than to make it land.

### D36. `halo` owns the mass budget, and the NFW profile carries only the dark half

**Decision.** The halo stage reads `baryon_retention`, publishes
`baryon_mass_total`, `disc_mass_fraction` and `halo_dark_mass`, and its NFW profile
carries (1 − m_d) M₂₀₀. The disc stage turns the baryon half into a disc.

**Settled by.** M₂₀₀ and its split are properties of the halo, and putting the split
anywhere else means two stages both know it `[inferred]`. Letting the NFW carry all
of M₂₀₀ would count the disc twice and inflate v_c(R₀) by 4.3 km/s — larger than row
3's error bar, and invisible without the check `[verified:
tests/test_halo.py::test_the_disc_is_not_counted_twice]`.

### D37. Solar-radius quantities are analytic scalars, never interpolated off the grid

**Decision.** `halo_circular_velocity_sun`, `v_circular_sun` and `v_tangential_sun`
are evaluated at R₀ directly. The halo publishes its own contribution as a scalar so
the disc can add to it without a second copy of the NFW formula.

**Settled by.** An acceptance row read off a grid would inherit the radial
resolution, so the S10 convergence sweep would move a number that has no business
moving — and rule A6 keeps N_R a quality knob, not a physics parameter `[verified:
tests/test_halo.py::test_grid_resolution_does_not_move_the_scalars`,
`tests/test_disc.py::test_solar_scalars_are_analytic_not_interpolated]`. Passing the
scalar between stages rather than importing the formula keeps one opinion in one
place (rule A9).

### D38. Grid extents confirmed; `n_phi` still S4's

**Decision.** `R_max = 30 kpc`, `z_max = 5 kpc`, `n_R = 400`, `n_z = 60` unchanged
from D6.

**Settled by.** 30 kpc is 11.5 disc scale lengths, which holds 99.99 % of the
exponential's mass, so nothing is being cut off `[verified:
tests/test_disc.py::test_surface_density_integrates_to_the_disc_mass]`. The NFW
potential is smooth on both axes at these resolutions and neither R = 0 nor z = 0 is
sampled, because the grid uses *centres*; that is what keeps K₀ and K₁ inside their
domain without a guard. `n_phi` is untouched: nothing at checkpoint 1 is
non-axisymmetric.

### D39. One new unit: `kpc.km2/s2/Msun`

**Decision.** Added to the closed vocabulary for `G`.

**Settled by.** Rule A8's vocabulary is closed and a declaration cannot invent a
unit (D3), so G either gets its unit or gets declared as something it is not.
Expressing G in the model's own length, velocity and mass units means G·M/R is a
squared velocity with no conversion factor anywhere in any stage `[inferred]`.

### D40. Sessions do not tag; tags are queued in `MANUAL_TODO.md` and applied in one batch

**Decision.** New rule **C2e**. A session's close ends at "push branch and main"
and adds a row to `MANUAL_TODO.md` carrying its `git tag` command; it also fills in
the *previous* session's merge SHA, which a merge commit cannot carry about itself.
The tags are applied by hand from a desktop checkout at the end of the build.
`tests/test_docs.py` fails if a ☑ session has no row there.

**Settled by.** S1 could push its branch and `main` and could not push a tag.
Annotated and lightweight both returned HTTP 403, and the GitHub API named the
cause: `"Write access to this GitHub API path is not permitted through this
proxy"` `[verified: the S1 session's own transcript; the same request through the
same proxy that carried the successful `main` push]`. The token the session holds
even reports `push: false` on the repository while its branch pushes succeed, so
the proxy is brokering writes under its own path policy rather than passing a
token's permissions through — which means **no credential supplied to a session
changes it** `[inferred]`. A close ritual whose last step fails every time is not a
ritual, it is a trained-in error (rule B13: when correctness depends on
remembering, move it where it cannot be forgotten — here, into a file with a test
behind it). The alternative considered and rejected was leaving the step in and
letting each session record its own failure, which is eleven identical debt entries
for one environment fact.

The board's **Tag** column now names the tag a session has *earned*. What exists on
the remote is `MANUAL_TODO.md`'s business, and it says so.

### D41. One authorised rewrite of `main`, to leave exactly one merge commit per session

**Decision.** The three commits S1 had already pushed to `main` — the S1 merge, the
tag-note commit and its merge — were replaced by a single merge commit containing
the same tree plus this correction, and `main` was force-pushed once. Rule **C2a
(never force-push) stands unamended**; this is a recorded exception, not a
precedent, and no session may take it.

**Settled by.** The project owner asked for it directly, having decided that the
per-session tag should land on one merge commit rather than a merge plus a
follow-up `[recall: stated by the project owner]`. C2a's justification is that
sessions are sequential and nobody else commits, so a non-fast-forward push is a
*signal* rather than an obstacle `[verified: RULES.md C2a]` — and that reasoning is
about a push the session did not expect. Here the rewrite is the intended act, by
the only person holding the repository, and the same "nobody else commits" fact
that makes an unexpected rejection alarming is what makes an intended rewrite safe.
Two consequences were stated before it was done and are recorded here rather than
discovered later: the merge commit's SHA necessarily changed, because a commit
cannot keep its hash when its content changes; and `s00` is unaffected, because it
points at `0bc546d`, which is an ancestor of the new merge.

The rule is left alone deliberately. Amending "never" to "never, except when it
suits" would buy one convenience and cost the rule its only useful property
`[inferred]`.

**And it cost something immediately, which is the point of recording it.** An `s01`
tag had been pushed by hand at the old merge commit while the session was still
open; `origin/main` was re-checked before the rewrite and `origin`'s *tags* were
not, so the rewrite orphaned it. The content is all in the new merge and nothing is
lost, but the tag has to be deleted and re-pointed by hand, and that is queued in
`MANUAL_TODO.md`. The general lesson is not "rewriting is bad" — the owner wanted
it — but that a rewrite invalidates **every** ref pointing into the rewritten range,
and refs include ones nobody in the session created.

## Session 2 — star formation history & chemistry

Surface: web. Model: Opus 5 `[verified: the session's own `get_session`]`. Ran on
the S1 branch rather than `session-02`, at the owner's direction.

### D42. Two stages, and the acceptance kinematics move to checkpoint 3

**Decision.** `sfh` (infall, star formation, the gas/star split) and `chemistry`
(metallicity, gradient, migration), both at checkpoint 3. `stellar_mass_total`,
`thin_disc_scale_length`, `v_circular_sun` and `v_tangential_sun` move there from
checkpoint 1. The disc stage keeps its λ_d prediction as
`disc_scale_length_spin` and its one-component `circular_velocity`.

**Settled by.** A velocity at R₀ cannot be right until the mass inside R₀ is
right, and checkpoint 1 has every baryon in one exponential by construction
(debt #11). Checkpoint order forbids a checkpoint-1 stage reading a checkpoint-3
field, so the acceptance scalars had to move rather than be corrected in place
`[verified: galaxy/specs/graph.py checkpoint-order check]`. The checkpoint-1
curve stays because GALAXY_PLAN.md §3 makes stage one's preview a rotation curve,
and stage one genuinely does not know the split `[inferred]`.

### D43. τ(R) is anchored at R₀, not at R_d

**Decision.** `τ(R) = τ₀ (R/R₀)ⁿ`.

**Settled by.** GALAXY_INPUTS.md §3 states τ₀ as "~7 Gyr **at R₀**" in one row and
the law as `τ₀ (R/R_d)ⁿ` in the next `[verified: GALAXY_INPUTS.md §3 rows 4, 5]`.
Those cannot both hold: R₀/R_d ≈ 3.1, so at n = 1 they differ by a factor of
three in every timescale. R₀ is the anchor that matches the source's own numbers —
the two-infall model §3 cites gives τ_D(R) = 1.033R − 1.267 Gyr, which is 7.2 Gyr
at R = 8.2 `[recall: Chiappini+01]`. Same reasoning fixes `inside_out_index` at
1.0: a linear τ(R) *is* n = 1, so τ₀ and n are two readings of one relation rather
than two free numbers.

### D44. A general razor-thin disc solver, because the gas disc is not an exponential

**Decision.** `disc.disc_circular_velocity` least-squares any Σ(R) onto a fixed
basis of eight exponentials and superposes the exact Freeman solution for each,
returning the fit residual with the answer.

**Settled by.** Star formation holds the inner gas near the threshold and leaves
the outer gas alone, so the profile is flat and then falling; fitting one
exponential to it gave a "scale length" of 10–25 kpc depending only on the fitting
range, and that number was feeding an acceptance row. Poisson is linear in Σ, so
superposition is exact and the coefficients may be signed without meaning anything
physical `[inferred]`. On a pure exponential it reproduces Freeman to 0.02 km/s at
R₀ — row 3's bar is 3 km/s — degrading to 2% only at the grid edge where v is
small `[verified: tests/test_disc.py::test_the_general_solver_reproduces_freeman_on_an_exponential]`.
S3's bulge and S4's thick disc need the same machinery.

### D45. `migration_efficiency` is in kpc

**Decision.** Unit `kpc`, default 3.6, range 0–8. It smooths stellar populations
with a Gaussian of width `migration_efficiency × √(age/8 Gyr)` and never touches
the gas.

**Settled by.** S0 marked the unit provisional and gave S2 the ruling (D8). A
radial dispersion has a length; leaving it dimensionless would have let a kernel
width be compared against a metallicity without any check firing `[inferred]`.
Acting on stars only is what makes it falsifiable: acceptance row 22 is measured
from young tracers and must not see it, row 23's old populations must
`[verified: tests/test_chemistry.py::test_migration_flattens_old_stars_and_leaves_gas_alone]`.

### D46. The star formation threshold is smooth, and that is numerical rather than aesthetic

**Decision.** `Ψ = KS_NORM Σ^KS_INDEX × ½(1 + tanh((Σ − Σ_crit)/(0.25 Σ_crit)))`.
The width belongs to the threshold rather than being a constant of its own.

**Settled by.** A convergence sweep, run because rule B7 says a scaling exponent
finds what a stopwatch cannot. The gas mass and the gradient converged to 0.1%
across N_R and N_t; the star formation rate wandered between 1.47 and 1.79 **with
no trend in either**, which is the signature of an artefact rather than a
truncation error. The cause is that self-regulation holds a wide annulus of gas
*at* the threshold, so with a step the integrated SFR depends on which side of it
each cell lands on. Row 2 "passing" at 1.597 was grid alignment. The smooth switch
converges the rate to 0.1% and improves the gas mass at the same time
`[verified: tests/test_sfh.py::test_the_star_formation_rate_converges]`. A
threshold in nature is not a step, so this is also the more honest law.

### D47. `NET_YIELD` is an effective yield, calibrated, and it costs no acceptance row

**Decision.** 0.011, against a nucleosynthetic 0.03–0.04.

**Settled by.** At the nucleosynthetic value the solar neighbourhood comes out at
[Fe/H] = +0.50 rather than 0.00, because the simple model has no outflows to
remove metals and GALAXY_INPUTS.md §8 makes them an advanced-model axis. The
factor of three is that missing loss. What makes the calibration defensible rather
than a fit to a check is a measurement: the gradient rows are **exactly**
insensitive to the yield `[verified:
tests/test_chemistry.py::test_the_gradient_does_not_depend_on_the_yield]`, so no
acceptance row moves when this constant does. Debt #16 applies rule B10 the moment
S9 adds outflows.

### D48. Five acceptance rows fail, and they have three causes between them

**Decision.** Rows 3, 4, 20, 22 and 23 are registered misses. Rows 1, 2 and 19
pass.

**Settled by.** Rule B5, and the fact that the causes are fewer than the symptoms
— which is what makes them worth recording rather than tuning away:

- **Rows 3 and 4, one cause (debt #13).** λ_d gives a disc scale length of 2.60
  kpc; the star formation history builds one of 3.74 kpc, because the accreting
  gas must be more extended than the stars for the model to keep the observed gas
  mass at all. Row 4 reads the fitted one — row 4 measures starlight, not angular
  momentum. Row 3 misses low at 237.2 km/s for the same reason.
- **Rows 22 and 23, one cause (debt #15).** Every gradient the model makes is
  about a third of the observed one. Reproducing −0.06 needs n ≈ 3 against a
  citation-backed n = 1. Migration is close to right: the young/old ratio comes out
  2.3 against an observed 1.75, so the error is in the gradient being flattened
  rather than in the flattening.
- **Row 20, a defect in the table (debt #17).** The target has no width, so the
  check fails for any float that is not bit-exact, and the model agrees to 3%.

**S1's prediction is falsified and the falsification is the useful part.** S1
recorded that giving the gas its own profile would bring row 3 to about 246.4 km/s.
S2 ran the mechanism and got 237.2: right direction, wrong magnitude, because the
same change that moved the gas out also broadened the stellar disc. The recorded
entry is updated rather than quietly replaced (rule B5).

## Session 3 — assembly & mergers

Surface: web. Model: Opus 5. Ran on the S1 branch at the owner's direction.

### D49. Debt #13 discharged: the infall carries the disc's own scale length

**Decision.** `GAS_DISC_SCALE_RATIO` 1.5 → 1.0.

**Settled by.** The brief named it as the first suspect and it was the right one.
S2 set 1.5 from the observed HI-to-optical ratio, which is measured between
*final* discs and not between the infall and the stars — a mis-application S2
flagged itself. Two independent arguments then agree on 1.0: MMW98 predicts the
gas that forms the disc carries the halo's angular momentum distribution and so
arrives with the disc's own scale length; and running the model back from the
*observed* final ratio picks 1.0–1.1, because star formation makes the surviving
gas more extended than the gas that fell in. The two routes to the disc scale
length now give 2.52 and 2.605 kpc `[verified:
tests/test_sfh.py::test_the_two_disc_scale_lengths_agree]`.

A sweep first established that no value satisfies every row: the structure rows
want ≤ 1.25 and the gas-content rows want ≥ 1.35. That gap is debt #18, and it is
a structural insufficiency rather than a calibration — **one knob, and the
criteria that set it disagree by more than its tolerance.**

### D50. Heating at checkpoint 2, the population it sorts at checkpoint 3

**Decision.** `assembly` (checkpoint 2) publishes gas delivery and the σ_z a star
born at time t carries today; `vertical` (checkpoint 3) sorts stars into thin and
thick and computes scale heights.

**Settled by.** GALAXY_PLAN.md §3 gives stage 2 the preview "edge-on view showing
the thick disc appear", but checkpoint 2 runs before star formation and there are
no stars there to heat `[verified: galaxy/specs/graph.py checkpoint-order check]`.
§1 calls the §3 grouping a hypothesis to be checked against the audit, and this is
it failing usefully: the *heating* is assembly's and the *population* is not.

### D51. The gate passes, and it passes on two errors cancelling

**Decision.** Row 9 reads 0.103 inside its 12% ± 4%, and is recorded as a
compensated pass, with rows 5 and 11 registered as misses under debt #19.

**Settled by.** The thick disc comes out at 1.17 kpc against 2.0 and
1.07 × 10¹⁰ M☉ against 6 × 10⁹. Those are not independent of the gate: raising the
merger's `gas_fraction` to bring the mass into range drives row 9 from 0.103 to
0.015, because a thick disc this centrally concentrated sheds surface density at
R₀ far faster than it sheds mass `[verified:
tests/test_vertical.py::test_the_gate_passes_on_two_errors_cancelling]`. Reporting
the gate as met without this would be the exact failure rule B3 describes — a
check that passes because it takes the one path immune to the defect. Row 5 is the
prerequisite: with the right extent the mass and the ratio can be right together.

### D52. Ruling 11 implemented: the merger *is* the second infall

**Decision.** Each `MergerEvent` carries `gas_fraction`, the share of the
outstanding baryon budget it delivers. `sfh` runs two accretion episodes on the
same inside-out timescale, the second starting at the last major merger.

**Settled by.** Ruling 11 dissolved `second_infall_onset` by putting a
`gas_fraction` on the events `[verified: GALAXY_INPUTS.md §11 ruling 11]`, which
only means something if the event delivers the gas. It reproduces Chiappini's
two-infall structure from the merger list rather than from an input naming an
onset, and it fixes a defect S3 found on the way in: with a single infall the
model formed 56% of its stars before the merger epoch against a 12% thick-disc
target. It is now 20%. A first attempt delivered the gas as a burst over the
merger's own crossing time and drove the SFR to 0.64 — the second infall needs its
own long decay, not a delivery.

### D53. Debt #9 answered by establishing it cannot be answered here

**Decision.** The α-bimodality test moves to S9, and the split criterion must move
with it (debt #20).

**Settled by.** Two independent reasons, either sufficient. [α/Fe] needs two
nucleosynthetic channels with different delay times, and instantaneous recycling
collapses them into one — the model has a single abundance and no α–Fe plane in
which anything could be bimodal, so a null result from it would be a reading of an
instrument that cannot detect the signal (rule B3). And the model *defines*
thin/thick as "born before the last major merger", so the merger-free control has
no thick disc by construction `[verified:
tests/test_vertical.py::test_no_major_merger_means_no_thick_disc]` and cannot be
evidence about whether a merger is needed. The second is the more serious and is
recorded separately as debt #20.

### D54. Two constants corrected from the measurements they name

**Decision.** `SECULAR_HEATING` 20 → 25 km/s. `h_z = σ_z²/(2πGΣ)`, not `σ_z²/πGΣ`.

**Settled by.** The age–velocity dispersion relation runs from about 20 km/s at
5 Gyr to 25–30 at 10, and the constant is defined at 10 Gyr; it had been set from
the 5 Gyr end, leaving the thin disc half its observed thickness. σ_z(thin) is now
20.1 km/s and row 6 passes. The factor of 2 is the self-gravitating isothermal
sheet's, and S3's own brief wrote the relation without it — which would have made
every scale height twice too large `[verified: galaxy/stages/vertical.py]`.

## Session 4 — pattern: bar and arms

Surface: web. Model: Opus 5. Ran on the S1 branch at the owner's direction.

### D55. Two stages at checkpoint 4, because provenance is derived per stage

**Decision.** `bar` (derived: half-length, shear rate, disc dominance) and
`pattern` (seeded: corotation radius, pattern speed, pitch angle, arm
multiplicity), both at checkpoint 4.

**Settled by.** `graph.py` computes provenance for a whole stage — a stage that
reads a seed publishes seeded fields, all of them `[verified: galaxy/specs/graph.py
provenance block]`. But the bar's *length* has no draw in it while its *pattern
speed* does, and acceptance row 15 is pointwise where 16 and 17 are statistical.
Declaring the length seeded would be a false label on a reproducible number, and
rule A10 exists precisely to stop that vagueness. Splitting gets both labels right
with the machinery that already exists. **The alternative — per-field provenance —
is a contract change**: a field would have to declare which seeds it depends on,
and every existing declaration would need revisiting. That belongs to the S10
audit, and it is the same seam D10 flagged from the other side.

### D56. The pitch draw uses `pattern_seed`, not `world_seed`

**Decision.** `pattern_seed`, as the registry and GALAXY_PLAN.md §3 have it.

**Settled by.** GALAXY_INPUTS.md §5 says the pitch dispersion comes from
`world_seed` `[verified: GALAXY_INPUTS.md §5 ruling 3]`, and it cannot: rerolling
the arms would then invalidate every checkpoint from 1 onwards, when the entire
point of per-stage seeds is that rerolling stage 4 invalidates 5 and 6 and nothing
earlier `[verified: GALAXY_PLAN.md §3 locking]`. `graph.py` would also fail the
checkpoint hypothesis, since `world_seed` is assigned to checkpoint 1. Two
documents against one, and the two that agree are the ones the locking design
depends on.

### D57. The S-spread, run once as ruling 3 asks: 0.3% trend, 99.7% draw

**Decision.** Recorded here and not re-run. Sweeping `halo_mass` over
3 × 10¹¹–4 × 10¹² M☉, `disc_spin` over 0.010–0.030 and `halo_assembly_z` over
1.5–3.5 (27 galaxies) moves the shear rate only from **0.829 to 0.967**, which
buys a pitch-angle spread of **0.30°**. The seeded draw over 40 seeds gives
**5.12°**. So the trend holds **0.3%** of the variance and the draw **99.7%**.

**Settled by.** Ruling 3 predicted the draw would dominate and asked for the check
once `[verified: GALAXY_INPUTS.md §5]`. It is confirmed, and by a wider margin than
"weak trend" suggests — the model's rotation curves are near-flat whatever the
inputs, so the pitch–shear relation has almost no lever to pull. Two consequences,
both stated rather than left implicit. `PITCH_SHEAR_SLOPE` is doing no measurable
work, so **the model cannot falsify the pitch–shear relation** — a live instance of
rule B11, where a relation that fits the validation table is not thereby the right
relation. And `pitch_angle` is, as ruling 3 says, effectively a pure draw, so
anything downstream that reads it inherits a random component rather than a
consequence of the mass distribution. Recorded as debt #22.

### D58. `spec.py` grows a real ensemble

**Decision.** `spec.ensemble(model, fields, n)` runs the model over `n` galaxies
that differ only in their seeds; `evaluate_models` builds one per model, and
`python -m galaxy.specs` judges the statistical rows against it.

**Settled by.** Rows 16 and 17 are statistical by debt #8, and D16 fixed what
passing means — the central 95% of at least 20 seeded values intersecting the
target — but nothing built the 20 values, so both rows reported
not-yet-computable however good the model was. Every seed moves together because
the members of an ensemble should be different galaxies, not one galaxy with one
knob jiggled. Cost is 20 runs per model, about 3 seconds; if that becomes a
problem the fix is to re-run only the seeded tail, which is a `performance.py`
question (S10).

## Session 5 — systems: the star catalogue

Surface: web. Model: Opus 5. Ran on the S1 branch at the owner's direction.

### D59. The gate, measured: 10⁶ stars in 1.07 s, and there is no cache to read

**Decision.** Recorded here, as rule B2 requires the measurement to be cold.

**Settled by.** A full materialisation of 10⁶ stars takes **1.07 s** against a gate
of 10 s. The cold/warm ratio is **0.88** — the second call is *slower* than the
first, which is the honest way of saying there is no cache anywhere in the path,
so the number is not a reading of one. The full model run costs 0.48 s, of which
the published 20 000-star catalogue is about 0.2 s.

### D60. Identity, not care, is what makes a region deterministic

**Decision.** A star is `(cell, index)`, and every property is drawn at position
`index` from `rng(systems_seed, "cell", cell, property)` — one stream per
*property*, not one per star.

**Settled by.** Two properties fall out that a per-star stream would not give.
Order independence is immediate: nothing is drawn from a shared stream, so a
region generated alone is the region generated inside a full sweep. And a small
sample is a strict **prefix** of a large one, because each property's stream is
consumed only by that property — asking for 43 stars from a cell gives the first
43 of the 436 a bigger request would give `[verified:
tests/test_systems.py::test_a_small_sample_is_a_prefix_of_a_large_one]`. That is
what makes GALAXY_PLAN.md §4's clickable sample stable while the LOD ladder
materialises more underneath it. With one stream per star, drawing
radius-then-age for 43 stars would leave the stream at a different position than
for 436, and the prefix would break.

**A test found a real bug in this.** The birth-time CDF was keyed off the realised
mean radius of a cell, so a cell's ages changed with how many stars were asked
for. It is now keyed off the ring's mass-weighted radius, computed from the
density field and independent of any sample. The prefix property is exactly the
kind of invariant that fails silently, which is why it is asserted rather than
argued.

### D61. The cell grid is a measured trade-off, not a round number

**Decision.** 32 × 32 cells: 0.94 kpc rings, 11.25° sectors.

**Settled by.** Every cell costs eight `Generator` constructions — about 22 µs
each, and numpy's construction cost, not the BLAKE2b path hashing, which caching
showed to be worth only 1.1× `[verified: measured at S5]`. They are paid on every
run whether or not anything asks for that cell's stars. 48 × 48 put the catalogue
at 76% of the whole model run; 32 × 32 halves it. Going coarser makes a small
region query materialise stars it then discards, so this is a real trade-off with
an optimum that depends on what the viewer asks for, and S7 is the session that
will know. Debt #24 records the structural fix: the spec ensemble re-runs the
entire pipeline twenty times for two scalars that depend on one checkpoint, which
is rule D4's principle — no endpoint runs more of the pipeline than its answer
requires — applied to the spec runner rather than the API.

### D62. What the catalogue does not have

**Decision.** The catalogue is axisymmetric, and says so rather than being given a
modulation.

**Settled by.** S4 published a pitch angle and an arm multiplicity but no
non-axisymmetric density field, so there is nothing in the model to wind stars
into arms. Inventing a modulation here would put a spiral pattern in the
catalogue that no published field justifies — the same failure rule A4 names for
inputs, one level up. Recorded as debt #23, whose owner is whoever needs the
galaxy to look like a galaxy: GALAXY_PLAN.md §3 promises stage 4 is the "first
recognisable galaxy", and on this evidence it is not.

## Session 6 — the API: headless, fully tested

Surface: web. Model: Opus 5. Ran on the S6 branch.

### D63. The runner learned to run part of itself

**Decision.** `run(model, …, only=fields)` executes the dependency closure above
`fields` and nothing else; `run(…, resume=outputs)` continues an earlier partial
run without repeating a stage. `Outputs.ran` is what a call executed,
`Outputs.order` what is present.

**Settled by.** Rule D4 is a rule about endpoints, but an endpoint cannot obey it
if the only thing it can call is "build the galaxy". The closure is
`graph.Graph.needed_for`, which is the same edge set the graph already audits, so
what is pruned is pruned by the structure that is checked rather than by a list
somebody maintains. Two guards make the pruning safe rather than merely
convenient: inputs are owed by the stages that actually run, so a partial run is
not stopped by an UNSET default nothing on its path reads (rule B9), and a
resumed run refuses an `Outputs` from a different model, grid or input vector —
mixing two input vectors would publish a self-consistent galaxy that no input
vector generates, and nothing downstream could detect it `[verified:
tests/test_run.py::test_resume_refuses_a_galaxy_it_did_not_compute]`.

**It changes no value, and that is asserted rather than argued.** A stage is a
pure function of its declared reads, so running fewer of them cannot move the
ones that run; the test compares every field of a partial run against the full
run bitwise `[verified:
tests/test_run.py::test_a_partial_run_agrees_with_the_full_run]`.

**Debt #24 is discharged by the same eight lines.** `spec.ensemble` now names the
two scalars rows 16 and 17 need instead of rebuilding a 20 000-star catalogue
twenty times to read them: **0.162 s per member against 0.616 s, 3.8×**, and the
twenty runs 3.2 s instead of 12.3 s `[verified: measured at S6 on the default
grid, both models]`. The ensemble values are bit-identical before and after.

### D64. What the API publishes, and what it refuses to

**Decision.** Six routes: `/api` (the route table), `/api/version`,
`/api/stages`, `/api/fields`, `/api/inputs`, `/api/arrays`, `/api/region`.
They publish declarations, numbers, ramps and hashes. They publish **no
constants, no stage source and no model internals** (rule D5).

**Settled by.** The viewer has to be replaceable by reimplementing against these
endpoints (rule D5), which fixes what they must carry: enough to draw a field
and name it, and not enough to reconstruct the model. So a field arrives as its
`FieldDecl` — label, unit and its display form, kind, axes, categories, ramp,
meaningful zero, provenance, `about` — and a stage arrives as what it publishes
and reads, never as what it computes with. The boundary is checked rather than
intended: a test greps every metadata body for every Level 0 constant name
`[verified: tests/test_api.py::test_the_api_publishes_no_model_internals]`. The
one name that does appear is `CANARY`, inside the canary field's own `about`,
which is a declaration and published on purpose (rule A8).

**Controls are validated against the ranges the same endpoint publishes**, so a
viewer cannot ask for a galaxy the input table says is out of bounds, and the
range enforced is the range advertised. An unknown input is a 404 and an
out-of-range control a 400, both before anything runs. `mergers` is settable as
a JSON array because it is a list of records rather than a scalar, and each
record is handed to `MergerEvent`, which already knows what a merger may be.

### D65. `galaxy-bin/1`: one JSON header, the arrays behind it, padded to eight

**Decision.** A binary response is `GLXY`, a `uint32` header length, a UTF-8 JSON
header space-padded to an 8-byte boundary, then the arrays back to back,
little-endian, in the order the header lists.

**Settled by.** Three things, in order of how much they cost to get wrong.

- **Text loses the value.** `feh_history` is 400 × 2000 float64 — 6.4 MB of
  bytes, and JSON would be about twice that and would round every number. The
  API's job is to hand over what the model computed.
- **One request, not N.** A frame carries several arrays, so asking for three
  fields is one fetch, one dependency closure and one run rather than three of
  each. That is rule D2 and rule D4 pulling in the same direction.
- **The padding is load-bearing.** A browser reads an array as
  `new Float64Array(buffer, offset, n)`, which *throws* unless `offset` is a
  multiple of 8, so the header is padded and the alignment asserted `[verified:
  tests/test_api.py::test_the_frame_round_trips_and_the_payload_is_aligned]`.

A categorical column stays `int64`, which reaches JavaScript as `BigInt`; the
transport exports `codes()` to copy one into an `Int32Array` once, where the copy
can be seen, rather than leaving `Number(x)` scattered through drawing code.
JSON has no NaN, so a non-finite scalar is published as `null` and never as a
number (rule B9) `[verified:
tests/test_api.py::test_a_scalar_with_no_value_is_published_as_null_not_as_a_number]`.

### D66. The version hash is over content, and recomputed on every request

**Decision.** `/api/version` hashes the bytes of `galaxy/api/client/` — the
viewer's own files — and, separately, the API's own `.py` bytes. Content, not
mtime, and no caching of the answer.

**Settled by.** Rule D3 exists so that "am I running the new code" is a glance.
A file touched but unchanged must not look like a deployment and a file changed
within one second must not look identical, which rules out mtime. Caching the
hash would be worse than useless: the question is asked precisely while files
are changing under the server, so a cached answer would be a reading of the
cache (rule B2). It costs **0.9 ms** to answer, which is published below rather
than asserted to be small. A rename changes the aggregate even though no byte of
content moved, because what is served is the path as well as the bytes
`[verified: tests/test_api.py::test_the_hash_changes_when_the_bytes_change]`.

### D67. Cold timings, published (rules B2, B6) — one fresh process per endpoint

**Decision.** `tools/timings.py` measures every route in its own interpreter and
prints the numbers. Every route in `service.routes()` must appear in it, and a
test fails if one does not.

**Settled by.** A cache turns a measurement into a reading of the cache, and the
caches that matter are not only the service's own — an imported module, a numpy
array still in the allocator, a galaxy already resolved. The only way to measure
a first request is to make it the first request. Measured on the default grid
(400 × 2000 × 60 × 360):

    endpoint                 cold s   warm s    c/w      bytes  stages
    index                    0.0001   0.0000   1.96        998  -
    version                  0.0009   0.0006   1.46        402  -
    stages                   0.0003   0.0002   1.74      7,011  -
    fields                   0.0010   0.0006   1.59     43,298  -
    inputs                   0.0002   0.0001   1.76      9,091  -
    arrays: one profile      0.2655   0.0005 578.04      4,672  halo,assembly,disc,sfh
    arrays: history          0.3769   0.0143  26.29  6,401,472  halo,…,chemistry
    arrays: scalar           0.2378   0.0004 666.54      1,416  halo,assembly,disc,sfh
    region: one sector       0.2804   0.0084  33.19     18,656  halo,…,vertical
    region: whole disc       0.7232   0.3737   1.94  1,126,808  halo,…,vertical

    import + registry: 0.079-0.109 s per process, excluded from the cold column

Read three things off it `[verified: measured at S6; a second run agreed within
about 20% on the compute-bound rows and was identical in shape]`.

- **Metadata is sub-millisecond and runs no stage**, which is what rule D4 asks
  for and the `stages` column is where it is visible.
- **A region query costs what the region costs.** Nine cells of 1024 warm in
  8.4 ms against 374 ms for all of them — 44×. Cold it is 0.28 s against a full
  model run's 0.48 s (D59), because it runs six stages and not the two it does
  not need.
- **The cold/warm ratios are the argument for not checking D4 with a
  stopwatch.** 578 on one row and 1.5 on another says only which rows the galaxy
  cache serves; an endpoint that quietly ran the whole pipeline would sit in the
  same range. The stage list cannot be flattered by a cache, and that is what the
  assertions read.

### D68. The one `fetch` is counted, and then run

**Decision.** Rule D2 is asserted twice: a scan over every `.js` file in the
repository — comments and string literals stripped — must find exactly one
network call and it must be in `client/transport.js`; and a node driver imports
that module unmodified and drives a live server with it.

**Settled by.** The count is the rule S7 will actually be held to, and it is
written over the *tree* rather than over the file that exists today, so a viewer
file added next session is covered without anybody remembering to extend it
(rule B13). But a count says nothing about whether the client works. Alignment,
little-endian doubles, `BigInt` category codes and the error path are all things
a Python twin of the decoder would get right by construction and the real file
could still get wrong (rule B3), so the driver fetches `/api/version`,
`/api/arrays` and `/api/region` over a socket and its numbers are compared
against the same three requests made in Python `[verified:
tests/test_api.py::test_the_transport_decodes_what_the_server_sends]`. Where
node is absent the test *skips*, which is visible; it does not quietly pass.

### D69. A star's identity is its cell, not its position

**Decision.** The region endpoint selects cells and materialises those; the test
that checks it against a full sweep asserts containment only on the strict
interior of the window, one R-spacing in.

**Settled by.** Writing the check found the fact. A star's radius comes from
inverting its ring's CDF, and that CDF is flat outside the ring, so `np.interp`
can place a star up to one grid spacing beyond its own ring's edge — 0.075 kpc on
the default grid, 0.6 kpc on a coarse one. A star therefore belongs to the cell
that *drew* it, not to the cell its radius falls in, and a check written the
geometric way disagrees with the endpoint by one star in sixty and is right to.
The endpoint is unaffected — cells are selected by footprint and materialised by
identity — but S7 must know it before it draws a cell boundary and expects every
star inside it to have come from it `[verified:
tests/test_api.py::test_a_region_is_exactly_what_the_full_sweep_puts_there]`.

## Session 7 — the viewer: galaxy view, checkpoints, stage previews

Surface: web. Model: Opus 5. Ran on the S6 branch, restarted from `main`.

### D70. The viewer is a state machine, a renderer and a shell

**Decision.** `galaxy/api/client/` is five modules and one page. `flow.js` is the
checkpoint state machine, `ramp.js` value-to-colour, `field.js` field-to-pixels,
`stars.js` catalogue-to-screen, `view.js` what-a-checkpoint-shows — all pure
functions over plain objects — and `app.js`, the only file that touches the DOM.

**Settled by.** Rule D1 is four statements, and every one of them is a claim
about *state*: where a page load lands, what a confirm disables, what a reopen
discards, what a lock protects. Written into event handlers they would be checked
by looking at a screen, which is rule B3's failure — the one access path immune
to the defect. Written as functions they are asserted: 45 node tests run against
declarations dumped from the live API, so a registry change the viewer would
mishandle fails in the suite rather than in a browser `[verified:
tests/test_viewer.py::test_the_viewer_logic_holds]`. CI has no browser and needs
none, which is only true because the rules do not live in the DOM.

The split has a second payment. The end-to-end test drives the *client's own*
modules against a live server — the walk through six checkpoints, the region
query, the projection, the click — so what is tested is the code the browser
loads, not a Python retelling of it (rule B3 again).

### D71. The stops behind a ramp are published, and the viewer holds no colour

**Decision.** `galaxy/core/cmaps.py` holds the colour stops for the eight-name
closed vocabulary, `/api/fields` publishes them beside the declarations, and two
tests assert the client's JavaScript contains **no colour literal and no cmap
name**.

**Settled by.** Rule A9 puts the rendering opinion in the declaration, but naming
`viridis` is only half an answer — something must know what viridis is. If that
something is the viewer, then every client reimplements it and they disagree,
which is the duplicate A9 exists to prevent, one level down. So the stops moved
into `core/` beside the vocabulary they belong to, and the API serves them. The
gate is written as an absence, which is the only form that stays true: a colour
that is not in the file cannot drift from the declaration.

Two properties are enforced where they are defined rather than where they are
used. A diverging map must have an **odd** number of stops, so its middle anchor
is a defined neutral point; without that, a field with a meaningful zero is drawn
with zero half a stop off the neutral colour and nothing says so. And a name in
the vocabulary with no stops is refused at import `[verified:
tests/test_viewer.py::test_a_cmap_the_vocabulary_names_but_does_not_define_is_refused]`.

### D72. `Number(null)` is 0, and that is rule B9's failure inside a language feature

**Decision.** `numberOf()` is the one place a published value becomes a number in
the client, and it returns NaN for `null`, `undefined` and `""`.

**Settled by.** A test written while the ramp was being built. `/api/arrays`
publishes a scalar the model has no number for as JSON `null` (D65, rule B9) —
and JavaScript's `Number(null)` is `0`. Left alone, a missing metallicity would
have been drawn the exact colour of zero metallicity and read as a measurement:
the failure rule B9 is about, arriving through a coercion rather than a decision,
and invisible in every screenshot. `Number("")` is 0 as well, so an empty field
in a form is not a zero either. The fix is one function, and both modules that
turn values into pixels go through it `[verified:
tests/js/render.test.mjs "a value that is not a number is drawn as nothing"]`.

### D73. Rule D4 can be broken by the client, and was

**Decision.** `view.js` decides what a checkpoint asks for, and a scalar whose
stage also publishes object columns is **not** among it.

**Settled by.** The end-to-end test caught the viewer running the star catalogue.
`catalogue_size` is a galaxy-level scalar published by the systems stage, so
asking for it materialises the galaxy-wide sample — beside a region query that
had just carefully avoided doing that. Rule D4 says no *endpoint* runs more of
the pipeline than its answer requires; this is the same waste committed from the
other side of the wire, and no endpoint check could see it.

The rule that replaces it is derived rather than listed: the region response's
own census already says how many stars were drawn, so a scalar counting them is
never worth a stage. Nothing in the viewer names `catalogue_size`, or `systems`
`[verified: tests/js/render.test.mjs "the viewer never asks for a scalar that
would build the catalogue"; tests/test_viewer.py asserts no request the viewer
makes runs the catalogue stage]`.

### D74. The viewer is served from a directory it cannot leave

**Decision.** Any path that is not `/api/...` is answered from
`galaxy/api/client/`: `/` is `index.html`, the suffix must be in a seven-entry
media-type allowlist, and the resolved path must still be inside the directory.

**Settled by.** The viewer has to be served from somewhere, and the somewhere is
already the directory `/api/version` hashes (D3), so a stale bundle stays one
glance away. The two guards are the ones a static handler is always wrong about:
an allowlist cannot be widened by an unexpected file appearing in the directory,
where a denylist can, and resolving before comparing is what makes `..` a 404
rather than a read of `/etc/passwd` `[verified:
tests/test_viewer.py::test_the_viewer_is_served_from_its_own_directory_and_nowhere_else]`.

### D75. What the picture does not have, said by the picture

**Decision.** The face-on disc is a radial profile revolved, and the viewer says
so underneath it — in a line it derives from the declarations, not one somebody
typed.

**Settled by.** Debt #23: no stage publishes a non-axisymmetric density, so there
is nothing to wind stars into arms and the galaxy has no spiral structure.
GALAXY_PLAN.md §3 promises stage 4 is "the first recognisable galaxy"; on this
evidence it is a smooth exponential disc with a seeded sample over it, and that
is what the screen shows. Painting arms here would put structure in the picture
that no field justifies — rule A4's failure two levels up from an input, and
refused for the same reason S5 refused it in the catalogue (D62).

The note is computed: the viewer asks whether *any* published field has a `phi`
axis, and says nothing when one does. When a stage finally publishes one the
sentence disappears on its own, which is the difference between a note and a
comment `[verified: tests/js/render.test.mjs "nothing published varies with phi,
and the viewer can tell"]`.

### D76. Cold timings at S7 (rules B2, B6)

**Decision.** The viewer's two routes are measured like every other, in a fresh
interpreter each.

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0001   0.0001   1.91        940  -
    viewer: a module         0.0001   0.0001   2.01     17,409  -
    index                    0.0001   0.0000   1.87      1,087  -
    version                  0.0012   0.0009   1.36      1,050  -
    stages                   0.0003   0.0002   1.45      7,011  -
    fields                   0.0008   0.0005   1.55     44,714  -
    inputs                   0.0001   0.0001   1.68      9,091  -
    arrays: one profile      0.2173   0.0004 620.06      4,672  halo,assembly,disc,sfh
    arrays: history          0.3080   0.0045  67.80  6,401,472  halo,…,chemistry
    arrays: scalar           0.1359   0.0003 409.97      1,416  halo,assembly,disc,sfh
    region: one sector       0.2998   0.0064  46.77     18,656  halo,…,vertical
    region: whole disc       0.4911   0.2667   1.84  1,126,808  halo,…,vertical

    import + registry: 0.068-0.071 s per process, excluded from the cold column

**Settled by.** Two readings. Serving a file is 0.1 ms and runs no stage, so the
page arrives before the data it will ask for — which is why the viewer paints its
shell first and fills it in. And `/api/fields` grew from 43,298 to 44,714 bytes
when the cmap stops joined it: the whole rendering vocabulary costs 1.4 KB, once,
against a client that would otherwise carry its own copy for ever `[verified:
measured at S7; D67 has the S6 numbers for comparison]`.

### D77. A screenshot is an instrument (`tools/shot.py`)

**Decision.** A tool that starts the server, renders a path in headless Chromium
and writes a PNG. Not a test; CI has no browser and the suite does not want one.

**Settled by.** GALAXY_PLAN.md §5b calls S7 the largest quota risk in the build
because "visual work iterates blind". It does not have to be blind, and it was
not: the first render showed checkpoint one opening on `canary` — the
model-boundary probe, drawn as a flat white disc — a constant field drawn on the
floor of its box where it reads as zero, and a legend overflowing into the next
column. None of the three is visible to any assertion that was worth writing, and
all three took one look. Rule B1 asks for the instrument before the thing it
certifies; this is that, for pictures, and S8's system view is the next session
that needs it.

## Session 8 — planets and the system view

Surface: web. Model: Opus 5. Ran on the S6 branch.

### D78. The planets stage splits the way the systems stage did

**Decision.** Two stages at checkpoint 6. `formation` is derived and publishes
where giant planets are possible and when; `planets` is seeded and publishes the
systems themselves.

**Settled by.** GALAXY_INPUTS.md §12 makes the object half a seeded draw *by
construction* — the late giant-impact phase is chaotic, so there is no
deterministic outcome to have scatter about — while the occurrence of giants
across the galaxy is a function of the metallicity field and nothing else.
`graph.py` computes provenance from what a stage reads: a stage that reads a seed
publishes seeded fields (rule A10). Putting both halves in one stage would have
declared `giant_occurrence` seeded, which is false and would have been enforced
as true. S5 had the same problem and solved it the same way (`population` beside
`systems`), so this is the second instance of a pattern rather than a one-off
`[verified: tests/test_graph.py asserts giant_occurrence is derived]`.

### D79. Occurrence is not a law here. It is a threshold on a log-normal

**Decision.** Metallicity enters the planets stage exactly once — a disc's solid
mass is its mass times its metal fraction — and giant occurrence comes out as the
probability that the solids in a zone beyond the ice line clear the critical core
mass. Nothing multiplies by 10^(β[Fe/H]).

**Settled by.** Rule A3: if it can be derived, derive it. §12 quotes β ≈ 2 and it
would have been one line to write down; writing it down would have made every
later comparison circular. Deriving it instead makes β a *measurement of the
model*, published as `giant_occurrence_index`, and the measurement disagrees with
the literature in a way that turns out to be informative.

**The number is β = 2.99, and it is not free.** For a threshold on a log-normal,
the slope at 5% occurrence is fixed by the width of the log-normal alone, and
§12's own disc-mass scatter of 0.3 dex forces β ≈ 3. Matching β = 2 needs 0.45
dex. That is the whole content of debt #25: §12 cites β ≈ 2 *and* an occurrence
running 5% → 25% across [Fe/H] = 0 → +0.5, and those are different claims (β = 2
takes 5% to 50%). The mechanism reproduces the steeper one and overshoots the
endpoint, at 51% `[verified: tests/test_planets.py, and the debt register's
prediction that a disc-mass width measurement decides it]`.

**One constant is fitted and the rest are predictions.**
`PLANETESIMAL_EFFICIENCY` = 0.171 sets occurrence to 5% for a solar-mass star at
[Fe/H] = 0. Everything else follows, including the stellar-mass dependence, which
was given no data at all: around an M dwarf the model gives ~1% at [Fe/H] = 0
rising to ~20% by +0.5, bracketing the 0.96 ± 0.51% and 12.4 ± 5.4% §12 quotes
from Montet+14.

### D80. A belt is not placed. It is what a giant prevented

**Decision.** Belt edges are mean-motion resonances of the giants: the asteroid
analogue between the innermost giant's 4:1 and 2:1, the Kuiper analogue outward
from the outermost giant's 3:2. Zero inputs, zero seeds, twelve lines.

**Settled by.** §12 says so, and the Solar System is a sharp check on whether it
was done right, because nothing about either belt is in the code — only Kepler's
third law applied to two period ratios. Jupiter at 5.204 AU gives **2.06–3.28 AU**
against an observed asteroid belt of ~2.1–3.3, and Neptune at 30.07 gives a
Kuiper inner edge of **39.3 AU** against an observed 39.4 `[verified:
tests/test_planets.py::test_belts_are_where_the_giants_left_them]`. Two numbers
that were not fitted and land on top of the real ones is the strongest evidence
in this session that the derivation is the right one.

### D81. A star is named by the layout, not by an identifier field

**Decision.** `(cell, index)` reaches a caller through the *shape* of a response —
the `(cell, count)` runs a catalogue was built from — and never as a column.

**Settled by.** §12 opens a system by `hash(planets_seed, star_id)` and S7 found
that no star_id was published anywhere. Making it a column was the obvious move
and the declaration system refused it, for good reasons: an identifier has no
unit in the closed vocabulary, no meaningful zero, and an object field must carry
a ramp (rule A9) — a colour for a number nobody colours. Rather than invent a
unit and a palette to satisfy a contract that was right, identity travels beside
the columns: `Catalogue.counts`, `catalogue.star(row)`, and the same runs in the
region response for the client. `systems.cell_counts` is the single definition,
split out of `materialise`, and it is cheap enough — one `Generator` per cell, no
property streams — that naming a star costs a fraction of drawing one `[verified:
tests/test_systems.py::test_the_layout_costs_a_fraction_of_the_stars]`.

### D82. Opening a system costs a cell

**Decision.** `/api/system?cell=…&index=…` materialises that one cell, takes that
one star, and gives it planets. It runs neither materialiser stage.

**Settled by.** Rule D4, and it is the return on D81. The closure the endpoint
needs is what the *catalogue stage reads* — six stages — and then two direct
calls. Running the `systems` stage would build every cell; running the `planets`
stage would give all 20 000 sampled stars their planets to answer about one. Cold
it is **0.158 s against 0.322 s for a whole-disc region**, and warm 2.8 ms
`[verified: D84's table]`. The response is 2.8 KB.

### D83. The isolation mass is an embryo's, and a planet is what embryos become

**Decision.** Planet masses come from partitioning the disc's solids across
geometric zones, not from the isolation mass. The Hill criterion is used as §12
specifies — to *filter* — rather than to build.

**Settled by.** The first architecture used the classical isolation mass directly
and produced systems of gravel: ~0.02 M⊕ at 1 AU in this disc, three orders below
Earth. That is not a bug in the arithmetic, it is what the isolation mass *is* —
the mass of one embryo in its own feeding zone — and a terrestrial planet is the
merger of many across a much wider annulus. Zones partition the solids instead,
which conserves mass by construction, and then neighbours closer than
HILL_SEPARATION mutual Hill radii merge.

**The filter took two attempts.** Comparing neighbouring *slots* left 0.4% of
surviving pairs crowded, because a merge makes the survivor heavier and widens
the Hill radius of a pair that was already checked. Carrying the survivor forward
through the sweep is exact in one pass and leaves none `[verified:
tests/test_planets.py::test_the_stability_filter_leaves_nothing_crowded]`.

### D84. Cold timings at S8 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0001   0.0001   1.92        940  -
    viewer: a module         0.0001   0.0001   2.01     21,599  -
    index                    0.0001   0.0000   1.91      1,237  -
    version                  0.0011   0.0009   1.26      1,132  -
    stages                   0.0002   0.0001   1.78      8,381  -
    fields                   0.0007   0.0005   1.45     57,617  -
    inputs                   0.0001   0.0001   1.68      9,091  -
    arrays: one profile      0.1275   0.0002 527.59      4,672  halo,assembly,disc,sfh
    arrays: history          0.1410   0.0046  30.84  6,401,472  halo,…,chemistry
    arrays: scalar           0.0922   0.0003 307.84      1,416  halo,assembly,disc,sfh
    region: one sector       0.1775   0.0048  36.99     18,720  halo,…,vertical
    region: whole disc       0.3224   0.1669   1.93  1,126,208  halo,…,vertical
    system: one star         0.1575   0.0028  55.90      2,816  halo,…,vertical

**Read the table against itself, not against S7's.** Every row is faster than
D76's — a whole-disc region went 0.49 s to 0.32 s without anything being
optimised — so the machine, not the code, moved. What is comparable within one
run is the shape: opening one system costs half a whole-disc region and the same
six stages, `/api/fields` has grown to 57.6 KB now that it carries the planet
declarations, and metadata is still sub-millisecond with no stage behind it. A
full model run is 0.60 s, of which the planets stage is about 0.12 s.

**One measurement changed the code.** Evaluating occurrence over the 800 000-cell
history built an 800 000 × 8 array of zones and took 1.5 s of a 2.5 s run, until
the part that depends only on the star was split out (`giant_zone_share`). The
zones depend on the ice line, the ice line depends on luminosity, and metallicity
scales every zone together — so for a fixed stellar mass it is one scalar and an
elementwise operation `[verified: measured at S8]`.

## Session 9 — the advanced model

### D85. The advanced model's axes are constants, not inputs

**Decision.** The yields, the type Ia delay-time distribution and the wind
loading are `Constant`s declared in `models/advanced.py` and nowhere else. The
control count stays at 7; `NET_YIELD` moves out of Level 0 into
`models/simple.py`, because only the simple chemistry reads it.

**Settled by.** GALAXY_INPUTS.md §8 tabulates these as "inputs" and §2 lists the
same quantities as Level 0 constants; rule A4 decides between them. A supernova
yield or a delay-time index would exist whether or not this galaxy did, and none
is a property of *it*, so they are constants with recorded debt, exactly as §2
says. Preflight fails a model that declares a constant no stage reads (D29), so
the two models now carry different constant sets and the registry says which is
which `[verified: tests/test_models.py::test_shared_constants_are_shared_and_own_ones_are_read]`.

### D86. A model's own stage may require its own optional field

**Decision.** Preflight's `optional-read-strict` fires only when a stage that
strictly requires an optional field is *shared* with a model that does not
publish it.

**Settled by.** The rule as written refused every strict read of any optional
field. `alpha_fe_history` must be optional — the simple model does not publish it
— and `vertical_alpha` cannot run without it; asking that stage to handle an
absence that cannot occur in any model it is mapped in would have been a false
declaration enforced as true. The case the rule exists for is still refused
`[verified: tests/test_preflight.py::test_optional_discipline]`.

### D87. Misses belong to a model (rule A7)

**Decision.** `spec.Miss` carries a `model`; `spec.misses(name)` is what the
runner judges against; `MISSES` and `MISSES_ADVANCED` are the two views. Rows
2, 3 and 20 are shared (debt #18); rows 5, 11, 22 and 23 are the simple model's
own; the advanced model's are in `_MISSES_ADVANCED`.

**Settled by.** Row 22 passes in the advanced model and fails in the simple one.
Under a single register that is simultaneously a stale miss and a recorded one,
and the run would fail either way. The advanced model's findings are stored
separately, which rule A7 asked for before there was anything to store.

### D88. The thin/thick split is the valley, and the catalogue follows it

**Decision.** `vertical_alpha` calls a star thick if the gas it formed from had
[α/Fe] above `alpha_split`, the minimum of the [α/Fe] mass histogram between its
two modes at R₀; NaN means no valley and no thick disc. `vertical.split()` holds
the arithmetic once for both implementations. The systems stage reads
`alpha_split` and `alpha_fe_history` optionally and draws its population code by
the same criterion when they are there, so a catalogue star's population is the
vertical stage's whichever model built it.

**Settled by.** Debt #20: a split that names the merger cannot be evidence about
mergers. A fixed [α/Fe] threshold would have been a constant chosen to produce a
thick disc; the valley is derived from the distribution, and its absence is a
result (D91). `vertical_alpha.requires` does not contain
`last_major_merger_time` `[verified: tests/test_chemistry_dtd.py::test_the_split_criterion_never_names_the_merger]`.

### D89. The wind is metal-loaded, set by the escape velocity, and fitted once

**Decision.** `f_esc(R) = 1/(1 + (v_esc/WIND_SPEED)^WIND_INDEX)` of a
generation's fresh metals leave before mixing; `v_esc` is derived from the halo
potential plus the resolved baryons' midplane potential; `WIND_INDEX = 2` is the
energy-driven choice; `WIND_SPEED = 1010 km/s` is the one fitted constant, set so
the present-day gas at R₀ is solar. The wind removes no gas (debt #26).

**Settled by.** GALAXY_INPUTS.md §2: "the loading is derived per radius from
local escape velocity; only the coefficient is constant." The escape velocity at
R₀ comes out at 578 km/s against a measured 530–580, with nothing fitted to it
`[verified: tests/test_chemistry_dtd.py::test_the_escape_velocity_at_the_sun_is_where_it_is_measured]`.
With the calibration, **f_esc(R₀) = 0.75**: the factor of three between
`NET_YIELD` and the nucleosynthetic yield is now a number the model produces
rather than one it was given, and debt #16 is discharged. The two conventions
do not coincide exactly — the simple model's effective total-metal yield per unit
mass formed is 0.011 × 0.7 = 0.0077, the advanced model's retained one at R₀ is
0.0101 — because the advanced model calibrates *iron* at R₀ and a third of its
iron arrives late; that difference is the DTD, not a discrepancy.

### D90. Row 22 closes as predicted; row 23 does not, as predicted

**Decision.** The present-day gradient in the advanced model is **−0.057
dex/kpc**, inside row 22's target; row 23 stays at −0.019 and is recorded under
debt #28 with the migration width that would close it (2.5 kpc).

**Settled by.** Debt #15 predicted outflows would steepen row 22 towards −0.06.
Measured, with the mechanism switched off by its own constant: a wind with no
radial dependence (`WIND_INDEX = 0`) gives −0.043, so the wind's tilt is −0.014
and the rest — the simple model's −0.024 plus −0.019 from the delayed iron, which
the younger outer disc has received less of — is the DTD's `[verified:
tests/test_chemistry_dtd.py::test_the_tilt_is_the_wind_s_radial_dependence,
::test_iron_lags_oxygen_so_the_iron_gradient_is_the_steeper]`. The [O/H] gradient
is −0.037: iron's is steeper than oxygen's for the same reason. S2's row 23
prediction said that if row 22 steepened and 23 did not, migration was wrong
too; it fired. The young/old ratio is 3.1 against 1.75; the input default stays
the cited value and the conflict is on the register (rule B12).

### D91. Row 24 is computable, and it fails: one mode, no valley

**Decision.** Row 24 reads `alpha_sequence`, expects `bimodal_wide`, and the
advanced model publishes `single`. Recorded under debt #27 with the six thick-disc
rows it takes down (5, 7, 8, 9, 10, 11), every one at zero or at the whole mass.

**Settled by.** The mass at R₀ sits in one mode at [α/Fe] = +0.21, where the local
track lingers while a star formation history that never pauses keeps forming
stars as the delayed iron catches up; the plateau at +0.45 and the present-day
gas at +0.05 are both there, and nothing between them is a valley. Three things
were tried before recording it. A sweep over τ₀ and the merger's gas fraction:
dip depth at most 0.38, at τ₀ = 1 Gyr. Re-integrating the infall in a probe with
episode-specific timescales (1 Gyr, then 7) and the smooth episode interrupted
for 1.5–2 Gyr before the merger: depth 0.25–0.31, and the pause adds nothing.
Reading the distribution with no migration: still single. The detector was then
checked on a distribution that *is* bimodal `[verified:
tests/test_chemistry_dtd.py::test_bimodality_is_read_off_a_histogram_that_can_say_two]`,
which also found its own defect — a bump on a tail counted as a mode until a
mode was required to hold a tenth of the mass. What the register predicts is
in debt #27. Debt #9's question is answered on the way: a merger-free galaxy is
`single` too, from a criterion that never named the merger.

### D92. The scaling exponent, measured: 0.77 in N_t, against 2.04 for the naive form

    chemistry stage        N_t=500    N_t=1000    N_t=2000    N_t=4000    N_t=8000  exponent
    simple                  0.0117      0.0208      0.0407      0.0779      0.1466      0.92
    advanced                0.1051      0.1577      0.2598      0.4533      0.8794      0.77
    naive DTD (tool)       N_t=250     N_t=500    N_t=1000    N_t=2000                exponent
                            0.0052      0.0214      0.0911      0.3600                    2.04
    advanced chemistry / simple chemistry at N_t = 2000: 6.76x
    whole model, cold: simple 0.414 s, advanced 0.634 s (1.53x)

**Decision.** `tools/scaling.py` measures the exponent rather than the stage
asserting it (rule B7), and times the naive convolution beside it so the
instrument shows it can see the defect it exists to find (rule B3).

**Settled by.** The binned kernel touches `DTD_BINS = 32` shifted copies of the
star formation history whatever N_t is; the per-step part is linear and the
transport kernels (400 × 400 per age bin) do not scale with N_t at all, which is
why the measured exponent is *below* one at these grids. The naive convolution
in the tool comes out at 2.04 on the same histories — §10's 2.07, reproduced.
The multiplier is 6.8× for the chemistry stage and 1.5× for the whole model;
§10 priced the DTD at 4.9× and the coupled fixed point at ×8 on top, and there is
no fixed point here — the wind reads the potential and the histories, nothing
reads the wind — so rule A1 holds with nothing to iterate. Absolute seconds moved
with the machine and are not comparable to §10's.

### D93. Cold timings at S9 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0002   1.49        940  -
    viewer: a module         0.0003   0.0002   1.43     21,599  -
    index                    0.0000   0.0000   1.63      1,237  -
    version                  0.0015   0.0013   1.18      1,132  -
    stages                   0.0002   0.0001   1.46      8,645  -
    fields                   0.0006   0.0004   1.46     57,008  -
    inputs                   0.0001   0.0001   1.43      9,091  -
    arrays: one profile      0.0702   0.0002 320.47      4,672  halo,assembly,disc,sfh
    arrays: history          0.1102   0.0022  51.01  6,401,472  halo,…,chemistry
    arrays: scalar           0.0714   0.0002 342.90      1,416  halo,assembly,disc,sfh
    region: one sector       0.1279   0.0031  40.97     18,720  halo,…,vertical
    region: whole disc       0.2429   0.1095   2.22  1,126,208  halo,…,vertical
    system: one star         0.1273   0.0020  63.14      2,816  halo,…,vertical
    adv: history             0.3260   0.0026 124.97  6,401,480  halo,…,chemistry_dtd
    adv: alpha plane         0.3227   0.0023 142.63  6,401,528  halo,…,chemistry_dtd
    adv: one sector          0.3388   0.0031 108.00     18,736  halo,…,chemistry_dtd,vertical_alpha
    adv: one star            0.3365   0.0019 172.67      2,824  halo,…,chemistry_dtd,vertical_alpha

**Read within the run.** Every simple-model row is faster than D84's — the
desktop, not the code — so the shape is what carries: the advanced chemistry adds
about 0.21 s cold to any route that reaches it, and nothing to a route that does
not; warm, the two models are indistinguishable. Metadata is still
sub-millisecond with no stage behind it, and `/api/stages` grew by two
declarations. A full run is 0.41 s simple, 0.63 s advanced (D92).

## Session 10 — the audit (run 2 of 2)

Run 2 branched from the S9 merge (`635c3c8`) and, by instruction, read nothing of
run 1 (`session-10-gamma`). The defect list in D96 is written to be diffed against
run 1's; the diff itself is owed by whoever has both (BRIEF.md).

### D94. Every acceptance scalar is swept in N_R and N_t separately, and none moves past a tenth of its width

    default n_R=400, n_t=2000, n_z=60; each axis alone: n_R in (200, 800), n_t in (1000, 4000)
    row  quantity (simple)             default      n_R=200      n_R=800     n_t=1000     n_t=4000  drift/width
      1  Total stellar mass        5.27619e+10  5.27609e+10   5.2762e+10   5.2876e+10  5.28174e+10   0.006
      2  Star formation rate           1.96876      1.96974      1.96851      1.96726      1.96959   0.004
      3  Solar tangential velocity     256.004      256.068      255.959      256.338      256.173   0.056
      4  Thin disc scale length        2.49018      2.48942      2.48979      2.48788      2.48899   0.002
      5  Thick disc scale length       1.17317      1.16909      1.17087      1.17135      1.17286   0.010
      6  Thin disc scale height        253.054      253.051       253.18      253.023       253.05   0.001
      7  Thick disc scale height       1039.32      1039.03      1039.69      1038.61      1039.01   0.002
      8  Thick/thin local ratio      0.0250762    0.0250948    0.0250767    0.0249624    0.0250305   0.003
      9  Thick/thin surface ratio      0.10299     0.103039     0.102978     0.102465     0.102774   0.007
     10  Thin disc stellar mass    4.20319e+10  4.20362e+10  4.20307e+10   4.2161e+10  4.20958e+10   0.006
     11  Thick disc stellar mass     1.073e+10  1.07248e+10  1.07313e+10  1.07151e+10  1.07216e+10   0.002
     15  Bar half-length               4.98037      4.97885      4.97958      4.97575      4.97799   0.012
     16  Bar pattern speed             45.5648      45.5784      45.5744      45.6166      45.5909   0.003
     17  Bar corotation radius         5.24231      5.24071      5.24148      5.23745       5.2398   0.002
     19  Halo virial mass              1.1e+12      1.1e+12      1.1e+12      1.1e+12      1.1e+12   0.000
     20  Total gas mass (<30 kpc)  5.79503e+09   5.7964e+09  5.79471e+09  5.79412e+09  5.79619e+09   untestable
     22  Present-day gradient       -0.0236683   -0.0236669   -0.0236807   -0.0236422   -0.0236683   0.001
     23  Gradient, old end         -0.00668545  -0.00676996  -0.00672227  -0.00679806  -0.00663669   0.006
    advanced, where it differs (rows 1-4, 15-20 are shared code and read the same):
      5, 7, 8, 9, 11                       0            0            0            0            0   vacuous
      6  Thin disc scale height        326.166      327.059      326.761      325.733      325.994   0.009
     10  Thin disc stellar mass    5.27619e+10  5.27609e+10   5.2762e+10   5.2876e+10  5.28174e+10   0.006
     22  Present-day gradient       -0.0565751   -0.0562879    -0.056485    -0.056418   -0.0564906   0.014
     23  Gradient, old end          -0.0192657   -0.0194336   -0.0193567   -0.0192764   -0.0192285   0.008
     24  [α/Fe] bimodality              single       single       single       single       single   converged

**Decision.** `galaxy/specs/convergence.py` runs each model at the default grid and
at every point of `SWEEP`, one axis moved at a time, and judges every acceptance
row's drift against `Quantity.width`. Five statuses: `converged`, `unconverged`,
`untestable` (zero width, debt #17), `vacuous` (reads 0 at every grid), and
`not-yet-computable`. An unconverged row is recorded in `_UNCONVERGED` with a
debt and a prediction, as a miss is in `spec.py`; the register is empty. Only the
closure above the rows' fields runs (rule D4), so the sweep is ten runs and 4.8 s.

**Settled by.** The numbers. The widest drift is row 3's 0.33 km/s from N_t = 1000,
5.6% of its window; everything else is under 1.5%, and the vertical and pattern
rows under 1%. N_R never moves a row more than N_t does — GALAXY_INPUTS.md §10's
0.13-against-1 seen from the other side, and D37's analytic scalars holding
`[verified: tests/test_convergence.py::test_the_radial_axis_is_the_cheap_one]`.
One thing published and not explained (rule B6): the sfh scalars' dependence on
N_t is not monotone at the 0.1% level — row 1 reads +0.22% at N_t = 1000 and
+0.11% at 4000 against 2000 — which is D46's no-trend signature at a level no
row can see, and a first-order-in-dt normalisation error would be monotone. The
advanced model's thick-disc rows are `vacuous` rather than `converged`: nothing
moved because nothing is there, and a valley opening (debt #27) will make them
rows the sweep judges for the first time. Row 20 is `untestable` and stays `fail`
in the spec report on purpose (D97).

### D95. The profile per stage, cold in a fresh process, and D61's per-cell cost measured

    model simple: import 0.139 s (paid once per process)      model advanced: import 0.134 s
    stage            cp    cold s    warm s    c/w  cold %    stage            cp    cold s    warm s    c/w  cold %
    halo              1    0.0007    0.0004   1.66    0.1%    halo              1    0.0007    0.0005   1.33    0.1%
    assembly          2    0.0002    0.0002   1.27    0.0%    assembly          2    0.0002    0.0002   1.03    0.0%
    disc              1    0.0004    0.0003   1.15    0.1%    disc              1    0.0004    0.0007   0.60    0.1%
    sfh               3    0.0892    0.0912   0.98   16.5%    sfh               3    0.0913    0.0891   1.03   11.2%
    chemistry         3    0.0516    0.0525   0.98    9.6%    chemistry_dtd     3    0.3423    0.3331   1.03   42.0%
    vertical          3    0.0102    0.0104   0.98    1.9%    vertical_alpha    3    0.0120    0.0107   1.12    1.5%
    bar               4    0.0002    0.0002   1.01    0.0%    bar               4    0.0002    0.0002   0.76    0.0%
    population        5    0.0000    0.0000   0.73    0.0%    population        5    0.0000    0.0000   0.77    0.0%
    pattern           4    0.0115    0.0002  51.34    2.1%    pattern           4    0.0102    0.0002  46.27    1.2%
    systems           5    0.1526    0.1497   1.02   28.3%    systems           5    0.1374    0.1547   0.89   16.9%
    formation         6    0.0808    0.0798   1.01   15.0%    formation         6    0.0796    0.0805   0.99    9.8%
    planets           6    0.1417    0.1305   1.09   26.3%    planets           6    0.1404    0.1377   1.02   17.2%
    whole model            0.5393    0.5157   1.05  100.0%    whole model            0.8148    0.8077   1.01  100.0%
    catalogue (D61), both models: 1024 cells x 8 streams; stage 0.14-0.15 s at 20 000 stars (516 cells realised)
      layout 0.017 s; 1024 stars 0.10 s (406 cells); sample 0.14 s -> per cell ~100 us, per star 1.5-2.2 us;
      per-cell share at the sample 70-78%; every stream of every cell constructed alone 0.13 s (16 us each)

**Decision.** The runner records what each stage cost it (`Outputs.seconds`, the
compute plus the validation of what it published), and `galaxy/specs/performance.py`
runs each model in a fresh interpreter — the clock started before anything of the
package is imported — once cold and once warm, then splits the systems stage by
timing it at 1024 stars and at 20 000 and at the layout alone. Published, not
judged (rule B6): the one problem the spec can raise is a profile it could not take.

**Settled by.** D61 priced a stream at ~22 µs on that machine and left the share
open; here it is 16 µs, the per-cell part is ~100 µs against ~2 µs per star, and at
the published sample three quarters of the systems stage is per-cell setup that is
paid whether or not any cell's stars are asked for. Constructing every stream of
every cell alone costs 0.13 s, the ceiling of that part, which is 25% of a simple
run and 16% of an advanced one — the size of what a lazy catalogue could save,
and no more. The two models' pipelines differ by one stage: chemistry_dtd is 0.34
of the advanced model's 0.81 s (42%), the rest is shared to the millisecond. Two
readings within the run: `pattern` is 50× colder than warm because its first
`Generator` draw pays numpy's first-call cost, and nothing else has a cache to
read (c/w ≈ 1 everywhere else), so the cold column is the honest one.

### D96. The calibration audit (rule B10): the defect list

Every constant fitted or chosen while a mechanism the advanced model now has was
missing, re-examined; every register prediction the audit could run, run. As
tests, `tests/test_audit.py`; on the register, GALAXY_INPUTS.md §11. Numbered so
the two runs can be diffed line by line.

1. **Debt #12, measured.** `CONCENTRATION_NORM` = 4.1 normalises c_vir (Δ_vir ≈ 101
   ρ_crit) and is applied to c₂₀₀ unconverted. Converted through the NFW profile,
   c₂₀₀ = 10.9 not 14.35 (−24%); v_c(R₀) 243.8 → 230.4 km/s; **row 3 256.0 →
   242.6**, through its window and out. The cited z_f = 2–3 spans 15.3 km/s on row
   3 (248.2–263.5), not the 10 recorded. Recorded, not applied: debt #18's extended
   component lowers row 3 too, and both together overshoot.
2. **Debt #17, discharged.** The row 20/21 source quotes no uncertainty (abstract,
   §4.2) and its §5 gives its own HI mass a factor-of-two history. `Quantity.testable`
   says "no testable target"; nothing widened (D97).
3. **New debt #29.** Row 20's 8.0 × 10⁹ M☉ is HI + H₂ — hydrogen; `gas_mass_30kpc`
   is every retained baryon not in a star, helium included, and no constant names
   helium. Like for like the shortfall is **47%, not 28%**; debt #18's component must
   supply ~5 × 10⁹ M☉ of hydrogen, and `baryon_retention`'s budget argument is 3%
   low for the same reason.
4. **Debt #26, measured.** Gas above [Fe/H] = +0.5 out to 2.7 kpc (+1.20 at 1 kpc,
   +0.27 at 4) against 0.8 kpc in the simple model. `WIND_SPEED` 800 → 1300 km/s
   moves the centre only +1.65 → +1.37 and row 22 by 0.004 while taking the gas at
   R₀ from +0.15 to −0.17: the fitted constant sets the level, not the centre or
   the tilt. B10 note for the mass-loaded wind: refit `WIND_SPEED`; row 22 survives.
5. **Debt #27, prediction run — held in part.** Default merger list: n = 2, 3 at τ₀
   = 7, 1 Gyr all `single`, no second mode. Gaia-Enceladus alone: n = 3 with the
   merger delivering 0.2 of the budget (τ₀ = 7), or n = 3 at τ₀ = 1 with 0.5, reads
   **`bimodal_wide`** — depth 0.57–0.64, valley at +0.40, α-rich span 1.2 dex — with
   a present-day gradient of −0.13 to −0.14 dex/kpc, twice the observed. The thick
   disc it finds is the simple model's compact one: 6.6 × 10⁹ M☉ (row 11 in), 0.71
   kpc (row 5 far out), 1113 pc (row 7 just over), ratio 0.011 at R₀ (row 9 an order
   of magnitude low), thin disc 443 pc (row 6 out). The valley and row 22 are not
   both reachable through the inside-out index (rule B12); what is missing is a
   fast inner disc that does not steepen the infall law everywhere — the bulge and
   its inflow. The "DTD's long tail" fallback is not the whole story.
6. **Debt #28, measured in both models.** Old-population gradient with no migration
   −0.105 (simple) and −0.129 (advanced); young −0.020 and −0.062; the default kernel
   takes the old one down 16× and 7×; the young/old ratio lands at 3.2 and 3.1.
   A 10 Gyr gradient near −0.04 convicts the width in both models at once.
7. **New debt #30.** Row 6 reads 253 pc in the simple model (floor 250) and 326 in
   the advanced (ceiling 350). `SECULAR_HEATING` 20 fails the simple model low (176),
   30 fails the advanced high (429). `MERGER_HEATING` calibrates row 7 in the simple
   model (616 → 1745 pc over 60–180 km/s, row 6 untouched) and row 6 in the advanced
   one (287 → 392), where the heated stars have no thick disc to belong to. Two
   constants fitted to make one population thick are holding a different row within
   24 pc of its edge in the other model.
8. **New debt #31.** `GAS_DISC_SCALE_RATIO` (kept "so S10 can sweep it") swept 0.8 →
   1.5: R_d 2.00 → 3.68 kpc, row 3 261 → 237, SFR 1.54 → 2.78, gas 4.3 → 9.3 × 10⁹.
   At 1.5 the simple model's rows 5 and 11 pass and 3, 4, 22 fail (S3's conflict,
   with numbers). The advanced model's row 22 runs −0.086, −0.057, −0.047, −0.043,
   so its pass needs the infall scale within a tenth of R_d: the no-op is load-bearing.
9. **Debt #21, a note.** Row 15 is `BAR_LENGTH_RATIO × R_d` exactly: 2.0 × 2.49 =
   4.98 against 4.8–5.2. A check on R_d, not the bar; it follows debt #18 one for one.
10. **Ratchet.** `tests/test_registry.py` bounded UNSET defaults at ≤ 1 for seven
    sessions while the count was 0; now == 0.
11. **Not re-examined, named.** `RETURN_FRACTION` returns mass instantaneously in the
    shared sfh stage while the advanced chemistry delays a third of the iron; no
    row reads the difference. `PLANETESIMAL_EFFICIENCY`/`ICE_BOOST` are debt #25's.
    `NET_YIELD` is debt #16's, discharged. `disc_spin` and `baryon_retention` were
    not fitted to a row (D30, D32) and stand.
12. **Absences.** No acceptance row moves with the grid (D94). The fetch gate's one
    failure at open was a machine artefact, not a defect (D99).

**Register after the audit:** 23 open, 8 discharged (`tools/progress.py`).

### D97. A zero-width target says "no testable target" rather than borrowing a width

**Decision.** `spec.Quantity.width` is `hi − lo`; `testable` is False for a
pointwise row with zero width (rows 20 and 21) and True for a statistical one
(row 14: an ensemble's interval can contain a point). The spec report says "no
testable target — debt #17" on such a row and still reports `fail`; the
convergence spec publishes its drift and gives no verdict. Rows 22 and 23 keep the
`[inferred]` intervals S2 gave them; rows 20 and 21 get none.

**Settled by.** The source was read (arXiv:1511.08877): no uncertainty anywhere on
the 8.0 × 10⁹ or the 89 : 11, and the paper's own HI mass moved by a factor of two
between its Paper I and III. An interval this project inferred would be a guess
dressed as a citation; a zero width that says so is the honest table (rules B5,
B9, B14). Row 20's miss stays recorded under debt #18 because 5.8 against 8.0 is a
miss on any reading — and 4.2 against 8.0 once helium is taken out (debt #29).

### D98. Cold timings at S10 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0002   1.48        940  -
    viewer: a module         0.0003   0.0002   1.54     21,599  -
    index                    0.0000   0.0000   1.95      1,237  -
    version                  0.0018   0.0016   1.09      1,132  -
    stages                   0.0002   0.0001   1.58      8,645  -
    fields                   0.0007   0.0004   1.60     57,008  -
    inputs                   0.0001   0.0001   1.74      9,091  -
    arrays: one profile      0.0910   0.0002 388.38      4,672  halo,assembly,disc,sfh
    arrays: history          0.1389   0.0027  52.28  6,401,472  halo,…,chemistry
    arrays: scalar           0.0882   0.0003 254.04      1,416  halo,assembly,disc,sfh
    region: one sector       0.1684   0.0039  42.69     18,720  halo,…,vertical
    region: whole disc       0.3260   0.1407   2.32  1,126,208  halo,…,vertical
    system: one star         0.1586   0.0022  73.61      2,816  halo,…,vertical
    adv: history             0.4334   0.0043  99.66  6,401,480  halo,…,chemistry_dtd
    adv: alpha plane         0.4325   0.0028 152.21  6,401,528  halo,…,chemistry_dtd
    adv: one sector          0.4544   0.0038 120.02     18,736  halo,…,chemistry_dtd,vertical_alpha
    adv: one star            0.4409   0.0021 205.16      2,824  halo,…,chemistry_dtd,vertical_alpha
    import + registry: 0.096-0.123 s, paid once per process and excluded from the cold column

**Read within the run.** Every row is 20–35% slower than D93's on the same desktop
— the machine, not the code: no stage changed and the runner's per-stage clock
costs a `perf_counter` per stage. The shape is D93's: the advanced chemistry adds
about 0.3 s cold to any route that reaches it and nothing warm; metadata is
sub-millisecond with no stage behind it. `tools/scaling.py` was not re-run (rule
B7): no stage's cost changed.

### D99. The runner keeps its own clock, and the gate walks its own tree

**Decision.** `Outputs.seconds` is part of the runner's contract, keyed like `ran`.
`tests/test_api.py`'s one-fetch gate skips `.claude/` — on a desktop checkout the
harness keeps other sessions' worktrees there, each with its own `transport.js`,
and the gate walked into one at open. A machine artefact, fixed at the gate; the
worktrees themselves were not read (rule C1 in spirit: the second run stays blind
to the first).

**Settled by.** A profile read from outside the runner is a reading of the wrapper
(rule B3); the runner's own clock is the one that cannot disagree with the order
it ran. The gate's failure was the first thing the session saw and the last thing
it had to fix.

### D100. The two blind audits diffed: what both found, what only one found, where they disagree

**Decision.** The two lists the board's gate asks for are run 1's, on
`session-10-gamma` (its DECISIONS.md D94–D102, BRIEF.md "This run's defect
list", GALAXY_INPUTS.md §11 #29–#31 and amendments to #12, #17, #18, #26,
`tests/test_calibration.py`, six tests), and run 2's, this branch's D96 with
D94, D95, D97 and `tests/test_audit.py`, eleven tests. Both were cut from the
S9 merge `635c3c8`, both ran on Fable 5.1 on the desktop, and neither read the
other or any commit after that merge `[verified: git merge-base session-10-gamma
session-10-gamme-run-2 = 635c3c8; this branch's D96 and gamma's D102]`. Run 1
numbers itself "run 3" because its instruction named two earlier branches; here
it is run 1 of this pair. The diff is written from both branches read side by
side, once, and nothing in it is averaged (rule B12): where the runs disagree
both readings stand on their branches and the merge picks one.

**Both found (9).** Every number the two runs both measured agrees to the last
printed digit; the lists differ in what was measured, not in what was read.

1. **Debt #12.** c_vir = 14.35 converted at Δ_vir = 101 ρ_crit is c₂₀₀ = 10.9,
   and row 3 falls 256.0 → 242.6 km/s — through its window and out — in both
   (gamma D97, here D96.1). Both conclude the conversion and z_f are degenerate
   in row 3, either fix alone overshoots, and the two must be set together
   against rows 3 and 19; both recorded and changed nothing.
2. **Debt #17, the fact.** Both read arXiv:1511.08877 and found no uncertainty
   on 8.0 × 10⁹ or 89 : 11; both discharged the debt. The remedies differ — the
   one substantive split, below.
3. **Row 6 and the heating constants** (gamma #31 ≡ here #30). `SECULAR_HEATING`
   fitted for the simple model's merger-defined thin disc holds the advanced
   model's row 6 at 326 pc, 24 pc under its ceiling; 30 km/s puts it at 429 in
   both runs. Both call it one constant, two fits (rule B10).
4. **The `GAS_DISC_SCALE_RATIO` sweep** (gamma's #18 amendment ≡ here #31). The
   advanced gradient reads −0.086 at 0.8 in both, −0.048 (gamma) against −0.047
   (here) at 1.2; both find rows 3 and 20 bought only by paying rows 2 and 22,
   and both read that as the case for a second component rather than a wider
   first. They file it differently, below.
5. **Debt #26.** Both name the bulge and its inflow as the open question and
   measured the centre from opposite ends — gamma downstream at the planets, here
   at the lever — with one number in common: the `WIND_SPEED` lever on the gas at
   R₀, −0.064 dex per +10% (gamma #30) against −0.32 dex for +62% (here #26),
   consistent to the curvature.
6. **Convergence.** Every reachable row stays inside its width in both models
   with the same criterion (drift ≤ width) and empty registers; row 3 is the
   widest testable drift, 0.34 / 0.33 km/s from n_t (5.7% / 5.6% of 6 km/s);
   n_R moves no row more than n_t; row 1's 0.2% step in n_t is D46's class; the
   advanced thick-disc rows read zero on every grid (debt #27 is not a
   resolution effect); row 24 is `single` everywhere.
7. **Performance.** 0.54 s simple, 0.82 / 0.81 s advanced, cold; `chemistry_dtd`
   42% of the advanced run; `pattern`'s first `Generator` draw the only cold/warm
   gap (40× / 50×); a `Generator` costs 14–18 µs (gamma) / 16 µs (here); D61
   answered the same way — per-cell setup, not stars, is the catalogue's cost.
8. **Cold timings** 20–30% slower than D93 on the same desktop; both blame the
   machine; the stages column unchanged.
9. **Housekeeping.** Both lowered the UNSET ratchet 1 → 0, both made the
   one-`fetch` gate skip `.claude/`, both changed no physics: spec counts
   11 / 7 / 6 and 8 / 11 / 5 are S9's in both.

**Run 1 only (3 findings, 3 smaller readings).**

- **`KS_NORM`'s own ±1σ contains row 2** (gamma #29): across (2.5 ± 0.7) × 10⁻⁴
  the SFR runs 2.16–1.85 and the gas 6.8–5.2 × 10⁹ the other way, so row 2 is
  not a check by itself and only the pair with row 20 is evidence. Run 2 never
  moved `KS_NORM`. **Registered here as #32.**
- **`NET_YIELD` and `WIND_SPEED` are provisional on debt #18** (gamma #30), with
  the levers that make the re-fit one line: +10% `WIND_SPEED` = −0.064 dex, +10%
  `NET_YIELD` = +0.041 dex at R₀. Run 2 declined `NET_YIELD` by name ("debt
  #16's, discharged", D96.11) and tied `WIND_SPEED`'s refit to #26's mass-loaded
  wind only. **Registered here as #33.**
- **The centre reaches the planets** (gamma D100): 1.2% of the advanced
  catalogue above [Fe/H] = +0.5 against 0.02%, giant occurrence inside 1 kpc
  0.43 against 0.07, the published sample's giant fraction 1.65% against 1.02%,
  occurrence at R₀ 5.0% in both. Run 2 measured the gas, not the stars. **#26
  amended.**
- Smaller: row 3 moves 0.22 km/s with n_R because the disc's resolved term is
  integrated on the grid while the halo's is analytic (gamma D94); 52 pc of the
  advanced row 6 is `MERGER_HEATING`'s (274 without) and 30 km/s leaves the
  simple model at 347 (gamma #31 → here #30); at ratio 1.2 rows 3 and 4 pass at
  248.7 km/s and 2.97 kpc, row 20 reads 7.2 × 10⁹, row 2 2.33 and the simple
  gradient −0.018 (gamma #18 → here #31).

**Run 2 only (6 findings, 4 smaller readings).**

- **Row 20 compares total gas with a hydrogen mass** (#29): like for like the
  miss is 47%, not 28%; debt #18's component owes ~5 × 10⁹ M☉ of hydrogen and
  `baryon_retention`'s budget argument is 3% low. Gamma read the same abstract
  and kept "28%" — the miss its own remedy for #17 is written to preserve.
- **Debt #27's prediction, run** (D96.5): the default merger list stays `single`
  at n = 2, 3; Gaia-Enceladus alone with n = 3 opens `bimodal_wide` (depth
  0.57–0.64, valley at +0.40) at the price of row 22 (−0.13 to −0.14), and the
  thick disc it finds is the simple model's compact one. Gamma's one #27
  reading is that it is not a resolution effect.
- **Debt #28 measured in both models** (D96.6): old gradient −0.105 / −0.129
  without migration, the kernel flattens it 16× / 7×, young/old 3.2 / 3.1.
- **`MERGER_HEATING` calibrates a different row in each model** (#30): row 7 in
  the simple one (616 → 1745 pc over 60–180 km/s), row 6 in the advanced
  (287 → 392); `SECULAR_HEATING` 20 fails the simple model low at 176.
- **`GAS_DISC_SCALE_RATIO` is load-bearing** (#31 as a debt, rule B11): the
  advanced row 22 runs −0.086, −0.057, −0.047, −0.043 across 0.8–1.5 and passes
  only within a tenth of the disc's scale; at 1.5 rows 5 and 11 pass and 3, 4,
  22 fail.
- **`WIND_SPEED` sets the level, not the centre** (#26): 800 → 1300 km/s moves
  the central maximum +1.65 → +1.37, the gas at R₀ +0.15 → −0.17, row 22 by
  0.004.
- Smaller: z_f = 2–3 spans 15.3 km/s on row 3 (248.2–263.5), not the 10 the S2
  text of #12 recorded; row 15 is `BAR_LENGTH_RATIO × R_d` exactly, a check on
  R_d (#21); `RETURN_FRACTION` named as not re-examined (D96.11); the sfh scalars'
  dependence on n_t is not monotone at the 0.1% level (D94).

**Where they disagree (5, one of them substantive).**

1. **Debt #17's remedy.** Gamma gives rows 14, 20 and 21 the half-unit of the
   source's last printed digit — `spec.py` now reads 112.5–113.5, 7.95–8.05 × 10⁹,
   0.105–0.115 — and argues rule B5 widens nothing because no failed row passes,
   and that "no testable target" would hide row 20's 28% miss (gamma D95). Run 2
   leaves the intervals at zero width, adds `Quantity.testable` (False for a
   pointwise row with `lo == hi`, True for a statistical one), prints "no
   testable target — debt #17", and keeps row 20 `fail` and a recorded miss
   under #18, arguing that an interval this project infers is a guess dressed as
   a citation (rule B14; here D97). Each run's objection to the other's remedy:
   gamma's does not reach run 2's implementation, whose row 20 still fails and
   is still recorded; run 2's reaches gamma's half-unit, though gamma's is a
   declared convention, not a guess. Three things follow from the split and are
   not themselves disagreements: gamma judges row 20's convergence (6.8% of a
   10⁸ M☉ width, its largest drift) where run 2 says `untestable` (its largest is
   row 3's 5.6%); gamma's row 14 has a width, run 2's is testable at zero width
   by being statistical; gamma's `spec.py` notes and #17/#18 text carry "28%",
   which #29 makes stale. **Not averaged.** The merge takes one remedy whole;
   the other is a named ruleset on its branch (rule B12).
2. **The numbers.** Both runs opened #29–#31 with different contents, and both
   started decisions at D94. Mapping, gamma → here: #29 → #32 (new), #30 → #33
   (new), #31 → #30 (same finding), the #18 amendment → #31 (same sweep);
   D94 → D94, D95 → D97 (opposite remedy), D96 → D95, D97 → D96.1, D98 → #31 and
   #32, D99 → #30 and #33, D100 → #26, D101 → D98, D102 → this entry. Run 2's
   #29–#31 keep their numbers here because the register and D96 and
   `tests/test_audit.py` cite them; renumbering is the merge's, not the diff's.
3. **The catalogue's per-cell cost.** Gamma: 276 µs per realised cell and 7 µs
   per star, `Generator` construction 41–53% of the stage (gamma D96). Run 2:
   ~100 µs per cell and 1.5–2.2 µs per star, per-cell setup 70–78% of the stage
   (here D95). The same word for two quantities — gamma's is the stage's time
   over its realised cells, stars included; run 2's is the fixed cost from a
   two-sample fit — and the one like-for-like number, a `Generator`, agrees
   (14–18 against 16 µs), as does the conclusion. A disagreement about a word.
4. **Row 20's miss**: 28% (gamma, hydrogen against total) against 47% (here,
   like for like). Not two measurements of one thing: run 2 found the accounting
   gamma inherited from S2. If #29 stands, gamma's 28% is superseded, not wrong.
5. **The sweep's points**: gamma six (n_R 100 / 200 / 800, n_t 500 / 1000 / 4000),
   run 2 four (200 / 800, 1000 / 4000), same criterion. Gamma's coarser grids give
   its larger row-6 drift (2.05 pc at n_R = 100); nothing else differs.

**What the diff measures.** Both runs were Fable 5.1, so this pair is not the
plan's "once on each model" comparison (GALAXY_PLAN.md, "Run S10 twice, once on each model"): it holds the model
fixed and varies the run — blind, from one commit, on one machine. Read that
way: every measurement both made is reproducible to the printed digit, and the
divergence is entirely in *choices* — which constant to move, whether a finding
is an amendment or a debt, which of two remedies to a zero width. Coverage,
counting distinct substantive findings in the union:

    found by          both   run 1 only   run 2 only   union
    findings            5         3            6         14
    one run alone would have found 8 (gamma) or 11 (here) of 14

So a single audit by this model misses between a fifth and two fifths of what
two find, and the two lists' *disagreement* — one remedy — is the only place
where the merge has to choose rather than take the union `[inferred from the
lists above]`.

**Actions taken here, none of them physics.** #32 and #33 registered from run 1
with its test names cited by branch; #26, #30 and #31 amended with run 1's
numbers; `test_the_register_carries_s10s_findings` counts 25 open, 8 discharged;
the board's debt line regenerated. Nothing renumbered, nothing averaged,
`session-10-gamma` untouched. One lesson recorded: two blind runs that share a
numbering guarantee the collision this entry had to map, so a paired run should
be handed a reserved range of debt and decision numbers before it starts.

**Beyond this pair.** `main` already carries `Merge S10 into main` (`ff12928`,
from `session-10`), whose D94–D98 and debts #29–#33 are a third list — its own
two runs, `AUDIT_RUN1.md` / `AUDIT_RUN2.md`, diffed in its D97 — and
`session-10-beta` holds a fourth (D94–D105, debts #29–#35). So this branch
cannot merge as BRIEF.md planned without a second reconciliation against `main`,
and the board row stays ◐: the diff the gate asked for is done, the merge is the
maintainer's (BRIEF.md, MANUAL_TODO.md §2). The other lists were not read for
this entry beyond their headings and debt titles, so that what is written above
is this pair's diff and nothing else's.

### D101. The four S10 lists side by side: main's two runs, beta's two, and the gamma pair

**Decision.** D100 diffed the gamma pair. This entry sets that diff beside the
two other S10 lists in the repository, read from their branches for this
purpose and nothing else: **main** (`session-10`: `AUDIT_RUN1.md` §4, six items;
`AUDIT_RUN2.md` D-1…D-14, C1–C5, P1–P5; the two diffed in main's D97; debts
#29–#33 there) and **beta** (`session-10-beta`: D94–D105, two runs by one
author aimed apart, diffed in its D105; debts #29–#35 there). Six runs in all,
every one from S9's model on the desktop: main's two and the pair's two on
Fable 5.1, **beta's two on Opus 5** `[verified: the S10 board row on each of
the four branches]` — so beta against the other two lists is the model
comparison GALAXY_PLAN.md asked S10 for. Three lists are independent of each
other — main, beta, the pair — and inside main and beta the second run knew
the first (main D97 §"what the diff says", beta D105 §"what it is worth").
Nothing below is averaged (rule B12); where two lists
give one quantity two numbers, both stand and what each assumed is stated.

**The common core: what every list found (5).**

1. **Debt #12's conversion is the size of row 3's miss or larger.** Measured
   by four of the six runs (main's run 1 only flagged it; beta's second run
   audited the instruments) — and given three different numbers,
   disagreement 1 below.
2. **Row 20 cannot be judged against a zero width.** Every list; the remedy
   splits 4 : 1, disagreement 2.
3. **The advanced chemistry is 40–42% of its model, and the first `Generator`
   of a process lands on `pattern`.** main run 2 46×, beta 30× with the one-off
   measured alone at 8.9 ms, gamma 40×, here 50×. main run 1 alone wrote "cold
   and warm agree at every stage" and main's own run 2 corrected it (D-12).
4. **No acceptance scalar drifts across its width in N_R or N_t.** The worst
   is row 3 under N_t at 0.33–0.34 km/s of 6, 0.055 of a width, in every run;
   the advanced thick-disc rows read zero on every grid; rows 1 and 10 move
   non-monotonically in N_t at 0.2% (main C2, beta's margin lesson, gamma,
   here). main and beta also swept N_z (harmless, 3 × 10⁻⁷ dex/kpc); the pair
   did not.
5. **Housekeeping.** All four branches lowered the UNSET ratchet 1 → 0; none
   changed physics; the spec counts are S9's in every run (11 / 7 / 6, 8 / 11 / 5).

**Where two or three lists overlap, with the numbers.**

- **The `GAS_DISC_SCALE_RATIO` sweep**: main run 2 (P5), gamma and here read
  the same digits — 0.8 → 1.2 takes row 3 261.1 → 248.7, R_d 2.00 → 2.97, row 20
  4.32 → 7.25 × 10⁹, the simple gradient −0.047 → −0.018, row 2 1.54 → 2.33.
  Filed three ways: main as D-6 and an amendment to #18, gamma as an
  amendment to #18, here as debt #31 (rule B11). beta did not sweep it; main
  run 1 wrote "holds".
- **`SECULAR_HEATING` is fitted to row 6**: main run 2 (P10: 20 → 176, 30 →
  347; row 7 883 / 1039 / 1231), gamma and here, which add the advanced model
  (326 pc; 429 at 30; `MERGER_HEATING` 287 → 392). main run 1's "holds: set
  from an observation" is contradicted by its own run 2 and by the pair.
- **`KS_NORM`'s own ±1σ contains row 2**: main run 2's round-3 probe (3.2 × 10⁻⁴
  → row 2 = 1.847, 0.007 above its bound; row 20 5.25 × 10⁹) and gamma's #29
  (→ #32 here) are the same numbers. Filed as "holds, load-bearing" on main
  and as a debt here — disagreement 5.
- **The iron-rich centre reaches the planets**: main run 1 (19% giant
  occurrence at 2 kpc against 2.6%; sample fraction 1.65% against 1.02%),
  main run 2 (known), gamma (adds 0.43 against 0.07 inside 1 kpc). beta and
  this run measured the gas instead (beta: the centre is the wind, not the
  grid; here: `WIND_SPEED` sets the level, not the centre).
- **Row 15 is `BAR_LENGTH_RATIO × R_d`**: main run 1, main run 2 (known), here
  (#21). Not gamma, not beta.
- **Debt #12's stated sensitivity is stale**: z_f = 2–3 spans 15.3 km/s on
  row 3, not 10 — beta (15.29) and here (15.3); z_f = 2.0 → 248.2 — main run 2
  (P8) and here.
- **`WIND_SPEED` is fragile, in four forms**: main run 2 (fitted against a
  potential carrying row 3's excess, and evaluated on the present-day potential
  at every time: f_esc 0.78 early against 0.753), beta (K = 3.42 moves its
  refit by 0.01 dex), gamma (provisional on #18; −0.064 dex per +10%), here
  (800 → 1300 km/s is −0.32 dex at R₀ and 0.004 on row 22). The levers agree:
  main ±5% → ∓0.03 dex, row 22 ±0.0006 per 10%.
- **Migration's young/old ratio 3.2 / 3.1**: main run 2 (3.18 / 3.09; the
  stale row-23 miss text corrected on main) and here (3.2 / 3.1; the 10 Gyr
  gradient as the discriminator, −0.105 / −0.129 without migration).
- **The harness's worktrees under `.claude/`** broke a tree-walking test on
  every desktop run: main run 2 (the hooks path), beta (D99: `git ls-files`),
  gamma and here (skip the directory). One artefact, three fixes.

**Found by one list only.**

- **main only** (its run 2, unless said): `MERGER_DURATION` is dead and the
  merger's gas arrives as a step (#30 main); the Sagittarius default delivers
  5.9 × 10⁹ M☉ from 3.8 Gyr and without it row 2 passes at 1.837 in both models
  (#29 main); the catalogue does not migrate, spread 0.19 against 0.30 (#31
  main); "without migration the spread is far too narrow" is refuted, 0.294
  against 0.299 (#32 main); Z(R₀) = 1.24 Z☉ with an unregistered 2.0 (#33 main);
  `vertical.scale_height` hard-codes G (D-9); `SF_THRESHOLD` = 10 closes rows 2
  and 20 with row 3 unmoved (D-3); `baryon_retention` = 0.30 passes rows 1–3
  (D-4); rows 1 and 10 pass by two cancellations and row 1's target includes
  the bulge (D-5); row 22's advanced pass is conditional on `WIND_INDEX` = 2
  (D-14); `tools/scaling.py` labels a warm run cold (D-13); `DTD_BINS` and
  `AGE_BIN` converged (C4); N_z has one consumer (C5); `DIP_DEPTH` decides row
  24 at a dip of 0.384 (§4.5). Fifteen items — the largest single list.
- **beta only**: the acceptance table reads nothing inside 4 kpc, so debt #26's
  +1.5 dex is invisible to it (#29 beta); N_z buys nothing and `escape_velocity`
  is evaluated half a cell above the midplane it is declared at (#30 beta);
  the default grid is 25× finer in radius and 80× in time than any row can
  detect, and `CELL_RINGS` is bound into a default argument (#31 beta);
  `tools/timings.py` carries the 8.9 ms one-off unlabelled (#32 beta); the
  statistical criterion rewards a noisier model and `ENSEMBLE_MIN` = 20 cannot
  deliver a central 95% — n = 41 would (#33 beta); `world_seed` is read by
  nothing and the ensemble samples a diagonal (#34 beta); the reproducibility
  check runs both halves in one interpreter (#35 beta); K and z_f enter only as
  their product and the epoch row 3 wants, z_f ∈ [1.9, 2.1], is below the cited
  range; #16's discharge quantified at 10%; a coarse grid (N_t = 8)
  manufactures debt #27's valley; a too-coarse control point on every sweep
  knob; a two-point difference that returned a negative cost per star. Twelve.
- **the pair only**: row 20's target is hydrogen and the miss is 47%, not 28%
  (#29 here — every other run wrote 28%); debt #27's prediction run, a fast
  inner disc opening `bimodal_wide` at the price of row 22 and finding the
  compact thick disc (D96.5; main's nearest probe: n = 3 gives −0.0666 at row 2
  = 1.29); `MERGER_HEATING` calibrates row 7 in one model and row 6 in the
  other (#30 here); #28 measured with no migration in both models (16× / 7×);
  `NET_YIELD` provisional on #18 (#33 here; main run 2: drifted −0.025 dex,
  harmless); row 3 moves with n_R through the disc's quadrature (gamma D94);
  the `Generator` ceiling 0.13 s (D95). Seven.

**Where the lists disagree on a number or a verdict (6).**

1. **How much debt #12's conversion is worth.** The pair: c₂₀₀ = 10.9 and row
   3 → 242.6, the NFW profile converted at Δ_vir = 101 ρ_crit (`test_audit.py::
   c200_from_cvir`, gamma's `concentration_at`). beta: c₂₀₀ = 11.98 and row 3 →
   246.92, from the ratio of the model's R₂₀₀ = 212.94 kpc to the cited 255 kpc
   top-hat radius, 1.198. main run 2: c₂₀₀ = 12.25 and row 3 → 247.97, K = 3.5
   from a recalled factor "of order 0.8". Same sign, 5.4 km/s apart; beta's and
   main's put the corrected row inside 245–251, the pair's 2.4 below it. Three
   conversions — one computed from the profile with its overdensity stated, one
   from an external radius, one recalled — and three discriminators proposed:
   rows 1 and 19 (main D-4), rows 2 and 20 (beta D95), rows 3 and 19 with z_f
   set jointly (the pair). Not averaged; this is main's BRIEF item 3.
2. **Debt #17's remedy, 4 : 1.** "No testable target" or `untestable`: main
   run 1 (the sweep only), beta (`Quantity.testable`, `untestable()`, a
   `SpecError` on a new silent zero-width row; row 14 exempt), here
   (`Quantity.testable`, statistical rows exempt); main run 2 took it as known.
   Gamma alone widened rows 14, 20 and 21 to printed-precision half-units. beta's
   D98 states the objection to gamma's move in advance: an interval chosen with
   the answer known is what rule B5 forbids; gamma's answer is that no failed
   row passes by it. main and beta keep #17 open with a mechanism; gamma and
   this branch discharge it.
3. **`MERGER_HEATING` in the advanced model.** main run 1: "no row reads the
   kick" until the valley opens. The pair: the advanced row 6 reads it — 287 →
   392 pc across 60–180 km/s, 52 pc at the default (274 without). Contradicted
   by a measurement.
4. **D61 and debt #24.** main run 1: the catalogue's cost is proportional to
   the stars asked for, D61's fear "is not what the code does", **#24
   discharged in full** and struck on main's register. beta: 90% of the
   catalogue's 113 ms does not depend on the star count (0.59 µs per star),
   14.9 ms lays out all 1024 cells whether or not anything asks, 163 µs per
   realised cell — D61 half right, the trade-off moved to beta's #31. Here:
   ~100 µs fixed per cell against ~2 µs per star, 70–78% of the stage per-cell
   setup, a 0.13 s ceiling; gamma 276 µs all-in per realised cell, 41–53%
   `Generator` construction. Every run agrees a nine-cell region query costs
   2.6–2.9 ms, so the pruning is real; the registers disagree on whether #24 is
   discharged (main yes; beta and the pair no). The marginal cost per star is
   0.59 µs on beta and 1.5–2.2 here, different sample ranges, the same order.
5. **`KS_NORM`.** One probe, one set of numbers, two verdicts: "holds,
   load-bearing" (main run 2) against "not a check on the model by itself"
   (gamma → #32 here).
6. **Row 20's miss.** 28% in main, beta and gamma; 47% here, like for like
   (#29 here). Not two measurements — an accounting the other four inherited
   from S2. If #29 stands, main's "`SF_THRESHOLD` = 10 leaves row 20 6% low"
   reads 27% low, and Sagittarius's "row 20 5.66 × 10⁹" is further off, not
   nearer.

Two contradictions inside main are already on its D97 and are not repeated
here (`SECULAR_HEATING` "holds", `SF_THRESHOLD` "holds").

**What the four lists together say.** The union is about forty distinct
findings. The largest single list, main's run 2, holds about a third of it;
the three independent lists each hold the core of five and then 15 (main),
12 (beta) and 7 (the pair) findings no other list has, and no two lists
share more than a third of either. beta's D105 drew from two aimed runs the
warning that the count found says nothing about the count remaining; three
independent lists say it with more force `[inferred from the lists above]`.

**The model comparison.** Four Fable 5.1 runs (main's two, the pair) against
two Opus 5 runs (beta's), with the plan's own caveats: one list on the Opus
side, and beta's two runs shared an author. What the lists show. (i) Size:
beta's twelve unique findings sit between main run 2's fifteen and the pair's
seven, and beta opened seven debts to main's five and the pair's five. (ii)
Aim: beta audited the instruments and the acceptance table's coverage — the
statistical criterion, the seed ensemble, the determinism check, the grid's
sizing, the one-off's billing, the table's blind inner disc; the Fable lists
audited the model's constants and the register's predictions — every
constant across its cited range, every field to a reader, the debts'
predictions run. The two aims barely intersect, and that, not quality, is why
the lists are nearly disjoint. (iii) Agreement where they meet: the shared
core agrees to the digit (0.055 widths, 8.9 ms, 42%, 0.33 km/s); the one
shared quantity with two numbers is #12's conversion, and the difference is
in what each assumed, not in the arithmetic. (iv) Contradicted verdicts: main
run 1 has five (three on main's D97, `MERGER_HEATING` and #24 here); main run
2, beta's two runs and the pair have none. So the weakest list in the
repository is a Fable run, and the distance between it and the next Fable
run on the same branch is larger than any distance between the Fable lists
and the Opus one. Read as the plan asked — did the model choice matter? — the
answer six runs give is that the **aim** decided what was found and the
model did not, visibly; a second Opus list, blind, is what would turn that
reading into a measurement `[inferred from the lists above; rule B12, nothing
averaged]`.

**What a union register needs (for MANUAL_TODO.md §2).** main's #29–#33 stand
as written — no other list found any of them. beta's #29–#35 are seven new
numbers, none duplicated anywhere. Of this branch's five: helium (#29) and the
provisional yields (#33) are new to main; row 6 (#30) is in main's
`AUDIT_RUN2.md` §5 as "fitted; fragile" and not as a debt; the ratio (#31) is
main's D-6, filed under #18; `KS_NORM` (#32) is main's "holds, load-bearing" —
whether the last three are debts or amendments is a filing choice the merge
makes once. Amendments to #12 come from three lists with three numbers, and
stay three; #17 takes one remedy; #24 is either re-opened (beta, the pair) or
stays discharged (main); #26, #27 and #28 take every list's measurement. The
decisions D94 onward exist three times; two sets are renumbered at the merge.
