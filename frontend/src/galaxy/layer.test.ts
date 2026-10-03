import { describe, expect, it } from "vitest";

import { type Loaded, failed } from "../useLoad";
import { runHash } from "../workflow/logic";
import { LAYER_KEY, LayerMismatch, PHYSICS_ONLY, askedLayer, checkLayer, echoedLayer, layerQuery, mustDiscard, onLayerFault, reportLayerFault } from "./layer";

// The workflow's query: the whole input vector and the model (useWorkflow.ts), with the fifth seed since S55.
const QUERY = { halo_mass: 1.1e12, disc_spin: 0.0173, world_seed: 0, pattern_seed: 0, texture_seed: 0, mergers: "[]", model: "azimuthal" };

describe("the query the Galaxy view asks with (S55, D214: invariant I5)", () => {
  it("adds layer=off while physics only is on, and nothing while it is off", () => {
    const off = layerQuery(QUERY, true);
    expect(off).toEqual({ ...QUERY, layer: "off" });
    expect(LAYER_KEY).toBe("layer");
    // The switch off is the query as it was before the switch existed: the same object, no `layer` key at all,
    // so every request - and every request key - is the one S54 sent, and an older API is asked as it was.
    expect(layerQuery(QUERY, false)).toBe(QUERY);
    expect("layer" in layerQuery(QUERY, false)).toBe(false);
    expect(JSON.stringify(layerQuery(QUERY, false))).toBe(JSON.stringify(QUERY));
  });

  it("is display state: the workflow's query is not touched, so the run hash and the template are not", () => {
    const before = JSON.stringify(QUERY);
    const off = layerQuery(QUERY, true);
    expect(off).not.toBe(QUERY);
    expect(JSON.stringify(QUERY)).toBe(before);
    // App.tsx hashes the workflow's query, never the Galaxy view's: the hash is the input vector's whatever the
    // switch says, and the line adds the words. (Hashing the view's query would have moved it.)
    expect(runHash(QUERY)).toBe(runHash(JSON.parse(before) as typeof QUERY));
    expect(runHash(off)).not.toBe(runHash(QUERY));
    expect(PHYSICS_ONLY).toBe("physics only");
  });

  it("reads what a request asked for and what a header echoes", () => {
    expect(askedLayer(layerQuery(QUERY, true))).toBe("off");
    expect(askedLayer(QUERY)).toBe("on");
    expect(askedLayer({ ...QUERY, layer: "on" })).toBe("on");
    expect(askedLayer(undefined)).toBe("on");
    expect(echoedLayer({ layer: "off" })).toBe("off");
    expect(echoedLayer({ layer: "on" })).toBe("on");
    // An API from before S55 echoes nothing, and every frame of it is the layer's.
    expect(echoedLayer({ level: 0 })).toBe("on");
    expect(echoedLayer(undefined)).toBe("on");
    // Anything else is neither.
    expect(echoedLayer({ layer: true })).toBeNull();
    expect(echoedLayer({ layer: "stars" })).toBeNull();
  });
});

describe("a frame is held to the setting it was asked for", () => {
  it("passes a frame that echoes what was asked", () => {
    expect(() => checkLayer("/api/render", layerQuery(QUERY, true), { layer: "off" })).not.toThrow();
    expect(() => checkLayer("/api/render", QUERY, { layer: "on" })).not.toThrow();
    // the switch off against an API from before S55: asked as before, answered as before
    expect(() => checkLayer("/api/render", QUERY, { set: "rgb" })).not.toThrow();
  });

  it("refuses a frame made under the other setting, by name", () => {
    const refuse = (params: Record<string, unknown>, header: unknown) => {
      try {
        checkLayer("/api/clouds", params, header);
      } catch (error) {
        return error as LayerMismatch;
      }
      throw new Error("the frame was not refused");
    };
    const stale = refuse(layerQuery(QUERY, true), { layer: "on" });
    expect(stale).toBeInstanceOf(LayerMismatch);
    expect(stale.message).toMatch(/\/api\/clouds was asked with layer=off and its header says layer=on: this API does not switch the randomness layer off/);
    expect([stale.route, stale.asked, stale.echoed]).toEqual(["/api/clouds", "off", "on"]);
    // An API from before S55 ignores or lacks the parameter and echoes nothing: its frame is the layer's.
    expect(refuse(layerQuery(QUERY, true), { level: 0 }).echoed).toBe("on");
    // And the other way round, and a header that says neither.
    expect(refuse(QUERY, { layer: "off" }).message).toMatch(/asked with layer=on and its header says layer=off: the frame is not the one asked for/);
    expect(refuse(layerQuery(QUERY, true), { layer: "maybe" }).message).toMatch(/says neither on nor off/);
  });

  it("is not drawn: a refused frame takes what was shown before it off the screen", () => {
    const shown: Loaded<string> = { state: "ready", value: "the galaxy with its layer" };
    const refused = failed(shown, new LayerMismatch("/api/region", "off", "on"));
    expect(refused).toMatchObject({ state: "error", last: null });
    expect(mustDiscard(new LayerMismatch("/api/region", "off", "on"))).toBe(true);
    // Any other failure keeps the old galaxy on screen, as it always has (useLoad).
    expect(failed(shown, new Error("503 /api/region: request failed"))).toEqual({ state: "error", message: "503 /api/region: request failed", last: "the galaxy with its layer" });
    expect(mustDiscard(new Error("x"))).toBe(false);
    expect(mustDiscard(null)).toBe(false);
    expect(failed<string>({ state: "idle" }, new Error("x"))).toEqual({ state: "error", message: "x", last: null });
  });

  it("is surfaced: a refusal reaches whoever listens, until they stop", () => {
    const heard: string[] = [];
    const stop = onLayerFault((message) => heard.push(message));
    reportLayerFault("first");
    stop();
    reportLayerFault("second");
    expect(heard).toEqual(["first"]);
  });
});
