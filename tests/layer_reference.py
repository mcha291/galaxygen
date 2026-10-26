"""The reference the layer-off model is held to: S55 with the randomness layer off (S56, DECISIONS.md D215).

**What it replaced, and why.** Phase R (S55, D214) was behaviour-preserving, and this module's first reference was of
S54 with the layer **on** (``tests/layer_reference_s54.json``): every field and every route's arrays, bit for bit.
That reference is retired at S56: from Phase P1 the layer-on galaxy changes by design - several arm modes at once,
their phases a new draw on ``texture_seed`` - so a layer-on digest stops being a statement about anything a phase
must keep. What a phase must keep is the physics, and the physics alone is the layer-off run.

**The reference is S55's layer-off run** (D215, the lead's reading 3), captured at S55's state (session-56 at
9b54398, before any of P1's model code moved) and committed as ``tests/layer_reference_s55.json``. On the
production grid:

- **every field of a full run with ``layer=False``**, of both models at both templates' inputs: sha256 of the
  array's bytes with its dtype and shape, a scalar by its exact value;
- **each route that takes inputs, with ``layer=off``**, for one window and for the whole disc: every array of the
  body (name, dtype, shape, sha256, in the body's order) and the header less ``stages`` (what a request ran depends
  on what the service had already run);
- under ``single_mode``, **the two composed fields as S55 made them with the layer on**, for one arm number - the
  drawn 4, which are the fields S55 published, and 2 - on each template's own scalars. P1's single-mode regression
  is held to these. They are made by ``tests/s55_patterns.py``, a frozen copy of S55's two classes that was the
  classes themselves bit for bit, and the published fields, at capture.

``tests/test_layer.py`` holds every later layer-off run to it, field by field, **with a closed, named list of
exceptions** (``LAYER_OFF_EXCEPTIONS``; at S56 one entry, ``arm_multiplicity``: it was the drawn arm number and is
the derived dominant one).

``uv run python tests/layer_reference.py`` prints the digest's own sha256 and what differs from the reference, and
writes nothing; ``... write`` rewrites the reference, which is a deliberate act a decision must record.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REFERENCE = Path(__file__).resolve().parent / "layer_reference_s55.json"

MODELS = ("azimuthal", "basic")
TEMPLATES = ("milky_way", "ngc_4414")
SINGLE_MODES = (4.0, 2.0)
WINDOW = "r_min=7.5&r_max=9&phi_min=0.2&phi_max=0.9"
NARROW = "r_min=8&r_max=8.4&phi_min=0.3&phi_max=0.4"
# What a header is compared without: only what a request ran, which depends on what the service already held.
DROPPED_KEYS = ("stages",)
# What the render sends since S63 (D223) that S55 did not: the stars split by age and their placing weights.
ADDED_AT_S63 = ("stars_young", "stars_middle", "stars_old", "stars_placement", "stars_middle_placement", "stars_young_placement")
# What S64 (V6, the clouds as extinction) sends that S55 did not: the render's share of each ring's dust that is diffuse
# (with its header entry `clouds`) and the clouds' own dust column (with its entry in the clouds header's `derived`).
ADDED_AT_S64 = ("dust_diffuse_share", "cloud_dust_extinction_v")
# What S70 (Audit V F-4-3) sends that S55 did not: each cloud's face-on shape along the gas field's shear (with their
# entries in the clouds header's `derived`, digested apart with S64's).
ADDED_AT_S70 = ("cloud_axis_ratio", "cloud_angle")
# What S64 (V6, the HII regions as knots) sends that S55 did not: the clusters' line_response (with filters=) and the
# clusters header's entries `knots` and `line_response`; and the sentence each of the render's two HII abouts gains.
ADDED_KNOTS = ("line_response", "knots")
# What S66 (V7, D226 R4-R6) sends that S55 did not: the render header's entries for the viewer's march - the two fields
# and the gas spurs, their values null with the layer off - and its arrays: the placement without the spurs (with the
# layer off the neutral placement itself) named in `placement`, and the middle part's three kept-octave windows (in
# `ages`, digested apart since S63).
ADDED_AT_S66 = ("gas_fluctuation", "census_clustering", "spurs")
ADDED_ARRAYS_AT_S66 = ("dust_placement_unspurred", "stars_middle_kept3", "stars_middle_kept2", "stars_middle_kept1")
# What S73 (#199) sends in place of S66's three header entries, which moved to /api/layer (a route S55 did not have):
# the render header's `layer_tables`, naming the route, and its `template` (the name asked, or null: what a client
# pairs the route's answer by, the review's G2) - digested apart likewise and returned among the added.
ADDED_AT_S73 = ("template", "layer_tables")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def value_digest(value: Any) -> str:
    """A field's value, exactly: an array by dtype, shape and bytes; a scalar by its hex; a label as itself."""
    if isinstance(value, str):
        return "label:" + value
    arr = np.asarray(value)
    if arr.ndim == 0:
        return "scalar:" + float(arr).hex()
    arr = np.ascontiguousarray(arr)
    return f"{arr.dtype.str}{list(arr.shape)}:" + _sha(arr.tobytes())


