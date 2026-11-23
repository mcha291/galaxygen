// The framing (S105, BUILD_VIII row 105): the template's stand puts the camera at radius_kpc (half the picture's height
// at the centre), which leaves the disc small in the frame beside the goal pictures. Under the illustrative look the
// stand's radius is multiplied by this; the lens, inclination and azimuth are the template's. Illustrative (D275).

import type { IllFeature, IllParams } from "./feature";

export const framing: IllFeature = {
  id: "framing",
  label: "framing",
  about: "The template stand's framing radius, multiplied: below 1 the disc fills more of the frame.",
  controls: [
    {
      key: "scale", label: "framing", min: 0.3, max: 1.5, step: 0.01, unit: "×", default: 1,
      perTemplate: { milky_way: 0.82, ngc_4414: 0.8 },
      about: "A multiplier on the template camera's framing radius (half the picture's height at the centre): below 1 closer. Remakes the view's camera. Illustrative.",
    },
  ],
};

/** The stand's radius multiplier. */
export const standScale = (p: IllParams): number => p.scale ?? 1;
