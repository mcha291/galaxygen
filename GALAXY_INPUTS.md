# Galaxy generator — fundamental input investigation

Method: rules A3 and A4 from `RULES.md`. A3 — *if it can be derived, derive it;
a control earns its place only if nothing more fundamental determines it, and
"derived" means determined, not correlated.* A4 — *never invent a variable to
justify a stage; judged individually, would this input exist if no stage needed
filling?*

Every claim tagged. `[verified]` carries a citation from the session that wrote
this file. `[recall]` is memory. `[inferred]` is design reasoning.

---

## 1. The headline result

**The simple model needs 8 physical inputs, 2 seeds, and one variable-length
event list**, against a ceiling of 12. `[inferred]`

A galaxy has *fewer* fundamental inputs than a planet, and the reason is
structural rather than lucky: ΛCDM constrains a disc galaxy more tightly than
planet formation constrains a planet. There is no galactic equivalent of
obliquity, rotation rate, atmospheric composition or water inventory — the
things a planet-scale model needs most of its inputs for. Orientation is
arbitrary and affects
no internal physics; ISM composition is an *output* of chemical evolution rather
than an input to it. `[inferred]`

Ceiling: **12** (ruling 6), leaving five slots of headroom before the advanced
model has to be raided. The ceiling matters more than the count: a simple model
stays small only *because* an advanced model exists on paper to absorb
everything else. `[inferred]`

---

## 1b. Three categories

Moved to `RULES.md` A10, where every session can reach it without reading this
document.

---

## 2. Level 0 — constants, not inputs

These are physical constants that happen to be uncertain. They are recorded as
calibration debt, never exposed as controls. Rule 4 disqualifies each: they
would exist whether or not this model did, and none is a property of *this*
galaxy.

| Constant | Status |
|---|---|
| H₀, Ω_M, Ω_Λ | Cosmology. BHG16 use h=0.7, Ω_M=0.3, Ω_Λ=0.7 `[verified: BHG16 §1]` |
| Cosmic baryon fraction | Ω_b/Ω_M |
| IMF | Kroupa/Chabrier. MW bulge dynamics **rules out Salpeter** at 10 Gyr — it predicts more mass than is dynamically allowed `[verified: BHG16 §4.2.4]` |
| Nucleosynthetic yields | Per-element tables |
| SNIa delay-time distribution | Simple model uses instantaneous recycling; DTD is an advanced-model axis |
| Stellar lifetimes / isochrones | |
| Kennicutt–Schmidt index and normalisation | |
| Outflow mass-loading coefficient | The *loading* is derived per radius from local escape velocity; only the coefficient is constant `[inferred]` |

Making the IMF an input is the most tempting rule-4 violation, because a
variable IMF is a live hypothesis. It stays a constant in the simple model, and
becomes an input only in the advanced model. `[inferred]`

---

## 3. Level 1 — the eight

| # | Input | MW default | Provenance |
|---|---|---|---|
| 1 | `halo_mass` M₂₀₀ | 1.1 × 10¹² M☉ | Literature spans 0.89–1.3 × 10¹² `[verified: Karukes+19 0.89⁺⁰·¹⁰₋₀.₀₈; McMillan 1.3 ± 0.3]` |
| 2 | `disc_spin` λ_d | **0.0144** — RULED (8) | The **disc** spin parameter, not the halo's. See §6 |
| 3 | `halo_assembly_z` | z ≈ 2–3 | RULED (7): renamed; `galaxy_age` cut. Also derives c₂₀₀ (5) |
| 3b | `baryon_retention` | ~0.35 | RULED (9). f_b × this = m_d ≈ 0.055 |
| 4 | `infall_timescale` τ₀ | ~7 Gyr at R₀ | Two-infall framework `[verified: Chiappini+97 via Molero+23]` |
| 5 | `inside_out_index` n | τ(R) = τ₀(R/R_d)ⁿ | Sets the metallicity gradient `[inferred]` |
| 6 | `second_infall_onset` | ~8 Gyr ago | Produces the thin/thick chemical split `[recall]` |
| 7 | `migration_efficiency` | — | RULED IN (ruling 4). Dispersion kernel, §8 |
| ~~8~~ | ~~`bh_seed_mass`~~ | — | **CUT** by ruling 2 — derived, miss recorded |
| ? | ~~`galaxy_age`~~ | 13.6 Gyr | **New rule-3 candidate — see below** |
| — | `world_seed` | | |
| — | `systems_seed` | | Own seed, own workflow step |
| — | `mergers[]` | 4 scalars per event | Exempt from ceiling, as `impacts` is |

**Count after rulings: 7 physical inputs, 2 seeds, one event list** — if
`galaxy_age` also goes.

**M_• (ruling 2).** Derived from M–σ. The MW falls **below** the relation for
ellipticals and classical bulges by a factor of 5–6 `[verified: BHG16 §3.4]`, so
this is a deliberate failed acceptance check, entered as debt #2 rather than
relaxed (rule B5). Acceptance entry 18 is
expected to miss by ~0.75 dex and must not be quietly re-scoped to a range that
includes the miss.

**`galaxy_age` — a rule-3 candidate found while applying the rulings.** If the
galaxy is observed at z = 0, then age = t(z=0) − t(z_form), fully determined by
input #3 plus cosmological constants. It is only a free input if the generator
must present a galaxy at some *other* epoch, which nothing currently requires.
Recommend cutting it: 7 physical inputs. `[inferred]`

---

## 4. What gets derived — the rule-3 audit

Each of these was a candidate input and each was cut. This table is the
justification for the count being 8 rather than 25.

| Derived quantity | From | Note |
|---|---|---|
| **Disc scale length R_d** | λ and R_vir: R_d = (λ/√2)·R_vir `[verified: MMW98 via GECO]` | The single largest cut — see §6 |
| Virial radius R₂₀₀ | M₂₀₀ + cosmology | |
| **Halo concentration c₂₀₀** | M₂₀₀ + formation epoch | Concentration encodes formation history `[verified: Callingham+18 §4.2]`; BHG16 Fig. 1 plots c against M_vir per cosmic epoch `[verified: BHG16 §1]` |
| Rotation curve V(R) | Halo profile + baryons | |
| Disc-to-halo mass fraction m_d | M₂₀₀ via abundance matching | MMW98 assume a constant m_d = 0.05 `[verified: Boissier & Prantzos]`; deriving it is more fundamental but carries a calibration debt |
| Scale height h_z(R, age) | σ_z + surface density, hydrostatic | |
| Velocity dispersion σ(age) | Disc heating law | |
| Gas surface density Σ_gas(R,t) | Infall − SF + recycling | |
| SFR(R,t) | Kennicutt–Schmidt from Σ_gas | |
| Metallicity gradient | Inside-out formation + yields | |
| **Bar pattern speed Ω_b** | Bar length, via fast-bar R = R_CR/R_bar = 1.2 ± 0.2 `[verified: BHG16 §4.4]` | Derivation inherits a wide error — BHG16's own value is Ω_b = 43 ± 9 km/s/kpc, R_CR = 4.5–7 kpc `[verified: BHG16 §4.4]` |
| **Pitch angle** | Rotation-curve shear S = ½(1 − (R/V)dV/dR) `[verified: Seigar via Corbelli M33]` | **Conflicted — see §5** |
| Arm multiplicity | Swing amplification (disc/halo mass ratio) | `[recall]` |
| Bulge mass | Mergers + bar buckling | MW bulge is mostly secular; models need ≤8% initial classical bulge, and none was required `[verified: Shen+10 via BHG16 §4.2.3]` |
| Dust extinction | Gas × metallicity | |
| SN rate | SFR × IMF | |
| Habitable zone | Metallicity + SN rate | Falls out; never drawn by hand `[inferred]` |

## 4b. Determinacy audit

Rule 3 asks whether something more fundamental *determines* a quantity. This
audit asks the sharper question: **is it determined, or merely correlated?** A
relation with real galaxy-to-galaxy scatter, shipped as if exact, is a bug — the
model claims a precision it does not have and the acceptance check silently
becomes a check on the fit rather than the physics.

Three verdicts:

- **A — arithmetic.** A definition or a solved equation. No freedom.
- **B — closed by physics.** A law with no per-galaxy freedom; residual is a
  calibration debt, not a variable.
- **C — correlated with scatter.** Two galaxies with identical inputs could
  credibly differ. Needs a remedy.

| Quantity | Verdict | Note |
|---|---|---|
| Virial radius R₂₀₀ | **A** | R₂₀₀ = (3M₂₀₀/800πρ_crit)^⅓. A *definition*, not a relation |
| Scale height h_z | **A** | h_z = σ_z²/πGΣ, hydrostatic. Fully pinned once σ is right |
| SN rate | **A** | SFR × IMF |
| Habitable zone | **A** | Arithmetic given its own definition |
| Σ_gas, SFR, Z(R,t) | **A/B** | The integration itself; K-S constants are Level 0 |
| Rotation curve V(R) | **B** | Solved Poisson given components. Adiabatic contraction is a debt: cooling raises halo concentration, feedback reverses it `[verified: Kafle+14 §discussion]` |
| Dust | **B** | Dust-to-gas tracks metallicity tightly |
| **Disc scale length R_d** | **C — severe** | See below |
| **Baryon budget m_d** | **C — severe** | See below |
| Halo concentration c₂₀₀ | **C** | Epoch absorbs most scatter, not all. MW measurements themselves span c ≈ 10–18 `[verified: Huang+16 c=18.06⁺¹·²⁶₋₀.₉₀ vs ΛCDM-relation values ~10]` |
| σ(age) heating law | **C** | Heating from GMCs, arms, bars, bombardment. Partly derivable from the merger list; residual is real |
| Bar pattern speed | **C** | Two weak links in series: disc dominance → bar length → Ω_b. Fast-bar ratio itself is 1.2 ± 0.2, i.e. ±17% *observed scatter* `[verified: BHG16 §4.4]` |
| Arm multiplicity | **C** | Swing amplification sets a preferred m; real galaxies at similar X differ |
| Bulge mass | **C** | Inherits bar-strength scatter |
| **M_•** | **C — reopens ruling 2** | See below |

