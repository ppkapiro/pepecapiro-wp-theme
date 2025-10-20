# Troubleshooting Publicación de Contenido (REST / CI)

Guía para diagnosticar y resolver fallos de creación / actualización de posts y páginas mediante el workflow `Content Sync`.

## 1. Flujo Mental Rápido
```
¿CI en modo PLAN cuando esperaba APPLY? -> ¿faltan secrets?
¿CI en APPLY pero 401? -> credencial (Application Password) incorrecta o header cortado.
¿/users/me 200 pero POST 403? -> capacidades / ownership / plugin de seguridad.
¿POST 201 pero traducción faltante? -> mapping de translation_key o slug mismatch.
¿Timeout/intermitente? -> WAF / rate limiting / cache proxy.
```

## 2. Requisitos Previos
- Secrets configurados: `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`.
- `WP_APP_PASSWORD` es un Application Password (no la contraseña normal).
- Sitio sirve HTTPS válido (sin redirecciones infinitas).

## 3. Verificaciones Básicas Manuales
Exporta variables (no commitear):
```bash
export WP_URL="https://pepecapiro.com"
export WP_USER="ppcapiro"
export WP_APP_PASSWORD="<application_password>"
AUTH_TOKEN=$(printf "%s:%s" "$WP_USER" "$WP_APP_PASSWORD" | base64)
```

1. Identidad:
```bash
curl -i -H "Authorization: Basic $AUTH_TOKEN" "$WP_URL/wp-json/wp/v2/users/me"
```
Esperado: `200` y JSON con `slug":"ppcapiro"`.

2. Crear post borrador (prueba):
```bash
curl -i -X POST \
  -H "Authorization: Basic $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"diag-ci","status":"draft","content":"tmp"}' \
  "$WP_URL/wp-json/wp/v2/posts"
```
Esperado: `201 Created`.

3. Eliminar (limpieza):
```bash
curl -i -X DELETE -H "Authorization: Basic $AUTH_TOKEN" "$WP_URL/wp-json/wp/v2/posts/<ID>?force=true"
```

## 4. Interpretación de Errores Comunes
| Código / error | Causa típica | Acción |
|----------------|-------------|--------|
| 401 rest_cannot_create | Password inválido o Authorization no llega | Regenerar Application Password, revisar Site Health header |
| 403 rest_cannot_edit | Usuario no propietario / falta capability | Usar rol editor o reasignar autor | 
| 403 rest_forbidden | Plugin seguridad (rate / bloqueo) | Revisar logs, whitelist CI IPs |
| 404 (endpoint) | Permalinks corrompidos | Guardar enlaces permanentes en WP Admin |
| 500 | Plugin/theme fatal | Revisar `error_log` servidor |
| cURL 000 / vacíos | WAF / TLS handshake / firewall | Desactivar regla, inspeccionar reverse proxy |

## 5. Problemas con Traducciones
Si un post ES se crea pero EN falla:
- Confirmar que ambos objetos en `posts.json` comparten el mismo `translation_key`.
- Slugs por idioma: usar objeto `{ "es": "slug-es", "en": "slug-en" }` si difieren.
- Verificar que los markdown existen: `content/<slug-es>.es.md`, `content/<slug-en>.en.md`.
- Revisa artefacto `publish-verification.zip` → `verify.json`.

## 6. Modo PLAN vs APPLY
El workflow fuerza PLAN si falta alguno de los secrets. Logs: línea con `MODO=PLAN (faltan secrets)`.
Para forzar APPLY:
- Añade/actualiza secrets.
- Commit con `[publish]` o mantener archivo `.auto_apply`.

## 7. Reintentos Seguros
Cuando resuelvas un 401/403:
```bash
git commit --allow-empty -m "chore: retry content sync [publish]"
git push
```
El script es idempotente: reintentos no duplican porque busca coincidencias por slug + idioma.

## 8. Depuración Avanzada
1. Añadir variable temporal `DEBUG_HTTP=1` en el job (si se instrumenta) para volcar headers.
2. Capturar respuesta root:
```bash
curl -i "$WP_URL/wp-json/" | sed -n '1,20p'
```
3. Inspeccionar namespaces relacionados: `application-passwords`, `wp/v2`.
4. Verificar Site Health > REST API & Authorization header.

## 9. Seguridad y Rotación
- Revocar passwords no usados en Perfil > Application Passwords.
- Limitar rol a mínimo (author suficiente si ya existe estructura). Editor si se necesita editar páginas.
- Rotar si se expone en logs públicos (no deberíamos loggear el valor en CI).

## 10. Checklist Cierre de Incidente
- [ ] `/users/me` 200
- [ ] POST 201 en prueba aislada
- [ ] Segundo post publicado en ambos idiomas
- [ ] Traducciones enlazadas (ver front-end / ?lang=en)
- [ ] Artefacto `verify.md` sin errores
- [ ] README actualizado (Estado Actual)

## 11. Preguntas Frecuentes
**¿Por qué necesito Application Password y no la contraseña normal?**  
Porque WordPress bloquea el Basic Auth directo con la contraseña principal; los Application Passwords generan un token revocable y con scope reducido.

**¿Puedo usar bearer tokens?**  
No nativamente sin plugin adicional. El objetivo es mantener core + mínima superficie.

**¿Puedo limitar el Application Password?**  
Sólo revocación manual. Mantenerlo en GitHub Secrets y rotar si se sospecha exposición.

---
Actualiza este documento si aparecen nuevos patrones de error o se endurece la política (ej. convertir fallos de verificación en bloqueantes).
