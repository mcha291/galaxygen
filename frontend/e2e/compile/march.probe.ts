// The march probe (S78, T29; for VIEWER_TASKS T14, the march's cost): the field march's GPU time per re-march, per
// picture capture, on ONE built viewer - the site GALAXYGEN_URL names. Run by `npm --prefix frontend run march` against a
// site already standing (e.g. `uv run python -m galaxy.api --port 8019 --client frontend/dist` with GALAXYGEN_BUNDLES).
// To compare two trees, the caller stands two servers (each with its own built dist) and runs this against each, in
// alternating order; the probe itself measures the one site.
//
// Method. For each capture of e2e/captures.json a fresh page (1280 x 900 while choosing, dpr 1) is brought to the
// capture's template (the switcher), mode, "physics only" state, zoomed stand and square canvas as picture.spec.ts does,
// and waits until no /api request has been in flight for READY.quietMs and the frame sum has been lit and the same for
// READY.stillProbes probes. Then, in the page, the camera is nudged through __galaxygenCapture.place by +0.01 degree of
// azimuth once per animation frame for FRAMES frames, so the march re-runs every frame; each new reading of
// __galaxygenMarchGpu.ms (FieldVolume's timer query round the march's render call) is kept and the first WARM are
// dropped. Why every frame: nudged with pauses between, the GPU drops its clocks between marches and the readings came
// out bimodal, up to ten times apart at one size (a 256 px thumbnail read 5 ms on one page and 50 ms on another);
// nudged every frame - what an orbit drag does - each capture's spread is about 1 %. Why not frames.json's gpu_ms: that
// is a single first-march-after-settle reading (texture uploads and a GPU at rest in it: 107-148 ms for the fields
// against 23-36 ms here), not the per-frame cost. The march's target size is read from the Tuning panel ("march: W x H
// px") once the nudges are done.
//
// S78's reading (RTX 4070, ANGLE D3D11; three rounds a tree, old = de6344f's compiled-in step loop against d666c0f's
// dynamic bounds, two servers): new over old 0.985-1.001 on all nine captures - the same within 1.5 % - milky_way-field
// 23.6 ms, ngc_4414-field 36.1, milky_way-stars 19.8, ngc_4414-stars 29.4, the zooms 18.7 and 15.6, the thumbnails 4.5 and
// 5.2, at the full canvas (1024 x 1024; 256 x 256 for the thumbnails), the templates' own steps (96 and 48).
//
// Environment:
//   GALAXYGEN_URL           the site (default http://127.0.0.1:8019)
//   GALAXYGEN_MARCH_ROUNDS  rounds over the nine captures, each in a fresh browser (default 3)
//   GALAXYGEN_MARCH_FRAMES  nudged frames per capture (default 200)
//   GALAXYGEN_MARCH_LABEL   the results' name: e2e/.output/compile/<label>.{json,md} (default march_gpu)
//   GALAXYGEN_MARCH_TUNING  a JSON object of Tuning panel values laid over every captured template's own (S81, T14), as
//                           the panel stores them (localStorage, galaxygen.tuning.<template>) before the page loads: the
//                           nudges move the camera every frame, so the march runs at the moving cap (subMoving) - e.g.
//                           '{"settleMs":0}' measures the full cap, '{"subMoving":4}' another moving cap; default none.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { type Page, chromium, expect, test } from "@playwright/test";

import { CHOOSING_VIEWPORT, DUST_ONLY, GPU_ARGS, MODE_BUTTON, PHYSICS_ONLY_BUTTON, READY, SELECTION_TEXT, TEMPLATE_LABEL } from "../settings";

const SITE = (process.env.GALAXYGEN_URL ?? "http://127.0.0.1:8019").replace(/\/+$/, "");
const ROUNDS = Number(process.env.GALAXYGEN_MARCH_ROUNDS ?? 3);
const FRAMES = Number(process.env.GALAXYGEN_MARCH_FRAMES ?? 200);
const LABEL = process.env.GALAXYGEN_MARCH_LABEL ?? "march_gpu";
const TUNING = process.env.GALAXYGEN_MARCH_TUNING ? (JSON.parse(process.env.GALAXYGEN_MARCH_TUNING) as Record<string, unknown>) : null;
/** The first readings of each capture dropped: the GPU coming up to its clocks. */
const WARM = 20;
const FRONTEND = fileURLToPath(new URL("../..", import.meta.url));
const OUT = resolve(FRONTEND, "e2e/.output/compile");

