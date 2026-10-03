"""The randomness layer: realisations standing in for physics the model does not compute (BUILD_III section 1).

The physics model publishes laws and statistics; the layer publishes realisations, on its own seed, conserving
every ring total of a field it multiplies and every expected total of a census it places (every realised one from
L1: BUILD_III section 1c rule 2 as amended at gate G1), from sourced statistics, labelled with the physics they
stand in for, and evaluable at a point.

    galaxy/layer/noise.py           the noise primitives: integer hash, value noise, octaves to a spectral slope,
                                    shear, the per-cell unit-mean log-normal map
    galaxy/layer/vectors.json       the committed test vectors a GLSL twin must match
    galaxy/layer/compose.py         law x realisation: the one place a stage, a catalogue's materialisation or the
                                    API obtains a pattern object or a composed (R, phi) field, and the one place the
                                    layer's switch is read (``run(..., layer=False)``: the neutral values)
    galaxy/layer/cloud_texture.py   the first realisation stage (S55, D214): the four cloud columns and the shape
                                    of the cloud-interior noise, synthetic

A realisation stage registers with the rest when ``galaxy.stages`` is imported. Nothing is imported here: a reader
imports ``galaxy.layer.noise`` or ``galaxy.layer.compose`` by name.
"""
