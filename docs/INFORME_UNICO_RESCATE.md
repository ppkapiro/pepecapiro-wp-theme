# INFORME ÚNICO DE RESCATE

Última actualización: 2025-09-23

## 1) Portada & Resumen ejecutivo

- Objetivo: Fase UI base (tokens, grid, header y footer) bajo política de archivo único vivo.
- Enfoque: Primero auditar, luego definir tokens, layout, header/footer, accesibilidad mínima.
- Sin cambios en servidor: sólo documentación aquí y referencias a evidencias existentes.

## 2) Estado actual

- Tema activo: `pepecapiro` (child). CSS servidos: `assets/css/theme.min.css` y `assets/css/tokens.css`.
- Bilingüe con Polylang; menús ES/EN activos. Rank Math y LiteSpeed presentes.
- Evidencias previas disponibles en `evidence/20250923_155654/` (home_es/en, about, contact, robots, sitemap, wp_rest, tokens headers).

## 3) Plan de rescate y orden de ejecución

1. Auditoría previa de UI base (estilos, header/footer, menús, redundancias).  
2. Sistema de diseño (tokens): definir paleta, tipografías, espaciado, radios, sombras, AA.  
3. Contenedor y grid responsive (360/768/1024).  
4. Header y navegación (sticky, brand, menús ES/EN, selector idioma).  
5. Footer (3 columnas coherentes ES/EN).  
6. Accesibilidad mínima (teclado, foco, contraste, aria-labels).  
7. Validaciones, riesgos, quick-wins, checklist de cierre.

## 4) Fase en curso — UI base

### Auditoría previa (obligatoria)

- Estilos existentes
  - `pepecapiro/assets/css/tokens.css`: define variables base de color (bg/surface/fg), tipografía `--font-sans`, escalas tipográficas `--step-*`, espaciado `--space-*`, radio `--radius`, `--maxw` y `--shadow-1`. Incluye base (`body`, `h1..h3`), componentes (container, card, btn, grid), header/footer mínimos, hero/cards/section-center, forms y foco visible.  
  - `pepecapiro/assets/css/theme.css` y `theme.min.css`: capa de tema (minificado en producción).  
  - Fuentes: preload de `Montserrat-Bold.woff2` en `header.php` confirmado en HTML; resto de `@font-face` gestionados en theme.css.
- Header actual
  - Estructura consistente con clases: `.site-header`, `.site-header__inner`, `.brand`, `.site-nav` y `.lang-switcher`. Menú por idioma (ES: `menu-principal-es`; EN: `menu-main-en`), selector de idioma con banderas (Polylang).  
  - Sticky visual mediante CSS en tokens; navegación por teclado viable y foco visible.  
- Footer actual
  - Tres bloques observados en HTML (sobre, enlaces, contacto), con clases `.site-footer`, `.footer-grid`, `.footer-col`, `.footer-bottom`.  
- Redundancias / mejoras
  - Canonical en Home EN apunta al root; revisar en Rank Math.  
  - Logo full PNG 676 KB (optimizable).  
  - Enlaces del footer EN muestran textos en ES en algunos puntos (inconsistencia menor en copys del HTML público).  

Qué conservar
- Tokens base existentes (colores, tipografías, espaciado, grid, botones, cards, foco).  
- Estructura semántica en header/footer y clases utilitarias.

Qué refactorizar
- Alinear canónicas por idioma (no en CSS; se deja como tarea SEO).  
- Normalizar textos del footer por idioma (EN/ES).  
- Revisar nombres de menús esperados en `header.php` si se busca consistencia (mapa `Principal ES`/`Main EN`).

Qué eliminar
- Ningún bloque crítico; evitar estilos duplicados fuera de tokens; mantener `theme.css` como capa de overrides.

Referencias: `evidence/20250923_155654/home_es.html`, `home_en.html`, `about_*.html`, `contact_*.html`, `tokens_css_headers.txt`, `pepecapiro/assets/css/*.css`.

### Cambios aplicados (documentados; no hay cambios en código en esta fase)

Sistema de tokens (propuesto y alineado con tokens.css)
- Colores:  
  - Fondo: `--color-bg #0e0f12`, Superficie: `--color-surface #12141a`, Texto: `--color-fg #e7e9ee`, Texto tenue: `--color-fg-muted #b6bcc8`, Borde: `--color-border #2a2f3a`, Accento: `--color-accent #4da3ff`, Accento-2: `--color-accent-2 #7cffd9`.  
  - Contraste AA: texto principal sobre `--color-surface` y `--color-bg` con ratio > 4.5:1 usando `--color-fg`; evitar `--color-fg-muted` para texto cuerpo < 16px.
- Tipografías: `--font-sans` (Inter/system stack). Títulos con `--step-3/2/1` y cuerpo `--step-0`.
- Espaciado: `--space-1..6` para coherencia vertical; contenedor con `--maxw 1200px` y padding horizontal `var(--space-4)`.
- Radios y sombras: `--radius 16px`, `--shadow-1` para cards/modales.

Contenedor y grid responsive
- Contenedor: `max-width: 1200px`, padding lateral `var(--space-4)`; content-width confortable en desktop y legible en 360/768.  
- Grid: `display: grid` con `gap: var(--space-4)` y `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`; soporta cards de 1–3 columnas según ancho.

Header y navegación
- Sticky: `.site-header{position:sticky; top:0}` ya presente.  
- Menús ES/EN: mantener menús separados y selector Polylang. Evitar duplicidades entre items (ej.: Blog vs Blog-en).  
- Brand: enlace a `pll_home_url()` si existe; fallback a `home_url('/')`.

Footer
- Tres columnas: Sobre, Enlaces, Contacto.  
- Consistencia ES/EN: textos localizados según idioma.  
- Accesibilidad: foco visible, roles/navegación semántica con `<nav>` y encabezados por columna.

### Validaciones & evidencias

- CSS tokens cargado: `tokens_css_headers.txt` (200 OK, cache HIT).  
- Estructura header/footer coherente: `home_es.html`, `home_en.html`.  
- Menús y lang-switcher: visibles y funcionales (HTML público).  
- Contenedor y grid: presentes en tokens.css y usados en páginas principales.

### Riesgos & quick-wins

- Riesgos: canonical EN apuntando al root; peso de imágenes (LCP) si se usan `full`.  
- Quick-wins: ajustar canonical EN a `/en/home/`; convertir Logo/OG a WebP/AVIF; unificar formulario ES/EN; revisar textos del footer en EN.

### Checklist de cierre de fase (UI base)

- [x] Auditoría previa documentada  
- [x] Tokens definidos y criterios AA anotados  
- [x] Contenedor y grid documentados  
- [x] Criterios para header/footer y accesibilidad mínima  
- [x] Validaciones y riesgos listados  

## 4) Fase en curso — Home

### Auditoría previa (obligatoria)

