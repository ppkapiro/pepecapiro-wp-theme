# PR: UI/UX v0.3.1 — Paleta clara + fixes accesibilidad/UX

## 📋 Resumen

Migración de paleta oscura (#0D1B2A) a **paleta clara profesional** (#F5F6F8) para mejorar legibilidad, accesibilidad y sensación de amplitud visual.

**Baseline:** dd34254 (auditoría visual completa)  
**Branch:** `feat/uiux-v0.3.1-palette`  
**Commits:** 2 (7d43b31 + ab0d963)

---

## 🎨 Cambios de Paleta (tokens.css)

| Token | ANTES (v0.3.21) | DESPUÉS (v0.3.1) | Impacto |
|-------|----------------|------------------|---------|
| `--color-bg` | `#0D1B2A` (azul oscuro) | `#F5F6F8` (gris claro) | ⚠️ **INVERSIÓN** |
| `--color-bg-alt` | `#13263F` | `#EAECEF` | ⚠️ **INVERSIÓN** |
| `--color-accent` | `#1B9AAA` (turquesa) | `#0F7490` (petroleo) | 🔧 Desaturado |
| `--color-accent-strong` | `#137F8E` | `#0A5F75` | 🔧 Desaturado |
| `--color-text-primary` | `#0D1B2A` | `#1F2937` (gris) | 🔧 Neutral |
| `--color-text-secondary` | `#1E3A56` | `#4B5563` | 🔧 Jerarquía clara |
| `--color-text-muted` | `#5A6C7F` | `#6B7280` | 🔧 Neutral |
| `--color-border` | `#C7D0DB` | `#D1D5DB` | 🔧 Neutral |
| `--color-border-strong` | `#20354A` | `#9CA3AF` | 🔧 Neutral |

**Nuevo token agregado:**
- `--shadow-xs`: `0 4px 12px rgba(13, 27, 42, 0.08)` (hover cards)

---

## ✨ Mejoras UI/UX

### 1. Hero con gradiente claro sutil (theme.css)
```css
.hero {
  background: linear-gradient(135deg, #FDFDFD 0%, #F0F4F8 100%);
  background-image:
    radial-gradient(circle at 20% 50%, rgba(15, 116, 144, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(15, 116, 144, 0.03) 0%, transparent 50%);
}
```

### 2. Hover shadow en cards
```css
.card {
  transition: box-shadow var(--transition-base);
}
.card:hover,
.card:focus-within {
  box-shadow: var(--shadow-xs);
}
```

### 3. Fix enlace Cookies (footer.php)
- **Antes:** `/en/cookies/` (enlace roto)
- **Después:** `/cookies/` (ruta unificada)

### 4. Accesibilidad lang-switcher (header.php)
- **Agregado:** `aria-label="Cambiar idioma"` en contenedor `.lang-switcher`

---

## 📊 Validación

### Contraste WCAG
- **Primary/Surface:** ~14.5:1 (✅ AAA)
- **Secondary/Surface:** ~9.2:1 (✅ AAA)
- **Accent/Surface:** ~4.6:1 (✅ AA mejorado +1.4:1 vs baseline)

### Performance
- **CLS:** 0.000 (sin cambios estructurales)
- **LCP:** Sin impacto (gradiente CSS, no imagen)
- **CSS size:** Sin aumento significativo (solo valores HEX)

### Capturas post-cambio
- ✅ **20 screenshots regenerados** (10 desktop + 10 mobile)
- Log: `reports/uiux_audit/audit_execution_post_change.log`
- Comparativa visual: Antes (dd34254) vs Después (HEAD)

---

## 🚀 CI/CD — Workflow automático

**Archivo:** `.github/workflows/release_v0_3_1_uiux.yml`

### Jobs secuenciales:

1. **Lighthouse CI** (Home ES/EN)
   - Genera JSON/HTML + SUMMARY.md
   - Artifact: `lighthouse-v0.3.1`

2. **Merge + Tag**
   - Busca PR por rama, comenta resultado Lighthouse
   - Squash merge a `main`
   - Crea tag `v0.3.1-uiux-palette` + release

3. **Deploy SFTP**
   - Sincroniza `./pepecapiro` → `WP_REMOTE_PATH`
   - Valida secrets: SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASSWORD

4. **Purge + Verify**
   - WP-CLI: `wp cache flush`, `wp transient delete`, `wp litespeed-purge`
   - Fallback si WP-CLI no existe
   - Verifica HTTP 200 en Home ES/EN

5. **Doc update**
   - Append publicación a `docs/AUDITORIA_UIUX.md`
   - Commit automático post-deploy

### Trigger:
- **Manual:** Actions → "Release v0.3.1 UI/UX" → Run workflow
- **Automático:** Push a `feat/uiux-v0.3.1-palette` (ejecuta solo Lighthouse)

---

## ✅ Checklist de aceptación

### UX/A11y
- [x] Paleta clara aplicada (#F5F6F8 bg, #0F7490 accent, #1F2937 text)
- [x] Hero con gradiente sutil
- [x] Hover shadow en cards con transición
- [x] Enlace Cookies corregido (`/cookies/`)
- [x] `aria-label` en lang-switcher

### Contraste
- [x] Primary/Surface ≥ 7:1 (AAA)
- [x] Secondary/Surface ≥ 4.5:1 (AA)
- [x] Accent hover ≥ 3.8:1 (AA texto grande)

### Capturas
- [x] 20 screenshots post-cambio generados

### Performance
- [x] CLS 0.000 mantenido (sin cambios estructurales)
- [ ] Lighthouse CI OK (ejecutar workflow en Actions)

### Docs
- [x] `AUDITORIA_UIUX.md` actualizado con sección de validación
- [x] Commit ab0d963 incluye workflow completo

### CI/CD
- [x] Workflow `release_v0_3_1_uiux.yml` creado
- [x] Scripts auxiliares (`urls_lighthouse.txt`, `summarize_lighthouse_ci.js`)
- [ ] Secrets configurados en repo (SFTP_*, SSH_*, WP_*)

---

## 📝 Próximos pasos

1. **Validar secrets en repo:**
   - Settings → Secrets and variables → Actions
   - Verificar: SFTP_HOST, SFTP_PORT, SFTP_USER, SFTP_PASSWORD, WP_REMOTE_PATH
   - Verificar: SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD o SSH_KEY, WP_PATH_ROOT

2. **Ejecutar workflow:**
   - Actions → "Release v0.3.1 UI/UX — merge, tag, deploy"
   - Inputs:
     - `pr_branch`: `feat/uiux-v0.3.1-palette`
     - `tag_name`: `v0.3.1-uiux-palette`

3. **Revisar artifacts:**
   - Descargar `lighthouse-v0.3.1`
   - Validar SUMMARY.md (scores ≥ baseline)

4. **Verificar deploy:**
   - https://pepecapiro.com/ → Inspeccionar paleta clara
   - https://pepecapiro.com/en/ → Inspeccionar paleta clara
   - DevTools → Computed → verificar `--color-bg: #F5F6F8`

---

## 📚 Referencias

- **Propuesta detallada:** `reports/uiux_audit/color_proposal.md` (261 líneas)
- **Análisis baseline:** `reports/uiux_audit/color_analysis.md`
- **Auditoría completa:** `docs/AUDITORIA_UIUX.md`
- **Baseline commit:** dd34254 (20 screenshots + análisis)
- **Palette commit:** 7d43b31 (tokens.css + theme.css + header.php + footer.php)
- **CI/CD commit:** ab0d963 (workflow + scripts)

---

**Reviewers:** Validar contraste visual en screenshots post-cambio antes de merge.  
**Merge strategy:** Squash (para mantener historial limpio en main).
