#!/usr/bin/env python3
import re
import sys
import json
import urllib.parse
from pathlib import Path
import urllib.request

ROOT = Path(__file__).parent.parent
REPORT_JSON = ROOT / 'content' / 'preflight_links.json'
TIMEOUT = 10

# Collect candidate URLs from content markdown and config JSON files (simple heuristic)
content_dir = ROOT / 'content'
markdown_files = list(content_dir.glob('*.md'))
json_files = [content_dir / 'posts.json', content_dir / 'pages.json']

def extract_links(text: str):
    # Basic markdown link and raw URL detection
    md_link = re.findall(r'\[[^\]]+\]\((https?://[^)]+)\)', text)
    raw = re.findall(r'(https?://[\w./-]+)', text)
    return set(md_link + raw)

internal = set()
external = set()

site_domains = ['pepecapiro.com', 'www.pepecapiro.com']

for mf in markdown_files:
    txt = mf.read_text(encoding='utf-8', errors='ignore')
    for url in extract_links(txt):
        host = urllib.parse.urlparse(url).netloc.lower()
        if any(d == host or host.endswith(d) for d in site_domains):
            internal.add(url)
        else:
            external.add(url)

# Always include main canonical pages
seed = [
    'https://pepecapiro.com/',
    'https://pepecapiro.com/en/',
]
internal.update(seed)

results = []
fail = False

def head_or_get(url: str):
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status
    except Exception:
        # fallback GET
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT) as r2:
                return r2.status
        except Exception:
            return None

for url in sorted(internal):
    code = head_or_get(url)
    ok = code is not None and 200 <= code < 400
    if not ok:
        fail = True
    results.append({'url': url, 'status': code, 'ok': ok})

REPORT_JSON.write_text(json.dumps({'internal': results}, indent=2))

# Markdown summary
lines = ["# Preflight Links", '', '| URL | Status | OK |', '|-----|--------|----|']
for r in results:
    lines.append(f"| {r['url']} | {r['status']} | {'YES' if r['ok'] else 'NO'} |")
md_path = ROOT / 'content' / 'preflight_links.md'
md_path.write_text('\n'.join(lines) + '\n')

if fail:
    print("Preflight links: FAIL", file=sys.stderr)
    sys.exit(2)
print("Preflight links: OK")
