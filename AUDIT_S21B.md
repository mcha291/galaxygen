# AUDIT — S21, run b: the instruments and the viewer

The second of S21's two audits (GALAXY_PLAN.md §5d asks for the session to be run
twice with two stated aims, and the lists diffed at S22). **Aim (b): the
instruments and the viewer** — cold paths (rule D4), the flaky per-star slope
(D115), the audit tests' pins, the bimodality detector's reach, and whether every
published field arrives somewhere a person can see it. Run (a) — every prediction
since S13, killed or held with a number — is the other branch and this file does
not read it.

Reserved numbers (BRIEF.md, D116): debts **#65–#78**, decisions **D144–D157**.

**Model: Opus.** §5a gives Opus the work whose contract is decided and whose gate
is mechanical, and Fable the judgement; aim (b) is the mechanical half by
construction, so the pairing follows §5a rather than being chosen here.

## 0. What this run knew before it started

RULES.md, BRIEF.md, RESUMING.md, GALAXY_PLAN.md §5d, and the files each finding
touches. `AUDIT_RUN1.md` and `AUDIT_RUN2.md` were read — they are main's S10
lists and this run is not blind to them (D97, D102); §3 below re-opens one of
their conclusions, which is the point of reading them. The physics was not
re-litigated: every acceptance number in §1 is reported as the instruments
reported it.

## 1. The instruments, run here

Web container, uv-managed CPython 3.14.0rc2, the suite not running during any
timing (rule B2).

- `uv run pytest` — **exit 0**, 4 skips, all four the advanced model's absent
  thick disc and the simple model's absent local spread (debt #27).
