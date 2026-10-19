// The field view's display choices as one object (D199, S47): what the march samples, how bright the
// field and the points are drawn, the bloom and the tone curve. None of it is physics (rule D5) and
// none of it places structure (RENDER_PHYSICS §8: the dither stays fixed by the pixel). The Tuning
// panel exposes each as a control, experimental, so the owner can find the combination to rule on;
// the defaults are the values the view drew with before the panel, so untouched it draws the same.
//
// The display constants live here, one copy: FieldVolume and GalaxyView import them. The ones with a
// home of their own (the white point in filters.json, the sub-sample bound the shader is compiled
// with, the close-zoom floor in regimes.ts) are imported from it; the field's 1/400 and the points'
// 100 L☉ stay where they are and are tuned by a multiplier of 1.

import { WHITE_KELVIN } from "./filters";
import { CLOUD_RASTER } from "./cloudOpacity";
import { CLOSE_FIELD_FLOOR, SUB_SAMPLES_MAX } from "./regimes";

/** Ray-march steps through the galaxy's bounding box. */
export const STEPS = 96;
/**
 * The most pixels the field is marched at, whatever the screen: the image is stretched onto the
 * canvas, and the field is smooth, so this loses nothing to see. The work per frame has to be
 * bounded by a number, not by the display. Marching every pixel of a 4K screen the galaxy fills,
 * at a device pixel ratio of 2, is a billion shader iterations a frame; that outlasts Windows'
 * two-second GPU watchdog, the driver resets, and the browser does not come back.
 */
export const PIXEL_BUDGET = 400_000;
/** And never more than half the drawing buffer's resolution on a side. */
export const MAX_RESOLUTION = 0.5;
/** R5, kept restrained: only light above unit intensity blooms, and not by much. */
export const BLOOM = { strength: 0.35, radius: 0.45, threshold: 1.0 };
/** The default sprite's size on screen, px: the PSF's wings need about this many for its core to stay near two. */
export const STAR_SPRITE_PX = 9;

export type ToneMapping = "agx" | "aces" | "reinhard" | "linear";
export type Filtering = "linear" | "nearest";
/** The dust's two readings in the brightest mode's components (D205): the physical one and the diagnostic. */
export type DustReading = "acts" | "where";

