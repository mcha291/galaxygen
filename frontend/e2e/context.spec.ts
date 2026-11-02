// T13 (S83): the renderer survives a lost WebGL context - a forced loss through WEBGL_lose_context (loseContext(), then
// restoreContext()) on the Milky Way's field stand, the frame drawn after the restore held to the one drawn before it.
// Beside the picture spec, not in it: the stand is milky_way-field's, and the frame before the loss is checked to be that
// committed capture byte for byte, so after the restore the frame's summed light is compared and the bytes need not be
// proven twice. The browser, the server and the port are the picture test's (playwright.config.ts).
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import { type Page, expect, test } from "@playwright/test";

import type { LensCamera } from "../src/galaxy/capture";
import { CONTEXT_LOST_WORDS } from "../src/galaxy/contextLoss";
import { CHOOSING_VIEWPORT, MODE_BUTTON, READY, SELECTION_TEXT, STAND_TOLERANCE, TEMPLATE_LABEL } from "./settings";

declare global {
  interface Window {
    /** The context's state on the view's canvas (T13; GalaxyView's ContextGuard, contextLoss.ts). */
    __galaxygenContext?: () => { lost: boolean; generation: number; losses: number };
  }
}

const read = <T>(path: string) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf-8")) as T;
const CAPTURE = "milky_way-field";
const capture = read<{ captures: { name: string; template: string; camera: LensCamera; mode: keyof typeof MODE_BUTTON; viewport: number }[] }>("./captures.json").captures.find(
  (c) => c.name === CAPTURE,
)!;
const committed = read<{ frames: Record<string, { sha256: string }> }>("./frames.json").frames[CAPTURE];

/** The /api requests in flight and when one last began or ended (the picture spec's `watchApi`, without the record). */
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

/** The canvas at `side` x `side` pixels (the picture spec's `squareCanvas`). */
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

/** Ready (the picture spec's `settle`): quiet, the frame's sum lit and the same over READY.stillProbes probes, two pictures the same bytes. */
async function settle(page: Page, net: { inflight: number; last: number }) {
  const deadline = Date.now() + READY.timeoutMs;
  let last = "";
  let still = 0;
  while (still < READY.stillProbes) {
    if (Date.now() > deadline) throw new Error(`the view was not ready in ${READY.timeoutMs} ms: frame sum ${last}`);
    await page.waitForTimeout(READY.probeMs);
    const building = await page.evaluate(() => window.__galaxygenPsfPending?.() ?? 0);
    const quiet = net.inflight === 0 && Date.now() - net.last >= READY.quietMs && building === 0;
    const sum = await page.evaluate(() => window.__galaxygenFrameSum!().sum);
    const key = sum.join(",");
    still = quiet && sum.some((v) => v > 0) && key === last ? still + 1 : 0;
    last = key;
  }
  const picture = async () => {
    const got = await page.evaluate(() => window.__galaxygenCapture!.picture());
    return Buffer.from(got.png.slice(got.png.indexOf(",") + 1), "base64");
  };
  let shot = await picture();
  for (let tries = 0; tries < 8; tries += 1) {
    await page.waitForTimeout(READY.probeMs);
    const again = await picture();
    if (again.equals(shot)) return { png: again, sum: last };
    shot = again;
  }
  throw new Error("two pictures of a still view were never the same bytes");
}

/** The view's canvas's WEBGL_lose_context: `lose` then `restore` - the extension kept from before the loss, as a lost context gives none. */
const forceContext = (page: Page, what: "lose" | "restore") =>
  page.evaluate((w) => {
    const held = window as unknown as { __contextSpecExt?: WEBGL_lose_context | null };
    held.__contextSpecExt ??= document.querySelector("canvas")!.getContext("webgl2")!.getExtension("WEBGL_lose_context");
    const ext = held.__contextSpecExt;
    if (!ext) throw new Error("no WEBGL_lose_context on this browser");
    if (w === "lose") ext.loseContext();
    else ext.restoreContext();
  }, what);

/**
 * Whether the view's frame loop ran in the next `ms`: FieldVolume's frame loop writes a new `__galaxygenMarchSub`
 * object at every frame, so the one there now is still there `ms` later only if no frame ran.
 */
async function framesRun(page: Page, ms: number): Promise<boolean> {
  await page.evaluate(() => {
    const w = window as unknown as Record<string, unknown>;
    w.__contextSpecSeen = w.__galaxygenMarchSub;
  });
  await page.waitForTimeout(ms);
  return page.evaluate(() => {
    const w = window as unknown as Record<string, unknown>;
    return w.__contextSpecSeen !== w.__galaxygenMarchSub;
  });
}

