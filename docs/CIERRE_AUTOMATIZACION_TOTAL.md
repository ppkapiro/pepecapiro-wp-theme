# Cierre de Automatización Total

Fecha de activación Fase 6: 2025-10-20

Workflows de verificación:
- verify-home.yml (6h): valida portada y front ES/EN.
- verify-menus.yml (12h): compara menús con `content/menus/menus.json`.
- verify-media.yml (diario): existencia y asignaciones según `content/media/media_manifest.json`.
- verify-settings.yml (24h): timezone/permalinks/start_of_week.

Alertas e incidentes:
- Issues automáticos etiquetados `monitoring`, `incident` cuando hay KO. Se cierran al volver a OK.

Run Repair:
- `run-repair.yml` ejecuta la acción de corrección para el área indicada (plan/apply).

Rotación y limpieza:
- `rotate-app-password.yml` guía de rotación de credencial.
- Cleanup extendido pendiente de ampliación.
