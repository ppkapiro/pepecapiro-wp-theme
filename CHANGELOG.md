## 0.9.0 – 20251021 (Release)
- Hub Central (v0.9.0): `docs/hub/instances.json`, `docs/hub/hub_status.json`, `docs/hub/index.md`.
- Agregación planificada para v0.9.1 y workflow programado para refrescar `hub_status.json`.
- Ver notas: `docs/hub/HUB_OVERVIEW.md` y release https://github.com/ppkapiro/pepecapiro-wp-theme/releases/tag/v0.9.0

## 0.8.0 – 20251021 (Release)
- Export Kit (v0.8.0): `export/EXPORT_MANUAL.md` (480+ líneas), `export/scripts/bootstrap.sh`, manifiestos y plantilla de workflow.
- Dry‑run validado, checklist de compatibilidad y troubleshooting incluidos.
- Ver release: https://github.com/ppkapiro/pepecapiro-wp-theme/releases/tag/v0.8.0

## 0.7.0 – 20251021 (Release)
- API Gateway (v0.7.0): `GET /status` (public/status.json y docs/status.json) y `POST /trigger` (repository_dispatch, auth por token).
- Webhooks bidireccionales: GitHub→WP (workflow) y WP→GitHub (guía).
- Issue #7 (BLOCKER): Falta `API_GATEWAY_TOKEN` (scopes repo+workflow) – documentado con pasos.
- Ver release: https://github.com/ppkapiro/pepecapiro-wp-theme/releases/tag/v0.7.0

## 0.3.20 – 20250926 (Release)
- Cierre de etapa "Publicación Automática WP (Posts)":
	- Workflows consolidados: Publish Test Post (private, ES/EN, vinculación), Publish Prod Post (publish, ES/EN, categorías por idioma, idempotencia por slug), Cleanup Test Posts (cron diario).
	- Flags documentados: `.github/auto/README.flags.md` con instrucciones.
	- Docs nuevas/actualizadas: `README.md` (Automatización WP), `docs/LIENZO_AUTOMATIZACION_WP.md`, `docs/DEPLOY_RUNBOOK.md` (operación diaria), `docs/TROUBLESHOOTING_AUTOMATIZACION.md`, `docs/SECURITY_NOTES.md`, `docs/ROADMAP_AUTOMATIZACION_TOTAL.md`.
	- Release `release.yml` con título/nota de etapa.

## 0.3.19 – 20250926 (Release)
- Workflows WP bilingües:
	- Publish Test Post: publica ES/EN en privado, enlaza traducciones y emite resumen.
	- Publish Prod Post: publica ES/EN en publish con categorías (ES: Blog/Guías; EN: Blog/Guides), idempotencia por slug por idioma y enlace Polylang.
	- Cleanup Test Posts: elimina posts de prueba antiguos diariamente o manual.
- Flags para disparar: `.github/auto/publish_test_post.flag` y `.github/auto/publish_prod.flag`.
- Documentación: `.github/auto/README.flags.md` + sección en README.
- Bump tema a 0.3.19.

## 0.3.18 – 20250925 (Release)
- Modo `--drift-only`: genera `content/drift_report.md` sin realizar mutaciones (comprueba existencia y hash de contenido remoto vs local).
- Resumen de plan en dry-run: crea `content/content_plan_summary.md` listando acciones (create/update/skip/removed).
- Soft delete declarativo: campo `removed: true` en posts/páginas fuerza estado `draft` remoto sin recrear.
- Deduplicación de media: `.media_map.json` (hash SHA256 -> URL remota) evita subidas repetidas de la misma imagen.
- Enlazado de traducciones refactorizado tras creación para posts y páginas (agrupado por `translation_key`).
- Mejora hash drift interno para reportes (título+excerpt+content+status).
- Documentación pendiente de ampliación (se actualizará en este mismo release antes de cerrar la etiqueta).

