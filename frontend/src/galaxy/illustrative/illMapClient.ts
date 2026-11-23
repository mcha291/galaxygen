// The main side of the illustrative map's worker (S107, the sliders' stall; illMapJob.ts the job, illMap.worker.ts the
// worker), in the pattern of cloudRasterClient.ts. ONE long-lived worker, made at the first job and kept for the page.
// At most one job runs in it; at most one map job and one sparkle job wait, a newer one replacing the one of its kind
// that waits (never posted).
//
// THE MAP CONTRACT. GalaxyTab asks for the planes of the parameters it draws now (startIllMap) only where the runtime
// would have to build (index.ts illStale); until they arrive it draws the previous map and uniforms. Every answer, even
// a superseded one, is put into the features' own caches (seedMemo: a cache keyed by the inputs, so an older answer can
// never stand for newer parameters) and the view is told (illArrivals moves); the view then asks the runtime again
// (updateRuntime), which composes the map from its caches at the parameters drawn NOW - all channels of one parameter
// set - or, where a plane is still missing, asks again. Where there is no Worker (vitest, SSR) or it failed, nothing is
// posted and the runtime builds on this thread as it always did (startIllMap returns false).
//
// The sparkle's points (sparkleJob.ts) go the same way: SparkleLayer asks (requestSparkle) and draws the last points it
// had until the new ones arrive; built here where there is no worker.

import { type IllFrame, illMeasure, illNow, seedMemo } from "./feature";
import type { Encoded, JobAnswer, JobMessage, LanesSpec, MapRequest, Seed, SparkleRequest } from "./illMapJob";
import { type SparklePoints, sparklePoints } from "./sparkleJob";

type Listener = () => void;

let worker: Worker | null = null;
let broken = false;
let nextId = 1;
/** The release's generation: answers to jobs posted before the last release are dropped. */
let generation = 0;

interface Job {
  id: number;
  kind: "map" | "sparkle";
  key: string;
  generation: number;
  posted: number;
  make: () => { message: JobMessage; transfer: Transferable[] };
  /** For a sparkle: built here when the worker cannot. */
  fallback?: () => void;
}
let running: Job | null = null;
const waiting: { map: Job | null; sparkle: Job | null } = { map: null, sparkle: null };

const counts = { posted: 0, answered: 0, seeded: 0, skipped: 0, replaced: 0, dropped: 0, failed: 0, here: 0 };
let lastError: string | null = null;
/** The last job of each kind: its time in the worker and from its post to its answer here, ms (the probe's). */
const times = { map: { ms: 0, roundTripMs: 0 }, sparkle: { ms: 0, roundTripMs: 0 } };

/** Every object a token (the frames, the planes): a key part that moves exactly when the object does. */
const tokens = new WeakMap<object, number>();
let nextToken = 1;
export function objectToken(o: object | null | undefined): number {
  if (!o) return 0;
  let t = tokens.get(o);
  if (t === undefined) {
    t = nextToken++;
    tokens.set(o, t);
  }
  return t;
}

/** The frames sent, by token (the last two), and the one the worker holds. */
const frames = new Map<number, IllFrame | null>();
let workerFrame = -1;
/** The values seeded from the worker, by its ref, and the ref of each (the last 64). */
const byRef = new Map<number, object>();
const refOf = new WeakMap<object, number>();

/**
 * The map key answered last, and the keys that failed: where the key drawn now is the one answered last and the runtime
 * would still build (a cache no seed fills: an unnamed memo), it builds here; a failed key is not asked again. Only the
 * LAST answer counts - an older key's seeds may have been replaced since by a newer answer's, so a return to it asks again.
 */
let answered: string | null = null;
const failedKeys = new Set<string>();
let arrivals = 0;
const listeners = new Set<Listener>();
const tell = () => {
  for (const l of listeners) l();
};

/** Whether jobs go to the worker here (a Worker exists and has not failed). */
export function illWorkerAvailable(): boolean {
  return !broken && typeof Worker !== "undefined";
}

