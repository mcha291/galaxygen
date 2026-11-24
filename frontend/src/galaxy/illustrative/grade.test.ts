import { PerspectiveCamera, Vector3 } from "three";
import { describe, expect, it } from "vitest";

import { orbitPosition } from "../capture";
import { edge, edgeRamp } from "./edge";
import { framing, rolledUp } from "./framing";
import { CREAM, GRADE_FRAGMENT, LAVENDER, LUMA, ORANGE, SKY, grade, gradeColor, gradeTone, gradeUniforms, shoulder, toe } from "./grade";
import { illDefaults, paramsOf } from "./index";

const lum = (c: readonly number[]) => LUMA[0] * c[0] + LUMA[1] * c[1] + LUMA[2] * c[2];
/** Colour about luminance: the largest channel's distance from the luminance, over it. */
const chroma = (c: readonly number[]) => (Math.max(...c) - Math.min(...c)) / Math.max(lum(c), 1e-12);

// The grade with nothing of its own but the stretch: no shoulder below 0.95, no toe, no tint, no whitening.
const plain = {
  gain: 0, stretch: 30, white: 1, knee: 0.95, saturation: 1, faint: 0, faintsat: 1, contrast: 1, black: 0,
  balance: 0, split: 0, pivot: 0.6, cool: 0.5, warm: 0.5, green: 0, highlight: 0,
};

describe("the grade's tone curve (S105)", () => {
  it("stretches luminance by asinh below the knee: a grey goes to asinh(s g L) / asinh(s w)", () => {
    for (const L of [0.001, 0.05, 0.4]) {
      const out = gradeColor([L, L, L], plain);
      const y = Math.asinh(30 * L) / Math.asinh(30);
      for (const v of out) expect(v).toBeCloseTo(y, 12);
    }
    const twice = gradeColor([0.1, 0.1, 0.1], { ...plain, gain: 1 });
    expect(twice[0]).toBeCloseTo(Math.asinh(30 * 0.2) / Math.asinh(30), 12);
  });

  it("has a shoulder: the identity below the knee, continuous in value and slope there, monotone, never 1", () => {
    for (const k of [0.4, 0.6, 0.75, 0.9]) {
      for (const y of [0, 0.1, k * 0.5, k]) expect(shoulder(y, k)).toBe(y);
      const e = 1e-7;
      expect(shoulder(k + e, k)).toBeCloseTo(k + e, 12); // the value, and the slope 1, carried through the knee
      expect((shoulder(k + 2 * e, k) - shoulder(k + e, k)) / e).toBeCloseTo(1, 5);
      let last = -1;
      for (let y = 0; y < 40; y += 0.01) {
        const s = shoulder(y, k);
        expect(s).toBeGreaterThanOrEqual(last);
        expect(s).toBeLessThanOrEqual(1);
        if (y < 1.5) expect(s).toBeLessThan(1);
        last = s;
      }
      expect(shoulder(1e6, k)).toBeLessThanOrEqual(1);
    }
  });

  it("is monotone in luminance and never above 1 in any channel, at either template's preset and at the plain grade", () => {
    for (const p of [plain, paramsOf(grade, illDefaults("milky_way")), paramsOf(grade, illDefaults("ngc_4414"))]) {
      let last = -1;
      for (let e = -8; e <= 5; e += 0.02) {
        const L = 10 ** e;
        const y = gradeTone(L, p);
        expect(y).toBeGreaterThanOrEqual(last);
        last = y;
        for (const c of [[L, L, L], [L * 1.6, L, L * 0.5], [L * 0.6, L, L * 1.8], [L * 3, L * 0.4, L * 0.1]] as [number, number, number][]) {
          for (const v of gradeColor(c, p)) {
            expect(v).toBeGreaterThanOrEqual(0);
            expect(v).toBeLessThanOrEqual(1 + 1e-12);
          }
        }
      }
      expect(gradeColor([1e9, 1e9, 1e9], p).every((v) => Number.isFinite(v) && v <= 1)).toBe(true);
    }
  });

  it("has a soft black toe on luminance: 0 to 0, monotone, the identity at 0, each pixel's hue kept", () => {
    expect(toe(0.3, 0)).toBe(0.3);
    for (const b of [0.05, 0.1, 0.2]) {
      expect(toe(0, b)).toBeCloseTo(0, 12);
      expect(toe(1, b)).toBeCloseTo(1, 12);
      let last = -1;
      for (let y = 0; y <= 1; y += 0.001) {
        expect(toe(y, b)).toBeGreaterThan(last);
        last = toe(y, b);
      }
      expect(toe(b / 2, b)).toBeLessThan(b / 4); // the faint light under the level taken well down
    }
    const c: [number, number, number] = [0.002, 0.003, 0.006];
    const out = gradeColor(c, { ...plain, black: 0.1 });
    expect(out[0] / out[2]).toBeCloseTo(c[0] / c[2], 9); // no channel crushed first: the old per-channel cut made this pure blue
    expect(out[1] / out[2]).toBeCloseTo(c[1] / c[2], 9);
  });
});

