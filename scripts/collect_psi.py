#!/usr/bin/env python3
"""Collect PageSpeed Insights metrics for a list of URLs (mobile + desktop).

Características:
  - Lee lista de URLs desde configs/lh_urls.txt (reusa misma lista Lighthouse).
  - Para cada URL hace request a PSI API en estrategias: mobile y desktop.
  - Extrae métricas clave: performance score, LCP, FCP, INP (si presente), TBT (aprox), CLS, FID (legacy si existe), Speed Index.
  - Reintentos con backoff exponencial simple.
  - Salida por ejecución: directorio reports/psi/YYYYMMDD/HHMMSS/ con JSON raw y summary.json + summary.md.
  - Mantiene/actualiza índice global en reports/psi/index.html y index.json (histórico). 
  - Exit code 0 siempre (no bloquea pipeline si la API falla parcialmente; marca fallos en summary).

Variables de entorno:
  PSI_API_KEY  (opcional; si vacío usa free quota sin key)

Uso:
  python scripts/collect_psi.py
"""
from __future__ import annotations
import os
import sys
import json
import time
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

URLS_FILE = os.path.join('configs', 'lh_urls.txt')
BASE_OUT_DIR = os.path.join('reports', 'psi')
THRESHOLDS_PATH = os.path.join('configs', 'perf_thresholds.json')
TIMESERIES_JSON = os.path.join(BASE_OUT_DIR, 'timeseries.json')
BADGE_JSON = os.path.join(BASE_OUT_DIR, 'badge_mobile_performance.json')
MAX_RETRIES = 3
INITIAL_BACKOFF = 2
PSI_ENDPOINT = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'

METRICS_MAP = {
    'lcp': ('largest-contentful-paint', 'lcp'),
    'fcp': ('first-contentful-paint', 'fcp'),
    'cls': ('cumulative-layout-shift', 'cls'),
    'fid': ('max-potential-fid', 'fid'),  # legacy approximation
    'inp': ('experimental-interaction-to-next-paint', 'inp'),
    'tbt': ('total-blocking-time', 'tbt'),
    'si': ('speed-index', 'si'),
}


def load_urls() -> List[str]:
    if not os.path.exists(URLS_FILE):
        print(f"ERROR: No existe {URLS_FILE}")
        return []
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def ensure_run_dir() -> str:
    now = time.gmtime()
    date_dir = time.strftime('%Y%m%d', now)
    time_dir = time.strftime('%H%M%S', now)
    path = os.path.join(BASE_OUT_DIR, date_dir, time_dir)
    os.makedirs(path, exist_ok=True)
    return path


def fetch_psi(url: str, strategy: str, api_key: Optional[str]) -> Dict[str, Any]:
    params = {'url': url, 'strategy': strategy}
    if api_key:
        params['key'] = api_key
    qs = urllib.parse.urlencode(params)
    full_url = f"{PSI_ENDPOINT}?{qs}"
    req = urllib.request.Request(full_url, headers={'User-Agent': 'psi-metrics/1.0'})
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:  # nosec
                data = resp.read().decode('utf-8')
                return json.loads(data)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt == MAX_RETRIES:
                return {'error': str(e), 'attempts': attempt}
            time.sleep(backoff)
            backoff *= 2
    return {'error': 'unknown'}


def extract_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    if 'error' in payload:
        return {'error': payload['error']}
    lh = payload.get('lighthouseResult', {})
    audits = lh.get('audits', {})
    categories = lh.get('categories', {})
    perf_score = None
    try:
        perf_score = categories['performance']['score'] * 100
    except Exception:
        perf_score = None
    out = {'performance': perf_score}
    for key, (audit_id, short) in METRICS_MAP.items():
        audit = audits.get(audit_id) or {}
        val = audit.get('numericValue')
        if isinstance(val, (int, float)):
            out[short] = val
    return out


def build_index_entry(run_ts: str, date_str: str, summary: Dict[str, Any]) -> Dict[str, Any]:
    # summary: { 'urls': [ {url, mobile:{}, desktop:{} } ], 'errors': int }
    return {
        'timestamp': run_ts,
        'date': date_str,
        'errors': summary.get('errors', 0),
        'total_urls': len(summary.get('urls', [])),
        'avg_performance_mobile': summary.get('averages', {}).get('mobile', {}).get('performance'),
        'avg_performance_desktop': summary.get('averages', {}).get('desktop', {}).get('performance'),
        'summary_path': summary.get('relative_path'),
    }


