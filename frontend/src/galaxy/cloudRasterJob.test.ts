// S78 (R5): the clouds' raster built in a worker. Three things are proved here. (1) The worker's float-to-half (three's
// own module, three/src/extras/DataUtils.js, so the worker's chunk does not carry all of three) is DataUtils.toHalfFloat
// from "three", value for value. (2) The worker's job (rasterJob, its message handler's core), run on the request as it
// crosses the boundary (the columns copied, then structured-cloned with their buffers transferred, and the answer
// cloned back with its A_V and halves transferred), is keptCloudRaster's raster to the bit (Object.is per element) on
// the hoist test's synthetic censuses. (3) The main side's queue (cloudRasterClient.ts) against a stand-in Worker: one
// worker for the page, a newer raster replacing the waiting one, a superseded answer dropped, what arrives kept (a
// switch back synchronous), and a failed worker falling back to this thread.
import { DataUtils } from "three";
import { toHalfFloat } from "three/src/extras/DataUtils.js";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { syntheticCensus } from "./cloudCensus.fixture";
import { type CloudColumns, type KeptRaster, type RasterShape, keptCloudRaster, rasterKey } from "./cloudOpacity";
import { type RasterAnswer, type RasterMessage, RASTER_COLUMNS, answerTransfer, rasterJob, rasterRequest } from "./cloudRasterJob";

const f32 = new Float32Array(1);
const u32 = new Uint32Array(f32.buffer);
const fromBits = (bits: number) => {
  u32[0] = bits >>> 0;
  return f32[0];
};

describe("the worker's toHalf is three's DataUtils.toHalfFloat (S78, R5)", () => {
  beforeEach(() => {
    vi.spyOn(console, "warn").mockImplementation(() => undefined); // both warn past 65504, alike
  });
  afterEach(() => vi.restoreAllMocks());

  it("on every half's own value, the midpoints between neighbours and one float32 ulp either side, the edges, and 100 000 random floats", () => {
    const values: number[] = [0, -0, Infinity, -Infinity, Number.NaN, 65504, -65504, 65505, 65519, 65520, 65536, 1e30, -1e30, Number.MAX_VALUE, -Number.MAX_VALUE];
    // float32 denormals and the half's denormal / normal edges: 2^-24 (the least half), 2^-25 (half of it), 2^-14
    for (const e of [-149, -148, -127, -126, -125, -26, -25, -24, -23, -15, -14, -13, 15, 16]) {
      const v = 2 ** e;
      values.push(v, -v, Math.fround(v * (1 + 2 ** -23)), Math.fround(v * (1 - 2 ** -24)));
    }
    values.push(fromBits(0x00000001), fromBits(0x007fffff), fromBits(0x00800000), fromBits(0x80000001), fromBits(0x7fc00000), fromBits(0xffc00001));
    // every half, as the float it stands for, and the midpoint to the next one up, with a float32 ulp either side
    for (let h = 0; h < 0x7c00; h += 1) {
      for (const sign of [1, -1]) {
        const v = DataUtils.fromHalfFloat(h) * sign;
        const w = DataUtils.fromHalfFloat(h + 1) * sign;
        const mid = Math.fround((v + w) / 2);
        f32[0] = mid;
        const bits = u32[0];
        values.push(v, mid, fromBits(bits + 1), fromBits(bits - 1));
      }
    }
    // random float32 bit patterns (every exponent, NaNs among them) and random doubles across the half's range
    let t = 207;
    const rand = () => {
      t = (t + 0x6d2b79f5) >>> 0;
      let x = Math.imul(t ^ (t >>> 15), 1 | t);
      x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
      return (x ^ (x >>> 14)) >>> 0;
    };
    for (let k = 0; k < 50_000; k += 1) values.push(fromBits(rand()));
    for (let k = 0; k < 50_000; k += 1) values.push(((rand() / 4294967296) - 0.5) * 2 * 2 ** ((rand() % 40) - 26));
    expect(values.length).toBeGreaterThan(220_000);
    let differ = 0;
    for (const v of values) if (!Object.is(toHalfFloat(v), DataUtils.toHalfFloat(v))) differ += 1;
    expect(differ).toBe(0);
  });
});

/** The request as the worker receives it: copied, then structured-cloned across with its buffers transferred. */
function acrossToWorker(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape) {
  const { request, transfer } = rasterRequest(clouds, rLo, rHi, width, height, shape);
  const message: RasterMessage = { id: 1, request };
  const got = structuredClone(message, { transfer });
  for (const buffer of transfer) expect(buffer.byteLength).toBe(0); // transferred, not copied
  return got.request;
}

/** The answer as the main side receives it: cloned back, the A_V and halves transferred. */
function acrossToMain(raster: KeptRaster): KeptRaster {
  const transfer = answerTransfer(raster);
  const got = structuredClone({ id: 1, raster, ms: 0 } satisfies RasterAnswer, { transfer });
  for (const buffer of transfer) expect(buffer.byteLength).toBe(0);
  return got.raster;
}

