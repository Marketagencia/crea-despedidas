#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimiza el <head> de TODAS las páginas .html para PageSpeed (móvil):

  1. Quita el Play CDN de Tailwind (JS bloqueante) y enlaza css/tailwind.css (compilado).
  2. Quita Google Fonts (CSS bloqueante) y precarga las fuentes autoalojadas (assets/fonts).
  3. Carga diferida del Google tag (gtag.js): se carga en la primera interacción o
     5 s después del load; mientras tanto los eventos se encolan en dataLayer.
  4. Sustituye logo.png / fish.png (pesados) por logo.webp / fish.webp.

Es idempotente: se puede volver a ejecutar sobre páginas nuevas (p. ej. artículos que
publica AutoSEO con la plantilla antigua) sin estropear las ya optimizadas.

Uso:  python3 scripts/optimize_head.py [--dry-run]
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_V = os.environ.get("CSS_V", "61")      # ?v= de styles.css
TW_V = os.environ.get("TW_V", "2")         # ?v= de tailwind.css

GTAG_NEW = """<!-- Google tag (gtag.js) · carga diferida: primera interacción o 5 s tras el load -->
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'AW-10805472079');
    (function () {
      var done = 0;
      function load() {
        if (done) return; done = 1;
        var s = document.createElement('script');
        s.async = true;
        s.src = 'https://www.googletagmanager.com/gtag/js?id=AW-10805472079';
        document.head.appendChild(s);
      }
      ['pointerdown', 'keydown', 'scroll', 'touchstart'].forEach(function (e) {
        addEventListener(e, load, { once: true, passive: true });
      });
      addEventListener('load', function () { setTimeout(load, 5000); });
    })();
  </script>"""

FONT_PRELOAD = """<link rel="preload" href="/assets/fonts/sora-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin />"""

RE_GTAG = re.compile(
    r'<!-- Google tag \(gtag\.js\) -->\s*<script async src="https://www\.googletagmanager\.com/gtag/js\?id=AW-10805472079">\s*</script>\s*<script>.*?</script>',
    re.S,
)
RE_FONTS = re.compile(
    r'(?:<!--\s*Fuentes:[^>]*-->\s*)?<link rel="preconnect" href="https://fonts\.googleapis\.com"\s*/>\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin\s*/>\s*'
    r'<link\s+href="https://fonts\.googleapis\.com/css2\?[^"]*"\s+rel="stylesheet"\s*/>',
    re.S,
)
RE_TW = re.compile(
    r'(?:<!--\s*Tailwind CSS[^>]*-->\s*)?<script src="https://cdn\.tailwindcss\.com"></script>\s*<script>\s*tailwind\.config\s*=.*?</script>',
    re.S,
)
RE_STYLES = re.compile(r'<link rel="stylesheet" href="((?:/)?css/)styles\.css\?v=\d+" />')


def process(html):
    orig = html
    html = RE_GTAG.sub(GTAG_NEW, html, count=1)
    html = RE_FONTS.sub(FONT_PRELOAD, html, count=1)
    html = RE_TW.sub("", html, count=1)

    def styles(m):
        pre = m.group(1)
        out = f'<link rel="stylesheet" href="{pre}styles.css?v={CSS_V}" />'
        out += f'\n  <link rel="stylesheet" href="{pre}tailwind.css?v={TW_V}" />'
        return out

    if "tailwind.css" not in html:
        html = RE_STYLES.sub(styles, html, count=1)
    else:
        html = re.sub(r'(css/styles\.css\?v=)\d+', r'\g<1>' + CSS_V, html)
        html = re.sub(r'(css/tailwind\.css\?v=)\d+', r'\g<1>' + TW_V, html)

    # <meta charset> debe quedar en los primeros 1024 bytes: siempre lo primero del <head>
    if re.search(r'<head>\s*<meta charset="UTF-8" />', html) is None:
        html = html.replace('<meta charset="UTF-8" />', '', 1)
        html = html.replace('<head>', '<head>\n  <meta charset="UTF-8" />', 1)

    html = html.replace('src="/assets/logo.png"', 'src="/assets/logo.webp"')
    html = html.replace('src="assets/logo.png"', 'src="assets/logo.webp"')
    html = html.replace('src="/assets/fish.png"', 'src="/assets/fish.webp"')
    html = html.replace('src="assets/fish.png"', 'src="assets/fish.webp"')
    # logo del pie: versión más grande y carga perezosa; el logo del menú usa la pequeña
    html = re.sub(
        r'(<a href="[^"]*" class="brand brand--footer"[^>]*>\s*)<img src="(/?)assets/logo\.webp"([^>]*?)\s*/>',
        lambda m: f'{m.group(1)}<img src="{m.group(2)}assets/logo-lg.webp"{m.group(3)} loading="lazy" decoding="async" />',
        html,
    )
    # el pez del cursor no es crítico: prioridad baja
    html = re.sub(
        r'(<img src="[^"]*fish\.webp" id="fish-cursor")(?![^>]*fetchpriority)',
        r'\1 fetchpriority="low" decoding="async"',
        html,
    )
    # favicon (evita la petición 404 a /favicon.ico y el error en consola)
    if 'rel="icon"' not in html:
        html = html.replace('</head>', '  <link rel="icon" type="image/webp" href="/assets/fish.webp" />\n</head>', 1)
    return html, html != orig


def main():
    dry = "--dry-run" in sys.argv
    files = [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True) if "/node_modules/" not in f]
    changed = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            html = fh.read()
        new, ch = process(html)
        if ch:
            changed += 1
            if not dry:
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(new)
    print(f"{len(files)} páginas, {changed} modificadas" + (" (dry-run)" if dry else ""))


if __name__ == "__main__":
    main()
