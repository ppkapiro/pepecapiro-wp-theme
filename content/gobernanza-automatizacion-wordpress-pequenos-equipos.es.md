# Gobernanza y Automatización de WordPress para Pequeños Equipos

> Cómo sostener velocidad sin perder control cuando sólo sois 1–3 personas.

## Resumen Ejecutivo
La clave: decidir explícitamente qué NO harás todavía. Un marco ligero de 5 pilares permite crecer con menos fuego.

## 1. Código y Activos
- Repositorio único del tema + scripts
- Versionado semántico (CHANGELOG disciplinado)
- Commits pequeños → despliegues pequeños
- Fuentes, imágenes críticas y CSS controlados (no depender de CDNs arbitrarios)

## 2. Contenido
- Automatizar creación idempotente (posts/pages bilingües) vía API
- Markdown fuente versionado → reproducibilidad
- Slugs estables, evitar renombrar
- Auditoría: script compara hash de contenido

## 3. Entregas y CI
- Pipeline: build -> validaciones -> deploy
- Health checks: página blog lista, markers detectables
- Releases empaquetadas (.zip + .sha256)
- Revisión rápida: Lighthouse programado

## 4. Observabilidad Ligera
- Logs de despliegue retenidos
- Métrica mínima: tiempo de respuesta home/blog
- Chequeo CRON de salud (HTTP 200 + posts_found)
- Alertas sólo en fallos críticos

## 5. Riesgo y Cambios
- Regla de “1 cambio funcional por release” cuando hay incertidumbre
- Feature flags simples (opciones WP + condicionales del tema)
- Backups automáticos diarios verificados
- Política de rollback: reinstalar zip previo verificado

## Flujo Diario Propuesto
1. Crear branch corta (feature/blog-categorias)
2. Ajuste + markdown de contenido
3. Ejecutar script de publicación (idempotente)
4. Revisar health + Lighthouse
5. Merge + tag versión
6. Deploy automático

## Métricas de Salud Iniciales
| Métrica | Objetivo | Frecuencia |
|--------|----------|------------|
| Tiempo TTFB | < 600ms | Diario |
| Lighthouse móvil | ≥ 90 | Semanal |
| Fallos health check | 0 | Continuo |
| Releases fallidas | 0 | Por release |

## Antipatrón Clave
“Subo cambios manuales por FTP” → no auditable, no reversible, no escalable.

## Próximos Incrementos
- Test visual ligero (capturas diffs básicas)
- Cache de objeto (Redis) si aumenta complejidad
- Monitor sintético de formulario

---
Gobernanza no es burocracia: es reducir fricción futura al documentar decisiones mínimas ahora.
