// The instrument's PSF table worker (S82, #178 (ii)): builds psf.ts physicalPsf's table - and, with the spikes on, the
// pupil's 2048^2 FFT it is made from - off the main thread. One job at a time, in the order posted; the answer's corners
// transferred. The job is psfTableJob.ts's psfJob: hstPsf.ts's own functions, so the table is the same bits. S81's
// pattern (meshTexels.worker.ts).
import { type PsfAnswer, type PsfMessage, answerTransfer, psfJob } from "./psfTableJob";

// The worker's global scope, typed by what is used here (the app's lib is the DOM's, whose `self` is a Window).
const scope = self as unknown as {
  onmessage: ((event: MessageEvent<PsfMessage>) => void) | null;
  postMessage(message: PsfAnswer, transfer: Transferable[]): void;
};

scope.onmessage = (event) => {
  const { id, request } = event.data;
  const started = performance.now();
  const table = psfJob(request);
  scope.postMessage({ id, table, ms: performance.now() - started }, answerTransfer(table));
};
