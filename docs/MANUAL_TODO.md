# Manual TODO

Things the build cannot do for itself, queued for one pass by hand. Nothing here
blocks a session; everything here is owed before the project is finished.

## 1. Session tags

**Since 2026-09-30 (rule C2e as amended, D193) every session tags its own merge at
close and this table is the record, not a queue.** The procedure, after the
`--no-ff` merge to `main` is pushed:

```sh
git tag -a s<NN> <merge sha> -m "S<N>: <what the row did>"
git push origin s<NN>
git ls-remote --tags origin | grep "s<NN>"     # the listing is the check
```

then add the row below as **applied** with the SHA the tag peels to (a merge's
hash is known once it exists; the tag is made after the merge, so no row is left
`TBD` any more). **No tag is queued.** A session that finds itself behind a proxy
that refuses tag refs (the web environment, below) queues its command here instead,
marks its row **queued**, and says so in its decision.

**Why this file exists (history, kept).** The web sessions pushed through an egress
proxy that allowed branch refs and refused tag refs: `git push origin s01` returned
HTTP 403, and the GitHub API answered `"Write access to this GitHub API path is not
permitted through this proxy"`, while pushes to `main` in the same session
succeeded `[verified: DECISIONS.md D40]`. It was a policy on the path, not a
permission on a token, so no credential handed to a session changed it. Rather
than have eleven closes each end in the same failure, **no session tagged** (rule
C2e until D193): each queued its command here, and they were applied in one go from a
desktop checkout. **The first batch ran on 2026-09-27** from this desktop, on the
owner's word ("run the tag batch for me"): 39 tags, `s00`–`s20` and `s22`–`s39`,
the listing under D161, the run recorded at D192. **Rows `s40`–`s42` were applied on
2026-09-30** by the same desktop on the owner's word ("run the tags and do them with
each session from now on"): 42 tags on the remote, the listing appended under D161
(D193).

**How a session updated this until D193.** At close, a session added its own row
with the merge SHA left as `TBD` — a merge commit cannot contain its own hash — and
**filled in the previous session's SHA**, which was knowable by then. So the table
ran one row behind, by construction. Since D193 the tag is made after the merge and
the row is written with its SHA at once.

| S | Tag | Merge commit on `main` | State |
|---|---|---|---|
| 0 | `s00` | `0bc546d` | **applied** — pushed from the desktop session that ran S0 |
| 1 | `s01` | `4ebbe8f8dfeb` | **applied** 2026-09-27 — the stale `s01` deleted and re-pointed first, as the note below said

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

