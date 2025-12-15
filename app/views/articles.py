"""
Blueprint de artículos - CRUD y gestión de artículos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, send_file
from app.controllers.article_controller import ArticleController
from app.controllers.report_controller import ReportController
from app.forms.article_form import ArticleForm, ArticleSearchForm
from app.forms.utils import populate_form_choices
from app.models import Articulo
from app.services.pdf_batch_processor import PDFBatchProcessor
from config import Config
import logging

logger = logging.getLogger(__name__)

articles_bp = Blueprint('articles', __name__, url_prefix='/articles')


@articles_bp.route('/')
def index():
    """
    Lista de artículos con paginación y filtros.
    GET /articles?page=1&per_page=20&tipo_id=1&estado_id=2&query=machine+learning
    """
    # Obtener parámetros de la URL
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filtros
    filters = {
        'tipo_id': request.args.get('tipo_id', type=int),
        'estado_id': request.args.get('estado_id', type=int),
        'lgac_id': request.args.get('lgac_id', type=int),
        'anio': request.args.get('anio', type=int),
        'autor_id': request.args.get('autor_id', type=int),
        'query': request.args.get('query', '').strip()
    }
    
    # Remover filtros vacíos
    filters = {k: v for k, v in filters.items() if v}
    
    # Obtener artículos del controlador
    pagination, error = ArticleController.get_all(
        page=page,
        per_page=per_page,
        **filters
    )
    
    if error:
        flash(error, 'error')
        return render_template('articles/list.html', pagination=None, search_form=ArticleSearchForm())
    
    # Crear formulario de búsqueda pre-llenado con filtros actuales
    search_form = ArticleSearchForm(formdata=request.args)
    
    return render_template(
        'articles/list.html',
        pagination=pagination,
        search_form=search_form
    )


@articles_bp.route('/new', methods=['GET', 'POST'])
def new():
    """
    Formulario para crear nuevo artículo.
    GET /articles/new - Muestra formulario vacío
    POST /articles/new - Procesa creación
    """
    from app.forms.utils import populate_autor_choices
    
    form = ArticleForm()
    
    # Poblar campos de selección (catálogos)
    populate_form_choices(form)
    
    # Obtener opciones de autores para JavaScript
    autor_choices = populate_autor_choices()
    
    if form.validate_on_submit():
        # Extraer datos del formulario
        data = {
            'titulo': form.titulo.data,
            'titulo_revista': form.titulo_revista.data,
            'descripcion': form.descripcion.data,
            'tipo_produccion_id': form.tipo_produccion_id.data,
            'proposito_id': form.proposito_id.data if form.proposito_id.data else None,
            'lgac_id': form.lgac_id.data if form.lgac_id.data else None,
            'estado_id': form.estado_id.data,
            'anio_publicacion': form.anio_publicacion.data,
            'fecha_publicacion': form.fecha_publicacion.data,
            'fecha_aceptacion': form.fecha_aceptacion.data,
            'revista_id': form.revista_id.data if form.revista_id.data else None,
            'volumen': form.volumen.data,
            'numero': form.numero.data,
            'pagina_inicio': form.pagina_inicio.data,
            'pagina_fin': form.pagina_fin.data,
            'doi': form.doi.data,
            'url': form.url.data,
            'issn': form.issn.data,
            'nombre_congreso': form.nombre_congreso.data,
            'para_curriculum': form.para_curriculum.data,
            'factor_impacto': form.factor_impacto.data,
            'citas': form.citas.data if form.citas.data else 0,
        }
        
        # Crear artículo usando el controlador
        articulo, error = ArticleController.create(data)
        
        if error:
            flash(f'Error al crear artículo: {error}', 'error')
        else:
            # Procesar autores si se creó el artículo exitosamente
            if form.autores.data:
                from app.models import ArticuloAutor, Autor
                from app.models.relations import ArticuloIndexacion
                from app import db
                
                for autor_data in form.autores.data:
                    if autor_data.get('autor_id'):
                        articulo_autor = ArticuloAutor(
                            articulo_id=articulo.id,
                            autor_id=autor_data['autor_id'],
                            orden=autor_data.get('orden', 1),
                            es_corresponsal=autor_data.get('es_corresponsal', False)
                        )
                        db.session.add(articulo_autor)
                
                try:
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error al agregar autores: {str(e)}")
                    flash('Artículo creado pero hubo error al agregar autores', 'warning')
            
            # Procesar indexaciones
            if form.indexaciones.data:
                from app.models.relations import ArticuloIndexacion
                from app import db
                
                for indexacion_id in form.indexaciones.data:
                    if indexacion_id:
                        articulo_indexacion = ArticuloIndexacion(
                            articulo_id=articulo.id,
                            indexacion_id=indexacion_id
                        )
                        db.session.add(articulo_indexacion)
                
                try:
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error al agregar indexaciones: {str(e)}")
                    flash('Artículo creado pero hubo error al agregar indexaciones', 'warning')
            
            flash(f'Artículo "{articulo.titulo}" creado exitosamente', 'success')
            return redirect(url_for('articles.show', id=articulo.id))
    
    return render_template('articles/form.html', form=form, articulo=None, autor_choices=autor_choices)


@articles_bp.route('/<int:id>')
def show(id):
    """
    Ver detalle de un artículo.
    GET /articles/<id>
    """
    articulo, error = ArticleController.get_by_id(id)
    
    if error:
        flash(error, 'error')
        abort(404)
    
    return render_template('articles/detail.html', articulo=articulo)


@articles_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """
    Formulario para editar artículo existente.
    GET /articles/<id>/edit - Muestra formulario pre-llenado
    POST /articles/<id>/edit - Procesa actualización
    """
    from app.forms.utils import populate_autor_choices
    
    # Obtener artículo actual
    articulo, error = ArticleController.get_by_id(id)
    
    if error:
        flash(error, 'error')
        abort(404)
    
    # Crear formulario pre-llenado con datos actuales
    form = ArticleForm(obj=articulo)
    
    # Poblar campos de selección
    populate_form_choices(form)
    
    # Obtener opciones de autores para JavaScript
    autor_choices = populate_autor_choices()
    
    # Cargar autores e indexaciones existentes en modo GET
    if request.method == 'GET':
        from app.models import ArticuloAutor
        from app.models.relations import ArticuloIndexacion
        
        articulo_autores = ArticuloAutor.query.filter_by(articulo_id=articulo.id).order_by(ArticuloAutor.orden).all()
        
        # Limpiar y agregar entradas de autores
        while len(form.autores) > 0:
            form.autores.pop_entry()
        
        for aa in articulo_autores:
            form.autores.append_entry({
                'autor_id': aa.autor_id,
                'orden': aa.orden,
                'es_corresponsal': aa.es_corresponsal
            })
        
        # Cargar indexaciones existentes
        articulo_indexaciones = ArticuloIndexacion.query.filter_by(articulo_id=articulo.id).all()
        form.indexaciones.data = [ai.indexacion_id for ai in articulo_indexaciones]
        
        # Poblar choices de los autores recién agregados
        populate_form_choices(form)
    
    if form.validate_on_submit():
        # Extraer solo campos modificados
        data = {}
        
        if form.titulo.data != articulo.titulo:
            data['titulo'] = form.titulo.data
        if form.titulo_revista.data != articulo.titulo_revista:
            data['titulo_revista'] = form.titulo_revista.data
        if form.descripcion.data != articulo.descripcion:
            data['descripcion'] = form.descripcion.data
        if form.tipo_produccion_id.data != articulo.tipo_produccion_id:
            data['tipo_produccion_id'] = form.tipo_produccion_id.data
        if form.proposito_id.data != articulo.proposito_id:
            data['proposito_id'] = form.proposito_id.data if form.proposito_id.data else None
        if form.lgac_id.data != articulo.lgac_id:
            data['lgac_id'] = form.lgac_id.data if form.lgac_id.data else None
        if form.estado_id.data != articulo.estado_id:
            data['estado_id'] = form.estado_id.data
        if form.anio_publicacion.data != articulo.anio_publicacion:
            data['anio_publicacion'] = form.anio_publicacion.data
        if form.fecha_publicacion.data != articulo.fecha_publicacion:
            data['fecha_publicacion'] = form.fecha_publicacion.data
        if form.fecha_aceptacion.data != articulo.fecha_aceptacion:
            data['fecha_aceptacion'] = form.fecha_aceptacion.data
        if form.revista_id.data != articulo.revista_id:
            data['revista_id'] = form.revista_id.data if form.revista_id.data else None
        if form.volumen.data != articulo.volumen:
            data['volumen'] = form.volumen.data
        if form.numero.data != articulo.numero:
            data['numero'] = form.numero.data
        if form.pagina_inicio.data != articulo.pagina_inicio:
            data['pagina_inicio'] = form.pagina_inicio.data
        if form.pagina_fin.data != articulo.pagina_fin:
            data['pagina_fin'] = form.pagina_fin.data
        if form.doi.data != articulo.doi:
            data['doi'] = form.doi.data
        if form.url.data != articulo.url:
            data['url'] = form.url.data
        if form.issn.data != articulo.issn:
            data['issn'] = form.issn.data
        if form.nombre_congreso.data != articulo.nombre_congreso:
            data['nombre_congreso'] = form.nombre_congreso.data
        if form.para_curriculum.data != articulo.para_curriculum:
            data['para_curriculum'] = form.para_curriculum.data
        if form.factor_impacto.data != articulo.factor_impacto:
            data['factor_impacto'] = form.factor_impacto.data
        if form.citas.data != articulo.citas:
            data['citas'] = form.citas.data if form.citas.data else 0
        
        # Actualizar autores
        from app.models import ArticuloAutor
        from app.models.relations import ArticuloIndexacion
        from app import db
        
        # Eliminar autores actuales
        ArticuloAutor.query.filter_by(articulo_id=id).delete()
        
        # Agregar nuevos autores
        if form.autores.data:
            for autor_data in form.autores.data:
                if autor_data.get('autor_id'):
                    articulo_autor = ArticuloAutor(
                        articulo_id=id,
                        autor_id=autor_data['autor_id'],
                        orden=autor_data.get('orden', 1),
                        es_corresponsal=autor_data.get('es_corresponsal', False)
                    )
                    db.session.add(articulo_autor)
        
        # Actualizar indexaciones
        # Eliminar indexaciones actuales
        ArticuloIndexacion.query.filter_by(articulo_id=id).delete()
        
        # Agregar nuevas indexaciones seleccionadas
        if form.indexaciones.data:
            for indexacion_id in form.indexaciones.data:
                if indexacion_id:  # Asegurar que no sea 0 o vacío
                    articulo_indexacion = ArticuloIndexacion(
                        articulo_id=id,
                        indexacion_id=indexacion_id
                    )
                    db.session.add(articulo_autor)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar autores: {str(e)}")
            flash('Error al actualizar autores', 'error')
            return render_template('articles/form.html', form=form, articulo=articulo, autor_choices=autor_choices)
        
        # Si hay cambios en el artículo, actualizar
        if data:
            articulo_actualizado, error = ArticleController.update(id, data)
            
            if error:
                flash(f'Error al actualizar artículo: {error}', 'error')
            else:
                flash(f'Artículo "{articulo_actualizado.titulo}" actualizado exitosamente', 'success')
                return redirect(url_for('articles.show', id=articulo_actualizado.id))
        else:
            flash('Artículo actualizado exitosamente', 'success')
            return redirect(url_for('articles.show', id=id))
    
    return render_template('articles/form.html', form=form, articulo=articulo, autor_choices=autor_choices)
@articles_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """
    Eliminar artículo (soft delete por defecto).
    POST /articles/<id>/delete
    """
    # Verificar si se solicita eliminación física
    hard_delete = request.form.get('hard_delete', 'false').lower() == 'true'
    
    success, error = ArticleController.delete(id, soft=not hard_delete)
    
    if error:
        flash(f'Error al eliminar artículo: {error}', 'error')
        return redirect(url_for('articles.index'))
    
    tipo_eliminacion = 'permanentemente' if hard_delete else 'lógicamente'
    flash(f'Artículo eliminado {tipo_eliminacion}', 'success')
    return redirect(url_for('articles.index'))


@articles_bp.route('/<int:id>/restore', methods=['POST'])
def restore(id):
    """
    Restaurar artículo eliminado lógicamente.
    POST /articles/<id>/restore
    """
    articulo, error = ArticleController.restore(id)
    
    if error:
        flash(f'Error al restaurar artículo: {error}', 'error')
        return redirect(url_for('articles.index'))
    
    flash(f'Artículo "{articulo.titulo}" restaurado exitosamente', 'success')
    return redirect(url_for('articles.show', id=id))


@articles_bp.route('/upload', methods=['GET'])
def upload_form():
    """
    Mostrar formulario de upload de PDFs.
    GET /articles/upload
    """
    return render_template('articles/upload.html')


@articles_bp.route('/upload', methods=['POST'])
def upload_pdfs():
    """
    Procesar múltiples PDFs en paralelo y crear artículos automáticamente.
    POST /articles/upload
    
    Recibe:
        - pdfs: Lista de archivos FileStorage
    
    Retorna:
        - JSON con resultados del procesamiento
    """
    try:
        # Obtener archivos del request
        files = request.files.getlist('pdfs')
        
        if not files or len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No se recibieron archivos'
            }), 400
        
        # Validar número de archivos
        MAX_FILES = 10
        if len(files) > MAX_FILES:
            return jsonify({
                'success': False,
                'error': f'Máximo {MAX_FILES} archivos permitidos'
            }), 400
        
        # Filtrar archivos vacíos
        files = [f for f in files if f.filename]
        
        if len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No se recibieron archivos válidos'
            }), 400
        
        logger.info(f"Procesando {len(files)} archivos PDF")
        
        # Crear procesador
        from flask import current_app
        upload_folder = Config.UPLOAD_FOLDER
        processor = PDFBatchProcessor(
            upload_folder=upload_folder,
            max_workers=min(5, len(files)),  # Máximo 5 threads en paralelo
            app=current_app._get_current_object()
        )
        
        # Procesar archivos
        results = processor.process_files(files)
        
        logger.info(f"Procesamiento completado: {results['success']} éxitos, {results['errors']} errores")
        
        # Retornar resultados
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error en upload_pdfs: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500


@articles_bp.route('/export')
def export_excel():
    """
    Exporta artículos a Excel con filtros opcionales.
    GET /articles/export?anio_inicio=2020&anio_fin=2024&tipo_produccion_id=1
    """
    try:
        # Obtener filtros de la URL (mismos que en la lista)
        filters = {
            'tipo_id': request.args.get('tipo_id', type=int),
            'estado_id': request.args.get('estado_id', type=int),
            'lgac_id': request.args.get('lgac_id', type=int),
            'anio_inicio': request.args.get('anio_inicio', type=int),
            'anio_fin': request.args.get('anio_fin', type=int),
            'autor_id': request.args.get('autor_id', type=int),
            'indexacion_id': request.args.get('indexacion_id', type=int),
            'para_curriculum': request.args.get('para_curriculum', type=bool),
            'completo': request.args.get('completo', type=bool),
            'search': request.args.get('query', '').strip(),
            'activo': True  # Solo artículos activos por defecto
        }
        
        # Remover filtros vacíos
        filters = {k: v for k, v in filters.items() if v is not None and v != ''}
        
        logger.info(f"Exportando artículos con filtros: {filters}")
        
        # Generar reporte
        controller = ReportController()
        excel_file, filename = controller.export_excel(filters)
        
        # Enviar archivo
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error exportando a Excel: {str(e)}", exc_info=True)
        flash(f'Error al generar el archivo Excel: {str(e)}', 'error')
        return redirect(url_for('articles.index'))


@articles_bp.route('/export/preview')
def export_preview():
    """
    Muestra estadísticas de lo que se exportará antes de generar el archivo.
    GET /articles/export/preview?anio_inicio=2020
    """
    try:
        # Obtener filtros
        filters = {
            'tipo_id': request.args.get('tipo_id', type=int),
            'estado_id': request.args.get('estado_id', type=int),
            'lgac_id': request.args.get('lgac_id', type=int),
            'anio_inicio': request.args.get('anio_inicio', type=int),
            'anio_fin': request.args.get('anio_fin', type=int),
            'autor_id': request.args.get('autor_id', type=int),
            'indexacion_id': request.args.get('indexacion_id', type=int),
            'para_curriculum': request.args.get('para_curriculum', type=bool),
            'completo': request.args.get('completo', type=bool),
            'search': request.args.get('query', '').strip(),
            'activo': True
        }
        
        # Remover filtros vacíos
        filters = {k: v for k, v in filters.items() if v is not None and v != ''}
        
        # Obtener estadísticas
        controller = ReportController()
        stats = controller.get_export_statistics(filters)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo preview: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
