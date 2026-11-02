// Where the Galaxy view's regime caption stands while the edit drawer is open (S82, #190).
//
// The drawer (App.module.css .editDrawer) is a 320 px panel at the stage's top right, inset by --space-4; the
// regime caption (GalaxyTab.module.css .regime) sits at the top right of the render's captions. While the drawer
// is open the caption moves left of it, so neither covers the other; closed, nothing moves (the picture test's
// captures are taken with the drawer closed). The captions fill the whole stage, or - while a picture is set
// beside the render - the left of two halves whose right edge may or may not reach under the drawer, so the shift
// there is only the drawer's overlap with that half. On phones the drawer is a bottom sheet and nothing moves
// (the media queries in both files). The widths are written in the CSS; drawerLayout.test.ts holds the two files
// to the numbers here.

/** The edit drawer's width, px (App.module.css .editDrawer `width`). */
export const DRAWER_WIDTH_PX = 320;

/** How the regime caption stands: where it always stood, left of the drawer over the whole stage, or left of
 *  the drawer's overlap with the render's half. */
export type RegimePlace = "home" | "besideDrawer" | "besideDrawerHalf";

export function regimePlace(editing: boolean, pictureBeside: boolean): RegimePlace {
  if (!editing) return "home";
  return pictureBeside ? "besideDrawerHalf" : "besideDrawer";
}
