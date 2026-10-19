// A point as the instrument's image of a point at its physical size (S67, BUILD_III V8; D227 R1, R3; T9). No three.js
// here: the pure parts, tested, which FluxPoints' shader repeats line for line (psfCorner, psfRect).
//
// Where a template carries an instrument with a distance and the view's filter set is that instrument's own, a point is
// the telescope's PSF at each channel's pivot wavelength, its angle turned into pc by the template's distance, convolved
// with the instrument's pixel as a box (pixel_scale x distance), drawn through S64's extent box path (plummer.ts): a box
// of whole screen pixels round the point, each pixel taking the profile's light over its own area over the light over
// the whole box - so the box sums to the point's light at every scale, sub-pixel included. Two PSFs, one switch (R3):
//
// - **off, the obscured Airy (R1)**: I(v) = [2 J1(v)/v - eps^2 2 J1(eps v)/(eps v)]^2 / (1 - eps^2)^2, v = pi D theta /
//   lambda, eps the linear obscuration - the image of an annular aperture, exact.
// - **on, the full pupil's image (R3)**: |FFT(pupil)|^2 of the annulus with the spider's vanes and the mirror's three
//   pads, computed once at load (one transform: in units of lambda / D the image is the same at every wavelength).
//
// Either is tabulated on one grid of TABLE_CELLS^2 cells in pc about the point (the cell the bluest channel's lambda/D
// over CELLS_PER_LAMBDA), each cell the PSF's mean over the cell convolved exactly with the pixel box, the table
// renormalised to sum to 1 (the light past its edge put back: a truncation, stated as `captured`), and held as its
// corner integral C(i, j) - the table's light between the centre and node (i, j), signed (plummer.ts plummerCorner's
// form) - so a rectangle's light is four corners, and bilinear interpolation of C between nodes is exact for the
// table's cell-constant density.

/** Radians per arcsecond. */
export const ARCSEC = Math.PI / (180 * 3600);
/** pc per Mpc. */
export const PC_PER_MPC = 1e6;

/** The table's cells on a side (even: the point sits on the centre node). A sampling bound, fixed, not a display choice. */
export const TABLE_CELLS = 768;
/** Cells per the bluest channel's lambda / D: the table's grain. A sampling bound, fixed, not a display choice. */
export const CELLS_PER_LAMBDA = 8;
/** Sub-samples per cell on a side for the cell's mean of the PSF. A sampling bound, measured in hstPsf.test.ts. */
export const CELL_SUBSAMPLES = 4;
/** The pupil's FFT: points on a side and samples across the aperture's diameter (the image's grain, lambda/D / 16; its field +-64 lambda/D). */
export const FFT_SIZE = 2048;
export const PUPIL_SAMPLES = 128;
/** Sub-samples per pupil pixel on a side for its coverage (the vanes are 1.4 pupil pixels wide). */
export const PUPIL_SUBSAMPLES = 4;
/**
 * The vanes' angle to the frame's axes, degrees: a display choice [inferred]. TinyTim's 135 degree image-axis rotation
 * is a detector convention not read for the frame; the vanes are drawn at 45 degrees to the picture's axes (D227 R3).
 */
export const VANE_ANGLE_DEG = 45;

/** The telescope and the detector as a template states them (templates.py Instrument; /api/templates). */
export interface Optics {
  distanceMpc: number;
  pixelArcsec: number;
  apertureM: number;
  obscuration: number;
  /** Full width of each vane, pupil radii. */
  spiderWidth: number;
  vanes: number;
  /** Each pad's (V3, V2) centre and radius, pupil radii. */
  pads: readonly (readonly [number, number, number])[];
}

/** A template's instrument as the viewer receives it (workflow/templates.ts), or null where any number is not read. */
export interface InstrumentFields {
  distance_mpc: number | null;
  pixel_scale_arcsec: number | null;
  aperture_m?: number | null;
  obscuration?: number | null;
  spider_width?: number | null;
  spider_vanes?: number | null;
  pads?: readonly (readonly number[])[] | null;
}

