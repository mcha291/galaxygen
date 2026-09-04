// The checkpoint flow: rule D1, as a state machine with no DOM in it.
//
// D1 is four statements, and every one of them is a claim about *state* rather
// than about pixels:
//
//   - a page load lands on stage one
//   - confirmed controls are disabled rather than hidden
//   - reopening a stage discards every later one
//   - a lock means "do not re-roll this", and can never mean "freeze this
//     against upstream changes"
//
// Keeping them here, as pure functions over a plain object, is what lets them be
// asserted (tests/js/flow.test.mjs) instead of demonstrated. A rule that only
// lives in event handlers is a rule that is checked by looking at the screen.
//
// The last of the four is the one with a trap in it. A lock protects a *value*
// from being re-rolled. It protects nothing from being invalidated: reopening an
// earlier checkpoint discards every later result whether or not its seed is
// locked, because the galaxy those results describe no longer exists. Locking
// `pattern_seed` and then changing the halo mass must keep the seed and discard
// the pattern.
//
// Nothing here is stored anywhere. There is no localStorage in this viewer at
// all (rule D5) — the state lives in memory, and a reload starts at stage one
// because that is the only state there is.

export const UNSET_CHECKPOINT = 1; // where an input with no checkpoint of its own belongs

export class FlowError extends Error {
  constructor(message) {
    super(message);
    this.name = "FlowError";
  }
}

/**
 * Fold /api/stages and /api/inputs into the checkpoint list the viewer walks.
 *
 * Both are declarations; nothing is invented here. A checkpoint with no stages
 * is kept rather than dropped — "nothing is built at this checkpoint yet" is a
 * true and useful thing for the viewer to say, and hiding it would make the
 * build look further along than it is.
 */
export function catalogue(stages, inputs) {
  const controls = [...inputs.controls, ...inputs.seeds, ...inputs.events];
  const checkpoints = stages.checkpoints.map((cp) => ({
    n: cp.n,
    name: cp.name,
    stages: cp.stages.slice(),
    inputs: controls.filter((i) => (i.checkpoint ?? UNSET_CHECKPOINT) === cp.n).map((i) => i.name),
  }));
  const byName = new Map(controls.map((i) => [i.name, i]));
  return { model: stages.model, checkpoints, inputs: byName, order: stages.order.slice() };
}

/** A fresh session: stage one, nothing confirmed, every value its published default. */
export function initial(cat) {
  const values = {};
  for (const [name, input] of cat.inputs) values[name] = input.default;
  return { cat, values, locked: {}, confirmed: 0, current: 1, previews: {} };
}

export function checkpointOf(state, name) {
  const input = state.cat.inputs.get(name);
  if (!input) throw new FlowError(`${name} is not an input of model ${state.cat.model}`);
  return input.checkpoint ?? UNSET_CHECKPOINT;
}

/** Editable exactly while its checkpoint is unconfirmed. Confirmed means disabled, never hidden. */
export function isEditable(state, name) {
  return checkpointOf(state, name) > state.confirmed;
}

export function setValue(state, name, value) {
  if (!isEditable(state, name)) {
    throw new FlowError(`${name} belongs to checkpoint ${checkpointOf(state, name)}, which is confirmed`);
  }
  const input = state.cat.inputs.get(name);
  if (input.kind === "control") {
    const number = Number(value);
    if (!Number.isFinite(number)) throw new FlowError(`${name} takes a number, got ${value}`);
    if (input.lo !== null && input.hi !== null && (number < input.lo || number > input.hi)) {
      throw new FlowError(`${name} = ${number} is outside its published range [${input.lo}, ${input.hi}]`);
    }
    value = number;
  } else if (input.kind === "seed") {
    if (!Number.isInteger(Number(value))) throw new FlowError(`${name} is a seed and takes an integer`);
    value = Number(value);
  }
  return { ...state, values: { ...state.values, [name]: value } };
}

/** Confirm the current checkpoint and move on. The last one confirms without advancing past itself. */
export function confirm(state) {
  const last = state.cat.checkpoints.length;
  const confirmed = Math.max(state.confirmed, state.current);
  return { ...state, confirmed, current: Math.min(state.current + 1, last) };
}

/**
 * Reopen checkpoint n: it and everything after it are unconfirmed, and every
 * later result is discarded. Not marked stale — discarded. A preview of a galaxy
 * that no longer exists is worse than no preview.
 */
export function reopen(state, n) {
  const last = state.cat.checkpoints.length;
  if (!Number.isInteger(n) || n < 1 || n > last) throw new FlowError(`no checkpoint ${n}`);
  const previews = {};
  for (const [k, v] of Object.entries(state.previews)) if (Number(k) < n) previews[k] = v;
  return { ...state, confirmed: n - 1, current: n, previews };
}

export function goTo(state, n) {
  const last = state.cat.checkpoints.length;
  if (!Number.isInteger(n) || n < 1 || n > last) throw new FlowError(`no checkpoint ${n}`);
  // Forward is a look, not a confirmation: you may only go as far as you have confirmed.
  if (n > state.confirmed + 1) throw new FlowError(`checkpoint ${n} needs ${n - 1} confirmed first`);
  return n < state.current && n <= state.confirmed ? reopen(state, n) : { ...state, current: n };
}

export function isLocked(state, name) {
  return Boolean(state.locked[name]);
}

/** Lock a seed against re-rolling. Only a seed: nothing else is ever re-rolled. */
export function toggleLock(state, name) {
  const input = state.cat.inputs.get(name);
  if (!input || input.kind !== "seed") throw new FlowError(`${name} is not a seed; only seeds are locked`);
  return { ...state, locked: { ...state.locked, [name]: !state.locked[name] } };
}

/**
 * Re-roll the named seeds — skipping the locked ones, refusing the confirmed ones.
 *
 * `draw` is supplied by the caller so this stays a pure function of its
 * arguments; the viewer passes a random source, the tests pass a counter.
 */
export function reroll(state, names, draw) {
  let next = state;
  for (const name of names) {
    const input = state.cat.inputs.get(name);
    if (!input || input.kind !== "seed") continue;
    if (isLocked(state, name) || !isEditable(state, name)) continue;
    next = { ...next, values: { ...next.values, [name]: draw(name) } };
  }
  return next;
}

/** The seeds of a checkpoint, which is what a re-roll button there re-rolls. */
export function seedsAt(state, n) {
  const cp = state.cat.checkpoints.find((c) => c.n === n);
  return cp ? cp.inputs.filter((name) => state.cat.inputs.get(name).kind === "seed") : [];
}

export function withPreview(state, n, preview) {
  return { ...state, previews: { ...state.previews, [n]: preview } };
}

/** The input vector as the API takes it: every value, events as JSON. */
export function query(state) {
  const out = {};
  for (const [name, input] of state.cat.inputs) {
    const value = state.values[name];
    out[name] = input.kind === "events" ? JSON.stringify(value) : value;
  }
  return out;
}
