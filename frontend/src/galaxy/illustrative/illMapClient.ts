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
// set - or, where a plane is still missing, asks again. Where there is no Worker (vitest, SSR) or one cannot be made,
// nothing is posted and the runtime builds on this thread as it always did (startIllMap returns false).
//
// A FAILED JOB (S107 fix F1). A job fails three ways: it answers an error, the worker throws uncaught (onerror), or no
// answer comes within ILL_JOB_TIMEOUT_MS (the worker died - closed, killed, out of memory - or hung: the watchdog). Each
// failure is one console.warn (the job's kind and the reason) and the worker is replaced (terminated; a new one made at
// the next post, holding nothing). The job is then asked ONCE again of the new worker - unless a newer job of its kind
// waits, which stands for the parameters drawn now - and if that also fails it is done on this thread: a map's key
// marked answered (the runtime builds it here, so the picture always arrives), a sparkle built here. No key is ever
// left un-asked with nothing in flight, so the pending count returns to 0; the next job goes to a worker again. While
// the last map job failed, illMapFailure names it (the Tuning panel's line); the next map answered clears it.
//
// The sparkle's points (sparkleJob.ts) go the same way: SparkleLayer asks (requestSparkle) and draws the last points it
// had until the new ones arrive; built here where there is no worker.

import { ILL_MAP, type IllFrame, illMeasure, illNow, seedMemo } from "./feature";
import type { Encoded, JobAnswer, JobMessage, LanesSpec, MapRequest, Seed, SparkleRequest } from "./illMapJob";
import { type SparklePoints, sparklePoints } from "./sparkleJob";

type Listener = () => void;

let worker: Worker | null = null;
/** Set only where a Worker cannot be made at all: every job is then done on this thread. */
let broken = false;
let nextId = 1;

/**
 * The watchdog's bound on a running job, ms (S107 fix F1): far above a legitimate job's 0.1-0.5 s (a cold first map at
 * most ~1 s), so it fires only for a worker that died or hung.
 */
export const ILL_JOB_TIMEOUT_MS = 15_000;
let watchdog: ReturnType<typeof setTimeout> | null = null;
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
  /** How many times this job has failed (one retry in a new worker, then done here). */
  failures?: number;
}
let running: Job | null = null;
const waiting: { map: Job | null; sparkle: Job | null } = { map: null, sparkle: null };

const counts = { posted: 0, answered: 0, seeded: 0, skipped: 0, replaced: 0, dropped: 0, failed: 0, here: 0, retried: 0, restarted: 0, timedOut: 0 };
let lastError: string | null = null;
/** The Tuning panel's line while the last map job failed (null: it did not). */
let mapFailure: string | null = null;
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
/** A worker's refs are its own (a new worker numbers from 1 again): both forgotten when the worker is replaced. */
let refOf = new WeakMap<object, number>();

/**
 * The map key answered last: where the key drawn now is the one answered last and the runtime would still build (a
 * cache no seed fills: an unnamed memo; or a job that failed twice, done here), it builds here. Only the LAST answer
 * counts - an older key's seeds may have been replaced since by a newer answer's, so a return to it asks again.
 */
let answered: string | null = null;
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
export function illJobCounts(): Readonly<typeof counts> & { lastError: string | null; mapFailure: string | null; times: typeof times } {
  return { ...counts, lastError, mapFailure, times: { map: { ...times.map }, sparkle: { ...times.sparkle } } };
}

/** The Tuning panel's line while the last map job failed (retried, or rebuilt here), else null. */
export const illMapFailure = (): string | null => mapFailure;

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
    let made: Worker;
    try {
      made = new Worker(new URL("./illMap.worker.ts", import.meta.url), { type: "module" });
    } catch {
      broken = true;
      return null;
    }
    // Events of a worker since replaced are not heard.
    made.onmessage = (event: MessageEvent<JobAnswer>) => {
      if (made === worker) answeredJob(event.data);
    };
    made.onerror = (event) => {
      event.preventDefault();
      if (made !== worker) return;
      const message = (event as ErrorEvent).message;
      jobFailed(`the worker threw${message ? `: ${message}` : ""}`);
    };
    worker = made;
  }
  return worker;
}

/** The worker terminated and forgotten (its frame, its refs): the next post makes a new one, holding nothing. */
function replaceWorker() {
  if (!worker) return;
  worker.terminate();
  worker = null;
  workerFrame = -1;
  byRef.clear();
  refOf = new WeakMap();
  counts.restarted += 1;
}

