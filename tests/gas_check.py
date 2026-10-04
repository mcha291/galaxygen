"""The two measured numbers of the gas's arm that the model no longer reads (S57, D216; gate G3 item 7).

From S51 to S56 they were constants of the model: ``GAS_ARM_WIDTH`` shaped a von Mises ridge and
``GAS_ARM_MASK_WIDTH`` sized the mask a ridge's amplitude was solved in. Since S57 the gas's arm pattern is the
gas's own steady response to the stellar arms, which reads neither. Gate G3 took them out of the model's registry
- "a stage may not declare reads it does not make" - and they live here, in one place, as what they now are: the
**target** of the width's recorded miss and the **definition** of the disclosed check's mask
(``tests/test_gas_pattern.py``). Their values are unchanged. Each ``..._SOURCE`` is the constant's about line
carried over **verbatim** as it stood in ``model/galaxy/models/level0.py`` at tag ``s56``, the last state in
which the model read it: its [verified: ...] sources, its named alternatives and its coverage. What those lines
say the gas pattern stage *does* with the number was true at S56 and is history now.

``tests/layer_reference.py`` reads them too: its frozen copy of S55's ridge is made with the numbers S55 used.

The check's third number, the measured ratio of means, stays in the model: ``gas_arm_contrast``, derived by the
``bar`` stage from the two class means ``GAS_ARM_CONTRAST_GRAND_DESIGN`` and ``GAS_ARM_CONTRAST_OTHER``.
"""

from __future__ import annotations

# The width's target: the measured gas arm's full width at half maximum over the arm-to-arm period. Dimensionless.
GAS_ARM_WIDTH = 0.17
GAS_ARM_WIDTH_SOURCE = (
    "Full width at half maximum of the gas's arm ridge as a fraction of the arm-to-arm period, "
    "constant with radius. M51's gas (CO 1-0 plus HI, total hydrogen surface density) has arms "
    "'~30 degree (FWHM) for inner arms and ~5 degree for outer arms' against the stellar mass "
    "map's ~60 and ~30, Gaussian fits to azimuthal profiles at 240 pc [verified: Egusa et al. "
    "2017, MNRAS 465, 460, arXiv:1610.06642, Sects. 3.1-3.2; docs/READING_GAS_PATTERN.md "
    "Reading B]; with two arms the period is 180 degrees, so 0.17 for the gas's inner arms "
    "against 0.33 for the stars' - the gas ridge half the stellar arm's width (the fractions are "
    "the reader's arithmetic; the text says FWHM where Fig. 4's caption says sigma, and the text "
    "is taken). A fraction of the period, so the absolute width grows outward as every tracer's "
    "does. The gas pattern stage turns it into a von Mises concentration, kappa = ln 2 / (1 - "
    "cos(pi W)) = 4.98, exact for that shape - one arm number's ridge; since S56 a ring of several "
    "stellar modes takes that ridge's values in the order of the modes' sum, so this fraction of "
    "every ring stands above the ridge's half level, the tallest stellar crest carrying the "
    "widest ridge and a low one little or none (D215). Named alternatives: isothermal spiral shocks "
    "0.05-0.16 of the spacing [verified: Kim & Ostriker 2002, ApJ 570, 132, Table 1]; the Milky "
    "Way's masers (young stars, not gas) 0.30 as an FWHM [verified: Reid et al. 2019, ApJ 885, "
    "131, Sect. 3; the fraction the reader's arithmetic]; M51's outer arms 0.03, at the beam. "
    "Coverage: one galaxy, its inner arms (debt #129)."
)

# The mask's definition: the full width, perpendicular to an arm, of the source's arm mask. kpc.
GAS_ARM_MASK_WIDTH = 1.5
GAS_ARM_MASK_WIDTH_SOURCE = (
    "Full width, perpendicular to the arm, of the arm mask inside which the gas's ratio of means "
    "is measured: PHANGS's masks are log-spirals traced at 3.6 micron and widened in 500 pc steps "
    "until the CO flux gain falls below 1.25, 'typically 1-2 kpc wide', and the default where "
    "coverage is poor is 'the median (1.5 kpc) width across the whole PHANGS sample' [verified: "
    "Querejeta et al. 2021, A&A 656, A133, arXiv:2109.04491, Sect. 3.2; "
    "docs/READING_GAS_PATTERN.md Readings A-B]. The gas pattern stage derives the ridge's "
    "amplitude from the measured ratio over this mask, in the ridge's phase m (W/2)/(R sin p), "
    "clamped at half the period - which a 1.5 kpc mask reaches on a four-armed disc inside 12 kpc "
    "at the defaults, so the clamp is the source's geometry. Since S56 the stellar pattern is "
    "several arm numbers at once, and the mask is the share of the ring this width covers - "
    "m W / (2 pi R sin p) for the ring's power-weighted arm number, at most a half - taken where "
    "the stellar modes' sum is highest (D215). Named alternative: the narrow masks "
    "cut round the CO or H-alpha ridge, 'typical widths between 500 and 1000 pc, so about half "
    "the width of the original masks' [verified: Querejeta et al. 2024, A&A 687, A293, Appendix E "
    "and Sect. 2.6.1], whose ratio is GAS_ARM_CONTRAST_GRAND_DESIGN's narrow-mask alternative. "
    "Coverage: the PHANGS-ALMA spirals given masks (28 of 74)."
)
