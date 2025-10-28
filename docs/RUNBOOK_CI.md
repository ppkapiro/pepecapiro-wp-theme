# Runbook CI/CD - Workflows del Proyecto# Runbook CI/CD — Ejecución Manual

Generado: 2025-10-27T18:23:11.913405Z

**Última actualización:** 2025-10-28 (post-conversión a repositorio público)

Guía para disparar manualmente cada workflow y revisar sus resultados.

---

## Uso general

## Índice- Ejecutar workflows manuales: `gh workflow run <archivo>`.

- Para `workflow_dispatch` con inputs: `gh workflow run <archivo> --field clave=valor`.

1. [Workflows por categoría](#workflows-por-categoría)- Revisar estado: `gh run watch --exit-status` y artefactos vía `gh run download`.

2. [Triggers y concurrency](#triggers-y-concurrency)

3. [Control de costos (repo público)](#control-de-costos-repo-público)## Gestión de secrets

4. [Workflows críticos](#workflows-críticos)- Ubicación: GitHub Actions (`Settings > Secrets and variables > Actions`) en `ppkapiro/pepecapiro-wp-theme`.

5. [Reglas de operación](#reglas-de-operación)- Responsables: equipo de operaciones/seguridad (propietarios del entorno Hostinger + WordPress); solicitar altas vía ticket interno.

6. [Troubleshooting](#troubleshooting)- Rotación: usar `rotate-app-password.yml` para credenciales WP y actualizar tokens externos (PSI, GA4, GSC) coordinando con `docs/SECURITY_NOTES.md`. Tras cada rotación, regenerar el inventario con `python scripts/ci/build_workflow_inventory.py` y validar `reports/ci/missing_secrets.md`.



---### API Automation Trigger (`api-automation-trigger.yml`)



## Workflows por categoría- **Propósito:** Dispara pipelines externos vía API para sincronizaciones específicas.

- **Disparadores:** repository_dispatch(types:['automation-trigger']), workflow_dispatch(inputs:{'action': {'description': 'Acción a ejecutar', 'required': True, 'type': 'choice', 'options': ['sync-content', 'rebuild-dashboard', 'run-verifications', 'cleanup-test-data']}, 'target': {'description': 'Objetivo (opcional)', 'required': False, 'type': 'string'}})

### 1. Auditorías de rendimiento (pesadas - rate-limited)- **Inputs `workflow_dispatch`:** action(default=None), target(default=None)

- **Sección DTC relacionada:** Integraciones Externas

| Workflow | Archivo | Triggers | Duración aprox | Artifacts | Secrets |

|----------|---------|----------|----------------|-----------|---------|Comando sugerido: `gh workflow run api-automation-trigger.yml`

| **Lighthouse Audit** | `lighthouse.yml` | push (main), workflow_dispatch | 8 min | lighthouse_reports | - |

| **PSI Metrics** | `psi_metrics.yml` | schedule (diario 03:15), workflow_dispatch | 5 min | psi_reports | PSI_API_KEY |### Cleanup Test Posts (`cleanup-test-posts.yml`)

| **Weekly Audit** | `weekly-audit.yml` | schedule (domingo 02:00), workflow_dispatch | 15 min | audit_reports | - |

- **Propósito:** Elimina contenido de prueba en el entorno remoto tras ejecuciones QA.

**Concurrency:** ✅ Implementada (group por ref + cancel-in-progress)- **Disparadores:** schedule(cron:17 3 * * *), workflow_dispatch

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

### 2. Validaciones funcionales (ligeras)- **Sección DTC relacionada:** QA y Auditoría Continua



| Workflow | Archivo | Triggers | Duración aprox | Secrets |Comando sugerido: `gh workflow run cleanup-test-posts.yml`

|----------|---------|----------|----------------|---------|

| **Smoke Tests** | `smoke-tests.yml` | push (main), workflow_dispatch | 2-3 min | - |### Content Ops (remote WP-CLI) (`content-ops.yml`)

| **SEO Audit** | `seo_audit.yml` | push (main), schedule (diario 03:17), workflow_dispatch | 2 min | - |

| **CI Status Probe** | `ci_status_probe.yml` | push (main) | 1 min | - |- **Propósito:** Orquesta tareas de contenido (inventarios, validaciones y exportaciones).

| **Verify Media** | `verify-media.yml` | schedule, workflow_dispatch | 3 min | - |- **Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o dry-run (false)', 'required': True, 'default': 'false'}, 'create_privacy': {'description': 'Crear páginas de Privacidad/Cookies ES/EN', 'required': False, 'default': 'true'}, 'publish_post': {'description': 'Publicar primer post ES/EN y eliminar Hello World', 'required': False, 'default': 'true'}, 'unify_contact_es': {'description': 'Asignar plantilla Contacto (bilingüe) a ES', 'required': False, 'default': 'true'}}), push(paths:['.github/content-ops/run.apply', '.github/content-ops/run.dry'])

| **Verify Menus** | `verify-menus.yml` | schedule, workflow_dispatch | 2 min | - |- **Inputs `workflow_dispatch`:** apply(default=false), create_privacy(default=true), publish_post(default=true), unify_contact_es(default=true)

- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER

**Concurrency:** ✅ SEO Audit implementada; otros triviales (no requieren)- **Sección DTC relacionada:** Operaciones de Contenido



### 3. Mantenimiento y sincronizaciónComando sugerido: `gh workflow run content-ops.yml`



| Workflow | Archivo | Triggers | Duración aprox | Secrets |### Content Sync (`content-sync.yml`)

|----------|---------|----------|----------------|---------|

| **Content Sync** | `content-sync.yml` | workflow_dispatch (manual) | 5 min | WP_APP_PASSWORD |- **Propósito:** Publica contenido ES/EN en producción usando GitHub Actions (plan/apply).

| **Publish Test Post** | `publish-test-post.yml` | workflow_dispatch (manual) | 2 min | WP_APP_PASSWORD |- **Disparadores:** workflow_dispatch(inputs:{'apply': {'description': 'Aplicar cambios (true) o solo plan (false)', 'required': True, 'default': 'false'}}), push(paths:['content/**', 'scripts/publish_content.py', '.github/workflows/content-sync.yml', '.auto_apply'])

| **Link Scan** | `link-scan.yml` | schedule, workflow_dispatch | 10 min | - |- **Inputs `workflow_dispatch`:** apply(default=false)

| **Health Dashboard** | `health-dashboard.yml` | schedule (diario 04:00), workflow_dispatch | 5 min | - |- **Artefactos clave:** preflight-quality-gates, publish-verification, content-sync-log, content-plan-summary, content-drift-report

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

**Concurrency:** ✅ Content Sync implementada (group: content-sync-main)- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe



### 4. Deploy y administraciónComando sugerido: `gh workflow run content-sync.yml`



| Workflow | Archivo | Triggers | Duración aprox | Secrets |### Deploy pepecapiro theme (`deploy.yml`)

|----------|---------|----------|----------------|---------|

| **Deploy Theme** | `deploy.yml` | workflow_dispatch (manual) | 3 min | SSH_PRIVATE_KEY, REMOTE_HOST, REMOTE_USER |- **Propósito:** Despliega el tema y assets principales hacia producción.

| **Site Settings** | `site-settings.yml` | workflow_dispatch (manual) | 2 min | WP_APP_PASSWORD |- **Disparadores:** push(tags:['v*']), workflow_dispatch(inputs:{'version': {'description': 'Versión para desplegar (ej: 0.1.9)', 'required': False}, 'continue_on_verify_fail': {'description': 'Permitir continuar si hay difs en verificación (true/false)', 'required': False, 'default': 'false'}})

| **Finalize Blog** | `finalize-blog.yml` | workflow_dispatch (manual) | 3 min | WP_APP_PASSWORD |- **Inputs `workflow_dispatch`:** version(default=None), continue_on_verify_fail(default=false)

| **Run Repair** | `run-repair.yml` | workflow_dispatch (manual) | variable | WP_APP_PASSWORD |- **Artefactos clave:** content-ops-log, integrity-${{ steps.verify.outputs.mismatches || 'unknown' }}, release-${{ steps.ver.outputs.ver }}-${{ steps.env_tag.outputs.tag }}

- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER

**Nota:** Todos `workflow_dispatch` - NO se disparan automáticamente (seguridad).- **Sección DTC relacionada:** Operaciones / Releases



### 5. Agregación y reportesComando sugerido: `gh workflow run deploy.yml`



| Workflow | Archivo | Triggers | Duración aprox |### external_links_health (`external_links.yml`)

|----------|---------|----------|----------------|

| **Hub Aggregation** | `hub-aggregation.yml` | schedule (cada 6h), workflow_dispatch | 2 min |- **Propósito:** Verifica enlaces externos y reporta roturas.

| **Lighthouse Docs** | `lighthouse_docs.yml` | schedule (diario 04:30), workflow_dispatch | 3 min |- **Disparadores:** workflow_dispatch(), schedule(cron:29 4 * * *)

- **Artefactos clave:** external-links-report

---- **Sección DTC relacionada:** Fase 4 – SEO/Performance



## Triggers y concurrencyComando sugerido: `gh workflow run external_links.yml`



### Push triggers (repo público - control estricto)### Health Dashboard (`health-dashboard.yml`)



**Workflows que se disparan en `push` a `main`:**- **Propósito:** Genera el dashboard de salud general del sitio.

- ✅ `lighthouse.yml` (auditoría rendimiento)- **Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)

- ✅ `seo_audit.yml` (validación meta tags)- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- ✅ `smoke-tests.yml` (health check URLs)- **Sección DTC relacionada:** Monitoreo Técnico

- ✅ `ci_status_probe.yml` (status simple)

Comando sugerido: `gh workflow run health-dashboard.yml`

**Regla:** Solo workflows **ligeros** (< 5 min) o **críticos** (Lighthouse) en push.

### Hub Aggregation (`hub-aggregation.yml`)

### Schedule triggers (cron)

- **Propósito:** Agrega métricas desde servicios externos para informes consolidados.

**Daily (madrugada UTC):**- **Disparadores:** schedule(cron:*/10 * * * *), workflow_dispatch()

- 03:15 - `psi_metrics.yml` (PSI API - rate limited)- **Sección DTC relacionada:** Integraciones Externas

- 03:17 - `seo_audit.yml` (backup diario si no hubo push)

- 04:00 - `health-dashboard.yml`Comando sugerido: `gh workflow run hub-aggregation.yml`

- 04:30 - `lighthouse_docs.yml`

### Lighthouse Mobile Audit (`lighthouse.yml`)

**Weekly:**

- Domingo 02:00 - `weekly-audit.yml` (auditoría exhaustiva)- **Propósito:** Ejecuta auditorías Lighthouse en producción.

- **Disparadores:** workflow_dispatch, push(branches:['main'])

**Every 6h:**- **Artefactos clave:** lighthouse_reports

- `hub-aggregation.yml` (status report)- **Secrets requeridos:** GITHUB_TOKEN

- **Sección DTC relacionada:** Fase 4 – SEO/Performance

### Concurrency configuration

Comando sugerido: `gh workflow run lighthouse.yml`

**Implementada en:**

```yaml### Lighthouse CLI Batch (`lighthouse_cli.yml`)

# lighthouse.yml

concurrency:- **Propósito:** Corre Lighthouse desde CLI para smoke tests rápidos.

  group: lighthouse-${{ github.ref }}- **Disparadores:** workflow_dispatch, schedule(cron:0 3 * * *)

  cancel-in-progress: true  # Cancela run previo si nueva ejecución se dispara- **Artefactos clave:** lighthouse-reports-${{ github.run_id }}

- **Sección DTC relacionada:** Fase 4 – SEO/Performance

# seo_audit.yml

concurrency:Comando sugerido: `gh workflow run lighthouse_cli.yml`

  group: seo-audit-${{ github.ref }}

  cancel-in-progress: true### Lighthouse Mobile + Docs (`lighthouse_docs.yml`)



# weekly-audit.yml- **Propósito:** Genera informes Lighthouse en formato HTML y los publica en docs/.

concurrency:- **Disparadores:** workflow_dispatch(inputs:{'urls_file': {'description': 'Ruta del archivo con URLs', 'required': False, 'default': 'scripts/urls_lighthouse.txt'}}), schedule(cron:0 13 * * 1)

  group: weekly-audit- **Inputs `workflow_dispatch`:** urls_file(default=scripts/urls_lighthouse.txt)

  cancel-in-progress: false  # NO cancela audit en curso (puede durar 15 min)- **Artefactos clave:** lhci_raw, reports_after, lh_fail

- **Secrets requeridos:** PSI_API_KEY

# psi_metrics.yml- **Sección DTC relacionada:** Fase 4 – SEO/Performance

concurrency:

  group: psi-metrics-${{ github.ref }}Comando sugerido: `gh workflow run lighthouse_docs.yml`

  cancel-in-progress: true

### Prune Old Workflow Runs (`prune-runs.yml`)

# content-sync.yml

concurrency:- **Propósito:** Limpia ejecuciones antiguas de GitHub Actions para reducir ruido.

  group: content-sync-main- **Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre (name) del workflow a podar (ej: Content Sync). Vacío = todos.', 'required': False, 'default': ''}, 'keep': {'description': 'Número de ejecuciones más recientes a conservar', 'required': True, 'default': '10'}, 'dry_run': {'description': 'true = solo mostrar qué se borraría, false = borrar de verdad', 'required': False, 'default': 'true'}})

  cancel-in-progress: false  # NO cancela sync en curso (datos críticos)- **Inputs `workflow_dispatch`:** workflow(default=), keep(default=10), dry_run(default=true)

```- **Artefactos clave:** prune-runs-output

- **Secrets requeridos:** GITHUB_TOKEN

**Beneficio:** Evita múltiples Lighthouse/SEO audits concurrentes si se hacen varios pushes rápidos.- **Sección DTC relacionada:** Gobernanza y Auditorías



---Comando sugerido: `gh workflow run prune-runs.yml`



## Control de costos (repo público)### PSI Metrics (`psi_metrics.yml`)



### Minutos ilimitados vs derroche- **Propósito:** Consulta PageSpeed Insights y guarda métricas históricas.

- **Disparadores:** workflow_dispatch, schedule(cron:15 3 * * *)

**Con repositorio público:**- **Artefactos clave:** psi-run

- ✅ **Minutos ilimitados** en runners Linux (ubuntu-latest)- **Secrets requeridos:** GITHUB_TOKEN, PSI_API_KEY

- ⚠️ Pero **no es excusa para derroche** - ejecutar Lighthouse en cada push pequeño es innecesario- **Sección DTC relacionada:** Fase 4 – SEO/Performance



**Estrategia de control:**Comando sugerido: `gh workflow run psi_metrics.yml`

1. **Concurrency:** Cancela runs previos si se dispara nuevo (evita backlog)

2. **Triggers selectivos:** Workflows pesados solo en `main` (no en PRs)### Publish Prod Menu (`publish-prod-menu.yml`)

3. **Monitoring:** Revisar Actions tab periódicamente - si hay > 5 Lighthouse runs en 1 hora, investigar

- **Propósito:** Aplica cambios de menús en producción.

**Comando de monitoring:**- **Disparadores:** workflow_dispatch()

```bash- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

gh run list --workflow=lighthouse.yml --limit=20 --json createdAt,conclusion,databaseId- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

```

Comando sugerido: `gh workflow run publish-prod-menu.yml`

**Alerta si:** > 10 Lighthouse runs/día en días sin releases.

### Publish Prod Page (`publish-prod-page.yml`)

---

- **Propósito:** Publica páginas en producción (ES/EN).

## Workflows críticos- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod_page.flag']), workflow_dispatch

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

### 1. Lighthouse Audit (lighthouse.yml)- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe



**Criticidad:** 🔴 ALTA - Define si cumplimos thresholds de Core Web VitalsComando sugerido: `gh workflow run publish-prod-page.yml`



**Thresholds aplicados:**### Publish Prod Post (`publish-prod-post.yml`)

- Mobile: Performance ≥88, LCP ≤2600ms, CLS ≤0.12

- Desktop: Performance ≥92, LCP ≤2000ms, CLS ≤0.06- **Propósito:** Publica posts en producción (ES/EN).

- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_prod.flag']), workflow_dispatch

**URLs auditadas:** 10 páginas (ES/EN: home, about, projects, resources, contact)- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

**Artifacts generados:**

- `lighthouse_reports/` - HTML + JSON por cada URLComando sugerido: `gh workflow run publish-prod-post.yml`

- `assert_summary.txt` - "=== Lighthouse assert: OK ===" si pasa

### Publish Test Menu (`publish-test-menu.yml`)

**Steps críticos:**

- Step 9: **Assert Lighthouse thresholds** (Python script `scripts/ci/assert_lh.py`)- **Propósito:** Publica menús en entorno de prueba.

- Step 15: Commit updated reports (si hay cambios en reports/)- **Disparadores:** workflow_dispatch()

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

**Failure modes:**- **Sección DTC relacionada:** QA y Auditoría Continua

- Assert step failure → workflow conclusion: failure → bloquea merge si está como required check

- Chrome setup failure → revisar Actions system status (GitHub status page)Comando sugerido: `gh workflow run publish-test-menu.yml`



**Runbook si falla:**### Publish Test Page (`publish-test-page.yml`)

1. Verificar que pepecapiro.com responde (curl https://pepecapiro.com)

2. Verificar logs de "Run Lighthouse (mobile)" - buscar timeouts o HTTP 5xx- **Propósito:** Publica páginas en entorno de prueba.

3. Si assert falla: revisar qué URL falló y qué métrica (`scripts/ci/assert_lh.py` imprime detalles)- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_page.flag']), workflow_dispatch

4. Si es regresión de performance: investigar cambios en theme desde último pass- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- **Sección DTC relacionada:** QA y Auditoría Continua

**Manual dispatch:**

```bashComando sugerido: `gh workflow run publish-test-page.yml`

gh workflow run lighthouse.yml

```### Publish Test Post (`publish-test-post.yml`)



---- **Propósito:** Publica posts en entorno de prueba.

- **Disparadores:** push(branches:['main']; paths:['.github/auto/publish_test_post.flag']), workflow_dispatch

### 2. PSI Metrics (psi_metrics.yml)- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- **Sección DTC relacionada:** QA y Auditoría Continua

**Criticidad:** 🟡 MEDIA - Usa cuota PSI API (100 requests/día gratis)

Comando sugerido: `gh workflow run publish-test-post.yml`

**Secret requerido:** `PSI_API_KEY` (Google Cloud API key)

### Build Theme Release (`release.yml`)

**Schedule:** Diario 03:15 UTC

- **Propósito:** Genera releases versionadas con artefactos finales.

**Rate limits:**- **Disparadores:** push(tags:['v*'])

- 100 requests/día (con key gratuita)- **Sección DTC relacionada:** Operaciones / Releases

- Script audita ~10-15 URLs × 2 strategies (mobile+desktop) = ~25 requests/run

Comando sugerido: `gh workflow run release.yml`

**Failure modes:**

- HTTP 429 → cuota PSI excedida → esperar 24h### Rollback pepecapiro theme (`rollback.yml`)

- Secret no configurado → error de autenticación → verificar GitHub Secrets

- **Propósito:** Revierte un deployment de emergencia.

**Runbook si falla:**- **Disparadores:** workflow_dispatch(inputs:{'zip_url': {'description': 'URL del zip artefacto (o sube el archivo en este run)', 'required': False}})

1. Verificar cuota PSI: `curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://pepecapiro.com&key=$PSI_API_KEY"`- **Inputs `workflow_dispatch`:** zip_url(default=None)

2. Si 429: reducir URLs auditadas en `scripts/collect_psi.py`- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER

3. Si secret issue: re-create PSI_API_KEY en Google Cloud Console- **Sección DTC relacionada:** Operaciones / Releases



---Comando sugerido: `gh workflow run rollback.yml`



### 3. Content Sync (content-sync.yml)### Rotate Application Password (`rotate-app-password.yml`)



**Criticidad:** 🔴 ALTA - Sincroniza contenido MD → WordPress- **Propósito:** Asiste en la rotación del Application Password de WordPress.

- **Disparadores:** workflow_dispatch()

**Secret requerido:** `WP_APP_PASSWORD` (Application Password de WordPress)- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- **Sección DTC relacionada:** Seguridad y Accesos

**Trigger:** Solo manual (`workflow_dispatch`) - NUNCA automático (evita sobrescribir contenido en producción)

Comando sugerido: `gh workflow run rotate-app-password.yml`

**Input requerido:** `apply_changes` (true/false) - por defecto `false` (dry-run)

### Run Repair (`run-repair.yml`)

**Concurrency:** `cancel-in-progress: false` - NO cancelar sync en curso (puede corromper datos)

- **Propósito:** Reaplica contenido/ajustes para reparar drift detectado.

**Runbook si falla:**- **Disparadores:** workflow_dispatch(inputs:{'area': {'description': 'Área a reparar', 'type': 'choice', 'required': True, 'options': ['home', 'menus', 'media', 'settings']}, 'mode': {'description': 'Modo (plan/apply)', 'type': 'choice', 'required': False, 'default': 'apply', 'options': ['plan', 'apply']}})

1. Verificar WP_APP_PASSWORD válido: `curl -u "copilot_deploy:$WP_APP_PASSWORD" https://pepecapiro.com/wp-json/wp/v2/pages`- **Inputs `workflow_dispatch`:** area(default=None), mode(default=apply)

2. Si 401: regenerar Application Password en WordPress admin- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

3. Si sync parcial: revisar logs de script - identifica qué páginas/posts fallaron- **Sección DTC relacionada:** Gobernanza y Auditorías



**Manual dispatch (dry-run):**Comando sugerido: `gh workflow run run-repair.yml`

```bash

gh workflow run content-sync.yml --field apply_changes=false### Workflow Runs Summary (`runs-summary.yml`)

```

- **Propósito:** Resume ejecuciones recientes y publica un reporte.

---- **Disparadores:** workflow_dispatch(inputs:{'workflow': {'description': 'Nombre del workflow a filtrar (vacío = todos)', 'required': False, 'default': ''}, 'limit': {'description': 'Número máximo de runs listados por workflow', 'required': True, 'default': '40'}})

- **Inputs `workflow_dispatch`:** workflow(default=), limit(default=40)

## Reglas de operación- **Artefactos clave:** workflow-runs-summary

- **Secrets requeridos:** GITHUB_TOKEN

### 1. NO disparar workflows pesados en cada commit- **Sección DTC relacionada:** Gobernanza y Auditorías



**Anti-patrón:**Comando sugerido: `gh workflow run runs-summary.yml`

```bash

git commit -m "typo fix"### seo_audit (`seo_audit.yml`)

git push  # Dispara Lighthouse (8 min) + SEO Audit + Smoke Tests

```- **Propósito:** Auditoría SEO técnica (hreflang, canonical, schema, etc.).

- **Disparadores:** workflow_dispatch(), schedule(cron:17 3 * * *), push(branches:['main'])

**Patrón correcto:**- **Artefactos clave:** seo-audit

- Commits pequeños (typos, docs): OK push (workflows se disparan pero concurrency cancela previos si son rápidos)- **Sección DTC relacionada:** Fase 4 – SEO/Performance

- Cambios de theme/performance: Esperar a tener batch de commits, luego push

- Verificación manual: Usar `workflow_dispatch` en vez de pushComando sugerido: `gh workflow run seo_audit.yml`



### 2. Workflows de deploy/sync: SOLO manual### Set Home Page (`set-home.yml`)



**NUNCA automatizar:**- **Propósito:** Configura la página inicial del sitio.

- `deploy.yml` (deploy a producción)- **Disparadores:** workflow_dispatch(inputs:{'page_id_es': {'description': 'ID de la página ES a fijar como Home (opcional)', 'required': False}, 'page_slug_es': {'description': 'Slug de la página ES a fijar como Home (opcional)', 'required': False}, 'page_id_en': {'description': 'ID de la página EN a vincular (opcional)', 'required': False}, 'page_slug_en': {'description': 'Slug de la página EN a vincular (opcional)', 'required': False}})

- `content-sync.yml` (sobrescribe contenido WP)- **Inputs `workflow_dispatch`:** page_id_es(default=None), page_slug_es(default=None), page_id_en(default=None), page_slug_en(default=None)

- `site-settings.yml` (cambia configuración WP)- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- `publish-test-post.yml` (publica posts)- **Sección DTC relacionada:** Operaciones / Releases



**Razón:** Protección contra deploys accidentales o corrupción de datos.Comando sugerido: `gh workflow run set-home.yml`



### 3. Monitoring de forks (repo público)### Site Health & Auto-Remediation (`site-health.yml`)



**Verificar periódicamente:**- **Propósito:** Ejecuta el informe de salud del sitio desde WP.

```bash- **Disparadores:** schedule(cron:*/30 * * * *), workflow_dispatch

gh api /repos/ppkapiro/pepecapiro-wp-theme/forks --jq '.[] | {owner: .owner.login, created: .created_at}'- **Secrets requeridos:** PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER

```- **Sección DTC relacionada:** Monitoreo Técnico



**Alerta si:** Forks sospechosos (cuentas bot, nombres aleatorios, creados masivamente).Comando sugerido: `gh workflow run site-health.yml`



**Acción:** Revisar si el fork intenta ejecutar workflows maliciosos (GitHub Actions run on forks but can't access secrets by default).### Site Settings (`site-settings.yml`)



### 4. Secret scanning activo- **Propósito:** Sincroniza configuraciones clave del sitio.

- **Disparadores:** workflow_dispatch()

**GitHub Security Features habilitadas:**- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- [x] Secret scanning alerts- **Sección DTC relacionada:** Operaciones / Releases

- [x] Dependabot security updates

- [ ] CodeQL (opcional - consume más minutos)Comando sugerido: `gh workflow run site-settings.yml`



**Verificar mensualmente:**### Smoke Tests (`smoke-tests.yml`)

```bash

gh api /repos/ppkapiro/pepecapiro-wp-theme/security-advisories- **Propósito:** Ejecución de smoke tests end-to-end.

```- **Disparadores:** push(branches:['main']), workflow_dispatch()

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

---- **Sección DTC relacionada:** QA y Auditoría Continua



## TroubleshootingComando sugerido: `gh workflow run smoke-tests.yml`



### Workflow falla con "conclusion: failure" pero 0 steps ejecutados### CI Status Probe (`status.yml`)



**Síntoma:** Run muestra 4-5 segundos de duración, array de steps vacío.- **Propósito:** Actualiza public/status.json con métricas actuales.

- **Disparadores:** workflow_dispatch, push

**Causa probable:**- **Sección DTC relacionada:** Monitoreo Técnico

- Runner no disponible (GitHub infrastructure issue)

- Billing issue (si repo vuelve a ser privado y se agotan minutos)Comando sugerido: `gh workflow run status.yml`



**Solución:**### UI Visual Gates (`ui-gates.yml`)

1. Verificar GitHub Status: https://www.githubstatus.com/

2. Verificar repo visibility: `gh repo view --json isPrivate`- **Propósito:** Workflow sin descripción específica (añadir en WORKFLOW_DESCRIPTIONS).

3. Si repo privado: verificar Actions minutes remaining en Settings > Billing- **Disparadores:** workflow_dispatch, push(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py', '.github/workflows/ui-gates.yml']), pull_request(branches:['main']; paths:['pepecapiro/**/*.css', 'scripts/ci/check_css_tokens.py'])

- **Sección DTC relacionada:** Operaciones Generales

---

Comando sugerido: `gh workflow run ui-gates.yml`

### Lighthouse falla en "Assert Lighthouse thresholds"

### Upload Media (`upload-media.yml`)

**Síntoma:** Step 9 (Assert) muestra `exit code 1`, workflow conclusion: failure.

- **Propósito:** Sincroniza assets multimedia optimizados.

**Causa:** Una o más URLs no cumplen thresholds (Performance, LCP, CLS).- **Disparadores:** workflow_dispatch()

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

**Diagnóstico:**- **Sección DTC relacionada:** Fase 1 – Contenido Bilingüe

1. Descargar artifact `lighthouse_reports`:

   ```bashComando sugerido: `gh workflow run upload-media.yml`

   gh run download <run_id> --name lighthouse_reports

   ```### Verify Home (`verify-home.yml`)

2. Revisar `assert_summary.txt` - si dice "FAIL", leer detalles

3. Buscar JSON reports de URLs fallidas (e.g., `en-home.json`)- **Propósito:** Smoke test para la portada (contenido + links).

4. Verificar métricas específicas en JSON: `audits.metrics.details.items[0].largestContentfulPaint`- **Disparadores:** workflow_dispatch(), schedule(cron:0 */6 * * *)

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

**Fix:**- **Sección DTC relacionada:** QA y Auditoría Continua

- Si LCP alto: optimizar imágenes, preload fonts, mejorar TTFB

- Si CLS alto: agregar `min-height` a elementos dinámicos, usar `contain:layout`Comando sugerido: `gh workflow run verify-home.yml`

- Si Performance bajo: reducir JS/CSS, habilitar cache, comprimir assets

### Verify Media (`verify-media.yml`)

**Bypass temporal (NO recomendado en producción):**

```yaml- **Propósito:** Verifica assets y referencias multimedia.

# lighthouse.yml - Step Assert- **Disparadores:** workflow_dispatch(), schedule(cron:0 3 * * *)

continue-on-error: true  # Workflow pasa aunque assert falle- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

```- **Sección DTC relacionada:** QA y Auditoría Continua



---Comando sugerido: `gh workflow run verify-media.yml`



### PSI Metrics falla con HTTP 429### Verify Menus (`verify-menus.yml`)



**Síntoma:** Script `collect_psi.py` imprime "Error: HTTP 429 Too Many Requests".- **Propósito:** Comprueba consistencia de menús.

- **Disparadores:** workflow_dispatch(), schedule(cron:0 */12 * * *)

**Causa:** Cuota PSI API excedida (100 requests/día gratuitos).- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

- **Sección DTC relacionada:** QA y Auditoría Continua

**Solución:**

1. Verificar cuota actual en Google Cloud Console > APIs & Services > PageSpeed Insights APIComando sugerido: `gh workflow run verify-menus.yml`

2. Reducir URLs auditadas en `scripts/collect_psi.py` (comentar URLs no críticas)

3. Esperar 24h para reset de cuota### Verify Settings (`verify-settings.yml`)

4. Opción: Upgrade a plan de pago PSI (si se necesita más cuota)

- **Propósito:** Valida settings críticos en WP.

---- **Disparadores:** workflow_dispatch(), schedule(cron:0 0 * * *)

- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

### Content Sync falla con 401 Unauthorized- **Sección DTC relacionada:** QA y Auditoría Continua



**Síntoma:** Script imprime "Error: 401 Client Error: Unauthorized for url".Comando sugerido: `gh workflow run verify-settings.yml`



**Causa:** `WP_APP_PASSWORD` secret inválido o expirado.### Webhook GitHub to WordPress (`webhook-github-to-wp.yml`)



**Solución:**- **Propósito:** Entrega webhook hacia WordPress para acciones remotas.

1. Verificar secret en GitHub: Settings > Secrets > Actions > WP_APP_PASSWORD- **Disparadores:** push(branches:['main']; paths:['content/**']), release(types:['published']), workflow_dispatch(inputs:{'sync_type': {'description': 'Tipo de sincronización', 'required': True, 'type': 'choice', 'options': ['content', 'menus', 'media']}})

2. Regenerar Application Password en WordPress:- **Inputs `workflow_dispatch`:** sync_type(default=None)

   - Login en pepecapiro.com/wp-admin- **Secrets requeridos:** WP_APP_PASSWORD, WP_URL, WP_USER

   - Users > Profile > Application Passwords- **Sección DTC relacionada:** Integraciones Externas

   - Crear nuevo con nombre "GitHub Actions CI/CD"

   - Copiar password (formato: `xxxx xxxx xxxx xxxx xxxx xxxx`)Comando sugerido: `gh workflow run webhook-github-to-wp.yml`

   - Actualizar secret en GitHub (sin espacios)

3. Re-run workflow### Weekly Audit (`weekly-audit.yml`)



---- **Propósito:** Auditoría semanal de drift y disparo de verificaciones clave.

- **Disparadores:** workflow_dispatch(), schedule(cron:0 2 * * 0)

### Artifacts no se generan- **Sección DTC relacionada:** Gobernanza y Auditorías



**Síntoma:** Workflow pasa pero "Upload artifact" step muestra "No files to upload".Comando sugerido: `gh workflow run weekly-audit.yml`


**Causa:** Script de generación de reports falló silenciosamente (exit code 0 pero no creó archivos).

**Diagnóstico:**
1. Revisar logs del step previo (e.g., "Run Lighthouse (mobile)")
2. Buscar errores de Chrome/Node.js
3. Verificar que directorio `lighthouse_reports/` existe

**Fix:** Agregar validación en workflow:
```yaml
- name: Verify reports generated
  run: |
    if [ ! -d "lighthouse_reports" ] || [ -z "$(ls -A lighthouse_reports)" ]; then
      echo "Error: No reports generated"
      exit 1
    fi
```

---

## Anexo: Comandos útiles

### Listar últimos 10 runs de Lighthouse
```bash
gh run list --workflow=lighthouse.yml --limit=10
```

### Ver logs de run específico
```bash
gh run view <run_id> --log
```

### Descargar artifacts de run
```bash
gh run download <run_id> --name lighthouse_reports --dir /tmp/lh_artifacts
```

### Disparar workflow manualmente
```bash
gh workflow run lighthouse.yml
```

### Verificar estado de workflows
```bash
gh run list --status=in_progress
```

### Cancelar run en progreso
```bash
gh run cancel <run_id>
```

---

**Mantenido por:** Copilot (agente autónomo)  
**Última revisión:** 2025-10-28 (post-conversión a repo público)  
**Versión anterior:** docs/RUNBOOK_CI_OLD_20251028_142641.md
