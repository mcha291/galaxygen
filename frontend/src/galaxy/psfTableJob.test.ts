import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { FILTER_SETS } from "./filters";
import { type Optics, type PsfTable, imageDensity, psfTable, pupilImage } from "./hstPsf";
import { type PsfAnswer, type PsfMessage, type PsfRequest, answerTransfer, psfJob } from "./psfTableJob";

// S82 (#178 (ii)): the PSF table built in a worker. The reference is the pre-S82 synchronous path of psf.ts physicalPsf,
// line for line (psfTable, with imageDensity(pupilImage(optics)) where the spikes are on); the boundary a real
// structured clone, the request cloned and the answer's corners transferred, the buffer checked empty after.

const NGC: Optics = {
  distanceMpc: 17.7,
  pixelArcsec: 0.04,
  apertureM: 2.4,
  obscuration: 0.33,
  spiderWidth: 0.022,
  vanes: 4,
  pads: [
    [0.8921, 0, 0.065],
    [-0.4615, 0.7555, 0.065],
    [-0.4564, -0.7606, 0.065],
  ],
};
const PIVOTS = FILTER_SETS.wfc3.sources!.map((s) => s.pivot);

/** psf.ts physicalPsf's build before S82, line for line (its sampling overrides only for the small fixture). */
function beforeS82(request: PsfRequest): PsfTable {
  const { optics, pivots, spikes, cells, fft } = request;
  let density;
  if (spikes) {
    const image = fft ? pupilImage(optics, true, fft.n, fft.m) : pupilImage(optics);
    density = fft ? imageDensity(image, fft.n, fft.m) : imageDensity(image);
  }
  return psfTable(optics, { pivots, density, cells });
}

/** The job across the boundary: the message cloned in, the table built, the answer cloned out with its corners transferred. */
function throughTheBoundary(request: PsfRequest): PsfTable {
  const got = structuredClone({ id: 1, request } satisfies PsfMessage);
  const table = psfJob(got.request);
  const transfer = answerTransfer(table);
  const answer = structuredClone({ id: got.id, table, ms: 0 } satisfies PsfAnswer, { transfer });
  expect(table.corners.buffer.byteLength).toBe(0); // transferred, not copied
  return answer.table;
}

function expectSameTable(a: PsfTable, b: PsfTable) {
  expect([a.cells, a.cellPc, a.captured]).toEqual([b.cells, b.cellPc, b.captured]);
  expect(a.corners.length).toBe(b.corners.length);
  expect(Buffer.from(a.corners.buffer, a.corners.byteOffset, a.corners.byteLength).equals(Buffer.from(b.corners.buffer, b.corners.byteOffset, b.corners.byteLength))).toBe(true);
}

const SMALL = { cells: 96, fft: { n: 256, m: 32 } };

describe("the worker's job across the boundary is the synchronous build to the byte (S82, #178 ii)", () => {
  for (const spikes of [false, true]) {
    it(`the small fixture, spikes ${spikes ? "on" : "off"}`, () => {
      const request: PsfRequest = { optics: NGC, pivots: PIVOTS, spikes, ...SMALL };
      expectSameTable(throughTheBoundary(request), beforeS82(request));
    });
  }
  it("the drawn tables at full size, both switch states (768 cells; the 2048^2 FFT)", () => {
    for (const spikes of [false, true]) {
      const request: PsfRequest = { optics: NGC, pivots: PIVOTS, spikes };
      expectSameTable(throughTheBoundary(request), beforeS82(request));
    }
  }, 120_000); // four full builds, about 4 s alone and more beside the suite's other files
});

class FakeWorker {
  static made: FakeWorker[] = [];
  onmessage: ((event: { data: PsfAnswer }) => void) | null = null;
  onerror: ((event: { preventDefault(): void }) => void) | null = null;
  readonly inbox: PsfMessage[] = [];
  terminated = false;
  constructor(
    readonly url: URL,
    readonly options: WorkerOptions,
  ) {
    FakeWorker.made.push(this);
  }
  postMessage(message: PsfMessage) {
    this.inbox.push(structuredClone(message));
  }
  /** Runs the oldest message's job as the worker does and answers it. */
  deliver() {
    const { id, request } = this.inbox.shift()!;
    const table = psfJob(request);
    this.onmessage?.({ data: structuredClone({ id, table, ms: 1 }, { transfer: answerTransfer(table) }) });
  }
  terminate() {
    this.terminated = true;
  }
}