| 2 | `s02` | `fa7e74fb3cc2` | **applied** 2026-09-27 |
| 3 | `s03` | `8a6032ca31be` | **applied** 2026-09-27 |
| 4 | `s04` | `c4f217390464` | **applied** 2026-09-27 |
| 5 | `s05` | `4cc994062473` | **applied** 2026-09-27 |
| 6 | `s06` | `a7148384433b` | **applied** 2026-09-27 — the batch's literal `a71483844338` had an extra digit; the tag points at the S6 merge (D192)
| 7 | `s07` | `9b5c612ef027` | **applied** 2026-09-27 |
| 8 | `s08` | `589cb0f52805` | **applied** 2026-09-27 |
| 9 | `s09` | `635c3c8ff43d` | **applied** 2026-09-27 |
| 10 | `s10` | `ff129283543c` | **applied** 2026-09-27 |
| 11 | `s11` | `b1a62302bb47` | **applied** 2026-09-27 |
| 12 | `s12` | `701ab3ac12b2` | **applied** 2026-09-27 |
| 13 | `s13` | `6a2f3f7e669b` | **applied** 2026-09-27 |
| 14 | `s14` | `e645d430db90` | **applied** 2026-09-27 — the *second* S14 merge (D115); `780cd15` is the first and is not tagged |
| 15 | `s15` | `71a25128d33c` | **applied** 2026-09-27 |
| 16 | `s16` | `b0589232c886` | **applied** 2026-09-27 |
| 17 | `s17` | `4338a60fdcd2` | **applied** 2026-09-27 |
| 18 | `s18` | `4c73bca169b5` | **applied** 2026-09-27 |
| 19 | `s19` | `2a8a9b4fc32d` | **applied** 2026-09-27 |
| 20 | `s20` | `7e96422190ab` | **applied** 2026-09-27 — filled in by S21 (a) |
| 21 | `s21` | *no merge commit exists* | **not tagged, by design** — see below |
| 22 | `s22` | `b3939fe64ac8` | **applied** 2026-09-27 — filled in on 2026-09-26 (D171) |
| 23 | `s23` | `fb4a2da1f1d1` | **applied** 2026-09-27 — **not a merge**: S23 ran on `main` without a session branch and was recorded after the fact (D171); the tag marks its last commit |
| 24 | `s24` | `4a20490c5043` | **applied** 2026-09-27 — **not a merge**, as S23 (D171); the last commit of D163–D170 |
| 25 | `s25` | `a4c95cec0be9` | **applied** 2026-09-27 — the first row of the second build; filled in by S26 |
| 26 | `s26` | `05655dba6948` | **applied** 2026-09-27 — filled in by S27 |
| 27 | `s27` | `c72dffd59d36` | **applied** 2026-09-27 — filled in by S28 |
| 28 | `s28` | `e30d33a9d060` | **applied** 2026-09-27 — filled in by S29 |
| 29 | `s29` | `70ed6bd1da8d` | **applied** 2026-09-27 — filled in by S30 |
| 30 | `s30` | `34a76f6fa560` | **applied** 2026-09-27 — filled in by S31 |
| 31 | `s31` | `57c3d38d7810` | **applied** 2026-09-27 — filled in by S32 |
| 32 | `s32` | `89fa20c39e94` | **applied** 2026-09-27 — filled in by S33 |
| 33 | `s33` | `9f43a305a2be` | **applied** 2026-09-27 — filled in by S34 |
| 34 | `s34` | `7b61e2edce88` | **applied** 2026-09-27 — filled in by S35 |
| 35 | `s35` | `5d4cb7885dd0` | **applied** 2026-09-27 — filled in by S36 |
| 36 | `s36` | `f6ec37e5435f` | **applied** 2026-09-27 — filled in by S37 |
| 37 | `s37` | `12c5f80497cc` | **applied** 2026-09-27 — filled in by S38 |
| 38 | `s38` | `80fbf33f9394` | **applied** 2026-09-27 — filled in by S39 |
| 39 | `s39` | `8d8c89475086` | **applied** 2026-09-27 — filled in by S40 |
| 40 | `s40` | `73b95410fa1c` | **applied** 2026-09-30 — filled in by S41; tagged on the owner's word of 2026-09-30 (D193) |
| 41 | `s41` | `75abd5e4029e` | **applied** 2026-09-30 — filled in by S42; tagged the same day (D193) |
| 42 | `s42` | `396bd66ea368` | **applied** 2026-09-30 — the SHA resolved by the grep below; the last row of the queue, tagged the same day (D193) |
| 43 | `s43` | `493c783a7fc9` | **applied** 2026-09-30 at S43's own close — the first tag made under the amended C2e (D193); the SHA written on `main` in the commit after the merge, since a merge cannot carry its own hash |
| 44 | `s44` | `83d2ca25d7d7` | **applied** 2026-10-01 at S44's own close (C2e as amended, D193; D195); the SHA written on `main` in the commit after the merge, as S43's was |
| 45 | `s45` | `11af920ba02c` | **applied** 2026-10-01 at S45's own close (C2e; D196); the SHA written on `main` in the commit after the merge, as S43's and S44's were |
| 46 | `s46` | `7e23ba4337e5` | **applied** 2026-10-01 at S46's own close (C2e; D197, D198); the SHA written on `main` in the commit after the merge |
| 47 | `s47` | `bb8e0fb04e44` | **applied** 2026-10-01 at S47's own close (C2e; D199); the SHA written on `main` in the commit after the merge |
| 48 | `s48` | `62c7f8a79960` | **applied** 2026-10-01 at S48's own close (C2e; D200–D203); the SHA written on `main` in the commit after the merge |
| 49 | `s49` | `f118934182db` | **applied** 2026-10-01 at S49's own close (C2e; D204); the SHA written on `main` in the commit after the merge |

