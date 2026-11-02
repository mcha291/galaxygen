// The field's loads asked ahead (S80, #208 (a)): App asks, beside the star sample, the very requests the Galaxy tab's
// field mode makes on its mount, and the loaders take them. Run through the real transport (interface/transport.js,
// the project's one fetch) with `fetch` replaced, as api.test.ts does: what is asserted is the requests as they would
// leave the browser - the same set with the head start as without it, one request per key.
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { type FieldsPayload, type Query, forgetRenders, loadArrays, loadClouds, loadLayer, loadRender } from "../api";
import { askFieldAhead, fieldArrayNames, fieldLit, wholeDiscOf } from "./fieldLoads";
import { curvesOf } from "./filters";
import { type Tuning, defaultsFor } from "./tuning";

const QUERY: Query = { halo_mass: 1.1e12, world_seed: 0, texture_seed: 0, mergers: "[]", model: "azimuthal", template: "milky_way" };
const META = {
  model: "azimuthal",
  grid: { axes: { R: { lo: 0.25, hi: 30, n: 120 }, phi: { lo: 0, hi: 6.283185307179586, n: 64 } } },
  fields: ["disc_surface_brightness", "disc_light_temperature", "bulge_scale_radius", "gas_surface_density"].map((name) => ({ name, label: name, unit: "" })),
  cmaps: {},
} as unknown as FieldsPayload;

/** One galaxy-bin/1 frame with no arrays (interface/transport.js decode). */
function frameOf(header: Record<string, unknown>): ArrayBuffer {
  const text = new TextEncoder().encode(JSON.stringify({ format: "galaxy-bin/1", arrays: [], ...header }));
  const bytes = new Uint8Array(8 + text.length);
  bytes.set(new TextEncoder().encode("GLXY"), 0);
  new DataView(bytes.buffer).setUint32(4, text.length, true);
  bytes.set(text, 8);
  return bytes.buffer;
}

interface Sent {
  /** The request as it left: the route and its query (or POST body). */
  request: string;
  signal: AbortSignal | undefined;
}
let sent: Sent[] = [];
/** Answers held back until released, so a test can abort a request in flight. */
let gate: Promise<void> = Promise.resolve();

beforeEach(() => {
  sent = [];
  gate = Promise.resolve();
  forgetRenders();
  vi.stubGlobal("fetch", async (target: string, init: { method: string; body?: string; signal?: AbortSignal }) => {
    const at = new URL(target, "http://viewer.test");
    const params = init.method === "POST" ? new URLSearchParams(init.body) : at.searchParams;
    sent.push({ request: `${at.pathname}?${params.toString()}`, signal: init.signal });
    await gate;
    if (init.signal?.aborted) throw new DOMException("aborted", "AbortError");
    const header = { layer: params.get("layer") ?? "on" };
    if (at.pathname === "/api/layer") return new Response(JSON.stringify(header), { status: 200, headers: { "content-type": "application/json" } });
    return new Response(frameOf(header), { status: 200, headers: { "content-type": "application/octet-stream" } });
  });
});
afterEach(() => vi.unstubAllGlobals());

/** What the Galaxy tab's field mode asks on its mount (FieldVolume's three loaders and GalaxyTab's census), as they ask it. */
async function mount(tuning: Tuning, filterSet: "rgb" | "sho" = "rgb", signal?: AbortSignal) {
  const names = fieldArrayNames(META);
  const asks: Promise<unknown>[] = [loadArrays(names, QUERY, signal), loadRender(curvesOf(filterSet), tuning.whiteKelvin, QUERY, signal, null), loadLayer(QUERY, signal)];
  if (tuning.cloudsExtinction) asks.push(loadClouds(wholeDiscOf(META), QUERY, signal, "f4"));
  return Promise.all(asks);
}

