"""The stdlib server that adapts :mod:`galaxy.api.service` to HTTP.

Thin on purpose: everything worth testing is in the service, which is a pure
function of ``(path, query)``, and this module adds a socket. What it does add
is the two headers that matter.

- ``Cache-Control: no-store``. A viewer that renders a cached response while
  asking whether it is running the new code has answered its own question wrong
  (rule B2, D3). Nothing this server returns is cacheable by anyone.
- ``X-Galaxy-Stages``. Every response says which stages it ran, so rule D4 is
  answerable from outside the process and from a browser's network panel — a
  metadata endpoint that touched a stage cannot hide behind being fast.

    uv run python -m galaxy.api --port 8000
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from galaxy.api.service import JSON, Response, Service

HOST = "127.0.0.1"  # headless and local: S7 decides what a deployed viewer needs
PORT = 8017


class Handler(BaseHTTPRequestHandler):
    server_version = "galaxygen"
    protocol_version = "HTTP/1.1"
    service: Service
    quiet: bool = True

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler's spelling)
        parts = urlsplit(self.path)
        try:
            response = self.service.handle(parts.path, parts.query)
        except Exception as e:  # pragma: no cover - a bug in a handler, not a bad request
            print(f"galaxy.api: {type(e).__name__}: {e}", file=sys.stderr)
            body = json.dumps({"error": "internal error", "type": type(e).__name__}).encode("utf-8")
            response = Response(500, JSON, body)
        self._send(response)

    def do_HEAD(self) -> None:  # noqa: N802
        parts = urlsplit(self.path)
        response = self.service.handle(parts.path, parts.query)
        self._send(response, body=False)

    def _send(self, response: Response, body: bool = True) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.media)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Galaxy-Stages", ",".join(response.stages))
        self.end_headers()
        if body:
            self.wfile.write(response.body)

    def log_message(self, fmt: str, *args: Any) -> None:
        if not self.quiet:
            super().log_message(fmt, *args)


def make_server(host: str = HOST, port: int = PORT, service: Service | None = None, quiet: bool = True) -> ThreadingHTTPServer:
    """A bound, not-yet-serving server. ``port=0`` picks a free one, which tests want."""
    handler = type("BoundHandler", (Handler,), {"service": service or Service(), "quiet": quiet})
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str = HOST, port: int = PORT, service: Service | None = None, quiet: bool = True) -> None:
    httpd = make_server(host, port, service, quiet)
    bound = httpd.server_address
    print(f"galaxy.api on http://{bound[0]}:{bound[1]}/api")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