export interface Tuning {
  /** The march target's largest share of the drawing buffer on a side. */
  resolution: number;
  /** The most pixels the march target holds. */
  pixelBudget: number;
  /** Steps along each ray (compiled into the shader). */
  steps: number;
  /** The most sub-samples read along one step (a uniform, at most SUB_SAMPLES_MAX). */
  subMax: number;
  /** The per-pixel offset into each step; off reads each sub-step at its middle. */
  dither: boolean;
  /** The plane textures' sampling. */
  filtering: Filtering;
  /** A multiplier on the field's LIGHT_PER_LSUN_PC2. */
  fieldGain: number;
  /** The field's weight left at the closest zoom. */
  fieldFloor: number;
  /** The white point's colour temperature, K. */
  whiteKelvin: number;
  bloomStrength: number;
  bloomRadius: number;
  bloomThreshold: number;
  toneMapping: ToneMapping;
  /** The default sprite's size, px (a named instrument's sprite keeps its own). */
  spriteSize: number;
  /** A multiplier on the points' light: REFERENCE_LUMINOSITY is divided by it. */
  pointGain: number;
  /** Where a template's instrument draws a point (S67, D227 R3): the full pupil's image, spikes and pads, in place of the obscured Airy. */
  spikes: boolean;
  // The star-first mode's component layers (D205, D208): the picture's four on by default (the stars, the
  // starlight, the ionized gas and the dust as it acts), the two diagnostics off.
  /** The mode's own picture, the stars in the cells in view above the frame's threshold as points: on by default, switched off to see a layer alone. */
  compPoints: boolean;
  /** The field's stellar layer and the bulge, as a volume. */
  compStars: boolean;
  /** The HII layer and the diffuse layer, with their lines. */
  compGas: boolean;
  /** The dust, in the reading `dustReading` names. */
  compDust: boolean;
  dustReading: DustReading;
  /** The cloud census as markers. */
  compClouds: boolean;
  /** The level-0 cells' edges. */
  compCells: boolean;
  starsIntensity: number;
  gasIntensity: number;
  dustIntensity: number;
  /**
   * Every optical depth the viewer draws, multiplied (S67, D228): a display choice by the owner's ruling of 2026-10-18,
   * an exception to rule D5's "a display intensity never scales a depth". 1 is the model's extinction.
   */
  extinctionStrength: number;
  cloudIntensity: number;
  // The field mode's starlight by age (S63, D223): the render's three age parts, each a layer of the stellar
  // light, all on by default (their sum, the whole).
  /** The young part's light. */
  ageYoung: boolean;
  /** The middle part's light. */
  ageMiddle: boolean;
  /** The old part's light. */
  ageOld: boolean;
  // The clouds as extinction (S64, BUILD_III V6): the census's own dust drawn as a layer of opacity, and the raster's
  // resolution.
  /** The clouds' layer of opacity drawn (the diffuse dust is the render's reduced one either way). */
  cloudsExtinction: boolean;
  /** The clouds' raster, texels per render cell on each axis (cloudOpacity.ts). */
  cloudRaster: number;
  /** Each cloud's elongation along the gas field's shear, as a power of that shear's own axis ratio (S67, D230). */
  cloudElongation: number;
  // The HII regions as knots and the clusters with their radius (S64, BUILD_III V6; RULING_S64 R5-R7).
  /** The field mode's HII regions drawn as knots, the field's HII layers scaled by each cell's undrawn share. */
  knots: boolean;
  /** A cluster drawn with its Plummer profile once its half-mass diameter fills a pixel. */
  clusterRadius: boolean;
  // The randomness layer in the march (S66, BUILD_III V7; D226 R3-R5): each a function the model publishes, evaluated
  // once per ray as a thin screen at the ray's midplane crossing, the value multiplying each sub-step's placement; with
  // the layer off ("physics only") none is drawn whatever its switch.
  /** The gas fluctuation map multiplying the dust's placement (its column, not its scattered light). */
  gasInMarch: boolean;
  /** The gas spurs evaluated from the published table, in place of their cell means in the placement. */
  spursInMarch: boolean;
  /** The young and middle starlight modulated by the clustering field's maps over their cell means. */
  clumpsInMarch: boolean;
}

export const TUNING_DEFAULTS: Readonly<Tuning> = Object.freeze({
  resolution: MAX_RESOLUTION,
  pixelBudget: PIXEL_BUDGET,
  steps: STEPS,
  subMax: SUB_SAMPLES_MAX,
  dither: true,
  filtering: "linear",
  fieldGain: 1,
  fieldFloor: CLOSE_FIELD_FLOOR,
  whiteKelvin: WHITE_KELVIN,
  bloomStrength: BLOOM.strength,
  bloomRadius: BLOOM.radius,
  bloomThreshold: BLOOM.threshold,
  toneMapping: "agx",
  spriteSize: STAR_SPRITE_PX,
  pointGain: 1,
  spikes: false,
  compPoints: true,
  compStars: true,
  compGas: true,
  compDust: true,
  dustReading: "acts",
  compClouds: false,
  compCells: false,
  starsIntensity: 1,
  gasIntensity: 1,
  dustIntensity: 1,
  extinctionStrength: 1,
  cloudIntensity: 1,
  ageYoung: true,
  ageMiddle: true,
  ageOld: true,
  cloudsExtinction: true,
  cloudRaster: CLOUD_RASTER,
  cloudElongation: 1,
  knots: true,
  clusterRadius: true,
  gasInMarch: true,
  spursInMarch: true,
  clumpsInMarch: true,
});

export type TuningKey = keyof Tuning;

