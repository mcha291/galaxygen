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
 * today, the stellar pattern's contrast. Read from a part's `weight_fields` in the header's `ages`.
 */
export const PLACING_FIELDS = Object.freeze(["gas_density_contrast", "sfr_modulation", "pattern_density_contrast"]);

/** What the field regime asks /api/arrays for beside the render: the bulge's scale radius, and nothing else. */
export const FIELD_SCALARS = Object.freeze(["bulge_scale_radius"]);

/** Every part on: the parts' sum, the whole of the stars' light. */
export const ALL_AGES = Object.freeze({ young: 1, middle: 1, old: 1 });

const same = (a, b) => Array.isArray(a) && a.length === b.length && a.every((x, i) => x === b[i]);

/**
 * The parts a render carries and how each is drawn, youngest first; null unless all three are there and drawable
 * (the viewer then draws `stars`, the whole). The route's header says it under `ages.parts`, by part: `array` (the
 * part's per-ring (R, filter) array), `weight` (the (R, phi) array that places it), `weight_fields` (the published
 * fields that weight is made from) and `ages_gyr`. Each part returned: its name, switch key and label, its unit (the
 * stars component's, which it is a share of), the field that places it (the first placing field among the weight's
 * fields, else the weight's name: an even ring when the model publishes no pattern), `weight` - the (R, phi) array,
 * or null where the route has placed the part itself on (R, phi, filter) - and its ages, Gyr. `arrays` is the
 * render's arrays (only the names are read).
 */
export function ageParts(header, arrays) {
  const declared = header?.ages?.parts;
  if (!declared || !arrays) return null;
  const axes = header.axes ?? {};
  const out = [];
  for (const part of AGE_PARTS) {
    const entry = declared[part.key];
    if (!entry || typeof entry !== "object") return null;
    const name = typeof entry.array === "string" ? entry.array : part.name;
    if (!(name in arrays)) return null;
    const ax = axes[name];
    let weight = null;
    if (same(ax, ["R", "phi", "filter"])) {
      weight = null;
    } else if (ax === undefined || same(ax, ["R", "filter"])) {
      const w = entry.weight;
      if (typeof w !== "string" || !(w in arrays) || (axes[w] !== undefined && !same(axes[w], ["R", "phi"]))) return null;
      weight = w;
    } else {
      return null;
    }
    const fields = Array.isArray(entry.weight_fields) ? entry.weight_fields : [];
    out.push({
      ...part,
      name,
      unit: header.components?.stars?.unit ?? null,
      placedBy: fields.find((f) => PLACING_FIELDS.includes(f)) ?? fields[0] ?? weight,
      weight,
      ages: Array.isArray(entry.ages_gyr) ? entry.ages_gyr : null,
    });
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

// --- the young light clustered in the march (S66, BUILD_III V7; D226 R5) -----------------------------------------
// The field mode's young part keeps every clustering octave (its stars are younger than every octave's survival age),
// and the middle part's light is split by the route at those ages into the light that keeps 3, 2 and 1 octaves and the
// rest that keeps none (the header's `ages.middle_kept`, three per-ring arrays; the rest is `stars_middle` less their
// sum). The march multiplies each kept share by the clustering field's k-octave map over its level-0 cell's k-octave
// mean, per sub-step; here they are only split and placed - the same multiplications by published weights as
// agedLight, nothing evaluated.

/** The octave counts a share is clustered by, in the order the march's three clump textures hold them. */
export const KEPT_OCTAVES = Object.freeze([3, 2, 1]);

/**
 * The middle part's kept arrays as the render names them: { arrays: { 3, 2, 1 } (each a per-ring (R, filter) array
 * among `arrays`), weight } - or null where the header names none, or one is missing (the march then draws the parts as
 * agedLight does: nothing invented).
 */
export function keptParts(header, arrays) {
  const kept = header?.ages?.middle_kept;
  if (!kept || typeof kept !== "object" || !arrays) return null;
  const names = {};
  for (const k of KEPT_OCTAVES) {
    const name = kept.arrays?.[String(k)];
    if (typeof name !== "string" || !(name in arrays)) return null;
    names[k] = name;
  }
  return { arrays: names };
}

/**
 * The stellar layer split for the clustered march: `rest` (the old part and the middle part's light that keeps no
 * octave) and `clumps` [k = 3, 2, 1] - the young part with the middle's 3-octave light (both are multiplied by the
 * 3-octave map), the middle's 2-octave and its 1-octave light - each row-major over (R, phi, filter) and placed as
 * agedLight places its part (the middle's shares by the middle part's weight), each part times its switch. The four
 * sum to agedLight's sum per cell and filter, to rounding: a ring's light is where it was before any map multiplies it.
 * The middle part must be a per-ring part with a weight (keptParts' caller checks): its shares are per ring too.
 */
export function clumpedLight(arrays, parts, kept, gains, n) {
  const cells = n.R * n.phi;
  const rest = new Float64Array(cells * n.filter);
  const clumps = KEPT_OCTAVES.map(() => new Float64Array(cells * n.filter));
  const middleKept = KEPT_OCTAVES.map((k) => arrays[kept.arrays[k]]);
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
          const at = weight ? i * n.filter + k : c * n.filter + k;
          const v = Number(values[at]);
          if (!Number.isFinite(v)) continue;
          const q = c * n.filter + k;
          if (part.key === "young") {
            clumps[0][q] += g * w * v;
          } else if (part.key === "middle") {
            let left = v;
            middleKept.forEach((share, s) => {
              const x = Number(share[i * n.filter + k]); // the kept shares are per ring (R, filter)
              if (!Number.isFinite(x)) return;
              clumps[s][q] += g * w * x;
              left -= x;
            });
            rest[q] += g * w * left;
          } else {
            rest[q] += g * w * v;
          }
        }
      }
    }
  }
  return { rest, clumps };
}