- `uv run python -m galaxy.specs` — **OK**. graph acyclic both models; preflight
  0 UNSET; determinism reproducible within and across processes. spec: simple
  **10 pass, 12 fail, 2 not-yet-computable**, advanced **8 / 15 / 1** — the
  numbers BRIEF.md predicted, unmoved `[verified: §1 of this run, quoted below]`.
  convergence: simple 48 ok / 0 drift / 3 untestable / 0 vacuous / 15
  statistical; advanced 36 / 0 / 3 / 15 / 15. **No recorded miss has started
  passing** (#29).
- `uv run python tools/timings.py` — the table in §2.
- `uv run python -m galaxy.specs.performance` — simple **0.861 s cold**
  (systems 40.3%, sfh 21.8%, planets 17.0%), advanced **1.047 s**
  (chemistry_dtd 31.4%, systems 33.0%, planets 13.9%). `scaling.py` not re-run:
  no stage changed complexity class this session.

## 2. Cold paths: rule D4 checked from outside the thing that reports it

Every D4 assertion in the repository reads `Response.stages`, which is the
service's own account of what it ran. That is rule B3's situation exactly — a
check that takes the reporter's word is a check on the reporter — so this run
counted the stages from the stages. Every registered `Stage.compute` was replaced
with a counting wrapper, and the two pieces of physics the routes call *outside*
the runner (`systems.materialise`, `planets.one_system`) were wrapped too; then
every endpoint in `tools/timings.py` was called on a fresh `Service`.

**The self-report is honest.** On all 17 endpoints the set of stages that
actually executed equals the set the response named, exactly; no stage ran twice;
and all seven metadata endpoints ran **zero** stage computes, measured at the
stage rather than at the route `[verified: tests/test_audit.py::test_s21b_the_d4_report_is_what_actually_ran]`.

The cold table, one fresh interpreter per endpoint:

```
endpoint                 cold s   warm s    c/w      bytes  stages
viewer: index.html       0.0002   0.0002   0.89        940  -
viewer: a module         0.0001   0.0002   0.95     22,390  -
index                    0.0001   0.0001   0.80      1,237  -
version                  0.0012   0.0011   1.07      1,132  -
stages                   0.0004   0.0003   1.14     10,020  -
fields                   0.0010   0.0018   0.55     77,982  -
inputs                   0.0001   0.0001   1.03     10,388  -
arrays: one profile      0.3292   0.0007 445.36      4,984  halo,disc,assembly,sfh
arrays: history          0.2841   0.0057  49.98  6,401,776  halo,disc,assembly,sfh,chemistry
arrays: scalar           0.2178   0.0008 261.88      1,720  halo,disc,assembly,sfh
region: one sector*      0.2698   0.0200  13.47     20,320  halo,disc,assembly,sfh,chemistry,vertical
region: whole disc*      0.6108   0.3557   1.72  1,289,072  halo,disc,assembly,sfh,chemistry,vertical
system: one star*        0.2529   0.0185  13.67      3,240  halo,disc,assembly,sfh,chemistry,vertical
adv: history             0.6141   0.0024 251.71  6,401,784  halo,disc,assembly,sfh,chemistry_dtd
adv: alpha plane         0.6001   0.0024 254.17  6,401,840  halo,disc,assembly,sfh,chemistry_dtd
adv: one sector*         0.5005   0.0194  25.81     20,336  halo,disc,assembly,sfh,chemistry_dtd,vertical_alpha
adv: one star*           0.5246   0.0167  31.39      3,248  halo,disc,assembly,sfh,chemistry_dtd,vertical_alpha
* cold includes the interpreter's first seeded draw, about 8 ms here (debt #37)
import + registry: 0.070-0.083 s, paid once per process
```

Two things the column says that no record says.

- **`disc` is back in every physics route's closure**, and the last table to
  publish the stage column says it left. D115 (S14) recorded "the `disc` stage
  has left the stage column of every route" because `sfh` began reading the
  scale length from the halo (D113); S18 then put Kennicutt's threshold on κ(R),
  which is the disc stage's, and it returned. D125 and D129 publish cold seconds
  without the column, so nothing between S14 and here records the change
  `[verified: D115 against the table above]`. It costs 0.5 ms — the point is not
  the cost but that rule D4's instrument moved and no session read it. **Debt #66.**
- **The most expensive work a region or system query does is invisible to the
  D4 instrument.** `systems.materialise` — 350–420 µs per cell realised, §3 —
  runs outside the runner, so it appears in no `stages` tuple and no cold table
  has ever priced it per route. The region route's defence against D4's named
  defect is real and holds, but it is asserted through the response *header's*
  cell census, not through the instrument the rule is checked with. **Debt #65.**

## 3. The catalogue is priced against the wrong variable

`galaxy/specs/performance.py::catalogue_cost` fits a straight line through
(stars realised, seconds) and publishes a marginal cost per star and a fixed
cost. Every performance record since S11 quotes it; D129's is "1.42 / 1.75 µs
per star against 220 / 209 ms fixed, 89% / 87% of the catalogue at 20,000 stars
independent of how many were asked for".

**The line is fitted to a curve.** Twelve repeats of the fit the test runs, on a
quiet machine: the residuals keep their sign in 12 of 12 repeats at four of the
five sample sizes (−44, +5, +31, +28, −20 ms in the simple model), and the
marginal cost between consecutive sizes falls from 19.6 µs/star at 2k→5k to
0.93 µs/star at 20k→40k, a factor of 21 across the fitted range. A log–log
exponent of 0.18 says the same thing: seconds is very nearly *not* a function of
the stars asked for `[verified: tests/test_audit.py::test_s21b_the_catalogue_is_priced_per_cell_not_per_star]`.

**The variable it is a function of is cells.** Eight sample sizes from 500 to
80,000 stars, best of five per size:

| fitted against | simple | advanced |
|---|---|---|
| stars realised | 2.46 µs/star + 0.222 s, **R² 0.67** | 2.77 µs/star + 0.230 s, **R² 0.65** |
| cells realised | 426 µs/cell + 0.000 s, **R² 0.972** | 491 µs/cell − 0.027 s, **R² 0.977** |
| both | 354 µs/cell + 0.71 µs/star + 32 ms, **R² 0.9994** | 420 µs/cell + 0.69 µs/star + 4.5 ms, **R² 0.9966** |

The cells that realise a star saturate — 349 of 1024 at 500 stars, 800 at
20,000, 829 at 80,000 — and that saturation is the whole of the curvature. So:

- **There is no 270 ms fixed cost.** What the fit calls fixed is the per-cell
  price of however many cells the sample happens to light up, and it falls with
  the sample: the catalogue costs 156 ms at 500 stars, not "270 ms and change".
  The published figure "86% of the catalogue does not depend on how many stars
  are asked for" is false as stated — it depends on the stars, through the cells.
  **Debt #67.**
- **AUDIT_RUN1 §2 discharged debt #24's remainder on a reason that is wrong.**
  Its words are "Cost is proportional to the stars asked for. D61's fear — every
  cell's streams built whether asked for or not — is not what the code does now."
  The conclusion holds and the reason does not: cost is proportional to *cells*,
  and the code is safe from D61's fear for a better reason than the one recorded
  — a nine-cell query pays for nine cells, not for nine cells' share of a fixed
  cost `[verified: AUDIT_RUN1.md §2 against the table above]`. **Debt #73** asks
  S22 to re-read that discharge with the right price in it; nothing about the
  discharge's verdict changes.
- **A one-cell query is 98% overhead, and that is D60's price, not waste.**
  At 20,000 stars one cell costs 20.2 ms of which 0.35 ms is the cell: the rest
  is `materialise`'s per-call work — `cell_masses`, the ring radii, and the churn
  kernel over *every* ring whichever cells were asked for. The stage's comment
  says why, and it is the right why: narrowing the churn to a region's rings was
  tried at S19 and broke per-region determinism in the last bit (D60). Recorded
  as the honest residual of debt #24 rather than as a defect.

## 4. D115's flake: the misfit, not the machine

`tests/test_performance.py::test_the_catalogue_is_priced_per_cell` asserts
`per_star_us > 0`. D115 recorded it failing once in a close's full run, in both
models, on a negative fitted slope, and explained it as "at n = 2000 the slope
is about 2 ms of signal over 100 ms of fixed cost, and the desktop's noise flips
its sign".

Measured rather than recalled, twelve repeats per model:

- the fitted slope is **3.37 ± 0.32 µs/star** (simple) and **3.30 ± 0.18**
  (advanced) — reproducible to about 9% and 5%;
- the fit's *own* standard error on that slope is **1.24 and 1.29 µs**, which is
  **3.9× and 7.1×** the slope's actual scatter across repeats;
- the median t-statistic is 2.9 and 2.5. `per_star_us > 0` is therefore a
  one-sided test at under 3σ **by the fit's own error bar**, and that error bar
  is inflated by the structured residuals of §3, not by the machine
  `[verified: tests/test_audit.py::test_s21b_the_catalogue_is_priced_per_cell_not_per_star]`.

So D115 is right that load triggers the failure and wrong about what makes the
bar wide enough for load to matter: a straight line through a saturating curve
has residuals of ±45 ms whatever the machine does, and those residuals are the
whole error budget. **Fitted against cells the question does not arise** — R²
0.97, and no draw of any repeat comes near zero. The instrument now publishes
both prices and the test reads the conditioned one
(`galaxy/specs/performance.py`, `tests/test_performance.py`). **Debt #68** records
what was changed and why, so that rule B10's habit — a constant fitted against a
broken mechanism has no claim on its value — is applied to the *numbers this
instrument published* as well as to the model's constants.

## 5. The bimodality detector cannot see the thick disc the model is asked for

BRIEF.md states D128's finding as a thing to quantify, not to move (rule B5).
Quantified, from the histogram's exact Gaussian mass rather than a sample (rule
B8):

