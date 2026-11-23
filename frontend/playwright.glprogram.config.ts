import { defineConfig } from "@playwright/test";

import { CHOOSING_VIEWPORT, GPU_ARGS, PORT } from "./e2e/settings";

// The glGetProgramiv probe (S107 GL, docs/BRIEF.md "Known defects" (ii)): e2e/switch/glprogram.probe.ts against the API
// serving this worktree's frontend/dist on GALAXYGEN_E2E_PORT. GL_CHROME_ARGS adds browser flags (space separated),
// for instance "--disable-gpu-program-cache --disable-gpu-shader-disk-cache": every program linked cold, as in a fresh
// browser, where the burst came most often.
//
//   GALAXYGEN_E2E_PORT=8031 npx --prefix frontend playwright test -c frontend/playwright.glprogram.config.ts
const extra = (process.env.GL_CHROME_ARGS ?? "").split(/\s+/).filter(Boolean);

export default defineConfig({
  testDir: "e2e/switch",
  testMatch: "glprogram.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 3_000_000,
  reporter: [["list"]],
  outputDir: "e2e/.output/glprogram-run",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    viewport: CHOOSING_VIEWPORT,
    launchOptions: { args: [...GPU_ARGS, ...extra] },
  },
});
