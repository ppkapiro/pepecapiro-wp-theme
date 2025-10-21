# Hub Aggregation Setup — 2025-10-21

Objetivo: Implementar agregación automática de múltiples `status.json` en `docs/hub/hub_status.json` y publicarlo en repo (visible vía GitHub Pages).

## Acciones Realizadas

1. Script de agregación
   - Ruta: `scripts/hub/aggregate_status.sh`
   - Funciones:
     - Lee `docs/hub/instances.json`.
     - Consulta cada `status_endpoint` con `curl`.
     - Interpreta `version`, `health`, `last_update` (o `timestamp`).
     - Genera `docs/hub/hub_status.json` con resumen y lista de instancias.
   - Dependencias: `curl`, `jq` (se verifica al inicio del script).

2. Workflow programado
   - Ruta: `.github/workflows/hub-aggregation.yml`
   - Programación: cada 10 minutos (`cron: "*/10 * * * *"`) y `workflow_dispatch` manual.
   - Permisos: `contents: write` para poder comitear cambios.
   - Pasos:
     - Checkout del repo.
     - Asegura `jq` instalado (Ubuntu-latest ya lo suele incluir; fallback con apt-get).
     - Ejecuta `scripts/hub/aggregate_status.sh`.
     - Si cambia `docs/hub/hub_status.json`, comitea y hace push.

3. Artefactos afectados
   - `docs/hub/hub_status.json`: será refrescado automáticamente.
   - `docs/hub/instances.json`: fuente de endpoints (debe mantenerse actualizado).

## Validaciones

- Sintaxis JSON validada con `jq` en el script.
- Rutas verificadas y existentes (`docs/hub/*`).
- Se añadió evidencia de creación en este log.

## Próximos pasos (opcionales)

- Extender `hub_status.json` con latencias por endpoint y últimos N históricos.
- Añadir panel HTML interactivo (tabla y badges) — roadmap v0.9.1.
- Alertas: abrir issue automático si `offline > 0` o `degraded > 0` sostenido.

## Observaciones

- Si un endpoint falla (timeout o HTTP ≠ 200), la instancia se marca `offline` con nota `fetch_failed:http_<code>`.
- Requiere que `docs/hub/instances.json` tenga `status_endpoint` accesible públicamente.
- No se requieren secretos; usa endpoints públicos.

---

Ejecución verificada y lista para operar en producción.