test("a lost WebGL context: the loss prevented, the frame loop paused under a status line, and the restored context draws the field stand's frame again, in both modes", async ({ page }) => {
  test.setTimeout(READY.timeoutMs + 120_000);
  const net = watchApi(page);
  await page.setViewportSize(CHOOSING_VIEWPORT);
  await page.goto("/");
  await page.waitForFunction(() => !!window.__galaxygenCapture && !!window.__galaxygenFrameSum && !!window.__galaxygenContext, null, { timeout: READY.timeoutMs });
  // milky_way-field as the picture spec takes it: the default template, landed on, at its own stand, in the field mode.
  const press = async (name: string, siblingOf?: string) => {
    const exact = (n: string) => page.getByRole("button", { name: n, exact: true });
    const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name, exact: true }) : exact(name);
    if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
    await expect(button).toHaveAttribute("aria-pressed", "true");
  };
  await press(TEMPLATE_LABEL[capture.template]);
  await page.waitForFunction(
    ([want, tol]) => {
      const at = window.__galaxygenCapture?.where();
      if (!at) return false;
      const turn = Math.abs(at.azimuth_deg - want.azimuth_deg) % 360;
      return Math.abs(at.inclination_deg - want.inclination_deg) <= tol.degrees && Math.min(turn, 360 - turn) <= tol.degrees && Math.abs(at.radius_kpc - want.radius_kpc) <= tol.kpc && at.fov_deg === want.fov_deg;
    },
    [capture.camera, STAND_TOLERANCE] as const,
    { timeout: READY.standMs },
  );
  await press(MODE_BUTTON[capture.mode], MODE_BUTTON.stars);
  await squareCanvas(page, capture.viewport);
  const before = await settle(page, net);
  // The frame before the loss is the committed capture, so the sum after the restore stands for its bytes.
  expect(createHash("sha256").update(before.png).digest("hex"), `${CAPTURE} before the loss: not the committed picture`).toBe(committed.sha256);
  expect(await page.evaluate(() => window.__galaxygenContext!())).toEqual({ lost: false, generation: 0, losses: 0 });
  // The counterpart of the paused loop's check below: with the context live, frames run.
  expect(await framesRun(page, 500), "no frame ran with the context live").toBe(true);

  // Whether the loss's default was prevented when the event reached a listener added after the renderer's (three's).
  await page.evaluate(() => {
    document.querySelector("canvas")!.addEventListener("webglcontextlost", (e) => {
      (window as unknown as Record<string, unknown>).__contextSpecPrevented = e.defaultPrevented;
    });
  });
  const status = page.getByRole("status").filter({ hasText: CONTEXT_LOST_WORDS });
  await forceContext(page, "lose");
  await page.waitForFunction(() => window.__galaxygenContext!().lost, null, { timeout: 10_000 });
  expect(await page.evaluate(() => (window as unknown as Record<string, unknown>).__contextSpecPrevented), "the loss's default was not prevented").toBe(true);
  await expect(status).toBeVisible();
  expect(await page.evaluate(() => document.querySelector("canvas")!.getContext("webgl2")!.isContextLost())).toBe(true);
  // A frame already asked for when the loop was set to "never" still runs (react-three-fiber's `internal.frames`, at most
  // two): the loop is read as paused from a quarter second on. Nothing depends on that frame - three draws nothing while
  // the context is lost, and every target the viewer keeps is marched again on the restore's generation.
  await page.waitForTimeout(250);
  expect(await framesRun(page, 1000), "a frame ran while the context was lost").toBe(false);
  await forceContext(page, "restore");
  await page.waitForFunction(() => !window.__galaxygenContext!().lost, null, { timeout: 10_000 });
  expect(await page.evaluate(() => window.__galaxygenContext!())).toEqual({ lost: false, generation: 1, losses: 1 });
  await expect(status).toBeHidden({ timeout: 10_000 });

  const after = await settle(page, net);
  const same = after.png.equals(before.png);
  console.log(`context: ${CAPTURE} frame sum before the loss ${before.sum}, after the restore ${after.sum}; the picture after ${same ? "the same bytes" : "not the same bytes"} (${after.png.length.toLocaleString("en")} B)`);
  expect(after.sum, `${CAPTURE}: the frame's summed light after the restore`).toBe(before.sum);

  // The stars regime the owner saw black: the same stand in the star-first mode (milky_way-stars' view), lost and
  // restored once more - the points, their dust from the march's textures and the remainder's march - its frame's sum
  // held to the one before this loss (that capture's bytes are the picture spec's to prove).
  await press(MODE_BUTTON.stars);
  await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  const starsBefore = await settle(page, net);
  const was = await page.evaluate(() => window.__galaxygenContext!());
  await page.evaluate(() => {
    (window as unknown as { __contextSpecExt?: unknown }).__contextSpecExt = null; // the mode may have made a new canvas
  });
  await forceContext(page, "lose");
  await page.waitForFunction(() => window.__galaxygenContext!().lost, null, { timeout: 10_000 });
  await expect(status).toBeVisible();
  await forceContext(page, "restore");
  await page.waitForFunction(() => !window.__galaxygenContext!().lost, null, { timeout: 10_000 });
  expect(await page.evaluate(() => window.__galaxygenContext!())).toEqual({ lost: false, generation: was.generation + 1, losses: was.losses + 1 });
  await expect(status).toBeHidden({ timeout: 10_000 });
  const starsAfter = await settle(page, net);
  console.log(`context: the star-first mode at the same stand, frame sum before the loss ${starsBefore.sum}, after the restore ${starsAfter.sum}; the picture after ${starsAfter.png.equals(starsBefore.png) ? "the same bytes" : "not the same bytes"}`);
  expect(starsAfter.sum, "the star-first mode: the frame's summed light after the restore").toBe(starsBefore.sum);
});
