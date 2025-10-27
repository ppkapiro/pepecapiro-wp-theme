#!/usr/bin/env python3
import os
import json
import glob
import sys

THRESHOLDS_FILE = os.path.join(os.getcwd(), 'configs', 'perf_thresholds.json')
REPORT_DIR = os.path.join(os.getcwd(), 'lighthouse_reports')

PAGES_ORDER = [
  'home','en-home','sobre-mi','en-about','proyectos','en-projects',
  'recursos','en-resources','contacto','en-contact'
]

NAME_TO_PATH = {
  'home': '/',
  'en-home': '/en/',
  'sobre-mi': '/sobre-mi/',
  'en-about': '/en/about/',
  'proyectos': '/proyectos/',
  'en-projects': '/en/projects/',
  'recursos': '/recursos/',
  'en-resources': '/en/resources/',
  'contacto': '/contacto/',
  'en-contact': '/en/contact/'
}


def load_thresholds():
    with open(THRESHOLDS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Only mobile thresholds for now
    return data.get('psi', {}).get('mobile', {
        'performance_min': 90,
        'lcp_max_ms': 2500,
        'cls_max': 0.1,
    })


def parse_report(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    root = data.get('lighthouseResult') if 'lighthouseResult' in data else data
    if not isinstance(root, dict):
        raise ValueError('Unknown LH JSON format')
    cats = root.get('categories', {}) or {}
    audits = root.get('audits', {}) or {}

    perf_score = cats.get('performance', {}).get('score')
    perf = round(perf_score * 100) if isinstance(perf_score, (int, float)) else None

    lcp = audits.get('largest-contentful-paint', {}).get('numericValue')
    cls = audits.get('cumulative-layout-shift', {}).get('numericValue')
    return perf, lcp, cls


def main():
    thr = load_thresholds()
    perf_min = int(thr.get('performance_min', 90))
    lcp_max = float(thr.get('lcp_max_ms', 2500))
    cls_max = float(thr.get('cls_max', 0.1))

    json_files = { os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(REPORT_DIR, '*.json')) }
    if not json_files:
        print('[error] No se encontraron reportes JSON en lighthouse_reports/. ¿Se ejecutó Lighthouse?', file=sys.stderr)
        return 2

    failures = []
    checked = 0

    for name in PAGES_ORDER:
        jf = json_files.get(name)
        if not jf:
            # Solo avisar, no fallar por ausencia de alguna página
            print(f"[warn] Falta reporte: {name} ({NAME_TO_PATH.get(name, '')})")
            continue
        checked += 1
        try:
            perf, lcp, cls = parse_report(jf)
        except Exception as e:
            failures.append((name, f'parse-error: {e}'))
            continue
        issues = []
        if perf is None or perf < perf_min:
            issues.append(f'performance {perf} < {perf_min}')
        if lcp is None or lcp > lcp_max:
            issues.append(f'LCP {lcp}ms > {lcp_max}ms')
        if cls is None or cls > cls_max:
            issues.append(f'CLS {cls} > {cls_max}')
        if issues:
            failures.append((name, '; '.join(issues)))

    if checked == 0:
        print('[error] No se pudo validar, no hay reportes coincidentes con PAGES_ORDER.', file=sys.stderr)
        return 3

    if failures:
        print('=== Lighthouse assert: FALLA ===')
        for name, why in failures:
            print(f"- {name}: {why}")
        return 1

    print('=== Lighthouse assert: OK ===')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
