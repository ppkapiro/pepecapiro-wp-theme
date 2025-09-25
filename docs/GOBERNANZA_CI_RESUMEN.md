# Gobernanza CI / Automatización de Contenido y Limpieza de Runs

Fecha de corte: 2025-09-25

## 1. Objetivo del Documento
Consolidar en un único punto el estado actual, decisiones, lecciones aprendidas y el plan de evolución de:
- Automatización de publicación de contenido ("publicarlo todo automatizado").
- Observabilidad y verificación post-publicación.
- Gobernanza de pipelines CI (limpieza segura de workflow runs y reducción de ruido).
- Performance / Lighthouse y métricas auxiliares.

Sirve como base para las siguientes iteraciones sin tener que releer hilos previos.

## 2. Contexto Inicial
Problemas detectados al inicio:
- Volumen elevado de *workflow runs* (>150) dificultando inspección manual.
- Necesidad de publicar contenido (posts/pages ES/EN) de forma declarativa sin operaciones manuales en WP.
- Falta de visibilidad inmediata cuando un contenido aparentemente publicado no aparecía en el sitio (posibles caches, estado borrador, etc.).
- Auditorías de performance y SEO operando en paralelo pero sin consolidación de governance para limpieza.

## 3. Cambios Implementados (Cronología Resumida)
| Fecha (aprox) | Cambio | Detalle | Resultado |
|---------------|--------|---------|-----------|
| 2025-09-17/18 | Pipeline publicación contenido | Scripts + verificación `verify_content_live` | Publicación declarativa + comprobación URLs |
| 2025-09-18+   | Observabilidad contenido | Artefactos: `recent_posts.json/md`, `status_mismatches.md` | Diagnóstico rápido de estados WP |
| 2025-09-22     | Lighthouse docs & métricas móvil | Tablas resumen + badge | Métricas centralizadas y versión en docs |
| 2025-09-22/23 | Workflows resumen / prune (borrador) | `runs-summary.yml` y `prune-runs.yml` (dry-run) | Visibilidad de runs antes de borrar |
| 2025-09-23     | Harden GH_TOKEN uso | Export explícito env GH_TOKEN | Eliminación de fallos gh CLI | 
| 2025-09-24     | Artefactos robustos prune | `runs_all.json`, `runs_candidates.json`, `summary.md`, `_all_raw.json` | No pérdida de contexto si total=0 |
| 2025-09-25 (mañana) | Lighthouse push fix | `contents: write` + remote autenticado | Push de tablas OK |
| 2025-09-25 (tarde) | Diagnóstico 404 API runs | Fallback y luego `gh run list` | Eliminado conteo 0 fantasma |
| 2025-09-25 (tarde) | Interpretación filtro 'all' | 'all'/'*' = sin filtro | Lista completa (188 runs) |

## 4. Workflows Clave (Estado Actual)
| Workflow | Propósito | Notas de Seguridad |
|----------|-----------|--------------------|
| `content-sync.yml` | Publicar/actualizar contenido WP desde repo | Usa bandera `.auto_apply` o commit `[publish]` |
| `prune-runs.yml` | Limpieza segura de workflow runs antiguos | Dry-run por defecto, artefactos exhaustivos |
| `runs-summary.yml` | Snapshot agrupado de runs (inventario) | Sólo lectura, GH_TOKEN mínimo |
| `lighthouse.yml` / `lighthouse_docs.yml` | Métricas performance y documentación | Push autenticado, permisos contenidos limitados |
| `seo_audit.yml` | Auditoría SEO técnico | Puede emitir issues o reportes (futuro) |
| `external_links.yml` | Salud de enlaces externos | Alerta temprana enlaces rotos |
| `release.yml` | Empaquetado tema + checksum | Valida versión y changelog |

## 5. Seguridad y Salvaguardas
- `prune-runs` inicia en `dry_run=true` (ningún borrado accidental). 
- Artefactos siempre subidos (incluso sin candidatas o en error parcial).
- Filtrado por nombre optional; palabra clave `'all'` o `'*'` = sin filtro (evita falsas listas vacías).
- Logs incluyen conteo total, candidatas y top 20 listadas.
- Eliminación (cuando se active) evita runs `in_progress` y `queued`.
- Token de Actions sólo con permisos necesarios (`actions: write`, `contents: read`).

## 6. Diagnóstico de Incidencias Resueltas
| Incidencia | Causa Raíz | Fix | Prevención futura |
|------------|-----------|-----|-------------------|
| `gh api .../actions/runs` 404 | Ruta / permisos / contexto git mínimo | Sustituido por `gh run list --repo` | Mantener enfoque CLI estable |
| `runs-summary` fallo token | GH_TOKEN no exportado env | Añadido env en step | Plantilla para futuros workflows |
| Lighthouse push 403 | Falta `contents: write` + remote sin token | Añadir permisos + set-url con token | Checklist permisos CI |
| Total=0 en prune | Endpoint 404 + filtro literal `all` | Interpretar 'all'/'*' como sin filtro + nueva enumeración | Validación pre-borrado |

## 7. Estado Actual (2025-09-25)
- Runs totales visibles: 188 (dry-run keep=12 → 176 candidatas potenciales).
- Publicación de contenido: estable; verificación produce reportes de estado.
- Lighthouse móvil: scores 96–100 (ver tablas en `VALIDACION_MVP_v0_2_1.md`).
- SEO técnico: auditoría habilitada, sin bloqueos críticos.
- Observabilidad: artefactos clave generados en cada pipeline.

