// What a checkpoint shows — which is a question about declarations, so it is
// answered here rather than in the wiring, and can be asserted.
//
// The rule with teeth in it is the last one. A stage that publishes a star
// catalogue also publishes a scalar counting it, and asking for that scalar runs
// the stage — materialising the galaxy's whole sample to put one number on the
// screen, right beside a region query that deliberately did not. That is rule
// D4's waste committed by the client instead of the endpoint, and the viewer
// avoids it the way everything else here is decided: from the declarations. A
// scalar whose stage also publishes object columns is not asked for; the region
// response's own census says what was drawn.
//
// Nothing here knows the name of a field, a stage or a checkpoint.

/** The stages that publish objects — a catalogue is materialised by region, never by field. */
export function catalogueStages(fields) {
  return new Set(fields.filter((f) => f.domain === "object").map((f) => f.stage));
}

export function publishedAt(fields, n) {
  return fields.filter((f) => f.checkpoint === n);
}

/** Fields at this checkpoint that can be drawn as a picture. */
export function drawableAt(fields, n) {
  return publishedAt(fields, n).filter((f) => f.domain === "grid");
}

/** Scalars worth asking for here: everything but the ones that would build a catalogue. */
export function scalarsAt(fields, n) {
  const catalogues = catalogueStages(fields);
  return publishedAt(fields, n).filter((f) => f.domain === "galaxy" && !catalogues.has(f.stage));
}

/** Radial profiles available by checkpoint n — what the face-on disc can be drawn from. */
export function radialUpTo(fields, n) {
  return fields.filter((f) => f.checkpoint <= n && f.domain === "grid" && f.axes.length === 1 && f.axes[0] === "R");
}

/** True once some stage at or before n publishes object columns: there is a sample to draw. */
export function hasCatalogue(fields, n) {
  return fields.some((f) => f.domain === "object" && f.checkpoint <= n);
}

/** Whether anything published varies with φ. While nothing does, the disc is a revolution (debt #23). */
export function variesWithPhi(fields) {
  return fields.some((f) => f.axes.includes("phi"));
}

/**
 * The exact set of field names to ask for at checkpoint n.
 *
 * The disc under everything, the field being previewed, and this checkpoint's
 * scalars — and nothing else, so the closure the API runs is the one the picture
 * needs (rule D4).
 */
export function wanted(fields, n, picked) {
  const names = new Set();
  const disc = discField(fields, n, picked);
  if (disc) names.add(disc.name);
  const chosen = fields.find((f) => f.name === picked);
  if (chosen && chosen.domain === "grid") names.add(chosen.name);
  for (const f of scalarsAt(fields, n)) names.add(f.name);
  return [...names];
}

/** The radial field the face-on disc is drawn from: the picked one if it is radial, else the latest. */
export function discField(fields, n, picked) {
  const radial = radialUpTo(fields, n);
  return radial.find((f) => f.name === picked) ?? radial.at(-1) ?? null;
}

/**
 * What to open a checkpoint on: the last field published there.
 *
 * Last rather than first: /api/fields comes back in execution order, so the last
 * entry is what the latest stage made. First would open checkpoint one on the
 * model-boundary canary, which is not physics. This is a choice about what to
 * look at, never about how it is drawn — that stays in the declaration (A9).
 */
export function defaultField(fields, n) {
  return (drawableAt(fields, n).at(-1) ?? radialUpTo(fields, n).at(-1) ?? null)?.name ?? null;
}
