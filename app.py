"""
🛡️ SAFE GeoReport - Sistema de Gestión de Incidentes
=====================================================

Sistema de Reporte de Incidentes Georreferenciados
Basado en: Segmentación Estratégica de Variables de Reporte
API: Geoapify (b4be52d95c1543b99864371eb4562a37)

Autor: SAFE Inteligencia Segura
Versión: 2.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import folium
from folium.plugins import Fullscreen, LocateControl
from streamlit_folium import st_folium
import requests
from requests.structures import CaseInsensitiveDict
import os
import json
import uuid


# =============================================================================
# CONFIGURACIÓN PRINCIPAL
# =============================================================================

# API de Geoapify (del archivo Geo APIKEY.txt)
GEOAPIFY_API_KEY = "b4be52d95c1543b99864371eb4562a37"
GEOAPIFY_BASE_URL = "https://api.geoapify.com/v1"
GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/search"
REVERSE_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/reverse"
IP_GEOCODE_URL = f"{GEOAPIFY_BASE_URL}/geocode/ip"
MAP_TILES_URL = f"https://maps.geoapify.com/v1/tile/carto/{{z}}/{{x}}/{{y}}.png?apiKey={GEOAPIFY_API_KEY}"

DEFAULT_MAP_CENTER = [4.5709, -74.2973]
DEFAULT_ZOOM = 12
DATA_FILE = "georeferencia/data/incidents.json"


# =============================================================================
# SEGMENTACIÓN ESTRATÉGICA DE VARIABLES DE REPORTE
# =============================================================================


class SegmentacionReporte:
    """
    Segmentación Estratégica de Variables de Reporte
    Basado en el documento: SEGMENTACIÓN ESTRATÉGICA DE LAS VARIABLES DE REPORTE
    """

    # ==================== CATEGORÍAS PRINCIPALES ====================
    class Categoria:
        SEGURIDAD = {
            "id": "seguridad",
            "nombre": "Seguridad",
            "icono": "🔒",
            "descripcion": "Incidentes relacionados con seguridad ciudadana",
            "subcategorias": [
                "Robo/Asalto",
                "Vandalismo",
                "Agresión",
                "Secuestro",
                "Extorsión",
                "Delincuencia",
                "Seguridad Vial",
                "Otro Seguridad",
            ],
        }

        INFRAESTRUCTURA = {
            "id": "infraestructura",
            "nombre": "Infraestructura",
            "icono": "🏗️",
            "descripcion": "Problemas de infraestructura urbana",
            "subcategorias": [
                "Vía dañada",
                "Bache",
                "Semáforo dañado",
                "Alumbrado público",
                "Puente dañado",
                "Edificio en riesgo",
                "Obra abandonada",
                "Otro Infraestructura",
            ],
        }

        SERVICIOS = {
            "id": "servicios",
            "nombre": "Servicios",
            "icono": "⚙️",
            "descripcion": "Fallas en servicios públicos",
            "subcategorias": [
                "Sin agua",
                "Sin luz",
                "Sin gas",
                "Telecomunicaciones",
                "Transporte público",
                "Recolección basura",
                "Salud",
                "Otro Servicios",
            ],
        }

        AMBIENTAL = {
            "id": "ambiental",
            "nombre": "Ambiental",
            "icono": "🌿",
            "descripcion": "Incidentes ambientales",
            "subcategorias": [
                "Contaminación",
                "Deforestación",
                "Residuos peligrosos",
                "Maltrato animal",
                "Extinción",
                "Incendio",
                "Inundación",
                "Otro Ambiental",
            ],
        }

        TRANSITO = {
            "id": "transito",
            "nombre": "Tránsito",
            "icono": "🚗",
            "descripcion": "Incidentes de tráfico y transporte",
            "subcategorias": [
                "Accidente",
                "Congestión",
                "Señalización",
                "Estacionamiento indebido",
                "Vehículo abandonado",
                "Choque",
                "Atropello",
                "Otro Tránsito",
            ],
        }

        EMERGENCIAS = {
            "id": "emergencias",
            "nombre": "Emergencias",
            "icono": "🚨",
            "descripcion": "Situaciones de emergencia",
            "subcategorias": [
                "Incendio",
                "Explosión",
                "Fuga de gas",
                "Emergencia médica",
                "Desastre natural",
                "Evacuación",
                "Alerta sanitaria",
                "Otro Emergencia",
            ],
        }

        @classmethod
        def todas(cls):
            return [
                cls.SEGURIDAD,
                cls.INFRAESTRUCTURA,
                cls.SERVICIOS,
                cls.AMBIENTAL,
                cls.TRANSITO,
                cls.EMERGENCIAS,
            ]

    # ==================== NIVELES DE SEVERIDAD ====================
    class Severidad:
        CRITICO = {
            "id": "critico",
            "nombre": "Crítico",
            "icono": "⛔",
            "color": "darkred",
            "descripcion": "Riesgo inmediato a vidas o propiedad",
            "nivel": 4,
        }

        ALTO = {
            "id": "alto",
            "nombre": "Alto",
            "icono": "🔴",
            "color": "red",
            "descripcion": "Impacto significativo requiere atención urgente",
            "nivel": 3,
        }

        MEDIO = {
            "id": "medio",
            "nombre": "Medio",
            "icono": "🟠",
            "color": "orange",
            "descripcion": "Impacto moderado requiere atención",
            "nivel": 2,
        }

        BAJO = {
            "id": "bajo",
            "nombre": "Bajo",
            "icono": "🟢",
            "color": "green",
            "descripcion": "Impacto minimo o cosmetico",
            "nivel": 1,
        }

        @classmethod
        def todas(cls):
            return [cls.CRITICO, cls.ALTO, cls.MEDIO, cls.BAJO]

    # ==================== ESTADOS DEL REPORTE ====================
    class Estado:
        RECIBIDO = {"id": "recibido", "nombre": "Recibido", "icono": "📥"}
        VALIDANDO = {"id": "validando", "nombre": "Validando", "icono": "🔍"}
        ASIGNADO = {"id": "asignado", "nombre": "Asignado", "icono": "👤"}
        EN_PROCESO = {"id": "en_proceso", "nombre": "En Proceso", "icono": "⚙️"}
        RESUELTO = {"id": "resuelto", "nombre": "Resuelto", "icono": "✅"}
        CERRADO = {"id": "cerrado", "nombre": "Cerrado", "icono": "🔒"}
        RECHAZADO = {"id": "rechazado", "nombre": "Rechazado", "icono": "X"}

        @classmethod
        def todos(cls):
            return [
                cls.RECIBIDO,
                cls.VALIDANDO,
                cls.ASIGNADO,
                cls.EN_PROCESO,
                cls.RESUELTO,
                cls.CERRADO,
                cls.RECHAZADO,
            ]

    # ==================== PRIORIDADES ====================
    class Prioridad:
        URGENTE = {"id": "urgente", "nombre": "Urgente", "dias": 1}
        ALTA = {"id": "alta", "nombre": "Alta", "dias": 3}
        MEDIA = {"id": "media", "nombre": "Media", "dias": 7}
        BAJA = {"id": "baja", "nombre": "Baja", "dias": 15}

        @classmethod
        def todas(cls):
            return [cls.URGENTE, cls.ALTA, cls.MEDIA, cls.BAJA]

    # ==================== FUENTES DE REPORTE ====================
    class Fuente:
        CIUDADANO = {"id": "ciudadano", "nombre": "Ciudadano", "icono": "👤"}
        CAMARAS = {"id": "camaras", "nombre": "Cámaras de Seguridad", "icono": "📹"}
        SENSORES = {"id": "sensores", "nombre": "Sensores IoT", "icono": "📡"}
        EMERGENCIAS = {
            "id": "emergencias",
            "nombre": "Línea de Emergencias",
            "icono": "📞",
        }
        WEB = {"id": "web", "nombre": "Portal Web", "icono": "🌐"}
        MOVIL = {"id": "movil", "nombre": "App Móvil", "icono": "📱"}
        SOCIAL = {"id": "social", "nombre": "Redes Sociales", "icono": "📢"}

        @classmethod
        def todas(cls):
            return [
                cls.CIUDADANO,
                cls.CAMARAS,
                cls.SENSORES,
                cls.EMERGENCIAS,
                cls.WEB,
                cls.MOVIL,
                cls.SOCIAL,
            ]

    # ==================== IMPACTO ====================
    class Impacto:
        MUY_ALTO = {"id": "muy_alto", "nombre": "Muy Alto", "afectados": ">1000"}
        ALTO = {"id": "alto", "nombre": "Alto", "afectados": "100-1000"}
        MEDIO = {"id": "medio", "nombre": "Medio", "afectados": "10-100"}
        BAJO = {"id": "bajo", "nombre": "Bajo", "afectados": "1-10"}

        @classmethod
        def todo(cls):
            return [cls.MUY_ALTO, cls.ALTO, cls.MEDIO, cls.BAJO]


# Mapeos para UI
CATEGORY_EMOJI = {c["id"]: c["icono"] for c in SegmentacionReporte.Categoria.todas()}
SEVERITY_COLORS = {s["id"]: s["color"] for s in SegmentacionReporte.Severidad.todas()}


# =============================================================================
# SERVICIO DE GEOCODIFICACIÓN
# =============================================================================


class GeoapifyService:
    """Servicio de geocodificación usando Geoapify API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEOAPIFY_API_KEY

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
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
        return {
            "latitude": lat,
            "longitude": lon,
            "address": f"({lat}, {lon})",
            "city": "Unknown",
            "country": "Unknown",
        }

    def get_ip_location(self) -> Optional[Dict]:
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
        try:
            return self.geocode("Bogota, Colombia") is not None
        except Exception:
            return False


