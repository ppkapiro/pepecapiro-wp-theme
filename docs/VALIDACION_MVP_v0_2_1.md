# Validación MVP v0.2.1 — pepecapiro.com

Fecha: 2025-09-18

## Alcance

- Páginas auditadas (ES/EN): Home, Sobre mí/About, Proyectos/Projects, Recursos/Resources, Contacto/Contact.
- Checks: rendimiento (Lighthouse móvil), 404s, peso inicial (HTML + assets referenciados).

## Resumen ejecutivo

- Estado general: sin 404s en assets. HTML por página ~24–26 KB. Principales pesos: fuentes WOFF2 (Montserrat y Open Sans) y CSS del core de WP.
- Bloqueo PSI: la API pública de PageSpeed Insights devolvió 429 (cuota agotada del proyecto por defecto). Propuestas en “Siguientes pasos”.

## Métricas Lighthouse (móvil)

- Bloqueado: API PSI respondió 429 (RESOURCE_EXHAUSTED). No se pudieron obtener score, LCP, TTI, INP automáticamente en esta iteración.
- Alternativas:
  - Usar API key propia de Google PSI (proyecto de GCP del cliente) para evitar el pool compartido.
  - Ejecutar Lighthouse CLI local (Chrome headless) con `--preset=mobile` y exportar JSON/HTML.
  - Correr Lighthouse desde Chrome DevTools manualmente por página y capturar resultados.

## Peso inicial y assets

Fuente: script `_scratch/diagnostics/scan_payload_404.py` (GET HTML, extracción de assets, HEAD por asset).

Tabla de páginas (HTML y número de assets):

- https://pepecapiro.com/ — HTML 26,010 bytes; 9 assets
- https://pepecapiro.com/en/ — HTML 26,024 bytes; 9 assets
- https://pepecapiro.com/sobre-mi/ — HTML 24,658 bytes; 9 assets
- https://pepecapiro.com/en/about/ — HTML 24,903 bytes; 9 assets
- https://pepecapiro.com/proyectos/ — HTML 24,516 bytes; 9 assets
- https://pepecapiro.com/en/projects/ — HTML 24,740 bytes; 9 assets
- https://pepecapiro.com/recursos/ — HTML 24,358 bytes; 9 assets
- https://pepecapiro.com/en/resources/ — HTML 24,640 bytes; 9 assets
- https://pepecapiro.com/contacto/ — HTML 24,588 bytes; 9 assets
- https://pepecapiro.com/en/contact/ — HTML 24,825 bytes; 9 assets

Top assets por tamaño (Content-Length) — patrón consistente en todas las páginas:

1. Montserrat-Bold.woff2 — ~24.3 KB (200)
2. Montserrat-SemiBold.woff2 — ~23.9 KB (200)
3. OpenSans-Italic.woff2 — ~15.1 KB (200)
4. WP core block CSS style.min.css — ~15.1 KB (200)
5. OpenSans-Regular.woff2 — ~13.8 KB (200)

404/5xx assets: ninguno detectado.

## Recomendaciones

Corto plazo (sin cambiar diseño):
- Subconjuntos de fuentes (WOFF2 subset) para caracteres usados (latín básico) y cargarlas condicionalmente por peso/idioma; objetivo: -30–50% de bytes en WOFF2.
- Preload selectivo: mantener preload solo para la fuente crítica LCP; diferir otras fuentes con `font-display: swap`.
- Ajustar enqueue para no cargar `wp-includes/css/dist/block-library/style.min.css` si no se usan bloques nativos en páginas estáticas (o registrarlo como `print=false` en plantillas).

Medio plazo:
- Unificar tipografías: valorar reducir a una familia principal y 1–2 pesos.
- CSS crítico inline mínimo para el above-the-fold y carga diferida del resto.
- Añadir `fetchpriority="high"` al LCP si es imagen (no aplica aún).

## Siguientes pasos (Lighthouse)

- Opción A (recomendada): Proveer una API key de PSI (GCP) y repetir la recolección automática para las 10 URLs (móvil). Guardar JSON bruto en `_scratch/diagnostics/psi/` y agregar tabla de: Performance, LCP, TTI, INP.
- Opción B: Ejecutar Lighthouse CLI local y adjuntar reporte HTML/JSON a `_scratch/diagnostics/lh/`.
- Opción C: Ejecución manual en DevTools y volcado de métricas en este informe.

