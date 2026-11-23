// The flocculent network (S109, BUILD_VIII row 109): the map's determinism and encoding, its covering fraction at the
// defaults, the filaments' pitch against the published pitch, where the patches and clumps lie, the controls on every
// template, and the feature's registration. Illustrative: nothing here is a number of the model's but the convention
// of a pitch (ln R = tan(pitch) phi + c, azimuth growing outward).

import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import { ILL_MAP, ILL_MAP_CHANNELS, type IllFrame } from "./feature";
import { floc, flocChannel, flocDrawn, shapeOf } from "./floc";
import {
  FLOC_ARRAYS, FLOC_MAP, FLOC_REACH, type FlocGeometry, type FlocShape, Ladder, SHAPE_KEYS, buildFlocChannel, flocClumps, flocCover, flocDecode, flocGrains, flocKey, flocLight, flocPatches,
  flocStrands, geometryOf, lightReach, readField, spiralNoise, strandPitch,
} from "./flocMap";
import { features, illArrays, illDefaults, illGlsl, illustrativeFragment, paramsOf } from "./index";

const DEG = Math.PI / 180;
const TAU = 2 * Math.PI;
const RINGS = 400;
const SECTORS = 360;
const RHI = 30;
const PITCH = 28.9;

/** A galaxy for the tests: three gas ridges (1 +- 0.3) and four stellar ones (1 +- 0.35) on 20-degree spirals, an exponential gas profile. */
function frame(): IllFrame {
  const gas = new Float64Array(RINGS * SECTORS);
  const pattern = new Float64Array(RINGS * SECTORS);
  const profile = new Float64Array(RINGS);
  for (let i = 0; i < RINGS; i += 1) {
    const r = ((i + 0.5) * RHI) / RINGS;
    profile[i] = 40 * Math.exp(-r / 4);
    for (let j = 0; j < SECTORS; j += 1) {
      const phi = ((j + 0.5) * TAU) / SECTORS;
      const on = r < 10 ? 1 : 0;
      gas[i * SECTORS + j] = 1 + on * 0.3 * Math.cos(3 * (phi - Math.log(r) / Math.tan(20 * DEG)));
      pattern[i * SECTORS + j] = 1 + on * 0.35 * Math.cos(4 * (phi - Math.log(r) / Math.tan(20 * DEG)));
    }
  }
  return {
    header: { scalars: { pitch_angle: PITCH }, grid: { axes: { R: { n: RINGS, hi: RHI }, phi: { n: SECTORS } } } },
    arrays: { gas_density_contrast: gas, pattern_density_contrast: pattern, gas_surface_density: profile },
  };
}

const FRAME = frame();
const G: FlocGeometry = geometryOf(FRAME);
/** NGC 4414's defaults: the tuned preset. */
const P4414 = paramsOf(floc, illDefaults("ngc_4414"));
/**
 * The drawing's own shape, as its builder set it beside the goal (S109: the controls' defaults, the pitch NGC 4414's):
 * the properties below are the drawing's, read at it. S105 tuner N moved NGC 4414's shaping values (a denser, finer,
 * spread network); the tuned shape has a test of its own (the cover, below).
 */
const SHAPE: FlocShape = shapeOf({ ...paramsOf(floc, illDefaults(null)), pitch: P4414.pitch });
/** The map at the defaults, at its full size: built once for the tests that read it. */
let full: Uint8Array | null = null;
const fullMap = (): Uint8Array => (full ??= buildFlocChannel(G, SHAPE));
const byteAt = (map: Uint8Array, r: number, phi: number): number => {
  const i = Math.min(FLOC_MAP.rings - 1, Math.floor((r / RHI) * FLOC_MAP.rings));
  const j = ((Math.floor((phi / TAU) * FLOC_MAP.sectors) % FLOC_MAP.sectors) + FLOC_MAP.sectors) % FLOC_MAP.sectors;
  return map[j * FLOC_MAP.rings + i];
};