/** The optics R1 needs, all read, or null (R2: an instrument without a distance or a pixel scale draws today's sprite). */
export function opticsOf(instrument: InstrumentFields | null | undefined): Optics | null {
  if (!instrument) return null;
  const { distance_mpc, pixel_scale_arcsec, aperture_m, obscuration, spider_width, spider_vanes, pads } = instrument;
  const nums = [distance_mpc, pixel_scale_arcsec, aperture_m, obscuration];
  if (!nums.every((v) => typeof v === "number" && Number.isFinite(v) && v >= 0) || !(distance_mpc! > 0 && aperture_m! > 0)) return null;
  return {
    distanceMpc: distance_mpc!,
    pixelArcsec: pixel_scale_arcsec!,
    apertureM: aperture_m!,
    obscuration: obscuration!,
    spiderWidth: typeof spider_width === "number" ? spider_width : 0,
    vanes: typeof spider_vanes === "number" ? spider_vanes : 0,
    pads: (pads ?? []).filter((p) => p.length === 3).map((p) => [p[0], p[1], p[2]] as const),
  };
}

/** The instrument's pixel at the galaxy, pc: pixel_scale x distance (0.04" x 17.7 Mpc = 3.43 pc). */
export function pixelPc(o: Optics): number {
  return o.pixelArcsec * ARCSEC * o.distanceMpc * PC_PER_MPC;
}

/** lambda / D at the galaxy, pc, for a pivot in Angstrom. */
export function lambdaOverDPc(o: Optics, pivotAngstrom: number): number {
  return ((pivotAngstrom * 1e-10) / o.apertureM) * o.distanceMpc * PC_PER_MPC;
}

/**
 * J1 by Numerical Recipes' rational approximations (bessj1: |x| < 8 a ratio of polynomials, beyond the asymptotic form
 * with its two series), absolute error under 1e-8 - here because the table reaches v ~ 200, past the trapezoid's
 * range in psf.ts besselJ1 (held against it in hstPsf.test.ts).
 */
export function j1(x: number): number {
  const ax = Math.abs(x);
  if (ax < 8) {
    const y = x * x;
    const a = x * (72362614232.0 + y * (-7895059235.0 + y * (242396853.1 + y * (-2972611.439 + y * (15704.4826 + y * -30.16036606)))));
    const b = 144725228442.0 + y * (2300535178.0 + y * (18583304.74 + y * (99447.43394 + y * (376.9991397 + y))));
    return a / b;
  }
  const z = 8 / ax;
  const y = z * z;
  const xx = ax - 2.356194491;
  const p = 1 + y * (0.183105e-2 + y * (-0.3516396496e-4 + y * (0.2457520174e-5 + y * -0.240337019e-6)));
  const q = 0.04687499995 + y * (-0.2002690873e-3 + y * (0.8449199096e-5 + y * (-0.88228987e-6 + y * 0.105787412e-6)));
  const r = Math.sqrt(0.636619772 / ax) * (Math.cos(xx) * p - z * Math.sin(xx) * q);
  return x < 0 ? -r : r;
}

/** The obscured Airy pattern, 1 at the centre (D227 R1): [2 J1(v)/v - eps^2 2 J1(eps v)/(eps v)]^2 / (1 - eps^2)^2. */
export function obscuredAiry(v: number, eps: number): number {
  const jinc = (x: number) => (Math.abs(x) < 1e-8 ? 1 : (2 * j1(x)) / x);
  const a = (jinc(v) - eps * eps * jinc(eps * v)) / (1 - eps * eps);
  return a * a;
}

/**
 * The obscured Airy's integral over the plane in v's units: 4 pi / (1 - eps^2) (Parseval: the amplitude is the
 * annulus's transform normalised to 1 at the centre, the unobscured 4 pi over the area fraction 1 - eps^2).
 */
export function obscuredAiryTotal(eps: number): number {
  return (4 * Math.PI) / (1 - eps * eps);
}

/** A complex FFT in place, radix 2, of length re.length (a power of two); `stride`/`offset` read a row or a column. */
function fft1(re: Float64Array, im: Float64Array, n: number, offset: number, stride: number, wr: Float64Array, wi: Float64Array): void {
  for (let i = 1, j = 0; i < n; i += 1) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      const a = offset + i * stride;
      const b = offset + j * stride;
      let t = re[a]; re[a] = re[b]; re[b] = t;
      t = im[a]; im[a] = im[b]; im[b] = t;
    }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const step = n / len;
    const half = len >> 1;
    for (let i = 0; i < n; i += len) {
      for (let k = 0; k < half; k += 1) {
        const cr = wr[k * step];
        const ci = wi[k * step];
        const a = offset + (i + k) * stride;
        const b = offset + (i + k + half) * stride;
        const xr = re[b] * cr - im[b] * ci;
        const xi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - xr;
        im[b] = im[a] - xi;
        re[a] += xr;
        im[a] += xi;
      }
    }
  }
}