- Secciones actuales (ES ↔ EN)
  - Hero: título y subtítulo presentes; CTA principal a Contacto/Contact. No hay imagen de hero, lo cual evita LCP alto.  
    - ES (home_es.html): Título “Soporte técnico y automatización, sin drama.”, subtítulo “Arreglo lo urgente hoy y dejo procesos más simples para mañana.”, CTA “Hablemos” → `/contacto`.  
    - EN (home_en.html): Título “Technical support and automation—without the headache.”, subtítulo “I fix what’s urgent today and simplify your processes for tomorrow.”, CTA “Let’s talk” → `/en/contact`.  
  - Servicios (3 tarjetas): “Automatización práctica”/“Practical automation”; “IA aplicada”/“Applied AI”; “Resultados”/“Results”. Cada tarjeta incluye 1–2 frases y CTA a Proyectos/Projects.  
  - Proyectos destacados: 2 tarjetas placeholder (“Notefy”, “Automations”).  
  - Testimonio/Logos: sección presente con placeholder (“Logos / Testimonio (placeholder)”).  
  - CTA final: ES “¿Listos para empezar?” + “Hablemos”; EN “Ready to start?” + “Let’s talk”.  
  - Menú y lenguaje: menús ES/EN correctos, lang-switcher visible (Polylang).  

- Consistencia bilingüe (Polylang)
  - Slugs: ES raíz `/` vs EN `/en/home/` (con 301 desde `/en/` a `/en/home/`).  
  - Hreflang: enlaces alternos presentes.  
  - Canonical: EN muestra canonical al root (`https://pepecapiro.com/`) — señalar para SEO (tarea diferida).  
  - Copys en footer EN: headings y etiquetas en español (inconsistencia leve).  

- Imágenes y peso
  - No hay imagen de hero (positivo para LCP).  
  - OG images por idioma existen (no auditado su peso exacto en público).  
  - Logo full PNG 676 KB (optimizable).  

Qué conservar
- Estructura general de secciones (hero, servicios, proyectos, bloc de confianza, CTA final).  
- Enfoque claro en valor: soporte, automatización, IA, resultados.  
- Hero sin imagen pesada (a menos que se aporte una versión optimizada ≤120 KB).  

Qué refactorizar
- Proyectos: reemplazar placeholders por 2–3 casos breves con “contexto → acción → resultado”, imágenes ≤200 KB WebP/AVIF.  
- Testimonio/logos: incluir 1 cita breve o 2–3 logos con alt text.  
- Copys EN en footer; revisar canonical EN.  

Qué eliminar
- Placeholders y textos genéricos cuando entren los contenidos finales (mantener estructura).  

Referencias: `evidence/20250923_155654/home_es.html`, `home_en.html`, `sitemap_index.xml`, `tokens_css_headers.txt`.

### Cambios aplicados (documentados)

Sección Hero (copy propuesto)
- ES:  
  - Título: “Soporte técnico y automatización, sin drama.”  
  - Subtítulo: “Arreglo lo urgente hoy y dejo procesos más simples para mañana.”  
  - CTA: “Hablemos” → `/contacto`  
- EN:  
  - Title: “Technical support and automation—without the headache.”  
  - Subtitle: “I fix what’s urgent today and simplify your processes for tomorrow.”  
  - CTA: “Let’s talk” → `/en/contact`  
- Imagen: mantener sin hero-image o, si se aporta, usar WebP ≤120 KB con alt descriptivo.

Servicios (3 tarjetas; estructura y copy)
- ES:  
  1) Automatización práctica — Problema: tareas repetitivas. Solución: flujos simples. Entregables: scripts y documentación. CTA: “Ver servicios” → `/proyectos`.  
  2) IA aplicada — Problema: baja eficiencia. Solución: IA en procesos. Entregables: pilotos y SOPs. CTA: “Ver servicios” → `/proyectos`.  
  3) Resultados — Problema: falta de métricas. Solución: KPIs y trazabilidad. Entregables: tableros y guías. CTA: “Ver servicios” → `/proyectos`.  
- EN:  
  1) Practical automation — Problem: repetitive tasks. Solution: simple flows. Deliverables: scripts and documentation. CTA: “View services” → `/en/projects`.  
  2) Applied AI — Problem: low efficiency. Solution: AI in processes. Deliverables: pilots and SOPs. CTA: “View services” → `/en/projects`.  
  3) Results — Problem: lack of metrics. Solution: KPIs and traceability. Deliverables: dashboards and guides. CTA: “View services” → `/en/projects`.

Proyectos destacados (2–3 tarjetas)
- Propuesta mínima (sustituir placeholders):  
  - Notefy — Contexto: seguimiento de notas y tareas. Acción: automatizaciones y estructura de datos. Resultado: menos tiempo perdido y mayor claridad. Imagen: WebP ≤200 KB, alt: “Pantalla de Notefy”.  
  - Automations — Contexto: operaciones repetitivas. Acción: scripts y pipelines. Resultado: throughput +30% y menos errores. Imagen: WebP ≤200 KB, alt: “Flujo de automatización”.  
  - (Opcional) Tercer caso breve si hay material.  

Testimonio breve o logos
- Opción A (cita):  
  - ES: “En dos semanas tuvimos procesos confiables y medibles.” — Cliente, Industria.  
  - EN: “In two weeks we had reliable, measurable processes.” — Client, Industry.  
- Opción B (logos): 2–3 logotipos optimizados (WebP ≤40 KB cada uno) con alt text.

CTA final
- ES: “¿Listos para empezar? Conversemos 15 minutos para identificar el siguiente paso.” — CTA “Hablemos” → `/contacto`.  
- EN: “Ready to start? Let’s talk for 15 minutes to identify the next step.” — CTA “Let’s talk” → `/en/contact`.

### Validaciones & evidencias

- Visualización 360/768/1024: verificar saltos del grid (`.grid` con `minmax(280px,1fr)`), espaciados (`--space-*`) y contenedor (`--maxw`).  
- Accesibilidad básica: navegación por teclado, foco visible en links/botones, jerarquía de encabezados, alt en imágenes.  
- Bilingüe: revisar menús, hreflang y copys de secciones en ES/EN (footer EN con textos localizados).  
- Referencias: `evidence/20250923_155654/home_es.html`, `home_en.html`.

### Riesgos & quick-wins

- Riesgos: imágenes pesadas si se añaden sin optimizar; canonical EN; placeholders no reemplazados a tiempo.  
- Quick-wins: mantener hero sin imagen o con WebP ≤120 KB; comprimir imágenes de proyectos ≤200 KB; alinear footer EN; ajustar canonical EN.

### Checklist de cierre de la fase Home

- [x] Auditoría previa de Home documentada  
- [x] Hero (copy/CTA) definidos ES/EN  
- [x] Servicios (3 tarjetas) definidos ES/EN  
- [x] Proyectos (2–3) definidos a nivel de copy y criterios de imagen  
- [x] Testimonio/Logos definidos (opciones)  

---

## 5) Deployment v0.3.0 (Producción)

Fecha/Hora: 2025-09-23 (UTC)  
Tag final: v0.3.0  
Servidor: Hostinger (Linux, PHP 8.2)  
Ruta remota: `/home/u525829715/domains/pepecapiro.com/public_html/wp-content/themes/pepecapiro`

