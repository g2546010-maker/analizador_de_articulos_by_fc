"""
Servicio para procesar PDFs en batch usando threading.
Maneja el upload y procesamiento de múltiples PDFs en paralelo.
"""
import logging
import threading
from typing import List, Dict, Callable
from pathlib import Path
from queue import Queue
from datetime import datetime

from app import db
from app.models.articulo import Articulo
from app.models.catalogs import TipoProduccion, Estado
from app.services.file_handler import FileHandler
from app.services.pdf_service import PDFService


logger = logging.getLogger(__name__)


class PDFBatchProcessor:
    """
    Procesa múltiples PDFs en paralelo usando threads.
    Extrae metadatos y crea artículos automáticamente.
    """
    
    def __init__(self, upload_folder: str, max_workers: int = 5, app=None):
        """
        Inicializa el procesador de batch.
        
        Args:
            upload_folder: Carpeta donde se guardan los PDFs
            max_workers: Número máximo de threads simultáneos
            app: Instancia de la aplicación Flask (para el contexto)
        """
        self.file_handler = FileHandler(upload_folder)
        self.pdf_service = PDFService()
        self.max_workers = max_workers
        self.app = app
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
    
    def process_files(self, files: List, progress_callback: Callable = None) -> Dict:
        """
        Procesa múltiples archivos PDF en paralelo.
        
        Args:
            files: Lista de FileStorage objects de Werkzeug
            progress_callback: Función callback para reportar progreso
            
        Returns:
            Diccionario con resultados del procesamiento
        """
        self.results = []
        self.errors = []
        
        total_files = len(files)
        processed = 0
        
        # Cola de trabajo
        work_queue = Queue()
        for file in files:
            work_queue.put(file)
        
        # Crear threads
        threads = []
        num_threads = min(self.max_workers, total_files)
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=self._worker,
                args=(work_queue, progress_callback, total_files),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Esperar a que terminen todos los threads
        for thread in threads:
            thread.join()
        
        # Compilar resultados
        return {
            'total': total_files,
            'success': len(self.results),
            'errors': len(self.errors),
            'results': self.results,
            'error_details': self.errors
        }
    
    def _worker(self, work_queue: Queue, progress_callback: Callable, total: int):
        """
        Worker thread que procesa archivos de la cola.
        """
        # Si hay una app, configurar el contexto para este thread
        if self.app:
            ctx = self.app.app_context()
            ctx.push()
        else:
            ctx = None
        
        try:
            while not work_queue.empty():
                try:
                    file = work_queue.get_nowait()
                except:
                    break
                
                try:
                    result = self._process_single_file(file)
                    
                    with self.lock:
                        self.results.append(result)
                        
                        if progress_callback:
                            progress = len(self.results) + len(self.errors)
                            progress_callback(progress, total)
                            
                except Exception as e:
                    logger.error(f"Error procesando {file.filename}: {e}")
                    with self.lock:
                        self.errors.append({
                            'filename': file.filename,
                            'error': str(e)
                        })
                finally:
                    work_queue.task_done()
        finally:
            # Limpiar el contexto al finalizar el thread
            if ctx:
                ctx.pop()
    
    def _process_single_file(self, file) -> Dict:
        """
        Procesa un único archivo PDF.
        
        Args:
            file: FileStorage object
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        start_time = datetime.now()
        
        # 1. Guardar archivo
        success, error, filepath = self.file_handler.save_file(file)
        
        if not success:
            raise Exception(f"Error al guardar archivo: {error}")
        
        # 2. Extraer metadatos
        metadata = self.pdf_service.extract_metadata(filepath)
        
        if not metadata['success']:
            # Eliminar archivo si no se pudo procesar
            self.file_handler.delete_file(filepath)
            raise Exception(f"Error al extraer metadatos: {metadata['error']}")
        
        # 3. Crear artículo en la BD
        articulo = self._create_article_from_metadata(
            metadata,
            original_filename=file.filename,
            stored_filepath=filepath
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'filename': file.filename,
            'article_id': articulo.id,
            'title': articulo.titulo,
            'confidence': metadata['confidence'],
            'processing_time': processing_time,
            'extracted_fields': {
                'titulo': bool(metadata['titulo']),
                'autores': len(metadata['autores']),
                'anio': bool(metadata['anio_publicacion']),
                'doi': bool(metadata['doi']),
                'issn': bool(metadata['issn']),
                'resumen': bool(metadata['resumen'])
            }
        }
    
    def _create_article_from_metadata(self, metadata: Dict, original_filename: str, 
                                     stored_filepath: str) -> Articulo:
        """
        Crea un artículo en la BD a partir de metadatos extraídos.
        
        Args:
            metadata: Diccionario con metadatos extraídos
            original_filename: Nombre original del archivo
            stored_filepath: Ruta donde se guardó el archivo
            
        Returns:
            Instancia de Articulo creada
        """
        # Obtener o crear tipo de producción por defecto
        tipo_default = TipoProduccion.query.filter_by(
            nombre='Artículo científico'
        ).first()
        
        if not tipo_default:
            # Crear si no existe
            tipo_default = TipoProduccion(
                nombre='Artículo científico',
                activo=True
            )
            db.session.add(tipo_default)
            db.session.flush()
        
        # Obtener estado "Publicado" por defecto
        estado_default = Estado.query.filter_by(
            nombre='Publicado'
        ).first()
        
        if not estado_default:
            estado_default = Estado(
                nombre='Publicado',
                color='#28a745',
                activo=True
            )
            db.session.add(estado_default)
            db.session.flush()
        
        # Preparar datos del artículo
        titulo = metadata.get('titulo') or f"Documento sin título - {original_filename}"
        
        # Limpiar título si es muy largo
        if len(titulo) > 500:
            titulo = titulo[:497] + "..."
        
        # Crear artículo
        articulo = Articulo(
            titulo=titulo,
            tipo_produccion_id=tipo_default.id,
            estado_id=estado_default.id,
            anio_publicacion=metadata.get('anio_publicacion'),
            doi=metadata.get('doi'),
            issn=metadata.get('issn'),
            archivo_origen=original_filename,
            completo=False,  # Marcar como incompleto para edición posterior
            campos_faltantes=self._identify_missing_fields(metadata),
            activo=True,
            para_curriculum=True
        )
        
        db.session.add(articulo)
        db.session.flush()  # Para obtener el ID del artículo
        
        # Crear autores si se extrajeron
        if metadata.get('autores'):
            from app.models.autor import Autor
            from app.models.relations import ArticuloAutor
            
            for idx, autor_nombre in enumerate(metadata['autores'], start=1):
                # Intentar parsear nombre y apellidos
                partes = autor_nombre.strip().split()
                if len(partes) >= 2:
                    nombre = partes[0]
                    apellidos = ' '.join(partes[1:])
                else:
                    nombre = autor_nombre
                    apellidos = ''
                
                # Buscar o crear autor
                autor = Autor.query.filter_by(
                    nombre=nombre,
                    apellidos=apellidos
                ).first()
                
                if not autor:
                    autor = Autor(
                        nombre=nombre,
                        apellidos=apellidos,
                        es_miembro_ca=False,
                        activo=True
                    )
                    db.session.add(autor)
                    db.session.flush()
                
                # Crear relación artículo-autor
                articulo_autor = ArticuloAutor(
                    articulo_id=articulo.id,
                    autor_id=autor.id,
                    orden=idx,
                    es_corresponsal=(idx == 1)  # Primer autor como corresponsal
                )
                db.session.add(articulo_autor)
        
        db.session.commit()
        
        return articulo
    
    def _identify_missing_fields(self, metadata: Dict) -> str:
        """
        Identifica qué campos faltaron en la extracción.
        
        Args:
            metadata: Diccionario con metadatos extraídos
            
        Returns:
            String con lista de campos faltantes
        """
        missing = []
        
        if not metadata.get('titulo'):
            missing.append('titulo')
        if not metadata.get('autores'):
            missing.append('autores')
        if not metadata.get('anio_publicacion'):
            missing.append('año')
        if not metadata.get('doi'):
            missing.append('DOI')
        if not metadata.get('issn'):
            missing.append('ISSN')
        if not metadata.get('resumen'):
            missing.append('resumen')
        
        if missing:
            return f"Faltan: {', '.join(missing)}"
        else:
            return "Extracción completa"


class UploadSession:
    """
    Maneja una sesión de upload con estado y progreso.
    Útil para tracking en tiempo real.
    """
    
    def __init__(self, session_id: str, total_files: int):
        """
        Inicializa una sesión de upload.
        
        Args:
            session_id: ID único de la sesión
            total_files: Total de archivos a procesar
        """
        self.session_id = session_id
        self.total_files = total_files
        self.processed = 0
        self.success = 0
        self.errors = 0
        self.start_time = datetime.now()
        self.status = 'processing'  # processing, completed, failed
        self.results = []
        self.lock = threading.Lock()
    
    def update_progress(self, processed: int, success: bool = True):
        """Actualiza el progreso de la sesión"""
        with self.lock:
            self.processed = processed
            if success:
                self.success += 1
            else:
                self.errors += 1
            
            if self.processed >= self.total_files:
                self.status = 'completed'
    
    def get_progress(self) -> Dict:
        """Obtiene el progreso actual"""
        with self.lock:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            return {
                'session_id': self.session_id,
                'status': self.status,
                'total': self.total_files,
                'processed': self.processed,
                'success': self.success,
                'errors': self.errors,
                'progress_percent': (self.processed / self.total_files * 100) if self.total_files > 0 else 0,
                'elapsed_time': elapsed,
                'estimated_remaining': (elapsed / self.processed * (self.total_files - self.processed)) if self.processed > 0 else 0
            }
    
    def add_result(self, result: Dict):
        """Agrega un resultado a la sesión"""
        with self.lock:
            self.results.append(result)


# Almacenamiento global de sesiones (en producción usar Redis o similar)
_upload_sessions = {}
_sessions_lock = threading.Lock()


def create_upload_session(total_files: int) -> UploadSession:
    """Crea una nueva sesión de upload"""
    session_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    session = UploadSession(session_id, total_files)
    
    with _sessions_lock:
        _upload_sessions[session_id] = session
    
    return session


def get_upload_session(session_id: str) -> UploadSession:
    """Obtiene una sesión de upload existente"""
    with _sessions_lock:
        return _upload_sessions.get(session_id)


def cleanup_old_sessions(max_age_hours: int = 24):
    """Limpia sesiones antiguas"""
    with _sessions_lock:
        now = datetime.now()
        to_remove = []
        
        for session_id, session in _upload_sessions.items():
            age_hours = (now - session.start_time).total_seconds() / 3600
            if age_hours > max_age_hours:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del _upload_sessions[session_id]
        
        return len(to_remove)
