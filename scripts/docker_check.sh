#!/usr/bin/env bash
# Chequeo y reconstrucción segura del stack Docker local para pepecapiro.com (solo recursos del proyecto)
# - Detecta compose, lista estado, limpia contenedores/redes/volúmenes del proyecto
# - Reconstruye sin caché y levanta en segundo plano
# - Verifica montaje del tema y hash de style.css dentro del contenedor
# - Hace curl a localhost para smoke test
# - Genera _scratch/docker_check.md y muestra bloque BEGIN/END

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SCRATCH_DIR="$REPO_ROOT/_scratch"
mkdir -p "$SCRATCH_DIR"
REPORT_PATH="$SCRATCH_DIR/docker_check.md"

DOCKER_DIR="$REPO_ROOT/docker"
COMPOSE_FILE=""
for f in "$DOCKER_DIR/docker-compose.yml" "$DOCKER_DIR/compose.yml" "$DOCKER_DIR/compose.yaml" "$DOCKER_DIR/docker-compose.yaml"; do
  [[ -f "$f" ]] && COMPOSE_FILE="$f" && break
done

THEME_LOCAL_DIR="$REPO_ROOT/pepecapiro"
LOCAL_STYLE="$THEME_LOCAL_DIR/style.css"

mask_secrets(){
  sed -E \
    -e 's/(PASSWORD|PASS|MYSQL_ROOT_PASSWORD|MYSQL_PASSWORD|PMA_PASSWORD)(=|:\\s*).*/\1\2****/Ig' \
    -e 's/(WORDPRESS_DB_PASSWORD)(=|:\\s*).*/\1\2****/Ig'
}

has_cmd(){ command -v "$1" >/dev/null 2>&1; }

compose(){
  # Wrapper que usa docker compose si existe; fallback a docker-compose
  if has_cmd docker && docker compose version >/dev/null 2>&1; then
    docker compose -f "$COMPOSE_FILE" "$@"
  elif has_cmd docker-compose; then
    docker-compose -f "$COMPOSE_FILE" "$@"
  else
    echo "[ERROR] No se encontró docker compose ni docker-compose" >&2
    return 127
  fi
}

compose_with_env(){
  local envfile="$1"; shift
  if has_cmd docker && docker compose version >/dev/null 2>&1; then
    docker compose --env-file "$envfile" -f "$COMPOSE_FILE" "$@"
  else
    # docker-compose v1 no soporta --env-file; exportaremos variables
    set -a; source "$envfile"; set +a
    docker-compose -f "$COMPOSE_FILE" "$@"
  fi
}

collect_state(){
  echo "- Compose file: ${COMPOSE_FILE:-ND}"
  echo "- Docker: $(docker --version 2>/dev/null || echo ND)"
  echo "- Compose: $(docker compose version 2>/dev/null || docker-compose --version 2>/dev/null || echo ND)"
  echo "- Contenedores del proyecto (si existen):"
  docker ps -a --format '{{.Names}} | {{.Status}} | {{.Ports}}' | grep -E '^(wp_db|wp_app|wp_pma|wp_cli)\b' || echo "  (ninguno)"
  echo "- Volúmenes del proyecto:"
  docker volume ls --format '{{.Name}}' | grep -E '^(db_data|wp_html)$' || echo "  (ninguno)"
  echo "- Redes del proyecto:"
  docker network ls --format '{{.Name}}' | grep -E '(^|_)docker_default$' || echo "  (ninguna)"
}

wp_cli_method_detect(){
  # Detecta y fija el método global para WP-CLI: 'wp_app' si existe wp en app, si no 'wpcli-service'
  if docker exec wp_app bash -lc 'command -v wp >/dev/null 2>&1'; then
    WPCLI_METHOD="wp_app"
  else
    WPCLI_METHOD="wpcli-service"
  fi
}

wp_cli_run(){
  # Ejecuta WP-CLI usando el método ya detectado en WPCLI_METHOD
  local args=("$@")
  case "$WPCLI_METHOD" in
    wp_app)
      docker exec wp_app bash -lc "wp --path=/var/www/html ${args[*]} 2>&1" || true ;;
    wpcli-service)
      compose_with_env "$USED_ENV_FILE" run --rm wpcli wp --path=/var/www/html "${args[@]}" 2>&1 || true ;;
    *)
      # Fallback: detectar al vuelo
      wp_cli_method_detect
      wp_cli_run "${args[@]}" ;;
  esac
}

strip_compose_noise(){
  # Elimina líneas de ruido generadas por docker compose run (Container/Network/Volume ...)
  sed -E '/^[[:space:]]*(Container|Network|Volume) /d'
}

