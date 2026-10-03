// The region regime (BUILD_II V3, S40): below the stars handover the view asks the model for the cell
// hierarchy's level that fits it, and synthesises each cloud's interior from the published vector
// (RENDER_PHYSICS §5a): mass and size for the mean density, the log-normal width σ_s for the structure,
// the source offset for the cavity and the pillars, the gradient for the tilt — all seeded by the cloud's
// cell-and-index path, so the same cloud is the same at every approach and at every level (§5c, D181).
// Nothing here is physics the model does not publish: the noise is a construction that realises the
// published one-point distribution. Since S55 (D214 §5; rule D5 as amended) its three parameters - the octave
// count, the lacunarity and the gain - are the model's too, read from `/api/clouds`' header (`cloud_interior`)
// with the census, and with the randomness layer off (the header's `layer`) the interior is smooth (region.test.ts).

/**
 * The hierarchy level a view `across` kpc wide asks for: level 0 down to the stars handover (4 kpc),
 * then one level per factor four of width, so a level-k cell (a level-0 cell is ~1.6 kpc × 0.2 rad at
 * the Sun's radius, 2^k finer per side) is never more than about half the view. The steps are the
 * hierarchy's own factor, not a display choice; the anchor is REGIME_KPC.stars (regimes.ts).
 */
export const LEVEL_KPC: readonly number[] = [4, 1, 0.25, 0.0625];
export const MAX_LEVEL = 3;

export function levelFor(across: number): number {
  let level = 0;
  for (let k = 0; k < LEVEL_KPC.length; k += 1) if (across < LEVEL_KPC[k]) level = k + 1;
  return Math.min(level, MAX_LEVEL);
}

/**
 * A 32-bit integer hash of a lattice point and a seed (the cloud's cell and index). The same hash runs
 * in the shader (RegionVolume.tsx), line for line in integer arithmetic, so the CPU and the GPU agree
 * on every sample: the vitest asserts the CPU side's distribution, the shader draws it.
 */
export function hash3(x: number, y: number, z: number, seed: number): number {
  // Math.imul keeps every product in 32 bits, as the shader's uint arithmetic does: a float64 product of a
  // large seed loses its low bits before `| 0`, and the two sides would disagree.
  let h = (Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) + Math.imul(z | 0, 2147483647) + Math.imul(seed | 0, 1597334677)) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296; // [0, 1)
}

/** Value noise on the unit lattice: trilinear between the eight corners' hashes, smoothed. */
export function valueNoise(x: number, y: number, z: number, seed: number): number {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  const fx = x - ix, fy = y - iy, fz = z - iz;
  const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy), sz = fz * fz * (3 - 2 * fz);
  const c = (dx: number, dy: number, dz: number) => hash3(ix + dx, iy + dy, iz + dz, seed);
  const x00 = c(0, 0, 0) + (c(1, 0, 0) - c(0, 0, 0)) * sx;
  const x10 = c(0, 1, 0) + (c(1, 1, 0) - c(0, 1, 0)) * sx;
  const x01 = c(0, 0, 1) + (c(1, 0, 1) - c(0, 0, 1)) * sx;
  const x11 = c(0, 1, 1) + (c(1, 1, 1) - c(0, 1, 1)) * sx;
  const y0 = x00 + (x10 - x00) * sy;
  const y1 = x01 + (x11 - x01) * sy;
  return y0 + (y1 - y0) * sz; // [0, 1)
}

/**
 * The cloud interior's noise as the model publishes it (S55, D214 §5; rule D5 as amended): how many octaves of
 * the value noise are summed, the ratio of one octave's frequency to the last one's, and of its amplitude.
 * **The viewer holds none of the three**: they are constants of the model - parameters of a synthetic function,
 * the same with the layer on and off, and so no stage's scalars (gate G1's ruling) - and `/api/clouds` carries
 * them in its header under `cloud_interior`, with the census they belong to. The interior is evaluated with what
 * arrived, here and in the shader alike (`regionFragment`).
 */
export interface Interior {
  octaves: number;
  lacunarity: number;
  gain: number;
}

/** The key of `/api/clouds`' header that carries the three: `{"octaves": 4, "lacunarity": 2.0, "gain": 0.5}`. */
export const INTERIOR_KEY = "cloud_interior";

