"""``python -m galaxy.api``: serve the API, print where it is and what it is serving.

In a container the host, port and viewer directory come from the environment
(``GALAXY_HOST``, ``PORT``, ``GALAXY_CLIENT``), so the image serves the built
frontend on ``0.0.0.0`` without a different entry point.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from galaxy.api.http import HOST, PORT, serve
from galaxy.api.service import Service
from galaxy.api.version import CLIENT, content_hash
from galaxy.specs import utf8_stdout


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
    parser.add_argument("--verbose", action="store_true", help="log every request")
    args = parser.parse_args()

    if not (args.client / "index.html").is_file():
        parser.error(f"--client {args.client} has no index.html")
    service = Service(client=args.client)
    viewer = content_hash(service.client)
    print(f"viewer {args.client}: {viewer['hash']} ({viewer['count']} files, {viewer['bytes']} B)")
    serve(args.host, args.port, service, quiet=not args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
