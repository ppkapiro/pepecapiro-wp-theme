# pepecapiro-wp-theme

[![Lighthouse Mobile + Docs](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml/badge.svg)](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml)

Tema WordPress para pepecapiro.com.

## Documentación Clave
- Índice: `docs/INDEX.md`
- Arquitectura: `docs/ARCHITECTURE.md`
- Automatización de contenido: `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md`
- Operaciones/Gobernanza: `docs/OPERATIONS_OVERVIEW.md`
- Runbook de despliegue: `docs/DEPLOY_RUNBOOK.md`
- Métricas & Observabilidad: `docs/PERFORMANCE_METRICS.md`
- Changelog: `CHANGELOG.md`
- Reportes Lighthouse / auditorías: `docs/`

## Flujo Rápido (Publicar Contenido)
```
1. Editar content/posts.json o pages.json
2. Añadir markdown ES/EN (content/<slug>.<lang>.md)
3. Commit con [publish] en el mensaje (o tener .auto_apply)
4. Push a main → CI valida y publica (auto-apply) / si no, plan
```
Outputs generados:
- `content/content_plan_summary.md` (plan dry-run)
- `content/drift_report.md` (modo `--drift-only`)
- `content/.media_map.json` (deduplicación media)

Si no quieres auto-apply permanente, elimina `.auto_apply` y usa `[publish]` sólo cuando proceda.

## Métricas & Demo
[![GitHub Pages](https://img.shields.io/badge/Pages-online-brightgreen)](https://ppkapiro.github.io/pepecapiro-wp-theme/docs/index.html)

- Tabla resumen (Mobile): `docs/VALIDACION_MVP_v0_2_1.md`.
- Reportes completos (HTML): `docs/lighthouse/index.html`.

## CI
- Health y Lighthouse: workflows en `.github/workflows/`.
- Content Sync: `.github/workflows/content-sync.yml` (auto-apply condicional).

## Notas de Desarrollo
- WP 6.x, PHP 8.2.
- Tema versión actual: ver `style.css`.
- Parser markdown interno (sin dependencias externas) para contenido.

## Roadmap (extracto)
Resumen rápido (ver detalle y estado en `docs/PERFORMANCE_METRICS.md`):

| Item | Estado |
|------|--------|
| Release 0.3.18 | Preparación |
| Lighthouse CLI integrado | Planificado |
| PSI API (LCP/INP campo) | Planificado |
| Quality Gates preflight | Planificado |
| Breadcrumbs JSON-LD | Pendiente |
| Últimas Entradas widget | Pendiente |
| Auditoría hreflang/canonical | Pendiente |
| Primer post real ES/EN | Pendiente |

Detalle técnico y próximos pasos: `docs/PERFORMANCE_METRICS.md` y sección Roadmap en `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md`.


---
Para cualquier modificación estructural, actualizar primero el documento maestro.
