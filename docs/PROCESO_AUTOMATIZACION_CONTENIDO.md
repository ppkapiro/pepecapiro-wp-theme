# Proceso de Automatización de Contenido (Maestro)

Este documento centraliza TODO el flujo "contenido como código" implementado en el repositorio. Reemplaza descripciones dispersas previas y sirve como única referencia operacional.

## 1. Objetivo
Tener posts y páginas bilingües (ES/EN) + media versionados en Git que se publiquen/actualicen automáticamente en WordPress de forma idempotente y auditable, minimizando interacción manual con el panel.

## 2. Alcance
Incluye: posts, páginas estáticas (legales, home, about, etc.), linking de traducciones (Polylang), subida de media local, control de estado (draft/publish), desactivación por idioma, plan/apply, auto‑apply condicional y validaciones de esquema.

## 3. Componentes
| Componente | Ruta | Descripción |
|-----------|------|-------------|
| Config posts | `content/posts.json` | Metadatos posts bilingües. |
| Config páginas | `content/pages.json` | Metadatos páginas bilingües. |
| Markdown | `content/*.es.md` / `content/*.en.md` | Cuerpo por idioma. |
| Media local | `content/media/*` | Imágenes a subir (referenciadas). |
| Script core | `scripts/publish_content.py` | Orquestación completa. |
| Validadores | `scripts/validate_posts.py`, `scripts/validate_pages.py` | Esquema y campos obligatorios. |
| Workflow CI | `.github/workflows/content-sync.yml` | Plan/apply + auto‑apply. |
| Doc maestro | `docs/PROCESO_AUTOMATIZACION_CONTENIDO.md` | Este documento. |
| Stub rápido | `CONTENT_AUTOMATION.md` | Resumen + enlace a maestro. |

## 4. Esquemas
### 4.1 posts.json
```jsonc
{
  "translation_key": "wp-audit-basics",
  "slug": {"es": "auditoria-wordpress-inicial", "en": "wordpress-initial-audit"},
  "title": {"es": "Auditoría Inicial", "en": "Initial Audit"},
  "excerpt": {"es": "Guía...", "en": "Guide..."},
  "category": {"es": "Guías", "en": "Guides"},
  "status": {"es": "draft", "en": "draft"},
  "disabled": {"en": false}
}
```
Reglas: `translation_key` único; `slug` string o dict; `title/excerpt/category` obligatorios por idioma; `status` opcional (default publish, puede dict); `disabled` global o por idioma.

### 4.2 pages.json
```jsonc
{
  "translation_key": "contact-page",
  "slug": {"es": "contacto", "en": "contact"},
  "title": {"es": "Contacto", "en": "Contact"},
  "excerpt": {"es": "Formulario de contacto", "en": "Contact form"},
  "status": {"es": "publish", "en": "publish"},
  "disabled": false
}
```
No requiere categoría.

## 5. Convención Markdown
Archivo por slug e idioma: `<slug>.<lang>.md`. Si slugs difieren entre idiomas, se usan los específicos (`auditoria-wordpress-inicial.es.md` / `wordpress-initial-audit.en.md`).