describe("the grade's colour (S105)", () => {
  it("keeps each pixel's hue below the knee and divides by the largest channel past full scale", () => {
    const c: [number, number, number] = [0.02, 0.03, 0.05];
    const out = gradeColor(c, plain);
    expect(out[0] / out[2]).toBeCloseTo(c[0] / c[2], 12);
    expect(out[1] / out[2]).toBeCloseTo(c[1] / c[2], 12);
    expect(lum(out)).toBeCloseTo(Math.asinh(30 * lum(c)) / Math.asinh(30), 12);
    const bright = gradeColor([40, 20, 10], plain);
    expect(Math.max(...bright)).toBeCloseTo(1, 12);
    expect(bright[1] / bright[0]).toBeCloseTo(0.5, 12);
  });

  it("is the identity on colour at saturation 1, and moves it about luminance otherwise", () => {
    const c: [number, number, number] = [0.03, 0.02, 0.01];
    const at1 = gradeColor(c, plain);
    const grey = gradeColor(c, { ...plain, saturation: 0 });
    expect(grey[0]).toBeCloseTo(grey[2], 12);
    expect(grey[0]).toBeCloseTo(lum(at1), 12);
    const more = gradeColor(c, { ...plain, saturation: 2 });
    expect(more[0] - lum(at1)).toBeCloseTo(2 * (at1[0] - lum(at1)), 12);
  });

  it("drifts to a pale warm white only near the top: none below the knee, nearly all of it at the shoulder's end", () => {
    const p = { ...plain, knee: 0.6, highlight: 1 };
    const orange = (L: number): [number, number, number] => [L * 2, L * 0.8, L * 0.2];
    // Below the knee the hue is as drawn (the whitening and the saturation's take-off both nothing under 0.5).
    const low = orange(0.004);
    expect(gradeTone(lum(low), p)).toBeLessThan(0.5);
    const lowOut = gradeColor(low, p);
    expect(lowOut[1] / lowOut[0]).toBeCloseTo(0.4, 9);
    // The colour fades steadily through the shoulder, and a bar far past full scale is pale: cream, not orange.
    let last = Infinity;
    for (const L of [0.05, 0.2, 1, 5, 50]) {
      const out = gradeColor(orange(L), p);
      expect(chroma(out)).toBeLessThanOrEqual(last + 1e-9);
      last = chroma(out);
    }
    const top = gradeColor(orange(50), p);
    expect(chroma(top)).toBeLessThan(0.15);
    expect(top[0]).toBeGreaterThanOrEqual(top[1]);
    expect(top[1]).toBeGreaterThanOrEqual(top[2]); // warm white, red over blue
    expect(chroma(gradeColor(orange(50), { ...p, highlight: 0 }))).toBeGreaterThan(0.8); // without it, the saturated blob
  });

  it("fades the faint light's colour: grey-ward below `faint`, as drawn above it", () => {
    const p = { ...plain, saturation: 1.6, faint: 0.3, faintsat: 0.2 };
    const blue = (L: number): [number, number, number] => [L * 0.5, L * 0.9, L * 2];
    const faint = blue(0.0005);
    const bright = blue(0.1);
    expect(gradeTone(lum(faint), p)).toBeLessThan(0.05);
    expect(gradeTone(lum(bright), p)).toBeGreaterThan(0.3);
    const asDrawn = chroma(gradeColor(faint, plain));
    expect(chroma(gradeColor(faint, p))).toBeLessThan(0.5 * asDrawn);
    expect(chroma(gradeColor(bright, p))).toBeCloseTo(1.6 * chroma(gradeColor(bright, plain)), 6);
    // The fade is continuous: no step in the colour across the faint light.
    let prev = chroma(gradeColor(blue(1e-5), p));
    for (let e = -5; e <= -1.5; e += 0.01) {
      const ch = chroma(gradeColor(blue(10 ** e), p));
      expect(Math.abs(ch - prev)).toBeLessThan(0.05);
      prev = ch;
    }
  });

  it("tints with colours of their own: the cool side blue-lavender (red with green, never teal), the warm cream", () => {
    const grey = (L: number): [number, number, number] => [L, L, L];
    const p = { ...plain, split: 1, pivot: 0.5, cool: 1, warm: 1 };
    const faint = gradeColor(grey(0.002), p);
    expect(faint[2]).toBeGreaterThan(faint[1]);
    expect(faint[0]).toBeGreaterThanOrEqual(faint[1]); // lavender: red at least green
    const bright = gradeColor(grey(0.5), { ...p, knee: 0.98 });
    expect(bright[0]).toBeGreaterThan(bright[1]);
    expect(bright[1]).toBeGreaterThan(bright[2]);
    // The tints keep the stretched luminance.
    expect(lum(faint)).toBeCloseTo(gradeTone(0.002, p), 12);
    // The ends as stated.
    expect(SKY[2]).toBeGreaterThan(SKY[0]);
    expect(LAVENDER[0]).toBeGreaterThan(LAVENDER[1]);
    expect(ORANGE[1] - ORANGE[2]).toBeGreaterThan(0);
    expect(CREAM[1]).toBeGreaterThan(ORANGE[1]);
  });

  it("removes green: the green channel held to the mean of red and blue, luminance kept", () => {
    const c: [number, number, number] = [0.01, 0.03, 0.012];
    const out = gradeColor(c, { ...plain, green: 1 });
    expect(out[1]).toBeCloseTo(0.5 * (out[0] + out[2]), 12);
    expect(lum(out)).toBeCloseTo(gradeTone(lum(c), plain), 12);
    const pink: [number, number, number] = [0.03, 0.01, 0.02];
    expect(gradeColor(pink, { ...plain, green: 1 })).toEqual(gradeColor(pink, plain));
  });

  it("is the shader's text: the same constants and the same steps", () => {
    expect(GRADE_FRAGMENT).toContain("float y = gradeAsinh(uStretch * uGain * L) / gradeAsinh(uStretch * uWhite);");
    expect(GRADE_FRAGMENT).toContain(`dot(c, vec3(${LUMA.join(", ")}))`);
    expect(GRADE_FRAGMENT).toContain("y = gradeToe(gradeShoulder(y, uKnee), uBlack);");
    expect(GRADE_FRAGMENT).toContain("c2.g = mix(c2.g, min(c2.g, 0.5 * (c2.r + c2.b)), uGreen);");
    expect(GRADE_FRAGMENT).toContain("float w = uHighlight * smoothstep(uKnee, 1.0, y);");
    expect(GRADE_FRAGMENT).toContain("if (m > 1.0) c3 /= m;");
    for (const name of Object.keys(gradeUniforms({}))) expect(GRADE_FRAGMENT).toContain(`uniform float ${name};`);
  });
});

