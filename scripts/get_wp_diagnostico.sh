#!/usr/bin/env bash
# Objetivo: Generar un informe ÚNICO y COMPLETO del entorno local (WSL/Ubuntu + VS Code)
# y del WordPress remoto (Hostinger) enfocado en tema "pepecapiro" y WPForms.
# Reglas: Solo lectura, sin cambios en sistemas. Enmascarar secretos. Continuar ante errores.

set -u

# ============================
# Configuración de variables
# ============================
SSH_ALIAS="pepecapiro"
SSH_PORT="65002"
SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

# Directorios y rutas
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SCRATCH_DIR="$REPO_ROOT/_scratch"
REPORT_PATH="$SCRATCH_DIR/estado_local_remoto.md"

# Asegurar scratch
mkdir -p "$SCRATCH_DIR"

# Registro de comandos ejecutados (solo para volcar en el informe)
declare -a CMD_LOG
log_cmd() {
  CMD_LOG+=("$1")
}

# Utilidad: ejecutar comando y capturar salida/estado sin abortar
run_cmd() {
  local desc="$1"; shift
  local cmd=("$@")
  log_cmd "${cmd[*]}" 
  local out err rc
  out="$("${cmd[@]}" 2> >(err=$(cat); typeset -p err >/dev/null) )" || rc=$?
  rc=${rc:-0}
  if [[ $rc -ne 0 ]]; then
    echo "[ERROR:$rc] $desc"$'\n'"STDOUT:"$'\n'"${out:-}"$'\n'"STDERR:"$'\n'"${err:-}"$'\n'"" 
  else
    echo "$out"
  fi
  return 0
}

# Utilidad: ejecutar por SSH
ssh_run() {
  local desc="$1"; shift
  local remote_cmd="$*"
  local ssh_cmd=(ssh -p "$SSH_PORT" "$SSH_ALIAS" "$remote_cmd")
  log_cmd "ssh -p $SSH_PORT $SSH_ALIAS $remote_cmd"
  local out err rc
  out="$("${ssh_cmd[@]}" 2> >(err=$(cat); typeset -p err >/dev/null) )" || rc=$?
  rc=${rc:-0}
  if [[ $rc -ne 0 ]]; then
    echo "[ERROR:$rc] $desc"$'\n'"STDOUT:"$'\n'"${out:-}"$'\n'"STDERR:"$'\n'"${err:-}"$'\n'"" 
  else
    echo "$out"
  fi
  return 0
}

# Enmascarar posibles secretos en JSON de sftp.json sin depender de jq
mask_secrets() {
  sed -E \
    -e 's/("password"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("passphrase"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("privateKey"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("secret"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/([Pp]assword=)[^"\s]*/\1****/g'
}

# Detección WSL
detect_wsl() {
  if grep -qi 'microsoft' /proc/version 2>/dev/null || uname -r | grep -qi 'microsoft'; then
    echo "WSL: yes"
  else
    echo "WSL: no"
  fi
}

# Obtener versión si existe el binario
bin_version() {
  local bin="$1"; shift || true
  if command -v "$bin" >/dev/null 2>&1; then
    case "$bin" in
      ssh) ssh -V 2>&1 | head -n1 ;;
      php) php -v 2>&1 | head -n1 ;;
      node) node -v 2>&1 | head -n1 ;;
      python3) python3 -V 2>&1 | head -n1 ;;
      wp) wp --info 2>&1 | sed -n '1,6p' ;;
      composer) composer -V 2>&1 | head -n1 ;;
      *) "$bin" --version 2>&1 | head -n1 || "$bin" -v 2>&1 | head -n1 ;;
    esac
  else
    echo "$bin: ND (no encontrado)"
  fi
}

# Buscar rutas locales relevantes
find_local_theme_paths() {
  local base="$REPO_ROOT"
  # 1) wp-content/themes/pepecapiro
  find "$base" -type d -path "*/wp-content/themes/pepecapiro" 2>/dev/null
  # 2) directorios llamados exactamente pepecapiro
  find "$base" -type d -name "pepecapiro" 2>/dev/null
}

