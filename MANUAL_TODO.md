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
| 1 | `s01` | *TBD — S2 fills this in* | **queued** |

### Run these

From a desktop checkout with a credential that can push tags — any normal
personal access token with `Contents: read and write`, or SSH:

```sh
git fetch origin --prune
git checkout main && git pull --ff-only origin main

# S1 — halo & disc. Until S2 records the literal SHA, resolve it by subject:
git tag -a s01 "$(git rev-list -1 --grep='^Merge S1 into main' origin/main)" -m "S1: halo & disc"

git push origin --tags
git ls-remote --tags origin        # confirm; a push that says "Everything up-to-date" did nothing
```

`git rev-list -1 --grep=…` is exact because every session merge uses the subject
`Merge S<N> into main: …` and no other commit does. Once a row carries a literal
SHA, prefer it — a grep can in principle match twice, a SHA cannot.

## 2. Anything else owed

Nothing else at present. Calibration debt is **not** tracked here — it lives in
the register at `GALAXY_INPUTS.md` §11, which `tools/progress.py` counts onto the
board. This file is only for actions that need a human at a keyboard.
