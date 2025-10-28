# Runbook CI/CD — Ejecución Manual
Generado: 2025-10-27T18:23:11.913405Z

Guía para disparar manualmente cada workflow y revisar sus resultados.

## Uso general
- Ejecutar workflows manuales: `gh workflow run <archivo>`.
- Para `workflow_dispatch` con inputs: `gh workflow run <archivo> --field clave=valor`.
- Revisar estado: `gh run watch --exit-status` y artefactos vía `gh run download`.

## Gestión de secrets
- Ubicación: GitHub Actions (`Settings > Secrets and variables > Actions`) en `ppkapiro/pepecapiro-wp-theme`.
- Responsables: equipo de operaciones/seguridad (propietarios del entorno Hostinger + WordPress); solicitar altas vía ticket interno.
- Rotación: usar `rotate-app-password.yml` para credenciales WP y actualizar tokens externos (PSI, GA4, GSC) coordinando con `docs/SECURITY_NOTES.md`. Tras cada rotación, regenerar el inventario con `python scripts/ci/build_workflow_inventory.py` y validar `reports/ci/missing_secrets.md`.

### API Automation Trigger (`api-automation-trigger.yml`)

- **Propósito:** Dispara pipelines externos vía API para sincronizaciones específicas.
- **Disparadores:** repository_dispatch(types:['automation-trigger']), workflow_dispatch(inputs:{'action': {'description': 'Acción a ejecutar', 'required': True, 'type': 'choice', 'options': ['sync-content', 'rebuild-dashboard', 'run-verifications', 'cleanup-test-data']}, 'target': {'description': 'Objetivo (opcional)', 'required': False, 'type': 'string'}})
- **Inputs `workflow_dispatch`:** action(default=None), target(default=None)
- **Sección DTC relacionada:** Integraciones Externas

Comando sugerido: `gh workflow run api-automation-trigger.yml`

### Cleanup Test Posts (`cleanup-test-posts.yml`)

- **Propósito:** Elimina contenido de prueba en el entorno remoto tras ejecuciones QA.
- **Disparadores:** schedule(cron:17 3 * * *), workflow_dispatch
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run cleanup-test-posts.yml`

### Content Ops (remote WP-CLI) (`content-ops.yml`)

- **Propósito:** Orquesta tareas de contenido (inventarios, validaciones y exportaciones).
- **Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o dry-run (false)', 'required': True, 'default': 'false'}, 'create_privacy': {'description': 'Crear páginas de Privacidad/Cookies ES/EN', 'required': False, 'default': 'true'}, 'publish_post': {'description': 'Publicar primer post ES/EN y eliminar Hello World', 'required': False, 'default': 'true'}, 'unify_contact_es': {'description': 'Asignar plantilla Contacto (bilingüe) a ES', 'required': False, 'default': 'true'}}), push(paths:['.github/content-ops/run.apply', '.github/content-ops/run.dry'])
- **Inputs `workflow_dispatch`:** apply(default=false), create_privacy(default=true), publish_post(default=true), unify_contact_es(default=true)
- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- **Sección DTC relacionada:** Operaciones de Contenido

Comando sugerido: `gh workflow run content-ops.yml`

### Content Sync (`content-sync.yml`)

- **Propósito:** Publica contenido ES/EN en producción usando GitHub Actions (plan/apply).
- **Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o solo plan (false)', 'required': True, 'default': 'false'}}), push(paths:['content/**', 'scripts/publish_content.py', '.github/workflows/content-sync.yml', '.auto_apply'])
- **Inputs `workflow_dispatch`:** apply(default=false)
- **Artefactos clave:** preflight-quality-gates, publish-verification, content-sync-log, content-plan-summary, content-drift-report
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

Comando sugerido: `gh workflow run content-sync.yml`

### Deploy pepecapiro theme (`deploy.yml`)

- **Propósito:** Despliega el tema y assets principales hacia producción.
- **Disparadores:** push(tags:['v*']), workflow_dispatch(inputs:{'version': {'description': 'Versión para desplegar (ej: 0.1.9)', 'required': False}, 'continue_on_verify_fail': {'description': 'Permitir continuar si hay difs en verificación (true/false)', 'required': False, 'default': 'false'}})
- **Inputs `workflow_dispatch`:** version(default=None), continue_on_verify_fail(default=false)
- **Artefactos clave:** content-ops-log, integrity-${{ steps.verify.outputs.mismatches || 'unknown' }}, release-${{ steps.ver.outputs.ver }}-${{ steps.env_tag.outputs.tag }}
- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- **Sección DTC relacionada:** Operaciones / Releases

Comando sugerido: `gh workflow run deploy.yml`

### external_links_health (`external_links.yml`)

- **Propósito:** Verifica enlaces externos y reporta roturas.
- **Disparadores:** workflow_dispatch(), schedule(cron:29 4 * * *)
- **Artefactos clave:** external-links-report
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run external_links.yml`

