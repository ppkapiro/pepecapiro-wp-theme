# PUBLIC REPO READINESS - Runbook Operativo para Conversión a Repositorio Público

**Proyecto:** pepecapiro-wp-theme  
**Fecha de creación:** 2025-10-28  
**Propósito:** Checklist operativo paso-a-paso para convertir el repositorio de PRIVADO a PÚBLICO de forma segura.

---

## ⚠️ ADVERTENCIA PRE-LECTURA

**UNA VEZ PÚBLICO, EL CÓDIGO ES IRREVOCABLE:**
- ✘ Cualquiera puede **clonar** el repositorio completo (código, docs, historial Git)
- ✘ Hacer el repo privado después **NO borra** los forks existentes
- ✘ El historial Git completo se expone (incluyendo commits antiguos)
- ✅ Los **secrets de Actions** siguen protegidos (no se exponen)

**Leer documento de decisión completo antes de proceder:** [`DECISION_BRIEF_OPTION2_vs_OPTION3.md`](DECISION_BRIEF_OPTION2_vs_OPTION3.md)

---

## Pre-Conversión (15-20 minutos)

### ✅ PASO 1: Revisar escaneo de seguridad

**Acción:**
```bash
cd /home/pepe/work/pepecapiro-wp-theme
cat reports/security/secrets_scan.md
```

**Validaciones obligatorias:**
- [ ] **Riesgos ALTOS:** 0 detectados ✅
- [ ] **Tokens GitHub expuestos:** 0 ocurrencias ✅
- [ ] **WordPress App Passwords:** 0 ocurrencias ✅
- [ ] **Directorio `secrets/`:** Vacío y en .gitignore ✅

**Criterio de BLOQUEO:** Si hay >= 1 riesgo ALTO, **NO PROCEDER** hasta remediación.

---

### ⏳ PASO 2: Auditoría manual de imágenes en evidence/

**Imágenes a revisar (7 archivos):**
```bash
ls -1 evidence/ui/
```

Output esperado:
```
fase3_home-es-desktop.png
fase3_resources-es-desktop.png
home-desktop-20251027.png
home-mobile-20251027.png
fase3_home-es-mobile.png
fase3_projects-es-desktop.png
fase3_about-es-desktop.png
```

**Checklist por imagen:**

```bash
# Abrir cada imagen con visor de imágenes
xdg-open evidence/ui/fase3_home-es-desktop.png
# O en WSL: explorer.exe evidence/ui/fase3_home-es-desktop.png
```

Para CADA imagen, verificar:
- [ ] **NO** hay DevTools abierto (F12, consola, network tabs)
- [ ] **NO** hay URL `/wp-admin/` visible en la barra de direcciones
- [ ] **NO** hay formularios con datos personales reales (nombres, emails, teléfonos)
- [ ] **NO** hay tokens/passwords visibles en la página (ej: Application Passwords generados)
- [ ] **NO** hay URLs de staging/development (ej: `http://localhost:8080`)

**Si alguna imagen falla el checklist:**
```bash
# Opción 1: Eliminar imagen
git rm evidence/ui/IMAGEN_PROBLEMA.png
git commit -m "security: remove sensitive screenshot"

# Opción 2: Redactar con herramienta (ej: GIMP, ImageMagick)
convert evidence/ui/IMAGEN_PROBLEMA.png -fill black -draw "rectangle X1,Y1 X2,Y2" evidence/ui/IMAGEN_PROBLEMA_redacted.png
git add evidence/ui/IMAGEN_PROBLEMA_redacted.png
git rm evidence/ui/IMAGEN_PROBLEMA.png
git commit -m "security: redact sensitive area in screenshot"
```

---

### 🔧 PASO 3 (OPCIONAL): Limpiar metadatos EXIF

**Propósito:** Eliminar metadata de software, geolocalización, timestamps de las imágenes.

```bash
# Instalar exiftool si no está disponible
sudo apt install libimage-exiftool-perl

# Limpiar todos los metadatos de imágenes
exiftool -all= evidence/ui/*.png

# Verificar limpieza
exiftool evidence/ui/home-desktop-20251027.png | grep -i "exif\|gps\|software"
# Output esperado: vacío o solo metadata básica (dimensiones)
```

**Commit cambios (si aplica):**
```bash
git add evidence/ui/
git commit -m "security: strip EXIF metadata from screenshots"
git push origin main
```

---

### ✅ PASO 4: Verificar workflows NO imprimen secrets

**Validación:**
```bash
# Buscar cualquier uso de echo con secrets
grep -r "echo.*\${{.*secrets" .github/workflows/

# Output esperado: 0 resultados
```

