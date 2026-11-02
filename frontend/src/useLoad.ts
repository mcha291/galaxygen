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
//
// S82 (#187): the loaders whose key follows another loader's answer (the star-first mode's counts and tiles after the
// bright table, the field's remainder after the tiles' threshold) are in the swap from its start: while what they
// follow has not answered for this swap they wait on it and ask nothing (useLoad's `after`), and they read the held
// answer (useLoad's `next`) to take their own key inside the swap - so the swap publishes once, with them in, never a
// second, partial update after it. And the camera's loads are kept out of the hold: a loader keyed on the view
// (useLoad's `view`) holds a swap only while the view stands where it stood when the swap began; moved, it asks freely
// and holds nothing, its answer published with the swap if it comes first and on its own after - and if the swap ends
// before it answers, what it showed of the previous galaxy is taken down then (never one galaxy's field under
// another's points, rule D1).
//
// S82 (#188): a template landing over a galaxy on screen is a swap too, with its own line (`landing`): the previous
// picture stays, its camera with it (App.tsx), until every loader of the new template has answered, then the whole
// swap, as a Generate's. Its canvas is then made afresh at the template's stand (D213 ruling 5), so what the old
// canvas's loaders were published by the landing's swap is handed over to the new canvas's loaders of the same key
// (`handOver`, `handed`): nothing is asked twice, and the new canvas does not wait on the wire for what the old one had.
// The first landing of the app (nothing on screen) is no swap, as before.

/** A mounted loader's place in the store: a token, plus the publication of an answer it holds. */
type Token = object;
/** Publish a held answer; told whether the swap that held it was a landing's (#188's hand-over). */
type Publish = (landing: boolean) => void;
const waiting = new Set<Token>();
const held = new Map<Token, Publish>();
/** Loaders keyed on the view that the camera freed during this swap and that have not answered: taken down at its end. */
const roaming = new Map<Token, () => void>();
/** What a landing's swap published to loaders then unmounted with the old canvas, by key (#188): taken once. */
const handovers = new Map<string, unknown>();
const listeners = new Set<() => void>();

/** What a view reads of the swap: whether one is under way, and what failed in the last. */
export interface Swap {
  swapping: boolean;
  /** The first failure's message among the last swap's answers; null when every one arrived. */
  failure: string | null;
  /** The swap is a template landing's over a galaxy on screen (#188), not a Generate's alone. */
  landing: boolean;
}
let swap: Swap = { swapping: false, failure: null, landing: false };
/** Counts the swaps begun: a loader keyed on the view reads the view it stood at when this one began (ViewMark). */
let generation = 0;

const told = () => listeners.forEach((listener) => listener());

/** How many mounted loaders are waiting on the answer for their current key. */
export function pendingLoads(): number {
  return waiting.size;
}

/** How many answers are held, unpublished, until the swap completes. */
export function heldLoads(): number {
  return held.size;
}

/**
 * Publish every held answer in this tick (React batches the updates into one render) and end the swap; a loader the
 * camera freed that has still not answered takes down what it showed of the previous galaxy (#187).
 */
