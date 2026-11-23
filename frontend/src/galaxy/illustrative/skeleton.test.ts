import { describe, expect, it } from "vitest";

import { SKEL_CONTRAST_MAX, SKEL_MEAN_SAMPLES, skeletonPlanes } from "./armsSkeleton";
import type { Piece } from "./lanesMap";
import { SKELETON_DEFAULTS, armAt, bandProfile, buildSkeleton, grainDensity, piecesPitch, ridgeAt, ridgeLine, sampleRidges, skeletonBand } from "./skeleton";

/** Pieces of a trailing 12-degree winding (phi growing outward), two chains half a turn apart. */
const pieces: Piece[] = [0, 1].flatMap((c) =>
  [0, 1, 2].map((o) => {
    const tan = Math.tan((12 * Math.PI) / 180);
    const r0 = 5 * Math.exp(o * 0.8 * tan);
    return { chain: c, order: o, r0, phi0: c * Math.PI + 1 + o * 0.8, pitchDeg: 12, extent: 0.8, join: 0 };
  }),
);
const bar = { halfLength: 5, angle: 0.6 };
const TAU = 2 * Math.PI;

describe("the arm skeleton", () => {
  it("reads the pieces' pitch and sense", () => {
    expect(piecesPitch(pieces)).toEqual({ pitchDeg: 12, sense: 1 });
    const flipped = pieces.map((p) => ({ ...p, pitchDeg: -p.pitchDeg }));
    expect(piecesPitch(flipped).sense).toBe(-1);
  });

  it("draws two majors from the bar's ends, the lesser arms and the spurs the sliders ask for", () => {
    const sk = buildSkeleton({ pieces, bar }, { lesser: 2, spurs: 3 });
    expect(sk.arms.map((a) => a.kind)).toEqual(["major", "major", "lesser", "lesser", "spur", "spur", "spur"]);
    const [a, b] = sk.arms;
    expect(a.r0).toBeCloseTo(5, 6);
    expect(a.phi[0]).toBeCloseTo(0.6, 6);
    expect(b.phi[0]).toBeCloseTo(0.6 + Math.PI, 6);
    expect(a.r1).toBeCloseTo(SKELETON_DEFAULTS.outer, 6);
    expect(buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 0 }).arms).toHaveLength(2);
  });

  it("winds each arm continuously, in the pieces' sense, at about their pitch", () => {
    const sk = buildSkeleton({ pieces, bar }, { drift: 0, kink: 0 });
    const a = sk.arms[0];
    for (let i = 1; i < a.n; i++) expect(a.phi[i]).toBeGreaterThan(a.phi[i - 1]);
    // Without drift, a log spiral: turns = ln(r1 / r0) / tan(pitch) / 2 pi.
    const turns = (a.phi[a.n - 1] - a.phi[0]) / TAU;
    expect(turns).toBeCloseTo(Math.log(a.r1 / a.r0) / Math.tan((12 * Math.PI) / 180) / TAU, 2);
    // The drift moves the winding a little, never reverses it.
    const drifted = buildSkeleton({ pieces, bar }, { drift: 0.3, kink: 0.4 }).arms[0];
    for (let i = 1; i < drifted.n; i++) expect(drifted.phi[i]).toBeGreaterThan(drifted.phi[i - 1]);
    expect(Math.abs((drifted.phi[drifted.n - 1] - drifted.phi[0]) / TAU - turns)).toBeLessThan(0.35 * turns);
  });

  it("is strong inside and fades out at the outer end", () => {
    const a = buildSkeleton({ pieces, bar }).arms[0];
    const mid = armAt(a, 9)!;
    expect(mid.strength).toBeGreaterThan(0.7);
    expect(armAt(a, a.r1)!.strength).toBeLessThan(0.05);
    expect(armAt(a, a.r1 * 1.01)).toBeNull();
  });

  it("finds the nearest ridge, its strength and its side", () => {
    const sk = buildSkeleton({ pieces, bar }, { spurs: 0 });
    const a = armAt(sk.arms[0], 8)!;
    const on = ridgeAt(sk, 8, a.phi);
    expect(on.arm).toBe(0);
    expect(on.distance).toBeLessThan(1e-9);
    expect(on.strength).toBeCloseTo(a.strength, 9);
    const sin = a.tanp / Math.hypot(1, a.tanp);
    const off = ridgeAt(sk, 8, a.phi + 0.3 / (8 * sin));
    expect(off.distance).toBeCloseTo(0.3, 6);
    expect(off.side).toBe(1);
    expect(ridgeAt(sk, 8, a.phi - 0.3 / (8 * sin)).side).toBe(-1);
    // A ring no arm reaches.
    expect(ridgeAt(sk, 1, 0).arm).toBe(-1);
  });

  it("lays a band of the ridge's width on the map grid, fast", () => {
    const sk = buildSkeleton({ pieces, bar });
    const t0 = performance.now();
    const band = skeletonBand(sk, 2000, 3600, 30, 0.15);
    const ms = performance.now() - t0;
    expect(ms).toBeLessThan(600);
    // At a crest the band is the strength; one FWHM/2 across, half of it (less the wing's share).
    const a = sk.arms[0];
    const h = armAt(a, 9.0075)!;
    const c = Math.round((9.0075 / 30) * 2000 - 0.5);
    const row = Math.round(((((h.phi % TAU) + TAU) % TAU) / TAU) * 3600 - 0.5);
    expect(band[row * 2000 + c]).toBeCloseTo(h.strength, 1);
    expect(bandProfile(0.3, 0.6, 0)).toBeCloseTo(0.5, 4);
    // Between the arms (a quarter turn from both majors at a radius the lesser arms are off), nothing.
    const none = buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 0 });
    const b0 = skeletonBand(none, 400, 360, 30, 0);
    const h0 = armAt(none.arms[0], 9)!;
    const r0 = Math.round(((((h0.phi + Math.PI / 2) % TAU) + TAU) % TAU) / TAU * 360 - 0.5);
    expect(b0[r0 * 400 + Math.round((9 / 30) * 400 - 0.5)]).toBeLessThan(1e-3);
  });

  it("builds the arms' planes of the shared map within a slider's budget", () => {
    const sk = buildSkeleton({ pieces, bar }, { width: 0.45 });
    const n = new Float64Array(400 * 360).fill(1);
    skeletonPlanes(sk, 2000, 3600, 30, 0.15, 32, { n, nR: 400, nPhi: 360 });
    const t0 = performance.now();
    const planes = skeletonPlanes(sk, 2000, 3600, 30, 0.15, 32, { n, nR: 400, nPhi: 360 });
    const ms = performance.now() - t0;
    console.log(`skeleton planes: ${ms.toFixed(0)} ms`);
    expect(ms).toBeLessThan(600);
    expect(planes.ringMean).toHaveLength(SKEL_MEAN_SAMPLES);
    expect(planes.flags.every((f) => f === 65535)).toBe(true);
    // A carries the contrast: 1 over SKEL_CONTRAST_MAX everywhere for a flat field.
    // (dithered by at most half a byte: S106 B5, the ring banding)
    expect(Math.abs(planes.mean[12345] - 255 / SKEL_CONTRAST_MAX)).toBeLessThanOrEqual(1);
    let sum = 0;
    for (let i = 0; i < planes.mean.length; i += 97) sum += planes.mean[i];
    expect(sum / Math.ceil(planes.mean.length / 97)).toBeCloseTo(255 / SKEL_CONTRAST_MAX, 1);
  });

  it("samples points along the ridges, deterministically", () => {
    const sk = buildSkeleton({ pieces, bar });
    const s = sampleRidges(sk, 2000, 5, 0.3);
    expect(s.radius.length).toBe(2000);
    expect(sampleRidges(sk, 2000, 5, 0.3).azimuth).toEqual(s.azimuth);
    let near = 0;
    for (let i = 0; i < s.radius.length; i++) if (ridgeAt(sk, s.radius[i], s.azimuth[i]).distance < sk.width) near++;
    expect(near / s.radius.length).toBeGreaterThan(0.95);
  });

  it("gives the grain a crest, shoulders and a tail", () => {
    const hit = (d: number) => ({ distance: d, strength: 1, arm: 0, side: 1, width: 0.6 });
    expect(grainDensity(hit(0), 0.05, 1)).toBeCloseTo(1, 6);
    expect(grainDensity(hit(0.3), 0.05, 1)).toBeLessThan(0.5);
    expect(grainDensity(hit(1.2), 0.05, 1)).toBeGreaterThan(0.01);
    expect(grainDensity(hit(1.2), 0.05, 1)).toBeLessThan(0.06);
    expect(grainDensity({ ...hit(0), strength: 0.5 }, 0.05, 2)).toBeCloseTo(0.25, 6);
  });

  it("samples a crest line evenly", () => {
    const a = buildSkeleton({ pieces, bar }).arms[0];
    const l = ridgeLine(a, 0.1);
    for (let i = 1; i < l.x.length; i++) expect(Math.hypot(l.x[i] - l.x[i - 1], l.y[i] - l.y[i - 1])).toBeCloseTo(0.1, 1);
  });
});