## 0.3.17 – 20250925 (Release)
- Pages as code: nuevo `content/pages.json` para páginas estáticas (privacidad, cookies, etc.) con misma semántica de `translation_key`, slugs multi‑idioma, status y disabled.
- Publicación unificada posts + páginas en `scripts/publish_content.py` (lógica compartida de hash, creación/actualización y linking Polylang).
- Subida automática de media local: detección de referencias `<img src="media/...">` o `![alt](media/...)`, POST a endpoint `/media` y reemplazo de URLs en HTML final (sólo en apply).
- Parser markdown extendido: soporte de imágenes y blockquotes (`>`).
- Validación de páginas (`scripts/validate_pages.py`) añadida al flujo CI (plan + apply).
- Documentación: consolidación en `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md` (archivo maestro). `CONTENT_AUTOMATION.md` pasa a ser stub.
- Auto-apply condicional: archivo `.auto_apply` o commit con `[publish]` activa apply automático.
- Changelog reorganizado: entrada 0.3.16 se convierte en release anterior; 0.3.17 agrupa nuevas capacidades.

## 0.3.16 – 20250925 (Release)
- Slugs multi‑idioma: `slug` acepta objeto `{es,en}` (retrocompatible con string).
- Campos opcionales `status` (global o por idioma) y `disabled` (bool / dict) en `posts.json`.
- Filtro `--key=lista` para sincronizar sólo ciertos `translation_key`.
- Validación ampliada (`validate_posts.py`) soporta nuevo esquema.
- Hash de idempotencia ahora incluye `status` y categorías para detectar cambios.
- Salto explícito si falta markdown por idioma (`[skip-md]`).
- Documentación `CONTENT_AUTOMATION.md` actualizada (esquema 0.3.16+, subconjuntos, disabled parcial).

## 0.3.15 – 20250925 (Release)
- Pipeline "Contenido como código" consolidado:
	- `content/posts.json` como fuente única de metadata de posts.
	- Markdown por idioma (`*.es.md` / `*.en.md`) ingeridos dinámicamente.
	- Modo `--dry-run` / hash SHA256 (title+excerpt+content) para idempotencia y planificación.
- Nuevo workflow CI `content-sync.yml` (plan automático en push, apply manual con `apply=true`).
- Validación estructural previa (`scripts/validate_posts.py`).
- Documentación dedicada: `CONTENT_AUTOMATION.md`.
- Preparado terreno para slugs por idioma e imágenes (no implementado aún).
- Bump versión tema a 0.3.15.