function flush(failure: string | null = swap.failure) {
  const landing = swap.landing;
  const publish = [...held.values()];
  const takeDown = [...roaming.values()];
  held.clear();
  roaming.clear();
  swap = { swapping: false, failure, landing: false };
  if (landing) landed(performance.now()); // #188: the new canvas's loaders may start from what this publishes
  publish.forEach((p) => p(landing));
  takeDown.forEach((down) => down());
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

/**
 * A "Generate" - or, with `landing`, a template landing over a galaxy on screen (#188): from now until every waiting
 * loader has answered, answers are held (see above). A Generate begun during a landing's swap keeps it a landing's:
 * the landing's camera still waits on it.
 */
export function beginSwap(landing = false): void {
  generation += 1;
  roaming.clear();
  handovers.clear();
  swap = { swapping: true, failure: null, landing: landing || (swap.swapping && swap.landing) };
  told();
}

/** Anything that makes the swap moot: publish what is held now and forget the last failure. */
export function endSwap(): void {
  if (!swap.swapping && swap.failure === null && held.size === 0) return; // nothing to end: the snapshot stands
  flush(null);
}

/**
 * A template landing (useWorkflow.ts land; #188). Over a galaxy on screen it is a swap of its own (`landing`): the old
 * picture stays until the template's loaders have answered, then the whole swap, as a Generate's; a Generate under way
 * is moot (its held answers dropped as their loaders take the template's keys, its failure forgotten). With nothing
 * on screen - the app's first landing - it is as it always was: no swap, and any ended.
 */
export function beginLanding(onScreen: boolean): void {
  if (onScreen) beginSwap(true);
  else endSwap();
}

/** How many swaps have begun (a loader keyed on the view reads where it stood when the last began). */
export function swapGeneration(): number {
  return generation;
}

/**
 * A loader's three moves in the store, kept out of React so they can be tested as they are (useLoad.test.ts):
 * it starts waiting on a key, it answers (published now, or held during a swap), or it stops asking (a new key,
 * or unmounted), which drops anything it held and settles the swap after the commit.
 *
 * `wait`'s `free` (#187): a loader keyed on the view whose view has moved since the swap began - it asks, and holds
 * nothing; `takeDown` is what it does if the swap ends before it answers. `answer`'s `onHold` is told when the answer
 * is held, so the loader can show it to the loaders whose keys follow it (useLoad's `next`) without drawing it.
 */
export const loads = {
  wait(token: Token, free?: { takeDown: () => void }): void {
    if (free && swap.swapping) {
      waiting.delete(token);
      roaming.set(token, free.takeDown);
    } else {
      waiting.add(token);
    }
    told();
  },
  answer(token: Token, publish: Publish, failure: string | null = null, onHold?: () => void): void {
    waiting.delete(token);
    roaming.delete(token);
    if (swap.swapping) {
      if (failure !== null && swap.failure === null) swap = { ...swap, failure };
      held.set(token, publish);
      onHold?.();
      settle();
    } else {
      publish(false);
      told();
    }
  },
  drop(token: Token): void {
    waiting.delete(token);
    held.delete(token);
    roaming.delete(token);
    queueMicrotask(settle);
  },
};

/**
 * How long after a landing's swap is published its hand-over stands (#188), ms: the canvas is made afresh in the
 * frames after it, and a loader unmounted later (a tab left, a mode switched) is no part of the landing.
 */
export const HANDOVER_MS = 2000;
/** When the last landing's swap was published (performance.now()), or null: no hand-over is open. */
let landedAt: number | null = null;
const handing = (now: number) => landedAt !== null && now - landedAt < HANDOVER_MS;

/** A landing's swap has just been published (the loaders' publications say so): its hand-over opens now. */
export function landed(now: number): void {
  landedAt = now;
}

/**
 * #188's hand-over: a loader unmounted with the old canvas, holding what a landing's swap published to it, leaves it
 * here under its key; the new canvas's loader asking the same key first starts from it (`handed`) and asks nothing,
 * taking it (`takeHanded`) so no other does. Open for HANDOVER_MS after the landing's publish; emptied when the next
 * swap begins.
 */
export function handOver(key: string, value: unknown, now: number): void {
  if (handing(now)) handovers.set(key, value);
}

/** What was handed over for `key`, without taking it; undefined where nothing was, or the hand-over has closed. */
export function handed<T>(key: string, now: number): T | undefined {
  return handing(now) ? (handovers.get(key) as T | undefined) : undefined;
}

/** Take what was handed over for `key`: no other loader starts from it. */
export function takeHanded(key: string): void {
  handovers.delete(key);
}

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
 * When the user's part of a loader's key (`input`, below) last changed - the settle's clock (S76, D240 F3; the review's
 * G3), kept per loader out of React so it is tested as it is (useLoad.test.ts). `see` is told the input on every render:
 * a changed input is a move of the user's, and the loader's first render counts as one. A `null` input names nothing
 * yet - its cells wait on an answer (the bright table's layout) - so its first naming is that answer's doing and keeps
 * the last move's time. `undefined` is a loader without an input: every key waits the whole settle, as before F3.
 *
 * S78: the first key a loader asks is asked at once - nothing before it can be a drag, so there is nothing to settle
 * (on the landing three loaders in a chain each waited the whole settle on mount). `wait` is told the key: until a
 * request has gone out (`fired`) the first non-null key waits 0; every later key settles as above.
 */
export class InputClock {
  private input: string | null | undefined = undefined;
  private at = 0;
  private seen = false;
  /** The first non-null key this loader was asked for (null: none yet), and whether any request has gone out. */
  private first: string | null = null;
  private asked = false;

  see(input: string | null | undefined, now: number): void {
    if (!this.seen) {
      this.seen = true;
      this.input = input;
      this.at = now;
      return;
    }
    if (input === this.input) return;
    if (this.input !== null) this.at = now;
    this.input = input;
  }

  /**
   * How long a key asked at `now` waits: the rest of the settle since the user's last move (0 once it has passed) - or 0
   * for the loader's first key (`key`, S78), until its request has gone out. A cleanup and re-run of the same effect
   * before the timer fires (StrictMode's) asks the first key again, at once.
   */
  wait(settleMs: number, now: number, key?: string): number {
    if (key !== undefined && !this.asked) {
      if (this.first === null) this.first = key;
      if (key === this.first) return 0;
    }
    return this.input === undefined ? settleMs : Math.max(0, settleMs - (now - this.at));
  }

  /** A request has gone out: from now every key settles. */
  fired(): void {
    this.asked = true;
  }
}

/**
 * Where a loader keyed on the view stood when the swap under way began (S82, #187), kept per loader out of React so it
 * is tested as it is (useLoad.test.ts). `see` is told the view on every render with the swaps' count: the first render
 * in a new swap - the one the swap's new query is drawn in - fixes the view it began at. `moved` says whether the view
 * has left it since: the loader then holds nothing (the camera's loads are kept out of the hold).
 */
export class ViewMark {
  private generation = -1;
  private view: string | null = null;

  see(view: string | null, generation: number): void {
    if (generation === this.generation) return;
    this.generation = generation;
    this.view = view;
  }

  moved(view: string | null): boolean {
    return view !== this.view;
  }
}

/**
 * A loader's part in a swap beyond its key (S82, #187).
 *
 * `view`: the view this loader's key reads (the camera, a window), as a string - a loader keyed on the view holds a
 * swap only while it stands where it stood when the swap began; moved, it asks freely and holds nothing.
 *
 * `after`: what this key follows (another loader's answer: the bright table's layout, the tiles' threshold) has not
 * answered for this swap - true from a dependency's `settling`. The loader then waits on the swap and asks nothing, so
 * the swap cannot complete before it; when the answer it follows is held, it reads it (`next`) and asks its own key
 * inside the swap. Outside a swap it means nothing.
 */
export interface SwapRole {
  view?: string | null;
  after?: boolean;
}

/**
 * A loader's place in the swap under way, from what it is told (S82, #187), kept out of React so it is tested as it
 * is: `free`, the camera has moved it since the swap began (it asks, and holds nothing); `after`, it waits on what it
 * follows and asks nothing - even with no key yet, where its key waits on that answer to be named at all (the tiles
 * before the counts below 4 kpc); `settling`, it holds the swap - waiting on its own key's answer or on what it
 * follows. A null key otherwise holds nothing; outside a swap nothing is any of these.
 */
export function swapPart(at: { swapping: boolean; key: string | null; role: SwapRole; moved: boolean; answered: boolean }) {
  const free = at.swapping && at.role.view !== undefined && at.moved;
  const after = at.swapping && at.role.after === true;
  const settling = at.swapping && !free && (after || (at.key !== null && !at.answered));
  return { free, after, settling };
}

/**
 * Load whatever `key` describes, once it has stopped changing for `settleMs` - the loader's first key at once (S78,
 * InputClock).
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
 * key, and so the request, is the same. `input` must name everything the user moves that the key reads - the view
 * itself where the key reads the view (the review's G3), else a move with the input standing is asked at once.
 *
 * `firstAtOnce` (S78): the first key is asked at once (InputClock) unless this is false - for a key that reads the
 * view (a region's window, the star-first mode's cells and tiles), whose loader can mount while the view is moving: a
 * zoom into the region regime, a camera placed as the mode opens. Asked at once, its first key would be a frame of
 * the drag, a request no settled view makes; it settles as every other key.
 *
 * `role` (S82, #187): the loader's part in a swap (SwapRole). Beside `value` it returns `next`, the newest answer for
 * the current key - held by a swap and not yet drawn, or published - for the keys that follow it to read; `answered`,
 * whether an answer for the current key has come (held or published; a null key has nothing to wait for); and
 * `settling`, whether this loader holds the swap under way (waiting on its key, or on what it follows) - what a loader
 * that follows it passes as its `after`. Outside a swap `next` is `value` and `settling` false.
 */
export function useLoad<T>(
  key: string | null,
  load: (signal: AbortSignal) => Promise<T>,
  settleMs = SETTLE_MS,
  input?: string | null,
  firstAtOnce = true,
  role: SwapRole = {},
) {
  // #188: a loader of a canvas made afresh by a landing starts from what the old canvas's loader of the same key was
  // published by the landing's swap (handed over at its unmount), and asks nothing for that key.
  const [start] = useState(() => {
    const value = key === null ? undefined : handed<T>(key, performance.now());
    return value === undefined ? null : { key: key as string, value };
  });
  const handedKey = useRef<string | null>(start?.key ?? null);
  const [result, setResult] = useState<Loaded<T>>(() => (start ? { state: "ready", value: start.value } : { state: "idle" }));
  // The newest answer and its key, held or published (#187): what `next` and `answered` read. A failure's value is null.
  const [latest, setLatest] = useState<{ key: string; value: T | null } | null>(start);
  // What the last landing's swap published here, if that was the last publish (#188): handed over at the unmount.
  const landedHere = useRef<{ key: string; value: T } | null>(null);
  useEffect(
    () => () => {
      if (landedHere.current) handOver(landedHere.current.key, landedHere.current.value, performance.now());
    },
    [],
  );
  // The swap in which this loader last asked at once for a landing (#188), so later keys in it settle as usual.
  const landingAsked = useRef(-1);
  const [busy, setBusy] = useState(false);
  // This loader's token in the store: the same object for the loader's life (a state, never a memo).
  const [token] = useState<Token>(() => ({}));
  const loader = useRef(load);
  loader.current = load;
  // When the user's part of the key last changed (InputClock): read in the effect, never a dependency.
  const [clock] = useState(() => new InputClock());
  clock.see(input, performance.now());
  // Where the view stood when the swap began (ViewMark, #187): a loader keyed on the view, moved since, holds nothing.
  const { swapping } = useSwap();
  const [mark] = useState(() => new ViewMark());
  if (role.view !== undefined) mark.see(role.view, swapGeneration());
  const answered = key === null || latest?.key === key;
  const { free, after, settling } = swapPart({ swapping, key, role, moved: role.view !== undefined && mark.moved(role.view), answered });
  // Read in the effect, never a dependency: a view that moves while the key stands re-asks nothing.
  const freed = useRef(free);
  freed.current = free;

  useEffect(() => {
    // Nothing to load - unless the key waits on what it follows, inside a swap: then it holds the swap unnamed (#187).
    if (key === null && !after) return;
    // Started from a landing's hand-over (#188): that key's answer is here already, so it is not asked again. Taken,
    // so no other loader starts from it; a return to the key later asks as any key does.
    if (key !== handedKey.current) handedKey.current = null;
    else if (!after && key !== null) {
      takeHanded(key);
      clock.fired(); // as if its first key had been asked: every later key settles (InputClock)
      return;
    }
    // Freed by the camera: it asks and holds nothing; if the swap ends before it answers, what it showed of the
    // previous galaxy is taken down (rule D1: never one galaxy's loads under another's).
    const takeDown = () => {
      setResult({ state: "idle" });
      setLatest(null);
      landedHere.current = null;
    };
    loads.wait(token, freed.current ? { takeDown } : undefined);
    // What this key follows has not answered for the swap: wait on it, ask nothing yet (#187).
    if (after || key === null) return () => loads.drop(token);
    const abort = new AbortController();
    // An answer for this key: published now, or held until the swap completes - and then shown to the keys that
    // follow it at once (`next`), drawn only with the rest.
    const answer = (value: T | null, publish: () => void, failure: string | null) =>
      loads.answer(
        token,
        (landing) => {
          publish();
          setLatest({ key, value });
          landedHere.current = landing && value !== null ? { key, value } : null;
        },
        failure,
        () => setLatest({ key, value }),
      );
    // A key a landing moved is asked at once (#188), as the fresh canvas's first key was before the landing held the
    // old one (S78); later keys in the same swap settle as usual. A view's key settles as it always has.
    const now = swapState();
    const generationNow = swapGeneration();
    const landingKey = now.swapping && now.landing && firstAtOnce && landingAsked.current !== generationNow;
    const wait = landingKey ? 0 : clock.wait(settleMs, performance.now(), firstAtOnce ? key : undefined);
    const timer = setTimeout(() => {
      if (landingKey) landingAsked.current = generationNow;
      clock.fired();
      setBusy(true);
      loader.current(abort.signal)
        .then((value) => answer(value, () => setResult({ state: "ready", value }), null))
        .catch((error: Error) => {
          if (abort.signal.aborted) return;
          answer(null, () => setResult((r) => failed(r, error)), error.message);
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
  }, [key, settleMs, token, clock, firstAtOnce, after]);

  const value = result.state === "ready" ? result.value : result.state === "error" ? result.last : null;
  const next = latest !== null && latest.key === key && latest.value !== null ? latest.value : value;
  return { value, busy, error: result.state === "error" ? result.message : null, next, answered, settling };
}