remove_if_exists(){
  local type="$1"; shift
  local name
  for name in "$@"; do
    case "$type" in
      container)
        if docker ps -a --format '{{.Names}}' | grep -qx "$name"; then
          docker rm -f "$name" && echo "  - removed container: $name" || echo "  - error removing container: $name";
        fi ;;
      volume)
        if docker volume ls --format '{{.Name}}' | grep -qx "$name"; then
          docker volume rm "$name" && echo "  - removed volume: $name" || echo "  - error removing volume: $name";
        fi ;;
      network)
        if docker network ls --format '{{.Name}}' | grep -qx "$name"; then
          docker network rm "$name" && echo "  - removed network: $name" || echo "  - error removing network: $name";
        fi ;;
    esac
  done
}

# 1) Detectar configuración
if [[ -z "$COMPOSE_FILE" ]]; then
  echo "No se encontró archivo docker-compose en $DOCKER_DIR" >&2
fi

# 2) Estado actual
STATE_PRE="$(collect_state)"

# 3) Limpieza selectiva (solo nombres del proyecto)
REMOVED_LOG=""
{
  echo "## Recursos eliminados"
  remove_if_exists container wp_app wp_db wp_pma wp_cli
  remove_if_exists volume db_data wp_html
  # Red por defecto del proyecto (si existe). Suele llamarse 'docker_default'
  remove_if_exists network docker_default
} | tee >(REMOVED_LOG=$(cat); typeset -p REMOVED_LOG >/dev/null) >/dev/null || true

# 4) Preparar entorno y variables
ENV_FILE="${DOCKER_DIR}/.env"
USED_ENV_FILE="$ENV_FILE"
if [[ ! -f "$ENV_FILE" ]]; then
  USED_ENV_FILE="$SCRATCH_DIR/compose.dev.env"
  : > "$USED_ENV_FILE"
  {
    echo "# Variables generadas para dev local (sin secretos reales)"
    echo "MYSQL_VERSION=8.0"
    echo "MYSQL_DATABASE=wordpress"
    echo "MYSQL_USER=wpuser"
    echo "MYSQL_PASSWORD=wpuserpass"
    echo "MYSQL_ROOT_PASSWORD=rootpass"
    echo "WP_VERSION=6.8.2-php8.2-apache"
    echo "WP_PORT=8080"
    echo "PMA_PORT=8081"
    echo "WP_TABLE_PREFIX=wp_"
  } >> "$USED_ENV_FILE"
fi

ENV_PREVIEW="$(cat "$USED_ENV_FILE" | mask_secrets)"

# 4b) Build & Up
BUILD_OUT=""; UP_OUT=""; PS_OUT=""; LOGS_OUT=""
BUILD_RC=0; UP_RC=0
if [[ -n "$COMPOSE_FILE" ]]; then
  BUILD_OUT="$(compose_with_env "$USED_ENV_FILE" build --no-cache 2>&1)" || BUILD_RC=$?
  UP_OUT="$(compose_with_env "$USED_ENV_FILE" up -d 2>&1)" || UP_RC=$?
  PS_OUT="$(compose_with_env "$USED_ENV_FILE" ps 2>&1 || true)"
  LOGS_OUT="$(compose_with_env "$USED_ENV_FILE" logs --tail 50 2>&1 || true)"
fi

# 5) Verificación
WP_PORT_VAL="$(grep -E '^WP_PORT=' "$USED_ENV_FILE" | cut -d= -f2- || echo 8080)"
PMA_PORT_VAL="$(grep -E '^PMA_PORT=' "$USED_ENV_FILE" | cut -d= -f2- || echo 8081)"

THEME_INSIDE="/var/www/html/wp-content/themes/pepecapiro"
STYLE_INSIDE="$THEME_INSIDE/style.css"
THEME_LS="$(docker exec wp_app bash -lc "ls -la '$THEME_INSIDE' 2>/dev/null" 2>&1 || true)"
STYLE_CAT_HEAD="$(docker exec wp_app bash -lc "sed -n '1,20p' '$STYLE_INSIDE' 2>/dev/null" 2>&1 || true)"

LOCAL_STYLE_SHA="$(sha256sum "$LOCAL_STYLE" 2>/dev/null | awk '{print $1}' || echo ND)"
REMOTE_STYLE_SHA="$(docker exec wp_app bash -lc "sha256sum '$STYLE_INSIDE' 2>/dev/null" 2>&1 | awk '{print $1}' || true)"
[[ -z "$REMOTE_STYLE_SHA" ]] && REMOTE_STYLE_SHA="ND"

# HTTP smoke test
CURL_HOME="$(curl -sS -m 5 http://localhost:"$WP_PORT_VAL"/ 2>&1 || true)"

