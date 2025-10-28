# Preparación para Cambio de Visibilidad a PÚBLICO

**Fecha de preparación:** 2025-10-28 00:35 UTC  
**Responsable:** Copilot (ejecución Opción 2)  
**Commit pre-cambio:** `7915125` - docs(decision): análisis exhaustivo Opción 2 vs Opción 3

---

## Snapshot del estado PRE-cambio

### Repositorio

| Atributo | Valor |
|----------|-------|
| **Nombre** | `ppkapiro/pepecapiro-wp-theme` |
| **Visibilidad actual** | 🔒 PRIVADO |
| **Rama principal** | `main` |
| **Último commit** | `7915125` (2025-10-28) |
| **Total de workflows** | 39 archivos `.github/workflows/*.yml` |
| **GitHub Actions** | ⚠️ **BLOQUEADAS** (minutos agotados desde 2025-10-27 21:07 UTC) |

### Auditorías de seguridad completadas

| Auditoría | Archivo | Estado | Riesgos ALTOS | Bloqueadores |
|-----------|---------|--------|---------------|--------------|
| **Escaneo de secretos** | `reports/security/secrets_scan.md` | ✅ COMPLETO | 0 | 0 |
| **Auditoría de imágenes** | `reports/security/images_audit.md` | ✅ COMPLETO | 0 | 0 |
| **Verificación .gitignore** | `.gitignore` | ✅ ADECUADO | - | 0 |

**Resumen de riesgos:**
- 🟢 **0 riesgos ALTOS** detectados
- 🟡 **1 riesgo MEDIO** (emails en metadata Git - aceptable)
- 🟢 **7 imágenes auditadas** - todas aprobadas para exposición pública
- ✅ **Directorio `secrets/`** vacío y en .gitignore
- ✅ **0 tokens/passwords** hard-coded en código

### Workflows críticos afectados (39 total)

**Workflows de máxima prioridad (requieren validación inmediata):**
1. `lighthouse.yml` - Auditorías de performance (LCP/CLS)
2. `seo_audit.yml` - Validación meta tags/OG/JSON-LD
3. `smoke-tests.yml` - Health checks de URLs públicas
4. `psi_metrics.yml` - PageSpeed Insights metrics
5. `content-sync.yml` - Sincronización de contenido

**Estado actual:** TODOS bloqueados (conclusion: failure, duración: ~4s, steps: 0)

---

## Preparación del cambio

### Checklist pre-cambio (COMPLETADO)

- [x] ✅ Escaneo de seguridad ejecutado (0 riesgos ALTOS)
- [x] ✅ Auditoría de 7 imágenes en `evidence/ui/` (100% aprobadas)
- [x] ✅ Verificación de `.gitignore` (cubre `secrets/`, `.env*`, `.key`)
- [x] ✅ Verificación de `git ls-files secrets/` (solo .gitkeep)
- [x] ✅ Workflows inventariados (39 archivos YAML válidos)
- [x] ✅ Documentación de decisión completa ([`docs/DECISION_BRIEF_OPTION2_vs_OPTION3.md`](../../docs/DECISION_BRIEF_OPTION2_vs_OPTION3.md))
- [x] ✅ Runbook operativo preparado ([`docs/PUBLIC_REPO_READINESS.md`](../../docs/PUBLIC_REPO_READINESS.md))

### Documentos de referencia

| Documento | Ruta | Propósito |
|-----------|------|-----------|
| **Documento de decisión** | [`docs/DECISION_BRIEF_OPTION2_vs_OPTION3.md`](../../docs/DECISION_BRIEF_OPTION2_vs_OPTION3.md) | Análisis exhaustivo Opción 2 vs Opción 3 |
| **Runbook Opción 2** | [`docs/PUBLIC_REPO_READINESS.md`](../../docs/PUBLIC_REPO_READINESS.md) | Checklist operativo conversión a público |
| **Escaneo de secretos** | [`reports/security/secrets_scan.md`](secrets_scan.md) | 0 riesgos ALTOS confirmados |
| **Auditoría de imágenes** | [`reports/security/images_audit.md`](images_audit.md) | 7/7 imágenes aprobadas |
| **Impacto en workflows** | [`reports/ci/workflows_actions_impact.md`](../ci/workflows_actions_impact.md) | 39 workflows afectados por bloqueo |

