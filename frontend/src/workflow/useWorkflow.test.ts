import { describe, expect, it } from "vitest";

import { DEFAULT_MODEL } from "./useWorkflow";

describe("the viewer's starting model", () => {
  it("is the azimuthal model, the API's and the tests' default since S46 (D197)", () => {
    expect(DEFAULT_MODEL).toBe("azimuthal");
  });
});
