# Roadmap — Automatización Total (Siguiente fase)

Objetivo: extender la automatización a páginas, home, menús, medios y ajustes.

Entregables clave:
- Páginas: sincronización declarativa (pages.json) con contenidos markdown y linking de traducciones.
- Home: plantilla y bloques parametrizados; datos desde archivos de contenido.
- Menús: definición por idioma y orden declarativo; idempotente por slug.
- Medios: subida y reutilización (hash), mapeo `.media_map.json` compartido.
- Ajustes: portada estática, sitemaps y SEO técnico base (Rank Math).

Hitos cortos:
- v0.4.0: páginas y linking completo.
- v0.4.x: menús y medios.
- v0.5.0: ajustes y endurecer quality gates (apply por defecto, rollback auto).

Referencias: `content-sync.yml`, scripts `publish_content.py`, `validate_pages.py`.