/** The 2-D FFT of an n x n complex grid, row-major, in place. */
export function fft2(re: Float64Array, im: Float64Array, n: number): void {
  const wr = new Float64Array(n / 2);
  const wi = new Float64Array(n / 2);
  for (let k = 0; k < n / 2; k += 1) {
    wr[k] = Math.cos((-2 * Math.PI * k) / n);
    wi[k] = Math.sin((-2 * Math.PI * k) / n);
  }
  for (let r = 0; r < n; r += 1) fft1(re, im, n, r * n, 1, wr, wi);
  for (let c = 0; c < n; c += 1) fft1(re, im, n, c, n, wr, wi);
}

/** Whether a pupil point (pupil radii, the frame's axes) is open: in the annulus, off the vanes and the pads. */
export function pupilOpen(x: number, y: number, o: Pick<Optics, "obscuration" | "spiderWidth" | "vanes" | "pads">, vanesOn = true): boolean {
  const r2 = x * x + y * y;
  if (r2 > 1 || r2 < o.obscuration * o.obscuration) return false;
  if (!vanesOn) return true;
  // The pupil's own axes are the vanes' (V3, V2), turned by VANE_ANGLE_DEG to the frame's.
  const t = (-VANE_ANGLE_DEG * Math.PI) / 180;
  const u = x * Math.cos(t) - y * Math.sin(t);
  const w = x * Math.sin(t) + y * Math.cos(t);
  const halfWidth = o.spiderWidth / 2;
  for (let k = 0; k < o.vanes; k += 1) {
    // Vane k runs from the centre outward along angle k * 2 pi / vanes in the pupil's axes.
    const a = (2 * Math.PI * k) / o.vanes;
    const along = u * Math.cos(a) + w * Math.sin(a);
    const across = -u * Math.sin(a) + w * Math.cos(a);
    if (along > 0 && Math.abs(across) < halfWidth) return false;
  }
  for (const [pv3, pv2, pr] of o.pads) {
    if ((u - pv3) ** 2 + (w - pv2) ** 2 < pr * pr) return false;
  }
  return true;
}

/**
 * The pupil's image, |FFT|^2, fftshifted, FFT_SIZE^2 samples spaced PUPIL_SAMPLES / FFT_SIZE lambda/D (1/16), summing to 1
 * over the grid (the whole image's light, its far wings aliased into the grid by the transform's period, 128 lambda/D).
 * `vanesOn` false is the annulus alone: the FFT's own error, measured against the obscured Airy (hstPsf.test.ts).
 */
export function pupilImage(o: Pick<Optics, "obscuration" | "spiderWidth" | "vanes" | "pads">, vanesOn = true, n = FFT_SIZE, m = PUPIL_SAMPLES): Float64Array {
  const re = new Float64Array(n * n);
  const im = new Float64Array(n * n);
  const s = PUPIL_SUBSAMPLES;
  const dx = 2 / m; // pupil radii per pupil pixel
  const lo = -m / 2;
  for (let j = 0; j < m; j += 1) {
    for (let i = 0; i < m; i += 1) {
      let open = 0;
      for (let b = 0; b < s; b += 1) {
        for (let a = 0; a < s; a += 1) {
          if (pupilOpen((lo + i + (a + 0.5) / s) * dx, (lo + j + (b + 0.5) / s) * dx, o, vanesOn)) open += 1;
        }
      }
      if (open === 0) continue;
      // Wrapped so the pupil's centre is index 0: the image comes out real-centred, no phase ramp.
      const ii = (lo + i + n) % n;
      const jj = (lo + j + n) % n;
      re[jj * n + ii] = open / (s * s);
    }
  }
  // The pupil's centre sits between pixels (m even): its index-0 pixel is the one just above-right of the centre, so
  // the image carries a phase tilt of half a pixel each way, which |.|^2 drops.
  fft2(re, im, n);
  // A pupil pixel's coverage is the pupil convolved with the pixel's box, so its image is the pupil's times the box's
  // transform squared, sinc^2(pi f) on each axis (f in cycles per pupil pixel, |f| <= 1/2): divided out here, so the
  // wings are not dimmed by the pupil's sampling (by 2 % at 10 lambda/D and 13 % at 26 before it).
  const sinc = (f: number) => (f === 0 ? 1 : Math.sin(Math.PI * f) / (Math.PI * f));
  const out = new Float64Array(n * n);
  let sum = 0;
  for (let j = 0; j < n; j += 1) {
    const fy = (j < n / 2 ? j : j - n) / n;
    for (let i = 0; i < n; i += 1) {
      const fx = (i < n / 2 ? i : i - n) / n;
      const p = j * n + i;
      const v = (re[p] * re[p] + im[p] * im[p]) / (sinc(fx) * sinc(fy)) ** 2;
      out[((j + n / 2) % n) * n + ((i + n / 2) % n)] = v;
      sum += v;
    }
  }
  for (let p = 0; p < out.length; p += 1) out[p] /= sum;
  return out;
}

