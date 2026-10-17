// The surface-brightness gate's two sides (S67, BUILD_III V8; D227 R5; T1). No three.js here: the pure parts, tested.
//
// On screen: each pixel's linear light (the frame as FrameProbe draws it, before bloom and tone) turned back into the
// light it stands for - times the area of sky the pixel covers at the disc's plane, flux.ts pixelArea's form, the one
// the points are deposited by - and summed in rings of galactocentric radius where the pixel's ray meets the plane.
// Divided by the field's gain it is L_sun over the white point per channel, the render's own unit.
// From the render: the stars' published light per ring through each channel over the white point (the march's own
// division, regimes.ts balanced), times the ring's area - what test_render ties to disc_surface_brightness.

/** The render's stars per ring, L_sun over the white point per channel, on the grid's R cells. */
export interface RenderRings {
  /** The rings' edges, kpc: the grid's R cells. */
  edges: number[];
  light: [number, number, number][];
  /** The bulge's light per channel over the white point, L_sun (the header's bulge): not in any ring's. */
  bulge: [number, number, number];
  /**
   * The bulge's light in each ring as the march draws it - a Hernquist sphere of the published scale radius
   * (bulge_scale_radius), projected (hernquistWithin) - so each ring's light on screen can be set against the disc's
   * and the bulge's together. Zero where the render carries no bulge.
   */
  bulgeRings: [number, number, number][];
}

/**
 * A Hernquist sphere's share of its light within projected radius R, scale a (Hernquist 1990, eq. 37 integrated: M_p(<R)
 * / M = s^2 (X(s) - 1) / (1 - s^2), s = R / a, X(s) = sech^-1(s) / sqrt(1 - s^2) below 1 and sec^-1(s) / sqrt(s^2 - 1)
 * above; 1/3 at s = 1, by the limit). The march's bulge, FieldVolume's bulgeScale / (2 pi s (s + a)^3).
 */
export function hernquistWithin(R: number, a: number): number {
  if (!(R > 0) || !(a > 0)) return 0;
  const s = R / a;
  if (Math.abs(s - 1) < 1e-6) return 1 / 3;
  const X = s < 1 ? Math.acosh(1 / s) / Math.sqrt(1 - s * s) : Math.acos(1 / s) / Math.sqrt(s * s - 1);
  return (s * s * (X - 1)) / (1 - s * s);
}

/**
 * The render's stars summed round each ring (rows R, then phi, then filter, as /api/render lays them), over the white
 * point, times each cell's area: R cells [lo + i w, lo + (i + 1) w] kpc, nPhi equal sectors.
 */
export function renderRings(
  R: { lo: number; width: number; n: number },
  nPhi: number,
  stars: ArrayLike<number>,
  white: readonly number[],
  bulge: readonly (number | null)[] | null | undefined,
  bulgeScale = 0,
): RenderRings {
  const nF = white.length;
  const edges: number[] = [];
  for (let i = 0; i <= R.n; i += 1) edges.push(R.lo + i * R.width);
  const light: [number, number, number][] = [];
  for (let i = 0; i < R.n; i += 1) {
    const area = (Math.PI * (edges[i + 1] ** 2 - edges[i] ** 2) * 1e6) / nPhi; // pc^2 per cell
    const ring: [number, number, number] = [0, 0, 0];
    for (let j = 0; j < nPhi; j += 1) {
      for (let k = 0; k < 3 && k < nF; k += 1) {
        const v = Number(stars[(i * nPhi + j) * nF + k]) / white[k];
        if (Number.isFinite(v) && v > 0) ring[k] += v * area;
      }
    }
    light.push(ring);
  }
  const b = [0, 1, 2].map((k) => {
    const v = Number(bulge?.[k]) / white[k];
    return Number.isFinite(v) && v > 0 ? v : 0;
  }) as [number, number, number];
  const bulgeRings = light.map((_, i) => {
    const share = bulgeScale > 0 ? hernquistWithin(edges[i + 1], bulgeScale) - hernquistWithin(edges[i], bulgeScale) : 0;
    return [b[0] * share, b[1] * share, b[2] * share] as [number, number, number];
  });
  return { edges, light, bulge: b, bulgeRings };
}

/**
 * An age part's light per ring (the lead's second pass on R5): the render's (R, filter) part over the white point,
 * placed round each ring by its (R, phi) weight (interface/ages.js agedLight's product), times each cell's area; with
 * no weight, an even ring. Or an (R, phi, filter) array, summed as renderRings does.
 */
export function partRings(
  R: { lo: number; width: number; n: number },
  nPhi: number,
  part: ArrayLike<number>,
  weight: ArrayLike<number> | null,
  white: readonly number[],
): [number, number, number][] {
  const nF = white.length;
  const perCell = part.length === R.n * nPhi * nF;
  const out: [number, number, number][] = [];
  for (let i = 0; i < R.n; i += 1) {
    const r0 = R.lo + i * R.width;
    const area = (Math.PI * ((r0 + R.width) ** 2 - r0 ** 2) * 1e6) / nPhi;
    const ring: [number, number, number] = [0, 0, 0];
    for (let j = 0; j < nPhi; j += 1) {
      const w = perCell ? 1 : weight ? Number(weight[i * nPhi + j]) : 1;
      for (let k = 0; k < 3 && k < nF; k += 1) {
        const v = (Number(perCell ? part[(i * nPhi + j) * nF + k] : part[i * nF + k]) * w) / white[k];
        if (Number.isFinite(v) && v > 0) ring[k] += v * area;
      }
    }
    out.push(ring);
  }
  return out;
}

