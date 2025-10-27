#!/bin/bash
# Script para configurar WP via workflow dispatch
# Ejecuta workflow que ya tiene acceso a secrets

set -euo pipefail

echo "=== Configuración WP Fase 3 via GitHub Actions ==="
echo ""

# Crear workflow personalizado para esta tarea
WORKFLOW_FILE=".github/workflows/fase3-setup.yml"

echo "Creando workflow temporal..."
cat > "$WORKFLOW_FILE" << 'EOFWORKFLOW'
name: Fase 3 Setup

on:
  workflow_dispatch:

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - name: Configurar WP
        env:
          WP_URL: ${{ secrets.WP_URL }}
          WP_USER: ${{ secrets.WP_USER }}
          WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
        run: |
          set -euo pipefail
          AUTH="$WP_USER:$WP_APP_PASSWORD"
          API="${WP_URL}/wp-json/wp/v2"
          
          echo "1. Configurando front page..."
          RESP=$(curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
            -d '{"show_on_front":"page","page_on_front":5}' \
            "${WP_URL}/wp-json/wp/v2/settings")
          
          if echo "$RESP" | jq -e '.page_on_front == 5' > /dev/null; then
            echo "✅ Front page: ID 5"
          fi
          
          echo "2. Creando Proyectos..."
          PROY=$(curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
            -d '{"title":"Proyectos","slug":"proyectos","status":"publish","template":"page-projects.php"}' \
            "${API}/pages" || echo '{}')
          PROY_ID=$(echo "$PROY" | jq -r '.id // empty')
          [ -n "$PROY_ID" ] && echo "✅ Proyectos: ID $PROY_ID" || echo "⚠️ Proyectos: revisar"
          
          echo "3. Creando Projects..."
          PROJ=$(curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
            -d '{"title":"Projects","slug":"projects","status":"publish","template":"page-projects.php"}' \
            "${API}/pages" || echo '{}')
          PROJ_ID=$(echo "$PROJ" | jq -r '.id // empty')
          [ -n "$PROJ_ID" ] && echo "✅ Projects: ID $PROJ_ID" || echo "⚠️ Projects: revisar"
          
          echo "4. Creando Recursos..."
          REC=$(curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
            -d '{"title":"Recursos","slug":"recursos","status":"publish","template":"page-resources.php"}' \
            "${API}/pages" || echo '{}')
          REC_ID=$(echo "$REC" | jq -r '.id // empty')
          [ -n "$REC_ID" ] && echo "✅ Recursos: ID $REC_ID" || echo "⚠️ Recursos: revisar"
          
          echo "5. Creando Resources..."
          RES=$(curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
            -d '{"title":"Resources","slug":"resources","status":"publish","template":"page-resources.php"}' \
            "${API}/pages" || echo '{}')
          RES_ID=$(echo "$RES" | jq -r '.id // empty')
          [ -n "$RES_ID" ] && echo "✅ Resources: ID $RES_ID" || echo "⚠️ Resources: revisar"
          
          echo ""
          echo "=== Resumen ==="
          echo "Front: ${WP_URL}/"
          echo "Proyectos: ${WP_URL}/proyectos/"
          echo "Resources: ${WP_URL}/resources/"
EOFWORKFLOW

git add "$WORKFLOW_FILE"
git commit -m "feat: add fase3-setup workflow"
git push origin HEAD

echo "✅ Workflow creado y pusheado"
echo ""
echo "Ejecutando workflow..."
sleep 3
gh workflow run fase3-setup.yml

echo ""
echo "Workflow disparado. Monitorear con:"
echo "  gh run list --workflow=fase3-setup.yml"
echo "  gh run watch"
