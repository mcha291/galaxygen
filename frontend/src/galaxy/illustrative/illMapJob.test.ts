// S107 (the sliders' stall): the illustrative map built in a worker. Proved here against a stand-in Worker that runs the
// worker's own job (illMapJob.ts handle) in a module graph of its own - its own memos, as a real worker has - with every
// message structured-cloned across and its buffers transferred: (1) the planes and the sparkle that arrive are the main
// thread's own synchronous build, to the byte, the planes transferred, not copied, and nothing is built on the main
// thread after they arrive; (2) a superseded request's answer never stands for newer parameters and channels of two
// parameter sets are never composed together; (3) a failed job is reported and the previous map kept; (4) a release
// drops the answers in flight; (5) without a Worker everything builds on this thread as before (the tests' own path).
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { IllFrame } from "./feature";
import type { JobAnswer, JobMessage } from "./illMapJob";

const TAU = 2 * Math.PI;
const RINGS = 60;
const SECTORS = 360;
const RHI = 30;

/** A galaxy for the tests: two arm pieces for the skeleton, stellar and gas spirals for the arms and the network. */
function frame(): IllFrame {
  const gas = new Float64Array(RINGS * SECTORS);
  const pattern = new Float64Array(RINGS * SECTORS);
  const profile = new Float64Array(RINGS);
  const k = 1 / Math.tan((20 * Math.PI) / 180);
  for (let i = 0; i < RINGS; i += 1) {
    const r = ((i + 0.5) * RHI) / RINGS;
    profile[i] = 40 * Math.exp(-r / 4);
    for (let j = 0; j < SECTORS; j += 1) {
      const phi = ((j + 0.5) * TAU) / SECTORS;
      const on = r < 14 ? 1 : 0;
      gas[i * SECTORS + j] = 1 + on * 0.3 * Math.cos(3 * (phi - k * Math.log(r)));
      pattern[i * SECTORS + j] = 1 + on * 0.35 * Math.cos(2 * (phi - k * Math.log(r)));
    }
  }
  const col = (v: number[]) => Float64Array.from(v);
  return {
    header: { scalars: { pitch_angle: 20, thin_disc_scale_length: 2.6 }, grid: { axes: { R: { n: RINGS, hi: RHI }, phi: { n: SECTORS } } } },
    arrays: {
      gas_density_contrast: gas,
      pattern_density_contrast: pattern,
      gas_surface_density: profile,
      arm_piece_chain: col([0, 1]),
      arm_piece_order: col([0, 0]),
      arm_piece_start_radius: col([3, 3]),
      arm_piece_start_azimuth: col([0, Math.PI]),
      arm_piece_pitch: col([13, 13]),
      arm_piece_extent: col([5, 5]),
      arm_piece_join: col([0, 0]),
    },
  };
}

type Job = typeof import("./illMapJob");

/** A stand-in Worker: the worker's job in its own module graph, messages cloned across with their transfers. */
class FakeWorker {
  static made: FakeWorker[] = [];
  static job: Job;
  static failing = false;
  onmessage: ((event: { data: JobAnswer }) => void) | null = null;
  onerror: ((event: { preventDefault(): void }) => void) | null = null;
  readonly inbox: JobMessage[] = [];
  readonly state = new FakeWorker.job.MapJobState();
  constructor(
    readonly url: URL,
    readonly options: WorkerOptions,
  ) {
    FakeWorker.made.push(this);
  }
  postMessage(message: JobMessage, transfer: Transferable[]) {
    this.inbox.push(structuredClone(message, { transfer }));
  }
  /** Runs the oldest message as the worker does (illMap.worker.ts) and answers it, if it is answered. */
  deliver() {
    const message = this.inbox.shift()!;
    const out = FakeWorker.failing && message.kind === "map" ? { answer: { id: message.id, kind: "error" as const, message: "a builder threw" }, transfer: [] } : FakeWorker.job.handle(this.state, message);
    if (!out) return;
    const transfer = out.transfer;
    const data = structuredClone(out.answer, { transfer });
    for (const b of transfer) expect(b.byteLength).toBe(0); // transferred, not copied
    this.onmessage?.({ data });
  }
  deliverAll() {
    while (this.inbox.length) this.deliver();
  }
  terminate() {}
}

