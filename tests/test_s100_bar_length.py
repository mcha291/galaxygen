"""S100 (#80; the owner's word of 2026-11-12, D268 ruling 5; D270): the bar's half-length on an unpinned barred disc
is Erwin 2019's Table 4 - log a on log h and a broken log M - in place of its Table 3 (log a on log h alone).

The source, fetched at S96 and again at S100 (Erwin 2019, MNRAS 489, 3553, arXiv:1908.08423; ``docs/READING_BAR.md``
Part S96.1): eq. 4, log a_vis = alpha1 + beta X + beta1 log M* below M_brk and alpha2 + beta X + beta2 log M* above it,
"alpha2 = alpha1 + (beta1 - beta2) M_brk", X = log h; Table 4, row "log M* + log h": alpha1 0.02, beta1 0.00,
beta2 0.35, beta 0.61, log M_brk 10.13. Neither the table nor the text prints a residual scatter; the bar's stage drew
none about Table 3's law and draws none about this one.

What this file holds:

- **the law by hand** at three masses - below the break, at it, above - with this file's own arithmetic and the
  source's literal numbers, against the model's function and the model's runs (a barred disc below the break, one
  0.003 dex under it, the bare defaults above it);
- **the templates bit for bit**: ``milky_way`` (its length pinned at 5.0 kpc) and ``ngc_4414`` (pinned unbarred) read
  every field as they did on Table 3's law - against the same model with Table 3's numbers put back, and against the
  digests measured at the untouched head (0123c7f; machine-pinned);
- **the stand-in's excess, as measured**: the bar is at checkpoint 3 and the stellar mass is published at 4 (rule A1),
  so the law reads the retained baryons' mass that checkpoint 1 publishes. It holds the gas, not corrected (no sourced
  correction exists at checkpoint 1): +0.0919 dex over the stellar mass on the bare defaults and the Milky Way
  template, +0.0682 dex on NGC 4414 - above the break the law carries 0.35 of it into log a, +0.0322 dex (7.7 % of
  the length) on the bare defaults. The gate's stop was an excess over 0.18 dex on any of the three.

Where the three sit against the fit's range (log M* 9-11; the paper states none in h): the bare defaults and the Milky
Way template log M 10.768 (stellar 10.676), h 2.605 kpc; NGC 4414 log M 10.659 (stellar 10.591), h 1.755 kpc - all
inside in mass. Outside it the law is used as fitted (the constant's about says so).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import replace

import numpy as np
import pytest

from galaxy import templates
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run
from galaxy.specs import graph, spec
from galaxy.stages import pattern as pt

# Erwin 2019, Table 4, row "log M* + log h" - the source's literal numbers, not the model's constants.
ALPHA1, BETA1, BETA2, BETA, LOG_BREAK = 0.02, 0.00, 0.35, 0.61, 10.13
# Table 3 (log a on log h alone), the law from S87 to S100.
TABLE3 = (0.04, 0.76)
LAW_NAMES = ("BAR_LENGTH_LOG_NORM", "BAR_LENGTH_SLOPE", "BAR_LENGTH_MASS_SLOPE_LOW", "BAR_LENGTH_MASS_SLOPE_HIGH",
             "BAR_LENGTH_MASS_BREAK")
H_DEFAULT = 2.6048557002908947  # kpc, the bare defaults' lambda_d scale length (unmoved by S100)


def hand_law(h: float, log_m: float) -> float:
    """Eq. 4 by its two branches, alpha2 written out as the paper defines it."""
    if log_m < LOG_BREAK:
        return 10.0 ** (ALPHA1 + BETA * math.log10(h) + BETA1 * log_m)
    alpha2 = ALPHA1 + (BETA1 - BETA2) * LOG_BREAK
    return 10.0 ** (alpha2 + BETA * math.log10(h) + BETA2 * log_m)


def the_model(prod):
    return prod[0].get(DEFAULT_MODEL)


def consts(model) -> dict:
    return {k: c.value for k, c in model.constants.items()}


def table3_model(model):
    """The same model with Table 3's law put back: the mass terms' slopes 0, the zero point and slope Table 3's."""
    old = dict(zip(LAW_NAMES, (*TABLE3, 0.0, 0.0, LOG_BREAK)))
    return replace(model, constants={**model.constants, **{k: replace(model.constants[k], value=v) for k, v in old.items()}})