describe("the main side (psfTableClient.ts) against a stand-in Worker (S82, #178 ii)", () => {
  const ask = (spikes: boolean): PsfRequest => ({ optics: NGC, pivots: PIVOTS, spikes, ...SMALL });

  beforeEach(() => {
    FakeWorker.made = [];
    vi.resetModules();
    vi.stubGlobal("Worker", FakeWorker);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("one worker; a table asked twice while it builds is posted once; pending until answered", async () => {
    const client = await import("./psfTableClient");
    expect(client.psfWorkerAvailable()).toBe(true);
    const a = client.askPsfTable("on", ask(true));
    const again = client.askPsfTable("on", ask(true));
    const b = client.askPsfTable("off", ask(false));
    expect(again).toBe(a);
    expect(FakeWorker.made.length).toBe(1);
    const w = FakeWorker.made[0];
    expect(w.url.pathname.endsWith("/psfTable.worker.ts")).toBe(true);
    expect(w.options.type).toBe("module");
    expect(w.inbox.length).toBe(2);
    expect(client.psfPending()).toBe(2);
    w.deliver();
    w.deliver();
    const [on, off] = await Promise.all([a, b]);
    expect(client.psfPending()).toBe(0);
    expect([on.worker, off.worker]).toEqual([true, true]);
    expectSameTable(on.table, beforeS82(ask(true)));
    expectSameTable(off.table, beforeS82(ask(false)));
    expect(client.psfBuilds().map((x) => x.key)).toEqual(["on", "off"]);
  });

  it("a failed worker: the jobs it held built on this thread, and every later one", async () => {
    const client = await import("./psfTableClient");
    const a = client.askPsfTable("on", ask(true));
    FakeWorker.made[0].onerror?.({ preventDefault: () => undefined });
    expect(FakeWorker.made[0].terminated).toBe(true);
    const got = await a;
    expect(got.worker).toBe(false);
    expectSameTable(got.table, beforeS82(ask(true)));
    expect(client.psfWorkerAvailable()).toBe(false);
    const later = await client.askPsfTable("off", ask(false));
    expect(later.worker).toBe(false);
    expect(FakeWorker.made.length).toBe(1);
  });

  it("without a Worker (vitest's own case, and SSR) the table is built here", async () => {
    vi.unstubAllGlobals();
    vi.stubGlobal("Worker", undefined);
    const client = await import("./psfTableClient");
    expect(client.psfWorkerAvailable()).toBe(false);
    const got = await client.askPsfTable("off", ask(false));
    expect(got.worker).toBe(false);
    expectSameTable(got.table, beforeS82(ask(false)));
  });
});

describe("the kept tables (psf.ts, S82 #178 ii)", () => {
  it("keeps one texture per key and disposes the other optics' when a new optics' table arrives", async () => {
    vi.resetModules();
    const psf = await import("./psf");
    const set = FILTER_SETS.wfc3;
    const far = { ...NGC, distanceMpc: 20 };
    const askOff = psf.physicalAsk(set, NGC, false)!;
    const askOn = psf.physicalAsk(set, NGC, true)!;
    const askFar = psf.physicalAsk(set, far, false)!;
    expect(psf.physicalAsk(set, null, false)).toBeNull();
    const table = beforeS82({ optics: NGC, pivots: PIVOTS, spikes: false, cells: 8 });
    const off = psf.adoptPhysical(askOff, table);
    const on = psf.adoptPhysical(askOn, table);
    expect(psf.adoptPhysical(askOff, table)).toBe(off);
    let disposed = 0;
    for (const t of [off.texture, on.texture]) t.addEventListener("dispose", () => (disposed += 1));
    psf.adoptPhysical(askFar, table);
    expect(disposed).toBe(2);
    expect(psf.keptPhysical(askOff.key)).toBeNull();
    expect(psf.keptPhysical(askOn.key)).toBeNull();
    expect(psf.keptPhysical(askFar.key)).not.toBeNull();
  });
});