const F = frame();
const bytes = (a: Uint8Array | null) => (a ? Buffer.from(a) : null);
const same = (a: Uint8Array | null, b: Uint8Array | null) => (a === null || b === null ? a === b : Buffer.from(a).equals(Buffer.from(b)));

/** The main thread's modules, a fresh graph with the stand-in Worker; and a reference graph that builds everything here. */
async function graphs() {
  vi.resetModules();
  FakeWorker.job = await import("./illMapJob");
  const workerFeature = await import("./feature");
  vi.resetModules();
  vi.stubGlobal("Worker", FakeWorker);
  const main = await import("./index");
  const client = await import("./illMapClient");
  const feature = await import("./feature");
  vi.resetModules();
  const ref = await import("./index");
  const refSparkle = await import("./sparkleJob");
  return { main, client, feature, workerFeature, ref, refSparkle };
}

describe("the illustrative map's worker (S107: illMapJob.ts, illMapClient.ts)", () => {
  beforeEach(() => {
    FakeWorker.made = [];
    FakeWorker.failing = false;
  });
  afterEach(() => vi.unstubAllGlobals());

  it("puts the planes the worker built in the main thread's caches, to the byte, transferred; the main thread builds no plane", async () => {
    const { main, client, feature, workerFeature, ref } = await graphs();
    for (const template of ["milky_way", "ngc_4414"]) {
      const ill = main.illDefaults(template);
      const ctx = { template, frame: F };
      const rt = main.createRuntime(ill, { template, frame: null });
      expect(main.stepRuntime(rt, ill, ctx)).toBe("asked");
      expect(client.illJobsPending()).toBe(1);
      const w = FakeWorker.made[0];
      expect(w.url.pathname.endsWith("/illMap.worker.ts")).toBe(true);
      expect(w.options.type).toBe("module");
      w.deliverAll();
      expect(client.illJobsPending()).toBe(0);
      expect(client.illMapAnswered(client.illMapKey(ill, ctx))).toBe(true);
      // every plane now in the main thread's caches: nothing of the map would be built here
      expect(feature.wouldBuild(() => main.illMapPlanes(ill, ctx))).toBe(false);
      const planes = main.illMapPlanes(ill, ctx);
      const expected = ref.illMapPlanes(ill, ctx);
      expect(planes.map((p) => p !== null)).toEqual(expected.map((p) => p !== null));
      for (let c = 0; c < 4; c += 1) expect(same(planes[c], expected[c]), `${template} channel ${c}`).toBe(true);
      expect(planes.map((p) => (p ? "x" : "-")).join("")).toBe(template === "milky_way" ? "x-xx" : "xxxx");
      expect(planes.some((p) => p !== null)).toBe(true);
      // the worker's own copies went with the answer (transferred)
      for (const name of ["lanes.plane", "floc.channel"]) {
        const held = workerFeature.memoHeld(name)?.value as Uint8Array | null | undefined;
        if (held) expect(held.byteLength, name).toBe(0);
      }
      // the runtime drawn from the caches: the uniforms the main thread's own build gives, the composed map's bytes too
      expect(main.stepRuntime(rt, ill, ctx)).toBe("drawn");
      const refValues = ref.illUniformValues(ill, ctx);
      for (const [k, v] of Object.entries(refValues)) {
        if (k === "illMapTex") continue;
        expect(rt.uniforms[k].value, `${template} ${k}`).toEqual(v);
      }
      const got = (rt.uniforms.illMapTex.value as { image: { data: Uint8Array } }).image.data;
      const refMap = (refValues.illMapTex as { image: { data: Uint8Array } }).image.data;
      expect(Buffer.from(got).equals(Buffer.from(refMap))).toBe(true);
    }
    expect(client.illJobCounts().here).toBe(0);
    expect(client.illJobCounts().skipped).toBe(0);
  }, 120_000);

  it("never lets a superseded answer stand for newer parameters, nor composes channels of two parameter sets", async () => {
    const { main, client, feature, ref } = await graphs();
    const base = main.illDefaults("milky_way");
    const ctx = { template: "milky_way", frame: F };
    const A = { ...base, "lanes.width": 60, "arms.skelpitch": 1.2 };
    const B = { ...base, "lanes.width": 70 };
    const C = { ...base, "lanes.width": 80, "arms.skelpitch": 0.8 };
    const rt = main.createRuntime(base, { template: "milky_way", frame: null });
    expect(main.stepRuntime(rt, A, ctx)).toBe("asked"); // posted
    expect(main.stepRuntime(rt, B, ctx)).toBe("asked"); // waits
    expect(main.stepRuntime(rt, C, ctx)).toBe("asked"); // replaces B, which never runs
    expect(client.illJobCounts().replaced).toBe(1);
    const w = FakeWorker.made[0];
    const before = rt.uniforms.illMapTex.value;
    w.deliver(); // A's answer, C still owed
    // A's planes fill the caches under A's inputs only: at C every changed channel would still be built...
    expect(feature.wouldBuild(() => main.illMapPlanes(C, ctx))).toBe(true);
    expect(feature.wouldBuild(() => main.illMapPlanes(A, ctx))).toBe(false);
    // ...so the runtime, asked for C, keeps the map it had (no channel of A's composed for C)
    expect(main.stepRuntime(rt, C, ctx)).toBe("asked");
    expect(rt.uniforms.illMapTex.value).toBe(before);
    w.deliver(); // C's
    expect(w.inbox.length).toBe(0);
    expect(client.illJobCounts().posted).toBe(2);
    expect(main.stepRuntime(rt, C, ctx)).toBe("drawn");
    const got = (rt.uniforms.illMapTex.value as { image: { data: Uint8Array } }).image.data;
    const refMap = (ref.illUniformValues(C, ctx).illMapTex as { image: { data: Uint8Array } }).image.data;
    expect(Buffer.from(got).equals(Buffer.from(refMap))).toBe(true);
    // a return to A asks again (C's seeds replaced A's), and is answered from the worker's builds, never from A's old ones here
    expect(main.stepRuntime(rt, A, ctx)).toBe("asked");
    w.deliver();
    expect(main.stepRuntime(rt, A, ctx)).toBe("drawn");
    const gotA = (rt.uniforms.illMapTex.value as { image: { data: Uint8Array } }).image.data;
    const refA = (ref.illUniformValues(A, ctx).illMapTex as { image: { data: Uint8Array } }).image.data;
    expect(Buffer.from(gotA).equals(Buffer.from(refA))).toBe(true);
    expect(client.illJobCounts().here).toBe(0);
  }, 120_000);

  it("builds the sparkle's points in the worker, the same bits as the layer's own build, reading the lanes it kept", async () => {
    const { main, client, ref, refSparkle } = await graphs();
    const ill = main.illDefaults("milky_way");
    const ctx = { template: "milky_way", frame: F };
    const rt = main.createRuntime(ill, { template: "milky_way", frame: null });
    expect(main.stepRuntime(rt, ill, ctx)).toBe("asked");
    FakeWorker.made[0].deliverAll();
    expect(main.stepRuntime(rt, ill, ctx)).toBe("drawn");
    const params = main.paramsOf(main.features().find((f) => f.id === "arms")!, ill);
    expect(params.sparkle ?? 0).toBeGreaterThan(0);
    expect(params.sparkleavoid ?? 0).toBeGreaterThan(0);
    const tex = rt.uniforms.illMapTex.value as { image: { data: Uint8Array }; userData: { illPlanes: (Uint8Array | null)[] } };
    const lanesPlane = tex.userData.illPlanes[0];
    expect(lanesPlane).not.toBeNull();
    let got: unknown = "none";
    client.requestSparkle("k1", params, ctx, { plane: lanesPlane, rgba: tex.image.data }, (p) => (got = p));
    expect(got).toBe("none"); // asked, not built here
    FakeWorker.made[0].deliverAll();
    const refTex = ref.illUniformValues(ill, ctx).illMapTex as { image: { data: Uint8Array } };
    const want = refSparkle.sparklePoints(params, F, "milky_way", refTex.image.data);
    expect(want).not.toBeNull();
    const g = got as { positions: Float32Array; weight: Float32Array; radius: Float32Array };
    for (const k of ["positions", "weight", "radius"] as const) expect(Buffer.from(g[k].buffer, g[k].byteOffset, g[k].byteLength).equals(Buffer.from(want![k].buffer, want![k].byteOffset, want![k].byteLength)), k).toBe(true);
    // kept: asked again, heard at once
    let again: unknown = null;
    client.requestSparkle("k1", params, ctx, { plane: lanesPlane, rgba: tex.image.data }, (p) => (again = p));
    expect(again).toBe(got);
    expect(client.illJobCounts().here).toBe(0);
  }, 120_000);

  it("reports a failed job and keeps the previous map; a release drops the answers in flight", async () => {
    const { main, client, feature } = await graphs();
    const base = main.illDefaults("milky_way");
    const ctx = { template: "milky_way", frame: F };
    const rt = main.createRuntime(base, { template: "milky_way", frame: null });
    main.stepRuntime(rt, base, ctx);
    FakeWorker.made[0].deliverAll();
    expect(main.stepRuntime(rt, base, ctx)).toBe("drawn");
    const drawn = rt.uniforms.illMapTex.value;
    const moved = { ...base, "lanes.width": 90 };
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    FakeWorker.failing = true;
    expect(main.stepRuntime(rt, moved, ctx)).toBe("asked");
    FakeWorker.made[0].deliverAll();
    expect(client.illJobCounts().failed).toBe(1);
    expect(client.illJobCounts().lastError).toBe("a builder threw");
    expect(warn).toHaveBeenCalledTimes(1);
    expect(main.stepRuntime(rt, moved, ctx)).toBe("failed"); // not asked again, nothing built here, the map kept
    expect(rt.uniforms.illMapTex.value).toBe(drawn);
    expect(FakeWorker.made[0].inbox.length).toBe(0);
    warn.mockRestore();
    FakeWorker.failing = false;
    // a release with a job in flight: its answer dropped, nothing put in the caches
    const other = { ...base, "lanes.width": 95 };
    expect(main.stepRuntime(rt, other, ctx)).toBe("asked");
    main.releaseRuntime(rt);
    FakeWorker.made[0].deliverAll(); // the job's answer, then the release
    expect(client.illJobCounts().dropped).toBe(1);
    expect(feature.wouldBuild(() => main.illMapPlanes(other, ctx))).toBe(true);
    expect(client.illJobsPending()).toBe(0);
  }, 120_000);

  it("without a Worker builds everything on this thread, as before (vitest's own path, and SSR)", async () => {
    vi.resetModules();
    const main = await import("./index");
    const client = await import("./illMapClient");
    expect(typeof Worker).toBe("undefined");
    expect(client.illWorkerAvailable()).toBe(false);
    const ill = main.illDefaults("milky_way");
    const rt = main.createRuntime(ill, { template: "milky_way", frame: null });
    expect(main.stepRuntime(rt, ill, { template: "milky_way", frame: F })).toBe("drawn");
    expect(main.illStale(ill, { template: "milky_way", frame: F })).toBe(false);
    let got: unknown = "none";
    client.requestSparkle("k", main.paramsOf(main.features().find((f) => f.id === "arms")!, ill), { template: "milky_way", frame: F }, null, (p) => (got = p));
    expect(got).not.toBe("none"); // built here, at once
  }, 120_000);
});
