import { describe, expect, it } from "vitest";

import { SKEL_CONTRAST_MAX, SKEL_MEAN_SAMPLES, skeletonParamsOf, skeletonPlanes } from "./armsSkeleton";
import type { Piece } from "./lanesMap";
import { SKELETON_DEFAULTS, armAt, bandProfile, buildSkeleton, grainDensity, ovalIn, ovalOut, patchAt, piecesPitch, ridgeAt, ridgeLine, sampleRidges, skeletonBand } from "./skeleton";

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

describe("the arm skeleton's S107 controls (the Milky Way's spiral and patchy arms)", () => {
  it("leaves the S106 skeleton at their defaults", () => {
    const s106 = buildSkeleton({ pieces, bar }, { lesser: 2, spurs: 3 });
    const zeros = buildSkeleton({ pieces, bar }, { lesser: 2, spurs: 3, pitchGrow: 0, open: 0, lesserWidth: 0.85, lesserReach: 0.92, patch: 0, ragged: 0 });
    expect(zeros.arms.map((a) => [a.phi, a.width, a.r1])).toEqual(s106.arms.map((a) => [a.phi, a.width, a.r1]));
    expect(s106.arms.every((a) => a.patch === null && a.wIn === null)).toBe(true);
  });

  it("opens the pitch outward, leaves the bar more steeply, and sets the lessers' width and reach", () => {
    const flat = buildSkeleton({ pieces, bar }, { drift: 0, kink: 0, lesser: 2, spurs: 0 });
    const grown = buildSkeleton({ pieces, bar }, { drift: 0, kink: 0, lesser: 2, spurs: 0, pitchGrow: 0.5, open: 1, lesserWidth: 0.5, lesserReach: 0.6 });
    const m = grown.arms[0];
    // Steeper at the start (the open) and far out (the growth); the same pitch nowhere near both.
    expect(m.tanp[0]).toBeGreaterThan(1.5 * flat.arms[0].tanp[0]);
    expect(m.tanp[m.n - 1]).toBeGreaterThan(1.5 * flat.arms[0].tanp[flat.arms[0].n - 1]);
    // Fewer turns to the edge.
    expect(Math.abs(m.phi[m.n - 1] - m.phi[0])).toBeLessThan(0.75 * Math.abs(flat.arms[0].phi[flat.arms[0].n - 1] - flat.arms[0].phi[0]));
    const lesser = grown.arms.filter((a) => a.kind === "lesser");
    for (const a of lesser) {
      expect(a.width).toBeCloseTo(0.5 * grown.width, 9);
      expect(a.r1).toBeCloseTo(0.6 * m.r1, 6);
    }
  });

  it("clumps the glow and the grain along an arm, keeping each ring's mean from the unclumped band", () => {
    const sk = buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 0, patch: 0.9, patchScale: 1, ragged: 0.5 });
    const a = sk.arms[0];
    expect(a.patch).not.toBeNull();
    const vals = Array.from(a.patch!);
    expect(Math.max(...vals)).toBeLessThanOrEqual(1);
    expect(Math.min(...vals)).toBeLessThan(0.4);
    expect(vals.filter((v) => v > 0.95).length).toBeGreaterThan(0.1 * vals.length);
    // The grain follows the clumps.
    const hit = ridgeAt(sk, 9, armAt(a, 9)!.phi);
    expect(hit.patch).toBeCloseTo(patchAt(a, 9), 9);
    expect(grainDensity(hit, 0.05, 0)).toBeCloseTo(Math.min(1, 1.05 * hit.patch!), 6);
    // The planes' ring means are the unclumped band's: the same as with no clumps where the sides are even.
    const even = buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 0, patch: 0.9, patchScale: 1 });
    const none = buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 0 });
    const pe = skeletonPlanes(even, 200, 360, 20, 0.2, 1);
    const pn = skeletonPlanes(none, 200, 360, 20, 0.2, 1);
    // (to the far tail the clumped band reaches a little further: the ragged sides may be wider)
    pe.ringMean.forEach((v, k) => expect(v).toBeCloseTo(pn.ringMean[k], 3));
    expect(pe.share).not.toEqual(pn.share);
  });

  it("draws a spur's glow without a wing", () => {
    const sk = buildSkeleton({ pieces, bar }, { lesser: 0, spurs: 1 });
    const spurOnly = { ...sk, arms: [sk.arms[2]] };
    const band = skeletonBand(spurOnly, 200, 720, 20, 0.5);
    const noWing = skeletonBand(spurOnly, 200, 720, 20, 0);
    expect(band).toEqual(noWing);
  });
});

