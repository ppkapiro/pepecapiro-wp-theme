## v0.6.0 — Mantenimiento Proactivo + Dashboard
- **health-dashboard.yml**: genera `public/status.json` con estado de Auth/Home/Menus/Media/Settings/Polylang e issues; cron cada 6h.
- **smoke-tests.yml**: pruebas de humo post-deploy (Home ES/EN, REST API, Auth); ejecuta con push a main.
- **weekly-audit.yml**: auditoría semanal (domingos) que hashea manifiestos, lanza verify-*, genera `docs/AUDITORIA_SEMANAL.md` y crea issue si hay drift.
- **DASHBOARD_REFERENCE.md**: documentación del formato y uso de `status.json`.
- README actualizado con sección "Mantenimiento Proactivo".
- Proyecto completo: Automatización Total + Monitoreo Activo.

## v0.5.1 — Verificación Integral + Alertas Estables
- verify-home: fallbacks robustos, exportación WP_URL, issue handling vía gh api REST.
- verify-settings: permisos contents:read e issues:write, creación/asignación de labels best-effort.
- site-settings: PATCH real a /wp-json/wp/v2/settings con lectura post-apply.
- Todas las verificaciones ejecutan sin fallos de variables no definidas o permisos 403.
- Nota: timezone_string y permalink_structure pueden persistir en null según configuración del hosting.

## v0.5.0 — Ajustes Automáticos del Sitio
- Configuración de timezone, permalink y parámetros base.
- Ejecución manual segura (workflow_dispatch).

## v0.4.2 — Automatización de Medios
- Añadido soporte para menús ES/EN (test/prod).
- Jerarquías y localizaciones automáticas.
- Vinculación Polylang best‑effort validada.
- Flags y manifiestos documentados.
- Preparada estructura base para Medios y Ajustes.

## v0.4.2 — Automatización de Medios
- Soporte para subida automática de archivos.
- Detección por hash y reutilización.
- Asignación como imagen destacada mediante `assign_to`.
- Integración con `content/media/media_manifest.json`.

## v0.5.0 — Ajustes Automáticos del Sitio
- Configuración de timezone, permalink y parámetros base.
- Ejecución manual segura (workflow_dispatch).# Changelog (Docs)

## 0.3.20 — Cierre etapa "Publicación Automática WP (Posts)"
- Workflows consolidados: Test (private, ES/EN, vinculación), Prod (publish, ES/EN, categorías por idioma, idempotencia por slug), Cleanup (cron diario).
- Flags documentados en `.github/auto/README.flags.md`.
- Documentación ampliada: README, LIENZO, RUNBOOK, TROUBLESHOOTING, SECURITY NOTES y ROADMAP.
- Release etiquetado por tags con artefactos ZIP+SHA (workflow `release.yml`).

Nota: ver también `CHANGELOG.md` en la raíz del repo para historial completo.
