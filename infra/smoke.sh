#!/usr/bin/env bash
# The two images' smoke test (BUILD_IV Phase W4): run them together as the deployment will, and fail loudly on
# anything the deployment relies on. CI runs it between the build and the push (.github/workflows/image.yml); the
# owner can run it once Docker exists locally:
#
#   docker build -f Dockerfile.model -t galaxygen-model:smoke .
#   docker build -f gateway/Dockerfile -t galaxygen-gateway:smoke .
#   bash infra/smoke.sh galaxygen-model:smoke galaxygen-gateway:smoke
#
# What it shows: the bundles inside the model image carry the model.hash the running image publishes (else the
# server would refuse them, and the pin would be wrong); the landing's first answers come from the bundles; the
# gateway pinned to that hash is healthy, serves a bundled answer as a miss and then as a hit with the same bytes,
# and the hit asks the model nothing (its request log does not grow); a gateway pinned to another hash reports 503
# at /healthz once a request reaches the model. The hash goes to $GITHUB_OUTPUT as model_hash for the image label.
# Needs docker, curl, jq, sha256sum.

set -euo pipefail

MODEL_IMAGE=${1:?usage: smoke.sh MODEL_IMAGE GATEWAY_IMAGE}
GATEWAY_IMAGE=${2:?usage: smoke.sh MODEL_IMAGE GATEWAY_IMAGE}
NET=galaxygen-smoke
MODEL=galaxygen-smoke-model
GW=galaxygen-smoke-gateway
GW2=galaxygen-smoke-wrongpin
MODEL_URL=http://127.0.0.1:18000
GW_URL=http://127.0.0.1:18080
GW2_URL=http://127.0.0.1:18081
WORK=$(mktemp -d)

cleanup() {
  docker rm -f "$MODEL" "$GW" "$GW2" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
  rm -rf "$WORK"
}
trap cleanup EXIT

fail() {
  echo "SMOKE FAIL: $*" >&2
  for c in "$MODEL" "$GW" "$GW2"; do
    if docker inspect "$c" >/dev/null 2>&1; then
      echo "--- last log lines of $c" >&2
      docker logs --tail 40 "$c" >&2 2>&1 || true
    fi
  done
  exit 1
}

