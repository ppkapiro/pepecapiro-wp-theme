# Runbook de Deploy y Remediación

Este runbook describe cómo desplegar el tema `pepecapiro`, verificar integridad y ejecutar una remediación post-deploy para activar el tema, fijar la portada (opcional) y purgar cachés.

## 1) Vía GitHub Actions (recomendada)

- Workflow: `.github/workflows/deploy.yml`
- Disparadores:
  - Tag push `vX.Y.Z` (usa la versión del tag) — RECOMENDADO
  - Manual (workflow_dispatch) con input `version` (ej: `0.3.4`)
- Pasos clave del pipeline:
  - Ajusta `Version:` en `pepecapiro/style.css` a la versión indicada (idempotente)
  - Construye assets si existe `_scratch/build_assets.sh`
  - Despliega por rsync al servidor (SSH) usando ssh-agent
  - Smoke tests remotos (WP-CLI): tema activo, permalinks y purga LiteSpeed
  - Genera y compara manifests (SHA256) con orden determinista (LC_ALL=C + sort)
  - Sube artefacto ZIP + SHA y logs de integridad

Notas:
- Secrets requeridos: `PEPE_HOST`, `PEPE_PORT`, `PEPE_USER`, `PEPE_SSH_KEY` (clave privada PEM, ed25519 recomendado). No usar base64.
- Ruta remota definida en `REMOTE_PATH` (wp-content/themes/pepecapiro).
- Verificación de integridad: falla el job si hay diferencias, salvo que `continue_on_verify_fail=true`.

### Flujo por tags (recomendado)

1. Asegura que `main` tiene los cambios listos.
2. Crea y empuja un tag: `vX.Y.Z` (p.ej., `v0.3.5`).
3. El workflow se ejecuta automáticamente y, si todo va bien, termina en success.

### Workflow de Release Automático (Empaquetado)
Archivo: `.github/workflows/release.yml`

Disparo: cualquier push de tag `vX.Y.Z`.
Acciones:
1. Valida que `style.css` tenga `Version: X.Y.Z`.
2. Verifica que `CHANGELOG.md` marca la versión como (Release).
3. Empaqueta el directorio `pepecapiro/` generando `pepecapiro_<timestamp>_vX.Y.Z.zip`.
4. Calcula checksum SHA256 y lo adjunta.
5. Publica (o actualiza) el Release GitHub con ambos artefactos.

Rollback simplificado: descargar ZIP de un release anterior y redeploy (o re‑tag). No se requiere reconstruir manualmente.

## 2) Post-deploy remediation (opcional)

Script: `scripts/wp_post_deploy_remediate.sh`

- Objetivo: asegurar tema activo, portada estática correcta y purgar caches.
- Uso:
  - Dry-run: `scripts/wp_post_deploy_remediate.sh`
  - Aplicar: `scripts/wp_post_deploy_remediate.sh --apply`
- Requisitos: alias SSH y acceso al puerto configurado.

Acciones:
- `wp theme activate pepecapiro` (si no activo)
- `wp option update show_on_front page; page_on_front=<ID>` al detectar `home`/`inicio`
- `wp cache flush` y `wp litespeed-purge all` (si el plugin está)
- Validaciones simples de HTML (CSS y og:image)

## 3) Artifacts y verificación

- `release-<version>-<TAG>.zip`: ZIP del tema generado por CI.
- `integrity-<mismatches>.zip`: manifests local/remoto normalizados y `integrity_ci.log`.
- Si `mismatches>0`, revisa `integrity_ci.log`. El orden ya está normalizado, así que las diferencias deberían ser reales (archivos faltantes/cambiados).

## 4) Rollback

- Opción rápida: crear tag que apunte al commit estable previo y desplegarlo.
- Alternativa: usar `.github/workflows/rollback.yml` (si está activado) o reinstalar el ZIP anterior por rsync y purgar.

## 5) Lighthouse continuo

- Workflows: `.github/workflows/lighthouse.yml` y `.github/workflows/lighthouse_docs.yml` (si están en el repo).
- Generan reportes en `docs/lighthouse/`.

## 6) Troubleshooting

- Permission denied (publickey): añade la parte pública de `PEPE_SSH_KEY` a `~/.ssh/authorized_keys` del server.
- base64: invalid input: ya no aplica (no usamos base64 en la clave).
- Diffs de integridad: descarga `integrity-*.zip` y revisa el log; si hay 1-2 archivos, confirmar rsync/permisos y regenerados en server.
- LiteSpeed CDN: el workflow purga el plugin; si usas CDN, añade un paso de purga CDN.

## 7) Validaciones post-deploy (públicas)

- HEAD 200: `wp-content/themes/pepecapiro/assets/css/tokens.css`
- Home ES/EN: títulos y `og:image` correctos; héroe visible.

## 8) Listado de Blog Bilingüe (v0.3.10)

Contexto: Se introdujo `page-blog.php` como plantilla dedicada para listar entradas sin depender de `page_for_posts`, aplicando filtrado por idioma (Polylang) y añadiendo un marcador HTML para verificación automatizada.

Detalles clave:

Health check script (local, carpeta `_scratch/`): `blog_health_check.sh`

Integración CI:
  
Script incorporado:

Notas operativas:

## 9) Operación diaria — Automatización WP (Posts)

## Páginas y Home (Automatización)

### Workflows
- `.github/workflows/publish-test-page.yml`: Crea página ES/EN en estado `private` (flag o manual).
- `.github/workflows/publish-prod-page.yml`: Crea página ES/EN en estado `publish` (flag o manual).
- `.github/workflows/set-home.yml`: Fija la última página creada (o por ID/slug) como portada; refleja traducción EN si existe.

### Flags
- `.github/auto/publish_test_page.flag`: dispara test-page.
- `.github/auto/publish_prod_page.flag`: dispara prod-page.

### Cómo disparar
1. Modifica y haz push a uno de los flags para disparar el workflow.
2. Alternativamente, ejecuta manualmente desde Actions → "Run workflow".

### Output esperado
- Job Summary: Auth OK/KO, IDs/links ES/EN, estado, template, traducciones vinculadas Sí/No.
- Para set-home: show_on_front=page, IDs/links ES/EN fijados, best-effort traducción EN.
Workflows clave:
- Publish Test Post: pruebas privadas ES/EN; resumen con Auth, IDs, links, vínculo, categorías.
- Publish Prod Post: publicación real ES/EN con categorías; idempotente por slug; vínculo best‑effort.
- Cleanup Test Posts: cron diario (elimina test antiguos) o manual.

Cómo disparar:
- Flags: editar `.github/auto/publish_test_post.flag` o `.github/auto/publish_prod.flag` y hacer push a `main`.
- Manual: Actions → seleccionar workflow → Run workflow.

Guardarraíles:
- Nunca exponer `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` en commits/logs.
- Validar `/wp-json/wp/v2/users/me` devuelve 200 antes de publicar en prod.
- Revisar el Job Summary: debe listar IDs y links ES/EN; si IDs coinciden, revisar slugs por idioma.
- Rotación de Application Passwords cada 60–90 días (ver `docs/SECURITY_NOTES.md`).

Cómo ver último uso del token (Application Password):
- WP Admin → Users → Profile (del usuario CI) → Application Passwords → columna "Last Used".
