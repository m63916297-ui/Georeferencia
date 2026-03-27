# GeoReport Provider

Sistema de gestión y reporte de incidentes georreferenciados con Streamlit y Geoapify API.

## API de Geoapify (del archivo Geo APIKEY.txt)

**API Key:** `b4be52d95c1543b99864371eb4562a37`

### URLs de la API:
- **Geocodificación:** `https://api.geoapify.com/v1/geocode/search?text={direccion}&apiKey={apiKey}`
- **Geocodificación Inversa:** `https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={apiKey}`
- **Tiles de Mapa:** `https://maps.geoapify.com/v1/tile/carto/{z}/{x}/{y}.png?apiKey={apiKey}`

### Ejemplo de código (del archivo original):
```python
import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.geoapify.com/v1/geocode/search?text=38%20Upper%20Montagu%20Street%2C%20Westminster%20W1H%201LJ%2C%20United%20Kingdom&apiKey=b4be52d95c1543b99864371eb4562a37"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

resp = requests.get(url, headers=headers)
print(resp.status_code)
```

## Características

- 📍 **Geocodificación** - API de Geoapify para búsqueda de direcciones
- 🗺️ **Mapas interactivos** - Tiles de Geoapify (carto)
- 📝 **Reporte de incidentes** - Formulario completo con geolocalización
- 📊 **Dashboard** - Estadísticas en tiempo real
- 🔄 **Gestión de incidentes** - Actualizar estados y eliminar
- 🔍 **Búsqueda** - Autocompletado de direcciones

## Estructura del Proyecto

```
georeferencia/
├── app/
│   ├── __init__.py
│   ├── models.py          # Modelos de datos
│   ├── storage.py         # Almacenamiento JSON
│   ├── geo_service.py     # Servicio Geoapify (usa API del archivo)
│   ├── utils.py          # Utilidades UI y mapas
│   └── pages.py          # Páginas de Streamlit
├── data/
│   └── incidents.json     # Base de datos
├── .streamlit/
│   ├── config.toml        # Configuración
│   └── secrets.toml       # Secrets (API Key)
├── requirements.txt
├── app.py                 # Entry point
└── README.md
```

## Instalación Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en Streamlit Cloud

### Paso 1: Subir a GitHub
Sube toda la carpeta `georeferencia` a un repositorio de GitHub.

### Paso 2: Configurar en Streamlit Cloud
1. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
2. New app → From existing repo
3. Configura:
   - **Repository:** `[tu-usuario]/[tu-repo]`
   - **Branch:** `main`
   - **Main file path:** `georeferencia/app.py`
   - **Requirements file:** `georeferencia/requirements.txt`

### Paso 3: Secrets (opcional)
En Streamlit Cloud, puedes agregar el secret:
```
GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"
```

O usar el archivo `.streamlit/secrets.toml` ya incluido.

### Paso 4: Deploy
Click en "Deploy"

## Uso de la Aplicación

| Página | Descripción |
|--------|-------------|
| 🏠 Dashboard | Vista general con estadísticas y mapa |
| 📝 Reportar Incidente | Formulario con 3 métodos de ubicación |
| 🗺️ Mapa | Visualización interactiva con filtros |
| 📋 Lista | Gestionar incidentes (cambiar estado/eliminar) |
| 📈 Estadísticas | Gráficos y métricas |
| ⚙️ Configuración | Prueba de conexión API |

## Categorías y Severidad

**Categorías:** Seguridad, Infraestructura, Servicios, Ambiental, Tránsito, Otro

**Severidad:** Bajo (verde), Medio (naranja), Alto (rojo), Crítico (rojo oscuro)

---

**GeoReport Provider v1.0.0** - © 2026
