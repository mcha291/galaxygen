// S95 (Audit VI F-3B-9, register #114's call site): the region regime's cluster points are coloured by each cluster's
// own band response through the filter set over the white point's (colors.responseColors, S91 T2 / #114) - not by a
// blackbody share of its bolometric light, which painted the census 1.89 / 2.12 / 2.43 times its R / G / B light.
// colors.test.ts holds responseColors' arithmetic; nothing held the CALL: GalaxyTab computes clusterColors inline in a
// useMemo, which no test can reach without moving the choice into a pure function (a non-test edit, not this lane's).
// So this reads the source, as tests/test_ordered_products.py does for the model: the clusterColors memo calls
// responseColors on the clusters' response and the white point's, calls no other colouring, and is what the cluster
// layer draws. A return to a blackbody painting fails it.
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./GalaxyTab.tsx", import.meta.url), "utf-8");

function memoBody(name: string): string {
  const start = source.indexOf(`const ${name} = useMemo(`);
  expect(start).toBeGreaterThan(0);
  const end = source.indexOf("}, [", start); // the memo's closing line, its dependency list
  expect(end).toBeGreaterThan(start);
  return source.slice(start, end);
}

describe("the region regime's cluster colours (#114's call site)", () => {
  it("are the clusters' own band response over the white point's, through responseColors", () => {
    const body = memoBody("clusterColors");
    expect(body).toMatch(/responseColors\(\s*c\.response\s*,\s*shownClusters\.header\.white\?\.response\b/);
  });

  it("call no other colouring - no blackbody, light or star colours", () => {
    const body = memoBody("clusterColors");
    for (const other of ["lightColors(", "starColors(", "photometricColors(", "colorsFor(", "blackbody", "Blackbody"]) {
      expect(body.includes(other), other).toBe(false);
    }
  });

  it("are what the cluster layer draws", () => {
    expect(source).toMatch(/layers\.push\(\{\s*positions:\s*clusterPositions,\s*colors:\s*clusterColors\b/);
  });
});
