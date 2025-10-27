# Notas de Seguridad — Automatización WP

- Rotación de Application Passwords (cada 60–90 días)
  1. Crear un nuevo Application Password para el usuario publicador.
  2. Actualizar el secret `WP_APP_PASSWORD` en GitHub.
  3. Validar `/users/me` (200) en un run de prueba.
  4. Revocar el password anterior en WP Admin.

- Plugins que deshabilitan Application Passwords
  - Algunos paneles (Hostinger Tools) o plugins de seguridad pueden bloquearlos.
  - Asegura que la opción está habilitada para el usuario y sitio.

- Buenas prácticas
  - No imprimir secretos en logs. Los workflows ya evitan exponer valores.
  - Usar usuario con el mínimo rol necesario (author/editor).
  - Revisar "Último uso" del Application Password en WP Admin para detectar fugas.

- Secretos locales (entornos desarrollador)
  - Guardar `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` únicamente en `secrets/.wp_env.local` (ignorado por Git).
  - Para cargar credenciales: `source secrets/.wp_env.local` (bash) o iterar con `Get-Content` en PowerShell.
  - Rotar Application Password y actualizar `secrets/.wp_env.local` y secrets de GitHub inmediatamente.
  - `scripts/env/configure_wp_creds.py` automatiza la creación/actualización del archivo local (no imprime los valores).
