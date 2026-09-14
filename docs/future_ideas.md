# Future ideas

Short notes on things worth doing later. Not a plan.

- **Stellar disc growing over time.** `stars_formed_history` is published at the radii
  stars occupy *today*, so the checkpoint 3 scrubber cannot use it to show the stellar
  disc at a past epoch. Publish a stars-formed history at *birth* radius so the scrubber
  can show the stellar disc building up.
- **Pattern amplitudes.** `arm_amplitude` and `bar_amplitude` are experimental controls
  on the bottom bar. Once good values are found, derive them or draw them from
  `pattern_seed` (RENDER_PLAN M1) instead of leaving them as inputs.
- **Photometry for M2** uses PARSEC isochrone tables (chosen over MIST, whose basic set is a
  210 MB download with no stated licence).
- **The last isochrone age.** The table now reaches log age 10.1 (`fetch_parsec.py
  --append-age 10.1`). CMD's grid ends at 10.13, off the 0.1 step the lookup assumes.