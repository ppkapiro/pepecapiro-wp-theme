# Fase 3 — Maquetado Home y páginas base (ES/EN)

Generado: 2025-10-27

## Objetivo
Construir las plantillas Home, Sobre mí, Proyectos, Recursos y Contacto usando los tokens consolidados en Fase 2, asegurando bilingüismo, menús coherentes y metadatos OG correctos.

## Páginas en scope

| Página      | Slug ES      | Slug EN     | Plantilla              | Estado actual   |
|-------------|--------------|-------------|------------------------|-----------------|
| Home        | inicio       | home        | page-home.php          | Existe (MVP)    |
| Sobre mí    | sobre-mi     | about       | page-about.php         | Existe (MVP)    |
| Proyectos   | proyectos    | projects    | page.php (generic)     | Sin plantilla   |
| Recursos    | recursos     | resources   | page.php (generic)     | Sin plantilla   |
| Contacto    | contacto     | contact     | page-contact.php       | Existe (bilingüe)|

## Requisitos técnicos

### Tokens y estilos
- Todas las plantillas deben consumir variables CSS de `pepecapiro/assets/css/tokens.css`:
  - Colores: `--color-*`
  - Tipografía: `--font-title`, `--font-body`, `--font-size-step-*`
  - Espaciado: `--space-*`
  - Layout: `--max-width-content`, `--max-width-wide`
- Focos accesibles (`--focus-ring`) en enlaces y botones.
- Grid responsive (`@media (max-width: 62.5rem)` y `@media (max-width: 40rem)`).

### Bilingüismo
- Detectar idioma con `pll_current_language()` o fallback a inspección de URL.
- Copy específico ES/EN para títulos, subtítulos, CTAs.
- Enlaces internos via `home_url('/slug/')` o `pll_home_url()`.

### Menús
- Menú principal registrado como `primary` en `functions.php`.
- Contenido en `content/menus/` (menu-es.json, menu-en.json) con ítems Home, Sobre mí, Proyectos, Recursos, Contacto, Blog.
- Sincronización vía `scripts/content/publish_content.py --apply` o workflows de CI.

### Open Graph
- Imágenes OG obligatorias (1200×630):
  - `pepecapiro/assets/og/og-home-es.png`
  - `pepecapiro/assets/og/og-home-en.png`
  - (Opcional) og-about-es/en.png, og-projects-es/en.png, og-resources-es/en.png.
- `functions.php` ya sirve OG dinámico para Home; extender a otras páginas si detecta template.
- Metadatos: `og:title`, `og:description`, `og:image`, `og:url`.
- hreflang alternates generados automáticamente si Polylang está activo.

## Plantillas a actualizar/crear

### 1. page-home.php (actualizar)
- **Hero bilingüe**: título/CTA ajustados por idioma.
- **Grid de pilares** (3 columnas desktop, 1 móvil): usa `.pilares` y `.pilar-card` con tokens.
- **SVG placeholder inline** para hero__img (evitar 403 de imágenes del tema).
- **Botón CTA** con enlace a `/contacto/` o `/en/contact/`.

### 2. page-about.php (actualizar)
- **Grid 2 columnas** (`.about-grid`): copy + foto/placeholder.
- **Botones**: LinkedIn externo + CTA secundario a Contacto.
- **Copy ES/EN**: detección de idioma y condicionales.
- **Imagen placeholder SVG** inline (mismo motivo que Home).

### 3. page-projects.php (crear)
- **Título H1** bilingüe.
- **Intro breve**: "Proyectos seleccionados" / "Selected projects".
- **Grid de tarjetas**: `.grid` con `.card` para cada proyecto.
  - Placeholder: nombre, descripción, enlace "Ver más" (si aplica).
- **Sin contenido dinámico por ahora**: estructura estática para validar diseño.

### 4. page-resources.php (crear)
- **Título H1** bilingüe.
- **Intro**: "Recursos útiles" / "Useful resources".
- **Listado simple**: enlaces a guías, artículos, herramientas.
- **Estructura**: lista con íconos/placeholders y descripciones breves.

### 5. page-contact.php (revisar y confirmar)
- Ya existe y es bilingüe.
- Validar que use tokens (`var(--space-*)`, `.btn`, `.card`, etc.).
- Confirmar estados de formulario (`?status=ok|error`).
- Verificar honeypot y nonce.

## Menús

### Estructura esperada (ES/EN)
- Home / Inicio
- Sobre mí / About
- Proyectos / Projects
- Recursos / Resources
- Blog
- Contacto / Contact

### Archivos
- `content/menus/menu-es.json`
- `content/menus/menu-en.json`

### Sincronización
- Ejecutar `python scripts/content/publish_content.py --apply` tras editar.
- O usar workflow `publish-prod-menu.yml` en CI.

## Open Graph

### Imágenes a generar
1. **og-home-es.png** (1200×630)
   - Título: "Soporte técnico y automatización, sin drama."
   - Subtítulo: "Arreglo lo urgente hoy y dejo procesos más simples para mañana."
   - Logo/marca: pepecapiro.com
   - Colores: usar `--color-bg` (#0D1B2A), `--color-accent` (#1B9AAA).

2. **og-home-en.png** (1200×630)
   - Título: "Technical support and automation—without the headache."
   - Subtítulo: "I fix what's urgent today and simplify your processes for tomorrow."
   - Mismos colores/branding.

3. **(Opcional)** og-about, og-projects, og-resources con copy específico.

### Configuración en functions.php
- Ya existe lógica OG para Home en `functions.php` (detecta `is_home` y `$is_en`).
- Extender con condicionales para otras plantillas:
  ```php
  if (is_page_template('page-about.php')) {
    // servir og-about-es.png o og-about-en.png
  }
  ```

## Criterios de cierre Fase 3

- [ ] Plantillas Home, Sobre mí, Proyectos, Recursos actualizadas/creadas.
- [ ] Todas consumen tokens CSS sin valores hardcodeados.
- [ ] Copy bilingüe en cada plantilla (detección de idioma funcional).
- [ ] Menús ES/EN sincronizados y visibles en header.
- [ ] Imágenes OG generadas y servidas dinámicamente.
- [ ] Capturas desktop/móvil de Home, Sobre mí, Proyectos actualizadas en `evidence/ui/`.
- [ ] Validación visual: no hay colores hex fuera de tokens, focos visibles, grid responsive OK.

## Próximos pasos (post-Fase 3)

- **Fase 4**: SEO técnico (hreflang automático, schema estructurado, analítica).
- **Fase 5**: Performance y accesibilidad (subsets de fuentes, auditoría Lighthouse completa, axe-core).
- **Fase 6**: Contenido dinámico (posts blog, taxonomías, filtros).