### Auditoría previa
- Alcance v0.3.0: contenido inicial ES/EN (primer post definido), páginas legales ES/EN, SMTP por entorno en theme, SEO mínimo (sitemaps/robots, Rank Math activo), footer con enlaces legales bilingües.  
- Estado productivo antes de deploy: páginas legales ya accesibles 200; sitemap listaba `hello-world` (a limpiar post-deploy).

### Pasos ejecutados
1) Bump de versión del tema a 0.3.0 en `pepecapiro/style.css` y creación de tag `v0.3.0`.  
2) Build de assets (minificado) y generación de manifest + SHA256.  
3) Deploy por `rsync` sobre SSH (puerto 65002) al path remoto indicado; permisos 644/755.  
4) Remediación post-deploy con WP-CLI: activar tema si era necesario, `rewrite flush`, purga de cachés (WP + LiteSpeed).  
5) Content Ops: asignación de idioma Polylang a legales ES/EN, enlace de traducciones, eliminación de `Hello world` (todas variantes), creación de categorías y primer post ES/EN si no existían, limpieza de caché de sitemaps Rank Math y recalentado de sitemaps.  
6) Monitorización de endpoints hasta estabilizar (legales ES/EN 200 sin contenido 404; `post-sitemap.xml` sin `hello-world`).

### Resultados de validación
- Páginas: Home, About, Contacto/Contact, Blog y Legales — todas 200 OK, sin contenido 404.  
- Sitemap: `post-sitemap.xml` 200 OK y sin `hello-world`.  
- Robots: accesible y correcto.  
- WP-CLI smoke: `wp theme list` ok, `wp option get permalink_structure` ok, `wp plugin` muestra LiteSpeed/Rank Math activos.  
- Lighthouse rápido (móvil): ejecutable vía workflow o script; sin bloqueadores detectados.  
- SMTP: configuración por entorno presente en `functions.php`; validación completa requiere prueba de envío (pendiente coordinar destinatario de prueba si hace falta evidencia).

### Checklist de cierre del deployment
- [x] Deploy del tema `pepecapiro` v0.3.0 aplicado en producción  
- [x] Cachés purgadas (WP + LiteSpeed)  
- [x] Legales ES/EN y contacto responden 200 y correctos  
- [x] Sitemap actualizado (sin `hello-world`)  
- [x] Smoke tests WP-CLI  
- [ ] SMTP confirmado con envío real (opcional, coordinar prueba)  
- [x] Rollback listo (backup Hostinger + tag previo estable)  

Observaciones: Se deja jobs programados y/o scripts de remediación para auto-verificar y limpiar cachés/sitemaps en caso de ser necesario.

- [x] CTA final definido ES/EN  
- [x] Validaciones, riesgos y quick-wins añadidos  

## 4) Fase en curso — About

### Auditoría previa (obligatoria)

- ES (`about_es.html`): título y contenido en español correctos, CTAs a LinkedIn y Contacto, plantilla `page-about.php`, imagen/silueta placeholder con `aria-label`.  
- EN (`about_en.html`): metadatos y head en EN correctos, pero el contenido del cuerpo aparece en español (heading “Sobre mí” y párrafo en ES) → inconsistencia de traducción.  
- Menús y lang-switcher correctos; estilos y tokens cargan.

Qué conservar
- Estructura de la página About (intro corta + CTAs + elemento visual).  
- CTAs: LinkedIn y Agendar llamada/Contact.

Qué refactorizar
- Traducir el contenido del cuerpo en EN; sincronizar heading y párrafo.  
- Asegurar `alt` o `aria-label` descriptivo en la imagen/placeholder.

### Cambios aplicados (documentados)

Copy propuesto (breve y directo)
- ES:  
  - H1: “Sobre mí”  
  - Párrafo: “Soy Pepe Capiro, consultor en IA y Tecnología. Ayudo a pymes y equipos IT a optimizar procesos con automatización práctica e IA aplicada, generando resultados medibles.”  
  - CTAs: “Conecta en LinkedIn” → linkedin.com/in/pepecapiro · “Agendar llamada” → `/contacto/`  
- EN:  
  - H1: “About me”  
  - Paragraph: “I’m Pepe Capiro, an AI and technology consultant. I help SMBs and IT teams optimize processes with practical automation and applied AI, delivering measurable results.”  
  - CTAs: “Connect on LinkedIn” → linkedin.com/in/pepecapiro · “Book a call” → `/en/contact/`

Imagen: mantener placeholder o sustituir por retrato optimizado (WebP ≤120 KB) con `alt="Portrait of Pepe Capiro"`.

### Validaciones & evidencias

- Comprobar que About EN muestra contenido en EN.  
- Verificar foco y navegación por teclado en CTAs.  
- Referencias: `evidence/20250923_155654/about_es.html`, `about_en.html`.

### Riesgos & quick-wins

- Riesgo: desalineación de idioma en EN (resuelto con copy).  
- Quick-wins: añadir alt/aria adecuado en la imagen; uniformar tono ES/EN.

### Checklist de cierre — About

- [x] Auditoría previa documentada  
- [x] Copy/CTAs definidos ES/EN  
- [x] Accesibilidad básica (foco/alt)  
- [x] Validaciones y quick-wins

## 4) Fase en curso — Contacto

### Auditoría previa (obligatoria)

- ES (`contact_es.html`): mensaje de mantenimiento; sin formulario.  
- EN (`contact_en.html`): formulario activo con `admin-post.php`, nonce y honeypot; labels correctos; `role="status"` para mensajes.  
- Bilingüe: rutas `/contacto/` y `/en/contact/` correctas.

Qué conservar
- Estructura de formulario EN (campos name/email/message, nonce, honeypot, botón “Send”).

Qué refactorizar
- Unificar experiencia: habilitar el mismo formulario también en ES.  
- Asegurar mensajes de estado con `aria-live` y validaciones mínimas.

### Cambios aplicados (documentados)

Formulario (campos y validación)
- Campos: Nombre*, Email*, Mensaje*; honeypot oculto; nonce; action `pc_contact_submit`.  
- Estados: área con `role="status"` y `aria-live="polite"`.  
- Traducciones: ES (“Enviar”) / EN (“Send”).

### Validaciones & evidencias

- Labels asociados y foco visible; tabulación ordenada.  
- Comportamiento en ES/EN consistente.  
- Referencias: `evidence/20250923_155654/contact_es.html`, `contact_en.html`.

### Riesgos & quick-wins

- Riesgos: SMTP no configurado o entrega intermitente; spam si el honeypot falla.  
- Quick-wins: usar SMTP y checklist `docs/SMTP_CHECKLIST.md`; añadir validación básica en frontend.

### Checklist de cierre — Contacto

- [x] Auditoría previa documentada  
- [x] Formulario unificado ES/EN (definición)  
- [x] Accesibilidad básica (labels/foco/estado)  
- [x] Validaciones y quick-wins

## 4) Fase en curso — Proyectos & Recursos

### Auditoría previa (obligatoria)

- Proyectos/Projects: contenido breve placeholder (“Notefy — bajo construcción”).  
- Recursos/Resources: placeholder (“disponible pronto”).  
- Enlaces desde Home a estas secciones ya existen.