function expectSameRaster(got: KeptRaster, want: KeptRaster) {
  for (const k of ["top", "width", "height", "census", "held", "outside", "split"] as const) expect(Object.is(got[k], want[k]), k).toBe(true);
  expect(got.av).toBeInstanceOf(Float32Array);
  expect(got.halves).toBeInstanceOf(Uint16Array);
  expect(got.av.length).toBe(want.av.length);
  expect(got.halves.length).toBe(want.halves.length);
  let differ = 0;
  for (let t = 0; t < want.av.length; t += 1) if (!Object.is(got.av[t], want.av[t])) differ += 1;
  for (let t = 0; t < want.halves.length; t += 1) if (got.halves[t] !== want.halves[t]) differ += 1;
  expect(differ).toBe(0);
}

const SHAPES: [string, RasterShape][] = [
  ["round, no cap", {}],
  ["the published ellipses, the Milky Way's cap", { elongation: 1, verticalCap: 1.7627 * 0.034 }],
  ["half the elongation", { elongation: 0.5, verticalCap: 0.08 }],
];

describe("the worker's job across the boundary is keptCloudRaster's raster to the bit (S78, R5)", () => {
  for (const [name, shape] of SHAPES) {
    it(`on a 600-cloud float32 census over a 0-20 kpc raster, ${name}`, () => {
      const clouds = syntheticCensus(600, 78, 0, 20, true);
      // capBytes 0: built here, never taken from the kept rasters
      const want = keptCloudRaster(clouds, 0, 20, 200, 180, shape, DataUtils.toHalfFloat, 0);
      const request = acrossToWorker(clouds, 0, 20, 200, 180, shape);
      for (const column of RASTER_COLUMNS) expect(request.clouds[column]).toBeInstanceOf(Float32Array);
      const got = acrossToMain(rasterJob(request));
      expect(want.split).toBeGreaterThan(100);
      expectSameRaster(got, want);
    });
  }

  it("on a float64 census over a raster that starts off the centre, at odd texel counts", () => {
    const clouds = syntheticCensus(400, 4414, 0.6, 15.3, false);
    for (const [, shape] of SHAPES) {
      const want = keptCloudRaster(clouds, 0.6, 15.3, 157, 211, shape, DataUtils.toHalfFloat, 0);
      expectSameRaster(acrossToMain(rasterJob(acrossToWorker(clouds, 0.6, 15.3, 157, 211, shape))), want);
    }
  });

  it("copies a column that is a view into a larger buffer as its own range only, and leaves absent columns out", () => {
    const clouds = syntheticCensus(50, 3, 0, 20, true);
    const big = new Float32Array(1000);
    big.set(clouds.cloud_radius as Float32Array, 300);
    const viewed = { ...clouds, cloud_radius: big.subarray(300, 350), cloud_axis_ratio: undefined, cloud_angle: undefined };
    const { request, transfer } = rasterRequest(viewed, 0, 20, 40, 36, {});
    expect((request.clouds.cloud_radius as Float32Array).buffer.byteLength).toBe(200);
    expect(transfer.length).toBe(5);
    expect("cloud_axis_ratio" in request.clouds).toBe(false);
    expectSameRaster(rasterJob(request), keptCloudRaster(viewed, 0, 20, 40, 36, {}, DataUtils.toHalfFloat, 0));
  });
});

/** A stand-in for the browser's Worker: messages held until `deliver` runs the worker's job on them, cloned both ways. */
class FakeWorker {
  static made: FakeWorker[] = [];
  onmessage: ((event: { data: RasterAnswer }) => void) | null = null;
  onerror: ((event: { preventDefault(): void }) => void) | null = null;
  readonly inbox: RasterMessage[] = [];
  terminated = false;
  constructor(
    readonly url: URL,
    readonly options: WorkerOptions,
  ) {
    FakeWorker.made.push(this);
  }
  postMessage(message: RasterMessage, transfer: Transferable[]) {
    this.inbox.push(structuredClone(message, { transfer }));
  }
  /** Runs the oldest message's job as the worker does and answers it. */
  deliver() {
    const { id, request } = this.inbox.shift()!;
    const raster = rasterJob(request);
    this.onmessage?.({ data: structuredClone({ id, raster, ms: 1 }, { transfer: answerTransfer(raster) }) });
  }
  terminate() {
    this.terminated = true;
  }
}

