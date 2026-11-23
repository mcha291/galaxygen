// The illustrative look's base overlay (S105, BUILD_VIII row 105): per template, the Tuning panel's own keys that
// differ under the illustrative look from the physical look's defaults (TEMPLATE_TUNING), laid over them. The
// illustrative parameters' own per-template defaults are each control's `perTemplate` in its feature file. Tuned by
// eye against the goal pictures (D275: a goal picture is a target for this look alone); the owner's to re-tune.

/** Base Tuning keys over TEMPLATE_TUNING[template], under the illustrative look (values made valid by tuning.ts sanitize). */
export const ILLUSTRATIVE_BASE: Readonly<Record<string, Readonly<Record<string, number | string | boolean>>>> = Object.freeze({
  // S105, by eye against the goal: the bloom restrained (the grade compresses the core instead), the white point cooler so
  // the old light reads cream and the young blue, the knots dimmer (their sprites are dots, row 106 draws the regions),
  // and the clouds' raster off - its 17 000 dark flecks are an even speckle the goal's lanes are not (row 107 draws lanes).
  // S105 tuner M (all features together): the bloom halved and its threshold raised, so the regions and the sparkle
  // catch no violet halo.
  milky_way: Object.freeze({ bloomStrength: 0.3, bloomRadius: 0.4, bloomThreshold: 1.5, whiteKelvin: 6000, cloudsExtinction: false, knotsIntensity: 0.3 }),
  // The clouds kept and darkened (the goal's brown network is the nearest thing the frame has), 96 steps (at 48 the core
  // drew a green-cyan cast under the stretch).
  ngc_4414: Object.freeze({ bloomStrength: 0.6, bloomRadius: 0.4, bloomThreshold: 1.0, whiteKelvin: 6000, steps: 96, extinctionStrength: 1.6 }),
});
