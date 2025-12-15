"""
Controlador para generación de reportes y exportaciones.
"""
from typing import List, Optional, Dict, Any
from flask import send_file
from sqlalchemy import or_, and_
from app.models.articulo import Articulo
from app.models.autor import Autor
from app.models.catalogs import (
    TipoProduccion, Estado, LGAC, Proposito, Indexacion, Pais
)
from app.models.revista import Revista
from app.services.excel_service import ExcelService
from app import db
import logging

logger = logging.getLogger(__name__)


class ReportController:
    """Controlador para manejo de reportes y exportaciones."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.excel_service = ExcelService()
        self.logger = logger
    
    def export_excel(self, filters: Optional[Dict[str, Any]] = None) -> tuple:
        """
        Exporta artículos a Excel aplicando filtros opcionales.
        
        Args:
            filters: Diccionario con filtros a aplicar:
                - search: Búsqueda por texto en título o revista
                - anio_inicio: Año de publicación desde
                - anio_fin: Año de publicación hasta
                - tipo_produccion_id: ID del tipo de producción
                - estado_id: ID del estado
                - lgac_id: ID de la LGAC
                - autor_id: ID del autor
                - para_curriculum: True/False
                - completo: True/False
                - activo: True/False (default True)
        
        Returns:
            Tupla (BytesIO, filename) con el archivo Excel y su nombre
        """
        try:
            # Construir query con filtros
            articulos = self._build_filtered_query(filters)
            
            # Generar archivo Excel
            excel_file = self.excel_service.generate(articulos)
            
            # Generar nombre de archivo
            filename = self._generate_filename(filters)
            
            self.logger.info(f"Reporte generado: {len(articulos)} artículos")
            
            return excel_file, filename
            
        except Exception as e:
            self.logger.error(f"Error generando reporte Excel: {str(e)}")
            raise
    
    def _build_filtered_query(self, filters: Optional[Dict[str, Any]] = None) -> List[Articulo]:
        """
        Construye query con filtros aplicados.
        
        Args:
            filters: Diccionario con filtros
            
        Returns:
            Lista de artículos filtrados
        """
        query = Articulo.query
        
        # Filtros por defecto
        if filters is None:
            filters = {}
        
        # Filtro de activos (por defecto True)
        if filters.get('activo', True):
            query = query.filter(Articulo.activo == True)
        
        # Búsqueda por texto
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Articulo.titulo.ilike(search_term),
                    Articulo.titulo_revista.ilike(search_term)
                )
            )
        
        # Filtro por rango de años
        if filters.get('anio_inicio'):
            query = query.filter(Articulo.anio_publicacion >= filters['anio_inicio'])
        
        if filters.get('anio_fin'):
            query = query.filter(Articulo.anio_publicacion <= filters['anio_fin'])
        
        # Filtro por tipo de producción
        if filters.get('tipo_produccion_id'):
            query = query.filter(Articulo.tipo_produccion_id == filters['tipo_produccion_id'])
        
        # Filtro por estado
        if filters.get('estado_id'):
            query = query.filter(Articulo.estado_id == filters['estado_id'])
        
        # Filtro por LGAC
        if filters.get('lgac_id'):
            query = query.join(Articulo.lgacs).filter(LGAC.id == filters['lgac_id'])
        
        # Filtro por autor
        if filters.get('autor_id'):
            query = query.join(Articulo.articulo_autores).filter(
                Articulo.articulo_autores.any(autor_id=filters['autor_id'])
            )
        
        # Filtro por indexación
        if filters.get('indexacion_id'):
            query = query.join(Articulo.indexaciones).filter(
                Indexacion.id == filters['indexacion_id']
            )
        
        # Filtro para currículum
        if filters.get('para_curriculum') is not None:
            query = query.filter(Articulo.para_curriculum == filters['para_curriculum'])
        
        # Filtro por completitud
        if filters.get('completo') is not None:
            query = query.filter(Articulo.completo == filters['completo'])
        
        # Ordenar por año descendente y título
        query = query.order_by(
            Articulo.anio_publicacion.desc().nullslast(),
            Articulo.titulo
        )
        
        # Eager loading de relaciones para evitar N+1 queries
        # Nota: no se puede hacer joinedload en backrefs dinámicos, se cargan bajo demanda
        query = query.options(
            db.joinedload(Articulo.tipo),
            db.joinedload(Articulo.estado),
            db.joinedload(Articulo.revista),
            db.joinedload(Articulo.lgac),
            db.joinedload(Articulo.proposito)
        )
        
        return query.all()
    
    def _generate_filename(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Genera nombre descriptivo para el archivo según filtros aplicados.
        
        Args:
            filters: Diccionario con filtros aplicados
            
        Returns:
            Nombre de archivo descriptivo
        """
        prefix_parts = ['articulos']
        
        if filters:
            # Agregar información de filtros al nombre
            if filters.get('anio_inicio') and filters.get('anio_fin'):
                prefix_parts.append(f"{filters['anio_inicio']}-{filters['anio_fin']}")
            elif filters.get('anio_inicio'):
                prefix_parts.append(f"desde_{filters['anio_inicio']}")
            elif filters.get('anio_fin'):
                prefix_parts.append(f"hasta_{filters['anio_fin']}")
            
            if filters.get('tipo_produccion_id'):
                try:
                    tipo = TipoProduccion.query.get(filters['tipo_produccion_id'])
                    if tipo:
                        # Sanitizar nombre para filename
                        tipo_nombre = tipo.nombre.lower().replace(' ', '_')
                        prefix_parts.append(tipo_nombre)
                except:
                    pass
            
            if filters.get('estado_id'):
                try:
                    estado = Estado.query.get(filters['estado_id'])
                    if estado:
                        estado_nombre = estado.nombre.lower().replace(' ', '_')
                        prefix_parts.append(estado_nombre)
                except:
                    pass
            
            if filters.get('para_curriculum'):
                prefix_parts.append('curriculum')
            
            if filters.get('completo') is False:
                prefix_parts.append('incompletos')
        
        prefix = '_'.join(prefix_parts)
        return self.excel_service.generate_filename(prefix)
    
    def get_export_statistics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los artículos que se exportarían.
        
        Args:
            filters: Diccionario con filtros
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            articulos = self._build_filtered_query(filters)
            
            # Calcular estadísticas
            total = len(articulos)
            completos = sum(1 for a in articulos if a.completo)
            incompletos = total - completos
            para_curriculum = sum(1 for a in articulos if a.para_curriculum)
            
            # Por año
            por_anio = {}
            for a in articulos:
                if a.anio_publicacion:
                    por_anio[a.anio_publicacion] = por_anio.get(a.anio_publicacion, 0) + 1
            
            # Por tipo de producción
            por_tipo = {}
            for a in articulos:
                if a.tipo:
                    tipo = a.tipo.nombre
                    por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
            
            # Por estado
            por_estado = {}
            for a in articulos:
                if a.estado:
                    estado = a.estado.nombre
                    por_estado[estado] = por_estado.get(estado, 0) + 1
            
            return {
                'total': total,
                'completos': completos,
                'incompletos': incompletos,
                'para_curriculum': para_curriculum,
                'por_anio': dict(sorted(por_anio.items(), reverse=True)),
                'por_tipo': por_tipo,
                'por_estado': por_estado
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando estadísticas: {str(e)}")
            return {
                'total': 0,
                'error': str(e)
            }