geo_service = GeoapifyService()


# =============================================================================
# ALMACENAMIENTO
# =============================================================================


class IncidentStorage:
    """Sistema de almacenamiento de incidentes"""

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
            "by_priority": self._count_by(incidents, "priority"),
            "by_impact": self._count_by(incidents, "impact"),
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
# INTERFAZ DE USUARIO
# =============================================================================


def init_session():
    if "map_center" not in st.session_state:
        st.session_state.map_center = DEFAULT_MAP_CENTER.copy()
    if "pending_location" not in st.session_state:
        st.session_state.pending_location = None
    if "location_confirmed" not in st.session_state:
        st.session_state.location_confirmed = False


def render_header():
    st.set_page_config(
        page_title="SAFE GeoReport - Sistema de Incidentes",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <style>
    .safe-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .safe-header h1 {
        color: white;
        margin: 0;
    }
    .badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
    }
    .badge-provider {
        background: linear-gradient(90deg, #4CAF50, #2E7D32);
        color: white;
    }
    .badge-safe {
        background: linear-gradient(90deg, #FF9800, #F57C00);
        color: white;
    }
    .stat-box {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .category-card {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 5px solid;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            """
        <div class="safe-header">
            <h1>🛡️ SAFE GeoReport</h1>
            <p>Sistema de Gestión de Incidentes - Segmentación Estratégica de Variables</p>
            <p style="font-size: 11px; color: #90CAF9;">🔗 API: https://api.geoapify.com/v1/geocode | Key: b4be52d95c1543b99864371eb4562a37</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<span class="badge badge-provider">🏢 PROVIDER ACTIVO</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="badge badge-safe">🛡️ SAFE INTELIGENCIA</span>',
            unsafe_allow_html=True,
        )


def render_sidebar():
    st.sidebar.title("🗺️ Navegación")

    menu = [
        "🏠 Dashboard",
        "📝 Nuevo Reporte",
        "🗺️ Mapa Global",
        "📋 Todos los Reportes",
        "📈 Analytics",
        "⚙️ Configuración",
    ]

    choice = st.sidebar.radio("Menú", menu)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estadísticas Rápidas")

    stats = storage.get_stats()
    st.sidebar.metric("Total Reportes", stats["total"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🛡️ SAFE Inteligencia
    **Versión:** 2.0.0
    
    **API Geoapify:** ✅
    - Geocoding: Activo
    - Maps: Activo
    - IP Location: Activo
    """)

    return choice


def create_map(incidents: List[Dict], center: List = None, zoom: int = DEFAULT_ZOOM):
    if center is None:
        center = DEFAULT_MAP_CENTER.copy()

    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=MAP_TILES_URL,
        attr='&copy; <a href="https://www.geoapify.com/">Geoapify</a>',
    )

    Fullscreen(position="topright").add_to(m)
    LocateControl(auto_start=False).add_to(m)

    for inc in incidents:
        loc = inc.get("location", {})
        lat, lon = loc.get("latitude", 0), loc.get("longitude", 0)

        if lat == 0 and lon == 0:
            continue

        cat, sev = inc.get("category", "seguridad"), inc.get("severity", "bajo")
        popup = f"""
        <div style="font-family: Arial; min-width: 280px;">
            <h4 style="color: #1565C0; margin: 0 0 10px 0;">{inc.get("title", "Sin título")}</h4>
            <p><b>📁 Categoría:</b> {CATEGORY_EMOJI.get(cat, "📌")} {inc.get("subcategoria", cat)}</p>
            <p><b>⚠️ Severidad:</b> <span style="color:{SEVERITY_COLORS.get(sev, "blue")}; font-weight:bold;">{sev.upper()}</span></p>
            <p><b>📊 Estado:</b> {inc.get("status", "recibido")}</p>
            <p><b>🎯 Prioridad:</b> {inc.get("priority", "media")}</p>
            <hr>
            <p style="font-size: 12px;">{inc.get("description", "")[:120]}...</p>
            <p style="font-size: 10px; color: #666;">📍 {loc.get("address", "N/A")}</p>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup, max_width=320),
            tooltip=f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')}",
            icon=folium.Icon(color=SEVERITY_COLORS.get(sev, "blue"), icon="info-sign"),
        ).add_to(m)

        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color=SEVERITY_COLORS.get(sev, "blue"),
            fill=True,
            fillOpacity=0.3,
            weight=2,
        ).add_to(m)

    return m


def render_stats(stats: Dict):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", stats.get("total", 0))
    with col2:
        pend = stats.get("by_status", {}).get("recibido", 0)
        st.metric("Recibidos", pend)
    with col3:
        proc = stats.get("by_status", {}).get("en_proceso", 0)
        st.metric("En Proceso", proc)
    with col4:
        res = stats.get("by_status", {}).get("resuelto", 0)
        st.metric("Resueltos", res)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📁 Por Categoría")
        cat_data = stats.get("by_category", {})
        if cat_data:
            df = pd.DataFrame(list(cat_data.items()), columns=["Categoría", "Cantidad"])
            st.bar_chart(df.set_index("Categoría"))

    with col2:
        st.subheader("⚠️ Por Severidad")
        sev_data = stats.get("by_severity", {})
        if sev_data:
            df = pd.DataFrame(list(sev_data.items()), columns=["Severidad", "Cantidad"])
            st.bar_chart(df.set_index("Severidad"))

    with col3:
        st.subheader("🎯 Por Prioridad")
        pri_data = stats.get("by_priority", {})
        if pri_data:
            df = pd.DataFrame(list(pri_data.items()), columns=["Prioridad", "Cantidad"])
            st.bar_chart(df.set_index("Prioridad"))


# =============================================================================
# PÁGINAS
# =============================================================================


def page_dashboard():
    st.title("📊 Dashboard SAFE")
    st.markdown("### Sistema de Gestión de Incidentes - Segmentación Estratégica")

    stats = storage.get_stats()
    render_stats(stats)

    st.markdown("---")
    st.subheader("🗺️ Mapa de Incidentes")

    incidents = storage.get_all()
    col_map, col_side = st.columns([3, 1])

    with col_map:
        if incidents:
            m = create_map(incidents, st.session_state.map_center)
            st_folium(m, width=800, height=500, key="dash_map")
        else:
            m = create_map([], DEFAULT_MAP_CENTER)
            st_folium(m, width=800, height=500)
            st.info("No hay incidentes registrados")

    with col_side:
        st.markdown("#### 📋 Por Categoría")
        for cat in SegmentacionReporte.Categoria.todas():
            count = stats.get("by_category", {}).get(cat["id"], 0)
            st.markdown(f"{cat['icono']} **{cat['nombre']}**: {count}")


def page_report():
    st.title("📝 Nuevo Reporte de Incidente")
    st.markdown(
        "### Complete el formulario según la Segmentación Estratégica de Variables"
    )

    # Mostrar categorías disponibles
    st.markdown("#### 📁 Seleccione la Categoría")
    cols = st.columns(3)
    for i, cat in enumerate(SegmentacionReporte.Categoria.todas()):
        with cols[i % 3]:
            st.markdown(
                f"""
            <div class="category-card" style="border-left-color: {"#E53935" if cat["id"] == "seguridad" else "#1E88E5" if cat["id"] == "infraestructura" else "#43A047" if cat["id"] == "servicios" else "#8E24AA" if cat["id"] == "ambiental" else "#FB8C00" if cat["id"] == "transito" else "#E53935"}; background: #f5f5f5;">
                <b>{cat["icono"]} {cat["nombre"]}</b><br>
                <small>{cat["descripcion"]}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with st.form("report_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Título del Incidente *", placeholder="Descripción breve del incidente"
            )
            category = st.selectbox(
                "Categoría *",
                [c["id"] for c in SegmentacionReporte.Categoria.todas()],
                format_func=lambda x: (
                    f"{[c['icono'] for c in SegmentacionReporte.Categoria.todas() if c['id'] == x][0]} {[c['nombre'] for c in SegmentacionReporte.Categoria.todas() if c['id'] == x][0]}"
                ),
            )
            subcategoria = st.selectbox(
                "Subcategoría",
                [
                    s
                    for c in SegmentacionReporte.Categoria.todas()
                    if c["id"] == (category or "seguridad")
                    for s in c["subcategorias"]
                ],
            )
            severity = st.selectbox(
                "Severidad *",
                [s["id"] for s in SegmentacionReporte.Severidad.todas()],
                format_func=lambda x: (
                    f"{[s['icono'] for s in SegmentacionReporte.Severidad.todas() if s['id'] == x][0]} {[s['nombre'] for s in SegmentacionReporte.Severidad.todas() if s['id'] == x][0]}"
                ),
            )

        with col2:
            reporter = st.text_input(
                "Reportado por *", placeholder="Nombre del reportante"
            )
            contact = st.text_input("Contacto *", placeholder="Teléfono o email")
            fuente = st.selectbox(
                "Fuente del Reporte",
                [f["id"] for f in SegmentacionReporte.Fuente.todas()],
                format_func=lambda x: (
                    f"{[f['icono'] for f in SegmentacionReporte.Fuente.todas() if f['id'] == x][0]} {[f['nombre'] for f in SegmentacionReporte.Fuente.todas() if f['id'] == x][0]}"
                ),
            )
            priority = st.selectbox(
                "Prioridad",
                [p["id"] for p in SegmentacionReporte.Prioridad.todas()],
                format_func=lambda x: (
                    f"{[p['nombre'] for p in SegmentacionReporte.Prioridad.todas() if p['id'] == x][0]}"
                ),
            )

        impact = st.selectbox(
            "Impacto Estimado",
            [i["id"] for i in SegmentacionReporte.Impacto.todo()],
            format_func=lambda x: (
                f"{[i['nombre'] for i in SegmentacionReporte.Impacto.todo() if i['id'] == x][0]} ({[i['afectados'] for i in SegmentacionReporte.Impacto.todo() if i['id'] == x][0]} afectados)"
            ),
        )

        description = st.text_area(
            "Descripción Detallada *",
            height=120,
            placeholder="Describa el incidente con detalle...",
        )

        st.markdown("---")
        st.subheader("📍 Ubicación del Incidente")

        method = st.radio(
            "Método de ubicación:",
            ["🔍 Buscar dirección", "📍 Mi ubicación (IP)", "🗺️ Seleccionar en mapa"],
            horizontal=True,
        )

        location_data = {}

        if method == "🔍 Buscar dirección":
            addr = st.text_input(
                "Dirección:", placeholder="Ej: Av. Jiménez # 4-35, Bogotá"
            )
            if addr and st.form_submit_button("🔍 Buscar en Geoapify"):
                with st.spinner("Consultando API de Geoapify..."):
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
            if st.form_submit_button("📍 Obtener mi ubicación"):
                with st.spinner("Obteniendo ubicación..."):
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
                lat, lon = (
                    clicked["last_clicked"]["lat"],
                    clicked["last_clicked"]["lng"],
                )

            if st.form_submit_button("✅ Confirmar ubicación"):
                loc = geo_service.reverse_geocode(lat, lon)
                if loc:
                    location_data = {**loc, "latitude": lat, "longitude": lon}
                    st.session_state.pending_location = location_data
                    st.session_state.location_confirmed = True

        if st.session_state.location_confirmed and st.session_state.pending_location:
            loc = st.session_state.pending_location
            st.markdown(
                f"""
            <div style="background: #E3F2FD; padding: 15px; border-radius: 10px; border-left: 4px solid #1565C0;">
                <b>📍 Ubicación Confirmada</b><br>
                {loc.get("address", "N/A")}<br>
                <small>{loc.get("city", "")} | {loc.get("country", "")} | Lat: {loc.get("latitude", 0):.6f}, Lon: {loc.get("longitude", 0):.6f}</small>
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
                st.error("⚠️ Complete todos los campos requeridos (*)")
            elif not st.session_state.location_confirmed:
                st.error("⚠️ Seleccione una ubicación")
            else:
                incident = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "subcategoria": subcategoria,
                    "severity": severity,
                    "priority": priority,
                    "impact": impact,
                    "fuente": fuente,
                    "location": st.session_state.pending_location,
                    "reporter_name": reporter,
                    "reporter_contact": contact,
                    "status": "recibido",
                }

                created = storage.create(incident)
                st.session_state.pending_location = None
                st.session_state.location_confirmed = False

                st.success(f"✅ Reporte creado exitosamente!")
                st.info(f"📋 ID del reporte: `{created['id']}`")
                st.balloons()


def page_map():
    st.title("🗺️ Mapa Global de Incidentes")
    st.markdown("Visualización geoespacial de todos los reportes")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_cat = st.selectbox(
            "Categoría",
            ["Todas"] + [c["id"] for c in SegmentacionReporte.Categoria.todas()],
        )
    with col2:
        f_sev = st.selectbox(
            "Severidad",
            ["Todas"] + [s["id"] for s in SegmentacionReporte.Severidad.todas()],
        )
    with col3:
        f_stat = st.selectbox(
            "Estado", ["Todos"] + [e["id"] for e in SegmentacionReporte.Estado.todos()]
        )
    with col4:
        f_pri = st.selectbox(
            "Prioridad",
            ["Todas"] + [p["id"] for p in SegmentacionReporte.Prioridad.todas()],
        )

    incidents = storage.get_all()

    if f_cat != "Todas":
        incidents = [i for i in incidents if i.get("category") == f_cat]
    if f_sev != "Todas":
        incidents = [i for i in incidents if i.get("severity") == f_sev]
    if f_stat != "Todos":
        incidents = [i for i in incidents if i.get("status") == f_stat]
    if f_pri != "Todas":
        incidents = [i for i in incidents if i.get("priority") == f_pri]

    st.markdown(f"**Total de incidentes:** {len(incidents)}")

    if incidents:
        m = create_map(incidents, st.session_state.map_center, zoom=11)
        st_folium(m, width=1100, height=650, key="full_map")
    else:
        m = create_map([], DEFAULT_MAP_CENTER)
        st_folium(m, width=1100, height=650)


def page_list():
    st.title("📋 Todos los Reportes")
    st.markdown("Gestión completa de incidentes")

    incidents = storage.get_all()
    st.markdown(f"**Total:** {len(incidents)} reportes")

    if not incidents:
        st.info("No hay reportes")
        return

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        f_cat = st.selectbox(
            "Filtrar categoría",
            ["Todas"] + [c["id"] for c in SegmentacionReporte.Categoria.todas()],
        )
    with col2:
        f_stat = st.selectbox(
            "Filtrar estado",
            ["Todos"] + [e["id"] for e in SegmentacionReporte.Estado.todos()],
        )

    if f_cat != "Todas":
        incidents = [i for i in incidents if i.get("category") == f_cat]
    if f_stat != "Todos":
        incidents = [i for i in incidents if i.get("status") == f_stat]

    for i, inc in enumerate(incidents):
        cat, sev = inc.get("category", "seguridad"), inc.get("severity", "bajo")

        with st.expander(
            f"{CATEGORY_EMOJI.get(cat, '📌')} {inc.get('title', '')} | :{SEVERITY_COLORS.get(sev, 'blue')}[{sev.upper()}]"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"**📁 Categoría:** {inc.get('subcategoria', inc.get('category', ''))}"
                )
                st.markdown(f"**⚠️ Severidad:** {inc.get('severity', '')}")
            with col2:
                st.markdown(f"**🎯 Prioridad:** {inc.get('priority', '')}")
                st.markdown(f"**📊 Estado:** {inc.get('status', '')}")
            with col3:
                st.markdown(f"**👤 Reportante:** {inc.get('reporter_name', '')}")
                st.markdown(f"**📅 Fecha:** {inc.get('created_at', '')[:16]}")

            st.markdown(f"**📝 Descripción:** {inc.get('description', '')}")

            loc = inc.get("location", {})
            st.markdown(f"**📍 Ubicación:** {loc.get('address', 'N/A')}")
            st.markdown(
                f"**🗺️ Coordenadas:** ({loc.get('latitude', 0):.6f}, {loc.get('longitude', 0):.6f})"
            )

            col_upd, col_del = st.columns(2)

            with col_upd:
                new_status = st.selectbox(
                    "Cambiar Estado",
                    [e["id"] for e in SegmentacionReporte.Estado.todos()],
                    index=[e["id"] for e in SegmentacionReporte.Estado.todos()].index(
                        inc.get("status", "recibido")
                    )
                    if inc.get("status", "recibido")
                    in [e["id"] for e in SegmentacionReporte.Estado.todos()]
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
    st.title("📈 Analytics")
    st.markdown("Análisis de datos de incidentes")

    stats = storage.get_stats()
    render_stats(stats)


def page_settings():
    st.title("⚙️ Configuración")

    st.subheader("🗺️ API de Geoapify")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input("API Key", value=GEOAPIFY_API_KEY, type="password")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Probar Conexión"):
            with st.spinner("Probando..."):
                if geo_service.test_connection():
                    st.success("✅ Conexión exitosa con Geoapify API")
                else:
                    st.error("❌ Error de conexión")

    st.markdown("---")
    st.subheader("ℹ️ Información del Sistema")

    st.markdown(f"""
    **SAFE GeoReport v2.0.0**
    
    | Configuración | Valor |
    |--------------|-------|
    | API Key | `{GEOAPIFY_API_KEY}` |
    | URL Base | `{GEOAPIFY_BASE_URL}` |
    | Tiles | Geoapify Carto |
    | Provider | ACTIVO |
    
    **Segmentación Estratégica:**
    - Categorías: 6
    - Subcategorías: 48
    - Niveles de Severidad: 4
    - Estados: 7
    - Prioridades: 4
    - Fuentes: 7
    - Impactos: 4
    
    ---
    🛡️ SAFE Inteligencia Segura - Siempre Activa
    """)


# =============================================================================
# MAIN
# =============================================================================


def main():
    init_session()
    render_header()

    choice = render_sidebar()

    pages = {
        "🏠 Dashboard": page_dashboard,
        "📝 Nuevo Reporte": page_report,
        "🗺️ Mapa Global": page_map,
        "📋 Todos los Reportes": page_list,
        "📈 Analytics": page_stats,
        "⚙️ Configuración": page_settings,
    }

    pages[choice]()


if __name__ == "__main__":
    main()
