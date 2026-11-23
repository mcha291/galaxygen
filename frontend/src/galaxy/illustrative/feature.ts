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
 * builder of their bytes, one plane per channel in `channels`' order, each ILL_MAP.width * ILL_MAP.height bytes laid
 * out as ILL_MAP says, or null for a channel that reads zero. Called at every change of a parameter or the context:
 * the feature caches its planes (memoOn) and returns the same Uint8Array while nothing that shapes them changed - the
 * registry re-composes and re-uploads the map only when some plane's object changes. The march's GLSL reads the
 * channels through `vec4 illMap(vec2 rp)`.
 */
export interface IllMapBuilder {
  channels: readonly number[];
  build(params: IllParams, context: IllContext): (Uint8Array | null)[];
}

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
  hooks?: IllHooks;
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
 */
export function memoOn<T>(build: (...inputs: unknown[]) => T): (...inputs: unknown[]) => T {
  let last: { inputs: unknown[]; value: T } | null = null;
  MEMOS.add({ release: () => (last = null) });
  return (...inputs: unknown[]) => {
    if (last && last.inputs.length === inputs.length && last.inputs.every((v, i) => Object.is(v, inputs[i]))) return last.value;
    // A probe (wouldBuild) asks whether anything would be built, and builds nothing.
    if (probing > 0) throw MISS;
    const value = build(...inputs);
    last = { inputs, value };
    return value;
  };
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
