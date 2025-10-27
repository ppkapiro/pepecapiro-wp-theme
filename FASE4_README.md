# Fase 4 — Rendimiento, Accesibilidad y SEO

Fecha: 2025-10-27

Este documento resume los cambios y cómo verificarlos.

## Cambios clave

- Rendimiento
  - Preload woff2 en `wp_head` (Montserrat SemiBold, OpenSans Regular/SemiBold).
  - `utilities.css` con `.sr-only` y enqueue opcional.
  - Limpieza de OG con fallback si falta archivo.
- SEO
  - JSON-LD extra en Home: `Organization` + `WebSite` con `SearchAction`.
  - Open Graph consistente: meta OG por plantilla; fallback robusto.
- Accesibilidad
  - Landmarks y labels: `role="main"`, `aria-labelledby`, grillas como listas (`role="list"/`listitem`).
  - Enlace "Saltar al contenido" al inicio del `<body>`.
- CI (Lighthouse Gate)
  - Script `scripts/assert_lh_thresholds.py` valida Performance/LCP/CLS (móvil y desktop) contra `configs/perf_thresholds.json`.
  - Workflow actualizado `.github/workflows/lighthouse.yml` para ejecutar móvil y desktop, con reintento simple por URL, fallar si no se cumplen umbrales, publicar HTML en `docs/lighthouse/`, generar resumen en Markdown y adjuntar `_assert_summary.txt` con el detalle de fallos.

## Cómo validar

- UI Gate tokens
  - Ejecutar la tarea "UI Gate: Anti-hex CSS" (debe pasar sin hex fuera de `tokens.css`).
- Lighthouse en CI
  - Disparar "Lighthouse Audit (Mobile + Desktop)".
  - Revisar logs: si hay violaciones, el job falla con detalle por página.
  - Ver `docs/VALIDACION_MVP_v0_2_1.md` y reportes HTML publicados en `docs/lighthouse/` (móvil y desktop).
- Local opcional
  - `scripts/ci/run_lighthouse_local.py` lee `configs/lh_urls.txt` y genera HTML en `reports/lighthouse/<fecha>/`.

## Ajustes y extensiones (completados en esta fase)

- OG dedicadas para About/Projects/Resources (`pepecapiro/assets/og/`) — placeholder PNG válidos 1200×630 (1×1 mínimos de momento).
- Gate extendido a Desktop usando umbrales en `configs/perf_thresholds.json`.
- `.skip-link` inclusiva añadida en `header.php`.

## Archivos modificados

- `pepecapiro/functions.php`
- `pepecapiro/page-home.php`, `pepecapiro/page-about.php`, `pepecapiro/page-projects.php`, `pepecapiro/page-resources.php`
- `pepecapiro/header.php`, `pepecapiro/style.css`
- `.github/workflows/lighthouse.yml`
- `scripts/assert_lh_thresholds.py`
- `pepecapiro/assets/css/utilities.css`

