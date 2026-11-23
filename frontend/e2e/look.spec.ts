// The look capture (S105, BUILD_VIII row 105): frames of the Galaxy view at a template's own stand, under either look,
// at the look's defaults or at a pasted combination, written as 1024 px PNGs for tools/goal_sheet.py to set beside the
// goal pictures. A working tool, not a test: nothing is compared, nothing committed is written.
//
//   npm --prefix frontend run look                               every capture in e2e/look.json
//   GALAXYGEN_LOOK_ONLY=milky_way-illustrative npm --prefix frontend run look
//   GALAXYGEN_LOOK_COMBINATION='<a copy box>' GALAXYGEN_LOOK_NAME=try1 npm --prefix frontend run look
//   GALAXYGEN_LOOK_LIST=<a list in look.json's format> npm --prefix frontend run look
//
// GALAXYGEN_E2E_PORT (default 8019) is the API's port, serving this worktree's frontend/dist (`npm run build` first);
// GALAXYGEN_LOOK_DIR (default docs/goals/look/ under the repository) where the PNGs go.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY, storageKeyFor } from "../src/galaxy/tuning";
import { CHOOSING_VIEWPORT, MODE_BUTTON, READY, SELECTION_TEXT } from "./settings";

interface LookCapture {
  name: string;
  template: string;
  look: "physical" | "illustrative";
  mode?: keyof typeof MODE_BUTTON;
  combination?: Record<string, unknown>;
  exposure?: number;
  viewport?: number;
  /** S107: another stand than the template's (GalaxyView's capture probe `place`), about a point of the disc if `target` is given. */
  stand?: { inclination_deg: number; azimuth_deg: number; radius_kpc: number; fov_deg?: number; target?: { radius_kpc: number; azimuth_deg: number } };
}

const here = (name: string) => fileURLToPath(new URL(name, import.meta.url));
const ROOT = resolve(here(".."), "..");
const OUT = resolve(ROOT, process.env.GALAXYGEN_LOOK_DIR ?? join("docs", "goals", "look"));
// GALAXYGEN_LOOK_LIST names another list in look.json's format (a tuning pass's own batch), in place of look.json.
const LIST = (JSON.parse(readFileSync(process.env.GALAXYGEN_LOOK_LIST ?? here("./look.json"), "utf-8")) as { captures: LookCapture[] }).captures;

/** The captures this run takes: the list (or the names asked for), and a pasted combination's. */
function captures(): LookCapture[] {
  const only = process.env.GALAXYGEN_LOOK_ONLY?.split(",").map((s) => s.trim()).filter(Boolean);
  const out = only ? LIST.filter((c) => only.includes(c.name)) : process.env.GALAXYGEN_LOOK_COMBINATION ? [] : [...LIST];
  const pasted = process.env.GALAXYGEN_LOOK_COMBINATION;
  if (pasted) {
    const box = JSON.parse(pasted) as Record<string, unknown>;
    const { template, filters: _filters, exposure, look, ...combination } = box;
    void _filters;
    out.push({
      name: process.env.GALAXYGEN_LOOK_NAME ?? "combination",
      template: typeof template === "string" ? template : "milky_way",
      look: look === "illustrative" ? "illustrative" : "physical",
      combination,
      exposure: typeof exposure === "number" ? exposure : undefined,
    });
  }
  return out;
}

declare const window: Window & {
  __galaxygenCapture?: { picture(): { png: string; width: number; height: number }; place(view: object, target?: object): void };
  __galaxygenFrameSum?: () => { sum: number[] };
  __galaxygenPsfPending?: () => number;
};

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

async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

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

const picture = async (page: Page) => {
  await page.waitForFunction(() => !!window.__galaxygenCapture, null, { timeout: READY.timeoutMs });
  const got = await page.evaluate(() => window.__galaxygenCapture!.picture());
  return Buffer.from(got.png.slice(got.png.indexOf(",") + 1), "base64");
};

/** Ready as the picture test's settle: the network quiet, the frame's light lit and still, two pictures the same bytes. */
async function settle(page: Page, net: ReturnType<typeof watchApi>, mode: keyof typeof MODE_BUTTON) {
  const deadline = Date.now() + READY.timeoutMs;
  if (mode === "stars") await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  let last = "";
  let still = 0;
  while (still < READY.stillProbes) {
    if (Date.now() > deadline) throw new Error(`the view was not ready in ${READY.timeoutMs} ms`);
    await page.waitForTimeout(READY.probeMs);
    const building = await page.evaluate(() => window.__galaxygenPsfPending?.() ?? 0);
    const quiet = net.inflight === 0 && Date.now() - net.last >= READY.quietMs && building === 0;
    // A canvas made again (a stand moved) has no probe for a moment: not still.
    const sum = ((await page.evaluate(() => window.__galaxygenFrameSum?.().sum)) ?? []).join(",");
    still = quiet && sum !== "" && sum !== "0,0,0" && sum === last ? still + 1 : 0;
    last = sum;
  }
  let shot = await picture(page);
  for (let tries = 0; tries < 8; tries += 1) {
    await page.waitForTimeout(READY.probeMs);
    const again = await picture(page);
    if (again.equals(shot)) return again;
    shot = again;
  }
  return shot;
}

/** A console line that says a shader or a program failed: the march then draws nothing (S105's 17 samplers). */
const SHADER_ERROR = /THREE\.WebGLProgram|WebGL shader error|WebGL program not valid|could not compile|link(ing)? (error|fail)/i;

