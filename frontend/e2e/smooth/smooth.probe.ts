// The smoothness probe (S76, BUILD_IV Phase W5; D240 R1): how long a user waits for the landing, a template switch
// and a zoom step, and where that time goes - the /api answers or the client's own work after them. Run by
// `npm --prefix frontend run smooth` against a site already standing (tools/smoothness.py stands one locally: the model
// on :8050, the gateway on :8060), or against the deployed site with GALAXYGEN_URL. It reads the viewer's own
// instruments and nothing else: readiness through `__galaxygenFrameSum` as the picture test reads it (settings.ts
// READY), the template through the switcher's buttons, the zoom through `__galaxygenCapture.place` at the
// `milky_way-zoom` capture's stand.
//
// Environment:
//   GALAXYGEN_URL        the site (default http://127.0.0.1:8060, the local gateway)
//   GALAXYGEN_RUNS       runs, each on a fresh browser context (default 5)
//   GALAXYGEN_RUN_BASE   the first run's number in the results (default 1; the runner restarts before each run)
//   GALAXYGEN_STATE      a label written into the results: warm | gateway-cold | model-cold
//   GALAXYGEN_HEALTHZ    where /healthz is sampled every 250 ms during each step (default ${GALAXYGEN_URL}/healthz)
//   GALAXYGEN_OUT        the JSON results path (default e2e/.output/smooth/<state>.json)
//   GALAXYGEN_MODEL_URL  optional: the model's own URL, asked /api/version?capture=<marker> before and after each step
//                        so its source log (--source-log) can be cut per step; never through the gateway, so the
//                        gateway's window never counts a marker
//
// The ready instant. `settle` waits READY.quietMs (1.5 s) of network quiet and three still frame sums 250 ms apart
// before it calls a view ready: that is the instrument's confirmation, not the user's wait. Here the frame sum is
// probed every PROBE_MS (each probe's own cost adds to that; the results record the intervals), settle's criteria
// decide THAT the view is ready (no /api in flight and none begun or ended for quietMs + (stillProbes - 1) x probeMs
// after the step began, the sum lit and unchanged for stillProbes x probeMs), and the ready instant is the page-clock
// time of the first probe of that final still run: when the frame first took the value it then held.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { type Page, type Request, expect, test } from "@playwright/test";

import { CHOOSING_VIEWPORT, DEFAULT_TEMPLATE, MODE_BUTTON, READY, SELECTION_TEXT } from "../settings";

const SITE = (process.env.GALAXYGEN_URL ?? "http://127.0.0.1:8060").replace(/\/+$/, "");
const RUNS = Number(process.env.GALAXYGEN_RUNS ?? 5);
const RUN_BASE = Number(process.env.GALAXYGEN_RUN_BASE ?? 1);
const STATE = process.env.GALAXYGEN_STATE ?? "warm";
const HEALTHZ = process.env.GALAXYGEN_HEALTHZ ?? `${SITE}/healthz`;
const OUT = resolve(process.env.GALAXYGEN_OUT ?? fileURLToPath(new URL(`../.output/smooth/${STATE}.json`, import.meta.url)));
const MODEL_URL = (process.env.GALAXYGEN_MODEL_URL ?? "").replace(/\/+$/, "");
/** How often the frame sum is probed, ms: the ready instant's nominal resolution. */
const PROBE_MS = 50;
const HEALTHZ_MS = 250;
/** The template switched to and back from. */
const OTHER = "ngc_4414";
const ZOOM_CAPTURE = "milky_way-zoom";

interface LensCamera {
  inclination_deg: number;
  azimuth_deg: number;
  radius_kpc: number;
  fov_deg: number;
}
interface Target {
  radius_kpc: number;
  azimuth_deg: number;
}
/** The two instruments, as GalaxyView publishes them (typed here, not in a global, so picture.spec.ts's stays its own). */
type Probes = {
  __galaxygenCapture?: { place(view: LensCamera, target?: Target): void };
  __galaxygenFrameSum?: () => { sum: number[] };
};

