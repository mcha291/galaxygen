// The illustrative look's feature contract (S105, BUILD_VIII row 105, D275): what one feature file exports. Types and
// small helpers only - no feature imports this file's siblings, and nothing here imports tuning.ts at run time, so the
// registry (index.ts) can be read by tuning.ts without a cycle. The hook contract itself is index.ts's header.

import type { ComponentType } from "react";

/**
 * An /api/arrays answer as a feature reads it (api.ts Frame, restated so this file imports nothing of the transport and
 * the e2e tools can import the registry): the header's scalars and the named arrays.
 */
export interface IllFrame {
  header: { scalars: Record<string, number>; [key: string]: unknown };
  arrays: Record<string, Float64Array | Float32Array | BigInt64Array>;
}

/** One slider of a feature. Its value is stored in Tuning.ill under `${feature.id}.${key}`, clamped to [min, max]. */
export interface IllControl {
  /** The feature-local key (letters and digits); the stored key is `${feature.id}.${key}`. */
  key: string;
  label: string;
  min: number;
  max: number;
  /** The slider's grain (a log control rounds to three significant figures instead). */
  step: number;
  /** A logarithmic slider (min must be above 0). */
  log?: boolean;
  /** Shown after the value: "kpc", "stops", "×" or "". */
  unit?: string;
  /** The default on every template... */
  default: number;
  /** ...unless the template has its own here (the illustrative preset, tuned to the goal pictures). */
  perTemplate?: Readonly<Record<string, number>>;
  /** What it does, one line: an illustrative choice, never physics. */
  about: string;
}

/** A feature's own parameters, by its local keys, each already clamped. */
export type IllParams = Readonly<Record<string, number>>;

/** What a feature's uniforms are computed from besides its parameters. */
export interface IllContext {
  /** The template on screen (null without one). */
  template: string | null;
  /**
   * The /api/arrays answer for every array any registered feature names in `arrays` (one request through api.ts
   * loadArrays, the one transport), for the galaxy on screen; null until it has arrived or when no feature asks.
   */
  frame: IllFrame | null;
  /**
   * (S106, B4) Every registered feature's CURRENT parameters (the values being drawn, clamped), by feature id: a
   * read-only accessor so one feature may read another's live sliders (the lanes read the arms' skeleton). Bound by
   * index.ts (illContextFor) around every call of a feature's map builder, its uniforms and the debounce's probes, and
   * handed to the layers the same way; an unknown id reads {}. Absent only on a context built by hand (a test): a reader
   * then falls back to its own defaults. A value read through it that shapes a plane must be in that plane's memo keys.
   */
  paramsOf?: (featureId: string) => IllParams;
}

/** The march hooks a feature may take part in: each names a GLSL function the feature's `glsl` defines. */
export interface IllHooks {
  /** `float f(vec2 rp)`: extra face-on A_V (magnitudes) at the midplane point rp; summed over features. */
  dustAv?: string;
  /** `float f(vec2 rp)`: a multiplier on the young (clustered) starlight at rp; multiplied over features. */
  youngGain?: string;
  /** `float f(float r)`: a multiplier on all emission and depth at radius r; multiplied over features. */
  edge?: string;
  /**
   * `vec3 f(vec2 rp)` (S107): a per-channel multiplier on a ray's whole light, read once where the ray crosses the
   * midplane; multiplied over features. A drawing laid over the picture (a lane inked in front of all the starlight),
   * not a depth in the dust's layer: the march only, the points are not veiled.
   */
  veil?: string;
  /** `vec3 f(vec2 rp)`: a per-channel multiplier on the disc's starlight at rp (S108); multiplied over features. */
  light?: string;
  /**
   * `float f(vec2 xy, float g)` (S106): the gas fluctuation map's value g at the face-on point xy (kpc, noise.glsl.ts's
   * frame) made the value the dust's placement is multiplied by; chained over features. Read where the map is drawn
   * (the march's screenGas, FluxPoints' gasAt) and only while it is; it must be defined in `noiseGlsl`.
   */
  gas?: string;
  /**
   * `vec3 f(vec3 d, vec2 rp)` (S106, the base's mend): the ring texture's face-on diffuse depth per channel d, as read
   * at the midplane point rp (before the placement, the clouds' share and the extinction strength multiply it), made the
   * depth the dust's layer carries; chained over features. The march's tau and FluxPoints' face; it must be defined in
   * `noiseGlsl` (it may read the `rings` texture, which only those two shaders bind).
   */
  depth?: string;
}

