# Fase 2 — Gate visual y accesibilidad

Generado: 2025-10-27

Este gate valida la consolidación del sistema de diseño (tokens + estilos) y su calidad en producción móvil.

## Checklist rápida (debe quedar en PASS)

- [x] CSS sin hex fuera de `pepecapiro/assets/css/tokens.css` (enforced por script).
- [x] Enlaces y botones con `:focus-visible` claro (ring visible y contraste AA).
- [x] CTAs primario/secundario usan tokens (`--color-accent`, `--color-text-inverse`).
- [x] Hero y footer respetan `--max-width-content`, espaciado `--space-*` y grid responsive.
- [x] No hay valores “mágicos” de padding/margin; todo via `--space-*`.
- [x] Formularios con focus y labels visibles; placeholders no son el único descriptor.

## Validaciones automáticas locales

1) Hex colors fuera de tokens

```bash
python scripts/ci/check_css_tokens.py
```

Esperado: `PASS` sin rutas listadas.

También disponible como tarea de VS Code: "UI Gate: Anti-hex CSS".

2) URLs a auditar (móvil)

- Archivo: `configs/lh_urls.txt` (ES/EN para Home, Sobre mí, Proyectos, Recursos, Contacto).
- Config: `lighthouserc.json` (emulación móvil y throttling documentado).

## Auditoría Lighthouse en CI

Usa cualquiera de estos workflows:

- Lighthouse Mobile Audit: `lighthouse.yml` (artefacto `lighthouse_reports`).
- Lighthouse Mobile + Docs: `lighthouse_docs.yml` (artefactos `lhci_raw`, `reports_after`).
- CSS anti-hex en PRs: `ui-gates.yml` (falla si hay hex fuera de tokens).

Ejemplo manual (requiere GitHub CLI autenticado):

```bash
gh workflow run lighthouse_docs.yml --field urls_file=configs/lh_urls.txt
gh run watch --exit-status
gh run download -p reports_after
```

Umbrales de referencia: `configs/perf_thresholds.json` (Lighthouse móvil ≥90, LCP ≤2.5 s).

## Evidencia

- Capturas actualizadas:
  - Desktop: `evidence/ui/home-desktop-20251027.png`
  - Mobile: `evidence/ui/home-mobile-20251027.png`
- Reporte de deuda actualizado: `reports/deuda_visual.md` (sección “Evidencia”).

### Nota sobre Lighthouse
- La ejecución en GitHub Actions quedó bloqueada por límites de facturación (ver anotación del run). Se dejó configurado `ui-gates.yml` y los workflows `lighthouse*.yml` listos.
- Intento local con `scripts/ci/run_lighthouse_local.py` falló por limitaciones del entorno (DevTools connection en headless Chrome). El script y estructura de reportes quedan disponibles en `reports/lighthouse/` para volver a ejecutar en entorno con Chrome estable.

## Criterio de cierre

1) Script anti-hex en PASS.
2) Lighthouse móvil en PASS (todas las URLs >= umbral configurado).
3) Checklist visual marcada en PASS y evidencia adjunta.
