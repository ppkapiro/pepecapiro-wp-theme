# Métricas, Observabilidad y Performance

Este documento define cómo medimos, almacenamos, analizamos y mejoramos el rendimiento y la salud del sitio.

## 1. Objetivos
- Estabilidad: detectar regresiones temprano.
- Comparabilidad: formatos y rutas consistentes.
- Acción: cada métrica tiene umbral y owner.

## 2. Superficie de Métricas
| Dominio | Métricas | Fuente | Artefacto |
|---------|---------|--------|-----------|
| Performance sintética | Score móvil, LCP, TTI, INP (cuando disponible) | Lighthouse CLI | `docs/lighthouse/<fecha>/` (HTML/JSON) |
| Performance PSI | LCP (field), INP (field), FCP, CLS | PageSpeed Insights API | `metrics/psi_raw/*.json` |
| Contenido | Drift hash, acciones (create/update/skip) | `publish_content.py` | `content_plan_summary.md`, `drift_report.md` |
| Media | Reutilización (%) | `.media_map.json` | Derivado (script futuro) |
| Deploy | Integridad (mismatches) | Integridad post‑deploy | `_scratch/integrity_ci.log` |

## 3. Estructura de Directorios
```
docs/lighthouse/            # Reportes HTML/JSON organizados por fecha
metrics/psi_raw/            # Respuestas JSON sin procesar de PSI
metrics/derived/            # (Futuro) Series temporales agregadas
content/                    # Plan/drift/media_map
```

## 4. Recolección Lighthouse CLI (Fase 1)
Script objetivo: `scripts/collect_lighthouse.py`
- Input: lista de URLs (`configs/lh_urls.txt`)
- Flags: `--mobile` (preset), `--output-dir docs/lighthouse/2025-09-25/`
- Output por URL: `<slug>.report.html`, `<slug>.report.json`
- Tabla agregada: `docs/lighthouse/index.html` (generada/actualizada)

Estado: pendiente de implementación.

## 5. Recolección PSI API (Fase 2)
Script objetivo: `scripts/collect_psi.py`
- Require env: `PSI_API_KEY`
- Rate limit: retry exponencial si 429 (máx 3 reintentos)
- Output bruto: `metrics/psi_raw/<fecha>_<slug>.json`
- Parser derivado (futuro): consolida en `metrics/derived/psi_summary_<fecha>.json`

## 6. Quality Gates (Fase 3)
Preflight antes de apply contenido:
| Gate | Script | Falla si |
|------|--------|---------|
| Links internos | `scripts/preflight_links.py` | HTTP !=200 en enlaces locales críticos |
| Categorías | `scripts/preflight_taxonomies.py` | Categoría declarada no existe y no puede crearse |
| Integridad Markdown | `scripts/preflight_content_completeness.py` | Falta markdown requerido para idioma activo |

Salida común: `preflight_report.md` (status PASS/FAIL + detalles). El workflow aborta si FAIL.

## 7. Umbrales Iniciales
| Métrica | Umbral | Acción si falla |
|---------|--------|-----------------|
| Lighthouse móvil Home | < 90 | Issue + plan reducción peso fuentes/images |
| LCP sintético Home | > 2.5s | Revisar imágenes LCP / critical CSS |
| LCP campo (PSI) | > 2.5s p75 | Investigación causas reales (caching, TTFB) |
| Drift inesperado | >0 items | Revisar ediciones manuales WP |
| Media reutilización | <50% | Analizar naming / hashes repetidos |

## 8. Backlog Métricas (Futuro)
- CLS real (field) y comparativa semanal.
- INP real cuando haya suficiente tráfico.
- Serie temporal de acciones (create/update/skip) para detectar olas atípicas.
- Tamaño medio de HTML y conteo de assets por página (script HEAD consolidado).

## 9. Flujo de Evolución
1. Fase 1: Lighthouse CLI estable + tabla agregada.
2. Fase 2: PSI API con clave y persistencia.
3. Fase 3: Quality Gates integrados.
4. Fase 4: Derivados/series y alertas (issues automáticas si brecha >N runs).

## 10. Tabla de Estado (Resumen)
| Item | Estado | Próximo Paso |
|------|--------|--------------|
| Release 0.3.18 | Preparación | Cerrar fecha/tag |
| Lighthouse CLI | Planificado | Implementar script F1 |
| PSI API | Planificado | Script + clave env |
| Quality Gates | Planificado | Implementar 3 scripts |
| Breadcrumbs JSON-LD | Pendiente | Diseño esquema |
| Últimas Entradas widget | Pendiente | Shortcode o template part |
| Auditoría hreflang/canonical | Pendiente | Script HEAD + parse DOM |
| Primer post real ES/EN | Pendiente | Definir contenido y publicar |

## 11. Roles / Ownership
| Área | Owner | Escalado |
|------|-------|----------|
| Contenido declarativo | Repo maintainer | Issue etiquetado content |
| Performance sintética | Repo maintainer | Issue perf + labeling |
| PSI field | Repo maintainer | Igual |
| Calidad preflight | Repo maintainer | Fail interrumpe pipeline |

## 12. FAQ
- ¿Por qué separar Lighthouse y PSI? Lighthouse = laboratorio; PSI añade datos de campo + puede diferir por red real y dispositivos.
- ¿Necesito todos los HTML? Sí, sirven para auditoría manual e histórico visual.

---
Documento vivo. Actualizar al completar cada fase.
