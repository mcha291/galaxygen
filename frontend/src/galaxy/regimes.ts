// The field regime (design brief §3, RENDER_PLAN R3/R4/M4): the galaxy's light as a
// volume the renderer integrates along each line of sight. No three.js here.
//
// Everything in the volume is published. In the plane: the disc's surface brightness,
// the colour of that light, its Hα, and the dust's face-on extinction, each times the
// (R, φ) pattern contrast. Out of the plane: the thin disc's sech² scale height for the
// old light, and a thinner layer for the young light, the line and the dust. In the
// middle: the Hernquist bulge. The viewer lays these out as polar textures and a few
// numbers and marches rays through them, adding light and taking away what the dust in
// front absorbs. How the published values are placed within each ring (young light in the
// arms, dust on their inner edge, clumps and knots along them) is the viewer's, and every
// ring keeps its published mean.

import type { Axis } from "../preview/axes";

/**
 * Linear sRGB of an HII region's light: Hα 656.3 nm and Hβ 486.1 nm at the case-B ratio
 * 2.86 : 1, through the same CIE 1931 fit and XYZ-to-sRGB matrix as the blackbody cmap
 * (galaxy/core/cmaps.py), brightest channel at 1. Computed there once and copied here,
 * because a line colour is not a field and has no ramp.
 * [recall: Osterbrock & Ferland 2006, case B Hα/Hβ = 2.86 at 10⁴ K]
 */
export const HII_RGB = [1.0, 0.1607, 0.5032] as const;

/**
 * The line's weight against the starlight in the viewer's channels. Starlight is drawn at
 * its bolometric luminosity, of which a population puts roughly a fifth into the red
 * channel; the line puts all of its light there. A display correction of that mismatch,
 * not a measured ratio.
 */
export const LINE_CHANNEL_WEIGHT = 5;

/**
 * How much harder the line crowds into the arms than the starlight: the contrast raised to
 * this power, renormalised around each ring so the ring still carries its published Hα.
 * Star formation goes as gas density to the Kennicutt–Schmidt power and the arms are where
 * the gas is; the exponent is a display choice standing in for that, not a derivation.
 */
export const LINE_CLUMP = 3;

/**
 * The share of each ring's starlight drawn as young light crowded into the arms, the rest
 * following the published contrast as the old disc does. The ring's light and its mean colour
 * stay as published; what changes is where in the ring the blue light sits. In a star-forming
 * disc the arms are a contrast in colour more than in mass: OB stars and their HII regions
 * live and die inside them. A display choice, not a population synthesis.
 */
export const YOUNG_SHARE = 0.3;

/** How hard the young light crowds into the arms: between the old stars (1) and the line (LINE_CLUMP). */
export const YOUNG_CLUMP = 2;

/**
 * The colour temperature the young light is drawn at, K: a population a few tens of Myr old,
 * dominated by B stars [recall]. A display choice read through the published temperature ramp.
 */
export const YOUNG_KELVIN = 12000;

/** However blue the young light, the old light keeps at least this share of each channel's published colour. */
const OLD_COLOUR_FLOOR = 0.2;

/**
 * How hard the dust crowds into the arms: as the gas and the line do. Renormalised around each
 * ring, so the ring keeps its published face-on A_V.
 */
export const DUST_CLUMP = 3;

/**
 * How far inside each arm's ridge the dust lane lies, as a share of the radial spacing between
 * arms. Gas overtakes the pattern inside corotation and shocks on the arm's concave edge, so the
 * lanes run along the inner side of the starlight [recall: Roberts 1969]. A display choice.
 */
export const DUST_LEAD = 0.12;

/** Optical depth per magnitude: τ = A / 1.086. */
export const TAU_PER_MAG = 1 / 1.086;


