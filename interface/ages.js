// The field's starlight by age (S63, D223; BUILD_III Phase V5): what /api/render serves of it and how the viewer
// draws it. No fetch, no colour, no physics: a reading of the render's header and a sum of its arrays.
//
// The route returns the stars' light in three age parts - `stars_young` (under 20 Myr), `stars_middle` (20 to
// 100 Myr), `stars_old` - each the field's light of that part through the curves on its own, per ring and filter,
// summing to `stars` per ring and filter. The header names, for each part, the (R, phi) array that places it round
// the ring - the young by the gas's weight (the dust's placement), the middle by sfr_modulation normalised per
// ring, the old by the stellar pattern's contrast - each averaging to 1 round every ring. The viewer multiplies a
// part's ring value by its weight at each cell, as D207 places the dust: a published value times a published
// weight, nothing evaluated (rule D5). The three are layers of the one stellar layer, each through the same colour
// path as `stars` (its own response in each filter over the white point), switched by a multiplier; all three on
// draw the parts' sum.
//
// A part the route had placed itself, on (R, phi, filter), is drawn as it comes. A per-ring part whose weight the
// header does not name among the render's arrays is not drawable, and the viewer draws `stars` as before.

/** The three parts, youngest first, as the route names them, and the words the viewer's switches use. */
export const AGE_PARTS = Object.freeze([
  Object.freeze({ name: "stars_young", key: "young", label: "young stars" }),
  Object.freeze({ name: "stars_middle", key: "middle", label: "middle-aged stars" }),
  Object.freeze({ name: "stars_old", key: "old", label: "old stars" }),
]);

/**
 * The published fields that place light round a ring (D210, D218, D223): the gas's own contrast, where stars form
 * today, the stellar pattern's contrast. Read from a part's `fields` when its entry carries no `placed_by`.
 */
export const PLACING_FIELDS = Object.freeze(["gas_density_contrast", "sfr_modulation", "pattern_density_contrast"]);

/** What the field regime asks /api/arrays for beside the render: the bulge's scale radius, and nothing else. */
export const FIELD_SCALARS = Object.freeze(["bulge_scale_radius"]);

/** Every part on: the parts' sum, the whole of the stars' light. */
export const ALL_AGES = Object.freeze({ young: 1, middle: 1, old: 1 });

const same = (a, b) => Array.isArray(a) && a.length === b.length && a.every((x, i) => x === b[i]);

/**
 * The field a part's header entry names as its placement: its `placed_by` (or `placement`) where the route says so
 * in one word, else the first of its `fields` that is a placing field; null when it names none (an even ring).
 */
export function placingField(entry) {
  if (!entry || typeof entry !== "object") return null;
  if (typeof entry.placed_by === "string" && entry.placed_by) return entry.placed_by;
  const fields = Array.isArray(entry.fields) ? entry.fields : [];
  return fields.find((f) => PLACING_FIELDS.includes(f)) ?? null;
}

/**
 * The (R, phi) array among the render's that places a per-ring part: named in the header's `placement` under the
 * part's name (as `placement.dust` names the dust's), or in the part's own entry (`placement`, `weight`). Null when
 * none is named, or the name is not among the arrays.
 */
function weightOf(header, entry, name, arrays) {
  const candidates = [header.placement?.[name], entry.placement, entry.weight];
  for (const c of candidates) if (typeof c === "string" && c in arrays) return c;
  return null;
}

/**
 * The parts a render carries and how each is drawn, youngest first; null unless all three are there and drawable
 * (the viewer then draws `stars`, the whole). Each: its name, switch key and label, its unit, the field that places
 * it, and `weight` - null when the route has placed it on (R, phi, filter), else the name of the (R, phi) array that
 * places its per-ring light. `arrays` is the render's arrays (only the names are read).
 */
export function ageParts(header, arrays) {
  if (!header || !arrays) return null;
  const components = header.components ?? {};
  const axes = header.axes ?? {};
  const out = [];
  for (const part of AGE_PARTS) {
    const entry = components[part.name];
    if (!entry || !(part.name in arrays)) return null;
    let weight = null;
    const ax = axes[part.name];
    if (ax === undefined || same(ax, ["R", "phi", "filter"])) {
      weight = null;
    } else if (same(ax, ["R", "filter"])) {
      const named = weightOf(header, entry, part.name, arrays);
      if (named === null || (axes[named] !== undefined && !same(axes[named], ["R", "phi"]))) return null;
      weight = named;
    } else {
      return null;
    }
    out.push({ ...part, unit: entry.unit ?? null, placedBy: placingField(entry) ?? weight, weight });
  }
  return out;
}

/**
 * The stellar layer the march draws: each part's light times its switch, summed, row-major over (R, phi, filter)
 * as `stars` is. `n` is { R, phi, filter }. A part with a `weight` is its per-ring light times that (R, phi) weight
 * (a weight that is not a number is an even ring, 1, as the dust's placement is read). A value that is not a
 * number is no light from that part. All switches at 1 is the parts' sum.
 */
export function agedLight(arrays, parts, gains, n) {
  const cells = n.R * n.phi;
  const out = new Float64Array(cells * n.filter);
  for (const part of parts) {
    const g = Number(gains?.[part.key] ?? 1);
    if (!(g > 0)) continue;
    const values = arrays[part.name];
    const weight = part.weight ? arrays[part.weight] : null;
    for (let i = 0; i < n.R; i += 1) {
      for (let j = 0; j < n.phi; j += 1) {
        const c = i * n.phi + j;
        let w = 1;
        if (weight) {
          const x = Number(weight[c]);
          w = Number.isFinite(x) && x >= 0 ? x : 1;
        }
        for (let k = 0; k < n.filter; k += 1) {
          const v = Number(weight ? values[i * n.filter + k] : values[c * n.filter + k]);
          if (Number.isFinite(v)) out[c * n.filter + k] += g * w * v;
        }
      }
    }
  }
  return out;
}

/**
 * The closure D223 rules: the parts' light round each ring against `stars`'s, per ring and filter, as the largest
 * relative departure over the rings and filters where `stars` has light. Each ring's light is its cells' sum (the
 * cells of a ring share one area), so a part placed by its own weight closes on the ring, not cell by cell.
 */
export function ringClosure(arrays, parts, n) {
  const summed = agedLight(arrays, parts, ALL_AGES, n);
  const stars = arrays.stars;
  let worst = 0;
  for (let i = 0; i < n.R; i += 1) {
    for (let k = 0; k < n.filter; k += 1) {
      let a = 0;
      let b = 0;
      for (let j = 0; j < n.phi; j += 1) {
        const c = (i * n.phi + j) * n.filter + k;
        a += summed[c];
        b += Number(stars[c]);
      }
      if (b > 0) worst = Math.max(worst, Math.abs(a / b - 1));
    }
  }
  return worst;
}
