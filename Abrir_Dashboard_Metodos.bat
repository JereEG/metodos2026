@echo off
chcp 65001 >nul
title Suite Interactiva - Metodos Computacionales (UNNE)
cd /d "%~dp0"

echo ============================================================================
echo    SUITE EDUCATIVA INTERACTIVA - METODOS COMPUTACIONALES (Lab 3 al Lab 7)
echo ============================================================================
echo.
echo Iniciando el servidor grafico interactivo...
echo El navegador web se abrira automaticamente en unos segundos.
echo (Para cerrar el programa cuando termine, simplemente cierre esta ventana).
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run "dashboard_general.py"
) else if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -m streamlit run "dashboard_general.py"
) else (
    python -m streamlit run "dashboard_general.py"
)

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo iniciar la aplicacion automaticamente.
    echo Verifique que Python este instalado y ejecute por unica vez:
    echo     pip install -r requirements.txt
    echo.
    pause
)

