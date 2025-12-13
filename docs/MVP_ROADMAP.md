# Plan de Implementación MVP

## Resumen Ejecutivo

Este documento presenta el roadmap detallado para implementar el MVP (Producto Mínimo Viable) del Sistema de Gestión de Artículos Académicos. El proyecto se divide en 4 fases principales con duración estimada de **6-7 semanas**.

---

## Fases del Proyecto

### 📋 FASE 1: Configuración Base (Semana 1)

**Objetivo**: Establecer la infraestructura del proyecto y configuración inicial.

#### Tareas

1. **Setup del Proyecto** (2 días)

   - [x] Crear estructura de directorios
   - [x] Configurar entorno virtual
   - [x] Instalar dependencias (`requirements.txt`)
   - [x] Configurar variables de entorno (`.env`)
   - [x] Inicializar Git y primer commit

2. **Configuración de Base de Datos** (2 días)

   - [x] Configurar SQLAlchemy
   - [x] Crear modelos base (Artículo, Autor, Revista)
   - [x] Crear modelos de catálogos
   - [x] Configurar Flask-Migrate
   - [x] Generar primera migración
   - [x] Crear script de seed data (catálogos iniciales)

3. **Estructura MVC Base** (1 día)
   - [x] Implementar Factory Pattern en `app/__init__.py`
   - [x] Crear Blueprints básicos (main, articles, catalogs)
   - [x] Configurar routing básico
   - [x] Crear template base con Bootstrap

**Entregables**:

- ✅ Proyecto configurado y funcionando
- ✅ Base de datos inicializada con catálogos
- ✅ Estructura MVC implementada
- ✅ Aplicación arranca sin errores

---

### 🏗️ FASE 2: CRUD de Artículos (Semanas 2-3)

**Objetivo**: Implementar funcionalidad completa de gestión de artículos.

#### Tareas

4. **Modelos y Relaciones** (2 días) ✅

   - [x] Completar modelo `Articulo` con todas las relaciones
   - [x] Implementar métodos `to_dict()` y validaciones
   - [x] Crear tablas de asociación (N:N)
   - [x] Testear queries básicas

5. **Formularios** (2 días) ✅

   - [x] Crear `ArticleForm` con Flask-WTF
   - [x] Implementar validaciones de campos
   - [x] Crear campos dinámicos (SelectField para catálogos)
   - [x] Agregar validación de ISSN, DOI, año

6. **Controladores** (3 días) ✅

   - [x] `ArticleController.create()` - Crear artículo
   - [x] `ArticleController.get_all()` - Listar con paginación
   - [x] `ArticleController.get_by_id()` - Detalle
   - [x] `ArticleController.update()` - Editar
   - [x] `ArticleController.delete()` - Eliminación lógica
   - [x] Implementar manejo de errores

7. **Vistas (Routes)** (2 días) ✅

   - [x] `GET /articles` - Lista de artículos
   - [x] `GET /articles/new` - Formulario crear
   - [x] `POST /articles/new` - Procesar creación
   - [x] `GET /articles/<id>` - Detalle
   - [x] `GET /articles/<id>/edit` - Formulario editar
   - [x] `POST /articles/<id>/edit` - Procesar edición
   - [x] `POST /articles/<id>/delete` - Eliminar

8. **Templates** (2 días)
   - [ ] `articles/list.html` - Tabla de artículos
   - [ ] `articles/form.html` - Formulario (crear/editar)
   - [ ] `articles/detail.html` - Vista detallada
   - [ ] Agregar paginación
   - [ ] Agregar mensajes flash

**Entregables**:

- ✅ CRUD completo de artículos
- ✅ Interfaz funcional
- ✅ Validaciones implementadas

---

### 📄 FASE 3: Extracción de PDFs y Upload (Semanas 3-4)

**Objetivo**: Implementar extracción automática de metadatos desde PDFs.

#### Tareas

9. **Servicio de Upload** (2 días)

   - [ ] Crear `FileHandler` para manejo de archivos
   - [ ] Implementar validación de tipo MIME
   - [ ] Configurar carpeta de uploads
   - [ ] Generar nombres únicos de archivo
   - [ ] Implementar limpieza de archivos antiguos

10. **Servicio de Extracción PDF** (3 días)

    - [ ] Crear `PDFService.extract_text()`
    - [ ] Implementar extracción de título
    - [ ] Implementar extracción de autores
    - [ ] Implementar extracción de año
    - [ ] Implementar extracción de DOI
    - [ ] Implementar extracción de ISSN
    - [ ] Implementar extracción de resumen
    - [ ] Manejo de errores y PDFs mal formateados

11. **Integración Upload + Extracción** (2 días)

    - [ ] Crear ruta `POST /articles/upload`
    - [ ] Procesar PDF y extraer metadatos
    - [ ] Pre-llenar formulario con datos extraídos
    - [ ] Permitir edición antes de guardar
    - [ ] Asociar PDF al artículo

