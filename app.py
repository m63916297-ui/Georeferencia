"""
SAFE GeoReport - Sistema de Gestión de Incidentes Georreferenciados
====================================================================

Aplicación de reportes de incidentes basada en Geoapify API.
Diseñado para inteligencia segura y siempre activa.

API Key: b4be52d95c1543b99864371eb4562a37
URL Base: https://api.geoapify.com/v1/geocode/search

Autor: SAFE Inteligencia Segura
Versión: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium
import requests
from requests.structures import CaseInsensitiveDict
import os
import json
import uuid


# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================

GEOAPIFY_API_KEY = os.environ.get(
    "GEOAPIFY_API_KEY", "b4be52d95c1543b99864371eb4562a37"
)
GEOAPIFY_BASE_URL = "https://api.geoapify.com/v1"
GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/search"
REVERSE_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/reverse"
IP_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/ip"

MAP_TILES_URL = f"https://maps.geoapify.com/v1/tile/carto/{{z}}/{{x}}/{{y}}.png?apiKey={GEOAPIFY_API_KEY}"

DEFAULT_MAP_CENTER = [4.5709, -74.2973]
DEFAULT_ZOOM = 10

DATA_FILE = "georeferencia/data/incidents.json"


# =============================================================================
# MODELOS DE DATOS
# =============================================================================


class SeverityLevel:
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

    @classmethod
    def all(cls):
        return [cls.BAJO, cls.MEDIO, cls.ALTO, cls.CRITICO]


class IncidentCategory:
    SEGURIDAD = "seguridad"
    INFRAESTRUCTURA = "infraestructura"
    SERVICIOS = "servicios"
    AMBIENTAL = "ambiental"
    TRANSITO = "transito"
    OTRO = "otro"

    @classmethod
    def all(cls):
        return [
            cls.SEGURIDAD,
            cls.INFRAESTRUCTURA,
            cls.SERVICIOS,
            cls.AMBIENTAL,
            cls.TRANSITO,
            cls.OTRO,
        ]


class IncidentStatus:
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"

    @classmethod
    def all(cls):
        return [cls.PENDIENTE, cls.EN_PROCESO, cls.RESUELTO, cls.CERRADO]


CATEGORY_EMOJI = {
    "seguridad": "🔒",
    "infraestructura": "🏗️",
    "servicios": "⚙️",
    "ambiental": "🌿",
    "transito": "🚗",
    "otro": "📌",
}

CATEGORY_ICONS = {
    "seguridad": "lock",
    "infraestructura": "building",
    "servicios": "cogs",
    "ambiental": "leaf",
    "transito": "car",
    "otro": "map-marker",
}

SEVERITY_COLORS = {
    "bajo": "green",
    "medio": "orange",
    "alto": "red",
    "critico": "darkred",
}

STATUS_LABELS = {
    "pendiente": "⏳ Pendiente",
    "en_proceso": "🔄 En Proceso",
    "resuelto": "✅ Resuelto",
    "cerrado": "🔒 Cerrado",
}


# =============================================================================
# SERVICIO DE GEOCODIFICACIÓN (Basado en Geo APIKEY.txt)
# =============================================================================


class GeoapifyService:
    """
    Servicio de geocodificación usando la API de Geoapify.
    Implementación basada en el archivo Geo APIKEY.txt:
    https://api.geoapify.com/v1/geocode/search?text=...&apiKey=...
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEOAPIFY_API_KEY

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Método base para hacer requests usando el formato del archivo APIKEY"""
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException as e:
            st.error(f"Error de conexión: {e}")
        return None

    def geocode(self, address: str) -> Optional[Dict]:
        """
        Geocodifica una dirección usando la API.
        URL: https://api.geoapify.com/v1/geocode/search
        """
        if not address or not address.strip():
            return None

        params = {"text": address.strip(), "apiKey": self.api_key}

        data = self._make_request(GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": result.get("lat", 0.0),
                "longitude": result.get("lon", 0.0),
                "address": result.get("address_line1", "") or "",
                "city": result.get("city", "") or result.get("county", "") or "",
                "country": result.get("country", "") or "",
                "postal_code": result.get("postcode"),
            }
        return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """Geocodificación inversa"""
        params = {"lat": lat, "lon": lon, "apiKey": self.api_key}

        data = self._make_request(REVERSE_GEOCODE_URL, params)

        if data and data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "latitude": lat,
                "longitude": lon,
                "address": result.get("address_line1", "") or "",
                "city": result.get("city", "") or result.get("county", "") or "",
                "country": result.get("country", "") or "",
                "postal_code": result.get("postcode"),
            }
        else:
            return {
                "latitude": lat,
                "longitude": lon,
                "address": f"({lat}, {lon})",
                "city": "Unknown",
                "country": "Unknown",
            }

    def get_ip_location(self) -> Optional[Dict]:
        """Obtiene ubicación basada en IP"""
        params = {"apiKey": self.api_key}

        data = self._make_request(IP_GEOCODE_URL, params)

        if data and data.get("location"):
            loc = data["location"]
            return {
                "latitude": loc.get("lat", 0.0),
                "longitude": loc.get("lon", 0.0),
                "address": "",
                "city": loc.get("city", "") or "Unknown",
                "country": loc.get("country", "") or "Unknown",
            }
        return None

    def test_connection(self) -> bool:
        """Prueba la conexión con la API"""
        try:
            result = self.geocode("Bogota, Colombia")
            return result is not None
        except Exception:
            return False


geo_service = GeoapifyService()


# =============================================================================
# ALMACENAMIENTO (JSON)
# =============================================================================


class IncidentStorage:
    """Sistema de almacenamiento de incidentes en JSON"""

    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read(self) -> List[Dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write(self, data: List[Dict]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create(self, incident: Dict) -> Dict:
        incidents = self._read()
        incident["id"] = str(uuid.uuid4())
        incident["created_at"] = datetime.now().isoformat()
        incident["updated_at"] = datetime.now().isoformat()
        incidents.append(incident)
        self._write(incidents)
        return incident

    def get_all(self) -> List[Dict]:
        return self._read()

    def get_by_id(self, incident_id: str) -> Optional[Dict]:
        for inc in self._read():
            if inc.get("id") == incident_id:
                return inc
        return None

    def update(self, incident_id: str, updates: Dict) -> Optional[Dict]:
        incidents = self._read()
        for i, inc in enumerate(incidents):
            if inc.get("id") == incident_id:
                inc.update(updates)
                inc["updated_at"] = datetime.now().isoformat()
                incidents[i] = inc
                self._write(incidents)
                return inc
        return None

    def delete(self, incident_id: str) -> bool:
        incidents = self._read()
        initial = len(incidents)
        incidents = [i for i in incidents if i.get("id") != incident_id]
        if len(incidents) < initial:
            self._write(incidents)
            return True
        return False

    def get_stats(self) -> Dict:
        incidents = self.get_all()
        return {
            "total": len(incidents),
            "by_category": self._count_by(incidents, "category"),
            "by_severity": self._count_by(incidents, "severity"),
            "by_status": self._count_by(incidents, "status"),
        }

    def _count_by(self, incidents: List[Dict], field: str) -> Dict:
        counts = {}
        for inc in incidents:
            val = inc.get(field)
            if val:
                counts[val] = counts.get(val, 0) + 1
        return counts


storage = IncidentStorage()


# =============================================================================
# FUNCIONES DE INTERFAZ
# =============================================================================


def init_session():
    """Inicializa el estado de la sesión"""
    if "map_center" not in st.session_state:
        st.session_state.map_center = DEFAULT_MAP_CENTER.copy()
    if "pending_location" not in st.session_state:
        st.session_state.pending_location = None
    if "location_confirmed" not in st.session_state:
        st.session_state.location_confirmed = False


def render_header():
    """Renderiza el header de la aplicación"""
    st.set_page_config(
        page_title="SAFE GeoReport - Inteligencia Activa",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <style>
    .safe-header {
        background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 50%, #1565C0 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .safe-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
    }
    .safe-header p {
        color: #BBDEFB;
        margin: 8px 0 0 0;
        font-size: 14px;
    }
    .provider-badge {
        background: linear-gradient(90deg, #4CAF50, #2E7D32);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
    }
    .safe-badge {
        background: linear-gradient(90deg, #FF9800, #F57C00);
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(
            """
        <div class="safe-header">
            <h1>🛡️ SAFE GeoReport</h1>
            <p>Sistema de Inteligencia Segura - Reporte de Incidentes Georreferenciados</p>
            <p style="margin-top: 5px; font-size: 12px; color: #90CAF9;">
                🔗 API: https://api.geoapify.com/v1/geocode/search | 
                Key: b4be52d95c1543b99864371eb4562a37
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<span class="provider-badge">🏢 PROVIDER ACTIVO</span>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<span class="safe-badge">⚡ SAFE INTELIGENCIA</span>',
            unsafe_allow_html=True,
        )


