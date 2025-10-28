# Incidente Deploy v0.3.21 — Estado y Resolución

**Fecha:** 2025-10-28 17:30 UTC  
**Severity:** HIGH (sitio 500)  
**PR:** #9 (UI/UX v0.3.1 — Paleta clara + fixes)  
**Tag:** v0.3.21  
**Workflow:** Deploy pepecapiro theme (deploy.yml)

---

## Cronología

### 1. Preparación y merge exitoso
- ✅ PR #9 creado: https://github.com/ppkapiro/pepecapiro-wp-theme/pull/9
- ✅ Comentario pre-merge: Validación OK (paleta clara, WCAG AAA, CLS 0.000)
- ✅ Merge completado: commit 305821a
- ✅ Tag v0.3.21 creado y pusheado

### 2. Deploy automático por tag (run 18883696015)
- ⚠️ Workflow trigger: push tag v0.3.21
- ❌ Fallo en step "Content Ops (WP-CLI remoto)"
- **Error:** `Bad port '"***"'`
- **Causa:** Comillas dobles extra en variables SSH del workflow

```yaml
# Problema en deploy.yml línea ~60
SSH="ssh -p \"***\" \"***@***\""
# Las comillas escapadas causan error: Bad port '"65002"'
```

### 3. Deploy parcial ejecutado
- ✅ Checkout OK
- ✅ Bump style.css a 0.3.21 OK
- ✅ Build (minify CSS) OK
- ✅ Manifest local OK
- ✅ rsync tema al servidor OK
- ❌ Content Ops (WP-CLI) FAILED
- ❌ Verificación remota NOT REACHED

**Consecuencia:** Tema actualizado en servidor, pero Content Ops (flush cache, rewrite rules, etc.) no ejecutado.

### 4. Estado del sitio post-deploy parcial
- ❌ HTTP 500 (3 checks consecutivos confirmados)
- Error WordPress genérico (página de error estándar WP)
- Causa probable: Cache desincronizado, rewrite rules no actualizados, o error PHP en tema

### 5. Intento de rollback (run 18883730121)
- ❌ Workflow rollback.yml FAILED
- **Error:** `scp: stat local "restore.zip": No such file or directory`
- **Causa:** Workflow incompleto, falta paso de creación del ZIP de rollback

---

## Estado Actual

### Sitio en Producción
- **URL:** https://pepecapiro.com/
- **Status:** HTTP 500 (Error de WordPress)
- **Última versión funcional:** v0.3.20 (antes del tag v0.3.21)
- **Versión actual en servidor:** v0.3.21 (parcialmente desplegada)

### Archivos Actualizados en Servidor
- `pepecapiro/style.css`: Bumped a 0.3.21
- `pepecapiro/assets/css/tokens.css`: Paleta clara aplicada
- `pepecapiro/assets/css/theme.css`: Hero gradiente + cards hover
- `pepecapiro/header.php`: aria-label lang-switcher
- `pepecapiro/footer.php`: cookies link fix

### Operaciones NO Ejecutadas
- ❌ `wp rewrite flush --hard`
- ❌ `wp cache flush`
- ❌ `wp litespeed-purge all`
- ❌ `wp transient delete --all`
- ❌ Rank Math sitemap cache clear
- ❌ Sitemap warm-up

---

## Diagnóstico

### Causa Raíz: Comillas Dobles en Variables SSH

**Archivo:** `.github/workflows/deploy.yml`  
**Línea:** ~155 (step "Content Ops")

```bash
# ❌ INCORRECTO (comillas extra)
SSH="ssh -p \"${{ env.SSH_PORT }}\" \"${{ env.SSH_USER }}@${{ env.SSH_HOST }}\""

# ✅ CORRECTO
SSH="ssh -p ${{ env.SSH_PORT }} ${{ env.SSH_USER }}@${{ env.SSH_HOST }}"
```

Cuando la variable se expande:
```bash
# Actual (incorrecto):
ssh -p "65002" "u525829715@***"  # Las comillas causan error
# Esperado (correcto):
ssh -p 65002 u525829715@***
```

### Causa Secundaria: Error 500 en WordPress

**Hipótesis:**
1. **Cache desincronizado**: LiteSpeed Cache + Rank Math sitemaps cacheados con CSS viejo
2. **Rewrite rules**: No se ejecutó `wp rewrite flush`, posible conflicto en rutas
3. **Error PHP en tema**: Poco probable (código reviewed, no hay cambios de lógica)

---

## Plan de Resolución

### Opción 1: Fix Manual SSH (RECOMENDADO)

**Pre-requisitos:**
- Acceso SSH directo al servidor (no vía workflow)
- Credenciales: `$SSH_USER@$SSH_HOST -p $SSH_PORT`

**Pasos:**

```bash
# 1. Conectar al servidor
ssh -p 65002 u525829715@<host>

# 2. Navegar al root de WordPress
cd /home/u525829715/domains/pepecapiro.com/public_html

# 3. Flush cache y rewrite rules
wp cache flush
wp rewrite flush --hard
wp litespeed-purge all
wp transient delete --all

# 4. Limpiar cache de sitemaps Rank Math
PREFIX=$(wp db prefix)
wp db query "DELETE FROM ${PREFIX}options WHERE option_name LIKE 'rank_math_sitemap_%';"

# 5. Warm-up sitemaps
curl -sS https://pepecapiro.com/sitemap_index.xml >/dev/null
curl -sS https://pepecapiro.com/post-sitemap.xml >/dev/null

# 6. Verificar estado
wp theme list
wp plugin list --status=active
wp option get home
wp option get siteurl

# 7. Test HTTP
curl -I https://pepecapiro.com/
```

