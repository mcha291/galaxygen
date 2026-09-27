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

Deployment: `Dockerfile` builds `frontend/` and serves it from `galaxy.api` on
one origin; `.github/workflows/image.yml` publishes it to ghcr.io per commit;
`infra/main.bicep` is the Azure Container Apps setup, sized for the free grants
(scale to zero, one 0.5 vCPU / 1 GiB replica), and
`infra/deploy.ps1 -ResourceGroup <name> -Tag <commit>` rolls out that image.
Locally, `uv run python -m galaxy.api --client frontend/dist` serves the built UI.

Models are declared one file each in `model/galaxy/models/` (one today, `basic.py`,
since D170 collapsed the earlier `simple` and `advanced` into it); a new file there
is picked up automatically. Shared constants
live in `level0.py`, stage implementations in `model/galaxy/stages/`.
`uv run python -m galaxy.models` prints every model's stage slots side by side
and the constants each declares beyond the shared ones.

## Attributions

**PARSEC stellar isochrones.** `model/galaxy/data/parsec_isochrones.npz` is derived
from PARSEC v1.2S isochrones with COLIBRI TP-AGB evolution, generated with the CMD 3.9
web service maintained by Léo Girardi at the Osservatorio Astronomico di Padova
(<https://stev.oapd.inaf.it/cgi-bin/cmd>). It keeps initial mass, present mass, log L,
log T_eff, the evolutionary-phase label, the bolometric magnitude and the absolute
magnitudes in U B V R I J H K (Vega; the UBVRIJHK system of Maíz Apellániz 2006 and
Bessell 1990, with the YBC bolometric corrections of Chen et al. 2019) for 396
isochrones: 36 ages (log age 6.6–10.1, step 0.1) at each of 11 metallicities ([M/H]
−2.19 to +0.30, step 0.25); `tools/fetch_parsec.py` regenerates it. The references CMD lists
for these tables:

- Bressan, A., et al. 2012, MNRAS, 427, 127 — PARSEC
- Chen, Y., et al. 2014, MNRAS, 444, 2525 — PARSEC low-mass stars
- Chen, Y., et al. 2015, MNRAS, 452, 1068 — PARSEC massive stars
- Tang, J., et al. 2014, MNRAS, 445, 4287 — PARSEC low-metallicity massive stars
- Marigo, P., et al. 2017, ApJ, 835, 77 — COLIBRI TP-AGB and the CMD isochrones
- Pastorelli, G., et al. 2019, MNRAS, 485, 5666 — TP-AGB calibration (SMC)
- Pastorelli, G., et al. 2020, MNRAS, 498, 3283 — TP-AGB calibration (LMC)
- Chen et al. (2019) — the YBC bolometric corrections, as the CMD output header cites them
- Maíz Apellániz (2006) and Bessell (1990) — the UBVRIJHK photometric system, likewise

**Nebular line grid.** `model/galaxy/data/nebular_lines.npz` is derived from the Cloudy
line grid of Byler, N., Dalcanton, J. J., Conroy, C. & Johnson, B. D. 2017, ApJ
(doi:10.3847/1538-4357/aa6c66, arXiv:1611.08305), as
FSPS ships it (`nebular/ZAU_ND_prsc.lines`, PARSEC-ionized, no dust in the region), at
commit `bd187a0d07dac17b55c4dc7c60d83f63694c1b4e` of <https://github.com/cconroy20/fsps>
(MIT License, Copyright (c) 2009-2021 Charlie Conroy & contributors; FSPS: Conroy, Gunn &
White 2009, ApJ, 699, 486; Conroy & Gunn 2010, ApJ, 712, 833). It keeps the grid's three
axes and six lines (Hβ, [O III] 5007, Hα, [N II] 6583, [S II] 6716, 6731) as log L☉ per
ionizing photon; `tools/fetch_nebular.py` regenerates it.

**Instrument filter curves.** `frontend/src/galaxy/instruments.json` holds HST WFC3/UVIS
system throughputs (F814W, F555W, F438W; F673N, F656N, F502N), resampled, from the SVO Filter
Profile Service; `tools/fetch_filters.py` regenerates it. This research has made use of the
SVO Filter Profile Service "Carlos Rodrigo", funded by MCIN/AEI/10.13039/501100011033/ through
grant PID2023-146210NB-I00 (Rodrigo, C., Cruz, P., Aguilar, J. F., et al. 2024, 2024A&A...689A..93R;
Rodrigo, C., Solano, E. & Bayo, A. 2012, 2012ivoa.rept.1015R; Rodrigo, C. & Solano, E. 2020,
2020sea..confE.182R — the references SVO asks for). The curves are STScI's
(<https://www.stsci.edu/hst/instrumentation/wfc3/performance/throughputs>).

**Massive-star tables** (`model/galaxy/stages/massive_stars.py`, entered row by row from
the published tables): Sternberg, A., Hoffmann, T. L. & Pauldrach, A. W. A. 2003, ApJ,
599, 1333, Table 1 (ionizing photon fluxes of O and early-B dwarfs); Martins, F.,
Schaerer, D. & Hillier, D. J. 2005, A&A, 436, 1049, Table 4 (the comparison
calibration); the mass-loss recipe of Vink, J. S., de Koter, A. & Lamers, H. J. G. L. M.
2001, A&A, 369, 574; the Wolf-Rayet thresholds of Crowther, P. A. 2007, ARA&A, 45, 177.
