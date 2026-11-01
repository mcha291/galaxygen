// The compile probe (S78, T29): how long the march's program takes to build on this machine's browser, and which of
// its loops the time is in. Run by `npm --prefix frontend run compile`; it needs no server.
//
// The text measured is the viewer's own: capture.ts, bundled here with vite from this frontend's config, runs the
// viewer's precompileMarch on a blank page and records what three r186 hands to shaderSource (its prefix and
// FieldVolume's VERTEX and fieldFragment), so nothing of three's prefix is reproduced by hand. The variants are text
// edits of that capture (VARIANTS below; each edit must find its line exactly once, or the variant is not applicable
// and says so). Each measurement is a fresh browser (a new GPU process: Chromium's in-memory program cache and ANGLE's
// blob cache start empty) with GPU_ARGS and --disable-gpu-shader-disk-cache, a blank page and a raw WebGL2 context:
// compileShader to COMPILE_STATUS, linkProgram to LINK_STATUS, and the first draw of a full-screen triangle into a
// 1 x 1 half-float target (as the march draws into one) to its readPixels - each timed, the total their sum.
// The variants are taken in turn inside each repeat, so a drift of the machine falls on all of them alike.
//
// Environment:
//   GALAXYGEN_COMPILE_REPEATS   measurements per variant and step count (default 3)
//   GALAXYGEN_COMPILE_VARIANTS  a comma list of variant names to measure (default all)
//   GALAXYGEN_COMPILE_LABEL     the results' name under e2e/.output/compile/ (default "compile")
//   GALAXYGEN_COMPILE_HLSL      1 to also write each variant's translated HLSL (WEBGL_debug_shaders, a browser started
//                               with --enable-privileged-webgl-extensions; never one that is timed)

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { type Browser, chromium, expect, test } from "@playwright/test";

import { GPU_ARGS } from "../settings";

const FRONTEND = fileURLToPath(new URL("../..", import.meta.url));
const OUT = resolve(FRONTEND, "e2e/.output/compile");
const BUNDLE = resolve(OUT, "bundle");
const REPEATS = Number(process.env.GALAXYGEN_COMPILE_REPEATS ?? 3);
const ONLY = (process.env.GALAXYGEN_COMPILE_VARIANTS ?? "").split(",").map((s) => s.trim()).filter(Boolean);
const LABEL = process.env.GALAXYGEN_COMPILE_LABEL ?? "compile";
const HLSL = process.env.GALAXYGEN_COMPILE_HLSL === "1";
const ARGS = [...GPU_ARGS, "--disable-gpu-shader-disk-cache"];
/** The step counts the pinned text is measured at: the viewer's two (the Milky Way's 96, NGC 4414's 48) and two below. */
const STEP_COUNTS = [96, 48, 24, 12];

interface Captured {
  vertex: string;
  fragment: string;
  ms: number;
}

/** Replace `from` by `to` in `text`, where `from` occurs exactly once; null if it does not. */
function once(text: string | null, from: string, to: string): string | null {
  if (text === null) return null;
  const at = text.indexOf(from);
  if (at < 0 || text.indexOf(from, at + 1) >= 0) return null;
  return text.slice(0, at) + to + text.slice(at + from.length);
}

/** The step loop's bound a uniform: the same text for every step count (the shared program). */
function stepsUniform(text: string, steps: number): string | null {
  let t = once(text, "  uniform float subMax;\n", "  uniform float subMax;\n  uniform int steps;\n");
  t = once(t, `1.0 / float(${steps}));`, "1.0 / float(steps));");
  return once(t, `for (int k = 0; k < ${steps}; k++) {`, "for (int k = 0; k < steps; k++) {");
}
/** The sub-samples' loop bounded by n itself, not by the constant with a break. */
function subSamplesDynamic(text: string | null): string | null {
  return once(text, "for (int j = 0; j < 8; j++) {\n        if (j >= n) break;\n", "for (int j = 0; j < n; j++) {\n");
}
/** The pieces' loop bounded by a uniform (pieceMax, set to the constant it replaces). */
function piecesUniform(text: string | null): string | null {
  const t = once(text, "  uniform float subMax;\n", "  uniform float subMax;\n  uniform int pieceMax;\n");
  return once(t, "for (int m = 0; m <= 19; m++) {", "for (int m = 0; m <= pieceMax; m++) {");
}

