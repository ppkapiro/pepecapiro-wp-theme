# Manual de Exportación y Replicación del Ecosistema

**Versión**: 0.8.0  
**Última actualización**: 2025-10-20  
**Objetivo**: Guía completa para replicar el ecosistema pepecapiro-wp-theme en un nuevo repositorio/sitio WordPress

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerequisitos](#prerequisitos)
3. [Configuración Paso a Paso](#configuración-paso-a-paso)
4. [Modos de Replicación](#modos-de-replicación)
5. [Validación Post-Setup](#validación-post-setup)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Introducción

Este manual te guiará en la **replicación completa** del ecosistema de automatización WordPress + GitHub Actions desarrollado en el proyecto pepecapiro-wp-theme.

### ¿Qué incluye el Export Kit?

- **34+ workflows** de GitHub Actions (operaciones, verificación, monitorización)
- **Scripts de inicialización** (bootstrap.sh, validate_wp_connectivity.sh)
- **Configuración de datos** (pages.json, menus.json, settings.json)
- **Documentación completa** (API_REFERENCE, WEBHOOK_WP_TO_GITHUB)
- **Manifiesto de dependencias** (files_by_phase.json)

### Casos de Uso

- **Nuevo sitio WordPress**: Automatizar gestión desde GitHub
- **Migración de ecosistema**: Replicar infraestructura en otro repositorio
- **Multi-instancia**: Crear hub centralizado para varios sitios
- **Aprendizaje**: Estudiar arquitectura de automatización WordPress

---

## Prerequisitos

### 1. Instalación de Software

| Herramienta | Versión Mínima | Instalación |
|-------------|----------------|-------------|
| **Git** | 2.x | `sudo apt install git` (Linux) / [git-scm.com](https://git-scm.com) |
| **GitHub CLI** | 2.x | `sudo apt install gh` (Linux) / [cli.github.com](https://cli.github.com) |
| **jq** | 1.6+ | `sudo apt install jq` |
| **curl** | 7.x+ | (Preinstalado en mayoría de sistemas) |

Verificar instalación:
```bash
git --version
gh --version
jq --version
curl --version
```

### 2. WordPress Instalado

- **Versión**: WordPress 5.9 o superior (recomendado: 6.x)
- **Plugins requeridos**:
  - Ninguno (el ecosistema usa REST API nativa)
- **Plugins opcionales**:
  - **WP Webhooks** (para webhooks WP→GitHub, v0.7+)
  - **Polylang** (si necesitas multiidioma)
- **Permisos**:
  - Usuario con rol **Administrator**
  - Application Password habilitado (WordPress 5.6+)

#### Crear Application Password

1. Ir a `wp-admin` → Usuarios → Tu perfil
2. Desplazarse a **Application Passwords**
3. Introducir nombre (ej: "GitHub Actions")
4. Clic en **Add New Application Password**
5. **Copiar la contraseña** (NO la guardes en texto plano sin encriptar)

### 3. Repositorio de GitHub

- Repositorio nuevo o existente (público o privado)
- Permisos de admin para configurar secrets
- GitHub Actions habilitado (por defecto en repos nuevos)

---

## Configuración Paso a Paso

### Paso 1: Clonar el Repositorio Base

```bash
# Opción A: Fork (si quieres mantener referencia al original)
gh repo fork ppkapiro/pepecapiro-wp-theme --clone

# Opción B: Clone directo y reinicializar git
git clone https://github.com/ppkapiro/pepecapiro-wp-theme nuevo-proyecto
cd nuevo-proyecto
rm -rf .git
git init
gh repo create nuevo-proyecto --public --source=. --push
```

### Paso 2: Ejecutar Script de Bootstrap

```bash
bash export/scripts/bootstrap.sh
```

El script te guiará interactivamente:

1. **Verificación de WordPress**: Confirmará que tienes instalación lista
2. **Datos de conexión**: Solicitará URL, usuario y Application Password
3. **Validación de conectividad**: Probará conexión con WordPress REST API
4. **Configuración de secrets**: Añadirá `WP_URL`, `WP_USER`, `WP_APP_PASSWORD`, `WP_PATH` a GitHub
5. **API Gateway Token** (opcional): Configurará `API_GATEWAY_TOKEN` para webhooks externos
6. **Ajuste de configs**: Opción de editar `pages.json`, `menus.json`, `settings.json`
7. **Workflow de prueba**: Ejecutará `health-dashboard.yml` para validar setup

**Salida esperada**:
```
✅ Prerequisitos OK
✅ WordPress instalado
✅ Conectividad con WordPress OK
✅ Secrets configurados en GitHub
🎉 Bootstrap Completado
```

### Paso 3: Personalizar Configuración

#### 3.1. Páginas (configs/pages.json)

```json
{
  "pages": [
    {
      "title": "Inicio",
      "slug": "home",
      "content": "Bienvenido a mi sitio",
      "status": "publish",
      "template": "page-templates/full-width.php"
    }
  ]
}
```

Ajusta títulos, slugs, contenido y templates según tu diseño.

#### 3.2. Menús (configs/menus.json)

```json
{
  "menus": [
    {
      "name": "Menu Principal",
      "location": "primary",
      "items": [
        {
          "title": "Inicio",
          "url": "/",
          "type": "custom"
        },
        {
          "title": "Blog",
          "url": "/blog",
          "type": "post_type",
          "object": "post"
        }
      ]
    }
  ]
}
```

Define estructura de navegación.

#### 3.3. Ajustes (configs/settings.json)

```json
{
  "settings": {
    "blogname": "Mi Sitio WordPress",
    "blogdescription": "Automatizado con GitHub Actions",
    "timezone_string": "Europe/Madrid",
    "permalink_structure": "/%postname%/"
  }
}
```

Configura opciones generales de WordPress.

### Paso 4: Ejecutar Workflows

#### 4.1. Crear Páginas

```bash
gh workflow run create-pages.yml
```

Monitorizar ejecución:
```bash
gh run watch
```

#### 4.2. Publicar Posts (opcional)

Crear archivo en `content/posts/mi-primer-post.md`:
```markdown
---
title: Mi Primer Post
date: 2025-10-20
status: publish
---

Contenido del post.
```

Ejecutar workflow:
```bash
gh workflow run create-posts.yml
```

#### 4.3. Configurar Menús

```bash
gh workflow run create-menus.yml
```

#### 4.4. Aplicar Ajustes

```bash
gh workflow run configure-wp-settings.yml
```

### Paso 5: Verificación

Ejecutar workflows de verificación:

```bash
# Verificar home
gh workflow run verify-home.yml

# Verificar menús
gh workflow run verify-menus.yml

# Verificar configuración
gh workflow run verify-settings.yml
```

Revisar resultados en GitHub Actions o consultar `public/status.json` (generado por `health-dashboard.yml`).

---

## Modos de Replicación

### Modo Completo (Default)

Incluye **todos los workflows**: operación, verificación, monitorización, integración externa.

```bash
bash export/scripts/bootstrap.sh
```

**Componentes**:
- 5 workflows de operación (create-pages, create-posts, create-menus, upload-media, configure-wp-settings)
- 4 workflows de verificación (verify-home, verify-menus, verify-media, verify-settings)
- 3 workflows de monitorización (health-dashboard, smoke-tests, weekly-audit)
- 2 workflows de integración (api-automation-trigger, webhook-github-to-wp)

### Modo Minimal

Solo workflows de **operación** (sin verificación ni monitorización).

```bash
bash export/scripts/bootstrap.sh --minimal
```

**Ideal para**:
- Setup rápido
- Ambientes de desarrollo
- Reducir complejidad inicial

### Modo Verify-Only

Solo workflows de **verificación** (sin operación).

```bash
bash export/scripts/bootstrap.sh --verify-only
```

**Ideal para**:
- Auditorías de sitios existentes
- Monitorización externa (sin modificar WordPress)

### Modo Dry-Run

Simula el proceso **sin hacer cambios reales** (no configura secrets, no ejecuta workflows).

```bash
bash export/scripts/bootstrap.sh --dry-run
```

**Ideal para**:
- Entender el flujo antes de ejecutar
- Validar prerequisitos
- Documentación y demostraciones

---

## Validación Post-Setup

### 1. Verificar Secrets Configurados

```bash
gh secret list
```

**Esperado**:
```
WP_URL              Updated 2025-10-20
WP_USER             Updated 2025-10-20
WP_APP_PASSWORD     Updated 2025-10-20
WP_PATH             Updated 2025-10-20
```

### 2. Ejecutar Health Dashboard

```bash
gh workflow run health-dashboard.yml
sleep 10
curl https://ppkapiro.github.io/nuevo-proyecto/public/status.json
```

**Salida esperada**:
```json
{
  "version": "0.6.0",
  "services": {
    "auth": "OK",
    "home": "OK",
    "menus": "OK",
    "media": "OK",
    "settings": "OK"
  },
  "health": "healthy",
  "issues": 0,
  "last_update": "2025-10-20T10:30:00Z"
}
```

### 3. Verificar Conectividad Manual

```bash
bash scripts/validate_wp_connectivity.sh
```

**Esperado**:
```
✅ WordPress REST API accesible (HTTP 200)
✅ Autenticación válida
✅ Namespaces detectados: wp/v2, oembed/1.0, ...
```

### 4. Ejecutar Smoke Tests

```bash
gh workflow run smoke-tests.yml
```

Verificar que todos los tests pasan (revisa GitHub Actions).

---

## Troubleshooting

### Error: "No se pudo conectar a WordPress (HTTP 401)"

**Causas**:
- Application Password incorrecto
- Usuario sin permisos de administrador
- Plugin de seguridad bloqueando REST API

**Solución**:
1. Regenera Application Password en `wp-admin`
2. Verifica que el usuario tiene rol **Administrator**
3. Desactiva temporalmente plugins de seguridad (Wordfence, iThemes Security)
4. Añade IP de GitHub Actions a whitelist: [Lista de IPs](https://api.github.com/meta) (campo `actions`)

### Error: "Secrets no encontrados"

**Causa**: Secrets no configurados o mal nombrados

**Solución**:
```bash
# Verificar secrets actuales
gh secret list

# Reconfigurar manualmente
gh secret set WP_URL --body "https://mi-sitio.com"
gh secret set WP_USER --body "admin"
gh secret set WP_APP_PASSWORD --body "xxxx xxxx xxxx xxxx xxxx xxxx"
```

### Error: "Workflow no encontrado"

**Causa**: Workflows no commiteados o branch incorrecta

**Solución**:
```bash
# Verificar workflows presentes
ls -la .github/workflows/

# Commitear si faltan
git add .github/workflows/
git commit -m "feat: Add workflows"
git push
```

### Error: "jq: command not found"

**Causa**: `jq` no instalado

**Solución**:
```bash
# Linux (Debian/Ubuntu)
sudo apt update && sudo apt install jq

# macOS
brew install jq

# Verificar
jq --version
```

### Error: "API rate limit exceeded"

**Causa**: Demasiadas requests a GitHub API (5000/hora autenticado, 60/hora no autenticado)

**Solución**:
1. Autenticar con `gh auth login`
2. Reducir frecuencia de workflows (ej: weekly-audit de diario a semanal)
3. Implementar caching en workflows

### Webhook WP→GitHub no funciona

**Causa**: `API_GATEWAY_TOKEN` no configurado (issue #7)

**Solución**:
1. Generar GitHub Personal Access Token (classic):
   - Ir a https://github.com/settings/tokens/new
   - Scopes: `repo`, `workflow`
   - Copiar token
2. Configurar secret:
   ```bash
   gh secret set API_GATEWAY_TOKEN --body "ghp_..."
   ```
3. Configurar webhook en WordPress según `docs/WEBHOOK_WP_TO_GITHUB.md`

---

## FAQ

### ¿Puedo usar esto con Multisite?

Sí, pero requiere ajustes:
- Añadir `--url=https://site1.example.com` a comandos `wp`
- Configurar secrets por sitio (`WP_URL_SITE1`, `WP_URL_SITE2`, etc.)
- Duplicar workflows para cada sitio

### ¿Funciona con WordPress.com?

**No directamente**. WordPress.com tiene limitaciones en REST API y no soporta Application Passwords en planes gratuitos.  
Requiere plan **Business** o superior.

### ¿Puedo replicar solo algunos workflows?

Sí. Edita `export/manifests/files_by_phase.json` y filtra los workflows que necesites.  
Luego ejecuta `bootstrap.sh` con las opciones correspondientes.

### ¿Cómo actualizo el ecosistema cuando haya cambios?

```bash
# Añadir remoto original
git remote add upstream https://github.com/ppkapiro/pepecapiro-wp-theme

# Fetch cambios
git fetch upstream

# Merge selectivo (workflows específicos)
git cherry-pick <commit-hash>

# O merge completo
git merge upstream/main
```

### ¿Es seguro almacenar Application Password en secrets?

**Sí**. GitHub Secrets están encriptados y solo son accesibles por workflows del repositorio.  
**Nunca** los incluyas en código o commits.

### ¿Puedo usar esto en repositorio privado?

Sí, funciona igual. Asegúrate de que GitHub Actions esté habilitado (Settings → Actions → Allow all actions).

### ¿Cuánto cuesta ejecutar estos workflows?

- **Repositorios públicos**: **Gratis** (minutos ilimitados)
- **Repositorios privados**: 2000 minutos/mes gratis (plan Free), luego $0.008/minuto

Un workflow típico consume ~2-5 minutos, por lo que puedes ejecutar ~400-1000 workflows/mes gratis en repos privados.

---

## Soporte y Contribuciones

### Reportar Problemas

Abre un issue en el repositorio original:  
https://github.com/ppkapiro/pepecapiro-wp-theme/issues

Incluye:
- Descripción del problema
- Logs relevantes (de GitHub Actions)
- Comandos ejecutados
- Versión del Export Kit (ver `export/manifests/files_by_phase.json`)

### Contribuir

Pull requests bienvenidos. Para cambios grandes:
1. Abre un issue primero para discutir
2. Fork el repo
3. Crea branch (`git checkout -b feature/nueva-funcionalidad`)
4. Commit (`git commit -m 'feat: Nueva funcionalidad'`)
5. Push (`git push origin feature/nueva-funcionalidad`)
6. Abre Pull Request

---

## Créditos

- **Proyecto**: pepecapiro-wp-theme
- **Autor**: ppkapiro
- **Licencia**: [Revisar LICENSE en repositorio]
- **Versión Export Kit**: 0.8.0
- **Última actualización**: 2025-10-20

---

## Próximos Pasos

Una vez completado el setup:

1. **Explora la documentación**:
   - `docs/API_REFERENCE.md` (endpoints GET /status, POST /trigger)
   - `docs/WEBHOOK_WP_TO_GITHUB.md` (integración bidireccional)

2. **Configura monitorización**:
   - Habilita `weekly-audit.yml` (auditoría automática semanal)
   - Configura alertas (ej: Slack webhook en workflow `on: failure`)

3. **Expande el ecosistema**:
   - Añade workflows personalizados (usa `export/templates/workflow_template.yml`)
   - Integra con Hub Central (v0.9.0) para gestión multi-instancia

4. **Comparte tu experiencia**:
   - Documenta personalizaciones
   - Contribuye mejoras al repositorio original

---

**¡Gracias por usar el Export Kit de pepecapiro-wp-theme! 🚀**

Para cualquier duda, consulta la [documentación completa](https://github.com/ppkapiro/pepecapiro-wp-theme/tree/main/docs) o abre un [issue](https://github.com/ppkapiro/pepecapiro-wp-theme/issues).