/** The PSF as a density in lambda/D units at (x, y) lambda/D: a function the table is built from. */
type Density = (x: number, y: number) => number;

/** The obscured Airy as a density in lambda/D units (v = pi x), integrating to 1 over the plane. */
export function airyDensity(eps: number): Density {
  // A radial table in v, linear between its points (step 0.005: 600 a period of the rings), so the table's millions
  // of reads are cheap; the step's error is under 1e-6 of the core (hstPsf.test.ts).
  const dv = 0.005;
  const vMax = 400;
  const n = Math.ceil(vMax / dv) + 2;
  const radial = new Float64Array(n);
  for (let k = 0; k < n; k += 1) radial[k] = obscuredAiry(k * dv, eps);
  const norm = (Math.PI * Math.PI) / obscuredAiryTotal(eps); // d2v = pi^2 d2x
  return (x, y) => {
    const v = (Math.PI * Math.hypot(x, y)) / dv;
    const k = Math.floor(v);
    if (k >= n - 1) return 0;
    const f = v - k;
    return (radial[k] * (1 - f) + radial[k + 1] * f) * norm;
  };
}

/** The pupil's image as a density in lambda/D units, bilinear between its samples; zero outside its grid. */
export function imageDensity(image: Float64Array, n = FFT_SIZE, m = PUPIL_SAMPLES): Density {
  const spacing = m / n; // lambda/D per sample
  const norm = 1 / (spacing * spacing);
  return (x, y) => {
    const gx = x / spacing + n / 2;
    const gy = y / spacing + n / 2;
    const i = Math.floor(gx);
    const j = Math.floor(gy);
    if (i < 0 || j < 0 || i >= n - 1 || j >= n - 1) return 0;
    const fx = gx - i;
    const fy = gy - j;
    const p = j * n + i;
    return ((image[p] * (1 - fx) + image[p + 1] * fx) * (1 - fy) + (image[p + n] * (1 - fx) + image[p + n + 1] * fx) * fy) * norm;
  };
}

/**
 * A row of cell-constant values (cells of width `cell`) convolved with a box of width `box` and averaged over each cell:
 * exact for the cell-constant input, through its running integral F (linear between nodes) and that one's integral G
 * (quadratic). Zero outside the row.
 */
export function boxRow(values: Float64Array, cell: number, box: number): Float64Array {
  const n = values.length;
  const F = new Float64Array(n + 1);
  const G = new Float64Array(n + 1);
  for (let i = 0; i < n; i += 1) {
    F[i + 1] = F[i] + values[i] * cell;
    G[i + 1] = G[i] + F[i] * cell + (values[i] * cell * cell) / 2;
  }
  const total = F[n];
  const g = (x: number) => {
    // G at x, the row starting at x = 0; flat F beyond either end.
    if (x <= 0) return 0;
    if (x >= n * cell) return G[n] + total * (x - n * cell);
    const i = Math.floor(x / cell);
    const t = x - i * cell;
    return G[i] + F[i] * t + (values[i] * t * t) / 2;
  };
  const out = new Float64Array(n);
  if (box <= 0) return Float64Array.from(values);
  const h = box / 2;
  for (let i = 0; i < n; i += 1) {
    const x0 = i * cell;
    const x1 = x0 + cell;
    out[i] = (g(x1 + h) - g(x1 - h) - g(x0 + h) + g(x0 - h)) / (box * cell);
  }
  return out;
}

