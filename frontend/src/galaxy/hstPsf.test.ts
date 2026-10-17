import { describe, expect, it } from "vitest";

import { FILTER_SETS } from "./filters";
import {
  CELL_SUBSAMPLES,
  type Optics,
  boxRow,
  imageDensity,
  j1,
  lambdaOverDPc,
  obscuredAiry,
  obscuredAiryTotal,
  opticsOf,
  pixelPc,
  psfHalf,
  psfRect,
  psfTable,
  psfWeights,
  pupilImage,
  pupilOpen,
} from "./hstPsf";
import { PROFILE_MAX_HALF, profileBox } from "./plummer";
import { airy, besselJ1 } from "./psf";

// NGC 4414's instrument as templates.py states it (S67, D227 R1): WFC3/UVIS at 17.7 Mpc.
const NGC: Optics = {
  distanceMpc: 17.7,
  pixelArcsec: 0.04,
  apertureM: 2.4,
  obscuration: 0.33,
  spiderWidth: 0.022,
  vanes: 4,
  pads: [
    [0.8921, 0, 0.065],
    [-0.4615, 0.7555, 0.065],
    [-0.4564, -0.7606, 0.065],
  ],
};
const PIVOTS = FILTER_SETS.wfc3.sources!.map((s) => s.pivot);
// The two stands the gate is read at: the template's camera (1024 px over 30 kpc at 343 kpc: 29.3 pc a pixel) and the
// zoom capture's (1024 px over 0.5 kpc: 0.49 pc), the point off a pixel's centre.
const CAMERA_PC = (2 * 15000) / 1024;
const ZOOM_PC = 500 / 1024;
const CENTRE: [number, number] = [512.3, 511.8];

const analytic = psfTable(NGC, { pivots: PIVOTS });
const spiked = psfTable(NGC, { pivots: PIVOTS, density: imageDensity(pupilImage(NGC)) });

const boxOf = (sidePc: number) => profileBox(CENTRE[0], CENTRE[1], psfHalf(analytic, sidePc));
const sums = (w: Float64Array[]) => w.map((a) => a.reduce((s, v) => s + v, 0));