/**
 * The published parameters, read from a clouds header's `cloud_interior`; null where the header carries no
 * usable set (an API that publishes none): a whole number of octaves, at least one, and a positive finite
 * lacunarity and gain. Nothing is filled in for a number that is not there, and no other place in the header is
 * looked in: the three stood among `scalars` for a few commits of S55, and that shape is gone.
 */
export function interiorOf(header: unknown): Interior | null {
  const carried = (header as Record<string, unknown> | null | undefined)?.[INTERIOR_KEY];
  if (typeof carried !== "object" || carried === null || Array.isArray(carried)) return null;
  const { octaves, lacunarity, gain } = carried as Record<string, unknown>;
  const positive = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v) && v > 0;
  if (!positive(octaves) || !Number.isInteger(octaves) || !positive(lacunarity) || !positive(gain)) return null;
  return { octaves, lacunarity, gain };
}

/** A single octave of smoothed value noise, uniform corners: its standard deviation, measured (region.test.ts). */
export const OCTAVE_SIGMA = 0.1794;

/**
 * The amplitudes' quadrature sum, derived from the published count and gain: were the octaves independent, the
 * sum's spread would be OCTAVE_SIGMA × this (0.2067 for four octaves at a gain of a half).
 */
export function octaveNorm(interior: Interior): number {
  let sum = 0;
  let w = 1;
  for (let k = 0; k < interior.octaves; k += 1) {
    sum += w * w;
    w *= interior.gain;
  }
  return Math.sqrt(sum);
}

/**
 * The summed octaves' standard deviation, **a measurement and not a parameter**: 0.2088 on 64 000 points
 * (region.test.ts), 1% above the independent-octave figure because the octaves share lattice corners. The field
 * is divided by it, so its variance is 1 by measurement rather than by assumption. The measurement was made for
 * one set of parameters, recorded beside it: `measuredFor` is what the number is true of, never what the
 * interior is evaluated with. For any other published set the correction over `octaveNorm` is not known, and the
 * interior is not drawn (`interiorNoise`) - the measured number is not stretched to parameters it was not
 * measured for, and no quadrature of the viewer's own stands in for the measurement.
 */
export const FIELD_SIGMA_MEASURED = { sigma: 0.2088, measuredFor: { octaves: 4, lacunarity: 2, gain: 0.5 } } as const;

/** The published function ready to evaluate: its parameters and the standard deviation its sum is divided by. */
export interface InteriorNoise extends Interior {
  sigma: number;
}

/**
 * The noise for a published parameter set, or null where the viewer cannot normalise it: no set published, or a
 * set other than the one the field's standard deviation was measured for.
 */
export function interiorNoise(published: Interior | null): InteriorNoise | null {
  if (!published) return null;
  const { sigma, measuredFor } = FIELD_SIGMA_MEASURED;
  const same = published.octaves === measuredFor.octaves && published.lacunarity === measuredFor.lacunarity && published.gain === measuredFor.gain;
  return same ? { ...published, sigma } : null;
}

/**
 * How a census's clouds are drawn inside: with the published noise, or smooth - and, where smooth is not what
 * was asked for, why, in words for the page.
 * - **The layer off** (the header's own `layer`): the physics alone. The interior is the layer's, so it is smooth
 *   and nothing is to be said.
 * - No parameters published, or a set the normaliser was not measured for: smooth, and said.
 * A smooth cloud keeps its mass, its radius and its mean column: the density ratio is 1 where the noise's
 * log-normal factor has mean 1.
 */
export function cloudInterior(layerOff: boolean, header: unknown): { noise: InteriorNoise | null; note: string | null } {
  if (layerOff) return { noise: null, note: null };
  const published = interiorOf(header);
  if (!published) {
    return { noise: null, note: "cloud interiors are drawn smooth: this API publishes no cloud-interior noise (/api/clouds' header carries no cloud_interior), and the viewer holds none of its own" };
  }
  const noise = interiorNoise(published);
  if (noise) return { noise, note: null };
  const { measuredFor: m } = FIELD_SIGMA_MEASURED;
  return {
    noise: null,
    note:
      `cloud interiors are drawn smooth: the model publishes a noise of ${published.octaves} octaves, lacunarity ${published.lacunarity}, gain ${published.gain}, ` +
      `and the viewer's normaliser was measured for ${m.octaves}, ${m.lacunarity}, ${m.gain}`,
  };
}