---

## Proceso de cambio

### 1. Cambio de visibilidad (GitHub UI)

**Acción manual requerida:**

1. Abrir: https://github.com/ppkapiro/pepecapiro-wp-theme/settings
2. Scroll hasta **Danger Zone** (al final)
3. Click en **Change visibility**
4. Seleccionar **Make public**
5. **Leer advertencia de GitHub**: código será visible públicamente
6. Escribir nombre del repositorio para confirmar: `ppkapiro/pepecapiro-wp-theme`
7. Click **I understand, make this repository public**
8. Esperar confirmación (banner verde)

**⏰ Hora exacta del cambio:** _[Registrar tras ejecución manual]_

### 2. Verificación inmediata post-cambio

```bash
# Verificar nueva visibilidad
gh repo view ppkapiro/pepecapiro-wp-theme --json isPrivate,visibility

# Output esperado:
# {
#   "isPrivate": false,
#   "visibility": "PUBLIC"
# }
```

### 3. Commit post-cambio (trigger workflows)

```bash
# Actualizar marca en runbook
echo "✅ COMPLETADO - $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> docs/PUBLIC_REPO_READINESS.md

# Commit
git add docs/PUBLIC_REPO_READINESS.md reports/security/public_switch_prep.md
git commit -m "ci(public): repositorio convertido a público; CI/CD reactivando"
git push origin main
```

---

## Validaciones post-cambio (PASO 3)

**A ejecutar inmediatamente tras hacer el repo público:**

1. ✅ Verificar que workflows **NO** fallan instantáneamente (duración > 10s)
2. ✅ Confirmar que steps aparecen en logs (no array vacío)
3. ✅ Disparar 3 workflows críticos manualmente (`lighthouse`, `seo_audit`, `smoke-tests`)
4. ✅ Descargar artifacts y verificar que NO contienen secrets
5. ✅ Revisar logs y confirmar masking activo de secrets (`***`)

**Archivo de resultados:** [`reports/ci/post_public_health.md`](../ci/post_public_health.md)

---

## Plan de rollback (si se detecta problema crítico)

**Escenarios que requieren rollback:**
- 🚨 Secret expuesto en logs/artifacts (no masked)
- 🚨 Datos personales/corporativos descubiertos en docs tras hacerse públicos
- 🚨 Requisito legal inesperado de privacidad

**Procedimiento de rollback:**

```bash
# 1. Volver a privado INMEDIATAMENTE
gh repo edit ppkapiro/pepecapiro-wp-theme --visibility private

# 2. Verificar cambio
gh repo view ppkapiro/pepecapiro-wp-theme --json isPrivate
# {"isPrivate": true}

# 3. Rotar TODOS los secrets (precaución)
gh secret set WP_APP_PASSWORD --body "NUEVO_PASSWORD_AQUI"
# (repetir para PSI_API_KEY, etc.)

# 4. Cambiar Application Password en WordPress
# WP Admin > Users > Profile > Application Passwords > Revoke all + Generate new

# 5. Investigar forks públicos
gh api /repos/ppkapiro/pepecapiro-wp-theme/forks --jq '.[] | .full_name'
# Contactar propietarios para solicitar eliminación si aplica
```

**⚠️ NOTA:** Forks creados mientras era público **permanecen públicos** incluso tras rollback.

---

## Estado actual

**Fecha de última actualización:** 2025-10-28 00:35 UTC  
**Estado:** 🟡 **PREPARADO - Esperando ejecución manual del cambio de visibilidad**

---

## Registro de ejecución

_[Completar tras ejecutar el cambio de visibilidad]_

| Timestamp | Acción | Responsable | Resultado |
|-----------|--------|-------------|-----------|
| 2025-10-28 00:35 UTC | Preparación completada | Copilot | ✅ Documentos listos |
| _[PENDIENTE]_ | Cambio visibilidad a PÚBLICO | Usuario (GitHub UI) | _[Registrar resultado]_ |
| _[PENDIENTE]_ | Verificación post-cambio | Copilot | _[Registrar]_ |
| _[PENDIENTE]_ | Primer workflow ejecutado | GitHub Actions | _[Registrar run ID]_ |

---

**Próximo paso:** Usuario debe ejecutar el cambio de visibilidad en GitHub UI y notificar para continuar con PASO 3.
