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
| 3 | `halo_assembly_z` | z ≈ 2–3; **default 1.66 since S15** | RULED (7): renamed; `galaxy_age` cut. Also derives c₂₀₀ (5). The default is the epoch of the ΛCDM median halo of the default mass, 1.08–2.41 across the relation's scatter; the 2–3 was read against measurements of the *contracted* halo (debt #12, D117) |
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
| Rotation curve V(R) | **B** | Solved Poisson given components. Adiabatic contraction was a debt (#6) until S14 modelled it — cooling raises halo concentration, feedback reverses it `[verified: Kafle+14 §discussion]` — and its strength is now debt #46: every published invariant overshoots row 3 |
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
   **S17 built it and the miss is exactly the recorded size.** The `nucleus` stage
   (checkpoint 1, the first seeded stage in the run) publishes `black_hole_mass` as
   ruling 10 specifies: the M–σ mean of the spheroid's own dispersion, times a
   lognormal residual drawn from `world_seed`. The ensemble's median is 2.0 × 10⁷ M☉
   and the mean relation 2.9 × 10⁷, against 4.2 ± 0.2 × 10⁶ — 0.67 and 0.83 dex high,
   the ~0.75 GALAXY_INPUTS.md §3 says is expected `[verified: spec._MISSES row 18]`.
   **This debt is not the model's to discharge.** The relation is calibrated on
   classical bulges and ellipticals; the Milky Way's spheroid is a pseudobulge and
   pseudobulges do not correlate with the hole at all (§13), so the mean is being asked
   a question it cannot answer, and the model's own `bulge_classical_fraction` (0.17)
   says so in its own terms. What would discharge it is a published pseudobulge
   calibration — a zero point and a width — entered before the row is next judged; that
   is S22's ruling, not a session's build. Two closures were available and both refused
   with the answer already known (rule B5): an M_•–M_bulge relation on the classical
   share alone reads 5.2 × 10⁶ and would land the row, and a hard branch on bulge type
   needs a crossover constant ruling 10 declined to add.
3. m_d derived by abundance matching rather than from feedback physics.
4. Pitch-angle closure radius is arbitrary — largely dissolved by ruling 3 (§5).
5. Cooling delay from halo assembly to SF onset is unvalidated (§3).
6. ~~Adiabatic contraction of the halo by infalling baryons is unmodelled (§4b).~~
   **DISCHARGED at S14 — modelled, and the register's number for it was wrong by an
   order of magnitude** (D113; its strength is debt #46).
   **S13:** now the named lever for acceptance row 3. With debt #12's conversion done
   the row reads 242.7, low, and a bulge drawn from the disc lowers it further (debt
   #11's probe), so the mass the row misses inside R₀ is the halo's response to the
   baryons — several km/s at R₀ for a disc this massive `[recall: Blumenthal et al.
   1986]` — or a later assembly epoch (z_f 2.7–3.1). **Prediction:** contraction closes
   row 3 with z_f at 2.5; if it does not, the cited z ≈ 2–3 is wrong at its low end
   (spec.MISSES row 3, D107).
   **S14:** the halo stage contracts its NFW profile around the disc's exponential on
   its own radial mesh — Gnedin et al. 2004's invariant r M(r̄) by default, Blumenthal
   et al. 1986's as the named alternative (debt #46) — and publishes the contracted
   enclosed mass, circular velocity and potential; `halo_contraction` is r_i/r_f and
   `halo_circular_velocity_sun_initial` the halo's share at R₀ before it responded. The
   prediction failed the other way: the halo's share at R₀ rises 139 → 181 km/s (196
   under Blumenthal) and row 3 reads 270.8, not 245–251, so the epoch the row wants is
   0.7–1.0, not 2.7–3.1 `[verified: tests/test_halo.py::test_the_named_rulesets_and_what_each_is_worth_at_R0,
   ::test_the_epoch_row_3_wants_is_below_the_cited_range]`. The "several km/s" was
   recalled, not measured, and a probe would have cost fifty lines (rule B4). The
   scale length is computed by the halo since S14 — it is the disc the halo contracts
   around — and the disc stage reads it.
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
   **S10 (run 2):** the gas has its own profile now and row 1 still passes for
   the wrong reason. Its target, 5 ± 1 × 10¹⁰, is rows 10 + 11 + 12 — it
   *includes the bulge* — and the model has no bulge, so the disc carries the
   bulge's 1.4–1.7 × 10¹⁰; and row 10 passes only because row 11 fails high
   (thin = total − thick: a thick disc at its own target puts the thin disc at
   4.7 × 10¹⁰, outside 2.5–4.5) `[verified: AUDIT_RUN2.md §5, D-5]`. Rows 1, 10
   and 11 cannot be green together without a bulge stage or a smaller budget,
   and a smaller budget fails row 3 by 9 km/s more (`baryon_retention` 0.40 →
   265 km/s).
   **S14:** with the halo contracted around the disc (debt #6) row 3 reads 270.8, high
   by 20 km/s, and the bulge's 5–8 (D110) is not enough on its own: the bulge stays a
   stage for rows 10, 12 and 13, and row 3 is debt #12's epoch and debt #46's calibration.
   **S15:** row 3 is this debt's again. With the epoch derived (debt #12 discharged, D117)
   the row reads 260.1, high by 9–15 km/s against its window, and what is left inside R₀ is
   the baryons: 5.9 × 10¹⁰ M☉ in one exponential at 2.6 kpc. The bulge's 5–8 (D110) and the
   extended component's 4–13 (D114) together span 9–21, so the two mechanisms are the row's
   prediction (`spec._MISSES` row 3): S17's bulge and S16's component close it with the epoch
   at 1.66, or the baryon distribution is not the cause and debt #46 is.
   **S16:** the component's half is in: the high-j tail takes row 3 from 260.1 to 252.9 (the
   baryons' pull −4.3, the halo's weaker response −2.5; D119), high by 2 now. The bulge's
   5–8 (D110) is the other half and more than closes it — the prediction is now that S17
   reads the row inside 245–251, and if the bulge overshoots below 245 the two mechanisms
   together are too much and debt #46's invariant is too weak, not too strong.
   **S17: the spheroid is built and that prediction failed — the bulge is worth 1.6 km/s,
   not 5–8, and row 3 reads 251.3, a quarter of a km/s outside** (D121). The model is no
   longer one baryonic component: it is an exponential disc, the high-j tail beyond 12 kpc
   and a Hernquist spheroid of 7.71 × 10⁹ M☉ inside 2.5 kpc, all three derived from the
   same angular-momentum distribution and all three contracted around. Why D110's probe
   over-read by a factor of four: it drew the spheroid from the *stellar* disc in
   proportion on the uncontracted S13 halo, whereas the derived spheroid comes out of the
   accreting budget — and that budget included the ~15% of the exponential that lay
   outside R₀ and pulled the Sun outward, so moving it inward gives back nearly as much as
   the disc's flattening loses. Measured at S17: 1.4 × 10¹⁰ in the spheroid is worth 3.7
   km/s and 1.7 × 10¹⁰ is worth 4.2 `[verified: spec._MISSES row 3]`.
   **Rows 12, 13 and 14 are this debt's now, with row 3, and they have one cause.** The
   spheroid is 45% under the observed 1.4–1.7 × 10¹⁰ because it is only the mass no
   exponential disc *could* hold; BHG16 §4.2 says most of the Milky Way's bulge is the
   box/peanut a bar makes of the inner disc, and this model has no bar dynamics (debt
   #21). The prediction: buckling adds ~7 × 10⁹ and lands rows 12, 13 **and 3** together
   — and pushes row 14 from 116 to 123, outside 110–116, unless the bar-built component is
   less concentrated than the dissipational one. What S17 removed from this debt: rows 1
   and 10 no longer pass on the cancellation S10 recorded. Row 1 is the disc's stars *plus*
   the spheroid, which is what its target (rows 10 + 11 + 12) always meant, and row 10
   reads 3.17 × 10¹⁰ — inside whether or not row 11 is right (3.66 × 10¹⁰ if it were).   **S18: row 3 landed, by 0.04, and not on the bar.** 251.3 → 250.96: the merger's radial
   kick carries a fifth of the disc's stars outward across R₀ (−0.2 km/s on the built model,
   −0.4 alone), the basis-free velocity solver reads S17's profile 0.09 lower than the
   exponential basis did, and the derived threshold moves the row not at all (D124). The
   entry in `spec._MISSES` went (debt #29) and its replacement says so; the bar's prediction
   — 7e9 buckled into the spheroid reads 249.4 — stands unread, and rows 12–14 are still
   this debt's. A green row 3 is now worth exactly what a green row 2 is: inside on a
   mechanism smaller than the window.   **S20: row 3 is this debt's again, by 0.03.** 250.96 →
   251.03: `MERGER_HEATING` was re-derived from the thick disc's observed dispersion net of the
   secular heating (120 → 88.8, debt #42, D128), the radial spread at R₀ fell 1.47 → 1.09 kpc,
   fewer of the disc's stars cross R₀, and the +0.07 takes the row back out — by less than the
   solver's own correction, on the constant that had put it in. Its entry is back in
   `spec._MISSES` (since S20, both models) and its prediction is unchanged: the bar's buckling,
   249.4. The first infall's law, probed five ways at S20, moves this row by under 0.1.

12. ~~**The c₂₀₀–z relation is unvalidated and load-bearing.**~~ **DISCHARGED by S13 and
   S15** — the conversion at S13, the epoch at S15 (D117): the default is the epoch of the
   ΛCDM median halo of the default mass, derived below, and the relation's validation is
   read against the contracted halo. Kept for the history. c₂₀₀ = 4.1(1 + z_f)
   applies a normalisation quoted for c_vir to c₂₀₀ without the conversion
   between the two overdensities, and z_f = 2.5 is the midpoint of §3's
   "z ≈ 2–3" rather than a measurement. Across that cited range v_c(R₀) moves
   about 10 km/s — three times acceptance entry 3's error bar. The one check it
   passes is that c₂₀₀ = 14.4 lands inside the 10–18 the Milky Way's own
   measurements span (§4b). **S10 (run 2), measured:** K = 3.5 (c₂₀₀ = 12.25)
   puts v_tan at 247.97, inside row 3's 245–251, and z_f = 2.0 at 248.17; the
   conversion this debt names is on its own the size of row 3's miss, which
   debt #18 attributes to the missing extended component. `halo_concentration`
   and row 1 tell the two apart `[verified: AUDIT_RUN2.md D-4]`.
   **S11, the other two audits' numbers beside this one** — three conversions,
   three numbers, none averaged (rule B12). `session-10-beta` took the
   conversion from the ratio of this model's own R₂₀₀ = 212.94 kpc to the
   255 kpc top-hat radius of debt #10, 1.198, so K = 3.42, c₂₀₀ = 11.98 and
   row 3 reads 246.92 — inside — while the SFR, the gas and stellar masses and
   R_d move by less than one part in 10⁹ `[verified:
   tests/test_halo.py::test_the_conversion_closes_row_3_and_moves_nothing_else]`.
   The gamma pair converted the NFW profile itself at Δ_vir = 101 ρ_crit
   `[recall: Bryan & Norman 1998, Ω_M = 0.3]`: c₂₀₀ = 10.9 (−24%), v_c(R₀)
   243.8 → 230.4 km/s and row 3 at **242.6** — through the window and out the
   other side `[verified: tests/test_audit.py::
   test_debt_12_the_concentration_is_quoted_at_the_wrong_overdensity]`. So the
   correction is worth 8 to 13 km/s depending on what is taken as the
   conversion, and two of the three land row 3 inside 245–251. Three things
   every list agrees on. K and z_f enter only as their product, so no
   measurement of the assembly epoch alone validates the relation `[verified:
   tests/test_halo.py::test_k_and_the_assembly_epoch_enter_only_as_their_product]`.
   The sensitivity this entry quotes is stale: across z_f = 2–3 row 3 spans
   248.2–263.5, 15.3 km/s and five half-widths, not 10 and three, and the epoch
   the row wants, z_f ∈ [1.9, 2.1], lies below the cited range `[verified:
   tests/test_halo.py::test_the_epoch_the_acceptance_table_wants_is_below_the_cited_range]`.
   And the conversion and debt #18's component both lower row 3, so either fix
   alone can overshoot and the two are judged together — against rows 1 and 19
   (this list), rows 2 and 20 (beta), or rows 3 and 19 with z_f set jointly (the
   pair): whichever closes row 3, the others are the check. At K = 3.42 the
   escape velocity at R₀ falls 578 → 565 km/s and `WIND_SPEED` would need a
   refit of about a hundredth of a dex; row 22 stays inside at −0.0563
   `[verified: session-10-beta, DECISIONS.md D95]`.
   **S13, half discharged.** The halo stage converts: `halo_concentration_virial` =
   K(1 + z_f) at Δ_vir(Ω_M) ≈ 101 ρ_crit `[recall: Bryan & Norman 1998]` becomes
   `halo_concentration` = 10.9 through the NFW invariant Δ c³/μ(c) — the gamma pair's
   conversion, computed from the profile rather than recalled or taken from a cited
   radius (D107). Row 3 fell 256.2 → 242.7 km/s and no other row moved by more than
   1e-9 `[verified: tests/test_halo.py::test_the_conversion_moved_row_3_and_nothing_else]`.
   What this debt still holds is the epoch: z_f = 2.5 is the cited midpoint, the row
   wants 2.7–3.1, and choosing it against a known answer is what rule B5 forbids.
   `WIND_SPEED` was refitted to the converted potential, 1010 → 987 km/s (debt #43).
   **S14:** with the halo contracted around the disc (debt #6) the epoch row 3 wants is
   0.7–1.0 (c₂₀₀ = 5.2–6.2), below the cited 2–3 by as much as it was above it before; the
   cited range now spans 264.5–276.7 km/s on the row, 12 km/s, all of it high
   `[verified: tests/test_halo.py::test_the_epoch_row_3_wants_is_below_the_cited_range]`.
   All three S10 conversions were read against an uncontracted halo, and so was every
   epoch the register has quoted; the row's miss is under this debt since S14 (D113).
   **S15, discharged.** The one check the default passed — c₂₀₀ = 14.4 inside the 10–18
   the Milky Way's measurements span — compared unlike things: K is a dark-matter-only
   calibration `[verified: Wechsler et al. 2002, c_vir = c₁/a_c, Ω_M = 0.3, σ₈ = 1.0]`, so
   the concentration it gives is the halo's *before* it contracted around the disc, while
   a measurement of the Milky Way fits an NFW to the halo *after*. The halo stage publishes
   that fit since S15, `halo_concentration_contracted` (the c₂₀₀ enclosing the same dark
   mass inside R₀), and at z_f = 2.5 it reads 18.5 — over the span. So the default is
   derived instead: the ΛCDM median c₂₀₀ for the default mass at z = 0, 8.25 `[verified:
   Dutton & Macciò 2014, log₁₀ c₂₀₀ = 0.905 − 0.101 log₁₀(M₂₀₀/10¹² h⁻¹ M☉), Planck, 0.11
   dex scatter; h = 0.7 here]`, converted to c_vir = 10.92 at Δ_vir and read back through K
   as z_f = 1.66, the scatter spanning 1.08–2.41 and the old 2.5 outside it `[verified:
   tests/test_registry.py::test_the_epochs_default_is_the_lcdm_median]`. The Milky Way's own
   pre-contraction concentration from a contracted fit to Gaia DR2, 9.4 (+1.9/−2.6)
   `[recall: Cautun et al. 2020]`, is z_f = 2.0 (+0.6/−0.9) and brackets it; its local
   dark-matter density, 8.8 × 10⁻³ M☉/pc³, is what the model reads at 1.7. At the derived
   default the contracted fit reads 15.4, inside; row 3 reads 260.1 (the less concentrated
   halo responds *more*, r_i/r_f 1.50, its share at R₀ 119 → 166) and stays a miss under
   debt #11; the advanced model's escape velocity at R₀ falls 585 → 569, inside its 530–580
   `[verified: tests/test_halo.py::test_concentration_from_the_assembly_redshift,
   ::test_the_named_rulesets_and_what_each_is_worth_at_R0]`. What is permanent: K and z_f
   enter only as their product, so the input is the concentration's scatter under another
   name (verdict C, ruling 5) — that is its job, not a defect.
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
   **S10 (beta) put a number on the discharge.** The two routes share no
   constant — one is a fit to the solar neighbourhood with no outflows, the
   other nucleosynthetic yields minus what a wind removes — and they agree to
   10%: y_Z = 0.0406 with 75.32% of fresh metals escaping at R₀ gives an
   effective yield of 0.01001 against the fitted 0.01100 `[verified:
   tests/test_chemistry_dtd.py::test_the_winds_effective_yield_and_the_fitted_one_and_how_far_they_agree]`.
   Agreeing at all is the content of the discharge; the residual 10% is the
   two models' different recycling, recorded rather than tuned away. Both fits
   are provisional on debt #18 (debt #43).
17. **Acceptance rows 20 and 21 have zero-width targets.** The sources quote no
   uncertainty, so the check fails for any float that is not bit-exact. Row 20
   agrees to 6% and still fails. A defect in the table, not the model; the fix
   is to read the source's uncertainty or to give the table a way to say "no
   testable target", which belongs to the S10 audit. **S10 (run 1)**: the
   convergence sweep now reports such rows as *untestable* rather than judging a
   drift against nothing `[verified: galaxy/specs/convergence.py]`; the source's
   uncertainty was not found in the material this project holds, so row 20 stays
   as it is — 28% low on the model and unjudgeable on the table — and the row is
   still red for the right reason (debt #18).
   **S11 chose the second remedy, which two audits had built independently**
   (`session-10-beta` D98, `session-10-gamme-run-2` D97): `spec.Quantity.testable`
   is False for a pointwise row with `lo == hi`, `spec.untestable()` lists such
   rows, the spec report names them once as a table defect and the row's own
   reason says "no testable target — debt #17", a new zero-width row must say
   so in its note or the table refuses it, and row 14 is exempt because an
   ensemble's central interval can contain a point `[verified:
   tests/test_spec.py::test_the_table_says_which_rows_have_no_testable_target,
   ::test_a_new_zero_width_row_cannot_be_added_silently;
   tests/test_audit.py::test_debt_17_the_zero_width_rows_say_no_testable_target]`.
   Nothing is widened and no verdict moves: row 20 still fails, under debt #18.
   The alternative one run took — `session-10-gamma` D95 gave rows 14, 20 and 21
   the half-unit of the source's last printed digit, ±0.5, ±0.05 × 10⁹, ±0.5% —
   is recorded as a named ruleset and not applied (rule B12): an interval
   chosen with the model's answer already known is the move rule B5 exists to
   prevent, whatever its width. The debt stays **open**; what discharges it is
   a citation with an uncertainty, entered before the row is next judged. What
   the same reading of the source found about the target's *accounting* is
   debt #41.
   **S13:** row 14 joins rows 20 and 21 as untestable — a statistical row now passes on
   its median (debt #38), which no float meets at zero width either `[verified:
   tests/test_spec.py::test_the_table_says_which_rows_have_no_testable_target]`.
   **S17: row 14 leaves the list, by the remedy this debt asks for and no other.** The row
   was about to be judged for the first time (the bulge did not exist until S17), so the
   source was read again, and BHG16 does quote an uncertainty for the bulge's dispersion
   where it quotes none for the gas masses: "the rms is σ_rms,b ≈ 113 km/s, to ≈3 km/s",
   mass-weighted within the bulge's half-mass radius `[verified: BHG16 §4.3, read at S17]`.
   The target is now 110–116 and the model fails it at 116.2, honestly. The width is the
   source's verbatim and nothing was chosen: the model's number was already known when the
   source was consulted, and that is recorded in D122 so a reader can weigh it. Rows 20 and
   21 stay, and the debt stays **open** for them — the same reading of Nakanishi & Sofue
   still finds no uncertainty.
18. ~~**No high-angular-momentum accretion component.**~~ **DISCHARGED at S16 — built,
   as the high-j tail of the halo's angular-momentum distribution, and the timescale the
   register wanted for it turned out not to be the decision** (D119; what it leaves is
   debt #47). Kept for the history. With the infall carrying
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
   be judged together. **S10 (run 2):** three cited constants inside their own
   ranges close or nearly close these rows without the component:
   `SF_THRESHOLD` = 10 (the top of its 5–10) gives row 2 = 1.709 and row 20 =
   7.5 × 10⁹ with row 3 unmoved; `baryon_retention` = 0.30 gives rows 1, 2 and 3
   all inside; `GAS_DISC_SCALE_RATIO` = 1.2 gives rows 3 and 4 inside with row
   20 at 7.2 × 10⁹ `[verified: AUDIT_RUN2.md D-3, D-4, D-6]`. The component's
   discriminating prediction is that it closes row 20 with rows 3 and 4
   *unmoved*, which none of the three does. Half of row 2's excess is debt
   #29's Sagittarius gas.
   The gamma pair swept `GAS_DISC_SCALE_RATIO` to 1.5 and read the same trade
   from the other side (debt #45): one broader infall cannot buy rows 3 and 20
   without paying rows 2 and 22, which is the case for a *second* component
   rather than a wider first one.
   **S13:** row 3 is no longer this debt's. With debt #12's conversion done it reads
   242.7, low, so an extended component — which moves baryons outward — would take it
   further from its target; row 3's miss is debt #11's and #6's now. Rows 2 and 20
   remain: with a physical Sagittarius (debt #29) row 2 reads 1.89, and 1.85 with no
   Sagittarius at all, so what is left of its excess is this debt's timescale; row 20
   like for like is 4.17 × 10⁹ M☉ of hydrogen against 8.0 (debt #41), so the component
   must supply about 3.8 × 10⁹ M☉ of hydrogen — 5.2 × 10⁹ of gas.
   **S14:** row 3 is this debt's evidence again, and in the right direction: with the
   halo contracted (debt #6) the row reads 270.8, high, and a component that moves
   baryons outward lowers both their own pull at R₀ and the halo's response to them.
   Rows 2, 20 and 3 pull together now; rows 3 and 4 remain the check that the component
   is high enough in angular momentum. **Probed, not built (D114):** a share s of the
   budget at k R_d on the disc's own inside-out timescale, the halo contracting around
   it, swept over s = 0.1–0.3 and k = 2–5. Every setting lowers row 3 (4–13 km/s from
   the baryons, 1–7 from the halo's weaker response) and lifts row 20 toward 8 × 10⁹,
   and every setting lifts row 2 with it — 1.98 to 2.45 against 1.46–1.84 — because
   gas at 2–5 R_d accreting as the disc does is still above the star formation
   threshold when it arrives; row 4 broadens to 2.55–2.77, inside. The premise that
   the threshold protects the component fails for this form of it: what is wanted
   arrives late or diffuse enough to stay under the threshold, a timescale of its own,
   and that is the decision the next session takes before any constant is swept.
   **S15:** row 3 reads 260.1 with the epoch derived (D117), 9–15 km/s high, and the
   component's 4–13 is half of its prediction with the bulge's 5–8 (debt #11); D114's
   table was read at z_f = 2.5 and is re-read when the component is built.
   **S16, discharged.** The component is derived, not sized: the halo's specific angular
   momentum has a universal distribution, M(< j) = M μ j/(j₀ + j) with μ = 1.25 the median
   `[verified: Bullock et al. 2001, read at S16]`, and mapped onto the plane on the model's
   own rotation curve with its mean j the exponential disc's, it lies below the exponential
   inside 12 kpc and above it outside — the high-j tail the exponential never held, 7.6% of
   the budget, 3.7 M☉/pc² at 15–20 kpc, ending where j_max lands at 25 kpc. The halo stage
   computes it after its first contraction and contracts again around the total (rule A9:
   the profile is held where the halo needs it first); `sfh` adds it to the infall. **The
   timescale was not the decision.** Three arrival laws — the inside-out law from t = 0, the
   same from the assembly epoch, the halo's own growth after it — read the same on every row
   and within 0.05 M☉/yr on row 2, because at 12–25 kpc the inside-out law already accretes
   over 10–20 Gyr; what mattered was the angular momentum, i.e. the radius, and D114's form
   failed on row 2 only because its inner part overlapped the disc's own gas. Rows 3 and 4
   were the check that the component is high enough in angular momentum: row 4 reads 2.49,
   unmoved, and row 3 falls 260.1 → 252.9 (the baryons' pull −4.3, the halo's weaker
   response −2.5 km/s). Row 20 reads 6.24 × 10⁹ of hydrogen (4.17 until S16), row 2 rises
   1.89 → 2.08, and both stay misses: row 2 under debt #44, row 20 under debt #47, which
   holds what this component does not explain `[verified: tests/test_halo.py::test_the_high_j_tail_is_derived_and_where_it_lies,
   tests/test_sfh.py::test_the_tail_is_accreted_and_what_it_moved]`.
19. **The thick disc is too compact and too massive, and the gate passes on the
   cancellation.** Scale length 1.17 kpc against 2.0 (row 5) and mass
   1.07 × 10¹⁰ against 6 × 10⁹ (row 11). Row 9 — S3's gate — reads 0.103 inside
   its 12% ± 4% *only because those two errors compensate*: raising the merger's
   `gas_fraction` to fix the mass drives row 9 to 0.015, because a thick disc
   this centrally concentrated sheds surface density at R₀ far faster than it
   sheds mass `[verified: DECISIONS.md D51]`. Row 5 is the prerequisite — with
   the right extent the mass and the ratio can be right together. If they still
   cannot, the split criterion is what is wrong.
   **S13 moved the numbers, not the shape:** with Sagittarius delivering a physical
   share the pre-merger episode carries half the budget, so the thick disc reads
   1.32 kpc (row 5) and 1.42 × 10¹⁰ M☉ (row 11), and the gate, row 9, reads 0.152 —
   inside 0.08–0.16 by less than the 0.103 it read before, still on the cancellation.
   **S16:** row 7 joins this debt. The high-j tail took 7.6% of the budget out of the
   exponential (D119), the stellar surface density at R₀ fell 51.6 → 47.6 M☉/pc², and the
   thick disc's scale height, at the top of its window on the same cancellation, rose 1042
   → 1126 pc, over 1080; row 9 reads 0.147, row 5 1.27, row 11 1.3 × 10¹⁰. D119's probe of a
   derived Toomre threshold moves row 9 to 0.06 — the thick disc forms from the reservoir
   the threshold holds — so S18 judges rows 2, 5, 7, 9 and 11 together.   **S18 tested the prediction this debt has carried since D51 and killed it by the number.**
   The merger's radial kick is built and derived — the vertical impulse read isotropically,
   turned into a displacement by the epicyclic frequency and the guiding-centre shift,
   ⟨ΔR²⟩ = σ_k²(1/2κ² + 6Ω²/κ⁴) — and it is 1.47 kpc at R₀ but 0.30 at 2 kpc, because the
   inner disc is stiff: row 5 moves 1.18 → 1.51 on the constant threshold, 0.93 → 1.17 on the
   derived one, row 9 by −0.015, rows 7 and 11 not at all (D124). The sweep §5d's gate asks
   for, on the built model (merger share 0.3 → 0.8): row 9 0.135, 0.088, 0.051, 0.024, 0.007,
   0.001 against row 11 1.45e10, 1.21e10, 9.6e9, 7.2e9, 4.9e9, 2.8e9, row 5 never past 1.36 —
   **never inside together; the cancellation is still there**, and with the derived threshold
   (debt #47, which pre-committed this reading) row 9 is red at 0.051 and row 8 with it. Row 7
   leaves this debt for #42: it reads 1260–1370 across every thick-disc shape probed because
   Σ(R₀) is 47.3 M☉/pc² and does not move; it is the dispersion. **Where the shape is decided:**
   the early episode's arrival law (debt #49). With the first infall at ~1 Gyr everywhere, as
   the two-infall framework the inside-out index cites specifies, the pre-merger disc reads
   2.11 kpc; the rest of that probe is under #49. What would land rows 5, 9 and 11 together is
   a thick disc extended *and* light, and at the observed scale lengths and masses row 9 is
   0.11 by arithmetic, so the three rows are one row.

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
   up. `disc_dominance` is published and unused so the gap is visible. **S10
   (run 1) audit finding:** row 15 passes at 4.98 kpc against 5.0 ± 0.2 because
   `BAR_LENGTH_RATIO` was set to 2.0 inside a cited 1.5–2.5 and R_d is 2.49 —
   the pass is a choice of constant, not a prediction, and the row should not be
   read as evidence for the bar model until the first link exists
   `[verified: AUDIT_RUN1.md §3]`.
   Row 15 is `BAR_LENGTH_RATIO × R_d` exactly, 2.0 × 2.49 against 4.8–5.2, so
   whatever debt #18's extended component does to the scale length, row 15
   follows one for one — a check on R_d, not on the bar `[verified:
   tests/test_audit.py::test_row_15_is_the_bar_constant_times_the_scale_length]`.
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
   ~~a `performance.py` question at S10.~~ **Measured at S10 (run 1) and
   discharged in full**: at the published sample size one cell costs 1.1 ms, nine
   2.6 ms and every cell 116 ms, so the catalogue's cost is proportional to the
   stars asked for and nothing is paid for a cell nobody asked about
   `[verified: DECISIONS.md D95]`.
   **S11, the other two audits' reading of the same measurement.** The pruning
   is real in every run — a nine-cell query costs 2.6–2.9 ms, about 2.4% of the
   whole — but the per-cell cost D61 named is not gone. `session-10-beta` fitted
   the catalogue's time against the sample size and found 90% of its 113 ms
   independent of how many stars are asked for (0.59 µs per star): 14.9 ms lays
   out all 1024 cells at 14.5 µs each whether or not anything asks, and 84 ms
   draws in the 516 cells that realise a star, about 163 µs each — D61 right
   about the cost of a realising cell and wrong about who pays it, since 508
   cells cost only their layout draw `[verified: session-10-beta, DECISIONS.md
   D96]`. The gamma pair read ~100 µs fixed per cell against ~2 µs per star and
   put a 0.13 s ceiling on what a lazy catalogue could save `[verified:
   session-10-gamme-run-2, DECISIONS.md D95]`. The discharge stands — nothing
   is paid for a cell a *query* did not ask for — and the trade-off the cell
   grid embodies is debt #36. `performance.py` publishes the fit since S11.

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
   and its inflow are S10 questions; recorded, not clipped (rule B9).
   **S11, from the other audits.** It is not the grid: across N_t from 500 to
   8000 the centre's peak wanders under 0.10 dex and stays above +1.4 while the
   simple model's stays below +0.7 `[verified: tests/test_chemistry_dtd.py::
   test_the_centres_iron_is_the_wind_and_not_the_grid]`, and no acceptance row
   could ever have caught it — debt #34. The gas is above [Fe/H] = +0.5 out to
   2.7 kpc (+1.20 at 1 kpc, +0.27 at 4, just outside row 22's fit range) against
   0.8 kpc in the simple model, and the one fitted constant does not reach it:
   `WIND_SPEED` 800 → 1300 km/s moves the central maximum +1.65 → +1.37 while
   taking the gas at R₀ from +0.15 to −0.17 and row 22 by 0.004 — the constant
   sets the level, not the centre or the tilt `[verified: tests/test_audit.py::
   test_debt_26_the_centre_is_the_missing_mass_loss_not_the_fitted_constant]`.
   Downstream, the centre reaches the planets: 1.2% of the advanced catalogue
   sits above [Fe/H] = +0.5 against 0.02%, giant occurrence inside 1 kpc is
   0.43 against 0.07, and the published sample's giant fraction is 1.65%
   against 1.02% while occurrence at R₀ is 5.0% in both — `PLANETESIMAL_
   EFFICIENCY`'s fit is untouched, its consumer moved `[verified:
   tests/test_audit.py::test_debt_26_the_iron_at_the_centre_reaches_the_planets]`.
   Rule B10's note for the session that adds a mass-loaded wind: `WIND_SPEED`
   was fitted against this massless one and has no claim on its value then;
   the tilt survives a refit, the level does not (debt #43).
   **S13:** the centre came down with the physics around it — peak +1.36 (was +1.53),
   above +0.5 out to 2.5 kpc; the simple model's gas no longer reaches +0.5 anywhere
   (peak +0.46). Sagittarius' early gas and the unconverted potential were part of the
   excess; the massless wind is the rest.   **S18: the centre halved, for a reason that is not the wind's.** The derived threshold
   (debt #47) rises with κ inside — 47 M☉/pc² at 2 kpc, 72 at 1, 589 at the first cell — so the
   innermost disc holds a gas reservoir it never had (1.5e9 inside 4 kpc against S17's 0.4e9)
   and the same metals sit in far more gas: the advanced peak 1.39 → **0.70** dex, super-solar
   out to 1.9 kpc rather than 2.66, the peak at 0.5 kpc rather than the first ring (which never
   crosses its threshold); the simple 0.46 → 0.25. The occurrence inside a kiloparsec 0.36 →
   0.25 and the catalogue's metal-rich share 0.010 → 0.005 (D124). The massless wind is still
   the mechanism this debt names; the reservoir is the bar's absence (#21) and is #47's.
   **S20 probed the wind's mass, and it is the one mechanism that opens a valley at no new
   constant — at the cost of the budget** (D128). Read as the same energy-driven wind whose
   metal loading the model already has, the mass loading is the escape fraction's own odds,
   η(R) = f_esc/(1 − f_esc) = (`WIND_SPEED`/v_esc)^`WIND_INDEX`, 2.3 at R₀. On the fast first
   infall it ends the thick-disc phase by consumption (the depletion time at R₀ falls 1.4 →
   0.4 Gyr) and reads `bimodal_wide` at dip 0.59–0.72 — but the α-rich "mode" is the plateau
   spike (split 0.23; #27), and the wind ejects 60% of the budget the halo says the disc
   retained: row 2 0.4–0.7, row 3 214–224, row 10 0.9–1.4e10, the advanced row 6 770–1090. It
   cannot be built by re-normalising the accreted budget, because the retained mass is then a
   fixed point across checkpoints 1 and 3 — the halo contracts around it (rule A1) — and the
   chemistry's `kept` fraction already removes the same wind's metals, so a mass-loaded wind
   on top double-counts them until the two are one wind (rule B10 on `WIND_SPEED`). Ruled for
   S22: the honest statement is that the disc's retained fraction (`baryon_retention`, an
   input) is what the wind decides, and the model has it the other way round.

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
   thick disc is the merger's and its rows read as before.
   **The prediction ran at S10 (the gamma pair) and held in part** `[verified:
   tests/test_audit.py::
   test_debt_27s_prediction_ran_a_fast_inner_disc_opens_a_valley_and_closes_row_22_doing_it]`.
   With the default merger list, inside-out indices of 2 and 3 at τ₀ = 7 and
   1 Gyr all stay `single`. With Gaia-Enceladus alone a fast inner disc *does*
   open the valley — n = 3 with the merger delivering 0.2 of the budget at
   τ₀ = 7, or n = 3 at τ₀ = 1 with the default 0.5: depth 0.57–0.64, valley at
   [α/Fe] ≈ +0.40, row 24 `bimodal_wide`, rows 5, 7–11 computable — and what
   they read is the simple model's compact thick disc again: 6.6 × 10⁹ M☉ (row
   11, in), 0.71 kpc (row 5, far out), 1113 pc (row 7, just over), ratio 0.011
   at R₀ (row 9, an order of magnitude low), thin disc 443 pc (row 6, out)
   `[verified: tests/test_audit.py::
   test_the_thick_disc_a_valley_would_find_is_the_simple_models_compact_one]`.
   What it costs is row 22: every such galaxy has a present-day gradient of
   −0.13 to −0.14 dex/kpc, twice the observed, because τ(4 kpc) is then under a
   gigayear. The valley and the gradient are not both reachable through the
   inside-out index; the default stays n = 1 and the conflict is preserved
   (rule B12). So the DTD's long tail is not the whole story: the two modes are
   there once the inner disc is fast enough, and what is missing is a
   mechanism that makes the inner disc fast without steepening the infall law
   everywhere — the bulge and its inflow, the question debt #26 names. Two traps
   for whoever picks this up. At N_t = 8 the advanced model reports a valley: a
   coarse time grid manufactures exactly this signal, so a `bimodal` verdict is
   worth nothing until its grid is stated `[verified: tests/test_chemistry_dtd.py::
   test_a_coarse_time_grid_manufactures_the_valley_debt_27_is_looking_for]`. And
   the detector's `DIP_DEPTH = 0.5` decides row 24 for S9's best input vector —
   a dip of 0.384 reads `single` at 0.5 and 0.4 and `bimodal_wide` at 0.3 —
   though at the default the dip is 0.0 and no threshold matters `[verified:
   AUDIT_RUN2.md §4.5]`.
   **S13:** with the default merger list a fast inner disc — n = 3 at τ₀ = 1 Gyr — now
   opens the valley (`bimodal_wide`, depth 0.64); until S13 Sagittarius' unphysical
   share arriving beside Gaia-Enceladus kept that track single `[verified:
   tests/test_audit.py::test_debt_27s_prediction_ran_a_fast_inner_disc_opens_a_valley_and_closes_row_22_doing_it]`.
   n = 2, and n = 3 at τ₀ = 7, stay single; the price in row 22 is unchanged.   **S18: the valley reopened on the default merger list, and the fast first infall alone
   does not open it.** With the derived threshold (debt #47), a fast inner disc — τ₀ = 1 Gyr
   at n = 2 *and* n = 3 — reads `bimodal_wide` with dips 0.57 and 0.64 and the split at 0.39
   (S17 had closed the one setting, n = 3, that opened it), at τ₀ = 7 neither does, and the
   row-6 cost is 700 pc there; the single-merger probes read as before (0.56–0.64). The
   threshold holds the inner disc's gas high and the second infall restarts the sequence from
   a diluted start, which is this debt's own mechanism. Probed for S20 and not built: a first
   infall on its own short timescale (debt #49) reads a dip of 0.15 at most on the default
   list, with the advanced row 6 at 720 (D124). S20 has two levers where the record said one.
   **S20: neither lever, and every valley this detector has found is the plateau spike**
   (D128). The [α/Fe] mass at R₀ was decomposed by birth epoch, radius and time: the early
   population is 75–100% migrants born inside 6 kpc and is spread *evenly* from +0.2 to +0.45
   (no bin above 3% of the mass, against 18% in the thin mode's), because dN/d[α/Fe] =
   Ψ/|d[α/Fe]/dt| and in a threshold-regulated Kennicutt disc fed from t = 0 the star formation
   rate is already falling while the α-fall runs. Probed, the repo unchanged, at the default
   grid and across N_t = 1000–4000: the first infall on 0.1/H(z_f) (dip 0.15; #49), a compact
   early disc at R_d(z_f) (0.00, row 22 −0.147), Wechsler's M(a) as the rate (no thick disc),
   the switch's width (0.19), a bar-driven drain of the inner disc (a valley at split 0.37 and
   row 10 halved), the mass-loaded wind (split 0.23, the budget gutted; #26). **The S13/S18
   valleys (τ₀ = 1, n = 2–3, split 0.39) and both new ones are the stars formed before any Ia
   iron: +0.45 exactly, 5–7% of the mass, the split above the α-rich sequence itself, the
   early population a plain beneath it** `[verified: tests/test_audit.py::test_debt_27_every_
   valley_the_detector_has_found_is_the_plateau_spike]`. The S9 prediction is replaced:
   a thick mode near +0.3 needs the first phase's star formation to rise on gas-rich material
   and be cut within ~1 Gyr — a burst — which no accretion law gives under a constant-efficiency
   Kennicutt law (the reading #47 and #49 reached from rows 5, 9 and 11); if a mechanism ends
   the first phase sharply and there is still no mode short of the plateau, the DTD's minimum
   delay (0.15 Gyr, a δ-spike at +0.45 by construction) is what the detector reads. Row 24
   and the six rows on it stay misses with that prediction; the advanced row 6 reads 356.

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
   gradient measured at 10 Gyr decides between them. **S10 (run 2):** the
   framing "once the tilt is right" is wrong — the simple model over-flattens by
   the same ratio (3.18) with the tilt wrong, and S3's own test pinned it
   `[verified: tests/test_chemistry.py::test_migration_over_flattens_the_old_population;
   AUDIT_RUN2.md D-2]`. One kernel over-flattening two different old-gas
   gradients by one factor favours the first explanation: the citation's width
   is not this kernel's width.
   **Measured in both models at S10 (the gamma pair)** `[verified:
   tests/test_audit.py::
   test_debt_28_migration_flattens_the_old_population_from_a_steeper_start_in_both_models]`:
   with no migration the old population's gradient is −0.105 in the simple
   model and −0.129 in the advanced one (the young: −0.020 and −0.062); the
   default kernel takes the old one down by a factor 16 and 7, and the
   young/old ratio lands at 3.2 and 3.1 — the 3.18 and 3.09 above, from a
   different probe. A gradient measured at 10 Gyr near −0.04 would convict the
   width in both models at once; one near −0.13 would say the width is right
   and the old stars' starting point is not.
   **S13:** the unmigrated old gradient is −0.084 (simple) and −0.106 (advanced) now,
   flattened 13× and 5.5× by the default kernel; the young/old ratio 3.27 and 3.03. The
   discriminator stands.
29. ~~**The Sagittarius default delivers a tenth of the baryon budget, five Gyr
   early.**~~ **DISCHARGED by S13.** The default is 0.01 of the outstanding budget —
   about 3 × 10⁸ M☉, what a 10⁸–10⁹ M☉ progenitor can bring `[recall]` — and with debt
   #30's fix its gas arrives around 8.8 Gyr. **The prediction ran and failed**: row 2
   reads 1.89 at 0.01 and 1.85 with no Sagittarius at all, not the 1.837 the step model
   gave, so the residual excess is debt #18's timescale after all, as this entry said it
   would then be (D106). What else moved: rows 5, 9 and 11 (debt #19), the advanced row 6
   to 358 pc (debt #42), the centre (debt #26). The S10 finding, kept:
   `MergerEvent(8.8, 0.02, 0.2)` took 0.2 of the budget outstanding
   after Gaia-Enceladus, 0.1 of the whole, 5.9 × 10⁹ M☉ — more gas than the
   progenitor's entire mass [recall: 10⁸–10⁹ M☉] — and `sfh` starts it at the
   *last major merger*, 3.8 Gyr, because it reads only the total share and the
   major onset; a minor event's `time` reaches nothing that survives. Without
   the event row 2 reads **1.837, inside 1.46–1.84, in both models**, row 8
   0.037 and row 9 0.150 (inside), row 20 5.66 × 10⁹, row 11 1.38 × 10¹⁰
   `[verified: AUDIT_RUN2.md D-7]`. Not corrected by the audit: a registered
   miss that starts passing fails the spec run, so the default and the row-2
   entries (both models) must change in one commit. **Prediction:** with
   Sagittarius carrying ≤ 1% of the budget, row 2 passes in both models; if it
   does not, debt #18's timescale explanation is the whole story after all.
   Read like for like (debt #41), the 5.66 × 10⁹ here — and every row-20 number
   in this register — is hydrogen plus helium against a hydrogen target.
30. ~~**`MERGER_DURATION` is dead; the merger's gas arrives as a step.**~~ **DISCHARGED
   by S13.** `sfh` accretes the merger-delivered gas from `merger_delivery` — each
   event's share over its own window at its own epoch — with the exponential's own
   recursion, normalised on the grid so the budget closes to rounding. **The prediction
   held**: rows 1 and 10's movement with N_t went from 0.22% and non-monotone to 0.007%
   and monotone `[verified:
   tests/test_sfh.py::test_the_merger_gas_arrives_at_its_own_epoch_and_the_grid_no_longer_sees_a_step]`.
   The S10 finding, kept: `assembly`
   spreads each event over a Gaussian window and publishes `merger_delivery`;
   nothing reads it; `sfh` rebuilds the second episode as an exponential from a
   step at the last major merger. 0.1–2.0 Gyr changes every acceptance scalar
   by ≤ 3 × 10⁻¹⁵ `[verified: AUDIT_RUN2.md D-1]`. The constant's about line
   describes the timestep dependence the step *has*: rows 1 and 10 are
   non-monotone under N_t at 0.2% (AUDIT_RUN2.md C2). **Prediction:** feeding
   `merger_delivery` into `sfh` removes that non-monotonicity.
31. ~~**The catalogue does not migrate.**~~ **DISCHARGED by S19** (D126). `systems`
   drew radii from the unmigrated `stellar_surface_density` and looked abundances up at
   that radius and birth time, so the advanced model's migrants reached neither the viewer
   nor the planets: the catalogue's [Fe/H] spread at R₀ was 0.19 dex against the
   chemistry's own 0.30 at S10 `[verified: AUDIT_RUN2.md D-11]`, and 0.299 against 0.360
   by S18. A star's birth radius **and birth time** are now drawn together from the
   chemistry's own backward weights — born(R_b, t_b) × K(R_b → R_now), the product
   `chemistry_dtd` already wrote inline — and the abundance is read there. The catalogue's
   spread at R₀ reads **0.361** against `feh_spread_sun` **0.360**
   `[verified: tests/test_systems.py::test_the_catalogue_carries_the_chemistrys_own_spread_at_the_sun]`,
   and it reproduces `feh_stars_young` and `feh_stars_old` at R₀ by sampling where the
   chemistry convolves, in both models. **What the half-rule was worth, measured before the
   build:** the birth *radius* alone, with the birth time still drawn from the local birth
   rate, reads 0.273 — narrower than doing nothing. The birth-time marginal of the stars
   now at R₀ is itself a migrated quantity, and it is most of the answer. `star_birth_radius`
   is published so the churning can be seen: 84% of the stars at R₀ were born inside it,
   mean birth radius 5.4 kpc. What it moved: R₀ mean age 5.7 → 7.3 Gyr (advanced) and
   6.0 → 7.3 (simple), R₀ [Fe/H] mean −0.33 → −0.25 and −0.27 → −0.18, the R₀ thick
   fraction 0.049 → 0.221 in the simple model with the thick disc's *total* unmoved
   (0.2516 → 0.2535) — which is debt #50 — and the two models' giant-fraction contrast
   1.58 → 1.25 (debt #26's sample instrument, re-pinned). Rows 6 and 7 are still judged
   together when debt #27's valley opens (debt #42); nothing here reaches them.
32. **The local [Fe/H] spread is the age–metallicity relation, not migration.**
   §8's "without migration the local metallicity distribution comes out far
   too narrow" is refuted by the model built to show it: `feh_spread_sun` is
   0.294 dex with `migration_efficiency` = 0 and 0.299 at 3.6 `[verified:
   AUDIT_RUN2.md D-8]`. The field's about line and the test named for the
   mechanism overstate it; §8's claim needs a re-ruling.
   **S18** made the sign explicit rather than merely small: 0.370 without migration and
   0.360 with, so the kernel *narrows* the local distribution — the migrants reaching R₀
   carry narrower age–metallicity relations than the local one `[verified:
   tests/test_chemistry_dtd.py::test_the_solar_neighbourhood_has_a_spread_and_migration_makes_it]`.
   **S19: the spread was the wrong observable to have argued over** (D126). With the
   catalogue drawing birth places from the same kernel, migration turns out to dominate
   the solar neighbourhood on every statistic except the one §8 named: 84% of the stars
   at R₀ were born inside it and their mean birth radius is 5.4 kpc, the mean age at R₀
   rises 5.7 → 7.3 Gyr and the mean [Fe/H] rises 0.08 dex. A spread is a second moment of
   a mixture and two shifted narrow components make a wide one look unchanged; the mean
   and the birth-radius distribution separate the hypotheses and the dispersion does not.
   So §8's re-ruling should replace "the local metallicity distribution comes out far too
   narrow" with the claim migration actually makes here, and the falsifiable statement is
   the one debt #28 already holds: at `migration_efficiency` = 3.6 the Sun's neighbours
   come from too far in, and that is the same number the young/old gradient ratio rejects.
33. **The advanced model's total metallicity has its own zero point.** Z(R₀)
   reads 1.24 Z☉ where [Fe/H] = 0.00: core-collapse metals are taken in solar
   proportion to oxygen (which already holds the Sun's whole iron) and the Ia
   iron-peak is added on top with a factor 2.0 that lives in the code, not the
   register `[verified: AUDIT_RUN2.md D-10]`. No stage reads Z in the advanced
   model today; the first consumer of `metallicity_history` inherits it. **S12:**
   the factor is registered — `IA_METAL_TO_IRON` = 2.0 `[recall]` in
   `galaxy/models/advanced.py`, read by `chemistry_dtd` `[verified:
   tests/test_chemistry_dtd.py::test_the_ia_metal_to_iron_factor_is_a_registered_constant]`.
   The zero point itself — whether an Ia's whole ejecta should count twice its
   iron toward Z, and what 1.24 Z☉ means for the first consumer — is what this
   debt still holds.
34. **The acceptance table reads nothing inside 4 kpc, so the model's worst
   number is invisible to it** (S10, beta). The gradient rows are fitted over
   R = 4–12 kpc; rows 3, 6 and 8 are evaluated at R₀; rows 1, 10, 11, 19 and 20
   are integrals over the whole disc. Nothing reads a *value* in the inner
   disc, which is exactly where debt #26's [Fe/H] = +1.5 lives — a full dex
   above what real bulges reach, on 7 annuli of the default grid, and every
   acceptance row passes over it `[verified:
   tests/test_chemistry_dtd.py::test_no_acceptance_row_reads_the_disc_inside_four_kiloparsecs]`.
   The table was assembled from BHG16's summary quantities, which are the ones
   the Milky Way is *measured* in, so this is not an oversight so much as an
   inherited shape — but it means the table cannot be read as covering the
   model. **Prediction, stated so it can fail:** a single row on the central
   metallicity would have caught debt #26 at S9 rather than S10, and if adding
   one turns out to catch nothing the model does not already record, then the
   inner disc really is only wrong in the one way debt #26 names.
35. ~~**The vertical grid buys nothing and quietly moves a published field**~~
   **DISCHARGED by S12.** `escape_velocity` reads `halo_potential_midplane`,
   Φ(R, 0) exactly, which the halo stage now publishes beside Φ(R, z); N_z moves
   no published field `[verified: tests/test_chemistry_dtd.py::
   test_the_midplane_escape_velocity_is_at_the_midplane_and_does_not_move_with_n_z]`.
   Whether the z axis should exist at all, with one rendered field and no
   consumer left, is debt #36's question. The S10 finding, kept: (S10, beta). `halo_potential` is the only field on the z axis, and its only
   consumer — the advanced chemistry's escape velocity — reads column 0. So N_z
   is not a quality knob for anything the acceptance table can see: not one row
   moves by even a thousandth of its target's width at any N_z, including
   N_z = 1, where the single sample sits 2.5 kpc above the plane `[verified:
   session-10-beta, tests/test_convergence.py::test_n_z_moves_no_acceptance_row_at_any_resolution;
   AUDIT_RUN2.md C5]`. Two consequences. The scale heights of rows 6 and 7 are
   computed analytically by the vertical stage and are not fitted to a z
   profile, which is worth knowing before anyone reads them as a
   vertical-structure measurement. And `escape_velocity` is *declared* as the
   midplane escape speed while being evaluated at z = z_max/(2 N_z) — half a
   cell above the plane, at a height set by a grid knob. Measured, because the
   size is the whole question: the innermost annulus moves 1.03 km/s in 725
   between N_z = 15 and 960, under 0.2%, because the NFW potential is nearly
   flat near r = 0 `[verified:
   tests/test_chemistry_dtd.py::test_the_midplane_escape_velocity_is_half_a_cell_above_the_midplane]`.
   The fix is one line — evaluate the potential at z = 0 rather than at the
   first cell centre — recorded rather than made.
36. **The default grid is far finer than any acceptance row can detect, and
   nothing records what it is sized for** (S10, beta). N_R = 400, N_t = 2000,
   N_z = 60. Swept one knob at a time, the worst any acceptance scalar drifts
   against the default is **0.056 of its own target's width**, in either
   model; the drift-exceeds-width criterion first fires below N_R ≈ 16 and
   N_t ≈ 25, and never for N_z `[verified: session-10-beta, DECISIONS.md D94
   and tests/test_convergence.py::test_the_criterion_can_fire_and_is_shown_to;
   D94 and AUDIT_RUN2.md §1.2 here]`. So the default is about 25× finer in
   radius and 80× finer in time than the table requires, and the justification
   must be the *rendered fields* — a profile plotted at 16 annuli is not a
   profile — which is nowhere written down. **This is not a proposal to
   coarsen the grid**: the acceptance table is 24 scalars and the viewer draws
   arrays. It is that the number nobody can defend is the one that will be
   changed by accident. D61's cell grid is the same shape of question one
   level down, and cannot be re-measured at all without editing the source,
   because `CELL_RINGS` and `CELL_SECTORS` are module constants and one of them
   is bound into a default argument; what the catalogue's fixed cost is, per
   cell and in total, is now published by `performance.py` (debt #24).
37. ~~**A per-stage or per-route cold profile bills a process-wide one-off to
   whichever stage triggers it**~~ **DISCHARGED by S12.** `performance.py` measures
   the one-off alone (S11, D101), and `tools/timings.py` now probes the RNG after
   each route's cold request and stars the routes whose cold number carries the
   first draw, with a footer saying what the star means `[verified:
   tests/test_timings.py::test_a_metadata_route_does_not_pay_the_first_draw_and_the_table_says_which_do]`.
   Nothing is subtracted (rule B6): the column is labelled, not corrected. The S10
   finding, kept: (S10, beta). The first `seeds.rng` call in a
   fresh interpreter costs about 9 ms; every one after it costs 0.02 ms, a
   factor of several hundred. The `pattern` stage is the first stage of both
   models to draw, so it reads at 30–50× cold-over-warm in the profile and is
   not a 9 ms stage `[verified: session-10-beta, DECISIONS.md D97; AUDIT_RUN2.md
   P1]`. `performance.py` now measures the one-off in its own interpreter and
   publishes it beside the table (S11). **`tools/timings.py` has the same term
   in its cold column and does not say so**: whichever route first reaches a
   seeded stage carries those milliseconds, which are not the route's — 11% of
   `arrays: one profile`, 2% of `adv: one sector`. Not corrected there, because
   subtracting a measured constant from a published measurement is the sort of
   tidying that outlives its justification (rule B6); recorded so the column
   can be read.
38. ~~**A statistical row tests overlap, not agreement, and its ensemble is too
   small for the interval it quotes**~~ **DISCHARGED by S13.** A statistical row passes
   when the ensemble's median lies in the target; `ENSEMBLE_MIN` = 41, the smallest n
   at which the central 95% excludes one draw at each end, and the interval is
   published beside the verdict `[verified:
   tests/test_spec.py::test_a_statistical_row_is_judged_on_its_median_not_on_its_reach,
   ::test_the_ensemble_size_and_the_central_fraction_agree_since_s13]`. Rows 16 and 17
   pass on their medians as this entry said they would; row 14 is untestable at zero
   width (debt #17). The S10 finding, kept: (S10, beta). Two defects in one
   criterion.
   - `evaluate` passes a statistical row when the ensemble's central interval
     **intersects** the target, so it asks whether the distribution *reaches*
     the observation rather than whether it is centred on it. Measured against
     row 16's target of [34, 52]: a median of 60 passes on a spread of ±20, and
     a median of 100 passes on ±60. **A noisier model is monotonically easier
     to pass** `[verified:
     tests/test_spec.py::test_a_statistical_row_tests_overlap_and_not_agreement]`.
   - `ENSEMBLE_MIN = 20` and `CENTRAL = 0.95` do not agree with each other.
     `np.percentile` interpolates, so at n = 20 the 2.5th percentile sits at
     order-statistic index 0.475 — between the smallest and second-smallest
     draw — and the "central 95%" interval therefore trims no whole draw. It
     is 91% of the full range and is set by the two most extreme values in
     each tail, the highest-variance statistics in the sample. **n would have
     to be 41** for the nominal fraction to exclude one draw at each end
     `[verified:
     tests/test_spec.py::test_the_ensemble_size_and_the_central_fraction_do_not_agree]`.
     The consequence is visible: across five disjoint blocks of twenty seeds
     row 16's upper endpoint moves 50.2 → 59.8, more than half its target's
     whole width, while its median moves only 39.5 → 42.5 `[verified:
     session-10-beta, DECISIONS.md D102]`.
   **Not changed**, because what a statistical row *means* is a decision and
   not an implementation defect — the docstring already says a later session
   may revise it. What makes the revision cheap is recorded instead: **both
   live rows would still pass under "the median lies in the target"** (row
   16's medians span 39.5–42.5 against [34, 52], row 17's 5.68–6.15 against
   [4.5, 7.0]), so tightening the criterion costs no verdict today. Rows 13,
   14 and 18 are not-yet-computable and will be judged by whatever this
   becomes.
39. **The seed ensemble is a diagonal, and one of its four dimensions is inert**
   (S10, beta). `spec.ensemble` builds member k by setting *every* seed to k,
   so twenty members sample the diagonal of a four-dimensional space rather
   than the space — an interaction between two seeds is invisible to every
   statistical row by construction. Harmless today and measured to be: no
   published quantity depends on more than one seed, and row 16 is identical
   whether `pattern_seed` moves alone or all four move together. Separately,
   **`world_seed` is read by no stage of either model**; its declaration says
   it seeds "the residual draws of stages 1–3 (e.g. the M_• residual of ruling
   10)" and no such stage exists, so it describes a future rather than the
   model `[verified:
   tests/test_spec.py::test_world_seed_is_read_by_no_stage_of_either_model,
   ::test_the_ensemble_samples_the_diagonal_of_seed_space]`. `graph` reports it
   unbound rather than failing, which is deliberate — but the ensemble varies
   it anyway. Both bite at the same moment: the bulge rows (13, 14, 18) debt
   #8 is waiting on are precisely the ones that would read `world_seed` beside
   another.
   **S17 discharged the second half: `world_seed` is live.** The `nucleus` stage reads
   it for the M_• residual — the exact use its declaration named — and it binds at
   checkpoint 1, which is its own hypothesis, so no input of either model is unbound
   any more `[verified: tests/test_spec.py::test_world_seed_is_live_and_every_declared_
   seed_is_bound, tests/test_graph.py::test_production_graphs_hold]`. What S17 found
   about the other half is that the moment did not arrive after all: rows 13 and 14
   came out **derived**, not seeded — the spheroid's mass and dispersion are determined
   — so only row 18 reads `world_seed`, and no published quantity depends on two seeds
   yet. The diagonal stays a diagonal and this debt stays **open** for that.
40. ~~**`determinism.check_reproducible` runs the model twice in one interpreter**~~
   **DISCHARGED by S12.** `determinism.check` and `report` also run each production
   model in two fresh interpreters under two `PYTHONHASHSEED`s and compare every
   field's bytes, so `python -m galaxy.specs` carries the stronger check `[verified:
   tests/test_determinism.py::test_the_spec_checks_reproducibility_across_processes_too]`.
   The S10 finding, kept: (S10, beta). Everything a process holds fixed — `PYTHONHASHSEED`, set and
   dict iteration order, the allocator, module-level caches — is constant
   across that comparison, so a field depending on any of them passes it every
   time. That is rule B3 exactly: the check takes the one path immune to the
   defect, and it is the same argument rule C2 already makes about testing the
   working copy you pushed from. **Measured, and the model meets the stronger
   standard**: identical field bytes and identical stage order across three
   processes at `PYTHONHASHSEED` 0, 1 and 12345, for all 91 simple and 101
   advanced fields `[verified:
   tests/test_determinism.py::test_the_model_is_reproducible_across_processes_too]`.
   So this is a latent hole in an instrument rather than a live defect, and the
   suite now closes it; what is still true is that `python -m galaxy.specs` —
   the report a session actually reads — carries only the weaker check. The
   fix is to run the second comparison in a subprocess, as `performance.py`
   already does.
41. ~~**Acceptance row 20 compares total gas with a hydrogen mass**~~ **DISCHARGED by
   S13.** `HELIUM_MASS_FRACTION` = 0.27 `[recall]` is a Level 0 constant, `sfh`
   publishes `hydrogen_mass_30kpc` = (1 − Y) × gas, and row 20 reads it: 4.17 × 10⁹
   against 8.0, a 48% miss `[verified:
   tests/test_audit.py::test_debt_41_row_20_compares_total_gas_with_a_hydrogen_mass]`.
   The prediction held — the row misses by half — and debt #18's component is judged
   against that. The S10 finding, kept: (S10, the gamma pair — found by no other run). The target, 8.0 × 10⁹ M☉, is HI plus
   H₂ from 21 cm and CO column densities — hydrogen, with no helium correction
   anywhere in the source `[verified: arXiv:1511.08877 §3, §4.2]` — and
   `gas_mass_30kpc` is every retained baryon the star formation law has not
   consumed, helium included: nothing in either model names helium, so nothing
   takes it out. Read like for like — the model's hydrogen at Y ≈ 0.27 by mass
   `[recall: solar]`, or the target at 8.0/(1 − Y) = 1.1 × 10¹⁰ — the shortfall
   is **47%, not 28%** `[verified:
   tests/test_audit.py::test_debt_41_row_20_compares_total_gas_with_a_hydrogen_mass]`.
   Row 21's 89 : 11 is a hydrogen split and is unaffected. Consequences,
   recorded rather than fixed: debt #18's extended accretion component has to
   supply about 5 × 10⁹ M☉ of hydrogen, not 2 × 10⁹; `baryon_retention`'s
   "reconciles row 1 with row 20" argument used the hydrogen number for a
   total, so the budget it justifies is 3% low; and every row-20 reading in
   this register (debts #18, #29, `SF_THRESHOLD` = 10's "6% low") is the
   table's reading, not the like-for-like one. **Prediction:** the table gains
   a helium fraction as a Level 0 constant or the row reads a hydrogen field;
   either way row 20 then misses by half, and debt #18's fix is judged against
   that.
42. **Row 6 passes at the edge of its window in both models, for opposite
   reasons, and the heating constants calibrate different rows in each** (S10,
   the gamma pair; `AUDIT_RUN2.md` §5 had it as "fitted; fragile" in the
   simple model alone). The thin disc's scale height at R₀ reads 253 pc in the
   simple model (floor 250) and 326 in the advanced one (ceiling 350).
   `SECULAR_HEATING` was set from the 10 Gyr end of the age–velocity relation
   (D54); 20 km/s fails the simple model low (176 pc) and 30 fails the advanced
   one high (429), while 30 leaves the simple model inside at 347.
   `MERGER_HEATING` was scaled so the merger leaves the pre-existing disc at
   ~30 km/s and makes the simple model's thick disc — row 7 runs 616 → 1745 pc
   across 60–180 km/s with row 6 untouched — but the advanced model has no
   thick disc for the heated stars to belong to (debt #27), so the same
   constant moves *its* row 6, 287 → 392 pc, and 52 pc of the default 326 is
   the merger's (274 without) `[verified: tests/test_audit.py::
   test_debt_42_row_6_is_at_the_edge_of_its_window_in_both_models]`. A
   constant fitted to make one population thick is holding a different row in
   the other model, within 24 pc of its edge (rule B10); `AUDIT_RUN1.md` §3's
   "no row reads the kick" in the advanced model was wrong — row 6 does.
   **Prediction:** when a valley opens in the advanced model (debt #27), its
   row 6 falls toward the simple model's 253 — the bimodal probe under debt
   #27 reads 443 because its thin disc is still carrying most of the heated
   stars — and rows 6 and 7 then have to be judged together, with both heating
   constants re-examined against both.
   **S13:** the advanced row 6 crossed its ceiling — 358 pc — the moment Sagittarius
   stopped delivering a tenth of the budget as young gas (debt #29), and is a recorded
   miss. `SECULAR_HEATING` 20 → 177 pc (simple), 30 → 466 (advanced); `MERGER_HEATING`
   60–180 → 303–451 on the advanced row 6, 619–1747 on the simple row 7 `[verified:
   tests/test_audit.py::test_debt_42_row_6_is_at_the_edge_of_its_window_in_both_models]`.
   The rule stands: rows 6 and 7 judged together, both constants re-examined, when the
   valley opens.
   **S17: the simple model's row 6 crossed to the other edge and the advanced one went
   further out.** The spheroid takes 13% of the budget out of the disc, Σ(R₀) falls and
   h_z = σ²/2πGΣ rises: the simple row 6 went 275 → 321 pc (it entered this debt at 255,
   24 pc off the *floor*, and is now 29 pc off the ceiling) and the advanced 384 → 439.
   Neither heating constant was touched. That is the debt's own point made twice over —
   this row has been inside for four sessions and never for a stable reason — and it
   sharpens the rule rather than changing it: when S20 opens the valley, rows 6 and 7 are
   judged together at whatever Σ(R₀) the disc has *then*, and a row 6 that lands must be
   shown to land on σ_z rather than on the surface density it divides by.   **S18: row 7 is this debt's, and one setting lands rows 6 and 7 together.** The simple
   model's row 7 reads 1260–1370 pc across every thick-disc shape S18 probed — Σ(R₀) is 47.3
   M☉/pc², what is observed, and does not move — so the row is the dispersion: 40.4 km/s, of
   which 30 is `MERGER_HEATING`'s kick in quadrature with 27 of secular heating over 11 Gyr,
   against an observed thick-disc σ_z of ~35 (958 pc at the same Σ). **`MERGER_HEATING` = 60
   reads row 7 at 751 and the advanced row 6 at 346, both inside**, the first setting of
   either constant to land the two rows together (180 reads 2148 / 429; 96 reads 1027 / —).
   The derived threshold moved the advanced row 6 439 → 373 on its own (more gas at R₀). Not
   set at S18: the rule stands that both constants are re-examined together when S20 opens the
   valley, and S20 now has this number to start from (D124). Rows 6 and 7 re-attributed in
   `spec._MISSES`: row 7 under this debt since S16's number.
   **S20, judged: `MERGER_HEATING` 120 → 88.8, derived; `SECULAR_HEATING` stays at 25** (D128).
   The valley did not open (#27), so the rule was applied without it. The constant's about line
   said it was scaled so the merger "leaves the pre-existing disc at about 30 km/s" — as if the
   kick were the whole dispersion — while the assembly stage composes it in quadrature with the
   secular heating and the birth dispersion, 27.06 km/s over the thick population at R₀; net of
   that, the observed σ_W = 35 `[recall: Bensby, Feltzing & Lundström 2003]` needs √(35² −
   27.06²) = 22.2 km/s, and 22.2/0.25 = 88.8 `[verified: tests/test_audit.py::test_debt_42_the_
   merger_kick_is_the_observed_dispersion_net_of_the_secular_heating]`. Row 7 reads **962**,
   inside, off the miss list with the reason; the advanced row 6 373 → **356**, 6 pc over, the
   heated old population counted as thin (#27). `SECULAR_HEATING` is bracketed by its own row:
   20 reads the simple row 6 at 228 and 30 at 451, both out (252 and 483 in the advanced). Not
   taken: 60, which lands rows 7 and the advanced 6 together (751 / 346) and is a sweep. The
   cost: the radial kick 1.47 → 1.09 kpc at R₀, row 5 1.17 → 1.09, row 9 0.051 → 0.0455, row 8
   0.013 → 0.016 — and row 3 251.03, out by 0.03, back under #11. Rows 6 and 7 are now inside
   together in the simple model on a cited number; in the advanced model both are #27's.

43. **`NET_YIELD` and `WIND_SPEED` are each fitted on the star formation
   history that misses rows 2 and 20** (S10, the gamma pair). Both set the
   present-day gas at R₀ solar (debt #16, D89), and both were fitted with no
   extended accretion component (#18); whatever that component does to the
   infall at R₀ moves them. Levers, measured so the re-fit is one line: +10%
   `WIND_SPEED` is −0.064 dex at R₀, +10% `NET_YIELD` is +0.041 dex
   `[verified: tests/test_audit.py::test_debt_43_the_two_solar_calibrations_and_their_levers]`;
   the larger step agrees to the curvature (800 → 1300 km/s is −0.32 dex at R₀,
   debt #26), and `AUDIT_RUN2.md` §4.3 has the same lever from the potential's
   side (±5% in v_esc is ∓0.03 dex). Rule B10 applies the day #18 closes;
   until then both are provisional rather than re-fitted against a mechanism
   that is not there. Debt #16 stays discharged — the yield is explained, not
   yet final — and `AUDIT_RUN2.md` §7's "no stale calibration" is read with
   this beside it: the fits still sit on their observables, and the observables
   sit on the wrong history.
   **S13:** `WIND_SPEED` refitted 1010 → 987 km/s — not against debt #18's component,
   still missing, but because the potential it was fitted against carried an
   unconverted concentration (debt #12): the gas at R₀ read −0.015 dex once the halo
   converted, and the constant was re-set to solar (rule B10, D107). `NET_YIELD` stays:
   its −0.025 dex drift is S3's and no row reads it. Both remain provisional on #18.
   **S14:** `WIND_SPEED` refitted 987 → 1028 km/s once the halo contracted around the
   disc (debt #6): v_esc(R₀) rose 562 → 585 and the gas at R₀ read +0.026 dex, and the
   constant was re-set to solar by bisection (rule B10, D113). The potential it is now
   fitted against overshoots row 3 and the observed escape velocity (debt #46), so the
   value is provisional on that as well as on #18.
   **S15:** `WIND_SPEED` refitted 1028 → 999 km/s once the epoch's default is the ΛCDM
   median (debt #12, D117): v_esc(R₀) fell 585 → 569, the gas at R₀ read −0.019 dex, and
   the constant was re-set to solar by bisection. The escape velocity is inside its
   observed range now; row 3 still overshoots by 12, so the value stays provisional on #18
   and on the bulge (#11).
   **S16:** the day #18 closed, as this debt said. Both refitted by bisection to solar at R₀
   (D119): `NET_YIELD` 0.011 → 0.0117 (the gas at R₀ read −0.027 dex once the tail took 7.6%
   of the budget out of the exponential — the first move since S3) and `WIND_SPEED` 999 →
   993 (−0.004 dex; v_esc(R₀) 569 → 568). What both now sit on is the tail as derived and
   the constant threshold; the derived threshold D119 probed moves the gas at R₀ by −0.085
   dex and would move both again. Provisional on that and on the bulge (#11).
   **S17:** the bulge arrived, and it barely moved them — which is itself the finding. The
   spheroid takes 13% of the budget out of the disc, but the gas at R₀ read only −0.005 dex
   (simple) and −0.007 (advanced), a fifth of S16's shift, because a disc with less gas
   also makes fewer stars and the effective yield is a ratio. Refitted anyway, on the rule
   rather than on the size: `NET_YIELD` 0.0117 → 0.01184 (+1.2%) and `WIND_SPEED` 993 →
   982.2 (−1.1%), each by bisection to solar at R₀; `metal_escape_fraction`(R₀) 0.7536 →
   0.7503. Still provisional on the derived threshold and now on the bar (#11, #21).   **S18: the derived threshold, and the largest refit either constant has had.** Kennicutt's
   threshold holds 10.8 M☉/pc² of gas at R₀ where the constant held 6.3 (debt #47), the gas
   there read −0.065 dex (simple) and −0.084 (advanced) — D119 predicted −0.085 — and both were
   re-set to solar by bisection: `NET_YIELD` 0.01184 → **0.01376** (+16%) and `WIND_SPEED`
   982.2 → **860.3** (−12%); `metal_escape_fraction`(R₀) 0.7503 → 0.699, the two effective
   yields 13% apart (17% at S17). The levers: +10% `WIND_SPEED` is −0.060 dex now (−0.064),
   +10% `NET_YIELD` +0.041 (D124). Provisional on the bar (#11, #21) and on the inner
   reservoir the threshold holds (#47), which is upstream of R₀ only through the wind.

44. **Row 2 cannot see past `KS_NORM`'s own uncertainty** (S10, the gamma
   pair; `AUDIT_RUN2.md` §4.1 has the same probe filed as "holds,
   load-bearing"). Kennicutt's normalisation is (2.5 ± 0.7) × 10⁻⁴ and is
   deliberately not fitted (§2). Across that ±1σ the present-day rate runs
   2.16–1.85 M☉/yr and the gas mass 6.8–5.2 × 10⁹: the swing is 2.5 times row
   2's miss, and at +1σ the row is 0.007 from passing `[verified:
   tests/test_audit.py::test_debt_44_row_2_cannot_see_past_ks_norms_own_uncertainty]`.
   A target inside the error bar of the one constant it depends on is not a
   check on the model by itself. What survives is the *pair*: rows 2 and 20
   pull `KS_NORM` opposite ways, so no value of it satisfies both, and that is
   evidence for debt #18 that neither row is alone — the more so once row 20 is
   read like for like (debt #41), and once debt #29's Sagittarius gas, which
   is half of row 2's excess, is taken out.
   **S13:** at +1σ (3.2 × 10⁻⁴) row 2 now reads 1.77 and passes outright; at the default
   1.89. The pair with row 20 is still the evidence.
   **S16, the claim no longer holds:** with the high-j tail built (debt #18, D119) row 2
   reads 2.08 at the default and 1.98 at +1σ, so the ±1σ band (2.25–1.98) no longer reaches
   the window and the row sees past `KS_NORM` now; its miss is debt #47's (the threshold
   and the present infall rate), not this one's. The pair's evidence did its job: the
   component exists. What this debt still records is that the row's *value* carries the
   normalisation's ±0.13 M☉/yr `[verified: tests/test_audit.py::test_debt_44_row_2_cannot_see_past_ks_norms_own_uncertainty]`.   **S18: the band collapsed — the claim is now false in the other direction.** With the
   threshold derived the disc is threshold-regulated everywhere inside 12 kpc (the gas sits
   at 70–90% of Σ_crit), so the present-day rate is whatever the infall supplies and
   `KS_NORM` no longer reaches row 2 at all: 1.764 / 1.755 / 1.755 across its ±1σ band, where
   S17 read 1.97 / 1.82 / 1.73 `[verified: tests/test_audit.py::test_debt_44_row_2_cannot_see_
   past_ks_norms_own_uncertainty]`. Row 2 is a prediction of the infall and the threshold
   alone, inside its window; the gas mass still reads the normalisation (1.17e10 → 1.07e10).
   What this debt recorded — that the row's verdict was the constant's to make — is no longer
   true, and what replaces it is that the row cannot see the constant (D124).

45. **`GAS_DISC_SCALE_RATIO` multiplies nothing at 1.0 and carries the advanced
   model's row 22** (S10, the gamma pair; `AUDIT_RUN2.md` D-6 has the sweep to
   1.2 under debt #18). S3 kept it "so that S10 can sweep it". Swept 0.8 → 1.5:
   the shared upstream goes from R_d = 2.00 to 3.68 kpc, row 3 from 261 to
   237 km/s, the SFR from 1.54 to 2.78 and the gas from 4.3 to 9.3 × 10⁹ M☉;
   at 1.5 the simple model's merger thick disc reaches rows 5 *and* 11 (2.02
   kpc, 7.6 × 10⁹) while rows 3, 4 and 22 are lost — S3's structure-against-gas
   conflict, now with both models' numbers. In the advanced model the
   present-day gradient runs −0.086, −0.057, −0.047, −0.043 across the four
   values, so row 22's pass needs the infall's scale length within a tenth of
   the disc's `[verified: tests/test_audit.py::
   test_debt_45_the_infall_scale_ratio_trades_the_structure_rows_against_the_gas_rows]`.
   The assumption that the accreting gas arrives with exactly the disc's scale
   length (MMW98's, D49) is therefore load-bearing for a passing row, not a
   no-op, and the row is passing on an assumption rather than a measurement
   (rule B11). **Prediction:** debt #18's high-angular-momentum component is
   this constant's second value in disguise — an outer accretion channel
   steepens nothing inside 12 kpc only if it carries no metals in, so with it
   row 22 either holds or moves toward −0.047, which decides whether the
   wind's tilt or the infall's is the one doing the work.
   **S13's numbers:** with the conversion done, row 3 runs 248.3 → 222.7 km/s across
   0.8–1.5 (inside at 0.8 only); at 1.25 the simple thick disc reaches row 5 (1.84 kpc)
   and not row 11; at 1.5 it overshoots row 5 (2.22). The advanced gradient still
   passes only at 1.0.
   **S14:** on the contracted halo the sweep reads row 3 at 253.0 km/s at 1.5 (222.7
   before): a broader infall still cannot buy the row on its own.
   **S16, the prediction held:** with debt #18's component built as the high-j tail (D119)
   the advanced row 22 reads −0.059 (−0.058 before), inside and moved away from −0.047,
   not toward it — the tail carries no metals in and steepens nothing inside 12 kpc, so
   the wind's tilt is the one doing the work. The ratio still multiplies nothing at 1.0;
   the tail is not its second value in disguise because it has no inner part.
   **S17: the debt got wider, not narrower.** The spheroid steepened every setting of the
   sweep by about 0.006 dex/kpc, and 1.25 came inside row 22's window alongside 1.0 — so a
   constant that multiplies nothing at its default now carries the advanced model's row 22
   over a quarter of its 0.8–1.5 range rather than a tenth (−0.106, −0.064, −0.051, −0.046
   `[verified: tests/test_audit.py::test_debt_45_the_infall_scale_ratio_trades_the_
   structure_rows_against_the_gas_rows]`). Row 3 at 1.5 reads 236.1 and row 2 there 2.56.   **S18: no setting of the ratio reads the advanced row 22.** With the derived threshold the
   gradient at 1.0 is −0.0698 (out by 0.0008, the recorded miss under #47) and at 1.25 −0.0468
   (out by 0.002 the other way); 0.8 reads −0.147 and 1.5 −0.038. The window sits between 1.0
   and 1.25, and the constant that multiplies nothing at 1.0 is not the lever that would land
   it — it is named in the miss as the wrong answer that would (D124). The simple model: 1.25
   reads the thick disc at 1.45 kpc and 1.5 at 1.69, *under* row 5 now (2.16 and inside at
   S17), because the threshold truncates the pre-merger disc whatever the infall's extent.

46. **The contraction's strength is a simulation calibration, and every published
   one overshoots row 3** (S14). The halo's response to the disc is modelled with
   Gnedin et al. 2004's invariant r M(r̄), r̄ = A R₂₀₀ (r/R₂₀₀)^w at A = 0.85, w = 0.8
   `[recall]`, chosen on the literature before the row was read (rule B5). At the
   default it adds 43 km/s to the halo's share at R₀ (139 → 181) and 28 to row 3
   (242.7 → 270.8); Blumenthal et al. 1986's circular-orbit invariant, A = w = 1, adds
   57 and 38 (280.9); A = 1.6 at w = 0.8 — a normalisation recalled from the later
   revision with less confidence and not adopted `[recall: Gnedin et al. 2011, where A
   and w vary with halo mass and epoch]` — adds 22 and 14 (256.8). None lands inside
   245–251 at the cited epoch, and the advanced model's escape velocity at R₀ rises
   562 → 585 km/s, above the 530–580 commonly measured `[recall]` — a second
   discriminant overshooting the same way `[verified: tests/test_halo.py::
   test_the_named_rulesets_and_what_each_is_worth_at_R0, ::test_a_third_ruleset_reads_a_third_number]`.
   The two named rulesets are kept and not averaged (rule B12); A enters only through
   the invariant, and a version of the solver that attached the final mass to r̄_f made
   it cancel exactly — found because a third ruleset read the default's number back
   (D113). **Prediction:** the row closes with the contraction as modelled and an
   assembly epoch of 0.7–1.0 (debt #12), or with a baryon distribution less compact
   than one exponential at 2.6 kpc (debts #11, #18); if neither does, the invariant's
   calibration is what is wrong for a disc galaxy, and a mass- and epoch-dependent
   (A, w) is the next thing to try. A recalled magnitude — "several km/s" — was wrong
   by an order of magnitude; the mechanism, not the number, is what belongs in a
   register (rule B4).
   **S15:** the calibration is not the lever, on three readings (D117). The mass- and
   epoch-dependent (A, w) does not exist: Gnedin et al. 2011 report that A and w correlate
   with neither and that the response "cannot be reduced to a simple prescription",
   recommending A = 1.6 with w swept over 0.6–1.3 `[verified: arXiv:1108.5736, read this
   session]` — the form this debt named was recalled, not read. The modern hydrodynamic
   calibration, M_DM(< r) = M_NFW(< r) [0.45 + 0.38 (η + 1.16)^0.53] fitted to the Auriga
   simulations `[verified: Cautun et al. 2020, eq. 11]`, agrees with Gnedin et al. 2004's
   invariant at R₀ to 2 km/s (180.3 against 181.4 at z_f = 2.5, 163.6 against 165.8 at
   1.66), so the default ruleset is not the outlier. And A = 1.6 at w = 0.8 reads 245.6 at
   the derived epoch — inside — and is not adopted, because two calibrations that agree
   are not overruled by a third read with less confidence to land a row (rule B5). The
   local dark-matter density, published as `halo_density_sun` to judge the contraction
   without the rotation curve, does not: 0.28–0.43 GeV/cm³ across z_f = 1–3 against the
   measured 0.3–0.5, because the response steepens the profile inside R₀ more than it
   raises the density there. **Prediction, revised:** the row closes with the bulge and
   the extended component at z_f = 1.66 (debt #11); if it does not, the invariant is the
   remaining suspect and its test is a two-parameter sweep of w at A = 1.6 against rows 3,
   19 and the escape velocity together, not another normalisation.
47. **The extended gas is one derived tail and a constant threshold, and the gas inside
   R₀ is what row 20 still lacks** (S16, D119). The high-j tail (debt #18) follows one
   Level 0 constant, the angular-momentum profile's μ = 1.25, whose 90% range 1.06–2.0
   `[verified: Bullock et al. 2001]` no input absorbs: across μ = 1.06–1.4 the tail's share
   holds at 0.07–0.08 but its inner edge moves 14.9 → 11.0 kpc and row 20 reads 5.8 → 5.0
   × 10⁹ through 6.9 at 1.15, with row 3 unmoved at 252.5–252.6 and row 4 at 2.49. Its
   shape differs from the observed HI two ways: the model holds 3.6 M☉/pc² at 20 kpc where
   the outer HI falls as an exponential of scale length 3.75 kpc from ~10 at 12.5 kpc
   `[verified: Kalberla & Dedes 2008, read at S16]` — the tail ends at j_max, 25 kpc, and
   the grid at 30 — and inside 12 kpc the model's gas is 6.8 at R₀ against the observed
   10–13, because the star formation threshold is the constant 5 M☉/pc², the bottom of its
   cited 5–10. That threshold is derivable: Kennicutt's Σ_crit = α κ σ_g/3.36 G from the
   rotation curve's epicyclic frequency `[recall: Kennicutt 1989; Martin & Kennicutt 2001,
   α ≈ 0.69]`, which at σ_g = 6 km/s reads 11 M☉/pc² at R₀ and 4 at 20 kpc. Probed at S16
   with the tail as built: the gas at R₀ 10.8, hydrogen 8.2 × 10⁹ (row 20 met), row 2 1.95
   (still out), row 4 2.47, the advanced row 22 −0.063 (inside) — and row 9 0.06, out,
   because the thick disc forms from the reservoir the threshold holds. So the threshold
   is judged with the thick disc at S18 (rows 2, 5, 7, 9, 11, 20 together), not here.
   **Prediction:** the derived threshold with S18's radial heating lands rows 9 and 20
   together; if row 9 cannot be restored with the threshold derived, the thick disc's split
   criterion is what is wrong (debt #19), not the threshold. A model that sizes the tail to
   the HI instead would pass row 20 by construction and is the wrong answer that passes.
   **S17: row 2 left this debt without the mechanism being built, and that is worth
   knowing.** The spheroid took 13% of the budget out of what the disc accretes and the
   rate fell 2.08 → 1.82, inside 1.65 ± 0.19 for the first time since S2, so the recorded
   miss was removed (a miss that passes is itself an error, debt #29). The threshold is
   still the constant 5 M☉/pc² at the bottom of its range and nothing about it changed, so
   the debt is unaltered and rows 9 and 20 are still judged with it at S18 — **but row 2 is
   no longer available as evidence there**, and it now sits inside a window its own
   KS_NORM band straddles: at −1σ the row reads 1.97 and fails, at +1σ 1.73 and passes
   `[verified: tests/test_audit.py::test_debt_44_row_2_cannot_see_past_ks_norms_own_
   uncertainty]`. Debt #44's original claim is true again, which is the honest reading of
   a green row 2. The tail's own μ sensitivity is unchanged; row 20 read 6.24 → 6.03 × 10⁹.   **S18 built the threshold, as derived, and judged it with the thick disc (D124).**
   `TOOMRE_ALPHA` = 0.69 and `GAS_DISPERSION` = 6 km/s replace the constant 5; `sfh`
   publishes Σ_crit(R) off the checkpoint-1 curve's epicyclic frequency — 589 M☉/pc² at
   the first cell, 47 at 2 kpc, 26 at 4, **11.5 at R₀**, 3.9 at 20. The gas at R₀ reads
   **10.8** against the observed 10–13; row 20's hydrogen **8.09e9** against 8.0; row 2 1.755,
   inside; the advanced row 6 439 → 373. The prediction this debt made — the threshold with
   S18's radial heating lands rows 9 and 20 together — **failed on row 9**: 0.135 → 0.036
   without the kick, 0.051 with it, and the pre-committed reading applies: the thick disc is
   what is wrong (#19, and now #49), not the threshold. Two findings the number carries.
   **The reservoir at the centre**: Σ_crit diverges with κ where the Toomre argument does not
   hold and the bar (#21) empties the disc, so the model holds 1.5e9 of gas inside 4 kpc
   (S17 0.4e9; the Galaxy a few 1e8) — 1.1e9 of row 20's hydrogen, and outside 4 kpc the
   model reads 7.0e9 against ~7.7e9; row 20 is at its target partly for a wrong reason and
   its entry says so (under #17 now: the number is at a target with no width). The same
   reservoir halves the centre's iron (#26), steepens the advanced row 22 past its edge by
   0.0008 (a recorded miss under this debt), doubles the unmigrated old gradient (#28) and
   reopens the α valley at a fast inner disc (#27). **Regulation**: the disc is
   threshold-regulated inside 12 kpc, so `KS_NORM` no longer reaches row 2 (#44). Still
   open: the reservoir's cause is the bar, and the inner shape is the prediction — a gas
   dispersion that rises inward makes the excess worse (8 km/s everywhere reads row 22 at
   −0.089 and hydrogen 9.9e9), so σ_g is not the lever. Discharged when the inner gas is
   read against the Galaxy's with the bar built, or when a threshold that knows the bar's
   region is derived rather than capped.
   **S20 probed the drain** (D128): a bar-driven inflow inside 2 R_d after Efstathiou, Lake &
   Negroponte's criterion fires (ε = v_max/√(GM_d/R_d) < 1.1, at 0.5 Gyr on a fast first infall
   and 3.3 Gyr on the built one), gas leaving on the local orbital time. It empties the
   reservoir (4.8e6 M☉ inside 4 kpc) and takes 2e10 out of the disc's accretion with it: row 10
   1.4e10, row 22 +0.15, row 4 −12. A bar does not stop the inner disc forming stars; a drain
   on the parked gas alone would be a rule with the answer in it. Still the bar's (#21).

48. **The M_• residual's width is the classical one, for a bulge the model calls 83%
   pseudo** (S17, D121). Ruling 10 (§13) specifies the width "interpolated by the classical
   bulge fraction the model computes", between 0.28 dex for a fully classical bulge and
   "the observed pseudobulge spread, ~no correlation" at the other end. The model computes
   the fraction — `bulge_classical_fraction`, 0.17, and it lands inside BHG16 §4.2.4's
   0–25% for the Milky Way — but **the pseudobulge endpoint has no published number to
   interpolate towards**: Kormendy & Ho declined to fit pseudobulges at all, on the grounds
   that the relation has no physical significance for them, and Ho & Kim 2014 say only "a
   different zero point and much larger scatter" `[verified: Kormendy & Ho 2013 abstract
   and Ho & Kim 2014 abstract, read at S17]`. Inventing a width would be showing a missing
   number as a measured one (rule B9), so `BLACK_HOLE_SCATTER` is the classical 0.28 dex
   and the model **understates** the spread: at the default it publishes a central 95%
   interval of 5.7 × 10⁶ – 9.4 × 10⁷ where the truth is wider. It moves no verdict — a
   statistical row is judged on its median (D109) and the median is the mean relation at
   any width — so this is a defect in what the model *claims*, not in what it scores.
   **What discharges it:** a citation giving the pseudobulge scatter, after which the
   interpolation is two lines and the fraction is already there to drive it. **Prediction,
   stated so it can fail:** whatever that number is, row 18's verdict does not move, and if
   a future session finds the verdict moving when the width is entered, the ensemble's
   median is being estimated at too small an n (ENSEMBLE_MIN = 41 gives a median 0.16 dex
   below the mean here) rather than the width mattering.

49. **The first infall accretes on the thin disc's inside-out law, and that is where the
   thick disc's shape is decided** (S18, D124). `sfh` accretes both episodes on
   τ(R) = τ₀ (R/R₀)ⁿ, so by the last major merger at 3.8 Gyr only 42% of the early gas at R₀
   and 31% at 12 kpc has arrived, and the threshold holds what has arrived outside ~4 kpc as
   gas: the pre-merger disc — the simple model's thick disc — is 1.2 kpc because the model
   makes its gas arrive slowly. The two-infall framework the inside-out index cites gives the
   *first* infall a short, radius-independent timescale (~0.8–1 Gyr, the halo/thick-disc
   phase) and reserves τ_D(R) for the thin disc `[recall: Chiappini et al. 1997, 2001]`; the
   halo's own dynamical time at its assembly epoch, 0.1/H(z_f) = 0.55 Gyr at z_f = 1.66, is
   the derivable candidate and reads the same. Probed at S18 with the early episode at 1 Gyr
   everywhere, the repo unchanged: row 5 **2.11** (inside) — and the whole early share turns
   into thick disc, row 11 1.74e10, row 9 0.62, row 2 1.30; shrinking the share through the
   merger's gas fraction re-truncates the pre-merger disc through the threshold (share 0.8:
   rows 9 and 11 inside at 0.127 and 6.4e9, row 5 1.35 on the constant threshold; 0.032 and
   4.4e9 on the derived one). So rows 5 and 11 trade through the merger share either way,
   and a thick disc both extended and light needs most of the early gas to still be gas at
   the merger — the observed early disc was gas-rich — which a constant-efficiency
   Kennicutt law with a threshold does not allow. In the advanced model the fast first
   infall alone reads a dip of 0.15 at most and row 6 at 720 (#27). **Prediction, stated so
   it can fail:** built with the early episode on its own timescale, row 5 lands at any
   merger share and rows 9 and 11 move together under the share; if they still trade against
   each other, the star formation law at high redshift is what is wrong, and if row 5 does
   not land, the split criterion is (#19). Owned by S20 with the valley: the same lever is
   the two-infall mechanism that makes the inner disc fast, and its other consequence — rows
   6 and 7 — is judged there with both heating constants (#42).
   **S20 ran the prediction and it failed** (D128) `[verified: tests/test_audit.py::test_debt_
   49s_prediction_ran_the_first_infall_on_the_halos_dynamical_time_and_failed]`. With the early
   episode on 0.1/H(z_f) = 0.55 Gyr — derived from `H0`, `OMEGA_M` and the model's own z_f; 1 Gyr
   reads the same — row 5 reads 1.95 at the default share, 2.15 at 0.3, 1.70 at 0.65, 1.26 at
   0.8: it lands only where row 11 is 1.67e10 and row 9 0.56, and where row 11 lands (0.8,
   4.8e9) rows 5 and 9 are 1.26 and 0.04. Rows 5 and 11 still trade through the share, so the
   pre-committed reading is the ruling: **the star formation law at high redshift is what is
   wrong**, not the arrival law and not the split. Also dead: a compact early disc at R_d(z_f)
   (0.62–0.82 on row 5, row 22 −0.147) and Wechsler's M(a) as the rate (row 11 1.5e9: 29% of
   the halo is in place by z_f). In the advanced model the fast law reads a dip of 0.15 at
   N_t 1000/2000/4000 and row 6 at 594. Not built: it would move rows 2, 6, 9, 10 and 11 out to
   move row 5 in. What lands rows 5, 9 and 11 together is the same thing that would open the
   valley (#27): a first phase that consumes gas slower than it accretes it and then stops.

50. **The model moves stars twice, with two kernels, and nothing reconciles them** (S19,
   D126). `sfh` moves a star from where it was born to where it is now with the merger's
   radial kick and the disc's radial spread — 1.47 kpc rms at R₀ for stars born before
   3.8 Gyr (#19, S18) — and `stellar_surface_density`, the thin/thick surface densities and
   every acceptance row read off them are the result. `chemistry` moves the *same stars*
   with the migration kernel, σ = `migration_efficiency` √(age/8 Gyr) = 3.4 kpc at the mean
   local age, and `feh_stars_old`, `alpha_fe_stars` and `feh_spread_sun` are the result.
   Neither knows about the other. They are different mechanisms — an impulsive kick and a
   secular churn — so physically they compose, and the total displacement should be
   √(σ_kick² + σ_churn²); the model applies each alone in a different stage. S19 had to
   choose which one the catalogue follows and chose the chemistry, because the gate and
   debt #31 are both about abundances, so the catalogue's thick fraction at R₀ is now
   **0.221** where `thick_thin_surface_density_ratio` says 0.051 (row 9, a recorded miss
   whose target is 0.08–0.16). **The two transports bracket the observed number**, which is
   the finding: the kick alone puts too little thick disc at R₀ and the churn alone too
   much. The thick disc's *total* is unmoved either way (0.2516 → 0.2535 of the catalogue),
   so this is about where the population sits, not how much of it there is.
   **Prediction, stated so it can fail:** if `sfh` moved stars through both kernels, row 9
   would land between 0.051 and 0.221 and rows 5, 8 and 11 would move with it; if row 9
   still cannot be reached from inside that interval, the split criterion is what is wrong
   (#19, #49) and not the transport. Not S19's to build — it moves five acceptance rows and
   the plan gives none of them to this session — and not S20's either, whose lever is the
   infall law; **for S21 to read and S22 to rule.**

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