interface Base {
  key: TuningKey;
  label: string;
  group: "March" | "Light" | "Bloom and tone" | "Points" | "Components";
  /** Switched in the brightest mode's Components section, not in the Tuning panel. */
  switch?: boolean;
  /** What it does, one line, and that it is a display choice. */
  about: string;
}
export interface RangeControl extends Base {
  kind: "range";
  min: number;
  max: number;
  /** The value's grain; a log control rounds to three significant figures instead. */
  step: number;
  log?: boolean;
  unit: string;
  /** Shown as value × scale (the budget is held in pixels, shown in megapixels). */
  scale?: number;
  integer?: boolean;
}
export interface ToggleControl extends Base {
  kind: "toggle";
}
export interface SelectControl extends Base {
  kind: "select";
  options: { value: string; label: string }[];
}
export type TuningControl = RangeControl | ToggleControl | SelectControl;

export const TUNING_CONTROLS: readonly TuningControl[] = [
  {
    key: "resolution", label: "resolution cap", group: "March", kind: "range", min: 0.25, max: 1, step: 0.05, unit: "× side",
    about: "The march target's largest share of the screen's resolution on a side. A display choice: sampling, not light.",
  },
  {
    key: "pixelBudget", label: "pixel budget", group: "March", kind: "range", min: 100_000, max: 4_000_000, step: 1, log: true, unit: "MP", scale: 1e-6, integer: true,
    about: "The most pixels the field is marched at, whatever the screen. A display choice; large values cost GPU time.",
  },
  {
    key: "steps", label: "steps", group: "March", kind: "range", min: 32, max: 256, step: 16, unit: "", integer: true,
    about: "Ray-march steps along each line of sight. A display choice; recompiles the shader (300 ms after the last move).",
  },
  {
    key: "subMax", label: "sub-samples cap", group: "March", kind: "range", min: 1, max: SUB_SAMPLES_MAX, step: 1, unit: "", integer: true,
    about: "The most reads of the layers along one step (fewer shows grazing terraces). A display choice.",
  },
  {
    key: "dither", label: "dither", group: "March", kind: "toggle",
    about: "A per-pixel offset into each step, fixed by the pixel; off reads each sub-step at its middle. A display choice.",
  },
  {
    key: "gasInMarch", label: "gas fluctuation in the march", group: "March", kind: "toggle",
    about:
      "The gas fluctuation field (the randomness layer's, D221), read once per ray as a thin screen at the ray's crossing of the midplane, the value multiplying each sub-step's " +
      "placement; a column map says nothing of height, and drawn through the layer it would smear each feature by h tan i " +
      "along the view, " +
      "multiplying the dust's placement - its depth, its thermal light and the diagnostic, not its scattered light - " +
      "from the render header's gas_fluctuation (every number the model's; unit mean over every level-0 cell). Off reads " +
      "the placement's cell means alone; with the layer off it is never drawn (S66, V7, D226 R3). A display choice.",
  },
  {
    key: "spursInMarch", label: "spurs in the march", group: "March", kind: "toggle",
    about:
      "The gas spurs evaluated from the render header's spurs table (stages/spurs.py's point function, every " +
      "parameter the model's), their sum read once per ray as a thin screen at the ray's crossing of the midplane (a " +
      "column map says nothing of height, and drawn through the layer it would smear each feature by h tan i along the " +
      "view), composed per sub-step as (1 - <S>(R)) times the placement without them plus S: a spur 60 pc wide that " +
      "the 75 pc x 1 degree cells smear. Off reads the placement's cell means, spurs included (S66, V7, D226 R4). A display choice.",
  },
  {
    key: "clumpsInMarch", label: "young light clustered in the march", group: "March", kind: "toggle",
    about:
      "The field mode's young starlight and the middle part's light that keeps 1, 2 or 3 clustering octaves, each " +
      "multiplied by the clustering field's k-octave map over its level-0 cell's k-octave mean (the render " +
      "header's census_clustering), the map read once per ray as a thin screen at the ray's crossing of the midplane, the value multiplying each sub-step's " +
      "placement; a column map says nothing of height, and drawn through the layer it would smear each feature by h tan i " +
      "along the view, so each cell keeps its light. Off draws them placed by their weights alone (S66, V7, " +
      "D226 R5). A display choice.",
  },
  {
    key: "filtering", label: "plane filtering", group: "March", kind: "select",
    options: [{ value: "linear", label: "linear" }, { value: "nearest", label: "nearest" }],
    about: "How the plane textures are read between cells: linear blends them, nearest shows the model's grid. A display choice.",
  },
  {
    key: "fieldGain", label: "field gain", group: "Light", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Multiplies the field's 1/400 per L☉/pc² against the points. A display balance, not a physical constant.",
  },
  {
    key: "fieldFloor", label: "field floor (close)", group: "Light", kind: "range", min: 0, max: 0.3, step: 0.01, unit: "",
    about: "The field's weight left at the closest zoom, under a region's own stars. A display choice.",
  },
  {
    key: "whiteKelvin", label: "white point", group: "Light", kind: "range", min: 3000, max: 10000, step: 100, unit: "K", integer: true,
    about: "The colour temperature drawn white; asks the model for new responses (400 ms after the last move). A display choice.",
  },
  {
    key: "bloomStrength", label: "bloom strength", group: "Bloom and tone", kind: "range", min: 0, max: 4, step: 0.05, unit: "",
    about: "How much light above the threshold spreads (S67: the range 0-4, was 0-1.5, on the owner's ask; the pass has no upper limit). It acts only on light above the threshold: lower that to see it. A display choice.",
  },
  {
    key: "bloomRadius", label: "bloom radius", group: "Bloom and tone", kind: "range", min: 0, max: 1, step: 0.05, unit: "",
    about: "How far the bloom spreads. Held to 0-1: the pass blends its five blur levels by mix(f, 1.2 - f, radius), and past 1 the finest level's weight turns negative. A display choice.",
  },
  {
    key: "bloomThreshold", label: "bloom threshold", group: "Bloom and tone", kind: "range", min: 0, max: 3, step: 0.05, unit: "",
    about: "The linear intensity above which light blooms. A display choice.",
  },
  {
    key: "toneMapping", label: "tone mapping", group: "Bloom and tone", kind: "select",
    options: [
      { value: "agx", label: "AgX" },
      { value: "aces", label: "ACES Filmic" },
      { value: "reinhard", label: "Reinhard" },
      { value: "linear", label: "Linear" },
    ],
    about: "The curve from summed light to the screen (three.js's). A display choice.",
  },
  {
    key: "spriteSize", label: "sprite size", group: "Points", kind: "range", min: 3, max: 25, step: 1, unit: "px", integer: true,
    about:
      "The default star sprite's size on screen; a named instrument's sprite keeps its own, and where a template carries " +
      "its instrument with a distance (NGC 4414 through WFC3) a point is drawn at its physical size instead (S67). A display choice.",
  },
  {
    key: "pointGain", label: "point gain", group: "Points", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Divides the points' 100 L☉ reference luminosity: brighter or fainter stars against the field. A display choice.",
  },
  {
    key: "spikes", label: "diffraction spikes", group: "Points", kind: "toggle",
    about:
      "Where a template carries its instrument (NGC 4414 through WFC3: HST at 17.7 Mpc), each point is drawn as the " +
      "telescope's image of a point at its physical size. Off: the obscured Airy pattern (2.4 m, obscuration 0.33). On: the " +
      "full pupil's image - the obscuration, four vanes 0.022 pupil radii wide and the primary's three pads, by a 2-D FFT of " +
      "the pupil at load - normalised to the same light, so the switch moves none. Close in the box is clamped: at 0.488 " +
      "pc a screen pixel (NGC 4414's zoom stand) the table's half-width is 314 px and the box 60, the light outside it " +
      "returned inside by the box's share (0.958 of the red Airy, 0.940 of the red spikes), so the core is drawn 4.4 to " +
      "6.4 % brighter in red and the spikes end at the box's square edge. The vanes stand at 45 degrees to the " +
      "picture's axes, a display choice: the detector's own angle was not read. No effect without an instrument (S67, D227 R3). A display choice.",
  },
  {
    key: "compPoints", label: "stars", group: "Components", kind: "toggle", switch: true,
    about: "The star-first mode's own picture: every disc star in the cells in view above the frame's threshold (the faintest the point budget allows), as points. A display choice of what is drawn.",
  },
  {
    key: "compStars", label: "starlight", group: "Components", kind: "toggle", switch: true,
    about: "The brightest mode's starlight volume: the field's stellar layer and the bulge (D205). A display choice of what is drawn.",
  },
  {
    key: "compGas", label: "ionized gas", group: "Components", kind: "toggle", switch: true,
    about: "The HII layer and the diffuse layer with their lines, as the field draws them (D205). A display choice of what is drawn.",
  },
  {
    key: "compDust", label: "dust", group: "Components", kind: "toggle", switch: true,
    about: "The dust, as it acts or where it is (D205). A display choice of what is drawn.",
  },
  {
    key: "dustReading", label: "dust reading", group: "Components", kind: "select", switch: true,
    options: [{ value: "acts", label: "as it acts" }, { value: "where", label: "where it is" }],
    about: "As it acts: extinction, scattered and thermal light. Where it is: a diagnostic, its optical depth drawn as light. A display choice.",
  },
  {
    key: "compClouds", label: "molecular clouds", group: "Components", kind: "toggle", switch: true,
    about: "The cloud census as markers, sized by cloud_size, painted by cloud_mass's ramp: a diagnostic display.",
  },
  {
    key: "compCells", label: "cell outlines", group: "Components", kind: "toggle", switch: true,
    about: "The level-0 cells' edges, 32 rings by 32 sectors: a diagnostic display.",
  },
  {
    key: "starsIntensity", label: "starlight intensity", group: "Components", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Multiplies the starlight volume, in either mode, on the field's gain and the slider's stops. A display balance.",
  },
  {
    key: "gasIntensity", label: "ionized gas intensity", group: "Components", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Multiplies the ionized gas's light, in either mode, on the field's gain and the slider's stops. A display balance.",
  },
  {
    key: "dustIntensity", label: "dust intensity", group: "Components", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Multiplies the dust's own light (as it acts, in either mode) or its drawn depth (where it is, the star-first mode); never its extinction. A display balance.",
  },
  {
    key: "extinctionStrength", label: "extinction strength", group: "Components", kind: "range", min: 0, max: 2, step: 0.01, unit: "×",
    about: "Multiplies every optical depth the viewer draws - the diffuse dust's, the field march's cloud raster, the region's clouds and the dust to each point - in either mode; never the dust's own light (dust intensity). A display choice by the owner's ruling of 2026-10-18 (D228), and an exception to rule D5's \"a display intensity never scales a depth\": at 1 the extinction is the model's.",
  },
  {
    key: "cloudIntensity", label: "cloud marker brightness", group: "Components", kind: "range", min: 0.25, max: 4, step: 0.01, log: true, unit: "×",
    about: "Multiplies the cloud markers' ramp colour. A display balance.",
  },
  {
    key: "ageYoung", label: "young stars", group: "Components", kind: "toggle", switch: true,
    about: "The field's starlight of the young part, placed round each ring by its own weight (S63, D223). A display choice of what is drawn.",
  },
  {
    key: "ageMiddle", label: "middle-aged stars", group: "Components", kind: "toggle", switch: true,
    about: "The field's starlight of the middle age part, placed round each ring by its own weight (S63, D223). A display choice of what is drawn.",
  },
  {
    key: "ageOld", label: "old stars", group: "Components", kind: "toggle", switch: true,
    about: "The field's starlight of the old part, placed round each ring by its own weight (S63, D223). A display choice of what is drawn.",
  },
  {
    key: "cloudsExtinction", label: "clouds as extinction", group: "Components", kind: "toggle", switch: true,
    about:
      "The molecular clouds' own dust as a layer of opacity in the clouds' layer: /api/clouds' cloud_dust_extinction_v, " +
      "rasterised conserving each cloud's A_V x area (S64, V6). Off draws no clouds' layer; the diffuse dust stays the " +
      "render's reduced one (dust_diffuse_share, the model's), so off shows the dust without what the clouds hold. A display choice.",
  },
  {
    key: "knots", label: "HII regions as knots", group: "Components", kind: "toggle", switch: true,
    about:
      "The field mode's HII regions as knots at galaxy scale: each cluster's region a point of its own lines through the " +
      "filter set (/api/clusters' line_response), a disc of its Stromgren radius once that fills a pixel; in each level-0 " +
      "cell the field's HII layers are scaled by 1 - D_c / K_c, D_c the Halpha of the knots drawn there and K_c of every " +
      "knot the cell names; a cell that names no knot by 1 - d, d the drawn share of the whole census's Halpha. With " +
      "every knot drawn the screen carries the census exactly, with none the field; the knots' Halpha " +
      "is 0.921 of the field's on the Milky Way and 1.081 on NGC 4414 (the census's own draw, a measured check, not a " +
      "target) (S64, V6). A display choice.",
  },
  {
    key: "clusterRadius", label: "clusters with their radius", group: "Components", kind: "toggle", switch: true,
    about:
      "A cluster drawn as a Plummer sphere of its half-mass radius (a = r_h / 1.305) once 2 r_h fills a pixel, in place " +
      "of the point sprite, its light the same (S64, V6, T6). At galaxy scale no cluster is that large: it shows below " +
      "about 1 kpc across. A display choice.",
  },
  {
    key: "cloudElongation", label: "cloud elongation", group: "March", kind: "range", min: 0, max: 2, step: 0.05, unit: "power",
    about: "Each cloud's face-on shape in the clouds' raster (S67, D230, the owner's choice: \"Stretch clouds along arms\"): an ellipse of the cloud's own area, its long axis along the gas fluctuation field's local shear (the render header's gas_fluctuation strain per ring, D221), its axis ratio that shear's own, lambda+ = 1 + k^2/2 + |k| sqrt(1 + k^2/4) (5.8 inside 2 kpc, 2.7 at the Sun's radius on the Milky Way), raised to this power: 0 round, 1 the field's. Every cloud's A_V x area is conserved at any value; with the randomness layer off there is no field and the clouds are round. A display choice.",
  },
  {
    key: "cloudRaster", label: "cloud raster", group: "March", kind: "range", min: 1, max: CLOUD_RASTER, step: 1, integer: true, unit: "texels / cell",
    about:
      `The clouds' opacity raster, texels per render cell on each axis. The default, ${CLOUD_RASTER}, is the finest whose ` +
      `float32 texture fits 16 MiB on the 400 x 360 render grid (${400 * CLOUD_RASTER} x ${360 * CLOUD_RASTER} texels, ` +
      `${((400 * CLOUD_RASTER * 360 * CLOUD_RASTER * 4) / 1e6).toFixed(1)} MB; computed in cloudOpacity.ts). Every cloud's A_V x area is ` +
      "conserved at any setting: a display resolution, not light. Beside it a half-float texture of the same texels holds each " +
      "texel's slab (4 bytes a texel: 14.4 MB more at the default, 28.8 MB the two): the clouds are drawn at their own heights, " +
      "a texel holding one cloud as exactly that cloud at its height and extent, one holding several as one uniform slab " +
      "spanning them (their A_V-weighted mean height, half-thickness the rms of their heights in quadrature with their mean " +
      "radius) - the approximation, finer as the raster is finer.",
  },
];

