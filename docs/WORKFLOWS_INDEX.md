# Índice de Workflows CI/CD
Generado: 2025-10-27T18:23:11.913405Z

Este índice resume cada workflow disponible en `.github/workflows/`.

## API Automation Trigger — `api-automation-trigger.yml`

**Descripción:** Dispara pipelines externos vía API para sincronizaciones específicas.
**Disparadores:** repository_dispatch(types:['automation-trigger']), workflow_dispatch(inputs:{'action': {'description': 'Acción a ejecutar', 'required': True, 'type': 'choice', 'options': ['sync-content', 'rebuild-dashboard', 'run-verifications', 'cleanup-test-data']}, 'target': {'description': 'Objetivo (opcional)', 'required': False, 'type': 'string'}})
**Jobs:** trigger
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Integraciones Externas

[Ver workflow](../.github/workflows/api-automation-trigger.yml)

## Cleanup Test Posts — `cleanup-test-posts.yml`

**Descripción:** Elimina contenido de prueba en el entorno remoto tras ejecuciones QA.
**Disparadores:** schedule(cron:17 3 * * *), workflow_dispatch
**Jobs:** cleanup
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/cleanup-test-posts.yml)

## Content Ops (remote WP-CLI) — `content-ops.yml`

**Descripción:** Orquesta tareas de contenido (inventarios, validaciones y exportaciones).
**Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o dry-run (false)', 'required': True, 'default': 'false'}, 'create_privacy': {'description': 'Crear páginas de Privacidad/Cookies ES/EN', 'required': False, 'default': 'true'}, 'publish_post': {'description': 'Publicar primer post ES/EN y eliminar Hello World', 'required': False, 'default': 'true'}, 'unify_contact_es': {'description': 'Asignar plantilla Contacto (bilingüe) a ES', 'required': False, 'default': 'true'}}), push(paths:['.github/content-ops/run.apply', '.github/content-ops/run.dry'])
**Jobs:** run
**Artefactos:** —
**Secrets:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
**Sección DTC:** Operaciones de Contenido

[Ver workflow](../.github/workflows/content-ops.yml)

## Content Sync — `content-sync.yml`

**Descripción:** Publica contenido ES/EN en producción usando GitHub Actions (plan/apply).
**Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o solo plan (false)', 'required': True, 'default': 'false'}}), push(paths:['content/**', 'scripts/publish_content.py', '.github/workflows/content-sync.yml', '.auto_apply'])
**Jobs:** sync
**Artefactos:** preflight-quality-gates, publish-verification, content-sync-log, content-plan-summary, content-drift-report
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Fase 1 – Contenido Bilingüe

[Ver workflow](../.github/workflows/content-sync.yml)

## Deploy pepecapiro theme — `deploy.yml`

**Descripción:** Despliega el tema y assets principales hacia producción.
**Disparadores:** push(tags:['v*']), workflow_dispatch(inputs:{'version': {'description': 'Versión para desplegar (ej: 0.1.9)', 'required': False}, 'continue_on_verify_fail': {'description': 'Permitir continuar si hay difs en verificación (true/false)', 'required': False, 'default': 'false'}})
**Jobs:** deploy
**Artefactos:** content-ops-log, integrity-${{ steps.verify.outputs.mismatches || 'unknown' }}, release-${{ steps.ver.outputs.ver }}-${{ steps.env_tag.outputs.tag }}
**Secrets:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
**Sección DTC:** Operaciones / Releases

[Ver workflow](../.github/workflows/deploy.yml)

## external_links_health — `external_links.yml`

**Descripción:** Verifica enlaces externos y reporta roturas.
**Disparadores:** workflow_dispatch(), schedule(cron:29 4 * * *)
**Jobs:** scan
**Artefactos:** external-links-report
**Secrets:** —
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/external_links.yml)

## Health Dashboard — `health-dashboard.yml`

**Descripción:** Genera el dashboard de salud general del sitio.
**Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)
**Jobs:** generate-status
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Monitoreo Técnico

[Ver workflow](../.github/workflows/health-dashboard.yml)

## Hub Aggregation — `hub-aggregation.yml`

**Descripción:** Agrega métricas desde servicios externos para informes consolidados.
**Disparadores:** schedule(cron:*/10 * * * *), workflow_dispatch()
**Jobs:** aggregate
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Integraciones Externas

