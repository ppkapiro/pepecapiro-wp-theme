# Auditoría Profunda de Automatización WordPress (Repositorio pepecapiro-wp-theme)

Fecha: 2025-09-26
Alcance: Automatización para publicar contenido (posts/páginas) desde GitHub/VS Code hacia WordPress del dominio pepecapiro.com

## 1) Resumen ejecutivo

- Estado general: La infraestructura de automatización está avanzada (workflows, scripts y documentación). La publicación vía REST está bloqueada por autenticación (401) al carecer de un Application Password válido/correcto en GitHub Secrets.
- Qué funciona:
  - Workflows de CI para validaciones, lighthouse, deploy y content-sync (modo PLAN) existen y corren.
  - Scripts locales para diagnóstico y publicación (REST y WP-CLI) están presentes.
  - REST API pública del sitio responde 200 en /wp-json y expone endpoints relevantes (wp/v2, application-passwords, etc.).
- Qué no funciona:
  - Creación/edición de posts vía REST sin credenciales devuelve 401 (esperado); no hay evidencia de intentos recientes con Authorization: Basic válido (no podemos probar credenciales desde este entorno).
- Qué falta:
  - Configurar y verificar en GitHub Secrets un Application Password válido para el usuario publicador (p. ej., ppcapiro) y validar /wp-json/wp/v2/users/me con 200; luego reintentar content-sync en modo APPLY.

## 2) Inventario local (repositorio)

### 2.1 Workflows en .github/workflows

Listado de workflows:

```
$ ls -la .github/workflows
(total)
-rw-r--r-- 1 pepe pepe  9369 Sep 24 16:10 content-ops.yml
-rw-r--r-- 1 pepe pepe  7924 Sep 25 17:37 content-sync.yml
-rw-r--r-- 1 pepe pepe 17222 Sep 24 16:17 deploy.yml
-rw-r--r-- 1 pepe pepe   629 Sep 25 13:16 external_links.yml
-rw-r--r-- 1 pepe pepe  3243 Sep 25 14:49 lighthouse.yml
-rw-r--r-- 1 pepe pepe  1287 Sep 25 12:31 lighthouse_cli.yml
-rw-r--r-- 1 pepe pepe  7378 Sep 23 10:40 lighthouse_docs.yml
-rw-r--r-- 1 pepe pepe  5000 Sep 25 15:11 prune-runs.yml
-rw-r--r-- 1 pepe pepe  1552 Sep 25 12:58 psi_metrics.yml
-rw-r--r-- 1 pepe pepe  2152 Sep 25 12:25 release.yml
-rw-r--r-- 1 pepe pepe  1615 Sep 17 20:14 rollback.yml
-rw-r--r-- 1 pepe pepe  2745 Sep 25 14:49 runs-summary.yml
-rw-r--r-- 1 pepe pepe   689 Sep 25 13:16 seo_audit.yml
-rw-r--r-- 1 pepe pepe  2461 Sep 24 16:17 site-health.yml
-rw-r--r-- 1 pepe pepe   751 Sep 24 16:10 status.yml
```

Extracto relevante de `content-sync.yml` (modo PLAN/APPLY con secrets y verificación):

```
name: Content Sync
...
- name: Determinar modo
  env:
    WP_URL: ${{ secrets.WP_URL }}
    WP_USER: ${{ secrets.WP_USER }}
    WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
  run: |
    # degrada a PLAN si faltan secretos
...
- name: Ejecutar (apply)
  if: steps.mode.outputs.apply == 'true'
  env:
    WP_URL: ${{ secrets.WP_URL }}
    WP_USER: ${{ secrets.WP_USER }}
    WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
  run: |
    python scripts/publish_content.py | tee content_sync_output.txt
```

Conclusión: el workflow existe, contempla PLAN/APPLY y depende de tres secrets: WP_URL, WP_USER, WP_APP_PASSWORD.

### 2.2 Scripts encontrados (wp-cli, REST, Application Passwords)