interface LensCamera {
  inclination_deg: number;
  azimuth_deg: number;
  radius_kpc: number;
  fov_deg: number;
}
interface Target {
  radius_kpc: number;
  azimuth_deg: number;
}
interface Capture {
  name: string;
  template: string;
  camera: LensCamera;
  mode: keyof typeof MODE_BUTTON;
  viewport: number;
  layer?: "on" | "off";
  stand?: { target: Target; radius_kpc: number };
}
/** The viewer's probes this reads (GalaxyView, FieldVolume), typed here so that picture.spec.ts's globals stay its own. */
type Probes = {
  __galaxygenCapture?: { place(view: LensCamera, target?: Target): void };
  __galaxygenFrameSum?: () => { sum: number[] };
  __galaxygenMarchGpu?: { available: boolean; ms: number | null };
  __galaxygenMarchSub?: { sub: number; full: number; moving: boolean };
};
interface Reading {
  round: number;
  available: boolean | null;
  samples: number[];
  readings: number;
  seconds: number;
  march: string | null;
  /** The sub-samples cap the march used on the last nudged frame (S81, T14; FieldVolume's __galaxygenMarchSub). */
  sub: number | null;
}

const CAPTURES = (JSON.parse(readFileSync(resolve(FRONTEND, "e2e/captures.json"), "utf8")) as { captures: Capture[] }).captures;

const median = (xs: number[]) => {
  const s = [...xs].sort((a, b) => a - b);
  return s.length % 2 ? s[(s.length - 1) / 2] : 0.5 * (s[s.length / 2 - 1] + s[s.length / 2]);
};
const quantile = (xs: number[], p: number) => {
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.round(p * (s.length - 1)))];
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

async function settle(page: Page, net: ReturnType<typeof watchApi>, mode: Capture["mode"]) {
  const deadline = Date.now() + READY.timeoutMs;
  if (mode === "stars") await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  let last = "";
  let still = 0;
  while (still < READY.stillProbes) {
    if (Date.now() > deadline) throw new Error(`the view was not ready in ${READY.timeoutMs} ms`);
    await page.waitForTimeout(READY.probeMs);
    const quiet = net.inflight === 0 && Date.now() - net.last >= READY.quietMs;
    const sum = await page.evaluate(() => (window as unknown as Probes).__galaxygenFrameSum!().sum);
    const key = sum.join(",");
    still = quiet && sum.some((v) => v > 0) && key === last ? still + 1 : 0;
    last = key;
  }
}

