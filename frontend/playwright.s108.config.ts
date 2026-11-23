import { defineConfig } from "@playwright/test";

import { CHOOSING_VIEWPORT, GPU_ARGS, PORT } from "./e2e/settings";

// The controls' probe (S108, builder H: the illustrative look under the owner's controls): e2e/s108/*.probe.ts against
// the API serving this worktree's frontend/dist on GALAXYGEN_E2E_PORT (start it first, as for the look capture).
// S108_PROBE picks the probes (physonly, orbit, stars, reroll; all by default); S108_OUT where the PNGs go
// (default docs/goals/s108/ under the repository, gitignored).
//
//   GALAXYGEN_E2E_PORT=8034 S108_PROBE=physonly npx --prefix frontend playwright test -c frontend/playwright.s108.config.ts
export default defineConfig({
  testDir: "e2e/s108",
  testMatch: "**/*.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 900_000,
  reporter: [["list"]],
  outputDir: "e2e/.output/s108-run",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    viewport: CHOOSING_VIEWPORT,
    launchOptions: { args: GPU_ARGS },
  },
});
