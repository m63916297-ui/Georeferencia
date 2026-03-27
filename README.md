# GeoReport Provider

Sistema de gestión y reporte de incidentes georreferenciados con Streamlit y Geoapify API.

## Características

- 📍 **Geocodificación** - Uso de API de Geoapify para ubicación
- 🗺️ **Mapa interactivo** - Visualización de incidentes en mapa
- 📝 **Reporte de incidentes** - Formulario completo para reportar
- 📊 **Dashboard** - Estadísticas en tiempo real
- 🔄 **Gestión de incidentes** - Actualizar estados y eliminar

## Estructura del Proyecto

```
georeferencia/
├── app/
│   ├── __init__.py
│   ├── models.py          # Modelos de datos
│   ├── storage.py        # Sistema de almacenamiento JSON
│   ├── geo_service.py    # Servicio de Geoapify
│   ├── utils.py          # Utilidades UI
│   └── pages.py          # Páginas de la app
├── data/
│   └── incidents.json    # Base de datos de incidentes
├── .streamlit/
│   └── config.toml       # Configuración de Streamlit
├── requirements.txt      # Dependencias
├── .env.example          # Variables de entorno
└── app.py                # Punto de entrada
```

## Variables de Entorno

Crear archivo `.env`:
```
GEOAPIFY_API_KEY=b4be52d95c1543b99864371eb4562a37
```

## Despliegue en Streamlit Cloud

1. Subir el proyecto a GitHub
2. Ir a [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conectar repositorio
4. Configurar:
   - Main file: `app.py`
   - Requirements file: `requirements.txt`
5. Deploy

## Ejecución Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Categorías de Incidentes

- 🔒 Seguridad
- 🏗️ Infraestructura
- ⚙️ Servicios
- 🌿 Ambiental
- 🚗 Tránsito
- 📌 Otro

## Severidad

- Bajo (verde)
- Medio (naranja)
- Alto (rojo)
- Crítico (rojo oscuro)
