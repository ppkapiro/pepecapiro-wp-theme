# Fase 3 — Validación y Tareas Pendientes Post-Deploy

Actualizado: 2025-10-27 15:20

## Estado del deploy

✅ **Archivos desplegados correctamente**:
- 6 plantillas PHP (page-home.php, page-about.php, page-projects.php, page-resources.php, functions.php, style.css v0.9.1)
- 2 imágenes OG (og-home-es.png, og-home-en.png)

✅ **Verificación de archivos en servidor**: OK

⚠️ **Issue encontrado**: Página de inicio incorrecta

## Problema identificado

La raíz del sitio (https://pepecapiro.com/) está mostrando una página de prueba automática en lugar de la página "Inicio" con el nuevo template.

### Diagnóstico
```json
{
  "id": 133,
  "slug": "auto-prod-page-en-20251020-160949-2127",
  "title": "Auto Prod Page EN 20251020-160949 #2127",
  "template": "",
  "link": "https://pepecapiro.com/"
}
```

La página correcta está en `/inicio/`:
```json
{
  "id": 5,
  "slug": "inicio",
  "template": "page-home.php",
  "link": "https://pepecapiro.com/inicio/"
}
```

### Contenido visible actualmente
- Hero antiguo: "Soporte técnico y automatización, sin drama."
- Pilares nuevos: "Automatización práctica" ✓
- Template: Sin asignar (página ID 133)

## Tareas pendientes

### 1. Configurar front page correcta (URGENTE)

**Método recomendado — WP Admin**:
1. Ir a: `Ajustes → Lectura`
2. Seleccionar "Una página estática"
3. Página de inicio: **"Inicio"** (ID: 5, slug: inicio)
4. Guardar cambios
5. Purgar caché: `Ajustes → LiteSpeed Cache → Purgar todo`

**Alternativa — WP-CLI** (si disponible vía SSH):
```bash
wp option update show_on_front page
wp option update page_on_front 5
```

**Alternativa — REST API** (requiere credenciales WP):
```bash
curl -X POST https://pepecapiro.com/wp-json/wp/v2/settings \
  -u "usuario:app_password" \
  -H "Content-Type: application/json" \
  -d '{"show_on_front":"page","page_on_front":5}'
```

### 2. Crear páginas Proyectos y Recursos

Crear en WP Admin → Páginas → Añadir nueva:

**Página Proyectos ES**:
- Título: `Proyectos`
- Slug: `proyectos`
- Plantilla: `page-projects.php`
- Estado: Publicar
- Idioma: Español

**Página Projects EN**:
- Título: `Projects`
- Slug: `projects`
- Plantilla: `page-projects.php`
- Estado: Publicar
- Idioma: English

**Página Recursos ES**:
- Título: `Recursos`
- Slug: `recursos`
- Plantilla: `page-resources.php`
- Estado: Publicar
- Idioma: Español

**Página Resources EN**:
- Título: `Resources`
- Slug: `resources`
- Plantilla: `page-resources.php`
- Estado: Publicar
- Idioma: English

**Vincular traducciones** (Polylang):
- Proyectos ↔ Projects (translation_key: projects-page)
- Recursos ↔ Resources (translation_key: resources-page)

### 3. Actualizar menús

**Menú Principal ES** (ubicación: Primary):
- Inicio (`/inicio/`)
- Sobre mí (`/sobre-mi/`)
- **Proyectos** (`/proyectos/`) ← NUEVO
- **Recursos** (`/recursos/`) ← NUEVO
- Blog (`/blog/`)
- Contacto (`/contacto/`)

**Menú Main EN** (ubicación: Primary):
- Home (`/en/home/`)
- About (`/en/about/`)
- **Projects** (`/en/projects/`) ← NUEVO
- **Resources** (`/en/resources/`) ← NUEVO
- Blog (`/en/blog-en/`)
- Contact (`/en/contact/`)

Actualizar en: `Apariencia → Menús`

### 4. Eliminar página de prueba obsoleta

**Borrador o eliminar**:
- ID: 133
- Slug: `auto-prod-page-en-20251020-160949-2127`
- Motivo: Página de prueba automática que quedó asignada como front page

### 5. Validación visual post-corrección

Una vez configurada la front page correcta, verificar:

**Home ES** (`https://pepecapiro.com/` o `/inicio/`):
- [ ] Hero muestra: "Consultor en IA y Tecnología — Optimización de procesos..."
- [ ] 3 pilares: Automatización práctica, IA aplicada en Miami, Resultados medibles
- [ ] CTA enlaza a `/contacto/`
- [ ] Meta OG: `og-home-es.png`

**Home EN** (`https://pepecapiro.com/en/home/`):
- [ ] Hero muestra: "AI & Technology Consultant — Process optimization..."
- [ ] 3 pilares: Practical Automation, Applied AI in Miami, Measurable Results
- [ ] CTA enlaza a `/en/contact/`
- [ ] Meta OG: `og-home-en.png`

**About ES** (`https://pepecapiro.com/sobre-mi/`):
- [ ] Copy: "Soy Pepe Capiro, consultor en IA y Tecnología..."
- [ ] CTAs: LinkedIn + Agendar llamada

**About EN** (`https://pepecapiro.com/en/about/`):
- [ ] Copy: "I'm Pepe Capiro, AI and Technology consultant..."
- [ ] CTAs: Connect on LinkedIn + Schedule a call

**Projects/Resources** (tras crear páginas):
- [ ] Proyectos ES muestra 3 tarjetas placeholder
- [ ] Projects EN muestra 3 tarjetas traducidas
- [ ] Recursos ES muestra 4 tarjetas con íconos
- [ ] Resources EN muestra 4 tarjetas traducidas

## URLs de verificación

- Home ES raíz: https://pepecapiro.com/
- Home ES slug: https://pepecapiro.com/inicio/
- Home EN: https://pepecapiro.com/en/home/
- About ES: https://pepecapiro.com/sobre-mi/
- About EN: https://pepecapiro.com/en/about/
- Contact ES: https://pepecapiro.com/contacto/
- Contact EN: https://pepecapiro.com/en/contact/

(Proyectos y Recursos no existen aún en WP)

## Notas técnicas

- Templates desplegados consumen tokens CSS correctamente (validación anti-hex: PASS)
- Lógica OG dinámica en `functions.php` lista para todas las plantillas
- Copy bilingüe detecta idioma vía `pll_current_language()`
- SVG placeholders inline para evitar 403 de imágenes del tema
- Backup creado: `backup_pre_fase3_20251027_150817.tar.gz`

