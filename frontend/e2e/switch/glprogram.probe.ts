// The glGetProgramiv warnings round a canvas remount (S107 GL, docs/BRIEF.md "Known defects" (ii)): every WebGL
// program call wrapped (init script) to log each call on a program that is deleted, null or of another context, with
// its JS stack; every console line kept with its time. A sequence of look and template switches (GL_SEQ) is run
// GL_RUNS times. Fails on any glGetProgramiv console line or any bad call the wrapper saw. The regression check.
//
// What it found (S107 GL): the burst (12 lines, now and then 24 or 48) was raised on the canvas made at a landing from
// the Milky Way on NGC 4414 with the old framing and remade 300 ms later with the new one (GalaxyTab's framing key) -
// some 250-450 ms into that short-lived context's life, while its programs were still linking in parallel
// (KHR_parallel_shader_compile). No call from the page was invalid; told there is no parallel compile, or with a round
// trip after each program call (GL_SYNC), it never came. The sequence and flags that brought it most often:
//   GL_POLL=1 GL_RELOAD=1 GL_RUNS=30 GL_SEQ="T S T S L S"
//   GL_CHROME_ARGS="--disable-gpu-program-cache --disable-gpu-shader-disk-cache"
//   GALAXYGEN_E2E_PORT=8031 npx --prefix frontend playwright test -c frontend/playwright.glprogram.config.ts
// (before the fix: a burst in 13 of 68 such runs; it is also run by playwright.switch.config.ts with its defaults.)
//
//   GL_SEQ tokens, space separated: L (the look toggled), T (the other template pressed), S (wait until the frame is
//   still), W<ms> (wait), O (60 frames of orbit through the capture hook).
//   GL_RELOAD=1: each run on a fresh page. GL_POLL=1: every context's getError read every 50 ms (which context, when).
//   GL_SYNC=1: getError after each program call (its stack). GL_NO_PARALLEL=1: KHR_parallel_shader_compile hidden.
//   GL_HEAVY=1: every call kept (main-thread load). GL_OUT=<file>: the console, the steps and the trace as JSON.

import { writeFileSync } from "node:fs";

import { type Page, expect, test } from "@playwright/test";

import { LOOK_STORAGE_KEY } from "../../src/galaxy/tuning";
import { MODE_BUTTON, READY } from "../settings";

interface BadCall {
  t: number;
  ctx: number;
  fn: string;
  prog: number;
  why: string;
  stack: string;
}
interface GlTrace {
  bad: BadCall[];
  recent: { t: number; ctx: number; fn: string; prog: number; arg?: number }[];
  contexts: { id: number; t: number; lostAt: number; live?: number }[];
}
declare const window: Window & {
  __galaxygenFrameSum?: () => { sum: number[] };
  __galaxygenCapture?: { place(v: object, t?: object): void; where(): Record<string, number> };
  __glTrace?: GlTrace;
};

const LABEL = ["Milky Way", "NGC 4414"];

async function press(page: Page, label: string, siblingOf?: string) {
  const exact = (name: string) => page.getByRole("button", { name, exact: true });
  const button = siblingOf ? exact(siblingOf).locator("xpath=..").getByRole("button", { name: label, exact: true }) : exact(label);
  if ((await button.getAttribute("aria-pressed")) !== "true") await button.click();
  await expect(button).toHaveAttribute("aria-pressed", "true");
}

/** Until the frame's light holds still three reads running; false (and the last reads logged) after `ms`. */
async function still(page: Page, ms = Number(process.env.GL_STILL_MS ?? 60_000)) {
  let last = -1;
  let n = 0;
  const seen: (number | null)[] = [];
  const deadline = Date.now() + Math.min(ms, READY.timeoutMs);
  while (n < 3) {
    if (Date.now() > deadline) {
      console.log(`  not still after ${ms} ms; last reads ${seen.slice(-6).map((s) => (s === null ? "none" : s.toExponential(4))).join(" ")}`);
      return false;
    }
    await page.waitForTimeout(300);
    const sum = await page.evaluate(() => window.__galaxygenFrameSum?.().sum ?? null);
    const s = sum ? sum[0] + sum[1] + sum[2] : null;
    seen.push(s);
    n = s !== null && s > 0 && s === last ? n + 1 : 0;
    last = s ?? -1;
  }
  return true;
}

