// The clouds as extinction at whole-galaxy scale (S64, BUILD_III Phase V6; RULING_S64 R3-R4). No three.js here: the
// pure parts, tested.
//
// The model publishes each cloud's own dust column (/api/clouds' `cloud_dust_extinction_v`: its face-on mean A_V over
// its disc, from its own dust - its mass times the ring's dust-to-gas ratio times the ring's A_V per unit dust column,
// over pi cloud_size^2) and, on /api/render, the share of each ring's dust left diffuse once the realised clouds hold
// theirs (`dust_diffuse_share`, the header's `clouds`). Most clouds are smaller than a pixel of a whole-galaxy frame
// (74 % of the Milky Way's under its 39 pc pixel, the S64 probe), so the viewer rasterises the census into a polar
// texture of face-on A_V - the raster is the viewer's (R4), a display resolution that conserves what it is given:
// every cloud deposits its A_V x area over the texels it covers, and the texels' A_V x area sums to the census's to
// float32 rounding. The march reads it as a third layer of opacity in the clouds' own published layer (R3), each
// filter's depth the diffuse dust's conversion (A_V x the header's extinction_ratio / 1.0857, regimes.ts depthOf of
// 10^(-0.4 A_V r)). Nothing here is physics the model did not publish: a sum, a share by area, a unit change (D5).

/** Magnitudes per unit of optical depth, 2.5 / ln 10: a definition (what turns the diffuse dust's 10^(-0.4 A) into e^-tau). */
export const MAG_PER_DEPTH = 2.5 / Math.LN10;

/**
 * The raster's budget (A9: declared where it is computed): at most this many bytes of texture. One float32 channel per
 * texel (A_V, the filter's depth is a multiplication in the shader), so 16 MiB holds 4 194 304 texels.
 */
export const CLOUD_RASTER_BUDGET_BYTES = 16 * 1024 * 1024;
export const CLOUD_TEXEL_BYTES = 4;

/** The finest raster, texels per render cell on each axis, whose (nR k) x (nPhi k) float32 texels fit the budget. */
export function finestRaster(nR: number, nPhi: number, budget: number = CLOUD_RASTER_BUDGET_BYTES, bytes: number = CLOUD_TEXEL_BYTES): number {
  const cells = Math.max(1, nR) * Math.max(1, nPhi);
  return Math.max(1, Math.floor(Math.sqrt(budget / (cells * bytes))));
}

/**
 * The model's render grid on which the default is computed: 400 rings by 360 sectors (GridSpec's default, the grid
 * every /api/render answer has carried since S38). At 5 texels a cell a side the raster is 2000 x 1800 float32 texels,
 * 14.4 MB (13.7 MiB) - 6 would be 20.7 MB, over the budget. The "cloud raster" tuning value's default.
 */
export const RENDER_GRID = { R: 400, phi: 360 } as const;
export const CLOUD_RASTER = finestRaster(RENDER_GRID.R, RENDER_GRID.phi);

/** The census columns the raster reads (kpc, rad, pc, mag, kpc). */
export interface CloudColumns {
  cloud_radius: ArrayLike<number>;
  cloud_azimuth: ArrayLike<number>;
  cloud_size: ArrayLike<number>;
  cloud_dust_extinction_v: ArrayLike<number>;
  /** The cloud's published height above the plane, kpc (S64, the lead's ruling on R3: each cloud at its own height). */
  cloud_height: ArrayLike<number>;
  /** Its published face-on axis ratio, long over short (S70, F-4-3: /api/clouds' cloud_axis_ratio); absent, round. */
  cloud_axis_ratio?: ArrayLike<number>;
  /** Its long axis's angle from r-hat towards phi-hat, rad (S70: /api/clouds' cloud_angle). */
  cloud_angle?: ArrayLike<number>;
}

export interface CloudRaster {
  /** Face-on A_V per texel, mag: row-major with phi as the row (texel (i, j) at j * width + i), as the polar textures. */
  av: Float32Array;
  width: number;
  height: number;
  rLo: number;
  rHi: number;
  /** Sum over the census of A_V x the cloud's area, mag kpc^2: what the texels hold. */
  census: number;
  /** Sum over the texels of A_V x the texel's area, mag kpc^2, from the float32 values. */
  held: number;
  /** A_V x area of the clouds, or the parts of clouds, outside [rLo, rHi): drawn nowhere, mag kpc^2. */
  outside: number;
  /** How many clouds were split over several texels (the rest fell in one). */
  split: number;
  /**
   * Per texel, two numbers, kpc (S64, R3 as the lead ruled it): the A_V-weighted mean height of the clouds the texel
   * holds, and the half-thickness of the slab they are drawn as - the A_V-weighted rms of their heights about that
   * mean in quadrature with their A_V-weighted mean radius, floored at the smallest radius among them. A texel holding
   * one cloud is that cloud at its own height and extent; one holding several is one slab spanning them. 0, 0 where a
   * texel holds nothing. Row-major as `av`, two values a texel.
   */
  slab: Float32Array;
}

