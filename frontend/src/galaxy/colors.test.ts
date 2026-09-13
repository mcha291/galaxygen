import { describe, expect, it } from "vitest";

import { srgbToLinear } from "./colors";

describe("srgbToLinear", () => {
  it("keeps the endpoints", () => {
    expect(srgbToLinear(0)).toBe(0);
    expect(srgbToLinear(1)).toBeCloseTo(1, 12);
  });

  it("darkens the middle: sRGB 0.5 is about 21% linear light", () => {
    expect(srgbToLinear(0.5)).toBeCloseTo(0.214, 3);
  });
});
