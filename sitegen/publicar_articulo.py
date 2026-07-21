# Uso: python3 publicar_articulo.py /ruta/nuevo_articulo.json
import os, sys, json, datetime, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
AJSON = os.path.join(HERE, "articles.json")
new = json.load(open(sys.argv[1], encoding="utf-8"))
arts = json.load(open(AJSON, encoding="utf-8"))
slugs = {a["slug"] for a in arts}
if new["slug"] in slugs:
    print("Ya existe el slug, no se anade:", new["slug"]); sys.exit(0)
new.setdefault("date", datetime.date.today().isoformat())
new.setdefault("author", "Equipo editorial de Sin Rodeos")
arts.insert(0, new)
json.dump(arts, open(AJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Anadido:", new["slug"], "| total:", len(arts))
subprocess.run([sys.executable, os.path.join(HERE, "construir.py")], check=True)
try:
    subprocess.run([sys.executable, os.path.join(HERE, "indexnow_ping.py"), new["slug"]], check=False, timeout=20)
except Exception as e:
    print("Aviso IndexNow omitido:", e)
