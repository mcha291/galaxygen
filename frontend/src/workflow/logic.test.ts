import { describe, expect, it } from "vitest";

import { type InputDecl, drawSeed, formatNumber, formatPower, fromSlider, isLog, runHash, toSlider } from "./logic";

const halo: InputDecl = { name: "halo_mass", label: "", kind: "control", about: "", checkpoint: 1, default: 1.1e12, lo: 1e11, hi: 1e13 };
const spin: InputDecl = { name: "disc_spin", label: "", kind: "control", about: "", checkpoint: 1, default: 0.0173, lo: 0.005, hi: 0.05 };

describe("drawSeed", () => {
  it("is a non-negative integer", () => {
    expect(drawSeed(() => 0)).toBe(0);
    const s = drawSeed(() => 0.999999);
    expect(Number.isInteger(s) && s >= 0 && s < 2 ** 31).toBe(true);
  });
});

describe("sliders", () => {
  it("drags two decades in log space and one in linear", () => {
    expect(isLog(halo)).toBe(true);
    expect(isLog(spin)).toBe(false);
    expect(fromSlider(halo, 500)).toBeCloseTo(1e12, -8);
    expect(fromSlider(spin, 500)).toBeCloseTo(0.0275, 6);
  });

  it("round-trips the default and pins the ends to the published bounds", () => {
    expect(fromSlider(halo, toSlider(halo, 1.1e12)) / 1.1e12).toBeCloseTo(1, 2);
    expect(fromSlider(halo, 0)).toBe(1e11);
    expect(fromSlider(halo, 1000)).toBe(1e13);
  });
});

describe("runHash", () => {
  it("is six hex digits, independent of key order, and moves with any input", () => {
    const a = runHash({ model: "simple", halo_mass: 1.1e12, world_seed: 0 });
    expect(a).toMatch(/^[0-9a-f]{6}$/);
    expect(runHash({ world_seed: 0, halo_mass: 1.1e12, model: "simple" })).toBe(a);
    expect(runHash({ model: "simple", halo_mass: 1.1e12, world_seed: 1 })).not.toBe(a);
  });
});

describe("formatPower", () => {
  it("writes decades as bare powers, and small ones plainly", () => {
    expect(formatPower(1e12)).toBe("10¹²");
    expect(formatPower(1e-5)).toBe("10⁻⁵");
    expect(formatPower(100)).toBe("100");
  });
});

describe("formatNumber", () => {
  it("writes large and small magnitudes as powers of ten", () => {
    expect(formatNumber(1.1e12)).toBe("1.10 × 10¹²");
    expect(formatNumber(2.5e-4)).toBe("2.50 × 10⁻⁴");
  });

  it("uses a real minus sign", () => {
    expect(formatNumber(-0.04861)).toBe("−0.0486");
  });

  it("leaves ordinary numbers plain", () => {
    expect(formatNumber(0.0173)).toBe("0.0173");
    expect(formatNumber(7)).toBe("7");
  });
});
