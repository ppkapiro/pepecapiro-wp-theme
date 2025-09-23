#!/usr/bin/env bash
set -euo pipefail

# Configuración por defecto (puedes sobreescribir por env)
GH_OWNER=${GH_OWNER:-"ppkapiro"}
GH_REPO=${GH_REPO:-"pepecapiro-wp-theme"}
WF_FILE=${WF_FILE:-"lighthouse_docs.yml"}
BRANCH=${BRANCH:-"main"}
URLS_FILE=${URLS_FILE:-"scripts/urls_lighthouse.txt"}
POLL_SECONDS=${POLL_SECONDS:-15}
POLL_MAX=${POLL_MAX:-80}

cd "$(dirname "$0")/.."

# Cargar configuración local si existe (incluye GITHUB_TOKEN)
if [ -f .env.lighthouse ]; then
  set -a; source .env.lighthouse; set +a
fi

# Resolver token desde entorno ya cargado
TOKEN=${GITHUB_TOKEN:-${GH_TOKEN:-""}}

if ! command -v jq >/dev/null 2>&1; then
  echo "[X] jq no está instalado. Instálalo para continuar (sudo apt-get install -y jq)." >&2
  exit 2
fi

gh_api() {
  local method="$1"; shift
  local endpoint="$1"; shift
  local data="${1:-}"
  if [ -z "$TOKEN" ]; then
    echo "[X] Falta GITHUB_TOKEN/GH_TOKEN en el entorno." >&2
    exit 2
  fi
  local url="https://api.github.com/repos/${GH_OWNER}/${GH_REPO}${endpoint}"
  if [ -n "$data" ]; then
    curl -fsSL -X "$method" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      -d "$data" \
      "$url"
  else
    curl -fsSL -X "$method" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Accept: application/vnd.github+json" \
      "$url"
  fi
}

echo "[1/5] Buscar ID del workflow…"
WF_ID=$(gh_api GET "/actions/workflows" | jq -r \
  ".workflows[] | select(.path|endswith(\"${WF_FILE}\")) | .id" | head -n1)
if [ -z "$WF_ID" ]; then echo "[X] No se encontró el workflow ${WF_FILE}"; exit 3; fi
echo "     Workflow ID: $WF_ID"

echo "[2/5] Disparar workflow_dispatch…"
# Registrar último run antes de disparar para detectar el nuevo
LAST_BEFORE=$(gh_api GET "/actions/workflows/${WF_ID}/runs?branch=${BRANCH}&per_page=1" \
  | jq -r '.workflow_runs[0].id // empty')
PAYLOAD=$(jq -nc --arg ref "$BRANCH" --arg urls "$URLS_FILE" '{ref:$ref, inputs:{urls_file:$urls}}')
gh_api POST "/actions/workflows/${WF_ID}/dispatches" "$PAYLOAD" >/dev/null
echo "     Enviado. Esperando a que aparezca el run…"

echo "[3/5] Localizar el run recien creado…"
RUN_ID=""
ATTEMPT=0
while [ -z "$RUN_ID" ] && [ $ATTEMPT -lt 40 ]; do
  sleep 3
  RUNS_JSON=$(gh_api GET "/actions/workflows/${WF_ID}/runs?branch=${BRANCH}&event=workflow_dispatch&per_page=3")
  CANDIDATE=$(echo "$RUNS_JSON" | jq -r '.workflow_runs[0].id // empty')
  if [ -n "$CANDIDATE" ] && [ "$CANDIDATE" != "$LAST_BEFORE" ]; then
    RUN_ID="$CANDIDATE"
    break
  fi
  ATTEMPT=$((ATTEMPT+1))
done
if [ -z "$RUN_ID" ]; then echo "[X] No se pudo localizar el run iniciado."; exit 4; fi
RUN_HTML_URL="https://github.com/${GH_OWNER}/${GH_REPO}/actions/runs/${RUN_ID}"
echo "     Run: $RUN_ID"
echo "     URL: $RUN_HTML_URL"

echo "[4/5] Esperar finalización…"
STATE="queued"
CONCLUSION=""
COUNT=0
while [ "$STATE" != "completed" ] && [ $COUNT -lt $POLL_MAX ]; do
  sleep "$POLL_SECONDS"
  JSON=$(gh_api GET "/actions/runs/${RUN_ID}")
  STATE=$(echo "$JSON" | jq -r '.status')
  CONCLUSION=$(echo "$JSON" | jq -r '.conclusion // empty')
  echo "     Estado: $STATE (conclusion: ${CONCLUSION:-n/a}) — intento $COUNT/$POLL_MAX"
  COUNT=$((COUNT+1))
done

if [ "$STATE" != "completed" ]; then
  echo "[X] El run no completó a tiempo. Revisa: $RUN_HTML_URL"
  exit 5
fi

echo "[5/5] Resultado final:"
echo "     Run: $RUN_HTML_URL"
PAGES_URL="https://${GH_OWNER}.github.io/${GH_REPO}/docs/index.html"
LIGHTHOUSE_INDEX="https://${GH_OWNER}.github.io/${GH_REPO}/docs/lighthouse/index.html"
echo "     Pages landing: $PAGES_URL"
echo "     Índice Lighthouse: $LIGHTHOUSE_INDEX"

if [ "$CONCLUSION" = "success" ]; then
  echo "✅ ÉXITO: Gates OK. Tabla y reportes deberían estar actualizados."
  exit 0
fi

echo "⚠️ El run terminó con conclusión: $CONCLUSION (posible fallo de umbrales)."
echo "     Buscando artifacts (lh_fail)…"
ARTS=$(gh_api GET "/actions/runs/${RUN_ID}/artifacts")
LH_FAIL_URL=$(echo "$ARTS" | jq -r '.artifacts[] | select(.name=="lh_fail") | .archive_download_url' | head -n1)
if [ -n "$LH_FAIL_URL" ]; then
  echo "     Artifact lh_fail: $LH_FAIL_URL"
  echo "     (Descárgalo autenticado con un token de GitHub si lo necesitas)"
else
  echo "     No se encontró artifact lh_fail. Revisa el run."
fi

echo "🔎 También verifica la tabla en docs/VALIDACION_MVP_v0_2_1.md y los HTML en docs/lighthouse/."
exit 6
