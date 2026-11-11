// T11 (S83): "as JWST" - NIRCam's set carries JWST's optics (instruments.json, written by tools/fetch_filters.py), the
// segmented primary is a pupil the PSF job images (hstPsf.ts pupilOpen, aperture "hexagonal-18"), and a set with its own
// optics is drawn physically at any template with a distance (psf.ts viewOptics). HST's path is held unchanged here too.
import { describe, expect, it } from "vitest";

import { FILTER_SETS } from "./filters";
import { type InstrumentFields, type Optics, FFT_SIZE, PUPIL_SAMPLES, SEGMENT_CENTRES, onSegment, opticsOf, pixelPc, psfRect, psfTable, pupilImage, pupilOpen } from "./hstPsf";
import { viewOptics } from "./psf";
import { psfJob } from "./psfTableJob";

// NGC 4414's instrument as /api/templates states it (templates.py): WFC3/UVIS at 17.7 Mpc, its own set WFC3's.
const NGC: InstrumentFields = {
  distance_mpc: 17.7,
  pixel_scale_arcsec: 0.04,
  aperture_m: 2.4,
  obscuration: 0.33,
  spider_width: 0.022,
  spider_vanes: 4,
  pads: [
    [0.8921, 0, 0.065],
    [-0.4615, 0.7555, 0.065],
    [-0.4564, -0.7606, 0.065],
  ],
};
// The Milky Way's: nothing read (R2).
const MW: InstrumentFields = { distance_mpc: null, pixel_scale_arcsec: null };
const JWST = FILTER_SETS.jwst_nircam;
const PIVOTS = JWST.sources!.map((s) => s.pivot);
const optics = viewOptics(NGC, FILTER_SETS.wfc3, JWST)!;

describe("whose optics a point is drawn with (S83, T11; psf.ts viewOptics)", () => {
  it("HST's set at NGC 4414: the template's instrument, field for field as before S83", () => {
    expect(viewOptics(NGC, FILTER_SETS.wfc3, FILTER_SETS.wfc3)).toEqual(opticsOf(NGC));
    expect(JSON.stringify(viewOptics(NGC, FILTER_SETS.wfc3, FILTER_SETS.wfc3n))).toBe(JSON.stringify(opticsOf(NGC))); // the table's key unchanged
    expect(viewOptics(NGC, FILTER_SETS.wfc3, FILTER_SETS.rgb)).toBeNull(); // a stand-in set: the sprite
  });

  it("NIRCam at NGC 4414: JWST's telescope and detectors at the template's distance, none of HST's numbers", () => {
    const o = JWST.optics!;
    expect(optics).toEqual({
      distanceMpc: 17.7,
      pixelArcsec: 0.063,
      apertureM: o.aperture_m,
      obscuration: o.obscuration,
      spiderWidth: o.spider_width,
      vanes: 3,
      pads: [],
      aperture: "hexagonal-18",
      segment: o.segment,
      gap: o.gap,
      vaneAngles: [90, 240, 300],
      channelPixelArcsec: [0.063, 0.031, 0.031],
    } satisfies Optics);
    // Each channel's own pixel: 0.063" x 17.7 Mpc = 5.41 pc in red, 0.031" = 2.66 pc in green and blue.
    const want = [0.063, 0.031, 0.031].map((a) => (a * Math.PI * 17.7e6) / (180 * 3600));
    [0, 1, 2].forEach((k) => expect(pixelPc(optics, k)).toBeCloseTo(want[k], 12));
  });

  it("NIRCam without a distance (the Milky Way) or without a template: the display sprite (R2)", () => {
    expect(viewOptics(MW, null, JWST)).toBeNull();
    expect(viewOptics(null, null, JWST)).toBeNull();
  });

  it("the template's numbers win over a set's where both are read (the same instrument)", () => {
    const merged = opticsOf(NGC, JWST.optics!)!;
    expect([merged.apertureM, merged.obscuration, merged.spiderWidth, merged.vanes, merged.pixelArcsec]).toEqual([2.4, 0.33, 0.022, 4, 0.04]);
    expect(merged.vaneAngles).toBeUndefined(); // the template's vanes, evenly spaced
    expect(merged.channelPixelArcsec).toBeUndefined(); // the template's one pixel
  });
});

