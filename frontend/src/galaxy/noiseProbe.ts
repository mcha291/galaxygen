/**
 * The noise's instrument on the GPU (S66, V7; D226 R9b, rule B1): the GLSL include's functions evaluated at given
 * inputs into an N x 1 float target and read back, so the e2e spec (`e2e/noise.spec.ts`) can hold the GLSL itself -
 * not only its TypeScript twin - to the model's vectors on the machine's own GPU. It draws into its own target with
 * its own camera and touches nothing the viewer shows. `GalaxyView`'s NoiseProbe puts it on
 * `window.__galaxygenNoiseProbe`.
 */

import {
  ClampToEdgeWrapping,
  DataTexture,
  FloatType,
  Mesh,
  NearestFilter,
  OrthographicCamera,
  PlaneGeometry,
  RGBAFormat,
  RGBAIntegerFormat,
  RedFormat,
  Scene,
  ShaderMaterial,
  type Texture,
  UnsignedIntType,
  type WebGLRenderer,
  WebGLRenderTarget,
} from "three";

import type { ClusteringEntry, GasFluctuationEntry, SpursEntry } from "../api";
import {
  gasRingTexels,
  gasWeightTexels,
  noiseScalars,
  prepareClustering,
  prepareGas,
  prepareSpurs,
  spurTexels,
} from "./noise";
import { NOISE_GLSL, NOISE_UNIFORMS } from "./noise.glsl";

/** What the probe evaluates, by the include's function: the inputs each kind reads are listed in PROBE_FRAGMENT. */
export const NOISE_PROBE_KINDS = {
  hash: 0, noise2: 1, noise3: 2, shear: 3, fractal: 4, lognormal: 5, gasSum: 6, gasMap: 7, clusterMaps: 8, spurSum: 9,
} as const;
export type NoiseProbeKind = keyof typeof NOISE_PROBE_KINDS;

/** One point's inputs: up to eight uints (two texels) and twelve floats (three texels: f[0..3], f[4..7], f[8..11]). */
export interface NoiseProbeRow {
  u?: number[];
  f?: number[];
}

/** The fields' entries, as /api/layer carries them (the render header until S73), for the kinds that read tables (gasSum to spurSum). */
export interface NoiseProbeTables {
  gas?: GasFluctuationEntry | null;
  clustering?: ClusteringEntry | null;
  spurs?: SpursEntry | null;
  /** The gas tables' twist as given (false) or reduced modulo 2 pi (the march's, true: the default). */
  reduceTwist?: boolean;
}

const PROBE_VERTEX = /* glsl */ `
void main() { gl_Position = vec4(position.xy, 0.0, 1.0); }
`;

/**
 * The probe's fragment: pixel i reads its inputs from two uint texels (2i, 2i + 1) and three float texels (3i ..
 * 3i + 2) and writes the function's value(s):
 * hash (u: seed, octave, ix, iy | iz, 3-D?) -> (h >> 16, h & 0xffff, lattice value); noise2 (u: seed, octave; f: x, y);
 * noise3 (f: x, y, z); shear (f: x, y, strain); fractal (u: seed, octaves, ndim; f: x, y, z | base, lacunarity, gain,
 * top | norm); lognormal (as fractal, 2-D; f: ... | norm, sigma, normaliser) -> (map, g); gasSum (u: ring; f: X, Y) ->
 * g; gasMap (f: x, y) -> (map, g); clusterMaps (f: x, y) -> (m1, m2, m3); spurSum (f: R, phi) -> S.
 */
export const PROBE_FRAGMENT = /* glsl */ `
uniform highp usampler2D uProbeInts;
uniform highp sampler2D uProbeFloats;
uniform int uProbeKind;
uniform int uSpurCount;
${NOISE_UNIFORMS}
${NOISE_GLSL}
void main() {
  int i = int(gl_FragCoord.x);
  uvec4 u0 = texelFetch(uProbeInts, ivec2(2 * i, 0), 0);
  uvec4 u1 = texelFetch(uProbeInts, ivec2(2 * i + 1, 0), 0);
  vec4 f0 = texelFetch(uProbeFloats, ivec2(3 * i, 0), 0);
  vec4 f1 = texelFetch(uProbeFloats, ivec2(3 * i + 1, 0), 0);
  vec4 f2 = texelFetch(uProbeFloats, ivec2(3 * i + 2, 0), 0);
  vec4 result = vec4(0.0);
  if (uProbeKind == 0) {
    uint h = u1.y == 1u ? layerHash(u0.x, u0.y, u0.z, u0.w, u1.x) : layerHash(u0.x, u0.y, u0.z, u0.w);
    result = vec4(float(h >> 16u), float(h & 0xffffu), layerValue(h), 0.0);
  } else if (uProbeKind == 1) {
    result.x = layerNoise2(u0.x, f0.x, f0.y, u0.y);
  } else if (uProbeKind == 2) {
    result.x = layerNoise3(u0.x, f0.x, f0.y, f0.z, u0.y);
  } else if (uProbeKind == 3) {
    float xs = f0.x - f0.z * f0.y;
    result.x = layerNoise2(u0.x, xs, f0.y, u0.y);
  } else if (uProbeKind == 4) {
    result.x = layerFractal(u0.x, f0.xyz, int(u0.z), int(u0.y), f1.x, f1.y, f1.z, f1.w, f2.x);
  } else if (uProbeKind == 5) {
    float g = layerFractal(u0.x, f0.xyz, 2, int(u0.y), f1.x, f1.y, f1.z, f1.w, f2.x);
    result.xy = vec2(layerLognormal(g, f2.y, f2.z), g);
  } else if (uProbeKind == 6) {
    result.x = layerGasSum(f0.xy, int(u0.x));
  } else if (uProbeKind == 7) {
    int ring = layerGasRing(length(f0.xy));
    result.xy = vec2(layerGasMap(f0.xy), layerGasSum(layerGasRead(f0.xy, ring), ring));
  } else if (uProbeKind == 8) {
    result.xyz = layerClusterMaps(f0.xy);
  } else if (uProbeKind == 9) {
    result.x = layerSpurSum(f0.x, f0.y, uSpurCount);
  }
  gl_FragColor = result;
}
`;

