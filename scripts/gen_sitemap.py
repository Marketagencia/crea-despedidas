#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera sitemap.xml a partir de las páginas fijas del sitio + todos los
artículos del blog ya sincronizados (blog/_data.json).

No requiere dependencias externas. Vuelve a ejecutarse cada vez que
sync_blog.py traiga artículos nuevos, para mantener sitemap.xml al día.

Uso:
  python3 scripts/gen_sitemap.py
"""
import json
import os
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blog")
MANIFEST_PATH = os.path.join(BLOG_DIR, "_data.json")
OUT_PATH = os.path.join(ROOT, "sitemap.xml")
BASE = "https://creadespedidas.com"

# Páginas fijas del sitio: (ruta, changefreq, priority)
STATIC_PAGES = [
    ("/", "weekly", "1.0"),
    ("/restaurantes-despedidas-cumpleanos-valencia/", "monthly", "0.9"),
    ("/experiencias-actividades-valencia/", "monthly", "0.9"),
    ("/alojamientos-despedidas-valencia/", "monthly", "0.8"),
    ("/traslados-valencia/", "monthly", "0.8"),
    ("/blog/", "daily", "0.8"),
]


def load_blog_entries():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def to_date(iso):
    try:
        return datetime.fromisoformat(iso.split("+")[0]).date().isoformat()
    except Exception:
        return date.today().isoformat()


def main():
    entries = load_blog_entries()
    today = date.today().isoformat()

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for path, freq, prio in STATIC_PAGES:
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE}{path}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")

    for e in sorted(entries, key=lambda x: x["date"], reverse=True):
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE}/blog/{e['slug']}/</loc>")
        lines.append(f"    <lastmod>{to_date(e['date'])}</lastmod>")
        lines.append("    <changefreq>yearly</changefreq>")
        lines.append("    <priority>0.6</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    lines.append("")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Escrito {OUT_PATH}: {len(STATIC_PAGES)} páginas fijas + {len(entries)} artículos de blog.")


if __name__ == "__main__":
    main()
