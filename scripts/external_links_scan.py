#!/usr/bin/env python3
import os
import re
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import concurrent.futures
from html.parser import HTMLParser

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            at = dict(attrs)
            href = at.get('href')
            if href:
                self.links.add(href.strip())

def fetch(url, timeout):
    req = urllib.request.Request(url, headers={'User-Agent':'LinkScanner/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8','replace')

def discover_site_urls(base_url, langs):
    # Simple: get recent posts via REST per language, plus home for each language
    urls = []
    api_base = base_url.rstrip('/')
    for lang in langs:
        home = f"{api_base}/{lang}/" if lang != 'es' else f"{api_base}/"
        urls.append(home)
        api = f"{api_base}/wp-json/wp/v2/posts?lang={lang}&status=publish&per_page=50"
        try:
            raw = fetch(api, 15)
            data = json.loads(raw)
            for p in data:
                link = p.get('link')
                if link:
                    urls.append(link)
        except Exception as e:
            sys.stderr.write(f"[WARN] No posts discovered for {lang}: {e}\n")
    return sorted(set(urls))

def should_ignore(href, ignore_patterns):
    for pat in ignore_patterns:
        if re.search(pat, href):
            return True
    return False

def classify_link(href, internal_domain):
    if href.startswith('#'):
        return 'fragment'
    if href.startswith('mailto:') or href.startswith('tel:'):
        return 'protocol'
    parsed = urllib.parse.urlparse(href)
    if not parsed.netloc:
        return 'internal'
    if internal_domain and internal_domain in parsed.netloc:
        return 'internal'
    return 'external'

def head_or_get(url, timeout):
    # Try HEAD then fallback to GET
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent':'LinkScanner/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except Exception:
        # fallback GET
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'LinkScanner/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            return 0  # network / timeout

def scan_page(url, cfg):
    start = time.time()
    try:
        html = fetch(url, cfg['timeout_seconds'])
    except Exception as e:
        return {'url':url,'error':str(e),'links':[],'duration_ms':int((time.time()-start)*1000)}
    parser = LinkExtractor()
    parser.feed(html)
    links = []
    for raw in parser.links:
        if should_ignore(raw, cfg['ignore_patterns']):
            continue
        kind = classify_link(raw, cfg['internal_domain'])
        if kind in ('fragment','protocol'):
            continue
        abs_url = raw
        if raw.startswith('/'):
            abs_url = cfg['base_url'].rstrip('/') + raw
        links.append({'raw':raw,'url':abs_url,'kind':kind})
    # Deduplicate by absolute url
    uniq = {}
    for link_item in links:
        uniq[link_item['url']] = link_item
    return {'url':url,'links':list(uniq.values()),'error':'','duration_ms':int((time.time()-start)*1000)}

def load_link_scan_cfg():
    path = os.path.join('configs','link_scan.json')
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

def main():
    seo_cfg_path = os.path.join('configs','seo_audit.json')
    with open(seo_cfg_path,'r',encoding='utf-8') as f:
        seo_cfg = json.load(f)
    link_cfg = load_link_scan_cfg()
    base_url = seo_cfg['base_url']
    link_cfg['base_url'] = base_url
    langs = seo_cfg.get('languages',['es'])
    target_pages = discover_site_urls(base_url, langs)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=link_cfg['concurrency']) as ex:
        fut_map = { ex.submit(scan_page, url, link_cfg): url for url in target_pages }
        for fut in concurrent.futures.as_completed(fut_map):
            results.append(fut.result())

    # Collect external links
    external_targets = {}
    for page in results:
        for lk in page['links']:
            if lk['kind'] == 'external':
                external_targets.setdefault(lk['url'], {'url':lk['url'],'pages':set()})['pages'].add(page['url'])
    # Fetch statuses
    external_list = list(external_targets.values())
    for item in external_list:
        status = head_or_get(item['url'], link_cfg['timeout_seconds'])
        item['status'] = status
        item['pages'] = sorted(item['pages'])

    # Metrics & thresholds
    broken = [e for e in external_list if e.get('status',0) >= 400 or e.get('status',0) == 0]
    failure_pct = (len(broken)/len(external_list)*100) if external_list else 0.0
    threshold = link_cfg['failure_threshold_percent']
    out_dir = os.path.join('reports','links')
    os.makedirs(out_dir, exist_ok=True)
    report = {
        'scanned_pages': len(results),
        'external_links': len(external_list),
        'broken_links': len(broken),
        'failure_pct': round(failure_pct,2),
        'threshold_pct': threshold,
        'failed': failure_pct > threshold,
        'broken_list': broken,
    }
    with open(os.path.join(out_dir,'scan.json'),'w',encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    # Markdown
    lines = ["# External Links Scan","",f"Pages scanned: {len(results)}",f"External links: {len(external_list)}",f"Broken: {len(broken)} ({failure_pct:.2f}% vs threshold {threshold}%)",""]
    if broken:
        lines.append("## Broken Links")
        for b in broken:
            lines.append(f"- {b['status']} {b['url']} — referenced by {len(b['pages'])} page(s)")
    with open(os.path.join(out_dir,'scan.md'),'w',encoding='utf-8') as f:
        f.write('\n'.join(lines)+"\n")
    if report['failed']:
        print(f"FAIL broken link ratio {failure_pct:.2f}% > {threshold}%")
        return 1
    print("OK external links health within threshold.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
