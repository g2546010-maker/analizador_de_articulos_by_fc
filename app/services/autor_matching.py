"""
Servicio para matching y deduplicación de autores.
Maneja diferentes formatos de nombres y encuentra coincidencias.
"""
import re
from app.models import Autor
from app import db


class AutorMatchingService:
    """
    Servicio para identificar y evitar duplicados de autores.
    Maneja múltiples formatos de nombres.
    """
    
    @staticmethod
    def parsear_nombre_autor(texto):
        """
        Parsea diferentes formatos de nombres a (nombre, apellidos).
        
        Formatos soportados:
        - "Francisco Comparan Pantoja" -> ("Francisco", "Comparan Pantoja")
        - "Comparan Pantoja, Francisco" -> ("Francisco", "Comparan Pantoja")
        - "Comparan-Pantoja, F." -> ("F", "Comparan Pantoja")
        - "F. Comparan Pantoja" -> ("F", "Comparan Pantoja")
        
        Returns:
            tuple: (nombre, apellidos)
        """
        if not texto:
            return ("", "")
        
        texto = texto.strip()
        
        # Formato: "Apellidos, Nombre"
        if ',' in texto:
            partes = texto.split(',', 1)
            apellidos = partes[0].strip().replace('-', ' ')
            nombre = partes[1].strip()
            return (nombre, apellidos)
        
        # Formato: "Nombre Apellidos" (asume último token es apellido)
        partes = texto.split()
        if len(partes) == 1:
            return (partes[0], "")
        
        # Si empieza con inicial (ej: "F. Comparan Pantoja")
        if len(partes[0]) <= 2 and partes[0].endswith('.'):
            nombre = partes[0]
            apellidos = ' '.join(partes[1:])
            return (nombre, apellidos)
        
        # Caso general: primer token es nombre, resto son apellidos
        nombre = partes[0]
        apellidos = ' '.join(partes[1:])
        
        return (nombre, apellidos)
    
    @staticmethod
    def encontrar_o_crear_autor(texto_nombre, orcid=None, email=None, crear_si_no_existe=True):
        """
        Busca un autor existente o crea uno nuevo.
        
        Estrategia de búsqueda (en orden):
        1. Por ORCID (si se proporciona)
        2. Por email (si se proporciona)
        3. Por fuzzy matching del nombre completo
        4. Si no encuentra y crear_si_no_existe=True, crea uno nuevo
        
        Args:
            texto_nombre: Nombre en cualquier formato
            orcid: ORCID del autor (opcional)
            email: Email del autor (opcional)
            crear_si_no_existe: Si crear nuevo autor si no se encuentra
        
        Returns:
            Autor: Instancia del autor (existente o nuevo)
            bool: True si es nuevo, False si ya existía
        """
        # 1. Buscar por identificador único
        autor = Autor.buscar_por_identificador(orcid=orcid, email=email)
        if autor:
            return autor, False
        
        # 2. Buscar por fuzzy matching
        resultados = Autor.buscar_fuzzy(texto_nombre, umbral=85)
        if resultados:
            # Retornar el mejor match
            mejor_autor, score = resultados[0]
            print(f"✓ Match encontrado: '{texto_nombre}' -> '{mejor_autor.nombre_completo}' (score: {score})")
            return mejor_autor, False
        
        # 3. No encontrado, crear nuevo si se permite
        if not crear_si_no_existe:
            return None, False
        
        nombre, apellidos = AutorMatchingService.parsear_nombre_autor(texto_nombre)
        
        # Verificar si ya existe con nombre exacto
        autor_exacto = Autor.buscar_por_nombre(nombre, apellidos)
        if autor_exacto:
            return autor_exacto, False
        
        # Crear nuevo autor
        nuevo_autor = Autor(
            nombre=nombre,
            apellidos=apellidos,
            orcid=orcid,
            email=email,
            activo=True
        )
        nuevo_autor.actualizar_nombre_normalizado()
        
        db.session.add(nuevo_autor)
        
        print(f"✓ Nuevo autor creado: '{nuevo_autor.nombre_completo}'")
        return nuevo_autor, True
    
    @staticmethod
    def detectar_duplicados(umbral=90):
        """
        Detecta posibles autores duplicados en la base de datos.
        
        Args:
            umbral: Porcentaje de similitud para considerar duplicado
        
        Returns:
            list: Lista de tuplas (autor1, autor2, score)
        """
        autores = Autor.query.filter_by(activo=True).all()
        duplicados = []
        
        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            print("⚠️  Instala 'fuzzywuzzy' para detección de duplicados: pip install fuzzywuzzy python-Levenshtein")
            return []
        
        # Comparar cada par de autores
        for i, autor1 in enumerate(autores):
            for autor2 in autores[i+1:]:
                if not autor1.nombre_normalizado or not autor2.nombre_normalizado:
                    continue
                
                score = fuzz.token_sort_ratio(
                    autor1.nombre_normalizado,
                    autor2.nombre_normalizado
                )
                
                if score >= umbral:
                    duplicados.append((autor1, autor2, score))
        
        # Ordenar por score descendente
        duplicados.sort(key=lambda x: x[2], reverse=True)
        
        return duplicados
    
    @staticmethod
    def fusionar_autores(autor_principal_id, autor_duplicado_id):
        """
        Fusiona dos autores, moviendo todos los artículos del duplicado al principal.
        
        Args:
            autor_principal_id: ID del autor a mantener
            autor_duplicado_id: ID del autor a eliminar (marcar como inactivo)
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        from app.models import ArticuloAutor
        
        autor_principal = Autor.query.get(autor_principal_id)
        autor_duplicado = Autor.query.get(autor_duplicado_id)
        
        if not autor_principal or not autor_duplicado:
            return False, "Autor no encontrado"
        
        if autor_principal.id == autor_duplicado.id:
            return False, "No se puede fusionar un autor consigo mismo"
        
        try:
            # Mover todas las relaciones de artículos
            relaciones = ArticuloAutor.query.filter_by(autor_id=autor_duplicado.id).all()
            
            for relacion in relaciones:
                # Verificar si ya existe relación para evitar duplicados
                existe = ArticuloAutor.query.filter_by(
                    articulo_id=relacion.articulo_id,
                    autor_id=autor_principal.id
                ).first()
                
                if not existe:
                    relacion.autor_id = autor_principal.id
                else:
                    # Si ya existe, eliminar la relación duplicada
                    db.session.delete(relacion)
            
            # Copiar información adicional si el principal no la tiene
            if not autor_principal.orcid and autor_duplicado.orcid:
                autor_principal.orcid = autor_duplicado.orcid
            
            if not autor_principal.email and autor_duplicado.email:
                autor_principal.email = autor_duplicado.email
            
            if not autor_principal.registro and autor_duplicado.registro:
                autor_principal.registro = autor_duplicado.registro
            
            # Marcar duplicado como inactivo
            autor_duplicado.activo = False
            
            db.session.commit()
            
            return True, f"Fusión exitosa: {len(relaciones)} artículos movidos"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error al fusionar: {str(e)}"
