# 🚀 Fase 3: Configuración Final

## Estado Actual

✅ **Todo el código está desplegado en producción**
- Templates refactorizados (Home, About, Projects, Resources)
- OG images generadas y subidas
- Versión 0.9.1 activa

⚠️ **Falta configuración en WordPress Admin**

---

## Opción Rápida: Script Automatizado

### Paso 1: Genera Application Password

1. Ve a: https://pepecapiro.com/wp-admin/profile.php
2. Scroll hasta "Application Passwords"
3. Nombre: `fase3-setup`
4. Click "Add New Application Password"
5. **Copia el password** (se muestra una sola vez)

### Paso 2: Ejecuta el Script

```bash
bash scripts/fase3_quick_setup.sh
```

El script te pedirá:
- Usuario WP (default: `ppcapiro`)
- Application Password (pegarlo)

**Tiempo:** ~2 minutos

### Paso 3: Actualiza Menús (Manual)

Esto NO se puede automatizar fácilmente via REST API:

1. Ve a: https://pepecapiro.com/wp-admin/nav-menus.php
2. Selecciona menú **"Principal ES"**
3. En panel izquierdo → **Páginas** → Marca:
   - ☑️ Proyectos
   - ☑️ Recursos
4. Click "Añadir al menú"
5. Arrastra para ordenar: Inicio, Sobre mí, **Proyectos**, **Recursos**, Blog, Contacto
6. Click "Guardar menú"
7. Repite para menú **"Main EN"** con Projects y Resources

**Tiempo:** ~5 minutos

---

## Validación

Después de ejecutar todo:

```bash
# Verificar hero refactorizado
curl -s https://pepecapiro.com/ | grep "Consultor en IA y Tecnología"

# Verificar nuevas páginas
curl -I https://pepecapiro.com/proyectos/
curl -I https://pepecapiro.com/resources/

# Verificar OG image
curl -I https://pepecapiro.com/assets/og/og-home-es.png
```

Navegador:
- https://pepecapiro.com/ → Debe mostrar hero "Consultor en IA y Tecnología"
- https://pepecapiro.com/proyectos/ → 3 tarjetas de proyectos
- https://pepecapiro.com/recursos/ → 4 recursos con emojis
- Menús → Deben tener 6 items (Inicio, Sobre mí, Proyectos, Recursos, Blog, Contacto)

---

## Si Algo Falla

### Front page no muestra nuevo hero
```bash
# Verificar qué página está como front
curl -s https://pepecapiro.com/wp-json/wp/v2/settings | jq '.page_on_front'
# Debe ser: 5

# Si es otro número, re-ejecutar script o hacerlo manual en:
# WP Admin → Ajustes → Lectura → Página de inicio = "Inicio"
```

### Páginas devuelven 404
```bash
# Verificar si existen
curl -s "https://pepecapiro.com/wp-json/wp/v2/pages?slug=proyectos" | jq '.[0].id'
# Si devuelve null, re-ejecutar script
```

### OG image no aparece al compartir
```bash
# Purgar cache social
# Facebook: https://developers.facebook.com/tools/debug/?q=https://pepecapiro.com/
# Twitter: https://cards-dev.twitter.com/validator
```

---

## Documentación Completa

- **Guía detallada:** `reports/fase3_manual_steps.md`
- **Resumen ejecutivo:** `reports/fase3_resumen.md`
- **Deployment log:** `reports/fase3_deploy.md`
- **Pendientes originales:** `reports/fase3_pendientes.md`

---

## Contacto

Si tienes dudas o errores:
1. Revisa logs del script
2. Verifica Application Password no haya expirado
3. Consulta documentación en `reports/`

**¡La Fase 3 está casi completa! Solo faltan 10 minutos de configuración manual** 🎉
