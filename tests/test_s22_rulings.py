"""S22's own measurements: the three rulings the close-out could not make from the record alone.

S22 ports both S21 lists and rules every open debt (GALAXY_PLAN.md §5d). Three of those
rulings needed a number that neither audit ran, and they are here rather than in prose:

* **#51's pre-committed test.** Its own sentence was "if every statistical verdict is the
  same on seeds 41-81, 82-122 and the diagonal, the sample is not deciding any of them and
  this debt is a precision statement only." Run.
* **Row 3's miss against the mesh it is read on** (#11). The row misses by 0.03 km/s on the
  default grid, and the convergence sweep moves it by more than that, so the size of the
  miss is not a physical number until the mesh is taken out of it.
* **The detector's reach against row 9's own window** (#70 x #27). Aim (b) put
  `MODE_MIN_SHARE` in closed form and aim (a) opened the one alpha-rich mode this project
  has ever made short of the plateau. Neither list could put the two together; this does.

Pinned as measurements, never as targets, with the precision each was checked at (S19).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from galaxy.core.grids import DEFAULT
from galaxy.core.registry import INPUTS
from galaxy.run import run
from galaxy.specs import spec
from test_audit import Q

SEEDS = [name for name, inp in INPUTS.items() if inp.kind == "seed"]
SEEDED_ROWS = {16: "bar_pattern_speed", 17: "bar_corotation_radius", 18: "black_hole_mass"}
DERIVED_ROWS = {13: "bulge_stellar_fraction", 14: "bulge_velocity_dispersion"}


@pytest.fixture(scope="module")
def simple(prod):
    return prod[0].get("simple")


def diagonal(model, start, fields):
    """The spec's own ensemble, offset: every seed set to k for k in [start, start + 41)."""
    vals: dict[str, list[float]] = {f: [] for f in fields}
    for draw in range(start, start + spec.ENSEMBLE_MIN):
        out = run(model, {s: draw for s in SEEDS}, only=tuple(fields)).fields
        for f in fields:
            vals[f].append(float(out[f]))
    return vals


def test_debt_51_every_statistical_verdict_is_the_same_on_three_disjoint_diagonals(simple):
    """#51's own test, run: three samples of 41, none sharing a draw (S22).

    The verdict is identical on all three for every statistical row, so the fixed sample
    decides no row's pass or fail and the debt is a statement about precision. The numbers
    still move - row 18's median by 48% of its value - which is why it is a statement and
    not a discharge of the instrument: what the sample cannot reach is a verdict, because
    every statistical row is either derived (13, 14) or further from its window edge than
    the sample's own spread (16, 17) or out by a factor (18).
    """
    fields = list(SEEDED_ROWS.values())
    med = {start: {f: float(np.median(v)) for f, v in diagonal(simple, start, fields).items()}
           for start in (0, 41, 82)}

    verdicts = {row: {s: Q[row].lo <= med[s][f] <= Q[row].hi for s in med} for row, f in SEEDED_ROWS.items()}
    for row, by_start in verdicts.items():
        assert len(set(by_start.values())) == 1, (row, by_start, med)
    assert verdicts[16][0] is verdicts[17][0] is True and verdicts[18][0] is False

    # The margin each verdict holds, against the spread the three samples show. Rows 16 and
    # 17 clear their nearest edge by four to five times the spread; row 18 is 4.5-6.6x over.
    for row in (16, 17):
        f = SEEDED_ROWS[row]
        meds = [med[s][f] for s in med]
        spread = max(meds) - min(meds)
        margin = min(min(abs(m - Q[row].lo), abs(m - Q[row].hi)) for m in meds)
        assert margin > 4.0 * spread, (row, margin, spread, meds)
    over = [med[s]["black_hole_mass"] / Q[18].hi for s in med]
    assert min(over) > 4.0, over

    # Rows 13 and 14 do not move at all: S17 found them derived, not seeded (debt #39).
    fixed = {s: diagonal(simple, s, list(DERIVED_ROWS.values())) for s in (0, 82)}
    for f in DERIVED_ROWS.values():
        assert len(set(fixed[0][f])) == 1 and fixed[0][f][0] == fixed[82][f][0], f


