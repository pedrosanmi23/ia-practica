@echo off
REM Publica los cambios del sitio en GitHub (Cloudflare despliega solo).
cd /d "%~dp0"
git add -A
git commit -m "Actualizacion de contenido"
git push
echo {"host":"sin-rodeos.com","key":"49576089a6c51ce766770178fec48c38","keyLocation":"https://sin-rodeos.com/49576089a6c51ce766770178fec48c38.txt","urlList":["https://sin-rodeos.com/","https://sin-rodeos.com/sitemap.xml"]} > "%TEMP%\indexnow_payload.json"
curl -s -X POST "https://api.indexnow.org/indexnow" -H "Content-Type: application/json; charset=utf-8" --data "@%TEMP%\indexnow_payload.json" >nul 2>&1
echo.
echo Listo. Si no habia cambios, no pasa nada.
pause
