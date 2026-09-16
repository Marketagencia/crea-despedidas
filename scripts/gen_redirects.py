#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera redirects.conf (301) para las URLs antiguas de WordPress:

1. Cada artículo migrado a /blog/<slug>/ tenía su URL antigua en la raíz
   (https://creadespedidas.com/<slug>) -> redirige a /blog/<slug>/.
2. Las páginas de "servicio/producto" antiguas que siguen enlazadas desde
   dentro del contenido ya migrado de los artículos (detectadas escaneando
   blog/*/index.html) -> redirigen a la página nueva equivalente.

No requiere dependencias externas. Vuelve a ejecutarse cada vez que
sync_blog.py traiga artículos nuevos, para mantener redirects.conf al día.

Uso:
  python3 scripts/gen_redirects.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blog")
MANIFEST_PATH = os.path.join(BLOG_DIR, "_data.json")
OUT_PATH = os.path.join(ROOT, "redirects.conf")

# Páginas de servicio/producto de la web antigua (WordPress) que siguen
# enlazadas desde el contenido de los artículos migrados. Se añaden a mano
# porque no viven en este repo; si aparecen enlaces nuevos, añádelos aquí.
SERVICE_MAP = {
    "pack-cena-espectaculo": "/restaurantes-despedidas-cumpleanos-valencia/",
    "pack-comida-charanga": "/restaurantes-despedidas-cumpleanos-valencia/",
    "restaurantes-despedidas": "/restaurantes-despedidas-cumpleanos-valencia/",
    "humor-amarillo-valencia": "/experiencias-actividades-valencia/",
    "karting-valencia-2": "/experiencias-actividades-valencia/",
    "paintball-valencia-despedidas-soltera-soltero": "/experiencias-actividades-valencia/",
    "fiesta-privada-velero": "/experiencias-actividades-valencia/",
    "banana-boat-valencia-3": "/experiencias-actividades-valencia/",
    "alquilar-motos-de-agua-valencia": "/experiencias-actividades-valencia/",
    "mega-big-paddle-valencia": "/experiencias-actividades-valencia/",
    "tiro-con-arco-valencia": "/experiencias-actividades-valencia/",
    "bubbles-valencia-despedidas": "/experiencias-actividades-valencia/",
}

LINK_RE = re.compile(r'href="https://creadespedidas\.com/([a-z0-9\-]+)/?"')


def load_blog_slugs():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    return sorted(set(e["slug"] for e in manifest))


def scan_referenced_slugs(blog_slugs_set):
    """Slugs no-blog enlazados desde dentro de los artículos ya migrados,
    para detectar páginas de servicio nuevas que aún no estén en SERVICE_MAP."""
    found = set()
    for slug in blog_slugs_set:
        path = os.path.join(BLOG_DIR, slug, "index.html")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for m in LINK_RE.finditer(content):
            s = m.group(1)
            if s not in blog_slugs_set:
                found.add(s)
    return found


def main():
    blog_slugs = load_blog_slugs()
    blog_slugs_set = set(blog_slugs)

    referenced = scan_referenced_slugs(blog_slugs_set)
    unmapped = sorted(referenced - set(SERVICE_MAP))
    if unmapped:
        print("Aviso: slugs de servicio enlazados sin mapear en SERVICE_MAP (se omiten):")
        for s in unmapped:
            print(f"  - {s}")
        print("Añádelos a SERVICE_MAP en scripts/gen_redirects.py si quieres redirigirlos.\n")

    lines = [
        "# Generado por scripts/gen_redirects.py — NO editar a mano, se sobrescribe.",
        "# Redirecciones 301 de URLs antiguas de WordPress (creadespedidas.com) a la web nueva.",
        "",
        "# --- Artículos del blog: /<slug> -> /blog/<slug>/ ---",
    ]
    for slug in blog_slugs:
        lines.append(f"location = /{slug} {{ return 301 /blog/{slug}/; }}")

    lines.append("")
    lines.append("# --- Páginas de servicio/producto antiguas -> página nueva equivalente ---")
    for slug, dest in sorted(SERVICE_MAP.items()):
        lines.append(f"location = /{slug} {{ return 301 {dest}; }}")

    lines.append("")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Escrito {OUT_PATH}: {len(blog_slugs)} redirecciones de blog + {len(SERVICE_MAP)} de servicio.")


if __name__ == "__main__":
    main()