def test_debt_11_row_3s_miss_is_half_the_mesh_and_half_the_model(simple):
    """Row 3 reads 251.03 against a window ending at 251.0, and n_R is worth more than that.

    Refined to the value the radial mesh converges to: 251.013, so the miss is 0.013 km/s -
    one part in 460 of the window's half-width - and the other 0.013 is the default grid's
    discretisation. The row stays out at every mesh, which is what keeps it an honest miss
    (rule B5, debt #29); what is not honest is reading 0.03 as a physical quantity.
    """
    reads = {}
    for n in (400, 800, 1600, 3200):
        reads[n] = float(run(simple, grid=DEFAULT.replace(n_R=n), only=("v_tangential_sun",)).fields["v_tangential_sun"])
    assert reads[400] == pytest.approx(251.026, abs=0.005)
    assert reads[3200] == pytest.approx(251.013, abs=0.005)
    assert all(v > Q[3].hi for v in reads.values()), reads  # out at every mesh: the miss is real
    converged = reads[3200] - Q[3].hi
    assert 0.005 < converged < 0.02, converged
    assert reads[400] - reads[3200] > 0.5 * converged  # the mesh is worth as much as the miss


def test_debt_70_and_27_the_only_mode_ever_opened_is_narrower_than_the_milky_ways(simple):
    """The two lists, put together: what the detector can see, against what row 9 asks for.

    Aim (b) (#70): a Gaussian mode of share s and dispersion sigma is kept only if
    s * erf(0.05 / (sigma sqrt2)) >= MODE_MIN_SHARE. Aim (a) (A-4): the one alpha-rich mode
    short of the plateau any probe has produced holds 0.103 of the mass **in one 0.02 dex
    bin**. So it is seen because it is narrower than the observed alpha-rich sequence by a
    factor of two or more, and at the observed ~0.04 dex width the same share is invisible.

    Read against row 9's own window, the consequence is that rows 9 and 24 are very nearly
    mutually exclusive: at 0.04 dex the detector needs a thick/thin ratio of 0.145, which is
    the top 18% of row 9's 0.08-0.16, and at 0.05 dex it needs 0.172 and row 9 has no value
    that would do. That is GALAXY_PLAN.md §7's risk 6 - the 24 quantities are not mutually
    consistent - with two rows named and the arithmetic shown.
    """
    from galaxy.stages.chemistry_dtd import MODE_MIN_SHARE, PEAK_SEPARATION

    half = 0.5 * PEAK_SEPARATION

    def smallest_visible_share(sigma: float) -> float:
        return MODE_MIN_SHARE / math.erf(half / (sigma * math.sqrt(2.0)))

    def as_ratio(share: float) -> float:
        return share / (1.0 - share)

    assert smallest_visible_share(0.01) == pytest.approx(0.100, abs=0.001)  # a spike is free
    assert smallest_visible_share(0.04) == pytest.approx(0.1268, abs=0.001)
    assert smallest_visible_share(0.05) == pytest.approx(0.1465, abs=0.001)

    # A-4's mode: 0.103 of the mass in one bin, so sigma <~ the bin and erf ~ 1.
    assert 0.103 > smallest_visible_share(0.01)
    # The same share at the observed width is not seen.
    assert 0.103 < smallest_visible_share(0.04)

    lo, hi = Q[9].lo, Q[9].hi
    assert (lo, hi) == (0.08, 0.16)
    needed = as_ratio(smallest_visible_share(0.04))
    assert needed == pytest.approx(0.145, abs=0.002) and lo < needed < hi
    assert (hi - needed) / (hi - lo) == pytest.approx(0.18, abs=0.02)  # the top 18% of the window
    assert as_ratio(smallest_visible_share(0.05)) > hi  # at 0.05 dex, nowhere in the window


