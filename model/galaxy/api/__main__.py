"""``python -m galaxy.api``: serve the API, print where it is and what it is serving.

In a container the host, port and viewer directory come from the environment
(``GALAXY_HOST``, ``PORT``, ``GALAXY_CLIENT``, ``GALAXY_BUNDLES``), so the image serves the built
frontend and its template bundles on ``0.0.0.0`` without a different entry point.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from pathlib import Path

from galaxy.api.bundle import BundleError
from galaxy.api.http import HOST, PORT, serve
from galaxy.api.service import Service
from galaxy.api.version import CLIENT, content_hash
from galaxy.specs import utf8_stdout


def _logged(handle, path: Path):
    """``handle``, recording each answer's path, status, source and size as a JSON line in ``path`` (S72, W2)."""
    lock = threading.Lock()

    def logged(route, query=None):
        response = handle(route, query)
        entry = {"path": route, "status": response.status, "source": response.source, "bytes": len(response.body)}
        if route.rstrip("/") == "/api/version" and isinstance(query, str) and query:
            entry["query"] = query[:200]  # the picture test's capture marker (its answers follow it)
        line = json.dumps(entry)
        # The e2e runner empties its output directory (frontend/e2e/.output) once the run starts, after this server
        # is up: the directory is made again on every write, so a log placed there survives the wipe (S72's gate).
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with lock, path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(line + "\n")
        except OSError as e:  # the record is the test's, the answer the viewer's: a failed write never costs the answer
            print(f"galaxy.api: source log {path} unwritable: {e}", file=sys.stderr)
        return response

    return logged


def main() -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("GALAXY_HOST", HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", PORT)))
    parser.add_argument(
        "--client",
        type=Path,
        default=Path(os.environ.get("GALAXY_CLIENT", CLIENT)),
        help="directory of viewer files to serve at / (default: interface/)",
    )
    parser.add_argument(
        "--bundles",
        type=Path,
        default=Path(os.environ["GALAXY_BUNDLES"]) if os.environ.get("GALAXY_BUNDLES") else None,
        help="directory of template bundles (tools/export_template.py) to answer from; default $GALAXY_BUNDLES or none",
    )
    parser.add_argument(
        "--source-log",
        type=Path,
        default=Path(os.environ["GALAXY_SOURCE_LOG"]) if os.environ.get("GALAXY_SOURCE_LOG") else None,
        help="append one JSON line per request (path, status, source, bytes): the picture test's record of which "
        "answers came from a bundle; default $GALAXY_SOURCE_LOG or none",
    )
    parser.add_argument("--verbose", action="store_true", help="log every request")
    args = parser.parse_args()

    if not (args.client / "index.html").is_file():
        parser.error(f"--client {args.client} has no index.html")
    try:
        service = Service(client=args.client, bundles=args.bundles)
    except BundleError as e:  # a bundle from another model is a startup failure, not a fallback (BUILD_IV 2b)
        print(f"galaxy.api: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if args.source_log is not None:
        service.handle = _logged(service.handle, args.source_log)  # the instance's own: the handler calls it
    viewer = content_hash(service.client)
    print(f"viewer {args.client}: {viewer['hash']} ({viewer['count']} files, {viewer['bytes']} B)")
    if service.bundles is None:
        print(f"model {service.model_hash}; no bundles")
    else:
        held = ", ".join(f"{b['template']}/{b['layer']} {b['entries']}" for b in service.bundles.bundles) or "none found"
        print(f"model {service.model_hash}; bundles {args.bundles}: {len(service.bundles)} entries ({held})")
    serve(args.host, args.port, service, quiet=not args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