/**
 * A field g(x) of zero mean and unit variance built from the octaves — approximately Gaussian, being a
 * sum of many smoothed uniforms — read at a point in the cloud's own frame (units of its radius). The octaves,
 * their frequencies' ratio and their amplitudes' ratio are the published ones.
 */
export function unitField(x: number, y: number, z: number, seed: number, noise: InteriorNoise): number {
  let sum = 0;
  let f = 1;
  let w = 1;
  for (let k = 0; k < noise.octaves; k += 1) {
    sum += (valueNoise(x * f + 17.3 * k, y * f + 31.7 * k, z * f + 47.1 * k, seed + 1013 * k) - 0.5) * w;
    f *= noise.lacunarity;
    w *= noise.gain;
  }
  return sum / noise.sigma;
}

/**
 * The cloud's density over its mean at a point: the log-normal the census publishes the width of,
 * ρ/ρ̄ = exp(σ_s g − σ_s²/2), whose mean over the field is 1 (RENDER_PHYSICS §6: the same mechanism
 * that structures the cloud keeps its mean column). The gradient tilts the mean: 1 + G (x · ĝ) over the
 * cloud's radius, clamped so the tilted mean stays positive [inferred: a linear tilt].
 *
 * **Without a noise the interior is smooth** (S55): the log-normal factor is 1, its own mean. With the layer off
 * the model sends no gradient either (the column is 0), so the ratio is 1 everywhere: the cloud's mean density.
 */
export function densityRatio(
  x: number, y: number, z: number, seed: number, sigmaS: number, gradient: number, gradientAngle: number, noise: InteriorNoise | null,
): number {
  const tilt = Math.max(0.05, 1 + Math.min(0.95, Math.abs(gradient)) * (x * Math.cos(gradientAngle) + z * Math.sin(gradientAngle)));
  if (!noise) return tilt;
  const g = unitField(x, y, z, seed, noise);
  return tilt * Math.exp(sigmaS * g - 0.5 * sigmaS * sigmaS);
}

/** How a cloud's rows are keyed: the same (cell, index) path the model names it by (§5a), as one integer seed. */
export function cloudSeed(cell: number, index: number): number {
  return ((cell & 0xffff) << 15) ^ (index & 0x7fff);
}

// --- the objects a region volume draws (RegionVolume.tsx) ---------------------------------------------

/** Unit conversions, not physics: a parsec in cm (IAU 2015, exact) and the Sun's luminosity the model uses. */
export const CM_PER_PC = 3.0856775814913673e18;
export const L_SUN_ERG_S = 3.828e33;
/** erg s⁻¹ cm⁻³ to L☉ pc⁻³: the model publishes emissivity per volume in cgs (§4); the march integrates in pc. */
export const ERG_S_CM3_TO_LSUN_PC3 = CM_PER_PC ** 3 / L_SUN_ERG_S;
/** Magnitudes to optical depth: 2.5 log10 e, a definition. */
export const MAG_PER_TAU = 2.5 / Math.LN10;

/**
 * The most objects one region volume marches, and the share each kind gets — a display budget, stated: every
 * pixel loops over them, so the loop's length is bounded by a number, not by the window (a level-1 window holds
 * hundreds of clouds). The kept ones are the heaviest clouds and the brightest regions and shells.
 */
export const MAX_OBJECTS = 256;
export const BUDGET = { clouds: 128, hii: 64, shells: 64 } as const;
/** Floats per object in the table the shader reads: four RGBA texels. */
export const OBJECT_FLOATS = 16;
export const KIND = { cloud: 0, hii: 1, shell: 2 } as const;

/** Each line's weight per display channel - its transmission through the channel's filter over the white point's
 * response - by the model's line name (S42). */
export type LineWeights = Record<string, readonly [number, number, number]>;
/** The forbidden lines a region carries as ratios to its Hα (`hii_<line>_ratio`, the nebular stage's, S42). */
export const FORBIDDEN_LINES = ["oiii_5007", "nii_6583", "sii_6716", "sii_6731"] as const;
const HALPHA_ONLY: LineWeights = { halpha: [1, 1, 1] };

