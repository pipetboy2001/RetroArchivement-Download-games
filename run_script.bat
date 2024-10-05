@echo off

REM Verificar si las bibliotecas necesarias están instaladas
python -c "import requests; import rich" 2>nul
IF ERRORLEVEL 1 (
    echo Faltan bibliotecas, instalando...
    pip install requests rich
)

REM Ejecutar el script
python descargar_juego.py
pause
