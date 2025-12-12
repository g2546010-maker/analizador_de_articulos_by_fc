# Sistema de Gestión de Artículos Académicos

## Descripción General

Aplicación web local desarrollada en Python con Flask para el registro, consulta y gestión de artículos académicos de un Cuerpo Académico. El sistema minimiza la captura manual mediante extracción automática de información desde archivos PDF y cartas de aceptación.

## Características Principales

- **Captura Mínima**: Extracción automática de metadatos desde PDFs y cartas de aceptación
- **Gestión Completa**: Registro, consulta, edición y eliminación de artículos
- **Filtrado Avanzado**: Por año, estado, LGAC y otros campos
- **Exportación a Excel**: Compatible con formato institucional
- **Procesamiento en Background**: Tareas automáticas sin bloquear la interfaz
- **Arquitectura MVC**: Código organizado y mantenible

## Tecnologías

- **Framework Web**: Flask 3.0+
- **ORM**: SQLAlchemy 2.0+
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción opcional)
- **Procesamiento PDF**: PyPDF2, pdfplumber
- **Exportación**: openpyxl
- **Concurrencia**: threading (hilo en background)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)

## Requisitos del Sistema

- **Python 3.12.x** (recomendado para compatibilidad completa)
  - Python 3.14 puede tener problemas con algunos paquetes que requieren compilación
  - Python 3.11 o 3.12 es la versión más estable para este proyecto
- pip (gestor de paquetes de Python)
- Navegador web moderno (Chrome, Firefox, Edge)

## Instalación y Configuración Inicial

### 1. Clonar o Descargar el Proyecto

```bash
git clone <url-del-repositorio>
cd analizador_articulos
```

### 2. Crear Ambiente Virtual

**Windows (usando Python 3.12 específicamente):**

```bash
# Verificar que tienes Python 3.12 instalado
py -3.12 --version

# Crear ambiente virtual con Python 3.12
py -3.12 -m venv venv

# Activar el ambiente
venv\Scripts\activate
```

**Linux/Mac (usando Python 3.12 específicamente):**

```bash
# Verificar que tienes Python 3.12 instalado
python3.12 --version

# Crear ambiente virtual con Python 3.12
python3.12 -m venv venv

# Activar el ambiente
source venv/bin/activate
```

