// The illustrative map's builds as a job (S107, the sliders' stall): what the map worker (illMap.worker.ts) is asked and
// answers, and the job itself. The worker runs the registry's OWN builders (each feature's map.build, through the same
// memoOn caches, so a channel whose inputs did not move is not built again there either) and hears every NAMED memo's
// build (feature.ts observeMemoBuilds). Each build goes back as a seed - the memo's name, its inputs (the frame and
// another memo's value by token) and its value, a map plane's bytes transferred, not copied - and the main thread puts
// it in its own memo under the same inputs (illMapClient.ts), so its synchronous calls (updateRuntime, the uniforms,
// the debounce's probes) find every plane cached and build nothing. The worker answers no picture: what is drawn is
// always what the main thread's own calls return at the parameters drawn now, so a superseded answer can only fill a
// cache, and no upload ever mixes channels of two parameter sets.
//
// The sparkle (sparkleJob.ts) is the other job: its points for the arms' parameters, the lanes read from the copy of
// the R plane the worker kept when it built it (its token).

import { ILL_MAP, type IllFrame, type IllParams, observeMemoBuilds, releaseMemos } from "./feature";
import { features, illContextFor, paramsOf } from "./index";
import { type SparklePoints, sparklePoints } from "./sparkleJob";

/** A memo's input as it crosses: a primitive, the job's frame, or another named memo's value (its ref). */
export type Encoded = string | number | boolean | null | undefined | { $frame: number } | { $memo: number };

/** One named memo's build: its name, inputs, value and the value's ref (another seed's input may name it). */
export interface Seed {
  name: string;
  inputs: Encoded[];
  value: unknown;
  ref: number;
}

/** The planes for these parameters: the frame (sent with its token where the worker may not hold it), the template, all of `ill`. */
export interface MapRequest {
  frameId: number;
  frame?: IllFrame | null;
  template: string | null;
  ill: Record<string, number>;
}

/** How the sparkle reads the lanes: not at all, a map with no lanes (zeros), the worker's kept R plane, or bytes sent. */
export type LanesSpec = { kind: "none" } | { kind: "zeros" } | { kind: "ref"; ref: number } | { kind: "bytes"; plane: Uint8Array };

export interface SparkleRequest {
  frameId: number;
  frame?: IllFrame | null;
  template: string | null;
  params: IllParams;
  lanes: LanesSpec;
}

export type JobMessage =
  | { id: number; kind: "map"; request: MapRequest }
  | { id: number; kind: "sparkle"; request: SparkleRequest }
  | { id: number; kind: "release" };

export type JobAnswer =
  | { id: number; kind: "map"; seeds: Seed[]; ms: number; stages: Record<string, number> }
  | { id: number; kind: "sparkle"; points: SparklePoints | null; missing: boolean; ms: number }
  | { id: number; kind: "error"; message: string };

const PLANE_BYTES = ILL_MAP.width * ILL_MAP.height;

/** A plane of the map that owns its whole buffer (one that can be transferred without taking anything else along). */
const ownPlane = (v: unknown): v is Uint8Array =>
  v instanceof Uint8Array && v.length === PLANE_BYTES && v.byteOffset === 0 && v.buffer.byteLength === v.byteLength;

/** The buffers a seed's value hands over: map planes, the value itself or its own properties, each once. */
export function seedTransfer(seeds: readonly Seed[]): ArrayBuffer[] {
  const out = new Set<ArrayBuffer>();
  for (const { value } of seeds) {
    if (ownPlane(value)) out.add(value.buffer as ArrayBuffer);
    else if (value && typeof value === "object" && !ArrayBuffer.isView(value))
      for (const v of Object.values(value as Record<string, unknown>)) if (ownPlane(v)) out.add(v.buffer as ArrayBuffer);
  }
  return [...out];
}

/** The sparkle's buffers to hand back. */
export function sparkleTransfer(points: SparklePoints | null): ArrayBuffer[] {
  if (!points) return [];
  return [...new Set([points.positions.buffer, points.weight.buffer, points.radius.buffer] as ArrayBuffer[])];
}

/** What the worker holds between jobs: the frame, the refs of the named memos' values, the lanes it kept. */
export class MapJobState {
  frame: { id: number; frame: IllFrame | null } | null = null;
  private refs = new WeakMap<object, number>();
  private nextRef = 1;
  /** The R planes built here, copied before they were transferred (the sparkle reads them), by ref: the last two. */
  private lanes = new Map<number, Uint8Array>();
  /** The last lanes laid out as the layer reads them (RGBA, R the lanes), by its spec's token. */
  private rgba: { token: string; data: Uint8Array } | null = null;

  frameOf(frameId: number, frame: IllFrame | null | undefined): IllFrame | null {
    if (frame !== undefined) this.frame = { id: frameId, frame };
    if (!this.frame || this.frame.id !== frameId) throw new Error(`illustrative map job: frame ${frameId} not held`);
    return this.frame.frame;
  }

  refOf(value: unknown): number {
    if (!value || typeof value !== "object") return 0;
    let ref = this.refs.get(value);
    if (ref === undefined) {
      ref = this.nextRef++;
      this.refs.set(value, ref);
    }
    return ref;
  }

  knownRef(value: unknown): number | undefined {
    return value && typeof value === "object" ? this.refs.get(value) : undefined;
  }

  /**
   * S109 (A4): the named memos' values built here outside a map job (the sparkle's job builds arms.skeleton at its own
   * values), with their names and inputs. No seed went back for them, so a later map job that finds one cached and names
   * it as an input sends its seed first (mapJob's encode) - before, that input had no ref, the dependent seed was dropped,
   * and the main thread, told the job was answered, built the plane itself (a skeleton slider's drag: a 1.4 s long task).
   */
  private unheard = new WeakMap<object, { name: string; inputs: unknown[] }>();

