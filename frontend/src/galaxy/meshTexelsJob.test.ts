// S81 (#208 b): the field mesh's texels built in a worker. Proved here: (1) the worker's job (meshTexels, its message
// handler's core), run on the request as it crosses the boundary (the arrays copied, structured-cloned with their
// buffers transferred, and the answer cloned back with every texture's buffer transferred), is the synchronous build
// FieldVolume made until S81 - planeTexture with the mesh's arguments, then fillStars's clustered fill - byte for byte,
// for every source of the stellar layer (the whole `stars`, the star-first remainder, the age parts' sum at three sets
// of switches, and the clustered split at the same three); (2) the request carries only the arrays the job reads, each
// copied as its own range; (3) the main side's queue (meshTexelsClient.ts) against a stand-in Worker: one worker for the
// page, a newer mesh replacing the waiting one, a superseded answer dropped, an answer that came before its listener
// handed to it once, and a failed worker falling back to this thread.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ALL_AGES, ageParts, agedLight, clumpedLight, keptParts } from "@interface/ages.js";

import { type MeshAnswer, type MeshMessage, type MeshRequest, type MeshTexels, answerTransfer, meshArrayNames, meshRequest, meshTexels } from "./meshTexelsJob";
import { planeTexture, starTexels, summed } from "./regimes";

// A render in miniature, as the transport decodes it: every array a float32 view into one answer's buffer.
const R = { unit: "kpc", unit_display: "kpc", n: 24, lo: 0.25, hi: 18.25, width: 0.75 };
const phi = { unit: "rad", unit_display: "rad", n: 60, lo: 0, hi: 2 * Math.PI, width: (2 * Math.PI) / 60 };
const nF = 3;
const cells = R.n * phi.n;
const white = [0.21, 0.11, 0.047];
let seed = 81;
const rand = () => {
  seed = (seed * 1103515245 + 12345) % 2147483648;
  return seed / 2147483648;
};
const shapes: Record<string, number> = {
  stars: cells * nF,
  stars_unresolved: cells * nF,
  stars_young: R.n * nF,
  stars_middle: R.n * nF,
  stars_old: R.n * nF,
  stars_middle_kept3: R.n * nF,
  stars_middle_kept2: R.n * nF,
  stars_middle_kept1: R.n * nF,
  dust_placement: cells,
  stars_middle_placement: cells,
  stars_placement: cells,
  dust_placement_unspurred: cells,
  halpha_hii: cells * nF,
  lines_hii: cells * nF,
  halpha_dig: R.n * nF,
  lines_dig: R.n * nF,
  dust_extinction: R.n * nF,
  dust_scattered: cells * nF,
  dust_thermal: R.n * nF,
  dust_height: R.n,
  dust_diffuse_share: R.n,
  not_read: cells * nF,
};
const total = Object.values(shapes).reduce((s, v) => s + v, 0);
const buffer = new Float32Array(total + 7);
const arrays: Record<string, Float32Array> = {};
{
  let at = 7;
  for (const [name, size] of Object.entries(shapes)) {
    const view = buffer.subarray(at, at + size);
    for (let q = 0; q < size; q += 1) view[q] = name.startsWith("stars_middle_kept") ? 0.1 + 0.4 * rand() : name === "dust_extinction" ? 0.2 + 0.79 * rand() : 0.5 + 2 * rand();
    arrays[name] = view;
    at += size;
  }
  // a missing number here and there: drawn as nothing, or an even ring, as the build reads them
  arrays.dust_placement[5] = Number.NaN;
  arrays.halpha_hii[11] = Number.NaN;
  arrays.stars_middle[4] = Number.NaN;
}
const part = (array: string, weight: string, fields: string[]) => ({ array, weight, weight_fields: fields, ages_gyr: [0, 1] });
const header = {
  axes: { stars: ["R", "phi", "filter"], stars_young: ["R", "filter"], stars_middle: ["R", "filter"], stars_old: ["R", "filter"] },
  components: { stars: { unit: "Lsun/pc2" } },
  ages: {
    parts: {
      young: part("stars_young", "dust_placement", ["gas_density_contrast"]),
      middle: part("stars_middle", "stars_middle_placement", ["sfr_modulation"]),
      old: part("stars_old", "stars_placement", ["pattern_density_contrast"]),
    },
    middle_kept: { arrays: { "3": "stars_middle_kept3", "2": "stars_middle_kept2", "1": "stars_middle_kept1" }, weight: "stars_middle_placement" },
  },
};
type Part = { name: string; key: "young" | "middle" | "old"; weight: string | null };
const parts = ageParts(header, arrays) as Part[];
const kept = keptParts(header, arrays) as { arrays: Record<number, string> };
const spurShare = Array.from({ length: R.n }, (_, i) => (i % 5 === 0 ? 0 : 0.01 * i));
const n = { R: R.n, phi: phi.n, filter: nF };
const SWITCHES = [ALL_AGES, { young: 0, middle: 1, old: 1 }, { young: 1, middle: 0.5, old: 0 }];

