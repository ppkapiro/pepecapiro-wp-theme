#!/usr/bin/env bash
# Verifica que el remoto sirva los estilos tras sincronizar style.css
# - No modifica DB, ni archivos, ni plugins
# - Intenta purgar LSCache vía WP-CLI (no intrusivo) y fuerza primer hit sin caché

set -euo pipefail

SSH_ALIAS="pepecapiro"
SSH_PORT="65002"
SITE_ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
SCRATCH_DIR="$REPO_ROOT/_scratch"
REPORT_PATH="$SCRATCH_DIR/style_verify.md"
mkdir -p "$SCRATCH_DIR"

WP_PORT_LOCAL="8080" # por defecto; se actualiza leyendo docker/.env si existe
ENV_FILE="$REPO_ROOT/docker/.env"
if [[ -f "$ENV_FILE" ]]; then
  WP_PORT_LOCAL="$(grep -E '^WP_PORT=' "$ENV_FILE" | cut -d= -f2- || echo 8080)"
fi

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

http_fetch(){
  local url="$1"; shift || true
  curl -sS -m 12 -D - "$url" -o /dev/stdout 2>/dev/null || true
}

extract_css_urls(){
  # Extrae URLs de CSS del HTML (links rel=stylesheet y href con .css)
  # Salida: una URL por línea
    sed -n '1,500p' | tr -d '\r' | grep -oiE "<link[^>]+rel=['\"]stylesheet['\"][^>]*href=['\"][^'\"<>]+['\"][^>]*>" | sed -E "s/.*href=['\"]([^'\"<>]+)['\"].*/\\1/i" | sed -E 's/&amp;/\&/g'
}

head_value(){ grep -i "^$1:" | head -n1 | sed -E 's/^[^:]+:\s*//I'; }

size_of_url(){
  local url="$1"
  curl -sS -m 12 -I "$url" 2>/dev/null \
    | awk 'BEGIN{IGNORECASE=1} /^Content-Length:/ {gsub(/\r/,"",$2); print $2; exit}'
}

status_of_url(){
  local url="$1"
  curl -s -o /dev/null -w '%{http_code}' -m 12 "$url" 2>/dev/null || echo ND
}

collect_css_info(){
  local base_url="$1"
  local html="$2"
  local out urls sizes statuses
  urls=$(printf '%s' "$html" | extract_css_urls | sed -E "s#^//#https://#" )
  if [[ -z "$urls" ]]; then
    echo "(sin <link rel=stylesheet>)"
    return 0
  fi
  while IFS= read -r u; do
    # Normalizar relativas
    if [[ "$u" =~ ^/ ]]; then u="${base_url%/}$u"; fi
    local sz st
    sz="$(size_of_url "$u")"; st="$(status_of_url "$u")"
    printf "- %s | size=%s | status=%s\n" "$u" "${sz:-ND}" "${st:-ND}"
  done <<< "$urls"
}