def update_global_index(run_dir: str, summary: Dict[str, Any]):
    index_json_path = os.path.join(BASE_OUT_DIR, 'index.json')
    index_html_path = os.path.join(BASE_OUT_DIR, 'index.html')
    date_part = os.path.basename(os.path.dirname(run_dir))  # YYYYMMDD
    time_part = os.path.basename(run_dir)  # HHMMSS
    run_ts = f"{date_part}T{time_part}Z"
    summary['relative_path'] = os.path.relpath(os.path.join(run_dir, 'summary.json'), BASE_OUT_DIR)

    entries = []
    if os.path.exists(index_json_path):
        try:
            with open(index_json_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except Exception:
            entries = []
    entry = build_index_entry(run_ts, date_part, summary)
    # Añadir passes (mobile/desktop) si evaluations presentes
    evals = summary.get('evaluations', {})
    for side in ('mobile', 'desktop'):
        side_eval = evals.get(side)
        if isinstance(side_eval, dict) and 'passes' in side_eval:
            entry[f'{side}_passes'] = side_eval['passes']
    entries.append(entry)
    # ordenar descendente por timestamp
    entries.sort(key=lambda x: x['timestamp'], reverse=True)
    with open(index_json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    # HTML simple
    lines = [
        '<html><head><meta charset="utf-8"><title>PSI Metrics Index</title>'
        '<style>body{font-family:system-ui,Arial;padding:1rem;}table{border-collapse:collapse;}td,th{border:1px solid #ccc;padding:4px 8px;text-align:left;}th{background:#f3f3f3;} .fail{color:#b00;font-weight:600}</style>'
        '</head><body>',
        '<h1>Histórico PSI</h1>',
        '<table><thead><tr><th>Run</th><th>Errors</th><th>URLs</th><th>Perf (Mob)</th><th>Perf (Desk)</th><th>Summary</th></tr></thead><tbody>'
    ]
    for e in entries:
        cls = ' class="fail"' if e['errors'] else ''
        lines.append(
            f"<tr{cls}><td>{e['timestamp']}</td><td>{e['errors']}</td><td>{e['total_urls']}</td><td>{e.get('avg_performance_mobile','')}</td><td>{e.get('avg_performance_desktop','')}</td><td><a href='{e['summary_path']}'>JSON</a></td></tr>"
        )
    lines.append('</tbody></table></body></html>')
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def compute_averages(url_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    def avg(side: str, metric: str):
        vals = [u[side].get(metric) for u in url_entries if side in u and metric in u[side] and isinstance(u[side][metric], (int, float))]
        if not vals:
            return None
        return round(sum(vals)/len(vals), 2)
    out = {'mobile': {}, 'desktop': {}}
    for side in ('mobile', 'desktop'):
        for m in ['performance', 'lcp', 'fcp', 'inp', 'tbt', 'cls', 'si']:
            out[side][m] = avg(side, m)
    return out


def build_markdown(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append('# PageSpeed Insights Metrics')
    lines.append('')
    lines.append(f"Estado: {summary['errors']} errores")
    lines.append('')
    av = summary.get('averages', {})
    if av:
        lines.append('## Promedios (Mobile)')
        for k,v in av.get('mobile', {}).items():
            lines.append(f"- {k}: {v}")
        lines.append('')
        lines.append('## Promedios (Desktop)')
        for k,v in av.get('desktop', {}).items():
            lines.append(f"- {k}: {v}")
    lines.append('')
    lines.append('## Detalle por URL')
    for u in summary.get('urls', []):
        lines.append('')
        lines.append(f"### {u['url']}")
        for side in ('mobile','desktop'):
            lines.append(f"#### {side}")
            side_data = u.get(side, {})
            if 'error' in side_data:
                lines.append(f"- error: {side_data['error']}")
                continue
            for mk, mv in side_data.items():
                lines.append(f"- {mk}: {mv}")
    lines.append('')
    lines.append(f"Generado: {summary['timestamp']}")
    return '\n'.join(lines)


def main():
    urls = load_urls()
    if not urls:
        print('No URLs para procesar PSI.')
        sys.exit(0)
    api_key = os.environ.get('PSI_API_KEY') or ''
    run_dir = ensure_run_dir()

    thresholds = {}
    if os.path.exists(THRESHOLDS_PATH):
        try:
            with open(THRESHOLDS_PATH, 'r', encoding='utf-8') as f:
                thresholds = json.load(f)
        except Exception as e:
            print(f"WARN: No se pudieron cargar thresholds: {e}")

    url_entries = []
    total_errors = 0
    for url in urls:
        entry = {'url': url}
        for strategy in ('mobile', 'desktop'):
            raw = fetch_psi(url, strategy, api_key)
            with open(os.path.join(run_dir, f"psi_{strategy}_" + hashlib.sha256(f"{url}|{strategy}".encode()).hexdigest()[:12] + '.json'), 'w', encoding='utf-8') as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
            metrics = extract_metrics(raw)
            if 'error' in metrics:
                total_errors += 1
            entry[strategy] = metrics
        url_entries.append(entry)

    averages = compute_averages(url_entries)
    evaluations = {}
    try:
        psi_th = thresholds.get('psi', {}) if isinstance(thresholds, dict) else {}
        for side in ('mobile', 'desktop'):
            side_eval = {'passes': True, 'checks': []}
            side_avg = averages.get(side, {})
            side_cfg = psi_th.get(side, {}) if isinstance(psi_th, dict) else {}
            perf_min = side_cfg.get('performance_min')
            if perf_min and side_avg.get('performance') is not None:
                ok = side_avg['performance'] >= perf_min
                side_eval['checks'].append({'metric': 'performance', 'value': side_avg['performance'], 'min': perf_min, 'pass': ok})
                if not ok:
                    side_eval['passes'] = False
            lcp_max = side_cfg.get('lcp_max_ms')
            if lcp_max and side_avg.get('lcp') is not None:
                ok = side_avg['lcp'] <= lcp_max
                side_eval['checks'].append({'metric': 'lcp', 'value': side_avg['lcp'], 'max': lcp_max, 'pass': ok})
                if not ok:
                    side_eval['passes'] = False
            cls_max = side_cfg.get('cls_max')
            if cls_max and side_avg.get('cls') is not None:
                ok = side_avg['cls'] <= cls_max
                side_eval['checks'].append({'metric': 'cls', 'value': side_avg['cls'], 'max': cls_max, 'pass': ok})
                if not ok:
                    side_eval['passes'] = False
            evaluations[side] = side_eval
    except Exception as e:
        print(f"WARN: Error evaluando thresholds: {e}")
        evaluations = {}
    summary = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'urls': url_entries,
        'errors': total_errors,
        'averages': averages,
        'thresholds': thresholds.get('psi', {}) if isinstance(thresholds, dict) else {},
        'evaluations': evaluations,
    }
    with open(os.path.join(run_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    md = build_markdown(summary)
    with open(os.path.join(run_dir, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write(md)

    update_global_index(run_dir, summary)

    # Actualizar timeseries
    try:
        ts = []
        if os.path.exists(TIMESERIES_JSON):
            with open(TIMESERIES_JSON, 'r', encoding='utf-8') as f:
                ts = json.load(f)
        ts_entry = {
            'timestamp': summary['timestamp'],
            'avg_mobile_performance': averages.get('mobile', {}).get('performance'),
            'avg_desktop_performance': averages.get('desktop', {}).get('performance'),
            'errors': total_errors
        }
        ts.append(ts_entry)
        # cap últimas 500 entradas para mantener tamaño
        if len(ts) > 500:
            ts = ts[-500:]
        with open(TIMESERIES_JSON, 'w', encoding='utf-8') as f:
            json.dump(ts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"WARN: No se pudo actualizar timeseries: {e}")

    # Badge (simple JSON consumible por shields.io endpoint estático)
    try:
        mobile_perf = averages.get('mobile', {}).get('performance')
        color = 'lightgrey'
        if isinstance(mobile_perf, (int, float)):
            if mobile_perf >= 95:
                color = 'brightgreen'
            elif mobile_perf >= 90:
                color = 'green'
            elif mobile_perf >= 80:
                color = 'yellow'
            elif mobile_perf >= 70:
                color = 'orange'
            else:
                color = 'red'
        badge = {
            'schemaVersion': 1,
            'label': 'PSI Mobile Perf',
            'message': f"{mobile_perf}" if mobile_perf is not None else 'n/a',
            'color': color
        }
        with open(BADGE_JSON, 'w', encoding='utf-8') as f:
            json.dump(badge, f, ensure_ascii=False)
    except Exception as e:
        print(f"WARN: No se pudo generar badge: {e}")
    print(f"PSI metrics recopiladas en {run_dir}")
    # Exit 0 siempre para no romper pipeline por cuotas
    sys.exit(0)


if __name__ == '__main__':
    main()
