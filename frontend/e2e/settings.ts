// The picture test's settings (T12), shared by playwright.config.ts and the spec.

/**
 * The port of the test's own server: the API serving the built viewer from one origin. 8017 and 5173 are the
 * owner's live servers and 8018 the `prod` launch configuration; the test never binds or stops any of them.
 */
export const PORT = 8019;

/**
 * The browser's flags. Headless Chromium draws WebGL on the CPU (SwiftShader) unless it is told which backend to
 * use; this one flag puts ANGLE on Direct3D 11 and so on the machine's GPU (S53: with it the headless shell
 * reports the RTX 4070, without it "SwiftShader Device (Subzero)"). Where there is no Direct3D the browser falls
 * back by itself, and the renderer it drew with is recorded with each frame (frames.json) either way.
 */
export const GPU_ARGS = ["--use-angle=d3d11"];

/**
 * When a frame fails. A pixel counts as different when its colour is further from the committed frame's than
 * `threshold` (pixelmatch's distance in YIQ, 0 to 1: 0.01 lets every channel move by 2/255 and counts a grey step
 * of 3/255), and a frame fails when more than `maxDiffPixelRatio` of its pixels are different.
 *
 * Measured at S53 on the renderer in frames.json: the same capture run again is the same file, byte for byte
 * (the march's jitter is fixed by the pixel, never by the frame), so nothing here is spent on run-to-run noise;
 * the allowance is for the last bit of a driver's arithmetic. The field gain's default raised from 1 to 1.25 put
 * 54 to 67 % of each frame's pixels over the threshold, some six hundred times this allowance, and raised to 1.05
 * it put 1.2 to 3.2 % over: twelve times the allowance at the least. Another renderer is not inside it: two of
 * the captures drawn on SwiftShader differ from the RTX 4070's by more than 2/255 in 0.09 and 0.16 % of the pixels.
 */
export const TOLERANCE = { threshold: 0.01, maxDiffPixelRatio: 0.001 };

/** The mode buttons' labels under "Rendering" (GalaxyTab's MODES), by the capture list's mode names. */
export const MODE_BUTTON = { field: "field", stars: "star-first" } as const;

/**
 * The layer's switch under "Rendering" (S55, D214: invariant I5), by its label - src/galaxy/layer.ts PHYSICS_ONLY,
 * which tests/test_picture.py holds this to. A capture whose `layer` is "off" is taken with it pressed.
 */
export const PHYSICS_ONLY_BUTTON = "physics only";

/**
 * The routes that take an input vector, and so the layer's switch (the API's own list: every route but the
 * declarations, the templates and the blackbody table). Under "physics only" every request to one of them carries
 * `layer=off`; with the switch released none carries a `layer` parameter at all.
 */
export const INPUT_ROUTES = ["/api/arrays", "/api/region", "/api/system", "/api/render", "/api/clouds", "/api/clusters", "/api/remnants", "/api/bright"];

// --- what the layer may do to the frame's light (S55, D214: invariant I5; split by principle at S58, D217's follow-up) ---
// The spec reads the layer-off capture's view both ways through `__galaxygenFrameSum`: the frame's summed linear
// light per channel, physics only over layered. The model conserves each ring's totals, so what a ring EMITS is
// the same with the layer and without. What REACHES the camera is another matter where there is dust, so the one
// bound S55 put on the capture's frame (0.01, measured then at 1.00257, 1.00115, 0.99942) is two statements since
// S58, each held where its principle applies. The gate's ruling: "Do not keep 0.01 on the dusty frame by treating
// the lanes' dust differently."

/**
 * (i) The conserving principle, where it applies - **the view with no dust in it**: how far the frame's light may
 * move, per channel, when the layer is switched off. Measured at S58 on the Milky Way template at its own camera
 * (face-on, 20 kpc framed, rgb, 1024 px), starlight and ionized gas, the dust switched off: physics only over
 * layered **1.00001, 1.00005, 1.00004** (1.0000104, 1.0000461, 1.0000396) - the totals are conserved, to the
 * march's quadrature and what the frame's edge cuts off (the disc runs past a 20 kpc frame, and how much of a
 * ring's light lies outside depends on where round the ring it is placed; S55's pattern read 1.0008 to 1.0013
 * here, and 1.00003 with the whole disc in the frame). A layer that changed a ring's total would move the sum by
 * far more than the bound. Read again at S59, with the arms' winding in segments (D218): **1.00000, 1.00004,
 * 1.00003** (0.9999954, 1.0000382, 1.0000320) - the re-wound pattern moves the dusty frame's ratio by up to
 * 0.0025 (below) and this one by 0.000015 at most: the rings' totals are where they were.
 */