/**
 * One region's colour per unit Hα: Hα's weight, Hβ's over the region's Balmer decrement, and each forbidden line's
 * times its ratio. A line the region or the filters lack adds nothing (a NaN ratio included).
 */
export function regionLineColour(clusters: Record<string, Col>, i: number, lines: LineWeights): [number, number, number] {
  const out: [number, number, number] = [0, 0, 0];
  const add = (w: readonly [number, number, number] | undefined, share: number) => {
    if (!w || !Number.isFinite(share) || share <= 0) return;
    for (let k = 0; k < 3; k += 1) out[k] += w[k] * share;
  };
  add(lines.halpha, 1);
  add(lines.hbeta, 1 / num(clusters.hii_balmer_decrement, i));
  for (const n of FORBIDDEN_LINES) add(lines[n], num(clusters[`hii_${n}_ratio`], i));
  return out;
}

type Col = ArrayLike<number | bigint>;
const num = (c: Col | undefined, i: number): number => (c ? Number(c[i]) : Number.NaN);

export interface RegionObjects {
  /** OBJECT_FLOATS per object: centre (kpc, scene) and radius; kind, cell, index, σ_s; kind-specific; a cavity. */
  data: Float32Array;
  count: number;
  /** Scene-space bounds of every object's sphere, kpc: the box the march is drawn over. */
  min: [number, number, number];
  max: [number, number, number];
}

function scene(radius: number, azimuth: number, height: number): [number, number, number] {
  return [radius * Math.cos(azimuth), height, -radius * Math.sin(azimuth)];
}

/**
 * The region's clouds, HII regions and bubble shells as the table the shader marches, within the budget.
 * - a cloud: its sphere, its seed path (cell, index), σ_s, its gradient, κ_V per kpc from the census's central
 *   A_V through a uniform sphere (τ over the diameter), and the cavity its cluster's Strömgren sphere carves;
 * - an HII region: the Strömgren sphere at its cluster, its Hα emissivity per volume in L☉ pc⁻³, and its colour per
 *   unit Hα from all its lines through the filters (`regionLineColour`, S42);
 * - a shell: the bubble's sphere, its shell emissivity in L☉ pc⁻³, its thickness.
 * Lengths from the routes are in pc except positions (kpc); a row with a non-finite size is skipped.
 */