interface Variant {
  name: string;
  about: string;
  /** The text at a step count, or null where the edit does not apply. */
  text: (fragment: (steps: number) => string, steps: number) => string | null;
  /** The step counts it is measured at; its text the same at each when `shared`. */
  steps: number[];
  shared?: boolean;
}

const VARIANTS: Variant[] = [
  { name: "v0", about: "the text as the viewer has it", text: (f, s) => f(s), steps: STEP_COUNTS },
  { name: "v1", about: "v0, the step loop's bound the uniform steps (one program for every count)", text: (f, s) => stepsUniform(f(s), s), steps: [96], shared: true },
  { name: "v2", about: "v1, the sub-samples' loop j < n (no constant 8 and break)", text: (f, s) => subSamplesDynamic(stepsUniform(f(s), s)), steps: [96], shared: true },
  { name: "v3", about: "v2, the pieces' loop m <= pieceMax (a uniform 19)", text: (f, s) => piecesUniform(subSamplesDynamic(stepsUniform(f(s), s))), steps: [96], shared: true },
  { name: "v4", about: "v0, only the sub-samples' loop j < n", text: (f, s) => subSamplesDynamic(f(s)), steps: [96, 48] },
  { name: "v5", about: "v0, only the pieces' loop m <= pieceMax", text: (f, s) => piecesUniform(f(s)), steps: [96, 48] },
];

interface Timing {
  renderer: string;
  compileMs: number;
  linkMs: number;
  drawMs: number;
  totalMs: number;
  ok: boolean;
  log: string;
}

/** In the page: build the program on a fresh WebGL2 context and time each stage (no closures: it is serialised). */
function measure(arg: { vertex: string; fragment: string; ints: Record<string, number> }): Timing {
  const canvas = document.createElement("canvas");
  canvas.width = 1;
  canvas.height = 1;
  const gl = canvas.getContext("webgl2", { antialias: true, alpha: true, powerPreference: "high-performance" });
  if (!gl) return { renderer: "none", compileMs: 0, linkMs: 0, drawMs: 0, totalMs: 0, ok: false, log: "no webgl2" };
  const info = gl.getExtension("WEBGL_debug_renderer_info");
  const renderer = String(info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
  gl.getExtension("EXT_color_buffer_float");
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, 1, 1, 0, gl.RGBA, gl.HALF_FLOAT, null);
  const fb = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
  // Unbound, or every sampler (unit 0 by default) would read the target it draws into: a feedback loop, which WebGL
  // refuses at the draw (INVALID_OPERATION) before the program is ever run.
  gl.bindTexture(gl.TEXTURE_2D, null);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 0.5, 3, -1, 0.5, -1, 3, 0.5]), gl.STATIC_DRAW);
  gl.finish();

  const t0 = performance.now();
  const vs = gl.createShader(gl.VERTEX_SHADER)!;
  gl.shaderSource(vs, arg.vertex);
  gl.compileShader(vs);
  const fs = gl.createShader(gl.FRAGMENT_SHADER)!;
  gl.shaderSource(fs, arg.fragment);
  gl.compileShader(fs);
  const compiled = Boolean(gl.getShaderParameter(vs, gl.COMPILE_STATUS)) && Boolean(gl.getShaderParameter(fs, gl.COMPILE_STATUS));
  const t1 = performance.now();
  const program = gl.createProgram()!;
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.bindAttribLocation(program, 0, "position");
  gl.linkProgram(program);
  const linked = Boolean(gl.getProgramParameter(program, gl.LINK_STATUS));
  const t2 = performance.now();
  if (!compiled || !linked) {
    const log = `${gl.getShaderInfoLog(vs) ?? ""}\n${gl.getShaderInfoLog(fs) ?? ""}\n${gl.getProgramInfoLog(program) ?? ""}`;
    return { renderer, compileMs: t1 - t0, linkMs: t2 - t1, drawMs: 0, totalMs: t2 - t0, ok: false, log };
  }
  gl.useProgram(program);
  const identity = new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  for (const name of ["modelMatrix", "viewMatrix", "projectionMatrix"]) {
    const at = gl.getUniformLocation(program, name);
    if (at) gl.uniformMatrix4fv(at, false, identity);
  }
  for (const [name, value] of Object.entries(arg.ints)) {
    const at = gl.getUniformLocation(program, name);
    if (at) gl.uniform1i(at, value);
  }
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
  gl.viewport(0, 0, 1, 1);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  const pixel = new Float32Array(4);
  gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.FLOAT, pixel);
  const t3 = performance.now();
  const error = gl.getError();
  return { renderer, compileMs: t1 - t0, linkMs: t2 - t1, drawMs: t3 - t2, totalMs: t3 - t0, ok: error === gl.NO_ERROR, log: error ? `gl error ${error}` : "" };
}

