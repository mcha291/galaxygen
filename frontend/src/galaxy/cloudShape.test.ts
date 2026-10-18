import { describe, expect, it } from "vitest";

import { SECH2_HWHM_PER_H, cloudRaster, shearEllipse, strainAt, texelArea } from "./cloudOpacity";
import { composeStep } from "./regimes";

// S67, D230: each cloud's deposit in the galaxy-scale raster - R1 its vertical half-extent capped at the clouds' layer's
// half-maximum (the lead's ruling, an amendment of D224 R3), R2 its face-on ellipse along the gas fluctuation field's
// shear (the owner's choice, "Stretch clouds along arms"). Face-on A_V x area is conserved per cloud in both.

const held = (av: Float32Array, w: number, h: number, rLo: number, rHi: number) => {
  const dR = (rHi - rLo) / w, dP = (2 * Math.PI) / h;
  let s = 0;
  for (let i = 0; i < w; i += 1) for (let j = 0; j < h; j += 1) s += av[j * w + i] * texelArea(i, rLo, dR, dP);
  return s;
};

/** One large cloud (300 pc radius, 10 mag) at R = 3 kpc, phi = 1 rad, height 20 pc, on a fine raster. */
const GIANT = { cloud_radius: [3], cloud_azimuth: [1], cloud_size: [300], cloud_dust_extinction_v: [10], cloud_height: [0.02] };
const W = 400, H = 3600, RLO = 2, RHI = 4; // 5 pc rings, ~5 pc sectors at 3 kpc

describe("R1: a cloud's vertical extent capped at the clouds' layer (S67, D230)", () => {
  it("is the sech² layer's half-maximum: 1.7627 h (60.0 pc at h = 34.04 pc)", () => {
    expect(1 / Math.cosh(SECH2_HWHM_PER_H / 2) ** 2).toBeCloseTo(0.5, 12);
    expect(SECH2_HWHM_PER_H * 34.04).toBeCloseTo(60.0, 1);
  });

  it("flattens the slab and moves no A_V: the face-on raster is the same to the bit, the half-thickness at most the cap", () => {
    const free = cloudRaster(GIANT, RLO, RHI, W, H);
    const cap = SECH2_HWHM_PER_H * 0.03404;
    const capped = cloudRaster(GIANT, RLO, RHI, W, H, { verticalCap: cap });
    expect(Array.from(capped.av)).toEqual(Array.from(free.av));
    let maxHalf = 0, maxFree = 0;
    for (let t = 0; t < capped.av.length; t += 1) if (capped.av[t] > 0) {
      maxHalf = Math.max(maxHalf, capped.slab[2 * t + 1]);
      maxFree = Math.max(maxFree, free.slab[2 * t + 1]);
      expect(capped.slab[2 * t]).toBe(free.slab[2 * t]); // the height is the cloud's, untouched
    }
    expect(maxFree).toBeCloseTo(0.3, 6);
    expect(maxHalf).toBeCloseTo(cap, 6);
    // and the march's twin (composeStep) sees the light in front of an opaque cloud at the midplane rise to the layer's
    const h = 0.356;
    const lit = (half: number) => composeStep(50, -50, 100, h, 0, 0, 0.02, half, 100).light / composeStep(50, -50, 100, h, 0, 0).light;
    expect(lit(0.3)).toBeLessThan(0.33);
    expect(lit(cap)).toBeGreaterThan(0.43);
  });
});

