#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}PASS${NC} - $1"; }
fail(){ echo -e "${RED}FAIL${NC} - $1"; }
note(){ echo -e "${YELLOW}NOTE${NC} - $1"; }

BASE="${BASE_URL:-http://127.0.0.1:8000}"
U1="tester1"; P1="Test1234!"; E1="tester1@example.com"
U2="tester2"; P2="Test1234!"; E2="tester2@example.com"

step(){ echo -e "\n==== $1 ===="; }

step "Auth: register"
REG=$(curl -s -o /tmp/reg.json -w "%{http_code}" -X POST "$BASE/api/auth/register/" -H 'Content-Type: application/json' --data "{\"username\":\"$U1\",\"password\":\"$P1\",\"email\":\"$E1\"}") || true
if [[ "$REG" =~ ^20 ]]; then pass "register ($REG)"; else fail "register ($REG)"; fi

step "Auth: login"
HTTP=$(curl -s -o /tmp/login.json -w "%{http_code}" -X POST "$BASE/api/auth/login/" -H 'Content-Type: application/json' --data "{\"username\":\"$U1\",\"password\":\"$P1\"}")
ACCESS=$(jq -r .access /tmp/login.json 2>/dev/null || echo "")
REFRESH=$(jq -r .refresh /tmp/login.json 2>/dev/null || echo "")
[[ "$HTTP" == "200" && -n "$ACCESS" && -n "$REFRESH" ]] && pass "login" || fail "login ($HTTP)"

step "Auth: me"
HTTP=$(curl -s -o /tmp/me.json -w "%{http_code}" "$BASE/api/users/me/" -H "Authorization: Bearer $ACCESS")
[[ "$HTTP" == "200" ]] && pass "me" || fail "me ($HTTP)"

step "Auth: refresh"
HTTP=$(curl -s -o /tmp/refresh.json -w "%{http_code}" -X POST "$BASE/api/auth/refresh/" -H 'Content-Type: application/json' --data "{\"refresh\":\"$REFRESH\"}")
NEW_ACCESS=$(jq -r .access /tmp/refresh.json 2>/dev/null || echo "")
[[ "$HTTP" == "200" && -n "$NEW_ACCESS" ]] && pass "refresh" || fail "refresh ($HTTP)"

step "Auth: logout (blacklist refresh)"
HTTP=$(curl -s -o /tmp/logout.json -w "%{http_code}" -X POST "$BASE/api/auth/logout/" -H 'Content-Type: application/json' --data "{\"refresh\":\"$REFRESH\"}") || true
[[ "$HTTP" =~ ^20|205$ ]] && pass "logout" || note "logout not implemented ($HTTP)"

step "Auth: negative"
HTTP=$(curl -s -o /tmp/me401.json -w "%{http_code}" "$BASE/api/users/me/")
[[ "$HTTP" == "401" ]] && pass "me without token -> 401" || fail "me without token ($HTTP)"
HTTP=$(curl -s -o /tmp/l401.json -w "%{http_code}" "$BASE/api/todos/lists/")
[[ "$HTTP" == "401" ]] && pass "lists without token -> 401" || fail "lists without token ($HTTP)"

step "Todos: create list"
HTTP=$(curl -s -o /tmp/list.json -w "%{http_code}" -X POST "$BASE/api/todos/lists/" -H 'Content-Type: application/json' -H "Authorization: Bearer $NEW_ACCESS" --data '{"name":"Work","description":"Daily","kind":"work"}')
LIST_ID=$(jq -r .id /tmp/list.json)
[[ "$HTTP" == "201" && "$LIST_ID" != "null" ]] && pass "create list" || fail "create list ($HTTP)"

step "Todos: create items"
HTTP=$(curl -s -o /tmp/item1.json -w "%{http_code}" -X POST "$BASE/api/todos/items/" -H 'Content-Type: application/json' -H "Authorization: Bearer $NEW_ACCESS" --data "{\"list\":$LIST_ID,\"title\":\"Task A\"}")
I1=$(jq -r .id /tmp/item1.json)
[[ "$HTTP" == "201" && "$I1" != "null" ]] && pass "create item1" || fail "create item1 ($HTTP)"
HTTP=$(curl -s -o /tmp/item2.json -w "%{http_code}" -X POST "$BASE/api/todos/items/" -H 'Content-Type: application/json' -H "Authorization: Bearer $NEW_ACCESS" --data "{\"list\":$LIST_ID,\"title\":\"Task B\"}")
I2=$(jq -r .id /tmp/item2.json)
[[ "$HTTP" == "201" && "$I2" != "null" ]] && pass "create item2" || fail "create item2 ($HTTP)"

step "Todos: create subitems"
HTTP=$(curl -s -o /tmp/sub1.json -w "%{http_code}" -X POST "$BASE/api/todos/subitems/" -H 'Content-Type: application/json' -H "Authorization: Bearer $NEW_ACCESS" --data "{\"parent\":$I1,\"title\":\"Sub A1\"}")
S11=$(jq -r .id /tmp/sub1.json)
[[ "$HTTP" == "201" && "$S11" != "null" ]] && pass "create sub1" || fail "create sub1 ($HTTP)"
HTTP=$(curl -s -o /tmp/sub2.json -w "%{http_code}" -X POST "$BASE/api/todos/subitems/" -H 'Content-Type: application/json' -H "Authorization: Bearer $NEW_ACCESS" --data "{\"parent\":$I1,\"title\":\"Sub A2\"}")
S12=$(jq -r .id /tmp/sub2.json)
[[ "$HTTP" == "201" && "$S12" != "null" ]] && pass "create sub2" || fail "create sub2 ($HTTP)"

step "Todos: toggle item"
HTTP=$(curl -s -o /tmp/toggle.json -w "%{http_code}" -X POST "$BASE/api/todos/items/$I1/toggle-done/" -H "Authorization: Bearer $NEW_ACCESS")
[[ "$HTTP" == "200" ]] && pass "toggle item" || fail "toggle item ($HTTP)"

step "Todos: verify progress"
HTTP=$(curl -s -o /tmp/listget.json -w "%{http_code}" "$BASE/api/todos/lists/$LIST_ID/" -H "Authorization: Bearer $NEW_ACCESS")
PCT=$(jq -r .progress_cached /tmp/listget.json)
[[ "$HTTP" == "200" && "$PCT" != "null" ]] && pass "list progress ($PCT%)" || fail "list progress ($HTTP)"

step "Perms: second user cannot see first user data"
curl -s -o /tmp/reg2.json -w "%{http_code}" -X POST "$BASE/api/auth/register/" -H 'Content-Type: application/json' --data "{\"username\":\"$U2\",\"password\":\"$P2\",\"email\":\"$E2\"}" >/dev/null
HTTP=$(curl -s -o /tmp/login2.json -w "%{http_code}" -X POST "$BASE/api/auth/login/" -H 'Content-Type: application/json' --data "{\"username\":\"$U2\",\"password\":\"$P2\"}")
ACC2=$(jq -r .access /tmp/login2.json)
HTTP=$(curl -s -o /tmp/u2lists.json -w "%{http_code}" "$BASE/api/todos/lists/" -H "Authorization: Bearer $ACC2")
COUNT=$(jq -r .count /tmp/u2lists.json 2>/dev/null || echo "")
[[ "$HTTP" == "200" && ( -z "$COUNT" || "$COUNT" == "0" ) ]] && pass "ownership isolation" || fail "ownership isolation ($HTTP/$COUNT)"

echo -e "\nDone."