describe("JWST's primary as a pupil (S83, T11; hstPsf.ts pupilOpen, hexagonal-18)", () => {
  const s = optics.segment!;
  const p = s + optics.gap!; // the pitch: a segment and a gap

  it("is 18 flat-topped segments of 1.32 m, 7 mm apart, about a missing centre: 6.63 m across the flats in a 6.67 m circle", () => {
    expect(SEGMENT_CENTRES).toHaveLength(18);
    expect(onSegment(0, 0, s, optics.gap)).toBe(false); // the missing centre (the secondary's shadow inside it)
    const top = 2 * p + s / 2; // the top flat: the column's second segment up
    expect(onSegment(0, top - 1e-6, s, optics.gap) && !onSegment(0, top + 1e-6, s, optics.gap)).toBe(true);
    expect(!onSegment(0, s / 2 + optics.gap! / 2, s, optics.gap)).toBe(true); // in the gap between the centre's neighbours' rows
    const metres = optics.apertureM / 2; // a pupil radius
    expect(s * metres).toBeCloseTo(1.32, 4);
    expect(optics.gap! * metres).toBeCloseTo(0.007, 5);
    expect(2 * top * metres).toBeCloseTo(4 * 1.327 + 1.32, 3);
    // Every segment inside the unit circle, the outermost corners on it.
    let far = 0;
    for (const [cx, cy] of SEGMENT_CENTRES) {
      for (let k = 0; k < 6; k += 1) far = Math.max(far, Math.hypot(cx * p + (s / Math.sqrt(3)) * Math.cos((k * Math.PI) / 3), cy * p + (s / Math.sqrt(3)) * Math.sin((k * Math.PI) / 3)));
    }
    expect(far).toBeCloseTo(1, 5);
  });

  it("has three struts that cover 1 - 25.4/26.3 of the segments (JDox's unobscured over polished area)", () => {
    const n = 1201;
    let open = 0;
    let segments = 0;
    for (let j = 0; j < n; j += 1) {
      for (let i = 0; i < n; i += 1) {
        const x = -1 + (2 * (i + 0.5)) / n;
        const y = -1 + (2 * (j + 0.5)) / n;
        if (pupilOpen(x, y, optics, false)) segments += 1;
        if (pupilOpen(x, y, optics, true)) open += 1;
      }
    }
    expect(1 - open / segments).toBeCloseTo(1 - 25.4 / 26.3, 3);
    // The segments' area: 18 hexagons of flat-to-flat s, (sqrt 3 / 2) s^2 each, of the square's 4.
    expect(segments / (n * n)).toBeCloseTo((18 * (Math.sqrt(3) / 2) * s * s) / 4, 3);
    expect(1 - open / segments).toBeGreaterThan(0.03);
    expect(pupilOpen(0, 0.5, optics, false)).toBe(true); // on the segment above the centre,
    expect(pupilOpen(0, 0.5, optics, true)).toBe(false); // which the upper strut crosses
    expect(pupilOpen(0.5 * Math.cos((240 * Math.PI) / 180), 0.5 * Math.sin((240 * Math.PI) / 180), optics, true)).toBe(false); // a lower strut
  });
});

/** The pupil's image's light at radii [r0, r1] lambda/D in a narrow wedge (+-2 degrees) about each direction, degrees. */
function wedgeLight(image: Float64Array, degs: number[], r0: number, r1: number): number[] {
  const n = FFT_SIZE;
  const spacing = PUPIL_SAMPLES / n;
  const out = degs.map(() => 0);
  for (let j = 0; j < n; j += 1) {
    for (let i = 0; i < n; i += 1) {
      const x = (i - n / 2) * spacing;
      const y = (j - n / 2) * spacing;
      const r = Math.hypot(x, y);
      if (r < r0 || r > r1) continue;
      const a = ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
      degs.forEach((d, k) => {
        const off = Math.abs(((a - d + 540) % 360) - 180);
        if (off <= 2) out[k] += image[j * n + i];
      });
    }
  }
  return out;
}

describe("JWST's image of a point (S83, T11): the same transform, the same table, the light held", () => {
  const segments = pupilImage(optics, false);
  const struts = pupilImage(optics, true);
  const spikes = [90, 270, 30, 210, 150, 330];
  const between = [60, 240, 120, 300];
  const horizontal = [0, 180];

  it("the segments alone make six spikes: along the edges' normals the far light is many times the light between them", () => {
    const along = wedgeLight(segments, spikes, 8, 40);
    const off = wedgeLight(segments, between, 8, 40);
    const meanOff = off.reduce((a, b) => a + b, 0) / off.length;
    for (const v of along) expect(v / meanOff).toBeGreaterThan(3); // 4.0-4.2 measured (S83)
  });

  it("the struts add a horizontal pair from the upper strut and strengthen the four diagonals, the vertical pair left", () => {
    // Measured (S83, the drawn 2048^2 transform), the light in +-2 degrees at 8-40 lambda/D, segments alone -> with the
    // struts: horizontal 2.9 -> 22.1 (1e-4 of the light), diagonals 11.3 -> 26.5, vertical 12.0 -> 10.8.
    const ratio = (degs: number[]) => {
      const a = wedgeLight(segments, degs, 8, 40);
      const b = wedgeLight(struts, degs, 8, 40);
      return b.map((v, k) => v / a[k]);
    };
    for (const r of ratio(horizontal)) expect(r).toBeGreaterThan(4);
    for (const r of ratio([30, 150, 210, 330])) expect(r).toBeGreaterThan(1.5);
    for (const r of ratio([90, 270])) expect(Math.abs(r - 1)).toBeLessThan(0.2);
  });

  it("a table of each switch holds the light: the whole table sums to one per channel, and the job builds the same table", () => {
    // A small table and transform for speed; the drawn tables are 768 cells on the 2048^2 transform (psfTableJob.ts).
    const fft = { n: 512, m: 64 };
    for (const spike of [false, true]) {
      const table = psfJob({ optics, pivots: PIVOTS, spikes: spike, cells: 96, fft });
      const whole = psfRect(table, [-48, -48], [48, 48]);
      for (const v of whole) expect(Math.abs(v - 1)).toBeLessThan(1e-6);
      expect(table.captured.every((c) => c > 0.5 && c <= 1 + 1e-9)).toBe(true);
    }
    // The circular case is untouched: off is the obscured Airy, no transform (S67's table, by its own builder).
    const hst = opticsOf(NGC)!;
    const pivots = FILTER_SETS.wfc3.sources!.map((x) => x.pivot);
    expect(psfJob({ optics: hst, pivots, spikes: false, cells: 64 }).corners).toEqual(psfTable(hst, { pivots, cells: 64 }).corners);
  });
});
