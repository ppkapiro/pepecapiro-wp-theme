# Desarrollo del entorno — pepecapiro

Fecha de última actualización: 2025-09-22

## 1. Resumen
Entorno local y de producción configurados para desarrollo de tema WordPress `pepecapiro`, con flujos de validación de rendimiento (Lighthouse) y despliegue manual.

## 2. Infraestructura
- WordPress 6.8.2 (Hostinger), PHP 8.2.28
- Tema: `pepecapiro`
- Plugins clave: Polylang, LiteSpeed Cache, Rank Math, WPForms

## 3. Tooling y automatización
- GitHub Actions para auditorías Lighthouse (móvil) sobre 10 URLs.
- Reportes publicados en `docs/lighthouse/` para navegación vía GitHub Pages.

## 4. Prácticas de performance
- Dequeue de CSS de bloques/core.
- Carga de fuentes WOFF2 con `font-display: swap` y preload único de la fuente crítica.

## 5. Plantillas MVP
- `page-home.php` y `page-about.php` implementadas y asignadas (ES/EN).

## 6. Polylang
- Páginas ES/EN vinculadas y consistentes.

## 7. Verificación
- 0×404 en assets; conteo de assets por página=4; HTML ~14–16 KB.
- Lighthouse móvil: métricas en `docs/VALIDACION_MVP_v0_2_1.md`.

## 8. Conclusión
El entorno alcanzó el estado MVP v0.2.1 validado. Está listo para avanzar a v0.3.0 con foco en:
- SMTP (configuración de correo transaccional)
- Publicación del primer artículo
- Cookies/políticas (banner y páginas legales)
