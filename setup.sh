#!/bin/bash
# Script de inicialización rápida para Linux/Mac

echo "============================================================"
echo "  Inicializando Proyecto - Sistema de Gestión de Artículos"
echo "============================================================"
echo ""

# 1. Crear ambiente virtual si no existe
if [ ! -d "venv" ]; then
    echo "[1/4] Creando ambiente virtual con Python 3.12..."
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv venv
        echo "    ✓ Ambiente virtual creado con Python 3.12"
    else
        echo "    ERROR: Python 3.12 no encontrado. Instala Python 3.12 o usa: python3 -m venv venv"
        exit 1
    fi
else
    echo "[1/4] Ambiente virtual ya existe"
fi
echo ""

# 2. Activar ambiente e instalar dependencias
echo "[2/4] Instalando dependencias..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "    ✓ Dependencias instaladas"
echo ""

# 3. Inicializar base de datos
echo "[3/4] Inicializando base de datos..."
if [ -f "articulos.db" ]; then
    echo "    Base de datos ya existe, aplicando migraciones..."
    export FLASK_APP=run.py
    flask db upgrade
else
    echo "    Creando nueva base de datos..."
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('    ✓ Base de datos creada')"
fi
echo ""

# 4. Poblar catálogos
echo "[4/4] Poblando catálogos iniciales..."
python scripts/seed_catalogs.py
echo ""

echo "============================================================"
echo "  ✓ Proyecto inicializado correctamente"
echo "============================================================"
echo ""
echo "Para ejecutar la aplicación:"
echo "  1. Activa el ambiente virtual: source venv/bin/activate"
echo "  2. Ejecuta el servidor: python run.py"
echo "  3. Abre tu navegador en: http://localhost:5000"
echo ""
