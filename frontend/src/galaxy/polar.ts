import { cellAt } from "@interface/field.js";

import type { Axis } from "../preview/axes";

interface Paint {
  color(value: number): number[];
}

/**
 * A face-on image of Σ(R) × contrast(R, φ): a published radial profile times a
 * published (R, φ) factor, nearest cell in both, painted by the profile's ramp.
 *
 * Row y of the image is v = r sin φ and column x is u = r cos φ, which is the
 * frame DiscLayer's plane lays into the scene: stars at (r cos φ, h, −r sin φ)
 * land on the pixels of their own azimuth. Off the grid is transparent (rule B9).
 */
export function polarImage(
  profile: ArrayLike<number>,
  contrast: ArrayLike<number>,
  R: Axis,
  phi: Axis,
  paint: Paint,
  size = 512,
): { data: Uint8ClampedArray; width: number; height: number } {
  const data = new Uint8ClampedArray(size * size * 4);
  const half = size / 2;
  for (let y = 0; y < size; y += 1) {
    const v = ((y + 0.5 - half) / half) * R.hi;
    for (let x = 0; x < size; x += 1) {
      const u = ((x + 0.5 - half) / half) * R.hi;
      const i = cellAt(Math.hypot(u, v), R);
      if (i < 0) continue;
      let angle = Math.atan2(v, u);
      if (angle < 0) angle += 2 * Math.PI;
      const j = Math.min(phi.n - 1, Math.floor((angle / (2 * Math.PI)) * phi.n));
      const [r, g, b, a] = paint.color(profile[i] * contrast[i * phi.n + j]);
      const p = (y * size + x) * 4;
      data[p] = r;
      data[p + 1] = g;
      data[p + 2] = b;
      data[p + 3] = a;
    }
  }
  return { data, width: size, height: size };
}
