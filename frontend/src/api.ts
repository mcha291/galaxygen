// The app's view of the API. No network code lives here: every request goes
// through interface/transport.js, the project's one fetch (rule D2), and every
// colour comes from the field declarations it returns (rule A9).
import { fields, inputs, region, stages } from "@interface/transport.js";

import type { Checkpoint, InputDecl } from "./workflow/logic";

/** How many stars the galaxy view asks for: the materialised sample (D61). */
export const STAR_SAMPLE = 20_000;

export type Columns = Record<string, ArrayLike<number | bigint>>;
export type Query = Record<string, unknown>;

export interface FieldDecl {
  name: string;
  label: string;
  unit: string;
  ramp?: { kind: "ramp" | "palette" } & Record<string, unknown>;
  categories?: string[];
  [key: string]: unknown;
}

export interface FieldsPayload {
  model: string;
  fields: FieldDecl[];
  cmaps: Record<string, unknown>;
}

export interface StagesPayload {
  model: string;
  models: string[];
  order: string[];
  checkpoints: Omit<Checkpoint, "inputs">[];
}

export interface InputsPayload {
  model: string;
  controls: InputDecl[];
  seeds: InputDecl[];
  events: InputDecl[];
}

export interface Sample {
  columns: Columns;
  header: {
    cells: { ids: number[]; counts: number[]; count: number; of: number };
    stars: { materialised: number; requested: number; seed: number };
    [key: string]: unknown;
  };
}

export async function loadFields(model?: string, signal?: AbortSignal): Promise<FieldsPayload> {
  return (await fields({ model, signal })) as FieldsPayload;
}

/** What the workflow walks: a model's checkpoints and the inputs that belong to them. */
export async function loadDeclarations(
  model?: string,
  signal?: AbortSignal,
): Promise<{ stages: StagesPayload; inputs: InputsPayload }> {
  const [s, i] = await Promise.all([stages({ model, signal }), inputs({ model, signal })]);
  return { stages: s as StagesPayload, inputs: i as InputsPayload };
}

/** The whole-galaxy star sample for one input vector: every cell, STAR_SAMPLE stars in all. */
export async function loadSample(query: Query = {}, signal?: AbortSignal): Promise<Sample> {
  const got = await region({}, { ...query, stars: STAR_SAMPLE }, { signal });
  return { columns: got.arrays as Columns, header: got.header as Sample["header"] };
}
