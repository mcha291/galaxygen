// The picture test (T12, BUILD_III Phase 0; the templates since S54, D213 ruling 7): each capture of captures.json
// is the React viewer's Galaxy view of one template - at the template's own camera, lens and filter set - in a
// stated mode and size, taken as the canvas shows it and compared with its committed file: a frame under
// e2e/frames/, or a thumbnail under public/templates/, which the app's switcher serves. `npm --prefix frontend
// run picture` compares; `picture:update` rewrites the files and frames.json, which records the renderer each was
// drawn by.
//
// The template is chosen through the viewer's own switcher, as a user would, and the mode through its buttons;
// the camera, the lens and the filter set are then what the viewer took from the template, and the test reads
// them back and holds them to the capture list. The picture comes through `window.__galaxygenCapture`
// (GalaxyView's CaptureProbe) and readiness is read through `window.__galaxygenFrameSum` (its FrameProbe, D208):
// instruments that change nothing that is drawn.

import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

import { type Page, expect, test } from "@playwright/test";

import type { LensCamera } from "../src/galaxy/capture";
import { CHOOSING_VIEWPORT, DEFAULT_TEMPLATE, GPU_ARGS, MODE_BUTTON, READY, SELECTION_TEXT, STAND_TOLERANCE, TOLERANCE } from "./settings";

interface Capture {
  name: string;
  template: string;
  camera: LensCamera;
  mode: keyof typeof MODE_BUTTON;
  filters: string;
  viewport: number;
  /** Where the picture is committed, from frontend/: e2e/frames/<name>.png, or public/templates/<template>.png. */
  file: string;
  /** Present while the picture cannot be taken yet; says what it waits on. */
  pending?: string;
}

interface FrameRecord {
  file: string;
  template: string;
  width: number;
  height: number;
  bytes: number;
  sha256: string;
  renderer: string;
  browser: string;
}

interface FramesFile {
  about: string;
  playwright: string;
  args: string[];
  tolerance: typeof TOLERANCE;
  frames: Record<string, FrameRecord>;
}

/** What the test reads of `/api/templates` (the viewer's own reading is src/workflow/templates.ts). */
interface Served {
  default: string;
  templates: { name: string; label: string; camera: LensCamera; filters: string }[];
}

declare global {
  interface Window {
    __galaxygenCapture?: {
      place(view: Partial<LensCamera> & Omit<LensCamera, "fov_deg">): void;
      where(): LensCamera;
      picture(): { png: string; width: number; height: number };
    };
    __galaxygenFrameSum?: () => { sum: number[]; width: number; height: number };
  }
}

const here = (name: string) => fileURLToPath(new URL(name, import.meta.url));
const read = <T>(path: string) => JSON.parse(readFileSync(path, "utf-8")) as T;
type Labels = { sets: Record<string, { label: string }> };
const CAPTURES = read<{ captures: Capture[] }>(here("./captures.json")).captures;
// The viewer's filter sets: the stand-ins and the named instruments (src/galaxy/filters.ts FILTER_SETS).
const FILTER_LABELS = { ...read<Labels>(here("../src/galaxy/filters.json")).sets, ...read<Labels>(here("../src/galaxy/instruments.json")).sets };
const FRAMES_JSON = here("./frames.json");
const PLAYWRIGHT = (createRequire(import.meta.url)("@playwright/test/package.json") as { version: string }).version;

const FRAMES_ABOUT =
  "Written by `npm --prefix frontend run picture:update` (e2e/picture.spec.ts), never by hand: what each committed picture of e2e/captures.json is and what drew it. " +
  "`file` is from frontend/. `renderer` is WebGL's UNMASKED_RENDERER string. Committed pictures belong to that renderer: on another machine `picture:update` regenerates them and the comparison is then local to it.";