export function packObjects(
  clouds: Record<string, Col>,
  clusters: Record<string, Col>,
  extinctionV: number,
  budget: { clouds: number; hii: number; shells: number } = BUDGET,
  remnants: Record<string, Col> = {},
  lines: LineWeights = HALPHA_ONLY,
): RegionObjects {
  type Obj = { weight: number; row: number[] };
  const pick = (list: Obj[], n: number) => list.sort((a, b) => b.weight - a.weight).slice(0, n);

  // Clusters by name, for the cavity a cloud's cluster carves.
  const clusterAt = new Map<string, number>();
  const nClusters = clusters.cluster_radius?.length ?? 0;
  for (let i = 0; i < nClusters; i += 1) clusterAt.set(`${num(clusters.cell, i)}:${num(clusters.index, i)}`, i);

  const cloudList: Obj[] = [];
  const nClouds = clouds.cloud_radius?.length ?? 0;
  const tauCentre = extinctionV / MAG_PER_TAU;
  for (let i = 0; i < nClouds; i += 1) {
    const sizePc = num(clouds.cloud_size, i);
    if (!(sizePc > 0) || !Number.isFinite(sizePc)) continue;
    const [x, y, z] = scene(num(clouds.cloud_radius, i), num(clouds.cloud_azimuth, i), num(clouds.cloud_height, i));
    const r = sizePc / 1000;
    let cavity = [0, 0, 0, 0];
    const host = num(clouds.cloud_cluster_index, i);
    if (host >= 0) {
      const j = clusterAt.get(`${num(clouds.cell, i)}:${host}`);
      if (j !== undefined) {
        const rs = num(clusters.hii_stromgren_radius, j) / 1000;
        if (rs > 0) cavity = [...scene(num(clusters.cluster_radius, j), num(clusters.cluster_azimuth, j), num(clusters.cluster_height, j)), rs];
      }
    }
    cloudList.push({
      weight: num(clouds.cloud_mass, i),
      row: [x, y, z, r, KIND.cloud, num(clouds.cell, i), num(clouds.index, i), num(clouds.cloud_density_pdf_width, i),
        num(clouds.cloud_density_gradient, i) || 0, num(clouds.cloud_gradient_angle, i) || 0, tauCentre / (2 * r), 0, ...cavity],
    });
  }

  const hiiList: Obj[] = [];
  const shellList: Obj[] = [];
  for (let i = 0; i < nClusters; i += 1) {
    const [x, y, z] = scene(num(clusters.cluster_radius, i), num(clusters.cluster_azimuth, i), num(clusters.cluster_height, i));
    const rs = num(clusters.hii_stromgren_radius, i) / 1000;
    const eps = num(clusters.hii_halpha_emissivity, i) * ERG_S_CM3_TO_LSUN_PC3;
    if (rs > 0 && Number.isFinite(eps) && eps > 0) {
      const colour = regionLineColour(clusters, i, lines);
      hiiList.push({ weight: eps * rs ** 3, row: [x, y, z, rs, KIND.hii, num(clusters.cell, i), num(clusters.index, i), 0, eps, ...colour, 0, 0, 0, 0] });
    }
    const rb = num(clusters.bubble_radius, i) / 1000;
    const thick = num(clusters.bubble_shell_thickness, i) / 1000;
    const epsShell = num(clusters.bubble_shell_emissivity, i) * ERG_S_CM3_TO_LSUN_PC3;
    if (rb > 0 && thick > 0 && Number.isFinite(epsShell) && epsShell > 0) {
      const shellVolume = rb ** 3 - Math.max(0, rb - thick) ** 3;
      shellList.push({ weight: epsShell * shellVolume, row: [x, y, z, rb, KIND.shell, num(clusters.cell, i), num(clusters.index, i), 0, epsShell, Math.min(thick, rb), 0, 0, 0, 0, 0, 0] });
    }
  }

  // Supernova remnants: shells too, competing with the bubbles' for the shell budget by the light they carry.
  const nRemnants = remnants.remnant_radius?.length ?? 0;
  for (let i = 0; i < nRemnants; i += 1) {
    const [x, y, z] = scene(num(remnants.remnant_radius, i), num(remnants.remnant_azimuth, i), num(remnants.remnant_height, i));
    const rr = num(remnants.remnant_size, i) / 1000;
    const thick = num(remnants.remnant_shell_thickness, i) / 1000;
    const epsShell = num(remnants.remnant_shell_emissivity, i) * ERG_S_CM3_TO_LSUN_PC3;
    if (rr > 0 && thick > 0 && Number.isFinite(epsShell) && epsShell > 0) {
      const shellVolume = rr ** 3 - Math.max(0, rr - thick) ** 3;
      shellList.push({ weight: epsShell * shellVolume, row: [x, y, z, rr, KIND.shell, num(remnants.cell, i), num(remnants.index, i), 0, epsShell, Math.min(thick, rr), 0, 0, 0, 0, 0, 0] });
    }
  }

  const kept = [...pick(cloudList, budget.clouds), ...pick(hiiList, budget.hii), ...pick(shellList, budget.shells)].slice(0, MAX_OBJECTS);
  const data = new Float32Array(MAX_OBJECTS * OBJECT_FLOATS);
  const min: [number, number, number] = [Infinity, Infinity, Infinity];
  const max: [number, number, number] = [-Infinity, -Infinity, -Infinity];
  kept.forEach((o, k) => {
    data.set(o.row, k * OBJECT_FLOATS);
    for (let a = 0; a < 3; a += 1) {
      min[a] = Math.min(min[a], o.row[a] - o.row[3]);
      max[a] = Math.max(max[a], o.row[a] + o.row[3]);
    }
  });
  return { data, count: kept.length, min, max };
}

