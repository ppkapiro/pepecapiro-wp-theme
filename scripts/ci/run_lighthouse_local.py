#!/usr/bin/env python3
"""Run Lighthouse locally for a list of URLs and save HTML reports.

Reads URLs from configs/lh_urls.txt.
Outputs to reports/lighthouse/<timestamp>/ as HTML files.
Requires: Node.js and Google Chrome. Uses `npx lighthouse`.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
URLS_FILE = REPO_ROOT / 'configs' / 'lh_urls.txt'
OUT_DIR = REPO_ROOT / 'reports' / 'lighthouse'


def slugify_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip('/').replace('/', '_') or 'home'
    lang = 'root'
    if '/en/' in parsed.path:
        lang = 'en'
    elif parsed.netloc.startswith('en.'):
        lang = 'en'
    elif parsed.netloc:
        lang = 'es'
    return f"{lang}_{path}"


def read_urls() -> list[str]:
    if not URLS_FILE.is_file():
        print(f"[fatal] No existe {URLS_FILE}")
        sys.exit(2)
    urls: list[str] = []
    for line in URLS_FILE.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if s and not s.startswith('#'):
            urls.append(s)
    return urls


def run_lighthouse(url: str, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    chrome_path = '/usr/bin/google-chrome'
    if not Path(chrome_path).exists():
        chrome_path = 'google-chrome'
    cmd = [
        'npx', '--yes', 'lighthouse', url,
        '--output=html', f'--output-path={out_path}',
        '--only-categories=performance,accessibility,best-practices,seo',
        '--emulated-form-factor=mobile',
        '--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage',
        f'--chrome-path={chrome_path}',
    ]
    print(f"[lh] {url}\n -> {out_path}")
    try:
        result = subprocess.run(cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        print('[fatal] npx no está disponible. Instala Node.js/npm.')
        return 127
    if result.returncode != 0:
        print(f"[warn] Lighthouse falló (code={result.returncode}) para {url}\n{result.stderr[-500:]}\n")
    else:
        print(f"[ok] Reporte generado: {out_path}")
    return result.returncode


def main() -> int:
    ts = time.strftime('%Y%m%d_%H%M%S')
    out_root = OUT_DIR / ts
    urls = read_urls()
    if not urls:
        print('[fatal] No hay URLs en configs/lh_urls.txt')
        return 2
    failures = 0
    for url in urls:
        slug = slugify_url(url)
        out_file = out_root / f"{slug}.html"
        code = run_lighthouse(url, out_file)
        if code != 0:
            failures += 1
    index = out_root / 'INDEX.txt'
    index.write_text('\n'.join(urls) + '\n', encoding='utf-8')
    print(f"[summary] Directorio: {out_root} | URLs: {len(urls)} | fallos: {failures}")
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