export interface PlaneFields {
  R: Axis;
  /** Surface brightness per R cell, L☉/pc². */
  brightness: ArrayLike<number>;
  /** Linear RGB of the light per R cell, three per cell; non-finite means no light is drawn there. */
  colour: ArrayLike<number>;
  /** Hα surface brightness per R cell, L☉/pc². */
  halpha?: ArrayLike<number>;
  /** Face-on A_V per R cell. */
  extinction?: ArrayLike<number>;
  /** The (R, φ) contrast, row-major over (R, φ), when the model publishes one. */
  contrast?: { values: ArrayLike<number>; phi: Axis };
  /** Linear RGB of the young light, YOUNG_KELVIN through the same ramp as `colour`. Without it all the light is old. */
  young?: readonly number[];
  /** The published arm geometry, which places the dust lanes; without it the dust sits on the ridge. */
  arms?: { pitchDeg: number; multiplicity: number };
  /** Seeds the clumps laid along the arms; without it, or without `arms`, the rings are smooth. */
  seed?: number;
}

/**
 * The clumps: seeded noise that breaks the smooth rings into star clouds, HII knots and feathered
 * dust, laid out along the arms. A multiplicative factor on each midplane component, evaluated by
 * the shader at every sample (a texture of them could not hold a clump smaller than its cells) and
 * renormalised around every ring by a factor computed here, so no ring's published value moves.
 * Everything here is a display choice.
 */
export const CLUMPS = {
  /** Lattice cells around the arm phase ψ: sets a clump's width across the arm, 2πR sin p / cells. */
  cells: 64,
  /** How much longer a clump runs along the arm than across it. */
  aspect: 2,
  /**
   * Log-normal widths: the young light and the dust. Kept below the arms' own contrast, or the
   * clumps hide the arms they sit in. The old disc is smooth.
   */
  sigma: { young: 0.35, dust: 0.3 },
  /**
   * The line is not spread through the clumps but gathered into knots: HII regions are discrete,
   * a few hundred parsecs across at most, lit by the few clusters young enough to ionise them.
   * Only the young light's noise above this many standard deviations carries line, weighted by
   * its excess up to `knotCap`, so each ring's Hα sits in under 2% of its area, a typical knot
   * some sixty times the ring's mean and the brightest a hundred: about the share of a
   * star-forming disc HII regions cover [recall]. At 1.5σ the knots took 7% of the area at six
   * times the mean, a pink wash rather than knots. They sit in the young light's own clumps,
   * where the clusters are.
   */
  knotThreshold: 2.0,
  /**
   * The excess, in standard deviations, beyond which a knot is no brighter. HII regions have a
   * ceiling: the squared excess put the brightest thousands of times over the ring's mean, and a
   * few such pixels were bright enough for the bloom to wash the whole view white.
   */
  knotCap: 0.3,
  /**
   * The radius, kpc, inside which the clumps fade out, as 1 − exp(−(R/fade)²). A clump's size goes
   * as R, so near the centre they shrink to a grain; and the inner disc is old light, not star clouds.
   */
  fade: 2,
  /** Added to the seed for the dust's own lattice, so dust and star clouds are not the same clumps. */
  dustSeedOffset: 7919,
};

/**
 * One lattice of arm-aligned noise: the cells per turn of φ across (n) and along (m) the arms, the
 * pitch, the seed, and the mean and spread that normalise it. Everything the shader needs to draw
 * the same noise as `clumpNoise`.
 */
export interface ClumpLattice {
  n: number;
  m: number;
  cot: number;
  tan: number;
  seed: number;
  mean: number;
  std: number;
}

/** Added to every along-arm lattice index, keeping it positive; the shader adds the same. */
export const LATTICE_LIFT = 65536;

// A lattice value in [−1, 1] per integer cell and seed: a 32-bit integer hash, no state. The
// shader's `lattice` is this line for line in uint arithmetic; Math.imul is the same wrap.
function latticeValue(x: number, y: number, seed: number): number {
  let h = Math.imul(x, 0x27d4eb2d) ^ Math.imul(y, 0x165667b1) ^ Math.imul(seed, 0x9e3779b1);
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  return (h >>> 0) / 0x7fffffff - 1;
}

