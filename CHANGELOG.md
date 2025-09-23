# Changelog

## 0.3.0 – 20250923 (Release)
- Contenido inicial: primer artículo ES/EN definido (título, excerpt, cuerpo, slugs y categorías Guías/Guides) listo para publicar; retirada de “Hello world!” planificada.
- Legales mínimos: Políticas de Privacidad y Cookies (ES/EN) redactadas y listas para alta; enlazado en footer ES/EN definido.
- Formularios/SMTP: unificación de formulario ES/EN (campos, validaciones, microcopy, estados); plan de configuración SMTP (Hostinger 587 TLS o proveedor externo) y plan de pruebas (éxito/error/antispam).
- SEO inicial: sitemaps/robots validados; canónicas/hreflang a revisar con Rank Math al publicar; Search Console pendiente de verificación por propiedad.
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

