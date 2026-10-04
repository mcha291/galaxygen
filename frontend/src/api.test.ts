// The layer's switch on the wire (S55, D214: invariant I5's viewer half). Every loader is run through the real
// transport (interface/transport.js, the project's one fetch) with `fetch` itself replaced, so what is asserted is
// the request as it would leave the browser - the URL's query, or the POST body of a query too long for one -
// and the frame's header as the loader reads it back.
import { MAX_URL } from "@interface/transport.js";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { type Query, loadArrays, loadBright, loadClouds, loadClusters, loadRegion, loadRemnants, loadRender, loadSample } from "./api";
import { LayerMismatch, layerQuery, onLayerFault } from "./galaxy/layer";
import { templateQuery } from "./workflow/templates";

const QUERY: Query = { halo_mass: 1.1e12, world_seed: 0, texture_seed: 0, mergers: "[]", model: "azimuthal" };
const WINDOW = { r_min: 7.5, r_max: 8.5, phi_min: 0.1, phi_max: 0.3 };
const CURVES = [{ name: "r", shape: "gaussian", centre: 600, width: 80 }];
const VIEW = Array.from({ length: 16 }, (_, k) => k / 7);

/** One galaxy-bin/1 frame with no arrays: the magic, the header's length, the header (interface/transport.js decode). */
function frameOf(header: Record<string, unknown>): ArrayBuffer {
  const text = new TextEncoder().encode(JSON.stringify({ format: "galaxy-bin/1", arrays: [], ...header }));
  const bytes = new Uint8Array(8 + text.length);
  bytes.set(new TextEncoder().encode("GLXY"), 0);
  new DataView(bytes.buffer).setUint32(4, text.length, true);
  bytes.set(text, 8);
  return bytes.buffer;
}

interface Sent {
  route: string;
  method: string;
  params: URLSearchParams;
}

let sent: Sent[] = [];
/** What the stand-in API echoes for a request: by default what a model since S55 does, the setting it was asked. */
let echo: (params: URLSearchParams) => Record<string, unknown>;
const honest = (params: URLSearchParams) => ({ layer: params.get("layer") ?? "on" });

beforeEach(() => {
  sent = [];
  echo = honest;
  vi.stubGlobal("fetch", async (target: string, init: { method: string; body?: string }) => {
    const at = new URL(target, "http://viewer.test");
    const params = init.method === "POST" ? new URLSearchParams(init.body) : at.searchParams;
    sent.push({ route: at.pathname, method: init.method, params });
    return new Response(frameOf(echo(params)), { status: 200, headers: { "content-type": "application/octet-stream" } });
  });
});
afterEach(() => vi.unstubAllGlobals());

/** Every request shape the Galaxy view makes for model data, by the name of what asks it. */
const REQUESTS: Record<string, { route: string; ask(query: Query): Promise<unknown> }> = {
  "the star sample (App)": { route: "/api/region", ask: (q) => loadSample(q) },
  "a region's stars (GalaxyTab)": { route: "/api/region", ask: (q) => loadRegion(WINDOW, 60_000, q) },
  "the fields the march reads (FieldVolume)": { route: "/api/arrays", ask: (q) => loadArrays(["disc_surface_brightness", "disc_scale_height"], q) },
  "a sampled history (the loader's other shape)": { route: "/api/arrays", ask: (q) => loadArrays(["sfr_history"], q, undefined, { tSamples: 200, precision: "f4" }) },
  "the render (FieldVolume, field mode)": { route: "/api/render", ask: (q) => loadRender(CURVES as never, 5800, q) },
  "the render's remainder under the points (FieldVolume, star-first mode)": { route: "/api/render", ask: (q) => loadRender(CURVES as never, 5800, q, undefined, 12.5) },
  "a region's render (RegionVolume)": { route: "/api/render", ask: (q) => loadRender(CURVES as never, 5800, { ...q, ...WINDOW, level: 2 }) },
  "the bright catalogue (GalaxyTab, star-first mode)": { route: "/api/bright", ask: (q) => loadBright(WINDOW, 1000, VIEW, CURVES as never, 5800, q) },
  "the whole disc's clusters with their light (GalaxyTab, star-first mode)": { route: "/api/clusters", ask: (q) => loadClusters({ ...WINDOW, level: 0 }, q, undefined, { curves: CURVES as never, white: 5800 }) },
  "a region's clusters (GalaxyTab)": { route: "/api/clusters", ask: (q) => loadClusters({ ...WINDOW, level: 2 }, q) },
  "the cloud census (GalaxyTab's markers, RegionVolume)": { route: "/api/clouds", ask: (q) => loadClouds({ ...WINDOW, level: 2 }, q) },
  "a region's remnants (RegionVolume)": { route: "/api/remnants", ask: (q) => loadRemnants({ ...WINDOW, level: 2 }, q) },
};

