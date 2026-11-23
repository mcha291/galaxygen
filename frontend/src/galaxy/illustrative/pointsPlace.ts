// The points' placement under the illustrative look (S108, the grazing handover): a file of its own so both the
// registry (index.ts, FluxPoints' patch) and the regions' layer (knotsLayer.ts) read it without an import cycle.

/**
 * The points' placement (S108; FluxPoints' vertex shader under the illustrative look): the point's grazing weight from
 * its sight line, and the point lifted by the material's own `illPointsLift` (kpc; a layer that hands FluxPoints a
 * runtime with that uniform added - CloudsLayer; absent elsewhere, read as 0: the point where it is). `position` is
 * defined over the lifted place for everything after this (dustTo, main), so the point is drawn and dimmed there.
 */
export const POINTS_PLACE_GLSL = /* glsl */ `
  uniform float illPointsLift;
  vec3 illPointsPos;
  void illPointsPlace() {
    illGraze = illGrazeOf(position - cameraPosition);
    illPointsPos = illLiftOf(position, illPointsLift);
  }
  #define position illPointsPos`;