> **There is no `s21`.** S21 ran twice on two branches that are never merged, into each
> other or into `main` (D99, GALAXY_PLAN.md §5d), so no commit on `main` is S21's merge and
> a tag would have to point at something that is not one. S22 ported both lists instead, and
> the commit that carries them is S22's merge, which `s22` tags. The two branches are the
> record — `session-21-a` and `claude/keen-lamport-lldlvp` — and MANUAL_TODO §2 says to keep
> them. The row above exists so that the gap is stated rather than discovered: a session
> missing from the batch is exactly what this table is for.

### S22 tried, and the batch was owed until 2026-09-27 (kept as the record; D161, D192)

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

### The batch as it was run (history; nothing here is still to run)

**Ran on 2026-09-27 through `s39`** (the listing under D161); the block is kept
whole as the record of what was run, with `s06`'s SHA as the tag actually points
(`a7148384433b…`; the literal here read `a71483844338`, one digit too many — D192).
**The last three commands, `s40`, `s41` and `s42`, ran on 2026-09-30** from this
desktop on the owner's word (D193), `s42`'s grep resolving to
`396bd66ea36849cb5d6034ff80a9893e588e2194`; `git ls-remote --tags origin` then listed
42 tags, appended under D161. From S43 on, each session's close makes its own tag
(§1's procedure above) and no command is queued here.

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

# S6 — the API. (The literal was a71483844338 until S42 — an extra 8, no such object; corrected to the S6 merge, D192.)
git tag -a s06 a7148384433bb3218027ea9966afdc19b41d12c3 -m "S6: API"

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

# S22 — the close-out: both audit lists ported, every debt ruled. Literal SHA filled in on 2026-09-26.
git tag -a s22 b3939fe64ac8f16867dabb54d91502099e1f1678 -m "S22: the close-out"

# S23 — the viewer rebuilt, M1's contrast, the restructure. Not a merge: the last commit of the stretch (D171).
git tag -a s23 fb4a2da1f1d10aa5fdb890581dc3cfd3d342cff9 -m "S23: the viewer rebuilt, the pattern's contrast"

# S24 — the render plan's model side and one model (D163–D170). Not a merge: the last commit of the stretch (D171).
git tag -a s24 4a20490c5043adcfd84e481ea9679066c8b7e031 -m "S24: the render plan's model side, one model"

# S25 — A1 rewritten, the pattern ahead of star formation (BUILD_II Phases 0 and 1).
git tag -a s25 a4c95cec0be903ab7dd330dad17aa5c9c7be7199 -m "S25: A1 rewritten, the pattern ahead of star formation"

# S26 — the amplitudes derived and seeded, the arm number from the swing window (Phase 1b).
git tag -a s26 05655dba69488f36ecb927fc20c0319fe85de0ed -m "S26: the amplitudes derived and seeded, the arm number from the disc"

# S27 — the azimuthal model: sfh_azimuthal, the star-formation modulation (Phase 2).
git tag -a s27 c72dffd59d366d7b56f372b33a0598bcdd992415 -m "S27: the azimuthal model, star formation that follows the arms"

# S28 — the photometric rows, the ionizing budget, the wind, the Tully-Fisher sweep (Phase 3).
git tag -a s28 e30d33a9d060966e8b7c87b87bae5c6a58b7af19 -m "S28: the magnitudes, the ionizing budget and the Tully-Fisher sweep"

# S29 — remnants and planetary nebulae (Phase 4).
git tag -a s29 70ed6bd1da8d28109f0bd5df268f8acbc2f353b6 -m "S29: remnants and planetary nebulae"

# S30 — the supernova rates and the habitable zone (Phase 6).
git tag -a s30 34a76f6fa5607674473d932e0e4e9610b38da692 -m "S30: the supernova rates and the habitable zone"

# S31 — dust that radiates: the grain model, the heating balance, G0 and the PAHs (Phase 7).
git tag -a s31 57c3d38d7810179768acd40621b9b220403cd53a -m "S31: dust that radiates"

# S32 — the molecular-cloud census and the cell hierarchy (Phase 8).
git tag -a s32 89fa20c39e948fbf83adbdbe7d5b79c1eaadc5c3 -m "S32: the cloud census and the cell hierarchy"

# S33 — young star clusters as objects, the efficiency derived, the Q closure (Phase 11).
git tag -a s33 9f43a305a2be79b9e3aeb0ad4ad67987fd9a5c5d -m "S33: clusters as objects"

# S34 — globular clusters as the bound clusters' survivors, the stellar halo, rows 32-33 as misses (Phase 5).
git tag -a s34 7b61e2edce88d22c9a6c96bbcb5a8cfeac29b8a9 -m "S34: globular clusters and the stellar halo"

# S35 — the HII regions' shape parameters and volume emissivity, Case B, the diffuse layer, rows 34-36 (Phase 9).
git tag -a s35 5d4cb7885dd0c7a8aaf3ea012c5b8945a082d2fb -m "S35: nebular emission"

# S36 — Weaver bubbles per cluster and star, the supernova-remnant census, the hot phase (Phase 10).
git tag -a s36 f6ec37e5435f6f3ecda2796df848855909cae82d -m "S36: mechanical feedback"

# S37 — Audit III: the second build re-read, re-derived, its greens conditioned, two windows read blind.
git tag -a s37 12c5f80497ccdc441e7df0c9612c4bf5911b0c4f -m "S37: Audit III"

# S38 — Audit III's fixes; V1: /api/render, the eight-band SED, the filter sets, the gate to 1e-4 mag.
git tag -a s38 80fbf33f93940532a26f29193345f122f3bdaa27 -m "S38: V1, the filter integral"

# S39 — V2: the dust in three components, the line in two layers, the frame's balance and profile.
git tag -a s39 8d8c89475086421c77c13dace70cd9149c2f7564 -m "S39: V2, volumetric emission and emitting dust"

# S40 — V3: the region regime from the cloud vector, the censuses named by (cell, index), catalogue against field.
git tag -a s40 73b95410fa1caad603f405de1924641cf4a584fd -m "S40: V3, region synthesis from the cloud vector"

# S41 — V4: clusters drawn as objects, every object column drawn or ruled not drawn in its declaration. SHA filled in by S42.
git tag -a s41 75abd5e4029ea27b854c6d91b5201f5b62d88535 -m "S41: V4, clusters as objects and the object columns ruled"

# S42 — the owner's four answers: the FSPS grid, the blind windows, WFC3 from SVO, the batch; the POST path; P6. SHA filled in by the next session.
git tag -a s42 "$(git rev-list -1 --grep='^Merge S42 into main' main)" -m "S42: the forbidden lines, the blind windows, a named instrument, the points through the filters"

git push origin --tags
git ls-remote --tags origin        # confirm; a push that says "Everything up-to-date" did nothing
```

**Then finish the record**, which is the only thing left after a batch runs:
paste that `git ls-remote --tags origin` listing into `DECISIONS.md` under D161,
and mark the rows above **applied** (done for `s00`–`s39` at S42's close, when
S22's board row ticked ◐ → ☑, and for `s40`–`s42` at S43's opening, D193). A tag
push that 403s prints an error and exits 1; a tag push that succeeded and a tag
push that did nothing both print little, so the listing is the check and not the
command's own output — which is why the per-session procedure in §1 ends with it.

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
