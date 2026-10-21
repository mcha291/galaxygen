"""The clouds as extinction at whole-galaxy scale (S64, BUILD_III Phase V6; RULING_S64 R1-R2): API-side arithmetic
on published fields, no stage and no constant on the wire (rule D4; the pattern of ``/api/clusters``' ``response``).

Two answers, each a hook in its own route method of ``service.py`` (and since S70 the clouds' shape, below):

- **The cloud's own dust column** (``/api/clouds``' ``cloud_dust_extinction_v``, :func:`dust_extinction_v`): the
  cloud's face-on MEAN A_V over its disc, from its own dust - its mass times the ring's dust-to-gas ratio, times the
  ring's A_V per unit of dust column, over the disc's area ``pi cloud_size^2`` (``cloud_size`` is the cloud's radius,
  ``sqrt(M / (pi Sigma_GMC))`` at its regime's Sigma_GMC and capped, ``clouds.cloud_size_law``, S67 D231). Each
  ring term is read at the cloud's ``cloud_birth_radius`` - the radius its ring drew, which every per-cloud law and every binner reads (D220) -
  interpolated on the grid as the census reads its metallicity there. The ring's dust law applied to the cloud's
  gas: the clouds stage's own ``cloud_extinction_v`` (S40, the interior's central A_V at solar dust per hydrogen and
  one surface density) is on another law and the two disagree (debt #167).
- **The diffuse share** (``/api/render``'s ``dust_diffuse_share``, :func:`diffuse_share`): per level-0 cell ring,
  1 - (the ring's REALISED clouds' dust) / (the ring's published dust mass). The clouds' dust is summed off the
  ring-first draw's own streams (D220: each ring's count, and each cloud's ``mass`` and ``radius`` uniforms on the
  ring's streams), so no census is materialised and nothing is placed: the same clouds layer on and off.
- **The cloud's face-on shape** (``/api/clouds``' ``cloud_axis_ratio`` and ``cloud_angle``, :func:`cloud_shape`; S70,
  Audit V F-4-3): the ellipse a round feature of the gas fluctuation field becomes under the field's local shear at
  the cloud's placed radius, from the published strain, edges and sense - the formula the viewer applied itself from
  S67 (D230 R2) to S70, moved here unchanged, so the shape is the model's and the viewer only reads it (rule D5).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np

from galaxy.core import seeds as _seeds
from galaxy.stages import clouds as _clouds
from galaxy.stages.systems import CELL_RINGS, cell_edges

COLUMN = "cloud_dust_extinction_v"
SHARE = "dust_diffuse_share"
# The published fields the two answers read, each at the cloud's birth radius or over a ring.
COLUMN_FIELDS = ("dust_to_gas_ratio", "dust_extinction_v", "dust_surface_density")
SHARE_FIELDS = ("gas_molecular_surface_density", "dust_to_gas_ratio", "dust_surface_density")

# The diffuse dust's rule, as the ruling states it (RULING_S64 R2): depth(R) is the dust_extinction component's.
RULE = f"diffuse depth(R, phi) = depth(R) x dust_placement(R, phi) x {SHARE}(R)"

# The derived column's entry in /api/clouds' header (``clouds.derived``): what it is, from which fields, by which rule.
COLUMN_ABOUT: dict[str, Any] = {
    "unit": "mag",
    "fields": ["cloud_mass", "cloud_size", "cloud_birth_radius", *COLUMN_FIELDS],
    "rule": "A_V = cloud_mass * dust_to_gas_ratio(R_b) * (dust_extinction_v / dust_surface_density)(R_b) "
            "/ (pi * cloud_size^2), R_b = cloud_birth_radius",
    "about": "the cloud's face-on mean V-band extinction over its disc, from its own dust: its mass times the ring's "
             "dust-to-gas ratio, times the ring's A_V per unit of dust column, over the area of its disc (cloud_size is "
             "its radius). Every term a published field, each ring field read at the radius the cloud's ring drew "
             "(cloud_birth_radius, linear on the grid, as the census reads its metallicity there), derived here and "
             "not by a stage (S64, V6). SEEDED (rule A10): a function of the inputs and the clouds stage's seed, "
             "systems_seed, through each cloud's realised mass, size and birth radius; the same with the randomness "
             "layer on or off. The ring's dust law applied to the cloud's gas, so the clouds' dust and the "
             "diffuse dust /api/render's dust_diffuse_share leaves sum to the ring's published dust. 0 where the ring "
             "holds no dust (no dust, no extinction; never a guess). The clouds stage's own cloud_extinction_v (the "
             "header's scalars; S40) is the interior's central A_V on another law - solar dust per hydrogen at one "
             "surface density, 5.80 mag at the inner regime's 82 Msun/pc2 since D231 (2.97 at one 42 before), no "
             "metallicity - and the two disagree (at S64, on the 42: 6.3x this law's column at R = 2 kpc, 0.15x at R = 14 on the Milky Way; debt #167)",
}


# S70 (Audit V F-4-3, D233/D234): each cloud's face-on shape along the gas fluctuation field's shear - the formula the
# viewer applied to the published strain since S67 (D230 R2; cloudOpacity.ts shearEllipse and strainAt), moved here
# verbatim so the shape is the model's statement and the viewer reads it (rule D5). Two columns after the dust column.
AXIS_RATIO = "cloud_axis_ratio"
ANGLE = "cloud_angle"
SHAPE_COLUMNS = (AXIS_RATIO, ANGLE)
# Every column this route derives, in the order it sends them after the census's own (S64's, then S70's two).
DERIVED_COLUMNS = (COLUMN, *SHAPE_COLUMNS)
# The published terms the two read: the render header's gas_fluctuation entry carries each (edges, ring.strain, sense).
SHAPE_TERMS = ["cloud_radius", "gas_fluctuation.edges", "gas_fluctuation.ring.strain", "gas_fluctuation.sense"]
SHAPE_RULE = ("k = sense * strain[r], r = the level-0 ring of cloud_radius by edges (the last edge not above it, held to "
              "the first and last rings); cloud_axis_ratio = (2 + k^2 + |k| sqrt(k^2 + 4)) / 2; "
              "cloud_angle = atan2(cloud_axis_ratio - 1, k)")
_SHAPE_ABOUT = (
    "The gas fluctuation field is read at its point rotated by theta(R) = sense (twist + strain ln(R / R_r)) "
    "(gas_fluctuation.GasFluctuationField.read_positions), whose local Jacobian in the (radial, azimuthal) frame is the "
    "simple shear [[1, 0], [-k, 1]], k = sense x strain (dtheta / dlnR); a round feature of the field is the image of a "
    "circle under its inverse, the ellipse [[1, k], [k, 1 + k^2]], of axis ratio lambda+ = (2 + k^2 + |k| sqrt(k^2 + "
    "4)) / 2 and long axis along (k, lambda+ - 1) in (r-hat, phi-hat). Each term is published: the strain per level-0 "
    "ring, the ring edges and the disc's sense in the render header's gas_fluctuation entry, the cloud's placed radius "
    "here. SYNTHETIC (rule A10): the layer's - the shear of the gas fluctuation field, a function of the rotation curve "
    "and the shear time's cap (gas_fluctuation.shear_strain), read at the radius the layer placed the cloud at "
    "(cloud_radius) - and with the layer off, when the field is not published, 1 and 0: every cloud round. Derived "
    "here, not by a stage (S70, Audit V F-4-3; the viewer's formula since S67, D230 R2, moved to the model unchanged); "
    "the viewer draws the cloud's disc as an ellipse of the same area pi cloud_size^2 of axis ratio cloud_axis_ratio "
    "raised to its own 'cloud elongation' power (a display control: 0 round, 1 the field's own anisotropy)"
)
SHAPE_ABOUT: dict[str, dict[str, Any]] = {
    AXIS_RATIO: {
        "unit": "dimensionless", "fields": SHAPE_TERMS, "rule": SHAPE_RULE,
        "about": "the cloud's face-on axis ratio, long over short (>= 1; 1 is round), along the gas fluctuation "
                 "field's local shear. " + _SHAPE_ABOUT,
    },
    ANGLE: {
        "unit": "rad", "fields": SHAPE_TERMS, "rule": SHAPE_RULE,
        "about": "the angle of the cloud's long axis from r-hat (outward) towards phi-hat (increasing azimuth) at the "
                 "cloud, in (-pi, pi]; 0 for a round cloud. " + _SHAPE_ABOUT,
    },
}


def shear_ellipse(k: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(lambda+, angle)`` of the shear ``[[1, 0], [-k, 1]]``'s round-feature ellipse: ``(2 + k^2 + |k| sqrt(k^2 +
    4)) / 2`` and ``atan2(lambda+ - 1, k)`` - cloudOpacity.ts ``shearEllipse`` at exponent 1, term for term in its
    order (k = 0 is round: 1 and 0)."""
    k = np.asarray(k, dtype=float)
    lam = (2.0 + k * k + np.abs(k) * np.sqrt(k * k + 4.0)) / 2.0
    return lam, np.arctan2(lam - 1.0, k)


