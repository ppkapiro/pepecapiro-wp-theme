#!/usr/bin/env python3
"""Genera un reporte unificado de los preflight gates.

Lee:
  preflight_links.json
  preflight_taxonomies.json
  preflight_content.json

Produce:
  preflight_report.json
  preflight_report.md

Reglas de estado:
  - Si cualquier status == FAILED => FAILED
  - Si ninguno FAILED y alguno UNKNOWN_* => UNKNOWN
  - Else => OK

No altera exit code (si se quiere fallar ya lo hizo cada gate individual).
"""
from __future__ import annotations
import json
import os
import time
from typing import Dict, Any, List

INPUT_FILES = [
    ('links', 'preflight_links.json'),
    ('taxonomies', 'preflight_taxonomies.json'),
    ('content', 'preflight_content.json'),
]
OUT_JSON = 'preflight_report.json'
OUT_MD = 'preflight_report.md'


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            return {'error': str(e)}


def compute_status(parts: List[Dict[str, Any]]) -> str:
    statuses = [p.get('status', '') for p in parts if p]
    if any(s == 'FAILED' for s in statuses):
        return 'FAILED'
    if any(s.startswith('UNKNOWN') for s in statuses):
        return 'UNKNOWN'
    return 'OK'


def build_markdown(aggregate: Dict[str, Any]) -> str:
    lines = []
    lines.append('# Preflight Quality Gates (Unificado)')
    lines.append('')
    lines.append(f"Estado global: **{aggregate['status']}**")
    lines.append('')
    lines.append('## Estados Individuales')
    lines.append('')
    for name, data in aggregate['gates'].items():
        if not data:
            lines.append(f"### {name}\n- (sin datos)")
            continue
        lines.append(f"### {name}")
        lines.append(f"- status: {data.get('status')}")
        if 'missing' in data and isinstance(data['missing'], dict):
            missing_total = sum(len(v) for v in data['missing'].values())
            lines.append(f"- missing: {missing_total}")
        if 'errors' in data and isinstance(data['errors'], list):
            lines.append(f"- errors: {len(data['errors'])}")
        lines.append('')
    lines.append(f"Generado: {aggregate['timestamp']}")
    return '\n'.join(lines)


def main():
    gates_data = {}
    parts = []
    for key, filename in INPUT_FILES:
        data = load_json(filename)
        gates_data[key] = data
        if data:
            parts.append(data)
    aggregate = {
        'status': compute_status(parts),
        'gates': gates_data,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(aggregate, f, ensure_ascii=False, indent=2)
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(build_markdown(aggregate))
    print(f"Reporte preflight unificado generado: {OUT_MD}")


if __name__ == '__main__':
    main()
