#!/usr/bin/env python3
import os
import shutil
import glob
import re

ROOT = os.getcwd()
LHCI_DIR = os.path.join(ROOT, '.lighthouseci')
OUT_DIR = os.path.join(ROOT, 'lighthouse_reports')
DOCS_HTML = os.path.join(ROOT, 'docs', 'lighthouse')

# Mapeo URL → nombre base esperado por summarize_lh_to_md.py
NAME_MAP = {
    '/$': 'home',
    '/en/$': 'en-home',
    '/sobre-mi/$': 'sobre-mi',
    '/en/about/$': 'en-about',
    '/proyectos/$': 'proyectos',
    '/en/projects/$': 'en-projects',
    '/recursos/$': 'recursos',
    '/en/resources/$': 'en-resources',
    '/contacto/$': 'contacto',
    '/en/contact/$': 'en-contact',
}

def match_name_from_url(url: str) -> str:
    for pattern, name in NAME_MAP.items():
        if re.search(pattern, url):
            return name
    return None

def parse_url_from_filename(filename: str) -> str:
    # LHCI filesystem strategy produces files like lhr-<hash>.json and <hash>.html with URL inside JSON
    # We'll open JSON to get final URL
    return None

def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DOCS_HTML, exist_ok=True)

def extract_url_from_json(path: str) -> str:
    try:
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return (data.get('finalUrl') or data.get('requestedUrl') or '').strip()
    except Exception:
        return ''

def main():
    ensure_dirs()
    html_files = sorted(glob.glob(os.path.join(LHCI_DIR, '*.html')))

    # Normalize JSON names into lighthouse_reports/{name}.json
    for jf in sorted(glob.glob(os.path.join(LHCI_DIR, '*.json'))):
        url = extract_url_from_json(jf)
        name = match_name_from_url(url)
        if not name:
            # fallback by heuristics from filename
            base = os.path.basename(jf)
            # try to infer from common slugs in filename
            lower = base.lower()
            if 'about' in lower and '/en/' in url:
                name = 'en-about'
            elif 'about' in lower:
                name = 'sobre-mi'
            elif 'projects' in lower and '/en/' in url:
                name = 'en-projects'
            elif 'projects' in lower:
                name = 'proyectos'
            elif 'resources' in lower and '/en/' in url:
                name = 'en-resources'
            elif 'resources' in lower:
                name = 'recursos'
            elif 'contact' in lower and '/en/' in url:
                name = 'en-contact'
            elif 'contact' in lower:
                name = 'contacto'
            elif '/en/' in url:
                name = 'en-home'
            else:
                name = 'home'
        dest = os.path.join(OUT_DIR, f'{name}.json')
        shutil.copy2(jf, dest)

        # Try to find a matching HTML by shared hash in filename; otherwise fall back to first available
        base = os.path.basename(jf)
        m = re.search(r'([0-9a-fA-F]{16,})', base)
        html_src = ''
        if m:
            h = m.group(1)
            for hfile in html_files:
                if h in os.path.basename(hfile):
                    html_src = hfile
                    break
        if not html_src and html_files:
            html_src = html_files.pop(0)
        if html_src and os.path.exists(html_src):
            shutil.copy2(html_src, os.path.join(DOCS_HTML, f'{name}.html'))
    print('[ok] Normalization done: HTML in docs/lighthouse, JSON in lighthouse_reports')

if __name__ == '__main__':
    raise SystemExit(main())
