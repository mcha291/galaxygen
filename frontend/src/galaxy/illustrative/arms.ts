// The arms (BUILD_VIII row 108, S108): a STUB from S105. The young light sharpened onto the arms' ridges, and its
// sparkle. Fill in this file only (index.ts's header is the contract): controls, `arrays` (the arm pieces), uniforms,
// and a body for illArmsYoung, a multiplier on the young starlight at rp. Neutral until then: 1.

import type { IllFeature } from "./feature";

export const arms: IllFeature = {
  id: "arms",
  label: "arms",
  about: "The young light sharpened onto the arms' ridges (row 108; not built yet).",
  controls: [],
  glsl: /* glsl */ `
  float illArmsYoung(vec2 rp) {
    return 1.0;
  }
`,
  hooks: { youngGain: "illArmsYoung" },
};
