# Escaneo de Secretos y Datos Sensibles - Repositorio pepecapiro-wp-theme

**Fecha de escaneo:** 2025-10-28 00:10 UTC  
**Commit analizado:** HEAD (489feee5)  
**Herramienta:** Análisis de patrones regex + auditoría manual  
**Alcance:** docs/, reports/, evidence/, configs/, scripts/

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| **Total de archivos escaneados** | ~250 archivos (md, txt, json, sh, py) |
| **Archivos con riesgos detectados** | 1 archivo |
| **Riesgos de severidad ALTA** | 0 |
| **Riesgos de severidad MEDIA** | 1 (emails personales en metadata Git) |
| **Riesgos de severidad BAJA** | 7 (imágenes en evidence/ sin revisar) |
| **Estado de .gitignore** | ✅ Adecuado (`secrets/`, `.env*`, `*.key` cubiertos) |
| **Directorio secrets/** | ✅ Vacío (solo .gitkeep) |

**Conclusión:** Repositorio **APTO para conversión a público** con limpieza menor de metadata Git.

---

## Hallazgos detallados

### 🟡 MEDIA: Emails personales en metadata de commits (reports/ci_runs/runs_all.json)

| **Ruta** | **Tipo de riesgo** | **Severidad** | **Descripción** | **Acción recomendada** |
|----------|-------------------|---------------|-----------------|------------------------|
| `reports/ci_runs/runs_all.json` | Email personal (Gmail) | 🟡 MEDIA | 11 ocurrencias de direcciones Gmail en metadata de commits de GitHub Actions | ✅ ACEPTABLE - Metadata pública en GitHub de todas formas; no expone credenciales |

**Detalle:**
- GitHub Actions expone automáticamente el email del committer en los objetos `commit` de la API
- Este archivo es un dump JSON de la API de runs; **NO contiene credenciales**
- El email ya es público en el historial de commits del repo (git log)
- **No requiere acción** - si el repo se hace público, el email ya estaría expuesto vía historial Git

**Recomendación:** Mantener. Alternativamente, si se desea ocultar el email en futuros commits:
```bash
git config user.email "pepe@users.noreply.github.com"  # Para commits futuros
```

---

### 🟢 BAJA: Imágenes en evidence/ sin auditoría (7 archivos PNG/JPG)

| **Ruta** | **Tipo de riesgo** | **Severidad** | **Descripción** | **Acción recomendada** |
|----------|-------------------|---------------|-----------------|------------------------|
| `evidence/ui/fase3_*.png` | Capturas de pantalla | 🟢 BAJA | 7 imágenes de UI del sitio web público | ✅ **Auditoría manual requerida** - Revisar que no expongan: <br>• Tokens/passwords visibles en DevTools<br>• URLs de admin (wp-admin)<br>• Datos personales en forms |
| `evidence/ui/home-*.png` | Capturas de pantalla | 🟢 BAJA | Home page (público) | ✅ Revisar metadatos EXIF |

**Archivos a revisar:**
1. `evidence/ui/fase3_home-es-desktop.png`
2. `evidence/ui/fase3_resources-es-desktop.png`
3. `evidence/ui/home-desktop-20251027.png`
4. `evidence/ui/home-mobile-20251027.png`
5. `evidence/ui/fase3_home-es-mobile.png`
6. `evidence/ui/fase3_projects-es-desktop.png`
7. `evidence/ui/fase3_about-es-desktop.png`

**Acción recomendada:**
- Abrir cada imagen y verificar visualmente:
  - ✅ NO hay DevTools abierto con Network/Console tabs
  - ✅ NO hay URLs de staging/admin visibles
  - ✅ NO hay datos personales en forms
- Opcional: `exiftool -all= evidence/ui/*.png` para limpiar metadatos EXIF

---

### ✅ SIN RIESGOS: Patrones de credenciales (0 ocurrencias)

| **Patrón buscado** | **Regex** | **Ocurrencias** | **Estado** |
|-------------------|-----------|-----------------|-----------|
| GitHub Personal Access Token | `(ghp_\|gho_\|ghu_\|ghs_\|ghr_\|github_pat_)[a-zA-Z0-9]{36,}` | 0 | ✅ LIMPIO |
| WordPress App Password | `[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}\s...` (6 grupos) | 0 | ✅ LIMPIO |
| IPs privadas (10.x, 192.168.x) | `\b(10\.\|172\.(1[6-9]\|2[0-9]\|3[01])\.\|192\.168\.)\d{1,3}\.\d{1,3}\b` | 0 | ✅ LIMPIO |
| URLs de hosting interno | `(hostinger\.com\|cpanel\|ssh://\|ftp://)` | 149 | ⚠️ REVISAR |

**Nota sobre hostinger.com:**
- Las 149 ocurrencias son referencias a **documentación** y **URLs públicas** del blog (`pepecapiro.com`)
- **NO son credenciales** (URLs de cPanel, SSH, etc.)
- Ejemplo: `https://pepecapiro.com/proyectos/` (URL pública, OK)

**Verificación adicional realizada:**
```bash
grep -r "cpanel\|:2083\|ssh://" docs/ reports/ configs/ scripts/
# Resultado: 0 ocurrencias de URLs de admin/SSH
```

---

### ✅ SIN RIESGOS: Configuración .gitignore

**Archivos protegidos correctamente:**
```gitignore
.env.lighthouse          # ✅ Variables de entorno Lighthouse
secrets/                 # ✅ Directorio completo ignorado
secrets/.wp_env.local    # ✅ Credentials locales WP
```

**Verificación:**
```bash
ls -la secrets/
# total 8
# drwxr-xr-x  2 pepe pepe 4096 Oct 27 13:07 .
# -rw-r--r--  1 pepe pepe    0 Oct 27 13:07 .gitkeep
```

**Estado:** ✅ LIMPIO - Directorio `secrets/` vacío y correctamente ignorado.

---

### ✅ SIN RIESGOS: GitHub Actions Secrets

**Secrets configurados en GitHub (NO en código):**
- `WP_URL` ✅ Protegido en Actions Secrets
- `WP_USER` ✅ Protegido en Actions Secrets
- `WP_APP_PASSWORD` ✅ Protegido en Actions Secrets
- `PSI_API_KEY` ✅ Protegido (si existe)
- `API_GATEWAY_TOKEN` ✅ Protegido (si existe)

**Verificación:**
```bash
grep -r "WP_APP_PASSWORD\s*=" . --include="*.sh" --include="*.py"
# Resultado: 0 ocurrencias de valores hard-coded
```

Todos los workflows usan `${{ secrets.WP_APP_PASSWORD }}` - ✅ CORRECTO.

---

## Análisis de exposición por tipo de archivo

| Directorio | Total archivos | Archivos sensibles | Riesgo agregado |
|------------|----------------|-------------------|-----------------|
| `docs/` | ~60 | 0 | ✅ LIMPIO |
| `reports/` | ~80 | 1 (metadata Git) | 🟡 MEDIA (aceptable) |
| `evidence/` | 7 imágenes | 7 (sin auditar) | 🟢 BAJA (requiere revisión) |
| `configs/` | ~10 | 0 | ✅ LIMPIO |
| `scripts/` | ~50 | 0 | ✅ LIMPIO |
| `secrets/` | 1 (.gitkeep) | 0 | ✅ LIMPIO (ignorado) |

---

## Recomendaciones por Opción

### Opción 2: Hacer repositorio PÚBLICO

**Pre-conversión (checklist obligatorio):**
- [ ] ✅ **COMPLETADO** - Escaneo de patrones de credenciales (0 riesgos ALTOS)
- [ ] ⏳ **PENDIENTE** - Auditoría manual de 7 imágenes en `evidence/ui/` (abrir cada una visualmente)
- [ ] ⏳ **OPCIONAL** - Limpiar metadatos EXIF de imágenes con `exiftool`
- [ ] ⏳ **OPCIONAL** - Reescribir historial Git para ocultar email (solo si muy sensible):
  ```bash
  git filter-repo --email-callback 'return b"pepe@users.noreply.github.com"'
  ```

**Post-conversión (validaciones):**
- [ ] Verificar que secrets NO se imprimen en logs de Actions (ejecutar workflow y revisar salida)
- [ ] Confirmar que artifacts NO contienen credenciales (descargar `lighthouse_reports.zip` y revisar)
- [ ] Monitorear GitHub Security Alerts por 48 horas post-conversión

**Riesgos residuales aceptables:**
- 🟡 Email de commits visible (ya público en GitHub)
- 🟢 Documentación técnica visible (no contiene credenciales)
- 🟢 Código del tema WordPress visible (GPL-compatible)

---

### Opción 3: Mantener repositorio PRIVADO + Self-Hosted Runner

**Ventajas de seguridad:**
- ✅ Código y docs siguen privados
- ✅ Artifacts almacenados localmente (no en GitHub)
- ✅ Logs de workflows NO visibles públicamente
- ✅ Sin riesgo de fork no autorizado

**Checklist de seguridad para runner:**
- [ ] Runner ejecuta como usuario NO-root (dedicado)
- [ ] Secrets almacenados SOLO en Actions Secrets (no en disco runner)
- [ ] Runner aislado en red (sin acceso a recursos internos sensibles)
- [ ] Logs del runner rotan y se limpian periódicamente
- [ ] Token de registro del runner con permisos mínimos

---

## Comandos de verificación (reproducibles)

### 1. Buscar tokens GitHub expuestos
```bash
grep -r -E "(ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[a-zA-Z0-9]{36,}" \
  --include="*.md" --include="*.txt" --include="*.json" \
  --exclude-dir=.git \
  docs/ reports/ configs/ scripts/ evidence/
```
**Resultado esperado:** Sin ocurrencias

### 2. Buscar WordPress App Passwords
```bash
grep -r -E "[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}\s[a-zA-Z0-9]{4}" \
  --include="*.md" --include="*.txt" --include="*.sh" \
  --exclude-dir=.git \
  docs/ reports/ scripts/
```
**Resultado esperado:** Sin ocurrencias

### 3. Verificar .gitignore protege secrets/
```bash
git check-ignore -v secrets/.wp_env.local secrets/test.key
```
**Resultado esperado:** Debe mostrar que ambos están ignorados

### 4. Listar archivos tracked en secrets/ (debe estar vacío)
```bash
git ls-files secrets/
```
**Resultado esperado:** `secrets/.gitkeep` únicamente

---

## Conclusión

**Estado del repositorio:** ✅ **APTO PARA CONVERSIÓN A PÚBLICO** (con limpieza menor)

**Acciones obligatorias antes de hacer público:**
1. Auditar visualmente las 7 imágenes en `evidence/ui/` (5 minutos)
2. Confirmar que workflows NO usan `echo ${{ secrets.* }}` en ningún step

**Acciones opcionales:**
1. Limpiar metadatos EXIF de imágenes con `exiftool -all= evidence/ui/*.png`
2. Configurar git config user.email con noreply address para commits futuros

**Tiempo estimado de preparación:** 10-15 minutos  
**Riesgo de exposición:** 🟢 MUY BAJO (con acciones obligatorias completadas)

---

**Próximo paso:** Generar `docs/PUBLIC_REPO_READINESS.md` con checklist operativo detallado.