// Smooth value noise on a lattice that repeats under the shift (n, m): cell (x, y) is cell
// (x + n, y + m). One turn of φ is that shift, so the noise wraps around the ring without a seam.
function valueNoise(x: number, y: number, n: number, m: number, seed: number): number {
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const fx = x - x0;
  const fy = y - y0;
  const sx = fx * fx * (3 - 2 * fx);
  const sy = fy * fy * (3 - 2 * fy);
  // Brought into the first turn, and lifted by LATTICE_LIFT so no index is negative: GLSL ES 3.00
  // does not promise a negative int keeps its bits on the way to uint.
  const value = (cx: number, cy: number) => {
    const turns = Math.floor(cx / n);
    return latticeValue(cx - turns * n, cy - turns * m + LATTICE_LIFT, seed);
  };
  const a = value(x0, y0);
  const b = value(x0 + 1, y0);
  const c = value(x0, y0 + 1);
  const d = value(x0 + 1, y0 + 1);
  return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
}

// Two octaves, before normalising.
function rawNoise(l: Omit<ClumpLattice, "mean" | "std">, lnR: number, angle: number): number {
  // In cells: ψ over a turn gives n; (ln R tan p + φ) over a turn gives m.
  const x = ((angle - l.cot * lnR) * l.n) / (2 * Math.PI);
  const y = ((lnR * l.tan + angle) * l.m) / (2 * Math.PI);
  return 0.7 * valueNoise(x, y, l.n, l.m, l.seed) + 0.3 * valueNoise(2 * x, 2 * y, 2 * l.n, 2 * l.m, l.seed + 1);
}

/**
 * Noise over (R, φ) on a lattice square to the arms. In (ln R, φ) lengths go as R times the flat
 * distance, so a lattice there is a true local grid at every radius; the arm of pitch p runs along
 * (sin p, cos p) in it, and the lattice's axes are that direction and the one across it. Across is
 * the arm phase ψ = φ − cot p ln R (pattern.py's convention) times sin p; along is
 * ln R sin p + φ cos p. A clump is then an ellipse CLUMPS.aspect times longer than it is wide,
 * R · 2π sin p / cells across. One turn of φ moves both coordinates by whole cells (the along count
 * is rounded to make it so), which is what lets the lattice wrap without a seam. Normalised to
 * zero mean and unit spread over the (R, φ) grid given.
 */
export function clumpLattice(R: Axis, phi: Axis, pitchDeg: number, seed: number): ClumpLattice {
  const p = (Math.min(Math.max(pitchDeg, 1), 89) * Math.PI) / 180;
  const cot = 1 / Math.tan(p);
  const n = CLUMPS.cells;
  const base = { n, m: Math.max(1, Math.round((n * cot) / CLUMPS.aspect)), cot, tan: Math.tan(p), seed };
  let sum = 0;
  let sum2 = 0;
  for (let i = 0; i < R.n; i += 1) {
    const lnR = Math.log(Math.max(R.lo + (i + 0.5) * R.width, 1e-3));
    for (let j = 0; j < phi.n; j += 1) {
      const v = rawNoise(base, lnR, phi.lo + (j + 0.5) * phi.width);
      sum += v;
      sum2 += v * v;
    }
  }
  const count = R.n * phi.n;
  const mean = sum / count;
  return { ...base, mean, std: Math.sqrt(Math.max(sum2 / count - mean * mean, 1e-12)) };
}

/** The normalised noise at radius `radius` (kpc) and azimuth `angle`. */
export function clumpNoise(l: ClumpLattice, radius: number, angle: number): number {
  return (rawNoise(l, Math.log(Math.max(radius, 1e-3)), angle) - l.mean) / l.std;
}

