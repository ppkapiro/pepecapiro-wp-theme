#!/usr/bin/env bash
set -euo pipefail

# Config
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
POLL_SECS="10"
URLS=(
  "https://pepecapiro.com/privacidad/"
  "https://pepecapiro.com/cookies/"
  "https://pepecapiro.com/en/privacy/"
  "https://pepecapiro.com/en/cookies/"
  "https://pepecapiro.com/contacto/"
  "https://pepecapiro.com/en/contact/"
  "https://pepecapiro.com/post-sitemap.xml"
)

have_cmd(){ command -v "$1" >/dev/null 2>&1; }

color() { local c="$1"; shift; case "$c" in
  red) printf "\033[31m%s\033[0m" "$*";;
  green) printf "\033[32m%s\033[0m" "$*";;
  yellow) printf "\033[33m%s\033[0m" "$*";;
  blue) printf "\033[34m%s\033[0m" "$*";;
  *) printf "%s" "$*";; esac; }

section(){ echo; color blue "==> $*"; echo; }

check_code(){
  local url="$1"; local code
  code=$(curl -s -L -o /tmp/_wd_body -w '%{http_code}' "$url" || echo "000")
  echo "$code"
}

goals_met(){
  local ok_priv_es=0 ok_priv_en=0 ok_cookies_es=0 ok_cookies_en=0 ok_sitemap=0
  local code

  code=$(check_code "https://pepecapiro.com/privacidad/")
  [[ "$code" == "200" ]] && ok_priv_es=1
  code=$(check_code "https://pepecapiro.com/en/privacy/")
  [[ "$code" == "200" ]] && ok_priv_en=1
  code=$(check_code "https://pepecapiro.com/cookies/")
  [[ "$code" == "200" ]] && ok_cookies_es=1
  code=$(check_code "https://pepecapiro.com/en/cookies/")
  [[ "$code" == "200" ]] && ok_cookies_en=1
  code=$(curl -s -L -o /tmp/_wd_sitemap -w '%{http_code}' "https://pepecapiro.com/post-sitemap.xml" || echo "000")
  if [[ "$code" == "200" ]] && ! grep -qi 'hello-world' /tmp/_wd_sitemap 2>/dev/null; then ok_sitemap=1; fi

  # Éxito cuando legales 200 (ES/EN) y sitemap sin hello-world
  [[ $ok_priv_es -eq 1 && $ok_priv_en -eq 1 && $ok_cookies_es -eq 1 && $ok_cookies_en -eq 1 && $ok_sitemap -eq 1 ]]
}

print_status(){
  section "Estado de URLs"
  for u in "${URLS[@]}"; do
    code=$(check_code "$u")
    body=""
    if [[ "$u" == *"post-sitemap.xml"* ]]; then
      curl -s -L "$u" -o /tmp/_wd_sitemap || true
      body=$(cat /tmp/_wd_sitemap 2>/dev/null || true)
    fi
    local badge=""; local note=""
    if [[ "$code" == "200" ]]; then badge=$(color green "200 OK"); else badge=$(color red "$code"); fi
    if [[ "$u" == *"post-sitemap.xml"* ]]; then
      if grep -qi 'hello-world' <<<"$body"; then note=$(color yellow "(aún lista hello-world)"); else note=$(color green "(hello-world ausente)"); fi
    fi
    printf "%-38s %s %s\n" "$u" "$badge" "$note"
  done
}

main(){
  while true; do
    clear
    section "Monitoreo de despliegue y Content Ops"
    date
    print_status
    if goals_met; then
      section "Objetivos alcanzados ✅"
      echo "Legales ES/EN en 200 y sitemap actualizado (sin hello-world)."
      break
    else
      section "Aún en progreso…"
      echo "Refrescando en ${POLL_SECS}s (Ctrl+C para salir)"
      sleep "$POLL_SECS"
    fi
  done
}

main "$@"
