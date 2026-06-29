#!/usr/bin/env python3
# Generador de sitio estatico multi-categoria con cabecera visual y anuncios laterales.
import os, html, datetime, shutil
from content import CONFIG, ARTICLES

try:
    import markdown as md
    def render_md(t): return md.markdown(t, extensions=["extra","toc"])
except Exception:
    def render_md(text):
        out, in_list = [], False
        for line in text.strip().split("\n"):
            s=line.strip()
            if s.startswith("## "):
                if in_list: out.append("</ul>"); in_list=False
                out.append("<h2>"+html.escape(s[3:])+"</h2>")
            elif s.startswith("- "):
                if not in_list: out.append("<ul>"); in_list=True
                out.append("<li>"+html.escape(s[2:])+"</li>")
            elif s=="":
                if in_list: out.append("</ul>"); in_list=False
            else:
                if in_list: out.append("</ul>"); in_list=False
                out.append("<p>"+html.escape(s)+"</p>")
        if in_list: out.append("</ul>")
        return "\n".join(out)

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,"..","site")
DOMAIN=CONFIG["domain"].rstrip("/")
ADS=CONFIG.get("adsense_client","")
CATS=CONFIG.get("categories",[])
NAME2SLUG={c["name"]:c["slug"] for c in CATS}

CAT_COLORS={
 "ia":("#4f8cff","#7b5cff"),"tecnologia":("#00b4d8","#0077b6"),
 "gaming":("#b5179e","#7209b7"),"finanzas":("#2dc653","#138a36"),
 "guias-compra":("#ff8800","#e85d04"),"deportes":("#ef233c","#d90429"),
 "salud":("#06d6a0","#058c6f"),"hogar":("#f4a261","#e76f51"),
 "actualidad":("#f72585","#b5179e"),
}
def colors(name):
    return CAT_COLORS.get(NAME2SLUG.get(name,""),("#4f8cff","#7b5cff"))

