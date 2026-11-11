import { defineConfig } from "@playwright/test";

import { CHOOSING_VIEWPORT, GPU_ARGS } from "./e2e/settings";

// The request walk (S95, Audit VI F-4-1): e2e/walk/walk.probe.ts against a server already standing - tools/
// walk_requests.py stands the API with the built viewer and the template bundles on :8041 and logs every answer
// (`uv run python tools/walk_requests.py walk ...` runs this config itself). No webServer. The file ends in .probe.ts
// so that the picture test's config (testMatch **/*.spec.ts under e2e) never lists it.
//
//   npm --prefix frontend run walk                         against http://127.0.0.1:8041
//   GALAXYGEN_URL=http://127.0.0.1:<port> npm --prefix frontend run walk
export default defineConfig({
  testDir: "e2e/walk",
  testMatch: "**/*.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  // The whole walk is one test: both templates, every set in both modes, physics only, the Science tab and the
  // clouds' switches. Against the bundles it is minutes; a cold model with no bundle computes every galaxy once.
  timeout: 60 * 60_000,
  reporter: [["list"]],
  outputDir: "e2e/.output/walk-run",
  use: {
    baseURL: process.env.GALAXYGEN_URL ?? "http://127.0.0.1:8041",
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    viewport: CHOOSING_VIEWPORT,
    launchOptions: { args: GPU_ARGS },
  },
});