/** One request of the page: its timing relative to the step it began in, and what the server said of it. */
interface Asked {
  url: string;
  route: string;
  api: boolean;
  method: string;
  /** Bytes of the query: the URL's search for a GET, the form body for a POST (transport.js MAX_URL). */
  query: number;
  start: number;
  response: number | null;
  end: number | null;
  status: number | null;
  /** Response body bytes as sent (Request.sizes().responseBodySize), filled in once known. */
  bytes: number | null;
  cache: string | null;
  source: string | null;
  failed: string | null;
}

function watch(page: Page) {
  const net = { inflight: 0, last: Date.now(), asked: [] as Asked[] };
  const entries = new Map<Request, Asked>();
  // watchApi's definition of an /api request (picture.spec.ts), which READY's quiet is counted over.
  const isApi = (url: string) => new URL(url).pathname.startsWith("/api/");
  page.on("request", (r) => {
    const at = new URL(r.url());
    const api = isApi(r.url());
    const post = r.method() === "POST";
    const entry: Asked = {
      url: r.url().slice(0, 160),
      route: at.pathname,
      api,
      method: r.method(),
      query: post ? (r.postData() ?? "").length : at.search.length,
      start: Date.now(),
      response: null,
      end: null,
      status: null,
      bytes: null,
      cache: null,
      source: null,
      failed: null,
    };
    entries.set(r, entry);
    net.asked.push(entry);
    if (api) {
      net.inflight += 1;
      net.last = Date.now();
    }
  });
  page.on("response", (response) => {
    const entry = entries.get(response.request());
    if (!entry) return;
    const headers = response.headers();
    entry.response = Date.now();
    entry.status = response.status();
    entry.cache = headers["x-gateway-cache"] ?? null;
    entry.source = headers["x-galaxy-source"] ?? null;
  });
  const ended = (r: Request, failed: string | null) => {
    const entry = entries.get(r);
    if (!entry) return;
    entry.end = Date.now();
    entry.failed = failed;
    if (entry.api) {
      net.inflight -= 1;
      net.last = Date.now();
    }
    r.sizes()
      .then((s) => {
        entry.bytes = s.responseBodySize;
      })
      .catch(() => undefined);
  };
  page.on("requestfinished", (r) => ended(r, null));
  page.on("requestfailed", (r) => ended(r, r.failure()?.errorText ?? "failed"));
  return net;
}
type Net = ReturnType<typeof watch>;

/** /healthz every HEALTHZ_MS while a step runs: the most requests computing at the model and waiting for it. */
function sampleHealth() {
  const seen = { samples: 0, errors: 0, inFlight: 0, waiting: 0, statuses: [] as number[] };
  let first: unknown = null;
  const once = async () => {
    try {
      const answer = await fetch(HEALTHZ);
      const body = (await answer.json()) as { limits?: { model?: { in_flight?: number; waiting?: number } } };
      if (first === null) first = body;
      seen.samples += 1;
      if (!seen.statuses.includes(answer.status)) seen.statuses.push(answer.status);
      seen.inFlight = Math.max(seen.inFlight, body.limits?.model?.in_flight ?? 0);
      seen.waiting = Math.max(seen.waiting, body.limits?.model?.waiting ?? 0);
    } catch {
      seen.errors += 1;
    }
  };
  void once();
  const timer = setInterval(() => void once(), HEALTHZ_MS);
  return {
    stop: () => {
      clearInterval(timer);
      return seen;
    },
    first: () => first,
  };
}

