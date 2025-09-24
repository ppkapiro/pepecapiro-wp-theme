#!/usr/bin/env bash
# Remediación post-deploy para pepecapiro en Hostinger (vía SSH + WP-CLI)
# - Activar tema hijo si no está activo
# - (Opcional) Fijar portada estática si existe página "home" o "inicio"
# - Purgar cachés (WP + LiteSpeed si está)
# - Validaciones simples (HTML/CSS/OG)
# Uso:
#   scripts/wp_post_deploy_remediate.sh            # dry-run (no cambia nada)
#   scripts/wp_post_deploy_remediate.sh --apply    # aplica cambios

set -euo pipefail

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then APPLY=1; fi

SSH_HOST="${PEPE_HOST:-157.173.214.43}"
SSH_PORT="${PEPE_PORT:-65002}"
SSH_USER="${PEPE_USER:-u525829715}"
SSH_KEY="${PEPE_SSH_KEY:-}"
SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"
THEME_SLUG="pepecapiro"

log(){ echo "[remediate] $*"; }
err(){ echo "[error] $*" >&2; }
run_ssh(){
  local cmd="$*"
  local SSH_OPTS=("-p" "$SSH_PORT" "-o" "StrictHostKeyChecking=no" "-o" "UserKnownHostsFile=/dev/null")
  if [[ -n "$SSH_KEY" ]]; then SSH_OPTS+=("-i" "$SSH_KEY"); fi
  ssh "${SSH_OPTS[@]}" "$SSH_USER@$SSH_HOST" "$cmd"
}
wp(){
  local cmd="$*"
  run_ssh "cd '$SITE_ROOT' && wp $cmd"
}

# 1) Estado inicial
log "Comprobando tema activo..."
ACTIVE_JSON="$(wp "theme list --status=active --format=json" 2>&1 || true)"
ACTIVE_THEME="$(echo "$ACTIVE_JSON" | sed -n 's/.*"name"\s*:\s*"\([^"]*\)".*/\1/p' | head -n1)"
[[ -z "$ACTIVE_THEME" ]] && ACTIVE_THEME="ND"
log "Tema activo: $ACTIVE_THEME"

# 2) Activar tema si no es el esperado
if [[ "$ACTIVE_THEME" != "$THEME_SLUG" ]]; then
  log "Tema activo no es '$THEME_SLUG'. Se propone activarlo."
  if [[ $APPLY -eq 1 ]]; then
    log "Aplicando: wp theme activate $THEME_SLUG"
    wp "theme activate $THEME_SLUG" || err "Fallo activando tema"
  else
    log "DRY-RUN: omitiendo activación (use --apply para ejecutar)"
  fi
else
  log "Tema '$THEME_SLUG' ya activo."
fi

# 3) (Opcional) Portada estática si hay página 'home' o 'inicio'
SHOW_ON_FRONT="$(wp "option get show_on_front" 2>/dev/null || echo ND)"
PAGE_ON_FRONT="$(wp "option get page_on_front" 2>/dev/null || echo 0)"
log "show_on_front=$SHOW_ON_FRONT, page_on_front=$PAGE_ON_FRONT"

# Detectar candidatos
HOME_ID="$(wp "post list --post_type=page --name=home --field=ID" 2>/dev/null | head -n1 || true)"
INICIO_ID="$(wp "post list --post_type=page --name=inicio --field=ID" 2>/dev/null | head -n1 || true)"
CAND_ID="${HOME_ID:-}"; [[ -z "$CAND_ID" ]] && CAND_ID="${INICIO_ID:-}"
if [[ -n "$CAND_ID" && "$CAND_ID" =~ ^[0-9]+$ ]]; then
  if [[ "$SHOW_ON_FRONT" != "page" || "$PAGE_ON_FRONT" != "$CAND_ID" ]]; then
    log "Se propone fijar portada estática a page ID=$CAND_ID"
    if [[ $APPLY -eq 1 ]]; then
      wp "option update show_on_front page" || true
      wp "option update page_on_front $CAND_ID" || true
    else
      log "DRY-RUN: omitiendo cambio de portada (use --apply)"
    fi
  else
    log "Portada ya configurada a $CAND_ID"
  fi
else
  log "No se encontró página con slug 'home' o 'inicio'; no se toca portada."
fi

# 4) Purgar cachés (WP + LiteSpeed si plugin instalado)
log "Purgando cachés..."
wp "cache flush" || true
if wp "plugin is-installed litespeed-cache" >/dev/null 2>&1; then
  log "LiteSpeed Cache detectado; purgando todo"
  wp "litespeed-purge all" || true
fi

# 5) Validaciones sencillas
log "Validación rápida: CSS/OG en HTML"
HEAD_HTML="$(curl -sS -m 12 https://pepecapiro.com/ | head -n 400 || true)"
CSS_LINE="$(printf "%s" "$HEAD_HTML" | grep -oiE "href=\"[^\"]+\.css[^\"]*\"" | head -n1 || true)"
OG_IMAGE="$(printf "%s" "$HEAD_HTML" | grep -oiE "<meta[^>]+property=\"og:image\"[^>]*>" | head -n1 || true)"
log "Primer CSS encontrado: ${CSS_LINE:-ND}"
log "Meta OG:image presente: $( [[ -n "$OG_IMAGE" ]] && echo SI || echo NO )"

log "Remediación finalizada (modo: $([[ $APPLY -eq 1 ]] && echo apply || echo dry-run))"
