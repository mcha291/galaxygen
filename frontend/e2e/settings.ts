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

/**
 * How far the frame's summed linear light may move, per channel, when the layer is switched off (the spec reads
 * the same view both ways through `__galaxygenFrameSum`). The model conserves each ring's totals, so the light
 * emitted is the same. Measured at S55 on the Milky Way template, face-on, field mode, rgb: physics only over
 * layered 1.00257, 1.00115, 0.99942 - a quarter of a percent at most. Why not exactly 1, measured the same day
 * with the star-first mode's component switches (the points off, so the starlight volume is all the starlight):
 * - **the starlight alone, the whole disc in the frame (45 kpc framed): 1.00003** in every channel - the totals
 *   are conserved, to the march's quadrature;
 * - **the frame's edge**: at the template's 20 kpc the disc runs past the frame, and what is cut off depends on
 *   where round the ring the light lies - the starlight alone reads 1.0008 to 1.0013;
 * - **the dust**: what it removes is not linear in its column, so the same dust and stars placed otherwise round a
 *   ring lose another share - with the dust on, the whole disc in the frame, 1.0007, 0.9992, 0.9975.
 * The bound is four times the capture's largest move: a layer that changed a ring's total would move the sum by
 * far more than these two rearrangements do.
 */
export const LAYER_SUM_TOLERANCE = 0.01;

/** The star-first mode's own sentence once its selection has arrived (GalaxyTab's regime text). */
export const SELECTION_TEXT = /every disc star in view above/;

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