**Patrones a buscar (BLOQUEADORES):**
```yaml
# ❌ MAL - Imprime el secret
- run: echo "Password is ${{ secrets.WP_APP_PASSWORD }}"

# ❌ MAL - Imprime en variable de entorno visible
- run: |
    export WP_PASS="${{ secrets.WP_APP_PASSWORD }}"
    env | grep WP_PASS

# ✅ BIEN - Usa el secret sin imprimirlo
- run: |
    curl -u "${{ secrets.WP_USER }}:${{ secrets.WP_APP_PASSWORD }}" \
      https://pepecapiro.com/wp-json/wp/v2/posts
```

**Si se encuentra algún patrón MAL:**
```bash
# Editar workflow problemático
nano .github/workflows/WORKFLOW_PROBLEMA.yml
# Remover echo/print del secret
git add .github/workflows/WORKFLOW_PROBLEMA.yml
git commit -m "security: remove secret printing from workflow"
git push origin main
```

---

### ✅ PASO 5: Confirmar .gitignore cubre archivos sensibles

**Validación:**
```bash
# Verificar que secrets/ está ignorado
git check-ignore -v secrets/.wp_env.local secrets/test.key

# Output esperado:
# .gitignore:X:secrets/    secrets/.wp_env.local
# .gitignore:X:secrets/    secrets/test.key
```

**Archivos críticos que DEBEN estar ignorados:**
```bash
cat .gitignore | grep -E "secret|\.env|\.key"
```

Output esperado mínimo:
```
.env.lighthouse
secrets/
secrets/.wp_env.local
```

**Si falta algún patrón crítico:**
```bash
echo "*.key" >> .gitignore
echo ".env*" >> .gitignore
git add .gitignore
git commit -m "security: improve .gitignore coverage"
git push origin main
```

---

### ✅ PASO 6: Listar archivos tracked en secrets/ (debe estar vacío)

**Validación:**
```bash
git ls-files secrets/
```

**Output esperado:**
```
secrets/.gitkeep
```

**Si aparecen otros archivos:**
```bash
# ¡CRÍTICO! Archivos en secrets/ están tracked y se expondrán
git ls-files secrets/  # Revisar lista

# Remover del tracking (CUIDADO: esto reescribe historial si el archivo se committeó antes)
git rm --cached secrets/ARCHIVO_PROBLEMA
git commit -m "security: remove sensitive file from tracking"

# Verificar que el archivo NO está en historial reciente
git log --all --full-history -- secrets/ARCHIVO_PROBLEMA
# Si aparece en commits antiguos, considerar git filter-repo (avanzado)
```

---

### ✅ PASO 7: Checklist final pre-conversión

**Confirmación manual (marcar cada item):**
- [ ] Escaneo de seguridad revisado: 0 riesgos ALTOS
- [ ] 7 imágenes auditadas: sin datos sensibles visibles
- [ ] Metadatos EXIF limpiados (opcional pero recomendado)
- [ ] Workflows verificados: sin `echo ${{ secrets.*  }}`
- [ ] .gitignore verificado: cubre secrets/, .env*, *.key
- [ ] `git ls-files secrets/` retorna SOLO `.gitkeep`
- [ ] Última sincronización: `git pull origin main` (working tree clean)
- [ ] Backup local creado (opcional): `git clone --mirror . ../pepecapiro-wp-theme-backup.git`

**Si TODOS los items están ✅ → Proceder a Conversión**

---

## Conversión (2 minutos)

### 🚀 PASO 8: Cambiar visibilidad del repositorio

**Método 1: GitHub Web UI (recomendado)**

1. Abrir: https://github.com/ppkapiro/pepecapiro-wp-theme/settings
2. Scroll hasta **Danger Zone** (al final de la página)
3. Click en **Change visibility**
4. Seleccionar **Make public**
5. Leer el warning de GitHub
6. Escribir el nombre del repositorio exacto: `ppkapiro/pepecapiro-wp-theme`
7. Click **I understand, make this repository public**
8. Esperar confirmación (debe aparecer banner verde)

**Método 2: GitHub CLI (alternativo)**

```bash
# ⚠️ ESTE COMANDO ES IRREVERSIBLE (sin confirmación)
gh repo edit ppkapiro/pepecapiro-wp-theme --visibility public
```

**Verificación inmediata:**
```bash
gh repo view ppkapiro/pepecapiro-wp-theme --json isPrivate,visibility
```

Output esperado:
```json
{
  "isPrivate": false,
  "visibility": "PUBLIC"
}
```

---

## Post-Conversión (10-15 minutos)

### ✅ PASO 9: Verificar que secrets NO se exponen

**Validación:**
```bash
# Listar secrets (solo nombres, no valores)
gh secret list
```

