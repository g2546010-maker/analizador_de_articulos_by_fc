"""
Servicio para extraer metadatos de archivos PDF.
Soporta múltiples estrategias de extracción para manejar diferentes formatos.
"""
import re
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime

# Librerías de extracción de PDF
import PyPDF2
import pdfplumber
import pikepdf

# Configurar logging
logger = logging.getLogger(__name__)


class PDFService:
    """
    Servicio para extraer metadatos de archivos PDF académicos.
    Utiliza múltiples estrategias para maximizar la tasa de éxito.
    """
    
    # Patrones regex para extracción
    DOI_PATTERN = re.compile(
        r'(?:doi[:\s]*|https?://(?:dx\.)?doi\.org/)?(10\.\d{4,}/[^\s]+)',
        re.IGNORECASE
    )
    
    ISSN_PATTERN = re.compile(
        r'ISSN[:\s]*(\d{4}[-\s]?\d{3}[\dXx])',
        re.IGNORECASE
    )
    
    YEAR_PATTERN = re.compile(
        r'\b(19\d{2}|20[0-2]\d)\b'
    )
    
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    # Palabras clave para identificar secciones
    ABSTRACT_KEYWORDS = [
        'abstract', 'resumen', 'resumo', 'résumé',
        'summary', 'síntesis'
    ]
    
    KEYWORDS_SECTION = [
        'keywords', 'palabras clave', 'key words',
        'palabras-clave', 'términos', 'descriptores'
    ]
    
    INTRODUCTION_KEYWORDS = [
        'introduction', 'introducción', 'introdução',
        '1. introduction', '1 introduction'
    ]
    
    def __init__(self):
        """Inicializa el servicio de extracción PDF"""
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, pdf_path: str, max_pages: int = 5) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Extrae texto de un PDF usando múltiples estrategias.
        
        Args:
            pdf_path: Ruta al archivo PDF
            max_pages: Máximo de páginas a extraer (optimización)
            
        Returns:
            Tupla (exito, texto_extraido, mensaje_error)
        """
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            return False, None, f"Archivo no encontrado: {pdf_path}"
        
        if not pdf_file.suffix.lower() == '.pdf':
            return False, None, "El archivo no es un PDF"
        
        # Estrategia 1: pdfplumber (mejor para texto estructurado)
        try:
            text = self._extract_with_pdfplumber(pdf_path, max_pages)
            if text and len(text) > 100:
                return True, text, None
        except Exception as e:
            self.logger.warning(f"pdfplumber falló: {e}")
        
        # Estrategia 2: PyPDF2 (fallback)
        try:
            text = self._extract_with_pypdf2(pdf_path, max_pages)
            if text and len(text) > 100:
                return True, text, None
        except Exception as e:
            self.logger.warning(f"PyPDF2 falló: {e}")
        
        # Estrategia 3: pikepdf (para PDFs complejos)
        try:
            text = self._extract_with_pikepdf(pdf_path, max_pages)
            if text and len(text) > 100:
                return True, text, None
        except Exception as e:
            self.logger.warning(f"pikepdf falló: {e}")
        
        return False, None, "No se pudo extraer texto del PDF. Puede estar protegido o ser una imagen."
    
    def _extract_with_pdfplumber(self, pdf_path: str, max_pages: int) -> Optional[str]:
        """Extrae texto usando pdfplumber"""
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts) if text_parts else None
    
    def _extract_with_pypdf2(self, pdf_path: str, max_pages: int) -> Optional[str]:
        """Extrae texto usando PyPDF2"""
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = min(len(reader.pages), max_pages)
            
            for i in range(num_pages):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts) if text_parts else None
    
    def _extract_with_pikepdf(self, pdf_path: str, max_pages: int) -> Optional[str]:
        """Extrae texto usando pikepdf"""
        text_parts = []
        
        with pikepdf.open(pdf_path) as pdf:
            num_pages = min(len(pdf.pages), max_pages)
            
            for i in range(num_pages):
                page = pdf.pages[i]
                # pikepdf requiere procesamiento adicional
                # Esta es una implementación simplificada
                try:
                    if '/Contents' in page:
                        content = str(page.Contents.read_bytes())
                        text_parts.append(content)
                except:
                    continue
        
        return '\n\n'.join(text_parts) if text_parts else None
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, any]:
        """
        Extrae todos los metadatos posibles de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con metadatos extraídos
        """
        result = {
            'titulo': None,
            'autores': [],
            'anio_publicacion': None,
            'doi': None,
            'issn': None,
            'resumen': None,
            'palabras_clave': [],
            'emails': [],
            'success': False,
            'error': None,
            'confidence': 0.0  # Nivel de confianza (0-1)
        }
        
        # Extraer texto
        success, text, error = self.extract_text(pdf_path)
        
        if not success:
            result['error'] = error
            return result
        
        result['success'] = True
        
        # Extraer cada campo
        result['titulo'] = self.extract_title(text)
        result['autores'] = self.extract_authors(text)
        result['anio_publicacion'] = self.extract_year(text)
        result['doi'] = self.extract_doi(text)
        result['issn'] = self.extract_issn(text)
        result['resumen'] = self.extract_abstract(text)
        result['palabras_clave'] = self.extract_keywords(text)
        result['emails'] = self.extract_emails(text)
        
        # Calcular nivel de confianza basado en campos encontrados
        fields_found = sum([
            bool(result['titulo']),
            bool(result['autores']),
            bool(result['anio_publicacion']),
            bool(result['doi']),
            bool(result['issn']),
            bool(result['resumen'])
        ])
        result['confidence'] = fields_found / 6.0
        
        return result
    
    def extract_title(self, text: str) -> Optional[str]:
        """
        Extrae el título del artículo.
        Estrategia: El título suele estar en las primeras líneas, en mayúsculas o negrita.
        """
        if not text:
            return None
        
        lines = text.split('\n')
        title_candidates = []
        
        # Buscar en las primeras 20 líneas
        for i, line in enumerate(lines[:20]):
            line = line.strip()
            
            # Ignorar líneas muy cortas o muy largas
            if len(line) < 10 or len(line) > 200:
                continue
            
            # Ignorar líneas que parecen ser encabezados de revista
            if any(keyword in line.lower() for keyword in ['issn', 'volume', 'journal', 'revista', 'doi']):
                continue
            
            # El título suele estar en mayúsculas o ser la línea más larga
            if line.isupper() or len(line) > 30:
                title_candidates.append((i, line, len(line)))
        
        # Retornar el candidato más largo en las primeras posiciones
        if title_candidates:
            title_candidates.sort(key=lambda x: (x[0] * -1, x[2]), reverse=True)
            return title_candidates[0][1]
        
        # Fallback: primera línea significativa
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 20 and not line.startswith(('http', 'www', 'doi')):
                return line
        
        return None
    
    def extract_authors(self, text: str) -> List[str]:
        """
        Extrae autores del artículo.
        Estrategia: Buscar patrones de nombres después del título.
        """
        if not text:
            return []
        
        authors = []
        lines = text.split('\n')
        
        # Buscar entre las líneas 5-30 (después del título, antes del abstract)
        for line in lines[5:30]:
            line = line.strip()
            
            # Patrón: Nombre Apellido, Nombre Apellido
            # o Apellido, N., Apellido, N.
            if ',' in line and len(line) < 200:
                # Verificar que tenga formato de autores
                if any(char.isupper() for char in line):
                    # Limpiar y separar
                    potential_authors = [a.strip() for a in line.split(',')]
                    
                    # Filtrar nombres válidos
                    for author in potential_authors:
                        if len(author) > 3 and len(author) < 50:
                            # Verificar que tenga al menos una letra mayúscula
                            if any(c.isupper() for c in author):
                                authors.append(author)
            
            # Si ya encontramos autores razonables, parar
            if len(authors) >= 2:
                break
        
        # Limpiar duplicados y retornar
        return list(set(authors[:10]))  # Máximo 10 autores
    
    def extract_year(self, text: str) -> Optional[int]:
        """
        Extrae el año de publicación.
        Estrategia: Buscar años en las primeras páginas.
        """
        if not text:
            return None
        
        # Buscar en los primeros 2000 caracteres
        text_sample = text[:2000]
        
        years = self.YEAR_PATTERN.findall(text_sample)
        
        if years:
            # Filtrar años razonables (últimos 50 años)
            current_year = datetime.now().year
            valid_years = [int(y) for y in years if current_year - 50 <= int(y) <= current_year + 1]
            
            if valid_years:
                # Retornar el año más reciente
                return max(valid_years)
        
        return None
    
    def extract_doi(self, text: str) -> Optional[str]:
        """
        Extrae el DOI del artículo.
        Estrategia: Buscar patrón DOI estándar.
        """
        if not text:
            return None
        
        # Buscar en todo el documento
        match = self.DOI_PATTERN.search(text)
        
        if match:
            doi = match.group(1)
            # Limpiar caracteres finales comunes
            doi = doi.rstrip('.,;:)]} ')
            return doi
        
        return None
    
    def extract_issn(self, text: str) -> Optional[str]:
        """
        Extrae el ISSN del artículo.
        Estrategia: Buscar patrón ISSN estándar.
        """
        if not text:
            return None
        
        match = self.ISSN_PATTERN.search(text)
        
        if match:
            issn = match.group(1)
            # Normalizar formato: XXXX-XXXX
            issn = issn.replace(' ', '-')
            if '-' not in issn and len(issn) == 8:
                issn = f"{issn[:4]}-{issn[4:]}"
            return issn
        
        return None
    
    def extract_abstract(self, text: str) -> Optional[str]:
        """
        Extrae el resumen/abstract del artículo.
        Estrategia: Buscar sección "Abstract" y extraer hasta la siguiente sección.
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Buscar inicio del abstract
        abstract_start = -1
        for keyword in self.ABSTRACT_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            match = re.search(pattern, text_lower)
            if match:
                abstract_start = match.end()
                break
        
        if abstract_start == -1:
            return None
        
        # Buscar fin del abstract (siguiente sección)
        abstract_end = len(text)
        
        # Buscar keywords o introducción
        for keyword in self.KEYWORDS_SECTION + self.INTRODUCTION_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            match = re.search(pattern, text_lower[abstract_start:])
            if match:
                potential_end = abstract_start + match.start()
                if potential_end < abstract_end:
                    abstract_end = potential_end
        
        # Extraer abstract
        abstract = text[abstract_start:abstract_end].strip()
        
        # Limpiar
        abstract = re.sub(r'\s+', ' ', abstract)  # Normalizar espacios
        
        # Validar longitud razonable
        if 50 < len(abstract) < 2000:
            return abstract
        
        return None
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extrae palabras clave del artículo.
        Estrategia: Buscar sección "Keywords" o "Palabras clave".
        """
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Buscar sección de keywords
        keywords_start = -1
        for keyword in self.KEYWORDS_SECTION:
            pattern = rf'\b{keyword}\b[:\s]*'
            match = re.search(pattern, text_lower)
            if match:
                keywords_start = match.end()
                break
        
        if keywords_start == -1:
            return []
        
        # Extraer hasta el siguiente párrafo (máximo 500 caracteres)
        keywords_text = text[keywords_start:keywords_start + 500]
        
        # Buscar hasta el primer punto seguido o nueva línea doble
        end_match = re.search(r'\.\s*\n|\n\n', keywords_text)
        if end_match:
            keywords_text = keywords_text[:end_match.start()]
        
        # Separar keywords por comas, punto y coma, o nueva línea
        keywords = re.split(r'[,;•\n]', keywords_text)
        
        # Limpiar y filtrar
        keywords = [
            kw.strip().strip('.').strip()
            for kw in keywords
            if kw.strip() and len(kw.strip()) > 2
        ]
        
        return keywords[:15]  # Máximo 15 keywords
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extrae emails de los autores.
        """
        if not text:
            return []
        
        # Buscar en los primeros 3000 caracteres (donde suelen estar los autores)
        text_sample = text[:3000]
        
        emails = self.EMAIL_PATTERN.findall(text_sample)
        
        # Filtrar emails válidos y únicos
        valid_emails = []
        for email in emails:
            email = email.lower()
            # Filtrar dominios comunes no académicos
            if not any(bad in email for bad in ['example.com', 'test.com', 'mailto']):
                if email not in valid_emails:
                    valid_emails.append(email)
        
        return valid_emails[:10]  # Máximo 10 emails
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, any]:
        """
        Obtiene información básica del PDF (metadatos del archivo).
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con información del PDF
        """
        info = {
            'num_pages': None,
            'file_size': None,
            'encrypted': False,
            'pdf_version': None,
            'metadata': {}
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                info['num_pages'] = len(reader.pages)
                info['encrypted'] = reader.is_encrypted
                
                # Metadatos del PDF
                if reader.metadata:
                    metadata = reader.metadata
                    info['metadata'] = {
                        'title': metadata.get('/Title'),
                        'author': metadata.get('/Author'),
                        'subject': metadata.get('/Subject'),
                        'creator': metadata.get('/Creator'),
                        'producer': metadata.get('/Producer'),
                        'creation_date': metadata.get('/CreationDate'),
                    }
            
            # Tamaño del archivo
            info['file_size'] = Path(pdf_path).stat().st_size
            
        except Exception as e:
            self.logger.error(f"Error al obtener info del PDF: {e}")
        
        return info