**Tiempo estimado:** 5-10 minutos  
**Riesgo:** BAJO (operaciones idempotentes)

---

### Opción 2: Rollback Manual SSH

Si Opción 1 no resuelve, rollback a último backup:

```bash
# 1. Conectar al servidor
ssh -p 65002 u525829715@<host>

# 2. Listar backups disponibles
ls -lh /home/u525829715/backups_pepecapiro_theme/

# 3. Identificar último backup funcional (pre-v0.3.21)
# Ejemplo: pepecapiro_20251028_HHMMSS.zip

# 4. Restaurar desde backup
cd /home/u525829715/domains/pepecapiro.com/public_html/wp-content/themes/
rm -rf pepecapiro
unzip /home/u525829715/backups_pepecapiro_theme/<backup_file>.zip

# 5. Ejecutar Opción 1 pasos 3-7
```

**Tiempo estimado:** 10-15 minutos  
**Riesgo:** MEDIO (requiere identificar backup correcto)

---

### Opción 3: Fix Workflow + Re-deploy

**Pre-requisitos:**
- Fix de `.github/workflows/deploy.yml`
- Tag nuevo (v0.3.22 o v0.3.21-hotfix)

**Pasos:**

1. **Crear rama de hotfix:**
```bash
git checkout main
git pull origin main
git checkout -b hotfix/deploy-yml-quotes
```

2. **Fix deploy.yml:**
```diff
# Archivo: .github/workflows/deploy.yml
# Línea: ~155 (step "Content Ops (WP-CLI remoto)")

- SSH="ssh -p \"${{ env.SSH_PORT }}\" \"${{ env.SSH_USER }}@${{ env.SSH_HOST }}\""
+ SSH="ssh -p ${{ env.SSH_PORT }} ${{ env.SSH_USER }}@${{ env.SSH_HOST }}"
```

3. **Commit y push:**
```bash
git add .github/workflows/deploy.yml
git commit -m "fix(ci): remover comillas extra en SSH command (deploy.yml)

- Causa: Bad port '\"65002\"' en Content Ops
- Fix: Eliminar escapes innecesarios en construcción de variable SSH
- Ref: run 18883696015 (v0.3.21 deploy failure)"
git push origin hotfix/deploy-yml-quotes
```

4. **Merge a main y crear tag hotfix:**
```bash
gh pr create --title "Hotfix: Deploy workflow SSH quotes" --body "Fix deploy.yml línea 155" --base main
gh pr merge <PR_NUMBER> --merge
git checkout main && git pull origin main
git tag -a v0.3.22 -m "Hotfix v0.3.22: Deploy workflow SSH fix"
git push origin v0.3.22
```

5. **Monitorear nuevo deploy:**
```bash
# Auto-trigger por tag push
gh run list --workflow deploy.yml --limit 1
gh run watch <RUN_ID>
```

**Tiempo estimado:** 20-30 minutos  
**Riesgo:** MEDIO (depende de que el fix del workflow sea correcto)

---

## Recomendaciones Post-Resolución

### 1. Fix Permanente de Workflows
- [ ] Auditar TODOS los workflows con comandos SSH
- [ ] Eliminar comillas extra en variables de ambiente
- [ ] Test en repo de prueba antes de merge a main

### 2. Deploy Strategy Update
- [ ] Implementar smoke tests POST-deploy (HTTP 200 check)
- [ ] Añadir rollback automático si verificación falla
- [ ] Crear workflow de "hotfix-deploy" sin Content Ops pesado

### 3. Monitoring
- [ ] Configurar Uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Alertas HTTP 500 vía webhook/email
- [ ] Dashboard de estado en GitHub Pages

### 4. Backup Strategy
- [ ] Backup automático PRE-deploy (rollback.yml fix)
- [ ] Retención de últimos 5 backups funcionales
- [ ] Test de restore mensual

---

## Referencias

- **PR #9:** https://github.com/ppkapiro/pepecapiro-wp-theme/pull/9
- **Deploy run (failed):** 18883696015
- **Rollback run (failed):** 18883730121
- **Tag:** v0.3.21
- **Commit merge:** 305821a
- **Color proposal:** reports/uiux_audit/color_proposal.md (261 líneas)

---

## Logs Disponibles

- `logs/deploy_watch_18883696015.log`: Salida parcial del deploy
- `logs/rollback_watch_18883730121.log`: Salida del rollback fallido
- `logs/http_head_home_precheck.txt`: HTTP 500 confirmado
- `logs/http_status_checks.txt`: 3 checks consecutivos (500)
- `logs/html_error_500.txt`: Contenido del error WordPress

---

## Contacto

**Responsable:** GitHub Copilot (automated)  
**Timestamp:** 2025-10-28T17:35:00Z  
**Nivel de urgencia:** HIGH (sitio down)

**Próxima acción:** Ejecutar Opción 1 (Fix Manual SSH) o contactar con acceso SSH para resolución inmediata.
