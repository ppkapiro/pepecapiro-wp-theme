# WordPress Segunda Semana: Endurecimiento y Estabilización Prioritaria

La primera semana tras el lanzamiento mitigaste riesgos urgentes. Ahora toca consolidar, cerrar huecos residuales y establecer señales básicas de salud.

## Objetivos de esta fase
1. Reducir superficie expuesta.
2. Ganar visibilidad mínima (logs y monitoreo ligero).
3. Eliminar residuos que puedan degradar rendimiento.
4. Preparar base para escalado de contenido.

## 1. Revisión de cuentas y roles
- Elimina usuarios temporales creados para el lanzamiento.
- Verifica que no haya administradores sobrantes.
- Fuerza actualización de contraseñas débiles.

## 2. Endpoints y XML-RPC
- Si no usas apps móviles o Jetpack, deshabilita XML-RPC.
- Limita REST endpoints sensibles (plugins de seguridad o reglas WAF).

## 3. Copias de seguridad consistentes
- Programa backup diario incremental + semanal completo.
- Prueba una restauración parcial (tabla `wp_options`) para validar.

## 4. Monitorización mínima
- Activa logging de errores (WP_DEBUG_LOG en entorno controlado).
- Implementa alerta simple (cron que busque "Fatal error" y envíe correo si aparece).

## 5. Limpieza táctica
- Elimina temas no usados (deja uno por fallback).
- Borra plugins inactivos.
- Revisa la librería de medios por duplicados no referenciados.

## 6. Rendimiento sostenible
- Genera un nuevo Lighthouse para home y una plantilla de post.
- Compara contra la línea base inicial (variación tolerable < 5%).
- Ajusta precarga de fuentes sólo si aporta mejora en LCP.

## 7. Endurecimiento adicional del panel
- Limita intentos de login.
- Ajusta caducidad de sesiones.
- Restringe acceso wp-admin por país/IP si aplica.

## 8. Checklist mínima de contenido
- Define 3 próximas piezas (título + objetivo + CTA).
- Etiqueta borradores con un prefijo para agruparlos (ej: `draft-*`).

## 9. SEO y Discoverability
- Revisa Search Console (cobertura + errores).
- Verifica sitemap generado y accesible.
- Revisa que canonical + hreflang funcionen en nuevas piezas.

## 10. Preparar fase 3 (Optimización continua)
- Documenta lecciones de la primera quincena.
- Lista riesgos pendientes y asigna due date.

---
**Resultado esperado:** Sitio más difícil de comprometer, estable en performance y con backlog de contenido claro.
