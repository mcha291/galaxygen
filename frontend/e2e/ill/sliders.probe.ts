// The illustrative sliders' stall (S107, BUILD_VIII section 6, "the cost of the sliders"): the view at a template's own
// stand under the illustrative look, then one slider of the Tuning panel's Illustrative group moved at a time, as the
// owner drags it; for each move the longest gap between two animation frames from the move until the picture is drawn
// again (the panel's "rebuilding" mark gone and a second more), the long tasks, and the layer's own stage measures
// (feature.ts illMeasure: `ill map <feature>`, `ill compose`, `ill upload`, `ill sparkle`, ...), with the WebGL texture
// uploads timed here. A probe, not a test of a picture: it fails only where a move stalls the view past GALAXYGEN_ILL_STALL_MS
// (default: no bound, the numbers only).
//
//   GALAXYGEN_E2E_PORT=8031 npx --prefix frontend playwright test -c frontend/playwright.ill.config.ts
//   GALAXYGEN_ILL_OUT=<file.json> also writes the numbers there.

import { writeFileSync } from "node:fs";

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY, storageKeyFor } from "../../src/galaxy/tuning";
import { MODE_BUTTON, READY } from "../settings";

interface Move {
  template: "milky_way" | "ngc_4414";
  label: string;
  filter: string;
  values: number[];
}

/** The sliders moved, by their panel name (TuningPanel illName: "<feature label>: <control label>"), each a few times. */
const MOVES: Move[] = [
  { template: "milky_way", label: "arms: skeleton pitch", filter: "skeleton pitch", values: [1.05, 0.95, 1] },
  { template: "milky_way", label: "dust lanes: strand width", filter: "strand width", values: [50, 40, 45] },
  { template: "milky_way", label: "dust lanes: lane depth", filter: "lane depth", values: [1.8, 1.4, 1.6] },
  { template: "ngc_4414", label: "flocculent network: thread spacing", filter: "thread spacing", values: [210, 190, 200] },
  { template: "ngc_4414", label: "flocculent network: dust piece size", filter: "dust piece size", values: [360, 340, 350] },
];

const BOUND = Number(process.env.GALAXYGEN_ILL_STALL_MS ?? "Infinity");

declare const window: Window & {
  __galaxygenFrameSum?: () => { sum: number[] };
  __illProbe?: { frames: number[]; tasks: { start: number; ms: number }[]; on: boolean; busyUntil: number };
  __galaxygenIllPending?: () => number;
  __galaxygenIllJobs?: () => { posted: number; seeded: number; skipped: number; here: number; failed: number; times: Record<string, { ms: number; roundTripMs: number }> };
};

async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

/** The frame's light lit and the same number four probes running. */
async function still(page: Page) {
  let last = "";
  let n = 0;
  const deadline = Date.now() + READY.timeoutMs;
  while (n < 4) {
    if (Date.now() > deadline) throw new Error("the view was not still");
    await page.waitForTimeout(500);
    const s = ((await page.evaluate(() => window.__galaxygenFrameSum?.().sum)) ?? []).join(",");
    n = s !== "" && s !== "0,0,0" && s === last ? n + 1 : 0;
    last = s;
  }
}

const rebuilding = (page: Page) => page.getByRole("status").filter({ hasText: "rebuilding" });