export const LAYER_SUM_TOLERANCE = 0.01;

/**
 * How the dust-free view is reached: through the viewer's own component switches, which it has in the star-first
 * mode alone (GalaxyTab's COMPONENT_SWITCHES; the field mode has none). `released` are switched off - "stars", the
 * points, so that the starlight volume is the whole of the stars' light and the frame is the field's own march
 * with nothing over it; and "dust", which takes its extinction, its scattered and its thermal light out of that
 * march (components.ts brightestLayers: dust 0, dustDepth 0). `kept` stay on. `beside` names a button of the same
 * group, so that "stars" is the component and no other button of that name. Measured at S58: without the dust the
 * frame is 1.35 to 1.38 times as bright as with it, in every channel, layered and physics only alike.
 */
export const DUST_FREE = { released: ["stars", "dust"], kept: ["starlight", "ionized gas"], beside: "starlight" } as const;

/**
 * (ii) The transfer principle, on the capture's own frame, which has the dust: transmission exp(-tau) is convex in
 * the dust's column, so the same dust concentrated round a ring (a conserving placement) can only raise the ring's
 * mean transmission. The layered frame is therefore no dimmer than the physics-only one: **physics only over
 * layered is at most 1, plus this**, per channel. It stands for the frame's noise, **measured at S58 as zero** on
 * the renderer in frames.json: the same state drawn twice is the same sum to the last digit, both within a page
 * (physics only pressed, released and pressed again: a relative difference of 0) and across two page loads (the
 * layered frame of `milky_way-field` and of `milky_way-physics-only`: 32451.434562054346, 28458.472909397446,
 * 26434.91662099352 in both). So nothing of it is spent on run-to-run noise here; it is the room left for another
 * renderer's arithmetic, and the spec fails if the same state drawn twice ever differs by as much.
 */
export const TRANSFER_SLACK = 1e-3;

/**
 * Physics only over layered on the dusty frame, per channel (R, G, B), as measured at S59 (0.9824103, 0.9851266,
 * 0.9877067): with the layer the frame is 1.2 to 1.8 % brighter. **The lanes' dust, D217; moves with the lane
 * width**: the bar's gas lanes gather a ring's dust into a narrow range of azimuth, and by (ii) that lets more of
 * the ring's light through. Pinned to DUSTY_RATIO_PIN, so that a change to the lanes (or to anything else that
 * places the dust) is seen here and the numbers re-read, not absorbed by a bound wide enough to hold any of them.
 *
 * Re-pinned at S59 from S58's 0.98487, 0.98688, 0.98845 (0.9848697, 0.9868845, 0.9884525): **the segments'
 * re-wound lanes and arms, D218**. The arms' winding is in segments with the layer on, so every layer-on (R, phi)
 * field is wound again and the dust lies elsewhere round each ring; the physics-only frame is the same file, byte
 * for byte, and the layered one is brighter by 0.25, 0.18 and 0.08 % (the ratio moved by -0.00246, -0.00176 and
 * -0.00075: past the pin in R and G, inside it in B).
 *
 * Re-pinned at S64 from 0.98805, 0.99210, 0.99716 to the measured 0.97275, 0.97786, 0.98691: **the clouds as
 * extinction, BUILD_III V6**. Half the ring's dust (0.490 of the disc's) is now the census's clouds, drawn as their
 * own layer from the whole disc's raster: with the layer on the clouds are placed in their cells by the clustering
 * field and the gas pattern (D220), gathered as the lanes gather the diffuse dust, and by (ii) let more of the light
 * through; with it off each stands uniform in its sector. The layered frame is brighter by a further 1.5 % in R (each
 * texel's clouds a slab at their own heights, the lead's ruling on R3; 0.96717, 0.97239, 0.98261 with the clouds
 * spread through their sech2 layer).
 */
