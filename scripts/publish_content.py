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
import time
import base64
import json
from typing import Dict, Any, Optional

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
POST_ES = {
    "slug": "checklist-wordpress-produccion-1-dia",
    "title": "Checklist para poner un WordPress a producir en 1 día",
    "excerpt": "Una guía práctica para pasar de cero a producción en 24 horas: seguridad, rendimiento, SEO, contenido mínimo y verificación.",
    "content": "<p>[Contenido largo ES: reemplazar o inyectar desde fuente externa]</p>",
    "lang": "es",
    "category_name": "Guías",
}
POST_EN = {
    "slug": "ship-wordpress-production-in-one-day",
    "title": "Ship a Production-Ready WordPress in One Day: A Practical Checklist",
    "excerpt": "A hands-on guide to go live in 24 hours: security, performance, SEO, minimum content, and final checks.",
    "content": "<p>[Long EN content: replace or inject from external source]</p>",
    "lang": "en",
    "category_name": "Guides",
}
PAGES = [
    {"slug": "privacidad", "title": "Política de Privacidad", "content": "<p>[Texto legal privacidad ES]</p>", "lang": "es"},
    {"slug": "cookies", "title": "Política de Cookies", "content": "<p>[Texto legal cookies ES]</p>", "lang": "es"},
    {"slug": "privacy", "title": "Privacy Policy", "content": "<p>[Legal privacy EN text]</p>", "lang": "en"},
    {"slug": "cookies", "title": "Cookies Policy", "content": "<p>[Legal cookies EN text]</p>", "lang": "en"},
]

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
            "content": item["content"],
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

    # Categorías
    cat_es_id = client.ensure_category(POST_ES["category_name"], POST_ES["lang"])
    cat_en_id = client.ensure_category(POST_EN["category_name"], POST_EN["lang"])
    print(f"[info] cat_es_id={cat_es_id} cat_en_id={cat_en_id}")

    post_es = client.create_or_update(POST_ES, is_post=True, category_id=cat_es_id)
    post_en = client.create_or_update(POST_EN, is_post=True, category_id=cat_en_id)
    if post_es: print(f"[ok] Post ES id={post_es['id']} url={post_es.get('link')}")
    if post_en: print(f"[ok] Post EN id={post_en['id']} url={post_en.get('link')}")

    # Páginas
    pages_created = []
    for p in PAGES:
        pg = client.create_or_update(p, is_post=False)
        if pg:
            pages_created.append(pg)
            print(f"[ok] Página {p['slug']} id={pg['id']} lang={p['lang']}")

    # Intentar enlazar traducciones posts
    if post_es and post_en:
        client.link_translations({"es": post_es['id'], "en": post_en['id']}, 'posts')

    # Enlazar páginas legales por slug agrupado
    def find_page_id(slug: str) -> Optional[int]:
        pg = client.find_content(slug, is_post=False)
        return pg.get('id') if pg else None
    priv_es = find_page_id('privacidad')
    priv_en = find_page_id('privacy')
    cook_es = find_page_id('cookies')  # mismo slug, se desambiguará por idioma interno
    cook_en = find_page_id('cookies')
    if priv_es and priv_en:
        client.link_translations({"es": priv_es, "en": priv_en}, 'pages')
    if cook_es and cook_en and cook_es != cook_en:  # si Polylang separa, IDs diferentes
        client.link_translations({"es": cook_es, "en": cook_en}, 'pages')

    # Validaciones HTTP básicas
    urls = []
    if post_es: urls.append(post_es.get('link'))
    if post_en: urls.append(post_en.get('link'))
    for slug in ('privacidad','privacy','cookies'):
        urls.append(f"{WP_URL}/{('en/' if slug=='privacy' else '')}{slug}/")

    health = True
    for u in urls:
        if not u: continue
        ok = validate_http(u)
        print(f"[check] {u} => {'OK' if ok else 'FAIL'}")
        health = health and ok

    print("[result] Éxito global" if health else "[result] Con incidencias (revisar logs)")
    return 0 if health else 1

if __name__ == '__main__':
    sys.exit(main())
