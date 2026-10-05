"""compose: a law applied to a realisation, and the one place the layer's switch is read.

BUILD_III section 1a: "a composed field - a density contrast over (R, phi), a census placement - is a law applied
to a realisation". The physics stages hold the laws (how strong an arm is, how the gas answers it, how many clouds a
ring holds); the layer holds the realisations (where the arms are, how a cloud leans). This module is where the two
meet, and **the only place in the model that asks whether the layer is on** (DECISIONS.md D214 sections 1 and 4;
rule B13: a switch read in one place cannot be forgotten in another). ``tests/test_layer.py`` holds that by reading
the source: no other module under ``model/galaxy/`` branches on the setting, none calls ``.from_fields(``, and
none constructs a pattern object by its class (since S56 the pattern stage itself asks here for the pattern of its
own composed field, handing over the law it has just made).

**What a caller gets.**

- A *pattern object* (:func:`stellar_pattern`, :func:`gas_pattern`): the law's own class, built from the pattern
  stage's published fields (the arm modes' amplitudes at every radius, the pitch, the bar) and the layer's
  realisation (the modes' phases, S56) - or ``None`` with the layer off, which is the "no pattern" every census
  already handles for a model that publishes none (a uniform weight round the ring).
- A *placement weight* (:func:`placement_weight`): a published composed field as a census reads it - the array, or
  ``None`` with the layer off or where the model publishes none.
- A *composed field* (:func:`field`): what a composing stage publishes - what its law makes, or with the layer off
  the neutral value **its declaration states** (``FieldDecl(composed=True, neutral=...)``; gate G1, change 3: a
  field is composed because it says so, never because of its axes). :func:`published` reads one back from a run's
  fields (it is its neutral there with the layer off).
- A *realisation* (:func:`realise`, :func:`realise_scalars`, :func:`cloud_texture`): what a layer stage draws,
  or - with the layer off - its neutral value, which for a scalar that was not realised is NaN (D215).

With the layer off every scalar and every radial field the physics stages publish is unchanged - the pitch, the
amplitudes, the modes' split of the arms' power, the gas's ratio of means are laws and measured scatters, and they
are still made. What is switched off is where the arms *are* (D214 section 1): the modes' phases are not drawn. **What the switch keeps, exactly** (BUILD_III section 1c rule 2 and 1d as
amended at G1): every ring total of a field a composed field multiplies, and every *expected* count and expected
total of a census it places. A census draws each cell's count on the cell's own stream at an expectation that
carries the composed weight, so with the layer off its *realised* objects are another draw, and the statistics
computed from them move by that re-draw noise until L1's ring-first draw.

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

from collections import ChainMap
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


def words(source: Any, on: str, off: str) -> str:
    """One of two texts by the run's setting: for a response that describes what it placed by, so that what it
    says of a composed field is true with the layer off too (gate G1, change 11)."""
    return on if _on(source) else off


def agree(fields: Any, layer: bool) -> None:
    """Refuse to continue a run under the other setting: its composed fields were made under its own."""
    if _on(fields) != bool(layer):
        raise LayerError(
            f"cannot resume: the run was made with the layer {setting(fields)} and is asked for with it "
            f"{'on' if layer else 'off'}"
        )


# --- pattern objects -----------------------------------------------------------------------------------


def stellar_pattern(source: Any, R: np.ndarray, law: Mapping[str, Any] | None = None) -> Any:
    """The stellar pattern of arm pieces and the bar (``pieces.ArmPattern``): the law's published fields - the
    pieces' amplitude and width on the run's grid radii ``R``, the pitch, the bar - applied to the layer's
    realisation, the census of arm pieces (S60, D219; from S56 to S59 it was five modes' amplitudes applied to
    five drawn phases). None with the layer off, or where the fields hold no pattern.

    Since S58 (D217) the bar is a body: its length and shape, its share of the disc's mass and the disc's
    surface density that share is of are among the fields read, and every reader builds the same body from
    them. An unbarred galaxy - the bar's numbers NaN - gives a pattern of arm pieces alone, not None.

    ``law`` is for the composing stage itself: the ``stellar_pattern`` stage has just made the pieces'
    amplitude and has not published it yet, so it hands it here and the rest - the pieces, the width, the pitch,
    the bar, the disc - is read from its view of the fields. Everyone else reads everything from the run."""
    if not _on(source):
        return None
    from galaxy.stages.pieces import ArmPattern

    fields = getattr(source, "fields", source)
    return ArmPattern.from_fields(fields if law is None else ChainMap(dict(law), fields), R)


def gas_pattern(source: Any, R: np.ndarray, constants: Mapping[str, Any]) -> Any:
    """The gas's own arm pattern (``gas_pattern.GasPattern``) - the gas's steady response to the stellar arms,
    solved ring by ring (S57, D216), blended inside a bar's reach with the bar's gas lanes (S58, D217) -
    from the published fields on the run's grid radii ``R`` and the constants the law reads (the gas's sound
    speed and G; the stellar layer's flattening; the lanes' four numbers), or None: with the layer off, or
    where the fields hold no pattern.

    Since S60 (D219) the gas answers the stellar pattern's arm pieces: the stellar pattern of the same fields is
    built here and handed to it, so the two are one census read once and no stage builds a pattern itself."""
    if not _on(source):
        return None
    from galaxy.stages.gas_pattern import GasPattern

    return GasPattern.from_fields(getattr(source, "fields", source), R, constants, stellar_pattern(source, R))


# --- composed fields -----------------------------------------------------------------------------------


def neutral(decl: Any, shape: tuple[int, ...]) -> np.ndarray:
    """A composed field at its declared neutral value everywhere (``FieldDecl.neutral``): what it is with the layer
    off, and what a law that has nothing to place (a flat pattern) makes with it on."""
    if not getattr(decl, "composed", False):
        raise LayerError(
            f"field {getattr(decl, 'name', decl)!r} is not declared composed: only a declared composed field has a "
            "neutral value (FieldDecl(composed=True, neutral=...))"
        )
    return np.full(shape, decl.neutral)


def field(source: Any, decl: Any, shape: tuple[int, ...], make: Callable[[], np.ndarray]) -> np.ndarray:
    """A composed field: ``make()``, the law applied to the realisation, or - with the layer off - the neutral value
    its declaration states, everywhere. ``decl`` is the field's own ``FieldDecl``, which must declare it composed;
    the neutral is read from it and nowhere else. ``make`` is not called with the layer off: nothing of the
    realisation is computed."""
    if not _on(source):
        return neutral(decl, shape)
    neutral(decl, (0,))  # an undeclared field is refused with the layer on too, not only when it is switched off
    return make()


def published(source: Any, name: str) -> Any:
    """A composed field as a run published it, or None where the model publishes none. With the layer off the
    run published its neutral value everywhere (:func:`field`), so this is the neutral value then. For a reader
    that draws the field itself - the API's render - rather than placing a census by it."""
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


def realise_scalars(source: Any, names: Sequence[str], draw: Callable[[], Mapping[str, float]]) -> dict[str, float]:
    """Synthetic scalars a layer stage publishes: ``draw()``, or - with the layer off - NaN for each. "A synthetic
    quantity is not realised, and an unrealised quantity is NaN (D164); the field list is the same on and off; 0
    would claim a draw that was not made" (D215, gate ruling 5). ``draw`` is not called with the layer off, so
    the layer's stream is never drawn then."""
    return realise(source, lambda: dict(draw()), lambda: {name: float("nan") for name in names})


def cloud_texture(source: Any, seed: int, counts: Sequence[tuple[int, int]], size: np.ndarray) -> dict[str, np.ndarray]:
    """The four cloud texture columns for a census's cells (``layer/cloud_texture.py``): drawn on the cells' own
    streams, or zero with the layer off - no offset, no gradient, angles 0."""
    from galaxy.layer import cloud_texture as _texture

    return realise(source, lambda: _texture.draw(seed, counts, size), lambda: _texture.neutral(len(size)))
