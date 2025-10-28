# Documento de Decisión: Opción 2 (Repositorio Público) vs Opción 3 (Self-Hosted Runner)

**Proyecto:** pepecapiro-wp-theme  
**Fecha:** 2025-10-28  
**Autor:** Equipo técnico (análisis automatizado)  
**Estado:** PENDIENTE DE DECISIÓN

---

## 1. Resumen ejecutivo

Desde el 2025-10-27 21:07 UTC, **todos los workflows de GitHub Actions (39 workflows) están fallando** debido al agotamiento de minutos de Actions para repositorios privados. Esto ha bloqueado completamente el pipeline de CI/CD, impidiendo:

- ✘ Auditorías de performance (Lighthouse)
- ✘ Validaciones SEO/A11y
- ✘ Smoke tests post-deploy
- ✘ Monitoring automatizado
- ✘ Publicación de reportes

**Opciones evaluadas:**
- **Opción 1:** Aumentar plan de pago GitHub → ❌ DESCARTADA (requiere aprobación de billing)
- **Opción 2:** Convertir repositorio a **PÚBLICO** → ✅ VIABLE (minutos ilimitados)
- **Opción 3:** Mantener **PRIVADO** + self-hosted runner → ✅ VIABLE (cero consumo de minutos)

Este documento analiza exhaustivamente Opción 2 vs Opción 3 para permitir una decisión informada.

---

## 2. Matriz comparativa de decisión

| **Criterio** | **Opción 2: Repo PÚBLICO** | **Opción 3: Self-Hosted Runner** | **Ganador** |
|--------------|---------------------------|----------------------------------|-------------|
| **Costo mensual** | $0 (Actions ilimitadas) | $0 local / $5-15 VPS básico | 🟢 EMPATE |
| **Tiempo de implementación** | 15 minutos (auditoría + cambio visibilidad) | 2-4 horas (setup runner + migrar workflows) | 🟢 Opción 2 |
| **Complejidad técnica** | 🟢 MUY BAJA (1 clic en Settings) | 🔴 ALTA (instalación, configuración, permisos) | 🟢 Opción 2 |
| **Mantenimiento operativo** | 🟢 CERO (GitHub gestiona runners) | 🔴 ALTO (actualizaciones, limpieza, monitoring) | 🟢 Opción 2 |
| **Seguridad del código** | 🔴 EXPUESTO (cualquiera puede clonar) | 🟢 PRIVADO (solo colaboradores) | 🟢 Opción 3 |
| **Seguridad de secrets** | 🟢 PROTEGIDOS (Actions Secrets no se exponen) | 🟢 PROTEGIDOS (Actions Secrets o .env local) | 🟢 EMPATE |
| **Riesgo de exposición docs** | 🟡 MEDIO (docs técnicas visibles) | 🟢 BAJO (todo privado) | 🟢 Opción 3 |
| **Velocidad de ejecución** | 🟢 ALTA (runners GitHub optimizados) | 🟡 MEDIA (depende de hardware local) | 🟢 Opción 2 |
| **Concurrencia de jobs** | 🟢 ILIMITADA (múltiples runners en paralelo) | 🔴 LIMITADA (1 job por runner; escalar = más runners) | 🟢 Opción 2 |
| **Fiabilidad (uptime)** | 🟢 99.9% (SLA GitHub) | 🟡 VARIABLE (depende de PC/WSL/VPS uptime) | 🟢 Opción 2 |
| **Portabilidad** | 🟢 ALTA (cualquier dev puede forkear/clonar) | 🔴 BAJA (dependencia de máquina específica) | 🟢 Opción 2 |
| **Cambios en workflows** | 🟢 CERO (YAML sin cambios) | 🔴 39 archivos (cambiar `runs-on: self-hosted`) | 🟢 Opción 2 |
| **Instalación de software** | 🟢 PREINSTALADO (Node, Python, Chrome, etc.) | 🔴 MANUAL (cada herramienta por separado) | 🟢 Opción 2 |
| **Artifacts** | 🟡 PÚBLICOS por defecto | 🟢 PRIVADOS (almacenados localmente) | 🟢 Opción 3 |
| **Logs de workflows** | 🟡 PÚBLICOS (cualquiera puede ver) | 🟢 PRIVADOS (solo colaboradores) | 🟢 Opción 3 |
| **Cumplimiento/Regulaciones** | 🔴 BAJO (si docs contienen info sensible) | 🟢 ALTO (todo controlado) | 🟢 Opción 3 |

