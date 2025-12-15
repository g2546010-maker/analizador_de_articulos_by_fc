"""
Utilidades para formularios.
Funciones para poblar campos dinámicos desde la base de datos.
"""
from app.models.catalogs import TipoProduccion, Proposito, LGAC, Estado
from app.models.revista import Revista
from app.models.autor import Autor


def populate_tipo_produccion_choices():
    """
    Obtiene las opciones para el campo tipo_produccion_id.
    
    Returns:
        list: Lista de tuplas (id, nombre) ordenadas alfabéticamente
    """
    tipos = TipoProduccion.query.order_by(TipoProduccion.nombre).all()
    return [(0, '-- Seleccione --')] + [(t.id, t.nombre) for t in tipos]


def populate_proposito_choices():
    """
    Obtiene las opciones para el campo proposito_id.
    
    Returns:
        list: Lista de tuplas (id, nombre) ordenadas alfabéticamente
    """
    propositos = Proposito.query.order_by(Proposito.nombre).all()
    return [(0, '-- Seleccione --')] + [(p.id, p.nombre) for p in propositos]


def populate_lgac_choices():
    """
    Obtiene las opciones para el campo lgac_id.
    
    Returns:
        list: Lista de tuplas (id, nombre) ordenadas alfabéticamente
    """
    lgacs = LGAC.query.order_by(LGAC.nombre).all()
    return [(0, '-- Seleccione --')] + [(l.id, l.nombre) for l in lgacs]


def populate_estado_choices():
    """
    Obtiene las opciones para el campo estado_id.
    
    Returns:
        list: Lista de tuplas (id, nombre) ordenadas alfabéticamente
    """
    estados = Estado.query.order_by(Estado.nombre).all()
    return [(0, '-- Seleccione --')] + [(e.id, e.nombre) for e in estados]


def populate_revista_choices():
    """
    Obtiene las opciones para el campo revista_id.
    
    Returns:
        list: Lista de tuplas (id, nombre) ordenadas alfabéticamente
    """
    revistas = Revista.query.order_by(Revista.nombre).all()
    return [(0, '-- Seleccione --')] + [(r.id, r.nombre) for r in revistas]


def populate_autor_choices():
    """
    Obtiene las opciones para el campo autor_id.
    
    Returns:
        list: Lista de tuplas (id, nombre_completo) ordenadas alfabéticamente
    """
    autores = Autor.query.order_by(Autor.nombre, Autor.apellidos).all()
    return [(0, '-- Seleccione --')] + [(a.id, a.nombre_completo) for a in autores]


def populate_form_choices(form):
    """
    Puebla todos los campos de selección de un formulario de artículo.
    
    Args:
        form: Instancia de ArticleForm o ArticleSearchForm
        
    Returns:
        form: El formulario con los campos poblados
    """
    if hasattr(form, 'tipo_produccion_id'):
        form.tipo_produccion_id.choices = populate_tipo_produccion_choices()
    
    if hasattr(form, 'proposito_id'):
        form.proposito_id.choices = populate_proposito_choices()
    
    if hasattr(form, 'lgac_id'):
        form.lgac_id.choices = populate_lgac_choices()
    
    if hasattr(form, 'estado_id'):
        form.estado_id.choices = populate_estado_choices()
    
    if hasattr(form, 'revista_id'):
        form.revista_id.choices = populate_revista_choices()
    
    if hasattr(form, 'autor_id'):
        form.autor_id.choices = populate_autor_choices()
    
    # Poblar choices de autores en sub-formularios
    if hasattr(form, 'autores'):
        autor_choices = populate_autor_choices()
        for autor_form in form.autores:
            if hasattr(autor_form, 'autor_id'):
                autor_form.autor_id.choices = autor_choices
    
    return form


def validate_articulo_data(form_data):
    """
    Validaciones adicionales de negocio para un artículo.
    
    Args:
        form_data (dict): Datos del formulario
        
    Returns:
        tuple: (is_valid, errors_dict)
    """
    errors = {}
    
    # Si el estado es "Publicado", debe tener revista
    if form_data.get('estado_id'):
        estado = Estado.query.get(form_data['estado_id'])
        if estado and estado.nombre == 'Publicado':
            if not form_data.get('revista_id'):
                errors['revista_id'] = 'La revista es obligatoria para artículos publicados'
            if not form_data.get('anio_publicacion'):
                errors['anio_publicacion'] = 'El año es obligatorio para artículos publicados'
    
    # Si tiene DOI, debería tener otros datos
    if form_data.get('doi'):
        if not form_data.get('anio_publicacion'):
            errors['anio_publicacion'] = 'El año es recomendado cuando se especifica DOI'
    
    # Conference paper debe tener nombre de congreso
    if form_data.get('tipo_produccion_id'):
        tipo = TipoProduccion.query.get(form_data['tipo_produccion_id'])
        if tipo and 'conference' in tipo.nombre.lower():
            if not form_data.get('nombre_congreso'):
                errors['nombre_congreso'] = 'El nombre del congreso es obligatorio para conference papers'
    
    return len(errors) == 0, errors