Output esperado:
```
WP_URL               Updated 2025-10-XX
WP_USER              Updated 2025-10-XX
WP_APP_PASSWORD      Updated 2025-10-XX
PSI_API_KEY          Updated 2025-10-XX
```

**Intentar acceder a un secret (debe fallar):**
```bash
# Desde fuera del repo (sin permisos de colaborador)
# Esto simula un usuario externo
gh secret get WP_APP_PASSWORD --repo ppkapiro/pepecapiro-wp-theme
```

Output esperado:
```
HTTP 403: Resource not accessible by personal access token
# O "Secret not found" si el token no tiene permisos
```

✅ **CONFIRMADO:** Secrets protegidos incluso en repo público.

---

### ✅ PASO 10: Disparar workflow de prueba

**Objetivo:** Verificar que workflows ejecutan correctamente y NO imprimen secrets.

```bash
# Disparar workflow Lighthouse (crítico para Fase 4)
gh workflow run lighthouse.yml

# Esperar 5 segundos y obtener el ID del run
sleep 5
RUN_ID=$(gh run list --workflow=lighthouse.yml --limit=1 --json databaseId --jq '.[0].databaseId')
echo "Run ID: $RUN_ID"

# Monitorear en tiempo real
gh run watch $RUN_ID
```

**Verificaciones durante ejecución:**
- [ ] Workflow inicia correctamente (no falla instantáneamente como antes)
- [ ] Steps aparecen en la salida (`Setup Chrome`, `Run Lighthouse`, etc.)
- [ ] No aparecen errores de "minutes exceeded" o "billing"

**Tiempo esperado:** 5-8 minutos para Lighthouse completo (mobile + desktop).

---

### ✅ PASO 11: Revisar logs del workflow

**Una vez completado el run:**
```bash
# Abrir logs en browser
gh run view $RUN_ID --web

# O descargar logs localmente
gh run view $RUN_ID --log > /tmp/lighthouse_run_$RUN_ID.log

# Buscar secrets accidentalmente impresos (NO debe haber matches)
grep -i "WP_APP_PASSWORD\|application.*password\|Basic.*Auth" /tmp/lighthouse_run_$RUN_ID.log
```

**Output esperado:** Sin matches (0 líneas).

**Si se encuentra un secret impreso:**
```bash
# 🚨 ACCIÓN INMEDIATA
# 1. Hacer repo privado de nuevo (rollback)
gh repo edit ppkapiro/pepecapiro-wp-theme --visibility private

# 2. Identificar workflow problemático
gh run view $RUN_ID --json jobs --jq '.jobs[].steps[] | select(.conclusion == "failure") | .name'

# 3. Corregir workflow
nano .github/workflows/WORKFLOW_PROBLEMA.yml
# Remover echo del secret

# 4. Rotar secret expuesto en GitHub
gh secret set WP_APP_PASSWORD --body "NUEVO_PASSWORD_AQUI"

# 5. Cambiar Application Password en WordPress
# WP Admin > Users > Profile > Application Passwords > Revoke + Generate New
```

---

### ✅ PASO 12: Descargar y verificar artifacts

**Obtener artifact del run:**
```bash
# Descargar artifact (ahora debe funcionar sin error)
gh run download $RUN_ID --name lighthouse_reports --dir /tmp/lh_test

# Verificar contenido
ls -lh /tmp/lh_test/
```

Output esperado:
```
assert_summary.txt
home.json
home.html
home-d.json
home-d.html
... (más reportes)
```

**Revisar assert_summary.txt:**
```bash
cat /tmp/lh_test/assert_summary.txt
```

**Verificar que NO contiene datos sensibles:**
- [ ] NO hay tokens/passwords
- [ ] NO hay URLs de admin (wp-admin)
- [ ] Solo métricas públicas (Performance, LCP, CLS scores)

✅ **ACEPTABLE:** Artifacts contienen solo métricas de performance (públicas).

---

### ✅ PASO 13: Verificar workflows adicionales

**Disparar 2-3 workflows críticos más:**
```bash
# Smoke tests
gh workflow run smoke-tests.yml
sleep 3
SMOKE_RUN=$(gh run list --workflow=smoke-tests.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch $SMOKE_RUN

# SEO Audit
gh workflow run seo_audit.yml
sleep 3
SEO_RUN=$(gh run list --workflow=seo_audit.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh run watch $SEO_RUN
```

**Criterio de éxito:**
- [ ] Ambos workflows completan con `conclusion: success`
- [ ] Logs no muestran secrets
- [ ] Artifacts (si aplica) no contienen datos sensibles

---

### ✅ PASO 14: Activar GitHub Security Features