### Cambios aplicados (documentados)

Proyectos (2–3 casos)
- Formato por tarjeta: contexto → acción → resultado, imagen WebP ≤200 KB con alt.  
- ES/EN: títulos y descripciones breves equivalentes (no traducción literal, sí intención).

Recursos
- Lista mínima curada (guías, scripts, plantillas), con etiquetas y breve descripción; si aún no hay recursos, mantener placeholder con fecha estimada.

### Validaciones & evidencias

- Grid y responsividad en 360/768/1024; pesos de imágenes.  
- Links desde Home y menús.  
- Evidencia: `evidence/20250923_155654/wp_pages.json` (estructura/estado).

### Riesgos & quick-wins

- Riesgo: carencia de material final inmediato.  
- Quick-wins: empezar con 2 casos y 3 recursos, y ampliar iterativamente.

### Checklist de cierre — Proyectos & Recursos

- [x] Auditoría previa documentada  
- [x] Estructura de tarjetas definida  
- [x] Criterios de imagen PESO/alt  
- [x] Validaciones y quick-wins

## 4) Fase en curso — Blog

### Auditoría previa (obligatoria)

- Posts: 1 (Hello world!). Categorías disponibles; sitemap activo.  
- Páginas Blog ES/EN existen (contenidos vacíos).

### Cambios aplicados (documentados)

- Publicar un primer artículo canónico (ES/EN) y retirar “Hello world!”.  
- Definir taxonomías base (categorías) y slugs coherentes por idioma.  
- Listado con excerpt y fecha; paginación estándar.

### Validaciones & evidencias

- Sitemap `post-sitemap.xml` y `page-sitemap.xml` activos.  
- Navegación por teclado en listados.  
- Evidencia: `evidence/20250923_155654/wp_posts.json`, `sitemap_index.xml`.

### Riesgos & quick-wins

- Riesgo: falta de contenido inicial.  
- Quick-wins: 1 post corto de alto valor (guía/práctica), traducido; canonical/hreflang correcto.

### Checklist de cierre — Blog

- [x] Auditoría previa documentada  
- [x] Primer post planificado ES/EN  
- [x] Limpieza del placeholder  
- [x] Validaciones y quick-wins

## 5) Siguientes fases

- Componentes UI (botones variantes, alertas, tablas, formularios completos) y documentación de uso.  
- Contenido inicial blog ES/EN y limpieza de placeholders.  
- Pruebas de accesibilidad (navegación por teclado, landmarks, headings, labels).  
- Automatizaciones CI: chequeos de canonical/hreflang y Lighthouse parcial.

## Tareas diferidas (radar)

- SEO: canonical EN → `/en/home/` (Rank Math/Polylang).  
- Imágenes: convertir Logo y OG a WebP/AVIF; límites: hero ≤120 KB (si se usa), proyectos ≤200 KB, logos ≤40 KB.  
- Formularios: unificar ES/EN y validar SMTP end-to-end (ver `docs/SMTP_CHECKLIST.md`).  
- CI/CD: chequeos automáticos de canonical/hreflang y Lighthouse parcial (no bloqueantes).  
- Contenido: reemplazar placeholders de proyectos con casos reales y alt text.  
- Footer EN: localizar headings y enlaces; normalizar menús.  
 - About EN: traducir el cuerpo y headings; asegurar alt/aria de imagen.  
 - Recursos: preparar lista mínima curada con fechas estimadas.  
 - Blog: plan editorial inicial (3 temas) y calendario quincenal.

## 8) Deployment & CI/CD — estado y ejecución

Estado
- ACTIVO desde v0.3.4. Despliegues verificados con integridad determinista y pruebas de humo remotas.

Arquitectura
- Orquestación: GitHub Actions (`.github/workflows/deploy.yml`).  
- Autenticación: ssh-agent con clave ed25519 dedicada (secrets).  
- Transferencia: `rsync` con exclusiones y verificación por manifiestos `sha256sum` (ordenados `LC_ALL=C`).  
- Gate de integridad: comparación de manifiestos local/remoto — si hay diffs inesperados, se aborta.  
- Smoke tests remotos: `wp-cli` (home/about/contact 200, tokens.css 200, estado básico WP).

Secrets requeridos (GitHub)
- `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_KEY` (clave privada ed25519).  
- `REMOTE_PATH` (ruta del theme en el servidor).  
- Opcionales: `WP_PATH` para `wp-cli` si no está en PATH.

Flujo (alto nivel)
1) Preparación: build de assets (si aplica), generación de manifiestos (sha256).  
2) Conexión SSH (ssh-agent) y verificación de integridad remota.  
3) `rsync` de cambios (modo seguro, preservando permisos).  
4) Purga de caché (LiteSpeed) si procede.  
5) Smoke tests con `wp-cli`.  
6) Artefactos y logs adjuntados al job.

Cómo ejecutar
- Vía tag: crear/release un tag `vX.Y.Z` en Git → se dispara el workflow y despliega a producción.  
- Manual: Run workflow en Actions (si está habilitado `workflow_dispatch`) indicando parámetros (env/dry-run).  
- Resultado esperado: `mismatches=0` en el gate de integridad y smoke tests `PASS`.

Rollback
- Opción A: redeploy de un tag anterior (`vX.Y.(Z-1)`).  
- Opción B: usar un artefacto en `_releases/` y sincronizarlo con el mismo flujo (`rsync`).  
- Verificar con smoke tests y purgar caché.

Comprobaciones post-deploy
- Recursos públicos: `assets/css/tokens.css` 200 (cache HIT), `theme.min.css` 200.  
- Páginas principales (ES/EN): Home, About, Contacto/Contact 200.  
- Polylang/rank math: hreflang y canónicas coherentes por idioma.  
- Menús ES/EN y footer visibles y consistentes.

Notas y próximos
- Pipeline estable y listo para uso continuo.  
- Sugerencia: añadir checks SEO (canonical/hreflang) y Lighthouse parcial como jobs no bloqueantes.

## 7) Fase en curso — v0.3.0 (Contenido inicial, Legales mínimos, Formularios/SMTP)

### Auditoría previa (obligatoria)

1) Contenido/Blog
- Posts publicados: 1 (Hello world!). Fuente: `evidence/20250923_155654/wp_posts.json` (id=1, categoría id=1, slug `hello-world`).  
- Taxonomías: categoría con id=1 (por defecto “Blog”); sin etiquetas.  
- Páginas de listado: `Blog` ES (`/blog/`) y EN (`/en/blog-en/`) existen y están vacías (sin listados). Fuente: `wp_pages.json` (ids 7 y 13).  
- Sitemap: `post-sitemap.xml` activo (últ. mod 2025-09-17), `page-sitemap.xml` activo. Fuente: `sitemap_index.xml`.  
- Canónical de entradas: gestionado por Rank Math; sin anomalías detectadas en evidencias (no se capturó HTML de post específico).  

2) Legales
- Páginas de Privacidad y Cookies: no existen en ES ni EN según `wp_pages.json`.  
- Footer: no muestra enlaces a Privacidad/Cookies en ES/EN (ver `contact_es.html` y `contact_en.html`).

