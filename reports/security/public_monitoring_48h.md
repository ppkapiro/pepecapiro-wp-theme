# Monitoreo Post-Conversión Pública (48 horas)

**Inicio del período:** 2025-10-28 14:45 UTC  
**Fin proyectado:** 2025-10-30 14:45 UTC

**Objetivo:** Verificar que la conversión a repositorio público no introduce vulnerabilidades, exposición de datos sensibles, o comportamiento anómalo en workflows/forks.

---

## Security Features Activadas

**Timestamp:** 2025-10-28 14:45 UTC

| Feature | Status | Notas |
|---------|--------|-------|
| **Secret Scanning** | ✅ Enabled | Detecta tokens/passwords en commits |
| **Secret Scanning Push Protection** | ✅ Enabled | Bloquea pushes con secrets detectados |
| **Dependabot Security Updates** | ✅ Enabled | PRs automáticos para vulnerabilidades en deps |
| **Secret Scanning (non-provider patterns)** | ❌ Disabled | Opcional - patrones custom |
| **Secret Scanning (validity checks)** | ❌ Disabled | Opcional - valida tokens activos |

**Verificación:**
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/security-and-analysis
```

---

## Checklist de Monitoreo (48h)

### Día 1 (2025-10-28 - 2025-10-29)

**Hora 0-6h (14:45-20:45 UTC):**
- [x] ✅ Secret scanning activado (14:45 UTC)
- [x] ✅ Push protection activado (14:45 UTC)
- [x] ✅ Dependabot security updates activado (14:45 UTC)
- [ ] ⏳ Verificar alerts de secret scanning (Settings > Security > Code security):
  ```bash
  gh api /repos/ppkapiro/pepecapiro-wp-theme/secret-scanning/alerts
  ```
  **Criterio OK:** Array vacío `[]` o solo alertas cerradas (false positives)

- [ ] ⏳ Verificar forks del repo:
  ```bash
  gh api /repos/ppkapiro/pepecapiro-wp-theme/forks --jq '.[] | {owner: .owner.login, created: .created_at}'
  ```
  **Criterio OK:** 0 forks, o forks legítimos (no cuentas bot con nombres random)

**Hora 6-12h (20:45-02:45 UTC+1):**
- [ ] ⏳ Verificar que workflows schedule se ejecutan correctamente:
  ```bash
  gh run list --workflow=psi_metrics.yml --limit=1  # Schedule: 03:15 UTC
  gh run list --workflow=seo_audit.yml --limit=1   # Schedule: 03:17 UTC
  ```
  **Criterio OK:** Ambos con `conclusion: success`

- [ ] ⏳ Revisar logs de PSI Metrics run (verificar que PSI_API_KEY no se expuso):
  ```bash
  gh run view <run_id> --log | grep -i "PSI_API_KEY\|application.*password"
  ```
  **Criterio OK:** Solo `***` (masking activo) o "Secret source: Actions"

**Hora 12-24h (02:45-14:45 UTC+1):**
- [ ] ⏳ Verificar que no hay PRs externos sospechosos (desde forks):
  ```bash
  gh pr list --state=all --json author,createdAt,title
  ```
  **Criterio OK:** Solo PRs del propietario o colaboradores conocidos

- [ ] ⏳ Revisar issues/discussions por spam o actividad maliciosa:
  ```bash
  gh issue list --limit=20
  ```
  **Criterio OK:** Issues legítimos (si los hay) - no spam, no phishing links

---

### Día 2 (2025-10-29 - 2025-10-30)

**Hora 24-36h (14:45-02:45 UTC):**
- [ ] ⏳ Re-verificar secret scanning alerts:
  ```bash
  gh api /repos/ppkapiro/pepecapiro-wp-theme/secret-scanning/alerts
  ```
  **Criterio OK:** Sin alertas nuevas desde 24h previas

- [ ] ⏳ Verificar que Lighthouse runs siguen pasando (no regresión):
  ```bash
  gh run list --workflow=lighthouse.yml --limit=3 --json conclusion,createdAt
  ```
  **Criterio OK:** 3/3 con `conclusion: success` (si hubo pushes)

- [ ] ⏳ Revisar tráfico del repo (Settings > Insights > Traffic):
  - Clones/día: ¿pico anormal?
  - Visitors únicos: ¿aumento sospechoso?
  - Top referrers: ¿orígenes legítimos?
  
  **Criterio OK:** Tráfico bajo/normal (blog personal sin promoción pública reciente)

**Hora 36-48h (02:45-14:45 UTC):**
- [ ] ⏳ Verificar que weekly-audit.yml se ejecutó (schedule: domingo 02:00 UTC):
  ```bash
  gh run list --workflow=weekly-audit.yml --limit=1
  ```
  **Criterio OK:** Si es domingo/lunes - run con `conclusion: success`

- [ ] ⏳ Revisar Dependabot alerts (si aparecen):
  ```bash
  gh api /repos/ppkapiro/pepecapiro-wp-theme/dependabot/alerts
  ```
  **Criterio OK:** Array vacío `[]` o solo vulnerabilidades LOW/MEDIUM (evaluar si requieren action)

- [ ] ⏳ Snapshot final de salud CI/CD:
  ```bash
  gh run list --limit=10 --json workflowName,conclusion,createdAt > /tmp/ci_health_48h.json
  cat /tmp/ci_health_48h.json
  ```
  **Criterio OK:** > 90% runs con `conclusion: success` (ignorar Hub Aggregation si falla)

---

## Alertas y Umbrales

### Alerta CRÍTICA (requiere acción inmediata):

1. **Secret scanning alert activa (HIGH severity)**
   - Acción: Verificar el secret detectado → si es válido, regenerar inmediatamente
   - Comando: `gh secret set <SECRET_NAME> --body "nuevo_valor"`
   - Cerrar alert en GitHub UI tras remediar

2. **Fork con workflow malicioso ejecutándose**
   - Síntoma: Fork intenta acceder a secrets o modifica workflows para exfiltrar datos
   - GitHub protege secrets por defecto en forks, pero revisar manualmente
   - Acción: Contactar GitHub Support si es ataque coordinado

3. **Logs de workflow exponen secret sin masking**
   - Síntoma: `grep` muestra valor de WP_APP_PASSWORD o PSI_API_KEY en texto plano
   - Acción: Regenerar secret comprometido, cerrar run público, reportar a GitHub si es bug de masking

### Alerta MEDIA (monitoreo continuo):

1. **Incremento anormal de forks (> 5 en 24h)**
   - Revisar perfiles de cuentas que forkearon (bots vs humanos)
   - Si legítimos: OK; si bots: evaluar si es scraping automatizado

2. **PRs externos sin contexto claro**
   - Revisar código propuesto (NO hacer merge sin review manual exhaustivo)
   - Verificar que no inyectan código malicioso en workflows

3. **Dependabot alerts para deps críticas (Python, Node.js)**
   - Evaluar severity (LOW = ignorar temporalmente; HIGH/CRITICAL = actualizar deps)

### Alerta BAJA (informativa):

1. **Tráfico del repo aumenta moderadamente**
   - Probable: Indexación por motores de búsqueda, agregadores de GitHub
   - OK si referrers son legítimos (GitHub Explore, Google)

2. **Issues/discussions de terceros con preguntas legítimas**
   - Responder si es pertinente; cerrar si es spam

---

## Comandos de Verificación Rápida

### Secret scanning alerts (diario)
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/secret-scanning/alerts --jq '.[] | {number: .number, secret_type: .secret_type, state: .state, created_at: .created_at}'
```

