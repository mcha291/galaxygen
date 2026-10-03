// The viewer's half of invariant I5 (BUILD_III §1d, D214): a switch between the physics model alone and the
// physics with the randomness layer. The switch is the model's - `layer=off` on every route that takes inputs,
// echoed in every wire header - and the viewer only sends it and holds the answer to it. Pure: no React, no
// network. Display state, not an input: it is no part of the workflow's query, of the run hash or of what makes
// a template "edited".

/** The layer's two settings, as the API spells them (`layer=on`, the default, or `layer=off`). */
export type LayerSetting = "on" | "off";

/** The query parameter and the wire header's key. */
export const LAYER_KEY = "layer";

/** The switch's label in the Galaxy panel, and what the top bar's hash line adds while it is on. */
export const PHYSICS_ONLY = "physics only";

type Query = Record<string, unknown>;

/**
 * The query the Galaxy view asks the model with: the workflow's input vector and, while "physics only" is on,
 * `layer=off`. **The one place the parameter is added** (App.tsx hands the result to the star sample and to the
 * Galaxy tab, whose every loader spreads the query it is given), so a loader added later carries it without
 * knowing of it (rule B13). With the switch off the workflow's own object is returned, untouched: nothing is
 * sent that was not sent before the switch existed, and an API from before S55 is asked exactly as it was.
 */
export function layerQuery<Q extends Query>(query: Q, physicsOnly: boolean): Q {
  return physicsOnly ? { ...query, [LAYER_KEY]: "off" } : query;
}

/** The setting a request asked for: `off` only where it says so; absent is the API's default, on. */
export function askedLayer(params: Query | null | undefined): LayerSetting {
  return params?.[LAYER_KEY] === "off" ? "off" : "on";
}

/**
 * The setting a wire header says its frame was made under. A header without the key is an API from before the
 * layer had a switch (S55), whose every frame is the layer's: on.
 */
export function echoedLayer(header: unknown): LayerSetting | null {
  const raw = (header as Record<string, unknown> | null | undefined)?.[LAYER_KEY];
  if (raw === undefined) return "on";
  return raw === "on" || raw === "off" ? raw : null;
}

/**
 * A frame made under the other setting than the one asked for. Not drawn (useLoad drops what it showed before
 * for an error that says `discard`) and surfaced (`onLayerFault`): a picture of the layered galaxy under a
 * pressed "physics only" would be a false statement on screen.
 */
export class LayerMismatch extends Error {
  readonly discard = true;
  constructor(
    readonly route: string,
    readonly asked: LayerSetting,
    readonly echoed: LayerSetting | null,
  ) {
    super(
      `${route} was asked with layer=${asked} and its header says ${echoed === null ? "neither on nor off" : `layer=${echoed}`}: ` +
        (asked === "off" && echoed === "on"
          ? "this API does not switch the randomness layer off (one from before S55?), so its frame is not the physics alone and is not drawn"
          : "the frame is not the one asked for and is not drawn"),
    );
    this.name = "LayerMismatch";
  }
}

/** Whether an error says that what was shown before it must not stay on screen (useLoad). */
export function mustDiscard(error: unknown): boolean {
  return (error as { discard?: unknown } | null)?.discard === true;
}

/**
 * Hold a frame's header to the request that asked for it: the echoed `layer` is the one asked for, or the frame
 * is refused. Called for every binary route in one place (api.ts `route`), which reports the refusal too.
 */
export function checkLayer(route: string, params: Query | null | undefined, header: unknown): void {
  const asked = askedLayer(params);
  const echoed = echoedLayer(header);
  if (echoed !== asked) throw new LayerMismatch(route, asked, echoed);
}

// --- the fault's way to the page ---------------------------------------------------------------------------
// Most loads in the Galaxy view read a value and drop the load's error, and two of them run inside the
// react-three-fiber canvas, where the app's React context does not reach. A refused frame is therefore reported
// here, once, where it is refused, and App.tsx listens: one place to remember, not one per loader (rule B13).

const listeners = new Set<(message: string) => void>();

/** Listen for refused frames; returns the function that stops listening. */
export function onLayerFault(listener: (message: string) => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function reportLayerFault(message: string): void {
  for (const listener of listeners) listener(message);
}