# 6) Servicios levantados
SERVICES_TABLE="$(docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | (grep -E '^(wp_db|wp_app|wp_pma|wp_cli)\b' || true))"

# Verificación/activación de tema con WP-CLI
WPCLI_METHOD="ND"
wp_cli_method_detect
CORE_IS_INSTALLED_OUT="$(wp_cli_run core is-installed)"
THEME_ACTIVE_JSON="$(wp_cli_run theme list --status=active --format=json | strip_compose_noise)"
THEME_IS_ACTIVE="no"
if echo "$THEME_ACTIVE_JSON" | grep -q '"name"\s*:\s*"pepecapiro"'; then
  THEME_IS_ACTIVE="si"
else
  ACTIVATE_OUT="$(wp_cli_run theme activate pepecapiro)"
  THEME_ACTIVE_JSON_POST="$(wp_cli_run theme list --status=active --format=json | strip_compose_noise)"
  if echo "$THEME_ACTIVE_JSON_POST" | grep -q '"name"\s*:\s*"pepecapiro"'; then
    THEME_IS_ACTIVE="si (activado por script)"
  else
    THEME_IS_ACTIVE="no (intento de activación fallido)"
  fi
fi

# 7) Generar reporte
{
  echo "===== BEGIN DOCKER CHECK ====="
  echo "# Docker check pepecapiro.com (local)"
  echo
  echo "Generado: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Workspace: $REPO_ROOT"
  echo
  echo "## 1) Configuración detectada"
  echo "- Compose file: ${COMPOSE_FILE:-ND}"
  echo "- .env usado (enmascarado):"
  echo '```env'
  echo "$ENV_PREVIEW"
  echo '```'
  echo
  echo "## 2) Estado previo"
  echo "$STATE_PRE"
  echo
  echo "## 3) Limpieza aplicada"
  echo "(solo recursos de este proyecto)"
  echo "$REMOVED_LOG"
  echo
  echo "## 4) Build & Up"
  echo "- Build rc: $BUILD_RC"
  echo '```'
  echo "$BUILD_OUT" | tail -n 50
  echo '```'
  echo "- Up rc: $UP_RC"
  echo '```'
  echo "$UP_OUT"
  echo '```'
  echo
  echo "## 5) Servicios levantados"
  echo '```'
  echo "$SERVICES_TABLE"
  echo '```'
  echo
  echo "### Verificación de tema activo (WP-CLI)"
  echo "- Método WP-CLI: $WPCLI_METHOD"
  if echo "$CORE_IS_INSTALLED_OUT" | grep -qi 'not installed'; then
    echo "- core is-installed: NO"
  elif [[ -n "$CORE_IS_INSTALLED_OUT" ]]; then
    echo "- core is-installed: SI"
  else
    echo "- core is-installed: ND"
  fi
  echo "- Estado: $THEME_IS_ACTIVE"
  echo "- wp theme list --status=active (json):"
  echo '```json'
  echo "${THEME_ACTIVE_JSON_POST:-$THEME_ACTIVE_JSON}"
  echo '```'
  if [[ -n "${ACTIVATE_OUT:-}" ]]; then
    echo "- Salida de activación:"
    echo '```'
    echo "$ACTIVATE_OUT"
    echo '```'
  fi
  echo
  echo "## 6) Logs de arranque (últimas 50 líneas)"
  echo '```'
  echo "$LOGS_OUT"
  echo '```'
  echo
  echo "## 7) Validación del tema pepecapiro"
  echo "- Ruta en contenedor: $THEME_INSIDE"
  echo '```'
  echo "$THEME_LS"
  echo '```'
  echo "- style.css (primeras líneas):"
  echo '```'
  echo "$STYLE_CAT_HEAD"
  echo '```'
  echo "- SHA256 local: $LOCAL_STYLE_SHA"
  echo "- SHA256 en contenedor: $REMOTE_STYLE_SHA"
  if [[ "$LOCAL_STYLE_SHA" != "ND" && "$REMOTE_STYLE_SHA" != "ND" ]]; then
    if [[ "$LOCAL_STYLE_SHA" == "$REMOTE_STYLE_SHA" ]]; then echo "- Resultado: MATCH"; else echo "- Resultado: DIFF"; fi
  else
    echo "- Resultado: ND (no se pudo calcular)"
  fi
  echo
  echo "## 8) Smoke test HTTP"
  echo "- URL: http://localhost:$WP_PORT_VAL/"
  echo "- HTML recibido (primeras líneas):"
  echo '```html'
  echo "$CURL_HOME" | sed -n '1,30p'
  echo '```'
  echo
  echo "=====  END  DOCKER CHECK ====="
} | tee "$REPORT_PATH"

exit 0