[Ver workflow](../.github/workflows/hub-aggregation.yml)

## Lighthouse Mobile Audit — `lighthouse.yml`

**Descripción:** Ejecuta auditorías Lighthouse en producción.
**Disparadores:** workflow_dispatch, push(branches:['main'])
**Jobs:** lighthouse
**Artefactos:** lighthouse_reports
**Secrets:** GITHUB_TOKEN
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/lighthouse.yml)

## Lighthouse CLI Batch — `lighthouse_cli.yml`

**Descripción:** Corre Lighthouse desde CLI para smoke tests rápidos.
**Disparadores:** workflow_dispatch, schedule(cron:0 3 * * *)
**Jobs:** lh
**Artefactos:** lighthouse-reports-${{ github.run_id }}
**Secrets:** —
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/lighthouse_cli.yml)

## Lighthouse Mobile + Docs — `lighthouse_docs.yml`

**Descripción:** Genera informes Lighthouse en formato HTML y los publica en docs/.
**Disparadores:** workflow_dispatch(inputs:{'urls_file': {'description': 'Ruta del archivo con URLs', 'required': False, 'default': 'scripts/urls_lighthouse.txt'}}), schedule(cron:0 13 * * 1)
**Jobs:** audit-and-update
**Artefactos:** lhci_raw, reports_after, lh_fail
**Secrets:** PSI_API_KEY
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/lighthouse_docs.yml)

## Prune Old Workflow Runs — `prune-runs.yml`

**Descripción:** Limpia ejecuciones antiguas de GitHub Actions para reducir ruido.
**Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre (name) del workflow a podar (ej: Content Sync). Vacío = todos.', 'required': False, 'default': ''}, 'keep': {'description': 'Número de ejecuciones más recientes a conservar', 'required': True, 'default': '10'}, 'dry_run': {'description': 'true = solo mostrar qué se borraría, false = borrar de verdad', 'required': False, 'default': 'true'}})
**Jobs:** prune
**Artefactos:** prune-runs-output
**Secrets:** GITHUB_TOKEN
**Sección DTC:** Gobernanza y Auditorías

[Ver workflow](../.github/workflows/prune-runs.yml)

## PSI Metrics — `psi_metrics.yml`

**Descripción:** Consulta PageSpeed Insights y guarda métricas históricas.
**Disparadores:** workflow_dispatch, schedule(cron:15 3 * * *)
**Jobs:** psi
**Artefactos:** psi-run
**Secrets:** GITHUB_TOKEN, PSI_API_KEY
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/psi_metrics.yml)

## Publish Prod Menu — `publish-prod-menu.yml`

**Descripción:** Aplica cambios de menús en producción.
**Disparadores:** workflow_dispatch()
**Jobs:** publish-prod-menu
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Fase 1 – Contenido Bilingüe

[Ver workflow](../.github/workflows/publish-prod-menu.yml)

## Publish Prod Page — `publish-prod-page.yml`

**Descripción:** Publica páginas en producción (ES/EN).
**Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod_page.flag']), workflow_dispatch
**Jobs:** publish
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Fase 1 – Contenido Bilingüe

[Ver workflow](../.github/workflows/publish-prod-page.yml)

## Publish Prod Post — `publish-prod-post.yml`

**Descripción:** Publica posts en producción (ES/EN).
**Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod.flag']), workflow_dispatch
**Jobs:** publish
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Fase 1 – Contenido Bilingüe

[Ver workflow](../.github/workflows/publish-prod-post.yml)

## Publish Test Menu — `publish-test-menu.yml`

