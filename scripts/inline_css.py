#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inserta (minificado) css/styles.css + css/tailwind.css dentro de index.html, entre las
marcas <!-- inline-css:start --> y <!-- inline-css:end -->.

Por qué: con el CSS en un <link> bloqueante la portada tardaba ~1,8 s en pintar en móvil
(PageSpeed 99). Con el CSS ya dentro del HTML baja a ~0,9 s (PageSpeed 100).
Las demás páginas siguen usando los <link> (se cachean entre páginas).

IMPORTANTE: ejecutar SIEMPRE después de tocar css/styles.css o css/tailwind.css:
    bash scripts/build_css.sh        # recompila Tailwind (si hay clases nuevas)
    python3 scripts/inline_css.py    # reinyecta el CSS en index.html
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
START, END = "<!-- inline-css:start -->", "<!-- inline-css:end -->"


def minify(css):
    with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False, encoding="utf-8") as t:
        t.write(css)
        path = t.name
    try:
        out = subprocess.run(
            ["npx", "--yes", "esbuild@0.25.0", path, "--minify", "--log-level=error"],
            capture_output=True, text=True, check=True,
        ).stdout
    finally:
        os.unlink(path)
    return out.strip()


def main():
    with open(os.path.join(ROOT, "css", "styles.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ROOT, "css", "tailwind.css"), encoding="utf-8") as f:
        css += "\n" + f.read()
    block = f"{START}<style>{minify(css)}</style>{END}"

    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    if START in html:
        html = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, html, count=1, flags=re.S)
    else:
        pat = re.compile(
            r'<link rel="stylesheet" href="css/styles\.css\?v=\d+" />\s*<link rel="stylesheet" href="css/tailwind\.css\?v=\d+" />'
        )
        if not pat.search(html):
            sys.exit("No encuentro ni las marcas ni los <link> de CSS en index.html")
        html = pat.sub(lambda m: block, html, count=1)

    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"CSS inline en index.html: {len(block)/1024:.1f} KB")


if __name__ == "__main__":
    main()
