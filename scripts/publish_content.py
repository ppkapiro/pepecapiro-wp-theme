#!/usr/bin/env python3
"""
Automatiza creación de contenido inicial (posts y páginas legales) en WordPress con Polylang.
Requisitos:
  - Usuario admin + contraseña de aplicación (Basic Auth).
  - WP REST API habilitada.
  - Polylang activo (para enlazar traducciones).
  - Rank Math (no se requiere llamada específica; canónicas se generan automáticamente).

Placeholders a definir vía variables de entorno o edición directa:
  WP_USER, WP_APP_PASSWORD, WP_URL (sin slash final)

Flujo:
 1. Resolver/crear categorías (Guías/Guides) y obtener IDs.
 2. Crear/actualizar post ES y EN (idempotente por slug).
 3. Crear/actualizar páginas legales ES (privacidad, cookies).
 4. Crear/actualizar páginas legales EN (privacy, cookies) y enlazar traducciones.
 5. Enlazar traducciones posts (ES<->EN) y legales (privacidad/privacy, cookies/cookies).
 6. Mostrar resumen (IDs, URLs) y validaciones HTTP 200.

Enlazado Polylang:
  - Polylang no ofrece endpoint REST oficial estándar; método usado:
    * Paso 1: crear cada recurso con el idioma mediante cabecera/param si disponible.
    * Paso 2: usar endpoint interno wp/v2/<type>/<id> PATCH con campo meta personalizado si el sitio expone/meta aceptado.
  - Si el sitio no acepta meta para enlazar traducciones vía REST, existe fallback indicando curl/wp-cli manual.

NOTA: Ajustar la variable POLY_TRANSLATION_ENDPOINT si existe un endpoint personalizado.
"""
import os
import sys
import base64
import json
from typing import Dict, Any, Optional, List

import requests

