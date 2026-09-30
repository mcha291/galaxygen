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

A POST is the same request with its query in the body (S42): a form-encoded body
is appended to the URL's query and handled exactly as a GET. It exists because
``/api/render`` carries the viewer's filter curves, and a named instrument's
sampled curves make a query of tens of kilobytes — past what a proxy in front of
a deployment may accept on a request line. Nothing is written by a POST.

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
# The largest POST body taken (S42): a request's query, not an upload. Three sampled curves of 241 points
# are about 20 KB; a thousand-point set of four about 90 KB.
MAX_BODY = 1 << 20
FORM = "application/x-www-form-urlencoded"


class Handler(BaseHTTPRequestHandler):
    server_version = "galaxygen"
    protocol_version = "HTTP/1.1"
    service: Service
    quiet: bool = True

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler's spelling)
        parts = urlsplit(self.path)
        self._answer(parts.path, parts.query)

    def do_POST(self) -> None:  # noqa: N802
        parts = urlsplit(self.path)
        length = self.headers.get("Content-Length")
        kind = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        refusal = None
        if length is None or not length.isdigit():
            refusal = (411, "a POST carries its query as a body with a Content-Length")
        elif int(length) > MAX_BODY:
            refusal = (413, f"a POST body is a query of at most {MAX_BODY} bytes")
        elif kind != FORM:
            refusal = (415, f"a POST body is {FORM}, the query a GET would carry")
        if refusal is not None:
            self.close_connection = True
            body = json.dumps({"error": refusal[1]}).encode("utf-8")
            self._send(Response(refusal[0], JSON, body))
            return
        try:
            extra = self.rfile.read(int(length)).decode("ascii")
        except UnicodeDecodeError:
            self._send(Response(400, JSON, json.dumps({"error": "a form-encoded body is ASCII"}).encode("utf-8")))
            return
        self._answer(parts.path, "&".join(q for q in (parts.query, extra) if q))

    def _answer(self, path: str, query: str) -> None:
        try:
            response = self.service.handle(path, query)
        except Exception as e:  # pragma: no cover - a bug in a handler, not a bad request
            print(f"galaxy.api: {type(e).__name__}: {e}", file=sys.stderr)
            body = json.dumps({"error": "internal error", "type": type(e).__name__}).encode("utf-8")
            response = Response(500, JSON, body)
        try:
            self._send(response)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # The viewer aborted the request (its view moved on before the answer came): the
            # answer has nowhere to go, and a traceback for that is not an error report.
            pass

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
