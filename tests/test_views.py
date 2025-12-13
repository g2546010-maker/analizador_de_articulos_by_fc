"""
Tests para las vistas (routes) de artículos.
"""
import pytest
from flask import url_for
from app.models import Articulo, Autor, TipoProduccion, Estado


class TestArticleViews:
    """Tests para las rutas de artículos."""
    
    def test_index_route_empty(self, client, app, db_session, catalogs):
        """Test de ruta index sin artículos."""
        with app.app_context():
            response = client.get(url_for('articles.index'))
            
            assert response.status_code == 200
            assert b'articles' in response.data or b'art' in response.data.lower()
    
    def test_index_route_with_articles(self, client, app, db_session, catalogs):
        """Test de ruta index con artículos."""
        with app.app_context():
            # Crear algunos artículos
            for i in range(3):
                articulo = Articulo(
                    titulo=f'Test Article {i+1}',
                    tipo_produccion_id=catalogs['tipo'].id,
                    estado_id=catalogs['estado'].id
                )
                db_session.add(articulo)
            db_session.commit()
            
            response = client.get(url_for('articles.index'))
            
            assert response.status_code == 200
            # Verificar que al menos uno de los títulos aparece
            assert b'Test Article' in response.data
    
    def test_index_with_pagination(self, client, app, db_session, catalogs):
        """Test de paginación en index."""
        with app.app_context():
            # Crear 25 artículos
            for i in range(25):
                articulo = Articulo(
                    titulo=f'Article {i+1}',
                    tipo_produccion_id=catalogs['tipo'].id,
                    estado_id=catalogs['estado'].id
                )
                db_session.add(articulo)
            db_session.commit()
            
            # Página 1
            response = client.get(url_for('articles.index', page=1, per_page=10))
            assert response.status_code == 200
            
            # Página 2
            response = client.get(url_for('articles.index', page=2, per_page=10))
            assert response.status_code == 200
    
    def test_new_route_get(self, client, app, db_session, catalogs):
        """Test de ruta para mostrar formulario de nuevo artículo."""
        with app.app_context():
            response = client.get(url_for('articles.new'))
            
            assert response.status_code == 200
            # Verificar que contiene elementos de formulario
            assert b'form' in response.data or b'titulo' in response.data.lower()
    
    def test_new_route_post_success(self, client, app, db_session, catalogs):
        """Test de creación exitosa de artículo."""
        with app.app_context():
            data = {
                'titulo': 'New Test Article',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'anio_publicacion': 2023,
                'para_curriculum': True,
                'citas': 0
            }
            
            response = client.post(
                url_for('articles.new'),
                data=data,
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verificar que el artículo fue creado
            articulo = Articulo.query.filter_by(titulo='New Test Article').first()
            assert articulo is not None
            assert articulo.titulo == 'New Test Article'
    
    def test_new_route_post_missing_required(self, client, app, db_session, catalogs):
        """Test de creación con campo requerido faltante."""
        with app.app_context():
            data = {
                # Falta título
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
            }
            
            response = client.post(
                url_for('articles.new'),
                data=data,
                follow_redirects=True
            )
            
            # Debe retornar al formulario con error
            assert response.status_code == 200
            # El artículo no debe ser creado
            count = Articulo.query.count()
            assert count == 0
    
    def test_show_route_success(self, client, app, db_session, catalogs):
        """Test de vista de detalle de artículo existente."""
        with app.app_context():
            # Crear artículo
            articulo = Articulo(
                titulo='Detail Test Article',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add(articulo)
            db_session.commit()
            
            response = client.get(url_for('articles.show', id=articulo.id))
            
            assert response.status_code == 200
            assert b'Detail Test Article' in response.data
    
    def test_show_route_not_found(self, client, app, db_session, catalogs):
        """Test de vista de detalle con ID inexistente."""
        with app.app_context():
            response = client.get(url_for('articles.show', id=999))
            
            assert response.status_code == 404
    
    def test_edit_route_get(self, client, app, db_session, catalogs):
        """Test de ruta para mostrar formulario de edición."""
        with app.app_context():
            # Crear artículo
            articulo = Articulo(
                titulo='Edit Test Article',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add(articulo)
            db_session.commit()
            
            response = client.get(url_for('articles.edit', id=articulo.id))
            
            assert response.status_code == 200
            assert b'Edit Test Article' in response.data
    
    def test_edit_route_post_success(self, client, app, db_session, catalogs):
        """Test de actualización exitosa de artículo."""
        with app.app_context():
            # Crear artículo
            articulo = Articulo(
                titulo='Original Title',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add(articulo)
            db_session.commit()
            article_id = articulo.id
            
            # Actualizar
            data = {
                'titulo': 'Updated Title',
                'tipo_produccion_id': catalogs['tipo'].id,
                'estado_id': catalogs['estado'].id,
                'anio_publicacion': 2024,
                'para_curriculum': True,
                'citas': 5
            }
            
            response = client.post(
                url_for('articles.edit', id=article_id),
                data=data,
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verificar cambios
            articulo_actualizado = Articulo.query.get(article_id)
            assert articulo_actualizado.titulo == 'Updated Title'
            assert articulo_actualizado.anio_publicacion == 2024
    
    def test_edit_route_not_found(self, client, app, db_session, catalogs):
        """Test de edición con ID inexistente."""
        with app.app_context():
            response = client.get(url_for('articles.edit', id=999))
            
            assert response.status_code == 404
    
    def test_delete_route_soft(self, client, app, db_session, catalogs):
        """Test de eliminación lógica de artículo."""
        with app.app_context():
            # Crear artículo
            articulo = Articulo(
                titulo='To Delete',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add(articulo)
            db_session.commit()
            article_id = articulo.id
            
            # Eliminar (soft delete)
            response = client.post(
                url_for('articles.delete', id=article_id),
                data={'hard_delete': 'false'},
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verificar que está marcado como inactivo
            articulo = Articulo.query.get(article_id)
            assert articulo is not None
            assert articulo.activo is False
    
    def test_delete_route_hard(self, client, app, db_session, catalogs):
        """Test de eliminación física de artículo."""
        with app.app_context():
            # Crear artículo
            articulo = Articulo(
                titulo='To Delete Hard',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add(articulo)
            db_session.commit()
            article_id = articulo.id
            
            # Eliminar (hard delete)
            response = client.post(
                url_for('articles.delete', id=article_id),
                data={'hard_delete': 'true'},
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verificar que fue eliminado de la BD
            articulo = Articulo.query.get(article_id)
            assert articulo is None
    
    def test_delete_route_not_found(self, client, app, db_session, catalogs):
        """Test de eliminación con ID inexistente."""
        with app.app_context():
            response = client.post(
                url_for('articles.delete', id=999),
                follow_redirects=True
            )
            
            assert response.status_code == 200
            # Debe contener mensaje de error
            assert b'error' in response.data.lower() or b'no se encontr' in response.data.lower()
    
    def test_restore_route(self, client, app, db_session, catalogs):
        """Test de restauración de artículo eliminado."""
        with app.app_context():
            # Crear y eliminar artículo
            articulo = Articulo(
                titulo='To Restore',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id,
                activo=False  # Ya eliminado
            )
            db_session.add(articulo)
            db_session.commit()
            article_id = articulo.id
            
            # Restaurar
            response = client.post(
                url_for('articles.restore', id=article_id),
                follow_redirects=True
            )
            
            assert response.status_code == 200
            
            # Verificar que está activo
            articulo = Articulo.query.get(article_id)
            assert articulo.activo is True
    
    def test_index_with_filters(self, client, app, db_session, catalogs):
        """Test de filtros en lista de artículos."""
        with app.app_context():
            # Crear artículos con diferentes características
            articulo1 = Articulo(
                titulo='Article 2023',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id,
                anio_publicacion=2023
            )
            articulo2 = Articulo(
                titulo='Article 2024',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id,
                anio_publicacion=2024
            )
            db_session.add_all([articulo1, articulo2])
            db_session.commit()
            
            # Filtrar por año
            response = client.get(url_for('articles.index', anio=2023))
            
            assert response.status_code == 200
            # Verificar que retorna resultados filtrados
    
    def test_index_with_search_query(self, client, app, db_session, catalogs):
        """Test de búsqueda por texto en lista."""
        with app.app_context():
            # Crear artículos
            articulo1 = Articulo(
                titulo='Machine Learning in Medicine',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            articulo2 = Articulo(
                titulo='Deep Learning Applications',
                tipo_produccion_id=catalogs['tipo'].id,
                estado_id=catalogs['estado'].id
            )
            db_session.add_all([articulo1, articulo2])
            db_session.commit()
            
            # Buscar por palabra
            response = client.get(url_for('articles.index', query='Machine'))
            
            assert response.status_code == 200
