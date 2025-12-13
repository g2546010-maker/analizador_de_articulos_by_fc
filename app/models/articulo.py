"""
Modelo de Artículo.
Modelo principal del sistema que representa una producción académica.
"""
from datetime import datetime
from app import db


class Articulo(db.Model):
    """
    Modelo principal para representar artículos/producciones académicas.
    Contiene todos los campos necesarios para el Excel del CA.
    """
    __tablename__ = 'articulos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # === Información básica del artículo ===
    titulo = db.Column(db.String(500), nullable=False)
    titulo_revista = db.Column(db.String(300), nullable=True)  # Puede diferir de revista.nombre
    
    # === Clasificación y tipo ===
    tipo_produccion_id = db.Column(db.Integer, db.ForeignKey('tipos_produccion.id'), 
                                    nullable=False)
    proposito_id = db.Column(db.Integer, db.ForeignKey('propositos.id'), nullable=True)
    lgac_id = db.Column(db.Integer, db.ForeignKey('lgac.id'), nullable=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    
    # === Fechas ===
    anio_publicacion = db.Column(db.Integer, nullable=True)
    fecha_publicacion = db.Column(db.Date, nullable=True)
    fecha_aceptacion = db.Column(db.Date, nullable=True)
    
    # === Datos de la publicación ===
    revista_id = db.Column(db.Integer, db.ForeignKey('revistas.id'), nullable=True)
    volumen = db.Column(db.String(20), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    pagina_inicio = db.Column(db.Integer, nullable=True)
    pagina_fin = db.Column(db.Integer, nullable=True)
    
    # === Identificadores ===
    doi = db.Column(db.String(100), nullable=True, unique=True)
    url = db.Column(db.String(500), nullable=True)  # Dirección electrónica del artículo
    issn = db.Column(db.String(20), nullable=True)  # ISSN de la revista (cache)
    
    # === Campos específicos para congresos ===
    nombre_congreso = db.Column(db.String(300), nullable=True)
    
    # === Campos para el CA ===
    para_curriculum = db.Column(db.Boolean, nullable=False, default=True)
    
    # === Indicadores ===
    factor_impacto = db.Column(db.Float, nullable=True)
    quartil = db.Column(db.String(5), nullable=True)  # Q1, Q2, Q3, Q4
    citas = db.Column(db.Integer, nullable=True, default=0)
    
    # === Estado del registro ===
    completo = db.Column(db.Boolean, nullable=False, default=False)
    campos_faltantes = db.Column(db.Text, nullable=True)  # JSON con lista de campos faltantes
    
    # === Archivo fuente ===
    archivo_origen = db.Column(db.String(255), nullable=True)
    
    # === Metadatos ===
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    # === Relaciones ===
    # Relación con TipoProduccion (muchos a uno)
    tipo = db.relationship('TipoProduccion', back_populates='articulos', lazy='joined')
    
    # Relación con Proposito (muchos a uno)
    proposito = db.relationship('Proposito', back_populates='articulos', lazy='joined')
    
    # Relación con LGAC (muchos a uno)
    lgac = db.relationship('LGAC', back_populates='articulos', lazy='joined')
    
    # Relación con Estado (muchos a uno)
    estado = db.relationship('Estado', back_populates='articulos', lazy='joined')
    
    # Relación con Revista (muchos a uno)
    revista = db.relationship('Revista', back_populates='articulos', lazy='joined')
    
    # Nota: Las relaciones N:N con Autores e Indexaciones están definidas
    # en las tablas intermedias ArticuloAutor y ArticuloIndexacion
    # Acceso a autores a través de: articulo.articulo_autores
    # Acceso a indexaciones a través de: articulo.articulo_indexaciones
    
    def __repr__(self):
        return f'<Articulo {self.titulo[:50]}...>'
    
    @property
    def paginas(self):
        """Retorna el rango de páginas formateado."""
        if self.pagina_inicio and self.pagina_fin:
            return f"{self.pagina_inicio}-{self.pagina_fin}"
        elif self.pagina_inicio:
            return str(self.pagina_inicio)
        return None
    
    @property
    def num_paginas(self):
        """Calcula el número de páginas del artículo."""
        if self.pagina_inicio and self.pagina_fin:
            return self.pagina_fin - self.pagina_inicio + 1
        return None
    
    @property
    def es_conference_paper(self):
        """Indica si es un artículo de conferencia."""
        if self.tipo:
            return 'conference' in self.tipo.nombre.lower() or 'congreso' in self.tipo.nombre.lower()
        return False
    
    def to_dict(self, include_relations=False):
        """
        Convierte el artículo a diccionario.
        
        Args:
            include_relations: Si es True, incluye autores e indexaciones.
        """
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'titulo_revista': self.titulo_revista,
            'tipo_produccion_id': self.tipo_produccion_id,
            'tipo_produccion': self.tipo.nombre if self.tipo else None,
            'proposito_id': self.proposito_id,
            'proposito': self.proposito.nombre if self.proposito else None,
            'lgac_id': self.lgac_id,
            'lgac': self.lgac.nombre if self.lgac else None,
            'estado_id': self.estado_id,
            'estado': self.estado.nombre if self.estado else None,
            'anio_publicacion': self.anio_publicacion,
            'fecha_publicacion': self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            'fecha_aceptacion': self.fecha_aceptacion.isoformat() if self.fecha_aceptacion else None,
            'revista_id': self.revista_id,
            'revista': self.revista.nombre if self.revista else None,
            'volumen': self.volumen,
            'numero': self.numero,
            'paginas': self.paginas,
            'pagina_inicio': self.pagina_inicio,
            'pagina_fin': self.pagina_fin,
            'doi': self.doi,
            'url': self.url,
            'issn': self.issn,
            'nombre_congreso': self.nombre_congreso,
            'para_curriculum': self.para_curriculum,
            'factor_impacto': self.factor_impacto,
            'quartil': self.quartil,
            'citas': self.citas,
            'completo': self.completo,
            'campos_faltantes': self.campos_faltantes,
            'archivo_origen': self.archivo_origen,
            'activo': self.activo
        }
        
        if include_relations:
            data['autores'] = [aa.autor.to_dict() for aa in self.articulo_autores]
            # Las indexaciones se obtienen de la revista
            if self.revista:
                data['indexaciones'] = [ri.indexacion.to_dict() 
                                         for ri in self.revista.revista_indexaciones]
        
        return data
    
    def calcular_completitud(self):
        """
        Calcula si el artículo tiene todos los campos obligatorios.
        Retorna True si está completo, False si faltan campos.
        Actualiza el campo campos_faltantes con la lista de campos faltantes.
        """
        import json
        from app.models.relations import ArticuloAutor
        
        campos_obligatorios = [
            ('titulo', 'Título'),
            ('tipo_produccion_id', 'Tipo de producción'),
            ('estado_id', 'Estado'),
            ('anio_publicacion', 'Año de publicación'),
        ]
        
        # Campos adicionales obligatorios para artículos publicados
        if self.estado and self.estado.nombre.lower() == 'publicado':
            campos_obligatorios.extend([
                ('revista_id', 'Revista'),
                ('volumen', 'Volumen'),
                ('numero', 'Número'),
                ('pagina_inicio', 'Página inicio'),
                ('pagina_fin', 'Página fin'),
            ])
        
        # Si es conference paper, el nombre del congreso es obligatorio
        if self.es_conference_paper:
            campos_obligatorios.append(('nombre_congreso', 'Nombre del congreso'))
        
        faltantes = []
        for campo, nombre in campos_obligatorios:
            valor = getattr(self, campo, None)
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                faltantes.append(nombre)
        
        # Verificar que tenga al menos un autor - hacer query directo si el objeto está persistido
        if self.id:
            # Si el artículo ya existe en la DB, hacer un query directo
            num_autores = db.session.query(ArticuloAutor).filter_by(articulo_id=self.id).count()
            if num_autores == 0:
                faltantes.append('Autores')
        else:
            # Si es un objeto nuevo, verificar la relación cargada
            if not hasattr(self, 'articulo_autores') or not self.articulo_autores:
                faltantes.append('Autores')
        
        self.campos_faltantes = json.dumps(faltantes, ensure_ascii=False) if faltantes else None
        self.completo = len(faltantes) == 0
        
        return self.completo
    
    def to_excel_row(self):
        """
        Convierte el artículo al formato de fila para Excel del CA.
        Retorna un diccionario con las columnas del Excel.
        """
        autores_lista = [aa.autor.nombre_completo for aa in self.articulo_autores] if hasattr(self, 'articulo_autores') else []
        
        # Obtener indexaciones de la revista
        indexaciones_lista = []
        if self.revista and hasattr(self.revista, 'revista_indexaciones'):
            indexaciones_lista = [ri.indexacion.nombre for ri in self.revista.revista_indexaciones]
        
        return {
            'Título del artículo': self.titulo,
            'Tipo de producción': self.tipo.nombre if self.tipo else '',
            'Estado': self.estado.nombre if self.estado else '',
            'Propósito': self.proposito.nombre if self.proposito else '',
            'LGAC': self.lgac.nombre if self.lgac else '',
            'Autores': ', '.join(autores_lista),
            'Nombre de la revista': self.revista.nombre if self.revista else self.titulo_revista or '',
            'Volumen': self.volumen or '',
            'Número': self.numero or '',
            'Página inicio': self.pagina_inicio or '',
            'Página fin': self.pagina_fin or '',
            'Año de publicación': self.anio_publicacion or '',
            'Fecha de publicación': self.fecha_publicacion.strftime('%d/%m/%Y') if self.fecha_publicacion else '',
            'ISSN': self.issn or (self.revista.issn if self.revista else ''),
            'País de la revista': self.revista.pais.nombre if self.revista and self.revista.pais else '',
            'DOI': self.doi or '',
            'URL': self.url or '',
            'Indexaciones': ', '.join(indexaciones_lista),
            'Factor de impacto': self.factor_impacto or '',
            'Quartil': self.quartil or '',
            'Nombre del congreso': self.nombre_congreso or '',
            'Para currículum CA': 'Sí' if self.para_curriculum else 'No'
        }
    
    # === Métodos de validación ===
    
    def validar_doi(self):
        """
        Valida que el formato del DOI sea correcto.
        Formato típico: 10.xxxx/xxxxx
        """
        if not self.doi:
            return True
        
        import re
        patron_doi = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
        return bool(re.match(patron_doi, self.doi, re.IGNORECASE))
    
    def validar_issn(self):
        """
        Valida que el formato del ISSN sea correcto.
        Formato: XXXX-XXXX (8 dígitos con guion)
        """
        if not self.issn:
            return True
        
        import re
        patron_issn = r'^\d{4}-\d{3}[\dX]$'
        return bool(re.match(patron_issn, self.issn))
    
    def validar_anio(self):
        """
        Valida que el año de publicación sea razonable.
        Debe estar entre 1900 y el año actual + 2
        """
        if not self.anio_publicacion:
            return True
        
        from datetime import datetime
        anio_actual = datetime.now().year
        return 1900 <= self.anio_publicacion <= anio_actual + 2
    
    def validar_paginas(self):
        """
        Valida que el rango de páginas sea coherente.
        pagina_fin debe ser mayor o igual a pagina_inicio
        """
        if self.pagina_inicio and self.pagina_fin:
            return self.pagina_fin >= self.pagina_inicio
        return True
    
    def validar_quartil(self):
        """
        Valida que el quartil sea uno de los valores permitidos.
        """
        if not self.quartil:
            return True
        
        quartiles_validos = ['Q1', 'Q2', 'Q3', 'Q4']
        return self.quartil.upper() in quartiles_validos
    
    def validar(self):
        """
        Ejecuta todas las validaciones del modelo.
        Retorna (es_valido, lista_errores)
        """
        errores = []
        
        if not self.validar_doi():
            errores.append('El formato del DOI no es válido. Debe ser: 10.xxxx/xxxxx')
        
        if not self.validar_issn():
            errores.append('El formato del ISSN no es válido. Debe ser: XXXX-XXXX')
        
        if not self.validar_anio():
            errores.append('El año de publicación debe estar entre 1900 y el año actual + 2')
        
        if not self.validar_paginas():
            errores.append('La página final debe ser mayor o igual a la página inicial')
        
        if not self.validar_quartil():
            errores.append('El quartil debe ser uno de: Q1, Q2, Q3, Q4')
        
        return len(errores) == 0, errores
    
    # === Métodos de negocio ===
    
    def agregar_autor(self, autor, orden=None, es_corresponsal=False):
        """
        Agrega un autor al artículo.
        
        Args:
            autor: Instancia de Autor
            orden: Orden del autor en la lista (si es None, se asigna el siguiente)
            es_corresponsal: Si es el autor corresponsal
        
        Returns:
            ArticuloAutor creado
        """
        from app.models.relations import ArticuloAutor
        
        if orden is None:
            # Obtener el siguiente orden disponible
            max_orden = db.session.query(db.func.max(ArticuloAutor.orden))\
                .filter_by(articulo_id=self.id)\
                .scalar()
            orden = (max_orden or 0) + 1
        
        articulo_autor = ArticuloAutor(
            articulo_id=self.id,
            autor_id=autor.id,
            orden=orden,
            es_corresponsal=es_corresponsal
        )
        
        db.session.add(articulo_autor)
        return articulo_autor
    
    def remover_autor(self, autor):
        """
        Remueve un autor del artículo y reorganiza los órdenes.
        
        Returns:
            True si el autor fue removido, False si no estaba asociado
        """
        from app.models.relations import ArticuloAutor
        
        # Verificar si existe la asociación antes de eliminarla
        relacion = ArticuloAutor.query.filter_by(
            articulo_id=self.id,
            autor_id=autor.id
        ).first()
        
        if not relacion:
            return False
        
        # Eliminar la relación
        ArticuloAutor.query.filter_by(
            articulo_id=self.id,
            autor_id=autor.id
        ).delete()
        
        # Reorganizar órdenes
        autores = ArticuloAutor.query.filter_by(articulo_id=self.id)\
            .order_by(ArticuloAutor.orden).all()
        
        for idx, aa in enumerate(autores, start=1):
            aa.orden = idx
        
        return True
    
    def agregar_indexacion(self, indexacion, fecha_verificacion=None):
        """
        Agrega una indexación específica al artículo.
        
        Args:
            indexacion: Instancia de Indexacion
            fecha_verificacion: Fecha en que se verificó la indexación
        
        Returns:
            ArticuloIndexacion creado
        """
        from app.models.relations import ArticuloIndexacion
        
        articulo_indexacion = ArticuloIndexacion(
            articulo_id=self.id,
            indexacion_id=indexacion.id,
            fecha_verificacion=fecha_verificacion
        )
        
        db.session.add(articulo_indexacion)
        return articulo_indexacion
    
    def obtener_todas_indexaciones(self):
        """
        Obtiene todas las indexaciones del artículo.
        Combina las indexaciones de la revista y las específicas del artículo.
        
        Returns:
            Lista de objetos Indexacion (sin duplicados)
        """
        indexaciones = set()
        
        # Indexaciones de la revista
        if self.revista:
            for ri in self.revista.revista_indexaciones:
                if ri.activo:
                    indexaciones.add(ri.indexacion)
        
        # Indexaciones específicas del artículo
        for ai in self.articulo_indexaciones:
            indexaciones.add(ai.indexacion)
        
        return list(indexaciones)
    
    @staticmethod
    def buscar(query=None, tipo_id=None, estado_id=None, lgac_id=None, 
               anio=None, autor_id=None, para_curriculum=None):
        """
        Método estático para búsqueda avanzada de artículos.
        
        Args:
            query: Texto a buscar en título o revista
            tipo_id: ID del tipo de producción
            estado_id: ID del estado
            lgac_id: ID de la LGAC
            anio: Año de publicación
            autor_id: ID del autor
            para_curriculum: Filtrar por artículos para currículum
        
        Returns:
            Query de SQLAlchemy (permite agregar más filtros o paginación)
        """
        from app.models.relations import ArticuloAutor
        
        articulos = Articulo.query.filter_by(activo=True)
        
        if query:
            articulos = articulos.filter(
                db.or_(
                    Articulo.titulo.ilike(f'%{query}%'),
                    Articulo.titulo_revista.ilike(f'%{query}%')
                )
            )
        
        if tipo_id:
            articulos = articulos.filter_by(tipo_produccion_id=tipo_id)
        
        if estado_id:
            articulos = articulos.filter_by(estado_id=estado_id)
        
        if lgac_id:
            articulos = articulos.filter_by(lgac_id=lgac_id)
        
        if anio:
            articulos = articulos.filter_by(anio_publicacion=anio)
        
        if autor_id:
            articulos = articulos.join(ArticuloAutor)\
                .filter(ArticuloAutor.autor_id == autor_id)
        
        if para_curriculum is not None:
            articulos = articulos.filter_by(para_curriculum=para_curriculum)
        
        return articulos
