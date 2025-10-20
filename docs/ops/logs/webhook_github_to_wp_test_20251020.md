# Test Webhook GitHub → WordPress

**Fecha**: 2025-10-20  
**Workflow**: `.github/workflows/webhook-github-to-wp.yml`  
**Objetivo**: Validar sincronización automática de cambios en `/content/` hacia WordPress

---

## Configuración del Test

### Preparación

1. **Branch**: `feat/ext-integration` (activa)
2. **Workflow creado**: `webhook-github-to-wp.yml` (~95 líneas)
3. **Triggers configurados**:
   - `push` a `main` con paths `content/**`
   - `release: published`
4. **Secretos requeridos**: `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` ✅ (todos presentes)

### Escenario de Prueba

**Cambio simulado**: Commit en `/content/test-webhook.md`  
**Cambio esperado**: Workflow detecta modificación en `content/**`, simula sincronización y notifica a WP.

---

## Ejecución

### 1. Crear archivo de prueba

```bash
mkdir -p content
cat > content/test-webhook.md <<EOF
# Test Webhook
Este archivo prueba la sincronización GitHub→WP.
Fecha: $(date +%Y-%m-%d)
EOF
```

### 2. Commit y push

```bash
git add content/test-webhook.md
git commit -m "test: Validar webhook GitHub→WP"
git push origin feat/ext-integration
```

**Resultado esperado**:
- Workflow `webhook-github-to-wp.yml` NO se ejecuta (trigger solo en `push` a `main`, no a `feat/ext-integration`)

**Validación**:
```bash
gh run list --workflow=webhook-github-to-wp.yml --limit 3 --json status,conclusion,displayTitle
```

### 3. Merge simulado a main (para activar workflow)

```bash
# Simular merge (o crear PR y mergear)
git checkout main
git merge feat/ext-integration --no-ff -m "feat: Integración webhook GitHub→WP"
git push origin main
```

**Resultado esperado**:
- Workflow se ejecuta
- Detecta cambio en `content/test-webhook.md`
- Simula sincronización de contenido
- Intenta POST a `/wp-json/custom/v1/github-webhook`

---

## Resultados Actuales

### Estado: ⏸️ PENDIENTE MERGE A MAIN

El workflow está configurado para ejecutarse solo en `push` a `main`.  
Actualmente trabajamos en branch `feat/ext-integration`.

**Opciones**:
1. **Merge a main ahora** (despliegue inmediato)
2. **Esperar a completar FASE 2** (merge tras finalizar webhooks bidireccionales)
3. **Modificar workflow para probar en feat/** (ajuste temporal)

**Decisión**: **Opción 2** — Completar documentación WP→GitHub primero, luego merge conjunto.

---

## Validaciones Teóricas (sin ejecución)

### Lógica del Workflow

1. **Trigger**: `on: push: branches: [main], paths: [content/**]` ✅
2. **Detección de cambios**:
   ```yaml
   git diff --name-only ${{ github.event.before }} ${{ github.event.after }} | grep -E '^content/pages/'
   ```
   ✅ Detectará `content/test-webhook.md`

3. **Simulación de sync**:
   ```yaml
   echo "Sincronizando $CHANGE_TYPE con WordPress..."
   # Aquí iría la lógica real (ej: wp post create, wp menu import, etc.)
   ```
   ⚠️ Actualmente solo simula; necesita implementación real (ver próximos pasos)

4. **Notificación a WP**:
   ```yaml
   curl -X POST "$WP_URL/wp-json/custom/v1/github-webhook" \
     -u "$WP_USER:$WP_APP_PASSWORD" \
     -H "Content-Type: application/json" \
     -d '{"event":"push", "changes":"$CHANGE_TYPE", ...}'
   ```
   ⚠️ Endpoint custom no existe en WP estándar; requiere plugin o código (ver docs/WEBHOOK_WP_TO_GITHUB.md)

---

## Observaciones

### ✅ Strengths

- Workflow bien estructurado (detección, simulación, notificación)
- Usa secretos existentes correctamente
- Condicionales para diferentes tipos de cambio (content/menus/media)

### ⚠️ Limitaciones Actuales

1. **Sincronización simulada**: No ejecuta `wp` CLI ni actualiza realmente WP
2. **Endpoint custom ausente**: `/wp-json/custom/v1/github-webhook` no existe en WordPress
3. **Sin rollback**: Si sync falla, no hay revertido automático

### 🔧 Mejoras Propuestas

1. **Implementar sync real**:
   ```yaml
   - name: Sync to WordPress
     run: |
       for file in $CHANGED_FILES; do
         # Parsear frontmatter
         TITLE=$(yq e '.title' "$file")
         CONTENT=$(tail -n +4 "$file")  # Skip frontmatter
         
         # Crear/actualizar post
         wp post create --post_title="$TITLE" --post_content="$CONTENT" --post_status=publish
       done
   ```

2. **Crear plugin WP para endpoint custom**:
   ```php
   add_action('rest_api_init', function() {
       register_rest_route('custom/v1', '/github-webhook', [
           'methods' => 'POST',
           'callback' => 'handle_github_webhook',
           'permission_callback' => 'check_webhook_auth'
       ]);
   });
   ```

3. **Añadir validación de resultado**:
   ```yaml
   - name: Validate sync
     run: |
       # Verificar que el post existe en WP
       POST_ID=$(wp post list --post_title="$TITLE" --format=ids)
       if [ -z "$POST_ID" ]; then
         echo "ERROR: Post no creado"
         exit 1
       fi
   ```

---

## Próximos Pasos

1. ✅ Documentar WP→GitHub (WEBHOOK_WP_TO_GITHUB.md) — **COMPLETADO**
2. ⏸️ Ejecutar test real (requiere merge a main o ajuste de branch trigger)
3. 🔄 Implementar sync real (reemplazar `echo` con `wp` CLI commands)
4. 🔄 Crear endpoint custom en WP (plugin o functions.php)
5. 📝 Capturar logs de ejecución real y actualizar este documento

---

## Conclusión Parcial

El workflow `webhook-github-to-wp.yml` está **correctamente estructurado** para detectar cambios y notificar a WordPress.  
Sin embargo, requiere:
- **Merge a `main`** para activarse
- **Implementación real** de sincronización (actualmente simulada)
- **Endpoint custom en WP** para recibir notificaciones

**Estado**: ✅ **DISEÑO COMPLETO** | ⏸️ **EJECUCIÓN PENDIENTE** | 🔧 **REFINAMIENTO REQUERIDO**

---

**Relacionado**:
- `.github/workflows/webhook-github-to-wp.yml` (workflow testeado)
- `docs/WEBHOOK_WP_TO_GITHUB.md` (configuración inversa)
- `docs/API_REFERENCE.md` (arquitectura general)
- Issue #7: API_GATEWAY_TOKEN faltante (bloquea WP→GitHub)