/** The table a point is drawn from: its corner integral per channel and its scale. */
export interface PsfTable {
  /** Cells on a side; the corners are (cells + 1)^2. */
  cells: number;
  /** pc per cell. */
  cellPc: number;
  /** C(i, j) per channel, RGBA float, row-major over (cells + 1)^2 nodes (alpha 0): what the shader reads. */
  corners: Float32Array;
  /** Each channel's share of the PSF's light the table holds before it is renormalised (the light past its edge put back). */
  captured: [number, number, number];
}

export interface TableOptions {
  /** Pivot wavelengths, Angstrom, red green blue (the set's sources). */
  pivots: readonly number[];
  /** The PSF in lambda/D units; the obscured Airy of the optics when absent. */
  density?: Density;
  cells?: number;
  cellsPerLambda?: number;
  subsamples?: number;
}

/** Builds the table (D227 R1, R3): each channel's PSF in pc, its cell means, the pixel box, renormalised, its corners. */
export function psfTable(o: Optics, opts: TableOptions): PsfTable {
  const cells = opts.cells ?? TABLE_CELLS;
  const per = opts.cellsPerLambda ?? CELLS_PER_LAMBDA;
  const sub = opts.subsamples ?? CELL_SUBSAMPLES;
  const density = opts.density ?? airyDensity(o.obscuration);
  const pivots = opts.pivots.slice(0, 3);
  const cellPc = lambdaOverDPc(o, Math.min(...pivots)) / per;
  const box = pixelPc(o);
  const nodes = cells + 1;
  const corners = new Float32Array(nodes * nodes * 4);
  const captured: [number, number, number] = [0, 0, 0];
  const half = cells / 2;
  for (let k = 0; k < pivots.length; k += 1) {
    const ld = lambdaOverDPc(o, pivots[k]); // pc per lambda/D
    // The cell means of the density in pc (density_pc = density_ld / ld^2).
    const grid = new Float64Array(cells * cells);
    for (let j = 0; j < cells; j += 1) {
      for (let i = 0; i < cells; i += 1) {
        let s = 0;
        for (let b = 0; b < sub; b += 1) {
          for (let a = 0; a < sub; a += 1) {
            const x = (i - half + (a + 0.5) / sub) * cellPc;
            const y = (j - half + (b + 0.5) / sub) * cellPc;
            s += density(x / ld, y / ld);
          }
        }
        grid[j * cells + i] = s / (sub * sub) / (ld * ld);
      }
    }
    // The instrument's pixel, a box of `box` pc, separably: along each row, then along each column.
    const row = new Float64Array(cells);
    for (let j = 0; j < cells; j += 1) {
      for (let i = 0; i < cells; i += 1) row[i] = grid[j * cells + i];
      const c = boxRow(row, cellPc, box);
      for (let i = 0; i < cells; i += 1) grid[j * cells + i] = c[i];
    }
    for (let i = 0; i < cells; i += 1) {
      for (let j = 0; j < cells; j += 1) row[j] = grid[j * cells + i];
      const c = boxRow(row, cellPc, box);
      for (let j = 0; j < cells; j += 1) grid[j * cells + i] = c[j];
    }
    // The summed-area table over the nodes, then the corner integral about the centre node.
    const sat = new Float64Array(nodes * nodes);
    for (let j = 0; j < cells; j += 1) {
      let run = 0;
      for (let i = 0; i < cells; i += 1) {
        run += grid[j * cells + i] * cellPc * cellPc;
        sat[(j + 1) * nodes + (i + 1)] = sat[j * nodes + (i + 1)] + run;
      }
    }
    const total = sat[cells * nodes + cells];
    captured[k] = total;
    const centre = sat[half * nodes + half];
    for (let j = 0; j < nodes; j += 1) {
      for (let i = 0; i < nodes; i += 1) {
        const c = sat[j * nodes + i] - sat[j * nodes + half] - sat[half * nodes + i] + centre;
        corners[(j * nodes + i) * 4 + k] = c / total;
      }
    }
  }
  return { cells, cellPc, corners, captured };
}

/**
 * The table's corner integral at u (cells from the centre, each axis), per channel: clamped to the table (past its
 * edge the light is all counted), bilinear between nodes. FluxPoints' psfCorner, line for line.
 */
