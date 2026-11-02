// The field mesh's texels worker (S81, #208 (b)): builds the march's plane textures off the main thread, so a landing's
// or a switch's mesh build (planeTexture and the clustered fill, one long task of ~60 ms on the main thread of a
// production build) leaves it free. One job at a time, in the order posted (meshTexelsClient.ts sends at most one while
// another runs); the answer's textures transferred. The job is meshTexelsJob.ts's meshTexels: planeTexture, agedLight,
// clumpedLight and starTexels themselves, so the textures are the same bits. The clouds' raster worker's pattern
// (cloudRaster.worker.ts), a worker of its own so the two builds overlap.
import { type MeshAnswer, type MeshMessage, answerTransfer, meshTexels } from "./meshTexelsJob";

// The worker's global scope, typed by what is used here (the app's lib is the DOM's, whose `self` is a Window).
const scope = self as unknown as {
  onmessage: ((event: MessageEvent<MeshMessage>) => void) | null;
  postMessage(message: MeshAnswer, transfer: Transferable[]): void;
};

scope.onmessage = (event) => {
  const { id, request } = event.data;
  const started = performance.now();
  const texels = meshTexels(request);
  scope.postMessage({ id, texels, ms: performance.now() - started }, answerTransfer(texels));
};
