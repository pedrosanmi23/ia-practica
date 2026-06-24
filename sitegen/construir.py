# Regenera el sitio y copia los archivos a la raiz del repositorio.
import os, glob, shutil, build
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TMP = "/tmp/_site_build"
if os.path.exists(TMP): shutil.rmtree(TMP, ignore_errors=True)
build.OUT = TMP
build.build()
for f in glob.glob(TMP + "/*"):
    shutil.copy(f, REPO)
print("Sitio regenerado y copiado a", REPO)
