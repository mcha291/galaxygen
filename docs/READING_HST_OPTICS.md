# Reading: HST's optics and the NGC 4414 goal's camera (S67, BUILD_III Phase V8, D227)

A reader agent (Opus, read-only, 2026-10-17) read official pages for T9 and NGC 4414's instrument look. Each number is
marked **read** (quoted on the page named) or **inferred**. Nothing here was downloaded into the repository.

## WFC3/UVIS pixel scale
- **Read**, WFC3 Instrument Handbook §1.3 (hst-docs.stsci.edu/wfc3ihb/chapter-1-introduction-to-wfc3/1-3-key-features-of-wfc3):
  "pixel scale 0.04 arcsec/pix"; §6.3: the plate scale is "approximately 0.04 arcsec per pixel".
- **Read**, Appendix B.2 (geometric distortion, UVIS): 0.0396 (x) / 0.0393 (y) arcsec per pixel at UVIS1's centre,
  0.0400 / 0.0398 on UVIS2; the axes at ~86.1°. The model uses the nominal 0.04; the x/y difference (< 2 %) is
  not drawn.

## The telescope
- **Read**, HST Primer (Cycle 34, optical performance): aperture 2.4 m, f/24; NASA's optics page: the primary
  "2.4 meters in diameter", the secondary 30.5 cm.
- **Read**, TinyTim's pupil table `wfc3_uvis1.pup` (github.com/spacetelescope/tinytim): "0.330 = OTA Secondary
  Mirror Radius", "0.022 = OTA Spider Width", three pads at radius 0.065 about 120° apart, "135.0 = image axis
  rotation"; `cpupil.c` scales each by the pupil radius, so ε = 0.33 is the linear obscuration ratio.
- **Read** (S67's builder, the same file, 2026-10-17): the pads' lines, "# Mirror pad positions and radii",
  "0.8921  0.0000 0.065 = OTA Pad 1 (V3, V2, Pad Radius)", "-0.4615  0.7555 0.065 = OTA Pad 2",
  "-0.4564 -0.7606 0.065 = OTA Pad 3" - each pad's centre (V3, V2) and radius in pupil radii. Whether 0.022
  is a full or half width is not stated in the code read (**inferred**: full width, ~26 mm).
- **Inferred**: four spider vanes (Hubble's pictures show four spikes; no official page read states the count),
  and the spikes' angle on the detector (not read).

## The goal picture of NGC 4414
- **Read**, NSSDC caption for STScI-PRC99-25: Wide Field Planetary Camera 2 (WFPC2); half imaged in 1995 by the
  Key Project, the other half by the Heritage team in 1999 through the same filters.
- **Read**, ESA/Hubble opo9925a: B 439 nm, V 555 nm, I 814 nm; 2.86 × 2.36 arcmin, 1730 × 1428 px.
- **Read**, WFPC2 Data Handbook Table 1.1: PC 0.0455″ per pixel, WF2–4 0.0996″ per pixel.
- **Conflict**: ESA's field over pixels gives 0.099″/px (the WF scale), AstroPix's AVM 0.0805″/px; neither states a
  resampled scale or which chips. **Inferred**: a WF mosaic near 0.1″/px.

**What follows for the template.** `ngc_4414`'s filter set is WFC3's (D213), so its instrument is WFC3/UVIS at
0.04″/px; the goal was taken with WFPC2's WF chips at 0.0996″/px through near-identical filters. The difference is
disclosed, not changed: a template's instrument is its filter set's, and nothing is chosen to look like a goal.
