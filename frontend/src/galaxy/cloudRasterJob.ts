// The clouds' raster as a job (S78, R5): what the raster worker (cloudRaster.worker.ts) is asked and answers, and the
// job itself - cloudRaster and packRaster imported from cloudOpacity.ts, not copied, so what the worker builds is what
// the main thread would have built, bit for bit (cloudRasterJob.test.ts asserts it). No three.js here but the
// float-to-half conversion, imported from three's own module (three/src/extras/DataUtils.js) so the worker's chunk
// does not carry all of three; the test proves it the same function as `DataUtils.toHalfFloat` from "three".
import { toHalfFloat } from "three/src/extras/DataUtils.js";

import { type CloudColumns, type KeptRaster, type RasterShape, cloudRaster, packRaster } from "./cloudOpacity";

/** The census columns the raster reads, by name (CloudColumns'), in the order they are sent. */
export const RASTER_COLUMNS = [
  "cloud_radius", "cloud_azimuth", "cloud_size", "cloud_dust_extinction_v", "cloud_height", "cloud_axis_ratio", "cloud_angle",
] as const;

/** One raster asked of the worker: the census's columns (copies, each its own buffer), the grid and the shape. */
export interface RasterRequest {
  clouds: CloudColumns;
  rLo: number;
  rHi: number;
  width: number;
  height: number;
  shape: RasterShape;
}

/** The worker's answer: the packed raster (its `av` and `halves` transferred, not copied) and its own time, ms. */
export interface RasterAnswer {
  id: number;
  raster: KeptRaster;
  ms: number;
}

/** What the main side posts: the request with the job's number, which the answer carries back. */
export interface RasterMessage {
  id: number;
  request: RasterRequest;
}

/** The job: cloudRaster then packRaster, with three's own half-float conversion - what keptCloudRaster builds on a miss. */
export function rasterJob(request: RasterRequest): KeptRaster {
  const { clouds, rLo, rHi, width, height, shape } = request;
  return packRaster(cloudRaster(clouds, rLo, rHi, width, height, shape), toHalfFloat);
}

/**
 * A request for these columns: each typed column copied into a buffer of its own (a column may be a view into the
 * whole answer's buffer, which a structured clone would copy entire), the rest as they are; absent columns left out.
 * The copies are the request's own, so they can be transferred.
 */
export function rasterRequest(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape): { request: RasterRequest; transfer: ArrayBuffer[] } {
  const copied: Record<string, ArrayLike<number>> = {};
  const transfer: ArrayBuffer[] = [];
  for (const name of RASTER_COLUMNS) {
    const column = clouds[name];
    if (!column) continue;
    if (ArrayBuffer.isView(column)) {
      const copy = (column as unknown as Float32Array).slice();
      copied[name] = copy;
      transfer.push(copy.buffer as ArrayBuffer);
    } else copied[name] = Array.from(column);
  }
  return {
    request: { clouds: copied as unknown as CloudColumns, rLo, rHi, width, height, shape: { verticalCap: shape.verticalCap, elongation: shape.elongation } },
    transfer,
  };
}

/** The buffers of an answer to transfer back: the A_V's and the halves'. */
export function answerTransfer(raster: KeptRaster): ArrayBuffer[] {
  return [raster.av.buffer as ArrayBuffer, raster.halves.buffer as ArrayBuffer];
}