### Forks (diario)
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/forks --jq 'length'  # Cuenta de forks
```

### Workflows health (diario)
```bash
gh run list --limit=10 --json workflowName,conclusion | jq 'group_by(.conclusion) | map({conclusion: .[0].conclusion, count: length})'
```

### Dependabot alerts (semanal)
```bash
gh api /repos/ppkapiro/pepecapiro-wp-theme/dependabot/alerts --jq '.[] | {number: .number, severity: .security_advisory.severity, package: .dependency.package.name}'
```

### Tráfico (semanal - requiere UI)
GitHub UI: Settings > Insights > Traffic (no hay API pública para clones/views)

---

## Reporte Final (Post-48h)

**Template para agregar a DTC tras 48h:**

```markdown
**Monitoreo 48h post-conversión (2025-10-28 a 2025-10-30):**
- ✅ Secret scanning: <N> alertas (todas cerradas/false positives)
- ✅ Forks: <N> forks detectados (todos legítimos / ninguno sospechoso)
- ✅ Workflows: <X>/<Y> runs exitosos (>90% success rate)
- ✅ Dependabot: <N> alertas (severidad: LOW/MEDIUM/HIGH - todas evaluadas)
- ✅ PRs/Issues externos: <N> detectados (todos legítimos / cerrados como spam)
- ✅ Logs auditados: 0 secrets expuestos sin masking
- ✅ **Conclusión:** Repositorio público operando normalmente sin incidentes de seguridad.
```

---

## Rollback Plan (Si se detectan problemas críticos)

**Escenario A: Secret comprometido detectado**
1. Regenerar secret en origen (WordPress, Google Cloud Console, etc.)
2. Actualizar GitHub Secret: `gh secret set <NAME> --body "nuevo_valor"`
3. Re-run workflows fallidos tras actualización

**Escenario B: Actividad maliciosa sostenida (forks/PRs sospechosos)**
1. Deshabilitar forks temporalmente: Settings > General > Uncheck "Allow forking"
2. Cerrar PRs/Issues externos sin review
3. Evaluar si requiere volver a privado (Opción 3: Self-hosted runner)

**Escenario C: Workflow logs exponen secrets (bug de masking)**
1. Reportar a GitHub Support inmediatamente
2. Regenerar secret expuesto
3. Considerar agregar step de sanitización manual en workflows:
   ```yaml
   - name: Sanitize logs
     run: echo "LOGS OCULTOS POR PRIVACIDAD" && exit 1
   ```

---

**Responsable:** Copilot (agente autónomo) + revisión manual del propietario del repo  
**Próxima revisión:** 2025-10-30 14:45 UTC (fin de período 48h)