/** The table reordered nearest-first from `eye`, so the march composites front to back (overlaps approximate). */
export function sortedFrom(objects: RegionObjects, eye: readonly [number, number, number], out: Float32Array): Float32Array {
  const order = Array.from({ length: objects.count }, (_, k) => k);
  const dist = order.map((k) => {
    const o = k * OBJECT_FLOATS;
    return Math.hypot(objects.data[o] - eye[0], objects.data[o + 1] - eye[1], objects.data[o + 2] - eye[2]) - objects.data[o + 3];
  });
  order.sort((a, b) => dist[a] - dist[b]);
  order.forEach((k, slot) => out.set(objects.data.subarray(k * OBJECT_FLOATS, (k + 1) * OBJECT_FLOATS), slot * OBJECT_FLOATS));
  return out;
}

// --- the march's fragment shader ---------------------------------------------------------------------------

/** Samples of a cloud's density along each chord through it. */
export const CLOUD_SAMPLES = 4;

/** A number as a GLSL float literal: a whole number keeps its point (`2` is an int there, `2.0` a float). */
export const glslFloat = (v: number): string => (Number.isInteger(v) ? v.toFixed(1) : String(v));

const FRAGMENT_HEAD = /* glsl */ `
  precision highp float;
  precision highp int;
  uniform sampler2D objects;
  uniform int count;
  uniform vec3 lineWeight;
  uniform vec3 extRatio;
  uniform float gain;
  uniform float weight;
  uniform int mode;
  varying vec3 vWorld;

  float hash01(int x, int y, int z, int seed) {
    uint h = uint(x) * 374761393u + uint(y) * 668265263u + uint(z) * 2147483647u + uint(seed) * 1597334677u;
    h = (h ^ (h >> 13u)) * 1274126177u;
    h = h ^ (h >> 16u);
    return float(h) / 4294967296.0;
  }
  float valueNoise(vec3 p, int seed) {
    vec3 i = floor(p);
    vec3 f = p - i;
    vec3 s = f * f * (3.0 - 2.0 * f);
    int ix = int(i.x), iy = int(i.y), iz = int(i.z);
    float c000 = hash01(ix, iy, iz, seed), c100 = hash01(ix + 1, iy, iz, seed);
    float c010 = hash01(ix, iy + 1, iz, seed), c110 = hash01(ix + 1, iy + 1, iz, seed);
    float c001 = hash01(ix, iy, iz + 1, seed), c101 = hash01(ix + 1, iy, iz + 1, seed);
    float c011 = hash01(ix, iy + 1, iz + 1, seed), c111 = hash01(ix + 1, iy + 1, iz + 1, seed);
    float x00 = c000 + (c100 - c000) * s.x;
    float x10 = c010 + (c110 - c010) * s.x;
    float x01 = c001 + (c101 - c001) * s.x;
    float x11 = c011 + (c111 - c011) * s.x;
    float y0 = x00 + (x10 - x00) * s.y;
    float y1 = x01 + (x11 - x01) * s.y;
    return y0 + (y1 - y0) * s.z;
  }
`;

/** `unitField` and `densityRatio` with the published noise: region.ts's own, line for line. */
const fragmentNoisy = (noise: InteriorNoise) => /* glsl */ `  float unitField(vec3 p, int seed) {
    float sum = 0.0;
    float f = 1.0;
    float w = 1.0;
    for (int k = 0; k < ${noise.octaves}; k++) {
      vec3 q = p * f + vec3(17.3, 31.7, 47.1) * float(k);
      sum += (valueNoise(q, seed + 1013 * k) - 0.5) * w;
      f *= ${glslFloat(noise.lacunarity)};
      w *= ${glslFloat(noise.gain)};
    }
    return sum / ${noise.sigma.toFixed(6)};
  }
  float densityRatio(vec3 p, int seed, float sigmaS, float gradient, float angle) {
    float g = unitField(p, seed);
    float tilt = max(0.05, 1.0 + min(0.95, abs(gradient)) * (p.x * cos(angle) + p.z * sin(angle)));
    return tilt * exp(sigmaS * g - 0.5 * sigmaS * sigmaS);
  }
`;

/** `densityRatio` without a noise: the tilt alone, the log-normal factor at its mean, 1. */
const FRAGMENT_SMOOTH = /* glsl */ `  float densityRatio(vec3 p, int seed, float sigmaS, float gradient, float angle) {
    return max(0.05, 1.0 + min(0.95, abs(gradient)) * (p.x * cos(angle) + p.z * sin(angle)));
  }
`;

