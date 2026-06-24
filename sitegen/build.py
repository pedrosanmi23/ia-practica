#!/usr/bin/env python3
"""
Generador de sitio estatico para monetizacion con Google AdSense.
- Lee los articulos de content.py
- Genera HTML estatico SEO-friendly en ../site
- Crea sitemap.xml, robots.txt, paginas legales y CSS

Para anadir un articulo nuevo (automatizacion): anade un dict a ARTICLES en
content.py y ejecuta de nuevo este script. Idempotente.
"""
import os, html, datetime, shutil
from content import CONFIG, ARTICLES

try:
    import markdown as md
    def render_md(text): return md.markdown(text, extensions=["extra", "toc"])
except Exception:
    def render_md(text):
        out, in_list = [], False
        for line in text.strip().split("\n"):
            s = line.strip()
            if s.startswith("## "):
                if in_list: out.append("</ul>"); in_list=False
                out.append(f"<h2>{html.escape(s[3:])}</h2>")
            elif s.startswith("- "):
                if not in_list: out.append("<ul>"); in_list=True
                out.append(f"<li>{html.escape(s[2:])}</li>")
            elif s == "":
                if in_list: out.append("</ul>"); in_list=False
            else:
                if in_list: out.append("</ul>"); in_list=False
                out.append(f"<p>{html.escape(s)}</p>")
        if in_list: out.append("</ul>")
        return "\n".join(out)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "site")
DOMAIN = CONFIG["domain"].rstrip("/")
ADS = CONFIG.get("adsense_client", "")

ADS_HEAD = (
    f'<script async src="https://pagead2.googlesyndication.com/pagead/js/'
    f'adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>'
    if ADS else "<!-- AdSense: pega aqui tu script cuando te aprueben -->"
)

