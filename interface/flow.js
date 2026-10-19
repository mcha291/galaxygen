// The inputs of one galaxy, in their groups: rule D1 (as amended at D232) as state, with no DOM in it.
//
// D1 reads, since BUILD_III's Phase V9 (S68): *the viewer shows one galaxy at a time and never a galaxy that is
// half one input set and half another.* Every input is editable at any time, in its registry group; seeds are
// rerolled; "Generate" regenerates the galaxy whole from the inputs shown, and until it returns the previous galaxy
// stays on screen, marked stale; "Reset to template" returns the inputs to the template's.
//
// The first sentence is what the staged flow of the first three builds was for, and it is kept: a preview must
// agree with the inputs that made it. A view drawn half from one input set and half from another is a galaxy that
// does not exist, and it is wrong in a way nobody can see by looking. The staged flow kept it by locks - a
// confirmed checkpoint could not be edited, and reopening one discarded every later result. The panel keeps it by
// construction instead: a viewer holds two input vectors, the **draft** being edited and the **shown** one whose
// galaxy is on screen, and every view asks with the shown one alone. Only "Generate" makes the draft the shown, and
// it moves the whole vector at once. Nothing here locks, confirms or reopens; there is nothing left to.
//
// This module is the draft's half: the groups (`catalogue`), a fresh draft at the published defaults (`initial`),
// one edit held to its published range and type (`setValue`), a reroll of the named seeds (`reroll`), a group's
// seeds (`seedsAt`), the vector as the API takes it (`query`), and which groups two vectors differ in
// (`changedGroups`) - the dirty marker. Keeping them here, as pure functions over a plain object, is what lets
// them be asserted (tests/js/flow.test.mjs) rather than demonstrated.
//
// Nothing here is stored anywhere. There is no localStorage in this viewer at all (rule D5): the state lives in
// memory, and a reload lands on the published defaults because that is the only state there is.

export const UNSET_CHECKPOINT = 1; // where an input with no group of its own belongs

export class FlowError extends Error {
  constructor(message) {
    super(message);
    this.name = "FlowError";
  }
}

/**
 * Fold /api/stages and /api/inputs into the groups the panel shows: the checkpoints the stage graph declares,
 * each with the inputs that belong to it. The groups are names for convenience, with no order a user must walk.
 *
 * Both are declarations; nothing is invented here. A group with no stages is kept rather than dropped - "nothing
 * is built here yet" is a true and useful thing for the viewer to say.
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

/** A fresh draft: every value its published default. */
export function initial(cat) {
  const values = {};
  for (const [name, input] of cat.inputs) values[name] = input.default;
  return { cat, values };
}

/** The group an input belongs to. */
export function checkpointOf(state, name) {
  const input = state.cat.inputs.get(name);
  if (!input) throw new FlowError(`${name} is not an input of model ${state.cat.model}`);
  return input.checkpoint ?? UNSET_CHECKPOINT;
}

/** One edit, at any time: held to the published range of a control and to an integer for a seed. */
export function setValue(state, name, value) {
  checkpointOf(state, name); // an input the model does not have is refused, not sent
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

/**
 * Reroll the named seeds and nothing else: a name that is not a seed of this model is skipped.
 *
 * `draw` is supplied by the caller so this stays a pure function of its arguments; the viewer passes a random
 * source, the tests pass a counter.
 */
export function reroll(state, names, draw) {
  let next = state;
  for (const name of names) {
    const input = state.cat.inputs.get(name);
    if (!input || input.kind !== "seed") continue;
    next = { ...next, values: { ...next.values, [name]: draw(name) } };
  }
  return next;
}

/** The seeds of a group, each of which the panel rerolls by name. */
export function seedsAt(state, n) {
  const cp = state.cat.checkpoints.find((c) => c.n === n);
  return cp ? cp.inputs.filter((name) => state.cat.inputs.get(name).kind === "seed") : [];
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

/**
 * The groups of `state`'s catalogue in which two input vectors (as `query` gives them) differ, in the
 * catalogue's order: the panel's dirty marker, with `a` the draft's vector and `b` the shown galaxy's. An input
 * the other vector does not have (another model's) counts as changed.
 */
export function changedGroups(state, a, b) {
  const changed = new Set();
  for (const name of state.cat.inputs.keys()) {
    if (a[name] !== b[name]) changed.add(checkpointOf(state, name));
  }
  return state.cat.checkpoints.map((cp) => cp.n).filter((n) => changed.has(n));
}
