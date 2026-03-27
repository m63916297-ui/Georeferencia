# 🛡️ SAFE GeoReport

Sistema de Gestión de Incidentes Georreferenciados con Segmentación Estratégica de Variables de Reporte.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                      SAFE GEOREPORT                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Frontend  │  │   Backend   │  │   Storage   │             │
│  │  (Streamlit)│◄─►│  (Python)   │◄─►│   (JSON)    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                 │                 │                    │
│         └─────────────────┼─────────────────┘                    │
│                           ▼                                      │
│              ┌─────────────────────────┐                         │
│              │    Geoapify API         │                         │
│              │  (Geocodificación)      │                         │
│              └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. Capa de Presentación (Frontend)
- **Framework:** Streamlit
- **Mapas:** Folium + streamlit-folium
- **Visualizaciones:** Pandas + Streamlit

### 2. Capa de Lógica de Negocio
- **Segmentación Estratégica:** Sistema de categorización de incidentes
- **Gestión de Estados:** Workflow de incidentes (recibido → resuelto → cerrado)
- **Cálculo de Prioridades:** Asignación automática según severidad e impacto

### 3. Capa de Datos
- **Almacenamiento:** JSON (incidentes.json)
- **Modelos de Datos:** Incident, Location, ReportFilters

### 4. Capa de Servicios Externos
- **Geocodificación:** Conversión de direcciones a coordenadas
- **Mapas Interactivos:** Visualización de incidentes en mapa

---

## Segmentación Estratégica de Variables

El sistema implementa una segmentación estratégica para el reporte de incidentes:

### 📁 Categorías
| ID | Nombre | Descripción |
|----|--------|-------------|
| seguridad | Seguridad | Incidentes de seguridad ciudadana |
| infraestructura | Infraestructura | Problemas de infraestructura urbana |
| servicios | Servicios | Fallas en servicios públicos |
| ambiental | Ambiental | Incidentes ambientales |
| transito | Tránsito | Incidentes de tráfico y transporte |
| emergencias | Emergencias | Situaciones de emergencia |

### 📝 Subcategorías
Cada categoría contiene 8 subcategorías específicas para detalhado de incidentes.

### ⚠️ Niveles de Severidad
| Nivel | Color | Descripción |
|-------|-------|-------------|
| Crítico | 🔴 Oscuro | Riesgo inmediato a vidas o propiedad |
| Alto | 🔴 | Impacto significativo requiere atención urgente |
| Medio | 🟠 | Impacto moderado requiere atención |
| Bajo | 🟢 | Impacto mínimo |

### 📊 Estados del Reporte
1. 📥 Recibido
2. 🔍 Validando
3. 👤 Asignado
4. ⚙️ En Proceso
5. ✅ Resuelto
6. 🔒 Cerrado
7. ❌ Rechazado

### 🎯 Prioridades
| Prioridad | Tiempo de Respuesta |
|-----------|---------------------|
| Urgente | 1 día |
| Alta | 3 días |
| Media | 7 días |
| Baja | 15 días |

### 📢 Fuentes de Reporte
- Ciudadano
- Cámaras de Seguridad
- Sensores IoT
- Línea de Emergencias
- Portal Web
- App Móvil
- Redes Sociales

### 💥 Impacto
| Nivel | Personas Afectadas |
|-------|-------------------|
| Muy Alto | > 1000 |
| Alto | 100 - 1000 |
| Medio | 10 - 100 |
| Bajo | 1 - 10 |

---

## Estructura de Archivos

```
georeferencia/
├── app.py                 # Aplicación principal (todo en uno)
├── requirements.txt       # Dependencias Python
├── data/
│   └── incidents.json    # Base de datos de incidentes
├── .streamlit/
│   ├── config.toml       # Configuración de Streamlit
│   └── secrets.toml     # Secrets (API keys)
├── README.md
└── Geo APIKEY.txt       # Archivo de API (referencia)
```

---

## Funcionalidades

### 🏠 Dashboard
- Vista general del sistema
- Métricas principales (total, pendientes, en proceso, resueltos)
- Mapa de incidentes recientes
- Estadísticas por categoría y severidad

### 📝 Nuevo Reporte
- Formulario completo con segmentación estratégica
- Selección de categoría y subcategoría
- Determinación de severidad y prioridad
- Estimación de impacto
- Ubicación geográfica (3 métodos):
  - Búsqueda por dirección
  - Ubicación por IP
  - Selección en mapa interactivo

### 🗺️ Mapa Global
- Visualización de todos los incidentes
- Filtros múltiples (categoría, severidad, estado, prioridad)
- Mapas interactivos con popups informativos
- Marcadores por severidad

### 📋 Todos los Reportes
- Lista completa de incidentes
- Filtros y búsqueda
- Cambio de estado
- Eliminación de reportes
- Detalle completo de cada incidente

### 📈 Analytics
- Estadísticas detalladas
- Gráficos por categoría
- Distribución por severidad
- Historial reciente

### ⚙️ Configuración
- Información del sistema
- Prueba de conexión API

---

## Uso del Sistema

### Ejecución Local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la aplicación
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

### Despliegue en Streamlit Cloud

1. **Preparar repositorio:**
   - Crear repositorio en GitHub
   - Subir la carpeta `georeferencia/`

2. **Configurar Streamlit Cloud:**
   - Main file: `georeferencia/app.py`
   - Requirements: `georeferencia/requirements.txt`

3. **Deploy:**
   - Click en "Deploy"

---

## Flujo de Trabajo

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Usuario    │────►│   Reporte    │────►│  Validación  │
│  reporta     │     │   creado     │     │   automática │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                                                ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Cerrado    │◄────│   Resuelto    │◄────│   En Proceso │
│   (fin)      │     │   (confirmado)│     │  (asignado)  │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## Características Técnicas

- **Framework UI:** Streamlit
- **Mapas:** Folium + Geoapify
- **Storage:** JSON local
- **API:** RESTful
- **Authentication:** No requerida (demo)
- **Responsive:** Sí

---

## Licencia

© 2026 SAFE Inteligencia Segura - Todos los derechos reservados.
