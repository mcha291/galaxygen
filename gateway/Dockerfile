# The gateway image (BUILD_IV Phase W4): the built frontend and the .NET gateway, one container, port 8080.
# Build from the repository root, because the frontend needs interface/ beside it:
#
#   docker build -f gateway/Dockerfile -t galaxygen-gateway .
#
# The Python model is its own image (Dockerfile.model at the root) and is reached at Gateway__Model__BaseUrl.
# Published untrimmed (trimming is a later step). .github/workflows/image.yml builds, smoke-tests and pushes it.
# No template bundle is copied here: since S72 the model answers a bundled request itself (S74, D-3).

FROM node:24-slim AS frontend
WORKDIR /src
COPY interface/ interface/
COPY frontend/package.json frontend/package-lock.json frontend/.npmrc frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY gateway/ gateway/
RUN dotnet publish gateway/Galaxygen.Gateway/Galaxygen.Gateway.csproj -c Release -o /app/publish \
    -p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
COPY --from=frontend /src/frontend/dist /app/web
ENV ASPNETCORE_URLS=http://+:8080 \
    Gateway__Frontend__Path=/app/web
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "Galaxygen.Gateway.dll"]
