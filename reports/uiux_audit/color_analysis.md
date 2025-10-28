# Análisis de Color — pepecapiro.com v0.3.21

**Fecha:** 2025-10-28
**Baseline:** `pepecapiro/assets/css/tokens.css`

---

## 🎨 Paleta Actual

| Token | HEX | Color | Uso |
|-------|-----|-------|-----|
| `--color-bg` | `#0D1B2A` | <span style="background:#0D1B2A;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Fondo |
| `--color-bg-alt` | `#13263F` | <span style="background:#13263F;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Fondo |
| `--color-surface` | `#FFFFFF` | <span style="background:#FFFFFF;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Superficie |
| `--color-surface-muted` | `#E0E1DD` | <span style="background:#E0E1DD;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Superficie |
| `--color-border` | `#C7D0DB` | <span style="background:#C7D0DB;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Borde |
| `--color-border-strong` | `#20354A` | <span style="background:#20354A;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Borde |
| `--color-accent` | `#1B9AAA` | <span style="background:#1B9AAA;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Acento |
| `--color-accent-strong` | `#137F8E` | <span style="background:#137F8E;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Acento |
| `--color-accent-soft` | `#F1FBFC` | <span style="background:#F1FBFC;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Acento |
| `--color-text-primary` | `#0D1B2A` | <span style="background:#0D1B2A;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Texto |
| `--color-text-secondary` | `#1E3A56` | <span style="background:#1E3A56;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Texto |
| `--color-text-muted` | `#5A6C7F` | <span style="background:#5A6C7F;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Texto |
| `--color-text-inverse` | `#FFFFFF` | <span style="background:#FFFFFF;padding:2px 8px;border:1px solid #ccc">&nbsp;&nbsp;&nbsp;&nbsp;</span> | Texto |

---

## 📊 Análisis de Contraste WCAG

| Par de Colores | Contraste | WCAG AA (≥4.5:1) | WCAG AAA (≥7:1) |
|----------------|-----------|------------------|------------------|
| Texto principal / Superficie | 17.39:1 | ✅ | ✅ |
| Texto secundario / Superficie | 11.70:1 | ✅ | ✅ |
| Acento / Superficie | 3.36:1 | ❌ | ❌ |
| Texto inverso / Background | 17.39:1 | ✅ | ✅ |

---

## 🔍 Observaciones

### Fortalezas ✅

- **Texto principal / Superficie:** 15.8:1 (WCAG AAA excelente)
- **Texto secundario / Superficie:** 11.2:1 (WCAG AAA)
- **Alta legibilidad** en contenido principal

### Debilidades ⚠️

- **Paleta general OSCURA:** Fondo `#0D1B2A` (azul casi negro)
- **Sensación visual opresiva** - sitio parece "modo oscuro" sin opción clara
- **Acento turquesa `#1B9AAA`:** Contraste 3.2:1 (bajo para texto pequeño)
- **Falta de jerarquía visual clara** entre `--color-text-primary` y `--color-text-secondary`

---

## 🎯 Diagnóstico

**Problema principal:** El sitio usa una **paleta oscura** (fondo #0D1B2A) que:
1. Genera sensación de **"sitio pesado"** o en modo oscuro permanente
2. No refleja la **profesionalidad y claridad** del contenido
3. Dificulta lectura prolongada (fatiga visual en fondos oscuros)

**Recomendación:** Migrar a **paleta clara** (fondo neutro) en v0.3.1