# get NAME URL: the body to $WORK/NAME, the headers to $WORK/NAME.h (CR stripped); prints the status and the time.
get() {
  local name=$1 url=$2 out
  out=$(curl -sS -g -o "$WORK/$name" -D "$WORK/$name.raw" -w '%{http_code} %{time_total}' "$url") || fail "curl $url"
  tr -d '\r' <"$WORK/$name.raw" >"$WORK/$name.h"
  local code=${out% *} secs=${out#* }
  printf '%-28s %s %8.0f ms %10s B  %s\n' "$name" "$code" "$(awk -v s="$secs" 'BEGIN { print s * 1000 }')" \
    "$(stat -c %s "$WORK/$name")" "${url:0:110}"
  echo "$code" >"$WORK/$name.code"
}
code() { cat "$WORK/$1.code"; }
header() { grep -i "^$2:" "$WORK/$1.h" | head -1 | cut -d: -f2- | sed 's/^ *//' || true; }
expect_header() {
  local got
  got=$(header "$1" "$2")
  [ "$got" = "$3" ] || fail "$1: $2 is '$got', expected '$3'"
}
model_lines() { docker logs "$MODEL" 2>&1 | wc -l; }

# wait_for URL SECONDS: until the URL answers at all (any status).
wait_for() {
  local url=$1 limit=$2 t=0
  until curl -s -o /dev/null "$url"; do
    t=$((t + 2))
    [ "$t" -le "$limit" ] || fail "$url did not answer in $limit s"
    sleep 2
  done
  echo "up after ~$t s: $url"
}

docker network create "$NET" >/dev/null

# --- The model, as Container Apps runs it (the image's own environment, --verbose for the request log) ---------
docker run -d --name "$MODEL" --network "$NET" --network-alias model -p 18000:8000 "$MODEL_IMAGE" \
  python -m galaxy.api --verbose >/dev/null
wait_for "$MODEL_URL/api" 600

get version "$MODEL_URL/api/version"
[ "$(code version)" = 200 ] || fail "/api/version answered $(code version)"
HASH=$(jq -r '.model.hash // empty' "$WORK/version")
[[ "$HASH" =~ ^[0-9a-f]{32}$ ]] || fail "/api/version's model.hash is '$HASH', not 32 hex"
echo "live model.hash $HASH"

# Every bundle manifest in the image must carry the live hash.
mkdir -p "$WORK/manifests"
manifests=$(docker exec "$MODEL" find /app/bundles -name manifest.json | sort)
[ -n "$manifests" ] || fail "no manifest under /app/bundles"
n=0
for m in $manifests; do
  n=$((n + 1))
  docker cp "$MODEL:$m" "$WORK/manifests/$n.json" >/dev/null
  built=$(jq -r '.model_hash' "$WORK/manifests/$n.json")
  printf '  %-44s model_hash %s  entries %s\n' "$m" "$built" "$(jq '.entries | length' "$WORK/manifests/$n.json")"
  [ "$built" = "$HASH" ] || fail "$m was built from $built, the live model is $HASH"
done
echo "all $n manifests carry the live hash"

# The landing's first answers. /api/version is never bundled; /api/templates and the two picked below are. The
# picks are the Milky Way bundle's (layer on) smallest render and its layer tables, in the viewer's own spelling as
# the manifest records it, and short enough for a GET line through Kestrel.
MW=$(docker exec "$MODEL" find /app/bundles -path '*/milky_way/on/manifest.json')
docker cp "$MODEL:$MW" "$WORK/mw.json" >/dev/null
RENDER_Q=$(jq -r '[.entries[] | select(.route == "/api/render" and (.query | length) < 4000)] | sort_by(.bytes) | .[0].query // empty' "$WORK/mw.json")
LAYER_Q=$(jq -r '[.entries[] | select(.route == "/api/layer" and (.query | length) < 4000)] | sort_by(.bytes) | .[0].query // empty' "$WORK/mw.json")
[ -n "$RENDER_Q" ] || fail "no short /api/render entry in $MW"
[ -n "$LAYER_Q" ] || fail "no short /api/layer entry in $MW"

get templates "$MODEL_URL/api/templates"
get render "$MODEL_URL/api/render?$RENDER_Q"
get layer "$MODEL_URL/api/layer?$LAYER_Q"
for r in templates render layer; do
  [ "$(code $r)" = 200 ] || fail "$r answered $(code $r)"
  expect_header "$r" X-Galaxy-Source bundle
done
RENDER_SHA=$(sha256sum "$WORK/render" | cut -d' ' -f1)
echo "the model answered templates, render and layer from its bundles (render sha256 $RENDER_SHA)"

# --- The gateway pinned to the live hash, as the Bicep configures it (forwarded headers off: no ingress here) ---
docker run -d --name "$GW" --network "$NET" -p 18080:8080 \
  -e Gateway__Model__BaseUrl=http://model:8000 \
  -e Gateway__Model__ContentHash="$HASH" \
  -e Gateway__Limits__TrustForwardedFor=false \
  "$GATEWAY_IMAGE" >/dev/null
wait_for "$GW_URL/healthz" 120
get healthz "$GW_URL/healthz"
[ "$(code healthz)" = 200 ] || fail "gateway /healthz answered $(code healthz)"
[ "$(jq -r '.pinned' "$WORK/healthz")" = true ] || fail "gateway not pinned: $(cat "$WORK/healthz")"
[ "$(jq -r '.pin_mismatch' "$WORK/healthz")" = false ] || fail "gateway pin mismatch: $(cat "$WORK/healthz")"
[ "$(jq -r '.frontend' "$WORK/healthz")" = true ] || fail "gateway found no frontend: $(cat "$WORK/healthz")"

get gw_index "$GW_URL/"
[ "$(code gw_index)" = 200 ] || fail "gateway / answered $(code gw_index)"

get gw_render_1 "$GW_URL/api/render?$RENDER_Q"
[ "$(code gw_render_1)" = 200 ] || fail "gateway render answered $(code gw_render_1)"
expect_header gw_render_1 X-Gateway-Cache miss
expect_header gw_render_1 X-Galaxy-Source bundle
sleep 1 # the log driver's copy of the miss's lines
before=$(model_lines)
get gw_render_2 "$GW_URL/api/render?$RENDER_Q"
sleep 1
after=$(model_lines)
[ "$(code gw_render_2)" = 200 ] || fail "gateway render (again) answered $(code gw_render_2)"
expect_header gw_render_2 X-Gateway-Cache hit
SHA1=$(sha256sum "$WORK/gw_render_1" | cut -d' ' -f1)
SHA2=$(sha256sum "$WORK/gw_render_2" | cut -d' ' -f1)
[ "$SHA1" = "$RENDER_SHA" ] || fail "the gateway's miss ($SHA1) is not the model's bytes ($RENDER_SHA)"
[ "$SHA2" = "$RENDER_SHA" ] || fail "the gateway's hit ($SHA2) is not the model's bytes ($RENDER_SHA)"
echo "model log lines before the hit $before, after $after"
[ "$before" = "$after" ] || fail "the model logged $((after - before)) line(s) during a cache hit"

# The first miss made the gateway compare its pin with the live hash: still pinned, no mismatch.
get healthz_after "$GW_URL/healthz"
[ "$(code healthz_after)" = 200 ] || fail "gateway /healthz after a model contact answered $(code healthz_after)"
[ "$(jq -r '.pinned' "$WORK/healthz_after")" = true ] || fail "pin dropped: $(cat "$WORK/healthz_after")"

# --- A gateway pinned to another hash: healthy until a request reaches the model, then 503 -------------------
WRONG=$(printf '%s' "$HASH" | tr '0-9a-f' '1-9a-f0') # every character moved one on: never the live hash
docker run -d --name "$GW2" --network "$NET" -p 18081:8080 \
  -e Gateway__Model__BaseUrl=http://model:8000 \
  -e Gateway__Model__ContentHash="$WRONG" \
  -e Gateway__Limits__TrustForwardedFor=false \
  "$GATEWAY_IMAGE" >/dev/null
wait_for "$GW2_URL/healthz" 120
get wrong_healthz "$GW2_URL/healthz"
[ "$(code wrong_healthz)" = 200 ] || fail "wrong-pin gateway answered $(code wrong_healthz) before any model contact"
get wrong_templates "$GW2_URL/api/templates" # an empty cache: this one reaches the model and checks the pin
get wrong_healthz_after "$GW2_URL/healthz"
[ "$(code wrong_healthz_after)" = 503 ] || fail "wrong-pin gateway /healthz answered $(code wrong_healthz_after), expected 503"
[ "$(jq -r '.pin_mismatch' "$WORK/wrong_healthz_after")" = true ] || fail "no pin_mismatch: $(cat "$WORK/wrong_healthz_after")"
echo "the wrong pin $WRONG: /healthz 503 with pin_mismatch after one model contact"

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "model_hash=$HASH" >>"$GITHUB_OUTPUT"
fi
echo "SMOKE OK: model.hash $HASH"