export const DUSTY_LAYER_RATIO = [0.96265, 0.96703, 0.97596] as const;
// S66 (V7, D226 R2c): was [0.97275, 0.97786, 0.98691] at S64/S65 - the gas fluctuation map multiplies the dust's
// placement and the spurs are drawn from their table: the same column per level-0 cell, clumped below the
// cell, so by (ii) more light gets through (Jensen; the probe's +2.4 % at R_sun face-on). Predicted before the capture:
// the layered frame brighter, the ratio lower. Measured (physics only over layered, the physics-only frame the committed
// picture byte for byte): 0.96265, 0.96703, 0.97596 - moved by -0.01010, -0.01083, -0.01095. That capture read the
// layer's maps per sub-step; the pin stands for the amended read (D226 R3/R5 as amended: each map read once per ray as a
// thin screen at the ray's crossing of the midplane, the value multiplying each sub-step's placement), which measures
// 0.96249, 0.96672, 0.97547 (-1.6e-4, -3.1e-4, -4.9e-4 from the pin, inside DUSTY_RATIO_PIN; predicted to fall before
// the capture, it fell), so the pin was not re-taken.
// S63 (D223): was [0.98675, 0.99042, 0.99454] at S61/S62 - the field mode draws the starlight by age, the young
// part placed by the gas contrast's law: more of the young light stands in the gas arms behind the dust, so the
// layered frame is dimmer against physics only by a further 0.13, 0.17, 0.26 % (the ratio moved by +0.00130,
// +0.00168, +0.00262: past the pin in every channel).
// S61 (D220): was [0.98618, 0.98950, 0.99265] at S60 - the censuses are drawn ring-first and the clouds, clusters and
// young bright stars are placed by the clustering field with the layer on (the layer-off frame is a new draw too), so
// the HII knots and the clusters' light lie elsewhere; the ratio moved by +0.00057, +0.00092, +0.00189: past the pin in B.
// S60 (D219): was [0.98241, 0.98513, 0.98771] at S59 - the arms as a census of pieces re-lay every layer-on (R, phi)
// field, the lanes' gas among them, so the dust lies elsewhere round each ring again; the layered frame is now
// brighter than physics only by 1.4, 1.1 and 0.7 % (the ratio moved by +0.00377, +0.00437, +0.00494: past the pin).
export const DUSTY_RATIO_PIN = 1e-3;

/**
 * The dust's column on screen (S66, BUILD_III V7; D226 R2a): the gas fluctuation map multiplies the dust's placement - read
 * once per ray as a thin screen at the ray's crossing of the midplane, the value multiplying each sub-step's placement
 * (D226 R3 as amended) - and its mean is 1 over every level-0 cell on the model's quadrature lattice - so the dust's column on the
 * frame's pixels moves only by the lattice's sampling. The gate reads it on a frame that is linear in the column: the
 * default template at its own camera (face-on, 20 kpc framed) in the star-first mode with the points, the starlight and
 * the ionized gas switched off (`released`, beside "starlight") and the dust kept in its "where it is" reading
 * (`reading`) - the diagnostic draws each ring's level times the placement, spread through the dust's layer by its
 * column, with the depth off (components.ts brightestLayers: dust 0, dustDepth 0) - so the frame's light is a sum over
 * pixels of a ring weight times the placement times the dust's column, with nothing dimmed and nothing else drawn.
 * `__galaxygenFrameSum` with "gas fluctuation in the march" and "spurs in the march" (`toggles`, the Tuning panel's
 * March group) on over both off - the whole layer in the march, as far as this frame draws it - per channel, must lie
 * within DUST_COLUMN_TOLERANCE of 1. Measured: 1.000247 with the gas map alone read per sub-step (S66's first capture);
 * 1.000545 with it alone on the thin screen (D226 R3 as amended); 1.000553 with the gas map and the spurs together
 * (the S66 fix pass, review N4: the spurs' ring mean is exact in the model's quadrature, so they move it little). The ruling's number, a sampling tolerance: the probe measured the
 * whole face-on frame's column, place times the map over place, at -5.9e-4 on 39 pc pixels and +9.3e-4 on the march's
 * own 78 pc ones (Milky Way), -1.7e-3 on NGC 4414's 59 pc ones (REPORT_PROBE D; RULING_S66 R2a). The transmitted light
 * is not held: a clumped medium of the same column lets more light through (Jensen), which is the mechanism.
 */
export const DUST_ONLY = {
  released: ["stars", "starlight", "ionized gas"],
  kept: ["dust"],
  beside: "starlight",
  reading: "where it is",
  // The layer's two dust terms in the march, both switched (review N4): the young light is not in this frame.
  toggles: ["gas fluctuation in the march", "spurs in the march"],
  panel: "Tuning — display choices (experimental)",
} as const;
export const DUST_COLUMN_TOLERANCE = 3e-3;

