import { ShaderLib } from "three";
import { describe, expect, it } from "vitest";

import {
  MAG_PER_TAU,
  NO_FRONT,
  POINTS_REGION_FRAGMENT,
  POINTS_REGION_PARS,
  POINTS_REGION_VERTEX,
  type PointsRegionUniforms,
  REGION_ORDER,
  marchTransmission,
  packObjects,
  patchPointsForRegion,
  pointTransmission,
  regionFragment,
  sphereChord,
} from "./region";

// The gate of T5 (S64, RULING_S64 R9): one cloud on the line of sight, a star in front of it and a star behind it,
// through the march's twin and the points' twin. The cloud is smooth (the layer off: no noise, no gradient, no
// cavity), so its optical depth on the axis is the published central one exactly: A_V / (2.5 log10 e), the diameter
// times kappa_V = tau_centre / (2 r). Its A_V is the census's (2.9696 mag); the extinction ratios are a synthetic
// set, standing in for /api/render's per-channel A_lambda / A_V.
const A_V = 2.9696;
const EXT: [number, number, number] = [1.3, 1.0, 0.75];
const eye: [number, number, number] = [0, 0, 0];
const axis: [number, number, number] = [1, 0, 0]; // the scene's +x: a cloud at azimuth 0, height 0 lies on it

/** Clouds on the +x axis at these radii (kpc) and sizes (pc), smooth and without a host cluster. */
function cloudsAt(radii: number[], sizes: number[]) {
  const n = radii.length;
  return {
    cloud_radius: radii, cloud_azimuth: Array(n).fill(0), cloud_height: Array(n).fill(0), cloud_size: sizes,
    cloud_mass: radii.map((_, i) => n - i), cloud_density_pdf_width: Array(n).fill(1.4), cloud_density_gradient: Array(n).fill(0),
    cloud_gradient_angle: Array(n).fill(0), cloud_cluster_index: Array(n).fill(-1), cell: Array(n).fill(300), index: radii.map((_, i) => i),
  };
}
const march = (table: ReturnType<typeof packObjects>, weight = 1, dir = axis, origin = eye) =>
  marchTransmission(origin, dir, table.data, table.count, EXT, weight, null);

describe("the depth-aware composite (T5): one cloud, a star in front and a star behind", () => {
  const table = packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, A_V);
  const ray = march(table);
  const texel: [number, number, number, number] = [...ray.trans, ray.alpha];

  it("writes the whole ray's transmission and the cloud's entry distance", () => {
    expect(table.count).toBe(1);
    // T per channel is exp(-tau_V x A_lambda/A_V), tau_V the central optical depth (float32 storage: 1e-6)
    for (let k = 0; k < 3; k += 1) {
      expect(Math.abs(ray.trans[k] / Math.exp((-A_V / MAG_PER_TAU) * EXT[k]) - 1)).toBeLessThan(1e-6);
    }
    // the front is the cloud's near edge, 8 kpc less 20 pc, negated: the entry t0 of the one cloud on the ray
    expect(ray.alpha).toBeLessThanOrEqual(0);
    expect(Math.abs(-ray.alpha - 7.98)).toBeLessThan(1e-6);
    const chord = sphereChord(eye, axis, [table.data[0], table.data[1], table.data[2]], table.data[3])!;
    expect(ray.alpha).toBeCloseTo(-chord[0], 12); // -(tau t0)/tau: t0 to the last bit or two
  });

  it("leaves the star in front undimmed and dims the star behind by exactly the cloud's T", () => {
    const star = [0.8, 0.6, 0.4];
    const front = pointTransmission(texel, 4);
    const behind = pointTransmission(texel, 12);
    expect(front).toEqual([1, 1, 1]);
    expect(star.map((v, k) => v * front[k])).toEqual(star);
    expect(behind).toEqual(ray.trans);
    expect(star.map((v, k) => v * behind[k])).toEqual(star.map((v, k) => v * ray.trans[k]));
    // Before S64 the multiply quad dimmed both: the star in front lost 1 - T of its V light, 93.5 %.
    expect(1 - ray.trans[1]).toBeCloseTo(1 - Math.exp(-A_V / MAG_PER_TAU), 6);
    expect(1 - ray.trans[1]).toBeGreaterThan(0.93);
    // A star past the entry but inside the cloud is behind the front: the whole cloud's T (the pixel holds one T).
    expect(pointTransmission(texel, 8)).toEqual(ray.trans);
    // A star exactly at the front is in front of it (the comparison is strict, as in the shader): undimmed.
    expect(pointTransmission(texel, -texel[3])).toEqual([1, 1, 1]);
  });

  it("draws the points between the multiply and the light", () => {
    expect(REGION_ORDER.multiply).toBeLessThan(REGION_ORDER.points);
    expect(REGION_ORDER.points).toBeLessThan(REGION_ORDER.light);
  });
});

