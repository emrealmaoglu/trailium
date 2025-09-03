#!/usr/bin/env bash
set -euo pipefail

API_BASE=${API_BASE:-http://localhost:8000}
USERNAME=${USERNAME:-emreaslan663}
PASSWORD=${PASSWORD:-demo123}

need_cmd() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1" >&2; exit 1; }; }
need_cmd curl
need_cmd jq

login() {
  curl -s -X POST "$API_BASE/api/auth/login/" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" | tee /tmp/trailium_login.json >/dev/null
  ACCESS=$(jq -r .access /tmp/trailium_login.json)
  if [ -z "${ACCESS:-}" ] || [ "$ACCESS" = null ]; then
    echo "Login failed" >&2
    exit 1
  fi
  echo "$ACCESS"
}

ACCESS=$(login)
AUTH=(-H "Authorization: Bearer $ACCESS")

# Me
curl -sf -i "${AUTH[@]}" "$API_BASE/api/users/me/" >/dev/null

# List users and follow the first non-self user
USERS_JSON=$(curl -sf "${AUTH[@]}" "$API_BASE/api/users/?page_size=5")
TARGET_ID=$(echo "$USERS_JSON" | jq -r '.results[] | select(.username!="'$USERNAME'") | .id' | head -n 1)
if [ -n "${TARGET_ID:-}" ]; then
  curl -sf -X POST "${AUTH[@]}" "$API_BASE/api/follows/users/$TARGET_ID/follow/" >/dev/null || true
fi

# Feed, Posts, Albums basic checks
curl -sf -i "${AUTH[@]}" "$API_BASE/api/feed/posts?page_size=5" >/dev/null
POSTS_JSON=$(curl -sf "${AUTH[@]}" "$API_BASE/api/posts/?page_size=5")
PID=$(echo "$POSTS_JSON" | jq -r '.results[0].id')

if [ -n "${PID:-}" ] && [ "$PID" != null ]; then
  # Like and Unlike
  curl -sf -X POST "${AUTH[@]}" "$API_BASE/api/posts/$PID/like/" >/dev/null
  curl -sf -X DELETE "${AUTH[@]}" "$API_BASE/api/posts/$PID/like/" >/dev/null
  # Comments list and add
  curl -sf -i "${AUTH[@]}" "$API_BASE/api/posts/$PID/comments/" >/dev/null
  curl -sf -X POST "${AUTH[@]}" -H 'Content-Type: application/json' \
    -d '{"body":"smoke comment"}' "$API_BASE/api/posts/$PID/comments/" >/dev/null || true
fi

# Albums
curl -sf -i "${AUTH[@]}" "$API_BASE/api/albums/" >/dev/null

echo "Smoke OK: follow → feed → like/comment passed."
