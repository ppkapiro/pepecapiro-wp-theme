#!/usr/bin/env python3
import os
import json
import sys
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser

class TitleJSONLDParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ''
        self.jsonld_raw = []
        self._capture_jsonld = False
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'title':
            self.in_title = True
        if tag.lower() == 'script':
            at = dict(attrs)
            if at.get('type','').lower() == 'application/ld+json':
                self._capture_jsonld = True
                self._buf = []
    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False
        if tag.lower() == 'script' and self._capture_jsonld:
            raw = ''.join(self._buf).strip()
            if raw:
                self.jsonld_raw.append(raw)
            self._capture_jsonld = False
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if getattr(self, '_capture_jsonld', False):
            self._buf.append(data)

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent':'ContentVerify/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        status = r.status
        body = r.read().decode('utf-8','replace')
        return status, body

def load_posts_manifest():
    with open('content/posts.json','r',encoding='utf-8') as f:
        data = json.load(f)
    items = []
    for entry in data:
        status_field = entry.get('status','publish')
        for lang in ['es','en']:
            if isinstance(status_field, dict):
                st = status_field.get(lang,'publish')
            else:
                st = status_field
            if st == 'publish':
                slug_field = entry['slug']
                if isinstance(slug_field, dict):
                    slug = slug_field.get(lang) or slug_field.get('es')
                else:
                    slug = slug_field
                items.append({'lang':lang,'slug':slug,'title_expected':entry['title'][lang] if isinstance(entry['title'], dict) else entry['title']})
    return items

def main():
    base = os.environ.get('LIVE_BASE_URL','https://www.pepecapiro.com').rstrip('/')
    posts = load_posts_manifest()
    results = []
    errors = 0
    for p in posts:
        if p['lang'] == 'en':
            url = f"{base}/en/{p['slug'].strip('/')}/"
        else:
            url = f"{base}/{p['slug'].strip('/')}/"
        try:
            status, body = fetch(url, 20)
        except Exception as e:
            results.append({'url':url,'error':str(e),'ok':False})
            errors += 1
            continue
        parser = TitleJSONLDParser()
        parser.feed(body)
        title_clean = re.sub(r'\s+',' ', parser.title).strip()
        expected_norm = re.sub(r'\s+',' ', p['title_expected']).strip()
        title_ok = expected_norm[:40].lower() in title_clean.lower()
        jsonld_ok = any('"Article"' in raw or '"BlogPosting"' in raw for raw in parser.jsonld_raw)
        ok = (status == 200) and title_ok and jsonld_ok
        if not ok:
            errors += 1
        results.append({
            'url': url,
            'status': status,
            'title_found': title_clean,
            'title_expected_snippet': expected_norm[:60],
            'title_ok': title_ok,
            'jsonld_blocks': len(parser.jsonld_raw),
            'jsonld_article_present': jsonld_ok,
            'ok': ok
        })
    out_dir = 'reports/publish'
    os.makedirs(out_dir, exist_ok=True)
    with open(f'{out_dir}/verify.json','w',encoding='utf-8') as f:
        json.dump({'results':results,'errors':errors}, f, ensure_ascii=False, indent=2)
    lines = ["# Publicación — Verificación en Vivo","",f"Errores: {errors}",""]
    for r in results:
        lines.append(f"## {r['url']}")
        if 'error' in r:
            lines.append(f"- ERROR fetch: {r['error']}")
            continue
        lines.append(f"- HTTP: {r['status']}")
        lines.append(f"- Title OK: {r['title_ok']}")
        lines.append(f"- JSON-LD Article presente: {r['jsonld_article_present']}")
        lines.append(f"- Resultado: {'OK' if r['ok'] else 'FALLO'}")
        lines.append('')
    with open(f'{out_dir}/verify.md','w',encoding='utf-8') as f:
        f.write('\n'.join(lines)+"\n")
    if errors:
        print(f"FALLAN {errors} páginas publicadas")
        return 1
    print("Todas las páginas publicadas verificadas correctamente.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
