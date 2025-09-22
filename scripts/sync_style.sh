#!/usr/bin/env bash
# Sincroniza style.css del tema pepecapiro: calcula hashes, respalda remoto, sube archivo y valida.
# Reglas: No tocar DB ni otros archivos. Enmascarar secretos si se muestran. No abortar ante errores.

set -euo pipefail

SSH_ALIAS="pepecapiro"
SSH_PORT="65002"
SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SCRATCH_DIR="$REPO_ROOT/_scratch"
REPORT_PATH="$SCRATCH_DIR/sync_style.md"
mkdir -p "$SCRATCH_DIR"

THEME_LOCAL_DIR="$REPO_ROOT/pepecapiro"
LOCAL_STYLE="$THEME_LOCAL_DIR/style.css"
REMOTE_STYLE_PATH="$SITE_ROOT/wp-content/themes/pepecapiro/style.css"

mask_secrets(){
  sed -E \
    -e 's/("password"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("passphrase"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("privateKey"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/("secret"\s*:\s*")([^"]*)(")/\1****\3/gI' \
    -e 's/([Pp]assword=)[^"\s]*/\1****/g'
}

log(){ echo "$1" >&2; }

ssh_run(){
  local desc="$1"; shift
  local remote_cmd="$*"
  local out err rc
  out="$(ssh -p "$SSH_PORT" "$SSH_ALIAS" "$remote_cmd" 2> >(err=$(cat); typeset -p err >/dev/null) )" || rc=$?
  rc=${rc:-0}
  if [[ $rc -ne 0 ]]; then
    echo "[ERROR:$rc] $desc"$'\n'"STDOUT:"$'\n'"${out:-}"$'\n'"STDERR:"$'\n'"${err:-}"$'\n'""
  else
    echo "$out"
  fi
  return 0
}

calc_local_sha(){
  if [[ -f "$LOCAL_STYLE" ]]; then sha256sum "$LOCAL_STYLE" | awk '{print $1}'; else echo ND; fi
}

calc_remote_sha(){
  local out
  out="$(ssh_run "sha256 remoto" "[ -f '$REMOTE_STYLE_PATH' ] && sha256sum '$REMOTE_STYLE_PATH' || echo ND")"
  if echo "$out" | grep -q '^\[ERROR:'; then echo ND; else echo "$out" | awk '{print $1}' | head -n1; fi
}

timestamp(){ date -u +"%Y%m%d_%H%M%S"; }

BACKUP_PATH=""

report(){
  local content="$1"
  printf '%s\n' "===== BEGIN SYNC STYLE =====" "$content" "=====  END  SYNC STYLE ====="
}

main(){
  local before_local_sha before_remote_sha after_remote_sha upload_rc=0 backup_rc=0 cache_rc=0 curl_rc=0
  local backup_msg upload_msg cache_msg curl_msg

  before_local_sha="$(calc_local_sha)"
  before_remote_sha="$(calc_remote_sha)"

  # Backup remoto
  if [[ "$before_remote_sha" != "ND" ]]; then
    local bkname="style.css.$(timestamp).bak"
    local cmd="cp -f '$REMOTE_STYLE_PATH' '$(dirname "$REMOTE_STYLE_PATH")/$bkname' && echo '$bkname'"
    BACKUP_PATH="$(ssh_run "backup remoto" "$cmd")"
    if echo "$BACKUP_PATH" | grep -q '^\[ERROR:'; then
      backup_msg="ERROR: no se pudo crear backup"
      backup_rc=1
    else
      backup_msg="Backup creado: $BACKUP_PATH"
    fi
  else
    backup_msg="Backup omitido: archivo remoto no existe (ND)"
  fi

  # Subida del archivo local via scp (SSH)
  if [[ -f "$LOCAL_STYLE" ]]; then
    local scp_out rc
    scp_out="$(scp -P "$SSH_PORT" "$LOCAL_STYLE" "$SSH_ALIAS:$REMOTE_STYLE_PATH" 2>&1)" || upload_rc=$?
    if [[ $upload_rc -ne 0 ]]; then
      upload_msg="ERROR subiendo style.css (scp rc=$upload_rc): $scp_out"
    else
      upload_msg="Subida OK (scp)"
    fi
  else
    upload_msg="ERROR: style.css local no existe en $LOCAL_STYLE"
    upload_rc=2
  fi

  # Recalcular remoto
  after_remote_sha="$(calc_remote_sha)"

  # Limpieza de caché (LiteSpeed, si aplica)
  # Intento 1: WP-CLI si está disponible
  cache_msg="ND"
  local cache_try
  cache_try="$(ssh_run "purge cache" "cd '$SITE_ROOT' && wp cache flush 2>&1 || echo ND")"
  if ! echo "$cache_try" | grep -qi '^\[ERROR:'; then
    cache_msg="wp cache flush ejecutado"
  else
    cache_msg="wp cache flush no disponible"
  fi
  # Intento 2: headers/purge simples en LSCache (si plugin activo, requiere URL especial). Lo dejamos como nota.

  # Smoke test
  local curl_out
  curl_out="$(curl -sS -m 8 https://pepecapiro.com/ 2>&1 || true)" || curl_rc=$?
  if echo "$curl_out" | grep -qi 'wp-content/themes/pepecapiro/style.css'; then
    curl_msg="HTML incluye referencia a style.css"
  else
    curl_msg="ADVERTENCIA: no se detectó referencia directa a style.css en HTML (puede estar encolado como inline o no referenciado explícitamente)"
  fi
  # Chequeo de no vacío: que el style.css tenga contenido (>0 bytes) remoto
  local remote_size
  remote_size="$(ssh_run "stat remoto" "stat -c %s '$REMOTE_STYLE_PATH' 2>/dev/null || echo 0")"

  # Construir reporte
  local result_match="ND"
  if [[ "$before_local_sha" != "ND" && "$after_remote_sha" != "ND" ]]; then
    if [[ "$before_local_sha" == "$after_remote_sha" ]]; then result_match="MATCH"; else result_match="DIFF"; fi
  fi

  {
    echo "# Sincronización style.css (pepecapiro)"
    echo
    echo "Generado: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "Workspace: $REPO_ROOT"
    echo
    echo "## 1) Hashes antes"
    echo "- Local  : $before_local_sha"
    echo "- Remoto : $before_remote_sha"
    echo
    echo "## 2) Backup"
    echo "- $backup_msg"
    echo
    echo "## 3) Subida"
    echo "- $upload_msg"
    echo
    echo "## 4) Hashes después"
    echo "- Local  : $before_local_sha"
    echo "- Remoto : $after_remote_sha"
    echo "- Resultado: $result_match"
    echo
    echo "## 5) Caché"
    echo "- $cache_msg"
    echo "(Si el sitio usa LiteSpeed Cache, considera purgarlo desde el panel si no ves cambios inmediatos)"
    echo
    echo "## 6) Smoke test"
    echo "- HEAD HTML contiene style.css: $curl_msg"
    echo "- Tamaño remoto de style.css: $remote_size bytes"
  } > "$REPORT_PATH"

  report "$(cat "$REPORT_PATH")"
}

main "$@"