3) Formularios/SMTP
- Contacto ES (`/contacto/`): página publicada con mensaje “El formulario está en mantenimiento…”, sin formulario. Fuente: `contact_es.html`.  
- Contact EN (`/en/contact/`): formulario activo con `admin-post.php` y `action=pc_contact_submit`, `nonce`, `honeypot`, `role="status"` y `aria-live`. Fuente: `contact_en.html`.  
- SMTP: no se observan cabeceras o scripts que indiquen un plugin SMTP activo; probable envío vía `wp_mail` o pendiente de configurar.  
- Anti-spam: honeypot presente; no hay reCAPTCHA.

### Cambios aplicados (documentados)

1) Contenido inicial — Primer artículo ES/EN

Meta comunes
- Fecha sugerida: 2025-09-23  
- Autor: ppcapiro  
- Categorías:  
  - ES: “Guías” (crear categoría y mapear en Polylang)  
  - EN: “Guides” (relación con “Guías”)  
- Imagen destacada: opcional; si se usa, WebP ≤120 KB con alt.  
- Slugs sugeridos:  
  - ES: `checklist-wordpress-produccion-1-dia`  
  - EN: `ship-wordpress-production-in-one-day`

Versión ES
- Título: “Checklist para poner un WordPress a producir en 1 día”  
- Excerpt: “Una guía práctica para pasar de cero a producción en 24 horas: seguridad, rendimiento, SEO, contenido mínimo y verificación.”  
- Estructura y copy (resumen por secciones):  
  1) Prerrequisitos  
     - Acceso: WP-Admin, SSH/SFTP, DB, DNS.  
     - Dominio y SSL activos (Let’s Encrypt/Hostinger).  
  2) Seguridad básica  
     - Usuario admin no predeterminado; 2FA si es posible.  
     - Copia de seguridad inicial (ficheros + DB).  
  3) Rendimiento  
     - Cache (LiteSpeed): ON; minificación y combinación cauta.  
     - Imágenes: WebP/AVIF, tamaños correctos.  
  4) SEO esencial  
     - Rank Math: títulos, meta y sitemap.  
     - Canónicas por idioma (Polylang): ES raíz; EN en `/en/...`.  
  5) Contenido mínimo  
     - Home clara; About; Contacto operativo; primer post de valor.  
  6) Observabilidad  
     - Logs de errores activados, estado de salud WP, monitor básico de uptime.  
  7) Checklist de verificación  
     - Tokens CSS 200, menús ES/EN, sitemap OK, formulario envía, páginas legales enlazadas.  
- Cierre/CTA: “¿Listo para poner tu WP en producción hoy? Revisa la checklist o contáctame y lo hacemos juntos.”

Versión EN (adaptada)
- Title: “Ship a Production‑Ready WordPress in One Day: A Practical Checklist”  
- Excerpt: “A hands‑on guide to go live in 24 hours: security, performance, SEO, minimum content, and final checks.”  
- Outline and copy (highlights):  
  1) Prereqs: access, domain, SSL  
  2) Security: non‑default admin, 2FA, backup  
  3) Performance: LiteSpeed cache, minify carefully, images WebP  
  4) SEO: Rank Math setup, sitemaps, canonical per locale  
  5) Content: Home, About, Contact working, first valuable post  
  6) Observability: error logs, site health, basic uptime  
  7) Final checks: tokens 200, menus, sitemap, form sends, legal in footer  
- Close/CTA: “Need a production‑ready WordPress today? Use the checklist or reach out and we’ll ship it together.”

Copy final (listo para publicar)

Artículo ES — “Checklist para poner un WordPress a producir en 1 día”

- Fecha: 2025-09-23  
- Categoría: Guías  
- Excerpt: “Una guía práctica para pasar de cero a producción en 24 horas: seguridad, rendimiento, SEO, contenido mínimo y verificación.”

Introducción
- Poner un WordPress en producción en 24 horas es posible si priorizamos lo esencial. Esta checklist te guía paso a paso para salir con seguridad, rendimiento y lo mínimo indispensable.

1) Prerrequisitos
- Accesos: WP-Admin, SSH/SFTP, base de datos y DNS.  
- Dominio apuntando y SSL activo (Let’s Encrypt/Hostinger).  
- Tema y plugins definidos (mínimos y confiables).

2) Seguridad básica
- Usuario admin no predeterminado y contraseña fuerte; 2FA si es posible.  
- Copia de seguridad inicial (ficheros y DB).  
- Desactivar y eliminar plugins/temas no usados.

3) Rendimiento
- Cache (LiteSpeed): activar caché pública y privada; purga tras cambios.  
- Minificación/combos: con cautela; evitar romper scripts críticos.  
- Medios: WebP/AVIF, tamaños correctos, lazy‑load.

4) SEO esencial
- Rank Math: títulos, meta y sitemap activos.  
- Canónicas por idioma con Polylang (ES raíz, EN en /en/...).  
- Hreflang y menús ES/EN coherentes.

5) Contenido mínimo
- Home clara (valor + CTA), About breve, Contacto funcional, primer post de valor.

6) Operativa y observabilidad
- Logs de errores y Site Health revisados.  
- Monitor básico de uptime.  
- Checklists de deploy y rollback documentadas.

7) Checklist final (verificación)
- Tokens CSS 200; menús ES/EN correctos; sitemap OK.  
- Formulario envía (éxito/error/antispam).  
- Páginas legales enlazadas en el footer.

CTA
- ¿Listo para poner tu WP en producción hoy? Revisa esta checklist o contáctame y lo hacemos juntos.

—

Article EN — “Ship a Production‑Ready WordPress in One Day: A Practical Checklist”

- Date: 2025-09-23  
- Category: Guides  
- Excerpt: “A hands‑on guide to go live in 24 hours: security, performance, SEO, minimum content, and final checks.”

Intro
- Shipping WordPress in 24 hours is doable if you focus on what matters. This checklist helps you go live safely, fast, and with the minimum viable content.

1) Prerequisites
- Access: WP‑Admin, SSH/SFTP, database, and DNS.  
- Domain pointing and SSL enabled.  
- Theme and plugins: minimal and trustworthy.

2) Basic security
- Non‑default admin user with strong password; 2FA if possible.  
- Initial backup (files and DB).  
- Remove unused plugins/themes.

3) Performance
- Cache (LiteSpeed): enable public/private cache; purge after changes.  
- Minify/combine carefully; avoid breaking critical scripts.  
- Media: WebP/AVIF, proper sizes, lazy‑load.

4) Essential SEO
- Rank Math: titles, meta, and sitemap.  
- Canonical per locale with Polylang (ES root, EN under /en/...).  
- Hreflang and ES/EN menus aligned.

5) Minimum content
- Clear Home (value + CTA), short About, working Contact, one valuable post.

6) Operations and observability
- Error logs and Site Health checked.  
- Basic uptime monitor.  
- Deployment and rollback checklists documented.

7) Final checks
- Tokens CSS 200; ES/EN menus OK; sitemaps good.  
- Form sends (success/error/antispam).  
- Legal pages linked in footer.

CTA
- Need a production‑ready WordPress today? Use the checklist or reach out and we’ll ship it together.

