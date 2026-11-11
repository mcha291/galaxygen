// S95 (the review's C-1; Audit VI F-W-1, rule D1): brightTiles.test.ts holds shownTable and ofGalaxy in a hand-built
// chain; nothing held the CALL - GalaxyTab reverted to reading the bright table as the loader's raw `next` (the last
// galaxy's after a switch) left every test green. As clusterColors.test.ts does for #114, this reads GalaxyTab's source:
// the pick's table comes through shownTable on the table's own load and key, the loader tags each table with the key it
// was asked for, the remainder's threshold comes through ofGalaxy for the shown galaxy, and the old readings are gone.
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./GalaxyTab.tsx", import.meta.url), "utf-8");

describe("GalaxyTab reads the star-first pick's inputs for the shown galaxy only (F-W-1's call site)", () => {
  it("takes the bright table through shownTable, on the table's load and key", () => {
    expect(source).toMatch(/const\s+brightTable\s*=\s*shownTable\(\s*tableLoad\s*,\s*brightTableKey\s*\)/);
  });

  it("tags each table with the key it was asked for (what shownTable compares, C-2)", () => {
    expect(source).toMatch(/loadBrightTable\(\s*query\s*,\s*signal\s*\)\s*\.then\(\s*\(\s*table\s*\)\s*=>\s*\(\s*\{\s*\.\.\.table\s*,\s*key\s*:\s*brightTableKey\b/);
  });

  it("takes the remainder's threshold through ofGalaxy, for the shown galaxy's tiles", () => {
    expect(source).toMatch(/const\s+brightAsked\s*=\s*pointsOn\s*\?\s*ofGalaxy\(\s*brightLoad\.next\s*,\s*countsGalaxy\s*\)/);
    expect(source).toMatch(/\.then\(\s*\(\s*frame\s*\)\s*=>\s*\(\s*\{\s*\.\.\.frame\s*,\s*galaxy\s*:\s*countsGalaxy\s*\}\s*\)\s*\)/);
  });

  it("no longer reads either through the loaders' raw fallback (the old expressions)", () => {
    expect(source).not.toMatch(/=\s*tableLoad\.next\s*\?\?\s*null/);
    expect(source).not.toMatch(/brightLoad\.next\s*\?\s*brightLoad\.next\s*:\s*null/);
    expect(source).not.toMatch(/tableLoad\.(?:value|last)\b/);
  });
});