/** What the mesh's build reads, as FieldVolume's plan names it. */
function askOf(stars: MeshRequest["stars"]): Omit<MeshRequest, "arrays"> {
  return { R, phi, white, stars, dustHeight: "dust_height", dustPlacement: "dust_placement", diffuseShare: "dust_diffuse_share", unspurred: "dust_placement_unspurred", spurShare };
}

/**
 * The synchronous build as FieldVolume made it until S81, line for line: planeTexture with the mesh's arguments, then,
 * clustered, fillStars's fill of the plane texture's data and the three clump textures (zeros of the same size first).
 */
function beforeS81(stars: MeshRequest["stars"]) {
  const a = arrays as Record<string, ArrayLike<number>>;
  const aged = stars.from === "array" ? null : stars;
  const clumped = stars.from === "clumped";
  const gains = aged ? aged.gains : ALL_AGES;
  const { data, scatter, hii, rings, width, height, cell } = planeTexture({
    R,
    phi,
    stars: stars.from === "array" ? a[stars.name] : clumped ? null : agedLight(a, parts, gains, n),
    hii: summed(a.halpha_hii, a.lines_hii),
    dig: summed(a.halpha_dig, a.lines_dig),
    extinction: a.dust_extinction,
    scattered: a.dust_scattered,
    thermal: a.dust_thermal,
    dustHeight: a.dust_height,
    dustPlacement: a.dust_placement,
    diffuseShare: a.dust_diffuse_share,
    unspurred: a.dust_placement_unspurred,
    spurShare,
    white,
  });
  const clumps = [0, 1, 2].map(() => new Float32Array(width * height * 4));
  if (clumped) {
    const split = clumpedLight(a, parts, kept, gains, n);
    data.set(starTexels(n.R, n.phi, split.rest, white));
    split.clumps.forEach((c: Float64Array, k: number) => clumps[k].set(starTexels(n.R, n.phi, c, white)));
  }
  return { data, scatter, hii, rings, width, height, cell, clumps };
}

/** The request as the worker receives it: copied, then structured-cloned across with its buffers transferred. */
function acrossToWorker(ask: Omit<MeshRequest, "arrays">): MeshRequest {
  const { request, transfer } = meshRequest(ask, arrays);
  const message: MeshMessage = { id: 1, request };
  const got = structuredClone(message, { transfer });
  for (const b of transfer) expect(b.byteLength).toBe(0); // transferred, not copied
  return got.request;
}

/** The answer as the main side receives it: cloned back, every texture's buffer transferred. */
function acrossToMain(texels: MeshTexels): MeshTexels {
  const transfer = answerTransfer(texels);
  const got = structuredClone({ id: 1, texels, ms: 0 } satisfies MeshAnswer, { transfer });
  for (const b of transfer) expect(b.byteLength).toBe(0);
  return got.texels;
}

const bytes = (t: Float32Array) => new Uint8Array(t.buffer, t.byteOffset, t.byteLength);
function expectSameBytes(got: Float32Array, want: Float32Array, what: string) {
  expect(got, what).toBeInstanceOf(Float32Array);
  expect(got.length, what).toBe(want.length);
  const g = bytes(got);
  const w = bytes(want);
  let differ = 0;
  for (let q = 0; q < w.length; q += 1) if (g[q] !== w[q]) differ += 1;
  expect(differ, what).toBe(0);
}

