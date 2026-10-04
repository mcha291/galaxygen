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
import {
  CHOOSING_VIEWPORT,
  DEFAULT_TEMPLATE,
  DUSTY_LAYER_RATIO,
  DUSTY_RATIO_PIN,
  DUST_FREE,
  GPU_ARGS,
  INPUT_ROUTES,
  LAYER_SUM_TOLERANCE,
  MODE_BUTTON,
  PHYSICS_ONLY_BUTTON,
  READY,
  SELECTION_TEXT,
  STAND_TOLERANCE,
  TOLERANCE,
  TRANSFER_SLACK,
} from "./settings";

interface Capture {
  name: string;
  template: string;
  camera: LensCamera;
  mode: keyof typeof MODE_BUTTON;
  filters: string;
  viewport: number;
  /** "off": taken with the viewer's "physics only" switch pressed (S55, invariant I5). Absent or "on": the layer on. */
  layer?: "on" | "off";
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
type Net = ReturnType<typeof watchApi>;
type Labels = { sets: Record<string, { label: string }> };
const CAPTURES = read<{ captures: Capture[] }>(here("./captures.json")).captures;
// The viewer's filter sets: the stand-ins and the named instruments (src/galaxy/filters.ts FILTER_SETS).
const FILTER_LABELS = { ...read<Labels>(here("../src/galaxy/filters.json")).sets, ...read<Labels>(here("../src/galaxy/instruments.json")).sets };
const FRAMES_JSON = here("./frames.json");
const PLAYWRIGHT = (createRequire(import.meta.url)("@playwright/test/package.json") as { version: string }).version;

const FRAMES_ABOUT =
  "Written by `npm --prefix frontend run picture:update` (e2e/picture.spec.ts), never by hand: what each committed picture of e2e/captures.json is and what drew it. " +
  "`file` is from frontend/. `renderer` is WebGL's UNMASKED_RENDERER string. Committed pictures belong to that renderer: on another machine `picture:update` regenerates them and the comparison is then local to it.";

/**
 * One /api request as it left the page: its route, the `layer` it asked with and the `template` it named (null: no
 * such parameter).
 */
interface Asked {
  route: string;
  layer: string | null;
  template: string | null;
}

/**
 * The /api requests of a page: how many are in flight, when one last began or ended, and each one's route, `layer`
 * and `template` parameters - read from the URL's query, or from the body of a query sent as a POST (transport.js
 * MAX_URL).
 */
function watchApi(page: Page) {
  const net = { inflight: 0, last: Date.now(), asked: [] as Asked[] };
  const isApi = (url: string) => new URL(url).pathname.startsWith("/api/");
  page.on("request", (r) => {
    if (!isApi(r.url())) return;
    net.inflight += 1;
    net.last = Date.now();
    const at = new URL(r.url());
    const params = r.method() === "POST" ? new URLSearchParams(r.postData() ?? "") : at.searchParams;
    net.asked.push({ route: at.pathname, layer: params.get("layer"), template: params.get("template") });
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
async function settle(page: Page, net: Net, mode: Capture["mode"]) {
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

/**
 * No /api request in flight, and none begun or ended for READY.quietMs - counted from this call at the earliest,
 * since what was just pressed asks for its data only when the viewer's debounce (350 ms) has run: a page that was
 * quiet before the press is not yet quiet after it.
 */
async function quiet(page: Page, net: Net) {
  const from = Date.now();
  const deadline = from + READY.timeoutMs;
  while (!(net.inflight === 0 && Date.now() - Math.max(net.last, from) >= READY.quietMs)) {
    if (Date.now() > deadline) throw new Error(`the page was not quiet in ${READY.timeoutMs} ms: ${net.inflight} requests in flight`);
    await page.waitForTimeout(READY.probeMs);
  }
}

/** Release one of the viewer's toggles, and see that it is. `siblingOf` names a button of the same group, as `press` takes it. */
async function release(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) === "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "false");
}

/** A frame's summed linear light per channel, from `settle`'s reading of it. */
const lightOf = (shot: { sum: string }) => shot.sum.split(",").map(Number);

/** One frame's light over another's, per channel. */
const over = (a: number[], b: number[]) => a.map((v, k) => v / b[k]);

/** The largest move from 1 among ratios. */
const farthest = (ratio: number[]) => Math.max(...ratio.map((r) => Math.abs(r - 1)));

const five = (ratio: number[]) => ratio.map((r) => r.toFixed(5)).join(", ");

/** A galaxy-bin/1 frame's header: the magic, the header's length, the header (interface/transport.js decode). */
const wireHeader = (body: Buffer) => JSON.parse(body.subarray(8, 8 + body.readUInt32LE(4)).toString("utf-8")) as Record<string, unknown>;

/** The requests for model data among `asked`: those to a route that takes an input vector. */
const forModelData = (asked: Asked[]) => asked.filter((a) => INPUT_ROUTES.includes(a.route));

/**
 * The template on the wire (S58, D217 item 2): every request for model data names the template the galaxy was
 * started from - `template=<name>` beside its inputs, which is what brings the template's pins to the run (NGC 4414
 * was drawn barred until the viewer sent it). The viewer lands on the default template and the test then chooses
 * the capture's, so the requests are the landing's, naming the default, and from the first that names the
 * capture's template on, every one names it: none goes back and none is nameless. Read off the requests
 * themselves, so nothing here depends on when a press reached the page. Against an API without templates (one
 * from before S54) no request names one.
 */
function namesItsTemplate(what: string, asked: Asked[], template: string, served: Served | null) {
  const data = forModelData(asked);
  if (!served) {
    expect(data.filter((a) => a.template !== null), `${what}: requests naming a template to an API that serves none`).toEqual([]);
    return;
  }
  const first = data.findIndex((a) => a.template === template);
  expect(first, `${what}: no request for model data names the template ${template}`).toBeGreaterThanOrEqual(0);
  expect(data.slice(0, first).filter((a) => a.template !== served.default), `${what}: requests before ${template} was chosen that do not name the landing's template, ${served.default}`).toEqual([]);
  expect(data.slice(first).filter((a) => a.template !== template), `${what}: requests made of ${template} that do not name it`).toEqual([]);
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
    // The layer's switch (S55, D214: invariant I5), through the real control. What was asked before it is the
    // landing, with the layer; everything from here on is asked under the switch.
    const physicsOnly = capture.layer === "off";
    if (physicsOnly) await quiet(page, net);
    const before = net.asked.length;
    if (physicsOnly) await press(page, PHYSICS_ONLY_BUTTON);
    await squareCanvas(page, side);

    const shot = await settle(page, net, capture.mode);
    expect([shot.width, shot.height]).toEqual([side, side]);
    await standsAt(page, capture.camera); // and it is still there: nothing moved the camera while the view settled

    // The switch on the wire. Released, no request names the layer at all: the requests are those of a viewer
    // without the switch (S54's, but for the `template` they name since S58, held to the capture's below).
    // Pressed, every request for model data made since carries layer=off - and the three the field mode draws
    // from were all asked again (the star sample, the fields the march reads, the render).
    if (physicsOnly) {
      const sinceSwitch = forModelData(net.asked.slice(before));
      expect(sinceSwitch.filter((a) => a.layer !== "off"), `${capture.name}: requests made under physics only without layer=off`).toEqual([]);
      expect([...new Set(sinceSwitch.map((a) => a.route))]).toEqual(expect.arrayContaining(["/api/arrays", "/api/region", "/api/render"]));
      await expect(page.getByText(`· ${PHYSICS_ONLY_BUTTON}`)).toBeVisible(); // the hash line says so, after the hash
      await expect(page.getByRole("alert")).toHaveCount(0); // and no frame was refused for its layer
    } else {
      expect(net.asked.filter((a) => a.layer !== null), `${capture.name}: requests naming the layer with the switch released`).toEqual([]);
    }
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
    // What the layer does to the light (S55; split by principle at S58, D217's follow-up): the same view with
    // the switch released again, read as light. The model conserves each ring's totals, so what a ring emits is
    // the same with the layer and without; the picture itself must differ (the arms and the bar are the layer's).
    // What reaches the camera is held by two principles, each where it applies (settings.ts states the numbers):
    // (ii) the transfer principle, on this frame, which has the dust; (i) the conserving principle, on the same
    // view with the dust switched off.
    if (physicsOnly) {
      const off = lightOf(shot);
      await release(page, PHYSICS_ONLY_BUTTON);
      const layered = await settle(page, net, capture.mode);
      const on = lightOf(layered);
      const ratio = over(off, on);
      expect(layered.png.equals(shot.png), "the picture with the layer is the physics-only picture: the switch drew nothing different").toBe(false);
      // The frame noise the transfer principle's allowance stands for: the physics-only state entered a second
      // time (the switch pressed again, the view asked for and drawn again), its light over the first reading's.
      await press(page, PHYSICS_ONLY_BUTTON);
      const again = await settle(page, net, capture.mode);
      const noise = farthest(over(lightOf(again), off));
      console.log(`${capture.name}: frame sum with the layer ${layered.sum}; physics only over it, per channel: ${five(ratio)}; the physics-only frame taken twice differs by ${noise.toExponential(2)}`);
      expect(noise, `the same state drawn twice differs by ${noise}: the allowance ${TRANSFER_SLACK} no longer stands for the frame's noise`).toBeLessThan(TRANSFER_SLACK);

      // (ii) The transfer principle. The dust's transmission exp(-tau) is convex in its column, so dust
      // concentrated round a ring - the same dust, conserved - can only raise the ring's mean transmission: with
      // the layer the frame is no dimmer than without it, and physics only over layered is at most 1 (plus the
      // frame's noise). How far under 1 is the lanes' dust (the bar's gas lanes, D217), and moves with the lane
      // width: pinned, so that a change to the lanes is seen here and re-read, not absorbed by a wide bound.
      for (const [k, r] of ratio.entries()) {
        expect(r, `physics only is brighter than the layered frame by more than ${TRANSFER_SLACK} in channel ${k}: a conserving placement of the dust can only raise the transmission (${five(ratio)})`).toBeLessThanOrEqual(1 + TRANSFER_SLACK);
        expect(Math.abs(r - DUSTY_LAYER_RATIO[k]), `channel ${k}: physics only over layered is ${r.toFixed(5)}, pinned at ${DUSTY_LAYER_RATIO[k]} to ${DUSTY_RATIO_PIN} - the lanes' dust, D217; moves with the lane width (${five(ratio)})`).toBeLessThanOrEqual(DUSTY_RATIO_PIN);
      }

      // (i) The conserving principle, where it applies: the same view with no dust in it. Through the viewer's
      // own switches - the star-first mode's components, the only place the viewer has them: "stars" off, so the
      // starlight volume is the whole of the stars' light (the field's own march, no points over it), and "dust"
      // off, which takes its extinction, its scattered and its thermal light out of the march. Starlight and
      // ionized gas stay. Physics only is still pressed; then released for the layered frame. Two sums compared
      // with each other: no picture of either is committed.
      await press(page, MODE_BUTTON.stars);
      for (const label of DUST_FREE.released) await release(page, label, DUST_FREE.beside);
      for (const label of DUST_FREE.kept) await expect(page.getByRole("button", { name: label, exact: true })).toHaveAttribute("aria-pressed", "true");
      await standsAt(page, capture.camera);
      // With the points off there is no selection to wait for: the view settles as the field mode's does.
      const freeOff = await settle(page, net, "field");
      const sinceFree = net.asked.length;
      await release(page, PHYSICS_ONLY_BUTTON);
      const freeOn = await settle(page, net, "field");
      expect(forModelData(net.asked.slice(sinceFree)).filter((a) => a.layer !== null), "requests naming the layer for the dust-free frame with the switch released").toEqual([]);
      expect([freeOff.width, freeOff.height, freeOn.width, freeOn.height]).toEqual([side, side, side, side]);
      await standsAt(page, capture.camera);
      const free = over(lightOf(freeOff), lightOf(freeOn));
      // The dust is out of both: without its extinction each frame is brighter than its dusty counterpart.
      const lift = { layered: over(lightOf(freeOn), on), physicsOnly: over(lightOf(freeOff), off) };
      console.log(`${capture.name}: without the dust, frame sum with the layer ${freeOn.sum} and physics only ${freeOff.sum}; physics only over layered, per channel: ${five(free)}; dust-free over dusty: layered ${five(lift.layered)}, physics only ${five(lift.physicsOnly)}`);
      await testInfo.attach("layer.json", {
        body: JSON.stringify({ dusty: { physicsOnly: off, layered: on, ratio, noise }, dustFree: { physicsOnly: lightOf(freeOff), layered: lightOf(freeOn), ratio: free }, dustFreeOverDusty: lift }, null, 2),
        contentType: "application/json",
      });
      expect(freeOn.png.equals(freeOff.png), "without the dust the picture with the layer is the physics-only picture").toBe(false);
      for (const r of [...lift.layered, ...lift.physicsOnly]) expect(r, `the dust-free frame is not brighter than the dusty one: the dust switch took nothing out (${five(lift.layered)}; ${five(lift.physicsOnly)})`).toBeGreaterThan(1);
      for (const r of free) expect(Math.abs(r - 1), `without the dust the frame's light moved by more than ${LAYER_SUM_TOLERANCE} with the layer off: ${five(free)}`).toBeLessThan(LAYER_SUM_TOLERANCE);
    }
    namesItsTemplate(capture.name, net.asked, capture.template, served);
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

// The switch on the wire, in every request shape the Galaxy view has (S55, D214: invariant I5; rule B13). The
// captures above show it for the field mode's three routes; this walks the rest - the star-first mode's bright
// catalogue, its whole-disc clusters and the cloud census, then a region's stars, clusters, clouds, remnants and
// render - and holds every request for model data made after the switch was pressed to layer=off. Nothing is
// compared as a picture here.
//
// It is also the one place the region regime is exercised: no capture stands that close. So it holds the cloud
// census's header to the shape the viewer reads the interior noise from (`cloud_interior`, gate G1's ruling:
// constants of the model under their own key, not a stage's scalars) and sees that, with the layer back, the
// region's clouds are drawn with that noise - a header the viewer cannot read it from is drawn smooth, and says so.
test("physics only on the wire: every request for model data carries layer=off, in both modes and in a region", async ({ page }) => {
  const net = watchApi(page);
  // Every /api/clouds header the page is answered with (a request the page gave up on has no body to read).
  const censuses: Promise<Record<string, unknown> | null>[] = [];
  page.on("response", (r) => {
    if (new URL(r.url()).pathname === "/api/clouds" && r.ok()) censuses.push(r.body().then(wireHeader, () => null));
  });
  await page.setViewportSize(CHOOSING_VIEWPORT);
  const served = await servedTemplates(page);
  await page.goto("/");
  await page.waitForFunction(() => !!window.__galaxygenCapture && !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
  await quiet(page, net);
  expect(net.asked.filter((a) => a.layer !== null), "requests naming the layer before the switch was touched").toEqual([]);

  await press(page, PHYSICS_ONLY_BUTTON);
  const before = net.asked.length;
  await quiet(page, net);
  // The star-first mode: the N brightest in view, every cluster, and - a diagnostic layer - the cloud census.
  await press(page, MODE_BUTTON.stars);
  await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  await press(page, "molecular clouds");
  await quiet(page, net);
  // Back in the field mode, down to a region: the zoom's own "stars" regime button.
  await press(page, MODE_BUTTON.field, MODE_BUTTON.stars);
  await press(page, "stars");
  await quiet(page, net);

  const asked = forModelData(net.asked.slice(before));
  expect(asked.filter((a) => a.layer !== "off"), "requests made under physics only without layer=off").toEqual([]);
  const routes = [...new Set(asked.map((a) => a.route))].sort();
  // Every route the viewer asks for model data (/api/system has had no caller since D209).
  expect(routes).toEqual(INPUT_ROUTES.filter((r) => r !== "/api/system").sort());
  await expect(page.getByText(`· ${PHYSICS_ONLY_BUTTON}`)).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  console.log(`physics only on the wire: ${asked.length} requests for model data after the switch, all layer=off, over ${routes.join(", ")}`);

  // Released, the same view is asked for again and no request names the layer.
  const released = net.asked.length;
  await release(page, PHYSICS_ONLY_BUTTON);
  await quiet(page, net);
  const after = forModelData(net.asked.slice(released));
  expect(after.length).toBeGreaterThan(0);
  expect(after.filter((a) => a.layer !== null), "requests naming the layer after the switch was released").toEqual([]);
  // And the template (S58): the galaxy landed on is the default one, and every request made of it - on every
  // route above, in a URL or in a POST's body, with the layer and without - names it.
  namesItsTemplate("physics only on the wire", net.asked, served?.default ?? DEFAULT_TEMPLATE, served);

  // The cloud census, as it was answered under each setting: the interior noise's three parameters under
  // `cloud_interior`, with the layer on and off alike, and none of them among the scalars.
  const headers = (await Promise.all(censuses)).filter((h): h is Record<string, unknown> => h !== null);
  expect([...new Set(headers.map((h) => h.layer))].sort(), "the settings /api/clouds was answered under").toEqual(["off", "on"]);
  for (const header of headers) {
    const interior = header.cloud_interior as Record<string, unknown> | undefined;
    expect(interior, `/api/clouds (layer ${String(header.layer)}) carries no cloud_interior`).toBeDefined();
    expect(Object.keys(interior!).sort()).toEqual(["gain", "lacunarity", "octaves"]);
    for (const value of Object.values(interior!)) expect(typeof value).toBe("number");
    expect(Object.keys((header.scalars ?? {}) as object).filter((name) => name.startsWith("cloud_interior")), "interior parameters among the scalars").toEqual([]);
  }
  // And the viewer read them there: the region's clouds are drawn with the published noise, not smooth with a note.
  await expect(page.getByRole("button", { name: "stars", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByText(/cloud interiors are drawn smooth/)).toHaveCount(0);
  console.log(`physics only on the wire: ${headers.length} cloud censuses, each with cloud_interior ${JSON.stringify(headers[0].cloud_interior)}`);
});