/** The star-first mode's own sentence once its selection has arrived (GalaxyTab's regime text). */
// S64 (V6, R8): the stars are the tiles in view, so the sentence counts the cells.
export const SELECTION_TEXT = /every disc star in the [\d,]+ cells in view above/;

/**
 * The page's size while the template, the mode and the filters are chosen: wide enough that the panel is the
 * desktop's and every button is on screen. The canvas is brought to the capture's own size after the choosing
 * (a 256 px thumbnail's page is a phone's, its panel a bottom sheet).
 */
export const CHOOSING_VIEWPORT = { width: 1280, height: 900 };

/**
 * The template whose inputs are the published defaults (D213 ruling 1: `milky_way` overrides nothing). Against an
 * API from before the templates the viewer lands on the default galaxy with no switcher, and this template's
 * captures - only this one's - can still be taken there, the test placing its camera, lens and filter set.
 */
export const DEFAULT_TEMPLATE = "milky_way";

/**
 * How closely the view must stand at the capture's camera, read back from the camera itself: a thousandth of a
 * degree (face-on stands 0.0006 degrees off the axis, capture.ts MIN_INCLINATION) and a millionth of a
 * kiloparsec of framing radius. The lens is compared exactly.
 */
export const STAND_TOLERANCE = { degrees: 1e-3, kpc: 1e-6 };

/** How the test decides a view is ready: see the spec's `settle`. */
export const READY = {
  /** No /api request in flight, and none begun or finished for this long: longer than every debounce in the viewer (350 ms). */
  quietMs: 1500,
  /** The frame's summed linear light is read this often, */
  probeMs: 250,
  /** and has to be lit and the same number this many times running. */
  stillProbes: 3,
  /** The longest a capture waits to become ready: the first load computes the galaxy. */
  timeoutMs: 180_000,
  /** The longest the camera takes to stand where a template or the test put it: a canvas remade, not a model run. */
  standMs: 30_000,
};

/**
 * The GPU light check for R1's path (S67's fix pass, F3; D227 R1, R3): NGC 4414 in the star-first mode at its own camera
 * (29.3 pc a pixel) and at the zoom capture's stand (0.488 pc), per channel.
 * - (i) **the spikes' switch moves no light**: the frame's summed linear light with the spikes on over off, every
 *   component at its default, within `spikesTolerance` (ruled 1e-4). Measured at the fix pass (RTX 4070, 1024 px), on
 *   over off - 1, red/green/blue, in two runs: 9.3e-6 / 7.7e-6 / 6.4e-6 and 4.9e-7 / 6.8e-7 / 8.5e-7 at the template's
 *   camera, 3.6e-6 / 8.4e-6 / 1.85e-5 and 1.1e-6 / -1.3e-6 / -5.3e-7 at the zoom stand (the first run's server cold).
 *   Part (ii) read the same to three figures in both runs.
 * - (ii) **the points' light lands on screen**: with the field and the dust off (`released`, beside `beside`), the
 *   points-only frame's sum against the drawn points' own light (`__galaxygenPointsShown`) as FluxPoints deposits it -
 *   each point's flux times its gain over the sky's area a pixel covers at it, times the share of its box on screen (the
 *   box the shader draws, by the table's or the Plummer's rectangle integrals) - within `pointsTolerance`, for both
 *   switch states, over every point in front of the camera: the GPU draws a wide point whose centre is off the frame
 *   (counted by centres alone the zoom frame read +1.04 % in red). Measured, frame over drawn - 1: at the template's
 *   camera (7 661 points, no box clamped) -5.3e-5 / -2.0e-5 / -7.5e-6 with the spikes on, -5.1e-5 / -1.8e-5 / -6.0e-6
 *   off; at the zoom stand (36 746 points, 33 958 boxes clamped to PROFILE_MAX_HALF, 2 861 clusters as Plummer spheres)
 *   -3.57e-4 / -8.6e-5 / -4.5e-5 on, -3.58e-4 / -8.6e-5 / -4.5e-5 off.
 *   **The tolerance, derived**: above the largest measured (3.6e-4, the zoom's red) by at least a factor two, so the
 *   float32 rectangle differences it stands for do not fail it - the smallest power of ten above 7.2e-4, 1e-3; and far
 *   below what the clamp's renormalisation carries (hstPsf.ts psfHalf: the 60 px box holds 0.958 / 0.971 / 0.976 of the
 *   Airy and 0.940 / 0.952 / 0.958 of the spikes, so a box drawn without its 1/share would read 2.4-6.0 % low on the
 *   clamped points, 92 % of the zoom's): 1e-3 is 24 times under the smallest of those, the blue Airy's 2.4e-2.
 */