def test_debt_28_one_width_lands_row_23_and_the_ratio_together_and_it_is_not_the_cited_one(prod):
    """A-10 read two points below the crossing and concluded the ratio could not be landed.

    S21 (a) swept `migration_efficiency` to 2.5 and 2.0 — row 23 inside at 2.5 with the
    young/old ratio at 1.22, inverted at 2.0 — and ruled "the row can be landed; the ratio
    cannot be landed with it". Both points are below where the ratio crosses the observed
    1.75, and the crossing is inside row 23's window: at **3.0 kpc** the old gradient reads
    −0.033 (inside −0.05 to −0.03) and the ratio 1.76 against Willett+23's 1.75. So the two
    chemistry observables *are* landed together, by one width, 17% below the cited 3.6 kpc
    [recall: Frankel et al. 2018] — which is debt #28's *first* explanation, that the
    citation's width is not this kernel's width, and not the second one A-10 convicted.

    Both ends are about 17% shallower than the source's (−0.058 against −0.07 young,
    −0.033 against −0.04 old), so what 3.0 kpc reproduces is the ratio and not the pair.
    The default stays the cited 3.6: moving it here, with both readings known, is the move
    rule B5 exists to prevent. What this pins is that the width the abundances want exists,
    and that it disagrees with the width the disc's structure wants (debt #50: under 1.8 kpc
    once the mass follows the kernel, A-2).
    """
    advanced = prod[0].get("advanced")
    fields = ("metallicity_gradient_old", "metallicity_gradient_young")
    read = {}
    for eff in (2.5, 3.0, 3.6):
        f = run(advanced, {"migration_efficiency": eff}, only=fields).fields
        read[eff] = (float(f["metallicity_gradient_old"]), float(f["metallicity_gradient_young"]))

    old3, young3 = read[3.0]
    assert old3 == pytest.approx(-0.0328, abs=0.002) and Q[23].lo <= old3 <= Q[23].hi
    assert young3 / old3 == pytest.approx(1.76, abs=0.06)  # Willett+23's 1.75

    # The crossing is bracketed, and the cited default is on the far side of it.
    assert read[2.5][1] / read[2.5][0] < 1.75 < read[3.6][1] / read[3.6][0]
    # And the default's own ratio is not what the register has carried since S13: S18's
    # threshold moved it and nobody re-read it. 3.03 (advanced) / 3.27 (simple) then.
    assert read[3.6][1] / read[3.6][0] == pytest.approx(2.55, abs=0.08)
    simple = prod[0].get("simple")
    f = run(simple, only=fields).fields
    assert f["metallicity_gradient_young"] / f["metallicity_gradient_old"] == pytest.approx(2.49, abs=0.08)


def test_debt_79_row_21_has_never_been_judged_in_either_model(prod):
    """The close-out's own finding: one acceptance row is neither a pass nor a recorded miss.

    `gas_h2_fraction` is declared in the table and published by no stage of either model, so
    row 21 reads not-yet-computable in both and always has. Row 24 is not-yet-computable in
    the simple model as well, but by design and with the reason in its own note (one
    abundance, rule B3); this row has no note like that because nobody noticed.

    Pinned so that the day a molecular phase is built, this fails and the row is judged.
    """
    from galaxy.core.registry import production

    models, _, _ = production()
    for model in models:
        out = run(model)
        assert "gas_h2_fraction" not in out.fields, model.name
    assert Q[21].field == "gas_h2_fraction"
    assert Q[21].lo == Q[21].hi == 0.11 and not Q[21].testable  # and it could not pass anyway (#17)
    # Row 24's own not-yet-computable is the documented kind: the note says why.
    assert "not-yet-computable" in Q[24].note and "one abundance" in Q[24].note


def test_no_green_row_is_unconditioned(judged):
    """§5d's gate: "no green row unconditioned (AUDIT_RUN2 §5)", checked against the list.

    `AUDIT_II_A.md` §3 is aim (a)'s re-reading of every passing row — what each is green on
    and whether it would survive its cause being repaired. The gate is only met if that table
    covers the pass set *exactly*: a row that passes and is not in the table is a green nobody
    re-read, and a row in the table that no longer passes means the table is stale.
    """
    import re
    from pathlib import Path

    text = Path(__file__).resolve().parents[1].joinpath("docs", "AUDIT_II_A.md").read_text(encoding="utf-8")
    section = text.split("## 3. The green rows")[1].split("\n## ")[0]
    listed: dict[str, set[int]] = {"simple": set(), "advanced": set()}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not re.fullmatch(r"[\d, ]+", cells[0]):
            continue
        rows = {int(n) for n in cells[0].split(",")}
        for name in ("simple", "advanced") if cells[1] == "both" else (cells[1],):
            listed[name] |= rows

    for name, results in judged.items():
        passing = {r.n for r in results if r.status == "pass"}
        assert passing == listed[name], (name, sorted(passing ^ listed[name]))
    assert len(listed["simple"]) == 10 and len(listed["advanced"]) == 8
