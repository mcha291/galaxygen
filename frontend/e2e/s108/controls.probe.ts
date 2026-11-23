// The illustrative look under the owner's controls (S108, builder H). Not the picture test (its files end in .probe.ts);
// run by playwright.s108.config.ts against the API serving this worktree's frontend/dist:
//
//   GALAXYGEN_E2E_PORT=8034 S108_PROBE=physonly npx --prefix frontend playwright test -c frontend/playwright.s108.config.ts
//
//   physonly  "physics only" under each stored look on both templates: the frames under the illustrative look must be the
//             physical look's own byte for byte, the look's switch says "suspended", released the illustrative look is back.
//   orbit     the illustrative stand orbited in azimuth (the capture hook's place, as a drag would): the roll must stay a
//             rotation about the line of sight - the camera's screen-up measured against the disc's projected axis.
//   stars     the star-first mode under each look on NGC 4414 (the points' edge).
//   reroll    pattern_seed and texture_seed rerolled and Generate pressed, under the illustrative look, on both templates.
// S108_OUT: where the PNGs go (default docs/goals/s108 under the repository, gitignored).

import { mkdirSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY } from "../../src/galaxy/tuning";
import { MODE_BUTTON, PHYSICS_ONLY_BUTTON, READY, SELECTION_TEXT } from "../settings";

declare const window: Window & {
  __galaxygenCapture?: {
    picture(): { png: string; width: number; height: number };
    place(view: object, target?: object): void;
    where(): Record<string, number>;
    target(): [number, number, number];
  };
  __galaxygenFrameSum?: () => { sum: number[] };
  __galaxygenPsfPending?: () => number;
  __galaxygenIllPending?: () => number;
  __galaxygenCameraAxes?: () => { up: number[]; forward: number[]; right: number[]; eye: number[] };
};

const ROOT = resolve(fileURLToPath(new URL("../..", import.meta.url)), "..");
const OUT = resolve(ROOT, process.env.S108_OUT ?? join("docs", "goals", "s108"));
const ASKED = (process.env.S108_PROBE ?? "physonly,orbit,stars,reroll").split(",").map((s) => s.trim());
const LABEL: Record<string, string> = { milky_way: "Milky Way", ngc_4414: "NGC 4414" };
const TEMPLATES = (process.env.S108_TEMPLATES ?? "milky_way,ngc_4414").split(",");

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

