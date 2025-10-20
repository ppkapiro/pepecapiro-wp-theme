#!/usr/bin/env bash
#
# bootstrap.sh — Configuración inicial del ecosistema WordPress + GitHub
#
# Uso:
#   bash export/scripts/bootstrap.sh                # Replicación completa
#   bash export/scripts/bootstrap.sh --minimal      # Solo workflows operacionales
#   bash export/scripts/bootstrap.sh --verify-only  # Solo workflows de verificación
#   bash export/scripts/bootstrap.sh --dry-run      # Simular sin ejecutar
#

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
MODE="${1:---full}"
DRY_RUN=false
MANIFEST_FILE="export/manifests/files_by_phase.json"

if [[ "$MODE" == "--dry-run" ]]; then
  DRY_RUN=true
  MODE="--full"
  echo -e "${YELLOW}🔍 Modo DRY-RUN: Simulación sin cambios reales${NC}"
fi

# Funciones de utilidad
log_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

check_command() {
  if ! command -v "$1" &> /dev/null; then
    log_error "Comando '$1' no encontrado. Por favor instálalo antes de continuar."
    exit 1
  fi
}

# Verificar prerequisitos
log_info "Verificando prerequisitos..."
check_command "git"
check_command "gh"
check_command "jq"
log_success "Prerequisitos OK"

# Verificar que estamos en el root del repositorio
if [[ ! -f "$MANIFEST_FILE" ]]; then
  log_error "No se encuentra $MANIFEST_FILE. Ejecuta este script desde el root del repositorio."
  exit 1
fi

# Cargar manifiesto
log_info "Cargando manifiesto de archivos..."
MANIFEST=$(cat "$MANIFEST_FILE")
VERSION=$(echo "$MANIFEST" | jq -r '.version')
log_info "Versión del Export Kit: $VERSION"

# Mostrar modo de replicación
case "$MODE" in
  --minimal)
    log_info "Modo: MINIMAL (solo workflows operacionales)"
    ;;
  --verify-only)
    log_info "Modo: VERIFY-ONLY (solo workflows de verificación)"
    ;;
  --full|*)
    log_info "Modo: FULL (replicación completa)"
    ;;
esac

# 1. Verificar instalación de WordPress
log_info ""
log_info "====== PASO 1: Verificar WordPress ======"
echo ""
read -p "¿Tienes una instalación de WordPress lista? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  log_error "Por favor, instala WordPress antes de continuar."
  log_info "Guía: https://wordpress.org/support/article/how-to-install-wordpress/"
  exit 1
fi
log_success "WordPress instalado"

# 2. Solicitar datos de WordPress
log_info ""
log_info "====== PASO 2: Configuración de WordPress ======"
echo ""
read -p "URL de WordPress (ej: https://mi-sitio.com): " WP_URL
read -p "Usuario admin de WordPress: " WP_USER
read -sp "Application Password de WordPress: " WP_APP_PASSWORD
echo
read -p "Path de instalación (dejar vacío si es root): " WP_PATH

# Validar conectividad
log_info "Validando conectividad con WordPress..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  --user "$WP_USER:$WP_APP_PASSWORD" \
  "$WP_URL/wp-json/wp/v2/users/me")

if [[ "$RESPONSE" != "200" ]]; then
  log_error "No se pudo conectar a WordPress. Código HTTP: $RESPONSE"
  log_error "Verifica la URL, usuario y Application Password."
  exit 1
fi
log_success "Conectividad con WordPress OK"

# 3. Configurar secrets en GitHub
log_info ""
log_info "====== PASO 3: Configurar Secrets en GitHub ======"
echo ""
log_info "Configurando secrets en el repositorio..."

if [[ "$DRY_RUN" == true ]]; then
  log_warning "DRY-RUN: No se configurarán secrets reales"
else
  gh secret set WP_URL --body "$WP_URL"
  gh secret set WP_USER --body "$WP_USER"
  gh secret set WP_APP_PASSWORD --body "$WP_APP_PASSWORD"
  
  if [[ -n "$WP_PATH" ]]; then
    gh secret set WP_PATH --body "$WP_PATH"
  fi
  
  log_success "Secrets configurados en GitHub"
fi

# 4. Preguntar por API_GATEWAY_TOKEN (opcional)
log_info ""
log_info "====== PASO 4: API Gateway Token (Opcional) ======"
echo ""
log_info "El API_GATEWAY_TOKEN permite triggers externos (webhooks WP→GitHub)."
log_info "Si no lo configuras ahora, puedes hacerlo después resolviendo issue #7."
echo ""
read -p "¿Deseas configurar API_GATEWAY_TOKEN ahora? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  log_info "Ve a: https://github.com/settings/tokens/new"
  log_info "Scopes requeridos: repo, workflow"
  read -sp "Pega tu GitHub Personal Access Token: " API_GATEWAY_TOKEN
  echo
  
  if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY-RUN: No se configurará API_GATEWAY_TOKEN"
  else
    gh secret set API_GATEWAY_TOKEN --body "$API_GATEWAY_TOKEN"
    log_success "API_GATEWAY_TOKEN configurado"
  fi
else
  log_warning "API_GATEWAY_TOKEN no configurado. Recuerda resolver issue #7 si necesitas webhooks WP→GitHub."
fi

# 5. Ajustar archivos de configuración
log_info ""
log_info "====== PASO 5: Ajustar Configuración ======"
echo ""
log_info "Archivos a personalizar:"
log_info "  - configs/pages.json (define páginas a crear)"
log_info "  - configs/menus.json (estructura de menús)"
log_info "  - configs/settings.json (opciones de WordPress)"
echo ""
read -p "¿Deseas editarlos ahora con tu editor por defecto? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  ${EDITOR:-nano} configs/pages.json
  ${EDITOR:-nano} configs/menus.json
  ${EDITOR:-nano} configs/settings.json
  log_success "Configuración personalizada"
else
  log_warning "Recuerda ajustar configs/pages.json, menus.json y settings.json según tu sitio."
fi

# 6. Ejecutar primer workflow de prueba
log_info ""
log_info "====== PASO 6: Ejecutar Workflow de Prueba ======"
echo ""
log_info "Probaremos la conectividad ejecutando 'health-dashboard.yml'"
echo ""
read -p "¿Deseas ejecutar el workflow de prueba? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  if [[ "$DRY_RUN" == true ]]; then
    log_warning "DRY-RUN: No se ejecutará workflow real"
  else
    log_info "Ejecutando health-dashboard.yml..."
    gh workflow run health-dashboard.yml
    sleep 3
    log_info "Estado de ejecución:"
    gh run list --workflow=health-dashboard.yml --limit 1
    log_success "Workflow ejecutado. Verifica el resultado en GitHub Actions."
  fi
else
  log_info "Puedes ejecutarlo manualmente con: gh workflow run health-dashboard.yml"
fi

# 7. Resumen final
log_info ""
log_info "====== 🎉 Bootstrap Completado ======"
echo ""
log_success "El ecosistema está configurado."
echo ""
log_info "Próximos pasos:"
log_info "  1. Revisa la ejecución del workflow en GitHub Actions"
log_info "  2. Ejecuta workflows según necesites:"
log_info "     - gh workflow run create-pages.yml"
log_info "     - gh workflow run create-posts.yml"
log_info "     - gh workflow run verify-home.yml"
log_info "  3. Consulta la documentación en docs/API_REFERENCE.md"
echo ""
log_info "Para soporte, abre un issue en GitHub."
echo ""
log_success "¡Listo para automatizar WordPress! 🚀"
