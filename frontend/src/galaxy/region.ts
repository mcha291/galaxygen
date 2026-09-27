// The region regime (BUILD_II V3, S40): below the stars handover the view asks the model for the cell
// hierarchy's level that fits it, and synthesises each cloud's interior from the published vector
// (RENDER_PHYSICS §5a): mass and size for the mean density, the log-normal width σ_s for the structure,
// the source offset for the cavity and the pillars, the gradient for the tilt — all seeded by the cloud's
// cell-and-index path, so the same cloud is the same at every approach and at every level (§5c, D181).
// Nothing here is physics the model does not publish: the noise is a construction that realises the
// published one-point distribution, and its parameters are stated here and tested (region.test.ts).

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

/** Octaves of the value noise, frequencies 1, 2, 4, 8 per unit, weights 1, 1/2, 1/4, 1/8. */
export const OCTAVES = 4;
/** A single octave of smoothed value noise, uniform corners: its standard deviation, measured (region.test.ts). */
export const OCTAVE_SIGMA = 0.1794;
/** The weights' quadrature sum: were the octaves independent, the sum's spread would be OCTAVE_SIGMA × this (0.2067). */
export const OCTAVE_NORM = Math.sqrt(1 + 1 / 4 + 1 / 16 + 1 / 64);
/**
 * The summed octaves' standard deviation, measured on 64 000 points (region.test.ts): 0.2088, 1% above the
 * independent-octave figure because the octaves share lattice corners. The field is divided by this, so its
 * variance is 1 by measurement rather than by assumption.
 */
export const FIELD_SIGMA = 0.2088;

/**
 * A field g(x) of zero mean and unit variance built from the octaves — approximately Gaussian, being a
 * sum of many smoothed uniforms — read at a point in the cloud's own frame (units of its radius).
 */
export function unitField(x: number, y: number, z: number, seed: number): number {
  let sum = 0;
  let f = 1;
  let w = 1;
  for (let k = 0; k < OCTAVES; k += 1) {
    sum += (valueNoise(x * f + 17.3 * k, y * f + 31.7 * k, z * f + 47.1 * k, seed + 1013 * k) - 0.5) * w;
    f *= 2;
    w *= 0.5;
  }
  return sum / FIELD_SIGMA;
}

/**
 * The cloud's density over its mean at a point: the log-normal the census publishes the width of,
 * ρ/ρ̄ = exp(σ_s g − σ_s²/2), whose mean over the field is 1 (RENDER_PHYSICS §6: the same mechanism
 * that structures the cloud keeps its mean column). The gradient tilts the mean: 1 + G (x · ĝ) over the
 * cloud's radius, clamped so the tilted mean stays positive [inferred: a linear tilt].
 */
export function densityRatio(
  x: number, y: number, z: number, seed: number, sigmaS: number, gradient: number, gradientAngle: number,
): number {
  const g = unitField(x, y, z, seed);
  const tilt = Math.max(0.05, 1 + Math.min(0.95, Math.abs(gradient)) * (x * Math.cos(gradientAngle) + z * Math.sin(gradientAngle)));
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
