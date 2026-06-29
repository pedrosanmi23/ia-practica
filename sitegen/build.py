#!/usr/bin/env python3
# Generador estatico multi-categoria con SEO avanzado (JSON-LD, URLs limpias, enlazado interno).
import os, html, json, datetime, shutil
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
BRAND=CONFIG["brand"]
ADS=CONFIG.get("adsense_client","")
CATS=CONFIG.get("categories",[])
NAME2SLUG={c["name"]:c["slug"] for c in CATS}
CSSV="?v=5"

CAT_COLORS={"ia":("#4f8cff","#7b5cff"),"tecnologia":("#00b4d8","#0077b6"),
 "gaming":("#b5179e","#7209b7"),"finanzas":("#2dc653","#138a36"),
 "guias-compra":("#ff8800","#e85d04"),"deportes":("#ef233c","#d90429"),
 "salud":("#06d6a0","#058c6f"),"hogar":("#f4a261","#e76f51"),
 "actualidad":("#f72585","#b5179e")}
def colors(name): return CAT_COLORS.get(NAME2SLUG.get(name,""),("#4f8cff","#7b5cff"))
def cat_slug(name): return NAME2SLUG.get(name,"general")
def cat_url(name): return f"/categoria-{cat_slug(name)}"

ADS_HEAD=(f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>' if ADS else "<!-- AdSense: pega aqui tu script cuando te aprueben -->")

def ad_unit():
    if not ADS or not CONFIG.get("ad_slot"):
        return '<div class="ad-placeholder">Espacio reservado para anuncio (se activa al aprobar AdSense)</div>'
    return (f'<ins class="adsbygoogle" style="display:block" data-ad-client="{ADS}" data-ad-slot="{CONFIG["ad_slot"]}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')

def ad_rail():
    if not ADS or not CONFIG.get("ad_slot"):
        return '<div class="ad-rail-ph">Anuncio</div>'
    return (f'<ins class="adsbygoogle" style="display:inline-block;width:160px;height:600px" data-ad-client="{ADS}" data-ad-slot="{CONFIG["ad_slot"]}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')

def hero_svg(a):
    c1,c2=colors(a["category"]); cat=html.escape(a["category"].upper())
    return (f'<svg class="hero-img" viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(a["category"])}">'
            f'<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect width="1200" height="300" fill="url(#hg)"/><circle cx="1010" cy="60" r="220" fill="#fff" opacity="0.08"/>'
            f'<circle cx="180" cy="300" r="180" fill="#000" opacity="0.08"/><circle cx="980" cy="250" r="90" fill="#fff" opacity="0.10"/>'
            f'<text x="60" y="165" font-family="system-ui,Segoe UI,Arial,sans-serif" font-size="34" font-weight="800" letter-spacing="3" fill="#fff" opacity="0.92">{cat}</text></svg>')

def nav_html():
    return "".join(f'<a href="/categoria-{c["slug"]}">{html.escape(c["name"])}</a>' for c in CATS)

def page(title, desc, body, canonical, is_article=False, main_class="wrap", jsonld=None):
    full=title if title==BRAND else f"{title} | {BRAND}"
    ld=f'\n<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="{html.escape(BRAND)}">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{'article' if is_article else 'website'}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(full)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="stylesheet" href="/style.css{CSSV}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{ADS_HEAD}{ld}
</head>
<body>
<header class="site-header">
  <div class="wrap topbar"><a class="logo" href="/">{html.escape(BRAND)}</a></div>
  <nav class="catnav" aria-label="Categorias"><div class="wrap">{nav_html()}</div></nav>
</header>
<main class="{main_class}">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {datetime.date.today().year} {html.escape(BRAND)}. Todos los derechos reservados.</p>
    <p><a href="/sobre-nosotros">Sobre nosotros</a> &middot; <a href="/politica-privacidad">Privacidad</a> &middot; <a href="/aviso-legal">Aviso legal</a> &middot; <a href="/contacto">Contacto</a></p>
  </div>
</footer>
</body>
</html>"""

def card(a):
    return f"""<article class="card">
  <a class="tag" href="{cat_url(a['category'])}">{html.escape(a['category'])}</a>
  <h2><a href="/{a['slug']}">{html.escape(a['title'])}</a></h2>
  <p>{html.escape(a['description'])}</p>
  <a class="more" href="/{a['slug']}">Leer mas &rarr;</a>
</article>"""

def related_block(a):
    same=[x for x in ARTICLES if x["category"]==a["category"] and x["slug"]!=a["slug"]]
    same=sorted(same, key=lambda x:x["date"], reverse=True)[:4]
    if not same: return ""
    items="".join(f'<li><a href="/{x["slug"]}">{html.escape(x["title"])}</a></li>' for x in same)
    return f'<section class="related"><h2>Te puede interesar</h2><ul>{items}</ul></section>'

def article_jsonld(a, canonical):
    return [
      {"@context":"https://schema.org","@type":"BlogPosting",
       "headline":a["title"],"description":a["description"],
       "datePublished":a["date"],"dateModified":a["date"],"inLanguage":"es-ES",
       "mainEntityOfPage":{"@type":"WebPage","@id":canonical},
       "author":{"@type":"Organization","name":BRAND,"url":DOMAIN+"/"},
       "publisher":{"@type":"Organization","name":BRAND,
                    "logo":{"@type":"ImageObject","url":DOMAIN+"/favicon.svg"}},
       "articleSection":a["category"]},
      {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Inicio","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":a["category"],"item":DOMAIN+cat_url(a["category"])},
        {"@type":"ListItem","position":3,"name":a["title"],"item":canonical}]}
    ]

def article_html(a):
    bh=render_md(a["body"])
    parts=bh.split("</h2>",1)
    if len(parts)==2: bh=parts[0]+"</h2>"+ad_unit()+parts[1]
    canonical=f"{DOMAIN}/{a['slug']}"
    post=f"""
<article class="post">
  {hero_svg(a)}
  <nav class="crumb" aria-label="Ruta"><a href="/">Inicio</a> &rsaquo; <a href="{cat_url(a['category'])}">{html.escape(a['category'])}</a></nav>
  <h1>{html.escape(a['title'])}</h1>
  <p class="meta">Publicado el <time datetime="{a['date']}">{a['date']}</time> &middot; {html.escape(a['category'])}</p>
  {bh}
  {ad_unit()}
  {related_block(a)}
</article>"""
    body=f"""
<div class="article-layout">
  <aside class="rail rail-left"><div class="rail-sticky">{ad_rail()}</div></aside>
  {post}
  <aside class="rail rail-right"><div class="rail-sticky">{ad_rail()}</div></aside>
</div>"""
    return page(a["title"],a["description"],body,canonical,is_article=True,main_class="wrap-wide",jsonld=article_jsonld(a,canonical))

def home_html():
    bycat={}
    for a in ARTICLES: bycat.setdefault(a["category"],[]).append(a)
    secs=f'<section class="hero"><h1>{html.escape(BRAND)}</h1><p>{html.escape(CONFIG["tagline"])}</p></section>{ad_unit()}'
    recientes=sorted(ARTICLES,key=lambda x:x["date"],reverse=True)[:12]
    rc="".join(card(a) for a in recientes)
    secs+=f'<section class="catblock"><div class="cathead"><h2>Lo mas reciente</h2></div><div class="grid">{rc}</div></section>' 
    for c in CATS:
        arts=sorted(bycat.get(c["name"],[]), key=lambda x:x["date"], reverse=True)
        if not arts: continue
        cards="".join(card(a) for a in arts[:4])
        secs+=f'<section class="catblock"><div class="cathead"><h2>{html.escape(c["name"])}</h2><a class="seeall" href="/categoria-{c["slug"]}">Ver todo &rarr;</a></div><div class="grid">{cards}</div></section>'
    ld=[{"@context":"https://schema.org","@type":"WebSite","name":BRAND,"url":DOMAIN+"/","inLanguage":"es-ES"},
        {"@context":"https://schema.org","@type":"Organization","name":BRAND,"url":DOMAIN+"/",
         "logo":{"@type":"ImageObject","url":DOMAIN+"/favicon.svg"}}]
    return page(BRAND,CONFIG["description"],secs,DOMAIN+"/",jsonld=ld)

def category_html(c):
    arts=sorted([a for a in ARTICLES if a["category"]==c["name"]], key=lambda x:x["date"], reverse=True)
    cards="".join(card(a) for a in arts) or "<p>Pronto publicaremos contenido en esta categoria.</p>"
    body=f'<section class="hero"><nav class="crumb"><a href="/">Inicio</a> &rsaquo; {html.escape(c["name"])}</nav><h1>{html.escape(c["name"])}</h1></section>{ad_unit()}<section class="grid">{cards}</section>'
    return page(c["name"],f"Articulos de {c['name']} en {BRAND}: guias, comparativas y consejos practicos.",body,f"{DOMAIN}/categoria-{c['slug']}")

LEGAL={
"sobre-nosotros":("Sobre nosotros",f"Quienes somos en {BRAND}.",f"""
<h1>Sobre nosotros</h1>
<p>{BRAND} es un proyecto editorial que publica guias, comparativas y articulos practicos sobre tecnologia, inteligencia artificial, finanzas, ocio y estilo de vida.</p>
<p>Nuestro objetivo es explicar cada tema de forma clara y directa. Si tienes dudas, escribenos desde la <a href="/contacto">pagina de contacto</a>.</p>
"""),
"contacto":("Contacto",f"Contacta con {BRAND}.",f"""
<h1>Contacto</h1>
<p>Puedes escribirnos a:</p>
<p><strong>{CONFIG['email']}</strong></p>
<p>Respondemos en un plazo aproximado de 48-72 horas laborables.</p>
"""),
"politica-privacidad":("Politica de privacidad","Politica de privacidad y uso de cookies.",f"""
<h1>Politica de privacidad</h1>
<p>En {BRAND} respetamos tu privacidad. Esta pagina explica que datos se recogen y como se usan.</p>
<h2>Publicidad y cookies de terceros</h2>
<p>Este sitio utiliza Google AdSense para mostrar anuncios. Google, como proveedor externo, utiliza cookies para publicar anuncios en funcion de las visitas del usuario a este y otros sitios web.</p>
<h2>Tus opciones</h2>
<p>Puedes configurar o desactivar las cookies desde tu navegador y gestionar tus preferencias en la configuracion de anuncios de Google.</p>
<h2>Contacto</h2>
<p>Para cualquier cuestion sobre privacidad: {CONFIG['email']}</p>
"""),
"aviso-legal":("Aviso legal","Aviso legal y condiciones de uso.",f"""
<h1>Aviso legal</h1>
<p>El contenido de {BRAND} tiene caracter informativo. Procuramos que sea veraz y actual, pero no garantizamos la ausencia de errores. Las marcas y nombres de productos pertenecen a sus respectivos propietarios. Algunos enlaces pueden ser de afiliados.</p>
"""),
}

FAVICON='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="fg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4f8cff"/><stop offset="1" stop-color="#7b5cff"/></linearGradient></defs><rect width="64" height="64" rx="14" fill="url(#fg)"/><text x="32" y="43" font-family="system-ui,Segoe UI,Arial,sans-serif" font-size="30" font-weight="800" fill="#ffffff" text-anchor="middle">SR</text></svg>'

def write(d,n,c):
    with open(os.path.join(d,n),"w",encoding="utf-8") as f: f.write(c)

def sitemap():
    today=datetime.date.today().isoformat()
    rows=[(f"{DOMAIN}/",today,"1.0")]
    for c in CATS: rows.append((f"{DOMAIN}/categoria-{c['slug']}",today,"0.8"))
    for a in ARTICLES: rows.append((f"{DOMAIN}/{a['slug']}",a["date"],"0.7"))
    for s in LEGAL: rows.append((f"{DOMAIN}/{s}",today,"0.3"))
    items="\n".join(f"  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{p}</priority></url>" for u,m,p in rows)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+items+'\n</urlset>'

CSS_PATH=os.path.join(ROOT,"style.css")

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    write(OUT,"style.css",open(CSS_PATH,encoding="utf-8").read())
    write(OUT,"favicon.svg",FAVICON)
    write(OUT,"index.html",home_html())
    for a in ARTICLES: write(OUT,f"{a['slug']}.html",article_html(a))
    for c in CATS: write(OUT,f"categoria-{c['slug']}.html",category_html(c))
    for s,(t,d,b) in LEGAL.items(): write(OUT,f"{s}.html",page(t,d,b,f"{DOMAIN}/{s}"))
    write(OUT,"sitemap.xml",sitemap())
    write(OUT,"robots.txt",f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    if ADS:
        pubid=ADS.replace("ca-","")
        write(OUT,"ads.txt",f"google.com, {pubid}, DIRECT, f08c47fec0942fa0\n")
    print(f"OK -> {len(ARTICLES)} articulos, {len(CATS)} categorias (SEO v4)")

if __name__=="__main__": build()
