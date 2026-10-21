# BRIEF — after S70: BUILD_IV begins (row 71 W3 is the owner's; the next agent session is S72, Phase W2, the bundles)

**The state (2026-10-21).** S70 is merged (D234): Audit V's fixes — the per-object invariant with declared placement
sets, the owner's three rulings (#191–#193), the clouds' ring draw fixed, the citations corrected, the layer's bounds
measured over the population, the two viewer gaps closed, the register's drift corrected; every frame regenerated.
Register 129 open = 11 + 118, 52 discharged; next number **#199**, decisions from **D235**, board row 71 (W3, the
owner's) / 72 (W2), acceptance rows from 38. **The owner's standing order** covered BUILD_III (S54–S70); BUILD_IV's
rows were adopted at D222 with W3 the owner's own build. **Ask before starting W2** unless the owner's word already
says to go on; the rationing rule holds (two agents, one heavy; check `get_usage` before each spawn).

## What waits on the owner (nothing else awaited)
- **W3, the gateway (row 71):** `gateway/` is scaffolded; an agent built the features on the owner's ask on branch
  `worktree-session-70-gateway` (09147c9: queue, share links, hash-keyed output cache, 17 tests; D222's note that
  `/api/version`'s hash covers only `api/*.py`). Unmerged, no decision or board entry: the owner says whether it is
  theirs to finish, or to merge as built (then a session reviews it against BUILD_IV §2c and Appendix A's D3/D5 lines).
- **#197:** the stars' and remnants' ring draws (5 % born up to 70 pc below their ring) — a session of its own; it
  moves the whole catalogue, every frame and the catalogue's pins. Their word on when.
- **#195:** the arm pieces carry 0.57 / 0.85 of the law's power budget (declared); filling it moves a number.
- **F-4-1:** their Milky Way default (`cloudsExtinction: false`) leaves 0.492 of the disc's dust undrawn.

## Build: Phase W2 — the template bundles (`BUILD_IV.md` §2b, §4b, §7 rulings 6 and 11; row 72)
- `tools/export_template.py` runs the model once per template and writes a bundle: every metadata route's JSON, every
  published array, `/api/render` for each shipped filter set at the default white point, the censuses (`clouds`,
  `clusters`, `remnants`, `bright` at the viewer's levels), `/api/region` for every cell at the levels the ruling
  allows, the content hash it was built from, a manifest (route, query, bytes). The service answers from a bundle
  when template, layer switch, query and content hash match, byte-identical to the computation — **the gate asserts
  it on every entry**; a mismatch is an error, not a fallback. Ruling 6: all shipped sets; levels 0–1 whole, level 2
  as the probe allows, 3 on demand; **the size bound is set after a probe measures the bundle** (report the table
  first, then the owner rules). Ruling 11: the in-memory galaxy cache stays beside the bundles.
- Touches `model/galaxy/api/` (the bundle reader) and `tools/`; **no stage, no field, no number**; D3 (every cache
  keyed on the content hash) restated at the boundary; a `tools/timings.py` row for the reader.
- **Gate:** every bundle entry byte-identical to the live route; the suite once; the picture test byte for byte (the
  viewer must not know which path answered); the bundle's table in the decision. **Agents:** one probe (the sizes),
  one builder, one reviewer.

## Read
- `BUILD_IV.md` §0–§2, §4, §7, Appendix A; D222, D234; `RULES.md` D2–D5; `model/galaxy/api/service.py` (ROUTES, the
  cache, `/api/version`), `tools/timings.py`, `tools/verify_clone.py` (the shape of a tool that runs the model once).

## Traps learned at S70
- **An agent worktree is cut from `main`:** its first step is `git merge --ff-only session-NN`; a second builder on
  the same files merges, it does not fast-forward — cherry-pick or merge its branch, then remove the worktree
  (`remove -f -f` if its own background run still locks it).
- **A builder's measured number is re-measured by the next who touches it** (0.47 vs 0.569: the lead settles it).
- **The register's two pins live in `tests/test_audit.py`** (the tuple and the carried row); re-pin both in the commit
  that moves the register. `#173`'s randomised-order test is gated (`GALAXYGEN_AUDIT_ORDER=1`): run it once at a close.
- Still standing: Bash under 8 KB; pytest's exit code to a file; one picture-test run at a time (:8019); `tools/bootstrap.py`
  before the suite; layer off nothing may move; nothing is tuned to a goal picture; a detached verify_clone's log is
  read before the session ends; run the owner's servers in their Terminal panel.