describe("the front on other rays", () => {
  it("writes NO_FRONT where the ray meets no cloud, and the points then take nothing", () => {
    const table = packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, A_V);
    const miss = march(table, 1, [0, 1, 0]);
    expect(miss).toEqual({ trans: [1, 1, 1], alpha: NO_FRONT });
    expect(NO_FRONT).toBeGreaterThan(0);
    for (const d of [0.1, 8, 100]) expect(pointTransmission([1, 1, 1, NO_FRONT], d)).toEqual([1, 1, 1]);
    // a texel that says nothing is in front is not read as a front, whatever its colour (the clear's white, 1)
    expect(pointTransmission([0.2, 0.2, 0.2, NO_FRONT], 100)).toEqual([1, 1, 1]);
  });

  it("weights the entries by optical depth: two equal clouds give the midpoint, a heavier one pulls the front", () => {
    const equal = march(packObjects(cloudsAt([6, 10], [20, 20]), { cluster_radius: [] }, A_V));
    // equal tau (same A_V and size): the mean of the two entries, 5.98 and 9.98
    expect(Math.abs(-equal.alpha - 7.98)).toBeLessThan(1e-5);
    for (let k = 0; k < 3; k += 1) expect(Math.abs(equal.trans[k] / Math.exp((-2 * A_V / MAG_PER_TAU) * EXT[k]) - 1)).toBeLessThan(2e-6);
    // the same column per diameter, a larger cloud: tau on the axis is the central tau again (kappa scales as 1/r),
    // so a cloud's weight is its tau on the ray, not its size
    const sized = march(packObjects(cloudsAt([6, 10], [20, 40]), { cluster_radius: [] }, A_V));
    expect(Math.abs(-sized.alpha - (5.98 + 9.96) / 2)).toBeLessThan(1e-5);
    // a star between the two is behind the front (the tau-weighted mean): the stated approximation of one front
    expect(pointTransmission([...equal.trans, equal.alpha], 8.5)).toEqual(equal.trans);
    expect(pointTransmission([...equal.trans, equal.alpha], 7)).toEqual([1, 1, 1]);
  });

  it("puts the front at the camera when the camera is inside the cloud: every star is behind it", () => {
    const table = packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, A_V);
    const inside = march(table, 1, axis, [8, 0, 0]);
    expect(inside.alpha).toBeLessThanOrEqual(0);
    expect(-inside.alpha).toBe(0);
    // from the centre the ray crosses one radius: half the central optical depth
    expect(Math.abs(inside.trans[1] / Math.exp(-A_V / MAG_PER_TAU / 2) - 1)).toBeLessThan(1e-6);
    expect(pointTransmission([...inside.trans, inside.alpha], 0.001)).toEqual(inside.trans);
  });

  it("fades T with the regime's weight and keeps the front", () => {
    const table = packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, A_V);
    const full = march(table, 1);
    const half = march(table, 0.5);
    expect(half.alpha).toBe(full.alpha);
    for (let k = 0; k < 3; k += 1) expect(half.trans[k]).toBeCloseTo(0.5 + 0.5 * full.trans[k], 15);
  });

  it("draws nothing from a missing optical depth (B9): a cloud with no A_V writes no front", () => {
    const missing = march(packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, Number.NaN));
    expect(missing.alpha).toBe(NO_FRONT);
    expect(pointTransmission([...missing.trans, missing.alpha], 12)).toEqual([1, 1, 1]);
    // and a cloud of no optical depth is no front either
    expect(march(packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, 0)).alpha).toBe(NO_FRONT);
  });

  it("does not count HII regions or shells: they emit, the other pass's", () => {
    const clusters = {
      cluster_radius: [5], cluster_azimuth: [0], cluster_height: [0], hii_stromgren_radius: [30], hii_halpha_emissivity: [1e-20],
      bubble_radius: [40], bubble_shell_thickness: [5], bubble_shell_emissivity: [2e-21], cell: [300], index: [0],
    };
    const both = march(packObjects(cloudsAt([8], [20]), clusters, A_V));
    const alone = march(packObjects(cloudsAt([8], [20]), { cluster_radius: [] }, A_V));
    expect(both).toEqual(alone);
  });
});

