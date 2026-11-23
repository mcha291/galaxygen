// The glGetProgramiv warnings round a canvas remount (S106, docs/BRIEF.md "Known defects" (ii)): the Milky Way landed,
// then the look toggled again and again at several delays (each toggle remakes the canvas at the other look's stand),
// and every WebGL warning on the console counted by the delay after which it came. A probe, not a test: it fails only
// on a page error.

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY } from "../../src/galaxy/tuning";
import { MODE_BUTTON, READY } from "../settings";

declare const window: Window & { __galaxygenFrameSum?: () => { sum: number[] } };

async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

test("the look toggled at several delays: WebGL warnings round each remount", async ({ page }) => {
  const lines: { at: number; text: string }[] = [];
  const errors: string[] = [];
  page.on("console", (m) => {
    if (/GL_INVALID|glGetProgram/i.test(m.text())) lines.push({ at: Date.now(), text: `${m.type()}: ${m.text()}` });
  });
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(([key]) => localStorage.setItem(key, "illustrative"), [LOOK_STORAGE_KEY] as const);
  // GALAXYGEN_REMOUNT_CHECKS=1: the look capture's own compile and link checks (look.spec.ts), which read each
  // program's status after its link.
  if (process.env.GALAXYGEN_REMOUNT_CHECKS === "1")
    await page.addInitScript(() => {
      for (const proto of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) {
        const link = proto.linkProgram;
        proto.linkProgram = function (this: WebGLRenderingContext, program: WebGLProgram) {
          link.call(this, program);
          if (!this.getProgramParameter(program, this.LINK_STATUS)) console.error(`WebGL program not valid: ${this.getProgramInfoLog(program)}`);
        };
      }
    });
  await page.goto("/");
  await page.waitForFunction(() => !!window.__galaxygenFrameSum, null, { timeout: READY.timeoutMs });
  await press(page, "Milky Way");
  await press(page, MODE_BUTTON.field, MODE_BUTTON.stars);
  await page.waitForTimeout(8000);
  const delays = (process.env.GALAXYGEN_REMOUNT_DELAYS ?? "50,150,300,600,1000,2000,4000").split(",").map(Number);
  const toggles: { at: number; delay: number }[] = [];
  for (let round = 0; round < 3; round += 1) {
    for (const delay of delays) {
      toggles.push({ at: Date.now(), delay });
      await page.getByRole("button", { name: "illustrative", exact: true }).click();
      await page.waitForTimeout(delay);
    }
  }
  await page.waitForTimeout(5000);
  const byDelay = new Map<number, number>();
  for (const l of lines) {
    const t = [...toggles].reverse().find((x) => x.at <= l.at);
    if (t) byDelay.set(t.delay, (byDelay.get(t.delay) ?? 0) + 1);
  }
  console.log(`warnings: ${lines.length}; by the delay after the toggle before them: ${JSON.stringify([...byDelay])}`);
  for (const l of lines.slice(0, 12)) console.log(`  +${l.at - toggles[0].at} ms ${l.text.slice(0, 400)}`);
  expect(errors).toEqual([]);
});