> **Importante**: Usa Python 3.12 para evitar problemas de compatibilidad. El ambiente virtual `venv/` contiene todas las dependencias del proyecto aisladas del sistema. Siempre activa el ambiente antes de trabajar en el proyecto.
>
> Si no tienes Python 3.12, descárgalo desde [python.org](https://www.python.org/downloads/) o usa tu gestor de paquetes del sistema.

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará todas las librerías necesarias:

- Flask, SQLAlchemy, Flask-Migrate (framework y base de datos)
- fuzzywuzzy, python-Levenshtein (matching de autores)
- PyPDF2, pdfplumber, pikepdf (extracción de PDFs)
- openpyxl (exportación a Excel)
- regex (expresiones regulares avanzadas)
- Y más...

> **Nota**: Con Python 3.12, todos los paquetes se instalan correctamente, incluyendo pikepdf y regex que requieren compilación C++.

### 4. Inicializar la Base de Datos

La base de datos se crea automáticamente en la carpeta `instance/` al ejecutar las migraciones.

#### Primera vez iniciando el proyecto:

```bash
# Aplicar las migraciones existentes para crear la base de datos
flask db upgrade

# Poblar catálogos iniciales (tipos de producción, estados, países, etc.)
python scripts/seed_catalogs.py
```

**¡Importante!** Ejecuta `seed_catalogs.py` solo la primera vez. Este script llena las tablas de catálogos con datos iniciales necesarios para el funcionamiento del sistema.

#### Si necesitas reiniciar la base de datos:

```bash
# Eliminar la base de datos existente
# Windows:
Remove-Item instance\articulos.db

# Linux/Mac:
rm instance/articulos.db

# Volver a crear aplicando migraciones
flask db upgrade

# Poblar catálogos
python scripts/seed_catalogs.py
```

> **Nota sobre migraciones**: Este proyecto usa Flask-Migrate (Alembic) para control de versiones de la base de datos. Nunca uses `db.create_all()` directamente ya que esto omite el sistema de migraciones. Siempre usa `flask db upgrade` para crear o actualizar la base de datos.

### 5. Ejecutar la Aplicación

```bash
python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

### 6. Verificar la Instalación

Abre tu navegador y accede a `http://localhost:5000`. Deberías ver:

- La página de inicio con el menú de navegación
- Secciones: Inicio, Artículos, Subir PDF, Catálogos, Reportes
- Interfaz con Bootstrap 5

## Scripts Útiles

### Poblar Catálogos

```bash
python scripts/seed_catalogs.py
```

Crea registros iniciales en:

- Tipos de producción (8 tipos)
- Propósitos (6 propósitos)
- Estados (9 estados)
- LGAC (3 ejemplos - **personalizar según tu CA**)
- Indexaciones (13 indexaciones)
- Países (20 países)

### Actualizar Nombres Normalizados de Autores

```bash
python scripts/actualizar_nombres_normalizados.py
```

Actualiza el campo `nombre_normalizado` para todos los autores existentes. Ejecutar después de importaciones masivas.

## Ubicación de Archivos Importantes

### Base de Datos

La base de datos SQLite se guarda en: `instance/articulos.db`

**Importante**: La carpeta `instance/` está incluida en `.gitignore` para evitar subir datos locales al repositorio. Cada desarrollador tendrá su propia base de datos local.

### Migraciones

Las migraciones de la base de datos se encuentran en: `migrations/versions/`

Estas **SÍ se incluyen** en el repositorio para mantener sincronizado el esquema de la base de datos entre todos los desarrolladores.

### Archivos Subidos

- PDFs cargados: `uploads/pdfs/`
- Archivos Excel exportados: `exports/excel/`

Estas carpetas también están en `.gitignore`.

## Desactivar el Ambiente Virtual

Cuando termines de trabajar:

```bash
deactivate
```

## Solución de Problemas Comunes

### Error: "python no es reconocido" o "Python 3.12 no encontrado"

**Problema**: No tienes Python 3.12 instalado o no está en el PATH.

**Solución**:

1. Descarga Python 3.12.x desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marca "Add Python to PATH"
3. Verifica la instalación:
   ```bash
   py -3.12 --version  # Windows
   python3.12 --version  # Linux/Mac
   ```

### Error al compilar pikepdf o regex

**Problema**: Estás usando Python 3.14 u otra versión incompatible.

**Solución**:

1. Elimina el ambiente virtual: `Remove-Item -Recurse venv` (Windows) o `rm -rf venv` (Linux/Mac)
2. Instala Python 3.12 si no lo tienes
3. Recrea el ambiente con Python 3.12:
   ```bash
   py -3.12 -m venv venv  # Windows
   python3.12 -m venv venv  # Linux/Mac
   ```
4. Activa e instala: `venv\Scripts\activate; pip install -r requirements.txt`

### Error: "flask: command not found"

Asegúrate de que el ambiente virtual está activado:

```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Error: "No module named 'flask'"

Instala las dependencias con el ambiente activado:

```bash
pip install -r requirements.txt
```

### Error: "Can't locate revision..." o problemas con migraciones

La base de datos tiene un estado inconsistente con las migraciones. Solución:

```bash
# Windows:
Remove-Item instance\articulos.db
flask db upgrade
python scripts\seed_catalogs.py

# Linux/Mac:
rm instance/articulos.db
flask db upgrade
python scripts/seed_catalogs.py
```

**Si el problema persiste** (migraciones corruptas), reinicia el sistema de migraciones:

```bash
# ADVERTENCIA: Esto elimina el historial de migraciones
# Windows:
Remove-Item instance\articulos.db
Remove-Item -Recurse -Force migrations
flask db init
flask db migrate -m "Migracion inicial"
flask db upgrade
python scripts\seed_catalogs.py

# Linux/Mac:
rm instance/articulos.db
rm -rf migrations
flask db init
flask db migrate -m "Migracion inicial"
flask db upgrade
python scripts/seed_catalogs.py
```

### Base de Datos Bloqueada

Si ves "database is locked":

1. Cierra todos los procesos que usen la base de datos
2. Reinicia el servidor Flask
3. En desarrollo, SQLite solo permite una conexión de escritura

## Actualización del Proyecto

Para obtener cambios recientes:

```bash
git pull origin main
pip install -r requirements.txt  # Por si hay nuevas dependencias
flask db upgrade                  # Aplicar nuevas migraciones
```

## Estructura del Proyecto

```
analizador_articulos/
├── app/
│   ├── __init__.py           # Inicialización de Flask
│   ├── models/               # Modelos de datos (ORM)
│   ├── controllers/          # Lógica de negocio
│   ├── views/                # Rutas y endpoints
│   ├── services/             # Servicios auxiliares
│   ├── templates/            # Plantillas HTML
│   ├── static/               # CSS, JS, imágenes
│   └── utils/                # Utilidades
├── migrations/               # Migraciones de BD
├── uploads/                  # Archivos subidos
├── exports/                  # Archivos exportados
├── config.py                 # Configuración
├── requirements.txt          # Dependencias
└── run.py                    # Punto de entrada
```

## Casos de Uso Principales

### 1. Registro de Artículo

1. Usuario sube PDF o carta de aceptación
2. Sistema extrae automáticamente: título, autores, año, revista
3. Usuario completa campos faltantes
4. Sistema valida y guarda

### 2. Consulta y Filtrado

1. Usuario accede a la lista de artículos
2. Aplica filtros (año, estado, LGAC)
3. Visualiza resultados en tabla
4. Puede editar o eliminar registros

### 3. Exportación

1. Usuario solicita exportación
2. Sistema genera Excel con formato institucional
3. Descarga automática del archivo

### 4. Procesamiento Automático

1. Hilo en background detecta artículos incompletos
2. Notifica al usuario
3. Genera reportes periódicos

## Modelo de Datos

### Tablas Principales

- **articulos**: Información de cada artículo
- **autores**: Catálogo de autores
- **revistas**: Catálogo de revistas
- **tipos_produccion**: Catálogo de tipos
- **estados**: Catálogo de estados
- **lgac**: Líneas de Generación y Aplicación del Conocimiento
- **paises**: Catálogo de países
- **indexaciones**: Tipos de indexación (Scopus, WoS, etc.)

### Relaciones

- Artículo ↔ Autores (N:N)
- Artículo → Revista (N:1)
- Artículo → Tipo Producción (N:1)
- Artículo → Estado (N:1)
- Artículo → LGAC (N:1)
- Revista → País (N:1)
- Revista ↔ Indexaciones (N:N)

## Roadmap de Desarrollo

### Fase 1: MVP Base (2 semanas)

- [ ] Configuración inicial del proyecto
- [ ] Modelos de base de datos
- [ ] CRUD básico de artículos
- [ ] Interfaz web simple

### Fase 2: Extracción Automática (2 semanas)

- [ ] Upload de archivos PDF
- [ ] Extracción de metadatos
- [ ] Pre-llenado de formularios

### Fase 3: Funcionalidades Avanzadas (2 semanas)

- [ ] Sistema de filtrado
- [ ] Exportación a Excel
- [ ] Validaciones completas

### Fase 4: Concurrencia y Optimización (1 semana)

- [ ] Hilo en background
- [ ] Detección de artículos incompletos
- [ ] Optimización de rendimiento

## Contribución

Este es un proyecto académico. Para modificaciones:

1. Documentar cambios en el código
2. Seguir convenciones de nombrado
3. Actualizar documentación si es necesario

## Licencia

Proyecto académico - Uso educativo

## Contacto

Proyecto desarrollado para el Cuerpo Académico - Maestría en Tecnologías de Programación

---

**Versión**: 1.0.0 (MVP)  
**Última actualización**: Diciembre 2025
