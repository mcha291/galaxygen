"""The S54 reference the layer's switch is held to (S55, BUILD_III Phase R; DECISIONS.md D214).

Phase R is behaviour-preserving: with the layer on, every published field, every catalogue column and every
scalar is bit-identical to S54's. This module is the digest that says so. It was **run once at S54's state
(session-55 at 90d198b, before any of Phase R's model code moved)** and its output committed as
``tests/layer_reference_s54.json``; ``tests/test_layer.py`` recomputes it and compares.

What is digested, on the production grid:

- **every field of a full run** of both models at the default inputs, and of the default model at
  ``ngc_4414``'s inputs: sha256 of the array's bytes with its dtype and shape, a scalar by its exact value;
- **each route that takes inputs**, for one window and for the whole disc: every array of the body (name,
  dtype, shape, sha256, in the body's order) and the header.

**The header is compared after the keys Phase R adds are taken out** (:func:`normalise`): the fifth seed
among ``inputs`` (``texture_seed``, D214 section 3), the ``layer`` echo (section 1), ``/api/clouds``'
``cloud_interior`` (the cloud-interior noise's three parameters, constants of the model: section 5 as ruled at
gate G1, change 4 - until then three scalars, which a first pass of this module took out of ``scalars``), and
``stages`` (what a request ran depends on what the service had already run). A body's own sha256 is recorded
too, for the record: it is not compared, because those additions change it by construction. **Phase R adds no
field**: a layer-on run's fields are S54's, name for name.

``uv run python tests/layer_reference.py`` prints the digest's own sha256 and writes nothing;
``... write`` rewrites the reference, which is a deliberate act a decision must record.

**Since S56 (D215) there is a second reference, of S55 with the layer off** (``... off`` / ``... write-off``,
``tests/layer_reference_s55.json``): see the section at the end of this module.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REFERENCE = Path(__file__).resolve().parent / "layer_reference_s54.json"

MODELS = ("azimuthal", "basic")
WINDOW = "r_min=7.5&r_max=9&phi_min=0.2&phi_max=0.9"
NARROW = "r_min=8&r_max=8.4&phi_min=0.3&phi_max=0.4"
# Phase R's additions to a header, taken out before it is compared (the module's docstring).
ADDED_INPUTS = ("texture_seed",)
ADDED_KEYS = ("layer", "stages", "cloud_interior")


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
    for key in ADDED_KEYS:
        out.pop(key, None)
    if isinstance(out.get("inputs"), dict):
        for name in ADDED_INPUTS:
            out["inputs"].pop(name, None)
    return out


def curves() -> str:
    from galaxy.stages import spectra

    return json.dumps([spectra.band_curve(b).json() for b in ("B", "V")])


def requests() -> list[tuple[str, str, dict[str, list[str]]]]:
    """(label, path, query) for every digested request. Queries are mappings so the curves need no escaping."""

    def q(text: str = "", **more: str) -> dict[str, list[str]]:
        pairs = [p.split("=", 1) for p in text.split("&") if p]
        return {**{k: [v] for k, v in pairs}, **{k: [v] for k, v in more.items()}}

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

    got = service.handle(path, query)
    if not got.ok:
        return {"status": got.status, "error": got.json().get("error")}
    header, arrays = wire.decode(got.body)
    return {
        "status": got.status,
        "header": _sha(json.dumps(normalise(header), sort_keys=True).encode("utf-8")),
        "arrays": [[spec["name"], value_digest(arrays[spec["name"]])] for spec in header["arrays"]],
        "body": _sha(got.body),
    }


def run_digest(model_name: str, inputs: dict[str, Any] | None = None, **run_kwargs: Any) -> dict[str, str]:
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    out = run(models.get(model_name), inputs, **run_kwargs)
    return {name: value_digest(out.fields[name]) for name in sorted(out.fields)}


def template_inputs(name: str) -> dict[str, Any]:
    """A template's overrides, less the seed Phase R adds (it has no reader, so it moves no field)."""
    from galaxy import templates

    given = templates.overrides(templates.TEMPLATES[name])
    return {k: v for k, v in given.items() if k not in ADDED_INPUTS}


def fields_digest() -> dict[str, dict[str, str]]:
    out = {model: run_digest(model) for model in MODELS}
    out["azimuthal@ngc_4414"] = run_digest("azimuthal", template_inputs("ngc_4414"))
    return out


def routes_digest(labels: tuple[str, ...] | None = None) -> dict[str, dict[str, Any]]:
    from galaxy.api.service import Service

    service = Service()
    return {label: route_digest(service, path, query) for label, path, query in requests() if labels is None or label in labels}


def digest() -> dict[str, Any]:
    return {"fields": fields_digest(), "routes": routes_digest()}


def load() -> dict[str, Any]:
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


# --- the layer-off reference (S56, DECISIONS.md D215) --------------------------------------------------------------
#
# From Phase P1 the layer-on galaxy changes by design (several arm modes at once, their phases a new draw), so S54's
# layer-on reference above stops being a statement about anything. **The reference becomes S55's layer-off run**
# (D215, the lead's reading 3): every field of both models at both templates' inputs with ``layer=False``, and every
# input route with ``layer=off``, digested at S55's state (session-56 at 9b54398, before any of P1's model code
# moved) and committed as ``tests/layer_reference_s55.json``. A later phase holds its layer-off run to it, field by
# field, with a closed, named list of exceptions.
#
# It also holds, under ``single_mode``, the two composed fields **as S55 made them with the layer on** - the stellar
# contrast and the gas's ridge on each template's own scalars, at the drawn arm number (4 for both) and at 2 - which
# is what P1's single-mode regression is held to. They are made by ``tests/s55_patterns.py``, a frozen copy of S55's
# two classes that was checked bit for bit against the classes themselves, and against the published fields, at
# capture.

