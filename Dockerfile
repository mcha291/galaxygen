# galaxygen: the API and the built frontend in one image, one origin.
#
#   docker build -t galaxygen .            (locally, if Docker is installed)
#   az acr build -r <registry> -t galaxygen:<tag> .   (in Azure, no local Docker)
#
# Stage 1 builds frontend/ into static files. It needs interface/ beside it: the
# app imports transport.js, ramp.js and friends from there, and Vite bundles them.

FROM node:24-slim AS frontend
WORKDIR /src
COPY interface/ interface/
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build

# Stage 2 runs the model. uv installs exactly what uv.lock pins (no dev group).

FROM python:3.14-slim AS runtime
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY model/ model/
RUN uv sync --frozen --no-dev

COPY --from=frontend /src/frontend/dist /app/web

# The template bundles (S72, BUILD_IV W2): every answer the viewer asks of each template, computed here by the model
# this image runs, so the bundles' hash is always the image's own ("a template's bundle can never be older than the
# model that serves it", BUILD_IV 2b) and the server refuses them at startup if it were not. The default scope: what
# the viewer asks at galaxy scale, both templates, both layer settings (nothing below 4 kpc; per-cell levels are the
# owner's ruling). BUNDLES=0 builds an image without them (an empty directory: every request is computed, as before).
ARG BUNDLES=1
COPY frontend/src/galaxy/filters.json frontend/src/galaxy/instruments.json frontend/src/galaxy/
COPY tools/export_template.py tools/
RUN if [ "$BUNDLES" = "1" ]; then \
      /app/.venv/bin/python tools/export_template.py --out /app/bundles; \
    else mkdir -p /app/bundles; fi

# galaxy.api reads these; Container Apps sends traffic to PORT.
ENV GALAXY_HOST=0.0.0.0 PORT=8000 GALAXY_CLIENT=/app/web GALAXY_BUNDLES=/app/bundles PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

RUN useradd --system --uid 10001 galaxy
USER galaxy

CMD ["python", "-m", "galaxy.api"]
