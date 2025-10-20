## v0.4.1 — Automatización de Menús Bilingües
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
