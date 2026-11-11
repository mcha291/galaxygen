// The request walk (S95, Audit VI F-4-1; S73's #200 walk, D236, written down): the built viewer driven through every
// situation whose requests the template bundles plan for, each situation marked in the server's log with
// `/api/version?walk=<step>` so that tools/walk_requests.py can cut the log by step. It presses the viewer's own
// controls and reads nothing but whether the page is quiet: what the viewer sends is the measurement, and nothing
// here changes it.
//
// What it visits, per template (the landing's, then the other through the switcher):
//   the field mode under each shipped filter set (src/galaxy/filters.json and instruments.json: rgb, sho, hoo, wfc3,
//   wfc3n, jwst_nircam); the star-first mode under each; physics only (layer=off) in the star-first and the field
//   mode under each; the layer back on; the Science tab, the scene and the plots looks, every group's previews, every
//   history each offers (the plots' picker and the scene's chips), the preview charts on and off; then, layer on and
//   off, the field mode's "clouds as extinction" flipped and back and the star-first mode's "molecular clouds" on and
//   off. S73's walk visited all of this but jwst_nircam, which shipped at S93.
//
// Environment:
//   GALAXYGEN_URL          the site (default the config's, http://127.0.0.1:8041)
//   GALAXYGEN_WALK_ONLY    a comma list of parts to run: galaxy, science, clouds (default all three)

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { type Locator, type Page, expect, test } from "@playwright/test";

import { MODE_BUTTON, PHYSICS_ONLY_BUTTON, READY, SELECTION_TEXT, TEMPLATE_LABEL } from "../settings";