def ad_unit():
    if not ADS:
        return ('<div class="ad-placeholder">Espacio reservado para anuncio '
                '(se activa al aprobar AdSense)</div>')
    return (f'<ins class="adsbygoogle" style="display:block" '
            f'data-ad-client="{ADS}" data-ad-slot="0000000000" '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')

def page(title, desc, body, canonical, is_article=False):
    full_title = title if title == CONFIG["brand"] else f"{title} | {CONFIG['brand']}"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{'article' if is_article else 'website'}">
<meta property="og:url" content="{canonical}">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/style.css">
{ADS_HEAD}
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/">{html.escape(CONFIG['brand'])}</a>
    <nav>
      <a href="/">Inicio</a>
      <a href="/sobre-nosotros.html">Sobre nosotros</a>
      <a href="/contacto.html">Contacto</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {datetime.date.today().year} {html.escape(CONFIG['brand'])}. Todos los derechos reservados.</p>
    <p><a href="/politica-privacidad.html">Privacidad</a> &middot;
       <a href="/aviso-legal.html">Aviso legal</a> &middot;
       <a href="/contacto.html">Contacto</a></p>
  </div>
</footer>
</body>
</html>"""

def article_html(a):
    body_html = render_md(a["body"])
    parts = body_html.split("</h2>", 1)
    if len(parts) == 2:
        body_html = parts[0] + "</h2>" + ad_unit() + parts[1]
    canonical = f"{DOMAIN}/{a['slug']}.html"
    body = f"""
<article class="post">
  <p class="crumb"><a href="/">Inicio</a> &rsaquo; {html.escape(a['category'])}</p>
  <h1>{html.escape(a['title'])}</h1>
  <p class="meta">Publicado el {a['date']} &middot; {html.escape(a['category'])}</p>
  {body_html}
  {ad_unit()}
</article>
"""
    return page(a["title"], a["description"], body, canonical, is_article=True)

def home_html():
    cards = ""
    for a in sorted(ARTICLES, key=lambda x: x["date"], reverse=True):
        cards += f"""
    <article class="card">
      <span class="tag">{html.escape(a['category'])}</span>
      <h2><a href="/{a['slug']}.html">{html.escape(a['title'])}</a></h2>
      <p>{html.escape(a['description'])}</p>
      <a class="more" href="/{a['slug']}.html">Leer mas &rarr;</a>
    </article>"""
    body = f"""
<section class="hero">
  <h1>{html.escape(CONFIG['brand'])}</h1>
  <p>{html.escape(CONFIG['tagline'])}</p>
</section>
{ad_unit()}
<section class="grid">{cards}
</section>
"""
    return page(CONFIG["brand"], CONFIG["description"], body, DOMAIN + "/")

LEGAL = {
"sobre-nosotros.html": ("Sobre nosotros", f"Quienes somos en {CONFIG['brand']}.", f"""
<h1>Sobre nosotros</h1>
<p>{CONFIG['brand']} es un proyecto editorial dedicado a explicar de forma clara y
practica como aprovechar las herramientas de inteligencia artificial y el software
de productividad en el dia a dia.</p>
<p>Publicamos guias, comparativas y tutoriales pensados para personas que quieren
trabajar mejor y ahorrar tiempo, sin necesidad de conocimientos tecnicos avanzados.</p>
<p>Si tienes dudas o sugerencias, escribenos a traves de la <a href="/contacto.html">pagina de contacto</a>.</p>
"""),
"contacto.html": ("Contacto", f"Contacta con {CONFIG['brand']}.", f"""
<h1>Contacto</h1>
<p>Puedes ponerte en contacto con nosotros por correo electronico:</p>
<p><strong>{CONFIG['email']}</strong></p>
<p>Respondemos en un plazo aproximado de 48-72 horas laborables.</p>
"""),
"politica-privacidad.html": ("Politica de privacidad", "Politica de privacidad y uso de cookies.", f"""
<h1>Politica de privacidad</h1>
<p>En {CONFIG['brand']} respetamos tu privacidad. Esta pagina explica que datos se
recogen y como se usan.</p>
<h2>Publicidad y cookies de terceros</h2>
<p>Este sitio utiliza Google AdSense para mostrar anuncios. Google, como proveedor
externo, utiliza cookies para publicar anuncios. El uso de la cookie DART permite a
Google mostrar anuncios a los usuarios en funcion de sus visitas a este y otros
sitios web.</p>
<p>Los usuarios pueden inhabilitar el uso de la cookie DART visitando la pagina de
politica de privacidad de la red de contenido y los anuncios de Google.</p>
<h2>Tus opciones</h2>
<p>Puedes configurar o desactivar las cookies desde tu navegador. Tambien puedes
gestionar tus preferencias de anuncios personalizados en la configuracion de anuncios
de Google.</p>
<h2>Contacto</h2>
<p>Para cualquier cuestion sobre privacidad: {CONFIG['email']}</p>
"""),
"aviso-legal.html": ("Aviso legal", "Aviso legal y condiciones de uso.", f"""
<h1>Aviso legal</h1>
<p>El contenido de {CONFIG['brand']} tiene caracter exclusivamente informativo.
Hacemos lo posible por mantener la informacion actualizada y veraz, pero no
garantizamos la ausencia de errores ni la disponibilidad permanente del sitio.</p>
<p>Las marcas y nombres de productos mencionados pertenecen a sus respectivos
propietarios. Algunos enlaces pueden ser de afiliados.</p>
"""),
}

def write(d, name, content):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(content)

def sitemap():
    today = datetime.date.today().isoformat()
    urls = [f"{DOMAIN}/"] + [f"{DOMAIN}/{a['slug']}.html" for a in ARTICLES] + \
           [f"{DOMAIN}/{n}" for n in LEGAL]
    items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>'

CSS = """
:root{--bg:#0f1115;--card:#171a21;--ink:#e8eaed;--muted:#9aa0aa;--brand:#4f8cff;--line:#262a33}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}
.wrap{max-width:820px;margin:0 auto;padding:0 20px}
.site-header{border-bottom:1px solid var(--line);background:#11131a;position:sticky;top:0;z-index:10}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;height:62px}
.logo{font-weight:800;font-size:20px;color:var(--ink);text-decoration:none}
nav a{color:var(--muted);text-decoration:none;margin-left:18px;font-size:15px}
nav a:hover{color:var(--ink)}
.hero{padding:48px 0 24px}
.hero h1{font-size:34px;margin:0 0 8px}
.hero p{color:var(--muted);font-size:18px;margin:0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:18px 0 48px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
.card h2{font-size:18px;margin:8px 0 6px;line-height:1.3}
.card h2 a{color:var(--ink);text-decoration:none}
.card p{color:var(--muted);font-size:14px;margin:0 0 12px}
.tag{display:inline-block;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--brand);background:rgba(79,140,255,.12);padding:3px 9px;border-radius:999px}
.more{color:var(--brand);text-decoration:none;font-size:14px;font-weight:600}
.post{padding:34px 0 50px}
.post h1{font-size:30px;line-height:1.25;margin:6px 0 8px}
.post h2{font-size:22px;margin:30px 0 10px}
.post p{margin:14px 0}
.post ul{margin:14px 0;padding-left:22px}
.post li{margin:6px 0}
.crumb,.meta{color:var(--muted);font-size:13px;margin:0}
.crumb a{color:var(--muted)}
a{color:var(--brand)}
.ad-placeholder{border:1px dashed #3a3f4b;color:#6b7280;text-align:center;padding:22px;border-radius:10px;margin:26px 0;font-size:13px;background:#13161d}
.site-footer{border-top:1px solid var(--line);margin-top:30px;padding:26px 0;color:var(--muted);font-size:14px}
.site-footer a{color:var(--muted)}
@media(max-width:640px){.grid{grid-template-columns:1fr}.hero h1{font-size:28px}}
"""

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    write(OUT, "style.css", CSS)
    write(OUT, "index.html", home_html())
    for a in ARTICLES:
        write(OUT, f"{a['slug']}.html", article_html(a))
    for fname, (title, desc, body) in LEGAL.items():
        canonical = f"{DOMAIN}/{fname}"
        write(OUT, fname, page(title, desc, body, canonical))
    write(OUT, "sitemap.xml", sitemap())
    write(OUT, "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"OK -> {len(ARTICLES)} articulos + {len(LEGAL)} paginas. Sitio en: {os.path.abspath(OUT)}")

if __name__ == "__main__":
    build()
