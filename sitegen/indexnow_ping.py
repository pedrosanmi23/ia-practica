#!/usr/bin/env python3
# Notifica a los motores compatibles con IndexNow (Bing, Yandex, Naver, Seznam, Yep...)
# de que hay URLs nuevas o actualizadas. Google NO participa en IndexNow (usa Search Console aparte).
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
DOMAIN = CONFIG["domain"].rstrip("/")
HOST = DOMAIN.replace("https://", "").replace("http://", "")
KEY = CONFIG.get("indexnow_key")

def ping(urls):
    if not KEY:
        print("No hay indexnow_key en config.json, nada que hacer.")
        return
    if not urls:
        return
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{DOMAIN}/{KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("IndexNow respuesta:", resp.status)
    except urllib.error.HTTPError as e:
        print("IndexNow HTTPError:", e.code, e.read().decode(errors="replace")[:300])
    except Exception as e:
        print("IndexNow error:", e)

if __name__ == "__main__":
    # Uso: python3 indexnow_ping.py slug1 slug2 ...
    # Si no se pasan argumentos, notifica TODAS las URLs del sitio (uso puntual/bootstrap).
    slugs = sys.argv[1:]
    if slugs:
        urls = [f"{DOMAIN}/{s}" for s in slugs]
    else:
        ARTICLES = json.load(open(os.path.join(HERE, "articles.json"), encoding="utf-8"))
        urls = [f"{DOMAIN}/"] + [f"{DOMAIN}/{a['slug']}" for a in ARTICLES]
        for c in CONFIG.get("categories", []):
            urls.append(f"{DOMAIN}/categoria-{c['slug']}")
    print(f"Notificando {len(urls)} URLs a IndexNow...")
    ping(urls)
