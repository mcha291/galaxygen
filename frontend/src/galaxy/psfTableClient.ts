// The main side of the PSF table worker (S82, #178 (ii)), S81's pattern (meshTexelsClient.ts): ONE long-lived worker,
// made when the first table is asked for and kept for the page's life. A table is asked once per key while it builds
// (a second ask is the first's answer); the worker builds in the order posted. psf.ts keeps the tables that arrive and
// disposes them when the optics change. Where there is no Worker (vitest, SSR), or the worker fails, the table is built
// here, on the main thread, as before S82.
import type { PsfTable } from "./hstPsf";
import { type PsfAnswer, type PsfMessage, type PsfRequest, psfJob } from "./psfTableJob";

/** A table ready: the build's own ms, the post-to-answer ms, and where it was built. */
export interface PsfArrival {
  key: string;
  table: PsfTable;
  /** The build's time, ms: the worker's own (psfJob), or the main thread's. */
  ms: number;
  /** From the job's post to its answer on the main side, ms (the build's time when built here). */
  roundTripMs: number;
  worker: boolean;
}

/** What the probe reads: each build's key, times and place (the table itself left out). */
export type PsfBuild = Omit<PsfArrival, "table">;

let worker: Worker | null = null;
let broken = false;
let nextId = 1;
const running = new Map<number, { key: string; request: PsfRequest; posted: number; resolve: (a: PsfArrival) => void }>();
const asked = new Map<string, Promise<PsfArrival>>();
const builds: PsfBuild[] = [];

/** Whether tables are built in the worker here (a Worker exists and has not failed). */
export function psfWorkerAvailable(): boolean {
  return !broken && typeof Worker !== "undefined";
}

/** The tables building now (asked and not yet answered): the picture test waits for none. */
export function psfPending(): number {
  return asked.size;
}

/** Every build so far, in the order answered: key, ms, round trip, worker. */
export function psfBuilds(): readonly PsfBuild[] {
  return builds.slice();
}

function workerOf(): Worker | null {
  if (!psfWorkerAvailable()) return null;
  if (!worker) {
    try {
      worker = new Worker(new URL("./psfTable.worker.ts", import.meta.url), { type: "module" });
    } catch {
      broken = true;
      return null;
    }
    worker.onmessage = (event: MessageEvent<PsfAnswer>) => answered(event.data);
    worker.onerror = (event) => {
      event.preventDefault();
      failed();
    };
  }
  return worker;
}

function arrive(arrival: PsfArrival, resolve: (a: PsfArrival) => void) {
  asked.delete(arrival.key);
  builds.push({ key: arrival.key, ms: arrival.ms, roundTripMs: arrival.roundTripMs, worker: arrival.worker });
  resolve(arrival);
}

function buildHere(key: string, request: PsfRequest, resolve: (a: PsfArrival) => void) {
  const started = performance.now();
  const table = psfJob(request);
  const ms = performance.now() - started;
  arrive({ key, table, ms, roundTripMs: ms, worker: false }, resolve);
}

function answered({ id, table, ms }: PsfAnswer) {
  const job = running.get(id);
  if (!job) return;
  running.delete(id);
  arrive({ key: job.key, table, ms, roundTripMs: performance.now() - job.posted, worker: true }, job.resolve);
}

/** The worker failed (its script, or a job): every job it held built here, and every later one. */
function failed() {
  broken = true;
  worker?.terminate();
  worker = null;
  const jobs = [...running.values()];
  running.clear();
  for (const job of jobs) buildHere(job.key, job.request, job.resolve);
}

/**
 * Asks for the table under `key` (psf.ts's: the set's pivots, the optics and the switch): posted to the worker, or built
 * here without one. Asking again while it builds is answered by the same promise.
 */
export function askPsfTable(key: string, request: PsfRequest): Promise<PsfArrival> {
  const known = asked.get(key);
  if (known) return known;
  let resolve!: (a: PsfArrival) => void;
  const promise = new Promise<PsfArrival>((r) => (resolve = r));
  asked.set(key, promise);
  const w = workerOf();
  if (!w) {
    buildHere(key, request, resolve);
    return promise;
  }
  const id = nextId;
  nextId += 1;
  running.set(id, { key, request, posted: performance.now(), resolve });
  const message: PsfMessage = { id, request };
  w.postMessage(message);
  return promise;
}

// The probe (the picture test): how many tables build now, and every build's times.
if (typeof window !== "undefined") {
  const holder = window as unknown as Record<string, unknown>;
  holder.__galaxygenPsfPending = psfPending;
  holder.__galaxygenPsfBuilds = psfBuilds;
}
