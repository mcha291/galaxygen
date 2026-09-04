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
> **Still outstanding as of 2026-09-03**, and checked rather than taken on
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
| 9 | `s09` | *TBD — S10 fills this in* | **queued** |

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

# S9 — the advanced model. S10 replaces this with the literal SHA.
git tag -a s09 "$(git rev-list -1 --grep='^Merge S9 into main' origin/main)" -m "S9: advanced model"

git push origin --tags
git ls-remote --tags origin        # confirm; a push that says "Everything up-to-date" did nothing
```

`git rev-list -1 --grep=…` is exact because every session merge uses the subject
`Merge S<N> into main: …` and no other commit does — checked after the rebuild:
one match on `main`. Once a row carries a literal
SHA, prefer it — a grep can in principle match twice, a SHA cannot.

## 2. Anything else owed

Nothing else at present. Calibration debt is **not** tracked here — it lives in
the register at `GALAXY_INPUTS.md` §11, which `tools/progress.py` counts onto the
board. This file is only for actions that need a human at a keyboard.
