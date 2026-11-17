"""The stellar disc's edge, declared where it is computed (S102, batch Q, lane G; register #226).

The field regime's light ends at a circle (#226): every light array ``/api/render`` sends falls several hundred-fold
within a few hundred parsecs, on the Milky Way template near 24 kpc. The law that ends it (s102_G.md, the probe
s102_G_edge.py): the halo stage's high-j tail of the angular-momentum distribution (``infall_tail_surface_density``)
falls to nothing where its j_max lands; past it the gas the exponential alone brings lies far under Kennicutt's
threshold, and the threshold's switch turns that fall of the gas into a fall of the stars. The declaration is in
``stellar_surface_density``'s and ``infall_tail_surface_density``'s abouts and the render's stars component.

Held here: the edge the render sends - the ring of the steepest fall of its summed starlight - is the edge the
field publishes - the ring of the steepest fall of ``stellar_surface_density`` - within one ring, and the tail ends
within one ring of it.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from galaxy import templates
from galaxy.api.service import Service
from galaxy.core.grids import GridSpec
from galaxy.models import DEFAULT as DEFAULT_MODEL
from galaxy.run import run

SMALL = GridSpec(n_R=48, n_t=64, n_z=8, n_phi=36)
V_BAND = json.dumps([{"name": "V", "shape": "gaussian", "centre": 5500.0, "fwhm": 900.0}])


def steepest_fall(values: np.ndarray) -> int:
    """The ring after which ln(values) falls most to the next ring (values floored at the smallest positive)."""
    v = np.asarray(values, dtype=float)
    v = np.log(np.maximum(v, v[v > 0.0].min()))
    return int(np.argmin(np.diff(v)))


@pytest.mark.parametrize("template", ("milky_way", "ngc_4414"))
def test_the_edge_the_render_sends_is_the_stellar_disc_s_edge(prod, template):
    model = prod[0].get(DEFAULT_MODEL)
    o = run(model, templates.overrides(templates.TEMPLATES[template]), SMALL,
            only=("stellar_surface_density", "infall_tail_surface_density"))
    R = o.grid.R
    sigma = np.asarray(o.fields["stellar_surface_density"], dtype=float)
    tail = np.asarray(o.fields["infall_tail_surface_density"], dtype=float)
    field_edge = steepest_fall(sigma)
    header, arrays = Service(grid=SMALL).handle("/api/render", {"template": [template], "filters": [V_BAND]}).frame()
    first = int(header["window"]["R"]["first"])
    light = np.asarray(arrays["stars"], dtype=float)
    light = light.reshape(light.shape[0], -1).sum(axis=1)
    render_edge = first + steepest_fall(light)
    print(f"{template}: the field's edge after R {R[field_edge]:.3f} kpc, the render's after {R[render_edge]:.3f}, "
          f"the tail's last ring {R[np.flatnonzero(tail > 0.0).max()]:.3f}")
    assert abs(render_edge - field_edge) <= 1
    assert abs(int(np.flatnonzero(tail > 0.0).max()) - field_edge) <= 1
    # an edge, not a scale length: the fall across it is far steeper than the disc's inside it
    assert sigma[field_edge + 1] < 0.1 * sigma[field_edge]
