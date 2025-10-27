# Operaciones WordPress — Flujo Local

Este documento resume cómo preparar credenciales y ejecutar los scripts locales
que publican contenido bilingüe en pepecapiro.com.

## 1. Configurar credenciales locales

1. Ejecuta el discovery:
   ```bash
   python scripts/env/discover_wp_creds.py
   ```
   - Si falta algún dato, el script devuelve código 2.
2. Completa los valores faltantes con el asistente interactivo:
   ```bash
   python scripts/env/configure_wp_creds.py
   ```
   - Solicita `WP_URL`, `WP_USER` y `WP_APP_PASSWORD` (el Application Password se
     ingresa en modo oculto).
   - Las credenciales se guardan en `secrets/.wp_env.local` (ignorado por Git).

## 2. Cargar las credenciales en la sesión actual

- Bash / Linux / WSL:
  ```bash
  source secrets/.wp_env.local
  ```
- PowerShell (Windows):
  ```powershell
  Get-Content secrets/.wp_env.local | ForEach-Object {
      if ($_ -match '=') { $name, $value = $_.Split('=',2); setx $name $value }
  }
  ```
  > Reinicia la terminal para que las variables estén disponibles.

## 3. Verificar autenticación (opcional, recomendado)

```bash
python scripts/env/verify_wp_auth.py
```
- Usa Basic Auth contra `/wp-json/wp/v2/users/me`.
- Si devuelve 200, las credenciales son válidas.

## 4. Publicar contenido bilingüe

1. Genera (o regenera) las traducciones EN:
   ```bash
   python scripts/content/translate.py --provider auto --force
   ```
2. Publica en WordPress:
   ```bash
   python scripts/content/publish_content.py --apply
   ```
3. Confirma que no existen divergencias:
   ```bash
   python scripts/content/publish_content.py --drift-only --dry-run
   ```

## 5. Rotación y mantenimiento

- Para rotar el Application Password repite el paso 1.2 y actualiza el secret en
  GitHub (`WP_APP_PASSWORD`).
- Documenta cualquier cambio en `docs/SECURITY_NOTES.md`.
- Conserva `secrets/.wp_env.local` con permisos restringidos (`chmod 600`).
