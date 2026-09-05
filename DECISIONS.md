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

## Session 10 — the audit

### D94. Convergence is swept one knob at a time, and the sweep carries a control

**Decision.** `galaxy/specs/convergence.py` sweeps N_R, N_t and N_z
*independently*, each against the default grid, and judges every acceptance
scalar's drift against the width of that row's own target interval. Each knob
also carries a deliberately too-coarse **control** point, measured alongside the
sweep, and what the control did when it was measured is recorded on the knob: a
control that stops firing, or one that starts, is a problem.

**Settled by.** GALAXY_INPUTS.md §10 measured the cost exponent at 0.13 in N_R
against ~1 in N_t, so a single "resolution" dial would hide which knob a number
is sensitive to. The seed of the module,
`tests/test_sfh.py::test_scalars_do_not_move_with_grid_resolution`, moved N_R and
N_t together and so could not have told them apart. N_z is swept although the S10
brief names only the other two: it is the third grid axis, rows 6 and 7 are scale
heights, and an audit that leaves an axis out is the defect it exists to find,
one level up.

The control is rule B3 applied to this instrument. **Nothing drifts** — the worst
margin across both models and all three knobs is 0.056 of a target's width — and
a sweep in which nothing drifts is either a converged model or an instrument that
cannot fire, which look identical from the sweep alone. `scaling.py` answers the
same objection by timing the naive convolution it exists to rule out. Measured:
the criterion fires on rows 3, 5, 7 and 16 at N_R = 8 and on thirteen advanced
rows at N_t = 8; row 3 goes first in radius, because it is read at a single
radius and so is the first thing a coarse radial grid loses.

**What the sweep found.** The acceptance table is converged on the default grid
with a factor of about 18 to spare on its worst row. Pushed further, the
criterion first fires below N_R ≈ 16 and N_t ≈ 25, and **never for N_z, even at
N_z = 1**. That is debt #31 and debt #30: the default grid is 25× finer in radius
and 80× finer in time than any acceptance row can detect, and the vertical grid
has one field on it whose one consumer reads column 0.

Drifts are registered exactly as acceptance misses are (rule B5): a recorded
drift prints and does not stop the run, an unrecorded one does, and a recorded
one that has converged is stale and does too (rule B10). The register is empty,
which is the honest state of it and not an omission.

### D95. Debt #12 gives acceptance row 3 a second explanation, and the two are separable

**Decision.** `CONCENTRATION_NORM` stays at 4.1. What changes is the record: row
3's recorded miss now names the competing explanation and the measurement that
tells the two apart.

**Settled by.** Rule B10 says a constant fitted against a broken mechanism has no
claim on its value, and the S10 brief sends this audit at debt #12 first. The
debt says K = 4.1 is quoted for c_vir and used as a c₂₀₀ normalisation "without
the conversion between the two overdensities … folded into K rather than
modelled". The conversion turns out not to be a free choice: the model publishes
its own R₂₀₀ = 212.94 kpc, and debt #10 already established that the 255 kpc it
is set against is a top-hat virial radius. Their ratio is 1.198, so K should be
3.42 and c₂₀₀ = 11.98 rather than 14.35 — and **both pass the only check the
constant has**, since the Milky Way's own measurements span 10–18.

