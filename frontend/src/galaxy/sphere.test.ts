import { describe, expect, it } from "vitest";

import {
  GOLDEN_ANGLE,
  SPHERE_KERNEL_MAX_HALF,
  SPHERE_LATTICE_PX,
  SPHERE_MAX_PAIRS,
  SPHERE_MIN_PX,
  SPHERE_NORM_LOOP_HALF,
  type Kernel,
  chord,
  chordCell,
  chordIntegral,
  kernelSum,
  knotDeposit,
  knotScale,
  latticeHalf,
  sphereMode,
  sphereNorm,
  tapOffset,
  tapPairs,
} from "./sphere";
import { spriteSample, spriteTexels } from "./sprite";

// S102 (#232, batch Q's viewer lane V2): a knot is its HII region's sphere in projection - the chord profile
// sqrt(1 - (r/R)^2) - convolved with what a point already gets. The closures: the knot's light is the point's.

const SPRITE_PX = 9; // the default sprite (tuning.ts STAR_SPRITE_PX)
const TEXELS = spriteTexels(64);
/** The default sprite as a point deposits it (FluxPoints mode 0): its texture read at gl_PointCoord over its square. */
const sprite: Kernel = (ox, oy) =>
  Math.abs(ox) < SPRITE_PX / 2 && Math.abs(oy) < SPRITE_PX / 2 ? spriteSample(TEXELS, 64, ox / SPRITE_PX + 0.5, 0.5 - oy / SPRITE_PX) : 0;
const SPRITE_REACH = Math.floor(SPRITE_PX / 2);

/**
 * A kernel of the instrument's kind (hstPsf.ts psfRect, FluxPoints' sphere modes): a Gaussian of width `sigma` px
 * integrated over each pixel through its cumulative (any monotone cumulative telescopes the same way), the rectangle
 * clipped to the kernel's box of half-side `reach` + 0.5 and divided by the box's light - so its sum over the pixels is
 * 1 wherever the point stands, as the shaders' clipped psfRect over the centred box's light is.
 */
function hstPsfLikeKernel(sigma: number, reach = 4): { kernel: Kernel; reach: number } {
  const erf = (x: number) => {
    const t = 1 / (1 + 0.3275911 * Math.abs(x));
    const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return x >= 0 ? y : -y;
  };
  const cum = (x: number) => 0.5 * (1 + erf(x / (sigma * Math.SQRT2)));
  const b = reach + 0.5;
  const clip = (v: number) => Math.min(b, Math.max(-b, v));
  const along = (lo: number, hi: number) => cum(clip(hi)) - cum(clip(lo));
  const box = along(-b, b) ** 2;
  return { kernel: (ox, oy) => (along(ox - 0.5, ox + 0.5) * along(oy - 0.5, oy + 0.5)) / box, reach };
}

/** Every pixel's deposit summed: the knot's light on the screen. */
function total(kernel: Kernel, reach: number, cx: number, cy: number, r: number): number {
  const h = Math.ceil(r) + 2 + reach;
  const scale = knotScale(kernel, reach, cx, cy, r);
  let s = 0;
  for (let kx = Math.floor(cx) - h; kx <= Math.floor(cx) + h; kx += 1) {
    for (let ky = Math.floor(cy) - h; ky <= Math.floor(cy) + h; ky += 1) s += knotDeposit(kernel, reach, kx, ky, cx, cy, r, scale);
  }
  return s;
}

