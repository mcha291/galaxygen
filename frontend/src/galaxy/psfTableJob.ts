// The instrument's PSF table as a job (S82, #178 (ii)): what psf.ts physicalPsf draws a point from - the obscured Airy's
// table, or the pupil's image (the 2048^2 FFT) and its table - asked of a worker (psfTable.worker.ts) so the build
// leaves the main thread (about 1.6 s the first time the spikes are switched on), on S81's pattern (meshTexelsJob.ts).
// The job is hstPsf.ts's psfTable, pupilImage and imageDensity themselves, imported, not copied, so what the worker
// builds is what the main thread would have built, bit for bit (psfTableJob.test.ts asserts it). The pupil's image
// (32 MB of float64 at 2048^2) lives only inside the job: it is dropped once its table is made. No three.js here.
import { type Optics, type PsfTable, imageDensity, psfTable, pupilImage } from "./hstPsf";

/** One table asked: the optics, the set's pivots (Angstrom), and the switch (R3: off the obscured Airy, on the pupil's image). */
export interface PsfRequest {
  optics: Optics;
  pivots: number[];
  spikes: boolean;
  /** Sampling overrides, for the tests' small fixture only: the table's cells and the FFT's size and pupil samples. */
  cells?: number;
  fft?: { n: number; m: number };
}

export interface PsfMessage {
  id: number;
  request: PsfRequest;
}

export interface PsfAnswer {
  id: number;
  table: PsfTable;
  /** The build's own time, ms. */
  ms: number;
}

/** Builds the table (hstPsf.ts psfTable, with the pupil's image as its density where the spikes are on). */
export function psfJob(request: PsfRequest): PsfTable {
  const { optics, pivots, spikes, cells, fft } = request;
  // The image is a local: once the table is built nothing holds it, and it is collected.
  const density = spikes ? (fft ? imageDensity(pupilImage(optics, true, fft.n, fft.m), fft.n, fft.m) : imageDensity(pupilImage(optics))) : undefined;
  return psfTable(optics, { pivots, density, cells });
}

/** What the answer transfers: the corners' buffer (the only large array). */
export function answerTransfer(table: PsfTable): ArrayBuffer[] {
  return [table.corners.buffer as ArrayBuffer];
}
