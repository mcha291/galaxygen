import { describe, expect, it } from "vitest";

import { features, illDefaults, illGlsl, paramsOf } from "./index";
import { MAX_SKY_STARS, buildSkyStars, frameSolidAngle, sky, skyBrightness, skyDrawn, skyTint, sphereCount } from "./sky";

const LUMA = [0.2126, 0.7152, 0.0722];
const shape = { count: 5000, seed: 7, slope: 1.1, range: 80, warm: 0.12, blue: 0.7 };

describe("the sky (S106): field stars fixed on the sky, the floor and the halo", () => {
  it("is registered, with no GLSL in the march and no hook: a layer of its own", () => {
    expect(features()).toContain(sky);
    expect(sky.glsl).toBeUndefined();
    expect(sky.noiseGlsl).toBeUndefined();
    expect(sky.hooks).toBeUndefined();
    expect(sky.map).toBeUndefined();
    expect(sky.uniforms).toBeUndefined();
    expect(sky.layer).toBeDefined();
    expect(illGlsl()).not.toMatch(/sky/i);
  });

  it("draws nothing on the Milky Way by default and all three parts on NGC 4414", () => {
    const mw = paramsOf(sky, illDefaults("milky_way"));
    expect(skyDrawn(mw)).toBe(false);
    expect(mw.stars).toBe(0);
    expect(mw.floor).toBe(0);
    expect(mw.halo).toBe(0);
    const ngc = paramsOf(sky, illDefaults("ngc_4414"));
    expect(ngc.stars).toBeGreaterThan(0);
    expect(ngc.floor).toBeGreaterThan(0);
    expect(ngc.halo).toBeGreaterThan(0);
    expect(skyDrawn(ngc)).toBe(true);
  });

  it("measures a frame's solid angle (small fields: the product of the two angles; a hemisphere at 180 degrees square)", () => {
    const a = (5 * Math.PI) / 180;
    expect(frameSolidAngle(5, 1) / (a * a)).toBeCloseTo(1, 2);
    expect(frameSolidAngle(5, 2) / frameSolidAngle(5, 1)).toBeCloseTo(2, 1);
    expect(frameSolidAngle(179.999, 1)).toBeCloseTo(2 * Math.PI, 2);
  });

  it("puts the asked number in the frame: the sphere's count scales with the lens, capped", () => {
    expect(sphereCount(0, 45, 1)).toBe(0);
    const n45 = sphereCount(100, 45, 1);
    expect(n45 * frameSolidAngle(45, 1) / (4 * Math.PI)).toBeCloseTo(100, 0);
    expect(sphereCount(100, 5, 1)).toBeGreaterThan(100 * 1500);
    expect(sphereCount(100, 5, 1)).toBeLessThanOrEqual(MAX_SKY_STARS);
    expect(sphereCount(10000, 1, 1)).toBe(MAX_SKY_STARS);
  });

  it("builds the same stars from the same seed and other stars from another", () => {
    const a = buildSkyStars(shape);
    const b = buildSkyStars(shape);
    const c = buildSkyStars({ ...shape, seed: 8 });
    expect(a.direction).toEqual(b.direction);
    expect(a.colour).toEqual(b.colour);
    expect(a.direction).not.toEqual(c.direction);
  });

  it("gives unit directions spread over the whole sphere, weights from 1 to the range, colour of the weight's luminance", () => {
    const s = buildSkyStars(shape);
    let mean = [0, 0, 0];
    for (let i = 0; i < shape.count; i++) {
      const d = [s.direction[3 * i], s.direction[3 * i + 1], s.direction[3 * i + 2]];
      expect(Math.hypot(d[0], d[1], d[2])).toBeCloseTo(1, 5);
      mean = mean.map((m, k) => m + d[k] / shape.count);
      expect(s.weight[i]).toBeGreaterThanOrEqual(1);
      expect(s.weight[i]).toBeLessThanOrEqual(shape.range);
      const l = LUMA[0] * s.colour[3 * i] + LUMA[1] * s.colour[3 * i + 1] + LUMA[2] * s.colour[3 * i + 2];
      expect(l / s.weight[i]).toBeCloseTo(1, 4);
    }
    for (const m of mean) expect(Math.abs(m)).toBeLessThan(0.05);
    // many faint, a handful bright
    const bright = Array.from(s.weight).filter((w) => w > 20).length;
    expect(bright / shape.count).toBeLessThan(0.05);
    expect(Array.from(s.weight).filter((w) => w < 3).length / shape.count).toBeGreaterThan(0.6);
  });

  it("makes about the warm share warm (red above blue) and the rest white to blue-white", () => {
    const s = buildSkyStars(shape);
    let warm = 0;
    for (let i = 0; i < shape.count; i++) if (s.colour[3 * i] > s.colour[3 * i + 2]) warm++;
    expect(warm / shape.count).toBeGreaterThan(0.09);
    expect(warm / shape.count).toBeLessThan(0.15);
  });

  it("keeps its brightness law and tints bounded", () => {
    expect(skyBrightness(0, 1.1, 80)).toBeCloseTo(1, 6);
    expect(skyBrightness(0.999999, 1.1, 80)).toBe(80);
    const t = skyTint([0.08, 0.05, 1], 1);
    expect(LUMA[0] * t[0] + LUMA[1] * t[1] + LUMA[2] * t[2]).toBeCloseTo(1, 6);
    expect(skyTint([0.08, 0.05, 1], 0)).toEqual([1, 1, 1]);
  });
});
