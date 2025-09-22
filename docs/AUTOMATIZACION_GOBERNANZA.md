# Propuesta de Automatización y Gobernanza — pepecapiro.com

## 0) Mensaje para la organización (listo para enviar)
Equipo, a partir de hoy formalizamos el flujo de validación y publicación de métricas del sitio **pepecapiro.com**:
- **Salida oficial**: https://ppkapiro.github.io/pepecapiro-wp-theme/docs/index.html
- **Reportes de Lighthouse (móvil)**: https://ppkapiro.github.io/pepecapiro-wp-theme/docs/lighthouse/index.html
- **Informe de validación**: /docs/VALIDACION_MVP_v0_2_1.md
- **Plan siguiente release (v0.3.0)**: /docs/PLAN_v0_3_0.md

**Roles**
- **Regulador** (Pepe): define umbrales, aprueba cierres de versión, prioriza mejoras.
- **Secretario** (ops): ejecuta el workflow, actualiza documentos, prepara evidencia, levanta incidencias.

**Umbrales (MVP v0.2.1)**  
- Perf móvil ≥ 90 en **/** y **/en/**; LCP ≤ 2.5s en todas las páginas.

**Ritmo**
- Semanal: auditoría automática (cron) + actualización de docs.
- Ad-hoc: se puede disparar manualmente ante cambios relevantes.

## 1) RACI (rápido)
- **Definir umbrales**: Regulador (R/A); Secretario (C).
- **Ejecutar auditorías**: Secretario (R); Regulador (I).
- **Actualizar docs/tabla**: Secretario (R); Regulador (I).
- **Decidir cierre de release**: Regulador (A); Secretario (C).

## 2) GitHub Actions — Workflow unificado (programado + manual)
Colocar en: `.github/workflows/lighthouse_docs.yml`  
Requiere Pages con /docs habilitado. Usa GITHUB_TOKEN con contents: write.

```yaml
name: Lighthouse Mobile + Docs

on:
  workflow_dispatch:
  schedule:
    - cron: "0 13 * * 1"   # Lunes 13:00 UTC (ajustar si conviene)

permissions:
  contents: write
  actions: read

jobs:
  audit-and-update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      # (Ejemplo) Instala tu runner de Lighthouse o usa PSI si prefieres API.
      # Aquí asumimos que ya tienes script que genera JSON/HTML en ./lighthouse_reports
      - name: Install deps
        run: |
          npm -v || true
          python3 --version || true
          sudo apt-get update -y
          sudo apt-get install -y jq

      - name: Run Lighthouse (placeholder)
        run: |
          mkdir -p lighthouse_reports
          # Sustituir por tu comando real; si ya usas un action propio, invócalo aquí.
          # Ejemplo (falso): node scripts/run_lighthouse_ci.js
          echo '{}' > lighthouse_reports/home.json
          echo '<html>demo</html>' > lighthouse_reports/home.html

      - name: Publicar reportes en docs/lighthouse
        run: |
          mkdir -p docs/lighthouse
          cp -f lighthouse_reports/*.html docs/lighthouse/ || true

      - name: Resumir a Markdown (actualiza VALIDACION_MVP_v0_2_1.md)
        run: |
          python3 scripts/summarize_lh_to_md.py

      - name: Ajustar enlaces y notas (asegurar navegación)
        run: |
          # Asegura referencia a index de Lighthouse y landing Docs
          if grep -q "Índice navegable de reportes" docs/VALIDACION_MVP_v0_2_1.md; then
            echo "[i] Nota de navegación ya presente."
          else
            printf "\n> **Índice navegable de reportes:** ver \`docs/lighthouse/index.html\`.\n" >> docs/VALIDACION_MVP_v0_2_1.md
          fi

      - name: Commit [skip ci] si hay cambios
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/lighthouse/ docs/VALIDACION_MVP_v0_2_1.md || true
          if ! git diff --cached --quiet; then
            git commit -m "docs: actualizar Lighthouse y navegación [skip ci]"
            git push origin ${{ github.ref_name }}
          else
            echo "[i] Sin cambios para commitear."
          fi
```

### Alternativa si tu repo exige PAT (ramas protegidas)
Crear un PAT con `contents:write` como secret: `PAT_CONTENTS` y reemplazar el paso de commit por un push autenticado con token (ver plantilla en la propuesta original).

## 4) Runbook (Secretario)
- Disparo manual: Actions → "Lighthouse Mobile + Docs" → Run workflow.
- Verificar job y notificar al Regulador con:
  - Docs landing: `/docs/index.html`
  - Informe: `/docs/VALIDACION_MVP_v0_2_1.md`
  - Índice LH: `/docs/lighthouse/index.html`

## 5) SLAs y alarmas ligeras
- Si perf Home < 90 o LCP > 2.5s:
  - Secretario etiqueta `incidencia-perf` y sugiere quick wins.
  - Regulador prioriza (24–48h) y aprueba plan.

## 6) Escalada futura
- Integrar PSI (API) para runs más realistas.
- Añadir "gates" (fallar CI si umbrales no se cumplen).
- Despliegues condicionados (solo publicar si perf ≥ N).

## 7) Variables a confirmar (1 minuto)
- Usuario/repo GitHub para fijar URLs definitivas (ya aplicado: `ppkapiro/pepecapiro-wp-theme`).
- Si `main` está protegida, usar PAT o excepciones para el bot.
