import { defineConfig } from "@playwright/test";

// The compile probe (S78, T29): e2e/compile/compile.probe.ts times the march's program build on this machine's
// browser, per variant of its text. No webServer and no baseURL: the probe launches its own browser for every
// measurement (GPU_ARGS and --disable-gpu-shader-disk-cache, so no program cache hides a compile) on a blank page. The
// file ends in .probe.ts so that the picture test's config (testMatch **/*.spec.ts under e2e) never lists it.
//
// It hosts the march probe too (e2e/compile/march.probe.ts, S78: the march's GPU time per re-march on a standing site);
// each npm script names its one file, so neither runs the other.
//
//   npm --prefix frontend run compile
//   GALAXYGEN_COMPILE_LABEL=after GALAXYGEN_COMPILE_VARIANTS=v0 npm --prefix frontend run compile
//   GALAXYGEN_URL=http://127.0.0.1:8019 npm --prefix frontend run march
export default defineConfig({
  testDir: "e2e/compile",
  testMatch: "**/*.probe.ts",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  reporter: [["list"]],
  outputDir: "e2e/.output/compile-run",
});
