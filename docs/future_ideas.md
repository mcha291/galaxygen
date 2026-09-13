# Future ideas

Short notes on things worth doing later. Not a plan.

- **Stellar disc growing over time.** `stars_formed_history` is published at the radii
  stars occupy *today*, so the checkpoint 3 scrubber cannot use it to show the stellar
  disc at a past epoch. Publish a stars-formed history at *birth* radius so the scrubber
  can show the stellar disc building up.
- **Smaller history downloads.** Each (R, t) history is 400 radii × 2000 time steps ×
  8 bytes = 6.4 MB. Options: float32 (3.2 MB), fewer time steps for scrubbing (200 steps
  = 640 KB), or a single time slice per request.
- **Pattern amplitudes.** `arm_amplitude` and `bar_amplitude` are experimental controls
  on the bottom bar. Once good values are found, derive them or draw them from
  `pattern_seed` (RENDER_PLAN M1) instead of leaving them as inputs.
- **Photometry source for M2.** MIST v1.2 basic isochrones are a 210 MB download (full:
  656 MB; EEP tracks 67–107 MB per metallicity); the site states no licence terms.
  PARSEC generates tables on request. An analytic fit (e.g. Hurley et al. 2000) needs
  no download.