### Puntuación agregada (criterios ponderados)

| Opción | Velocidad | Costo | Operación | Seguridad | **TOTAL** |
|--------|-----------|-------|-----------|-----------|-----------|
| **Opción 2 (Público)** | 10/10 | 10/10 | 10/10 | 6/10 | **36/40** (90%) |
| **Opción 3 (Self-Hosted)** | 6/10 | 9/10 | 4/10 | 9/10 | **28/40** (70%) |

**Interpretación:**
- Si **prioridad = Velocidad de recuperación + Mínima fricción**: Opción 2
- Si **prioridad = Privacidad + Cumplimiento**: Opción 3

---

## 3. Riesgos clave y mitigaciones

### Opción 2: Repositorio PÚBLICO

| **Riesgo** | **Probabilidad** | **Impacto** | **Mitigación** |
|------------|------------------|-------------|----------------|
| **R2.1** Exposición de URLs internas de Hostinger | BAJA | MEDIO | ✅ **COMPLETADO** - Escaneo realizado: 0 URLs de cPanel/SSH expuestas |
| **R2.2** Credenciales hard-coded en código | BAJA | ALTO | ✅ **COMPLETADO** - Escaneo: 0 tokens/passwords en archivos tracked |
| **R2.3** Capturas con datos sensibles en `evidence/` | MEDIA | MEDIO | ⚠️ **PENDIENTE** - Auditar 7 imágenes manualmente (10 min) |
| **R2.4** Secrets impresos en logs de Actions | BAJA | ALTO | ✅ **VERIFICADO** - Workflows usan `${{ secrets.* }}` sin echo |
| **R2.5** Artifacts públicos con datos sensibles | BAJA | MEDIO | ✅ **ACEPTABLE** - Artifacts contienen solo métricas públicas (Lighthouse) |
| **R2.6** Fork malicioso del código | BAJA | BAJO | ✅ **ACEPTABLE** - Código WordPress es GPL-compatible |
| **R2.7** Historial Git con commits sensibles | BAJA | MEDIO | ✅ **VERIFICADO** - Historial limpio; solo metadata Git pública (emails) |

**Riesgo residual total:** 🟢 **MUY BAJO** (con auditoría de imágenes completada)

### Opción 3: Self-Hosted Runner

| **Riesgo** | **Probabilidad** | **Impacto** | **Mitigación** |
|------------|------------------|-------------|----------------|
| **R3.1** Runner comprometido expone secrets locales | MEDIA | ALTO | • Usuario dedicado NO-root<br>• Secrets en Actions (no en disco)<br>• Aislamiento de red |
| **R3.2** PC/WSL apagado = workflows colgados | ALTA | MEDIO | • VPS con uptime 99.9%<br>• Timeouts agresivos en workflows<br>• Notificaciones de fallo |
| **R3.3** Falta de mantenimiento del runner | MEDIA | MEDIO | • Cron job para actualizaciones<br>• Monitoring de espacio en disco<br>• Documentación de runbook |
| **R3.4** Dependencias desactualizadas (Chrome, Node) | MEDIA | BAJO | • Script de bootstrap con instalación<br>• Versionado explícito en Dockerfile |
| **R3.5** Consumo de ancho de banda/disco | BAJA | BAJO | • `retention-days: 7` en artifacts<br>• Limpieza periódica de workspace |
| **R3.6** Token de registro del runner expuesto | BAJA | ALTO | • Token de un solo uso en registro<br>• Rotación tras cada re-registro |

**Riesgo residual total:** 🟡 **MEDIO** (requiere disciplina operativa)

---

## 4. Costos y operación

### Opción 2: Repositorio PÚBLICO