### Health Dashboard (`health-dashboard.yml`)

- **Propósito:** Genera el dashboard de salud general del sitio.
- **Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Monitoreo Técnico

Comando sugerido: `gh workflow run health-dashboard.yml`

### Hub Aggregation (`hub-aggregation.yml`)

- **Propósito:** Agrega métricas desde servicios externos para informes consolidados.
- **Disparadores:** schedule(cron:*/10 * * * *), workflow_dispatch()
- **Sección DTC relacionada:** Integraciones Externas

Comando sugerido: `gh workflow run hub-aggregation.yml`

### Lighthouse Mobile Audit (`lighthouse.yml`)

- **Propósito:** Ejecuta auditorías Lighthouse en producción.
- **Disparadores:** workflow_dispatch, push(branches:['main'])
- **Artefactos clave:** lighthouse_reports
- **Secrets requeridos:** GITHUB_TOKEN
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run lighthouse.yml`

### Lighthouse CLI Batch (`lighthouse_cli.yml`)

- **Propósito:** Corre Lighthouse desde CLI para smoke tests rápidos.
- **Disparadores:** workflow_dispatch, schedule(cron:0 3 * * *)
- **Artefactos clave:** lighthouse-reports-${{ github.run_id }}
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run lighthouse_cli.yml`

### Lighthouse Mobile + Docs (`lighthouse_docs.yml`)

- **Propósito:** Genera informes Lighthouse en formato HTML y los publica en docs/.
- **Disparadores:** workflow_dispatch(inputs:{'urls_file': {'description': 'Ruta del archivo con URLs', 'required': False, 'default': 'scripts/urls_lighthouse.txt'}}), schedule(cron:0 13 * * 1)
- **Inputs `workflow_dispatch`:** urls_file(default=scripts/urls_lighthouse.txt)
- **Artefactos clave:** lhci_raw, reports_after, lh_fail
- **Secrets requeridos:** PSI_API_KEY
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run lighthouse_docs.yml`

### Prune Old Workflow Runs (`prune-runs.yml`)

- **Propósito:** Limpia ejecuciones antiguas de GitHub Actions para reducir ruido.
- **Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre (name) del workflow a podar (ej: Content Sync). Vacío = todos.', 'required': False, 'default': ''}, 'keep': {'description': 'Número de ejecuciones más recientes a conservar', 'required': True, 'default': '10'}, 'dry_run': {'description': 'true = solo mostrar qué se borraría, false = borrar de verdad', 'required': False, 'default': 'true'}})
- **Inputs `workflow_dispatch`:** workflow(default=), keep(default=10), dry_run(default=true)
- **Artefactos clave:** prune-runs-output
- **Secrets requeridos:** GITHUB_TOKEN
- **Sección DTC relacionada:** Gobernanza y Auditorías

Comando sugerido: `gh workflow run prune-runs.yml`

### PSI Metrics (`psi_metrics.yml`)

- **Propósito:** Consulta PageSpeed Insights y guarda métricas históricas.
- **Disparadores:** workflow_dispatch, schedule(cron:15 3 * * *)
- **Artefactos clave:** psi-run
- **Secrets requeridos:** GITHUB_TOKEN, PSI_API_KEY
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run psi_metrics.yml`

### Publish Prod Menu (`publish-prod-menu.yml`)

- **Propósito:** Aplica cambios de menús en producción.
- **Disparadores:** workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

