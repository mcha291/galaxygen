// The pink HII regions (BUILD_VIII row 106, S106): a STUB from S105. HII regions drawn at a visible size in H-alpha's
// colour with a white-blue core, gathered to the arms. Fill in this file only (index.ts's header is the contract): its
// controls, a `layer` (a component drawn in the Galaxy view's canvas, given the knots, their gain and the march's dust)
// and `replacesKnots` where it draws in place of the field mode's default knots. Neutral until then: nothing drawn.

import type { IllFeature } from "./feature";

export const knots: IllFeature = {
  id: "knots",
  label: "HII regions",
  about: "The HII regions drawn pink at a visible size (row 106; not built yet).",
  controls: [],
};