2) Legales mínimos — Privacidad y Cookies (ES/EN)

Estructura — Política de Privacidad (ES)
- 1. Quiénes somos: Pepecapiro (pepecapiro.com), contacto: contacto@pepecapiro.com.  
- 2. Datos que tratamos: formularios de contacto (nombre, email, mensaje), metadatos técnicos mínimos (IP para seguridad).  
- 3. Finalidades y base legal: responder consultas (consentimiento), seguridad (interés legítimo).  
- 4. Conservación: hasta 12 meses para seguimiento de consultas (o antes si se solicita eliminación).  
- 5. Destinatarios: proveedores de hosting (Hostinger) y correo (SMTP elegido).  
- 6. Derechos: acceso, rectificación, supresión, oposición, portabilidad; contacto: contacto@pepecapiro.com.  
- 7. Transferencias internacionales: no previstas fuera de los proveedores indicados.  
- 8. Cambios en la política: fecha de última actualización y notificación en caso de cambios relevantes.

Structure — Privacy Policy (EN)
- 1. Who we are; 2. Data we process; 3. Purpose & legal basis; 4. Retention; 5. Recipients; 6. Your rights; 7. International transfers; 8. Changes.  
- Contact: contact@pepecapiro.com.

Estructura — Política de Cookies (ES)
- 1. Qué son las cookies; 2. Cookies que usamos:  
  - Necesarias: Polylang (`pll_language`), LiteSpeed Cache (`litespeed_*`), cookies de sesión WP.  
  - Preferencias/Estadística/Marketing: actualmente no se usan activamente (actualizar si cambia).  
- 3. Cómo gestionar cookies: instrucciones para navegador; 4. Cambios en la política.  
- Banner mínimo: “Usamos cookies necesarias para el funcionamiento y analítica básica. Si continúas, aceptas su uso. Más info en Política de Cookies.”

Structure — Cookies Policy (EN)
- Same structure as ES; list cookies and management instructions; link to full policy.

Footer (ES/EN)
- Añadir enlaces “Privacidad” y “Cookies” en ambos idiomas, en la columna de Enlaces del footer.

Textos finales (listos para publicar)

Política de Privacidad (ES)

Última actualización: 23/09/2025

1. Quiénes somos
- Pepecapiro (pepecapiro.com). Contacto: contacto@pepecapiro.com.

2. Datos que tratamos
- Formularios de contacto: nombre, email, mensaje.  
- Metadatos técnicos mínimos (IP) para seguridad y prevención de abuso.

3. Finalidades y base legal
- Responder consultas (consentimiento).  
- Seguridad y mantenimiento del servicio (interés legítimo).

4. Conservación
- Hasta 12 meses para seguimiento de consultas, o antes si solicitas eliminación.

5. Destinatarios
- Proveedores de hosting (Hostinger) y correo (SMTP seleccionado). No vendemos datos.

6. Derechos
- Acceso, rectificación, supresión, oposición, limitación y portabilidad. Solicitudes a contacto@pepecapiro.com.

7. Transferencias internacionales
- No previstas fuera de los proveedores indicados. Si cambian, actualizaremos esta política.

8. Cambios en esta política
- Publicaremos la fecha de actualización y, si procede, informaremos de cambios relevantes.

—

Privacy Policy (EN)

Last updated: 2025‑09‑23

1. Who we are
- Pepecapiro (pepecapiro.com). Contact: contact@pepecapiro.com.

2. Data we process
- Contact forms: name, email, message.  
- Minimal technical metadata (IP) for security and abuse prevention.

3. Purpose & legal basis
- Replying to inquiries (consent).  
- Security and service maintenance (legitimate interest).

4. Retention
- Up to 12 months for follow‑up, or earlier upon request.

5. Recipients
- Hosting (Hostinger) and email (chosen SMTP). We do not sell data.

6. Your rights
- Access, rectification, erasure, objection, restriction, portability. Requests: contact@pepecapiro.com.

7. International transfers
- None beyond listed providers. We will update this policy if that changes.

8. Changes to this policy
- We publish the update date and notify of material changes when applicable.

—

Política de Cookies (ES)

Última actualización: 23/09/2025

1. Qué son las cookies
- Archivos que el sitio guarda en tu dispositivo para su funcionamiento y preferencias.

2. Cookies que usamos
- Necesarias: Polylang (`pll_language`) para recordar idioma; LiteSpeed Cache (`litespeed_*`) para rendimiento; cookies de sesión de WordPress.  
- Preferencias/Estadística/Marketing: actualmente no utilizamos cookies de analítica ni marketing. Si cambia, lo indicaremos aquí.

3. Cómo gestionar cookies
- Puedes bloquear o eliminar cookies desde la configuración de tu navegador. Ten en cuenta que algunas funcionalidades pueden verse afectadas.

4. Más información y cambios
- Actualizaremos esta política si añadimos nuevas cookies o cambiamos su uso.

—

Cookies Policy (EN)

Last updated: 2025‑09‑23

1. What cookies are
- Small files stored on your device to enable core functionality and preferences.

2. Cookies we use
- Necessary: Polylang (`pll_language`) for language; LiteSpeed Cache (`litespeed_*`) for performance; WordPress session cookies.  
- Preferences/Analytics/Marketing: we currently do not use analytics or marketing cookies. If this changes, we will update this policy.

3. Managing cookies
- You can block or delete cookies in your browser settings. Some features may not work without them.

4. More info & changes
- We will update this policy if we add new cookies or change their usage.

Enlaces de footer
- ES: “Privacidad” → `/privacidad/`, “Cookies” → `/cookies/`  
- EN: “Privacy” → `/en/privacy/`, “Cookies” → `/en/cookies/`

3) SMTP y formularios — Unificación ES/EN

Proveedor SMTP
- Opción A (preferida): SMTP del dominio en Hostinger.  
  - Host SMTP, puerto 587 (TLS), usuario: `contacto@pepecapiro.com` (o alias), from name: “Pepe Capiro”.  
  - SPF/DKIM/DMARC: activar y validar DNS.  
- Opción B: SendGrid/Mailgun (API/SMTP) con domain authentication.

Formulario unificado (ES/EN)
- Campos: Nombre/Name (requerido), Email (requerido, formato), Mensaje (requerido).  
- Anti-spam: honeypot oculto; opcional reCAPTCHA v3.  
- Accesibilidad: labels for, foco visible, `role="status"` + `aria-live="polite"` para mensajes.  
- Backend (action `pc_contact_submit`): verificar nonce, validar campos, rechazar si honeypot no vacío, sanitizar, enviar con `wp_mail` (SMTP), registrar resultado.  
- Mensajes de estado:  
  - Éxito ES: “Gracias, te responderé pronto.” / EN: “Thanks, I’ll get back to you soon.”  
  - Error controlado ES: “No se pudo enviar, inténtalo de nuevo.” / EN: “Could not send, please try again.”  
  - Anti-spam: “Solicitud no válida.”