const fragmentTail = () => /* glsl */ `
  vec4 obj(int i, int row) { return texelFetch(objects, ivec2(row, i), 0); }
  bool sphere(vec3 o, vec3 d, vec3 c, float r, out float t0, out float t1) {
    vec3 oc = o - c;
    float b = dot(oc, d);
    float h = b * b - (dot(oc, oc) - r * r);
    if (h < 0.0) { t0 = 0.0; t1 = 0.0; return false; }
    h = sqrt(h);
    t0 = max(-b - h, 0.0);
    t1 = -b + h;
    return t1 > t0;
  }

  void main() {
    vec3 origin = cameraPosition;
    vec3 dir = normalize(vWorld - cameraPosition);
    vec3 light = vec3(0.0);
    vec3 trans = vec3(1.0);
    for (int i = 0; i < ${MAX_OBJECTS}; i++) {
      if (i >= count) break;
      vec4 a = obj(i, 0);
      vec4 b = obj(i, 1);
      vec4 c = obj(i, 2);
      vec4 e = obj(i, 3);
      float t0, t1;
      if (!sphere(origin, dir, a.xyz, a.w, t0, t1)) continue;
      int kind = int(b.x + 0.5);
      if (kind == 1) {
        // An HII region: uniform emissivity (L_sun/pc^3) over the chord in pc - brighter toward the limb for free -
        // in its own colour per unit Halpha, every line it carries through the filters (S42).
        light += trans * c.x * (t1 - t0) * 1000.0 * c.yzw;
      } else if (kind == 2) {
        // A shell: the chord through the sphere less the chord through its hollow.
        float i0, i1;
        float inner = sphere(origin, dir, a.xyz, max(a.w - c.y, 0.0), i0, i1) ? i1 - i0 : 0.0;
        light += trans * c.x * ((t1 - t0) - inner) * 1000.0 * lineWeight;
      } else {
        // A cloud: the published mean column made log-normal by its own seeded field; inside its cluster's cavity
        // only the clumps denser than e^sigma survive - the pillars (HANDOFF_S40 R3).
        int seed = ((int(b.y) & 0xffff) << 15) ^ (int(b.z) & 0x7fff);
        float ds = (t1 - t0) / float(${CLOUD_SAMPLES});
        float tau = 0.0;
        for (int k = 0; k < ${CLOUD_SAMPLES}; k++) {
          vec3 p = origin + dir * (t0 + (float(k) + 0.5) * ds);
          float rho = densityRatio((p - a.xyz) / a.w, seed, b.w, c.x, c.y);
          if (e.w > 0.0 && length(p - e.xyz) < e.w && rho < exp(b.w)) rho = 0.0;
          tau += c.z * rho * ds;
        }
        trans *= exp(-tau * extRatio);
      }
    }
    if (mode == 0) gl_FragColor = vec4(light * gain, 1.0);
    else gl_FragColor = vec4(mix(vec3(1.0), trans, weight), 1.0);
  }
`;

/**
 * The region march's fragment shader (RegionVolume.tsx draws with it): this file's hash3 / valueNoise / unitField /
 * densityRatio line for line in 32-bit unsigned arithmetic, so the shader draws the field the vitest measures (the
 * float32 division at the end differs from float64 at 1e-7).
 *
 * **The interior's parameters are written into the source from the published values** (S55; rule D5 as amended):
 * the octave count as the loop's bound, the lacunarity and the gain as the two factors, the measured standard
 * deviation as the divisor. Written, not passed as uniforms, for one reason: at the model's published values the
 * text is, byte for byte, the shader the viewer drew with before the parameters were the model's (region.test.ts
 * pins its hash), so the picture cannot have moved by a bit - a guarantee a uniform, which the compiler may not
 * fold as it folds a literal, would not give. A census with other values gets another program.
 *
 * Without a noise (`null`: the layer off, or a set the viewer cannot normalise) the clouds are smooth: the tilt
 * alone, the published mean column.
 */
export function regionFragment(noise: InteriorNoise | null): string {
  return FRAGMENT_HEAD + (noise ? fragmentNoisy(noise) : FRAGMENT_SMOOTH) + fragmentTail();
}