/** The client's counts (the tests' and the probe's): posted, answered, seeds put in caches and skipped, ... */
export function illJobCounts(): Readonly<typeof counts> & { lastError: string | null; times: typeof times } {
  return { ...counts, lastError, times: { map: { ...times.map }, sparkle: { ...times.sparkle } } };
}

/** How many jobs are running or waiting now. */
export const illJobsPending = (): number => (running ? 1 : 0) + (waiting.map ? 1 : 0) + (waiting.sparkle ? 1 : 0);

/** Moves at every arrival (a map's seeds put in the caches, or a sparkle's points): the view's cue to look again. */
export const illArrivals = (): number => arrivals;

/** Hears every arrival and every change of what is pending (useSyncExternalStore's subscribe). */
export function subscribeIll(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function workerOf(): Worker | null {
  if (!illWorkerAvailable()) return null;
  if (!worker) {
    try {
      worker = new Worker(new URL("./illMap.worker.ts", import.meta.url), { type: "module" });
    } catch {
      broken = true;
      return null;
    }
    worker.onmessage = (event: MessageEvent<JobAnswer>) => answeredJob(event.data);
    worker.onerror = (event) => {
      event.preventDefault();
      failed();
    };
  }
  return worker;
}

function post(job: Job) {
  const w = workerOf();
  if (!w) {
    here(job);
    return;
  }
  running = job;
  job.posted = performance.now();
  counts.posted += 1;
  const { message, transfer } = job.make();
  w.postMessage(message, transfer);
}

function next() {
  const job = waiting.map ?? waiting.sparkle;
  if (!job) return;
  if (job === waiting.map) waiting.map = null;
  else waiting.sparkle = null;
  post(job);
}

function enqueue(job: Job) {
  if (running) {
    const slot = waiting[job.kind];
    if (slot) counts.replaced += 1;
    waiting[job.kind] = job;
    tell();
    return;
  }
  post(job);
  tell();
}

/** A job the worker cannot do: a map is left to the main thread's own build (marked answered), a sparkle built here. */
function here(job: Job) {
  counts.here += 1;
  if (job.kind === "map") markAnswered(job.key);
  else job.fallback?.();
  arrivals += 1;
}

function markAnswered(key: string) {
  answered = key;
}

const decode = (e: Encoded): unknown => {
  if (e && typeof e === "object") {
    if ("$frame" in e) return frames.has(e.$frame) ? frames.get(e.$frame) : SKIP;
    return byRef.has(e.$memo) ? byRef.get(e.$memo) : SKIP;
  }
  return e;
};
const SKIP: unique symbol = Symbol("not held");

/** A map answer's seeds put in the features' caches, in the order they were built (an input may name an earlier one's value). */
export function applySeeds(seeds: readonly Seed[]): void {
  for (const seed of seeds) {
    const inputs = seed.inputs.map(decode);
    if (inputs.some((v) => v === SKIP) || !seedMemo(seed.name, inputs, seed.value)) {
      counts.skipped += 1;
      continue;
    }
    counts.seeded += 1;
    if (seed.value && typeof seed.value === "object" && seed.ref > 0) {
      byRef.set(seed.ref, seed.value);
      refOf.set(seed.value, seed.ref);
      while (byRef.size > 64) byRef.delete(byRef.keys().next().value as number);
    }
  }
}

const sparkleListeners = new Map<string, Set<(points: SparklePoints | null) => void>>();
const sparkleKept = new Map<string, SparklePoints | null>();
function keepSparkle(key: string, points: SparklePoints | null) {
  sparkleKept.delete(key);
  sparkleKept.set(key, points);
  while (sparkleKept.size > 2) sparkleKept.delete(sparkleKept.keys().next().value as string);
  const heard = sparkleListeners.get(key);
  sparkleListeners.delete(key);
  for (const l of heard ?? []) l(points);
}

function answeredJob(answer: JobAnswer) {
  if (!running || running.id !== answer.id) return;
  const job = running;
  running = null;
  counts.answered += 1;
  if (answer.kind !== "error") {
    times[answer.kind] = { ms: answer.ms, roundTripMs: performance.now() - job.posted };
    // the worker's stages as measures here (the slider probe's breakdown): each ending now, its own length
    if (answer.kind === "map") for (const [id, ms] of Object.entries(answer.stages)) illMeasure(`worker map ${id}`, illNow() - ms);
    else illMeasure("worker sparkle", illNow() - answer.ms);
  }
  if (job.generation !== generation) counts.dropped += 1;
  else if (answer.kind === "error") {
    counts.failed += 1;
    lastError = answer.message;
    console.warn(`illustrative ${job.kind} job failed: ${answer.message}`);
    if (job.kind === "map") failedKeys.add(job.key);
    else job.fallback?.();
    arrivals += 1;
  } else if (answer.kind === "map") {
    const started = illNow();
    applySeeds(answer.seeds);
    illMeasure("seed", started);
    markAnswered(job.key);
    arrivals += 1;
  } else if (answer.kind === "sparkle") {
    if (answer.missing) job.fallback?.();
    else keepSparkle(job.key, answer.points);
    arrivals += 1;
  }
  next();
  tell();
}

/** The worker failed (its script, or a job's message): the running and waiting jobs done here, and every later one. */
function failed() {
  broken = true;
  worker?.terminate();
  worker = null;
  workerFrame = -1;
  const jobs = [running, waiting.map, waiting.sparkle].filter((j): j is Job => j !== null);
  running = waiting.map = waiting.sparkle = null;
  for (const job of jobs) here(job);
  tell();
}

/** The frame as a request carries it: by token, and itself where the worker may not hold it. */
function frameFields(frame: IllFrame | null): { frameId: number; frame?: IllFrame | null } {
  const frameId = objectToken(frame) || -2;
  frames.set(frameId, frame);
  while (frames.size > 2) frames.delete(frames.keys().next().value as number);
  if (workerFrame === frameId) return { frameId };
  workerFrame = frameId;
  return { frameId, frame };
}

/** The key of a map job: the frame's token, the template, every illustrative value. */
export const illMapKey = (ill: Readonly<Record<string, number>>, context: { template: string | null; frame: IllFrame | null }): string =>
  JSON.stringify([objectToken(context.frame), context.template, ill]);

/** Whether the map job under `key` has been answered (its seeds are in the caches) or has failed. */
export const illMapAnswered = (key: string): boolean => answered === key;
export const illMapFailed = (key: string): boolean => failedKeys.has(key);

/**
 * Asks for the planes at these parameters (key: illMapKey): posted now if the worker is idle, else waiting in place of
 * any map job that waits; nothing more if it runs or waits already. False where there is no worker: the caller builds.
 */
export function startIllMap(key: string, ill: Readonly<Record<string, number>>, context: { template: string | null; frame: IllFrame | null }): boolean {
  if (!illWorkerAvailable()) return false;
  if (running?.key === key || waiting.map?.key === key) return true;
  const frame = context.frame;
  const template = context.template;
  const values = { ...ill };
  enqueue({
    id: nextId++,
    kind: "map",
    key,
    generation,
    posted: 0,
    make() {
      const request: MapRequest = { ...frameFields(frame), template, ill: values };
      return { message: { id: this.id, kind: "map", request }, transfer: [] };
    },
  });
  return true;
}

/** The sparkle's points kept under `key` (undefined: not built yet). */
export const sparkleHeld = (key: string): SparklePoints | null | undefined => sparkleKept.get(key);

/**
 * Asks for the sparkle's points under `key` (sparkleJob.ts sparkleKey) and hears them when they arrive - at once where
 * they are kept, or where there is no worker (built here, on this thread). `lanes`: the composed map's R plane as the
 * texture holds it (index.ts illMapTexture's userData.illPlanes[0]), with the RGBA bytes the layer would read, or null.
 * Returns the function that stops listening.
 */
export function requestSparkle(
  key: string,
  params: Readonly<Record<string, number>>,
  context: { template: string | null; frame: IllFrame | null },
  lanes: { plane: Uint8Array | null; rgba: ArrayLike<number> } | null,
  listener: (points: SparklePoints | null) => void,
): () => void {
  if (sparkleKept.has(key)) {
    listener(sparkleKept.get(key)!);
    return () => undefined;
  }
  let set = sparkleListeners.get(key);
  if (!set) sparkleListeners.set(key, (set = new Set()));
  set.add(listener);
  const stop = () => {
    const now = sparkleListeners.get(key);
    now?.delete(listener);
    if (now && now.size === 0) sparkleListeners.delete(key);
  };
  const values = { ...params };
  const { template, frame } = context;
  const build = () => keepSparkle(key, sparklePoints(values, frame, template, lanes ? lanes.rgba : null));
  if (!illWorkerAvailable()) {
    counts.here += 1;
    build();
    return stop;
  }
  if (running?.key === key || waiting.sparkle?.key === key) return stop;
  const spec: LanesSpec = !lanes
    ? { kind: "none" }
    : !lanes.plane
      ? { kind: "zeros" }
      : refOf.has(lanes.plane)
        ? { kind: "ref", ref: refOf.get(lanes.plane)! }
        : { kind: "bytes", plane: lanes.plane.slice() };
  enqueue({
    id: nextId++,
    kind: "sparkle",
    key,
    generation,
    posted: 0,
    fallback: build,
    make() {
      const request: SparkleRequest = { ...frameFields(frame), template, params: values, lanes: spec };
      return { message: { id: this.id, kind: "sparkle", request }, transfer: spec.kind === "bytes" ? [spec.plane.buffer as ArrayBuffer] : [] };
    },
  });
  return stop;
}

/**
 * Lets go of everything (index.ts releaseShared, the look leaving illustrative): the worker's caches (a release posted
 * in order), the answers of every job posted before now (dropped), the kept sparkle and the keys answered.
 */
export function releaseIllJobs(): void {
  generation += 1;
  waiting.map = waiting.sparkle = null;
  answered = null;
  failedKeys.clear();
  byRef.clear();
  sparkleKept.clear();
  frames.clear();
  if (worker) {
    workerFrame = -1;
    worker.postMessage({ id: nextId++, kind: "release" } satisfies JobMessage);
  }
  tell();
}

/** What the view still owes the picture (GalaxyTab: the debounce held, a plane not drawn yet): the capture's wait. */
let viewPending = false;
export function setIllViewPending(pending: boolean): void {
  viewPending = pending;
}

/** The galaxy each illustrative drawing on screen was built for, against the field's (the probe's check of rule D1). */
let drawnFor: (() => { map: string | null; mapDrawn: boolean; field: string | null }) | null = null;
const sparkleFor = new Map<object, string | null>();
export function setIllDrawnFor(read: typeof drawnFor): void {
  drawnFor = read;
}
/** A sparkle layer's points on screen and the template they were built for (null: none drawn); `owner` its own token. */
export function setSparkleDrawnFor(owner: object, template: string | null): void {
  if (template === null) sparkleFor.delete(owner);
  else sparkleFor.set(owner, template);
}

// The probe (the look capture and the slider probe): how many illustrative builds the picture still waits for.
if (typeof window !== "undefined") {
  const holder = window as unknown as Record<string, unknown>;
  holder.__galaxygenIllPending = () => illJobsPending() + (viewPending ? 1 : 0);
  holder.__galaxygenIllJobs = illJobCounts;
  holder.__galaxygenIllDrawnFor = () => (drawnFor ? { ...drawnFor(), sparkle: [...sparkleFor.values()] } : null);
}
