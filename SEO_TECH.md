# SEO Técnico (Inicial)

Esta capa añade elementos básicos de discoverability y verificabilidad automatizada.

## Elementos implementados

1. Etiqueta canonical generada dinámicamente para cada vista (`wp_head`).
2. Etiquetas `hreflang` (incluye `x-default`) aprovechando Polylang.
3. JSON-LD:
   - `BreadcrumbList` (cuando hay más de un ítem en la jerarquía).
   - `Article` para entradas del blog (incluye fechas, autor, publisher con logo y `inLanguage`).
4. Script de auditoría `scripts/audit_seo_head.py` que:
   - Descubre URLs de posts publicados vía REST (`/wp-json/wp/v2/posts?lang=...`).
   - Valida presencia de canonical único.
   - Verifica `hreflang` para todos los idiomas configurados y `x-default`.
   - Comprueba JSON-LD `BreadcrumbList` y `Article`.
   - Genera reporte JSON y Markdown en `reports/seo/`:
     - `audit.json`
     - `audit.md`
   - Sale con código !=0 si hay errores críticos (sirve como gate futuro en CI).

## Configuración
Archivo `configs/seo_audit.json`:
```jsonc
{
  "base_url": "https://www.pepecapiro.com",
  "languages": ["es", "en"],
  "expected_hreflang_map": {"es": "es", "en": "en"},
  "require_article_jsonld": true,
  "require_breadcrumb_jsonld": true
}
```

## Próximos pasos sugeridos
- Gate CI opcional que ejecute auditoría tras deploy de staging.
- Extender mapeo `expected_hreflang_map` a códigos regionales (ej. es-ES, en-US) si se necesita geotargeting.
- Añadir validaciones: meta description dinámica, OpenGraph image fallback para posts, validación de `alt` en imágenes destacadas.
- Integrar verificación de estatus HTTP de enlaces externos (scanner ya planificado en roadmap general).

---
Generado automáticamente por la fase inicial de SEO técnico.