/** A marker in the model's source log (asked of the model directly, never through the gateway). */
async function mark(label: string) {
  if (!MODEL_URL) return;
  try {
    await fetch(`${MODEL_URL}/api/version?capture=${encodeURIComponent(label)}`);
  } catch {
    /* the marker is the runner's convenience; a lost one costs only the per-step count */
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** The union of [start, end) intervals, ms. */
function covered(spans: [number, number][]) {
  const sorted = spans.filter(([a, b]) => b > a).sort((x, y) => x[0] - y[0]);
  let total = 0;
  let to = -Infinity;
  for (const [a, b] of sorted) {
    if (b <= to) continue;
    total += b - Math.max(a, to);
    to = b;
  }
  return total;
}

interface StepResult {
  step: string;
  /** The ready instant, ms from the step's start; null when the view never became ready. */
  ready_ms: number | null;
  /** When settle's criteria first held, ms from the step's start (the instrument's confirmation). */
  confirmed_ms: number | null;
  /** The first lit frame, ms from the step's start. */
  first_lit_ms: number | null;
  error: string | null;
  /** Time with at least one /api request in flight before the ready instant, ms: the server and network share. */
  api_wait_ms: number | null;
  /** The ready instant less api_wait_ms: the client's own work (and its idle gaps, the debounces among them). */
  client_ms: number | null;
  /** The last /api answer's end before the ready instant, ms from the step's start, and the client's work after it. */
  last_api_end_ms: number | null;
  after_last_api_ms: number | null;
  /** Time with any request in flight (the page's files too) before the ready instant. */
  any_wait_ms: number | null;
  api_requests: number;
  api_bytes: number;
  other_requests: number;
  other_bytes: number;
  by_cache: Record<string, number>;
  by_source: Record<string, number>;
  statuses: Record<string, number>;
  longest: { route: string; method: string; ms: number; bytes: number | null; cache: string | null; source: string | null; query: number } | null;
  healthz: { samples: number; errors: number; inFlight: number; waiting: number; statuses: number[] };
  probes: { count: number; interval_ms_median: number | null; cost_ms_median: number | null };
  requests: Asked[];
}

const median = (xs: number[]) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  return s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2;
};
const count = (xs: (string | null)[]) => xs.reduce<Record<string, number>>((acc, x) => ({ ...acc, [x ?? "none"]: (acc[x ?? "none"] ?? 0) + 1 }), {});

/**
 * One step: `act` starts it (a navigation, a press, a placement), then the frame sum is probed until settle's
 * criteria hold or READY.timeoutMs has passed. `selection`: the star-first mode's sentence must be on the page too.
 */
async function step(page: Page, net: Net, label: string, act: () => Promise<void>, selection = false): Promise<StepResult> {
  await mark(`${label}-begin`);
  const health = sampleHealth();
  const from = net.asked.length;
  const t0 = Date.now();
  let error: string | null = null;
  let runKey = "";
  let runStart = 0;
  let firstLit: number | null = null;
  let confirmed: number | null = null;
  const probeAt: number[] = [];
  const probeCost: number[] = [];
  try {
    await act();
  } catch (e) {
    error = `the step's action failed: ${String(e).slice(0, 300)}`;
  }
  const deadline = t0 + READY.timeoutMs;
  const quietNeeded = READY.quietMs + (READY.stillProbes - 1) * READY.probeMs;
  const stillNeeded = READY.stillProbes * READY.probeMs;
  while (error === null) {
    if (Date.now() > deadline) {
      error = `not ready in ${READY.timeoutMs} ms: ${net.inflight} /api requests in flight, frame sum ${runKey || "unlit"}`;
      break;
    }
    let probe: { at: number; done: number; sum: number[] | null };
    try {
      probe = await page.evaluate(() => {
        const at = Date.now();
        const f = (window as unknown as Probes).__galaxygenFrameSum;
        const sum = f ? f().sum : null;
        return { at, done: Date.now(), sum };
      });
    } catch {
      // A navigation still committing, or the canvas remade: no frame to read this time.
      probe = { at: Date.now(), done: Date.now(), sum: null };
    }
    probeAt.push(probe.at);
    probeCost.push(probe.done - probe.at);
    const lit = !!probe.sum && probe.sum.some((v) => v > 0);
    const key = lit ? probe.sum!.join(",") : "";
    if (!lit) runKey = "";
    else if (key !== runKey) {
      runKey = key;
      runStart = probe.at;
    }
    if (lit && firstLit === null) firstLit = probe.at;
    const now = Date.now();
    const quiet = net.inflight === 0 && now - Math.max(net.last, t0) >= quietNeeded;
    if (lit && quiet && now - runStart >= stillNeeded && (!selection || (await page.getByText(SELECTION_TEXT).isVisible()))) {
      confirmed = now;
      break;
    }
    const wait = probe.at + PROBE_MS - Date.now();
    if (wait > 0) await sleep(wait);
  }
  const seen = health.stop();
  await mark(`${label}-end`);
  // Answers still arriving (sizes are filled in asynchronously) settle before the step is read.
  await sleep(100);
  const asked = net.asked.slice(from).map((a) => ({ ...a, start: a.start - t0, response: a.response === null ? null : a.response - t0, end: a.end === null ? null : a.end - t0 }));
  const ready = confirmed === null ? null : runStart - t0;
  const before = ready === null ? asked : asked.filter((a) => a.start < ready);
  const api = before.filter((a) => a.api);
  const other = before.filter((a) => !a.api);
  const limit = ready ?? Date.now() - t0;
  const spans = (xs: Asked[]) => xs.map((a): [number, number] => [Math.max(0, a.start), Math.min(a.end ?? limit, limit)]);
  const apiWait = covered(spans(api));
  const lastEnd = api.length ? Math.max(...api.map((a) => Math.min(a.end ?? limit, limit))) : null;
  const longest = api
    .filter((a) => a.end !== null)
    .map((a) => ({ route: a.route, method: a.method, ms: a.end! - a.start, bytes: a.bytes, cache: a.cache, source: a.source, query: a.query }))
    .sort((x, y) => y.ms - x.ms)[0] ?? null;
  const intervals = probeAt.slice(1).map((t, k) => t - probeAt[k]);
  return {
    step: label.split("-").pop()!,
    ready_ms: ready,
    confirmed_ms: confirmed === null ? null : confirmed - t0,
    first_lit_ms: firstLit === null ? null : firstLit - t0,
    error,
    api_wait_ms: ready === null ? null : apiWait,
    client_ms: ready === null ? null : ready - apiWait,
    last_api_end_ms: lastEnd,
    after_last_api_ms: ready === null || lastEnd === null ? null : ready - lastEnd,
    any_wait_ms: ready === null ? null : covered(spans(before)),
    api_requests: api.length,
    api_bytes: api.reduce((s, a) => s + (a.bytes ?? 0), 0),
    other_requests: other.length,
    other_bytes: other.reduce((s, a) => s + (a.bytes ?? 0), 0),
    by_cache: count(api.map((a) => a.cache)),
    by_source: count(api.map((a) => a.source)),
    statuses: count(api.map((a) => String(a.status))),
    longest,
    healthz: seen,
    probes: { count: probeAt.length, interval_ms_median: median(intervals), cost_ms_median: median(probeCost) },
    requests: asked,
  };
}

const CAPTURES = JSON.parse(readFileSync(fileURLToPath(new URL("../captures.json", import.meta.url)), "utf-8")) as {
  captures: { name: string; camera: LensCamera; stand?: { target: Target; radius_kpc: number } }[];
};

const fmt = (x: number | null) => (x === null ? "-" : (x / 1000).toFixed(2));
const range = (xs: number[]) => (xs.length ? `${fmt(Math.min(...xs))}-${fmt(Math.max(...xs))}` : "-");

test.use({ viewport: CHOOSING_VIEWPORT });

test(`smoothness: ${STATE}, ${RUNS} run(s) on ${SITE}`, async ({ browser }) => {
  test.setTimeout(RUNS * 20 * 60_000);
  const templates = (await (await fetch(`${SITE}/api/templates`)).json()) as { default: string; templates: { name: string; label: string }[] };
  const labelOf = (name: string) => {
    const t = templates.templates.find((x) => x.name === name);
    if (!t) throw new Error(`the site serves no template ${name}`);
    return t.label;
  };
  const home = labelOf(templates.default ?? DEFAULT_TEMPLATE);
  const away = labelOf(OTHER);
  const zoom = CAPTURES.captures.find((c) => c.name === ZOOM_CAPTURE);
  if (!zoom?.stand) throw new Error(`captures.json has no stand for ${ZOOM_CAPTURE}`);
  const zoomCamera: LensCamera = { ...zoom.camera, radius_kpc: zoom.stand.radius_kpc };
  const zoomTarget = zoom.stand.target;
  const healthz = await fetch(HEALTHZ).then(
    async (r) => ({ status: r.status, body: (await r.json()) as unknown }),
    (e) => ({ status: 0, body: String(e) }),
  );
  console.log(`healthz once: ${JSON.stringify(healthz)}`);

  const runs: { run: number; renderer: string | null; steps: StepResult[] }[] = [];
  for (let i = 0; i < RUNS; i += 1) {
    const n = RUN_BASE + i;
    const tag = `smooth-${STATE}-${n}`;
    // A fresh context per run: no cookies, no storage, an empty HTTP cache (the page's files are fetched again).
    const context = await browser.newContext({ viewport: CHOOSING_VIEWPORT, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const net = watch(page);
    const steps: StepResult[] = [];
    const press = async (label: string) => {
      const button = page.getByRole("button", { name: label, exact: true });
      await button.click({ timeout: READY.standMs });
      await expect(button).toHaveAttribute("aria-pressed", "true", { timeout: READY.standMs });
    };
    // (a) the first paint: navigation to the landing's ready frame.
    steps.push(await step(page, net, `${tag}-first_paint`, async () => void (await page.goto(`${SITE}/`, { waitUntil: "commit" }))));
    let renderer: string | null = null;
    if (steps[0].error === null) {
      renderer = await page.evaluate(() => {
        const gl = document.querySelector("canvas")?.getContext("webgl2");
        const info = gl?.getExtension("WEBGL_debug_renderer_info");
        return gl ? String(info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)) : null;
      });
      // (b) the template switch, both ways, through the switcher's buttons.
      steps.push(await step(page, net, `${tag}-switch_to_${OTHER}`, () => press(away)));
      steps.push(await step(page, net, `${tag}-switch_back`, () => press(home)));
      // (c) the zoom step: the star-first mode (its own load timed as well, not a W5 step), then the stand.
      steps.push(await step(page, net, `${tag}-mode_stars`, () => press(MODE_BUTTON.stars), true));
      steps.push(
        await step(
          page,
          net,
          `${tag}-zoom`,
          () => page.evaluate(([c, t]) => (window as unknown as Probes).__galaxygenCapture!.place(c, t), [zoomCamera, zoomTarget] as const),
          true,
        ),
      );
    }
    runs.push({ run: n, renderer, steps });
    await context.close();
    for (const s of steps) console.log(`run ${n} ${s.step}: ready ${fmt(s.ready_ms)} s (api ${fmt(s.api_wait_ms)}, client ${fmt(s.client_ms)}), ${s.api_requests} /api${s.error ? `, ERROR ${s.error}` : ""}`);
  }

  mkdirSync(dirname(OUT), { recursive: true });
  const about = {
    site: SITE,
    state: STATE,
    healthz: HEALTHZ,
    probe_ms: PROBE_MS,
    ready: READY,
    zoom: { capture: ZOOM_CAPTURE, camera: zoomCamera, target: zoomTarget },
    healthz_once: healthz,
    taken: new Date().toISOString(),
  };
  writeFileSync(OUT, `${JSON.stringify({ about, runs }, null, 1)}\n`, "utf-8");

  const names = [...new Set(runs.flatMap((r) => r.steps.map((s) => s.step)))];
  const lines = [`| ${STATE} | ready s, median (range) | api wait s | client s | /api reqs | longest /api |`, "|---|---|---|---|---|---|"];
  for (const name of names) {
    const got = runs.map((r) => r.steps.find((s) => s.step === name)).filter((s): s is StepResult => !!s);
    const ok = got.filter((s) => s.ready_ms !== null);
    const pick = (f: (s: StepResult) => number | null) => ok.map(f).filter((x): x is number => x !== null);
    const long = ok.map((s) => s.longest).filter((l) => !!l).sort((a, b) => b!.ms - a!.ms)[0];
    lines.push(
      `| ${name} | ${fmt(median(pick((s) => s.ready_ms)))} (${range(pick((s) => s.ready_ms))})${ok.length < got.length ? ` ${got.length - ok.length} failed` : ""} | ${fmt(median(pick((s) => s.api_wait_ms)))} | ${fmt(median(pick((s) => s.client_ms)))} | ${median(ok.map((s) => s.api_requests)) ?? "-"} | ${long ? `${long.route} ${fmt(long.ms)} s` : "-"} |`,
    );
  }
  console.log(`\n${lines.join("\n")}\n\nwritten ${OUT}`);
});
