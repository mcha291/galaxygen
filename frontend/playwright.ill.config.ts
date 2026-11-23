import { defineConfig } from "@playwright/test";

import { CHOOSING_VIEWPORT, GPU_ARGS, PORT } from "./e2e/settings";

// The illustrative sliders' stall probe (S107): e2e/ill/*.probe.ts against the API serving this worktree's
// frontend/dist on GALAXYGEN_E2E_PORT (start it first, as for the look capture). Not the picture test: its files end in
// .probe.ts so that config (testMatch **/*.spec.ts under e2e) never lists them.
//
//   GALAXYGEN_E2E_PORT=8031 npx --prefix frontend playwright test -c frontend/playwright.ill.config.ts
export default defineConfig({
  testDir: "e2e/ill",
  testMatch: "**/*.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 600_000,
  reporter: [["list"]],
  outputDir: "e2e/.output/ill-run",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    viewport: CHOOSING_VIEWPORT,
    launchOptions: { args: GPU_ARGS },
  },
});