/** A lattice's noise at every texel centre of an (R, φ) grid, row-major over (R, φ). */
function noiseGrid(l: ClumpLattice, R: Axis, phi: Axis): Float64Array {
  const out = new Float64Array(R.n * phi.n);
  for (let i = 0; i < R.n; i += 1) {
    const radius = R.lo + (i + 0.5) * R.width;
    for (let j = 0; j < phi.n; j += 1) out[i * phi.n + j] = clumpNoise(l, radius, phi.lo + (j + 0.5) * phi.width);
  }
  return out;
}

/** The noise at every texel centre of an (R, φ) grid, row-major over (R, φ). */
export function armNoise(R: Axis, phi: Axis, pitchDeg: number, seed: number): Float64Array {
  return noiseGrid(clumpLattice(R, phi, pitchDeg, seed), R, phi);
}

/** How strongly the clumps show at a radius: faded out toward the centre. */
export function clumpStrength(radius: number): number {
  return 1 - Math.exp(-((radius / CLUMPS.fade) ** 2));
}

const knotExcess = (n: number) => Math.min(Math.max(0, n - CLUMPS.knotThreshold), CLUMPS.knotCap);

/** The least share of a ring's line its knots must carry for the ring to be drawn knotted. */
const KNOT_MIN_SHARE = 0.25;

/**
 * The clump factors at one point, before each ring's renormalisation: the young light's, the
 * line's and the dust's, from the star noise `n` and the dust noise `nd` at clump strength `s`.
 * The shader's `clumpFactors` is this, line for line.
 */
export function clumpFactors(n: number, nd: number, s: number, knotMean: number): [number, number, number] {
  return [
    Math.exp(CLUMPS.sigma.young * s * n),
    knotMean > 0 ? 1 - s + (s * knotExcess(n)) / knotMean : 1,
    Math.exp(CLUMPS.sigma.dust * s * nd),
  ];
}

export interface PlaneTexture {
  /** The old disc, in the thin disc's height: RGB its light through a face-on column (L☉/pc², linear colour). */
  data: Float32Array;
  /**
   * The midplane layer, smooth: R the young light (L☉/pc², drawn in the young colour), G the line
   * (L☉/pc² times LINE_CHANNEL_WEIGHT, drawn in HII_RGB), B the dust's face-on optical depth in V.
   */
  layer: Float32Array;
  /**
   * Per ring, one texel per R cell: what multiplies each clump factor so the ring keeps its mean.
   * R the young light's, G the line's, B the dust's; A is 1 where the line gathers into knots and
   * 0 in a ring no knot crosses, where the line stays smooth.
   */
  norms: Float32Array;
  /** The star clouds' and the dust's lattices and the knots' mean weight; null when the rings are smooth. */
  clumps: { stars: ClumpLattice; dust: ClumpLattice; knotMean: number } | null;
  width: number;
  height: number;
}

/**
 * Three RGBA float textures from the published fields, one texel per (R cell, φ cell), row-major
 * with φ as the row, and one per R cell for the rings' clump norms. Split by the layer the light
 * lives in, so the renderer can give each its own thickness: the old disc fills the thin disc, and
 * the young light, the line and the dust lie in a far thinner layer at the midplane. Without a
 * contrast the disc is axisymmetric and one φ row serves.
 *
 * Around each ring the light, its colour, the line and the dust all average to their published
 * values; only their placement in azimuth is the viewer's. The old light follows the contrast,
 * the young light and the line crowd harder into the arms, and the dust crowds in as hard as the
 * line but on the arms' inner edge. With a seed, the midplane layer is broken into clumps along
 * the arms and the line into knots, by `clumpFactors` and `norms`.
 */