describe("layer=off on the wire, in every request shape", () => {
  for (const [what, { route, ask }] of Object.entries(REQUESTS)) {
    it(`${what}: ${route} carries the switch`, async () => {
      await ask(layerQuery(QUERY, true));
      expect(sent).toHaveLength(1);
      expect(sent[0].route).toBe(route);
      expect(sent[0].params.getAll("layer")).toEqual(["off"]);
      // and it is still the same galaxy that is asked for
      expect(sent[0].params.get("model")).toBe("azimuthal");
      expect(sent[0].params.get("texture_seed")).toBe("0");

      // The switch off: no `layer` parameter at all - the request S54 sent, to the letter.
      await ask(layerQuery(QUERY, false));
      expect(sent[1].params.has("layer")).toBe(false);
      const without = new URLSearchParams(sent[0].params);
      without.delete("layer");
      expect(sent[1].params.toString()).toBe(without.toString());
    });
  }

  it("rides in the body of a query too long for a URL (a named instrument's sampled curves)", async () => {
    const long = Array.from({ length: 200 }, (_, k) => ({ name: `f${k}`, shape: "sampled", wavelength: [400 + k, 500 + k], throughput: [0.5, 0.25] }));
    await loadRender(long as never, 5800, layerQuery(QUERY, true));
    expect(JSON.stringify(long).length).toBeGreaterThan(MAX_URL);
    expect(sent[0].method).toBe("POST");
    expect(sent[0].params.getAll("layer")).toEqual(["off"]);
  });
});

