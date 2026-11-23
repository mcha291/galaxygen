// The field's edge (S105, BUILD_VIII row 105): the render's grid ends at rHi (30 kpc) and every texture reads zero
// beyond it, which a stretched picture shows as a hard circle face-on and a hard ellipse inclined. Under the
// illustrative look every emission and every depth of the march is multiplied by a taper over the last `width` kpc
// before `radius` (at most rHi). A display choice of the illustrative look (D275).

import type { IllFeature } from "./feature";

export const edge: IllFeature = {
  id: "edge",
  label: "edge",
  about: "A taper of all the field's light and dust over the last kpc before the grid's outer radius, so the disc never ends in a hard circle.",
  controls: [
    {
      key: "radius", label: "edge radius", min: 2, max: 30, step: 0.5, unit: "kpc", default: 30, perTemplate: { milky_way: 22, ngc_4414: 20 },
      about: "Where the taper reaches nothing, kpc (at most the grid's 30): a template whose own light ends inside the grid (NGC 4414's disc near 20 kpc) is tapered to its own end. Illustrative.",
    },
    {
      key: "width", label: "edge taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 8, perTemplate: { milky_way: 12, ngc_4414: 8 },
      about: "The field's light and dust taken smoothly to nothing over this many kpc inside the grid's end (30 kpc); 0 the hard edge. Illustrative.",
    },
  ],
  glsl: /* glsl */ `
  uniform float illEdgeRadius;
  uniform float illEdgeWidth;
  float illEdgeTaper(float r) {
    float end = min(illEdgeRadius, rHi);
    if (illEdgeWidth <= 0.0) return r < end ? 1.0 : 0.0;
    return 1.0 - smoothstep(end - illEdgeWidth, end, r);
  }
`,
  hooks: { edge: "illEdgeTaper" },
  uniforms: (p) => ({ illEdgeRadius: p.radius ?? 30, illEdgeWidth: p.width ?? 0 }),
};