Doing the conversion puts v_c(R₀) at 246.92, inside 248 ± 3, and moves the star
formation rate, the gas mass, the stellar mass and the disc scale length by less
than one part in 10⁹. Row 3 already has a recorded miss whose explanation is that
every baryon sits inside R₀ with no extended component and no bulge (debt #18),
and whose prediction is that rows 2, 3 and 20 close *together*. So the two
explanations make different predictions and **rows 2 and 20 are the
discriminator**, which is the whole content of this decision: not that the halo
is wrong, but that closing row 3 without checking rows 2 and 20 would no longer
be evidence for anything.

Three things measured alongside it. K and z_f enter only as their product, so
c₂₀₀ ≈ 12 is reachable by K = 3.42 at z_f = 2.5 or by K = 4.1 at z_f = 1.92 and
**no measurement of the assembly epoch alone can validate the relation**. The
sensitivity debt #12 records — "about 10 km/s across z = 2–3, three times row 3's
error bar" — is stale: after S2 and S3 changed the baryon profile it is 15.29
km/s, 5.1× row 3's half-width. And the epoch the table wants, z_f ∈ [1.9, 2.1],
lies *below* the cited z ≈ 2–3 rather than inside it.

**Why the constant does not move.** Two reasons, and only the second is about
scope. A value chosen now would be chosen with the model's answer for row 3
already known, which is the move rule B5 exists to prevent; and this session
audits. The chain was followed to its end first, so that whoever does move it
knows what else goes: at K = 3.42 the escape velocity at R₀ falls from 578 to
565 km/s and the present-day gas at R₀ from +0.001 to −0.014 dex, so the advanced
model's one fitted constant `WIND_SPEED` needs refitting by about a hundredth of
a dex and row 22 stays inside its target at −0.0563. The correction is cheap;
the reason to hold it is that it is a candidate answer to an open question.

### D96. What the star catalogue costs, and what D61 got half right

**Decision.** `galaxy/specs/performance.py` profiles every stage of every model
cold in a fresh process, publishes the numbers with no time budget, and gates
only on completeness: every stage of every model must appear.

**Settled by.** Rule B6 — publish the number, not the verdict — leaves nothing
for a threshold to do, and a threshold buried in an instrument is a judgement
made once and then forgotten. What is worth asserting is the omission rule B2
exists to prevent: `tools/timings.py` already fails a route nobody timed, and a
stage nobody profiled is the same defect. Each stage is timed from a run resumed
at its own dependencies, so the number is the stage's rather than the pipeline
prefix's, and the runner's own per-call cost — 0.09 ms of graph build and input
resolution — is measured by resuming with `only=()` and **published rather than
subtracted**.

**D61's question, answered.** The catalogue is 113 ms for the published
20 000-star sample, and **90% of it does not depend on how many stars are asked
for**: the marginal cost is 0.59 µs per star, fitted over an eightfold range of
sample sizes. Of the 100 ms that is fixed, 1.0 ms is setup, **14.9 ms lays out
all 1024 cells at 14.5 µs each**, and 84.3 ms draws in the 516 cells that
actually realise a star, about 163 µs each. D61 said every cell costs eight
`Generator` constructions at about 22 µs, "paid on every run whether or not
anything asks for that cell". The 176 µs that implies is right for a cell that
realises stars — measured at 163 — and **wrong about who pays it: 508 of the
1024 cells realise nothing and cost only their single layout draw.** The
unconditional cost is 14.9 ms, 13% of the catalogue and 3.5% of the whole simple
model. A nine-cell region query costs 2.8 ms, 2.4% of the whole, so the pruning
`materialise(cells=…)` does is real.

**How the split was arrived at, and how it was not.** The obvious method is to
difference the whole-galaxy materialisation against the nine-cell one and solve
for cost-per-cell and cost-per-star. It returns a **negative cost per star**:
both points sit at nearly the same stars-per-cell ratio, so the 2×2 is
ill-conditioned and amplifies timing noise into nonsense. Replaced by a slope
over four sample sizes — the idiom `scaling.py` already uses, and for the same
reason: a difference of two points cannot see what a slope can. The failed
version is recorded here rather than deleted, because the number it produced was
not obviously wrong to look at.

**What is still open.** The cell grid cannot be re-measured without editing the
source: `CELL_RINGS` and `CELL_SECTORS` are module constants and one is bound
into a default argument. That is debt #31, and it is why D61's trade-off has not
been revisited since S5.

### D97. A cold profile bills the interpreter's one-offs to whoever trips them

**Decision.** The first seeded draw's cost is measured in its own fresh
interpreter and published beside the per-stage table, rather than being paid
before the table so as to tidy it.

**Settled by.** `pattern` reads at 8.9 ms cold against 0.3 ms warm — a ratio of
30, the largest in either model, and out of scale with everything the stage does.
It is not the stage. The first `seeds.rng` call in a fresh interpreter costs
8.9 ms and every one after costs 0.023 ms, a factor of about 380, and `pattern`
is the first stage of both models to draw. A per-stage cold profile times each
stage's first execution, so a cost belonging to the interpreter lands entirely on
whichever stage runs into it first, and is then read as that stage being
expensive.

Paying it inside `profile()` before the loop would have produced a cleaner table
and destroyed the only evidence that the effect exists, so it is measured
separately and the table is left as it reads. Rule B6: the number is published,
the correction is not applied. **`tools/timings.py` has the same term in its cold
column** — whichever route first reaches a seeded stage carries 8.9 ms that is
not the route's — and that is debt #32.

### D98. The acceptance table can say it has no testable target

**Decision.** `Quantity.testable` is false for a pointwise row whose interval has
zero width; `spec.untestable()` lists them; the report names them once, as a
defect of the table rather than of any model; and a new row added without an
interval has to declare itself in its note. No verdict changes.

**Settled by.** Debt #17 names two fixes and says the choice belongs to this
audit: read the source's uncertainty, or give the table a way to say "no testable
target". The first was not available — the uncertainty is not in this repository,
and rule B14 will not let a verified tag rest on a document outside it — and
the second is what is implemented.

The stronger reason for not taking the first is that it is no longer honestly
available to *anyone here*. Row 20's answer is known: 5.80 × 10⁹ against
8.0 × 10⁹, a 28% miss. An interval chosen now would be chosen against a known
answer, which is what rule B5 forbids, and the fact that any plausible width
would still leave row 20 failing does not make choosing one honest. So the defect
is recorded and made countable instead, and what discharges it is a citation with
an uncertainty entered *before* the row is next judged.

Row 14 quotes no uncertainty either and is deliberately unaffected: it is
statistical, and an ensemble's central interval can contain a point target, which
is the mechanism debt #8 already put there.

### D99. The one-fetch gate asks git what the repository contains

**Decision.** `tests/test_api.py::js_files` enumerates JavaScript through
`git ls-files --cached --others --exclude-standard` instead of walking the
filesystem behind a denylist of directory names.

**Settled by.** The gate failed on `transport.js` — the one file it exists to
permit — inside a sibling git worktree checked out under `.claude/`. The denylist
held `.git`, `node_modules`, `.venv` and `__pycache__`, and had to grow by one
entry for every new kind of thing that can appear under the root; rule B13 says to
move a correctness condition where it cannot be forgotten rather than to remember
it in N places. `--cached --others --exclude-standard` is the same pair rule C2
already asserts empty at close, so the gate now sees exactly what the repository
is answerable for: newly written files included, ignored ones never.

### D100. Cold timings at S10 (rules B2, B6)

Measured with `uv run python tools/timings.py`, one fresh interpreter per
endpoint, on the same desktop as D93.

    endpoint                 cold s   warm s    c/w      bytes  stages
    viewer: index.html       0.0003   0.0002   1.51        940  -
    viewer: a module         0.0003   0.0002   1.49     21,599  -
    index                    0.0000   0.0000   1.66      1,237  -
    version                  0.0016   0.0014   1.20      1,132  -
    stages                   0.0002   0.0001   1.56      8,645  -
    fields                   0.0007   0.0004   1.53     57,008  -
    inputs                   0.0001   0.0001   2.06      9,091  -
    arrays: one profile      0.0800   0.0002 349.81      4,672  halo,assembly,disc,sfh
    arrays: history          0.1305   0.0027  47.88  6,401,472  halo,…,chemistry
    arrays: scalar           0.0829   0.0002 372.75      1,416  halo,assembly,disc,sfh
    region: one sector       0.1495   0.0037  40.73     18,720  halo,…,vertical
    region: whole disc       0.2679   0.1337   2.00  1,126,208  halo,…,vertical
    system: one star         0.1445   0.0022  65.00      2,816  halo,…,vertical
    adv: history             0.3680   0.0023 160.92  6,401,480  halo,…,chemistry_dtd
    adv: alpha plane         0.3768   0.0027 138.29  6,401,528  halo,…,chemistry_dtd
    adv: one sector          0.3879   0.0034 113.50     18,736  halo,…,chemistry_dtd,vertical_alpha
    adv: one star            0.3750   0.0021 179.33      2,824  halo,…,chemistry_dtd,vertical_alpha

    import + registry: 0.082-0.092 s, paid once per process, excluded from the cold column

**Read within the run.** Every row is 10–15% slower than D93's and the shape is
unchanged, so this is the machine and not the code: no stage's `compute` was
touched this session, and `tools/scaling.py` is therefore not re-run (rule B7 asks
for it when a stage's cost changes). The advanced chemistry still adds about
0.24 s cold to any route that reaches it and nothing warm; metadata is
sub-millisecond with no stage behind it. **Every cold number on a stage-running
route contains the 8.9 ms of D97**, which is 11% of `arrays: one profile` and 2%
of `adv: one sector` — debt #32.

### D101. What this audit did not do

**Decision.** Recorded here so the next session does not have to infer it.

The board asks for two independent audits and a diff of their defect lists. This
is one of the two runs, made without reading the other; **the diff is not in this
branch and cannot be, because making it requires both lists.** It is the first
thing owed after both runs are in.

No physics was changed. `CONCENTRATION_NORM` stays at 4.1 (D95); the
`escape_velocity` midplane is still the first cell centre (debt #30); the cell
grid stays 32 × 32 (debt #31); no acceptance target moved and no recorded miss
was removed. The spec report reads exactly as it did at S9 close — 11 pass, 7
fail for the simple model, 8 pass, 11 fail for the advanced — which is the
correct outcome for a session whose job was to find out what the numbers mean
rather than to change them.

### D102. The statistical criterion rewards a noisy model

**Decision.** Recorded as debt #33 and left in place. `ENSEMBLE_MIN` stays 20,
`CENTRAL` stays 0.95, and the criterion stays "intersects".

**Settled by.** Rule B3 asks what a check cannot see, and this one cannot see the
difference between a distribution centred on the observation and one whose tail
merely reaches it. Measured against row 16's target of [34, 52]: a median of 60
passes on a spread of ±20, and a median of 100 passes on ±60. Widening the
ensemble is monotonically helpful to the model, which is the wrong direction for
an acceptance check to point.

Underneath it, the two constants do not agree. `np.percentile` interpolates, so
the 2.5th percentile of twenty values sits at order-statistic index
0.025 × 19 = 0.475 — between the smallest and the second-smallest. The "central
95 %" interval therefore trims no whole draw, comes to 91 % of the full range,
and is pinned by the two most extreme values in each tail. **The nominal fraction
needs n = 41 to exclude one draw at each end**, and `ENSEMBLE_MIN` is 20.

The instability that follows is visible in the model's own numbers. Across five
disjoint blocks of twenty `pattern_seed` values, row 16's upper endpoint moves
50.2 → 59.8 — more than half the width of the target it is compared against —
while the median moves only 39.5 → 42.5:

    seeds    central 95%              min      max    median   verdict
    0-19     [32.81, 51.87]         32.29    54.83     42.51   pass
    20-39    [35.18, 59.84]         34.58    67.06     40.90   pass
    40-59    [32.31, 57.47]         31.74    58.02     39.51   pass
    60-79    [32.45, 51.87]         32.30    54.98     40.95   pass
    80-99    [31.20, 50.19]         28.98    50.83     40.86   pass

**Why it is not changed here.** What a statistical row *means* is a decision
about the acceptance table, not a defect in an implementation, and `spec.py`'s
own docstring already reserves the revision to a later session. Changing it
during an audit would also make the audit the thing that moved the verdicts. What
is recorded instead is the fact that makes the change cheap: **both live rows
would still pass under the stricter reading** — row 16's medians span 39.5–42.5
inside [34, 52], row 17's 5.68–6.15 inside [4.5, 7.0] — so requiring the median
to lie in the target costs no verdict today and would cost one later, which is
the moment to have the argument rather than after.

### D103. One of the four seeds is read by nothing, and the ensemble is a diagonal

**Decision.** Recorded as debt #34. `world_seed` stays declared.

**Settled by.** `graph` already reports `world_seed` as an unbound input in both
models, which is the deliberate treatment of an input no stage reads *yet*. What
had not been noticed is that `spec.ensemble` varies it anyway: a member is built
by setting every seed to the same integer, so a quarter of the nominal seed
dimension does nothing and the twenty members trace the diagonal of a
four-dimensional space rather than sampling it.

Both are harmless today and measured to be: no published quantity depends on more
than one seed, and row 16 comes out identical whether `pattern_seed` moves alone
or all four move together. They stop being harmless at the same moment — the
bulge rows debt #8 is waiting on (13, 14, 18) are the ones whose residual draws
`world_seed`'s own declaration promises, and the first quantity to read two seeds
is the first one the diagonal cannot see.

### D104. The reproducibility check runs both halves in the same interpreter

**Decision.** Recorded as debt #35; the suite gains the stronger check, the spec
does not.

**Settled by.** `determinism.check_reproducible` runs the model twice and compares
the fields. Within one process, `PYTHONHASHSEED`, set and dict iteration order,
the allocator and every module-level cache are all held constant, so a field that
depended on any of them would compare equal every time. This is rule B3 in the
same shape rule C2 already states for the working copy: the comparison takes the
one path immune to the defect it exists to find. It is not a hypothetical class —
iterating a set of field names to build an array is an ordinary thing to write,
and nothing here would have caught it.

Measured rather than assumed: the model runs identically in three separate
processes at `PYTHONHASHSEED` 0, 1 and 12345 — same stage order, byte-identical
values for all 91 simple and 101 advanced fields. So the hole is latent. The
suite now carries the cross-process comparison; `python -m galaxy.specs`, which is
the report a session actually reads, still carries only the weaker one, and the
fix is the subprocess pattern `performance.py` already uses.

### D105. The diff of the two audit runs

**Decision.** The gate S10 could not meet from inside either run, met here, with
what it is worth stated first.

**What it is worth.** The board asked for two *independent* audits so that the
overlap would measure coverage. These two runs share an author: run 2 was made
knowing everything run 1 found, and aimed deliberately at what run 1 had not
touched. So the diff below measures **what a differently-aimed pass finds**, and
it cannot measure what an independent one would. Reading it as evidence of
coverage would be exactly the error rule B3 names. `[inferred]`

**Run 1 — the model and its cost.** Convergence (`convergence.py`), performance
(`performance.py`), and the calibration audit of the constants. Findings: debt
#12 re-measured and given a second explanation for row 3 with rows 2 and 20 as
the discriminator (D95); debt #29, no acceptance row reads inside 4 kpc; debt
#30, the vertical grid buys nothing and `escape_velocity` is not at the midplane;
debt #31, the default grid is 25× finer in radius and 80× finer in time than any
row can detect; debt #32, a cold profile bills the interpreter's one-offs to
whoever trips them. Debt #24's D61 question answered (D96), debt #17 given a
mechanism (D98), debt #16's discharge quantified at 10 %, debt #26's centre shown
to be the wind and not the grid, debt #27 given a coarse-grid trap. Two defects
found inside run 1's own instruments: the rule D2 gate's directory denylist
(D99), and an ill-conditioned 2×2 that returned a negative cost per star (D96).

**Run 2 — the instruments and the seeded machinery.** Findings: debt #33, a
statistical row tests overlap rather than agreement, and `ENSEMBLE_MIN = 20` is
too small for the 95 % interval it quotes (D102); debt #34, `world_seed` is read
by no stage and the ensemble samples a diagonal (D103); debt #35, the
reproducibility check compares two runs in one interpreter (D104). Two clean
results, recorded because an audit that reports only problems is not an audit:
every row that quotes a ± has `lo`/`hi` equal to that arithmetic, checked across
the whole table; and every one of the six specs has at least one test that makes
it report a problem, so none is a check that cannot fail.

**The diff.** **The two lists do not intersect at all.** Not one defect appears
on both. That is the finding, and it is a warning rather than a comfort: two
passes over one repository, by one author, aimed differently, produced disjoint
lists, which bounds neither list from above. The count of defects found is not
evidence about the count remaining.

Two patterns do cross the boundary. **Every defect either run found in an
instrument was found by the run that was not building it** — run 1 found the D2
gate's denylist while writing something else, run 2 found the ensemble criterion
in a file run 1 had edited that session without looking at it. And **both runs
found a constant chosen once and never re-derived**: run 1 the default grid
(#31), run 2 `ENSEMBLE_MIN` (#33). Neither is a physics constant, so rule B10 as
written does not reach them — it speaks of a constant "fitted against a broken
mechanism". The audit's own suggestion is that the rule wants widening to the
constants inside the instruments, which is what LESSONS.md now carries.

**Still owed.** A third pass, by someone who has read neither list, is the only
thing that would measure what these two could not.

**One thing in the log is wrong and is left wrong.** Commit `b8c0fbd`'s subject
reads "S10 partial close (run 2 of 2)"; that work is **run 1**, and was numbered
before a second run on this branch was asked for. Rule C2a forbids the rewrite
that would fix it, and a wrong subject discovered later is cheaper than a
force-push, so it is recorded here instead: `c4549b4`–`b8c0fbd` is run 1,
`7b0a4e1` is run 2.