/** What a feature's own drawing (`layer`) receives: drawn inside the Galaxy view's canvas under the illustrative look. */
export interface IllLayerProps {
  params: IllParams;
  /** The shared uniforms (index.ts IllRuntime): hand them to a material to read the hooks' textures. */
  runtime: IllRuntimeLike;
  context: IllContext;
  /** The HII regions as the field mode draws them as knots (GalaxyTab's knotPoints), or null where none is drawn. */
  knots: { positions: Float32Array; flux: Float32Array; extent: Float32Array } | null;
  /** The knots' FluxPoints gain (GalaxyTab's knotsGain). */
  knotsGain: number;
  /** The march's dust as the points read it (FluxPoints' PointDust), or null. */
  dust: unknown;
}

/** index.ts IllRuntime's shape, restated so this file imports nothing of its siblings. */
export interface IllRuntimeLike {
  glsl: string;
  uniforms: Record<string, { value: unknown }>;
  version: number;
}

/**
 * The shared illustrative map's grid (index.ts owns the map; S105 fix): `width` texels along R over [0, rHi], `height`
 * rows round one turn of phi, cell-centred (u = (col + 0.5) / width = R / rHi, v = (row + 0.5) / height = phi / 2 pi),
 * row-major: the byte of texel (col, row) at index row * width + col. Clamped in R, wrapped in phi, linear filtering.
 * The lanes' grid (lanesMap.ts LANE_MAP: 15 pc by 0.1 degree at rHi = 30 kpc).
 */
export const ILL_MAP = { width: 2000, height: 3600 } as const;

/** The map's channels, by index: R the lanes, G the flocculent network (floc.ts), B and A the arms. */
export const ILL_MAP_CHANNELS = { lanes: [0], floc: [1], arms: [2, 3] } as const;

/**
 * A feature's share of the shared map: the channels it owns (0 R, 1 G, 2 B, 3 A; each owned by one feature) and a
 * builder of their bytes (S107: run in the map worker as well - pure, its plane memos named; index.ts's header), one plane per channel in `channels`' order, each ILL_MAP.width * ILL_MAP.height bytes laid
 * out as ILL_MAP says, or null for a channel that reads zero. Called at every change of a parameter or the context:
 * the feature caches its planes (memoOn) and returns the same Uint8Array while nothing that shapes them changed - the
 * registry re-composes and re-uploads the map only when some plane's object changes. The march's GLSL reads the
 * channels through `vec4 illMap(vec2 rp)`.
 */
export interface IllMapBuilder {
  channels: readonly number[];
  build(params: IllParams, context: IllContext): (Uint8Array | null)[];
}

/** (S108) What the grazing handover does with a hook's value: fade it to the hook's identity, or keep it. */
export type IllGrazeMode = "fade" | "keep";

export interface IllFeature {
  /** Lower-case letters: the prefix of its stored keys and, by convention, of its GLSL names (illLanes..., uniform illLanesWidth). */
  id: string;
  label: string;
  about: string;
  controls: readonly IllControl[];
  /**
   * GLSL at global scope, put into BOTH the march's fragment shader and the points' vertex shader (FluxPoints): uniform
   * declarations and functions. It may use only its own uniforms, `rHi` (the grid's outer radius, kpc), `cloudExt` (each
   * channel's optical depth per magnitude of A_V) and index.ts's `illMap` (the shared map). It declares NO sampler: the
   * march has no texture unit to spare (16 at most, 15 the pinned march's own) - a texture over the disc goes into the
   * shared map through `map`. No texture derivative functions (the points read it in a vertex shader).
   */
  glsl?: string;
  /**
   * GLSL at global scope put only where the randomness layer's include is (noise.glsl.ts: the march's fragment and
   * FluxPoints' vertex shader), after `glsl`: it may call the include's functions (layerGasMap, layerGasSum...) and read
   * its uniforms. Not in other layers' shaders (runtime.glsl). The same rules as `glsl` (no sampler, no derivative).
   */
  noiseGlsl?: string;
  hooks?: IllHooks;
  /**
   * (S108, the grazing handover; index.ts GRAZE_DEFAULT) per hook, what the registry's composition does with this
   * feature's value as a ray (or a point's sight line) turns from the disc's axis toward the plane: "fade" takes it
   * smoothly to the hook's identity (1, or no added depth, or the depth / gas value unchanged) as the grazing weight
   * illGraze goes from 1 to 0, "keep" leaves it whole. Absent: the hook kind's default.
   */
  graze?: Partial<Record<keyof IllHooks, IllGrazeMode>>;
  /** Its channels of the shared map and their builder (see IllMapBuilder). */
  map?: IllMapBuilder;
  /**
   * The values of the uniforms its `glsl` declares, from its parameters and the context. Called at every change of
   * either; a texture it builds it must cache itself (memoOn below), the same object returned while nothing changed.
   * A number, a number[] (vec2/3/4), a three.js Texture/Vector, or null for a sampler not yet built.
   */
  uniforms?: (params: IllParams, context: IllContext) => Record<string, unknown>;
  /** /api/arrays names it needs (fetched once for all features, in IllContext.frame). */
  arrays?: readonly string[];
  /** A drawing of its own in the Galaxy view's canvas, under the illustrative look only. */
  layer?: ComponentType<IllLayerProps>;
  /** True where the feature's own drawing replaces the field mode's default HII knots (they are then not drawn). */
  replacesKnots?: (params: IllParams) => boolean;
}