def render_sidebar():
    """Renderiza la barra lateral"""
    st.sidebar.title("🗺️ Navegación")

    menu = [
        "🏠 Dashboard",
        "📝 Reportar Incidente",
        "🗺️ Mapa de Incidentes",
        "📋 Lista de Incidentes",
        "📈 Estadísticas",
        "⚙️ Configuración",
    ]

    choice = st.sidebar.radio("Menú", menu)

    st.sidebar.markdown("---")

    stats = storage.get_stats()
    st.sidebar.markdown("### 📊 Resumen")
    st.sidebar.metric("Total Incidentes", stats["total"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🛡️ SAFE Inteligencia
    
    **Versión:** 1.0.0
    
    **API Geoapify:**
    - Geocoding: ✅ Activo
    - Maps: ✅ Activo
    - IP Location: ✅ Activo
    
    ---
    © 2026 SAFE Inteligencia Segura
    """)

    return choice


def create_map(incidents: List[Dict], center: List = None, zoom: int = DEFAULT_ZOOM):
    """Crea un mapa interactivo con los incidentes"""
    if center is None:
        center = DEFAULT_MAP_CENTER.copy()

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=MAP_TILES_URL,
        attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
    )

    Fullscreen(position="topright").add_to(m)

    if not incidents:
        return m

    for inc in incidents:
        loc = inc.get("location", {})
        lat = loc.get("latitude", 0)
        lon = loc.get("longitude", 0)

        if lat == 0 and lon == 0:
            continue

        cat = inc.get("category", "otro")
        sev = inc.get("severity", "bajo")

        popup = f"""
        <div style="font-family: Arial; min-width: 250px;">
            <h4 style="color: #1E88E5; margin: 0 0 10px 0;">{inc.get("title", "Sin título")}</h4>
            <p><b>📁 Categoría:</b> {CATEGORY_EMOJI.get(cat, "📌")} {cat}</p>
            <p><b>⚠️ Severidad:</b> <span style="color:{SEVERITY_COLORS.get(sev, "blue")}; font-weight:bold;">{sev.upper()}</span></p>
            <p><b>📊 Estado:</b> {STATUS_LABELS.get(inc.get("status", "pendiente"), inc.get("status", "pendiente"))}</p>
            <hr>
            <p style="font-size: 12px; color: #666;">{inc.get("description", "")[:100]}...</p>
            <p style="font-size: 10px; color: #999;">📍 {loc.get("address", "N/A")}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup, max_width=300),
            tooltip=f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')}",
            icon=folium.Icon(
                color=SEVERITY_COLORS.get(sev, "blue"),
                icon=CATEGORY_ICONS.get(cat, "info-sign"),
                prefix="fa",
            ),
        ).add_to(m)

        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=SEVERITY_COLORS.get(sev, "blue"),
            fill=True,
            fillColor=SEVERITY_COLORS.get(sev, "blue"),
            fillOpacity=0.3,
            weight=2,
        ).add_to(m)

    return m