`bimodality` keeps a local maximum as a mode only if the histogram sums to
`MODE_MIN_SHARE` = 0.10 of the **total** mass within ±`PEAK_SEPARATION`/2 = ±0.05
dex of the peak. That is a test on the peak's *density*, not on the mode's
*share*. For a Gaussian mode of share s and dispersion σ the condition is exactly

    s · erf( 0.05 / (σ√2) ) ≥ 0.10

so the widest mode the detector can see, per share:

| share of the mass | 5% | 8% | 10% | 12% | 15% | 20% | 30% |
|---|---|---|---|---|---|---|---|
| widest σ it can see (dex) | never | never | 0.007 | 0.035 | 0.051 | 0.073 | 0.116 |

**The Milky Way's own thick disc is inside the blind spot.** Acceptance row 9
asks the model for a thick/thin surface-density ratio of 0.08–0.16 at R₀ — a
thick mode holding 7–14% of the local mass — and the observed α-rich sequence is
about 0.04 dex wide in [α/Fe]. At share 0.12 and σ 0.04 the detector finds the
α-rich local maximum exactly where it was put, at +0.29 dex, and then rejects it:
the window holds **0.0929** of the mass against a threshold of **0.1000**, a miss
by seven parts in a thousand of the total
`[verified: tests/test_audit.py::test_s21b_the_detector_cannot_see_a_thick_mode_at_row_9s_share]`.
A mode holding 10% or less is invisible at every width a galaxy could have.

