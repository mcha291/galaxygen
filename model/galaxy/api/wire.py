"""``galaxy-bin/1``: one JSON header, then the arrays, in one response.

A field is 400 x 2000 float64 and a catalogue is seven columns; JSON would
double the bytes and lose the exact value. So arrays travel as bytes and
everything else travels as JSON, in a single body:

    magic   4 bytes   b"GLXY"
    length  4 bytes   uint32 little-endian: the header's length, padding included
    header  n bytes   UTF-8 JSON, space-padded so the payload starts 8-aligned
    payload           the arrays back to back, in the order the header lists

**The padding is load-bearing.** A browser reads an array as
``new Float64Array(buffer, offset, count)``, which throws unless ``offset`` is a
multiple of 8. Every dtype here is 8 bytes wide, so aligning the header aligns
every array behind it, and the alignment is asserted rather than assumed.

Little-endian is stated in the header and written explicitly rather than taken
from the host: the one machine that disagrees would produce numbers that are
wrong and plausible.
"""

from __future__ import annotations

import json
import struct
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

MAGIC = b"GLXY"
FORMAT = "galaxy-bin/1"
ALIGN = 8
MEDIA = "application/octet-stream"

# The closed set of wire dtypes. A field is float64 or an int64 category code
# (galaxy/core/fielddoc.py); anything else is a declaration this format has not
# been taught, and saying so beats shipping a silent cast.
DTYPES: dict[str, str] = {"float64": "f8", "int64": "i8"}


class WireError(ValueError):
    """A value cannot be framed, or a frame cannot be read."""


def _dtype(arr: np.ndarray) -> str:
    name = arr.dtype.name
    if name not in DTYPES:
        raise WireError(f"dtype {name!r} is not one of {sorted(DTYPES)}")
    return DTYPES[name]


def encode(header: Mapping[str, Any], arrays: Sequence[tuple[str, np.ndarray]]) -> bytes:
    """Frame ``arrays`` under ``header``, which is extended with their layout."""
    described: list[dict[str, Any]] = []
    payload: list[bytes] = []
    offset = 0
    for name, value in arrays:
        arr = np.ascontiguousarray(value)
        code = _dtype(arr)
        raw = arr.astype("<" + code, copy=False).tobytes()
        described.append({
            "name": name,
            "dtype": code,
            "shape": list(arr.shape),
            "offset": offset,
            "bytes": len(raw),
        })
        payload.append(raw)
        offset += len(raw)

    full = {**dict(header), "format": FORMAT, "endian": "little", "arrays": described}
    body = json.dumps(full, allow_nan=False).encode("utf-8")
    pad = -(len(MAGIC) + 4 + len(body)) % ALIGN
    body += b" " * pad
    return MAGIC + struct.pack("<I", len(body)) + body + b"".join(payload)


def decode(blob: bytes) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """The reader for Python callers and for the test that the framing round-trips."""
    if blob[:4] != MAGIC:
        raise WireError(f"not a {FORMAT} frame: magic is {blob[:4]!r}")
    (n,) = struct.unpack("<I", blob[4:8])
    header = json.loads(blob[8 : 8 + n].decode("utf-8"))
    start = 8 + n
    if start % ALIGN:
        raise WireError(f"payload starts at {start}, which is not {ALIGN}-aligned")
    out: dict[str, np.ndarray] = {}
    for spec in header["arrays"]:
        lo = start + spec["offset"]
        raw = blob[lo : lo + spec["bytes"]]
        if len(raw) != spec["bytes"]:
            raise WireError(f"array {spec['name']!r} is truncated: {len(raw)} of {spec['bytes']} bytes")
        out[spec["name"]] = np.frombuffer(raw, dtype="<" + spec["dtype"]).reshape(spec["shape"])
    return header, out
