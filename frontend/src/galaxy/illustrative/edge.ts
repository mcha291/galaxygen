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
      key: "radius", label: "edge radius", min: 2, max: 30, step: 0.5, unit: "kpc", default: 30, perTemplate: { milky_way: 16, ngc_4414: 16 },
      about: "Where the taper reaches nothing, kpc (at most the grid's 30): a template whose own light ends inside the grid (NGC 4414's disc near 20 kpc) is tapered to its own end. Illustrative.",
    },
    {
      key: "width", label: "edge taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 8, perTemplate: { milky_way: 9, ngc_4414: 14 },
      about: "The field's light and dust taken smoothly to nothing over this many kpc inside the grid's end (30 kpc); 0 the hard edge. Illustrative.",
    },
    {
      key: "young", label: "young edge", min: 2, max: 30, step: 0.5, unit: "kpc", default: 30, perTemplate: { milky_way: 13.5, ngc_4414: 14 },
      about: "Where the clustered young light's own taper reaches nothing, kpc: beyond it the outer disc is the smooth light alone, without its grain. 30 and a taper of 0: as drawn. Illustrative.",
    },
    {
      key: "youngwidth", label: "young taper", min: 0, max: 25, step: 0.5, unit: "kpc", default: 0, perTemplate: { milky_way: 5, ngc_4414: 8 },
      about: "The clustered young light taken smoothly to nothing over this many kpc inside the young edge; 0 a hard cut there. Illustrative.",
    },
    {
      key: "bulge", label: "bulge haze dimmed", min: 0, max: 0.95, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.5, ngc_4414: 0 },
      about: "The bulge's light (and the dust's, the HII's and the gas's) dimmed by this share round the bar - from none at the centre, full from the radius below, none again from the next - the disc's starlight kept: the pale haze round the bar thinned so the bar stands on a darker ground; 0 none. Illustrative (S106).",
    },
    {
      key: "bulgein", label: "bulge dim from", min: 0.1, max: 6, step: 0.05, unit: "kpc", default: 1, perTemplate: { milky_way: 1.5 },
      about: "The bulge's dimming (above) is full from this radius, kpc (rising smoothly from the centre). Illustrative (S106).",
    },
    {
      key: "bulgeout", label: "bulge dim to", min: 1, max: 20, step: 0.1, unit: "kpc", default: 8, perTemplate: { milky_way: 10 },
      about: "The bulge's dimming has faded to nothing at this radius, kpc (from half of it). Illustrative (S106).",
    },
    {
      key: "grazeRadius", label: "edge radius edge-on", min: 0, max: 30, step: 0.5, unit: "kpc", default: 0, perTemplate: { ngc_4414: 9.5 },
      about: "The edge radius handed over to toward edge-on (with the grazing handover, base.grazeFrom to base.grazeTo): the disc's own fall-offs are veils that fade there, so a wide face-on taper would let the smooth disc run on past the lane as a thin band; 0 the face-on radius kept. Face-on nothing moves. Illustrative (S110).",
    },
    {
      key: "grazeWidth", label: "edge taper edge-on", min: 0, max: 25, step: 0.5, unit: "kpc", default: 0, perTemplate: { ngc_4414: 4 },
      about: "The edge taper handed over to toward edge-on, kpc (with the edge radius edge-on); 0 with that radius at 0 the face-on taper kept. Illustrative (S110).",
    },
  ],
  glsl: /* glsl */ `
  uniform float illEdgeRadius;
  uniform float illEdgeWidth;
  uniform float illEdgeYoungRadius;
  uniform float illEdgeYoungWidth;
  uniform vec3 illEdgeBulge;
  float illEdgeRamp(float r, float end, float width) {
    if (width <= 0.0) return r < end ? 1.0 : 0.0;
    return 1.0 - smoothstep(end - width, end, r);
  }
  // S106 (B5): the bulge's dimming at cylindrical radius r (1 none). The edge hook multiplies every emission by it and
  // the light hook gives the disc's starlight it back, so in sum only the bulge (with the dust's, HII's and gas's own
  // light and the depths) is dimmed.
  // S108 (the handover, index.ts illGraze): the dimming's share handed back toward edge-on, where the model's round
  // bulge is the galaxy's shape; the same share in both hooks, so the disc's starlight stays undimmed throughout.
  float illEdgeBulgeAt(float r) {
    float share = illGraze >= 1.0 ? illEdgeBulge.x : illEdgeBulge.x * illGraze;
    return 1.0 - share * smoothstep(0.0, illEdgeBulge.y, r) * (1.0 - smoothstep(0.5 * illEdgeBulge.z, illEdgeBulge.z, r));
  }
  // S110 (B1): the taper's end and width handed over toward edge-on (illEdgeGraze: x the radius, y the width; x 0 none),
  // exactly the face-on pair while illGraze is 1.
  uniform vec2 illEdgeGraze;
  vec2 illEdgeEnd() {
    vec2 face = vec2(min(illEdgeRadius, rHi), illEdgeWidth);
    if (illGraze >= 1.0 || illEdgeGraze.x <= 0.0) return face;
    return mix(vec2(min(illEdgeGraze.x, rHi), illEdgeGraze.y), face, illGraze);
  }
  float illEdgeTaper(float r) {
    vec2 end = illEdgeEnd();
    float t = illEdgeRamp(r, end.x, end.y);
    return illEdgeBulge.x > 0.0 ? t * illEdgeBulgeAt(r) : t;
  }
  vec3 illEdgeDisc(vec2 rp) { return illEdgeBulge.x > 0.0 ? vec3(1.0 / illEdgeBulgeAt(rp.x)) : vec3(1.0); }
  float illEdgeYoung(vec2 rp) { return illEdgeYoungRadius >= rHi && illEdgeYoungWidth <= 0.0 ? 1.0 : illEdgeRamp(rp.x, illEdgeYoungRadius, illEdgeYoungWidth); }
`,
  hooks: { edge: "illEdgeTaper", youngGain: "illEdgeYoung", light: "illEdgeDisc" },
  // S108: the disc's light here is the bulge dimming's give-back, paired with the edge hook (handed over inside).
  graze: { light: "keep" },
  uniforms: (p) => ({
    illEdgeRadius: p.radius ?? 30,
    illEdgeWidth: p.width ?? 0,
    illEdgeYoungRadius: p.young ?? 30,
    illEdgeYoungWidth: p.youngwidth ?? 0,
    illEdgeBulge: [p.bulge ?? 0, p.bulgein ?? 1, Math.max(p.bulgeout ?? 8, 0.2)] as [number, number, number],
    illEdgeGraze: [Math.max(p.grazeRadius ?? 0, 0), Math.max(p.grazeWidth ?? 0, 0)] as [number, number],
  }),
};

/** The taper's value at radius r, kpc (the GLSL's twin): 1 inside end - width, 0 from end on, smooth between. */
export function edgeRamp(r: number, end: number, width: number): number {
  if (width <= 0) return r < end ? 1 : 0;
  const t = Math.min(1, Math.max(0, (r - (end - width)) / width));
  return 1 - t * t * (3 - 2 * t);
}
