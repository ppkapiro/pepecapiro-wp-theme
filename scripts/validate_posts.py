#!/usr/bin/env python3
import json
import sys
import os
PATH='content/posts.json'
if not os.path.isfile(PATH):
    print(f'[E] Falta {PATH}', file=sys.stderr)
    sys.exit(2)
with open(PATH,'r',encoding='utf-8') as f:
    data=json.load(f)
required={'translation_key','slug','title','excerpt','category'}
errs=0
for i,e in enumerate(data):
    miss=required-set(e.keys())
    if miss:
        print(f'[E] item {i} faltan claves: {miss}', file=sys.stderr)
        errs+=1
    # slug: string o dict con es/en
    slug_field=e.get('slug')
    if isinstance(slug_field, dict):
        if not slug_field.get('es') or not slug_field.get('en'):
            print(f"[E] item {i} slug dict debe tener es y en", file=sys.stderr)
            errs += 1
    elif not isinstance(slug_field, str):
        print(f"[E] item {i} slug debe ser string o dict", file=sys.stderr)
        errs += 1
    for field in ('title','excerpt','category'):
        val=e.get(field)
        if not isinstance(val,dict):
            print(f'[E] item {i} {field} debe ser objeto con es/en', file=sys.stderr)
            errs+=1
            continue
        for lang in ('es','en'):
            if lang not in val:
                print(f'[E] item {i} {field} sin {lang}', file=sys.stderr)
                errs+=1
    # disabled opcional: bool o dict
    dis=e.get('disabled')
    if dis is not None and not (isinstance(dis,bool) or isinstance(dis,dict)):
        print(f"[E] item {i} disabled debe ser bool o dict", file=sys.stderr)
        errs += 1
    if isinstance(dis, dict):
        for lang in dis.keys():
            if lang not in ('es','en'):
                print(f"[E] item {i} disabled contiene idioma no soportado {lang}", file=sys.stderr)
                errs += 1
    # status opcional: string o dict es/en
    st=e.get('status')
    if st is not None and not (isinstance(st,str) or isinstance(st,dict)):
        print(f"[E] item {i} status debe ser string o dict", file=sys.stderr)
        errs += 1
    if isinstance(st, dict):
        for lang,v in st.items():
            if lang not in ('es','en'):
                print(f"[E] item {i} status idioma no soportado {lang}", file=sys.stderr)
                errs += 1
            if not isinstance(v,str):
                print(f"[E] item {i} status[{lang}] debe ser string", file=sys.stderr)
                errs += 1
if errs:
    print(f'[F] errores totales: {errs}', file=sys.stderr)
    sys.exit(3)
print(f'[OK] posts.json válido, entradas: {len(data)}')