/** The storage key: a UI preference, not a generated object. Since S67 (D227 R4) one per template: `<key>.<template>`. */
export const TUNING_STORAGE_KEY = "galaxygen.tuning";

/**
 * Each template's display defaults over TUNING_DEFAULTS (S67, D227 R4; T1): what the owner tuned on that template,
 * pasted from the Tuning panel's copy box. Display choices (rule D5), each declared one where it is computed (A9); none
 * picked to look like a goal. Both templates carry the owner's pastes (2026-10-18, 2026-10-19), and since the third
 * (2026-10-19) each its own set.
 */
/**
 * The owner's display defaults (S67, D227 T1): the paste of 2026-10-18 ("set these values as the default so i can
 * adjust them after the fix finish"), with the paste of 2026-10-19 laid over it ("update milky way default with this,
 * then copy it over to 4414") - the copy box lists only the choices that differ from the template's own defaults, so
 * the second paste changes steps, field gain, the bloom, the three intensities and the extinction strength and keeps
 * the rest of the first. Display choices, none physics (D5); the extinction strength the owner's ruled exception (D228).
 */
const OWNER_DEFAULTS_2026_10_19 = Object.freeze({
  resolution: 1,
  pixelBudget: 2_000_000,
  steps: 96,
  fieldGain: 1.65,
  fieldFloor: 0.1,
  bloomStrength: 2.25,
  bloomRadius: 0.35,
  bloomThreshold: 0.45,
  toneMapping: "aces",
  spriteSize: 3,
  pointGain: 4,
  compCells: true,
  starsIntensity: 0.55,
  gasIntensity: 1,
  dustIntensity: 1,
  extinctionStrength: 1.25,
  cloudsExtinction: false,
} satisfies Partial<Tuning>);

