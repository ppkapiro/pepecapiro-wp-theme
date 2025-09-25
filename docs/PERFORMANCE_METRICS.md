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

Estado: COMPLETADO (script + workflow + ejecuciones; índice generado).

## 5. Recolección PSI API (Fase 2)
Script: `scripts/collect_psi.py`
- Usa lista `configs/lh_urls.txt` (misma que Lighthouse)
- Ejecuta estrategias: mobile y desktop
- Salida actual: `reports/psi/YYYYMMDD/HHMMSS/` con `summary.json`, `summary.md` + JSON individuales y `reports/psi/index.(json|html)` histórico
- Retry exponencial simple; errores no rompen CI (exit 0)

### 5.1 Thresholds Evaluados
Archivo: `configs/perf_thresholds.json`
Ejemplo:
```json
{
  "psi": {
    "mobile": {"performance_min": 90, "lcp_max_ms": 2500, "cls_max": 0.1},
    "desktop": {"performance_min": 95, "lcp_max_ms": 1800, "cls_max": 0.05}
  }
}
```
El script añade sección `evaluations` en `summary.json` con pass/fail por métrica. No rompe CI (exit 0); futuras fases podrían convertir fallos críticos en issues automáticas.

Estado: IMPLEMENTADO (pendiente observación primeras corridas y ajuste de campos derivados).

### 5.2 Auto‑Issues Thresholds
Cuando una corrida PSI produce `evaluations.<strategy>.passes = False`, el script `scripts/psi_threshold_issue.py` crea (si no existe) un issue titulado "PSI Thresholds Fallidos en último run" con detalles de checks y promedios. Evita duplicados buscando issues abiertas con mismo título. No rompe CI si falla la creación.

### 5.3 Timeseries & Badge
El script PSI genera ahora:
- `reports/psi/timeseries.json` (array acotado últimas 500 corridas)
- `reports/psi/badge_mobile_performance.json` (schemaVersion=1 consumible por shields.io)

### 5.4 Media Reuse
`media_reuse_report.{json,md}` (ratio reutilización hashes media) generado en corrida PSI. Fuente: `content/.media_map.json`.

### 5.5 Soft Gating
`performance_advisory.py` imprime líneas `PERF_ADVISORY:` en `content-sync` (no bloquea). Sirve para visibilidad inmediata antes de publicar contenido.

### 5.6 Escalado Prioritario
Si hay ≥2 corridas consecutivas fallando thresholds, el issue se crea/actualiza con label `priority:high`.

## 6. Quality Gates (Fase 3)
Integrados en workflow `content-sync.yml` antes de validaciones de esquema.
| Gate | Script | Falla si | Salida |
|------|--------|---------|--------|
| Links internos | `scripts/preflight_links.py` | HTTP >=400 | `preflight_links.json/md` |
| Categorías | `scripts/preflight_taxonomies.py` | Categorías declaradas faltantes | `preflight_taxonomies.json/md` |
| Completitud contenido | `scripts/preflight_content_completeness.py` | Campos obligatorios/duplicados | `preflight_content.json/md` |
Estado: IMPLEMENTADO (artefacto agregado `preflight-quality-gates`).

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
| Release 0.3.18 | Cerrado | — |
| Lighthouse CLI | Completado | Ajustar thresholds si cambian patrones |
| PSI API | Completado | Añadir series derivadas | 
| Quality Gates | Completado | Posible reporte unificado |
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
