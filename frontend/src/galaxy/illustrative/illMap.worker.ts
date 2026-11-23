// The illustrative map's worker (S107, the sliders' stall): builds the features' map planes and the arms' sparkle off
// the main thread (illMapJob.ts the job, illMapClient.ts the main side). One job at a time, in the order posted; a
// release drops the worker's caches. The planes and the points are transferred back, not copied.
import { type JobMessage, MapJobState, handle } from "./illMapJob";

// The worker's global scope, typed by what is used here (the app's lib is the DOM's, whose `self` is a Window).
const scope = self as unknown as {
  onmessage: ((event: MessageEvent<JobMessage>) => void) | null;
  postMessage(message: unknown, transfer: Transferable[]): void;
};

const state = new MapJobState();

scope.onmessage = (event) => {
  const out = handle(state, event.data);
  if (out) scope.postMessage(out.answer, out.transfer);
};
