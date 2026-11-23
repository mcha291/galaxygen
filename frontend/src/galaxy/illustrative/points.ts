// The points' edge (S108, builder H): under the illustrative look the field is tapered to nothing at the edge's radius
// (edge.ts: NGC 4414's at 11 kpc), but the star-first mode's points (its stars and clusters, FluxPoints) kept their
// whole light out to the grid's end, so large blue sprites spread to the frame's corners over a field that had already
// ended. Here each such point's light is multiplied by the field's own edge taper at the point's cylindrical radius (the
// `points` hook, index.ts; read in FluxPoints' vertex shader only, and only by the materials GalaxyTab marks illEdged:
// the field mode's knots are drawn as before), so the points fade with the field. The taper is the edge's (its radius and width sliders), without its
// bulge dimming (the points are the disc's stars, whose light the march gives back the bulge's share of). Display-only
// (D275): no published number moves; the physical look's points are untouched.

import type { IllFeature } from "./feature";

export const points: IllFeature = {
  id: "points",
  label: "points",
  about: "The star-first mode's points (its stars and clusters) faded with the field's edge taper.",
  controls: [
    {
      key: "edge", label: "points' edge", min: 0, max: 1, step: 0.01, unit: "×", default: 1,
      about: "How much of the field's edge taper (the edge's radius and width) the points take: 1 they fade with the field, 0 their whole light to the grid's end as before. Illustrative (S108).",
    },
  ],
  // The edge's GLSL (edge.ts, earlier in the registry) declares illEdgeRamp, illEdgeRadius and illEdgeWidth.
  glsl: /* glsl */ `
  uniform float illPointsEdge;
  float illPointsAt(vec2 rp) {
    if (illPointsEdge <= 0.0) return 1.0;
    return mix(1.0, illEdgeRamp(rp.x, min(illEdgeRadius, rHi), illEdgeWidth), illPointsEdge);
  }
`,
  hooks: { points: "illPointsAt" },
  uniforms: (p) => ({ illPointsEdge: p.edge ?? 1 }),
};
