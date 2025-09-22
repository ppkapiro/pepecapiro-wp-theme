#!/usr/bin/env bash
# Diagnóstico profundo (solo lectura) local/remoto para pepecapiro.com
# Incluye: Docker local, diff style.css, plugins/formularios, y reporte extendido.

set -u

# ============================
# Configuración
# ============================
SSH_ALIAS="pepecapiro"
SSH_PORT="65002"
SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SCRATCH_DIR="$REPO_ROOT/_scratch"
REPORT_PATH="$SCRATCH_DIR/diagnostico_profundo.md"
mkdir -p "$SCRATCH_DIR"

declare -a CMD_LOG
log_cmd(){ CMD_LOG+=("$1"); }

run_cmd(){
  local desc="$1"; shift
  local cmd=("$@")
  log_cmd "${cmd[*]}"
  local out err rc
  out="$(${cmd[@]} 2> >(err=$(cat); typeset -p err >/dev/null))" || rc=$?
  rc=${rc:-0}
  if [[ $rc -ne 0 ]]; then
    echo "[ERROR:$rc] $desc"$'\n'"STDOUT:"$'\n'"${out:-}"$'\n'"STDERR:"$'\n'"${err:-}"$'\n'""
  else
    echo "$out"
  fi
  return 0
}

ssh_run(){
  local desc="$1"; shift
  local remote_cmd="$*"
  local ssh_cmd=(ssh -p "$SSH_PORT" "$SSH_ALIAS" "$remote_cmd")
  log_cmd "ssh -p $SSH_PORT $SSH_ALIAS $remote_cmd"
  local out err rc
  out="$(${ssh_cmd[@]} 2> >(err=$(cat); typeset -p err >/dev/null))" || rc=$?
  rc=${rc:-0}
  if [[ $rc -ne 0 ]]; then
    echo "[ERROR:$rc] $desc"$'\n'"STDOUT:"$'\n'"${out:-}"$'\n'"STDERR:"$'\n'"${err:-}"$'\n'""
  else
    echo "$out"
  fi
  return 0
}

detect_wsl(){ if grep -qi 'microsoft' /proc/version 2>/dev/null || uname -r | grep -qi 'microsoft'; then echo "WSL: yes"; else echo "WSL: no"; fi; }

bin_version(){
  local bin="$1"
  if command -v "$bin" >/dev/null 2>&1; then
    case "$bin" in
      ssh) ssh -V 2>&1 | head -n1 ;;
      php) php -v 2>&1 | head -n1 ;;
      node) node -v 2>&1 | head -n1 ;;
      python3) python3 -V 2>&1 | head -n1 ;;
      composer) composer -V 2>&1 | head -n1 ;;
      docker) docker --version 2>&1 | head -n1 ;;
      *) "$bin" --version 2>&1 | head -n1 || "$bin" -v 2>&1 | head -n1 ;;
    esac
  else
    echo "$bin: ND (no encontrado)"
  fi
}

find_local_theme_paths(){
  local base="$REPO_ROOT"
  find "$base" -type d -path "*/wp-content/themes/pepecapiro" 2>/dev/null
  find "$base" -type d -name "pepecapiro" 2>/dev/null
}

file_info_block(){
  local dir="$1"; local -a files=(style.css functions.php index.php header.php footer.php screenshot.png)
  for f in "${files[@]}"; do
    local p="$dir/$f"
    if [[ -f "$p" ]]; then
      local shasum mtime
      shasum="$(sha256sum "$p" 2>/dev/null | awk '{print $1}')"
      mtime="$(stat -c '%y' "$p" 2>/dev/null || echo ND)"
      echo "- $f"; printf "  - path: %s\n  - sha256: %s\n  - mtime: %s\n" "$p" "${shasum:-ND}" "${mtime:-ND}"
    else
      echo "- $f"; printf "  - path: %s\n  - sha256: ND\n  - mtime: ND\n" "$p"
    fi
  done
}

compare_hashes(){
  local local_dir="$1"; local remote_dir="$SITE_ROOT/wp-content/themes/pepecapiro"
  local -a files=(style.css functions.php index.php header.php footer.php screenshot.png)
  printf "| Archivo | Local SHA256 | Remoto SHA256 | MATCH/DIFF |\n"; printf "|---|---|---|---|\n"
  for f in "${files[@]}"; do
    local lf="$local_dir/$f"; local lhash="ND"; [[ -f "$lf" ]] && lhash="$(sha256sum "$lf" | awk '{print $1}')"
    local ro
    ro="$(ssh_run "sha256 $f" "[ -f '$remote_dir/$f' ] && sha256sum '$remote_dir/$f' || echo ND")"
    local rhash; if echo "$ro" | grep -q '^\[ERROR:'; then rhash="ND"; else rhash="$(echo "$ro" | awk '{print $1}' | head -n1)"; [[ -z "$rhash" ]] && rhash="ND"; fi
    local match="ND"; if [[ "$lhash" != ND && "$rhash" != ND ]]; then [[ "$lhash" == "$rhash" ]] && match=MATCH || match=DIFF; fi
    printf "| %s | %s | %s | %s |\n" "$f" "$lhash" "$rhash" "$match"
  done
}

