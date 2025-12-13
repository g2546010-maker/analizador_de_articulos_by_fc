"""
Tests para el controlador de artículos.
"""
import pytest
from datetime import datetime
from app.controllers import ArticleController
from app.models import Articulo, Autor, Revista, TipoProduccion, Estado, LGAC, Proposito


class TestArticleControllerCreate:
    """Tests para el método create del controlador."""
    
    def test_create_article_success(self, app, db_session, catalogs):
        """Test crear artículo con datos válidos."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'anio_publicacion': 2024
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is not None
            assert error is None
            assert articulo.titulo == 'Test Article'
            assert articulo.anio_publicacion == 2024
    
    def test_create_article_missing_title(self, app, db_session, catalogs):
        """Test crear artículo sin título."""
        with app.app_context():
            data = {
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert error == "El título es obligatorio"
    
    def test_create_article_missing_tipo(self, app, db_session, catalogs):
        """Test crear artículo sin tipo de producción."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'estado_id': catalogs['estado'].id
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert error == "El tipo de producción es obligatorio"
    
    def test_create_article_missing_estado(self, app, db_session, catalogs):
        """Test crear artículo sin estado."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert error == "El estado es obligatorio"
    
    def test_create_article_invalid_doi(self, app, db_session, catalogs):
        """Test crear artículo con DOI inválido."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'doi': 'invalid-doi'
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert 'DOI inválido' in error
    
    def test_create_article_invalid_issn(self, app, db_session, catalogs):
        """Test crear artículo con ISSN inválido."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'issn': '12345678'
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert 'ISSN inválido' in error
    
    def test_create_article_invalid_year(self, app, db_session, catalogs):
        """Test crear artículo con año inválido."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'anio_publicacion': 1800
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert 'Año inválido' in error
    
    def test_create_article_invalid_pages(self, app, db_session, catalogs):
        """Test crear artículo con páginas inválidas."""
        with app.app_context():
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'pagina_inicio': 20,
                'pagina_fin': 10
            }
            
            articulo, error = ArticleController.create(data)
            
            assert articulo is None
            assert 'página final' in error.lower()


class TestArticleControllerGetAll:
    """Tests para el método get_all del controlador."""
    
    def test_get_all_empty(self, app, db_session, catalogs):
        """Test obtener artículos cuando no hay ninguno."""
        with app.app_context():
            pagination, error = ArticleController.get_all()
            
            assert pagination is not None
            assert error is None
            assert pagination.total == 0
    
    def test_get_all_with_articles(self, app, db_session, catalogs):
        """Test obtener artículos cuando hay varios."""
        with app.app_context():
            # Crear artículos de prueba
            for i in range(5):
                data = {
                    'titulo': f'Article {i}',
                    'tipo_produccion_id': catalogs['tipo'].id,
                    'estado_id': catalogs['estado'].id
                }
                ArticleController.create(data)
            
            pagination, error = ArticleController.get_all()
            
            assert pagination is not None
            assert error is None
            assert pagination.total == 5
    
    def test_get_all_pagination(self, app, db_session, catalogs):
        """Test paginación de artículos."""
        with app.app_context():
            # Crear 25 artículos
            for i in range(25):
                data = {
                    'titulo': f'Article {i}',
                    'tipo_produccion_id': catalogs['tipo'].id,
                    'estado_id': catalogs['estado'].id
                }
                ArticleController.create(data)
            
            # Obtener página 1 con 10 por página
            pagination, error = ArticleController.get_all(page=1, per_page=10)
            
            assert pagination is not None
            assert error is None
            assert len(pagination.items) == 10
            assert pagination.total == 25
            assert pagination.pages == 3
    
    def test_get_all_filter_by_tipo(self, app, db_session, catalogs):
        """Test filtrar artículos por tipo."""
        with app.app_context():
            # Crear artículos con el tipo de catálogo
            for i in range(3):
                data = {
                    'titulo': f'Article {i}',
                    'tipo_produccion_id': catalogs['tipo'].id,
                    'estado_id': catalogs['estado'].id
                }
                ArticleController.create(data)
            
            # Filtrar por tipo
            pagination, error = ArticleController.get_all(tipo_id=catalogs['tipo'].id)
            
            assert pagination is not None
            assert error is None
            assert pagination.total == 3
    
    def test_get_all_invalid_page(self, app, db_session, catalogs):
        """Test obtener artículos con página inválida."""
        with app.app_context():
            pagination, error = ArticleController.get_all(page=0)
            
            assert pagination is None
            assert 'página debe ser mayor' in error.lower()
    
    def test_get_all_invalid_per_page(self, app, db_session, catalogs):
        """Test obtener artículos con per_page inválido."""
        with app.app_context():
            pagination, error = ArticleController.get_all(per_page=200)
            
            assert pagination is None
            assert 'entre 1 y 100' in error