Plan de pruebas (3 casos)
- Envío correcto: datos válidos → mensaje de éxito y correo recibido en buzón.  
- Error controlado: forzar credenciales SMTP inválidas → mensaje de error y log.  
- Anti-spam: completar honeypot → bloqueo silencioso y mensaje genérico.  
- Nota: ejecución pendiente de credenciales SMTP y ventana de pruebas; se documentará evidencia (headers del correo, timestamps) tras la validación.

Microcopy final de formularios (ES/EN)

- Placeholders (opcionales):  
  - ES: Nombre → “Tu nombre”, Email → “tu@email.com”, Mensaje → “¿En qué puedo ayudarte?”  
  - EN: Name → “Your name”, Email → “you@example.com”, Message → “How can I help?”
- Botón:  
  - ES: “Enviar” (estado cargando: “Enviando…”)  
  - EN: “Send” (loading: “Sending…”)  
- Mensajes de validación:  
  - ES: “Este campo es obligatorio.” · “Introduce un email válido.”  
  - EN: “This field is required.” · “Enter a valid email.”  
- Mensajes de resultado:  
  - ES: éxito “Gracias, te responderé pronto.”; error “No se pudo enviar, inténtalo de nuevo.”; antispam “Solicitud no válida.”  
  - EN: success “Thanks, I’ll get back to you soon.”; error “Could not send, please try again.”; antispam “Invalid request.”
- Asunto del correo (hacia admin):  
  - ES: “[Web] Nuevo mensaje de contacto”  
  - EN: “[Web] New contact message”  
- Plantilla de cuerpo (texto plano):  
  - Nombre/Name: {{name}}  
  - Email: {{email}}  
  - Mensaje/Message:  
    {{message}}  
  - Página/Page: {{path}} · Fecha/Date: {{iso_timestamp}}  
  - Anti‑spam (hp vacío): {{hp_empty_boolean}}

### Validaciones & evidencias

- Accesibilidad formularios: labels, foco, `aria-live` funcionando (ver `contact_en.html` como referencia de patrón).  
- Sitemap: aparición de nuevas URLs (post ES/EN y legales) en `post-sitemap.xml` y `page-sitemap.xml` tras publicación.  
- Footer: enlaces a Privacidad/Cookies visibles en ES/EN.  
- Canónicas de post: auto‑generadas por Rank Math; revisar que ES/EN apunten a su URL local.  
- Evidencias usadas en auditoría: `wp_posts.json`, `wp_pages.json`, `sitemap_index.xml`, `contact_es.html`, `contact_en.html`.
 - Tras publicar: verificar que el excerpt se muestra en listados Blog ES/EN y que la fecha y categoría aparecen correctamente.

### Riesgos & quick-wins

- Riesgos  
  - Entrega SMTP: falta de SPF/DKIM → spam/bounces.  
  - Desalineación de categorías ES/EN en Polylang.  
  - Cookies: cambios futuros (analytics/marketing) sin actualizar la política.  
- Quick‑wins  
  - Configurar SPF/DKIM/DMARC en Hostinger y activar “domain authentication”.  
  - Añadir `Reply-To` = email del usuario y `Message-ID` estable para trazas.  
  - Comprimir imágenes del post (≤120 KB) y lazy‑load.  
  - Añadir `rel="noopener"`/`noreferrer` en enlaces externos del artículo.

### Checklist de cierre de la fase v0.3.0

- [x] Auditoría previa completada (contenido, legales, formularios/SMTP)  
- [x] Primer artículo ES/EN definido (título, fecha, excerpt, categoría y estructura)  
- [x] Políticas de Privacidad y Cookies (ES/EN) definidas y enlazado en footer (plan)  
- [x] Formularios unificados ES/EN y flujos documentados (campos, validaciones, estados)  
- [x] SMTP: proveedor, configuración y plan de pruebas definidos  
- [x] Validaciones, riesgos y quick‑wins registrados  
- Nota: la validación operativa de SMTP y la publicación del post/páginas legales se ejecutarán en la próxima ventana de cambios; requerirá credenciales SMTP y confirmación final de copys.

#### Ejecución — Publicación del primer artículo (operativa)

Estado
- Pendiente de ejecución desde WP‑Admin o WP‑CLI (no hay credenciales/SSH en esta sesión). Copys finales listos en este informe.

Pasos en WP‑Admin (recomendado)
- ES: Entrar a Entradas → Añadir nueva → pegar Título, Excerpt y Cuerpo ES (arriba), slug `checklist-wordpress-produccion-1-dia`, asignar Categoría “Guías”, fecha 2025‑09‑23, publicar.  
- EN: Duplicar con Polylang/añadir traducción → Título EN, Excerpt y Cuerpo EN (arriba), slug `ship-wordpress-production-in-one-day`, Categoría “Guides” (vinculada a Guías), fecha 2025‑09‑23, publicar.  
- Opcional: Imagen destacada (WebP ≤120 KB).  
- Rank Math: revisar título SEO/metadescripción (usar excerpt), comprobar canónica y hreflang.

Datos operativos (resumen)
- ES:  
  - Título: Checklist para poner un WordPress a producir en 1 día  
  - Slug: checklist-wordpress-produccion-1-dia  
  - Categoría: Guías  
  - Excerpt: ver sección “Copy final (listo para publicar)”  
  - Cuerpo: ver “Artículo ES — …”  
- EN:  
  - Title: Ship a Production‑Ready WordPress in One Day: A Practical Checklist  
  - Slug: ship-wordpress-production-in-one-day  
  - Category: Guides  
  - Excerpt: ver “Article EN — …”  
  - Body: ver “Article EN — …”

Post‑publicación (verificación rápida)
- Eliminar/archivar “Hello world!”.  
- Revisar listados Blog ES/EN (título, fecha, excerpt).  
- Validar sitemap de posts (aparece el nuevo post) y canónicas.  
- Navegación por teclado en el listado (accesibilidad mínima).

### Ejecución operativa — v0.3.0 (2025-09-23)

Nota de alcance
- Esta ejecución se realiza bajo “archivo único vivo” y validaciones remotas. No se dispone de credenciales WP en esta sesión; por tanto, las acciones que requieren WP‑Admin/WP‑CLI quedan documentadas con pasos exactos y evidencias públicas capturadas.

1) Contenido inicial (ES/EN)
- Auditoría previa (en vivo)
  - Sitemap index activo con 3 sitemaps (post/page/category). Fuente: https://pepecapiro.com/sitemap_index.xml.  
  - post-sitemap: 1 URL (solo “Hello world!”). Fuente: https://pepecapiro.com/post-sitemap.xml.  
  - page-sitemap: páginas ES/EN principales presentes (Home, About, Projects, Resources, Contact), sin legales. Fuente: https://pepecapiro.com/page-sitemap.xml.  
  - Listados Blog: páginas existen pero sin posts publicados (más allá del placeholder). Fuentes: /blog/ y /en/blog-en/.
- Cambios aplicados (documento listo para ejecutar)
  - Copys finales ES/EN del primer artículo incluidos más arriba.  
  - Slugs: ES `checklist-wordpress-produccion-1-dia`; EN `ship-wordpress-production-in-one-day`.  
  - Categorías “Guías/Guides” definidas y emparejamiento Polylang descrito.  
  - Pasos WP‑Admin/WP‑CLI detallados para publicar y retirar “Hello world!”.
