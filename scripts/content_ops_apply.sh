#!/usr/bin/env bash
set -euo pipefail

# Uso: export PEPE_HOST, PEPE_USER, (opcional) PEPE_PORT=22; luego ./scripts/content_ops_apply.sh

SSH_HOST="${PEPE_HOST:-}"
SSH_USER="${PEPE_USER:-}"
SSH_PORT="${PEPE_PORT:-22}"
ROOT="/home/u525829715/domains/pepecapiro.com/public_html"

if [[ -z "$SSH_HOST" || -z "$SSH_USER" ]]; then
  echo "[x] Configura PEPE_HOST y PEPE_USER en tu entorno." >&2
  exit 1
fi

echo "[i] Ejecutando Content Ops en $SSH_USER@$SSH_HOST:$SSH_PORT …"

ssh -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" "bash -se" <<'REMOTE_CMDS'
set -euo pipefail
ROOT="/home/u525829715/domains/pepecapiro.com/public_html"
LOG="/tmp/content_ops_$(date +%s).log"
cd "$ROOT"

note(){ echo "[op] $1" | tee -a "$LOG"; }

note "Asignar plantilla bilingüe a Contacto ES"
ID=$(wp post list --post_type=page --name=contacto --field=ID || true)
if [ -n "$ID" ]; then wp post meta update "$ID" _wp_page_template page-contact.php | tee -a "$LOG"; fi

note "Crear/asegurar legales ES + idioma"
P=$(wp post list --post_type=page --name=privacidad --field=ID || true)
if [ -z "$P" ]; then NEW=$(wp post create --post_type=page --post_status=publish --post_title='Política de Privacidad' --post_name=privacidad --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'es');}" | tee -a "$LOG"; else wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$P,'es');}" | tee -a "$LOG"; fi
C=$(wp post list --post_type=page --name=cookies --field=ID || true)
if [ -z "$C" ]; then NEW=$(wp post create --post_type=page --post_status=publish --post_title='Política de Cookies' --post_name=cookies --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'es');}" | tee -a "$LOG"; else wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$C,'es');}" | tee -a "$LOG"; fi

note "Crear/asegurar legales EN + idioma"
PE=$(wp post list --post_type=page --name=privacy --field=ID || true)
if [ -z "$PE" ]; then NEW=$(wp post create --post_type=page --post_status=publish --post_title='Privacy Policy' --post_name=privacy --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'en');}" | tee -a "$LOG"; else wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$PE,'en');}" | tee -a "$LOG"; fi
CE=$(wp post list --post_type=page --name=cookies --field=ID || true)
if [ -z "$CE" ]; then NEW=$(wp post create --post_type=page --post_status=publish --post_title='Cookies Policy' --post_name=cookies --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'en');}" | tee -a "$LOG"; else wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$CE,'en');}" | tee -a "$LOG"; fi

note "Enlazar traducciones Privacidad y Cookies"
ES_PRIV=$(wp post list --post_type=page --name=privacidad --field=ID || true); EN_PRIV=$(wp post list --post_type=page --name=privacy --field=ID || true)
if [ -n "$ES_PRIV" ] && [ -n "$EN_PRIV" ]; then wp eval "if(function_exists('pll_save_post_translations')){pll_save_post_translations(['es'=>$ES_PRIV,'en'=>$EN_PRIV]);}" | tee -a "$LOG"; fi
ES_CID=$(wp post list --post_type=page --title='Política de Cookies' --field=ID || true); EN_CID=$(wp post list --post_type=page --title='Cookies Policy' --field=ID || true)
if [ -n "$ES_CID" ] && [ -n "$EN_CID" ]; then wp eval "if(function_exists('pll_save_post_translations')){pll_save_post_translations(['es'=>$ES_CID,'en'=>$EN_CID]);}" | tee -a "$LOG"; fi

note "Eliminar Hello World (todas variantes)"
for ID in $(wp post list --post_type=post --name=hello-world --field=ID || true); do wp post delete "$ID" --force | tee -a "$LOG"; done || true
for ID in $(wp post list --post_type=post --title='Hello world!' --field=ID || true) $(wp post list --post_type=post --title='Hello world' --field=ID || true) $(wp post list --post_type=post --title='Hola mundo!' --field=ID || true) $(wp post list --post_type=post --title='Hola mundo' --field=ID || true); do [ -n "$ID" ] && wp post delete "$ID" --force | tee -a "$LOG"; done || true

note "Crear categorías ES/EN"
wp term create category 'Guías' --slug=guias | tee -a "$LOG" || true
wp term create category 'Guides' --slug=guides | tee -a "$LOG" || true

note "Publicar posts ES/EN iniciales"
ES=$(wp post list --post_type=post --name=checklist-wordpress-produccion-1-dia --field=ID || true)
if [ -z "$ES" ]; then NEW=$(wp post create --post_type=post --post_status=publish --post_title='Checklist para poner un WordPress a producir en 1 día' --post_name=checklist-wordpress-produccion-1-dia --post_excerpt='Una guía práctica para pasar de cero a producción en 24 horas: seguridad, rendimiento, SEO, contenido mínimo y verificación.' --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'es');}" | tee -a "$LOG"; wp post term add "$NEW" category guias | tee -a "$LOG"; fi
EN=$(wp post list --post_type=post --name=ship-wordpress-production-in-one-day --field=ID || true)
if [ -z "$EN" ]; then NEW=$(wp post create --post_type=post --post_status=publish --post_title='Ship a Production‑Ready WordPress in One Day: A Practical Checklist' --post_name=ship-wordpress-production-in-one-day --post_excerpt='A hands‑on guide to go live in 24 hours: security, performance, SEO, minimum content, and final checks.' --porcelain); wp eval "if(function_exists('pll_set_post_language')){pll_set_post_language((int)$NEW,'en');}" | tee -a "$LOG"; wp post term add "$NEW" category guides | tee -a "$LOG"; fi

note "Flush de permalinks y purga de caché"
wp rewrite flush --hard | tee -a "$LOG"
wp cache flush | tee -a "$LOG"
wp plugin is-installed litespeed-cache && wp litespeed-purge all | tee -a "$LOG" || true

note "Limpiar transients y caché de sitemaps Rank Math + recalentar"
wp transient delete --all | tee -a "$LOG" || true
PREFIX=$(wp db prefix)
wp db query "DELETE FROM ${PREFIX}options WHERE option_name LIKE 'rank_math_sitemap_%';" | tee -a "$LOG" || true
curl -sS https://pepecapiro.com/sitemap_index.xml >/dev/null || true
curl -sS https://pepecapiro.com/post-sitemap.xml >/dev/null || true

note "Resumen"
echo 'PAGES:' >> "$LOG"; wp post list --post_type=page --fields=ID,post_name,post_title,post_status --format=table >> "$LOG"
echo 'POSTS:' >> "$LOG"; wp post list --post_type=post --fields=ID,post_name,post_title,post_status --format=table >> "$LOG"

echo "[ok] Content Ops finalizado. Log: $LOG"
REMOTE_CMDS

echo "[i] Hecho. Puedes revisar el log en el servidor en /tmp/content_ops_*.log"