main(){
  local remote_theme_json remote_theme_active remote_stat remote_perm remote_owner
  local remote_head remote_html remote_head_nc remote_html_nc remote_head_v remote_html_v
  local local_head local_html
  local purge_out purge_note

  # 1) Estado base
  remote_theme_json="$(ssh_run "tema activo" "cd '$SITE_ROOT' && wp theme list --status=active --format=json 2>&1")"
  if echo "$remote_theme_json" | grep -q '^\[ERROR:'; then remote_theme_active="ND"; else remote_theme_active="$(echo "$remote_theme_json" | sed -n 's/.*"name"\s*:\s*"\([^"]*\)".*/\1/p' | head -n1)"; fi
  remote_stat="$(ssh_run "stat style.css" "stat -c '%s %y' '$SITE_ROOT/wp-content/themes/pepecapiro/style.css' 2>/dev/null || echo '0 ND'")"
  remote_perm="$(ssh_run "permisos style.css" "stat -c '%a %U:%G' '$SITE_ROOT/wp-content/themes/pepecapiro/style.css' 2>/dev/null || echo 'ND ND')"

  # 2) Purga de caché (no intrusiva)
  purge_out="$(ssh_run "wp cache flush" "cd '$SITE_ROOT' && wp cache flush 2>&1 || echo ND")"
  if echo "$purge_out" | grep -qi '^\[ERROR:'; then
    purge_note="NO (wp cache flush no disponible)"
  else
    purge_note="SI (wp cache flush ejecutado)"
  fi

  # 3) Verificación de referencia a CSS en remoto
  remote_head="$(http_fetch 'https://pepecapiro.com/')"
  remote_html="$remote_head"
  remote_head_nc="$(http_fetch 'https://pepecapiro.com/?nocache=1')"
  remote_html_nc="$remote_head_nc"
  remote_head_v="$(http_fetch "https://pepecapiro.com/?v=$(date +%s)")"
  remote_html_v="$remote_head_v"

  # 4) Comparativa con Docker local
  local_head="$(http_fetch "http://localhost:${WP_PORT_LOCAL}/")"
  local_html="$local_head"

  # 5) Comprobaciones del tema (solo lectura)
  local header_cat footer_cat
  header_cat="$(sed -n '1,200p' "$REPO_ROOT/pepecapiro/header.php" 2>/dev/null || true)"
  footer_cat="$(sed -n '1,200p' "$REPO_ROOT/pepecapiro/footer.php" 2>/dev/null || true)"
  local has_wp_head has_wp_footer
  echo "$header_cat" | grep -qE 'wp_head[[:space:]]*\(' && has_wp_head="SI" || has_wp_head="NO"
  echo "$footer_cat" | grep -qE 'wp_footer[[:space:]]*\(' && has_wp_footer="SI" || has_wp_footer="NO"

  # 6) Cabeceras relevantes
  hdr_remote_normal="$(printf '%s' "$remote_head" | sed -n '1,20p')"
  hdr_remote_nc="$(printf '%s' "$remote_head_nc" | sed -n '1,20p')"
  hdr_remote_v="$(printf '%s' "$remote_head_v" | sed -n '1,20p')"

  # 7) Construcción del reporte (simple y lineal)
  : > "$REPORT_PATH"
  echo "===== BEGIN STYLE VERIFY =====" >> "$REPORT_PATH"
  echo "# Verificación de estilos pepecapiro" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "Generado: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$REPORT_PATH"
  echo "Workspace: $REPO_ROOT" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 1) Estado base remoto" >> "$REPORT_PATH"
  echo "- Tema activo: ${remote_theme_active:-ND}" >> "$REPORT_PATH"
  echo "- style.css tamaño/mtime: $remote_stat" >> "$REPORT_PATH"
  echo "- style.css permisos/owner: $remote_perm" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 2) Purga de caché" >> "$REPORT_PATH"
  echo "- Ejecutada: $purge_note" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 3) CSS en remoto (HTML)" >> "$REPORT_PATH"
  echo "- URLs CSS (normal):" >> "$REPORT_PATH"
  collect_css_info "https://pepecapiro.com" "$remote_html" >> "$REPORT_PATH"
  echo "- URLs CSS (?nocache=1):" >> "$REPORT_PATH"
  collect_css_info "https://pepecapiro.com" "$remote_html_nc" >> "$REPORT_PATH"
  echo "- URLs CSS (?v=timestamp):" >> "$REPORT_PATH"
  collect_css_info "https://pepecapiro.com" "$remote_html_v" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 4) CSS en Docker local" >> "$REPORT_PATH"
  echo "- Base: http://localhost:${WP_PORT_LOCAL}/" >> "$REPORT_PATH"
  collect_css_info "http://localhost:${WP_PORT_LOCAL}" "$local_html" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 5) Comprobaciones de tema (solo lectura)" >> "$REPORT_PATH"
  echo "- header.php tiene wp_head(): $has_wp_head" >> "$REPORT_PATH"
  echo "- footer.php tiene wp_footer(): $has_wp_footer" >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 6) Cabeceras relevantes (primeras líneas)" >> "$REPORT_PATH"
  echo "- Remoto normal:" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  printf "%s\n" "$hdr_remote_normal" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  echo "- Remoto ?nocache=1:" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  printf "%s\n" "$hdr_remote_nc" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  echo "- Remoto ?v=timestamp:" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  printf "%s\n" "$hdr_remote_v" >> "$REPORT_PATH"
  echo '```' >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  echo "## 7) Conclusión" >> "$REPORT_PATH"
  remote_css_list="$(collect_css_info "https://pepecapiro.com" "$remote_html" | tr -d '\r')"
  remote_css_has_size="NO"
  while IFS= read -r line; do
    if echo "$line" | awk -F 'size=' '{print $2}' | awk '{print $1}' | grep -qE '^[1-9]'; then remote_css_has_size="SI"; break; fi
  done <<< "$remote_css_list"
  if [[ "$remote_css_has_size" == "SI" ]]; then
    echo "- ¿Se ve el CSS en remoto?: Sí (al menos una hoja con size>0)" >> "$REPORT_PATH"
  else
    echo "- ¿Se ve el CSS en remoto?: No (no se detectó hoja con size>0 en la respuesta analizada)" >> "$REPORT_PATH"
  fi
  echo "- Diferencias remotas vs Docker:" >> "$REPORT_PATH"
  echo "  - Remoto:" >> "$REPORT_PATH"
  printf "%s\n" "$remote_css_list" | sed -n '1,10p' >> "$REPORT_PATH"
  echo "  - Docker:" >> "$REPORT_PATH"
  collect_css_info "http://localhost:${WP_PORT_LOCAL}" "$local_html" | sed -n '1,10p' >> "$REPORT_PATH"
  echo >> "$REPORT_PATH"
  if [[ "$remote_css_has_size" == "SI" ]]; then
    echo "- Recomendación: ok para continuar con formularios" >> "$REPORT_PATH"
  else
    echo "- Recomendación: investigar enqueue en functions.php (wp_enqueue_style) o interferencias de plugins/caché" >> "$REPORT_PATH"
  fi
  echo >> "$REPORT_PATH"
  echo "=====  END  STYLE VERIFY =====" >> "$REPORT_PATH"
  cat "$REPORT_PATH"
}

main "$@"
