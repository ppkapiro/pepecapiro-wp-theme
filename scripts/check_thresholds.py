#!/usr/bin/env python3
import json
import glob
import os
import sys

PERF_HOME_MIN   = float(os.getenv("PERF_HOME_MIN",   "90"))
PERF_OTHERS_MIN = float(os.getenv("PERF_OTHERS_MIN", "85"))
LCP_MAX         = float(os.getenv("LCP_MAX",         "2.5"))

# Mapeo esperado para mostrar nombres bonitos en el informe
PRETTY = {
  "home": "/", "en-home": "/en/",
  "sobre-mi": "/sobre-mi/", "en-about": "/en/about/",
  "proyectos": "/proyectos/", "en-projects": "/en/projects/",
  "recursos": "/recursos/", "en-resources": "/en/resources/",
  "contacto": "/contacto/", "en-contact": "/en/contact/"
}

def ms_to_s(ms):
    try:
        return float(ms)/1000.0
    except Exception:
        return None

def read_perf_and_lcp(p):
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Lighthouse JSON (o PSI adaptado): busca audits y categories
    cats = data.get("categories", {}) or data.get("lighthouseResult", {}).get("categories", {})
    audits = data.get("audits", {}) or data.get("lighthouseResult", {}).get("audits", {})
    perf_score = cats.get("performance", {}).get("score")
    if perf_score is None:
        perf_score = cats.get("performance", {}).get("score", 0)
    if perf_score is None:
        perf = None
    else:
        perf = round(float(perf_score) * 100, 1) if perf_score <= 1 else float(perf_score)

    lcp_audit = audits.get("largest-contentful-paint") or audits.get("largest-contentful-paint-element") or {}
    lcp_val = lcp_audit.get("numericValue")
    lcp_s = ms_to_s(lcp_val) if lcp_val is not None else None
    return perf, lcp_s

rows = []
violations = []
json_list = sorted(glob.glob("lighthouse_reports/*.json"))
if not json_list:
    msg = (
        "No se encontraron reportes JSON en lighthouse_reports/.\n"
        "Es posible que la ejecución de Lighthouse haya fallado o no haya generado resultados."
    )
    print("[X] ", msg)
    with open("/tmp/lh_fail.md", "w", encoding="utf-8") as f:
        f.write("### Fallo en recolección de Lighthouse\n\n" + msg + "\n")
    sys.exit(2)

for path in json_list:
    name = os.path.splitext(os.path.basename(path))[0]
    perf, lcp = read_perf_and_lcp(path)
    url = PRETTY.get(name, name)

    # Reglas
    perf_min = PERF_HOME_MIN if url in ("/", "/en/") else PERF_OTHERS_MIN
    ok_perf = (perf is not None) and (perf >= perf_min)
    ok_lcp  = (lcp is not None) and (lcp <= LCP_MAX)

    rows.append((url, perf, lcp, perf_min, LCP_MAX, ok_perf, ok_lcp))
    if not (ok_perf and ok_lcp):
        violations.append((url, perf, lcp, perf_min, LCP_MAX))

# Render breve para consola e issue
def fmt(v):
    return "n/a" if v is None else f"{v:.1f}"

table = ["| Página | Perf | LCP (s) | Umbral Perf | Umbral LCP |",
         "|-------|------|---------|-------------|------------|"]
for (url, perf, lcp, pmin, lmax, okp, okl) in rows:
    table.append(f"| {url} | {fmt(perf)} | {fmt(lcp)} | ≥ {pmin:.0f} | ≤ {lmax:.1f} |")

summary = "\n".join(table)
print(summary)

if violations:
    # Construir cuerpo del issue
    lines = ["### Incidencia de rendimiento (Lighthouse móvil)",
             "",
             summary,
             "",
             "**Violaciones:**"]
    for (url, perf, lcp, pmin, lmax) in violations:
        lines.append(f"- {url}: Perf={fmt(perf)} (min {pmin:.0f}) / LCP={fmt(lcp)}s (max {lmax:.1f})")
    lines.append("\nRevisar reportes HTML en `docs/lighthouse/` y la tabla en `docs/VALIDACION_MVP_v0_2_1.md`.")
    with open("/tmp/lh_fail.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    sys.exit(2)  # provocar fallo del job
