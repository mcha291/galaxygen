// The field mesh's texels as a job (S81, #208 (b)): what the field volume's mesh is built from - planeTexture's four
// textures and, where the young light is clustered in the march, the stellar layer split into the rest and the three
// clump shares (interface/ages.js clumpedLight, as FieldVolume's fillStars writes them) - asked of a worker
// (meshTexels.worker.ts) so the build leaves the main thread, as the clouds' raster did at S78 (cloudRasterJob.ts).
// The job is planeTexture, agedLight, clumpedLight and starTexels themselves, imported, not copied, so what the worker
// builds is what the main thread would have built, bit for bit (meshTexelsJob.test.ts asserts it). No three.js here.
//
// The request names the render's arrays it reads instead of holding them, so that each array crosses the boundary
// once, copied into a buffer of its own (an array of the decoded answer is a view into the whole answer's buffer,
// which a structured clone would copy entire) and transferred; the answer's textures are transferred back.
import { agedLight, clumpedLight } from "@interface/ages.js";

import type { Axis } from "../preview/axes";
import { planeTexture, starTexels, summed } from "./regimes";

/** One age part as the job reads it (interface/ages.js ageParts): its array, its switch and the weight placing it. */
export interface MeshPart {
  name: string;
  key: string;
  weight: string | null;
}

/** Each age part's switch, 0 off and 1 on (FieldVolume's AgeGains). */
export type MeshGains = Readonly<Record<"young" | "middle" | "old", number>>;

/**
 * Where the stellar layer comes from, as FieldVolume chose it: a render array whole (`stars`, or under the star-first
 * mode's threshold `stars_unresolved`); the age parts' sum at the switches (agedLight); or, clustered in the march, the
 * split (clumpedLight) - `data` the rest's texels and three clump textures the young and kept shares'.
 */
export type MeshStars =
  | { from: "array"; name: string }
  | { from: "aged"; parts: MeshPart[]; gains: MeshGains }
  | { from: "clumped"; parts: MeshPart[]; kept: { arrays: Record<number, string> }; gains: MeshGains };

/** One mesh's texels asked: the grid, the white point, the render's arrays the build reads, and what each is. */
export interface MeshRequest {
  R: Axis;
  phi: Axis;
  white: number[];
  /** The render's arrays by name: only those the build reads (meshArrayNames), each its own buffer once copied. */
  arrays: Record<string, ArrayLike<number>>;
  stars: MeshStars;
  /** The dust layer's height: the name of the render's per-ring array (D206), or one height, or none. */
  dustHeight: string | number | null;
  /** The render's arrays the header names, or null where it names none (FieldVolume's reading of the header). */
  dustPlacement: string | null;
  diffuseShare: string | null;
  unspurred: string | null;
  /** The spurs' ring mean (/api/layer's spurs.share), where the march reads the spurs per sub-step; else null. */
  spurShare: ArrayLike<number> | null;
}

/** The mesh's texels: planeTexture's, with the clump textures' where the stellar layer was split (else null). */
export interface MeshTexels {
  data: Float32Array;
  scatter: Float32Array;
  hii: Float32Array;
  rings: Float32Array;
  clumps: Float32Array[] | null;
  width: number;
  height: number;
  cell: number;
}

/** What the main side posts: the request with the job's number, which the answer carries back. */
export interface MeshMessage {
  id: number;
  request: MeshRequest;
}

/** The worker's answer: the texels (every texture's buffer transferred, not copied) and its own time, ms. */
export interface MeshAnswer {
  id: number;
  texels: MeshTexels;
  ms: number;
}

/** The render's components the stellar-free textures are made from, by the names the route gives them (FieldVolume's). */
const LINE_HII = ["halpha_hii", "lines_hii"] as const;
const LINE_DIG = ["halpha_dig", "lines_dig"] as const;
const DUST = ["dust_extinction", "dust_scattered", "dust_thermal"] as const;

/** Every render array the job reads for this request: the ones it names and the fixed components, each once. */
export function meshArrayNames(request: Omit<MeshRequest, "arrays">): string[] {
  const names = new Set<string>([...LINE_HII, ...LINE_DIG, ...DUST]);
  const { stars } = request;
  if (stars.from === "array") names.add(stars.name);
  else {
    for (const part of stars.parts) {
      names.add(part.name);
      if (part.weight) names.add(part.weight);
    }
    if (stars.from === "clumped") for (const name of Object.values(stars.kept.arrays)) names.add(name);
  }
  for (const name of [request.dustHeight, request.dustPlacement, request.diffuseShare, request.unspurred]) if (typeof name === "string") names.add(name);
  return [...names];
}

/**
 * The job: the mesh's texels as FieldVolume built them on the main thread until S81 - planeTexture over the render's
 * components, its stellar layer the array, the parts' sum (agedLight) or, clustered, none, then fillStars's clustered
 * fill: `data` set from clumpedLight's rest's texels and each clump texture its share's.
 */
export function meshTexels(request: MeshRequest): MeshTexels {
  const { R, phi, white, arrays: a, stars } = request;
  const n = { R: R.n, phi: phi.n, filter: white.length };
  const named = (name: string | null) => (name === null ? null : a[name]);
  const plane = planeTexture({
    R,
    phi,
    stars: stars.from === "array" ? a[stars.name] : stars.from === "aged" ? agedLight(a, stars.parts, stars.gains, n) : null,
    hii: summed(a[LINE_HII[0]], a[LINE_HII[1]]),
    dig: summed(a[LINE_DIG[0]], a[LINE_DIG[1]]),
    extinction: a[DUST[0]],
    scattered: a[DUST[1]],
    thermal: a[DUST[2]],
    dustHeight: typeof request.dustHeight === "string" ? a[request.dustHeight] : request.dustHeight,
    dustPlacement: named(request.dustPlacement),
    diffuseShare: named(request.diffuseShare),
    unspurred: named(request.unspurred),
    spurShare: request.spurShare,
    white,
  });
  let clumps: Float32Array[] | null = null;
  if (stars.from === "clumped") {
    const split = clumpedLight(a, stars.parts, stars.kept, stars.gains, n);
    plane.data.set(starTexels(n.R, n.phi, split.rest, white));
    clumps = split.clumps.map((c: Float64Array) => starTexels(n.R, n.phi, c, white));
  }
  return { ...plane, clumps };
}

/**
 * A request whose arrays are copies, each typed array into a buffer of its own (an array of the decoded answer is a
 * view into the whole answer's buffer), with those buffers to transfer; a plain array is copied as one. Absent names
 * are left out, as the job reads them (undefined).
 */
export function meshRequest(request: Omit<MeshRequest, "arrays">, arrays: Record<string, ArrayLike<number>>): { request: MeshRequest; transfer: ArrayBuffer[] } {
  const copied: Record<string, ArrayLike<number>> = {};
  const transfer: ArrayBuffer[] = [];
  for (const name of meshArrayNames(request)) {
    const column = arrays[name];
    if (!column) continue;
    if (ArrayBuffer.isView(column)) {
      const copy = (column as unknown as Float32Array).slice();
      copied[name] = copy;
      transfer.push(copy.buffer as ArrayBuffer);
    } else copied[name] = Array.from(column);
  }
  const spurShare = request.spurShare ? Array.from(request.spurShare) : null;
  return { request: { ...request, spurShare, arrays: copied }, transfer };
}

/** The buffers of an answer to transfer back: every texture's. */
export function answerTransfer(texels: MeshTexels): ArrayBuffer[] {
  return [texels.data, texels.scatter, texels.hii, texels.rings, ...(texels.clumps ?? [])].map((t) => t.buffer as ArrayBuffer);
}
