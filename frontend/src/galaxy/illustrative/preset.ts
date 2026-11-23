// The illustrative look's base overlay (S105, BUILD_VIII row 105): per template, the Tuning panel's own keys that
// differ under the illustrative look from the physical look's defaults (TEMPLATE_TUNING), laid over them. The
// illustrative parameters' own per-template defaults are each control's `perTemplate` in its feature file. Tuned by
// eye against the goal pictures (D275: a goal picture is a target for this look alone); the owner's to re-tune.

/** Base Tuning keys over TEMPLATE_TUNING[template], under the illustrative look (values made valid by tuning.ts sanitize). */
export const ILLUSTRATIVE_BASE: Readonly<Record<string, Readonly<Record<string, number | string | boolean>>>> = Object.freeze({
  milky_way: Object.freeze({ bloomStrength: 0.6, bloomRadius: 0.4, bloomThreshold: 1.0 }),
  ngc_4414: Object.freeze({ bloomStrength: 0.6, bloomRadius: 0.4, bloomThreshold: 1.0 }),
});