/** As look.spec.ts's settle: the network quiet, no build pending, the frame's light still, two pictures the same. */
async function settle(page: Page, net: ReturnType<typeof watchApi>, stars = false) {
  const deadline = Date.now() + READY.timeoutMs * 2;
  if (stars) await expect(page.getByText(SELECTION_TEXT)).toBeVisible({ timeout: READY.timeoutMs });
  let last = "";
  let still = 0;
  while (still < READY.stillProbes) {
    if (Date.now() > deadline) throw new Error("the view was not ready");
    await page.waitForTimeout(READY.probeMs);
    const building = await page.evaluate(() => (window.__galaxygenPsfPending?.() ?? 0) + (window.__galaxygenIllPending?.() ?? 0));
    const generating = (await page.getByText("generating", { exact: false }).count()) > 0;
    const quiet = net.inflight === 0 && Date.now() - net.last >= READY.quietMs && building === 0 && !generating;
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

function save(name: string, png: Buffer) {
  mkdirSync(OUT, { recursive: true });
  const path = join(OUT, `${name}.png`);
  writeFileSync(path, png);
  console.log(`${name} -> ${path} (${png.length} bytes)`);
}

async function open(page: Page, look: "physical" | "illustrative", template: string, mode: "field" | "stars" = "field") {
  const net = watchApi(page);
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.addInitScript(([key, l]) => localStorage.setItem(key, l), [LOOK_STORAGE_KEY, look] as const);
  await page.goto("/");
  await page.waitForFunction(() => !!window.__galaxygenCapture && !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
  await press(page, LABEL[template]);
  await press(page, MODE_BUTTON[mode], mode === "field" ? MODE_BUTTON.stars : undefined);
  await squareCanvas(page, 1024);
  return net;
}

const lookButton = (page: Page) => page.getByRole("button", { name: "illustrative", exact: true });

if (ASKED.includes("physonly")) {
  for (const template of TEMPLATES) {
    test(`physics only draws the physical look on ${template}`, async ({ browser }) => {
      const shots: Record<string, Buffer> = {};
      for (const look of ["physical", "illustrative"] as const) {
        const page = await browser.newPage();
        const net = await open(page, look, template);
        shots[`${look}-layer`] = await settle(page, net);
        save(`${template}-${look}-layer`, shots[`${look}-layer`]);
        await page.getByRole("button", { name: PHYSICS_ONLY_BUTTON, exact: true }).click();
        await expect(page.getByRole("button", { name: PHYSICS_ONLY_BUTTON, exact: true })).toHaveAttribute("aria-pressed", "true");
        shots[`${look}-physonly`] = await settle(page, net);
        save(`${template}-${look}-physonly`, shots[`${look}-physonly`]);
        const text = (await lookButton(page).textContent()) ?? "";
        console.log(`${template} ${look}: the look's switch under physics only reads "${text}", pressed ${await lookButton(page).getAttribute("aria-pressed")}`);
        expect(text.includes("suspended")).toBe(look === "illustrative");
        await expect(lookButton(page)).toHaveAttribute("aria-pressed", look === "illustrative" ? "true" : "false");
        expect(await page.evaluate((key) => localStorage.getItem(key), LOOK_STORAGE_KEY)).toBe(look);
        await page.getByRole("button", { name: PHYSICS_ONLY_BUTTON, exact: true }).click();
        await expect(page.getByRole("button", { name: PHYSICS_ONLY_BUTTON, exact: true })).toHaveAttribute("aria-pressed", "false");
        shots[`${look}-released`] = await settle(page, net);
        save(`${template}-${look}-released`, shots[`${look}-released`]);
        expect(((await lookButton(page).textContent()) ?? "").includes("suspended")).toBe(false);
        await page.close();
      }
      const same = shots["illustrative-physonly"].equals(shots["physical-physonly"]);
      const back = shots["illustrative-released"].equals(shots["illustrative-layer"]);
      console.log(`${template}: physics only under the illustrative look ${same ? "IS" : "is NOT"} the physical look's frame byte for byte; released, the illustrative frame ${back ? "is" : "is NOT"} the one before`);
      expect(same).toBe(true);
    });
  }
}

/** The disc's axis (scene y) projected on the screen: its angle counter-clockwise from the screen's up, degrees. */
async function axisAngle(page: Page): Promise<number> {
  const cam = await page.evaluate(() => {
    const probe = (window as unknown as { __galaxygenRingProfile?: (e: number[]) => { camera: { up: number[]; right: number[] } } }).__galaxygenRingProfile;
    return probe ? probe([0, 1]).camera : null;
  });
  if (!cam) throw new Error("no ring probe");
  return (Math.atan2(-cam.right[1], cam.up[1]) * 180) / Math.PI;
}

if (ASKED.includes("orbit")) {
  for (const template of TEMPLATES) {
    test(`the roll is held through an orbit on ${template}`, async ({ page }) => {
      const net = await open(page, "illustrative", template);
      save(`${template}-orbit-stand`, await settle(page, net));
      const home = await page.evaluate(() => window.__galaxygenCapture!.where());
      // Whether the camera holds still at the stand (the march's sub-sample cut, T14): read twice, a second apart.
      const held = [];
      for (let k = 0; k < 2; k += 1) {
        held.push(await page.evaluate(() => ({ where: window.__galaxygenCapture!.where(), sub: (window as unknown as { __galaxygenMarchSub?: unknown }).__galaxygenMarchSub })));
        await page.waitForTimeout(1000);
      }
      console.log(`${template}: at the stand, twice: ${JSON.stringify(held)}`);
      const rows: string[] = [`stand ${JSON.stringify(home)}: axis at ${(await axisAngle(page)).toFixed(3)} deg`];
      const inclinations = template === "milky_way" ? [60] : [home.inclination_deg];
      for (const inc of inclinations) {
        for (const az of [0, 90, 180, 270]) {
          await page.evaluate((v) => window.__galaxygenCapture!.place(v), { ...home, inclination_deg: inc, azimuth_deg: az });
          const png = await settle(page, net);
          save(`${template}-orbit-i${Math.round(inc)}-az${az}`, png);
          rows.push(`inclination ${inc.toFixed(1)}, azimuth ${az}: axis at ${(await axisAngle(page)).toFixed(3)} deg`);
        }
      }
      // A drag, as the owner orbits: a third of the canvas to the right, from the stand.
      await page.evaluate((v) => window.__galaxygenCapture!.place(v), home);
      await settle(page, net);
      const box = (await page.locator("canvas").first().boundingBox())!;
      await page.mouse.move(box.x + box.width * 0.4, box.y + box.height * 0.5);
      await page.mouse.down();
      for (let k = 1; k <= 20; k += 1) await page.mouse.move(box.x + box.width * (0.4 + (0.33 * k) / 20), box.y + box.height * 0.5);
      await page.mouse.up();
      save(`${template}-orbit-drag`, await settle(page, net));
      const dragged = await page.evaluate(() => window.__galaxygenCapture!.where());
      rows.push(`dragged to ${JSON.stringify(dragged)}: axis at ${(await axisAngle(page)).toFixed(3)} deg`);
      for (const r of rows) console.log(`${template}: ${r}`);
    });
  }
}

if (ASKED.includes("stars")) {
  for (const template of TEMPLATES) {
    test(`the star-first points under each look on ${template}`, async ({ browser }) => {
      for (const look of ["physical", "illustrative"] as const) {
        const page = await browser.newPage();
        const net = await open(page, look, template, "stars");
        save(`${template}-stars-${look}`, await settle(page, net, true));
        const got = await page.evaluate(() => {
          const probe = (window as unknown as { __galaxygenRingProfile?: (e: number[]) => { sprite: unknown; camera: { tanHalfY: number } } }).__galaxygenRingProfile;
          const r = probe?.([0, 1]);
          return { sprite: r?.sprite, fovDeg: r ? (2 * Math.atan(r.camera.tanHalfY) * 180) / Math.PI : null, ratio: window.devicePixelRatio, where: window.__galaxygenCapture?.where() };
        });
        console.log(`${template} ${look} star-first: sprite ${JSON.stringify(got.sprite)} (device pixel ratio ${got.ratio}), lens ${got.fovDeg?.toFixed(2)} deg, stand ${JSON.stringify(got.where)}`);
        await page.close();
      }
    });
  }
}