WP_URL = os.getenv("WP_URL", "https://pepecapiro.com")  # sin slash final
WP_USER = os.getenv("WP_USER", "ADMIN_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "APP_PASSWORD")
TIMEOUT = 20

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode(),
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Datos de contenido
# Nuevo: función para cargar markdown y convertirlo muy simple a HTML
MD_BASE = os.getenv("CONTENT_DIR", "content")

def md_to_html(md: str) -> str:
    # Conversión mínima: párrafos y encabezados (# -> h1, ## -> h2, etc.)
    html_lines: List[str] = []
    for raw_line in md.splitlines():
        line_clean = raw_line.strip()
        if not line_clean:
            continue
        if line_clean.startswith('###### '):
            html_lines.append(f"<h6>{line_clean[7:].strip()}</h6>")
        elif line_clean.startswith('##### '):
            html_lines.append(f"<h5>{line_clean[6:].strip()}</h5>")
        elif line_clean.startswith('#### '):
            html_lines.append(f"<h4>{line_clean[5:].strip()}</h4>")
        elif line_clean.startswith('### '):
            html_lines.append(f"<h3>{line_clean[4:].strip()}</h3>")
        elif line_clean.startswith('## '):
            html_lines.append(f"<h2>{line_clean[3:].strip()}</h2>")
        elif line_clean.startswith('# '):
            html_lines.append(f"<h1>{line_clean[2:].strip()}</h1>")
        elif line_clean.startswith('- '):
            # Simple lista: cerramos/abrimos manualmente (no soporta listas anidadas complejas)
            if not html_lines or not html_lines[-1].startswith('<ul'):
                html_lines.append('<ul>')
            html_lines.append(f"<li>{line_clean[2:].strip()}</li>")
        else:
            if html_lines and html_lines[-1] == '</ul>':
                # ensure not appended wrongly (placeholder logic simplified)
                pass
            html_lines.append(f"<p>{line_clean}</p>")
    # Cerrar listas abiertas
    if any(x.startswith('<li>') for x in html_lines) and not any(x == '</ul>' for x in html_lines):
        html_lines.append('</ul>')
    return '\n'.join(html_lines)

def load_md(slug: str, lang: str, fallback_html: str) -> str:
    path = os.path.join(MD_BASE, f"{slug}.{lang}.md")
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return md_to_html(f.read())
        except Exception as e:
            print(f"[warn] No se pudo leer {path}: {e}")
    return fallback_html

# Redefinir estructura: lista de posts con translation_key para agrupar
POSTS = [
    {
        "translation_key": "checklist-wp-prod-day",
        "slug": "checklist-wordpress-produccion-1-dia",
        "title": "Checklist para poner un WordPress a producir en 1 día",
        "excerpt": "Una guía práctica para pasar de cero a producción en 24 horas: seguridad, rendimiento, SEO, contenido mínimo y verificación.",
        "content_html": "<p>[Contenido largo ES: reemplazar o inyectar desde fuente externa]</p>",
        "lang": "es",
        "category_name": "Guías",
    },
    {
        "translation_key": "checklist-wp-prod-day",
        "slug": "ship-wordpress-production-in-one-day",
        "title": "Ship a Production-Ready WordPress in One Day: A Practical Checklist",
        "excerpt": "A hands-on guide to go live in 24 hours: security, performance, SEO, minimum content, and final checks.",
        "content_html": "<p>[Long EN content: replace or inject from external source]</p>",
        "lang": "en",
        "category_name": "Guides",
    },
    # Segundo post (nuevo) – tema más estratégico sobre gobernanza y automatización ligera
    {
        "translation_key": "governance-automation-pillars",
        "slug": "gobernanza-automatizacion-wordpress-pequenos-equipos",
        "title": "Gobernanza y Automatización en WordPress para Equipos Pequeños: 5 Pilares Prácticos",
        "excerpt": "Cinco pilares accionables para mantener orden, velocidad y calidad en un sitio WordPress sin sobrecarga operativa.",
        "content_html": "<p>[Borrador ES segundo post: se cargará desde markdown si existe gob-automation.es.md]</p>",
        "lang": "es",
        "category_name": "Guías",
    },
    {
        "translation_key": "governance-automation-pillars",
        "slug": "wordpress-governance-automation-small-teams",
        "title": "WordPress Governance & Automation for Small Teams: 5 Practical Pillars",
        "excerpt": "Five actionable pillars to keep order, speed and quality without operational fatigue.",
        "content_html": "<p>[Draft EN second post: will load from markdown if present]</p>",
        "lang": "en",
        "category_name": "Guides",
    },
]

PAGES = [
    {"slug": "privacidad", "title": "Política de Privacidad", "content_html": "<p>[Texto legal privacidad ES]</p>", "lang": "es"},
    {"slug": "cookies", "title": "Política de Cookies", "content_html": "<p>[Texto legal cookies ES]</p>", "lang": "es"},
    {"slug": "privacy", "title": "Privacy Policy", "content_html": "<p>[Legal privacy EN text]</p>", "lang": "en"},
    {"slug": "cookies", "title": "Cookies Policy", "content_html": "<p>[Legal cookies EN text]</p>", "lang": "en"},
]

# Cargar markdown dinámicamente si existen archivos content/<slug>.<lang>.md (posts y páginas)
for p in POSTS:
    p["content_html"] = load_md(p["slug"], p["lang"], p["content_html"])
for pg in PAGES:
    pg["content_html"] = load_md(pg["slug"], pg["lang"], pg["content_html"])

API_POSTS = f"{WP_URL}/wp-json/wp/v2/posts"
API_PAGES = f"{WP_URL}/wp-json/wp/v2/pages"
API_CATS = f"{WP_URL}/wp-json/wp/v2/categories"

class WPClient:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def get(self, url: str, params=None) -> requests.Response:
        return requests.get(url, headers=self.headers, params=params, timeout=TIMEOUT)

    def post(self, url: str, data: Dict[str, Any]) -> requests.Response:
        return requests.post(url, headers=self.headers, data=json.dumps(data), timeout=TIMEOUT)

    def patch(self, url: str, data: Dict[str, Any]) -> requests.Response:
        return requests.patch(url, headers=self.headers, data=json.dumps(data), timeout=TIMEOUT)

    def ensure_category(self, name: str, lang: str) -> Optional[int]:
        # Buscar por nombre exacto primero
        r = self.get(API_CATS, params={"search": name, "per_page": 50})
        if r.status_code == 200:
            for c in r.json():
                if c.get("name") == name:
                    return c.get("id")
        # Crear
        payload = {"name": name, "slug": slugify(name)}
        # Polylang: algunos setups aceptan 'lang' o 'pll_language'
        payload["lang"] = lang
        r2 = self.post(API_CATS, payload)
        if r2.status_code in (200,201):
            return r2.json().get("id")
        print(f"[warn] No se pudo crear categoría {name}: {r2.status_code} {r2.text}")
        return None

    def find_content(self, slug: str, is_post=True) -> Optional[Dict[str, Any]]:
        endpoint = API_POSTS if is_post else API_PAGES
        r = self.get(endpoint, params={"slug": slug})
        if r.status_code == 200 and r.json():
            return r.json()[0]
        return None

    def create_or_update(self, item: Dict[str, Any], is_post=True, category_id: Optional[int]=None) -> Optional[Dict[str, Any]]:
        endpoint = API_POSTS if is_post else API_PAGES
        existing = self.find_content(item["slug"], is_post=is_post)
        payload = {
            "title": item["title"],
            "content": item.get("content") or item.get("content_html",""),
            "slug": item["slug"],
            "status": "publish",
            "excerpt": item.get("excerpt", ""),
        }
        # Polylang hints
        payload["lang"] = item.get("lang")
        if is_post and category_id:
            payload["categories"] = [category_id]
        if existing:
            # Update minor fields if changed
            diff = False
            for f in ("title","content","excerpt"):
                # Simple heuristic (not diff HTML deeply)
                if f == "title" and existing.get("title",{}).get("rendered") != item["title"]:
                    diff = True
                if f == "content" and existing.get("content",{}).get("rendered","")[:120] != item["content"][:120]:
                    diff = True
                if f == "excerpt" and existing.get("excerpt",{}).get("rendered","")[:80] != item.get("excerpt","")[:80]:
                    diff = True
            if diff:
                r = self.post(f"{endpoint}/{existing['id']}", payload)  # WP admite POST para update
                if r.status_code not in (200,201):
                    print(f"[warn] Update falló {existing['id']}: {r.status_code} {r.text}")
                else:
                    existing = r.json()
            return existing
        else:
            r = self.post(endpoint, payload)
            if r.status_code not in (200,201):
                print(f"[error] Creación falló {item['slug']}: {r.status_code} {r.text}")
                return None
            return r.json()

    def link_translations(self, mapping: Dict[str,int], content_type: str):
        # Polylang no define endpoint REST estándar; aquí se intenta PATCH a uno de los IDs con meta
        any_id = next(iter(mapping.values()))
        endpoint = f"{self.base_url}/wp-json/wp/v2/{content_type}/{any_id}"
        payload = {"meta": {"pll_translations": mapping}}
        r = self.patch(endpoint, payload)
        if r.status_code not in (200,201):
            print(f"[warn] No se enlazaron traducciones {content_type}: {r.status_code} {r.text}")
        else:
            print(f"[ok] Traducciones enlazadas {content_type}: {mapping}")


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u").replace("ñ","n")


def validate_http(url: str) -> bool:
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200 and 'Page not found' not in r.text and 'Página no encontrada' not in r.text
    except Exception as e:
        print(f"[warn] HTTP fail {url}: {e}")
        return False


def main():
    missing = [k for k,v in {"WP_USER":WP_USER, "WP_APP_PASSWORD":WP_APP_PASSWORD}.items() if v in ("APP_PASSWORD","ADMIN_USER","")]
    if missing:
        print("[fatal] Debes exportar credenciales reales (WP_USER / WP_APP_PASSWORD)")
        sys.exit(2)

    client = WPClient(WP_URL, HEADERS)

    # Categorías (agrupar por lang => id)
    cat_ids: Dict[str, Dict[str,int]] = {}
    for p in POSTS:
        lang = p["lang"]
        cname = p["category_name"]
        if lang not in cat_ids:
            cat_ids[lang] = {}
        if cname not in cat_ids[lang]:
            cid = client.ensure_category(cname, lang)
            if cid:
                cat_ids[lang][cname] = cid
    print(f"[info] cat_ids={cat_ids}")

    created_posts: Dict[str, Dict[str, Any]] = {}
    # Crear/actualizar posts
    for p in POSTS:
        cid = cat_ids.get(p["lang"], {}).get(p["category_name"]) if p.get("category_name") else None
        obj = client.create_or_update(p, is_post=True, category_id=cid)
        if obj:
            created_posts[p["slug"]] = obj
            print(f"[ok] Post {p['lang']} slug={p['slug']} id={obj['id']}")

    # Link traducciones por translation_key
    translation_groups: Dict[str, Dict[str,int]] = {}
    for p in POSTS:
        slug = p["slug"]
        obj = created_posts.get(slug)
        if not obj:
            continue
        key = p["translation_key"]
        translation_groups.setdefault(key, {})[p["lang"]] = obj["id"]
    for key, mapping in translation_groups.items():
        if len(mapping) > 1:  # sólo enlazar si hay al menos dos idiomas
            client.link_translations(mapping, 'posts')

    # Páginas legales
    created_pages: Dict[str, Any] = {}
    for page in PAGES:
        obj = client.create_or_update({
            "title": page["title"],
            "slug": page["slug"],
            "content_html": page["content_html"],
            "lang": page["lang"],
        }, is_post=False)
        if obj:
            key = f"{page['slug']}:{page['lang']}"
            created_pages[key] = obj
            print(f"[ok] Página {page['lang']} slug={page['slug']} id={obj['id']}")

    # Enlazar traducciones legales (privacidad/privacy y cookies/cookies si difieren IDs)
    def find_page(slug: str, lang: str) -> Optional[int]:
        pg = created_pages.get(f"{slug}:{lang}")
        return pg.get('id') if pg else None
    priv_es = find_page('privacidad','es')
    priv_en = find_page('privacy','en')
    cook_es = find_page('cookies','es')
    cook_en = find_page('cookies','en')
    if priv_es and priv_en:
        client.link_translations({"es": priv_es, "en": priv_en}, 'pages')
    if cook_es and cook_en and cook_es != cook_en:
        client.link_translations({"es": cook_es, "en": cook_en}, 'pages')

    # Validaciones HTTP básicas
    urls: List[str] = []
    for obj in created_posts.values():
        urls.append(obj.get('link'))
    # Comprobar legales según slugs base
    urls.extend([
        f"{WP_URL}/privacidad/",
        f"{WP_URL}/cookies/",
        f"{WP_URL}/en/privacy/",
        f"{WP_URL}/en/cookies/",
    ])

    health = True
    for u in urls:
        if not u:
            continue
        ok = validate_http(u)
        print(f"[check] {u} => {'OK' if ok else 'FAIL'}")
        health = health and ok

    print("[result] Éxito global" if health else "[result] Con incidencias (revisar logs)")
    return 0 if health else 1

if __name__ == '__main__':
    sys.exit(main())
