// The far field (RENDER_PLAN R3): the disc's unresolved light as an image of linear
// radiance, drawn under the star sample in photometric mode. No three.js here.
//
// Everything in it is published: the surface brightness Σ_L(R), the colour of that
// light per radius (the blackbody colour of disc_light_temperature, through its
// declared ramp), and from checkpoint 4 the (R, φ) density contrast of the bar and
// arms. The viewer multiplies and lays them out, which is compositing (rule D5).

import type { Axis } from "../preview/axes";

/**
 * How bright 1 L☉/pc² draws against a star point, at zero exposure stops. A display
 * balance between the two layers, not a physical constant: a point is one star and
 * a pixel of the far field is a patch of disc, and there is no exposure at which
 * both are "right". At this value the inner disc's few hundred L☉/pc² sits near
 * unit intensity, as a 100 L☉ giant does.
 */
export const FAR_FIELD_PER_LSUN_PC2 = 1 / 400;

/**
 * Extinction in the viewer's red, green and blue channels per magnitude of A_V: the R, V
 * and B bands of the Cardelli, Clayton & Mathis law at R_V = 3.1 standing in for the three
 * channels `[recall: CCM 1989, A_R/A_V = 0.748, A_B/A_V = 1.324]`. Dust dims blue more
 * than red, so a dusty region reddens as it darkens: occlusion, never an added colour.
 */
export const CHANNEL_EXTINCTION = [0.748, 1.0, 1.324] as const;

/**
 * The fraction of its own light a face-on slab lets out when stars and dust are mixed
 * through it uniformly: (1 − e^−τ)/τ, with τ = A / 1.086 the optical depth for A
 * magnitudes. A screen in front would be e^−τ and would black out the dusty centre;
 * mixed, half the stars sit in front of half the dust.
 */
export function mixedSlab(magnitudes: number): number {
  const tau = magnitudes / 1.086;
  return tau < 1e-6 ? 1 : (1 - Math.exp(-tau)) / tau;
}

/** Linear interpolation of a profile on cell centres at radius r; NaN off the grid. */
function profileAt(profile: ArrayLike<number>, R: Axis, r: number): number {
  const x = (r - R.lo) / R.width - 0.5;
  if (r < R.lo || r > R.hi) return Number.NaN;
  const i = Math.max(0, Math.min(R.n - 2, Math.floor(x)));
  const f = Math.max(0, Math.min(1, x - i));
  return profile[i] * (1 - f) + profile[i + 1] * f;
}

/**
 * RGBA float image, `size` square over ±R.hi, in the frame polarImage uses: row y is
 * v = r sin φ, column x is u = r cos φ, so it lays into DiscLayer's plane and a star
 * at azimuth φ sits on its own pixels.
 *
 * `colour` is linear RGB per R cell (three per cell). `contrast`, when given, is the
 * published (R, φ) factor, row-major, read linearly in R and wrapping in φ. Pixels off
 * the grid, and radii whose brightness or colour is not a number, are left black: the
 * layer adds light, so black is nothing drawn (rule B9).
 */
export function farFieldImage(
  brightness: ArrayLike<number>,
  colour: ArrayLike<number>,
  R: Axis,
  gain: number,
  size = 512,
  contrast?: { values: ArrayLike<number>; phi: Axis },
  /** Face-on A_V per R cell; the dust is taken to follow the same arm contrast as the light. */
  extinction?: ArrayLike<number>,
): Float32Array {
  const data = new Float32Array(size * size * 4);
  const half = size / 2;
  for (let y = 0; y < size; y += 1) {
    const v = ((y + 0.5 - half) / half) * R.hi;
    for (let x = 0; x < size; x += 1) {
      const u = ((x + 0.5 - half) / half) * R.hi;
      const r = Math.hypot(u, v);
      const level = profileAt(brightness, R, r);
      if (!(level > 0)) continue;
      const cx = Math.max(0, Math.min(R.n - 1, Math.round((r - R.lo) / R.width - 0.5)));
      const cr = colour[3 * cx];
      if (!Number.isFinite(cr)) continue;

      let factor = 1;
      if (contrast) {
        const { values, phi } = contrast;
        let angle = Math.atan2(v, u);
        if (angle < 0) angle += 2 * Math.PI;
        const ax = (angle / (2 * Math.PI)) * phi.n - 0.5;
        const j0 = ((Math.floor(ax) % phi.n) + phi.n) % phi.n;
        const j1 = (j0 + 1) % phi.n;
        const fj = ax - Math.floor(ax);
        const rx = Math.max(0, Math.min(R.n - 2, Math.floor((r - R.lo) / R.width - 0.5)));
        const fr = Math.max(0, Math.min(1, (r - R.lo) / R.width - 0.5 - rx));
        const at = (i: number, j: number) => values[i * phi.n + j];
        factor =
          (at(rx, j0) * (1 - fj) + at(rx, j1) * fj) * (1 - fr) + (at(rx + 1, j0) * (1 - fj) + at(rx + 1, j1) * fj) * fr;
        if (!Number.isFinite(factor)) continue;
      }

      const intensity = level * factor * gain;
      const av = extinction ? Math.max(0, profileAt(extinction, R, r)) * factor : 0;
      const p = (y * size + x) * 4;
      data[p] = cr * intensity * mixedSlab(av * CHANNEL_EXTINCTION[0]);
      data[p + 1] = colour[3 * cx + 1] * intensity * mixedSlab(av * CHANNEL_EXTINCTION[1]);
      data[p + 2] = colour[3 * cx + 2] * intensity * mixedSlab(av * CHANNEL_EXTINCTION[2]);
      data[p + 3] = 1;
    }
  }
  return data;
}
