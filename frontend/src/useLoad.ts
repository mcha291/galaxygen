import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import { mustDiscard } from "./galaxy/layer";

// A slider drag sends one request when it pauses, not one per pixel.
export const SETTLE_MS = 350;

export type Loaded<T> =
  | { state: "idle" }
  | { state: "error"; message: string; last: T | null }
  | { state: "ready"; value: T };

/**
 * What a failed load leaves: the error, and the value shown before it - unless the error says that value must
 * not stay on screen (S55: a frame made under the other layer setting than the one asked for, galaxy/layer.ts
 * LayerMismatch). Then nothing is left to draw: the old galaxy is the very thing the request did not ask for.
 */
export function failed<T>(previous: Loaded<T>, error: Error): Loaded<T> {
  return { state: "error", message: error.message, last: previous.state === "ready" && !mustDiscard(error) ? previous.value : null };
}

// --- the swap (S68, rule D1 as amended: never half one input set and half another) -----------------------------
//
// A "Generate" changes the query every loader is keyed on, and the loaders answer one by one: drawn as they
// arrive, the new stars would sit over the old field's light for seconds. So from a Generate (`beginSwap`) until
// every mounted loader waiting on its current key has answered, an answer that arrives is **held**, unpublished,
// and its loader keeps showing its previous value; when the last one answers, every held answer is published in
// the same tick. A failure counts as answered (so the others can publish) and is remembered as the swap's
// failure, which the view says until the next Generate or landing. Outside a swap - the landing, a pan, a
// display setting - nothing is held and every loader publishes as it always has. A loader whose key did not
// change is not waiting, and is unaffected.

/** A mounted loader's place in the store: a token, plus the publication of an answer it holds. */
type Token = object;
const waiting = new Set<Token>();
const held = new Map<Token, () => void>();
const listeners = new Set<() => void>();

/** What a view reads of the swap: whether one is under way, and what failed in the last. */
export interface Swap {
  swapping: boolean;
  /** The first failure's message among the last swap's answers; null when every one arrived. */
  failure: string | null;
}
let swap: Swap = { swapping: false, failure: null };

const told = () => listeners.forEach((listener) => listener());

/** How many mounted loaders are waiting on the answer for their current key. */
export function pendingLoads(): number {
  return waiting.size;
}

/** How many answers are held, unpublished, until the swap completes. */
export function heldLoads(): number {
  return held.size;
}

/** Publish every held answer in this tick (React batches the updates into one render) and end the swap. */
function flush(failure: string | null = swap.failure) {
  const publish = [...held.values()];
  held.clear();
  swap = { swapping: false, failure };
  publish.forEach((p) => p());
  told();
}

/** If a swap is under way and nothing is waiting any longer, it is complete. */
function settle() {
  if (swap.swapping && waiting.size === 0) flush();
  else told();
}

/** Complete a swap that nothing is waiting on any longer (a view that knows no loader will ask). */
export function settleSwap(): void {
  settle();
}

/** A "Generate": from now until every waiting loader has answered, answers are held (see above). */
export function beginSwap(): void {
  swap = { swapping: true, failure: null };
  told();
}

/** A landing (or anything that makes the swap moot): publish what is held now and forget the last failure. */
export function endSwap(): void {
  if (!swap.swapping && swap.failure === null && held.size === 0) return; // nothing to end: the snapshot stands
  flush(null);
}

/**
 * A loader's three moves in the store, kept out of React so they can be tested as they are (useLoad.test.ts):
 * it starts waiting on a key, it answers (published now, or held during a swap), or it stops asking (a new key,
 * or unmounted), which drops anything it held and settles the swap after the commit.
 */
export const loads = {
  wait(token: Token): void {
    waiting.add(token);
    told();
  },
  answer(token: Token, publish: () => void, failure: string | null = null): void {
    waiting.delete(token);
    if (swap.swapping) {
      if (failure !== null && swap.failure === null) swap = { ...swap, failure };
      held.set(token, publish);
      settle();
    } else {
      publish();
      told();
    }
  },
  drop(token: Token): void {
    waiting.delete(token);
    held.delete(token);
    queueMicrotask(settle);
  },
};

/** The swap's current state (what useSwap renders from). */
export function swapState(): Swap {
  return swap;
}

/** The swap's state, as state: re-renders when a swap begins or ends, and at nothing else. */
export function useSwap(): Swap {
  return useSyncExternalStore(subscribe, () => swap, () => swap);
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

/**
 * Load whatever `key` describes, once it has stopped changing for `settleMs`.
 *
 * The previous value stays available (`last`, and `busy` says a newer one is on
 * its way) so a view keeps showing the old galaxy rather than blanking; a newer
 * key aborts the request in flight rather than racing it. `key === null` means
 * there is nothing to load yet. During a swap (above) the answer is held until
 * every other waiting loader has answered, and then published with theirs.
 *
 * `input` (S76, BUILD_IV W5, D240 F3: a settle is for the user's input only): the part of the key the user moves - the
 * camera, a slider, the galaxy - with what an answer contributes left out. The settle is then counted from the last
 * change of `input`, not of the key: a key an answer moved (the counts naming the tiles, the tiles naming the render's
 * threshold) after the user has been still for `settleMs` is asked at once, and one moved while the user moves still
 * waits out the rest of the settle. Without `input` every key waits `settleMs`, as before. Only the timing moves: the
 * key, and so the request, is the same.
 */
export function useLoad<T>(key: string | null, load: (signal: AbortSignal) => Promise<T>, settleMs = SETTLE_MS, input?: string) {
  const [result, setResult] = useState<Loaded<T>>({ state: "idle" });
  const [busy, setBusy] = useState(false);
  // This loader's token in the store: the same object for the loader's life (a state, never a memo).
  const [token] = useState<Token>(() => ({}));
  const loader = useRef(load);
  loader.current = load;
  // When the user's part of the key last changed (the loader's mount counts as one): read in the effect, never a dependency.
  const inputSeen = useRef<{ input: string | undefined; at: number } | null>(null);
  if (inputSeen.current === null || inputSeen.current.input !== input) inputSeen.current = { input, at: performance.now() };

  useEffect(() => {
    if (key === null) return;
    loads.wait(token);
    const abort = new AbortController();
    // An answer for this key: published now, or held until the swap completes.
    const answer = (publish: () => void, failure: string | null) => loads.answer(token, publish, failure);
    const seen = inputSeen.current;
    const wait = seen && seen.input !== undefined ? Math.max(0, settleMs - (performance.now() - seen.at)) : settleMs;
    const timer = setTimeout(() => {
      setBusy(true);
      loader.current(abort.signal)
        .then((value) => answer(() => setResult({ state: "ready", value }), null))
        .catch((error: Error) => {
          if (abort.signal.aborted) return;
          answer(() => setResult((r) => failed(r, error)), error.message);
        })
        .finally(() => {
          if (!abort.signal.aborted) setBusy(false);
        });
    }, wait);
    return () => {
      clearTimeout(timer);
      abort.abort();
      // A held answer for a key no longer asked is dropped. The swap is settled after the commit, so a key that
      // moves (this cleanup and the next run, in one commit) does not end it early.
      loads.drop(token);
    };
  }, [key, settleMs, token]);

  const value = result.state === "ready" ? result.value : result.state === "error" ? result.last : null;
  return { value, busy, error: result.state === "error" ? result.message : null };
}