export function planeTexture(fields: PlaneFields): PlaneTexture {
  const { R, brightness, colour, halpha, extinction, contrast, young, arms, seed } = fields;
  const nPhi = contrast ? contrast.phi.n : 1;
  const data = new Float32Array(R.n * nPhi * 4);
  const layer = new Float32Array(R.n * nPhi * 4);
  const norms = new Float32Array(R.n * 4);
  const at = (i: number, j: number) => (contrast ? Math.max(0, Number(contrast.values[i * contrast.phi.n + j])) : 1);
  // The contrast at a radius between cells, clamped to the grid.
  const atRadius = (radius: number, j: number) => {
    const x = Math.min(R.n - 1, Math.max(0, (radius - R.lo) / R.width - 0.5));
    const i0 = Math.floor(x);
    const i1 = Math.min(R.n - 1, i0 + 1);
    return at(i0, j) + (at(i1, j) - at(i0, j)) * (x - i0);
  };
  // A logarithmic spiral's arms are 2πR tan p / m apart along a radius.
  const lead = arms && contrast && Number.isFinite(arms.pitchDeg) && arms.multiplicity > 0
    ? DUST_LEAD * 2 * Math.PI * Math.tan((arms.pitchDeg * Math.PI) / 180) / arms.multiplicity
    : 0;

  // Star clouds (the young light and its knots) and dust clumps from two lattices.
  let clumps: PlaneTexture["clumps"] = null;
  let starNoise: Float64Array | null = null;
  let dustNoise: Float64Array | null = null;
  if (contrast && arms && seed !== undefined && Number.isFinite(arms.pitchDeg)) {
    const stars = clumpLattice(R, contrast.phi, arms.pitchDeg, seed);
    const dust = clumpLattice(R, contrast.phi, arms.pitchDeg, seed + CLUMPS.dustSeedOffset);
    starNoise = noiseGrid(stars, R, contrast.phi);
    dustNoise = noiseGrid(dust, R, contrast.phi);
    let knotMean = 0;
    for (let k = 0; k < starNoise.length; k += 1) knotMean += knotExcess(starNoise[k]);
    clumps = { stars, dust, knotMean: knotMean / starNoise.length };
  }

  const youngC = new Float64Array(nPhi);
  const lineC = new Float64Array(nPhi);
  const dustC = new Float64Array(nPhi);
  for (let i = 0; i < R.n; i += 1) {
    const light = Number(brightness[i]);
    const [r, g, b] = [Number(colour[3 * i]), Number(colour[3 * i + 1]), Number(colour[3 * i + 2])];
    const lit = light > 0 && Number.isFinite(r) && Number.isFinite(g) && Number.isFinite(b);
    const line = halpha ? Math.max(0, Number(halpha[i]) || 0) * LINE_CHANNEL_WEIGHT : 0;
    const av = extinction ? Math.max(0, Number(extinction[i]) || 0) : 0;

    // The young share, cut where the old light would need a negative colour to keep the
    // ring's mean at the published one; the old colour is what is left of it.
    let share = young && lit && contrast ? YOUNG_SHARE : 0;
    const pub = [r, g, b];
    if (share > 0) for (let k = 0; k < 3; k += 1) if (young![k] > 0) share = Math.min(share, ((1 - OLD_COLOUR_FLOOR) * pub[k]) / young![k]);
    const old = pub.map((v, k) => (share > 0 ? (v - share * young![k]) / (1 - share) : v));

    // Each component's smooth shape around the ring, renormalised so its ring mean is the
    // contrast's (for the young stars, as for the old) or 1 (for the line and the dust, which
    // carry their own published values).
    const radius = R.lo + (i + 0.5) * R.width;
    let meanC = 0;
    let meanYoung = 0;
    let meanLine = 0;
    let meanDust = 0;
    for (let j = 0; j < nPhi; j += 1) {
      const c = at(i, j);
      youngC[j] = c ** YOUNG_CLUMP;
      lineC[j] = c ** LINE_CLUMP;
      dustC[j] = atRadius(radius + lead * radius, j) ** DUST_CLUMP;
      meanC += c;
      meanYoung += youngC[j];
      meanLine += lineC[j];
      meanDust += dustC[j];
    }
    meanC = meanC / nPhi || 1;
    meanYoung = meanYoung / nPhi || 1;
    meanLine = meanLine / nPhi || 1;
    meanDust = meanDust / nPhi || 1;

    // The clump factors' own mean around the ring, weighted by each smooth shape: dividing by it
    // gives the ring back its mean.
    const p = 4 * i;
    norms[p] = norms[p + 1] = norms[p + 2] = 1;
    norms[p + 3] = 0;
    if (clumps && starNoise && dustNoise) {
      const s = clumpStrength(radius);
      let young0 = 0;
      let young1 = 0;
      let line0 = 0;
      let line1 = 0;
      let knotted = 0;
      let dust0 = 0;
      let dust1 = 0;
      for (let j = 0; j < nPhi; j += 1) {
        const [fy, fl, fd] = clumpFactors(starNoise[i * nPhi + j], dustNoise[i * nPhi + j], s, clumps.knotMean);
        young0 += youngC[j];
        young1 += youngC[j] * fy;
        line0 += lineC[j];
        line1 += lineC[j] * fl;
        knotted += (lineC[j] * s * knotExcess(starNoise[i * nPhi + j])) / clumps.knotMean;
        dust0 += dustC[j];
        dust1 += dustC[j] * fd;
      }
      if (young1 > 0) norms[p] = young0 / young1;
      if (dust1 > 0) norms[p + 2] = dust0 / dust1;
      // A ring whose knots would carry under a quarter of its line keeps the line spread with the
      // arms. Renormalising it instead divides by the few knots it has, or by the smooth 1 − s
      // alone, which near full strength is nearly nothing: the norm then runs to thousands, and a
      // knot the shader finds between this ring's texels is drawn thousands of times too bright.
      if (line1 > 0 && knotted >= KNOT_MIN_SHARE * line0) {
        norms[p + 1] = line0 / line1;
        norms[p + 3] = 1;
      }
    }

    for (let j = 0; j < nPhi; j += 1) {
      const q = (j * R.n + i) * 4;
      const c = at(i, j);
      const oldLight = lit ? (1 - share) * light * c : 0;
      for (let k = 0; k < 3; k += 1) data[q + k] = old[k] * oldLight;
      layer[q] = share > 0 ? (share * light * meanC * youngC[j]) / meanYoung : 0;
      layer[q + 1] = (line * lineC[j]) / meanLine;
      layer[q + 2] = contrast ? (av * TAU_PER_MAG * dustC[j]) / meanDust : av * TAU_PER_MAG;
    }
  }
  return { data, layer, norms, clumps, width: R.n, height: nPhi };
}

