# 🎛️ Hub Central — Panel de Estado

<div align="center">
  
**Versión**: 0.9.0  
**Última actualización**: 2025-10-20 10:30 UTC

</div>

---

## 📊 Resumen Global

| Métrica | Valor |
|---------|-------|
| **Total Instancias** | 2 |
| 🟢 **Healthy** | 1 |
| 🟡 **Degraded** | 1 |
| 🔴 **Offline** | 0 |
| **Uptime Promedio** | 97.5% |
| **Response Time Promedio** | 994ms |
| **Issues Abiertos** | 1 |
| **Blockers Críticos** | 1 |

---

## 🌐 Estado por Instancia

### 🟢 Pepecapiro Production

| | |
|---|---|
| **ID** | `pepecapiro-prod` |
| **Estado** | 🟢 **Healthy** |
| **URL** | [pepecapiro.com](https://pepecapiro.com) |
| **Repositorio** | [ppkapiro/pepecapiro-wp-theme](https://github.com/ppkapiro/pepecapiro-wp-theme) |
| **Versión** | 0.6.0 |
| **Environment** | Production |
| **Uptime** | 99.8% |
| **Response Time** | 738ms |
| **Issues** | 0 |
| **Último Check** | 2025-10-20 10:25 UTC |

**Servicios**:
- ✅ Auth: OK
- ✅ Home: OK
- ✅ Menus: OK
- ✅ Media: OK
- ⚠️ Settings: DRIFT

**Features**:
- ✅ API Gateway
- ✅ Webhooks
- ✅ Export Kit
- ✅ Hub Enabled

---

### 🟡 Pepecapiro Staging

| | |
|---|---|
| **ID** | `pepecapiro-staging` |
| **Estado** | 🟡 **Degraded** |
| **URL** | [staging.pepecapiro.com](https://staging.pepecapiro.com) |
| **Repositorio** | [ppkapiro/pepecapiro-wp-theme-staging](https://github.com/ppkapiro/pepecapiro-wp-theme-staging) |
| **Versión** | 0.7.0-alpha |
| **Environment** | Staging |
| **Uptime** | 95.2% |
| **Response Time** | 1250ms |
| **Issues** | 1 |
| **Último Check** | 2025-10-20 10:20 UTC |

**Servicios**:
- ✅ Auth: OK
- ✅ Home: OK
- ❌ Menus: **KO**
- ✅ Media: OK
- ⚠️ Settings: DRIFT

**Features**:
- ✅ API Gateway
- ✅ Webhooks
- ❌ Export Kit
- ✅ Hub Enabled

**Blockers** (1):
- 🔴 [#7: BLOCKER: Falta API_GATEWAY_TOKEN para trigger remoto](https://github.com/ppkapiro/pepecapiro-wp-theme/issues/7)

---

## 🚨 Incidentes Recientes

| Instancia | Fecha | Severidad | Mensaje | Estado |
|-----------|-------|-----------|---------|--------|
| pepecapiro-staging | 2025-10-18 14:30 | ⚠️ Warning | Menus verification failed: Expected 3 locations, found 2 | ✅ Resuelto (2025-10-19 09:00) |

---

## 📅 Próximos Checks Programados

| Instancia | Tipo | Fecha Programada |
|-----------|------|------------------|
| pepecapiro-prod | Health Check | 2025-10-20 10:35 UTC |
| pepecapiro-staging | Health Check | 2025-10-20 10:40 UTC |
| pepecapiro-prod | Weekly Audit | 2025-10-27 00:00 UTC |

---

## 📖 Documentación

- [HUB_OVERVIEW.md](./HUB_OVERVIEW.md) — Arquitectura completa del Hub
- [instances.json](./instances.json) — Configuración de instancias
- [hub_status.json](./hub_status.json) — Datos del estado agregado (JSON raw)
- [API_REFERENCE.md](../API_REFERENCE.md) — Endpoints de las instancias

---

## 🔧 Gestión

### Añadir Nueva Instancia

1. Editar [`instances.json`](./instances.json)
2. Validar endpoint: `curl https://tu-instancia.github.io/.../public/status.json`
3. Regenerar hub: `bash docs/hub/scripts/aggregate_hub_status.sh`
4. Commit y push

Ver [HUB_OVERVIEW.md § Configuración](./HUB_OVERVIEW.md#configuración) para detalles.

### Forzar Actualización

```bash
# Ejecutar workflow de agregación manualmente
gh workflow run hub-aggregation.yml

# O ejecutar script localmente
bash docs/hub/scripts/aggregate_hub_status.sh
```

---

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/ppkapiro/pepecapiro-wp-theme/issues)
- **Contacto**: admin@pepecapiro.com
- **Documentación**: [docs/](../README.md)

---

<div align="center">

**Hub Central v0.9.0** | Generado automáticamente cada 10 minutos

_Última actualización: 2025-10-20 10:30 UTC_

</div>

---

## 💡 Notas

Este panel consume datos de [`hub_status.json`](./hub_status.json), que es generado automáticamente por el workflow `hub-aggregation.yml`.

**Para dashboard interactivo**: En futuras versiones se implementará un panel HTML con JavaScript que renderice gráficos (Chart.js) y permita filtros en tiempo real.

**Actual**: Panel estático en Markdown (ideal para GitHub Pages sin JavaScript).