**Costos monetarios:**
- GitHub Actions: **$0/mes** (ilimitadas para repos públicos)
- Storage de artifacts: **$0** (incluido)
- Bandwidth: **$0** (incluido)

**Costos de tiempo (one-time):**
- Auditoría de imágenes: **10 minutos**
- Cambio de visibilidad: **1 minuto** (Settings > General > Change visibility)
- Verificación post-cambio: **5 minutos** (ejecutar 1 workflow y revisar logs)
- **TOTAL:** **~15 minutos**

**Costos de tiempo (recurrente):**
- Mantenimiento: **0 horas/mes**

### Opción 3: Self-Hosted Runner

**Costos monetarios (escenario VPS):**
- VPS básico (2 vCPU, 2GB RAM, 40GB SSD): **$5-15/mes** (DigitalOcean, Linode, Hetzner)
- O PC/WSL local: **$0** (pero dependencia de uptime)

**Costos de tiempo (one-time):**
- Provisión VPS + SSH setup: **30 minutos**
- Instalación de runner: **20 minutos**
- Instalación de dependencias (Node, Python, Chrome, etc.): **40 minutos**
- Configuración como servicio: **10 minutos**
- Modificar 39 workflows (`runs-on`): **30 minutos**
- Testing y validación: **30 minutos**
- **TOTAL:** **~2.5 horas**

**Costos de tiempo (recurrente):**
- Actualizaciones de runner: **15 min/mes**
- Limpieza de workspace: **10 min/mes**
- Monitoring/troubleshooting: **30 min/mes** (promedio)
- **TOTAL:** **~1 hora/mes**

**Costo anual (5 años):**
- Opción 2: $0 + 15 min = **$0**
- Opción 3 (VPS $10/mes): $600 + 2.5h + (1h × 60 meses) = **$600 + 62.5 horas**

---

## 5. Impacto en seguridad y cumplimiento

### Opción 2: Repositorio PÚBLICO

**Exposición:**
- ✅ Código del tema WordPress → **Aceptable** (código GPL-compatible; no es propiedad intelectual crítica)
- ✅ Documentación técnica (DTC, fase reports) → **Aceptable** (no contiene credenciales según escaneo)
- ⚠️ Evidencias visuales (7 imágenes) → **Requiere auditoría** (posible exposición de URLs de admin)
- ✅ Workflows de CI/CD → **Aceptable** (lógica no sensible; secrets protegidos)

**Protecciones activas:**
- GitHub Actions Secrets: **NO se exponen** en repos públicos (requieren permisos de colaborador)
- Artifacts: **Públicos** pero contienen solo métricas de performance (Lighthouse, PSI)
- Logs: **Públicos** pero workflows NO usan `echo ${{ secrets.* }}`

**Cumplimiento:**
- GDPR: ✅ OK (no hay datos personales en código/docs según escaneo)
- HIPAA/PCI-DSS: N/A (proyecto WordPress no procesa salud/pagos)
- Propiedad intelectual: ✅ OK (tema WordPress es publicable; no hay IP crítica)

**Recomendación:** Si el blog `pepecapiro.com` es **personal/profesional** (no corporativo), hacer el repo público es **estándar de la industria** para proyectos WordPress.

### Opción 3: Self-Hosted Runner + Repositorio PRIVADO

**Exposición:**
- ✅ Código → **Privado** (solo colaboradores)
- ✅ Docs → **Privadas**
- ✅ Artifacts → **Privados** (almacenados en runner)
- ✅ Logs → **Privados**

**Protecciones activas:**
- Runner aislado: Usuario dedicado, sin acceso a recursos de red sensibles
- Secrets: Almacenados en Actions Secrets (nunca en disco del runner)
- Logs: Rotación automática con `logrotate`

**Cumplimiento:**
- **Máxima privacidad**: Ideal si el proyecto fuera corporativo o bajo NDA
- **Control total**: Auditorías internas sin exposición externa

**Recomendación:** Opción 3 es **overkill** para un blog personal, pero necesaria si hay **regulaciones de privacidad** o si el código contiene **lógica de negocio propietaria**.