describe("the frame read (FLOC_ARRAYS)", () => {
  it("takes the pitch, the two contrasts and the gas's profile, and a pitch of its own where none is published", () => {
    expect(G.pitchDeg).toBe(PITCH);
    expect(G.rHi).toBe(RHI);
    expect(G.gas?.values.length).toBe(RINGS * SECTORS);
    expect(G.pattern?.values.length).toBe(RINGS * SECTORS);
    expect(G.gasProfile?.length).toBe(RINGS);
    const bare = geometryOf({ header: { scalars: {} }, arrays: {} });
    expect(bare.pitchDeg).toBe(20);
    expect([bare.gas, bare.pattern, bare.gasProfile]).toEqual([null, null, null]);
    expect(illArrays()).toEqual(expect.arrayContaining([...FLOC_ARRAYS]));
  });
});

describe("the spiral noise: cells along a log spiral, no seam at the turn", () => {
  it("reads the same on both sides of phi = 0 = 2 pi, and is constant along its own spiral within a cell's worth", () => {
    const invTan = 1 / Math.tan(20 * DEG);
    for (const lnR of [-0.5, 0.3, 1.1, 2.0]) {
      expect(spiralNoise(lnR, 1e-9, invTan, 7, 5, 99)).toBeCloseTo(spiralNoise(lnR, TAU - 1e-9, invTan, 7, 5, 99), 6);
    }
    const ladder = new Ladder(20 * DEG, 0.4, 3, flocKey(1, 2, 3, 4));
    for (const r of [0.6, 2.2, 5.1, 8.7]) {
      const at = Ladder.place(r);
      expect(ladder.at(Math.log(r), 1e-9, at)).toBeCloseTo(ladder.at(Math.log(r), TAU - 1e-9, at), 6);
    }
    // Along the spiral ln R = tan(pitch) phi the noise moves far less than across it over the same distance.
    const wide = new Ladder(20 * DEG, 0.4, 6, flocKey(5, 0, 0, 1));
    let along = 0;
    let across = 0;
    for (let k = 0; k < 400; k += 1) {
      const r = 3 + 3 * ((k * 0.6180339887) % 1);
      const phi = TAU * ((k * 0.7548776662) % 1);
      const at = Ladder.place(r);
      const d = 0.2 / r; // 200 pc as an angle
      const here = wide.at(Math.log(r), phi, at);
      along += Math.abs(wide.at(Math.log(r) + d * Math.sin(20 * DEG), phi + d * Math.cos(20 * DEG), at) - here);
      across += Math.abs(wide.at(Math.log(r) + d * Math.cos(20 * DEG), phi - d * Math.sin(20 * DEG), at) - here);
    }
    expect(along).toBeLessThan(0.5 * across);
  });
});

