# Impacto de Visibilidad del Repositorio en Workflows de GitHub Actions

**Fecha de análisis:** 2025-10-28  
**Estado actual del repo:** PRIVADO (ppkapiro/pepecapiro-wp-theme)  
**GitHub Actions:** Habilitadas, allowed_actions: all  
**Total de workflows:** 39

---

## Contexto del problema

Desde el 2025-10-27 21:07 UTC, **TODOS los workflows están fallando instantáneamente** (4 segundos de duración) sin ejecutar ningún step. Diagnóstico: **límite de minutos de GitHub Actions agotado** para repositorios privados.

**Último run exitoso:** 2025-10-21 16:45 UTC (run #18691226897 - Lighthouse)  
**Runs analizados:** 50 últimos - 100% fallos  

---

## Workflows críticos afectados

| Workflow | Trigger | Runner | ¿Requiere minutos? | ¿Crítico? | Impacto del bloqueo |
|----------|---------|--------|-------------------|-----------|---------------------|
| **lighthouse.yml** | push, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🔴 CRÍTICO | Sin métricas LCP/CLS/Performance - Phase 4 bloqueada |
| **seo_audit.yml** | push, schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🔴 CRÍTICO | Sin validación meta tags/OG/JSON-LD |
| **smoke-tests.yml** | push, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🔴 CRÍTICO | Sin validación disponibilidad URLs |
| **psi_metrics.yml** | schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟡 ALTO | Sin métricas PSI automáticas |
| **weekly-audit.yml** | schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟡 ALTO | Sin auditoría semanal estado blog |
| **hub-aggregation.yml** | schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟡 ALTO | Sin agregación de status |
| **status.yml** | push, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟢 MEDIO | Fallback: chequeo manual |
| **ui-gates.yml** | push, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟢 MEDIO | Validación CSS tokens bloqueada |
| **verify-settings.yml** | schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟢 MEDIO | Sin verificación periódica config WP |
| **webhook-github-to-wp.yml** | push, release | ubuntu-latest | ✅ SÍ | 🟢 BAJO | Webhooks externos no dependen de esto |
| **cleanup-test-posts.yml** | schedule, workflow_dispatch | ubuntu-latest | ✅ SÍ | 🟢 BAJO | Limpieza manual alternativa disponible |
| Otros 28 workflows | Variados | ubuntu-latest | ✅ SÍ | 🟢 BAJO-MEDIO | Operación no crítica o manual |

**Total workflows con runs-on ubuntu-latest/windows-latest:** 39/39 (100%)  
**Total workflows bloqueados:** 39/39 (100%)

---

## Análisis de opciones

### Opción 1: Aumentar minutos GitHub Actions (plan de pago) ❌ DESCARTADA
- **Costo:** Variable según plan (Team ~$4/usuario/mes + minutos adicionales)
- **Problema:** Inviable si el usuario no desea pagar o si el límite se agotó por mal uso

### Opción 2: Convertir repositorio a PÚBLICO ✅ VIABLE
**Impacto en workflows:**
- ✅ **Minutos ilimitados** para repos públicos (Linux runners)
- ✅ **CERO cambios en YAML** - todos los workflows funcionan igual
- ✅ Secrets siguen protegidos en Actions Secrets (no se exponen)
- ⚠️ **RIESGO:** Exposición de código, documentación, evidencias, capturas

**Cambios operativos:**
- Ninguno en workflows (sintaxis/estructura igual)
- Secrets **NO** se exponen automáticamente (quedan en Settings > Secrets)
- Artifacts públicos por defecto (pueden contener URLs/datos sensibles)
- Logs de Actions visibles públicamente (cuidado con `echo` de variables)

**Validaciones necesarias:**
1. Escaneo de secretos/credenciales hard-coded
2. Revisión de `evidence/`, `reports/`, `docs/` (capturas, URLs internas)
3. Confirmar `.gitignore` cubre `secrets/`, `.env`, `*.key`
4. Sanitizar artifacts (assert_summary, lighthouse reports)

### Opción 3: Self-Hosted Runner ✅ VIABLE
**Impacto en workflows:**
- ✅ **Cero consumo de minutos GitHub** (runner local)
- ⚠️ Requiere cambio en **cada workflow**: `runs-on: self-hosted` (o etiqueta personalizada)
- ⚠️ Dependencia de infraestructura local (PC/WSL encendido 24/7 o VPS)
- ✅ Repo sigue privado - sin exposición de código

**Cambios operativos por workflow:**
```yaml
# ANTES
jobs:
  lighthouse:
    runs-on: ubuntu-latest

# DESPUÉS
jobs:
  lighthouse:
    runs-on: self-hosted  # O [self-hosted, linux, x64]
```

**Requisitos:**
- Máquina con 2+ vCPU, 2+ GB RAM, Linux/Windows/macOS
- Instalación de dependencias (Node.js, Python, Chrome/Chromium, etc.)
- Registro del runner en Settings > Actions > Runners
- Mantenimiento: actualizaciones, limpieza de workspace, logs

**Workflows afectados (todos 39):**
- Lighthouse: requiere Chrome/Chromium instalado
- PSI metrics: requiere Python + requests
- Smoke tests: requiere curl/wget
- SEO audit: requiere Python + BeautifulSoup/lxml
- Cleanup/publish: requieren WP-CLI o REST API access

---

## Comparativa de compatibilidad

| Aspecto | Opción 2 (Público) | Opción 3 (Self-Hosted) |
|---------|-------------------|------------------------|
| **Cambios en workflows** | 0 cambios | 39 archivos a modificar (`runs-on`) |
| **Instalación de software** | N/A (preinstalado en runners GitHub) | Manual (Node, Python, Chrome, etc.) |
| **Artifacts** | Públicos por defecto | Privados (almacenados localmente) |
| **Logs** | Públicos | Privados |
| **Secrets** | Protegidos (Actions Secrets) | Protegidos (Actions Secrets o local .env) |
| **Velocidad de queue** | Inmediata (runners GitHub pool) | Depende de disponibilidad runner local |
| **Concurrencia** | Ilimitada (múltiples jobs en paralelo) | 1 job simultáneo por runner (o configurar múltiples) |
| **Mantenimiento** | Cero | Alto (actualizaciones OS, dependencias, limpieza) |

---

## Riesgos específicos por opción

### Opción 2: Repositorio público
| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Exposición de URLs internas de Hostinger en reports | 🔴 ALTA | Escaneo + sanitización antes de hacer público |
| Capturas de pantalla con datos sensibles en `evidence/` | 🟡 MEDIA | Auditoría manual + redacción o eliminación |
| Credenciales hard-coded en scripts/configs | 🔴 ALTA | Escaneo con `gitleaks` o `truffleHog` |
| Application Passwords de WP en artifacts/logs | 🔴 ALTA | Revisar workflows que usan `WP_APP_PASSWORD` |
| Artifacts con `assert_summary.txt` expuestos | 🟢 BAJA | Sanitizar o aceptar (métricas públicas OK) |
| Fork no autorizado del código del tema | 🟢 BAJA | Aceptable (código GPL-like de WP) |

### Opción 3: Self-hosted runner
| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Runner comprometido expone secrets locales | 🟡 MEDIA | Usuario dedicado, no root; secrets en Actions |
| PC/WSL apagado = workflows colgados | 🟡 MEDIA | VPS alternativa o timeout agresivo en workflows |
| Fallo de disco local pierde artifacts | 🟢 BAJA | Backup periódico de `_work/` del runner |
| Actualizaciones de runner no automáticas | 🟢 BAJA | Cron job para `./run.sh` con auto-update |
| Consumo de ancho de banda (artifacts grandes) | 🟢 BAJA | Configurar `retention-days: 7` en artifacts |

---

## Recomendación preliminar (basada en fricción técnica)

### SI prioridad = **Velocidad de recuperación** → Opción 2 (Público)
- ✅ Cero cambios en workflows
- ✅ Disponible en <1 hora (tras auditoría de secretos)
- ⚠️ Requiere limpieza manual de docs/evidencias

### SI prioridad = **Privacidad/Cumplimiento** → Opción 3 (Self-Hosted)
- ✅ Código y docs siguen privados
- ⚠️ Requiere 2-4 horas de setup inicial
- ⚠️ Dependencia operativa de infraestructura local/VPS

---

## Workflows que NO funcionarán igual con self-hosted (edge cases)

| Workflow | Problema potencial | Solución |
|----------|-------------------|----------|
| **lighthouse.yml** | Chrome/Chromium no instalado por defecto | `apt install chromium-browser` en runner |
| **psi_metrics.yml** | Python requests library | `pip install requests` en runner |
| **seo_audit.yml** | BeautifulSoup4/lxml | `pip install beautifulsoup4 lxml` en runner |
| Todos | Actions de marketplace pueden requerir Docker | Instalar Docker en runner host |

**Nota:** GitHub-hosted runners tienen **cientos de herramientas preinstaladas** ([lista completa](https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2204-Readme.md)). Self-hosted requiere instalarlas manualmente.

---

## Siguiente paso

Ejecutar **escaneo de secretos** (Task 2) para determinar viabilidad de Opción 2. Si hay riesgos ALTOS, Opción 3 es mandatoria.

**Comando de decisión (para usuario):**
```bash
# Tras revisar DECISION_BRIEF_OPTION2_vs_OPTION3.md:
echo "2" > .ci_decision  # O "3"
```
