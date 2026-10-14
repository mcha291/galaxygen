# The gateway image (BUILD_IV Phase W4): the built frontend and the .NET gateway, one container, port 8080.
# Build from the repository root, because the frontend needs interface/ beside it:
#
#   docker build -f gateway/Dockerfile -t galaxygen-gateway .
#
# The Python model is its own image (the root Dockerfile) and is reached at Gateway__Model__BaseUrl.
# W2's template bundles are copied in at /app/bundles once the export tool exists (TODO(W2)).

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
    Gateway__Frontend__Path=/app/web \
    Gateway__Bundles__Path=/app/bundles
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "Galaxygen.Gateway.dll"]
