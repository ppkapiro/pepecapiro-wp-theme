#!/usr/bin/env python3
import os
import json
import sys
import urllib.request
import urllib.error
from html.parser import HTMLParser

# Simple HTML head parser extracting link rel+hreflang, canonical, and JSON-LD scripts
class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.links = []
        self.jsonld = []
        self._capture_script = False
        self._script_type_jsonld = False
        self._script_buf = []

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        if tag == 'head':
            self.in_head = True
        if not self.in_head:
            return
        if tag == 'link':
            rel = at.get('rel')
            if rel:
                self.links.append(at)
        if tag == 'script':
            tp = at.get('type','')
            if tp.lower() == 'application/ld+json':
                self._capture_script = True
                self._script_type_jsonld = True
                self._script_buf = []

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        if tag == 'script' and self._capture_script:
            if self._script_type_jsonld:
                raw = ''.join(self._script_buf).strip()
                self.jsonld.append(raw)
            self._capture_script = False
            self._script_type_jsonld = False

    def handle_data(self, data):
        if self._capture_script and self._script_type_jsonld:
            self._script_buf.append(data)

# Utilities

def fetch(url, timeout=15):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode('utf-8','replace')
    except urllib.error.URLError as e:
        raise RuntimeError(f"fetch error {url}: {e}")

def load_config():
    cfg_path = os.path.join('configs','seo_audit.json')
    with open(cfg_path,'r',encoding='utf-8') as f:
        return json.load(f)

ARTICLE_TYPES = {"Article","NewsArticle","BlogPosting"}

# Detect JSON-LD types

def parse_jsonld_blocks(raw_blocks):
    objs = []
    for raw in raw_blocks:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                objs.extend(data)
            else:
                objs.append(data)
        except json.JSONDecodeError:
            pass
    return objs

# Evaluate a single URL

def evaluate_url(url, cfg):
    html = fetch(url)
    parser = HeadParser()
    parser.feed(html)
    issues = []

    # Canonical
    canon_links = [link for link in parser.links if link.get('rel') == 'canonical']
    if not canon_links:
        issues.append({'severity':'error','code':'canonical_missing','msg':'Falta <link rel="canonical">'})
    else:
        # Uniqueness
        if len(canon_links) > 1:
            issues.append({'severity':'warn','code':'canonical_multiple','msg':'Más de un canonical encontrado'})

    # hreflang
    expected_langs = cfg.get('languages',[])
    hreflang_links = [link for link in parser.links if link.get('rel') == 'alternate' and link.get('hreflang')]
    found_map = { link.get('hreflang'): link.get('href') for link in hreflang_links }
    for lang in expected_langs:
        if lang not in found_map:
            issues.append({'severity':'error','code':'hreflang_missing','lang':lang,'msg':f'Falta hreflang para {lang}'})
    if 'x-default' not in found_map:
        issues.append({'severity':'warn','code':'hreflang_xdefault_missing','msg':'Falta hreflang x-default'})

    # JSON-LD
    objs = parse_jsonld_blocks(parser.jsonld)
    types = set()
    breadcrumb_ok = False
    article_ok = False
    for o in objs:
        if isinstance(o, dict):
            t = o.get('@type')
            if isinstance(t, list):
                for i in t:
                    types.add(i)
            elif isinstance(t,str):
                types.add(t)
            if o.get('@type') == 'BreadcrumbList' and 'itemListElement' in o:
                breadcrumb_ok = True
            if t in ARTICLE_TYPES or (isinstance(t, list) and any(x in ARTICLE_TYPES for x in t)):
                article_ok = True
    if cfg.get('require_breadcrumb_jsonld') and not breadcrumb_ok:
        issues.append({'severity':'error','code':'breadcrumb_jsonld_missing','msg':'No se detectó BreadcrumbList JSON-LD'})
    if cfg.get('require_article_jsonld') and not article_ok:
        issues.append({'severity':'error','code':'article_jsonld_missing','msg':'No se detectó Article/BlogPosting JSON-LD'})

    return {
        'url': url,
        'canonical_present': bool(canon_links),
        'hreflang_count': len(hreflang_links),
        'jsonld_blocks': len(parser.jsonld),
        'breadcrumb_jsonld': breadcrumb_ok,
        'article_jsonld': article_ok,
        'issues': issues
    }

# Collect target URLs: for simplicity, use WP REST to list published posts for both languages
# Requires WORDPRESS_BASE_URL and authentication if not public; fallback to cfg base_url + /{lang}/

def discover_post_urls(cfg):
    base = cfg['base_url'].rstrip('/')
    urls = []
    # naive approach: query REST posts? We'll allow env var WP_API_BASE for direct root.
    api_base = os.environ.get('WP_API_BASE', base)
    # Try language subpaths
    for lang in cfg.get('languages', []):
        # REST locale param may vary; Polylang sets lang=es|en
        api_url = f"{api_base}/wp-json/wp/v2/posts?lang={lang}&status=publish&per_page=50"  # limit 50
        try:
            raw = fetch(api_url)
            data = json.loads(raw)
            for p in data:
                link = p.get('link')
                if link:
                    urls.append(link)
        except Exception as e:
            # fallback: skip language if API fails
            sys.stderr.write(f"[WARN] No se pudieron descubrir posts para {lang}: {e}\n")
    return urls

def main():
    cfg = load_config()
    urls = discover_post_urls(cfg)
    if not urls:
        print("No se descubrieron URLs de posts publicados. Nada que auditar.")
        return 0
    results = []
    errors = 0
    for u in urls:
        r = evaluate_url(u, cfg)
        for iss in r['issues']:
            if iss['severity'] == 'error':
                errors += 1
        results.append(r)
    out_dir = os.path.join('reports','seo')
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, 'audit.json')
    with open(out_json,'w',encoding='utf-8') as f:
        json.dump({'results':results}, f, ensure_ascii=False, indent=2)
    # Markdown summary
    lines = ["# SEO Head Audit","",f"Total URLs: {len(results)}",""]
    for r in results:
        lines.append(f"## {r['url']}")
        lines.append(f"- Canonical: {'OK' if r['canonical_present'] else 'FALTA'}")
        lines.append(f"- hreflang count: {r['hreflang_count']}")
        lines.append(f"- Breadcrumb JSON-LD: {'OK' if r['breadcrumb_jsonld'] else 'FALTA'}")
        lines.append(f"- Article JSON-LD: {'OK' if r['article_jsonld'] else 'FALTA'}")
        if r['issues']:
            lines.append('- Issues:')
            for iss in r['issues']:
                lines.append(f"  - [{iss['severity']}] {iss['code']} {iss.get('lang','')}")
        lines.append('')
    with open(os.path.join(out_dir,'audit.md'),'w',encoding='utf-8') as f:
        f.write('\n'.join(lines))
    # Exit non-zero if errors (allow gating later)
    if errors:
        print(f"Errores críticos SEO: {errors}")
        return 1
    print("SEO audit completada sin errores críticos.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