  hearUnheard(name: string, inputs: unknown[], value: unknown) {
    if (value && typeof value === "object" && !this.refs.has(value)) this.unheard.set(value, { name, inputs });
  }

  unheardOf(value: unknown): { name: string; inputs: unknown[] } | undefined {
    return value && typeof value === "object" ? this.unheard.get(value) : undefined;
  }

  keepLanes(ref: number, plane: Uint8Array) {
    if (this.lanes.has(ref)) return;
    this.lanes.set(ref, plane.slice());
    while (this.lanes.size > 2) this.lanes.delete(this.lanes.keys().next().value as number);
  }

  /** The RGBA bytes the sparkle reads for this spec; null where it reads none, undefined where the plane is not held. */
  lanesFor(spec: LanesSpec): Uint8Array | null | undefined {
    if (spec.kind === "none") return null;
    const token = spec.kind === "ref" ? `ref:${spec.ref}` : spec.kind;
    if (spec.kind !== "bytes" && this.rgba?.token === token) return this.rgba.data;
    const plane = spec.kind === "zeros" ? null : spec.kind === "bytes" ? spec.plane : this.lanes.get(spec.ref);
    if (plane === undefined) return undefined;
    const data = new Uint8Array(PLANE_BYTES * 4);
    if (plane) for (let i = 0; i < PLANE_BYTES; i++) data[i * 4] = plane[i];
    this.rgba = { token, data };
    return data;
  }

  release() {
    releaseMemos();
    this.frame = null;
    this.refs = new WeakMap();
    this.unheard = new WeakMap();
    this.lanes.clear();
    this.rgba = null;
  }
}

/**
 * The job: every feature's map builder at these parameters, in the registry's order, the named memos' builds heard and
 * returned as seeds (a value's map planes to be transferred: seedTransfer). The R plane's bytes, where built here, are
 * kept (copied) for the sparkle.
 */
export function mapJob(state: MapJobState, request: MapRequest, stages: Record<string, number> = {}): Seed[] {
  const frame = state.frameOf(request.frameId, request.frame);
  const context = illContextFor({ template: request.template, frame }, request.ill);
  const seeds: Seed[] = [];
  const encode = (v: unknown): Encoded | typeof SKIP => {
    if (v === null || v === undefined || typeof v === "string" || typeof v === "number" || typeof v === "boolean") return v;
    if (v === frame) return { $frame: request.frameId };
    const ref = state.knownRef(v);
    if (ref !== undefined) return { $memo: ref };
    // S109 (A4): a named memo's value built unheard (by the sparkle's job) and found cached by this one: its own seed
    // first, so the main thread holds it by ref when the seed that names it arrives.
    const built = state.unheardOf(v);
    if (!built) return SKIP;
    const inputs = built.inputs.map(encode);
    if (inputs.some((e) => e === SKIP)) return SKIP;
    const made = state.refOf(v);
    seeds.push({ name: built.name, inputs: inputs as Encoded[], value: v, ref: made });
    return { $memo: made };
  };
  const stop = observeMemoBuilds((name, inputs, value) => {
    const encoded = inputs.map(encode);
    const ref = state.refOf(value);
    if (encoded.some((e) => e === SKIP)) return;
    seeds.push({ name, inputs: encoded as Encoded[], value, ref });
  });
  try {
    for (const f of features()) {
      if (!f.map) continue;
      const started = performance.now();
      const built = f.map.build(paramsOf(f, request.ill), context);
      stages[f.id] = performance.now() - started;
      const at = f.map.channels.indexOf(0);
      const lanes = at >= 0 ? built[at] : null;
      if (lanes && lanes.length === PLANE_BYTES) {
        const ref = state.knownRef(lanes);
        if (ref !== undefined) state.keepLanes(ref, lanes);
      }
    }
  } finally {
    stop();
  }
  return seeds;
}

/** The sparkle's job; `missing` where the lanes it names are not held here (the main thread then builds it). */
export function sparkleJob(state: MapJobState, request: SparkleRequest): { points: SparklePoints | null; missing: boolean } {
  const frame = state.frameOf(request.frameId, request.frame);
  const lanes = state.lanesFor(request.lanes);
  if (lanes === undefined) return { points: null, missing: true };
  // S109 (A4): the named memos it builds (the arms' skeleton) heard and kept for a later map job to seed (mapJob's encode).
  const stop = observeMemoBuilds((name, inputs, value) => state.hearUnheard(name, inputs, value));
  try {
    return { points: sparklePoints(request.params, frame, request.template, lanes), missing: false };
  } finally {
    stop();
  }
}

const SKIP: unique symbol = Symbol("unencodable");

/** One message's handling, as the worker does it: its answer and what to transfer with it (null: nothing to answer). */
export function handle(state: MapJobState, message: JobMessage): { answer: JobAnswer; transfer: ArrayBuffer[] } | null {
  const started = performance.now();
  try {
    if (message.kind === "release") {
      state.release();
      return null;
    }
    if (message.kind === "map") {
      const stages: Record<string, number> = {};
      const seeds = mapJob(state, message.request, stages);
      return { answer: { id: message.id, kind: "map", seeds, ms: performance.now() - started, stages }, transfer: seedTransfer(seeds) };
    }
    const { points, missing } = sparkleJob(state, message.request);
    return { answer: { id: message.id, kind: "sparkle", points, missing, ms: performance.now() - started }, transfer: sparkleTransfer(points) };
  } catch (e) {
    return { answer: { id: message.id, kind: "error", message: e instanceof Error ? e.message : String(e) }, transfer: [] };
  }
}
