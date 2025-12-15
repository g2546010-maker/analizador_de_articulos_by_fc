"""
Tests para formularios de artículos.
"""
import pytest
from datetime import datetime, timedelta
from app.forms import ArticleForm, ArticleSearchForm, ArticleAuthorForm
from app.forms.utils import populate_form_choices, validate_articulo_data
from app.models.catalogs import TipoProduccion, Estado, LGAC, Proposito
from app.models.revista import Revista
from app.models.autor import Autor


class TestArticleForm:
    """Tests para el formulario de artículo."""
    
    def test_form_creation(self, app):
        """Test que el formulario se puede crear."""
        with app.app_context():
            form = ArticleForm()
            assert form is not None
            assert hasattr(form, 'titulo')
            assert hasattr(form, 'doi')
            assert hasattr(form, 'issn')
    
    def test_doi_validation_valid(self, app):
        """Test validación de DOI con formato válido."""
        with app.app_context():
            form = ArticleForm()
            form.doi.data = '10.1234/journal.2024.001'
            
            # No debería lanzar excepción
            try:
                form.validate_doi(form.doi)
                assert True
            except Exception:
                pytest.fail("DOI válido fue rechazado")
    
    def test_doi_validation_invalid(self, app):
        """Test validación de DOI con formato inválido."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            form.doi.data = 'invalid-doi'
            
            with pytest.raises(ValidationError):
                form.validate_doi(form.doi)
    
    def test_issn_validation_valid(self, app):
        """Test validación de ISSN con formato válido."""
        with app.app_context():
            form = ArticleForm()
            form.issn.data = '1234-5678'
            
            try:
                form.validate_issn(form.issn)
                assert True
            except Exception:
                pytest.fail("ISSN válido fue rechazado")
    
    def test_issn_validation_invalid(self, app):
        """Test validación de ISSN con formato inválido."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            form.issn.data = '12345678'  # Sin guión
            
            with pytest.raises(ValidationError):
                form.validate_issn(form.issn)
    
    def test_anio_validation_valid(self, app):
        """Test validación de año con valor válido."""
        with app.app_context():
            form = ArticleForm()
            current_year = datetime.now().year
            form.anio_publicacion.data = current_year
            
            try:
                form.validate_anio_publicacion(form.anio_publicacion)
                assert True
            except Exception:
                pytest.fail("Año válido fue rechazado")
    
    def test_anio_validation_future(self, app):
        """Test validación de año futuro (más de un año adelante)."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            current_year = datetime.now().year
            form.anio_publicacion.data = current_year + 5
            
            with pytest.raises(ValidationError):
                form.validate_anio_publicacion(form.anio_publicacion)
    
    def test_anio_validation_too_old(self, app):
        """Test validación de año muy antiguo."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            form.anio_publicacion.data = 1800
            
            with pytest.raises(ValidationError):
                form.validate_anio_publicacion(form.anio_publicacion)
    
    def test_paginas_validation_valid(self, app):
        """Test validación de páginas con valores válidos."""
        with app.app_context():
            form = ArticleForm()
            form.pagina_inicio.data = 1
            form.pagina_fin.data = 20
            
            try:
                form.validate_pagina_fin(form.pagina_fin)
                assert True
            except Exception:
                pytest.fail("Páginas válidas fueron rechazadas")
    
    def test_paginas_validation_invalid(self, app):
        """Test validación de páginas con página fin menor que inicio."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            form.pagina_inicio.data = 20
            form.pagina_fin.data = 1
            
            with pytest.raises(ValidationError):
                form.validate_pagina_fin(form.pagina_fin)
    
    def test_fecha_publicacion_validation_future(self, app):
        """Test validación de fecha de publicación futura."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            future_date = datetime.now().date() + timedelta(days=30)
            form.fecha_publicacion.data = future_date
            
            with pytest.raises(ValidationError):
                form.validate_fecha_publicacion(form.fecha_publicacion)
    
    def test_fecha_aceptacion_validation_invalid(self, app):
        """Test validación de fecha de aceptación posterior a publicación."""
        with app.app_context():
            from wtforms.validators import ValidationError
            
            form = ArticleForm()
            form.fecha_publicacion.data = datetime(2024, 1, 1).date()
            form.fecha_aceptacion.data = datetime(2024, 6, 1).date()
            
            with pytest.raises(ValidationError):
                form.validate_fecha_aceptacion(form.fecha_aceptacion)
    
    def test_populate_form_choices(self, app, db_session, catalogs):
        """Test que los campos dinámicos se pueblan correctamente."""
        with app.app_context():
            form = ArticleForm()
            populate_form_choices(form)
            
            # Verificar que hay opciones
            assert len(form.tipo_produccion_id.choices) > 1
            assert len(form.estado_id.choices) > 1
            assert len(form.proposito_id.choices) > 1
            assert len(form.lgac_id.choices) > 1


