#!/usr/bin/env python3
import json
import os
import re
import glob
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
EVIDENCE = BASE / "evidence"

# Helper: find latest timestamp prefix based on files we expect
TS_PATTERN = re.compile(r"(\d{8}_\d{6})_")

def latest_ts(evd_dir: Path) -> str:
    candidates = []
    for p in evd_dir.glob("*_pages.json"):
        m = TS_PATTERN.match(p.name)
        if m:
            candidates.append(m.group(1))
    if not candidates:
        raise SystemExit("No se encontraron JSON de pages en /evidence. Ejecuta primero la auditoría bash.")
    return sorted(candidates)[-1]

def read_json(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def count_by_status(items, key="status"):
    counts = {}
    for it in items:
        st = it.get(key, "unknown")
        counts[st] = counts.get(st, 0) + 1
    return counts


def lang_from_link(link: str) -> str:
    # Heurística: '/en/' -> EN, otherwise ES
    if "/en/" in link:
        return "EN"
    return "ES"


def norm_slug_from_link(link: str) -> str:
    # Normalizar quitando dominio y prefijo 'en/' y sufijo '-en'
    try:
        path = re.sub(r"^https?://[^/]+/", "", link).strip("/")
    except Exception:
        return link
    path = re.sub(r"^en/", "", path)
    # usar última parte del path
    slug = path.split("/")[-1]
    slug = re.sub(r"-en$", "", slug)
    return slug


def pair_bilingual(pages):
    es = {}
    en = {}
    for p in pages:
        link = p.get("link", "")
        slug = p.get("slug", "")
        lang = lang_from_link(link)
        key = norm_slug_from_link(link) or slug
        entry = {
            "id": p.get("id"),
            "slug": slug,
            "title": (p.get("title") or {}).get("rendered", "").strip(),
            "link": link,
        }
        if lang == "ES":
            es[key] = entry
        else:
            en[key] = entry
    # Pair by normalized key
    pairs = []
    es_only = []
    en_only = []
    keys = set(es) | set(en)
    for k in sorted(keys):
        if k in es and k in en:
            pairs.append((es[k], en[k]))
        elif k in es:
            es_only.append(es[k])
        else:
            en_only.append(en[k])
    return pairs, es_only, en_only


def grep_file_contains(path: Path, patterns):
    if not path.exists():
        return []
    txt = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for pat in patterns:
        if re.search(pat, txt, flags=re.IGNORECASE):
            hits.append(pat)
    return hits


def og_findings(ts: str):
    findings = []
    for name in [f"{ts}_home.html", f"{ts}_home_es.html", f"{ts}_home_en.html"]:
        p = EVIDENCE / name
        if not p.exists():
            findings.append((name, "archivo no encontrado"))
            continue
        html = p.read_text(encoding="utf-8", errors="ignore")
        have = {
            'og:title': bool(re.search(r'property=[\"\']og:title[\"\']', html, re.I)),
            'og:description': bool(re.search(r'property=[\"\']og:description[\"\']', html, re.I)),
            'og:image': bool(re.search(r'property=[\"\']og:image[\"\']', html, re.I)),
            'twitter:card': bool(re.search(r'name=[\"\']twitter:card[\"\']', html, re.I)),
        }
        missing = [k for k, v in have.items() if not v]
        if missing:
            findings.append((name, f"Faltan: {', '.join(missing)}"))
        else:
            findings.append((name, "OK: tags OG/Twitter presentes"))
    return findings


def robots_sitemap_status(ts: str):
    res = []
    for name in [f"{ts}_robots.txt", f"{ts}_sitemap.xml"]:
        p = EVIDENCE / name
        if p.exists():
            size = p.stat().st_size
            status = "presente" if size > 0 else "vacío"
        else:
            size = 0
            status = "no encontrado"
        res.append((name, status, size))
    return res


def read_shortcodes_log(ts: str):
    p = EVIDENCE / f"{ts}_shortcodes_scan.txt"
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8", errors="ignore").strip().splitlines()
    return [ln for ln in lines if ln.strip()]


def smtp_signals(ts: str):
    pats = [r"wpforms", r"post-smtp", r"wpmailsmtp", r'action=\"/wp-json/\"']
    hits = {}
    for name in [f"{ts}_home.html", f"{ts}_home_es.html", f"{ts}_home_en.html"]:
        p = EVIDENCE / name
        found = grep_file_contains(p, pats)
        if found:
            hits[name] = found
    return hits


def main():
    ts = latest_ts(EVIDENCE)
    pages = read_json(EVIDENCE / f"{ts}_pages.json")
    posts = read_json(EVIDENCE / f"{ts}_posts.json")
    media = read_json(EVIDENCE / f"{ts}_media.json")

    pages_counts = count_by_status(pages)
    posts_counts = count_by_status(posts)

    pairs, es_only, en_only = pair_bilingual(pages)

    # Listar slugs/links por idioma
    es_list = sorted([(p.get('slug',''), p.get('link','')) for p in pages if lang_from_link(p.get('link','')) == 'ES'])
    en_list = sorted([(p.get('slug',''), p.get('link','')) for p in pages if lang_from_link(p.get('link','')) == 'EN'])

    shortcodes_log = read_shortcodes_log(ts)
    ogs = og_findings(ts)
    rs = robots_sitemap_status(ts)
    smtp = smtp_signals(ts)

    out_path = EVIDENCE / f"INFORME_AUDITORIA_{ts}.md"

    def h2(t):
        return f"\n\n## {t}\n\n"

    with out_path.open("w", encoding="utf-8") as out:
        out.write(f"# Informe de Auditoría Pública — pepecapiro.com (TS {ts})\n")
        out.write(f"Generado: {datetime.now().isoformat(timespec='seconds')}\n")

        # 1. Resumen ejecutivo
        out.write(h2("1. Resumen ejecutivo"))
        out.write("- Páginas: {} (por estado: {})\n".format(len(pages), pages_counts))
        out.write("- Entradas: {} (por estado: {})\n".format(len(posts), posts_counts))
        out.write("- Media: {} items\n".format(len(media)))

        # 2. Contenido
        out.write(h2("2. Contenido (páginas/entradas) + posibles huérfanas"))
        out.write("### Páginas ES\n")
        for slug, link in es_list:
            out.write(f"- {slug} — {link}\n")
        out.write("\n### Páginas EN\n")
        for slug, link in en_list:
            out.write(f"- {slug} — {link}\n")
        out.write("\nNota: 'huérfanas' requiere mapa de enlaces/menús; no concluyente desde público.\n")

        # 3. Bilingüe
        out.write(h2("3. Bilingüe (pareos ES/EN) — páginas sin pareja"))
        out.write("### Pareadas\n")
        for es_p, en_p in pairs:
            out.write(f"- {es_p['slug']} ↔ {en_p['slug']}\n")
        out.write("\n### Solo ES\n")
        for p in es_only:
            out.write(f"- {p['slug']} — {p['link']}\n")
        out.write("\n### Solo EN\n")
        for p in en_only:
            out.write(f"- {p['slug']} — {p['link']}\n")

        # 4. Formularios/shortcodes
        out.write(h2("4. Formularios/shortcodes (mapa de ubicaciones)"))
        if shortcodes_log:
            out.write("Archivo: {}\n\n".format(f"{ts}_shortcodes_scan.txt"))
            for ln in shortcodes_log:
                out.write(ln + "\n")
        else:
            out.write("No se detectaron shortcodes clásicos en pages/posts por REST.\n")

        # 5. SEO/OG/social
        out.write(h2("5. SEO/OG/social (hallazgos)"))
        for name, note in ogs:
            out.write(f"- {name}: {note}\n")

        # 6. Robots/Sitemap
        out.write(h2("6. Robots/Sitemap (estado)"))
        for name, status, size in rs:
            out.write(f"- {name}: {status} — {size} bytes\n")

        # 7. Recomendaciones inmediatas
        out.write(h2("7. Recomendaciones inmediatas (conservar/refactorizar/eliminar)"))
        out.write("- Mantener estructura bilingüe; completar pareos donde falten.\n")
        out.write("- Añadir og:image consistente para ES/EN si falta.\n")
        out.write("- Validar robots.txt y sitemap.xml en Search Console.\n")
        out.write("- Formularios: implementar solución única (CF7/Gravity/WPForms) o shortcode propio — hoy no hay huellas.\n")
        out.write("- Consolidar CSS y tokens tras analizar frecuencias (ver grep CSS).\n")

        # 7bis. SMTP señales
        out.write(h2("7bis. SMTP — señales públicas"))
        if smtp:
            for fname, pats in smtp.items():
                out.write(f"- {fname}: señales {', '.join(pats)}\n")
        else:
            out.write("Sin señales visibles de wpforms/post-smtp/wp-mail-smtp ni formularios que POSTeen a /wp-json/.\n")

    print(f"[✓] Informe generado: {out_path}")


if __name__ == "__main__":
    main()
