// The workflow's pure pieces. The checkpoint state machine itself is
// interface/flow.js (rule D1, tested in tests/js/flow.test.mjs); this file adds
// only what the panel needs on top of it, and nothing here touches React.
import * as flow from "@interface/flow.js";

export interface InputDecl {
  name: string;
  label: string;
  kind: "control" | "seed" | "events";
  about: string;
  checkpoint: number | null;
  unit?: string;
  unit_display?: string;
  default: unknown;
  lo?: number | null;
  hi?: number | null;
}

export interface Checkpoint {
  n: number;
  name: string;
  stages: string[];
  inputs: string[];
}

export interface FlowState {
  cat: { model: string; checkpoints: Checkpoint[]; inputs: Map<string, InputDecl>; order: string[] };
  values: Record<string, unknown>;
  locked: Record<string, boolean>;
  confirmed: number;
  current: number;
  previews: Record<string, unknown>;
}

export interface MergerEvent {
  time: number;
  mass_ratio: number;
  gas_fraction: number;
  about?: string;
}

/**
 * What a checkpoint is, for the rail:
 * - `locked`: confirmed; its controls are disabled and still shown (D1)
 * - `editing`: the one open for edits
 * - `next`: the first unconfirmed one, reachable but not open
 * - `blocked`: needs the one before it confirmed first
 */
export type Status = "locked" | "editing" | "next" | "blocked";

export function statusOf(state: FlowState, n: number): Status {
  if (n <= state.confirmed) return "locked";
  if (n === state.current) return "editing";
  if (n === state.confirmed + 1) return "next";
  return "blocked";
}

/**
 * Reopen checkpoint n, and say which later checkpoints that discarded.
 *
 * flow.reopen drops their results; the panel also needs to *tell* the user which
 * confirmations were thrown away until they confirm those checkpoints again,
 * so it gets the list back rather than a silent state change.
 */
export function reopenCost(state: FlowState, n: number): number[] {
  const out: number[] = [];
  for (let k = n + 1; k <= state.confirmed; k += 1) out.push(k);
  return out;
}

export function reopen(state: FlowState, n: number): { state: FlowState; discarded: number[] } {
  return { state: flow.reopen(state, n) as FlowState, discarded: reopenCost(state, n) };
}

/** Re-rolling a checkpoint's seed invalidates every later checkpoint and nothing earlier. */
export function rerollCost(state: FlowState, n: number): number[] {
  const last = state.cat.checkpoints.length;
  return Array.from({ length: last - n }, (_, i) => n + 1 + i);
}

/** A fresh seed: a uniform non-negative 31-bit integer. Any integer is a valid seed. */
export function drawSeed(random: () => number = Math.random): number {
  return Math.floor(random() * 2 ** 31);
}

/**
 * The first checkpoint at which two models run different stages.
 *
 * Switching models is an edit at that checkpoint: everything before it is the
 * same galaxy, everything from it on is not. Read from both models' /api/stages
 * rather than written down, so a third model needs nothing here.
 */
export function firstDifference(a: Checkpoint[], b: Checkpoint[]): number | null {
  const count = Math.max(a.length, b.length);
  for (let i = 0; i < count; i += 1) {
    const x = a[i];
    const y = b[i];
    if (!x || !y || x.stages.join() !== y.stages.join()) return (x ?? y).n;
  }
  return null;
}

// --- controls ---------------------------------------------------------------

/** A control spanning two decades or more is dragged in log space. */
export function isLog(input: InputDecl): boolean {
  const { lo, hi } = input;
  return lo != null && hi != null && lo > 0 && hi / lo >= 100;
}

export const SLIDER_STEPS = 1000;

/** A control's value to a slider position in [0, SLIDER_STEPS]. */
export function toSlider(input: InputDecl, value: number): number {
  const lo = input.lo as number;
  const hi = input.hi as number;
  const t = isLog(input) ? Math.log(value / lo) / Math.log(hi / lo) : (value - lo) / (hi - lo);
  return Math.round(Math.min(Math.max(t, 0), 1) * SLIDER_STEPS);
}

/**
 * A slider position back to a value, rounded to four significant figures so a
 * drag does not send 1.0999999999e12 to the API. The ends are the published
 * bounds exactly, so the range check in flow.setValue never trips on rounding.
 */
export function fromSlider(input: InputDecl, position: number): number {
  const lo = input.lo as number;
  const hi = input.hi as number;
  if (position <= 0) return lo;
  if (position >= SLIDER_STEPS) return hi;
  const t = position / SLIDER_STEPS;
  const raw = isLog(input) ? lo * (hi / lo) ** t : lo + t * (hi - lo);
  return Math.min(Math.max(Number(raw.toPrecision(4)), lo), hi);
}

/**
 * A short, stable name for one run: FNV-1a over the input vector, six hex digits.
 * Not a security hash; two runs with the same inputs and model share it, and
 * any change to either gives a different one, which is all the top bar needs.
 */
export function runHash(query: Record<string, unknown>): string {
  const text = JSON.stringify(Object.keys(query).sort().map((k) => [k, query[k]]));
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, "0").slice(0, 6);
}

// --- numbers ------------------------------------------------------------------

const SUPERSCRIPT: Record<string, string> = {
  "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻",
};
const MINUS = "−"; // a real minus sign (design readme, "Numbers are never rounded away")

/** An exact power of ten as "10¹²", for log-axis ticks where the mantissa is always 1. */
export function formatPower(value: number): string {
  const k = Math.round(Math.log10(value));
  if (k >= -2 && k <= 3) return formatNumber(10 ** k);
  return `10${String(k).replace(/./g, (c) => SUPERSCRIPT[c] ?? c)}`;
}

/** 1.1e12 as "1.10 × 10¹²"; ordinary magnitudes plainly; always a real minus sign. */
export function formatNumber(value: number, digits = 3): string {
  if (!Number.isFinite(value)) return "—";
  const magnitude = Math.abs(value);
  let text: string;
  if (magnitude !== 0 && (magnitude >= 1e5 || magnitude < 1e-3)) {
    const [mantissa, exponent] = value.toExponential(digits - 1).split("e");
    const power = String(Number(exponent)).replace(/./g, (c) => SUPERSCRIPT[c] ?? c);
    text = `${mantissa} × 10${power}`;
  } else {
    text = String(Number(value.toPrecision(digits)));
  }
  return text.replace(/^-/, MINUS);
}