describe("the instrument's image of a point (S67, D227 R1)", () => {
  it("reads the optics only where every number is read (R2: no distance, no pixel scale, the display sprite)", () => {
    expect(opticsOf({ distance_mpc: null, pixel_scale_arcsec: null })).toBeNull();
    expect(opticsOf({ distance_mpc: 17.7, pixel_scale_arcsec: null, aperture_m: 2.4, obscuration: 0.33 })).toBeNull();
    const o = opticsOf({ distance_mpc: 17.7, pixel_scale_arcsec: 0.04, aperture_m: 2.4, obscuration: 0.33, spider_width: 0.022, spider_vanes: 4, pads: NGC.pads });
    expect(o).toEqual(NGC);
  });

  it("scales by the distance: the pixel 3.43 pc, lambda/D 5.92 pc in F814W and 3.19 in F438W", () => {
    expect(pixelPc(NGC)).toBeCloseTo(3.4325, 4);
    expect(PIVOTS).toEqual([8029.3, 5307.9, 4325.15]);
    expect(lambdaOverDPc(NGC, PIVOTS[0])).toBeCloseTo(5.9216, 4);
    expect(lambdaOverDPc(NGC, PIVOTS[2])).toBeCloseTo(3.1898, 4);
    expect(analytic.cellPc).toBeCloseTo(3.1898 / 8, 4);
  });

  it("computes J1 to 1e-8 and the obscured Airy as the formula: the unobscured case is psf.ts's, its total 4 pi / (1 - eps^2)", () => {
    let err = 0;
    for (let x = 0; x < 60; x += 0.37) err = Math.max(err, Math.abs(j1(x) - besselJ1(x, 256)));
    expect(err).toBeLessThan(1e-8);
    for (const v of [0.3, 2.1, 5, 11]) expect(obscuredAiry(v, 0)).toBeCloseTo(airy(v), 9);
    expect(obscuredAiry(0, 0.33)).toBe(1);
    // The radial integral, 2 pi v I(v) dv, to v = 2000 by the midpoint rule, plus the tail's asymptotic share.
    let total = 0;
    const dv = 0.01;
    for (let v = dv / 2; v < 2000; v += dv) total += 2 * Math.PI * v * obscuredAiry(v, 0.33) * dv;
    expect(total / obscuredAiryTotal(0.33)).toBeGreaterThan(0.999);
    expect(total / obscuredAiryTotal(0.33)).toBeLessThan(1);
  });

  it("holds the light: a point's screen pixels sum to its light within 1e-6, at the template's camera and at the zoom stand", () => {
    for (const [side, table] of [
      [CAMERA_PC, analytic],
      [ZOOM_PC, analytic],
      [CAMERA_PC, spiked],
      [ZOOM_PC, spiked],
    ] as const) {
      for (const [cx, cy] of [CENTRE, [100.0, 100.0], [7.93, 250.5]] as const) {
        const box = profileBox(cx, cy, psfHalf(table, side));
        const w = psfWeights(table, cx, cy, side, box);
        for (const s of sums(w.weights)) expect(Math.abs(s - 1)).toBeLessThan(1e-6);
      }
    }
  });

  it("is sub-pixel at the template's camera and about 13 px across in F814W at the zoom stand", () => {
    const fwhm = (side: number, k: number) => {
      // The profile through the centre at a twentieth of a pixel.
      const s = side / analytic.cellPc;
      const values: number[] = [];
      for (let x = -400; x <= 400; x += 1) {
        const at = x * 0.05;
        values.push(psfRect(analytic, [(at - 0.025) * s, -0.025 * s], [(at + 0.025) * s, 0.025 * s])[k]);
      }
      const peak = Math.max(...values);
      return values.filter((v) => v >= peak / 2).length * 0.05;
    };
    expect(fwhm(CAMERA_PC, 0)).toBeLessThan(0.3);
    expect(fwhm(ZOOM_PC, 0)).toBeCloseTo(13.05, 1);
    expect(fwhm(ZOOM_PC, 2)).toBeCloseTo(8.15, 1);
    // The box: the table's half-width, clamped by S64's bound at the zoom stand.
    expect(boxOf(CAMERA_PC).side).toBe(13);
    expect(boxOf(ZOOM_PC).side).toBe(2 * PROFILE_MAX_HALF + 1);
  });

  it("states what is cut: the light past the table, and past the box at the zoom stand (renormalised, conserving)", () => {
    // The table's own share of the obscured Airy (the convolved pixel box included), per channel.
    expect(analytic.captured[0]).toBeCloseTo(0.98948, 4);
    expect(analytic.captured[2]).toBeCloseTo(0.99431, 4);
    const camera = psfWeights(analytic, ...CENTRE, CAMERA_PC, boxOf(CAMERA_PC)).share;
    const zoom = psfWeights(analytic, ...CENTRE, ZOOM_PC, boxOf(ZOOM_PC)).share;
    expect(camera).toEqual([1, 1, 1]);
    expect(zoom[0]).toBeCloseTo(0.95824, 4);
    expect(zoom[2]).toBeCloseTo(0.9758, 4);
  });

  it("samples the PSF's cell means to 2e-5 of the light (four sub-samples a side against eight)", () => {
    const small = { pivots: PIVOTS, cells: 128 };
    const four = psfTable(NGC, { ...small, subsamples: CELL_SUBSAMPLES });
    const eight = psfTable(NGC, { ...small, subsamples: 8 });
    let d = 0;
    for (let p = 0; p < four.corners.length; p += 1) d = Math.max(d, Math.abs(four.corners[p] - eight.corners[p]));
    expect(d).toBeLessThan(2e-5);
  });

  it("convolves a row with the pixel's box exactly: the light kept, a delta becomes the box", () => {
    const row = new Float64Array(64);
    row[32] = 1 / 0.5; // one cell of width 0.5 holding unit light
    const out = boxRow(row, 0.5, 2);
    expect(out.reduce((s, v) => s + v * 0.5, 0)).toBeCloseTo(1, 12);
    // The cell [16, 16.5] spread by a box of 2: a trapezoid over [15, 17.5], flat at 1/2 over [15.5, 17].
    expect(out[32]).toBeCloseTo(0.5, 12);
    expect(out[30]).toBeCloseTo(0.25, 12); // [15, 15.5]: the ramp's mean
    expect(out[29]).toBe(0);
  });
});

