# galaxygen

A procedural galaxy generator: Python core plus a web viewer, physically
grounded, generating the Milky Way when nothing is touched. Built over eleven
sessions; the status board at the top of `GALAXY_PLAN.md` says where the build is.

```
uv run python tools/bootstrap.py   # once per clone
uv run pytest                      # the suite, quiet
uv run python -m galaxy.specs      # graph, preflight, determinism, acceptance spec
```

- `RULES.md` — the rules the project is held to.
- `GALAXY_PLAN.md` — the build plan and the status board.
- `GALAXY_INPUTS.md` — the model: inputs, rulings, acceptance table, debts.
- `RESUMING.md` — how to open and close a session; where things are.
- `BRIEF.md` — what the next session builds.
- `DECISIONS.md`, `LESSONS.md` — why things are the way they are.

Package layout is described in `galaxy/__init__.py`.
