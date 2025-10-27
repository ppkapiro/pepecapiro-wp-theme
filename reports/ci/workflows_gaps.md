# Brechas entre Workflows y DTC
Generado: 2025-10-27T18:23:11.913405Z

## Workflows sin mención en el DTC
- hub-aggregation.yml
- lighthouse.yml
- lighthouse_cli.yml
- publish-prod-menu.yml
- publish-test-menu.yml
- publish-test-page.yml
- publish-test-post.yml
- release.yml
- rollback.yml
- rotate-app-password.yml
- runs-summary.yml
- set-home.yml
- site-settings.yml
- ui-gates.yml
- verify-settings.yml

## Secciones del DTC sin workflow asignado
- Todas las secciones principales están cubiertas por al menos un workflow.

## Secrets y nomenclatura
- Secrets no estándar en uso: PEPE_HOST, PEPE_PORT, PEPE_SSH_KEY, PEPE_USER
- Secrets estándar aún no referenciados: GA_API_SECRET, GA_MEASUREMENT_ID, GSC_API_KEY, GSC_CLIENT_ID, GSC_CLIENT_SECRET, HEALTH_API_TOKEN, LIGHTHOUSE_GH_TOKEN, META_TOKEN, PSI_API_TOKEN, SMTP_PASSWORD, WP_APP_PASSWORD_NEW, WP_DEPLOY_KEY, WP_HOST, WP_PATH, WP_SFTP_PASSWORD, WP_SFTP_USER