def render_stats(stats: Dict):
    """Renderiza las estadísticas"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total", stats.get("total", 0))
    with col2:
        pend = stats.get("by_status", {}).get("pendiente", 0)
        st.metric("Pendientes", pend)
    with col3:
        proc = stats.get("by_status", {}).get("en_proceso", 0)
        st.metric("En Proceso", proc)
    with col4:
        res = stats.get("by_status", {}).get("resuelto", 0)
        st.metric("Resueltos", res)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Por Categoría")
        cat_data = stats.get("by_category", {})
        if cat_data:
            df_cat = pd.DataFrame(
                list(cat_data.items()), columns=["Categoría", "Cantidad"]
            )
            st.bar_chart(df_cat.set_index("Categoría"))
        else:
            st.info("Sin datos")

    with col2:
        st.subheader("⚠️ Por Severidad")
        sev_data = stats.get("by_severity", {})
        if sev_data:
            df_sev = pd.DataFrame(
                list(sev_data.items()), columns=["Severidad", "Cantidad"]
            )
            st.bar_chart(df_sev.set_index("Severidad"))
        else:
            st.info("Sin datos")


# =============================================================================
# PÁGINAS DE LA APLICACIÓN
# =============================================================================


def page_dashboard():
    """Página principal del dashboard"""
    st.title("📊 Dashboard SAFE")
    st.markdown("### Vista general del sistema de gestión de incidentes")

    stats = storage.get_stats()
    render_stats(stats)

    st.markdown("---")
    st.subheader("🗺️ Mapa de Incidentes")

    incidents = storage.get_all()

    col_map, col_list = st.columns([2, 1])

    with col_map:
        if incidents:
            m = create_map(incidents, st.session_state.map_center)
            st_folium(m, width=700, height=450, key="dash_map")
        else:
            m = create_map([], DEFAULT_MAP_CENTER)
            st_folium(m, width=700, height=450)
            st.info("No hay incidentes registrados")

    with col_list:
        st.markdown("#### 📋 Recientes")
        recent = sorted(incidents, key=lambda x: x.get("created_at", ""), reverse=True)[
            :5
        ]
        for inc in recent:
            sev = inc.get("severity", "bajo")
            color = SEVERITY_COLORS.get(sev, "blue")
            st.markdown(
                f"**{CATEGORY_EMOJI.get(inc.get('category', 'otro'), '📌')} {inc.get('title', '')}**"
            )
            st.markdown(f":{color}[{sev}] - {inc.get('status', '')}")
            st.markdown("---")


def page_report():
    """Página para reportar incidentes"""
    st.title("📝 Reportar Incidente")
    st.markdown("Complete el formulario para reportar un nuevo incidente")

    with st.form("report_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título *", placeholder="Ej: Bache peligroso en vía principal"
            )
            category = st.selectbox("Categoría *", IncidentCategory.all())
            severity = st.selectbox("Severidad *", SeverityLevel.all())

        with col2:
            reporter = st.text_input("Nombre *", placeholder="Su nombre")
            contact = st.text_input("Contacto *", placeholder="Teléfono o email")

        description = st.text_area(
            "Descripción *",
            height=100,
            placeholder="Describa el incidente detalladamente...",
        )

        st.markdown("---")
        st.subheader("📍 Ubicación")

        method = st.radio(
            "Método:",
            ["🔍 Buscar dirección", "📍 Mi ubicación (IP)", "🗺️ Seleccionar en mapa"],
            horizontal=True,
        )

        location_data = {}

        if method == "🔍 Buscar dirección":
            addr = st.text_input(
                "Dirección:", placeholder="Ej: Calle 72 # 45-12, Bogotá"
            )
            if addr and st.form_submit_button("🔍 Buscar"):
                with st.spinner("Buscando..."):
                    loc = geo_service.geocode(addr)
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(f"✅ {loc.get('address', '')}")
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]
                    else:
                        st.error("No se encontró la dirección")

        elif method == "📍 Mi ubicación (IP)":
            if st.form_submit_button("📍 Obtener"):
                with st.spinner("Obteniendo..."):
                    loc = geo_service.get_ip_location()
                    if loc:
                        location_data = loc
                        st.session_state.pending_location = loc
                        st.session_state.location_confirmed = True
                        st.success(
                            f"✅ {loc.get('city', '')}, {loc.get('country', '')}"
                        )
                        st.session_state.map_center = [
                            loc.get("latitude"),
                            loc.get("longitude"),
                        ]
                    else:
                        st.error("No se pudo obtener")

        elif method == "🗺️ Seleccionar en mapa":
            m = create_map([], st.session_state.map_center)
            clicked = st_folium(
                m,
                width=600,
                height=350,
                key="sel_map",
                returned_objects=["last_clicked"],
            )

            col_lat, col_lon = st.columns(2)
            with col_lat:
                lat = st.number_input("Latitud", value=4.5709, format="%.6f")
            with col_lon:
                lon = st.number_input("Longitud", value=-74.2973, format="%.6f")

            if clicked.get("last_clicked"):
                lat = clicked["last_clicked"]["lat"]
                lon = clicked["last_clicked"]["lng"]

            if st.form_submit_button("✅ Confirmar"):
                loc = geo_service.reverse_geocode(lat, lon)
                if loc:
                    location_data = {**loc, "latitude": lat, "longitude": lon}
                    st.session_state.pending_location = location_data
                    st.session_state.location_confirmed = True
                    st.success(f"✅ {loc.get('address', '')}")

        if st.session_state.location_confirmed and st.session_state.pending_location:
            loc = st.session_state.pending_location
            st.markdown(
                f"""
            <div style="background: #E8F5E9; padding: 15px; border-radius: 10px; 
                        border-left: 4px solid #4CAF50; margin: 10px 0;">
                <b>📍 Ubicación Confirmada</b><br>
                {loc.get("address", "N/A")}<br>
                <small>{loc.get("city", "")} | {loc.get("country", "")}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        submitted = st.form_submit_button(
            "📨 Enviar Reporte", type="primary", use_container_width=True
        )

        if submitted:
            if not title or not description or not reporter or not contact:
                st.error("⚠️ Complete todos los campos requeridos")
            elif not st.session_state.location_confirmed:
                st.error("⚠️ Seleccione una ubicación")
            else:
                incident = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "severity": severity,
                    "location": st.session_state.pending_location,
                    "reporter_name": reporter,
                    "reporter_contact": contact,
                    "status": "pendiente",
                }

                created = storage.create(incident)
                st.session_state.pending_location = None
                st.session_state.location_confirmed = False

                st.success(f"✅ Incidente reportado! ID: {created['id']}")
                st.balloons()