/**
 * The owner's third paste (S67, D227 T1, 2026-10-19): "ok use this for ngc4414 {"template":"ngc_4414","filters":"rgb",
 * "exposure":0,"fieldGain":1.2,"bloomStrength":2,"spikes":true,"cloudsExtinction":true,"cloudRaster":3} then change the
 * steps for both to 48", and, asked which filter set NGC 4414 should open on, "Switch to RGB". The copy box lists only
 * what differs from the template's own defaults, so the paste is laid over NGC 4414's set above: its field gain, bloom,
 * spikes, clouds as extinction and cloud raster; its exposure 0 is TEMPLATE_EXPOSURE's absent entry, its filter set the
 * template's own (templates.py, now rgb). Steps 48 on both. `spikes` acts only while the template's instrument's own set
 * (WFC3) is shown (GalaxyTab's physical reading, R1-R3): on RGB it waits for the owner to switch sets.
 */
const OWNER_STEPS_2026_10_19 = 48;
// The owner, after the measurement (the Milky Way 4 % brighter at 48 than at 96, its march no faster): "Put the Milky
// Way back to 96 steps, keep NGC 4414 at 48, and close S67."

export const TEMPLATE_TUNING: Readonly<Record<string, Readonly<Partial<Tuning>>>> = Object.freeze({
  milky_way: Object.freeze({ ...OWNER_DEFAULTS_2026_10_19, steps: 96 }),
  // "then copy it over to 4414" (the second paste), then the third paste laid over it. Its points keep the instrument's
  // image (T9) while the WFC3 set is shown, so the sprite size does not reach them there.
  ngc_4414: Object.freeze({
    ...OWNER_DEFAULTS_2026_10_19,
    steps: OWNER_STEPS_2026_10_19,
    fieldGain: 1.2,
    bloomStrength: 2,
    spikes: true,
    cloudsExtinction: true,
    cloudRaster: 3,
  } satisfies Partial<Tuning>),
});
/** Each template's default exposure, stops (S67, D227 R4: the photometric slider's start, App's state); 0 where absent. */
export const TEMPLATE_EXPOSURE: Readonly<Record<string, number>> = Object.freeze({});

