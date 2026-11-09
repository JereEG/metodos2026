@echo off
chcp 65001 >nul
title Suite Interactiva de Metodos Computacionales (FaCENA - UNNE)
cd /d "%~dp0"

echo ============================================================================
echo    METODOS COMPUTACIONALES - SUITE EDUCATIVA INTERACTIVA (FaCENA - UNNE)
echo                    Modulos 1 al 7 (Laboratorios 1 al 7)
echo ============================================================================
echo.
echo Iniciando el entorno grafico interactivo...
echo Su navegador web se abrira automaticamente con el Catalogo Principal.
echo (Para finalizar la sesion cuando termine, simplemente cierre esta ventana).
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
    echo Verifique que Python este instalado en el equipo y ejecute por unica vez:
    echo     pip install -r requirements.txt
    echo.
    pause
)
