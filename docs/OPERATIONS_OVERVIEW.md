# Operaciones y Gobernanza

## 1. Objetivo
Centralizar prácticas operativas: performance, salud, auditorías y criterios de calidad continua.

## 2. Cadencia y Roles
- Auditorías Lighthouse programadas (cron) + disparos manuales.
- Salud sitio (listados blog, páginas legales, home) monitorizada vía workflows.
Roles (ligero): Propietario (define umbrales), Operador (ejecuta y actualiza).

## 3. Métricas Clave
| Métrica | Umbral inicial | Fuente |
|---------|----------------|--------|
| Performance móvil Home | ≥ 90 | Lighthouse HTML |
| LCP | ≤ 2.5s | Lighthouse / Field (futuro) |
| Integridad deploy | 0 mismatches | `integrity_ci.log` |
| Hash drift contenido | 0 divergencias inesperadas | `drift_report.md` |

## 4. Workflows Relevantes
| Workflow | Propósito |
|----------|-----------|
| `content-sync.yml` | Plan/apply contenido + artifacts |
| `deploy.yml` | Despliegue tema + integridad |
| `lighthouse*.yml` | Auditorías performance |
| `site-health.yml` | Salud periódica (endpoints clave) |
| `status.yml` | Estado rápido (pings/básicos) |

## 5. Salud del Blog Bilingüe
`scripts/blog_health_ci.sh` asegura:
- Páginas listado ES/EN 200
- Marker `posts_found` y `lang` presentes
- Plantilla correcta

## 6. Gestión de Contenido
- Declarativo (JSON + Markdown). Cambios fuera del repo = riesgo de drift.
- Usar siempre `[publish]` o `.auto_apply` para consistencia.

## 7. Checklist Rápida de Operaciones
1. Revisar `CHANGELOG.md` antes de tag.  
2. Ejecutar dry-run de contenido (`--dry-run`) y revisar plan.  
3. Tag y desplegar.  
4. Verificar `integrity_ci.log` + blog health.  
5. Lighthouse si cambio estructural.  
6. Opcional: `--drift-only` semanal.

## 8. Mejora Continua (Backlog Operativo)
- Automatizar SEO canónicas/hreflang checks.
- Añadir trending de métricas (persistir JSON histórico). 
- Alertas ligeras (issue automática si LCP > umbral 2 runs seguidos).

## 9. Observabilidad & Métricas
Documento base: `docs/PERFORMANCE_METRICS.md`.

| Dominio | Estado | Próximo paso |
|---------|--------|--------------|
| Lighthouse CLI | Planificado | Implementar script F1 |
| PSI API | Planificado | Añadir clave y recolector |
| Quality Gates preflight | Planificado | Scripts links/categorías/completitud |
| Media reutilización | Pendiente | Script derivado |
| Breadcrumbs JSON-LD | Pendiente | Generar y validar schema |

Umbrales activos actuales se mantienen en la tabla de Métricas Clave; evolución y backlog detallado en el documento dedicado.