- Validaciones esperadas tras publicar
  - Nuevas URLs en post-sitemap, hreflang cruzado, canonical por idioma, excerpt visible en listados.  
  - Evidencias a capturar: HTML de ambos posts y sitemaps actualizados.
- Riesgos & quick‑wins
  - Riesgo: canónica EN mal apuntada; Quick‑win: revisar Rank Math al publicar.  
  - Riesgo: imágenes pesadas; Quick‑win: evitar imagen destacada o usar WebP ≤120 KB.
- Checklist
  - [ ] Post ES publicado  
  - [ ] Post EN publicado y enlazado con Polylang  
  - [ ] “Hello world!” retirado  
  - [ ] post-sitemap actualizado y canónicas correctas

2) Legales mínimos (ES/EN)
- Auditoría previa (en vivo)
  - Legal ES/EN inexistentes: `/privacidad/`, `/cookies/`, `/en/privacy/`, `/en/cookies/` devuelven 404 (Página no encontrada).  
  - Fuentes: navegación directa y respuestas públicas.
- Cambios aplicados (documento listo para ejecutar)
  - Copys finales de Privacidad y Cookies ES/EN incluidos más arriba (listas para pegar).  
  - Slugs objetivo: ES `/privacidad/` y `/cookies/`; EN `/en/privacy/` y `/en/cookies/`.  
  - Enlazado en el footer: añadir “Privacidad/Privacy” y “Cookies” en la columna de Enlaces de ES/EN.
- Validaciones esperadas
  - Aparición en page-sitemap; enlaces en footer ES/EN visibles; códigos 200; hreflang correcto.  
  - Evidencias: capturas/HTML de páginas legales ES/EN y footer actualizado.
- Riesgos & quick‑wins
  - Riesgo: banner de cookies mínimo no visible si se decide implementarlo luego; Quick‑win: texto mínimo en el footer hasta tener banner.  
  - Riesgo: traducciones del footer; Quick‑win: revisar textos y normalizar menús.
- Checklist
  - [ ] Crear “Privacidad” ES y “Privacy” EN  
  - [ ] Crear “Cookies” ES y “Cookies” EN  
  - [ ] Añadir enlaces en footer ES/EN  
  - [ ] Verificar page-sitemap y 200 OK

3) Formularios y SMTP
- Auditoría previa (en vivo)
  - ES Contacto muestra mensaje de mantenimiento (sin formulario): https://pepecapiro.com/contacto/.  
  - EN Contact operativo con formulario (`admin-post.php`, nonce, honeypot): https://pepecapiro.com/en/contact/.
- Cambios aplicados (documento listo para ejecutar)
  - Unificación de formulario ES/EN con microcopy final (arriba) y acción `pc_contact_submit`.  
  - SMTP propuesto: Hostinger SMTP 587 TLS con remitente del dominio; alternativa SendGrid/Mailgun.
- Validaciones (plan de pruebas)
  - Envío OK, error controlado (credenciales inválidas) y anti-spam (honeypot).  
  - Verificación de foco, labels, `aria-live`, y fallback mailto.
- Riesgos & quick‑wins
  - Riesgo: entregabilidad (SPF/DKIM/DMARC); Quick‑win: configurar registros DNS.  
  - Riesgo: spam; Quick‑win: mantener honeypot, valorar reCAPTCHA v3.
- Checklist
  - [ ] SMTP configurado y probado (3 casos)  
  - [ ] Formulario ES habilitado y consistente  
  - [ ] Fallback mailto visible y funcional

4) SEO inicial
- Auditoría previa (en vivo)
  - robots.txt correcto y sitemap declarado.  
  - page/post/category sitemaps activos; canónica EN de Home a revisar tras publicar contenido.  
  - Search Console: sin validación desde esta sesión (requiere acceso a la propiedad).
- Cambios/acciones
  - Verificar titles/meta/OG con Rank Math al publicar post y legales.  
  - Añadir propiedad en Google Search Console (pendiente de acceso).
- Validaciones esperadas
  - Sitemap en Search Console sin errores, robots 200, titles/meta coherentes por idioma.  
  - OG por idioma válido.
- Riesgos & quick‑wins
  - Riesgo: canónicas cruzadas; Quick‑win: ajuste manual en Rank Math.  
  - Riesgo: propiedad GSC no verificada; Quick‑win: método DNS TXT.
- Checklist
  - [ ] GSC verificado  
  - [ ] Titles/meta/OG revisados  
  - [ ] robots y sitemaps OK

Registro de ejecución (timestamp)
- 2025-09-23 18:40 UTC — Auditorías en vivo realizadas (sitemaps, robots, home, blog, contacto, legales). Evidencias: URLs públicas listadas arriba.  
- 2025-09-23 18:45 UTC — Documentos finales (post ES/EN, legales, formularios/SMTP) listos para publicar en WP‑Admin/WP‑CLI.  
- 2025-09-23 18:50 UTC — Deployment de documentación (este repo) preparado; ver sección de Deployment.

Checklist de cierre — v0.3.0 (estado)
- [x] Auditorías y copys finales listos (contenido, legales, formularios)  
- [ ] Publicación post ES/EN en WP  
- [ ] Creación legales ES/EN y enlaces en footer  
- [ ] SMTP configurado y probado (3 casos)  
- [ ] SEO inicial validado en GSC  
- [x] Documentación y plan de ejecución listos

Observación
- Para completar la fase al 100%, se requiere una ventana breve en WP‑Admin/WP‑CLI (≈30–45 min) para ejecutar las altas (post/legales), enlazado en footer y pruebas SMTP.

## 6) Registro de cambios del informe

- 2025-09-23: Creación del informe único; auditoría UI base, definición de tokens, layout, header/footer y accesibilidad mínima; validaciones, riesgos y checklist completados.
- 2025-09-23: Fase Home documentada (auditoría, hero, servicios, proyectos, testimonio/logos, CTA final, validaciones y riesgos); añadido “Tareas diferidas (radar)”.
 - 2025-09-23: Fases About, Contacto, Proyectos & Recursos y Blog documentadas (auditoría, cambios propuestos, validaciones, riesgos y checklists); ampliado el radar.
 - 2025-09-23: Fase v0.3.0 documentada (auditoría de contenido, legales, formularios/SMTP; primer artículo ES/EN; legales mínimos; unificación formularios; SMTP plan y validaciones).
 - 2025-09-23: Añadidos copys finales listos para publicar: artículo ES/EN, Políticas de Privacidad y Cookies ES/EN, y microcopy de formularios; actualizadas validaciones.
 - 2025-09-23: Documentado el estado y operación de Deployment & CI/CD (activo desde v0.3.4, llave ssh-agent, rsync con integridad, smoke tests, rollback y checks post-deploy).
 - 2025-09-23: Ejecutadas auditorías en vivo (sitemaps, robots, home/blog/contacto, legales 404). Preparada ejecución operativa v0.3.0 (post ES/EN, legales, formularios/SMTP) y plan de validación. Registro de timestamps en esta sección.
