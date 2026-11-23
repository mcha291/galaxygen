import { fileURLToPath } from "node:url";

import { defineConfig } from "@playwright/test";

import { GPU_ARGS, PORT } from "./e2e/settings";

// The look capture (S105, BUILD_VIII row 105): e2e/look.spec.ts, frames of either look for tools/goal_sheet.py. Not the
// picture test (playwright.config.ts ignores this spec): nothing is compared or committed.
//
//   npm --prefix frontend run look      (GALAXYGEN_E2E_PORT, GALAXYGEN_LOOK_DIR, GALAXYGEN_LOOK_ONLY, GALAXYGEN_LOOK_COMBINATION)
const root = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  testDir: "e2e",
  testMatch: "look.spec.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 240_000,
  reporter: [["list"]],
  outputDir: "e2e/.output/look-run",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    launchOptions: { args: GPU_ARGS },
  },
  // One already answering on the port (started with --bundles, so nothing is recomputed) is used and left running.
  webServer: {
    command: `uv run python -m galaxy.api --port ${PORT} --client frontend/dist`,
    cwd: root,
    url: `http://127.0.0.1:${PORT}/api/version`,
    reuseExistingServer: true,
    timeout: 120_000,
    stdout: "ignore",
    stderr: "pipe",
  },
});
