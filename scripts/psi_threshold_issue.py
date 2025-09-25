#!/usr/bin/env python3
"""Crea un issue en GitHub si el último run PSI viola thresholds.

Condiciones:
  - Lee reports/psi/index.json (primer elemento = run más reciente por orden descendente).
  - Abre el summary.json correspondiente y revisa evaluations.{mobile,desktop}.passes.
  - Si cualquiera es False, crea (o reutiliza) un issue etiquetado con 'performance' y título estándar.
  - Evita duplicados: busca issues abiertas con mismo título antes de crear.

Requisitos:
  - Variables de entorno GITHUB_REPOSITORY (owner/repo) y GITHUB_TOKEN (permiso repo scope).

No falla el pipeline si la creación de issue falla; sólo imprime advertencia.
"""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict

BASE_DIR = os.path.join('reports', 'psi')
INDEX_JSON = os.path.join(BASE_DIR, 'index.json')
USER_AGENT = 'psi-threshold-issue/1.0'
LABELS = ['performance', 'psi', 'automation']
ISSUE_TITLE = 'PSI Thresholds Fallidos en último run'
PRIORITY_LABEL = 'priority:high'


def load_latest_summary() -> Dict[str, Any]:
    if not os.path.exists(INDEX_JSON):
        return {}
    try:
        with open(INDEX_JSON, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except Exception:
        return {}
    if not entries:
        return {}
    # primer entry es más reciente
    entry = entries[0]
    rel = entry.get('summary_path')
    if not rel:
        return {}
    summary_path = os.path.join(BASE_DIR, rel)
    if not os.path.exists(summary_path):
        return {}
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
    except Exception:
        return {}
    return summary

def consecutive_failures(summary: Dict[str, Any]) -> int:
    """Cuenta fallos consecutivos recientes en timeseries.json (mobile performance mensurable vs threshold)."""
    index_path = os.path.join(BASE_DIR, 'index.json')
    if not os.path.exists(index_path):
        return 1 if should_create_issue(summary) else 0
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except Exception:
        return 1
    # contamos desde el más reciente mientras haya fallos (usa mobile_passes si está, si no evaluations)
    count = 0
    for e in entries:  # entries ya ordenadas desc
        sp = e.get('summary_path')
        if not sp:
            break
        path = os.path.join(BASE_DIR, sp)
        if not os.path.exists(path):
            break
        try:
            with open(path, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            break
        if should_create_issue(s):
            count += 1
        else:
            break
    return count


def should_create_issue(summary: Dict[str, Any]) -> bool:
    evals = summary.get('evaluations') or {}
    for side in ('mobile', 'desktop'):
        side_eval = evals.get(side) or {}
        if side_eval.get('passes') is False:
            return True
    return False


def github_api_request(method: str, url: str, token: str, data: Dict[str, Any] | None = None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': USER_AGENT,
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, method=method, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:  # nosec
        return json.loads(resp.read().decode('utf-8'))


def find_existing_issue(repo: str, token: str):
    q = urllib.parse.quote(f'repo:{repo} in:title is:open "{ISSUE_TITLE}"')
    url = f'https://api.github.com/search/issues?q={q}'
    try:
        result = github_api_request('GET', url, token)
        items = result.get('items') or []
        if items:
            return items[0]
    except Exception:
        return None
    return None


def create_issue(repo: str, token: str, summary: Dict[str, Any]):
    url = f'https://api.github.com/repos/{repo}/issues'
    evaluations = summary.get('evaluations', {})
    averages = summary.get('averages', {})
    lines = []
    lines.append('Se han detectado fallos en thresholds PSI (automático).')
    lines.append('')
    lines.append('## Evaluations')
    for side, data in evaluations.items():
        lines.append(f"### {side}")
        lines.append(f"passes: {data.get('passes')}")
        for chk in data.get('checks', []):
            parts = [chk.get('metric'), f"value={chk.get('value')}"]
            if 'min' in chk:
                parts.append(f"min={chk['min']}")
            if 'max' in chk:
                parts.append(f"max={chk['max']}")
            parts.append(f"pass={chk.get('pass')}")
            lines.append('- ' + ' '.join(parts))
        lines.append('')
    lines.append('## Promedios')
    for side, data in averages.items():
        lines.append(f"### {side}")
        for k,v in data.items():
            lines.append(f"- {k}: {v}")
    body = '\n'.join(lines)
    labels = list(LABELS)
    if consecutive_failures(summary) >= 2:
        labels.append(PRIORITY_LABEL)
    payload = {'title': ISSUE_TITLE, 'body': body, 'labels': labels}
    try:
        created = github_api_request('POST', url, token, payload)
        print(f"Issue creado: {created.get('html_url')}")
    except Exception as e:
        print(f"WARN: No se pudo crear issue: {e}")


def main():
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    if not repo or not token:
        print('GITHUB_REPOSITORY o GITHUB_TOKEN no definidos; saltando.')
        return
    summary = load_latest_summary()
    if not summary:
        print('No summary PSI disponible; saltando.')
        return
    if not should_create_issue(summary):
        print('Thresholds OK; no se crea issue.')
        return
    existing = find_existing_issue(repo, token)
    if existing:
        print(f"Issue existente encontrado: {existing.get('html_url')} (no se duplica)")
        return
    create_issue(repo, token, summary)


if __name__ == '__main__':
    main()
