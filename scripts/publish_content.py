#!/usr/bin/env python3
"""
Automatiza creación de contenido inicial (posts y páginas legales) en WordPress con Polylang.

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
import re
import hashlib
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests  # Dependencia externa: instalar con `pip install requests` si se ejecuta fuera de entorno CI

# Buffer de depuración HTTP (se volcará a reports/publish/http_debug.json).
HTTP_DEBUG: List[Dict[str, Any]] = []

WP_URL = ""
WP_USER = ""
WP_APP_PASSWORD = ""
TIMEOUT = 20

HEADERS: Dict[str, str] = {}

CREDENTIALS_FILE = Path("secrets/.wp_env.local")
ALLOWED_DOMAIN = "pepecapiro.com"
CREDENTIAL_KEYS = ("WP_URL", "WP_USER", "WP_APP_PASSWORD")
API_POSTS = ""
API_PAGES = ""
API_CATS = ""
API_MEDIA = ""


def parse_credentials_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.is_file():
        return data
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in CREDENTIAL_KEYS and value:
                data[key] = value
    except OSError:
        pass
    return data


def sanitize_wp_url(url: str) -> str:
    url = url.strip()
    if url.endswith("/"):
        url = url.rstrip("/")
    return url


def resolve_wp_credentials() -> Tuple[Dict[str, str], Dict[str, str]]:
    values: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    for key in CREDENTIAL_KEYS:
        val = os.getenv(key)
        if val:
            values[key] = val.strip()
            sources[key] = "env"
    missing = [key for key in CREDENTIAL_KEYS if key not in values]
    if missing:
        file_values = parse_credentials_file(CREDENTIALS_FILE)
        for key in missing:
            val = file_values.get(key)
            if val:
                values[key] = val.strip()
                sources[key] = f"file:{CREDENTIALS_FILE}"
    return values, sources


def build_headers(user: str, app_password: str) -> Dict[str, str]:
    token = base64.b64encode(f"{user}:{app_password}".encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def render_preflight(creds: Dict[str, str], sources: Optional[Dict[str, str]] = None) -> None:
    wp_url = creds.get("WP_URL", "")
    display_url = "-"
    if wp_url:
        parsed = urlparse(wp_url)
        display_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else wp_url
    print(f"[preflight] WP_URL: {'OK' if wp_url else 'NO'} ({display_url})")
    print(f"[preflight] WP_USER: {'OK' if creds.get('WP_USER') else 'NO'}")
    print(f"[preflight] WP_APP_PASSWORD: {'OK' if creds.get('WP_APP_PASSWORD') else 'NO'}")
    if sources:
        summary = ", ".join(f"{key}:{sources.get(key, '-')}" for key in CREDENTIAL_KEYS)
        print(f"[preflight] Origen credenciales: {summary}")


def configure_endpoints(base_url: str) -> None:
    global API_POSTS, API_PAGES, API_CATS, API_MEDIA
    API_POSTS = f"{base_url}/wp-json/wp/v2/posts"
    API_PAGES = f"{base_url}/wp-json/wp/v2/pages"
    API_CATS = f"{base_url}/wp-json/wp/v2/categories"
    API_MEDIA = f"{base_url}/wp-json/wp/v2/media"

DRY_SAFE = '--dry-run' in sys.argv or os.getenv('DRY_RUN','0') in ('1','true','TRUE')
DRIFT_ONLY = '--drift-only' in sys.argv  # nuevo modo solo informe de divergencias

# Datos de contenido
# Nuevo: función para cargar markdown y convertirlo muy simple a HTML
MD_BASE = os.getenv("CONTENT_DIR", "content")

def md_to_html(md: str) -> str:
    """Conversión Markdown muy ligera a HTML.
    Soporta:
      - Encabezados # .. ######
      - Listas con -, * (un nivel anidado usando indent 2/4 espacios)
      - Code blocks triple backtick ``` (sin resaltar)
      - Código inline `code`
      - Enlaces [texto](url)
      - Párrafos
        No pretende ser completo; evita dependencia externa.
        Extendido:
            - Imágenes ![alt](url)
            - Blockquotes > línea
    """
    lines = md.splitlines()
    html: List[str] = []
    in_code = False
    list_stack: List[int] = []  # niveles de indent

    def close_lists(to_level: int = 0):
        while list_stack and list_stack[-1] >= to_level:
            list_stack.pop()
            html.append('</ul>')

    for raw in lines:
        # Detectar fenced code
        if raw.strip().startswith('```'):
            if not in_code:
                close_lists(0)
                in_code = True
                html.append('<pre><code>')
            else:
                in_code = False
                html.append('</code></pre>')
            continue
        if in_code:
            # Escapar mínimo
            esc = raw.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            html.append(esc)
            continue

        line = raw.rstrip()
        if not line.strip():
            close_lists(0)
            continue

        # Encabezados
        m = re.match(r'^(#{1,6})\s+(.*)$', line.strip())
        if m:
            close_lists(0)
            level = len(m.group(1))
            html.append(f"<h{level}>{m.group(2).strip()}</h{level}>")
            continue

    # Listas (indent opcional)
        lm = re.match(r'^(\s*)([-*])\s+(.*)$', line)
        if lm:
            indent_spaces = len(lm.group(1).replace('\t','    '))
            # Normalizar nivel (cada 2 espacios = 1 nivel simple)
            level = indent_spaces // 2
            # Abrir niveles nuevos
            if not list_stack or level > list_stack[-1]:
                list_stack.append(level)
                html.append('<ul>')
            # Cerrar si retrocedemos
            while list_stack and level < list_stack[-1]:
                list_stack.pop()
                html.append('</ul>')
            content = lm.group(3).strip()
            content = re.sub(r'`([^`]+)`', lambda m: f"<code>{m.group(1)}</code>", content)
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html.append(f"<li>{content}</li>")
            continue

        # Blockquote
        bq = re.match(r'^>\s?(.*)$', line.strip())
        if bq:
            close_lists(0)
            content = bq.group(1).strip()
            content = re.sub(r'`([^`]+)`', lambda m: f"<code>{m.group(1)}</code>", content)
            content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', content)
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html.append(f"<blockquote><p>{content}</p></blockquote>")
            continue

        # Párrafo / inline code / links / imágenes
        txt = line.strip()
        txt = re.sub(r'`([^`]+)`', lambda m: f"<code>{m.group(1)}</code>", txt)
        txt = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" />', txt)
        txt = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', txt)
        html.append(f"<p>{txt}</p>")

    close_lists(0)
    if in_code:
        html.append('</code></pre>')
    return '\n'.join(html)