describe("the chord through a uniform sphere (geometry)", () => {
  it("is sqrt(1 - rho^2) inside, 0 outside, and integrates to 2 pi R^2 / 3", () => {
    expect(chord(0)).toBe(1);
    expect(chord(0.6)).toBeCloseTo(0.8, 15);
    expect(chord(1)).toBe(0);
    expect(chord(1.5)).toBe(0);
    // the pixel means summed over a large radius are the integral (a midpoint rule on a fine grid)
    expect(sphereNorm(0.3, 0.7, 30) / chordIntegral(30)).toBe(1); // past the loop's bound: the integral itself
    const h = SPHERE_NORM_LOOP_HALF - 1;
    expect(Math.abs(sphereNorm(0.3, 0.7, h - 1) / chordIntegral(h - 1) - 1)).toBeLessThan(1e-3);
    expect(latticeHalf(h - 1)).toBeLessThanOrEqual(SPHERE_NORM_LOOP_HALF);
  });

  it("taps: antipodal pairs at the profile's radial quantiles, centroid the centre, second moment 2/5", () => {
    for (const n of [1, 2, 8, 32]) {
      let sx = 0;
      let sy = 0;
      let s2 = 0;
      for (let t = 0; t < 2 * n; t += 1) {
        const [x, y] = tapOffset(t, n);
        expect(Math.hypot(x, y)).toBeLessThan(1);
        sx += x;
        sy += y;
        s2 += x * x + y * y;
      }
      expect(Math.abs(sx)).toBeLessThan(1e-12);
      expect(Math.abs(sy)).toBeLessThan(1e-12);
      // <rho^2> of the projected uniform sphere is 2/5; the quantile midpoints reach it as n grows
      if (n >= 8) expect(Math.abs(s2 / (2 * n) - 0.4)).toBeLessThan(0.01);
    }
    expect(tapPairs(0.25)).toBe(1);
    expect(tapPairs(1)).toBe(2);
    expect(tapPairs(3.99)).toBe(32);
    expect(sphereMode(SPHERE_MIN_PX * 0.999)).toBe(0);
    expect(sphereMode(SPHERE_MIN_PX)).toBe(1);
    expect(sphereMode(SPHERE_LATTICE_PX)).toBe(2);
    expect(sphereMode(Number.NaN)).toBe(0);
  });
});