/** The /api requests of a page: how many are in flight, and when one last began or ended. */
function watchApi(page: Page) {
  const net = { inflight: 0, last: Date.now() };
  const isApi = (url: string) => new URL(url).pathname.startsWith("/api/");
  page.on("request", (r) => {
    if (!isApi(r.url())) return;
    net.inflight += 1;
    net.last = Date.now();
  });
  const ended = (url: string) => {
    if (!isApi(url)) return;
    net.inflight -= 1;
    net.last = Date.now();
  };
  page.on("requestfinished", (r) => ended(r.url()));
  page.on("requestfailed", (r) => ended(r.url()));
  return net;
}

/**
 * The templates the API under test serves, or null where it has no such route (a 404: an API from before S54,
 * where the viewer lands on the default galaxy with no switcher). Asked by the test's own client, not the page's.
 */
async function servedTemplates(page: Page): Promise<Served | null> {
  const answer = await page.request.get("/api/templates");
  if (answer.status() === 404) return null;
  expect(answer.ok(), `/api/templates answered ${answer.status()}`).toBe(true);
  return (await answer.json()) as Served;
}

/** The viewport that makes the canvas a square of `side` pixels: the page's bars take a height of their own. */
async function squareCanvas(page: Page, side: number) {
  for (let pass = 0; pass < 6; pass += 1) {
    const box = await page.evaluate(() => {
      const canvas = document.querySelector("canvas")!;
      const rect = canvas.getBoundingClientRect();
      return { width: rect.width, height: rect.height, bufferWidth: canvas.width, bufferHeight: canvas.height, viewWidth: window.innerWidth, viewHeight: window.innerHeight };
    });
    if (box.bufferWidth === side && box.bufferHeight === side) return;
    await page.setViewportSize({ width: Math.ceil(side + box.viewWidth - box.width), height: Math.ceil(side + box.viewHeight - box.height) });
    await page.waitForTimeout(READY.probeMs);
  }
  throw new Error(`the canvas would not come to ${side} x ${side} pixels`);
}

/** Press one of the viewer's buttons, unless it is pressed already, and see that it is. */
async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  // "field" names two buttons in the field mode (the mode and the zoom regime): the mode's is the one beside "star-first".
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

/** Whether the view stands where a camera says, through its lens: the probe's own reading of the camera. */
const standsAt = (page: Page, camera: LensCamera) =>
  page.waitForFunction(
    ([want, tolerance]) => {
      const at = window.__galaxygenCapture?.where();
      if (!at) return false;
      const turn = Math.abs(at.azimuth_deg - want.azimuth_deg) % 360;
      return (
        Math.abs(at.inclination_deg - want.inclination_deg) <= tolerance.degrees &&
        Math.min(turn, 360 - turn) <= tolerance.degrees &&
        Math.abs(at.radius_kpc - want.radius_kpc) <= tolerance.kpc &&
        at.fov_deg === want.fov_deg
      );
    },
    [camera, STAND_TOLERANCE] as const,
    { timeout: READY.standMs },
  );

const picture = async (page: Page) => {
  const got = await page.evaluate(() => window.__galaxygenCapture!.picture());
  return { width: got.width, height: got.height, png: Buffer.from(got.png.slice(got.png.indexOf(",") + 1), "base64") };
};

/**
 * Ready, in either mode: no /api request is in flight and none has begun or ended for READY.quietMs (every load in
 * the viewer starts within 350 ms of what caused it, so nothing is still to be asked for); the frame's summed
 * linear light is above zero and the same number over READY.stillProbes consecutive probes (the data is drawn, the
 * march has run for this camera and nothing is still arriving); and two pictures taken a probe apart are the same
 * bytes. The star-first mode has first to say its selection has arrived (SELECTION_TEXT): its points are asked for
 * 250 ms after the camera stops, and the field under them is asked for again once their threshold is known.
 */
