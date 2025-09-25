#!/usr/bin/env python3
"""Analiza reutilización de media a partir de .media_map.json histórico.

Calcula:
  - total entradas en media_map
  - total hashes únicos (igual a len keys)
  - ratio reutilización estimado = (subidas evitadas) / (total referencias potenciales)
    Suponemos que cada hash apareció N veces y se subió 1: evitadas = sum(N-1)
  - genera detalle top 10 hashes por reuse.

Entrada: content/.media_map.json (si no existe, reporte vacío OK)
Salida: media_reuse_report.json, media_reuse_report.md
Exit code: 0 siempre.
"""
from __future__ import annotations
import json
import os
import time
from typing import Dict, Any

MEDIA_MAP_PATH = os.path.join('content', '.media_map.json')
OUT_JSON = 'media_reuse_report.json'
OUT_MD = 'media_reuse_report.md'


def load_media_map() -> Dict[str, Any]:
    if not os.path.exists(MEDIA_MAP_PATH):
        return {}
    with open(MEDIA_MAP_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}


def compute_stats(data: Dict[str, Any]):
    # data: hash -> { "url": str, "count": int? } (asumimos que publish_content.py puede extender count en futuro; si no existe count => 1)
    total_hashes = len(data)
    avoided = 0
    total_refs = 0
    rows = []
    for h, meta in data.items():
        count = 1
        if isinstance(meta, dict):
            c = meta.get('count')
            if isinstance(c, int) and c > 0:
                count = c
        total_refs += count
        if count > 1:
            avoided += (count - 1)
        rows.append({'hash': h, 'count': count, 'url': meta.get('url') if isinstance(meta, dict) else None})
    ratio = None
    if total_refs > 0:
        ratio = round(avoided / total_refs, 4)
    rows.sort(key=lambda x: x['count'], reverse=True)
    top10 = rows[:10]
    return {
        'total_hashes': total_hashes,
        'total_refs': total_refs,
        'avoided_uploads': avoided,
        'reuse_ratio': ratio,
        'top10': top10,
    }


def write_outputs(stats):
    result = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'stats': stats,
    }
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    lines = []
    lines.append('# Media Reuse Report')
    lines.append('')
    s = stats
    lines.append(f"Total hashes: {s['total_hashes']}")
    lines.append(f"Total referencias (estimadas): {s['total_refs']}")
    lines.append(f"Subidas evitadas: {s['avoided_uploads']}")
    lines.append(f"Ratio reutilización: {s['reuse_ratio']}")
    lines.append('')
    lines.append('## Top 10')
    for r in s['top10']:
        lines.append(f"- {r['hash']}: count={r['count']} url={r['url']}")
    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    data = load_media_map()
    stats = compute_stats(data)
    write_outputs(stats)
    print('Media reuse report generado.')


if __name__ == '__main__':
    main()
