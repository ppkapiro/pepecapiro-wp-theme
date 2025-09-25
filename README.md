# pepecapiro-wp-theme

[![Lighthouse Mobile + Docs](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml/badge.svg)](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml)

Tema WordPress para pepecapiro.com.

Versión estable actual: 0.3.18 (ver `CHANGELOG.md`).

## Documentación Clave
- Índice: `docs/INDEX.md`
- Arquitectura: `docs/ARCHITECTURE.md`
- Automatización de contenido: `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md`
- Operaciones/Gobernanza: `docs/OPERATIONS_OVERVIEW.md`
- Runbook de despliegue: `docs/DEPLOY_RUNBOOK.md`
- Métricas & Observabilidad: `docs/PERFORMANCE_METRICS.md`
- Changelog: `CHANGELOG.md`
- Reportes Lighthouse / auditorías: `docs/`
- SEO Técnico: `SEO_TECH.md`
- Salud de enlaces: `LINKS_HEALTH.md`

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
- PSI histórico: `reports/psi/index.html` (promedios mobile/desktop + enlace a cada run)
- Timeseries: `reports/psi/timeseries.json` (evolución histórica acotada)
- Badge performance móvil: `reports/psi/badge_mobile_performance.json`
- Media reuse: `media_reuse_report.md` / `.json`
- Preflight unificado: artefacto `preflight_report.md` (CI) antes de publicar contenido.
- Auto‑issues PSI + escalado `priority:high` tras 2 fallos consecutivos.
- Soft advisory performance en content-sync (`PERF_ADVISORY:` en logs).

## CI
- Health y Lighthouse: workflows en `.github/workflows/`.
- Content Sync: `.github/workflows/content-sync.yml` (auto-apply condicional).
- Release automático: `.github/workflows/release.yml` (al crear tag `vX.Y.Z` empaqueta y publica ZIP+SHA256 en GitHub Releases).
- Auditoría SEO: `.github/workflows/seo_audit.yml` (canonical, hreflang, JSON-LD)
- Salud enlaces externos: `.github/workflows/external_links.yml` (rotos vs umbral)

### Auto‑publicación y verificación
Si existe el archivo `.auto_apply`, cualquier cambio en `content/` ejecuta publicación directa (sin necesitar `[publish]`). Tras aplicar, el paso `verify_content_live` consulta las URLs publicadas y genera:
- `reports/publish/verify.json`
- `reports/publish/verify.md`

Checks: HTTP 200, fragmento de título esperado y presencia de JSON-LD Article. Si falla, el pipeline refleja el error en el reporte (log no bloqueante de momento — se puede endurecer).

Override temporal: eliminar `.auto_apply` o revertir a borrador cambiando `status` en `posts.json`.

### Publicar un release
```
git tag v0.3.19
git push origin v0.3.19
```
El workflow valida versión en `style.css`, entrada en `CHANGELOG.md`, empaqueta y sube artefactos.

## Notas de Desarrollo
- WP 6.x, PHP 8.2.
- Tema versión actual: ver `style.css`.
- Parser markdown interno (sin dependencias externas) para contenido.

## Roadmap (extracto)
Resumen rápido (ver detalle y estado en `docs/PERFORMANCE_METRICS.md`):

| Item | Estado |
|------|--------|
| Release 0.3.18 | Cerrado |
| Lighthouse CLI integrado | Completado |
| PSI API (LCP/INP campo) | Completado |
| Quality Gates preflight | Completado |
| Breadcrumbs JSON-LD | Completado |
| Últimas Entradas widget | Pendiente |
| Auditoría hreflang/canonical | Completado |
| Primer post real ES/EN | Completado |

Detalle técnico y próximos pasos: `docs/PERFORMANCE_METRICS.md` y sección Roadmap en `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md`.


---
Para cualquier modificación estructural, actualizar primero el documento maestro.
