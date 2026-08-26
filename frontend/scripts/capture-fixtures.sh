#!/usr/bin/env bash
#
# Captures live API responses into the gzipped fixtures the mock servers serve.
#
# There was no tooling for this: every `__mocks__/gzipped/**/*.json.gz` was a
# hand-run `curl | gzip`, which is why they drifted behind the API. Six by hand
# now and six more every time a shape changes is not sustainable - and a stale
# fixture does not fail loudly, it makes a page test render the empty state and
# pass vacuously.
#
# Usage:
#   scripts/capture-fixtures.sh                       # everything below
#   scripts/capture-fixtures.sh markets exchange-rate # named groups only
#
# Environment:
#   API_BASE_URL      Defaults to http://localhost/api (the nginx proxy).
#   MARKET_IDS        Space-separated market UUIDs. Defaults to every id in the
#                     freshly captured markets list.
#   LISTING_IDS       Space-separated listing UUIDs to capture overviews for.
#   PROPERTY_IDS      Space-separated property UUIDs. Defaults to every id in
#                     the freshly captured properties list.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURE_DIR="$FRONTEND_DIR/__mocks__/gzipped"

API_BASE_URL="${API_BASE_URL:-http://localhost/api}"
MARKET_IDS="${MARKET_IDS:-}"
LISTING_IDS="${LISTING_IDS:-}"
PROPERTY_IDS="${PROPERTY_IDS:-}"

log() { printf '%s\n' "$*" >&2; }

# Writes one endpoint's response to one fixture path.
#
# The response is validated as JSON before anything is written: a 500's HTML
# error page gzips just as happily as a payload, and a fixture full of markup
# fails at read time in a test with no hint of where it came from.
capture() {
  local endpoint="$1"
  local fixture_rel_path="$2"
  local fixture_path="$FIXTURE_DIR/$fixture_rel_path"
  local url="$API_BASE_URL/$endpoint"

  local body
  local status
  body="$(curl --silent --show-error --write-out '\n%{http_code}' "$url")" || {
    log "  ✗ $endpoint - request failed"
    return 1
  }

  status="$(printf '%s' "$body" | tail -n 1)"
  body="$(printf '%s' "$body" | sed '$d')"

  if [[ "$status" != "200" ]]; then
    log "  ✗ $endpoint - HTTP $status"
    return 1
  fi

  if ! printf '%s' "$body" | python3 -m json.tool > /dev/null 2>&1; then
    log "  ✗ $endpoint - response was not JSON"
    return 1
  fi

  mkdir -p "$(dirname "$fixture_path")"
  printf '%s' "$body" | gzip --no-name > "$fixture_path"
  log "  ✓ $fixture_rel_path"
}

fetch_ids() {
  curl --silent --show-error "$API_BASE_URL/$1" |
    python3 -c 'import json,sys; print(" ".join(row["id"] for row in json.load(sys.stdin)["data"]))'
}

capture_home() {
  log "home"
  capture "home/listings/highest-earners" \
    "home/listings/highest-earners/highest-earners__data.json.gz"
  capture "home/listings/newest" "home/listings/newest/newest__data.json.gz"
}

capture_markets() {
  log "markets"
  capture "markets" "markets/list__data.json.gz"

  local ids="$MARKET_IDS"
  if [[ -z "$ids" ]]; then
    ids="$(fetch_ids markets)"
  fi

  for market_id in $ids; do
    capture "markets/$market_id" "markets/${market_id}__data.json.gz"
  done
}

capture_listings() {
  log "listings"
  for listing_id in $LISTING_IDS; do
    capture "listings/$listing_id" "listings/${listing_id}__data.json.gz"
  done
}

capture_exchange_rate() {
  log "exchange-rate"
  capture "exchange-rate" "exchange-rate/list__data.json.gz"
}

capture_properties() {
  log "properties"
  capture "properties" "properties/list__data.json.gz"

  local ids="$PROPERTY_IDS"
  if [[ -z "$ids" ]]; then
    ids="$(fetch_ids properties)"
  fi

  for property_id in $ids; do
    capture "properties/$property_id" "properties/${property_id}__data.json.gz"
    capture "properties/$property_id/report" \
      "properties/report/${property_id}__data.json.gz"
    # Deliberately the cached route for both: capturing `/comps` spends an
    # AirROI call per property, and the two serve the same shape.
    capture "properties/$property_id/comps/cached" \
      "properties/comps/cached/${property_id}__data.json.gz"
    capture "properties/$property_id/comps/cached" \
      "properties/comps/${property_id}__data.json.gz"
  done
}

GROUPS=("$@")
if [[ ${#GROUPS[@]} -eq 0 ]]; then
  GROUPS=(home markets listings exchange-rate properties)
fi

log "Capturing fixtures from $API_BASE_URL into $FIXTURE_DIR"

for group in "${GROUPS[@]}"; do
  case "$group" in
    home) capture_home ;;
    markets) capture_markets ;;
    listings) capture_listings ;;
    exchange-rate) capture_exchange_rate ;;
    properties) capture_properties ;;
    *)
      log "Unknown fixture group '$group'"
      exit 1
      ;;
  esac
done

log "Done."
log ""
log "NOTE: POST fixtures - properties/created__data.json.gz and"
log "properties/analyze/<id>__data.json.gz - are not captured here. Creating a"
log "property and analysing it both write rows and spend AirROI calls, so they"
log "are copied by hand from a run you actually meant to make."