async function measure(page: Page, capture: Capture, round: number): Promise<Reading> {
  const net = watchApi(page);
  await page.goto(`${SITE}/`);
  await page.waitForFunction(() => !!(window as unknown as Probes).__galaxygenCapture && !!(window as unknown as Probes).__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
  const label = TEMPLATE_LABEL[capture.template];
  if (!label) throw new Error(`${capture.name}: no switcher label for ${capture.template} (settings.ts TEMPLATE_LABEL)`);
  await press(page, label);
  await press(page, MODE_BUTTON[capture.mode], capture.mode === "field" ? MODE_BUTTON.stars : undefined);
  const camera: LensCamera = capture.stand ? { ...capture.camera, radius_kpc: capture.stand.radius_kpc } : capture.camera;
  const target = capture.stand?.target;
  // A template or a mode remakes the canvas, and its probes with it: wait for them again before placing the camera.
  const probesBack = () => page.waitForFunction(() => !!(window as unknown as Probes).__galaxygenCapture, null, { timeout: READY.standMs });
  await page.waitForTimeout(500);
  await probesBack();
  if (capture.stand) await page.evaluate(([c, t]) => (window as unknown as Probes).__galaxygenCapture!.place(c, t), [camera, target] as const);
  if (capture.layer === "off") await press(page, PHYSICS_ONLY_BUTTON);
  await squareCanvas(page, capture.viewport);
  await settle(page, net, capture.mode);
  await probesBack();
  const available = await page.evaluate(() => (window as unknown as Probes).__galaxygenMarchGpu?.available ?? null);
  const run = await page.evaluate(
    ([c, t, frames]) =>
      new Promise<{ seen: number[]; seconds: number; sub: number | null }>((done) => {
        const probes = window as unknown as Probes;
        const seen: number[] = [];
        let prev = probes.__galaxygenMarchGpu?.ms ?? null;
        let i = 0;
        const t0 = performance.now();
        const tick = () => {
          const g = probes.__galaxygenMarchGpu;
          if (g && typeof g.ms === "number" && g.ms !== prev) {
            seen.push(g.ms);
            prev = g.ms;
          }
          i += 1;
          if (i > frames) {
            done({ seen, seconds: (performance.now() - t0) / 1000, sub: probes.__galaxygenMarchSub?.sub ?? null });
            return;
          }
          probes.__galaxygenCapture?.place({ ...c, azimuth_deg: c.azimuth_deg + 0.01 * i }, t);
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }),
    [camera, target, FRAMES] as const,
  );
  await page.getByRole("button", { name: DUST_ONLY.panel }).click();
  await page.waitForTimeout(600);
  const march = await page.evaluate(() => document.body.innerText.match(/march: \d+×\d+ px/)?.[0] ?? null);
  return { round, available, samples: run.seen.slice(WARM), readings: run.seen.length, seconds: run.seconds, march, sub: run.sub };
}

test("the march's GPU time per re-march, per capture, on one site", async () => {
  test.setTimeout(3_600_000);
  mkdirSync(OUT, { recursive: true });
  const results: Record<string, Reading[]> = {};
  for (let round = 1; round <= ROUNDS; round += 1) {
    const browser = await chromium.launch({ headless: true, args: GPU_ARGS });
    try {
      for (const capture of CAPTURES) {
        const context = await browser.newContext({ viewport: CHOOSING_VIEWPORT, deviceScaleFactor: 1 });
        if (TUNING) {
          const templates = [...new Set(CAPTURES.map((c) => c.template))];
          await context.addInitScript(
            ([names, values]) => {
              for (const name of names) window.localStorage.setItem(`galaxygen.tuning.${name}`, JSON.stringify(values));
            },
            [templates, TUNING] as const,
          );
        }
        try {
          const r = await measure(await context.newPage(), capture, round);
          (results[capture.name] ??= []).push(r);
          console.log(`round ${round} ${capture.name}: ${r.samples.length} readings kept, median ${r.samples.length ? median(r.samples).toFixed(2) : "-"} ms, ${r.march ?? "march size unread"}, timer ${r.available}, sub-samples ${r.sub ?? "-"}`);
        } finally {
          await context.close();
        }
      }
    } finally {
      await browser.close();
    }
  }
  const lines = [
    `# The march's GPU time per re-march (${LABEL})`,
    "",
    `Site ${SITE}; ${ROUNDS} rounds, ${FRAMES} nudged frames a capture, the first ${WARM} readings dropped; ms; tuning ${TUNING ? JSON.stringify(TUNING) : "the templates' own"}.`,
    "",
    "| capture | median | p10-p90 | readings | per-round medians | march target | sub-samples | timer |",
    "|---|---|---|---|---|---|---|---|",
  ];
  for (const capture of CAPTURES) {
    const rows = results[capture.name] ?? [];
    const all = rows.flatMap((r) => r.samples);
    const cell = (x: number) => x.toFixed(1);
    lines.push(
      `| ${capture.name} | ${all.length ? cell(median(all)) : "-"} | ${all.length ? `${cell(quantile(all, 0.1))}-${cell(quantile(all, 0.9))}` : "-"} | ${all.length} | ${rows.map((r) => (r.samples.length ? cell(median(r.samples)) : "-")).join(", ")} | ${rows[0]?.march ?? "-"} | ${rows.map((r) => r.sub ?? "-").join(", ")} | ${rows.map((r) => r.available).join(", ")} |`,
    );
  }
  const table = `${lines.join("\n")}\n`;
  console.log(table);
  writeFileSync(resolve(OUT, `${LABEL}.md`), table);
  writeFileSync(resolve(OUT, `${LABEL}.json`), JSON.stringify({ site: SITE, rounds: ROUNDS, frames: FRAMES, warm: WARM, args: GPU_ARGS, tuning: TUNING, results }, null, 2));
  for (const capture of CAPTURES) expect(results[capture.name]?.flatMap((r) => r.samples).length ?? 0, `${capture.name}: no timer readings past the first ${WARM} (too few frames? GALAXYGEN_MARCH_FRAMES)`).toBeGreaterThan(0);
});