/** In the page: the fragment shader's translation (ANGLE's HLSL), where the browser exposes WEBGL_debug_shaders. */
function translate(fragment: string): string {
  const gl = document.createElement("canvas").getContext("webgl2");
  if (!gl) return "no webgl2";
  const debug = gl.getExtension("WEBGL_debug_shaders");
  if (!debug) return "no WEBGL_debug_shaders";
  const fs = gl.createShader(gl.FRAGMENT_SHADER)!;
  gl.shaderSource(fs, fragment);
  gl.compileShader(fs);
  return debug.getTranslatedShaderSource(fs);
}

async function fresh<T>(args: string[], run: (browser: Browser) => Promise<T>): Promise<T> {
  const browser = await chromium.launch({ headless: true, args });
  try {
    return await run(browser);
  } finally {
    await browser.close();
  }
}

const median = (xs: number[]) => {
  const s = [...xs].sort((a, b) => a - b);
  return s.length % 2 ? s[(s.length - 1) / 2] : 0.5 * (s[s.length / 2 - 1] + s[s.length / 2]);
};

test("the march's program: compile, link and first draw, per variant", async () => {
  test.setTimeout(3_600_000);
  mkdirSync(OUT, { recursive: true });
  const { build } = await import("vite");
  await build({
    configFile: resolve(FRONTEND, "vite.config.ts"),
    root: FRONTEND,
    logLevel: "warn",
    mode: "production",
    publicDir: false,
    define: { "process.env.NODE_ENV": JSON.stringify("production") },
    build: {
      outDir: BUNDLE,
      emptyOutDir: true,
      minify: false,
      lib: { entry: resolve(FRONTEND, "e2e/compile/capture.ts"), formats: ["iife"], name: "galaxygenCompileCapture", fileName: () => "capture.js" },
    },
  });
  const script = readFileSync(resolve(BUNDLE, "capture.js"), "utf8");

  // The viewer's text at each step count it is measured at, and precompileMarch's own time in that page.
  const counts = [...new Set(VARIANTS.flatMap((v) => v.steps))];
  const captured = new Map<number, Captured>();
  for (const steps of counts) {
    const got = await fresh(ARGS, async (browser) => {
      const page = await browser.newPage();
      await page.goto("about:blank");
      await page.addScriptTag({ content: script });
      return page.evaluate(async (s) => {
        const run = (globalThis as unknown as { __galaxygenCompileCapture: (steps: number) => Promise<Captured> }).__galaxygenCompileCapture;
        return run(s);
      }, steps);
    });
    captured.set(steps, got);
    writeFileSync(resolve(OUT, `${LABEL}.fragment.${steps}.glsl`), got.fragment);
  }
  const vertex = captured.get(counts[0])!.vertex;
  for (const c of captured.values()) expect(c.vertex).toBe(vertex);
  writeFileSync(resolve(OUT, `${LABEL}.vertex.glsl`), vertex);
  const fragmentAt = (steps: number) => captured.get(steps)!.fragment;

  interface Row {
    variant: string;
    steps: string;
    about: string;
    text: string | null;
    ints: Record<string, number>;
    runs: Timing[];
  }
  const rows: Row[] = [];
  for (const v of VARIANTS) {
    if (ONLY.length && !ONLY.includes(v.name)) continue;
    for (const steps of v.steps) {
      const text = v.text(fragmentAt, steps);
      rows.push({ variant: v.name, steps: v.shared ? `${steps} (any)` : String(steps), about: v.about, text, ints: { steps, pieceMax: 19 }, runs: [] });
    }
  }
  for (const row of rows) if (row.text) writeFileSync(resolve(OUT, `${LABEL}.${row.variant}.${row.steps.split(" ")[0]}.glsl`), row.text);

  if (HLSL) {
    for (const row of rows) {
      if (!row.text) continue;
      const hlsl = await fresh([...ARGS, "--enable-privileged-webgl-extensions"], async (browser) => {
        const page = await browser.newPage();
        await page.goto("about:blank");
        return page.evaluate(translate, row.text!);
      });
      writeFileSync(resolve(OUT, `${LABEL}.${row.variant}.${row.steps.split(" ")[0]}.hlsl`), hlsl);
    }
  }

  for (let r = 0; r < REPEATS; r += 1) {
    for (const row of rows) {
      if (!row.text) continue;
      const timing = await fresh(ARGS, async (browser) => {
        const page = await browser.newPage();
        await page.goto("about:blank");
        return page.evaluate(measure, { vertex, fragment: row.text!, ints: row.ints });
      });
      row.runs.push(timing);
      console.log(`${row.variant} ${row.steps} run ${r + 1}: total ${timing.totalMs.toFixed(0)} ms (compile ${timing.compileMs.toFixed(0)}, link ${timing.linkMs.toFixed(0)}, draw ${timing.drawMs.toFixed(0)})${timing.ok ? "" : " FAILED " + timing.log}`);
    }
  }

  const renderer = rows.find((r) => r.runs.length)?.runs[0].renderer ?? "unknown";
  const fmt = (xs: number[]) => (xs.length ? `${median(xs).toFixed(0)} [${Math.min(...xs).toFixed(0)}-${Math.max(...xs).toFixed(0)}]` : "-");
  const lines = [
    `compile probe "${LABEL}": ${REPEATS} runs each, a fresh browser per run; ms, median [min-max]`,
    `renderer: ${renderer}`,
    `browser args: ${ARGS.join(" ")}`,
    `precompileMarch in the capture page (the viewer's own call, compileAsync to its resolution): ${[...captured].map(([s, c]) => `${s} steps ${c.ms.toFixed(0)} ms`).join(", ")}`,
    "",
    "variant | steps    | total            | compile        | link             | first draw     | about",
  ];
  for (const row of rows) {
    if (!row.text) {
      lines.push(`${row.variant.padEnd(7)} | ${row.steps.padEnd(8)} | not applicable to this text | ${row.about}`);
      continue;
    }
    const pick = (k: keyof Timing) => row.runs.map((t) => t[k] as number);
    const failed = row.runs.filter((t) => !t.ok);
    lines.push(
      `${row.variant.padEnd(7)} | ${row.steps.padEnd(8)} | ${fmt(pick("totalMs")).padEnd(16)} | ${fmt(pick("compileMs")).padEnd(14)} | ${fmt(pick("linkMs")).padEnd(16)} | ${fmt(pick("drawMs")).padEnd(14)} | ${row.about}${failed.length ? ` (FAILED: ${failed[0].log.trim().slice(0, 200)})` : ""}`,
    );
  }
  const table = lines.join("\n") + "\n";
  console.log(table);
  writeFileSync(resolve(OUT, `${LABEL}.txt`), table);
  writeFileSync(
    resolve(OUT, `${LABEL}.json`),
    JSON.stringify({ label: LABEL, renderer, args: ARGS, repeats: REPEATS, capture: Object.fromEntries([...captured].map(([s, c]) => [s, c.ms])), rows: rows.map(({ text, ...r }) => ({ ...r, applicable: text !== null })) }, null, 2),
  );
  for (const row of rows) for (const t of row.runs) expect(t.ok, `${row.variant} ${row.steps}: ${t.log}`).toBe(true);
});