## 6. Parser Soportado
Elementos: encabezados (#..######), párrafos, listas 1 nivel, código inline y bloques ```, enlaces, imágenes `![alt](url)`, blockquotes `>`. No (todavía): tablas, listas profundas >1.

## 7. Hash / Idempotencia
Cada item calcula hash SHA256 de: `title + excerpt + content_html + status + (category_id para posts)`. Si coincide con lo publicado, se omite update `[skip]`.

## 8. Linking Traducciones
Agrupación por `translation_key`. Si existen ≥2 idiomas, se intenta PATCH meta Polylang. Fallback CLI si la API no acepta: `wp pll translation set posts es:<id_es> en:<id_en>` (o `pages`).

## 9. Media
Referenciar imágenes locales con `<img src="media/archivo.png" alt="..." />` o `![alt](media/archivo.png)`. En apply: se suben y URLs reemplazadas (sólo si la ruta comienza por `media/`).

### 9.1 Deduplicación (Implementado 0.3.18)
Cada archivo se hashea (SHA256). Se mantiene `.media_map.json` en `content/` con el mapping `hash -> url subida`. Si el hash ya existe, se reutiliza la URL (no se vuelve a subir). Beneficios: idempotencia fuerte al renombrar archivos y menor ruido en librería WP.

## 10. Flags y Selectividad
- `--dry-run`: no muta (plan). Implícito en workflow salvo auto-apply.
- `--drift-only`: genera `drift_report.md` comparando hash local vs remoto SIN crear plan de acciones ni modificar nada (fuerza dry). Útil para auditoría de divergencias en producción.
- `--key=a,b`: filtra por `translation_key` (posts y páginas conjuntamente).
- `disabled`: evita procesar global o idioma específico.
- Campo `removed: true`: soft delete declarativo → si el recurso existe lo pasa a `draft`; si no existe se anota como `removed-missing` (no crea nada nuevo). NO elimina físicamente.

## 11. Outputs del Proceso
| Archivo | Contexto | Descripción |
|---------|----------|-------------|
| `content_plan_summary.md` | Dry-run | Lista acciones previstas (create/update/skip/removed) |
| `drift_report.md` | `--drift-only` | Divergencias hash local vs remoto |
| `.media_map.json` | Apply | Cache hash->URL media para no re-subir |

## 11. Workflow CI
Archivo: `.github/workflows/content-sync.yml`.
Pasos clave: checkout → instalar deps → validar posts/pages → determinar modo → plan/apply → artifact log.

### 11.1 Auto-Apply Condicional
Apply automático si:
1. Manual dispatch con `apply=true`.
2. Archivo `.auto_apply` presente (persistente).
3. Último commit message contiene `[publish]`.
Si ninguna condición ⇒ plan (dry-run).

## 12. Credenciales
Secrets: `WP_URL`, `WP_USER`, `WP_APP_PASSWORD` (App Password WP). Sólo se necesitan para apply.

## 13. Añadir Nuevo Post (Checklist Operativa)
1. Definir entry en `content/posts.json` (nueva `translation_key`).
2. Crear markdown ES/EN.
3. (Opcional) Añadir media en `content/media/`.
4. Commit con mensaje conteniendo `[publish]` (o confiar en `.auto_apply`).
5. Push → CI publica.
6. Verificar enlace y traducciones.

## 14. Añadir Nueva Página
Igual que post pero en `pages.json` (sin categoría).

## 15. Cambiar Estado (draft ↔ publish)
Editar `status` en JSON, commit `[publish]`; el hash cambia y se fuerza update.

## 16. Desactivar Temporalmente
`"disabled": true` (global) o `{ "en": true }` para idioma. No borra en WP (no destructivo).

## 17. Seguridad / Riesgos
- Evitar credenciales en commits. Usar Secrets.
- Auto-apply requiere disciplina en PR review. Recomendado squash & signed commits en main.
- No se implementa borrado: remover item del JSON no lo elimina en WP (roadmap: política de archivado).

## 18. Errores Comunes
| Mensaje | Causa | Acción |
|---------|-------|-------|
| `[skip-md]` | Falta markdown idioma | Añadir archivo faltante |
| 401 Unauthorized | Secret incorrecto | Rotar secret |
| `No se pudo crear categoría` | Permisos / endpoint bloqueado | Revisar logs WP | 
| Imagen no reemplazada | Ruta no comienza por `media/` | Ajustar markdown |

## 19. Roadmap Futuro
1. Reporte diff HTML enriquecido (resaltar bloques cambiados).
2. Tablas y listas profundas en parser.
3. Rollback rápido (snapshot contenido + revert apply).
4. Firma obligatoria en commits que auto‑apply.
5. Archivado avanzado (etiquetar y ocultar vs draft plano) + purga opcional tras retención.
6. Previsualización local (mini server que renderice markdown con layout WP).

## 19.1 Pipeline Preflight & Quality Gates

(Actualizado)

Los gates se ejecutan ANTES de validar y antes de plan/apply en el workflow `content-sync.yml`.

| Gate | Script | Salidas | Criterio FAIL | Exit code | Notas |
|------|--------|---------|---------------|-----------|-------|
| Links internos | `scripts/preflight_links.py` | `preflight_links.json/md` | ≥1 enlace interno con status HTTP >=400 | 2 | Ignora externos; tolera timeouts aislados como warnings (futuro) |
| Categorías | `scripts/preflight_taxonomies.py` | `preflight_taxonomies.json/md` | Categorías declaradas inexistentes confirmadas en WP | 2 | Modo `--strict-offline` para fallar si no se alcanza WP; por defecto UNKNOWN_OFFLINE no bloquea |
| Completitud contenido | `scripts/preflight_content_completeness.py` | `preflight_content.json/md` | Falta slug/title requerido o duplicidad de translation_key/slug | 2 | No bloquea por items disabled |

Consolidación: el workflow sube un artefacto `preflight-quality-gates` con todos los archivos. Si cualquiera devuelve exit code 2 → aborta pipeline antes de publicar.

### 19.1.1 Reporte Unificado
Implementado: `scripts/generate_preflight_report.py` produce `preflight_report.json` y `preflight_report.md` con resumen y estado global (OK / FAILED / UNKNOWN). El workflow sube este artefacto adicional.

### 19.1.2 Escalado Automático
Si en el futuro se desea: convertir fallos críticos (p.ej. 2 corridas consecutivas con performance < umbral) en bloqueo de publicación de contenido o en etiqueta adicional del issue ("priority:high"). Actual hoy: sólo creación de issue PSI independiente.

### 19.1.3 Soft Performance Advisory
Integrado script `performance_advisory.py` en `content-sync` que añade contexto sobre estado de thresholds PSI móvil sin bloquear.

### 19.1.4 Media Reuse Metric
`media_reuse_report.{json,md}` se genera en la corrida PSI para visibilidad sobre eficacia de deduplicación.

## 20. Versionado
Cada mejora funcional → bump en `style.css` + entrada en `CHANGELOG.md`. Versión actual: 0.3.18 (Unreleased). Validadores activos: posts/pages schema, hash idempotencia, drift, media dedup.


## 21. Guía Rápida (TL;DR)
Nuevo contenido:
```
Editar JSON + crear markdown
Commit: feat(content): nuevo post X [publish]
Push → CI publica
```

## 22. FAQ Express
- ¿Puedo publicar sólo ES? Sí, omite EN markdown (se saltará). Añadir EN más adelante lo enlaza.
- ¿Forzar update sin cambiar texto? Ajusta excerpt mínimamente.
- ¿Revertir? Edita markdown/JSON al estado previo y commit `[publish]`.

---
Documento maestro vivo. Cualquier cambio estructural debe actualizar este archivo primero.
