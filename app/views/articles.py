"""
Blueprint de artículos - CRUD y gestión de artículos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.controllers.article_controller import ArticleController
from app.forms.article_form import ArticleForm, ArticleSearchForm
from app.forms.utils import populate_form_choices
from app.models import Articulo

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
    form = ArticleForm()
    
    # Poblar campos de selección (catálogos)
    populate_form_choices(form)
    
    if form.validate_on_submit():
        # Extraer datos del formulario
        data = {
            'titulo': form.titulo.data,
            'titulo_revista': form.titulo_revista.data,
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
            'quartil': form.quartil.data,
            'citas': form.citas.data if form.citas.data else 0,
        }
        
        # Crear artículo usando el controlador
        articulo, error = ArticleController.create(data)
        
        if error:
            flash(f'Error al crear artículo: {error}', 'error')
        else:
            flash(f'Artículo "{articulo.titulo}" creado exitosamente', 'success')
            return redirect(url_for('articles.show', id=articulo.id))
    
    return render_template('articles/form.html', form=form, articulo=None)


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
    # Obtener artículo actual
    articulo, error = ArticleController.get_by_id(id)
    
    if error:
        flash(error, 'error')
        abort(404)
    
    # Crear formulario pre-llenado con datos actuales
    form = ArticleForm(obj=articulo)
    
    # Poblar campos de selección
    populate_form_choices(form)
    
    if form.validate_on_submit():
        # Extraer solo campos modificados
        data = {}
        
        if form.titulo.data != articulo.titulo:
            data['titulo'] = form.titulo.data
        if form.titulo_revista.data != articulo.titulo_revista:
            data['titulo_revista'] = form.titulo_revista.data
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
        if form.quartil.data != articulo.quartil:
            data['quartil'] = form.quartil.data
        if form.citas.data != articulo.citas:
            data['citas'] = form.citas.data if form.citas.data else 0
        
        # Si hay cambios, actualizar
        if data:
            articulo_actualizado, error = ArticleController.update(id, data)
            
            if error:
                flash(f'Error al actualizar artículo: {error}', 'error')
            else:
                flash(f'Artículo "{articulo_actualizado.titulo}" actualizado exitosamente', 'success')
                return redirect(url_for('articles.show', id=articulo_actualizado.id))
        else:
            flash('No se detectaron cambios', 'info')
            return redirect(url_for('articles.show', id=id))
    
    return render_template('articles/form.html', form=form, articulo=articulo)


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
        return redirect(url_for('articles.show', id=id))
    
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