## 8. Procedimiento Operativo Actual (Prune)
1. Lanzar manualmente `Prune Old Workflow Runs`.
2. Inputs recomendados iniciales: `workflow=all`, `keep=30`, `dry_run=true`.
3. Revisar artefacto `summary.md` + `runs_candidates.json`.
4. Ajustar `keep` si la concentración por workflow es asimétrica.
5. Para borrado real: `dry_run=false` (sólo tras revisión manual de la lista y quizá guardar backup de `runs_candidates.json`).

## 9. Métricas y Evidencias Generadas
| Artefacto | Fuente | Uso |
|-----------|--------|-----|
| `runs_all.json` | prune-runs | Lista simplificada de runs (post-filtro nombre) |
| `runs_candidates.json` | prune-runs | Objetos potencialmente eliminables |
| `_all_raw.json` | prune-runs | Captura diagnóstica (input base) |
| `summary.md` | prune-runs | Informe humano para PR / revisión |
| `recent_posts.json/md` | content-sync | Observabilidad publicación |
| `verify.md` | verify_content_live | Confirmación URLs y estado HTTP |
| Lighthouse HTML/JSON | lighthouse workflows | Performance y regresiones |

## 10. Riesgos Residuales
| Riesgo | Mitigación Actual | Mejora Propuesta |
|--------|-------------------|------------------|
| Borrado excesivo de un workflow poco frecuente | keep global alto | Retención per-workflow (fase 1) |
| Pérdida de runs fallidos útiles para RCA | Artefacto previo antes de borrar | Retener últimos N fallidos adicionales |
| Crecimiento futuro >400 runs (límite listado) | Límite 400 actual | Paginado multi-llamada / chunking |
| Cambios silenciosos en API gh | Uso comando de alto nivel `gh run list` | Añadir smoke test semanal de enumeración |

## 11. Backlog Propuesto (Priorizado)
| Prioridad | Item | Descripción | Valor |
|-----------|------|------------|-------|
| Alta | Retención per-workflow | Mantener N últimos por cada workflow además del global | Equidad, evita borrados sesgados |
| Alta | Retener fallidos extra | Siempre conservar últimos X con `conclusion!=success` | Mejora RCA | 
| Media | Lista exclusión | No podar `release.yml`, `deploy.yml` | Protección artefactos críticos |
| Media | Schedule semanal | Ejecución automática (cron) dry-run + issue resumen | Consistencia |
| Media | Config central (`.ci_prune.yml`) | Declarar policies sin editar YAML workflow | Reducir fricción |
| Baja | Notificación (Issue/Slack) | Post-run con datos de borrado | Visibilidad |
| Baja | Export histórico runs → JSON | Serie temporal de conteos por workflow | Tendencias |

## 12. Plan Iterativo
### Fase 1 (Gobernanza Mínima Avanzada)
- Implementar retención per-workflow (parámetro `mode=global|per_workflow`).
- Añadir `keep_failed_extra` (ej: 5).
- Campo `exclude_workflows` (regex simple). 
- Validar en dry-run y documentar ejemplo.

### Fase 2 (Automatización & Reporting)
- Programar ejecución semanal (cron) en dry-run.
- Generar issue o comentario consolidado si hay >0 candidates.
- Exportar snapshot `reports/ci_runs/history/<timestamp>.json`.

### Fase 3 (Madurez / Observabilidad Extendida)
- Activar borrado automático condicionado a passing rate >= X% por workflow.
- Añadir dashboard ligero (HTML estático) con: totales, trending, ratio éxito.
- Integrar notificación (Slack/Webhook futuro).

## 13. Acciones Inmediatas Sugeridas
| Acción | Responsable | Estado Propuesto |
|--------|-------------|------------------|
| Ejecutar primera poda real con keep=40 | Ops/Dev | Pendiente (tras revisión) |
| Implementar per-workflow + fallidos | Dev | Próxima iteración |
| Definir lista exclusión (release/deploy) | Dev/Ops | Decidir antes de Fase 1 |
| Proveer API key PSI dedicada | Cliente | Pendiente |

## 14. Cómo Integrar Nuevas Políticas
1. Editar futuro archivo `.ci_prune.yml` (cuando se implemente) con:
```yaml
mode: per_workflow
keep_global: 40
per_workflow_keep: 15
keep_failed_extra: 5
exclude_workflows: ["release", "deploy"]
```
2. Lanzar `prune-runs` en dry-run para verificar resumen.
3. Revisar `summary.md` → si ok, re-lanzar con `dry_run=false`.

## 15. Lecciones Aprendidas
- Siempre capturar raw antes de filtrar (facilita RCA de listas vacías).
- Uso explícito de GH_TOKEN evita dependencias implícitas frágiles.
- Dry-run obligatorio en primera adopción reduce riesgo y aumenta confianza.
- Documentar inputs dentro del propio workflow agiliza la operación.

## 16. Glosario Rápido
| Término | Definición |
|---------|-----------|
| Dry-run | Ejecución que simula y no borra realmente |
| Candidate | Run elegible para borrado según política |
| Per-workflow retention | Mantener N runs por cada workflow en vez de un pool global |

## 17. Referencias
- `README.md` (visión general)
- `VALIDACION_MVP_v0_2_1.md` (métricas lighthouse recientes)
- Directorio `.github/workflows/` (implementaciones actuales)
- Reportes generados: `reports/` y `docs/`

---
Fin del documento. Mantener este archivo actualizado por commit atómico cuando se modifique la política.
