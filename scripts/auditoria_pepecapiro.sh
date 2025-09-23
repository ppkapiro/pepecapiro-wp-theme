#!/usr/bin/env bash
set -euo pipefail

# === Config ===
BASE="$(pwd)"
DOMAIN="https://pepecapiro.com"
OUT="$BASE/evidence"
TS="$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUT"

echo "[i] Auditoría pública de $DOMAIN — $TS"

# 1) Endpoints REST básicos
curl -fsSL "$DOMAIN/wp-json" -o "$OUT/${TS}_wp-json_root.json" || true

# 2) Contenido público (páginas/entradas/medios)
# Nota: per_page=100 para abarcar bastante; repetir con ?page=2 si hace falta
curl -fsSL "$DOMAIN/wp-json/wp/v2/pages?per_page=100&_fields=id,date,slug,link,status,title,content" \
  -o "$OUT/${TS}_pages.json" || true
curl -fsSL "$DOMAIN/wp-json/wp/v2/posts?per_page=100&_fields=id,date,slug,link,status,title,excerpt,content" \
  -o "$OUT/${TS}_posts.json" || true
curl -fsSL "$DOMAIN/wp-json/wp/v2/media?per_page=100&_fields=id,date,slug,source_url,media_type" \
  -o "$OUT/${TS}_media.json" || true

# 3) Home y variantes idiomáticas
curl -I -sS "$DOMAIN/"            > "$OUT/${TS}_home_headers.txt" || true
curl -fsSL    "$DOMAIN/"          > "$OUT/${TS}_home.html"        || true
curl -I -sS "$DOMAIN/es/"         > "$OUT/${TS}_home_es_headers.txt" || true
curl -fsSL    "$DOMAIN/es/"       > "$OUT/${TS}_home_es.html"     || true
curl -I -sS "$DOMAIN/en/"         > "$OUT/${TS}_home_en_headers.txt" || true
curl -fsSL    "$DOMAIN/en/"       > "$OUT/${TS}_home_en.html"     || true

# 4) robots.txt, sitemap.xml
curl -fsSL "$DOMAIN/robots.txt"   -o "$OUT/${TS}_robots.txt"      || true
curl -fsSL "$DOMAIN/sitemap.xml"  -o "$OUT/${TS}_sitemap.xml"     || true

# 5) OG/Twitter tags (extraer líneas relevantes)
grep -iE 'og:|twitter:' "$OUT/${TS}_home.html"    || true
grep -iE 'og:|twitter:' "$OUT/${TS}_home_es.html" || true
grep -iE 'og:|twitter:' "$OUT/${TS}_home_en.html" || true

# 6) Búsqueda de shortcodes clásicos en contenido REST
# Guardamos un mini log para cada patrón
for PAT in "\[wpforms" "\[contact-form-7" "\[gravityforms" "\[shortcode-"; do
  echo "== Resultados para patrón $PAT ==" >> "$OUT/${TS}_shortcodes_scan.txt"
  (cat "$OUT/${TS}_pages.json" "$OUT/${TS}_posts.json" 2>/dev/null || true) | grep -i "$PAT" -n || true
done >> "$OUT/${TS}_shortcodes_scan.txt" 2>/dev/null

# 7) Head meta y títulos (chequeo rápido)
grep -i "<title>" "$OUT/${TS}_home.html"    || true
grep -i "<title>" "$OUT/${TS}_home_es.html" || true
grep -i "<title>" "$OUT/${TS}_home_en.html" || true

# 8) Opcional: Lighthouse (si hay Node/npx)
if command -v npx >/dev/null 2>&1; then
  LH_DIR="$OUT/lighthouse_$TS"; mkdir -p "$LH_DIR"
  npx -y lighthouse "$DOMAIN/"    --quiet --chrome-flags="--headless" --output=html --output-path="$LH_DIR/home.html"    || true
  npx -y lighthouse "$DOMAIN/es/" --quiet --chrome-flags="--headless" --output=html --output-path="$LH_DIR/home_es.html" || true
  npx -y lighthouse "$DOMAIN/en/" --quiet --chrome-flags="--headless" --output=html --output-path="$LH_DIR/home_en.html" || true
fi

echo "[✓] Auditoría pública completada. Evidencia en $OUT"
