// The main side of the clouds' raster worker (S78, R5). ONE long-lived worker, made when the first raster is asked
// for and kept for the page's life. At most one job runs in it and at most one waits: a newer raster asked while one
// runs replaces the waiting one (never posted), and the running one's answer, if a newer raster was asked since and
// no field still listens for it, is dropped - so at most one stale raster is ever built. What arrives is kept in the
// F1 cache (cloudOpacity.ts keepRaster, its bytes counted as before) under the key the main side computed
// (rasterKey), so a remount or a switch back finds it there synchronously, with no round trip. Where there is no
// Worker (vitest, SSR), or the worker fails, the raster is built here, on the main thread, as before.
import { type KeptRaster, keepRaster, keptRasterHit } from "./cloudOpacity";
import { type RasterAnswer, type RasterMessage, type RasterRequest, rasterJob } from "./cloudRasterJob";

/** A raster ready for the field: the packed raster, the build's own ms, the post-to-answer ms, and where it was built. */
export interface RasterArrival {
  key: string;
  raster: KeptRaster;
  /** The build's time, ms: the worker's own (cloudRaster + packRaster), or the main thread's. */
  ms: number;
  /** From the job's post to its answer on the main side, ms (0 when built here). */
  roundTripMs: number;
  worker: boolean;
}

type Make = () => { request: RasterRequest; transfer: ArrayBuffer[] };
type Listener = (arrival: RasterArrival) => void;

let worker: Worker | null = null;
let broken = false;
let nextId = 1;
let running: { id: number; key: string; posted: number; make: Make } | null = null;
let waiting: { key: string; make: Make } | null = null;
let lastAsked: string | null = null;
let lastArrival: RasterArrival | null = null;
const listeners = new Map<string, Set<Listener>>();
const counts = { posted: 0, answered: 0, stale: 0, replaced: 0 };

/** Whether rasters are built in the worker here (a Worker exists and has not failed). */
export function rasterWorkerAvailable(): boolean {
  return !broken && typeof Worker !== "undefined";
}

/** The worker's counts: jobs posted, answered, answers dropped as stale, waiting jobs replaced before they ran. */
export function rasterWorkerCounts(): Readonly<typeof counts> {
  return { ...counts };
}

function workerOf(): Worker | null {
  if (!rasterWorkerAvailable()) return null;
  if (!worker) {
    try {
      worker = new Worker(new URL("./cloudRaster.worker.ts", import.meta.url), { type: "module" });
    } catch {
      broken = true;
      return null;
    }
    worker.onmessage = (event: MessageEvent<RasterAnswer>) => answered(event.data);
    worker.onerror = (event) => {
      event.preventDefault();
      failed();
    };
  }
  return worker;
}

function finish(arrival: RasterArrival) {
  const heard = listeners.get(arrival.key);
  if (arrival.key !== lastAsked && !heard?.size) {
    counts.stale += 1;
    return;
  }
  keepRaster(arrival.key, arrival.raster);
  lastArrival = arrival;
  listeners.delete(arrival.key);
  for (const listener of heard ?? []) listener(arrival);
}

function buildHere(key: string, make: Make) {
  const started = performance.now();
  const raster = rasterJob(make().request);
  finish({ key, raster, ms: performance.now() - started, roundTripMs: 0, worker: false });
}

function post(key: string, make: Make) {
  const w = workerOf();
  if (!w) {
    buildHere(key, make);
    return;
  }
  const { request, transfer } = make();
  const id = nextId;
  nextId += 1;
  running = { id, key, posted: performance.now(), make };
  counts.posted += 1;
  const message: RasterMessage = { id, request };
  w.postMessage(message, transfer);
}

function next() {
  if (!waiting) return;
  const { key, make } = waiting;
  waiting = null;
  post(key, make);
}

function answered({ id, raster, ms }: RasterAnswer) {
  if (!running || running.id !== id) return;
  const job = running;
  running = null;
  counts.answered += 1;
  finish({ key: job.key, raster, ms, roundTripMs: performance.now() - job.posted, worker: true });
  next();
}

/** The worker failed (its script, or a job): the running and the waiting job built here, and every later one. */
function failed() {
  broken = true;
  worker?.terminate();
  worker = null;
  const job = running;
  running = null;
  if (job) buildHere(job.key, job.make);
  next();
}

/**
 * Asks for the raster under `key` (rasterKey of the census and shape `make` copies): posted now if the worker is idle,
 * else waiting in place of any raster that waits. Asking again for the running or waiting raster does nothing more.
 * The caller has looked in the kept cache first (keptRasterHit).
 */
export function startRaster(key: string, make: Make): void {
  lastAsked = key;
  if (running?.key === key) {
    if (waiting) counts.replaced += 1;
    waiting = null;
    return;
  }
  if (waiting?.key === key) return;
  if (running) {
    if (waiting) counts.replaced += 1;
    waiting = { key, make };
    return;
  }
  post(key, make);
}

/**
 * Hears the raster under `key` when it arrives - at once if it already has (it is the last to arrive, or kept).
 * Returns the function that stops listening.
 */
export function listenRaster(key: string, listener: Listener): () => void {
  if (lastArrival?.key === key) {
    listener(lastArrival);
    return () => undefined;
  }
  const hit = keptRasterHit(key);
  if (hit) {
    listener({ key, raster: hit, ms: 0, roundTripMs: 0, worker: false });
    return () => undefined;
  }
  let set = listeners.get(key);
  if (!set) listeners.set(key, (set = new Set()));
  set.add(listener);
  return () => {
    const now = listeners.get(key);
    now?.delete(listener);
    if (now && now.size === 0) listeners.delete(key);
  };
}
