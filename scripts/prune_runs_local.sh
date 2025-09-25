#!/usr/bin/env bash
# Borra ejecuciones antiguas de workflows usando la CLI gh.
# Requisitos: gh auth login (con repo scope), jq
# Uso:
#   ./scripts/prune_runs_local.sh "Content Sync" 15
#     -> mantiene las 15 más recientes de ese workflow
#   ./scripts/prune_runs_local.sh "" 50
#     -> mantiene 50 globalmente (todos)
set -euo pipefail
WF_NAME="${1:-}"
KEEP="${2:-20}"
REPO="${GITHUB_REPOSITORY:-ppkapiro/pepecapiro-wp-theme}"

echo "Repo: $REPO" >&2
echo "Workflow filter: '${WF_NAME}'" >&2
echo "Manteniendo últimas $KEEP" >&2

page=1
ALL='[]'
while true; do
  RESP=$(gh api repos/$REPO/actions/runs -F per_page=100 -F page=$page || true)
  CNT=$(echo "$RESP" | jq '.workflow_runs | length')
  if [ "$CNT" = "0" ]; then break; fi
  if [ -n "$WF_NAME" ]; then
    PART=$(echo "$RESP" | jq --arg N "$WF_NAME" '[.workflow_runs[] | select(.name==$N) | {id:.id,name:.name,created:.created_at}]')
  else
    PART=$(echo "$RESP" | jq '[.workflow_runs[] | {id:.id,name:.name,created:.created_at}]')
  fi
  ALL=$(jq -s 'add' <(echo "$ALL") <(echo "$PART"))
  page=$((page+1))
  if [ $page -gt 15 ]; then break; fi
done

TOTAL=$(echo "$ALL" | jq 'length')
echo "Total capturado: $TOTAL" >&2
if [ "$TOTAL" -le "$KEEP" ]; then
  echo "Nada que borrar (total <= keep)" >&2
  exit 0
fi
TO_DELETE=$(echo "$ALL" | jq -r --argjson K "$KEEP" 'sort_by(.created) | reverse | .[K:] | .[].id')
DEL=0
for ID in $TO_DELETE; do
  echo "Deleting run $ID" >&2
  gh api repos/$REPO/actions/runs/$ID -X DELETE || true
  DEL=$((DEL+1))
done
echo "Borrados $DEL runs" >&2
