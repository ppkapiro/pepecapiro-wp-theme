#!/usr/bin/env python3
"""Obtiene últimos posts y páginas por idioma + categorías vía REST y guarda artefacto.
Uso:
    python scripts/debug_recent_posts.py --limit=5
Variables necesarias:
  WP_URL, WP_USER, WP_APP_PASSWORD
Salida:
    reports/publish/recent_posts.json y recent_posts.md
"""
import os
import sys
import json
import base64
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
results = { 'posts': {}, 'pages': {}, 'categories': {} }
errors = []

for lang in langs:
    # Posts
    url_posts = f"{WP_URL}/wp-json/wp/v2/posts"
    p_params = {"per_page": LIMIT, "orderby":"date", "order":"desc", "_fields":"id,slug,status,link,date,title,lang"}
    p_params['lang'] = lang
    rP = requests.get(url_posts, headers=HEADERS, params=p_params, timeout=20)
    if rP.status_code == 200:
        arr = rP.json()
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
        results['posts'][lang] = simplified
    else:
        errors.append(f"posts lang={lang} status={rP.status_code} body={rP.text[:180]}")
    # Pages
    url_pages = f"{WP_URL}/wp-json/wp/v2/pages"
    g_params = {"per_page": LIMIT, "orderby":"date", "order":"desc", "_fields":"id,slug,status,link,date,title,lang"}
    g_params['lang'] = lang
    rG = requests.get(url_pages, headers=HEADERS, params=g_params, timeout=20)
    if rG.status_code == 200:
        arr = rG.json()
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
        results['pages'][lang] = simplified
    else:
        errors.append(f"pages lang={lang} status={rG.status_code} body={rG.text[:180]}")
    # Categories
    url_cats = f"{WP_URL}/wp-json/wp/v2/categories"
    c_params = {"per_page": 50, "orderby":"count", "order":"desc", "_fields":"id,name,slug,count"}
    c_params['lang'] = lang
    rC = requests.get(url_cats, headers=HEADERS, params=c_params, timeout=20)
    if rC.status_code == 200:
        arr = rC.json()
        simplified = []
        for obj in arr:
            simplified.append({
                'id': obj.get('id'),
                'name': obj.get('name'),
                'slug': obj.get('slug'),
                'count': obj.get('count'),
            })
        results['categories'][lang] = simplified
    else:
        errors.append(f"categories lang={lang} status={rC.status_code} body={rC.text[:160]}")

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
        f.write(f'## Posts {lang}\n')
        for item in results['posts'].get(lang,[]):
            f.write(f"- {item['id']} {item['slug']} status={item['status']} link={item['link']}\n")
        if not results['posts'].get(lang):
            f.write('- (sin resultados)\n')
        f.write(f'\n## Pages {lang}\n')
        for item in results['pages'].get(lang,[]):
            f.write(f"- {item['id']} {item['slug']} status={item['status']} link={item['link']}\n")
        if not results['pages'].get(lang):
            f.write('- (sin resultados)\n')
        f.write(f'\n## Categories {lang}\n')
        for item in results['categories'].get(lang,[]):
            f.write(f"- {item['id']} {item['name']} slug={item['slug']} count={item['count']}\n")
        if not results['categories'].get(lang):
            f.write('- (sin resultados)\n')
    if errors:
        f.write('\n## Errores\n')
        for e in errors:
            f.write(f'- {e}\n')
print(f"[debug] recent_posts escritos -> {json_path}")