class TestArticleSearchForm:
    """Tests para el formulario de búsqueda."""
    
    def test_search_form_creation(self, app):
        """Test que el formulario de búsqueda se puede crear."""
        with app.app_context():
            form = ArticleSearchForm()
            assert form is not None
            assert hasattr(form, 'query')
            assert hasattr(form, 'tipo_produccion_id')
            assert hasattr(form, 'estado_id')


class TestArticleAuthorForm:
    """Tests para el formulario de autor."""
    
    def test_author_form_creation(self, app):
        """Test que el formulario de autor se puede crear."""
        with app.app_context():
            form = ArticleAuthorForm()
            assert form is not None
            assert hasattr(form, 'autor_id')
            assert hasattr(form, 'orden')
            assert hasattr(form, 'es_corresponsal')


class TestValidateArticuloData:
    """Tests para validaciones de negocio."""
    
    def test_publicado_sin_revista(self, app, db_session, catalogs):
        """Test que un artículo publicado debe tener revista."""
        with app.app_context():
            estado_publicado = Estado.query.filter_by(nombre='Publicado').first()
            
            form_data = {
                'estado_id': estado_publicado.id,
                'revista_id': None,
                'anio_publicacion': 2024
            }
            
            is_valid, errors = validate_articulo_data(form_data)
            assert not is_valid
            assert 'revista_id' in errors
    
    def test_publicado_sin_anio(self, app, db_session, catalogs):
        """Test que un artículo publicado debe tener año."""
        with app.app_context():
            estado_publicado = Estado.query.filter_by(nombre='Publicado').first()
            revista = Revista.query.first()
            
            form_data = {
                'estado_id': estado_publicado.id,
                'revista_id': revista.id if revista else None,
                'anio_publicacion': None
            }
            
            is_valid, errors = validate_articulo_data(form_data)
            assert not is_valid
            assert 'anio_publicacion' in errors
    
    def test_conference_paper_sin_congreso(self, app, db_session, catalogs):
        """Test que un conference paper debe tener nombre de congreso."""
        with app.app_context():
            # Buscar o crear un tipo conference paper
            tipo_conference = TipoProduccion.query.filter(
                TipoProduccion.nombre.ilike('%conference%')
            ).first()
            
            if tipo_conference:
                form_data = {
                    'tipo_produccion_id': tipo_conference.id,
                    'nombre_congreso': None
                }
                
                is_valid, errors = validate_articulo_data(form_data)
                assert not is_valid
                assert 'nombre_congreso' in errors


class TestFormIntegration:
    """Tests de integración entre formularios y modelos."""
    
    def test_form_to_model_mapping(self, app, db_session, catalogs):
        """Test que los campos del formulario mapean correctamente al modelo."""
        with app.app_context():
            from app.models.articulo import Articulo
            
            form = ArticleForm()
            populate_form_choices(form)
            
            # Verificar que todos los campos importantes existen
            articulo_fields = [c.name for c in Articulo.__table__.columns]
            
            # Campos que deben estar en el formulario
            expected_fields = [
                'titulo', 'doi', 'issn', 'anio_publicacion',
                'tipo_produccion_id', 'estado_id'
            ]
            
            for field in expected_fields:
                assert hasattr(form, field), f"Falta el campo {field}"
