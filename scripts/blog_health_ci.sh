#!/usr/bin/env bash
# Blog Health CI Script
# Verifica que /blog (ES) y /en/blog-en (EN) respondan 200, contengan marker
# <!-- posts_found:X lang:YY --> y/o div #blog-query-info con data-posts>0.
# Salida:
#  - exit 0 si ambos idiomas pasan (permitiendo posts_found>=0 pero exige >=1 por robustez salvo override)
#  - exit 1 fallo crítico
# Variables opcionales:
#   ALLOW_ZERO=1  (si se permite 0 posts sin fallar)

set -euo pipefail
BASE="https://pepecapiro.com"
ES_PATH="/blog/"
EN_PATH="/en/blog-en/"
ALLOW_ZERO=${ALLOW_ZERO:-0}

test_endpoint(){
  local url="$1"; local expect_lang="$2"; local label="$3"
  echo "[check] $label => $url" >&2
  local body status
  status=$(curl -sS -L -o /tmp/_bh_body -w '%{http_code}' "$url" || echo 000)
  if [[ "$status" != 200 ]]; then
    echo "[fail] $label status=$status" >&2; return 1
  fi
  cp /tmp/_bh_body /tmp/_bh_body_${label}.html
  local marker
  marker=$(grep -oE '<!-- posts_found:[0-9]+ lang:[a-z]+' /tmp/_bh_body || true)
  local div_posts
  div_posts=$(grep -oE 'id="blog-query-info"[^>]+data-posts="[0-9]+"' /tmp/_bh_body || true)
  if [[ -z "$marker" && -z "$div_posts" ]]; then
    echo "[fail] $label sin marker ni div oculto" >&2; return 1
  fi
  local count=; count=$(echo "$marker" | grep -oE 'posts_found:[0-9]+' | cut -d: -f2 | head -n1 || true)
  if [[ -z "$count" ]]; then
    count=$(echo "$div_posts" | grep -oE 'data-posts="[0-9]+' | grep -oE '[0-9]+' | head -n1 || true)
  fi
  if [[ -z "$count" ]]; then
    echo "[fail] $label sin count detectable" >&2; return 1
  fi
  if [[ "$ALLOW_ZERO" != 1 && "$count" -lt 1 ]]; then
    echo "[fail] $label count=$count (<1)" >&2; return 1
  fi
  echo "[ok] $label count=$count" >&2
}

FAIL=0
test_endpoint "$BASE$ES_PATH" es ES || FAIL=1
test_endpoint "$BASE$EN_PATH" en EN || FAIL=1

if [[ $FAIL -eq 0 ]]; then
  echo "Blog health OK"; exit 0
else
  echo "Blog health FAIL"; exit 1
fi
