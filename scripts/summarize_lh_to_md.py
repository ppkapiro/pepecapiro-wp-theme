#!/usr/bin/env python3
import json
import os
import glob
from datetime import datetime

REPORT_DIR = os.path.join(os.getcwd(), 'lighthouse_reports')
DOC_PATH = os.path.join(os.getcwd(), 'docs', 'VALIDACION_MVP_v0_2_1.md')

# Map file base name to page path for the table
PAGE_MAP = {
  'home': '/',
  'en-home': '/en/',
  'sobre-mi': '/sobre-mi/',
  'en-about': '/en/about/',
  'proyectos': '/proyectos/',
  'en-projects': '/en/projects/',
  'recursos': '/recursos/',
  'en-resources': '/en/resources/',
  'contacto': '/contacto/',
  'en-contact': '/en/contact/',
}


def ms_to_pretty(ms):
    if ms is None:
        return 'n/a'
    # format in seconds with one decimal place if >= 1000ms, else ms
    if ms >= 1000:
        return f"{ms/1000:.1f}s"
    return f"{int(ms)}ms"


def extract_top_opportunities(audits: dict):
    # Collect audits with scoreDisplayMode == 'opportunity'
    opps = []
    for key, audit in audits.items():
        if isinstance(audit, dict) and audit.get('scoreDisplayMode') == 'opportunity':
            title = audit.get('title') or key
            # Use overall savings or weight as tie-breaker
            details = audit.get('details') or {}
            savings_ms = 0.0
            if isinstance(details, dict):
                savings_ms = float(details.get('overallSavingsMs') or 0.0)
            opps.append((savings_ms, title))
    opps.sort(reverse=True)
    tops = [title for _, title in opps[:2]]
    return ', '.join(tops) if tops else '—'


def parse_report(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    cats = data.get('categories', {}) or {}
    audits = data.get('audits', {}) or {}

    perf_score = cats.get('performance', {}).get('score')
    if isinstance(perf_score, (int, float)):
        perf = round(perf_score * 100)
    else:
        perf = 'n/a'

    lcp = audits.get('largest-contentful-paint', {}).get('numericValue')
    tti = audits.get('interactive', {}).get('numericValue')
    inp = audits.get('experimental-interaction-to-next-paint', {}).get('numericValue')

    top2 = extract_top_opportunities(audits)

    return perf, ms_to_pretty(lcp), ms_to_pretty(tti), ms_to_pretty(inp), top2


def build_table(rows):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = []
    lines.append(f"## Lighthouse móvil (métricas reales) — {ts}")
    lines.append("")
    lines.append("| Página | Perf | LCP | TTI | INP | Top 2 oportunidades |")
    lines.append("|--------|------|-----|-----|-----|----------------------|")
    for page, perf, lcp, tti, inp, top2 in rows:
        lines.append(f"| {page} | {perf} | {lcp} | {tti} | {inp} | {top2} |")
    lines.append("")
    return "\n".join(lines)


def main():
    json_files = sorted(glob.glob(os.path.join(REPORT_DIR, '*.json')))
    if not json_files:
        print('[warn] No JSON reports found in lighthouse_reports/')
        return 0

    # Build rows in the fixed order defined by PAGE_MAP
    rows = []
    name_to_metrics = {}
    for jf in json_files:
        name = os.path.splitext(os.path.basename(jf))[0]
        if name not in PAGE_MAP:
            continue
        perf, lcp, tti, inp, top2 = parse_report(jf)
        name_to_metrics[name] = (perf, lcp, tti, inp, top2)

    ordered_keys = [
        'home','en-home','sobre-mi','en-about','proyectos','en-projects',
        'recursos','en-resources','contacto','en-contact'
    ]
    for k in ordered_keys:
        page = PAGE_MAP[k]
        perf, lcp, tti, inp, top2 = name_to_metrics.get(k, ('n/a','n/a','n/a','n/a','—'))
        rows.append((page, perf, lcp, tti, inp, top2))

    table_md = build_table(rows)

    # Append or replace in doc: find section starting with '## Lighthouse móvil (métricas reales) —'
    if not os.path.isfile(DOC_PATH):
        print(f"[warn] Doc file not found: {DOC_PATH}")
        return 0

    with open(DOC_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strategy: replace the last '## Lighthouse móvil (métricas reales)' block with new one
    import re
    pattern = r"## Lighthouse móvil \(métricas reales\)[\s\S]*$"
    if re.search(pattern, content, flags=re.M):
        new_content = re.sub(pattern, table_md + "\n", content, flags=re.M)
    else:
        # If not found, append
        new_content = content.rstrip() + "\n\n" + table_md + "\n"

    with open(DOC_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('[ok] Markdown table updated in', DOC_PATH)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
