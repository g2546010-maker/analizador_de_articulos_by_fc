"""
Script para actualizar el campo nombre_normalizado de todos los autores existentes.
Este script debe ejecutarse después de aplicar la migración que agrega el campo.

Uso:
    python scripts/actualizar_nombres_normalizados.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.autor import Autor


def actualizar_nombres():
    """Actualiza el campo nombre_normalizado para todos los autores."""
    app = create_app()
    
    with app.app_context():
        # Obtener todos los autores
        autores = Autor.query.all()
        total = len(autores)
        actualizados = 0
        
        print(f"Procesando {total} autores...")
        
        for autor in autores:
            try:
                # Actualizar el nombre normalizado usando el método del modelo
                autor.actualizar_nombre_normalizado()
                actualizados += 1
                
                if actualizados % 100 == 0:
                    print(f"Procesados {actualizados}/{total} autores...")
                    
            except Exception as e:
                print(f"Error al procesar autor ID {autor.id}: {e}")
        
        # Guardar todos los cambios
        try:
            db.session.commit()
            print(f"\n✓ Actualización completada: {actualizados}/{total} autores")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error al guardar cambios: {e}")
            return False
    
    return True


if __name__ == "__main__":
    if actualizar_nombres():
        print("\nScript ejecutado exitosamente.")
        sys.exit(0)
    else:
        print("\nScript terminó con errores.")
        sys.exit(1)