/** The mesh's textures as FieldVolume makes them from the texels: the clump textures zeros where none came. */
function expectSameTexels(got: MeshTexels, want: ReturnType<typeof beforeS81>) {
  expect([got.width, got.height, got.cell]).toEqual([want.width, want.height, want.cell]);
  for (const k of ["data", "scatter", "hii", "rings"] as const) expectSameBytes(got[k], want[k], k);
  [0, 1, 2].forEach((k) => expectSameBytes(got.clumps?.[k] ?? new Float32Array(got.width * got.height * 4), want.clumps[k], `clump ${k}`));
}

const SOURCES: [string, MeshRequest["stars"]][] = [
  ["the whole stars", { from: "array", name: "stars" }],
  ["the star-first remainder", { from: "array", name: "stars_unresolved" }],
  ...SWITCHES.map((gains): [string, MeshRequest["stars"]] => [`the parts' sum at ${JSON.stringify(gains)}`, { from: "aged", parts, gains }]),
  ...SWITCHES.map((gains): [string, MeshRequest["stars"]] => [`the clustered split at ${JSON.stringify(gains)}`, { from: "clumped", parts, kept, gains }]),
];

describe("the worker's job across the boundary is FieldVolume's synchronous build to the byte (S81, #208 b)", () => {
  for (const [name, stars] of SOURCES) {
    it(name, () => {
      const want = beforeS81(stars);
      // sanity: the fixture draws light, places dust and splits where asked
      expect(want.data.some((v) => v > 0)).toBe(true);
      if (stars.from === "clumped") expect(want.clumps[0].some((v) => v > 0)).toBe(true);
      const ask = askOf(stars);
      expectSameTexels(acrossToMain(meshTexels(acrossToWorker(ask))), want);
      // and built on this thread (no Worker), from the render's own arrays, uncopied
      expectSameTexels(meshTexels({ ...ask, arrays }), want);
    });
  }

  it("asks only the arrays the job reads, each copied as its own range of the answer's buffer", () => {
    const ask = askOf({ from: "clumped", parts, kept, gains: ALL_AGES });
    const names = meshArrayNames(ask).sort();
    expect(names).not.toContain("not_read");
    expect(names).not.toContain("stars");
    expect(names).toContain("stars_middle_kept2");
    const { request, transfer } = meshRequest(ask, arrays);
    expect(Object.keys(request.arrays).sort()).toEqual(names);
    expect(transfer.length).toBe(names.length);
    for (const name of names) expect((request.arrays[name] as Float32Array).buffer.byteLength).toBe(arrays[name].byteLength);
    // an absent name (a header naming what the render does not carry) is left out, as the build reads it (undefined)
    const absent = meshRequest({ ...ask, diffuseShare: "no_such_array" }, arrays);
    expect("no_such_array" in absent.request.arrays).toBe(false);
  });
});

