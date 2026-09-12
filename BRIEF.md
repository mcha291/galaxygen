# BRIEF — the build is closed. This is for whoever maintains it.

S0–S22 are spent and §5d's plan is complete except for one command no session can run. Read
RULES.md in full, then RESUMING.md, then `GALAXY_INPUTS.md` §11's head — the debt map — and stop
there unless you are changing something. GALAXY_PLAN.md's board is the record of what is done (A9).

## The one thing owed
**Run the tag batch in `MANUAL_TODO.md` §1 from a desktop**, delete the stale `s01` first, then
paste `git ls-remote --tags origin` under DECISIONS.md D161 and tick S22's board row from ◐ to
☑. Twenty-one tags are queued at literal SHAs. S22 attempted it and got HTTP 403 on a tag ref
with a branch push succeeding seconds later on the same credential — D40's finding, reproduced
eight sessions on, and the reason rule C2e exists. Nothing else is outstanding.

## What the instruments say
`uv run pytest && uv run python -m galaxy.specs`: graph acyclic in both models, preflight 0
UNSET, determinism reproducible within and across processes, spec **simple 10 / 12 / 2** and
**advanced 8 / 15 / 1**, convergence 0 drifts. Those counts have not moved since S20 and are the
fastest check that a clone is sound. `tools/verify_clone.py --ref main` does the whole of it in
a fresh clone, which is the only verification rule C2 accepts.

## What the model does not have, in one paragraph
Twenty-seven register items are open: **15 ruled permanent**, **12 carried**, none unruled. The
twelve carried are not twelve mechanisms. **Four of them are one** — #19, #27, #49 and the
inner half of #47 — and it is the largest single absence in the build: *a first phase that
consumes gas slower than it accretes it and then stops, the stopping after the first Ia iron
has arrived*. A constant-efficiency Kennicutt law with a threshold cannot do it, and fourteen
acceptance rows across the two models hang on it. Three more — #11, #52, #47's reservoir — are
the bar, which is permanent because this model's controls are global scalars (A2) and no
relation for the bar's first link is quoted anywhere in the project (A4). The permanent
fifteen are eight source limitations, five scope limitations, one rule-A1 fixed point (#26's
mass-loaded wind, which would make the retained baryon fraction a fixed point across
checkpoints 1 and 3), and one rule-A9 instrument gap (#65).

## Three things a maintainer should not have to rediscover
- **Row 23 is the one recorded miss whose cause is a constant the model could tune.** At
  `migration_efficiency` = 3.0 kpc the old gradient reads −0.033 (inside) and the young/old
  ratio 1.76 against Willett+23's 1.75. The default stays the cited 3.6 kpc, because moving it
  with both readings known is what rule B5 exists to prevent. Its miss entry says so.
- **Row 3's miss is half the mesh.** 251.026 at the default grid against a window ending at 251.0;
  251.013 at n_R = 3200. Red at every mesh, honestly — but 0.03 km/s is not a physical quantity.
- **Rows 9 and 24 are nearly mutually exclusive through the bimodality detector.** At the observed
  α-width it needs a thick/thin ratio of 0.145 — the top 18% of row 9's 0.08–0.16 — and at 0.05 dex
  no value in row 9's window would do. GALAXY_PLAN.md §7's risk 6, with two rows named.

## If you change something
RESUMING.md's "Writing a stage" still applies, and two habits are worth more than the rest. A
constant's *citation* is read before a row it lands is trusted — `MERGER_HEATING`'s "cited 35
km/s" is a selection-function constant whose underlying measurement is 39 ± 4, at which row 7
fails and row 3 passes; both values are in its about line and neither is averaged (B12). And a
number an instrument prints gets republished by whoever runs the close next, so a corrected
instrument must print the right number *beside* the wrong one — which is what `performance.py`
now does with the catalogue's two fits, after ten sessions of a straight line through a curve.

## Traps
- **Write files with `newline="\n"`**; the full suite outlasts a tool's output cap — background
  it with `EXIT=$?` appended to its log and gate the merge on that line.
- A recorded miss that starts *passing* fails the run (#29): remove the entry and write down why.
- **Do not merge or delete** `session-10-beta`, `session-10-gamma`, `session-10-gamme-run-2`,
  `session-21-a` or `claude/keen-lamport-lldlvp`. They are the sealed audit lists D99 and D102
  rest on; their findings are on `main` and the branches are the record.
