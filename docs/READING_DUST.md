# READING_DUST — what the dust's carried closers need that the repository does not hold (S89, 2026-11-04)

**The lead's note (S89, BUILD_V row 89, M2's first session; no web access).** Five of M2's dust entries (#82, #91, #92,
#109, #136) were read beside today's model — the dust stage heating the stars' layer through two dust layers since
S89 (#168: the clouds' share in the molecular layer, the rest in the gas's) — and the numbers below were measured on
it. None of the five is built; each needs a source the repository does not hold, a light the model does not compute,
or a ruling. Every number here is a measurement on the S89 model (`[verified]` by the probe named, run in the
session), every source not read is `[recall — NEEDS SOURCING]`.

---

## #91 — the heating's grey slab: the light the eight bands do not hold

The closer reads "the absorbed power integrated over the bands the light stage publishes (U B V R I J H K) with the
grain model's extinction curve per band — eight rows instead of one", predicting L_IR up ~10 % and T_d(R₀) up ~0.5 K.
What the repository shows against it:

- The eight-band continuum (`spectra.sed_density` through the eight `disc_sed_*` samples and their blackbody tails)
  carries **0.687 of `disc_luminosity`** (`tests/test_render.py`, the whole-grid box; 0.708 at S38): the young stars'
  ultraviolet shortward of U is not in it.
- Through that continuum the grain curve removes **0.7847 of what grey absorption at V removes**
  (`tests/test_render.py`'s `CURVE_OVER_GREY`): the old stars' red light is absorbed less, as the entry says, and the
  continuum has no ultraviolet to absorb more.
- So the closer as written would apply a fraction that falls (~0.78 of today's on the continuum) to a light 31 % of
  which is the ultraviolet the curve absorbs *most* — the prediction's sign rests on that 31 %, and its spectrum is not
  computed. The one measured side (S31) put the star formation rate's Habing-band light at the far-ultraviolet depth at
  +10.8 % of the absorbed power.

**What would close it:** the light's spectrum shortward of U — the isochrone points as blackbodies at their own T_eff
(the PARSEC table holds `log_teff` and `log_l` for every point, `model/galaxy/data/parsec_isochrones.npz`), or
ultraviolet bands in the isochrone tables — so that the absorbed power is the whole spectrum through the grain curve.
That is a light-stage change, the populations' batch's (M3, beside T2 / #114 "points through the filter set"). The
CMB floor (2.725 K) needs its source read before it enters code; since S52 no unheated grain is drawn (nothing past the
stellar disc's edge is heated), so it moves no published temperature today.

## #82 — rows 25–28: a dust-attenuated magnitude, measured

All directions together, in the dust stage's convention (a scattered photon escapes): each band's disc light through
its own absorbing depth, (1 − albedo) τ_V A_λ/A_V at the band's reference wavelength, in the two-layer geometry; the
bulge undimmed (it has no radial profile). On the default galaxy: intrinsic M_B −20.585, M_V −21.147, B − V 0.562;
**attenuated M_B −20.246, M_V −20.816, B − V 0.570** (A_V 0.330, A_K 0.181 — the inner disc's opaque rings lose
about half their light at any wavelength). NGC 4414: intrinsic M_V −20.601, B − V 0.661; attenuated −20.275, 0.651
(bluer: the dust removes the red inner light first). Against BHG16's M_V −21.37, B − V 0.73: if the table is
corrected light the model is 0.22 mag short and 0.17 bluer; if observed light, 0.55 short and 0.16 bluer. **The two
readings do not separate on the colour** — the entry's prediction (B4) said they would: attenuation reddens the
galaxy by 0.009 only, so the colour gap is the stars', not the dust's, under either reading.

**What would close it:** the rows have no window (BHG16's Table 2 quotes no errors — "presented in Table 2 without the
uncertainties", pointing to Licquia, Newman & Brinchmann 2015 — though a footnote gives typical ~0.1 mag calibration
errors (re-read at Audit VI, 1B's notes); `lo == hi`, D100), so a published attenuated
magnitude would be a field no row reads (S41: dead) until a source with errors is read — Licquia, Newman &
Brinchmann 2015's analogue values with their uncertainties `[recall — NEEDS SOURCING]` (the source exists and
prints asymmetric errors - ApJ 809, 96: read at S95, reader R; its values not entered). Whether the rows then read
intrinsic or attenuated light is the source's statement to make, and the owner's ruling (S28 ruling (b)) if it does
not.

## #92 — the PAH fraction's sSFR form

Until S95 only the metallicity relation (Rémy-Ruyer et al. 2015 eq. 5) was read (`AUDIT_III.md` A3 row on
`PAH_METALLICITY_INTERCEPT`), and this section said the sSFR form was not held. **It is printed in the same numbered
equation** (sec. 4.3): "log(f_PAH) = (-11.0 +/- 0.3) + (1.30 +/- 0.04) x (12 + log(O/H)); log(f_PAH) = (-5.5 +/- 0.1)
- (0.53 +/- 0.01) x log(sSFR)" (5), "with a dispersion of 0.35 dex around the relation with metallicity, and of 0.38
dex around the relation with sSFR"; f_PAH normalised to the Galactic 4.57 % (Zubko et al. 2004) (read at S95, reader
R, F-R-1; the metallicity line, its errors and the 0.35 dex MATCH the model's constants). Not read: the sSFR's units
in eq. 5 and the sample's range. **What closes #92 now:** a build or a ruling - the sSFR line used per radius in
place of (or beside) the metallicity line, its units read first - or a resolved per-radius calibration (KINGFISH
`[recall]`).

## #109 — the scattered light's phase in an inclined disc

The phase table averages Henyey–Greenstein over in-plane illumination from every azimuth (`[inferred]`); no
radiative-transfer source for an inclined exponential disc's scattered light is held. Since S89 the scattering's
geometry takes the clouds' share in the clouds' layer (#168). **What would close it:** a source's scattered-light phase
for an inclined disc (e.g. a Monte Carlo transfer grid for exponential discs `[recall]`), or region-scale scattering.
The infrared channel's white point is a display ruling, the owner's with the viewer.

## #136 — NGC 4414's face-on colour: the three dust terms read

The template check's own computation (`specs.templates.face_on_colour`, the two-layer face-on transmission since S89)
taken apart on the judged (layer-off) frame: **NGC 4414 — stars alone 0.6607, through the extinction 0.6453, plus the
scattered light 0.6458, plus the thermal (the check) 0.6458**; the Milky Way template 0.5618 → 0.5651 → 0.5663 → 0.5663.
The extinction makes NGC 4414's frame **bluer** by 0.0155 (its dust lies in the inner disc, where the light is reddest),
the scattered light adds 0.0005, the thermal nothing. So against the window [0.72, 0.82] the stars alone are 0.059 under
its floor: the dust as built reddens nothing that could close the gap, and the reading "the stars are too blue" leads
— but is not ruled, for want of the comparison the closer names. **What would close it:** a sourced face-on attenuation
for an Sc disc, the catalogues' own A_B − A_V (`READING_NGC_4414.md` W-K: RC3 / HyperLeda correct to face-on, not to
dust-free; V02's line-of-sight A_B − A_V 0.18 at 55–70″ is not face-on). What kills the dust reading, as the entry
says: a frame still under 0.72 with that reddening applied by hand — at 0.6458 it needs a face-on E(B − V) above 0.074.
