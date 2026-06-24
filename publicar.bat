@echo off
REM Publica los cambios del sitio en GitHub (Cloudflare despliega solo).
cd /d "%~dp0"
git add -A
git commit -m "Actualizacion de contenido"
git push
echo.
echo Listo. Si no habia cambios, no pasa nada.
pause
