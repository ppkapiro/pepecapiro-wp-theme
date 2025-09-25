#!/usr/bin/env bash
set -euo pipefail

echo "[diag] Iniciando diagnóstico API WordPress"

missing=0
for v in WP_URL WP_USER WP_APP_PASSWORD; do
  if [ -z "${!v:-}" ]; then echo "[diag][ERROR] Falta variable $v" >&2; missing=1; fi
done
if [ $missing -eq 1 ]; then echo "[diag] Abortando"; exit 2; fi

BASE="$WP_URL"
AUTH="$WP_USER:$WP_APP_PASSWORD"

echo "[diag] GET /wp-json/ (ping)" || true
curl -s -i "$BASE/wp-json/" | head -n 15

echo "[diag] GET posts?per_page=1 autenticado" || true
curl -s -i -u "$AUTH" "$BASE/wp-json/wp/v2/posts?per_page=1" | head -n 20 > /tmp/diag_posts_hdr.txt
status_posts=$(grep -m1 '^HTTP/' /tmp/diag_posts_hdr.txt | awk '{print $2}')
echo "[diag] Status GET posts: $status_posts"

echo "[diag] GET usuario actual" || true
curl -s -i -u "$AUTH" "$BASE/wp-json/wp/v2/users/me" | head -n 25 > /tmp/diag_me_hdr.txt || true
status_me=$(grep -m1 '^HTTP/' /tmp/diag_me_hdr.txt | awk '{print $2}')
echo "[diag] Status /users/me: $status_me"

PAYLOAD='{"title":"CI Probe Post","status":"draft"}'
echo "[diag] Creando post de prueba (draft)" || true
curl -s -i -u "$AUTH" -H 'Content-Type: application/json' -d "$PAYLOAD" "$BASE/wp-json/wp/v2/posts" > /tmp/diag_create.txt || true
status_create=$(grep -m1 '^HTTP/' /tmp/diag_create.txt | awk '{print $2}')
echo "[diag] Status create post: $status_create"
grep -m1 '^Location:' /tmp/diag_create.txt || true
tail -n 20 /tmp/diag_create.txt | sed 's/^[[:space:]]*/[body] /'

echo "{" > wp_api_diag_report.json
echo "  \"status_get_posts\": \"$status_posts\"," >> wp_api_diag_report.json
echo "  \"status_me\": \"$status_me\"," >> wp_api_diag_report.json
echo "  \"status_create\": \"$status_create\"" >> wp_api_diag_report.json
echo "}" >> wp_api_diag_report.json

echo "[diag] Reporte JSON -> wp_api_diag_report.json"
echo "[diag] Fin"
