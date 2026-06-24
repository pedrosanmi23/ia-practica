@echo off
REM Version silenciosa para el Programador de tareas de Windows (sin pause).
cd /d "%~dp0"
git add -A
git commit -m "Articulo automatico %date%"
git push