**Configurar alertas de seguridad:**
1. Abrir: https://github.com/ppkapiro/pepecapiro-wp-theme/settings/security_analysis
2. Activar:
   - [x] **Dependency graph**
   - [x] **Dependabot alerts**
   - [x] **Dependabot security updates**
   - [x] **Secret scanning** (crítico)
   - [x] **Code scanning** (CodeQL - opcional)

**Verificar configuración:**
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/vulnerability-alerts --method PUT
gh api /repos/ppkapiro/pepecapiro-wp-theme --jq '{security: {secret_scanning: .security_and_analysis.secret_scanning.status, dependabot: .security_and_analysis.dependabot_alerts.status}}'
```

Output esperado:
```json
{
  "security": {
    "secret_scanning": "enabled",
    "dependabot": "enabled"
  }
}
```

---

### ✅ PASO 15: Monitorear forks y acceso

**Verificar forks (primeras 24 horas):**
```bash
# Listar forks del repo
gh repo list --fork --source ppkapiro/pepecapiro-wp-theme

# Output esperado (inicialmente): vacío
```

**Si aparecen forks sospechosos:**
- Revisar perfil del usuario que hizo fork
- Si es legítimo (otro dev, portafolio): ✅ OK
- Si es sospechoso (cuentas bot, scraping): Reportar a GitHub

**Configurar notificaciones:**
1. GitHub > Settings > Notifications
2. Activar: **Email notifications for new forks**
3. Activar: **Security alerts**

---

## Post-Conversión: Monitoring (48 horas)

### 📊 PASO 16: Dashboard de monitoreo

**Checklist diario (Día 1 y Día 2):**

```bash
# 1. Verificar workflows siguen ejecutándose sin errores
gh run list --limit=10 --json conclusion,workflowName | jq -r '.[] | "\(.workflowName): \(.conclusion)"'

# 2. Revisar alertas de seguridad
gh api /repos/ppkapiro/pepecapiro-wp-theme/secret-scanning/alerts

# 3. Contar forks
gh api /repos/ppkapiro/pepecapiro-wp-theme --jq '.forks_count'

# 4. Verificar issues abiertos por externos (si aplica)
gh issue list --state=open
```

**Criterios de alerta (requieren acción):**
- 🚨 Secret scanning detecta credenciales → Rotar secret inmediatamente
- 🚨 Fork sospechoso con commits maliciosos → Reportar a GitHub
- ⚠️ Workflow falla por "secret not found" → Verificar permisos de Actions

---

## Rollback (si se detecta problema crítico)

### 🔙 Volver a privado (1 minuto)

**Escenarios que requieren rollback:**
- Secret expuesto en logs/artifacts
- Datos personales/corporativos descubiertos en docs
- Requisito legal inesperado de privacidad

**Procedimiento:**
```bash
# 1. Cambiar visibilidad inmediatamente
gh repo edit ppkapiro/pepecapiro-wp-theme --visibility private

# 2. Verificar
gh repo view ppkapiro/pepecapiro-wp-theme --json isPrivate
# {"isPrivate": true}

# 3. Rotar TODOS los secrets (precaución)
gh secret set WP_APP_PASSWORD --body "NUEVO_PASSWORD_1"
gh secret set PSI_API_KEY --body "NUEVO_API_KEY_2"
# ... (repetir para cada secret)

# 4. Cambiar Application Password en WordPress
# WP Admin > Users > Profile > Application Passwords > Revoke all + Generate new

# 5. Investigar forks públicos existentes
gh api /repos/ppkapiro/pepecapiro-wp-theme/forks --jq '.[] | .full_name'
# Contactar a propietarios de forks para solicitar eliminación (si aplica)
```

**⚠️ IMPORTANTE:** Forks públicos creados antes del rollback **permanecen públicos**. Volver el repo a privado NO los borra.

---

## Checklist final de éxito

**Tras 48 horas de monitoreo, confirmar:**
- [ ] ✅ Workflows ejecutan correctamente (5+ runs exitosos)
- [ ] ✅ Sin secrets detectados en logs (secret scanning limpio)
- [ ] ✅ Artifacts descargables y sanitizados
- [ ] ✅ 0 alertas de seguridad en GitHub
- [ ] ✅ Forks legítimos o cero forks
- [ ] ✅ CI/CD totalmente operativo (minutos ilimitados confirmados)

**Estado:** 🎉 **CONVERSIÓN EXITOSA**

---

## Contactos y escalación

**Si aparecen problemas inesperados:**
- GitHub Support: https://support.github.com/
- Documentación de seguridad: https://docs.github.com/en/code-security
- Reporte de fork malicioso: https://support.github.com/contact/report-abuse

---

**Última actualización:** 2025-10-28  
**Próxima revisión:** Post-conversión (si se ejecuta)
