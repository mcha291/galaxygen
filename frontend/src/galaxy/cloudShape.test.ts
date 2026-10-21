import { describe, expect, it } from "vitest";

import { SECH2_HWHM_PER_H, cloudEllipse, cloudRaster, texelArea } from "./cloudOpacity";
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

describe("R2: a cloud's face-on ellipse along the gas field's shear (S67, D230; the shape published since S70, F-4-3)", () => {
  // Since S70 (Audit V F-4-3) the model publishes each cloud's axis ratio lambda+ and long axis angle (/api/clouds'
  // cloud_axis_ratio and cloud_angle; tests/test_v6_clouds.py holds them to the field's own read by finite differences);
  // the viewer raises the ratio to its elongation power. At the strain -2 and sense -1 of the S67 tests, k = 2: lambda+ =
  // 3 + 2 sqrt 2, the long axis at atan2(lambda+ - 1, k) from r-hat - this file's own arithmetic.
  const LAM = 3 + 2 * Math.SQRT2;
  const ANGLE = Math.atan2(LAM - 1, 2);
  const SHAPED = { ...GIANT, cloud_axis_ratio: [LAM], cloud_angle: [ANGLE] };

  it("raises the published ratio to the elongation's power: round at 0 and for a round cloud, lambda+ ^ e between", () => {
    expect(cloudEllipse(LAM, ANGLE, 1)).toEqual({ ratio: LAM, angle: ANGLE });
    expect(cloudEllipse(LAM, ANGLE, 0).ratio).toBe(1);
    expect(cloudEllipse(1, 0, 1).ratio).toBe(1);
    expect(cloudEllipse(LAM, ANGLE, 0.5).ratio).toBeCloseTo(Math.sqrt(LAM), 12);
  });

  it("conserves each cloud's A_V x area, elongated as round, and lays it along the long axis", () => {
    const round = cloudRaster(GIANT, RLO, RHI, W, H);
    const long = cloudRaster(SHAPED, RLO, RHI, W, H, { elongation: 1 });
    expect(long.census).toBe(round.census);
    expect(Math.abs(held(long.av, W, H, RLO, RHI) / long.census - 1)).toBeLessThan(1e-6);
    expect(long.outside).toBe(0);
    // the deposit's second moments: its long axis along the published angle, its axes' ratio the published (5.83)
    const ratio = LAM, angle = ANGLE;
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

  it("is round to the bit at the exponent 0, without the columns, and for a published ratio of 1 (the layer off)", () => {
    const round = cloudRaster(GIANT, RLO, RHI, W, H);
    expect(Array.from(cloudRaster(SHAPED, RLO, RHI, W, H, { elongation: 0 }).av)).toEqual(Array.from(round.av));
    expect(Array.from(cloudRaster(GIANT, RLO, RHI, W, H, { elongation: 1 }).av)).toEqual(Array.from(round.av));
    const off = { ...GIANT, cloud_axis_ratio: [1], cloud_angle: [0] };
    expect(Array.from(cloudRaster(off, RLO, RHI, W, H, { elongation: 1 }).av)).toEqual(Array.from(round.av));
  });
});
