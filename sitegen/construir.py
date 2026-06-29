# Regenera el sitio y copia los archivos a la raiz del repositorio.
import os, glob, shutil, tempfile, build
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TMP = tempfile.mkdtemp(prefix="iasite_")
build.OUT = TMP
build.build()
for f in glob.glob(TMP + "/*"):
    shutil.copy(f, REPO)
print("Sitio regenerado y copiado a", REPO)
