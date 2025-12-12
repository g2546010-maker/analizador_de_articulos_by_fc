"""
Modelo de Autor.
Representa a los autores de artículos académicos.
"""
from datetime import datetime
from app import db


class Autor(db.Model):
    """
    Modelo para representar autores de artículos.
    Un autor puede pertenecer a múltiples artículos (relación N:N).
    """
    __tablename__ = 'autores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    
    # Identificadores únicos para matching confiable
    orcid = db.Column(db.String(19), nullable=True, unique=True)  # Formato: 0000-0002-1825-0097
    
    # Número de registro institucional (para miembros del CA)
    registro = db.Column(db.String(50), nullable=True)
    
    # Indica si es miembro activo del Cuerpo Académico
    es_miembro_ca = db.Column(db.Boolean, nullable=False, default=False)
    
    # Nombre normalizado para búsquedas (sin acentos, minúsculas, sin guiones)
    nombre_normalizado = db.Column(db.String(250), nullable=True, index=True)
    
    # Estado del registro
    activo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Autor {self.nombre_completo}>'
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del autor."""
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def nombre_formato_cita(self):
        """Retorna el nombre en formato de cita: Apellidos, N."""
        inicial = self.nombre[0].upper() if self.nombre else ''
        return f"{self.apellidos}, {inicial}."
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'registro': self.registro,
            'es_miembro_ca': self.es_miembro_ca,
            'activo': self.activo
        }
    
    @staticmethod
    def normalizar_texto(texto):
        """
        Normaliza texto para búsqueda: sin acentos, minúsculas, sin caracteres especiales.
        Ejemplo: "Comparán-Pantoja, Francisco" -> "comparan pantoja francisco"
        """
        import unicodedata
        import re
        
        if not texto:
            return ""
        
        # Remover acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('utf-8')
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover puntuación y caracteres especiales, dejar solo letras y espacios
        texto = re.sub(r'[^a-z\s]', ' ', texto)
        
        # Normalizar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    @staticmethod
    def buscar_por_nombre(nombre, apellidos):
        """
        Busca un autor por nombre y apellidos (búsqueda exacta).
        Útil para evitar duplicados al importar.
        """
        return Autor.query.filter(
            db.func.lower(Autor.nombre) == db.func.lower(nombre),
            db.func.lower(Autor.apellidos) == db.func.lower(apellidos)
        ).first()
    
    @staticmethod
    def buscar_por_identificador(orcid=None, email=None, registro=None):
        """
        Busca autor por identificador único (ORCID, email o registro).
        Retorna el primer match encontrado.
        """
        if orcid:
            autor = Autor.query.filter_by(orcid=orcid).first()
            if autor:
                return autor
        
        if email:
            autor = Autor.query.filter_by(email=email).first()
            if autor:
                return autor
        
        if registro:
            autor = Autor.query.filter_by(registro=registro).first()
            if autor:
                return autor
        
        return None
    
    @staticmethod
    def buscar_fuzzy(texto_nombre, umbral=80):
        """
        Busca autores usando fuzzy matching sobre nombres normalizados.
        Retorna lista de tuplas (autor, score) ordenadas por similitud.
        
        Args:
            texto_nombre: Texto a buscar (cualquier formato)
            umbral: Porcentaje mínimo de similitud (0-100)
        
        Returns:
            Lista de tuplas (Autor, score) con score >= umbral
        """
        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            # Si no está instalada la librería, hacer búsqueda simple
            return []
        
        # Normalizar el texto de búsqueda
        texto_normalizado = Autor.normalizar_texto(texto_nombre)
        
        # Obtener todos los autores activos
        autores = Autor.query.filter_by(activo=True).all()
        
        resultados = []
        for autor in autores:
            # Calcular similitud con el nombre completo normalizado
            score = fuzz.token_sort_ratio(texto_normalizado, autor.nombre_normalizado or "")
            
            if score >= umbral:
                resultados.append((autor, score))
        
        # Ordenar por score descendente
        resultados.sort(key=lambda x: x[1], reverse=True)
        
        return resultados
    
    def actualizar_nombre_normalizado(self):
        """Actualiza el campo nombre_normalizado basado en nombre y apellidos."""
        texto_completo = f"{self.nombre} {self.apellidos}"
        self.nombre_normalizado = self.normalizar_texto(texto_completo)
