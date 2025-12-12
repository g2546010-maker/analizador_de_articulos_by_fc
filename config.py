"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuración base"""
    

    
    # Secret key para sesiones y formularios
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de datos
    # La BD se guarda en la carpeta instance/ por defecto en Flask
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'articulos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'pdfs')
    EXPORT_FOLDER = os.path.join(basedir, 'exports', 'excel')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB máximo
    ALLOWED_EXTENSIONS = {'pdf', 'xlsx'}
    
    # Paginación
    ARTICLES_PER_PAGE = 20
    
    # Background worker
    WORKER_CHECK_INTERVAL = 3600  # 1 hora en segundos
    
    # Timezone
    TIMEZONE = 'America/Mexico_City'


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar queries SQL


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