---

## 6. Plan de implementación (alto nivel)

### Opción 2: Hacer repositorio PÚBLICO

**Fase 1: Pre-conversión (15 minutos)**
1. [ ] Ejecutar escaneo de secretos → ✅ COMPLETADO (`reports/security/secrets_scan.md`)
2. [ ] Auditar 7 imágenes en `evidence/ui/` → ⏳ PENDIENTE (abrir cada una, verificar no hay admin URLs)
3. [ ] (Opcional) Limpiar EXIF de imágenes: `exiftool -all= evidence/ui/*.png`
4. [ ] Verificar `.gitignore` cubre `secrets/`, `.env*` → ✅ VERIFICADO

**Fase 2: Conversión (2 minutos)**
1. [ ] GitHub: Settings > General > Danger Zone > Change visibility
2. [ ] Seleccionar "Make public"
3. [ ] Confirmar escribiendo nombre del repo
4. [ ] Esperar confirmación

**Fase 3: Post-conversión (10 minutos)**
1. [ ] Disparar workflow `lighthouse.yml` manualmente: `gh workflow run lighthouse.yml`
2. [ ] Verificar que ejecuta sin errores: `gh run watch`
3. [ ] Abrir logs y confirmar que NO se imprimen secrets
4. [ ] Descargar artifact `lighthouse_reports.zip` y verificar contenido
5. [ ] Disparar 2-3 workflows más (smoke-tests, seo_audit) para validar

**Fase 4: Monitoring (48 horas)**
1. [ ] Activar GitHub Security Alerts: Settings > Security > Code security and analysis
2. [ ] Monitorear notificaciones de secret scanning
3. [ ] Revisar forks no autorizados (si aparecen)

**Plan de rollback (si se detecta exposición crítica):**
1. Inmediato: Settings > Change visibility > Make private (1 minuto)
2. Investigar fork maliciosos y reportar a GitHub (si aplica)
3. Rotar secrets expuestos: WP Application Password, API keys, etc.
4. Ejecutar `git filter-repo` para reescribir historial si secreto committed

**Tiempo total:** 15 min pre + 2 min conversión + 10 min post = **~27 minutos**

**Enlace a runbook detallado:** [`docs/PUBLIC_REPO_READINESS.md`](PUBLIC_REPO_READINESS.md)

---

### Opción 3: Mantener PRIVADO + Self-Hosted Runner

**Fase 1: Provisión de infraestructura (30 minutos)**
1. [ ] Elegir host: PC/WSL local O VPS (recomendado VPS para uptime)
2. [ ] Si VPS: Provisionar en DigitalOcean/Hetzner (Ubuntu 22.04 LTS, 2 vCPU, 2GB RAM)
3. [ ] Configurar SSH key-based auth
4. [ ] Hardening básico: firewall (ufw), fail2ban, actualizaciones automáticas

**Fase 2: Instalación de runner (1 hora)**
1. [ ] Crear usuario dedicado: `sudo adduser github-runner`
2. [ ] Descargar runner: https://github.com/actions/runner/releases
3. [ ] Configurar runner:
   ```bash
   ./config.sh --url https://github.com/ppkapiro/pepecapiro-wp-theme \
               --token <RUNNER_TOKEN> \
               --labels self-hosted,linux,x64 \
               --unattended
   ```
4. [ ] Instalar como servicio: `sudo ./svc.sh install && sudo ./svc.sh start`
5. [ ] Verificar en GitHub: Settings > Actions > Runners (debe aparecer "Idle")

**Fase 3: Instalación de dependencias (40 minutos)**
1. [ ] Node.js 20 LTS: `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -`
2. [ ] Python 3.11: `sudo apt install python3.11 python3-pip`
3. [ ] Chrome/Chromium: `sudo apt install chromium-browser`
4. [ ] Lighthouse CLI: `npm install -g lighthouse`
5. [ ] Python libs: `pip3 install requests beautifulsoup4 lxml pyyaml`
6. [ ] WP-CLI (si aplica): `curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar`
7. [ ] Verificar versiones:
   ```bash
   node --version  # v20.x
   python3 --version  # 3.11.x
   lighthouse --version  # 11.x
   chromium-browser --version
   ```