describe("the even winding (S107, MW2)", () => {
  it("leaves the lessers as they were at its defaults", () => {
    const before = buildSkeleton({ pieces, bar }, { lesser: 3, spurs: 2, open: 0.8, pitchGrow: 0.35 });
    const at = buildSkeleton({ pieces, bar }, { lesser: 3, spurs: 2, open: 0.8, pitchGrow: 0.35, nudge: 35, even: 0 });
    expect(at.arms.map((a) => [a.phi, a.tanp])).toEqual(before.arms.map((a) => [a.phi, a.tanp]));
  });

  it("lays the lessers at even shares of the gaps between the majors on every ring", () => {
    const sk = buildSkeleton({ pieces, bar }, { lesser: 3, spurs: 0, open: 0.8, pitchGrow: 0.35, drift: 0.3, nudge: 0, even: 1 });
    const [m0, m1] = sk.arms;
    const lessers = sk.arms.filter((a) => a.kind === "lesser");
    const want = [1 / 3, 2 / 3, 1.5];
    for (const R of [8, 11, 15]) {
      const p0 = armAt(m0, R)!.phi;
      const gap0 = ((((armAt(m1, R)!.phi - p0) % TAU) + TAU) % TAU);
      lessers.forEach((a, k) => {
        const off = ((((armAt(a, R)!.phi - p0) % TAU) + TAU) % TAU);
        const share = off < gap0 ? off / gap0 : 1 + (off - gap0) / (TAU - gap0);
        expect(share).toBeCloseTo(want[k], 3);
      });
    }
    // The pitch read back off the moved crest stays a winding in the pieces' sense.
    for (const a of lessers) for (let i = 1; i < a.n; i++) expect(a.phi[i]).toBeGreaterThan(a.phi[i - 1]);
  });
});

describe("the skeleton's least pitch (S108, a rerolled galaxy)", () => {
  it("opens the arms of near-circular pieces to the floor and leaves a template's pitch as it was", () => {
    const piece = (pitchDeg: number, r0: number): Piece => ({ chain: 0, order: 0, r0, phi0: 0, pitchDeg, extent: 1, join: 0 }) as unknown as Piece;
    const tight = buildSkeleton({ pieces: [piece(1.4, 4), piece(1.3, 6), piece(1.5, 8)], bar: null });
    expect(tight.pitchDeg).toBeCloseTo(SKELETON_DEFAULTS.pitchMin ?? 0, 9);
    const open = buildSkeleton({ pieces: [piece(12.6, 4), piece(12.6, 6)], bar: null });
    expect(open.pitchDeg).toBeCloseTo(12.6, 9);
  });
});

describe("the pitch floor's slider (S108 J2, arms.skelpitchmin)", () => {
  it("reaches the skeleton: absent the default floor, set the floor it names", () => {
    expect(skeletonParamsOf({}).pitchMin).toBe(SKELETON_DEFAULTS.pitchMin);
    const piece = (pitchDeg: number, r0: number): Piece => ({ chain: 0, order: 0, r0, phi0: 0, pitchDeg, extent: 1, join: 0 }) as unknown as Piece;
    const g = { pieces: [piece(1.4, 4), piece(1.3, 6), piece(1.5, 8)], bar: null };
    expect(buildSkeleton(g, skeletonParamsOf({ skelpitchmin: 16 })).pitchDeg).toBeCloseTo(16, 9);
    expect(buildSkeleton(g, skeletonParamsOf({ skelpitchmin: 4 })).pitchDeg).toBeCloseTo(4, 9);
  });
});