type Labels = { sets: Record<string, { label: string }> };
const read = <T>(rel: string) => JSON.parse(readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf-8")) as T;
/** Every shipped set, in filters.ts FILTER_SETS's order: the stand-ins, then the named instruments. */
const SETS = Object.entries({ ...read<Labels>("../../src/galaxy/filters.json").sets, ...read<Labels>("../../src/galaxy/instruments.json").sets }).map(
  ([name, s]) => ({ name, label: s.label }),
);
const ONLY = new Set((process.env.GALAXYGEN_WALK_ONLY ?? "galaxy,science,clouds").split(",").map((s) => s.trim()).filter(Boolean));
/** How long one step may take to fall quiet: a miss computes its galaxy (tens of seconds cold, more for a new set). */
const STEP_MS = 15 * 60_000;

/** The page's /api requests in flight, and when one last began or ended. */
function watchApi(page: Page) {
  const net = { inflight: 0, last: Date.now(), asked: 0 };
  const isApi = (url: string) => new URL(url).pathname.startsWith("/api/");
  page.on("request", (r) => {
    if (!isApi(r.url())) return;
    net.inflight += 1;
    net.asked += 1;
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
type Net = ReturnType<typeof watchApi>;

/** No /api request in flight and none begun or ended for READY.quietMs, counted from this call at the earliest. */
async function quiet(page: Page, net: Net) {
  const from = Date.now();
  while (!(net.inflight === 0 && Date.now() - Math.max(net.last, from) >= READY.quietMs)) {
    if (Date.now() - from > STEP_MS) throw new Error(`not quiet in ${STEP_MS} ms: ${net.inflight} requests in flight`);
    await page.waitForTimeout(READY.probeMs);
  }
}

const marks: string[] = [];
/** The log's mark: the answers after it are this step's. Asked by the runner's own client, not the page. */
async function mark(page: Page, step: string) {
  marks.push(step);
  const r = await page.request.get(`/api/version?walk=${encodeURIComponent(step)}`);
  expect(r.ok()).toBe(true);
}

const exact = (page: Page, name: string, siblingOf?: string) => {
  const b = (n: string) => page.getByRole("button", { name: n, exact: true });
  return siblingOf ? b(siblingOf).locator("xpath=..").getByRole("button", { name, exact: true }) : b(name);
};

/** Set a toggle to `on`, and see that it is. */
async function toggle(page: Page, label: string, on: boolean, siblingOf?: string) {
  const button = exact(page, label, siblingOf);
  if (((await button.getAttribute("aria-pressed")) === "true") !== on) await button.click();
  await expect(button).toHaveAttribute("aria-pressed", on ? "true" : "false");
}

/** The mode, through its button: "field" names two buttons, the mode's is the one beside "star-first". */
const mode = (page: Page, m: keyof typeof MODE_BUTTON) => toggle(page, MODE_BUTTON[m], true, m === "field" ? MODE_BUTTON.stars : undefined);

/** One step: mark, act, wait for the page to fall quiet (and in the star-first mode for its selection). */
async function step(page: Page, net: Net, name: string, act: () => Promise<void>, stars = false) {
  await mark(page, name);
  await act();
  if (stars) await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: STEP_MS });
  await quiet(page, net);
}

async function galaxyTab(page: Page) {
  await page.getByRole("tab", { name: "Galaxy" }).click();
  await expect(page.getByRole("tab", { name: "Galaxy" })).toHaveAttribute("aria-selected", "true");
}

async function walkGalaxy(page: Page, net: Net, t: string) {
  for (const s of SETS) {
    await step(page, net, `${t}/on/field/${s.name}`, async () => {
      await mode(page, "field");
      await toggle(page, s.label, true);
    });
  }
  for (const s of SETS) {
    await step(page, net, `${t}/on/stars/${s.name}`, async () => {
      await mode(page, "stars");
      await toggle(page, s.label, true);
    }, true);
  }
  await step(page, net, `${t}/off/switch`, () => toggle(page, PHYSICS_ONLY_BUTTON, true), true);
  for (const s of SETS) {
    await step(page, net, `${t}/off/stars/${s.name}`, async () => {
      await mode(page, "stars");
      await toggle(page, s.label, true);
    }, true);
  }
  for (const s of SETS) {
    await step(page, net, `${t}/off/field/${s.name}`, async () => {
      await mode(page, "field");
      await toggle(page, s.label, true);
    });
  }
  await step(page, net, `${t}/on/back`, () => toggle(page, PHYSICS_ONLY_BUTTON, false));
}

/** Every button of every "History" group on the page, pressed in turn (the plots' picker, the scene's chips). */
async function histories(page: Page, net: Net, at: string) {
  const groups = page.getByRole("group", { name: "History", exact: true });
  const n = await groups.count();
  for (let g = 0; g < n; g += 1) {
    const buttons = groups.nth(g).getByRole("button");
    const m = await buttons.count();
    for (let i = 0; i < m; i += 1) {
      const label = ((await buttons.nth(i).textContent()) ?? "").trim();
      await step(page, net, `${at}/history/${g}/${i}/${label}`, () => buttons.nth(i).click());
    }
  }
}

/** A group's "previews" pressed (it chooses what the Science tab draws), unless it is already. */
async function previews(region: Locator) {
  const b = region.getByRole("button", { name: "previews", exact: true });
  if ((await b.getAttribute("aria-pressed")) !== "true") await b.click();
  await expect(b).toHaveAttribute("aria-pressed", "true");
}

async function walkScience(page: Page, net: Net, t: string) {
  await step(page, net, `${t}/science/tab`, async () => {
    await page.getByRole("tab", { name: "Science" }).click();
    await expect(page.getByRole("tab", { name: "Science" })).toHaveAttribute("aria-selected", "true");
  });
  const groups = page.getByRole("region").filter({ has: page.getByRole("button", { name: "previews", exact: true }) });
  const count = await groups.count();
  expect(count, "the Science tab's groups with previews").toBeGreaterThan(0);
  for (const look of ["scene", "plots"]) {
    await step(page, net, `${t}/science/${look}`, () => toggle(page, look, true));
    for (let g = 0; g < count; g += 1) {
      const region = groups.nth(g);
      const name = (await region.getAttribute("aria-label")) ?? String(g);
      await step(page, net, `${t}/science/${look}/${name}`, () => previews(region));
      await histories(page, net, `${t}/science/${look}/${name}`);
    }
  }
  // The preview charts on, every group's scene seen with them, then off (the footer's switch; CheckpointScene draws
  // and asks an inset only where a checkpoint has one - Halo & disc's rotation curve).
  await step(page, net, `${t}/science/charts`, () => toggle(page, "scene", true));
  const charts = page.getByRole("button", { name: /^preview charts (on|off)$/ });
  await step(page, net, `${t}/science/charts/on`, () => charts.click());
  for (let g = 0; g < count; g += 1) {
    const region = groups.nth(g);
    const name = (await region.getAttribute("aria-label")) ?? String(g);
    await step(page, net, `${t}/science/charts/${name}`, () => previews(region));
  }
  await step(page, net, `${t}/science/charts/off`, () => charts.click());
  await step(page, net, `${t}/science/back`, () => galaxyTab(page));
}

async function walkClouds(page: Page, net: Net, t: string) {
  for (const layer of ["on", "off"] as const) {
    await step(page, net, `${t}/${layer}/clouds/layer`, () => toggle(page, PHYSICS_ONLY_BUTTON, layer === "off"));
    await step(page, net, `${t}/${layer}/clouds/field`, () => mode(page, "field"));
    await step(page, net, `${t}/${layer}/clouds/extinction-off`, () => toggle(page, "clouds as extinction", false));
    await step(page, net, `${t}/${layer}/clouds/extinction-on`, () => toggle(page, "clouds as extinction", true));
    await step(page, net, `${t}/${layer}/clouds/stars`, () => mode(page, "stars"), true);
    await step(page, net, `${t}/${layer}/clouds/molecular-on`, () => toggle(page, "molecular clouds", true));
    await step(page, net, `${t}/${layer}/clouds/molecular-off`, () => toggle(page, "molecular clouds", false));
  }
  await step(page, net, `${t}/on/clouds/back`, async () => {
    await toggle(page, PHYSICS_ONLY_BUTTON, false);
    await mode(page, "field");
  });
}

test("the walk: every situation the bundles plan for, marked", async ({ page }) => {
  const started = Date.now();
  const net = watchApi(page);
  await mark(page, "landing");
  await page.goto("/");
  await expect(page.getByRole("button", { name: TEMPLATE_LABEL.milky_way, exact: true })).toHaveAttribute("aria-pressed", "true", { timeout: STEP_MS });
  await quiet(page, net);
  for (const t of Object.keys(TEMPLATE_LABEL)) {
    await step(page, net, `${t}/switch`, async () => {
      await galaxyTab(page);
      await toggle(page, TEMPLATE_LABEL[t], true);
    });
    if (ONLY.has("galaxy")) await walkGalaxy(page, net, t);
    if (ONLY.has("science")) await walkScience(page, net, t);
    if (ONLY.has("clouds")) await walkClouds(page, net, t);
  }
  await mark(page, "end");
  console.log(`walk: ${marks.length} marks, ${net.asked} /api requests from the page, ${((Date.now() - started) / 1000).toFixed(1)} s`);
});
