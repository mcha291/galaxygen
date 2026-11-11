"""S93 (BUILD_V row 92, batch M3; T3 / #115): the young population drawn once - the closure VIEWER_TASKS row T3 names.

The cluster census is the whole young population (the ages its clouds' blown-open and dispersing phases span, 20 Myr;
``systems.cluster_window``), and the star sample (``/api/region``, the field mode's region regime at "sampled") drew the
same stars beside the points with no accounting between them, while half the census by count - the dissolved clusters,
an association spread over its cell - was drawn as one point. Since S93 the catalogue publishes ``star_cluster_member``
(``systems.cluster_member``): 1 for a sampled star the points carry - younger than the window and in a cluster that is
still a point, every one younger than the dissolution age and past it a bound one, at the census's own bound fraction
drawn on the star's ``member`` uniform - so the viewer draws the sample without its members and the census without
its dissolved clusters (``regionStars.ts dropRows``). It is the census's partition by class, not by object: the light
matches in expectation.

What is measured (``measure``; S93, the sample at 10^6 stars on the Milky Way and the default galaxy -
the numbers in each test's docstring). The young part ``Y`` is the render's (``resolved.light.young``, the census's
ages). The sample's young light is read **in expectation given its ages**: each star younger than the window weighted
by the mass formed one sampled star stands for (the IMF's mean mass) times the population's light per mass at its age
and [Fe/H] (``photometry.population_at``), over the sampling fraction ``s = n (1 - R) / star_count_total`` - a
10^6-star sample holds a handful of the O stars that carry the young light, so its realised young light is a coin's
toss (0.42 Y on the Milky Way), while the expectation is the membership's own arithmetic.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from galaxy.api import wire
from galaxy.api.service import Service
from galaxy.stages import photometry as ph
from galaxy.stages import systems as sy

ROOT = Path(__file__).resolve().parents[1]
RGB = json.dumps(json.loads((ROOT / "frontend/src/galaxy/filters.json").read_text(encoding="utf-8"))["sets"]["rgb"]["curves"])
WHITE = 6500
DISC = {"r_min": "0", "r_max": "1000", "phi_min": "0", "phi_max": repr(2 * math.pi)}
SAMPLE = 500_000  # the sample's size over the whole disc: ~280 stars younger than the window on the Milky Way


def _ask(service: Service, path: str, q0: dict, **q):
    r = service.handle(path, {k: [str(v)] for k, v in {**q0, **q}.items()})
    assert r.status == 200, r.body[:400]
    return wire.decode(r.body)


def measure(template: str | None, n: int) -> dict:
    """The young part's accounting before and after the membership, bolometric in expectation (module docstring)."""
    service = Service(cache=4)
    q0 = {"template": template} if template else {}
    rh, _ = _ask(service, "/api/render", q0, level=0, l_min="1000", filters=RGB, white=WHITE, **DISC)
    _, ca = _ask(service, "/api/clusters", q0, **DISC)
    ah, _ = _ask(service, "/api/arrays", q0, fields="star_count_total")
    sh, sa = _ask(service, "/api/region", q0, stars=n, **DISC)
    constants = {k: c.value for k, c in service.models.get(sh["model"]).constants.items()}
    s = n * (1.0 - float(constants["RETURN_FRACTION"])) / float(ah["scalars"]["star_count_total"])
    L = np.asarray(ca["cluster_luminosity"], dtype=float)
    state = np.asarray(ca["cluster_bound"])
    age = np.asarray(sa["star_age"], dtype=float)
    young = age < sy.cluster_window(constants)
    member = np.asarray(sa["star_cluster_member"])
    per_mass, _ = ph.population_at(age[young], np.asarray(sa["star_metallicity"], dtype=float)[young])
    light = np.zeros(age.size)
    light[young] = sy.imf_mean_mass() * per_mass
    return {
        "Y": float(rh["resolved"]["light"]["young"]),
        "census": float(L.sum()), "points": float(L[state != 2].sum()), "dissolved": float(L[state == 2].sum()),
        "sample_young": float(light.sum() / s), "kept": float(light[member == 0].sum() / s),
        "members_outside": int((member[~young] == 1).sum()), "young_count": int(young.sum()),
        "dissolved_count_share": float(np.mean(state == 2)),
        "_w": light[young], "_k": member[young] == 0,  # the young stars' expected light and kept flag (the scatter)
    }


def test_the_membership_is_the_census_s_own_rule():
    """A sampled star is a member exactly where a cluster of its age, bound or not by the same uniform, is still a
    point in the census, and only inside the window. The census states its clusters by ``systems.cluster_state`` -
    the one rule both read (the review's mend: no third copy here; tests/test_clusters.py holds the census to it)."""
    from galaxy.stages import clusters as cu

    assert cu.cluster_state is sy.cluster_state  # the census's own function, not a copy
    constants = {"GMC_PHASE_BLOWN_OPEN": 6.0, "GMC_PHASE_DISPERSING": 14.0, "CLUSTER_DISSOLUTION_AGE": 10.0,
                 "CLUSTER_BOUND_FRACTION": 0.07}
    rng = np.random.default_rng(93)
    age_myr = rng.uniform(0.0, 40.0, 20_000)
    u = rng.random(age_myr.size)
    member = sy.cluster_member(age_myr / 1000.0, u, constants)
    state = sy.cluster_state(age_myr, u, 0.07, 10.0)  # the census's rule, in Myr as clusters.py calls it
    assert np.array_equal(member == 1, (age_myr < 20.0) & (state != 2))
    assert sy.cluster_window(constants) == pytest.approx(0.020)


@pytest.fixture(scope="module")
def milky_way():
    return measure("milky_way", SAMPLE)


def test_the_young_population_is_drawn_once(milky_way):
    """Before S93 the sample's young stars, over the sampling fraction, were the young part a second time beside every
    cluster point: (sample + points) / Y = 1.9319 on the Milky Way at 10^6 stars (the sample's young 1.0000 Y, the
    census's 0.9318 Y; the Milky Way is the default galaxy), 1.9813 on ngc_4414. After: the sample keeps the dissolved clusters' share (0.1513 of
    its young light against the census's dissolved light share 0.1597; by count 0.466 of the census is dissolved) and
    the points drop the dissolved, (kept + points) / Y = 0.9343 - the census's own 6 % shortfall (T2: the census's draw
    against its expectation, its seed-to-seed spread 4.4 %, D210), per unit of the census's light 0.9916 (ngc_4414: 1.0241, the kept share 0.1601 against 0.1545, per unit 1.0056)."""
    m = milky_way
    Y = m["Y"]
    assert m["members_outside"] == 0
    assert m["young_count"] > 150
    assert abs(m["sample_young"] / Y - 1.0) < 0.15, m  # the sample is the young part in expectation (measured 1.000)
    assert (m["sample_young"] + m["census"]) / Y > 1.75, m  # the double count the membership removes (1.93)
    after = (m["kept"] + m["points"]) / Y
    assert 0.85 < after < 1.10, after  # T2's bound on the census's bolometric light (measured 0.934)
    # the light the sample keeps is the dissolved clusters', share for share (measured 0.151 against 0.160)
    assert abs(m["kept"] / m["sample_young"] - m["dissolved"] / m["census"]) < 0.05, m
