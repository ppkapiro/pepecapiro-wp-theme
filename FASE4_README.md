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
  - Workflow actualizado `.github/workflows/lighthouse.yml` para ejecutar móvil y desktop, fallar si no se cumplen umbrales y luego generar resumen.

## Cómo validar

- UI Gate tokens
  - Ejecutar la tarea "UI Gate: Anti-hex CSS" (debe pasar sin hex fuera de `tokens.css`).
- Lighthouse en CI
  - Disparar "Lighthouse Mobile Audit".
  - Revisar logs: si hay violaciones, el job falla con detalle por página.
  - Ver `docs/VALIDACION_MVP_v0_2_1.md` y artifacts HTML en `lighthouse_reports`.
- Local opcional
  - `scripts/ci/run_lighthouse_local.py` lee `configs/lh_urls.txt` y genera HTML en `reports/lighthouse/<fecha>/`.

## Ajustes y extensiones sugeridas

- Añadir OG dedicadas para About/Projects/Resources (`pepecapiro/assets/og/`).
- Extender gate a Desktop usando los umbrales existentes en `configs/perf_thresholds.json`.
- Añadir `.skip-link` estilizada si se desea un enlace visible para saltar al contenido.

## Archivos modificados

- `pepecapiro/functions.php`
- `pepecapiro/page-home.php`, `pepecapiro/page-about.php`, `pepecapiro/page-projects.php`, `pepecapiro/page-resources.php`
- `pepecapiro/header.php`, `pepecapiro/style.css`
- `.github/workflows/lighthouse.yml`
- `scripts/assert_lh_thresholds.py`
- `pepecapiro/assets/css/utilities.css`