# ============================
# Recolección local
# ============================
LOCAL_OS_NAME="$(. /etc/os-release 2>/dev/null; echo "${NAME:-ND} ${VERSION:-}")"
LOCAL_KERNEL="$(uname -srm 2>/dev/null || echo ND)"
LOCAL_WSL="$(detect_wsl)"

SSH_VER="$(bin_version ssh)"; PHP_VER="$(bin_version php)"; NODE_VER="$(bin_version node)"; PY3_VER="$(bin_version python3)"; COMPOSER_VER="$(bin_version composer)"; DOCKER_VER="$(bin_version docker)"

WORKSPACE_DIR="$REPO_ROOT"
THEME_PATHS="$(find_local_theme_paths | sort -u)"
PRIMARY_LOCAL_THEME_DIR="$(echo "$THEME_PATHS" | head -n1)"
LOCAL_STYLE_PATH=""; [[ -n "$PRIMARY_LOCAL_THEME_DIR" ]] && LOCAL_STYLE_PATH="$PRIMARY_LOCAL_THEME_DIR/style.css"

# Docker: detección de archivos
readarray -t DOCKERFILES < <(find "$REPO_ROOT" -type f \( -name 'Dockerfile' -o -name 'docker-compose.yml' -o -name 'docker-compose.yaml' -o -name 'compose.yml' -o -name 'compose.yaml' \) 2>/dev/null | sort)