describe("the knot's light is the point's (the closure)", () => {
  const radii = [0.1, 0.25, 0.5, 1, 2, 3.5, 3.99, 4, 6, 10, 20];
  const centres: [number, number][] = [
    [100.5, 100.5],
    [100.13, 100.71],
    [100.0, 100.97],
  ];

  it("through an instrument's image whose box sum is 1 at every offset: exactly, R from 0.1 to 20 px", () => {
    // a pixel-integrated kernel (the PSF table's way, hstPsf.ts psfRect): its sum over the pixels is 1 wherever it stands
    const { kernel, reach } = hstPsfLikeKernel(1.3);
    for (const [cx, cy] of centres) {
      for (const r of radii) expect(Math.abs(total(kernel, reach, cx, cy, r) - 1), `R ${r} at ${cx}, ${cy}`).toBeLessThan(1e-12);
    }
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)

  it("through the default sprite: exactly the point's own light at the same centre, R from 0.1 to 20 px", () => {
    // The sprite's deposit wobbles with where a point falls in its pixel (bilinear sampling at the pixel centres in its
    // square): the knot's samples are scaled to the point's own sum at the centre (knotScale), so the closure is exact.
    const pointAt = (x: number, y: number) => total(sprite, SPRITE_REACH, x, y, 0);
    const spread: number[] = [];
    for (let i = 0; i < 16; i += 1) for (let j = 0; j < 16; j += 1) spread.push(pointAt(100 + i / 16, 100 + j / 16));
    // measured 0.0209 (S102): the point's own light wobbles this much as it crosses a pixel, before any knot
    expect(Math.max(...spread) / Math.min(...spread) - 1).toBeLessThan(0.025);
    expect(pointAt(100.13, 100.71)).toBe(kernelSum(sprite, SPRITE_REACH, 100.13, 100.71));
    let worst = 0;
    for (const [cx, cy] of centres) {
      const point = pointAt(cx, cy);
      for (const r of radii) {
        const knot = total(sprite, SPRITE_REACH, cx, cy, r);
        worst = Math.max(worst, Math.abs(knot / point - 1));
        expect(Math.abs(knot / point - 1), `R ${r} at ${cx}, ${cy}`).toBeLessThan(1e-12);
        if (r < SPHERE_MIN_PX) expect(knot).toBe(point); // the point, by the same statement
      }
    }
    console.log(`S102 sphere closure through the default sprite, R 0.1-20 px: worst |knot / point - 1| ${worst.toExponential(2)}`);
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)


  it("the two samplings agree where they hand over, and the profile's width follows R", () => {
    const { kernel, reach } = hstPsfLikeKernel(1.3);
    const below = SPHERE_LATTICE_PX - 1e-9;
    let diff = 0;
    let sum = 0;
    const cx = 100.13;
    const cy = 100.71;
    for (let kx = 90; kx <= 111; kx += 1) {
      for (let ky = 90; ky <= 111; ky += 1) {
        const a = knotDeposit(kernel, reach, kx, ky, cx, cy, below);
        const b = knotDeposit(kernel, reach, kx, ky, cx, cy, SPHERE_LATTICE_PX);
        diff += Math.abs(a - b);
        sum += b;
      }
    }
    expect(diff / sum).toBeLessThan(0.05);
    // The light's second moment about the centre: the kernel's plus the profile's 2 R^2 / 5 (convolution adds them).
    const moment = (r: number) => {
      let m = 0;
      for (let kx = 60; kx <= 141; kx += 1) {
        for (let ky = 60; ky <= 141; ky += 1) m += knotDeposit(kernel, reach, kx, ky, 100.5, 100.5, r) * ((kx + 0.5 - 100.5) ** 2 + (ky + 0.5 - 100.5) ** 2);
      }
      return m;
    };
    const k0 = moment(0);
    for (const r of [10, 20]) expect(Math.abs((moment(r) - k0) / (0.4 * r * r) - 1)).toBeLessThan(0.02);
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)

  it("chordCell is the 2 x 2 mean of the chord over the pixel", () => {
    expect(chordCell(0, 0, 1e6)).toBeCloseTo(1, 9);
    expect(chordCell(10, 0, 2)).toBe(0);
  });
});

describe("the shaders carry sphere.ts's numbers and expressions (FluxPoints modes 5 and 6)", () => {
  it("the switch, the taps, the cells, the lattice's bound and the closure's scale", async () => {
    const { FLUX_POINTS_SHADER } = await import("./FluxPoints");
    const { vertex, fragment } = FLUX_POINTS_SHADER;
    for (const text of [vertex, fragment]) {
      expect(text).toContain("float rho = sqrt(1.0 - pow(1.0 - f, 2.0 / 3.0));");
      expect(text).toContain(`float turn = p * ${GOLDEN_ANGLE.toFixed(9)} + mod(t, 2.0) * 3.14159265;`);
      expect(text).toContain("return sqrt(max(0.0, 1.0 - rho * rho));");
      expect(text).toContain(`if (r < ${SPHERE_LATTICE_PX.toFixed(1)}) {`);
    }
    expect(vertex).toContain(`if (profile > 2.5 && extent >= ${SPHERE_MIN_PX} * side) mode = mode > 2.5 ? 6.0 : 5.0;`);
    expect(vertex).toContain(`float pairs = min(${SPHERE_MAX_PAIRS.toFixed(1)}, max(1.0, ceil(2.0 * r * r)));`);
    expect(vertex).toContain(`if (h > ${SPHERE_NORM_LOOP_HALF.toFixed(1)}) return 2.0 * 3.14159265 * r * r / 3.0;`);
    expect(vertex).toContain(`min(ceil(0.5 * psfCells * psfCellPc / side), ${SPHERE_KERNEL_MAX_HALF.toFixed(1)})`);
    expect(vertex).toContain("samples = spriteSum(vec2(0.5));");
  });
});