def digest(fields) -> str:
    """The digest the S100 measure took at the untouched head (scratchpad s100_B2_measure.py): every field, by name."""
    h = hashlib.sha256()
    for k in sorted(fields):
        v = fields[k]
        h.update(k.encode())
        try:
            a = np.asarray(v)
            h.update(a.tobytes() if a.dtype.kind in "fiub" else repr(v).encode())
        except Exception:
            h.update(repr(v).encode())
    return h.hexdigest()[:16]


def template_inputs(name: str) -> dict:
    return templates.overrides(templates.TEMPLATES[name])


# --- the law -------------------------------------------------------------------------------------------------------


def test_the_constants_are_table_4(prod):
    c = consts(the_model(prod))
    assert tuple(c[k] for k in LAW_NAMES) == (ALPHA1, BETA, BETA1, BETA2, LOG_BREAK)


@pytest.mark.parametrize("log_m, expected", [
    (9.8, 1.877708),             # below the break: beta1 = 0, the mass drops out at fixed h
    (LOG_BREAK, 1.877708),       # at it: both branches meet
    (10.767809747725602, 3.139507),  # above: the bare defaults' retained baryons
])
def test_the_law_by_hand_at_three_masses(prod, log_m, expected):
    c = consts(the_model(prod))
    a = pt.bar_length_law(H_DEFAULT, 10.0 ** log_m, c)
    assert a == pytest.approx(hand_law(H_DEFAULT, log_m), rel=1e-12) and a == pytest.approx(expected, abs=1e-6)


def test_the_law_is_continuous_at_the_break():
    below = 10.0 ** (ALPHA1 + BETA * math.log10(H_DEFAULT) + BETA1 * LOG_BREAK)
    above = 10.0 ** (ALPHA1 + (BETA1 - BETA2) * LOG_BREAK + BETA * math.log10(H_DEFAULT) + BETA2 * LOG_BREAK)
    assert below == pytest.approx(above, rel=1e-14)


@pytest.mark.parametrize("inputs, side", [
    ({"halo_mass": 2e11}, "below"),         # log M 10.027, h 1.476
    ({"baryon_retention": 0.08}, "at"),     # log M 10.127, 0.003 dex under the break
    ({}, "above"),                          # the bare defaults, log M 10.768
])
def test_the_model_reads_the_law_on_its_own_numbers(prod, inputs, side):
    F = run(the_model(prod), inputs or None, only=("bar_half_length", "bar_present", "baryon_mass_total",
                                                   "disc_scale_length_spin"), layer=False).fields
    log_m, h = math.log10(float(F["baryon_mass_total"])), float(F["disc_scale_length_spin"])
    assert F["bar_present"] == "yes"
    assert {"below": log_m < LOG_BREAK - 0.05, "at": abs(log_m - LOG_BREAK) < 0.005, "above": log_m > LOG_BREAK}[side]
    assert float(F["bar_half_length"]) == pytest.approx(hand_law(h, log_m), rel=1e-12)


def test_the_default_disc_and_row_15(prod):
    """2.2698 kpc on Table 3 (S87-S100), 3.1395 on Table 4: row 15 (5.0 +/- 0.2) still a recorded miss (B5)."""
    model = the_model(prod)
    F = run(model, only=("bar_half_length",), layer=False).fields
    assert float(F["bar_half_length"]) == pytest.approx(3.139507, abs=1e-6)
    assert float(run(table3_model(model), only=("bar_half_length",), layer=False).fields["bar_half_length"]) == \
        pytest.approx(2.2698417984554817, abs=1e-12)  # the untouched head's number, Table 3 put back
    r15 = {r.n: r for r in spec.run(model)}[15]
    assert r15.status == "fail" and r15.value == pytest.approx(3.139507, abs=1e-6)