Comando sugerido: `gh workflow run publish-prod-menu.yml`

### Publish Prod Page (`publish-prod-page.yml`)

- **Propósito:** Publica páginas en producción (ES/EN).
- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod_page.flag']), workflow_dispatch
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

Comando sugerido: `gh workflow run publish-prod-page.yml`

### Publish Prod Post (`publish-prod-post.yml`)

- **Propósito:** Publica posts en producción (ES/EN).
- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod.flag']), workflow_dispatch
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

Comando sugerido: `gh workflow run publish-prod-post.yml`

### Publish Test Menu (`publish-test-menu.yml`)

- **Propósito:** Publica menús en entorno de prueba.
- **Disparadores:** workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run publish-test-menu.yml`

### Publish Test Page (`publish-test-page.yml`)

- **Propósito:** Publica páginas en entorno de prueba.
- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_page.flag']), workflow_dispatch
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run publish-test-page.yml`

### Publish Test Post (`publish-test-post.yml`)

- **Propósito:** Publica posts en entorno de prueba.
- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_post.flag']), workflow_dispatch
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run publish-test-post.yml`

### Build Theme Release (`release.yml`)

- **Propósito:** Genera releases versionadas con artefactos finales.
- **Disparadores:** push(tags:['v*'])
- **Sección DTC relacionada:** Operaciones / Releases

Comando sugerido: `gh workflow run release.yml`

### Rollback pepecapiro theme (`rollback.yml`)

- **Propósito:** Revierte un deployment de emergencia.
- **Disparadores:** workflow_dispatch(inputs:{'zip_url': {'description': 'URL del zip artefacto (o sube el archivo en este run)', 'required': False}})
- **Inputs `workflow_dispatch`:** zip_url(default=None)
- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- **Sección DTC relacionada:** Operaciones / Releases

Comando sugerido: `gh workflow run rollback.yml`

### Rotate Application Password (`rotate-app-password.yml`)

- **Propósito:** Asiste en la rotación del Application Password de WordPress.
- **Disparadores:** workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Seguridad y Accesos

Comando sugerido: `gh workflow run rotate-app-password.yml`

### Run Repair (`run-repair.yml`)

- **Propósito:** Reaplica contenido/ajustes para reparar drift detectado.
- **Disparadores:** workflow_dispatch(inputs:{'area': {'description': 'Área a reparar', 'type': 'choice', 'required': True, 'options': ['home', 'menus', 'media', 'settings']}, 'mode': {'description': 'Modo (plan/apply)', 'type': 'choice', 'required': False, 'default': 'apply', 'options': ['plan', 'apply']}})
- **Inputs `workflow_dispatch`:** area(default=None), mode(default=apply)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Gobernanza y Auditorías

Comando sugerido: `gh workflow run run-repair.yml`

### Workflow Runs Summary (`runs-summary.yml`)

- **Propósito:** Resume ejecuciones recientes y publica un reporte.
- **Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre del workflow a filtrar (vacío = todos)', 'required': False, 'default': ''}, 'limit': {'description': 'Número máximo de runs listados por workflow', 'required': True, 'default': '40'}})
- **Inputs `workflow_dispatch`:** workflow(default=), limit(default=40)
- **Artefactos clave:** workflow-runs-summary
- **Secrets requeridos:** GITHUB_TOKEN
- **Sección DTC relacionada:** Gobernanza y Auditorías

Comando sugerido: `gh workflow run runs-summary.yml`

### seo_audit (`seo_audit.yml`)

- **Propósito:** Auditoría SEO técnica (hreflang, canonical, schema, etc.).
- **Disparadores:** workflow_dispatch(), schedule(cron:17 3 * * *), push(branches:['main'])
- **Artefactos clave:** seo-audit
- **Sección DTC relacionada:** Fase 4 – SEO/Performance

Comando sugerido: `gh workflow run seo_audit.yml`

### Set Home Page (`set-home.yml`)

- **Propósito:** Configura la página inicial del sitio.
- **Disparadores:** workflow_dispatch(inputs:{'page_id_es': {'description': 'ID de la página ES a fijar como Home (opcional)', 'required': False}, 'page_slug_es': {'description': 'Slug de la página ES a fijar como Home (opcional)', 'required': False}, 'page_id_en': {'description': 'ID de la página EN a vincular (opcional)', 'required': False}, 'page_slug_en': {'description': 'Slug de la página EN a vincular (opcional)', 'required': False}})
- **Inputs `workflow_dispatch`:** page_id_es(default=None), page_slug_es(default=None), page_id_en(default=None), page_slug_en(default=None)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Operaciones / Releases

Comando sugerido: `gh workflow run set-home.yml`

### Site Health & Auto-Remediation (`site-health.yml`)

- **Propósito:** Ejecuta el informe de salud del sitio desde WP.
- **Disparadores:** schedule(cron:*/30 * * * *), workflow_dispatch
- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- **Sección DTC relacionada:** Monitoreo Técnico

Comando sugerido: `gh workflow run site-health.yml`

### Site Settings (`site-settings.yml`)

- **Propósito:** Sincroniza configuraciones clave del sitio.
- **Disparadores:** workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Operaciones / Releases

Comando sugerido: `gh workflow run site-settings.yml`

### Smoke Tests (`smoke-tests.yml`)

- **Propósito:** Ejecución de smoke tests end-to-end.
- **Disparadores:** push(branches:['main']), workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run smoke-tests.yml`