/** A template's display defaults: TUNING_DEFAULTS with its own laid over, each made valid; the plain defaults for none. */
export function defaultsFor(template: string | null | undefined, map: Readonly<Record<string, Readonly<Partial<Tuning>>>> = TEMPLATE_TUNING): Tuning {
  const own = template ? map[template] : undefined;
  return own ? sanitize(own, TUNING_DEFAULTS) : { ...TUNING_DEFAULTS };
}

/** A template's default exposure, stops. */
export function exposureFor(template: string | null | undefined, map: Readonly<Record<string, number>> = TEMPLATE_EXPOSURE): number {
  const v = template ? map[template] : undefined;
  return typeof v === "number" && Number.isFinite(v) ? v : 0;
}

/** Where a template's tuning is kept: its own key, or the one key of before S67 with no template (an API without templates). */
export function storageKeyFor(template: string | null | undefined): string {
  return template ? `${TUNING_STORAGE_KEY}.${template}` : TUNING_STORAGE_KEY;
}

const controlOf = (key: string) => TUNING_CONTROLS.find((c) => c.key === key);

/** A control's value made valid: a number clamped (and rounded where integer), a choice among the options. Null if unusable. */
export function clampValue(control: TuningControl, value: unknown): number | boolean | string | null {
  if (control.kind === "toggle") return typeof value === "boolean" ? value : null;
  if (control.kind === "select") return typeof value === "string" && control.options.some((o) => o.value === value) ? value : null;
  const v = typeof value === "number" ? value : Number.NaN;
  if (!Number.isFinite(v)) return null;
  const clamped = Math.min(control.max, Math.max(control.min, v));
  return control.integer ? Math.round(clamped) : clamped;
}

