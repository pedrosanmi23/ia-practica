@echo off
REM Publica el sitio en GitHub de forma automatica y a prueba de fallos.
REM Lo ejecuta el Programador de tareas de Windows (sin pause).
cd /d "%~dp0"

REM 1) Limpia bloqueos colgados (no pasa nada si no existen)
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock" del /f /q ".git\HEAD.lock"
if exist ".git\refs\heads\main.lock" del /f /q ".git\refs\heads\main.lock"

REM 2) Prepara los cambios; si el indice esta corrupto, lo reconstruye y reintenta
git add -A
if errorlevel 1 (
  echo Indice corrupto, reconstruyendo...
  del /f /q ".git\index"
  git reset
  git add -A
)

REM 3) Commit y push solo si hay algo que publicar
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Articulo automatico %date%"
  git push
) else (
  echo Sin cambios que publicar.
)
