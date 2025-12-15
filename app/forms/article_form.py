"""
Formulario de Artículo.
Incluye validaciones personalizadas y campos dinámicos.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, DateField,
    IntegerField, FloatField, BooleanField, SubmitField, FieldList, FormField
)
from wtforms.validators import (
    DataRequired, Optional, Length, NumberRange, 
    ValidationError, URL
)
import re
from datetime import datetime


class AuthorSubForm(FlaskForm):
    """
    Sub-formulario para un autor individual.
    """
    class Meta:
        csrf = False  # No CSRF para sub-formularios
    
    autor_id = SelectField(
        'Autor',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un autor')]
    )
    
    orden = IntegerField(
        'Orden',
        validators=[
            DataRequired(message='El orden es obligatorio'),
            NumberRange(min=1, message='El orden debe ser mayor a 0')
        ],
        default=1
    )
    
    es_corresponsal = BooleanField(
        'Autor corresponsal',
        default=False
    )


class ArticleForm(FlaskForm):
    """
    Formulario para crear/editar artículos académicos.
    Incluye validaciones de DOI, ISSN, año y otros campos.
    """
    
    # === Información básica ===
    titulo = StringField(
        'Título del artículo',
        validators=[
            DataRequired(message='El título es obligatorio'),
            Length(max=500, message='El título no puede exceder 500 caracteres')
        ],
        render_kw={'placeholder': 'Ingrese el título completo del artículo'}
    )
    
    titulo_revista = StringField(
        'Título de la revista',
        validators=[
            Optional(),
            Length(max=300, message='El título de revista no puede exceder 300 caracteres')
        ],
        render_kw={'placeholder': 'Nombre de la revista donde se publicó'}
    )
    
    # === Clasificación ===
    tipo_produccion_id = SelectField(
        'Tipo de producción',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un tipo de producción')]
    )
    
    proposito_id = SelectField(
        'Propósito',
        coerce=int,
        validators=[Optional()]
    )
    
    lgac_id = SelectField(
        'LGAC',
        coerce=int,
        validators=[Optional()]
    )
    
    estado_id = SelectField(
        'Estado',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un estado')]
    )
    
    # === Fechas ===
    anio_publicacion = IntegerField(
        'Año de publicación',
        validators=[
            Optional(),
            NumberRange(min=1900, max=2100, message='Año inválido (1900-2100)')
        ],
        render_kw={'placeholder': 'YYYY'}
    )
    
    fecha_publicacion = DateField(
        'Fecha de publicación',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    
    fecha_aceptacion = DateField(
        'Fecha de aceptación',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    
    # === Datos de publicación ===
    revista_id = SelectField(
        'Revista',
        coerce=int,
        validators=[Optional()]
    )
    
    volumen = StringField(
        'Volumen',
        validators=[
            Optional(),
            Length(max=20, message='El volumen no puede exceder 20 caracteres')
        ],
        render_kw={'placeholder': 'Ej: 15'}
    )
    
    numero = StringField(
        'Número',
        validators=[
            Optional(),
            Length(max=20, message='El número no puede exceder 20 caracteres')
        ],
        render_kw={'placeholder': 'Ej: 3'}
    )
    
    pagina_inicio = IntegerField(
        'Página inicio',
        validators=[
            Optional(),
            NumberRange(min=1, message='Debe ser un número positivo')
        ],
        render_kw={'placeholder': '1'}
    )
    
    pagina_fin = IntegerField(
        'Página fin',
        validators=[
            Optional(),
            NumberRange(min=1, message='Debe ser un número positivo')
        ],
        render_kw={'placeholder': '20'}
    )
    
    # === Identificadores ===
    doi = StringField(
        'DOI',
        validators=[
            Optional(),
            Length(max=100, message='El DOI no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': '10.1234/journal.2024.001'}
    )
    
    url = StringField(
        'URL',
        validators=[
            Optional(),
            Length(max=500, message='La URL no puede exceder 500 caracteres'),
            URL(message='URL inválida')
        ],
        render_kw={'placeholder': 'https://...'}
    )
    
    issn = StringField(
        'ISSN',
        validators=[
            Optional(),
            Length(max=20, message='El ISSN no puede exceder 20 caracteres')
        ],
        render_kw={'placeholder': '1234-5678'}
    )
    
    # === Campos específicos para congresos ===
    nombre_congreso = StringField(
        'Nombre del congreso',
        validators=[
            Optional(),
            Length(max=300, message='El nombre del congreso no puede exceder 300 caracteres')
        ],
        render_kw={'placeholder': 'Solo para conference papers'}
    )
    
    # === Indicadores ===
    factor_impacto = FloatField(
        'Factor de impacto',
        validators=[
            Optional(),
            NumberRange(min=0, message='Debe ser un número positivo')
        ],
        render_kw={'placeholder': '2.5', 'step': '0.001'}
    )
    
    citas = IntegerField(
        'Número de citas',
        validators=[
            Optional(),
            NumberRange(min=0, message='Debe ser un número positivo o cero')
        ],
        default=0,
        render_kw={'placeholder': '0'}
    )
    
    # === Autores ===
    autores = FieldList(
        FormField(AuthorSubForm),
        min_entries=0,
        max_entries=20
    )
    
    # === Opciones ===
    para_curriculum = BooleanField(
        'Incluir en curriculum',
        default=True
    )
    
    # === Botones ===
    submit = SubmitField('Guardar artículo')
    
    # === Validaciones personalizadas ===
    
    def validate_doi(self, field):
        """
        Valida el formato del DOI.
        Formato esperado: 10.xxxx/xxxxx
        """
        if field.data:
            doi_pattern = r'^10\.\d{4,}/[\S]+$'
            if not re.match(doi_pattern, field.data):
                raise ValidationError(
                    'DOI inválido. Formato esperado: 10.xxxx/xxxxx'
                )
    
    def validate_issn(self, field):
        """
        Valida el formato del ISSN.
        Formato esperado: XXXX-XXXX
        """
        if field.data:
            issn_pattern = r'^\d{4}-\d{3}[\dX]$'
            if not re.match(issn_pattern, field.data):
                raise ValidationError(
                    'ISSN inválido. Formato esperado: XXXX-XXXX'
                )
    
    def validate_anio_publicacion(self, field):
        """
        Valida que el año de publicación sea razonable.
        No puede ser futuro (excepto año siguiente).
        """
        if field.data:
            current_year = datetime.now().year
            if field.data > current_year + 1:
                raise ValidationError(
                    f'El año no puede ser mayor a {current_year + 1}'
                )
            if field.data < 1900:
                raise ValidationError(
                    'El año debe ser 1900 o posterior'
                )
    
    def validate_pagina_fin(self, field):
        """
        Valida que la página final sea mayor o igual a la página inicial.
        """
        if field.data and self.pagina_inicio.data:
            if field.data < self.pagina_inicio.data:
                raise ValidationError(
                    'La página final debe ser mayor o igual a la página inicial'
                )
    
    def validate_fecha_publicacion(self, field):
        """
        Valida que la fecha de publicación no sea futura.
        """
        if field.data:
            if field.data > datetime.now().date():
                raise ValidationError(
                    'La fecha de publicación no puede ser futura'
                )
    
    def validate_fecha_aceptacion(self, field):
        """
        Valida que la fecha de aceptación sea anterior a la de publicación.
        """
        if field.data and self.fecha_publicacion.data:
            if field.data > self.fecha_publicacion.data:
                raise ValidationError(
                    'La fecha de aceptación debe ser anterior a la de publicación'
                )


class ArticleSearchForm(FlaskForm):
    """
    Formulario para búsqueda y filtrado de artículos.
    """
    
    query = StringField(
        'Buscar',
        validators=[Optional()],
        render_kw={'placeholder': 'Buscar por título, revista...'}
    )
    
    tipo_produccion_id = SelectField(
        'Tipo',
        coerce=int,
        validators=[Optional()]
    )
    
    estado_id = SelectField(
        'Estado',
        coerce=int,
        validators=[Optional()]
    )
    
    lgac_id = SelectField(
        'LGAC',
        coerce=int,
        validators=[Optional()]
    )
    
    anio = IntegerField(
        'Año',
        validators=[
            Optional(),
            NumberRange(min=1900, max=2100, message='Año inválido')
        ],
        render_kw={'placeholder': 'YYYY'}
    )
    
    para_curriculum = SelectField(
        'Para curriculum',
        choices=[
            ('', 'Todos'),
            ('1', 'Sí'),
            ('0', 'No')
        ],
        validators=[Optional()]
    )
    
    submit = SubmitField('Buscar')


class ArticleAuthorForm(FlaskForm):
    """
    Formulario para agregar autores a un artículo.
    """
    
    autor_id = SelectField(
        'Autor',
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar un autor')]
    )
    
    orden = IntegerField(
        'Orden',
        validators=[
            DataRequired(message='El orden es obligatorio'),
            NumberRange(min=1, message='El orden debe ser mayor a 0')
        ],
        default=1,
        render_kw={'placeholder': '1'}
    )
    
    es_corresponsal = BooleanField(
        'Autor corresponsal',
        default=False
    )
    
    submit = SubmitField('Agregar autor')
