// The client transport: the one place in this project that talks to the network.
//
// Rule D2 — exactly one `fetch`, asserted in CI (tests/test_api.py). The reason
// is not tidiness: instrumentation that has to be remembered in N places will be
// forgotten in one of them (rule B13), and the one that is forgotten is the one
// that matters. Retries, timing, the staleness check, an offline banner — every
// one of those is a change to this file only.
//
// Rule A9 — nothing here has an opinion about how a field is drawn. Ramps,
// units, labels and categories arrive inside the field declaration from
// /api/fields, and a viewer that keeps its own table of colours has created a
// duplicate that either loses (dead code) or wins (a bug wearing the right
// name). This module hands the declaration through untouched.
//
// Rule D5 — no physics here, and nothing generated is persisted. This is a
// decoder and a URL builder.

export const WIRE = "galaxy-bin/1";
export const MAGIC = "GLXY";
export const BASE = "/api";
// Same-origin by default: the page and the API are served together. An absolute
// origin is passed per call by whatever is not a page — a test harness, a viewer
// developed against a server on another port.
export const ORIGIN = "";

const HEADER_OFFSET = 8; // magic (4) + header length (4)
const READERS = { f8: Float64Array, i8: BigInt64Array };

export class ApiError extends Error {
  constructor(status, body, url) {
    super(`${status} ${url}: ${(body && body.error) || "request failed"}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

/** Build a URL: params with a null or undefined value are simply not sent. */
export function url(path, params = {}, origin = ORIGIN) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined) continue;
    query.set(key, Array.isArray(value) ? value.join(",") : String(value));
  }
  const search = query.toString();
  const route = `${origin}${path.startsWith("/") ? path : `${BASE}/${path}`}`;
  return search ? `${route}?${search}` : route;
}

/**
 * The single fetch. Everything else in the viewer goes through here.
 *
 * Returns { status, stages, type, buffer }: the raw bytes plus the stages the
 * server says it ran, which is how rule D4 is visible from the client side.
 */
async function transport(path, params, options = {}) {
  const target = url(path, params, options.origin);
  const response = await fetch(target, {
    method: options.method || "GET",
    cache: "no-store",
    signal: options.signal,
  });
  const buffer = await response.arrayBuffer();
  const type = response.headers.get("content-type") || "";
  const stages = (response.headers.get("x-galaxy-stages") || "").split(",").filter(Boolean);
  if (!response.ok) {
    throw new ApiError(response.status, safeJson(buffer), target);
  }
  return { status: response.status, stages, type, buffer, url: target };
}

function safeJson(buffer) {
  try {
    return JSON.parse(new TextDecoder().decode(buffer));
  } catch {
    return null;
  }
}

/** A JSON route: /api, /api/version, /api/stages, /api/fields, /api/inputs. */
export async function get(path, params, options) {
  const { buffer, stages, url: target } = await transport(path, params, options);
  const parsed = safeJson(buffer);
  if (parsed === null) throw new ApiError(200, null, target);
  return Object.defineProperty(parsed, "stages", { value: stages, enumerable: false });
}

/** A binary route: /api/arrays, /api/region. Returns { header, arrays, stages }. */
export async function frame(path, params, options) {
  const { buffer, stages } = await transport(path, params, options);
  return { ...decode(buffer), stages };
}

/**
 * Decode one galaxy-bin/1 frame.
 *
 * The header is padded so that the payload starts on an 8-byte boundary, which
 * is what lets each array be a view onto the response buffer rather than a copy:
 * a typed-array view with a misaligned offset throws.
 */
export function decode(buffer) {
  const bytes = new Uint8Array(buffer);
  const magic = new TextDecoder().decode(bytes.subarray(0, 4));
  if (magic !== MAGIC) throw new Error(`not a ${WIRE} frame: magic is ${JSON.stringify(magic)}`);
  const length = new DataView(buffer).getUint32(4, true);
  const header = JSON.parse(new TextDecoder().decode(bytes.subarray(HEADER_OFFSET, HEADER_OFFSET + length)));
  if (header.format !== WIRE) throw new Error(`unknown wire format ${header.format}`);
  const start = HEADER_OFFSET + length;
  const arrays = {};
  for (const spec of header.arrays) {
    const Reader = READERS[spec.dtype];
    if (!Reader) throw new Error(`unknown dtype ${spec.dtype} for ${spec.name}`);
    arrays[spec.name] = new Reader(buffer, start + spec.offset, spec.bytes / Reader.BYTES_PER_ELEMENT);
  }
  return { header, arrays };
}

/**
 * Category codes as numbers.
 *
 * A categorical column is int64 on the wire, because that is what the model
 * publishes, and int64 reaches JavaScript as BigInt. Rendering wants an index
 * into the palette from the field declaration, so this copies once, deliberately
 * and where it can be seen, rather than leaving `Number(codes[i])` scattered
 * through drawing code.
 */
export function codes(view) {
  const out = new Int32Array(view.length);
  for (let i = 0; i < view.length; i += 1) out[i] = Number(view[i]);
  return out;
}

// --- the routes, named ------------------------------------------------------
// Thin wrappers so a caller writes what it wants rather than a path and a
// parameter spelling. Every one of them goes through `transport` above.

// Every one of them takes one options object — `{ model, origin, signal }` —
// because a mixture of `f(model, options)` and `f(options)` is a call somebody
// gets wrong by passing the options as the model, and the URL that results is
// `model=[object Object]`. Uniform beats memorable (rule B13).

export const version = (options) => get("/api/version", {}, options);
export const stages = (options = {}) => get("/api/stages", { model: options.model }, options);
export const fields = (options = {}) => get("/api/fields", { model: options.model }, options);
export const inputs = (options = {}) => get("/api/inputs", { model: options.model }, options);

export const arrays = (names, params = {}, options) =>
  frame("/api/arrays", { ...params, fields: names }, options);

export const region = (window = {}, params = {}, options) =>
  frame("/api/region", { ...params, ...window }, options);
