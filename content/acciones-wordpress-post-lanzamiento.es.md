# WordPress Post‑Lanzamiento: 7 Acciones Clave en los Primeros 7 Días

Un sitio recién publicado suele estar “correcto” pero no optimizado. Esta checklist prioriza acciones de alto impacto (defensa, rendimiento, observabilidad y gobernanza) que consolidan la base antes de escalar contenido o tráfico.

## 1. Endurecer superficie de acceso
**Problema:** Exposición innecesaria del login y credenciales débiles.
**Acción:** Forzar contraseñas fuertes, activar 2FA para cuentas con rol alto, limitar intentos (fail2ban/Nginx rate limit) y mover `/wp-admin` detrás de una regla de WAF/IP si es viable.
**Resultado:** Menor vector de ataque automatizado y reducción de ruido en logs.

## 2. Congelar plugins innecesarios y depurar
**Problema:** Bloat = más superficie, más consultas, más vulnerabilidades.
**Acción:** Inventario → clasificar (core, imprescindible, prescindible). Desactivar y eliminar lo prescindible. Registrar decisión en control de versiones (README sección plugins/justificación).
**Resultado:** Menor TTFB, menos CVEs potenciales, ciclo de actualización más simple.

## 3. Cache y política de activos críticos
**Problema:** Carga lenta inicial y recursos estáticos sin caducidad clara.
**Acción:** Activar page cache (Object cache si aplica), definir headers `cache-control` para CSS/JS/imagenes (hash en filename), evaluar precarga de fuentes críticas (`preload`) sólo si reduce LCP medible.
**Resultado:** Mejor LCP y menor carga del servidor bajo picos.

## 4. Observabilidad mínima y métricas de rendimiento
**Problema:** No detectar regresiones hasta que son visibles para usuarios.
**Acción:** Configurar pipeline Lighthouse + PSI (ya integrado) y establecer thresholds explícitos (`perf_thresholds.json`). Guardar histórico y activar auto‑issues.
**Resultado:** Detección temprana y base para decisiones basadas en datos.

## 5. Protección de contenido y medios
**Problema:** Subidas duplicadas y media no versionada provocan caos y tamaño excesivo en backups.
**Acción:** Uso de deduplicación por hash (`.media_map.json`), convención de nombres, alternativa de CDN si escala. Revisar periódicamente el reporte de reutilización.
**Resultado:** Librería limpia + backups más rápidos.

## 6. Hardening de configuración y escaneo rápido
**Problema:** Config inicial sin validación de archivo ni integridad.
**Acción:** Verificar `DISALLOW_FILE_EDIT`, asegurar salts, forzar HTTPS, comprobar no hay archivos de instalación residuales (`wp-admin/install.php` bloqueado). Escaneo rápido con herramienta externa (wpscan o similar) y registrar hallazgos.
**Resultado:** Base alineada a buenas prácticas y documentación verificable.

## 7. Definir ciclo de publicación automatizado
**Problema:** Cambios manuales en panel generan divergencias difíciles de rastrear.
**Acción:** Consolidar “contenido como código” (este repo): plan/apply, preflight gates (links, taxonomías, completitud), soft gating performance y auto‑issues.
**Resultado:** Operación predecible, auditable y escalable con poco capital humano.

## Checklist Rápida
- [ ] 2FA y rate limit login
- [ ] Plugins inventariados y bloat removido
- [ ] Cache + headers estáticos activos
- [ ] Thresholds PSI definidos y monitoreados
- [ ] Media deduplicada y reporte revisado
- [ ] Config endurecida (salts, HTTPS, file edit off)
- [ ] Pipeline de publicación sin acciones manuales ad‑hoc

## Métricas Clave a Vigilar
- LCP móvil (objetivo < 2.5s, ideal < 2.0s)
- CLS (< 0.1 consistente)
- Reutilización media (ratio creciente)
- Drift de contenido (0 inesperado)
- Corridas consecutivas con fallos de thresholds (evitar escalado)

## Próximo Paso
Tras estos 7 días, enfocar en SEO técnico avanzado (JSON-LD, hreflang) y pruebas de carga ligeras.

---
*Este artículo forma parte de la serie de gobernanza y automatización continua del sitio.*
