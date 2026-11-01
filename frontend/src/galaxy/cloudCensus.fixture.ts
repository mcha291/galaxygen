// A synthetic census for the raster's bit-identity tests (S78: the hoist's, R2, and the worker's, R5). Not a test file
// itself (vitest collects *.test.ts): the census the tests share.
import type { CloudColumns } from "./cloudOpacity";

/** A deterministic census (mulberry32): `n` clouds across and past [rLo, rHi), at every size and shape. */
export function syntheticCensus(n: number, seed: number, rLo: number, rHi: number, f4: boolean): CloudColumns {
  let t = seed >>> 0;
  const rand = () => {
    t = (t + 0x6d2b79f5) >>> 0;
    let x = Math.imul(t ^ (t >>> 15), 1 | t);
    x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
  const make = () => (f4 ? new Float32Array(n) : new Float64Array(n));
  const c = {
    cloud_radius: make(), cloud_azimuth: make(), cloud_size: make(), cloud_dust_extinction_v: make(), cloud_height: make(),
    cloud_axis_ratio: make(), cloud_angle: make(),
  };
  for (let k = 0; k < n; k += 1) {
    const kind = k % 10;
    // radii: most inside, some at the centre, some past either edge
    c.cloud_radius[k] = kind === 0 ? 0.05 + 0.3 * rand() : kind === 1 ? rHi - 0.2 + 0.6 * rand() : rLo + (rHi - rLo) * rand();
    // azimuths: anywhere, and some just either side of phi = 0
    c.cloud_azimuth[k] = kind === 2 ? 2 * Math.PI - 0.01 * rand() : kind === 3 ? 0.01 * rand() : 2 * Math.PI * rand();
    // sizes, pc: from far under a texel to many texels across
    c.cloud_size[k] = kind === 4 ? 2 + 10 * rand() : kind === 5 ? 300 + 600 * rand() : 20 + 150 * rand();
    c.cloud_dust_extinction_v[k] = kind === 6 && rand() < 0.3 ? (rand() < 0.5 ? 0 : Number.NaN) : 0.05 + 3 * rand();
    c.cloud_height[k] = (rand() - 0.5) * 0.2;
    c.cloud_axis_ratio[k] = kind === 7 ? 1 : 1 + 4 * rand();
    c.cloud_angle[k] = (rand() - 0.5) * 2 * Math.PI;
  }
  return c;
}
