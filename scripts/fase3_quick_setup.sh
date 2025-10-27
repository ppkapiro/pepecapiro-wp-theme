#!/bin/bash
# Configuración rápida Fase 3 - WordPress
# Ejecuta todas las tareas pendientes via REST API

set -euo pipefail

echo "=== Fase 3: Configuración WordPress ==="
echo ""
echo "Este script configurará:"
echo "  1. Front page (Inicio como página principal)"
echo "  2. 4 nuevas páginas (Proyectos/Projects, Recursos/Resources)"
echo "  3. Purga de cache LiteSpeed"
echo ""
echo "⚠️  Requiere Application Password de WordPress"
echo "   Generar en: https://pepecapiro.com/wp-admin/profile.php"
echo ""

# Solicitar credenciales
WP_URL="https://pepecapiro.com"
read -p "Usuario WP [ppcapiro]: " WP_USER
WP_USER=${WP_USER:-ppcapiro}
read -sp "Application Password: " WP_APP_PASSWORD
echo ""
echo ""

if [ -z "$WP_APP_PASSWORD" ]; then
  echo "❌ Application Password requerido"
  exit 1
fi

AUTH="$WP_USER:$WP_APP_PASSWORD"
API="${WP_URL}/wp-json/wp/v2"

# Test de autenticación
echo "🔐 Verificando credenciales..."
AUTH_TEST=$(curl -s -u "$AUTH" -w "%{http_code}" -o /dev/null "${WP_URL}/wp-json/wp/v2/users/me")
if [ "$AUTH_TEST" != "200" ]; then
  echo "❌ Error de autenticación (HTTP $AUTH_TEST)"
  echo "   Verifica usuario y Application Password"
  exit 1
fi
echo "✅ Autenticación OK"
echo ""

# 1. Front page
echo "1️⃣  Configurando front page (Inicio ID 5)..."
SETTINGS_RESP=$(curl -s -u "$AUTH" -X POST \
  -H "Content-Type: application/json" \
  -d '{"show_on_front":"page","page_on_front":5}' \
  "${WP_URL}/wp-json/wp/v2/settings")

FRONT_ID=$(echo "$SETTINGS_RESP" | jq -r '.page_on_front // empty')
if [ "$FRONT_ID" = "5" ]; then
  echo "✅ Front page configurada: Inicio (ID 5)"
  echo "   URL: ${WP_URL}/"
else
  echo "⚠️  Error configurando front page"
  echo "$SETTINGS_RESP" | jq -r '.message // "Error desconocido"'
fi
echo ""

# Helper para crear/obtener página
create_or_get_page() {
  local title="$1"
  local slug="$2"
  local template="$3"
  local excerpt="$4"
  
  echo "Creando/verificando: $title ($slug)..."
  
  RESP=$(curl -s -u "$AUTH" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"$title\",\"slug\":\"$slug\",\"status\":\"publish\",\"template\":\"$template\",\"excerpt\":\"$excerpt\"}" \
    "${API}/pages" 2>&1)
  
  PAGE_ID=$(echo "$RESP" | jq -r '.id // empty' 2>/dev/null || echo "")
  
  if [ -n "$PAGE_ID" ]; then
    PAGE_LINK=$(echo "$RESP" | jq -r '.link')
    echo "✅ $title - ID: $PAGE_ID"
    echo "   URL: $PAGE_LINK"
  else
    ERROR=$(echo "$RESP" | jq -r '.message // .code // "Error"' 2>/dev/null || echo "Error")
    if echo "$ERROR" | grep -qi "slug.*already\|existe"; then
      echo "⚠️  Ya existe, obteniendo ID..."
      EXISTING=$(curl -s -u "$AUTH" "${API}/pages?slug=$slug&per_page=1")
      PAGE_ID=$(echo "$EXISTING" | jq -r '.[0].id // empty')
      PAGE_LINK=$(echo "$EXISTING" | jq -r '.[0].link // empty')
      echo "   ID existente: $PAGE_ID"
      echo "   URL: $PAGE_LINK"
    else
      echo "❌ Error: $ERROR"
    fi
  fi
  echo ""
}

# 2-5. Crear páginas
echo "2️⃣  Páginas Proyectos/Projects..."
create_or_get_page "Proyectos" "proyectos" "page-projects.php" "Portafolio de proyectos"
create_or_get_page "Projects" "projects" "page-projects.php" "Projects portfolio"

echo "3️⃣  Páginas Recursos/Resources..."
create_or_get_page "Recursos" "recursos" "page-resources.php" "Colección de recursos"
create_or_get_page "Resources" "resources" "page-resources.php" "Resources collection"

# 6. Purgar cache
echo "4️⃣  Purgando cache LiteSpeed..."
PURGE_RESP=$(curl -s "${WP_URL}/?LSCWP_CTRL=PURGE_ALL")
if echo "$PURGE_RESP" | grep -qi "purged\|success\|ok" || [ -z "$PURGE_RESP" ]; then
  echo "✅ Cache purgado"
else
  echo "⚠️  Cache: verificar manualmente"
fi
echo ""

# Resumen final
echo "================================"
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "================================"
echo ""
echo "URLs verificadas:"
echo "  🏠 Home: ${WP_URL}/"
echo "  📁 Proyectos: ${WP_URL}/proyectos/"
echo "  📁 Projects: ${WP_URL}/projects/"
echo "  📚 Recursos: ${WP_URL}/recursos/"
echo "  📚 Resources: ${WP_URL}/resources/"
echo ""
echo "⚠️  ACCIÓN MANUAL PENDIENTE:"
echo "   Actualizar menús en WP Admin"
echo "   https://pepecapiro.com/wp-admin/nav-menus.php"
echo ""
echo "   Principal ES: Añadir Proyectos y Recursos"
echo "   Main EN: Añadir Projects y Resources"
echo ""
echo "📊 Validación rápida:"
echo "   curl -s ${WP_URL}/ | grep 'Consultor en IA'"
echo ""