describe("the field's loads asked ahead of the Galaxy tab's mount (S80, #208 a)", () => {
  const tuning = defaultsFor("milky_way");

  it("names what the field volume asks: the declared scalars, and the light it needs", () => {
    expect(fieldArrayNames(META)).toEqual(["bulge_scale_radius"]);
    expect(fieldLit(META)).toBe(true);
    expect(fieldLit({ ...META, fields: META.fields.filter((f) => f.name !== "disc_light_temperature") })).toBe(false);
    expect(wholeDiscOf(META)).toEqual({ r_min: 0.25, r_max: 30, phi_min: 0, phi_max: 2 * Math.PI, level: 0 });
  });

  it("asks the same requests as the mount alone, once each, and the mount asks nothing again", async () => {
    expect(tuning.cloudsExtinction).toBe(true);
    await mount(tuning);
    const alone = sent.map((s) => s.request).sort();
    expect(alone.map((r) => r.split("?")[0])).toEqual(["/api/arrays", "/api/clouds", "/api/layer", "/api/render"]);

    sent = [];
    forgetRenders();
    askFieldAhead(META, QUERY, "rgb", tuning);
    expect(sent.map((s) => s.request).sort()).toEqual(alone);
    await mount(tuning);
    expect(sent.map((s) => s.request).sort()).toEqual(alone);
  });

  it("asks no census where the clouds are not drawn as extinction, and nothing for a model with no light", async () => {
    askFieldAhead(META, QUERY, "rgb", { ...tuning, cloudsExtinction: false });
    expect(sent.map((s) => s.request.split("?")[0]).sort()).toEqual(["/api/arrays", "/api/layer", "/api/render"]);
    sent = [];
    forgetRenders();
    askFieldAhead({ ...META, fields: [] }, QUERY, "rgb", tuning);
    expect(sent).toEqual([]);
  });

  it("is taken once: a later mount asks its own, as before the head start", async () => {
    askFieldAhead(META, QUERY, "rgb", tuning);
    await mount(tuning);
    const first = sent.length;
    await loadArrays(fieldArrayNames(META), QUERY);
    await loadClouds(wholeDiscOf(META), QUERY, undefined, "f4");
    expect(sent.slice(first).map((s) => s.request.split("?")[0])).toEqual(["/api/arrays", "/api/clouds"]);
  });

  it("a taker that stops asking aborts the request it took, as its own would have been", async () => {
    let release = () => {};
    gate = new Promise((r) => (release = r));
    askFieldAhead(META, QUERY, "rgb", tuning);
    const stop = new AbortController();
    const taken = loadArrays(fieldArrayNames(META), QUERY, stop.signal);
    stop.abort();
    await expect(taken).rejects.toThrow();
    const arrays = sent.find((s) => s.request.startsWith("/api/arrays"));
    expect(arrays?.signal?.aborted).toBe(true);
    // the census not taken is still in flight
    expect(sent.find((s) => s.request.startsWith("/api/clouds"))?.signal?.aborted).toBe(false);
    release();
  });

  it("keeps one galaxy's head start: another query's drops the last's, aborted", () => {
    let release = () => {};
    gate = new Promise((r) => (release = r));
    askFieldAhead(META, QUERY, "rgb", tuning);
    askFieldAhead(META, { ...QUERY, template: "ngc_4414" }, "rgb", tuning);
    const of = (template: string) => sent.filter((s) => s.request.includes(`template=${template}`) && /arrays|clouds/.test(s.request));
    expect(of("milky_way").map((s) => s.signal?.aborted)).toEqual([true, true]);
    expect(of("ngc_4414").map((s) => s.signal?.aborted)).toEqual([false, false]);
    release();
  });

  it("asks the same render as a filter set's mount: a mismatch would be a second request, and none is made", async () => {
    askFieldAhead(META, QUERY, "sho", tuning);
    await mount(tuning, "sho");
    expect(sent.filter((s) => s.request.startsWith("/api/render")).length).toBe(1);
  });
});