async function settle(page: Page, net: { inflight: number; last: number }, mode: Capture["mode"]) {
  const deadline = Date.now() + READY.timeoutMs;
  if (mode === "stars") await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  let last = "";
  let still = 0;
  while (still < READY.stillProbes) {
    if (Date.now() > deadline) throw new Error(`the view was not ready in ${READY.timeoutMs} ms: ${net.inflight} requests in flight, frame sum ${last}`);
    await page.waitForTimeout(READY.probeMs);
    const quiet = net.inflight === 0 && Date.now() - net.last >= READY.quietMs;
    const sum = await page.evaluate(() => window.__galaxygenFrameSum!().sum);
    const key = sum.join(",");
    still = quiet && sum.some((v) => v > 0) && key === last ? still + 1 : 0;
    last = key;
  }
  let shot = await picture(page);
  for (let tries = 0; tries < 8; tries += 1) {
    await page.waitForTimeout(READY.probeMs);
    const again = await picture(page);
    if (again.png.equals(shot.png)) return { ...again, sum: last };
    shot = again;
  }
  throw new Error("two pictures of a still view were never the same bytes");
}

/** WebGL's unmasked renderer, read on the viewer's own canvas. */
const rendererOf = (page: Page) =>
  page.evaluate(() => {
    const gl = document.querySelector("canvas")!.getContext("webgl2");
    if (!gl) return "no WebGL 2 context";
    const info = gl.getExtension("WEBGL_debug_renderer_info");
    return String(info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
  });

function record(name: string, frame: FrameRecord) {
  const before = existsSync(FRAMES_JSON) ? read<FramesFile>(FRAMES_JSON).frames : {};
  const frames: Record<string, FrameRecord> = {};
  // The list's order, and only its captures: a picture dropped from the list leaves the record too.
  for (const c of CAPTURES) {
    const entry = c.name === name ? frame : before[c.name];
    if (entry) frames[c.name] = entry;
  }
  const file: FramesFile = { about: FRAMES_ABOUT, playwright: PLAYWRIGHT, args: GPU_ARGS, tolerance: TOLERANCE, frames };
  writeFileSync(FRAMES_JSON, `${JSON.stringify(file, null, 2)}\n`, "utf-8");
}

for (const capture of CAPTURES) {
  test(`${capture.name}: ${capture.template}, ${capture.mode} mode, ${capture.filters}, ${capture.viewport} px`, async ({ page, browser }, testInfo) => {
    const filters = FILTER_LABELS[capture.filters];
    if (!filters) throw new Error(`${capture.name}: no filter set ${capture.filters} among the viewer's (src/galaxy/filters.json, instruments.json)`);
    const started = Date.now();
    const net = watchApi(page);
    const side = capture.viewport;
    // Chosen at a size where every control is on screen; the canvas comes to the capture's size afterwards.
    await page.setViewportSize(CHOOSING_VIEWPORT);

    const served = await servedTemplates(page);
    const template = served?.templates.find((t) => t.name === capture.template);
    // A capture marked pending waits on a template the API under test does not serve yet: skipped until it does,
    // and then run like any other (tests/test_picture.py refuses the mark once the model has templates).
    test.skip(!template && capture.pending !== undefined, `pending: ${capture.pending}`);

    // The viewer lands on the Galaxy view of the default template (rule D1 as amended); the canvas and its probes
    // are there once the star sample has arrived, which on a cold server is the galaxy being computed.
    await page.goto("/");
    await page.waitForFunction(() => !!window.__galaxygenCapture && !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });

    if (template) {
      // The list states what the template is seen at; the template is the source. A camera, a lens or a filter
      // set that has moved in the model fails here, by name, before any picture is compared.
      expect({ camera: template.camera, filters: template.filters }, `${capture.name}: the capture list against /api/templates`).toEqual({ camera: capture.camera, filters: capture.filters });
      // Through the switcher, as a user would: the default is pressed already, having been landed on.
      await press(page, template.label);
      // What the viewer took from the template: its stand and lens, read back from the camera, and its filter set.
      await standsAt(page, capture.camera);
      await expect(page.getByRole("button", { name: filters.label, exact: true })).toHaveAttribute("aria-pressed", "true");
    } else {
      // An API from before the templates (S54): no switcher, and the galaxy landed on is the published defaults,
      // which is what `milky_way` is (D213 ruling 1: it overrides nothing). Only its captures can be taken, with
      // the camera, the lens and the filter set placed here as the template would have brought them.
      if (capture.template !== DEFAULT_TEMPLATE) throw new Error(`${capture.name}: the API under test serves no templates, and ${capture.template} is not the default galaxy`);
      await page.evaluate((camera) => window.__galaxygenCapture!.place(camera), capture.camera);
      await standsAt(page, capture.camera);
      await press(page, filters.label);
    }
    await press(page, MODE_BUTTON[capture.mode], capture.mode === "field" ? MODE_BUTTON.stars : undefined);
    await squareCanvas(page, side);

    const shot = await settle(page, net, capture.mode);
    expect([shot.width, shot.height]).toEqual([side, side]);
    await standsAt(page, capture.camera); // and it is still there: nothing moved the camera while the view settled
    const renderer = await rendererOf(page);
    const seconds = (Date.now() - started) / 1000;
    const selection = capture.mode === "stars" ? ((await page.getByText(SELECTION_TEXT).textContent())?.match(/[\d,]+ stars: [^.]*\./)?.[0] ?? "") : "";

    // The committed file, by its path from frontend/ (playwright.config.ts's snapshotPathTemplate).
    const segments = capture.file.split("/");
    const path = testInfo.snapshotPath(...segments);
    const recorded = existsSync(FRAMES_JSON) ? read<FramesFile>(FRAMES_JSON).frames[capture.name] : undefined;
    // Whether this run drew the committed picture to the byte: the comparison below allows TOLERANCE, and this says
    // how much of it was used (at S53, none: a capture run again is the same file).
    const sha256 = createHash("sha256").update(shot.png).digest("hex");
    const against = !recorded ? "no committed picture yet" : recorded.sha256 === sha256 ? "the committed picture, byte for byte" : "not the committed picture's bytes";
    const through = template ? "chosen in the switcher" : "the default galaxy of an API without templates";
    const facts = { capture: capture.name, template: capture.template, through, file: capture.file, renderer, browser: `chromium ${browser.version()}`, playwright: PLAYWRIGHT, args: GPU_ARGS, seconds, bytes: shot.png.length, sha256, against, frameSum: shot.sum, selection };
    await testInfo.attach("capture.json", { body: JSON.stringify(facts, null, 2), contentType: "application/json" });
    testInfo.annotations.push({ type: "renderer", description: renderer });
    console.log(`${capture.name}: ${side} x ${side}, ${shot.png.length.toLocaleString("en")} B (${against}), ${through}, frame sum ${shot.sum}, ready and taken in ${seconds.toFixed(1)} s, ${renderer}${selection ? `; ${selection}` : ""}`);

    const updating = testInfo.config.updateSnapshots === "all" || testInfo.config.updateSnapshots === "changed";
    try {
      expect(shot.png).toMatchSnapshot(segments, TOLERANCE);
    } catch (error) {
      if (recorded && recorded.renderer !== renderer) {
        throw new Error(
          `${capture.name}: the committed picture was drawn by "${recorded.renderer}" and this run by "${renderer}". ` +
            `Committed pictures belong to their renderer: run \`npm --prefix frontend run picture:update\` here and compare locally.\n${String(error)}`,
        );
      }
      throw error;
    }
    if (updating) {
      const bytes = readFileSync(path);
      record(capture.name, {
        file: capture.file,
        template: capture.template,
        width: shot.width,
        height: shot.height,
        bytes: bytes.length,
        sha256: createHash("sha256").update(bytes).digest("hex"),
        renderer,
        browser: `chromium ${browser.version()}`,
      });
    }
  });
}