/**
 * The points a side each texel a split cloud touches is sampled at: 16 a texel. A sampling choice, not a display
 * choice (fixed; no tuning value moves it): at 4 x 4 a cloud's edge texels lie 0.03 % to 33 % off a 24 x 24
 * quadrature's share (S64 review, measured), and each cloud's total A_V x area is conserved whatever the sampling
 * (the weights are normalised over the cloud's texels).
 */
export const SPLIT_SAMPLES = 4;

/**
 * The half-maximum of a sech²(z / 2h) layer in units of h: sech²(x) = 1/2 at x = arcsech(1/sqrt 2) = ln(1 + sqrt 2), so
 * z = 2 ln(1 + sqrt 2) h = 1.7627 h. Geometry, not a choice. (S67, D230 R1.)
 */
export const SECH2_HWHM_PER_H = 2 * Math.log(1 + Math.SQRT2);

/**
 * A cloud's face-on ellipse as drawn (S67, D230 R2; the shape the model's since S70, Audit V F-4-3): /api/clouds
 * publishes each cloud's `cloud_axis_ratio` lambda+ and `cloud_angle` - the ellipse a round feature of the gas
 * fluctuation field becomes under the field's local shear at the cloud (the header's clouds.derived states the rule;
 * api/v6_clouds.py cloud_shape) - and the viewer raises the ratio to its own `exponent` in log, lambda+ ^ exponent:
 * 0 round, 1 the field's own anisotropy (the "cloud elongation" control, a display choice). The angle is the long
 * axis's from r-hat towards phi-hat, the model's.
 */
export function cloudEllipse(axisRatio: number, angle: number, exponent: number): { ratio: number; angle: number } {
  const ratio = exponent === 0 || axisRatio === 1 ? 1 : axisRatio ** exponent;
  return { ratio, angle };
}

/** What the raster reads beside the census (S67, D230): the clouds' vertical cap and the elongation's power. */
export interface RasterShape {
  /** Each cloud's vertical half-extent is at most this, kpc (R1: the clouds' layer's half-maximum). */
  verticalCap?: number;
  /** The elongation's exponent (R2's tuning control): 0 round, 1 the field's own anisotropy (the published shape). */
  elongation?: number;
}

/** One texel's area, kpc^2: the annulus sector between its radii over its azimuth span. */
export function texelArea(i: number, rLo: number, dR: number, dPhi: number): number {
  const r0 = rLo + i * dR;
  const r1 = r0 + dR;
  return 0.5 * (r1 * r1 - r0 * r0) * dPhi;
}

/**
 * The census rasterised into a polar texture of face-on A_V, `width` texels over [rLo, rHi) in R and `height` over
 * [0, 2 pi) in phi. A cloud whose diameter is under the smaller side of the texel at its centre falls whole in that
 * texel; a larger one is split by area: each texel its disc may touch takes the integral over the texel's own area of a
 * uniform sphere's chord (sqrt(1 - rho^2 / s^2), the column's profile; SPLIT_SAMPLES^2 points a texel), and the cloud's
 * A_V x area is shared in those weights - normalised to the cloud's own, so the split conserves it whatever the
 * sampling, and the share of texels past the raster's radii is counted as outside, never moved in. A
 * texel holds its A_V x area over its own area: the mean face-on A_V across it. Clouds with no column (0, or a missing
 * number) deposit nothing (rule B9).
 */
