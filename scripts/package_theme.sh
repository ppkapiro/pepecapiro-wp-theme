#!/usr/bin/env bash
set -euo pipefail
VER=$(grep -E '^Version:' pepecapiro/style.css | awk '{print $2}')
TS=$(date +%Y%m%d_%H%M%S)
OUT="_releases/pepecapiro_${TS}_v${VER}.zip"
mkdir -p _releases
zip -r "$OUT" pepecapiro > /dev/null
sha256sum "$OUT" | tee "${OUT%.zip}.sha256"
echo "Generado: $OUT"
