import { describe, expect, it } from "vitest";

import { gpuTimer, gpuWords } from "./gpuTimer";

// A context as the extension's spec describes it: queries whose results arrive when the test says so.
function fakeGl(withExt = true) {
  const results = new Map<object, { ready: boolean; ns: number }>();
  const state = { disjoint: false, begun: 0, deleted: 0 };
  const ext = { TIME_ELAPSED_EXT: 0x88bf, GPU_DISJOINT_EXT: 0x8fbb };
  const gl = {
    QUERY_RESULT: 0x8866,
    QUERY_RESULT_AVAILABLE: 0x8867,
    getExtension: (name: string) => (withExt && name === "EXT_disjoint_timer_query_webgl2" ? ext : null),
    createQuery: () => {
      const q = {};
      results.set(q, { ready: false, ns: 0 });
      return q as WebGLQuery;
    },
    deleteQuery: () => void (state.deleted += 1),
    beginQuery: () => void (state.begun += 1),
    endQuery: () => undefined,
    getQueryParameter: (q: WebGLQuery, p: number) => (p === 0x8867 ? results.get(q)!.ready : results.get(q)!.ns),
    getParameter: (p: number) => (p === ext.GPU_DISJOINT_EXT ? state.disjoint : null),
  };
  return { gl, results, state };
}

describe("the GPU's time for the march (S67, D227 R6)", () => {
  it("reads a query back once the GPU has it, in ms", () => {
    const { gl, results } = fakeGl();
    const t = gpuTimer(gl as never);
    expect(t.available).toBe(true);
    t.begin();
    t.end();
    expect(t.poll()).toBeNull();
    const [q] = [...results.keys()];
    results.set(q, { ready: true, ns: 4_250_000 });
    expect(t.poll()).toBeCloseTo(4.25, 12);
    expect(gpuWords(t.poll(), t.available)).toBe("GPU 4.3 ms");
  });

  it("drops what a disjoint event spoiled, and keeps one query open at a time", () => {
    const { gl, results, state } = fakeGl();
    const t = gpuTimer(gl as never);
    t.begin();
    t.begin();
    expect(state.begun).toBe(1);
    t.end();
    const [q] = [...results.keys()];
    results.set(q, { ready: true, ns: 9e9 });
    state.disjoint = true;
    expect(t.poll()).toBeNull();
    expect(state.deleted).toBe(1);
  });

  it("says so where the extension is absent", () => {
    const t = gpuTimer(fakeGl(false).gl as never);
    expect(t.available).toBe(false);
    t.begin();
    t.end();
    expect(t.poll()).toBeNull();
    expect(gpuWords(null, false)).toBe("GPU time not available");
    expect(gpuTimer(null).available).toBe(false);
  });
});
