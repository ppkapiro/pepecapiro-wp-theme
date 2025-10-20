# Hub Central — Arquitectura de Gestión Multi-Instancia

**Versión**: 0.9.0  
**Última actualización**: 2025-10-20  
**Propósito**: Centralizar monitorización y gestión de múltiples instancias del ecosistema WordPress + GitHub

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Componentes](#componentes)
4. [Configuración](#configuración)
5. [Casos de Uso](#casos-de-uso)
6. [Troubleshooting](#troubleshooting)
7. [Roadmap](#roadmap)

---

## Introducción

### ¿Qué es el Hub Central?

El **Hub Central** es un sistema de agregación que:
- **Recopila** el estado de múltiples instancias del ecosistema pepecapiro-wp-theme
- **Consolida** métricas de salud (uptime, response time, issues)
- **Alerta** sobre incidentes críticos (blockers, servicios offline)
- **Visualiza** un panel unificado con el estado global

### ¿Por qué usar un Hub?

**Sin Hub**:
- Debes revisar manualmente cada repositorio (status.json individual)
- No hay vista consolidada del estado global
- Detección de problemas lenta (revisión manual)

**Con Hub**:
- ✅ Vista unificada de todas las instancias
- ✅ Detección automática de problemas (health checks periódicos)
- ✅ Alertas proactivas (issues críticos, servicios degradados)
- ✅ Métricas globales (uptime promedio, response time agregado)

### Casos de Uso

1. **Multi-sitio**: Gestionar varios sitios WordPress desde un panel central
2. **Ambientes**: Monitorizar producción, staging, desarrollo simultáneamente
3. **Agencia**: Administrar sitios de múltiples clientes
4. **Disaster Recovery**: Detectar rápidamente fallos en cualquier instancia

---

## Arquitectura

### Vista General

```
┌─────────────────────────────────────────────────────────────┐
│                        HUB CENTRAL                          │
│                     (Agregador Central)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           hub_status.json (Generado)                 │  │
│  │  - Total instances: 2                                │  │
│  │  - Healthy: 1, Degraded: 1, Offline: 0              │  │
│  │  - Global metrics: uptime, response time, issues    │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ▲                                │
│                            │ Aggregation (poll every 10m)  │
│                            │                                │
│              ┌─────────────┴─────────────┐                  │
│              │                           │                  │
└──────────────┼───────────────────────────┼──────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Instance: Production   │  │    Instance: Staging     │
│  (pepecapiro-wp-theme)   │  │ (pepecapiro-wp-staging)  │
│                          │  │                          │
│  status.json             │  │  status.json             │
│  - version: 0.6.0        │  │  - version: 0.7.0-alpha  │
│  - services: OK          │  │  - services: KO (menus)  │
│  - issues: 0             │  │  - issues: 1             │
│                          │  │                          │
│  WordPress               │  │  WordPress               │
│  - URL: pepecapiro.com   │  │  - URL: staging.pepe...  │
│  - REST API: ✅          │  │  - REST API: ✅          │
└──────────────────────────┘  └──────────────────────────┘
```

### Flujo de Datos

1. **Cada instancia** genera su propio `status.json` (via `health-dashboard.yml`)
2. **Hub** hace polling cada 10 minutos a los endpoints de cada instancia:
   ```
   GET https://ppkapiro.github.io/pepecapiro-wp-theme/public/status.json
   GET https://ppkapiro.github.io/pepecapiro-wp-theme-staging/public/status.json
   ```
3. **Hub** agrega los datos:
   - Cuenta instancias por estado (healthy/degraded/offline)
   - Calcula métricas globales (uptime promedio, response time)
   - Detecta blockers (issues con label "blocker")
4. **Hub** genera `hub_status.json` con la vista consolidada
5. **Panel (index.md)** consume `hub_status.json` y renderiza el dashboard

---

## Componentes

### 1. instances.json (Configuración)

**Ubicación**: `docs/hub/instances.json`

**Propósito**: Define qué instancias monitorizar y cómo contactarlas.

**Estructura**:
```json
{
  "hub_version": "0.9.0",
  "instances": [
    {
      "id": "pepecapiro-prod",
      "name": "Pepecapiro Production",
      "url": "https://pepecapiro.com",
      "status_endpoint": "https://ppkapiro.github.io/.../public/status.json",
      "environment": "production",
      "features": {
        "api_gateway": true,
        "webhooks": true,
        "export_kit": true,
        "hub_enabled": true
      },
      "monitoring": {
        "health_check_interval": "5m",
        "alert_on_failure": true
      }
    }
  ],
  "aggregation_config": {
    "poll_interval": "10m",
    "timeout": "30s",
    "retry_attempts": 3
  }
}
```

**Campos clave**:
- `id`: Identificador único (slug)
- `status_endpoint`: URL pública del status.json de la instancia
- `environment`: `production` | `staging` | `development`
- `monitoring.health_check_interval`: Frecuencia de checks
- `aggregation_config.poll_interval`: Frecuencia de polling del hub

### 2. hub_status.json (Estado Agregado)

**Ubicación**: `docs/hub/hub_status.json`

**Propósito**: Vista consolidada del estado de todas las instancias (auto-generado).

**Estructura**:
```json
{
  "hub_version": "0.9.0",
  "generated_at": "2025-10-20T10:30:00Z",
  "summary": {
    "total_instances": 2,
    "healthy": 1,
    "degraded": 1,
    "offline": 0
  },
  "instances": [
    {
      "id": "pepecapiro-prod",
      "status": "healthy",
      "version": "0.6.0",
      "health_details": { "auth": "OK", "home": "OK", ... },
      "issues": 0,
      "uptime_percentage": 99.8,
      "response_time_ms": 738
    }
  ],
  "global_metrics": {
    "average_uptime": 97.5,
    "average_response_time_ms": 994,
    "total_issues": 1
  },
  "recent_incidents": [...]
}
```

**Generación**:
```bash
# Manual
bash docs/hub/scripts/aggregate_hub_status.sh

# Automatizado (GitHub Actions)
# Ejecutar workflow hub-aggregation.yml cada 10 minutos
```

### 3. HUB_OVERVIEW.md (Documentación)

**Ubicación**: `docs/hub/HUB_OVERVIEW.md` (este archivo)

**Propósito**: Explicar arquitectura, configuración y uso del Hub.

### 4. index.md (Panel de Visualización)

**Ubicación**: `docs/hub/index.md`

**Propósito**: Dashboard HTML/Markdown consumiendo `hub_status.json`.

**Tecnología**: Markdown con embeds de JSON o HTML simple con JavaScript para renderizar.

---

## Configuración

### Añadir Nueva Instancia

1. **Editar `instances.json`**:
   ```json
   {
     "id": "cliente-nuevo",
     "name": "Sitio Cliente Nuevo",
     "url": "https://cliente-nuevo.com",
     "repo": "miorganizacion/cliente-nuevo-wp",
     "status_endpoint": "https://miorganizacion.github.io/cliente-nuevo-wp/public/status.json",
     "environment": "production",
     "owner": "mi-organizacion",
     "contact": "admin@cliente-nuevo.com",
     "features": {
       "api_gateway": true,
       "webhooks": false,
       "export_kit": true,
       "hub_enabled": true
     },
     "monitoring": {
       "health_check_interval": "5m",
       "alert_on_failure": true,
       "weekly_audit": true
     }
   }
   ```

2. **Validar status_endpoint**:
   ```bash
   curl -s https://miorganizacion.github.io/cliente-nuevo-wp/public/status.json | jq
   ```

3. **Regenerar hub_status.json**:
   ```bash
   bash docs/hub/scripts/aggregate_hub_status.sh
   ```

4. **Commitear cambios**:
   ```bash
   git add docs/hub/instances.json docs/hub/hub_status.json
   git commit -m "feat(hub): Add cliente-nuevo instance"
   git push
   ```

### Configurar Polling Automatizado

**Crear workflow `hub-aggregation.yml`**:

```yaml
name: Hub Aggregation

on:
  schedule:
    - cron: '*/10 * * * *'  # Cada 10 minutos
  workflow_dispatch:

jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: |
          sudo apt-get install -y jq curl
      
      - name: Aggregate hub status
        run: |
          bash docs/hub/scripts/aggregate_hub_status.sh
      
      - name: Commit updated hub_status.json
        run: |
          git config user.name "Hub Aggregator"
          git config user.email "bot@pepecapiro.com"
          git add docs/hub/hub_status.json
          git commit -m "chore(hub): Update hub_status.json [skip ci]" || exit 0
          git push
```

**Habilitar workflow**:
```bash
git add .github/workflows/hub-aggregation.yml
git commit -m "feat(hub): Add automated aggregation workflow"
git push
```

---

## Casos de Uso

### Caso 1: Agencia con 10 Clientes

**Configuración**:
- 10 instancias en `instances.json` (una por cliente)
- `poll_interval: "15m"` (para reducir carga)
- `alert_on_failure: true` para clientes premium, `false` para plan básico

**Beneficios**:
- Vista única de salud de todos los sitios
- Alertas automáticas si algún sitio falla
- Reportes mensuales (uptime promedio por cliente)

### Caso 2: Ambientes de Desarrollo

**Configuración**:
- 3 instancias: `production`, `staging`, `development`
- `production`: `health_check_interval: "5m"`, alertas activas
- `staging`/`development`: `health_check_interval: "30m"`, sin alertas

**Beneficios**:
- Validar cambios en staging antes de production
- Detectar regressions en development
- Métricas comparativas entre ambientes

### Caso 3: Multi-Región

**Configuración**:
- Instancias en diferentes regiones (US, EU, ASIA)
- `hub_status.json` incluye campo `region`
- Dashboard agrupa por región

**Beneficios**:
- Monitorización geográfica
- Detección de problemas regionales (CDN, DNS)
- Análisis de performance por región

---

## Troubleshooting

### Hub no actualiza hub_status.json

**Causas**:
- Workflow `hub-aggregation.yml` no ejecutándose (deshabilitado o error)
- Script `aggregate_hub_status.sh` con errores
- Permisos insuficientes para commit (GitHub token)

**Solución**:
```bash
# Verificar últimas ejecuciones
gh run list --workflow=hub-aggregation.yml --limit 5

# Ver logs del último run
gh run view $(gh run list --workflow=hub-aggregation.yml --limit 1 --json databaseId --jq '.[0].databaseId') --log

# Ejecutar manualmente
gh workflow run hub-aggregation.yml

# Validar script localmente
bash docs/hub/scripts/aggregate_hub_status.sh
git diff docs/hub/hub_status.json
```

### Instancia aparece como "offline" incorrectamente

**Causas**:
- `status_endpoint` inválido (404, 403)
- Instancia no publica `status.json` (workflow `health-dashboard.yml` no ejecutado)
- Timeout en polling (30s default puede ser insuficiente)

**Solución**:
```bash
# Validar endpoint manualmente
curl -sL -w "%{http_code}" -o /dev/null https://..../public/status.json

# Si es 404, ejecutar health-dashboard en la instancia
gh workflow run health-dashboard.yml --repo ppkapiro/pepecapiro-wp-theme

# Aumentar timeout en instances.json
# "aggregation_config.timeout": "60s"
```

### Métricas globales incorrectas

**Causas**:
- Instancias offline no excluidas del cálculo de promedios
- Datos desactualizados (polling interval muy largo)

**Solución**:
- Modificar script de agregación para excluir instancias offline:
  ```bash
  # aggregate_hub_status.sh
  # Filtrar solo instancias con status != "offline"
  jq '[.instances[] | select(.status != "offline")] | add | . / length' hub_status.json
  ```
- Reducir `poll_interval` a 5m para datos más frescos

### Dashboard (index.md) muestra datos obsoletos

**Causas**:
- Cache del navegador
- GitHub Pages no actualizó (tarda ~2-3 minutos tras commit)

**Solución**:
```bash
# Forzar rebuild de GitHub Pages
git commit --allow-empty -m "chore: Trigger GitHub Pages rebuild"
git push

# Limpiar cache del navegador (Ctrl+F5)
```

---

## Roadmap

### v0.9.1 (Próxima versión menor)

- [ ] Script `aggregate_hub_status.sh` funcional (actualmente solo JSON estático)
- [ ] Dashboard HTML interactivo (gráficos de uptime con Chart.js)
- [ ] Alertas vía Slack/Discord (webhook en caso de instancia offline)

### v0.10.0 (Próxima versión mayor)

- [ ] API REST del Hub (GET /hub/status, GET /hub/instances/:id)
- [ ] Autenticación para añadir instancias vía API
- [ ] Histórico de métricas (almacenar uptime/response_time en DB)
- [ ] Gráficos de tendencias (uptime últimos 30 días)

### v1.0.0 (Versión estable)

- [ ] Soporte para instancias no basadas en pepecapiro-wp-theme (custom status endpoints)
- [ ] Multi-hub federation (hubs de hubs)
- [ ] Mobile app para alertas push

---

## Scripts de Ejemplo

### aggregate_hub_status.sh (Pseudocódigo)

```bash
#!/usr/bin/env bash
# Script de agregación (implementación futura)

set -euo pipefail

INSTANCES_FILE="docs/hub/instances.json"
HUB_STATUS_FILE="docs/hub/hub_status.json"

# Leer instancias
INSTANCES=$(jq -r '.instances[] | .id + "|" + .status_endpoint' "$INSTANCES_FILE")

# Inicializar counters
TOTAL=0
HEALTHY=0
DEGRADED=0
OFFLINE=0

# Agregar datos
echo '{"hub_version":"0.9.0","generated_at":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","instances":[]}' > "$HUB_STATUS_FILE.tmp"

while IFS='|' read -r ID ENDPOINT; do
  TOTAL=$((TOTAL + 1))
  
  # Fetch status
  STATUS_JSON=$(curl -sf --max-time 30 "$ENDPOINT" || echo '{"services":{"auth":"KO"}}')
  
  # Determinar estado
  if echo "$STATUS_JSON" | jq -e '.services.auth == "OK"' > /dev/null; then
    if echo "$STATUS_JSON" | jq -e '.issues > 0' > /dev/null; then
      DEGRADED=$((DEGRADED + 1))
      STATUS="degraded"
    else
      HEALTHY=$((HEALTHY + 1))
      STATUS="healthy"
    fi
  else
    OFFLINE=$((OFFLINE + 1))
    STATUS="offline"
  fi
  
  # Añadir a hub_status.json
  echo "$STATUS_JSON" | jq --arg id "$ID" --arg status "$STATUS" \
    '{id: $id, status: $status, version: .version, health_details: .services, issues: .issues}' \
    >> "$HUB_STATUS_FILE.tmp"
done <<< "$INSTANCES"

# Generar resumen
jq --argjson total "$TOTAL" --argjson healthy "$HEALTHY" --argjson degraded "$DEGRADED" --argjson offline "$OFFLINE" \
  '.summary = {total_instances: $total, healthy: $healthy, degraded: $degraded, offline: $offline}' \
  "$HUB_STATUS_FILE.tmp" > "$HUB_STATUS_FILE"

rm "$HUB_STATUS_FILE.tmp"

echo "✅ Hub status aggregated: $HEALTHY healthy, $DEGRADED degraded, $OFFLINE offline"
```

---

## Conclusión

El **Hub Central v0.9.0** proporciona una infraestructura sólida para gestionar múltiples instancias del ecosistema WordPress + GitHub.

**Estado actual**:
- ✅ Arquitectura diseñada
- ✅ Formato de datos definido (instances.json, hub_status.json)
- ✅ Documentación completa (este documento)
- ⏸️ Script de agregación (a implementar en v0.9.1)
- ⏸️ Dashboard interactivo (a implementar en v0.9.1)

**Para empezar**:
1. Configura `docs/hub/instances.json` con tus instancias
2. Crea workflow `hub-aggregation.yml` (ver sección Configuración)
3. Ejecuta manualmente: `gh workflow run hub-aggregation.yml`
4. Consulta `docs/hub/hub_status.json` para ver el estado agregado

---

**Relacionado**:
- `docs/hub/instances.json` (configuración)
- `docs/hub/hub_status.json` (estado agregado)
- `docs/hub/index.md` (panel de visualización)
- `docs/API_REFERENCE.md` (endpoints de instancias individuales)