def test_the_bar_reads_the_mass_checkpoint_1_publishes(prod):
    models, impls_, table = prod
    g = graph.analyse(the_model(prod), impls_, table)
    bar = g.stages["bar"]
    assert "baryon_mass_total" in bar.requires and "stellar_mass_total" not in bar.requires
    assert g.stages[g.producer["baryon_mass_total"]].checkpoint == 1 < bar.checkpoint == 3
    assert g.stages[g.producer["stellar_mass_total"]].checkpoint == 4  # downstream of the bar: why it is not read (A1)


# --- the templates do not move ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["milky_way", "ngc_4414"])
def test_a_pinned_or_unbarred_template_is_table_3s_bit_for_bit(prod, name):
    model = the_model(prod)
    now = run(model, template_inputs(name), layer=False).fields
    then = run(table3_model(model), template_inputs(name), layer=False).fields
    assert set(now) == set(then)
    for k in now:
        a, b = np.asarray(now[k]), np.asarray(then[k])
        if a.dtype.kind in "fc":
            assert np.array_equal(a, b, equal_nan=True), k
        else:
            assert repr(now[k]) == repr(then[k]), k
    assert (now["bar_present"], float(now["bar_half_length"]) if name == "milky_way" else None) == \
        (("yes", 5.0) if name == "milky_way" else ("no", None))


# Measured at the untouched head 0123c7f (scratchpad s100_B2_measure_before.json), every field's digest.
# S100 (batch P, D270; #130 merged after #80, the gate's ruling 9): re-pinned to the merged head cfb78af. Were
# 132c097763162165 / 141c094867b2d93a / 964d4e6cc31c434c / 5a87d17a964bb664 - read again on 061e5ed (#80 merged,
# #130 not) bit for bit, so #80 moves no template (the proof stands on s100-barlen). Field by field (scratchpad
# s100_P_digcmp.py) only fields downstream of the placed gas differ: the new atomic_gas_density_contrast (all four)
# and gas_density_contrast (the blend, layer on); nothing upstream of the placed gas moved.
BEFORE_DIGESTS = {
    ("milky_way", True): "1fa7077707a4cbb1", ("milky_way", False): "6a88e6b94507cff0",
    ("ngc_4414", True): "07e2d0c9ef80d213", ("ngc_4414", False): "6893ce2cc8271eed",
}


@pytest.mark.machine_pinned
@pytest.mark.parametrize("name, layer", list(BEFORE_DIGESTS))
def test_the_templates_digest_as_at_the_untouched_head(prod, name, layer):
    assert digest(run(the_model(prod), template_inputs(name), layer=layer).fields) == BEFORE_DIGESTS[(name, layer)]


# --- the stand-in's excess, as measured -----------------------------------------------------------------------------

# (retained baryons over stellar mass in dex, and what the law's mass slope makes of it in log a)
EXCESS = {"bare_defaults": 0.09187, "milky_way": 0.09187, "ngc_4414": 0.06817}


@pytest.mark.parametrize("name", list(EXCESS))
def test_the_stand_in_is_high_by_the_gas_as_measured(prod, name):
    inputs = {} if name == "bare_defaults" else template_inputs(name)
    F = run(the_model(prod), inputs or None, only=("baryon_mass_total", "stellar_mass_total", "disc_scale_length_spin"),
            layer=False).fields
    log_b, log_s = math.log10(float(F["baryon_mass_total"])), math.log10(float(F["stellar_mass_total"]))
    excess = log_b - log_s
    assert excess == pytest.approx(EXCESS[name], abs=5e-5) and 0.0 < excess < 0.18  # the gate's stop: 0.18 dex
    assert 9.0 < log_s < log_b < 11.0 and log_s > LOG_BREAK  # inside the fit's mass range, both above the break
    h = float(F["disc_scale_length_spin"])
    lift = math.log10(hand_law(h, log_b) / hand_law(h, log_s))
    assert lift == pytest.approx(BETA2 * excess, rel=1e-9)  # +0.0322 dex (7.7 %) on the defaults, +0.0239 on NGC 4414
