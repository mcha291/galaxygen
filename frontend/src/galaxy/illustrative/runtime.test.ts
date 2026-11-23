import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { readFileSync } from "node:fs";

import { ILL_MAP, memoOn, wouldBuild } from "./feature";
import { floc } from "./floc";
import {
  ILL_SETTLE_MS,
  createRuntime,
  illDefaults,
  illEffective,
  illStale,
  registerFeature,
  releaseRuntime,
  releaseShared,
  sharedBytes,
  updateRuntime,
} from "./index";

// S105 fix R1 and R5: the runtime's debounce contract and its release. A fake feature owns channel 1 (the flocculent
// network's, set aside here) with one plane-shaping control and one uniform-only control, and counts its builds.
const SIZE = ILL_MAP.width * ILL_MAP.height;
let builds = 0;
const plane = memoOn((shape: unknown) => {
  builds += 1;
  const out = new Uint8Array(SIZE);
  for (let i = 0; i < SIZE; i += 997) out[i] = ((shape as number) * 13 + i) & 255;
  return out;
});
const ctx = { template: null, frame: null };
let drop: () => void = () => {};
const flocMap = floc.map;

beforeEach(() => {
  floc.map = undefined;
  drop = registerFeature({
    id: "fakeshape",
    label: "fake shape",
    about: "a test's",
    controls: [
      { key: "shape", label: "shape", min: 0, max: 10, step: 1, default: 1, about: "reshapes the plane" },
      { key: "gain", label: "gain", min: 0, max: 10, step: 0.1, default: 1, about: "a uniform" },
    ],
    glsl: "  uniform float illFakeshapeGain;\n",
    map: { channels: [1], build: (p) => [plane(p.shape)] },
    uniforms: (p) => ({ illFakeshapeGain: p.gain }),
  });
  releaseShared();
  builds = 0;
});

afterEach(() => {
  releaseShared();
  drop();
  floc.map = flocMap;
});

const mapBytes = (rt: { uniforms: Record<string, { value: unknown }> }) => (rt.uniforms.illMapTex.value as { image: { data: Uint8Array } }).image.data;

describe("the debounce (S105 fix R1): uniforms at once, a plane rebuilt once after the sliders settle", () => {
  it("probes a memo without building it", () => {
    const before = builds;
    expect(wouldBuild(() => plane(42))).toBe(true);
    expect(builds).toBe(before);
    plane(42);
    expect(wouldBuild(() => plane(42))).toBe(false);
    expect(builds).toBe(before + 1);
  });

  it("draws a uniform-only change at once, holds a plane-shaping drag at the settled values, and builds once when it settles", () => {
    expect(ILL_SETTLE_MS).toBeGreaterThanOrEqual(200);
    expect(ILL_SETTLE_MS).toBeLessThanOrEqual(300);
    const base = illDefaults(null);
    const rt = createRuntime(base, ctx);
    expect(builds).toBe(1);
    expect(illStale(base, ctx)).toBe(false);

    // A uniform-only move: live at once, nothing held, nothing built.
    const gain = { ...base, "fakeshape.gain": 2.5 };
    const g = illEffective(gain, base, ctx);
    expect(g.held).toEqual([]);
    expect(g.ill).toBe(gain);
    const v0 = rt.version;
    updateRuntime(rt, g.ill, ctx);
    expect(rt.uniforms.illFakeshapeGain.value).toBe(2.5);
    expect(rt.version).toBe(v0 + 1);
    expect(builds).toBe(1);

    // A drag of the shaping slider: six moves before it settles, each held at the settled values, none built.
    let settled: Record<string, number> = gain;
    for (let s = 2; s <= 7; s += 1) {
      const live = { ...settled, "fakeshape.shape": s };
      const e = illEffective(live, settled, ctx);
      expect(e.held).toEqual(["fakeshape"]);
      expect(e.ill["fakeshape.shape"]).toBe(1);
      expect(illStale(e.ill, ctx)).toBe(false);
      updateRuntime(rt, e.ill, ctx);
      expect(builds).toBe(1);
      if (s === 7) settled = live;
    }
    // Settled: drawn as it stands, stale until the one build, then not.
    const e = illEffective(settled, settled, ctx);
    expect(e.held).toEqual([]);
    expect(illStale(e.ill, ctx)).toBe(true);
    updateRuntime(rt, e.ill, ctx);
    expect(builds).toBe(2);
    expect(illStale(e.ill, ctx)).toBe(false);
    expect(mapBytes(rt)[997 * 4 + 1]).toBe((7 * 13 + 997) & 255);
    // the other features' (lanes, arms) uniforms ride on at once: nothing of theirs is held without a frame
    expect(illEffective({ ...settled, "lanes.depth": 3, "arms.floor": 0.2 }, settled, ctx).held).toEqual([]);
  });

  it("is wired so: the settled copy fed to the runtime, the mark passed to the panel", () => {
    const tab = readFileSync(new URL("../GalaxyTab.tsx", import.meta.url), "utf-8");
    expect(tab).toContain("useDebounced(illParams, ILL_SETTLE_MS");
    expect(tab).toContain("illEffective(illParams, illSettled, illContext)");
    expect(tab).toContain("updateRuntime(illRuntime, illDrawnParams, illContext)");
    expect(tab).toContain("illPending={illPending}");
    expect(tab).toContain("return () => releaseRuntime(illRuntime);");
  });
});

describe("the release (S105 fix R5): nothing of the layer held after the look leaves illustrative", () => {
  it("frees the shared buffer and the cached planes, and a new runtime builds the same bytes", () => {
    const base = { ...illDefaults(null), "fakeshape.shape": 4 };
    const a = createRuntime(base, ctx);
    const bytesA = mapBytes(a).slice();
    expect(sharedBytes()).toBe(SIZE * 4);
    expect(builds).toBe(1);
    releaseRuntime(a);
    expect(sharedBytes()).toBe(0);
    expect((a.uniforms.illMapTex.value as { image: { width: number } }).image.width).toBe(1);
    // the feature's cache went too: the next runtime builds again
    expect(wouldBuild(() => plane(4))).toBe(true);
    const b = createRuntime(base, ctx);
    expect(builds).toBe(2);
    expect(sharedBytes()).toBe(SIZE * 4);
    const bytesB = mapBytes(b);
    expect(bytesB.length).toBe(bytesA.length);
    expect(Buffer.from(bytesB).equals(Buffer.from(bytesA))).toBe(true);
  });
});

describe("the knots layer's stand-in texture (S105 fix R2)", () => {
  it("is one RGBA texel of bytes, its type the bytes' own, and is released with the material", async () => {
    const { DataTexture, RGBAFormat, ShaderMaterial, UnsignedByteType } = await import("three");
    const { disposeKnotsMaterial, knotsBlank } = await import("./knotsLayer");
    const blank = knotsBlank();
    expect(blank).toBeInstanceOf(DataTexture);
    expect(blank.image.data).toBeInstanceOf(Uint8Array);
    if (!blank.image.data) throw new Error("no data");
    expect(blank.image.data.length).toBe(4);
    expect(blank.type).toBe(UnsignedByteType);
    expect(blank.format).toBe(RGBAFormat);
    const material = new ShaderMaterial({ userData: { blank } });
    let released = 0;
    blank.addEventListener("dispose", () => (released += 1));
    material.addEventListener("dispose", () => (released += 1));
    disposeKnotsMaterial(material);
    expect(released).toBe(2);
  });
});