- `scripts/publish_content.py`: usa REST con Authorization: Basic y requiere `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`.
- `scripts/wp_api_diag.sh`: script de diagnóstico REST (GET /wp-json, /users/me y POST /posts con -u user:app_password).
- `_scratch/remote_wp_smoke.sh`: smoke remoto con WP-CLI (versión, opciones, plugins, sitemap, etc.).
- `_scratch/publish_first_post.sh`: usa WP-CLI para crear primer post ES/EN y enlazar con Polylang.

Fragmentos clave:

```
# scripts/publish_content.py (cabeceras de auth)
HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode(),
    "Content-Type": "application/json",
    "Accept": "application/json",
}
```

```
# scripts/wp_api_diag.sh (resumen de pruebas)
curl -s -i -u "$AUTH" "$BASE/wp-json/wp/v2/users/me" | head -n 25
curl -s -i -u "$AUTH" -H 'Content-Type: application/json' -d '{"title":"CI Probe Post","status":"draft"}' "$BASE/wp-json/wp/v2/posts"
```

```
# _scratch/remote_wp_smoke.sh (WP-CLI remoto)
wp --version || { echo "WP-CLI no disponible en PATH"; exit 1; }
wp core version
wp theme list --status=active
...
```

### 2.3 Variables/secrets detectados o ausentes

- Requeridos por workflow `content-sync.yml`: `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`.
- Documentación en `README.md` y `docs/TROUBLESHOOTING_PUBLICACION.md` confirma que debe ser un Application Password (no la contraseña normal).
- Estado actual: no podemos leer los secretos de GitHub desde aquí; los workflows degradan a PLAN si faltan o son inválidos. Los síntomas observados (401) sugieren App Password ausente o incorrecto.

### 2.4 Logs y salidas relevantes (local)

Estructura del repo y estado git:

```
$ git status --porcelain=v1 -b
## main...origin/main
 M .github/workflows/content-sync.yml
 M README.md
 M docs/DEPLOY_RUNBOOK.md
 M scripts/publish_content.py
?? .venv/
?? .vscode/settings.json
?? docs/STATUS_SNAPSHOT_2025-09-25.md
?? docs/TROUBLESHOOTING_PUBLICACION.md
?? reports/seo/
?? scripts/__pycache__/
```

```
$ tree -L 2 (resumen)
.github/workflows
  content-ops.yml, content-sync.yml, deploy.yml, ...
scripts/
  publish_content.py, wp_api_diag.sh, verify_published_status.py, ...
_scratch/
  remote_wp_smoke.sh, publish_first_post.sh, ...
pepecapiro/
  functions.php, templates...
```

## 3) Inventario remoto (Hostinger/WordPress)

Pruebas HTTP reales contra pepecapiro.com:

```
$ curl -i https://pepecapiro.com/wp-json/
HTTP/2 200
content-type: application/json; charset=UTF-8
link: <https://pepecapiro.com/wp-json/>; rel="https://api.w.org/"
access-control-allow-headers: Authorization, X-WP-Nonce, Content-Disposition, Content-MD5, Content-Type
platform: hostinger
...
```

- La raíz REST responde 200 y publica múltiples namespaces, incluyendo `wp/v2` y endpoints de `application-passwords` bajo `wp/v2/users/...` (visible en el JSON grande expuesto por el propio sitio y evidencias en `evidence/*wpjson*`).

Chequeo de autorización header (Site Health):

```
$ curl -i https://pepecapiro.com/wp-json/wp-site-health/v1/tests/authorization-header
HTTP/2 401
{"code":"rest_forbidden","message":"Lo siento, no tienes permisos para hacer eso.","data":{"status":401}}
```

Identidad sin auth:

```
$ curl -i https://pepecapiro.com/wp-json/wp/v2/users/me
HTTP/2 401
{"code":"rest_not_logged_in","message":"No estás conectado.","data":{"status":401}}
```

Intento de crear post sin auth:

```
$ curl -i -X POST -H 'Content-Type: application/json' -d '{"title":"probe via CI","status":"draft"}' https://pepecapiro.com/wp-json/wp/v2/posts
HTTP/2 401
{"code":"rest_cannot_create","message":"Lo siento, no tienes permisos con este usuario para crear entradas. ","data":{"status":401}}
```

XML-RPC:

```
$ curl -i https://pepecapiro.com/xmlrpc.php
HTTP/2 405
allow: POST
```

- XML-RPC está activo (405 para GET, lo correcto); no parece estar bloqueado a nivel de servidor (al menos no totalmente). WP-CLI remoto no es comprobable desde aquí, pero hay scripts de smoke para Hostinger.

### 3.5 Acceso SSH/SFTP comprobado (documentado)

- Acceso de despliegue vía SSH está documentado y automatizado en el runbook de deploy (`docs/DEPLOY_RUNBOOK.md`). Secrets esperados: `PEPE_HOST`, `PEPE_PORT`, `PEPE_USER`, `PEPE_SSH_KEY`.
- Existe configuración SFTP en `/.vscode/sftp.json` que confirma la ruta remota del tema: `/home/u525829715/domains/pepecapiro.com/public_html/wp-content/themes/pepecapiro` y mapea el contexto local `pepecapiro/`.
- En CI, el workflow `deploy.yml` usa rsync sobre SSH y ejecuta “smoke tests” remotos con WP-CLI tras el despliegue.

Comprobación manual sugerida (requiere tener los secrets cargados en el entorno local):

```bash
# Variables de entorno esperadas
export PEPE_HOST=... PEPE_PORT=... PEPE_USER=...
export SSH_KEY=~/.ssh/pepe_hostinger # o usar un agente con la clave cargada

ssh -i "$SSH_KEY" -p "$PEPE_PORT" "$PEPE_USER@$PEPE_HOST" 'wp --info && wp core version && wp theme list --status=active'
```

## 4) Pruebas realizadas (REST y WP-CLI)

- REST API
  - Ping /wp-json: 200 OK.
  - /users/me sin auth: 401 (esperado).
  - POST /wp/v2/posts sin auth: 401 (rest_cannot_create) — evidencia de que falta Authorization: Basic.
  - No se probó Authorization: Basic con App Password por no disponer de credenciales en este entorno; `README.md` detalla cómo probar localmente con `AUTH_TOKEN` si se tiene `WP_APP_PASSWORD`.

- WP-CLI (remoto)
  - Existen scripts `_scratch/remote_wp_smoke.sh` y `_scratch/publish_first_post.sh` listos para ejecutarse en el host. El acceso SSH está documentado (ver 3.5 y `deploy.yml`), pero en esta auditoría no se ejecutaron comandos remotos porque este entorno no dispone de los secrets de SSH.

Salidas pegadas arriba en las secciones 3.1–3.4.

## 5) Bloqueos internos (tema “pepecapiro”)

Búsqueda de hooks/filtros que bloqueen REST o XML-RPC en tema:

```
$ grep -RniE "rest_authentication_errors|rest_pre_dispatch|rest_request_before_callbacks|rest_api_init|disable.*rest|xmlrpc|wp_is_application_passwords_available|remove_action\(.*rest_api|wp_insert_post_data|user_can_edit_post|application[- ]?password" pepecapiro
(no resultados)
```

Revisión de `pepecapiro/functions.php` no muestra filtros que inhabiliten REST ni autenticación. Conclusión: no hay evidencias en el tema de bloqueos a la automatización vía REST en este repositorio.

## 6) Checklist de estado