# Info de archivos clave: sha256 y mtime
file_info_block() {
  local dir="$1"
  local -a files=(style.css functions.php index.php header.php footer.php screenshot.png)
  for f in "${files[@]}"; do
    local p="$dir/$f"
    if [[ -f "$p" ]]; then
      local shasum mtime
      shasum="$(sha256sum "$p" 2>/dev/null | awk '{print $1}')"
      mtime="$(stat -c '%y' "$p" 2>/dev/null || echo ND)"
      echo "- $f"
      printf "  - path: %s\n  - sha256: %s\n  - mtime: %s\n" "$p" "${shasum:-ND}" "${mtime:-ND}"
    else
      echo "- $f"
      printf "  - path: %s\n  - sha256: ND\n  - mtime: ND\n" "$p"
    fi
  done
}

# Comparativa local vs remoto (usa el primer path local encontrado si existe)
compare_hashes() {
  local local_dir="$1"
  local remote_dir="$SITE_ROOT/wp-content/themes/pepecapiro"
  local -a files=(style.css functions.php index.php header.php footer.php screenshot.png)
  printf "| Archivo | Local SHA256 | Remoto SHA256 | MATCH/DIFF |\n"
  printf "|---|---|---|---|\n"
  for f in "${files[@]}"; do
    local lf="$local_dir/$f"
    local lhash="ND"
    [[ -f "$lf" ]] && lhash="$(sha256sum "$lf" 2>/dev/null | awk '{print $1}')"
    local rhash_out
    rhash_out="$(ssh_run "sha256 remoto $f" "[ -f '$remote_dir/$f' ] && sha256sum '$remote_dir/$f' || echo ND")"
    local rhash
    if echo "$rhash_out" | grep -q '^\[ERROR:'; then
      rhash="ND"
    else
      rhash="$(echo "$rhash_out" | awk '{print $1}' | head -n1)"
      [[ -z "$rhash" ]] && rhash="ND"
    fi
    local match="ND"
    if [[ "$lhash" != "ND" && "$rhash" != "ND" ]]; then
      if [[ "$lhash" == "$rhash" ]]; then match="MATCH"; else match="DIFF"; fi
    fi
    printf "| %s | %s | %s | %s |\n" "$f" "$lhash" "$rhash" "$match"
  done
}

# ============================
# Recolección Local
# ============================
LOCAL_OS_NAME="$(. /etc/os-release 2>/dev/null; echo "${NAME:-ND} ${VERSION:-}" )"
LOCAL_KERNEL="$(uname -srm 2>/dev/null || echo ND)"
LOCAL_WSL="$(detect_wsl)"

SSH_VER="$(bin_version ssh)"
PHP_VER="$(bin_version php)"
NODE_VER="$(bin_version node)"
PY3_VER="$(bin_version python3)"
WP_INFO="$(bin_version wp)"
COMPOSER_VER="$(bin_version composer)"

WORKSPACE_DIR="$REPO_ROOT"
THEME_PATHS="$(find_local_theme_paths | sort -u)"
PRIMARY_LOCAL_THEME_DIR="$(echo "$THEME_PATHS" | head -n1)"

SFTP_JSON_PATH="$REPO_ROOT/.vscode/sftp.json"
SFTP_JSON_MASKED="ND"
SFTP_JSON_NOTES=""
if [[ -f "$SFTP_JSON_PATH" ]]; then
  SFTP_JSON_MASKED="$(cat "$SFTP_JSON_PATH" | mask_secrets)"
  # Comprobación básica de campos esperados
  for key in host username remotePath port protocol; do
    if ! echo "$SFTP_JSON_MASKED" | grep -q '"'"$key"'"'; then
      SFTP_JSON_NOTES+="Falta campo: $key; "
    fi
  done
fi