/** The wrapper, run in the page before any script: each program call checked against its owner and its deletion. */
function wrapWebGl() {
  const trace: GlTrace = { bad: [], recent: [], contexts: [] };
  (window as unknown as { __glTrace: GlTrace }).__glTrace = trace;
  const ctxId = new WeakMap<object, number>();
  const progInfo = new WeakMap<object, { id: number; ctx: number; deleted: boolean }>();
  const live = new Map<number, number>();
  let nextCtx = 0;
  let nextProg = 0;
  const t0 = performance.now();
  const now = () => Math.round(performance.now() - t0);
  (window as unknown as { __glNow: () => number }).__glNow = now;
  const polled: WeakRef<WebGL2RenderingContext>[] = [];
  const idOf = (gl: object) => {
    let id = ctxId.get(gl);
    if (id === undefined) {
      id = ++nextCtx;
      ctxId.set(gl, id);
      trace.contexts.push({ id, t: now(), lostAt: -1 });
      polled.push(new WeakRef(gl as WebGL2RenderingContext));
    }
    return id;
  };
  // GL_POLL: every context's error read every 50 ms (one round trip each), so a GL error raised inside the browser is
  // told with the context it was raised on and the time to 50 ms.
  if ((window as unknown as { __glPoll?: boolean }).__glPoll)
    setInterval(() => {
      for (const ref of polled) {
        const gl = ref.deref();
        if (!gl || gl.isContextLost()) continue;
        const e = gl.getError();
        if (e) trace.bad.push({ t: now(), ctx: idOf(gl), fn: "polled getError", prog: -1, why: `error 0x${e.toString(16)}`, stack: "" });
      }
    }, 50);
  const proto = WebGL2RenderingContext.prototype as unknown as Record<string, (...a: unknown[]) => unknown>;
  const create = proto.createProgram;
  proto.createProgram = function (this: WebGL2RenderingContext) {
    const p = create.call(this) as object;
    if (p) {
      progInfo.set(p, { id: ++nextProg, ctx: idOf(this), deleted: false });
      live.set(idOf(this), (live.get(idOf(this)) ?? 0) + 1);
    }
    return p;
  };
  const progFns = [
    "getProgramParameter", "getProgramInfoLog", "useProgram", "deleteProgram", "linkProgram", "attachShader", "detachShader",
    "getUniformLocation", "getAttribLocation", "getActiveUniform", "getActiveAttrib", "getUniformBlockIndex",
    "uniformBlockBinding", "getActiveUniforms", "getActiveUniformBlockParameter", "getActiveUniformBlockName",
    "validateProgram", "bindAttribLocation", "getAttachedShaders", "getFragDataLocation", "getUniform",
    "transformFeedbackVaryings", "getTransformFeedbackVarying",
  ];
  for (const fn of progFns) {
    const orig = proto[fn];
    if (!orig) continue;
    proto[fn] = function (this: WebGL2RenderingContext, ...a: unknown[]) {
      const p = a[0] as object | null;
      const ctx = idOf(this);
      const info = p ? progInfo.get(p) : undefined;
      const lost = this.isContextLost();
      if ((window as unknown as { __glHeavy?: boolean }).__glHeavy) {
        // S107 GL: the first wrapper, which kept every call (useProgram too) and so loaded the main thread; the burst
        // came at about one template switch in four with it and at none of some fifty without.
        trace.recent.push({ t: now(), ctx, fn, prog: info?.id ?? -1 });
        if (trace.recent.length > 4000) trace.recent.splice(0, 2000);
      } else if (fn !== "useProgram" && fn !== "getUniformLocation") {
        trace.recent.push({ t: now(), ctx, fn, prog: info?.id ?? -1, arg: typeof a[1] === "number" ? (a[1] as number) : undefined });
        if (trace.recent.length > 20000) trace.recent.splice(0, 10000);
      }
      let why = "";
      if (p === null || p === undefined) why = fn === "useProgram" ? "" : "null program";
      else if (!info) why = "unknown program";
      else if (info.ctx !== ctx) why = `program of context ${info.ctx}`;
      else if (info.deleted) why = "deleted program";
      if (why && !lost) trace.bad.push({ t: now(), ctx, fn, prog: info?.id ?? -1, why, stack: new Error().stack ?? "" });
      // GL_SYNC: the service's own error read right after the call (a round trip each), so the call that raised it is
      // known with its stack, whatever the console's delivery time.
      const sync = (window as unknown as { __glSync?: boolean }).__glSync && !lost;
      if (sync) {
        const pre = this.getError();
        if (pre) trace.bad.push({ t: now(), ctx, fn: `before ${fn}`, prog: info?.id ?? -1, why: `error 0x${pre.toString(16)} pending`, stack: "" });
      }
      const r = orig.apply(this, a);
      if (sync) {
        const e = this.getError();
        if (e) trace.bad.push({ t: now(), ctx, fn, prog: info?.id ?? -1, why: `error 0x${e.toString(16)} (arg ${String(a[1])})`, stack: new Error().stack ?? "" });
      }
      if (fn === "deleteProgram" && info && !info.deleted) {
        info.deleted = true;
        live.set(info.ctx, (live.get(info.ctx) ?? 1) - 1);
      }
      return r;
    };
  }
  const ext = proto.getExtension;
  proto.getExtension = function (this: WebGL2RenderingContext, name: string) {
    // GL_NO_PARALLEL: the page told there is no KHR_parallel_shader_compile (three.js then never polls COMPLETION_STATUS)
    if (name === "KHR_parallel_shader_compile" && (window as unknown as { __glNoParallel?: boolean }).__glNoParallel) return null;
    const e = ext.call(this, name) as { loseContext?: () => void } | null;
    if (e && name === "WEBGL_lose_context" && e.loseContext && !(e as { __w?: boolean }).__w) {
      const lose = e.loseContext.bind(e);
      const gl = this;
      (e as { __w?: boolean }).__w = true;
      e.loseContext = () => {
        const c = trace.contexts.find((x) => x.id === idOf(gl));
        if (c) {
          c.lostAt = now();
          c.live = live.get(idOf(gl)) ?? 0;
        }
        if ((window as unknown as { __glSync?: boolean }).__glSync && !gl.isContextLost()) {
          const pre = gl.getError();
          if (pre) trace.bad.push({ t: now(), ctx: idOf(gl), fn: "before loseContext", prog: -1, why: `error 0x${pre.toString(16)} pending`, stack: new Error().stack ?? "" });
        }
        lose();
      };
    }
    return e;
  };
}