describe("the hug (S109, arms.skelopen below 0)", () => {
  const hugParams = { lesser: 3, spurs: 0, drift: 0, kink: 0, open: -0.8, openTurns: 0.3, pitchGrow: 0.35, start: 0.85 };
  it("runs each major round the bar close to its end before it opens, and reads its band along the ray", () => {
    const sk = buildSkeleton({ pieces, bar }, hugParams);
    const [a] = sk.arms;
    expect(a.ray).toBe(true);
    // A quarter turn on, the crest is within 1.15 of its start (the S108 skeleton's open arm: past 1.4).
    let i = 0;
    while (i < a.n - 1 && (a.phi[i] - a.phi[0]) * sk.sense < Math.PI / 2) i++;
    expect(Math.exp(a.lnR0 + i * a.dlnR) / a.r0).toBeLessThan(1.15);
    const open = buildSkeleton({ pieces, bar }, { ...hugParams, open: 0.8, openTurns: 0.175 });
    expect(open.arms[0].ray).toBeUndefined();
    // Read along the ray: just inside the crest a quarter turn on, the band is the crest's (a ring reading had nothing
    // inside the start's radius: a hard dark disc), and half a ridge width inside it, about half.
    const W = 2000;
    const H = 3600;
    const band = skeletonBand(sk, W, H, 30, 0);
    const R = Math.exp(a.lnR0 + i * a.dlnR);
    const row = Math.round(((((a.phi[i] % TAU) + TAU) % TAU) / TAU) * H - 0.5);
    const col = (r: number) => Math.round((r / 30) * W - 0.5);
    expect(band[row * W + col(R)]).toBeGreaterThan(0.8 * a.strength[i]);
    const half = band[row * W + col(R - a.width / 2)] / band[row * W + col(R)];
    expect(half).toBeGreaterThan(0.3);
    expect(half).toBeLessThan(0.7);
    // ridgeAt agrees: on the crest, nearly no distance.
    expect(ridgeAt(sk, R, a.phi[i]).distance).toBeLessThan(0.05);
  });
  it("builds its planes within a slider's budget", () => {
    const sk = buildSkeleton({ pieces, bar }, { ...hugParams, patch: 0.9, ragged: 0.5 });
    const t0 = performance.now();
    skeletonPlanes(sk, 2000, 3600, 30, 0.35, 32, null);
    const ms = performance.now() - t0;
    console.log(`hug skeleton planes: ${ms.toFixed(0)} ms`);
    expect(ms).toBeLessThan(600);
  });
});

describe("the oval round the bar (S109 A2, arms.skeloval)", () => {
  const params = { oval: 0.6, ovalReach: 1.0, ovalFade: 2.0 };
  it("is absent at 1 and leaves the band byte for byte", () => {
    const plain = buildSkeleton({ pieces, bar }, {});
    const one = buildSkeleton({ pieces, bar }, { oval: 1, ovalReach: 1, ovalFade: 2 });
    expect(one.oval).toBeUndefined();
    expect(Array.from(skeletonBand(one, 96, 128, 30, 0.15))).toEqual(Array.from(skeletonBand(plain, 96, 128, 30, 0.15)));
  });
  it("squashes across the bar to q inside its reach, not along it, and not beyond its fade", () => {
    const sk = buildSkeleton({ pieces, bar }, params);
    expect(sk.oval).toBeDefined();
    expect(ovalOut(sk, 4, bar.angle)).toBeCloseTo(4, 9);
    expect(ovalOut(sk, 4, bar.angle + Math.PI / 2)).toBeCloseTo(0.6 * 4, 9);
    expect(ovalOut(sk, 10.5, bar.angle + Math.PI / 2)).toBe(10.5);
  });
  it("ovalIn inverts ovalOut at every azimuth, and the plane's radius grows with the skeleton's", () => {
    const sk = buildSkeleton({ pieces, bar }, params);
    for (let k = 0; k < 16; k++) {
      const phi = (k / 16) * TAU;
      let last = 0;
      for (let Rs = 0.2; Rs < 12; Rs += 0.35) {
        const R = ovalOut(sk, Rs, phi);
        expect(R).toBeGreaterThan(last);
        last = R;
        expect(ovalIn(sk, R, phi)).toBeCloseTo(Rs, 4);
      }
    }
  });
  it("draws the lanes' ridge points through the oval, the band and ridgeAt read through it", () => {
    const sk = buildSkeleton({ pieces, bar }, params);
    const a = sk.arms[0];
    const l = ridgeLine(a, 0.2, sk);
    for (let i = 0; i < l.x.length; i += 7) expect(Math.hypot(l.x[i], l.y[i])).toBeCloseTo(ovalOut(sk, l.r[i], l.phi[i]), 6);
    const i = Math.floor(l.x.length / 6);
    const Rp = Math.hypot(l.x[i], l.y[i]);
    expect(ridgeAt(sk, Rp, l.phi[i]).distance).toBeLessThan(0.05);
  });
});