function stopWatchdog() {
  if (watchdog !== null) clearTimeout(watchdog);
  watchdog = null;
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
  stopWatchdog();
  try {
    const { message, transfer } = job.make();
    w.postMessage(message, transfer);
  } catch (e) {
    jobFailed(`it could not be posted: ${e instanceof Error ? e.message : String(e)}`);
    return;
  }
  watchdog = setTimeout(() => {
    watchdog = null;
    if (running !== job) return;
    counts.timedOut += 1;
    jobFailed(`no answer within ${ILL_JOB_TIMEOUT_MS / 1000} s (the worker died or hung)`);
  }, ILL_JOB_TIMEOUT_MS);
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

const PLANE_BYTES = ILL_MAP.width * ILL_MAP.height;
const isPlane = (v: unknown): boolean => ArrayBuffer.isView(v) && v.byteLength >= PLANE_BYTES;
/** A map plane, or an object one of whose own values is one (arms' planes: share, mean). */
const carriesPlane = (v: object): boolean => isPlane(v) || (!ArrayBuffer.isView(v) && Object.values(v as Record<string, unknown>).some(isPlane));

/** How many values are held by ref for later seeds' inputs, and their map planes' bytes (the review's test). */
export function illHeldByRef(): { count: number; planeBytes: number } {
  let planeBytes = 0;
  for (const v of byRef.values()) {
    if (isPlane(v)) planeBytes += (v as ArrayBufferView).byteLength;
    else for (const p of Object.values(v as Record<string, unknown>)) if (isPlane(p)) planeBytes += (p as ArrayBufferView).byteLength;
  }
  return { count: byRef.size, planeBytes };
}

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
      refOf.set(seed.value, seed.ref);
      // S107 review: a value that is or carries a map plane (7.2 MB each) is not kept by ref - no memo takes a plane as
      // an input (a seed naming one is skipped and built here, as any not held), and the last 64 kept strongly held up
      // to 64 superseded planes (460 MB and more) alive after their memos had moved on.
      if (!carriesPlane(seed.value)) {
        byRef.set(seed.ref, seed.value);
        while (byRef.size > 64) byRef.delete(byRef.keys().next().value as number);
      }
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
  if (answer.kind === "error") {
    counts.answered += 1;
    jobFailed(`it answered an error: ${answer.message}`);
    return;
  }
  stopWatchdog();
  const job = running;
  running = null;
  counts.answered += 1;
  times[answer.kind] = { ms: answer.ms, roundTripMs: performance.now() - job.posted };
  // the worker's stages as measures here (the slider probe's breakdown): each ending now, its own length
  if (answer.kind === "map") for (const [id, ms] of Object.entries(answer.stages)) illMeasure(`worker map ${id}`, illNow() - ms);
  else illMeasure("worker sparkle", illNow() - answer.ms);
  if (job.generation !== generation) counts.dropped += 1;
  else if (answer.kind === "map") {
    const started = illNow();
    applySeeds(answer.seeds);
    illMeasure("seed", started);
    markAnswered(job.key);
    mapFailure = null;
    arrivals += 1;
  } else {
    if (answer.missing) job.fallback?.();
    else keepSparkle(job.key, answer.points);
    arrivals += 1;
  }
  next();
  tell();
}

/**
 * The running job failed (`reason`: it answered an error, the worker threw, or the watchdog fired): one warning, the
 * worker replaced, and the job asked once again of the new worker - or, where a newer job of its kind waits, dropped
 * for that one; failed twice, done on this thread (a map: its key marked answered, so the runtime builds it here).
 */
function jobFailed(reason: string) {
  stopWatchdog();
  const job = running;
  running = null;
  replaceWorker();
  if (!job) {
    next();
    tell();
    return;
  }
  if (job.generation !== generation) {
    counts.dropped += 1;
    next();
    tell();
    return;
  }
  counts.failed += 1;
  job.failures = (job.failures ?? 0) + 1;
  lastError = reason;
  const newer = waiting[job.kind] !== null;
  // A sparkle is not asked again (its lanes may have gone with the first post, transferred): built here at once.
  const retry = !newer && job.kind === "map" && job.failures < 2;
  const outcome = newer ? "dropped for the newer one waiting" : retry ? "asked again of a new worker" : "built on the main thread";
  console.warn(`illustrative ${job.kind} job failed: ${reason}; ${outcome}`);
  if (job.kind === "map") mapFailure = retry || newer ? "the map's worker failed; retrying" : "the map's worker failed; rebuilt here";
  if (retry) {
    counts.retried += 1;
    post(job);
  } else {
    if (!newer) here(job);
    next();
  }
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

/** Whether the map job under `key` has been answered (its seeds are in the caches, or it is left to this thread). */
export const illMapAnswered = (key: string): boolean => answered === key;
/**
 * Whether the map job under `key` failed and will not be asked again: never since S107 fix F1 (a failed job is asked
 * once again of a new worker, then built here), so the runtime's "failed" step no longer occurs.
 */
export const illMapFailed = (_key: string): boolean => false;

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
  mapFailure = null;
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
const sparkleFor = new Map<object, string | (() => string | null)>();
export function setIllDrawnFor(read: typeof drawnFor): void {
  drawnFor = read;
}
/**
 * A sparkle layer's points on screen and the template they were built for (null: none drawn); `owner` its own token.
 * S107 (MW2): or a reading of it made when asked - the template while the layer draws its points this frame, else null
 * (SparkleLayer.tsx draws them only while the field drawn is their galaxy, by the same reading).
 */
export function setSparkleDrawnFor(owner: object, template: string | null | (() => string | null)): void {
  if (template === null) sparkleFor.delete(owner);
  else sparkleFor.set(owner, template);
}
/** S107 (MW2, rule D1): the template whose field is drawn now (GalaxyTab's commit); undefined where no view reports one. */
export function illFieldDrawn(): string | null | undefined {
  return drawnFor ? drawnFor().field : undefined;
}

// The probe (the look capture and the slider probe): how many illustrative builds the picture still waits for.
if (typeof window !== "undefined") {
  const holder = window as unknown as Record<string, unknown>;
  holder.__galaxygenIllPending = () => illJobsPending() + (viewPending ? 1 : 0);
  holder.__galaxygenIllJobs = illJobCounts;
  holder.__galaxygenIllDrawnFor = () =>
    drawnFor ? { ...drawnFor(), sparkle: [...sparkleFor.values()].map((v) => (typeof v === "function" ? v() : v)).filter((v): v is string => v !== null) } : null;
}