def cloud_shape(field: Any, radius: np.ndarray) -> dict[str, np.ndarray]:
    """Each cloud's ``cloud_axis_ratio`` and ``cloud_angle`` from the gas fluctuation field ``field`` (its published
    edges, per-ring strain and sense; ``compose.gas_fluctuation``'s answer) at the cloud's ``cloud_radius``: the ring
    by ``field.ring_of`` (cloudOpacity.ts ``strainAt``'s), ``k = sense * strain[ring]``. ``field`` None (the layer off:
    no field is published) is every cloud round - 1 and 0."""
    radius = np.asarray(radius, dtype=float)
    if field is None:
        return {AXIS_RATIO: np.ones(radius.shape), ANGLE: np.zeros(radius.shape)}
    k = float(field.sense) * np.asarray(field.strain, dtype=float)[field.ring_of(radius)]
    lam, angle = shear_ellipse(k)
    return {AXIS_RATIO: lam, ANGLE: angle}


def extinction_per_dust(fields: Mapping[str, Any]) -> np.ndarray:
    """The ring's V-band extinction per unit of dust column, mag per Msun/pc2: ``dust_extinction_v`` over
    ``dust_surface_density``, 0 where the ring holds no dust (rule B9: no dust, no extinction - never a guess)."""
    a_v = np.asarray(fields["dust_extinction_v"], dtype=float)
    sigma = np.asarray(fields["dust_surface_density"], dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(sigma > 0.0, a_v / np.where(sigma > 0.0, sigma, 1.0), 0.0)


def dust_extinction_v(fields: Mapping[str, Any], R: np.ndarray, mass: np.ndarray, size_pc: np.ndarray, birth_radius: np.ndarray) -> np.ndarray:
    """Each cloud's face-on mean A_V, mag: ``mass * dgr(birth R) * (A_V / Sigma_dust)(birth R) / (pi size^2)``.
    A cloud of no size has no area to spread over and gets 0 (none is drawn: sizes are ``sqrt(M / pi Sigma)``)."""
    mass = np.asarray(mass, dtype=float)
    size = np.asarray(size_pc, dtype=float)
    birth = np.asarray(birth_radius, dtype=float)
    dust = mass * np.interp(birth, R, np.asarray(fields["dust_to_gas_ratio"], dtype=float))
    area = math.pi * size**2
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(area > 0.0, dust * np.interp(birth, R, extinction_per_dust(fields)) / np.where(area > 0.0, area, 1.0), 0.0)


def ring_dust_mass(fields: Mapping[str, Any], R: np.ndarray) -> np.ndarray:
    """Each level-0 cell ring's published dust mass, Msun: ``dust_surface_density`` integrated over the ring's
    annulus as the clouds stage integrates a ring's molecular mass (``clouds.ring_molecular_mass``)."""
    return _clouds.ring_molecular_mass(np.asarray(fields["dust_surface_density"], dtype=float), R)


def ring_cloud_dust(fields: Mapping[str, Any], R: np.ndarray, seed: int, constants: Mapping[str, float]) -> np.ndarray:
    """Each level-0 cell ring's realised clouds' dust, Msun: sum over the ring's clouds of ``mass * dgr(birth R)``,
    read off the ring-first draw's streams alone (D220 item 1) - the ring's count (``clouds.ring_counts`` at
    ``clouds.ring_expected``), each cloud's mass (the ring's ``"mass"`` uniforms through the mass function that
    applies at the ring) and its birth radius (the ring's ``"radius"`` uniforms through the inverse of the ring's
    molecular surface density times R), exactly as ``clouds.materialise_clouds`` derives them. No placement, no
    other column, no census: the same number with the layer on or off."""
    edges, _ = cell_edges(R)
    lam = _clouds.ring_expected(fields, R, constants)
    sizes = _clouds.ring_counts(lam, seed, range(CELL_RINGS))
    sigma_h2 = np.asarray(fields["gas_molecular_surface_density"], dtype=float)
    dgr = np.asarray(fields["dust_to_gas_ratio"], dtype=float)
    out = np.zeros(CELL_RINGS)
    for r in range(CELL_RINGS):
        n = sizes[r]
        if n == 0:
            continue
        lo, hi = edges[r], edges[r + 1]
        mass = _clouds.mass_function_sample(
            _seeds.rng(seed, "cloud", r, "mass").random(n), *_clouds.law_for(0.5 * (lo + hi), constants)
        )
        weight = np.where((R >= lo) & (R <= hi), sigma_h2 * R, 0.0)
        u = _seeds.rng(seed, "cloud", r, "radius").random(n)
        # S70 (D234; Audit V F-2-7): was invert_cdf(u, R, weight) - the clouds stage's draw on the ring's own interval.
        birth = _clouds.ring_birth_radius(u, R, weight, lo, hi) if weight.sum() > 0.0 else np.full(n, 0.5 * (lo + hi))
        out[r] = float(np.sum(mass * np.interp(birth, R, dgr)))
    return out


def ring_share(ring_dust: np.ndarray, cloud_dust: np.ndarray) -> np.ndarray:
    """Per level-0 cell ring, the share of the ring's dust that is diffuse: ``1 - cloud_dust / ring_dust``, 1 where
    the ring holds no dust, floored at 0 (S64, the lead's ruling: a negative depth is no depth, rule B9). Where the
    floor acts the ring's realised clouds hold more dust than the ring publishes, and the closure misses by the
    excess - :func:`floored` lists those rings (none on either template, layer on or off: the tests' measurement)."""
    ring_dust = np.asarray(ring_dust, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(ring_dust > 0.0, 1.0 - np.asarray(cloud_dust, dtype=float) / np.where(ring_dust > 0.0, ring_dust, 1.0), 1.0)
    return np.maximum(raw, 0.0)


def floored(ring_dust: np.ndarray, cloud_dust: np.ndarray) -> list[dict[str, float]]:
    """The rings where :func:`ring_share`'s floor acted, each with the excess - the realised clouds' dust past the
    ring's published dust, Msun: what the closure misses there."""
    excess = np.asarray(cloud_dust, dtype=float) - np.asarray(ring_dust, dtype=float)
    return [{"ring": int(i), "excess_dust_mass": float(excess[i])}
            for i in np.flatnonzero((np.asarray(ring_dust, dtype=float) > 0.0) & (excess > 0.0))]


def ring_of(R: np.ndarray, at: np.ndarray | None = None) -> np.ndarray:
    """The level-0 cell ring that holds each radius (the grid's own when ``at`` is None): ``searchsorted`` on the
    ring edges, the last edge in the last ring - the mapping ``bubbles`` uses to put a per-ring quantity on the grid."""
    edges, _ = cell_edges(R)
    where = R if at is None else np.asarray(at, dtype=float)
    return np.clip(np.searchsorted(edges, where, side="right") - 1, 0, CELL_RINGS - 1)


def diffuse_share(fields: Mapping[str, Any], R: np.ndarray, seed: int, constants: Mapping[str, float]) -> tuple[np.ndarray, dict[str, Any]]:
    """(the share on the grid's rings, (R,); the per-cell-ring numbers behind it for the header): each grid ring
    takes the share of the level-0 cell ring that holds it (:func:`ring_of`)."""
    ring_dust = ring_dust_mass(fields, R)
    cloud_dust = ring_cloud_dust(fields, R, seed, constants)
    share = ring_share(ring_dust, cloud_dust)
    expected = _clouds.ring_molecular_mass(
        np.asarray(fields["gas_molecular_surface_density"], dtype=float) * np.asarray(fields["dust_to_gas_ratio"], dtype=float), R
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        expected_share = np.where(ring_dust > 0.0, expected / np.where(ring_dust > 0.0, ring_dust, 1.0), 0.0)
    total = float(ring_dust.sum())
    rings = {
        "share": share.tolist(),
        "dust_mass": ring_dust.tolist(),
        "cloud_dust_mass": cloud_dust.tolist(),
        "clouds_share": (1.0 - share).tolist(),
        "clouds_share_disc": float(cloud_dust.sum() / total) if total > 0.0 else 0.0,
        "expected_clouds_share": expected_share.tolist(),
        "expected_clouds_share_disc": float(expected.sum() / total) if total > 0.0 else 0.0,
        "floored": floored(ring_dust, cloud_dust),
    }
    return share[ring_of(R)], rings


def render_header(rings: Mapping[str, Any], clouds_layer: float | None, placement: str | None, even: str) -> dict[str, Any]:
    """``/api/render``'s header entry ``clouds`` (D223's ``ages`` pattern): the array, its rule, where the clouds
    are and in which layer, the closure, and the per-ring numbers behind it - the expected share marked a check."""
    return {
        "array": SHARE,
        "rule": RULE + ("" if placement is not None else "; this model places no dust round the ring: dust_placement = 1"),
        "fields": [*SHARE_FIELDS, "cloud seed"],
        "route": "/api/clouds",
        "column": COLUMN,
        "layers": {
            "diffuse": "dust",
            "clouds": "halpha_hii",
            "about": "the diffuse dust stays in the dust layer (the gas's published scale height, dust_height); the "
                     "clouds sit in their own layer, cloud_layer_height (the molecular layer's measured FWHM, S67 D229) - the halpha_hii layer, the clouds' layer the "
                     "HII regions are drawn in - each cloud at its published cloud_height. The dust stage's heating "
                     "and the scattered light were computed with all the dust in the gas layer (debt #168)",
            "clouds_scale_height": clouds_layer,
        },
        "about": "the share of each ring's dust that is diffuse once the ring's realised clouds hold theirs: 1 - (the "
                 "sum over the ring's clouds of cloud_mass * dust_to_gas_ratio at the cloud's birth radius) / (the "
                 "ring's published dust mass, dust_surface_density over the level-0 cell ring's annulus). Summed off "
                 "the ring-first draw's own streams (each ring's count, each cloud's mass and birth radius; D220), so "
                 "no census is materialised and nothing is placed: the same share with the layer on or off. SEEDED "
                 "(rule A10): the realised census's, a function of the inputs and the clouds stage's seed, systems_seed "
                 "(the 'cloud seed' of fields), not of the inputs alone (its expectation, 1 - rings.expected_clouds_share, "
                 "is a recorded check, not used). Each grid "
                 "ring takes the share of the level-0 cell ring that holds it; at level=k a cell's mean, as the other "
                 "arrays. 1 where a ring holds no dust. The dust_extinction component is unchanged: the viewer "
                 "multiplies the diffuse depth by this array and draws the clouds' own column (/api/clouds' "
                 f"{COLUMN}) in the clouds' layer" + even,
        "closure": "per level-0 cell ring: dust_diffuse_share * the ring's dust mass + the ring's clouds' dust (the "
                   "census's rows of that ring, cloud_mass * dust_to_gas_ratio at cloud_birth_radius) = the ring's "
                   "published dust mass, to 1e-12 (tests/test_v6_clouds.py, both templates, layer on and off)",
        "rings": {
            **rings,
            "about": "per level-0 cell ring, inner first: the share (floored at 0: a negative depth is no depth; "
                     "floored lists each ring where the floor acted - its realised clouds holding more dust than the "
                     "ring publishes - with the excess dust mass, Msun, by which the closure misses there), the "
                     "ring's dust mass (Msun), the realised clouds' "
                     "dust (Msun) and their share, and the disc's. expected_clouds_share is the ring's molecular "
                     "dust over its dust - the clouds' share in expectation, the ring's molecular fraction: a "
                     "recorded check on the realised share, which departs from it by the census's Poisson noise and "
                     "heavy mass function; not used",
        },
    }
