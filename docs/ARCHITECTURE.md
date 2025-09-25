# Arquitectura y Flujos

## 1. Visión General
El repositorio integra: tema WordPress, contenido como código, automatización de publicación, despliegue verificado e informes de rendimiento.

## 2. Componentes
| Componente | Ruta | Rol |
|------------|------|-----|
| Tema WP | `pepecapiro/` | Plantillas, estilos, hooks. |
| Contenido declarativo | `content/` | Markdown + metadatos (posts/pages). |
| Scripts operativos | `scripts/` | Publicación, validación, salud, Lighthouse, deploy. |
| Workflows CI | `.github/workflows/` | Orquestación (contenido, deploy, perf). |
| Evidencias | `evidence/` | Capturas/HTML de auditorías previas. |
| Lanzamientos | `_releases/` | Artefactos entregables (ZIP + SHA256). |

## 3. Flujos Principales
### 3.1 Publicación de Contenido
Fuente: `content/*.md`, `posts.json`, `pages.json` → `scripts/publish_content.py` → WordPress REST (posts/pages/media) + Polylang linking → artifacts (`content_plan_summary.md`, `drift_report.md`, `.media_map.json`).

### 3.2 Deploy Tema
Tag `vX.Y.Z` o workflow manual → `deploy.yml` → rsync + verificación SHA256 → smoke WP-CLI → logs + artefactos.

### 3.3 Rendimiento y Salud
`lighthouse*.yml` → genera HTML en `docs/lighthouse/` → resumen Markdown. `site-health.yml` y `status.yml` validan endpoints y markers.

### 3.4 Operaciones Post-Deploy
`wp_post_deploy_remediate.sh`: activar tema, portada, purgas. `blog_health_ci.sh`: listar blog bilingüe consistente.

## 4. Validadores / Guard Rails
| Guardia | Implementación |
|---------|----------------|
| Estructura posts/pages | `scripts/validate_posts.py`, `scripts/validate_pages.py` |
| Hash idempotencia | Dentro de `publish_content.py` (contenido y estado) |
| Deduplicación media | Hash SHA256 (.media_map.json) |
| Drift detection | `--drift-only` (genera `drift_report.md`) |
| Salud blog | `scripts/blog_health_ci.sh` |
| Integridad deploy | Manifests SHA256 comparados en CI |
| Rendimiento | Lighthouse workflows |

## 5. Outputs Clave
| Archivo | Generador | Uso |
|---------|----------|-----|
| `content_plan_summary.md` | Dry-run contenido | Revisión plan previo a apply |
| `drift_report.md` | `--drift-only` | Auditoría divergencias prod vs repo |
| `.media_map.json` | apply contenido | Cache de media remota por hash |
| `integrity_ci.log` | deploy | Evidencia integridad binaria |
| `lighthouse/*.html` | Lighthouse workflows | Auditorías rendimiento |

## 6. Extensión Futura (Roadmap Doc)
- Diff HTML enriquecido para drift.
- Previsualización local de markdown con layout tema.
- Chequeos automáticos SEO (canonical/hreflang) gating opcional.

## 7. Modelo de Versionado
`style.css` refleja versión del tema. Cada feature relevante → entrada en `CHANGELOG.md` + tag si es release.
