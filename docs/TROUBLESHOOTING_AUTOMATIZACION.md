# Troubleshooting — Automatización WordPress (Posts)

Errores típicos y acciones mínimas:

- 401 (rest_cannot_create / Unauthorized)
  - Causa: Application Password incorrecto o bloqueado por plugin.
  - Acción: regenerar Application Password; verificar `/wp-json/wp/v2/users/me` devuelve 200 con Basic Auth; revisar plugins de seguridad.

- 403 (rest_cannot_edit / Forbidden)
  - Causa: rol insuficiente o autor no coincide.
  - Acción: usar usuario con `publish_posts` y `edit_posts` (author/editor) o cambiar autor del post.

- 422 (Unprocessable Entity)
  - Causa: datos inválidos o faltantes (título/contenido), slug duplicado, taxonomía inexistente.
  - Acción: revisar payload; ajustar slug por idioma; no forzar creación de categorías.

- 500 (Server Error)
  - Causa: plugin/tema con fatal error, WAF, o base de datos.
  - Acción: revisar logs del servidor; desactivar temporalmente plugins problemáticos; reintentar.

- Vinculación de traducciones falla (Polylang)
  - Causa: permiso denegado al escribir `meta`.
  - Acción: enlazar manualmente en WP Admin o usar WP‑CLI (`pll_set_post_language`, `pll_save_post_translations`).

Verificación rápida:
1) `GET /wp-json/` → 200.
2) `GET /wp-json/wp/v2/users/me` con Basic Auth → 200.
3) `POST /wp-json/wp/v2/posts` con `status:draft` → 201.

Más detalles en `docs/DEPLOY_RUNBOOK.md` (guardarraíles) y `README.md`.