class TestArticleControllerGetById:
    """Tests para el método get_by_id del controlador."""
    
    def test_get_by_id_success(self, app, db_session, catalogs):
        """Test obtener artículo por ID existente."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            
            # Obtener por ID
            articulo, error = ArticleController.get_by_id(articulo_creado.id)
            
            assert articulo is not None
            assert error is None
            assert articulo.id == articulo_creado.id
            assert articulo.titulo == 'Test Article'
    
    def test_get_by_id_not_found(self, app, db_session, catalogs):
        """Test obtener artículo por ID inexistente."""
        with app.app_context():
            articulo, error = ArticleController.get_by_id(9999)
            
            assert articulo is None
            assert 'No se encontró' in error


class TestArticleControllerUpdate:
    """Tests para el método update del controlador."""
    
    def test_update_article_success(self, app, db_session, catalogs):
        """Test actualizar artículo con datos válidos."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Original Title',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            
            # Actualizar
            update_data = {
                'titulo': 'Updated Title',
                'anio_publicacion': 2024
            }
            articulo, error = ArticleController.update(articulo_creado.id, update_data)
            
            assert articulo is not None
            assert error is None
            assert articulo.titulo == 'Updated Title'
            assert articulo.anio_publicacion == 2024
    
    def test_update_article_not_found(self, app, db_session, catalogs):
        """Test actualizar artículo inexistente."""
        with app.app_context():
            update_data = {'titulo': 'Updated'}
            articulo, error = ArticleController.update(9999, update_data)
            
            assert articulo is None
            assert 'No se encontró' in error
    
    def test_update_article_empty_title(self, app, db_session, catalogs):
        """Test actualizar artículo con título vacío."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Original Title',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            
            # Intentar actualizar con título vacío
            update_data = {'titulo': ''}
            articulo, error = ArticleController.update(articulo_creado.id, update_data)
            
            assert articulo is None
            assert 'título no puede estar vacío' in error


class TestArticleControllerDelete:
    """Tests para el método delete del controlador."""
    
    def test_delete_article_soft(self, app, db_session, catalogs):
        """Test eliminación lógica de artículo."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            
            # Eliminar lógicamente
            success, error = ArticleController.delete(articulo_creado.id, soft=True)
            
            assert success is True
            assert error is None
            
            # Verificar que sigue existiendo pero inactivo
            articulo = Articulo.query.get(articulo_creado.id)
            assert articulo is not None
            assert articulo.activo is False
    
    def test_delete_article_hard(self, app, db_session, catalogs):
        """Test eliminación física de artículo."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            article_id = articulo_creado.id
            
            # Eliminar físicamente
            success, error = ArticleController.delete(article_id, soft=False)
            
            assert success is True
            assert error is None
            
            # Verificar que ya no existe
            articulo = Articulo.query.get(article_id)
            assert articulo is None
    
    def test_delete_article_not_found(self, app, db_session, catalogs):
        """Test eliminar artículo inexistente."""
        with app.app_context():
            success, error = ArticleController.delete(9999)
            
            assert success is False
            assert 'No se encontró' in error
    
    def test_restore_article(self, app, db_session, catalogs):
        """Test restaurar artículo eliminado lógicamente."""
        with app.app_context():
            # Crear y eliminar artículo
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo_creado, _ = ArticleController.create(data)
            ArticleController.delete(articulo_creado.id, soft=True)
            
            # Restaurar
            articulo, error = ArticleController.restore(articulo_creado.id)
            
            assert articulo is not None
            assert error is None
            assert articulo.activo is True


class TestArticleControllerAuthors:
    """Tests para gestión de autores."""
    
    def test_add_author_success(self, app, db_session, catalogs):
        """Test agregar autor a artículo."""
        with app.app_context():
            # Crear artículo
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo, _ = ArticleController.create(data)
            
            # Crear autor
            autor = Autor(nombre='John', apellidos='Doe')
            db_session.add(autor)
            db_session.commit()
            
            # Agregar autor al artículo
            success, error = ArticleController.add_author(
                articulo.id, autor.id, orden=1, es_corresponsal=True
            )
            
            assert success is True
            assert error is None
            
            # Verificar que se agregó  
            articulo_actualizado = Articulo.query.get(articulo.id)
            # La relación con autores es a través de articulo_autores
            from app.models.relations import ArticuloAutor
            relaciones = ArticuloAutor.query.filter_by(articulo_id=articulo.id).all()
            assert len(relaciones) == 1
    
    def test_add_author_duplicate(self, app, db_session, catalogs):
        """Test agregar autor duplicado."""
        with app.app_context():
            # Crear artículo y autor
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo, _ = ArticleController.create(data)
            
            autor = Autor(nombre='John', apellidos='Doe')
            db_session.add(autor)
            db_session.commit()
            
            # Agregar autor
            ArticleController.add_author(articulo.id, autor.id)
            
            # Intentar agregar nuevamente
            success, error = ArticleController.add_author(articulo.id, autor.id)
            
            assert success is False
            assert 'ya está asociado' in error
    
    def test_remove_author_success(self, app, db_session, catalogs):
        """Test remover autor de artículo."""
        with app.app_context():
            # Crear artículo y autor
            data = {
                'titulo': 'Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id
            }
            articulo, _ = ArticleController.create(data)
            
            autor = Autor(nombre='John', apellidos='Doe')
            db_session.add(autor)
            db_session.commit()
            
            # Agregar y remover autor
            ArticleController.add_author(articulo.id, autor.id)
            success, error = ArticleController.remove_author(articulo.id, autor.id)
            
            assert success is True
            assert error is None
            
            # Verificar que se removió
            articulo_actualizado = Articulo.query.get(articulo.id)
            from app.models.relations import ArticuloAutor
            relaciones = ArticuloAutor.query.filter_by(articulo_id=articulo.id).all()
            assert len(relaciones) == 0


class TestArticleControllerStatistics:
    """Tests para estadísticas."""
    
    def test_get_statistics_empty(self, app, db_session, catalogs):
        """Test obtener estadísticas sin artículos."""
        with app.app_context():
            stats, error = ArticleController.get_statistics()
            
            assert stats is not None
            assert error is None
            assert stats['total'] == 0
    
    def test_get_statistics_with_articles(self, app, db_session, catalogs):
        """Test obtener estadísticas con artículos."""
        with app.app_context():
            # Crear varios artículos
            for i in range(5):
                data = {
                    'titulo': f'Article {i}',
                    'tipo_produccion_id': catalogs['tipo'].id,
                    'estado_id': catalogs['estado'].id,
                    'anio_publicacion': 2024,
                    'para_curriculum': True
                }
                ArticleController.create(data)
            
            stats, error = ArticleController.get_statistics()
            
            assert stats is not None
            assert error is None
            assert stats['total'] == 5
            assert stats['para_curriculum'] == 5
            assert len(stats['por_tipo']) > 0
            assert len(stats['por_estado']) > 0
