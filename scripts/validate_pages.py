#!/usr/bin/env python3
import json
import sys
import os
PATH='content/pages.json'
if not os.path.isfile(PATH):
    print('[I] pages.json no existe (opcional).')
    sys.exit(0)
with open(PATH,'r',encoding='utf-8') as f:
    data=json.load(f)
required={'translation_key','slug','title','excerpt'}
errs=0
for i,e in enumerate(data):
    miss=required-set(e.keys())
    if miss:
        print(f'[E] item {i} faltan claves: {miss}', file=sys.stderr)
        errs+=1
    slug_field=e.get('slug')
    if isinstance(slug_field, dict):
        if not slug_field.get('es') or not slug_field.get('en'):
            print(f'[E] item {i} slug dict incompleto', file=sys.stderr)
            errs += 1
    elif not isinstance(slug_field, str):
        print(f'[E] item {i} slug debe ser string o dict', file=sys.stderr)
        errs += 1
    for field in ('title','excerpt'):
        val=e.get(field)
        if not isinstance(val,dict):
            print(f'[E] item {i} {field} debe ser objeto con es/en', file=sys.stderr)
            errs += 1
            continue
        for lang in ('es','en'):
            if lang not in val:
                print(f'[E] item {i} {field} sin {lang}', file=sys.stderr)
                errs += 1
    # status / disabled opcionales
    st=e.get('status')
    if st is not None and not (isinstance(st,str) or isinstance(st,dict)):
        print(f'[E] item {i} status inválido', file=sys.stderr)
        errs += 1
    dis=e.get('disabled')
    if dis is not None and not (isinstance(dis,bool) or isinstance(dis,dict)):
        print(f'[E] item {i} disabled inválido', file=sys.stderr)
        errs += 1
if errs:
    print(f'[F] errores totales: {errs}', file=sys.stderr)
    sys.exit(3)
print(f'[OK] pages.json válido, entradas: {len(data)}')
