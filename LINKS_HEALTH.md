# Auditoría de Enlaces Externos

Este módulo monitoriza salud de enlaces externos publicados para reducir UX roto y pérdida de autoridad.

## Flujo
1. Descubrimiento de páginas públicas (home por idioma + posts publicados vía REST Polylang).
2. Extracción de enlaces `<a href>`.
3. Filtrado (ignora `mailto:`, `tel:`, anchors internos, patrones configurados en `configs/link_scan.json`).
4. Clasificación: interno / externo.
5. Dedupe por URL absoluta.
6. HEAD (fallback GET) para estado HTTP.
7. Métricas y umbral de fallo (`failure_threshold_percent`).
8. Reportes: `reports/links/scan.json` y `scan.md`.

## Configuración (`configs/link_scan.json`)
```jsonc
{
  "timeout_seconds": 8,
  "concurrency": 12,
  "retry": 1,
  "failure_threshold_percent": 5,
  "ignore_patterns": ["mailto:", "tel:", ".*\\.pdf$"],
  "internal_domain": "pepecapiro.com"
}
```

## CI
Workflow: `.github/workflows/external_links.yml`
- Cron diario 04:29 UTC.
- Ejecutable manual (`workflow_dispatch`).
- Falla si porcentaje de enlaces externos rotos supera umbral.
- Artifacts: carpeta `reports/links/`.

## Extensiones futuras
- Cache de resultados (ETag/Last-Modified) para reducir tiempo.
- Reintentos exponenciales diferenciados por tipo de error.
- Clasificación severidad (404 vs 500 vs timeout).
- Auto-creación de issue con histórico (similar a PSI) si supera umbral 2 veces seguidas.

---
Generado por fase de gobernanza de enlaces externos.
