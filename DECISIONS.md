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