def load_md(slug: str, lang: str, fallback_html: str) -> str:
    path = os.path.join(MD_BASE, f"{slug}.{lang}.md")
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return md_to_html(f.read())
        except Exception as e:
            print(f"[warn] No se pudo leer {path}: {e}")
    return fallback_html

def load_posts_config(selected_keys: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    cfg_path = os.path.join(MD_BASE, 'posts.json')
    if not os.path.isfile(cfg_path):
        print(f"[fatal] No existe {cfg_path}. Crea content/posts.json")
        sys.exit(3)
    with open(cfg_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    posts: List[Dict[str, Any]] = []
    for entry in raw:
        tkey = entry.get("translation_key")
        if selected_keys and tkey not in selected_keys:
            continue
        # Control de desactivación global
        disabled_field = entry.get("disabled")
        if isinstance(disabled_field, bool) and disabled_field:
            print(f"[skip-disabled] translation_key={tkey} (global)")
            continue
        # Slugs bilingües normalizados (Fase 1). Se mantiene compatibilidad con formato legacy.
        slug_es = entry.get("slug_es")
        slug_en_override = entry.get("slug_en")
        legacy_slug_field = entry.get("slug")
        if not slug_es:
            if isinstance(legacy_slug_field, dict):
                slug_es = legacy_slug_field.get("es")
            elif isinstance(legacy_slug_field, str):
                slug_es = legacy_slug_field
        if not slug_en_override and isinstance(legacy_slug_field, dict):
            slug_en_override = legacy_slug_field.get("en")

        # Compatibilidad con heurísticas anteriores si aún no se define slug EN explícito
        if not slug_en_override and slug_es == 'checklist-wordpress-produccion-1-dia':
            slug_en_override = 'ship-wordpress-production-in-one-day'
        elif not slug_en_override and slug_es == 'gobernanza-automatizacion-wordpress-pequenos-equipos':
            slug_en_override = 'wordpress-governance-automation-small-teams'

        for lang in ("es","en"):
            title = entry["title"].get(lang)
            excerpt = entry["excerpt"].get(lang)
            category = entry["category"].get(lang)
            if not title or not excerpt or not category:
                continue
            # Desactivación por idioma si disabled es dict
            if isinstance(disabled_field, dict) and disabled_field.get(lang):
                print(f"[skip-disabled] translation_key={tkey} lang={lang}")
                continue
            slug = slug_es if lang == 'es' or not slug_en_override else slug_en_override
            if not slug:
                print(f"[warn] Falta slug para translation_key={tkey} lang={lang}")
                continue
            status_field = entry.get("status", "publish")
            if isinstance(status_field, dict):
                status_lang = status_field.get(lang, 'publish')
            else:
                status_lang = status_field
            posts.append({
                "translation_key": tkey,
                "slug": slug,
                "title": title,
                "excerpt": excerpt,
                "content_html": f"<p>[Placeholder {lang} – se cargará markdown si existe]</p>",
                "lang": lang,
                "category_name": category,
                "status": status_lang,
            })
    return posts
def parse_selected_keys() -> Optional[Set[str]]:
    keys = None
    for arg in sys.argv:
        if arg.startswith('--key='):
            raw = arg.split('=',1)[1].strip()
            if raw:
                keys = {k.strip() for k in raw.split(',') if k.strip()}
        elif arg == '--key':
            # next token
            try:
                idx = sys.argv.index('--key')
                if idx+1 < len(sys.argv):
                    raw = sys.argv[idx+1]
                    keys = {k.strip() for k in raw.split(',') if k.strip()}
            except ValueError:
                pass
    return keys

SELECTED_KEYS = parse_selected_keys()
if SELECTED_KEYS:
    print(f"[info] Filtrando translation_key en {SELECTED_KEYS}")
POSTS = load_posts_config(SELECTED_KEYS)

def load_pages_config(selected_keys: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
    cfg_path = os.path.join(MD_BASE, 'pages.json')
    if not os.path.isfile(cfg_path):
        return []
    with open(cfg_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    pages: List[Dict[str, Any]] = []
    for entry in raw:
        tkey = entry.get('translation_key')
        if selected_keys and tkey not in selected_keys:
            continue
        disabled_field = entry.get('disabled')
        if isinstance(disabled_field, bool) and disabled_field:
            print(f"[skip-disabled] page translation_key={tkey} (global)")
            continue
        slug_es = entry.get('slug_es')
        slug_en = entry.get('slug_en')
        legacy_slug_field = entry.get('slug')
        if not slug_es:
            if isinstance(legacy_slug_field, dict):
                slug_es = legacy_slug_field.get('es')
            elif isinstance(legacy_slug_field, str):
                slug_es = legacy_slug_field
        if not slug_en and isinstance(legacy_slug_field, dict):
            slug_en = legacy_slug_field.get('en')
        for lang in ('es','en'):
            title = entry.get('title', {}).get(lang)
            excerpt = entry.get('excerpt', {}).get(lang, '')
            if not title:
                continue
            if isinstance(disabled_field, dict) and disabled_field.get(lang):
                print(f"[skip-disabled] page {tkey} lang={lang}")
                continue
            slug = slug_es if lang == 'es' or not slug_en else slug_en
            if not slug:
                print(f"[warn] Falta slug para página {tkey} lang={lang}")
                continue
            status_field = entry.get('status', 'publish')
            if isinstance(status_field, dict):
                status_lang = status_field.get(lang, 'publish')
            else:
                status_lang = status_field
            pages.append({
                'translation_key': tkey,
                'slug': slug,
                'title': title,
                'excerpt': excerpt,
                'content_html': f"<p>[Placeholder page {lang}]</p>",
                'lang': lang,
                'status': status_lang,
            })
    return pages

PAGES = load_pages_config(SELECTED_KEYS)

# Cargar markdown dinámicamente si existen archivos content/<slug>.<lang>.md (posts y páginas)
def md_exists(slug: str, lang: str) -> bool:
    return os.path.isfile(os.path.join(MD_BASE, f"{slug}.{lang}.md"))

for p in POSTS:
    p["content_html"] = load_md(p["slug"], p["lang"], p["content_html"])
    p["md_found"] = md_exists(p["slug"], p["lang"])
for pg in PAGES:
    pg["content_html"] = load_md(pg["slug"], pg["lang"], pg["content_html"])
    pg["md_found"] = os.path.isfile(os.path.join(MD_BASE, f"{pg['slug']}.{pg['lang']}.md"))

class WPClient:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    def get(self, url: str, params=None) -> requests.Response:
        r = requests.get(url, headers=self.headers, params=params, timeout=TIMEOUT)
        try:
            HTTP_DEBUG.append({
                'ts': datetime.utcnow().isoformat()+'Z',
                'method': 'GET',
                'url': url,
                'params': params,
                'status': r.status_code,
                'ok': r.ok,
                'resp_excerpt': (r.text[:300] if r.text else ''),
            })
        except Exception:
            pass
        return r

    def post(self, url: str, data: Dict[str, Any]) -> requests.Response:
        r = requests.post(url, headers=self.headers, data=json.dumps(data), timeout=TIMEOUT)
        try:
            HTTP_DEBUG.append({
                'ts': datetime.utcnow().isoformat()+'Z',
                'method': 'POST',
                'url': url,
                'payload_keys': list(data.keys()) if isinstance(data, dict) else None,
                'status': r.status_code,
                'ok': r.ok,
                'resp_excerpt': (r.text[:300] if r.text else ''),
            })
        except Exception:
            pass
        return r

    def patch(self, url: str, data: Dict[str, Any]) -> requests.Response:
        r = requests.patch(url, headers=self.headers, data=json.dumps(data), timeout=TIMEOUT)
        try:
            HTTP_DEBUG.append({
                'ts': datetime.utcnow().isoformat()+'Z',
                'method': 'PATCH',
                'url': url,
                'payload_keys': list(data.keys()) if isinstance(data, dict) else None,
                'status': r.status_code,
                'ok': r.ok,
                'resp_excerpt': (r.text[:300] if r.text else ''),
            })
        except Exception:
            pass
        return r

    def upload_media(self, filepath: str, filename: str, mime: str) -> Optional[str]:
        try:
            with open(filepath, 'rb') as f:
                bin_data = f.read()
        except Exception as e:
            print(f"[warn] No se pudo leer media {filepath}: {e}")
            return None
        headers = dict(self.headers)
        headers.pop('Content-Type', None)  # WP exige boundary/multipart
        headers['Content-Disposition'] = f'attachment; filename={filename}'
        headers['Content-Type'] = mime
        r = requests.post(API_MEDIA, headers=headers, data=bin_data, timeout=TIMEOUT)
        if r.status_code not in (200,201):
            print(f"[warn] Falló subida media {filename}: {r.status_code} {r.text[:120]}")
            return None
        return r.json().get('source_url')

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
        # Soft delete: si marcado removed => draft (no crear nuevos)
        if item.get('removed'):
            if not existing:
                print(f"[removed-skip] No existe remoto slug={item['slug']}")
                return None
            if existing.get('status') == 'draft':
                print(f"[removed-skip] Ya draft slug={item['slug']}")
                return existing
            rrm = self.post(f"{endpoint}/{existing['id']}", {"status": "draft"})
            if rrm.status_code in (200,201):
                print(f"[removed] Marcado draft slug={item['slug']} id={existing['id']}")
                return rrm.json()
            print(f"[warn] Soft delete falló slug={item['slug']} {rrm.status_code}")
            return existing
        payload = {
            "title": item["title"],
            "content": item.get("content") or item.get("content_html",""),
            "slug": item["slug"],
            "status": item.get("status","publish"),
            "excerpt": item.get("excerpt", ""),
        }
        # Polylang hints
        payload["lang"] = item.get("lang")
        if is_post and category_id:
            payload["categories"] = [category_id]
        if existing:
            # Hash diff para evitar updates innecesarios
            existing_obj = existing
            cat_component = ''
            if is_post and category_id:
                cat_component = str(category_id)
            new_hash = hashlib.sha256((payload["title"] + payload["excerpt"] + payload["content"] + payload["status"] + cat_component).encode('utf-8')).hexdigest()
            old_title = existing_obj.get("title",{}).get("rendered","")
            old_excerpt = existing_obj.get("excerpt",{}).get("rendered","")
            old_content = existing_obj.get("content",{}).get("rendered","")
            existing_status = existing_obj.get('status','')
            existing_cats = ''
            if is_post:
                existing_cats = ','.join(str(c) for c in existing_obj.get('categories',[]))
            old_hash = hashlib.sha256((old_title + old_excerpt + old_content + existing_status + existing_cats).encode('utf-8')).hexdigest()
            if new_hash != old_hash:
                print(f"[update] slug={item['slug']} lang={item.get('lang')} id={existing_obj['id']} status_from={existing_status}->{payload['status']}")
                r = self.post(f"{endpoint}/{existing_obj['id']}", payload)
                if r.status_code in (200,201):
                    print(f"[update-ok] id={existing_obj['id']} slug={item['slug']} status={payload['status']}")
                    return r.json()
                print(f"[warn] Update falló {existing_obj['id']}: {r.status_code} body_excerpt={r.text[:160]}")
                return existing_obj
            print(f"[skip] Sin cambios slug={item['slug']} ({new_hash[:8]}) status={existing_status}")
            return existing_obj
        r = self.post(endpoint, payload)
        if r.status_code in (200,201):
            robj = r.json()
            print(f"[create-ok] slug={item['slug']} lang={item.get('lang')} id={robj.get('id')} status={robj.get('status')} link={robj.get('link')}")
            return robj
        print(f"[error] Creación falló {item['slug']}: {r.status_code} body_excerpt={r.text[:200]}")
        return None

    def link_translations(self, mapping: Dict[str,int], content_type: str):
        # Polylang no define endpoint REST estándar; aquí se intenta PATCH a uno de los IDs con meta
        any_id = next(iter(mapping.values()))
        endpoint = f"{self.base_url}/wp-json/wp/v2/{content_type}/{any_id}"
        payload = {"meta": {"pll_translations": mapping}}
        r = self.patch(endpoint, payload)
        if r.status_code not in (200,201):
            print(f"[warn] No se enlazaron traducciones {content_type}: {r.status_code} {r.text}")
            # Fallback sugerido (wp-cli) para ejecutar manualmente si REST no admite meta
            langs_cli = ' '.join([f"{lang}:{cid}" for lang,cid in mapping.items()])
            print("[hint] Fallback manual (wp-cli):")
            print(f"  wp pll translation set {content_type} {langs_cli}")
            print("[hint] O bien PATCH individual vía curl si meta se habilita:")
            print(f"  curl -u $WP_USER:$WP_APP_PASSWORD -X PATCH {endpoint} -H 'Content-Type: application/json' --data '{json.dumps(payload)}'")
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
    creds, sources = resolve_wp_credentials()
    if creds.get("WP_URL"):
        creds["WP_URL"] = sanitize_wp_url(creds["WP_URL"])
    render_preflight(creds, sources)

    missing = [key for key in CREDENTIAL_KEYS if not creds.get(key)]
    if missing:
        print("[fatal] Credenciales WP incompletas. Ejecuta python scripts/env/configure_wp_creds.py")
        return 2

    wp_url = creds["WP_URL"]
    if not wp_url.startswith("https://"):
        print("[fatal] WP_URL debe iniciar con https://")
        return 2
    if ALLOWED_DOMAIN not in wp_url:
        print(f"[fatal] WP_URL no autorizado ({wp_url}). Solo se admite {ALLOWED_DOMAIN}")
        return 2

    global WP_URL, WP_USER, WP_APP_PASSWORD, HEADERS
    WP_URL = wp_url
    WP_USER = creds["WP_USER"]
    WP_APP_PASSWORD = creds["WP_APP_PASSWORD"]
    HEADERS = build_headers(WP_USER, WP_APP_PASSWORD)
    configure_endpoints(WP_URL)

    client = WPClient(WP_URL, HEADERS)
    dry = os.getenv('DRY_RUN','0') in ('1','true','TRUE') or '--dry-run' in sys.argv
    if DRIFT_ONLY:
        dry = True
    if dry:
        print('[mode] DRY-RUN activo: no se enviarán mutaciones')
    if DRIFT_ONLY:
        print('[mode] DRIFT-ONLY: análisis de divergencias')
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

    plan_actions: List[Dict[str, Any]] = []
    created_posts: Dict[str, Dict[str, Any]] = {}
    created_pages: Dict[str, Dict[str, Any]] = {}
    # --- Procesar posts ---
    for p in POSTS:
        # removed
        if p.get('removed'):
            existing = client.find_content(p['slug'], is_post=True)
            action = 'removed-draft' if existing else 'removed-missing'
            plan_actions.append({'type':'post','slug':p['slug'],'lang':p['lang'],'action':action})
            if dry and not DRIFT_ONLY:
                print(f"[plan] {action} post slug={p['slug']} lang={p['lang']}")
                continue
        # markdown faltante
        if not p.get('md_found') and not p.get('removed'):
            msg = f"[skip-md] Falta markdown para {p['slug']}.{p['lang']}.md"
            plan_actions.append({'type':'post','slug':p['slug'],'lang':p['lang'],'action':'skip-md'})
            if dry:
                print(f"[plan]{msg}")
                continue
        if DRIFT_ONLY:
            continue
        if dry:
            plan_actions.append({'type':'post','slug':p['slug'],'lang':p['lang'],'action':'create-or-update','status':p.get('status')})
            print(f"[plan] Post {p['lang']} slug={p['slug']} status={p.get('status')} -> create_or_update")
            continue
        # apply
        cid = cat_ids.get(p['lang'], {}).get(p['category_name']) if p.get('category_name') else None
        obj = client.create_or_update(p, is_post=True, category_id=cid)
        if obj:
            created_posts[p['slug']] = obj
    # --- Procesar páginas ---
    for pg in PAGES:
        if pg.get('removed'):
            existing = client.find_content(pg['slug'], is_post=False)
            action = 'removed-draft' if existing else 'removed-missing'
            plan_actions.append({'type':'page','slug':pg['slug'],'lang':pg['lang'],'action':action})
            if dry and not DRIFT_ONLY:
                print(f"[plan] {action} page slug={pg['slug']} lang={pg['lang']}")
                continue
        if not pg.get('md_found') and not pg.get('removed'):
            plan_actions.append({'type':'page','slug':pg['slug'],'lang':pg['lang'],'action':'skip-md'})
            if dry:
                print(f"[plan][skip-md] Falta markdown para página {pg['slug']}.{pg['lang']}.md")
                continue
        if DRIFT_ONLY:
            continue
        if dry:
            plan_actions.append({'type':'page','slug':pg['slug'],'lang':pg['lang'],'action':'create-or-update','status':pg.get('status')})
            print(f"[plan] Página {pg['lang']} slug={pg['slug']} status={pg.get('status')} -> create_or_update")
            continue
        # apply
        obj = client.create_or_update(pg, is_post=False)
        if obj:
            created_pages[pg['slug']] = obj
    # --- Drift Only Report ---
    if DRIFT_ONLY:
        drift_entries: List[str] = []
        for p in POSTS + PAGES:
            existing = client.find_content(p['slug'], is_post=(p in POSTS))
            if not existing:
                drift_entries.append(f"MISSING {p['slug']}:{p['lang']}")
                continue
            local_hash = hashlib.sha256((p['title'] + p.get('excerpt','') + p['content_html'] + p.get('status','publish')).encode()).hexdigest()
            remote_hash = hashlib.sha256((existing.get('title',{}).get('rendered','') + existing.get('excerpt',{}).get('rendered','') + existing.get('content',{}).get('rendered','') + existing.get('status','')).encode()).hexdigest()
            if local_hash != remote_hash:
                drift_entries.append(f"DRIFT {p['slug']}:{p['lang']} local={local_hash[:8]} remote={remote_hash[:8]}")
        report = os.path.join(MD_BASE,'drift_report.md')
        with open(report,'w',encoding='utf-8') as f:
            f.write('# Drift Report\n')
            f.write(f'Generado: {datetime.utcnow().isoformat()}Z\n\n')
            if drift_entries:
                for line in drift_entries:
                    f.write(f'- {line}\n')
            else:
                f.write('Sin diferencias detectadas.\n')
        print(f"[drift] Reporte generado {report} ({len(drift_entries)} items)")
        return 0
    # --- Resumen Plan ---
    if dry:
        summary = os.path.join(MD_BASE,'content_plan_summary.md')
        with open(summary,'w',encoding='utf-8') as f:
            f.write('# Content Plan Summary\n')
            f.write(f'Generado: {datetime.utcnow().isoformat()}Z\n\n')
            for a in plan_actions:
                f.write(f"- {a['type']} {a.get('lang','')} {a['slug']} => {a['action']}{' ('+a.get('status','')+')' if a.get('status') else ''}\n")
        print(f"[plan-summary] {summary}")
        print('[result] DRY-RUN completado (no validaciones HTTP)')
        return 0
    # Enlazar traducciones (apply)
    if not dry and not DRIFT_ONLY:
        # Posts
        groups_posts: Dict[str, Dict[str,int]] = {}
        for p in POSTS:
            slug = p['slug']
            if slug in created_posts:
                tk = p['translation_key']
                groups_posts.setdefault(tk, {})[p['lang']] = created_posts[slug]['id']
        for mapping in groups_posts.values():
            if len(mapping) > 1:
                client.link_translations(mapping, 'posts')
        # Pages
        groups_pages: Dict[str, Dict[str,int]] = {}
        for pg in PAGES:
            slug = pg['slug']
            if slug in created_pages:
                tk = pg['translation_key']
                groups_pages.setdefault(tk, {})[pg['lang']] = created_pages[slug]['id']
        for mapping in groups_pages.values():
            if len(mapping) > 1:
                client.link_translations(mapping, 'pages')

    # Aplicar cambios (solo si no es DRIFT_ONLY)
    health = True
    if not DRIFT_ONLY:
        # Reemplazo de imágenes locales (media/*) tras creación (solo apply).
        # Estrategia: buscar <img src="media/..."> en contenido y subir si ruta existe.
        media_dir = os.path.join(MD_BASE, 'media')
        if os.path.isdir(media_dir):
            import mimetypes
            import re as _re
            # Cargar mapa de deduplicación (hash->url)
            media_map_path = os.path.join(MD_BASE, '.media_map.json')
            try:
                if os.path.isfile(media_map_path):
                    with open(media_map_path,'r',encoding='utf-8') as f:
                        media_map = json.load(f)
                else:
                    media_map = {}
            except Exception as e:
                print(f"[warn] No se pudo cargar media_map: {e}")
                media_map = {}
            media_map_changed = False
            pattern = _re.compile(r'<img src=\"(media/[^\"]+)\"')
            # Actualizar posts
            for slug, obj in list(created_posts.items()):
                rendered = obj.get('content', {}).get('rendered', '')
                matches = pattern.findall(rendered)
                replaced = False
                for rel in matches:
                    local_path = os.path.join(MD_BASE, rel)
                    if os.path.isfile(local_path):
                        # Calcular hash
                        h = hashlib.sha256()
                        try:
                            with open(local_path,'rb') as fb:
                                h.update(fb.read())
                            file_hash = h.hexdigest()
                        except Exception as e:
                            print(f"[warn] No se pudo hashear {local_path}: {e}")
                            file_hash = None
                        remote = None
                        if file_hash and file_hash in media_map:
                            remote = media_map[file_hash]
                            # print(f"[dedup] Reutilizando media {rel} -> {remote}")
                        else:
                            mime = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
                            remote = client.upload_media(local_path, os.path.basename(local_path), mime)
                            if remote and file_hash:
                                media_map[file_hash] = remote
                                media_map_changed = True
                        if remote:
                            new_html = rendered.replace(rel, remote)
                            if new_html != rendered:
                                rendered = new_html
                                replaced = True
                if replaced:
                    # Patch contenido final
                    payload = {"content": rendered}
                    r_up = client.post(f"{API_POSTS}/{obj['id']}", payload)
                    if r_up.status_code in (200,201):
                        created_posts[slug] = r_up.json()
                        print(f"[ok] Media inyectada post {slug}")
                    else:
                        print(f"[warn] No se pudo actualizar post {slug} con media: {r_up.status_code}")
            # Actualizar páginas
            for key, obj in list(created_pages.items()):
                rendered = obj.get('content', {}).get('rendered', '')
                matches = pattern.findall(rendered)
                replaced = False
                for rel in matches:
                    local_path = os.path.join(MD_BASE, rel)
                    if os.path.isfile(local_path):
                        h = hashlib.sha256()
                        try:
                            with open(local_path,'rb') as fb:
                                h.update(fb.read())
                            file_hash = h.hexdigest()
                        except Exception as e:
                            print(f"[warn] No se pudo hashear {local_path}: {e}")
                            file_hash = None
                        remote = None
                        if file_hash and file_hash in media_map:
                            remote = media_map[file_hash]
                        else:
                            mime = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
                            remote = client.upload_media(local_path, os.path.basename(local_path), mime)
                            if remote and file_hash:
                                media_map[file_hash] = remote
                                media_map_changed = True
                        if remote:
                            new_html = rendered.replace(rel, remote)
                            if new_html != rendered:
                                rendered = new_html
                                replaced = True
                if replaced:
                    payload = {"content": rendered}
                    r_up = client.post(f"{API_PAGES}/{obj['id']}", payload)
                    if r_up.status_code in (200,201):
                        created_pages[key] = r_up.json()
                        print(f"[ok] Media inyectada página {key}")
                    else:
                        print(f"[warn] No se pudo actualizar página {key} con media: {r_up.status_code}")
            if media_map_changed:
                try:
                    with open(media_map_path,'w',encoding='utf-8') as f:
                        json.dump(media_map, f, ensure_ascii=False, indent=2)
                    print(f"[dedup] media_map actualizado {media_map_path}")
                except Exception as e:
                    print(f"[warn] No se pudo escribir media_map: {e}")
    urls: List[str] = []
    for obj in created_posts.values():
        link = obj.get('link')
        if isinstance(link, str) and link:
            urls.append(link)
    # Comprobar legales según slugs base
    urls.extend([
        f"{WP_URL}/privacidad/",
        f"{WP_URL}/cookies/",
        f"{WP_URL}/en/privacy/",
        f"{WP_URL}/en/cookies/",
    ])

    if dry:
        print('[result] DRY-RUN completado (no validaciones HTTP)')
        return 0
    else:
        health = True
        for u in urls:
            if not u:
                continue
            ok = validate_http(u)
            print(f"[check] {u} => {'OK' if ok else 'FAIL'}")
            health = health and ok
    # Volcar debug HTTP
    try:
        debug_dir = os.path.join('reports','publish')
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir,'http_debug.json'),'w',encoding='utf-8') as fdbg:
            json.dump({'generated': datetime.utcnow().isoformat()+'Z', 'entries': HTTP_DEBUG}, fdbg, ensure_ascii=False, indent=2)
        print('[debug] http_debug.json generado')
    except Exception as e:
        print(f"[warn] No se pudo escribir http_debug.json: {e}")
        print("[result] Éxito global" if health else "[result] Con incidencias (revisar logs)")
        return 0 if health else 1

if __name__ == '__main__':
    sys.exit(main())