export function cloudRaster(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape = {}): CloudRaster {
  const cap = shape.verticalCap ?? Infinity;
  const elongation = shape.elongation ?? 0;
  const ratios = clouds.cloud_axis_ratio;
  const angles = clouds.cloud_angle;
  const shaped = elongation > 0 && Boolean(ratios && angles);
  const dR = (rHi - rLo) / width;
  const dPhi = (2 * Math.PI) / height;
  const sum = new Float64Array(width * height); // A_V x area per texel, mag kpc^2
  // The slab's sums, kept only for the texels a cloud reaches: each texel's weights times height, height squared and
  // radius, and its smallest radius (the weight is the A_V x area deposited there).
  const slot = new Int32Array(width * height).fill(-1);
  const wz: number[] = [];
  const wz2: number[] = [];
  const ws: number[] = [];
  const least: number[] = [];
  let z = 0;
  let s = 0;
  let sv = 0; // the cloud's vertical half-extent: its radius, capped at the clouds' layer (S67, D230 R1)
  const deposit = (t: number, part: number) => {
    sum[t] += part;
    let k = slot[t];
    if (k < 0) {
      k = slot[t] = wz.length;
      wz.push(0);
      wz2.push(0);
      ws.push(0);
      least.push(Infinity);
    }
    wz[k] += part * z;
    wz2[k] += part * z * z;
    ws[k] += part * sv;
    if (sv < least[k]) least[k] = sv;
  };
  let census = 0;
  let outside = 0;
  let split = 0;
  const texelOf = (x: number, y: number): number => {
    const r = Math.hypot(x, y);
    const i = Math.floor((r - rLo) / dR);
    if (!(i >= 0 && i < width)) return -1;
    let phi = Math.atan2(y, x);
    if (phi < 0) phi += 2 * Math.PI;
    const j = Math.min(height - 1, Math.floor(phi / dPhi));
    return j * width + i;
  };
  const n = clouds.cloud_radius.length;
  for (let c = 0; c < n; c += 1) {
    const av = Number(clouds.cloud_dust_extinction_v[c]);
    s = Number(clouds.cloud_size[c]) / 1000; // the cloud's radius, kpc
    sv = Math.min(s, cap);
    z = Number(clouds.cloud_height[c]); // its height, kpc
    const r = Number(clouds.cloud_radius[c]);
    const phi = Number(clouds.cloud_azimuth[c]);
    if (!(av > 0) || !(s > 0) || !Number.isFinite(r) || !Number.isFinite(phi) || !Number.isFinite(z)) continue;
    const total = av * Math.PI * s * s;
    census += total;
    const x = r * Math.cos(phi);
    const y = r * Math.sin(phi);
    const side = Math.min(dR, Math.max(r, 0.5 * dR) * dPhi);
    // Its face-on shape (S67, D230 R2): round, or an ellipse of the same area pi s² along the gas field's local shear -
    // the model's published ratio and angle (S70, F-4-3) at the elongation's power - semi-axes s sqrt(q) and s / sqrt(q);
    // e1 its long axis, e2 the short, in the raster's (x, y).
    const ell = shaped ? cloudEllipse(Number(ratios![c]), Number(angles![c]), elongation) : null;
    const q = ell ? ell.ratio : 1;
    const along = s * Math.sqrt(q);
    const across = s / Math.sqrt(q);
    const e1x = ell ? Math.cos(ell.angle) * Math.cos(phi) - Math.sin(ell.angle) * Math.sin(phi) : 1;
    const e1y = ell ? Math.cos(ell.angle) * Math.sin(phi) + Math.sin(ell.angle) * Math.cos(phi) : 0;
    if (2 * along < side) {
      const t = texelOf(x, y);
      if (t < 0) outside += total;
      else deposit(t, total);
      continue;
    }
    split += 1;
    // Every texel the cloud's disc may touch - those past the raster's radii too, whose share is drawn nowhere -
    // each weighted by the chord's integral over its own area (SPLIT_SAMPLES^2 points in it), so every texel is
    // sampled alike and none aliases; then the cloud's A_V x area shared in those weights.
    const i0 = Math.floor((Math.max(0, r - along) - rLo) / dR);
    const i1 = Math.floor((r + along - rLo) / dR);
    const half = along < r ? Math.asin(along / r) : Math.PI;
    let j0 = Math.floor((phi - half) / dPhi);
    let j1 = Math.floor((phi + half) / dPhi);
    if (j1 - j0 + 1 >= height) {
      j0 = 0;
      j1 = height - 1;
    }
    const at: number[] = [];
    const weight: number[] = [];
    let w = 0;
    const m = SPLIT_SAMPLES;
    for (let i = i0; i <= i1; i += 1) {
      for (let j = j0; j <= j1; j += 1) {
        let got = 0;
        for (let a = 0; a < m; a += 1) {
          const ra = rLo + (i + (a + 0.5) / m) * dR;
          if (!(ra > 0)) continue;
          for (let b = 0; b < m; b += 1) {
            const pb = (j + (b + 0.5) / m) * dPhi;
            const dx = ra * Math.cos(pb) - x;
            const dy = ra * Math.sin(pb) - y;
            // round: the S64 expression, to the bit; an ellipse: its own axes
            const rho2 = q === 1 ? (dx * dx + dy * dy) / (s * s) : ((dx * e1x + dy * e1y) / along) ** 2 + ((dy * e1x - dx * e1y) / across) ** 2;
            if (rho2 < 1) got += Math.sqrt(1 - rho2) * ra;
          }
        }
        if (!(got > 0)) continue;
        at.push(i >= 0 && i < width ? (((j % height) + height) % height) * width + i : -1);
        weight.push(got);
        w += got;
      }
    }
    if (!(w > 0)) {
      const t = texelOf(x, y);
      if (t < 0) outside += total;
      else deposit(t, total);
      continue;
    }
    for (let q = 0; q < at.length; q += 1) {
      const part = (total * weight[q]) / w;
      if (at[q] < 0) outside += part;
      else deposit(at[q], part);
    }
  }
  const av = new Float32Array(width * height);
  const slab = new Float32Array(width * height * 2);
  let held = 0;
  for (let i = 0; i < width; i += 1) {
    const area = texelArea(i, rLo, dR, dPhi);
    for (let j = 0; j < height; j += 1) {
      const t = j * width + i;
      if (sum[t] === 0) continue;
      av[t] = sum[t] / area;
      held += av[t] * area;
      const k = slot[t];
      const mean = wz[k] / sum[t];
      const spread = Math.max(0, wz2[k] / sum[t] - mean * mean);
      const radius = ws[k] / sum[t];
      slab[2 * t] = mean;
      slab[2 * t + 1] = Math.max(Math.sqrt(spread + radius * radius), least[k]);
    }
  }
  return { av, width, height, rLo, rHi, census, held, outside, split, slab };
}