/**
 * The midplane layer at one texel with its clumps applied, as the shader draws it at that point:
 * the young light, the line and the dust. For checking the ring means; the renderer does this per
 * sample, not per texel.
 */
export function clumpedLayer(tex: PlaneTexture, R: Axis, phi: Axis, i: number, j: number): [number, number, number] {
  const q = (j * R.n + i) * 4;
  const [young, line, dust] = [tex.layer[q], tex.layer[q + 1], tex.layer[q + 2]];
  if (!tex.clumps) return [young, line, dust];
  const radius = R.lo + (i + 0.5) * R.width;
  const angle = phi.lo + (j + 0.5) * phi.width;
  const n = clumpNoise(tex.clumps.stars, radius, angle);
  const nd = clumpNoise(tex.clumps.dust, radius, angle);
  const [fy, fl, fd] = clumpFactors(n, nd, clumpStrength(radius), tex.clumps.knotMean);
  const k = 4 * i;
  return [young * fy * tex.norms[k], line * (tex.norms[k + 3] > 0 ? fl * tex.norms[k + 1] : 1), dust * fd * tex.norms[k + 2]];
}

/**
 * How visible each regime is at a view `across` kpc wide. The field is the whole galaxy and
 * never goes fully away (most stars stay unresolved at any zoom); the sample fades in as the
 * galaxy fills the view and out again when a region's own stars take over.
 */