12. **Interfaz de Upload** (2 días)
    - [ ] Template `articles/upload.html`
    - [ ] Drag & drop de archivos
    - [ ] Barra de progreso
    - [ ] Preview de metadatos extraídos
    - [ ] Formulario de confirmación

**Entregables**:

- ✅ Upload de PDFs funcional
- ✅ Extracción automática implementada
- ✅ Pre-llenado de formularios
- ✅ 70% de éxito en extracción

---

### 🔍 FASE 4: Filtrado y Consultas (Semana 4)

**Objetivo**: Implementar sistema de filtrado avanzado.

#### Tareas

13. **Filtros en Backend** (2 días)

    - [ ] Implementar filtro por año
    - [ ] Implementar filtro por estado
    - [ ] Implementar filtro por LGAC
    - [ ] Implementar filtro por autor
    - [ ] Implementar búsqueda por texto (título, revista)
    - [ ] Combinar múltiples filtros

14. **Interfaz de Filtros** (2 días)

    - [ ] Formulario de filtros en `articles/list.html`
    - [ ] Filtros dinámicos con JavaScript
    - [ ] Mantener estado de filtros en URL
    - [ ] Botón "Limpiar filtros"
    - [ ] Contador de resultados

15. **Ordenamiento** (1 día)
    - [ ] Ordenar por año (desc/asc)
    - [ ] Ordenar por título
    - [ ] Ordenar por fecha de registro
    - [ ] Indicadores visuales de ordenamiento

**Entregables**:

- ✅ Filtrado funcional
- ✅ Búsqueda por texto
- ✅ Ordenamiento dinámico

---

### 📊 FASE 5: Exportación a Excel (Semana 5)

**Objetivo**: Generar archivos Excel con formato institucional.

#### Tareas

16. **Servicio de Excel** (3 días)

    - [ ] Crear `ExcelService.generate()`
    - [ ] Implementar mapeo de columnas
    - [ ] Aplicar formato institucional
    - [ ] Manejo de campos vacíos
    - [ ] Generar múltiples hojas (opcional)
    - [ ] Agregar metadatos al archivo

17. **Controlador de Reportes** (1 día)

    - [ ] `ReportController.export_excel()`
    - [ ] Aplicar filtros antes de exportar
    - [ ] Generar nombre de archivo con timestamp

18. **Interfaz de Exportación** (1 día)
    - [ ] Botón "Exportar a Excel" en lista
    - [ ] Modal de confirmación
    - [ ] Opciones: todos o filtrados
    - [ ] Descarga automática

**Entregables**:

- ✅ Exportación a Excel funcional
- ✅ Formato institucional correcto
- ✅ Descarga automática

---

### ⚙️ FASE 6: Hilo en Background (Semana 5-6)

**Objetivo**: Implementar tareas automáticas sin bloquear la interfaz.

#### Tareas

19. **Background Worker** (2 días)

    - [ ] Crear `BackgroundWorker` con threading
    - [ ] Implementar loop principal
    - [ ] Configurar intervalo de ejecución
    - [ ] Manejo de errores sin crashes
    - [ ] Logging de operaciones

20. **Detección de Artículos Incompletos** (2 días)

    - [ ] Definir criterios de "incompleto"
    - [ ] Query para detectar artículos incompletos
    - [ ] Generar reporte en log
    - [ ] Opción de notificación en interfaz

21. **Generación de Reportes Automáticos** (1 día)
    - [ ] Generar Excel periódicamente
    - [ ] Limpiar archivos antiguos (>7 días)
    - [ ] Registrar operaciones en log

**Entregables**:

- ✅ Hilo en background funcional
- ✅ Tareas automáticas implementadas
- ✅ Logs detallados

---

### 🎨 FASE 7: Gestión de Catálogos (Semana 6)

**Objetivo**: Permitir administración de catálogos maestros.

#### Tareas

22. **CRUD de Catálogos** (3 días)

    - [ ] `CatalogController` genérico
    - [ ] Rutas CRUD para cada catálogo
    - [ ] Formularios dinámicos
    - [ ] Templates reutilizables
    - [ ] Activar/Desactivar registros

23. **Catálogos Específicos** (2 días)
    - [ ] Tipos de Producción
    - [ ] Estados
    - [ ] LGACs
    - [ ] Indexaciones
    - [ ] Autores
    - [ ] Revistas
    - [ ] Países

**Entregables**:

- ✅ Gestión completa de catálogos
- ✅ Interfaz consistente

---

### 🧪 FASE 8: Testing y Refinamiento (Semana 7)

**Objetivo**: Asegurar calidad y corregir errores.

#### Tareas

24. **Tests Unitarios** (2 días)

    - [ ] Tests de modelos
    - [ ] Tests de controladores
    - [ ] Tests de servicios
    - [ ] Cobertura >60%