**Prediction, stated so it can fail (rule B4).** If the advanced model is ever
given a thick disc at row 9's target share with the observed α-width, row 24
will still read `single`, and row 24's failure will then be the detector's and
not the model's. What kills this: any advanced-model configuration that lands
row 9 inside 0.08–0.16 *and* reads `bimodal_wide` at the default grid. **Debt #70.**
The threshold is not moved here — B5 — and the remedy is not obviously a
different number: a share test that integrated the mode rather than its peak
would be a different instrument, and choosing one is S22's ruling.

## 6. The viewer: four published fields reach no surface

`view.js` decides what a checkpoint shows from declarations alone, so the
question is answerable without a browser. A field reaches the viewer as a
picture if it is a grid field, as a number if it is a galaxy scalar whose stage
publishes no object columns, and as a column of the region response if it is an
object field. Counting all three sets against `/api/fields`:

| | simple | advanced |
|---|---|---|
| published fields | 113 | 123 |
| picture (grid) | 32 | 37 |
| number (galaxy scalar) | 59 | 64 |
| column (object, via region) | 18 | 18 |
| **reaches no surface** | **4** | **4** |

The four, in both models: `catalogue_size`, `giant_fraction_sample`,
`mean_planets_per_star`, `planet_count_sample`
`[verified: tests/test_audit.py::test_s21b_four_published_scalars_reach_no_surface_of_the_viewer]`.