// The template's name on the wire (S58, D217 item 2): a galaxy that is a template or was started from one is
// asked for with `template=<name>` beside its inputs, on every route that takes an input vector - it is what
// brings the template's pins, which no input can. The query is the workflow's (useWorkflow.ts queryOf, which adds
// the parameter in one place through templateQuery); what is asserted is each loader carrying it to the request.
describe("template=<name> on the wire, in every request shape", () => {
  const NGC = { name: "ngc_4414" };

  for (const [what, { route, ask }] of Object.entries(REQUESTS)) {
    it(`${what}: ${route} names the template the galaxy was started from`, async () => {
      await ask(templateQuery(QUERY, NGC));
      expect(sent).toHaveLength(1);
      expect(sent[0].route).toBe(route);
      expect(sent[0].params.getAll("template")).toEqual(["ngc_4414"]);
      // beside the inputs, not in place of them: the query's own values are what the API lays over the template's
      expect(sent[0].params.get("halo_mass")).toBe("1100000000000");
      expect(sent[0].params.get("mergers")).toBe("[]");
      expect(sent[0].params.get("model")).toBe("azimuthal");
      // and no pin is sent as an input: the API refuses one
      expect(sent[0].params.has("bar_present")).toBe(false);

      // A galaxy started from no template: no `template` parameter at all - the request as it was, to the letter.
      await ask(templateQuery(QUERY, null));
      expect(sent[1].params.has("template")).toBe(false);
      const without = new URLSearchParams(sent[0].params);
      without.delete("template");
      expect(sent[1].params.toString()).toBe(without.toString());

      // With the layer off as with it on: the two parameters ride together.
      await ask(layerQuery(templateQuery(QUERY, NGC), true));
      expect([sent[2].params.getAll("template"), sent[2].params.getAll("layer")]).toEqual([["ngc_4414"], ["off"]]);
    });
  }

  it("rides in the body of a query too long for a URL (the POST path past 4 KB)", async () => {
    const long = Array.from({ length: 200 }, (_, k) => ({ name: `f${k}`, shape: "sampled", wavelength: [400 + k, 500 + k], throughput: [0.5, 0.25] }));
    expect(JSON.stringify(long).length).toBeGreaterThan(MAX_URL);
    await loadRender(long as never, 5800, templateQuery(QUERY, NGC));
    await loadBright(WINDOW, 1000, VIEW, long as never, 5800, templateQuery(QUERY, NGC));
    await loadClusters({ ...WINDOW, level: 0 }, templateQuery(QUERY, NGC), undefined, { curves: long as never, white: 5800 });
    expect(sent.map((s) => [s.route, s.method, s.params.getAll("template")])).toEqual([
      ["/api/render", "POST", ["ngc_4414"]],
      ["/api/bright", "POST", ["ngc_4414"]],
      ["/api/clusters", "POST", ["ngc_4414"]],
    ]);
    // the same long query from a galaxy of no template: still a POST, and no template in its body
    await loadRender(long as never, 5800, templateQuery(QUERY, null));
    expect([sent[3].method, sent[3].params.has("template")]).toEqual(["POST", false]);
  });
});

describe("the header's echo, checked where every frame is read", () => {
  for (const [what, { route, ask }] of Object.entries(REQUESTS)) {
    it(`${what}: a frame that says on under physics only is refused and reported`, async () => {
      const heard: string[] = [];
      const stop = onLayerFault((message) => heard.push(message));
      echo = () => ({ layer: "on" }); // an API that does not switch the layer off
      const refused = await ask(layerQuery(QUERY, true)).then(
        () => null,
        (error: unknown) => error,
      );
      stop();
      expect(refused).toBeInstanceOf(LayerMismatch);
      expect((refused as LayerMismatch).route).toBe(route);
      expect(heard).toEqual([(refused as LayerMismatch).message]);
    });
  }

  it("refuses an API from before S55 under physics only (no echo), and takes it as it is with the switch off", async () => {
    echo = () => ({});
    await expect(loadSample(layerQuery(QUERY, true))).rejects.toBeInstanceOf(LayerMismatch);
    await expect(loadSample(layerQuery(QUERY, false))).resolves.toMatchObject({ header: { format: "galaxy-bin/1" } });
  });

  it("refuses a layer-off frame nobody asked for", async () => {
    echo = () => ({ layer: "off" });
    await expect(loadClouds({ ...WINDOW, level: 1 }, layerQuery(QUERY, false))).rejects.toThrow(/asked with layer=on and its header says layer=off/);
  });

  it("hands on a frame that echoes what was asked, header and all", async () => {
    echo = (params) => ({ ...honest(params), scalars: { cloud_extinction_v: 2.9696 }, cloud_interior: { octaves: 4, lacunarity: 2.0, gain: 0.5 } });
    const census = await loadClouds({ ...WINDOW, level: 1 }, layerQuery(QUERY, true));
    expect(census.header.layer).toBe("off");
    expect(census.header.scalars).toEqual({ cloud_extinction_v: 2.9696 });
    // the interior noise's parameters ride under their own key, with the layer off as with it on (region.ts interiorOf)
    expect(census.header.cloud_interior).toEqual({ octaves: 4, lacunarity: 2, gain: 0.5 });
  });
});