export const GPU_LIGHT = {
  template: "ngc_4414",
  zoom: "ngc_4414-zoom",
  spikes: "diffraction spikes",
  released: ["starlight", "dust", "ionized gas"],
  beside: "starlight",
  spikesTolerance: 1e-4,
  pointsTolerance: 1e-3,
} as const;

/**
 * The surface-brightness gates (S67, BUILD_III V8; D227 R5 as ruled on the measurement; T1): the default template's
 * face-on field in the star-first mode, the dust off (the conserving principle, as DUST_FREE) and the ionized gas off
 * (its light is not the stars'), each ring of `widthKpc` out to `maxKpc` (the frame's inscribed circle), per channel, its
 * light on screen (`__galaxygenRingProfile`, over the field's gain) with the layer and without:
 * - **A**, the points ("stars") off: against the render's stars in the ring plus the march's bulge there
 *   (`__galaxygenRenderRings`);
 * - **B**, the points on: against the render's remainder in the ring plus the bulge plus the drawn points' own light
 *   (`__galaxygenPointsShown`: the realised census, so the gate holds the drawing, not the draw), each point's display
 *   sprite binned pixel by pixel where its pixels' rays meet the plane (ringProfile.ts spriteRings) - as the screen is:
 *   at the size the page drew it (the ring probe's `sprite`, the fix pass F1) and each pixel turned back by the sky's
 *   area at the plane over that at the point (F2).
 * Each ring from `innerKpc` out within `tolerance`, S66's per-ring bound; the ring inside `innerKpc` within
 * `innerTolerance`, a carried debt (#177 at the close): the march's bulge cusp, -2.3 % in every state.
 *
 * Measured at S67 (RTX 4070, 1024 px), the largest |ratio - 1| over 1-20 kpc and the three channels: A 1.359e-2 with
 * the layer (8-9 kpc, B) and 5.33e-3 without; B 5.04e-3 with the layer and 5.01e-3 without - after the fix pass's F2
 * (the area ratio) B 5.16e-3 with the layer and 5.04e-3 without (11-12 kpc, R), A unmoved. The ring 0-1 kpc 0.977-0.978
 * in all four states. B binned by the points' own radii read up to 4.57e-2 off (the lead's fourth pass): the clusters
 * stand off the plane (|height| median 233 pc, 90 % 740 pc, at most 2.75 kpc), so from the face-on camera 48 kpc away a
 * cluster lands up to 7 px from its own radius at 15 kpc (the brightest of 15-16 kpc, 5 % of the ring at 525 pc up, in
 * 16-17 on screen); bloom, the tone curve and the clusters' radius moved none of it (the probes read before both, and no
 * cluster fills a pixel here).
 */
export const RING_GATE = {
  widthKpc: 1,
  maxKpc: 20,
  innerKpc: 1,
  tolerance: 1.5e-2,
  innerTolerance: 3e-2,
  released: ["dust", "ionized gas"],
  beside: "starlight",
  /**
   * Since the fix pass (F7) the gates read the page's own gains (`__galaxygenPointsShown`: the field's, LIGHT_PER_LSUN_PC2
   * x the field gain x 2^exposure, and the points', times the point gain) in place of a hard-coded 1/400, and run at each
   * setting here, set through the page's exposure slider and the Tuning panel's point gain; the gains read are held to the
   * setting's against FieldVolume's LIGHT_PER_LSUN_PC2. Measured at F7, the largest |ratio - 1| over 1-20 kpc: at the
   * defaults as above; at exposure +1 and point gain 2, A 1.359e-2 on / 5.33e-3 off (unmoved: the field alone scales with
   * the stop) and B 4.53e-3 on / 4.99e-3 off (the points' selection moves with the point gain).
   */
  settings: [
    { name: "at the defaults", exposure: 0, pointGain: 1 },
    { name: "exposure +1 stop, point gain 2", exposure: 1, pointGain: 2 },
  ],
  lightPerLsunPc2: 1 / 400,
  /** The point gain's control (tuning.ts TUNING_CONTROLS pointGain): a log slider of 1000 positions from min to max. */
  pointGainControl: { min: 0.25, max: 4 },
} as const;