/** Any object read as a Tuning: unknown keys dropped, bad values replaced by the default (`base`'s), numbers clamped. */
export function sanitize(raw: unknown, base: Readonly<Tuning> = TUNING_DEFAULTS): Tuning {
  const out: Tuning = { ...base };
  if (!raw || typeof raw !== "object") return out;
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const control = controlOf(key);
    if (!control) continue;
    const v = clampValue(control, value);
    if (v !== null) (out as unknown as Record<string, unknown>)[key] = v;
  }
  return out;
}

/** The stored tuning of a template (S67: its own key, over its own defaults), or its defaults when there is none or storage is unavailable. */
export function loadTuning(storage: Pick<Storage, "getItem"> | null = safeStorage(), template: string | null = null): Tuning {
  const base = defaultsFor(template);
  try {
    // A template with no key of its own falls back to the one key of before S67 (the lead's second pass, D227): the
    // choices made under it carry over, read and never written back - the first save writes the template's own key.
    const own = storage?.getItem(storageKeyFor(template));
    const text = own ?? (template ? storage?.getItem(TUNING_STORAGE_KEY) : null);
    return text ? sanitize(JSON.parse(text), base) : base;
  } catch {
    return base;
  }
}

/**
 * Keeps only what differs from the template's defaults, under its own key. With no template nothing is stored at the
 * defaults; a template's key is kept as "{}" there, so the old key (loadTuning's fallback) is not read again for it.
 */
