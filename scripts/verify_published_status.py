#!/usr/bin/env python3
"""Verifica que cada entrada declarada con status publish en content/posts.json y pages.json esté
realmente publicada (status=publish) en el remoto WordPress; reporta desajustes.

Salida:
  reports/publish/status_mismatches.json
  reports/publish/status_mismatches.md
Exit code:
  0 si todo consistente, 1 si hay desajustes o errores de acceso.
"""
import os, json, base64, sys
from datetime import datetime
import requests

WP_URL = os.getenv('WP_URL','https://pepecapiro.com').rstrip('/')
WP_USER = os.getenv('WP_USER','ADMIN_USER')
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD','APP_PASSWORD')

AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Accept": "application/json"}

CONTENT_DIR = os.getenv('CONTENT_DIR','content')

# Cargar definiciones locales
posts_cfg = []
pages_cfg = []
try:
    with open(os.path.join(CONTENT_DIR,'posts.json'),'r',encoding='utf-8') as f:
        posts_cfg = json.load(f)
except Exception as e:
    print(f"[warn] No se pudo leer posts.json: {e}")
try:
    with open(os.path.join(CONTENT_DIR,'pages.json'),'r',encoding='utf-8') as f:
        pages_cfg = json.load(f)
except FileNotFoundError:
    pass

# Expandir a lista por idioma de lo que espera publish
expected = []
for entry in posts_cfg:
    dis = entry.get('disabled')
    slug_field = entry.get('slug')
    slug_es = slug_en = None
    if isinstance(slug_field, dict):
        slug_es = slug_field.get('es')
        slug_en = slug_field.get('en')
    else:
        slug_es = slug_field
    for lang in ('es','en'):
        if isinstance(dis, dict) and dis.get(lang):
            continue
        if dis is True:
            continue
        status_field = entry.get('status','publish')
        if isinstance(status_field, dict):
            status_lang = status_field.get(lang,'publish')
        else:
            status_lang = status_field
        if status_lang != 'publish':
            continue
        slug = slug_es if (lang=='es' or not slug_en) else slug_en
        expected.append({'type':'post','slug':slug,'lang':lang})

for entry in pages_cfg:
    dis = entry.get('disabled')
    slug_field = entry.get('slug')
    slug_es = slug_en = None
    if isinstance(slug_field, dict):
        slug_es = slug_field.get('es')
        slug_en = slug_field.get('en')
    else:
        slug_es = slug_field
    for lang in ('es','en'):
        if isinstance(dis, dict) and dis.get(lang):
            continue
        if dis is True:
            continue
        status_field = entry.get('status','publish')
        if isinstance(status_field, dict):
            status_lang = status_field.get(lang,'publish')
        else:
            status_lang = status_field
        if status_lang != 'publish':
            continue
        slug = slug_es if (lang=='es' or not slug_en) else slug_en
        expected.append({'type':'page','slug':slug,'lang':lang})

mismatches = []
errors = []

def fetch(slug: str, is_post: bool):
    endpoint = f"{WP_URL}/wp-json/wp/v2/{'posts' if is_post else 'pages'}"
    params = { 'slug': slug, 'per_page': 1 }
    r = requests.get(endpoint, headers=HEADERS, params=params, timeout=20)
    if r.status_code != 200:
        errors.append(f"slug={slug} http={r.status_code} body={r.text[:160]}")
        return None
    arr = r.json()
    if not arr:
        return None
    return arr[0]

for item in expected:
    remote = fetch(item['slug'], is_post=(item['type']=='post'))
    if not remote:
        mismatches.append({**item, 'issue':'missing'})
        continue
    r_status = remote.get('status')
    if r_status != 'publish':
        mismatches.append({**item, 'issue':'status', 'remote_status': r_status, 'id': remote.get('id')})

out_dir = os.path.join('reports','publish')
os.makedirs(out_dir, exist_ok=True)
json_path = os.path.join(out_dir,'status_mismatches.json')
md_path = os.path.join(out_dir,'status_mismatches.md')
with open(json_path,'w',encoding='utf-8') as f:
    json.dump({'generated': datetime.utcnow().isoformat()+'Z', 'expected_publish': expected, 'mismatches': mismatches, 'errors': errors}, f, ensure_ascii=False, indent=2)
with open(md_path,'w',encoding='utf-8') as f:
    f.write('# Status Mismatches\n')
    f.write(f'Generado: {datetime.utcnow().isoformat()}Z\n\n')
    if mismatches:
        f.write('## Desajustes\n')
        for m in mismatches:
            if m['issue']=='missing':
                f.write(f"- MISSING {m['type']} {m['slug']} ({m['lang']})\n")
            else:
                f.write(f"- STATUS {m['type']} {m['slug']} ({m['lang']}) remoto={m.get('remote_status')}\n")
    else:
        f.write('Sin desajustes.\n')
    if errors:
        f.write('\n## Errores HTTP\n')
        for e in errors:
            f.write(f'- {e}\n')

exit(1 if mismatches or errors else 0)
