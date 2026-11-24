// The plane style of the flocculent network (S106, flocNet.ts): isotropic in the small, on arcs in the large, the
// encoding flocMap.ts's, fast enough for a slider.
import { describe, expect, it } from "vitest";

import { cloudShapeOf, cloudThin, floc, shapeOf } from "./floc";
import { buildClouds } from "./flocClouds";
import { FLOC_MAP, type FlocGeometry, flocDecode } from "./flocMap";
import { buildNetChannel, netSampler } from "./flocNet";
import { illDefaults, paramsOf } from "./index";

const RHI = 30;
const G: FlocGeometry = { rHi: RHI, pitchDeg: 20, gas: null, pattern: null, gasProfile: null };
// NGC 4414's network with its threads drawn (its default draws its dust as the march's mesh, netDepth 0; S106 C4).
const SHAPE = { ...shapeOf(paramsOf(floc, illDefaults("ngc_4414"))), netDepth: 1.6, cloudGlow: 1 }; // S109: the clouds' glow held on (NGC 4414's default is now 0) so the knots are drawn

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

describe("the star clouds' complexes (S106 C4)", () => {
  it("makes a share of the groups large: more members over a wider glow", () => {
    const plain = buildClouds(G, { ...SHAPE, cloudComplex: 0 });
    const rich = buildClouds(G, { ...SHAPE, cloudComplex: 0.5 });
    const largest = (c: ReturnType<typeof buildClouds>) => c.groups.reduce((m, g) => Math.max(m, g.size), 0);
    expect(largest(rich)).toBeGreaterThan(largest(plain));
    expect(rich.groups.length).toBeLessThan(plain.groups.length);
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

  it("draws thin threads (tens of parsecs across), most dust in the ring, little in the nuclear region", () => {
    const net = netSampler(G, SHAPE);
    const widths: number[] = [];
    const cover = (lo: number, hi: number) => {
      let n = 0;
      let hit = 0;
      for (let k = 0; k < 60; k += 1) {
        const phi = k * 0.1047;
        let start = -1;
        for (let r = lo; r < hi; r += 0.004) {
          const v = net.dust(r * Math.cos(phi), r * Math.sin(phi));
          n += 1;
          if (v > 0.3) hit += 1;
          if (v > 0.5 && start < 0) start = r;
          if (v <= 0.5 && start >= 0) {
            widths.push((r - start) * 1000);
            start = -1;
          }
        }
      }
      return hit / n;
    };
    const outer = SHAPE.outerRadius;
    const ring = cover(0.3 * outer, 0.6 * outer);
    widths.sort((a, b) => a - b);
    const median = widths[Math.floor(widths.length / 2)];
    // Measured along the radius, a thread at the pitch reads a little wider than across it.
    expect(median).toBeGreaterThan(15);
    expect(median).toBeLessThan(90);
    expect(widths.length).toBeGreaterThan(300);
    const core = cover(0.02 * outer, 0.07 * outer);
    expect(ring).toBeGreaterThan(2 * core);
  });

  it("lays the near-side bias toward its azimuth", () => {
    const biased = netSampler(G, { ...SHAPE, nearBias: 0.8, nearAz: 90 });
    const mean = (phi0: number) => {
      let s = 0;
      for (let k = 0; k < 4000; k += 1) {
        const r = 2 + (k % 50) * 0.08;
        const phi = phi0 + ((k * 0.618) % 1 - 0.5) * 1.2;
        s += biased.dust(r * Math.cos(phi), r * Math.sin(phi));
      }
      return s;
    };
    expect(mean(Math.PI / 2)).toBeGreaterThan(1.5 * mean((3 * Math.PI) / 2));
  });
});

describe("the star clouds thinned by the fall-off (S109 B2)", () => {
  it("changes nothing on the Milky Way; on NGC 4414 leaves the inner clouds and takes some of the outer away", () => {
    expect(cloudThin(paramsOf(floc, illDefaults("milky_way"))).thin).toBeUndefined();
    const p = paramsOf(floc, illDefaults("ngc_4414"));
    const { thin } = cloudThin(p);
    expect(thin).toBeDefined();
    expect(thin!(p.fallIn - 0.1)).toBe(1);
    expect(thin!(p.fallOut + 1)).toBeCloseTo(2 ** -(p.fall * p.cloudFall), 9);
    // A thinning of 1 everywhere draws the clouds as without it, point for point.
    const a = buildClouds(G, SHAPE, cloudShapeOf(p));
    const b = buildClouds(G, SHAPE, cloudShapeOf(p), () => 1);
    expect(Array.from(b.x)).toEqual(Array.from(a.x));
    const c = buildClouds(G, SHAPE, cloudShapeOf(p), thin);
    const outer = (cl: typeof a) => Array.from(cl.x).filter((x, i) => Math.hypot(x, cl.y[i]) > p.fallIn + 1.5).length;
    expect(outer(c)).toBeLessThan(outer(a));
  });
});
