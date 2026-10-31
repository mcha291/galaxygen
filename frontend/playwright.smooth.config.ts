import { defineConfig } from "@playwright/test";

import { CHOOSING_VIEWPORT, GPU_ARGS } from "./e2e/settings";

// The smoothness probe (S76, BUILD_IV Phase W5; D240 R1): e2e/smooth/smooth.probe.ts against a site already standing.
// No webServer: tools/smoothness.py stands the model and the gateway locally (and restarts them between states), or
// GALAXYGEN_URL names the deployed site. The probe's file ends in .probe.ts so that the picture test's config
// (testMatch **/*.spec.ts under e2e) never lists it.
//
//   npm --prefix frontend run smooth                                      the local gateway on :8060
//   GALAXYGEN_URL=https://<site> GALAXYGEN_STATE=warm npm --prefix frontend run smooth
export default defineConfig({
  testDir: "e2e/smooth",
  testMatch: "**/*.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  reporter: [["list"]],
  outputDir: "e2e/.output/smooth-run",
  use: {
    baseURL: process.env.GALAXYGEN_URL ?? "http://127.0.0.1:8060",
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    viewport: CHOOSING_VIEWPORT,
    launchOptions: { args: GPU_ARGS },
  },
});
