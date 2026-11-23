// The dust lanes (BUILD_VIII row 107, S107): a STUB from S105. Continuous, narrow, translucent reddening lanes along
// the arms' ridges and the bar's leading edges. Fill in this file only (index.ts's header is the contract): add
// controls, `arrays` (the arm pieces, e.g. arm_piece_start_radius ...), a `uniforms` that rasterises a polar A_V map
// into a texture (memoOn), and a body for illLanesAv that reads it (illPolar). Neutral until then: no A_V.

import type { IllFeature } from "./feature";

export const lanes: IllFeature = {
  id: "lanes",
  label: "dust lanes",
  about: "Dust lanes along the arms and the bar (row 107; not built yet).",
  controls: [],
  glsl: /* glsl */ `
  float illLanesAv(vec2 rp) {
    return 0.0;
  }
`,
  hooks: { dustAv: "illLanesAv" },
};