### The remedy is two-valued, not one

Strictly applied, "if it can credibly differ it should be an input" balloons the
count past the ceiling — six C-verdicts above. The distinction that keeps the
model honest without doing that:

- **Input** when the residual is *legible* — someone would want to set it, and it
  means something. "How compact is this galaxy for its mass" is legible.
- **Seeded draw** when the residual is real but nobody would ever choose it. The
  arm-multiplicity residual is not a decision.

Both are honest: neither pretends the relation is exact. Seeded draws do not
break rule 2 (nothing per-cell is an input) and do not count against the ceiling.
What they cost is that the affected acceptance checks become **statistical rather
than pointwise** — the model must reproduce the MW's bar pattern speed *within
the ensemble*, not exactly. That cost must be entered explicitly against
acceptance entries 14, 16, 17 and 13. `[inferred]`

**Assigned seeded draws:** c₂₀₀ residual, σ(age) residual, bar pattern speed,
arm multiplicity, bulge mass residual, **M_• residual** (ruling 10). **No new
inputs from these.**

### R_d — the derivation is circular

Ruling 1 set λ ≈ 0.015 by inverting R_d = (λ/√2)·R_vir to hit the measured 2.6
kpc. λ has no independent measurement for the MW. So `spin` does not derive the
scale length; **it is the scale length wearing a physical name.**

The escape would be a second input, the angular-momentum retention j_d/m_d —
MMW98's j_d ≃ m_d is explicitly an *assumption* `[verified: GECO §2]`, and fits
to real galaxies require λ_d and m_d to move together `[verified: Burkert+10
abstract]`, so retention credibly differs between galaxies. But only the
**product** λ·(j_d/m_d) enters R_d, and nothing else in the simple model reads
them separately. Rule 4 therefore forbids splitting them: the second input would
buy nothing measurable.

**Ruling needed.** Either rename the input to what it is, or keep the name and
put the circularity on its `about` line where it cannot be forgotten `[verified:
rules A8, A9]`. Recommend renaming — a duplicate that
wins is a bug wearing the right name.

### Baryon budget — a genuine missing input

**Structural error in the previous table.** m_d was listed as derived from
abundance matching. But the disc mass is the *integral of the accretion history*,
and the inputs currently specify only the infall **timescale** (τ₀) and its
radial index (n) — no normalisation. **Nothing in the current input set fixes the
total baryon budget.**

Total baryons available is cosmological: f_b · M₂₀₀. The fraction actually
retained is set by feedback and credibly varies — observed disc fractions span
f_disk ≈ 0.01–0.07 against a cosmic f_bar `[verified: Burkert+10 §abstract]`, a
factor of seven.