/**
 * The last value computed from the same inputs, compared by identity: for a feature's texture, built once per frame of
 * arrays (and per parameter that shapes it) and not on every slider move.
 *
 * (S107) A `name` (unique, "<feature>.<what>") lets the map worker build it off the main thread: the worker runs the
 * same builders (illMapJob.ts), hears each named memo's build (observeMemoBuilds) and sends it back, and the main
 * thread puts the value in this cache under the same inputs (seedMemo) - so the main thread's own synchronous call then
 * finds it and builds nothing. A name changes nothing else: on a miss the main thread still builds, as before.
 */
export function memoOn<T>(build: (...inputs: unknown[]) => T, name?: string): (...inputs: unknown[]) => T {
  let last: { inputs: unknown[]; value: T } | null = null;
  MEMOS.add({ release: () => (last = null) });
  if (name) NAMED.set(name, { seed: (inputs, value) => (last = { inputs, value: value as T }), held: () => last });
  return (...inputs: unknown[]) => {
    if (last && last.inputs.length === inputs.length && last.inputs.every((v, i) => Object.is(v, inputs[i]))) return last.value;
    // A probe (wouldBuild) asks whether anything would be built, and builds nothing.
    if (probing > 0) throw MISS;
    const value = build(...inputs);
    last = { inputs, value };
    if (name && observer) observer(name, inputs, value);
    return value;
  };
}

/** The named memos (S107): each one's seeding and its last inputs and value. The last definition of a name holds it. */
const NAMED = new Map<string, { seed(inputs: unknown[], value: unknown): void; held(): { inputs: unknown[]; value: unknown } | null }>();
let observer: ((name: string, inputs: unknown[], value: unknown) => void) | null = null;

/** (S107) Hears every named memo's build (the map worker's job) until the returned function is called. */
export function observeMemoBuilds(listener: (name: string, inputs: unknown[], value: unknown) => void): () => void {
  observer = listener;
  return () => {
    if (observer === listener) observer = null;
  };
}

/** (S107) Puts `value` in the named memo's cache under `inputs` (built elsewhere, the same way); false for no such memo. */
export function seedMemo(name: string, inputs: unknown[], value: unknown): boolean {
  const m = NAMED.get(name);
  if (!m) return false;
  m.seed(inputs, value);
  return true;
}

/** (S107) The named memo's last inputs and value, or null (a test's and the map client's read). */
export const memoHeld = (name: string): { inputs: unknown[]; value: unknown } | null => NAMED.get(name)?.held() ?? null;

/** A clock in ms (performance.now where there is one; 0 elsewhere). */
export const illNow = (): number => (typeof performance !== "undefined" ? performance.now() : 0);

/**
 * (S107) A stage's time since `started` as a browser performance measure named `ill <name>` (the slider probe,
 * e2e/ill/sliders.probe.ts, reads them with performance.getEntriesByType("measure")); only in a page, and only a stage of
 * a millisecond or more. Returns the ms. Nothing drawn reads it.
 */
export function illMeasure(name: string, started: number): number {
  const ms = illNow() - started;
  if (ms >= 1 && typeof window !== "undefined" && typeof performance !== "undefined" && typeof performance.measure === "function") {
    try {
      performance.measure(`ill ${name}`, { start: started, duration: ms });
    } catch {
      // a measure is a diagnostic only
    }
  }
  return ms;
}

/** Every memoOn's cache (S105 fix R5): released together when the look leaves illustrative. */
const MEMOS = new Set<{ release(): void }>();
let probing = 0;
const MISS: unique symbol = Symbol("memoOn: would build");

/** Drops every memoOn's last value (the features' cached planes and maps): the next call builds afresh. */
export function releaseMemos(): void {
  for (const m of MEMOS) m.release();
}

/**
 * Whether `run` would build anything through a memoOn whose last inputs differ (S105 fix R1): it runs with every memoOn
 * answering from its cache, and the first one that would have to build stops it. Nothing is built or cached.
 */
export function wouldBuild(run: () => void): boolean {
  probing += 1;
  try {
    run();
    return false;
  } catch (e) {
    if (e === MISS) return true;
    throw e;
  } finally {
    probing -= 1;
  }
}
