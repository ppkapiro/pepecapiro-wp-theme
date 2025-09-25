# Checklist para poner un WordPress a producir en 1 día

> Versión inicial sintetizada. Completar con secciones técnicas si se requiere mayor detalle.

## 1. Base y Acceso
- Dominio apuntado
- Hosting listo (PHP 8.2, HTTPS activo)
- Usuario admin + contraseña fuerte

## 2. Seguridad mínima
- Actualizaciones core + plugins
- Eliminar plugins/themes no usados
- Ajustar permalink “/%postname%/”

## 3. Rendimiento inicial
- Cache (LiteSpeed o equivalente) activada
- Fuentes WOFF2 self-host
- Imágenes comprimidas (WebP preferible)

## 4. SEO y estructura
- Rank Math configurado (sitemaps ok)
- `robots.txt` limpio
- Título y descripción coherentes

## 5. Contenido mínimo
- Home + About + Contact (ES/EN)
- Primer post (ES/EN) con excerpt
- Páginas legales (privacidad, cookies)

## 6. Verificación final
- Sitemap sin “hello-world”
- Lighthouse móvil ≥90
- Formulario contacto funcional

---
Checklist ejecutable en 24h si se reduce alcance gráfico y se prioriza estabilidad + medición.