describe("the edge's tapers (S105)", () => {
  it("takes the clustered young light to nothing at its own edge, earlier than the field's, on both templates", () => {
    for (const t of ["milky_way", "ngc_4414"]) {
      const p = paramsOf(edge, illDefaults(t));
      expect(p.young).toBeLessThan(p.radius);
      expect(edgeRamp(p.young, p.young, p.youngwidth)).toBe(0);
      expect(edgeRamp(p.young - p.youngwidth, p.young, p.youngwidth)).toBe(1);
    }
    expect(edge.glsl).toContain("float illEdgeYoung(vec2 rp)");
    expect(edge.hooks?.youngGain).toBe("illEdgeYoung");
    // The default (no template): the young light as drawn.
    const d = paramsOf(edge, illDefaults(null));
    expect(d.young).toBe(30);
    expect(d.youngwidth).toBe(0);
  });
});

describe("the framing's roll (S105)", () => {
  const screenAngle = (camera: PerspectiveCamera, p: Vector3) => {
    const v = p.clone().project(camera);
    return (Math.atan2(v.y, v.x) * 180) / Math.PI;
  };
  const cameraAt = (inclination: number, azimuth: number, roll: number) => {
    const position = orbitPosition({ inclination_deg: inclination, azimuth_deg: azimuth, radius_kpc: 15 }, 5);
    const camera = new PerspectiveCamera(5, 1, 1, 1e5);
    camera.position.set(...position);
    camera.up.set(...rolledUp(position, roll));
    camera.lookAt(0, 0, 0);
    camera.updateMatrixWorld();
    return camera;
  };
  /** Two axis directions apart, degrees (mod 180). */
  const axisOff = (a: number, b: number) => { const d = (((a - b) % 180) + 180) % 180; return Math.min(d, 180 - d); };
  /** The direction of an inclined disc's long axis on screen, degrees in [0, 180). */
  const longAxis = (camera: PerspectiveCamera) => {
    let best = { r: -1, a: 0 };
    for (let phi = 0; phi < 360; phi += 0.25) {
      const p = new Vector3(10 * Math.cos((phi * Math.PI) / 180), 0, -10 * Math.sin((phi * Math.PI) / 180));
      const v = p.clone().project(camera);
      const r = Math.hypot(v.x, v.y);
      if (r > best.r) best = { r, a: (((Math.atan2(v.y, v.x) * 180) / Math.PI) % 180 + 180) % 180 };
    }
    return best.a;
  };

  it("is the disc's axis at no roll, a unit vector, and as far from the line of sight as the axis was", () => {
    expect(rolledUp([3, 4, 5], 0)).toEqual([0, 1, 0]);
    const position = orbitPosition({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 15 }, 5);
    const up = rolledUp(position, -30);
    expect(Math.hypot(...up)).toBeCloseTo(1, 12);
    const n = Math.hypot(...position);
    const along = (up[0] * position[0] + up[1] * position[1] + up[2] * position[2]) / n;
    expect(along).toBeCloseTo(position[1] / n, 12); // turned about the line of sight
  });

  it("turns the picture counter-clockwise by the roll, face-on and inclined", () => {
    const point = new Vector3(10, 0, 0);
    const a0 = screenAngle(cameraAt(0, 270, 0), point);
    const a30 = screenAngle(cameraAt(0, 270, 30), point);
    expect((((a30 - a0) % 360) + 360) % 360).toBeCloseTo(30, 4);
    expect(axisOff(longAxis(cameraAt(55, 0, 0)), 0)).toBeLessThan(2);
    // NGC 4414's preset: the long axis from upper left to lower right, 25 degrees below the horizontal (the goal's, by its second moments).
    const roll = paramsOf(framing, illDefaults("ngc_4414")).roll;
    expect(roll).toBe(-25);
    expect(axisOff(longAxis(cameraAt(55, 0, roll)), 155)).toBeLessThan(2);
  });

  it("leaves a stand unrolled where no template names a roll (S106: the Milky Way's bar at its goal's angle)", () => {
    expect(paramsOf(framing, illDefaults(null)).roll).toBe(0);
    expect(paramsOf(framing, illDefaults("milky_way")).roll).toBe(15);
    expect(paramsOf(framing, illDefaults("milky_way")).turn).toBe(0);
  });
});
