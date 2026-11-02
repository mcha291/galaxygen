// three's shader checks (S80, #208 (c)): on in development and in the tests, off in a production build. The flag is
// Vite's `import.meta.env.PROD`, replaced at build time; under vitest the mode is "test", so the checks are on here.
// The production build's side - no getProgramInfoLog on the landing - is read in the built viewer (S80's report).
import { describe, expect, it } from "vitest";

import { SHADER_CHECKS } from "./renderer";

describe("three's shader checks (S80, #208 c)", () => {
  it("are on outside a production build, so a broken shader is said in development and in the tests", () => {
    expect(import.meta.env.PROD).toBe(false);
    expect(SHADER_CHECKS).toBe(true);
  });
});
