// The field's edge (S105, BUILD_VIII row 105): the render's grid ends at rHi (30 kpc) and every texture reads zero
// beyond it, which a stretched picture shows as a hard circle face-on and a hard ellipse inclined. Under the
// illustrative look every emission and every depth of the march is multiplied by a taper over the last `width` kpc
// before rHi. A display choice of the illustrative look (D275).

import type { IllFeature } from "./feature";

export const edge: IllFeature = {
  id: "edge",
  label: "edge",
  about: "A taper of all the field's light and dust over the last kpc before the grid's outer radius, so the disc never ends in a hard circle.",
  controls: [
    {
      key: "width", label: "edge taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 8,
      about: "The field's light and dust taken smoothly to nothing over this many kpc inside the grid's end (30 kpc); 0 the hard edge. Illustrative.",
    },
  ],
  glsl: /* glsl */ `
  uniform float illEdgeWidth;
  float illEdgeTaper(float r) {
    if (illEdgeWidth <= 0.0) return 1.0;
    return 1.0 - smoothstep(rHi - illEdgeWidth, rHi, r);
  }
`,
  hooks: { edge: "illEdgeTaper" },
  uniforms: (p) => ({ illEdgeWidth: p.width ?? 0 }),
};
