/// <reference types="vitest/config" />
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The reference viewer's modules are imported, not copied: interface/transport.js
// holds the project's one fetch (rule D2) and ramp.js / stars.js / flow.js are
// already tested by tests/js. A second copy here would be a second fetch.
const iface = fileURLToPath(new URL("../interface", import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@interface": iface } },
  server: {
    port: 5173,
    // Same origin in development as in production: the page asks for /api and
    // the dev server hands it to `uv run python -m galaxy.api`.
    proxy: { "/api": "http://127.0.0.1:8017" },
    fs: { allow: [".", iface] },
  },
  build: { outDir: "dist", emptyOutDir: true },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
