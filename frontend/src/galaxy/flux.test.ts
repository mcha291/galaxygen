import { describe, expect, it } from "vitest";

import { DUST_SEGMENT_STEPS, DUST_TOP_HEIGHTS, type DustRead, dustToPoint, fluxOf, pixelArea, spriteLight, tallestLayer } from "./flux";
import { patternMean, psfMean, psfProfile } from "./psf";

describe("a point's flux (D208)", () => {
  const white = [0.2, 0.1, 0.05];

  it("is its published response over the white point's, channel by channel", () => {
    const flux = fluxOf(Float32Array.from([2, 1, 0.5, 40, 5, 1]), white, 2)!;
    expect(Array.from(flux.slice(0, 3))).toEqual([10, 10, 10]); // a white-point star: the same light in each channel
    expect(flux[3]).toBeCloseTo(200, 4);
    expect(flux[4]).toBeCloseTo(50, 4);
    expect(flux[5]).toBeCloseTo(20, 4);
  });

  it("is no light for a missing number, and nothing at all without a response or a usable white point", () => {
    const flux = fluxOf(Float32Array.from([Number.NaN, -1, 0.5]), white, 1)!;
    expect(Array.from(flux)).toEqual([0, 0, 10]);
    expect(fluxOf(undefined, white, 1)).toBeNull();
    expect(fluxOf(Float32Array.from([1, 1, 1]), null, 1)).toBeNull();
    expect(fluxOf(Float32Array.from([1, 1, 1]), [0.2, 0, 0.05], 1)).toBeNull(); // a channel divided by zero is not drawn
    expect(fluxOf(Float32Array.from([1, 1, 1]), [0.2, null, 0.05], 1)).toBeNull();
    expect(fluxOf(Float32Array.from([1, 1, 1, 1]), white, 2)).toBeNull(); // not N × filters
  });
});

describe("the field's scale (D208)", () => {
  // A 45° camera on a 1000-pixel-high buffer: 1207 px per kpc at unit depth.
  const pxPerUnit = 1000 / (2 * Math.tan((45 * Math.PI) / 360));

  it("gives a pixel the area of sky it covers at the point: its side at that depth, squared, on the axis", () => {
    // At 54 kpc (the whole galaxy in view) a pixel is 44.7 pc on a side.
    expect(Math.sqrt(pixelArea(54, 54, pxPerUnit))).toBeCloseTo((1000 * 54) / pxPerUnit, 9);
    expect(Math.sqrt(pixelArea(54, 54, pxPerUnit))).toBeCloseTo(44.7, 1);
    expect(pixelArea(27, 27, pxPerUnit) / pixelArea(54, 54, pxPerUnit)).toBeCloseTo(0.25, 12); // half as far: a quarter
  });

  it("and off the axis the solid angle's, smaller by the cosine", () => {
    const cos = Math.cos((20 * Math.PI) / 180);
    expect(pixelArea(54, 54 / cos, pxPerUnit) / pixelArea(54, 54, pxPerUnit)).toBeCloseTo(cos, 12);
  });

  it("does not change with the lens: the same framing through 45° and 5° gives a pixel the same sky at the centre (S54, D213)", () => {
    // The points' pixels per kpc at unit depth as FluxPoints sets them, from the camera's own field of view.
    const perUnit = (fov: number) => 1000 / (2 * Math.tan((fov * Math.PI) / 360));
    const distance = (fov: number) => 20 / Math.tan((fov * Math.PI) / 360); // a 20 kpc framing radius (capture.ts distanceFor)
    const wide = pixelArea(distance(45), distance(45), perUnit(45));
    const long = pixelArea(distance(5), distance(5), perUnit(5));
    expect(distance(5)).toBeCloseTo(458.075, 3);
    expect(Math.sqrt(wide)).toBeCloseTo(40, 9); // 40 kpc over 1000 pixels: 40 pc a pixel
    expect(long / wide).toBeCloseTo(1, 12); // so a point is drawn no brighter and no dimmer for the lens
    // Off the centre the two differ by the perspective alone: a star 15 kpc along the near side of a 55° disc is
    // 12.3 kpc nearer the camera, and a pixel there covers less sky - by 44 % at 45°, by 5 % at 5°.
    const nearer = 15 * Math.sin((55 * Math.PI) / 180);
    expect(pixelArea(distance(45) - nearer, distance(45) - nearer, perUnit(45)) / wide).toBeCloseTo(0.556, 3);
    expect(pixelArea(distance(5) - nearer, distance(5) - nearer, perUnit(5)) / long).toBeCloseTo(0.947, 3);
  });

  it("makes a sprite's pixels sum to the point's light over that area, whatever the sprite's size and shape", () => {
    const flux = 34000; // L☉: the 3 162nd brightest disc star
    const area = pixelArea(54, 54, pxPerUnit);
    const gain = 1 / 400;
    for (const [px, mean] of [[9, psfMean()], [18, psfMean()], [25, 0.02]] as const) {
      // A sprite of px × px pixels whose pattern averages `mean`: its pixels' patterns sum to px² × mean.
      const summed = spriteLight(flux, gain, area, px, mean) * px * px * mean;
      expect(summed).toBeCloseTo((flux * gain) / area, 12);
    }
    // 17 L☉/pc² in all, spread over the sprite: far under a disc of tens to hundreds (D208 (2)).
    expect(flux / area).toBeCloseTo(17.0, 0);
  });

  it("knows each sprite's mean: the default's from its own profile, an instrument's from its texture", () => {
    // The default sprite as its 8-bit texture holds it, against the profile integrated on the same grid.
    let exact = 0;
    for (let y = 0; y < 64; y += 1) for (let x = 0; x < 64; x += 1) exact += psfProfile(Math.hypot(x + 0.5 - 32, y + 0.5 - 32) / 32);
    expect(psfMean()).toBeCloseTo(exact / 4096, 3);
    expect(psfMean()).toBeGreaterThan(0.03);
    expect(psfMean()).toBeLessThan(0.12);
    // A float sprite: channel × alpha, averaged over every texel.
    expect(patternMean(Float32Array.from([1, 0.5, 0, 0.5, 0, 0, 0, 0, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0]))).toEqual([0.375, 0.3125, 0.25]);
  });
});