describe("the map's bytes", () => {
  it("are the same for the same inputs, and another drawing for another seed", () => {
    const a = buildFlocChannel(G, SHAPE, 500, 900);
    const b = buildFlocChannel(geometryOf(frame()), { ...SHAPE }, 500, 900);
    expect(b).toEqual(a);
    const c = buildFlocChannel(G, { ...SHAPE, seed: SHAPE.seed + 1 }, 500, 900);
    let differing = 0;
    for (let i = 0; i < a.length; i += 1) if (a[i] !== c[i]) differing += 1;
    expect(differing).toBeGreaterThan(0.05 * a.length);
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)

  it("hold dust above 128 and light below, never 0; beyond the light's reach every byte is the patches' mean level", () => {
    const map = fullMap();
    expect(map.length).toBe(ILL_MAP.width * ILL_MAP.height);
    expect([FLOC_MAP.rings, FLOC_MAP.sectors]).toEqual([ILL_MAP.width, ILL_MAP.height]);
    const reach = lightReach(G, SHAPE);
    expect(reach).toBeCloseTo(FLOC_REACH * SHAPE.outerRadius, 12);
    const mean = 128 - Math.round(127 * (FLOC_MAP.lightFloor + 0.5 * (0.5 - FLOC_MAP.lightFloor)));
    let least = 255;
    let dustBeyond = 0;
    let offMean = 0;
    for (let j = 0; j < FLOC_MAP.sectors; j += 7) {
      for (let i = 0; i < FLOC_MAP.rings; i += 1) {
        const b = map[j * FLOC_MAP.rings + i];
        const r = ((i + 0.5) * RHI) / FLOC_MAP.rings;
        least = Math.min(least, b);
        if (b > 128 && (r > SHAPE.outerRadius + 0.5 || r < 0.25 * SHAPE.innerRadius)) dustBeyond += 1;
        if (r > reach + 0.05 && b !== mean) offMean += 1;
      }
    }
    expect(least).toBeGreaterThan(0);
    expect(dustBeyond).toBe(0);
    expect(offMean).toBe(0);
    // The decoding the GLSL does: the mean level is a patch level of a half (it changes nothing), no clump, known.
    const read = flocDecode(mean);
    expect(read.shape).toBe(0);
    expect(read.patch).toBeCloseTo(0.5, 2);
    expect(read.clump).toBe(0);
    expect(read.known).toBe(1);
    expect(flocDecode(0)).toEqual({ shape: 0, light: 0, patch: 0.5, clump: 0, known: 0 });
    expect(flocDecode(255).shape).toBeCloseTo(FLOC_MAP.shapeMax, 12);
    expect(flocLight(1)).toEqual({ patch: 1, clump: 1, known: 1 });
    expect(flocLight(0.5 * FLOC_MAP.lightFloor).known).toBeCloseTo(0.5, 12);
  });

  it("cover between 10 and 30 per cent of the disc with dust at the defaults (1 kpc to 0.7 of the outer radius, a quarter of a filament's depth or more)", () => {
    const cover = flocCover(fullMap(), G, 1, 0.7 * SHAPE.outerRadius);
    expect(cover).toBeGreaterThan(0.1);
    expect(cover).toBeLessThan(0.3);
    // ... and thins outward: less of the disc's outer part (0.7 to 1 of the outer radius) than of its middle.
    expect(flocCover(fullMap(), G, 0.7 * SHAPE.outerRadius, SHAPE.outerRadius)).toBeLessThan(0.6 * cover);
    // No dust, no cover.
    const none = buildFlocChannel(G, { ...SHAPE, density: 0, lace: 0 }, 500, 900);
    expect(flocCover(none, G, 0, RHI, 0.01, 500, 900)).toBe(0);
  });
  it("cover more of the disc at NGC 4414's tuned shape (S105 tuner N: the photograph's network over the inner two thirds), and still thin outward", () => {
    const tuned = shapeOf(P4414);
    const map = buildFlocChannel(G, tuned);
    const cover = flocCover(map, G, 1, 0.7 * tuned.outerRadius);
    expect(cover).toBeGreaterThan(flocCover(fullMap(), G, 1, 0.7 * SHAPE.outerRadius));
    expect(cover).toBeGreaterThan(0.35);
    expect(cover).toBeLessThan(0.8);
    expect(flocCover(map, G, 0.7 * tuned.outerRadius, tuned.outerRadius)).toBeLessThan(0.8 * cover);
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)
});

describe("the filaments' pitch against the published pitch", () => {
  it("is exactly the published pitch times the pitch slider for a trunk with no spread and no wander", () => {
    const strands = flocStrands(G, { ...SHAPE, density: 2, pitchSpread: 0, wiggle: 0, branches: 0, bands: 0 });
    expect(strands.length).toBeGreaterThan(100);
    for (const s of strands) {
      expect(s.kind).toBe(0);
      expect(Math.abs(strandPitch(s) - PITCH * SHAPE.pitch)).toBeLessThan(0.3);
    }
    const twice = flocStrands(G, { ...SHAPE, density: 2, pitch: 0.5, pitchSpread: 0, wiggle: 0, branches: 0, bands: 0 });
    for (const s of twice) expect(Math.abs(strandPitch(s) - PITCH * 0.5)).toBeLessThan(0.3);
  });

  it("is that pitch on the mean of the trunks at the defaults (within 3 degrees), each a short piece of a turn", () => {
    const trunks = flocStrands(G, { ...SHAPE, density: 3 }).filter((s) => s.kind === 0);
    expect(trunks.length).toBeGreaterThan(150);
    let sum = 0;
    let length = 0;
    for (const s of trunks) {
      sum += strandPitch(s) * s.length;
      length += s.length;
      expect(s.length).toBeLessThanOrEqual(1.75 * SHAPE.length + 0.07);
      // Nothing runs more than a fraction of a turn: under a quarter, outside the innermost kiloparsec.
      const r = Math.hypot(s.x[0], s.y[0]);
      if (r > 1) expect(s.length / r).toBeLessThan(TAU / 4);
    }
    expect(Math.abs(sum / length - PITCH * SHAPE.pitch)).toBeLessThan(3);
    // The branches leave them: there are some, shorter and thinner than their trunks' typical.
    const all = flocStrands(G, { ...SHAPE, density: 3 });
    expect(all.filter((s) => s.kind === 1).length).toBeGreaterThan(trunks.length);
    expect(all.filter((s) => s.kind === 2).length).toBeGreaterThan(0);
  });

  it("is the lace's too: on the map dust runs on along the drawn spiral far more often than across it or 40 degrees off it", () => {
    const map = fullMap();
    const pitch = PITCH * SHAPE.pitch * DEG;
    const dusty = (r: number, phi: number) => flocDecode(byteAt(map, r, phi)).shape >= 0.25;
    const run = (heading: number): number => {
      let from = 0;
      let on = 0;
      for (let k = 0; k < 60000; k += 1) {
        const r = 2 + 4 * ((k * 0.6180339887) % 1);
        const phi = TAU * ((k * 0.7548776662) % 1);
        if (!dusty(r, phi)) continue;
        from += 1;
        // 250 pc on, at `heading` from the direction of growing azimuth toward that of growing radius.
        const x = r * Math.cos(phi) + 0.25 * (-Math.sin(phi) * Math.cos(heading) + Math.cos(phi) * Math.sin(heading));
        const y = r * Math.sin(phi) + 0.25 * (Math.cos(phi) * Math.cos(heading) + Math.sin(phi) * Math.sin(heading));
        if (dusty(Math.hypot(x, y), (Math.atan2(y, x) + TAU) % TAU)) on += 1;
      }
      expect(from).toBeGreaterThan(3000);
      return on / from;
    };
    const along = run(pitch);
    expect(along).toBeGreaterThan(run(pitch + 90 * DEG) + 0.1);
    expect(along).toBeGreaterThan(run(pitch + 40 * DEG) + 0.04);
    expect(along).toBeGreaterThan(run(pitch - 40 * DEG) + 0.04);
  });
});

describe("where the light's patches and clumps lie", () => {
  it("draws the patches and their grains evenly over the disc out to the light's reach", () => {
    const reach = lightReach(G, SHAPE);
    for (const blobs of [flocPatches(G, SHAPE), flocGrains(G, SHAPE)]) {
      expect(blobs.length).toBeGreaterThan(2000);
      // As many inside the circle of half the area as outside it (within a tenth), none beyond the reach's margin.
      const innerHalf = blobs.filter((b) => Math.hypot(b.x, b.y) < (0.8 * reach) / Math.SQRT2).length;
      const outerHalf = blobs.filter((b) => Math.hypot(b.x, b.y) >= (0.8 * reach) / Math.SQRT2 && Math.hypot(b.x, b.y) < 0.8 * reach).length;
      expect(Math.abs(innerHalf / outerHalf - 1)).toBeLessThan(0.1);
      for (const b of blobs) expect(Math.hypot(b.x, b.y)).toBeLessThan(reach + 1.5);
    }
  });

  it("gathers the young clumps on the published stars' contrast, outside the clumps' inner radius", () => {
    const clumps = flocClumps(G, SHAPE);
    expect(clumps.length).toBeGreaterThan(300);
    let sum = 0;
    let inside = 0;
    for (const b of clumps) {
      const r = Math.hypot(b.x, b.y);
      if (r < 0.5 * SHAPE.clumpInner) inside += 1;
      sum += readField(G.pattern!, RHI, b.x, b.y);
    }
    // The pattern is 1 +- 0.35 inside 10 kpc (its mean 1): the clumps stand where it is high.
    expect(sum / clumps.length).toBeGreaterThan(1.1);
    expect(inside / clumps.length).toBeLessThan(0.01);
    // Kept to the pieces by the slider: at 0 they stand anywhere (the mean contrast at them near 1).
    const anywhere = flocClumps(G, { ...SHAPE, clumpFollow: 0 });
    let mean = 0;
    for (const b of anywhere) mean += readField(G.pattern!, RHI, b.x, b.y);
    expect(Math.abs(mean / anywhere.length - 1)).toBeLessThan(0.05);
    // On the map: a clump's level (the light above a half) only outside half the clumps' inner radius.
    const map = fullMap();
    let clumpTexels = 0;
    for (let j = 0; j < FLOC_MAP.sectors; j += 5) {
      for (let i = 0; i < FLOC_MAP.rings; i += 1) {
        if (flocDecode(map[j * FLOC_MAP.rings + i]).clump > 0.2) {
          clumpTexels += 1;
          expect(((i + 0.5) * RHI) / FLOC_MAP.rings).toBeGreaterThan(0.5 * SHAPE.clumpInner);
        }
      }
    }
    expect(clumpTexels).toBeGreaterThan(200);
  });

  it("holds the patches' level at a half on the mean over the disc, so the light swells and thins about what it was", () => {
    const map = buildFlocChannel(G, { ...SHAPE, density: 0, lace: 0, clumpDensity: 0 }, 1000, 1800);
    const reach = lightReach(G, SHAPE);
    let sum = 0;
    let weight = 0;
    let low = 0;
    let high = 0;
    for (let j = 0; j < 1800; j += 1) {
      for (let i = 0; i < 1000; i += 1) {
        const r = ((i + 0.5) * RHI) / 1000;
        if (r > 0.8 * reach) continue;
        const read = flocDecode(map[j * 1000 + i]);
        expect(read.shape).toBe(0);
        sum += read.patch * r;
        weight += r;
        if (read.patch < 0.25) low += r;
        if (read.patch > 0.75) high += r;
      }
    }
    expect(sum / weight).toBeGreaterThan(0.45);
    expect(sum / weight).toBeLessThan(0.55);
    // Patchy: a good share of the disc well under the mean and a good share well over it.
    expect(low / weight).toBeGreaterThan(0.1);
    expect(high / weight).toBeGreaterThan(0.1);
  }, 30_000); // a heavy build: 1.5-1.7 s alone, past the 5 s default under a loaded machine (the S106 review)
});

describe("the feature", () => {
  it("has every default inside its range on every template, and every control an illustrative one", () => {
    for (const template of [null, "milky_way", "ngc_4414", "another"]) {
      const defaults = illDefaults(template);
      for (const c of floc.controls) {
        const v = defaults[`floc.${c.key}`];
        expect(v, `${c.key} on ${template}`).toBeGreaterThanOrEqual(c.min);
        expect(v, `${c.key} on ${template}`).toBeLessThanOrEqual(c.max);
        expect(c.step).toBeGreaterThan(0);
        if (c.log) expect(c.min).toBeGreaterThan(0);
        expect(c.about).toMatch(/Illustrative\.$|Colour for appearance\.$/);
        for (const own of Object.values(c.perTemplate ?? {})) {
          expect(own).toBeGreaterThanOrEqual(c.min);
          expect(own).toBeLessThanOrEqual(c.max);
        }
      }
    }
    expect(new Set(floc.controls.map((c) => c.key)).size).toBe(floc.controls.length);
    for (const k of SHAPE_KEYS) expect(floc.controls.some((c) => c.key === k), k).toBe(true);
  });

  it("draws nothing on the Milky Way and on a galaxy with no template (no map is built), and the network on NGC 4414", () => {
    for (const template of [null, "milky_way"]) {
      const p = paramsOf(floc, illDefaults(template));
      expect(flocDrawn(p)).toBe(false);
      expect(flocChannel(p, FRAME)).toBeNull();
      expect(floc.map!.build(p, { template, frame: FRAME })).toEqual([null]);
    }
    expect(flocDrawn(P4414)).toBe(true);
    expect(flocChannel(P4414, null)).toBeNull();
  });

  it("hands the shared map its channel: one plane on the map's grid, the same object until a shaping value moves", () => {
    expect(floc.map!.channels).toEqual(ILL_MAP_CHANNELS.floc);
    const context = { template: "ngc_4414", frame: FRAME };
    const [plane] = floc.map!.build(P4414, context);
    expect(plane).toBeInstanceOf(Uint8Array);
    expect(plane!.length).toBe(ILL_MAP.width * ILL_MAP.height);
    // The depths, gains and colours are uniforms, and so is the mesh drawn in the march (S106 C4): the same plane.
    expect(floc.map!.build({ ...P4414, depth: 0.3, ink: 0.2, redness: 3, hardness: 1, patch: 0.2, clump: 4, young: 9, blue: 1, warmth: 1, warmRadius: 2, meshDepth: 0.5, meshCell: 400, meshArc: 0.2, meshHaze: 1, puffs: 1, puffSize: 500 }, context)[0]).toBe(plane);
    // A shaping value: another plane.
    const [moved] = floc.map!.build({ ...P4414, litScale: P4414.litScale + 40 }, context);
    expect(moved).not.toBe(plane);
    expect(moved).not.toEqual(plane);
  });

  it("is registered with its three hooks, declares no sampler, names no reserved word, and gives every uniform it declares", () => {
    expect(features().some((f) => f === floc)).toBe(true);
    expect(floc.hooks).toEqual({ dustAv: "illFlocAv", youngGain: "illFlocYoung", veil: "illFlocVeil" });
    const glsl = floc.glsl!;
    for (const name of Object.values(floc.hooks!)) expect(glsl).toContain(` ${name}(vec2 rp) {`);
    expect(glsl).not.toMatch(/sampler/);
    // `patch` is a reserved word of the GLSL the march is compiled as (a variable of that name blacked the field out).
    expect(glsl.replace(/\/\/.*$/gm, "")).not.toMatch(/\b(patch|sample|filter|input|output|common|partition|active)\b/);
    expect(glsl).toContain("illMap(rp).g");
    const declared = [...glsl.matchAll(/uniform (float|vec4) (\w+);/g)].map((m) => m[2]).sort();
    const vec4s = new Set([...glsl.matchAll(/uniform vec4 (\w+);/g)].map((m) => m[1]));
    for (const template of ["milky_way", "ngc_4414"]) {
      const values = floc.uniforms!(paramsOf(floc, illDefaults(template)), { template, frame: FRAME });
      expect(Object.keys(values).sort()).toEqual(declared);
      for (const [k, v] of Object.entries(values)) {
        if (vec4s.has(k)) expect((v as number[]).length).toBe(4);
        else expect(typeof v).toBe("number");
      }
    }
    const g = illGlsl();
    expect(g).toMatch(/float illDustAv\(vec2 rp\) \{ return .*illFlocAv\(rp\).*; \}/);
    expect(g).toMatch(/float illYoungGain\(vec2 rp\) \{ return .*illFlocYoung\(rp\).*; \}/);
    expect(g).toMatch(/vec3 illVeil\(vec2 rp\) \{ return .*illFlocVeil\(rp\).*; \}/);
    expect(illustrativeFragment(fieldFragment())).toContain("float illFlocAv(vec2 rp) {");
  });
});
