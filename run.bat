@echo off
:: Calculadora de Valor Hora/Aula - Launcher

echo.
echo ====================================
echo  Calculadora de Valor Hora/Aula
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python nao foi encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install requirements if needed
pip list | findstr "PyQt5" >nul
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

:: Run the application
echo.
echo Iniciando aplicacao...
echo.
python main.py

pause

