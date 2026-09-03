"""The API: metadata as JSON, arrays as bytes, and no rendering (GALAXY_PLAN.md §5b, S6).

Headless and fully tested, which is why it is a session of its own: everything
here is checkable without a browser, and S7 inherits a surface that already
holds rather than one discovered to be wrong while rendering against it.

**What it publishes.** Stage declarations and their checkpoints, field
declarations, the input registry, arrays by field name, a materialised star
catalogue for a region, and a content hash of the viewer's own bytes. Nothing
about model internals: no constants, no stage source, no intermediate the
declarations do not name (rule D5).

**The one rendering opinion travels with the field** (rule A9). A ramp reaches
the viewer inside the field declaration that computed it and nowhere else. The
API does not invent one, does not carry a default table, and has no opinion to
lose track of.

**No endpoint runs more of the pipeline than its answer requires** (rule D4).
This is the session's real work rather than a checkbox, and it is structural:
metadata is answered from declarations, which no stage has to run to produce;
an array request executes the dependency closure above the fields asked for
(``run(..., only=…)``); a region query runs what ``systems.materialise`` reads
and *not the systems stage itself*, so asking for a thousand stars in one
sector does not build the galaxy's whole catalogue first. Every response says
which stages it ran, and the assertion in ``tests/test_api.py`` reads that
rather than a stopwatch — a check against a warm cache would pass whatever the
endpoint did (rule B2, GALAXY_PLAN.md §7 risk 5).

Layout:

    wire.py      the binary framing: one JSON header, arrays packed behind it
    version.py   content hashes of the client bytes and of the API's own
    service.py   the routes, as pure functions of (path, query) -> Response
    http.py      the stdlib server that adapts them; ``python -m galaxy.api``
    client/      what the browser imports; transport.js holds the one fetch (D2)
"""

from galaxy.api.service import Response, Service, routes
from galaxy.api.version import content_hash

__all__ = ["Response", "Service", "routes", "content_hash"]