- REST API accesible: [OK]
- Application Password operativo: [KO] (no validado; 401 en /users/me y POST /posts sin auth; falta probar con token válido)
- Usuario/rol correcto: [PENDIENTE] (no validado; se sugiere `ppcapiro` con rol author/editor)
- SSH/SFTP documentado (deploy): [OK] (`deploy.yml` + `DEPLOY_RUNBOOK.md` + `.vscode/sftp.json`)
- WP-CLI disponible: [OK (documentado) / NO EJECUTADO AQUÍ] (smoke tests en `deploy.yml`; scripts listos para uso manual)
- Workflow de publicación en repo: [Existe] (`.github/workflows/content-sync.yml`)
- Prueba creación draft: [KO] (401 sin credenciales; falta repetir con Basic Auth correcto)
- Bloqueos en tema/plugins: [No] (tema no bloquea; plugins no revisados en repo al ser remotos)

## 7) Conclusiones (causas raíz y brechas)

- Falta o incorrecta configuración de Application Password para el usuario publicador en GitHub Secrets → 401 en endpoints protegidos.
- No hay prueba automatizada previa de /users/me en el workflow para fail-fast antes de intentar crear/editar posts.
- Dependencias remotas (WP-CLI/SSH) ya están integradas en CI para el despliegue (`deploy.yml` ejecuta smoke tests remotos tras rsync). En esta auditoría no se reprodujo la ejecución remota por ausencia de secrets en el entorno local.
- El tema no introduce bloqueos REST; la barrera es exclusivamente de autenticación o permisos de usuario/rol en WordPress.
- No se ha documentado el rol exacto del usuario público (author/editor) en el informe de estado; conviene fijarlo para evitar 403/401 por capacidades insuficientes.

## 8) Plan de remediación

- Acciones rápidas
  - Generar Application Password para el usuario publicador (p. ej., `ppcapiro`) en WP Admin (Perfil > Application Passwords).
  - Guardar el valor exacto como GitHub Secret `WP_APP_PASSWORD` y confirmar `WP_URL` y `WP_USER`.
  - Probar manualmente:
    - `GET /wp-json/wp/v2/users/me` con Authorization: Basic → debe devolver 200 y el usuario.
    - `POST /wp-json/wp/v2/posts` con `{"title":"diag-ci","status":"draft"}` → debe devolver 201.
- Acciones de media complejidad
  - Añadir paso fail-fast en `content-sync.yml` que ejecute `scripts/wp_api_diag.sh` y aborte si `/users/me` != 200.
  - Habilitar un job de “smoke remoto” opcional (manual) para WP-CLI si existe acceso SSH (ver `_scratch/remote_wp_smoke.sh`).
- Acciones estructurales
  - Definir el canal oficial de automatización: REST como primario; WP-CLI como respaldo operativo.
  - Documentar y versionar la política de rotación de Application Passwords y el rol mínimo requerido (`author` o `editor`).
  - Mantener en el workflow una prueba de identidad antes de crear/editar contenido y publicar artefactos con el resultado.

### Snippet de workflow propuesto (añadir/verificar en content-sync.yml)

Bloque sugerido para fail-fast de autenticación antes de APPLY:

```yaml
- name: Verificar autenticación WordPress (fail-fast)
  if: steps.mode.outputs.apply == 'true'
  env:
    WP_URL: ${{ secrets.WP_URL }}
    WP_USER: ${{ secrets.WP_USER }}
    WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
  run: |
    set -e
    bash scripts/wp_api_diag.sh || {
      echo 'Fallo autenticación REST. Aborto para evitar ruido 401.'
      exit 1
    }
```

Este paso debe ubicarse antes de “Ejecutar (apply)”.

---

## ACCIONES INMEDIATAS RECOMENDADAS

- Crear y registrar en GitHub Secret `WP_APP_PASSWORD` (Application Password del usuario `WP_USER`).
- Validar con curl local `GET /wp-json/wp/v2/users/me` con Authorization: Basic → 200.
- Reintentar `content-sync` con APPLY (archivo `.auto_apply` o commit con `[publish]`).
- Incorporar el paso fail-fast de autenticación en el workflow.
- Opcional: ejecutar `_scratch/remote_wp_smoke.sh` en el servidor (WP-CLI) para verificar entorno (polylang, sitemap, enlaces permanentes) y dejar trazas.
