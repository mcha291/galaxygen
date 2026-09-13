# galaxygen

A procedural galaxy generator: Python core plus a web viewer, physically
grounded, generating the Milky Way when nothing is touched. Built over eleven
sessions; the status board at the top of `docs/GALAXY_PLAN.md` says where the build is.

```
uv run python tools/bootstrap.py   # once per clone
uv run pytest                      # the suite, quiet
uv run python -m galaxy.specs      # graph, preflight, determinism, acceptance spec
uv run python -m galaxy.api        # serve the API on 127.0.0.1:8017
uv run python tools/timings.py     # cold timings, one fresh process per endpoint
```

- `docs/RULES.md` — the rules the project is held to.
- `docs/GALAXY_PLAN.md` — the build plan and the status board.
- `docs/GALAXY_INPUTS.md` — the model: inputs, rulings, acceptance table, debts.
- `docs/RESUMING.md` — how to open and close a session; where things are.
- `docs/BRIEF.md` — what the next session builds.
- `docs/DECISIONS.md`, `docs/LESSONS.md` — why things are the way they are.

Repository layout:

- `docs/` — every document: rules, plan, inputs, decisions, lessons, audits.
- `model/` — the `galaxy` Python package: stages, models, specs, the runner and the HTTP API.
- `interface/` — the web viewer the API serves.

Package layout is described in `model/galaxy/__init__.py`.

Models are declared one file each in `model/galaxy/models/` (`simple.py`,
`advanced.py`); a new file there is picked up automatically. Shared constants
live in `level0.py`, stage implementations in `model/galaxy/stages/`.
`uv run python -m galaxy.models` prints every model's stage slots side by side
and the constants each declares beyond the shared ones.