function dataTexture(data: Float32Array | Uint32Array, width: number, height: number, integer = false, red = false): DataTexture {
  const t = integer
    ? new DataTexture(data, width, height, RGBAIntegerFormat, UnsignedIntType)
    : new DataTexture(data, width, height, red ? RedFormat : RGBAFormat, FloatType);
  if (integer) t.internalFormat = "RGBA32UI";
  t.minFilter = NearestFilter;
  t.magFilter = NearestFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = ClampToEdgeWrapping;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
}

/** A 1 x 1 placeholder for a table a kind does not read. */
const empty = () => dataTexture(new Float32Array(4), 1, 1);

/**
 * Evaluate the include's `kind` at each row's inputs on `gl`'s GPU: N x 4 floats, row-major, in the order of `rows`.
 * Everything made here is disposed before it returns.
 */
export function runNoiseProbe(gl: WebGLRenderer, kind: NoiseProbeKind, rows: NoiseProbeRow[], tables: NoiseProbeTables = {}): Float32Array {
  const n = rows.length;
  if (n === 0) return new Float32Array(0);
  const ints = new Uint32Array(n * 8);
  const floats = new Float32Array(n * 12);
  rows.forEach((row, i) => {
    (row.u ?? []).forEach((v, k) => (ints[i * 8 + k] = v >>> 0));
    (row.f ?? []).forEach((v, k) => (floats[i * 12 + k] = v));
  });
  const gas = prepareGas(tables.gas ?? null, tables.reduceTwist ?? true);
  const clustering = prepareClustering(tables.clustering ?? null);
  const spurs = prepareSpurs(tables.spurs ?? null);
  const made: Texture[] = [dataTexture(ints, 2 * n, 1, true), dataTexture(floats, 3 * n, 1)];
  const gasRing = gas ? dataTexture(gasRingTexels(gas), 32, 2) : empty();
  const gasWeights = gas ? dataTexture(gasWeightTexels(gas), gas.weights.length / 8, 2) : empty();
  const gasCells = gas ? dataTexture(gas.cells, 32, 32, false, true) : empty();
  const spurTable = spurs ? dataTexture(spurTexels(spurs), Math.max(3, 3 * spurs.count), 1) : empty();
  made.push(gasRing, gasWeights, gasCells, spurTable);
  const uniforms: Record<string, { value: unknown }> = {
    uProbeInts: { value: made[0] }, uProbeFloats: { value: made[1] }, uProbeKind: { value: NOISE_PROBE_KINDS[kind] },
    uSpurCount: { value: spurs ? spurs.count : 0 }, uGasRing: { value: gasRing }, uGasWeights: { value: gasWeights },
    uGasCells: { value: gasCells }, uSpurs: { value: spurTable },
    uGasSeed: { value: 0 }, uGasInvScale: { value: 0 }, uGasSense: { value: 0 }, uGasEdge0: { value: 0 },
    uClusterSeed: { value: 0 }, uClusterInvScale: { value: 0 }, uClusterGain: { value: 0 }, uClusterTop: { value: 0 },
    uClusterNorm: { value: 0 }, uClusterSigma: { value: 0 }, uSpurTurn: { value: 0 }, uSpurReach: { value: 0 },
  };
  for (const [name, value] of Object.entries(noiseScalars(gas, clustering, spurs))) uniforms[name] = { value };
  const material = new ShaderMaterial({ vertexShader: PROBE_VERTEX, fragmentShader: PROBE_FRAGMENT, uniforms, depthTest: false, depthWrite: false });
  const geometry = new PlaneGeometry(2, 2);
  const scene = new Scene();
  scene.add(new Mesh(geometry, material));
  const camera = new OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const target = new WebGLRenderTarget(n, 1, { type: FloatType, format: RGBAFormat, depthBuffer: false });
  const before = gl.getRenderTarget();
  const out = new Float32Array(n * 4);
  try {
    gl.setRenderTarget(target);
    gl.render(scene, camera);
    gl.readRenderTargetPixels(target, 0, 0, n, 1, out);
  } finally {
    gl.setRenderTarget(before);
    target.dispose();
    material.dispose();
    geometry.dispose();
    for (const t of made) t.dispose();
  }
  return out;
}