for (const template of ["milky_way", "ngc_4414"] as const) {
  test(`the illustrative sliders' stall on ${template}`, async ({ page }) => {
    await page.addInitScript(
      ([lookKey, tuningKey]) => {
        localStorage.setItem(lookKey, "illustrative");
        localStorage.setItem(tuningKey, "{}");
        // Every animation frame's time and every long task while `on`; every WebGL texture upload timed as `ill upload`
        // (one of a megabyte or more) - the main thread's share of it, which is what stalls a frame.
        const probe = { frames: [] as number[], tasks: [] as { start: number; ms: number }[], on: false, busyUntil: 0 };
        (window as unknown as { __illProbe: typeof probe }).__illProbe = probe;
        const tick = (t: number) => {
          if (probe.on) {
            probe.frames.push(t);
            // the last frame at which an illustrative build was still owed (the picture not yet the move's)
            const pending = (window as unknown as { __galaxygenIllPending?: () => number }).__galaxygenIllPending?.() ?? 0;
            if (pending > 0) probe.busyUntil = t;
          }
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        try {
          new PerformanceObserver((list) => {
            if (!probe.on) return;
            for (const e of list.getEntries()) probe.tasks.push({ start: e.startTime, ms: e.duration });
          }).observe({ type: "longtask", buffered: false });
        } catch {
          // no long-task timing in this browser
        }
        for (const proto of [WebGL2RenderingContext.prototype]) {
          for (const name of ["texImage2D", "texSubImage2D"] as const) {
            const original = proto[name] as (...args: unknown[]) => void;
            (proto as unknown as Record<string, unknown>)[name] = function (this: WebGL2RenderingContext, ...args: unknown[]) {
              const started = performance.now();
              original.apply(this, args);
              const ms = performance.now() - started;
              // texImage2D(target, level, internalformat, width, height, ...); texSubImage2D(target, level, x, y, width, height, ...)
              const at = name === "texImage2D" ? 3 : 4;
              const w = typeof args[at] === "number" ? (args[at] as number) : 0;
              const h = typeof args[at + 1] === "number" ? (args[at + 1] as number) : 0;
              if (w * h >= 250_000) performance.measure(`ill upload ${name} ${w}x${h}`, { start: started, duration: ms });
            };
          }
        }
      },
      [LOOK_STORAGE_KEY, storageKeyFor(template, "illustrative")] as const,
    );
    await page.goto("/");
    await page.waitForFunction(() => !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
    const served = (await (await page.request.get("/api/templates")).json()) as { templates: { name: string; label: string }[] };
    await press(page, served.templates.find((t) => t.name === template)!.label);
    await press(page, MODE_BUTTON.field, MODE_BUTTON.stars);
    await expect(page.getByRole("button", { name: "illustrative", exact: true })).toHaveAttribute("aria-pressed", "true");
    await still(page);
    await page.getByRole("button", { name: /Tuning — display choices/ }).click();
    const rows: Record<string, unknown>[] = [];
    for (const move of MOVES.filter((m) => m.template === template)) {
      await page.getByRole("searchbox", { name: "Filter the illustrative controls" }).fill(move.filter);
      const slider = page.getByRole("slider", { name: move.label, exact: true });
      await expect(slider).toBeVisible();
      for (const value of move.values) {
        await page.waitForTimeout(1500);
        await page.evaluate(() => {
          performance.clearMeasures();
          window.__illProbe!.frames.length = 0;
          window.__illProbe!.tasks.length = 0;
          window.__illProbe!.busyUntil = 0;
          window.__illProbe!.on = true;
        });
        const t0 = await page.evaluate(() => performance.now());
        await slider.fill(String(value));
        // The move's effect: the mark comes (a map-shaping slider) and goes; then a second more of frames.
        await page.waitForTimeout(400);
        await expect(rebuilding(page)).toHaveCount(0, { timeout: 30_000 });
        await page.waitForFunction(() => (window.__galaxygenIllPending?.() ?? 0) === 0, null, { timeout: 30_000 });
        await page.waitForTimeout(1000);
        const got = await page.evaluate((from) => {
          const p = window.__illProbe!;
          p.on = false;
          const frames = p.frames.filter((t) => t >= from);
          let gap = 0;
          for (let i = 1; i < frames.length; i += 1) gap = Math.max(gap, frames[i] - frames[i - 1]);
          const stages: Record<string, { n: number; ms: number; max: number }> = {};
          for (const e of performance.getEntriesByType("measure")) {
            if (!e.name.startsWith("ill ") || e.startTime < from) continue;
            const s = (stages[e.name] ??= { n: 0, ms: 0, max: 0 });
            s.n += 1;
            s.ms += e.duration;
            s.max = Math.max(s.max, e.duration);
          }
          const tasks = p.tasks.filter((t) => t.start >= from).map((t) => Math.round(t.ms));
          return { gap, frames: frames.length, stages, tasks, drawnMs: p.busyUntil > from ? p.busyUntil - from : 0 };
        }, t0);
        const jobs = await page.evaluate(() => window.__galaxygenIllJobs?.() ?? null);
        const row = { template, slider: move.label, value, gapMs: Math.round(got.gap), drawnMs: Math.round(got.drawnMs), frames: got.frames, longTasksMs: got.tasks, stages: got.stages, jobs };
        rows.push(row);
        const stageWords = Object.entries(got.stages)
          .sort((a, b) => b[1].max - a[1].max)
          .map(([k, s]) => `${k.slice(4)} ${s.max.toFixed(0)}${s.n > 1 ? `x${s.n}` : ""}`)
          .join(", ");
        console.log(`ill-probe ${template} "${move.label}" -> ${value}: longest frame gap ${got.gap.toFixed(0)} ms; long tasks [${got.tasks.join(", ")}] ms; stages: ${stageWords}`);
        if (jobs)
          console.log(
            `ill-probe   worker: ${jobs.posted} posted, ${jobs.seeded} seeded, ${jobs.skipped} skipped, ${jobs.here} on the main thread, ${jobs.failed} failed; ` +
              `last map ${jobs.times.map.ms.toFixed(0)} ms in the worker (${jobs.times.map.roundTripMs.toFixed(0)} round trip), ` +
              `last sparkle ${jobs.times.sparkle.ms.toFixed(0)} ms (${jobs.times.sparkle.roundTripMs.toFixed(0)}); the picture the move's ${got.drawnMs.toFixed(0)} ms after it`,
          );
      }
    }
    if (process.env.GALAXYGEN_ILL_OUT) {
      const out = process.env.GALAXYGEN_ILL_OUT.replace(".json", `.${template}.json`);
      writeFileSync(out, JSON.stringify(rows, null, 2));
    }
    for (const r of rows) expect(r.gapMs as number, `${r.slider} -> ${r.value}`).toBeLessThanOrEqual(BOUND);
  });
}
