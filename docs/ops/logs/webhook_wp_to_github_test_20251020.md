# Test Webhook WordPress → GitHub

**Fecha**: 2025-10-20  
**Configuración**: `docs/WEBHOOK_WP_TO_GITHUB.md`  
**Objetivo**: Validar notificación desde WordPress hacia GitHub cuando se publique contenido

---

## Estado Actual

### 🚫 BLOQUEADO por Issue #7

El webhook WP→GitHub requiere `API_GATEWAY_TOKEN` para autenticarse con la API de GitHub.  
Este secret **no existe** actualmente en el repositorio.

**Referencia**: https://github.com/ppkapiro/pepecapiro-wp-theme/issues/7

### Prerequisitos Faltantes

1. ❌ **Secret `API_GATEWAY_TOKEN`**: No configurado
2. ⏸️ **Plugin de webhooks en WP**: No instalado (pendiente hasta resolver #7)
3. ⏸️ **Endpoint receptor en GitHub**: `.github/workflows/api-automation-trigger.yml` existe pero sin token no puede autenticar

---

## Configuración Documentada

Ver `docs/WEBHOOK_WP_TO_GITHUB.md` para instrucciones completas.

### Resumen de Configuración (cuando se resuelva #7)

**Opción 1: Plugin WP Webhooks**
- Trigger: "Post Published"
- URL: `https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches`
- Headers: `Authorization: Bearer <API_GATEWAY_TOKEN>`
- Body: 
  ```json
  {
    "event_type": "automation-trigger",
    "client_payload": {
      "action": "rebuild-dashboard",
      "source": "wordpress",
      "post_id": "{{post_id}}"
    }
  }
  ```

**Opción 2: Custom Code**
- Hook: `publish_post`
- Función: `notify_github_on_post_publish()`
- API: `wp_remote_post()` a GitHub dispatches endpoint

---

## Test End-to-End (Procedimiento)

### Cuando se resuelva Issue #7:

1. **Crear API_GATEWAY_TOKEN**:
   ```bash
   # En GitHub: Settings → Developer settings → Personal access tokens → Generate new token (classic)
   # Scopes: repo, workflow
   # Copiar token
   ```

2. **Añadir secret al repositorio**:
   ```bash
   gh secret set API_GATEWAY_TOKEN
   # Pegar token cuando se solicite
   ```

3. **Configurar webhook en WordPress**:
   - Instalar plugin "WP Webhooks"
   - Configurar según `docs/WEBHOOK_WP_TO_GITHUB.md`
   - Activar webhook

4. **Publicar post de prueba**:
   ```bash
   # Desde wp-admin o WP-CLI
   wp post create --post_title="Test Webhook GitHub" --post_content="Probando integración bidireccional" --post_status=publish
   ```

5. **Verificar ejecución en GitHub**:
   ```bash
   gh run list --workflow=api-automation-trigger.yml --limit 3 --json status,conclusion,displayTitle,createdAt
   
   # Ver logs del último run
   gh run view $(gh run list --workflow=api-automation-trigger.yml --limit 1 --json databaseId --jq '.[0].databaseId') --log
   ```

6. **Validar resultado**:
   - ✅ Run ejecutado con status "completed"
   - ✅ Logs muestran `Triggered by: repository_dispatch`
   - ✅ Logs muestran `Client: wordpress-webhook`
   - ✅ Workflow ejecutó acción correspondiente (ej: `rebuild-dashboard`)

7. **Capturar evidencia**:
   - Screenshot de logs de ejecución → `docs/ops/logs/webhook_wp_to_github_success_YYYYMMDD.png`
   - Extracto de logs → actualizar este documento con sección "Resultados"

---

## Resultados Actuales

### ⏸️ TEST NO EJECUTABLE

**Motivo**: Falta `API_GATEWAY_TOKEN` (issue #7)

**Impacto**:
- WordPress no puede autenticarse con GitHub API
- Requests retornarán `401 Unauthorized`
- Workflow `api-automation-trigger.yml` no se ejecutará

**Estado del Workflow Receptor**:
- ✅ `.github/workflows/api-automation-trigger.yml` existe y está correctamente configurado
- ✅ Maneja `repository_dispatch` con tipo `automation-trigger`
- ✅ Valida acciones y ejecuta workflows correspondientes
- ❌ No puede recibir eventos hasta resolver autenticación

---

## Validación Teórica

### Flujo Esperado (sin blocker)

1. **Usuario publica post en WordPress**
2. **Plugin WP Webhooks detecta evento `publish_post`**
3. **Plugin envía POST a GitHub**:
   ```http
   POST https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches
   Authorization: Bearer <API_GATEWAY_TOKEN>
   Content-Type: application/json
   
   {
     "event_type": "automation-trigger",
     "client_payload": {
       "action": "rebuild-dashboard",
       "source": "wordpress",
       "post_id": "123",
       "post_title": "Mi Nuevo Post",
       "client": "wordpress-webhook"
     }
   }
   ```

4. **GitHub recibe dispatch y ejecuta workflow**:
   - Workflow: `api-automation-trigger.yml`
   - Event: `repository_dispatch: types: [automation-trigger]`
   - Action detectada: `rebuild-dashboard`

5. **Workflow ejecuta acción**:
   ```bash
   gh workflow run health-dashboard.yml
   ```

6. **Resultado**: Dashboard actualizado con nuevo contenido de WordPress

### ✅ Strengths del Diseño

- Workflow receptor robusto con validación de acciones
- Autenticación basada en token (seguro)
- Payload flexible (client_payload personalizable)
- Retry automático en caso de fallo (GitHub actions built-in)

### ⚠️ Riesgos Identificados

1. **Token expira**: Si API_GATEWAY_TOKEN caduca, webhooks fallan silenciosamente
   - **Mitigación**: Usar tokens con expiración larga o regenerar periódicamente
2. **Rate limit de GitHub**: 5000 requests/hora para autenticados
   - **Mitigación**: Implementar debounce en WordPress (no enviar en cada save_post, solo publish_post)
3. **Endpoint custom ausente**: WP notifica pero GitHub no confirma recepción
   - **Mitigación**: Implementar endpoint de confirmación en WP (opcional)

---

## Troubleshooting Proactivo

### Si webhook no funciona (futuro)

**Síntoma**: WordPress envía pero GitHub no ejecuta workflow

**Checklist de diagnóstico**:
1. ✅ **Token válido**: Verificar en GitHub settings que no ha expirado
2. ✅ **Scopes correctos**: `repo` + `workflow` requeridos
3. ✅ **URL correcta**: `api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches`
4. ✅ **Event type coincide**: `automation-trigger` en payload y workflow
5. ✅ **Workflow activo**: No deshabilitado manualmente
6. ✅ **Logs WP**: Revisar `wp-content/debug.log` para errores de `wp_remote_post()`

**Comandos de diagnóstico**:
```bash
# Verificar últimas ejecuciones de api-automation-trigger
gh run list --workflow=api-automation-trigger.yml --limit 10

# Verificar secret existe
gh secret list | grep API_GATEWAY_TOKEN

# Test manual del endpoint (simular WordPress)
curl -X POST \
  -H "Authorization: Bearer $API_GATEWAY_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches \
  -d '{"event_type":"automation-trigger","client_payload":{"action":"rebuild-dashboard","source":"test"}}'
```

---

## Próximos Pasos

1. 🔴 **Resolver Issue #7**: Crear y configurar `API_GATEWAY_TOKEN`
2. ⏸️ **Instalar plugin en WP**: WP Webhooks o implementar custom code
3. ⏸️ **Configurar webhook**: Según `docs/WEBHOOK_WP_TO_GITHUB.md`
4. ⏸️ **Ejecutar test end-to-end**: Publicar post y verificar ejecución
5. ⏸️ **Capturar evidencia**: Logs y screenshots
6. ⏸️ **Actualizar este documento**: Sección "Resultados" con evidencia real

---

## Conclusión Parcial

La arquitectura del webhook WP→GitHub está **completamente diseñada y documentada**.  
El workflow receptor (`api-automation-trigger.yml`) está **operativo y listo para recibir eventos**.  

**BLOCKER**: No puede probarse hasta resolver Issue #7 (crear `API_GATEWAY_TOKEN`).

**Recomendación**: Continuar con FASE 3 (Export Kit) mientras el propietario del repositorio genera el token.  
Cuando se resuelva, ejecutar test end-to-end y actualizar evidencia.

---

**Estado**: ✅ **DISEÑO COMPLETO** | 🚫 **EJECUCIÓN BLOQUEADA** (#7) | 📋 **PROCEDIMIENTO DOCUMENTADO**

**Relacionado**:
- `docs/WEBHOOK_WP_TO_GITHUB.md` (guía de configuración)
- `.github/workflows/api-automation-trigger.yml` (workflow receptor)
- `docs/API_REFERENCE.md` (endpoint POST /trigger)
- Issue #7: https://github.com/ppkapiro/pepecapiro-wp-theme/issues/7
