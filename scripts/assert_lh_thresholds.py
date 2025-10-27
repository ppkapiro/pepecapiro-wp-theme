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
    psi = data.get('psi', {})
    mobile = psi.get('mobile', {
        'performance_min': 90,
        'lcp_max_ms': 2500,
        'cls_max': 0.1,
    })
    desktop = psi.get('desktop', {
        'performance_min': 95,
        'lcp_max_ms': 1800,
        'cls_max': 0.05,
    })
    return {'mobile': mobile, 'desktop': desktop}


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
    summary_lines = []
    thr_all = load_thresholds()
    m_thr = thr_all['mobile']
    d_thr = thr_all['desktop']
    m_perf_min = int(m_thr.get('performance_min', 90))
    m_lcp_max = float(m_thr.get('lcp_max_ms', 2500))
    m_cls_max = float(m_thr.get('cls_max', 0.1))
    d_perf_min = int(d_thr.get('performance_min', 95))
    d_lcp_max = float(d_thr.get('lcp_max_ms', 1800))
    d_cls_max = float(d_thr.get('cls_max', 0.05))

    json_files = { os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(REPORT_DIR, '*.json')) }
    if not json_files:
        msg = '[error] No se encontraron reportes JSON en lighthouse_reports/. ¿Se ejecutó Lighthouse?'
        print(msg, file=sys.stderr)
        summary_lines.append(msg)
        _write_summary(summary_lines)
        return 2

    failures = []
    checked_m = 0
    checked_d = 0

    for name in PAGES_ORDER:
        # Mobile
        jf_m = json_files.get(name)
        if not jf_m:
            warn = f"[warn] Falta reporte móvil: {name} ({NAME_TO_PATH.get(name, '')})"
            print(warn)
            summary_lines.append(warn)
        else:
            checked_m += 1
            try:
                perf, lcp, cls = parse_report(jf_m)
            except Exception as e:
                failures.append((name, f'mobile-parse-error: {e}'))
            else:
                issues = []
                if perf is None or perf < m_perf_min:
                    issues.append(f'mobile performance {perf} < {m_perf_min}')
                if lcp is None or lcp > m_lcp_max:
                    issues.append(f'mobile LCP {lcp}ms > {m_lcp_max}ms')
                if cls is None or cls > m_cls_max:
                    issues.append(f'mobile CLS {cls} > {m_cls_max}')
                if issues:
                    failures.append((name, '; '.join(issues)))

        # Desktop (sufijo -d)
        jf_d = json_files.get(f"{name}-d")
        if not jf_d:
            warn = f"[warn] Falta reporte desktop: {name}-d ({NAME_TO_PATH.get(name, '')})"
            print(warn)
            summary_lines.append(warn)
        else:
            checked_d += 1
            try:
                perf, lcp, cls = parse_report(jf_d)
            except Exception as e:
                failures.append((f"{name}-d", f'desktop-parse-error: {e}'))
            else:
                issues = []
                if perf is None or perf < d_perf_min:
                    issues.append(f'desktop performance {perf} < {d_perf_min}')
                if lcp is None or lcp > d_lcp_max:
                    issues.append(f'desktop LCP {lcp}ms > {d_lcp_max}ms')
                if cls is None or cls > d_cls_max:
                    issues.append(f'desktop CLS {cls} > {d_cls_max}')
                if issues:
                    failures.append((f"{name}-d", '; '.join(issues)))

    if checked_m == 0 and checked_d == 0:
        msg = '[error] No se pudo validar, no hay reportes coincidentes con PAGES_ORDER (ni móvil ni desktop).'
        print(msg, file=sys.stderr)
        summary_lines.append(msg)
        _write_summary(summary_lines)
        return 3

    if failures:
        print('=== Lighthouse assert: FALLA ===')
        summary_lines.append('=== Lighthouse assert: FALLA ===')
        for name, why in failures:
            line = f"- {name}: {why}"
            print(line)
            summary_lines.append(line)
        _write_summary(summary_lines)
        return 1

    ok_msg = '=== Lighthouse assert: OK ==='
    print(ok_msg)
    summary_lines.append(ok_msg)
    _write_summary(summary_lines)
    return 0


def _write_summary(lines):
    try:
        out_dir = os.path.join(os.getcwd(), 'lighthouse_reports')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, 'assert_summary.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    except Exception:
        pass


if __name__ == '__main__':
    raise SystemExit(main())
