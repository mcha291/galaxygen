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

// The loads whose answer for their current key has not arrived yet (S68, rule D1 as amended): one token per
// mounted loader that is waiting, so a view can say "the galaxy on screen is the previous one's" from a
// "Generate" until every loader asking with the new query has answered - the loaders' own arrival, not a timer.
const waiting = new Set<object>();
const listeners = new Set<() => void>();
const told = () => listeners.forEach((listener) => listener());

/** How many mounted loaders are waiting on the answer for their current key. */
export function pendingLoads(): number {
  return waiting.size;
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};
const idle = () => () => undefined;
const none = () => 0;

/**
 * pendingLoads(), as state: re-renders as it changes - only while `active`, so a view that is not waiting on a
 * "Generate" is not re-rendered by every load the galaxy makes.
 */
export function usePendingLoads(active: boolean): number {
  return useSyncExternalStore(active ? subscribe : idle, active ? pendingLoads : none, none);
}

/**
 * Load whatever `key` describes, once it has stopped changing for `settleMs`.
 *
 * The previous value stays available (`last`, and `busy` says a newer one is on
 * its way) so a view keeps showing the old galaxy rather than blanking; a newer
 * key aborts the request in flight rather than racing it. `key === null` means
 * there is nothing to load yet.
 */
export function useLoad<T>(key: string | null, load: (signal: AbortSignal) => Promise<T>, settleMs = SETTLE_MS) {
  const [result, setResult] = useState<Loaded<T>>({ state: "idle" });
  const [busy, setBusy] = useState(false);
  // The key the last answer (or failure) was for: until it is `key`, this loader is waiting (pendingLoads).
  const [answered, setAnswered] = useState<string | null>(null);
  const loader = useRef(load);
  loader.current = load;
  const waitingNow = key !== null && answered !== key;

  useEffect(() => {
    if (!waitingNow) return;
    const token = {};
    waiting.add(token);
    told();
    return () => {
      waiting.delete(token);
      told();
    };
  }, [waitingNow]);

  useEffect(() => {
    if (key === null) return;
    const abort = new AbortController();
    const timer = setTimeout(() => {
      setBusy(true);
      loader.current(abort.signal)
        .then((value) => {
          setResult({ state: "ready", value });
          setAnswered(key);
        })
        .catch((error: Error) => {
          if (abort.signal.aborted) return;
          setResult((r) => failed(r, error));
          setAnswered(key);
        })
        .finally(() => {
          if (!abort.signal.aborted) setBusy(false);
        });
    }, settleMs);
    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [key, settleMs]);

  const value = result.state === "ready" ? result.value : result.state === "error" ? result.last : null;
  return { value, busy, error: result.state === "error" ? result.message : null };
}
