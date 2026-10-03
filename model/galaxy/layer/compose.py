"""compose: a law applied to a realisation, and the one place the layer's switch is read.

BUILD_III section 1a: "a composed field - a density contrast over (R, phi), a census placement - is a law applied
to a realisation". The physics stages hold the laws (how strong an arm is, how wide the gas ridge, how many clouds a
ring holds); the layer holds the realisations (where the arms are, how a cloud leans). This module is where the two
meet, and **the only place in the model that asks whether the layer is on** (DECISIONS.md D214 sections 1 and 4;
rule B13: a switch read in one place cannot be forgotten in another). ``tests/test_layer.py`` holds that by reading
the source: no other module under ``model/galaxy/`` branches on the setting, and none calls ``.from_fields(``.

**What a caller gets.**

- A *pattern object* (:func:`stellar_pattern`, :func:`gas_pattern`): the law's own class, built from the pattern
  stages' published scalars - or ``None`` with the layer off, which is the "no pattern" every census already
  handles for a model that publishes none (a uniform weight round the ring).
- A *placement weight* (:func:`placement_weight`): a published composed field as a census reads it - the array, or
  ``None`` with the layer off or where the model publishes none.
- A *composed field* (:func:`field`): what a composing stage publishes over (R, phi) - what its law makes, or ones
  with the layer off. :func:`published` reads one back from a run's fields (it is ones there with the layer off).
- A *realisation* (:func:`realise`, :func:`cloud_texture`): what a layer stage draws, or its neutral value.

With the layer off every scalar the physics stages publish is unchanged - the arm number, the pitch, the
amplitudes, the gas's ratio of means are laws and measured scatters, and they are still drawn. What is switched off
is where the arms *are* (D214 section 1).

**How the setting reaches here.** ``run(model, inputs, grid, layer=...)`` gives it to every stage's
:class:`~galaxy.core.stage.Context` and records it on the run's fields (:class:`~galaxy.core.stage.Fields`, and the
restricted view a stage sees, :class:`~galaxy.core.stage.FieldView`). Every function here takes that mapping - a
stage's ``ctx.fields`` or a run's ``Outputs.fields`` - and reads the setting from it, so a catalogue materialised
from a run's fields is placed as that run was: there is no second argument to get wrong. A plain ``dict`` of fields
carries no setting and is refused (:class:`~galaxy.core.stage.LayerError`).

**Who may ask.** A stage's view also says whether the stage may place by the layer (``Stage.may_place``: a
placement reader, a composing stage or a layer stage - invariant I4). The graph refuses any other stage that
*requires* a composed or synthetic field; this module refuses one that *asks* for a pattern object or a weight,
which the graph cannot see because a pattern object is rebuilt from scalars.

The laws' classes live with the stages that publish them and are imported when called, not at module load: the
pattern stages import this module to publish their composed fields.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from types import MappingProxyType
from typing import Any

import numpy as np

from galaxy.core.stage import LayerError, UndeclaredAccess

# The switch as a request spells it (``layer=off``; absent is on) and as a response echoes it.
SETTINGS: Mapping[str, bool] = MappingProxyType({"on": True, "off": False})


def _on(source: Any) -> bool:
    """Whether the run ``source`` belongs to composes the layer. ``source`` is a run's fields or a stage's view of
    them (or a stage's context, whose view is taken)."""
    fields = getattr(source, "fields", source)
    try:
        layer = fields.layer
    except AttributeError:
        raise LayerError(
            f"a {type(fields).__name__} of fields does not say whether the randomness layer is on: pass a run's "
            "Outputs.fields or a stage's ctx.fields, which carry the run's setting (galaxy.core.stage.Fields)"
        ) from None
    if not getattr(fields, "placement", True):
        raise UndeclaredAccess(
            f"stage {fields._stage!r} asked the layer for a placement without being a placement reader, a "
            "composing stage or a layer stage (invariant I4): declare placement_reader=True if it is a census"
        )
    return bool(layer)


def setting(source: Any) -> str:
    """``"on"`` or ``"off"``: the run's setting as a response echoes it and a cache key carries it."""
    return "on" if _on(source) else "off"


def agree(fields: Any, layer: bool) -> None:
    """Refuse to continue a run under the other setting: its composed fields were made under its own."""
    if _on(fields) != bool(layer):
        raise LayerError(
            f"cannot resume: the run was made with the layer {setting(fields)} and is asked for with it "
            f"{'on' if layer else 'off'}"
        )


# --- pattern objects -----------------------------------------------------------------------------------


def stellar_pattern(source: Any) -> Any:
    """The stellar arm and bar pattern (``pattern.ArmPattern``) from the published scalars, or None: with the
    layer off, or where the fields hold no pattern."""
    if not _on(source):
        return None
    from galaxy.stages.pattern import ArmPattern

    return ArmPattern.from_fields(getattr(source, "fields", source))


def gas_pattern(source: Any, constants: Mapping[str, Any]) -> Any:
    """The gas's own arm pattern (``gas_pattern.GasPattern``) from the published scalars and the ridge's two
    constants, or None: with the layer off, or where the fields hold no pattern."""
    if not _on(source):
        return None
    from galaxy.stages.gas_pattern import GasPattern

    return GasPattern.from_fields(getattr(source, "fields", source), constants)


# --- composed fields -----------------------------------------------------------------------------------


def field(source: Any, shape: tuple[int, ...], make: Callable[[], np.ndarray]) -> np.ndarray:
    """A composed (R, phi) field: ``make()``, the law applied to the realisation, or its neutral value - 1
    everywhere - with the layer off. ``make`` is not called then: nothing of the realisation is computed."""
    if not _on(source):
        return np.ones(shape)
    return make()


def published(source: Any, name: str) -> Any:
    """A composed field as a run published it, or None where the model publishes none. With the layer off the
    run published ones (:func:`field`), so this is the neutral value then. For a reader that draws the field
    itself - the API's render - rather than placing a census by it."""
    _on(source)  # a mapping that does not carry the setting is refused here as everywhere
    fields = getattr(source, "fields", source)
    return fields.get(name)


def placement_weight(source: Any, name: str) -> Any:
    """A published composed field as a census places by it: the array, or None - with the layer off, or where
    the model publishes none. None is the uniform weight a census already takes for a model without the field,
    so a layer-off catalogue is drawn by exactly the arithmetic of a model that has no such field."""
    if not _on(source):
        return None
    fields = getattr(source, "fields", source)
    return fields.get(name)


# --- realisations --------------------------------------------------------------------------------------


def realise(source: Any, draw: Callable[[], Any], neutral: Callable[[], Any]) -> Any:
    """What a layer stage publishes: ``draw()``, or ``neutral()`` with the layer off."""
    return draw() if _on(source) else neutral()


def cloud_texture(source: Any, seed: int, counts: Sequence[tuple[int, int]], size: np.ndarray) -> dict[str, np.ndarray]:
    """The four cloud texture columns for a census's cells (``layer/cloud_texture.py``): drawn on the cells' own
    streams, or zero with the layer off - no offset, no gradient, angles 0."""
    from galaxy.layer import cloud_texture as _texture

    return realise(source, lambda: _texture.draw(seed, counts, size), lambda: _texture.neutral(len(size)))