/**
 * How lit the frame's central square (the middle half of each side) is: the share of its pixels whose brightest channel
 * is above `BLACK` of 255. Decoded in the page (the browser reads its own PNG), so the tool needs no decoder of its own.
 */
async function centralLit(page: Page, png: Buffer): Promise<number> {
  return page.evaluate(async ([url, black]) => {
    const image = new Image();
    image.src = url;
    await image.decode();
    const w = image.naturalWidth;
    const h = image.naturalHeight;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d")!;
    ctx.drawImage(image, 0, 0);
    const x0 = Math.floor(w / 4);
    const y0 = Math.floor(h / 4);
    const data = ctx.getImageData(x0, y0, Math.floor(w / 2), Math.floor(h / 2)).data;
    let lit = 0;
    for (let i = 0; i < data.length; i += 4) if (Math.max(data[i], data[i + 1], data[i + 2]) > black) lit += 1;
    return lit / (data.length / 4);
  }, [`data:image/png;base64,${png.toString("base64")}`, BLACK] as const);
}
/** A pixel at or under this (of 255) in every channel counts as dark (the sprites' bloom over a black disc lies above 24). */
const BLACK = 48;
/**
 * The least share of the central square lit, a backstop to the shader check: measured at S105, the two looks' frames
 * whole 53-100 % (the physical Milky Way 74 %, NGC 4414 53 %; the illustrative 97-100 %), the field failed (only the
 * regions and the sparkle over black) 37 % (Milky Way) and 12 % (NGC 4414).
 */
const LEAST_LIT = 0.45;

for (const capture of captures()) {
  test(`look: ${capture.name} (${capture.template}, ${capture.look})`, async ({ page }) => {
    // Every console error and page error while the capture runs: a shader or a program that fails to compile or link
    // leaves the march undrawn without failing anything else, so the capture fails on it (S105).
    const errors: string[] = [];
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    page.on("pageerror", (e) => errors.push(`pageerror: ${e.message}`));
    const net = watchApi(page);
    // The production build reads no shader's or program's log (renderer.ts SHADER_CHECKS): the capture asks WebGL itself
    // after every compile and link and says a failure on the console, where the listener above hears it.
    await page.addInitScript(() => {
      for (const proto of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) {
        const compile = proto.compileShader;
        proto.compileShader = function (this: WebGLRenderingContext, shader: WebGLShader) {
          compile.call(this, shader);
          if (!this.getShaderParameter(shader, this.COMPILE_STATUS)) console.error(`WebGL shader error: ${this.getShaderInfoLog(shader)}`);
        };
        const link = proto.linkProgram;
        proto.linkProgram = function (this: WebGLRenderingContext, program: WebGLProgram) {
          link.call(this, program);
          if (!this.getProgramParameter(program, this.LINK_STATUS)) console.error(`WebGL program not valid: ${this.getProgramInfoLog(program)}`);
        };
      }
    });
    await page.setViewportSize(CHOOSING_VIEWPORT);
    // The browser's look and this template's tuning under it, before the page loads: the look's defaults ("{}"), or the
    // combination over them (stored as the app stores a diff, read through its own sanitize).
    const key = storageKeyFor(capture.template, capture.look);
    await page.addInitScript(
      ([lookKey, look, tuningKey, tuning]) => {
        // S105 fix R6: each capture's look stored as it is, physical too (the default is the illustrative one since D276).
        localStorage.setItem(lookKey, look);
        localStorage.setItem(tuningKey, tuning);
      },
      [LOOK_STORAGE_KEY, capture.look, key, JSON.stringify(capture.combination ?? {})] as const,
    );
    await page.goto("/");
    await page.waitForFunction(() => !!window.__galaxygenCapture && !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
    const served = (await (await page.request.get("/api/templates")).json()) as { templates: { name: string; label: string }[] };
    const template = served.templates.find((t) => t.name === capture.template);
    if (!template) throw new Error(`${capture.name}: no template ${capture.template}`);
    await press(page, template.label);
    const mode = capture.mode ?? "field";
    await press(page, MODE_BUTTON[mode], mode === "field" ? MODE_BUTTON.stars : undefined);
    await expect(page.getByRole("button", { name: "illustrative", exact: true })).toHaveAttribute("aria-pressed", capture.look === "illustrative" ? "true" : "false");
    if (capture.exposure !== undefined) await page.getByRole("slider", { name: "Exposure", exact: true }).fill(String(capture.exposure));
    await squareCanvas(page, capture.viewport ?? 1024);
    let png = await settle(page, net, mode);
    if (capture.stand) {
      // Placed once the view is ready at the template's own stand (a stand placed earlier is taken back when the
      // template's lands), then settled again.
      const { target, ...view } = capture.stand;
      await page.evaluate(([v, t]) => window.__galaxygenCapture!.place(v as object, t as object | undefined), [view, target] as const);
      png = await settle(page, net, mode);
    }
    mkdirSync(OUT, { recursive: true });
    const path = join(OUT, `${capture.name}.png`);
    writeFileSync(path, png);
    const lit = await centralLit(page, png);
    console.log(`look: ${capture.name} -> ${path} (${png.length} bytes; central square ${(100 * lit).toFixed(1)} % lit)`);
    for (const e of errors) console.log(`look: ${capture.name} console error: ${e.slice(0, 2000)}`);
    const shaderErrors = errors.filter((e) => SHADER_ERROR.test(e));
    expect(shaderErrors, `${capture.name}: a shader or program failed`).toEqual([]);
    expect(lit, `${capture.name}: the central square is nearly all black`).toBeGreaterThan(LEAST_LIT);
  });
}