docker_section(){
  echo "- Docker bin: $(echo "$DOCKER_VER" | head -n1)"
  # Compose version (plugin v2 o binario v1)
  local compose_ver; compose_ver=$(docker compose version 2>&1 | head -n1 || true)
  if [[ -z "$compose_ver" ]]; then compose_ver=$(docker-compose --version 2>&1 | head -n1 || echo "docker compose: ND"); fi
  echo "- Docker Compose: $compose_ver"

  if command -v docker >/dev/null 2>&1; then
    echo "- Contenedores en ejecución:"; docker ps --format '{{.Names}} | {{.Image}} | {{.Status}} | {{.Ports}}' 2>/dev/null || echo "ND"
    echo "- Contenedores detenidos (top 10 por fecha):"; docker ps -a --format '{{.Names}} | {{.Image}} | {{.Status}}' --no-trunc 2>/dev/null | head -n 10 || echo "ND"
    echo "- Imágenes locales (top 10):"; docker images --format '{{.Repository}}:{{.Tag}} | {{.ID}} | {{.Size}}' 2>/dev/null | head -n 10 || echo "ND"
    echo "- Volúmenes:"; docker volume ls 2>/dev/null || echo "ND"
    echo "- Redes (top 10):"; docker network ls 2>/dev/null | head -n 10 || echo "ND"
  else
    echo "- Docker no disponible localmente"
  fi

  echo "- Archivos Docker/Compose detectados:"; if [[ ${#DOCKERFILES[@]} -gt 0 ]]; then for f in "${DOCKERFILES[@]}"; do echo "  - $f"; done; else echo "  - ND"; fi

  # Servicios definidos por compose (mejor esfuerzo, no ejecuta contenedores)
  if command -v docker >/dev/null 2>&1; then
    for f in "${DOCKERFILES[@]}"; do
      case "$f" in *compose*.y*ml)
        echo "- Servicios definidos en $f:";
        docker compose -f "$f" config --services 2>/dev/null || docker-compose -f "$f" config --services 2>/dev/null || echo "  (No disponible)";
        echo "- Estado compose ps para $f:";
        docker compose -f "$f" ps 2>/dev/null || docker-compose -f "$f" ps 2>/dev/null || echo "  (No disponible)";
        ;;
      esac
    done
  fi
}

# ============================
# Recolección remota
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
REMOTE_FORMS_JSON="$(ssh_run "listar formularios json" "cd '$SITE_ROOT' && wp post list --post_type=wpforms --fields=ID,post_title,post_status --format=json 2>&1 || true")"
REMOTE_FORMS_TABLE="$(ssh_run "listar formularios table" "cd '$SITE_ROOT' && wp post list --post_type=wpforms --fields=ID,post_title,post_status --format=table 2>&1 || true")"

REMOTE_POST9_CONTENT="$(ssh_run "wp post get 9" "cd '$SITE_ROOT' && wp post get 9 --field=post_content 2>&1 || true")"
REMOTE_POST15_CONTENT="$(ssh_run "wp post get 15" "cd '$SITE_ROOT' && wp post get 15 --field=post_content 2>&1 || true")"
REMOTE_CONTACTO_HTML="$(ssh_run "curl contacto" "curl -sS https://pepecapiro.com/contacto || true")"
REMOTE_CONTACT_HTML="$(ssh_run "curl contact" "curl -sS https://pepecapiro.com/contact || true")"

REMOTE_LS_THEME="$(ssh_run "ls themes/pepecapiro" "ls -la '$SITE_ROOT/wp-content/themes/pepecapiro' 2>&1 || true")"
REMOTE_DEBUG_TAIL="$(ssh_run "tail debug.log" "[ -f '$SITE_ROOT/wp-content/debug.log' ] && tail -n 200 '$SITE_ROOT/wp-content/debug.log' || echo 'ND' 2>/dev/null")"

detect_shortcode(){ local content="$1"; echo "$content" | tr -d '\r' | grep -o -i '\[wpforms[^]]*\]' | head -n1 || true; }
SHORTCODE_9="$(detect_shortcode "$REMOTE_POST9_CONTENT")"; SHORTCODE_15="$(detect_shortcode "$REMOTE_POST15_CONTENT")"
SHORTCODE_CONTACTO_HTML="$(echo "$REMOTE_CONTACTO_HTML" | tr -d '\r' | grep -inF '[wpforms' -m 1 || true)"
SHORTCODE_CONTACT_HTML="$(echo "$REMOTE_CONTACT_HTML" | tr -d '\r' | grep -inF '[wpforms' -m 1 || true)"

REMOTE_ACTIVE_THEME="$(echo "$REMOTE_THEME_ACTIVE_JSON" | tr -d '\r' | sed -n 's/.*"name"\s*:\s*"\([^"]*\)".*/\1/p' | head -n1)"; [[ -z "$REMOTE_ACTIVE_THEME" ]] && REMOTE_ACTIVE_THEME="ND"

clean_ver(){ local v="$1"; if echo "$v" | grep -q '^\[ERROR:'; then echo ND; else echo "$v" | tr -d '\r' | head -n1; fi }
WPFORMS_VER_CLEAN="$(clean_ver "$REMOTE_WPFORMS_VER")"; WPFORMS_LITE_VER_CLEAN="$(clean_ver "$REMOTE_WPFORMS_LITE_VER")"

# Servicios en remoto (detección por cabeceras HTTP)
REMOTE_HEADERS="$(run_cmd "curl headers" curl -sI https://pepecapiro.com)"
REMOTE_SERVER_HDR="$(echo "$REMOTE_HEADERS" | grep -i '^server:' | head -n1 | cut -d: -f2- | sed 's/^ *//')"

# ============================
# Diff style.css (local vs remoto)
# ============================
REMOTE_STYLE_TMP="$SCRATCH_DIR/remote_style.css"
REMOTE_STYLE_FETCH="$(ssh_run "cat remote style.css" "cat '$SITE_ROOT/wp-content/themes/pepecapiro/style.css' 2>/dev/null || echo ND")"
if [[ -n "$REMOTE_STYLE_FETCH" && "$REMOTE_STYLE_FETCH" != ND* ]]; then printf "%s\n" "$REMOTE_STYLE_FETCH" > "$REMOTE_STYLE_TMP"; else :; fi

DIFF_STYLE_OUTPUT=""
if [[ -f "$REMOTE_STYLE_TMP" && -n "$LOCAL_STYLE_PATH" && -f "$LOCAL_STYLE_PATH" ]]; then
  DIFF_STYLE_OUTPUT="$(diff -u --label local/style.css "$LOCAL_STYLE_PATH" --label remote/style.css "$REMOTE_STYLE_TMP" 2>&1 || true)"
fi

# ============================
# Inferencias/alertas
# ============================
ACTIVE_WPFORMS="$(echo "$REMOTE_PLUGIN_ACTIVE_JSON" | tr -d '\r' | grep -o '"name"\s*:\s*"wpforms"' | head -n1 || true)"
ACTIVE_WPFORMS_LITE="$(echo "$REMOTE_PLUGIN_ACTIVE_JSON" | tr -d '\r' | grep -o '"name"\s*:\s*"wpforms-lite"' | head -n1 || true)"

# Capturar ID de shortcode; no citar el regex
SHORTCODE_FORM_ID=""
if [[ $SHORTCODE_9 =~ id="([0-9]+)" ]]; then
  SHORTCODE_FORM_ID="${BASH_REMATCH[1]}"
elif [[ $SHORTCODE_15 =~ id="([0-9]+)" ]]; then
  SHORTCODE_FORM_ID="${BASH_REMATCH[1]}"
fi

FORM_ID_EXISTS="unknown"; REMOTE_FORM_STATUS="ND"
if [[ -n "$SHORTCODE_FORM_ID" ]]; then
  if echo "$REMOTE_FORMS_JSON" | grep -q '"ID"\s*:\s*'"$SHORTCODE_FORM_ID"; then
    FORM_ID_EXISTS="yes"
  else
    FORM_ID_EXISTS="no"
  fi
  # Intentar obtener estado directo del post si existe o comprobar error
  REMOTE_FORM_STATUS="$(ssh_run "estado form $SHORTCODE_FORM_ID" "cd '$SITE_ROOT' && wp post get $SHORTCODE_FORM_ID --field=post_status 2>&1 || true")"
  # Si WP-CLI responde con Error, normalizar a ND
  if echo "$REMOTE_FORM_STATUS" | grep -qi '^error:'; then REMOTE_FORM_STATUS="ND"; fi
fi

# Conteo de formularios publicados (best-effort)
FORMS_PUBLISHED_COUNT="$(echo "$REMOTE_FORMS_JSON" | grep -o '"post_status":"publish"' | wc -l | tr -d ' ')"

# ============================
# Reporte
# ============================
{
  echo "===== BEGIN PROFUNDO ====="
  echo "# Diagnóstico profundo: pepecapiro.com"
  echo
  echo "Generado: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "Workspace: $WORKSPACE_DIR"
  echo
  echo "## 1) Resumen ejecutivo"
  echo "- Tema (remoto/local): '$REMOTE_ACTIVE_THEME' | '${PRIMARY_LOCAL_THEME_DIR:-ND}'"
  echo "- WP/PHP remoto: WP=$(echo "$REMOTE_CORE_VER" | head -n1) | PHP=$(echo "$REMOTE_PHP_VER" | head -n1) | siteurl=$(echo "$REMOTE_SITEURL" | head -n1) | Server Header=${REMOTE_SERVER_HDR:-ND}"
  echo "- Plugins WPForms: wpforms=${WPFORMS_VER_CLEAN:-ND} | wpforms-lite=${WPFORMS_LITE_VER_CLEAN:-ND} | activos: wpforms=$([[ -n $ACTIVE_WPFORMS ]] && echo si || echo no) / wpforms-lite=$([[ -n $ACTIVE_WPFORMS_LITE ]] && echo si || echo no)"
  echo "- Shortcodes contacto: /contacto='${SHORTCODE_9:-ND}' | /contact='${SHORTCODE_15:-ND}' | HTML detectado: contacto='${SHORTCODE_CONTACTO_HTML:-ND}' contact='${SHORTCODE_CONTACT_HTML:-ND}'"
  echo "- Formularios (post_type=wpforms): $(echo "$REMOTE_FORMS_JSON" | wc -c) bytes JSON; publicados=$FORMS_PUBLISHED_COUNT (detalle abajo)"
  echo "- Docker local: $(echo "$DOCKER_VER" | head -n1) | Compose: $(docker compose version 2>/dev/null | head -n1 || docker-compose --version 2>/dev/null | head -n1 || echo ND)"
  echo
  echo "## 2) Estado local (incluye Docker)"
  echo "- OS: $LOCAL_OS_NAME | Kernel: $LOCAL_KERNEL | $(echo "$LOCAL_WSL")"
  echo "- Herramientas:"; echo "  - $(echo "$SSH_VER" | head -n1)"; echo "  - $(echo "$PHP_VER" | head -n1)"; echo "  - $(echo "$NODE_VER" | head -n1)"; echo "  - $(echo "$PY3_VER" | head -n1)"; echo "  - $(echo "$COMPOSER_VER" | head -n1)"; echo "  - $(echo "$DOCKER_VER" | head -n1)"
  echo "- Directories de tema local:"; if [[ -n "$THEME_PATHS" ]]; then echo "$THEME_PATHS" | sed 's/^/- /'; else echo "  - ND"; fi
  echo "- Archivos clave del tema local:"; if [[ -n "$PRIMARY_LOCAL_THEME_DIR" ]]; then file_info_block "$PRIMARY_LOCAL_THEME_DIR"; else echo "  - ND"; fi
  echo "- Docker local:"; docker_section
  echo
  echo "## 3) Estado remoto"
  echo "- siteurl: $(echo "$REMOTE_SITEURL" | head -n1)"
  echo "- WordPress: $(echo "$REMOTE_CORE_VER" | head -n1) | PHP: $(echo "$REMOTE_PHP_VER" | head -n1) | Server: ${REMOTE_SERVER_HDR:-ND}"
  echo "- Tema activo (json):"; echo '```json'; echo "$REMOTE_THEME_ACTIVE_JSON"; echo '```'
  echo "- Temas instalados (json):"; echo '```json'; echo "$REMOTE_THEME_ALL_JSON"; echo '```'
  echo "- Plugins instalados (json):"; echo '```json'; echo "$REMOTE_PLUGIN_LIST_JSON"; echo '```'
  echo "- Plugins activos (json):"; echo '```json'; echo "$REMOTE_PLUGIN_ACTIVE_JSON"; echo '```'
  echo "- Formularios (post_type=wpforms) (json):"; echo '```json'; echo "$REMOTE_FORMS_JSON"; echo '```'
  echo "- Formularios (tabla):"; echo '```'; echo "$REMOTE_FORMS_TABLE"; echo '```'
  echo "- Directorio tema remoto (ls -la):"; echo '```'; echo "$REMOTE_LS_THEME"; echo '```'
  echo
  echo "## 4) Comparativa local vs remoto"
  if [[ -n "$PRIMARY_LOCAL_THEME_DIR" ]]; then compare_hashes "$PRIMARY_LOCAL_THEME_DIR"; else echo "ND (no se detectó tema local)"; fi
  echo
  echo "### Diff style.css (local vs remoto)"
  if [[ -n "$DIFF_STYLE_OUTPUT" ]]; then echo '```diff'; echo "$DIFF_STYLE_OUTPUT"; echo '```'; else echo "(Sin diferencias o no disponible)"; fi
  echo
  echo "## 5) Riesgos y observaciones"
  if [[ -z "$ACTIVE_WPFORMS" && -n "$ACTIVE_WPFORMS_LITE" ]]; then echo "- Solo wpforms-lite activo (OK)."; else echo "- Revisión: coexistencia wpforms/wpforms-lite."; fi
  if [[ -n "$SHORTCODE_FORM_ID" ]]; then
    if [[ "$FORM_ID_EXISTS" == "no" ]]; then
      echo "- Shortcodes de contacto apuntan a ID=$SHORTCODE_FORM_ID que NO existe (posible formulario eliminado)."
    else
      echo "- Shortcodes de contacto apuntan a ID=$SHORTCODE_FORM_ID; estado remoto: ${REMOTE_FORM_STATUS:-ND}"
    fi
  else
    echo "- No se pudo inferir ID de shortcode."
  fi
  echo "- Docker local detectado: $(command -v docker >/dev/null 2>&1 && echo si || echo no). En remoto, entorno compartido (no Docker); cabecera Server=${REMOTE_SERVER_HDR:-ND}."
  echo
  echo "## 6) Recomendaciones inmediatas"
  echo "- Alineación tema: si solo style.css difiere, decidir fuente de verdad (remoto vs local) y sincronizar tras backup."
  echo "- Formularios: validar que el formulario ID=${SHORTCODE_FORM_ID:-ND} exista/publicado en WPForms Lite; si no existe, actualizar shortcode o restaurar formulario."
  echo "- Mantener un único plugin de formularios (Lite actualmente)."
  echo "- Docker: si se usa para desarrollo local, documentar servicios y puertos para emular remoto; no se observa Docker en Hostinger."
  echo
  echo "### Docker: comparación servicios vs remoto"
  if [[ ${#DOCKERFILES[@]} -gt 0 ]]; then
    echo "- Servicios locales definidos por Compose:"
    for f in "${DOCKERFILES[@]}"; do
      case "$f" in *compose*.y*ml)
        echo "  - Archivo: $f"; docker compose -f "$f" config --services 2>/dev/null || docker-compose -f "$f" config --services 2>/dev/null || echo "    (No disponible)";
      esac
    done
  else
    echo "- No se detectaron archivos Compose locales"
  fi
  echo "- Remoto (Hostinger): sin Docker; servicios activos visibles: HTTP(${REMOTE_SERVER_HDR:-ND}), PHP($(echo "$REMOTE_PHP_VER" | head -n1)); base de datos no expuesta."
  echo
  echo "=====  END  PROFUNDO ====="
} | tee "$REPORT_PATH"

exit 0
