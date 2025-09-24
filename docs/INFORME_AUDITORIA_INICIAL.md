# Informe de Auditoría Inicial — Plan de Rescate (Fase 1)

Fecha: 2025-09-23  
Alcance: Auditoría no intrusiva basada en evidencias públicas. Sin cambios en servidor ni WP-Admin.

Ruta de evidencias: `evidence/20250923_155654/`

## Resumen ejecutivo

- Estado general: estable. Sitio bilingüe (ES/EN) operativo con Polylang, SEO con Rank Math y caché LiteSpeed funcionando.  
- Home ES/EN: consistentes, con metas SEO correctas y OG images cargando. `tokens.css` responde 200 (HIT CDN).  
- Contenidos: 6 páginas ES + 6 EN (pares clave: Home, About/Sobre mí, Contact/Contacto, Projects/Proyectos, Resources/Recursos, Blog).  
- Blog: 1 post placeholder (“Hello world!”).  
- Medios: al menos 1 imagen PNG (Logo) con variantes generadas; tamaño full 676 KB (optimizable).  
- Sitemap y robots: correctos; sitemap index activo por Rank Math.  
- Accesibilidad/performance: base sólida; hay margen de mejora en pesos de imágenes y copy/hreflang secundarios.

Conclusión: Base sana para el MVP. Recomendable una pasada de optimización ligera (imágenes/alt text) y checklist de SEO técnico/hreflang. Formularios: EN incluye formulario simple con honeypot; ES muestra mensaje de mantenimiento: alinear.

## Evidencias clave

- Home ES: `home_es.html` (lang es-ES, Rank Math, OG image `assets/og/og-home-es.png`, menú `menu-principal-es`)  
- Home EN: `home_en.html` (lang en-US, redirect previo 301 a `/en/home/`, Rank Math, OG image `assets/og/og-home-en.png`, menú `menu-main-en`)  
- About ES/EN: `about_es.html`, `about_en.html` (plantilla `page-about.php`, enlaces alternos hreflang OK)  
- Contact ES/EN: `contact_es.html`, `contact_en.html` (EN tiene formulario activo; ES indica mantenimiento)  
- Robots.txt: `robots.txt` (Sitemap declarado)  
- Sitemaps: `sitemap_index.xml` (post, page, category sitemaps)  
- REST API: `wp_pages.json`, `wp_posts.json`, `wp_media.json`  
- Tokens: `tokens_css_headers.txt` (HTTP 200, cache HIT, ETag presente)

## Contenido y estructura

- Páginas publicadas (REST):
  - ES: Inicio (id=5, `/`), Sobre mí (id=16), Proyectos (id=6), Blog (id=7), Recursos (id=8), Contacto (id=9)
  - EN: Home (id=10, `/en/home/`), About (id=11), Projects (id=12), Blog (id=13), Resources (id=14), Contact (id=15)
- Plantillas:
  - Home: `page-home.php` (ES id=5, EN id=10)
  - About: `page-about.php` (ES id=16, EN id=11)
  - Otras: plantilla por defecto (Contact/Contacto, Projects/Proyectos, Resources/Recursos, Blog)
- Emparejamientos ES/EN: coherentes por slugs y menús; hreflang alternates presentes en head.

Referencias: `wp_pages.json`, `home_es.html`, `home_en.html`, `about_es.html`, `about_en.html`, `contact_es.html`, `contact_en.html`.

## Blog y taxonomías

- Posts: 1 (Hello world!, id=1)  
- Categorías/sitemaps: presentes en `sitemap_index.xml` (category-sitemap).  
- Recomendación: despublicar/eliminar el post placeholder o reemplazar por un primer artículo canónico en ambos idiomas.

Referencias: `wp_posts.json`, `sitemap_index.xml`.

## Medios y rendimiento

- Logo.png (1024×1024, 676 KB full, PNG) con derivadas 300/150/768.  
- Oportunidades:
  - Convertir a WebP/AVIF, comprimir a < 120 KB para `full` si es posible (o limitar uso de `full` en front).  
  - Introducir `loading=lazy` en imágenes no críticas (ya presente en derivadas).  
  - Confirmar que OG images están optimizadas (< 200 KB) y con dimensiones 1200×630.

