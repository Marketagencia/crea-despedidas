#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincroniza artículos del blog real de creadespedidas.com (WordPress) como
páginas estáticas /blog/<slug>/ en este sitio, con el mismo diseño premium
(nav, footer, tipografía, glass cards) que el resto de la web.

No requiere dependencias externas (solo librería estándar de Python 3).

Uso:
  python3 scripts/sync_blog.py                  # trae los 25 más recientes que falten
  python3 scripts/sync_blog.py --limit 40        # trae hasta 40 más recientes que falten
  python3 scripts/sync_blog.py --slugs a,b,c     # trae solo esos slugs concretos
  python3 scripts/sync_blog.py --force           # regenera también los que ya existen
  python3 scripts/sync_blog.py --list-only       # solo lista qué hay en creadespedidas.com

Al terminar, regenera blog/index.html con el listado de TODO lo ya sincronizado
localmente (no solo lo de esta pasada), ordenado por fecha descendente.
Vuelve a ejecutarse cuando quieras traer artículos nuevos: solo genera los que
falten, salvo que uses --force.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blog")
MANIFEST_PATH = os.path.join(BLOG_DIR, "_data.json")
API = "https://creadespedidas.com/wp-json/wp/v2/posts"
CACHE_V = "31"  # debe coincidir con el ?v= de css/js del resto del sitio

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def fetch_json(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; CreaDespedidasBlogSync/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_posts(limit, slugs):
    if slugs:
        posts = []
        for slug in slugs:
            url = f"{API}?slug={slug}&_fields=slug,date,title,content,excerpt,aioseo_head_json"
            data = fetch_json(url)
            posts.extend(data)
        return posts

    posts = []
    per_page = min(limit, 100) if limit else 100
    page = 1
    while limit is None or len(posts) < limit:
        url = (
            f"{API}?per_page={per_page}&page={page}&orderby=date&order=desc"
            "&_fields=slug,date,title,content,excerpt,aioseo_head_json"
        )
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as e:
            if e.code == 400:  # se acabaron las páginas
                break
            raise
        if not data:
            break
        posts.extend(data)
        page += 1
        if len(data) < per_page:
            break
    return posts[:limit] if limit else posts


def fmt_date_es(iso):
    d = datetime.fromisoformat(iso.split("+")[0])
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def truncate(s, n):
    s = s.strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


def esc_attr(s):
    return html.escape(s or "", quote=True)


PAGE_TMPL = """<!DOCTYPE html>
<html lang="es" class="scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0B0B0F" />
  <script>document.documentElement.classList.add('js');</script>
  <title>{title_tag}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{canonical}" />
{extra_head}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{ extend: {{
        fontFamily: {{ display: ['Syne', 'system-ui', 'sans-serif'], sans: ['"Space Grotesk"', 'system-ui', 'sans-serif'] }},
        colors: {{ ink: '#0B0B0F', surface: '#121218', neon: {{ cyan: '#00F2FE', blue: '#4FACFE', pink: '#FF2FB9', orange: '#FF7A18' }} }},
      }} }},
    }};
  </script>
  <link rel="stylesheet" href="{root}css/styles.css?v={cache_v}" />
</head>

<body class="bg-ink text-white font-sans antialiased overflow-x-hidden">
  <div class="bg-canvas" aria-hidden="true">
    <span class="orb orb--1"></span><span class="orb orb--2"></span><span class="orb orb--3"></span><span class="grain"></span>
  </div>

  <a href="#contenido" class="skip-link">Saltar al contenido</a>

  <header id="nav" class="fixed inset-x-0 top-0 z-50 transition-all duration-300">
    <nav class="mx-auto flex max-w-7xl items-center justify-between px-5 py-3 md:px-8" aria-label="Principal">
      <a href="/" class="brand" aria-label="Crea Despedidas — Inicio">
        <img src="/assets/logo.png" class="brand-logo" alt="Crea Despedidas" width="972" height="701" />
      </a>
      <ul class="hidden items-center gap-8 text-sm text-white/70 lg:flex">
        <li class="nav-item has-submenu">
          <a class="nav-link" href="/#servicios" aria-haspopup="true">
            Servicios
            <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </a>
          <div class="submenu" role="menu">
            <a role="menuitem" href="/restaurantes-despedidas-cumpleanos-valencia/">Restaurante Propio</a>
            <a role="menuitem" href="/experiencias-actividades-valencia/">Experiencias &amp; Actividades</a>
            <a role="menuitem" href="/alojamientos-despedidas-valencia/">Alojamientos</a>
            <a role="menuitem" href="/traslados-valencia/">Traslados</a>
          </div>
        </li>
        <li><a class="nav-link" href="/#planner">Configurador</a></li>
        <li><a class="nav-link" href="/blog/">Blog</a></li>
        <li><a class="nav-link" href="/#opiniones">Opiniones</a></li>
        <li><a class="nav-link" href="/#contacto">Contacto</a></li>
      </ul>
      <div class="flex items-center gap-3">
        <a href="https://wa.me/34644687001" target="_blank" rel="noopener" class="hidden rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 backdrop-blur-md transition hover:border-white/30 hover:text-white sm:inline-flex">WhatsApp</a>
        <a href="/#planner" data-magnetic class="btn-primary text-sm"><span>Crea tu experiencia</span></a>
      </div>
    </nav>
  </header>

  <main class="subpage-main" id="contenido">
    <div class="mx-auto max-w-7xl px-5 md:px-8">

{body}
    </div>
  </main>

  <footer id="contacto" class="relative border-t border-white/10 px-5 pb-10 pt-20 md:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="grid gap-12 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div>
          <a href="/" class="brand brand--footer" aria-label="Crea Despedidas — Inicio">
            <img src="/assets/logo.png" class="brand-logo" alt="Crea Despedidas" width="972" height="701" />
          </a>
          <p class="mt-4 max-w-xs text-sm leading-relaxed text-white/50">Despedidas de soltero/a y eventos privados en Valencia. La despedida que nunca olvidaréis.</p>
        </div>
        <nav aria-label="Servicios">
          <h3 class="footer-h">Servicios</h3>
          <ul class="footer-list">
            <li><a href="/restaurantes-despedidas-cumpleanos-valencia/">Restaurante Propio</a></li>
            <li><a href="/experiencias-actividades-valencia/">Experiencias &amp; Actividades</a></li>
            <li><a href="/alojamientos-despedidas-valencia/">Alojamientos</a></li>
            <li><a href="/traslados-valencia/">Traslados</a></li>
            <li><a href="/blog/">Blog</a></li>
          </ul>
        </nav>
        <nav aria-label="Enlaces">
          <h3 class="footer-h">Crea Despedidas</h3>
          <ul class="footer-list">
            <li><a href="/#planner">Configurador</a></li>
            <li><a href="/#opiniones">Opiniones</a></li>
            <li><a href="/#contacto">Contacto</a></li>
          </ul>
        </nav>
        <div>
          <h3 class="footer-h">Contacto</h3>
          <address class="mt-3 space-y-1 text-sm not-italic text-white/50">
            <p>Av. de l'Enginyer Manuel Soto, 14 Bis · Valencia</p>
            <p><a class="hover:text-white" href="mailto:info@creadespedidas.com">info@creadespedidas.com</a></p>
            <p><a class="hover:text-white" href="tel:+34644687001">+34 644 687 001</a> · L–S 9:00–20:00</p>
          </address>
        </div>
      </div>
      <div class="mt-16 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 text-xs text-white/40 md:flex-row">
        <p>© <span id="year">2026</span> Crea Despedidas. Todos los derechos reservados.</p>
        <ul class="flex gap-6"><li><a href="/" class="hover:text-white">Inicio</a></li></ul>
      </div>
    </div>
  </footer>

  <img src="/assets/fish.png" id="fish-cursor" alt="" aria-hidden="true" />
  <a href="https://wa.me/34644687001" target="_blank" rel="noopener" class="wa-float" aria-label="Escríbenos por WhatsApp">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20l1.5-4.5A8 8 0 1 1 9 19L4 20Z"/><path d="M9 10c0 3 2.5 5.5 5.5 5.5M9 10c0-1 1-1.5 1.5-1l1 1.5-1 1M14.5 15.5c1 0 1.5-1 1-1.5L14 13l-1 1"/></svg>
  </a>
  <script src="{root}js/main.js?v={cache_v}" defer></script>
</body>
</html>
"""

ARTICLE_CTA = """      <section class="svc-section">
        <div class="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] px-8 py-14 text-center backdrop-blur-xl">
          <div class="cta-glow" aria-hidden="true"></div>
          <h2 class="relative font-display text-[clamp(1.6rem,3.6vw,2.6rem)] font-800">¿Te organizamos la tuya?</h2>
          <p class="relative mx-auto mt-3 max-w-md text-white/60">Cuéntanos grupo, fecha y estilo. Te preparamos una propuesta a medida en menos de 24&nbsp;h.</p>
          <div class="relative mt-7 flex flex-wrap justify-center gap-4">
            <a href="/#planner" data-magnetic class="btn-primary text-base"><span>Crea tu experiencia</span></a>
            <a href="https://wa.me/34644687001" target="_blank" rel="noopener" data-magnetic class="btn-glass text-base"><span>Hablar por WhatsApp</span></a>
          </div>
        </div>
      </section>
"""


def build_article_page(post):
    slug = post["slug"]
    title = strip_tags(post["title"]["rendered"])
    date_iso = post["date"]
    date_es = fmt_date_es(date_iso)
    excerpt_plain = truncate(strip_tags(post.get("excerpt", {}).get("rendered", "")), 200)
    aioseo = post.get("aioseo_head_json") or {}
    description = truncate(strip_tags(aioseo.get("description") or excerpt_plain), 160)
    content_html = post["content"]["rendered"]
    canonical = f"/blog/{slug}/"

    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "datePublished": date_iso,
        "author": {"@type": "Organization", "name": "Crea Despedidas"},
        "publisher": {"@type": "Organization", "name": "Crea Despedidas"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }
    extra_head = (
        '  <meta property="og:type" content="article" />\n'
        f'  <meta property="og:title" content="{esc_attr(title)}" />\n'
        f'  <meta property="og:description" content="{esc_attr(description)}" />\n'
        '  <script type="application/ld+json">\n'
        f"  {json.dumps(schema, ensure_ascii=False)}\n"
        "  </script>"
    )

    body = f"""      <section class="subhero">
        <nav class="crumbs" aria-label="Ruta">
          <a href="/">Inicio</a><span>/</span><a href="/blog/">Blog</a><span>/</span> {html.escape(title)}
        </nav>
        <p class="post-date">{date_es}</p>
        <h1>{html.escape(title)}</h1>
      </section>

      <section class="svc-section">
        <div class="post-prose">{content_html}</div>
      </section>

{ARTICLE_CTA}"""

    page = PAGE_TMPL.format(
        title_tag=esc_attr(f"{title} · Blog Crea Despedidas"),
        description=esc_attr(description),
        canonical=canonical,
        extra_head=extra_head,
        root="/",
        cache_v=CACHE_V,
        body=body,
    )
    return page, {
        "slug": slug,
        "title": title,
        "date": date_iso,
        "date_es": date_es,
        "excerpt": excerpt_plain,
    }


def build_index_page(entries):
    entries_sorted = sorted(entries, key=lambda e: e["date"], reverse=True)
    cards = []
    for e in entries_sorted:
        cards.append(
            f'''          <a class="blog-card" href="/blog/{e["slug"]}/">
            <span class="blog-date">{esc_attr(e["date_es"])}</span>
            <h3>{html.escape(e["title"])}</h3>
            <p>{html.escape(truncate(e["excerpt"], 140))}</p>
            <span class="blog-more">Leer más →</span>
          </a>'''
        )
    grid = "\n".join(cards) if cards else "          <p class=\"text-white/50\">Muy pronto, nuevos artículos.</p>"

    body = f"""      <section class="subhero">
        <nav class="crumbs" aria-label="Ruta">
          <a href="/">Inicio</a><span>/</span> Blog
        </nav>
        <h1>El <span class="text-gradient">blog</span> de Crea Despedidas</h1>
        <p class="lead">
          Ideas, guías y trucos para organizar la despedida perfecta en Valencia:
          actividades, restaurantes, packs y todo lo que necesitas saber antes de reservar.
        </p>
      </section>

      <section class="svc-section" aria-label="Artículos del blog">
        <div class="blog-grid">
{grid}
        </div>
      </section>

{ARTICLE_CTA}"""

    extra_head = ""
    page = PAGE_TMPL.format(
        title_tag=esc_attr("Blog · Ideas y guías para tu despedida en Valencia · Crea Despedidas"),
        description=esc_attr(
            "Ideas, guías y trucos para organizar la despedida perfecta en Valencia: actividades, "
            "restaurantes, packs y consejos prácticos, directo desde el equipo de Crea Despedidas."
        ),
        canonical="/blog/",
        extra_head=extra_head,
        root="/",
        cache_v=CACHE_V,
        body=body,
    )
    return page


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_manifest(entries):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=25, help="Nº de artículos más recientes a comprobar (por defecto 25)")
    ap.add_argument("--slugs", type=str, default=None, help="Lista de slugs concretos, separados por comas")
    ap.add_argument("--force", action="store_true", help="Regenera también los artículos ya sincronizados")
    ap.add_argument("--list-only", action="store_true", help="Solo lista los artículos disponibles en origen, no escribe nada")
    args = ap.parse_args()

    slugs = [s.strip() for s in args.slugs.split(",")] if args.slugs else None

    print("Consultando creadespedidas.com…", file=sys.stderr)
    posts = fetch_posts(None if slugs else args.limit, slugs)
    print(f"  {len(posts)} artículo(s) obtenidos de origen.", file=sys.stderr)

    if args.list_only:
        for p in posts:
            print(f'{p["date"][:10]}  {p["slug"]}')
        return

    manifest = {e["slug"]: e for e in load_manifest()}
    created, skipped = 0, 0

    for post in posts:
        slug = post["slug"]
        out_dir = os.path.join(BLOG_DIR, slug)
        out_file = os.path.join(out_dir, "index.html")
        if os.path.exists(out_file) and not args.force:
            skipped += 1
            continue
        page_html, entry = build_article_page(post)
        os.makedirs(out_dir, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(page_html)
        manifest[slug] = entry
        created += 1
        print(f"  + {slug}", file=sys.stderr)

    save_manifest(list(manifest.values()))

    index_html = build_index_page(list(manifest.values()))
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(
        f"Hecho: {created} artículo(s) nuevo(s), {skipped} ya existían, "
        f"{len(manifest)} en total en blog/index.html.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
