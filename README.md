# pepecapiro-wp-theme

[![Lighthouse Mobile + Docs](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml/badge.svg)](https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml)

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
- GitHub Actions: Lighthouse móvil (10 URLs) + verificación periódica de salud (`site-health.yml`).
- Health blog: `scripts/blog_health_ci.sh` usado en deploy y health schedule.

## CI/CD & Deploy (importante)

- Runbook de despliegue por tags y troubleshooting:
  - `docs/DEPLOY_RUNBOOK.md`
- Workflow principal de deploy (Actions):
  - `.github/workflows/deploy.yml`
- Releases (tags v*):
  - https://github.com/ppkapiro/pepecapiro-wp-theme/releases
- Último release: https://github.com/ppkapiro/pepecapiro-wp-theme/releases/tag/v0.3.13
- Artifacts y logs de integridad: ver pestaña “Actions” del run correspondiente.

## Estado de validación de rendimiento (etapa cerrada)
## Contenido Automatizado (Markdown -> WP)

El script `scripts/publish_content.py` ahora soporta múltiples posts y páginas usando archivos Markdown fuente:

Estructura:
```
content/
  <slug>.es.md
  <slug>.en.md
```

Flujo:
1. Añadir nueva entrada en la lista `POSTS` (clave `translation_key`, slugs, títulos, excerpts, categoría).
2. Crear archivos `content/<slug>.<lang>.md` con el cuerpo en Markdown.
3. Ejecutar el script exportando credenciales:
   ```bash
   export WP_URL=https://pepecapiro.com
   export WP_USER=admin
   export WP_APP_PASSWORD=xxxxx
   python3 scripts/publish_content.py
   ```
4. El script convierte Markdown (encabezados, listas, enlaces, código) a HTML ligero e **idempotente**: sólo actualiza si cambia el hash (`title+excerpt+content`).

Traducciones:
- Agrupa por `translation_key` y enlaza con Polylang (vía meta REST si disponible) o muestra fallback wp-cli.

Extender:
- Añadir más posts = añadir objetos a `POSTS` + Markdown. No requiere tocar lógica central.

Limitaciones parser ligero:
- No soporta tablas complejas ni imágenes Markdown todavía.
- Listas anidadas: un nivel adicional (indent 2+ espacios) soportado.

Mejoras futuras sugeridas: soporte imágenes, bloques de cita y tablas.


- Último workflow: https://github.com/ppkapiro/pepecapiro-wp-theme/actions/workflows/lighthouse_docs.yml
- Landing de Docs: https://ppkapiro.github.io/pepecapiro-wp-theme/docs/index.html
- Índice Lighthouse: https://ppkapiro.github.io/pepecapiro-wp-theme/docs/lighthouse/index.html
