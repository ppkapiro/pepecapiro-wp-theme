#!/usr/bin/env python3
"""Genera advertencia de performance si último PSI móvil < performance_min threshold.

Lee reports/psi/index.json -> summary más reciente -> evaluations.mobile.checks.
Imprime líneas con prefijo PERF_ADVISORY si falla.
Nunca falla (exit 0). Sirve para integrarse en content-sync plan/apply como contexto.
"""
from __future__ import annotations
import json
import os

BASE_DIR = os.path.join('reports', 'psi')
INDEX_JSON = os.path.join(BASE_DIR, 'index.json')


def load_latest_summary():
    if not os.path.exists(INDEX_JSON):
        return None
    try:
        with open(INDEX_JSON, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except Exception:
        return None
    if not entries:
        return None
    sp = entries[0].get('summary_path')
    if not sp:
        return None
    path = os.path.join(BASE_DIR, sp)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def main():
    summary = load_latest_summary()
    if not summary:
        print('PERF_ADVISORY: No summary PSI disponible aún.')
        return
    evals = summary.get('evaluations', {})
    mobile = evals.get('mobile') or {}
    if mobile.get('passes') is False:
        # extraer checks fallidos
        for chk in mobile.get('checks', []):
            if chk.get('pass') is False:
                print(f"PERF_ADVISORY: mobile {chk.get('metric')} value={chk.get('value')} threshold={'min=' + str(chk.get('min')) if 'min' in chk else 'max=' + str(chk.get('max'))}")
    else:
        print('PERF_ADVISORY: OK (mobile thresholds cumplidos)')


if __name__ == '__main__':
    main()