**Descripción:** Publica menús en entorno de prueba.
**Disparadores:** workflow_dispatch()
**Jobs:** publish-test-menu
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/publish-test-menu.yml)

## Publish Test Page — `publish-test-page.yml`

**Descripción:** Publica páginas en entorno de prueba.
**Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_page.flag']), workflow_dispatch
**Jobs:** publish
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/publish-test-page.yml)

## Publish Test Post — `publish-test-post.yml`

**Descripción:** Publica posts en entorno de prueba.
**Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_post.flag']), workflow_dispatch
**Jobs:** publish
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/publish-test-post.yml)

## Build Theme Release — `release.yml`

**Descripción:** Genera releases versionadas con artefactos finales.
**Disparadores:** push(tags:['v*'])
**Jobs:** build-release
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Operaciones / Releases

[Ver workflow](../.github/workflows/release.yml)

## Rollback pepecapiro theme — `rollback.yml`

**Descripción:** Revierte un deployment de emergencia.
**Disparadores:** workflow_dispatch(inputs:{'zip_url': {'description': 'URL del zip artefacto (o sube el archivo en este run)', 'required': False}})
**Jobs:** rollback
**Artefactos:** —
**Secrets:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
**Sección DTC:** Operaciones / Releases

[Ver workflow](../.github/workflows/rollback.yml)

## Rotate Application Password — `rotate-app-password.yml`

**Descripción:** Asiste en la rotación del Application Password de WordPress.
**Disparadores:** workflow_dispatch()
**Jobs:** rotate-app-password
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Seguridad y Accesos

[Ver workflow](../.github/workflows/rotate-app-password.yml)

## Run Repair — `run-repair.yml`

**Descripción:** Reaplica contenido/ajustes para reparar drift detectado.
**Disparadores:** workflow_dispatch(inputs:{'area': {'description': 'Área a reparar', 'type': 'choice', 'required': True, 'options': ['home', 'menus', 'media', 'settings']}, 'mode': {'description': 'Modo (plan/apply)', 'type': 'choice', 'required': False, 'default': 'apply', 'options': ['plan', 'apply']}})
**Jobs:** run-repair
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Gobernanza y Auditorías

[Ver workflow](../.github/workflows/run-repair.yml)

## Workflow Runs Summary — `runs-summary.yml`

**Descripción:** Resume ejecuciones recientes y publica un reporte.
**Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre del workflow a filtrar (vacío = todos)', 'required': False, 'default': ''}, 'limit': {'description': 'Número máximo de runs listados por workflow', 'required': True, 'default': '40'}})
**Jobs:** summary
**Artefactos:** workflow-runs-summary
**Secrets:** GITHUB_TOKEN
**Sección DTC:** Gobernanza y Auditorías

[Ver workflow](../.github/workflows/runs-summary.yml)

## seo_audit — `seo_audit.yml`

**Descripción:** Auditoría SEO técnica (hreflang, canonical, schema, etc.).
**Disparadores:** workflow_dispatch(), schedule(cron:17 3 * * *), push(branches:['main'])
**Jobs:** audit
**Artefactos:** seo-audit
**Secrets:** —
**Sección DTC:** Fase 4 – SEO/Performance

[Ver workflow](../.github/workflows/seo_audit.yml)

## Set Home Page — `set-home.yml`

**Descripción:** Configura la página inicial del sitio.
**Disparadores:** workflow_dispatch(inputs:{'page_id_es': {'description': 'ID de la página ES a fijar como Home (opcional)', 'required': False}, 'page_slug_es': {'description': 'Slug de la página ES a fijar como Home (opcional)', 'required': False}, 'page_id_en': {'description': 'ID de la página EN a vincular (opcional)', 'required': False}, 'page_slug_en': {'description': 'Slug de la página EN a vincular (opcional)', 'required': False}})
**Jobs:** set-home
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Operaciones / Releases

[Ver workflow](../.github/workflows/set-home.yml)

## Site Health & Auto-Remediation — `site-health.yml`