## 0.3.14 – 20250925 (Release)
- Mejoras script contenido:
	- Parser Markdown ampliado (listas anidadas básicas, enlaces, código inline y bloques ```).
	- Diff por hash SHA256 (title+excerpt+content) evita updates innecesarios (log [skip]).
	- Fallback traducciones Polylang: muestra comandos wp-cli y curl si el PATCH meta falla.
	- README documenta flujo `content/*.md` y extensión multi-post.
- Bump versión del tema a 0.3.14.

# Changelog

### Notas complementarias 0.3.18
- Limpieza documental final: eliminación de archivos históricos (`INFORME_UNICO_RESCATE.md`, `PLAN_v0_3_0.md`, documento maestro previo y gobernanza inicial) tras migrar checklists operativas.
- Consolidación de índice (`docs/INDEX.md`) sin sección de archivo; referencia a historial vía Git.
- Documentación ampliada: métricas y observabilidad (`docs/PERFORMANCE_METRICS.md`), quality gates planificados.

## 0.3.13 – 20250925 (Release)
- Refactor multi‑post: `scripts/publish_content.py` ahora soporta lista `POSTS` (n>1) con `translation_key` para agrupar y enlazar traducciones de forma genérica.
- Ingesta Markdown: fuentes externas en `content/*.md` convierten a HTML (posts y futuras páginas) de forma idempotente.
- Añadidos 4 archivos Markdown iniciales:
	- `checklist-wordpress-produccion-1-dia.es.md` / `ship-wordpress-production-in-one-day.en.md`
	- `gobernanza-automatizacion-wordpress-pequenos-equipos.es.md` / `wordpress-governance-automation-small-teams.en.md`
- Segundo post bilingüe (gobernanza y automatización) generado automáticamente (slugs y categorías gestionadas).
- Idempotencia extendida: comparación y actualización selectiva multi‑post sin duplicados.
- Estructura preparada para añadir más posts simplemente agregando pares Markdown y entrada en `POSTS`.
- Housekeeping: directorio `content/` versionado como fuente única de verdad de contenidos.

## 0.3.12 – 20250925 (Release)
- Automatización de contenido inicial vía script `scripts/publish_content.py` (posts bilingües + legales + linking básico Polylang).
- Idempotencia: re-ejecutar no duplica posts/páginas; actualiza título/excerpt/content si cambian.
- Preparado para integrar textos completos desde fuentes externas.

## 0.3.11 – 20250924 (Release)
- CI reforzado: script `scripts/blog_health_ci.sh` para validar listados de blog ES/EN (HTTP 200, markers `posts_found` o `#blog-query-info`).
- Workflow `deploy.yml`: paso "Blog listing health" posterior a content ops y antes de integridad.
- Workflow `site-health.yml`: verificación periódica de markers de blog añadida.
- Housekeeping: `_releases/` y artifacts `.zip/.sha256` ignorados en git.
- Documentación: README (último release), Runbook sección 8 ampliada con nota de integración CI.
- Bump versión a 0.3.11 en `style.css`.

## 0.3.10 – 20250924 (Release)
- Blog bilingüe operativo: plantilla `page-blog.php` independiente de `page_for_posts`, query filtrada por idioma (Polylang) y paginación.
- Normalización de slugs Blog: resolución de conflicto (`blog`, `blog-en`, `blog-2`, `blog-es`) mediante scripts idempotentes (`normalize_blog_slug.sh`, `finalize_blog_slugs.sh`).
- Health check específico (`_scratch/blog_health_check.sh`): valida slugs, plantilla, HTTP 200, marker `posts_found` y conteo por idioma.
- Marker de depuración en HTML (`<!-- posts_found:X lang:YY -->`) para observabilidad remota.
- Ajustes de documentación pendientes: sección Blog bilingüe añadida al informe único; preparación de próximos pasos SEO (breadcrumbs, bloque "Últimas entradas").
- Housekeeping pendiente: consolidar scripts de migración de slugs (se documentan antes de archivarlos / limpieza futura).

## 0.3.0 – 20250923 (Release)
- Contenido inicial: primer artículo ES/EN definido (título, excerpt, cuerpo, slugs y categorías Guías/Guides) listo para publicar; retirada de “Hello world!” planificada.
- Legales mínimos: Políticas de Privacidad y Cookies (ES/EN) redactadas y listas para alta; enlazado en footer ES/EN definido.
- Formularios/SMTP: unificación de formulario ES/EN (campos, validaciones, microcopy, estados); plan de configuración SMTP (Hostinger 587 TLS o proveedor externo) y plan de pruebas (éxito/error/antispam).
- SEO inicial: sitemaps/robots validados; canónicas/hreflang a revisar con Rank Math al publicar; Search Console pendiente de verificación por propiedad.
- Limpieza de sitemap: retirada efectiva de `hello-world` tras limpiar caché de Rank Math (DB+FS), purgar LiteSpeed y recalentar sitemaps (script remoto + mu-plugin temporal).
- Documentación: `docs/INFORME_UNICO_RESCATE.md` actualizado (sección “Deployment v0.3.0”) con auditoría, pasos, validaciones y checklist; anotación en `docs/VALIDACION_MVP_v0_2_1.md` para v0.3.0.

## 0.1.2 – 20250917_191856
- Paleta y tipografías (Montserrat + Open Sans).
- Home con Hero + 3 cards (front-page.php).
- Encolado de estilos (assets/css/theme.css).
- Deploy del tema a producción.

## 0.1.1 – 20250917_190030
- Deploy a producción por SCP (solo tema).

## 0.1.3 – 20250917_192551
- Menú “Principal” creado y asignado.
- Páginas base ES/EN generadas.
- Footer con enlaces placeholders legales.
- Deploy del tema a producción.

## 0.1.4 – 20250917_193413
- Templates base: page, single, archive, 404.
- SEO mínimo (OG/Twitter en head).
- Polylang instalado/activado (prod) y checklist ES/EN.
- Script de rollback de tema.
- Deploy del tema a producción.
## 0.1.5 – 20250917_194157
- Imagen destacada mostrada antes del título en `single.php` (si existe thumbnail).
- Breadcrumbs básicos (`pc_breadcrumbs()`) inyectados vía hook `wp_body_open`.
- Plantilla de resultados de búsqueda `search.php` y formulario accesible `searchform.php`.
- Conmutador de idioma en el header: usa Polylang si está activo; fallback manual ES / EN.
- Versionado dinámico de assets usando `wp_get_theme()->get('Version')` (elimina caché obsoleta en updates).
- Script unificado de deploy `_scratch/deploy_theme.sh` (bump versión, ZIP, SHA256, SCP, purge, resumen Markdown).
- Deploy del tema a producción.
## 0.1.6 – 20250917_195114
- Imagen destacada en single, breadcrumbs básicos, plantilla search y searchform accesible,
- switcher de idioma (Polylang si disponible), y script de deploy unificado con -m/-F/-n/-N.
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.
- Hotfix (TAG 20250917_195536): limpieza de cabecera en style.css (normaliza `Version: 0.1.6`).

## 0.1.7 – 20250917_200935
- i18n real: menús por idioma (Principal ES / Main EN) y header que selecciona menú según Polylang. Switcher opcional.
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.8 – 20250917_201422
- CI/CD: cache-busting + workflow deploy por tag + smoke tests
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.9 – 20250917_202234
- MEJORA_09: minificación CSS + manifest SHA256 + verificación remota opcional

- Hotfix (20250917_202315): Hotfix MEJORA_09: reintento deploy con verificación
- Hotfix (20250917_202417): Hotfix MEJORA_09: verificación ajustada con puerto
## 0.1.10 – 20250917_203939
- Perf: preconnect/preload, critical opcional, manifest extendido (woff2/webmanifest/ico/json)
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.11 – 20250917_204757
- Self-host fonts (woff2) + preloads; retiro Google Fonts; LCP hero optimizado (fetchpriority=high); mantiene cache-busting.
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.12 – 20250917_205359
- MEJORA_13: subsetting fuentes latin + unicode-range, preparación 0.1.12
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.13 – 20250917_211347
- Fuentes self-host WOFF2 reales (latin subset) con unicode-range; menor peso y mejor LCP.
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.1.14 – 20250918_092306
- WOFF2 reales (latin subset) reemplazan placeholders; unicode-range y guard-rails anti-vacíos.
- - -
**Próximos pasos sugeridos**
- Revisar menú/footers y enlaces.
- Verificar 404/search y métricas (Analytics/Search Console).
- Ajustar caché e imágenes (LiteSpeed/WebP).
- Preparar contenidos ES/EN y emparejar con Polylang.

## 0.2.0 – 20250918_ReleaseCandidate
- MVP bilingüe: páginas base ES/EN (Inicio/Home, Sobre mí/About, Proyectos/Projects, Blog/Blog EN, Recursos/Resources, Contacto/Contact).
- Menús por idioma (Principal ES / Main EN) poblados y ordenados.
- Home estática configurada (Inicio ID=5); page_for_posts sin asignar (decisión temporal EN Blog).
- SEO básico: Rank Math activo con títulos y meta descriptions iniciales (Home / Sobre mí / About).
- Formulario de contacto (WPForms Lite) creado (ID=29) e incrustado en páginas Contacto/Contact.
- Contenidos mínimos: tagline + pilares + bio breve + CTAs.
- Infra deploy + integridad (manifest, verificación, subsetting woff2) estable.
- Pendiente UI: asignar location `primary` por idioma en Polylang, validar formulario (envío real), refinar textos y ejecutar Lighthouse.

## 0.2.1 – 20250922_172013
- Plantillas: placeholder SVG inline (evitar 403 en imágenes del tema). EN Home/About asignadas y purga aplicada.

