#!/usr/bin/env python3
"""
Fallback para obtener reportes tipo Lighthouse usando PageSpeed Insights API.
Lee scripts/urls_lighthouse.txt, consulta PSI en modo mobile y guarda JSON en lighthouse_reports/.
Requiere variable de entorno PSI_API_KEY.
"""
import os
import sys
import time
import urllib.parse
import urllib.request

URLS_FILE = os.path.join(os.getcwd(), 'scripts', 'urls_lighthouse.txt')
OUT_DIR = os.path.join(os.getcwd(), 'lighthouse_reports')
API_KEY = os.getenv('PSI_API_KEY')
BASE = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'

if not API_KEY:
    print('[warn] PSI_API_KEY no está definido, abortando fallback PSI.')
    sys.exit(0)

os.makedirs(OUT_DIR, exist_ok=True)

with open(URLS_FILE, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

for u in urls:
    params = {
        'url': u,
        'strategy': 'mobile',
        'key': API_KEY,
    }
    qs = urllib.parse.urlencode(params)
    full = f"{BASE}?{qs}"
    out_name = u.replace('https://', '').replace('http://', '').strip('/')
    out_name = out_name.replace('/', '-')
    # Mapear a nombres canónicos para que el resto del pipeline funcione
    # usando el path final
    canonical_map = {
        '': 'home',
        'en': 'en-home',
        'sobre-mi': 'sobre-mi',
        'en-about': 'en-about',
        'proyectos': 'proyectos',
        'en-projects': 'en-projects',
        'recursos': 'recursos',
        'en-resources': 'en-resources',
        'contacto': 'contacto',
        'en-contact': 'en-contact',
    }
    path = urllib.parse.urlparse(u).path.strip('/')
    key = path if path else ''
    key = key.replace('/', '-')
    name = canonical_map.get(key, 'home' if 'en' not in key else 'en-home')
    out_path = os.path.join(OUT_DIR, f'{name}.json')

    try:
        with urllib.request.urlopen(full) as resp:
            data = resp.read().decode('utf-8')
        # Guardar el JSON crudo de PSI
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f'[ok] PSI guardado: {out_path}')
    except Exception as e:
        print(f'[warn] PSI fallo para {u}: {e}')
    time.sleep(1)  # leve backoff

print('[ok] Fallback PSI completado')
