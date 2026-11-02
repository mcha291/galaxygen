import { useEffect, useState } from "react";
import { CanvasTexture, DataTexture, FloatType, LinearFilter, NearestFilter, RGBAFormat, SRGBColorSpace, type Texture } from "three";

import type { FilterSet } from "./filters";
import { type InstrumentFields, type Optics, type PsfTable, opticsOf } from "./hstPsf";
import { askPsfTable } from "./psfTableClient";
import type { PsfRequest } from "./psfTableJob";
import { psfProfile } from "./sprite";

// The default sprite's profile and its mean live in sprite.ts (no three.js there); re-exported here for their callers.
export { psfMean, psfProfile } from "./sprite";

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
  /** Each channel's deposited pattern (rgb × alpha) averaged over the sprite's square: the star-first mode's unit sum (D208). */
  mean: [number, number, number];
}

/** Each channel's mean of a float sprite's deposited pattern, channel × alpha, over its square (airyTexture's layout). */
export function patternMean(data: ArrayLike<number>): [number, number, number] {
  const texels = data.length / 4;
  const sum: [number, number, number] = [0, 0, 0];
  for (let p = 0; p < data.length; p += 4) {
    for (let k = 0; k < 3; k += 1) sum[k] += Number(data[p + k]) * Number(data[p + 3]);
  }
  return [sum[0] / texels, sum[1] / texels, sum[2] / texels];
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
    const texture = airyTexture(pivots);
    psf = { texture, size: 25, alphaTest: 0, mean: patternMean(texture.image.data as Float32Array) };
    instrumentCache.set(key, psf);
  }
  return psf;
}

/**
 * Which instrument a filter set's curves are (S67, D227 R1): its curves' SVO family, "HST/WFC3_UVIS2" for both of the
 * WFC3 sets, or null for a stand-in set. A template's instrument applies where the view's set is its own set's.
 */
export function instrumentOfSet(set: FilterSet | null | undefined): string | null {
  const svo = set?.psf?.kind === "airy" ? set.sources?.[0]?.svo : undefined;
  return svo ? svo.slice(0, svo.lastIndexOf(".")) : null;
}

/**
 * The optics a point is drawn with, for a template's instrument, the instrument's own set and the set in view (S67, D227
 * R1; S83, T11), or null for the display sprite (R2). The view's set the instrument's own (the same SVO family): the
 * template's numbers, any it does not read taken from the set's own optics where it carries them. Another set that
 * carries its own optics (JWST's NIRCam, which no template names): the set's telescope and detector at the template's
 * distance - the template's other numbers are another telescope's. Neither: null.
 */
export function viewOptics(instrument: InstrumentFields | null | undefined, ownSet: FilterSet | null | undefined, viewSet: FilterSet): Optics | null {
  if (!instrument) return null;
  const own = instrumentOfSet(ownSet);
  if (own && own === instrumentOfSet(viewSet)) return opticsOf(instrument, viewSet.optics ?? null);
  if (viewSet.optics) return opticsOf({ distance_mpc: instrument.distance_mpc, pixel_scale_arcsec: null }, viewSet.optics);
  return null;
}

/**
 * A point drawn as the instrument's image of a point at its physical size (S67, D227 R1, R3; hstPsf.ts): the table's
 * corner integral as a float texture of (cells + 1)^2 texels, read by texelFetch (FluxPoints psfCorner), and its scale.
 */
export interface PhysicalPsf {
  texture: DataTexture;
  cells: number;
  cellPc: number;
}

/** A table kept: the texture and the optics it was built for (the key's middle part). */
interface Kept {
  psf: PhysicalPsf;
  optics: string;
}

const physicalCache = new Map<string, Kept>();

/** What a set, the optics and the switch ask for: the table's key, its optics' key and the job, or null (R2: no optics). */
export function physicalAsk(set: FilterSet, optics: Optics | null, spikes: boolean): { key: string; optics: string; request: PsfRequest } | null {
  if (!optics || !set.sources?.length) return null;
  const pivots = set.sources.map((s) => s.pivot);
  const opticsKey = JSON.stringify(optics);
  return { key: `${pivots.join(",")}|${opticsKey}|${spikes}`, optics: opticsKey, request: { optics, pivots, spikes } };
}

/**
 * Keeps an arrived table as its texture (S82, #178 (ii)), and disposes every kept texture of other optics: the optics
 * changed, and their tables are not drawn again unless asked again.
 */
export function adoptPhysical(ask: { key: string; optics: string }, table: PsfTable): PhysicalPsf {
  const kept = physicalCache.get(ask.key);
  if (kept) return kept.psf;
  for (const [key, other] of physicalCache) {
    if (other.optics === ask.optics) continue;
    other.psf.texture.dispose();
    physicalCache.delete(key);
  }
  const nodes = table.cells + 1;
  const texture = new DataTexture(table.corners, nodes, nodes, RGBAFormat, FloatType);
  texture.minFilter = NearestFilter;
  texture.magFilter = NearestFilter;
  texture.needsUpdate = true;
  const psf = { texture, cells: table.cells, cellPc: table.cellPc };
  physicalCache.set(ask.key, { psf, optics: ask.optics });
  return psf;
}

/** The kept table under a key, if it has arrived. */
export function keptPhysical(key: string): PhysicalPsf | null {
  return physicalCache.get(key)?.psf ?? null;
}

/**
 * The table for a set's pivots under a template's optics, the obscured Airy (spikes off) or the pupil's transform with
 * its vanes and pads (on), as a hook (S82, #178 (ii)): built once per set, optics and switch in the PSF table worker
 * (psfTableClient.ts; the transform about 1 s and a table about 0.6 s, off the main thread since S82), its pupil image
 * dropped once the table is made. Until a new table arrives the last one drawn stays drawn (S81's mesh rule), none before
 * the first. Null where the optics are not all read (R2: the display sprite instead).
 */
export function usePhysicalPsf(set: FilterSet, optics: Optics | null, spikes: boolean): PhysicalPsf | null {
  const ask = physicalAsk(set, optics, spikes);
  const key = ask?.key ?? null;
  const [arrived, setArrived] = useState<PhysicalPsf | null>(null);
  useEffect(() => {
    if (!ask || physicalCache.has(ask.key)) return;
    let live = true;
    void askPsfTable(ask.key, ask.request).then((a) => {
      const psf = adoptPhysical(ask, a.table);
      if (live) setArrived(psf);
    });
    return () => {
      live = false;
    };
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps -- the key names everything the ask holds
  if (!key) return null;
  // The last drawn, while it is still kept (a table of other optics is disposed when the new optics' arrives).
  return keptPhysical(key) ?? ([...physicalCache.values()].some((k) => k.psf === arrived) ? arrived : null);
}
