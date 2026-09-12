# Manual TODO

Things the build cannot do for itself, queued for one pass by hand. Nothing here
blocks a session; everything here is owed before the project is finished.

## 1. Session tags

**Why this file exists.** The web sessions push through an egress proxy that
allows branch refs and refuses tag refs: `git push origin s01` returns HTTP 403,
and the GitHub API answers `"Write access to this GitHub API path is not
permitted through this proxy"`, while pushes to `main` in the same session
succeed `[verified: DECISIONS.md D40]`. It is a policy on the path, not a
permission on a token, so no credential handed to a session changes it. Rather
than have eleven closes each end in the same failure, **no session tags** (rule
C2e): each queues its command here, and they are all applied in one go from a
desktop checkout at the end of the build.

**How a session updates this.** At close, a session adds its own row with the
merge SHA left as `TBD` — a merge commit cannot contain its own hash — and
**fills in the previous session's SHA**, which is knowable by then. So the table
runs one row behind, by construction, and the last row is filled in by whoever
closes the project.

| S | Tag | Merge commit on `main` | State |
|---|---|---|---|
| 0 | `s00` | `0bc546d` | **applied** — pushed from the desktop session that ran S0 |
| 1 | `s01` | `4ebbe8f8dfeb` | **queued**, and a stale `s01` must be deleted first — see below |

> **Delete the stale `s01` before running the batch.** An `s01` tag was pushed by
> hand at `56d7510` while S1 was still open, and `main` was afterwards rebuilt into
> a single merge commit per session at the owner's request (D41). `56d7510` is no
> longer reachable from `main`, so that tag now points at an orphan whose tree is
> S1's state *before* its last two commits. Nothing is lost — the content is all in
> the current merge — but the tag has to be re-pointed, and a tag cannot be moved
> from a web session (the same 403 that created this file). This is the cost of the
> rewrite, recorded rather than left to be discovered when the batch runs.
> **Still outstanding as of 2026-09-12**, and checked rather than taken on
> report: `git ls-remote origin refs/tags/s01` returns `e3e8bba`, which peels to
> the orphaned `56d7510`. A local `git tag -d s01` does not touch the remote —
> the refspec push below is what deletes it, and it must run before the batch
> creates the new one, or the create fails as already-existing.

| 2 | `s02` | `fa7e74fb3cc2` | **queued** |
| 3 | `s03` | `8a6032ca31be` | **queued** |
| 4 | `s04` | `c4f217390464` | **queued** |
| 5 | `s05` | `4cc994062473` | **queued** |
| 6 | `s06` | `a71483844338` | **queued** |
| 7 | `s07` | `9b5c612ef027` | **queued** |
| 8 | `s08` | `589cb0f52805` | **queued** |
| 9 | `s09` | `635c3c8ff43d` | **queued** |
| 10 | `s10` | `ff129283543c` | **queued** |
| 11 | `s11` | `b1a62302bb47` | **queued** |
| 12 | `s12` | `701ab3ac12b2` | **queued** |
| 13 | `s13` | `6a2f3f7e669b` | **queued** |
| 14 | `s14` | `e645d430db90` | **queued** — the *second* S14 merge (D115); `780cd15` is the first and is not tagged |
| 15 | `s15` | `71a25128d33c` | **queued** |
| 16 | `s16` | `b0589232c886` | **queued** |
| 17 | `s17` | `4338a60fdcd2` | **queued** |
| 18 | `s18` | `4c73bca169b5` | **queued** |
| 19 | `s19` | `2a8a9b4fc32d` | **queued** |
| 20 | `s20` | `7e96422190ab` | **queued** — filled in by S21 (a) |
| 21 | `s21` | *no merge commit exists* | **not tagged, by design** — see below |
| 22 | `s22` | *TBD — filled in when S22 is merged* | **queued** |

> **There is no `s21`.** S21 ran twice on two branches that are never merged, into each
> other or into `main` (D99, GALAXY_PLAN.md §5d), so no commit on `main` is S21's merge and
> a tag would have to point at something that is not one. S22 ported both lists instead, and
> the commit that carries them is S22's merge, which `s22` tags. The two branches are the
> record — `session-21-a` and `claude/keen-lamport-lldlvp` — and MANUAL_TODO §2 says to keep
> them. The row above exists so that the gap is stated rather than discovered: a session
> missing from the batch is exactly what this table is for.

### S22 tried, and the batch is still owed

**The close-out session attempted the batch and could not run it, which is the
outcome rule C2e predicted and the reason this file exists.** From S22's web
container, on 2026-09-12, with a credential that pushes branches to `main` in the
same session and in the same command sequence:

```
$ git push origin refs/tags/s02          # a queued tag, at its literal SHA
error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
                                          # git exit status 1
$ git push origin claude/…                # the same remote, the same credential
Everything up-to-date                     # git exit status 0
```

That is D40's finding reproduced eight sessions later and unchanged: the egress
proxy allows branch refs and refuses tag refs, so it is a policy on the path and
no credential handed to a session changes it. The local tag was deleted again and
**nothing was pushed**. `git ls-remote --tags origin` still returns exactly what
it returned at S0: `s00` (applied) and the stale `s01` (an orphan).

**So the project is not finished, and the one thing between it and finished is
this batch.** GALAXY_PLAN.md §5d's "done means" lists it, and S22's board row says
so rather than claiming the close. Everything else on that list is met.
**§5d also plans S22 on the web while requiring the batch to be run from a
desktop** — the two cannot both hold, and the plan carried that contradiction
from the day it was written (D116).