export function regimeWeights(across: number): { field: number; sampled: number; stars: number; active: "field" | "sampled" | "stars" } {
  const ramp = (x: number, from: number, to: number) => Math.min(1, Math.max(0, (Math.log(from) - Math.log(x)) / (Math.log(from) - Math.log(to))));
  const stars = ramp(across, REGIME_KPC.stars, REGIME_KPC.stars / 2);
  const sampled = ramp(across, REGIME_KPC.field * 2, REGIME_KPC.field * 0.6) * (1 - stars);
  // Close up the region's own stars carry the light, so the field steps back to a faint glow of
  // what stays unresolved. Left at a third, the bulge's surface brightness — which does not fall
  // as the camera closes in — flooded a close view white and hid every star in it.
  const field = 1 - 0.7 * ramp(across, REGIME_KPC.field, REGIME_KPC.stars) - 0.27 * stars;
  const active = across >= REGIME_KPC.field ? "field" : across >= REGIME_KPC.stars ? "sampled" : "stars";
  return { field, sampled, stars, active };
}

/** The view widths, kpc, where the regimes hand over: the field above the first, a region's stars below the second. */
export const REGIME_KPC = { field: 25, stars: 4 };

export interface RegionWindow {
  r_min: number;
  r_max: number;
  phi_min: number;
  phi_max: number;
}

/**
 * The region a close view asks the catalogue for: a box `half` kpc around the orbit target,
 * as radius and azimuth bounds, snapped so small camera moves reuse a response. A window
 * that holds the centre or crosses φ = 0 asks for every azimuth.
 */
export function regionAround(x: number, z: number, half: number): RegionWindow {
  const snap = (v: number, step: number) => Math.round(v / step) * step;
  const h = 2 ** Math.ceil(Math.log2(Math.max(0.5, half)));
  const r0 = snap(Math.hypot(x, z), h / 2);
  const r_min = Math.max(0, r0 - h);
  const r_max = r0 + h;
  if (r0 <= h) return { r_min: 0, r_max, phi_min: 0, phi_max: 2 * Math.PI };
  let phi0 = Math.atan2(-z, x);
  if (phi0 < 0) phi0 += 2 * Math.PI;
  const dPhi = Math.min(Math.PI, Math.asin(Math.min(1, h / r0)) * 1.2);
  const step = Math.PI / 64;
  const phi_min = snap(phi0 - dPhi, step);
  const phi_max = snap(phi0 + dPhi, step);
  if (phi_min < 0 || phi_max > 2 * Math.PI) return { r_min, r_max, phi_min: 0, phi_max: 2 * Math.PI };
  return { r_min, r_max, phi_min, phi_max };
}

/** How many of the sample's stars fall inside a window: its share of the galaxy's stars, measured rather than guessed. */
export function starsInWindow(radius: ArrayLike<number>, azimuth: ArrayLike<number>, window: RegionWindow): number {
  let n = 0;
  for (let i = 0; i < radius.length; i += 1) {
    const r = radius[i];
    const a = azimuth[i];
    if (r >= window.r_min && r <= window.r_max && a >= window.phi_min && a <= window.phi_max) n += 1;
  }
  return n;
}

/**
 * The whole-galaxy sample size a region is materialised at, so that about `target` stars land
 * in it: the base sample scaled by the share of its stars the window already holds (the centre
 * is dense and the outskirts are not, so the share is counted, not taken from the area). A
 * power of two times the base, so it changes in steps and a nudge reuses a response.
 */
export function regionSampleSize(base: number, inWindow: number, target: number, max: number): number {
  const share = Math.max(inWindow, 1) / base;
  const scale = 2 ** Math.floor(Math.log2(Math.max(1, target / (share * base))));
  return Math.min(max, base * scale);
}
