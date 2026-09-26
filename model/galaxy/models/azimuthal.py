"""The azimuthal model: ``basic`` with star formation that follows the arms (BUILD_II Phase 2, S27).

Built **from** ``BASIC``'s stage tuple with the ``sfh`` slot swapped for ``sfh_azimuthal``,
and ``BASIC``'s constants, so the two declarations cannot drift apart (rule B13): a stage
added to ``basic`` is in this model the moment it is added, and a test asserts the two
differ in exactly one slot. Everything else BUILD_II builds — photometry, remnants, the
stellar halo, clusters, supernova rates, dust emission, clouds, nebular lines — is a shared
derivation and arrives here through the tuple.

What the one slot changes: ``sfh_azimuthal`` publishes every field ``sfh`` does, computed
by ``sfh`` itself, plus the present-day star-formation modulation over (R, φ), and the
catalogue places its young stars by that modulation rather than by the density contrast.
Every acceptance row is radial or vertical, so every row reads what ``basic`` reads.
"""

from galaxy.core.registry import MODELS, Model
from galaxy.models.basic import BASIC

AZIMUTHAL = MODELS.register(
    Model(
        name="azimuthal",
        about=(
            "The basic model with star formation that follows the spiral arms and the bar: the "
            "same histories, the same chemistry and the same totals, plus where around each ring "
            "today's stars form — the star formation law applied to gas that follows the "
            "pattern — so the catalogue's young stars crowd into the arms more tightly than the "
            "old ones do."
        ),
        stages=tuple(("sfh", "sfh_azimuthal") if slot == "sfh" else (slot, impl) for slot, impl in BASIC.stages),
        constants=BASIC.constants,
    )
)