describe("R2: a cloud's face-on ellipse along the gas field's shear (S67, D230)", () => {
  it("is the image of a round feature under the field's read: the shear's shape from noise.ts's rotation", () => {
    // The field is read at p rotated by theta(R) = sense (twist + strain ln(R / R_r)) (noise.ts gasReadPosition). Its
    // Jacobian, by finite differences in doubles, maps a small circle of the field to an ellipse in the disc whose
    // shape is (J^T J)^-1: its axis ratio and long axis are shearEllipse's.
    const sense = -1, strain = -1.6, twist = 0.7, Rr = 2.84;
    const read = (x: number, y: number) => {
      const R = Math.hypot(x, y), th = sense * (twist + strain * Math.log(R / Rr));
      return [x * Math.cos(th) + y * Math.sin(th), y * Math.cos(th) - x * Math.sin(th)];
    };
    const R = 3.3, phi = 0.4, x = R * Math.cos(phi), y = R * Math.sin(phi), d = 1e-6;
    const fx = read(x + d, y), bx = read(x - d, y), fy = read(x, y + d), by = read(x, y - d);
    const J = [[(fx[0] - bx[0]) / (2 * d), (fy[0] - by[0]) / (2 * d)], [(fx[1] - bx[1]) / (2 * d), (fy[1] - by[1]) / (2 * d)]];
    // M = J^T J; the ellipse in the disc is {p : p^T M p = 1}: its long axis is M's small eigenvector
    const m00 = J[0][0] ** 2 + J[1][0] ** 2, m01 = J[0][0] * J[0][1] + J[1][0] * J[1][1], m11 = J[0][1] ** 2 + J[1][1] ** 2;
    const tr = m00 + m11, det = m00 * m11 - m01 * m01, disc = Math.sqrt(tr * tr / 4 - det);
    const lmin = tr / 2 - disc, lmax = tr / 2 + disc;
    const ratio = Math.sqrt(lmax / lmin);
    const long = [m01, lmin - m00]; // (M - lmin) v = 0
    const longAngle = Math.atan2(long[1], long[0]);
    const { ratio: q, angle } = shearEllipse(sense * strain, 1);
    expect(q).toBeCloseTo(ratio, 6);
    // the long axis in the disc's (x, y) from shearEllipse's angle in (r-hat, phi-hat), modulo a half turn
    const ours = phi + angle;
    const diff = Math.abs(Math.sin(ours - longAngle));
    expect(diff).toBeLessThan(1e-6);
    // round at the exponent 0 and with no strain; lambda+ ^ e in between
    expect(shearEllipse(1.6, 0).ratio).toBe(1);
    expect(shearEllipse(0, 1).ratio).toBe(1);
    expect(shearEllipse(1.6, 0.5).ratio).toBeCloseTo(Math.sqrt(q), 12);
  });

  it("conserves each cloud's A_V x area, elongated as round, and lays it along the long axis", () => {
    const shear = { edges: [0, 10], strain: [-2], sense: -1 };
    const round = cloudRaster(GIANT, RLO, RHI, W, H);
    const long = cloudRaster(GIANT, RLO, RHI, W, H, { shear, elongation: 1 });
    expect(long.census).toBe(round.census);
    expect(Math.abs(held(long.av, W, H, RLO, RHI) / long.census - 1)).toBeLessThan(1e-6);
    expect(long.outside).toBe(0);
    // the deposit's second moments: its long axis along shearEllipse's, its axes' ratio the shape's (5.83)
    const { ratio, angle } = shearEllipse(2, 1);
    const dR = (RHI - RLO) / W, dP = (2 * Math.PI) / H;
    let sw = 0, sxx = 0, syy = 0, sxy = 0;
    const cx = 3 * Math.cos(1), cy = 3 * Math.sin(1);
    for (let i = 0; i < W; i += 1) for (let j = 0; j < H; j += 1) {
      const v = long.av[j * W + i];
      if (!(v > 0)) continue;
      const r = RLO + (i + 0.5) * dR, p = (j + 0.5) * dP, w = v * texelArea(i, RLO, dR, dP);
      const dx = r * Math.cos(p) - cx, dy = r * Math.sin(p) - cy;
      sw += w; sxx += w * dx * dx; syy += w * dy * dy; sxy += w * dx * dy;
    }
    const a = sxx / sw, b = syy / sw, c = sxy / sw;
    const axis = 0.5 * Math.atan2(2 * c, a - b); // the moments' long axis
    expect(Math.abs(Math.sin(axis - (1 + angle)))).toBeLessThan(0.02);
    const l1 = (a + b) / 2 + Math.sqrt(((a - b) / 2) ** 2 + c * c), l2 = (a + b) / 2 - Math.sqrt(((a - b) / 2) ** 2 + c * c);
    expect(Math.sqrt(l1 / l2) / ratio).toBeGreaterThan(0.95); // the axes' ratio (sampled on 5 pc texels)
    expect(Math.sqrt(l1 / l2) / ratio).toBeLessThan(1.05);
  });

  it("is round to the bit at the exponent 0 and with the field absent (the layer off)", () => {
    const round = cloudRaster(GIANT, RLO, RHI, W, H);
    expect(Array.from(cloudRaster(GIANT, RLO, RHI, W, H, { shear: { edges: [0, 10], strain: [-2], sense: -1 }, elongation: 0 }).av)).toEqual(Array.from(round.av));
    expect(Array.from(cloudRaster(GIANT, RLO, RHI, W, H, { shear: null, elongation: 1 }).av)).toEqual(Array.from(round.av));
  });

  it("reads the strain of the ring the cloud sits in", () => {
    const edges = [0, 1, 2, 3], strain = [-2, -1.8, -1.6];
    expect([strainAt(0.5, edges, strain), strainAt(1, edges, strain), strainAt(2.5, edges, strain), strainAt(9, edges, strain)]).toEqual([-2, -1.8, -1.6, -1.6]);
  });
});
