#!/usr/bin/env bash
set -euo pipefail

# Aggregate multiple status.json endpoints into docs/hub/hub_status.json
# Requirements: bash, curl, jq

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
INSTANCES_FILE="$ROOT_DIR/docs/hub/instances.json"
OUTPUT_FILE="$ROOT_DIR/docs/hub/hub_status.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "[ERROR] 'jq' no está instalado en el runner. Instálalo antes de ejecutar este script." >&2
  exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
  echo "[ERROR] 'curl' no está disponible en el runner." >&2
  exit 1
fi

if [[ ! -f "$INSTANCES_FILE" ]]; then
  echo "[ERROR] No se encontró $INSTANCES_FILE" >&2
  exit 1
fi

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Read instances
mapfile -t IDS < <(jq -r '.instances[].id' "$INSTANCES_FILE")

instances_json="[]"
healthy_count=0
degraded_count=0
offline_count=0

for id in "${IDS[@]}"; do
  name=$(jq -r --arg id "$id" '.instances[] | select(.id==$id) | .name' "$INSTANCES_FILE")
  env=$(jq -r --arg id "$id" '.instances[] | select(.id==$id) | .environment' "$INSTANCES_FILE")
  endpoint=$(jq -r --arg id "$id" '.instances[] | select(.id==$id) | .status_endpoint' "$INSTANCES_FILE")

  http_code=0
  body=$(curl -sS -m 20 -w '\n%{http_code}' "$endpoint" || true)
  http_code=$(echo "$body" | tail -n1)
  json=$(echo "$body" | sed '$d')

  health="offline"
  version="unknown"
  last_update=null
  notes=""

  if [[ "$http_code" == "200" ]] && echo "$json" | jq -e . >/dev/null 2>&1; then
    version=$(echo "$json" | jq -r '.version // "unknown"')
    last_update=$(echo "$json" | jq -r '.last_update // .timestamp // empty')
    health_val=$(echo "$json" | jq -r '.health // empty')
    if [[ "$health_val" == "healthy" || "$health_val" == "OK" ]]; then
      health="healthy"
      ((healthy_count++))
    elif [[ -n "$health_val" ]]; then
      health="degraded"
      ((degraded_count++))
    else
      health="degraded"
      ((degraded_count++))
    fi
  else
    notes="fetch_failed:http_$http_code"
    ((offline_count++))
  fi

  instance_entry=$(jq -n \
    --arg id "$id" \
    --arg name "$name" \
    --arg environment "$env" \
    --arg endpoint "$endpoint" \
    --arg health "$health" \
    --arg version "$version" \
    --arg notes "$notes" \
    --argjson last_update ${last_update:+"\"$last_update\""} \
    '{id:$id,name:$name,environment:$environment,status_endpoint:$endpoint,version:$version,health:$health,last_update:$last_update,notes:($notes|select(.!=""))}'
  )

  instances_json=$(echo "$instances_json" | jq --argjson item "$instance_entry" '. += [$item]')
done

total_count=$(echo "$instances_json" | jq 'length')

summary=$(jq -n \
  --arg generated_at "$NOW_ISO" \
  --arg total "$total_count" \
  --arg healthy "$healthy_count" \
  --arg degraded "$degraded_count" \
  --arg offline "$offline_count" \
  '{generated_at:$generated_at, total:($total|tonumber), healthy:($healthy|tonumber), degraded:($degraded|tonumber), offline:($offline|tonumber)}')

final=$(jq -n --argjson summary "$summary" --argjson instances "$instances_json" '{summary:$summary, instances:$instances}')

echo "$final" | jq '.' > "$OUTPUT_FILE"
echo "[hub] Hub status agregado en $OUTPUT_FILE"
