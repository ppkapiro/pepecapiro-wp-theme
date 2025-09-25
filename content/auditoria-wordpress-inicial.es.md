# Auditoría Inicial de WordPress: 12 Chequeos Críticos

> Lista mínima para entender el estado real antes de tocar nada.

## 1. Versiones
- Core actualizado
- Plugins y temas sin vulnerabilidades conocidas

## 2. Accesos
- Usuarios admin mínimos
- Sin cuentas genéricas tipo `admin`

## 3. Backups
- Existen y restauración probada
- Frecuencia ≥ diaria

## 4. Plugins
- Eliminar los inactivos
- Evitar duplicidad funcional (cache/SEO)

## 5. Temas
- Solo tema activo + parent necesario
- Child theme versionado

## 6. Seguridad Básica
- Prefijo tablas no `wp_`
- Archivo `wp-config.php` con salts únicos

## 7. Rendimiento Base
- Cache de página activa
- Fuentes y assets minificados

## 8. Medición
- Analytics correcto (sin duplicados)
- Search Console verificado

## 9. SEO Técnico
- Sitemaps limpios
- `robots.txt` sin bloqueos indebidos

## 10. Contenido
- Sin lorem ipsum visible
- Páginas legales presentes

## 11. Formularios
- Envío correcto (probar éxito/error)
- Protección básica spam

## 12. Logs / Errores
- WP_DEBUG desactivado en prod
- No warnings visibles

---
Checklist usable como base de informe previo a mejoras.