**Fase 4: Migrar workflows (30 minutos)**
1. [ ] Crear branch: `git checkout -b feat/self-hosted-runner`
2. [ ] Script de migración masiva:
   ```bash
   find .github/workflows -name "*.yml" -exec sed -i 's/runs-on: ubuntu-latest/runs-on: self-hosted/g' {} \;
   ```
3. [ ] Commit: `git add .github/workflows/ && git commit -m "ci: migrate to self-hosted runner"`
4. [ ] Push: `git push origin feat/self-hosted-runner`

**Fase 5: Testing (30 minutos)**
1. [ ] Disparar workflow simple: `gh workflow run status.yml`
2. [ ] Monitorear en runner: `tail -f ~github-runner/_work/_diag/Runner_*.log`
3. [ ] Verificar éxito; iterar si falla (instalar dependencias faltantes)
4. [ ] Disparar workflows críticos: lighthouse, smoke-tests, seo_audit
5. [ ] Merge a main: `git checkout main && git merge feat/self-hosted-runner && git push`

**Fase 6: Mantenimiento (configurar cron jobs)**
1. [ ] Actualización del runner:
   ```cron
   0 2 * * 0 cd /home/github-runner/actions-runner && ./run.sh --check-version
   ```
2. [ ] Limpieza de workspace:
   ```cron
   0 3 * * * find /home/github-runner/_work/ -type d -mtime +7 -exec rm -rf {} \;
   ```
3. [ ] Monitoring de disco:
   ```cron
   0 * * * * df -h /home/github-runner | awk '$5 > 80 {print "Disco al "$5}' | mail -s "Runner disk warning" admin@example.com
   ```

**Plan de rollback (volver a GitHub-hosted runners):**
1. Revertir workflows: `git revert <commit_hash>` del cambio `runs-on: self-hosted`
2. Desconectar runner: `sudo ./svc.sh stop && sudo ./svc.sh uninstall`
3. GitHub: Settings > Actions > Runners > Remove runner
4. Limpiar VPS (si aplica): `sudo userdel -r github-runner`

**Tiempo total:** 30 min infra + 1h runner + 40 min deps + 30 min migrate + 30 min test = **~2.5 horas**

**Enlace a runbook detallado:** [`docs/SELF_HOSTED_RUNNER_PLAN.md`](SELF_HOSTED_RUNNER_PLAN.md)

---

## 7. Plan de rollback (comparativa)

| Aspecto | Opción 2 Rollback | Opción 3 Rollback |
|---------|------------------|-------------------|
| **Tiempo de rollback** | 1 minuto (cambiar visibilidad) | 30 minutos (revertir workflows + desconectar runner) |
| **Pérdida de datos** | Ninguna | Artifacts locales (si no backed up) |
| **Riesgo de forks** | ALTO (forks persisten incluso tras volver a privado) | BAJO (nunca fue público) |
| **Rotación de secrets** | Requerida si se detectó exposición | No requerida |
| **Complejidad** | 🟢 MUY BAJA | 🟡 MEDIA |

**Conclusión:** Opción 2 tiene rollback más rápido pero irreversible (forks públicos permanecen). Opción 3 tiene rollback más lento pero sin consecuencias externas.

---

## 8. Recomendación preliminar (condicional)

### SI `blog_type == "personal/profesional"` AND `no_regulatory_requirements` → **Opción 2** (Repo Público)

**Justificación:**
- ✅ Recuperación CI/CD en **15 minutos** vs 2.5 horas
- ✅ Cero mantenimiento operativo
- ✅ Escaneo de seguridad confirma **0 riesgos ALTOS**
- ✅ Estándar de industria para proyectos WordPress (la mayoría son públicos)
- ✅ Beneficio adicional: Portafolio público → SEO + credibilidad técnica

