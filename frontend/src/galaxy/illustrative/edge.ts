// The field's edge (S105, BUILD_VIII row 105): the render's grid ends at rHi (30 kpc) and every texture reads zero
// beyond it, which a stretched picture shows as a hard circle face-on and a hard ellipse inclined. Under the
// illustrative look every emission and every depth of the march is multiplied by a taper over the last `width` kpc
// before `radius` (at most rHi). A display choice of the illustrative look (D275).
//
// The fix pass (S105): the clustered young light (the march's clumped young and middle shares) is what reaches furthest
// out as grain - a ring of saturated flecks round both discs beyond about 15 kpc, where the smooth disc under it is
// already faint and the goals fade softly. It has a taper of its own (the youngGain hook), earlier than the field's, so
// the outer disc is the smooth light alone as it sinks into the sky.

import type { IllFeature } from "./feature";

export const edge: IllFeature = {
  id: "edge",
  label: "edge",
  about: "A taper of all the field's light and dust over the last kpc before the grid's outer radius, so the disc never ends in a hard circle; and an earlier one of the clustered young light alone, so the outer disc fades smooth.",
  controls: [
    {
      key: "radius", label: "edge radius", min: 2, max: 30, step: 0.5, unit: "kpc", default: 30, perTemplate: { milky_way: 21, ngc_4414: 13 },
      about: "Where the taper reaches nothing, kpc (at most the grid's 30): a template whose own light ends inside the grid (NGC 4414's disc near 20 kpc) is tapered to its own end. Illustrative.",
    },
    {
      key: "width", label: "edge taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 8, perTemplate: { milky_way: 10, ngc_4414: 8 },
      about: "The field's light and dust taken smoothly to nothing over this many kpc inside the grid's end (30 kpc); 0 the hard edge. Illustrative.",
    },
    {
      key: "young", label: "young edge", min: 2, max: 30, step: 0.5, unit: "kpc", default: 30, perTemplate: { milky_way: 13, ngc_4414: 9 },
      about: "Where the clustered young light's own taper reaches nothing, kpc: beyond it the outer disc is the smooth light alone, without its grain. 30 and a taper of 0: as drawn. Illustrative.",
    },
    {
      key: "youngwidth", label: "young taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 0, perTemplate: { milky_way: 8, ngc_4414: 4 },
      about: "The clustered young light taken smoothly to nothing over this many kpc inside the young edge; 0 a hard cut there. Illustrative.",
    },
  ],
  glsl: /* glsl */ `
  uniform float illEdgeRadius;
  uniform float illEdgeWidth;
  uniform float illEdgeYoungRadius;
  uniform float illEdgeYoungWidth;
  float illEdgeRamp(float r, float end, float width) {
    if (width <= 0.0) return r < end ? 1.0 : 0.0;
    return 1.0 - smoothstep(end - width, end, r);
  }
  float illEdgeTaper(float r) { return illEdgeRamp(r, min(illEdgeRadius, rHi), illEdgeWidth); }
  float illEdgeYoung(vec2 rp) { return illEdgeYoungRadius >= rHi && illEdgeYoungWidth <= 0.0 ? 1.0 : illEdgeRamp(rp.x, illEdgeYoungRadius, illEdgeYoungWidth); }
`,
  hooks: { edge: "illEdgeTaper", youngGain: "illEdgeYoung" },
  uniforms: (p) => ({
    illEdgeRadius: p.radius ?? 30,
    illEdgeWidth: p.width ?? 0,
    illEdgeYoungRadius: p.young ?? 30,
    illEdgeYoungWidth: p.youngwidth ?? 0,
  }),
};

/** The taper's value at radius r, kpc (the GLSL's twin): 1 inside end - width, 0 from end on, smooth between. */
export function edgeRamp(r: number, end: number, width: number): number {
  if (width <= 0) return r < end ? 1 : 0;
  const t = Math.min(1, Math.max(0, (r - (end - width)) / width));
  return 1 - t * t * (3 - 2 * t);
}