test("look and template switches: no program call on a dead program, no glGetProgramiv warning", async ({ page }) => {
  test.setTimeout(3_000_000);
  const seq = (process.env.GL_SEQ ?? "T S T S L S").split(/\s+/).filter(Boolean);
  const runs = Number(process.env.GL_RUNS ?? 3);
  const lines: { t: number; type: string; text: string }[] = [];
  const t0 = Date.now();
  page.on("console", (m) => lines.push({ t: Date.now() - t0, type: m.type(), text: m.text() }));
  page.on("pageerror", (e) => lines.push({ t: Date.now() - t0, type: "pageerror", text: e.message }));
  if (process.env.GL_NO_PARALLEL === "1") await page.addInitScript(() => ((window as unknown as { __glNoParallel: boolean }).__glNoParallel = true));
  if (process.env.GL_POLL === "1")await page.addInitScript(() => ((window as unknown as { __glPoll: boolean }).__glPoll = true));
  if (process.env.GL_HEAVY === "1")await page.addInitScript(() => ((window as unknown as { __glHeavy: boolean }).__glHeavy = true));
  if (process.env.GL_SYNC === "1")await page.addInitScript(() => ((window as unknown as { __glSync: boolean }).__glSync = true));
  await page.addInitScript(wrapWebGl);
  await page.addInitScript(([key]) => localStorage.setItem(key, "illustrative"), [LOOK_STORAGE_KEY] as const);
  let template = 0;
  // The page loaded, the Milky Way under the illustrative look in the field mode, still.
  const land = async () => {
    await page.goto("/");
    await page.waitForFunction(() => !!window.__galaxygenFrameSum && !!window.__galaxygenCapture, null, { timeout: READY.timeoutMs });
    template = 0;
    await press(page, LABEL[template]);
    await press(page, MODE_BUTTON.field, MODE_BUTTON.stars);
    await still(page);
  };
  // GL_RELOAD=1: each run on a fresh page (the burst came mostly at the first switch after a load).
  const reload = process.env.GL_RELOAD === "1";
  const bad: BadCall[] = [];
  const keep = async () => bad.push(...(await page.evaluate(() => window.__glTrace!.bad)));
  await land();
  const steps: { t: number; run: number; step: string }[] = [];
  const perRun: number[] = [];
  for (let run = 0; run < runs; run += 1) {
    if (reload && run > 0) {
      await keep();
      await land();
    }
    const before = lines.filter((l) => /glGetProgramiv/.test(l.text)).length;
    for (const step of seq) {
      steps.push({ t: Date.now() - t0, run, step });
      if (step === "L") await page.getByRole("button", { name: "illustrative", exact: true }).click();
      else if (step === "T") {
        template = 1 - template;
        await page.getByRole("button", { name: LABEL[template], exact: true }).click();
      } else if (step === "S") await still(page);
      else if (step.startsWith("W")) await page.waitForTimeout(Number(step.slice(1)));
      else if (step === "O")
        await page.evaluate(async () => {
          const cap = window.__galaxygenCapture!;
          const base = cap.where();
          for (let i = 1; i <= 60; i += 1) {
            cap.place({ ...base, azimuth_deg: ((base.azimuth_deg ?? 0) + 0.5 * i) % 360 });
            await new Promise((r) => requestAnimationFrame(() => r(null)));
          }
        });
    }
    await still(page);
    perRun.push(lines.filter((l) => /glGetProgramiv/.test(l.text)).length - before);
    // the contexts lost in this run, with the programs still undeleted at the loss
    const lost = await page.evaluate(() => window.__glTrace!.contexts.filter((c) => c.lostAt >= 0).map((c) => `${c.id}:${c.live}`));
    console.log(`run ${run}: glGetProgramiv lines ${perRun[run]}; contexts lost (id:programs live) ${lost.join(" ")}`);
    if (perRun[run] > 0) {
      // the page's clock against the probe's, then each warning, context and polled error on the page's clock
      const pageNow = await page.evaluate(() => (window as unknown as { __glNow: () => number }).__glNow());
      const shift = Date.now() - t0 - pageNow;
      const tr = await page.evaluate(() => window.__glTrace!);
      const warnAt = [...new Set(lines.filter((l) => /glGetProgramiv/.test(l.text)).slice(-perRun[run]).map((l) => `${l.t - shift}:${l.text.slice(1, 22)}`))];
      console.log(`  warnings at (page ms) ${warnAt.join(" ")}`);
      console.log(`  contexts (id made lost) ${tr.contexts.map((c) => `${c.id}:${c.t}-${c.lostAt}`).join(" ")}`);
      console.log(`  polled/bad ${tr.bad.map((b) => `${b.t}:ctx${b.ctx}:${b.fn}:${b.why}`).join(" | ")}`);
    }
  }
  await page.waitForTimeout(2000);
  const trace = await page.evaluate(() => window.__glTrace!);
  bad.push(...trace.bad);
  const warn = lines.filter((l) => /glGetProgramiv|GL_INVALID/.test(l.text));
  const out = process.env.GL_OUT;
  if (out) writeFileSync(out, JSON.stringify({ seq, runs, perRun, steps, lines, trace }, null, 1));
  console.log(`runs with a warning: ${perRun.filter((n) => n > 0).length} of ${runs}; lines ${warn.length}; bad calls ${bad.length}`);
  for (const b of bad.slice(0, Number(process.env.GL_SHOW ?? 5))) console.log(`  bad ${b.fn} ctx ${b.ctx} prog ${b.prog} t ${b.t}: ${b.why}\n${b.stack}`);
  expect(bad.length, "program calls on a dead program").toBe(0);
  expect(warn.length, "glGetProgramiv warnings").toBe(0);
});