Referencias: `wp_media.json`, `home_es.html`, `home_en.html`.

## SEO técnico y metadatos

- Rank Math inyecta: title, description, canonical, OG/Twitter, JSON-LD.  
- Hreflang: enlaces `alternate` ES↔EN en Home, About, Contact (coherentes).  
- Canonical Home EN: observado como `https://pepecapiro.com/` en head; sugerencia: revisar que canonical apunte a la URL real en EN (`/en/home/`) para consistencia en Rank Math (evitar canónicas cruzadas)[1].  
- OG images: separadas por idioma (`og-home-es.png`, `og-home-en.png`).  
- Robots: `index, follow`; `robots.txt` correcto con sitemap.

[1] Nota: El HTML de Home EN muestra `<link rel="canonical" href="https://pepecapiro.com/" />`. Conviene validar en Rank Math/Polylang la canonical específica para EN.

## Menús y navegación

- ES: `menu-principal-es` con Inicio, Sobre mí, Proyectos, Blog, Recursos, Contacto.  
- EN: `menu-main-en` con Home, About, Projects, Blog, Resources, Contact.  
- Lang-switcher visible en cabecera; cookies `pll_language` establecidas (ES/EN) por Polylang.

Referencias: `home_es.html`, `home_en.html`, `about_*`, `contact_*`.

## Formularios y comunicación

- EN Contact: formulario activo simple (POST a `admin-post.php`, nonce, honeypot).  
- ES Contacto: mensaje de mantenimiento sin formulario.  
- Sugerencia: unificar UX (ambos idiomas con el mismo mecanismo). Validar entrega SMTP (docs: `docs/SMTP_CHECKLIST.md`).

Referencias: `contact_en.html`, `contact_es.html`.

## Caché/CDN y headers

- `tokens.css`: 200 OK, `cache-control: public, max-age=604800`, `x-hcdn-cache-status: HIT`, `ETag` con variante gzip, `last-modified` presente.  
- LiteSpeed Cache marca páginas como cacheadas.

Referencias: `tokens_css_headers.txt`, pie de página HTML con marca de LiteSpeed.

## Riesgos y quick-wins

- Riesgos bajos:
  - Canonical de Home EN apuntando al root (posible canibalización de canonical).  
  - Imagen Logo full de 676 KB (penalización de LCP si se usa en viewport grande).
- Quick-wins:
  - Ajustar canonical EN a `/en/home/`.  
  - Optimizar imágenes a WebP/AVIF y revisar pesos de OG.  
  - Unificar formulario en ES/EN y probar envío (SMTP).  
  - Añadir alt text descriptivos a imágenes y verificar contraste y foco.

## Próximos pasos propuestos

1) SEO técnico y hreflang (1–2 h)
- Revisar ajustes Rank Math para canónicas por idioma (Home EN → `/en/home/`).
- Verificar sitemap de páginas por idioma y etiquetas `hreflang` consistentes.

2) Imágenes y estáticos (1–2 h)
- Convertir `Logo.png` y OG a WebP/AVIF; actualizar referencias si aplica.
- Asegurar `preload` sólo de fuentes críticas, y `lazy` en no críticas.

3) Formularios y SMTP (1–2 h)
- Activar el mismo formulario en ES; validar nonce/honeypot/CSRF.  
- Probar entrega SMTP end-to-end con credenciales y checklist interno.

4) Contenido inicial (1–2 h)
- Crear/elaborar 1 post real ES/EN y retirar “Hello world!”.  
- Afinar copys del hero para consistencia tonal ES/EN.

5) Observabilidad y CI (0.5 h)
- Añadir verificación automática de canonical/hreflang en smoke tests (curl + grep).  
- Añadir job de Lighthouse partial (home ES/EN) fuera de deploy crítico.

## Anexo: índices y cuentas

- Páginas publicadas: 12 (6 ES + 6 EN). Ver `wp_pages.json`.
- Posts: 1. Ver `wp_posts.json`.
- Medios inspeccionados: 1 (Logo). Ver `wp_media.json`.
- Sitemaps: posts, pages, categories. Ver `sitemap_index.xml`.

---

Elaborado por: Equipo técnico  
Contacto: contacto@pepecapiro.com