def normalise(header: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(header)
    for key in DROPPED_KEYS:
        out.pop(key, None)
    _s67_cloud_layer(out)
    return out


def _s67_cloud_layer(header: dict[str, Any]) -> None:
    """A by-decision carve-out (S67, D229): the clouds' layer - the render's ``layers.halpha_hii`` and ``lines_hii``,
    and the ``clouds`` entry's ``layers.clouds_scale_height`` - is since S67 the molecular layer's measured thickness
    (MOLECULAR_LAYER_FWHM 120 pc, h = 34.04 pc), a constant of the model; S55 had it at half the thin disc's scale
    height, the stars' layer ``layers.stars``, with ``thin_disc_scale_height`` last among the HII components' fields.
    The header is digested with those words put back as S55's rule made them - 0.5 x layers.stars, exact (a power of
    two) - so every other word of it is still held to S55's. The new values are pinned in tests/test_render.py."""
    layers = header.get("layers")
    if not isinstance(layers, dict) or not isinstance(layers.get("stars"), float):
        return
    s55 = 0.5 * layers["stars"]
    for name in ("halpha_hii", "lines_hii"):
        if name in layers:
            layers[name] = s55
    clouds = header.get("clouds")
    if isinstance(clouds, dict) and isinstance(clouds.get("layers"), dict) and "clouds_scale_height" in clouds["layers"]:
        clouds["layers"]["clouds_scale_height"] = s55
    for name in ("halpha_hii", "lines_hii"):
        comp = header.get("components", {}).get(name)
        if isinstance(comp, dict) and isinstance(comp.get("fields"), list) and "thin_disc_scale_height" not in comp["fields"]:
            comp["fields"] = [*comp["fields"], "thin_disc_scale_height"]


def curves() -> str:
    from galaxy.stages import spectra

    return json.dumps([spectra.band_curve(b).json() for b in ("B", "V")])


def requests() -> list[tuple[str, str, dict[str, list[str]]]]:
    """(label, path, query) for every digested request, each asked with ``layer=off``. Queries are mappings so the
    curves need no escaping."""

    def q(text: str = "", **more: str) -> dict[str, list[str]]:
        pairs = [p.split("=", 1) for p in text.split("&") if p]
        return {**{k: [v] for k, v in pairs}, **{k: [v] for k, v in more.items()}, "layer": ["off"]}

    out: list[tuple[str, str, dict[str, list[str]]]] = []
    for model in MODELS:
        m = f"model={model}"
        out += [
            (f"{model}/region/window", "/api/region", q(f"{m}&{WINDOW}")),
            (f"{model}/region/disc", "/api/region", q(m)),
            (f"{model}/region/level2", "/api/region", q(f"{m}&{NARROW}&level=2")),
            (f"{model}/region/brightest", "/api/region", q(f"{m}&brightest=2000")),
            (f"{model}/system", "/api/system", q(f"{m}&cell=300&index=0")),
            (f"{model}/clouds/window", "/api/clouds", q(f"{m}&{WINDOW}")),
            (f"{model}/clouds/disc", "/api/clouds", q(m)),
            (f"{model}/clouds/level1", "/api/clouds", q(f"{m}&{WINDOW}&level=1")),
            (f"{model}/clusters/window", "/api/clusters", q(f"{m}&{WINDOW}")),
            (f"{model}/clusters/disc", "/api/clusters", q(m)),
            (f"{model}/clusters/filters", "/api/clusters", q(f"{m}&{WINDOW}", filters=curves())),
            (f"{model}/remnants/window", "/api/remnants", q(f"{m}&{WINDOW}")),
            (f"{model}/remnants/disc", "/api/remnants", q(m)),
            (f"{model}/bright/disc", "/api/bright", q(f"{m}&n=5000")),
            (f"{model}/bright/window", "/api/bright", q(f"{m}&{WINDOW}&l_min=10000")),
            (f"{model}/render/disc", "/api/render", q(m, filters=curves())),
            (f"{model}/render/unresolved", "/api/render", q(f"{m}&l_min=1000", filters=curves())),
            (f"{model}/render/level1", "/api/render", q(f"{m}&{WINDOW}&level=1", filters=curves())),
            (f"{model}/arrays", "/api/arrays", q(f"{m}&fields=sfr_surface_density,cloud_count_total,pattern_density_contrast")),
        ]
    out += [
        ("ngc_4414/clouds/disc", "/api/clouds", q("template=ngc_4414")),
        ("ngc_4414/clusters/window", "/api/clusters", q(f"template=ngc_4414&{WINDOW}")),
        ("ngc_4414/region/window", "/api/region", q(f"template=ngc_4414&{WINDOW}")),
        ("ngc_4414/render/disc", "/api/render", q("template=ngc_4414", filters=curves())),
    ]
    return out


def route_digest(service: Any, path: str, query: dict[str, list[str]]) -> dict[str, Any]:
    from galaxy.api import wire

    from galaxy.core.registry import pins

    got = service.handle(path, query)
    if not got.ok:
        return {"status": got.status, "error": got.json().get("error")}
    header, arrays = wire.decode(got.body)
    # S58 (D217 item 2): a template's pin rides among a request's inputs, and S55 knew none. The header is digested
    # with the pins taken out of its inputs - so every other word of it is still held to S55's - and the pins it
    # carried are returned beside the digest, for the test to read (none, but for a template that states one).
    header = normalise(header)
    pinned = {i.name: header["inputs"].pop(i.name) for i in pins() if i.name in header.get("inputs", {})}
    # S63 (D223): the render's light by age - its header's `ages`, three per-ring arrays and the weights that place
    # them - which S55 did not send. Digested with them taken out, so every other word and array is still S55's; the
    # arrays are returned beside the digest, for the test to read.
    added = [spec["name"] for spec in header.get("arrays", []) if spec["name"] in ADDED_AT_S63]
    if added:
        header.pop("ages", None)
        header["arrays"] = [spec for spec in header["arrays"] if spec["name"] not in ADDED_AT_S63]
        header["axes"] = {k: v for k, v in header["axes"].items() if k not in ADDED_AT_S63}
    # S64 (V6): the clouds as extinction - the render's diffuse share and its header entry, the clouds' dust column and
    # its entry - digested apart in the same way, and returned among the added.
    s64 = [spec["name"] for spec in header.get("arrays", []) if spec["name"] in ADDED_AT_S64]
    if s64:
        if "dust_diffuse_share" in s64:
            header.pop("clouds", None)
        if "cloud_dust_extinction_v" in s64:
            header["clouds"].pop("derived", None)
            header["columns"] = [c for c in header["columns"] if c not in ADDED_AT_S64]
        header["arrays"] = [spec for spec in header["arrays"] if spec["name"] not in ADDED_AT_S64]
        if "axes" in header:
            header["axes"] = {k: v for k, v in header["axes"].items() if k not in ADDED_AT_S64}
    added += s64
    # S70 (Audit V F-4-3): the clouds' shape, two columns after the dust column (their entries went with `derived`
    # above), digested apart likewise and returned among the added.
    s70 = [spec["name"] for spec in header.get("arrays", []) if spec["name"] in ADDED_AT_S70]
    if s70:
        header["columns"] = [c for c in header["columns"] if c not in ADDED_AT_S70]
        header["arrays"] = [spec for spec in header["arrays"] if spec["name"] not in ADDED_AT_S70]
    added += s70
    # S64 (V6, R5): the HII regions as knots - the clusters' line_response and its header entries, and the sentence the
    # render's halpha_hii and lines_hii abouts gain - digested apart likewise; the clusters' returned among the added.
    if "knots" in header:
        from galaxy.api import v6_knots

        lines = [spec["name"] for spec in header.get("arrays", []) if spec["name"] == v6_knots.COLUMN]
        header.pop("knots")
        header.pop(v6_knots.COLUMN, None)
        header["arrays"] = [spec for spec in header["arrays"] if spec["name"] != v6_knots.COLUMN]
        if "axes" in header:
            header["axes"] = {k: v for k, v in header["axes"].items() if k != v6_knots.COLUMN}
        added += [*lines, "knots"]
    # S66 (V7, R4-R6): the render header's three new entries and its four new arrays (with the placement's two words of
    # them), digested apart and returned among the added (D223's handling).
    s66_arrays = [spec["name"] for spec in header.get("arrays", []) if spec["name"] in ADDED_ARRAYS_AT_S66]
    if s66_arrays:
        header["arrays"] = [spec for spec in header["arrays"] if spec["name"] not in ADDED_ARRAYS_AT_S66]
        header["axes"] = {k: v for k, v in header["axes"].items() if k not in ADDED_ARRAYS_AT_S66}
        if isinstance(header.get("placement"), dict):
            header["placement"].pop("dust_unspurred", None)
            header["placement"].get("arrays", {}).pop("dust_placement_unspurred", None)
    s66 = [key for key in ADDED_AT_S66 if key in header and "components" in header]
    for key in s66:
        header.pop(key)
    # S73 (#199): the three entries are /api/layer's; the render's header names the route instead.
    s73 = [key for key in ADDED_AT_S73 if key in header and "components" in header]
    for key in s73:
        header.pop(key)
    added += s66_arrays + s66 + s73
    components = header.get("components", {})
    if "halpha_hii" in components:
        from galaxy.api import v6_knots

        for name, words in (("halpha_hii", v6_knots.HALPHA_WORDS), ("lines_hii", v6_knots.LINES_WORDS)):
            if name in components and words in components[name].get("about", ""):
                components[name]["about"] = components[name]["about"].replace(words, "", 1)
    out = {
        "status": got.status,
        "header": _sha(json.dumps(header, sort_keys=True).encode("utf-8")),
        "arrays": [[spec["name"], value_digest(arrays[spec["name"]])] for spec in header["arrays"]],
    }
    if added:
        out["added"] = added
    if pinned:
        out["pinned"] = pinned
    return out


def run_digest(model_name: str, inputs: dict[str, Any] | None = None, **run_kwargs: Any) -> dict[str, str]:
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    out = run(models.get(model_name), inputs, **run_kwargs)
    return {name: value_digest(out.fields[name]) for name in sorted(out.fields)}


def template_inputs(template: str) -> dict[str, Any]:
    from galaxy import templates

    return templates.overrides(templates.TEMPLATES[template])


def label(model: str, template: str) -> str:
    return model if template == "milky_way" else f"{model}@{template}"


def fields_digest() -> dict[str, dict[str, str]]:
    return {label(model, t): run_digest(model, template_inputs(t), layer=False) for t in TEMPLATES for model in MODELS}


def routes_digest(labels: tuple[str, ...] | None = None) -> dict[str, dict[str, Any]]:
    from galaxy.api.service import Service

    service = Service()
    return {name: route_digest(service, path, query) for name, path, query in requests() if labels is None or name in labels}


def single_mode_scalars(template: str) -> dict[str, float]:
    """The scalars S55's two laws were built from, on the default model at a template's inputs. None of them is the
    arm number: the pitch, the two amplitudes, the bar's length and the gas's ratio keep their streams in P1.

    **S58 (D217): read with the template's pins taken off.** S55 knew no pin and every galaxy had a bar; since S58
    ``ngc_4414`` is pinned unbarred and publishes NaN for its bar's numbers. The numbers S55 drew are still the
    model's - every draw keeps its stream and value - and are read where the model derives its presence (which bars
    this disc, as it bars the Milky Way's): the template's controls, seeds and merger list, and no pin."""
    from galaxy import templates
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    names = ("arm_contrast", "bar_contrast", "pitch_angle", "bar_half_length", "gas_arm_contrast")
    pinned = templates.pinned(templates.TEMPLATES[template])
    inputs = {k: v for k, v in template_inputs(template).items() if k not in pinned}
    out = run(models.get(MODELS[0]), inputs, only=(*names, "bar_present"), layer=False)
    assert out.fields["bar_present"] == "yes", "S55's scalars are a barred galaxy's: the derivation must bar this disc"
    return {n: float(out.fields[n]) for n in names}


def single_mode_fields(template: str, m: float) -> tuple[np.ndarray, np.ndarray]:
    """(stars, gas): S55's two composed fields on the production grid for one arm number, by the frozen copy."""
    import gas_check
    import s55_patterns as s55
    from galaxy.core.grids import DEFAULT

    f = single_mode_scalars(template)
    grid = DEFAULT.build()
    stars = s55.stellar_contrast(grid.R, grid.phi, f["arm_contrast"], f["bar_contrast"], m, f["pitch_angle"], f["bar_half_length"])
    # S57 (D216, gate G3 item 7): the ridge's width and the mask's were constants of the model until S57 and are
    # read from tests/gas_check.py since - the same two numbers S55 used (0.17, 1.5 kpc), so the same bits.
    gas = s55.gas_contrast(grid.R, grid.phi, f["gas_arm_contrast"], f["bar_contrast"], m, f["pitch_angle"], f["bar_half_length"],
                           gas_check.GAS_ARM_WIDTH, gas_check.GAS_ARM_MASK_WIDTH)
    return stars, gas


def single_mode_digest() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {}
    for template in TEMPLATES:
        for m in SINGLE_MODES:
            stars, gas = single_mode_fields(template, m)
            out.setdefault(template, {})[f"m{m:.0f}"] = {"stars": value_digest(stars), "gas": value_digest(gas)}
    return out


def digest() -> dict[str, Any]:
    return {"fields": fields_digest(), "routes": routes_digest(), "single_mode": single_mode_digest()}


def load() -> dict[str, Any]:
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def differences(made: dict[str, Any], held: dict[str, Any]) -> list[str]:
    moved = [f"fields/{m}/{n}" for m, fs in held["fields"].items() for n, v in fs.items() if made["fields"].get(m, {}).get(n) != v]
    # (a route's digest is compared on what the reference holds of it: the pins a header carries since S58 are beside it)
    moved += [f"routes/{k}" for k, v in held["routes"].items() if {n: made["routes"].get(k, {}).get(n) for n in v} != v]
    moved += [f"single_mode/{t}/{m}" for t, ms in held["single_mode"].items() for m, v in ms.items()
              if made["single_mode"].get(t, {}).get(m) != v]
    return moved


def main(argv: list[str]) -> int:
    made = digest()
    text = json.dumps(made, indent=1, sort_keys=True) + "\n"
    print("layer-off digest sha256", _sha(text.encode("utf-8")), "fields", {k: len(v) for k, v in made["fields"].items()},
          "routes", len(made["routes"]))
    if argv[1:] == ["write"]:
        with open(REFERENCE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", REFERENCE.name)
    elif REFERENCE.exists():
        print("differs from the reference:", differences(made, load()) or "nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
