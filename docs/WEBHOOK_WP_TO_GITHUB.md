# Webhook WordPress → GitHub — Configuración

**Última actualización**: 2025-10-20

Este documento describe cómo configurar WordPress para notificar a GitHub cuando se publiquen/actualicen contenidos.

## Prerequisitos

1. Plugin de webhooks en WordPress (ej: WP Webhooks, Zapier for WordPress, o custom)
2. Token de GitHub con scope `repo` almacenado en `API_GATEWAY_TOKEN` (ver issue #7)
3. URL del endpoint: `https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches`

## Configuración en WordPress

### Opción 1: Plugin WP Webhooks (recomendado)

1. Instalar plugin "WP Webhooks" desde wp-admin
2. Ir a Settings → WP Webhooks → Send Data
3. Crear nuevo webhook:
   - **Trigger**: "Post Published" o "Post Updated"
   - **URL**: `https://api.github.com/repos/ppkapiro/pepecapiro-wp-theme/dispatches`
   - **Method**: POST
   - **Headers**:
     ```
     Authorization: Bearer <API_GATEWAY_TOKEN>
     Accept: application/vnd.github+json
     Content-Type: application/json
     ```
   - **Body template**:
     ```json
     {
       "event_type": "automation-trigger",
       "client_payload": {
         "action": "rebuild-dashboard",
         "source": "wordpress",
         "post_id": "{{post_id}}",
         "post_title": "{{post_title}}",
         "post_status": "{{post_status}}",
         "client": "wordpress-webhook"
       }
     }
     ```

4. Guardar y activar webhook

### Opción 2: Custom Code (functions.php o mu-plugin)

```php
<?php
/**
 * Notificar a GitHub cuando se publique un post
 */
add_action('publish_post', 'notify_github_on_post_publish', 10, 2);

function notify_github_on_post_publish($post_id, $post) {
    $github_token = get_option('github_api_token'); // Almacenar en opciones
    $github_repo = 'ppkapiro/pepecapiro-wp-theme';
    $endpoint = "https://api.github.com/repos/{$github_repo}/dispatches";
    
    $payload = array(
        'event_type' => 'automation-trigger',
        'client_payload' => array(
            'action' => 'rebuild-dashboard',
            'source' => 'wordpress',
            'post_id' => $post_id,
            'post_title' => $post->post_title,
            'post_status' => $post->post_status,
            'client' => 'wordpress-webhook'
        )
    );
    
    $response = wp_remote_post($endpoint, array(
        'headers' => array(
            'Authorization' => 'Bearer ' . $github_token,
            'Accept' => 'application/vnd.github+json',
            'Content-Type' => 'application/json'
        ),
        'body' => json_encode($payload),
        'timeout' => 15
    ));
    
    if (is_wp_error($response)) {
        error_log('GitHub webhook error: ' . $response->get_error_message());
    } else {
        $code = wp_remote_retrieve_response_code($response);
        error_log("GitHub webhook response: {$code}");
    }
}
```

## Prueba End-to-End

### 1. Preparar WordPress

Configurar webhook según Opción 1 o 2.

### 2. Publicar post de prueba

```bash
# Desde wp-admin o via WP-CLI
wp post create --post_title="Test Webhook GitHub" --post_content="Probando integración" --post_status=publish
```

### 3. Verificar recepción en GitHub

```bash
# Listar últimas ejecuciones de api-automation-trigger
gh run list --workflow=api-automation-trigger.yml --limit 3 --json conclusion,displayTitle,createdAt,headSha

# Ver logs del último run
gh run view $(gh run list --workflow=api-automation-trigger.yml --limit 1 --json databaseId --jq '.[0].databaseId') --log
```

**Esperado**: 
- Run nuevo con status "completed" o "in_progress"
- En logs: `Triggered by: repository_dispatch`
- En logs: `Client: wordpress-webhook`

### 4. Registrar evidencia

Capturar screenshot del log y guardarlo en `docs/ops/logs/webhook_wp_to_github_test_*.png`

## Troubleshooting

### Webhook no se dispara

- **Verificar**: Plugin activado y webhook habilitado
- **Verificar**: Token válido (no expirado)
- **Verificar**: URL correcta (repos/owner/name/dispatches)
- **Logs WP**: Revisar `wp-content/debug.log` si WP_DEBUG activo

### GitHub recibe pero no ejecuta workflow

- **Verificar**: `event_type` coincide con el configurado en workflow (`automation-trigger`)
- **Verificar**: Workflow tiene `repository_dispatch: types: [automation-trigger]`
- **Verificar**: Workflow no está deshabilitado

### Error 401 Unauthorized

- **Causa**: Token inválido, expirado o sin scope `repo`
- **Solución**: Regenerar token y actualizar secret `API_GATEWAY_TOKEN`

### Error 404 Not Found

- **Causa**: URL incorrecta o repositorio privado sin acceso
- **Solución**: Verificar owner/repo en URL; confirmar token tiene acceso al repo

## Estado Actual

⚠️ **BLOCKER (#7)**: No existe `API_GATEWAY_TOKEN` en secrets.  
Sin este token, WordPress no puede autenticarse con GitHub.

**Acción requerida**: Generar token y añadirlo como secret (ver docs/API_REFERENCE.md).

## Próximos Pasos

1. Resolver issue #7 (crear API_GATEWAY_TOKEN)
2. Configurar webhook en WordPress (Opción 1 o 2)
3. Ejecutar prueba end-to-end
4. Documentar evidencia en `docs/ops/logs/webhook_wp_to_github_test_YYYYMMDD.md`

---

**Relacionado**:
- docs/API_REFERENCE.md (endpoint POST /trigger)
- .github/workflows/api-automation-trigger.yml (workflow receptor)
- .github/workflows/webhook-github-to-wp.yml (dirección opuesta)
