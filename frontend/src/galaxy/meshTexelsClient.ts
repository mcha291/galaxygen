// The main side of the field mesh's texels worker (S81, #208 (b)), the clouds' raster client's pattern
// (cloudRasterClient.ts): ONE long-lived worker, made when the first mesh is asked for and kept for the page's life. At
// most one job runs in it and at most one waits: a newer mesh asked while one runs replaces the waiting one (never
// posted), and the running one's answer, if a newer mesh was asked since and no field still listens for it, is dropped -
// so at most one stale build is ever made. Unlike the raster, nothing is kept across remounts: the field refills its
// stellar texture in place when an age switch moves (FieldVolume's fillStars), so an answer's textures are handed to
// one field and to no other. Where there is no Worker (vitest, SSR), or the worker fails, the texels are built here, on
// the main thread, as before.
import { type MeshAnswer, type MeshMessage, type MeshRequest, type MeshTexels, meshTexels } from "./meshTexelsJob";

/** A mesh's texels ready for the field: the texels, the build's own ms, the post-to-answer ms, and where they were built. */
export interface MeshArrival {
  key: string;
  texels: MeshTexels;
  /** The build's time, ms: the worker's own (meshTexels), or the main thread's. */
  ms: number;
  /** From the job's post to its answer on the main side, ms (0 when built here). */
  roundTripMs: number;
  worker: boolean;
}

type Make = () => { request: MeshRequest; transfer: ArrayBuffer[] };
type Listener = (arrival: MeshArrival) => void;

let worker: Worker | null = null;
let broken = false;
let nextId = 1;
let running: { id: number; key: string; posted: number; make: Make } | null = null;
let waiting: { key: string; make: Make } | null = null;
let lastAsked: string | null = null;
/** An answer that came before its field listened (the field's effect runs after its render): handed to the first listener. */
let unheard: MeshArrival | null = null;
const listeners = new Map<string, Set<Listener>>();
const counts = { posted: 0, answered: 0, stale: 0, replaced: 0 };

/** Whether meshes are built in the worker here (a Worker exists and has not failed). */
export function meshWorkerAvailable(): boolean {
  return !broken && typeof Worker !== "undefined";
}

/** The worker's counts: jobs posted, answered, answers dropped as stale, waiting jobs replaced before they ran. */
export function meshWorkerCounts(): Readonly<typeof counts> {
  return { ...counts };
}

function workerOf(): Worker | null {
  if (!meshWorkerAvailable()) return null;
  if (!worker) {
    try {
      worker = new Worker(new URL("./meshTexels.worker.ts", import.meta.url), { type: "module" });
    } catch {
      broken = true;
      return null;
    }
    worker.onmessage = (event: MessageEvent<MeshAnswer>) => answered(event.data);
    worker.onerror = (event) => {
      event.preventDefault();
      failed();
    };
  }
  return worker;
}

function finish(arrival: MeshArrival) {
  const heard = listeners.get(arrival.key);
  if (!heard?.size) {
    if (arrival.key === lastAsked) unheard = arrival;
    else counts.stale += 1;
    return;
  }
  listeners.delete(arrival.key);
  // One field takes the textures (they are refilled in place): the first listener.
  const [first] = heard;
  first(arrival);
}

function buildHere(key: string, make: Make) {
  const started = performance.now();
  const texels = meshTexels(make().request);
  finish({ key, texels, ms: performance.now() - started, roundTripMs: 0, worker: false });
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
  const message: MeshMessage = { id, request };
  w.postMessage(message, transfer);
}

function next() {
  if (!waiting) return;
  const { key, make } = waiting;
  waiting = null;
  post(key, make);
}

function answered({ id, texels, ms }: MeshAnswer) {
  if (!running || running.id !== id) return;
  const job = running;
  running = null;
  counts.answered += 1;
  finish({ key: job.key, texels, ms, roundTripMs: performance.now() - job.posted, worker: true });
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
 * Asks for the mesh's texels under `key` (FieldVolume's: the frame, the render and the layer's tables it reads, the
 * threshold's use and the age switches): posted now if the worker is idle, else waiting in place of any mesh that waits.
 * Asking again for the running or waiting mesh does nothing more.
 */
export function startMesh(key: string, make: Make): void {
  lastAsked = key;
  if (unheard && unheard.key !== key) unheard = null;
  if (unheard?.key === key) return;
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
 * Hears the texels under `key` when they arrive - at once if they came before this listened. Returns the function that
 * stops listening.
 */
export function listenMesh(key: string, listener: Listener): () => void {
  if (unheard?.key === key) {
    const arrival = unheard;
    unheard = null;
    listener(arrival);
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
