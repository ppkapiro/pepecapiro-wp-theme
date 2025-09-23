#!/usr/bin/env bash
set -euo pipefail
BASE="$(pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
OUT="$BASE/evidence"
mkdir -p "$OUT"
THEME_NAME="pepecapiro"

# Patrones a buscar
mapfile -t PATTERNS < <(cat << 'EOF'
wpforms
contact-form-7
gravityforms
\[shortcode
customize_additional_css
og:
EOF
)

for pat in "${PATTERNS[@]}"; do
  safe=$(echo "$pat" | sed 's/[^A-Za-z0-9_-]/_/g')
  file="$OUT/${TS}_grep_theme_${THEME_NAME}_${safe}.txt"
  echo "== grep -Rin '$pat' . ==" > "$file" || true
  grep -Rin --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="vendor" --line-number -E "$pat" . >> "$file" 2>/dev/null || true
  echo "[i] Guardado $file"
done

# CSS: frecuencias de color/box-shadow/border-radius
CSS_FREQ="$OUT/${TS}_css_frecuencias.txt"
{
  echo "# Frecuencias CSS (color, box-shadow, border-radius)"
  echo "## color"
  grep -Rho --include="*.css" "color:\s*[^;]+" ./pepecapiro 2>/dev/null | sed -E 's/.*color:\s*//; s/\s+!/ !/; s/\s+$//' | sort | uniq -c | sort -nr || true
  echo "\n## box-shadow"
  grep -Rho --include="*.css" "box-shadow:\s*[^;]+" ./pepecapiro 2>/dev/null | sed -E 's/.*box-shadow:\s*//; s/\s+!/ !/; s/\s+$//' | sort | uniq -c | sort -nr || true
  echo "\n## border-radius"
  grep -Rho --include="*.css" "border-radius:\s*[^;]+" ./pepecapiro 2>/dev/null | sed -E 's/.*border-radius:\s*//; s/\s+!/ !/; s/\s+$//' | sort | uniq -c | sort -nr || true
} > "$CSS_FREQ" || true

echo "[✓] Trazas guardadas en $OUT con TS $TS"