# ============================
# Recolección Remota (SSH)
# ============================
REMOTE_SITEURL="$(ssh_run "wp option get siteurl" "cd '$SITE_ROOT' && wp option get siteurl 2>&1")"
REMOTE_CORE_VER="$(ssh_run "wp core version" "cd '$SITE_ROOT' && wp core version 2>&1")"
REMOTE_PHP_VER="$(ssh_run "PHP_VERSION" "php -r 'echo PHP_VERSION;' 2>/dev/null || echo ND")"
REMOTE_THEME_ACTIVE_JSON="$(ssh_run "wp theme list --status=active" "cd '$SITE_ROOT' && wp theme list --status=active --format=json 2>&1")"
REMOTE_THEME_ALL_JSON="$(ssh_run "wp theme list" "cd '$SITE_ROOT' && wp theme list --format=json 2>&1")"
REMOTE_PLUGIN_LIST_JSON="$(ssh_run "wp plugin list" "cd '$SITE_ROOT' && wp plugin list --format=json 2>&1")"
REMOTE_PLUGIN_ACTIVE_JSON="$(ssh_run "wp plugin list --status=active" "cd '$SITE_ROOT' && wp plugin list --status=active --format=json 2>&1")"
REMOTE_WPFORMS_VER="$(ssh_run "wp plugin get wpforms" "cd '$SITE_ROOT' && wp plugin get wpforms --field=version 2>&1 || true")"
REMOTE_WPFORMS_LITE_VER="$(ssh_run "wp plugin get wpforms-lite" "cd '$SITE_ROOT' && wp plugin get wpforms-lite --field=version 2>&1 || true")"
REMOTE_POST9_CONTENT="$(ssh_run "wp post get 9" "cd '$SITE_ROOT' && wp post get 9 --field=post_content 2>&1 || true")"
REMOTE_POST15_CONTENT="$(ssh_run "wp post get 15" "cd '$SITE_ROOT' && wp post get 15 --field=post_content 2>&1 || true")"
REMOTE_CONTACTO_HTML="$(ssh_run "curl contacto" "curl -sS https://pepecapiro.com/contacto || true")"
REMOTE_CONTACT_HTML="$(ssh_run "curl contact" "curl -sS https://pepecapiro.com/contact || true")"

REMOTE_LS_THEME="$(ssh_run "ls themes/pepecapiro" "ls -la '$SITE_ROOT/wp-content/themes/pepecapiro' 2>&1 || true")"
REMOTE_LS_MU="$(ssh_run "ls mu-plugins" "ls -la '$SITE_ROOT/wp-content/mu-plugins' 2>&1 || true")"
REMOTE_LS_WPFORMS="$(ssh_run "ls plugins|grep wpforms" "ls -la '$SITE_ROOT/wp-content/plugins' 2>/dev/null | grep -i wpforms || true")"

REMOTE_DEBUG_TAIL="$(ssh_run "tail debug.log" "[ -f '$SITE_ROOT/wp-content/debug.log' ] && tail -n 200 '$SITE_ROOT/wp-content/debug.log' || echo 'ND' 2>/dev/null")"
REMOTE_DEBUG_GREP="$(ssh_run "grep wpforms|square" "[ -f '$SITE_ROOT/wp-content/debug.log' ] && grep -inE 'wpforms|square' '$SITE_ROOT/wp-content/debug.log' | sed -n '1,10p' || echo 'ND' 2>/dev/null")"
REMOTE_DEBUG_GREP_COUNT="$(ssh_run "count grep" "[ -f '$SITE_ROOT/wp-content/debug.log' ] && grep -inE 'wpforms|square' '$SITE_ROOT/wp-content/debug.log' | wc -l || echo '0' 2>/dev/null")"

# ============================
# Derivados: hallazgos clave, shortcode, etc.
# ============================
detect_shortcode() {
  local content="$1"
  echo "$content" | tr -d '\r' | grep -o -i '\[wpforms[^]]*\]' | head -n1 || true
}

SHORTCODE_9="$(detect_shortcode "$REMOTE_POST9_CONTENT")"
SHORTCODE_15="$(detect_shortcode "$REMOTE_POST15_CONTENT")"
SHORTCODE_CONTACTO_HTML="$(detect_shortcode "$REMOTE_CONTACTO_HTML")"
SHORTCODE_CONTACT_HTML="$(detect_shortcode "$REMOTE_CONTACT_HTML")"