def page_map():
    """Página del mapa de incidentes"""
    st.title("🗺️ Mapa de Incidentes")
    st.markdown("Visualización geoespacial interactiva")

    col1, col2, col3 = st.columns(3)
    with col1:
        f_cat = st.selectbox("Categoría", ["Todas"] + IncidentCategory.all())
    with col2:
        f_sev = st.selectbox("Severidad", ["Todas"] + SeverityLevel.all())
    with col3:
        f_stat = st.selectbox("Estado", ["Todos"] + IncidentStatus.all())

    incidents = storage.get_all()

    if f_cat != "Todas":
        incidents = [i for i in incidents if i.get("category") == f_cat]
    if f_sev != "Todas":
        incidents = [i for i in incidents if i.get("severity") == f_sev]
    if f_stat != "Todos":
        incidents = [i for i in incidents if i.get("status") == f_stat]

    st.markdown(f"**Total:** {len(incidents)} incidentes")

    if incidents:
        m = create_map(incidents, st.session_state.map_center, zoom=11)
        st_folium(m, width=1000, height=600, key="full_map")
    else:
        m = create_map([], DEFAULT_MAP_CENTER)
        st_folium(m, width=1000, height=600)
        st.warning("No hay incidentes con esos filtros")


def page_list():
    """Página de lista de incidentes"""
    st.title("📋 Lista de Incidentes")
    st.markdown("Gestión de incidentes reportados")

    incidents = storage.get_all()
    st.markdown(f"**Total:** {len(incidents)}")

    if not incidents:
        st.info("No hay incidentes")
        return

    for i, inc in enumerate(incidents):
        cat = inc.get("category", "otro")
        sev = inc.get("severity", "bajo")

        with st.expander(
            f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')} - :{SEVERITY_COLORS.get(sev, 'blue')}[{sev}]"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Categoría:** {cat}")
                st.markdown(f"**Severidad:** {sev}")
                st.markdown(
                    f"**Estado:** {STATUS_LABELS.get(inc.get('status', 'pendiente'))}"
                )
            with col2:
                st.markdown(f"**Reportero:** {inc.get('reporter_name', '')}")
                st.markdown(f"**Contacto:** {inc.get('reporter_contact', '')}")
                st.markdown(f"**Fecha:** {inc.get('created_at', '')[:16]}")

            st.markdown(f"**Descripción:** {inc.get('description', '')}")

            loc = inc.get("location", {})
            st.markdown(f"**📍 Dirección:** {loc.get('address', 'N/A')}")
            st.markdown(
                f"**🗺️ Coordenadas:** ({loc.get('latitude', 0):.6f}, {loc.get('longitude', 0):.6f})"
            )

            col_upd, col_del = st.columns(2)

            with col_upd:
                new_status = st.selectbox(
                    "Cambiar Estado",
                    IncidentStatus.all(),
                    index=IncidentStatus.all().index(inc.get("status", "pendiente"))
                    if inc.get("status", "pendiente") in IncidentStatus.all()
                    else 0,
                    key=f"stat_{inc.get('id')}_{i}",
                )
                if new_status != inc.get("status"):
                    if st.button(f"✅ Actualizar", key=f"btn_{inc.get('id')}_{i}"):
                        storage.update(inc.get("id"), {"status": new_status})
                        st.success("Estado actualizado")
                        st.rerun()

            with col_del:
                if st.button(f"🗑️ Eliminar", key=f"del_{inc.get('id')}_{i}"):
                    storage.delete(inc.get("id"))
                    st.success("Eliminado")
                    st.rerun()


def page_stats():
    """Página de estadísticas"""
    st.title("📈 Estadísticas")
    st.markdown("Análisis de incidentes")

    stats = storage.get_stats()
    render_stats(stats)

    incidents = storage.get_all()

    if incidents:
        st.markdown("---")
        st.subheader("📋 Historial Reciente")

        recent = sorted(incidents, key=lambda x: x.get("created_at", ""), reverse=True)[
            :10
        ]

        for inc in recent:
            sev = inc.get("severity", "bajo")
            color = SEVERITY_COLORS.get(sev, "blue")
            st.markdown(
                f"**{CATEGORY_EMOJI.get(inc.get('category', 'otro'), '📌')} {inc.get('title', '')}**"
            )
            st.markdown(
                f":{color}[{sev}] - {inc.get('status', '')} - {inc.get('created_at', '')[:16]}"
            )


def page_settings():
    """Página de configuración"""
    st.title("⚙️ Configuración")
    st.markdown("Configuración del sistema SAFE")

    st.subheader("🗺️ API de Geoapify")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("API Key", value=GEOAPIFY_API_KEY, type="password")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Probar Conexión"):
            with st.spinner("Probando..."):
                if geo_service.test_connection():
                    st.success("✅ Conexión exitosa")
                else:
                    st.error("❌ Error de conexión")

    st.markdown("---")
    st.subheader("ℹ️ Información")
    st.markdown(f"""
    **SAFE GeoReport Provider v1.0.0**
    
    - **API Key:** `b4be52d95c1543b99864371eb4562a37`
    - **URL Base:** `https://api.geoapify.com/v1`
    - **Tiles:** `https://maps.geoapify.com/v1/tile/carto/{{z}}/{{x}}/{{y}}.png`
    
    🛡️ SAFE Inteligencia Segura - Siempre Activa
    """)


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================


def main():
    """Función principal de la aplicación"""
    init_session()
    render_header()

    choice = render_sidebar()

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📝 Reportar Incidente": page_report,
        "🗺️ Mapa de Incidentes": page_map,
        "📋 Lista de Incidentes": page_list,
        "📈 Estadísticas": page_stats,
        "⚙️ Configuración": page_settings,
    }

    pages[choice]()


if __name__ == "__main__":
    main()
