# BLOCKER — Falta API_GATEWAY_TOKEN

Estado: ABIERTO (requiere acción del owner)
Fecha: 2025-10-21

Impacto:
- `POST /api/automation/trigger` no autenticable desde el exterior.
- Webhooks WordPress → GitHub (repository_dispatch) no funcionales.

Requisitos del token:
- Tipo: GitHub Personal Access Token (classic)
- Scopes: `repo`, `workflow`

Pasos para resolver:
1. Generar PAT en https://github.com/settings/tokens/new (classic) con scopes `repo` + `workflow`.
2. Guardarlo como secret del repo: `API_GATEWAY_TOKEN`.
3. Probar `POST /trigger` con header `Authorization: Bearer <token>` (ver `docs/API_REFERENCE.md`).
4. Validar webhook WP→GitHub (ver `docs/WEBHOOK_WP_TO_GITHUB.md`).

Notas:
- El token no debe exponerse en logs. Usar siempre secretos de GitHub Actions.
- Si se rota, actualizar el secret y reintentar.