export function saveTuning(t: Tuning, storage: Pick<Storage, "setItem" | "removeItem"> | null = safeStorage(), template: string | null = null): void {
  try {
    const diff = changed(t, defaultsFor(template));
    const key = storageKeyFor(template);
    if (Object.keys(diff).length === 0 && !template) storage?.removeItem(key);
    else storage?.setItem(key, JSON.stringify(diff));
  } catch {
    // Private windows and blocked site data: the panel works for this visit without it.
  }
}

/** The entries that differ from the defaults (a template's, since S67: defaultsFor): the combination to report. */
export function changed(t: Tuning, defaults: Readonly<Tuning> = TUNING_DEFAULTS): Partial<Tuning> {
  const out: Record<string, unknown> = {};
  for (const control of TUNING_CONTROLS) {
    if (t[control.key] !== defaults[control.key]) out[control.key] = t[control.key];
  }
  return out as Partial<Tuning>;
}

/** A range control's slider position, 0 to 1000, for a value: linear in the value, or in its log. */
export function positionOf(control: RangeControl, value: number): number {
  const f = control.log
    ? Math.log(value / control.min) / Math.log(control.max / control.min)
    : (value - control.min) / (control.max - control.min);
  return Math.round(1000 * Math.min(1, Math.max(0, f)));
}

/** The value at a slider position: snapped to the control's step, or to three significant figures on a log scale. */
export function valueAt(control: RangeControl, position: number): number {
  const f = Math.min(1, Math.max(0, position / 1000));
  if (control.log) {
    const v = control.min * (control.max / control.min) ** f;
    return clampValue(control, Number(v.toPrecision(3))) as number;
  }
  const v = control.min + Math.round((f * (control.max - control.min)) / control.step) * control.step;
  return clampValue(control, Number(v.toFixed(6))) as number;
}

function safeStorage(): Storage | null {
  try {
    return typeof localStorage === "undefined" ? null : localStorage;
  } catch {
    return null;
  }
}
