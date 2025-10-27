# Auditoría Total — pepecapiro.com

## 1. Resumen Ejecutivo
pepecapiro.com se encuentra en fase de maduración hacia la versión v0.3.0 con una base técnica robusta: tema propio (v0.3.20), automatización de contenido bilingüe y monitoreo de rendimiento y salud ya implantados. El sistema dispone de pipelines CI/CD extensos que cubren despliegue, calidad de contenido, SEO y auditorías periódicas. Persisten tareas críticas relacionadas con autenticación REST intermitente, finalización del contenido bilingüe publicado, activación de SMTP y consolidación del sistema de diseño. La meta sigue siendo un sitio bilingüe profesional con CI/CD estable, contenido completo y flujos operativos reproducibles desde código.

## 2. Infraestructura y Entorno
- **Hosting y dominio**: WordPress 6.8.2 en Hostinger con dominio activo `https://pepecapiro.com`. Certificado SSL funcional y cabeceras `x-litespeed-cache: hit` que confirman caché LiteSpeed habilitada.
- **Stack servidor**: PHP 8.2.28 según `desarrollo_entorno_pepecapiro.md`. Acceso SSH gestionado mediante claves (secrets `PEPE_*`) y rsync en workflows de deploy.
- **Flujo local**: Desarrollo en VS Code sobre este repositorio. Contenido y tema versionados; publicación mediante GitHub Actions o, como fallback, scripts `_scratch/` para despliegues manuales.
- **Tema WordPress**: Directorio `pepecapiro/`, versión declarada 0.3.20, empaquetado automático en cada release (`release.yml`). Incluye layouts específicos (Home, About, Blog, Contacto) y activos self-host (fuentes WOFF2, placeholders SVG).
- **Plugins activos documentados**: Polylang (bilingüe), Rank Math (SEO), LiteSpeed Cache (rendimiento), WPForms (formularios). No existe aún plugin SMTP configurado (pendiente en checklist).
- **Entornos integrados**: Repositorio principal (`main`) sincronizado con producción mediante workflows; no hay ambiente de staging documentado. Auditores y scripts locales (`scripts/`, `_scratch/`) sirven como herramientas de diagnóstico remoto.

## 3. Flujo de Desarrollo y CI/CD
- **Ciclo base**: edición en contenido (`content/*.md`, `posts.json`, `pages.json`) → validaciones en CI (`validate_*`, preflight) → publicación automática vía `content-sync.yml` cuando existe `.auto_apply` o commits con `[publish]`.
- **Workflows clave**: `publish-test-post.yml`, `publish-prod-post.yml`, `publish-test-page.yml`, `publish-prod-page.yml`, `upload-media.yml`, `site-settings.yml`, `set-home.yml`, `content-sync.yml`, `deploy.yml`, `release.yml`, `lighthouse*.yml`, `collect_psi.yml`, `site-health.yml`, `verify-home.yml`, `verify-menus.yml`, `verify-media.yml`, `health-dashboard.yml`, `weekly-audit.yml`, `external_links.yml`, `seo_audit.yml`, `smoke-tests.yml`, `run-repair.yml`.
- **Automatización de contenido**: `scripts/publish_content.py` gestiona posts y páginas bilingües, deduplicación de media (`.media_map.json`), linking Polylang y hash idempotente. `content_plan_summary.md` y `drift_report.md` dan trazabilidad.
- **Governanza**: `weekly-audit.yml` genera cortes programados, `health-dashboard.yml` publica `public/status.json`, y `run-repair.yml` permite ejecutar reparaciones dirigidas.
- **KPIs y quality gates**: Umbrales definidos en `configs/perf_thresholds.json` (Lighthouse móvil ≥90, LCP ≤2.5 s). Preflight links/taxonomías/completitud bloquean publicaciones inconsistentes.
- **Estado del pipeline**: `CIERRE_AUTOMATIZACION_TOTAL.md` y `CIERRE_ETAPA_RESUMEN.md` confirman workflows en verde para publicación de posts bilingües; `Cleanup Test Posts` falla ocasionalmente cuando no hay borradores antiguos (impacto bajo).

## 4. Contenido y Estructura del Sitio
- **Páginas vigentes**: Home (`inicio`/`home`), Sobre mí (`sobre-mi`/`about`), Servicios/Recursos (`recursos`/`resources`), Proyectos (`proyectos`/`projects`), Blog (`blog` bilingüe con plantilla dedicada), Contacto (`contacto`/`contact`), Políticas (`privacidad`/`privacy`, `cookies`/`cookies`). Todas definidas en `content/pages.json` y con markdown ES/EN correspondiente.
- **Posts**: `posts.json` define cinco artículos:
  - `checklist-wp-prod-day` (ES/EN, orientado a lanzamiento exprés).
  - `governance-automation-pillars` (contenido bilingüe; publicación confirmada tras etapa v0.3.20).
  - `wp-audit-basics` (marcado draft en ambos idiomas).
  - `wp-post-7-acciones-post-lanzamiento` (estado publish ES/EN; orientado a T+7 días).
  - `wp-hardening-week-two` (estado publish ES/EN; checklist segunda semana).
