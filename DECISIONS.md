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

## Session 10 — the audit, run 1

### D94. The grid is swept one axis at a time, and nothing drifts

**Decision.** `galaxy/specs/convergence.py` runs every published acceptance
scalar of each model at N_R ∈ {200, 400, 800}, N_t ∈ {1000, 2000, 4000} and
N_z ∈ {30, 60, 120}, each axis alone with the others at the default, and fails
the spec run on a pointwise row whose largest departure from the default-grid
value exceeds its own target's width. A zero-width target is *untestable*, not
failed (debt #17); a category that changes is a drift; statistical rows are
reported at the default seed without a verdict. `python -m galaxy.specs` runs it
after the four existing specs (`--quick` halves the sweep).

**Settled by.** GALAXY_INPUTS.md §10: the cost exponent is 0.13 in N_R against
about 1 in N_t, so the two are not one quality knob and a sweep that moved them
together would hide which one a scalar follows. **Result: 0 drifts of 54 row×axis
pairs in the simple model, 0 of 57 in the advanced.** The largest movement is
v_tan under N_t, 0.33 km/s of a 6 km/s target; the stellar mass moves 0.2% under
N_t and 0.002% under N_R; N_z moves the advanced gradient by 3 × 10⁻⁷ dex/kpc, so
reading the halo potential off the first z-row (D89) costs nothing. The
instrument was checked on a stage built to drift before it was believed on one
that does not `[verified: tests/test_convergence.py::test_a_scalar_that_moves_with_the_grid_is_caught]`.

### D95. The profile, cold, per stage — and the catalogue costs what is asked for

    model simple: 0.425 s cold, 0.410 s warm
      sfh 16.3%  chemistry 9.1%  vertical 1.7%  pattern 2.3%  systems 28.5%  formation 15.3%  planets 26.6%
    model advanced: 0.658 s cold, 0.651 s warm
      sfh 11.4%  chemistry_dtd 41.1%  vertical_alpha 1.3%  pattern 1.5%  formation 9.5%  systems 17.6%  planets 17.3%
    catalogue at 20,000 stars: layout 0.014 s; one cell 0.0011 s (23 stars), nine 0.0026 s (206), every cell 0.116 s (19,998)

**Decision.** `galaxy/specs/performance.py` times every stage of one default run
in a fresh interpreter per model (rule B2), warm beside cold, and materialises
the catalogue for one, nine and every cell. It publishes numbers and fails on
nothing (rule B6).

**Settled by.** Cold and warm agree at every stage, so there is no cache in the
reading *[S11: not at `pattern`, whose cold column carries the interpreter's first
seeded draw, 10 ms against 0.4 warm — AUDIT_RUN2.md D-12, debt #37, D101]*. One
stage is over a fifth of either model: the advanced chemistry, at
41% — its per-timestep Python loop and 28 transport kernels of 400 × 400 — and it
is the only optimisation worth a session. The per-cell table closes what debt
#24 left open: cost is proportional to the stars asked for, one cell is a
thousandth of the whole disc, and D61's fear that every cell's streams were
built regardless is not what the code does. **Debt #24 is discharged in full.**

### D96. The calibration audit, run 1: one defect, four flags, and the protocol for run 2

**Decision.** Every constant fitted or chosen against a mechanism is re-examined
in `AUDIT_RUN1.md` §3 against the mechanisms that have arrived since (rule B10).
The defect list is §4 of that file. **Run 2 continues on `session-10` (rule C2d),
uses the instruments, and must not read `AUDIT_RUN1.md` until its own list is
written**; the diff goes here as D97 or later. Run 1 therefore closes partially:
the board row is ◐, nothing is merged, no tag is queued.

**Settled by.** The one defect: row 15 passes because `BAR_LENGTH_RATIO` = 2.0
was chosen inside a cited 1.5–2.5 and 2.0 × 2.49 ≈ 5.0 — a choice, not a
prediction, appended to debt #21. The flags: `WIND_SPEED` was fitted against a
massless wind (debt #26); `MERGER_HEATING` has no row reading it in the advanced
model until the valley opens (debt #27); `migration_efficiency` wants 2.5 kpc
there (debt #28); `CONCENTRATION_NORM` still holds 10 km/s of lever on row 3
(debt #12). One consequence measured rather than assumed: the advanced model's
iron-rich centre reaches the planets stage — giant occurrence 19% at 2 kpc against
2.6% in the simple model, and the sampled giant fraction 1.65% against 1.02% —
on debt #26 alone. `PLANETESIMAL_EFFICIENCY` itself holds, being a function
evaluation at [Fe/H] = 0 for one solar mass, and the published
`giant_occurrence` field is at the galaxy's *mean* stellar mass (0.46% at R₀),
which its `about` says and a reader could miss. The UNSET ratchet, loose for six
sessions, is at zero.

## Session 10 — the audit, run 2

### D97. The two audits diffed: what both found, what only one found, and why

**Decision.** Run 2's list is `AUDIT_RUN2.md` — fourteen defects D-1…D-14,
five convergence findings C1–C5, five performance findings P1–P5, a
constant-by-constant table (§4) and a green-row table (§5) — written and
committed at `ccc0a42` before `AUDIT_RUN1.md` or D96 were opened `[verified:
git log: ccc0a42 "S10 (run 2): the second audit sealed…" precedes this entry]`.
Run 1's list is `AUDIT_RUN1.md` §4, six items. The diff:

**Both found (5).** (1) Row 15 passes by construction on `BAR_LENGTH_RATIO`
(run 1 §4.1; run 2 §5). (2) The advanced model's iron-rich centre reaches the
planets stage — run 1: 19% at 2 kpc against 2.6%, sampled giant fraction 1.65%
against 1.02%; run 2, by its own probe: 0.189 against 0.026, 0.0165 against
0.0102 `[verified: AUDIT_RUN2.md §4.1]`. (3) Row 20 cannot be judged (zero-width
target, debt #17). (4) `chemistry_dtd` is the only stage worth a session (41%;
40.3% in run 2). (5) The advanced thick disc is absent and converged (debt #27).
**Every one of the five was in material run 2 was allowed to read** — the
register's amendments to debts #17, #21 and #24, the S10 lessons (one names
D96's 7×), and the brief's "known state" — and `AUDIT_RUN2.md` §0 marks each
**(known)**. They are agreement, not independent confirmation.

**Run 1 only (1).** The UNSET ratchet loose for six sessions (run 1 §4.6). Run
2 could not find it: run 1 lowered the bound to zero in the same commit and run
2 read it at zero `[verified: tests/test_registry.py::test_unset_defaults_are_owed_and_never_increase]`.

**Run 2 only (16).** D-1 `MERGER_DURATION` is dead: `merger_delivery` is read
by nothing, `sfh` delivers the merger's gas as a step, and 0.1–2.0 Gyr moves
every acceptance scalar by ≤ 3 × 10⁻¹⁵. D-2 the simple model's row-23 miss
carries a reason ("the young/old ratio is near the observed 1.75") that has
been false since S3 (it is 3.18; S3's own test pins 3.2). D-3 `SF_THRESHOLD`
at the top of its cited 5–10 gives row 2 = 1.709 (pass) and row 20 = 7.5 × 10⁹
with row 3 unmoved. D-4 row 3 has three explanations the register does not
name beside debt #18's: the c_vir→c₂₀₀ conversion (K = 3.5 → 247.97), z_f = 2.0
(248.17), `baryon_retention` = 0.30 (246.3). D-5 row 1 passes because the disc
carries the bulge's mass and row 10 because row 11 fails high. D-6
`GAS_DISC_SCALE_RATIO`'s "does nothing" is the steepest lever on rows 3, 4, 20
and 22. D-7 the Sagittarius default delivers 5.9 × 10⁹ M☉ of gas from 3.8 Gyr,
and without it row 2 reads 1.837, inside its target, in both models. D-8
"without migration the local spread is far too narrow" is refuted: 0.294 dex
without, 0.299 with. D-9 `vertical.scale_height` hard-codes G (rule A9). D-10
the advanced total metallicity reads 1.24 Z☉ at [Fe/H] = 0 with an unregistered
factor 2.0. D-11 the catalogue does not migrate, so the advanced model's
migrants reach neither the viewer nor the planets (local spread 0.19 in the
catalogue against the chemistry's 0.30). D-12 D95's "cold and warm agree at
every stage" is false at `pattern` (46×). D-13 `tools/scaling.py` labels a
warm number "cold". D-14 row 22's advanced pass is conditional on `WIND_INDEX`
= 2 (at the equally cited 1 it fails). Plus C2, the default grid is the
outlier under N_t (rows 1, 10 non-monotone at 0.2%, the step of D-1), and P3,
the 0.78 exponent is fixed cost, not sublinearity. **Three of run 1's verdicts
are contradicted**: `SECULAR_HEATING` "holds: set from an observation" (its
about line says it was re-chosen after row 6 failed; at 20 row 6 reads 176),
`SF_THRESHOLD` "holds: deliberately unfitted" (D-3), `GAS_DISC_SCALE_RATIO`
"holds" (D-6) `[verified: AUDIT_RUN1.md §3 against AUDIT_RUN2.md §4.1]`.

**Why run 1 missed them** [inferred from AUDIT_RUN1.md §3's method]. Run 1
asked rule B10's question literally — which constant was fitted against a
mechanism S9 changed — and answered it from the register and the about lines,
with one probe (the planets consequence). It did not (a) move each constant
across its own cited range and read the rows, which is where D-3, D-4, D-6,
D-14 and the three contradicted verdicts live; (b) trace published fields to
their readers (D-1, D-11); (c) re-read the miss register's prose against the
current numbers (D-2); (d) compare its profile's warm column with the cold one
per stage, or read the tool it quoted (D-12, D-13); (e) ask what an input
*default* delivers in mass (D-7). Run 1's own lesson about row 15 — ask of
every green row which constant could have made it green — was written at the
end of run 1 and applied by run 2 to every row; run 1 applied it to one.

**Why run 2 missed run 1's.** The ratchet was already at zero. Nothing else.

**What the diff says about the protocol.** The sealed file hid run 1's list and
not its conclusions: the register amendments and the lessons carried all five
overlaps across, so the overlap measures the leak rather than the agreement. A
protocol that wants two independent lists seals the register and the lessons
too, and lets the *first* run's amendments land in the diff. Recorded as a
lesson.

**Actions taken here, none of them physics.** Debts #29–#33 registered
(Sagittarius; the dead duration; the unmigrated catalogue; the spread claim;
the Z zero point) and #11, #12, #18, #28 amended with run 2's numbers. The
row-23 (simple) and row-22 (simple) miss texts in `galaxy/specs/spec.py`
corrected — the register is the record, and a wrong reason is a record defect
(rule B10), not a target change (rule B5): the rows still fail. No ratchet
lowered: nothing was discharged (UNSET 0, controls without a range 0). D-9,
D-12, D-13 and D-10's factor are one-line fixes queued in BRIEF.md for the
maintainer, because each changes a stage's declared reads or a tool's output
and belongs in a commit with its own test.

### D98. S10 closes: cold timings and the profile at run 2 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0002   1.39        940  -
    viewer: a module         0.0003   0.0002   1.39     21,599  -
    index                    0.0000   0.0000   1.67      1,237  -
    version                  0.0016   0.0014   1.18      1,132  -
    stages                   0.0002   0.0001   1.53      8,645  -
    fields                   0.0006   0.0004   1.44     57,008  -
    inputs                   0.0001   0.0001   1.52      9,091  -
    arrays: one profile      0.0733   0.0002 328.69      4,672  halo,assembly,disc,sfh
    arrays: history          0.1197   0.0023  52.86  6,401,472  halo,…,chemistry
    arrays: scalar           0.0729   0.0003 284.29      1,416  halo,assembly,disc,sfh
    region: one sector       0.1359   0.0032  42.52     18,720  halo,…,vertical
    region: whole disc       0.2425   0.1078   2.25  1,126,208  halo,…,vertical
    system: one star         0.1350   0.0020  67.80      2,816  halo,…,vertical
    adv: history             0.3334   0.0026 129.13  6,401,480  halo,…,chemistry_dtd
    adv: alpha plane         0.3394   0.0027 126.40  6,401,528  halo,…,chemistry_dtd
    adv: one sector          0.3459   0.0032 107.81     18,736  halo,…,chemistry_dtd,vertical_alpha
    adv: one star            0.3545   0.0021 168.35      2,824  halo,…,chemistry_dtd,vertical_alpha

    model simple: 0.433 s cold, 0.408 s warm
      sfh 16.5%  chemistry 9.3%  vertical 1.7%  pattern 2.2% (9.3 ms cold, 0.2 warm)
      systems 26.6%  formation 16.0%  planets 27.5%
    model advanced: 0.660 s cold, 0.640 s warm
      sfh 11.8%  chemistry_dtd 40.3%  vertical_alpha 1.4%  pattern 1.4%  formation 9.4%
      systems 17.8%  planets 17.6%
    catalogue at 20,000 stars: layout 0.014 s; one cell 0.0012 s (23), nine 0.0027 s (206), every cell 0.112 s (19,998)
    scaling: exponent in N_t 0.94 simple, 0.78 advanced, 2.03 naive; chemistry 6.51×; whole model 0.418 / 0.631 s in one warm process

**Read within the run.** Every row is within a few percent of D93's and D95's
— the same desktop `[verified: AUDIT_RUN2.md §1.3–1.5 against D93, D95]`. What
run 2 adds to the reading is D-12 and D-13: the one stage whose warm column is
a cache (`pattern`, the process's first `Generator`), and the one tool whose
"cold" is not. The shape is unchanged: the advanced chemistry adds ~0.22 s cold
to any route that reaches it; metadata runs no stage.

**Close.** The board row is ☑ (desktop, Fable 5.1, runs 1 and 2, `s10`,
2026-09-05); `session-10` is merged into `main` with `--no-ff`; `s10` is queued
in MANUAL_TODO.md with S9's SHA filled in from `origin/main`. The build's
eleven sessions are closed; BRIEF.md is written for a maintainer rather than a
session.

## Session 11 — the three S10 audits integrated

Surface: desktop. Model: Fable 5.1. Branch `session-11`, cut from `main` at
`ff12928`, the S10 merge. The repository held four S10 lists on three branches
after the audit was run six times — main's two runs (Fable 5.1), `session-10-beta`'s
two (Opus 5), and the blind pair `session-10-gamma` / `session-10-gamme-run-2`
(Fable 5.1) — and only main's was merged. This session brings the other two onto
`main` as findings, tests and three instrument features, and records the
four-way comparison the plan asked for (D102). No physics changed: the spec
counts are S9's, 11 / 7 / 6 and 8 / 11 / 5.

### D99. Integration by porting, not by merging: main is the base, the branches are sealed evidence

**Decision.** `main` stays as S10 left it (rule C2a: never rewritten) and the
three audit branches are never merged into it. What each holds is ported:
its register entries as new debts and amendments, its measurement tests
verbatim, and the instrument features that found something. The branches stay
on the remote unmerged, cited by name and SHA, as the sealed lists the
comparison rests on. Numbering, once: main's #29–#33 stand; beta's #29–#35
become **#34–#40** in beta's order; the pair's five become **#41** (row 20
counts hydrogen), **#42** (row 6 and the heating constants), **#43** (the
solar calibrations provisional on #18), **#44** (`KS_NORM`'s band), **#45**
(the infall ratio load-bearing). Ten existing entries take the other lists'
measurements (#12, #16, #17, #18, #21, #24, #26, #27, #28, #29); where lists
gave one quantity different numbers, #12 carries all three with what each
assumed. Decisions made on the branches are cited by branch (`session-10-beta
D95`), not copied; the four-way comparison and the choices this session made
are the only new entries.

**Settled by.** The branches conflict on fifteen files and hold four
implementations of the same two instruments; a textual merge would have
mangled the instruments and gained nothing, because the audits' value is in
what they found and the tests that pin it. Those port cleanly for a reason
that is itself a check: no branch changed physics, so every test that pins a
model measurement — the pair's eleven, gamma's three, beta's twelve — ran on
`main` unchanged and passed, 137 in the ported files `[verified: uv run pytest
tests/test_audit.py tests/test_halo.py tests/test_chemistry_dtd.py
tests/test_determinism.py tests/test_api.py tests/test_spec.py, 2026-09-07]`.
Not ported, and why: beta's convergence controls (main's sweep already proves it
can fire, on a stage built to drift), beta's and the pair's `convergence.py` and
`performance.py` wholesale (main's stay, with three features added in D101),
the pair's `Outputs.seconds` runner clock (main's profile times each stage's
compute directly, which is the same clock), and the branches' about-line edits
that carried one list's number where the register now carries three. What
`main` owed before this session — the one-line fixes and the physics decisions
in BRIEF.md — is untouched and still owed.

### D100. Debt #17: the table says "no testable target", and the debt stays open

**Decision.** `spec.Quantity.testable` is False for a pointwise row with
`lo == hi`; `spec.untestable()` lists such rows; the report names them once as
a table defect and the row's own reason reads "no testable target — debt
#17"; a new zero-width row must say so in its note or `Quantity` refuses it;
row 14 is exempt, being statistical. Rows 20 and 21 keep their zero width. The
implementation is beta's (`session-10-beta` D98) with the reason wording of the
pair's (`session-10-gamme-run-2` D97); `Quantity.width` is added for the
convergence sweep. Debt #17 stays **open** with its discharge condition — a
citation with an uncertainty, entered before the row is next judged — as it
does on main's and beta's registers.

**Settled by.** Four of the six runs built or chose this remedy; one,
`session-10-gamma` (D95), instead gave rows 14, 20 and 21 the half-unit of the
source's last printed digit. Both are recorded in the register and only one is
applied (rule B12). The argument that decides it is the project's own: an
interval chosen now is chosen with the model's answer for row 20 already known,
which is the move rule B5 exists to prevent, and it does not stop being that
move because the interval is small or because no failed row passes by it. The
objection gamma raised to this remedy — that "no testable target" would hide
row 20's miss — does not reach this implementation: row 20 still evaluates,
still prints its number, still fails, and is still a recorded miss under debt
#18 `[verified: tests/test_spec.py::test_the_report_names_the_table_defect;
tests/test_audit.py::test_debt_17_the_zero_width_rows_say_no_testable_target]`.
What the pair found about the *target* — that it is a hydrogen mass, debt #41 —
means the row's eventual interval will be judged against a different number in
any case.

### D101. Three instrument features ported: `vacuous`, the catalogue's fixed cost fitted, the one-off measured alone

    convergence (S11)   simple:   45 ok, 0 drift, 3 untestable,  0 vacuous, 6 statistical (row x axis)
                        advanced: 33 ok, 0 drift, 3 untestable, 15 vacuous, 6 statistical
                                  — rows 5, 7, 8, 9 and 11 read exactly 0 on every N_R, N_t and N_z (debt #27)
    performance (S11)   catalogue against sample size, cold, one fresh interpreter per model:
                        simple    5k 0.132 s  10k 0.142  20k 0.141  40k 0.147  -> 0.33 us per star, 134 ms fixed
                                  (95% of the catalogue at 20k does not depend on how many stars are asked for);
                                  layout 26.7 ms over all 1024 cells, 516 of them realise a star
                        advanced  5k 0.136 s  10k 0.120  20k 0.133  40k 0.153  -> 0.69 us per star, 123 ms fixed (90%);
                                  layout 19.4 ms
                        one-off, the first seeded draw of a fresh interpreter: 10.60 ms, then 0.024 ms (436x);
                                  billed by the per-stage table to `pattern` in both models

**Decision.** Main's `convergence.py` and `performance.py` stay and gain three
things the other audits' instruments had. (1) A pointwise row that reads exactly
zero at the default grid and at every swept grid is `vacuous`, not `ok`: nothing
moved because nothing is there (the gamma pair's D94; rule B9). It is not a
problem and fails nothing; a valley opening in the advanced model (debt #27) will
make those five rows ones the sweep judges for the first time `[verified:
tests/test_convergence.py::test_a_row_that_reads_zero_at_every_grid_is_vacuous_not_converged,
::test_the_production_scalars_hold_under_a_half_sweep]`. (2) `catalogue_cost`
times the whole catalogue at `SAMPLES` = 5k, 10k, 20k, 40k stars and fits a
straight line through (stars realised, seconds): the slope is the marginal cost
per star, the intercept the fixed cost, published with the layout's share and
the count of cells that realise a star (session-10-beta D96) `[verified:
tests/test_performance.py::test_the_catalogue_is_priced_per_cell]`. (3) The
first seeded draw is measured in its own interpreter (`--one-off`) and printed
beside the table rather than paid before the stage loop (session-10-beta D97)
`[verified: tests/test_performance.py::test_the_first_seeded_draw_is_measured_in_a_fresh_interpreter]`.
Also ported, from beta's D99: the one-`fetch` gate asks `git ls-files` what the
repository contains instead of walking the filesystem behind a denylist, which
is what made it fail on every desktop checkout with worktrees under `.claude/`.

**Settled by.** The numbers above, which settle two of D102's disagreements
without averaging them. On D61: the pruning main's run 1 measured is real (one
cell 1.3 ms, nine 2.9 ms) *and* the fixed cost beta and the pair measured is
real — 90–95% of the catalogue's time at the published sample does not depend
on the stars asked for, and about a fifth of that fixed part is the layout of
every cell whether or not anything asks. Debt #24 stays discharged for what it
said (a query pays for its own cells) and the cell grid's trade-off is debt
#36. On D95's "cold and warm agree at every stage": false at `pattern` by a
factor of hundreds, for a reason that belongs to the interpreter and not the
stage, and D95 now carries a note saying so rather than being rewritten (debt
#37). The two-point split beta first tried is recorded in `performance.py`'s
docstring because the negative number it returned was not obviously wrong to
look at. The `vacuous` count is the honest table: the advanced model's row 11 was
"converged" at 0 against a 6 × 10⁹ M☉ width, a green row earned by an absence.
`tools/scaling.py` was not re-run: no stage's cost changed (rule B7).

### D102. The four S10 lists side by side: main's two runs, beta's two, and the gamma pair

**Decision.** GALAXY_PLAN.md asked for S10 to be run twice and the defect lists
diffed, "the only controlled evidence this project will produce about whether
the model choice mattered". The repository ended with six runs and four lists.
This entry is their comparison, made from the branches read side by side, so
that the record the plan asked for is on `main`; it was first written on the
pair's branch (`session-10-gamme-run-2` D101) and is carried here with the
register numbers of this branch. The lists: **main** (`session-10`:
`AUDIT_RUN1.md` §4, six items; `AUDIT_RUN2.md` D-1…D-14, C1–C5, P1–P5; the two
diffed in D97; debts #29–#33), **beta** (`session-10-beta`: D94–D105, two runs
by one author aimed apart, diffed in its D105; debts #29–#35 there, #34–#40
here) and **the pair** (`session-10-gamma` D94–D102 and `session-10-gamme-run-2`
D94–D99, two blind runs from the S9 merge, diffed in the latter's D100; debts
#41–#45 here). Six runs in all, every one from S9's model on the desktop:
main's two and the pair's two on Fable 5.1, **beta's two on Opus 5**
`[verified: the S10 board row on each of the four branches]` — so beta against
the other two lists is the model comparison the plan asked for. Three lists
are independent of each other — main, beta, the pair — and inside main and
beta the second run knew the first (D97 §"what the diff says"; beta D105 §"what
it is worth"). Nothing below is averaged (rule B12).

**The common core: what every list found (5).**

1. **Debt #12's conversion is the size of row 3's miss or larger.** Measured
   by four of the six runs (main's run 1 only flagged it; beta's second run
   audited the instruments) — and given three different numbers,
   disagreement 1 below.
2. **Row 20 cannot be judged against a zero width.** Every list; the remedy
   split 4 : 1, disagreement 2, settled in D100.
3. **The advanced chemistry is 40–42% of its model, and the first `Generator`
   of a process lands on `pattern`.** main run 2 46×, beta 30× with the one-off
   measured alone at 8.9 ms, gamma 40×, the pair's run 2 50×. main run 1 alone
   wrote "cold and warm agree at every stage" and main's own run 2 corrected it
   (D-12).
4. **No acceptance scalar drifts across its width in N_R or N_t.** The worst
   is row 3 under N_t at 0.33–0.34 km/s of 6, 0.055 of a width, in every run;
   the advanced thick-disc rows read zero on every grid; rows 1 and 10 move
   non-monotonically in N_t at 0.2% (main C2, beta's margin lesson, both of
   the pair). main and beta also swept N_z (harmless, 3 × 10⁻⁷ dex/kpc); the
   pair did not.
5. **Housekeeping.** All four branches lowered the UNSET ratchet 1 → 0; none
   changed physics; the spec counts are S9's in every run.

**Where two or three lists overlap, with the numbers.**

- **The `GAS_DISC_SCALE_RATIO` sweep**: main run 2 (P5), gamma and the pair's
  run 2 read the same digits — 0.8 → 1.2 takes row 3 261.1 → 248.7, R_d 2.00 →
  2.97, row 20 4.32 → 7.25 × 10⁹, the simple gradient −0.047 → −0.018, row 2
  1.54 → 2.33. Filed three ways: main as D-6 and an amendment to #18, gamma as
  an amendment to #18, the pair's run 2 as a debt (#45 here, rule B11). beta
  did not sweep it; main run 1 wrote "holds".
- **`SECULAR_HEATING` is fitted to row 6**: main run 2 (P10: 20 → 176, 30 →
  347; row 7 883 / 1039 / 1231), gamma and the pair's run 2, which add the
  advanced model (326 pc; 429 at 30; `MERGER_HEATING` 287 → 392; #42 here).
  main run 1's "holds: set from an observation" is contradicted by its own run
  2 and by the pair.
- **`KS_NORM`'s own ±1σ contains row 2**: main run 2's round-3 probe (3.2 × 10⁻⁴
  → row 2 = 1.847, 0.007 above its bound; row 20 5.25 × 10⁹) and gamma's #29
  (#44 here) are the same numbers. Filed as "holds, load-bearing" on main and
  as a debt by gamma — disagreement 5.
- **The iron-rich centre reaches the planets**: main run 1 (19% giant
  occurrence at 2 kpc against 2.6%; sample fraction 1.65% against 1.02%),
  main run 2 (known), gamma (adds 0.43 against 0.07 inside 1 kpc). beta and
  the pair's run 2 measured the gas instead (beta: the centre is the wind, not
  the grid; the pair's run 2: `WIND_SPEED` sets the level, not the centre).
- **Row 15 is `BAR_LENGTH_RATIO × R_d`**: main run 1, main run 2 (known), the
  pair's run 2 (#21). Not gamma, not beta.
- **Debt #12's stated sensitivity is stale**: z_f = 2–3 spans 15.3 km/s on row
  3, not 10 — beta (15.29) and the pair's run 2 (15.3); z_f = 2.0 → 248.2 —
  main run 2 (P8) and the pair's run 2.
- **`WIND_SPEED` is fragile, in four forms**: main run 2 (fitted against a
  potential carrying row 3's excess, and evaluated on the present-day potential
  at every time: f_esc 0.78 early against 0.753), beta (K = 3.42 moves its refit
  by 0.01 dex), gamma (provisional on #18; −0.064 dex per +10%; #43 here), the
  pair's run 2 (800 → 1300 km/s is −0.32 dex at R₀ and 0.004 on row 22). The
  levers agree: main ±5% → ∓0.03 dex, row 22 ±0.0006 per 10%.
- **Migration's young/old ratio 3.2 / 3.1**: main run 2 (3.18 / 3.09; the
  stale row-23 miss text corrected on main) and the pair's run 2 (3.2 / 3.1;
  the 10 Gyr gradient as the discriminator, −0.105 / −0.129 without migration).
- **The harness's worktrees under `.claude/`** broke a tree-walking test on
  every desktop run: main run 2 (the hooks path), beta (D99: `git ls-files`,
  ported here), gamma and the pair's run 2 (skip the directory). One artefact,
  three fixes.

**Found by one list only.**

- **main only** (its run 2, unless said): `MERGER_DURATION` is dead and the
  merger's gas arrives as a step (#30); the Sagittarius default delivers
  5.9 × 10⁹ M☉ from 3.8 Gyr and without it row 2 passes at 1.837 in both models
  (#29); the catalogue does not migrate, spread 0.19 against 0.30 (#31);
  "without migration the spread is far too narrow" is refuted, 0.294 against
  0.299 (#32); Z(R₀) = 1.24 Z☉ with an unregistered 2.0 (#33);
  `vertical.scale_height` hard-codes G (D-9); `SF_THRESHOLD` = 10 closes rows 2
  and 20 with row 3 unmoved (D-3); `baryon_retention` = 0.30 passes rows 1–3
  (D-4); rows 1 and 10 pass by two cancellations and row 1's target includes
  the bulge (D-5); row 22's advanced pass is conditional on `WIND_INDEX` = 2
  (D-14); `tools/scaling.py` labels a warm run cold (D-13); `DTD_BINS` and
  `AGE_BIN` converged (C4); N_z has one consumer (C5); `DIP_DEPTH` decides row
  24 at a dip of 0.384 (§4.5). Fifteen items — the largest single list.
- **beta only** (Opus 5): the acceptance table reads nothing inside 4 kpc, so
  debt #26's +1.5 dex is invisible to it (#34); N_z buys nothing and
  `escape_velocity` is evaluated half a cell above the midplane it is declared
  at (#35); the default grid is 25× finer in radius and 80× in time than any
  row can detect, and `CELL_RINGS` is bound into a default argument (#36);
  `tools/timings.py` carries the 8.9 ms one-off unlabelled (#37); the
  statistical criterion rewards a noisier model and `ENSEMBLE_MIN` = 20 cannot
  deliver a central 95% — n = 41 would (#38); `world_seed` is read by nothing
  and the ensemble samples a diagonal (#39); the reproducibility check runs
  both halves in one interpreter (#40); K and z_f enter only as their product
  and the epoch row 3 wants, z_f ∈ [1.9, 2.1], is below the cited range; #16's
  discharge quantified at 10%; a coarse grid (N_t = 8) manufactures debt #27's
  valley; a too-coarse control point on every sweep knob; a two-point
  difference that returned a negative cost per star. Twelve.
- **the pair only**: row 20's target is hydrogen and the miss is 47%, not 28%
  (#41 — every other run wrote 28%); debt #27's prediction run, a fast inner
  disc opening `bimodal_wide` at the price of row 22 and finding the compact
  thick disc (main's nearest probe: n = 3 gives −0.0666 at row 2 = 1.29);
  `MERGER_HEATING` calibrates row 7 in one model and row 6 in the other (#42);
  #28 measured with no migration in both models (16× / 7×); `NET_YIELD`
  provisional on #18 (#43; main run 2: drifted −0.025 dex, harmless); row 3
  moves with n_R through the disc's quadrature (gamma D94); the `Generator`
  ceiling 0.13 s. Seven.

**Where the lists disagree on a number or a verdict (6).**

1. **How much debt #12's conversion is worth.** The pair: c₂₀₀ = 10.9 and row
   3 → 242.6, the NFW profile converted at Δ_vir = 101 ρ_crit
   (`tests/test_audit.py::c200_from_cvir`). beta: c₂₀₀ = 11.98 and row 3 →
   246.92, from the ratio of the model's R₂₀₀ = 212.94 kpc to the cited 255 kpc
   top-hat radius, 1.198 (`tests/test_halo.py`). main run 2: c₂₀₀ = 12.25 and
   row 3 → 247.97, K = 3.5 from a recalled factor "of order 0.8". Same sign,
   5.4 km/s apart; beta's and main's put the corrected row inside 245–251, the
   pair's 2.4 below it. Three conversions — one computed from the profile with
   its overdensity stated, one from an external radius, one recalled — and
   three discriminators proposed: rows 1 and 19 (main D-4), rows 2 and 20 (beta
   D95), rows 3 and 19 with z_f set jointly (the pair). Not averaged: debt #12
   carries all three, and this is BRIEF.md's physics item 3.
2. **Debt #17's remedy, 4 : 1.** "No testable target" or `untestable`: main run
   1 (the sweep only), beta (`Quantity.testable`, `untestable()`, a `SpecError`
   on a new silent zero-width row; row 14 exempt), the pair's run 2
   (`Quantity.testable`, statistical rows exempt); main run 2 took it as known.
   Gamma alone widened rows 14, 20 and 21 to printed-precision half-units.
   beta's D98 states the objection to gamma's move in advance: an interval
   chosen with the answer known is what rule B5 forbids; gamma's answer is
   that no failed row passes by it. Settled for `main` in D100.
3. **`MERGER_HEATING` in the advanced model.** main run 1: "no row reads the
   kick" until the valley opens. The pair: the advanced row 6 reads it — 287 →
   392 pc across 60–180 km/s, 52 pc at the default (274 without). Contradicted
   by a measurement (#42).
4. **D61 and debt #24.** main run 1: the catalogue's cost is proportional to
   the stars asked for, D61's fear "is not what the code does", #24 discharged
   in full. beta: 90% of the catalogue's 113 ms does not depend on the star
   count (0.59 µs per star), 14.9 ms lays out all 1024 cells whether or not
   anything asks, 163 µs per realised cell — D61 half right, the trade-off
   moved to a debt (#36 here). The pair: ~100 µs fixed per cell against ~2 µs
   per star, 70–78% of the stage per-cell setup, a 0.13 s ceiling; gamma 276 µs
   all-in per realised cell, 41–53% `Generator` construction. Every run agrees
   a nine-cell region query costs 2.6–2.9 ms, so the pruning is real; the
   registers disagreed on whether #24 is discharged. Resolved here without
   averaging: #24 stays discharged (nothing is paid for a cell a *query* did
   not ask for), the fixed cost is published by the instrument (D101) and its
   trade-off is #36. The marginal cost per star is 0.59 µs on beta and 1.5–2.2
   in the pair, different sample ranges, the same order.
5. **`KS_NORM`.** One probe, one set of numbers, two verdicts: "holds,
   load-bearing" (main run 2) against "not a check on the model by itself"
   (gamma). Registered here as #44: a standing condition, countable, with the
   probe cited.
6. **Row 20's miss.** 28% in main, beta and gamma; 47% in the pair's run 2,
   like for like (#41). Not two measurements — an accounting the other four
   inherited from S2. Every row-20 number on this register is now marked as
   the table's reading.

Two contradictions inside main are already on D97 and are not repeated here
(`SECULAR_HEATING` "holds", `SF_THRESHOLD` "holds").

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
run 1 has five (three on D97, `MERGER_HEATING` and #24 here); main run 2,
beta's two runs and the pair have none. So the weakest list in the repository
is a Fable run, and the distance between it and the next Fable run on the same
branch is larger than any distance between the Fable lists and the Opus one.
Read as the plan asked — did the model choice matter? — the answer six runs
give is that the **aim** decided what was found and the model did not,
visibly; a second Opus list, blind, is what would turn that reading into a
measurement `[inferred from the lists above; rule B12, nothing averaged]`.

### D103. Cold timings at S11 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0004   0.0002   1.55        940  -
    viewer: a module         0.0003   0.0002   1.45     21,599  -
    index                    0.0000   0.0000   2.07      1,237  -
    version                  0.0022   0.0017   1.27      1,132  -
    stages                   0.0002   0.0001   1.68      8,645  -
    fields                   0.0007   0.0004   1.61     57,008  -
    inputs                   0.0001   0.0001   1.66      9,091  -
    arrays: one profile      0.0840   0.0002 350.65      4,672  halo,assembly,disc,sfh
    arrays: history          0.1389   0.0032  43.03  6,401,472  halo,…,chemistry
    arrays: scalar           0.0881   0.0004 250.52      1,416  halo,assembly,disc,sfh
    region: one sector       0.1612   0.0035  45.72     18,720  halo,…,vertical
    region: whole disc       0.2890   0.1516   1.91  1,126,208  halo,…,vertical
    system: one star         0.1537   0.0021  72.42      2,816  halo,…,vertical
    adv: history             0.4206   0.0041 102.10  6,401,480  halo,…,chemistry_dtd
    adv: alpha plane         0.4281   0.0031 137.02  6,401,528  halo,…,chemistry_dtd
    adv: one sector          0.4355   0.0040 107.80     18,736  halo,…,chemistry_dtd,vertical_alpha
    adv: one star            0.4362   0.0022 197.09      2,824  halo,…,chemistry_dtd,vertical_alpha
    import + registry: 0.095-0.100 s, paid once per process and excluded from the cold column

    model simple:   0.505 s cold, 0.474 s warm   sfh 17.4%  chemistry 10.2%  systems 26.6%  formation 16.5%  planets 25.0%
                    pattern 0.0113 cold / 0.0004 warm (the one-off, D101)
    model advanced: 0.807 s cold, 0.760 s warm   sfh 11.1%  chemistry_dtd 41.1%  systems 18.1%  formation 9.3%  planets 17.5%

**Read within the run.** Every row is 15–25% slower than D98's on the same
desktop two days later — the machine, not the code: no stage's `compute` was
touched this session and the stages column is unchanged. The shape holds: the
advanced chemistry adds about 0.28 s cold to any route that reaches it and
nothing warm; metadata is sub-millisecond with no stage behind it; every cold
number on a stage-running route carries the 10 ms of D101's one-off, which is
12% of `arrays: one profile` and 2% of `adv: one sector` (debt #37).
`tools/scaling.py` not re-run (rule B7).

**Close.** The board gains row 11 (desktop, Fable 5.1, `s11`, 2026-09-07);
`session-11` is merged into `main` with `--no-ff`; `s11` is queued in
MANUAL_TODO.md with S10's SHA filled in. The three audit branches stay on the
remote, unmerged, as the sealed evidence D102 rests on.

## Session 12 — the maintainer's one-line fixes

Surface: desktop. Model: Fable 5.1. Branch `session-12`, cut from `main` at
`b1a6230`, the S11 merge. BRIEF.md's "owed first" list, done: five fixes, each
with a test, three debts discharged and one amended, no acceptance verdict moved.

### D104. Five one-line fixes, each with a test: G, two tool labels, the midplane, the cross-process check, the Ia factor

**Decision.** (1) `vertical.scale_height` takes `G` as an argument and both
vertical stages declare the read; the literal copy of G in `vertical.py` is gone
(AUDIT_RUN2.md D-9, rule A9) `[verified: tests/test_vertical.py::test_scale_height_reads_the_registered_G_not_a_copy]`.
(2) `tools/scaling.py`'s "whole model, cold" row is measured in a fresh
interpreter per model (D-13, rule B2) `[verified: tests/test_scaling.py::test_the_whole_model_row_is_measured_in_a_fresh_interpreter]`,
and `tools/timings.py` probes the RNG after each route's cold request and stars
the routes whose cold number carries the interpreter's first seeded draw, with a
footer (debt #37) `[verified: tests/test_timings.py]`. (3) The halo stage
publishes `halo_potential_midplane`, Φ(R, 0) exactly, and the advanced
chemistry's `escape_velocity` reads it instead of `halo_potential`'s first
z-row (debt #35) `[verified: tests/test_chemistry_dtd.py::test_the_midplane_escape_velocity_is_at_the_midplane_and_does_not_move_with_n_z]`.
(4) `determinism.check` and `report` run each production model in two fresh
interpreters under two `PYTHONHASHSEED`s and compare every field's bytes
(debt #40) `[verified: tests/test_determinism.py::test_the_spec_checks_reproducibility_across_processes_too]`.
(5) The Ia ejecta's metal-to-iron ratio is a registered constant,
`IA_METAL_TO_IRON` = 2.0 `[recall]`, read by `chemistry_dtd` (debt #33)
`[verified: tests/test_chemistry_dtd.py::test_the_ia_metal_to_iron_factor_is_a_registered_constant]`.
Debts #35, #37 and #40 are discharged; #33 keeps the zero-point question.

**Settled by.** Each was a claim the code did not honour: a rule quoted in the
file that broke it (A9), a label that said cold on a warm number (B2), a field
declared at the midplane and evaluated half a cell above it, a check that took
the one path immune to its defect (B3), a constant with no registry entry. What
the fixes moved: `escape_velocity` now reads the deeper plane value, so the
advanced model's wind loading shifts imperceptibly and the present-day gradient
reads −0.0565752 dex/kpc, from −0.0565751 at S11 — one part in 10⁶; no acceptance verdict changed and
the spec counts are S9's `[verified: python -m galaxy.specs, exit 0, 2026-09-07]`.
The midplane fix is the only one that touches a published number, and it is
the right number for what the field says. Not done, and why: the z axis itself
stays (debt #36 asks what it is for); `tools/timings.py` labels the one-off and
does not subtract it (rule B6); the total-Z zero point is a physics question,
not a registration.

### D105. Cold timings at S12 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0004   0.0003   1.21        940  -
    viewer: a module         0.0003   0.0003   1.07     21,599  -
    index                    0.0000   0.0000   0.94      1,237  -
    version                  0.0019   0.0021   0.91      1,132  -
    stages                   0.0002   0.0002   0.95      8,672  -
    fields                   0.0008   0.0006   1.29     57,707  -
    inputs                   0.0001   0.0002   0.56      9,091  -
    arrays: one profile      0.0895   0.0005 188.35      4,672  halo,assembly,disc,sfh
    arrays: history          0.1458   0.0027  54.23  6,401,472  halo,assembly,disc,sfh,chemistry
    arrays: scalar           0.0885   0.0003 299.29      1,416  halo,assembly,disc,sfh
    region: one sector*      0.1656   0.0037  44.30     18,720  halo,assembly,disc,sfh,chemistry,vertical
    region: whole disc*      0.3302   0.1400   2.36  1,126,208  halo,assembly,disc,sfh,chemistry,vertical
    system: one star*        0.1701   0.0021  79.99      2,816  halo,assembly,disc,sfh,chemistry,vertical
    adv: history             0.4571   0.0030 152.58  6,401,480  halo,assembly,disc,sfh,chemistry_dtd
    adv: alpha plane         0.4694   0.0026 183.54  6,401,528  halo,assembly,disc,sfh,chemistry_dtd
    adv: one sector*         0.4695   0.0035 134.72     18,736  halo,assembly,disc,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.4627   0.0022 211.18      2,824  halo,assembly,disc,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, numpy's bit-generator setup, about 10 ms here; measured alone by `python -m galaxy.specs.performance --one-off` (debt #37)
    import + registry: 0.100-0.117 s, paid once per process and excluded from the cold column

    model simple: 0.537 s cold, 0.528 s warm; import + registry 0.011 s
    catalogue against sample size: 5k:0.1426s 10k:0.1526s 20k:0.1481s 40k:0.1497s -> 0.10 us per star, 146.4 ms fixed (99% of the catalogue at 20k does not depend on how many stars are asked for); layout 17.7 ms over all 1024 cells, 516 of them realise a star
    one-off, first seeded draw: 11.28 ms then 0.025 ms (455x) — billed by this table to the first stage that draws (pattern); debt #37
    model advanced: 0.869 s cold, 0.844 s warm; import + registry 0.008 s
    catalogue against sample size: 5k:0.1296s 10k:0.1514s 20k:0.1411s 40k:0.1510s -> 0.39 us per star, 136.0 ms fixed (95% of the catalogue at 20k does not depend on how many stars are asked for); layout 16.8 ms over all 1024 cells, 516 of them realise a star
    one-off, first seeded draw: 11.28 ms then 0.025 ms (455x) — billed by this table to the first stage that draws (pattern); debt #37
    model simple: reproducible across processes (PYTHONHASHSEED ['0', '1']) OK
    model advanced: reproducible across processes (PYTHONHASHSEED ['0', '1']) OK

**Read within the run.** The starred rows are the ones whose cold number holds
the interpreter's first seeded draw — the routes that materialise objects —
which is what debt #37 asked the table to say; the arrays routes do not draw
and are unstarred. The shape is D103's on the same desktop; the halo stage
publishes one more profile and the vertical stages read one more constant,
neither measurable in these columns, so `tools/scaling.py` is not re-run (rule
B7). The determinism spec now prints its cross-process line per model.

**Close.** Board row 12 (desktop, Fable 5.1, `s12`, 2026-09-07); `session-12`
merged into `main` with `--no-ff`; `s12` queued in MANUAL_TODO.md with S11's
SHA filled in.

## Session 13 — the physics decisions

Surface: desktop. Model: Fable 5.1. Branch `session-13`, cut from `main` at
`701ab3a`, the S12 merge. BRIEF.md's seven decisions, taken in the order in
which each measurement informed the next: the step infall and Sagittarius
together (D106), the concentration (D107), the hydrogen target (D108), the
statistical criterion (D109), and the bulge and the catalogue probed and
recorded rather than built (D110). Every change was measured before and after
with the same probe; every number a test pinned was re-pinned to the new
measurement, never to a target (rule B5); three instrument defects the changes
exposed were fixed (D111). The acceptance table after: simple **11 pass, 7 fail**
(the same seven rows, row 3 now low instead of high), advanced **7 pass, 12
fail** (row 6 joins, a recorded miss under debt #42).

### D106. The merger's gas accretes from its own delivery windows, and Sagittarius delivers a physical share (debts #30, #29)

**Decision.** `sfh` no longer starts the second infall as a step at the last
major merger. It accretes `merger_delivery` — the assembly stage's per-event
Gaussian windows, each event's share at its own epoch — through the
exponential kernel's own recursion, normalised on the grid so that everything
delivered has arrived by the last step and the budget closes to rounding. The
Sagittarius default's gas share is 0.01 of the outstanding budget (about
3 × 10⁸ M☉), not 0.2 (5.9 × 10⁹): a 10⁸–10⁹ M☉ progenitor `[recall]` cannot
bring more gas than its own mass. `MERGER_DURATION` is read to some effect for
the first time since S3.

**Settled by.** The two are one change: with the step, a minor event's gas
arrived with the major one five Gyr early, and once the windows were wired in,
the unphysical 0.2 share landing at 8.8–13.8 Gyr took the present-day SFR to
2.70 and the simple thin disc to 241 pc — the default's error made visible by
fixing the mechanism that hid it. Measured with the physical share:

    Sagittarius gas share (windows in place):
      gas   row 2 sfr  row 20 gas   row 6 simple  row 9   row 11      row 6 adv   row 22 adv
      0.20   2.703     6.54e9       241.3         0.110   1.13e10     319.8       -0.0485
      0.05   2.069     5.90e9       251.7         0.143   1.36e10     350.4       -0.0542
      0.01   1.892     5.72e9       254.6         0.152   1.42e10     358.3       -0.0565
      0.00   1.848     5.67e9       255.3         0.154   1.44e10     360.3       -0.0572
    rows 1 and 10 against N_t (simple), 1000 / 2000 / 4000:
      before  5.2876e10  5.27619e10  5.28174e10   spread 0.22%, non-monotone (AUDIT_RUN2.md C2)
      after   5.28765e10 5.2874e10   5.28727e10   spread 0.007%, monotone
    Sagittarius' gas (infall with the event minus without, positive part): peak at 9.5 Gyr, was 3.8

Debt #30's prediction held in full. Debt #29's did not: it said row 2 would
pass with Sagittarius at a physical share, and the row reads 1.89 at 0.01 and
1.85 with no Sagittarius at all — the 1.837 it predicted was the step model's
number. So the residual excess is debt #18's timescale after all, as the entry
said it would then be, and the row-2 miss is rewritten to say so. Two other
rows moved with the physics: the simple thick disc grew (row 5 1.32 kpc, row 11
1.42 × 10¹⁰, the gate row 9 at 0.152 — still inside, still on the cancellation,
debt #19), and the advanced thin disc, which is every star, thickened to 358 pc
once no young gas arrived late — over its 350 ceiling, a new recorded miss under
debt #42, whose finding this is: `SECULAR_HEATING` and `MERGER_HEATING` were
fitted to the simple model's merger split (rule B10). Nothing was tuned back.
Both debts are discharged; `[verified: tests/test_sfh.py::test_the_merger_gas_arrives_at_its_own_epoch_and_the_grid_no_longer_sees_a_step,
::test_the_split_is_computed_not_assumed; tests/test_audit.py::test_debt_42_row_6_is_at_the_edge_of_its_window_in_both_models]`.

### D107. The concentration is converted from the virial overdensity, the epoch stays at the cited midpoint, and row 3 misses low (debt #12; debts #6, #11, #43)

**Decision.** The halo stage computes `c_vir = K(1 + z_f)` as Wechsler et al.
quote it, at Δ_vir(Ω_M) = 18π² + 82x − 39x² ≈ 101 ρ_crit `[recall: Bryan &
Norman 1998]` with a new Level 0 constant `OMEGA_M` = 0.3 (the value F_BARYON
already assumed), and converts it through the NFW invariant Δ c³/μ(c) to the
c₂₀₀ it builds the halo with, publishing both (`halo_concentration_virial`
14.35, `halo_concentration` 10.91). This is the gamma pair's conversion, chosen
over beta's (the ratio of the model's R₂₀₀ to a cited 255 kpc) and main's (a
recalled factor) because it is the one computed from the profile with its
overdensity stated (D102 disagreement 1). `halo_assembly_z` stays 2.5.
`WIND_SPEED` is refitted 1010 → 987 km/s.

**Settled by.**

    z_f     2.0     2.5     2.7     2.8     2.9     3.0     3.1     3.2
    v_tan  236.2   242.7   245.3   246.6   247.8   249.1   250.3   251.5   (target 245-251)
    c200    9.32   10.91   11.55   11.87   12.18   12.50   12.82   13.14   (c_vir at 2.5: 14.35)
    the conversion alone: 256.2 -> 242.7 km/s, 13.5 km/s; every other row moved by < 1e-9

Row 3 fell through its window and out the other side: 242.7, low by 2.3. The
epoch that would put it back inside is 2.7–3.1, the top of the cited 2–3, and
choosing it now would be choosing an input against a known answer — the move
rule B5 exists to prevent and both audits that touched this debt refused
(beta D95, the pair's D96). So the row is a recorded miss the other way,
debt #11 (the missing bulge) with debt #6 (contraction) as the lever, since
its old explanation — every baryon in the compact disc — now has the wrong
sign: an extended component lowers v_c(R₀) further. The refit is rule B10's
direct case: `WIND_SPEED` was fitted so the gas at R₀ is solar against a
potential built on the unconverted concentration; converted, v_esc(R₀) fell
578 → 562 km/s, the escape fraction rose 0.753 → 0.764 and the gas at R₀ read
−0.015 dex, so the constant was re-set by bisection to the value that restores
solar (−0.002 at 987; the lever is −0.065 dex per +10%) and its about line
records old and new. The advanced gradient stays inside at −0.056 (the tilt is
the wind's radial dependence, not its speed); `NET_YIELD` is left, its −0.025
dex drift being S3's and read by no row `[verified: tests/test_halo.py::test_the_concentration_is_converted_from_the_virial_overdensity,
::test_the_conversion_moved_row_3_and_nothing_else, ::test_the_epoch_row_3_wants_is_the_top_of_the_cited_range;
tests/test_audit.py::test_debt_12_the_concentration_is_converted_and_row_3_reads_low]`.

### D108. Acceptance row 20 reads the gas's hydrogen mass (debt #41)

**Decision.** `HELIUM_MASS_FRACTION` = 0.27 `[recall: solar; the disc's ISM is
near it, primordial 0.245]` is a Level 0 constant; `sfh` publishes
`hydrogen_mass_30kpc` = (1 − Y) × `gas_mass_30kpc`; row 20's field is the
hydrogen mass, its stated value and zero width unchanged. The metals' one to
two percent stays in, the sfh stage being upstream of the chemistry.

**Settled by.** The target is HI + H₂ from 21 cm and CO — hydrogen — and the
model's gas is every retained baryon the star formation law has not consumed,
so the table had been reading 28% for a 48% miss (4.17 × 10⁹ against 8.0 × 10⁹).
Nothing else changes: the miss is recorded under debt #18 as before, with the
component it asks for now sized at 3.8 × 10⁹ M☉ of hydrogen, 5.2 × 10⁹ of gas.
Rule B9 the other way round: a number shown as measured was measuring the
wrong thing `[verified: tests/test_audit.py::test_debt_41_row_20_compares_total_gas_with_a_hydrogen_mass;
tests/test_sfh.py::test_the_split_is_computed_not_assumed]`.

### D109. A statistical row passes on its median, and the ensemble is 41 (debt #38)

**Decision.** `spec.evaluate` passes a statistical row when the median of the
ensemble lies in the target; the central 95% interval is published beside the
verdict and no longer decides it. `ENSEMBLE_MIN` = 41, the smallest n at
which a 95% interval excludes one whole draw at each end. A statistical row
with a zero-width target is untestable like a pointwise one — row 14 joins
rows 20 and 21 (debt #17) — because no median meets a point either.

**Settled by.** The S0 criterion, "the interval intersects the target", passed
a median of 60 against [34, 52] on a spread of ±20 and rewarded a noisier
model monotonically; at n = 20 the "central 95%" trimmed no whole draw and was
pinned by the two most extreme values (beta's D102). Rows 16 and 17 pass on
their medians — 42.5 and 5.7, well inside — exactly as debt #38 said they
would, so the change costs no verdict today and would have cost one later. The
`judged` fixture and `python -m galaxy.specs` run 41 members per model, about
two seconds more `[verified: tests/test_spec.py::test_a_statistical_row_is_judged_on_its_median_not_on_its_reach,
::test_the_ensemble_size_and_the_central_fraction_agree_since_s13; tests/test_pattern.py::test_rows_16_and_17_are_judged_statistically]`.

### D110. The bulge and the catalogue: probed and recorded, not built (debts #11, #31, #42)

**Decision.** No bulge stage this session and no migration in the catalogue;
both are a session each and the plan sized them so. What this session did
instead was measure what the bulge would do — so that it is not built for the
wrong reason — and write the judgement rules down.

**Settled by.** The bulge probe: a Hernquist spheroid of the observed mass,
drawn from the stellar disc in proportion, and the rotation curve re-read at R₀
with the model's own razor-thin solver.

    M_b        a (kpc)   v_tan   change   thin disc after   row 10   thin if row 11 were right
    1.4e10     0.5-1.0   236-238  -4.8 to -6.3   2.84e10    in       3.29e10  in
    1.5e10     0.5-1.0   236-237  -5.1 to -6.8   2.77e10    in       3.19e10  in
    1.7e10     0.5-1.0   235-237  -5.8 to -7.7   2.62e10    in       2.99e10  in
    row 13, bulge/total: 1.5e10 / 5.29e10 = 0.284 (target 0.24-0.36)

**A bulge lowers row 3**, by 5–8 km/s: a flat disc rotates faster than the same
mass in a sphere, so moving 1.5 × 10¹⁰ M☉ from the disc into a spheroid takes
more from v_c(R₀) than the spheroid gives back. The register's assumption
since S1 — that the bulge "pushes row 3 the other way" — was the wrong sign,
and it was about to be written into row 3's new miss as its prediction when the
probe was run first (rule B4, the cheap way round). What the bulge is for: rows
10 and 11 stop passing on a cancellation (row 10 reads 2.6–3.3 × 10¹⁰ with a
bulge whether or not the thick disc is right), row 13 lands at 0.28, row 12 is
its own mass, and row 14 needs the source's uncertainty before it can be met
(debt #17). Row 3's remaining levers are the halo's contraction (debt #6) and
the epoch (D107). The catalogue (debt #31): the change is confined to
`systems.materialise` — draw a birth radius around the present one with the
migration kernel's width, look the abundance up there — for both models, and
it moves every seeded catalogue number the viewer and the planets read, so it
is a session with its own golden values; `feh_spread_sun`'s about now says the
viewer's stars do not carry its spread. Rows 6 and 7 in the advanced model are
judged together, both heating constants re-examined, when debt #27's valley
opens (debt #42); until then row 6 is a recorded miss and nothing is tuned.

### D111. What the physics exposed in the instruments, and what moved

**Decision.** Three defects fixed with the physics, none of them physics. (1)
The recursion's normalisation: a unit delivered in step j accretes over the
steps left, normalised on the grid — the continuous normalisation first tried
was a left-rectangle rule that over-accreted by dt/2τ and put the budget 0.08%
over; the test that closes it to 1e-4 caught it. (2) `determinism._equal`
treated a NaN scalar as differing from itself while the arrays already used
`equal_nan`; a fitted scale length that is NaN on the 16-cell test grid read as
irreproducible. (3) `tests/test_planets.py` asked the drawn giant fraction to
agree with the computed occurrence to 5%, inside the 7% binomial width of 200
giants in 20 000 stars — it had passed by luck; the tolerance is binomial now.
And every pinned measurement moved by the physics was re-pinned to the new
number with the old one in the comment: the audit tests (rows 2, 3, 5, 6, 9,
11, 20, the centre, the migration flattening, the heating sweeps, the ratio
sweep), the sfh, halo, spec, pattern and chemistry tests.

**Settled by.** The spec report, before → after: simple 11 / 7 / 6 → 11 / 7 / 6
with row 3's miss reversed in sign; advanced 8 / 11 / 5 → 7 / 12 / 5 with row 6
added; every failure recorded for its model, exit 0. Numbers to spot a
regression by: R200 212.94, c_vir 14.35, c200 10.91, R_d 2.49, M_star 5.287e10,
SFR 1.891, gas 5.714e9, hydrogen 4.171e9, v_tan 242.7 (both); simple grad −0.0236,
old −0.0064, thick M 1.42e10, row 9 0.152; advanced grad −0.0561, old −0.0195,
v_esc(R₀) 561.5, f_esc 0.757, spread 0.304, row 6 358.5 `[verified:
python -m galaxy.specs, 2026-09-07, exit 0]`.

    model simple: 45 ok, 0 drift, 3 untestable, 0 vacuous, 6 statistical (row x axis)
    model advanced: 33 ok, 0 drift, 3 untestable, 15 vacuous, 6 statistical (row x axis)

### D112. Cold timings at S13 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0003   1.00        940  -
    viewer: a module         0.0003   0.0003   1.00     21,599  -
    index                    0.0000   0.0000   1.01      1,237  -
    version                  0.0024   0.0017   1.45      1,132  -
    stages                   0.0005   0.0002   2.19      8,717  -
    fields                   0.0012   0.0006   2.05     59,264  -
    inputs                   0.0001   0.0001   0.90      9,399  -
    arrays: one profile      0.1087   0.0003 343.60      4,984  halo,assembly,disc,sfh
    arrays: history          0.1745   0.0034  51.28  6,401,776  halo,assembly,disc,sfh,chemistry
    arrays: scalar           0.1105   0.0003 334.76      1,720  halo,assembly,disc,sfh
    region: one sector*      0.1884   0.0037  51.12     19,032  halo,assembly,disc,sfh,chemistry,vertical
    region: whole disc*      0.3585   0.1568   2.29  1,126,456  halo,assembly,disc,sfh,chemistry,vertical
    system: one star*        0.1859   0.0021  87.93      3,120  halo,assembly,disc,sfh,chemistry,vertical
    adv: history             0.4890   0.0059  83.15  6,401,784  halo,assembly,disc,sfh,chemistry_dtd
    adv: alpha plane         0.5205   0.0032 161.26  6,401,840  halo,assembly,disc,sfh,chemistry_dtd
    adv: one sector*         0.5500   0.0059  93.44     19,040  halo,assembly,disc,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.5297   0.0028 188.28      3,136  halo,assembly,disc,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, numpy's bit-generator setup, about 10 ms here; measured alone by `python -m galaxy.specs.performance --one-off` (debt #37)
    import + registry: 0.108-0.119 s, paid once per process and excluded from the cold column

    model simple: 0.627 s cold, 0.608 s warm; import + registry 0.009 s
    catalogue against sample size: 5k:0.1341s 10k:0.1540s 20k:0.1652s 40k:0.1961s -> 1.65 us per star, 131.5 ms fixed (80% of the catalogue at 20k does not depend on how many stars are asked for); layout 18.4 ms over all 1024 cells, 516 of them realise a star
    one-off, first seeded draw: 12.40 ms then 0.027 ms (463x) — billed by this table to the first stage that draws (pattern); debt #37
    model advanced: 0.978 s cold, 0.946 s warm; import + registry 0.009 s
    catalogue against sample size: 5k:0.1532s 10k:0.1662s 20k:0.1585s 40k:0.1784s -> 0.60 us per star, 152.9 ms fixed (92% of the catalogue at 20k does not depend on how many stars are asked for); layout 18.7 ms over all 1024 cells, 516 of them realise a star
    one-off, first seeded draw: 12.40 ms then 0.027 ms (463x) — billed by this table to the first stage that draws (pattern); debt #37

**Read within the run.** The shape is D105's on the same desktop. `sfh` carries
one more array recursion and the halo a bisection, neither measurable in these
columns; the ensemble is twice the size, which is the spec runner's cost and
not a route's. `tools/scaling.py` not re-run: no stage's cost changed within
its resolution (rule B7).

**Close.** Board row 13 (desktop, Fable 5.1, `s13`, 2026-09-07); `session-13`
merged into `main` with `--no-ff`; `s13` queued in MANUAL_TODO.md with S12's
SHA filled in.

## Session 14 — the physics the maintainer's brief listed

### D113. The halo contracts around the disc, and the register's number for it was wrong by an order of magnitude (debts #6, #12, #43, #46)

**Decision.** The halo stage solves the halo's adiabatic contraction around
the disc on its own radial mesh — 600 log-spaced points from 10⁻³ kpc to 1.5
R₂₀₀ — and every profile it publishes is the contracted one: `halo_enclosed_mass`,
`halo_circular_velocity`, `halo_potential`, `halo_potential_midplane` and the
scalar at R₀. The invariant is Gnedin et al. 2004's ``r M(r̄)`` with ``r̄ = A R₂₀₀
(r/R₂₀₀)^w`` at A = 0.85, w = 0.8 `[recall]`, two new Level 0 constants
`CONTRACTION_A` and `CONTRACTION_W`; Blumenthal et al. 1986's circular-orbit
invariant is A = w = 1, kept as the named alternative and not averaged in
(rule B12). The disc it contracts around is the MMW98 exponential — M_d = m_d
M₂₀₀ at R_d = λ_d R₂₀₀/√2, its cylindrical enclosed mass taken as spherical —
so the scale length is computed by the halo stage now and the disc stage reads
it (rule A9). Two fields are new: `halo_contraction`, the shell displacement
r_i/r_f on R, and `halo_circular_velocity_sun_initial`, the halo's share at R₀
before it responded, so the contraction can be read off as a difference the way
`halo_concentration_virial` lets the conversion be read. The ruleset was chosen
on the literature and written into the constant's about line **before the row
was read**, so that the number could not choose the physics (rule B5). Debt #6
is discharged; the contraction's strength is debt #46; `WIND_SPEED` is refitted
987 → 1028 km/s (debt #43, rule B10) because the deeper potential raised
v_esc(R₀) 562 → 585 km/s and the gas at R₀ read +0.026 dex.

**Settled by.** The register had carried the contraction since S13 as "several
km/s at R₀" `[recall: Blumenthal et al. 1986]`, the lever that would close row 3
from 242.7. Measured:

    ruleset                          A     w    halo v_c(R0)  r_i/r_f(R0)  row 3    v_esc(R0), adv
    none (until S14)                 -     -    138.6         1.000        242.7    561.5
    Gnedin et al. 2004  (default)    0.85  0.8  181.4         1.419        270.8    584.8
    Blumenthal et al. 1986           1.0   1.0  195.6         1.572        280.9    593.0
    A = 1.6, w = 0.8 [recall, weak]  1.6   0.8  160.8         1.209        256.8    570.8
    the epoch, Gnedin:  z_f 0.5 243.4 | 0.6 244.9 | 0.7 246.4 | 0.8 247.9 | 0.9 249.4 | 1.0 250.9 | 1.1 252.3
                        1.5 257.9 | 2.0 264.5 | 2.5 270.8 | 3.0 276.7   (target 245-251; c200 at 0.7-1.0: 5.2-6.2)
    baryon_retention:   0.25 245.5 (M_star 3.7e10, row 1 fails) | 0.30 258.6 | 0.35 270.8
    GAS_DISC_SCALE_RATIO 1.5 (debt #45's sweep): row 3 253.0, was 222.7
    every other row: < 1e-9 between rulesets; the advanced escape fraction at R0 0.757 -> 0.740 -> 0.756 after the refit

The prediction failed the other way, by eight half-widths: the disc this model
builds — 5.8 × 10¹⁰ M☉ in one exponential at 2.6 kpc inside a c₂₀₀ = 10.9 halo
— pulls the halo's share at R₀ up by 43 km/s under the weaker published
invariant and 57 under the stronger, and row 3 reads 270.8, high by 20. So the
epoch the row wants is 0.7–1.0, not the 2.7–3.1 of D107, and it lies below the
cited 2–3 by as much as it lay above it before; every epoch the register has
quoted, and all three S10 conversions, were read against an uncontracted halo.
The miss is rewritten under debt #12 with its prediction: the bulge (D110,
5–8 km/s the right way now) and debt #18's component together do not close
it, and the epoch has to fall below 2 — or the calibration of the invariant
is wrong for a disc galaxy, which is what debt #46 says a mass- and
epoch-dependent (A, w) would test. A second discriminant overshoots the same
way: the advanced model's escape velocity at R₀, 585 km/s against the 530–580
commonly measured `[recall]`.

**The instrument, and the defect it found** (rule B1). Three checks were written
before the physics was read: with no disc every invariant returns r_i = r_f to
4 × 10⁻¹⁶ and the potential to 7 × 10⁻⁶ (the trapezoid in ln r); quadrupling the
mesh moves v_halo(R₀) by a part in 10⁶; and a third (A, w) was probed beside the
two named ones. The third probe read the default's number back to the digit —
274.7 for A = 0.85 and for A = 1.6 alike — because the first solver attached
the final dark mass to the orbit-averaged radius r̄_f, and with the mass at r̄
on both sides A is a relabelling of the mesh and cancels exactly. Gnedin's
shell keeps its mass at its own radius: the dark mass inside r_f afterwards is
what was inside r_i before. Fixed, the three read 181.4, 195.6 and 160.8, and
the default's row 3 moved 274.7 → 270.8. The Blumenthal number was never
wrong, which is why two rulesets would not have found it `[verified:
tests/test_halo.py::test_a_third_ruleset_reads_a_third_number,
::test_with_no_disc_the_halo_comes_back_unchanged, ::test_the_mesh_does_not_move_the_scalars,
::test_the_named_rulesets_and_what_each_is_worth_at_R0, ::test_the_epoch_row_3_wants_is_below_the_cited_range,
::test_the_scale_length_is_the_halos_now_and_the_disc_reads_it; tests/test_sfh.py::test_row_3_misses_high_once_the_halo_contracts]`.

**What else moved.** The resolved rotation curve is higher everywhere inside
R₂₀₀, so the bar's pattern speed and corotation (rows 16, 17: medians 43.3 →
44.9 km/s/kpc and 5.25 → 5.82 kpc, inside), the shear at 2.2 R_d (0.924 →
0.944) and the disc dominance (0.550) moved with it; the advanced gradient
reads −0.058 (from −0.056, inside), the old-star gradient −0.0202, and the
centre holds more metal (peak [Fe/H] 1.39 out to 2.66 kpc, from 1.36 and 2.5).
Rows 1, 2, 4–11, 19, 20 and every mass are unchanged to 10⁻⁹: the contraction
enters only through the kinematics and the potential. Every pinned measurement
was re-pinned to the new number with the old beside it (S13's lesson); the
potential's test no longer asserts the analytic NFW curve but that the field is
deeper than it everywhere and spherical.

### D114. The extended component, probed and not built: on the disc's own timescale it buys row 20 with row 2 (debt #18)

**Decision.** No second accretion channel this session. What was measured
instead, so that the next decision is taken on numbers (rule B4, the way S13
took the bulge): a share s of the budget accreting with scale length k R_d on
the same inside-out timescale, the halo contracting around the same
two-component disc. Both halves are substituted through one function each —
`sfh.infall_profile`, factored out of the stage for the purpose with no change
in behaviour, and `halo.disc_enclosed_mass` — and the repository is unchanged.

**Settled by.** Rows 2, 3, 4, 20 and 22 (the advanced model's), with the simple
model's thin disc and thick-disc gate beside them:

    s     k   row 2 SFR   row 3 v_tan (halo share)   row 4 R_d   row 20 H     row 22 adv   row 6   row 5   row 9
    0     1   1.891 out   270.8 out  (181.4)         2.49 in     4.17e9       -0.0582 in   255     1.32    0.152
    0.1   2   1.982 out   267.1 out  (180.6)         2.57 in     4.91e9       -0.0550 in   249     1.44    0.154
    0.2   2   2.090 out   263.4 out  (179.8)         2.66 in     5.55e9       -0.0523 in   243     1.56    0.155
    0.3   2   2.210 out   259.6 out  (179.0)         2.77 in     6.11e9       -0.0502 in   238     1.68    0.156
    0.1   3   1.985 out   265.1 out  (179.9)         2.56 in     5.52e9       -0.0548 in   254     1.44    0.152
    0.2   3   2.129 out   259.2 out  (178.3)         2.65 in     6.65e9       -0.0520 in   254     1.56    0.152
    0.3   3   2.316 out   253.2 out  (176.6)         2.75 in     7.57e9       -0.0496 in   254     1.69    0.152
    0.1   5   1.963 out   263.4 out  (179.0)         2.55 in     6.14e9       -0.0554 in   261     1.41    0.151
    0.2   5   2.146 out   255.8 out  (176.5)         2.61 in     7.77e9       -0.0529 in   268     1.51    0.149
    0.3   5   2.453 out   247.9 IN   (173.9)         2.69 in     8.92e9       -0.0507 in   276     1.62    0.147
    the two halves at s = 0.2, k = 3: the profile alone takes row 3 to 261.5 (-9.3), the halo's weaker response alone to 268.5 (-2.3)

Every setting lowers row 3 — the baryons' own pull by 4 to 13 km/s and the
halo's response by 1 to 7 — and lifts row 20 toward its 8 × 10⁹ M☉ of hydrogen,
and every setting lifts row 2 with it, 1.98 to 2.45 against 1.46–1.84: gas at
2–5 R_d that accretes on the disc's timescale is still above the star
formation threshold when it arrives, so the register's premise — that the
threshold would protect it — does not hold for a component that accretes as
the disc does. Row 4 broadens, 2.49 → 2.55–2.77 and inside, so by the
register's own check the component is not high enough in angular momentum;
row 22 stays inside at every setting (the wind's tilt, not the infall's, D95)
and the simple model's thick-disc gate barely moves. The one setting that puts
row 3 inside, s = 0.3 at k = 5, costs row 2 a third. So the component the
register wants must arrive late enough or diffuse enough to stay under the
threshold — a timescale of its own, not only a scale length — and that is a
second decision, not a constant to sweep: recorded under debt #18, not built.
Row 3's miss keeps its prediction (D113): the bulge and the component together
do not close it without the epoch moving.

### D115. Cold timings at S14 (rules B2, B6, B7)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0007   0.43        940  -
    viewer: a module         0.0003   0.0003   0.96     21,599  -
    index                    0.0000   0.0000   0.95      1,237  -
    version                  0.0058   0.0017   3.41      1,132  -
    stages                   0.0009   0.0002   4.18      8,845  -
    fields                   0.0008   0.0006   1.27     61,337  -
    inputs                   0.0001   0.0001   0.93      9,399  -
    arrays: one profile      0.1109   0.0003 350.45      4,976  halo,assembly,sfh
    arrays: history          0.1989   0.0033  60.68  6,401,768  halo,assembly,sfh,chemistry
    arrays: scalar           0.1264   0.0005 263.93      1,712  halo,assembly,sfh
    region: one sector*      0.2538   0.0034  74.39     19,024  halo,assembly,sfh,chemistry,vertical
    region: whole disc*      0.3987   0.1936   2.06  1,126,448  halo,assembly,sfh,chemistry,vertical
    system: one star*        0.2211   0.0021 104.24      3,112  halo,assembly,sfh,chemistry,vertical
    adv: history             0.6478   0.0034 189.83  6,401,776  halo,assembly,sfh,chemistry_dtd
    adv: alpha plane         0.6449   0.0026 243.79  6,401,832  halo,assembly,sfh,chemistry_dtd
    adv: one sector*         0.6325   0.0035 182.39     19,032  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.6866   0.0049 141.01      3,128  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, about 10 ms here; measured alone by `python -m galaxy.specs.performance --one-off` (debt #37)
    import + registry: 0.105-0.153 s, paid once per process and excluded from the cold column

    model simple: 0.575 s cold, 0.617 s warm; halo 0.0030 s (0.0008 until S14: the contraction mesh), sfh 19%, systems 26%, planets 26%
    model advanced: 0.905 s cold, 0.946 s warm; halo 0.0030 s, chemistry_dtd 41%
    catalogue against sample size: simple 1.82 us per star, 109.0 ms fixed (77%); advanced 1.88 us, 132.8 ms fixed (78%)
    one-off, first seeded draw: 10.45 ms then 0.024 ms (430x), billed to pattern; debt #37

    scaling (tools/scaling.py):
    chemistry stage        N_t=500    N_t=1000    N_t=2000    N_t=4000    N_t=8000  exponent
    simple                  0.0140      0.0264      0.0543      0.0986      0.2109      0.97
    advanced                0.1471      0.2153      0.3780      0.7074      1.3421      0.81
    naive DTD (tool)       N_t=250     N_t=500    N_t=1000    N_t=2000  exponent: 2.10
    advanced chemistry / simple chemistry at N_t = 2000: 7.09x
    whole model, cold (fresh interpreter): simple 0.830 s, advanced 1.221 s (1.47x)

**Read within the run.** Two things changed shape. The halo stage costs 3 ms
where it cost 0.8: the contraction mesh, 600 points solved by 80 vectorised
bisection steps and one trapezoid, a fixed cost with no dependence on N_R, N_t
or N_z (the mesh is the halo's own), so the scaling exponents are the chemistry
stage's as before and `tools/scaling.py` was re-run only to say so. And the
`disc` stage has left the stage column of every route: the sfh stage reads the
scale length from the halo now (D113), so the closure above the acceptance
fields no longer contains the checkpoint-1 preview, which runs only when its
own fields are asked for (rule D4). Nothing else moved outside the desktop's
noise; the whole-model rows read 0.83 / 1.22 s against D105's 0.63 / 0.98 in a
fresh interpreter, which is the machine's variance on the day (D112 read 0.63 /
0.98 warm-process), not a regression: the per-stage table is within 10% of S13's
everywhere but the halo `[verified: python -m galaxy.specs, tools/timings.py,
tools/scaling.py, 2026-09-07]`.

**A flake, recorded.** `tests/test_performance.py::test_the_catalogue_is_priced_per_cell`
failed once in the close's full run, in both models, on a *negative* fitted
per-star cost (-6.3 and -1.1 us) and passed twice when run alone: at n = 2000
the slope is about 2 ms of signal over 100 ms of fixed cost, and the desktop's
noise flips its sign. Not this session's physics - the catalogue is untouched -
and not fixed here: the S11 lesson (fit over a range wide enough to condition
the slope) applies to the test's own sample, which is the maintainer's to widen.

**Close.** Board row 14 (desktop, Fable 5.1, `s14`, 2026-09-07); `session-14`
merged into `main` with `--no-ff`; `s14` queued in MANUAL_TODO.md with S13's
SHA filled in. **Merged twice.** The first merge (780cd15) carried RESUMING.md
three lines over its cap: the close's shell chain tested the exit status of the
`tail` that printed the suite's last line, not the suite's, and the failing
`test_resuming_is_capped_at_120_lines` did not stop the merge or the push. Rule
C2a forbids the force-push that would hide it, so the file is trimmed and merged
again, and the second merge — the one `s14` names, and the one `rev-list -1
--grep` finds — is the state verify_clone ran on.

### D116. The completion plan: S15–S22, with the model each runs on (GALAXY_PLAN.md §5d)

**Decision.** At the owner's request after S14, GALAXY_PLAN.md gains §5d — the
eight sessions that finish the project, each with a deliverable, a gate read
from `spec.py`, and a model — and the board carries them as open rows, so the
generated bar reads 15 of 23 and `tools/progress.py` names S15 as next. Done is
defined: every row green or a recorded miss whose cause is a mechanism, every
debt discharged or ruled permanent with its reason, every field previewed, the
tag batch applied, `verify_clone` OK.

**Settled by.** The model rule is the one the project's own evidence supports.
S10's six runs found the aim mattered and the model did not (D102); what
separated the sessions since was whether a wrong answer could pass the gate.
So Fable takes the sessions where verification is weakest — S15 (what row 3's
cause is), S16 (the component's timescale), S18 (a cancellation that could be
tuned into passing), S20 (the valley, with its coarse-grid false positive) and
one of S21's two audits — and Opus takes the gated builds S17, S19 and S22 and
the other audit, the way S1–S8 were built and passed. S21 reserves its debt and
decision numbers before it starts (S11's lesson). What the plan does not
promise is written beside it: the debts that are properties of the model's
scope are ruled on at S22, not closed `[inferred]`.

### D117. Row 3's cause: the assembly epoch's default is derived, the contraction's calibration is not the lever, and what is left is the baryons (debts #12, #46, #11, #18, #43)

**Decision.** `halo_assembly_z`'s default is 1.66, derived: the epoch at which
the ΛCDM median halo of the default mass assembled — c₂₀₀ = 10^(0.905 − 0.101
log₁₀(M₂₀₀ h/10¹² M☉)) = 8.25 at z = 0 `[verified: Dutton & Macciò 2014, Planck;
h = 0.7 here]`, converted to c_vir = 10.92 at Δ_vir through the NFW invariant
(D107) and read back through K = 4.1 as z_f = c_vir/K − 1. The old default,
2.5, was the midpoint of §3's "z ≈ 2–3" and was justified by c₂₀₀ = 14.4 landing
inside the 10–18 the Milky Way's measurements span; K is a dark-matter-only
calibration `[verified: Wechsler et al. 2002, c_vir = c₁/a_c, c₁ = 4.1, Ω_M = 0.3,
σ₈ = 1.0]`, so the concentration it gives is the halo's *before* it contracted
around the disc (D113), and the measurements are fits to the halo *after*. The
halo stage publishes two more scalars so that the comparison is between like
things: `halo_concentration_contracted`, the c₂₀₀ of the NFW halo of the same
dark mass enclosing the same mass inside R₀ as the contracted one (18.5 at 2.5,
over; 15.4 at 1.66, inside), and `halo_density_sun`, the dark-matter density at
R₀ in M☉/pc³, the one halo property measured without the rotation curve. The
contraction stays Gnedin et al. 2004's at (0.85, 0.8) with Blumenthal's named
(rule B12); A = 1.6 at w = 0.8 reads 245.6 now, inside, and is not adopted. Row
3 reads 260.1, a recorded miss under debt #11 whose prediction names the bulge
(D110, S17) and the extended component (D114, S16). `WIND_SPEED` is refitted
1028 → 999 km/s (rule B10, debt #43). Debt #12 is discharged; #46, #11, #18 and
#43 are amended. GALAXY_PLAN.md §5d's reserved D-numbers are restated as counts
fixed when S21 opens, because decisions are numbered sequentially by a test and
this one is D117.

**Settled by.** The three levers read against three discriminants, the repo
unchanged, before anything was decided (the plan's "probe before build"):

    ruleset       z_f   c_vir  c200   c_eff   halo v(R0)  r_i/r_f  rho(R0) Msun/pc3  GeV/cm3  row 3   v_esc(R0) adv
    Gnedin 2004   0.7    6.97   5.20  11.84    144.7      1.667    0.0066            0.25     246.4   548.8
    Gnedin 2004   1.0    8.20   6.15  12.97    151.8      1.604    0.0073            0.28     250.9   555.3
    Gnedin 2004   1.5   10.25   7.73  14.84    162.6      1.524    0.0083            0.32     257.9   565.8
    Gnedin 2004   1.66  10.91   8.24  15.43    165.8      1.503    0.0087            0.33     260.1   569.0   <- default
    Gnedin 2004   2.0   12.30   9.32  16.68    172.4      1.464    0.0094            0.36     264.5   575.6
    Gnedin 2004   2.5   14.35  10.91  18.50    181.4      1.419    0.0103            0.39     270.8   584.8   <- until S15
    Gnedin 2004   3.0   16.40  12.50  20.31    189.8      1.383    0.0112            0.43     276.7   593.2
    Blumenthal    1.66  10.91   8.24  17.0     180.6      1.680    -                 -        270.2   -
    A=1.6, w=0.8  1.66  10.91   8.24  -        143.3      -        -                 -        245.6   -
    LCDM median c200 8.25 -> z_f 1.66; +-0.11 dex -> 1.08-2.41.  Cautun et al. 2020's Auriga response at R0:
    180.3 at z_f 2.5 (Gnedin 181.4), 163.6 at 1.66 (165.8).  Measured: c 10-18 (post-contraction fits);
    rho 0.3-0.5 GeV/cm3 (global analyses); v_esc(R0) 533 +54/-41, 528 +24/-25; MW pre-contraction c 9.4 +1.9/-2.6.

Three things the table says. **The epoch's validation compared unlike things**:
at 2.5 the pre-contraction c₂₀₀ of 10.9 sat inside the measured span and the
post-contraction fit, which is what the span measures, sat above it; at the
median epoch the fit is inside and the Milky Way's own pre-contraction
concentration, 9.4 (+1.9/−2.6) `[recall: Cautun et al. 2020, Table 2]`, brackets
the median (z_f 2.0, +0.6/−0.9), and its local density, 8.8 × 10⁻³ M☉/pc³, is
what the model reads at 1.7. **The calibration is not the lever**: the recalled
"mass- and epoch-dependent (A, w)" that debt #46 and §5d named as the untried
form does not exist — Gnedin et al. 2011 find no correlation of A or w with
either and write that the response cannot be reduced to a prescription
`[verified: arXiv:1108.5736, read this session by a read-only agent]` — and the
modern Auriga calibration `[verified: Cautun et al. 2020, eq. 11]` agrees with
the default invariant at R₀ to 2 km/s, so the number that would land the row
(A = 1.6) is the one two calibrations agree against. **The local density does
not discriminate**: the response raises the dark mass inside R₀ by 70% and the
density there by 16%, because it steepens the profile inside R₀ more than it
raises it at R₀, and every epoch from 1 to 3 reads inside the measured span.
The expectation before the probe was a factor of two; the number was measured
before the about line was written (S14's lesson, rule B4).

So the epoch is derived and the row still misses, by 9–15 km/s, with the
baryons as the cause: 5.9 × 10¹⁰ M☉ in one exponential at 2.6 kpc, no bulge, no
extended component. The bulge's 5–8 (D110) and the component's 4–13 (D114)
together span 9–21, so the prediction is that S16 and S17 close it with the
epoch at 1.66; if they do not, the invariant is the remaining suspect and its
test is w swept at A = 1.6 against rows 3, 19 and the escape velocity together.
Not levers: the epoch below 1.08, outside the relation's scatter; a baryon
retention of 0.25, which fails row 1. Rule B5 is kept the way the audits kept
it — the default was not chosen against the row, and the row is not inside.

**The instrument** (rule B1). Both scalars were tested before a number was read:
with no disc the mesh density matches the analytic NFW density to a part in 10⁴
away from the mesh's ends and the effective concentration returns the halo's
own c to 10⁻⁵, and quadrupling the mesh moves neither `[verified:
tests/test_halo.py::test_with_no_disc_the_density_and_the_effective_concentration_are_the_nfw_ones,
::test_the_mesh_does_not_move_the_density_or_the_effective_concentration,
::test_the_stage_publishes_both_in_the_units_a_measurement_quotes]`. The
derived default is reproduced from the relation, the cosmology and K by a
test, with the scatter's ends and the old value outside them `[verified:
tests/test_registry.py::test_the_epochs_default_is_the_lcdm_median]`.

**What moved.** The less concentrated halo responds more (r_i/r_f at R₀ 1.42 →
1.50, the central ratio 2.22 → 2.51) and its share at R₀ falls 181.4 → 165.8
(119.3 before the response, 138.6 until S15); row 3 270.8 → 260.1 in both
models; the conversion of D107 is worth 10.7 km/s at this epoch (12.4 at 2.5).
The advanced model: v_esc(R₀) 584.8 → 569.0, inside 530–580; the gas at R₀
read −0.019 dex at 1028 and `WIND_SPEED` was bisected to 999 (0.000 dex); the
escape fraction at R₀ 0.7556 → 0.7552, the gradient −0.0582 → −0.0578 (inside),
the old-star gradient −0.0202 → −0.0201. Rows 16 and 17: medians 44.9 → 43.2
km/s/kpc and 5.82 → 5.82 kpc, inside. Rows 1, 2, 4–11, 19, 20, every mass and
every simple-model gradient: unchanged to 10⁻⁹. Debt #45's sweep re-read:
`GAS_DISC_SCALE_RATIO` = 1.5 takes row 3 to 241.5 (253.0 at S14). Every pinned
measurement re-pinned with the old number beside it `[verified:
tests/test_halo.py::test_concentration_from_the_assembly_redshift,
::test_the_disc_is_not_counted_twice, ::test_the_concentration_is_converted_from_the_virial_overdensity,
::test_the_conversion_moved_row_3_and_nothing_else, ::test_k_and_the_assembly_epoch_enter_only_as_their_product,
::test_the_named_rulesets_and_what_each_is_worth_at_R0; tests/test_sfh.py::test_row_3_misses_high_once_the_halo_contracts;
tests/test_audit.py::test_debt_12_the_concentration_is_converted_and_row_3_reads_low,
::test_debt_45_the_infall_scale_ratio_trades_the_structure_rows_against_the_gas_rows;
tests/test_registry.py::test_defaults_are_the_milky_way; tests/test_spec.py]`.
The two new fields have no viewer preview; S19 owns that (§5d).

### D118. Cold timings at S15 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0006   0.0003   1.79        940  -
    viewer: a module         0.0006   0.0003   2.04     21,599  -
    index                    0.0000   0.0000   0.89      1,237  -
    version                  0.0042   0.0021   2.06      1,132  -
    stages                   0.0007   0.0003   2.10      8,898  -
    fields                   0.0013   0.0006   2.11     63,368  -
    inputs                   0.0001   0.0001   1.06     10,388  -
    arrays: one profile      0.1227   0.0004 305.45      4,976  halo,assembly,sfh
    arrays: history          0.1620   0.0028  57.69  6,401,768  halo,assembly,sfh,chemistry
    arrays: scalar           0.1036   0.0003 345.02      1,712  halo,assembly,sfh
    region: one sector*      0.2203   0.0044  49.62     19,024  halo,assembly,sfh,chemistry,vertical
    region: whole disc*      0.3682   0.1718   2.14  1,126,448  halo,assembly,sfh,chemistry,vertical
    system: one star*        0.1956   0.0024  81.59      3,112  halo,assembly,sfh,chemistry,vertical
    adv: history             0.5359   0.0026 206.43  6,401,776  halo,assembly,sfh,chemistry_dtd
    adv: alpha plane         0.5782   0.0034 168.91  6,401,832  halo,assembly,sfh,chemistry_dtd
    adv: one sector*         0.5692   0.0040 142.76     19,032  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.4994   0.0025 199.44      3,128  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, about 10 ms here (debt #37)
    import + registry: 0.104-0.135 s, paid once per process and excluded from the cold column

    model simple: 0.620 s cold, 0.630 s warm; halo 0.0043 s, sfh 17%, systems 27%, planets 24%
    model advanced: 0.988 s cold, 0.934 s warm; halo 0.0033 s, chemistry_dtd 43%
    catalogue against sample size: simple 0.35 us per star, 156.2 ms fixed (95%); advanced 0.92 us, 142.5 ms fixed (89%)
    one-off, first seeded draw: 9.92 ms then 0.026 ms (385x), billed to pattern; debt #37

**Read within the run.** Nothing changed shape. The halo stage's two new
scalars are one bisection and one gradient on a mesh it already builds, inside
the noise of its 3–4 ms; the `fields` route grew 2 kB for their declarations
and the `stages` route 50 bytes. The whole-model numbers, 0.62 / 0.99 s, sit
between D115's warm-process (0.58 / 0.91) and fresh-interpreter (0.83 / 1.22)
readings; the per-stage shares are S14's within a few percent everywhere, and
`tools/scaling.py` was not re-run because no stage's cost or complexity moved
`[verified: python -m galaxy.specs, tools/timings.py, 2026-09-09]`. The
catalogue's per-star slope read 0.35 and 0.92 µs against D115's 1.8 — the
flake D115 recorded, in its benign direction (the fixed cost dominates and the
slope is noise at this sample); not this session's, not touched.

**Close.** Board row 15 (desktop, Fable 5.1, `s15`, 2026-09-09); `session-15`
merged `--no-ff` into `main`; `s14`'s SHA filled in MANUAL_TODO.md as the
second merge's, `s15` queued; register 30 open / 16 discharged. Next: S16, the
extended component with its own timescale (§5d), judged against row 3 at 260.1.

### D119. The extended component is the high-j tail of the halo's angular momentum, its timescale was not the decision, and the threshold is the next one (debts #18, #43, #44, #45, #47, #11, #19)

**Decision.** The halo stage derives the extended accretion component from the
halo's specific-angular-momentum distribution and contracts around it; `sfh`
accretes it on the inside-out law it already has. The distribution is Bullock
et al. 2001's universal profile, ``M(< j) = M μ j/(j₀ + j)`` for ``j ≤
j₀/(μ − 1)``, with μ = 1.25 the median `[verified: Bullock et al. 2001, μ − 1
log-mean −0.6, scatter 0.4 dex, read at S16]` as a new Level 0 constant
`ANGULAR_MOMENTUM_MU`. Mapped onto the plane through ``j(R) = R v_c(R)`` on the
curve the halo's first contraction gives — the contracted halo plus the
razor-thin exponential — with ``j₀`` fixed so that its mean j is the
exponential disc's (λ_d already sets it), the profile lies below the
exponential inside 12.3 kpc and above it outside. The excess beyond that outer
crossing is gas the exponential never held: the tail, 7.6% of the retained
budget, 3.7 M☉/pc² at 15–20 kpc, ending where j_max lands at 25 kpc. Its share
comes out of the exponential's normalisation, the halo contracts a second time
around the total (two bounded passes, rule A1), and three fields are new:
`infall_tail_surface_density`, `infall_tail_share`, `infall_tail_inner_radius`.
The low-j excess inside the crossing is discarded, not modelled — it is what
feedback ejects and the bulge is drawn from (D110) — and the constant's about
line says so. Debt #18 is discharged; #47 opens on what the tail does not
explain; `NET_YIELD` 0.011 → 0.0117 and `WIND_SPEED` 999 → 993 are refitted
(debt #43, the day #18 closed, as it said); rows 2, 7 and 20 are recorded
misses under #44, #19 and #47. The §5d gate — rows 2 and 20 inside — is not
met, and the record says why rather than the constant that would meet it.

**Settled by.** Probe before build, three times. First, the forms, the repo
unchanged (D114's substitution plus the stage's compute set on the Stage
object), all with the halo contracting around the total, at z_f = 1.66:

    form                                  row 2   row 3   row 4   H (1e9)  adv row 22  M*(1e10)  gas at 8 / 15 / 20 kpc
    none (S15)                            1.891   260.1   2.49    4.17     -0.0578     5.29      7.1 / 3.9 / 0.6
    D114: s 0.2 at 3 R_d, tau(R)          2.129   248.4   2.65    6.65     -0.0515     4.95      7.1 / 4.6 / 3.1
    annular s 0.15 at 5 R_d, edge 4 R_d   2.110   245.5   2.52    7.75     -0.0535     4.80      6.7 / 4.6 / 3.7
    Bullock profile whole, mu 1.25        1.737   258.7   1.82    6.39     -0.0541     4.98      5.7 / 4.6 / 3.9
    Bullock tail, mu 1.15                 1.921   252.1   2.49    7.13     -0.0596     4.88      6.8 / 4.4 / 3.3
    Bullock tail, mu 1.25  (built)        2.088   251.7   2.49    6.66     -0.0595     4.95      6.7 / 4.5 / 3.9
    Bullock tail, mu 1.4                  2.235   251.2   2.49    5.41     -0.0568     5.12      6.8 / 4.7 / 4.3
    the tail on three arrival laws, mu 1.25: inside-out from t = 0  2.088 | the same from t_f = 3.84 Gyr  2.132 | the halo's growth after z_f  2.095
                                             every other column identical to the digit across the three

Three things the table says. **The timescale is not the decision.** The
register (debt #18, D114) asked for a component that arrives late enough to
stay under the threshold; the three arrival laws for the tail read the same on
every row and within 0.05 M☉/yr on row 2, because the inside-out law at 12–25
kpc already accretes over 10–20 Gyr, and "late" adds nothing to that. What
D114's form paid on row 2 was its inner part — an exponential at 3 R_d carries
a third of its mass inside 12 kpc, on top of gas the disc already holds near
the threshold — and the annular version shows it: no inner part, row 4
unmoved. **The distribution derives the share.** Across μ = 1.06–1.4 the tail's
share holds at 0.07–0.08; the shape moves its inner edge (14.9 → 11.0 kpc) and
with it row 20 (5.8 → 5.0 × 10⁹ through 6.9 at 1.15), not row 3 (252.5–252.9)
and not row 4. A component "sized to the observed HI disc", which the register
had asked for, would pass row 20 by construction (debt #47). **The whole
distribution fails row 4** at 1.82 kpc: the well-known low-j excess. Keeping
the exponential inside the crossing is MMW98's assumption kept where the stars
show it holds, and the tail is the part of the distribution the assumption
drops.

Second, the threshold. With the tail built, row 2 reads 2.08 and row 20 6.2 ×
10⁹, and the rows point at the one constant between them: the star formation
threshold, 5 M☉/pc², the bottom of its cited 5–10, at which the model's gas at
R₀ is 6.8 against the observed 10–13. Kennicutt's threshold is derivable —
``Σ_crit = α κ σ_g / 3.36 G`` from the rotation curve's epicyclic frequency
`[recall: Kennicutt 1989; Martin & Kennicutt 2001, α ≈ 0.69]` — and was probed
by substituting `sfh.star_formation_rate`:

    threshold                    Sigma_crit at 4 / 8.2 / 12 / 20 kpc   row 2   row 4   H (1e9)  row 9   row 5   adv row 22  gas at 8 kpc
    constant 5 (built)           5 everywhere                          2.083   2.49    6.24     0.147   1.27    -0.0592     6.8
    alpha 0.69, sigma_g 6 km/s   25.8 / 11.2 / 6.9 / 4.2               1.945   2.47    8.23     0.062   1.01    -0.0627     10.8
    alpha 0.69, sigma_g 8        34.5 / 15.0 / 9.3 / 5.6               1.842   2.43    10.0     0.025   0.90    -0.0768     13.6
    alpha 0.63, sigma_g 8        31.5 / 13.7 / 8.5 / 5.1               1.879   2.44    9.43     0.035   0.93    -0.0715     12.6

At Kennicutt's own numbers the derived threshold puts the gas at R₀ where it is
observed and row 20 at its target, and does not close row 2 (1.95) — star
formation is self-regulated by the infall rate, which is why `KS_NORM` at −1σ
reads *higher*, 2.25 — while row 9 falls from 0.147 to 0.062 and fails: the
thick disc forms from the reservoir the threshold holds. That is S18's
cancellation (debt #19), so the threshold is a decision for the session that
builds the thick disc's radial heating, judged on rows 2, 5, 7, 9, 11 and 20
together, and is recorded here (debt #47), not built.

Third, the instrument. The tail computed on the grid moved `halo_circular_velocity_sun`
with N_R and the grid-independence test caught it in the first full run; it is
computed on the halo's own mesh now and interpolated to the grid for
publication, and the scalars agree to 10⁻¹² across N_R = 40–800 `[verified:
tests/test_halo.py::test_grid_resolution_does_not_move_the_scalars]`. The
first probe's "own timescale" rows were the unsubstituted model — the Stage
holds its own `compute` — and only the mass budget (M* = 0.8 × budget with
nothing added) said so.

**What moved.** Row 3 260.1 → 252.9 in both models, high by 2: the baryons'
pull at R₀ −4.3 km/s and the halo's weaker response −2.5 (its share 165.8 →
163.3, r_i/r_f 1.503 → 1.474, the contracted fit 15.4 → 15.0). Row 20 4.17 →
6.24 × 10⁹ of hydrogen (48% → 22% short). Row 2 1.89 → 2.08. Row 4 2.49,
unmoved. Row 1 5.29 → 5.00 × 10¹⁰; row 10 3.87 → 3.71; row 11 1.42 → 1.30 ×
10¹⁰; row 5 1.32 → 1.27; row 9 0.152 → 0.147; row 6 254.6 → 275.4 (simple,
inside) and 358.5 → 384.2 (advanced, debt #42's miss, wider); row 7 1042 →
1126, over 1080, a new recorded miss under debt #19. The advanced gradient
−0.0578 → −0.0592, inside, away from −0.047: debt #45's prediction held, the
wind's tilt does the work. Rows 16/17 medians 43.2 → 42.0 km/s/kpc and 5.82
kpc. The gas at 20 kpc 0.6 → 3.8 M☉/pc². Every pinned measurement re-pinned
with the old number beside it; the spec test's debt map, counts and row 20
regex updated; the API's "no internals" test caught the constant's name in a
field's about line and it was rephrased (rule D5). Two new tests read the tail
and what it moved `[verified: tests/test_halo.py::test_the_high_j_tail_is_derived_and_where_it_lies,
::test_the_tail_moves_the_halos_response_and_not_the_scale_length;
tests/test_sfh.py::test_the_tail_is_accreted_and_what_it_moved]`. The three
new fields have no viewer preview; S19 owns that (§5d).

### D120. Cold timings at S16 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0003   1.06        940  -
    viewer: a module         0.0003   0.0003   0.95     21,599  -
    index                    0.0000   0.0001   0.55      1,237  -
    version                  0.0020   0.0019   1.07      1,132  -
    stages                   0.0002   0.0002   1.04      9,030  -
    fields                   0.0007   0.0006   1.09     66,268  -
    inputs                   0.0001   0.0001   0.95     10,388  -
    arrays: one profile      0.1275   0.0003 404.45      4,976  halo,assembly,sfh
    arrays: history          0.1887   0.0029  64.45  6,401,768  halo,assembly,sfh,chemistry
    arrays: scalar           0.1214   0.0004 280.04      1,712  halo,assembly,sfh
    region: one sector*      0.1953   0.0039  50.41     18,632  halo,assembly,sfh,chemistry,vertical
    region: whole disc*      0.4173   0.2141   1.95  1,128,456  halo,assembly,sfh,chemistry,vertical
    system: one star*        0.1956   0.0025  77.03      3,112  halo,assembly,sfh,chemistry,vertical
    adv: history             0.4885   0.0030 163.77  6,401,776  halo,assembly,sfh,chemistry_dtd
    adv: alpha plane         0.4913   0.0030 163.51  6,401,832  halo,assembly,sfh,chemistry_dtd
    adv: one sector*         0.5217   0.0044 119.88     18,640  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.5079   0.0025 202.23      3,128  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, about 11 ms here (debt #37)
    import + registry: 0.114-0.122 s, paid once per process and excluded from the cold column

    model simple: 0.638 s cold, 0.628 s warm; model advanced: 1.047 s cold, 0.990 s warm
    catalogue at 20,000 stars: layout 16-19 ms over all 1024 cells, 704 of them realise a star (516 until S16)
    catalogue against sample size: simple 1.60 us per star, 163.7 ms fixed (85%); advanced 2.06 us, 173.1 ms fixed (81%)
    one-off, first seeded draw: 11.47 ms then 0.029 ms (397x), billed to pattern; debt #37

**Read within the run.** The halo stage contracts twice now and computes the
tail on its mesh between the passes; it stays inside 3–5 ms, a fixed cost with
no dependence on N_R, N_t or N_z, so no scaling exponent moved and
`tools/scaling.py` was not re-run. The `fields` route grew 3 kB for three
declarations. One thing changed shape that is not a cost: the catalogue's
layout realises a star in 704 of its 1024 cells where it realised 516 — the
tail's gas forms stars out to 20 kpc (0.4 M☉/pc² of them there) and cells that
were empty are not. The whole-model numbers, 0.64 / 1.05 s, are within D118's
noise (0.62 / 0.99); the per-star slope read 1.6 and 2.1 µs against D118's 0.35
and 0.92, which is the flake D115 recorded, in its other direction.

**Close.** Board row 16 (desktop, Fable 5.1, `s16`, 2026-09-09); `session-16`
merged `--no-ff` into `main`; `s15`'s SHA filled in MANUAL_TODO.md, `s16`
queued; register 30 open / 17 discharged. §5d's gate for this session — rows 2
and 20 inside — is not met, and D119 says which constant would meet it and why
it is S18's to decide. Next: S17, the bulge stage and M_• (Opus, §5d), with row
3 at 252.9 and the bulge worth −5 to −8 on the S13 halo; BRIEF.md says re-probe
first.

## Session 17 — the spheroid and the hole

### D121. The bulge is the low-j end of the halo's angular momentum, it is worth 1.6 km/s and not five to eight, and rows 3 and 12 now have one cause (debts #11, #2, #17, #39, #42, #43, #44, #45, #47, #48)

**Decision.** The central spheroid is **derived, not sized**: it is the mirror of
S16's high-j tail. Bullock et al. 2001's `M(< j)` profile, mapped onto the plane
on the model's own rotation curve, lies above the exponential disc at *both* ends
and below it in between. S16 took the outer excess and called it the extended gas
disc (debt #18). S17 takes the inner one — mass with too little angular momentum
to be in any exponential disc of this scale length — and calls it the bulge.
`angular_momentum_excess` is the construction, `angular_momentum_tail` and
`angular_momentum_core` read it at each end, so the two components cannot drift
apart (rule A9). No new constant: μ = 1.25 is S16's.

**The numbers.** 7.71 × 10⁹ M☉, 13.2% of the retained budget, inside a crossing at
2.46 kpc with half of it inside 0.88 kpc; stable to ±1% across meshes of 300–2400
points and two inner cuts `[verified: tests/test_halo.py::test_the_spheroid_is_derived_and_does_not_move_with_the_mesh]`.
The spheroid is Hernquist and its scale radius is derived by equating its own
half-mass radius, a(1 + √2), to the radius inside which half the low-j excess
lies: **0.365 kpc**. That identity is algebra a test reproduces, and it was chosen
over matching the *projected* half-mass radius (a = r_half/1.8153 = 0.485, the
named alternative, rule B12) because both sides are then a mass inside a radius
with no projection assumed on either. Both were measured before the choice — the
alternative reads row 3 at 251.0 and row 14 at 110.9 — and the argument, not the
reading, is the reason.

**Where it lives, and why it is not a stage.** In the halo. Three constraints
close on one answer: row 3 is computed in `sfh`, so the spheroid must exist
upstream of it; the halo contracts around the *total* baryons, so it cannot
contract around a spheroid a later stage would derive; and the low-j excess needs
the potential on the halo's own 600-point mesh, which no stage can be handed. A
`bulge` stage that only republished four scalars would be the duplicate rule A9
forbids. `sfh` reads the mass and the scale, subtracts the share from the budget
it accretes, adds the sphere's own circular velocity to the quadrature, publishes
`stellar_mass_total` as the disc's stars *plus* the spheroid — which is what that
row's target (rows 10 + 11 + 12) always meant — and publishes row 13, the fraction,
because it is the stage that knows what the fraction is of.

**M_• is its own stage** (`nucleus`, checkpoint 1, the first seeded stage in the
run). Provenance is derived per stage (D55): folding the draw into the halo would
relabel the spheroid's mass, scale and dispersion as seeded, and rule A10 forbids
that — they are determined. `world_seed` sits at checkpoint 1 and nothing had read
it (debt #39); the M_• residual is the use its own declaration named.

**The finding, and it kills a prediction that has stood since S13.** The bulge is
worth **1.6 km/s** at R₀, not the 5–8 D110 measured. Row 3: 252.9 → **251.3**, a
quarter of a km/s outside 245–251. D110's probe drew a spheroid from the *stellar*
disc in proportion on the uncontracted S13 halo; the derived spheroid comes out of
the accreting budget, and that budget included the ~15% of the exponential lying
outside R₀ that pulled the Sun outward — so moving mass inward gives back in
quadrature nearly what the disc's flattening loses. Measured at S17, so the
replacement prediction can fail too: 1.4 × 10¹⁰ in the spheroid is worth 3.7 km/s
and reads row 3 at 249.4; 1.7 × 10¹⁰ is worth 4.2 and reads 248.7.

**Rows 12, 13, 14 and 18 are computable and all four miss.** Row 12 reads 7.71e9
against 1.4–1.7 × 10¹⁰, low by 45%; row 13 follows it at 0.153. That is not a
tuning gap: the low-j excess is one formation channel — material that could never
have been a disc — and BHG16 §4.2 says most of the Milky Way's bulge is the
box/peanut a bar makes of the *inner disc*, which this model has no dynamics for
(debt #21). **So rows 3 and 12 have one cause**, and closing row 12 with ~7 × 10⁹
of buckled disc closes row 3 as well. Row 14 reads 116.2 against a window S17
entered from the source (D122), high by 0.16 — and the surprise is that it is
nearly right while row 12 is 45% low, because σ inside the half-mass radius is set
by the whole enclosed mass and not by the spheroid alone (on self-gravity it would
read 71). **The two rows pull opposite ways**: adding the bar's missing mass takes
row 14 to 123, outside, unless a bar-built component is less concentrated than a
dissipational one — which is the tension the session that builds buckling reads
first. Row 18's median is 2.0 × 10⁷ against 4.2 ± 0.2 × 10⁶, 0.67 dex high (the
mean relation is 0.83 high), which is §3's expected ~0.75 and is the source's miss
rather than the model's: the M–σ relation is calibrated on classical bulges and
the model's own `bulge_classical_fraction` says this spheroid is 83% pseudo.

**The classical fraction is derived rather than assumed** — 1 − ⟨j⟩/(r_half
v_c(r_half)), the V/σ axis pseudobulges are classified on `[recall: Kormendy &
Kennedy 2004 via Kormendy & Ho 2013]`. It reads **0.171**, inside BHG16 §4.2.4's
0–25% classical share for the Milky Way. Reading a support ratio as a mass
fraction is the model's assumption and the linear map is the least it can make;
it is in the `about`.

**Two closures refused with the answer known** (rule B5). Ruling 10's residual
width should be interpolated by that fraction, but the pseudobulge endpoint has no
published number — Kormendy & Ho declined to fit pseudobulges and Ho & Kim 2014 say
only "much larger scatter" — so inventing one would be showing a missing number as
measured (rule B9): `BLACK_HOLE_SCATTER` stays the classical 0.28 dex, the model
understates the spread, and that is **debt #48**. And an M_•–M_bulge relation
applied to the classical share alone reads 5.2 × 10⁶ and would land row 18; it was
not adopted, precisely because that was visible before the choice.

**Row 2 landed and its miss was removed, without debt #47's mechanism.** The
spheroid takes 13% of the budget out of the disc and the rate fell 2.08 → **1.82**,
inside 1.65 ± 0.19 for the first time since S2. A registered miss that passes is an
error (debt #29), so the entry went — but the threshold is still the constant 5
M☉/pc² and nothing about #47 changed, so the debt is unaltered and **row 2 is no
longer available as evidence at S18**. It now sits in a window its own KS_NORM band
straddles (−1σ 1.97, out; +1σ 1.73, in), which is debt #44's original claim coming
true again. The advanced model's row 10 also started passing (5.00 → 4.26 × 10¹⁰)
and its miss went for the same reason; it is green on the same cancellation debt
#11 named — thin = every star — so it is not evidence for the chemical split.

**What else moved, measured not assumed.** Row 1 5.00 → 5.03 × 10¹⁰ (and now means
what its target means); row 4 2.491 → 2.484; row 6 simple 275 → 321 pc, from 24 pc
off its floor to 29 off its ceiling, advanced 384 → 439 (debt #42, and the point of
that debt made twice); row 9 0.147 → 0.135; row 10 3.70 → 3.17 × 10¹⁰, inside
whether or not row 11 is right; row 20's hydrogen 6.24 → 6.03 × 10⁹; rows 5, 7 and
11 further out under #19, which is S18's. `NET_YIELD` 0.0117 → **0.01184** and
`WIND_SPEED` 993 → **982.2**, refitted by bisection to solar at R₀ (debt #43) —
both moves are ~1%, a fifth of S16's, because a disc with less gas also makes fewer
stars and the effective yield is a ratio. **And the advanced model's α valley closed
at the one default-merger setting that had it**: n = 3, τ₀ = 1 read a dip of 0.6 at
S16 and reads nothing now, so S20 has one lever fewer than the record said; the
single-merger probe still opens it, shallower (0.55–0.62 against 0.55–0.66). Debt
#45's constant now carries the advanced row 22 over a quarter of its range rather
than a tenth: 1.25 came inside alongside 1.0.

### D122. Row 14's target came from the source, and the model's answer was already known

**Decision.** Acceptance row 14 leaves debt #17's zero-width list. BHG16 quotes
"the rms is σ_rms,b ≈ 113 km/s, to ≈3 km/s", mass-weighted within the bulge's
half-mass radius `[verified: BHG16 §4.3, read at S17]`, so the target is 110–116.

**Why this is recorded as its own decision rather than as a line in D121.** The
debt's remedy is "a citation with an uncertainty, entered before the row is next
judged", and the order here was the other way round: the spheroid was built, the
dispersion read 116.2, and *then* the source was consulted. Nothing was chosen —
the ±3 is the source's own and the model fails against it — but a reader is
entitled to know the sequence, because the alternative reading of the same event
is a session that went looking for a window its number would fit. What makes it
checkable: the same reading gave the *definition* too (mass-weighted inside the
half-mass radius), and the model's σ was recomputed to match it, which moved the
number **away** from the target — 112.8 over the whole spheroid, 116.2 inside the
half-mass radius, and the second is what row 14 reads.

**What did not change.** Rows 20 and 21 stay zero-width and the debt stays open for
them; the same reading of Nakanishi & Sofue still finds no uncertainty. The rule
that a new zero-width row must say so in its note is untouched.

### D123. Cold timings at S17 (rules B2, B6)

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0003   1.15        940  -
    viewer: a module         0.0003   0.0003   0.89     21,599  -
    index                    0.0000   0.0000   0.82      1,237  -
    version                  0.0017   0.0023   0.72      1,132  -
    stages                   0.0002   0.0002   0.96      9,874  -
    fields                   0.0007   0.0008   0.88     72,209  -
    inputs                   0.0001   0.0001   1.07     10,388  -
    arrays: one profile      0.1142   0.0003 372.48      4,976  halo,assembly,sfh
    arrays: history          0.1713   0.0028  60.23  6,401,768  halo,assembly,sfh,chemistry
    arrays: scalar           0.1156   0.0003 389.59      1,712  halo,assembly,sfh
    region: one sector*      0.1970   0.0037  53.83     18,576  halo,assembly,sfh,chemistry,vertical
    region: whole disc*      0.3775   0.1822   2.07  1,128,184  halo,assembly,sfh,chemistry,vertical
    system: one star*        0.1967   0.0026  75.73      3,112  halo,assembly,sfh,chemistry,vertical
    adv: history             0.4551   0.0026 175.72  6,401,776  halo,assembly,sfh,chemistry_dtd
    adv: alpha plane         0.4446   0.0025 175.93  6,401,832  halo,assembly,sfh,chemistry_dtd
    adv: one sector*         0.4684   0.0038 122.03     18,584  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    adv: one star*           0.4687   0.0024 197.30      3,128  halo,assembly,sfh,chemistry_dtd,vertical_alpha
    * cold includes the interpreter's first seeded draw, about 9-12 ms here (debt #37)
    import + registry: 0.094-0.103 s, paid once per process and excluded from the cold column

    model simple: 0.603 s cold, 0.569 s warm; model advanced: 0.867 s cold, 0.862 s warm
    halo 6.7-7.2 ms, nucleus 11.3 ms cold / 0.1 ms warm, sfh 105-107 ms
    catalogue at 20,000 stars: layout 16.2-16.4 ms over 1024 cells, 712 of them realise a star (704 at S16)
    catalogue against sample size: simple 1.21 us per star, 154.9 ms fixed (87%)
    one-off, first seeded draw: 11.97 ms then 0.025 ms (481x), billed to **nucleus**; debt #37

**Read within the run.** Nothing measurable was added. The halo now solves the
low-j excess and a Jeans integral between its two contraction passes and stays at
6.7–7.2 ms, inside S16's 7.1–7.3 — both are one-pass quadratures on the same
600-point mesh, so the cost was already paid. The `nucleus` stage is arithmetic on
two scalars and its 11.3 ms cold column is the process-wide one-off, not work: its
warm column is 0.1 ms. No stage's cost changed shape, so no scaling exponent moved
and `tools/scaling.py` was not re-run. The whole-model numbers, 0.60 / 0.87 s, are
below D120's 0.64 / 1.05 and within the same noise; the per-star slope read 1.21 µs
against D120's 1.60, which is the flake D115 recorded. The `fields` route grew 6 kB
for the five new declarations and `stages` 0.8 kB for the new stage.

**One instrument fix, and it is a rule B13 instance rather than a cost.** The
profile's one-off note named the stage that pays it in a literal — "billed to the
first stage that draws (`pattern`)" — and that was true in both models until this
session put a seeded stage at checkpoint 1. It derives the name from the widest
cold/warm ratio now, and prints `nucleus`. The note had been correct for six
sessions and was wrong within one commit of a stage moving.

**Close.** Board row 17 (desktop, Opus 5, `s17`, 2026-09-09); `session-17` merged
`--no-ff` into `main`; `s16`'s SHA filled in MANUAL_TODO.md, `s17` queued; register
31 open / 17 discharged (#48 opened; #17 discharged for row 14 only). §5d's gate for
this session — rows 10, 12, 13 inside, row 11 off its cancellation, 14 and 18
statistical, row 3 re-read — is **half met**: rows 10 and 11 came off the
cancellation and row 10 is inside on its own; rows 14 and 18 are computed and
judged statistically; row 3 was re-read and moved 252.9 → 251.3. Rows 12 and 13 are
outside, and D121 says why and what closes them. Next: S18, the thick disc (Fable,
§5d), with row 2 no longer available as evidence for debt #47 and rows 5, 7 and 11
further out than S16 left them.

## Session 18 — the thick disc: the radial kick, the derived threshold, and where the thick disc's shape is decided

Surface: desktop. Model: Fable 5.1. Branch `session-18`.

### D124. The merger's radial kick is derived and worth a third of a kiloparsec, the threshold is Kennicutt's and lands the gas rows at the cost of row 9, and the thick disc's shape is decided by the first infall's arrival law (debts #19, #47, #42, #43, #44, #26, #27, #45, #11, #17, #21; #49 opened)

**Decisions.** Three, each probed before it was built (rule B1), and one judgement.

1. **The radial kick is built, derived, and the prediction it carried is dead.**
   §5d's prediction for this session was that "a merger that thickens the disc also
   spreads it, so rows 5 and 11 can be right together". The kick is derived from what
   the model already has: the vertical impulse `MERGER_HEATING × mass_ratio` read as
   an isotropic one, turned into a displacement by the checkpoint-1 curve — a radial
   impulse δv starts an epicycle of amplitude δv/κ, an azimuthal one shifts the
   guiding centre by 2Ω δv/κ² and leaves an epicycle of that amplitude around it —
   so ⟨ΔR²⟩ = σ_k² (1/2κ² + 6Ω²/κ⁴): **1.47 kpc at R₀ and 0.30 at 2 kpc**, because
   the inner disc is stiff. The disc stage publishes `epicyclic_frequency` once,
   assembly publishes `disc_radial_spread` (R, t) beside `disc_heating`, `sfh` moves
   each step's stars through it after the loop (the stars never feed back on the gas,
   so the transport can wait for the whole history) and publishes
   `stars_formed_history`, which both vertical stages sort instead of rebuilding the
   birth history — one opinion about where the stars are, held where it is computed
   (rule A9). Mass is conserved ring by ring; with no major merger the field is the
   birth history exactly `[verified: tests/test_sfh.py::test_the_stars_formed_history_is_the_birth_history_moved_by_the_kick]`.
   Isotropy is the assumption; an anisotropic kick has no cited number and the probe
   read the answer's insensitivity to it (a kick 1.5× and 2× larger moves row 5 to
   1.45 and 1.52 against 1.35 on the epicyclic term alone).

   What it is worth, by the number (rule B4): row 5 **1.18 → 1.51** on the constant
   threshold and 0.93 → 1.17 on the derived one; row 9 −0.015; row 3 −0.4 alone and
   −0.2 with the threshold; rows 11 and 7 nothing. The sweep §5d's gate asks for,
   on the built model, merger share 0.3 → 0.8: row 9 reads 0.135, 0.088, 0.051, 0.024,
   0.007, 0.001 while row 11 reads 1.45e10, 1.21e10, 9.6e9, 7.2e9, 4.9e9, 2.8e9 and
   row 5 never passes 1.36 — **rows 9 and 11 are never inside together and the
   cancellation D51 recorded is still there** `[verified: tests/test_vertical.py::test_the_gate_is_still_a_cancellation_across_the_sweep]`.
   A kernel of ~2 kpc everywhere would be needed (constant 2.0 kpc reads row 5 at
   1.77), and that is migration's scale, not heating's — and a symmetric kernel of
   that size reflects mass at R = 0 into a cusp the old solver could not represent
   (its residual went 0.001 → 0.30), which is how the third decision was found.

2. **The star formation threshold is Kennicutt's, derived from the curve.**
   `SF_THRESHOLD` = 5 M☉/pc² — the bottom of its cited 5–10, "chosen, and it is the
   other end of its own range that the failing rows want" (AUDIT_RUN2.md D-3) — is
   replaced by Σ_crit = α κ σ_g / 3.36 G `[recall: Kennicutt 1989; Martin & Kennicutt
   2001]` with two Level 0 constants, `TOOMRE_ALPHA` = 0.69 and `GAS_DISPERSION` = 6
   km/s, whose about lines say they are one calibration (α was fitted with the
   dispersion assumed, rule B10). Published as `sf_threshold_surface_density`: 589 at
   the first cell, 47 at 2 kpc, 26 at 4, **11.5 at R₀**, 3.9 at 20. The gas at R₀ reads
   **10.8** against the observed 10–13 (6.3 until now), row 20's hydrogen **8.09e9**
   against 8.0 (6.03e9), row 2 1.755 (inside), the advanced row 6 439 → 373. Debt #47
   pre-committed the reading of what it costs: "if row 9 cannot be restored with the
   threshold derived, the thick disc is what is wrong, not the threshold" (D119). It
   costs **row 9 (0.135 → 0.051)** and row 8 with it, row 5 (1.51 → 1.17 with the kick),
   and, in the advanced model, **row 22 by 0.0008** (−0.064 → −0.0698). All recorded.

   Two things the threshold does that the record must carry. **The disc is now
   threshold-regulated**: the gas sits at 70–90% of Σ_crit everywhere inside 12 kpc,
   so the rate is whatever the infall supplies and `KS_NORM` no longer reaches row 2
   at all — 1.764 / 1.755 / 1.755 across its ±1σ band where S17 read 1.97 / 1.82 / 1.73
   (debt #44's claim is now false the other way; the gas mass still reads the
   normalisation, 1.17e10 → 1.07e10). And **the threshold diverges with κ at the
   centre**, where the Toomre argument does not hold and the bar the model lacks
   empties the disc: the model holds 1.5e9 of gas inside 4 kpc (S17: 0.4e9; the Galaxy
   a few 1e8), 44 M☉/pc² at 1 kpc and 276 at the first cell. That reservoir is 1.1e9 of
   row 20's hydrogen — outside 4 kpc the model reads 7.0e9 against ~7.7e9 — so the
   row is at its target partly for a wrong reason, and its entry says so. The same
   reservoir halves the centre's iron excess (debt #26: the advanced peak 1.39 → 0.70
   dex, out to 1.9 kpc rather than 2.66, the peak now at 0.5 kpc because the innermost
   rings never cross their threshold; the simple 0.46 → 0.25), steepens the advanced
   gradient past its edge, and doubles the unmigrated old gradient (debt #28: −0.102 →
   −0.228 simple, −0.127 → −0.254 advanced; the kernel takes a factor 33 and 11 out of
   it now, young/old 2.5 in both).

3. **The disc velocity solver is basis-free.** From S2 the razor-thin solver
   least-squared a profile onto eight exponentials and summed Freeman's solution.
   On the S17 profiles that read the stars at R₀ to 0.14 km/s and the gas to 1.4; on
   S18's — the kick steepens the centre, the threshold shapes the gas like κ — it
   missed the gas by 2.1 km/s and both curves by 7–12 at 12 kpc, and it cannot be
   densified (the exponentials are collinear; past twelve terms the fit returns
   nothing or thousands of km/s). Replaced by the homoeoid form `[recall: Binney &
   Tremaine 2008 §2.6.2]`, v_c²(R) = −4G ∫₀^R a g′(a)/√(R² − a²) da with g(a) =
   ∫₀^∞ Σ(√(a² + u²)) du, both integrals regular after substitution, validated on a
   Kuzmin disc (analytic; 0.03% at R₀ with the 30 kpc truncation accounted for) and
   Freeman's (0.005%), converged to 10⁻⁵ at R₀, 40 ms `[verified: tests/test_disc.py::test_the_general_solver_reproduces_freeman_on_an_exponential]`.
   It reads S17's profile 0.09 km/s below the basis fit (251.26 → 251.17), so every
   earlier pin stands inside its tolerance; on S18's it is worth −0.7.

4. **Judgement: the gate is not met, and the record says where the thick disc's
   shape is decided.** Rows 5, 7, 9 and 11 are all out (1.17, 1279, 0.051, 9.6e9). The
   probe that killed the kick's prediction found the lever: **the early episode's
   arrival law**. `sfh` accretes both infalls on the thin disc's inside-out law, τ(R) =
   7 Gyr × R/R₀, so by the merger at 3.8 Gyr only 42% of the early gas at R₀ and 31% at
   12 kpc has arrived — the pre-merger disc is compact because the model makes it
   arrive slowly. The two-infall framework the inside-out index cites gives the
   *first* infall a short, radius-independent timescale (~1 Gyr) and reserves τ_D(R)
   for the second `[recall: Chiappini et al. 1997, 2001]`. Probed with the early
   episode at 1 Gyr everywhere (0.55 — the halo's dynamical time at z_f, 0.1/H(z_f) —
   reads the same): row 5 **2.11**, inside, but the whole early share becomes thick
   disc — row 11 1.74e10, row 9 0.62, row 2 1.30 — and shrinking the share through
   the merger's gas fraction re-truncates the pre-merger disc through the threshold
   (share 0.8: rows 9 and 11 inside at 0.127 and 6.4e9, row 5 1.35). A thick disc
   both extended and light needs most of the early gas to still be gas at the merger,
   which a constant-efficiency Kennicutt law does not allow. That is **debt #49**, and
   the same lever is S20's: in the advanced model the fast first infall alone does not
   open the valley (dip 0.15 at most, row 6 to 720), while the derived threshold
   **reopens it on the default merger list** at τ₀ = 1 for n = 2 and n = 3 (dips 0.57
   and 0.64, the split at 0.39; S17 had closed the one setting that opened it), with
   row 6 at 700 there. Not built here: it moves every row of both models and its
   other consequence is judged at S20.

   Row 7 is re-attributed. It reads 1260–1370 across every thick-disc shape probed,
   because Σ(R₀) is 47.3 M☉/pc², what is observed, and does not move; the row is the
   dispersion, 40.4 km/s of which 30 is `MERGER_HEATING`'s kick on top of 27 of secular
   heating. At the observed 35 km/s the same Σ reads 958 pc; **`MERGER_HEATING` = 60
   reads row 7 at 751 and the advanced row 6 at 346, both inside, the first setting of
   either heating constant to land rows 6 and 7 together** — S20's first probe, under
   debt #42, and not this session's to set.

**Row 3 landed, by 0.04, on none of the mechanisms its prediction named.** 251.26
→ **250.96**: the solver −0.09, the kick −0.2 (a fifth of the disc's stars carried
outward across R₀), the threshold 0.00 (251.17 with and without it). The bar's
prediction (7e9 buckled into the spheroid reads 249.4) stands unread; its entry
went because a miss that passes is an error to leave (debt #29), and the reason is
written in its place. Rows 2 and 3 are green on the same footing now: inside their
windows on mechanisms worth less than the windows.

**What moved, both models.** Row 1 5.03 → 4.75e10 (the disc makes fewer stars from
the same budget; inside), row 4 2.48 → 2.44, row 6 simple 321 → 327, advanced 439 →
373; row 10 3.17 → 3.02e10; hydrogen 6.03 → 8.09e9, total gas 8.26e9 → 1.11e10; the
gas at 20 kpc 3.75 → 3.33 (the threshold there is 3.9); `NET_YIELD` 0.01184 →
**0.01376** (+16%) and `WIND_SPEED` 982.2 → **860.3** (−12%), the largest moves either
has made, because the gas at R₀ read −0.065 and −0.084 dex — D119 predicted −0.085 —
and both were re-set to solar by bisection (debt #43); the wind's escape fraction at
R₀ 0.750 → 0.699, the two effective yields 13% apart (17% at S17). Debt #45: no
setting of `GAS_DISC_SCALE_RATIO` reads the advanced row 22 now (1.0 is −0.0698,
1.25 is −0.0468; the window sits between). Migration narrows the local spread a
little instead of widening it (0.370 → 0.360). The execution order changed: the
disc runs before assembly, which reads its curve. Every pin re-pinned with the old
number beside; the spec's simple model reads 10 pass / 12 fail / 2 n-y-c and the
advanced 9 / 14 / 1.

**Not done, on purpose.** The fast first infall (#49, S20 with the valley); either
heating constant (#42, S20); the inner reservoir's cause, the bar (#21); a cap on the
threshold at the centre (an invention, rule A4). The viewer previews for
`epicyclic_frequency`, `disc_radial_spread`, `stars_formed_history` and
`sf_threshold_surface_density` are S19's.

### D125. Cold timings at S18 (rules B2, B6)

Desktop, Windows 11, uv-managed CPython 3.14, `tools/timings.py` and `python -m
galaxy.specs.performance`, one process each, the suite not running.

**Profile.** Simple **0.81 s cold** (0.60 at S17), advanced **1.08 s** (0.87): the whole
of the difference is `sfh`, 0.18 s (22.7% / 14.3%) from ~0.05 — the basis-free solver
(two calls, one per profile, grid and R₀ together, ~40 ms each on 1000-point
quadrature), the radial transport (a 400×400 kernel against 550 columns) and the
(R, t) `stars_formed_history` array. The catalogue (`systems`, 0.24 s), planets (0.18)
and the advanced chemistry (0.38) are unchanged. Import + registry 7–10 ms.

**Routes** (cold / warm): one profile 0.198 / 0.0004 s, history 0.227 / 0.003,
scalar 0.173 / 0.0004, one sector 0.250 / 0.004, whole disc 0.482 / 0.255, one star
0.245 / 0.002; advanced history 0.556, alpha plane 0.562, one sector 0.567, one star
0.595. Every physics route carries `sfh`'s new 0.15 s; metadata routes are unmoved
(stages 0.5 ms, fields 1 ms, inputs 0.1 ms). The one-off first seeded draw is 11 ms
(debt #37).

**Scaling** (`tools/scaling.py`): the simple chemistry is linear in N_t (exponent
1.00), the advanced 0.82, the naive DTD 2.06 — unchanged; the advanced chemistry is
7.1× the simple at N_t = 2000 and the whole model 1.48×. The solver's cost does not
scale with N_t; with N_R it is quadratic in the quadrature, fixed at 1000 points.

**Convergence**: 0 drifts on N_R, N_t and N_z in either model, every row; row 3 moves
0.04 km/s across N_R (250.99 / 250.96 / 250.95) against a 6 km/s window — and against
its 0.04 margin, which the sweep is not built to judge and the record says so (D124).

---

### D126. The catalogue migrates, and the rule is the chemistry's whole rule and not half of it (debts #31, #32, #26; #50 opened)

**The gate.** §5d gives S19 one number: the catalogue's [Fe/H] spread at R₀ equals the
chemistry's `feh_spread_sun`. It reads **0.361 against 0.360** `[verified:
tests/test_systems.py::test_the_catalogue_carries_the_chemistrys_own_spread_at_the_sun]`,
and it is an identity rather than a coincidence — the catalogue draws from the distribution
the field is a moment of. Getting there needed one decision the brief left open and one it
did not anticipate.

**Probed before built** (§5d), four rules, the advanced spread at R₀ in a ±0.25 kpc window:

| rule | spread | |
|---|---|---|
| abundance at the present radius (S18's catalogue) | 0.284 | |
| birth radius drawn backward, birth time from the local birth rate | 0.273 | *narrower* |
| the same with the birth time from `stars_formed_history` | 0.273 | S18's transport is worth 1.5% |
| **birth radius and birth time drawn together, backward** | **0.361** | against 0.360 |

The BRIEF's sentence — "a birth radius drawn around the present one with the migration
kernel's width" — read minimally is the second row, and it moves the number the wrong way.
Two things had to be seen to get the fourth.

1. **"Around the present one" is not a symmetric draw.** `transport` is normalised over the
   *destination*, so `K[:, j]` read as a distribution over birth rings is not one. The
   backward weight is `born[i] · K[i, j]` — Bayes — and both chemistries already compute
   exactly that: `chemistry_dtd` writes `w = m * K[:, at_sun][:, None]` inline, and
   `chemistry.migrate`'s mass-weighted smoothing is the same posterior in un-normalised
   form. A symmetric draw is not merely different; it puts stars where nothing was born and
   reads a metallicity off gas that made no stars (rule B9). Measured, it gives 0.84.

2. **The birth-*time* marginal is itself a migrated quantity, and it is most of the answer.**
   The catalogue drew a star's birth time from `sfr_surface_density_history` at its present
   ring — "born here", the answer for a disc whose stars never moved. Of the stars now at
   R₀, when they were born is `Σ_i born[i,k] K[i,R₀]`, which is 1.4 Gyr older in the mean:
   **R₀ mean age 5.7 → 7.3 Gyr** in the advanced model, 6.0 → 7.3 in the simple. Drawing the
   radius and leaving the time is half the rule and less than half the effect.

So a star's birth radius and birth time are drawn together from the backward weights, and
its abundance is read there. **The kick does not enter the draw** — the brief's open
question. Two reasons, and the second is the finding: the kick is already spent in the
present radius (`stellar_surface_density` is `stars_formed_history` summed, i.e. birth
positions already moved by it), and the chemistry moves abundances with the churn alone, so
entering the kick as well would make the catalogue disagree with `feh_stars_old`,
`alpha_fe_stars` and `feh_spread_sun` — every published statement about where the stars now
at R came from. Trading one inconsistency for another is not progress; naming it is, and
that is **debt #50**: the model transports stars twice, with two kernels, and nothing
reconciles them.

**What #50 costs, stated because it is the price of the decision.** The catalogue's thick
fraction at R₀ is now 0.221 where `thick_thin_surface_density_ratio` says 0.051 — row 9, a
recorded miss whose target is 0.08–0.16. The two transports bracket the observed number:
the kick alone puts too little thick disc at R₀, the churn alone too much. The thick disc's
*total* is unmoved (0.2516 → 0.2535 of the catalogue), so this is about where the population
sits and not how much of it there is, and the prediction is in the register.

**Two duplicates removed, both rule A9, and the second was hiding a bug.**

- The migration kernel and its age bins move to `chemistry.py` — `transport`,
  `transport_columns`, `migration_width`, `age_bin_edges` — read by `chemistry_dtd` and by
  `systems`. The catalogue cannot now churn by a different rule or a different binning than
  the chemistry it is checked against.
- **The thin/thick criterion is published**, as `birth_population` (R, t), by the vertical
  stage that owns it. `systems` rebuilt it from `last_major_merger_time`, `alpha_fe_history`
  and `alpha_split`. In the advanced model that reconstruction and `vertical_alpha`'s mask
  *disagreed*: with no valley (debt #27) the stage's mask selects nothing, while the
  catalogue's fallback was the merger time. It never showed, because the thick surface
  density was zero and the population was drawn against it — the wrong criterion was
  masked by a zero. Draw the population from the birth place, as the model's own definition
  says, and the disagreement would have surfaced as a 21% thick disc in a model that says
  it has none. Published, the advanced catalogue's empty thick disc follows from #27
  instead of from an accident.

`star_birth_radius` is published: the difference from `star_radius` is the churning, which
is what debt #31 said never reached the viewer. **84% of the stars at R₀ were born inside
it, mean birth radius 5.4 kpc** — which is debt #28's "migration is too strong" in its most
direct form, and is pinned so that lowering `migration_efficiency` moves it first.

**Debt #32 re-ruled: the spread was the wrong observable to have argued over.** §8's claim
was that without migration the local distribution is far too narrow; the model refuted it
(0.370 without, 0.360 with — migration *narrows* it). With the catalogue drawing birth
places from the same kernel, migration turns out to dominate the solar neighbourhood on
every statistic except the one §8 named: the mean age, the mean [Fe/H] (−0.33 → −0.25), and
where the stars came from. A spread is a second moment of a mixture, and two shifted narrow
components make a wide one look unchanged. The mean and the birth-radius distribution
separate the hypotheses; the dispersion does not.

**Debt #26's sample instrument is weaker, and that is re-pinned rather than left to drift.**
The catalogue's metal-rich share went 0.005 → 0.0031 and the two models' giant-fraction
contrast 1.58× → 1.25×, because a metal-rich star born at 1 kpc is now spread over the disc
instead of counted where it formed. The centre's iron still reaches the planets — the
occurrence assertion inside 1 kpc is unmoved — but the sample says less about it than it did.

**The acceptance table did not move.** 10 pass / 12 fail / 2 not-yet-computable in the
simple model and 9 / 14 / 1 in the advanced, unchanged from S18, and rows 16, 17 and 18 read
42.8193, 5.70059 and 1.97 × 10⁷ as before: no acceptance row reads the catalogue.

**Two things the build got wrong first, both caught by the suite.**

- The empty-bin fallback returned `R[ring]` where `ring` numbers the *cell* rings, not the
  grid — out of bounds on a small grid and silently a different radius on the default one.
- The first draw took each star's birth radius from its own birth *step*, which put a
  400-cell cumulative sum on every star: per-star cost 3.9 → 11.2 µs, and the star-dependent
  part became the larger half of the catalogue, which `test_performance` asserts against
  (D24). The kernel is a bin-level object — one width per 0.5 Gyr age bin — so the
  birth-radius CDF is built at that resolution, once per (ring, bin), and drawing is a
  vectorised binary search. It costs nothing in accuracy: 0.3655 binned against 0.3562 per
  step, either side of the chemistry's 0.3602.

**And one measurement that reversed a change.** Restricting the churn to the rings a region
query actually touches made a region's star differ from the sweep's in the last bit: the
arrival law is a matrix product over the rings, and BLAS sums a one-column product in a
different order than a thirty-two-column one. Per-region determinism is this stage's whole
contract (D60), so the churn is built for every ring whatever was asked for, and
`transport_columns` — the kernel read by column, nine times cheaper over the catalogue's
twenty-eight widths — is what makes that affordable. A one-cell query went 2.9 → 58 → 32 ms.

---

### D127. Cold timings and the profile at S19 (rules B2, B6)

One fresh process per endpoint, `uv run python tools/timings.py`; the profile is
`python -m galaxy.specs`'s performance section. Everything S19 moved is in the catalogue.

```
arrays: one profile      0.529 cold / 0.001 warm      region: one sector*   0.467 / 0.034
arrays: history          0.577 / 0.007  6.4 MB        region: whole disc*   1.091 / 0.649
arrays: scalar           0.280 / 0.001                system: one star*     0.626 / 0.029
adv: history             0.984 / 0.004                adv: one sector*      0.822 / 0.035
adv: alpha plane         0.951 / 0.004                adv: one star*        0.785 / 0.029
metadata (index, version, stages, fields, inputs): 0.0001–0.0015, no stage run (rule D4)
* includes the interpreter's first seeded draw, ~10 ms (debt #37). import + registry 0.085–0.099 s.
```

**The profile.** Whole model 1.393 s cold simple, 1.880 s advanced. `systems` is the
costliest stage in both — 0.684 s (49.1%) and 0.662 s (35.2%) — ahead of `sfh` 0.233 and
`chemistry_dtd` 0.747. It was 0.554 / 0.592 at S18, so the migration draw costs about 0.1 s.

**Where the 0.1 s went, and why it matters that it went there.** The catalogue's cost is
supposed to be per *cell*, not per *star* (D24), and `test_performance` asserts it. The
first build broke that — a 400-cell cumulative sum per star took the per-star cost from
3.88 to 11.2 µs and made the star-dependent part the larger half. Drawing at the kernel's
own age-bin resolution and searching with a vectorised binary search puts it back: **4.19 /
3.13 µs per star and 523 / 552 ms fixed**, against 3.88 / 2.76 µs and 397 / 432 ms at S18.
87–90% of the catalogue at 20,000 stars still does not depend on how many stars were asked
for, which is the property the LOD ladder rests on.

**And the number that had to be watched separately.** A one-cell query — what `/api/system`
costs, and the interactive path — went 2.9 → 58 → **28 ms**. The 58 was the whole churn built
for a single cell; reading the kernel by column rather than building it square (`transport_
columns`, nine times cheaper over the twenty-eight widths) is what brought it back. It cannot
be brought back further by asking for fewer rings: that changes the arithmetic with the query
and breaks per-region determinism (D126). Against the 0.63 s the same request spends running
the six stages above the catalogue, 28 ms is not where that request's time is.

**Unchanged.** `scaling.py` is not re-run: no stage changed complexity class — the churn is
linear in the grid per ring and the kernels are counted by age bin, not by star.


### D128. The valley does not open on any mechanism the model can derive, and the record says why; the merger's kick is re-derived from the thick disc's dispersion net of the secular heating (debts #27, #42, #49, #26, #47, #11, #19)

**The decision the brief asked for.** §5d gave S20 one question — which mechanism the model
*derives* to make the inner disc fast without steepening the infall law everywhere — with two
candidates: the bulge's inflow (the plan's) and the first infall on its own short timescale
(debt #49's, which S18 probed). The answer is **neither, and the question was the wrong shape**.
Both were probed, with three more the probes led to, the repo unchanged (D114: `sfh.first_infall`
is now one substitutable function, and the tests substitute it), every verdict at the default
grid with the dip read across N_t = 1000–4000 (the N_t = 8 trap, debt #27). None opens the valley
row 24 asks for. What they read, and the instrument that showed why:

| first infall | advanced: dip, verdict | simple: rows 5 / 9 / 11 | other rows |
|---|---|---|---|
| the thin disc's law, as built | 0.00 single | 1.17 / 0.051 / 9.6e9 | — |
| 0.1/H(z_f) = 0.55 Gyr everywhere (the halo's dynamical time; 1 Gyr reads the same) | **0.15** single, at N_t 1000/2000/4000 | **1.95** / 0.56 / 1.67e10 | row 2 1.27, adv row 6 594 |
| the same at merger share 0.3 / 0.65 / 0.8 | — | 2.15 / 1.44 / 2.5e10; 1.70 / 0.23 / 1.06e10; 1.26 / 0.04 / **4.8e9** | rows 5 and 11 never inside together |
| a compact early disc, R_d E(z_f)^(−2/3) = 1.4 kpc, on τ(R) | 0.00 | 0.62 / 0.002 / 1.5e10 | row 4 1.74, **row 22 −0.147** |
| fast *and* compact (the disc the halo made at z_f) | 0.00 | 0.82 / 0.04 / 1.9e10 | row 22 −0.146 |
| Wechsler et al. 2002's M(a) at a_c = 1/(1+z_f), as the rate | 0.00 | 0.98 / 0.002 / **1.5e9** | row 2 3.03 |
| threshold switch width 0.25 → 0.1 → 0.05, on the fast law | 0.19 / 0.19 | — | not the lever |
| a bar-driven drain of the inner disc after ELN's criterion fires (0.5 Gyr on the fast law) | 0.63 **bimodal_wide** at split 0.37 | 3.3 / 0.10 / 7.2e9 | **row 10 1.4e10, row 22 +0.15, row 4 −12** |
| a mass-loaded wind, η = f_esc/(1 − f_esc), on the fast law | 0.59–0.72 **bimodal_wide** at split 0.23 | 2.1 / 0.4 / 4.5–6.8e9 | **row 2 0.4–0.7, row 3 214–224, row 10 0.9–1.4e10** |

The first two rows are measured on the derived kick (88.8); the rest were probed on the 120 km/s kick the session opened with, which moves the thick-disc rows by a few percent and no verdict.

**The instrument, and what it showed.** The [α/Fe] mass at R₀ was decomposed the way
`chemistry_dtd` builds it (the backward weights, D126) by birth epoch, birth radius and birth
time. At every law the early population at R₀ is 75–100% migrants born inside 6 kpc, and it is
spread *evenly* from +0.2 to +0.45: on the fast law the stars born at t = 0–1 Gyr sit at +0.39,
1–2 at +0.27, 2–3 at +0.18, each a sixth of the early mass, with no bin holding more than 3% of
the total, against 18% in the thin mode's bin at +0.11. The histogram is dN/d[α/Fe] =
Ψ / |d[α/Fe]/dt|, and in a threshold-regulated Kennicutt disc fed from t = 0 the star formation
rate is *already falling* while the α-fall runs — the infall peaks at t = 0, the gas at R₀ never
exceeds 15 M☉/pc² because it is consumed as it arrives, and the depletion time at that density
(1.4 Gyr) is longer than the infall's, so half the early stars form after the infall has ended,
on gas whose [α/Fe] falls 0.44 → 0.24 → 0.14 over 0.5–3.8 Gyr. Nothing piles up. A thick *mode*
near +0.3 needs Ψ high where d[α/Fe]/dt is small, which is a rising burst on gas-rich material
cut within a gigayear — exactly the reading debts #47 and #49 reached for rows 5, 9 and 11 from
the other side ("most of the early gas still gas at the merger"). A constant-efficiency Kennicutt
law with a threshold cannot do it: the threshold parks the gas and the switch keeps a third of
the Kennicutt rate going through the whole fall (the switch's width is not the lever: 0.25 → 0.05
moves the dip 0.15 → 0.19).

**Every valley the detector has ever reported is the plateau spike.** S13's, S18's (τ₀ = 1 at
n = 2–3, dips 0.57–0.64, split 0.39), the drain's (0.37) and the wind's (0.23): in each the α-rich
"mode" is the stars formed before any type Ia iron arrived, at +0.45 exactly, 5–7% of the mass in
the top two bins, with the split *above* the α-rich sequence itself and the rest of the early
population a plain between +0.2 and +0.40 `[verified: tests/test_audit.py::test_debt_27_every_valley_the_detector_has_found_is_the_plateau_spike]`.
DIP_DEPTH = 0.5 is met whenever the thin mode is tall and the plain thin enough, which is what
the fast inner disc and the wind both do by shrinking the early tail — not by making a thick
disc. Debt #27's S9 prediction is therefore dead in a way its earlier runs did not show: the
inner disc fast does open *a* valley, and it is the wrong one. The register's prediction is
replaced by the one above, stated so it can fail: if a mechanism ends the first phase sharply
and the histogram still shows no mode short of the plateau, the DTD's minimum delay (0.15 Gyr —
a δ-spike at +0.45 by construction) is what the detector is reading.

**Why nothing was built for the valley.** The two mechanisms that do open a spike valley
each cost the disc: the drain empties the inner disc (the bar's inflow, as the plan named it,
takes 2e10 out of the disc's accretion), and the mass-loaded wind at the metal escape fraction's
own odds — the one form with no new constant, η(R₀) = 2.3 — ejects 60% of the budget the halo
says the disc retained, which cannot be re-normalised without the disc's retained mass becoming a
fixed point across checkpoints 1 and 3 (the halo contracts around it; rule A1). Both are the bar's
and the wind's *mass*, debts #21 and #26, which §5d gives S22 to rule on rather than S20 to close;
the numbers are in the register. The derivable candidate the brief favoured, #49's first infall
on the halo's dynamical time, is real physics with no constant and is not built either: in the
simple model it lands row 5 (1.95) only where rows 9 and 11 read 0.56 and 1.67e10, and where row
11 lands (share 0.8) rows 5 and 9 read 1.26 and 0.04 — the trade #49 said would kill it, and its
pre-committed reading applies: **the star formation law at high redshift is what is wrong**, not
the arrival law. Built, it would move rows 2, 6, 9, 10 and 11 out and row 5 in; recorded instead
`[verified: tests/test_audit.py::test_debt_49s_prediction_ran_the_first_infall_on_the_halos_dynamical_time_and_failed]`.

**Debt #42, judged: `MERGER_HEATING` 120 → 88.8, derived; `SECULAR_HEATING` stays.** The
constant's own about line said it was "scaled so the Milky Way's 1:4 merger leaves the pre-existing
disc at about 30 km/s" — as if the kick were the thick disc's whole dispersion. The assembly stage
composes it in quadrature with the secular heating and the birth dispersion, which read 27.06 km/s
over the thick population at R₀, so the thick disc read 40.4 against the observed σ_W = 35
`[recall: Bensby, Feltzing & Lundström 2003]` and row 7 1279 pc. Net of what the model already
gives those stars the kick is √(35² − 27.06²) = 22.2 km/s and the constant 88.8; a test
reproduces the arithmetic `[verified: tests/test_audit.py::test_debt_42_the_merger_kick_is_the_observed_dispersion_net_of_the_secular_heating]`.
It is not a sweep: S18's 60 lands rows 7 and the advanced 6 together (751 / 346) and was not
taken; 88.8 is what the cited dispersion gives, and it lands **row 7 at 962** (inside; its miss
entry went, the reason written in `spec.py`) with the advanced row 6 at 356 — 6 pc over, the
merger-heated old population counted as thin, which is #27's. `SECULAR_HEATING` = 25 is bracketed
by its own row: 20 reads the simple row 6 at 228 and 30 at 451, both out, so it stays. Rows 6 and
7 are inside together in the simple model on a constant set by a citation; in the advanced model
row 7 is zero and row 6 is 6 pc out, for the one reason (#27).

**What the re-derivation costs, and where it is written.** The radial kick shrinks with it:
1.47 → **1.09 kpc at R₀**, 0.30 → 0.22 at 2 kpc; row 5 1.17 → 1.09, row 9 0.051 → 0.0455 (the kick
now returns 0.010 of it, not 0.015), row 8 0.013 → 0.016; the sweep of the merger share reads row
9 0.131 / 0.083 / 0.0455 / 0.019 / 0.005 / 0.001 against row 11 unmoved, still never inside
together. And **row 3 leaves its window by 0.03**: 250.96 → 251.03, because fewer of the disc's
stars are carried across R₀. S18 landed it on the kick by 0.04 and said so; the constant's
re-derivation is worth +0.07, and the row is back on the miss list under #11 with its cause
unchanged — the bar (D121: 7e9 buckled into the spheroid reads 249.4). Rows 2, 4, 20, 22 do not
move (the kick is downstream of the gas). The advanced model reads 8 pass / 15 fail / 1; the
simple 10 / 12 / 2 with row 7 in and row 3 out.

**Not done, on purpose.** The first infall on the halo's dynamical time (dead by the number,
above); a cap or a bar-shaped region on the threshold (an invention, rule A4); the wind's mass
(#26, S22's ruling — the number it needs is a retained budget that is an output, not an input);
the detector (its false positive is real and is now named, and changing DIP_DEPTH or
MODE_MIN_SHARE with the answer known is rule B5's exact prohibition); #50, which is S21's to read.
The register carries the probes; `tests/test_audit.py` carries the three that S21 should re-run.

### D129. Cold timings and the profile at S20 (rules B2, B6)

One fresh process per endpoint, `uv run python tools/timings.py`; the profile is
`python -m galaxy.specs.performance`. **This session ran on the desktop** where S19 ran on
the web, and the machine is about three times faster on every route, so the S19 → S20
comparison is a machine comparison, not a code one: nothing S20 changed touches a stage's
cost (one constant and a function boundary in `sfh`).

```
arrays: one profile      0.170 cold / 0.0003 warm    region: one sector*   0.258 / 0.021
arrays: history          0.219 / 0.003  6.4 MB       region: whole disc*   0.497 / 0.270
arrays: scalar           0.158 / 0.0004               system: one star*     0.268 / 0.017
adv: history             0.524 / 0.004                adv: one sector*      0.564 / 0.021
adv: alpha plane         0.525 / 0.003                adv: one star*        0.560 / 0.018
metadata (index, version, stages, fields, inputs): 0.0000–0.0007, no stage run (rule D4)
* includes the interpreter's first seeded draw, 11.7 ms (debt #37). import + registry 0.102–0.116 s.
```

**The profile.** Whole model 0.755 s cold simple, 1.104 s advanced. `systems` is still the
costliest stage in the simple model (0.261 s, 34.8%) and `chemistry_dtd` in the advanced
(0.387 s, 35.1%) ahead of `systems` (0.276, 25.0%); `sfh` 0.152 / 0.147. The catalogue's cost
is still per cell: 1.42 / 1.75 µs per star against 220 / 209 ms fixed, 89% / 87% of the
catalogue at 20,000 stars independent of how many were asked for (D24, D127). A one-cell
query 18–19 ms. `scaling.py` is not re-run: no stage changed complexity class.

## Session 21 (a) — Audit II, aim (a): every prediction since S13, killed or held with a number

Surface: desktop. Model: Fable 5.1. Branch `session-21-a` — sealed, never merged, never merged
into `session-21-b`; S22 ports (D99). Reserved numbers #51–#64 / D130–D143; this run uses #51,
#52, D130, D131.

### D130. Twenty-two predictions run with the repo unchanged; fourteen findings; two debts opened, ten amended, eleven miss predictions replaced (debts #11, #19, #27, #28, #42, #46, #47, #48, #49, #50; #51, #52 opened)

**Decision.** The list is `AUDIT_II_A.md`; the measurements are `tests/test_audit_ii_a.py`, one
test per finding, each pinning the number at a stated precision. Nothing was fixed: every probe
substitutes one function (`sfh.radial_transport`, `halo.angular_momentum_core`,
`sfh.first_infall`, `sfh.star_formation_rate`, `sfh.toomre_threshold`) or one constant, and the
verdict is read off the row's own window. Where a prediction carried a pre-committed reading,
that reading is applied and not re-argued (LESSONS, S20). What S22 ports is §5 of the list.

**Verdicts, in one paragraph each** `[verified: AUDIT_II_A.md §1; tests/test_audit_ii_a.py]`.

- **Debt #50 is dead** (A-1, A-2). Its bracket compared the catalogue's thick *fraction* (0.221)
  with a thick/thin *ratio*; as a ratio the bracket was 0.0455–0.284. Moved through both kernels
  — the built kick, then the chemistry's own `transport(R, migration_width(age))` per age bin —
  row 9 reads 0.266, and rows 4 and 3 read 3.49 and 244.9: the width `chemistry_dtd` and the
  catalogue use is ruled out by the disc's structure the moment the mass follows it. The kick is
  nothing beside the churn (0.002 on row 9). Rows 9 and 11 are inside together for the first time
  in the project at a merger share of 0.7, with row 5 at 2.56 — the cancellation debt #19
  recorded, run the other way. The reconciliation S22 rules on is not a composition: one of the two
  widths is wrong and rows 3 and 4 say which.
- **D121's bar prediction held on row 3 and died on row 14** (A-3, A-12). 7e9 at the derived scale
  radius, the halo contracted around it: row 3 249.64 (D121 said 249.4), rows 12 and 13 inside,
  row 14 144.4 (D121 said 123). At four times the half-mass radius row 14 is still 121.5, so no
  concentration lands rows 12 and 14 together; subtracting the rotation the model computes
  (160 km/s at r_half) leaves 70. Row 14's 116.2 is −46 and +28 cancelling — **debt #52**. The
  advanced model's rows 6 and 22 pay for the bar (400, −0.081), which D121 did not list.
- **D128's claims held with the clock corrected** (A-4). Every valley is the spike, on the
  single-merger cases and on the strongest accretion law (the early gas in 0.1 Gyr: dip 0.78,
  split 0.21, the spike 0.114 of the mass). A ×5 burst of star formation in the first 0.8 Gyr
  forms its stars at the plateau and makes nothing; the same burst inside the α-fall — 1–2 Gyr on
  the fast first infall, cut 2–3 Gyr — makes an α-rich mode at +0.35 holding a tenth of the mass
  in one 0.02 dex bin, twice the spike, the first mode short of the plateau the model has ever
  produced, with the advanced row 6 at 353. "A rising first phase cut within a gigayear" is right
  about the shape and wrong about when: after the first Ia iron and while the gas is still rich.
  Nothing in the repo makes one.
- **Rows 5, 9 and 11's reading fired** (A-5). Star formation off 1.0–3.8 Gyr on the fast first
  infall — the early gas left as gas at the merger — puts rows 8, 9, 10 and 11 inside together
  (0.040, 0.115, 3.36e10, 6.72e9) with row 5 at 1.61. Debt #19's own sentence, "the split
  criterion is what is wrong", is the reading by 0.2 kpc; S22 rules.
- **Debt #48's verdict held and its claim died** (A-6). The spec's ensemble is one fixed diagonal
  (seeds 0–40) whose standardised M_• residual has median −0.577σ, 2.9 standard errors from
  zero; row 18's median moves with the width (1.97e7 → 9.9e6) while its verdict does not. Seeds
  41–81 read −0.10σ and hold rows 16 and 17 (41.1 / 5.94). **Debt #51**: `ENSEMBLE_MIN` was
  derived for the interval, not the median.
- **The advanced row 22's mechanism is dead** (A-7). The row is fitted over 4–12 kpc; the
  reservoir inside 4 kpc emptied to 4e8 leaves it at −0.0699, the threshold capped at the R₀
  value inside R₀ takes it to −0.0794, the constant 5 everywhere reads −0.0633. It is the gas the
  threshold holds *in the window*, with the wind refitted to R₀; by the entry's own reading the
  wind's tilt (#26) is what is wrong and the bar is not this row's lever.
- **Debt #46's pre-committed sweep cannot judge** (A-8): row 19 is the input, v_esc(R₀) is inside
  530–580 at every w (544–577), and row 3 alone crosses between w = 0.8 (237.8) and 1.0 (249.3).
- **The smaller ones.** μ = 1.06 lands rows 3, 12, 13 and loses 2 (1.14), 14 (146), 20 (7.53e9),
  reproducing D121's 1.46e10–5.6e9 (A-9). The 2.5 kpc kernel lands the advanced row 23 (−0.048)
  with the young/old ratio at 1.22, the wrong side of 1.75; 2.0 kpc inverts it (A-10) — debt #28's
  second explanation is the one convicted. The advanced row 6 lands at `MERGER_HEATING` ≈ 74, not
  78 (A-11). Row 20's hydrogen outside 4 kpc never reaches 7.7e9 at any μ (A-13). Debt #44 held
  (1.764 / 1.755 / 1.755). Row 15 is 2.0 × 2.441, 0.08 above its floor.
- **`MERGER_HEATING`'s citation is a selection-function constant** (A-14). Bensby, Feltzing &
  Lundström 2003's σ_W = 35 is their Table 1's adopted characteristic value, no uncertainty; the
  measurement their Sect. 1 quotes is Soubiran, Bienaymé & Siebert 2003's 39 ± 4 `[verified: both
  papers read in full at S21 (a) by a read-only agent from the publisher-identical PDFs (Lund
  University's repository copy of Bensby et al.; arXiv:astro-ph/0210628 for Soubiran et al.)]`.
  At 39 the constant is 112.3, row 7 reads 1193 (out) and row 3 250.97 (in); the window's top is
  σ_W = 37.1. Row 7 is green on the round number at the −1σ edge of the measurement, and rows 3
  and 7 trade across the source's error bar. Not re-set here: the derivation's shape is S20's and
  the value is S22's ruling under #42, with this number beside it.

**The green rows** (`AUDIT_II_A.md` §3): no green row is an unconditioned prediction. Row 2 is the
nearest and it is a prediction of two constants' defaults (μ moves it 1.14–1.82 across its 90%
range). Row 4 is green because the mass does not follow the chemistry's churn (A-2).

**Not run, and why** (§4): row 18's M_•–M_bulge on the classical share (no relation in the repo;
entering one to read it is the tuning the entry exists to catch); #26's wind and #21's drain (S20
ran them for S22); the catalogue under the double transport (no row reads it, and the grid's ratio
agrees with the catalogue's to 7%).

**What this branch changes and what it does not.** No physics, no constant, no default: the
acceptance table reads 10 / 12 / 2 and 8 / 15 / 1 as S20 left it, and every pin in the suite
stands. Changed: `spec._MISSES` / `_MISSES_ADVANCED` predictions for rows 3, 5, 9, 11, 12, 14, 20,
the advanced 6, 22, 23 and `_NO_VALLEY_PREDICTION` (each appended with what S21 (a) read, the old
prediction kept); the register (#51, #52; ten amendments); `tests/test_audit_ii_a.py` (twelve
tests); `tests/test_docs.py` lists the audit file; `tests/test_audit.py` counts 34 / 18;
`MANUAL_TODO.md` carries S20's SHA. The board row is ◐ with the model used.

**Settled by.** Rule B4 — a prediction is a sentence that can fail, and twenty-two of them since
S13 had never been run as written; rule B5 — nothing was moved to land a row (μ, w, the kernel
width and the heating constant were read and left); D114 — a probe is a substituted function, and
S20's factoring of `first_infall` made four of these probes a monkeypatch each; rule B10 —
`MERGER_HEATING` was re-derived at S20 from a number the record called a citation, and the
citation was read before the row was trusted `[inferred]`.

### D131. Cold timings and the profile at S21 (a) (rules B2, B6)

One fresh process per endpoint, `uv run python tools/timings.py`; the profile is
`python -m galaxy.specs.performance`. Desktop, the same machine as S20 (D129). Nothing on this
branch touches a stage, so this is a repeat measurement and the comparison with D129 is the
machine's own scatter: every route within 10% of S20's number.

```
arrays: one profile      0.150 cold / 0.0003 warm    region: one sector*   0.241 / 0.019
arrays: history          0.201 / 0.003  6.4 MB       region: whole disc*   0.481 / 0.261
arrays: scalar           0.156 / 0.0003               system: one star*     0.257 / 0.018
adv: history             0.483 / 0.003                adv: one sector*      0.513 / 0.020
adv: alpha plane         0.478 / 0.003                adv: one star*        0.517 / 0.016
metadata (index, version, stages, fields, inputs): 0.0000–0.0046, no stage run (rule D4)
* includes the interpreter's first seeded draw, ~9 ms (debt #37). import + registry 0.097–0.105 s.
```

**The profile.** Whole model 0.689 s cold simple, 1.004 s advanced (S20: 0.755 / 1.104).
`systems` 0.242 s (35.1%) in the simple model, `chemistry_dtd` 0.352 s (35.0%) in the advanced
ahead of `systems` (0.251, 25.0%); `sfh` 0.140 / 0.140. The catalogue: 1.49 / 1.50 µs per star
against 224 / 209 ms fixed, 89% / 88% of it independent of how many stars are asked for (D24,
D127). The one-off first seeded draw 10.3 ms (debt #37). `scaling.py` not re-run: no stage
changed. Twelve audit tests: `tests/test_audit_ii_a.py` runs in about a minute, most of it the
two 41-seed diagonals and the six advanced runs.
