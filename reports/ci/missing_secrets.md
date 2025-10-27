# Estado de Secrets en Workflows
Generado: 2025-10-27T18:23:11.913405Z

## Secrets por workflow
- `cleanup-test-posts.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `content-ops.yml`: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- `content-sync.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `deploy.yml`: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- `health-dashboard.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `lighthouse.yml`: GITHUB_TOKEN
- `lighthouse_docs.yml`: PSI_API_KEY
- `prune-runs.yml`: GITHUB_TOKEN
- `psi_metrics.yml`: GITHUB_TOKEN, PSI_API_KEY
- `publish-prod-menu.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `publish-prod-page.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `publish-prod-post.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `publish-test-menu.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `publish-test-page.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `publish-test-post.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `rollback.yml`: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- `rotate-app-password.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `run-repair.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `runs-summary.yml`: GITHUB_TOKEN
- `set-home.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `site-health.yml`: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- `site-settings.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `smoke-tests.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `upload-media.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `verify-home.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `verify-media.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `verify-menus.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `verify-settings.yml`: WP_APP_PASSWORD, WP_URL, WP_USER
- `webhook-github-to-wp.yml`: WP_APP_PASSWORD, WP_URL, WP_USER

## Estado por secret
- `GITHUB_TOKEN`: **OK**
- `PEPE_HOST`: **FALTANTE** (nomenclatura no estándar)
- `PEPE_PORT`: **FALTANTE** (nomenclatura no estándar)
- `PEPE_SSH_KEY`: **FALTANTE** (nomenclatura no estándar)
- `PEPE_USER`: **FALTANTE** (nomenclatura no estándar)
- `PSI_API_KEY`: **OK**
- `WP_APP_PASSWORD`: **OK**
- `WP_URL`: **OK**
- `WP_USER`: **OK**

## Secrets estándar no referenciados
- GA_API_SECRET, GA_MEASUREMENT_ID, GSC_API_KEY, GSC_CLIENT_ID, GSC_CLIENT_SECRET, HEALTH_API_TOKEN, LIGHTHOUSE_GH_TOKEN, META_TOKEN, PSI_API_TOKEN, SMTP_PASSWORD, WP_APP_PASSWORD_NEW, WP_DEPLOY_KEY, WP_HOST, WP_PATH, WP_SFTP_PASSWORD, WP_SFTP_USER

## Observaciones
- Secrets no estándar detectados: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- Actualiza la nomenclatura o documenta los nombres de infraestructura cuando aplique.