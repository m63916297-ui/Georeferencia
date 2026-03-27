# 🛡️ SAFE GeoReport - Sistema de Gestión de Incidentes

**Inteligencia Segura y Siempre Activa**

---

## Información de la API (Basado en Geo APIKEY.txt)

### API Key
```
b4be52d95c1543b99864371eb4562a37
```

### URLs de la API
| Servicio | URL |
|----------|-----|
| Geocodificación | `https://api.geoapify.com/v1/geocode/search?text={direccion}&apiKey={apiKey}` |
| Geocodificación Inversa | `https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={apiKey}` |
| Tiles de Mapa | `https://maps.geoapify.com/v1/tile/carto/{z}/{x}/{y}.png?apiKey={apiKey}` |

### Código Original (del archivo)
```python
import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.geoapify.com/v1/geocode/search?text=38%20Upper%20Montagu%20Street%2C%20Westminster%20W1H%201LJ%2C%20United%20Kingdom&apiKey=b4be52d95c1543b99864371eb4562a37"

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

resp = requests.get(url, headers=headers)
print(resp.status_code)
```

---

## Características

- 🛡️ **SAFE Inteligencia** - Sistema siempre activo
- 📍 **Geocodificación** - API de Geoapify para direcciones
- 🗺️ **Mapas Interactivos** - Tiles de Geoapify (carto)
- 📝 **Reporte de Incidentes** - Formulario completo con geolocalización
- 📊 **Dashboard** - Estadísticas en tiempo real
- 🔄 **Gestión** - Actualizar estados y eliminar incidentes

---

## Estructura del Proyecto

```
georeferencia/
├── app.py                 # 📌 Aplicación principal (TODO en uno)
├── requirements.txt       # Dependencias
├── data/
│   └── incidents.json     # Base de datos de incidentes
├── .streamlit/
│   ├── config.toml        # Configuración de Streamlit
│   └── secrets.toml       # Secrets (API Key)
└── README.md
```

---

## Instalación

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Despliegue en Streamlit Cloud

1. **Sube a GitHub:** Toda la carpeta `georeferencia/`

2. **Configura en Streamlit Cloud:**
   - Main file: `georeferencia/app.py`
   - Requirements: `georeferencia/requirements.txt`

3. **Secrets (opcional):**
   ```
   GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"
   ```

4. **Deploy:** Click en "Deploy"

---

## Uso de la Aplicación

| Página | Descripción |
|--------|-------------|
| 🏠 Dashboard | Vista general con estadísticas y mapa |
| 📝 Reportar | Formulario con 3 métodos de ubicación |
| 🗺️ Mapa | Visualización interactiva con filtros |
| 📋 Lista | Gestionar incidentes |
| 📈 Estadísticas | Gráficos y métricas |
| ⚙️ Configuración | Prueba de conexión API |

---

## SAFE Inteligencia - Características

- 🔒 **Seguridad** - Sistema robusto y estable
- ⚡ **Siempre Activo** - Disponibilidad 24/7
- 🧠 **Inteligencia** - Análisis de datos en tiempo real
- 🔗 **Integración** - API de Geoapify conectada

---

## API Key y Credenciales

- **API Key:** `b4be52d95c1543b99864371eb4562a37`
- **Provider:** Geoapify
- **Tipo:** Geocoding API

---

**🛡️ SAFE GeoReport v1.0.0** - © 2026 SAFE Inteligencia Segura
