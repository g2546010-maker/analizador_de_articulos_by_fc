@echo off
REM Script de inicialización rápida para Windows
echo ============================================================
echo   Inicializando Proyecto - Sistema de Gestión de Artículos
echo ============================================================
echo.

REM 1. Crear ambiente virtual si no existe
if not exist venv (
    echo [1/4] Creando ambiente virtual con Python 3.12...
    py -3.12 -m venv venv
    if errorlevel 1 (
        echo     ERROR: Python 3.12 no encontrado. Instala Python 3.12 desde python.org
        pause
        exit /b 1
    )
    echo     ✓ Ambiente virtual creado con Python 3.12
) else (
    echo [1/4] Ambiente virtual ya existe
)
echo.

REM 2. Activar ambiente e instalar dependencias
echo [2/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo     ✓ Dependencias instaladas
echo.

REM 3. Inicializar base de datos
echo [3/4] Inicializando base de datos...
if exist articulos.db (
    echo     Base de datos ya existe, aplicando migraciones...
    set FLASK_APP=run.py
    flask db upgrade
) else (
    echo     Creando nueva base de datos...
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('     ✓ Base de datos creada')"
)
echo.

REM 4. Poblar catálogos
echo [4/4] Poblando catálogos iniciales...
python scripts\seed_catalogs.py
echo.

echo ============================================================
echo   ✓ Proyecto inicializado correctamente
echo ============================================================
echo.
echo Para ejecutar la aplicación:
echo   1. Activa el ambiente virtual: venv\Scripts\activate
echo   2. Ejecuta el servidor: python run.py
echo   3. Abre tu navegador en: http://localhost:5000
echo.
pause
