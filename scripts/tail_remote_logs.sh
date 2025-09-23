#!/usr/bin/env bash
set -euo pipefail

SSH_HOST="${PEPE_HOST:-}"
SSH_PORT="${PEPE_PORT:-22}"
SSH_USER="${PEPE_USER:-}"

if [[ -z "$SSH_HOST" || -z "$SSH_USER" ]]; then
  echo "Uso: export PEPE_HOST, PEPE_USER (y opcional PEPE_PORT)." >&2
  exit 1
fi

echo "Conectando a $SSH_USER@$SSH_HOST:$SSH_PORT …"
exec ssh -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" "tail -n 200 -F /tmp/content_ops_*.log 2>/dev/null || tail -n 200 -F /tmp/content_ops_*.log"
