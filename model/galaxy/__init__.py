"""galaxygen: a procedural galaxy generator, physically grounded, Milky Way by default.

Layering (GALAXY_PLAN.md §2):

    galaxy/core/     fielddoc, registry, seeds, grids, units, stage
    galaxy/models/   model declarations: which stage implementation, which constants
    galaxy/stages/   stage implementations (shared where identical)
    galaxy/specs/    executable specs: graph, preflight, determinism, spec
    galaxy/run.py    the runner: execute one model on one grid, or part of one
    galaxy/api/      the HTTP surface: JSON metadata, binary arrays, no rendering
"""
