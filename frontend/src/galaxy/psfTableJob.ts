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

/**
 * Builds the table (hstPsf.ts psfTable, with the pupil's image as its density where the spikes are on). A segmented
 * primary (S83, T11: JWST's hexagonal-18) has no closed form: its table is the pupil's image either way - the
 * segments alone with the switch off (their own six spikes, as the annulus alone is the obscured Airy), the segments and
 * the struts with it on - the same transform; a circular aperture with the switch off is the obscured Airy, as before.
 */
export function psfJob(request: PsfRequest): PsfTable {
  const { optics, pivots, spikes, cells, fft } = request;
  const imaged = spikes || optics.aperture === "hexagonal-18";
  // The image is a local: once the table is built nothing holds it, and it is collected.
  const density = imaged ? (fft ? imageDensity(pupilImage(optics, spikes, fft.n, fft.m), fft.n, fft.m) : imageDensity(pupilImage(optics, spikes))) : undefined;
  return psfTable(optics, { pivots, density, cells });
}

/** What the answer transfers: the corners' buffer (the only large array). */
export function answerTransfer(table: PsfTable): ArrayBuffer[] {
  return [table.corners.buffer as ArrayBuffer];
}