export function psfCorner(t: Pick<PsfTable, "cells" | "corners">, ux: number, uy: number): [number, number, number] {
  const n = t.cells;
  const gx = Math.min(n, Math.max(0, ux + 0.5 * n));
  const gy = Math.min(n, Math.max(0, uy + 0.5 * n));
  const ix = Math.min(Math.floor(gx), n - 1);
  const iy = Math.min(Math.floor(gy), n - 1);
  const fx = gx - ix;
  const fy = gy - iy;
  const out: [number, number, number] = [0, 0, 0];
  const nodes = n + 1;
  for (let k = 0; k < 3; k += 1) {
    const c00 = t.corners[(iy * nodes + ix) * 4 + k];
    const c10 = t.corners[(iy * nodes + ix + 1) * 4 + k];
    const c01 = t.corners[((iy + 1) * nodes + ix) * 4 + k];
    const c11 = t.corners[((iy + 1) * nodes + ix + 1) * 4 + k];
    out[k] = (c00 * (1 - fx) + c10 * fx) * (1 - fy) + (c01 * (1 - fx) + c11 * fx) * fy;
  }
  return out;
}

/** The table's light over [lo, hi] (cells from the centre), per channel: four corners. FluxPoints' psfRect. */
export function psfRect(t: Pick<PsfTable, "cells" | "corners">, lo: [number, number], hi: [number, number]): [number, number, number] {
  const a = psfCorner(t, hi[0], hi[1]);
  const b = psfCorner(t, lo[0], hi[1]);
  const c = psfCorner(t, hi[0], lo[1]);
  const d = psfCorner(t, lo[0], lo[1]);
  return [a[0] - b[0] - c[0] + d[0], a[1] - b[1] - c[1] + d[1], a[2] - b[2] - c[2] + d[2]];
}

/**
 * The box's half-side, screen pixels, at `sidePc` pc a pixel: the table's half-width, at most PROFILE_MAX_HALF (plummer.ts
 * profileBox clamps). The clamp, disclosed (the fix pass, F4; not changed): at NGC 4414's zoom stand, 0.488 pc a pixel,
 * the table's half-width is 314 px (768 cells of 0.399 pc), drawn in a box of 60 px each side; psfWeights divides by the
 * box's share, so the light outside it (the box holds 0.958 of the red Airy, 0.940 of the red spikes) is returned inside
 * it - the core drawn 4.4 % (Airy) to 6.4 % (spikes) brighter in red, less in the bluer channels (0.971 / 0.976 of the
 * Airy, 0.952 / 0.958 of the spikes) - and the spikes end at the box's square edge. The point's light is kept; its shape
 * past 60 px is not drawn. At the template's camera (29.3 pc a pixel) the half-width is 6 px and nothing is clamped.
 */
export function psfHalf(t: Pick<PsfTable, "cells" | "cellPc">, sidePc: number): number {
  return (0.5 * t.cells * t.cellPc) / sidePc;
}

/**
 * Each screen pixel's weight per channel in the point's box, row-major (side x side), each channel summing to 1: the
 * table's light over the pixel over its light over the box (plummer.ts profileWeights' form). The shader's sum.
 * `box` is plummer.ts profileBox(cx, cy, psfHalf(t, sidePc)).
 */
export function psfWeights(
  t: Pick<PsfTable, "cells" | "corners" | "cellPc">,
  cx: number,
  cy: number,
  sidePc: number,
  box: { x0: number; y0: number; side: number },
): { weights: Float64Array[]; norm: [number, number, number]; share: [number, number, number] } {
  const scale = sidePc / t.cellPc; // cells per screen pixel
  const share = psfRect(t, [(box.x0 - cx) * scale, (box.y0 - cy) * scale], [(box.x0 + box.side - cx) * scale, (box.y0 + box.side - cy) * scale]);
  const weights = [0, 1, 2].map(() => new Float64Array(box.side * box.side));
  for (let j = 0; j < box.side; j += 1) {
    for (let i = 0; i < box.side; i += 1) {
      const x = box.x0 + i - cx;
      const y = box.y0 + j - cy;
      const w = psfRect(t, [x * scale, y * scale], [(x + 1) * scale, (y + 1) * scale]);
      for (let k = 0; k < 3; k += 1) weights[k][j * box.side + i] = w[k] / share[k];
    }
  }
  return { weights, norm: [1 / share[0], 1 / share[1], 1 / share[2]], share };
}
