// NGC 4414's flocculent network (BUILD_VIII row 109, S109): a STUB from S105. The filament network of dust and the
// patchy young clumps of a flocculent disc. Fill in this file only (index.ts's header is the contract): its dust as
// illFlocAv (A_V, summed with the lanes'), and, if it brightens young light, a youngGain hook of its own. Neutral: no A_V.

import type { IllFeature } from "./feature";

export const floc: IllFeature = {
  id: "floc",
  label: "flocculent network",
  about: "The flocculent disc's filament network and clumps (row 109; not built yet).",
  controls: [],
  glsl: /* glsl */ `
  float illFlocAv(vec2 rp) {
    return 0.0;
  }
`,
  hooks: { dustAv: "illFlocAv" },
};