// --- the raster kept across remounts (S76, BUILD_IV W5, D240 F1) ------------------------------------------------
// The raster is the census's alone, at a shape: the same census at the same shape is the same raster, bit for bit
// (cloudRaster is a pure function). Building it takes 1.4-2.7 s of the main thread on the Milky Way (S76's probe), and
// the field remakes it whenever its component remounts - the star-first mode's own march, a template switch and back
// (the census answered again, the same bytes in a new object). So the last few rasters are kept here, keyed on the
// census's content (every column the raster reads, its bits) and the shape (the radii, the texels, the cap, the
// elongation): a remount with the same answer takes the kept one.

/** How many rasters are kept: the two templates, each with and without the layer. Each is at most the 16 MiB budget plus its slab. */
export const KEPT_RASTERS = 4;

const kept = new Map<string, CloudRaster>();

/** Two 32-bit hashes (FNV-1a and a multiplicative mix) over each value's float64 bits, with the column's length. */
function columnKey(values: ArrayLike<number> | undefined, scratch: DataView): string {
  if (!values) return "-";
  let a = 0x811c9dc5;
  let b = 0x9e3779b9 ^ values.length;
  for (let k = 0; k < values.length; k += 1) {
    scratch.setFloat64(0, Number(values[k]));
    for (let w = 0; w < 2; w += 1) {
      const word = scratch.getUint32(4 * w);
      a = Math.imul(a ^ word, 0x01000193);
      b = Math.imul(b ^ word, 0x85ebca6b);
      b ^= b >>> 13;
    }
  }
  return `${values.length}:${(a >>> 0).toString(16)}:${(b >>> 0).toString(16)}`;
}

/** The raster's cache key: the census's content and the shape it is drawn at. */
export function rasterKey(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape = {}): string {
  const scratch = new DataView(new ArrayBuffer(8));
  const columns = [
    clouds.cloud_radius, clouds.cloud_azimuth, clouds.cloud_size, clouds.cloud_dust_extinction_v, clouds.cloud_height,
    clouds.cloud_axis_ratio, clouds.cloud_angle,
  ].map((c) => columnKey(c, scratch));
  return [...columns, rLo, rHi, width, height, shape.verticalCap ?? Infinity, shape.elongation ?? 0].join("|");
}

/** cloudRaster, or the raster kept from an earlier call with the same census content and shape (the same bits). */
export function keptCloudRaster(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape = {}): CloudRaster {
  const key = rasterKey(clouds, rLo, rHi, width, height, shape);
  const hit = kept.get(key);
  if (hit) {
    kept.delete(key); // most recent last
    kept.set(key, hit);
    return hit;
  }
  const built = cloudRaster(clouds, rLo, rHi, width, height, shape);
  kept.set(key, built);
  while (kept.size > KEPT_RASTERS) kept.delete(kept.keys().next().value as string);
  return built;
}

/**
 * Each display channel's optical depth per magnitude of A_V: the header's `extinction_ratio` (A_lambda / A_V at each
 * filter's reference wavelength, the grain model's) over 1.0857 - the diffuse dust's own conversion, so the clouds'
 * dust dims each filter exactly as the ring's does. A missing ratio is no depth in that channel (rule B9).
 */
export function cloudDepthScale(extinctionRatio: readonly (number | null)[] | null | undefined): [number, number, number] {
  const out: [number, number, number] = [0, 0, 0];
  for (let k = 0; k < 3; k += 1) {
    const r = Number(extinctionRatio?.[k]);
    out[k] = Number.isFinite(r) && r > 0 ? r / MAG_PER_DEPTH : 0;
  }
  return out;
}

/** The share column of the render's ring texture: each ring's `dust_diffuse_share`, 1 where none is published (an even dust, all diffuse). */
export function shareAt(share: ArrayLike<number> | null | undefined, i: number): number {
  if (!share) return 1;
  const v = Number(share[i]);
  return Number.isFinite(v) && v >= 0 ? v : 1;
}