**Descripción:** Ejecuta el informe de salud del sitio desde WP.
**Disparadores:** schedule(cron:*/30 * * * *), workflow_dispatch
**Jobs:** health
**Artefactos:** —
**Secrets:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
**Sección DTC:** Monitoreo Técnico

[Ver workflow](../.github/workflows/site-health.yml)

## Site Settings — `site-settings.yml`

**Descripción:** Sincroniza configuraciones clave del sitio.
**Disparadores:** workflow_dispatch()
**Jobs:** site-settings
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Operaciones / Releases

[Ver workflow](../.github/workflows/site-settings.yml)

## Smoke Tests — `smoke-tests.yml`

**Descripción:** Ejecución de smoke tests end-to-end.
**Disparadores:** push(branches:['main']), workflow_dispatch()
**Jobs:** smoke
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/smoke-tests.yml)

## CI Status Probe — `status.yml`

**Descripción:** Actualiza public/status.json con métricas actuales.
**Disparadores:** workflow_dispatch, push
**Jobs:** probe
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Monitoreo Técnico

[Ver workflow](../.github/workflows/status.yml)

## UI Visual Gates — `ui-gates.yml`

**Descripción:** Workflow sin descripción específica (añadir en WORKFLOW_DESCRIPTIONS).
**Disparadores:** workflow_dispatch, push(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py', '.github/workflows/ui-gates.yml']), pull_request(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py'])
**Jobs:** css-anti-hex
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Operaciones Generales

[Ver workflow](../.github/workflows/ui-gates.yml)

## Upload Media — `upload-media.yml`

**Descripción:** Sincroniza assets multimedia optimizados.
**Disparadores:** workflow_dispatch()
**Jobs:** upload-media
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Fase 1 – Contenido Bilingüe

[Ver workflow](../.github/workflows/upload-media.yml)

## Verify Home — `verify-home.yml`

**Descripción:** Smoke test para la portada (contenido + links).
**Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)
**Jobs:** verify-home
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/verify-home.yml)

## Verify Media — `verify-media.yml`

**Descripción:** Verifica assets y referencias multimedia.
**Disparadores:** workflow_dispatch(), schedule(cron:0 3 * * *)
**Jobs:** verify-media
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/verify-media.yml)

## Verify Menus — `verify-menus.yml`

**Descripción:** Comprueba consistencia de menús.
**Disparadores:** workflow_dispatch(), schedule(cron:0 */12 * * *)
**Jobs:** verify-menus
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/verify-menus.yml)

## Verify Settings — `verify-settings.yml`

**Descripción:** Valida settings críticos en WP.
**Disparadores:** workflow_dispatch(), schedule(cron:0 0 * * *)
**Jobs:** verify-settings
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** QA y Auditoría Continua

[Ver workflow](../.github/workflows/verify-settings.yml)

## Webhook GitHub to WordPress — `webhook-github-to-wp.yml`

**Descripción:** Entrega webhook hacia WordPress para acciones remotas.
**Disparadores:** push(branches:['main']; paths:['content/**']), release(types:['published']), workflow_dispatch(inputs:{'sync_type': {'description': 'Tipo de sincronización', 'required': True, 'type': 'choice', 'options': ['content', 'menus', 'media']}})
**Jobs:** sync-to-wp
**Artefactos:** —
**Secrets:** WP_APP_PASSWORD, WP_URL, WP_USER
**Sección DTC:** Integraciones Externas

[Ver workflow](../.github/workflows/webhook-github-to-wp.yml)

## Weekly Audit — `weekly-audit.yml`

**Descripción:** Auditoría semanal de drift y disparo de verificaciones clave.
**Disparadores:** workflow_dispatch(), schedule(cron:0 2 * * 0)
**Jobs:** audit
**Artefactos:** —
**Secrets:** —
**Sección DTC:** Gobernanza y Auditorías

[Ver workflow](../.github/workflows/weekly-audit.yml)