## Anexos

- Script: `_scratch/diagnostics/scan_payload_404.py`
- Salida: `_scratch/diagnostics/scan_payload_404.out`

## Post-Optimización (Bloque 4)

Cambios aplicados:
- Front-end: se desregistró `wp-block-library`, `wp-block-library-theme` y `global-styles`.
- Fuentes: preload único de `Montserrat-Bold.woff2` (700) y `font-display: swap` para el resto; se dejaron solo variantes usadas en CSS (Montserrat 700; Open Sans 400 normal e italic).

Verificación (después de deploy y purge):
- HTML por página bajó de ~24–26 KB a ~14–16 KB.
- Assets por página bajaron de 9 a 4.
- Ya no aparece `wp-includes/css/dist/block-library/style.min.css` en las páginas estáticas.
- 0 errores 404/5xx.

Top assets actuales por tamaño:
1) Montserrat-Bold.woff2 ~24.3 KB
2) JS/CSS ligeros del plugin Hostinger Reach (~1.3 KB y ~1.0 KB)
3) theme.min.css ~0.25 KB

Notas:
- Si se observa FOUT notable en body copy, considerar precargar `OpenSans-Regular.woff2` (solo si impacta al LCP visible).
- Para exprimir más, generar subsets WOFF2 reales para Montserrat/Open Sans.

## Actualización 2025-09-22 17:20 EDT

- Plantillas EN asignadas: Home (/en/) → Home (MVP); About (/en/about/) → Sobre mí (MVP).
- Purgas ejecutadas: `wp cache flush` + `wp litespeed-purge all`.
- Cambio en plantillas: las imágenes temporales del tema (about-temp.jpg, hero-temp.jpg) se reemplazaron por placeholders SVG inline para evitar bloqueos 403 del host sobre /wp-content/themes/*/assets/img.
- Verificación posterior: 0 errores 404/5xx en las 10 URLs; conteo de assets por página=4 en todas (About ES/EN incluido); HTML ~15–16 KB en Home; ~15 KB en About.

## Lighthouse móvil (métricas reales) — 2025-10-28 15:50:47

| Página | Perf | LCP | TTI | INP | Top 2 oportunidades |
|--------|------|-----|-----|-----|----------------------|
| [/](lighthouse/home.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/](lighthouse/en-home.html) | 98 | 2.0s | 2.0s | n/a | — |
| [/sobre-mi/](lighthouse/sobre-mi.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/about/](lighthouse/en-about.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/proyectos/](lighthouse/proyectos.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/projects/](lighthouse/en-projects.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/recursos/](lighthouse/recursos.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/resources/](lighthouse/en-resources.html) | 100 | 1.4s | 1.4s | n/a | — |
| [/contacto/](lighthouse/contacto.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/contact/](lighthouse/en-contact.html) | 100 | 1.5s | 1.5s | n/a | — |

## Lighthouse desktop (métricas reales) — 2025-10-28 15:50:47

| Página | Perf | LCP | TTI | INP | Top 2 oportunidades |
|--------|------|-----|-----|-----|----------------------|
| [/](lighthouse/home-d.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/](lighthouse/en-home-d.html) | 98 | 1.9s | 1.9s | n/a | — |
| [/sobre-mi/](lighthouse/sobre-mi-d.html) | 99 | 1.6s | 1.6s | n/a | — |
| [/en/about/](lighthouse/en-about-d.html) | 100 | 1.4s | 1.4s | n/a | — |
| [/proyectos/](lighthouse/proyectos-d.html) | 100 | 1.4s | 1.4s | n/a | — |
| [/en/projects/](lighthouse/en-projects-d.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/recursos/](lighthouse/recursos-d.html) | 100 | 1.5s | 1.5s | n/a | — |
| [/en/resources/](lighthouse/en-resources-d.html) | 100 | 1.4s | 1.4s | n/a | — |
| [/contacto/](lighthouse/contacto-d.html) | 100 | 1.4s | 1.4s | n/a | — |
| [/en/contact/](lighthouse/en-contact-d.html) | 100 | 1.4s | 1.4s | n/a | — |
