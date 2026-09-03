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