/**
 * Points summed in rings (the lead's second pass on R5): each point's light per channel and its square, by the ring its
 * galactocentric radius falls in (scene positions, positions.ts toScene: x = R cos phi, z = -R sin phi), and the light
 * of the points within `edgeKpc` of their ring's inner or outer edge - what a sprite of that half-width can carry across.
 */
export function pointRings(
  positions: ArrayLike<number>,
  flux: ArrayLike<number>,
  edges: readonly number[],
  edgeKpc: number,
): { light: [number, number, number][]; square: [number, number, number][]; nearEdge: [number, number, number][]; count: number[] } {
  const n = edges.length - 1;
  const zero = () => Array.from({ length: n }, () => [0, 0, 0] as [number, number, number]);
  const light = zero();
  const square = zero();
  const nearEdge = zero();
  const count = new Array<number>(n).fill(0);
  for (let p = 0; p < flux.length / 3; p += 1) {
    const radius = Math.hypot(Number(positions[3 * p]), Number(positions[3 * p + 2]));
    const i = radiusIndex(radius, edges);
    if (i < 0) continue;
    count[i] += 1;
    const near = radius - edges[i] < edgeKpc || edges[i + 1] - radius < edgeKpc;
    for (let k = 0; k < 3; k += 1) {
      const L = Number(flux[3 * p + k]);
      light[i][k] += L;
      square[i][k] += L * L;
      if (near) nearEdge[i][k] += L;
    }
  }
  return { light, square, nearEdge, count };
}

/** A camera as the probe reads it: the eye, its unit axes (forward into the view), and the lens's tan(fov_y / 2). */
export interface RingCamera {
  eye: readonly [number, number, number];
  forward: readonly [number, number, number];
  right: readonly [number, number, number];
  up: readonly [number, number, number];
  tanHalfY: number;
}

/** Each pixel's ray to the disc's plane (y = 0): the ring it lands in, and the sky's area there, pc^2 (flux.ts pixelArea). */
export interface ScreenRings {
  /** Linear light x area per channel, summed per ring: divide by the gain for L_sun over the white point. */
  rings: [number, number, number][];
  /** Pixels that landed in each ring. */
  pixels: number[];
  /** Light that landed outside every ring or off the plane, the same units. */
  outside: [number, number, number];
}

/**
 * The frame's pixels (RGBA float, rows from the bottom, as readRenderTargetPixels returns them) summed in rings:
 * `edges` kpc of galactocentric radius at the plane. A pixel at (x, y) looks along forward + right u + up v, u and v its
 * centre's offsets over f = height / (2 tan(fov_y / 2)); its ray meets the plane at depth t along forward and distance
 * t |dir|, and the area of sky it covers there is (1000 t / f)^2 t / (t |dir|) pc^2 - the inverse of a point's deposit.
 */
export function screenRings(pixels: ArrayLike<number>, width: number, height: number, cam: RingCamera, edges: readonly number[]): ScreenRings {
  const n = edges.length - 1;
  const rings = Array.from({ length: n }, () => [0, 0, 0] as [number, number, number]);
  const counts = new Array<number>(n).fill(0);
  const outside: [number, number, number] = [0, 0, 0];
  const f = height / (2 * cam.tanHalfY);
  const [ex, ey, ez] = cam.eye;
  for (let y = 0; y < height; y += 1) {
    const v = (y + 0.5 - height / 2) / f;
    for (let x = 0; x < width; x += 1) {
      const p = (y * width + x) * 4;
      const r = pixels[p];
      const g = pixels[p + 1];
      const b = pixels[p + 2];
      if (r === 0 && g === 0 && b === 0) continue;
      const u = (x + 0.5 - width / 2) / f;
      const dx = cam.forward[0] + cam.right[0] * u + cam.up[0] * v;
      const dy = cam.forward[1] + cam.right[1] * u + cam.up[1] * v;
      const dz = cam.forward[2] + cam.right[2] * u + cam.up[2] * v;
      const t = Math.abs(dy) > 1e-12 ? -ey / dy : -1;
      let ring = -1;
      let area = 0;
      if (t > 0) {
        const radius = Math.hypot(ex + t * dx, ez + t * dz);
        const len = Math.hypot(dx, dy, dz);
        const side = (1000 * t) / f;
        area = (side * side) / len;
        ring = radiusIndex(radius, edges);
      }
      const into = ring >= 0 ? rings[ring] : outside;
      // Off the plane (no t) the light is counted outside by its count alone: area 0 would hide it.
      const w = ring >= 0 ? area : area || 1;
      into[0] += r * w;
      into[1] += g * w;
      into[2] += b * w;
      if (ring >= 0) counts[ring] += 1;
    }
  }
  return { rings, pixels: counts, outside };
}

/** The ring [edges[i], edges[i + 1]) holding `radius`, or -1. */
export function radiusIndex(radius: number, edges: readonly number[]): number {
  if (!(radius >= edges[0]) || !(radius < edges[edges.length - 1])) return -1;
  let lo = 0;
  let hi = edges.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (radius >= edges[mid]) lo = mid;
    else hi = mid;
  }
  return lo;
}
