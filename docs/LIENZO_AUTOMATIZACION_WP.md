# LIENZO — Automatización WP (Posts bilingües)

Estado final de la etapa (cierre):

- Publish Test Post: OK — publica ES/EN en privado, intenta vincular traducciones y emite Job Summary completo.
- Publish Prod Post: OK — publica ES/EN en `publish`, idempotente por slug por idioma, vinculación best‑effort y categorías por idioma.
- Cleanup Test Posts: OK — cron diario + ejecución manual.
- Content Sync: Sin cambios — sólo "catálogo" (no forma parte de este cierre).
- Flags documentados: OK — `.github/auto/README.flags.md`.
- Documentación: README (sección automatización), Runbook, Troubleshooting, Security Notes, Changelog, Roadmap.

Evidencias mínimas (IDs y links de últimos “Prod Post ES/EN”):
- Se imprimen en el Job Summary del workflow de producción. Consultar la última ejecución verde en Actions para ver `ID_ES`, `link_ES`, `ID_EN`, `link_EN`.

Riesgos conocidos y mitigaciones:
- Plugins que bloquean Application Passwords (p. ej., Hostinger Tools, plugins de seguridad): habilitar Application Passwords o añadir excepción.
- Roles insuficientes: el usuario debe tener `publish_posts`/`edit_posts` (author/editor).
- WAF/ModSecurity bloqueando POST: revisar logs del servidor y ajustar reglas.
- Polylang meta PATCH denegado: el enlace de traducciones es best‑effort; si falla, enlazar manualmente o usar WP‑CLI.

Checklist de cierre ✅
- [x] Ramas normalizadas (main por defecto)
- [x] Workflows en verde y con resumen
- [x] Flags explicados
- [x] Docs actualizadas
- [x] Release etiquetado y empaquetado por tags
- [x] Roadmap siguiente fase definido

---

Siguiente fase (puente): ver `docs/ROADMAP_AUTOMATIZACION_TOTAL.md`.