describe("the twins and the shader text carry the same expressions", () => {
  it("the march: the two sums and the alpha", () => {
    const glsl = regionFragment(null);
    expect(glsl).toContain("float tauSum = 0.0;\n    float tauT0 = 0.0;");
    expect(glsl).toContain("trans *= exp(-tau * extRatio);\n        tauSum += tau;\n        tauT0 += tau * t0;");
    expect(glsl).toContain("else gl_FragColor = vec4(mix(vec3(1.0), trans, weight), tauSum > 0.0 ? -tauT0 / tauSum : 1.0);");
    expect(glsl).toContain("t0 = max(-b - h, 0.0);\n    t1 = -b + h;\n    return t1 > t0;");
    const twin = marchTransmission.toString();
    expect(twin).toContain("tauSum += tau;");
    expect(twin).toContain("tauT0 += tau * t0;");
    expect(twin).toContain("tauSum > 0 ? -tauT0 / tauSum : NO_FRONT");
    expect(twin).toContain("tau += c[2] * rho * ds;");
    expect(glsl).toContain("tau += c.z * rho * ds;");
    const chord = sphereChord.toString();
    expect(chord).toContain("Math.max(-b - h, 0)");
    expect(chord).toContain("t1 > t0");
  });

  it("the points: the factor, read once per star, and applied to the colour", () => {
    expect(POINTS_REGION_VERTEX).toContain("vRegionT = regionTexel.a <= 0.0 && regionDistance > -regionTexel.a ? regionTexel.rgb : vec3(1.0);");
    expect(POINTS_REGION_VERTEX).toContain("float regionDistance = length(regionWorld.xyz - cameraPosition);");
    expect(POINTS_REGION_VERTEX).toContain("texelFetch(regionTransmission,");
    expect(pointTransmission.toString()).toContain("texel[3] <= 0 && distance > -texel[3]");
    expect(POINTS_REGION_FRAGMENT).toContain("diffuseColor.rgb *= vRegionT;");
  });

  it("patches three's own points shader, and refuses one it cannot patch", () => {
    const uniforms: PointsRegionUniforms = { regionTransmission: { value: null }, regionOn: { value: false } };
    const shader = { vertexShader: ShaderLib.points.vertexShader, fragmentShader: ShaderLib.points.fragmentShader, uniforms: {} as Record<string, unknown> };
    patchPointsForRegion(shader, uniforms);
    expect(shader.uniforms.regionTransmission).toBe(uniforms.regionTransmission);
    expect(shader.uniforms.regionOn).toBe(uniforms.regionOn);
    expect(shader.vertexShader).toContain("#include <common>" + POINTS_REGION_PARS);
    expect(shader.vertexShader).toContain("#include <fog_vertex>" + POINTS_REGION_VERTEX);
    // the factor is set after gl_Position is (project_vertex) and read after the vertex colour is applied
    expect(shader.vertexShader.indexOf("#include <project_vertex>")).toBeLessThan(shader.vertexShader.indexOf("vRegionT = vec3(1.0);"));
    expect(shader.fragmentShader).toContain("#include <color_fragment>" + POINTS_REGION_FRAGMENT);
    expect(shader.fragmentShader).toContain("varying vec3 vRegionT;");
    expect(() => patchPointsForRegion({ vertexShader: "void main() {}", fragmentShader: "", uniforms: {} }, uniforms)).toThrow(/no "#include <common>"/);
  });
});
