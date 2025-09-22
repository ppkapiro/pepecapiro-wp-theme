# pepecapiro-wp-theme

Tema WordPress para pepecapiro.com.

## Métricas & Demo
- Tabla resumen (Mobile): ver `docs/VALIDACION_MVP_v0_2_1.md`.
- Reportes completos (HTML): `docs/lighthouse/index.html`.
- GitHub Pages (opcional): si habilitas Pages con “Source: Deploy from a branch” y carpeta `/docs`, podrás navegar a:
  `https://<usuario>.github.io/<repo>/lighthouse/index.html`

## Desarrollo rápido
- WP 6.8.2 (Hostinger), PHP 8.2.28
- Tema: `pepecapiro` (plantillas MVP: `page-home.php`, `page-about.php`)
- Optimización: fuentes WOFF2 con `font-display: swap`; se desregistran CSS globales de bloques.

## CI
- GitHub Actions: ejecución de Lighthouse (móvil) sobre 10 URLs, artefactos y reportes HTML.
