import { useEffect, useRef, useState } from "react";

// A slider drag sends one request when it pauses, not one per pixel.
export const SETTLE_MS = 350;

export type Loaded<T> =
  | { state: "idle" }
  | { state: "error"; message: string; last: T | null }
  | { state: "ready"; value: T };

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
  const loader = useRef(load);
  loader.current = load;

  useEffect(() => {
    if (key === null) return;
    const abort = new AbortController();
    const timer = setTimeout(() => {
      setBusy(true);
      loader.current(abort.signal)
        .then((value) => setResult({ state: "ready", value }))
        .catch((error: Error) => {
          if (abort.signal.aborted) return;
          setResult((r) => ({ state: "error", message: error.message, last: r.state === "ready" ? r.value : null }));
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
