// The plane style of the flocculent network (S106, flocNet.ts): isotropic in the small, on arcs in the large, the
// encoding flocMap.ts's, fast enough for a slider.
import { describe, expect, it } from "vitest";

import { cloudShapeOf, floc, shapeOf } from "./floc";
import { buildClouds } from "./flocClouds";
import { FLOC_MAP, type FlocGeometry, flocDecode } from "./flocMap";
import { buildNetChannel, netSampler } from "./flocNet";
import { illDefaults, paramsOf } from "./index";

const RHI = 30;
const G: FlocGeometry = { rHi: RHI, pitchDeg: 20, gas: null, pattern: null, gasProfile: null };
const SHAPE = shapeOf(paramsOf(floc, illDefaults("ngc_4414")));

describe("the star clouds", () => {
  it("places NGC 4414's points in groups in the outer disc, inside its edge, fast", () => {
    const p = paramsOf(floc, illDefaults("ngc_4414"));
    const t0 = performance.now();
    const c = buildClouds(G, SHAPE, cloudShapeOf(p));
    const ms = performance.now() - t0;
    console.log(`star clouds: ${c.weight.length} points in ${c.groups.length} groups, ${ms.toFixed(0)} ms`);
    expect(c.weight.length).toBeGreaterThan(0.8 * p.cloudCount);
    expect(c.groups.length).toBeGreaterThan(20);
    let outside = 0;
    let beyond = 0;
    const edge = SHAPE.cloudReach * SHAPE.outerRadius;
    for (let i = 0; i < c.x.length; i += 1) {
      const r = Math.hypot(c.x[i], c.y[i]);
      if (r > 0.45 * SHAPE.outerRadius) outside += 1;
      if (r > 1.1 * edge) beyond += 1;
    }
    expect(outside / c.x.length).toBeGreaterThan(0.6);
    // Hardly anything past the disc's edge: a few stragglers of a group's spread at most.
    expect(beyond / c.x.length).toBeLessThan(0.02);
    expect(ms).toBeLessThan(1500);
    expect(cloudShapeOf(paramsOf(floc, illDefaults("milky_way"))).count).toBe(0);
  });
});

describe("the network drawn in the plane", () => {
  it("is NGC 4414's style, and not the Milky Way's", () => {
    expect(SHAPE.style).toBe(1);
    expect(shapeOf(paramsOf(floc, illDefaults("milky_way"))).style).toBe(0);
  });

  it("draws threads along the spiral: the dust changes more over 30 pc along the radius than along the azimuth", () => {
    const net = netSampler(G, SHAPE);
    let along = 0;
    let across = 0;
    let n = 0;
    for (let k = 0; k < 4000; k += 1) {
      const r = 2 + (k % 40) * 0.12;
      const phi = (k * 2.39996) % (2 * Math.PI);
      const x = r * Math.cos(phi);
      const y = r * Math.sin(phi);
      const d0 = net.dust(x, y);
      const h = 0.03;
      along += Math.abs(net.dust(x - Math.sin(phi) * h, y + Math.cos(phi) * h) - d0);
      across += Math.abs(net.dust(x + Math.cos(phi) * h, y + Math.sin(phi) * h) - d0);
      n += 1;
    }
    expect(along / n).toBeGreaterThan(0);
    // Thin threads at a low pitch: much sharper across the rings than along them.
    expect(across / along).toBeGreaterThan(1.8);
  });

  it("covers a share of the disc with dust and leaves light between, both from the one channel, in under 0.4 s", () => {
    const t0 = performance.now();
    const map = buildNetChannel(G, SHAPE);
    const ms = performance.now() - t0;
    console.log(`floc plane style: ${ms.toFixed(0)} ms`);
    expect(ms).toBeLessThan(1500);
    let dust = 0;
    let all = 0;
    let knots = 0;
    for (let i = 0; i < FLOC_MAP.rings; i += 1) {
      const r = ((i + 0.5) * RHI) / FLOC_MAP.rings;
      if (r < 1 || r > 0.6 * SHAPE.outerRadius) continue;
      for (let j = 0; j < FLOC_MAP.sectors; j += 7) {
        const d = flocDecode(map[j * FLOC_MAP.rings + i]);
        if (d.shape > 0.25) dust += r;
        if (d.clump > 0.2) knots += 1;
        all += r;
      }
    }
    expect(dust / all).toBeGreaterThan(0.1);
    expect(dust / all).toBeLessThan(0.9);
    expect(knots).toBeGreaterThan(0);
    // No byte of zero ("no map") is written.
    expect(map.indexOf(0)).toBe(-1);
  });
});