describe("the main side's queue (meshTexelsClient.ts) against a stand-in Worker (S81, #208 b)", () => {
  const sources: MeshRequest["stars"][] = [{ from: "array", name: "stars" }, { from: "aged", parts, gains: ALL_AGES }, { from: "clumped", parts, kept, gains: ALL_AGES }];
  const makeOf = (k: number) => () => meshRequest(askOf(sources[k]), arrays);

  beforeEach(() => {
    FakeWorker.made = [];
    vi.resetModules();
    vi.stubGlobal("Worker", FakeWorker);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("one worker; a newer mesh replaces the waiting one, the superseded answer is dropped, the latest heard", async () => {
    const client = await import("./meshTexelsClient");
    expect(client.meshWorkerAvailable()).toBe(true);
    const heard: { key: string; worker: boolean; texels: MeshTexels }[] = [];
    client.startMesh("k0", makeOf(0));
    const stop0 = client.listenMesh("k0", (a) => heard.push(a));
    client.startMesh("k1", makeOf(1)); // waits
    client.startMesh("k2", makeOf(2)); // replaces k1, which never runs
    stop0(); // the field moved on from k0 (its effect's cleanup)
    client.listenMesh("k2", (a) => heard.push(a));
    expect(FakeWorker.made.length).toBe(1);
    const w = FakeWorker.made[0];
    expect(w.url.pathname.endsWith("/meshTexels.worker.ts")).toBe(true);
    expect(w.options.type).toBe("module");
    expect(w.inbox.length).toBe(1); // only k0 posted
    w.deliver(); // k0's answer: superseded, dropped; k2 posted
    expect(heard.length).toBe(0);
    expect(w.inbox.length).toBe(1);
    w.deliver();
    expect(heard.map((a) => [a.key, a.worker])).toEqual([["k2", true]]);
    expectSameTexels(heard[0].texels, beforeS81(sources[2]));
    expect(client.meshWorkerCounts()).toEqual({ posted: 2, answered: 2, stale: 1, replaced: 1 });
  });

  it("an answer that came before its field listened is handed to it once; asked again, it is built again", async () => {
    const client = await import("./meshTexelsClient");
    client.startMesh("k0", makeOf(0));
    const w = FakeWorker.made[0];
    w.deliver(); // no one listens yet: kept for the first listener, the last asked
    let first: MeshTexels | null = null;
    client.listenMesh("k0", (a) => (first = a.texels));
    expect(first).not.toBeNull();
    let second: MeshTexels | null = null;
    client.listenMesh("k0", (a) => (second = a.texels));
    expect(second).toBeNull(); // the textures are one field's: never handed twice
    client.startMesh("k0", makeOf(0)); // a remount asks again: a job of its own
    expect(w.inbox.length).toBe(1);
    w.deliver();
    expect(second).not.toBeNull();
    expect(second).not.toBe(first);
    expect(client.meshWorkerCounts()).toEqual({ posted: 2, answered: 2, stale: 0, replaced: 0 });
  });

  it("asking again for the running mesh posts nothing more, and drops the one waiting", async () => {
    const client = await import("./meshTexelsClient");
    let got = 0;
    client.startMesh("k0", makeOf(0));
    client.startMesh("k1", makeOf(1));
    client.startMesh("k0", makeOf(0));
    client.listenMesh("k0", () => (got += 1));
    const w = FakeWorker.made[0];
    w.deliver();
    expect(got).toBe(1);
    expect(w.inbox.length).toBe(0);
    expect(client.meshWorkerCounts()).toEqual({ posted: 1, answered: 1, stale: 0, replaced: 1 });
  });

  it("a failed worker: the running job built on this thread, and every later one", async () => {
    const client = await import("./meshTexelsClient");
    const heard: { key: string; worker: boolean; texels: MeshTexels }[] = [];
    client.startMesh("k0", makeOf(0));
    client.listenMesh("k0", (a) => heard.push(a));
    const w = FakeWorker.made[0];
    w.onerror!({ preventDefault: () => undefined });
    expect(w.terminated).toBe(true);
    expect(client.meshWorkerAvailable()).toBe(false);
    expect(heard.map((a) => [a.key, a.worker])).toEqual([["k0", false]]);
    expectSameTexels(heard[0].texels, beforeS81(sources[0]));
    client.listenMesh("k2", (a) => heard.push(a));
    client.startMesh("k2", makeOf(2));
    expect(heard.map((a) => [a.key, a.worker])).toEqual([["k0", false], ["k2", false]]);
    expectSameTexels(heard[1].texels, beforeS81(sources[2]));
    expect(FakeWorker.made.length).toBe(1);
  });

  it("without a Worker there is none to ask (vitest's own case, and SSR): FieldVolume builds the texels in its plan", async () => {
    vi.unstubAllGlobals();
    const client = await import("./meshTexelsClient");
    expect(typeof Worker).toBe("undefined");
    expect(client.meshWorkerAvailable()).toBe(false);
  });
});

/** A stand-in for the browser's Worker: messages held until `deliver` runs the worker's job on them, cloned both ways. */
class FakeWorker {
  static made: FakeWorker[] = [];
  onmessage: ((event: { data: MeshAnswer }) => void) | null = null;
  onerror: ((event: { preventDefault(): void }) => void) | null = null;
  readonly inbox: MeshMessage[] = [];
  terminated = false;
  constructor(
    readonly url: URL,
    readonly options: WorkerOptions,
  ) {
    FakeWorker.made.push(this);
  }
  postMessage(message: MeshMessage, transfer: Transferable[]) {
    this.inbox.push(structuredClone(message, { transfer }));
  }
  /** Runs the oldest message's job as the worker does and answers it. */
  deliver() {
    const { id, request } = this.inbox.shift()!;
    const texels = meshTexels(request);
    this.onmessage?.({ data: structuredClone({ id, texels, ms: 1 }, { transfer: answerTransfer(texels) }) });
  }
  terminate() {
    this.terminated = true;
  }
}
