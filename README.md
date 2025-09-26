# pepecapiro-wp-theme

[![Lighthouse Mobile + Docs](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml/badge.svg)](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml)

Tema WordPress para pepecapiro.com.

Versión estable actual: 0.3.19 (ver `CHANGELOG.md`).

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
- Troubleshooting publicación: `docs/TROUBLESHOOTING_PUBLICACION.md`
- Snapshot estado (25 Sep 2025): `docs/STATUS_SNAPSHOT_2025-09-25.md`

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

## Estado Actual de la Automatización de Contenido (Sept 2025)

| Aspecto | Estado | Notas |
|---------|--------|-------|
| Infra CI (plan/apply) | OK | Fallback a PLAN si faltan secretos |
| Autenticación REST | PENDIENTE VALIDACIÓN | Se requieren 201 en POST /wp/v2/posts (actualmente 401) |
| Segundo post (governance-automation-pillars) | BLOQUEADO | Contenido listo, falla creación/update por 401 rest_cannot_create/rest_cannot_edit |
| Traducciones enlazadas | PENDIENTE | Se completará tras primer 201 exitoso |
| Próximos contenidos | En cola | Ver sección Roadmap y próximos posts |

Bloqueador actual: ausencia (o uso incorrecto) de un Application Password válido para el usuario publicador → respuestas 401. Una vez resuelto y verificado `/users/me` con 200, re‑ejecutar pipeline con `[publish]`.

### Requisitos de Credenciales (Secrets GitHub)

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `WP_URL` | URL base HTTPS del sitio | `https://pepecapiro.com` |
| `WP_USER` | Usuario WP con rol capaz de crear/editar posts (author/editor) | `ppcapiro` |
| `WP_APP_PASSWORD` | Application Password creado para `WP_USER` | `XXXX XXXX XXXX XXXX` |

Cómo generar `WP_APP_PASSWORD`:
1. Ingresar a WP Admin con `WP_USER`.
2. Ir a Perfil (Users > Profile / Tu perfil).
3. Sección "Application Passwords": introducir etiqueta (ej: `ci-content-sync`).
4. Click "Add New Application Password".
5. Copiar el valor COMPLETO exactamente (incluye espacios). No se vuelve a mostrar.
6. Guardarlo como secret `WP_APP_PASSWORD` en el repositorio.
7. Si se expone, revocar y regenerar (rotación).

Errores comunes:
- Usar la contraseña normal del usuario en lugar de un Application Password.
- Copiar con espacios iniciales/finales o saltos de línea.
- Usuario sin capacidad `publish_posts` / `edit_posts`.

### Verificación Rápida Local (antes de relanzar CI)

Configurar variables (NO commit, sólo en tu shell):

```bash
export WP_URL="https://pepecapiro.com"
export WP_USER="ppcapiro"
export WP_APP_PASSWORD="<application_password_exacto>"
AUTH_TOKEN=$(printf "%s:%s" "$WP_USER" "$WP_APP_PASSWORD" | base64)

echo "Token listo (no se muestra)"  # sanity
```

1. Comprobar raíz REST:
```bash
curl -i "$WP_URL/wp-json/"
```
Debe devolver 200 y listar namespaces (`wp/v2`, etc.).

2. Comprobar identidad autenticada:
```bash
curl -i -H "Authorization: Basic $AUTH_TOKEN" "$WP_URL/wp-json/wp/v2/users/me"
```
Esperado: 200 y JSON con `slug":"ppcapiro"` y un `id` (anótalo si lo necesitas para debugging futuro).

3. Prueba de creación de borrador mínima (opcional, sólo si quieres aislar antes de CI):
```bash
curl -i -X POST \
	-H "Authorization: Basic $AUTH_TOKEN" \
	-H "Content-Type: application/json" \
	-d '{"title":"diag-ci","status":"draft","content":"temp"}' \
	"$WP_URL/wp-json/wp/v2/posts"
```
Resultado esperado: 201 Created. Si obtienes 401/403 revisar sección Troubleshooting.

4. (Limpieza) Eliminar el draft de prueba (sustituye <ID>):
```bash
curl -i -X DELETE -H "Authorization: Basic $AUTH_TOKEN" "$WP_URL/wp-json/wp/v2/posts/<ID>?force=true"
```

### Disparar Publicación (apply)

Tras verificar autenticación:
```bash
git commit --allow-empty -m "chore: retry publish governance post [publish]"
git push
```
O mantener `.auto_apply` para aplicar automáticamente cada cambio en `content/`.

### Troubleshooting 401/403 Rápido

| Síntoma | Causa Probable | Acción |
|---------|----------------|--------|
| 401 rest_cannot_create | Application Password incorrecto o header no llega | Regenerar password, verificar paso curl /users/me |
| 403 rest_cannot_edit | Usuario sin permisos sobre el post existente | Usar rol editor/author propietario o cambiar autor | 
| 401 sólo en POST pero /users/me 200 | Falta capability específica | Revisar rol / plugins de seguridad |
| 0 (vacío) / bloqueo | ModSecurity / WAF filtrando | Revisar logs servidor / desactivar regla |
| 404 en endpoint posts | Reescrituras / permalinks rotos | Guardar permalinks WP Admin de nuevo |

Más detalle y flujo completo: ver `docs/TROUBLESHOOTING_PUBLICACION.md`.


### Automatización WordPress (bilingüe)
Resumen de workflows:
- Publish Test Post: crea entradas ES/EN en estado `private`, intenta vincular traducciones (Polylang) y muestra resumen (Auth, IDs, links, vínculo, categorías). Para pruebas.
- Publish Prod Post: publica ES/EN en `publish`, idempotente por slug por idioma; vincula y asigna categorías si existen (ES: Blog/Guías; EN: Blog/Guides). Disparo por flag y/o workflow_dispatch.
- Cleanup Test Posts: elimina posts de prueba antiguos (cron diario) y puede lanzarse manualmente.
- Content Sync: no cambia en esta etapa (sólo catálogo; ver `content-sync.yml`).

Cómo dispararlos:
- Flags: modifica `.github/auto/publish_test_post.flag` o `.github/auto/publish_prod.flag` y haz push a `main`.
- Manual: desde Actions → "Run workflow".

Multilenguaje y vinculación:
- Los workflows detectan Polylang (o WPML) y establecen `?lang=es|en` al crear; luego intentan vincular mediante meta `pll_translations` (best‑effort, sin exponer secretos en logs).

Guía de flags: `.github/auto/README.flags.md`.

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

## Mantenimiento: Limpieza de ejecuciones CI

Con el uso continuo se acumulan muchos workflow runs (p.ej. >100) ocupando espacio y ruido visual.

Opciones de limpieza:

1. Workflow manual: `Prune Old Workflow Runs`
	 - Inputs:
		 - `workflow`: nombre exacto (ej: `Content Sync`) o vacío para todos.
		 - `keep`: número de ejecuciones más recientes a conservar.
	 - Ejecuta paginando y borra el resto (usa GitHub API con token del repo).
2. Script local: `scripts/prune_runs_local.sh`
	 - Requiere `gh` y `jq` instalados y autenticación `gh auth login`.
	 - Ejemplos:
		 - `./scripts/prune_runs_local.sh "Content Sync" 25`
		 - `./scripts/prune_runs_local.sh "" 50` (todos los workflows, conserva 50)

Relanzar sincronización de contenido tras limpieza:
```
git commit --allow-empty -m "chore: retrigger content sync [publish]"
git push
```
O vía Actions → `Content Sync` → `Run workflow` con `apply=true`.
