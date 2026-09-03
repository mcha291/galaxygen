"""Content hashes: what bytes is this server actually serving? (rule D3)

"Am I running the new code" should be a glance, not an investigation. A viewer
that renders a stale bundle looks exactly like a viewer whose new code does not
work, and the two are told apart by comparing a hash the page can read against
the hash the API computes from the files on disk.

The hash is over content, not mtime: a file touched but unchanged must not look
like a deployment, and a file changed inside one second must not look identical.
It is recomputed per request rather than cached, because the question is asked
precisely while files are changing under the server, and a cached answer would
be a reading of the cache (rule B2). The cost is published with the rest of the
timings.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

DIGEST_BYTES = 16  # 32 hex characters: short enough to read aloud, long enough to differ

HERE = Path(__file__).resolve().parent
CLIENT = HERE / "client"  # the viewer's own bytes (D3); S7 fills this directory
SERVER = HERE  # the API's own bytes, so a stale *server* is visible too


def _files(root: Path, suffixes: Iterable[str] | None) -> list[Path]:
    if not root.is_dir():
        return []
    keep = None if suffixes is None else tuple(suffixes)
    return sorted(
        p for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and (keep is None or p.suffix in keep)
    )


def content_hash(root: Path = CLIENT, suffixes: Iterable[str] | None = None) -> dict:
    """``{"hash", "files": [{path, hash, bytes}], "count", "bytes"}`` for a directory tree.

    Paths are relative and POSIX-shaped, and each file's path goes into the
    aggregate alongside its bytes: renaming a file changes the tree's hash even
    though no byte of content moved, which is what makes the aggregate a hash of
    *what is served* rather than of what happens to be in it.
    """
    digest = hashlib.blake2b(digest_size=DIGEST_BYTES)
    files: list[dict] = []
    total = 0
    for path in _files(root, suffixes):
        raw = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        one = hashlib.blake2b(raw, digest_size=DIGEST_BYTES).hexdigest()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(raw)
        digest.update(b"\0")
        files.append({"path": rel, "hash": one, "bytes": len(raw)})
        total += len(raw)
    return {"hash": digest.hexdigest(), "files": files, "count": len(files), "bytes": total}
