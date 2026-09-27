import { CanvasTexture, DataTexture, FloatType, LinearFilter, RGBAFormat, SRGBColorSpace, type Texture } from "three";

import type { FilterSet } from "./filters";

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

/**
 * J1, the Bessel function of the first kind of order one, from its integral definition
 * J1(x) = (1/π) ∫₀^π cos(τ − x sin τ) dτ: the integrand is even and 2π-periodic, so the trapezoid over the whole
 * period converges geometrically - 128 points hold it to 1e-12 for |x| up to about 60, past any sprite's edge.
 */
export function besselJ1(x: number, points = 128): number {
  let sum = 0;
  for (let k = 0; k < points; k += 1) {
    const tau = (2 * Math.PI * k) / points;
    sum += Math.cos(tau - x * Math.sin(tau));
  }
  return sum / points;
}

/** The Airy pattern of a circular aperture, (2 J1(v) / v)², 1 at the centre; v = π D θ / λ. */
export function airy(v: number): number {
  if (Math.abs(v) < 1e-8) return 1;
  const a = (2 * besselJ1(v)) / v;
  return a * a;
}

/** Where the reddest channel's first dark ring sits, as a share of the sprite's radius: a display choice. */
export const AIRY_FIRST_RING = 0.16;
/** The first zero of J1 (v = 3.8317, 1.22 π: the 1.22 λ/D of the Rayleigh criterion), found here, not typed in. */
export function airyFirstZero(): number {
  let lo = 3;
  let hi = 4.5; // J1 changes sign once between these
  for (let k = 0; k < 60; k += 1) {
    const mid = 0.5 * (lo + hi);
    if (Math.sign(besselJ1(mid)) === Math.sign(besselJ1(lo))) lo = mid;
    else hi = mid;
  }
  return 0.5 * (lo + hi);
}

/**
 * A named instrument's sprite (S42): the Airy pattern per channel, each at a radius in proportion to its filter's
 * pivot wavelength (λ/D), so a star's red ring sits outside its blue one. Float RGBA: channel k is the pattern
 * over the brightest channel at that pixel, alpha the brightest, so an additive sprite deposits each channel's own
 * intensity - rings a hundredth of the core and fainter survive, which an 8-bit canvas would round away.
 */
export function airyTexture(pivots: readonly number[], size = 96): DataTexture {
  const longest = Math.max(...pivots);
  const edge = airyFirstZero() / AIRY_FIRST_RING; // v at the sprite's edge for the longest wavelength
  const data = new Float32Array(size * size * 4);
  const half = size / 2;
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      const r = Math.hypot(x + 0.5 - half, y + 0.5 - half) / half;
      const p = (y * size + x) * 4;
      if (r >= 1) continue;
      const channel = pivots.slice(0, 3).map((lam) => airy(r * edge * (longest / lam)));
      const peak = Math.max(...channel);
      for (let k = 0; k < 3; k += 1) data[p + k] = peak > 0 ? (channel[k] ?? 0) / peak : 0;
      data[p + 3] = peak;
    }
  }
  const texture = new DataTexture(data, size, size, RGBAFormat, FloatType);
  texture.minFilter = LinearFilter;
  texture.magFilter = LinearFilter;
  texture.needsUpdate = true;
  return texture;
}

/** What a star sprite is drawn with: the default PSF, or a named instrument's while its filter set is shown. */
export interface SpritePsf {
  texture: Texture;
  /** Pixels on screen. */
  size: number;
  alphaTest: number;
}

const instrumentCache = new Map<string, SpritePsf>();

/** The set's instrument sprite, or null for a set without one (the stand-in sets keep the default PSF). */
export function instrumentPsf(set: FilterSet): SpritePsf | null {
  if (set.psf?.kind !== "airy" || !set.sources?.length) return null;
  const pivots = set.sources.map((s) => s.pivot);
  const key = pivots.join(",");
  let psf = instrumentCache.get(key);
  if (!psf) {
    // The sprite is larger than the default's nine pixels so its first rings are resolved on screen; its core stays
    // about two pixels across in red, as the default's does.
    psf = { texture: airyTexture(pivots), size: 25, alphaTest: 0 };
    instrumentCache.set(key, psf);
  }
  return psf;
}
