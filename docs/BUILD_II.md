# BUILD_II — the second build: the `azimuthal` model and the render contract's model side

Seventeen board rows, S25–S41, in `GALAXY_PLAN.md` §5e. Hand a session this
document, `RULES.md`, `BRIEF.md`, and the sections of `GALAXY_INPUTS.md` its
phase names. **Phases 7–11 and V1–V4 additionally require `RENDER_PHYSICS.md`**,
the model/renderer contract those phases implement.

Everything here is `[inferred]` design unless tagged. Everything marked
**NEEDS SOURCING** must be read from a source before it enters code, not entered
from recall (rule B9); `RENDER_PHYSICS.md` §10 collects the ones the rendering
phases owe. Delegate the reading (a read-only agent with web access returns a
number and a citation: GALAXY_PLAN.md §5, "delegate reading, not deciding").

The owner's plan was written against the repository as it stood before D170
(three models) and before S23–S24 (the render plan's model side). It was
reconciled against the repository on 2026-09-26 and **each phase below opens
with what already exists**, so that no session rebuilds a stage that is there
or rules on a question already ruled. The owner's four rulings that shaped this
reconciliation are in `DECISIONS.md` D172.

---

## How the rows run (the protocol, adapted)

- **One board row = one phase = one `session-NN` branch = one `--no-ff` merge**,
  closed by §5's ritual: board ticked, `progress.py`, the full suite backgrounded
  with `EXIT=$?` on its log and the merge gated on that line, DECISIONS/LESSONS,
  cold timings when a stage's cost changes, RESUMING/BRIEF, MANUAL_TODO's tag
  row, push, `verify_clone`.
- **Sessions are sequential, so numbers are sequential**: debts from **#80**,
  decisions from **D173**, each taken at the moment the entry is written. No
  reserved blocks (S15's lesson: reservations were restated as counts the first
  time a session appended out of order).
- **Rows marked Fable** are done by the orchestrating session itself: every
  ruling, every derivation decision, every interface design, and the audit.
  **Rows marked Opus** are delegated to an Opus subagent in a worktree on the
  session branch with this document's phase text, the gate and `RULES.md`; the
  subagent neither pushes nor writes `DECISIONS.md` (GALAXY_PLAN.md §5,
  "Subagents and the remote"). The orchestrator reviews the diff against the
  gate, runs the suite, writes the decision, and closes the row. Two independent
  Opus rows may run as two subagents at once; their merges are still one at a
  time, in row order.
- **Probe before build** in every physics phase (§5d's rule): a fifty-line probe
  with the repo unchanged has overturned the register's stated lever three times
  (D110, D113, D114).
- A row that stops early closes partially (C2d): commit, push, BRIEF, ◐, no merge.

---

## Reconciled: what the repository already has (2026-09-26)

| Plan assumed | Repository has | Consequence |
|---|---|---|
| Three models: `simple`, `chemical`, `realistic_advanced` | **One model, `basic`** (D170, 2026-09-25) | Shared derivations go into `basic`; the new model is `basic` with one slot swapped, named **`azimuthal`** (D172) |
| Isochrone ruling needed (Phase 3) | **Ruled and built**: PARSEC v1.2S table committed, per-star L and T_eff on the catalogue (D164) | Phase 3 is the photometric *rows*, Q(H⁰), winds; the table gains bands |
| `ism-stage.patch` gated on #79 | **Merged**; #79 discharged (D163); row 21 judged, a miss under #17 | Phase 7 is the *extension* only: scattering, thermal emission, PAH |
| No line emission | `halpha_surface_brightness` = Σ_SFR × constant (D166) | Phase 9 replaces it; the constant becomes a check |
| No dust in the viewer | Dust subtracted per line of sight in the ray-marcher (D167) | R4 done; V2 replaces its slab with the emitting dust of Phase 7 |
| `sample_region` missing | `/api/region`, per-cell determinism (D60), cells galaxy-scale | Phase 8 adds the cell **hierarchy**, not the function |
| Arm number possibly hard-coded | **A seeded coin toss between m = 2 and 4** `[verified: pattern.py ARM_MULTIPLICITIES]` | Phase 1's finding, already made; Phase 1b decides |
| Arm amplitude derived or seeded (RENDER_PLAN M1) | **Two experimental inputs**, `arm_amplitude` and `bar_amplitude`, 9 controls of the ceiling's 12; debt #23 still ruled permanent; no DECISIONS entry (D171 records it) | Phase 1b, before Phase 2 (D172) |
| A1 justified by `bench2.py §4` | **`bench2.py` is in neither the tree nor the history**; the 8× is "8 iterations" assumed `[verified: GALAXY_INPUTS.md §10 table, "Coupled inflow/outflow fixed point, 8 iterations"]` | Phase 0's case holds from inside the repo |

---

## Phase 0 — rewrite A1 (S25, first commit)

Own commit, before anything else. Small, and it unblocks the rest.

### Why it needs rewriting

**Its stated justification is not a measurement.** A1 reads *"Justification:
measured — the coupled fixed point is an 8× multiplier"* `[verified: RULES.md A1]`
and cites `bench2.py §4`, a file the repository has never contained (rule B14:
a verified tag requires a citation to something inside this repo). The register's
own cost table lists the multiplier as *"Coupled inflow/outflow fixed point, 8
iterations — ×8 on top"* — an assumed iteration count multiplied through
`[verified: GALAXY_INPUTS.md §10]`. The benchmark's **exponents** were measured
and found a real defect; this multiplier was never measured at all.

**It conflates three claims.** *"Every field computable in one pass, in a fixed
order"* restates A6. *"No fixed-point solvers on the grid"* bans within-stage
iteration. *"Iteration only where bounded and cheap"* permits it. Sentences 2 and
3 contradict; sentence 1 is a duplicate.

**The real justification was never written down**, and it is stronger: the
six-checkpoint workflow runs a **prefix** of the pipeline and stops. A cycle
between checkpoints makes a prefix uncomputable — checkpoint 1's preview could
not be drawn without running checkpoint 3. That is a design constraint, not a
performance one, so no benchmark can overturn it.

**There is already a precedent in the codebase for the case A1 appears to
forbid.** `halo.py` solves the adiabatic contraction — baryons at 55–60% of the
enclosed mass inside 10 kpc — as a bisection on a monotone function, in one
pass `[verified: model/galaxy/stages/halo.py, contracted_halo]`. Strong coupling
does not by itself require a fixed point.

### The replacement text

> **A1. The stage graph is acyclic; iteration lives inside a stage.** No stage
> may depend on a later stage's output. Within a stage, iteration is permitted
> when **termination is guaranteed in advance** — a bisection on a monotone
> function, a fixed step count with a known error bound — and forbidden when it
> is a convergence loop whose step count depends on the data.
>
> *Justification: the staged workflow runs a prefix of the pipeline and stops, so
> a cycle between checkpoints makes a prefix uncomputable and the lock semantics
> of rule D1 become a lie. A design constraint, not a performance one.*
>
> *Precedent: `halo.py` solves the adiabatic contraction — baryons at 55–60% of
> the enclosed mass — as a bisection in one pass `[verified: halo.py]`.*

### Also correct the register

Debt **#26** (the mass-loaded wind) is ruled permanent citing A1's fixed point
across checkpoints 1 and 3, and debt **#3** (m_d from feedback physics) is ruled
permanent *as #26 from the other end* `[verified: GALAXY_INPUTS.md §11, items 3
and 26]`. Under the rewrite neither ruling automatically survives, and the
question changes shape: not *"may we have a fixed point"* but **"can the retained
budget be written as a root of a monotone function of itself inside checkpoint 1,
the way the contraction was?"** — the halo contracting around a budget that the
wind at that potential would leave.

Re-rule both or record that they are re-opened. Do not silently leave a
permanent ruling resting on a clause that no longer exists. The S22 map at the
head of §11 counts them; update its counts.

**Gate.** Suite green. `graph.py` unchanged — the rewrite removes a duplicate,
it does not relax the acyclicity check. `tests/test_docs.py` still passes (the
A1 text carries a `[verified: …]` with an in-repo citation).

---

## Phase 1 — the pattern reorder (S25)

**This is the prerequisite for azimuthal star formation, and the only step in
this plan that can move an acceptance row that currently passes.** Do it alone,
in its own commits after Phase 0.

Two stage declarations force the whole ordering `[verified: pattern.py, the
`bar` stage's requires and the `pattern` stage's requires]`:

```
bar     requires ("thin_disc_scale_length", "circular_velocity_resolved", "halo_circular_velocity")
pattern requires ("bar_half_length", "shear_rate", "circular_velocity_resolved")
```

`circular_velocity_resolved` comes from `sfh` (checkpoint 3), which is why the
pattern sits behind star formation and why **`sfh` publishes nothing on a φ
axis** — every field it declares is `("R",)` or `("R", "t")` `[verified: sfh.py]`.

`circular_velocity` is published by `disc` at checkpoint 1. Swap the dependency
in both stages and `graph.py` moves the pattern branch ahead of `sfh` on its own.
`chemistry_dtd` also reads `circular_velocity_resolved` (for the escape
velocity); it stays at checkpoint 3 and is not touched.

**The risk, named before running.** `disc_dominance` is where the resolved curve
genuinely differs from the analytic one, and it sets `bar_half_length`.
**Acceptance row 15 passes at 4.88277 in [4.8, 5.2]** `[verified: python -m
galaxy.specs, 2026-09-25]` — this change can move it out. The pitch angle is
nearly immune, because `PITCH_YU` makes it a seeded draw with a weak trend.

**Gate.** Rows 15, 16, 17 measured before and after, both numbers recorded in
the decision. If row 15 leaves its window, that is a result to record under B5,
not a reason to retune `disc_dominance`. Determinism and convergence re-run: the
pattern's checkpoint changes, and `graph` requires a seed to bind at the
checkpoint of its earliest reader (S17) — `pattern_seed`'s hypothesis is 4 and
must still hold, or the input's `checkpoint_hypothesis` is what moves.

### The arm number — the finding, already made

The stage publishes `arm_multiplicity` as **a seeded draw of 2 or 4 with equal
odds** (`ARM_MULTIPLICITIES = (2.0, 4.0)`, `rng("pattern_seed", "arms")`)
`[verified: pattern.py]`. §4b assigns it verdict C — *"swing amplification sets
a preferred m; real galaxies at similar X differ"* — and the draw is that
verdict's remedy with the mean part left out: there is no m = 3, no flocculent
state, and no dependence on the shear rate or the disc mass fraction, both of
which the stage already reads. Most real spiral morphologies are therefore
unreachable, and no rendering work will change that. Phase 1b decides it;
this phase records it in D-next and does nothing about it.

Also note **feathering** — the short dust spurs running off arms into the
interarm. They come from the arm's own shear acting on compressed gas, so they
are downstream of Phase 2 rather than new physics. Not this phase's job; noted
so it is not mistaken later for missing structure.

---

## Phase 1b — the amplitudes derived or seeded, and the arm number (S26)

Ruled in before Phase 2 (D172): Phase 2 reads `pattern_density_contrast`, and
the contrast's amplitudes are today two **inputs** — `arm_amplitude` and
`bar_amplitude`, "experimental controls on the bottom bar" `[verified:
registry.py; docs/future_ideas.md]` — so as planned the star-formation
modulation would be built on a hand control, which RENDER_PLAN M1 ("it does not
become a control") and rule A2 both forbid, and which puts the input vector at
9 of the ceiling's 12.

**Derive A** from what the stage has: swing amplification's gain is set by the
shear rate and the disc mass fraction (`shear_rate`, `disc_dominance`, both
published by `bar`), and the bar's contrast by its length relative to the disc.
A derivation that closes is verdict B; one that leaves real galaxy-to-galaxy
scatter is verdict C, and under §4b the remedy is **derive the mean, seed the
residual** on `pattern_seed`, exactly as `pitch_angle` is. **It does not become
a control.** Both inputs are removed; the viewer's bottom bar loses two sliders.

**The arm number**, the same decision by the same mechanism: swing amplification
predicts a preferred m from X = κ²R/(2πGΣm) `[recall — NEEDS SOURCING: Toomre
1981; Sellwood & Carlberg 1984]`, which is the disc mass fraction the stage
reads. Derive the preferred m (2, 3 or 4) with the residual seeded, and add the
**flocculent** state where the amplification is weak (A below a threshold the
derivation itself gives). Or, if the derivation will not close, keep the draw
and widen it to {2, 3, 4} with the odds stated — but say which and why.

**Gate.** Rows 15–17 unmoved (the amplitudes do not enter them). The contrast
still averages to 1 around every ring `[verified: tests/test_pattern.py]`.
Determinism re-pinned. Debt **#23 re-ruled**: it is "permanent, a property of
the model's scope" on the grounds that no stage publishes a non-axisymmetric
density — and one does. Discharge it, or restate what it now names (the
amplitude is derived to a mean whose scatter is real). The input count on
`/api/inputs` is 7 controls again.

**Fable**, because the derivation decision is the whole session and a wrong
amplitude passes every gate.

---

## Phase 2 — azimuthal star formation, and the model declaration (S27)

### The design decision, made here and not in the session

**The histories must not gain a φ axis.** `sfr_surface_density_history` is
(R, t) at 400 × 2000. Adding φ at 360 gives 288 million cells and a payload
nobody can fetch.

It is also **physically wrong to add it**. Gas orbits and mixes azimuthally on
~100 Myr, far faster than enrichment timescales, so the chemical evolution
*should* be azimuthally averaged. The arms do not change what the gas becomes;
they change **where stars are when they form**.

So: `sfh_azimuthal` keeps every history on (R, t) exactly as now, and publishes
**one new (R, φ) field** — a present-day star-formation modulation, read from
`pattern_density_contrast` through the star-formation law's own non-linearity:
if Σ_gas(R, φ) = Σ_gas(R) · c(R, φ) then Ψ ∝ Σ_gas^KS_INDEX gives a modulation
c^KS_INDEX, renormalised so its gas-weighted mean around the ring is 1 (the
threshold's `tanh` switch applied per cell, since an arm can carry gas over the
threshold that the ring mean does not). The catalogue then places young stars
using it — the *young* ones, on the pattern's own timescale (an arm crossing is
~100 Myr; older stars have phase-mixed and keep the density contrast alone).

That keeps the memory flat, keeps the chemistry correct, and gives arms that make
stars.

### The model

```python
# galaxy/models/azimuthal.py
AZIMUTHAL = MODELS.register(Model(
    name="azimuthal",
    stages=tuple(("sfh", "sfh_azimuthal") if slot == "sfh" else (slot, impl) for slot, impl in BASIC.stages),
    constants=BASIC.constants,
))
```

Built **from `BASIC`'s tuple**, so the two cannot drift (rule B13); a test
asserts they differ in exactly one slot. `sfh_azimuthal` publishes everything
`sfh` publishes under the same contract (`FieldDecl.contract`, D86) plus its own
field as `optional=True` — the runner's optional machinery that D170 reverted is
what a second model needs back, and D169's tests are the pattern to restore.

**Everything else this plan builds is a shared stage mapped by both models.**
Photometry, remnants, the stellar halo, globular clusters, supernova rates, dust
emission, clouds and nebular lines are derivations, not contested physics, so
they go into `basic` and `azimuthal` inherits them through the tuple above. What
distinguishes `azimuthal` is the azimuthal star formation. That is one slot,
which is how a model difference is supposed to look.

**The viewer** shows the model toggle again when the registry holds two
`[verified: D170 — hidden at one]`; the catalogue's young stars follow the
modulation in `azimuthal` and the contrast alone in `basic`.

**Gate.** Both models pass preflight, graph and determinism; `sfh_azimuthal`'s
modulation integrates to the axisymmetric SFR over φ at every radius, so the
total star formation is unchanged and only its distribution moves. **Assert
that** — it is the check that the modulation is a redistribution and not a new
source (RENDER_PHYSICS §7). Every acceptance row reads the same in both models
at the defaults (the rows are radial and vertical): assert that too, and record
any that do not.

**Opus**: the contract is decided above and the gate is an assertion.

---

## Phase 3 — photometric rows, the ionizing budget, and winds (S28)

**Reconciled.** The ruling the plan asks for was made at D164: PARSEC v1.2S,
tabulated, 1.1 MB committed, `tools/fetch_parsec.py` regenerates it; chosen
over MIST for its size and licence `[verified: docs/future_ideas.md]`. Per-star
`star_luminosity` and `star_temperature` exist and are looked up inside
`materialise`, so a region query carries them. No `star_rgb` is published and
none will be: the temperature's declared ramp is the computed blackbody cmap
(A9), and V1 makes colour a filter integral.

### The table gains bands

`fetch_parsec.py` already asks CMD for the UBVRIJHK system and keeps four
columns `[verified: tools/fetch_parsec.py, docstring and the column map]`. Keep
the band magnitudes too — U B V R I J H K, absolute, per isochrone point — and
regenerate the `.npz` (a network fetch; the raw tables stay out of the repo).
Extend `photometry.population_light` the same way `light.py` did for
bolometric light: **per-band light per unit mass formed**, integrated once along
every isochrone, so the galaxy-level numbers come from the *field* (the whole
history) and not from the 2 × 10⁴-star sample.

### Publish

Galaxy-level: `absolute_magnitude_b`, `absolute_magnitude_v` (and the other
bands as scalars), `colour_b_v`, `mass_to_light_v`, and `photometric_scale_length`
fitted to Σ_V(R) rather than the mass. Per star: `star_magnitude_v` at least
(the catalogue column the brightest-N mode should rank by, D168, in place of
bolometric luminosity — a display choice made physical).

### The ionizing budget — it rides along for almost nothing

`star_ionizing_photons` — Q(H⁰), the hydrogen-ionizing photon rate — is a
function of L and T_eff, both of which the catalogue carries, so it is one more
column rather than new physics; and a population integral `ionizing_photon_rate`
(R) from the same per-age tables, since the field is what the galaxy-scale
emission reads.

**Everything nebular depends on it.** Q is a brutally steep function of mass —
an O5 emits ~10⁴⁹ photons/s, a B0 about 10⁴⁸, and below that it falls off a
cliff `[recall — NEEDS SOURCING]` — so it is set by the top few rungs of the IMF.
**The ruling this phase owes**: a blackbody integral above 13.6 eV is wrong by a
factor of a few for O stars against atmosphere models `[recall]`; the sourced
alternative is a tabulated q₀(T_eff) calibration for O and early B stars
`[recall — NEEDS SOURCING: Sternberg, Hoffmann & Pauldrach 2003; Martins,
Schaerer & Hillier 2005]`, a Level 0 table. Weigh that the youngest isochrone
reaches 64 M☉ at 4 Myr and that stars heavier than it are NaN `[verified:
photometry.py docstring]`: the top of the IMF is partly unresolved by the table,
and the ionizing budget must say what fraction of Q it cannot see.

Also `star_wind_luminosity` (mechanical, ½ Ṁ v_∞², for Phase 10, with the
mass-loss and terminal-velocity prescriptions `[recall — NEEDS SOURCING: Vink,
de Koter & Lamers 2001]`) and a Wolf–Rayet flag: WR stars are brief but harden
the ionizing spectrum enough to change [O III]. PARSEC's phase label does not
name WR, so the flag is a **stated proxy** (hot, luminous, post-main-sequence at
high initial mass) and its declaration must say so.

### What it unlocks

**These are the rows the project has been missing**, and several are *population*
relations rather than one-galaxy fits — the validation problem §11 of the
inputs document names.

| Quantity | Target | Source |
|---|---|---|
| M_B | −20.70 | `[verified: BHG16 Table 2]` |
| M_V | −21.37 | `[verified: BHG16 Table 2]` |
| B − V | 0.73 | `[verified: BHG16 Table 2]` |
| Υ_V (M/L) | 1.70 | `[verified: BHG16 Table 2]` |

BHG16 Table 2 also carries ugriz magnitudes and the other Johnson colours; take
them from the table rather than from recall (delegate the read). Note its own
caveat: the SDSS magnitudes and colour indices use different calibrations, so
magnitude differences and colour indices are not consistent with each other — a
detail that belongs in the rows' notes. **The uncertainties are the table's to
state** (debt #17: a zero-width target is untestable by construction, D100).
Rows 25–28 in `spec.py`, `[verified: BHG16 Table 2]`, with the dust question
stated in each note: the model's light is intrinsic and BHG16's magnitudes are
what, exactly? Read the table's own definition before choosing which is judged.

**And Tully–Fisher becomes computable**, which is a scaling relation across a
rolled population rather than a fit to one galaxy. It needs an instrument the
spec does not have: a row judged over a **sweep of an input** (`halo_mass`)
rather than over seeds — build the instrument first (B1), and give it a source
`[recall — NEEDS SOURCING: the B-band TF zero point and slope]`.

**Opus**, with the Q(H⁰) ruling written up for the orchestrator to make: the
rows are in `spec.py` and the table's columns are a fetch.

---

## Phase 4 — stellar remnants and planetary nebulae (S29)

Depends on Phase 3 for lifetimes and the band tables.

Roughly **10–15% of a galaxy's stellar mass** is in remnants `[recall — NEEDS
SOURCING]`, and the catalogue currently publishes living stars only (a dead
star is NaN in L and T_eff, D164). The stellar mass acceptance row is counting
only what still shines — or rather, `stellar_mass_total` counts locked mass
through `RETURN_FRACTION`, and this phase says what that locked mass *is*.

Derive from the catalogue plus an initial–final mass relation `[recall — NEEDS
SOURCING: Cummings et al. 2018 for white dwarfs]`: below ~8 M☉ and past its
lifetime → white dwarf; 8–20 → neutron star; above → black hole. Black hole
mass is metallicity-dependent, since weaker line-driven winds at low metallicity
leave heavier remnants `[recall — NEEDS SOURCING]`.

**No new inputs.** Add `star_remnant` as a category column on the catalogue
(`none / white_dwarf / neutron_star / black_hole`) and `remnant_mass_fraction` as
a scalar from the population integral, not the sample.

### Planetary nebulae, while the lifetimes are open

Intermediate-mass stars ending as white dwarfs pass through a planetary nebula
phase, and the catalogue plus the lifetimes give it directly: a star within the
phase's duration of its death `[recall — NEEDS SOURCING: ~10⁴ yr]`.

**Build it for one specific reason:** the planetary nebula luminosity function
has a famously universal bright-end cutoff in [O III] 5007, M* ≈ −4.5
`[recall — NEEDS SOURCING: Ciardullo et al.]`, which makes it a
**population-level acceptance row** rather than another fit to one galaxy.
Those are the rows this project is short of.

The emissivity itself belongs to Phase 9; this phase publishes which stars are
in the phase (`star_remnant` gains a `planetary_nebula` category, or a flag) and
for how long. **Opus.**

---

## Phase 5 — globular clusters and the stellar halo (S34, after Phase 11)

Two derivations off inputs that already exist. Neither depends on Phases 1–4.
**Do it after Phase 11**, so the η relation lands as a check on the cluster mass
function rather than as a separate assertion.

**Satellite galaxies were cut from this phase.** The reason is recorded at the
end of this section; do not reinstate them without reading it.

### Globular clusters — sourced

    M_GC = η · M_halo

| | Value |
|---|---|
| η, all clusters | **(3–4) × 10⁻⁵** |
| η_b, metal-poor (blue) only | **(2–2.5) × 10⁻⁵** |
| Form | **linear, one-to-one** |
| Scatter at fixed M_halo | **σ ≲ 0.28 dex**, approximately constant |
| Valid range | **10¹⁰ ≲ M_halo/M☉ ≲ 10¹⁵** |

`[verified: Boylan-Kolchin 2018, "The globular cluster–dark matter halo
connection" — https://pmc.ncbi.nlm.nih.gov/articles/PMC6288678/]`

Five decades of halo mass, linear throughout, with a scatter that does not grow.
It derives a whole population from input #1 alone.

**Under §4b this is derive-the-mean-seed-the-residual**, exactly like the
dust-to-gas ratio: 0.28 dex is real and intrinsic, so the mean is a derivation
and the residual is a seeded draw on `world_seed`. Do not publish the mean and
call it the answer.

**The blue subset is a second free result.** η_b being separately measured means
the metal-poor/metal-rich split falls out of the same relation — and the
metal-poor clusters are the accreted ones, so this ties to `mergers[]` without
any new mechanism.

**Consistency check, which passes.** Milky Way at M₂₀₀ = 1.1 × 10¹²:
3.5 × 10⁻⁵ × 1.1 × 10¹² ≈ 3.9 × 10⁷ M☉. At a typical cluster mass of
~2.4 × 10⁵ M☉ that is ~160 clusters, against the **157** in the Harris
catalogue. The relation reproduces the Milky Way without being fitted to it.

**Acceptance row on mass, not count.** A count needs a mean cluster mass, which
is a second constant and a second source. Read the observed system mass off the
Harris catalogue (`https://physics.mcmaster.ca/~harris/mwgc.dat`) rather than
from the ~4 × 10⁷ figure in circulation; it is the catalogue's to state.

**With Phase 11 built first**, the globulars are the bound survivors at the
massive end of the cluster mass function integrated over the history, and η is
what that integral must reproduce: **one mechanism, and η a check on it**.

### The stellar halo

Accreted satellites, and `mergers[]` already carries their mass ratios and
times. Close to an integral over a list the model has. Its mass is in BHG16 §6
as `Ms`; read it rather than recall it.

Note that this stage consumes the *debris* of satellites without needing the
satellites themselves to exist as objects — which is why cutting them below does
not touch it.

### Why satellites were cut

An earlier draft of this phase said satellites come from the subhalo mass
function, "a ΛCDM prediction rather than an observation, so derivable in the
strong sense." **The slope is right and the conclusion is wrong.**

The subhalo mass function does have slope α ≈ −1.8, nearly self-similar across
host masses `[verified: Bullock & Boylan-Kolchin 2017 —
https://ned.ipac.caltech.edu/level5/Sept18/Bullock/Bullock1.html]`. But that
same review gives **~1000 subhalos above 10⁷ M☉ within 300 kpc** of a
Milky-Way-mass host against **~50 known luminous satellites**. A factor of
twenty — the missing satellites problem.

So a satellite count is not a subhalo count. Which subhalos light up is set by
galaxy formation efficiency collapsing at low halo mass, and that is contested
physics: under B12 it would need a named ruleset with its alternative kept
beside it, plus a blocking ruling on which occupation prescription to adopt.
The acceptance row would also be untrustworthy — ~50 is a lower bound on a
census that has roughly tripled since SDSS and is still rising with DES and
LSST, so the row would test survey depth rather than physics.

**Cut, not deferred.** If it is ever revisited, the useful thread is that the
threshold is time-dependent — 10⁶–10⁷ M☉ with H₂ cooling, ~10⁸ atomic, but
> ~10⁹ after reionization `[verified: Nadler 2025 —
https://arxiv.org/html/2503.04885]` — and input #3 `halo_assembly_z` already
says when the halo assembled relative to reionization. The occupation fraction
would therefore come from an existing input rather than a new control. That is
the one argument in its favour, and it was not enough.

**Opus.**

---

## Phase 6 — supernova rates and the habitable zone (S30)

**Core-collapse rate** is SFR × IMF, both of which exist: the `population`
stage already holds the Kroupa integrals `[verified: systems.py, compute_population]`,
so the number of stars above 8 M☉ per unit mass formed is one more of them.

**Type Ia rate** is the delay-time distribution convolved with the star formation
history — `chemistry_dtd` already computes exactly that convolution for the
iron `[verified: chemistry_dtd.py]`; publish the rate it implies. With one
model plus `azimuthal` both carrying the DTD, nothing is optional here; declare
it plainly.

**Rows.** The Milky Way's core-collapse and Ia rates are measured, with
uncertainties `[recall — NEEDS SOURCING: Adams et al. 2013 for core-collapse;
Li et al. 2011 / Maoz & Graur 2017 for the Ia rate per unit mass]`. Two rows,
sourced by an agent before they are entered.

**The galactic habitable zone** was in the original design as derivable from
metallicity plus supernova rate (§4b, verdict A) and was never built. Build it —
and **do not give it an acceptance row.** It is a model output nobody has
measured; inventing a target would be choosing a number with the answer known
(rules B5, B9). Record that it is deliberately unjudged, with the reason, in the
field's own `about` line, so it does not read as an oversight the way row 21 did
for twenty-three sessions.

**Opus.** Independent of every other phase; may run as a second subagent beside
Phase 4.

---

## Phase 7 — dust radiates, not only absorbs (S31)

**Reconciled.** The patch the plan describes is merged (D163): the `ism` stage
publishes `gas_midplane_pressure`, `gas_molecular_fraction_profile`,
`dust_to_gas_ratio`, `dust_surface_density` and `dust_extinction_v`; row 21 is
judged and is a recorded miss under #17, with Leroy's pair tested and killed
`[verified: spec.py, the row-21 Miss]`. The viewer already subtracts the dust
per line of sight (D167). What remains is the extension.

The existing stage gives extinction — A_V, a scalar per (R). That draws a dust
lane as a hole. Three things are missing and all three are needed:

**Scattering.** The blue haze around a disc and the lit rims on dust lanes are
*scattered* starlight. Needs the extinction law shape (R_V), the albedo
(~0.5–0.6 in V) and the scattering asymmetry g (~0.6, strongly forward-throwing)
`[recall — NEEDS SOURCING: Draine 2003; Weingartner & Draine 2001]`. Three
constants, not three fields, and they turn a silhouette into dust.

**Thermal emission.** Absorbed ultraviolet comes back out in the infrared as a
modified blackbody, emissivity index β ≈ 1.5–2 `[recall — NEEDS SOURCING]`.
Needs a dust temperature from the heating balance: the light absorbed per unit
dust mass at each radius, which the `light` stage's Σ_L and the ISM's τ give.
Publish `dust_temperature`(R) and `dust_infrared_surface_brightness`(R).

**PAH features** at 3.3, 6.2, 7.7, 8.6 and 11.3 µm `[recall — NEEDS SOURCING:
Draine & Li 2007]`. These trace the photodissociation region — the layer between
ionized gas and molecular cloud — because PAHs are destroyed in hard radiation
fields. They are most of what an infrared image of a star-forming region actually
shows. PAH abundance falls with metallicity `[recall — NEEDS SOURCING]`, so this
couples to Z(R, t) and makes metal-poor galaxies look genuinely different rather
than recoloured. Publish `pah_fraction`(R) and the radiation field G₀(R).

**Gate — energy balance.** Total ultraviolet and optical absorbed must equal
total infrared emitted, per radius and integrated, asserted in the suite
(RENDER_PHYSICS §7). This is the test that catches an extinction law and an
emission model that disagree, which is the class of defect that put the
extinction coefficient out by a factor of 162 and then by 1.38 with no test
catching either `[verified: DECISIONS.md D163]`.

**Opus.**

---

## Phase 8 — the cloud catalogue and the cell hierarchy (S32)

**Read `RENDER_PHYSICS.md` §0 and §5 first.** That document specifies the
interface; this phase builds the model side of it.

The galaxy scale and the nebula scale are six orders of magnitude apart, so the
model does not produce pillars or filaments. It produces a **catalogue of
molecular clouds**, each carrying a parameter vector from which the renderer
synthesises the interior on demand, deterministically.

The ISM stage gives the molecular surface density and midplane pressure, so a
cloud population is a short step: a mass function `[recall — NEEDS SOURCING:
dN/dM ∝ M^−1.8 to −2, Rosolowsky 2005]` normalised to Σ_H₂(R) × the pattern
contrast, sizes from the mass–radius relation and Mach numbers from the
size–linewidth relation `[recall — NEEDS SOURCING: Larson 1981; Heyer et al.
2009]` at the local sound speed. **Clouds are an object class** beside stars
(`of="cloud"`, a `core/` edit and a decision), drawn per cell by the same
cell-and-index machinery so that a region's clouds are a sweep's clouds (D60).

Two fields in the vector do most of the visual work and neither is obvious:

- **`mach_number`**, which sets the log-normal density PDF width
  σ_s² = ln(1 + b²ℳ²) `[recall — NEEDS SOURCING for b: Federrath et al. 2008,
  2010]`. That PDF is what generates clump-and-filament structure. Mean density
  alone produces fog.
- **`ionizing_source_offset`**, the vector from cloud centre to the embedded
  cluster. Pillars are the shadows of clumps that survived the ionization front
  eating the cloud from one side, so this is what makes them point the right way.

Add **`density_gradient`** for the same reason bubbles sit off-centre in their
clouds, and **`age`** with a state — embedded, blown open, dispersing, remnant —
drawn against a cloud lifetime `[recall — NEEDS SOURCING: ~20–30 Myr]`. Age
matters because a real field shows regions at different stages side by side,
and the difference between them is age rather than kind.

**The cell hierarchy.** The star catalogue is a sample, not a census, and
zooming needs stars down to the bottom of the IMF inside a tiny volume.
`/api/region` already answers any window deterministically, but its cells are
kiloparsecs across (RENDER_PHYSICS §0, §5c). Add levels: a level-k cell is one
of 4ᵏ children of a level-0 cell with its own seeded stream, a request names its
level, and the density a child draws from is its parent's density at the
child's centre. This is an interface change and the piece most likely to be
missed until the viewer needs it.

**Gate.** `/api/region` called twice on the same bounds and level returns the
same stars and clouds; on overlapping bounds it agrees on the overlap; **across
levels, a parent's stars are its children's** (the union property), and a
smaller sample is still a prefix of a larger one within a cell. The cloud mass
integrated over the galaxy equals the molecular gas mass the ISM publishes
(RENDER_PHYSICS §7's redistribution rule, for clouds).

**Fable**: the hierarchy is a determinism contract, and a contract that holds
at one level and breaks at another passes every existing test.

---

## Phase 9 — nebular and shock emission (S35)

Depends on Phase 3 (Q) and Phase 8 (clouds and their densities).

Publish **line emissivities, not colours** — Hα, Hβ, [O III] 4959/5007,
[S II] 6717/6731, [N II] 6548/6583. Recombination lines follow from Q and
density (Case B `[recall — NEEDS SOURCING: Osterbrock & Ferland]`); the
collisionally excited lines need electron temperature, ionization parameter and
abundance — **a ruling of the isochrone kind**: tabulated photoionization grids
(a Cloudy-derived table, a data dependency) against analytic emissivity fits (no
dependency, a calibration debt). Record the ruling and its reason; do not
default into one.

**The abundances are nearly free.** O and S are α elements and the chemistry
already carries [Fe/H] and [α/Fe]. Nitrogen is the exception — partly secondary,
so it scales differently `[recall — NEEDS SOURCING]` and needs its own treatment
rather than being lumped in.

**Emissivity is volumetric, not a surface** (`RENDER_PHYSICS.md` §4). Publish
per unit volume at region scale (a new unit in the closed vocabulary) and let
the renderer integrate along the ray; limb brightening then appears for free and
is correct at any viewing angle. At galaxy scale the same stage publishes the
surface integral, and each declaration says which it is.

**Clumping.** Emission measure goes as n²ℓ and ⟨n²⟩ ≠ ⟨n⟩², so mean density gets
brightness wrong by a large factor. The clumping factor comes from the same
log-normal PDF as Phase 8's structure — one mechanism, two payoffs.

**Diffuse ionized gas.** Warm ionized medium between the HII regions,
contributing perhaps 20–50% of a galaxy's Hα `[recall — NEEDS SOURCING]`. Needs
an escape fraction for ionizing photons. Build it: without it all the Hα sits in
discrete knots and real galaxies have a glow between them.

**Shocks come free.** [S II]/Hα separates shock excitation from photoionization
once both lines exist. No new field, one diagnostic.

**The existing `halpha_surface_brightness` and `HALPHA_PER_SFR`** (D166) become
the check: the Q-derived Hα integrated over the galaxy against Σ_SFR × the
constant. Note in the row's own text that **Hα-versus-SFR is a consistency
check, not independent validation** — the SFR is upstream of it. Labelling that
honestly stops it reading as free confirmation.

**New acceptance rows.** Integrated Hα luminosity of the Milky Way `[recall —
NEEDS SOURCING]`, the HII region luminosity function's slope `[recall — NEEDS
SOURCING: Kennicutt, Edgar & Hodge 1989]`, and the planetary nebula luminosity
function's cutoff from Phase 4.

**Fable**: three sourcing decisions, one dependency ruling, and a volumetric
contract that is expensive to retrofit.

---

## Phase 10 — mechanical feedback (S36)

Depends on Phase 3 (wind luminosity) and Phase 8 (ambient density).

Radiation does not evacuate a cavity; winds and supernovae do. Without this,
nebulae render filled, and hollow is most of what makes them read as real.

Bubble radius from mechanical luminosity, ambient density and age, by the
standard wind-bubble solution `[recall — NEEDS SOURCING: Weaver et al. 1977]`,
plus the shell density enhancement.

**Per star as well as per cluster.** A single O star blows a bubble; this is not
only a cluster-scale mechanism. Drive it from the massive end of the catalogue.

**Supernova remnants are the late state of the same object**, so they belong
here rather than in a stage of their own — the Sedov phase `[recall — NEEDS
SOURCING]` after the wind phase — and their [O III]-bright shells against
Hα-bright HII regions are exactly the excitation contrast that makes a wide
field read correctly. Their count follows from Phase 6's rates.

Scaled up, the same mechanism gives superbubbles and the hot phase, which
connects to the supernova rates in Phase 6.

**Opus.**

---

## Phase 11 — clusters as objects (S33, before Phase 5)

Depends on Phase 8.

Clusters are an object class, not a label on stars: a mass function
(dN/dM ∝ M⁻² `[recall — NEEDS SOURCING: Portegies Zwart, McKee & Gieles 2010]`),
a mass–radius relation, and a bound fraction, since most clusters dissolve
within ~10 Myr `[recall — NEEDS SOURCING: Lada & Lada 2003]`. Drawn per cell as
clouds and stars are; each cloud's `cluster_id` points at one; a cluster's
`Q_ionizing` and `wind_luminosity` are the sums over its members' Phase 3
columns.

**This unifies with Phase 5.** Globular clusters are the surviving massive end
of the same distribution integrated over the history. Build one mechanism and
the η relation becomes a *check* on it rather than a second independent
assertion — which is a stronger result than either phase gives alone.

**Opus.**

---

## Audit III (S37)

Not in the owner's plan; added by the reconciliation because it is what this
project does after a build (S10, S21) and because rule B3 says the phases'
own gates are checks on the phases. Once, on Fable, with a stated aim: **every
NEEDS-SOURCING that entered code has its citation read** (S21 (a)'s A-14 found
a "cited 35" that was an adopted value with the measurement at 39 ± 4), every
redistribution assertion re-derived by hand, the energy balance and the
catalogue-against-field tests run at a mesh the build did not use, and every
new row's green conditioned (AUDIT_RUN2 §5). Debts and decisions sequential.

---

## V1–V4 — the renderer side (S38–S41)

Ruled in after the model side (D172). Each row replaces one invented structure
with a published one (RENDER_PHYSICS §0, §8), and each has a gate that is a
number.

**V1 — the spectrum function and the filter sets (S38, Opus).** Rule §0's open
question: where the filter integral runs. Broadband RGB, SHO/HOO, one named
instrument's filter set with its PSF. The young-light share of the field regime
(30% at 12 000 K, a display constant) is replaced by the stellar component at
the population's own temperature mix per cell. *Gate:* the integrated B − V and
M_V of the rendered whole-galaxy image, read back from the frame, equal Phase
3's published scalars to the tone map's stated tolerance.

**V2 — volumetric emissivity and emitting dust in the field regime (S39,
Opus).** The ray-marcher integrates Phase 9's galaxy-scale line components and
Phase 7's scattered and thermal dust; the clump lattice and the Hα knots go.
*Gate:* energy balance holds in the frame (absorbed equals re-emitted over the
image), and the surface-brightness profile read from the face-on frame is the
published Σ_V(R) to a stated tolerance (RENDER_PLAN Part 3's check 2).

**V3 — region synthesis from the cloud vector (S40, Fable).** The stars regime
below 4 kpc becomes a region regime: the cell hierarchy asked for at the level
the view needs, the cloud interiors synthesised from the log-normal PDF at the
published Mach number, pillars from `ionizing_source_offset`, shells from Phase
10, all seeded by the cloud's cell-and-index path. *Gate:* RENDER_PHYSICS §7's
catalogue-against-field test — the region's light integrated over a patch
matches the field's — and determinism across zoom levels, a nebula the same at
every approach.

**V4 — clusters, instruments, close-out (S41, Opus).** Cluster objects drawn as
objects (Phase 11), the named-instrument modes' PSFs, the model toggle for
`azimuthal` against `basic`, the tag batch attempted again from the desktop
(D161), RESUMING/BRIEF for the maintainer. *Gate:* every published field of
both models shown or ruled invisible in its declaration (#69's rule),
`verify_clone` OK.

---

## Scope boundary — recorded as a decision

Two classes of image are **out of scope**, ruled so deliberately. They are
written here so they read as decisions rather than oversights.

**Interacting and merging systems.** `mergers[]` is a history of completed
events, not a second body present in the frame. Tidal tails, bridges, a shared
non-axisymmetric potential and merger-triggered starbursts are not expressible,
and the SFH is smooth and R-dependent by construction — a burst is a different
regime, not a larger number. The model generates one galaxy.

**Environment.** No intracluster medium, no cluster membership, no cooling-flow
filaments, no active nucleus. These are properties of *where a galaxy lives*
rather than of the galaxy, and the model has a dark matter halo and nothing
outside it. The M_• work stops at the mass; it does not become an AGN.

Background galaxies and foreground stars drawn into a rendered field are
viewer-side decoration. Fine to have, carry no physics, and must not be
described as if they do.

---

## Sequence

| S | Phase | Deliverable | Blocked by | Model |
|---|---|---|---|---|
| **25** | 0 + 1 | A1 rewritten; #26 and #3 re-ruled; pattern ahead of `sfh`; rows 15–17 measured before and after; the arm-number finding recorded | nothing | Fable |
| **26** | 1b | Arm and bar amplitudes derived or seeded, the two inputs removed; the arm number derived or its draw re-ruled; #23 re-ruled | 25 | Fable |
| **27** | 2 | `sfh_azimuthal`; the `azimuthal` model declared from `BASIC`'s tuple; the redistribution asserted | 26 | Opus |
| **28** | 3 | Band tables; rows 25–28 (M_B, M_V, B − V, Υ_V); Q(H⁰) ruled and published; wind luminosity; WR proxy; the sweep instrument for Tully–Fisher | nothing | Opus |
| **29** | 4 | Remnants; planetary nebulae | 28 | Opus |
| **30** | 6 | SN rates with two sourced rows; the habitable zone, unjudged | nothing | Opus |
| **31** | 7 | Scattering, thermal emission, PAH; the energy-balance test | nothing (#79 done) | Opus |
| **32** | 8 | Cloud catalogue as an object class; the cell hierarchy | 31 | Fable |
| **33** | 11 | Clusters as objects | 32 | Opus |
| **34** | 5 | Globular clusters as the check on 11; the stellar halo | 33 | Opus |
| **35** | 9 | Nebular lines, DIG, shocks, volumetric at region scale; rows for Hα, the HII LF, the PNLF | 28, 32 | Fable |
| **36** | 10 | Wind bubbles, shells, SNRs, per star and per cluster | 28, 32 | Opus |
| **37** | — | Audit III: every entered citation read, every assertion re-derived | 25–36 | Fable |
| **38** | V1 | Spectrum function and filter sets; the young-light constant replaced | 28, 37 | Opus |
| **39** | V2 | Volumetric emissivity and emitting dust in the field regime; clumps and knots removed | 31, 35 | Opus |
| **40** | V3 | Region synthesis from the cloud vector at the hierarchy's levels | 32, 35, 36 | Fable |
| **41** | V4 | Cluster objects, instrument PSFs, the model toggle, the tag batch, close-out | 33, 34 | Opus |

25 → 26 → 27 is the only hard chain on the model side. 28 is the highest value
and can start in parallel — and it is the prerequisite for 29, 35 and 36, so it
is the phase to staff first when two subagents run at once.

31 → 32 → {33, 35, 36} is the second chain, and it is the one the rendering work
depends on. 30 is independent and safe to delegate beside anything. 34 is
independent but is done after 33, so the globular cluster relation lands as a
check on the cluster mass function rather than as a separate assertion.

---

## Rulings needed before starting

1. **Q(H⁰): blackbody integral or a tabulated T_eff calibration?** (Phase 3,
   blocking for 9 and 10) — everything nebular depends on Q, and the youngest
   isochrone tops out at 64 M☉.
2. **Debts #26 and #3: re-rule under the new A1.** (Phase 0, blocking)
3. **Debt #23: re-rule once the amplitude is derived or seeded.** (Phase 1b)
4. **Nebular emissivities: tabulated photoionization grid or analytic fits?**
   (Phase 9, blocking) — the isochrone ruling's twin.
5. **Where the filter integral runs.** (V1, RENDER_PHYSICS §0)

Settled by the owner on 2026-09-26 (D172): the model's name is `azimuthal`; the
amplitudes are derived or seeded before Phase 2; the viewer sessions follow the
model side; sessions are numbered from S25 with S23–S24 recorded retrospectively.

## What not to do

**Do not add φ to the history fields.** 288 million cells, and azimuthal mixing
makes it physically wrong as well as unaffordable.

**Do not retune `disc_dominance` if row 15 leaves its window in Phase 1.** Record
the miss (B5).

**Do not give the habitable zone an acceptance target.**

**Do not reinstate satellite galaxies.** They are cut, and Phase 5 records why.
The subhalo mass function is not a satellite count.

**Do not implement the globular cluster relation from recall.** η and its
scatter are sourced in Phase 5; use those values and cite them, and take the
observed system mass from the Harris catalogue rather than from a figure in
circulation.

**Do not put the shared derivations inside `azimuthal` only.** They are
derivations, not contested physics; they go into `basic`, and `azimuthal`
inherits them through the tuple it is built from.

**Do not publish emission as colours, or as a surface quantity at region
scale.** `RENDER_PHYSICS.md` §2 and §4 say why. Both are cheap to get right
first and expensive to retrofit.

**Do not publish a spectrum per cell.** It is the 288-million-cell mistake in a
new costume. Publish the parameters that determine the spectrum and ship the
spectrum function as model-side code (`RENDER_PHYSICS.md` §3a, §0).

**Do not let the renderer invent structure.** Every visible feature must trace
to a published field or a seeded draw from one, with the seed coming from the
model rather than the frame. The present clump lattice is the dated exception
and is removed by V2/V3; nothing new of its kind is added.

**Do not build interacting systems or environment.** Ruled out of scope above.
The tempting half-measure — a second galaxy drawn in as decoration — is fine as
decoration and must never be described as a modelled companion.

**Do not reserve number blocks.** Sessions are sequential; take the next number
when the entry is written.