- **Cobertura Polylang**: workflows enlazan traducciones por `translation_key`. `BKLG-006` recuerda validar que no existan páginas/posts “Solo ES” o “Solo EN” tras nuevas publicaciones.
- **Menús**: Plantilla de menús por idioma implementada (release 0.1.7). Workflows `publish_prod_menu.yml` y `verify-menus.yml` preparan sincronización declarativa; requiere consolidar manifiesto en `content/menus/` y ejecutar pipeline (estado operativo en pruebas, pendiente producción).
- **Copy y tono**: Markdown utiliza voz profesional, orientada a consultoría y gobernanza. Falta revisión editorial final para posts en draft y para call-to-actions en Home (todavía genéricos). Contacto indica mantenimiento por ausencia de SMTP funcional.
- **Imágenes y OG**: Activo `assets/og/og-home.png`. Media adicional se gestiona vía deduplicación; falta repositorio completo de imágenes para posts publicados.

## 5. Diseño y UI
- **Sistema visual**: `style.css` define tokens básicos (`--c-bg`, `--c-accent`, tipografías). `reports/deuda_visual.md` señala necesidad de consolidar variables para sombras, radios y escalas.
- **Layout**: Home con hero dividido (`hero__inner`), grid de pilares (`grid3`). Templates personalizadas para páginas clave (Home, About, Blog, Contacto).
- **Tipografía**: Montserrat 700 y Open Sans 400 self-host con `font-display:swap`. No existen subsets específicos; peso combinado ~77 KB WOFF2.
- **Componentes principales**: header con switch de idioma, footer simple, tarjetas (`.card`), botones primario/secundario (`.btn`, `.cta-button`).
- **Accesibilidad**: Contraste alto en hero (azul oscuro sobre blanco). Falta inventario formal de estados de foco/tabulación. No hay evidencia de pruebas automáticas de accesibilidad; se recomienda integrar Lighthouse A11y y verificar etiquetas en formularios.

## 6. Performance y Accesibilidad
- **Resultados Lighthouse (20 Oct 2025)**: puntuaciones móviles 98–100; LCP entre 1.5 s y 1.9 s en todas las URLs auditadas (`docs/VALIDACION_MVP_v0_2_1.md`).
- **Cuellos de botella**: fuentes WOFF2 dominan el payload (~24 KB cada una). Subsetting pendiente y se mantiene como acción recurrente en recomendaciones.
- **Caché y minificación**: LiteSpeed Cache activo; CSS de bloques core desregistrado para páginas estáticas; manifest SHA256 verifica integridad post-deploy.
- **Lighthouserc**: configuración móvil emula red lenta (RTT 150 ms, throughput 1.6 Mbps) con un run por URL.
- **PageSpeed Insights**: `reports/psi/` almacena corridas con thresholds; script crea issues cuando se superan umbrales dos veces consecutivas.
- **Accesibilidad**: sin reportes específicos; la automatización actual prioriza performance. Se sugiere añadir axe-core o Lighthouse Accessibility como gate adicional.

## 7. SEO y Analítica
- **Rank Math**: configurado para títulos y meta descriptions base. `SEO_TECH.md` confirma canonical y hreflang dinámicos, así como JSON-LD `BreadcrumbList` y `Article`.
- **Sitemap y robots**: presentes y servidos (`reports/infra_seguridad.md`). Limpieza de `hello-world` confirmada tras purgar Rank Math y LiteSpeed.
- **Search Console**: verificación pendiente (mencionada en `CHANGELOG` y roadmap). No hay tracking de Google Analytics / GTM (`reports/seo_og_analytics.md`).
- **Open Graph**: `og:title` y `og:description` generados; `og:image` ausente en la evidencia pública y debe completarse.
- **Auditorías SEO automatizadas**: `scripts/audit_seo_head.py` y workflow `seo_audit.yml` evalúan canonical, hreflang y JSON-LD; fallos aún no bloquean CI.

## 8. Formularios y SMTP
- **WPForms**: Página de contacto muestra formulario, pero evidencias indican modo mantenimiento (mensajes de contacto directo) y ausencia de registros de envío.
- **SMTP**: `SMTP_CHECKLIST.md` permanece sin completar; `reports/smtp_estado.md` confirma falta de plugin WP Mail SMTP activo y sin trazas en HTML.
- **Testing**: no hay logs de pruebas de envío. Fallback actual es comunicación por email manual indicada en copy.
- **Recomendación inmediata**: elegir proveedor (Hostinger SMTP o servicio externo), instalar WP Mail SMTP, probar transacciones EN/ES y actualizar mensaje de estado.