REFERENCE_OFF = Path(__file__).resolve().parent / "layer_reference_s55.json"
TEMPLATES_OFF = ("milky_way", "ngc_4414")
SINGLE_MODES = (4.0, 2.0)
# What a header is compared without: only what a request ran, which depends on what the service already held.
OFF_KEYS = ("stages",)


def off_inputs(template: str) -> dict[str, Any]:
    from galaxy import templates

    return templates.overrides(templates.TEMPLATES[template])


def off_label(model: str, template: str) -> str:
    return model if template == "milky_way" else f"{model}@{template}"


def fields_digest_off() -> dict[str, dict[str, str]]:
    return {off_label(model, t): run_digest(model, off_inputs(t), layer=False) for t in TEMPLATES_OFF for model in MODELS}


def normalise_off(header: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(header)
    for key in OFF_KEYS:
        out.pop(key, None)
    return out


def routes_digest_off(labels: tuple[str, ...] | None = None) -> dict[str, dict[str, Any]]:
    from galaxy.api import wire
    from galaxy.api.service import Service

    service = Service()
    out: dict[str, dict[str, Any]] = {}
    for label, path, query in requests():
        if labels is not None and label not in labels:
            continue
        got = service.handle(path, {**query, "layer": ["off"]})
        if not got.ok:
            out[label] = {"status": got.status, "error": got.json().get("error")}
            continue
        header, arrays = wire.decode(got.body)
        out[label] = {
            "status": got.status,
            "header": _sha(json.dumps(normalise_off(header), sort_keys=True).encode("utf-8")),
            "arrays": [[spec["name"], value_digest(arrays[spec["name"]])] for spec in header["arrays"]],
        }
    return out


def single_mode_scalars(template: str) -> dict[str, float]:
    """The scalars S55's two laws were built from, on the default model at a template's inputs. None of them is the
    arm number: the pitch, the two amplitudes, the bar's length and the gas's ratio keep their streams in P1."""
    from galaxy.core.registry import production
    from galaxy.run import run

    models, _, _ = production()
    names = ("arm_contrast", "bar_contrast", "pitch_angle", "bar_half_length", "gas_arm_contrast")
    out = run(models.get(MODELS[0]), off_inputs(template), only=names, layer=False)
    return {n: float(out.fields[n]) for n in names}


def single_mode_fields(template: str, m: float) -> tuple[np.ndarray, np.ndarray]:
    """(stars, gas): S55's two composed fields on the production grid for one arm number, by the frozen copy."""
    import s55_patterns as s55
    from galaxy.core.grids import DEFAULT
    from galaxy.core.registry import production

    models, _, _ = production()
    c = models.get(MODELS[0]).constants
    f = single_mode_scalars(template)
    grid = DEFAULT.build()
    stars = s55.stellar_contrast(grid.R, grid.phi, f["arm_contrast"], f["bar_contrast"], m, f["pitch_angle"], f["bar_half_length"])
    gas = s55.gas_contrast(grid.R, grid.phi, f["gas_arm_contrast"], f["bar_contrast"], m, f["pitch_angle"], f["bar_half_length"],
                           float(c["GAS_ARM_WIDTH"].value), float(c["GAS_ARM_MASK_WIDTH"].value))
    return stars, gas


def single_mode_digest() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {}
    for template in TEMPLATES_OFF:
        for m in SINGLE_MODES:
            stars, gas = single_mode_fields(template, m)
            out.setdefault(template, {})[f"m{m:.0f}"] = {"stars": value_digest(stars), "gas": value_digest(gas)}
    return out


def digest_off() -> dict[str, Any]:
    return {"fields": fields_digest_off(), "routes": routes_digest_off(), "single_mode": single_mode_digest()}


def load_off() -> dict[str, Any]:
    return json.loads(REFERENCE_OFF.read_text(encoding="utf-8"))


def main_off(argv: list[str]) -> int:
    made = digest_off()
    text = json.dumps(made, indent=1, sort_keys=True) + "\n"
    print("layer-off digest sha256", _sha(text.encode("utf-8")), "fields", {k: len(v) for k, v in made["fields"].items()},
          "routes", len(made["routes"]))
    if argv[1:] == ["write-off"]:
        with open(REFERENCE_OFF, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", REFERENCE_OFF.name)
    elif REFERENCE_OFF.exists():
        held = load_off()
        moved = [f"fields/{m}/{n}" for m, fs in made["fields"].items() for n, v in fs.items() if held["fields"].get(m, {}).get(n) != v]
        moved += [f"routes/{k}" for k, v in made["routes"].items() if v != held["routes"].get(k)]
        moved += [f"single_mode/{t}/{m}" for t, ms in made["single_mode"].items() for m, v in ms.items() if held["single_mode"].get(t, {}).get(m) != v]
        print("differs from the layer-off reference:", moved or "nothing")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] in (["off"], ["write-off"]):
        return main_off(argv)
    made = digest()
    text = json.dumps(made, indent=1, sort_keys=True) + "\n"
    print("digest sha256", _sha(text.encode("utf-8")), "fields", {k: len(v) for k, v in made["fields"].items()},
          "routes", len(made["routes"]))
    if argv[1:] == ["write"]:
        with open(REFERENCE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote", REFERENCE.name)
    elif REFERENCE.exists():
        held = load()
        moved = [f"fields/{m}/{n}" for m, fs in made["fields"].items() for n, v in fs.items() if held["fields"].get(m, {}).get(n) != v]
        moved += [f"routes/{k}" for k, v in made["routes"].items()
                  if {a: b for a, b in v.items() if a != "body"} != {a: b for a, b in held["routes"].get(k, {}).items() if a != "body"}]
        print("differs from the reference:", moved or "nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