ADS_HEAD=(f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>' if ADS else "<!-- AdSense: pega aqui tu script cuando te aprueben -->")

def ad_unit():
    if not ADS:
        return '<div class="ad-placeholder">Espacio reservado para anuncio (se activa al aprobar AdSense)</div>'
    return (f'<ins class="adsbygoogle" style="display:block" data-ad-client="{ADS}" data-ad-slot="0000000000" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')

def ad_rail():
    if not ADS:
        return '<div class="ad-rail-ph">Anuncio</div>'
    return (f'<ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{ADS}" data-ad-slot="0000000000"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')

def hero_svg(a):
    c1,c2=colors(a["category"])
    cat=html.escape(a["category"].upper())
    return (f'<svg class="hero-img" viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(a["category"])}">'
            f'<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect width="1200" height="300" fill="url(#hg)"/>'
            f'<circle cx="1010" cy="60" r="220" fill="#ffffff" opacity="0.08"/>'
            f'<circle cx="180" cy="300" r="180" fill="#000000" opacity="0.08"/>'
            f'<circle cx="980" cy="250" r="90" fill="#ffffff" opacity="0.10"/>'
            f'<text x="60" y="165" font-family="system-ui,Segoe UI,Arial,sans-serif" font-size="34" font-weight="800" letter-spacing="3" fill="#ffffff" opacity="0.92">{cat}</text>'
            f'</svg>')

def cat_slug(name): return NAME2SLUG.get(name,"general")
def cat_url(name): return f"/categoria-{cat_slug(name)}.html"

def nav_html():
    return "".join(f'<a href="/categoria-{c["slug"]}.html">{html.escape(c["name"])}</a>' for c in CATS)

def page(title, desc, body, canonical, is_article=False, main_class="wrap"):
    full=title if title==CONFIG["brand"] else f"{title} | {CONFIG['brand']}"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{'article' if is_article else 'website'}">
<meta property="og:url" content="{canonical}">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="/style.css">
{ADS_HEAD}
</head>
<body>
<header class="site-header">
  <div class="wrap topbar"><a class="logo" href="/">{html.escape(CONFIG['brand'])}</a></div>
  <nav class="catnav"><div class="wrap">{nav_html()}</div></nav>
</header>
<main class="{main_class}">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {datetime.date.today().year} {html.escape(CONFIG['brand'])}. Todos los derechos reservados.</p>
    <p><a href="/politica-privacidad.html">Privacidad</a> &middot; <a href="/aviso-legal.html">Aviso legal</a> &middot; <a href="/contacto.html">Contacto</a></p>
  </div>
</footer>
</body>
</html>"""

def card(a):
    return f"""<article class="card">
  <a class="tag" href="{cat_url(a['category'])}">{html.escape(a['category'])}</a>
  <h2><a href="/{a['slug']}.html">{html.escape(a['title'])}</a></h2>
  <p>{html.escape(a['description'])}</p>
  <a class="more" href="/{a['slug']}.html">Leer mas &rarr;</a>
</article>"""

def article_html(a):
    bh=render_md(a["body"])
    parts=bh.split("</h2>",1)
    if len(parts)==2: bh=parts[0]+"</h2>"+ad_unit()+parts[1]
    canonical=f"{DOMAIN}/{a['slug']}.html"
    post=f"""
<article class="post">
  {hero_svg(a)}
  <p class="crumb"><a href="/">Inicio</a> &rsaquo; <a href="{cat_url(a['category'])}">{html.escape(a['category'])}</a></p>
  <h1>{html.escape(a['title'])}</h1>
  <p class="meta">Publicado el {a['date']} &middot; {html.escape(a['category'])}</p>
  {bh}
  {ad_unit()}
</article>"""
    body=f"""
<div class="article-layout">
  <aside class="rail rail-left"><div class="rail-sticky">{ad_rail()}</div></aside>
  {post}
  <aside class="rail rail-right"><div class="rail-sticky">{ad_rail()}</div></aside>
</div>"""
    return page(a["title"],a["description"],body,canonical,is_article=True,main_class="wrap-wide")

def home_html():
    bycat={}
    for a in ARTICLES: bycat.setdefault(a["category"],[]).append(a)
    secs=f'<section class="hero"><h1>{html.escape(CONFIG["brand"])}</h1><p>{html.escape(CONFIG["tagline"])}</p></section>{ad_unit()}'
    for c in CATS:
        arts=sorted(bycat.get(c["name"],[]), key=lambda x:x["date"], reverse=True)
        if not arts: continue
        cards="".join(card(a) for a in arts[:4])
        secs+=f'<section class="catblock"><div class="cathead"><h2>{html.escape(c["name"])}</h2><a class="seeall" href="/categoria-{c["slug"]}.html">Ver todo &rarr;</a></div><div class="grid">{cards}</div></section>'
    return page(CONFIG["brand"],CONFIG["description"],secs,DOMAIN+"/")

def category_html(c):
    arts=sorted([a for a in ARTICLES if a["category"]==c["name"]], key=lambda x:x["date"], reverse=True)
    cards="".join(card(a) for a in arts) or "<p>Pronto publicaremos contenido en esta categoria.</p>"
    body=f'<section class="hero"><p class="crumb"><a href="/">Inicio</a> &rsaquo; {html.escape(c["name"])}</p><h1>{html.escape(c["name"])}</h1></section>{ad_unit()}<section class="grid">{cards}</section>'
    return page(c["name"],f"Articulos de {c['name']} en {CONFIG['brand']}.",body,f"{DOMAIN}/categoria-{c['slug']}.html")

LEGAL={
"sobre-nosotros.html":("Sobre nosotros",f"Quienes somos en {CONFIG['brand']}.",f"""
<h1>Sobre nosotros</h1>
<p>{CONFIG['brand']} es un proyecto editorial que publica guias, comparativas y articulos practicos sobre tecnologia, inteligencia artificial, finanzas, ocio y estilo de vida.</p>
<p>Nuestro objetivo es explicar cada tema de forma clara y directa, para ayudarte a decidir y a ahorrar tiempo. Si tienes dudas, escribenos desde la <a href="/contacto.html">pagina de contacto</a>.</p>
"""),
"contacto.html":("Contacto",f"Contacta con {CONFIG['brand']}.",f"""
<h1>Contacto</h1>
<p>Puedes escribirnos a:</p>
<p><strong>{CONFIG['email']}</strong></p>
<p>Respondemos en un plazo aproximado de 48-72 horas laborables.</p>
"""),
"politica-privacidad.html":("Politica de privacidad","Politica de privacidad y uso de cookies.",f"""
<h1>Politica de privacidad</h1>
<p>En {CONFIG['brand']} respetamos tu privacidad. Esta pagina explica que datos se recogen y como se usan.</p>
<h2>Publicidad y cookies de terceros</h2>
<p>Este sitio utiliza Google AdSense para mostrar anuncios. Google, como proveedor externo, utiliza cookies para publicar anuncios en funcion de las visitas del usuario a este y otros sitios web.</p>
<h2>Tus opciones</h2>
<p>Puedes configurar o desactivar las cookies desde tu navegador y gestionar tus preferencias en la configuracion de anuncios de Google.</p>
<h2>Contacto</h2>
<p>Para cualquier cuestion sobre privacidad: {CONFIG['email']}</p>
"""),
"aviso-legal.html":("Aviso legal","Aviso legal y condiciones de uso.",f"""
<h1>Aviso legal</h1>
<p>El contenido de {CONFIG['brand']} tiene caracter informativo. Procuramos que sea veraz y actual, pero no garantizamos la ausencia de errores. Las marcas y nombres de productos pertenecen a sus respectivos propietarios. Algunos enlaces pueden ser de afiliados.</p>
"""),
}

def write(d,n,c):
    with open(os.path.join(d,n),"w",encoding="utf-8") as f: f.write(c)

def sitemap():
    today=datetime.date.today().isoformat()
    urls=[f"{DOMAIN}/"]+[f"{DOMAIN}/categoria-{c['slug']}.html" for c in CATS]
    urls+=[f"{DOMAIN}/{a['slug']}.html" for a in ARTICLES]+[f"{DOMAIN}/{n}" for n in LEGAL]
    items="\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+items+'\n</urlset>'

CSS_PATH=os.path.join(ROOT,"style.css")

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    write(OUT,"style.css",open(CSS_PATH,encoding="utf-8").read())
    write(OUT,"index.html",home_html())
    for a in ARTICLES: write(OUT,f"{a['slug']}.html",article_html(a))
    for c in CATS: write(OUT,f"categoria-{c['slug']}.html",category_html(c))
    for fn,(t,d,b) in LEGAL.items(): write(OUT,fn,page(t,d,b,f"{DOMAIN}/{fn}"))
    write(OUT,"sitemap.xml",sitemap())
    write(OUT,"robots.txt",f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"OK -> {len(ARTICLES)} articulos, {len(CATS)} categorias")

if __name__=="__main__": build()
