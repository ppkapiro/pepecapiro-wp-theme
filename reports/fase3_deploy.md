# Fase 3 — Deploy a Producción

Ejecutado: 2025-10-27 15:08 UTC-4

## Resumen

Deploy exitoso de Fase 3 (v0.9.1) a producción con todas las plantillas bilingües, imágenes OG y lógica dinámica.

## Archivos desplegados

### Plantillas PHP (6 archivos)
- ✅ `page-home.php` (4.5 KB) — Hero + pilares bilingües ES/EN
- ✅ `page-about.php` (3.1 KB) — About grid bilingüe
- ✅ `page-projects.php` (2.7 KB) — Grid proyectos (nuevo)
- ✅ `page-resources.php` (3.2 KB) — Grid recursos (nuevo)
- ✅ `functions.php` (16 KB) — Lógica OG dinámica extendida
- ✅ `style.css` (6.4 KB) — Versión bumpeada a 0.9.1

### Imágenes Open Graph (2 archivos)
- ✅ `assets/og/og-home-es.png` (215 KB, 1200×630)
- ✅ `assets/og/og-home-en.png` (210 KB, 1200×630)

## Verificación en producción

### Archivos confirmados
```bash
$ ssh pepecapiro "ls -1 page-*.php | wc -l"
7

$ ssh pepecapiro "grep 'Version:' style.css"
 Version: 0.9.1

$ ssh pepecapiro "ls -lh assets/og/og-home-*.png"
-rw-r--r-- 1 u525829715 o1007872188 210K Oct 27 19:08 assets/og/og-home-en.png
-rw-r--r-- 1 u525829715 o1007872188 215K Oct 27 19:08 assets/og/og-home-es.png
```

### Lógica OG funcional
```bash
$ ssh pepecapiro "grep -c 'page-projects.php\|page-resources.php' functions.php"
2
```
✅ Condicionales para `page-projects.php` y `page-resources.php` presentes en `functions.php`

### Respuesta HTTP
```
HTTP/2 200
x-litespeed-cache: hit
```
✅ Sitio respondiendo correctamente, caché funcionando

### Meta OG en Home
```html
<meta property="og:image" content="https://pepecapiro.com/wp-content/themes/pepecapiro/assets/og/og-home-es.png" />
```
✅ Imagen OG correcta servida dinámicamente según idioma

## Backup creado

Backup pre-deploy generado en servidor:
- `backup_pre_fase3_20251027_150817.tar.gz`
- Incluye: `style.css`, `functions.php`, `page-*.php`, `assets/og/`

## Siguiente fase pendiente

### Sincronización de contenido WP
**Pendiente**: Sincronizar `content/menus/menus.json` a WordPress via REST API.

#### Páginas a crear/verificar en WP Admin
Las siguientes páginas deben existir en WordPress con las plantillas asignadas:

| Página    | Slug ES    | Slug EN   | Plantilla          | Estado |
|-----------|------------|-----------|--------------------| -------|
| Inicio    | inicio     | home      | page-home.php      | ✓ Existe |
| Sobre mí  | sobre-mi   | about     | page-about.php     | ✓ Existe |
| Proyectos | proyectos  | projects  | page-projects.php  | ⚠ Crear |
| Recursos  | recursos   | resources | page-resources.php | ⚠ Crear |
| Contacto  | contacto   | contact   | page-contact.php   | ✓ Existe |

#### Menús a sincronizar
Actualizar menús **Principal ES** y **Main EN** en WP Admin con estructura de `content/menus/menus.json`:
- Inicio/Home
- Sobre mí/About
- Proyectos/Projects (nuevo)
- Recursos/Resources (nuevo)
- Blog
- Contacto/Contact

#### Método
1. **Opción A (Manual)**: WP Admin → Páginas → Añadir nueva → Asignar plantilla
2. **Opción B (Automatizado)**: Configurar `secrets/wp_creds.env` y ejecutar:
   ```bash
   python -m scripts.content.publish_content --apply
   ```

## Validación post-deploy

### CSS Anti-hex
```bash
$ python scripts/ci/check_css_tokens.py
[css-check] PASS: no hex colors found outside tokens.css
```
✅ Tokens CSS consistentes

### Commits
- `7975e97` — chore: bump version to 0.9.1 (Fase 3)
- `b61b2ab` — feat(fase3): plantillas bilingües, OG dinámico, menús completos

### Branch
- Rama activa: `feat/fases-0.3.0`
- Pendiente: merge a `main` tras validación visual en producción

## Próximos pasos

1. **Validación visual**: Revisar Home ES/EN en navegador (https://pepecapiro.com, https://pepecapiro.com/en/home/)
2. **Crear páginas**: Proyectos y Recursos en WP Admin con plantillas correctas
3. **Sincronizar menús**: Actualizar Principal ES y Main EN con ítems nuevos
4. **Merge a main**: `git checkout main && git merge feat/fases-0.3.0`
5. **Tag release**: `git tag v0.9.1 && git push origin v0.9.1`
6. **Fase 4**: SEO técnico (hreflang por página, schema About/Projects) + Performance (font subsets, Lighthouse)

## Notas

- Imágenes OG para About, Projects, Resources pueden generarse posteriormente (lógica ya preparada en `functions.php`)
- Templates usan SVG placeholders inline para evitar 403 de imágenes del tema
- Todos los estilos consumen tokens CSS (`--color-*`, `--space-*`, etc.)
- Copy bilingüe detecta idioma via `pll_current_language()`

