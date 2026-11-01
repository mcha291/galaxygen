// The clouds' raster worker (S78, R5): builds the raster off the main thread, so the landing's raster (0.3-0.5 s on the
// Milky Way's 2000 x 1800 texels) overlaps the field mesh's build instead of following it. One job at a time, in the
// order posted (cloudRasterClient.ts sends at most one while another runs); the answer's A_V and halves transferred.
// The job is cloudRasterJob.ts's rasterJob: cloudRaster and packRaster themselves, so the raster is the same bits.
import { type RasterAnswer, type RasterMessage, answerTransfer, rasterJob } from "./cloudRasterJob";

// The worker's global scope, typed by what is used here (the app's lib is the DOM's, whose `self` is a Window).
const scope = self as unknown as {
  onmessage: ((event: MessageEvent<RasterMessage>) => void) | null;
  postMessage(message: RasterAnswer, transfer: Transferable[]): void;
};

scope.onmessage = (event) => {
  const { id, request } = event.data;
  const started = performance.now();
  const raster = rasterJob(request);
  scope.postMessage({ id, raster, ms: performance.now() - started }, answerTransfer(raster));
};
