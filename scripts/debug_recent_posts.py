#!/usr/bin/env python3
"""Obtiene últimos posts por idioma vía REST y guarda artefacto.
Uso:
  python scripts/debug_recent_posts.py --limit=5
Variables necesarias:
  WP_URL, WP_USER, WP_APP_PASSWORD
Salida:
  reports/publish/recent_posts.json y recent_posts.md
"""
import os, sys, json, base64
from datetime import datetime
import requests

WP_URL = os.getenv('WP_URL','https://pepecapiro.com').rstrip('/')
WP_USER = os.getenv('WP_USER','ADMIN_USER')
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD','APP_PASSWORD')
LIMIT = 5
for arg in sys.argv:
    if arg.startswith('--limit='):
        try:
            LIMIT = int(arg.split('=',1)[1])
        except ValueError:
            pass

AUTH = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
HEADERS = {"Authorization": f"Basic {AUTH}", "Accept":"application/json"}

langs = ['es','en']
results = {}
errors = []

for lang in langs:
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    params = {"per_page": LIMIT, "orderby":"date", "order":"desc", "_fields":"id,slug,status,link,date,title,lang"}
    # Intento 1: parámetro lang (Polylang suele aceptar 'lang')
    params['lang'] = lang
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    if r.status_code != 200:
        errors.append(f"lang={lang} status={r.status_code} body={r.text[:200]}")
        continue
    arr = r.json()
    simplified = []
    for obj in arr:
        simplified.append({
            'id': obj.get('id'),
            'slug': obj.get('slug'),
            'status': obj.get('status'),
            'date': obj.get('date'),
            'title': obj.get('title',{}).get('rendered',''),
            'link': obj.get('link'),
            'lang': obj.get('lang') or lang
        })
    results[lang] = simplified

out_dir = os.path.join('reports','publish')
os.makedirs(out_dir, exist_ok=True)
json_path = os.path.join(out_dir, 'recent_posts.json')
md_path = os.path.join(out_dir, 'recent_posts.md')
with open(json_path,'w',encoding='utf-8') as f:
    json.dump({'generated': datetime.utcnow().isoformat()+'Z', 'limit': LIMIT, 'results': results, 'errors': errors}, f, ensure_ascii=False, indent=2)
with open(md_path,'w',encoding='utf-8') as f:
    f.write('# Recent Posts Debug\n')
    f.write(f'Generado: {datetime.utcnow().isoformat()}Z\n\n')
    for lang in langs:
        f.write(f'## {lang}\n')
        for item in results.get(lang,[]):
            f.write(f"- {item['id']} {item['slug']} status={item['status']} link={item['link']}\n")
        if not results.get(lang):
            f.write('- (sin resultados)\n')
    if errors:
        f.write('\n## Errores\n')
        for e in errors:
            f.write(f'- {e}\n')
print(f"[debug] recent_posts escritos -> {json_path}")
