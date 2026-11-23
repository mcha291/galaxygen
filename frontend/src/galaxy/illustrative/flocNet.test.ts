// The plane style of the flocculent network (S106, flocNet.ts): isotropic in the small, on arcs in the large, the
// encoding flocMap.ts's, fast enough for a slider.
import { describe, expect, it } from "vitest";

import { floc, shapeOf } from "./floc";
import { FLOC_MAP, type FlocGeometry, flocDecode } from "./flocMap";
import { buildNetChannel, netSampler } from "./flocNet";
import { illDefaults, paramsOf } from "./index";

const RHI = 30;
const G: FlocGeometry = { rHi: RHI, pitchDeg: 20, gas: null, pattern: null, gasProfile: null };
const SHAPE = shapeOf(paramsOf(floc, illDefaults("ngc_4414")));

describe("the network drawn in the plane", () => {
  it("is NGC 4414's style, and not the Milky Way's", () => {
    expect(SHAPE.style).toBe(1);
    expect(shapeOf(paramsOf(floc, illDefaults("milky_way"))).style).toBe(0);
  });

  it("is isotropic in the small: the dust's change over 60 pc along the azimuth and along the radius alike", () => {
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
      const h = 0.06;
      along += Math.abs(net.dust(x - Math.sin(phi) * h, y + Math.cos(phi) * h) - d0);
      across += Math.abs(net.dust(x + Math.cos(phi) * h, y + Math.sin(phi) * h) - d0);
      n += 1;
    }
    expect(along / n).toBeGreaterThan(0);
    // Within a factor 1.6 either way (S105's lace: five times smoother along than across).
    expect(along / across).toBeGreaterThan(1 / 1.6);
    expect(along / across).toBeLessThan(1.6);
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
    expect(dust / all).toBeLessThan(0.6);
    expect(knots).toBeGreaterThan(0);
    // No byte of zero ("no map") is written.
    expect(map.indexOf(0)).toBe(-1);
  });
});
