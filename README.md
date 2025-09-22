# pepecapiro-wp-theme

Tema WordPress para pepecapiro.com.

## Métricas & Demo

[![GitHub Pages](https://img.shields.io/badge/Pages-online-brightgreen)](https://ppkapiro.github.io/pepecapiro-wp-theme/docs/index.html)

- Tabla resumen (Mobile): `docs/VALIDACION_MVP_v0_2_1.md`.
- Reportes completos (HTML): `docs/lighthouse/index.html`.
- Landing de Docs: `docs/index.html`.

> GitHub Pages (modo /docs): https://ppkapiro.github.io/pepecapiro-wp-theme/docs/index.html

## Desarrollo rápido
- WP 6.8.2 (Hostinger), PHP 8.2.28
- Tema: `pepecapiro` (plantillas MVP: `page-home.php`, `page-about.php`)
- Optimización: fuentes WOFF2 con `font-display: swap`; se desregistran CSS globales de bloques.

## CI
- GitHub Actions: ejecución de Lighthouse (móvil) sobre 10 URLs, artefactos y reportes HTML.
