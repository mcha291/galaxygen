import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

import { fieldFragment } from "./FieldVolume";
import { FLUX_POINTS_SHADER } from "./FluxPoints";
import { SLAB_PIECES } from "./regimes";
import regimesSource from "./regimes.ts?raw";

// S64 review (N10): the field's fragment is pinned whole (tuning.test.ts); the points' shader - FluxPoints' dustTo,
// its copy of slabColumn, the Plummer and disc profiles - was pinned by nothing, and nothing held the TS twin of the
// march's step (regimes.ts composeStep, slabColumn) to the GLSL. The pin follows tuning.test.ts and region.test.ts:
// a change to the points' shader is a change to this file, made knowingly.

// S67's text (D227 R1): the instrument's image of a point - hstPsf.ts psfCorner and psfRect in both shaders, mode 3 in
// the vertex (the box at psfHalf, the per-channel normaliser) and its pixel's share in the fragment. Was S64's, hashed
// when the review's pin was added: vertex 6291 c47e7aaa901faee00621c8ff2bfd9088323ba616ab153f49c632e895facffed3,
// fragment 1269 0d28a2c493d5c139e316146d4c56723e685160e8fdff305da479e3f844fd602f (LF line ends).
const VERTEX_LENGTH = 8207;
const VERTEX_SHA256 = "ca2da355803635aa0cd5ff548b49a56afea4f61cfcf6a38ee6cd1fcf168f5864";
const FRAGMENT_LENGTH = 2410;
const FRAGMENT_SHA256 = "e8f58add7f895054ffb63159f5754d6d6f4ea6fdac6071e1d868ba5174cbd3da";

const sha256 = (text: string) => createHash("sha256").update(text.replace(/\r\n/g, "\n"), "utf-8").digest("hex");

describe("the points' shader (FluxPoints, S64)", () => {
  it("is the text S67 left, byte for byte", () => {
    expect(FLUX_POINTS_SHADER.vertex.length).toBe(VERTEX_LENGTH);
    expect(sha256(FLUX_POINTS_SHADER.vertex)).toBe(VERTEX_SHA256);
    expect(FLUX_POINTS_SHADER.fragment.length).toBe(FRAGMENT_LENGTH);
    expect(sha256(FLUX_POINTS_SHADER.fragment)).toBe(FRAGMENT_SHA256);
    // what the pin covers, named: the dust to each point, the slab's column in it, the two profiles
    expect(FLUX_POINTS_SHADER.vertex).toContain("vec3 dustTo(vec3 p) {");
    expect(FLUX_POINTS_SHADER.vertex).toContain("float slabColumn(float y0, float y1, float lo, float hi, float ds) {");
    expect(FLUX_POINTS_SHADER.vertex).toContain("plummerRect(");
    // S67: the PSF table's reader in both, and the physical mode's switch.
    for (const text of [FLUX_POINTS_SHADER.vertex, FLUX_POINTS_SHADER.fragment]) expect(text).toContain("vec3 psfRect(vec2 lo, vec2 hi) {");
    expect(FLUX_POINTS_SHADER.vertex).toContain("if (mode < 0.5 && physOn > 0.5) {");
  });
});

// The twin pin (region.test.ts / regionDepth.test.ts's pattern: the same expressions in the shader text and the TS
// source). Each GLSL expression line is put in the TS's words - abs/min/max as Math's, a float literal n.0 as n,
// float(i) as i, the field fragment's names as composeStep's - and compared with regimes.ts's source with the
// declarations (const, let), the parentheses and the whitespace taken out of both: the operators and operands in
// order, which is what "line for line" claims (prettier's added parentheses are not a difference).
const SLAB_BODY = /float slabColumn\(float y0, float y1, float lo, float hi, float ds\) \{\n([\s\S]*?)\n {2}\}\n/;
const RENAMES: [RegExp, string][] = [
  [/\bsgn\b/g, "sign"],
  [/\bslab\.x\b/g, "slabMid"],
  [/\bslab\.y\b/g, "slabHalf"],
  [/\btauC\b/g, "tauClouds"],
  [/\bpiece\b/g, "ds"],
];
const toTs = (glsl: string, renames: [RegExp, string][] = []) => {
  let s = glsl.replace(/\b(abs|min|max|exp)\(/g, "Math.$1(").replace(/\bfloat\((\w+)\)/g, "$1").replace(/(\d+)\.0(?!\d)/g, "$1");
  s = s.replace(/^\s*(float|vec2|vec3|bool|int)\s+/, "");
  for (const [from, to] of renames) s = s.replace(from, to);
  return squeeze(s);
};
const squeeze = (s: string) => s.replace(/\b(const|let)\s+/g, "").replace(/[()\s]/g, "");
const tsSource = squeeze(regimesSource.replace(/\bSLAB_PIECES\b/g, String(SLAB_PIECES)));

describe("the march's slab: the shader text and the TS twin carry the same expressions (S64)", () => {
  it("slabColumn: both GLSL copies are one text, and every line of it but the guard is regimes.ts's", () => {
    const points = SLAB_BODY.exec(FLUX_POINTS_SHADER.vertex)?.[1];
    const field = SLAB_BODY.exec(fieldFragment())?.[1];
    expect(points).toBeDefined();
    expect(points).toBe(field);
    const lines = points!.split("\n").map((l) => l.trim()).filter((l) => l !== "}" && l !== "");
    expect(lines).toHaveLength(8);
    // The guard is the one stated difference: the TS refuses a NaN thickness too (!(thick > 0)), the GLSL a
    // non-positive one; both return no column.
    const guard = "if (thick <= 0.0) return 0.0;";
    expect(lines).toContain(guard);
    expect(regimesSource).toContain("if (!(thick > 0)) return 0;");
    for (const line of lines.filter((l) => l !== guard)) expect(tsSource, line).toContain(toTs(line));
    // and the comparison sees a difference: the slab's two edges swapped in the overlap is not regimes.ts's
    expect(tsSource).not.toContain(toTs("float overlap = max(0.0, min(max(y0, y1), lo) - max(min(y0, y1), hi));"));
  });

  it("composeStep: the field fragment's slab lines are regimes.ts's", () => {
    const fragment = fieldFragment();
    const lines = [
      "float lo = sgn * slab.x - slab.y;",
      "float hi = sgn * slab.x + slab.y;",
      "float hMin = (dusty && clouds) ? min(hDust, slab.y) : (dusty ? hDust : (clouds ? slab.y : 0.0));",
      `float ns = (clouds && ps <= ${SLAB_PIECES}) ? lo + (hi - lo) * float(ps) / ${SLAB_PIECES}.0 : 1.0e9;`,
      "b = min(u1, min(nd, ns));",
      "share = (b - a) / du;",
    ];
    for (const line of lines) {
      expect(fragment, line).toContain(line);
      expect(tsSource, line).toContain(toTs(line, RENAMES));
    }
    // the slab's term in the step's depth: the clouds' own column in the piece
    const term = "(clouds ? tauC * slabColumn(a, b, lo, hi, piece)";
    expect(fragment).toContain(term);
    expect(tsSource).toContain(toTs(term, RENAMES));
  });
});

