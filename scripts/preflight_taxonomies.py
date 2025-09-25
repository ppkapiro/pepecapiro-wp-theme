#!/usr/bin/env python3
"""Preflight Taxonomies

Objetivo:
  - Verificar que todas las taxonomías/categorías declaradas en content/posts.json (y potencialmente content/pages.json si en el futuro requieren) existen en el WordPress remoto.
  - Si no se puede contactar el sitio (offline), se produce un WARNING pero no se falla duro salvo que se especifique --strict-offline.
  - Salida:
      preflight_taxonomies.json
      preflight_taxonomies.md
  - Exit codes:
      0 = OK (o únicamente warnings)
      2 = FAILED (categorías faltantes confirmadas contra el sitio)

Estrategia:
  1. Recolectar categorías declaradas (es/en) en posts.json.
  2. Consultar endpoint REST /wp-json/wp/v2/categories?per_page=100&_fields=id,name,slug
     (Se asume que cubre todas las necesarias; si hay más de 100 habría que paginar).
  3. Construir mapa slug->name (case-sensitive normalizado) y validar presencia de cada categoría en ambos idiomas.
  4. Reportar métricas: total declaradas, únicas, faltantes.
  5. Generar markdown amigable.

Uso:
  python scripts/preflight_taxonomies.py --site-url https://example.com [--strict-offline]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from typing import List, Dict, Any, Set
import urllib.request
import urllib.error

CONTENT_POSTS_PATH = os.path.join('content', 'posts.json')
OUTPUT_JSON = 'preflight_taxonomies.json'
OUTPUT_MD = 'preflight_taxonomies.md'
DEFAULT_TIMEOUT = 15


def load_posts() -> List[Dict[str, Any]]:
    if not os.path.exists(CONTENT_POSTS_PATH):
        return []
    with open(CONTENT_POSTS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_declared_categories(posts: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
    declared = {'es': set(), 'en': set()}
    for p in posts:
        cat = p.get('category') or {}
        if isinstance(cat, dict):
            for lang in ('es', 'en'):
                val = cat.get(lang)
                if isinstance(val, str) and val.strip():
                    declared[lang].add(val.strip())
    return declared


def fetch_remote_categories(site_url: str, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, Any]]:
    url = site_url.rstrip('/') + '/wp-json/wp/v2/categories?per_page=100&_fields=id,name,slug'
    req = urllib.request.Request(url, headers={'User-Agent': 'preflight-taxonomies/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310 (controlado)
        data = resp.read().decode('utf-8')
        return json.loads(data)


def build_slug_name_map(categories: List[Dict[str, Any]]) -> Dict[str, str]:
    mapping = {}
    for c in categories:
        slug = c.get('slug')
        name = c.get('name')
        if isinstance(slug, str) and isinstance(name, str):
            mapping[slug.lower()] = name
            mapping[name.lower()] = name  # permitir coincidencia por nombre
    return mapping


def evaluate(declared: Dict[str, Set[str]], slugmap: Dict[str, str]) -> Dict[str, Any]:
    missing = {lang: [] for lang in declared}
    for lang, cats in declared.items():
        for cat in sorted(cats):
            key = cat.lower()
            if key not in slugmap:
                missing[lang].append(cat)
    status = 'OK'
    if any(missing[lang] for lang in missing):
        status = 'FAILED'
    return {
        'status': status,
        'declared': {k: sorted(list(v)) for k, v in declared.items()},
        'declared_unique_total': len(set().union(*declared.values())),
        'missing': missing,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }


def write_outputs(result: Dict[str, Any]):
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append('# Preflight Taxonomías / Categorías')
    lines.append('')
    lines.append(f"Estado: **{result['status']}**")
    lines.append('')
    lines.append(f"Total categorías declaradas únicas: {result['declared_unique_total']}")
    lines.append('')
    lines.append('## Declaradas')
    lines.append('')
    lines.append('### ES')
    lines.append('')
    for c in result['declared']['es']:
        lines.append(f'- {c}')
    lines.append('')
    lines.append('### EN')
    lines.append('')
    for c in result['declared']['en']:
        lines.append(f'- {c}')
    lines.append('')
    lines.append('## Faltantes')
    lines.append('')
    lines.append('### ES')
    lines.append('')
    if result['missing']['es']:
        for c in result['missing']['es']:
            lines.append(f'- {c}')
    else:
        lines.append('(ninguna)')
    lines.append('')
    lines.append('### EN')
    lines.append('')
    if result['missing']['en']:
        for c in result['missing']['en']:
            lines.append(f'- {c}')
    else:
        lines.append('(none)')
    lines.append('')
    lines.append(f"Generado: {result['timestamp']}")
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description='Preflight de taxonomías/categorías declaradas vs sitio WP.')
    parser.add_argument('--site-url', required=True, help='URL base del sitio WordPress (https://...)')
    parser.add_argument('--strict-offline', action='store_true', help='Fallar si no se puede consultar el sitio (por defecto solo warning).')
    args = parser.parse_args()

    posts = load_posts()
    declared = collect_declared_categories(posts)

    offline_error = None
    remote_categories = []
    if not posts:
        print('WARN: No se encontró content/posts.json o está vacío; no hay categorías declaradas.')

    try:
        remote_categories = fetch_remote_categories(args.site_url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        offline_error = str(e)

    if offline_error:
        print(f"WARN: No se pudo obtener categorías remotas: {offline_error}")
        if args.strict_offline:
            # Generar salida mínima y fallar.
            result = {
                'status': 'FAILED',
                'reason': 'offline',
                'error': offline_error,
                'declared': {k: sorted(list(v)) for k, v in declared.items()},
                'missing': declared,  # desconocido realmente
                'declared_unique_total': len(set().union(*declared.values())),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
            write_outputs(result)
            print('ERROR: strict-offline activado y no se pudo contactar el sitio.')
            sys.exit(2)
        else:
            # Modo tolerante: status queda UNKNOWN
            result = {
                'status': 'UNKNOWN_OFFLINE',
                'declared': {k: sorted(list(v)) for k, v in declared.items()},
                'missing': {k: [] for k in declared},  # no podemos confirmar
                'declared_unique_total': len(set().union(*declared.values())),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            }
            write_outputs(result)
            sys.exit(0)

    slugmap = build_slug_name_map(remote_categories)
    result = evaluate(declared, slugmap)
    write_outputs(result)

    if result['status'] == 'FAILED':
        print('ERROR: Categorías faltantes detectadas.')
        sys.exit(2)
    else:
        print('OK: Taxonomías validadas.')
        sys.exit(0)


if __name__ == '__main__':
    main()
