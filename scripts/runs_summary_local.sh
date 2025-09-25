#!/usr/bin/env bash
# Genera un resumen de runs de GitHub Actions similar al workflow runs-summary.yml
# Requisitos: gh (autenticado), jq
# Uso:
#   ./scripts/runs_summary_local.sh "Nombre Workflow" 40
#   ./scripts/runs_summary_local.sh "" 50   # todos los workflows, límite 50 por workflow
set -euo pipefail
WF_NAME="${1:-}"        # nombre exacto del workflow (name) o vacío para todos
LIMIT="${2:-40}"
REPO="${GITHUB_REPOSITORY:-ppkapiro/pepecapiro-wp-theme}"
ROOT_DIR="/home/pepe/work/pepecapiro-wp-theme"
OUT_DIR="$ROOT_DIR/reports/ci_runs"
mkdir -p "$OUT_DIR"
TMP_DIR="$(mktemp -d)"

pushd "$TMP_DIR" >/dev/null

echo "[INFO] Repo: $REPO" >&2
echo "[INFO] Filtro workflow: '${WF_NAME:-*}'" >&2
echo "[INFO] Límite por workflow: $LIMIT" >&2

gh api -X GET \
  "/repos/${REPO}/actions/runs" \
  --paginate -F per_page=100 -q '.workflow_runs[]' | jq -s '.' > runs_all.json
if [ -n "$WF_NAME" ]; then
  jq --arg N "$WF_NAME" '[ .[] | select(.name==$N) ]' runs_all.json > runs_filtered.json
else
  cp runs_all.json runs_filtered.json
fi
jq --argjson L "$LIMIT" '
  group_by(.name) |
  map({
    name: .[0].name,
    total: length,
    listed: (sort_by(.created_at) | reverse | .[0:$L] | map({
      id, run_number, status, conclusion, created_at, event,
      actor: .actor.login
    }))
  })
' runs_filtered.json > summary.json
{
  echo "# Workflow Runs Summary";
  echo "Repositorio: $REPO";
  echo "Generado: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo;
  jq -r '.[] | "## \(.name) (total: \(.total))\n" + ( .listed[]? | "- #\(.run_number) id=\(.id) status=\(.status) conclusion=\(.conclusion) created=\(.created_at) event=\(.event) actor=\(.actor)" ) + "\n"' summary.json;
} > summary.md

cp summary.md summary.json runs_all.json runs_filtered.json "$OUT_DIR"/

popd >/dev/null
rm -rf "$TMP_DIR"

echo "[OK] Archivos generados en $OUT_DIR: summary.md, summary.json, runs_all.json, runs_filtered.json" >&2
