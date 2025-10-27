# Fase 3: Pasos Finales de Configuración WP

## Estado Actual

✅ **Completado:**
- Templates desplegados (page-home.php, page-about.php, page-projects.php, page-resources.php)
- OG images generadas y desplegadas (og-home-es.png, og-home-en.png)
- functions.php con lógica dinámica de OG
- Código mergeado a `main` (PR #8)

⚠️ **Pendiente (requiere WP Admin o Application Password):**

### 1. Configurar Front Page

**Objetivo:** Hacer que `https://pepecapiro.com/` muestre el template `page-home.php` refactorizado

**Método A - WP Admin UI:**
1. Ir a `https://pepecapiro.com/wp-admin/options-reading.php`
2. En "La portada muestra": seleccionar **"Una página estática"**
3. En "Página de inicio": seleccionar **"Inicio"** (debe ser ID 5)
4. Guardar cambios

**Método B - REST API (vía curl):**
```bash
# Configurar credenciales
WP_URL="https://pepecapiro.com"
WP_USER="<tu_usuario>"  # ej: ppcapiro
WP_APP_PASSWORD="<app_password>"  # Del perfil WP → Application Passwords

# Ejecutar
curl -u "$WP_USER:$WP_APP_PASSWORD" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"show_on_front":"page","page_on_front":5}' \
  "${WP_URL}/wp-json/wp/v2/settings"
```

**Verificación:**
```bash
curl https://pepecapiro.com/ | grep -o "Consultor en IA y Tecnología"
# Debe devolver: "Consultor en IA y Tecnología"
```

---

### 2. Crear Páginas para Proyectos y Recursos

**Páginas a crear:**

| Título | Slug | Template | Lang | Descripción |
|--------|------|----------|------|-------------|
| Proyectos | `proyectos` | `page-projects.php` | ES | Portfolio proyectos |
| Projects | `projects` | `page-projects.php` | EN | Projects portfolio |
| Recursos | `recursos` | `page-resources.php` | ES | Colección recursos |
| Resources | `resources` | `page-resources.php` | EN | Resources collection |

**Método A - WP Admin UI:**
1. Ir a `Páginas → Añadir nueva`
2. Título: **Proyectos**
3. Slug (permalink): **proyectos**
4. Plantilla de página (sidebar): **Projects** (`page-projects.php`)
5. Estado: **Publicar**
6. Repetir para Projects (EN), Recursos (ES), Resources (EN)

**Método B - REST API (script automatizado):**
```bash
#!/bin/bash
WP_URL="https://pepecapiro.com"
WP_USER="<tu_usuario>"
WP_APP_PASSWORD="<app_password>"

AUTH="$WP_USER:$WP_APP_PASSWORD"
API="${WP_URL}/wp-json/wp/v2/pages"

# Proyectos ES
curl -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Proyectos","slug":"proyectos","status":"publish","template":"page-projects.php"}' \
  "$API"

# Projects EN
curl -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Projects","slug":"projects","status":"publish","template":"page-projects.php"}' \
  "$API"

# Recursos ES
curl -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Recursos","slug":"recursos","status":"publish","template":"page-resources.php"}' \
  "$API"

# Resources EN
curl -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Resources","slug":"resources","status":"publish","template":"page-resources.php"}' \
  "$API"
```

**Verificación:**
```bash
curl -I https://pepecapiro.com/proyectos/ | head -1  # Debe ser 200 OK
curl -I https://pepecapiro.com/resources/ | head -1  # Debe ser 200 OK
```

---

### 3. Actualizar Menús

**Estructura objetivo (según `content/menus/menus.json`):**

**Principal ES:**
1. Inicio (`/`)
2. Sobre mí (`/sobre-mi/`)
3. **Proyectos** (`/proyectos/`) ← AÑADIR
4. **Recursos** (`/recursos/`) ← AÑADIR
5. Blog (`/blog/`)
6. Contacto (`/contacto/`)

**Main EN:**
1. Home (`/en/`)
2. About (`/about/`)
3. **Projects** (`/projects/`) ← AÑADIR
4. **Resources** (`/resources/`) ← AÑADIR
5. Blog (`/en/blog/`)
6. Contact (`/contact/`)

**Método - WP Admin UI:**
1. Ir a `Apariencia → Menús`
2. Seleccionar menú **Principal ES**
3. En panel izquierdo → **Páginas** → Buscar "Proyectos" y "Recursos"
4. Añadir al menú y reordenar según estructura
5. Guardar menú
6. Repetir para **Main EN** (añadir Projects y Resources)

---

### 4. Purgar Cache LiteSpeed

**Después de todos los cambios:**

```bash
curl "https://pepecapiro.com/?LSCWP_CTRL=PURGE_ALL"
```

O desde WP Admin:
- Barra superior → **LiteSpeed Cache** → **Purge All**

---

### 5. Validación Final

Verificar URLs públicas:

```bash
# Front page con nuevo hero
curl -s https://pepecapiro.com/ | grep "Consultor en IA y Tecnología"

# Nuevas páginas
curl -I https://pepecapiro.com/proyectos/  # 200 OK
curl -I https://pepecapiro.com/projects/   # 200 OK
curl -I https://pepecapiro.com/recursos/   # 200 OK
curl -I https://pepecapiro.com/resources/  # 200 OK

# OG images
curl -I https://pepecapiro.com/assets/og/og-home-es.png  # 200 OK
```

Verificar en navegador:
- `https://pepecapiro.com/` → Hero "Consultor en IA y Tecnología"
- `https://pepecapiro.com/proyectos/` → 3 tarjetas de proyectos
- `https://pepecapiro.com/recursos/` → 4 recursos con iconos
- Open Graph (compartir en redes) → Imagen personalizada

---

## Ejecución Rápida (Todo en Uno)

```bash
#!/bin/bash
# fase3_final_setup.sh
# Copiar/pegar este script completo en terminal con credenciales

WP_URL="https://pepecapiro.com"
read -p "Usuario WP: " WP_USER
read -sp "Application Password: " WP_APP_PASSWORD
echo ""

AUTH="$WP_USER:$WP_APP_PASSWORD"
API="${WP_URL}/wp-json/wp/v2"

echo "1. Configurando front page..."
curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"show_on_front":"page","page_on_front":5}' \
  "${WP_URL}/wp-json/wp/v2/settings" | jq -r '.page_on_front'

echo "2. Creando Proyectos..."
curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Proyectos","slug":"proyectos","status":"publish","template":"page-projects.php"}' \
  "$API/pages" | jq -r '.id + " - " + .link'

echo "3. Creando Projects..."
curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Projects","slug":"projects","status":"publish","template":"page-projects.php"}' \
  "$API/pages" | jq -r '.id + " - " + .link'

echo "4. Creando Recursos..."
curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Recursos","slug":"recursos","status":"publish","template":"page-resources.php"}' \
  "$API/pages" | jq -r '.id + " - " + .link'

echo "5. Creando Resources..."
curl -s -u "$AUTH" -X POST -H "Content-Type: application/json" \
  -d '{"title":"Resources","slug":"resources","status":"publish","template":"page-resources.php"}' \
  "$API/pages" | jq -r '.id + " - " + .link'

echo "6. Purgando cache..."
curl -s "${WP_URL}/?LSCWP_CTRL=PURGE_ALL" > /dev/null

echo ""
echo "✅ Configuración completada"
echo "⚠️  MANUAL: Actualizar menús en WP Admin → Apariencia → Menús"
```

---

## Notas

- **Application Password:** Se genera en `https://pepecapiro.com/wp-admin/profile.php` (sección "Application Passwords")
- **Seguridad:** El Application Password se puede revocar después de usar
- **Menús:** La actualización de menús via REST API requiere plugin adicional (por eso se recomienda UI manual)
- **Polylang:** Las traducciones ES↔EN se pueden vincular manualmente en WP Admin después de crear páginas

**Tiempo estimado:** 5-10 minutos (script automatizado) + 5 minutos (menús manuales)
