import { fileURLToPath } from "node:url";

import { defineConfig } from "@playwright/test";

import { GPU_ARGS, PORT } from "./e2e/settings";

// The picture test (T12, BUILD_III Phase 0): the React viewer captured at fixed cameras on headless Chromium and
// compared with committed frames. A development instrument (BUILD_III section 7, rulings 6 and 10): nothing in
// the pytest suite needs a browser, and tests/test_picture.py runs this only when GALAXYGEN_PICTURE=1.
//
//   npm --prefix frontend run picture          compare with e2e/frames/*.png
//   npm --prefix frontend run picture:update   rewrite them, and e2e/frames.json beside them
const root = fileURLToPath(new URL("..", import.meta.url));

export default defineConfig({
  testDir: "e2e",
  testMatch: "**/*.spec.ts",
  // One page at a time, in the list's order: the captures share one GPU and one server, and the first load
  // computes the default galaxy, which the later ones find cached.
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 240_000,
  reporter: [["list"]],
  outputDir: "e2e/.output",
  // Committed pictures at stable names and no platform suffix, each at the path its capture states from
  // frontend/ (captures.json `file`): e2e/frames/<name>.png, the path tools/goal_metrics.py reads, or a template's
  // thumbnail under public/templates/, where the app serves it from (S54, D213 ruling 7).
  snapshotPathTemplate: "{testDir}/../{arg}{ext}",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    browserName: "chromium",
    headless: true,
    deviceScaleFactor: 1,
    launchOptions: { args: GPU_ARGS },
  },
  // The API serving the built viewer (frontend/dist) from one origin. One already answering on the port is
  // used as it is and left running; one started here is stopped when the run ends.
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