describe("the spikes' switch (S67, D227 R3)", () => {
  it("transforms the annulus to the obscured Airy within 3e-4 of the light (the FFT's error)", () => {
    const annulus = psfTable(NGC, { pivots: PIVOTS, density: imageDensity(pupilImage(NGC, false)) });
    let d = 0;
    for (let p = 0; p < analytic.corners.length; p += 1) d = Math.max(d, Math.abs(analytic.corners[p] - annulus.corners[p]));
    expect(d).toBeLessThan(3e-4);
  });

  it("draws the pupil: the annulus, four vanes of 0.022 pupil radii at 45 degrees to the frame, three pads", () => {
    expect(pupilOpen(0, 0, NGC)).toBe(false); // the secondary
    expect(pupilOpen(0.6, 0, NGC)).toBe(true); // on the frame's axis, between two vanes
    const d = 0.6 / Math.SQRT2;
    expect(pupilOpen(d, d, NGC)).toBe(false); // on a vane, 45 degrees to the frame
    expect(pupilOpen(d, d, NGC, false)).toBe(true);
    // Pad 1 at (V3, V2) = (0.8921, 0) in the pupil's axes: turned 45 degrees in the frame.
    const p = 0.8921 / Math.SQRT2;
    expect(pupilOpen(p + 0.05, -p + 0.05, NGC)).toBe(true);
    expect(pupilOpen(0.8921 * Math.cos(Math.PI / 4), 0.8921 * Math.sin(Math.PI / 4) - 0.6, NGC)).toBe(true);
  });

  it("moves no light: both tables sum to one in every box; the spikes carry more past the box", () => {
    for (const side of [CAMERA_PC, ZOOM_PC]) {
      const box = boxOf(side);
      for (const t of [analytic, spiked]) for (const s of sums(psfWeights(t, ...CENTRE, side, box).weights)) expect(Math.abs(s - 1)).toBeLessThan(1e-6);
    }
    expect(spiked.captured[0]).toBeCloseTo(0.9853, 3);
    const zoom = psfWeights(spiked, ...CENTRE, ZOOM_PC, boxOf(ZOOM_PC)).share;
    expect(zoom[0]).toBeCloseTo(0.9401, 3);
    expect(zoom[0]).toBeLessThan(psfWeights(analytic, ...CENTRE, ZOOM_PC, boxOf(ZOOM_PC)).share[0]);
  });

  it("puts the spikes on the diagonals: along 45 degrees the profile's far light exceeds along the axis", () => {
    // A square of one lambda/D in red (15 cells) at 16 lambda/D (240 cells) from the centre: the rings averaged over.
    const at = (x: number, y: number) => psfRect(spiked, [x - 7.5, y - 7.5], [x + 7.5, y + 7.5])[0];
    const r = 240;
    expect(at(r / Math.SQRT2, r / Math.SQRT2)).toBeGreaterThan(3 * at(r, 0));
    expect(at(r / Math.SQRT2, -r / Math.SQRT2)).toBeGreaterThan(3 * at(0, r));
    // Without the vanes the two are the same light, to the table's sampling.
    const ring = (t: typeof analytic, x: number, y: number) => psfRect(t, [x - 7.5, y - 7.5], [x + 7.5, y + 7.5])[0];
    // (within 7 %: the square pixel box and the square cells are not round)
    expect(Math.abs(ring(analytic, r / Math.SQRT2, r / Math.SQRT2) / ring(analytic, r, 0) - 1)).toBeLessThan(0.1);
  });
});
