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

/** The star-first mode's own sentence once its selection has arrived (GalaxyTab's regime text). */
export const SELECTION_TEXT = /every disc star in view above/;

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
};