**Add input: `baryon_retention`.** Highly legible (it is "how much of its gas did
this galaxy keep"), directly sets total stellar mass, and abundance matching
becomes an *acceptance check* rather than a derivation — which is where it
belonged. `[inferred]`

### M_• — the new criterion reopens ruling 2

Ruling 2 derived M_• from M–σ and recorded the 5–6× MW miss as debt. Under the
determinacy criterion that ruling does not survive on its own terms: M–σ carries
intrinsic scatter, and the MW sits ~0.75 dex off it `[verified: BHG16 §3.4]`. A
relation that misses its only calibration target by most of an order of magnitude
is not determining anything.

Options: (a) uphold ruling 2 and accept the acceptance check is decorative;
(b) seeded draw about the relation, making entry 18 statistical; (c) restore it
as an input. **Flagged for re-ruling, not silently kept.**

### A cut found while auditing

`second_infall_onset` (input #6) may be redundant. If the second gas infall is
delivered *by* a merger, its onset is the timestamp of an event already in the
`mergers[]` list, and the input duplicates data the model already has. Requires
ruling on whether every second infall is merger-delivered. `[inferred]`

### Net effect on the count

| Change | Δ |
|---|---|
| `baryon_retention` added (genuinely missing) | +1 |
| `second_infall_onset` possibly cut | −1 (pending) |
| Six C-verdicts resolved as seeded draws | 0 |
| M_• re-ruling | 0 or +1 |

**7 inputs, unchanged** — but the composition is different and one of the seven
was doing no work. Ceiling of 12 still has headroom.

### What the two rulesets actually claim

`PITCH_SEIGAR`. Pitch angle P is a tight deterministic function of rotation-curve
shear, S = A/ω = ½(1 − (R/V)·dV/dR) `[verified: Seigar via Corbelli M33 eq. 11]`,
reported at r = 0.89, significance 99.75%, over 48 galaxies `[verified: Seigar+06
§4]`. High shear means a large central mass concentration and more tightly wound
arms `[verified: Seigar+06 §4]`. Under this ruleset pitch is **fully derived**:
no input, no scatter, and arm winding is a strict consequence of the mass
distribution the model already computed.

`PITCH_YU`. About a third of Seigar's pitch measurements were severely
overestimated, and once corrected the correlation is much weaker `[verified: Yu
& Ho 2019 §4.3.5]`. Under this ruleset pitch is **not derivable**. It needs
either a new input or a seeded draw around a weak trend.

### They are not rival relations — they are rival error bars

Worth being precise, because this changes what the ruling is about. Yu does not
claim the sign is wrong or that no relation exists. And the shear–pitch
mechanism has support independent of both observational datasets:

- Swing amplification theory predicts it analytically `[verified: Grand+13 intro,
  citing Goldreich & Lynden-Bell 1965, Toomre 1981, Julian & Toomre 1966]`.
- N-body simulations reproduce it, with pitch-angle range narrowing as shear
  rises, and **scatter comparable to the observed relation** `[verified: Grand+13
  abstract/conclusions]`.

So the functional form is theoretically motivated and independently reproduced;
what is disputed is how tight it is. The ruling is therefore not "which relation
is true" but **how much seeded dispersion sits on top of a form both sides
accept** — a calibration question with a recorded debt, not a fork. `[inferred]`

### The larger problem neither ruleset solves

The correlation holds only when shear is measured **at a fixed physical radius**
— 10 kpc — chosen independently of the galaxy `[verified: Seigar+06 fig. 3
discussion, which calls the choice "somewhat arbitrary"]`. Later work uses
2.2 R_d instead `[verified: TNG50 MW/M31 analogue study]`.

For a generator this is worse than the tightness dispute. A relation calibrated
at an absolute radius is not scale-free, and the generator will produce galaxies
across a wide size range: 10 kpc sits in the far outer disc of a compact galaxy
and barely past 1.5 scale lengths in an extended one. Applying an
absolute-radius closure across that range means running it outside its
calibration regime for most rolls. **`R_CLOSURE_ABSOLUTE` (10 kpc) vs
`R_CLOSURE_SCALED` (2.2 R_d) is the more consequential fork** and should be
ruled on alongside. `[inferred]`

### And a degeneracy check the model should run before trusting either

Shear is bounded in a way pitch is not. Writing α = d ln V / d ln R, S = ½(1 − α),
so a flat rotation curve gives S = 0.5 exactly, and real discs sit near it — M33
measures S = 0.46 `[verified: Corbelli M33 §4]`, the MW's curve is gently falling
from ~220 km/s at the solar radius `[verified: Xue+08 abstract]`, putting it just
above 0.5. Observed pitch angles meanwhile span roughly 5° to M33's 42.2°
`[verified: Corbelli M33 §4]`.

A narrow input range mapping to a wide output range means the closure is steep,
and a steep closure is a sensitive one: small errors in a model-computed S become
large errors in P. Before adopting any ruleset, measure the actual spread of S
across a generated population. If it clusters at 0.5 — which is what flat
rotation curves imply — then every generated galaxy gets near-identical arm
winding and the derivation has bought nothing. **Do not sample what you can
count** (rule B8): this is countable over a batch
of rolls, cheaply, before any ruling is needed.

### Recommendation

Adopt the shear form, set dispersion from Yu rather than Seigar, run the S-spread
check first, and rule `R_CLOSURE_*` explicitly. Pitch is high-visibility and
low-consequence — it sets where star formation concentrates and therefore what
the galaxy looks like, but nothing downstream depends on it the way habitability
depends on metallicity. It does not merit paying for a first-principles
derivation. `[inferred]`

### RULED (ruling 3): `PITCH_YU`

Implementation: mean pitch from the shear trend, dispersion from `world_seed`.
Because the trend is weak, the draw dominates and pitch is effectively seeded
rather than derived. **This costs no input** — seeded draws do not count against
the ceiling — but it does mean arm winding is no longer a consequence of the
mass distribution, and any downstream field that reads it inherits a random
component. Flag on `pitch_angle`'s `about` line accordingly `[verified:
rule A8]`.

**Two questions this ruling dissolves.** With a weak trend, the radius at which
shear is evaluated barely affects the output, so `R_CLOSURE_ABSOLUTE` vs
`R_CLOSURE_SCALED` stops being consequential — take the scaled form and move on.
The S-spread check likewise stops being a gate; run it once to record how much
pitch variance is trend versus draw, then leave it. `[inferred]`

This is also a live instance of the recorded lesson that **a relation which fits
the validation table can still be the wrong relation** `[verified:
rule B11]`.

---

## 6. The first calibration debt, found while writing this

The MMW98 relation makes λ *measurable* from the disc scale length rather than
free. Running it forward with the population-mean spin:

- λ̄ = 0.045 `[verified: Muñoz-Cuartas+11]`
- R_vir ≈ 255 kpc for M_vir ≈ 0.9 × 10¹² `[verified: Huang+16 §6.2.1]`
- R_d = (0.045/√2) × 255 ≈ **8.1 kpc**

The measured MW thin-disc scale length is **R_t = 2.6 ± 0.5 kpc** `[verified:
BHG16 §5.1.2]`. The prediction is off by a factor of ~3.

Inverting, the MW's implied spin is λ ≈ 0.015 — about 1.9σ low on the
log-normal. `[inferred]`

This matters because it directly threatens rule 5. **Defaulting λ to the
cosmological mean would not generate the Milky Way**; it would generate a galaxy
three times too spread out.

### RULING 8 resolves this: it was the wrong parameter, not the wrong galaxy

`spin` was λ, the **halo** spin parameter. What R_d actually depends on is

    R_d = (1/√2) · (j_d/m_d) · λ · R_vir      `[verified: MMW98 via GECO §2]`

where j_d/m_d is the **angular momentum retention fraction** — how much of the
halo's specific angular momentum the disc kept. MMW98 set it to 1 by assumption
`[verified: GECO §2]`. The combination that the disc actually has is standardly
written **λ_d**, the *disc* spin parameter `[verified: Burkert+10; Cervantes-Sodi
§2]`.

Inverting for the MW: **λ_d = R_d·√2/R_vir = 2.6 × 1.414 / 255 = 0.0144.**

Burkert et al. fit observed discs and find that reproducing them requires
**λ_d = 0.01–0.03 for m_d ≈ 0.05** `[verified: Burkert+10 abstract]`. The MW's
m_d ≈ 0.055 and its λ_d = 0.0144 sit squarely inside that range.

**The Milky Way is not a 1.9σ outlier. It is typical.** The factor of three was a
parameter confusion — quoting a halo-spin distribution for a disc-spin quantity.
The retention fraction it implies is j_d/m_d ≈ 0.32, i.e. the disc kept about a
third of the halo's specific angular momentum, which is the well-known angular
momentum loss during collapse rather than an anomaly. `[inferred from verified
values]`

**RULED (8): `disc_spin`, λ_d, default 0.0144.**

`about` line, to live in the stage that computes it: *Disc spin parameter. The
specific angular momentum of the disc in units of the halo's, i.e. the halo spin
λ times the retention fraction j_d/m_d. Not the halo spin parameter — halo λ
averages 0.044 and disc λ_d is several times smaller, because discs lose angular
momentum during collapse. Inferred from observed disc structure rather than
measured directly, which is the standard method.*

### And ruling 9 breaks what remained of the circularity

Debt #7 said λ was a fit to R_d wearing a physical name. With `baryon_retention`
added, m_d is no longer assumed — it is **pinned by the total stellar mass**
(acceptance entry 1), and R_d then pins λ_d given m_d. Two parameters, two
independent observables. That is a joint fit, not an inversion.

### Superseded (ruling 1)

**Superseded by ruling 8.** The gap
between that and the population mean is debt #1, published rather than tuned
away. One consequence survives the supersession and is not optional: **the prior must
be the λ_d distribution, not the halo λ distribution.** Rolling a random galaxy
from a log-normal centred on 0.044 would make every generated galaxy three times
too extended. Default and prior must be drawn from the same population.
`[inferred]`

Three explanations, none yet tested `[inferred]`:

1. **Definitional.** R_vir vs R₂₀₀, and M_vir vs M₂₀₀, differ by ~17–32%
   `[verified: Patel+16 abstract]` — real, but nowhere near a factor of 3.
2. **Angular momentum loss.** MMW98 assume j_d ≃ m_d, i.e. the disc keeps the
   halo's specific angular momentum. It's an assumption, not a result
   `[verified: GECO §2]`, and fits to real galaxies need λ_d and m_d to move
   together `[verified: Burkert+10 abstract]`.
3. **The MW really is a low-spin, compact galaxy.** BHG16 note its scalelength
   is small for its luminosity, against 4 ± 2 kpc for comparable disc masses
   `[verified: BHG16 §5.1.2]`.

State it as a prediction that could fail, then check it — the habit that has
paid most often in this project (rule B4).

---

## 7. The acceptance table — 24 quantities

Lives in `spec.py`, never in prose read at runtime (rule C6). All values `[verified: BHG16]` unless noted.

| # | Quantity | Value |
|---|---|---|
| 1 | Total stellar mass | 5 ± 1 × 10¹⁰ M☉ |
| 2 | Star formation rate | 1.65 ± 0.19 M☉/yr |
| 3 | Solar tangential velocity | 248 ± 3 km/s |
| 4 | Thin disc scale length | 2.6 ± 0.5 kpc |
| 5 | Thick disc scale length | 2.0 ± 0.2 kpc |
| 6 | Thin disc scale height | 300 ± 50 pc |
| 7 | Thick disc scale height | 900 ± 180 pc |
| 8 | Thick/thin local density ratio | 4% ± 2% |
| 9 | Thick/thin surface density ratio | 12% ± 4% |
| 10 | Thin disc stellar mass | 3.5 ± 1 × 10¹⁰ M☉ |
| 11 | Thick disc stellar mass | 6 ± 3 × 10⁹ M☉ |
| 12 | Bulge stellar mass | 1.4–1.7 × 10¹⁰ M☉ |
| 13 | Bulge/total stellar fraction | 0.30 ± 0.06 |
| 14 | Bulge velocity dispersion (rms) | 113 km/s |
| 15 | Bar half-length | 5.0 ± 0.2 kpc |
| 16 | Bar pattern speed | 43 ± 9 km/s/kpc |
| 17 | Bar corotation radius | 4.5–7.0 kpc |
| 18 | Black hole mass | 4.2 ± 0.2 × 10⁶ M☉ |
| 19 | Halo virial mass | 1.0–1.3 × 10¹² M☉ `[verified: McMillan]` |
| 20 | Total gas mass (<30 kpc) | 8.0 × 10⁹ M☉ `[verified: Nakanishi & Sofue 15]` |
| 21 | Gas HI:H₂ split | 89% : 11% `[verified: Nakanishi & Sofue 15]` |
| 22 | Present-day metallicity gradient | −0.06 dex/kpc `[verified: Trentin+24 −0.064 ± 0.003; Feuillet+19 −0.059 ± 0.010]` |
| 23 | Gradient evolution with age | −0.07 (young) → −0.04 (>10 Gyr) `[verified: Willett+23]` |
| 24 | [α/Fe] bimodality | Thick disc α-enhanced across a wide [Fe/H] range `[verified: BHG16 §5.2.2]` |

### Why this table is weaker than Earth's

Three degradations, all structural rather than fixable:

**It is not internally consistent.** BHG16 state outright that summary values
cannot yet all be made consistent within a single plausible dynamical
description of the Galaxy `[verified: BHG16 §1]`. Earth's 23 do not have this
problem. A model that fits all 24 exactly would be fitting a contradiction.

**Several entries have factor-of-two-to-three literature spreads.** Disc
scalelength estimates across 130 refereed papers run from 1.8 to 6.0 kpc
`[verified: BHG16 §5.1.2]`; thick disc scalelength across 12 papers runs 1.8 to
4.9 kpc `[verified: BHG16 §5.2.2]`; the metallicity gradient runs −0.01 to −0.09
depending on tracer `[verified: Lemasle IAU]`. An acceptance check against a
number with a 3× spread is barely a check.

**Substructure defeats the fitted forms.** Juríc et al. found substructure so
prevalent that a smooth double-exponential cannot be fitted to either disc
without accounting for it `[verified: BHG16 §5.1.2 "Disk substructure"]`. The
model publishes smooth exponential fields; the target is not smooth.

Consequence: **§12-style calibration debt is the primary deliverable of the
first sessions, not a footnote.** `[inferred]`

---

## 8. Advanced model — ~17 additional, by axis

| Axis | Inputs | Count |
|---|---|---|
| Chemistry dimensionality | SNIa DTD index, minimum delay, normalisation; per-element yield scaling | 3–4 |
| Radial migration | Churning efficiency; blurring/heating rate | 2 |
| Outflows | Loading normalisation; loading slope vs escape velocity | 2 |
| Gas dynamics | Radial inflow velocity; fountain recycling timescale | 2 |
| Bar evolution | Pattern speed decay (dynamical friction) | 1 |
| Transient spirals | Recurrence rate; amplitude | 2 |
| Assembly | Merger tree mass resolution; satellite SMHM normalisation | 2 |
| Accretion chemistry | Pre-enrichment of infalling gas | 1 |
| IMF | Variability with metallicity or SFR density | 1–2 |

**Total ≈ 25 for the advanced model**, a ~3× expansion on the simple model's
seven. `[inferred]`

### One item that should cross downward

Radial migration. Without it, metallicity is a pure function of birth radius and
birth time, and the local metallicity distribution comes out far too narrow
`[recall]`. That is a *qualitative* error, not an accuracy loss, and it lands on
gameplay-facing output if planet occurrence is conditioned on metallicity.
Migration is also directly evidenced: metallicity–age relations vary spatially
in a way that implies non-negligible migration in the disc plane `[verified:
Feuillet+19 §3]`.

Cheap form: a **dispersion kernel** whose width grows with stellar age, applied
by convolution over birth radius. One input, no iteration. Structurally the same
move as putting a physical smoothing length in front of a threshold `[verified:
§4b]`. This makes the simple model 9 inputs, still
well inside a ceiling of 12.

---

## 9. Depth of materialisation — a separate axis, separate document

Binaries, debris discs, moons, cluster membership, a full surface-scale build on
a visited planet. **None of this is more accurate physics; it is more stuff.** Filed with
the coupled-physics axis, the advanced model becomes a wish list and stops being
a spec. `[inferred]`

---

## 10. Computational complexity — measured

The previous version of this section asserted that the advanced model was
"computationally trivial." That was intuition, and **it was wrong in one place
and right for the wrong reason in another.** Benchmark in `bench.py` /
`bench2.py`; grid is N_R annuli marched over N_t timesteps.

### What the benchmark establishes and what it does not

Absolute times measure a sketch written to find scaling, not the real model, and
should not be quoted. **The exponents are the deliverable**, because they are
properties of algorithm structure rather than of the implementation.
`[verified: bench2.py output]`

### Scaling exponents in N_t

| Stage | Exponent | Verdict |
|---|---|---|
| Simple chemistry | 0.90 | Linear |
| Multi-element + DTD, naive | **2.07** | **Quadratic — class change** |
| DTD, deposit-forward with K ∝ N_t | **1.82** | Still quadratic — see below |
| DTD, kernel resolution decoupled (K fixed) | **1.01** | Linear. The fix |
| Migration, applied in-loop | 0.94 in N_t, **2.74 in N_R** | Superlinear in radius |
| Migration, post-process | — | 0.8× the simple model. Free |
| Catalogue sampling | 1.08 in N | Linear, as claimed. 10⁷ stars in 0.71 s |

### The instrument found a defect in my own proposal on first run

The deposit-forward scheme was proposed in §8 as the cheap fix for the DTD
quadratic. **It is not a fix.** Truncating the delay kernel at a fixed *physical*
window means K = T_window·N_t/T_total, so K grows with N_t and the scheme stays
quadratic — measured at 1.82. `[verified: bench2.py §1]`

The working fix is to decouple **kernel resolution from integration
resolution**: bin the DTD into a fixed number of coarse bins regardless of how
finely time is marched. Exponent 1.01, and the gap against naive widens with
refinement — 46× faster at N_t = 8000 and growing. `[verified: bench2.py §1]`

This is the recorded pattern holding again: the last three executable
specifications each found a real defect on their first run `[verified:
rule B1]`.

### The surprise: the class change is in time, not radius

The instinct is to protect radial resolution and refine time freely. **The
measurement says the opposite.**

The simple model is *interpreter-bound*, not FLOP-bound, at any realistic radial
grid: exponent 0.13 in N_R over 50–400 annuli, reaching only 0.75 by 3200
`[verified: bench2.py §3]`. Per-timestep cost is 6.9 µs at N_R = 50 and 9.0 µs
at N_R = 400 — quadrupling the radial grid costs 30%. **Radial resolution is
nearly free; temporal resolution is where the model can be made expensive.**
`[inferred from verified measurements]`

Consequence for the convergence audit: N_R and N_t are not interchangeable
quality knobs and must not share one. A galaxy analogue of `convergence.py`
should sweep them independently.

### Where the advanced model's cost actually lives

| Term | Multiplier over simple |
|---|---|
| Multi-element chemistry + DTD (correctly implemented) | **4.9×** |
| Coupled inflow/outflow fixed point, 8 iterations | **×8 on top** |
| 20 satellites at quarter resolution | +1.6× |
| **Total, realistic** | **~40–60×** |

`[verified: bench2.py §4]`

**The dominant term is not the added physics — it is the fixed-point iteration
that coupling requires.** The DTD quadratic is recoverable by implementation;
the migration cost is recoverable by moving it out of the loop; the coupling
multiplier is not recoverable, because it is what "cyclic" costs. That is an
independent, measured justification for the simple/advanced line already drawn
on other grounds: **everything one-pass and acyclic is simple** — the criterion
turns out to also be the criterion that separates the recoverable costs from the
unrecoverable one. `[inferred]`

### And the earlier conclusion survives, but not for the reason given

Even the pessimistic figure sits inside a 30-second whole-galaxy budget. The
structural reason is worth stating: the expensive stage in a *terrain* model is
drainage, which is globally connected — a cell's outflow depends on its whole
basin. **No field in a galaxy model has that property** `[inferred]`. So the
headline claim holds:
**the reason to defer the advanced model is validation, not runtime.** But it
holds at 40–60×, not at the "trivial" originally asserted, and only if the DTD
and migration are implemented as specified above rather than naively — naive
versions would put the advanced model 500×+ over simple and rising with time
resolution. `[inferred from verified measurements]`

### Not measured

Merger-tree construction; memory footprint; the catalogue's interaction with
advanced-model fields; anything cold-cache. Recorded as gaps, not assumed cheap
— that assumption is what this section just corrected.

---

## 11. Rulings

| # | Question | Ruling |
|---|---|---|
| 1 | λ default — population mean or MW-inferred? | **MW-inferred, λ ≈ 0.015.** Debt #1 |
| 2 | M_• input or derived? | **Derived**, 5–6× miss recorded as debt #2 |
| 3 | `PITCH_SEIGAR` or `PITCH_YU`? | **`PITCH_YU`.** Seeded draw, no input. Dissolves `R_CLOSURE_*` |
| 4 | Migration kernel in simple model? | **In.** Input #7 |
| 5 | c₂₀₀ derived from formation epoch? | **Derived.** Input #3 does two jobs |
| 6 | Ceiling: 12? | **12.** Currently at 8 |
| 7 | `galaxy_age` derivable from z_form? | **Cut.** Input renamed `halo_assembly_z` |
| 8 | Rename `spin`? | **`disc_spin` λ_d.** Discharges debts #1 and #7 — see §6 |
| 9 | Add `baryon_retention`? | **Added.** Input #3b |
| 10 | M_• — uphold, seed, or input? | **Derived mean + seeded residual**, width from bulge type. No branch, no input (§13) |
| 11 | Is every second infall merger-delivered? | **DISSOLVED.** `gas_fraction` on merger events; input #6 cut (§14) |

**Calibration debt register**

1. ~~λ default is 3× off the population mean.~~ **DISCHARGED by ruling 8** — the
   gap was a parameter confusion, not a property of the MW (§6).
2. M_• derived from M–σ misses the MW by 5–6×.
3. m_d derived by abundance matching rather than from feedback physics.
4. Pitch-angle closure radius is arbitrary — largely dissolved by ruling 3 (§5).
5. Cooling delay from halo assembly to SF onset is unvalidated (§3).
6. Adiabatic contraction of the halo by infalling baryons is unmodelled (§4b).
7. ~~`spin` is circular.~~ **LARGELY DISCHARGED** — λ_d is now jointly
   constrained by two independent observables, not one (§6).
8. Acceptance entries 13, 14, 16, 17 and **18** become statistical, not pointwise
   (§4b, §13).
9. ~~α-bimodality may be reachable without a merger.~~ **ANSWERED by S9, and the
   answer is that it is not reached *with* one either** — see debt #27. The
   advanced model has the α–Fe plane and a split that never names the merger,
   and a merger-free galaxy and the default one both come out `single`
   `[verified: tests/test_chemistry_dtd.py::test_the_experiments_that_looked_for_a_valley]`.
   The question as posed is therefore moot until the valley exists at all.
   S3's reasoning, kept for the record: **not testable in the
   simple model, and S3 established why rather than reporting a null result.**
   Two independent reasons. First, [α/Fe] needs two nucleosynthetic channels
   with different delay times, and instantaneous recycling collapses them into
   one — the model has a single abundance and *no α–Fe plane* in which anything
   could be bimodal. Reporting "no bimodality without a merger" from it would be
   reading an instrument that cannot detect the signal (rule B3). Second, and
   worse, the model's thin/thick split is **defined** as "born before the last
   major merger", so a merger-free run has no thick disc by construction and
   cannot be evidence about whether one is needed. The test moves to S9, which
   has the DTD; whoever runs it must also replace the split criterion with one
   that does not name the merger.
10. **λ_d's ruled default was inferred against the wrong radius.** Ruling 8 set
   λ_d = 0.0144 from R_d√2/R_vir with R_vir = 255 kpc, which is Huang+16's
   top-hat virial radius for M_vir ≈ 0.9 × 10¹² M☉ — about 95 ρ_crit, not 200
   `[verified: tests/test_disc.py::test_the_255_kpc_is_a_top_hat_radius_not_R200]`.
   MMW98's relation takes r₂₀₀, and this model's r₂₀₀ for the default
   M₂₀₀ = 1.1 × 10¹² M☉ is 212.9 kpc, so the same measured R_d = 2.6 kpc gives
   λ_d = 0.0173. S1 implements the mechanism correctly and moves the default;
   ruling 8's *argument* is untouched, and both numbers lie inside Burkert+10's
   λ_d = 0.01–0.03 for m_d ≈ 0.05. **Needs a re-ruling to close** (§6, D30).
11. **One baryonic component.** S1 puts the whole retained baryon budget in a
   single exponential of scale length 2.6 kpc: no gas phase (S2), no bulge
   (S3–S4). Two consequences, both recorded rather than tuned away:
   `stellar_mass_total` is the baryon budget and so is high by the ~8 × 10⁹ M☉
   of gas, and v_c(R₀) is over-concentrated, which makes acceptance entry 3
   miss high by 5.1 km/s. **Prediction, stated so it can fail:** giving the gas
   its own much shallower profile at S2 brings the Sun's tangential velocity to
   246.4 km/s, inside 248 ± 3 `[verified:
   tests/test_disc.py::test_the_recorded_cause_of_the_row_3_miss]`. Registered
   in `spec.MISSES`; if S2 does not close it, the explanation is wrong.
12. **The c₂₀₀–z relation is unvalidated and load-bearing, and S10 measured how
   load-bearing.** c₂₀₀ = 4.1(1 + z_f) applies a normalisation quoted for c_vir
   to c₂₀₀ without the conversion between the two overdensities, and z_f = 2.5
   is the midpoint of §3's "z ≈ 2–3" rather than a measurement. The one check it
   passes is that c₂₀₀ = 14.4 lands inside the 10–18 the Milky Way's own
   measurements span (§4b). Four things the S10 audit established, none of which
   changes the constant — this session records rather than fixes:
   - **The conversion is not a free choice.** The model publishes its own
     R₂₀₀ = 212.94 kpc, and debt #10 already established that the 255 kpc it is
     compared against is a top-hat virial radius. Their ratio is 1.198, so the
     c_vir normalisation used as a c₂₀₀ one is high by that factor and K should
     be 3.42, giving c₂₀₀ = 11.98. **Both values pass the only check the
     constant has**, because both are inside 10–18.
   - **The correction closes acceptance row 3 on its own**: v_c(R₀) goes from
     256.0 to 246.92, inside 248 ± 3, while the star formation rate, the gas
     mass, the stellar mass and the disc scale length move by less than 1 part
     in 10⁹. Row 3's recorded miss explains it by every baryon sitting inside R₀
     (debt #18) and predicts rows 2, 3 and 20 closing together, so **there are
     now two explanations and rows 2 and 20 tell them apart**. Whichever finally
     closes row 3, the other two rows are the check that it was the right one
     `[verified: tests/test_halo.py::test_the_conversion_closes_row_3_and_moves_nothing_else]`.
   - **K and z_f enter only as their product**, so no measurement of the
     assembly epoch alone can validate the relation: c₂₀₀ ≈ 12 is reachable by
     K = 3.42 at z_f = 2.5 or by K = 4.1 at z_f = 1.92, and the model cannot
     tell the two apart `[verified:
     tests/test_halo.py::test_k_and_the_assembly_epoch_enter_only_as_their_product]`.
   - **The recorded sensitivity is stale and too small.** Across the cited
     z = 2–3 this entry says v_c(R₀) moves "about 10 km/s, three times
     acceptance entry 3's error bar". Re-measured after S2 and S3 changed the
     baryon profile it is **15.29 km/s, 5.1× row 3's half-width**, and the epoch
     the table wants, z_f ∈ [1.9, 2.1], lies below the cited range rather than
     inside it `[verified:
     tests/test_halo.py::test_the_epoch_the_acceptance_table_wants_is_below_the_cited_range]`.
   The chain reaches the advanced model's one fitted constant and stops there:
   at K = 3.42 the escape velocity at R₀ falls from 578 to 565 km/s and the
   present-day gas at R₀ from +0.001 to −0.014 dex, so `WIND_SPEED` would need
   refitting by about a hundredth of a dex and row 22 stays inside its target at
   −0.0563 `[verified: DECISIONS.md D95]`.
13. ~~**Two routes to the disc scale length, disagreeing by 44%.**~~
   **DISCHARGED by S3.** The first suspect was the right one:
   `GAS_DISC_SCALE_RATIO` was set to 1.5 from the observed HI-to-optical ratio,
   which is measured between *final* discs and not between the infall and the
   stars. Corrected to 1.0, which two independent arguments agree on — MMW98
   predicts the gas that forms the disc arrives with the disc's own scale
   length, and running the model back from the observed final ratio picks
   1.0–1.1. The two routes then give 2.52 and 2.605 kpc, agreeing to 3.3%
   `[verified: tests/test_sfh.py::test_the_two_disc_scale_lengths_agree]`.
   MMW98's structure factors f_c and f_R are untouched and remain debt #6.
14. **One infall episode, not two.** GALAXY_INPUTS.md §3 names the two-infall
   framework, but ruling 11 makes the second infall merger-delivered and
   `mergers[]` is UNSET until S3. So S2 models a single exponential accretion
   and the thin/thick chemical split has nothing to make it. This is also the
   control for debt #9: a merger-free galaxy is exactly what is running now.
15. **Every gradient the model makes is a third of the observed one.** Row 22
   comes out −0.019 dex/kpc against −0.06, row 23's old end −0.009 against
   −0.04. Measured, not assumed: the gradient is *exactly* insensitive to the
   yield `[verified: tests/test_chemistry.py::test_the_gradient_does_not_depend_on_the_yield]`,
   so the level and the tilt are set by different things and this is about the
   tilt. Reproducing −0.06 needs an inside-out index near 3, while the source
   that gives τ₀ = 7 Gyr at R₀ gives a linear τ(R), i.e. n = 1. Predicted
   cause: outflows, which remove more metal from the outer disc than the inner
   and are an advanced-model axis (§8). **The prediction ran at S9 and held for
   row 22**: with a metal-loaded wind whose escape fraction follows the local
   escape velocity, the advanced model's present-day gradient is −0.057 dex/kpc,
   inside the target, and a wind with no radial dependence gives −0.043 — the
   difference is the tilt the wind supplies `[verified: tests/test_chemistry_dtd.py::
   test_debt_15s_prediction_holds_and_row_22_closes, ::test_the_tilt_is_the_wind_s_radial_dependence]`.
   Row 23 did not follow, which the S2 prediction said would mean migration is
   wrong too: debt #28. The simple model keeps both misses; it has no wind.
16. ~~**`NET_YIELD` is an effective yield and is calibrated.**~~ **DISCHARGED by
   S9.** 0.011 against a nucleosynthetic 0.03–0.04, the difference being metal
   loss the simple model has no mechanism for. The advanced model has the
   mechanism: nucleosynthetic yields (y_O = 0.015, y_Fe,cc = 0.0012, y_Fe,Ia =
   0.0017 `[recall: WAF17]`, y_Z = 0.037 by solar proportion) and a wind whose
   escape fraction at R₀ comes out at **0.75** once one constant, `WIND_SPEED`,
   is set so the present-day gas at R₀ is solar. The factor of three is now a
   result rather than a fit `[verified: tests/test_chemistry_dtd.py::
   test_the_wind_takes_the_share_the_effective_yield_was_hiding]`. The simple
   model keeps `NET_YIELD` as its own constant, explained rather than blind.
   **S10 puts a number on the discharge.** The two routes share no constant —
   one is a fit to the solar neighbourhood with no outflows, the other is
   nucleosynthetic yields minus what a wind removes — and they agree to 10%:
   y_Z = 0.0406 with 75.32% of fresh metals escaping at R₀ gives an effective
   yield of 0.01001 against the fitted 0.01100 `[verified:
   tests/test_chemistry_dtd.py::test_the_winds_effective_yield_and_the_fitted_one_agree_to_ten_percent]`.
   Agreeing at all is the content of the discharge; the residual 10% is the two
   models' different recycling, and is recorded rather than tuned away.
17. **Acceptance rows 20 and 21 have zero-width targets.** The sources quote no
   uncertainty, so the check fails for any float that is not bit-exact. Row 20
   agrees to 6% and still fails. A defect in the table, not the model; the fix
   is to read the source's uncertainty or to give the table a way to say "no
   testable target", which belongs to the S10 audit. **S10 took the second
   option and explains why it could not take the first.** `Quantity.testable` is
   false for a pointwise row whose interval has zero width, `spec.untestable()`
   lists them, the spec report names them once as a table defect rather than per
   model, and a new row added without an interval now has to declare itself in
   its note `[verified: tests/test_spec.py::test_the_table_says_which_rows_have_no_testable_target,
   ::test_a_new_zero_width_row_cannot_be_added_silently]`. Nothing is widened
   and no verdict moves: row 20 still fails, by 28%, for debt #18's reasons.
   Reading the source was not available — the uncertainty is not in this
   repository, and rule B14 will not let a `[verified]` tag rest on a document
   outside it. **Inventing an interval now would be worse than not having one**,
   because the model's answer is already known and choosing a width against a
   known answer is the move rule B5 exists to prevent. What discharges this is a
   citation with an uncertainty, entered before the row is next judged. Row 14
   quotes no uncertainty either and is *not* affected: it is statistical, and an
   ensemble's central interval can contain a point target.
18. **No high-angular-momentum accretion component.** With the infall carrying
   the disc's own scale length (debt #13's fix), nothing accretes beyond about
   10 kpc, so the extended HI disc that holds most of the Milky Way's gas does
   not exist in the model. **One cause, three failing rows**: gas mass 38% low
   (row 20), star formation rate 1.14 against 1.65 (row 2), and every baryon
   packed inside R₀ so v_c there is too high (row 3) `[verified: spec.MISSES
   rows 2, 3, 20]`. Predicted fix: a second accretion channel at high angular
   momentum, which adds gas where the star formation threshold protects it and
   leaves the stellar structure alone. Rows 3 and 4 are the check that it is
   *high* enough in angular momentum — if the stellar disc broadens, it is not.
   The bulge pushes row 3 the other way and arrives at S3–S4, so those two must
   be judged together.
19. **The thick disc is too compact and too massive, and the gate passes on the
   cancellation.** Scale length 1.17 kpc against 2.0 (row 5) and mass
   1.07 × 10¹⁰ against 6 × 10⁹ (row 11). Row 9 — S3's gate — reads 0.103 inside
   its 12% ± 4% *only because those two errors compensate*: raising the merger's
   `gas_fraction` to fix the mass drives row 9 to 0.015, because a thick disc
   this centrally concentrated sheds surface density at R₀ far faster than it
   sheds mass `[verified: DECISIONS.md D51]`. Row 5 is the prerequisite — with
   the right extent the mass and the ratio can be right together. If they still
   cannot, the split criterion is what is wrong.
20. ~~**The thin/thick split is defined by the merger, so it cannot be evidence
   about mergers.**~~ **DISCHARGED by S9 in the advanced model.** "Born before
   the last major merger" is a definition, not a measurement, and it made debt
   #9 circular. The advanced model's `vertical_alpha` splits on the valley
   between the two [α/Fe] sequences at R₀ and never reads the event list
   `[verified: tests/test_chemistry_dtd.py::test_the_split_criterion_never_names_the_merger]`.
   The simple model keeps the merger split by design; what the chemical
   criterion then finds is debt #27.
21. **The first link of the pattern-speed chain is not modelled.** §4b describes
   it as disc dominance → bar length → pattern speed. S4 models the second and
   third links; the bar's half-length is scaled from the disc scale length
   alone, because no relation between disc dominance and bar length is quoted
   anywhere in this project and inventing one would be rule A4's failure a level
   up. `disc_dominance` is published and unused so the gap is visible.
22. **The pitch–shear relation has no lever in this model, so it cannot be
   falsified by it.** Measured, once, as ruling 3 asks: across the whole input
   space the shear rate moves only 0.829 → 0.967, buying 0.30° of pitch, while
   the seeded draw gives 5.12° — **0.3% trend against 99.7% draw**
   `[verified: DECISIONS.md D57]`. `PITCH_SHEAR_SLOPE` is therefore doing no
   measurable work, and a wrong slope would look exactly like this one. A live
   instance of rule B11.
23. **The arms are parameters, not a pattern.** S4 publishes a pitch angle and an
   arm multiplicity; nothing publishes a non-axisymmetric density, so the star
   catalogue S5 draws from it is axisymmetric and the galaxy has no visible
   spiral structure. GALAXY_PLAN.md §3 promises stage 4 is the "first
   recognisable galaxy" and on this evidence it is not `[verified:
   DECISIONS.md D62]`. Faking a modulation in the catalogue was refused: it
   would put structure in the sample that no field justifies.
24. ~~**The spec ensemble re-runs the whole pipeline for two scalars.**~~
   **DISCHARGED by S6.** Rows 16 and 17 needed twenty seeded runs, and each one
   recomputed the halo, the chemistry and a 20 000-star catalogue to reach two
   numbers that depend only on checkpoint 4. The fix is the one rule D4 asks the
   API for, applied to the spec runner: `spec.ensemble` now names the fields it
   wants and the runner executes the dependency closure above them and nothing
   else (`run(..., only=…)`). An ensemble member costs **0.162 s instead of
   0.616 s, 3.8× less**, and the twenty runs 3.2 s instead of 12.3 s
   `[verified: DECISIONS.md D63]`. The values are bit-identical, which is
   asserted rather than argued — a stage is a pure function of its declared
   reads, so running fewer of them cannot move the ones that run `[verified:
   tests/test_run.py::test_a_partial_run_agrees_with_the_full_run;
   tests/test_spec.py::test_the_ensemble_runs_only_the_stages_its_fields_need]`.
   What is *not* discharged is D61's per-cell cost: the catalogue still builds
   every cell's streams whether or not anything asks for that cell, and that is
   a `performance.py` question at S10. **S10 measured it and D61's premise is
   half right.** The catalogue costs 113 ms for the published 20 000-star
   sample, and **90% of that does not depend on how many stars are asked for**
   (0.59 µs per star, fitted over an eightfold range of sample sizes). Of the
   100 ms fixed, 1.0 ms is setup, **14.9 ms lays out all 1024 cells at 14.5 µs
   each — that, and only that, is what is paid whether or not anything asks** —
   and 84.3 ms draws in the 516 cells that actually realise a star, about 163 µs
   each. So D61's "eight `Generator` constructions, about 22 µs each" is right
   about the cost of a cell that realises stars (176 µs predicted against 163
   measured) and wrong about who pays it: **508 of the 1024 cells realise
   nothing and cost only their layout draw.** A nine-cell region query costs
   2.8 ms, 2.4% of the whole `[verified: DECISIONS.md D96;
   tests/test_performance.py::test_the_catalogue_cost_is_separated_the_way_debt_61_asks]`.
   The trade-off itself is now debt #31.

25. **The two occurrence relations §12 cites cannot both be true, and the
   mechanism picks the steeper one.** §12 quotes giant occurrence going as
   10^(β[Fe/H]) with β ≈ 2 `[recall: Fischer & Valenti 2005, via §12]` *and*
   running from ~5% at [Fe/H] = 0 to ~25% at +0.5 `[recall: the Adibekyan review,
   via §12]`. Those are different claims: β = 2 takes 5% to 50% over that
   interval, and reaching 25% needs β ≈ 1.4. S8 did not choose between them. It
   derived occurrence instead — a giant is a zone whose solids clear the critical
   core mass, the disc mass is log-normal about its median, so occurrence is a
   probit in [Fe/H] — and **measured** the slope the mechanism produces:
   **β = 2.99**, with occurrence reaching **51%** at [Fe/H] = +0.5
   `[verified: galaxy/stages/planets.py giant_occurrence_index and
   giant_occurrence_rich; tests/test_planets.py]`. Only the zero point is fitted.
   The slope is not free: for a threshold on a log-normal, β at 5% occurrence is
   fixed by the disc-mass scatter alone, and §12's own 0.3 dex forces β ≈ 3.
   **Prediction, stated so it can fail:** matching β = 2 requires a disc-mass
   scatter near 0.45 dex, so a measurement of that width decides this — if discs
   really are 0.3 dex wide, then either occurrence is steeper than Fischer &
   Valenti found or a threshold is not the whole mechanism (migration destroying
   close-in giants would flatten it) `[verified:
   tests/test_planets.py::test_the_slope_is_the_disc_mass_scatter_and_not_a_fitted_exponent]`.
   What the model does get without being told: giant occurrence around an M dwarf
   falls to ~1% at [Fe/H] = 0 and rises to ~20% by +0.5, bracketing the
   12.4 ± 5.4% against 0.96 ± 0.51% split §12 quotes from Montet+14.

26. **The advanced model's wind carries metals and no mass.** The escape
   fraction removes a generation's fresh supernova metals before they mix, and
   the gas budget stays the sfh stage's — the wind's mass is taken to be the
   ejecta's, small against the accretion, so rows 1, 2, 3 and 20 are the same
   in both models by construction `[verified: tests/test_models.py::
   test_the_models_agree_upstream_of_chemistry_and_differ_below]`. A
   mass-loaded wind (η ≈ 1) would remove as much gas as forms stars and change
   every one of those rows; it is not modelled. One visible consequence: the
   gas-starved centre collects the late Ia iron of its old stars to [Fe/H] =
   +1.5 inside half a kiloparsec, against the +0.5 real bulges reach, because
   nothing carries iron out of a region with 5 M☉/pc² of gas `[verified:
   tests/test_systems.py::test_metallicity_is_looked_up_not_drawn]`. The bulge
   and its inflow are S10 questions; recorded, not clipped (rule B9). **S10
   checked the grid and it is not the grid.** Across N_t from 500 to 8000 the
   centre's peak [Fe/H] wanders by less than 0.10 dex without converging
   monotonically, and stays above +1.4 while the simple model's stays below
   +0.7 on every grid: the dex that separates +1.5 from the +0.5 bulges reach is
   the massless wind `[verified:
   tests/test_chemistry_dtd.py::test_the_centres_iron_is_the_wind_and_not_the_grid]`.
   What S10 also found is that **no acceptance row could ever have caught this**
   — see debt #29.
27. **There is no valley in the [α/Fe] distribution at R₀, so the advanced
   model has no thick disc — seven rows on one cause.** The plane exists: the
   plateau is at +0.45, the present-day gas at R₀ at +0.05. But the stars now
   at R₀, migrants included, form **one mode at [α/Fe] = +0.21** with a high-α
   tail, where the local track lingers while the delayed iron catches up with a
   star formation history that never pauses. The chemical split (debt #20)
   selects nothing, so rows 5, 7, 8, 9 and 11 read zero, row 10 carries every
   star, and row 24 reads `single` `[verified: spec.MISSES_ADVANCED]`. Measured
   rather than assumed: a sweep over τ₀ ∈ [1, 12] Gyr and the merger's
   gas_fraction ∈ [0.2, 0.95] never opens a valley (dip depth at most 0.38, at
   τ₀ = 1 Gyr), and re-integrating the infall with a fast first episode, a slow
   merger-delivered second one and a pause between them reaches 0.31 — the
   pause adds nothing `[verified: DECISIONS.md D91]`. **Prediction, stated so
   it can fail:** the missing piece is the inner disc reaching low [α/Fe]
   early and its migrants arriving at R₀ as a separate lump, which needs an
   infall far faster inside 4 kpc than τ₀(R/R₀) gives; if a steeper inside-out
   law inside R₀ does not open the valley, the DTD's long tail is what keeps
   the local track at intermediate [α/Fe]. The simple model is untouched: its
   thick disc is the merger's and its rows read as before. **A trap S10 found
   for whoever picks this up:** at N_t = 8 the advanced model reports a valley.
   A time grid coarse enough to under-resolve the delayed iron manufactures
   exactly the signal this debt is hunting, so a `bimodal` verdict is worth
   nothing until the grid it was measured on is stated `[verified:
   tests/test_chemistry_dtd.py::test_a_coarse_time_grid_manufactures_the_valley_debt_27_is_looking_for]`.
28. **Migration is too strong once the tilt is right.** S2 recorded that if
   row 22 steepened and row 23 did not, `migration_efficiency` was wrong too.
   Row 22 steepened to −0.057 in the advanced model and row 23 stayed at
   −0.019: the young/old ratio is 3.1 against the observed 1.75. A kernel
   width of **2.5 kpc** at 8 Gyr puts row 23 at −0.039 with a ratio of 1.6
   `[verified: tests/test_chemistry_dtd.py::
   test_s2s_prediction_fired_migration_is_too_strong_once_the_tilt_is_right]`;
   the default stays the cited 3.6 kpc `[recall: Frankel et al. 2018]`, and
   the conflict is preserved rather than averaged (rule B12). Two live
   explanations: the citation's width is not this kernel's width (a Gaussian
   in radius growing as √age), or the old gas gradient the model flattens from
   (−0.127 dex/kpc at 10 Gyr, with no migration) is too steep to begin with. A
   gradient measured at 10 Gyr decides between them.

29. **The acceptance table reads nothing inside 4 kpc, so the model's worst
   number is invisible to it.** The gradient rows are fitted over R = 4–12 kpc;
   rows 3, 6 and 8 are evaluated at R₀; rows 1, 10, 11, 19 and 20 are integrals
   over the whole disc. Nothing reads a *value* in the inner disc, which is
   exactly where debt #26's [Fe/H] = +1.5 lives — a full dex above what real
   bulges reach, on 7 annuli of the default grid, and every acceptance row
   passes over it `[verified:
   tests/test_chemistry_dtd.py::test_no_acceptance_row_reads_the_disc_inside_four_kiloparsecs]`.
   The table was assembled from BHG16's summary quantities, which are the ones
   the Milky Way is *measured* in, so this is not an oversight so much as an
   inherited shape — but it means the table cannot be read as covering the
   model. **Prediction, stated so it can fail:** a single row on the central
   metallicity would have caught debt #26 at S9 rather than S10, and if adding
   one turns out to catch nothing the model does not already record, then the
   inner disc really is only wrong in the one way debt #26 names.

30. **The vertical grid buys nothing and quietly moves a published field.**
   `halo_potential` is the only field on the z axis, and its only consumer —
   the advanced chemistry's escape velocity — reads column 0. So N_z is not a
   quality knob for anything the acceptance table can see: **not one row moves
   by even a thousandth of its target's width at any N_z, including N_z = 1**,
   where the single sample sits 2.5 kpc above the plane `[verified:
   tests/test_convergence.py::test_n_z_moves_no_acceptance_row_at_any_resolution]`.
   Two consequences. The scale heights of rows 6 and 7 are computed analytically
   by the vertical stage and are not fitted to a z profile, which is worth
   knowing before anyone reads them as a vertical-structure measurement. And
   `escape_velocity` is *declared* as the midplane escape speed while being
   evaluated at z = z_max/(2 N_z) — half a cell above the plane, at a height set
   by a grid knob. Measured, because the size is the whole question: the
   innermost annulus moves 1.03 km/s in 725 between N_z = 15 and 960, under 0.2%,
   because the NFW potential is nearly flat near r = 0 `[verified:
   tests/test_chemistry_dtd.py::test_the_midplane_escape_velocity_is_half_a_cell_above_the_midplane]`.
   The fix is one line — evaluate the potential at z = 0 rather than at the
   first cell centre — and this session records rather than fixes.

31. **The default grid is far finer than any acceptance row can detect, and
   nothing records what it is sized for.** N_R = 400, N_t = 2000, N_z = 60.
   Swept one knob at a time, the worst any acceptance scalar drifts against the
   default is **0.056 of its own target's width**, in either model; the
   drift-exceeds-width criterion first fires below N_R ≈ 16 and N_t ≈ 25, and
   never for N_z `[verified: DECISIONS.md D94;
   tests/test_convergence.py::test_the_acceptance_table_is_converged_on_the_default_grid,
   ::test_the_criterion_can_fire_and_is_shown_to]`. So the default is about 25×
   finer in radius and 80× finer in time than the table requires, and the
   justification must be the *rendered fields* — a profile plotted at 16 annuli
   is not a profile — which is nowhere written down. **This is not a proposal to
   coarsen the grid**: the acceptance table is 24 scalars and the viewer draws
   arrays. It is that the number nobody can defend is the one that will be
   changed by accident. D61's cell grid is the same shape of question one level
   down, and cannot be re-measured at all without editing the source, because
   `CELL_RINGS` and `CELL_SECTORS` are module constants and one of them is bound
   into a default argument.

32. **A per-stage or per-route cold profile bills a process-wide one-off to
   whichever stage triggers it.** The first `seeds.rng` call in a fresh
   interpreter costs 8.9 ms; every one after it costs 0.023 ms, a factor of
   about 380. The `pattern` stage is the first stage of both models to draw, so
   it reads at 30× cold-over-warm in `performance.py` and is not a 9 ms stage
   `[verified: DECISIONS.md D97]`. `performance.py` now measures the one-off in
   its own interpreter and publishes it beside the table. **`tools/timings.py`
   has the same term in its cold column and does not say so**: whichever route
   first reaches a seeded stage carries 8.9 ms that is not the route's. Not
   corrected there, because subtracting a measured constant from a published
   measurement is the sort of tidying that outlives its justification (rule B6);
   recorded so the column can be read.

---

## 12. The planets stage

Yes — but the two-substrate split falls in a different place, and one property of
planet formation makes this stage qualitatively unlike every other.

### The field half is structurally identical to the galactic disc

A protoplanetary disc is a **1D radial field**: surface density Σ(r), temperature
T(r), ice line, solid-to-gas ratio. Same shape as the galactic chemistry stage —
radial grid, prescribed rather than solved, no fixed point. The code is nearly
the same code. `[inferred]`

### The object half is chaotic, not merely scattered — and that changes the audit

§4b sorted derived quantities into *arithmetic*, *closed by physics*, and
*correlated with scatter*. **Planetary system architecture is in none of these.**
Identical initial conditions with infinitesimal perturbations give different
final systems; the late giant-impact phase is genuinely chaotic. It is not that
the relation has scatter — there is no deterministic outcome to have scatter
about. `[recall]`

Consequence: the planets stage is a **seeded draw by construction**, and its
acceptance checks are *necessarily* statistical.

This inverts the cost noted in §4b. For the galaxy, going statistical was a
concession. Here it is the native form of both the physics **and the data** —
Kepler and the RV surveys publish occurrence rates, not predictions for
individual systems. **The planets stage is therefore the easiest stage in the
pipeline to validate, not the hardest.** `[inferred]`

### Metallicity is inherited, not input — and the coupling is steep

The strongest single predictor of giant-planet occurrence is host metallicity,
which the galaxy model already computes. Occurrence scales roughly as
10^(β[Fe/H]) with β ≈ 2, i.e. with the square of the iron abundance `[verified:
Fischer & Valenti 2005 abstract; Wang & Fischer]`. Observationally, occurrence
runs ~5% at [Fe/H] = 0 to ~25% at [Fe/H] = 0.5 `[verified: Adibekyan review §
Trends with Stellar Metallicity]`, and for M dwarfs splits 12.4 ± 5.4% above the
sample median against 0.96 ± 0.51% below `[verified: Montet+14 §4.4]`.

**This is the payoff for the whole galactic chemistry stage.** The metallicity
gradient and its evolution with age — acceptance entries 22 and 23 — propagate
directly into where in the galaxy giant planets exist and when they became
possible. Nothing else in the model has that reach. `[inferred]`

### Asteroid belts are derived, not modelled

A belt is not an object to place; it is **a region where a giant planet's
resonances prevented accretion.** Given giant positions — which the formation
stage already produced — belt inner and outer edges follow from the resonance
locations, and the same construction gives the Kuiper analogue (outside the
outermost giant) and debris discs generally. Zero inputs, zero seeds.
`[inferred]`

Same treatment applies down the list: rings from moons inside the Roche limit;
Oort-cloud analogues from giant-planet scattering; regular satellites from
circumplanetary disc mass, which scales with planet mass; tidal locking from
semi-major axis, stellar mass and age. **Irregular satellites are captures and
must be seeded.** `[inferred]`

### Forbidden: N-body

Any stability filtering must be closed-form — mutual Hill separation, or an AMD
criterion. The moment an integrator enters the loop, rule 1 is gone and the cost
model in §10 is void. `[inferred]`

### Cost — measured

`bench_planets.py`, vectorised **across** systems rather than within one, since a
galaxy is one object with many cells and a planets stage is many objects with few
cells each.

| Systems | Time | Per system |
|---|---|---|
| 10³ | 0.003 s | 3.0 µs |
| 10⁴ | 0.039 s | 3.9 µs |
| 10⁵ | 0.354 s | 3.5 µs |
| 10⁶ | 4.70 s | 4.7 µs |

Scaling exponent **1.05** — linear, as the architecture requires. A million
systems with 48 radial zones each is 48 million cells in under five seconds.
`[verified: bench_planets.py output]`

**Why the handoff must be summary scalars.** A full surface-scale terrain build
is order tens of seconds per world `[recall]`. At 10⁵ systems that is hundreds of
hours. The summary-scalar handoff, with any deeper build run lazily on visit, is
not an optimisation — it is the only option.

**What the benchmark does not establish.** Cost only. Its giant-planet occurrence
comes out near 0.17%, against ~5–10% observed — the constants are unfitted, and
that failure is visible on the first run, which is the point of publishing the
number rather than the verdict. `[verified: bench_planets.py output vs Adibekyan
review]`

### The handoff: a self-defined, closed scalar set

The stage publishes what the formation model determines, declared under rule A8
like any other field: **mass, insolation, volatile inventory, rotation, obliquity,
atmosphere class.** Some are derived (mass, insolation), some seeded — obliquity
is set by giant impacts and rotation by accretion plus tides, both stochastic.
Each says which on its `about` line.

`preflight` asserts the set is **closed and documented**. That is the gate; there
is no external contract to satisfy.

Shaping this stage around some downstream consumer's current input list would
import that consumer's arbitrary choices into physics that does not share them.
Publishing what the model knows and letting integration adapt is the better
direction, and it is also the only one that keeps this project self-contained.

**Note, not a blocker.** If this is later joined to a surface-scale world
generator, the two scalar sets must be reconciled and authority declared per
quantity. That is an integration session with its own gate.

### Does the planets stage add inputs? No — and here is the check

Rule 2 settles most of it structurally: **controls are global scalars only**
(rule A2), and a per-system control is the
planetary equivalent of a per-cell input. So the stage cannot have per-system
inputs whatever else is true. Every system-level quantity is inherited, derived,
or seeded:

| Quantity | Status |
|---|---|
| Metallicity [Fe/H] | **Inherited** from the chemistry stage |
| Stellar mass | **Seeded** — drawn in the `systems` stage from the IMF |
| Disc mass | **Seeded** — correlates with stellar mass, ~0.3 dex residual |
| Disc dispersal time | **Derived**, then seeded. Photoevaporation depends on ambient UV, which depends on local SF density, which the galaxy model already computes `[inferred]` |
| Occurrence normalisation | **Level 0 constant**, with debt — the benchmark misses it by ~30× |
| Planetesimal formation efficiency | **Level 0 constant** |
| Disc-mass scatter width | **Level 0 constant**. Cluster truncation would make it derivable from local density; not modelled |

**Net: zero new inputs.** Count stands at 7 physical inputs.

### But it probably adds a seed, and the audit should decide, not me

`planets_seed`, separate from `systems_seed`, so planets can be re-rolled without
moving star positions. That is the same relationship `resource_seed` has to the
other stage seeds: its own workflow step, deciding nothing else.

But the checkpoint grouping is **derived, not designed** — `graph.py` computes
the earliest field each input can affect and `test_checkpoints.py` asserts the UI
agrees. So that audit decides whether planets is its own checkpoint. My expectation is that it will say yes; the expectation is not the
answer.

### The determinism that a game actually needs

`hash(planets_seed, star_id)` → the system. Same star, same planets, forever,
**regardless of visit order and without storing anything**. This is the property
that makes 10⁶ systems tractable: they are never persisted, only regenerated.

It is worth being explicit that this is a *stronger* practical guarantee than
derivation would give, not a weaker one. A derived system would also need its
inputs carried around; a seeded one needs the seed and the star's identity.
`[inferred]`

---

## 13. Ruling 10 in detail — M_• and the bulge-type fork

### Why the Milky Way misses

BHG16 record the MW falling below the M–σ relation by a factor of 5–6, and the
wording carries the answer: below the relation **for elliptical galaxies and
classical bulges** `[verified: BHG16 §3.4]`.

The Milky Way does not have a classical bulge. BHG16's own §4.2 concludes that
the bulk of bulge stars form a box/peanut structure — the inner three-dimensional
part of the bar — and that models match the observed cylindrical rotation with at
most ~8% initial classical bulge, and none was required `[verified: BHG16 §4.2.1,
§4.2.3]`. It is a **pseudobulge**, grown out of the disc by the bar.

### Pseudobulges do not merely scatter — they do not correlate

This is the part that changes the ruling. Classical bulges and ellipticals define
a tight M–σ relation with intrinsic scatter ~0.28 dex. **Pseudobulges show no
significant correlation at all** — Kormendy & Bender report r = 0.27 and r =
−0.08 for pseudobulges against r = 0.89 for classical bulges and ellipticals
`[verified: Kormendy & Ho 2013 §5 via Kormendy 2019; Kormendy & Bender 2011]`.
The proposed reason is that classical bulges and ellipticals form in gas-rich
mergers and coevolve with the hole, while pseudobulges grow secularly and do not
`[verified: Kormendy & Ho via Ho 2014 §summary]`.

So option (a) — uphold ruling 2 and derive from M–σ — is not "derive with a
recorded miss." **It is applying a relation that demonstrably does not hold for
this class of object.** That is worse than a failed acceptance check; it is a
wrong closure that happens to fail visibly.

### RULED (10): M_• is the sixth C-verdict, not a special case

Posing this as a fork between "derive" and "seed" was over-machinery. §4b already
established the standard remedy for a relation with real scatter: **derive the
mean, seed the residual.** Five quantities already have it. M_• is the sixth, and
it needs no new mechanism.

    mean:  M_•/10⁹ M☉ = 0.309 · (σ/200 km s⁻¹)^4.38    `[verified: Ho 2014 eq. 2]`
    width: interpolated by the classical bulge fraction the model computes
             fully classical  → 0.28 dex   `[verified: Kormendy & Ho via Ho 2014]`
             fully pseudo     → the observed pseudobulge spread, ~no correlation

Bulge mass comes from mergers plus bar buckling (§4), so the classical fraction
M_clb/M*_b is already available — BHG16 give 0–25% for the MW `[verified: BHG16
§4.2.4]`.

**What this avoids.** A hard branch needs a crossover constant and produces a
discontinuity in a quantity that is observationally continuous. Interpolating the
*width* by an existing derived quantity needs neither. `[inferred]`

**Cost: zero inputs, zero new constants beyond the two endpoint widths.**
Acceptance entry 18 becomes statistical — the cost §4b already priced.

### Why this is the right amount of machinery and not more

**M_• is a leaf.** Nothing in the simple model reads it. The nuclear region it
governs is far below the model's radial resolution; the galactic-centre hazard
field is dominated by supernova rate and metallicity; the systems and planets
stages never consult it. A leaf field with no consumers does not justify a branch
and a crossover constant. `[inferred]`

Revisit if AGN feedback enters the advanced model, at which point M_• acquires a
consumer and the precision starts to matter.

### A conflict that dissolves rather than persists

Harris reports the MW lying *close* to the M–σ line for a full mixed sample
`[verified: Harris 2012 §discussion]`, against BHG16's 5–6× miss. These are not
in conflict: they are measured against different reference relations, classical-
only versus all-galaxies. Recording the reference relation with the number is
what keeps this from looking like a contradiction later.

The Milky Way, being pseudobulge-dominated, lands at the wide end — its M_• is
drawn, not predicted. That is the correct representation of what is known.

---

## 14. Ruling 11 in detail — the second infall

### What the question is

The two-infall framework has the disc forming in two gas-accretion episodes
separated by a hiatus: the first builds the halo and thick disc, the second the
thin disc `[verified: Chiappini+97 via Molero+23]`. The hiatus is what produces
the α-bimodality — acceptance entry 24 `[verified: BHG16 §5.2.2]`.

Input #6 `second_infall_onset` names when the second episode starts. The question
is whether that timestamp is already implied by the `mergers[]` list.

### Why it cannot be settled by ruling on the physics

Two live positions `[recall]`:

- The second infall is **merger-delivered** — a gas-rich satellite brings the
  fuel, and the Gaia-Sausage-Enceladus event is the usual candidate for the MW.
- The second infall is **smooth cosmological accretion** resuming after a hiatus,
  with no merger required.

There is one galaxy in which this can be examined from the inside, and the answer
for it does not generalise. Ruling for either position would hard-wire a
contested claim into the input vector.

### The dissolution

**Do not rule. Put a gas fraction on merger events and let the mechanism
follow.**

`mergers[]` already carries per-event scalars and is already exempt from the
ceiling. Adding `gas_fraction` to each event means:

- A gas-rich merger delivers an infall episode. Its onset *is* the event's
  timestamp. `second_infall_onset` is then derived, and input #6 is cut.
- A galaxy with no gas-rich merger gets single-phase accretion, no hiatus, and no
  α-bimodality.

This is the pattern the project prefers — check whether an existing mechanism
already covers the case before adding a construct `[recall]`. The merger list is
the existing mechanism.

### It also makes the model falsifiable, which the input did not

Under the dissolution the model **predicts** that α-bimodality occurs only in
galaxies with a gas-rich merger. That is a claim which can fail. `second_infall_
onset` as a free input made no prediction at all — it simply granted the
bimodality wherever it was set.

State it as a prediction that could fail (rule B4).

### The honest caveat

Some chemical evolution models produce α-bimodality from smooth accretion plus
radial migration, with no merger `[recall]`. If that is right, the dissolution
under-produces bimodality in quiet galaxies. Record as **debt #9** and test it at
S4 by running a merger-free galaxy and checking whether the migration kernel
alone splits the sequence.

### RULED (11): dissolved

Input #6 `second_infall_onset` is **cut**. `mergers[]` event schema gains
`gas_fraction`. Debt #9 recorded. Count stands at **7 physical inputs** against a
ceiling of 12.
