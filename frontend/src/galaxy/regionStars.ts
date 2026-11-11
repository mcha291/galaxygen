// Which star layers the Galaxy view asks for and draws (S82, #172; the owner's ruling of 2026-11-02: "accept A but keep
// the current modes around for now so i can compare and assess later").
//
// The star-first mode draws the bright catalogue at level-k tiles (V6b, D225) and the clusters through the filter set's
// response, on the field's scale (FluxPoints). The field mode's region regime (below 4 kpc, V3) drew instead the level-k
// star sample (loadRegion) and the region's clusters as display-colour points. Since S82 the region regime draws the
// star-first mode's points by default ("catalogue"); "sampled" is V3's reading exactly as it was, kept for comparison.
// The region's volumes (RegionVolume: the window's clouds, HII spheres and shells, and the region's clusters they read)
// are drawn at both. Above 4 kpc nothing changes, nor anything in the star-first mode.

/** The field mode's region regime's star layer: the bright catalogue's points, or V3's display-colour sample. */
export type RegionStars = "catalogue" | "sampled";

/** What the frame asks for and draws: the star-first points (the bright table, counts, tiles and clusters), and V3's
 *  region sample with its display-colour cluster points. */
export interface StarLoads {
  points: boolean;
  sampled: boolean;
}

/**
 * The loaders the switch decides: the star-first mode its points when they are on; the field mode below 4 kpc (`inRegion`,
 * the region regime's window) the points at "catalogue" (when on) or V3's sample at "sampled"; the field mode above 4 kpc
 * neither.
 */
export function starLoads(mode: "field" | "stars", regionStars: RegionStars, compPoints: boolean, inRegion: boolean): StarLoads {
  if (mode === "stars") return { points: compPoints, sampled: false };
  if (!inRegion) return { points: false, sampled: false };
  return regionStars === "catalogue" ? { points: compPoints, sampled: false } : { points: false, sampled: true };
}

/**
 * The young population drawn once at "sampled" (S93, T3 / #115): a row whose `column` reads `drop` draws nothing - its
 * three colour channels zeroed in place, the points' positions and names untouched. The region sample drops the stars
 * the cluster points carry (`star_cluster_member` 1, the model's membership), the census its dissolved clusters
 * (`cluster_bound` 2), whose stars the sample keeps. A response without the column (an older model) is drawn whole.
 */
export function dropRows(colors: Float32Array | null, column: ArrayLike<number> | undefined, drop: number): Float32Array | null {
  if (!colors || !column || column.length * 3 !== colors.length) return colors;
  for (let i = 0; i < column.length; i += 1) {
    if (Number(column[i]) === drop) colors.fill(0, 3 * i, 3 * i + 3);
  }
  return colors;
}