**Condiciones obligatorias:**
1. [ ] Completar auditoría de 7 imágenes en `evidence/ui/` (10 minutos)
2. [ ] Confirmar que NO hay datos personales/corporativos sensibles en docs

### SI `blog_type == "corporativo"` OR `has_regulatory_requirements` OR `contains_proprietary_logic` → **Opción 3** (Self-Hosted)

**Justificación:**
- ✅ Máxima privacidad y control
- ✅ Cumplimiento regulatorio (GDPR, HIPAA, etc.)
- ✅ Protección de IP propietaria

**Condiciones obligatorias:**
1. [ ] Provisionar VPS (no usar PC/WSL por uptime)
2. [ ] Asignar responsable de mantenimiento (1 hora/mes)
3. [ ] Documentar runbook operativo

### Decisión híbrida (NO RECOMENDADA): Opción 2 temporal → Opción 3 después

Si se necesita CI/CD **YA** pero se quiere migrar a self-hosted después:
1. **Ahora:** Hacer repo público (15 min)
2. **Semana 1-2:** Workflows vuelven a funcionar
3. **Mes 1:** Setup self-hosted runner en paralelo
4. **Mes 2:** Migrar workflows + volver repo a privado

**Problema:** Doble esfuerzo (auditoría + setup runner); forks públicos permanecen.

---

## 9. Checklist final de decisión

Antes de ejecutar, el decisor debe confirmar:

### Para Opción 2 (Repo Público):
- [ ] ✅ Escaneo de seguridad revisado: 0 riesgos ALTOS confirmados
- [ ] ⏳ Auditoría de 7 imágenes completada: sin admin URLs/datos sensibles
- [ ] ✅ Equipo consciente: código y docs serán visibles públicamente
- [ ] ✅ No hay restricciones legales/contractuales de privacidad
- [ ] ✅ Blog es personal/profesional (no corporativo bajo NDA)
- [ ] ✅ Beneficio de portafolio público es deseable

### Para Opción 3 (Self-Hosted):
- [ ] ⏳ Infraestructura disponible: VPS aprovisionado O PC 24/7
- [ ] ⏳ Responsable operativo asignado: 1 hora/mes de mantenimiento
- [ ] ⏳ Runbook de mantenimiento documentado y aceptado
- [ ] ⏳ Presupuesto aprobado: $0 (local) o $5-15/mes (VPS)
- [ ] ✅ Privacidad es requisito mandatorio
- [ ] ✅ Código contiene lógica propietaria O cumplimiento regulatorio aplica

**Comando de decisión:**
```bash
# Tras revisar este documento, el decisor ejecuta:
echo "2" > .ci_decision  # O "3"
git add .ci_decision && git commit -m "decision: Opción [2|3] para CI/CD"
```

---

## 10. Anexos y evidencias

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Escaneo de secretos** | [`reports/security/secrets_scan.md`](../reports/security/secrets_scan.md) | Análisis exhaustivo de credenciales/datos sensibles |
| **Impacto en workflows** | [`reports/ci/workflows_actions_impact.md`](../reports/ci/workflows_actions_impact.md) | 39 workflows afectados, cambios requeridos por opción |
| **Runbook Opción 2** | [`docs/PUBLIC_REPO_READINESS.md`](PUBLIC_REPO_READINESS.md) | Checklist operativo para conversión a público |
| **Runbook Opción 3** | [`docs/SELF_HOSTED_RUNNER_PLAN.md`](SELF_HOSTED_RUNNER_PLAN.md) | Guía técnica de setup de runner |
| **Historial de runs** | [`reports/ci_runs/runs_all.json`](../reports/ci_runs/runs_all.json) | 50 últimos runs - 100% fallos desde 2025-10-27 21:07 |

**Referencias externas:**
- [GitHub Actions pricing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
- [Self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners)
- [Security hardening for runners](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**Próxima acción:** Decisor debe revisar este documento y ejecutar `echo "[2|3]" > .ci_decision` para proceder con el bloque operativo correspondiente.

**Fecha límite recomendada:** 2025-10-29 (48 horas) - CI/CD sigue bloqueado hasta decisión.
