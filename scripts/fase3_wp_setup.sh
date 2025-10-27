#!/bin/bash
# Script para completar configuración WP de Fase 3
# Usa secretos de GitHub Actions via gh secret get

set -euo pipefail

echo "=== Configuración WP Fase 3 ==="
echo ""

# Obtener secretos de GitHub
WP_URL=$(gh secret get WP_URL)
WP_USER=$(gh secret get WP_USER)
WP_APP_PASSWORD=$(gh secret get WP_APP_PASSWORD)

AUTH="$WP_USER:$WP_APP_PASSWORD"
API="${WP_URL}/wp-json/wp/v2"

echo "1️⃣  Configurando front page (Inicio ID 5)..."
SETTINGS_RESPONSE=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{"show_on_front":"page","page_on_front":5}' \
  "${WP_URL}/wp-json/wp/v2/settings")

if echo "$SETTINGS_RESPONSE" | grep -q '"page_on_front":5'; then
  echo "✅ Front page configurada: Inicio (ID 5)"
else
  echo "⚠️  Error configurando front page:"
  echo "$SETTINGS_RESPONSE" | jq '.'
fi
echo ""

echo "2️⃣  Creando página Proyectos (ES)..."
PROYECTOS_RESPONSE=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Proyectos",
    "slug":"proyectos",
    "status":"publish",
    "template":"page-projects.php",
    "content":"",
    "excerpt":"Portafolio de proyectos destacados"
  }' \
  "${API}/pages")

PROY_ID=$(echo "$PROYECTOS_RESPONSE" | jq -r '.id // empty')
if [ -n "$PROY_ID" ]; then
  PROY_LINK=$(echo "$PROYECTOS_RESPONSE" | jq -r '.link')
  echo "✅ Proyectos creada - ID: $PROY_ID"
  echo "   URL: $PROY_LINK"
else
  ERROR_MSG=$(echo "$PROYECTOS_RESPONSE" | jq -r '.message // "Error desconocido"')
  if echo "$ERROR_MSG" | grep -qi "slug.*already"; then
    echo "⚠️  Página ya existe, obteniendo ID..."
    EXISTING=$(curl -s -u "$AUTH" "${API}/pages?slug=proyectos")
    PROY_ID=$(echo "$EXISTING" | jq -r '.[0].id // empty')
    echo "   ID existente: $PROY_ID"
  else
    echo "⚠️  Error: $ERROR_MSG"
  fi
fi
echo ""

echo "3️⃣  Creando página Projects (EN)..."
PROJECTS_RESPONSE=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Projects",
    "slug":"projects",
    "status":"publish",
    "template":"page-projects.php",
    "content":"",
    "excerpt":"Featured projects portfolio"
  }' \
  "${API}/pages")

PROJ_ID=$(echo "$PROJECTS_RESPONSE" | jq -r '.id // empty')
if [ -n "$PROJ_ID" ]; then
  PROJ_LINK=$(echo "$PROJECTS_RESPONSE" | jq -r '.link')
  echo "✅ Projects creada - ID: $PROJ_ID"
  echo "   URL: $PROJ_LINK"
else
  ERROR_MSG=$(echo "$PROJECTS_RESPONSE" | jq -r '.message // "Error desconocido"')
  if echo "$ERROR_MSG" | grep -qi "slug.*already"; then
    echo "⚠️  Página ya existe, obteniendo ID..."
    EXISTING=$(curl -s -u "$AUTH" "${API}/pages?slug=projects")
    PROJ_ID=$(echo "$EXISTING" | jq -r '.[0].id // empty')
    echo "   ID existente: $PROJ_ID"
  else
    echo "⚠️  Error: $ERROR_MSG"
  fi
fi
echo ""

echo "4️⃣  Creando página Recursos (ES)..."
RECURSOS_RESPONSE=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Recursos",
    "slug":"recursos",
    "status":"publish",
    "template":"page-resources.php",
    "content":"",
    "excerpt":"Colección de herramientas y recursos útiles"
  }' \
  "${API}/pages")

REC_ID=$(echo "$RECURSOS_RESPONSE" | jq -r '.id // empty')
if [ -n "$REC_ID" ]; then
  REC_LINK=$(echo "$RECURSOS_RESPONSE" | jq -r '.link')
  echo "✅ Recursos creada - ID: $REC_ID"
  echo "   URL: $REC_LINK"
else
  ERROR_MSG=$(echo "$RECURSOS_RESPONSE" | jq -r '.message // "Error desconocido"')
  if echo "$ERROR_MSG" | grep -qi "slug.*already"; then
    echo "⚠️  Página ya existe, obteniendo ID..."
    EXISTING=$(curl -s -u "$AUTH" "${API}/pages?slug=recursos")
    REC_ID=$(echo "$EXISTING" | jq -r '.[0].id // empty')
    echo "   ID existente: $REC_ID"
  else
    echo "⚠️  Error: $ERROR_MSG"
  fi
fi
echo ""

echo "5️⃣  Creando página Resources (EN)..."
RESOURCES_RESPONSE=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Resources",
    "slug":"resources",
    "status":"publish",
    "template":"page-resources.php",
    "content":"",
    "excerpt":"Collection of useful tools and resources"
  }' \
  "${API}/pages")

RES_ID=$(echo "$RESOURCES_RESPONSE" | jq -r '.id // empty')
if [ -n "$RES_ID" ]; then
  RES_LINK=$(echo "$RESOURCES_RESPONSE" | jq -r '.link')
  echo "✅ Resources creada - ID: $RES_ID"
  echo "   URL: $RES_LINK"
else
  ERROR_MSG=$(echo "$RESOURCES_RESPONSE" | jq -r '.message // "Error desconocido"')
  if echo "$ERROR_MSG" | grep -qi "slug.*already"; then
    echo "⚠️  Página ya existe, obteniendo ID..."
    EXISTING=$(curl -s -u "$AUTH" "${API}/pages?slug=resources")
    RES_ID=$(echo "$EXISTING" | jq -r '.[0].id // empty')
    echo "   ID existente: $RES_ID"
  else
    echo "⚠️  Error: $ERROR_MSG"
  fi
fi
echo ""

echo "=== Resumen ==="
echo ""
echo "✅ Front page: ${WP_URL}/"
echo "✅ Proyectos: ${WP_URL}/proyectos/ (ID: ${PROY_ID:-N/A})"
echo "✅ Projects: ${WP_URL}/projects/ (ID: ${PROJ_ID:-N/A})"
echo "✅ Recursos: ${WP_URL}/recursos/ (ID: ${REC_ID:-N/A})"
echo "✅ Resources: ${WP_URL}/resources/ (ID: ${RES_ID:-N/A})"
echo ""
echo "⚠️  PENDIENTE: Actualizar menús en WP Admin"
echo "   - Principal ES: añadir Proyectos y Recursos"
echo "   - Main EN: añadir Projects y Resources"
echo ""
echo "💡 Purgar cache LiteSpeed: ${WP_URL}/?LSCWP_CTRL=PURGE_ALL"
