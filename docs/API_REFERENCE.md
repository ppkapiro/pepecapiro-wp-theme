# API Reference — Automation Gateway

**Versión**: 0.7.0  
**Última actualización**: 2025-10-20

Este documento describe los endpoints disponibles para interactuar con el sistema de automatización de pepecapiro-wp-theme.

## Endpoints

### 1. GET /status — Estado del Sistema

**URL completa**: `https://ppkapiro.github.io/pepecapiro-wp-theme/public/status.json`  
*Alternativa via raw*: `https://raw.githubusercontent.com/ppkapiro/pepecapiro-wp-theme/main/public/status.json`

**Descripción**: Devuelve el estado actualizado de todos los servicios del ecosistema WordPress.

**Autenticación**: No requerida (público)

**Método**: `GET`

**Respuesta exitosa** (200 OK):
```json
{
  "version": "0.6.0",
  "timestamp": "2025-10-20T17:00:00Z",
  "services": {
    "auth": "OK",
    "home": "OK",
    "menus": "OK",
    "media": "OK",
    "settings": "DRIFT",
    "polylang": "Yes"
  },
  "health": "healthy",
  "issues": 0,
  "last_update": "2025-10-20T17:00:00Z"
}
```

**Campos**:
- `version` (string): Versión del sistema
- `timestamp` (string ISO 8601): Momento de la última actualización
- `services` (object): Estado de cada servicio (OK, KO, DRIFT, SKIP)
- `health` (string): Estado global (healthy, degraded, critical)
- `issues` (number): Cantidad de issues de monitoring abiertos
- `last_update` (string ISO 8601): Timestamp de la última verificación

**Ejemplo cURL**:
```bash
curl -sSL https://ppkapiro.github.io/pepecapiro-wp-theme/public/status.json
```

**Actualización**: Automática cada 6 horas via `health-dashboard.yml` (cron).

---

### 2. POST /trigger — Ejecutar Automatización

**URL completa**: `https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches`

**Descripción**: Dispara workflows de automatización mediante `repository_dispatch`. Requiere autenticación con token de GitHub.

**Autenticación**: ✅ Requerida — Bearer Token de GitHub (scope `repo`)

**Método**: `POST`

**Headers requeridos**:
```
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
Content-Type: application/json
```

**Payload** (JSON):
```json
{
  "event_type": "automation-trigger",
  "client_payload": {
    "action": "sync-content | rebuild-dashboard | run-verifications | cleanup-test-data",
    "target": "opcional",
    "client": "nombre_del_cliente"
  }
}
```

**Acciones disponibles**:
- `sync-content`: Sincroniza contenido desde `content/` hacia WordPress
- `rebuild-dashboard`: Regenera `status.json` y ejecuta health checks
- `run-verifications`: Ejecuta verify-home, verify-menus, verify-media, verify-settings
- `cleanup-test-data`: Limpia posts/páginas de prueba antiguos

**Respuesta exitosa** (204 No Content):
```
(Sin body, workflow lanzado en segundo plano)
```

**Errores comunes**:
- `401 Unauthorized`: Token inválido o expirado
- `404 Not Found`: Repositorio o endpoint incorrecto
- `422 Unprocessable Entity`: Payload malformado

**Ejemplo cURL**:
```bash
# Rebuild dashboard
curl -X POST \
  -H "Authorization: Bearer ghp_xxxxxxxxxxxxx" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches \
  -d '{
    "event_type": "automation-trigger",
    "client_payload": {
      "action": "rebuild-dashboard",
      "client": "external-monitor"
    }
  }'

# Run verifications
curl -X POST \
  -H "Authorization: Bearer ghp_xxxxxxxxxxxxx" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches \
  -d '{
    "event_type": "automation-trigger",
    "client_payload": {
      "action": "run-verifications"
    }
  }'
```

**Verificación de ejecución**:
```bash
# Listar últimas ejecuciones
gh run list --workflow=api-automation-trigger.yml --limit 5
```

**Timeout**: Los workflows tienen timeout por defecto de 60 minutos. Cada acción específica puede tener su propio timeout.

---

## Autenticación

### Token de GitHub (para /trigger)

⚠️ **BLOCKER PENDIENTE**: No existe `API_GATEWAY_TOKEN` en los secrets del repositorio.

**Pasos para crear el token**:

1. Ir a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generar nuevo token con scopes:
   - `repo` (acceso completo al repositorio)
   - `workflow` (ejecutar workflows)
3. Copiar el token generado (formato `ghp_...`)
4. Añadir como secret en el repositorio:
   ```bash
   gh secret set API_GATEWAY_TOKEN
   ```
5. Configurar en clientes externos que necesiten disparar automatizaciones

**Alternativa con GitHub App**: Para mayor seguridad, considerar usar una GitHub App con permisos granulares.

---

## Códigos de Respuesta HTTP

| Código | Significado | Acción |
|--------|-------------|--------|
| 200 OK | Solicitud exitosa (GET /status) | Procesar response |
| 204 No Content | Trigger aceptado y procesando | Verificar workflow run |
| 401 Unauthorized | Token inválido o faltante | Regenerar/verificar token |
| 404 Not Found | Endpoint o repo no encontrado | Verificar URL |
| 422 Unprocessable Entity | Payload malformado | Revisar JSON y campos |
| 500 Internal Server Error | Error en servidor GitHub | Reintentar más tarde |

---

## Rate Limits

**GitHub API**:
- Autenticado: 5,000 requests/hora
- No autenticado (GET /status via raw.githubusercontent.com): Sin límite específico, pero sujeto a fair use

**Recomendación**: Para monitoreo continuo, cachear `status.json` localmente y consultar cada 6h (sincronizado con cron de actualización).

---

## Webhooks (Fase 2)

Ver sección de Webhooks Bidireccionales (en desarrollo) para:
- GitHub → WordPress (push events, release events)
- WordPress → GitHub (post publicado, actualización de contenido)

---

## Troubleshooting

### Error: "Resource not accessible by integration"
**Causa**: Token sin scope `repo` o `workflow`.  
**Solución**: Regenerar token con permisos completos.

### Workflow no se ejecuta tras POST /trigger
**Causa**: `event_type` incorrecto o workflow no listening a ese tipo.  
**Solución**: Verificar que `api-automation-trigger.yml` tiene `repository_dispatch: types: [automation-trigger]`.

### Status.json desactualizado
**Causa**: `health-dashboard.yml` no ejecutándose.  
**Solución**: Verificar cron o ejecutar manualmente:
```bash
gh workflow run health-dashboard.yml
```

---

## Próximas Mejoras (Roadmap)

- [ ] Autenticación con API Key dedicada (no reutilizar token personal)
- [ ] Endpoint PATCH para actualizar configuración dinámica
- [ ] Métricas de uso de API (rate limit, requests/día)
- [ ] Webhooks salientes configurables
- [ ] Dashboard interactivo HTML (además del JSON)

---

**Mantenido por**: GitHub Actions automation  
**Contacto**: Ver `docs/ops/SUMARIO_EVIDENCIAS.md` para bitácora completa  
**Última revisión**: 2025-10-20
