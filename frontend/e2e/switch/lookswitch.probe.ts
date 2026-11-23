// The look switched while a generation is pending (S106, BUILD_VIII section 6, docs/BRIEF.md "Known defects" (i)): the
// Milky Way at its stand under one look, a world_seed rerolled and "Generate" pressed, the look switched at once; then the
// frame's light read every 250 ms until the generation's mark has gone and the view is still. The defect: the canvas is
// made again at the other look's stand and its field is undrawn (the frame's light near nothing) until the generation
// ends. Fixed, the previous galaxy stays drawn - at the new stand, in the new look - until the swap publishes the new one.
// Also counts the console's glGetProgramiv warnings round the remount (defect (ii)).

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY } from "../../src/galaxy/tuning";
import { MODE_BUTTON, READY } from "../settings";

declare const window: Window & { __galaxygenFrameSum?: () => { sum: number[] } };

const frameLight = async (page: Page): Promise<number | null> => {
  const sum = await page.evaluate(() => window.__galaxygenFrameSum?.().sum ?? null);
  return sum ? sum[0] + sum[1] + sum[2] : null;
};

async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

async function still(page: Page) {
  let last = -1;
  let n = 0;
  const deadline = Date.now() + READY.timeoutMs;
  while (n < 4) {
    if (Date.now() > deadline) throw new Error("not still");
    await page.waitForTimeout(500);
    const s = await frameLight(page);
    n = s !== null && s > 0 && s === last ? n + 1 : 0;
    last = s ?? -1;
  }
  return last;
}

for (const from of ["physical", "illustrative"] as const) {
  test(`the look switched from ${from} while a generation is pending keeps the field drawn`, async ({ page }) => {
    const warnings: string[] = [];
    page.on("console", (m) => {
      if (/glGetProgramiv|GL_INVALID/i.test(m.text())) warnings.push(`${m.type()}: ${m.text()}`);
    });
    await page.addInitScript(([key, look]) => localStorage.setItem(key, look), [LOOK_STORAGE_KEY, from] as const);
    await page.goto("/");
    await page.waitForFunction(() => !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
    await press(page, "Milky Way");
    await press(page, MODE_BUTTON.field, MODE_BUTTON.stars);
    const before = await still(page);
    await page.getByRole("button", { name: "Edit galaxy" }).click();
    await page.getByRole("button", { name: "Reroll world_seed" }).click();
    await page.getByRole("button", { name: "Generate", exact: true }).click();
    await page.waitForTimeout(100);
    const shown = await page.getByRole("button", { name: "illustrative", exact: true }).getAttribute("aria-pressed");
    // the other look: the illustrative button toggles it
    await page.getByRole("button", { name: "illustrative", exact: true }).click();
    await expect(page.getByRole("button", { name: "illustrative", exact: true })).toHaveAttribute("aria-pressed", shown === "true" ? "false" : "true");
    const trace: { t: number; light: number | null; generating: boolean }[] = [];
    const t0 = Date.now();
    let quietSince = -1;
    while (Date.now() - t0 < 300_000) {
      await page.waitForTimeout(250);
      const generating = (await page.getByText("generating", { exact: false }).count()) > 0;
      trace.push({ t: Date.now() - t0, light: await frameLight(page), generating });
      if (!generating) {
        if (quietSince < 0) quietSince = Date.now();
        if (Date.now() - quietSince > 4000) break;
      } else quietSince = -1;
    }
    const pending = trace.filter((p) => p.generating);
    const dark = pending.filter((p) => p.light === null || p.light < 0.05 * before);
    console.log(`switch from ${from}: before ${before.toExponential(3)}, ${pending.length} probes while generating, ${dark.length} dark`);
    console.log(trace.map((p) => `${p.t}:${p.generating ? "G" : "-"}:${p.light === null ? "none" : (p.light / before).toFixed(2)}`).join(" "));
    console.log(`glGetProgramiv/GL_INVALID console lines: ${warnings.length}`);
    for (const w of warnings.slice(0, 5)) console.log(`  ${w.slice(0, 300)}`);
    expect(pending.length, "the generation was pending after the switch").toBeGreaterThan(0);
    expect(dark.length, "the field went undrawn while the generation was pending").toBe(0);
  });
}