They are excluded by `scalarsAt`, and for a good reason: asking for a scalar
whose stage publishes object columns would materialise the galaxy's whole sample
to put one number on the screen — rule D4's waste committed by the client. For
`catalogue_size` the exclusion costs nothing, because the region response's own
census carries the count. For the other three it is a real gap: they are
planets-stage aggregates, and neither the region response (star columns) nor the
system response (one star's planets) carries them, so three numbers the model
publishes cannot be seen anywhere in the viewer. §5d's "done means … the viewer
shows every published field" is not met, by four fields, for a reason that is
rule D4 rather than an oversight. **Debt #69**, for S22 to rule: either a cheap
aggregate endpoint, or the three declarations ruled viewer-invisible with the
reason written into them. Both are choices, not repairs, so neither is made here.

**The two numbers S20 moved do reach it.** `thick_disc_dispersion` is published
by `vertical`, which publishes no object columns, and arrives as a scalar at
**34.998** km/s against S20's 35.0. `disc_radial_spread` is a grid field on
(R, t) with a ramp, drawn as an image; its maximum over t at R₀ is **1.0924**
kpc and at 2 kpc **0.2284**, against S20's 1.09 and 0.22
`[verified: tests/test_audit.py::test_s21b_s20s_two_numbers_reach_the_viewer]`.
One qualification worth the record: the viewer shows that field as a picture, so
the number a reader would check against S20's record is not on the screen — it
is the maximum over the time axis of an image. **Debt #74.**

## 7. The audit tests' pins: the precision each was checked at

`tests/test_audit.py` says its numbers are "pinned loosely, as measurements to
spot a regression by". Forty-six `pytest.approx` pins, measured against two
yardsticks: **R**, the distance from the pinned value to the nearest edge of the
acceptance window of the row it is a value of (a tolerance wider than R lets a
pass/fail verdict flip silently); and **H**, the largest step the pin's own
trailing comment records (a tolerance wider than H would have slept through a
change this project actually made).

- **No pin can flip its row.** Two approxes are wider than R — row 3's
  `v_tangential_sun` at 251.03 ± 0.5 against an edge 0.03 away, and row 7's
  1069 ± 30 against an edge 11 away — and **both are guarded on the same line**
  by a clause that is sharper than the approx: `Q[3].hi < v < Q[3].hi + 0.1` and
  `inside(7, …)`. The pattern is worth naming because it is the one that works:
  *where a pinned value sits near a window edge, the guard is an inequality
  against the edge and the approx is only the measurement.*
- **One pin is looser than the refit it exists to watch.** Line 456, the wind's
  contribution to the solar calibration, is pinned at −0.060 ± 0.01 and its own
  comment records −0.064 before S18's refit — a step of 0.004, 2.5× inside the
  tolerance. S18 changed `WIND_SPEED` from 982 to 860 km/s, a 12% move in the
  constant, and this pin would not have noticed `[verified: tests/test_audit.py:456
  and its comment]`. **Debt #71.** Not tightened here: the pin's value was
  measured on this machine to the same 3 decimal places, so tightening it is a
  judgement about how much cross-machine drift to allow, which is S22's.
- **Precision stated, where it is wide and correctly wide.** Row 9's
  `thick_thin_surface_density_ratio` is pinned at 0.0014 ± 0.001 — a tolerance of
  **71% of the value**. Both yardsticks call it sharp (the row's edge is 0.0786
  away, the last recorded step was 0.0082), and they are right, but the honest
  statement is that this pin cannot see a factor-1.7 change in a number the model
  is 57× short on. That is the S19 lesson applied to itself: the pin is fine and
  the precision it checks at is 71%.

## 8. Not found

The instruments that would have found each of these ran and found nothing, which
is what this section is for (rule B5).

- No metadata endpoint ran a stage, counted at the stage rather than at the route
  (§2) — and the stronger form already in the suite, removing the runner from
  their path entirely, still passes.
- No stage ran twice in any request; no response named a stage it did not run,
  and none ran a stage it did not name.
- No route without a cold timing: `tools/timings.py` covers all 17 and
  `tests/test_api.py` fails if a route is added without a row.
- No second `fetch`: the D2 gate scans `git ls-files --cached --others
  --exclude-standard`, so a file added to the client directory and never
  committed is still scanned. The gate does not take the server's path, but the
  set it walks is a superset of what is served, which is the safe direction.
- The D3 content hash changes on a changed byte, on a rename, and not on a
  rewrite of the same bytes; `/api/version` publishes exactly the files on disk.
- No drift on any convergence axis in either model; no recorded miss has started
  passing (#29); no acceptance count moved from BRIEF.md's.
- No grid or object field published without a ramp, in either model (rule A9).
- No checkpoint opens on nothing in either model.
- `progress.debt_counts` reads 32 open / 18 discharged over §11, which is what
  `tests/test_audit.py` pins; `tools/progress.py` reads the board at 21 of 23 closed.

## 9. Not done, and why

- **The detector's threshold was not moved** (§5). Rule B5, and the BRIEF says so
  explicitly: an instrument finding to state, not a threshold to change.
- **The three invisible planets scalars were not given a surface** (§6). Both
  remedies are choices about what the API publishes, and §5d gives S22 the
  rulings.
- **The wind pin was not tightened** (§7). It needs a cross-machine tolerance,
  and one machine measured it.
- **No physics was touched, and no acceptance target moved.** Aim (a) is the
  other branch's.
- **`tools/scaling.py` was not re-run.** No stage changed complexity class; the
  catalogue's price changed variable, not order.