### Run these

From a desktop checkout with a credential that can push tags — any normal
personal access token with `Contents: read and write`, or SSH:

```sh
git fetch origin --prune
git checkout main && git reset --hard origin/main   # main was rebuilt once; see D41

# One-off: drop the stale s01 that points at the pre-rebuild merge commit.
git push origin :refs/tags/s01 ; git tag -d s01

# S1 — halo & disc.
git tag -a s01 4ebbe8f8dfebf142b166a207ec1bb57ca0918eb9 -m "S1: halo & disc"

# S2 — star formation history & chemistry.
git tag -a s02 fa7e74fb3cc24e5a25f20e3f6800c5939c6ae821 -m "S2: SFH & chemistry"

# S3 — assembly & mergers.
git tag -a s03 8a6032ca31befc5b6d4d643347d52e7c5dbf17fa -m "S3: assembly & mergers"

# S4 — pattern.
git tag -a s04 c4f2173904641d423f0648d6059a51682ad0aecc -m "S4: pattern"

# S5 — systems.
git tag -a s05 4cc994062473 -m "S5: systems"

# S6 — the API.
git tag -a s06 a71483844338 -m "S6: API"

# S7 — the viewer.
git tag -a s07 9b5c612ef027 -m "S7: viewer"

# S8 — planets.
git tag -a s08 589cb0f52805513eb96092b1ff8777d6b035ed8f -m "S8: planets"

# S9 — the advanced model.
git tag -a s09 635c3c8ff43d670b090d68577b2c8db578e5a1eb -m "S9: advanced model"

# S10 — the audit, run twice.
git tag -a s10 ff129283543c00ffaf0a074602a098aa25288653 -m "S10: audit"

# S11 — the three S10 audits integrated.
git tag -a s11 b1a62302bb47476b902f92cea878ec84f87febdc -m "S11: audits integrated"

# S12 — the maintainer's one-line fixes.
git tag -a s12 701ab3ac12b26068e77cf8a96cd623e0a2af3479 -m "S12: one-line fixes"

# S13 — the physics decisions.
git tag -a s13 6a2f3f7e669bd3e2694f02002d25279342b01aff -m "S13: physics decisions"

# S14 — the halo's contraction. The second merge (D115); the grep would match both, so the SHA is literal.
git tag -a s14 e645d430db9074cfa976e8e4de5b2e02bb723924 -m "S14: halo contraction"

# S15 — the assembly epoch derived.
git tag -a s15 71a25128d33c -m "S15: the epoch derived"

# S16 — the extended component derived.
git tag -a s16 b0589232c886 -m "S16: the high-j tail"

# S17 — the spheroid derived and M_•.
git tag -a s17 4338a60fdcd257d8297c4b1abd73d4bc6e932691 -m "S17: the spheroid and the hole"

# S18 — the radial kick and the derived threshold.
git tag -a s18 4c73bca169b5af2d2d6729d16a965f701ce2a7b7 -m "S18: the kick, the threshold and the solver"

# S19 — the catalogue migrates.
git tag -a s19 2a8a9b4fc32d0040c79e60ac798fe6abe95bd818 -m "S19: the catalogue migrates"

# S20 — the valley probed six ways and recorded; the kick re-derived.
git tag -a s20 7e96422190ab26cdb35ad895a7c7304c087900eb -m "S20: the valley's record and the derived kick"

# S21 — no tag. Two sealed branches, neither merged (D99); see the note above the batch.

# S22 — the close-out: both audit lists ported, every debt ruled. The batch replaces this with the literal SHA.
git tag -a s22 "$(git rev-list -1 --grep='^Merge S22 into main' origin/main)" -m "S22: the close-out"

git push origin --tags
git ls-remote --tags origin        # confirm; a push that says "Everything up-to-date" did nothing
```

**Then finish the record**, which is the only thing left after the batch runs:
paste that `git ls-remote --tags origin` listing into `DECISIONS.md` under D161,
mark every row above **applied**, and tick S22's board row from ◐ to ☑. A tag
push that 403s prints an error and exits 1; a tag push that succeeded and a tag
push that did nothing both print little, so the listing is the check and not the
command's own output.

`git rev-list -1 --grep=…` is exact because every session merge uses the subject
`Merge S<N> into main: …` and no other commit does — checked after the rebuild:
one match on `main`. Once a row carries a literal
SHA, prefer it — a grep can in principle match twice, a SHA cannot.

## 2. Anything else owed

**Keep the three S10 audit branches.** `session-10-beta`, `session-10-gamma` and
`session-10-gamme-run-2` are unmerged by design (DECISIONS.md D99) and are the sealed
lists the four-way comparison D102 rests on; do not delete them from the remote, and
do not merge them — their findings are on `main` as debts #34–#45 and tests.

**Keep both S21 audit branches, and never merge them into each other.** Aim (a) is
`session-21-a`; aim (b) is `claude/keen-lamport-lldlvp` — the web container names its
own branch, and that branch *is* `session-21-b` for every purpose GALAXY_PLAN.md §5d
gives it. S22 ported both lists onto `main` (D99) without merging either, so neither
branch is reachable from `main` and neither carries a tag: `s21` points at S22's merge
of the ported lists, which is the first commit on `main` that holds both.

Nothing else at present. Calibration debt is **not** tracked here — it lives in
the register at `GALAXY_INPUTS.md` §11, which `tools/progress.py` counts onto the
board. This file is only for actions that need a human at a keyboard.
