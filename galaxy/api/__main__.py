"""``python -m galaxy.api``: serve the API, print where it is and what it is serving."""

from __future__ import annotations

import argparse

from galaxy.api.http import HOST, PORT, serve
from galaxy.api.service import Service
from galaxy.api.version import content_hash
from galaxy.specs import utf8_stdout


def main() -> int:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--verbose", action="store_true", help="log every request")
    args = parser.parse_args()

    service = Service()
    viewer = content_hash(service.client)
    print(f"viewer bytes: {viewer['hash']} ({viewer['count']} files, {viewer['bytes']} B)")
    serve(args.host, args.port, service, quiet=not args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