### CI Status Probe (`status.yml`)

- **Propósito:** Actualiza public/status.json con métricas actuales.
- **Disparadores:** workflow_dispatch, push
- **Sección DTC relacionada:** Monitoreo Técnico

Comando sugerido: `gh workflow run status.yml`

### UI Visual Gates (`ui-gates.yml`)

- **Propósito:** Workflow sin descripción específica (añadir en WORKFLOW_DESCRIPTIONS).
- **Disparadores:** workflow_dispatch, push(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py', '.github/workflows/ui-gates.yml']), pull_request(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py'])
- **Sección DTC relacionada:** Operaciones Generales

Comando sugerido: `gh workflow run ui-gates.yml`

### Upload Media (`upload-media.yml`)

- **Propósito:** Sincroniza assets multimedia optimizados.
- **Disparadores:** workflow_dispatch()
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

Comando sugerido: `gh workflow run upload-media.yml`

### Verify Home (`verify-home.yml`)

- **Propósito:** Smoke test para la portada (contenido + links).
- **Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run verify-home.yml`

### Verify Media (`verify-media.yml`)

- **Propósito:** Verifica assets y referencias multimedia.
- **Disparadores:** workflow_dispatch(), schedule(cron:0 3 * * *)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run verify-media.yml`

### Verify Menus (`verify-menus.yml`)

- **Propósito:** Comprueba consistencia de menús.
- **Disparadores:** workflow_dispatch(), schedule(cron:0 */12 * * *)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run verify-menus.yml`

### Verify Settings (`verify-settings.yml`)

- **Propósito:** Valida settings críticos en WP.
- **Disparadores:** workflow_dispatch(), schedule(cron:0 0 * * *)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** QA y Auditoría Continua

Comando sugerido: `gh workflow run verify-settings.yml`

### Webhook GitHub to WordPress (`webhook-github-to-wp.yml`)

- **Propósito:** Entrega webhook hacia WordPress para acciones remotas.
- **Disparadores:** push(branches:['main']; paths:['content/**']), release(types:['published']), workflow_dispatch(inputs:{'sync_type': {'description': 'Tipo de sincronización', 'required': True, 'type': 'choice', 'options': ['content', 'menus', 'media']}})
- **Inputs `workflow_dispatch`:** sync_type(default=None)
- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER
- **Sección DTC relacionada:** Integraciones Externas

Comando sugerido: `gh workflow run webhook-github-to-wp.yml`

### Weekly Audit (`weekly-audit.yml`)

- **Propósito:** Auditoría semanal de drift y disparo de verificaciones clave.
- **Disparadores:** workflow_dispatch(), schedule(cron:0 2 * * 0)
- **Sección DTC relacionada:** Gobernanza y Auditorías

Comando sugerido: `gh workflow run weekly-audit.yml`
