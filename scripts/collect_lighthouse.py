#!/usr/bin/env python3
import subprocess
import json
import sys
import datetime
import re
from pathlib import Path

"""
Ejecuta Lighthouse CLI sobre una lista de URLs y genera reportes HTML/JSON + summary.
Requisitos:
  - Node + lighthouse global (`npm i -g lighthouse`) en el entorno.
  - Archivo configs/lh_urls.txt
Salidas:
  docs/lighthouse/<YYYY-MM-DD>/ <slug>.report.(html|json)
  docs/lighthouse/<YYYY-MM-DD>/summary.json
  docs/lighthouse/<YYYY-MM-DD>/summary.md
  (Opcional) Actualiza docs/lighthouse/index.html (tabla acumulada simple)
"""

ROOT = Path(__file__).parent.parent
URL_FILE = ROOT / 'configs' / 'lh_urls.txt'
OUT_ROOT = ROOT / 'docs' / 'lighthouse'
DATE = datetime.date.today().isoformat()
RUN_DIR = OUT_ROOT / DATE
RUN_DIR.mkdir(parents=True, exist_ok=True)

if not URL_FILE.exists():
    print(f"ERROR: No existe {URL_FILE}", file=sys.stderr)
    sys.exit(1)

urls = [u.strip() for u in URL_FILE.read_text().splitlines() if u.strip() and not u.startswith('#')]
if not urls:
    print("ERROR: Lista de URLs vacía", file=sys.stderr)
    sys.exit(1)

# Normalizador a slug de archivo
SAFE_RE = re.compile(r'[^a-z0-9]+')

def slugify(url: str) -> str:
    path = url.replace('https://', '').replace('http://', '')
    path = path.strip('/').lower() or 'home'
    return SAFE_RE.sub('-', path).strip('-') or 'home'

results = []

for url in urls:
    slug = slugify(url)
    html_out = RUN_DIR / f"{slug}.report.html"
    json_out = RUN_DIR / f"{slug}.report.json"
    cmd = [
        'lighthouse', url,
        '--preset=mobile',
        '--output=json',
        '--output=html',
        f'--output-path={json_out}',
        '--quiet', '--chrome-flags=--headless=new --no-sandbox'
    ]
    print(f"[LH] {url} -> {slug}")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"WARN: Lighthouse falló para {url}: {e}")
        continue
    # Mover HTML (lighthouse genera .report.html junto al json)
    gen_html = json_out.with_suffix('.report.html')
    if gen_html.exists():
        gen_html.rename(html_out)
    # Parsear JSON
    try:
        data = json.loads(json_out.read_text())
        cat = data.get('categories', {})
        perf = cat.get('performance', {}).get('score')
        audits = data.get('audits', {})
        lcp = audits.get('largest-contentful-paint', {}).get('numericValue')
        tti = audits.get('interactive', {}).get('numericValue')
        inp = audits.get('experimental-interaction-to-next-paint', {}).get('numericValue')
        def ms(v):
            if v is None:
                return None
            return round(v)
        results.append({
            'url': url,
            'slug': slug,
            'performance': perf * 100 if isinstance(perf, (int,float)) else None,
            'lcp_ms': ms(lcp),
            'tti_ms': ms(tti),
            'inp_ms': ms(inp)
        })
    except Exception as ex:
        print(f"WARN: No se pudo parsear JSON para {url}: {ex}")

# Guardar summary
summary_path = RUN_DIR / 'summary.json'
summary_path.write_text(json.dumps({'date': DATE, 'results': results}, indent=2))

# Summary Markdown
md = ["# Lighthouse Summary", f"Fecha: {DATE}", '', '| URL | Perf | LCP (ms) | TTI (ms) | INP (ms) |', '|------|------|---------|----------|---------|']
for r in results:
    md.append(f"| {r['url']} | {r['performance'] or ''} | {r['lcp_ms'] or ''} | {r['tti_ms'] or ''} | {r['inp_ms'] or ''} |")
(RUN_DIR / 'summary.md').write_text('\n'.join(md) + '\n')

# Actualizar índice simple
index_file = OUT_ROOT / 'index.html'
rows = []
# Cargar runs previos (buscamos summary.json en subdirs)
for d in sorted([p for p in OUT_ROOT.iterdir() if p.is_dir()]):
    s = d / 'summary.json'
    if s.exists():
        try:
            payload = json.loads(s.read_text())
            date = payload.get('date', d.name)
            for r in payload.get('results', []):
                rows.append((date, r['url'], r.get('performance'), r.get('lcp_ms')))
        except Exception:
            pass

table_rows = '\n'.join(f"<tr><td>{date}</td><td>{url}</td><td>{perf or ''}</td><td>{lcp or ''}</td></tr>" for date,url,perf,lcp in rows)
index_html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Lighthouse Runs</title><style>body{{font-family:Arial, sans-serif;font-size:14px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 8px}}th{{background:#f5f5f5}}</style></head><body><h1>Lighthouse Runs</h1><table><thead><tr><th>Fecha</th><th>URL</th><th>Perf</th><th>LCP (ms)</th></tr></thead><tbody>{table_rows}</tbody></table></body></html>"""
index_file.write_text(index_html)

print(f"OK: {len(results)} resultados. Directorio: {RUN_DIR}")
