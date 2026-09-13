import { CanvasTexture, LinearFilter, SRGBColorSpace } from "three";

/**
 * A star's point spread function as a sprite (RENDER_PLAN R2): a Gaussian core
 * with Moffat-like wings, white, so the vertex colour carries the hue.
 *
 * This is the shape of an unresolved point seen through optics, not a property
 * of the star, so it lives in the renderer (rule D5 is about physics, and a PSF
 * is instrument). Returned as alpha: the sprite's brightness falls off from the
 * centre instead of stopping at a square's edge.
 */
export function psfProfile(r: number, core = 0.3, beta = 2.2): number {
  // r is 0 at the centre and 1 at the sprite's edge.
  const gauss = Math.exp(-(r * r) / (2 * core * core));
  const moffat = (1 + (r / (core * 1.6)) ** 2) ** -beta;
  const edge = Math.max(0, 1 - r) ** 2; // the wing reaches zero at the edge, never a hard ring
  return Math.min(1, (0.7 * gauss + 0.3 * moffat) * edge);
}

let cached: CanvasTexture | null = null;

export function psfTexture(size = 64): CanvasTexture {
  if (cached) return cached;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  const image = ctx.createImageData(size, size);
  const half = size / 2;
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const r = Math.hypot(x + 0.5 - half, y + 0.5 - half) / half;
      const p = (y * size + x) * 4;
      image.data[p] = 255;
      image.data[p + 1] = 255;
      image.data[p + 2] = 255;
      image.data[p + 3] = Math.round(255 * psfProfile(r));
    }
  }
  ctx.putImageData(image, 0, 0);
  cached = new CanvasTexture(canvas);
  cached.colorSpace = SRGBColorSpace;
  cached.minFilter = LinearFilter;
  cached.magFilter = LinearFilter;
  return cached;
}
