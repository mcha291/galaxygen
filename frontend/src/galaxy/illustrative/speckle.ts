// The speckle (S105, BUILD_VIII row 105): in the field mode at galaxy scale the 20 000-star sample is drawn as
// fixed-pixel points over the field (GalaxyTab's sampled layer, at the regime's weight), an even sprinkle of dots the
// goal pictures do not have. Under the illustrative look its opacity is multiplied by this. Illustrative (D275).

import type { IllFeature, IllParams } from "./feature";

export const speckle: IllFeature = {
  id: "speckle",
  label: "speckle",
  about: "The 20 000-star sample's fixed-pixel points at galaxy scale, multiplied: 0 hides the even speckle.",
  controls: [
    {
      key: "opacity", label: "sample points", min: 0, max: 1, step: 0.01, unit: "×", default: 0,
      about: "A multiplier on the whole-galaxy star sample's opacity in the field mode (the regime's weight times this); 0 hides its uniform speckle. Illustrative.",
    },
  ],
};

/** The sample layer's opacity multiplier. */
export const sampleOpacity = (p: IllParams): number => p.opacity ?? 0;