describe("the main side's queue (cloudRasterClient.ts) against a stand-in Worker (S78, R5)", () => {
  const grid = [0, 20, 60, 54] as const;
  const shapes: RasterShape[] = [{}, { elongation: 1, verticalCap: 0.06 }, { elongation: 0.5 }];
  const clouds = syntheticCensus(200, 9, 0, 20, true);
  const keyOf = (shape: RasterShape) => rasterKey(clouds, ...grid, shape);
  const makeOf = (shape: RasterShape) => () => rasterRequest(clouds, ...grid, shape);

  beforeEach(() => {
    FakeWorker.made = [];
    vi.resetModules();
    vi.stubGlobal("Worker", FakeWorker);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("one worker; a newer raster replaces the waiting one, the superseded answer is dropped, what arrives is kept", async () => {
    const client = await import("./cloudRasterClient");
    const opacity = await import("./cloudOpacity");
    expect(client.rasterWorkerAvailable()).toBe(true);
    const [k1, k2, k3] = shapes.map(keyOf);
    const heard: { key: string; worker: boolean; raster: KeptRaster }[] = [];
    client.startRaster(k1, makeOf(shapes[0]));
    const stop1 = client.listenRaster(k1, (a) => heard.push(a));
    client.startRaster(k2, makeOf(shapes[1])); // waits
    client.startRaster(k3, makeOf(shapes[2])); // replaces k2, which never runs
    stop1(); // the field moved on from k1 (its effect's cleanup)
    client.listenRaster(k3, (a) => heard.push(a));
    expect(FakeWorker.made.length).toBe(1);
    const w = FakeWorker.made[0];
    expect(w.url.pathname.endsWith("/cloudRaster.worker.ts")).toBe(true);
    expect(w.options.type).toBe("module");
    expect(w.inbox.length).toBe(1); // only k1 posted
    w.deliver(); // k1's answer: superseded, dropped; k3 posted
    expect(heard.length).toBe(0);
    expect(opacity.keptRasterHit(k1)).toBeUndefined();
    expect(w.inbox.length).toBe(1);
    w.deliver();
    expect(heard.length).toBe(1);
    expect(heard[0].key).toBe(k3);
    expect(heard[0].worker).toBe(true);
    expectSameRaster(heard[0].raster, keptCloudRaster(clouds, ...grid, shapes[2], DataUtils.toHalfFloat, 0));
    expect(client.rasterWorkerCounts()).toEqual({ posted: 2, answered: 2, stale: 1, replaced: 1 });
    // kept: a switch back takes it at once, no job posted
    expect(opacity.keptRasterHit(k3)).toBe(heard[0].raster);
    expect(opacity.keptRasterBytes()).toBe(heard[0].raster.av.byteLength + heard[0].raster.halves.byteLength);
    // asked for again and heard at once (the answer came before the field's effect listened)
    let again: KeptRaster | null = null;
    client.listenRaster(k3, (a) => (again = a.raster));
    expect(again).toBe(heard[0].raster);
    expect(FakeWorker.made.length).toBe(1);
  });

  it("asking again for the running raster posts nothing more, and drops the one waiting", async () => {
    const client = await import("./cloudRasterClient");
    const [k1, k2] = shapes.map(keyOf);
    let got = 0;
    client.startRaster(k1, makeOf(shapes[0]));
    client.startRaster(k2, makeOf(shapes[1]));
    client.startRaster(k1, makeOf(shapes[0]));
    client.listenRaster(k1, () => (got += 1));
    const w = FakeWorker.made[0];
    w.deliver();
    expect(got).toBe(1);
    expect(w.inbox.length).toBe(0);
    expect(client.rasterWorkerCounts()).toEqual({ posted: 1, answered: 1, stale: 0, replaced: 1 });
  });

  it("a failed worker: the running job built on this thread, and every later one", async () => {
    const client = await import("./cloudRasterClient");
    const [k1, k2] = shapes.map(keyOf);
    const heard: { key: string; worker: boolean; raster: KeptRaster }[] = [];
    client.startRaster(k1, makeOf(shapes[0]));
    client.listenRaster(k1, (a) => heard.push(a));
    const w = FakeWorker.made[0];
    w.onerror!({ preventDefault: () => undefined });
    expect(w.terminated).toBe(true);
    expect(client.rasterWorkerAvailable()).toBe(false);
    expect(heard.map((a) => [a.key, a.worker])).toEqual([[k1, false]]);
    expectSameRaster(heard[0].raster, keptCloudRaster(clouds, ...grid, shapes[0], DataUtils.toHalfFloat, 0));
    client.listenRaster(k2, (a) => heard.push(a));
    client.startRaster(k2, makeOf(shapes[1]));
    expect(heard.map((a) => [a.key, a.worker])).toEqual([[k1, false], [k2, false]]);
    expect(FakeWorker.made.length).toBe(1);
  });

  it("without a Worker there is none to ask (vitest's own case, and SSR)", async () => {
    vi.unstubAllGlobals();
    const client = await import("./cloudRasterClient");
    expect(typeof Worker).toBe("undefined");
    expect(client.rasterWorkerAvailable()).toBe(false);
  });
});