describe("the dust in front of a point (T20, D208)", () => {
  // A disc whose dust thins outward and flares: face-on depth 5 e^(−r/3) in every channel (twice that in blue),
  // in a layer of 0.05 + 0.01 r kpc.
  const read: DustRead = (r) => {
    const t = 5 * Math.exp(-r / 3);
    return { depth: [t, t, 2 * t], height: 0.05 + 0.01 * r };
  };
  const sech2 = (x: number) => 1 / Math.cosh(Math.min(30, Math.max(-30, x))) ** 2;
  // The same integral by brute force: the dust's density along the segment, 200 000 points.
  const quadrature = (point: number[], eye: number[], n = 200_000) => {
    const d = eye.map((v, k) => v - point[k]);
    const length = Math.hypot(...d);
    let tau = 0;
    for (let j = 0; j < n; j += 1) {
      const s = ((j + 0.5) / n) * length;
      const q = point.map((v, k) => v + (d[k] / length) * s);
      const r = Math.hypot(q[0], q[2]);
      if (r >= 30) continue;
      const at = read(r, 0);
      tau += (at.depth[0] * sech2(q[1] / (2 * at.height)) * (length / n)) / (4 * at.height);
    }
    return tau;
  };

  it("is half the ring's depth for a star in the midplane seen face-on, all of it for one behind the layer, none in front", () => {
    const ring = read(5, 0).depth[0];
    expect(dustToPoint([5, 0, 0], [5, 60, 0], 8, 30, read)[0]).toBeCloseTo(ring / 2, 6);
    expect(dustToPoint([5, -6, 0], [5, 60, 0], 8, 30, read)[0]).toBeCloseTo(ring, 6);
    expect(dustToPoint([5, 6, 0], [5, 60, 0], 8, 30, read)[0]).toBeLessThan(1e-9 * ring);
    // Per channel: blue takes twice the depth.
    const tau = dustToPoint([5, 0, 0], [5, 60, 0], 8, 30, read);
    expect(tau[2]).toBeCloseTo(2 * tau[0], 12);
    expect(tau[1]).toBe(tau[0]);
  });

  it("follows the two layers' own integral along an inclined and a near edge-on segment", () => {
    for (const [point, eye, tolerance] of [
      [[5, 0, 0], [35, 30, 0], 0.01], // 45° to the plane
      [[5, 0.02, 2], [-20, 25, 30], 0.01],
      [[8, -0.1, 0], [8, 20, 60], 0.02], // steeply inclined: the ray runs 3 kpc of the plane per kpc of height
      [[-6, 0, 0], [70, 3, 0], 0.06], // near edge-on, through the centre: coarse steps over a steep inner disc
    ] as const) {
      const got = dustToPoint(point as unknown as [number, number, number], eye as unknown as [number, number, number], 8, 30, read)[0];
      const want = quadrature([...point], [...eye]);
      expect(Math.abs(got - want) / want, `${point} → ${eye}: ${got} against ${want}`).toBeLessThan(tolerance);
    }
  });

  it("stops at the slab and at the disc's edge, and is nothing where there is no layer", () => {
    expect(dustToPoint([40, 0, 0], [40, 60, 0], 8, 30, read)).toEqual([0, 0, 0]); // outside the disc's radius
    expect(dustToPoint([5, 20, 0], [5, 60, 0], 8, 30, read)).toEqual([0, 0, 0]); // above the slab, looking up
    expect(dustToPoint([5, 0, 0], [5, 0, 0], 8, 30, read)).toEqual([0, 0, 0]); // the camera on the star
    const none: DustRead = () => ({ depth: [3, 3, 3], height: 0 });
    expect(dustToPoint([5, 0, 0], [5, 60, 0], 8, 30, none)).toEqual([0, 0, 0]);
    expect(DUST_SEGMENT_STEPS).toBe(48);
  });

  it("cuts the slab at sixteen of the tallest layer's heights", () => {
    expect(DUST_TOP_HEIGHTS).toBe(16);
    expect(tallestLayer(Float32Array.from([0.02, 0.11, Number.NaN, 1.3, 0]))).toBeCloseTo(1.3, 6);
    expect(tallestLayer(0.36)).toBe(0.36);
    expect(tallestLayer(null)).toBe(0);
    expect(tallestLayer(Number.NaN)).toBe(0);
  });
});
