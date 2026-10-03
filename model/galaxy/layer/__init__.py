"""The randomness layer: realisations standing in for physics the model does not compute (BUILD_III section 1).

The physics model publishes laws and statistics; the layer publishes realisations, on its own seed, conserving
every total, from sourced statistics, labelled with the physics they stand in for, and evaluable at a point.

    galaxy/layer/noise.py       the noise primitives: integer hash, value noise, octaves to a spectral slope,
                                shear, the per-cell unit-mean log-normal map
    galaxy/layer/vectors.json   the committed test vectors a GLSL twin must match

Nothing is imported here: a reader imports ``galaxy.layer.noise`` by name.
"""
