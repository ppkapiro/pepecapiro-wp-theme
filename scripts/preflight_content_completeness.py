#!/usr/bin/env python3
"""Preflight Content Completeness

Valida que los objetos en content/posts.json y content/pages.json cumplan requisitos mínimos
antes de intentar publicarlos.

Checks principales:
  - Campos obligatorios: translation_key, slug (es/en o string), title.es, title.en
  - (Opcional futuro) excerpt.* si presente debe ser string
  - Estado: si status.* = 'draft' se permite; si falta status se asume 'publish' (no falla)
  - Flag disabled: si disabled=true se omite del conteo de pendientes
  - Longitud mínima título (>= 3 chars)
  - Unicidad de translation_key entre posts+pages
  - Slug único por idioma (posts + pages combinados)

Salida:
  preflight_content.json
  preflight_content.md

Exit codes:
  0 = OK (o solo warnings)
  2 = FAILED (errores de completitud)
"""
from __future__ import annotations
import json
import os
import sys
import time
from typing import Any, Dict, List

POSTS_PATH = os.path.join('content', 'posts.json')
PAGES_PATH = os.path.join('content', 'pages.json')
OUTPUT_JSON = 'preflight_content.json'
OUTPUT_MD = 'preflight_content.md'

REQUIRED_TITLE_LANGS = ('es', 'en')


def load_json(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_slug(value):
    if isinstance(value, str):
        return {'es': value, 'en': value}
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if isinstance(v, str)}
    return {}


def validate_items(kind: str, items: List[Dict[str, Any]], acc):
    for obj in items:
        translation_key = obj.get('translation_key')
        disabled = obj.get('disabled', False)
        if disabled:
            acc['stats']['disabled'] += 1
        if not isinstance(translation_key, str) or not translation_key.strip():
            acc['errors'].append({'type': 'missing_translation_key', 'kind': kind, 'obj': obj})
            continue
        if translation_key in acc['translation_keys']:
            acc['errors'].append({'type': 'duplicate_translation_key', 'key': translation_key, 'kind': kind})
        else:
            acc['translation_keys'].add(translation_key)

        slug_norm = normalize_slug(obj.get('slug'))
        if not slug_norm:
            acc['errors'].append({'type': 'missing_slug', 'key': translation_key, 'kind': kind})
        else:
            for lang, slug_val in slug_norm.items():
                if not slug_val or len(slug_val) < 2:
                    acc['errors'].append({'type': 'invalid_slug', 'lang': lang, 'slug': slug_val, 'key': translation_key})
                slug_key = f"{lang}:{slug_val}"
                if slug_key in acc['slugs']:
                    acc['errors'].append({'type': 'duplicate_slug', 'slug': slug_val, 'lang': lang, 'key': translation_key})
                else:
                    acc['slugs'].add(slug_key)

        title = obj.get('title')
        if not isinstance(title, dict):
            acc['errors'].append({'type': 'missing_title', 'key': translation_key})
        else:
            for lang in REQUIRED_TITLE_LANGS:
                t = title.get(lang)
                if not isinstance(t, str) or len(t.strip()) < 3:
                    acc['errors'].append({'type': 'invalid_title', 'lang': lang, 'key': translation_key})

        # Stats
        if not disabled:
            acc['stats']['enabled'] += 1


def build_markdown(result: Dict[str, Any]) -> str:
    lines = []
    lines.append('# Preflight Completitud de Contenido')
    lines.append('')
    lines.append(f"Estado: **{result['status']}**")
    lines.append('')
    stats = result['stats']
    lines.append('## Estadísticas')
    lines.append('')
    lines.append(f"Items habilitados: {stats['enabled']}")
    lines.append(f"Items deshabilitados: {stats['disabled']}")
    lines.append(f"translation_keys únicas: {stats['translation_keys_total']}")
    lines.append(f"slugs únicos: {stats['slugs_total']}")
    lines.append('')

    if result['errors']:
        lines.append('## Errores')
        lines.append('')
        for e in result['errors']:
            lines.append(f"- {e['type']}: {json.dumps(e, ensure_ascii=False)}")
    else:
        lines.append('Sin errores de completitud.')

    lines.append('')
    lines.append(f"Generado: {result['timestamp']}")
    return '\n'.join(lines)


def main():
    posts = load_json(POSTS_PATH)
    pages = load_json(PAGES_PATH)

    acc = {
        'translation_keys': set(),  # type: Set[str]
        'slugs': set(),  # type: Set[str]
        'errors': [],
        'stats': {
            'enabled': 0,
            'disabled': 0,
            'translation_keys_total': 0,
            'slugs_total': 0,
        }
    }

    validate_items('post', posts, acc)
    validate_items('page', pages, acc)

    acc['stats']['translation_keys_total'] = len(acc['translation_keys'])
    acc['stats']['slugs_total'] = len(acc['slugs'])

    status = 'OK'
    if acc['errors']:
        status = 'FAILED'

    result = {
        'status': status,
        'errors': acc['errors'],
        'stats': acc['stats'],
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    md = build_markdown(result)
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)

    if status == 'FAILED':
        print('ERROR: Completitud de contenido fallida.')
        sys.exit(2)
    else:
        print('OK: Completitud válida.')
        sys.exit(0)


if __name__ == '__main__':
    main()
