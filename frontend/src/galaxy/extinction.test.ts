import { describe, expect, it } from "vitest";

import { FIELD_LAYERS, brightestLayers, fieldLayers } from "./components";
import { FLUX_POINTS_SHADER } from "./FluxPoints";
import { KIND, MAG_PER_TAU, OBJECT_FLOATS, marchFieldTransmission, marchTransmission, packObjects, scaleCloudDepths } from "./region";
import { composeStep } from "./regimes";
import { TUNING_CONTROLS, TUNING_DEFAULTS } from "./tuning";

// The extinction strength (S67, D228): "Yes, add an extinction-strength display slider as well; I rule it a display
// choice" (the owner, 2026-10-18). Every optical depth the viewer draws is multiplied by it - the march's dust depth
// (the diffuse dust and the clouds' raster both read it), the dust to each point, the region's clouds - and never the
// dust's own light. At its default, 1, every number is the model's, so no frame moves.

describe("the extinction strength (S67, D228, the owner's ruling)", () => {
  it("defaults to 1, the model's extinction, and is a linear 0-2 control in Components", () => {
    expect(TUNING_DEFAULTS.extinctionStrength).toBe(1);
    expect(TUNING_CONTROLS.find((c) => c.key === "extinctionStrength")).toMatchObject({ group: "Components", kind: "range", min: 0, max: 2, step: 0.01 });
  });

  it("is the march's dust depth in both modes, and leaves every emitting layer alone", () => {
    const t = { ...TUNING_DEFAULTS };
    expect(fieldLayers(t)).toEqual({ ...FIELD_LAYERS }); // at 1: FIELD_LAYERS exactly
    expect(brightestLayers(t, null).dustDepth).toBe(1);
    for (const s of [0, 0.37, 2]) {
      const f = fieldLayers({ ...t, extinctionStrength: s });
      expect(f.dustDepth).toBe(s);
      expect([f.stars, f.gas, f.dust]).toEqual([1, 1, 1]);
      const b = brightestLayers({ ...t, extinctionStrength: s }, null);
      expect(b.dustDepth).toBe(s);
      expect(b.dust).toBe(t.dustIntensity); // the dust's own light is the dust intensity's, not this
    }
    // the dust "where it is" dims nothing, whatever the strength
    expect(brightestLayers({ ...t, dustReading: "where", extinctionStrength: 2 }, null).dustDepth).toBe(0);
  });

  it("scales a step's transmission as a depth: e^-s tau, so T at strength s is T^s", () => {
    // composeStep's depth is the march's dust depth uniform times the published one: a strength s is tau x s.
    const one = composeStep(5, -5, 10, 0.3, 0.1, 2.0, 0.05, 0.02, 4.0).transmitted;
    const half = composeStep(5, -5, 10, 0.3, 0.1, 2.0 * 0.5, 0.05, 0.02, 4.0 * 0.5).transmitted;
    expect(half).toBeCloseTo(Math.sqrt(one), 12);
    expect(composeStep(5, -5, 10, 0.3, 0.1, 0, 0.05, 0.02, 0).transmitted).toBe(1); // strength 0: no extinction
  });

  it("multiplies each cloud's kappa in the region's table, and nothing else; at 1 writes nothing", () => {
    const clouds = {
      cloud_radius: [8], cloud_azimuth: [0], cloud_height: [0], cloud_size: [20], cloud_mass: [1], cloud_density_pdf_width: [1.4],
      cloud_density_gradient: [0], cloud_gradient_angle: [0], cloud_cluster_index: [-1], cell: [300], index: [0], cloud_dust_extinction_v: [1.9],
    };
    const clusters = {
      cluster_radius: [7], cluster_azimuth: [0], cluster_height: [0], hii_stromgren_radius: [30], hii_halpha_emissivity: [1e-20],
      bubble_radius: [40], bubble_shell_thickness: [5], bubble_shell_emissivity: [2e-21], cell: [300], index: [0],
    };
    const table = packObjects(clouds, clusters);
    const copy = Float32Array.from(table.data);
    expect(scaleCloudDepths(copy, table.count, 1)).toBe(copy);
    expect(Array.from(copy)).toEqual(Array.from(table.data)); // at 1, untouched to the bit
    scaleCloudDepths(copy, table.count, 0.5);
    for (let k = 0; k < table.count; k += 1) {
      const o = k * OBJECT_FLOATS;
      for (let j = 0; j < OBJECT_FLOATS; j += 1) {
        const scaled = Math.floor(table.data[o + 4] + 0.5) === KIND.cloud && j === 10;
        expect(copy[o + j]).toBe(scaled ? Math.fround(table.data[o + j] * 0.5) : table.data[o + j]);
      }
    }
    // the march's T and the field's factor through the scaled table are the whole ray's at half the depth
    const eye: [number, number, number] = [8, 1, 0];
    const down: [number, number, number] = [0, -1, 0];
    const t1 = marchTransmission(eye, down, table.data, table.count, [1, 1, 1], 1, null).trans[0];
    const tHalf = marchTransmission(eye, down, copy, table.count, [1, 1, 1], 1, null).trans[0];
    expect(tHalf).toBeCloseTo(Math.sqrt(t1), 6);
    expect(-Math.log(t1) * MAG_PER_TAU).toBeGreaterThan(1.9); // the axis column, 1.5 x the mean
    const f0 = marchFieldTransmission(eye, down, scaleCloudDepths(Float32Array.from(table.data), table.count, 0), table.count, [1, 1, 1], 1, null, 0.3);
    expect(f0).toEqual([1, 1, 1]); // strength 0: the field undimmed
  });

  it("multiplies the dust to each point in the points' shader, at 1 by one", () => {
    expect(FLUX_POINTS_SHADER.vertex).toContain("uniform float dustDepthScale;");
    expect(FLUX_POINTS_SHADER.vertex).toContain("return tau * dustDepthScale;");
  });
});