# Tema activo remoto (intento parseo simple del JSON)
REMOTE_ACTIVE_THEME="$(echo "$REMOTE_THEME_ACTIVE_JSON" | tr -d '\r' | sed -n 's/.*"name"\s*:\s*"\([^"]*\)".*/\1/p' | head -n1)"
[[ -z "$REMOTE_ACTIVE_THEME" ]] && REMOTE_ACTIVE_THEME="ND"

# Versiones WPForms limpias (si error, dejar ND)
clean_ver() {
  local v="$1"
  if echo "$v" | grep -q '^\[ERROR:'; then echo ND; else echo "$v" | tr -d '\r' | head -n1; fi
}
WPFORMS_VER_CLEAN="$(clean_ver "$REMOTE_WPFORMS_VER")"
WPFORMS_LITE_VER_CLEAN="$(clean_ver "$REMOTE_WPFORMS_LITE_VER")"

# Resumen de logs
LOG_HITS="$REMOTE_DEBUG_GREP_COUNT"
if echo "$LOG_HITS" | grep -q '^\[ERROR:'; then LOG_HITS="ND"; else LOG_HITS="$(echo "$LOG_HITS" | tr -d '\r' | head -n1)"; fi

# Señales para resumen crítico
HAS_LOCAL_THEME="no"
[[ -n "$PRIMARY_LOCAL_THEME_DIR" ]] && HAS_LOCAL_THEME="sí"
CRIT_NOTES=()
if [[ "$REMOTE_ACTIVE_THEME" != "pepecapiro" && "$REMOTE_ACTIVE_THEME" != "ND" ]]; then CRIT_NOTES+=("Tema activo remoto no es 'pepecapiro' (es '$REMOTE_ACTIVE_THEME')"); fi
if [[ "$HAS_LOCAL_THEME" == "no" ]]; then CRIT_NOTES+=("No se detectó tema local 'pepecapiro' en el workspace"); fi
# Detección de estado WPForms activo
ACTIVE_WPFORMS=$(echo "$REMOTE_PLUGIN_ACTIVE_JSON" | tr -d '\r' | grep -o '"name"\s*:\s*"wpforms"' | head -n1 || true)
ACTIVE_WPFORMS_LITE=$(echo "$REMOTE_PLUGIN_ACTIVE_JSON" | tr -d '\r' | grep -o '"name"\s*:\s*"wpforms-lite"' | head -n1 || true)
if [[ -n "$ACTIVE_WPFORMS" && -n "$ACTIVE_WPFORMS_LITE" ]]; then CRIT_NOTES+=("Ambos plugins wpforms y wpforms-lite activos a la vez"); fi
if [[ -z "$ACTIVE_WPFORMS" && -z "$ACTIVE_WPFORMS_LITE" ]]; then CRIT_NOTES+=("Ningún plugin WPForms activo, pero existen shortcodes en páginas de contacto") ; fi
if [[ "$LOG_HITS" != "0" && "$LOG_HITS" != "ND" ]]; then CRIT_NOTES+=("debug.log contiene $LOG_HITS entradas que mencionan 'wpforms' o 'square'"); fi

join_by() { local IFS=", "; echo "$*"; }

# ============================
# Construcción del reporte
# ============================
{
  echo "===== BEGIN ESTADO ====="
  echo "# Estado local y remoto: pepecapiro.com"
  echo
  echo "Generado: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Workspace: $WORKSPACE_DIR"
  echo
  echo "## 1) Resumen ejecutivo"
  echo "- Tema (remoto/local): activo remoto='${REMOTE_ACTIVE_THEME:-ND}' | local='${PRIMARY_LOCAL_THEME_DIR:-ND}'"
  echo "- WordPress/PHP: WP=$(echo "$REMOTE_CORE_VER" | head -n1) | siteurl=$(echo "$REMOTE_SITEURL" | head -n1) | PHP=$(echo "$REMOTE_PHP_VER" | head -n1)"
  echo "- Plugins WPForms: wpforms=${WPFORMS_VER_CLEAN:-ND} | wpforms-lite=${WPFORMS_LITE_VER_CLEAN:-ND} | activos: wpforms=$([[ -n $ACTIVE_WPFORMS ]] && echo si || echo no) / wpforms-lite=$([[ -n $ACTIVE_WPFORMS_LITE ]] && echo si || echo no)"
  echo "- Shortcodes/contacto: post(ID9)='${SHORTCODE_9:-ND}' | post(ID15)='${SHORTCODE_15:-ND}' | HTML(/contacto)='${SHORTCODE_CONTACTO_HTML:-ND}' | HTML(/contact)='${SHORTCODE_CONTACT_HTML:-ND}'"
  echo "- debug.log menciones (wpforms/square): ${LOG_HITS}"
  if [[ ${#CRIT_NOTES[@]} -gt 0 ]]; then
    echo "- Diferencias/alertas críticas:"
    for n in "${CRIT_NOTES[@]}"; do echo "  - $n"; done
  else
    echo "- Diferencias/alertas críticas: ninguna obvia detectada"
  fi
  echo "- Comparativa de hashes incluida en la sección 4"
  echo
  echo "## 2) Estado local (VS Code + WSL)"
  echo "- OS: $LOCAL_OS_NAME | Kernel: $LOCAL_KERNEL | $(echo "$LOCAL_WSL")"
  echo "- Herramientas:"
  echo "  - $(echo "$SSH_VER" | head -n1)"
  echo "  - $(echo "$PHP_VER" | head -n1)"
  echo "  - $(echo "$NODE_VER" | head -n1)"
  echo "  - $(echo "$PY3_VER" | head -n1)"
  echo "  - WP CLI local: $(echo "$WP_INFO" | head -n1)"
  echo "  - $(echo "$COMPOSER_VER" | head -n1)"
  echo "- Carpeta de workspace (absoluta): $WORKSPACE_DIR"
  echo "- Directorios que coinciden con 'wp-content/themes/pepecapiro' o llamados 'pepecapiro':"
  if [[ -n "$THEME_PATHS" ]]; then echo "$THEME_PATHS" | sed 's/^/- /'; else echo "  - ND"; fi
  echo "- Archivos clave del tema local:"
  if [[ -n "$PRIMARY_LOCAL_THEME_DIR" ]]; then
    file_info_block "$PRIMARY_LOCAL_THEME_DIR"
  else
    echo "  - ND"
  fi
  echo "- VS Code .vscode/sftp.json (enmascarado):"
  if [[ -f "$SFTP_JSON_PATH" ]]; then
    echo '```json'
    echo "$SFTP_JSON_MASKED"
    echo '```'
    [[ -n "$SFTP_JSON_NOTES" ]] && echo "  - Notas: $SFTP_JSON_NOTES"
  else
    echo "  - ND (no existe)"
  fi
  echo "- Existencia de settings.json/tasks.json:" 
  [[ -f "$REPO_ROOT/.vscode/settings.json" ]] && echo "  - settings.json: sí" || echo "  - settings.json: no"
  [[ -f "$REPO_ROOT/.vscode/tasks.json" ]] && echo "  - tasks.json: sí" || echo "  - tasks.json: no"
  echo
  echo "## 3) Estado remoto (Hostinger/WordPress)"
  echo "- siteurl: $(echo "$REMOTE_SITEURL" | head -n1)"
  echo "- WordPress core: $(echo "$REMOTE_CORE_VER" | head -n1)"
  echo "- PHP versión: $(echo "$REMOTE_PHP_VER" | head -n1)"
  echo
  echo "- Tema activo (json):"
  echo '```json'
  echo "$REMOTE_THEME_ACTIVE_JSON"
  echo '```'
  echo "- Temas instalados (json):"
  echo '```json'
  echo "$REMOTE_THEME_ALL_JSON"
  echo '```'
  echo "- Plugins instalados (json):"
  echo '```json'
  echo "$REMOTE_PLUGIN_LIST_JSON"
  echo '```'
  echo "- Plugins activos (json):"
  echo '```json'
  echo "$REMOTE_PLUGIN_ACTIVE_JSON"
  echo '```'
  echo "- WPForms versiones detectadas:"
  echo "  - wpforms: ${WPFORMS_VER_CLEAN}"
  echo "  - wpforms-lite: ${WPFORMS_LITE_VER_CLEAN}"
  echo
  echo "- Directorios remotos relevantes (ls -la):"
  echo "  - $SITE_ROOT/wp-content/themes/pepecapiro"
  echo '```'
  echo "$REMOTE_LS_THEME"
  echo '```'
  echo "  - $SITE_ROOT/wp-content/mu-plugins"
  echo '```'
  echo "$REMOTE_LS_MU"
  echo '```'
  echo "  - $SITE_ROOT/wp-content/plugins | grep -i wpforms"
  echo '```'
  echo "$REMOTE_LS_WPFORMS"
  echo '```'
  echo
  echo "- Páginas de contacto (para detectar shortcodes)"
  echo "  - Post ID 9 (/contacto) - contenido (WP-CLI)"
  echo '```html'
  echo "$REMOTE_POST9_CONTENT"
  echo '```'
  echo "  - Post ID 15 (/contact) - contenido (WP-CLI)"
  echo '```html'
  echo "$REMOTE_POST15_CONTENT"
  echo '```'
  echo "  - HTML público /contacto (fragmentos con '[wpforms')"
  echo '```html'
  echo "$REMOTE_CONTACTO_HTML" | tr -d '\r' | grep -inF '[wpforms' -m 5 || echo "(sin coincidencias)"
  echo '```'
  echo "  - HTML público /contact (fragmentos con '[wpforms')"
  echo '```html'
  echo "$REMOTE_CONTACT_HTML" | tr -d '\r' | grep -inF '[wpforms' -m 5 || echo "(sin coincidencias)"
  echo '```'
  echo
  echo "- Logs wp-content/debug.log:"
  echo "  - Últimas 200 líneas:"
  echo '```'
  echo "$REMOTE_DEBUG_TAIL"
  echo '```'
  echo "  - Conteo de líneas con 'wpforms' y/o 'square': $LOG_HITS"
  echo "  - Ejemplos (máx 10):"
  echo '```'
  echo "$REMOTE_DEBUG_GREP"
  echo '```'
  echo
  echo "## 4) Comparativa local vs remoto"
  if [[ -n "$PRIMARY_LOCAL_THEME_DIR" ]]; then
    compare_hashes "$PRIMARY_LOCAL_THEME_DIR"
  else
    echo "ND (no se detectó tema local)"
  fi
  echo
  echo "- Notas sobre otros desajustes:"
  echo "  - Tema activo remoto: $REMOTE_ACTIVE_THEME"
  echo "  - WPForms activo: wpforms=$([[ -n $ACTIVE_WPFORMS ]] && echo si || echo no), wpforms-lite=$([[ -n $ACTIVE_WPFORMS_LITE ]] && echo si || echo no)"
  echo "  - WPForms versiones: wpforms=${WPFORMS_VER_CLEAN}, wpforms-lite=${WPFORMS_LITE_VER_CLEAN}"
  echo
  echo "## 5) Observaciones y riesgos"
  if [[ ${#CRIT_NOTES[@]} -gt 0 ]]; then
    for n in "${CRIT_NOTES[@]}"; do echo "- $n"; done
  else
    echo "- Sin hallazgos críticos evidentes."
  fi
  echo "- Potenciales causas: shortcode con ID inexistente, conflicto wpforms/wpforms-lite, diferencias de tema entre local y remoto, integración Square incompleta."
  echo
  echo "## 6) Recomendaciones iniciales"
  echo "- Opción A: Tomar REMOTO como fuente de verdad"
  echo "  - Respaldar wp-content (temas, plugins) y base de datos"
  echo "  - Sincronizar local con versiones y hashes remotos"
  echo "  - Confirmar solo un plugin WPForms activo (completo o lite)"
  echo "- Opción B: Tomar LOCAL como fuente de verdad"
  echo "  - Asegurar que el tema local está completo y probado"
  echo "  - Plan de despliegue: subir tema, revisar compatibilidades y limpiar cache"
  echo "  - Confirmar shortcodes y formularios existentes/activos"
  echo "- Checklist previo a alineación:"
  echo "  - Copias de seguridad recientes (archivos + DB)"
  echo "  - debug.log rotado/limpio para validar nuevos errores"
  echo "  - Identificar plugins críticos (SEO, caché, seguridad)"
  echo "  - Confirmar entorno de mantenimiento (ventana y rollback)"
  echo
  echo "## Anexos"
  echo "- Rutas locales detectadas:"
  if [[ -n "$THEME_PATHS" ]]; then echo "$THEME_PATHS" | sed 's/^/- /'; else echo "  - ND"; fi
  echo "- Valores de entorno usados:"
  echo "  - SSH_ALIAS=$SSH_ALIAS"
  echo "  - SSH_PORT=$SSH_PORT"
  echo "  - SITE_ROOT=$SITE_ROOT"
  echo "  - WORKSPACE_DIR=$WORKSPACE_DIR"
  echo "- Comandos ejecutados (sin secretos):"
  for c in "${CMD_LOG[@]}"; do echo "  - $c"; done
  echo
  echo "=====  END  ESTADO ====="
} | tee "$REPORT_PATH"

exit 0