## 9. Seguridad y Mantenimiento
- **Usuarios y credenciales**: Se utiliza Application Password para el usuario publicador `ppcapiro`. `SECURITY_NOTES.md` documenta rotación trimestral y chequeo de último uso.
- **Versiones**: WordPress 6.8.2, PHP 8.2.28, tema 0.3.20. Actualizaciones priorizadas via checklists.
- **Backups y restauración**: no existe documentación explícita en repo; depende de Hostinger. Se recomienda formalizar plan de backups y restore test.
- **Acceso servidor**: workflows usan SSH keys con `ssh-agent`. Scripts locales (`tail_remote_logs.sh`, `get_wp_diagnostico.sh`) para inspección remota.
- **.htaccess y políticas**: no versionadas aquí; caching y headers gestionados por LiteSpeed/Hostinger (ver evidencias headers). `content-security-policy: upgrade-insecure-requests` activo; considerar CSP más granular en futuras iteraciones.
- **Monitoreo**: `verify-*` workflows revisan Home, menús, media; `health-dashboard.yml` alimenta `public/status.json`. Branch protection pendiente por limitaciones del plan (documentado en `CIERRE_ETAPA_RESUMEN.md`).

## 10. Evaluación del Backlog y Estado de Avance
- **BKLG-001 Inventario de contenido**: documentación disponible, requiere refresco con últimos posts publicados.
- **BKLG-002 Trazas formularios**: sin shortcodes detectados; monitorizar futuras integraciones.
- **BKLG-003 SMTP**: abierto. Falta plugin y pruebas.
- **BKLG-004 SEO/OG/Analytics**: OG image faltante, sin analítica instalada.
- **BKLG-005 Deuda visual**: pendiente consolidar tokens y limpiar estilos repetidos.
- **BKLG-006 Bilingüe**: revisar pareos Polylang tras nuevas publicaciones.
- **BKLG-007 Performance**: esperar corridas Lighthouse locales cuando Chrome esté disponible; seguimiento mediante PSI activo.
- **BKLG-008 Infra/seguridad**: headers y sitemap verificados; continuar monitoreo de exposición de versiones.
- **Prioridad inmediata**: BKLG-003, BKLG-004 y cierre de contenidos en posts.json (publicar drafts) para alcanzar v0.3.0.

## 11. Conclusiones y Recomendaciones
- **Puntos fuertes**: automatización CI/CD integral, contenido como código con deduplicación de media, monitoreo continuo de rendimiento, documentación exhaustiva de operaciones y troubleshooting.
- **Áreas críticas**: autenticación REST debe mantenerse estable (vigilar Application Password), SMTP sin configurar limita conversión, y falta completar contenidos bilingües publicados.
- **Debilidades**: ausencia de analítica y Search Console, tokens visuales incompletos, fallback manual ante fallos de workflows no completamente automatizado.
- **Recomendaciones inmediatas**: asegurar credenciales REST con monitoreo proactivo, activar SMTP y pruebas end-to-end de formularios, publicar y enlazar los posts pendientes, completar OG/analytics y cerrar backlog SEO básico.
- **Recomendaciones estratégicas**: consolidar diseño mediante tokens reutilizables, endurecer quality gates (convertir advisories en bloqueantes tras estabilidad), extender menú y media automation a producción, formalizar backups y plan de disaster recovery.

## 12. Próximos Pasos Sugeridos
1. **Fase 1 – Limpieza y auditoría final de contenido**: ejecutar `--drift-only`, validar pareos Polylang, confirmar markdown actualizado y enlazar posts en producción.
2. **Fase 2 – Tokens CSS y diseño**: abordar BKLG-005 creando catálogo de variables (color, tipografía, spacing, radius) y refactorizando estilos.
3. **Fase 3 – Maquetado Home y páginas base**: aplicar contenido definitivo ES/EN, incorporar imágenes y CTAs alineadas con servicios.
4. **Fase 4 – SEO técnico, performance y accesibilidad**: completar OG image set, integrar analytics, reforzar auditorías Lighthouse/axe como gates y generar subsets de fuentes.
5. **Fase 5 – Integración SMTP y pruebas**: ejecutar checklist SMTP, validar entregabilidad en ambos idiomas, actualizar copy de contacto a “Operativo”.
6. **Fase 6 – Publicación final y métricas**: ejecutar despliegue final, revalidar KPIs (Lighthouse, PSI, enlaces, SEO audit), publicar snapshot de cierre y activar monitoreo continuo en `public/status.json`.
