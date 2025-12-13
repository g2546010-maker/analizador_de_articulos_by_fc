"""
Controlador de Artículos.
Maneja toda la lógica de negocio para el CRUD de artículos.
"""
from typing import Optional, Tuple, Dict, Any, List
from flask import flash
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app import db
from app.models import Articulo, Autor, Revista, TipoProduccion, Estado, LGAC, Proposito
from app.models.relations import ArticuloAutor


class ArticleController:
    """Controlador para operaciones CRUD de artículos."""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Tuple[Optional[Articulo], Optional[str]]:
        """
        Crea un nuevo artículo.
        
        Args:
            data: Diccionario con los datos del artículo
            
        Returns:
            Tuple (artículo, error_message)
            - Si exitoso: (articulo, None)
            - Si falla: (None, mensaje_error)
        """
        try:
            # Validar campos obligatorios
            if not data.get('titulo'):
                return None, "El título es obligatorio"
            
            if not data.get('tipo_produccion_id'):
                return None, "El tipo de producción es obligatorio"
            
            if not data.get('estado_id'):
                return None, "El estado es obligatorio"
            
            # Convertir valores vacíos a None para campos opcionales
            for field in ['proposito_id', 'lgac_id', 'revista_id']:
                if field in data and data[field] == 0:
                    data[field] = None
            
            # Validar que existan las referencias
            if data.get('tipo_produccion_id'):
                tipo = TipoProduccion.query.get(data['tipo_produccion_id'])
                if not tipo:
                    return None, "Tipo de producción inválido"
            
            if data.get('estado_id'):
                estado = Estado.query.get(data['estado_id'])
                if not estado:
                    return None, "Estado inválido"
            
            if data.get('proposito_id'):
                proposito = Proposito.query.get(data['proposito_id'])
                if not proposito:
                    return None, "Propósito inválido"
            
            if data.get('lgac_id'):
                lgac = LGAC.query.get(data['lgac_id'])
                if not lgac:
                    return None, "LGAC inválido"
            
            if data.get('revista_id'):
                revista = Revista.query.get(data['revista_id'])
                if not revista:
                    return None, "Revista inválida"
            
            # Validar DOI si está presente
            if data.get('doi'):
                articulo = Articulo(doi=data['doi'])
                if not articulo.validar_doi():
                    return None, "Formato de DOI inválido (debe ser 10.xxxx/xxxxx)"
            
            # Validar ISSN si está presente
            if data.get('issn'):
                articulo = Articulo(issn=data['issn'])
                if not articulo.validar_issn():
                    return None, "Formato de ISSN inválido (debe ser XXXX-XXXX)"
            
            # Validar año si está presente
            if data.get('anio_publicacion'):
                articulo = Articulo(anio_publicacion=data['anio_publicacion'])
                if not articulo.validar_anio():
                    return None, "Año inválido (debe estar entre 1900 y año actual + 1)"
            
            # Validar páginas si están presentes
            if data.get('pagina_inicio') and data.get('pagina_fin'):
                articulo_temp = Articulo(
                    pagina_inicio=data.get('pagina_inicio'),
                    pagina_fin=data.get('pagina_fin')
                )
                if not articulo_temp.validar_paginas():
                    return None, "La página final debe ser mayor o igual a la página inicial"
            
            # Validar quartil si está presente
            if data.get('quartil'):
                articulo = Articulo(quartil=data['quartil'])
                if not articulo.validar_quartil():
                    return None, "Quartil inválido (debe ser Q1, Q2, Q3 o Q4)"
            
            # Crear el artículo
            articulo = Articulo(**data)
            
            db.session.add(articulo)
            db.session.commit()
            
            return articulo, None
            
        except IntegrityError as e:
            db.session.rollback()
            return None, f"Error de integridad: El artículo podría estar duplicado"
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al crear el artículo: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return None, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def get_all(
        page: int = 1,
        per_page: int = 20,
        tipo_id: Optional[int] = None,
        estado_id: Optional[int] = None,
        lgac_id: Optional[int] = None,
        anio: Optional[int] = None,
        autor_id: Optional[int] = None,
        query: Optional[str] = None,
        para_curriculum: Optional[bool] = None
    ) -> Tuple[Any, Optional[str]]:
        """
        Obtiene todos los artículos con paginación y filtros.
        
        Args:
            page: Número de página (1-based)
            per_page: Artículos por página
            tipo_id: Filtrar por tipo de producción
            estado_id: Filtrar por estado
            lgac_id: Filtrar por LGAC
            anio: Filtrar por año
            autor_id: Filtrar por autor
            query: Búsqueda por texto
            para_curriculum: Filtrar por inclusión en curriculum
            
        Returns:
            Tuple (pagination, error_message)
            - Si exitoso: (pagination_object, None)
            - Si falla: (None, mensaje_error)
        """
        try:
            # Validar parámetros
            if page < 1:
                return None, "El número de página debe ser mayor a 0"
            
            if per_page < 1 or per_page > 100:
                return None, "Los artículos por página deben estar entre 1 y 100"
            
            # Construir query usando el método del modelo
            articles_query = Articulo.buscar(
                query=query,
                tipo_id=tipo_id,
                estado_id=estado_id,
                lgac_id=lgac_id,
                anio=anio,
                autor_id=autor_id,
                para_curriculum=para_curriculum
            )
            
            # Ordenar por fecha de creación descendente
            articles_query = articles_query.order_by(Articulo.created_at.desc())
            
            # Paginar usando db.paginate en lugar de query.paginate
            pagination = db.paginate(
                articles_query,
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return pagination, None
            
        except SQLAlchemyError as e:
            return None, f"Error al obtener artículos: {str(e)}"
        
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def get_by_id(article_id: int) -> Tuple[Optional[Articulo], Optional[str]]:
        """
        Obtiene un artículo por su ID.
        
        Args:
            article_id: ID del artículo
            
        Returns:
            Tuple (articulo, error_message)
            - Si exitoso: (articulo, None)
            - Si no existe: (None, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            
            if not articulo:
                return None, f"No se encontró el artículo con ID {article_id}"
            
            return articulo, None
            
        except SQLAlchemyError as e:
            return None, f"Error al obtener el artículo: {str(e)}"
        
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def update(article_id: int, data: Dict[str, Any]) -> Tuple[Optional[Articulo], Optional[str]]:
        """
        Actualiza un artículo existente.
        
        Args:
            article_id: ID del artículo a actualizar
            data: Diccionario con los datos a actualizar
            
        Returns:
            Tuple (articulo, error_message)
            - Si exitoso: (articulo_actualizado, None)
            - Si falla: (None, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            
            if not articulo:
                return None, f"No se encontró el artículo con ID {article_id}"
            
            # Validar campos si están presentes
            if 'titulo' in data and not data['titulo']:
                return None, "El título no puede estar vacío"
            
            # Convertir valores vacíos a None para campos opcionales
            for field in ['proposito_id', 'lgac_id', 'revista_id']:
                if field in data and data[field] == 0:
                    data[field] = None
            
            # Validar referencias si están presentes
            if 'tipo_produccion_id' in data and data['tipo_produccion_id']:
                tipo = TipoProduccion.query.get(data['tipo_produccion_id'])
                if not tipo:
                    return None, "Tipo de producción inválido"
            
            if 'estado_id' in data and data['estado_id']:
                estado = Estado.query.get(data['estado_id'])
                if not estado:
                    return None, "Estado inválido"
            
            if 'proposito_id' in data and data['proposito_id']:
                proposito = Proposito.query.get(data['proposito_id'])
                if not proposito:
                    return None, "Propósito inválido"
            
            if 'lgac_id' in data and data['lgac_id']:
                lgac = LGAC.query.get(data['lgac_id'])
                if not lgac:
                    return None, "LGAC inválido"
            
            if 'revista_id' in data and data['revista_id']:
                revista = Revista.query.get(data['revista_id'])
                if not revista:
                    return None, "Revista inválida"
            
            # Validar DOI si está presente
            if 'doi' in data and data['doi']:
                temp_articulo = Articulo(doi=data['doi'])
                if not temp_articulo.validar_doi():
                    return None, "Formato de DOI inválido (debe ser 10.xxxx/xxxxx)"
            
            # Validar ISSN si está presente
            if 'issn' in data and data['issn']:
                temp_articulo = Articulo(issn=data['issn'])
                if not temp_articulo.validar_issn():
                    return None, "Formato de ISSN inválido (debe ser XXXX-XXXX)"
            
            # Validar año si está presente
            if 'anio_publicacion' in data and data['anio_publicacion']:
                temp_articulo = Articulo(anio_publicacion=data['anio_publicacion'])
                if not temp_articulo.validar_anio():
                    return None, "Año inválido (debe estar entre 1900 y año actual + 1)"
            
            # Validar páginas si están presentes
            pagina_inicio = data.get('pagina_inicio', articulo.pagina_inicio)
            pagina_fin = data.get('pagina_fin', articulo.pagina_fin)
            
            if pagina_inicio and pagina_fin:
                articulo_temp = Articulo(
                    pagina_inicio=pagina_inicio,
                    pagina_fin=pagina_fin
                )
                if not articulo_temp.validar_paginas():
                    return None, "La página final debe ser mayor o igual a la página inicial"
            
            # Validar quartil si está presente
            if 'quartil' in data and data['quartil']:
                temp_articulo = Articulo(quartil=data['quartil'])
                if not temp_articulo.validar_quartil():
                    return None, "Quartil inválido (debe ser Q1, Q2, Q3 o Q4)"
            
            # Actualizar campos
            for key, value in data.items():
                if hasattr(articulo, key):
                    setattr(articulo, key, value)
            
            db.session.commit()
            
            return articulo, None
            
        except IntegrityError as e:
            db.session.rollback()
            return None, "Error de integridad al actualizar el artículo"
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al actualizar el artículo: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return None, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def delete(article_id: int, soft: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Elimina un artículo (lógica o física).
        
        Args:
            article_id: ID del artículo a eliminar
            soft: Si True, eliminación lógica (marcar como inactivo)
                  Si False, eliminación física (borrar de DB)
            
        Returns:
            Tuple (success, error_message)
            - Si exitoso: (True, None)
            - Si falla: (False, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            
            if not articulo:
                return False, f"No se encontró el artículo con ID {article_id}"
            
            if soft:
                # Eliminación lógica - marcar como inactivo
                articulo.activo = False
                db.session.commit()
            else:
                # Eliminación física - borrar de la base de datos
                # Primero eliminar las relaciones N:N
                ArticuloAutor.query.filter_by(articulo_id=article_id).delete()
                
                # Eliminar el artículo
                db.session.delete(articulo)
                db.session.commit()
            
            return True, None
            
        except IntegrityError as e:
            db.session.rollback()
            return False, "No se puede eliminar el artículo debido a referencias en otras tablas"
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al eliminar el artículo: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def restore(article_id: int) -> Tuple[Optional[Articulo], Optional[str]]:
        """
        Restaura un artículo eliminado lógicamente.
        
        Args:
            article_id: ID del artículo a restaurar
            
        Returns:
            Tuple (articulo, error_message)
            - Si exitoso: (articulo, None)
            - Si falla: (None, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            
            if not articulo:
                return None, f"No se encontró el artículo con ID {article_id}"
            
            articulo.activo = True
            db.session.commit()
            
            return articulo, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al restaurar el artículo: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return None, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def add_author(
        article_id: int,
        author_id: int,
        orden: int = 1,
        es_corresponsal: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Agrega un autor a un artículo.
        
        Args:
            article_id: ID del artículo
            author_id: ID del autor
            orden: Orden del autor en la lista
            es_corresponsal: Si es autor corresponsal
            
        Returns:
            Tuple (success, error_message)
            - Si exitoso: (True, None)
            - Si falla: (False, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            if not articulo:
                return False, f"No se encontró el artículo con ID {article_id}"
            
            autor = Autor.query.get(author_id)
            if not autor:
                return False, f"No se encontró el autor con ID {author_id}"
            
            # Verificar si ya existe la relación
            relacion = ArticuloAutor.query.filter_by(
                articulo_id=article_id,
                autor_id=author_id
            ).first()
            
            if relacion:
                return False, "El autor ya está asociado a este artículo"
            
            # Agregar el autor usando el método del modelo
            articulo.agregar_autor(autor, orden, es_corresponsal)
            db.session.commit()
            
            return True, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al agregar el autor: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def remove_author(article_id: int, author_id: int) -> Tuple[bool, Optional[str]]:
        """
        Remueve un autor de un artículo.
        
        Args:
            article_id: ID del artículo
            author_id: ID del autor
            
        Returns:
            Tuple (success, error_message)
            - Si exitoso: (True, None)
            - Si falla: (False, mensaje_error)
        """
        try:
            articulo = Articulo.query.get(article_id)
            if not articulo:
                return False, f"No se encontró el artículo con ID {article_id}"
            
            autor = Autor.query.get(author_id)
            if not autor:
                return False, f"No se encontró el autor con ID {author_id}"
            
            # Remover el autor usando el método del modelo
            result = articulo.remover_autor(autor)
            
            if not result:
                return False, "El autor no está asociado a este artículo"
            
            db.session.commit()
            
            return True, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al remover el autor: {str(e)}"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error inesperado: {str(e)}"
    
    @staticmethod
    def get_statistics() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Obtiene estadísticas generales de artículos.
        
        Returns:
            Tuple (statistics, error_message)
            - Si exitoso: (dict_with_stats, None)
            - Si falla: (None, mensaje_error)
        """
        try:
            stats = {
                'total': Articulo.query.filter_by(activo=True).count(),
                'por_tipo': {},
                'por_estado': {},
                'por_anio': {},
                'publicados': Articulo.query.join(Estado).filter(
                    Articulo.activo == True,
                    Estado.nombre == 'Publicado'
                ).count(),
                'para_curriculum': Articulo.query.filter_by(
                    activo=True,
                    para_curriculum=True
                ).count()
            }
            
            # Estadísticas por tipo
            tipos = db.session.query(
                TipoProduccion.nombre,
                db.func.count(Articulo.id)
            ).join(Articulo).filter(Articulo.activo == True).group_by(
                TipoProduccion.nombre
            ).all()
            
            stats['por_tipo'] = {tipo: count for tipo, count in tipos}
            
            # Estadísticas por estado
            estados = db.session.query(
                Estado.nombre,
                db.func.count(Articulo.id)
            ).join(Articulo).filter(Articulo.activo == True).group_by(
                Estado.nombre
            ).all()
            
            stats['por_estado'] = {estado: count for estado, count in estados}
            
            # Estadísticas por año
            anios = db.session.query(
                Articulo.anio_publicacion,
                db.func.count(Articulo.id)
            ).filter(
                Articulo.activo == True,
                Articulo.anio_publicacion.isnot(None)
            ).group_by(Articulo.anio_publicacion).order_by(
                Articulo.anio_publicacion.desc()
            ).limit(10).all()
            
            stats['por_anio'] = {anio: count for anio, count in anios if anio}
            
            return stats, None
            
        except SQLAlchemyError as e:
            return None, f"Error al obtener estadísticas: {str(e)}"
        
        except Exception as e:
            return None, f"Error inesperado: {str(e)}"