25. **Tests de Integración** (1 día)

    - [ ] Flujo completo: upload → extracción → guardado
    - [ ] Flujo: filtrado → exportación
    - [ ] Tests de background worker

26. **Refinamiento UI/UX** (2 días)

    - [ ] Responsive design
    - [ ] Mensajes de error claros
    - [ ] Validaciones en frontend
    - [ ] Mejoras visuales con Bootstrap

27. **Documentación Final** (1 día)
    - [ ] Actualizar README
    - [ ] Documentar API interna
    - [ ] Guía de usuario básica
    - [ ] Comentarios en código

**Entregables**:

- ✅ Tests implementados
- ✅ Bugs corregidos
- ✅ Documentación completa

---

## Cronograma Visual

```
Semana 1: [████████] Configuración Base
Semana 2: [████████] CRUD Artículos (Parte 1)
Semana 3: [████████] CRUD Artículos (Parte 2) + Upload/PDF (Parte 1)
Semana 4: [████████] Upload/PDF (Parte 2) + Filtrado
Semana 5: [████████] Exportación Excel + Background (Parte 1)
Semana 6: [████████] Background (Parte 2) + Catálogos
Semana 7: [████████] Testing y Refinamiento
```

---

## Prioridades para MVP

### 🔴 Crítico (Must Have)

- CRUD de artículos
- Extracción básica de PDFs
- Exportación a Excel
- Filtrado por año, estado, LGAC
- Hilo en background básico

### 🟡 Importante (Should Have)

- Gestión de catálogos
- Búsqueda por texto
- Validaciones completas
- Interfaz responsive

### 🟢 Deseable (Nice to Have)

- Dashboard con gráficas
- Importación desde Excel
- Búsqueda avanzada por DOI
- Notificaciones en interfaz

---

## Criterios de Éxito del MVP

✅ **Funcionalidad**

- [ ] Registra artículos con <50% captura manual
- [ ] Extrae 70% de metadatos correctamente
- [ ] Exporta Excel con formato institucional
- [ ] Hilo background funciona sin bloqueos

✅ **Rendimiento**

- [ ] Carga de página < 2 segundos
- [ ] Extracción PDF < 10 segundos
- [ ] Soporta 100+ artículos sin problemas

✅ **Código**

- [ ] Arquitectura MVC clara
- [ ] Código documentado
- [ ] Tests con cobertura >60%
- [ ] Sin errores críticos

---

## Riesgos y Mitigaciones

### Riesgo 1: Extracción de PDF imprecisa

**Impacto**: Alto  
**Probabilidad**: Media  
**Mitigación**:

- Implementar múltiples estrategias de extracción
- Permitir edición manual siempre
- Probar con variedad de PDFs

### Riesgo 2: Formato Excel cambia

**Impacto**: Medio  
**Probabilidad**: Baja  
**Mitigación**:

- Mapeo configurable de columnas
- Documentar estructura esperada
- Validar con docente antes de implementar

### Riesgo 3: Hilo background causa problemas

**Impacto**: Medio  
**Probabilidad**: Media  
**Mitigación**:

- Manejo robusto de errores
- Logging detallado
- Posibilidad de deshabilitar

---

## Próximos Pasos (Post-MVP)

**Versión 1.1**

- Dashboard con gráficas (Chart.js)
- Sistema de usuarios básico
- Exportación a otros formatos (CSV, JSON)

**Versión 1.2**

- Integración con APIs externas (Scopus, CrossRef)
- OCR para PDFs escaneados
- Búsqueda full-text en PDFs

**Versión 2.0**

- Migración a PostgreSQL
- Deploy en servidor
- Sistema multi-usuario completo
- API REST

---

## Recursos Necesarios

### Humanos

- 1 Desarrollador full-stack (tú)
- 1 Docente/Usuario para validación

### Tecnológicos

- Python 3.9+
- Editor de código (VS Code)
- Navegador moderno
- PDFs de prueba (variedad)

### Tiempo

- **Desarrollo**: 6-7 semanas
- **Testing**: Continuo + 1 semana final
- **Documentación**: Durante desarrollo

---

## Métricas de Seguimiento

### Semanales

- [ ] Tareas completadas vs. planificadas
- [ ] Errores encontrados y resueltos
- [ ] Tests pasando

### Finales

- [ ] Funcionalidades implementadas
- [ ] Cobertura de tests
- [ ] Documentación completa
- [ ] Aceptación del usuario

---

**Fecha de Inicio**: [A definir]  
**Fecha Estimada de Entrega MVP**: [Inicio + 7 semanas]  
**Revisión de Plan**: Semanal

---

## Notas Importantes

1. Este plan es **flexible** y puede ajustarse según avance el proyecto
2. Priorizar **funcionalidad sobre perfección** en MVP
3. Realizar **demos semanales** para feedback temprano
4. Mantener **documentación actualizada** durante desarrollo
5. **Commits frecuentes** en Git para tracking de progreso
